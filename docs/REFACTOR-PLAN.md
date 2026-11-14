# Refactor plan - PANPM

## Status: NOT STARTED

No research source files have been implemented or measured. Do not split or refactor files based on the planned architecture alone.

## Step 0: measure before refactoring

When source code exists, record per-area file count, line count, public symbols, imports, responsibilities and associated tests. Candidate areas are data, preprocessing, genetics, models, RL, evaluation and visualization. These are architecture boundaries, not evidence that a file needs splitting.

## Per-area procedure

1. Run the current tests and record the exact commands and counts.
2. Read `docs/components/<area>.md` and identify public interfaces.
3. Refactor one area per change. Keep behaviour unchanged and preserve the public interface unless a separate decision approves a change.
4. Add or update regression tests before changing the implementation.
5. Run narrow tests, lint and the full suite.
6. Regenerate component docs and resolve any documentation drift.
7. Record the result in `docs/debug.md`, `docs/status.md` and the event log.

## Suggested order after implementation exists

1. Pure data schema and validation utilities.
2. Data joins and cohort construction.
3. MRI preprocessing utilities.
4. Genetic evidence and regional mapping.
5. Prediction models.
6. RL environment and reward logic.
7. Evaluation/reporting interfaces.

This order is provisional and must be revisited after dependencies and test coverage are measured.

## Do not

- Split a class across files by method.
- Mix a behaviour-changing feature with a behaviour-preserving refactor.
- Refactor an area with a HOLD failure without first following `AGENTS.md` section 6.
- Modify raw PPMI data or embed it in tests/fixtures.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
