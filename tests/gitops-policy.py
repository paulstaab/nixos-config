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

    check(new, True)
    check(old, False)
    for node, field, value in [
        ("home-manager", "original", {"ref": "master"}),
        ("home-manager", "inputs", {"nixpkgs": ["codex-nixpkgs"]}),
        ("nixpkgs", "locked", {}),
        ("codex-nixpkgs", "original", {}),
        ("root", "inputs", {}),
    ]:
        bad = copy.deepcopy(new)
        bad["nodes"][node][field] = value
        check(bad, False)
    for field, value in [("owner", "attacker"), ("rev", "not-a-sha"),
                         ("narHash", "invalid"), ("lastModified", 0)]:
        bad = copy.deepcopy(new)
        bad["nodes"]["home-manager"]["locked"][field] = value
        check(bad, False)
    bad = copy.deepcopy(new)
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
