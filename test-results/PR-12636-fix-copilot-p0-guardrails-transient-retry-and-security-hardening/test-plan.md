# Test Plan: PR #12636 — fix(copilot): P0 guardrails, transient retry, and security hardening

## What changed
- SDK guardrails: fallback_model (auto-failover on 529), max_turns=1000, max_budget_usd=100.0
- CLAUDE_CODE_TMPDIR routing: CLI temp dirs go into per-session workspace
- Security env vars in ALL auth modes (subscription, OpenRouter, direct)
- Transient API retry: exponential backoff for 429/5xx/ECONNRESET (only when events_yielded==0)
- Provider-aware model resolution refactor

## Scenarios

1. **Copilot UI loads** — navigate to /copilot, verify page renders, input is visible
2. **Basic copilot chat** — send a simple message, verify response streams back with no errors
3. **Guardrails in env** — verify max_turns, max_budget_usd, fallback_model are in copilot env
4. **Security env vars** — verify CLAUDE_CODE_DISABLE_CLAUDE_MDS and siblings are set
5. **TMPDIR routing** — verify CLAUDE_CODE_TMPDIR is set to session workspace (not /tmp/claude-0/)
6. **Multi-turn conversation** — send 2-3 messages in same session, verify continuity
7. **Onboarding bypass** — POST /api/onboarding/step?step=VISIT_COPILOT before browser test

## API Tests
1. GET /api/onboarding — check onboarding state is handled
2. POST /api/chat/sessions — create session
3. POST /api/chat/sessions/{id}/stream — send message, verify SSE response

## UI Tests
1. /copilot page loads without redirect to onboarding
2. Chat input is present and enabled
3. Sending a message produces a visible response

## Negative Tests
1. No HOME= override in env (was removed in review — would break git/ssh/npm)
2. Security vars present in env regardless of auth mode

## Feature flags needed
- CHAT_MODE_OPTION — enable mode toggle UI (set NEXT_PUBLIC_FORCE_FLAG_CHAT_MODE_OPTION=true)
