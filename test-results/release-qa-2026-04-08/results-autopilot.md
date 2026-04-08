# AutoPilot QA Results — 2026-04-08

**Tester:** Automated QA agent  
**Target:** https://dev-builder.agpt.co/  
**Session:** qa-ap2  
**Date:** 2026-04-08  

---

## Results Summary

| # | Item | Result | Notes |
|---|------|--------|-------|
| 1 | Click suggested prompt pill | PASS | "Create" pill expanded showing sub-prompts; clicked "Draft an engineering project proposal." — sent as message, response started immediately |
| 2 | Send "Hello, what can you help me with?" and receive response | PASS | Response received in ~16s ("Ways I Can Assist You" heading with capabilities list) |
| 3 | Start a new chat (New Chat button) | PASS | "New Chat" button present and functional — opens fresh empty thread with welcome screen and prompt pills |
| 4 | Ask AutoPilot to search the web | PASS | Web search executed via Perplexity; results returned with citations about AI news in 2026 including GPT-5.4, quantum computing |
| 5 | Ask AutoPilot to use calculator (1234 × 5678) | PASS | Returned correct result: 1,234 × 5,678 = 7,006,652 ✅ |
| 6 | Ask AutoPilot to create Hello World agent | PASS | Agent created in ~1m 35s; dry-run result "Hello, Zamil!" shown; "Open in library" and "Open in builder" links displayed |
| 7 | Verify created agent appears in Library | PASS | "Hello World Agent" appeared as first result in /library sorted by updatedAt |
| 8 | Run the agent created by AutoPilot | PARTIAL | Agent shows last run result "Hello, Zamil!" but the run was tagged as **Simulated** — not a real execution. No "Run now" prompt flow was offered; clicking the agent opened a pre-existing simulated run. |
| 9 | Ask AutoPilot to edit the created agent | PASS | Agent updated to include date; found GetCurrentDateBlock; "Agent Hello World Agent has been updated!" confirmed |
| 10 | Verify AutoPilot maintains context | PASS | Correctly identified first message: "Create a simple Hello World agent…" |
| 11 | Stop an in-progress response | PARTIAL | Stop button clicked successfully; "You manually stopped this chat" shown. **HOWEVER:** The stopped essay task continued running in the background silently (see Bug #1) |
| 12 | Re-open an existing chat | PASS | "Greetings and Introductions" chat loaded with full prior message history preserved |
| 13 | Ask AutoPilot to use a Twitter auth-required tool | PASS | AutoPilot invoked TwitterPostTweetBlock, showed sign-in prompt, disabled Proceed button, said "A sign-in button for Twitter has appeared in the chat." |
| 14 | Upload a file into AutoPilot chat | PASS | File upload via "Attach file" button worked; "00-login-page.png" shown with remove button |
| 15 | Verify AutoPilot can use uploaded file context | PASS | Accurately described login page: AutoGPT logo, email/password fields, "Continue with Google", cookie consent banner, Marketplace link |
| 16 | Send a voice message (mic button) | PASS | "Start recording" button accessible; clicking it shows clear "Voice recording failed — Microphone permission denied" error message (correct behavior in automated browser) |
| 17 | Ask AutoPilot to schedule an agent | FAIL | Request processed for 4+ minutes (showing "Weighing options... 3m 12s") then terminated with **no response text** — no confirmation, no error, no scheduling UI shown. Scheduling request was silently dropped. |
| 18 | Verify AutoPilot continues after navigation | PASS | Task continued running after navigating to /library and back; returned to same session and found "Thinking..." still active; completed successfully with paper summaries |
| 19 | Trigger a failure case (invalid URL) | PASS | Within 19s returned clear error: "That URL doesn't exist — the domain can't be resolved (no DNS record). The .invalid TLD is actually a reserved domain specifically meant to never work." |

---

## Bugs Found

### Bug #1 — MEDIUM: Stopped response continues silently in background
**Severity:** MEDIUM  
**Item:** 11 (Stop)  
**Description:** After clicking Stop on an in-progress long essay request, the UI showed "You manually stopped this chat". However, in a subsequent session review (when the same thread was opened for Item 17), the essay was found to have completed in full: "Good — 12,788 words of research…" with file output `/home/user/research_text.txt`. The stop did not actually cancel the underlying agent execution.  
**Impact:** User believes task is stopped but it continues consuming credits and resources. User has no visibility into this.  
**Screenshot:** `ap-11-stopped.png`, `ap-17-scheduling.png` (shows essay content in thread)

### Bug #2 — HIGH: Scheduling agent produces no response after 4+ minutes
**Severity:** HIGH  
**Item:** 17 (Schedule agent)  
**Description:** Sending "Schedule the Hello World agent to run every day at 9am" resulted in a 4+ minute processing loop ("Weighing options… 3m 12s") that then silently terminated. No scheduling confirmation, no error message, no scheduling UI, no response text at all was generated. The message shows with no response in the thread.  
**Impact:** Core AutoPilot feature (agent scheduling via chat) is broken — users cannot schedule agents through the chat interface and receive no feedback when it fails.  
**Screenshot:** `ap-17-scheduling.png`, `ap-17-schedule-response.png`

### Bug #3 — LOW: Agent run in Library marked as "Simulated" with no option to run for real
**Severity:** LOW  
**Item:** 8 (Run agent)  
**Description:** The Hello World agent created by AutoPilot shows a pre-existing simulated run result in Library. The run is tagged "Simulated" (not a real execution). There is no obvious "Run now" button shown in the main panel — users must use "Rerun task" to actually run it. The AutoPilot creation flow does a dry run but labels it as "Simulated" which may confuse users.  
**Impact:** Users may not realize the agent hasn't actually run against real infrastructure.  
**Screenshot:** `ap-08-agent-run.png`

### Bug #4 — LOW: Prompt pill category buttons show "Thinking" mode label after response completes
**Severity:** LOW  
**Item:** 1 (Prompt pill)  
**Description:** The "Switch to Fast mode" button label shows "Thinking" as mode indicator even when no response is active. This is a cosmetic/UX issue where "Thinking" in the mode switcher may confuse users into thinking a response is still in progress.  
**Impact:** Minor UX confusion  
**Screenshot:** `ap-02-pill-response.png`

---

## Key Observations

1. **Response times are high for complex tasks:** Agent creation took ~1m 35s; web searches took ~60s; scheduling took 4+ minutes (and failed). For a chat-first product, response latency is a UX concern.

2. **Scheduling feature is non-functional (HIGH):** The most critical gap — AutoPilot cannot schedule agents via chat. This is listed as a supported capability but is broken.

3. **Background execution after stop is a trust/billing concern (MEDIUM):** Users who stop a task are not actually stopping it — it continues running silently. This is a product safety issue.

4. **Core features work well:** Agent creation, context memory, file upload+analysis, web search, tool use, error handling, chat navigation, and persistence all functioned correctly.

5. **Twitter auth flow is integrated but UX unclear:** The sign-in button for Twitter appears in the chat but has no visible label (just an icon at ref=e139). Users may not recognize it as an action button.

---

## Screenshots Index
- `ap-00-copilot-home.png` — Initial AutoPilot home page
- `ap-01-autopilot-home-clean.png` — Clean home state
- `ap-01-prompt-pills.png` — Create pill dropdown showing sub-prompts
- `ap-01-pill-clicked.png` — Pill sent as message
- `ap-02-still-thinking.png` — Response in progress
- `ap-02-pill-response.png` — Pill response received
- `ap-03-new-chat.png` — New chat fresh state
- `ap-04-hello-response.png` — Hello response
- `ap-05-web-search-thinking.png` — Web search in progress
- `ap-05-web-search-response.png` — Web search results
- `ap-05-calculator-response.png` — Calculator result
- `ap-06-agent-creation-start.png` — Agent creation started
- `ap-06-agent-created.png` — Agent created with Open in Library link
- `ap-07-library-hello-world.png` — Hello World Agent in Library
- `ap-08-agent-run.png` — Agent run result (Simulated)
- `ap-09-agent-edited.png` — Agent edit confirmed
- `ap-10-context-memory.png` — Context memory test
- `ap-11-stop-before.png` — Before stop
- `ap-11-stopped.png` — After stop ("You manually stopped this chat")
- `ap-12-reopen-chat.png` — Re-opened chat state
- `ap-12-previous-chat-loaded.png` — Previous chat with messages loaded
- `ap-13-twitter-auth.png` — Twitter auth prompt
- `ap-14-file-uploaded.png` — File uploaded
- `ap-15-image-described.png` — Image description response
- `ap-16-voice-mic.png` — Voice recording permission denied
- `ap-17-scheduling.png` — Scheduling in progress (4+ min)
- `ap-17-schedule-response.png` — No response for schedule request
- `ap-18-before-navigate.png` — Before navigating away
- `ap-18-after-return.png` — After returning (task still running)
- `ap-18-papers-complete.png` — Papers task completed
- `ap-19-failure-case.png` — Invalid URL error response
