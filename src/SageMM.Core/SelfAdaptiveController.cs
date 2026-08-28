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

    public double Tmin { get; set; } = 20.0; // seconds
    public double Tmax { get; set; } = 60.0; // seconds
    public double TFlush { get; private set; } = 20.0;

    public SelfAdaptiveController(ControlMode mode)
    {
        _telemetry = new TelemetryCollector();
        _engine = new DecisionEngine();
        _policy = new PolicyEnforcer();
        _mode = mode;

        _policy.OnCompactionDisabled += () => Console.WriteLine("[policy] compaction: DISABLED");
        _policy.OnCompactionEnabled  += () => Console.WriteLine("[policy] compaction: ENABLED");
    }

    public void Run(TimeSpan duration, CancellationToken ct)
    {
        var end = DateTime.UtcNow + duration;
        while (!ct.IsCancellationRequested && DateTime.UtcNow < end)
        {
            var x = _telemetry.Read();
            var decision = _engine.Step(_mode, x, TFlush, Tmin, Tmax);
            TFlush = decision.NextFlushSeconds;

            _policy.Apply(decision.DisableCompaction, () =>
            {
                int r = FlushPECaches.FlushAll(verbose:false);
                Console.WriteLine($"[flush] result={r}");
            });

            Console.WriteLine($"[telemetry] Lgc={x.GcPauseMs:F1}ms Fh={x.FragRatio:P1} Pf/s={x.PageFaultsPerSec:F1} ΔM={x.RssDeltaMB:+0.0;-0.0;0}MB | Tflush={TFlush:F1}s pressure={decision.PredictedPressure:F2} loss={decision.Loss:F3} disable={decision.DisableCompaction}");

            // Sleep until next flush window (bounded min)
            int sleepMs = (int)(Math.Max(5.0, TFlush) * 1000);
            Thread.Sleep(sleepMs);
            _policy.OnFlush?.Invoke();
        }
    }
}
