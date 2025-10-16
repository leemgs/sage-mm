using System;
using System.Threading;
using SageMM.Core;

class Program
{
    static void Main(string[] args)
    {
        var mode = ControlMode.Ml;
        int minutes = 1;
        double tmin=20, tmax=60;

        for (int i=0;i<args.Length;i++)
        {
            if (args[i] == "--mode" && i+1<args.Length)
                mode = args[++i].ToLower() switch {
                    "static" => ControlMode.Static,
                    "ewma"   => ControlMode.Ewma,
                    _        => ControlMode.Ml
                };
            else if (args[i] == "--minutes" && i+1<args.Length)
                minutes = int.Parse(args[++i]);
            else if (args[i] == "--flush-min" && i+1<args.Length)
                tmin = double.Parse(args[++i]);
            else if (args[i] == "--flush-max" && i+1<args.Length)
                tmax = double.Parse(args[++i]);
        }

        Console.WriteLine($"SAGE-MM Demo | mode={mode} duration={minutes}m bounds=[{tmin},{tmax}]");

        var cts = new CancellationTokenSource();
        Console.CancelKeyPress += (_,e)=>{ e.Cancel=true; cts.Cancel(); };

        var ctl = new SelfAdaptiveController(mode){ Tmin=tmin, Tmax=tmax, HysteresisFrag=0.07 };
        ctl.Run(TimeSpan.FromMinutes(minutes), cts.Token);
        Console.WriteLine("Done.");
    }
}
