# Architecture - PANPM

## System overview

PANPM is a research pipeline with a data layer, MRI preprocessing layer, feature and prediction models, a genetic-reference layer, an RL environment and evaluation/reporting tools. The system begins with approved PPMI exports. It creates a participant-level cohort manifest, aligns baseline imaging with clinical assessments, preprocesses eligible MRI sequences, extracts a global representation and candidate anatomical ROI features, then trains supervised baselines for diagnosis and longitudinal motor progression.

The RL contribution is an offline active-inspection simulator. At each step, the policy sees the global MRI representation and the information collected so far. It selects an available, uninspected ROI or STOP. The environment reveals that ROI's precomputed or lazily computed feature representation, updates the prediction, and calculates a reward during training from predictive improvement minus computational inspection cost. The policy is evaluated on held-out participants where targets are not exposed to the agent.

The GWAS/Allen Atlas branch produces population-level regional biological priors. It is kept distinct from participant-specific genotype data. These priors may influence a controlled fusion or interpretation experiment, but they do not become a patient's genetic profile.

**Implementation status:** this document specifies the intended architecture. Only the documentation, scripts and directory scaffold are being delivered now. Research source files, PPMI data and model checkpoints are not present.

## Components

### 1. Data manager (`src/data/`)
- **Responsibility:** import approved exports, normalize participant/visit/scan tables, verify joins, record source releases and generate cohort and modality inventories.
- **Depends on:** PPMI exports, data dictionary, PyArrow/Pandas and project configuration.
- **Key files planned:** `load_ppmi.py`, `schema.py`, `cohort.py`, `inventory.py`, `manifest.py`.
- **Must not:** scrape restricted sources, store credentials, infer sequence identity from one ambiguous label, or put identifying source IDs in logs.

### 2. MRI preprocessing (`src/preprocessing/`)
- **Responsibility:** convert and validate MRI series, run modality-specific preprocessing, register images, create masks and produce QC reports.
- **Depends on:** data manager, dcm2niix, NiBabel, SimpleITK, ANTs, FastSurfer and optional modality-specific tools.
- **Key files planned:** `dicom.py`, `sequence_classifier.py`, `qc.py`, `t1_pipeline.py`, `registration.py`, `segmentation.py`, optional `dti_pipeline.py` and `neuromelanin_pipeline.py` only when the inventory supports them.
- **Must not:** alter raw data, silently accept low-quality scans or treat conventional T1 as a neuromelanin measurement.

### 3. Feature extraction and models (`src/models/`)
- **Responsibility:** build reproducible global and ROI feature representations, train diagnostic and progression predictors, and expose prediction/loss functions to the RL simulator.
- **Depends on:** processed MRI, feature tables, split manifests, PyTorch/MONAI and Scikit-learn.
- **Key files planned:** `cnn3d.py`, `roi_encoder.py`, `fusion.py`, `diagnosis.py`, `progression.py`, `prediction_service.py`.
- **Must not:** train on validation/test participants or mix future outcomes into baseline features.

### 4. Genetics and spatial reference (`src/genetics/`)
- **Responsibility:** prioritize Parkinson's-associated genes using variant-to-gene evidence, process Allen Atlas regional expression and calculate statistically tested regional priors.
- **Depends on:** GWAS/functional evidence, participant genetics if authorized, Allen Atlas expression, atlas mapping and spatial null procedures.
- **Key files planned:** `gwas.py`, `gene_prioritization.py`, `allen_atlas.py`, `regional_scores.py`, `null_models.py`.
- **Must not:** equate nearest genes with causal genes, describe healthy Atlas expression as disease-specific, or conflate reference expression with participant genotype.

### 5. RL environment and policy (`src/rl/`)
- **Responsibility:** run finite-horizon ROI-inspection episodes, construct states, mask invalid actions, calculate training rewards and train/evaluate PPO policies.
- **Depends on:** frozen or cross-fitted prediction models, ROI embeddings, anatomical action map, training labels and cost configuration.
- **Key files planned:** `environment.py`, `state.py`, `action_space.py`, `reward.py`, `policy.py`, `train_agent.py`, `rollout.py`.
- **Must not:** expose labels or future measurements to the observation, calculate rewards from test labels, or claim physical scan-time reduction.

### 6. Evaluation (`src/evaluation/`)
- **Responsibility:** construct participant-level splits, calculate metrics and confidence intervals, run site-held-out tests, ablations, calibration and policy comparisons.
- **Depends on:** manifests, labels, predictions, model checkpoints and statistical utilities.
- **Key files planned:** `splits.py`, `classification.py`, `progression.py`, `rl_evaluation.py`, `calibration.py`, `site_validation.py`, `ablation.py`.

### 7. Visualization and reporting (`src/visualization/`)
- **Responsibility:** create brain-region maps, selected-ROI sequences, calibration plots, performance-versus-budget curves and reproducible report figures.
- **Depends on:** atlas labels, ROI scores, evaluation outputs and Plotly/Nilearn.
- **Key files planned:** `brain_map.py`, `roi_policy_map.py`, `performance_curves.py`, `report_figures.py`.

## Data flow

1. Researcher obtains approved PPMI exports and records the data release and terms.
2. Data manager validates schemas and creates pseudonymous participant, clinical-visit and scan tables.
3. Inventory process identifies MRI sequences using LONI metadata and DICOM headers, then counts participant-level overlap with clinical endpoints.
4. Cohort builder defines index visit, diagnosis cohort, baseline window, follow-up outcomes and subject-level data splits.
5. Preprocessing produces QC-approved NIfTI derivatives, segmentation masks and atlas-registered ROI definitions.
6. Feature extraction stores global embeddings and candidate ROI feature artifacts. The MRI encoder and supervised predictor are trained on training data only.
7. RL environment initializes an episode from a training participant, reveals one ROI per action and updates predictions. Training targets are available only to the reward function.
8. PPO learns a policy from training episodes. Validation is used for model and reward configuration selection.
9. Held-out evaluation compares PPO against exhaustive, fixed-order, random and greedy policies without exposing held-out labels during episode decisions.
10. Genetic priors and patient-genotype analyses are added as separate ablations when data and evidence permit.
11. Evaluation outputs, manifests and figures are stored with source version, code revision, configuration and seed.

## File tree (planned; implementation files do not exist yet)

```text
src/
|-- data/
|   |-- load_ppmi.py
|   |-- schema.py
|   |-- cohort.py
|   |-- inventory.py
|   `-- manifest.py
|-- preprocessing/
|   |-- dicom.py
|   |-- sequence_classifier.py
|   |-- qc.py
|   |-- t1_pipeline.py
|   |-- registration.py
|   `-- segmentation.py
|-- genetics/
|   |-- gwas.py
|   |-- gene_prioritization.py
|   |-- allen_atlas.py
|   |-- regional_scores.py
|   `-- null_models.py
|-- models/
|   |-- cnn3d.py
|   |-- roi_encoder.py
|   |-- fusion.py
|   |-- diagnosis.py
|   |-- progression.py
|   `-- prediction_service.py
|-- rl/
|   |-- state.py
|   |-- action_space.py
|   |-- environment.py
|   |-- reward.py
|   |-- policy.py
|   |-- rollout.py
|   `-- train_agent.py
|-- evaluation/
|   |-- splits.py
|   |-- classification.py
|   |-- progression.py
|   |-- rl_evaluation.py
|   |-- calibration.py
|   |-- site_validation.py
|   `-- ablation.py
`-- visualization/
    |-- brain_map.py
    |-- roi_policy_map.py
    |-- performance_curves.py
    `-- report_figures.py
```

## External dependencies

- PPMI approved data exports and current PPMI documentation.
- LONI/IDA imaging metadata supplied with the authorized imaging collection.
- GWAS Catalog and suitable fine-mapping / functional-genomics resources, with release dates recorded.
- Allen Human Brain Atlas expression data and a documented atlas-mapping process.
- Optional independent Parkinson's cohorts, only after confirming compatible modalities, labels, permissions and cohort independence.
- Neuroimaging software including dcm2niix, ANTs, FastSurfer and optional FSL/MRtrix3.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
