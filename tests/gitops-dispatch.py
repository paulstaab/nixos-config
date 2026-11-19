#!/usr/bin/env python3
"""Exercise the write-capable dispatch boundary using local Git and a fake API."""
import copy
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
real_git = shutil.which("git")
if real_git is None:
    raise SystemExit("git not found in PATH; dispatch fixtures require Git")
with tempfile.TemporaryDirectory() as tmp:
    work = pathlib.Path(tmp)
    repo, bin_dir = work / "repo", work / "bin"
    repo.mkdir()
    bin_dir.mkdir()
    (repo / "scripts").mkdir()
    shutil.copy(root / "scripts/gitops-lock-policy", repo / "scripts")
    original = json.loads((root / "flake.lock").read_text())
    (repo / "flake.lock").write_text(json.dumps(original))

    def git(*args):
        return subprocess.check_output([real_git, *args], cwd=repo, text=True).strip()

    git("init", "-q")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    updated = copy.deepcopy(original)
    locked = updated["nodes"]["nixpkgs"]["locked"]
    locked.update(rev="b" * 40, narHash="sha256-" + "B" * 43 + "=",
                  lastModified=locked["lastModified"] + 1)
    (repo / "flake.lock").write_text(json.dumps(updated))
    git("add", ".")
    git("commit", "-qm", "lock update")
    head = git("rev-parse", "HEAD")
    (repo / "unexpected.nix").write_text("{}\n")
    git("add", ".")
    git("commit", "-qm", "unexpected config")
    extra_head = git("rev-parse", "HEAD")
    (repo / "flake.lock").write_text(json.dumps(original))
    git("add", ".")
    git("commit", "-qm", "not an update")
    invalid_head = git("rev-parse", "HEAD")
    metadata = {
        "state": "open", "user": {"login": "github-actions[bot]"},
        "base": {"repo": {"id": 1455774448}, "ref": "main", "sha": base},
        "head": {"repo": {"id": 1455774448},
                 "ref": "automation/dependency-updates", "sha": head},
    }
    # API and dispatch are mocked. No token, remote request, or push is used.
    (bin_dir / "gh").write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
if args[:2] == ["api", "--method"]:
    # A fork PR (#3) has the same branch name. Only the owner-qualified
    # selector finds canonical #2, or no PR when only the fork exists.
    assert args[2:4] == ["GET", "repos/paulstaab/nixos-config/pulls"]
    assert "state=open" in args and "base=main" in args
    assert "head=paulstaab:automation/dependency-updates" in args
    if os.environ.get("MULTIPLE_PRS"):
        sys.exit(1)
    print("" if os.environ.get("NO_PR") else "2")
elif args[:2] == ["pr", "list"]:
    print("3")  # Regression: the old ambiguous selector picked the fork.
elif args[0] == "api":
    data = json.loads(pathlib.Path(os.environ["METADATA"]).read_text())
    if args[1].endswith("/3"):
        data["head"]["repo"]["id"] = 123
    else:
        assert args[1] == "repos/paulstaab/nixos-config/pulls/2"
    print(json.dumps(data))
elif args[:2] == ["workflow", "run"]:
    pathlib.Path(os.environ["DISPATCH"]).write_text(json.dumps(args))
    sys.exit(int(os.environ.get("DISPATCH_FAILURE", "0")))
else:
    sys.exit(90)
''')
    (bin_dir / "git").write_text('''#!/usr/bin/env python3
import os, sys
if sys.argv[1] == "fetch":
    assert sys.argv[2:4] == ["--no-tags", "https://github.com/paulstaab/nixos-config.git"]
    sys.exit(0)
os.execv(os.environ["REAL_GIT"], [os.environ["REAL_GIT"], *sys.argv[1:]])
''')
    for p in bin_dir.iterdir():
        p.chmod(0o755)
    data, dispatch = work / "metadata.json", work / "dispatch.json"
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
               REAL_GIT=real_git, METADATA=str(data), DISPATCH=str(dispatch),
               GITHUB_REPOSITORY="paulstaab/nixos-config", GITHUB_REF="refs/heads/main")

    def check(candidate, success, sends=False, **overrides):
        data.write_text(json.dumps(candidate))
        dispatch.unlink(missing_ok=True)
        result = subprocess.run([str(root / "scripts/gitops-dispatch-ci"), base],
                                cwd=repo, env=dict(env, **overrides), capture_output=True)
        assert (result.returncode == 0) == success, result.stderr
        assert dispatch.exists() == sends
        if sends:
            args = json.loads(dispatch.read_text())
            assert "expected_head=" + head in args
            assert "base_sha=" + base in args
            assert args[args.index("--ref") + 1] == "automation/dependency-updates"

    check(metadata, True, True)
    check(metadata, True, NO_PR="1")  # Fork-only result must not target the fork.
    check(metadata, False, MULTIPLE_PRS="1")
    check(metadata, False, True, DISPATCH_FAILURE="1")
    check(metadata, False, GITHUB_REF="refs/pull/2/merge")
    for section, key, value in [
        ("user", "login", "attacker"), ("head", "repo", {"id": 123}),
        ("base", "ref", "other"), ("base", "sha", "0" * 40),
        ("head", "sha", "not-a-sha"), ("head", "ref", "feature"),
        ("head", "sha", extra_head), ("head", "sha", invalid_head),
    ]:
        bad = copy.deepcopy(metadata)
        bad[section][key] = value
        check(bad, False)
    # Exercise the actual receiver shell from ci.yml, including head races.
    workflow = (root / ".github/workflows/ci.yml").read_text()
    step = workflow.split("      - name: Verify dispatched update identity\n", 1)[1]
    body = step.split("        run: |\n", 1)[1].split("      - name:", 1)[0]
    receiver = "\n".join(line[10:] for line in body.splitlines())
    git("checkout", "-q", "--detach", head)
    receiver_env = dict(env, BASE_SHA=base, EXPECTED_HEAD=head, GITHUB_SHA=head,
                        GITHUB_REF="refs/heads/automation/dependency-updates")

    def receive(success, **overrides):
        result = subprocess.run(["bash", "-c", receiver], cwd=repo,
                                env=dict(receiver_env, **overrides), capture_output=True)
        assert (result.returncode == 0) == success, result.stderr

    receive(True)
    receive(False, GITHUB_SHA=extra_head)  # Ref moved before dispatch resolved.
    receive(False, EXPECTED_HEAD=extra_head)
    receive(False, GITHUB_REF="refs/heads/main")
    receive(False, GITHUB_REPOSITORY="attacker/fork")
    receive(False, BASE_SHA="")  # Partial inputs must not select manual fallback.
    receive(False, EXPECTED_HEAD="")
    receive(False, BASE_SHA="not-a-sha")
    receive(False, BASE_SHA=extra_head)  # Candidate is not descended from base.
    receive(True, BASE_SHA="", EXPECTED_HEAD="")  # Ordinary manual CI.
print("Dispatch and receiver identity, lock-only, race, no-op and API failure fixtures passed.")
