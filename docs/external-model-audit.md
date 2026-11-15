# External model and workflow audit

**Audit date:** 2026-11-15  
**Scope:** Public GitHub repository metadata and source inspection. No external code was executed, no checkpoints were downloaded, and no participant-level data were accessed.

This audit separates model implementations, pretrained weights, preprocessing workflows and longitudinal methods. They are not interchangeable.

## Executive decision

- **KAN-MRI:** strongest MRI architecture/paper reference. No checkpoint files or repository license were found in the inspected Git tree. Several training-script dependencies are absent from that tree. Do not assume it is runnable or that its code can be reused.
- **DeepMRI-PD:** MIT-licensed architecture reference. No checkpoint files were found. Its inspected 3D cross-validation script reuses model instances across folds, which invalidates a clean independent-fold evaluation.
- **PIE:** MIT-licensed PPMI processing and imaging workflow toolkit, not a pretrained MRI classifier. Its README explicitly says PPMI data are not included and its example classification report uses synthetic data.
- **LivingPark utilities:** optional PPMI download and T1 NIfTI workflow reference, not a model repository.
- **Imaging-Validated Parkinson's Subtypes:** potentially relevant longitudinal subtype and generative modelling work. Its README describes clinical, DaTscan SBR and R2* MRI analysis. The claimed checkpoint filename and author-reported metrics have not been independently verified.

## Candidate audit

### 1. KAN-MRI

Repository: https://github.com/salilp42/KAN-MRI  
Paper: https://doi.org/10.1038/s43856-025-01009-9

**Claimed datasets and task:** PPMI, Neurocon and Tao Wu; MRI-based PD versus control classification.

**Architectures:** ConvKAN2D/3D, ResNet2D/3D, VGG, GCN and ViT.

**Input and preprocessing observations:**
- The dataset loader converts 2D slice arrays to channel-first tensors and adds a channel dimension for 3D volumes.
- The README describes ViT2D inputs resized to 224 × 224 and a hybrid slice-wise ViT3D.
- The loader imports `normalize_volume` and `resize_volume` from a preprocessing module that was not present in the inspected Git tree. The exact preprocessing implementation therefore remains unverified.

**Weights and license:** No `.pt`, `.pth`, `.ckpt`, `.onnx` or safetensors files were present in the inspected Git tree. No LICENSE file or declared license was present in that tree.

**Reproducibility concerns:** The inspected training script references `src/datasets/preprocessing.py` and `src/training/trainer.py`, which were absent from the inspected tree. Referenced configuration files were also not present in that tree. The repository should not be treated as runnable without resolving these gaps.

**PANPM decision:** use the paper and architecture descriptions as research references. Do not copy code until reuse rights are clarified. Reimplement a baseline only after independently specifying preprocessing, participant-level splits and evaluation.

### 2. DeepMRI-PD

Repository: https://github.com/salilp42/DeepMRI-PD

**Claimed datasets and task:** PPMI, Neurocon and Tao Wu; structural MRI PD versus control classification.

**Architectures:** CNN2D/3D, GCN2D/3D and ConvKAN2D/3D.

**Input and preprocessing observations:**
- The inspected 3D CNN accepts a single-channel 3D tensor.
- The preprocessing utility resizes volumes to 64 × 64 × 64 using interpolation order 1.
- The normalization utility performs min-max intensity scaling.
- The Neurocon loader searches subject `anat` directories for NIfTI files and derives labels from folder names containing `patient`.

**Weights and license:** No checkpoint files were present in the inspected Git tree. The repository contains an MIT license file.

**Reproducibility concerns:** In the inspected 3D independent experiment, model objects are created before the cross-validation loop. The same model instance is then trained across folds. This allows weights from earlier folds to carry into later folds. Some imports in inspected files do not match modules in the repository tree.

**PANPM decision:** architecture reference only. Do not rely on its reported results without repairing and independently reproducing the experiments.

### 3. Parkinson's Insight Engine (PIE)

Repository: https://github.com/MJFF-ResearchCommunity/PIE

**Purpose:** PPMI processing, imaging-derived phenotypes, statistics and tabular ML.

**Imaging workflows:** DICOM-to-NIfTI, T1/FastSurfer measures, diffusion free-water and tract measures, neuromelanin, FLAIR lesions, and resting-state fMRI processing.

**Weights and license:** Not a pretrained MRI classification model. MIT license is present. Third-party dependencies and atlas notices require separate review.

**Data and result caveat:** The README states that PPMI data are not included. It explicitly identifies the example classification report as synthetic data, not PPMI results.

**PANPM decision:** workflow reference only. Run any PPMI workflow only in the approved local environment and validate all outputs.

### 4. LivingPark MRI utilities

Repository: https://github.com/LivingPark-MRI/livingpark-utils

**Purpose:** PPMI study-file and T1 NIfTI retrieval utilities. Its README documents cohort inputs containing `PATNO`, `EVENT_ID` and `Description`.

**Weights:** Not a model repository.

**License:** A LICENSE file is present in the inspected tree; confirm its exact terms before reuse.

**PANPM decision:** optional workflow reference. PPMI download functionality requires authorized PPMI access.

### 5. Imaging-Validated Parkinson's Subtypes

Repository: https://github.com/Moado/Imaging-Validated-Parkinson-s

**Purpose described by README:** longitudinal clinical subtype modelling, imaging validation and conditional normalizing-flow generation using PPMI. The README describes clinical features, DaTscan SBR and R2* MRI relaxometry at multiple visits.

**Methods described:** z-score SuStaIn approximation with a 96-configuration sensitivity grid, followed by conditional Real NVP generation.

**Weights and artifacts:** the README names `best_flow_model.pt` and versioned result artefacts. The inspected repository tree did not expose checkpoint files for verification. The README declares MIT, but the actual LICENSE file and any artifact-specific terms must be checked.

**Evidence caveat:** the README describes the manuscript as under review and reports author-side validation metrics. Those results have not been independently reproduced. The README explicitly says raw and processed PPMI files are not redistributed.

**PANPM decision:** investigate as a possible longitudinal subtype-method reference, not as a ready-made structural MRI PD classifier. Contact authors and verify Zenodo artifacts before considering any weights.

## Reuse gates

Before importing any external model or code into PANPM, record:

1. Repository URL, immutable commit SHA and paper DOI.
2. Repository license and any third-party code licenses.
3. Model checkpoint URL, checksum, architecture and checkpoint-specific license.
4. Training dataset, modality, cohort definition and subject count as documented by the authors.
5. Input tensor shape, orientation, voxel spacing, intensity scaling and preprocessing order.
6. Train/validation/test split unit and whether subjects overlap across visits or cohorts.
7. Reported metrics and exact evaluation protocol.
8. Whether the code can run from a clean environment using documented commands.
9. Whether results can be independently reproduced without restricted data leaving its approved environment.

## PANPM research safeguards

- A paper's reported performance is not a PANPM result.
- A pretrained ImageNet or video backbone is not a PD-trained MRI checkpoint.
- Repository license, model-weight license and dataset license are separate checks.
- PPMI participant-level data and derived participant-level files must remain within the PPMI-approved environment.
- All visits from one participant must remain in one data partition.
- Cross-study metrics are not directly comparable unless modality, cohort, split unit, preprocessing and evaluation protocol match.
- Synthetic demonstrations must be labelled synthetic.
- No clinical claims should be made from small-sample exploratory experiments.

## Next verification tasks

1. Resolve KAN-MRI license and missing source dependencies with its authors or maintainers.
2. Reproduce a minimal DeepMRI-PD model with a fresh model initialization inside each fold, then audit participant grouping and leakage.
3. Inspect PIE's modality-specific preprocessing documentation against PANPM's source contracts before borrowing any workflow.
4. Verify the subtype repository's actual LICENSE, immutable commit, Zenodo record and checkpoint availability.
5. Add a local checkpoint registry to PANPM only after provenance, checksum and license checks pass.

## Audit limitations

This is a source-level audit, not a runtime reproduction. GitHub tree inspection cannot prove that no release attachment, external storage link or private author artifact exists. Checkpoint absence means no checkpoint was found in the inspected Git tree, not that no weights exist anywhere.
