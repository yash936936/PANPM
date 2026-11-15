# OpenNeuro ds005892 development dataset

**Selected development source:** OpenNeuro `ds005892`, version `1.0.0`  
**DOI:** https://doi.org/10.18112/openneuro.ds005892.v1.0.0  
**Repository snapshot inspected:** https://github.com/OpenNeuroDatasets/ds005892/tree/main  
**License declared in `dataset_description.json`:** CC0 1.0 Universal  
**BIDS version:** 1.8.0

## Why this dataset

The public `participants.tsv` contains 55 participants:

| Group | Participants |
|---|---:|
| Control | 22 |
| Parkinson's disease with normal cognition (PD-NC) | 18 |
| Parkinson's disease with mild cognitive impairment (PD-MCI) | 15 |
| **Total** | **55** |

The public BIDS tree contains T1-weighted anatomical NIfTI files and resting-state BOLD fMRI files. The dataset description identifies a Siemens TrioTim 3T scanner for the resting-state EPI acquisition, with TR 2000 ms, TE 29 ms and 3.5 mm slice thickness/spacing. These are dataset-level README values; per-run JSON sidecars and NIfTI headers must be inspected before preprocessing.

The dataset description says the imaging was collected during Year 1 of a longitudinal study from participants who consented to optional neuroimaging. This release is therefore suitable for a small, public development cohort and diagnosis/cognitive-group experiments, but it does not establish that repeated clinical outcomes or 12/24-month motor labels are present.

## PANPM scope using this source

**Primary development task:** participant-level classification of PD (PD-NC + PD-MCI) versus healthy controls using T1w MRI. Preserve PD-NC and PD-MCI as separate source labels and run a secondary three-class analysis only if the small sample supports a carefully qualified exploratory result.

**Secondary modality task:** resting-state BOLD feature extraction and a matched-cohort comparison with T1w. Keep T1w and BOLD branches separate until subject/run coverage and preprocessing quality are verified.

**Not supported by this release without further evidence:**
- PPMI-specific cohort or acquisition feasibility.
- A validated 12/24-month MDS-UPDRS Part III progression target.
- Medication ON/OFF or LEDD-aware progression modelling.
- Clinical claims or a reliable estimate of generalization to a large PD population.

With 55 participants, this dataset is too small for a credible standalone deep-learning benchmark or PPO performance claim. Use it to validate ingestion, metadata parsing, QC, split logic, feature extraction and small-sample baselines. Report uncertainty and avoid treating repeated slices/volumes as independent participants.

## Data handling and evaluation rules

- Download the versioned OpenNeuro snapshot locally. Record the snapshot/version, download date and source checksums.
- Read `participants.tsv`, `dataset_description.json`, `participants.json`, all relevant BIDS JSON sidecars and NIfTI headers.
- Keep source participant IDs in a restricted local linkage layer. Never commit participant-level manifests or derived data.
- Split by participant before any slice, patch, ROI or time-series expansion. No participant may appear in more than one partition.
- Fit normalization, feature selection, harmonization and learned preprocessing on training participants only.
- Audit age/sex/group imbalance and report participant counts per split. Do not claim an independent external validation from random slices.
- Preserve the three original labels. Define binary PD/HC only as PD-NC + PD-MCI versus Control in a versioned cohort rule.
- Do not infer sequence or geometry from filenames alone; verify NIfTI headers and sidecars.

## Download and inspect locally

OpenNeuro dataset page: https://openneuro.org/datasets/ds005892/versions/1.0.0

The OpenNeuro user guide documents browser, S3, DataLad and openneuro-cli download routes: https://docs.openneuro.org/user_guide.html

Do not place downloaded images, participant-level TSVs, BIDS sidecars, private manifests or derived outputs in this public Git repository. Only source-independent code, schemas, synthetic fixtures and aggregate facts permitted by the dataset terms belong here.

## Decision

Use `ds005892` as PANPM's immediate public development dataset. Retain PPMI contracts as a separate future adapter, not as the active dataset. Add Neurocon and Taowu later as secondary external cohorts only after checking their CC BY-NC-SA terms and documenting that their small samples and possible overlap with published model training make them unsuitable as an unquestioned independent test set.

---

**Next:** Build a BIDS metadata inventory and validation adapter for this dataset, then generate only local aggregate feasibility outputs.
