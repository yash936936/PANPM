# App flow - PANPM

PANPM is initially a researcher-facing pipeline rather than a patient-facing application. The flows below describe the intended research operator journey; none of the modelling stages is implemented yet.

## Researcher prepares a PPMI cohort
1. Researcher obtains PPMI access and confirms the permitted data use.
2. Researcher downloads the current clinical, cohort and imaging metadata files.
3. Data inventory validates schemas, source release, visit labels and scan metadata.
4. Cohort builder links participant, visit, clinical assessment and MRI series.
5. Researcher reviews cohort counts, missingness, sequence coverage and QC exclusions.
6. Researcher approves a versioned cohort and subject-level split manifest.

## Researcher trains baseline models
1. Approved MRI series are converted and preprocessed.
2. Segmentation and registration produce candidate ROI masks.
3. Global and regional features are extracted and stored with provenance.
4. Clinical-only and MRI-only baselines are trained.
5. Diagnosis and progression metrics are evaluated separately.
6. Researcher reviews calibration, confidence intervals, failure cases and site effects.

## Researcher trains and evaluates the RL agent
1. A training episode loads a participant's permitted MRI representations.
2. The initial state includes global context, an empty inspection mask, current prediction and remaining budget.
3. PPO selects an available ROI or STOP.
4. The environment reveals the selected ROI embedding and updates the prediction.
5. During training only, the reward function uses the participant's training target to measure predictive improvement and subtracts inspection cost.
6. PPO updates its Actor-Critic policy from collected trajectories.
7. A frozen policy is compared on held-out participants with exhaustive, fixed-order, random and greedy baselines.
8. The researcher reviews performance against ROI count/computational cost and inspects selected-region maps.

## Researcher investigates genetic interpretation
1. Researcher obtains the GWAS and fine-mapping evidence with recorded release versions.
2. Gene-prioritization process records locus-to-gene evidence and uncertainty.
3. Allen Atlas expression is mapped to a documented brain atlas.
4. Matched gene-set and spatial null tests evaluate regional enrichment.
5. Regional priors are compared against MRI-only results in an ablation.
6. Reports distinguish reference expression, participant genotype and model-selection behaviour.

## Inference-style research demonstration
1. Load a participant's permitted baseline MRI and the frozen preprocessing/model versions.
2. Create the global representation.
3. Let the frozen agent inspect valid ROI representations sequentially.
4. Return the research model's PD-group score and/or predicted motor-score change, the selected ROI sequence, inspection budget and uncertainty.
5. Display an explicit research-only warning and do not give diagnosis or treatment guidance.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
