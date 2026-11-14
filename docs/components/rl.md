# Component: rl

> Location: `src/rl/`. Planned source area; implementation is not present yet.

## Purpose

Provide an offline finite-horizon environment in which an agent sequentially inspects valid MRI ROI representations or stops, then train a masked PPO policy to balance predictive improvement against computational inspection cost.

## Route

A training episode loads a participant's global representation and ROI availability mask. The policy selects one legal ROI or STOP. The environment reveals the chosen ROI, updates the selected mask and predictor state, and calculates training reward. The resulting transition is returned to the PPO learner. Evaluation uses frozen policies and does not expose held-out labels during episode decisions.

## Config surface and invariants

- Primary learner: MaskablePPO from SB3 Contrib.
- Observation: global embedding, selected-region representation, inspection mask, task, prediction, uncertainty and remaining budget.
- Actions: available/uninspected ROI or STOP.
- Mask unavailable, invalid, already-selected and budget-infeasible actions.
- Labels and future outcomes are reward-only training information, never policy observations.
- Use cross-fitted training predictions for reward construction.
- Test participants and labels must not influence policy selection.
- Reward is predictive loss reduction minus a normalized, measured computational cost.
- The first RL claim is computational active inspection only, not reduced scanner time.

## Known limits

ROI action definitions, predictor uncertainty, compute-cost units and episode budget need to be finalized after the MRI pilot. No RL code or trained policy exists.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
