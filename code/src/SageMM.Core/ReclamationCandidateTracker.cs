using System;
using System.Collections.Generic;
using System.Linq;

namespace SageMM.Core;

/// <summary>Ranks modules without inspecting application data or evicting recently used code.</summary>
public sealed class ReclamationCandidateTracker
{
    private readonly Dictionary<string, AssemblyActivity> _entries = new(StringComparer.Ordinal);

    public void Observe(string modulePath, DateTime accessUtc, long cleanBytes)
    {
        if (string.IsNullOrWhiteSpace(modulePath)) throw new ArgumentException("A module path is required.", nameof(modulePath));
        if (cleanBytes < 0) throw new ArgumentOutOfRangeException(nameof(cleanBytes));
        bool found = _entries.TryGetValue(modulePath, out var old);
        _entries[modulePath] = new AssemblyActivity(modulePath, accessUtc, (found ? old.AccessCount : 0) + 1, cleanBytes);
    }

    /// <summary>
    /// Cold(a) = 0.6*normalized age + 0.3*inverse frequency + 0.1*clean-byte share.
    /// K is a byte-budget result rather than a fixed, unexplained constant.
    /// </summary>
    public IReadOnlyList<string> Select(DateTime nowUtc, long byteBudget, TimeSpan minimumIdle)
    {
        if (byteBudget <= 0) return Array.Empty<string>();
        var eligible = _entries.Values.Where(e => nowUtc - e.LastAccessUtc >= minimumIdle);
        return AssemblyColdness.Select(eligible, nowUtc, byteBudget).Select(e => e.Path).ToArray();
    }
}
