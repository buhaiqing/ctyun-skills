# API & SDK — Cloud Monitor

## OpenAPI Specification

- **OpenAPI URL:** [URL to be verified]
- **Base Path:** `/v1`
- **Service Endpoint:** `cloudmonitor.ctyun.cn`
- **Protocol:** HTTPS
- **Authentication:** HMAC-SHA256 signature with Access Key / Secret Key

## API Operations Map

| Goal | API OperationId | SDK Method | HTTP Method | Path |
|------|-----------------|------------|-------------|------|
| Create Alarm Rule | CreateAlarmRule | `create_alarm_rule()` | POST | /alarms |
| Describe Alarm Rules | DescribeAlarmRules | `describe_alarm_rules()` | GET | /alarms |
| Modify Alarm Rule | ModifyAlarmRule | `modify_alarm_rule()` | PUT | /alarms/{alarmId} |
| Delete Alarm Rule | DeleteAlarmRule | `delete_alarm_rule()` | DELETE | /alarms/{alarmId} |
| Enable Alarm Rule | EnableAlarmRule | `enable_alarm_rule()` | PUT | /alarms/{alarmId}/enable |
| Disable Alarm Rule | DisableAlarmRule | `disable_alarm_rule()` | PUT | /alarms/{alarmId}/disable |
| Query Metric Data | QueryMetricData | `query_metric_data()` | GET | /metrics/data |
| List Metrics | ListMetrics | `list_metrics()` | GET | /metrics |
| List Alarm History | ListAlarmHistory | `list_alarm_history()` | GET | /alarms/history |

## SDK Module Structure

```
ctyun_sdk/
├── core/
│   ├── credential.py
│   └── client.py
└── services/
    └── cloudmonitor/
        ├── client.py                 # CloudMonitorClient
        └── apis/
            ├── __init__.py
            ├── create_alarm_rule.py  # CreateAlarmRuleRequest/Response
            ├── describe_alarm_rules.py
            ├── modify_alarm_rule.py
            ├── delete_alarm_rule.py
            ├── query_metric_data.py
            ├── list_metrics.py
            └── list_alarm_history.py
```

## SDK Method Reference

> **Note:** The exact SDK import paths and method names below are placeholders.
> Verify against the actual `ctyun_sdk.services.cloudmonitor` module.

### CreateAlarmRule

**Request Class:** `CreateAlarmRuleRequest`
**Response Class:** `CreateAlarmRuleResponse`

```python
from ctyun_sdk.services.cloudmonitor.apis.create_alarm_rule import CreateAlarmRuleRequest

request = CreateAlarmRuleRequest(
    regionId="cn-gz",
    alarmName="high-cpu-alert",
    namespace="ECS",
    metricName="CPUUtilization",
    resourceId="i-xxxxxxxx",
    period=300,
    statistic="Average",
    comparisonOperator="GreaterThanThreshold",
    threshold=80.0,
    evaluationCount=3,
    alarmActions=["arn:ctyun:sms:cn-gz:xxxx:alert"]
)
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| regionId | string | Yes | Region identifier (e.g., cn-gz) |
| alarmName | string | Yes | User-defined alarm name |
| namespace | string | Yes | Metric namespace (ECS, RDS, etc.) |
| metricName | string | Yes | Metric name (CPUUtilization, etc.) |
| resourceId | string | Yes | Target resource ID |
| period | int | Yes | Evaluation period in seconds (60, 300, 3600, 86400) |
| statistic | string | Yes | Statistic type (Average, Minimum, Maximum, Sum, SampleCount) |
| comparisonOperator | string | Yes | GreaterThanThreshold, LessThanThreshold, GreaterThanOrEqualToThreshold, LessThanOrEqualToThreshold |
| threshold | float | Yes | Threshold value |
| evaluationCount | int | Yes | Consecutive periods before triggering (1-10) |
| alarmActions | list | No | List of action ARNs for ALARM state |
| okActions | list | No | List of action ARNs for OK state |
| insufficientDataActions | list | No | List of action ARNs for INSUFFICIENT_DATA state |

### DescribeAlarmRules

**Request Class:** `DescribeAlarmRulesRequest`

```python
from ctyun_sdk.services.cloudmonitor.apis.describe_alarm_rules import DescribeAlarmRulesRequest

request = DescribeAlarmRulesRequest(
    regionId="cn-gz",
    alarmId="al-xxxxxxxx",       # Optional
    alarmName="cpu-alert",       # Optional
    namespace="ECS",             # Optional
    pageNumber=1,
    pageSize=50
)
```

### QueryMetricData

**Request Class:** `QueryMetricDataRequest`

```python
from ctyun_sdk.services.cloudmonitor.apis.query_metric_data import QueryMetricDataRequest

request = QueryMetricDataRequest(
    regionId="cn-gz",
    namespace="ECS",
    metricName="CPUUtilization",
    resourceId="i-xxxxxxxx",
    startTime="2026-06-05T00:00:00Z",
    endTime="2026-06-05T01:00:00Z",
    period=300,
    statistic="Average"
)
```

## Response Structures

### CreateAlarmRule Response

```python
{
    "result": {
        "alarmId": "al-xxxxxxxxxxxxxxxx"
    },
    "requestId": "req-xxxxxxxx"
}
```

### DescribeAlarmRules Response

```python
{
    "result": {
        "alarms": [
            {
                "alarmId": "al-xxxxxxxx",
                "alarmName": "cpu-alert",
                "status": "enabled",
                "namespace": "ECS",
                "metricName": "CPUUtilization",
                "resourceId": "i-xxxxxxxx",
                "period": 300,
                "statistic": "Average",
                "comparisonOperator": "GreaterThanThreshold",
                "threshold": 80.0,
                "evaluationCount": 3,
                "alarmActions": [...],
                "createdAt": "2026-06-05T00:00:00Z"
            }
        ],
        "totalCount": 1
    },
    "requestId": "req-xxxxxxxx"
}
```

### QueryMetricData Response

```python
{
    "result": {
        "datapoints": [
            {"timestamp": "2026-06-05T00:00:00Z", "value": 45.2},
            {"timestamp": "2026-06-05T00:05:00Z", "value": 67.3}
        ],
        "unit": "Percent",
        "metricName": "CPUUtilization"
    },
    "requestId": "req-xxxxxxxx"
}
```

## Pagination

All list operations support pagination:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| pageNumber | int | 1 | Page number (1-indexed) |
| pageSize | int | 50 | Items per page (max 100) |

**Response pagination fields:**
- `$.result.totalCount`: Total number of items
- `$.result.alarms`: Array of items for current page

## Error Codes

| Error Code | HTTP Status | Meaning |
|------------|-------------|---------|
| InvalidParameter | 400 | Request parameter invalid |
| MissingParameter | 400 | Required parameter missing |
| ResourceNotFound | 404 | Alarm rule or resource not found |
| AlarmNameAlreadyExists | 409 | Alarm name already in use |
| QuotaExceeded | 403 | Alarm rule quota exceeded |
| InternalError | 500 | Server internal error |
| Throttling | 429 | Rate limit exceeded |

## Alarm Blacklist API (Monitor v4)

> **Note:** Alarm Blacklist operations use a **separate API endpoint** (`monitor-global.ctapi.ctyun.cn`) and authentication mechanism from the standard Cloud Monitor APIs documented above. The blacklist API uses AK/SK signature via request headers (`ctyun-account`, `x-ctyun-signature`, etc.) and returns responses with `code` / `msg` / `data` structure instead of the `result` / `requestId` pattern.

### Blacklist API Operations Map

| Goal | API Operation | HTTP Method | Path (v4) |
|------|---------------|-------------|-----------|
| Create Blacklist | CreateAlarmBlacklist | POST | `/v4/monitor/create-alarm-blacklist` |
| Query Blacklists | QueryAlarmBlacklists | GET | `/v4/monitor/query-alarm-blacklists` |
| Update Blacklist | UpdateAlarmBlacklist | POST | `/v4/monitor/update-alarm-blacklist` |
| Change Blacklist Status | ChangeAlarmBlacklistsStatus | POST | `/v4/monitor/change-alarm-blacklists-status` |
| Delete Blacklists | DeleteAlarmBlacklists | POST | `/v4/monitor/delete-alarm-blacklists` |

### Blacklist Response Structure (v4)

All blacklist APIs return a unified envelope:

```python
{
    "code": "200",          # "200" = success; others = error
    "msg": "success",
    "data": { ... }         # Operation-specific payload
}
```

### CreateAlarmBlacklist

**Endpoint:** `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/create-alarm-blacklist`

**Request (JSON body):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| regionId | string | Yes | Region identifier (e.g., cn-gz) |
| blacklistName | string | Yes | Human-readable blacklist name |
| serviceType | string | Yes | Cloud service type (ECS, RDS, SLB, etc.) |
| deviceUUID | string | Yes | Specific resource ID to blacklist |
| metrics | string | No | Metric to suppress (empty = all metrics for this resource) |
| dimension | string | Yes | Resource identifier key (e.g., InstanceId) |
| effectiveDuration | int | Yes | Duration value (e.g., 7) |
| effectiveDurationUnit | string | Yes | Unit: `day`, `month`, or `year` |

**Response (`data`):**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Newly created blacklist ID |

**Example:**

```python
import requests
import json

url = "https://monitor-global.ctapi.ctyun.cn/v4/monitor/create-alarm-blacklist"
headers = {
    "Content-Type": "application/json",
    # Auth headers (AK/SK signature) — see CTyun Monitor auth docs
    "ctyun-account": "{{env.CTYUN_ACCOUNT_ID}}",
}

payload = {
    "regionId": "{{user.region}}",
    "blacklistName": "{{user.blacklist_name}}",
    "serviceType": "{{user.service_type}}",
    "deviceUUID": "{{user.device_uuid}}",
    "metrics": "{{user.metric_name}}",       # optional: empty = all metrics
    "dimension": "InstanceId",
    "effectiveDuration": 7,
    "effectiveDurationUnit": "day"
}

resp = requests.post(url, headers=headers, json=payload)
result = resp.json()
# result["code"] == "200" → success
# result["data"]["id"] → blacklist ID
```

### QueryAlarmBlacklists

**Endpoint:** `GET https://monitor-global.ctapi.ctyun.cn/v4/monitor/query-alarm-blacklists`

**Query Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| regionId | string | Yes | Region identifier |
| serviceType | string | No | Filter by service type (ECS, RDS, etc.) |
| deviceUUID | string | No | Filter by resource ID |
| pageNo | int | Yes | Page number (1-indexed) |
| pageSize | int | Yes | Items per page (max 100) |

**Response (`data`):**

| Field | Type | Description |
|-------|------|-------------|
| totalCount | int | Total items matching query |
| currentPage | int | Current page number |
| pageSize | int | Items per page |
| cursor | int | Cursor position |
| isLastPage | bool | Whether this is the last page |
| result | array | Array of blacklist records |

**Blacklist record fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Blacklist ID |
| blacklistName | string | Blacklist name |
| status | int | 1 = enabled, 0 = disabled |
| serviceType | string | Cloud service type |
| regionId | string | Region |
| deviceUUID | string | Blacklisted resource ID |
| metrics | string | Suppressed metric (empty = all) |
| dimension | string | Resource dimension key |
| startTime | string | Effective start time (epoch ms) |
| endTime | string | Effective end time (epoch ms) |
| effectiveDuration | int | Duration value |
| effectiveDurationUnit | string | Duration unit |
| createTime | string | Creation time (epoch ms) |
| updateTime | string | Last update time (epoch ms) |

**Example:**

```python
GET https://monitor-global.ctapi.ctyun.cn/v4/monitor/query-alarm-blacklists?regionId=cn-gz&pageNo=1&pageSize=10&serviceType=ECS
```

Response:

```python
{
    "code": "200",
    "msg": "success",
    "data": {
        "totalCount": 5,
        "currentPage": 1,
        "pageSize": 10,
        "cursor": 1,
        "isLastPage": true,
        "result": [
            {
                "id": "bl-xxxxxxxx",
                "blacklistName": "maintenance-ecs-web01",
                "status": 1,
                "serviceType": "ECS",
                "regionId": "cn-gz",
                "deviceUUID": "i-xxxxxxxx",
                "metrics": "CPUUtilization",
                "dimension": "InstanceId",
                "effectiveDuration": 7,
                "effectiveDurationUnit": "day",
                "createTime": "1723564800000",
                "updateTime": "1723564800000"
            }
        ]
    }
}
```

### UpdateAlarmBlacklist

**Endpoint:** `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/update-alarm-blacklist`

**Request (JSON body):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Blacklist ID to update |
| blacklistName | string | No | New blacklist name |
| deviceUUID | string | No | New resource ID |
| metrics | string | No | New metric to suppress |
| effectiveDuration | int | No | New duration value |
| effectiveDurationUnit | string | No | New duration unit |

### ChangeAlarmBlacklistsStatus

**Endpoint:** `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/change-alarm-blacklists-status`

**Request (JSON body):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ids | array | Yes | Array of blacklist IDs to update |
| status | int | Yes | 0 = disable, 1 = enable |

**Example:**

```python
payload = {
    "ids": ["bl-xxxxxxxx", "bl-yyyyyyyy"],
    "status": 0  # disable
}
```

### DeleteAlarmBlacklists

**Endpoint:** `POST https://monitor-global.ctapi.ctyun.cn/v4/monitor/delete-alarm-blacklists`

**Request (JSON body):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ids | array | Yes | Array of blacklist IDs to delete |

**Example:**

```python
payload = {
    "ids": ["bl-xxxxxxxx", "bl-yyyyyyyy"]
}
```

## Rate Limits

| Operation | Requests per Second | Burst |
|-----------|---------------------|-------|
| Create/Modify/Delete (alarm rules) | 10 | 20 |
| Describe/List (alarm rules) | 50 | 100 |
| QueryMetricData | 100 | 200 |
| Blacklist Create/Update/Delete | 10 | 20 |
| Blacklist Query | 50 | 100 |
