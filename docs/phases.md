# Phases - PANPM

**Active development dataset:** OpenNeuro `ds005892` v1.0.0 (CC0 1.0). PPMI remains a future dataset adapter and validation target; no PPMI access is currently available.

> Complete phases in order. A phase is done only when its files exist, its checks pass, its evidence is recorded in `debug.md`, and its real status is recorded here and in `status.md`.

## Phase 0 - dataset access and feasibility audit

**Goal:** establish what can actually be studied from the active dataset before selecting MRI modalities or training models.

**Files touched:** `src/data/source_mapping.py`, `src/data/inventory.py`, `src/data/manifest.py`, `src/data/schema.py`, `src/data/ppmi_contracts.py`, `src/data/progression_targets.py`, `docs/ppmi-source-catalog.md`, `docs/progression-targets.md`, `src/data/load_ppmi.py` (planned), `configs/dataset.yaml` (after export audit).

**Work:** PPMI reference-document review is complete, but PPMI access is unavailable. Use the versioned public OpenNeuro ds005892 release for immediate development: record its version, license, download date and checksums; inventory BIDS participants, T1w, BOLD and fieldmap files; validate BIDS metadata, participant-to-file matching, group counts and image geometry; report missingness and cohort balance. Keep PPMI source contracts as a separate future adapter. Do not claim progression endpoint coverage from ds005892 unless longitudinal clinical labels are actually present.

**Done when:** dataset/version/license provenance, participant counts by group, participant-to-modality matching, BIDS metadata completeness, acquisition/geometry summaries, QC exclusions and missingness are reproducible; unknowns and exclusions are documented; no participant-level files are committed. PPMI-specific feasibility remains explicitly pending until approved PPMI access is obtained.

**Status:** Metadata inventory and NIfTI-1 geometry audit are implemented and synthetic-tested. PR #14 merged into `main`; PR checks (run #43725333584) and merge-commit CI (run #43725395612) passed. The local aggregate inventory reports 55 participants (22 Control, 18 PD-NC, 15 PD-MCI), 55 T1w and 55 BOLD files, complete participant coverage, zero missing/empty sidecars and zero invalid NIfTI headers. T1w spacing is 1 mm isotropic; BOLD is 64 x 64 x 32 x 200 with spatial spacing 3.125 x 3.125 x 3.5 mm and TR 2 seconds. The researcher has now rerun the affine diagnostic: all 55 T1w and 55 BOLD scans have qform_code=1 and sform_code=1, with sform selected. T1w qform/sform max absolute differences are 0 for 53 scans and 0.000004/0.000008 for two; BOLD differences range from 0 to 0.001743, with only three above the inventory's 0.001 flag threshold. These small values do not justify qform/sform-based scan exclusion. Orientation summaries are T1w RAS 54 and LPS 1; BOLD LAS 55. These are voxel-axis direction labels, not automatic QC failures. Phase 0 remains open: full BIDS validation, image-level QC, snapshot/download provenance completion, participant-level split feasibility and progression endpoint coverage are not established. PPMI feasibility remains blocked on approved access. No model training has started.

## Phase 1 - Cohort definition and MRI preprocessing

**Goal:** create a leakage-safe PD/HC cohort and quality-controlled baseline MRI derivatives.

**Files touched:** `src/data/cohort.py`, `src/preprocessing/dicom.py`, `src/preprocessing/sequence_classifier.py`, `src/preprocessing/qc.py`, `src/preprocessing/t1_pipeline.py`, `src/preprocessing/registration.py`, `src/preprocessing/segmentation.py`, `configs/preprocessing.yaml`.

**Done when:** each included scan is linked to one participant and visit; sequence identity is verified from metadata; preprocessing outputs pass documented QC; a participant-level split manifest is frozen; raw data remain unchanged.

**Status:** Initial source-independent cohort and split contracts are implemented on branch `phase1/cohort-and-split-contracts`: `build_diagnosis_cohort` preserves HC/PD-NC/PD-MCI source groups, requires one explicitly sequence-verified T1w scan per participant, and excludes ambiguous/missing scans with aggregate reason counts; `make_stratified_split` requires caller-supplied train/validation/test fractions and seed, stratifies by diagnosis, and assigns each participant once. Synthetic tests were added, but CI runs #43728681409, #43728751962 and #43728828396 failed at Ruff import sorting before tests could run; the third run also reported UP012. PR #16 is draft and held under D-014. These helpers have not been executed against the local BIDS snapshot, and no split proportions have been approved or frozen. Voxel-level T1w QC, BOLD motion/temporal QC, visual review, preprocessing, registration, segmentation and local cohort freeze remain outstanding. Phase 1 remains open.

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
**Next:** Return to `context.md` before starting a new task.
