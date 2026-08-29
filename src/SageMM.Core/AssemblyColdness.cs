using System;
using System.Collections.Generic;
using System.Linq;

namespace SageMM.Core;

public readonly record struct AssemblyActivity(string Path, DateTime LastAccessUtc,
    long AccessCount, long CleanBytes);

public static class AssemblyColdness
{
    /// <summary>Ranks candidates by normalized recency (0.6), inverse frequency (0.3),
    /// and reclaimable clean bytes (0.1). K is derived from a byte budget, not a fixed five.</summary>
    public static IReadOnlyList<AssemblyActivity> Select(IEnumerable<AssemblyActivity> input,
        DateTime nowUtc, long byteBudget)
    {
        var items = input.Where(x => x.CleanBytes > 0 && x.AccessCount >= 0 && x.LastAccessUtc <= nowUtc).ToArray();
        if (items.Length == 0 || byteBudget <= 0) return Array.Empty<AssemblyActivity>();
        double maxAge = Math.Max(1, items.Max(x => (nowUtc - x.LastAccessUtc).TotalSeconds));
        double maxCount = Math.Max(1, items.Max(x => x.AccessCount));
        double maxBytes = Math.Max(1, items.Max(x => x.CleanBytes));
        var ranked = items.OrderByDescending(x =>
            .6 * Math.Clamp((nowUtc - x.LastAccessUtc).TotalSeconds / maxAge, 0, 1) +
            .3 * (1 - Math.Clamp(x.AccessCount / maxCount, 0, 1)) +
            .1 * Math.Clamp(x.CleanBytes / maxBytes, 0, 1));
        var selected = new List<AssemblyActivity>(); long total = 0;
        foreach (var item in ranked) { selected.Add(item); total += item.CleanBytes; if (total >= byteBudget) break; }
        return selected;
    }
}
