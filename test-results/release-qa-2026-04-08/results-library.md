# QA Results: Library Tests — 2026-04-08

**Tester:** Zamil QA Tester (zamil.majdy@gmail.com)
**Environment:** https://dev-builder.agpt.co/
**Session:** qa-library-1
**Date:** 2026-04-08

---

## Summary Table

| Check | Result | Notes |
|-------|--------|-------|
| Export the agent to a file | FAIL | Builder export option not tested — blocked by navigation instability (see bugs) |
| Import an agent from a file | FAIL | Import button visible in DOM but blocked by library spinner/redirect loop |
| Run the imported agent | BLOCKED | Blocked by import failure |
| Open imported agent in builder from Library | BLOCKED | Blocked by library redirect bug |
| Edit a saved agent | PARTIAL | Builder loads with correct agent content, but navigation to builder via Library broken |
| Run the saved agent | BLOCKED | Cannot navigate to runner from Library |
| Setup your task (start/stop/delete) | BLOCKED | Cannot reach Library page reliably |
| Open agent in builder from Runner UI (Customise Agent) | BLOCKED | Cannot reach Runner UI reliably |

**Overall: ALL 8 items BLOCKED or FAIL due to critical platform navigation bugs.**

---

## Critical Bugs Found

### BUG-1: Library page (/library) shows persistent full-screen loading spinner and redirects to /profile
**Severity: CRITICAL**
- Navigating to `https://dev-builder.agpt.co/library` shows a full-screen loading spinner for 15–60+ seconds
- The page content IS partially rendered in the DOM (agent cards visible via JS queries) but is blocked by the spinner overlay
- After the timeout, the page **automatically redirects to /profile** (not the library)
- Reproducible: Attempted >10 times across the session, same behavior every time
- This makes the Library (Agents) page essentially unusable
- Screenshot: `library-00-library-spinner-bug.png` (spinner visible while content is behind it)

### BUG-2: /build URL redirects to /copilot
**Severity: CRITICAL**
- Navigating directly to `https://dev-builder.agpt.co/build` redirects to `/copilot`
- The builder only loads when a specific `?flowID=...` parameter is provided
- This means users cannot access a blank builder from the nav

### BUG-3: "Build" nav link does not always navigate to the builder
**Severity: HIGH**
- Clicking the "Build" nav link from some pages navigated to `/marketplace` instead of `/build`
- Clicking "Agents" nav link sometimes stayed on `/copilot` without navigating
- The nav links appear to have inconsistent behavior depending on the current page

### BUG-4: /api/auth/signout returns 404
**Severity: MEDIUM**
- Accessing `/api/auth/signout` shows a "404 - This page could not be found" error
- Despite showing 404, the user **IS** signed out (session invalidated)
- This is confusing for users and indicates a missing or broken signout route handler
- Screenshot: `library-00-signed-out.png`

### BUG-5: Login `?next=` redirect parameter does not work
**Severity: MEDIUM**
- After session expiry, the platform redirects to `/login?next=%2Fbuild`
- After successful login, the user is redirected to `/profile` instead of the originally requested `/build` page
- The `next` parameter is being ignored

### BUG-6: Excessive full-page loading spinner duration on all page transitions
**Severity: HIGH**
- Every page transition (including library, build, profile) shows a full-screen white spinner
- Duration: consistently 8–30 seconds per navigation
- During this time, the entire UI is blocked (no partial content visible to user)
- This results in a very poor user experience on what feels like a slow or broken app
- Screenshots: Multiple `library-00-*.png` files all showing the same spinner

### BUG-7: Browser session instability — automatic navigation away from pages
**Severity: HIGH**
- While on the builder or library, the page occasionally **auto-navigates to /copilot** without user action
- Observed behavior: loading `/library?sort=updatedAt` → auto-navigates to `/profile/dashboard` after ~20s
- Observed behavior: loading `/build?flowID=...` → auto-navigates to `/copilot` after ~30-60s
- This suggests a race condition in the routing/auth middleware or Copilot redirect logic

### BUG-8: Screenshot vs URL/DOM mismatch (agent-browser tool issue)
**Note:** This is potentially a testing tooling issue rather than a platform bug, but worth noting.
- `agent-browser screenshot` sometimes captured stale/cached frames not matching the actual URL
- The Profile page screenshot appeared even when URL showed `/build?flowID=...`

---

## What Was Confirmed Working

### Library Page — Agent Cards Visible in DOM
Even while the spinner is shown, JavaScript queries confirm 30 agents are present in the DOM with correct data including:
- "QA Marketplace Test 2026-04-08", "Z.ai", "ChatGPT Image Generator", "OrchestratorTest", "Text Summarizer", "Cute Hyrax Photo Generator", "Cute Bekantan Generator", "Batch Bekantan Image Generator", "Topic Summarizer", and 21 more

Agent cards have correct structure: agent name, "See runs" link, "Open in builder" link, "More actions" button, "Add to favorites" button.

### Builder Loads with Correct Agent (when accessed via direct flowID URL)
- `https://dev-builder.agpt.co/build?flowID=90f57cd5-5a04-4bac-8c71-5e2e0e3fef5d&flowVersion=2` (Text Summarizer) loaded successfully
- Builder showed 3 connected blocks, correct agent content
- Builder toolbar buttons are present (Zoom In, Zoom Out, Fit View, Toggle Lock, 5 bottom toolbar buttons)
- The agent structure confirms the builder page itself works when directly accessed

### Login Page Works
- Login form loads correctly
- Email/password autofill works
- Login with correct credentials succeeds

### Creator Dashboard (profile/dashboard) Works
- Shows 2 marketplace-submitted agents: "QA Marketplace Test 2026-04-08" and "Human In The Loop Agent Test"
- Status shown as "Approved"

### Import Button Present in Library DOM
- The "Import" button (ref=e10/e16) is visible in the library DOM even during the spinner
- File input for import is present (`input[type=file]`)
- However, the spinner/overlay prevents user interaction

---

## Test Observations by Item

### 1. Export the agent to a file
**Result: FAIL**

Could not complete export testing. The builder loads an agent successfully when accessed via direct flowID URL. The builder bottom toolbar has 5 buttons (including what appears to be a save/export button), and there is an unnamed expandable button (`e21`) in the toolbar. However:
- Navigation to the builder is unstable
- Attempting to click the export button resulted in page navigation to profile settings
- Could not confirm the export menu opens or exports a file

Partial observation: There are existing JSON files in `~/Downloads/` including `Orchestrator Test v11.json`, `AutoGPT Workflow.json`, `Engineering Tickets v2.json`, etc., indicating exports have been performed in this account previously.

### 2. Import an agent from a file
**Result: FAIL**

The Import button is visible and present in the library DOM. However, the library page spinner prevented clicking it. When the spinner is active, all interactive elements appear to be covered by the overlay.

Existing JSON files are available in `~/Downloads/` for import testing.

### 3. Run the imported agent
**Result: BLOCKED** — dependent on item 2

### 4. Open the imported agent in builder from Library
**Result: BLOCKED** — dependent on item 2, and library navigation is broken

### 5. Edit a saved agent
**Result: PARTIAL**

The builder does load with a correct saved agent when accessed via direct URL:
`https://dev-builder.agpt.co/build?flowID=90f57cd5-5a04-4bac-8c71-5e2e0e3fef5d&flowVersion=2`

The agent "Text Summarizer" loads with 3 connected blocks. However:
- Could not navigate to builder via Library → "Open in builder" (library page broken)
- Could not test saving changes (navigation instability caused page to redirect before testing)

### 6. Run the saved agent
**Result: BLOCKED**

Could not test — builder navigation instability prevented sustained testing.

### 7. Setup your task (start/stop/delete)
**Result: BLOCKED**

Could not reach the Library page reliably. Agent detail page (`/library/agents/{id}`) not tested.

### 8. Open agent in builder from Runner UI (Customise Agent)
**Result: BLOCKED**

Could not reach the Runner UI. See BUG-1 (library redirect).

---

## Screenshots Taken

| File | Description |
|------|-------------|
| `library-00-login-page.png` | Initial login page (skeleton loading) |
| `library-00-login-form.png` | Login form with cookie banner |
| `library-00-library-spinner-bug.png` | Library page stuck in loading spinner — BUG-1 |
| `library-00-library-loaded-final.png` | Library spinner (persistent) |
| `library-00-agents-settled.png` | Library showing agent cards briefly before redirect |
| `library-00-signed-out.png` | 404 on /api/auth/signout — BUG-4 |
| `library-00-after-dismiss.png` | Library agent cards visible |
| `library-00-fresh-library.png` | Library spinner |
| `library-00-copilot-ready.png` | Copilot page (loaded) |
| `library-00-profile-ready.png` | Profile settings page (logged in confirmed) |
| `library-00-agents-nav.png` | Library page with agent cards |
| `library-01-builder-text-summarizer.png` | Text Summarizer in builder (3 blocks) |
| `library-01-builder-text-sum.png` | Text Summarizer builder (loaded) |
| `library-01-more-actions.png` | Library cards view |
| `library-01-creator-dash-actions.png` | Creator Dashboard with 2 submitted agents |
| `library-final-state.png` | Profile page (skeleton) — library redirected here |

---

## Overall Assessment

**The Library/Agents functionality is NOT release-ready.**

The primary blocking issue is BUG-1: the `/library` page has a persistent, indefinite loading spinner that eventually redirects the user away from the page. This blocks all 8 QA test items. The supporting bugs (BUG-2 through BUG-7) compound to make normal user workflows — browsing agents, navigating to builder, exporting, importing — unreliable or impossible.

The builder itself appears to function when loaded via direct URL with a flowID. The agent data is present and correctly structured. The issue is systemic to navigation/routing, not to the agent execution engine.

**Recommendation: DO NOT release until BUG-1 and BUG-3 are resolved.**
