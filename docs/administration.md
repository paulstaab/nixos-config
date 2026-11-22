# Administration workflow

Run commands from the repository root. No activation is implied by validation.
The host configuration enables `nix-command` and `flakes` globally through
`nix.settings.experimental-features`.

## Agent administration

Git, Codex, Nix formatting, and the baseline diagnostic tools are installed in
the system profile and are available after a fresh boot without `nix-shell`.
Start Codex from a terminal in the repository:

```console
cd ~/nixos-config  # development clone, separate from the canonical checkout
codex
```

Complete interactive authentication if Codex requests it. Authentication files
and credentials remain in the user's private state: they are not declared by
Home Manager, copied to the Nix store, or committed to this repository. Never
place tokens in Nix expressions or tracked environment files.

Codex is selected from the separately pinned `codex-nixpkgs` flake input so it
can track stable upstream releases without updating the workstation's main
package set. Updating that input changes only Codex and its runtime closure.
Existing authentication, settings, and sessions under the user's private state
remain outside Nix and survive upgrades and rollbacks.

`fwupd` is enabled for hardware inventory and firmware diagnostics. Do not run a
firmware update without explicit approval.

## Validate

```console
nix flake check "path:$PWD"
nix build "path:$PWD#nixosConfigurations.xenon.config.system.build.toplevel"
sudo nixos-rebuild dry-activate --flake "path:$PWD#xenon"
```

The build command creates a local `result` symlink, which is ignored by Git. A
dry activation computes and reports changes but must not replace build validation.
Review the Git diff, the flake lock change, and the dry-activation report before
requesting activation approval.

## First activation proposal

After approval, first re-run validation and then temporarily activate:

```console
nix flake check "path:$PWD"
nix build "path:$PWD#nixosConfigurations.xenon.config.system.build.toplevel"
sudo nixos-rebuild dry-activate --flake "path:$PWD#xenon"
sudo nixos-rebuild test --flake "path:$PWD#xenon"
```

Test login, GNOME, Wi-Fi, audio, graphics, external displays, suspend, and any
Home Manager-managed files. Do not test hibernation as part of this migration.
If the temporary activation works, request approval before making it persistent:

```console
sudo nixos-rebuild switch --flake "path:$PWD#xenon"
```

Reboot testing is a separate step. A successful build does not prove runtime
functionality.

## Updating inputs

Follow [updates.md](updates.md) for the root-owned canonical checkout and manual/daily updater. Always
use explicit path flakes to include the ignored local lock. Initial activation
and manual privileged operations require approval. Automatic updates neither
commit nor push and never reboot.

## Current sandbox limitations

The initial assessment environment could not access system D-Bus, NetworkManager
runtime state, privileged Btrfs subvolume enumeration, systemd-boot files on the
ESP, or EFI boot entries. Those denials were assessment sandbox restrictions,
not diagnosed workstation failures. Privileged read-only checks should be run on
the host before the first activation where they are relevant.

## Codex update (2026-11-22)

Updated the separate Codex Nixpkgs pin from
`3730a4017d0f44c3a09faa593269bcbddae1fa18` to
`93a9ed0a866099a230ed5146a5bb7d16fd5c9b14`, selecting stable Codex
0.171.0 instead of 0.167.1. Only this input changed in the ignored local lock;
main Nixpkgs, Home Manager and state versions are unchanged.

Nix parsing, formatting, flake check and the complete xenon build passed with
`path:/home/paul/nixos-config`. The built binary reports `codex-cli 0.171.0`.
Closure comparison against running generation 10 shows only the Codex update.
Kernel, initrd and kernel parameters are identical. Generated service differences
are system-path references and derived D-Bus/polkit restart triggers; temporary
activation may restart those desktop services. Generation 10 still resolves to
an existing store path and remains available for recovery.

The validated build is rooted at `/tmp/xenon-codex-system`. Activation has not
been performed. After owner-approved temporary activation, start a fresh Codex
session and verify normal interactive use, plus desktop/D-Bus behavior if
services restart. Existing private Codex state is not managed by this change.
Use the previous generation for rollback if needed, following recovery.md.
