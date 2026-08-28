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

    public void Apply(bool disableCompaction, TelemetrySample sample, Action flushAction)
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

        OnFlush = () =>
        {
            // Avoid reclaim/fault thrashing during rapid switching, and rate-limit the syscall.
            if (sample.PageFaultsPerSec > MaximumFaultRate || DateTime.UtcNow - _lastFlush < Cooldown)
                return;
            flushAction();
            _lastFlush = DateTime.UtcNow;
        };
    }
}
