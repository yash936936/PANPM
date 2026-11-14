# Debug log - PANPM

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
