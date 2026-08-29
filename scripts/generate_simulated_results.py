#!/usr/bin/env python3
"""Generate clearly watermarked synthetic results for pipeline/manuscript-layout testing."""
import argparse, csv, io, json, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "experiments/expected_factorial_targets.csv"
RUNS = ROOT / "experiments/simulated/factorial_runs.csv"
SUMMARY = ROOT / "experiments/simulated/factorial_summary.json"
REPORT = ROOT / "docs/SIMULATED_RESULTS.md"
FIGURES = ROOT / "docs/figures"
SEED, N, RESAMPLES = 20260829, 30, 10_000
METRICS = [
    ("peak_pss", "expected_peak_pss_index", 2.0),
    ("allocation", "expected_allocation_rate_index", 2.5),
    ("gc_p99", "expected_gc_p99_index", 2.5),
    ("fault_rate", "expected_fault_rate_index", 7.0),
    ("input_p99", "expected_input_p99_index", 2.5),
    ("controller_cpu", "expected_controller_cpu_pct", .08),
]

def percentile(values, q):
    values = sorted(values); p = (len(values)-1)*q; lo = int(p); hi = min(lo+1,len(values)-1); f=p-lo
    return values[lo]*(1-f)+values[hi]*f

def ci(values, rng):
    means=[sum(rng.choice(values) for _ in values)/len(values) for _ in range(RESAMPLES)]
    return [percentile(means,.025),percentile(means,.975)]

def svg_bars(title, labels, values, ylabel):
    width,height=760,420; left,bottom,top=80,350,55; plot_h=270; maxv=max(values)*1.15
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{width/2}" y="28" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="bold">SIMULATED — {title}</text>',
         f'<text x="18" y="210" transform="rotate(-90 18 210)" text-anchor="middle" font-family="sans-serif" font-size="13">{ylabel}</text>',
         f'<line x1="{left}" y1="{bottom}" x2="{width-30}" y2="{bottom}" stroke="black"/>']
    step=(width-left-50)/len(values); bar=step*.58
    for i,(label,value) in enumerate(zip(labels,values)):
        x=left+i*step+step*.2; h=value/maxv*plot_h; y=bottom-h
        out += [f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar:.1f}" height="{h:.1f}" fill="#4c78a8"/>',
                f'<text x="{x+bar/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{value:.1f}</text>',
                f'<text x="{x+bar/2:.1f}" y="{bottom+20}" text-anchor="middle" font-family="sans-serif" font-size="11">{label}</text>']
    out.append('<text x="380" y="402" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b22222">Synthetic pipeline validation; not empirical evidence</text></svg>')
    return "\n".join(out)+"\n"

def generate():
    rng=random.Random(SEED)
    with TARGETS.open(newline='',encoding='utf-8') as f: targets=list(csv.DictReader(f))
    run_rows=[]; summaries=[]
    for t in targets:
        treatment=f"G{t['g']}I{t['i']}R{t['r']}C{t['c']}"; samples={m:[] for m,_,_ in METRICS}
        for run in range(1,N+1):
            row={'simulation':'true','treatment':treatment,'run_id':run,'seed':SEED}
            for metric,column,sd in METRICS:
                value=max(0,rng.gauss(float(t[column]),sd)); samples[metric].append(value); row[f'{metric}_index']=f'{value:.4f}'
            run_rows.append(row)
        item={'treatment':treatment,'factors':{k:int(t[k]) for k in ('g','i','r','c')},'n':N,'metrics':{}}
        for metric,column,_ in METRICS:
            mean=sum(samples[metric])/N; bounds=ci(samples[metric],rng); target=float(t[column]); tol=.2 if metric=='controller_cpu' else 5
            item['metrics'][metric]={'expected':target,'simulated_mean':mean,'ci95':bounds,'pass':abs(mean-target)<=tol}
        summaries.append(item)
    fields=['simulation','treatment','run_id','seed']+[f'{m}_index' for m,_,_ in METRICS]
    stream=io.StringIO(); writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n'); writer.writeheader(); writer.writerows(run_rows)
    summary=json.dumps({'simulation_only':True,'seed':SEED,'runs_per_cell':N,'bootstrap_resamples':RESAMPLES,'cells':summaries},indent=2,sort_keys=True)+'\n'
    def fmt(x): return f"{x:.1f}"
    lines=['# Simulation-only Results mock-up','', '> **SYNTHETIC DATA — NOT OBSERVED.** This chapter exercises the analysis, tables, figures, and acceptance rules before device experiments. It must be deleted or replaced with provenance-backed measurements before submission.','',
           '## RQ1 — Expected architecture/build effect','', 'The simulation projects heap configuration to reduce normalized GC p99 from 100 to 75 on the ARM32-centered workload and uses the previously stated 2.6× ARM32/ARM64 compaction-frequency hypothesis. Figure 1 is synthetic.','', '![Simulated RQ1](figures/simulated_rq1.svg)','',
           '## RQ2 — Expected interop and reclamation effects','', 'The simulation projects value-type interop to reduce allocation-rate index from 100 to 72. Static reclamation reduces PSS but raises the fault index to 160, explicitly representing the expected refault trade-off. Figure 2 is synthetic.','', '![Simulated RQ2](figures/simulated_rq2.svg)','',
           '## RQ3 — Expected coordinated-controller effects','', 'The simulation projects Threshold, EWMA, and Ridge to progressively reduce the unguarded refault/latency penalty. The expected Ridge-over-EWMA margin remains deliberately small; overlapping real CIs will be reported as no demonstrated ML advantage.','', '![Simulated RQ3](figures/simulated_rq3.svg)','',
           '## Complete simulated 2×2×2×2 factorial table','', '| Cell | PSS expected | PSS simulated [95% CI] | GC p99 expected | GC simulated [95% CI] | Fault expected | Fault simulated [95% CI] | Input expected | Input simulated [95% CI] | Pass |','|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|']
    for s in summaries:
        p,g,f,i=(s['metrics'][x] for x in ('peak_pss','gc_p99','fault_rate','input_p99')); passed=all(x['pass'] for x in s['metrics'].values())
        lines.append(f"| {s['treatment']} | {fmt(p['expected'])} | {fmt(p['simulated_mean'])} [{fmt(p['ci95'][0])}, {fmt(p['ci95'][1])}] | {fmt(g['expected'])} | {fmt(g['simulated_mean'])} [{fmt(g['ci95'][0])}, {fmt(g['ci95'][1])}] | {fmt(f['expected'])} | {fmt(f['simulated_mean'])} [{fmt(f['ci95'][0])}, {fmt(f['ci95'][1])}] | {fmt(i['expected'])} | {fmt(i['simulated_mean'])} [{fmt(i['ci95'][0])}, {fmt(i['ci95'][1])}] | {'PASS' if passed else 'FAIL'} |")
    lines += ['', '## Simulated additional-platform outcome','', '| Platform | PSS index | GC p99 index | Fault index | Input p99 index | CPU | Status |','|---|---:|---:|---:|---:|---:|---|','| Constrained ARM64 Linux SBC (synthetic) | 80.2 [78.9, 81.5] | 68.4 [66.1, 70.7] | 129.1 [123.0, 135.2] | 84.6 [82.3, 86.9] | 1.3% | PASS against prospective range |','',
              '## Simulated adverse and endurance outcomes','', '| Scenario | Synthetic outcome | Predeclared threshold | Status |','|---|---:|---:|:---:|','| Hot reuse, normal storage | reload p99 22.1 ms | ≤25 ms | PASS |','| Hot reuse, slow storage | reload p99 69.3 ms | ≤75 ms | PASS |','| Rapid switching | fault index 131.0 | ≤135 | PASS |','| Failure injection | 0 correctness failures; 100% errors surfaced | 0 failures | PASS |','| Fault storm | 100% reclamations suppressed above guard | 100% | PASS |','| Endurance | 10×8 h, 0 simulated OOM/watchdog, 0 censored | 80 device-hours; 0 OOM | PASS |','',
              '## Replacement rule','', 'Every value and figure in this file is generated from a seeded probability model centered on the prospective targets. Synthetic PASS only proves that the reporting pipeline accepts data near its targets. It cannot reveal runtime, firmware, measurement, safety, or performance bugs. Replace this entire file and all `simulated_*.svg` figures with observed outputs before peer review.']
    figures={
      'simulated_rq1.svg':svg_bars('RQ1 architecture expectation',['Stock','Static-G'],[100,75],'GC p99 index (lower is better)'),
      'simulated_rq2.svg':svg_bars('RQ2 component expectation',['Alloc stock','Interop','PSS stock','Reclaim','Fault stock','Reclaim'],[100,72,100,92,100,160],'Normalized index'),
      'simulated_rq3.svg':svg_bars('RQ3 controller expectation',['Static-GIR','Threshold','EWMA','Ridge'],[91,85,82,80],'Input p99 index (lower is better)')}
    return stream.getvalue(),summary,"\n".join(lines)+"\n",figures

def main():
    p=argparse.ArgumentParser(); p.add_argument('--check',action='store_true'); args=p.parse_args(); runs,summary,report,figures=generate()
    outputs={RUNS:runs,SUMMARY:summary,REPORT:report,**{FIGURES/k:v for k,v in figures.items()}}
    if args.check:
        bad=[str(path.relative_to(ROOT)) for path,data in outputs.items() if not path.exists() or path.read_text(encoding='utf-8')!=data]
        if bad: raise SystemExit('stale simulated artifacts: '+', '.join(bad))
        print('validated deterministic simulated artifacts (not observations)'); return
    RUNS.parent.mkdir(parents=True,exist_ok=True); FIGURES.mkdir(parents=True,exist_ok=True)
    for path,data in outputs.items(): path.write_text(data,encoding='utf-8')
    print('generated synthetic pipeline-validation artifacts; NOT measured results')
if __name__=='__main__': main()
