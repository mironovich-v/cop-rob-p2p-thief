#!/usr/bin/env bash
# Republish BOTH submission repos from the current workspace main.
#
# Run this after EVERY merge to main. The submission repos are generated
# exports: they do not track main, so between a merge and this script the
# commit we declare on the wire is unresolvable in the repos we submit. The
# armed-run gate (shared/provenance.py) refuses a counted series in that state,
# which is a safety net — not a substitute for keeping them current.
#
# Each repo gets two refs, and they mean different things:
#   main               the exported agent tree (its own history, no workspace hashes)
#   workspace-history  a mirror of workspace main — where playing commits resolve
#
# Usage: uv run bash scripts/publish_submissions.sh
set -euo pipefail

cd "$(dirname "$0")/.."
COMMIT="$(git rev-parse HEAD)"
SHORT="$(git rev-parse --short HEAD)"

if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "refusing: workspace has uncommitted tracked changes — publish a clean tree" >&2
  exit 1
fi

echo "==> exporting from ${SHORT}"
uv run python scripts/export_repos.py

for ROLE in police thief; do
  URL="https://github.com/mironovich-v/cop-rob-p2p-${ROLE}"
  DIR="dist/${ROLE}-agent"
  echo "==> ${ROLE}: ${URL}"
  (
    cd "$DIR"
    git init -q
    git remote add origin "$URL" 2>/dev/null || git remote set-url origin "$URL"
    git fetch -q origin main
    git update-ref refs/heads/main FETCH_HEAD
    git symbolic-ref HEAD refs/heads/main
    git reset -q
    git add -A
    # The exported .gitignore is the workspace one, which hides results/* AND
    # logs/* — so `git add -A` SILENTLY skips every evidence file under them
    # and publishes a repo missing exactly what the export shipped. Force-add
    # both, exactly as the workspace does for the same files (results found
    # 2026-08-19; logs found 2026-08-24 — the export fix #114 alone was not
    # enough, the ignore ate the files again one layer later).
    for EVIDENCE in results logs; do
      [ -d "$EVIDENCE" ] && git add -f "$EVIDENCE"
    done
    if git diff --cached --quiet; then
      echo "    tree unchanged — nothing to commit"
    else
      git -c user.name="mironovich-v" -c user.email="mironovichvasily@gmail.com" \
        commit -q -m "Republish ${ROLE} submission tree from workspace ${COMMIT}"
      git push -q origin main
      echo "    main -> $(git rev-parse --short HEAD)  (results files: $(git ls-files results | wc -l), logs files: $(git ls-files logs | wc -l))"
    fi
  )
  git push -q "$URL" main:workspace-history
  echo "    workspace-history -> ${SHORT}"
done

echo "==> verifying the playing commit resolves in both repos"
uv run python -c "
from cop_thief_core.orchestration.sealing import playing_commit
from cop_thief_core.shared.provenance import check_published, git_ls_remote, git_is_ancestor
repos = {'cop': 'https://github.com/mironovich-v/cop-rob-p2p-police',
         'thief': 'https://github.com/mironovich-v/cop-rob-p2p-thief'}
st = check_published(playing_commit(), repos, git_ls_remote, git_is_ancestor)
print('    published:', st['published'], '|', st['detail'] or 'reachable in both')
raise SystemExit(0 if st['published'] else 1)
"
