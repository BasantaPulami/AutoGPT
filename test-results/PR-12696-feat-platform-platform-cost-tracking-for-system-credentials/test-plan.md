# Test Plan: PR #12696 — feat(platform): platform cost tracking for system credentials

## What changed
- New PlatformCostLog DB model + Prisma schema migration
- Cost tracking in 22 system-credential blocks (LLM, Exa, Apollo, Jina, Google Maps, etc.)
- Copilot cost logging (SDK + baseline paths) via token_tracking.py
- Admin API endpoints: GET /platform-costs/dashboard and GET /platform-costs/logs
- Admin UI at /admin/platform-costs (By Provider / By User / Raw Logs tabs)
- Executor drain: pending cost logs flushed before shutdown

## Scenarios
1. **Migration applied** — PlatformCostLog table exists in DB
2. **Admin API access** — GET /platform-costs/dashboard returns 200 for admin user
3. **Non-admin blocked** — GET /platform-costs/dashboard returns 403 for regular user
4. **Dashboard data** — dashboard endpoint returns provider/user breakdown
5. **Logs endpoint** — GET /platform-costs/logs returns paginated logs
6. **Admin UI loads** — /admin/platform-costs page renders with tabs
7. **Copilot cost logging** — after a copilot turn, PlatformCostLog has a row
8. **Date filter** — dashboard with start/end params filters correctly
9. **Provider filter** — dashboard with provider param filters correctly

## API Tests
1. GET /api/platform-costs/dashboard (admin) → 200
2. GET /api/platform-costs/dashboard (non-admin) → 403
3. GET /api/platform-costs/logs (admin) → 200 with pagination
4. GET /api/platform-costs/dashboard?provider=copilot → filtered result

## UI Tests
1. /admin/platform-costs loads with three tabs
2. "By Provider" tab shows cost table
3. "By User" tab shows user cost table  
4. "Raw Logs" tab shows log entries

## Negative Tests
1. Non-admin user gets 403 on API
2. Invalid date range doesn't crash
