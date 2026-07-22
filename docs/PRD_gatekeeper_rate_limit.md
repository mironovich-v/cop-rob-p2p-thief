# PRD — API Gatekeeper & Rate Limiting

> Dedicated PRD (guideline §1.3). **Build stage:** 2 (TODO slice 2.2). Ground
> truth: reference `shared/gatekeeper.py`, `shared/rate_limiter.py`,
> `rate_limits.json`; guideline §4; `CLAUDE.md` §21.

## 1. Background

**All** external calls (LLM verbal provider, Gmail, opponent MCP where rate-bound)
go through one centralized gatekeeper. On overflow, requests **queue** (FIFO with
backpressure) rather than crash; transient failures retry. Limits come from
`rate_limits.json`, never hard-coded.

## 2. Requirements (FR-9, NFR-6)

No call bypasses the gatekeeper; limits enforced before every call; overflow
queued up to a max depth then backpressured; transient errors retried up to
`max_retries`; every call is logged.

## 3. Interface

- **`RateLimiter(limits, queue_cfg)`**: sliding-window token bucket over a 60 s
  window. `acquire()` grants immediately if under `requests_per_minute`; else
  queues if a slot is free (up to `queue.max_depth`), polling every
  `queue.drain_interval_seconds` until granted or `queue.timeout_seconds`.
- **`ApiGatekeeper(config, service)`**: `execute(api_call, *args, **kwargs)` →
  `acquire()` then call; on `ProviderError` retry up to `max_retries` (spacing
  `retry_after_seconds`); re-raise the last error if all attempts fail; tracks
  calls/failures. `service_limits(service)` falls back to the `default` block.

## 4. Parameters (from `rate_limits.json`; App-F minimums)

Per service: `requests_per_minute` (min 30), `concurrent_max` (min 2),
`retry_after_seconds` (min 5), `max_retries` (min 3). Queue: `max_depth`
(min 100), `drain_interval_seconds`, `timeout_seconds`. Window = 60 s.

## 5. Alternatives considered

Reject-on-overflow → **rejected** (book requires queueing, not dropping). A global
limiter shared across services → **rejected** (per-service limits differ: claude
vs email).

## 6. Success criteria & tests

Under-limit calls pass immediately; over-limit calls queue and drain; queue-full
backpressures within timeout; transient `ProviderError` retries then succeeds or
re-raises; default fallback works. Tests: `test_rate_limiter`, `test_gatekeeper`
(no real sleep dependence beyond bounded/fake timing; deterministic).
