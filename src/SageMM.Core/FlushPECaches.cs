using System;
using System.Runtime.InteropServices;

namespace SageMM.Core;

public static class FlushPECaches
{
    // Adjust path if you install the .so elsewhere (LD_LIBRARY_PATH suggested).
    const string NativeLib = "libpeflush.so";

    [DllImport(NativeLib, EntryPoint="FlushCleanPages")]
    private static extern int FlushCleanPagesNative(int verbose);

    [DllImport(NativeLib, EntryPoint="FlushBySubstring")]
    private static extern int FlushBySubstringNative(string needle, int verbose);

    public static int FlushAll(bool verbose=false)
    {
        try { return FlushCleanPagesNative(verbose ? 1 : 0); }
        catch (DllNotFoundException)
        {
            if (verbose) Console.Error.WriteLine("[FlushPECaches] Native library not found; skipping.");
            return -1;
        }
    }

    public static int FlushModule(string containsPath, bool verbose=false)
    {
        try { return FlushBySubstringNative(containsPath, verbose ? 1 : 0); }
        catch (DllNotFoundException)
        {
            if (verbose) Console.Error.WriteLine("[FlushPECaches] Native library not found; skipping.");
            return -1;
        }
    }
}
