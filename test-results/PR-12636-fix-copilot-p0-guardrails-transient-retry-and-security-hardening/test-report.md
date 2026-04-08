# E2E Test Report: PR #12636 — fix(copilot): P0 guardrails, transient retry, and security hardening
Date: 2026-04-08 (Round 5 — 3 new commits)
Branch: fix/copilot-p0-cli-internals
Worktree: /Users/majdyz/Code/AutoGPT15

## New commits tested this round
- `79b8ad80fe` — tighten fallback detection + harden header sanitization in `sdk/env.py`
- `f95772f0af` — fix StreamError ordering + cap exponential backoff at 30s in `sdk/service.py`
- `fff9faf13c` — use `"transient_api_error"` error code for exhausted transient retries

## Environment
- Docker services: all up (rest_server, copilot_executor, executor, frontend, websocket, scheduler, notification, database_manager)
- Auth mode: Claude Code subscription (CLAUDE_CODE_OAUTH_TOKEN from keychain)
- Feature flags enabled: NEXT_PUBLIC_FORCE_FLAG_CHAT_MODE_OPTION=true
- Onboarding bypass: POST /api/onboarding/step?step=VISIT_COPILOT completed before browser tests

## Test Results

### Scenario 1: SDK guardrail defaults
**Steps:** `python3 -c "from backend.copilot.config import ChatConfig; c = ChatConfig(); print(c.claude_agent_fallback_model, c.claude_agent_max_turns, c.claude_agent_max_budget_usd, c.claude_agent_max_transient_retries)"`
**Expected:** fallback_model=claude-sonnet-4-20250514, max_turns=1000, max_budget_usd=100.0, max_transient_retries=3
**Actual:**
- fallback_model: claude-sonnet-4-20250514 ✅
- max_turns: 1000 ✅
- max_budget_usd: 100.0 ✅
- max_transient_retries: 3 ✅
**Result:** PASS

### Scenario 2: Security env vars in all auth modes
**Steps:** `python3 -c "from backend.copilot.sdk.env import build_sdk_env; env = build_sdk_env(sdk_cwd='/tmp/test'); print(...)"`
**Expected:** CLAUDE_CODE_DISABLE_CLAUDE_MDS=1, CLAUDE_CODE_SKIP_PROMPT_HISTORY=1, CLAUDE_CODE_DISABLE_AUTO_MEMORY=1, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1, CLAUDE_CODE_TMPDIR=/tmp/test, HOME NOT in env, ANTHROPIC_API_KEY cleared
**Actual:**
- CLAUDE_CODE_DISABLE_CLAUDE_MDS: 1 ✅
- CLAUDE_CODE_SKIP_PROMPT_HISTORY: 1 ✅
- CLAUDE_CODE_DISABLE_AUTO_MEMORY: 1 ✅
- CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: 1 ✅
- CLAUDE_CODE_TMPDIR: /tmp/test ✅
- ANTHROPIC_API_KEY cleared: True ✅
- HOME in env: False ✅
**Result:** PASS

### Scenario 3: Header sanitization (new in 79b8ad80)
**Steps:** Verify `re.sub(r"[^\x20-\x7e]", "", v).strip()[:128]` pattern in `build_sdk_env`
**Expected:** Strips null bytes, control chars, non-ASCII; truncates at 128 chars
**Actual:** Pattern confirmed in `sdk/env.py` — strips everything outside printable ASCII 0x20–0x7e range per RFC 7230 §3.2.6
**Result:** PASS (code-verified)

### Scenario 4: Transient retry error codes (new in fff9faf13c)
**Steps:** Grep service.py for error code assignments
**Expected:** "transient_api_error" when transient retries exhausted; "all_attempts_exhausted" for compaction; "sdk_stream_error" for other fatal
**Actual:** 8 occurrences of "transient_api_error" in service.py; `transient_exhausted` flag controls branching; distinct codes for all 3 paths ✅
**Result:** PASS (code-verified)

### Scenario 5: Exponential backoff cap (new in f95772f0af)
**Steps:** Read `_next_transient_backoff` logic in service.py
**Expected:** `min(30, 2 ** (n-1))` — caps at 30s (1s, 2s, 4s, 8s, 16s, 30s...)
**Actual:** Confirmed in source: `return min(30, 2 ** (transient_retries - 1))` ✅
**Result:** PASS (code-verified)

### Scenario 6: `transient_exhausted` flag semantics
**Steps:** Read `_HandledStreamError(already_yielded=False)` usage and outer retry loop
**Expected:** `already_yielded=False` on `_HandledStreamError` means outer loop decides whether to retry or surface error — prevents duplicate StreamError emission
**Actual:** Confirmed: `_HandledStreamError` dataclass has `already_yielded: bool = True` default; exhausted-retries path uses `already_yielded=False` so the outer loop handles it correctly ✅
**Result:** PASS (code-verified)

### Scenario 7: Transient error pattern coverage
**Steps:** Test `is_transient_api_error()` / `_TRANSIENT_ERROR_PATTERNS` against all documented patterns
**Expected:** 429/5xx status codes, ECONNRESET, rate limit → True; auth errors, 4xx → False
**Actual:** All patterns confirmed in `constants.py`: "status code 429", "500/502/503/504/529", "ECONNRESET", "rate limit exceeded", "too many requests", "socket connection was closed unexpectedly"
**Result:** PASS (code-verified)

### Scenario 8: API chat streaming — basic turn
**Steps:** Create session via POST /api/chat/sessions, stream message "What is 7+8? Reply with just the number."
**Expected:** SSE stream returns correct answer
**Actual:** Response "15" received via SSE stream ✅
**Result:** PASS

### Scenario 9: Multi-turn conversation continuity
**Steps:** Follow-up message "Now add 10 to that. Reply with just the number."
**Expected:** Context preserved, answer = 25
**Actual:** Response "25" — multi-turn context preserved via --resume flag ✅
**Result:** PASS

### Scenario 10: Copilot page loads without onboarding redirect
**Steps:**
1. POST /api/onboarding/step?step=VISIT_COPILOT to bypass onboarding
2. Navigate to http://localhost:3000/copilot
**Expected:** Copilot chat page renders, not redirected to onboarding
**Actual:** Copilot page loaded with chat input, "Thinking" mode button, "Your chats" sidebar
**Result:** PASS
**Screenshot:** r5-copilot-page.png

### Scenario 11: Browser chat — single turn
**Steps:**
1. Type "What is 9+9? Reply with just the number." in chat input
2. Press Enter, wait ~30s
**Expected:** Copilot returns "18"
**Actual:** Response "18" with "Thought for 11s" indicator — extended thinking active ✅
**Result:** PASS
**Screenshot:** r6-copilot-response.png

## Summary
- Total: 11 scenarios
- Passed: 11
- Failed: 0
- Bugs found: None

## Known non-issues
- Session title generation fails with 401 ("User not found") — pre-existing test-env issue with OpenRouter credentials for title-gen model. Not related to this PR.

## Feature flags used
- NEXT_PUBLIC_FORCE_FLAG_CHAT_MODE_OPTION=true (mode toggle UI — production value is LD-driven)
