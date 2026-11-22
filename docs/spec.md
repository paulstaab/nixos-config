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

- Prepare local system updates daily for the next manual reboot, without
  switching the running system or rebooting automatically.
- Stay on the selected NixOS and Home Manager release branches until a deliberate
  release upgrade; update Codex through its separate revision pin.
- Keep routine updates local, without automatic Git commits, pushes, or PRs.
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

## Deferred scope and acceptance

- Hibernation repair, system snapshots, and full user-state backups are deferred.
- Server availability and server-side backups for Nextcloud and paperless-ngx
  are outside this laptop configuration's scope.
- A successful build alone does not establish runtime reliability. Desktop,
  networking, hardware, application integration, and reboot behavior require
  acceptance testing; the blank-SSD reinstall procedure also remains unproven
  end to end.

See [desktop-applications.md](desktop-applications.md),
[administration.md](administration.md), [updates.md](updates.md),
[recovery.md](recovery.md), and
[bare-metal-reinstall.md](bare-metal-reinstall.md) for operational details and
outstanding validation.
