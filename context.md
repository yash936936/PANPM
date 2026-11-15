# Context - PANPM

> Entry point. Read this file first at the start of every session, before touching code or any other project document. If you opened another file first, return here.

## What this project is

**PANPM (Parkinson's Active Neuroimaging and Progression Model)** is a research system for MRI-based Parkinson's disease analysis, with planned motor-progression modelling, regional interpretation and an RL agent for sequential computational ROI inspection. The RL task is active inspection of an already acquired scan, not treatment selection or physical MRI sequence ordering. OpenNeuro ds005892 v1.0.0 is the active public development dataset because approved PPMI access is not currently available. PPMI source contracts remain a future adapter. The researcher has run the corrected local aggregate BIDS inventory and supplied affine diagnostics. PR #14 added NIfTI-1 affine and spatial/temporal metadata validation and is merged with passing CI. All 55 T1w and 55 BOLD files have coded qform/sform; the observed differences are small and do not justify scan exclusion. T1w orientation counts are RAS 54/LPS 1; BOLD is LAS 55. Initial metadata-only diagnosis cohort and participant-split helpers exist in draft PR #16, but are held under D-014 after three CI lint failures and are not merged or tested. They have not been run on local data. T1w image QC, BOLD motion/temporal QC, visual review and MRI preprocessing remain unimplemented. No model has been trained.

## Project location

The project root is the directory containing this file. The absolute local path has not been supplied yet. Keep the same root open in the editor, terminal, Git workspace and any coding agent. Record the absolute path in `docs/workflow.md` once the repository is created locally.

## Folder structure

```text
PANPM/
|-- context.md
|-- AGENTS.md
|-- prompt.md
|-- README.md
|-- requirements-dev.txt
|-- Makefile
|-- .gitignore
|-- .github/workflows/ci.yml
|-- configs/
|-- data/                         # ignored; local/restricted data only
|   |-- raw/
|   |-- interim/
|   `-- processed/
|-- src/
|   |-- data/
|   |-- preprocessing/
|   |-- genetics/
|   |-- models/
|   |-- rl/
|   |-- evaluation/
|   `-- visualization/
|-- tests/
|-- scripts/
|   |-- events/
|   |-- docs/
|   `-- ci/
`-- docs/
    |-- prd.md
    |-- trd.md
    |-- architecture.md
    |-- phases.md
    |-- decisions.md
    |-- debug.md
    |-- appflow.md
    |-- workflow.md
    |-- readme.md
    |-- status.md
    |-- data-dictionary.md
    |-- research-protocol.md
    |-- NOT-COVERED-BY-CI.md
    |-- BRANCH-PROTECTION.md
    |-- REFACTOR-PLAN.md
    |-- FAILURE-LEDGER.md
    |-- components/
    `-- logs/events.jsonl
```

The directory structure, PPMI source contracts, aggregate table-grain audits, explicit mapping configuration, aggregate feasibility tools, local DICOM header indexer, BIDS metadata inventory and NIfTI-1 affine/orientation audit are implemented. PR #14 and its CI checks passed. The OpenNeuro local inventory reports complete T1w/BOLD file coverage across 55 participants; the corrected affine report has been reviewed at aggregate level. No approved participant-level PPMI exports have been processed. Image-level QC, visual review and MRI preprocessing remain unimplemented. Initial cohort/split contracts are held in draft PR #16 after repeated Ruff import-order failures and have not been executed on local data. Supervised models, genetics and RL remain unimplemented.

## Where to look by task

| I need to... | Read first |
|---|---|
| Understand the research problem and scope | `docs/prd.md` |
| Understand technical requirements and model constraints | `docs/trd.md` |
| Understand the complete system design | `docs/architecture.md` |
| Know what to build next | `docs/phases.md` and `docs/status.md` |
| Understand PPMI source tables and MRI fields | `docs/ppmi-source-catalog.md` and `docs/mri-metadata-intake.md` |
| Understand progression endpoint safeguards | `docs/progression-targets.md` |
| Understand the normalized PANPM tables | `docs/data-dictionary.md` |
| Extract what is implemented and prepare data intake | `docs/repo-extraction.md` |
| Understand experimental controls and endpoints | `docs/research-protocol.md` |
| Understand RL state, actions, reward and episode flow | `docs/code_logic.md` |
| Understand the researcher workflow | `docs/appflow.md` |
| Understand development tools and handoffs | `docs/workflow.md` |
| Review previous design decisions | `docs/decisions.md` |
| Review bugs and failed attempts | `docs/debug.md` |
| Review the current verified project state | `docs/status.md` |
| Work on a specific source area | `docs/components/README.md` and `docs/components/<area>.md` |
| Follow coding-agent rules | `AGENTS.md` |

## Evidence rules

Never describe a proposed feature as implemented. Use these evidence classes consistently:

1. **Specified:** a design is documented, but no code or data has verified it.
2. **Implemented:** source code exists, but may not have been tested.
3. **Tested:** a stated test or validation ran and its command/result are recorded.
4. **Research-evaluated:** a model was evaluated on the specified held-out data with reproducible metrics.
5. **Externally validated:** results were tested on an independent eligible cohort or site and the data provenance is documented.

A passing unit test is not clinical validation. A model metric is not evidence of clinical utility.

## Logging rules

- Every completed coding or data-pipeline task gets an entry in `docs/debug.md`, including what was tested and what was not tested.
- Every material design choice gets a new entry in `docs/decisions.md`. Do not rewrite older decisions; supersede them with a new ID.
- Every work session ends with a new entry at the top of `docs/status.md`.
- Every command used for project implementation or data processing should be run through `scripts/events/run-logged.mjs` where practical. Do not put credentials, participant identifiers or private paths into event logs.
- `docs/logs/events.jsonl` is append-only. `docs/FAILURE-LEDGER.md` is generated and must not be edited manually.
- At two occurrences of the same failure, form a new testable hypothesis. At three, stop retrying and either replace the approach or put that area on hold with a decision and resolution event.

## Roles

**Mode: split.** The research assistant in chat maintains and reviews documentation, checks claims against supplied evidence and prepares implementation instructions. A project coding agent implements and runs the code.

**Coding agent:** (open - choose the agent and its environment before the first implementation handoff). No coding-agent configuration or repository checkout was supplied with this documentation request, so no tool has been inferred.

**Editor and terminal:** not confirmed for this repository. Use one shared project root across them. Record the absolute project path in `docs/workflow.md` once confirmed.

## Current task

Continue Phase 0/1 using the local OpenNeuro ds005892 v1.0.0 snapshot. PR #14 is merged and CI is green. Run the full BIDS validator on the local snapshot. Then implement T1w image QC and BOLD motion/temporal QC as separate paths, followed by visual review, reproducible T1w preprocessing and a frozen participant-level split manifest. Do not train models until QC exclusions, cohort rules and leakage-safe participant splits are frozen. Keep all participant-level data and derived manifests local. PPMI access and PPMI-specific feasibility remain a separate future gate.

External pretrained MRI model selection: BrainIAC is excluded from primary PPMI held-out evaluation because an independent 2026 benchmark explicitly reports that BrainIAC was pretrained on PPMI. Exact participant/scan overlap is unknown. Triad is the next candidate to audit, but its pretraining cohort must be checked for PPMI overlap and its checkpoint license confirmed before use. Every pretrained model needs a documented upstream cohort-overlap audit; a participant-disjoint downstream split alone cannot remove pretraining contamination.
