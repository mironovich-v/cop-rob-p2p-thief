# COSTS.md — AI / Runtime / Review Cost Ledger

> Project: **vm__fabi** Cop-Thief P2P. Tracks AI-assisted development and expensive
> operations, per guideline §10.3 and `CLAUDE.md` §8. **Standing rule: one ledger
> row per PR.** Billing is via a Claude Code plan/subscription, so exact per-call
> token counts are usually unavailable — we record practical proxies (session
> count, wall-clock, review burden, subagent tokens when reported).

## Ledger

| Date | PR / Phase | Branch | Commit | Model · Effort | Task | Cost proxy | Accepted |
|------|-----------|--------|--------|----------------|------|-----------|----------|
| 2026-07-21 | Setup | phase-0-agent-control | ff97425 | Opus 4.8 (1M) · xhigh | Read guidelines + book PDF + reference repo via 5 explorer subagents; extract ground truth; bootstrap scaffold | ~1 session; ~200k subagent tokens | merged |
| 2026-07-21 | PR #1 | docs-prd-requirements | db889f0 | Opus 4.8 · high | Master PRD + requirements matrix + 19-PRD catalog | ~0.3 session | merged |
| 2026-07-21 | PR #2 | docs-plan-architecture-decisions | 6a9792f | Opus 4.8 · high | PLAN (C4) + architecture + decisions (ADRs) | ~0.3 session | merged |
| 2026-07-21 | PR #3 | docs-todo-and-process | 3421a60 | Opus 4.8 · high | TODO breakdown + PROMPTS + REVIEW_POLICY | ~0.2 session | merged |
| 2026-07-21 | PR #4 | stage-1-design-prds | a833fbd | Opus 4.8 · high | Stage-1 design PRDs | ~0.2 session | merged |
| 2026-07-21 | PR #5 (1.1) | stage-1-board | 3badbaa | Opus 4.8 · high | board + constants (TDD, cov 92%) | ~0.2 session | merged |
| 2026-07-21 | PR #6 (1.2) | stage-1-own-state | e8e7b07 | Opus 4.8 · high | own_state (TDD, cov 96%) | ~0.2 session | merged |
| 2026-07-21 | PR #7 (1.3) | stage-1-rules | e432455 | Opus 4.8 · high | rules (TDD, cov 96%) | ~0.1 session | merged |
| 2026-07-22 | PR #8 (1.4) | stage-1-scoring | 4e06278 | Opus 4.8 · high | scoring (TDD, cov 97%) | ~0.2 session | merged |
| 2026-07-22 | PR #9 (1.5) | stage-1-config | 84bd6a3 | Opus 4.8 · high | config loader + templates (TDD, cov 98%) | ~0.3 session | merged |
| 2026-07-22 | Stage-2 PRDs | stage-2-design-prds | ea6d59f | Opus 4.8 · high | 5 Stage-2 mechanism PRDs | ~0.3 session | merged |
| 2026-07-22 | Process docs | docs-process-and-tracking | f29a6a0 | Opus 4.8 · high | RTS acceptance, open decisions, phase plan, task checkboxes, per-PR PROMPTS/COSTS | ~0.2 session | merged |
| 2026-07-22 | PR (2.1) | stage-2-protocol | 672db1c | Opus 4.8 · high | protocol wire schemas (TDD, cov 98%) | ~0.2 session | merged |
| 2026-07-22 | PR (2.2) | stage-2-gatekeeper | 1b8bd95 | Opus 4.8 · high | gatekeeper + token-bucket rate limiter (TDD, cov 98%) | ~0.2 session | merged |
| 2026-07-22 | PR (2.3a) | stage-2-interop-primitives | 48ba793 | Opus 4.8 · high | canonical JSON + hashing + game_uid; 4 CORE vectors pass from our code | ~0.3 session | merged |
| 2026-07-22 | PR (2.3b) | stage-2-negotiation | 1c5d5e8 | Opus 4.8 · high | Negotiation (sign/verify), terms_from_config, data-driven App-F minimum-validation | ~0.2 session | merged |
| 2026-07-22 | PR (2.4) | stage-2-mcp-server | 58c49e6 | Opus 4.8 · high | FastMCP server (4 tools) + McpTransport client; in-memory Client(server) tests (no network) | ~0.3 session | merged |
| 2026-07-23 | PR (3.1) | stage-3-belief | e610f1d | Opus 4.8 · high | Bayesian belief map (observe/diffuse/exclude); Option-A reorder (ADR-16) | ~0.2 session | merged |
| 2026-07-23 | PR (3.2) | stage-3-brains | 312ce93 | Opus 4.8 · high | BrainBase + Thief/Police brains + config-driven strategy seam; move is pure Python | ~0.2 session | merged |
| 2026-07-23 | PR (4.1) | stage-4-smell | 5da8f3d | Opus 4.8 · high | SmellField (radial emit, subtractive decay, wire); pheromone CORE vector passes | ~0.2 session | merged |
| 2026-07-23 | PR (2.5a) | stage-2-runtime-handshake | ada2590 | Opus 4.8 · high | sealing helpers + handshake + shared FakeTransport fixture (queue-pair, no network) | ~0.3 session | merged |
| 2026-07-23 | PR (2.5b) | stage-2-runtime | a53ea71 | Opus 4.8 · high | PeerRuntime FSM + turn_handler + summary/audit; two-peer in-process match passes | ~0.4 session | merged |
| 2026-07-23 | PR (2.6) | stage-2-sdk-series | 726275f | Opus 4.8 · high | SimulationSdk.run_peer + series runner (role alternation); closes Stage 2 | ~0.2 session | merged |
| 2026-07-23 | PR (4.2) | stage-4-trash-talk | 7c3bc8d | Opus 4.8 · high | template trash-talk (landmarks, bluff, word-cap) + resolve_trash_talk; wired into resolve_brain | ~0.2 session | merged |
| 2026-07-23 | PR (4.3) | stage-4-llm-providers | 7c01e84 | Opus 4.8 · high | LlmTrashTalk (every_n_steps, deadline/parse fallback) + cli/ollama/api askers; mock-tested | ~0.2 session | merged |
| 2026-07-23 | PR (5.1) | stage-5-tunnel | 808f232 | Opus 4.8 · high | connectivity probe + PRD_cloud_tunnel (Host-header/tunnel docs); closes Stage 5 | ~0.1 session | merged |
| 2026-07-23 | PR (6.1) | stage-6-sysinfo | e04f3bd | Opus 4.8 · high | sysinfo collect_spec + Step-0 host-spec sealed record (into runtime) + PRD_commit_reveal | ~0.2 session | merged |
| 2026-07-23 | PR (6.2) | stage-6-audit | 5118b6b | Opus 4.8 · high | adversarial audit test: tampered opponent log -> tamper_forfeit (honest peer wins) | ~0.1 session | merged |
| 2026-07-23 | PR (6.3) | stage-6-report-sig | d8e8347 | Opus 4.8 · high | report consensus signature (spaced) + PRD_interop_serialization; ALL 6 CORE vectors pass | ~0.2 session | merged |
| 2026-07-24 | PR (7.1) | stage-7-artifacts | acb0929 | Opus 4.8 · high | four JSON artifact builders (declaration/config/log/result) + schemas/helpers + PRD_logging_audit_reporting | ~0.2 session | merged |
| 2026-07-25 | PR (7.2) | stage-7-emit | 8f14f69 | Opus 4.8 · high | emit_series writes 4 artifacts to disk + wired into SDK.run_peer; cross-peer mutual-signature test | ~0.2 session | merged |
| 2026-07-25 | PR (7.3a) | stage-7-report-body | 7c6f320 | Opus 4.8 · high | official Hebrew emailed report (build_report) + exact-bytes report_body + PRD_email_reporting | ~0.2 session | merged |
| 2026-07-29 | PR (7.3b) | stage-7-gmail-send | ebfec0c | Opus 4.8 · high | raw-HTTPS Gmail send-only client + gatekeeper-routed EmailSender (draft/disabled default, no new deps) | ~0.2 session | merged |
| 2026-08-04 | PR (7.4a) | stage-7-gui-viewmodel | bc54c14 | Opus 4.8 · high | live-GUI view-model (event→window, game-mode classifier) + local-truth boundary test + PRD_gui_replay | ~0.2 session | merged |
| 2026-08-05 | PR (7.4b) | stage-7-runtime-events | 3e941cf | Opus 4.8 · high | runtime emits moved/game_over live event stream (additive) + event-stream integration test | ~0.1 session | merged |
| 2026-08-05 | PR (7.4c) | stage-7-gui-shell | df98916 | Opus 4.8 · high | live Tk shell (board_view/window/player/__main__) + display-guarded smoke test; `python -m cop_thief_core.gui` | ~0.2 session | merged |
| 2026-08-05 | PR (7.5a) | stage-7-replay-data | e805fde | Opus 4.8 · high | replay data layer: commit-reveal re-verify + both-trajectory reconstruction from revealed logs | ~0.2 session | merged |
| 2026-08-05 | PR (7.5b) | stage-7-replay-view | 143f867 | Opus 4.8 · high | Tk ReplayApp (--replay, both revealed trajectories, per-step commit verify) + smoke test | ~0.2 session | merged |
| 2026-08-05 | PR (7.6a) | stage-7-agent-cli | 24d19ee | Opus 4.8 · high | headless role CLI (agent_cli.run_role) filling police/thief __main__ stubs; SDK-delegating | ~0.1 session | merged |
| 2026-08-05 | PR (7.6b) | stage-7-export | 4252faf | Opus 4.8 · high | deterministic two-repo export (vendored core + drift manifest, no secrets); vendored suite runs standalone | ~0.2 session | merged |
| 2026-08-05 | PR (7.7a) | stage-7-email-wiring | 3242ec2 | Opus 4.8 · high | wire email step into SDK.run_peer (exact report_body, draft/disabled default) + end-to-end byte-path test | ~0.1 session | merged |
| 2026-08-05 | PR (7.7b) | stage-7-readme | c1d106c | Opus 4.8 · high | full academic README (install/run/architecture/config/security/credits) | ~0.1 session | merged |
| 2026-08-05 | PR (7.7c) | stage-7-rts-gate | bb57f65 | Opus 4.8 · high | RTS gate review (AC1–AC17 with evidence; 6-series verified) + docs/PROGRESS.md owner checklist | ~0.1 session | merged |
| 2026-08-05 | PR (7.8) | stage-7-robustness | bdfebd5 | Opus 4.8 · high | step-monotonic dedup (stale/dup/out-of-order, AC7) + fix latent caught-branch step-advance desync | ~0.2 session | merged |
| 2026-08-17 | PR (D8) | stage-8-plan | 152e747 | Fable 5 · high | league-kit resync analysis (2 reader agents + code cross-check) + Stage-8 plan, ADR-17..20, email-PRD re-scope | ~0.4 session | merged |
| 2026-08-17 | PR (docs) | docs-pairing-imreeyal | cf7b811 | Fable 5 · high | record imreeyal first-contact verbatim + disposition map; fold 8.10/8.11 into Stage-8; OD-4 resolved (deadline 2026-08-20) | ~0.1 session | merged |
| 2026-08-17 | PR (8.1) | stage-8-endings | 7a9c79a | Fable 5 · high | rule-46/47 enclosure endings + thief concession final (TDD; 10 tests incl. cornering integration) | ~0.2 session | merged |
| 2026-08-17 | PR (8.2) | stage-8-corroboration | 70ad429 | Fable 5 · high | cop-side capture corroboration (answer/concession, disputed_capture settlement, strict-parse-or-degrade) | ~0.2 session | merged |
| 2026-08-17 | PR (8.5) | stage-8-negotiate-extras | e4f5921 | Fable 5 · high | negotiate extras + locked-model declarations + opponent-group guard + response-body agreement (16 tests) | ~0.2 session | merged |
| 2026-08-17 | PR (8.10+8.11) | stage-8-transport | f080022 | Fable 5 · high | per-call timeout cap + config refusal; handshake re-push + door-gap patience; session-per-call documented | ~0.15 session | merged |
| 2026-08-17 | PR (8.3) | stage-8-delivery | ff9ec12 | Fable 5 · high | delivery contract: commit-keyed dedup, loud equivocation, reorder buffer, flood rule, deadline discipline | ~0.2 session | merged |
| 2026-08-17 | PR (8.6) | stage-8-wire-validation | 9381f65 | Fable 5 · high | wire value validation (turn_message refusal rows) + receive() refusal path before any state change | ~0.1 session | merged |
| 2026-08-17 | PR (8.4) | stage-8-audit-binding | 23a5e24 | Fable 5 · high | audit live-binding: disclosure bound to arrived commits + completeness (7 tests) | ~0.1 session | merged |
| 2026-08-17 | PR (8.7) | stage-8-league-fields | merged | Fable 5 · high | graded league fields + links.github + committed rule-52 ledger in settlement path (7 tests) | ~0.15 session | merged |
| 2026-08-17 | PR (8.8) | stage-8-email-gate | merged | Fable 5 · high | email body+attachment, reference subject, auto-fire, dry-run default, recipient-shaped double-arming gate (14 tests) | ~0.2 session | merged |
| 2026-08-17 | PR (8.9) | stage-8-conformance | merged | Fable 5 · high | behavior-table conformance sweep (4 vector tables driven by production code); kit oracle 125/125, zero drift | ~0.1 session | merged |
| 2026-08-17 | PR (8.12) | config-imreeyal-pairing | merged | Fable 5 · high | pairing config (constitution byte-identical, derived ids pinned), real member names, reply draft committed | ~0.1 session | merged |
| 2026-08-17 | PR (8.13) | fix-foreign-identity | merged | Fable 5 · high | §0 sparring pass (6/6, audits OK, ALL SETS AGREE) + fix: declaration tolerates foreign identity without spec | ~0.2 session + 2 live series runs | merged |
| 2026-08-17 | PR (7.9) | chore-ci-gate | c890a77 | Fable 5 · high | CI gate workflow (ruff, cov, conformance, kit oracle, drift check) + PROGRESS/matrix refresh (AC1 done) | ~0.05 session | merged |
| 2026-08-18 | PR (8.14) | config-nis-yar1-pairing | merged | Fable 5 · high | role-split opponent dialing + nis-yar1 pairing config (digest verified, ids pinned) + reply draft + league template | ~0.15 session | merged |
| 2026-08-18 | PR (8.15) | fix-env-loading | 6175a77 | Fable 5 · high | stdlib .env loader (auto-fire would have stranded no_credentials) + live token-refresh preflight | ~0.05 session | merged |
| 2026-08-18 | PR (docs) | docs-imreeyal-parity | 1f69d97 | Fable 5 · high | imreeyal round-2: parity FLIP (we are POLICE on odds), five scars verified in code, response draft + runbook fix | ~0.1 session | merged |
| 2026-08-18 | PR (8.14 fix) | fix-role-split-handshake | 5c54f9e | Fable 5 · high | LIVE window finding: skip other-process greetings (PairingMismatchError, bounded); 2nd finding operational (burned windows -> kill+new T) | ~0.2 session + 1 burned window | merged |
| 2026-08-18 | PR (overlay) | feat-local-overlay | 3406628 | Fable 5 · high | git-ignored game.local.toml overlay so window-day tunnel URLs never dirty the tree (scar #5 clean-tree rule) | ~0.1 session | merged |
| 2026-08-18 | PR (8.14 fix2) | fix-handshake-skip-budget | 36ea7be | Fable 5 · high | live finding #2: time-budget handshake skips (greeting backlog); fixed 150s sleeper test | ~0.15 session + 1 burned window | merged |
| 2026-08-18 | PR (ADR-21) | fix-mail-result-file | 950ab89 | Fable 5 · high | friendly SETTLED (6/6, audits OK, mutual sha byte-identical); compare ritual caught mail carrying Hebrew report -> now mails the result artifact | ~0.15 session + 3 window attempts | merged |
| 2026-08-18 | PR (ledger) | chore-counted-ledger | merged | Fable 5 · high | COUNTED SERIES #1 BANKED vs nis-yar1 (6/6, audits clean, armed fields correct, lecturer-only mail); ledger committed; imreeyal counter -> 1 | 3 windows + ~0.05 session | merged |
| 2026-08-18 | PR (8.16) | feat-tactical-brains | 65013a1 | Fable 5 · high | night shift: brains v2 from counted forensics; A/B tournament + kit-sparring benchmark 0-6 -> 3-3 | ~0.5 session + 3 benchmark series | merged |
| 2026-08-18 | PR (export) | feat-export-evidence | merged | Fable 5 · high | export ships match evidence (counted artifacts + rule-52 ledger) — closes the links.github gap behind the filed counted report | ~0.1 session | merged |
| 2026-08-19 | PR (ADR-22) | docs-submission-repo-delegation | 821bb68 | Fable 5 · high | scoped delegation: Claude may publish the generated dist trees to the two submission repos | ~0.05 session | merged |
| 2026-08-19 | PR (8.18) | feat-export-standalone | 3fd649f | Fable 5 · high | submission repos STAND ALONE for grading: full docs/ + CLAUDE/COSTS/LICENSE/academic README/uv.lock/all configs (overlays excluded); standalone suite green in-tree | ~0.15 session | merged |
| 2026-08-19 | PR (ADR-23) | docs-history-mirror | 57f7803 | Fable 5 · high | book read DIRECTLY (pp.94-97,148-157): rules 41/49/50/p.156 verified; workspace-history mirrored into both submission repos; README explains it | ~0.2 session | merged |
| 2026-08-19 | PR (fix) | fix-handshake-delivery | b09f084 | Fable 5 · high | two-clone proof caught a startup race (half-handshake); exchange now guarantees one DELIVERED greeting; standalone two-tree match settles identically | ~0.2 session + 2 proof matches | merged |
| 2026-08-19 | PR (seed) | fix-per-subgame-seed | e1c56d6 | Fable 5 · high | per-sub-game brain seeding (static seed = identical games per role; opponent solves once, wins thrice) | ~0.1 session | merged |
| 2026-08-21 | PR (identity) | feat-identity-commit | b53e5d2 | Fable 5 · high | identity.github_commit (il-nv-ai hard gate; book p.156): env -> rev-parse -> core_manifest fallback | ~0.1 session | merged |
| 2026-08-21 | PR (config) | config-il-nv-ai | (pending) | Fable 5 · high | il-nv-ai uncounted-warm-up config (terms hash b97de3f6 verified; ids pinned; mail off) + six-key terminal verified in code | ~0.1 session | in review |
| 2026-08-21 | Live warm-up + PR (fix) | fix-claimless-capture-final | (pending) | Fable 5 · high | il-nv-ai warm-up game 1: tunnel was down (unreachable); peer crashed at audit on their claimless `caught:true` final — degrade instead of KeyError | ~0.4 session | in review |
| 2026-08-21 | PR (evidence) | chore-commit-match-evidence | (pending) | Fable 5 · high | commit played-match artifacts (league + self-play + both result sets, 170 files) as force-added snapshots; results/README provenance | ~0.2 session | in review |
| 2026-08-21 | PR (fix) | fix-final-audit-ack | (pending) | Fable 5 · high | final submit_audit ack killed by daemon-thread exit (il-nv-ai live report, both runs); reproduced 15.0s no-ack -> 0.22s ack; shutdown grace | ~0.3 session | in review |
| 2026-08-21 | Live warm-up | (main 0e463ce) | n/a | Fable 5 · high | il-nv-ai game 2, roles swapped (we thief): capture in 10 steps, 5-20, audit clean, consensus 1be7dd12 | ~0.1 session | evidence committed |
| 2026-08-21 | PR (strategy) | feat-thief-reads-cop-claims | (pending) | Fable 5 · high | thief belief: read the cop's declared cell (capture_claim) instead of lagging scent; new HerderCop bench reproduces the live loss | ~0.6 session | in review |
| 2026-08-21 | PR (strategy) | feat-herding-police | (pending) | Fable 5 · high | police herds (territory-minimising step) instead of chasing: captures 3/16 -> 8/16; oracle after the fix 16/16 => belief is now the next lever | ~0.3 session | in review |
| 2026-08-21 | PR (strategy) | feat-read-the-scent-peak | (pending) | Fable 5 · high | scent-map PEAK is the sender's exact cell (35/35 vs belief 0/35); police captures 8/16 -> 16/16 | ~0.3 session | in review |
| 2026-08-21 | PR (docs) | docs-strategy-prds | (pending) | Fable 5 · high | author the 4 stub PRDs (strategy_brains, belief_map, pheromone_scent, llm_verbal_layer) with today's measurements + rejected alternatives; zero stubs remain | ~0.3 session | in review |
| 2026-08-21 | PR (evidence) | feat-persist-received-messages | (pending) | Fable 5 · high | file the opponent's applied turns on the log artifact (outside the signature); ~20 KB/game | ~0.2 session | in review |
| 2026-08-21 | PR (config) | config-vibecode-pairing | (pending) | Fable 5 · high | vibecode pairing config (parity flip to police-on-odd, role-split static doors, ids pinned); scent-precision + parity questions answered from code | ~0.2 session | in review |
| 2026-08-22 | PR (reporting) | feat-withhold-unclean-counted-report | (pending) | Fable 5 · high | rule-35 filing guard: an armed run withholds below 6/6 verified; friendly still fires; disputed capture still files | ~0.2 session | in review |
| 2026-08-22 | Counted series | (main cabcb07) | n/a | Fable 5 · high | vibecode counted banked: 6/6, audits clean both ways, 30-90, ledger advanced -> rule-52 series 2 of 2, min_games_to_pass MET | ~0.4 session | banked |
| 2026-08-22 | PR (provenance) | feat-report-and-verify-playing-commit | (pending) | Fable 5 · high | github_commit in declaration + result rows (outside consensus scope, pinned); armed run refuses an unpublished playing commit | ~0.4 session | in review |
| 2026-08-22 | PR (process) | chore-publish-submissions-script | (pending) | Fable 5 · high | one-command submission republish + step 10 of the git loop; verified live (both mirrors -> c0aa29a, gate green) | ~0.2 session | in review |
| 2026-08-22 | PR (docs) | docs-single-core-provenance | (pending) | Fable 5 · high | document why one core = one reported commit; reject per-role export commits as false provenance; de-stale the intro | ~0.1 session | in review |
| 2026-08-22 | PR (compliance) | docs-separation-compliance | (pending) | Fable 5 · high | book re-read from the PDF: separation is PROCESS-level, two repos are the submission form; cited README section + ADR-24 | ~0.3 session | in review |
| 2026-08-22 | PR (config) | config-il-nv-ai-counted | (pending) | Fable 5 · high | il-nv-ai counted prep: num_games 6, parity INVERTS (we are thief), counted count -> 2; verified terms/uid/tie against their message | ~0.2 session | in review |
| 2026-08-22 | PR (export) | fix-export-results-evidence | (pending) | Fable 5 · high | export results/ from git ls-files (played_commits.md + results/README.md were never shipping); fix a pinned uid test I had claimed passing | ~0.2 session | in review |
| 2026-08-22 | PR (publish) | fix-publish-force-adds-evidence | (pending) | Fable 5 · high | exported .gitignore hid results/* so `git add -A` published NO evidence; force-add + published-count printed | ~0.2 session | in review |
| 2026-08-22 | PR (reporting) | feat-deferred-report-send | (pending) | Fable 5 · high | compare-then-send tool: sends filed bytes verbatim, re-applies the 6/6 guard, prints the message-id | ~0.3 session | in review |
| 2026-08-22 | PR (interop) | fix-numeric-hardware-spec | (pending) | Fable 5 · high | numeric hardware declaration (il-nv-ai validator refused strings); tie-award fork researched in SPEC §6 | ~0.3 session | in review |
| 2026-08-22 | PR (interop) | config-adopt-il-nv-ai-constitution | (pending) | Fable 5 · high | adopted their 911B constitution; it omits the signed term min_center_intensity — proved 0.5 and the 948B file that reproduces their hashes | ~0.2 session | in review |
| 2026-08-22 | PR (strategy) | feat-thief-avoids-reachable-cells | (pending) | Fable 5 · high | overnight brains work: evader reach-avoidance (10 -> 12 steps); FIVE cop hypotheses tested and disproved, none shipped | ~1.5 session | in review |
| 2026-08-22 | PR (strategy) | feat-police-breaks-parity-stall | (pending) | Fable 5 · high | cop can STAY to break a parity lock (fires at live steps 10-30, no bench regression); depth-8/12 evader search proven worthless | ~1.5 session | in review |
| 2026-08-23 | PR (interop) | fix-appendix-b-config-scope | (pending) | Fable 5 · high | Appendix B != signed terms: min_center is not in the book; adopt their 911B file, fill the term from the SPEC default | ~0.3 session | in review |
| 2026-08-23 | PR (config) | config-imreeyal-refresh | (pending) | Fable 5 · high | imreeyal: stale counted count 1->2, and role-split doors added (we dialled their cop door in every sub-game) | ~0.1 session | in review |
| 2026-08-23 | PR (reporting) | fix-subgame-start-timestamp | (pending) | Fable 5 · high | filed started_at was the peer launch, not the sub-game open (15-min error vs imreeyal); caught by cross-diff | ~0.1 session | in review |
| 2026-08-23 | PR (observability) | fix-peer-progress-logging | 959ed1d | Fable 5 · high | peer wrote a 0-byte log for 30 min across TWO aborted counted attempts; announce every seam, flushed, on stderr | ~0.3 session + 2 void windows | merged (#104) |
| 2026-08-23 | PR (reliability) | fix-bounded-audit-wait | 241ba6e | Fable 5 · high | audit wait shared connect_timeout (2400s armed) — a missing g3 audit hung us 40 min; separate budget, 120s x2 with one re-send | ~0.3 session | merged (#105) |
| 2026-08-23 | PR (protocol) | feat-void-on-missing-audit | eae0d70 | Fable 5 · high | option A agreed with imreeyal: lost audit voids the sub-game and stops the series, nothing filed | ~0.2 session | merged (#106) |
| 2026-08-24 | PR (strategy) | feat-brains-stay-and-containment | (pending) | Fable 5 · xhigh | overnight brains rebuild on imreeyal's debrief: evader gains STAY (the corner death), cop scores escapes, barriers OFF (0/32 -> 32/32); new arena + champion gate | ~4 session, ~30k arena games | in review |

## Notes on methodology
- Exact token accounting used when available (e.g. subagent token totals from the
  workflow harness); otherwise wall-clock time, session count, and review burden.
- Cost is not only financial — it also measures **review debt** (PR size),
  **runtime debt** (long matches, tunnel runs), and **agent efficiency** (rework).
- Log here as they occur: full 6-sub-game match runs, cross-implementation tunnel
  games, and any opt-in LLM (`claude_api` / `claude_cli`) banter usage against the
  token budget (200,000 / series).
