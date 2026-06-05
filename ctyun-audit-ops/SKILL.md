---
name: ctyun-audit-ops
version: "1.0.0"
description: >-
  Query and analyze CTyun audit logs for compliance, security review, and
  operational forensics. Read-only operations on Cloud Trace Service (CTS)
  data — list audit logs, filter by time/resource/user, export reports.
license: MIT
compatibility: Python 3.10+, valid API credentials, network access to CTyun endpoints
metadata:
  author: ctyun
  version: "1.0.0"
  last_updated: "2026-06-05"
  runtime: Harness AI Agent
  api_profile: "CTyun Cloud Trace Service API v1.0"
  cli_applicability: sdk-only
  cli_support_evidence: >-
    Audit query operations require structured filtering not available via CLI.
  environment:
    - CTYUN_ACCESS_KEY
    - CTYUN_SECRET_KEY
    - CTYUN_REGION
---

# CTyun Audit Operations Skill

## Overview

Audit Operations provides read-only access to CTyun Cloud Trace Service (CTS)
logs. It allows querying, filtering, and exporting audit trails for compliance,
security investigations, and operational forensics.

This skill is **read-only** and **SDK-only**.

## Trigger & Scope

### SHOULD Use This Skill When

- User asks to "view audit logs", "check audit trail", or "run compliance report"
- User needs to filter audit events by user, resource, or time range
- User asks about "who changed what" or "when was this resource modified"
- User needs to export audit data for external analysis

### SHOULD NOT Use This Skill When

- User asks about **real-time monitoring** → delegate to `ctyun-cloudmonitor-ops`
- User asks about **alert rules** → delegate to `ctyun-cloudmonitor-ops`
- User asks to **modify** audit configuration → not supported (read-only)

### Delegation Rules

| Condition | Action |
|-----------|--------|
| Real-time resource metrics | Route to `ctyun-cloudmonitor-ops` |
| IAM permission audit | Route to `ctyun-iam-ops` |

## Variable Convention

| Placeholder | Resolution | Example |
|-------------|------------|---------|
| `{{env.CTYUN_ACCESS_KEY}}` | Runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Runtime env | never prompt |
| `{{env.CTYUN_REGION}}` | Runtime env | `cn-gz` |
| `{{user.start_time}}` | Ask user once | `2026-01-01T00:00:00Z` |
| `{{user.end_time}}` | Ask user once | `2026-06-01T00:00:00Z` |
| `{{user.user_name}}` | Ask user once | `admin@example.com` |
| `{{user.resource_type}}` | Ask user once | `ecs`, `vpc` |

## Execution Flows

### Operation: ListAuditLogs

1. Call SDK to list audit logs:
   ```python
   from ctyun_sdk.services.cts.client import CTSClient
   client = CTSClient(credential, region)
   logs = client.list_traces(
       start_time="{{user.start_time}}",
       end_time="{{user.end_time}}",
   )
   ```
2. Parse response: extract trace list with `traceId`, `user`, `resourceType`, `time`
3. Return structured log entries

### Operation: FilterAuditLogs

1. Query audit logs with optional filters (user, resource type, trace status)
2. Apply server-side filtering where possible
3. Return filtered result set

### Operation: ExportAuditReport

1. Query audit logs for the requested time range
2. Format as Markdown or CSV summary
3. Return formatted report with key statistics

## Output Parsing Rules

| Operation | Key Field | Description |
|-----------|-----------|-------------|
| ListAuditLogs | `traces[]` | List of audit trace entries |
| FilterAuditLogs | `traces[]` | Filtered list |
| ExportAuditReport | `report` | Formatted report string |

## Failure Recovery

| Error Pattern | Retry | Agent Action |
|---------------|-------|--------------|
| Time range > 30 days | 0 | Narrow window |
| `InvalidParameter` | 0 | Fix and retry |
| `AccessDenied` | 0 | Delegate to `ctyun-iam-ops` |
| `InternalError` | 2 (2s, 4s) | Retry with backoff |

## Quality Gate (GCL)

| Parameter | Value | Reason |
|-----------|-------|--------|
| `gcl_mode` | `optional` | read-only |
| `max_iterations` | `5` | report quality can improve with iteration |
| `rubric_version` | `v1` | see `references/rubric.md` |
| `safety_confirm_required` | `false` | all operations read-only |

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-05 | Initial audit operations skill — list/filter/export audit logs |