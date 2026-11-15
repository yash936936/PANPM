# Context - PANPM

> Entry point. Read this file first at the start of every session, before touching code or any other project document. If you opened another file first, return here.

## What this project is

**PANPM (Parkinson's Active Neuroimaging and Progression Model)** is a research system using PPMI longitudinal data to study Parkinson's disease through MRI-based classification, motor-progression forecasting, genetically informed regional interpretation, and a reinforcement-learning agent that sequentially selects MRI brain regions for computational inspection. The RL agent's first task is active ROI inspection, not treatment selection and not physical MRI sequence ordering. The project is in Phase 0. Official PPMI reference documents have been inspected, but no approved participant-level exports or MRI images have been processed and no model has been trained.

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

The directory structure, metadata inventory, PPMI source contracts, aggregate table-grain audits, explicit mapping configuration and aggregate Phase 0 coverage-report functions are implemented. These utilities are source-independent and have not yet been run on approved participant-level PPMI exports. Approved-release ingestion, MRI preprocessing, models, genetics and RL remain unimplemented.

## Where to look by task

| I need to... | Read first |
|---|---|
| Understand the research problem and scope | `docs/prd.md` |
| Understand technical requirements and model constraints | `docs/trd.md` |
| Understand the complete system design | `docs/architecture.md` |
| Know what to build next | `docs/phases.md` and `docs/status.md` |
| Understand PPMI source tables and MRI fields | `docs/ppmi-source-catalog.md` |
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

Continue Phase 0. The repository implementation state is extracted in `docs/repo-extraction.md`. The aggregate feasibility pipeline is implemented but not yet CI-verified or run on real exports. Obtain approved PPMI access and actual Participant Status, MRI, MRI Acquisition, MRIQC, NUPDRS3TRT, LEDDLOG and LONI metadata exports. Validate the example mappings and LONI join keys against the exact release, inventory outside Git, audit table grain and state/sequence coverage, then freeze the clinical target rule. Do not train models or PPO until cohort feasibility and participant-level splits are established.
