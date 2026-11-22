{
  description = "Paul's Dell XPS 15 NixOS configuration";

  inputs = {
    # Release policy lives here; exact revisions remain pinned in flake.lock.
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

    # Keep Codex current without updating the workstation's package set.
    codex-nixpkgs.url = "github:NixOS/nixpkgs/93a9ed0a866099a230ed5146a5bb7d16fd5c9b14";

    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      codex-nixpkgs,
      home-manager,
      ...
    }:
    {
      nixosConfigurations.xenon = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        specialArgs = { inherit codex-nixpkgs; };
        modules = [
          ./hosts/xenon/configuration.nix
          home-manager.nixosModules.home-manager
          {
            home-manager.users.paul = import ./home/paul.nix;
          }
        ];
      };
    };
}
