# Component: models

> Location: `src/models/`. Planned source area; implementation is not present yet.

## Purpose

Extract global and regional MRI embeddings, build supervised PD classification and motor-progression predictors, and provide stable prediction/loss interfaces to the RL environment.

## Route

Processed MRI and ROI masks feed the global and regional encoders. Encodings feed separate classification and progression heads. A frozen or cross-fitted predictor is called by the RL simulator after each region reveal. No runtime route exists yet.

## Config surface and invariants

- Start with classical and compact 3D CNN baselines.
- Diagnosis and progression targets are separate tasks.
- Keep participant-level data splits fixed and versioned.
- Fit scaling, selection, harmonization and calibration on training data only.
- Progression predictors use baseline data only and record medication-state rules.
- Expose uncertainty and task loss needed for the RL state/reward without exposing target labels to the policy.

## Known limits

No MRI encoder or model checkpoint exists. Architecture, input shape, ROI atlas and hyperparameters require a data feasibility pilot.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
