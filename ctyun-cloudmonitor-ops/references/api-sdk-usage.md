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

## SDK Method: [to be verified]

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

## Rate Limits

| Operation | Requests per Second | Burst |
|-----------|---------------------|-------|
| Create/Modify/Delete | 10 | 20 |
| Describe/List | 50 | 100 |
| QueryMetricData | 100 | 200 |
