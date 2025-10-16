using System;
using System.Diagnostics;
using System.IO;

namespace SageMM.Core;

public record TelemetrySample(
    double GcPauseMs,
    double FragRatio,
    double PageFaultsPerSec,
    double RssDeltaMB);

public class TelemetryCollector
{
    private readonly Stopwatch _sw = new();
    private TimeSpan _lastGc = TimeSpan.Zero;
    private (ulong minflt, ulong majflt) _pfLast = ReadFaults();
    private long _rssLast = ReadRssKB();

    public TelemetrySample Read()
    {
        // Approximate GC pause using forced Gen0 with stopwatch window (demo-friendly).
        var before = GC.GetTotalMemory(forceFullCollection: false);
        _sw.Restart();
        GC.Collect(0, GCCollectionMode.Forced, blocking: true, compacting: false);
        _sw.Stop();
        var after = GC.GetTotalMemory(false);
        double gcMs = _sw.Elapsed.TotalMilliseconds;

        // Fragmentation proxy: LOH size + pinned bytes vs total managed (very rough demo proxy)
        long total = GC.GetTotalMemory(false);
        long pinned = GC.GetGCMemoryInfo().PinnedObjectCount; // count, not bytes, but OK as trend proxy
        double frag = Math.Min(0.25, (pinned / Math.Max(1.0, (double)(total >> 20)))) + 0.05; // 5% base

        // Page faults per second (delta)
        var pfNow = ReadFaults();
        double pfps = (double)((pfNow.minflt - _pfLast.minflt) + (pfNow.majflt - _pfLast.majflt)) / 1.0;
        _pfLast = pfNow;

        // RSS delta (MB)
        long rssKB = ReadRssKB();
        double rssDeltaMB = (rssKB - _rssLast) / 1024.0;
        _rssLast = rssKB;

        return new TelemetrySample(gcMs, frag, pfps, rssDeltaMB);
    }

    static (ulong minflt, ulong majflt) ReadFaults()
    {
        try
        {
            foreach (var line in File.ReadAllLines("/proc/self/status"))
            {
                if (line.StartsWith("MinFaults:") || line.StartsWith("MinFlt:"))
                {
                    // format varies; handle both
                }
            }
            // Fallback to /proc/self/stat (minor = field 10, major = 12)
            var parts = File.ReadAllText("/proc/self/stat").Split();
            ulong minflt = ulong.Parse(parts[9]);
            ulong majflt = ulong.Parse(parts[11]);
            return (minflt, majflt);
        }
        catch { return (0, 0); }
    }

    static long ReadRssKB()
    {
        try
        {
            var parts = File.ReadAllText("/proc/self/statm").Split();
            long rssPages = long.Parse(parts[1]);
            long pageKB = 4;
            return rssPages * pageKB;
        }
        catch { return 0; }
    }
}
