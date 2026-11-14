# Agent-driven updates

Run from `~/nixos-config`. Maintenance requests authorize preparation, validation,
and a local commit, but never activation, reboot, firmware updates, deletion of
generations, or pushing. Do one mode per commit. Never run a blanket flake update.
The helper uses existing Bash, Git, jq, Nix, nixfmt, and diff; it installs nothing.

## 1. Capture the baseline

Read AGENTS.md, administration.md, and recovery.md. Start with a completely clean
worktree, including untracked files. Preserve existing work; do not stash or
reset it without agreement. Choose a fresh absolute report directory outside the
repository (its parent must exist), for example:

```console
scripts/update-workflow prepare system /tmp/xenon-system-update
# Or, for an independent Codex update:
scripts/update-workflow prepare codex /tmp/xenon-codex-update
```

Preparation evaluates and builds the old configuration, records configured
package versions and all input revisions, and checks that the running system
has a retained, existing generation. The report's system symlinks also keep the
builds reachable by Nix. Keep the report through runtime testing. No generations
may be removed. An interrupted preparation is incomplete; use a fresh directory.

## 2. Select and update only the requested inputs

### system

The release policy is **NixOS 26.05**, with Home Manager **release-26.05**.
Obtain the current `nixos-26.05` branch head from the official NixOS/nixpkgs
repository, for example with `git ls-remote https://github.com/NixOS/nixpkgs.git
refs/heads/nixos-26.05`. Record that command's output and date in the report.
Verify the selected commit belongs to that release branch. Replace only the
40-character revision in `inputs.nixpkgs.url` in flake.nix with that commit.
Keep the explicit revision pin. Leave codex-nixpkgs unchanged, keep Home Manager's
URL at release-26.05, and preserve its nixpkgs follows relationship. Then run:

```console
nix flake update nixpkgs home-manager
```

Do not substitute unstable, another release, or another Home Manager branch if
the release branch is unavailable or no longer maintained. Report that condition
and request a separate release-upgrade task. The helper checks the evaluated
release but cannot prove Git ancestry; the agent must verify provenance.

### codex

Check official `https://github.com/openai/codex/releases` for a stable upstream
release (exclude prereleases/nightlies), then find a revision of official
NixOS/nixpkgs whose `codex` derivation packages that exact version. Record the
release URL, version, selected nixpkgs revision, and evidence in the report.
Inspect the upstream nixpkgs package definition and release source/tag; a version
string alone is insufficient evidence of stability. Do not assume an arbitrary
nixpkgs branch head packages the desired release.

Replace only the revision in `inputs.codex-nixpkgs.url`, keeping an explicit
40-character pin. Then run:

```console
nix flake update codex-nixpkgs
```

Main nixpkgs and Home Manager must remain byte-for-byte unchanged in the lock.
Codex's dependencies may change in its closure; review those too. Compare the
reported Codex version with the stable release selected above. If there is no
suitable packaged stable version, stop and report the limitation rather than
introducing an overlay or changing another input.

## 3. Validate and review

Use the same mode and report directory as preparation:

```console
scripts/update-workflow validate system /tmp/xenon-system-update
# Or:
scripts/update-workflow validate codex /tmp/xenon-codex-update
```

The helper rejects changes outside flake.nix and flake.lock and changes to
unrelated lock nodes. It checks formatting and whitespace without rewriting,
runs `nix flake check`, and builds the full xenon system closure with lock updates
disabled. It records old/new input revisions, configured package versions,
kernel/initrd derivations, selected boot and encryption settings, service names,
unit-file changes, and the complete closure diff. A failed command means no
validated result; fix the cause and rerun validation. Never bypass a failed check.

Agent review is mandatory before committing:

- Read input.diff and old-lock.json/new-lock.json. Ensure flake.nix changed only
  the intended revision and lock originals match it. The helper's allowlist does
  not validate arbitrary edits within flake.nix or prove upstream provenance.
- Read config.diff, services.diff, and closure.diff. Explain kernel and initrd
  changes, bootloader packages, cryptsetup, systemd, networking, graphics, GNOME,
  PipeWire, firmware packages, Home Manager, and Codex changes where present.
  A changed initrd/kernel derivation requires review even if its version is equal.
- Compare the built systems' `kernel`, `initrd`, `kernel-params`, and `boot.json`
  paths/files where present. Review generated boot metadata and relevant unit
  definitions; do not inspect credential files. No boot, storage, encryption,
  state-version, or service configuration edits are part of routine updates.
  Unexpected semantic changes in those areas require a separate owner decision.
- Summarize release notes, security fixes when relevant, likely regressions, and
  required runtime tests. A build does not establish hardware compatibility.
- Recheck that the recorded running-system path exists and is still represented
  by a generation under /nix/var/nix/profiles. If the running system changed during
  maintenance, reconcile the baseline and repeat the review before activation.

Put a concise durable record in the Git commit body: mode, upstream provenance,
old/new revisions and key versions, validation results, boot/service findings,
known-good generation, regressions, and pending runtime checks. Reports may stay
outside Git; do not commit generated unit files or private state. Review the
staged diff and create a focused local commit:

```console
git add flake.nix flake.lock
git diff --cached --check
git diff --cached
git commit
```

No change is needed when the selected revisions are already pinned. Do not
create an empty update commit. Stop here and present the commit and review to
the owner for explicit activation approval.

## 4. Approved activation and runtime tests

Recheck the clean worktree, exact approved commit, successful checks/build, and
known-good generation before each activation. If anything changed, revalidate.
After explicit approval for temporary activation:

```console
sudo nixos-rebuild dry-activate --flake .#xenon
sudo nixos-rebuild test --flake .#xenon
```

Review dry-activation output before test. This is a privileged review step,
kept outside the helper. Test changes against the running-system baseline too
when it differs from the old repository closure. Check failed system and user
units (`systemctl --failed`, `systemctl --user --failed`), login/GNOME, Wi-Fi/DNS,
Tailscale, audio, graphics, external displays, printing if used, and suspend/resume.
Check Home Manager file ownership/conflicts without reading private contents.
For Codex, check `codex --version` and an interactive session without copying or
logging credentials. Do not test hibernation. Kernel/early-boot behavior remains
unverified until a separately approved reboot; `test` cannot load a new kernel.

After successful smoke tests, request separate approval for persistence:

```console
sudo nixos-rebuild switch --flake .#xenon
```

Record runtime results in the administration record or a follow-up documentation
commit. Request reboot approval separately if needed. Keep old generations.

## 5. Recovery and publication

For a failed temporary activation, with approval restore the recorded known-good
store path using `sudo /nix/store/<recorded-system>/bin/switch-to-configuration
test`. A separately approved reboot returns to the default boot generation.
After a failed persistent activation, with approval use
`sudo nixos-rebuild switch --rollback`, or select a known-good generation at boot.
See recovery.md. Runtime rollback does not revert Git; explicitly restore the
corresponding pins in a new reviewed commit before a future rebuild. Do not delete
generations, garbage-collect, or repair hibernation incidentally.

Once validation and available runtime tests are documented, inspect `git status`,
the destination remote, and the exact commits to publish. Request explicit push
approval, then use `git push` to the agreed remote/branch. Never force-push as part
of this workflow. Builds and local commits alone do not authorize publication.
