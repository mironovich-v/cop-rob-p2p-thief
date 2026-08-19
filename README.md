# Cop-Thief P2P — thief agent (vm__fabi)

Generated export of the **thief** peer. Self-contained: vendors the canonical
`cop_thief_core` (see `core_manifest.json` for its source commit + hash).

```bash
uv sync
uv run pytest tests
uv run python -m thief_agent --config config/thief
```

- Canonical workspace: https://github.com/mironovich-v/cop-rob-p2p
- Sibling (police) repo: https://github.com/mironovich-v/cop-rob-p2p-police

Do not edit vendored `cop_thief_core` here — change it in the workspace and
re-run `scripts/export_repos.py`. No secrets are included; copy `.env-example`
to `.env` locally for Gmail/LLM/tunnel credentials.
