using System;
using System.Runtime.InteropServices;

namespace SageMM.Core.Interop;

// Lightweight POD types as value types (stack-allocated for temporaries).
[StructLayout(LayoutKind.Sequential)]
public struct Vec4
{
    public float X, Y, Z, W;
    public Vec4(float x,float y,float z,float w){X=x;Y=y;Z=z;W=w;}
    public static Vec4 FromRGBA(float r,float g,float b,float a) => new(r,g,b,a);
}

[StructLayout(LayoutKind.Sequential)]
public struct Color
{
    public float R,G,B,A;
    public Color(float r,float g,float b,float a){R=r;G=g;B=b;A=a;}
    public Vec4 ToVec4() => new(R,G,B,A);
}
