"""Deterministic two-repo export (Stage 7.6b): generate dist/police-agent and
dist/thief-agent, each vendoring the canonical cop_thief_core + its role package +
both configs + the test suite, cross-linked, carrying a core-drift manifest and no
secrets. Neither export depends at runtime on the other repo (§13).

    uv run python scripts/export_repos.py            # into ./dist
    uv run python scripts/export_repos.py --dist /tmp/out

See docs/PRD_two_repo_export.md.
"""

import argparse
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


def export_role(role: str, workspace: Path, dist_dir: Path, commit: str) -> dict:
    """Build one self-contained role export and return its manifest."""
    out = dist_dir / f"{role}-agent"
    if out.exists():
        shutil.rmtree(out)
    copy_tree(workspace / "src" / "cop_thief_core", out / "src" / "cop_thief_core")
    copy_tree(workspace / "src" / f"{role}_agent", out / "src" / f"{role}_agent")
    for cfg_role in ROLES:  # both configs ship (local self-play + the test suite)
        copy_tree(workspace / "config" / cfg_role, out / "config" / cfg_role)
    copy_tree(workspace / "tests", out / "tests")
    example = workspace / ".env-example"
    if example.is_file():
        (out / ".env-example").write_bytes(example.read_bytes())
    # Match evidence (rule 49 / WARNINGS §5a): the counted-series artifacts and
    # the committed rule-52 ledger are what the filed reports' links.github
    # promises the grader — they ship in BOTH role repos.
    ledger = workspace / "results" / "rule52_ledger.json"
    if ledger.is_file():
        (out / "results").mkdir(parents=True, exist_ok=True)
        (out / "results" / "rule52_ledger.json").write_bytes(ledger.read_bytes())
    counted = workspace / "results" / "counted"
    if counted.is_dir():
        copy_tree(counted, out / "results" / "counted")
    (out / "pyproject.toml").write_text(pyproject_toml(role), encoding="utf-8")
    sibling = "thief" if role == "police" else "police"
    (out / "README.md").write_text(
        readme_md(role, REPOS[sibling], WORKSPACE_REPO), encoding="utf-8")
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


def export_all(workspace: Path, dist_dir: Path, commit: str | None = None) -> dict:
    """Export both roles; assert the vendored core is byte-identical across them."""
    commit = commit or git_commit(workspace)
    manifests = {role: export_role(role, workspace, dist_dir, commit) for role in ROLES}
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
