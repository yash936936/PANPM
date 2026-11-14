# Component: genetics

> Location: `src/genetics/`. Planned source area; implementation is not present yet.

## Purpose

Prioritize PD-associated genes using traceable GWAS, fine-mapping, QTL and functional evidence, map those genes to Allen Human Brain Atlas expression, and derive a versioned population-level regional prior.

## Route

Versioned GWAS and functional-genomics evidence feed gene prioritization. The selected gene set and Allen Atlas expression feed region mapping and null-model analysis. The resulting regional prior is consumed by controlled model-ablation experiments. Participant genotype/PRS, if authorized, is a separate input branch. No runtime route exists yet.

## Config surface and invariants

- Record data source, release, identifier namespace and gene-mapping version.
- Do not equate nearest genes with causal genes.
- Keep gene evidence types traceable and weights reproducible.
- Distinguish Atlas reference expression from participant genotype.
- Use matched gene-set nulls, spatially aware nulls, donor sensitivity and multiple-testing correction.

## Known limits

Allen Atlas is a healthy post-mortem reference and cannot establish patient-specific or PD-specific expression. PPMI participant genotype availability and permissions are not yet verified.

<!-- BEGIN GENERATED: do not edit between markers -->

### Files and exports

| File | Exports | Responsibility (first header-comment line) |
|---|---|---|

**Imports other areas:** (none)

**Tests:** (none matched by name)

<!-- END GENERATED -->

---
**Next:** Return to [`context.md`](../../context.md) before starting a new task.
