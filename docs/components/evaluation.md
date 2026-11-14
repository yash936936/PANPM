# Component: evaluation

> Location: `src/evaluation/`. Planned source area; implementation is not present yet.

## Purpose

Define participant-level cohort splits, calculate classification/progression/policy metrics, assess calibration and uncertainty, run ablations and test site/cohort generalization.

## Route

Evaluation consumes frozen split manifests, true targets and model/policy outputs. It produces metrics and reports; it must not feed held-out targets back into training or policy tuning. No runtime route exists yet.

## Config surface and invariants

- Keep participants and all their visits in one partition.
- Maintain locked test and independent external cohorts.
- Report AUROC/AUPRC, sensitivity/specificity, balanced accuracy, Brier score and calibration for classification.
- Report MAE/RMSE and uncertainty intervals for progression.
- Report performance versus number of ROIs and measured processing cost for RL.
- Record confidence intervals, exclusions, missingness and site/scanner distribution.
- Do not claim external validation without an independent cohort.

## Known limits

Sample sizes, site counts, class balance and endpoint completeness are unknown until the PPMI inventory is complete.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
