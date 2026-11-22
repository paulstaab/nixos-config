# Workstation administration rules

This repository is the source of truth for the NixOS workstation named `xenon`.
Agents must leave it in a state another fresh session can understand and verify.

## Agent-first administration policy

Codex may autonomously inspect and edit configuration files, run non-privileged
validation and builds, and create local Git commits. Prefer declarative, minimal,
reversible changes. Validate and commit configuration changes before requesting
activation.

Never commit directly on `main`. Before making changes, create or switch to a
feature branch. Publish changes through a GitHub pull request targeting `main`;
never push directly to `main` or bypass branch protection. A request to publish
changes or create a PR authorizes pushing the relevant feature branch and
opening its PR; otherwise obtain approval before pushing. Do not merge a PR
without explicit owner approval.

Explicit user approval is required before:

- Activating a system configuration with `nixos-rebuild test` or `switch`.
- Running privileged commands that modify system state.
- Rebooting or shutting down the workstation.
- Updating firmware.
- Changing disks, partitions, filesystems, encryption, boot configuration, or
  sudo permissions.
- Deleting system generations or performing destructive garbage collection.
- Pushing changes to a remote repository.

Do not configure passwordless sudo or any alternative privilege-escalation
mechanism.

## Safety boundaries

- Prefer declarative, minimal, reviewable, reversible changes.
- Never access, display, copy, or commit credentials, passwords, private keys,
  tokens, recovery keys, or other secrets.
- Do not change partitioning, filesystems, Btrfs subvolumes, LUKS, swap,
  hibernation, the bootloader, EFI settings, or recovery behavior without the
  owner's explicit approval for that specific change.
- Preserve `system.stateVersion` and `home.stateVersion`; do not raise them during
  routine upgrades.
- Never run destructive commands without explicit approval.
- Never activate a configuration unless evaluation and a complete system build
  have succeeded. Activation includes `nixos-rebuild test`, `switch`, and `boot`.
- A successful build is not evidence that runtime hardware or desktop behavior
  works. Test affected behavior after an approved temporary activation.
- Keep changes small and make logical Git commits. Do not mix a release upgrade,
  storage change, or hibernation repair with unrelated administration.

## Required workflow

1. Read this file, `README.md`, and the relevant files under `docs/`.
2. Inspect the worktree, preserve unrelated user changes, and create or switch
   to a feature branch before editing; never commit directly on `main`.
3. Make the smallest declarative change that fulfills the request.
4. For configuration changes, run parse/evaluation checks, `nix flake check path:$PWD`,
   and build `path:$PWD#nixosConfigurations.xenon.config.system.build.toplevel`.
5. Review the activation diff and state what still requires runtime testing.
6. Confirm that a known-good system generation remains available.
7. Stop before activation unless the owner explicitly approved activation.
8. Document material operational decisions and recovery implications.
9. Commit on the feature branch and submit a GitHub PR targeting `main`, obtaining
   publication approval first unless already authorized. Keep `main` aligned
   with the merged remote history.

## Protected configuration

`hosts/xenon/hardware-configuration.nix` contains the installed storage and LUKS
layout. Treat it as protected even though it is tracked. The current encrypted
swap is active, but resume-from-hibernation was not configured in the running
kernel during the initial audit. Do not attempt to repair it incidentally.

Home Manager activation can replace user files or expose ownership conflicts.
Before adding a managed file, inspect only its path, type, ownership, and whether
it exists; do not read potentially secret contents unless explicitly necessary
and authorized. Prefer an explicit migration or backup plan over forced writes.

## Routine updates

Follow [docs/updates.md](docs/updates.md). The owner-authorized standing policy
is daily local input updates and `nixos-rebuild boot`, no automatic reboot,
weekly native GC with a 30-day threshold, and 20 systemd-boot entries. This is an
explicit exception to per-run boot activation and generation deletion approval
for these configured services only. Initial activation still requires approval.
Do not run the services or GC during implementation/validation.

flake.lock is local and ignored. Always use an explicit absolute `path:` flake
for checks/builds/rebuilds so the ignored lock is included. Preserve nixos-26.05,
release-26.05, the separate Codex revision pin, and state versions. Daily updates
do not commit or push. Keep the root-owned permanent checkout at
/var/lib/nixos-config; do not point the service at a transient worktree. Review
and publish source changes through main before deployment: the updater trusts
main as root code. All updates share its lock.
