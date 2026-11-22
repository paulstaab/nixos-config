# Laptop requirements

This document describes the high-level requirements for Paul's Dell XPS 15
9530, named `xenon`. It captures the agreed baseline from the repository's
configuration and operational documentation. Requirements describe intended
behavior; they do not imply that runtime acceptance testing has passed.
Implementation details and procedures belong in the linked runbooks.

## Desktop and everyday use

- Provide a GNOME desktop for Paul's normal, non-root user account.
- Support reliable login, Wi-Fi, audio, graphics, external displays, printing,
  and suspend on the laptop.
- Use an English interface and US keyboard, with German regional conventions
  and the Europe/Berlin time zone.

## Applications

- Provide Chromium as the default browser for web links and HTML files, with
  Firefox available as an alternative.
- Make the official Bitwarden browser extension available in Chromium for
  password management.
- Provide the official Microsoft Visual Studio Code build with access to its
  normal extension marketplace.
- Provide Nextcloud Desktop for owner-configured file synchronization. Account
  setup, folder selection, synchronization, and login autostart must remain
  deliberate owner choices.
- Provide Codex, Git, and baseline command-line tools for development,
  diagnostics, and workstation administration.
- Preserve private application settings, sessions, and authentication across
  routine system updates without placing them under configuration management.

## Security and privacy

- Protect system and user data at rest with encrypted storage, including swap.
- Keep credentials, vaults, private keys, tokens, and recovery secrets outside
  the repository and Nix store.
- Use a normal user account for everyday work and authenticated privilege
  escalation for administration; do not enable passwordless sudo or another
  privilege-escalation shortcut.
- Keep application authentication and account enrollment under owner control.
- Require explicit owner approval for sensitive system changes as defined in
  [AGENTS.md](../AGENTS.md), including storage, encryption, firmware, and boot
  changes outside the approved routine-update policy.

## Connectivity

- Support everyday network management through the desktop.
- Provide Tailscale for private network access after owner-controlled enrollment.
- Do not enable subnet routing, exit-node operation, Tailscale SSH, or published
  services without a separate decision.

## Configuration and administration

- Keep this repository as the source of truth for system configuration and
  managed user applications, using NixOS and Home Manager.
- Keep the canonical machine checkout at `/var/lib/nixos-config`, owned by
  root and not writable by ordinary users. Use separate user-owned clones or
  worktrees for development.
- Deploy reviewed configuration from the repository's `main` branch; reject an
  unexpected repository, unsafe checkout permissions, or local changes rather
  than silently overwriting them.
- Prefer small, declarative, reviewable, reversible changes that a fresh agent
  session can understand and validate.
- Validate configuration changes with evaluation, flake checks, and a complete
  system build before activation; verify affected hardware and desktop behavior
  after approved activation.
- Use feature branches and pull requests targeting `main`; publication and
  merging require the owner's authorization under the repository policy.
- Protect existing user files when introducing managed files through an explicit
  migration or backup plan.

## Updates and maintenance

- Provide `sudo xenon-update boot` to prepare the next boot generation and
  `sudo xenon-update switch` to activate immediately and persist the generation.
  Require an explicit mode; neither mode reboots the machine.
- Fetch the current `main` commit from the expected repository and validate and
  completely build its configuration before changing the system generation.
  Report the source commit and resulting system generation.
- Prepare local system updates daily from the same canonical checkout for the
  next manual reboot, without switching the running system or rebooting
  automatically.
- Serialize manual and scheduled updates across repository synchronization,
  input resolution, validation, building, and activation.
- Keep exact input revisions in a machine-local, Git-ignored lock file. Manual
  updates preserve existing pins, reconciling changed input declarations only;
  daily updates refresh inputs. Git history alone does not reproduce package
  versions. Use absolute path flakes so operations include the local lock.
- Stay on the selected NixOS and Home Manager release branches until a deliberate
  release upgrade; update Codex through its separate revision pin.
- Fetch source updates without depending on a user's credentials. Do not
  automatically create Git commits, pushes, or PRs during routine updates.
- Require separately approved initial migration and activation of the updater;
  the standing daily-update policy applies after that activation.
- Provide inspectable update status and failure logs, and retain the installed
  generation when downloads or builds fail.
- Perform weekly garbage collection with a 30-day threshold and retain up to
  20 boot-menu entries, subject to the recovery limitations in
  [updates.md](updates.md).

## Recovery and data

- Preserve a known-good system generation during configuration changes and
  provide documented rollback and installation-media recovery procedures.
- Provide a documented path to reinstall on a blank replacement SSD without
  depending on credentials or instructions stored only on the failed laptop.
- Recover documents separately through Nextcloud or paperless-ngx, with account
  access and recovery information available independently of the laptop.
- Treat a fresh reinstall as fresh user state: full recovery of local settings,
  sessions, and keys is outside the current scope.

See [desktop-applications.md](desktop-applications.md),
[administration.md](administration.md), [updates.md](updates.md),
[recovery.md](recovery.md), and
[bare-metal-reinstall.md](bare-metal-reinstall.md) for operational details and
outstanding validation.
