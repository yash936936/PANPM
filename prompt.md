# PANPM coding-agent entry prompt

Before changing anything:

1. Read `context.md`, the newest `docs/status.md` entry, `docs/FAILURE-LEDGER.md`, `docs/decisions.md` and the relevant `docs/components/<area>.md`.
2. Confirm the working tree and current phase. The project is currently at Phase 0; PPMI data and MRI availability have not yet been audited.
3. Follow `AGENTS.md` as the authoritative engineering and data-safety rules.
4. Work only on the specific task and files approved for the current phase. Do not skip the PPMI inventory and begin model training with assumed data.
5. Record commands through the event logger where practical. Update `docs/debug.md` and `docs/status.md`; add a new decision when scope or design changes.
6. State exactly what was tested and what remains unverified. Never claim scientific performance or clinical validity without corresponding evidence.

**Current task:** implement Phase 0 only after PPMI access and the local repository environment are available. Build a source-release-aware participant-by-modality and clinical-endpoint inventory. Keep identifiers protected and do not commit data.

---
**Next:** Return to [`context.md`](context.md) before starting a new task.
