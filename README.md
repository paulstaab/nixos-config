# NixOS workstation configuration

Declarative configuration for Paul's Dell XPS 15 9530. The host output is
`nixosConfigurations.nixos`.

The initial flake deliberately mirrors the graphical installer's configuration.
It adds Home Manager integration but does not yet manage user files or packages.

See [docs/administration.md](docs/administration.md) for the validation workflow
and [docs/recovery.md](docs/recovery.md) before activating a change.

