# Debug log - PANPM

> Append-only log. Newest entries go at the top. Record actual commands, outputs, failed attempts and what remains unverified. Do not invent test results.

## DBG-001 - Initial documentation scaffold - 2026-11-15
**Task:** Create PANPM documentation and engineering-governance scaffold from the approved project-docs setup guide and the research design discussed in this conversation.
**Tested:** `node scripts/docs/gen-components.mjs` generated seven component guides; the final `node scripts/docs/gen-components.mjs --check` passed; `node scripts/docs/check-docs.mjs` passed; `node scripts/events/failure-report.mjs --check` passed; `node scripts/selftest.mjs` passed all 20 checks; PyYAML parsed `.github/workflows/ci.yml`, confirmed all five jobs and verified the `requirements-dev.txt` install path; `python -m compileall -q src` exited successfully (there are no Python source files yet). The self-test uses a temporary synthetic repository and does not test PPMI or PANPM model code.
**Found:** No PANPM source implementation, PPMI data export, PPMI imaging metadata or model checkpoint was supplied with this request. The absolute local project-root path, repository slug and coding-agent choice are unknown.
**Fixed:** Created project-specific documentation and engineering scaffold only. Corrected the Python CI dependency file to `requirements-dev.txt`, customized the component-doc generator index and tightened the schema so source participant crosswalks and private filesystem paths remain outside ordinary analysis tables. No research source code or patient data were created.
**Not tested:** PPMI access, cohort counts, sequence classification, MRI preprocessing, model training, RL behaviour, scientific performance, external validation, repository-specific CI execution or branch protection. Python lint/test execution was not run because the research code and tests are not yet present and development dependencies were not installed in this packaging pass. The full GitHub Actions workflow was not executed in a remote repository.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
