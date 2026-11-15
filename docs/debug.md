## DBG-017 - Verify and merge T1w voxel QC (2026-11-15)
**CI evidence:** PR #17 initially failed documentation drift because the generated preprocessing component table incorrectly included the CLI script. It also failed the imaging tests because the singular-affine fixture attempted to construct a NIfTI image directly with a singular affine, which NiBabel rejects. The main verification job initially lacked the optional imaging dependencies.

**Repairs:** Removed the CLI script from the generated component table. The singular-affine test now constructs a valid NIfTI image, writes a singular sform explicitly and disables qform. The main CI verification environment installs both development and optional imaging dependencies so the full pytest suite can collect and run all tests.

**Tested:** CI run #43729401420 passed all jobs: Ruff, compileall, full pytest, docs/component drift, secret scan and `ci-pass`. PR #17 merged into `main` as `f085c49c9d562c84461156f8b3b74b6b7725d3ad`.

**Not tested:** No actual ds005892 T1w voxel data, no private manifest execution, no visual montage review, no BOLD motion QC, no brain extraction, registration, segmentation or preprocessing. Synthetic CI success does not establish image quality or Phase 1 completion.

**Next:** Run the T1w QC CLI against the local dataset and manually review the private montages before deciding scan inclusion.

---

## DBG-016 - Add first-pass T1w voxel QC and private montages (2026-11-15)
**Need:** Header-only BIDS inventory cannot detect intensity corruption, non-finite voxels or gross coverage problems. A local-only voxel QC step is required before preprocessing.

**Change:** Added `src/preprocessing/qc.py`, `scripts/qc_t1w.py`, `requirements-imaging.txt` and synthetic tests. The CLI accepts only a private manifest with explicit sequence verification, validates scan paths remain inside the BIDS root, pseudonymizes participant IDs with a local HMAC secret, and writes private per-scan metrics, an aggregate JSON report and native-orientation montages outside the source and repository.

**Metrics:** 3-D shape, spatial voxel sizes, orientation codes, affine determinant, non-finite count/fraction, zero/nonzero fractions, intensity percentiles, p99-p1 dynamic range and nonzero foreground bounds. Thresholds are caller-supplied. Nonzero foreground is explicitly not a brain mask. No automatic exclusions or source modifications occur.

**Tested:** Not yet. A dedicated CI imaging job installs the optional imaging dependencies and runs the synthetic tests; CI is pending.

**Not tested:** Actual ds005892 voxel data, montage review, BOLD motion/temporal QC, brain extraction, registration, segmentation or preprocessing.

**Next:** Review CI, then execute on the local T1w manifest and manually inspect all montages.

---

## DBG-013 - Review local NIfTI affine diagnostics (2026-11-15)
**Input:** Researcher-supplied aggregate counters from the corrected local ds005892 geometry inventory. No participant IDs or file paths were shared.

**Findings:** All 55 T1w and 55 BOLD files have qform_code=1 and sform_code=1; sform is selected for the inventory affine. T1w qform/sform max absolute differences were 0 for 53 scans, 0.000004 for one and 0.000008 for one. BOLD differences ranged from 0 to 0.001743; three exceeded the inventory's 0.001 flag threshold. Orientation summaries were T1w RAS 54/LPS 1 and BOLD LAS 55.

**Interpretation:** These qform/sform differences are numerically small and do not justify scan exclusion. The 0.001 threshold is a review flag, not a scientific exclusion criterion. RAS/LPS/LAS labels describe voxel-axis directions relative to RAS+ world axes; they do not alone indicate a bad scan. Keep original transforms and use a consistent selected-affine policy. Confirm anatomical orientation in voxel-level visual QC before any reorientation or preprocessing.

**Tested:** This was an interpretation of local aggregate metadata supplied by the researcher. No new code, image voxel data, or participant-level records were processed in this session.

**Not tested:** Full BIDS validation, anatomical image quality, BOLD motion/temporal quality, visual review, preprocessing, progression endpoint coverage, cohort freeze, participant-level splits or model training.

**Next:** Run the full BIDS validator locally, then implement separate T1w structural QC and BOLD motion/temporal QC paths.

---

## DBG-012 - Repair and merge NIfTI geometry audit CI (2026-11-15)
**Failure evidence:** PR #14 run #43724991716 had two failures. The synthetic aggregate-inventory test created its BOLD image with the helper's default `1.0, 1.0, 1.5` spatial spacing while asserting `3.125, 3.125, 3.5`. The component-doc generator reported a stale generated block in `docs/components/data.md` because the BIDS inventory module's first-line responsibility comment had changed.

**Repairs:** Updated the synthetic BOLD fixture to set the expected three spatial spacings and 2-second temporal spacing explicitly. Updated the generated data component row to match the current source header comment.

**Tested:** PR run #43725333584 passed Python lint, compilation, all pytest tests, component-doc generation, documentation checks and secret scan. PR #14 was merged by squash as `d18458345b653ce79a0ce6a84baf3798f4d540ba`. CI on the merge commit passed all jobs in run #43725395612.

**Not tested:** The corrected geometry inventory has not been run against the researcher's local ds005892 directory. No voxel-level image QC, BOLD motion/temporal QC, visual anatomical review, preprocessing or participant-level split manifest exists yet.

**Next:** Update local `main`, rerun the geometry inventory to a path outside the BIDS tree and repository, and review aggregate affine/orientation counts before starting the modality-specific QC pipelines.

---

## DBG-011 - Local DICOM header indexing and series manifest (2026-11-15)
**Need:** MRI modality and sequence coverage remain unknown. A first-stage index is needed to inspect actual DICOM acquisition headers without assuming T1 from labels or descriptions.

**Change:** Added `src/preprocessing/mri_manifest.py` to read DICOM headers from ZIP members with `stop_before_pixels=True`, aggregate by series, HMAC patient/study/series identifiers and report metadata consistency/QC checks. Added `scripts/index_mri_archive.py`, which requires a private HMAC key and rejects manifest output paths inside the Git worktree. Added synthetic tests and `docs/mri-metadata-intake.md`.

**Design safeguards:** The indexer does not infer sequence family, use LONI Weighting, choose a T1 series, extract pixels, or perform image preprocessing. HMAC pseudonyms are not anonymization; participant-level manifests remain restricted and must stay in an approved local environment.

**Tested:** Synthetic unit tests have been added but have not yet been executed in this session. Latest GitHub Actions run is pending at the time of this log update.

**Not tested:** No PPMI DICOM archive, LONI manifest, IDA metadata or participant-level PPMI table has been processed. No sequence mapping, conversion, image QC, FastSurfer, model training or RL training has occurred.

**Next:** Validate synthetic CI, then run only in the approved local environment and review the resulting private aggregate metadata before any sequence-selection code is written.

# Debug log - PANPM

## DBG-010 - Aggregate Phase 0 feasibility coverage pipeline (2026-11-15)
**Change:** Added release-configured JSON mappings, export-header validation, a CLI report builder and aggregate reporting functions for cohort coverage, MRI acquisition/image-manifest matching, medication-state-specific baseline/follow-up availability and report provenance.

**Privacy:** Participant join keys are HMACed with a supplied secret of at least 32 bytes. The functions return aggregate counts and configured field names, not identifiers. The report records release ID, download date, source SHA-256 values and mapping-config SHA-256.

**Synthetic tests:** Added config validation/normalization, cohort deduplication, MRI join matching, exact-state progression coverage, tie exclusion, duplicate-baseline exclusion and report-provenance cases.

**Not tested:** No approved PPMI data, LONI manifest or MRI files were processed. Example field mappings and all clinical/sequence rules remain unvalidated against a real release. Progression coverage requires an explicit `PAG_NAME` allowlist as well as state mapping; it excludes other forms and requires follow-up dates to be later than the selected baseline assessment. CI passed on 2026-11-15: [run #43710799588](https://github.com/yash936936/PANPM/actions/runs/43710799588), including 50 synthetic pytest cases, Ruff, compileall, docs and secret scan.

## DBG-009 - Aggregate source table grain and relationship audit (2026-11-15)
**Change:** Added `src/data/audit.py` with candidate-key completeness/uniqueness summaries and child-to-parent relationship coverage. Results contain field names and aggregate counts only. Composite keys are stored as ephemeral HMAC digests in an in-memory SQLite database; no key values are returned.

**Tests added:** Synthetic fixtures cover duplicate and missing composite keys, unmatched child rows, duplicate parent keys, mismatched key arity and identifier non-disclosure. CI must execute them before this work is marked tested.

**Not tested:** No PPMI export has been audited. No local Ruff or pytest run is claimed.

## DBG-008 - Add explicit medication-state progression target helpers (2026-11-15)
**Need:** The PPMI reference documents identify ON/OFF state and medication context for `NP3TOT`, but actual visit coverage and the correct state/window rule are unknown.

**Change:** Added `src/data/progression_targets.py` with `MotorAssessment`, `select_motor_assessment` and `motor_score_change`. Selection requires a caller-supplied target date, inclusive tolerance in days and exact normalized state. It chooses the closest eligible score, rejects tied closest records, and does not pool states. Score change requires same-state baseline/follow-up and chronological order.

**Tests added:** Synthetic tests cover state filtering, inclusive date boundary, missing scores, tied records, invalid tolerance/state, mixed-state rejection, chronology and follow-up-minus-baseline direction.

**Tested:** Not run locally. No local checkout is available in this session. No passing CI result is claimed for this branch.

**Not tested:** PPMI code mapping, clinical appropriateness of the state rule, actual target window, LEDD derivation, DBS eligibility, endpoint completeness, image processing, supervised models or RL.

**Next:** Validate source mapping and state-specific target availability using approved `NUPDRS3TRT` and `LEDDLOG` exports before freezing endpoint parameters.

---

# Debug log - PANPM

## DBG-007 - Add medication-aware progression source contracts (2026-11-15)
**Sources inspected:** Annotated Data Dictionary and Annotated Code List, dated May 23, 2025.

**Findings:** `NUPDRS3TRT` contains MDS-UPDRS Part III total score `NP3TOT`, ON/OFF state, order of OFF/ON examinations, medication-use/treatment flags, dose timing and DBS fields. The Code List identifies distinct `PAG_NAME` values for OFF-state, ON-state, treatment-determination and no-treatment forms. Individual motor item fields include 0–4 score codes and 101 for Unable to Rate. `LEDDLOG` contains medication and dose records with start/stop dates and levodopa-equivalent fields.

**Change:** Added `NUPDRS3TRT` and `LEDDLOG` source contracts and synthetic header/state-field tests. Updated the source catalog and data-component guide. No progression outcome rule was finalized because actual state-specific coverage and visit completeness are unknown.

**Tested:** Not run locally. GitHub Actions run 22 was queued at the last check; no passing CI result is claimed.

**Not tested:** actual NUPDRS3TRT/LEDDLOG exports, medication state at each assessment, 12/24-month endpoint completeness, preprocessing, models or RL.

**Next:** obtain approved participant-level exports and quantify valid ON/OFF state and medication exposure coverage before freezing progression targets.

---

## DBG-006 - Extract official PPMI reference documents (2026-11-15)
**Sources inspected:** PPMI Data User Guide (cover updated August 6, 2026), Annotated Data Dictionary (May 23, 2025), and Annotated Code List (May 23, 2025). Also inspected the uploaded screenshot of the PPMI Data Resources download page.

**Findings:** Identified source definitions for PATIENT_STATUS, MRI, MRI_ACQUISITION, MRIQC, GMVOLUME and DTIROI. Extracted MRI sequence flags for T1-weighted, T2-FLAIR, DTI, resting-state fMRI and neuromelanin MT; MRI acquisition quality and protocol codes; MRI assessment codes; and cohort codes 1, 2, 3, 4, 7 and 8. Recorded the discrepancy between the guide's five-cohort summary and the annotated code list's additional genetic registry codes. Also recorded the guide's conflicting revision dates on its cover and introductory page.

**Change:** Added `docs/ppmi-source-catalog.md`, `src/data/ppmi_contracts.py` and `tests/test_ppmi_contracts.py`. Contracts validate only selected documented participant/visit linkage fields and deliberately avoid enforcing ambiguous MRI_ACQUISITION uniqueness declarations.

**Tested:** Not run. The repository could not be cloned locally in the previous session, and no verified GitHub Actions run has been observed for this change. No claim is made that pytest or Ruff passes.

**Not tested:** Approved PPMI participant-level exports, LONI image metadata, actual DICOM/NIfTI files, table grain, MRI sequence prevalence, cohort overlap, progression endpoint completeness, preprocessing, supervised models or RL.

**Next:** Obtain approved PPMI data access and actual export files. Inventory them locally outside Git and reconcile the source contracts against real headers and row cardinality before building release-specific mappings.

---

## DBG-003 - Canonical schema contracts (2026-11-15)
**Symptom / need:** PPMI access and data files are not available, so the data pipeline cannot yet validate real exports or cohort joins.

**Change:** Added source-independent PANPM table contracts for participants, clinical visits, imaging scans, progression targets and split manifests. Added checks for minimum required columns, explicitly declared unique keys and participant foreign-key links. Added synthetic unit tests.

**Why this is safe:** The contracts are based on the internal schema in `docs/data-dictionary.md`; they do not claim that any PPMI release contains particular source columns. Clinical visit rows are not assigned an invented unique key because the documented grain permits multiple assessment-state records for a participant/event.

**Tested:** Not run. GitHub Actions status and local execution have not been verified in this session.

**Not tested:** Real PPMI headers, source mappings, joins, data coverage, MRI metadata, clinical endpoint completeness, preprocessing, models or RL.


## DBG-004 - Public PPMI tooling review and recursive CSV discovery (2026-11-15)
**Sources reviewed:** public repositories MJFF ResearchCommunity/PIE, MJFF ResearchCommunity/PIE-clean, NetNeuroLab/markello_ppmisnf, and the official PPMI Data Resources page. Findings and links are recorded in `docs/external-references.md`.

**Change:** Added `discover_csv_exports` and `inventory_csv_tree` to `src/data/inventory.py`. The helper recursively finds CSVs under a supplied export root, skips hidden directories, and returns relative path, release, checksum, file size, header and row count. It does not load or retain participant-level rows. Added synthetic tests for nested discovery and hidden-directory exclusion.

**Research caution:** PIE's public documentation reports possible LONI Weighting misclassification for some PPMI 2.0 3D T1 series. This is recorded as an upstream observation to verify against the official acquisition metadata and actual release, not as a PANPM sequence rule.

**Tested:** Not run. No local checkout or CI result has been verified.

**Not tested:** real PPMI exports, official dictionary extraction, source mapping, participant coverage, MRI sequence selection, image processing, model training or RL.

## DBG-005 - Schema validation privacy hardening (2026-11-15)
**Change:** Duplicate unique-key validation messages no longer echo the duplicate key value. The issue retains the row index needed for debugging without exposing participant or scan identifiers in logs.

**Test added:** A synthetic regression test asserts that a deliberately sensitive-looking scan ID is absent from the validation message.

**Tested:** Not run. GitHub workflow status and local pytest remain unverified.
---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
