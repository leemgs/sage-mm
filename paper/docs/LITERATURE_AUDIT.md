# Literature audit and positioning

The manuscript bibliography must be checked item-by-item against the claim each citation supports. Remove the cited JavaScript dynamic-taint paper from any Tizen profiler claim and the Concurrent Pascal operating-system paper from managed/native interop claims. Prefer authoritative .NET/Mono runtime documentation and source for collector and interop behavior.

Reviewer-suggested works must be cited accurately and positioned by domain.
The citation audit below is resolved; the matching records are in
`paper/sagemm.bib`.

* H. Sun et al., “AGC: An Adaptive Workload Burst-Aware Garbage Collection Mechanism for High-Performance SSDs,” *IEEE Transactions on Computers*. Distinct from the DumpKV preprint the reviewer’s duplicated DOI pointed to; cited by its stable IEEE Xplore record (article 11298441, <https://ieeexplore.ieee.org/document/11298441>). The IEEE DOI could not be confirmed from a primary source at edit time, so none is asserted in the bib — take the final volume/issue/pages/DOI from the Xplore page. Storage GC; not a managed-runtime baseline.
* W. Zhao, S. M. Blackburn, and K. S. McKinley, “Low-Latency, High-Throughput Garbage Collection,” *PLDI* (2022), pp. 76–91, DOI: 10.1145/3519939.3523440 (confirmed via the ACM Digital Library). LXR is a relevant managed-runtime design comparison but requires a collector port.
* M. Wu et al., “Platinum: A CPU-Efficient Concurrent Garbage Collector for Tail-Reduction of Interactive Services,” *USENIX ATC* (2020), pp. 159–172, <https://www.usenix.org/conference/atc20/presentation/wu-mingyu>. USENIX ATC papers carry no publisher DOI; the ACM index identifier 10.5555/3489146.3489157 is not an author-assigned DOI and is not cited as one.
* Z. Zhuang, X. Zeng, and Z. Chen, “DumpKV: Learning Based Lifetime Aware Garbage Collection for Key Value Separation in LSM-Tree,” *PVLDB* 18(4) (2024), pp. 1223–1236, DOI: 10.14778/3717755.3717778 (confirmed via the ACM Digital Library and vldb.org). The reviewer’s repeated arXiv DOI (2406.01250) is this work’s preprint, not the AGC paper. Storage GC; only motivates lightweight learning comparisons.

The novelty claim should be limited to coordinated integration and safety-aware control at the embedded Mono/Linux boundary, supported by factorial interaction effects. Static heap sizing, class-to-struct conversion, `madvise`, EWMA, and ridge regression are not individually novel.
