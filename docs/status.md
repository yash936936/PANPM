## 2026-11-15 - Add local-only DICOM header index and MRI series manifest
**Current phase:** Phase 0 - MRI metadata intake; no approved PPMI participant-level data or MRI archive has been processed.

**Added:** `src/preprocessing/mri_manifest.py` reads DICOM headers from a local ZIP without extracting pixel data, aggregates instances by series, HMACs patient/study/series identifiers, records scanner/acquisition metadata, and reports missing identifiers, duplicate SOP instance UIDs and intra-series metadata conflicts. `scripts/index_mri_archive.py` writes a private JSON manifest and rejects output paths inside the Git worktree. Added synthetic tests in `tests/test_mri_manifest.py` and instructions in `docs/mri-metadata-intake.md`.

**Sequence policy:** No sequence family is inferred from a filename, description or LONI Weighting field. `sequence_family` remains null and `selection_status` remains `needs_sequence_review`. The first-stage checks only report explicit DICOM Modality, MRAcquisitionType and ImageType values. This is not image QC or evidence that a series is suitable for modelling.

**Privacy:** Raw PatientID, SeriesInstanceUID, StudyInstanceUID, SOPInstanceUID and archive member names are not emitted. HMAC identifiers and all participant-level derived metadata remain restricted data, not anonymized data. The manifest and source archive must stay in the institution-approved environment and outside Git/ChatGPT.

**Not verified:** No PPMI DICOM archive was read; no LONI CSV/XML or PPMI MRI_ACQUISITION metadata was reconciled; no T1 selection, dcm2niix conversion, FastSurfer, image QC, supervised training or RL training has been run. Tests are synthetic only.

**Next:** Run the header index locally on an approved, representative MRI archive, inspect aggregate QC outcomes privately, then reconcile candidate series against the exact release's MRI acquisition metadata and LONI manifest before implementing sequence-family mapping or conversion.

---

# Status - PANPM

> Running project log. Newest entry goes at the top. Update this file at the end of every work session.

## 2026-11-15 - Add configured Phase 0 feasibility coverage pipeline
**Current phase:** Phase 0 - source-independent ingestion and feasibility tooling. No approved participant-level PPMI exports have been audited.

**Added:** `src/data/feasibility.py` supports release-specific JSON mapping validation, explicit record normalization, participant cohort counts, MRI acquisition-to-image-manifest matching, same-medication-state progression coverage and aggregate report assembly. Added `configs/ppmi_mapping.example.json`, `scripts/build_phase0_report.py` and synthetic tests in `tests/test_data_feasibility.py`. Documentation is in `docs/phase0-feasibility-pipeline.md`.

**Safety and research limits:** All participant join keys are ephemeral HMAC digests; outputs contain aggregate counts only. Source state mapping, LONI join keys, sequence flag interpretation, target states and tolerance must be explicitly reviewed. Duplicate baseline participants and tied nearest assessments are excluded as ambiguous. The example config is not validated against a real PPMI release.

**CI:** Passed on 2026-11-15 in [run #43710799588](https://github.com/yash936936/PANPM/actions/runs/43710799588). Ruff and Python compilation passed; pytest reported 50 passed; generated component docs, documentation checks, secret scan and `ci-pass` passed. These are synthetic/source-independent tests only.

**Not verified:** PPMI access/download, actual row grains, cohort or image coverage, valid progression endpoint counts, MRI sequence identity, local tests, model training or RL training.

**PR:** [#6](https://github.com/yash936936/PANPM/pull/6) is open as a draft and is not merged.

**Next:** Keep the pipeline in aggregate-only mode until approved exports arrive. Then fill the private mapping config using actual headers, validate LONI image join keys and `PAG_NAME`/`PDSTATE` mappings, and generate the first real feasibility report.

---

## 2026-11-15 - Add metadata-only table-grain and relationship audit
**Current phase:** Phase 0 - source-independent audit tooling; actual PPMI feasibility still awaits approved exports.
**Branch:** `research/phase0-table-grain-audit`.
**Previous PR:** [#4](https://github.com/yash936936/PANPM/pull/4) merged into `main`.

**Added:** `src/data/audit.py` reports candidate-key completeness, distinct-key counts, duplicate groups/rows, child-to-parent matches and unmatched rows. Composite key values are HMACed with a per-run random secret before temporary in-memory SQLite storage. Outputs contain no participant or image identifiers. Synthetic tests are in `tests/test_data_audit.py`.

**CI follow-up:** PR #4's docs and secret-scan jobs passed. Python setup and dependency installation passed, but Ruff failed on import modernization and import formatting in existing modules/tests. This branch applies those lint fixes. The first PR #5 run passed docs and secret scanning but Ruff still reported the prior import-order state in its merge checkout; the latest branch file has been reordered and a fresh run is required. No tests are claimed as passed yet.

**Not verified:** actual PPMI row grain, key cardinality, table relationships, participant counts, image coverage or clinical endpoint coverage. No participant-level data were used.

**Next:** run the audit against approved CSV exports using candidate keys justified by the source dictionary and observed row grain, then review ambiguous relationships before joins.

---

## 2026-11-15 - Extract repository implementation state and prepare PPMI intake
**Current phase:** Phase 0 - repository extraction and CI repair; participant-level feasibility audit still requires approved PPMI exports.
**Branch:** `research/phase0-repo-extraction-ci`.
**Previous PRs:** #1, #2 and #3 are merged into `main`.
**Repository extraction:** `docs/repo-extraction.md` records implemented source-independent utilities, documented PPMI source tables, normalized target schemas, unimplemented research components and the first-week intake sequence.

**CI findings from main merge commit:** Python setup failed because pip caching had no `requirements.txt` or `pyproject.toml` to hash; the docs job found a stale generated block in `docs/components/data.md`; the secret scanner found the self-test's fake key literal. This PR supplies the explicit cache dependency path, regenerates the data component inventory and constructs the synthetic key at runtime to keep the fixture from matching the scanner. These changes require CI verification.

**Not verified:** local Ruff/pytest, approved PPMI export contents, actual cohort/sequence/endpoint coverage, MRI image availability, row grain or model/RL feasibility. No model or PPO training has begun.

**Next:** obtain the approved PPMI export package, run metadata inventory outside Git, audit table grains and compute modality/endpoint overlap before freezing the MRI sequence and progression target.

---

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
