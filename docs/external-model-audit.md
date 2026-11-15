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

## Pretrained checkpoint ecosystem review

**Review date:** 2026-11-15  
**Scope:** Public model cards, papers, repository metadata and documented checkpoint links. No external weights were downloaded or executed.

### Candidate ranking

| Candidate | Verified artifact evidence | Modality / task fit | License and access | PANPM decision |
|---|---|---|---|---|
| BrainIAC | Hugging Face model card lists `backbone.safetensors`; upstream GitHub README states pretrained and downstream checkpoints are hosted by the BrainIAC platform/repository | 3D structural brain MRI; 96×96×96 single-channel input; 768-dimensional feature output. Strong encoder candidate, but not PD-specific | BrainIAC Research-Only License: non-commercial academic research and education only. Clinical workflow use and commercial use are expressly excluded | Highest-priority encoder to evaluate after checking input preprocessing and research-use compatibility |
| Triad | Upstream README provides four Google Drive checkpoint links: PlainConvUNet-MAE, PlainConvUNet-SimMIM, SwinB-MAE and SwinB-SimMIM | 3D MRI foundation model for segmentation, classification and registration; potentially useful for frozen-feature and fine-tuning comparisons | README displays an MIT badge, but the inspected upstream repository did not expose a LICENSE file. Weight-specific terms remain unverified | Strong candidate technically; do not download for integration or redistribute until authors confirm the effective license |
| BrainSegFounder | Hugging Face model card lists UKB, BraTS and ATLAS pretrained/fine-tuned checkpoint files | 3D brain MRI, mainly segmentation pretraining and fine-tuning. Possible encoder initialization | Hugging Face license tag is `uk-biobank-mta`; the data-use restrictions need review before any derivative fine-tuning or redistribution | Hold pending written confirmation that the applicable MTA permits PANPM's intended research use |
| NeuroVFM | Hugging Face diagnosis model card is public but gated; separate backbone is linked from the model card | Broad neuroimaging MRI feature backbone and a separate 74-diagnosis MRI model trained on 218,882 studies. Not established as a PD-specific classifier | Weights CC-BY-NC-SA 4.0; access requires accepting contact-information sharing conditions | Secondary feature-extractor candidate, subject to access and license review; do not treat the diagnosis head as a PD model |
| Brain2Vec | Hugging Face model card describes a 3D structural T1 brain-MRI checkpoint pretrained on 74,425 iSTAGING scans | Potential structural T1 encoder | CC-BY-NC-ND 4.0 tag. No-derivatives restriction makes fine-tuning/adaptation unsuitable unless the rights holder clarifies otherwise | Exclude from fine-tuning shortlist |
| RAVEN | Zenodo record lists a 2.1 GB `checkpoints.zip` model artifact | Structural MRI upsampling/super-resolution, not a PD diagnosis encoder | Zenodo record does not clearly expose a license in the inspected metadata | Not a classifier candidate; possible preprocessing research only after license and task-specific value are established |
| Vbai-DPA 2.4 | Hugging Face model card describes a Parkinson's/Alzheimer's/dementia MRI model | The model card claims disease classification, but does not establish cohort provenance, external validation, or a reproducible independent PD evaluation | License/provenance and access terms were not adequately verified in this review | Do not use as a scientific baseline until authors provide full methods, dataset provenance, weights terms and independent validation |

### Key sources

- BrainIAC model card: https://huggingface.co/eugenehp/brainiac
- BrainIAC paper: https://doi.org/10.1038/s41593-026-02202-6
- BrainIAC upstream code and license: https://github.com/AIM-KannLab/BrainIAC
- Triad upstream code and checkpoint links: https://github.com/wangshansong1/Triad
- BrainSegFounder model card: https://huggingface.co/smilelab/BrainSegFounder
- NeuroVFM MRI diagnosis model card: https://huggingface.co/mlinslab/neurovfm-dx-mri
- Brain2Vec model card: https://huggingface.co/cbica/Brain2Vec
- RAVEN Zenodo record: https://zenodo.org/records/21999063
- Vbai-DPA model card: https://huggingface.co/Neurazum/Vbai-DPA-2.4

### Interpretation for PANPM

1. No reviewed artifact is a verified, PPMI-trained Parkinson's MRI checkpoint with independently reproducible performance.
2. BrainIAC is the most defensible first encoder candidate because its architecture, input shape, feature output and research-only license are documented. It is not PD-specific, and its license excludes clinical workflows.
3. Triad may be a useful second encoder comparison, but its effective checkpoint license must be resolved first.
4. The PPMI MRI modality and acquisition distribution remain unknown. Do not build a BrainIAC/Triad adapter or preprocessing path until the local metadata audit establishes the actual sequence family, geometry, orientation, spacing and quality.
5. Evaluate pretrained encoders against a randomly initialized model and a conventional 3D CNN using participant-grouped splits. Report frozen linear-probe performance first, then fine-tuning. Include site/scanner and acquisition-protocol sensitivity analyses.
6. Keep all PPMI participant-level data and derived features inside the approved PPMI environment. Do not upload them to public model services or public-facing AI tools.

### Next verification tasks

1. Ask BrainIAC maintainers to confirm whether the research-only license permits the intended non-commercial academic adaptation and checkpoint use in PANPM.
2. Ask Triad maintainers to confirm the license applying to the four externally hosted checkpoints and provide immutable checkpoint hashes.
3. Review the UK Biobank MTA attached to BrainSegFounder before considering those weights.
4. Inspect BrainIAC and Triad preprocessing implementations only after the MRI modality audit has selected a compatible sequence.
5. Add a checkpoint registry only for candidates that pass provenance, license, hash, architecture and input-contract checks.

## Audit limitation update

The review found documented external checkpoint links, but did not download, hash, inspect tensor contents or execute any weights. A model card or README is evidence of a claimed release, not proof of scientific suitability for PANPM.


Next: update `context.md` with the selected checkpoint candidate and its unresolved license gates.
