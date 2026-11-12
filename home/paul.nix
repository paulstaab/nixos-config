{ lib, pkgs, ... }:

let
  # Pinned VS Code 1.144.0 moved its bundled ripgrep. Keep the upstream
  # packaging steps, but replace the binary at the archive's actual path.
  vscodeDesktop = pkgs.vscode.overrideAttrs (old: {
    postPatch =
      lib.replaceStrings
        [ "resources/app/node_modules/@vscode/ripgrep/bin/rg" ]
        [ "resources/app/node_modules.asar.unpacked/@vscode/ripgrep-universal/bin/linux-x64/rg" ]
        old.postPatch;
  });
in
{
  home.username = "paul";
  home.homeDirectory = "/home/paul";

  # Keep this at the first Home Manager version used for this account.
  home.stateVersion = "26.05";

  programs.home-manager.enable = true;

  # Only the official Microsoft VS Code build requires an unfree allowance.
  nixpkgs.config.allowUnfreePredicate = pkg: lib.getName pkg == "vscode";

  home.packages = with pkgs; [
    vscodeDesktop
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
