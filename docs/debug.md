# Debug log - PANPM

> Append-only log. Newest entries go at the top. Record actual commands, outputs, failed attempts and what remains unverified. Do not invent test results.

## DBG-002 - Phase 0 metadata utilities - 2026-11-15
**Task:** Add minimal, dependency-light utilities for explicit source mappings, tabular export inventory and pseudonymous participant-by-modality coverage.
**Changed:** Added `src/data/source_mapping.py`, `src/data/inventory.py`, `src/data/manifest.py` and three corresponding pytest modules on branch `research/phase0-repository-audit`. Added explicit validation for missing source columns, duplicate target mappings and missing required normalized fields. Inventory records file name, release identifier, size, SHA-256 and CSV header. Coverage aggregation uses keyed HMAC-SHA256 participant keys and counts series per modality; missing participant/modality values are skipped.
**Tests attempted:** Attempted `git clone --depth 1 --branch research/phase0-repository-audit https://github.com/yash936936/PANPM.git /tmp/panpm-audit && python -m pytest -q`. The clone failed before tests ran: `Could not resolve host: github.com`. No pytest or Ruff result is claimed.
**Not tested:** The new modules have not been executed in a local checkout. No PPMI data, export headers, sequence metadata, cohort labels or MRI files were supplied. No PPMI-specific mapping or scan classification has been created.
**Privacy:** HMAC secret material must be generated and stored outside the repository. The pseudonym is a project linkage key, not anonymization; access controls and PPMI terms still apply.

## DBG-001 - Initial documentation scaffold - 2026-11-15
**Task:** Create PANPM documentation and engineering-governance scaffold from the approved project-docs setup guide and the research design discussed in this conversation.
**Tested:** `node scripts/docs/gen-components.mjs` generated seven component guides; the final `node scripts/docs/gen-components.mjs --check` passed; `node scripts/docs/check-docs.mjs` passed; `node scripts/events/failure-report.mjs --check` passed; `node scripts/selftest.mjs` passed all 20 checks; PyYAML parsed `.github/workflows/ci.yml`, confirmed all five jobs and verified the `requirements-dev.txt` install path; `python -m compileall -q src` exited successfully (there were no Python source files at that time). The self-test uses a temporary synthetic repository and does not test PPMI or PANPM model code.
**Found:** No PANPM source implementation, PPMI data export, PPMI imaging metadata or model checkpoint was supplied with this request. The absolute local project-root path, repository slug and coding-agent choice are unknown.
**Fixed:** Created project-specific documentation and engineering scaffold only. Corrected the Python CI dependency file to `requirements-dev.txt`, customized the component-doc generator index and tightened the schema so source participant crosswalks and private filesystem paths remain outside ordinary analysis tables. No research source code or patient data were created.
**Not tested:** PPMI access, cohort counts, sequence classification, MRI preprocessing, model training, RL behaviour, scientific performance, external validation, repository-specific CI execution or branch protection. Python lint/test execution was not run because the research code and tests were not yet present and development dependencies were not installed in that packaging pass.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
