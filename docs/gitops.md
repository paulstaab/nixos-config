# GitHub verification only

Daily update PR publication and explicit bot-CI dispatch have been removed.
There is no auto-merge, deployment, GitHub update schedule or write-capable
workflow. Existing remote workflow files change only after separate publication
and merge; no remote settings or jobs were changed during local implementation.

Xenon CI remains read-only for PRs and pushes to main that change anything beyond
flake.lock, plus manual dispatch. Lock-only events are ignored. If such a PR is
opened despite the ignored lock policy, GitHub can leave its required check
pending; close it rather than bypass branch protection. Mixed changes still run.

Direct `scripts/gitops-ci` runs create a missing local lock before tests and
validation, preserving existing local pins. Failure to create it stops CI with
an explicit error.

CI generates local locks, evaluates and builds base and candidate using explicit
path flakes, compares closures, detects comparable downgrades and publishes
configuration/service diagnostics. Unpinned base/candidate trees resolve inputs
at validation time, so comparisons are evidence rather than reproducible release
records. No credentials or deployment authority are passed to candidate code.

Host updates run locally; see [updates.md](updates.md). Remote publication,
branch-protection settings and activation remain separate owner decisions.
