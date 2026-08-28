using SageMM.Core;
using Xunit;

namespace SageMM.Core.Tests;

public sealed class DecisionEngineTests
{
    [Fact]
    public void StaticModeDoesNotChangeInterval()
    {
        var decision = new DecisionEngine().Step(ControlMode.Static,
            new TelemetrySample(100, .5, 1000, 100), 40, 20, 60);
        Assert.Equal(40, decision.FlushIntervalSeconds);
    }

    [Fact]
    public void MlColdStartIsNeutralRatherThanZeroPressure()
    {
        var decision = new DecisionEngine().Step(ControlMode.Ml,
            new TelemetrySample(0, 0, 0, 0), 40, 20, 60);
        Assert.Equal(1, decision.PredictedPressure);
        Assert.Equal(40, decision.FlushIntervalSeconds);
    }

    [Fact]
    public void EwmaRemainsBoundedUnderSustainedPressure()
    {
        var engine = new DecisionEngine();
        double interval = 40;
        for (var i = 0; i < 100; i++)
            interval = engine.Step(ControlMode.Ewma,
                new TelemetrySample(1000, 1, 10000, 1000), interval, 20, 60).FlushIntervalSeconds;
        Assert.Equal(20, interval);
    }
}
