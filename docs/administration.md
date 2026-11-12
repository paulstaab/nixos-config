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

`fwupd` is enabled for hardware inventory and firmware diagnostics. Do not run a
firmware update without explicit approval.

## Validate

```console
nix flake check
nix build .#nixosConfigurations.xenon.config.system.build.toplevel
sudo nixos-rebuild dry-activate --flake .#xenon
```

The build command creates a local `result` symlink, which is ignored by Git. A
dry activation computes and reports changes but must not replace build validation.
Review the Git diff, the flake lock change, and the dry-activation report before
requesting activation approval.

## First activation proposal

After approval, first re-run validation and then temporarily activate:

```console
nix flake check
nix build .#nixosConfigurations.xenon.config.system.build.toplevel
sudo nixos-rebuild dry-activate --flake .#xenon
sudo nixos-rebuild test --flake .#xenon
```

Test login, GNOME, Wi-Fi, audio, graphics, external displays, suspend, and any
Home Manager-managed files. Do not test hibernation as part of this migration.
If the temporary activation works, request approval before making it persistent:

```console
sudo nixos-rebuild switch --flake .#xenon
```

Reboot testing is a separate step. A successful build does not prove runtime
functionality.

## Updating inputs

Input updates can change the entire system and require their own review and
build. Update one input deliberately; do not use an unreviewed blanket update.
Keep Home Manager on the release matching NixOS and following the same nixpkgs.

## Current sandbox limitations

The initial assessment environment could not access system D-Bus, NetworkManager
runtime state, privileged Btrfs subvolume enumeration, systemd-boot files on the
ESP, or EFI boot entries. Those denials were assessment sandbox restrictions,
not diagnosed workstation failures. Privileged read-only checks should be run on
the host before the first activation where they are relevant.
