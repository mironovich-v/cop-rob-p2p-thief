# Assignment: Distributed Cop–Thief P2P Agent System

## 1. Your role

Act as the senior engineer responsible for designing and implementing the final project described in the supplied official assignment and interoperability kit.

The result must be a reliable, testable distributed system, not merely a game simulation or a pair of prompts. Two autonomous peers must be able to play against independently implemented peers from other student teams over FastMCP, preserve private local state, audit one another, and settle on byte-identical results.

Do not begin by writing a large amount of code. First read the sources in the order below, extract the requirements, identify conflicts, and create a staged implementation plan. Then implement in small, testable increments.

---

## 2. Supplied sources and authority order

Read these files in this order:

1. `official/police_thief_p2p.pdf`
2. `interop/README.md`
3. `interop/SPEC.md`
4. `interop/verify_vectors.py`
5. `interop/examples/sample_exchange.md`
6. `interop/vectors/*.json`
7. `interop/gen_vectors.py`

Use the following authority hierarchy.

### 2.1 Official assignment authority

`official/police_thief_p2p.pdf` is authoritative for:

- mandatory game rules and minimum numeric parameters;
- the hidden-position and local-truth model;
- FastMCP/P2P architecture;
- required agent behavior;
- strategy and LLM responsibilities;
- GUI, replay, reliability, audit, league, Gmail and submission requirements;
- the required configuration, logs and result artifacts;
- the two-repository submission requirement.

Within the official book, follow its stated hierarchy: the binding parameter table and consolidated mandatory-rules appendix outrank illustrative prose, diagrams and code snippets.

### 2.2 Interoperability authority

`interop/SPEC.md` is the agreed cross-team byte-level interoperability contract. It complements rather than replaces the official assignment.

For the explicitly listed interoperability surfaces, implement the constructions in `interop/SPEC.md`, even where illustrative passages in the book disagree. The team has deliberately selected these constructions so independently implemented peers can start, audit and settle games successfully.

The interoperability kit is authoritative for:

- canonical JSON bytes;
- per-step commit–reveal preimages;
- agreement signatures;
- `game_uid` derivation;
- reference-compatible pheromone calculations;
- report canonicalization and consensus-signature bytes;
- the distinction between mandatory CORE behavior and opt-in ENH behavior.

Do not use the kit to weaken or replace any mandatory game, league, reporting or submission rule from the official assignment.

### 2.3 Executable contract

For interoperability behavior, use this precedence:

1. `interop/SPEC.md` defines intent and scope.
2. `interop/verify_vectors.py` defines the reference behavior.
3. `interop/vectors/*.json` defines expected observable results.
4. `interop/examples/sample_exchange.md` is a worked example, not an independent source of rules.
5. `interop/gen_vectors.py` regenerates fixtures and documents provenance; it is not production code.

Never modify a vector merely to make the implementation pass. A mismatch means the production implementation is wrong unless a documented source-version change proves otherwise.

---

## 3. Reading strategy

Do not treat all supplied files as undifferentiated prose.

- Read the official PDF for the complete assignment.
- Read `README.md` for orientation.
- Read `SPEC.md` carefully and turn every CORE rule into a production test.
- Inspect `verify_vectors.py` as an oracle, but do not import it from production code.
- Run the vector checker instead of manually copying expected hashes.
- Use the JSON files as fixtures in tests.
- Use the worked exchange for an end-to-end protocol test.
- Treat all ENH sections and vectors as disabled-by-default optional features.

Before implementation, create:

- `docs/requirements_matrix.md`: each requirement, source location, status, code owner and test;
- `docs/decisions.md`: contradictions, chosen interpretation and justification;
- `docs/architecture.md`: components, trust boundaries, runtime processes and data flow;
- `PLAN.md`: staged milestones and acceptance criteria;
- `TODO.md`: an actively maintained implementation checklist.

Also create the PRD documents required by Chapter 10 of the official assignment. Extract their exact required names and contents from the PDF rather than guessing. At minimum, the PRDs must cover game state, MCP protocol, pre-game agreement, player agents, commit–reveal, logging/audit/reporting and email reporting.

---

## 4. Product goal

Build a role-agnostic Cop–Thief agent framework with two independently runnable applications:

- Cop/Police peer;
- Thief peer.

Each peer must:

- run as its own operating-system process;
- maintain only its own private position and private local truth;
- have separate configuration, credentials, logs and runtime state;
- expose FastMCP tools as a server;
- call the opponent's FastMCP tools as a client;
- function without shared memory, shared mutable state or access to the other role's secrets;
- play against a peer implemented by another team, not just its sibling implementation;
- fail safely under malformed input, timeouts, duplicate messages and network interruptions;
- produce complete, auditable artifacts for replay and reporting.

A central game server, central judge or shared authoritative board state is forbidden.

---

## 5. Shared framework without manual duplication

The official assignment requires two final GitHub repositories. It does not justify maintaining two independent copies of the framework by hand.

Use one canonical development workspace and one canonical implementation of all shared infrastructure. Separate role-specific behavior through interfaces, dependency injection and configuration.

Recommended conceptual layout:

```text
workspace/
├── src/cop_thief_core/
│   ├── domain/          # board, rules, actions, scoring, scent
│   ├── interop/         # canonical bytes, hashes, UIDs, report signatures
│   ├── protocol/        # schemas and MCP-facing messages
│   ├── orchestration/   # state machine, deadlines, retries, watchdog
│   ├── audit/           # logs, reveal, verification, replay
│   ├── reporting/       # result derivation and Gmail draft creation
│   └── llm/             # verbal hint providers only
├── src/police_agent/    # police strategy and entry point
├── src/thief_agent/     # thief strategy and entry point
├── interop/             # supplied kit, retained as external test material
├── tests/
├── scripts/export_repos.py
└── docs/
```

At submission time, generate two self-contained release trees:

```text
dist/police-agent/
dist/thief-agent/
```

Each exported repository must contain everything required to install, test and run that role. Neither final repository may depend at runtime on cloning the other repository or on a private third shared-code repository.

The shared core may appear as a generated vendored snapshot in both release repositories, but it must be maintained in only one canonical source location. Add an automated drift check recording the core source commit/hash in both exports.

Do not:

- manually edit two copies of shared modules;
- let either role import the other role's private package;
- share a state file, singleton, database or in-memory object between running peers;
- create a hidden local central engine that knows both true positions;
- make final repositories depend on an unavailable private package.

---

## 6. Required implementation layers

### 6.1 Pure deterministic domain layer

Implement game state and transitions without networking, FastMCP, LLM calls, Gmail or GUI dependencies.

The official assignment is the authority for:

- board dimensions and coordinates;
- allowed movement and staying in place;
- barriers and placement restrictions;
- turn order and sub-game lifecycle;
- capture, immobilization, survival and other terminal states;
- scoring;
- six-sub-game series behavior and league rules;
- all minimum parameter values.

Numeric values must be configuration-driven and validated against official minimums. Never silently lower a required minimum.

The domain layer must be deterministic and exhaustively unit tested, including boundary, invalid-action and terminal-state cases.

### 6.2 Local-truth boundary

Represent public, private and inferred state separately.

At minimum distinguish:

- private self position and role-private strategy state;
- public agreed configuration and barriers;
- received scent observations;
- received natural-language hints;
- opponent belief distribution;
- sent/received commitments;
- audit-only revealed records available only after the reveal phase.

Make it structurally difficult for a strategy or GUI to access forbidden opponent truth. A live GUI must show only local knowledge; complete truth is permitted only in retrospective replay after audit material is available.

### 6.3 FastMCP peer protocol

Each runtime is both:

- a FastMCP server exposing the required tools;
- a FastMCP client calling the opponent's public endpoint.

Derive the exact required MCP tools, request/response schemas and game flow from the official assignment. Define typed schemas and reject unknown, malformed, stale, duplicated or out-of-order messages safely.

Network handlers must not directly mutate domain state without validation. Route every accepted message through the orchestrator/state machine.

### 6.4 Orchestrator and reliability

Implement an explicit finite-state machine for at least:

- startup and configuration loading;
- network readiness;
- pre-game declaration and agreement;
- per-sub-game setup;
- active turns;
- capture/win claims and responses;
- audit/reveal;
- result consensus;
- report creation;
- completion, abort and technical-failure states.

Add:

- idempotency keys or equivalent duplicate protection;
- monotonically validated step/sub-game identifiers;
- timeouts and bounded retries;
- watchdog/deadline tracking;
- Gatekeeper/rate limiting as required by the official book;
- persistent state sufficient for safe restart or explicit fail-closed behavior;
- structured error reasons rather than ambiguous exceptions.

### 6.5 Strategy layer

The legal-action set must be computed by deterministic code. Strategy selects only from legal actions.

Provide separate Police and Thief strategy interfaces and baseline heuristic implementations. Strategy may use:

- current legal actions;
- known barriers;
- received and decayed scent map;
- probabilistic belief map;
- opponent hint text and estimated reliability;
- historical observations and outcomes.

The LLM must not decide whether a move is legal and must never be the sole component keeping the game operational.

### 6.6 LLM verbal layer

Use the LLM only for the free-language/psychological layer described by the official assignment, such as producing or interpreting hints.

Provide a provider abstraction with at least:

- deterministic template/offline provider for tests and fallback;
- optional local provider;
- optional cloud provider configured externally.

No unit or integration test may require a real cloud model. Validate word limits and sanitize output before placing it on the wire or into a committed record.

### 6.7 Audit, replay and GUI

Persist enough exact data to:

- verify commitments after reveal;
- detect missing, duplicated or reordered records;
- reproduce state transitions;
- derive terminal outcomes and scores mechanically;
- generate required game artifacts;
- display a retrospective replay with integrity status.

The replay verifier must not trust claimed totals when they can be derived from logged sub-game events.

Implement the live GUI and replay viewer required by the official assignment, but keep GUI code outside the domain and protocol layers.

### 6.8 Gmail reporting

Implement Gmail reporting according to the official assignment, including OAuth/configuration requirements and required filenames/attachments.

Default to draft or dry-run behavior. Tests must never send real mail.

The production path must preserve the exact report bytes required by the interoperability contract. Do not hash one serialization and email another.

---

## 7. Mandatory interoperability contract

All CORE behavior below is mandatory.

### 7.1 Compact canonical JSON

For ordinary protocol hashes:

```python
json.dumps(
    obj,
    sort_keys=True,
    ensure_ascii=False,
    separators=(",", ":"),
).encode("utf-8")
```

Requirements:

- keys sorted recursively by the serializer;
- no insignificant whitespace;
- native UTF-8 for Hebrew, emoji and all non-ASCII text;
- Python-compatible shortest round-trip representation for floats;
- no pretty-printing before hashing.

Implement one production canonicalization function and reuse it consistently.

### 7.2 Commit–reveal

Use:

```text
SHA256(UTF8(canonical_json(payload) + "|" + nonce))
```

The nonce is pipe-appended after the canonical JSON string. It is not inserted into the hashed object, and the preimage is not merely `nonce|move`.

Each peer seals its own record. During audit, the opponent re-hashes the revealed payload and nonce using its own implementation.

Include step, sub-game and role identifiers in production sealed records so stale/replayed records can be rejected. The exact private payload may be richer than another team's payload; cross-team compatibility depends on canonical re-hashing of the revealed payload, not identical private schemas.

### 7.3 Terms signature

Use the same construction over agreed terms:

```text
SHA256(UTF8(canonical_json(terms) + "|" + nonce))
```

The peer must refuse to start when:

- terms are not value-equal;
- a signature does not verify;
- required fields are absent;
- a mandatory minimum is violated;
- the selected protocol/core version is incompatible.

### 7.4 Game UID

Derive:

```text
UUID(
  SHA256(
    UTF8(canonical_json(terms) + "|" + "|".join(sorted([group_a, group_b])))
  )[0:16]
)
```

Group order must not affect the result.

### 7.5 Pheromone/scent reference behavior

Implement the reference-compatible behavior pinned by the vectors:

```text
half = grid_size // 2
falloff = intensity / (half + 1)
value = round(max(0, intensity - falloff * ChebyshevDistance), 3)
```

Transmit only positive in-bounds values in the `"r,c" -> intensity` representation.

Per-step decay:

```text
round(max(0, value - decay), 3)
```

This deliberately follows the agreed reference-compatible construction documented in `interop/SPEC.md`, not conflicting illustrative pheromone prose in the book.

### 7.6 Report consensus signature

This is deliberately different from compact canonical JSON.

Serialize the report before inserting the signature key using:

```python
json.dumps(report, sort_keys=True, ensure_ascii=False)
```

This uses default spaced separators. Hash those UTF-8 bytes with SHA-256, then insert the signature under the exact key required by the report schema.

Verification must:

1. remove/pop the signature field;
2. re-serialize with the spaced form;
3. re-hash;
4. compare securely.

Do not accidentally use the compact serializer for this signature.

### 7.7 Exact emailed bytes

The final email body must be the exact canonical bytes that the protocol says were agreed/hashed. Do not pretty-print or independently re-serialize it during MIME construction.

### 7.8 CORE vector adoption

The project must retain the supplied interoperability kit under `interop/` and pass:

```bash
cd interop
python verify_vectors.py
```

More importantly, add project tests that load the same CORE JSON fixtures and exercise production functions. These tests must not call `verify_vectors.py` reference functions as the implementation under test.

CORE fixtures:

- `canonical_json.json`
- `commit_reveal.json`
- `terms_signature.json`
- `game_uid.json`
- `pheromone.json`
- `report_consensus.json`

Run regeneration in CI and fail on fixture drift:

```bash
cd interop
python gen_vectors.py
git diff --exit-code -- vectors/
python verify_vectors.py
```

### 7.9 Optional ENH behavior

The following are optional and disabled by default:

- transcript interlock DAG (`prev`, `prev_recv`);
- joint-seed coin flip;
- deterministic randomized start derivation;
- synchronized scheduling;
- demo staging and passive league services.

Never enable an enhancement unilaterally. Enable it only when both peers:

- advertise support;
- explicitly select it in the shared terms/configuration;
- sign the exact selected configuration;
- pass the corresponding ENH vectors where applicable.

A peer that does not support an optional enhancement must still be able to play the CORE protocol.

---

## 8. Configuration and protocol negotiation

Create:

- one shared signed `config/game.json` constitution per match;
- separate private configuration for Police and Thief;
- explicit protocol and interop-kit version fields;
- explicit feature flags for all optional enhancements;
- endpoint, timeout, LLM, strategy and email settings outside the shared rules where appropriate.

Do not put secrets, OAuth tokens or private strategy parameters in the shared configuration or Git history.

Configuration validation must be deterministic. Store the exact agreed configuration with match artifacts and in the appropriate repository as required by the official assignment.

---

## 9. Testing requirements

Use `uv`, `pytest` and `ruff`. Keep tests deterministic and offline unless explicitly marked as manual/live.

Required test groups:

### 9.1 Unit tests

- board and coordinate rules;
- every legal/illegal action category;
- barriers;
- terminal-state and scoring derivation;
- scent emission, merge and decay;
- belief-map updates;
- compact and spaced serializers;
- commitments and reveal verification;
- terms signatures and game UIDs;
- report derivation and exact bytes;
- state-machine transitions;
- duplicate/stale/out-of-order rejection;
- strategy always returns a legal action;
- LLM output validation and deterministic fallback.

### 9.2 Production conformance tests

For every CORE fixture, call production code and reproduce the committed expected value exactly, including Hebrew and emoji cases.

### 9.3 Local integration tests

Run Police and Thief in separate processes with separate temporary directories and no shared mutable state. Exercise:

- agreement;
- several legal turns;
- scent exchange;
- a claim path;
- reveal/audit;
- result consensus;
- report/draft generation.

### 9.4 Adversarial protocol tests

Test at least:

- invalid signature;
- modified reveal payload;
- incorrect nonce;
- non-ASCII serialization mismatch;
- duplicate message;
- stale step;
- skipped step;
- invalid role;
- malformed scent map;
- timeout/retry;
- conflicting result claim;
- restart or crash at sensitive phases;
- unsupported optional feature.

### 9.5 Cross-implementation acceptance test

Before declaring interop-ready:

1. call the peer through a real public tunnel;
2. exchange a complete test game with another implementation or conformant sparring peer;
3. feed each side's revealed log into the other side's verifier;
4. confirm zero false tamper forfeits;
5. confirm both sides independently derive byte-identical result/report bytes.

A match against only the sibling implementation is insufficient evidence of interoperability.

---

## 10. Tunnel and deployment requirements

Support local development and a documented public-tunnel mode.

Include a pre-match connectivity probe that makes a harmless FastMCP tool call through the public URL before the game starts.

Document the known Host-header issue from `interop/SPEC.md` Appendix D:

- Cloudflare named tunnel: configure `originRequest.httpHostHeader` for the bound local host/port;
- ngrok: use host-header rewrite as appropriate.

Do not weaken FastMCP security checks in application code merely to work around tunnel configuration.

---

## 11. Deliverables

Produce and maintain all files required by the official assignment. At minimum include:

- complete source code;
- tests;
- shared and private configuration templates;
- required PRDs;
- `PLAN.md`, `TODO.md`, `PROMPTS.md` and decision/requirements documentation;
- live GUI;
- replay and verification tool;
- logging and required JSON artifacts;
- Gmail draft/reporting integration;
- setup and run instructions;
- academic README content required by the official book;
- screenshots/evidence required by the submission checklist;
- annotated submission tag instructions;
- deterministic export process for the two final repositories.

Each exported role repository must:

- install and run independently;
- contain its role entry point and required shared core snapshot;
- have its own README and configuration template;
- cross-link the other repository as required;
- identify the canonical core source commit/hash;
- pass its own tests after export;
- contain no credentials or generated private match secrets.

---

## 12. Implementation discipline

Use small milestones and keep the repository green.

For each milestone:

1. update the relevant PRD/plan;
2. add failing tests;
3. implement the minimum coherent behavior;
4. run `ruff` and the full test suite;
5. update `TODO.md` and `docs/requirements_matrix.md`;
6. record any compliance decision in `docs/decisions.md`.

Do not hide incomplete behavior behind broad mocks and call the milestone complete. Network, LLM, Gmail and tunnel boundaries may be mocked in automated tests, but the domain, protocol, crypto, audit and serialization logic must be real.

Do not change an agreed wire construction casually. Any protocol change requires:

- a version bump;
- updated SPEC/documentation;
- new or updated vectors;
- regeneration proof;
- backward-compatibility decision;
- cross-team coordination.

---

## 13. Definition of done

The project is complete only when all of the following hold:

- every mandatory official requirement is mapped to implementation and evidence;
- every CORE vector passes against production code;
- the supplied vector generator produces no drift;
- Police and Thief run in separate processes and separate private directories;
- neither peer can access the other's private truth through imports, files or shared memory;
- local end-to-end games finish and audit cleanly;
- a public FastMCP endpoint works through the documented tunnel configuration;
- at least one complete cross-implementation game audits and settles cleanly;
- result totals are derived rather than trusted;
- emailed/draft report bytes are exactly the agreed bytes;
- optional ENH features are off by default and negotiation-gated;
- live GUI respects local truth;
- replay verifies integrity and reconstructs the match;
- both exported repositories are self-contained, testable and traceable to one canonical shared core;
- required README, PRDs, artifacts and submission tag are present.

---

## 14. First response and first work product

After reading the supplied sources, your first response must contain:

1. a concise understanding of the project;
2. the source/authority hierarchy you will follow;
3. the main conflicts you identified, including commit construction, pheromone behavior and report serialization;
4. a proposed component architecture;
5. a staged implementation plan;
6. a list of values that still require user-specific configuration, such as team identity, repository URLs, email addresses, tunnel provider and LLM mode.

Then create the documentation skeleton and begin with the deterministic domain and CORE interoperability tests before implementing live networking, GUI or Gmail.

Do not ask the user to restate information already present in the supplied files. Ask only for genuinely missing personal/team configuration or a decision about optional ENH features.
