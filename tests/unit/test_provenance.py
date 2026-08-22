"""The commit we declare must be reachable in the repos we submit.

We name the two role repositories on the wire and in every artifact, and the
lecturer resolves our playing commit there. A commit that only exists on the
operator's laptop is unverifiable, so an armed run must refuse rather than
publish an unresolvable claim. The submission repos mirror the workspace on
`workspace-history`; their `main` is the exported agent tree and never contains
these hashes.
"""

from pathlib import Path

import pytest

from cop_thief_core.shared.provenance import MIRROR_REF, check_published

REPO_ROOT = Path(__file__).resolve().parents[2]


class _NoopSender:
    def preflight_armed(self):
        return None

    def send_report(self, *a, **k):
        return {"sent": False}

REPOS = {"cop": "https://example.test/police", "thief": "https://example.test/thief"}
HEAD = "a" * 40
PUSHED = "b" * 40


def _resolver(mapping):
    return lambda url, ref: mapping.get(url)


def test_published_when_every_repo_mirror_contains_the_commit():
    out = check_published(HEAD, REPOS, _resolver(dict.fromkeys(REPOS.values(), PUSHED)),
                          is_ancestor=lambda a, b: True)
    assert out["published"] is True
    assert set(out["checked"]) == set(REPOS.values())


def test_unpublished_when_a_mirror_does_not_contain_it():
    """The commit is pushed to one repo but not the other — half-published is not
    published; the role we play in a given sub-game decides which repo is read."""
    out = check_published(HEAD, REPOS, _resolver(dict.fromkeys(REPOS.values(), PUSHED)),
                          is_ancestor=lambda a, b: b == PUSHED and a == HEAD and False)
    assert out["published"] is False
    assert "not reachable" in out["detail"]


def test_unpublished_when_a_mirror_ref_is_missing():
    out = check_published(HEAD, REPOS, _resolver({}), is_ancestor=lambda a, b: True)
    assert out["published"] is False
    assert MIRROR_REF in out["detail"]


def test_unknown_remote_sha_is_not_treated_as_published():
    """If we cannot decide ancestry (the remote tip is an object we do not hold),
    that is UNKNOWN — and unknown must never read as published."""
    out = check_published(HEAD, REPOS, _resolver(dict.fromkeys(REPOS.values(), PUSHED)),
                          is_ancestor=lambda a, b: None)
    assert out["published"] is False


def test_no_repos_configured_is_not_published():
    out = check_published(HEAD, {}, _resolver({}), is_ancestor=lambda a, b: True)
    assert out["published"] is False


def test_unknown_commit_is_not_published():
    """`playing_commit()` degrades to 'unknown' outside a checkout."""
    out = check_published("unknown", REPOS, _resolver(dict.fromkeys(REPOS.values(), PUSHED)),
                          is_ancestor=lambda a, b: True)
    assert out["published"] is False


# --- wiring: an ARMED run refuses an unpublished commit ----------------------

def test_armed_run_refuses_when_the_commit_is_not_published(tmp_path, monkeypatch):
    """A counted series declares a commit a grader will resolve. Publishing a
    claim nobody can check is worse than not playing, so arming refuses."""
    from cop_thief_core.exceptions import SimulationError
    from cop_thief_core.sdk import SimulationSdk
    sdk = SimulationSdk(REPO_ROOT / "config" / "vibecode", workdir=tmp_path)
    sdk.config.override("game.counted", True)   # config half of the ADR-20 arming
    sdk.email_sender = _NoopSender()
    monkeypatch.setattr("cop_thief_core.sdk.sdk.check_published",
                        lambda *a, **k: {"published": False, "detail": "not pushed",
                                         "checked": {}})
    with pytest.raises(SimulationError, match="not pushed"):
        sdk._arm(True)


def test_friendly_run_never_blocks_on_publication(tmp_path, monkeypatch):
    """A friendly must not be held hostage to a network check mid-window."""
    from cop_thief_core.sdk import SimulationSdk
    sdk = SimulationSdk(REPO_ROOT / "config" / "police", workdir=tmp_path)
    called = []
    monkeypatch.setattr("cop_thief_core.sdk.sdk.check_published",
                        lambda *a, **k: called.append(1) or {"published": False,
                                                             "detail": "x", "checked": {}})
    assert sdk._arm(False) is False
    assert called == []
