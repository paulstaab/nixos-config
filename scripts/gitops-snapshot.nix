c: {
  release = c.system.nixos.release;
  stateVersion = c.system.stateVersion;
  homeStateVersion = c.home-manager.users.paul.home.stateVersion;
  kernel = c.system.build.kernel.drvPath;
  initrd = c.system.build.initialRamdisk.drvPath;
  boot = {
    inherit (c.boot) kernelParams resumeDevice supportedFilesystems;
    inherit (c.boot.initrd) availableKernelModules kernelModules;
    luks = builtins.mapAttrs (_: d: {
      inherit (d)
        device
        allowDiscards
        bypassWorkqueues
        preLVM
        ;
    }) c.boot.initrd.luks.devices;
    systemdBoot = c.boot.loader.systemd-boot.enable;
    efiWrites = c.boot.loader.efi.canTouchEfiVariables;
  };
  networking = {
    inherit (c.networking) hostName useDHCP;
    networkmanager = c.networking.networkmanager.enable;
    firewall = {
      inherit (c.networking.firewall) enable allowedTCPPorts allowedUDPPorts;
    };
    nameservers = c.networking.nameservers;
  };
  privileged = {
    sudo = c.security.sudo.enable;
    openssh = c.services.openssh.enable;
    tailscale = c.services.tailscale.enable;
    services = builtins.attrNames c.systemd.services;
  };
}
