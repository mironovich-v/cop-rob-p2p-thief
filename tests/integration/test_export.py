"""Tests for the two-repo export (Stage 7.6b): both self-contained trees, a
matching core-drift manifest, no secrets, determinism, and importability of the
vendored core. This file is excluded from the exported tree (it needs the
workspace `scripts/` path)."""

import subprocess
import sys
from pathlib import Path

import pytest
from export_repos import export_all

WORKSPACE = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def exported(tmp_path_factory):
    dist = tmp_path_factory.mktemp("dist")
    manifests = export_all(WORKSPACE, dist, commit="deadbeefcafe")
    return dist, manifests


def test_both_trees_are_self_contained(exported):
    dist, _ = exported
    for role in ("police", "thief"):
        out = dist / f"{role}-agent"
        assert (out / "src" / "cop_thief_core" / "__init__.py").is_file()
        assert (out / "src" / f"{role}_agent" / "__main__.py").is_file()
        assert (out / "config" / role / "game.toml").is_file()
        assert (out / "pyproject.toml").is_file()
        assert (out / "README.md").is_file()
        assert (out / "core_manifest.json").is_file()
    # no cross-role package: the police export never ships thief_agent, and vice versa
    assert not (dist / "police-agent" / "src" / "thief_agent").exists()
    assert not (dist / "thief-agent" / "src" / "police_agent").exists()


def test_manifests_share_one_core_hash(exported):
    _, manifests = exported
    assert manifests["police"]["core_sha256"] == manifests["thief"]["core_sha256"]
    assert manifests["police"]["core_commit"] == "deadbeefcafe"
    assert manifests["police"]["sibling_repo"] == manifests["thief"]["repo"]


def test_no_secrets_or_private_logs_shipped(exported):
    dist, _ = exported
    for role in ("police", "thief"):
        out = dist / f"{role}-agent"
        assert not (out / ".env").exists()
        assert not (out / "secrets").exists()
        assert not (out / "logs").exists()
        assert not list(out.rglob("*.pyc"))
        assert (out / ".env-example").is_file()  # placeholders only
        assert not (out / "tests" / "integration" / "test_export.py").exists()


def test_export_is_deterministic(exported, tmp_path):
    _, first = exported
    again = export_all(WORKSPACE, tmp_path / "again", commit="deadbeefcafe")
    assert again["police"]["core_sha256"] == first["police"]["core_sha256"]


def test_vendored_core_imports_standalone(exported):
    dist, _ = exported
    out = dist / "police-agent"
    result = subprocess.run(
        [sys.executable, "-c", "import cop_thief_core, police_agent; print('ok')"],
        env={"PYTHONPATH": str(out / "src")}, cwd=str(out),
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_export_ships_the_match_evidence(exported):
    # The filed counted reports' links.github promises the grader the four
    # artifact kinds + the committed rule-52 ledger — BOTH role repos carry
    # them (rule 49; kit WARNINGS §5a).
    dist, _ = exported
    for role in ("police", "thief"):
        results = dist / f"{role}-agent" / "results"
        assert (results / "rule52_ledger.json").is_file()
        if (WORKSPACE / "results" / "counted").is_dir():  # banked 2026-08-18
            assert list((results / "counted").rglob("result_*.json")), (
                f"{role}: counted evidence missing from the export")
