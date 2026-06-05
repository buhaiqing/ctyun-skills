---
name: ctyun-cloudaudit-ops
version: 1.0.0
description: >
  Query and manage CTyun Cloud Audit (云审计/CTS) logs — audit trail
  queries, event tracking, compliance reporting, and log export. Primary
  route for any cloud audit, compliance, or security investigation task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: cts.ctapi.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-cloudaudit-ops

## Trigger & Scope

### SHOULD Use

- List audit log events
- Query audit logs by time range
- Query audit logs by resource type
- Query audit logs by user or operator
- Get audit log event details
- List supported services and event types
- Export audit logs to OOS (Object Storage)
- Query audit statistics
- Security incident investigation and forensics
- Compliance reporting and audit trail analysis

### SHOULD NOT Use

- Real-time monitoring or alerting → delegate to `ctyun-cloudmonitor-ops`
- Resource lifecycle management → delegate to the appropriate product skill
- IAM identity management → delegate to `ctyun-iam-ops`
- Bastion host audit sessions → delegate to `ctyun-bastion-ops`
- WAF attack log analysis → delegate to `ctyun-waf-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "audit log" or "云审计" or "operation log" | Route here |
| User asks about "compliance" or "audit trail" | Route here |
| User asks about "who changed what" or "who modified" | Route here |
| User asks about "security investigation" or "incident forensics" | Route here |
| User asks about "bastion audit" or "堡垒机审计" | Route to `ctyun-bastion-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.CTS_ENDPOINT}}` | Agent runtime env | `cts.ctapi.ctyun.cn` |
| `{{user.tracker_name}}` | Ask once, cache per session | `default` |
| `{{user.start_time}}` | Ask once, cache per session | `2026-01-01T00:00:00Z` |
| `{{user.end_time}}` | Ask once, cache per session | `2026-06-05T00:00:00Z` |
| `{{user.resource_type}}` | Ask once, cache per session | `ecs` / `rds` / `iam` |
| `{{user.user_name}}` | Ask once, cache per session | `operator@company.com` |
| `{{user.event_id}}` | Ask once, cache per session | `event-xxxxxxxx` |
| `{{user.bucket_name}}` | Ask once, cache per session | `audit-logs-prod` |
| `{{output.trace_id}}` | Parsed from JSON response | from ListLogs |
| `{{output.event_list}}` | Parsed from JSON response | from QueryLogs |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support Cloud Audit (CTS) operations (verified: `ctyun cts` subcommand does
not exist — note: `ctyun-cli` has a different `audit` module for a
different product, not Cloud Audit). The primary path uses direct REST API
calls to CTyun CTS OpenAPI endpoints with EOP signature authentication.

> **Note:** This is a **read-only** skill. No destructive operations exist.
> All flows query or export audit data only.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and CTS endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List Audit Logs

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{CTS_ENDPOINT}/v1/cts/log/list"
headers = sign_request(
    method="POST",
    url=url,
    body={},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "pageNumber": 1,
    "pageSize": 20
})
data = resp.json()
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Query Audit Logs by Time Range

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/log/query"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "pageNumber": 1,
    "pageSize": 50
})
```

### Flow C: Query Audit Logs by Resource Type

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/log/query"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "resourceType": "{{user.resource_type}}",
    "pageNumber": 1,
    "pageSize": 50
})
```

### Flow D: Query Audit Logs by User

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/log/query"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "userName": "{{user.user_name}}",
    "pageNumber": 1,
    "pageSize": 50
})
```

### Flow E: Get Audit Log Details

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/log/detail"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "traceId": "{{output.trace_id}}",
    "eventId": "{{user.event_id}}"
})
```

### Flow F: List Supported Services

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/services/list"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers)
```

### Flow G: Export Audit Logs to OOS

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/log/export"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "bucketName": "{{user.bucket_name}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

### Flow H: Query Audit Statistics

```python
url = f"https://{CTS_ENDPOINT}/v1/cts/statistics"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

---

## Output Parsing Rules

Cloud Audit API responses follow the standard CTyun JSON format.

| Operation | Data Path | Key Fields |
|---|---|---|
<!-- markdownlint-disable MD013 -->
| List Audit Logs | `$.returnObj[]` | `traceId, eventId, eventName, eventType, resourceType, resourceName, userName, eventTime, sourceIP` |
| Query by Time | `$.returnObj[]` | `traceId, eventId, eventName, eventTime, userName, resourceId` |
| Query by Resource | `$.returnObj[]` | `traceId, eventId, eventName, resourceType, resourceId, userName, eventTime` |
| Query by User | `$.returnObj[]` | `traceId, eventId, eventName, eventTime, resourceType, resourceId, sourceIP, userAgent` |
| Log Detail | `$.returnObj` | `traceId, eventId, eventName, request, response, errorCode, eventTime, regionId, sourceIP` |
<!-- markdownlint-enable MD013 -->
| Services List | `$.returnObj[]` | `serviceName, serviceType, events[]` |
| Export Logs | `$.returnObj` | `exportId, bucketName, status, fileCount, totalSize` |
| Audit Statistics | `$.returnObj` | `totalEvents, eventTypeCounts, dailyEventCounts[], activeUserCount, topUsers[]` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `NoLogsFound` | Business | No | Widen time range or remove filters |
| `TimeRangeTooWide` | Business | No | Split query into smaller time windows |
| `BucketNotFound` | Business | No | Verify OOS bucket exists |
| `ExportInProgress` | Business | No | Wait and retry export status check |
| `SignatureNotMatch` | Environment | 1x | Check credentials and system clock |
| `5xx` / timeout | Runtime | 3x exponential backoff | Retry with 2s → 4s → 8s |
| `requests` ImportError | Environment | 1x | `pip install requests` |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `optional` | Read-only skill — no destructive operations |
| `max_iterations` | `3` | Complex queries may need multiple iterations to converge |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `false` | Read-only — no destructive operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-cloudaudit-ops skill — audit log query, event tracking, log export, statistics |
