# PRD — Cloud Tunnel & Deployment

> Dedicated PRD (guideline §1.3). **Build stage:** 5 (TODO slice 5.1). Ground
> truth: assignment §10, league SPEC Appendix D; `CLAUDE.md` §36.

## 1. Background

Locally the two peers talk over `127.0.0.1` (thief 8801 / police 8802). To play a
peer from another team they must be reachable over the public internet. Each peer
stays a plain FastMCP HTTP server behind a **public tunnel**; only the tunnel
configuration changes, never the application's security.

## 2. Requirements (FR-16)

- Support a **local** mode (default) and a documented **public-tunnel** mode.
- A **pre-match connectivity probe** makes a harmless FastMCP call through the
  opponent's public URL before the game starts.
- Handle the tunnel **HTTP-421** issue at the tunnel, not in code — FastMCP's
  DNS-rebinding protection stays intact.
- Public endpoints use HTTPS + token auth (the tunnel terminates TLS); raw
  Ollama/LLM ports are never exposed.

## 3. Deployment modes

- **Local:** `network.opponent_url = http://127.0.0.1:<other_port>/mcp`. Start
  order is irrelevant (the client retries until the peer is up).
- **Public tunnel:** the peer binds `127.0.0.1:<my_port>`; a tunnel maps a public
  HTTPS URL to it. Set `network.opponent_url` to the opponent's public tunnel URL.

## 4. The HTTP-421 fix (SPEC Appendix D)

FastMCP's streamable-HTTP server rejects requests whose `Host` header is not its
bind address — which is every request arriving through a tunnel. **Fix at the
tunnel** (never weaken the server):

- **Cloudflare named tunnel:** `originRequest.httpHostHeader: 127.0.0.1:<port>`.
- **ngrok:** `--host-header=rewrite`.

## 5. Connectivity probe (`infra/connectivity.py`)

`probe_opponent(opponent, timeout=10.0) -> bool` opens a FastMCP `Client` to the
opponent and lists its tools (a harmless call that enqueues nothing). Returns True
if the endpoint answers in time, False on any error/timeout. `opponent` is a URL
(real HTTP) or a FastMCP object (in-memory, for tests). Run it as a pre-match
checklist item: "does your public URL answer a tool call?" catches a mis-configured
tunnel in seconds.

## 6. Alternatives considered

- Weakening FastMCP's DNS-rebinding check to accept tunnel Hosts → **rejected**
  (security regression; the fix belongs at the tunnel).
- A dedicated `ping` tool → **rejected**; `list_tools` is already a harmless,
  side-effect-free reachability check.

## 7. Success criteria & tests

The probe returns True against a reachable (in-memory) server and False against an
unreachable URL, within the timeout. Tunnel config is documented and reproducible.
Tests: `test_connectivity` (in-memory reachable; refused URL). A live cross-tunnel
run is manual (Stage-5 acceptance, AC12).
