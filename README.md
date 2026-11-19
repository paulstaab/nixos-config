# NixOS workstation configuration

Declarative configuration for Paul's Dell XPS 15 9530, named `xenon`. The host
output is `nixosConfigurations.xenon`.

The flake builds on the graphical installer's configuration. Home Manager
installs Paul's desktop applications and manages the default browser.

See [docs/administration.md](docs/administration.md) for the validation workflow
and [docs/recovery.md](docs/recovery.md) before activating a change.
See [docs/desktop-applications.md](docs/desktop-applications.md) for first-run
instructions.

See [docs/updates.md](docs/updates.md) for separate system and Codex updates,
validation reports, approval boundaries, runtime tests, and rollback.

See [docs/gitops.md](docs/gitops.md) for the prepared GitHub CI/update-PR workflows,
trust boundaries, pending GitHub settings and future pull deployment design.
Automatic updates are gated off; merging and deployment remain manual.
