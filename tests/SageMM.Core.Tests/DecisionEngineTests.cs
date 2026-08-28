using SageMM.Core;

namespace SageMM.Core.Tests;

public sealed class DecisionEngineTests
{
    [Fact]
    public void StaticModeDoesNotChangePolicy()
    {
        var engine = new DecisionEngine();
        var decision = engine.Step(ControlMode.Static,
            new TelemetrySample(100, 0.01, 500, 100), 30, 20, 60);

        Assert.Equal(30, decision.NextFlushSeconds);
        Assert.False(decision.DisableCompaction);
    }

    [Fact]
    public void EwmaStaysBoundedAndRespondsToPressure()
    {
        var engine = new DecisionEngine();
        var decision = engine.Step(ControlMode.Ewma,
            new TelemetrySample(300, 0.2, 1000, 500), 20, 20, 60);

        Assert.Equal(20, decision.NextFlushSeconds);
        Assert.False(decision.DisableCompaction);
    }

    [Fact]
    public void FrozenModelProducesRepeatablePrediction()
    {
        var engine = new DecisionEngine();
        var sample = new TelemetrySample(30, 0.08, 100, 10);

        var first = engine.Step(ControlMode.Ml, sample, 30, 20, 60, updateModel: false);
        var second = engine.Step(ControlMode.Ml, sample, 30, 20, 60, updateModel: false);

        Assert.Equal(first.PredictedPressure, second.PredictedPressure);
        Assert.Equal(first.NextFlushSeconds, second.NextFlushSeconds);
    }
}
