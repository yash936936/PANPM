# Public PPMI repository review for PANPM

**Reviewed:** 2026-11-15  
**Purpose:** extract reusable public methods and workflow design, not PPMI participant records.

> PPMI data are governed by the PPMI Data Use Agreement. The agreement prohibits use of AI tools, especially public-facing interfaces, for PPMI data. PANPM must not download, process, or store participant-level PPMI records or MRI scans through this assistant. Run all approved PPMI ingestion and analysis locally in an institution-approved environment. This review is limited to public source code and documentation.

## Repositories inspected

| Repository | What it contributes | License / handling |
|---|---|---|
| [MJFF-ResearchCommunity/PIE](https://github.com/MJFF-ResearchCommunity/PIE) | Current Python research toolkit covering tabular classification, statistics, cohort rules, provenance, MRI/DWI/neuromelanin/DaTscan/fMRI workflows and a local brain viewer. | MIT. Treat as a method reference; do not import its full stack without a separate dependency and scientific review. |
| [MJFF-ResearchCommunity/PIE-clean](https://github.com/MJFF-ResearchCommunity/PIE-clean) | Companion loaders and cleaning routines for PPMI study-data folders, including subject characteristics, medical history, motor, non-motor, biospecimen and imaging. | MIT. PIE documents this as its data-loading dependency. |
| [sameerd/ppmi](https://github.com/sameerd/ppmi) | Older SQLite workflow: create a local database from approved PPMI CSV exports, inspect the data dictionary/code list, then query specific tables. Includes older UPDRS SQL and DTI shell/SQL utilities. | No repository license was declared in the inspected repository metadata. Do not copy code. Its README explicitly says it contains no PPMI data. |
| [AgingLab/PPMI_Data_Wrangling](https://github.com/AgingLab/PPMI_Data_Wrangling) | R workflow from raw exports to wide, cleaned, processed behavioral, imaging and biospecimen tables, followed by an all-measures merge. | No repository license was declared in the inspected repository metadata. Do not copy code. |

## Findings to carry into PANPM

### 1. Keep clinical and imaging ingestion separate until keys are verified

PIE-clean exposes separate modality loaders. PIE's imaging documentation treats imaging-derived phenotypes as a separate table and joins them to clinical visits using `PATNO` and `EVENT_ID`. It also warns that a scan with no matching clinical visit can become a separate row with no cohort label.

PANPM should preserve that separation:
- retain source tables at their native grain;
- audit key uniqueness before joining;
- use explicit, release-specific key mappings;
- keep scan date and clinical visit date separately;
- report unmatched and duplicate imaging keys rather than silently dropping or collapsing them;
- only create a visit-level modelling table after the audit passes.

### 2. Use participant-grouped validation

PIE's documented classifier groups train/test splits and cross-validation folds by `PATNO`. This is the right anti-leakage pattern for repeated visits. PANPM should apply it to every supervised experiment, with all visits and scans from one participant confined to one partition.

PANPM should be stricter for longitudinal prediction: split participants first, choose baseline scans and follow-up labels within each partition, and never expose future clinical outcomes to the RL observation or action policy.

### 3. Treat preprocessing order as a leakage boundary

PIE's documentation describes a feature-engineering stage that scales numeric columns before its later train/test split stage, then refits scaling during selection. PANPM should **not** reproduce that ordering. Fit imputation, scaling, harmonisation, feature selection and any learned representation only on the training participants inside each fold. Apply the fitted transforms to validation/test participants.

### 4. Preserve visit and medication context

The older SQLite repository shows how to query MDS-UPDRS Part III at baseline, but its example SQL is historical and must not be copied as PANPM's target definition. PANPM already has explicit safeguards for assessment form, ON/OFF state, medication context, tied assessments and follow-up chronology. Keep those safeguards and validate every item-level total against the current PPMI dictionary and code list before creating a target.

The AgingLab R wrapper merges screening and baseline visits for some imaging and biospecimen outputs. PANPM should not adopt that collapse by default: it can erase visit chronology and scan-to-visit timing. Preserve original `EVENT_ID`, acquisition date and visit date; create any baseline/SC harmonisation only as a separately versioned derived rule.

### 5. Imaging workflow references, not assumed acquisition

PIE documents workflows for:
- structural T1 MRI and FastSurfer volumetric IDPs;
- diffusion MRI, including free-water and tract FA/MD measures;
- neuromelanin-sensitive MRI;
- FLAIR lesion measures;
- resting-state fMRI and connectivity;
- DaTscan/SPECT and PET.

These are candidate workflow references, not evidence that a given PPMI release or participant has each modality. PANPM must first inspect its approved LONI collection metadata and DICOM headers. Do not assume T1, sequence parameters, template space, scanner compatibility or coverage. Record tool versions, atlas/template identity, image checksums, QC and transformation provenance.

### 6. Keep the RL task separate from the image preprocessing pipeline

The reviewed repositories provide conventional preprocessing, feature extraction, statistical analysis and viewers. They do not establish PANPM's proposed RL method. PANPM's RL agent remains a research component: sequential ROI selection on an already acquired MRI, with a fixed and documented action space, bounded observation state, explicit reward, held-out participant evaluation and comparison against non-RL baselines. Do not describe the RL policy as a validated clinical decision system.

## PANPM implementation decisions

1. Retain PANPM's own source contracts, mapping configuration, key/grain audit, HMAC linkage and aggregate feasibility report.
2. Add a local-only adapter layer for PPMI exports. Do not make PIE-clean a required dependency until its current source mappings, supported release, cleaning rules and tests have been reviewed against PANPM's PPMI guide, dictionary and code list.
3. Add a separate imaging adapter only after actual acquisition metadata are available in the approved environment. It should emit a manifest and derived features with explicit `PATNO`/visit/scan linkage and QC provenance.
4. Do not copy the older UPDRS SQL or the R scripts' visit collapsing rules. Re-derive targets from the current code list and PANPM's medication-state rules.
5. Use synthetic fixtures in public CI. Never commit PPMI participant records, LONI manifests, MRI files, participant-level derived tables, raw IDs, crosswalks or HMAC secrets.

## Source files reviewed

- PIE: `README.md`, `documentation/pipeline.md`, `documentation/data_loader.md`, `documentation/data_preprocessor.md`, `documentation/imaging.md`, `documentation/imaging_dwi.md`, `pie/imaging/archives.py`, `pie/imaging/atlases.py`.
- PIE-clean: repository README and file tree for modality loaders and tests.
- sameerd/ppmi: `README.md`, repository file tree including SQLite database creation, table readers, DTI scripts and UPDRS notebook/SQL utilities.
- AgingLab: `README.md`, `PPMI_Wrapper.R`, and repository file tree for raw-to-wide, wide-to-cleaned and imaging/biospecimen processing scripts.

## Reproducibility note

The public repositories are actively changing. The review records the repository names and inspected paths, but does not pin a third-party commit as a validated PANPM dependency. Before any code reuse, record the exact commit SHA, license text, copied-file provenance and local test evidence in a separate dependency review.

**Next:** update `context.md` with any third-party method selected for controlled local reproduction.
