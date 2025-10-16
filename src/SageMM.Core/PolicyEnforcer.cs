using System;

namespace SageMM.Core;

public class PolicyEnforcer
{
    public event Action? OnCompactionDisabled;
    public event Action? OnCompactionEnabled;
    public event Action? OnFlush;

    private bool _compactionDisabled = false;

    public void Apply(bool disableCompaction, Action flushAction)
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

        OnFlush = () => flushAction();
    }
}
