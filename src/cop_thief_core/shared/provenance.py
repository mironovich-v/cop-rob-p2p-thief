"""Is the commit we are about to declare reachable in the repos we submit?

We name the two role repositories on the wire and in every artifact, and a
grader resolves our playing commit there. A commit that exists only on the
operator's machine is an unverifiable claim, so an armed run refuses rather than
publishing one — the counted series is the one that cannot be replayed.

The submission repos are GENERATED exports: their ``main`` is the agent tree and
never contains workspace hashes. The workspace history is mirrored onto
``workspace-history``, which is where these commits resolve, so that is the ref
we check.

Both the remote lookup and the ancestry test are injected: the check must be
unit-testable without a network, and a live run supplies git-backed ones.
"""

MIRROR_REF = "workspace-history"
UNKNOWN_COMMIT = "unknown"


def check_published(commit: str, repos: dict, ls_remote, is_ancestor) -> dict:
    """Report whether ``commit`` is reachable from ``MIRROR_REF`` in every repo.

    ``ls_remote(url, ref) -> sha | None`` and ``is_ancestor(a, b) -> bool | None``
    where None means UNDECIDABLE — typically the remote tip is an object we do
    not hold. Undecidable is never reported as published: the whole point is to
    refuse a claim we cannot stand behind.
    """
    urls = sorted({url for url in (repos or {}).values() if url})
    if not urls:
        return {"published": False, "detail": "no role repositories configured", "checked": {}}
    if not commit or commit == UNKNOWN_COMMIT:
        return {"published": False, "detail": f"playing commit is {commit!r}", "checked": {}}
    checked, problems = {}, []
    for url in urls:
        tip = ls_remote(url, MIRROR_REF)
        if not tip:
            checked[url] = None
            problems.append(f"{url} has no {MIRROR_REF} ref")
            continue
        reachable = is_ancestor(commit, tip)
        checked[url] = reachable
        if reachable is None:
            problems.append(f"{url} tip {tip[:12]} is not an object we hold — undecidable")
        elif not reachable:
            problems.append(f"{commit[:12]} not reachable from {url} {MIRROR_REF}")
    return {
        "published": not problems,
        "detail": "; ".join(problems),
        "checked": checked,
    }


def git_ls_remote(url: str, ref: str) -> str | None:  # pragma: no cover (network)
    """The remote sha for ``ref``, or None. Network boundary — kept thin."""
    import subprocess
    try:
        out = subprocess.run(["git", "ls-remote", url, ref], capture_output=True,
                             text=True, timeout=30, check=False).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return out.split("\t")[0] if out else None


def git_is_ancestor(commit: str, tip: str) -> bool | None:  # pragma: no cover (git)
    """True/False, or None when ``tip`` is not an object we hold (undecidable)."""
    import subprocess
    try:
        known = subprocess.run(["git", "cat-file", "-e", f"{tip}^{{commit}}"],
                               capture_output=True, timeout=15, check=False).returncode
        if known != 0:
            return None
        return subprocess.run(["git", "merge-base", "--is-ancestor", commit, tip],
                              capture_output=True, timeout=15, check=False).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None
