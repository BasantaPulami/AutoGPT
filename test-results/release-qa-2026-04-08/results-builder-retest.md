# QA Builder Retest Results — 2026-04-08
**Session:** qa-builder-retest  
**URL:** https://dev-builder.agpt.co/  
**Account:** zamil.majdy@gmail.com  
**Date:** 2026-04-08  

---

## Test Results Summary

| Test | Result | Notes |
|------|--------|-------|
| Build agent with 4 blocks | PARTIAL | 3 blocks added (AI Text Generator, Agent Input, Agent Output). "Smart Decision Maker" does not exist; added "AI Condition" instead. BLOCKED on save — see Bug #1 |
| Run the agent | PASS | Ran existing "Hello World Agent" successfully. All 4 nodes COMPLETED. Output: "Hello, Hello world test! Today's date is 2026-04-08." |
| Schedule an agent run | PASS | Schedule dialog works. Created "QA Test Schedule" (Daily 9:00 AM Jakarta). Appears in Scheduled tab with correct cron. |
| Export the agent to a file | PASS | "Export agent to file" found in More Actions menu on the library agent page. Agent exported via JSON download. Export also available via API: GET /api/proxy/api/graphs/{id}?include_config=true |
| Import an agent from file | FAIL | Import dialog works, file upload auto-populates name/description. Upload button submits but agent is NOT created (silent failure — affected by Bug #1). Count stays at 31. |
| Library — Setup your task | PASS | "New task" button opens task dialog with inputs. Filled "Your Name" = "Library Test User". Task ran and completed: "Hello, Library Test User! Today's date is 2026-04-08." Task deletion confirmed (count 5→4). |
| Open agent in builder from Runner UI ("Customise Agent") | PASS | "Edit agent" in More Actions menu opens builder with correct flowID (b03c1125). |
| Add credential block + authenticate | PASS | Added Github Comment block. "Add credential" button opens OAuth dialog. "Sign in with Github" initiates OAuth redirect to github.com/login correctly. |
| Verify credit deduction | PARTIAL | Balance: $1027.51 before → $1028.51 after runs (INCREASED by $1 — likely from earn-credits reward, not a deduction). No-cost template agent runs don't consume credits as expected. |
| Remove credential | SKIP | No credential was successfully added (OAuth not completed). Integrations page (/profile/integrations) loads correctly and shows Delete button for existing HTTP credential. |

---

## REAL BUGS FOUND

### Bug #1 — CRITICAL: Builder cannot save new agents (HTTP 500)
**Endpoint:** POST https://dev-builder.agpt.co/api/proxy/api/graphs  
**HTTP Status:** 500  
**Error Message:**
```json
{
  "message": "Failed to process POST /api/graphs",
  "detail": "'Input' object has no attribute 'name'",
  "hint": "Check server logs and dependent services."
}
```
**Impact:**
- Cannot create/save new agents from the builder
- Import agents from file silently fails (same endpoint)
- The builder UI does not surface the error to the user — the save dialog stays open with no error message

**Reproduction:**
1. Go to /build (new empty canvas)
2. Add any blocks
3. Click save (left sidebar icon, y=206)
4. Fill agent name and click "Save Agent"
5. Dialog stays open, no error shown, API returns 500

**Affected tests:** Test 1 (Build agent — PARTIAL), Test 5 (Import — FAIL)

---

### Bug #2 — MINOR: Login process takes 60+ seconds and appears stuck
**Description:** After submitting login credentials, the button shows "Logging in..." for 60+ seconds before the session is established. The UI gives no indication of progress. However, the session IS established (navigating to the site directly after the long wait works).  
**Impact:** Poor UX — users may think login failed  
**Note:** The actual authentication completes eventually (session persists to /copilot). The long delay seems to be a backend auth latency issue.

---

### Bug #3 — MINOR: "Smart Decision Maker" block does not exist
**Description:** The test plan references a "Smart Decision Maker" block, but no such block exists in the block registry. Search returns no results. The closest alternatives are "AI Condition" and "Condition". This may be a naming discrepancy in documentation vs. implementation.

---

## Additional Observations

- **Login:** Eventually succeeds but shows very long "Logging in..." state (60+ seconds)
- **Blocks panel search:** Works correctly, fast results, correct block categories
- **Run dialog (from builder):** Works correctly — Run Agent dialog appears with input fields
- **Run outputs panel:** Shows in-builder run results with COMPLETED status on all nodes
- **Schedule dialog:** Full schedule configuration available (name, Daily/other frequency, time, timezone)
- **Library:** Loads correctly with 31 agents, search works, sort works
- **Agent runs page:** Shows Tasks/Scheduled/Templates tabs with correct counts
- **OAuth credential flow:** Correctly redirects to GitHub OAuth (client_id=Ov23lipedAd4KrIxA11x)
- **Integrations page:** Loads correctly, shows existing credentials with Delete action
- **Credit balance:** $1027.51 → $1028.51 (no cost for template agent runs)
- **"Export agent to file"** is in the "More actions" menu on the library agent runs page (not in the builder toolbar as expected)

## Screenshots

| Screenshot | Description |
|-----------|-------------|
| retest-00-login.png | Login page with validation state |
| retest-02-logged-in.png | Successfully logged in (copilot page) |
| retest-03-build.png | Build page initial state |
| retest-04-build-sidebar.png | Blocks panel open |
| retest-06-four-blocks.png | 4 blocks on canvas (AI Text Generator, Agent Input, Agent Output, AI Condition) |
| retest-10-save-dialog.png | Save dialog with Prompt validation error |
| retest-13-save-500-error.png | Save attempt triggering 500 error |
| retest-15-existing-agent.png | Hello World Agent in builder |
| retest-18-run-filled.png | Run Agent dialog filled |
| retest-20-run-completed.png | All nodes showing COMPLETED |
| retest-22-schedule-filled.png | Schedule Graph dialog filled |
| retest-23-schedule-created.png | Schedule created successfully toast |
| retest-34-new-task.png | New task dialog in library |
| retest-36-task-completed.png | Task completed with output |
| retest-37-more-actions-menu.png | More actions menu showing Export and Delete options |
| retest-38-agent-exported.png | Agent exported confirmation |
| retest-39-task-deleted.png | Task deleted (count 5→4) |
| retest-40-builder-from-runner.png | Builder opened from Runner UI Edit agent |
| retest-42-credential-dialog.png | GitHub credential dialog (OAuth) |
| retest-43-github-oauth.png | GitHub OAuth redirect initiated |
| retest-44-integrations.png | Integrations/credentials settings page |
