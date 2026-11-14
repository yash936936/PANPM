# TRD - PANPM

## Stack

| Layer | Preferred technology | Purpose and status |
|---|---|---|
| Runtime | Python 3.11 | Proposed project runtime; pin after environment validation |
| Numerical data | NumPy, Pandas, SciPy, PyArrow | Tabular processing and Parquet files |
| MRI I/O | NiBabel, pydicom, dcm2niix | NIfTI and DICOM handling |
| Image processing | SimpleITK, ANTs | Bias correction, registration and image operations |
| Segmentation | FastSurfer; atlas-specific tools as required | Structural parcellation and ROI masks |
| Deep learning | PyTorch, MONAI, TorchIO | 3D image encoders and augmentation |
| Classical ML | Scikit-learn, XGBoost | Baselines and calibrated predictors |
| RL environment | Gymnasium | Sequential ROI-inspection simulator |
| RL algorithm | MaskablePPO from SB3 Contrib | Primary discrete-action policy learner |
| Genetic analysis | PLINK, MAGMA, abagen and validated GWAS resources | Genotype and transcriptomic analysis when data are available |
| Evaluation | SciPy, Statsmodels, Captum, SHAP | Statistics and explanation methods |
| Visualization | Nilearn, Plotly; Three.js only for a later interactive viewer | Brain maps and result inspection |
| Storage | NIfTI for image derivatives; Parquet for normalized tables; JSON/YAML for manifests | Reproducible local storage |

The dependency list is a proposed stack, not a locked environment. Heavy or platform-specific packages must be installed and tested separately. No CUDA, GPU type or hardware availability is assumed.

## System requirements

- Development target: Windows with WSL2 or Linux for neuroimaging command-line tools. Native Windows use may be possible for parts of the Python stack but is not assumed for the full pipeline.
- Use a single repository root across the editor, terminal and coding agent.
- Keep raw PPMI data outside version control and preferably on encrypted storage with access controls.
- Store file checksums, source release/version, preprocessing version and run configuration in manifests.
- Support CPU execution for basic tests. GPU training is optional and must be detected rather than assumed.
- Exact RAM, disk, GPU and runtime requirements must be measured after the MRI inventory and representative preprocessing pilot.

## Integration points

- **PPMI:** researcher portal and approved data exports. No undocumented API or automated scraping is assumed. Record the downloaded release, date, terms and file provenance.
- **LONI / imaging metadata:** use supplied collection manifests and DICOM metadata when included in the approved data package.
- **GWAS Catalog and genetic resources:** download or query published association and fine-mapping resources under their stated terms. Store release dates and source URLs.
- **Allen Human Brain Atlas:** use expression data and a documented brain-region mapping through a reproducible pipeline such as abagen, subject to version and probe-processing decisions.
- **External validation cohorts:** optional and only after checking access conditions, sequence compatibility, labels and participant independence.

## Model requirements

### Prediction models

- Establish tabular clinical-only, MRI-feature-only and combined baselines before relying on a large neural model.
- Use a 3D ResNet-18 or another small 3D CNN as the first volumetric baseline.
- Separate global whole-brain features from high-resolution ROI features.
- Train diagnosis and progression heads with task-appropriate targets. The progression head must not treat healthy controls as if they had PD progression measurements.
- Report uncertainty and calibration for classification, and prediction error with uncertainty for progression.

### RL model

- Initial problem: finite-horizon, partially observed sequential ROI inspection from a pre-existing MRI volume.
- Actions: inspect one available, uninspected ROI, or STOP.
- State: global embedding, selected ROI embeddings or their aggregated representation, inspected-region mask, current task prediction, uncertainty, remaining budget and task identifier.
- Observation must not contain diagnosis labels, future visits, progression targets, split labels or reward values.
- Reward is computed only inside the training environment using training targets. Use cross-fitted training predictions to reduce in-sample reward leakage.
- Primary learner: masked PPO with Actor-Critic. Mask invalid, missing, already inspected and budget-infeasible actions.
- Evaluation must include exhaustive ROI, fixed-order, random and greedy policies. A DQN experiment is optional and requires an explicitly tested action-mask implementation.
- State clearly that this policy reduces computational inspection cost only. It does not choose real scan acquisition in the initial study.

## Data and split requirements

- Internal participant key is pseudonymous. Keep any re-identification or source-ID mapping in restricted storage, never in Git or event logs.
- All scans and visits from one participant remain in one split.
- Baseline predictors must be dated no later than the prediction index time, subject to a prespecified alignment window.
- All learned preprocessing, imputation, scaling, feature selection, harmonization and calibration are fitted on training data only.
- External site or cohort validation is separate from the random participant holdout.
- Record all exclusions and missingness; do not silently drop participants.

## Non-functional requirements

- **Security:** no participant identifiers, private imaging paths, access tokens or credentials in Git, screenshots, logs, model cards or reports. De-identify DICOM headers and verify NIfTI sidecars.
- **Reliability:** pipeline stages are deterministic where practical, resumable, checksummed and versioned. Reprocessing must not overwrite raw inputs.
- **Observability:** record commands, code revision, data release, configuration, random seed, output paths and test result. Keep event logs free of sensitive data.
- **Reproducibility:** save split manifests, package versions, model checkpoints, optimizer settings and evaluation scripts.
- **Interpretability:** explain model attention or selection as a model behaviour, not as causal biological proof.

## Known technical constraints

- Actual PPMI imaging modality coverage is unknown until the participant-by-series inventory is built.
- T1 coverage, DTI coverage, neuromelanin MRI, QSM and fMRI coverage must be measured, not inferred from documentation alone.
- Conventional T1 MRI does not provide the same nigral signal as dedicated neuromelanin-sensitive imaging.
- QSM requires appropriate phase and magnitude data and a suitable reconstruction pipeline; an SWI label alone is insufficient.
- Allen Atlas donors are healthy post-mortem references. Regional expression does not establish disease-specific or patient-specific expression.
- Differences in scanner, site, acquisition protocol, medication and disease duration may confound results.
- PPMI access, cohort definitions and permitted analyses are governed by current PPMI documentation and data-use terms.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
