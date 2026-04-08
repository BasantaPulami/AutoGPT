# Test Plan: PR #12696 — feat(platform/admin): cost tracking for system credentials

## Summary
Adds end-to-end cost tracking for API calls made by backend blocks (LLM, Exa, Apollo, Google Maps, etc.).
- New `PlatformCostLog` table (via Prisma migration)
- Admin API: `GET /api/admin/platform-costs/dashboard` and `/logs`
- Admin frontend: `/admin/platform-costs` page with summary cards, provider table, user table, logs table
- Cost is tracked when blocks execute (executor hooks + copilot token tracking)

## Scenarios

### 1. Migration & Schema
- PlatformCostLog table exists in DB after migration

### 2. Admin API — Dashboard (requires admin JWT)
- `GET /api/admin/platform-costs/dashboard` returns 200 with PlatformCostDashboard schema
- Non-admin gets 403

### 3. Admin API — Logs (requires admin JWT)
- `GET /api/admin/platform-costs/logs` returns 200 with paginated CostLogRow list
- Pagination params (page, page_size) work correctly
- Non-admin gets 403

### 4. Cost tracking on execution
- Run a graph with LLM block — a PlatformCostLog row should be inserted
- Dashboard shows the cost after execution

### 5. Frontend admin page
- `/admin/platform-costs` loads for admin user
- Summary cards render
- Provider table shows cost breakdown

## Negative Tests
- Non-admin user gets 403 from both dashboard and logs endpoints
- Zero-cost entries are not logged (if applicable)
