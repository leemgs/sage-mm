using System;
using System.Threading;
using System.IO;
using System.Linq;
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
                    "threshold" => ControlMode.Threshold,
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

        var ctl = new SelfAdaptiveController(mode){ Tmin=tmin, Tmax=tmax };
        foreach (var path in AppDomain.CurrentDomain.GetAssemblies()
                     .Select(a => a.Location).Where(path => !string.IsNullOrEmpty(path) && File.Exists(path)))
            ctl.ObserveModuleAccess(path, new FileInfo(path).Length);
        ctl.Run(TimeSpan.FromMinutes(minutes), cts.Token);
        Console.WriteLine("Done.");
    }
}
