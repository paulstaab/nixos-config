# Desktop applications

Desktop applications are installed once through Paul's Home Manager packages.
Firefox remains installed by NixOS. Main nixpkgs and both state versions remain
unchanged. Only the `vscode` package is allowed as unfree, in Home Manager's
package set; the previous blanket system allowance has been removed.

Versions in the pinned main nixpkgs (`ac588ef1c914865dad517b337ea0eb9694a4021c`):

| Application | Version | Management |
| --- | --- | --- |
| Tailscale | 1.104.5 | NixOS service and CLI |
| Bitwarden Password Manager | Chrome Web Store updates | Home Manager Chromium extension registration |
| Chromium | 157.0.8103.38 | Home Manager package and default-browser MIME associations |
| Microsoft Visual Studio Code | 1.144.0 | Home Manager package, official Microsoft build |
| Nextcloud Desktop | 34.0.4 | Home Manager package, manual launch |

The pinned VS Code recipe expects an obsolete bundled ripgrep path and fails
during `patchPhase`. A local `overrideAttrs` changes that path to the verified
`node_modules.asar.unpacked/@vscode/ripgrep-universal/bin/linux-x64/rg` location
in Microsoft's 1.144.0 archive. Other packaging steps, the source/hash, and the
Microsoft marketplace configuration are preserved. Reassess this workaround
when deliberately updating nixpkgs or VS Code.

## Activation and first run

Follow [administration.md](administration.md): validation and a complete build
must succeed, then obtain approval before temporary activation:

```sh
sudo nixos-rebuild test --flake path:/var/lib/nixos-config#xenon
```

Verify the applications below. Making the result persistent requires separate
approval for `sudo nixos-rebuild switch --flake path:/var/lib/nixos-config#xenon`.
No reboot is needed to start testing; GNOME may require a new login to refresh
application menus or integration. A temporary system activation also changes
Home Manager files; rebooting to an older generation does not by itself undo
all user-state changes. Reactivating the prior configuration restores its
managed files, but may leave newly introduced MIME associations behind; review
those explicitly if abandoning Chromium as the default.

- **Tailscale:** inspect `systemctl status tailscaled` and `tailscale status`.
  The daemon is enabled without authentication or an auth key. Firewall opening
  and routing features retain the module's disabled defaults. No exit node,
  subnet routing, Tailscale SSH, or Serve is configured. Authentication is a
  separate owner action; do not run `tailscale up` as part of this rollout.
- **Bitwarden:** only the official Chromium extension is registered; no desktop
  client is installed. Check `chrome://extensions` for Bitwarden Password Manager
  with ID `nngceckbapebfimnlniiiahkandclblb`. Enable it if Chromium requests
  confirmation, then pin it if desired. Choose the intended server before
  logging in; account setup and vault unlock are manual. No Bitwarden account,
  server, or credentials are configured.
- **Chromium:** HTML files and HTTP/HTTPS URLs default to
  `chromium-browser.desktop`. Check with
  `xdg-mime query default x-scheme-handler/https` and
  `xdg-mime query default text/html`; open a link and verify it launches Chromium.
  Firefox stays available. Profiles and browser sign-in remain private user state.
- **VS Code:** launch Visual Studio Code (`code`). This is Microsoft's `vscode`
  package with its normal Microsoft extension marketplace, not VSCodium. Test
  opening Extensions and searching the marketplace. Extensions and sign-in are
  manual; no settings or authentication files are managed. On NixOS, some
  extensions downloading generic Linux binaries need additional compatibility
  configuration; assess those individually rather than enabling it globally.
- **Nextcloud:** launch Nextcloud (`nextcloud`) manually. The pinned client and
  GNOME Files both include `libcloudproviders` support; no separate
  `nautilus-nextcloud` package is available. Check Files integration after a
  deliberately configured account; overlay/context-menu support is not assumed.
  No Home Manager Nextcloud service, account, sync directory, or login autostart
  is configured. Do not complete the account wizard until ready to select and
  review local/remote folders: finishing it can start synchronization. Leave
  client-managed login autostart disabled unless deliberately requested later.

Credentials, vaults, browser profiles, and Nextcloud account information belong
in private runtime state, never in this repository or Nix expressions. GNOME
keyring handles applications' supported credential storage. Desktop launch,
marketplace access, MIME behavior, and GNOME integration require runtime testing
after approved activation; a build alone does not verify them.

## Home Manager file ownership

Before this change, both `~/.config/mimeapps.list` and
`~/.local/share/applications/mimeapps.list` were absent (metadata-only check).
Home Manager now owns `~/.config/mimeapps.list`. If it appears before activation,
inspect its path/type/ownership and arrange a backup or migration; do not force
overwrite it. Chromium, VS Code, and Nextcloud profiles are not managed files.

Home Manager also owns
`~/.config/chromium/External Extensions/nngceckbapebfimnlniiiahkandclblb.json`;
the file and its parent directories were absent at the metadata-only inspection.
The browser's remaining profile files are not managed.

## Bitwarden extension mechanism

The pinned Home Manager `programs.chromium.extensions` module writes a user-level
external-extension JSON file containing only
`external_update_url = "https://clients2.google.com/service/update2/crx"`.
Chromium downloads the current extension at browser startup with network access;
the extension version/content is not pinned or fetched by the Nix build.
It uses neither `/etc/chromium/policies` nor `ExtensionInstallForcelist` and does
not impose managed-browser restrictions. Users retain the ability to disable or
remove the extension in Chromium. A prior user removal can prevent automatic
reinstallation; if registration does not install it, use the official listing
manually rather than adding a forced-install policy.

The extension ID and update URL match
[Bitwarden's published identifiers](https://bitwarden.com/help/deploy-browser-extensions-with-intune/).
Only those public identifiers are used, not that page's enterprise deployment
instructions. Chromium's
[external-extension documentation](https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions)
describes this preferences-file mechanism separately from enterprise policy.
For manual fallback, visit the
[official Bitwarden Password Manager listing](https://chromewebstore.google.com/detail/bitwarden-password-manager/nngceckbapebfimnlniiiahkandclblb)
and verify the publisher is Bitwarden Inc. before installing. Check
`chrome://policy` after activation to confirm no extension policy was introduced.

## Validation record (2026-11-12)

Parsing, `nix flake check --no-update-lock-file`, and the complete
`nix build --no-update-lock-file .#nixosConfigurations.xenon.config.system.build.toplevel`
passed after the VS Code packaging fix. Closure and generated-unit review found
the expected application additions and new `tailscaled` service; the generated
firewall unit is unchanged. Evaluated Tailscale settings have `openFirewall =
false`, `useRoutingFeatures = "none"`, and no auth key. The built Chromium desktop
entry matches the MIME associations, and VS Code retains Microsoft's marketplace
URL. No existing installations of the requested applications were found in the
current system or Paul's Nix profile. The Bitwarden desktop client is excluded;
the extension's JSON registration is checked in the built Home Manager output.
The prior booted generation (2) remains available. No activation or application
authentication was performed; runtime
checks above remain outstanding. Neither flake input file nor state version was
changed.
