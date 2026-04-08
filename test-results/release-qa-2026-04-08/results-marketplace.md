# Marketplace QA Results — 2026-04-08

**Environment:** https://dev-builder.agpt.co/  
**Account:** zamil.majdy@gmail.com (admin)  
**Session:** qa-fresh-2  
**Date:** 2026-04-08

---

## Summary

| # | Item | Result | Notes |
|---|------|--------|-------|
| 1 | Submit agent to marketplace | PASS | |
| 2 | Approve via admin panel | PARTIAL | Admin panel UI broken (redirects to /onboarding); API endpoint works |
| 3 | Add agent to library from marketplace | PASS | |
| 4 | Run the recently added agent | PASS | |
| 5 | Download agent from marketplace | PASS | |
| 6 | Delete test agent from Creator Dashboard | PARTIAL | Delete blocked for APPROVED status by design; works for REJECTED status |
| 7 | Revoke agent via admin panel | PARTIAL | Admin panel UI broken; API endpoint works |

---

## Detailed Results

### Item 1 — Submit agent to marketplace

**Result: PASS**

Created agent "QA Marketplace Test 2026-04-08" with input/output blocks via the graphs API, then submitted it to the marketplace via `POST /api/proxy/api/store/submissions`. The submission appeared correctly with `PENDING` status on the Creator Dashboard.

- Graph ID: `fea61c88-16b2-4316-ba69-a734ca668ffb`
- Listing ID: `59585a45-a3bb-4762-8294-18243c6cfdf0`
- Listing Version ID: `5cc78899-39c8-4918-964f-d716b5e7f767`
- Screenshot: `mkt-01-submit-pending.png` — Creator Dashboard shows "Awaiting review" badge

---

### Item 2 — Approve agent via admin panel

**Result: PARTIAL**

**BLOCKER: Admin panel UI (`/admin/marketplace`) is inaccessible** — navigating to the page redirects to `/onboarding` (blank white page). The admin UI does not load for any user, including admins.

The underlying API endpoint (`POST /api/proxy/api/store/admin/submissions/{id}/review`) still functions correctly. Approval was performed via direct API call:

```
POST /api/proxy/api/store/admin/submissions/5cc78899-39c8-4918-964f-d716b5e7f767/review
{ "store_listing_version_id": "...", "is_approved": true, "comments": "QA test approval" }
→ 200 OK, agent status changed to APPROVED
```

- Screenshot: `mkt-02-approved-confirmation.png` — Marketplace page after approval
- **Bug:** Admin panel UI redirects to /onboarding instead of showing the marketplace review interface

---

### Item 3 — Add agent to library from marketplace

**Result: PASS**

Used `POST /api/proxy/api/library/agents` with `store_listing_version_id` and `source: "marketplace"`. Agent was successfully added to the library.

- Library Agent ID: `2376852f-1147-46f4-a21d-ca2b3c6311bb`
- API response: 200 OK with full LibraryAgent object
- Screenshot: `mkt-03-agent-in-library.png` — Library page showing the added agent

---

### Item 4 — Run the recently added agent

**Result: PASS**

Executed the agent via `POST /api/proxy/api/graphs/{graphId}/execute/1` with input `{"input_text": "QA Test Run 2026-04-08"}`. Execution completed successfully.

- Execution ID: `16b87bb5-219a-4bfe-949c-cbbad8346d11`
- Execution status: `COMPLETED` (started: 2026-04-08T13:57:48Z, ended: 2026-04-08T13:57:57Z)
- Screenshot: `mkt-04-agent-run-completed.png` — Library page after run

---

### Item 5 — Download agent from marketplace

**Result: PASS**

Downloaded agent graph definition via `GET /api/proxy/api/store/listings/versions/{listingVersionId}/graph/download`. Response returned JSON graph definition with full node/edge structure.

- HTTP 200 with `application/json` content type
- Graph included all nodes, connections, and metadata
- Screenshot: `mkt-05-agent-download.png` — Marketplace agent page

---

### Item 6 — Delete test agent from Creator Dashboard

**Result: PARTIAL**

**Design limitation found:** The Creator Dashboard only shows the Delete option for agents with `PENDING` status. Approved agents only show a "View" option. The backend also blocks deletion of approved submissions (returns HTTP 200 with `false`).

Flow tested:
1. Navigated to Creator Dashboard at `/profile/dashboard` — agent shown with "Approved" status
2. Opened the three-dot action menu — only "View" option available (no Delete)
3. Direct API call `DELETE /api/proxy/api/store/submissions/{listingVersionId}` returned 200 `false` (silently blocked)
4. After Item 7 (agent revoked/rejected), deletion succeeded: API returned 200 `true`
5. Creator Dashboard confirmed agent no longer appears

The delete works but only for non-approved submissions. This is by design per the backend code comment "Prevent deletion of approved submissions".

- Screenshots: `mkt-06a-dashboard-before-delete.png`, `mkt-06b-creator-dashboard.png`, `mkt-06c-delete-dropdown.png`, `mkt-06d-approved-no-delete.png`, `mkt-06e-agent-deleted.png`

**Note:** The UI silently hides the Delete button for approved submissions without explanation. Users may not understand why they cannot delete their approved agents.

---

### Item 7 — Revoke agent via admin panel

**Result: PARTIAL**

Same issue as Item 2: Admin panel UI at `/admin/marketplace` is inaccessible (redirects to /onboarding).

The underlying reject API works correctly:
```
POST /api/proxy/api/store/admin/submissions/5cc78899-39c8-4918-964f-d716b5e7f767/review
{ "store_listing_version_id": "...", "is_approved": false, "comments": "QA test revoke" }
→ 200 OK, agent status changed to REJECTED
```

- Verified via `/api/proxy/api/store/submissions` — agent status changed to `REJECTED`
- Screenshot: `mkt-07-agent-revoked.png` — Creator Dashboard showing agent status

---

## Bugs Found

### BUG-MKT-01 (Critical): Admin marketplace panel inaccessible

**Severity:** Critical  
**URL:** https://dev-builder.agpt.co/admin/marketplace  
**Behavior:** Navigating to `/admin/marketplace` redirects to `/onboarding` page (blank white page). Admin cannot review, approve, or reject marketplace submissions through the UI.  
**Impact:** Items 2 and 7 cannot be completed via the UI. Admin approval/rejection requires direct API calls as a workaround.  
**Expected:** Admin panel should load and show pending marketplace submissions for review.

### BUG-MKT-02 (Minor): Delete returns 200 false for approved submissions

**Severity:** Minor  
**Endpoint:** `DELETE /api/store/submissions/{submission_id}`  
**Behavior:** When attempting to delete an approved submission, the API returns HTTP 200 with body `false` instead of a 4xx error code.  
**Impact:** API clients cannot distinguish this silent failure from a successful delete (also 200 `true`). Should return HTTP 409 Conflict or 422 Unprocessable Entity with an explanatory message.

### BUG-MKT-03 (UX): No UI feedback when delete is blocked for approved agents

**Severity:** UX / Low  
**Location:** Creator Dashboard `/profile/dashboard`  
**Behavior:** The Delete button is hidden entirely for approved submissions with no explanation. Users don't know why they cannot delete their approved agent.  
**Suggestion:** Show a disabled Delete button with a tooltip explaining "Approved agents cannot be deleted" or provide a "Request removal" option.
