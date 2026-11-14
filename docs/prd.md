# PRD - PANPM

## Problem

Parkinson's disease neuroimaging research needs methods that can relate MRI-derived brain features to diagnosis and longitudinal motor outcomes while keeping the biological interpretation of regional findings testable. A conventional model processes a fixed image representation. PANPM will investigate whether an agent can make a sequence of region-inspection decisions and retain useful predictive performance with a smaller computational inspection budget.

The system is for research use by students and researchers working in neuroimaging, machine learning, computational neuroscience and Parkinson's disease data analysis. It is not intended to diagnose or treat patients.

## Goals

- Build a reproducible PPMI cohort and MRI inventory with participant-level data lineage.
- Establish leakage-resistant baselines for PD-versus-healthy-control classification.
- Forecast 12- and 24-month change in MDS-UPDRS Part III where valid longitudinal observations exist.
- Build an offline MRI-region inspection environment in which the RL agent selects an uninspected region or stops.
- Evaluate PPO against exhaustive, fixed-order, random and greedy region-selection baselines.
- Preserve the original GWAS Catalog / Allen Human Brain Atlas idea as a statistically validated population-level regional prior.
- Test whether MRI, clinical variables and available patient-specific genetic data add distinct value through controlled ablations.
- Produce reproducible reports, model cards, brain-region visualizations and experiment manifests.

## Non-goals

- Clinical diagnosis, screening recommendations, treatment recommendations or patient management.
- Selection of medication, surgery, stimulation settings or other treatment actions by RL.
- Claiming that the first RL agent reduces real MRI acquisition time. Its initial actions control computational inspection of regions from an already acquired scan.
- Assuming that a specific MRI sequence is present for every PPMI participant.
- Treating Allen Atlas expression as an individual's genotype or as Parkinson's-specific expression.
- Claiming a gene is causal because it is near a GWAS locus.
- Using diagnosis labels, future clinical visits or test-set outcomes in the agent's observation or policy-selection process.
- Training or evaluating on data whose PPMI terms do not permit the intended use.

## Users and use cases

- **Research developer:** imports approved PPMI exports, audits MRI sequences and builds reproducible cohorts.
- **Neuroimaging researcher:** inspects preprocessing QC, anatomical features and regional maps.
- **ML researcher:** trains classification and progression baselines, then evaluates adaptive ROI selection.
- **Research reviewer:** inspects data lineage, split definitions, metrics, ablations and limitations.

## Success criteria

- A cohort manifest records each included participant, index visit, diagnosis source, MRI linkage and split assignment without exposing direct identifiers.
- MRI sequence classification is supported by acquisition metadata and QC, not a single ambiguous LONI label.
- Every preprocessing transform is fitted or selected without access to the held-out test set.
- Classification and progression baselines are separately evaluated with subject-level splits.
- Progression targets state the assessment window and medication state.
- The RL simulator can reset, apply valid actions, mask repeated/unavailable regions, update observations, calculate training-only rewards and terminate cleanly.
- RL is compared with exhaustive ROI, fixed-order, random and greedy policies on the same held-out subjects.
- Results include uncertainty intervals, calibration or error analysis, and a complete experiment configuration.
- Any claimed benefit of genetic priors is supported by ablations and appropriate spatial and gene-set null tests.
- The public README describes only capabilities that have actually been implemented and tested.

No accuracy, AUC, sample-size or clinical-use target is asserted before the data audit and power/feasibility analysis.

## Constraints

- Primary data source: PPMI, subject to approved access and applicable data-use conditions.
- MRI modality: unknown until the PPMI imaging inventory is inspected. T1-weighted MRI is the first candidate baseline if adequate coverage and quality are confirmed.
- Research objectives: classification and longitudinal progression.
- RL is a core research objective, implemented first as active ROI inspection.
- The initial software stack is Python 3.11, PyTorch/MONAI, Gymnasium and Stable-Baselines3 Contrib, with neuroimaging tools installed separately.
- The project is a research prototype; no regulatory or clinical validation is claimed.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
