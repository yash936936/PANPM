# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Public PPMI tooling reviewed; recursive CSV discovery added
**Current phase:** Phase 0 - PPMI access and feasibility audit (software scaffold only; no PPMI data available).
**Branch:** `research/phase0-repository-audit`.
**Last debug:** `DBG-004` - public tooling review and CSV tree inventory; tests authored but not executed.
**Last decisions:** `D-010` - upstream tooling treated as reference, not source truth.

**Reviewed:** public documentation and code from MJFF Research Community PIE, PIE-clean, NetNeuroLab markello_ppmisnf, and the official PPMI Data Resources page. Added `docs/external-references.md` with source links, reusable patterns and cautions. In particular, upstream PIE warns against relying only on LONI's Weighting label for T1 selection; PANPM will verify acquisition metadata and DICOM headers against the actual release before sequence selection.

**Created:** `discover_csv_exports` and `inventory_csv_tree` recursively enumerate CSV exports and record relative path, header, row count, size and SHA-256 without loading participant-level rows. Added synthetic tests.

**Not verified:** local pytest, Ruff, CI, official PPMI field mappings, actual export headers, participant counts, MRI coverage, endpoint completeness, image QC, preprocessing, model training, RL behaviour or scientific results.

**Next up:** obtain official PPMI Data Dictionary, Code List and Data User Guide from the Data Resources page; once downloaded, inspect and extract their actual definitions. Obtain approved access before using participant-level exports or images.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
