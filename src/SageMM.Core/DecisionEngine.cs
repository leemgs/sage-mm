using System;

namespace SageMM.Core;

public enum ControlMode { Static, Threshold, Ewma, Ml }
public enum ControllerFallbackReason { None, InvalidTelemetry, FaultStorm }

/// <summary>All controller constants, including feature scales, in one reproducible configuration.</summary>
public sealed record ControllerOptions(
    double Beta = 0.85,
    double TargetGcPauseMs = 30.0,
    double TargetFaultsPerSecond = 100.0,
    double TargetRssGrowthMB = 50.0,
    double LearningRate = 5e-4,
    double RidgePenalty = 1e-4,
    double FragmentationLow = 0.05,
    double FragmentationHigh = 0.12,
    int MinimumCompactionDeferrals = 3,
    double ReclamationFaultCeiling = 500.0,
    double PressureLow = 0.9,
    double PressureHigh = 1.1,
    double ThresholdShortenFactor = 0.8,
    double ThresholdLengthenFactor = 1.2);

public readonly record struct ControlDecision(
    double NextFlushSeconds,
    bool DisableCompaction,
    double PredictedPressure,
    double Loss,
    bool ShouldReclaim,
    ControllerFallbackReason FallbackReason);

/// <summary>
/// A deterministic, online controller. A sample is used to predict the pressure of the
/// following interval; callers must split tuning and reporting traces externally.
/// </summary>
public sealed class DecisionEngine
{
    private readonly ControllerOptions _options;
    private readonly double[] _weights = { 1, 0, 0, 0, 0 }; // neutral bias + four signals
    private double[]? _pendingFeatures;
    private double _pendingPrediction;
    private double _ewmaPressure = 1.0;
    private bool _compactionDisabled;
    private int _deferrals;

    public DecisionEngine(ControllerOptions? options = null) =>
        _options = options ?? new ControllerOptions();

    public ControlDecision Step(
        ControlMode mode,
        TelemetrySample sample,
        double currentFlushSeconds,
        double minimumFlushSeconds,
        double maximumFlushSeconds,
        bool updateModel = true)
    {
        if (minimumFlushSeconds <= 0 || maximumFlushSeconds < minimumFlushSeconds)
            throw new ArgumentOutOfRangeException(nameof(minimumFlushSeconds));
        if (!IsValid(sample))
        {
            // Fail closed: keep the previous bounded interval, do not reclaim pages, and
            // ensure that compaction remains available until trustworthy telemetry returns.
            _compactionDisabled = false;
            _deferrals = 0;
            return new ControlDecision(
                Math.Clamp(currentFlushSeconds, minimumFlushSeconds, maximumFlushSeconds),
                DisableCompaction: false,
                PredictedPressure: 0,
                Loss: 0,
                ShouldReclaim: false,
                FallbackReason: ControllerFallbackReason.InvalidTelemetry);
        }

        double target = PressureTarget(sample);
        double loss = 0;
        if (mode == ControlMode.Ml && _pendingFeatures is not null)
        {
            // Score the prediction issued at t-1 against pressure observed at t, then
            // update with x(t-1). The current observation is never its own prediction.
            double residual = _pendingPrediction - target;
            loss = 0.5 * residual * residual;
            if (updateModel)
            {
                for (int i = 0; i < _weights.Length; i++)
                    _weights[i] -= _options.LearningRate *
                        (_pendingFeatures[i] * residual + _options.RidgePenalty * _weights[i]);
            }
        }

        var features = Features(sample);
        double prediction;
        double next = currentFlushSeconds;

        if (mode == ControlMode.Threshold)
        {
            prediction = target;
            double factor = target switch
            {
                var pressure when pressure > _options.PressureHigh => _options.ThresholdShortenFactor,
                var pressure when pressure < _options.PressureLow => _options.ThresholdLengthenFactor,
                _ => 1.0
            };
            next = currentFlushSeconds * factor;
        }
        else if (mode == ControlMode.Ewma)
        {
            _ewmaPressure = _options.Beta * _ewmaPressure + (1 - _options.Beta) * target;
            prediction = _ewmaPressure;
            // Pressure > 1 shortens the interval; pressure < 1 lengthens it.
            double desired = currentFlushSeconds / Math.Clamp(prediction, 0.5, 2.0);
            next = _options.Beta * currentFlushSeconds + (1 - _options.Beta) * desired;
        }
        else if (mode == ControlMode.Ml)
        {
            prediction = Math.Clamp(Dot(_weights, features), 0.0, 2.0);
            next = currentFlushSeconds / Math.Clamp(0.5 + prediction, 0.5, 1.5);
            _pendingFeatures = features;
            _pendingPrediction = prediction;
        }
        else
        {
            prediction = 1.0;
            _pendingFeatures = null;
        }

        if (mode == ControlMode.Static)
        {
            _compactionDisabled = false;
            _deferrals = 0;
        }
        else
        {
            UpdateCompactionGate(sample.FragRatio);
        }
        bool faultStorm = sample.PageFaultsPerSec > _options.ReclamationFaultCeiling;
        return new ControlDecision(
            Math.Clamp(next, minimumFlushSeconds, maximumFlushSeconds),
            _compactionDisabled,
            prediction,
            loss,
            ShouldReclaim: !faultStorm,
            FallbackReason: faultStorm ? ControllerFallbackReason.FaultStorm : ControllerFallbackReason.None);
    }

    private double[] Features(TelemetrySample x) => new[] {
        1.0,
        Math.Clamp(x.GcPauseMs / _options.TargetGcPauseMs, 0, 2),
        Math.Clamp(x.FragRatio / _options.FragmentationHigh, 0, 2),
        Math.Clamp(x.PageFaultsPerSec / _options.TargetFaultsPerSecond, 0, 2),
        Math.Clamp(Math.Max(0, x.RssDeltaMB) / _options.TargetRssGrowthMB, 0, 2)
    };

    // Dimensionless, equally weighted operational objective. The maximum component
    // makes any breached service objective visible instead of mixing ms, counts and MB.
    private double PressureTarget(TelemetrySample x) => Math.Clamp(Math.Max(
        x.GcPauseMs / _options.TargetGcPauseMs,
        Math.Max(x.PageFaultsPerSec / _options.TargetFaultsPerSecond,
                 Math.Max(0, x.RssDeltaMB) / _options.TargetRssGrowthMB)), 0, 2);

    private void UpdateCompactionGate(double fragmentation)
    {
        if (_compactionDisabled &&
            (fragmentation >= _options.FragmentationHigh ||
             _deferrals >= _options.MinimumCompactionDeferrals))
        {
            _compactionDisabled = false;
            _deferrals = 0;
        }
        else if (!_compactionDisabled && fragmentation <= _options.FragmentationLow)
        {
            _compactionDisabled = true;
            _deferrals = 0;
        }
        else if (_compactionDisabled)
        {
            _deferrals++;
        }
    }

    private static double Dot(double[] weights, double[] features)
    {
        double result = 0;
        for (int i = 0; i < weights.Length; i++) result += weights[i] * features[i];
        return result;
    }

    private static bool IsValid(TelemetrySample sample) =>
        double.IsFinite(sample.GcPauseMs) && sample.GcPauseMs >= 0 &&
        double.IsFinite(sample.FragRatio) && sample.FragRatio is >= 0 and <= 1 &&
        double.IsFinite(sample.PageFaultsPerSec) && sample.PageFaultsPerSec >= 0 &&
        double.IsFinite(sample.RssDeltaMB);
}
