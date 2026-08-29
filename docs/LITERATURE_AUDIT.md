# Literature audit and positioning

The manuscript bibliography must be checked item-by-item against the claim each citation supports. Remove the cited JavaScript dynamic-taint paper from any Tizen profiler claim and the Concurrent Pascal operating-system paper from managed/native interop claims. Prefer authoritative .NET/Mono runtime documentation and source for collector and interop behavior.

Reviewer-suggested works must be cited accurately and positioned by domain:

* H. Sun et al., “AGC: An Adaptive Workload Burst-Aware Garbage Collection Mechanism for High-Performance SSDs,” *IEEE Transactions on Computers* (2025), preprint DOI supplied by the reviewer: 10.48550/arXiv.2406.01250. Verify and add the final IEEE DOI before submission. Storage GC; not a managed-runtime baseline.
* W. Zhao, S. M. Blackburn, and K. S. McKinley, “Low-Latency, High-Throughput Garbage Collection,” *PLDI* (2022), pp. 76–91, DOI: 10.1145/3519939.3523440. LXR is a relevant managed-runtime design comparison but requires a collector port.
* M. Wu et al., “Platinum: A CPU-Efficient Concurrent Garbage Collector for Tail-Reduction of Interactive Services,” *USENIX ATC* (2020), pp. 159–172. Verify venue identifiers in the final bibliography; do not present ACM index identifier 10.5555/3489146.3489157 as an author-assigned DOI.
* Z. Zhuang, X. Zeng, and Z. Chen, “DumpKV: Learning Based Lifetime Aware Garbage Collection for Key Value Separation in LSM-Tree,” *PVLDB* 18(4) (2024), pp. 1223–1236. Verify its DOI from the publisher. The review's repeated arXiv DOI points to a different work and must not be copied. This is storage GC and only motivates lightweight learning comparisons.

The novelty claim should be limited to coordinated integration and safety-aware control at the embedded Mono/Linux boundary, supported by factorial interaction effects. Static heap sizing, class-to-struct conversion, `madvise`, EWMA, and ridge regression are not individually novel.
