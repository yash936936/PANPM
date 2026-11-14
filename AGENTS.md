# AGENTS.md - PANPM engineering instructions

This is the authoritative instruction file for coding agents working in PANPM. `context.md` routes here; `prompt.md` is a short entry wrapper. If instructions conflict, follow this file unless a newer decision in `docs/decisions.md` supersedes it.

## 1. Entry protocol

1. Read `context.md`.
2. Read the newest entry in `docs/status.md`.
3. Read `docs/FAILURE-LEDGER.md`; do not work in an area on HOLD until section 6 has been followed.
4. Read `docs/decisions.md` newest first. Hard decisions: D-008 research-only and data handling; D-007 participant split and label isolation; D-006 genetic-prior distinction; D-005 RL is active ROI inspection; D-004 dual outcomes; D-003 modality inventory first; D-002 PPMI primary; D-001 project scope.
5. Read `docs/components/<area>.md` for each area being changed.
6. Check `git status`, then run `ruff check .` and `pytest -q` as applicable. Keep commands separate and record commands/results.

## 2. Evidence classes

| Class | Meaning | Does not prove |
|---|---|---|
| Specified | Architecture or feature is documented | That code or data exist |
| Implemented | Source code exists | That it works or is scientifically valid |
| Tested | A named automated check passed | Clinical validity or external generalization |
| Research-evaluated | Frozen model evaluated on held-out data with reproducible metrics | Clinical utility |
| Externally validated | Tested on an independent eligible cohort/site | Regulatory approval or clinical deployment |

Never fabricate PPMI sample counts, labels, MRI sequences, model results, biological findings or policy behaviour. Record unknowns as unknown. A green CI run does not constitute research evaluation.

## 3. Hard prohibitions

- Do not use PANPM as a diagnostic, screening or treatment recommendation system (D-008).
- Do not place raw PPMI data, direct identifiers, private participant mappings, genetic records, credentials or restricted paths in Git, ordinary logs, screenshots or public reports (D-008).
- Never expose diagnosis labels or future progression outcomes to the RL policy observation; training labels may be used only by the reward/training process (D-007).
- Never fit preprocessing, feature selection, harmonization, calibration or policy choices on test participants (D-007).
- Do not reinterpret active ROI inspection as physical scan acquisition or reduced MRI scan time (D-005).
- Do not describe Allen Atlas expression as patient-specific or PD-specific expression (D-006).
- Do not assume MRI modality coverage before inventory and sequence verification (D-003).
- Never weaken a data-use, privacy, split, QC or validation rule to make a test pass.
- Do not add credentials or secret values to command arguments, config files or events. Use environment variables or approved secret storage.
- Do not add model-specific or participant-specific workarounds without a decision entry, a general regression test and a component-document update.
- Do not edit generated regions in `docs/FAILURE-LEDGER.md` or between generated markers in component docs.
- Commit-message convention: (open - confirm with repository owner before first commit).

## 4. Code structure rule

Use one source file per responsibility, not one file per function. Do not split a class across files by method. Every source file must start with a module docstring/comment whose first line states its responsibility. Keep components under the areas in `docs/components/`. Update the handwritten Purpose, Route, Config/invariants and Known limits sections when behaviour changes. Run `node scripts/docs/gen-components.mjs` after source changes and `node scripts/docs/check-docs.mjs` before a PR.

Refactor one area per PR, preserve behaviour, and keep feature work separate. Follow `docs/REFACTOR-PLAN.md`.

## 5. Debugging procedure

1. Reproduce with the smallest useful command using `node scripts/events/run-logged.mjs --area <AREA> -- <command>` where practical. On Windows shell commands may need `--shell`.
2. Identify the likely layer: source data, schema mapping, config, preprocessing, model, RL environment, dependency or platform. State a hypothesis and what result would disprove it.
3. Change one cause at a time and rerun the same reproduction.
4. Add a regression test that fails before the fix and passes after it.
5. Run the narrowest test first, then lint, then the full test suite.
6. Record the finding in `docs/debug.md`, design change in `docs/decisions.md` if material, and final state in `docs/status.md`. State what was not tested.

## 6. Repeated failure rule

Failure signatures are generated from the first specific error line plus the failing test name. Runner summary lines are not valid signatures.

- Two occurrences of the same area/signature: stop and state a new testable hypothesis before another attempt.
- Three occurrences without resolution: mark the area HOLD. Stop retrying. Record prior attempts and unknowns in `docs/debug.md`, then choose one path in a new decision: replace the approach wholesale or put it on hold. Log a `resolution` event using the exact area and signature from `docs/FAILURE-LEDGER.md`.
- Never delete or rewrite event history. The ledger is regenerated from `docs/logs/events.jsonl`.

## 7. Logging duties

| Event | Record |
|---|---|
| Implementation command | `docs/logs/events.jsonl` through `run-logged.mjs` |
| Review or owner evidence | Event using `log-event.mjs` |
| Completed coding/data task | New entry in `docs/debug.md` |
| Design/scope choice | New ID in `docs/decisions.md` |
| End of session | New entry in `docs/status.md` |
| Phase completion | Update `docs/phases.md` and actual capabilities in `docs/readme.md` |

Do not include source participant IDs, sensitive data, private file paths or secrets in events. Keep the event log append-only.

## 8. CI and merging

- Required status check: `ci-pass`; see `docs/BRANCH-PROTECTION.md`.
- Do not merge a red check.
- CI cannot verify PPMI permissions, DICOM de-identification, visual QC, real MRI processing, clinical endpoint validity, PPO research behaviour, external validation or clinical utility. See `docs/NOT-COVERED-BY-CI.md`.
- Before a PR, run `ruff check .`, `pytest -q` when tests exist, `node scripts/docs/gen-components.mjs --check`, `node scripts/docs/check-docs.mjs`, `node scripts/events/failure-report.mjs --check` and `node scripts/ci/secret-scan.mjs`.
- Branch protection is an owner action and is not applied by this scaffold.

## 9. Handoff

End every coding session with: what changed, exact checks and outcomes, what was not checked, relevant decision IDs, updated docs and the next concrete action. Do not claim a phase is complete without its definition-of-done evidence.

---
**Next:** Return to [`context.md`](context.md) before starting a new task.
