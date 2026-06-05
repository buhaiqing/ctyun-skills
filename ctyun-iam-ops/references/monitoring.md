# IAM Monitoring

## Available Metrics

IAM operations can be monitored through CTyun's Cloud Monitor and audit trails.
Full alarm rule configuration is delegated to `ctyun-cloudmonitor-ops`.

## Audit Events (Cloud Trail)

IAM operations generate audit events that can be tracked:

| Event Type | Description | Severity |
|---|---|---|
| `IAM.CreateUser` | New IAM user created | Info |
| `IAM.DeleteUser` | IAM user deleted | Warning |
| `IAM.CreateAccessKey` | Access key created | Info |
| `IAM.DeleteAccessKey` | Access key deleted | Warning |
| `IAM.AttachGroupPolicy` | Policy attached to group | Info |
| `IAM.DetachGroupPolicy` | Policy detached from group | Info |
| `IAM.CreateRole` | IAM role created | Info |
| `IAM.DeleteRole` | IAM role deleted | Warning |
| `IAM.UpdateAccessKey` | Access key status changed | Info |

## Recommended Alarm Rules

| Metric | Condition | Suggested Threshold | Action |
|---|---|---|---|
| Access key created | Count > 0 in 24h | Alert if > 3 | Review for unusual activity |
| Access key deleted | Count > 0 in 1h | Alert on any | Confirm intentional |
| User deleted | Count > 0 in 1h | Alert on any | Confirm intentional |
| Failed IAM API calls | Rate increase | > 50 in 5 min | Check for misconfigured clients |
| IAM policy change | Any policy CRUD | Alert on any | Review for privilege escalation |

## Security Indicators

| Indicator | Healthy | Warning | Critical |
|---|---|---|---|
| Active access keys per user | ≤ 2 | = 2 | N/A (max) |
| Inactive access keys | < 10% of total | 10–30% | > 30% |
| IAM users with MFA | > 80% | 50–80% | < 50% |
| Orphaned access keys (user deleted) | 0 | 0 | > 0 (security risk) |
| Custom policies without attachment | < 20% | 20–40% | > 40% |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for IAM events
- `ctyun-audit-ops` (planned) — Query IAM audit trails
