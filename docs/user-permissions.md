# User Permissions and Roles

## Overview

This document covers how to view, assign, and revoke user permissions and roles in the system.

---

## Roles

| Role | Description |
|------|-------------|
| `admin` | Full access — can manage users, settings, and all data |
| `editor` | Can create and modify content; cannot manage users or settings |
| `viewer` | Read-only access to content and dashboards |
| `api_user` | Programmatic access only; no UI login |

---

## Viewing a User's Current Roles

Use the admin panel or API:

```bash
GET /api/v2/users/{user_id}/roles
Authorization: Bearer <token>
```

---

## Assigning a Role

### Via Admin Panel
1. Navigate to **Settings → Users**.
2. Search for the user by name or email.
3. Click **Edit** next to their name.
4. Under **Roles**, select the role(s) to assign.
5. Click **Save**.

### Via API

```bash
POST /api/v2/users/{user_id}/roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "editor"
}
```

---

## Revoking a Role

### Via Admin Panel
Follow the same steps as assigning, and deselect the role before saving.

### Via API

```bash
DELETE /api/v2/users/{user_id}/roles/{role_name}
Authorization: Bearer <token>
```

---

## Bulk Role Updates

To update roles for multiple users at once, use the bulk endpoint:

```bash
POST /api/v2/users/roles/bulk
Authorization: Bearer <token>
Content-Type: application/json

{
  "updates": [
    { "user_id": "u_123", "role": "editor", "action": "add" },
    { "user_id": "u_456", "role": "viewer", "action": "remove" }
  ]
}
```

---

## Approval Requirements

- Assigning `admin` role requires approval from an existing admin **and** a manager.
- All role changes are logged in the audit trail under **Settings → Audit Log**.

---

## Notes

- A user can hold multiple roles simultaneously.
- Two-factor authentication (`two_factor_auth` feature flag) is **required** for all users in production — do not disable this flag.
- Role changes take effect immediately; no re-login required.
