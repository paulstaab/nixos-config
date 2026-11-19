#!/usr/bin/env python3
"""Offline adversarial fixtures; no dependency resolution or remote operations."""
import copy
import json
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
old = json.loads((root / "flake.lock").read_text())
new = copy.deepcopy(old)
new["nodes"]["home-manager"]["locked"].update(
    rev="a" * 40, narHash="sha256-" + "A" * 43 + "=",
    lastModified=old["nodes"]["home-manager"]["locked"]["lastModified"] + 1,
)
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    before, after = tmp / "before", tmp / "after"
    before.write_text(json.dumps(old))

    def check(candidate, expected):
        after.write_text(json.dumps(candidate))
        result = subprocess.run([str(root / "scripts/gitops-lock-policy"),
                                 str(before), str(after)], capture_output=True)
        assert (result.returncode == 0) == expected, result.stderr

    check(new, True)  # Home Manager only
    nixpkgs_only = copy.deepcopy(old)
    nixpkgs_only["nodes"]["nixpkgs"]["locked"].update(
        rev="b" * 40, narHash="sha256-" + "B" * 43 + "=",
        lastModified=old["nodes"]["nixpkgs"]["locked"]["lastModified"] + 1,
    )
    check(nixpkgs_only, True)
    both = copy.deepcopy(new)
    both["nodes"]["nixpkgs"]["locked"] = nixpkgs_only["nodes"]["nixpkgs"]["locked"]
    check(both, True)
    check(old, False)
    for node, field, value in [
        ("home-manager", "original", {"ref": "master"}),
        ("home-manager", "inputs", {"nixpkgs": ["codex-nixpkgs"]}),
        ("nixpkgs", "original", {"ref": "nixos-unstable"}),
        ("nixpkgs", "original", {"ref": "nixos-26.11"}),
        ("nixpkgs", "locked", {}),
        ("codex-nixpkgs", "original", {}),
        ("codex-nixpkgs", "locked", {}),
        ("root", "inputs", {}),
    ]:
        bad = copy.deepcopy(both)
        bad["nodes"][node][field] = value
        check(bad, False)
    for node in ("nixpkgs", "home-manager"):
        for field, value in [("owner", "attacker"), ("rev", "not-a-sha"),
                             ("narHash", "invalid"), ("lastModified", 0),
                             ("lastModified", True)]:
            bad = copy.deepcopy(both)
            bad["nodes"][node]["locked"][field] = value
            check(bad, False)
        bad = copy.deepcopy(old)
        bad["nodes"][node]["locked"]["lastModified"] += 1
        check(bad, False)
    bad = copy.deepcopy(both)
    bad["nodes"]["extra"] = {}
    check(bad, False)

    def closure(version):
        return {"/nix/store/" + "a" * 32 + "-example-" + version: {}}

    for a, b, expected in [("2.0", "1.9", False), ("1.9", "2.0", True),
                           ("1.9", "1.9", True), ("1.9", "1.10", True)]:
        before.write_text(json.dumps(closure(a)))
        after.write_text(json.dumps(closure(b)))
        result = subprocess.run([str(root / "scripts/gitops-downgrades"),
                                 str(before), str(after)], capture_output=True)
        assert (result.returncode == 0) == expected, result.stderr
print("Lock-policy rejection and downgrade fixtures passed.")
