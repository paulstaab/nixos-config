# Administration workflow

Run commands from the repository root. No activation is implied by validation.
The host configuration enables `nix-command` and `flakes` globally through
`nix.settings.experimental-features`.

## Agent administration

Git, Codex, Nix formatting, and the baseline diagnostic tools are installed in
the system profile and are available after a fresh boot without `nix-shell`.
Start Codex from a terminal in the repository:

```console
cd ~/nixos-config
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

Follow [updates.md](updates.md) for the local daily boot-only updater. Always
use explicit path flakes to include the ignored local lock. Initial activation
and manual privileged operations require approval. Automatic updates neither
commit nor push and never reboot.

## Current sandbox limitations

The initial assessment environment could not access system D-Bus, NetworkManager
runtime state, privileged Btrfs subvolume enumeration, systemd-boot files on the
ESP, or EFI boot entries. Those denials were assessment sandbox restrictions,
not diagnosed workstation failures. Privileged read-only checks should be run on
the host before the first activation where they are relevant.
