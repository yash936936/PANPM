# Branch protection - PANPM

A CI workflow cannot prevent a red merge by itself. Branch protection must be configured by the repository owner. No PANPM GitHub repository slug or branch-protection state was supplied, so no API command has been run and protection is not applied.

## Required settings for `main`

- Require a pull request before merging.
- Require status check **`ci-pass`** from `.github/workflows/ci.yml`.
- Require branches to be up to date before merging.
- Prevent force pushes and branch deletion.
- Decide whether administrators may bypass protections; any bypass should be documented.

## Owner action

After the repository exists, replace `(open - confirm with user)` with the actual `OWNER/REPO` and verify the branch name. Then the repository owner can apply a protection rule with GitHub Settings or the GitHub CLI. Do not run a command against an assumed repository.

```powershell
# Run only after replacing OWNER and REPO with the verified repository slug.
gh api -X PUT repos/OWNER/REPO/branches/main/protection `
  -H "Accept: application/vnd.github+json" `
  -f required_status_checks.strict=true `
  -f "required_status_checks.contexts[]=ci-pass" `
  -F enforce_admins=true `
  -f required_pull_request_reviews.required_approving_review_count=0 `
  -F restrictions=
```

Verify with:

```powershell
gh api repos/OWNER/REPO/branches/main/protection/required_status_checks
```

Record the actual result as a review event. Do not claim protection is active until the owner-run verification succeeds.

## What CI does not prove

See [`NOT-COVERED-BY-CI.md`](NOT-COVERED-BY-CI.md). In particular, CI cannot verify PPMI permissions, MRI quality, model scientific validity, PPO policy behaviour on real participants or independent clinical validation.

---
**Next:** Return to [`context.md`](../context.md) before starting a new task.
