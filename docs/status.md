# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Phase 0 metadata utilities added
**Current phase:** Phase 0 - PPMI access and feasibility audit (implementation started; no PPMI data audited).
**Branch:** `research/phase0-repository-audit`.
**Last debug:** `DBG-002` - metadata inventory utilities; repository checkout and execution blocked in this environment.
**Last decisions:** `D-008` through `D-001`.

**Created on the research branch:** explicit source-column mapping validation; CSV header, row-count, file-size and SHA-256 inventory helpers; keyed HMAC participant pseudonymization; participant-by-modality series-count aggregation; synthetic pytest coverage for these functions.

**Verified from source inspection:** files were committed to the research branch and are fetchable through the GitHub connector. The code avoids assuming PPMI source column names and keeps source participant IDs out of the generated coverage rows.

**Not verified:** local pytest, Ruff, CI, PPMI export mappings, PPMI cohort counts, MRI sequence coverage, visit alignment, endpoint availability, image QC, preprocessing, model training, RL behaviour, scientific performance or external validation. A local Git clone could not be completed because the environment could not resolve github.com; therefore no test result is claimed for these new modules.

**Next up:** run pytest and Ruff in a network-enabled checkout; inspect the actual approved PPMI CSV headers and MRI metadata; create versioned mapping files only after header review; then generate release-level and participant-by-modality coverage reports. Keep raw files and HMAC secrets outside Git.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
