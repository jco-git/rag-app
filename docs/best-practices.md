# Best Practices

General guidelines for working with this system safely and effectively.

---

## Configuration Changes

- **Never edit `config/` files directly in production.** Use the deployment pipeline to promote config changes from development → staging → production.
- Always validate JSON config files before deploying (`jq . config/app-settings.json`).
- Prefer increasing `cache_ttl_seconds` in production to reduce database load; coordinate with the platform team before changing `max_connections`.

---

## Feature Flags

- New features should start disabled in production (`"status": "disabled"`, `"rollout_percentage": 0`).
- Use incremental rollout percentages (e.g., 5% → 25% → 100%) when enabling features in production.
- Assign an `owner` team and link a ticket for every flag — orphaned flags without owners must be cleaned up.
- Remove flags from `config/feature-flags.json` once a feature has been fully rolled out and is stable.

---

## User and Role Management

- Follow the **principle of least privilege** — assign the minimum role needed for a user's job.
- Review and audit user roles quarterly. Remove roles for users who no longer need them.
- The `admin` role must never be assigned without dual approval (see `user-permissions.md`).
- Offboard departing users within 24 hours: deactivate their account and revoke all roles.

---

## API Usage

- Always use `v2` API endpoints. The `legacy_api_v1` flag is enabled only temporarily in production and will be sunset in Q3 — migrate any integrations now.
- Rotate API tokens every 90 days. Never commit tokens to source control.
- Respect the rate limit (`rate_limit_rpm`). Implement exponential backoff when you receive `429` responses.

---

## Incidents and Escalation

- For production issues, check the audit log and recent config/flag changes first — most incidents trace back to a recent change.
- Write a PIR for any SEV1 or SEV2 incident within 2 business days.
- Notify affected users promptly and clearly; avoid technical jargon in user-facing communications.

---

## General

- Keep documentation up to date. If you change a process, update the relevant doc in the same PR/commit.
- Prefer reversible changes over irreversible ones. Use feature flags to roll back quickly without a redeploy.
- When in doubt, test in staging before production.
