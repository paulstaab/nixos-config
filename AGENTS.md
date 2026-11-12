# Workstation administration rules

This repository is the source of truth for the NixOS workstation named `xenon`.
Agents must leave it in a state another fresh session can understand and verify.

## Agent-first administration policy

Codex may autonomously inspect and edit configuration files, run non-privileged
validation and builds, and create local Git commits. Prefer declarative, minimal,
reversible changes. Validate and commit configuration changes before requesting
activation.

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
2. Inspect the worktree and preserve unrelated user changes.
3. Make the smallest declarative change that fulfills the request.
4. For configuration changes, run parse/evaluation checks, `nix flake check`,
   and build `.#nixosConfigurations.xenon.config.system.build.toplevel`.
5. Review the activation diff and state what still requires runtime testing.
6. Confirm that a known-good system generation remains available.
7. Stop before activation unless the owner explicitly approved activation.
8. Document material operational decisions and recovery implications.

## Protected configuration

`hosts/xenon/hardware-configuration.nix` contains the installed storage and LUKS
layout. Treat it as protected even though it is tracked. The current encrypted
swap is active, but resume-from-hibernation was not configured in the running
kernel during the initial audit. Do not attempt to repair it incidentally.

Home Manager activation can replace user files or expose ownership conflicts.
Before adding a managed file, inspect only its path, type, ownership, and whether
it exists; do not read potentially secret contents unless explicitly necessary
and authorized. Prefer an explicit migration or backup plan over forced writes.
