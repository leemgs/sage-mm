# Highlights

**SAGE-MM: Coordinating Heap Configuration, Interop Allocation, and Page
Reclamation in Memory-Constrained Embedded .NET Firmware**

Elsevier Highlights — 3 to 5 bullet points, each ≤ 85 characters, describing
the core findings. Paste these into the "Highlights" file at submission.

- Coordinates heap, interop, and page reclamation under one embedded memory budget
- A narrow, fail-closed online controller adjusts one reclamation interval and gate
- Measured on ARM32/ARM64: ~24% lower peak PSS and ~37% lower GC tail pause
- The online controller recovers most reclamation-induced refaults at ~1% CPU
- Fail-safe when no gain exists; adverse loads expose a bounded regression
