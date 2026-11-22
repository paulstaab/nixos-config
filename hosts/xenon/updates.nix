{ pkgs, config, ... }:

let
  updater = pkgs.writeShellApplication {
    name = "xenon-update";
    runtimeInputs = [
      pkgs.coreutils
      pkgs.findutils
      pkgs.gnused
      pkgs.gitMinimal
      pkgs.util-linux
      config.nix.package
      config.system.build.nixos-rebuild
    ];
    text = builtins.readFile ../../scripts/xenon-update;
  };
in
{
  environment.systemPackages = [ updater ];

  systemd.services.nixos-upgrade = {
    description = "Refresh xenon inputs and prepare the next boot generation";
    restartIfChanged = false;
    unitConfig.X-StopOnRemoval = false;
    environment.HOME = "/root";
    wants = [ "network-online.target" ];
    after = [ "network-online.target" ];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${updater}/bin/xenon-update daily";
    };
  };
  systemd.timers.nixos-upgrade = {
    wantedBy = [ "timers.target" ];
    timerConfig = {
      OnCalendar = "04:40";
      Persistent = true;
    };
  };

  boot.loader.systemd-boot.configurationLimit = 20;
  nix.gc = {
    automatic = true;
    dates = "weekly";
    persistent = true;
    options = "--delete-older-than 30d";
  };
}
