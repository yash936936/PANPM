# Debug log - PANPM

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

