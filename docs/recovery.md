# Rollback and recovery

For a failed SSD replaced with a blank disk, use
[Bare-metal reinstall](bare-metal-reinstall.md). The procedures below assume
the existing installation and storage still exist.

## Before activation

Record the current generation and confirm its store path still exists:

```console
readlink -f /run/current-system
find /nix/var/nix/profiles -maxdepth 1 -type l -name 'system*-link' -print
```

Do not garbage-collect the known-good generation during migration.

## Temporary activation failure

`nixos-rebuild test` does not change the default boot generation. Reboot to
return to the last booted configuration. If the desktop is unusable but a TTY is
available, run the prior generation's `switch-to-configuration switch` directly.

## Persistent activation failure

From a working shell:

```console
sudo nixos-rebuild switch --rollback
```

If boot fails, select the previous NixOS generation from the systemd-boot menu.
Never remove old generations until the replacement has passed reboot and runtime
testing.

## Installation-media recovery

Boot official NixOS installation media, identify the existing devices, unlock
the existing LUKS container, and mount the existing Btrfs and EFI layout without
formatting anything. Use `nixos-enter` or rebuild a known-good Git revision.
Device identifiers and mount commands must be re-verified at recovery time; do
not copy commands blindly. Partitioning, formatting, LUKS changes, and bootloader
reinstallation require explicit approval.

The installed layout at the initial audit was:

- EFI: UUID `D0C9-CBBD`, mounted at `/boot`.
- Root LUKS UUID: `c1ee8d4a-8b0e-4706-8f2d-bcc9add662e0`.
- Root Btrfs top-level mounted at `/`; subvolumes `home` and `nix` mounted at
  `/home` and `/nix`.
- Separate encrypted swap UUID: `313af177-0457-49cd-a58e-9bf51024b8b3`.

UUIDs are identifiers, not secrets. Never record passphrases or recovery keys.
