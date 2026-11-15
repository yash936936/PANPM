## 2026-11-15 - Run local T1w QC and add first-pass BOLD temporal QC
**Current phase:** Phase 1. T1w automated voxel QC has run locally; visual review and all preprocessing/cohort gates remain open.

**Local T1w evidence supplied by the researcher:** The CLI inspected 55 scans, reported zero configured review flags, recorded orientations RAS 54/LPS 1, made zero automatic exclusions and did not modify source images. The aggregate report emitted no participant-level identifiers. This is evidence of the configured automated checks only, not expert anatomical acceptance. All 55 private montages still require manual review.

**Implemented on branch** `phase1/bold-temporal-qc`:
- Added `src/preprocessing/bold_qc.py` for 4-D BOLD geometry, NIfTI temporal-unit-aware header TR versus sidecar `RepetitionTime`, finite/zero fractions, temporal-SNR summaries, whole-volume RMS temporal differences and global-mean signal variation.
- Added private montage generation showing temporal mean, a temporal-SNR proxy and the global mean signal trace.
- Added optional Power framewise displacement from a supplied TSV with named translation-in-mm and rotation-in-radians columns. The module does not estimate or correct motion.
- Added `scripts/qc_bold.py`, requiring an explicitly sequence-verified private manifest and matching BIDS JSON sidecars. Reports are pseudonymous/private and source images are read-only.
- Added synthetic tests in `tests/test_preprocessing_bold_qc.py`.

**Scientific limits:** The whole-volume RMS temporal-difference metric is not standardized, brain-masked DVARS. Nonzero foreground is not a brain mask. No motion metric is produced unless motion parameters are supplied. No thresholds are set from this small cohort; optional thresholds are caller-supplied and only create review flags. No automatic exclusions are made.

**Not verified:** BOLD branch CI is pending; the code has not run on local ds005892 BOLD scans. T1w montage review is not yet reported. BOLD visual review, motion-estimation workflow, brain extraction, registration, segmentation, preprocessing derivatives, cohort freeze and participant-level split remain outstanding. PR #16 remains draft/held under D-014. No model training is authorized.

**Next:** Verify the BOLD branch CI, then create a private BOLD manifest after checking the 55 matching sidecars and sequence metadata. Run BOLD QC locally and review all montages. Keep motion-estimation outputs separate and document their software/configuration before supplying them.

---

## 2026-11-15 - Merge and verify first-pass T1w voxel QC
**Current phase:** Phase 1 T1w QC implementation is merged and CI-tested; local image execution and visual review remain pending.

**PR #17:** Merged into `main` as `f085c49c9d562c84461156f8b3b74b6b7725d3ad`. CI run #43729401420 passed all jobs: Ruff, Python compilation, the full pytest suite, documentation/component checks and secret scan.

**Implemented:** `src/preprocessing/qc.py` calculates first-pass 3-D T1w voxel and geometry metrics; `scripts/qc_t1w.py` reads an explicitly sequence-verified private manifest and writes pseudonymous private per-scan reports, aggregate JSON and native-orientation montages. Optional imaging dependencies are in `requirements-imaging.txt`. Source images are never modified; no automatic exclusions are made. Nonzero foreground bounds are not a brain mask.

**CI repairs:** The first CI attempt found a stale generated component block and a singular-affine synthetic fixture that NiBabel would not serialize through the image constructor. The generated block was corrected, the fixture was changed to write a singular sform on a valid base image, and imaging dependencies were added to the main verification environment. Final CI passed.

**Not verified:** No local ds005892 image has been processed by this code. No montage has been reviewed. No T1w scan has been included/excluded based on voxel QC. BOLD motion/temporal QC, brain extraction, registration, segmentation, preprocessing derivatives, cohort freeze and participant-level split generation remain outstanding. PR #16 remains draft/held under D-014. Phase 1 remains open and model training is not authorized.

**Next:** Run the merged T1w QC CLI locally with a private, manually verified manifest and protocol-approved thresholds, then inspect all 55 montages.

---

## 2026-11-15 - Implement first-pass T1w voxel QC
**Current phase:** Phase 1 T1w QC implementation; local image execution and visual review remain pending.

**Implemented on branch** `phase1/t1w-voxel-qc`:
- `src/preprocessing/qc.py` loads 3-D T1w NIfTI data and reports dimensions, voxel sizes, orientation, affine determinant, finite/non-finite voxel counts, zero/nonzero fractions, intensity percentiles, dynamic range and nonzero foreground bounds.
- Caller-supplied thresholds generate review flags. No learned or cohort-derived thresholds are used.
- `render_t1w_montage` saves native-orientation axial/coronal/sagittal center slices and an intensity histogram.
- `scripts/qc_t1w.py` requires a private manifest with `participant_id`, `scan_path` and explicit `sequence_verified=true`; it writes pseudonymous private per-scan output, an aggregate report and private montages outside the repository and BIDS source.
- `requirements-imaging.txt` declares optional NumPy, NiBabel and Matplotlib dependencies. CI now has a separate imaging QC test job.
- Synthetic tests cover image metrics, non-finite voxels, dimensionality rejection, threshold validation, montage generation and identifier non-disclosure.

**Scientific boundary:** Nonzero foreground bounds are not a brain mask and are not used to estimate brain volume. Orientation is recorded, not treated as an automatic failure. No scan is automatically excluded. Source images are read-only.

**Not tested:** CI is pending. The code has not been run against the local ds005892 scans. No visual QC has been reviewed. No BOLD motion/temporal QC, brain extraction, registration, segmentation, preprocessing derivatives, cohort freeze or participant split has been produced. Phase 1 remains open.

**Next:** Verify CI, then run the T1w QC CLI locally with a privately curated sequence-verified manifest and protocol-approved thresholds. Review every montage before defining exclusions.

---

## 2026-11-15 - Review local NIfTI affine diagnostics
**Current phase:** Phase 0 metadata/geometry review; Phase 1 voxel-level QC remains open.

**Local aggregate evidence supplied by the researcher:** All 55 T1w and 55 BOLD images have qform_code=1 and sform_code=1, and the inventory selects sform. T1w qform/sform max absolute differences: 53 exact matches, one 0.000008 and one 0.000004. BOLD differences range from 0 to 0.001743; three exceed the inventory's 0.001 review threshold. Orientation counts: T1w RAS 54 and LPS 1; BOLD LAS 55.

**Interpretation:** The qform/sform differences are very small and do not support excluding any scan on this criterion. RAS/LPS/LAS are voxel-axis direction summaries in RAS+ world coordinates, not standalone quality failures. Keep the sform selection policy consistent, retain the original qform/sform metadata, and perform anatomical orientation checks during voxel-level QC. No scan was reoriented or modified by this metadata-only review.

**Not verified:** Full BIDS validation, voxel-level anatomical/functional QC, motion estimates, visual review, preprocessing, progression-label coverage, cohort freeze or participant-level splits. The local diagnostic is aggregate-only and no participant identifiers or file paths were supplied.

**Next:** Run a full BIDS validator on the local snapshot, then implement independent T1w structural QC and BOLD motion/temporal QC. Do not start model training.

---

## 2026-11-15 - Merge NIfTI geometry audit and repair PR #14 CI
**Current phase:** Phase 0 metadata gate merged; local geometry rerun is still required before Phase 0 closure. Phase 1 image QC and preprocessing remain open.

**PR #14:** [Merged](https://github.com/yash936936/PANPM/pull/14) into `main` after marking it ready for review. CI run #43725333584 passed all jobs. The squash merge commit is `d18458345b653ce79a0ce6a84baf3798f4d540ba`; its CI run #43725395612 also passed all jobs.

**CI repairs:** Corrected the synthetic BOLD fixture to write spatial spacing `(3.125, 3.125, 3.5)` and temporal spacing `2.0`; regenerated the `docs/components/data.md` generated block to match the updated BIDS inventory module description. Ruff, compilation, all pytest tests, component-doc generation, documentation checks and secret scan passed on the PR head.

**Phase 0 boundary:** The new NIfTI affine/orientation fields have not yet been run against the local ds005892 snapshot. The earlier 55-participant aggregate inventory does not contain these fields. Keep the corrected report local and review only permitted aggregate counts. Full BIDS validation, image QC and progression-label feasibility remain separate gates.

**Phase 1 boundary:** No voxel-level T1w QC, BOLD motion/temporal QC, visual review, preprocessing or participant-level split manifest has been implemented or validated. Keep the two modality QC paths separate.

**Next:** Update local `main`, rerun `scripts/inventory_bids.py` to `D:\\PANPM-data\\ds005892-inventory-geometry.json`, and review the aggregate affine/orientation fields. Then implement T1w QC as its own pipeline and BOLD motion/temporal QC separately.

---

## 2026-11-15 - Add NIfTI affine and spatial-temporal metadata audit
**Current phase:** Phase 1 metadata validation; Phase 0 OpenNeuro aggregate inventory executed locally.

**Local evidence supplied by the researcher:** `ds005892-inventory.json` was created successfully (2,461 bytes). It reports 55 participants (22 Control, 18 PD-NC, 15 PD-MCI), 55 T1w and 55 BOLD files, complete participant coverage for both modalities, zero missing/empty sidecars, zero invalid NIfTI headers and zero unknown participant files. T1w dimensions are 256 x 256 x 191 for one scan and 256 x 256 x 192 for 54 scans, all at 1 mm isotropic. BOLD dimensions are 64 x 64 x 32 x 200 for all scans; spatial spacing is 3.125 x 3.125 x 3.5 mm and sidecar TR is 2 seconds.

**Finding:** the previous report grouped the fourth BOLD NIfTI `pixdim` value (2 seconds) under `voxel_spacing_mm_counts`. This was a field-labeling error. It did not change the source images. The new implementation reports spatial spacing, header temporal spacing and sidecar `RepetitionTime` separately.

**Implemented on branch `phase1/nifti-affine-validation`:** NIfTI-1 sform/qform parsing, affine determinant/finite checks, closest cardinal orientation codes, qform/sform disagreement counts, separate spatial and temporal spacing summaries, synthetic tests and output-path guards that keep reports outside both the repository and source BIDS tree.

**Not yet verified:** CI for this branch, rerun against the local dataset, visual anatomical orientation, image-level T1w QC, BOLD motion QC, participant-level split manifest, preprocessing, supervised models or RL. The existing aggregate report does not contain affine results, so no real-scan affine findings are claimed yet.

**Next:** review the PR and CI, pull the branch after merge, rerun the aggregate inventory locally and inspect only permitted aggregate geometry results. Then implement T1w and BOLD image QC as separate workflows.

---

## 2026-11-15 - Repair BIDS inventory CI findings
**Current phase:** Phase 0 - source-independent BIDS inventory implementation; local dataset execution pending.

**CI findings from PR #13:** Python verification found import ordering and two exception-type lint findings in `src/data/bids_inventory.py`. The docs/component job found the generated `docs/components/data.md` block was stale. The secret scan and gates-not-run job passed.

**Repairs:** Reordered imports, changed invalid JSON object-type errors to `TypeError`, renamed the new test to `test_data_bids_inventory.py` so the component generator discovers it, and updated the generated data component inventory and hand-written capability notes.

**Not verified:** CI after these repairs, local dataset download, BIDS inventory execution, full BIDS validation, affine orientation, image QC or progression-label coverage.

**Next:** Verify all PR #13 checks. Then run the inventory on the local versioned ds005892 snapshot and review aggregate outputs before declaring the dataset-specific Phase 0 complete.

---

## 2026-11-15 - Add metadata-only BIDS inventory for OpenNeuro
**Current phase:** Phase 0 - BIDS inventory implementation added; real local execution pending.

**Added:** `src/data/bids_inventory.py` reads `dataset_description.json`, `participants.tsv`, BIDS JSON sidecars and NIfTI-1 headers without loading voxel arrays. It reports aggregate group counts, T1w/BOLD file and participant coverage, unknown/missing subject counts, NIfTI shape/spacing distributions, selected sidecar-field presence and SHA-256 checksums for the dataset description and participant table. `scripts/inventory_bids.py` provides the local CLI and rejects output paths inside the PANPM worktree. Synthetic tests cover NIfTI geometry, aggregate coverage, duplicate participant IDs and invalid headers.

**Scope limits:** This is not a full BIDS validator. It does not parse NIfTI-2, validate affine orientation, inspect all BIDS entities, run image QC, load voxels, create participant-level splits or establish progression endpoints. No OpenNeuro image files have been downloaded or processed in this work session.

**Documentation:** `docs/bids-metadata-inventory.md` describes the CLI and acceptance checks. `docs/openneuro-ds005892.md` records the run command. Phase 0 status updated.

**CI:** Pending for the latest branch head. The previous PR #12 CI failed only in the docs check because the new dataset document lacked the required `Next: ... context.md` navigation footer. The footer was corrected. Python verification, secret scan and gates-not-run jobs had passed on that earlier PR run.

**Next:** Wait for the updated PR #12 checks. After merge, download OpenNeuro ds005892 v1.0.0 locally and run the metadata-only inventory; review aggregate output for modality coverage, geometry and metadata completeness before calling Phase 0 complete.

---

## 2026-11-15 - Select public OpenNeuro development dataset
**Current phase:** Phase 0 - public development dataset selected; BIDS inventory and local feasibility execution pending.

**Decision:** Use OpenNeuro `ds005892`, version `1.0.0`, DOI `10.18112/openneuro.ds005892.v1.0.0`, declared CC0 1.0, as the immediate development dataset. Keep PPMI contracts and its approved-data pathway as a separate future adapter/validation target.

**Public metadata audit:** The versioned `participants.tsv` contains 55 rows: 22 Control, 18 PD-NC and 15 PD-MCI. The BIDS repository contains T1w anatomical and resting-state BOLD files; the dataset README describes Siemens TrioTim 3T EPI with TR 2000 ms, TE 29 ms and 3.5 mm slice thickness/spacing. These acquisition values must be verified from all per-run JSON sidecars and NIfTI headers before preprocessing. The dataset description says imaging was collected during Year 1 from participants who opted into neuroimaging.

**Task scope:** Primary development endpoint is participant-level PD (PD-NC + PD-MCI) versus Control classification using T1w. Preserve the three source groups for exploratory secondary analysis. Resting-state BOLD is a separate secondary branch. No 12/24-month MDS-UPDRS progression endpoint, medication-state alignment or LEDD coverage is established by the inspected release.

**Added:** `docs/openneuro-ds005892.md` records dataset provenance, limits, tasks and handling rules. `configs/openneuro_ds005892.example.json` records the versioned source contract and cohort mapping. Updated `docs/phases.md` to make OpenNeuro the active development source without deleting the PPMI adapter work.

**Not done:** No image data were downloaded or inspected. No BIDS validator, NIfTI header inventory, file/participant matching, QC, preprocessing, model training or RL training has run. The 55-person sample is for pipeline validation and exploratory baselines, not a strong standalone deep-learning or PPO benchmark.

**Next:** Implement a BIDS metadata-only inventory and aggregate feasibility report, then run it locally on the downloaded OpenNeuro snapshot. Keep all participant-level files outside Git and ChatGPT.

---

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
