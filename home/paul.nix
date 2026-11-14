{ lib, pkgs, ... }:

{
  home.username = "paul";
  home.homeDirectory = "/home/paul";

  # Keep this at the first Home Manager version used for this account.
  home.stateVersion = "26.05";

  programs.home-manager.enable = true;

  # Only the official Microsoft VS Code build requires an unfree allowance.
  nixpkgs.config.allowUnfreePredicate = pkg: lib.getName pkg == "vscode";

  home.packages = with pkgs; [
    vscode
    # Includes libcloudproviders support for GNOME Files. Launch manually;
    # the Home Manager service would start the client at graphical login.
    nextcloud-client
  ];

  programs.chromium = {
    enable = true;
    # User-level external extension registration, not enterprise policy.
    extensions = [ "nngceckbapebfimnlniiiahkandclblb" ]; # Bitwarden Password Manager
  };

  xdg.mimeApps = {
    enable = true;
    defaultApplications = {
      "text/html" = [ "chromium-browser.desktop" ];
      "x-scheme-handler/http" = [ "chromium-browser.desktop" ];
      "x-scheme-handler/https" = [ "chromium-browser.desktop" ];
    };
  };
}
