# Phases - PANPM

> Complete phases in order. A phase is done only when its files exist, its checks pass, its evidence is recorded in `debug.md`, and its real status is recorded here and in `status.md`.

## ## Phase 0 - PPMI access and feasibility audit
**Goal:** establish what can actually be studied before selecting MRI modalities or training models.

**Files touched:** `src/data/source_mapping.py`, `src/data/inventory.py`, `src/data/manifest.py`, `src/data/schema.py`, `src/data/load_ppmi.py` (planned), `configs/dataset.yaml` (after export audit), `docs/data-dictionary.md`, `docs/research-protocol.md`.

**Work:** obtain approved data access; record data release and terms; inspect official cohort, clinical, MRI and LONI metadata; build participant-by-modality and participant-by-endpoint overlap; validate participant/visit/scan joins; generate a feasibility report.

**Done when:** cohort counts, modality coverage, scanner/site distribution, endpoint completeness and missingness are reproducible; all unknowns and exclusions are documented; no direct identifiers appear in outputs.

**Status:** In progress. Generic inventory, explicit mapping, pseudonymous coverage and internal schema-contract utilities are implemented on `research/phase0-repository-audit`. The user currently has no PPMI access or files. PPMI-specific feasibility audit is blocked until approved exports and imaging metadata are available. No PPMI fields or MRI sequences are assumed.
## Phase 1 - Cohort definition and MRI preprocessing
**Goal:** create a leakage-safe PD/HC cohort and quality-controlled baseline MRI derivatives.

**Files touched:** `src/data/cohort.py`, `src/preprocessing/dicom.py`, `src/preprocessing/sequence_classifier.py`, `src/preprocessing/qc.py`, `src/preprocessing/t1_pipeline.py`, `src/preprocessing/registration.py`, `src/preprocessing/segmentation.py`, `configs/preprocessing.yaml`.

**Done when:** each included scan is linked to one participant and visit; sequence identity is verified from metadata; preprocessing outputs pass documented QC; a participant-level split manifest is frozen; raw data remain unchanged.

**Status:** Not started.

## Phase 2 - Supervised MRI and clinical baselines
**Goal:** establish trusted diagnosis and progression reference models before RL training.

**Files touched:** `src/models/cnn3d.py`, `src/models/roi_encoder.py`, `src/models/diagnosis.py`, `src/models/progression.py`, `src/evaluation/splits.py`, `src/evaluation/classification.py`, `src/evaluation/progression.py`, `configs/model.yaml`.

**Done when:** clinical-only, MRI-feature and MRI-CNN baselines run with participant-level splits; progression targets are medication-aware and time-aligned; training-only transforms are enforced; validation and test results are reproducible.

**Status:** Not started.

## Phase 3 - Genetic and transcriptomic regional priors
**Goal:** reproduce and strengthen the GWAS-to-Allen-Atlas spatial enrichment analysis.

**Files touched:** `src/genetics/gwas.py`, `src/genetics/gene_prioritization.py`, `src/genetics/allen_atlas.py`, `src/genetics/regional_scores.py`, `src/genetics/null_models.py`, `src/models/fusion.py`.

**Done when:** variant-to-gene evidence is traceable; Atlas donor/probe/region processing is versioned; matched gene-set and spatial null tests are run; donor robustness is reported; genetic-prior ablations are compared with MRI-only models.

**Status:** Not started.

## Phase 4 - RL environment and PPO agent
**Goal:** train and evaluate sequential ROI-inspection policies.

**Files touched:** `src/rl/state.py`, `src/rl/action_space.py`, `src/rl/environment.py`, `src/rl/reward.py`, `src/rl/policy.py`, `src/rl/rollout.py`, `src/rl/train_agent.py`, `src/evaluation/rl_evaluation.py`, `configs/rl.yaml`.

**Done when:** environment tests cover reset, transitions, action masks, repeated actions, STOP, budget limits and label isolation; rewards use training-only targets and cross-fitted predictions; PPO is compared on identical held-out participants with exhaustive, fixed, random and greedy policies; performance-versus-budget curves and uncertainty are reported.

**Status:** Not started.

## Phase 5 - Multimodal extension
**Goal:** add additional MRI modalities and patient-specific genetic data only where coverage and permissions support valid paired analysis.

**Files touched:** modality-specific modules under `src/preprocessing/`, `src/models/fusion.py`, `src/data/` and associated evaluation modules.

**Done when:** the modality-specific participant intersection is documented; missing-modality handling is explicit; models are compared on matched cohorts; no performance gain is attributed to modality differences in cohort composition.

**Status:** Not started.

## Phase 6 - Generalization, reporting and research release
**Goal:** complete ablations, independent validation and reproducible research outputs.

**Files touched:** `src/evaluation/site_validation.py`, `src/evaluation/ablation.py`, `src/visualization/`, `reports/`, `docs/readme.md`, `docs/research-protocol.md`.

**Done when:** all primary experiments are repeated with frozen configurations; confidence intervals and failure cases are reported; independent validation is completed where eligible data exist; limitations and unrun gates are explicit; all reported figures are regenerable.

**Status:** Not started.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
