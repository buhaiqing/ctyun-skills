# Cloud Audit Monitoring & Observability

## Overview

Cloud Audit is a **read-only** audit trail. "Monitoring" in this context refers to checking audit log coverage and investigating suspicious activity — not monitoring health metrics.

## Audit Coverage Checks

| Check | Frequency | Purpose |
|---|---|---|
| Verify audit logs being generated | Daily | Ensure CTS is actively recording events |
| Check for gaps in event coverage | Weekly | Identify services not producing audit events |
| Review failed event records | Daily | Identify API failures across the account |
| Export logs to OOS for long-term storage | Monthly | Compliance requirement |

## Security Monitoring

| Pattern | Investigation | Action |
|---|---|---|
| Failed login attempts spike | Possible brute force attack | Check IAM users, rotate keys |
| API calls from unusual region | Possible credential compromise | Investigate the user and source IP |
| Resource deletion events | Verify authorized action | Cross-reference with incident tickets |
| IAM policy changes | Verify authorized modification | Audit trail for privilege escalations |
| Unusual API call volume | Possible automated abuse | Identify the caller and purpose |

## Cloud Monitor Integration

Cloud Audit statistics can feed into Cloud Monitor (`ctyun-cloudmonitor-ops`) for alerting:

| Scenario | Alarm Suggestion |
|---|---|
| No audit events for > 1 hour | CTS may be misconfigured or degraded |
| High number of failed API calls | Underlying infrastructure or permission issues |
| Sensitive operation detected | IAM policy change, key deletion, instance deletion |

## Operational Recommendations

| Check | Frequency | Action |
|---|---|---|
| Review recent audit events | Daily | Identify unusual patterns |
| Run audit statistics | Weekly | Track operation volume trends |
| Verify service coverage | Monthly | Confirm all active services produce audit logs |
| Export and archive logs | Monthly | Meet compliance retention requirements |
| Review user activity | Monthly | Verify users map to current IAM roles |