using SageMM.Core;

namespace SageMM.Core.Tests;

public sealed class ReclamationCandidateTrackerTests
{
    [Fact]
    public void ExcludesHotModulesAndStopsAtByteBudget()
    {
        var now = new DateTime(2026, 8, 28, 0, 0, 0, DateTimeKind.Utc);
        var tracker = new ReclamationCandidateTracker();
        tracker.Observe("old.dll", now.AddMinutes(-30), 4_096);
        tracker.Observe("older.dll", now.AddMinutes(-60), 4_096);
        tracker.Observe("hot.dll", now.AddSeconds(-1), 1_000_000);

        var selected = tracker.Select(now, 4_096, TimeSpan.FromMinutes(5));

        Assert.Single(selected);
        Assert.Equal("older.dll", selected[0]);
        Assert.DoesNotContain("hot.dll", selected);
    }
}
