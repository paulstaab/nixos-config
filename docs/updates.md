# Local automatic updates

The native `nixos-upgrade.service` runs daily at 04:40 Europe/Berlin. Its
persistent timer catches missed runs after power-on. ExecStartPre first runs
`nix flake update --flake path:/home/paul/nixos-config`; failure stops the service
before the build. Then native nixos-rebuild runs `boot --no-update-lock-file`.
It builds and registers the next boot generation without switching the running
system. It never reboots. Timer and manual starts of this same service serialize;
do not run independent rebuild/update commands concurrently.

Nixpkgs stays on nixos-26.05 and Home Manager on release-26.05. Release upgrades
require editing flake.nix. Codex remains explicitly pinned and does not advance
with daily updates. No Git fetch, commit, push, PR or remote automation is used.
A failed download/build leaves the installed generation intact; an updated lock
may remain after failure. The next daily run retries. Bootloader installation
errors can leave partially updated boot files and require local investigation.

## Checkout and local lock

The permanent checkout must be `/home/paul/nixos-config`, not a temporary agent
worktree. Publish/copy the reviewed configuration there before enabling it. Root
must be able to access it, including after unattended boot. This is a trusted,
user-editable root configuration: edits there may become booted root code without
another review. Keep the checkout free of secrets, generated reports and unrelated
files: path flakes copy the directory to the store, including ignored files.

flake.lock exists locally but is ignored by Git. Always use explicit `path:`
flakes: a Git flake omits the ignored lock and may silently resolve other inputs.
For interactive validation:

```console
cd /home/paul/nixos-config
nix flake lock path:/home/paul/nixos-config
nix flake check --no-update-lock-file path:/home/paul/nixos-config
nix build --no-update-lock-file path:/home/paul/nixos-config#nixosConfigurations.xenon.config.system.build.toplevel
```

There is no exact package-version recovery from Git. CI resolves a fresh lock
for each unpinned source tree, so results can change as release branches advance.
Never use the old Git-only maintenance workflow for this configuration.

## Operation and monitoring

After the separately approved initial activation, use:

```console
systemctl list-timers --all nixos-upgrade.timer nix-gc.timer
systemctl status nixos-upgrade.timer nixos-upgrade.service
systemctl show nixos-upgrade.service -p Result -p ExecMainStatus -p ExecMainStartTimestamp -p ExecMainExitTimestamp
journalctl -u nixos-upgrade.service --since '7 days ago'
sudo systemctl start nixos-upgrade.service
sudo nix-env --profile /nix/var/nix/profiles/system --list-generations
readlink -f /run/current-system
readlink -f /run/booted-system
readlink -f /nix/var/nix/profiles/system
bootctl status
bootctl list
```

The system profile names the prepared generation; `/run/current-system` names
the activated one. `/run/booted-system` identifies the booted generation.
Check bootctl for the actual default entry, including any manual overrides.
Repeated identical builds need not create a distinct generation. Logs expose
failure details; no external monitoring or custom retry loop is installed.

## Rollback and retention

Hold Space during boot to open systemd-boot, then choose an older NixOS entry.
Selecting one entry boots it once; it does not necessarily reset the default.
From a working system, with approval for the privileged change:

```console
sudo systemctl stop nixos-upgrade.timer nixos-upgrade.service
sudo nixos-rebuild boot --rollback
```

This changes the next boot default without switching the running system. If an
immediate rollback is required, use `sudo nixos-rebuild switch --rollback`
instead, after reviewing which profile generation will be selected. A prepared
but unbooted generation means “previous” need not mean the last known-good one;
inspect the generation list first. Reboot only manually. Keep the timer stopped
while diagnosing; it would otherwise prepare the faulty update again. Correct
the inputs/configuration before restarting it with `sudo systemctl start
nixos-upgrade.timer`. See [recovery.md](recovery.md).

Native weekly GC uses `--delete-older-than 30d`. This approximates 30 days (up to
one extra week), retains current profile generations, and removes unreachable
store paths. Running/booted system GC roots protect their store closures, but do
not guarantee their old profile links or boot-menu entries survive indefinitely.
Only the newest 20 generations appear in systemd-boot; profile generations and
store paths are distinct from menu entries. Twenty daily changed generations
may cover less than 30 days. GC does not immediately rewrite the boot menu;
the next boot installation reconciles it. Pause `nix-gc.timer` during prolonged
recovery if an old known-good generation must be retained. No GC or deletion is
performed during implementation.

## Reinstall and limitations

Clone the repository to `/home/paul/nixos-config`, review hardware UUIDs/mounts
for the new installation, then generate a fresh local lock with `nix flake update
--flake path:/home/paul/nixos-config`. Follow [bare-metal-reinstall.md](bare-metal-reinstall.md)
for mounting, validation and explicitly approved installation. Use the mounted
absolute path with `path:` before entering the installed system. Git restores
system/user/Home Manager configuration, packages, services and these timers;
personal files, application state and secrets require separate backups.

Successful builds do not establish boot, graphics, networking, audio, suspend or
Home Manager compatibility. Runtime verification requires approved activation
and a manual reboot. Unattended updates trade pre-activation review for convenient
next-boot updates. Offline periods, unavailable upstream branches, disk/ESP
exhaustion and build failures delay updates. There is no automatic release bump,
health rollback, firmware update or hibernation repair.

## Implementation validation (2026-11-22)

Validated against the existing local lock without refreshing inputs: Nix parsing
and formatting, flake check, complete xenon build, actionlint, ShellCheck, Bash
syntax and offline policy/downgrade fixtures passed. Full scripts/gitops-ci
against 946b985 also passed both base/candidate checks and builds; no comparable
downgrades were found. Reports are in `/tmp/xenon-local-updates-ci` (temporary,
not required for recovery). Corrected service-report comparison to follow the
top-level systemd directory symlinks; its resulting unit diff was reviewed.

Inspected the generated pre-start/start scripts and timer units: input refresh
precedes boot-only rebuild, scripts use `set -e`, the build forbids lock changes,
and no reboot command exists. The path-flake store snapshot contains a byte-equal
copy of the ignored local lock. Evaluated retention is 30d, weekly persistent GC,
20 systemd-boot entries and daily persistent updates at 04:40. Calendar expressions
were checked with systemd-analyze.

Compared with the running generation 8: kernel, initrd and kernel parameters are
unchanged; no storage, encryption, state-version or unrelated service setting
changed. The closure adds git-minimal and updater/timer infrastructure. Retained
generations 7 and 8 still resolve to existing store paths. No generation was
removed. Native build output is rooted at `/tmp/xenon-local-updates-system`.

Pending: transfer the reviewed commit into the permanent checkout, separately
approve initial activation (which enables both persistent timers and can trigger
catch-up runs), then verify actual update success/failure status, boot-profile
registration and unchanged running system. Boot selection and desktop/hardware
behavior require a separately approved manual reboot. Failure propagation is
verified from generated units, not an injected failure on the live host. Remote
CI/publication and cleanup execution have not been tested or performed.
