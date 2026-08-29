using System;
using SageMM.Core;
using Xunit;

namespace SageMM.Core.Tests;

public sealed class PolicyEnforcerTests
{
    [Fact]
    public void FaultStormSuppressesFlush()
    {
        var calls = 0;
        var policy = new PolicyEnforcer { MaximumFaultRate = 500, Cooldown = TimeSpan.Zero };
        policy.Apply(false, new TelemetrySample(0, 0, 501, 0), () => calls++);
        policy.RequestFlush();
        Assert.Equal(0, calls);
        Assert.Equal(1, policy.FaultRateSuppressions);
    }

    [Fact]
    public void CooldownSuppressesRepeatedFlush()
    {
        var calls = 0;
        var policy = new PolicyEnforcer { Cooldown = TimeSpan.FromMinutes(1) };
        var sample = new TelemetrySample(0, 0, 0, 0);
        policy.Apply(false, sample, () => calls++);
        policy.RequestFlush();
        policy.RequestFlush();
        Assert.Equal(1, calls);
        Assert.Equal(1, policy.FlushExecutions);
        Assert.Equal(1, policy.CooldownSuppressions);
    }
}
