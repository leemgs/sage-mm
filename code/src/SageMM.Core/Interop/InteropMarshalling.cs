using System;
using System.Runtime.InteropServices;

namespace SageMM.Core.Interop;

internal static class InteropMarshalling
{
    [DllImport("c", EntryPoint="memcpy")]
    private static extern IntPtr memcpy(IntPtr dst, IntPtr src, UIntPtr len);

    // Example: marshal Vec4 to a native buffer without heap allocations
    public static unsafe void WriteVec4(Span<byte> dst, in Vec4 v)
    {
        if (dst.Length < sizeof(Vec4)) throw new ArgumentException("dst too small");
        fixed (Vec4* pv = &v)
        fixed (byte* pb = dst)
        {
            memcpy((IntPtr)pb, (IntPtr)pv, (UIntPtr)sizeof(Vec4));
        }
    }
}
