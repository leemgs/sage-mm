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
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "paper", "generated", "evaluation-data")
GEN = os.path.join(ROOT, "paper", "generated")

SUMMARY = os.path.join(DATA, "summary_30run.csv")
POLICY = os.path.join(DATA, "policy_indices_30run.csv")

TREATMENT_ORDER = [
    "Stock", "Static-G", "Static-GI", "Static-GIR",
    "Threshold-GIR", "EWMA-GIR", "Ridge-GIR",
]
SCENARIO_ORDER = ["planning_hypothesis", "no_benefit", "regression"]
SCENARIO_TITLES = {
    "planning_hypothesis": "Primary workload",
    "no_benefit": "No-benefit control workload",
    "regression": "Regression control workload",
}
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


def _fmt(v, hw=None):
    if v is None:
        return "--"
    dec = 2 if abs(v) < 10 else 1
    s = f"{v:.{dec}f}"
    if hw is not None:
        s += f"\\,$\\pm$\\,{hw:.{dec}f}"
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
        n = r.get("n") or r.get("n_runs") or r.get("n_runs_assumed") or 0
        if (r.get("data_status", "").strip().lower().startswith("measured")
                and not _truthy(r.get("synthetic", "true"))
                and int(float(n or 0)) > 0):
            return True
    return False


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
    # index: (scenario, platform, treatment, metric) -> row
    idx = {(r["scenario"], r["platform_scenario"], r["treatment"], r["metric"]): r
           for r in rows}
    scenarios = [s for s in SCENARIO_ORDER
                 if any(r["scenario"] == s for r in rows)]
    platforms = sorted({r["platform_scenario"] for r in rows})
    out = []
    for scen in scenarios:
        lines = [
            r"\begin{table}[t]",
            r"  \caption{%s: mean $\pm$ 95\%% CI over $n{=}30$ independent runs "
            r"per condition. Lower is better for all metrics except controller "
            r"CPU (an overhead cost).}" % _tex(SCENARIO_TITLES.get(scen, scen)),
            r"  \label{tab:res-%s}" % scen.replace("_", "-"),
            r"  \scriptsize\setlength{\tabcolsep}{4pt}",
            r"  \begin{tabular}{@{}ll" + "r" * len(METRICS) + r"@{}}",
            r"    \toprule",
            "    " + " & ".join(
                ["\\textbf{Treatment}", "\\textbf{Platform}"]
                + [f"\\textbf{{{m[1]}}}" for m in METRICS]) + r" \\",
            r"    \midrule",
        ]
        for plat in platforms:
            treats = sorted(
                {r["treatment"] for r in rows
                 if r["scenario"] == scen and r["platform_scenario"] == plat},
                key=treat_sort)
            for t in treats:
                cells = [_tex(t), _tex(plat)]
                for mkey, _ in METRICS:
                    r = idx.get((scen, plat, t, mkey))
                    if r is None:
                        cells.append("--")
                        continue
                    mean = _num(cell(r, "mean"))
                    lo, hi = _num(cell(r, "ci95_low")), _num(cell(r, "ci95_high"))
                    hw = (hi - lo) / 2 if (lo is not None and hi is not None) else None
                    cells.append(_fmt(mean, hw))
                lines.append("    " + " & ".join(cells) + r" \\")
            lines.append(r"    \midrule")
        lines[-1] = r"    \bottomrule"
        lines += [r"  \end{tabular}", r"\end{table}", ""]
        out.append("\n".join(lines))
    return out, scenarios, platforms


def policy_table(rows):
    # aggregate mean of each index across runs per (scenario, treatment)
    agg = defaultdict(lambda: defaultdict(list))
    for r in rows:
        key = (r["scenario"], r["treatment"])
        for col, _ in INDEX_COLS:
            v = _num(cell(r, col))
            if v is not None:
                agg[key][col].append(v)
    lines = [
        r"\begin{table}[t]",
        r"  \caption{Normalized policy indices (Stock${=}100$ within each "
        r"scenario), mean over $n{=}30$ runs. Values ${<}100$ are improvements; "
        r"${>}100$ are regressions.}",
        r"  \label{tab:policy-index}",
        r"  \small\setlength{\tabcolsep}{5pt}",
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
            cells = [_tex(scen), _tex(t)]
            for col, _ in INDEX_COLS:
                vals = agg[(scen, t)][col]
                cells.append(_fmt(sum(vals) / len(vals)) if vals else "--")
            lines.append("    " + " & ".join(cells) + r" \\")
        lines.append(r"    \midrule")
    lines[-1] = r"    \bottomrule"
    lines += [r"  \end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def main():
    summ = load(SUMMARY)
    pol = load(POLICY) if os.path.exists(POLICY) else []
    ready = ready_from(summ)

    parts = [
        "% Generated by scripts/make_results.py from",
        "% paper/generated/evaluation-data/. Do not edit by hand; edit the CSV",
        "% bundle and rerun the generator.",
        "",
    ]
    if not ready:
        parts.append(watermark())
    tables, scenarios, platforms = summary_tables(summ)
    parts.extend(tables)
    if pol:
        parts.append(policy_table(pol))
    parts.append(
        r"\noindent\textit{Reading note.} Each cell is the mean of "
        r"run-level values over $n{=}30$ independent runs with a two-sided 95\% "
        r"confidence interval; failed and censored runs, if any, remain in the "
        r"run inventory. A mean of run-level p99 values is not a pooled-event "
        r"p99. These descriptive intervals do not by themselves establish "
        r"factorial interactions or the absence of failures.")
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
            r"manuscript under \texttt{paper/generated/evaluation-data/}.}" "\n")
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
        "bootstrap_resamples": 10000,
        "bootstrap_seed": 20260906,
        "scenarios": scenarios,
        "platforms": platforms,
        "runs_per_condition": 30,
        "n_summary_rows": len(summ),
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
