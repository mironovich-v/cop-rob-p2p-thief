#!/usr/bin/env bash
# Fetch or update the cross-team league interoperability kit.
#
# The kit is owned by ANOTHER team and may be updated independently, so we do NOT
# vendor its files (it stays git-ignored). This clones it if missing, or pulls the
# latest, into ./copthief-league-protocol so our conformance tests can run against
# the CORE vectors. See docs/INTEROP.md.
set -euo pipefail

REPO_URL="https://github.com/Imreec/copthief-league-protocol"
DEST="copthief-league-protocol"

if [ -d "$DEST/.git" ]; then
  echo "Updating $DEST ..."
  git -C "$DEST" pull --ff-only
else
  echo "Cloning $REPO_URL ..."
  git clone "$REPO_URL" "$DEST"
fi

echo "League kit ready at ./$DEST (commit $(git -C "$DEST" rev-parse --short HEAD))"
