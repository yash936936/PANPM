# Code logic - PANPM

## Participant and visit alignment
**Where:** planned `src/data/cohort.py` and `src/data/manifest.py`.
**What it does:** creates one pseudonymous participant record, links each clinical assessment and MRI scan to the correct study visit, identifies an index/baseline date, and creates longitudinal target windows.
**Why it is non-obvious:** participants can have repeated visits, multiple scans and multiple clinical assessments in one visit. Medication state can distinguish ON and OFF motor assessments. The model must not treat repeated assessments as independent participants or use a future scan as a baseline predictor. All visits for one participant remain in one data split.

## MRI sequence identity and ROI availability
**Where:** planned `src/preprocessing/sequence_classifier.py`, `src/preprocessing/qc.py` and `src/rl/action_space.py`.
**What it does:** classifies each series using supplied collection metadata and DICOM sequence/acquisition fields, then records which anatomical ROI crops are valid for each participant.
**Why it is non-obvious:** study labels and series descriptions may be inconsistent. Sequence family must be verified with multiple metadata fields and image characteristics. The RL action mask must exclude a region when its crop is missing, segmentation failed or QC is unacceptable.

## Global and regional MRI representations
**Where:** planned `src/models/cnn3d.py` and `src/models/roi_encoder.py`.
**What it does:** produces a low-resolution global brain embedding and high-resolution embeddings for candidate ROI crops. The global vector provides context before the agent selects a detailed region.
**Why it is non-obvious:** the RL environment must reveal only the selected region's detailed representation. If all ROI embeddings are placed in the agent's initial observation, the agent is not actually performing sequential active inspection. Precomputation is permitted for efficiency only if the observation remains masked and hidden until selection.

## RL episode and observation isolation
**Where:** planned `src/rl/state.py` and `src/rl/environment.py`.
**What it does:** starts an episode for one participant and one task, provides the global representation, tracks selected regions, reveals one valid ROI per action, updates the prediction state and terminates on STOP or budget exhaustion.
**Why it is non-obvious:** the environment has access to the training label for reward calculation, but the policy observation must not include that label, future MDS-UPDRS values, test-set outcomes or direct identifiers. The action mask prevents repeated or unavailable region selection. An episode is tied to a participant, not to a random MRI slice.

## Reward shaping
**Where:** planned `src/rl/reward.py`.
**What it does:** rewards the reduction in the task predictor's loss after a region is inspected and subtracts the region's computational cost.

For step t:

`r_t = L_(t-1) - L_t - lambda * cost(action_t)`

The sum telescopes to initial loss minus final loss minus the total weighted inspection cost. STOP ends the episode without revealing another region. The initial and updated loss use the same frozen prediction model for the episode.
**Why it is non-obvious:** training labels are available to calculate loss, but not to choose actions directly. Use cross-fitted training predictions or an equivalent leakage-controlled protocol so the agent is not rewarded for improvements measured on a predictor that memorized the same participant. Validation tunes the policy; test labels are used only after the policy is frozen for final scoring.

## Separate diagnosis and progression policies
**Where:** planned `src/models/diagnosis.py`, `src/models/progression.py` and `src/rl/train_agent.py`.
**What it does:** trains a classification model for PD-versus-HC and a regression model for future motor-score change. Initially, each task gets its own reward configuration and policy, while the MRI encoder can be shared where training design permits.
**Why it is non-obvious:** cross-entropy and Huber losses have different scales and meanings. A task-conditioned policy can be studied later, but the first experiments should not mix incompatible reward signals without normalization and ablation.

## Genetic regional prior
**Where:** planned `src/genetics/` and `src/models/fusion.py`.
**What it does:** links prioritized GWAS candidate genes to Allen Atlas regional expression and derives a reference score per brain region.
**Why it is non-obvious:** the Allen Atlas represents healthy post-mortem donors, not the participant's brain expression during PD. The score is a population-level spatial prior. It requires donor robustness, matched gene-set nulls, spatial-autocorrelation-aware null tests and multiple-testing correction. It must not be described as causal or patient-specific.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
