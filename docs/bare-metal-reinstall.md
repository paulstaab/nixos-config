# xenon: blank-SSD reinstall

Scope: Dell XPS 15 9530, x86_64 UEFI, NixOS 26.05. Rebuild the OS and start
with fresh user settings. Documents are recovered separately from Nextcloud or
paperless-ngx; their availability and server backups are outside this procedure.
Restic, Snapper, and full user-state recovery are deferred. Local SSH keys,
browser sessions, Codex sessions, and application settings will be lost.

This is a future installation procedure, not authorization to execute it.
Partitioning, formatting, encryption changes, installation/bootloader writes,
and reboot require explicit owner approval. Never use the destructive steps on
an existing installation. No Codex installation or authentication is needed.

## 1. Independently accessible prerequisites

- This runbook and the repository URL, available on another device or paper.
  A local-only commit on the failed SSD is unavailable during recovery; arrange
  an approved push or independent copy before relying on it.
- Official NixOS 26.05 graphical installer USB, verified against official
  download information, and ability to boot it in UEFI mode.
- Working Internet: Wi-Fi password or a tested wired/tethered fallback.
- GitHub account password/password-manager access, email recovery, and an
  independent MFA method or recovery codes. None may depend solely on xenon.
- Nextcloud/paperless-ngx URLs, credentials, and MFA recovery, independently
  accessible. Confirm they are hosted independently of this SSD.
- A way to retain new disk passphrases and account passwords off the SSD.

## 2. Retrieve the private repository without the old SSH key

In the live desktop, connect to the network and sign in at github.com. If
necessary, reset the account password using independently accessible email and
use an MFA recovery code/other enrolled recovery method. GitHub recovery is not
guaranteed when all enrolled methods are lost; do not rely on support bypassing
MFA. See [GitHub account recovery](https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa/recovering-your-account-if-you-lose-your-2fa-credentials).

Create a short-lived fine-grained personal access token restricted to
`paulstaab/nixos-config`, with repository Contents read access. Open a terminal:

```sh
git -c credential.helper= clone https://github.com/paulstaab/nixos-config.git /tmp/nixos-config
```

Enter the GitHub username and enter the token at the hidden password prompt.
The GitHub account password does not authenticate HTTPS Git. Never embed the
token in a URL, command, file, Nix expression, or Git configuration. If Git is
missing, obtain it with `nix-shell -p git` and retry within that shell. See
[GitHub HTTPS authentication](https://docs.github.com/en/get-started/git-basics/about-remote-repositories).

Review the retrieved revision with `git -C /tmp/nixos-config log -1`. Keep its
`flake.lock`; do not update inputs during recovery. Revoke the temporary token
after retrieval succeeds; this flake's inputs are public.

## 3. Identify the replacement and create its layout (manual approval gate)

Boot in UEFI mode; `test -d /sys/firmware/efi` must succeed. Inspect:

```sh
lsblk -o NAME,MODEL,SERIAL,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

Disconnect unrelated storage. Manually identify the blank replacement by model,
serial, and capacity; do not assume it is `/dev/nvme0n1`. With the owner's
approval, use the installer's partition editor to create GPT and this layout.
Do not launch an automatic OS installation that substitutes a different layout.

| Partition | Size | GPT type | Contents | Installed use |
| --- | --- | --- | --- | --- |
| 1 | 1 GiB | EFI System Partition (ESP) | FAT32 | `/boot` |
| 2 | Remaining space after ESP and swap | Linux filesystem | LUKS2 containing Btrfs | `/`, `/home`, `/nix` |
| 3 | Approximately 34.1 GiB | Linux filesystem | LUKS2 containing swap | swap |

Verified on 2026-11-12 against tracked configuration and `lsblk`: original
partition sizes were 1,073,741,824; 986,498,437,120; and 36,635,230,208 bytes
on a 1,024,209,543,168-byte SSD. Sizes are observations, not Nix declarations;
approve rounding/alignment in the editor. A different-size SSD changes partition
2's size. Both encrypted partitions had Linux filesystem GPT type; swap is not
an unencrypted swap partition.

Record and verify the three actual partition paths. In the following shell,
assign `ESP_PART`, `ROOT_PART`, and `SWAP_PART` to those paths manually; no
device-path defaults are supplied. Verify each with `lsblk` before continuing.

## 4. Format, unlock, and mount (replacement disk only)

The following commands destroy the contents of the selected partitions. Run
one block at a time only after the preceding manual checks and owner approval.
Choose and independently retain strong passphrases interactively. Existing
cipher/PBKDF parameters were not audited; these commands intentionally use the
live installer's LUKS2 defaults, not a claim to reproduce the old parameters.

```sh
sudo cryptsetup luksFormat --type luks2 "${ROOT_PART:?Set ROOT_PART}"
sudo cryptsetup luksFormat --type luks2 "${SWAP_PART:?Set SWAP_PART}"
ROOT_UUID=$(sudo cryptsetup luksUUID "$ROOT_PART")
SWAP_UUID=$(sudo cryptsetup luksUUID "$SWAP_PART")
sudo cryptsetup open "$ROOT_PART" "luks-$ROOT_UUID"
sudo cryptsetup open "$SWAP_PART" "luks-$SWAP_UUID"
sudo mkfs.fat -F 32 "${ESP_PART:?Set ESP_PART}"
sudo mkfs.btrfs "/dev/mapper/luks-$ROOT_UUID"
sudo mkswap "/dev/mapper/luks-$SWAP_UUID"
```

Mount the Btrfs top-level as root, not a new `@` subvolume:

```sh
sudo mount -o subvolid=5 "/dev/mapper/luks-$ROOT_UUID" /mnt
sudo btrfs subvolume create /mnt/home
sudo btrfs subvolume create /mnt/nix
sudo mount -o subvol=home "/dev/mapper/luks-$ROOT_UUID" /mnt/home
sudo mount -o subvol=nix "/dev/mapper/luks-$ROOT_UUID" /mnt/nix
sudo mkdir -p /mnt/boot
sudo mount "$ESP_PART" /mnt/boot
sudo swapon "/dev/mapper/luks-$SWAP_UUID"
sudo blkid "$ESP_PART"
findmnt -R /mnt
swapon --show
```

Only `home` and `nix` are declared subvolume mounts. Do not add a `tmp`
subvolume based on the previous audit's sandbox mount view. No snapshots or
resume configuration are required. This restores encrypted swap, not hibernation.

## 5. Update the replacement's configuration and validate

Copy the clone onto the mounted replacement:

```sh
sudo mkdir -p /mnt/home/paul
sudo cp -a /tmp/nixos-config /mnt/home/paul/nixos-config
cd /mnt/home/paul/nixos-config
```

Edit the copied files with an editor using `sudo`. UUIDs are public identifiers;
obtain the new values above, never infer them from partition numbers.

| Old identifier | Replace with | All references to update |
| --- | --- | --- |
| `c1ee8d4a-8b0e-4706-8f2d-bcc9add662e0` | `$ROOT_UUID` | `hardware-configuration.nix`: mapper paths for `/`, `/home`, `/nix`; root `boot.initrd.luks.devices` attribute name and its by-UUID device |
| `313af177-0457-49cd-a58e-9bf51024b8b3` | `$SWAP_UUID` | `configuration.nix`: swap LUKS attribute name and by-UUID device; `hardware-configuration.nix`: `swapDevices` mapper path |
| `D0C9-CBBD` | New ESP FAT UUID from `blkid` | `hardware-configuration.nix`: `/boot` device |

Both files are under `hosts/xenon/`. Preserve the `luks-` prefix in attribute
names and mapper paths. The Btrfs UUID, inner swap UUID, partition GUIDs, and
subvolume numeric IDs are not referenced in the current configuration.

Keep `system.stateVersion = "26.05"` and `home.stateVersion = "26.05"`.
Keep systemd-boot and EFI-variable support as declared. Do not overwrite the
tracked hardware file with generated configuration. If hardware beyond the SSD
changed, stop and manually review required drivers/platform settings.

From the copied repository, enable flakes in this live shell and validate:

```sh
export NIX_CONFIG='experimental-features = nix-command flakes'
git diff --check
git diff
rg 'c1ee8d4a-8b0e-4706-8f2d-bcc9add662e0|313af177-0457-49cd-a58e-9bf51024b8b3|D0C9-CBBD' hosts/xenon
nix flake check
nix build .#nixosConfigurations.xenon.config.system.build.toplevel
```

The `rg` check must find no old identifiers (exit status 1 means no matches).
Compare all new identifiers with `cryptsetup luksUUID`, `blkid`, and the mount
output. Proceed only after checks and the complete build succeed. Do not change
the lock file to work around a failure without reviewing the cause.

## 6. Install, set passwords, and boot

After reviewing the diff and obtaining installation/bootloader-write approval:

```sh
sudo nixos-install --root /mnt --flake /mnt/home/paul/nixos-config#xenon
sudo nixos-enter --root /mnt -c 'passwd paul'
sudo nixos-enter --root /mnt -c 'chown -R paul:users /home/paul/nixos-config'
sudo nixos-enter --root /mnt -c 'chown paul:users /home/paul'
```

Set the root password at the installer's prompt and Paul's password with
`passwd`; no account password is declared. Enter secrets only at hidden prompts.
Confirm installation completed successfully. With reboot approval, reboot and
remove the USB. Unlock encrypted root and swap as prompted; the number/order of
prompts is not verified. A failure here requires installer-based diagnosis, not
disabling encryption. See the [NixOS installation manual](https://nixos.org/manual/nixos/stable/).

## 7. Verify and finish

Log in as Paul. Check:

```sh
hostname
nixos-version
findmnt -t btrfs,vfat
swapon --show
systemctl --failed
systemctl status home-manager-paul.service --no-pager
sudo bootctl status
```

Expect hostname `xenon`, NixOS 26.05, the intended mounts and encrypted swap,
successful Home Manager activation, and systemd-boot on the replacement ESP.
Test GNOME login, networking, audio, graphics, external displays, and suspend.
Do not test hibernation as part of recovery. No old generations survive SSD loss;
retain the installer USB as the initial recovery route.

Reauthenticate to Nextcloud/paperless-ngx and verify documents are accessible.
Reauthenticate Codex if desired. Configure Git identity and create/register a
new SSH key only if needed; HTTPS access remains sufficient. Review old GitHub
SSH-key authorization and revoke the lost key where appropriate. Review and
commit the replacement UUID changes locally after verification; pushing needs
separate approval.

Manual decisions remain: target-disk identification and partition-editor
operations, credential/MFA recovery, passphrase selection, UUID editing,
hardware changes, boot failures, and runtime acceptance. This procedure has not
been tested end to end on a blank disk or VM; validate it in an isolated VM
before treating it as a proven recovery path.
