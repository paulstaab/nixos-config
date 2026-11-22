{ config, ... }:

{
  # Use the mutable checkout, never an immutable self.outPath store snapshot.
  system.autoUpgrade = {
    enable = true;
    flake = "path:/home/paul/nixos-config#xenon";
    operation = "boot";
    upgrade = false;
    allowReboot = false;
    dates = "04:40";
    persistent = true;
    flags = [ "--no-update-lock-file" ];
  };

  # ExecStartPre failure prevents the build. Timer and manual starts of this
  # same oneshot service cannot overlap, including input refresh and build.
  systemd.services.nixos-upgrade = {
    serviceConfig.WorkingDirectory = "/home/paul/nixos-config";
    preStart = ''
      ${config.nix.package}/bin/nix flake update --flake path:/home/paul/nixos-config
    '';
  };

  boot.loader.systemd-boot.configurationLimit = 20;
  nix.gc = {
    automatic = true;
    dates = "weekly";
    persistent = true;
    options = "--delete-older-than 30d";
  };
}
