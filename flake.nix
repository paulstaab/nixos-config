{
  description = "Paul's Dell XPS 15 NixOS configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/ac588ef1c914865dad517b337ea0eb9694a4021c";

    # Keep Codex current without updating the workstation's package set.
    codex-nixpkgs.url = "github:NixOS/nixpkgs/3730a4017d0f44c3a09faa593269bcbddae1fa18";

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
