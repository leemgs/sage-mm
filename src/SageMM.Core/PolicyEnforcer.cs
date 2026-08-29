using System;

namespace SageMM.Core;

public class PolicyEnforcer
{
    public event Action? OnCompactionDisabled;
    public event Action? OnCompactionEnabled;
    public event Action? OnFlush;

    private bool _compactionDisabled = false;
    private DateTime _lastFlush = DateTime.MinValue;
    public TimeSpan Cooldown { get; init; } = TimeSpan.FromSeconds(10);
    public double MaximumFaultRate { get; init; } = 500;
    public long CooldownSuppressions { get; private set; }
    public long FaultRateSuppressions { get; private set; }
    public long FlushExecutions { get; private set; }

    public void Apply(bool disableCompaction, Action? flushAction)
    {
        if (disableCompaction && !_compactionDisabled)
        {
            _compactionDisabled = true;
            OnCompactionDisabled?.Invoke();
        }
        else if (!disableCompaction && _compactionDisabled)
        {
            _compactionDisabled = false;
            OnCompactionEnabled?.Invoke();
        }

        OnFlush = flushAction;
    }

    public void Apply(bool disableCompaction, TelemetrySample sample, Action? flushAction)
    {
        Apply(disableCompaction, flushAction is null ? null : () =>
        {
            if (sample.PageFaultsPerSec > MaximumFaultRate)
            {
                FaultRateSuppressions++;
                return;
            }
            if (DateTime.UtcNow - _lastFlush < Cooldown)
            {
                CooldownSuppressions++;
                return;
            }
            flushAction();
            FlushExecutions++;
            _lastFlush = DateTime.UtcNow;
        });
    }

    public void Flush() => OnFlush?.Invoke();
    public void RequestFlush() => Flush();
}
