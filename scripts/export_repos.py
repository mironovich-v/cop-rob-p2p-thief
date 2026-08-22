"""Deterministic two-repo export (Stage 7.6b): generate dist/police-agent and
dist/thief-agent, each vendoring the canonical cop_thief_core + its role package +
both configs + the test suite, cross-linked, carrying a core-drift manifest and no
secrets. Neither export depends at runtime on the other repo (§13).

    uv run python scripts/export_repos.py            # into ./dist
    uv run python scripts/export_repos.py --dist /tmp/out

See docs/PRD_two_repo_export.md.
"""

import argparse
import contextlib
import json
import shutil
import subprocess
from pathlib import Path

from export_lib import content_hash, copy_tree, pyproject_toml, readme_md

ROLES = ("police", "thief")
REPOS = {
    "police": "https://github.com/mironovich-v/cop-rob-p2p-police",
    "thief": "https://github.com/mironovich-v/cop-rob-p2p-thief",
}
WORKSPACE_REPO = "https://github.com/mironovich-v/cop-rob-p2p"


def git_commit(workspace: Path) -> str:
    try:
        done = subprocess.run(["git", "-C", str(workspace), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True)
        return done.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"



def _tracked_under(workspace: Path, directory: str) -> list[str]:
    """Repo-relative paths of the git-TRACKED files under ``directory``.

    Evidence lives behind `.gitignore` and is force-added deliberately, so
    "tracked" is exactly the set we chose to publish — a more honest rule than
    any hand-maintained list, which is what went stale here.
    """
    result = subprocess.run(["git", "ls-files", "--", directory], cwd=workspace,
                            capture_output=True, text=True, check=False)
    return [line for line in result.stdout.splitlines() if line.strip()]

def export_role(role: str, workspace: Path, dist_dir: Path, commit: str) -> dict:
    """Build one self-contained role export and return its manifest."""
    out = dist_dir / f"{role}-agent"
    if out.exists():
        shutil.rmtree(out)
    copy_tree(workspace / "src" / "cop_thief_core", out / "src" / "cop_thief_core")
    copy_tree(workspace / "src" / f"{role}_agent", out / "src" / f"{role}_agent")
    # The WHOLE config tree ships: self-play configs plus the pairing
    # constitutions (match-record provenance the counted artifacts reference).
    # iter_files excludes game.local.toml (window-day URLs/arming overlays).
    copy_tree(workspace / "config", out / "config")
    copy_tree(workspace / "tests", out / "tests")
    example = workspace / ".env-example"
    if example.is_file():
        (out / ".env-example").write_bytes(example.read_bytes())
    # Match evidence (rule 49 / WARNINGS §5a): the counted-series artifacts and
    # the committed rule-52 ledger are what the filed reports' links.github
    # promises the grader — they ship in BOTH role repos.
    # Export every TRACKED file under results/ — not a hand-listed subset. The
    # first version copied only the ledger and counted/, which silently dropped
    # played_commits.md and results/README.md: the two documents written FOR a
    # grader holding just this repo. Driving the copy from `git ls-files` means
    # anything we deliberately track ships, and the untracked scratch copies in
    # results/ (browser-downloaded compare files) never do.
    for relative in _tracked_under(workspace, "results"):
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((workspace / relative).read_bytes())
    # A submission repo must STAND ALONE for grading: the guideline's mandatory
    # documentation set, the AI-control files, the academic README, the license,
    # and an .gitignore ship in BOTH trees (owner finding, 2026-08-19 — the
    # lecturer's own reference ships docs/ + uv.lock + LICENSE at root).
    copy_tree(workspace / "docs", out / "docs")
    for name in ("CLAUDE.md", "COSTS.md", "LICENSE", ".gitignore"):
        source = workspace / name
        if source.is_file():
            (out / name).write_bytes(source.read_bytes())
    (out / "pyproject.toml").write_text(pyproject_toml(role), encoding="utf-8")
    sibling = "thief" if role == "police" else "police"
    banner = readme_md(role, REPOS[sibling], WORKSPACE_REPO)
    academic = (workspace / "README.md").read_text(encoding="utf-8")
    (out / "README.md").write_text(  # role banner + the full academic manual
        banner + "\n---\n\n" + academic, encoding="utf-8")
    manifest = {
        "role": role,
        "core_commit": commit,
        "core_sha256": content_hash(out / "src" / "cop_thief_core"),
        "workspace_repo": WORKSPACE_REPO,
        "repo": REPOS[role],
        "sibling_repo": REPOS[sibling],
    }
    (out / "core_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def lock_tree(out: Path) -> None:
    """Generate the export's own uv.lock (matches ITS pyproject — the workspace
    lock would not). Skipped gracefully when uv is unavailable (CI-safe)."""
    with contextlib.suppress(subprocess.CalledProcessError, FileNotFoundError,
                             OSError, subprocess.TimeoutExpired):
        subprocess.run(["uv", "lock"], cwd=out, check=True,
                       capture_output=True, timeout=120)


def export_all(workspace: Path, dist_dir: Path, commit: str | None = None,
               lock: bool = True) -> dict:
    """Export both roles; assert the vendored core is byte-identical across them."""
    commit = commit or git_commit(workspace)
    manifests = {role: export_role(role, workspace, dist_dir, commit) for role in ROLES}
    if lock:
        for role in ROLES:
            lock_tree(dist_dir / f"{role}-agent")
    hashes = {role: manifest["core_sha256"] for role, manifest in manifests.items()}
    if len(set(hashes.values())) != 1:
        raise SystemExit(f"core drift between exports: {hashes}")
    return manifests


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the two submission repos")
    parser.add_argument("--dist", default="dist", help="output dir (default: ./dist)")
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parent.parent
    manifests = export_all(workspace, Path(args.dist).resolve())
    first = next(iter(manifests.values()))
    print(f"exported {', '.join(f'{r}-agent' for r in ROLES)} to {args.dist} "
          f"| core {first['core_sha256'][:16]} @ {first['core_commit'][:12]}")


if __name__ == "__main__":
    main()
