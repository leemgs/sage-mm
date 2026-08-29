using System;
using System.Collections.Generic;
using System.Linq;

namespace SageMM.Core;

/// <summary>Ranks modules without inspecting application data or evicting recently used code.</summary>
public sealed class ReclamationCandidateTracker
{
    private sealed record Entry(DateTime LastAccessUtc, long AccessCount, long CleanBytes);
    private readonly Dictionary<string, Entry> _entries = new(StringComparer.Ordinal);

    public void Observe(string modulePath, DateTime accessUtc, long cleanBytes)
    {
        if (string.IsNullOrWhiteSpace(modulePath)) throw new ArgumentException("A module path is required.", nameof(modulePath));
        if (cleanBytes < 0) throw new ArgumentOutOfRangeException(nameof(cleanBytes));
        _entries.TryGetValue(modulePath, out var old);
        _entries[modulePath] = new Entry(accessUtc, (old?.AccessCount ?? 0) + 1, cleanBytes);
    }

    /// <summary>
    /// Cold(a) = 0.6*normalized age + 0.3*inverse frequency + 0.1*clean-byte share.
    /// K is a byte-budget result rather than a fixed, unexplained constant.
    /// </summary>
    public IReadOnlyList<string> Select(DateTime nowUtc, long byteBudget, TimeSpan minimumIdle)
    {
        if (byteBudget <= 0) return Array.Empty<string>();
        var eligible = _entries.Where(e => nowUtc - e.Value.LastAccessUtc >= minimumIdle).ToArray();
        if (eligible.Length == 0) return Array.Empty<string>();
        double maxAge = eligible.Max(e => Math.Max(1, (nowUtc - e.Value.LastAccessUtc).TotalSeconds));
        long maxCount = eligible.Max(e => Math.Max(1, e.Value.AccessCount));
        long totalBytes = eligible.Sum(e => e.Value.CleanBytes);
        var ranked = eligible.OrderByDescending(e =>
            0.6 * (nowUtc - e.Value.LastAccessUtc).TotalSeconds / maxAge +
            0.3 * (1.0 - (double)e.Value.AccessCount / maxCount) +
            0.1 * (double)e.Value.CleanBytes / Math.Max(1, totalBytes));

        var result = new List<string>();
        long selectedBytes = 0;
        foreach (var candidate in ranked)
        {
            result.Add(candidate.Key);
            selectedBytes += candidate.Value.CleanBytes;
            if (selectedBytes >= byteBudget) break;
        }
        return result;
    }
}
