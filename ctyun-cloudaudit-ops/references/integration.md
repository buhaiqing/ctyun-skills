# Cloud Audit Integration Guide

## Cross-Skill Delegation

Cloud Audit is a read-only audit trail that spans all CTyun services. It complements operational skills by providing the "who, what, when" context.

| Context | Skill | Interaction |
|---|---|---|
| Security Investigation | `ctyun-iam-ops` | Audit IAM user activity — create/list/delete users, policy changes |
| Resource Operations | All ops skills | Validate that resource changes were executed as expected |
| Alert Analysis | `ctyun-cloudmonitor-ops` | Cross-reference alarm timestamps with audit events |
| Compliance | `ctyun-oos-ops` | Export audit logs to OOS bucket for long-term retention |

## Skill Boundary

| In scope (this skill) | Out of scope (delegate) |
|---|---|
| Query audit log list | IAM user management → `ctyun-iam-ops` |
| Query by time range | Cloud Monitor alarm management → `ctyun-cloudmonitor-ops` |
| Query by resource type | OOS bucket management → `ctyun-oos-ops` |
| Query by user | ECS/RDS/etc. resource management → respective ops skills |
| View log detail | |
| List tracked services | |
| Export logs to OOS | |
| Query audit statistics | |

## Common Integration Patterns

### Security Incident Investigation

```
Alert Received → Query Audit Logs → Identify Actor → Assess Impact
```

1. Receive alert from `ctyun-cloudmonitor-ops`
2. Query audit logs for the affected resource in the relevant time window via `ctyun-cloudaudit-ops`
3. Identify the user who performed the action
4. Query IAM user details via `ctyun-iam-ops` if needed
5. Take corrective action using the relevant ops skill

### Compliance Audit Trail

```
Select Time Range → List All Events → Verify Users → Export
```

1. Define audit time range (e.g., last 30 days)
2. Query all events via `ctyun-cloudaudit-ops`
3. Verify user accounts and actions against IAM policies
4. Export logs to OOS bucket for archival via `ctyun-cloudaudit-ops`
5. Set OOS lifecycle policy for log retention (via `ctyun-oos-ops`)