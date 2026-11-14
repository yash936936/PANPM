# Component: visualization

> Location: `src/visualization/`. Planned source area; implementation is not present yet.

## Purpose

Create research figures for regional MRI features, genetic-reference enrichment, selected ROI sequences, uncertainty and predictive performance versus inspection budget.

## Route

Evaluation and feature artifacts feed static or interactive visualizations. Figure scripts must write source data/config references with the output so plots can be reproduced. No runtime route exists yet.

## Config surface and invariants

- Display the atlas name/version and coordinate space.
- Distinguish MRI-derived effects, population genetic priors and RL selection frequencies.
- Do not label a region causal or disease-specific solely because it is highlighted.
- Include uncertainty and sample-size information where meaningful.
- Do not render participant-identifying metadata.

## Known limits

No imaging-derived results exist. The 3D visualization approach will be chosen after atlas registration and output requirements are established.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
