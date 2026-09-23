# Zenodo deposit

`sage-mm-dataset.zip` is the archive prepared for deposit on Zenodo. It packages
the measurement bundle under `paper/measured/evaluation-data/` together with the
generator/validator scripts and dataset metadata (`README.md`, `LICENSE.txt`
CC-BY-4.0, `CITATION.cff`).

Contents of the archive:

```
sage-mm-dataset/
  README.md            dataset description, file map, validation/regeneration
  LICENSE.txt          CC-BY-4.0 (data & docs)
  CITATION.cff         citation metadata (Geunsik Lim, ORCID 0000-0003-1845-7132)
  evaluation-data/     8 measured files + manifest/provenance/failures/checksums + templates/
  scripts/             make_results.py, validate_bundle.py
```

All eight measured files verify with `sha256sum -c checksums.sha256`.

## Deposit

Deposited on Zenodo under DOI **10.5281/zenodo.22918517**
(https://zenodo.org/records/22918517). The manuscript's Data Availability
statement cites this DOI.
