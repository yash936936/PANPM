# Research protocol - PANPM

## Research questions

1. How well do baseline clinical variables, MRI-derived features and volumetric MRI representations distinguish diagnosed PD participants from healthy controls in the defined PPMI cohort?
2. Do baseline MRI-derived features add predictive information for 12- and 24-month change in MDS-UPDRS Part III beyond baseline clinical and demographic variables?
3. Can a sequential ROI-inspection policy retain predictive performance while lowering computational inspection cost compared with exhaustive ROI processing?
4. Do genetically prioritized, Allen Atlas-derived regional priors improve prediction or provide reproducible spatial interpretation beyond MRI-only models?

## Cohorts

- **Primary diagnosis cohort:** participants classified as diagnosed PD and healthy controls according to the current PPMI consensus cohort definition and release.
- **Progression cohort:** diagnosed PD participants with eligible baseline MRI, baseline clinical assessment and valid follow-up motor assessment under the prespecified target rules.
- **Secondary cohort:** prodromal participants, analyzed separately for conversion or longitudinal risk questions after the primary study is established.

Exact inclusion/exclusion criteria, sample counts and diagnostic coding must be taken from the downloaded PPMI release. They are not fixed in this document because no data export has been audited.

## Index date and predictors

Choose a participant-specific index date using a prespecified rule linking baseline clinical assessment and MRI. Document the allowable time difference and apply it without looking at outcomes. Predictors must be available at or before index time. Do not use later visits, post-index medication changes or follow-up imaging as baseline predictors.

## Outcomes

### Classification

Primary label: PD versus healthy control from the official cohort definition. Prodromal participants are excluded from this binary task and handled separately.

### Progression

Primary continuous outcome: change in MDS-UPDRS Part III from baseline to the 24-month target window, where a valid and comparable assessment exists. Twelve-month change is a secondary horizon. Follow-up window tolerance, ON/OFF state and medication adjustment must be declared before outcome extraction. Prefer a prespecified medication-state-consistent analysis and report sensitivity analyses for alternative valid states. Do not treat medication-exposed observed change as untreated neurodegeneration.

## MRI sequence strategy

The sequence inventory is the first empirical gate. T1 is the first candidate baseline if verified participant coverage and QC are adequate. DTI, neuromelanin MRI, QSM and fMRI are conditional. A sequence is not included merely because a label mentions it. Check metadata, acquisition parameters, image content and QC. Maintain a participant-by-modality matrix.

## RL task formulation

- **Environment:** offline simulator built from already available MRI data and ROI masks.
- **Initial observation:** low-resolution whole-brain context plus current task and an empty inspected-region mask; no labels or future outcomes.
- **Action:** inspect one currently available, uninspected ROI or STOP.
- **Transition:** reveal the selected ROI representation, update prediction, uncertainty and remaining inspection budget.
- **Reward:** reduction in task-specific predictive loss minus the measured/normalized computational cost of the action.
- **Learner:** masked PPO as the primary method.
- **Episode:** one participant and one task. No episode may cross participants.
- **Training-only information:** the training target is accessible to the reward function, never to the policy observation. Cross-fitted training predictions reduce reward leakage.
- **Validation:** select policy and hyperparameters using validation participants only.
- **Test:** freeze the policy before final test evaluation. Test labels are not available to the policy or environment transition during the episode.

## Comparison policies

- Exhaustive ROI processing.
- Fixed anatomical ordering.
- Random valid ROI selection.
- Greedy selection by immediate validation of expected loss reduction or uncertainty reduction, defined without access to the test target.
- PPO active selection.
- Optional DQN only after an action-mask implementation has been verified.

Compare each policy at the same region-count and computational-budget points. Report AUROC/AUPRC, sensitivity/specificity, Brier score and calibration for classification; MAE/RMSE and prediction intervals for progression; plus number of ROIs inspected and measured computational cost.

## Data splitting and leakage control

- Split by participant before fitted preprocessing, feature selection, harmonization, calibration or model tuning.
- Keep every visit and scan for one participant in the same partition.
- Use validation data for design choices. Keep the test set locked until models and policies are frozen.
- Fit scaling, imputation and harmonization on training data only. Any harmonization method must be compatible with the intended external/site-held-out test.
- Build train-only cross-fitted predictions for the RL reward signal.
- A separate site-held-out evaluation is required when site counts and participant distribution allow it.
- If an external cohort is used, report data source, inclusion rules, sequence compatibility and all adaptation performed.

## Genetic and imaging-transcriptomic analysis

Use fine-mapping and variant-to-gene evidence rather than nearest-gene assignment alone. Map candidate genes to Allen Human Brain Atlas expression with a versioned method. Compare the weighted risk-gene set against matched gene sets and use spatial-autocorrelation-aware null models. Test donor robustness and correct for multiple comparisons. Interpret output as regional enrichment of PD-associated genetic evidence in healthy reference expression, not PD-specific regional gene activation.

## Ablations

1. Clinical only.
2. MRI features only.
3. Global MRI CNN only.
4. ROI features only.
5. Global plus ROI MRI.
6. MRI without genetic prior versus MRI with regional prior.
7. Participant genotype/PRS branch only if authorized and available.
8. Exhaustive ROI versus fixed, random, greedy and PPO selection.
9. Separate diagnosis and progression policies versus a task-conditioned policy, if pursued.
10. Sensitivity to ROI atlas, cost function, missing ROIs, scanner site and medication-state definition.

## Reporting

Report cohort flow, exclusions, modality coverage, missingness, scanner/site distribution, demographic and clinical characteristics, model configuration, random seeds, metrics with uncertainty intervals, calibration, decision thresholds, failure cases and all unrun validation gates. Do not report a result from a test set repeatedly used for tuning as an unbiased final estimate.

## Protocol status

This is a prespecified design scaffold, not a registered protocol or completed analysis. Exact sample counts, scan windows, exclusion rules, cost units, statistical tests and power calculations must be finalized after the PPMI data inventory.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
