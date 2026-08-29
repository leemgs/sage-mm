# System and reproducibility boundary

## Reference kit versus evaluated firmware

| Mechanism | Lifecycle | Transparent to deployed application? | This repository |
|---|---|---:|---|
| `INITIAL_ALLOC` 16→64 MiB | vendor-runtime build, ARM32 only | yes after firmware replacement | not included; requires vendor Mono patch |
| Controller telemetry/policy hooks | runtime startup and online | yes after firmware replacement | user-space analogue, .NET 6+ |
| Clean executable-page reclamation | online | yes | Linux native reference helper |
| class-to-struct interop migration | source/build time | **no**: source edit, ABI review, recompilation | analyzer suggestion and examples |

The commercial target was a vendor fork of **Mono in a Tizen .NET 6 firmware**, not “Mono CoreCLR.” Mono and CoreCLR are distinct runtime implementations. A publishable artifact must record the vendor source commit, patch hashes, compiler, kernel/firmware identifiers, ARM32/ARM64 build flags, and the exact hosting interfaces used. This public kit has none of the proprietary patch and therefore makes no claim of binary transparency for a stock runtime.

The analyzer is advisory: converting reference wrappers to value types can change identity, boxing, copying, nullability, layout, and native ABI. Every diagnostic needs human review and recompilation. It must not be described as requiring no application modification.

## Artifact manifest required for reproduction

Archive: runtime patch/configuration; analyzer version and accepted diagnostics; workload driver and state-transition seeds; build/measurement scripts; device reset script; raw per-run telemetry; OOM/kernel logs; and anonymized aggregate production traces. Each result bundle should contain a machine-readable manifest with Git revision, device ID pseudonym, start/end UTC, treatment, seed, and checksum.
