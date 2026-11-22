# Canonical checkout and updates

The canonical machine configuration is a standalone clone at
`/var/lib/nixos-config`, owned entirely by root and not group/other writable.
Ordinary development belongs in separate user-owned clones or worktrees. Never
edit the canonical checkout: publish reviewed changes through a PR to `main`.
The updater trusts that repository's main branch as root code.

## Manual command

```console
sudo xenon-update boot
sudo xenon-update switch
```

Choose one: `boot` prepares the next manual reboot; `switch` also activates
immediately. Neither reboots. The command requires root and an explicit mode.
It rejects unexpected ownership/permissions, a different origin, tracked changes,
untracked files, or ignored files other than flake.lock. It fetches
`https://github.com/paulstaab/nixos-config.git` main and checks out the fetched
commit detached, without merging or discarding tracked edits. The public HTTPS
remote requires no user SSH keys. A private repository would need a separately
reviewed authentication arrangement.

Manual runs preserve the local ignored flake.lock, reconciling changed input
declarations with `nix flake lock`. Consequently, main identifies source code,
not exact package versions. The command prints the fetched commit, checks the
flake, completes the system build, then runs nixos-rebuild with lock updates
forbidden. All flake operations use an absolute `path:` reference, including the
ignored lock. No commit, push, release upgrade or reboot is performed.

## Daily service and serialization

`nixos-upgrade.timer` runs daily at 04:40 Europe/Berlin, catching missed runs.
The service runs the same updater with its internal `daily` mode: fetch main,
refresh local inputs, check/build, then prepare boot only. Nixpkgs remains on
nixos-26.05, Home Manager on release-26.05, and Codex separately revision-pinned.
Manual and scheduled runs hold `/run/lock/xenon-update.lock` for the entire
operation; a competing run fails explicitly. Do not bypass this lock with
independent rebuilds or edits in the canonical checkout.

Failures before activation leave the installed generation intact, although the
checkout and local lock may have advanced. Activation/bootloader failures can
leave partially applied state and require investigation; there is no automatic
health rollback. A successful build does not establish desktop/hardware behavior.

## Initial migration (requires separate approval)

First merge the reviewed implementation into main. Stop the old update timer
and service before migrating; do not run either updater during implementation.
After approval, create a fresh root-owned clone, rather than copying a user's
Git configuration or hooks:

```console
sudo systemctl stop nixos-upgrade.timer nixos-upgrade.service
sudo git clone --origin origin --branch main https://github.com/paulstaab/nixos-config.git /var/lib/nixos-config
sudo chmod -R go-w /var/lib/nixos-config
sudo install -o root -g root -m 0644 /home/paul/nixos-config/flake.lock /var/lib/nixos-config/flake.lock
```

The last command preserves existing local package pins. The old user checkout
can remain for development; it is no longer an activation source. Validate the
new canonical tree with `nix flake check --no-update-lock-file
path:/var/lib/nixos-config` and a full `nix build --no-update-lock-file
path:/var/lib/nixos-config#nixosConfigurations.xenon.config.system.build.toplevel`.
Review the activation diff, confirm a known-good generation, then separately
approve initial activation with `nixos-rebuild switch --no-update-lock-file
--flake path:/var/lib/nixos-config#xenon`. This installs the command and replaces
the old service. The persistent timer may immediately catch up.

Verify checkout permissions, the installed command, generated service/timer,
manual boot and switch modes, contention, failure handling, journal status and
unchanged running generation after boot mode. Switching requires runtime desktop
checks; boot behavior requires a separately approved manual reboot.

## Monitoring and recovery

```console
systemctl list-timers --all nixos-upgrade.timer nix-gc.timer
systemctl status nixos-upgrade.service
journalctl -u nixos-upgrade.service --since '7 days ago'
sudo nix-env --profile /nix/var/nix/profiles/system --list-generations
readlink -f /run/current-system
readlink -f /run/booted-system
readlink -f /nix/var/nix/profiles/system
bootctl list
```

The system profile names the prepared generation; current-system names the
activated one. Booted-system identifies the booted generation. Inspect the boot
menu/default separately. Identical builds need not create a distinct generation.

For recovery, stop the timer/service with approval, select a known-good boot
entry (hold Space during boot), or use an approved `nixos-rebuild boot --rollback`
or `switch --rollback`. Inspect generations first: the previous generation may
be an untested prepared update. Fix and merge the source before resuming updates;
otherwise main will reintroduce the failure. See [recovery.md](recovery.md).

Weekly native GC retains generations younger than 30 days (up to one extra
week); systemd-boot shows at most 20 entries. Running/booted closures have GC
roots, but old profile links and menu entries are not permanently protected.
Pause GC during prolonged recovery if needed. No deletion occurs during validation.

Reinstallation uses the same root-owned path; see
[bare-metal-reinstall.md](bare-metal-reinstall.md). Git alone cannot reproduce
historical ignored locks. Personal state and secrets need separate backups.

## Implementation validation (2026-11-22)

Nix parse/format checks, flake check, and a complete xenon system build passed
using the existing local lock without refreshing inputs. Bash syntax, ShellCheck,
and offline updater fixtures passed; CI now runs these fixtures. They cover boot,
switch, daily refresh, bad arguments/ownership/remote/checkout state, fetch/check/
build failure, and shared-lock contention. Fixtures mock privileged operations;
they do not establish live activation behavior. Anonymous HTTPS access to main
was verified without a credential helper.

The generated service uses the packaged updater's internal daily mode and retains
native no-restart/no-stop-on-removal settings. Its persistent timer remains 04:40.
Kernel, initrd and kernel parameters match running generation 10. Generations 9
and 10 still resolve to available store paths. The build is rooted at
`/tmp/xenon-root-updater-system`. No configuration was activated, checkout migrated,
service started, generation removed, or change published. Live migration,
activation, contention against the real service and runtime checks remain pending.

Closure comparison also includes the already configured Codex 0.167.1 to 0.171.0
update from the existing local lock; this implementation does not change its pin.
Activation can restart derived desktop D-Bus/polkit units as the system path
changes, so verify desktop behavior after approved temporary activation.
