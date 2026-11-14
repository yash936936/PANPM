# Dev workflow - PANPM

**Project root:** the directory containing `context.md`. Absolute local path: (open - record the actual path after the repository is created locally).

**Coding agent:** (open - choose a coding agent and environment before the first implementation handoff). No coding-agent config was supplied or detected in the provided project materials.

**Mode:** split. The research assistant maintains and reviews project documents, research design and verification evidence. The selected coding agent writes and runs implementation code.

## Session workflow

1. Read `context.md`, the newest entry in `docs/status.md`, `docs/FAILURE-LEDGER.md` and relevant decisions.
2. Read the relevant component guide under `docs/components/` before changing that area.
3. Check `git status` and inspect the current phase. Do not assume this scaffold is a working implementation.
4. For design changes, update `docs/decisions.md` before or with the implementation. Supersede old decisions; do not rewrite history.
5. Implement one coherent area at a time. Keep one source file per responsibility and add a header comment/docstring stating the file's responsibility.
6. Run narrow tests, lint/type checks where configured, then relevant full checks. Use the event logger for implementation commands where practical.
7. Record failures and completed checks in `docs/debug.md`. Update component docs and regenerate their generated sections.
8. Update `docs/status.md` at the end of every session. Mark a phase complete only when its definition of done is verified.
9. Update `docs/readme.md` only for capabilities that exist and have evidence. Do not publish planned features as available.
10. Commit and push only after the repository owner has selected a workflow and reviewed data/privacy constraints. No commit-message convention has been specified yet.

## Data workflow

- Access PPMI only through the approved process and follow current data-use terms.
- Keep raw data immutable and excluded from Git.
- Store data-release identifiers and checksums, not sensitive content, in manifests.
- Use pseudonymous participant keys in analysis tables and logs.
- Separate train, validation and test participants before any fitted preprocessing or feature selection.
- Never include diagnosis/future targets in agent observations.

## Verification workflow

- Documentation: `node scripts/docs/gen-components.mjs --check` and `node scripts/docs/check-docs.mjs`.
- Failure ledger: `node scripts/events/failure-report.mjs --check`.
- Secret scan: `node scripts/ci/secret-scan.mjs` (requires a Git checkout).
- Python lint: `ruff check .` after installing `requirements-dev.txt`.
- Python tests: `pytest -q` when tests have been added.
- Full MRI/ML/RL verification is not covered by this documentation scaffold. See `docs/NOT-COVERED-BY-CI.md`.

## Handoff requirements

When a coding agent is selected, every implementation handoff must identify: the exact phase, files/areas, relevant decision IDs, expected tests, what to log in `docs/debug.md`, what to update in `docs/status.md`, and what must not be changed. Until a coding agent is selected, do not invent a tool-specific handoff command.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
