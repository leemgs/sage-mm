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

    [Fact]
    public void InvalidTelemetryFailsClosedWithoutUpdatingPolicy()
    {
        var engine = new DecisionEngine();

        var decision = engine.Step(ControlMode.Ml,
            new TelemetrySample(double.NaN, 0.03, 10, 1), 30, 20, 60);

        Assert.Equal(30, decision.NextFlushSeconds);
        Assert.False(decision.DisableCompaction);
        Assert.False(decision.ShouldReclaim);
        Assert.Equal(ControllerFallbackReason.InvalidTelemetry, decision.FallbackReason);
    }

    [Fact]
    public void RidgeLossUsesPreviousPredictionAndThenImproves()
    {
        var engine = new DecisionEngine(new ControllerOptions(LearningRate: 0.01));
        var highPressure = new TelemetrySample(60, 0.12, 200, 100);

        var warmup = engine.Step(ControlMode.Ml, highPressure, 30, 20, 60);
        var firstScored = engine.Step(ControlMode.Ml, highPressure, 30, 20, 60);
        var secondScored = engine.Step(ControlMode.Ml, highPressure, 30, 20, 60);

        Assert.Equal(0, warmup.Loss);
        Assert.True(firstScored.Loss > 0);
        Assert.True(secondScored.Loss < firstScored.Loss);
    }

    [Fact]
    public void FaultStormSuppressesReclamationAtDecisionBoundary()
    {
        var engine = new DecisionEngine(new ControllerOptions(ReclamationFaultCeiling: 500));
        var decision = engine.Step(ControlMode.Ewma,
            new TelemetrySample(10, 0.08, 501, 0), 30, 20, 60);

        Assert.False(decision.ShouldReclaim);
        Assert.Equal(ControllerFallbackReason.FaultStorm, decision.FallbackReason);
    }
}
