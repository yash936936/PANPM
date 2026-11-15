# PANPM - Parkinson's Active Neuroimaging and Progression Model

PANPM is a proposed research pipeline for studying Parkinson's disease using PPMI longitudinal clinical and MRI data. It is designed to compare MRI-based diagnosis and motor-progression models, explore genetically informed regional priors from GWAS and the Allen Human Brain Atlas, and test a PPO agent that learns which pre-existing MRI brain regions to inspect sequentially.

## Status

Documentation and engineering scaffold created on 2026-11-15. No PPMI data have been imported and PPMI MRI sequence availability is not audited. The first-pass T1w voxel-QC module and private montage CLI passed CI and were run locally on 55 OpenNeuro scans with zero configured review flags; expert visual review of all montages remains outstanding. A separate BOLD temporal-QC module and private CLI passed CI run #43731175121 (73 tests), but have not yet been run on local BOLD scans. This BOLD module does not estimate or correct motion; optional FD requires external motion estimates. Brain extraction, registration, segmentation, MRI preprocessing, supervised models, RL environment, PPO agent, genetic analysis and scientific evaluation are not implemented. No performance results are available.

## Setup

The project targets Python 3.11. Install development tools with `python -m pip install -r requirements-dev.txt`. Install optional first-pass T1w QC dependencies with `python -m pip install -r requirements-imaging.txt`. Additional preprocessing and ML dependencies remain subject to a local pilot and version pinning. Node.js 22 is used for documentation/event scripts.

The first research task is the PPMI data and imaging metadata inventory, not model training. See `docs/phases.md` Phase 0.

## Research scope

- PD-versus-healthy-control classification.
- 12- and 24-month MDS-UPDRS Part III progression forecasting where valid endpoints exist.
- Genetic and transcriptomic regional reference priors.
- Offline RL for adaptive computational inspection of MRI regions.

PANPM is a research prototype and is not a medical device or clinical decision tool.

## Structure

See `docs/architecture.md` for the system design and `docs/data-dictionary.md` for the planned internal schema.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
