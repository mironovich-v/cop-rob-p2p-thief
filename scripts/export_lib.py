"""Pure, deterministic helpers for the two-repo export (Stage 7.6b): a stable
content hash, a filtered tree copy that never carries secrets/junk, and the
generated per-role pyproject / README templates. No timestamps enter hashed
content, so re-running from the same source is byte-identical.
"""

import hashlib
import shutil
from pathlib import Path

# Directory names and file patterns that must never reach an export (secrets,
# private match logs, build junk, the git-ignored external league kit, and the
# exporter's own test — which needs the workspace `scripts/` path).
EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache", ".ruff_cache", ".venv",
                "secrets", "logs", "dist", "copthief-league-protocol"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_NAMES = {".env", ".coverage", "test_export.py",
                 "game.local.toml"}  # window-day overlay: URLs/arming, never shipped


def iter_files(root: Path):
    """Deterministic (sorted) file list under root, minus secrets/junk."""
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        rel_parts = set(path.relative_to(root).parts)
        if (rel_parts & EXCLUDE_DIRS or path.suffix in EXCLUDE_SUFFIXES
                or path.name in EXCLUDE_NAMES):
            continue
        yield path


def content_hash(root: Path) -> str:
    """SHA-256 over sorted (relpath, bytes) — a stable digest of a tree's content."""
    digest = hashlib.sha256()
    for path in iter_files(root):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def copy_tree(src: Path, dst: Path) -> None:
    """Copy src into dst with the same exclusions the hash uses."""
    for path in iter_files(src):
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def pyproject_toml(role: str) -> str:
    return f"""[project]
name = "cop-thief-{role}"
version = "1.0.0"
description = "vm__fabi — Cop-Thief P2P {role} agent (generated export; do not edit by hand)"
requires-python = ">=3.13"
dependencies = ["fastmcp>=3.4.3"]

[project.scripts]
{role}-agent = "{role}_agent.__main__:main"

[dependency-groups]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.6"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cop_thief_core", "src/{role}_agent"]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-q"

[tool.coverage.run]
source = ["src"]
omit = ["*/gui/*", "src/*/__main__.py"]
"""


def readme_md(role: str, sibling_url: str, workspace_url: str) -> str:
    return f"""# Cop-Thief P2P — {role} agent (vm__fabi)

Generated export of the **{role}** peer. Self-contained: vendors the canonical
`cop_thief_core` (see `core_manifest.json` for its source commit + hash).

```bash
uv sync
uv run pytest tests
uv run python -m {role}_agent --config config/{role}
```

- Canonical workspace: {workspace_url}
- Sibling ({'thief' if role == 'police' else 'police'}) repo: {sibling_url}

**Development history (book rules 41/49-50, p.156):** the branch
`workspace-history` in THIS repository mirrors the canonical workspace's full
development record (every PR, review, and played match commit). Commit hashes
declared in match declarations/emails resolve here: `git log workspace-history`.
`main` is the clean release line; the docs (`PRD`/`PLAN`/`TODO`/`PROMPTS`/
`COSTS`) narrate the same development story per the submission guide.

Do not edit vendored `cop_thief_core` here — change it in the workspace and
re-run `scripts/export_repos.py`. No secrets are included; copy `.env-example`
to `.env` locally for Gmail/LLM/tunnel credentials.
"""
