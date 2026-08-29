using System;
using SageMM.Core;
using Xunit;

namespace SageMM.Core.Tests;

public sealed class AssemblyColdnessTests
{
    [Fact]
    public void SelectsColdestAssembliesUntilBudgetIsMet()
    {
        var now = new DateTime(2026, 8, 28, 0, 0, 0, DateTimeKind.Utc);
        var hot = new AssemblyActivity("hot", now.AddSeconds(-1), 100, 100);
        var cold = new AssemblyActivity("cold", now.AddHours(-1), 0, 100);
        var result = AssemblyColdness.Select(new[] { hot, cold }, now, 100);
        Assert.Single(result);
        Assert.Equal("cold", result[0].Path);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public void NonPositiveBudgetSelectsNothing(long budget)
    {
        var item = new AssemblyActivity("a", DateTime.UnixEpoch, 0, 1);
        Assert.Empty(AssemblyColdness.Select(new[] { item }, DateTime.UtcNow, budget));
    }

    [Fact]
    public void FutureObservationsAreNotReclamationCandidates()
    {
        var now = new DateTime(2026, 8, 29, 0, 0, 0, DateTimeKind.Utc);
        var future = new AssemblyActivity("future", now.AddMinutes(1), 1, 1024);
        Assert.Empty(AssemblyColdness.Select(new[] { future }, now, 1024));
    }
}
