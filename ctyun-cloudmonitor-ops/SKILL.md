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

### 1. Common Patterns

All operations below share these patterns. Individual operations only document what differs.

#### SDK Client Initialization

```python
# Full code in references/api-sdk-usage.md §Initialization
from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient
client = CloudMonitorClient(credential, os.environ.get("CTYUN_REGION", "cn-gz"))
```

For `requests`-based SDK calls (alarm blacklist ops), see `references/api-sdk-usage.md` §Blacklist SDK.

#### Response Validation (applies to every SDK/CLI response)

| Check | How | Action |
|---|---|---|
| HTTP/status 200, `result` non-null | inspect JSON body | OK |
| `errorCode` starts with "5" | retry once; if persists, log | fall back to SDK (if currently CLI) |
| `errorCode` starts with "4" | business error | surface to user; **never** fall back |

#### Failure Recovery (applies to every operation unless overridden below)

| Pattern | Retries | Backoff | Agent Action |
|---|---|---|---|
| `InvalidParameter` / 400 | 0-1 | — | Fix args from OpenAPI; retry once if safe |
| `ResourceNotFound` / 404 | 0 | — | HALT; verify the resource/ID |
| `QuotaExceeded` / name exists | 0 | — | HALT or ask reuse |
| Throttling / 429 | 3 | 2s, 4s, 8s | Back off; retry |
| `InternalError` / 5xx | 3 | 2s, 4s, 8s | Retry; then HALT |

### 2. Operation Summary

| # | Operation | SDK method / CLI command | Safety Gate | Timeout | JSON output path |
|---|---|---|---|---|---|
| 1 | **CreateAlarmRule** | `client.create_alarm_rule` / `ctyun cloudmonitor create-alarm-rule` | — | 30s | `$.result.alarmId` |
| 2 | **DescribeAlarmRules** | `client.describe_alarm_rules` / `ctyun cloudmonitor describe-alarm-rules` | — | 30s | `$.result.alarms[*]` |
| 3 | **ModifyAlarmRule** | `client.modify_alarm_rule` / `ctyun cloudmonitor modify-alarm-rule` | confirm | 30s | `$.result.success` |
| 4 | **DeleteAlarmRule** | `client.delete_alarm_rule` / `ctyun cloudmonitor delete-alarm-rule` | **confirm** | 30s | `$.result.success` |
| 5 | **QueryMetricData** | `client.query_metric_data` / `ctyun cloudmonitor query-metric-data` | — | 60s | `$.result.datapoints[*]` |
| 6 | **ListMetrics** | `client.list_metrics` / `ctyun cloudmonitor list-metrics` | — | 30s | `$.result.metrics[*]` |
| 7 | **ListAlarmHistory** | `client.list_alarm_history` / `ctyun cloudmonitor list-alarm-history` | — | 30s | `$.result.history[*]` |
| 8 | **CreateAlarmBlacklist** | `requests.post` / `ctyun monitor create-alarm-blacklist` | — | 30s | `$.data.id` |
| 9 | **QueryAlarmBlacklists** | `requests.get` / `ctyun monitor query-alarm-blacklist` | — | 30s | `$.data.result[*]` |
| 10 | **ChangeAlarmBlacklistsStatus** | `requests.post` / `ctyun monitor change-alarm-blacklists-status` | **confirm** | 30s | `$.code` |
| 11 | **DeleteAlarmBlacklists** | `requests.post` / `ctyun monitor delete-alarm-blacklists` | **confirm** | 60s | `$.code` |

> **Execution preference:** Prefer `ctyun` CLI for quick ad-hoc ops; prefer SDK for automation. See [CLI-First Decision Matrix](../../AGENTS.md#cli-first-policy-repository-wide).

### 3. Per-Operation Details

#### Op 1: CreateAlarmRule

| Aspect | Detail |
|---|---|
| Pre-flight | region valid? resource exists? quota sufficient? |
| SDK | `client.create_alarm_rule(regionId="{{user.region}}", alarmName="{{user.alarm_name}}", metricName="{{user.metric_name}}", resourceId="{{user.resource_id}}", period=300, threshold=80.0, evaluationCount=3, ...)` — full params in `references/api-sdk-usage.md` |
| CLI | `ctyun --output json cloudmonitor create-alarm-rule --region-id "{{user.region}}" --alarm-name "{{user.alarm_name}}" --namespace "{{user.namespace}}" --metric-name "{{user.metric_name}}" --resource-id "{{user.resource_id}}" --threshold 80.0 --evaluation-count 3` |
| Output | `{{output.alarm_id}}` from `$.result.alarmId` |

#### Op 2: DescribeAlarmRules (read-only)

| Aspect | Detail |
|---|---|
| SDK | `client.describe_alarm_rules(regionId="{{user.region}}", alarmId="opt", alarmName="opt", namespace="opt", pageNumber=1, pageSize=50)` |
| CLI | `ctyun --output json cloudmonitor describe-alarm-rules --region-id "{{user.region}}" --page-number 1 --page-size 50` |
| Fields | `$.result.alarms[*]` — alarmId, alarmName, status, namespace, metricName, threshold |

#### Op 3: ModifyAlarmRule

| Aspect | Detail |
|---|---|
| Pre-flight | Alarm exists (call DescribeAlarmRules); confirm with user |
| SDK | `client.modify_alarm_rule(regionId="{{user.region}}", alarmId="{{output.alarm_id}}", ...)` — include only changed fields |
| CLI | `ctyun --output json cloudmonitor modify-alarm-rule --region-id "{{user.region}}" --alarm-id "{{output.alarm_id}}" --threshold 90.0 --evaluation-count 5` |
| Post-exec | Verify changes via DescribeAlarmRules |

#### Op 4: DeleteAlarmRule (destructive)

| Aspect | Detail |
|---|---|
| ✅ Safety Gate | MUST obtain explicit confirmation: "Delete alarm `{{user.alarm_name}}` (ID: `{{user.alarm_id}}`)? This cannot be undone." Document config first via DescribeAlarmRules. |
| SDK | `client.delete_alarm_rule(regionId="{{user.region}}", alarmId="{{user.alarm_id}}")` |
| CLI | `ctyun --output json cloudmonitor delete-alarm-rule --region-id "{{user.region}}" --alarm-id "{{user.alarm_id}}"` |
| Post-exec | Poll DescribeAlarmRules until absent (60s timeout) |
| Failure | 404 => already deleted (report success); throttling/5xx retry 3× |

#### Op 5: QueryMetricData

| Aspect | Detail |
|---|---|
| Pre-flight | `start_time < end_time`; `period` in [60, 300, 3600, 86400] |
| SDK | `client.query_metric_data(regionId="{{user.region}}", namespace="{{user.namespace}}", metricName="{{user.metric_name}}", resourceId="{{user.resource_id}}", startTime="...", endTime="...", period=300, statistic="Average")` |
| CLI | `ctyun --output json cloudmonitor query-metric-data --region-id "{{user.region}}" --namespace "{{user.namespace}}" --metric-name "{{user.metric_name}}" --resource-id "{{user.resource_id}}" --start-time "ISO8601" --end-time "ISO8601" --period 300` |
| Output | `$.result.datapoints[*].timestamp` → ISO8601, `.value` → number, `.unit` → string |

#### Op 6: ListMetrics (read-only)

| Aspect | Detail |
|---|---|
| SDK | `client.list_metrics(regionId="{{user.region}}", namespace="opt")` |
| CLI | `ctyun --output json cloudmonitor list-metrics --region-id "{{user.region}}" --namespace "{{user.namespace}}"` |
| Output | `$.result.metrics[*]` → metricName, namespace, description, unit |

#### Op 7: ListAlarmHistory (read-only)

| Aspect | Detail |
|---|---|
| SDK | `client.list_alarm_history(regionId="{{user.region}}", alarmId="opt", startTime="...", endTime="...", pageNumber=1, pageSize=100)` |
| CLI | `ctyun --output json cloudmonitor list-alarm-history --region-id "{{user.region}}" --start-time "ISO8601" --end-time "ISO8601" --page-number 1 --page-size 100` |
| Output | `$.result.history[*]` → timestamp, alarmId, status (ALARM/OK/INSUFFICIENT_DATA), metricValue, reason |

#### Op 8: CreateAlarmBlacklist (requires `CTYUN_ACCOUNT_ID` env var)

| Aspect | Detail |
|---|---|
| ⚠️ Prerequisite | Alarm Blacklist is a restricted-access feature; verify activation via customer manager. Uses Monitor v4 API (`monitor-global.ctapi.ctyun.cn`), not standard Cloud Monitor endpoint. |
| Pre-flight | Feature enabled? Resource exists? No duplicate blacklist for same device+metric? |
| SDK (`requests`) | `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/create-alarm-blacklist` — headers: `ctyun-account: {{env.CTYUN_ACCOUNT_ID}}`; body: `regionId, blacklistName, serviceType, deviceUUID, dimension, metrics, effectiveDuration, effectiveDurationUnit` |
| CLI | `ctyun --output json monitor create-alarm-blacklist --region-id "{{user.region}}" --blacklist-name "..." --service-type "..." --device-uuid "..." --effective-duration 7 --effective-duration-unit day` |
| Output | `{{output.blacklist_id}}` from `$.data.id`; verify via QueryAlarmBlacklists |

#### Op 9: QueryAlarmBlacklists (read-only, requires `CTYUN_ACCOUNT_ID`)

| Aspect | Detail |
|---|---|
| Pre-flight | Feature activation check |
| SDK (`requests`) | `GET https://monitor-global.ctapi.ctyun.cn/v4/monitor/query-alarm-blacklists` — params: `regionId, pageNo, pageSize, serviceType(opt), deviceUUID(opt)` |
| CLI | `ctyun --output json monitor query-alarm-blacklist --region-id "{{user.region}}" --page-no 1 --page-size 50 [--service-type "..." --device-uuid "..."]` |
| Output | `$.data.result[*]` → id, blacklistName, status (1=enabled), serviceType, deviceUUID, metrics; `$.data.totalCount` |

#### Op 10: ChangeAlarmBlacklistsStatus (destructive, requires `CTYUN_ACCOUNT_ID`)

| Aspect | Detail |
|---|---|
| ✅ Safety Gate | Confirm: "Disable blacklist `{{blacklist_name}}` (ID: `{{user.blacklist_id}}`)? Notifications will resume." |
| Pre-flight | Blacklist exists? Not already at target status? |
| SDK (`requests`) | `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/change-alarm-blacklists-status` — body: `ids: ["{{user.blacklist_id}}"], status: 0\|1` |
| CLI | `ctyun --output json monitor change-alarm-blacklists-status --ids "{{user.blacklist_id}}" --status 0\|1` |
| Post-exec | Verify `$.code == "200"`; confirm via QueryAlarmBlacklists |

#### Op 11: DeleteAlarmBlacklists (destructive, requires `CTYUN_ACCOUNT_ID`)

| Aspect | Detail |
|---|---|
| ✅ Safety Gate | Confirm: "Permanently delete blacklist `{{blacklist_name}}` (ID: `{{user.blacklist_id}}`)? Suppression removed. Cannot be undone." Document config first via QueryAlarmBlacklists. |
| Pre-flight | Blacklist exists? |
| SDK (`requests`) | `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/delete-alarm-blacklists` — body: `ids: ["{{user.blacklist_id}}"]` |
| CLI | `ctyun --output json monitor delete-alarm-blacklists --ids "{{user.blacklist_id}}"` |
| Post-exec | Poll QueryAlarmBlacklists until absent (60s timeout) |
| Failure | 404 => already deleted (report success); throttling/5xx retry 3× |

---

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
