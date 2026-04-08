# Release QA Results — Builder (2026-04-08)

**Target:** https://dev-builder.agpt.co/  
**Account:** zamil.majdy@gmail.com  
**Session:** qa-builder-1 / qa-builder-2  
**Starting credit balance:** $1027.53  

---

## Summary Table

| Check | Result | Notes |
|-------|--------|-------|
| Build an agent with a few blocks | FAIL | Builder canvas unreachable for new agent creation; constant session redirects block all block-adding interactions |
| Add a block requiring credentials | BLOCKED | Could not reach a stable builder state to add a credential block |
| Run the agent | BLOCKED | No agent could be built or saved due to builder instability |
| Schedule an agent run | BLOCKED | Could not reach scheduling flow |
| Verify credit deduction after run | PARTIAL | Credits confirmed at $1027.53 before tests; no run completed to verify deduction |
| Remove credential from integrations | PARTIAL | Integrations page loads and shows existing credential (api.openai.com/Http) with Delete button visible; could not add new credential to remove |

---

## Detailed Findings

### 1. Build an agent with a few blocks — FAIL

**What was observed:**

After login, navigating to `/build` (the "Build" nav item) initially shows the ReactFlow builder canvas for approximately 8–12 seconds, then automatically redirects to `/library?sort=updatedAt`, `/profile`, `/copilot`, `/onboarding/reset`, or `/reset-password?request=true` — the destination is unpredictable.

- On a fresh login, `/build` correctly shows an empty canvas with "Welcome to AutoGPT Builder!" tutorial dialog (screenshot: `builder-36-build-canvas2.png`, `builder-40-new-agent-blocks.png`)
- The new agent canvas initialises with two default blocks: **Agent Input** and **Agent Output** — the template is correct (screenshot: `builder-38-new-agent-canvas.png`, `builder-40-new-agent-blocks.png`)
- The canvas URL becomes `/build?flowID={new-uuid}&flowVersion=1` showing a new agent was auto-created
- Any click on the sidebar (blocks panel button, search, etc.) or any button on the canvas triggers navigation away from the builder — most commonly to `/copilot` or `/profile`
- This makes it impossible to open the blocks panel, add AI Text Generator or Smart Decision Maker blocks, connect blocks, or save

**Evidence of redirects encountered:**
- `/build` → `/library?sort=updatedAt` (most common, within 10–15s)
- `/build` → `/profile` (triggered by sidebar button clicks)
- `/build` → `/copilot` (triggered by sidebar/toolbar clicks)
- `/build` → `/reset-password?request=true` (spontaneous)
- `/build` → `/onboarding/reset` (spontaneous)
- `/build` → `/login` (session expiry)
- `/profile/billing` → `/onboarding`

**Root cause hypothesis:** The NextJS middleware / Supabase auth session refresh is misfiring and issuing redirects at ~10–20s intervals regardless of user action. Additionally, clicking elements on the builder canvas triggers navigation to profile or copilot pages, suggesting z-index/event-bubbling issues where sidebar button clicks reach profile menu links underneath.

**Screenshots:**
- `builder-01-empty-canvas-final.png` — empty canvas on fresh session
- `builder-36-build-canvas2.png` — tutorial dialog on new canvas
- `builder-38-new-agent-canvas.png` — new agent with Agent Input + Agent Output blocks
- `builder-40-new-agent-blocks.png` — same canvas (stable for ~8s)
- `builder-19-flow-loaded.png` — "Loading Flow" spinner on existing agent
- `builder-25-canvas-with-flow.png` — Z.ai agent canvas loading (briefly)
- `builder-27-canvas-fresh.png` — Z.ai canvas loaded with blocks (briefly, before redirect)

---

### 2. Add a block requiring credentials — BLOCKED

Could not reach a stable builder state to find and click a credential-requiring block (e.g. GitHub API block). The builder redirects before the block panel can be opened.

**What was confirmed separately:** The Integrations page (`/profile/integrations`) loads and shows existing credentials, including an Http credential for `api.openai.com`. A "Delete" button is present. This confirms the credential management infrastructure exists.

**Screenshot:** `builder-42-integrations.png`

---

### 3. Run the agent — BLOCKED

No agent could be built to completion. The run controls at the bottom of the canvas (play button, test button) appeared greyed out/disabled in all snapshots. The builder did not reach a state where running was possible.

---

### 4. Schedule an agent run — BLOCKED

The scheduling control (clock icon at bottom toolbar) was visible as a disabled button in all builder snapshots. Could not test due to builder instability.

---

### 5. Verify Credit usage deduction — PARTIAL

**Before run:** $1027.53 (confirmed in multiple screenshots from top-right balance display)  
**After run:** N/A — no run was completed  

Credit balance was consistently visible and correctly displayed throughout the session. No deduction could be verified because no agent run succeeded.

**Screenshot:** `builder-13-library-page.png` and `builder-42-integrations.png` both show $1027.53 balance in the nav bar.

---

### 6. Remove credential from integrations — PARTIAL

The Integrations page at `/profile/integrations` loaded and showed:
- Provider: **Http**, Name: `api.openai.com`, credential ID `fd430417-3178-415b-b669-a0220a2432ec`
- A red "Delete" button is present and appears functional

Could not test adding a new credential (step 2 was blocked) and therefore could not test removing a freshly-added one. The existing credential delete button is present and visible.

**Screenshot:** `builder-42-integrations.png`

---

## Bugs Found

### BUG-1: CRITICAL — Builder redirects away after 10–20 seconds
**Severity:** P0 — Blocker  
**Description:** The `/build` page (and `/build?flowID=...`) spontaneously redirects to `/profile`, `/copilot`, `/library`, `/onboarding/reset`, or `/login` within 10–20 seconds of loading. This makes the builder completely unusable.  
**Reproduction:** Log in → navigate to `/build` → wait 15 seconds → observe redirect  
**Screenshots:** `builder-33-build-loaded2.png` (profile redirect), `builder-34-zai-canvas.png` (profile redirect after open), `builder-09-build-click.png` (settings page from Build nav click)

### BUG-2: CRITICAL — Builder sidebar/toolbar button clicks navigate to /profile or /copilot
**Severity:** P0 — Blocker  
**Description:** Clicking any button in the builder left sidebar (blocks icon, search, etc.) navigates the page to `/copilot` or `/profile` instead of opening the panel/functionality. The run controls at the bottom do the same.  
**Reproduction:** Open builder → click first sidebar icon (blocks) → observe navigation to /copilot  
**Screenshots:** `builder-39-blocks-panel-open.png` (after clicking blocks → got copilot)

### BUG-3: HIGH — No visible "New Agent" button in the library/agents page
**Severity:** P1 — Navigation UX  
**Description:** The `/library` page (Agents tab) shows existing agents with "Open in builder" links but has no "New Agent" or "Create Agent" button. New agent creation is only possible via the `/build` URL (which redirects) or via the Copilot chat "Create" button (non-obvious).  
**Screenshots:** `builder-13-library-page.png`, `builder-22-library-clean.png`

### BUG-4: HIGH — "Build" nav link navigates to Settings/Profile page
**Severity:** P1  
**Description:** Clicking "Build" in the top navigation bar from the library or profile pages navigates to `/profile/settings` (My Account page) instead of the builder canvas.  
**Reproduction:** Be on `/library` or `/profile` → click "Build" in nav → land on `/profile/settings`  
**Screenshots:** `builder-09-build-click.png`

### BUG-5: MEDIUM — Extreme page load times (20–60+ second spinner)
**Severity:** P2 — Performance  
**Description:** Most pages (library, build, copilot) display a loading spinner for 20–60+ seconds before content appears or before redirecting. In many cases the spinner never resolves and redirects occur instead.  
**Screenshots:** Multiple spinner-only screenshots (builder-03, builder-04, builder-07, builder-10, builder-11, etc.)

### BUG-6: MEDIUM — /profile/billing redirects to /onboarding (blank page)
**Severity:** P2  
**Description:** Navigating to the billing page redirects to `/onboarding` which renders a blank white page.  
**Screenshots:** `builder-43-billing.png`

### BUG-7: LOW — Tutorial dismiss button ("Not now") navigates to /copilot
**Severity:** P3  
**Description:** The notification permission dialog that appears in the builder has a "Not now" button that, when clicked, navigates to the `/copilot` page instead of staying on the builder.  

---

## Navigation Architecture Notes (for engineering)

The app URL structure observed:
- `Home` nav → `/copilot` (Copilot chat interface)
- `Agents` nav → `/library` (Agent card grid)
- `Marketplace` nav → `/marketplace`
- `Build` nav → `/build` (should be builder, but redirects)

The `/build` URL without `flowID` shows a brief empty canvas (correct behaviour) then redirects to library/copilot. The builder canvas is only reliably accessible via `/build?flowID={uuid}` opened directly — but this also redirects within ~10–20s.

The session/auth mechanism appears to be issuing periodic server-side redirects that override the current page. This may be related to a Supabase auth token refresh loop or a Next.js middleware cookie validation issue.
