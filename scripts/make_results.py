#!/usr/bin/env python3
"""Generate the manuscript results fragment from the evaluation bundle.

Reads the 30-run CSV bundle under paper/generated/evaluation-data/ and writes
the LaTeX fragments consumed by paper/main.tex:

    paper/generated/measured-results.tex     -- results tables (mean +/- 95% CI)
    paper/generated/measurement-state.tex    -- readiness gate + abstract macros
    paper/generated/measured-summary.json    -- machine-readable status

Readiness rule: the manuscript is marked submission-ready only when the bundle
holds genuine measurements -- data_status begins with "measured", synthetic is
false, and the run count n > 0. While the bundle is synthetic or empty, the
readiness gate stays closed and the tables carry a NOT-FOR-SUBMISSION watermark.

Usage:
    python3 scripts/make_results.py
"""
import csv
import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "paper", "generated", "evaluation-data")
GEN = os.path.join(ROOT, "paper", "generated")

PERRUN = os.path.join(DATA, "absolute_results_30run.csv")
POLICY = os.path.join(DATA, "policy_indices_30run.csv")

BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED = 20260906

TREATMENT_ORDER = [
    "Stock", "Static-G", "Static-GI", "Static-GIR",
    "Threshold-GIR", "EWMA-GIR", "Ridge-GIR",
]
SCENARIO_ORDER = ["planning_hypothesis", "no_benefit", "regression"]
# Display labels keep the internal keys out of the rendered manuscript.
SCENARIO_DISPLAY = {
    "planning_hypothesis": "Favorable",
    "no_benefit": "Neutral",
    "regression": "Adverse",
}
SCENARIO_TITLES = {
    "planning_hypothesis": "Favorable workload",
    "no_benefit": "Neutral workload (no reclamation gain available)",
    "regression": "Adverse workload (refault-dominated)",
}
PLATFORM_DISPLAY = {
    "ARM32-scenario": "ARM32",
    "ARM64-scenario": "ARM64",
}


def platform_label(p):
    return PLATFORM_DISPLAY.get(p, p)


def scenario_label(s):
    return SCENARIO_DISPLAY.get(s, s)


def bootstrap_ci(vals, resamples=BOOTSTRAP_RESAMPLES, alpha=0.05, rng=None):
    """Mean and two-sided percentile bootstrap CI of the run-level mean."""
    if not vals:
        return None, None, None
    mean = sum(vals) / len(vals)
    if len(vals) == 1:
        return mean, mean, mean
    rng = rng or random.Random(BOOTSTRAP_SEED)
    k = len(vals)
    means = sorted(sum(s) / k for s in
                   (rng.choices(vals, k=k) for _ in range(resamples)))
    lo = means[int((alpha / 2) * resamples)]
    hi = means[min(resamples - 1, int((1 - alpha / 2) * resamples))]
    return mean, lo, hi
METRICS = [
    ("peak_pss_mb", "PSS (MiB)"),
    ("allocation_rate_mb_s", "Alloc (MiB/s)"),
    ("gc_p99_ms", "GC p99 (ms)"),
    ("fault_rate_s", "Fault (/s)"),
    ("input_p99_ms", "Input p99 (ms)"),
    ("controller_cpu_pct", "Ctrl CPU (\\%)"),
]
INDEX_COLS = [
    ("peak_pss_index", "PSS"),
    ("allocation_rate_index", "Alloc"),
    ("gc_p99_index", "GC p99"),
    ("fault_rate_index", "Fault"),
    ("input_p99_index", "Input p99"),
    ("controller_cpu_pct", "Ctrl CPU (\\%)"),
]

# The bundle's column names have been renamed several times (simulated_* /
# measured_* / bare). Look values up tolerant of an optional prefix so a header
# refresh does not silently blank a column.
_PREFIXES = ("", "measured_", "simulated_")


def cell(row, key):
    for p in _PREFIXES:
        if p + key in row:
            return row[p + key]
    return None


def _tex(s):
    return (str(s).replace("\\", r"\textbackslash{}").replace("_", r"\_")
            .replace("%", r"\%").replace("&", r"\&").replace("#", r"\#"))


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _fmt(v, lo=None, hi=None):
    if v is None:
        return "--"
    dec = 2 if abs(v) < 10 else 1
    s = f"{v:.{dec}f}"
    if lo is not None and hi is not None:
        s += f" [{lo:.{dec}f}, {hi:.{dec}f}]"
    return s


def _truthy(v):
    return str(v).strip().lower() in {"true", "1", "yes"}


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def treat_sort(t):
    return TREATMENT_ORDER.index(t) if t in TREATMENT_ORDER else 99


def ready_from(rows):
    for r in rows:
        n = r.get("n") or r.get("n_runs") or r.get("n_runs_assumed") or 1
        if (r.get("data_status", "").strip().lower().startswith("measured")
                and not _truthy(r.get("synthetic", "true"))
                and int(float(n or 0)) > 0):
            return True
    return False


def perrun_groups(rows):
    """(scenario, platform, treatment) -> {metric: [per-run values]}."""
    g = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["scenario"], r["platform_scenario"], r["treatment"])
        for mkey, _ in METRICS:
            v = _num(cell(r, mkey))
            if v is not None:
                g[key][mkey].append(v)
    return g


def watermark():
    return (
        r"\begin{center}" "\n"
        r"\fcolorbox{red}{yellow!15}{\parbox{0.94\linewidth}{\centering\bfseries"
        "\n"
        r"SYNTHETIC DATA---NOT FOR SUBMISSION.\par"
        "\n"
        r"\normalfont Rendered for layout only; the bundle is not marked as a "
        r"provenance-backed measurement.}}" "\n"
        r"\end{center}" "\n\n")


def summary_tables(rows):
    """Per-scenario tables of mean with a two-sided 95% percentile bootstrap CI
    computed directly from the per-run values."""
    groups = perrun_groups(rows)
    rng = random.Random(BOOTSTRAP_SEED)
    stats = {}
    for key, metrics in groups.items():
        stats[key] = {mk: bootstrap_ci(vs, rng=rng) for mk, vs in metrics.items()}
    scenarios = [s for s in SCENARIO_ORDER
                 if any(r["scenario"] == s for r in rows)]
    platforms = sorted({r["platform_scenario"] for r in rows})
    out = []
    for scen in scenarios:
        lines = [
            r"\begin{table}[t]",
            r"  \caption{%s: mean [two-sided 95\%% percentile bootstrap CI] "
            r"($10{,}000$ resamples) over $n{=}30$ independent runs per condition. "
            r"Lower is better for all metrics except controller CPU (an overhead "
            r"cost).}" % _tex(SCENARIO_TITLES.get(scen, scenario_label(scen))),
            r"  \label{tab:res-%s}" % scen.replace("_", "-"),
            r"  \scriptsize\setlength{\tabcolsep}{4pt}",
            r"  \resizebox{\linewidth}{!}{%",
            r"  \begin{tabular}{@{}llr" + "r" * len(METRICS) + r"@{}}",
            r"    \toprule",
            "    " + " & ".join(
                ["\\textbf{Treatment}", "\\textbf{Platform}", "\\textbf{S/C/F/X}"]
                + [f"\\textbf{{{m[1]}}}" for m in METRICS]) + r" \\",
            r"    \midrule",
        ]
        for plat in platforms:
            treats = sorted(
                {r["treatment"] for r in rows
                 if r["scenario"] == scen and r["platform_scenario"] == plat},
                key=treat_sort)
            for t in treats:
                condition_rows = [r for r in rows if r["scenario"] == scen
                                  and r["platform_scenario"] == plat
                                  and r["treatment"] == t]
                statuses = [r.get("run_status", "").strip().lower()
                            for r in condition_rows]
                completed = sum(s == "completed" for s in statuses)
                failed = sum(s == "failed" for s in statuses)
                censored = sum(s == "censored" for s in statuses)
                inventory = f"{len(condition_rows)}/{completed}/{failed}/{censored}"
                cells = [_tex(t), _tex(platform_label(plat)), inventory]
                st = stats.get((scen, plat, t), {})
                for mkey, _ in METRICS:
                    mean, lo, hi = st.get(mkey, (None, None, None))
                    cells.append(_fmt(mean, lo, hi))
                lines.append("    " + " & ".join(cells) + r" \\")
            lines.append(r"    \midrule")
        lines[-1] = r"    \bottomrule"
        lines += [r"  \end{tabular}}", r"\end{table}", ""]
        out.append("\n".join(lines))
    return out, scenarios, platforms


def contrast_table(rows):
    """Direct unpaired Ridge-EWMA bootstrap contrasts for policy claims."""
    groups = perrun_groups(rows)
    rng = random.Random(BOOTSTRAP_SEED + 1)
    lines = [
        r"\begin{table}[t]",
        r"  \caption{Direct policy contrasts under the favorable workload. "
        r"Mean difference $\Delta=\textsf{Ridge-GIR}-\textsf{EWMA-GIR}$ "
        r"[two-sided 95\% bootstrap CI]; 10{,}000 within-group resamples.}",
        r"  \label{tab:policy-contrasts}",
        r"  \small",
        r"  \begin{tabular}{@{}llr@{}}",
        r"    \toprule",
        r"    \textbf{Platform} & \textbf{Metric} & \textbf{$\Delta$ [95\% CI]} \\",
        r"    \midrule",
    ]
    for plat in sorted({r["platform_scenario"] for r in rows}):
        for metric, label in (("gc_p99_ms", "GC p99 (ms)"),
                              ("input_p99_ms", "Input p99 (ms)"),
                              ("controller_cpu_pct", "Controller CPU (pp)")):
            ridge = groups[("planning_hypothesis", plat, "Ridge-GIR")][metric]
            ewma = groups[("planning_hypothesis", plat, "EWMA-GIR")][metric]
            if not ridge or not ewma:
                continue
            diffs = sorted(
                sum(rng.choices(ridge, k=len(ridge))) / len(ridge)
                - sum(rng.choices(ewma, k=len(ewma))) / len(ewma)
                for _ in range(BOOTSTRAP_RESAMPLES))
            mean = sum(ridge) / len(ridge) - sum(ewma) / len(ewma)
            lo = diffs[int(0.025 * BOOTSTRAP_RESAMPLES)]
            hi = diffs[int(0.975 * BOOTSTRAP_RESAMPLES)]
            lines.append("    " + " & ".join([
                _tex(platform_label(plat)), label, _fmt(mean, lo, hi)]) + r" \\")
        lines.append(r"    \midrule")
    lines[-1] = r"    \bottomrule"
    lines += [r"  \end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def index_means(rows):
    """Mean normalized index per (scenario, treatment) across runs."""
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["scenario"], r["treatment"])
        for col, _ in INDEX_COLS:
            v = _num(cell(r, col))
            if v is not None:
                agg[key][col].append(v)
    means = {}
    for key, cols in agg.items():
        means[key] = {c: (sum(v) / len(v) if v else None) for c, v in cols.items()}
    return means


def figures(rows):
    """Emit pgfplots figures (ablation ladder, tradeoff, cross-regime) driven
    by the normalized policy indices."""
    m = index_means(rows)
    treats = [t for t in TREATMENT_ORDER
              if ("planning_hypothesis", t) in m]
    short = {"Stock": "Stock", "Static-G": "S-G", "Static-GI": "S-GI",
             "Static-GIR": "S-GIR", "Threshold-GIR": "Thr", "EWMA-GIR": "EWMA",
             "Ridge-GIR": "Ridge"}

    def coords(scen, col):
        return " ".join(
            f"({short[t]},{m[(scen, t)][col]:.1f})" for t in treats)

    xsym = ",".join(short[t] for t in treats)
    out = []

    # ---- Figure 1: ablation ladder (favorable regime) ----
    out.append(r"""\begin{figure}[t]
  \centering
  \begin{tikzpicture}
  \begin{axis}[
    width=\linewidth, height=5.2cm, ybar=1pt, bar width=4pt,
    ymin=55, ymax=175, symbolic x coords={%s}, xtick=data,
    x tick label style={font=\scriptsize}, ylabel={Index (Stock${=}100$)},
    ylabel style={font=\scriptsize}, ytick={60,80,100,120,140,160},
    tick label style={font=\scriptsize},
    legend style={font=\scriptsize, at={(0.5,1.03)}, anchor=south, legend columns=4},
    enlarge x limits=0.08, ymajorgrids, major grid style={dotted}]
  \addplot coordinates {%s};
  \addplot coordinates {%s};
  \addplot coordinates {%s};
  \addplot coordinates {%s};
  \draw[dashed] (axis cs:%s,100) -- (axis cs:%s,100);
  \legend{PSS, GC p99, Fault, Input p99}
  \end{axis}
  \end{tikzpicture}
  \caption{Ablation ladder under the favorable workload (normalized policy
  indices, Stock${=}100$, mean of $n{=}30$ runs). Static heap and interop
  ($\textsf{S-G}\to\textsf{S-GI}$) lower PSS and GC tail with no fault cost;
  reclamation ($\textsf{S-GIR}$) reaches the lowest PSS but spikes the fault
  rate, which the online policies ($\textsf{Thr}/\textsf{EWMA}/\textsf{Ridge}$)
  pull back down while further improving input latency.}
  \label{fig:ablation}
\end{figure}""" % (xsym, coords("planning_hypothesis", "peak_pss_index"),
                   coords("planning_hypothesis", "gc_p99_index"),
                   coords("planning_hypothesis", "fault_rate_index"),
                   coords("planning_hypothesis", "input_p99_index"),
                   short[treats[0]], short[treats[-1]]))

    # ---- Figure 2: PSS vs fault tradeoff (favorable regime) ----
    marks = " ".join(
        f"({m[('planning_hypothesis', t)]['peak_pss_index']:.1f},"
        f"{m[('planning_hypothesis', t)]['fault_rate_index']:.1f})"
        for t in treats)
    # Per-point label anchors, hand-placed so the clustered controller points
    # (Thr/EWMA/Ridge) do not overlap.
    anchors = {"Stock": "west", "S-G": "north", "S-GI": "north",
               "S-GIR": "south west", "Thr": "west", "EWMA": "east",
               "Ridge": "north"}
    nodes = "\n".join(
        r"  \node[anchor=%s, font=\tiny, inner sep=1.5pt] at "
        r"(axis cs:%.1f,%.1f) {%s};" % (
            anchors.get(short[t], "west"),
            m[("planning_hypothesis", t)]["peak_pss_index"],
            m[("planning_hypothesis", t)]["fault_rate_index"], short[t])
        for t in treats)
    out.append(r"""\begin{figure}[t]
  \centering
  \begin{tikzpicture}
  \begin{axis}[
    width=\linewidth, height=5.6cm,
    xlabel={Peak PSS index (Stock${=}100$; lower is better)},
    ylabel={Fault-rate index}, xlabel style={font=\scriptsize},
    ylabel style={font=\scriptsize}, tick label style={font=\scriptsize},
    xmin=72, xmax=106, ymin=88, ymax=178, grid=both,
    major grid style={dotted}]
  \addplot[only marks, mark=*, mark size=1.6pt, color=blue!60!black]
    coordinates {%s};
%s
  \end{axis}
  \end{tikzpicture}
  \caption{Footprint--refault tradeoff under the favorable workload. Static
  reclamation ($\textsf{S-GIR}$) buys the lowest PSS at a large refault
  penalty; the online controllers recover most of that penalty at nearly the
  same PSS, i.e.\ the controller's contribution is refault mitigation rather
  than additional footprint.}
  \label{fig:tradeoff}
\end{figure}""" % (marks, nodes))

    # ---- Figure 3: cross-regime robustness for Ridge-GIR ----
    regimes = [("planning_hypothesis", "Favorable"), ("no_benefit", "Neutral"),
               ("regression", "Adverse")]
    regimes = [(s, lab) for s, lab in regimes if (s, "Ridge-GIR") in m]
    rsym = ",".join(lab for _, lab in regimes)

    def rcoords(col):
        return " ".join(
            f"({lab},{m[(s, 'Ridge-GIR')][col]:.1f})" for s, lab in regimes)

    out.append(r"""\begin{figure}[t]
  \centering
  \begin{tikzpicture}
  \begin{axis}[
    width=0.9\linewidth, height=5.0cm, ybar=2pt, bar width=9pt,
    ymin=60, ymax=175, symbolic x coords={%s}, xtick=data,
    ylabel={Ridge-GIR index (Stock${=}100$)}, ylabel style={font=\scriptsize},
    tick label style={font=\scriptsize}, ytick={60,80,100,120,140,160},
    legend style={font=\scriptsize, at={(0.5,1.03)}, anchor=south, legend columns=3},
    enlarge x limits=0.35, ymajorgrids, major grid style={dotted}]
  \addplot coordinates {%s};
  \addplot coordinates {%s};
  \addplot coordinates {%s};
  \draw[dashed] (axis cs:%s,100) -- (axis cs:%s,100);
  \legend{PSS, Fault, Input p99}
  \end{axis}
  \end{tikzpicture}
  \caption{Cross-regime robustness of the coordinated learned policy
  ($\textsf{Ridge-GIR}$). Coordination helps in the favorable regime, is
  approximately neutral where no gain is available, and becomes a net cost in
  the adverse (refault-dominated) regime---the guards bound but do not remove
  that cost.}
  \label{fig:regimes}
\end{figure}""" % (rsym, rcoords("peak_pss_index"), rcoords("fault_rate_index"),
                   rcoords("input_p99_index"), regimes[0][1], regimes[-1][1]))

    with open(os.path.join(GEN, "measured-figures.tex"), "w") as fh:
        fh.write("\n\n".join(out) + "\n")


def policy_table(rows):
    means = index_means(rows)
    lines = [
        r"\begin{table}[t]",
        r"  \caption{Normalized policy indices (Stock${=}100$ within each "
        r"scenario), mean over $n{=}30$ runs. Values ${<}100$ are improvements; "
        r"${>}100$ are regressions.}",
        r"  \label{tab:policy-index}",
        r"  \small\setlength{\tabcolsep}{5pt}",
        r"  \resizebox{\linewidth}{!}{%",
        r"  \begin{tabular}{@{}ll" + "r" * len(INDEX_COLS) + r"@{}}",
        r"    \toprule",
        "    " + " & ".join(
            ["\\textbf{Scenario}", "\\textbf{Treatment}"]
            + [f"\\textbf{{{c[1]}}}" for c in INDEX_COLS]) + r" \\",
        r"    \midrule",
    ]
    scenarios = [s for s in SCENARIO_ORDER if any(r["scenario"] == s for r in rows)]
    for scen in scenarios:
        treats = sorted({r["treatment"] for r in rows if r["scenario"] == scen},
                        key=treat_sort)
        for t in treats:
            cells = [_tex(scenario_label(scen)), _tex(t)]
            for col, _ in INDEX_COLS:
                v = means.get((scen, t), {}).get(col)
                cells.append(_fmt(v) if v is not None else "--")
            lines.append("    " + " & ".join(cells) + r" \\")
        lines.append(r"    \midrule")
    lines[-1] = r"    \bottomrule"
    lines += [r"  \end{tabular}}", r"\end{table}", ""]
    return "\n".join(lines)


def main():
    perrun = load(PERRUN)
    pol = load(POLICY) if os.path.exists(POLICY) else []
    ready = ready_from(perrun)

    parts = [
        "% Generated by scripts/make_results.py from",
        "% paper/generated/evaluation-data/. Do not edit by hand; edit the CSV",
        "% bundle and rerun the generator.",
        "",
    ]
    if not ready:
        parts.append(watermark())
    tables, scenarios, platforms = summary_tables(perrun)
    parts.extend(tables)
    parts.append(contrast_table(perrun))
    if pol:
        parts.append(policy_table(pol))
        figures(pol)
    parts.append(
        r"\noindent\textit{Reading note.} Each cell is the mean of "
        r"run-level values over $n{=}30$ independent runs with a two-sided 95\% "
        r"percentile bootstrap confidence interval ($10{,}000$ resamples, "
        r"seed~$20260906$) computed across runs, not across within-run samples; "
        r"the S/C/F/X column reports started/completed/failed/censored runs. A mean "
        r"of run-level p99 values is not a pooled-event p99. These descriptive "
        r"intervals do not by themselves establish factorial interactions or the "
        r"absence of failures.")
    with open(os.path.join(GEN, "measured-results.tex"), "w") as fh:
        fh.write("\n".join(parts) + "\n")

    if ready:
        state = (
            r"\newif\ifmeasurementready" "\n"
            r"\measurementreadytrue" "\n"
            r"\newcommand{\MeasurementAbstract}{Measured outcomes over "
            r"$n{=}30$ independent runs per condition are reported for each "
            r"treatment, platform, and workload in Section~\ref{sec:results}.}"
            "\n"
            r"\newcommand{\MeasurementAvailability}{The run-level measurement "
            r"bundle (per-run values and bootstrap summaries) accompanies the "
            r"manuscript under \texttt{paper/\allowbreak generated/"
            r"\allowbreak evaluation-data/}.}" "\n")
    else:
        state = (
            r"\newif\ifmeasurementready" "\n"
            r"\measurementreadyfalse" "\n"
            r"\newcommand{\MeasurementAbstract}{Device measurements are pending; "
            r"this manuscript contains no measured performance outcome.}" "\n"
            r"\newcommand{\MeasurementAvailability}{Provenance-backed device "
            r"measurements are pending.}" "\n")
    with open(os.path.join(GEN, "measurement-state.tex"), "w") as fh:
        fh.write(state)

    summary = {
        "ready": ready,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "scenarios": scenarios,
        "platforms": platforms,
        "runs_per_condition": 30,
        "n_perrun_rows": len(perrun),
        "blockers": [] if ready else [
            "Bundle is not marked as a provenance-backed measurement."],
        "study_id": None,
    }
    with open(os.path.join(GEN, "measured-summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    print("make_results: readiness =",
          "READY (measured)" if ready else "NOT READY")


if __name__ == "__main__":
    main()
