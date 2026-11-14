# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Add explicit medication-state progression target helpers
**Current phase:** Phase 0 - source-document review and generic safeguards implemented; participant-level feasibility audit still requires approved PPMI exports.
**Branch:** `research/phase0-progression-targets`.
**Previous PR:** [#2](https://github.com/yash936936/PANPM/pull/2) merged into `main`.
**Last debug:** `DBG-008` - deterministic progression target selection helpers added.
**Last decision:** `D-013` - do not hard-code target windows or medication state before export audit.

**Added:** `src/data/progression_targets.py` provides exact-state, date-window assessment selection and state-consistent score change. `tests/test_progression_targets.py` adds synthetic cases for exact state matching, inclusive window boundaries, missing scores, ties, chronology and delta direction. `docs/progression-targets.md` documents the selection contract and unresolved protocol choices.

**Important:** the helper requires the caller to provide the target date, tolerance in days and normalized medication-state label. It does not decide 12/24-month windows, choose ON/OFF/untreated, map PPMI source codes, handle DBS eligibility or derive LEDD. Tied closest assessments raise an error instead of being selected arbitrarily.

**Previous work:** PR #2 merged the PPMI source catalog and contracts for MRI and progression/medication tables. No passing CI result was available for its merge commit when checked; tests have not been run locally.

**Not verified:** approved participant-level exports, actual assessment-state coverage, medication exposure, target availability, local pytest/Ruff or CI for this branch. No model or RL training has begun.

**Next:** validate the source-state mapping and progression target coverage against approved `NUPDRS3TRT` and `LEDDLOG` exports before selecting a clinical endpoint rule.

---

## 2026-11-15 - Added medication-aware progression source contracts
**Current phase:** Phase 0 - reference-document review complete; actual-data feasibility audit still requires approved PPMI exports.
**Branch:** `research/phase0-ppmi-dictionary`.
**PR:** [#2](https://github.com/yash936936/PANPM/pull/2), now merged.
**Last debug:** `DBG-007` - progression and medication fields extracted.
**Last decision:** `D-012` - preserve MDS-UPDRS Part III medication and DBS state.

**Added:** `NUPDRS3TRT` and `LEDDLOG` to `src/data/ppmi_contracts.py`, with synthetic tests. Updated `docs/ppmi-source-catalog.md` and the data component guide.

**Progression finding:** `NUPDRS3TRT` contains `NP3TOT`, `PDSTATE`, `ONOFFORDER`, `PDMEDYN`, `PDTRTMNT`, medication dose date/time and DBS fields. Its `PAG_NAME` values distinguish OFF-state, ON-state, treatment-determination and no-treatment forms. `LEDDLOG` contains medication, dose, start/stop date and levodopa-equivalent dose fields. These must be aligned before defining progression labels.

**Not verified:** actual table exports, visit-level state completeness, valid 12/24-month outcome coverage, medication exposure at assessment time, MRI/image availability, local tests, Ruff or CI completion. No passing CI result is claimed.

**Next:** approved PPMI access and actual Participant Status, MRI, MRI Acquisition, MRIQC, NUPDRS3TRT, LEDDLOG and LONI image metadata exports are needed to measure real coverage and validate row grains.

---

**Next:** Return to [`context.md`](../context.md) before starting a new task.
