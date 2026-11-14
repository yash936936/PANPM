# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Source-independent schema contracts added
**Current phase:** Phase 0 - PPMI access and feasibility audit (software scaffold in progress; no PPMI data available).
**Branch:** `research/phase0-repository-audit`.
**Last debug:** `DBG-003` - canonical schema contracts; tests authored but not executed.
**Last decisions:** `D-009` - proceed with source-independent validation while data access is unavailable.

**Created:** `src/data/schema.py` defines minimum internal table contracts for participants, clinical visits, imaging scans, progression targets and split manifests. It validates required columns, declared unique keys and participant foreign-key links. `tests/test_data_schema.py` uses small synthetic rows to exercise these checks.

**Input status:** PPMI access status is none; no PPMI files or data dictionary exports are available in this workspace. Therefore no PPMI field mapping, cohort count, modality coverage, endpoint feasibility or MRI sequence decision can be made.

**Not verified:** local pytest, Ruff, CI, PPMI export mappings, PPMI cohort counts, MRI sequence coverage, visit alignment, endpoint availability, image QC, preprocessing, model training, RL behaviour, scientific performance or external validation.

**Next up:** run tests and Ruff in a local checkout; obtain PPMI approval and download the official data dictionary plus approved de-identified export headers; map source fields only after inspection.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
