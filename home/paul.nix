{ ... }:

{
  home.username = "paul";
  home.homeDirectory = "/home/paul";

  # Keep this at the first Home Manager version used for this account.
  home.stateVersion = "26.05";

  programs.home-manager.enable = true;
}

