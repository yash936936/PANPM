# Context - PANPM

> Entry point. Read this file first at the start of every session, before touching code or any other project document. If you opened another file first, return here.

## What this project is

**PANPM (Parkinson's Active Neuroimaging and Progression Model)** is a research system using PPMI longitudinal data to study Parkinson's disease through MRI-based classification, motor-progression forecasting, genetically informed regional interpretation, and a reinforcement-learning agent that sequentially selects MRI brain regions for computational inspection. The RL agent's first task is active ROI inspection, not treatment selection and not physical MRI sequence ordering. The project is currently at the documentation and design-scaffold stage. No PPMI data have been imported, no MRI modality inventory has been verified, and no model has been trained.

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
    |-- code_logic.md
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

The directory structure and documentation scripts are scaffolded. Generic Phase 0 metadata utilities now exist under `src/data/`; PPMI-specific ingestion, MRI preprocessing, models, genetics and RL implementation remain planned.

## Where to look by task

| I need to... | Read first |
|---|---|
| Understand the research problem and scope | `docs/prd.md` |
| Understand technical requirements and model constraints | `docs/trd.md` |
| Understand the complete system design | `docs/architecture.md` |
| Know what to build next | `docs/phases.md` and `docs/status.md` |
| Understand the data tables | `docs/data-dictionary.md` |
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

**Editor and terminal:** not confirmed for this repository. Use one shared project root across them. The user has previously worked with VS Code, but the PANPM-specific workspace has not yet been confirmed.

## Current task

Continue Phase 0 without PPMI participant data. Public implementation references have been reviewed and recorded in `docs/external-references.md`. Generic CSV export discovery and metadata-only inventory now exist in `src/data/inventory.py`. Official PPMI Data Dictionary, Code List and Data User Guide have not yet been downloaded into this repository. Next, obtain those official documents from the PPMI Data Resources page and extract their exact definitions; keep public repository heuristics separate from official PPMI definitions. Do not create source mappings or MRI sequence rules until they are verified against the official documentation and approved release metadata.
