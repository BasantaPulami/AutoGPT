# Release QA — Settings Track
**Date:** 2026-04-08  
**Env:** https://dev-builder.agpt.co/  
**Account:** zamil.majdy@gmail.com  
**Session:** qa-settings-1  

---

## Results Summary

| # | Item | Result | Notes |
|---|------|--------|-------|
| 1 | Edit display name to "QA Tester Release" + upload profile photo → Save → verify persistence | PASS | Display name saved via POST to `/api/proxy/api/store/profile`. Photo uploaded via POST to `/api/proxy/api/store/submissions/media`. Both persisted after SPA navigation away and back. Note: profile page has a stability issue — direct navigation triggers session validation redirect within ~1-2s; SPA navigation via profile menu is required. |
| 2 | Settings → Billing → top up $10 with Stripe test card 4242 4242 4242 4242 | FAIL (BUG) | Billing page loads and $10 top-up flow opens Stripe checkout correctly (TEST MODE, card 4242424242424242 accepted, form submits). However Stripe's success redirect URL is configured as `localhost:3000` instead of `https://dev-builder.agpt.co`. After payment processing, Stripe redirects to `http://localhost:3000/copilot` and the credit balance remains at $1027.53 (no $10 added). |
| 3 | Settings → Notifications → turn Agent Run Notifications ON → run agent | PASS | Toggle successfully turned ON (aria-checked: false → true). Saved via POST to `/api/proxy/api/auth/user/preferences` with `AGENT_RUN: true` confirmed in backend response. Text Summarizer agent executed (`POST /api/graphs/.../execute/2`) and completed successfully. |
| 4 | Settings → Notifications → turn Agent Run Notifications OFF → run agent | PASS | Toggle successfully turned OFF (aria-checked: true → false). Saved via POST to `/api/proxy/api/auth/user/preferences` with `AGENT_RUN: false` confirmed via GET check. Text Summarizer agent ran and completed with "Success Execution 100%". |
| 5 | Confirm Non-Code & Config & Infra Changes | SKIP | Manual engineering check — not applicable to automated QA. |

---

## Bugs Found

### BUG-1 (CRITICAL): Stripe success redirect URL points to localhost:3000
**Item:** 2 — Billing top-up  
**Severity:** Critical — blocks credit purchase entirely on dev environment  
**Steps to reproduce:**
1. Go to https://dev-builder.agpt.co/profile/credits
2. Enter $10 in the top-up amount field
3. Click "Top-up" button
4. Fill Stripe checkout with test card 4242 4242 4242 4242, exp 12/27, CVC 123
5. Click "Pay"  
**Expected:** Redirected to `https://dev-builder.agpt.co/profile/credits?session_id=...` and $10 added to balance  
**Actual:** Redirected to `http://localhost:3000/copilot` — payment may have been processed by Stripe but webhook/success redirect fails. Credit balance shows no change ($1027.53).  
**Evidence:** Screenshots `settings-07` through `settings-11`, URL observed: `http://localhost:3000/copilot`  
**Root cause hypothesis:** `STRIPE_SUCCESS_URL` or `NEXT_PUBLIC_APP_URL` env var in the dev environment is set to `http://localhost:3000` instead of `https://dev-builder.agpt.co`.

### BUG-2 (MEDIUM): Profile page session instability — direct navigation triggers redirect
**Item:** 1 — Profile edit  
**Severity:** Medium — degrades UX, blocks direct URL access to `/profile`  
**Description:** Navigating directly to `https://dev-builder.agpt.co/profile` causes the page to redirect to `/profile/dashboard` within ~1-2 seconds. This is caused by `handleFocus`/`handleVisibilityChange` event listeners in `useSupabaseStore.ts` which call `validateSessionInternal()` when the browser window receives focus. The validation appears to fail because `persistSession: false` means session is not in localStorage.  
**Workaround confirmed:** Use SPA navigation via the profile dropdown menu ("Edit profile" link) — this keeps session context alive.  
**Evidence:** Multiple redirect observations during testing. See source: `/autogpt_platform/frontend/src/lib/supabase/hooks/useSupabaseStore.ts`

---

## Screenshots

| Screenshot | Description |
|-----------|-------------|
| settings-02-profile-persisted.png | Profile page showing "QA Tester Release" display name persisted |
| settings-05-profile-verified.png | Profile page after SPA nav showing persisted name + uploaded photo URL confirmed in GCS |
| settings-06-billing-page.png | Billing page loaded with top-up form |
| settings-08-stripe-checkout-loaded.png | Stripe checkout showing $10.00 in TEST MODE |
| settings-10-stripe-form-filled.png | Stripe form with 4242424242424242, 12/27, 123, QA Tester filled |
| settings-11-billing-no-topup.png | Credits page post-attempt showing balance unchanged at $1027.53 |
| settings-13-notifications-on-saved.png | Settings after Agent Run Notifications toggled ON and saved |
| settings-15-agent-run-started.png | Text Summarizer agent run with notifications ON |
| settings-16-notifications-off-saved.png | Settings with Agent Run Notifications toggled OFF |
| settings-17-agent-run-notif-off.png | Text Summarizer agent run with notifications OFF (Success 100%) |
