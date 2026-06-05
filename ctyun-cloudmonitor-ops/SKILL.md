---
name: ctyun-cloudmonitor-ops
description: >-
  Use when the user needs to deploy, configure, manage, troubleshoot, or monitor
  CTyun Cloud Monitor (云监控) resources via API, SDK, or the ctyun CLI. Trigger when
  the user mentions Cloud Monitor, 云监控, alarm rules, metric data, monitoring,
  or alarm history in an operational context — even if they do not explicitly
  mention 'CTyun' or 'API'. Also use when the user asks about ctyun CLI
  commands for cloudmonitor, ctyun SDK usage, OpenAPI operations, or automation scripts for
  alarm management and metric querying. Do not use for billing-only or IAM-only tasks; delegate to the
  appropriate dedicated skill.
license: MIT
compatibility: >-
  Official CTyun SDK (Python 3.10+), valid API credentials, network
  access to CTyun endpoints, and official CTyun CLI (`ctyun`) for cloudmonitor
  operations (dual-path skill).
metadata:
  author: ctyun
  version: "1.1.0"
  last_updated: "2026-06-05"
  runtime: Harness AI Agent
  api_profile: "CTyun Cloud Monitor API v1 - OpenAPI: https://www.ctyun.cn/document/10029510"
  cli_applicability: dual-path
  cli_support_evidence: >-
    `ctyun cloudmonitor --help` confirms CLI support for Cloud Monitor operations.
    Official documentation: https://www.ctyun.cn/document/10029510
  sdk_version_locked: ">=1.0.0"
  cli_version_locked: ">=1.0.0"
  environment:
    - CTYUN_ACCESS_KEY
    - CTYUN_SECRET_KEY
    - CTYUN_REGION
    - CTYUN_ACCOUNT_ID
---

> This skill follows the [Agent Skill OpenSpec](https://agentskills.io/specification).

# CTyun Cloud Monitor Operations Skill

## Overview

Cloud Monitor (云监控) on CTyun provides comprehensive monitoring capabilities for cloud resources, including metric collection, alarm rule management, and alarm history tracking. This skill is an **operational runbook** for agents: explicit scope, credential rules, pre-flight checks, **dual-path execution** (official **SDK/API** and **ctyun CLI** flows), response validation, and failure recovery. **Do not use the web console as the primary agent execution path** in `SKILL.md`.

### Primary Resources

| Resource | Description | Key Operations |
|----------|-------------|----------------|
| Alarm Rule | Defines metric thresholds and notification actions | Create, Describe, Modify, Delete |
| Alarm Blacklist | Suppresses notifications for specific resources/metrics without disabling the alarm rule | Create, Query, Update, Change Status, Delete |
| Metric Data | Time-series monitoring data from cloud resources | Query, List |
| Alarm History | Historical alarm events and status changes | List, Describe |

### CLI applicability (repository policy)

- **`cli_applicability: dual-path`:** Official `ctyun` supports Cloud Monitor operations. This skill documents **both** SDK steps **and** `ctyun` CLI steps for every operation. See `references/cli-usage.md` for CLI-specific commands.

## Trigger & Scope (Agent-Readable)

### SHOULD Use This Skill When

- User mentions "CTyun Cloud Monitor" OR "天翼云监控" OR "云监控"
- Task involves CRUD operations on **alarm rules** (create, describe, modify, delete)
- Task involves **metric data** operations (query metrics, list metrics)
- Task involves **alarm history** operations (list history, describe alarm events)
- Task keywords: alarm, alert, metric, monitoring, threshold, notification, cloudmonitor
- User asks to configure monitoring, set up alerts, or query resource metrics via API, SDK, CLI, or automation

### SHOULD NOT Use This Skill When

- Task is purely billing / account management → delegate to: `ctyun-billing-ops` (when present)
- Task is IAM / permission model only → delegate to: `ctyun-iam-ops` (when present)
- Task is about **ECS/VM resource lifecycle** → delegate to: `ctyun-ecs-ops` (when present)
- Task is about **RDS database operations** → delegate to: `ctyun-rds-ops` (when present)
- User insists on **console-only** flows with no API → state limitation; do not invent undocumented HTTP steps

### Delegation Rules

- If creating an alarm rule for a specific resource type (e.g., ECS), verify the resource exists via the appropriate skill before creating the alarm.
- Multi-product monitoring requests: handle Cloud Monitor operations with this skill; resource operations with their respective skills.

## Variable Convention (Agent-Readable)

Structured placeholders reduce injection ambiguity and unsafe prompts:

| Placeholder | Meaning | Agent Action |
|-------------|---------|--------------|
| `{{env.CTYUN_ACCESS_KEY}}` | From runtime environment | NEVER ask the user; fail if unset |
| `{{env.CTYUN_SECRET_KEY}}` | From runtime environment | NEVER ask the user; fail if unset |
| `{{env.CTYUN_REGION}}` | From runtime environment | Use documented default only if skill explicitly allows |
| `{{user.region}}` | User-supplied region | Ask once; reuse |
| `{{user.alarm_name}}` | User-supplied alarm rule name | Ask once; reuse |
| `{{user.namespace}}` | Metric namespace (e.g., ECS, RDS) | Ask once; reuse |
| `{{user.metric_name}}` | Metric name (e.g., CPUUtilization) | Ask once; reuse |
| `{{user.resource_id}}` | Target resource ID for alarm | Ask once; reuse |
| `{{output.alarm_id}}` | From CreateAlarmRule response | Parse per OpenAPI/SDK or verified `ctyun --output json` path |
| `{{output.metric_data}}` | From QueryMetricData response | Parse per API response structure |
| `{{output.alarm_history}}` | From ListAlarmHistory response | Parse per API response structure |
| `{{user.blacklist_name}}` | User-supplied blacklist name | Ask once; reuse |
| `{{user.service_type}}` | Cloud service type (ECS, RDS, etc.) | Ask once; reuse |
| `{{user.device_uuid}}` | Resource ID to blacklist | Ask once; reuse |
| `{{output.blacklist_id}}` | From CreateAlarmBlacklist response | Parse from `$.data.id` |
| `{{output.blacklist_records}}` | From QueryAlarmBlacklists response | Parse from `$.data.result` |

> **`{{env.*}}` MUST NOT** be collected from the user. **`{{user.*}}`** MUST be collected interactively when missing.

> **Security Warning:** **NEVER** log, print, or expose `CTYUN_SECRET_KEY` (or any secret) in console output, debug messages, or logs. When verification is needed, check existence only (e.g., `if os.environ.get('CTYUN_SECRET_KEY')`) without printing the actual value. If logging credential status is required, use masked placeholders like `CTYUN_SECRET_KEY=<masked>` or `CTYUN_SECRET_KEY=***`.

## Output Parsing Rules

### Alarm Rule Operations

| Operation | JSON Path (SDK) | JSON Path (CLI) | Type | Description |
|-----------|-----------------|-----------------|------|-------------|
| CreateAlarmRule | `$.result.alarmId` | `$.result.alarmId` | string | New alarm rule ID |
| DescribeAlarmRules | `$.result.alarms[*].alarmId` | `$.result.alarms[*].alarmId` | array | List of alarm rule IDs |
| DescribeAlarmRules | `$.result.alarms[*].alarmName` | `$.result.alarms[*].alarmName` | array | List of alarm rule names |
| DescribeAlarmRules | `$.result.alarms[*].status` | `$.result.alarms[*].status` | array | Alarm rule status (enabled/disabled) |
| ModifyAlarmRule | `$.result.success` | `$.result.success` | boolean | Modification success flag |
| DeleteAlarmRule | `$.result.success` | `$.result.success` | boolean | Deletion success flag |

### Metric Data Operations

| Operation | JSON Path (SDK) | JSON Path (CLI) | Type | Description |
|-----------|-----------------|-----------------|------|-------------|
| ListMetrics | `$.result.metrics[*].metricName` | `$.result.metrics[*].metricName` | array | Available metric names |
| ListMetrics | `$.result.metrics[*].namespace` | `$.result.metrics[*].namespace` | array | Metric namespaces |
| QueryMetricData | `$.result.datapoints[*].timestamp` | `$.result.datapoints[*].timestamp` | array | Data point timestamps |
| QueryMetricData | `$.result.datapoints[*].value` | `$.result.datapoints[*].value` | array | Data point values |
| QueryMetricData | `$.result.unit` | `$.result.unit` | string | Metric unit (Percent, Bytes, etc.) |

### Alarm History Operations

| Operation | JSON Path (SDK) | JSON Path (CLI) | Type | Description |
|-----------|-----------------|-----------------|------|-------------|
| ListAlarmHistory | `$.result.history[*].alarmId` | `$.result.history[*].alarmId` | array | Alarm rule IDs |
| ListAlarmHistory | `$.result.history[*].status` | `$.result.history[*].status` | array | Alarm status (ALARM, OK, INSUFFICIENT_DATA) |
| ListAlarmHistory | `$.result.history[*].timestamp` | `$.result.history[*].timestamp` | array | Event timestamp |

### Alarm Blacklist Operations

| Operation | JSON Path (SDK/API) | JSON Path (CLI) | Type | Description |
|-----------|---------------------|-----------------|------|-------------|
| CreateAlarmBlacklist | `$.data.id` | `$.data.id` | string | New blacklist ID |
| QueryAlarmBlacklists | `$.data.result[*].id` | `$.data.result[*].id` | array | Blacklist IDs |
| QueryAlarmBlacklists | `$.data.result[*].blacklistName` | `$.data.result[*].blacklistName` | array | Blacklist names |
| QueryAlarmBlacklists | `$.data.result[*].status` | `$.data.result[*].status` | array | Blacklist status (0=disabled, 1=enabled) |
| QueryAlarmBlacklists | `$.data.result[*].deviceUUID` | `$.data.result[*].deviceUUID` | array | Blacklisted resource IDs |
| QueryAlarmBlacklists | `$.data.totalCount` | `$.data.totalCount` | int | Total matching records |
| UpdateAlarmBlacklist | `$.code` | `$.code` | string | "200" = success |
| ChangeAlarmBlacklistsStatus | `$.code` | `$.code` | string | "200" = success |
| DeleteAlarmBlacklists | `$.code` | `$.code` | string | "200" = success |

### Expected State Transitions

| Operation | Initial State | Target State | Poll Interval | Max Wait |
|-----------|---------------|--------------|---------------|----------|
| CreateAlarmRule | — | `enabled` | N/A | Immediate |
| ModifyAlarmRule | any | updated config | N/A | Immediate |
| EnableAlarmRule | `disabled` | `enabled` | N/A | Immediate |
| DisableAlarmRule | `enabled` | `disabled` | N/A | Immediate |
| DeleteAlarmRule | any stable state | absent | 5s | 60s |
| CreateAlarmBlacklist | — | `enabled` (status=1) | N/A | Immediate |
| ChangeAlarmBlacklistsStatus | any | `enabled` (1) or `disabled` (0) | N/A | Immediate |
| DeleteAlarmBlacklists | any | absent | 5s | 60s |

## Execution Flows (Agent-Readable)

Every operation: **Pre-flight → Execute (SDK/API and `ctyun`) → Validate → Recover**. Do not skip phases.

**Execution Preference:** When both paths exist, prefer `ctyun` CLI for quick ad-hoc operations; prefer SDK for programmatic automation or complex workflows.

---

### Operation: CreateAlarmRule

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| SDK / deps | Import client; version matches `metadata.api_profile` | No import error | Document install pin |
| CLI / deps | `ctyun --version` | Exit code 0 | Document CLI install / `ctyun config init` |
| Credentials | Construct credential from env (SDK) or CLI config | Non-empty keys / valid config | HALT; user configures env |
| Region | Validate `{{user.region}}` is supported | Region exists in CTyun | Suggest valid region |
| Resource | Verify `{{user.resource_id}}` exists in target namespace | Resource found | HALT; verify resource ID |
| Quota | Check alarm rule quota | Sufficient quota | HALT; user raises quota |

#### Execution (Python SDK)

```python
import os
from ctyun_sdk.core.credential import Credential
from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient
from ctyun_sdk.services.cloudmonitor.apis.create_alarm_rule import CreateAlarmRuleRequest

credential = Credential(os.environ["CTYUN_ACCESS_KEY"], os.environ["CTYUN_SECRET_KEY"])
client = CloudMonitorClient(credential, os.environ.get("CTYUN_REGION", "cn-gz"))

req = CreateAlarmRuleRequest(
    regionId="{{user.region}}",
    alarmName="{{user.alarm_name}}",
    namespace="{{user.namespace}}",
    metricName="{{user.metric_name}}",
    resourceId="{{user.resource_id}}",
    period=300,  # 5 minutes
    statistic="Average",
    comparisonOperator="GreaterThanThreshold",
    threshold=80.0,
    evaluationCount=3,
    alarmActions=["arn:ctyun:sms:{{user.region}}:{{env.CTYUN_ACCESS_KEY}}:alert"],
    okActions=[],
    insufficientDataActions=[]
)
resp = client.create_alarm_rule(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor create-alarm-rule \
  --region-id "{{user.region}}" \
  --alarm-name "{{user.alarm_name}}" \
  --namespace "{{user.namespace}}" \
  --metric-name "{{user.metric_name}}" \
  --resource-id "{{user.resource_id}}" \
  --period 300 \
  --statistic Average \
  --comparison-operator GreaterThanThreshold \
  --threshold 80.0 \
  --evaluation-count 3 \
  --alarm-actions '["arn:ctyun:sms:{{user.region}}:{{env.CTYUN_ACCESS_KEY}}:alert"]'
```

#### Post-execution Validation

1. Read `{{output.alarm_id}}` from `$.result.alarmId` in the response.
2. Call **DescribeAlarmRules** to verify the alarm exists and is in `enabled` state.
3. On success, report `{{output.alarm_id}}` to the user.
4. On failure, go to **Failure Recovery**.

#### Failure Recovery

| Error pattern | Max retries | Backoff | Agent Action |
|--------------|-------------|---------|--------------|
| `InvalidParameter` / 400 invalid input | 0–1 | — | Fix args from OpenAPI; retry once if safe |
| `ResourceNotFound` | 0 | — | HALT; verify resource ID |
| `QuotaExceeded` | 0 | — | HALT |
| `AlarmNameAlreadyExists` | 0 | — | Ask reuse vs new name |
| Throttling / 429 | 3 | exponential | Back off; respect `Retry-After` |
| `InternalError` / 5xx | 3 | 2s, 4s, 8s | Retry; then HALT |

---

### Operation: DescribeAlarmRules

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.describe_alarm_rules import DescribeAlarmRulesRequest

req = DescribeAlarmRulesRequest(
    regionId="{{user.region}}",
    alarmId="{{user.alarm_id}}",  # optional: filter by ID
    alarmName="{{user.alarm_name}}",  # optional: filter by name
    namespace="{{user.namespace}}",  # optional: filter by namespace
    pageNumber=1,
    pageSize=50
)
resp = client.describe_alarm_rules(req)
```

#### Execution — CLI (`ctyun`)

```bash
# List all alarm rules
ctyun --output json cloudmonitor describe-alarm-rules \
  --region-id "{{user.region}}" \
  --page-number 1 \
  --page-size 50

# Filter by alarm name
ctyun --output json cloudmonitor describe-alarm-rules \
  --region-id "{{user.region}}" \
  --alarm-name "{{user.alarm_name}}"
```

#### Present to User

| Field | Path (SDK/CLI) | Notes |
|-------|----------------|-------|
| Alarm ID | `$.result.alarms[*].alarmId` | Unique identifier |
| Alarm Name | `$.result.alarms[*].alarmName` | User-defined name |
| Status | `$.result.alarms[*].status` | enabled/disabled |
| Namespace | `$.result.alarms[*].namespace` | Metric namespace |
| Metric | `$.result.alarms[*].metricName` | Monitored metric |
| Threshold | `$.result.alarms[*].threshold` | Alert threshold |

---

### Operation: ModifyAlarmRule

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Alarm exists | Call DescribeAlarmRules with `{{user.alarm_id}}` | Alarm found | HALT; verify alarm ID |
| User confirmation | Explicit confirmation for changes | Confirmed | HALT; wait for confirmation |

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.modify_alarm_rule import ModifyAlarmRuleRequest

req = ModifyAlarmRuleRequest(
    regionId="{{user.region}}",
    alarmId="{{output.alarm_id}}",
    threshold=90.0,  # new threshold
    evaluationCount=5  # new evaluation count
    # Only include fields to modify; omit others
)
resp = client.modify_alarm_rule(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor modify-alarm-rule \
  --region-id "{{user.region}}" \
  --alarm-id "{{output.alarm_id}}" \
  --threshold 90.0 \
  --evaluation-count 5
```

#### Post-execution Validation

1. Call **DescribeAlarmRules** to verify changes applied.
2. Confirm new configuration matches requested changes.

---

### Operation: DeleteAlarmRule

#### Pre-flight (Safety Gate)

**CRITICAL SAFETY REQUIREMENT:**

- **MUST** obtain explicit confirmation: "Are you sure you want to permanently delete alarm rule `{{user.alarm_name}}` (ID: `{{user.alarm_id}}`)? This action cannot be undone."
- **MUST NOT** proceed without clear user assent (e.g., "yes", "confirm", "delete").
- Document the alarm configuration (call DescribeAlarmRules first) for potential recovery/recreation.

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.delete_alarm_rule import DeleteAlarmRuleRequest

req = DeleteAlarmRuleRequest(
    regionId="{{user.region}}",
    alarmId="{{user.alarm_id}}"
)
resp = client.delete_alarm_rule(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor delete-alarm-rule \
  --region-id "{{user.region}}" \
  --alarm-id "{{user.alarm_id}}"
```

#### Post-execution Validation

1. Poll **DescribeAlarmRules** until the alarm is no longer returned (404 or absent from list).
2. Timeout after 60 seconds if alarm still appears.
3. Report deletion success or failure to user.

#### Failure Recovery

| Error pattern | Max retries | Backoff | Agent Action |
|--------------|-------------|---------|--------------|
| `ResourceNotFound` / 404 | 0 | — | Alarm already deleted; report success |
| Throttling / 429 | 3 | exponential | Back off; retry |
| `InternalError` / 5xx | 3 | 2s, 4s, 8s | Retry; then HALT |

---

### Operation: QueryMetricData

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Valid time range | Start time < End time | Range valid | HALT; fix time range |
| Supported period | Period in [60, 300, 3600, 86400] | Valid period | Adjust to nearest valid |

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.query_metric_data import QueryMetricDataRequest
from datetime import datetime, timedelta

req = QueryMetricDataRequest(
    regionId="{{user.region}}",
    namespace="{{user.namespace}}",
    metricName="{{user.metric_name}}",
    resourceId="{{user.resource_id}}",
    startTime=(datetime.now() - timedelta(hours=1)).isoformat(),
    endTime=datetime.now().isoformat(),
    period=300,  # 5 minutes
    statistic="Average"
)
resp = client.query_metric_data(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor query-metric-data \
  --region-id "{{user.region}}" \
  --namespace "{{user.namespace}}" \
  --metric-name "{{user.metric_name}}" \
  --resource-id "{{user.resource_id}}" \
  --start-time "2026-06-05T00:00:00Z" \
  --end-time "2026-06-05T01:00:00Z" \
  --period 300 \
  --statistic Average
```

#### Present to User

| Field | Path (SDK/CLI) | Notes |
|-------|----------------|-------|
| Timestamps | `$.result.datapoints[*].timestamp` | ISO 8601 format |
| Values | `$.result.datapoints[*].value` | Metric values |
| Unit | `$.result.unit` | Percent, Bytes, Count, etc. |

---

### Operation: ListMetrics

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.list_metrics import ListMetricsRequest

req = ListMetricsRequest(
    regionId="{{user.region}}",
    namespace="{{user.namespace}}"  # optional: filter by namespace
)
resp = client.list_metrics(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor list-metrics \
  --region-id "{{user.region}}" \
  --namespace "{{user.namespace}}"
```

#### Present to User

| Field | Path (SDK/CLI) | Notes |
|-------|----------------|-------|
| Metric Name | `$.result.metrics[*].metricName` | Available metric name |
| Namespace | `$.result.metrics[*].namespace` | Metric namespace |
| Description | `$.result.metrics[*].description` | Human-readable description |
| Unit | `$.result.metrics[*].unit` | Default unit |

---

### Operation: ListAlarmHistory

#### Execution (Python SDK)

```python
from ctyun_sdk.services.cloudmonitor.apis.list_alarm_history import ListAlarmHistoryRequest
from datetime import datetime, timedelta

req = ListAlarmHistoryRequest(
    regionId="{{user.region}}",
    alarmId="{{user.alarm_id}}",  # optional: filter by alarm
    startTime=(datetime.now() - timedelta(days=7)).isoformat(),
    endTime=datetime.now().isoformat(),
    pageNumber=1,
    pageSize=100
)
resp = client.list_alarm_history(req)
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json cloudmonitor list-alarm-history \
  --region-id "{{user.region}}" \
  --start-time "2026-05-29T00:00:00Z" \
  --end-time "2026-06-05T00:00:00Z" \
  --page-number 1 \
  --page-size 100
```

#### Present to User

| Field | Path (SDK/CLI) | Notes |
|-------|----------------|-------|
| Timestamp | `$.result.history[*].timestamp` | Event time |
| Alarm ID | `$.result.history[*].alarmId` | Related alarm rule |
| Status | `$.result.history[*].status` | ALARM/OK/INSUFFICIENT_DATA |
| Metric Value | `$.result.history[*].metricValue` | Value at trigger |
| Reason | `$.result.history[*].reason` | Trigger reason |

---

### Operation: CreateAlarmBlacklist

#### Prerequisites

- **Feature activation:** Alarm Blacklist is a "受限开放" (restricted access) feature. Verify that the CTyun customer manager has enabled it for this account before proceeding.
- **Endpoint:** This operation uses the Monitor v4 API endpoint (`monitor-global.ctapi.ctyun.cn`), not the standard Cloud Monitor API endpoint. Authentication requires AK/SK signature headers.

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Feature activation | Confirm via customer manager or existing blacklist query | Feature enabled | HALT; advise user to request activation |
| Resource exists | Verify `{{user.device_uuid}}` exists in target service | Resource found | HALT; verify resource ID |
| Duplicate check | Query existing blacklists for the same device+metric | No duplicate | HALT; blacklist already exists for this combination |

#### Execution (SDK — `requests`)

```python
import requests
import json

url = "https://monitor-global.ctapi.ctyun.cn/v4/monitor/create-alarm-blacklist"
headers = {
    "Content-Type": "application/json",
    # Auth headers — see CTyun Monitor v4 auth docs
    "ctyun-account": "{{env.CTYUN_ACCOUNT_ID}}",
}

payload = {
    "regionId": "{{user.region}}",
    "blacklistName": "{{user.blacklist_name}}",
    "serviceType": "{{user.service_type}}",
    "deviceUUID": "{{user.device_uuid}}",
    "dimension": "InstanceId",
    "metrics": "{{user.metric_name}}",   # optional: empty = all metrics
    "effectiveDuration": 7,
    "effectiveDurationUnit": "day"
}

resp = requests.post(url, headers=headers, json=payload)
result = resp.json()
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json monitor create-alarm-blacklist \
  --region-id "{{user.region}}" \
  --blacklist-name "{{user.blacklist_name}}" \
  --service-type "{{user.service_type}}" \
  --device-uuid "{{user.device_uuid}}" \
  --dimension "InstanceId" \
  --metrics "{{user.metric_name}}" \
  --effective-duration 7 \
  --effective-duration-unit day
```

#### Post-execution Validation

1. Read `{{output.blacklist_id}}` from `$.data.id` in the response.
2. Call **QueryAlarmBlacklists** to verify the blacklist exists and status is `1` (enabled).
3. On success, report `{{output.blacklist_id}}` to the user.
4. On failure, go to **Failure Recovery**.

#### Failure Recovery

| Error pattern | Max retries | Backoff | Agent Action |
|--------------|-------------|---------|--------------|
| `code != "200"` / 400 invalid input | 0–1 | — | Fix args from API spec; retry once if safe |
| `ResourceNotFound` / 404 | 0 | — | HALT; verify device UUID |
| Throttling / rate limit | 3 | exponential | Back off; respect rate limits |
| `InternalError` / 5xx | 3 | 2s, 4s, 8s | Retry; then HALT |

---

### Operation: QueryAlarmBlacklists

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Feature activation | Same as CreateAlarmBlacklist | Feature enabled | HALT; advise user to request activation |

#### Execution (SDK — `requests`)

```python
import requests

url = "https://monitor-global.ctapi.ctyun.cn/v4/monitor/query-alarm-blacklists"
params = {
    "regionId": "{{user.region}}",
    "pageNo": 1,
    "pageSize": 50,
}
# Optional filters
if "{{user.service_type}}":
    params["serviceType"] = "{{user.service_type}}"
if "{{user.device_uuid}}":
    params["deviceUUID"] = "{{user.device_uuid}}"

headers = {
    "ctyun-account": "{{env.CTYUN_ACCOUNT_ID}}",
}

resp = requests.get(url, headers=headers, params=params)
result = resp.json()
```

#### Execution — CLI (`ctyun`)

```bash
# List all blacklists
ctyun --output json monitor query-alarm-blacklist \
  --region-id "{{user.region}}" \
  --page-no 1 \
  --page-size 50

# Filter by service type
ctyun --output json monitor query-alarm-blacklist \
  --region-id "{{user.region}}" \
  --service-type "{{user.service_type}}"

# Filter by device UUID
ctyun --output json monitor query-alarm-blacklist \
  --region-id "{{user.region}}" \
  --device-uuid "{{user.device_uuid}}"
```

#### Present to User

| Field | Path (API/CLI) | Notes |
|-------|----------------|-------|
| Blacklist ID | `$.data.result[*].id` | Unique identifier |
| Blacklist Name | `$.data.result[*].blacklistName` | User-defined name |
| Status | `$.data.result[*].status` | 1=enabled, 0=disabled |
| Service Type | `$.data.result[*].serviceType` | ECS, RDS, etc. |
| Resource ID | `$.data.result[*].deviceUUID` | Blacklisted resource |
| Metric | `$.data.result[*].metrics` | Suppressed metric (empty=all) |
| Total Count | `$.data.totalCount` | Total matching records |

---

### Operation: ChangeAlarmBlacklistsStatus

#### Pre-flight (Safety Gate)

**CRITICAL SAFETY REQUIREMENT:**

- **Disabling an alarm blacklist** will **resume notifications** for previously suppressed resources. Confirm: "Are you sure you want to disable alarm blacklist `{{blacklist_name}}` (ID: `{{user.blacklist_id}}`)? Notifications for the blacklisted resource will resume immediately."
- **Re-enabling** is less critical but still requires explicit confirmation if the blacklist was disabled by another operator.
- **MUST NOT** proceed without clear user assent (e.g., "yes", "confirm", "disable").

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Blacklist exists | QueryAlarmBlacklists by ID | Blacklist found | HALT; verify blacklist ID |
| Current status | QueryAlarmBlacklists returns status | Not already at target | HALT; already in desired state |

#### Execution (SDK — `requests`)

```python
import requests

url = "https://monitor-global.ctapi.ctyun.cn/v4/monitor/change-alarm-blacklists-status"
headers = {
    "Content-Type": "application/json",
    "ctyun-account": "{{env.CTYUN_ACCOUNT_ID}}",
}

payload = {
    "ids": ["{{user.blacklist_id}}"],
    "status": 0   # 0 = disable, 1 = enable
}

resp = requests.post(url, headers=headers, json=payload)
result = resp.json()
```

#### Execution — CLI (`ctyun`)

```bash
# Disable blacklist
ctyun --output json monitor change-alarm-blacklists-status \
  --ids "{{user.blacklist_id}}" \
  --status 0

# Enable blacklist
ctyun --output json monitor change-alarm-blacklists-status \
  --ids "{{user.blacklist_id}}" \
  --status 1
```

#### Post-execution Validation

1. Verify `$.code == "200"` in the response.
2. Call **QueryAlarmBlacklists** to confirm the status changed.
3. Report the new status to the user.

#### Failure Recovery

| Error pattern | Max retries | Backoff | Agent Action |
|--------------|-------------|---------|--------------|
| `code != "200"` / 400 | 0–1 | — | Check blacklist ID and status value |
| `ResourceNotFound` / 404 | 0 | — | Blacklist may have been deleted; HALT |
| Throttling / 429 | 3 | exponential | Back off; retry |

---

### Operation: DeleteAlarmBlacklists

#### Pre-flight (Safety Gate)

**CRITICAL SAFETY REQUIREMENT:**

- **MUST** obtain explicit confirmation: "Are you sure you want to permanently delete alarm blacklist `{{blacklist_name}}` (ID: `{{user.blacklist_id}}`)? The resource will no longer be suppressed and notifications will resume. This action cannot be undone."
- **MUST NOT** proceed without clear user assent (e.g., "yes", "confirm", "delete").
- Document the blacklist configuration (call QueryAlarmBlacklists first) for potential recovery/recreation.

#### Pre-flight Checks

| Check | Method | Expected | On Failure |
|-------|--------|----------|------------|
| Blacklist exists | QueryAlarmBlacklists by ID | Blacklist found | HALT; already deleted |

#### Execution (SDK — `requests`)

```python
import requests

url = "https://monitor-global.ctapi.ctyun.cn/v4/monitor/delete-alarm-blacklists"
headers = {
    "Content-Type": "application/json",
    "ctyun-account": "{{env.CTYUN_ACCOUNT_ID}}",
}

payload = {
    "ids": ["{{user.blacklist_id}}"]
}

resp = requests.post(url, headers=headers, json=payload)
result = resp.json()
```

#### Execution — CLI (`ctyun`)

```bash
ctyun --output json monitor delete-alarm-blacklists \
  --ids "{{user.blacklist_id}}"
```

#### Post-execution Validation

1. Verify `$.code == "200"` in the response.
2. Poll **QueryAlarmBlacklists** until the blacklist is no longer returned.
3. Timeout after 60 seconds if blacklist still appears.
4. Report deletion success or failure to user.

#### Failure Recovery

| Error pattern | Max retries | Backoff | Agent Action |
|--------------|-------------|---------|--------------|
| `code != "200"` / 400 | 0–1 | — | Verify blacklist ID |
| `ResourceNotFound` / 404 | 0 | — | Already deleted; report success |
| Throttling / 429 | 3 | exponential | Back off; retry |
| `InternalError` / 5xx | 3 | 2s, 4s, 8s | Retry; then HALT |

## Prerequisites

> **Python 3.10+ is REQUIRED.** We recommend Python 3.10 for maximum compatibility with CTyun SDK and CLI.

1. **Install uv** (system-wide, one-time per machine):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or: brew install uv
   ```

2. **Bootstrap Python environment** (idempotent):
   ```bash
   uv venv --python 3.10
   source .venv/bin/activate  # macOS/Linux
   uv pip install ctyun-cli ctyun-sdk
   ctyun --version
   ```

3. **Configure Credentials**:

   **Method A: SDK (environment variables)**
   ```bash
   export CTYUN_ACCESS_KEY="{{env.CTYUN_ACCESS_KEY}}"
   export CTYUN_SECRET_KEY="{{env.CTYUN_SECRET_KEY}}"
   export CTYUN_REGION="cn-gz"
   ```

   **Method B: CLI (`~/.ctyun/config` INI)**
   See [CLI Usage / Sandbox Environment Setup](references/cli-usage.md#sandbox-environment-setup) for the CLI configuration guide.

4. **Verify Configuration**:
   ```bash
   ctyun --output json cloudmonitor describe-alarm-rules --region-id cn-gz
   ```

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop** (GCL) defined in [`AGENTS.md`](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate). GCL is **recommended** for this skill per `AGENTS.md` §8.

### Parameters (override `AGENTS.md` §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `recommended` | inherited from `AGENTS.md` §8 |
| `max_iterations` | **3** | `AGENTS.md` §8 default for `ctyun-cloudmonitor-ops` (recommended) |
| `rubric_version` | `v1` | see [references/rubric.md](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | **true** | `true` for any destructive op; DeleteAlarmRule, DeleteAlarmBlacklists, and ChangeAlarmBlacklistsStatus are destructive |
| `fallback_decision_table` | inline in SKILL.md §CLI-First Policy | reference to CLI-first decision table; required when any operation has `cli_applicability: sdk-only` |

### GCL Rubric Dimensions

| Dimension | Threshold | Scale | Notes |
|-----------|-----------|-------|-------|
| Correctness | ≥ 0.5 (1.0 for destructive ops: DeleteAlarmRule, DeleteAlarmBlacklists) | 0 / 0.5 / 1 | Resource ID/state correct |
| Safety | = 1 | 0 / 1 | Delete operations confirmed; no secret leakage |
| Idempotency | ≥ 0.5 | 0 / 0.5 / 1 | Retry-safe for metric queries |
| Traceability | ≥ 0.5 | 0 / 0.5 / 1 | All operations logged |
| Spec Compliance | ≥ 0.5 | 0 / 0.5 / 1 | Follows Agent Skill OpenSpec |

**Safety = 0 → ABORT immediately**, regardless of total score.

### Loop Overview

```
User Request
     │
     ▼
[0] Pre-flight (Orchestrator)
     │
     ▼
[1] Generate (G) ───────────────────────┐
     - run ctyun / SDK                    │
     - capture trace                      │
     │                                    │
     ▼                                    │
[2] Critique (C)                         │
     - isolated prompt context            │
     - score every rubric dimension       │
     - emit actionable suggestions        │
     │                                    │
     ▼                                    │
[3] Decide (Orchestrator)                │
     - Safety=0  → ABORT                  │
     - all pass  → RETURN                 │
     - else & iter<3 → inject            │
       suggestions into G                 │
     - else → RETURN best + unresolved    │
     └────────────────────────────────────┘
```

See [references/rubric.md](references/rubric.md) for detailed scoring rules and [references/prompt-templates.md](references/prompt-templates.md) for G/C/O prompt templates.

## Reference Directory

- [Core Concepts](references/core-concepts.md)
- [API & SDK Usage](references/api-sdk-usage.md)
- [CLI Usage](references/cli-usage.md)
- [Troubleshooting Guide](references/troubleshooting.md)
- [Monitoring & Alerts](references/monitoring.md)
- [Integration](references/integration.md)
- [GCL Rubric](references/rubric.md)
- [GCL Prompt Templates](references/prompt-templates.md)

## Operational Best Practices

- **Least privilege:** IAM policies scoped to Cloud Monitor APIs only (`cloudmonitor:CreateAlarmRule`, `cloudmonitor:DescribeAlarmRules`, etc.).
- **Alarm naming:** Use consistent naming conventions with prefixes (e.g., `prod-ecs-`, `test-rds-`) for easier filtering.
- **Threshold tuning:** Start with conservative thresholds and adjust based on historical data; avoid alert fatigue.
- **Notification channels:** Configure multiple notification channels (SMS, email) for critical alarms.
- **Cleanup:** Regularly review and delete obsolete alarm rules to stay within quota limits.
- **Blacklist hygiene:** Prefer time-limited blacklists (`effectiveDuration`) over permanent ones to prevent forgotten suppressions.
- **Blacklist naming:** Use descriptive names that include the reason and duration (e.g., `maintenance-ecs-web01-7d-202606`) for easier auditing.
- **Blacklist vs Disable:** Use blacklists for temporary, targeted suppressions (specific resource/metric); use alarm rule disable/enable for broad, permanent silencing.

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-06-05 | Added alarm blacklist operations: Create/Query/Update/ChangeStatus/Delete with SDK (requests-based) + CLI (monitor subcommand) dual-path; new core-concepts "Alarm Blacklist" section; new API mappings in api-sdk-usage.md; GCL safety gates updated for blacklist destructive ops |
| 1.0.0 | 2026-06-05 | Initial Cloud Monitor skill with Create/Describe/Modify/Delete AlarmRule, Query/List MetricData, ListAlarmHistory operations; dual-path (ctyun CLI + SDK); GCL quality gate with max_iter=3 |
