# NixOS workstation configuration

Declarative configuration for Paul's Dell XPS 15 9530, named `xenon`. The host
output is `nixosConfigurations.xenon`.

See [docs/spec.md](docs/spec.md) for the laptop's high-level requirements.

The flake builds on the graphical installer's configuration. Home Manager
installs Paul's desktop applications and manages the default browser.

See [docs/administration.md](docs/administration.md) for the validation workflow
and [docs/recovery.md](docs/recovery.md) before activating a change.
See [docs/desktop-applications.md](docs/desktop-applications.md) for first-run
instructions.

See [docs/updates.md](docs/updates.md) for the root-owned canonical checkout, `sudo xenon-update boot` or `switch`, and daily updates prepared for the
next manual reboot, local lock-file handling, monitoring, retention and rollback.
See [docs/gitops.md](docs/gitops.md) for read-only GitHub PR verification.
