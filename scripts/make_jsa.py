#!/usr/bin/env python3
"""Generate the Journal of Systems Architecture (Elsevier elsarticle) manuscript
from the ACM TECS source (paper/sagemm-tecs.tex).

The body, controller algorithm, tables, figures, and appendices are reused
verbatim so the two venue versions stay in sync: only the front matter
(document class, title block, abstract, keywords) and the back matter
(acknowledgements, bibliography style) are venue-specific.

Usage:
    python3 scripts/make_jsa.py            # writes paper/sagemm-jsa.tex

Cost note: JSA is a hybrid journal. Publish under the SUBSCRIPTION route for a
zero author fee; do NOT select Gold Open Access (which triggers an APC).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.join(HERE, os.pardir, "paper")
SRC = os.path.join(PAPER, "sagemm-tecs.tex")
DST = os.path.join(PAPER, "sagemm-jsa.tex")


def main():
    src = open(SRC).read().split("\n")

    def find(pred, start=0):
        for i in range(start, len(src)):
            if pred(src[i]):
                return i
        raise ValueError("marker not found")

    a0 = find(lambda l: l.strip() == r"\begin{abstract}")
    a1 = find(lambda l: l.strip() == r"\end{abstract}", a0)
    abstract = "\n".join(src[a0 + 1:a1]).strip()

    mk = find(lambda l: l.strip() == r"\maketitle")
    banner = find(lambda l: l.strip().startswith(r"\ifincludesimulation"), mk)
    acks = find(lambda l: l.strip() == r"\begin{acks}", banner)
    body = "\n".join(src[banner:acks]).rstrip()

    app = find(lambda l: l.strip() == r"\appendix")
    enddoc = find(lambda l: l.strip() == r"\end{document}", app)
    appendix = "\n".join(src[app:enddoc]).rstrip()

    preamble = PREAMBLE.replace("%%ABSTRACT%%", abstract)
    out = preamble + "\n" + body + "\n" + BACKMATTER + appendix + "\n\n\\end{document}\n"
    open(DST, "w").write(out)
    print("wrote", DST, len(out.split("\n")), "lines")


PREAMBLE = r"""%% =====================================================================
%% SAGE-MM --- Journal of Systems Architecture (Elsevier) submission
%% Template: Elsevier `elsarticle' class (preprint, single column).
%%
%% COST NOTE (zero author fee): JSA is a HYBRID journal. Publishing under the
%% traditional SUBSCRIPTION model is free of charge; Gold Open Access (APC)
%% is OPTIONAL. To pay nothing, at the "publishing option" step choose the
%% SUBSCRIPTION route and do NOT select open access. This source contains no
%% OA/CC option that would trigger an APC.
%%
%% GENERATED FILE -- do not edit by hand. Edit paper/sagemm-tecs.tex and rerun
%% scripts/make_jsa.py so the two venue versions stay in sync.
%% =====================================================================
\documentclass[preprint,12pt]{elsarticle}

\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{array}
\usepackage{graphicx}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{xcolor}

%% acmart provides \Description for accessibility; elsarticle does not. Define
%% it as a no-op so the shared body/simulation fragment compiles unchanged.
\providecommand{\Description}[1]{}

%% Internal layout mode (shared with the TECS source). A submission build MUST
%% set this false and supply provenance-backed observed results; the simulation
%% fragment is watermarked and must be removed before submission.
\newif\ifincludesimulation
\includesimulationtrue

\journal{Journal of Systems Architecture}

\begin{document}

\begin{frontmatter}

\title{SAGE-MM: Coordinating Heap Configuration, Interop Allocation, and
Page Reclamation in Memory-Constrained Embedded .NET Firmware}

\author[inst1]{Geunsik Lim\corref{cor1}}
\ead{leemgs@gmail.com}
\cortext[cor1]{Corresponding author.}
\affiliation[inst1]{organization={[Institution]},
  city={[City]},
  country={[Country]}}

\begin{abstract}
%%ABSTRACT%%
\end{abstract}

\begin{keyword}
Embedded runtimes \sep memory management \sep garbage collection \sep
managed/native interop \sep page reclamation \sep \texttt{madvise} \sep
online control \sep cross-layer coordination \sep .NET \sep Mono \sep
digital television
\end{keyword}

\end{frontmatter}
"""

BACKMATTER = r"""
%% =====================================================================
%% Elsevier-required author statements. Single author; no competing
%% interests; no specific funding. Edit these here (the generator), never in
%% the generated sagemm-jsa.tex. The same text is mirrored, human-readable, in
%% paper/DECLARATIONS_JSA.md for pasting into the submission system.
\section*{CRediT authorship contribution statement}
\textbf{Geunsik Lim:} Conceptualization, Methodology, Software, Validation,
Formal analysis, Investigation, Data curation, Writing --- original draft,
Writing --- review \& editing, Visualization.

\section*{Declaration of competing interest}
The author declares that he has no known competing financial interests or
personal relationships that could have appeared to influence the work
reported in this paper.

\section*{Funding}
This research did not receive any specific grant from funding agencies in the
public, commercial, or not-for-profit sectors.

\section*{Data availability}
The reference controller, safety guards, analyzer, evaluation protocol, and
the observed proxy-harness bundle are openly available in the SAGE-MM
repository. The proprietary vendor firmware patch and raw commercial-device
traces are withheld for confidentiality; the versioned observed-result bundle
underlying any reported device measurement will be released with the final
paper. No measured firmware result is reported until that bundle exists.

%% =====================================================================
\section*{Acknowledgements}
The author thanks the reviewers for feedback that sharpened the scope,
boundary, and evaluation protocol of this work.

%% =====================================================================
\bibliographystyle{elsarticle-num}
\bibliography{sagemm}

"""


if __name__ == "__main__":
    main()
