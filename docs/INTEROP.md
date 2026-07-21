# Interoperability kit (external — not vendored)

The cross-team league protocol and conformance vectors live in a **separate repo
owned by another team**, which may be updated independently. We therefore do
**not** commit its files here (it is git-ignored); we track only the link and
fetch it locally.

- **Upstream:** https://github.com/Imreec/copthief-league-protocol
- **Known-good commit at adoption:** `c12e4e9`
- **Local path (git-ignored):** `./copthief-league-protocol/`

## Fetch / update

```bash
scripts/fetch_interop.sh
```

Clones the kit if missing, or `git pull --ff-only` to pick up the other team's
updates. Our CORE-vector conformance tests (`tests/conformance/`) load the
fixtures from `./copthief-league-protocol/vectors/` and exercise **our**
production functions — never the kit's `verify_vectors.py` reference code.

## Rules (kit SPEC + assignment §7)

- **Never modify a vector** to make our code pass; a mismatch means our code is
  wrong unless a documented source-version change proves otherwise.
- The constructions we must match byte-for-byte are pinned in `CLAUDE.md` §36.3:
  compact canonical JSON, commit-reveal, terms signature, `game_uid`, pheromone
  math, and the (spaced) report consensus signature.
- ENH vectors are opt-in and negotiation-gated; a CORE-only peer must still play.
