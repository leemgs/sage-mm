using System;

namespace SageMM.Core;

public enum ControlMode { Static, Ewma, Ml }

/// <summary>A deterministic, bounded controller. All inputs are dimensionless after Normalize().</summary>
public sealed class DecisionEngine
{
    public double Beta { get; init; } = 0.85;
    public double LearningRate { get; init; } = 5e-4;
    public double RidgePenalty { get; init; } = 1e-4;
    public double PauseTargetMs { get; init; } = 30;
    public double FaultTargetPerSecond { get; init; } = 100;
    public double RssGrowthTargetMb { get; init; } = 50;

    private readonly double[] _weights = new double[5]; // bias + four features
    private double[]? _previousFeatures;
    private double _previousPrediction;
    private double _ewmaPressure = 1;

    public ControlDecision Step(ControlMode mode, TelemetrySample sample, double currentInterval,
        double minimumInterval, double maximumInterval, double fragmentationThreshold = .07)
    {
        var features = Normalize(sample);
        double observedPressure = Pressure(features);

        // At t, train the prediction made at t-1 against pressure observed at t. This avoids
        // fitting and reporting on the same observation and makes y-hat a one-step prediction.
        if (mode == ControlMode.Ml && _previousFeatures is not null)
            Update(_previousFeatures, _previousPrediction, observedPressure);

        if (mode == ControlMode.Ewma)
            _ewmaPressure = Beta * _ewmaPressure + (1 - Beta) * observedPressure;
        double predictedPressure = mode switch
        {
            ControlMode.Static => 1,
            ControlMode.Ewma => _ewmaPressure,
            // Ridge learns a correction around neutral pressure (1), avoiding an unsafe
            // zero-pressure cold start when all coefficients are initialized to zero.
            _ => Math.Clamp(1 + Dot(features), 0, 2)
        };

        _previousFeatures = features;
        _previousPrediction = predictedPressure;

        // Greater pressure reclaims sooner; a 10% dead-band prevents oscillation.
        double factor = predictedPressure switch { > 1.1 => .8, < .9 => 1.2, _ => 1 };
        double interval = mode == ControlMode.Static
            ? currentInterval
            : Math.Clamp(currentInterval * factor, minimumInterval, maximumInterval);
        bool disableCompaction = sample.FragRatio < fragmentationThreshold;
        return new(interval, disableCompaction, predictedPressure, observedPressure);
    }

    private double[] Normalize(TelemetrySample x) => new[] {
        1d,
        Math.Clamp(x.GcPauseMs / PauseTargetMs, 0, 2),
        Math.Clamp(x.FragRatio / .20, 0, 2),
        Math.Clamp(x.PageFaultsPerSec / FaultTargetPerSecond, 0, 2),
        Math.Clamp(Math.Max(0, x.RssDeltaMB) / RssGrowthTargetMb, 0, 2)
    };

    // Equal weights are intentional: scaling above makes each term relative to an explicit SLO.
    private static double Pressure(double[] x) => Math.Clamp((x[1] + x[2] + x[3] + x[4]) / 4, 0, 2);
    private double Dot(double[] x) { double v = 0; for (int i = 0; i < x.Length; i++) v += _weights[i] * x[i]; return v; }
    private void Update(double[] x, double prediction, double target)
    {
        double error = prediction - target;
        for (int i = 0; i < x.Length; i++)
            _weights[i] -= LearningRate * (error * x[i] + RidgePenalty * _weights[i]);
    }
}

public readonly record struct ControlDecision(double FlushIntervalSeconds, bool DisableCompaction,
    double PredictedPressure, double ObservedPressure);
