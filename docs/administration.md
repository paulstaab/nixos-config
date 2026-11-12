# Administration workflow

Run commands from the repository root. No activation is implied by validation.

## Validate

```console
nix flake check
nix build .#nixosConfigurations.nixos.config.system.build.toplevel
sudo nixos-rebuild dry-activate --flake .#nixos
```

The build command creates a local `result` symlink, which is ignored by Git. A
dry activation computes and reports changes but must not replace build validation.
Review the Git diff, the flake lock change, and the dry-activation report before
requesting activation approval.

## First activation proposal

After approval, first re-run validation and then temporarily activate:

```console
nix flake check
nix build .#nixosConfigurations.nixos.config.system.build.toplevel
sudo nixos-rebuild dry-activate --flake .#nixos
sudo nixos-rebuild test --flake .#nixos
```

Test login, GNOME, Wi-Fi, audio, graphics, external displays, suspend, and any
Home Manager-managed files. Do not test hibernation as part of this migration.
If the temporary activation works, request approval before making it persistent:

```console
sudo nixos-rebuild switch --flake .#nixos
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

