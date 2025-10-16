using System;

namespace SageMM.Core;

public enum ControlMode { Static, Ewma, Ml }

public class DecisionEngine
{
    // EWMA params
    public double Beta { get; set; } = 0.85;
    public double LTargetMs { get; set; } = 30.0;

    // ML (online ridge with SGD)
    private double[] w = new double[]{0,0,0,0};
    public double Eta { get; set; } = 5e-4;
    public double Lambda { get; set; } = 1e-4;

    public (double nextFlush, bool disableCompaction) Step(ControlMode mode, TelemetrySample x, double tFlush, double tMin, double tMax, double hysteresisFrag=0.07)
    {
        double next = tFlush;
        bool disable = x.FragRatio < hysteresisFrag;

        if (mode == ControlMode.Static)
        {
            next = tFlush; // unchanged
        }
        else if (mode == ControlMode.Ewma)
        {
            next = Beta * tFlush + (1 - Beta) * (x.GcPauseMs / Math.Max(1e-3, LTargetMs)) * tFlush;
        }
        else // ML
        {
            // Feature vector [Lgc, Fh, Pf, ΔM] normalized
            var fv = new double[]{
                x.GcPauseMs / Math.Max(1e-3, LTargetMs),
                x.FragRatio,
                Math.Tanh(x.PageFaultsPerSec/100.0),
                Math.Tanh(x.RssDeltaMB/50.0)
            };
            // Predict relative pressure yhat in [0, 2] approx
            double yhat = 0;
            for(int i=0;i<4;i++) yhat += w[i]*fv[i];
            // Map to multiplicative factor around 1.0
            double factor = Math.Clamp(1.0 + yhat, 0.5, 1.5);
            next = tFlush * factor;

            // SGD target: we want low pause, low faults => rough surrogate target
            double y = Math.Clamp((x.GcPauseMs/LTargetMs) + 0.2*x.FragRatio + 0.01*Math.Log10(1+x.PageFaultsPerSec), 0, 2);
            // Gradient: x(x^T w - y) + λ w
            double inner = yhat - y;
            for(int i=0;i<4;i++)
            {
                w[i] -= Eta * (fv[i]*inner + Lambda*w[i]);
            }
        }
        // Bounds + soft inertia
        next = Math.Clamp(next, tMin, tMax);
        return (next, disable);
    }
}
