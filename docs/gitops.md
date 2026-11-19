# GitOps preparation (2026-11-19)

Status: local preparation only. No resolved input revisions, installed packages, system services,
credentials or GitHub settings changed. No deployment or merge automation exists.
Daily PR creation is implemented but gated by ENABLE_UPDATE_PRS == true; leave
that variable unset until the owner approves enabling remote maintenance.
The current manual procedures and activation approval requirements remain in force.

## Inspection and pending work

Initial worktree was clean on main at 408e186, equal to the local origin/main
tracking ref. No workflows existed in that tree; remote ci.yml returned 404.
GitHub metadata confirms paulstaab/nixos-config is private, defaults to main,
and allow_auto_merge is false. The connector reports repository admin permissions,
but reading branch protection returned 403. Actions permissions/workflow listing
endpoints are unsupported by the connector. Protection, rulesets, enabled runners,
billing plan, budgets, secrets presence, and Copilot entitlement are unverified.
No credentials were inspected. Remote settings have not been modified.

The previous manual update is committed in 408e186. Its closure
/nix/store/yfmxfpm4c4138lxv1vdlibhnjmgdrj8q-nixos-system-xenon-26.05.20261113.f1e5c35
is both /run/current-system and the selected system profile (generation 8).
Thus it is no longer merely the unpersisted test activation described in that
commit. A later permanent activation is inferred from the profile, not audited.
Generation 7 and its store target remain available:
/nix/store/kqiwkb97g4x8vqqby4fivmw9myh6p1y7-nixos-system-xenon-26.05.20261108.ac588ef.
No generations were removed. Desktop/VS Code smoke tests and new-kernel/early-boot
tests remain unrecorded. Current symlinks alone cannot prove the booted kernel.
The earlier VS Code downgrade was explicitly accepted in that commit; future CI
compares against current main, so it does not retroactively reject that decision.

## Source of truth and CI

After publication and protection, main becomes the approved desired state.
Interactive work uses feature branches and reviewed PRs, never direct main pushes.
The installer hardware file has pre-existing nixfmt differences. CI parses it
but requires formatting only if that protected file changes; all other Nix files
are formatted unconditionally. No protected configuration was edited.

CI runs on every PR to main and push to main, plus manual dispatch. It uses an
isolated GitHub-hosted Ubuntu x86_64 runner, read-only contents permissions,
checkout without persisted credentials, and immutable action commit pins.
No pull_request_target, SSH, host credentials, cache signing keys or deployment
permissions are present. Pin provenance: official action release tags resolved
with git ls-remote (checkout v4.2.2, upload-artifact v4.6.2, install-nix v31.11.3).
Pin updates themselves need manual review, including action runtime requirements.

validate-xenon parses/formats tracked Nix files, checks whitespace, disallows
tracked symlinks/submodules, lints workflows and Bash, exercises security policy
fixtures, runs nix flake check and builds the complete xenon toplevel. Lock
mutation is forbidden. It checks/builds the immutable PR base too (pushes use
the prior main SHA; manual dispatch uses HEAD^). PR checkout is GitHub's merge
candidate. Tool packages come from that tree's locked nixpkgs, not a moving channel.
Candidate PR code can execute on the disposable runner; it is never a trust root
for a future privileged merge decision. Existing repository secrets must not be
injected into this job, even for same-repository PRs.

Artifacts (seven-day retention) and the job summary report changed paths,
old/new release and state versions, kernel/initrd derivations, boot/LUKS/resume
settings, selected networking settings, privileged service inventory, generated
system service unit diffs and complete closure changes. This is a useful review
surface, not an exhaustive semantic security proof: firewall rules beyond the
selected fields, user service changes, package implementation changes and
activation scripts require source/closure review too. Unit diffs flag changes to
networking and privileged services even when their names are unchanged.
No dry activation or switch-to-configuration is executed by CI.

Version detection compares named members of the entire old/new closure using
Nix compareVersions. A lower comparable version fails CI, with no exception list
or label bypass. Multiple package versions can produce conservative false
positives. Renames, removed packages, unversioned outputs and maliciously increased
version strings cannot be classified as downgrades; review closure.diff. Failed
base builds, missing tools, timeout and incomplete reports fail validation.
A failure before diagnostics exist remains a failed job, never a successful check.
A successful build establishes neither hardware compatibility nor benign code.

## Daily update PR

The 05:23 UTC schedule is best effort and may be delayed by GitHub. It is gated
off by default. When explicitly enabled it runs only trusted main, serializes
all invocations, updates only nixpkgs on nixos-26.05 and home-manager on release-26.05,
and requires flake.lock to be the sole changed file. Its Python guard preserves
the entire graph, originals, follows edges, release branch and other pins; only
nixpkgs and Home Manager locked revisions/hashes/timestamps can advance. No-op updates exit
without a commit or PR. A decreasing upstream timestamp fails closed.

The dedicated automation/dependency-updates branch and one open PR are reused.
Only this automation-owned branch may be force-updated with an exact SHA lease;
it never force-pushes main. Unexpected existing branch files/policy changes stop
the job for review. If main advances beyond an old PR so that its diff includes
other files, the job deliberately stops; the owner must review/recreate the
branch. Concurrent external branch edits fail the lease. Do not manually reuse
this branch for feature work. Publishing has contents:write and pull-requests:write
through the ephemeral GITHUB_TOKEN, without a PAT or stored credentials. It never
checks out or executes PR branch code and never builds updated dependencies.
No token is passed as a Nix input or committed. Do not add secrets to this job.

Nixpkgs now uses the fixed nixos-26.05 source ref, with its exact revision in
flake.lock; Home Manager retains release-26.05 and follows that nixpkgs. The
one-time migration changes only nixpkgs original metadata in flake.lock, preserving
all locked revisions, hashes and timestamps. Future daily system PRs change only
flake.lock. Codex keeps its explicit revision URL and remains a manual stable
release update under docs/updates.md. The structural policy does not independently
verify ancestry beyond the fixed upstream release refs; future auto-merge still
requires independent provenance checks. Daily PRs can contain security fixes,
ordinary bug fixes and other changes shipped on the release branch; they are not
restricted to security-only updates.

GITHUB_TOKEN-created PRs can require human approval before their CI runs; behavior
must be verified in this private repository. Never treat absent checks as success.
This preparation adds no PAT/App token to evade that boundary. If truly unattended
CI triggering later needs an App, scope its installation to this repository and
separate PR publication from read-only builds. See GitHub's current
[trigger rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Manual GitHub configuration and future auto-merge

Before enabling remote updates, confirm Actions availability and budget, permit
the pinned actions and GITHUB_TOKEN PR creation, require approval for untrusted
fork workflow runs, and keep default workflow token permissions read-only.
Explicit job permissions elevate only the trusted updater. Inventory existing
secrets without exposing their values; PR CI must have none available to its steps.
Set a spending limit and review artifact retention. Enable ENABLE_UPDATE_PRS only
after an approved publication and successful real PR trial.

Protect main: require PRs, current-base CI validate-xenon, resolved conversations,
dismiss stale approvals, block force pushes/deletion and direct pushes, and
include administrators/no routine bypass. Require human review for all changes
in this preparation. Prefer CODEOWNERS coverage of flake.nix, modules, scripts,
workflows and policy documents with a second trusted reviewer. A PR author cannot
approve their own PR: the single-owner case needs another reviewer or an explicit,
separately reviewed governance decision. Do not invent a self-approval workaround.
Configure optional automatic Copilot review if licensed; its comments are
supplemental, may miss malicious changes, and are never a required security gate.

Automatic merge remains absent. Before adding it, independently validate the
exact PR head and current base from trusted main code in a separate permission
boundary: repository identity, bot branch/author identity, exactly flake.lock,
complete lock graph allowlist and upstream release provenance, nondecreasing
closure versions, sensitive diffs policy and all required successful checks for
that exact SHA. Changed base/head invalidates eligibility. Treat service/boot
changes and ambiguous diagnostics as manual review, not automatic approval.
Do not trust PR-authored policy scripts, labels, comments, artifacts alone or
Copilot approval. A read-only trusted policy job may fetch data and build on an
isolated runner; a distinct minimal merge job can consume its attested exact-SHA
result without executing PR code. No privileged pull_request_target execution.

A blanket required human approval would also block unattended lock-only merges.
Resolve this explicitly before enabling: use an independent required trusted
policy gate that enforces human approval on every noneligible PR, or an
appropriately scoped GitHub App/ruleset design proven not to bypass required CI.
Do not give a merge bot unrestricted protection bypass. Verify review enforcement
with adversarial PR fixtures and failed/missing/stale checks before enabling
repository auto-merge. No repository setting is changed by this preparation.

## Future pull-based agent (design only)

A separately approved NixOS module should create /var/lib/nixos-updater root:root
0700 with checkout, status and GC roots outside every user-writable path. Use a
root-owned installed helper built from reviewed configuration, fixed executables,
sanitized environment, safe Git configuration, no inherited hooks/credential
helpers, no submodules, and no root execution of ~/nixos-config scripts. A
systemd timer polls canonical HTTPS paulstaab/nixos-config refs/heads/main under
a lock; it never receives connections from Actions. No runner is installed on
xenon. Even a user-writable parent or symlink must be rejected. Provision checkout
and root-owned helper through an approved administrative step, not a PR script.

Use a read-only single-repository deploy key or fine-grained read-only contents
credential provisioned out of band, root-readable systemd credentials, never
Nix strings/store files, logs or Git. Git credentials grant no workstation access.
Validate remote URL, repository identity/ID, expected branch, exact fetched SHA,
and policy against the last deployed SHA; require reviewed ancestry and reject
history rewrites until owner intervention. main protection is part of the trusted
control plane; optionally an independently provisioned signed-commit allowlist
can reduce account-compromise risk. Review key rotation/revocation before rollout.

Fetch into root-protected state, evaluate/check/build exact SHA with lock updates
disabled and sandboxed builds; preferably separate unprivileged evaluator/builder
from a minimal root activation helper with a read-only handoff. Nix evaluation is
code execution; protect token files from builder identity. Compare release/state
versions and sensitive config/closure against deployed state; until a separately
approved broader policy exists, boot/encryption/network/privilege changes require
manual intervention. Record commit, old/new store paths, check results, timestamps
and status atomically without credentials. Pin known-good and candidate closures
before activation, confirm prior generation exists, and keep every generation.

Remember failed SHAs across restart and polling; record failure stage, stop
retrying that SHA, and alert locally without automatic outbound messaging. Retry
transient fetch errors with bounded backoff; owner can explicitly clear a failed
SHA after diagnosis. On approved deployment, dry-activate then temporary test,
health checks and only then persist switch. Any failure preserves prior generation
and marks the commit failed; recovery/rollback must use a prevalidated root-owned
path. A systemd service restart or loss of network midway must not lose the prior
status. Use a transaction journal and reconcile interrupted activation on startup.
Do not claim health checks provide atomic rollback: activation may partially
modify services/user files and rollback itself may fail. Retain TTY/manual recovery.
Never reboot or GC automatically. New kernel behavior stays pending until an
owner-approved reboot. An operational kill switch must stop polling and permit
local rollback independently of GitHub. Git rollback needs a reviewed revert PR
so polling will not immediately reinstall the failed desired state.

No root service, timer, checkout, credential, activation helper or changed sudo
permission is implemented here. Enabling any of them needs separate approval and
an explicit replacement of the current per-activation owner approval policy.

## Failure and trust boundaries

- Compromised GitHub owner/admin: can alter main/protection/workflows; this can
  ultimately become root code with deployment enabled. MFA/hardware keys,
  independent reviewers, limited Apps, audited changes and an independent host
  authorization/signing gate reduce risk; branch protection alone cannot stop
  an administrator who can disable it. Stop polling/revoke credentials on suspicion.
- Malicious upstream update: NAR hashes establish content identity, not safety.
  CI may pass. Maintain release provenance, source review, narrow inputs, sandboxed
  builders and staged host health testing. Lock-only does not mean low privilege.
- CI outage/failure/resource exhaustion: block merge, retain deployed system;
  no emergency bypass, absent checks never count as success.
- Network/GitHub/cache outage: keep current host; retry retrieval later without
  activation or repeated known-failed deploy attempts. No forced source upgrade.
- Failed/partial activation: retain journal and generations, stop that commit,
  restore known-good where possible with explicit recovery authority. No reboot;
  local recovery remains necessary if networking/login breaks.
- Compromised cache/action: CI tools and fetched sources are supply-chain trust
  roots. Pin actions, trust only approved signed binary caches, never give CI a
  host credential or cache signing key. Do not make the host trust a PR-writeable
  cache. Successful CI is evidence, not an authorization to run arbitrary root code.

## Capacity, costs and rollout

Use GitHub-hosted ubuntu-24.04, not a self-hosted xenon runner. Standard private
Linux runners currently offer 2 CPU, 8 GB RAM and 14 GB SSD; a full GNOME closure
and two generations can exceed disk/time limits. This has not been measured
remotely. The workflow has a 120-minute cap; failures must remain blocking.
Use cache.nixos.org signed substitutes by default, no external cache account is
required. Explicit old pins/cache misses and unfree VS Code may require downloads
or local compilation. If capacity fails, use a larger ephemeral hosted Linux
runner with budget approval; do not silently omit the complete system build.
A later trusted cache can improve speed, with writes restricted to trusted main
and no signing secret in PR builds.

At 30–60 minutes per daily CI run, budget roughly 900–1800 Linux minutes/month
plus interactive PRs, reruns, main builds, and small update jobs. No-op update days
avoid CI. At the documented standard Linux rate of $0.006/minute, gross compute
is about $5.40–$10.80 before included credit; larger runners/storage differ.
This is a planning estimate, not observed runtime or a verified account quota.
Check the account plan, spending limit and invoices. Private branch protection
requires a qualifying paid plan (e.g. Pro for a personal repository). Copilot
review availability and additional consumption depend on license and settings.

References checked during preparation:
[runner specifications](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax),
[billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions),
[protection availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches),
[Actions permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository),
[Copilot review configuration](https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review).

Rollout order: review this local commit; approve publication separately; configure
and verify protection/permissions/budget; trial successful and deliberately failing
PRs; approve daily PR activation; resolve trusted eligibility/review
enforcement; trial auto-merge before separately approving it; implement and audit
host agent with rollback drills; separately approve temporary activation and runtime
tests before any persistent deployment/timer enablement. No step is implied by the
previous one.

## Local validation record

Preparation passed actionlint, ShellCheck for both new Bash scripts, Bash syntax,
Nix parse/format checks with the documented hardware-file exception, Python compile
and adversarial lock/downgrade fixtures. Full scripts/gitops-ci ran against 408e186:
base and candidate flake checks and complete system builds passed. Both builds
resolve to the generation-8 closure recorded above. Closure, sensitive configuration
and generated service-unit diffs are empty; no comparable downgrades were found.
Diagnostics remain in /tmp/xenon-gitops-validation-full (not committed).
Nix emitted a future JSON-format deprecation warning for path-info; the current
output is handled and this is not a validation failure. Pin/test a future CLI
format migration before the warning becomes an error.

No lock refresh, remote job, PR publication, merge, activation, timer enablement,
credential provisioning, reboot, GC, generation deletion or push was performed.
Workflow execution on GitHub, private-repository token behavior, runner capacity,
and actual upstream PR publication remain untested until approved publication.

### Release-ref follow-up validation

The minimal system-update policy change replaces nixpkgs' explicit source revision
with nixos-26.05 in flake.nix and matching original metadata in flake.lock. Every
locked revision/hash/timestamp and the complete Codex node are unchanged from
a90ef84. No lock update command was run during this migration. Daily PR preparation
now calls `nix flake update nixpkgs home-manager`; it still permits only flake.lock
changes and rejects any other lock-graph or release-ref change. The release guard
in the manual helper and administration instructions now match this policy.

Full local scripts/gitops-ci against a90ef84 passed: actionlint, ShellCheck, Bash
syntax, Nix parsing/formatting, Python policy fixtures, base/candidate flake checks
and complete system builds. The security fixtures cover either release input
advancing alone or together, forbidden release changes, Codex changes, malformed
metadata, decreasing timestamps and version downgrades. Both systems resolve to
the existing generation-8 closure; service, sensitive configuration and closure
diffs are empty. Reports: /tmp/xenon-gitops-release-ref-validation. Generation 7
remains available. No activation or runtime behavior changed; earlier runtime
checks remain pending. Remote workflows and settings remain untested/unchanged,
and daily PR creation remains gated off.
