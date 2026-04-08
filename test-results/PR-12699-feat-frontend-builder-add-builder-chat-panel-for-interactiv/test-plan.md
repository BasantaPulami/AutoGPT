# Test Plan: PR #12699 — feat(frontend/builder): add builder chat panel for interactive agent editing

## Summary
Adds a floating `BuilderChatPanel` to the agent builder. When opened, it creates a copilot chat session seeded with the current graph context. The AI responds with natural language and can emit structured `GraphAction` JSON blocks (`update_node_input`, `connect_nodes`) that are auto-applied to the canvas.

**Feature flag:** `BUILDER_CHAT_PANEL` (requires `NEXT_PUBLIC_FORCE_FLAG_BUILDER_CHAT_PANEL=true`)

## Scenarios

### UI / Rendering
1. Chat button renders in builder (bottom-right) — clicking it opens the panel
2. Panel shows welcome state when first opened (before sending a message)
3. Sending a message shows user message + streaming AI response
4. Stop button cancels streaming
5. Panel closes via X button

### AI Graph Actions
6. AI responds with `update_node_input` action — node input is updated on canvas
7. AI responds with `connect_nodes` action — edge is created on canvas

### Session / State
8. Navigating to a different graph resets session (seed is re-sent on next open)
9. Error state shown if session creation fails

## API Tests
1. `POST /api/chat/sessions` — creates a session for the chat panel
2. `POST /api/chat/sessions/{id}/stream` — streams AI response (SSE)

## Negative Tests
1. Send button disabled while streaming (canSend=false)
2. Seed message hidden from chat UI
