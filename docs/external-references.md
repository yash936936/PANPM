# External implementation review: PPMI tooling

**Reviewed:** 2026-11-15  
**Purpose:** identify reusable engineering patterns. This is a review of public source code and documentation, not a PPMI data audit.

## Repositories reviewed

### MJFF Research Community: PIE

Repository: https://github.com/MJFF-ResearchCommunity/PIE  
License shown by repository: MIT. Check the exact upstream version and third-party dependency licenses before reusing code.

Relevant documented design:
- Separates tabular cleaning/model workflows from imaging processing.
- Describes a LONI DICOM archive index, series selection, DICOM header probing, conversion to NIfTI, and MRI-derived feature extraction.
- Describes joining imaging sessions to clinical events, with participant and event keys.
- Documents scanner metadata and visual QC as part of the imaging pipeline.
- Explicitly states that PIE does not contain PPMI participant data.

Useful source files:
- `pie/imaging/index.py`: ZIP member indexing, series grouping, T1 candidate ranking, header probing.
- `documentation/imaging.md`: imaging pipeline overview, tool requirements and documented acquisition caveats.

**Important caution:** the PIE documentation reports that LONI's Weighting label may misclassify some PPMI 2.0 3D T1 series, and recommends checking series descriptions and PPMI MRI acquisition metadata rather than relying on the Weighting label alone. Treat this as an upstream implementation observation to verify against the exact PPMI release and metadata we eventually receive. PANPM must not hard-code PIE's regular expressions or selection ranking as ground truth.

### MJFF Research Community: PIE-clean

Repository: https://github.com/MJFF-ResearchCommunity/PIE-clean  
License shown by repository: MIT.

Relevant documented design:
- Provides separate loaders for subject characteristics, medical history, motor assessments, non-motor assessments and biospecimen tables.
- Uses `PATNO` and `EVENT_ID` as merge keys in its PPMI-oriented loader.
- Includes mocked test files that mimic PPMI file structures and types, while explicitly stating they are fabricated and not real participant records.

PANPM may use these mocked files as inspiration for synthetic contract tests only after checking the fixture licence and provenance. Do not copy their rows into PANPM as research data. Do not assume all PPMI tables share the same grain or are safe to merge into one wide table.

### NetNeuroLab: markello_ppmisnf

Repository: https://github.com/netneurolab/markello_ppmisnf  
Relevant walkthrough: https://github.com/netneurolab/markello_ppmisnf/blob/master/walkthrough/01_accessing_data.md

The walkthrough describes the PPMI data-use agreement requirement, manual LONI image-collection download, and use of archived DICOMs for subsequent conversion. It is useful as a workflow reference, not as permission to bypass current PPMI access requirements.

### Additional public workflow references

- [sameerd/ppmi](https://github.com/sameerd/ppmi): older SQLite import/query workflow, data dictionary and code-list use, plus historical UPDRS and DTI utilities. Its README says the repository contains no PPMI data. Its SQL examples are historical and are not PANPM target definitions.
- [AgingLab/PPMI_Data_Wrangling](https://github.com/AgingLab/PPMI_Data_Wrangling): R scripts for raw-to-wide conversion, cleaned/processed clinical and imaging tables, biospecimen processing and final merges. The wrapper includes baseline/screening visit collapsing; PANPM must not adopt that without a separately justified, versioned rule because it can erase longitudinal timing.
- Detailed findings and PANPM decisions are recorded in [third-party-methods-review.md](third-party-methods-review.md). The review covers PIE, PIE-clean, sameerd/ppmi and AgingLab/PPMI_Data_Wrangling.

### Official PPMI data resources

https://www.ppmi-info.org/access-data-specimens/guidance-resources

The page lists the Data Dictionary, Code List, Data User Guide, SAA overview, Biomarkers Dashboard and Dictionary, Publication Policy, and Groups and Subgroups Guidance Document. These should be downloaded and versioned locally by the researcher when available. This repository currently has not received those official files.

## PANPM implementation decisions from this review

1. Added recursive CSV discovery and metadata-only inventory to `src/data/inventory.py`. It records relative paths, headers, row counts, sizes and checksums; it does not load or persist participant-level rows.
2. Keep source-to-target mappings explicit and release-specific.
3. Preserve table grain. Do not merge every modality on participant and event without checking cardinality and repeated assessment states.
4. Treat MRI sequence labels as candidate evidence. Use acquisition metadata, DICOM headers, series descriptions, image QC and visit linkage before selecting sequences.
5. Keep raw data, direct identifiers, image IDs and restricted participant-level records outside Git.
6. Reuse upstream code only after reviewing its exact source, licence, dependencies, tests and fit to PANPM's intended cohort and endpoints.

## Not established by this review

- No current PPMI data dictionary or code list has been downloaded into PANPM.
- No source column mapping has been verified against an official release.
- No PPMI participant records, scan counts, MRI modality counts or clinical endpoint coverage have been inspected.
- No claim is made that PIE's sequence-selection rules are validated for PANPM.
- No model performance or clinical finding is inferred from these repositories.
---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
