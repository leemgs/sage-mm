using System;
using System.Threading;
using SageMM.Core;

namespace SageMM.Core;

public class SelfAdaptiveController
{
    private readonly TelemetryCollector _telemetry;
    private readonly DecisionEngine _engine;
    private readonly PolicyEnforcer _policy;
    private readonly ControlMode _mode;
    private readonly ReclamationCandidateTracker _candidates = new();

    public double Tmin { get; set; } = 20.0; // seconds
    public double Tmax { get; set; } = 60.0; // seconds
    public double TFlush { get; private set; } = 20.0;
    public long ReclamationByteBudget { get; set; } = 4 * 1024 * 1024;
    public TimeSpan MinimumModuleIdle { get; set; } = TimeSpan.FromSeconds(10);
    public long NoCandidateCount { get; private set; }
    public long NativeFailureCount { get; private set; }

    public SelfAdaptiveController(ControlMode mode)
    {
        _telemetry = new TelemetryCollector();
        _engine = new DecisionEngine();
        _policy = new PolicyEnforcer();
        _mode = mode;

        _policy.OnCompactionDisabled += () => Console.WriteLine("[policy] compaction: DISABLED");
        _policy.OnCompactionEnabled  += () => Console.WriteLine("[policy] compaction: ENABLED");
    }

    public void ObserveModuleAccess(string modulePath, long cleanByteEstimate, DateTime? accessUtc = null) =>
        _candidates.Observe(modulePath, accessUtc ?? DateTime.UtcNow, cleanByteEstimate);

    public void Run(TimeSpan duration, CancellationToken ct)
    {
        var end = DateTime.UtcNow + duration;
        while (!ct.IsCancellationRequested && DateTime.UtcNow < end)
        {
            var x = _telemetry.Read();
            var decision = _engine.Step(_mode, x, TFlush, Tmin, Tmax);
            TFlush = decision.NextFlushSeconds;

            _policy.Apply(decision.DisableCompaction, x, decision.ShouldReclaim
                ? () =>
                {
                    var selected = _candidates.Select(DateTime.UtcNow, ReclamationByteBudget, MinimumModuleIdle);
                    if (selected.Count == 0)
                    {
                        NoCandidateCount++;
                        Console.WriteLine("[flush] no eligible cold module");
                        return;
                    }
                    foreach (var module in selected)
                    {
                        int r = FlushPECaches.FlushModule(module, verbose:false);
                        if (r < 0) NativeFailureCount++;
                        Console.WriteLine($"[flush] module={module} result={r}");
                    }
                }
                : null);

            Console.WriteLine($"[telemetry] Lgc={x.GcPauseMs:F1}ms Fh={x.FragRatio:P1} Pf/s={x.PageFaultsPerSec:F1} ΔM={x.RssDeltaMB:+0.0;-0.0;0}MB | Tflush={TFlush:F1}s pressure={decision.PredictedPressure:F2} loss={decision.Loss:F3} disable={decision.DisableCompaction} reclaim={decision.ShouldReclaim} fallback={decision.FallbackReason}");

            // Sleep until next flush window (bounded min)
            int sleepMs = (int)(Math.Max(5.0, TFlush) * 1000);
            Thread.Sleep(sleepMs);
            _policy.Flush();
        }
    }
}
