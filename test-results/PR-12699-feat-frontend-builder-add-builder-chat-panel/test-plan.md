# Test Plan: PR #12699 — feat(frontend/builder): add builder chat panel for interactive agent editing

## Feature Flag
`NEXT_PUBLIC_FORCE_FLAG_BUILDER_CHAT_PANEL=true` must be set in backend + frontend .env and containers rebuilt.

## Scenarios

1. **Panel toggle** — Chat panel opens/closes via toggle button in builder
2. **Seed message hidden** — System seed message is NOT visible in chat UI
3. **AI suggestion with Apply/Reject buttons** — After sending a message, AI responds with graph actions; each action shows individual Apply/Reject buttons (NOT auto-applied)
4. **Apply action** — Clicking Apply on a node-add action adds the node to the graph
5. **Reject action** — Clicking Reject dismisses an action without applying it
6. **Prompt injection prevention** — Node names with `<`, `>`, `&` special chars don't break the XML serialization
7. **Multi-turn action persistence** — Actions from previous messages remain visible/applicable in later turns
8. **Escape key closes panel** — Pressing Escape closes the chat panel
9. **Panel closed hides content** — When panel is closed, chat content is not rendered

## API Tests
- None specifically (frontend-only feature)

## Negative Tests
1. Auto-apply should NOT happen — AI suggestions should NOT be applied without user clicking Apply
2. Empty node name or description should not cause errors in serialization
