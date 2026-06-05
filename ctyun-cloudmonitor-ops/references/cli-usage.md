# CLI — Cloud Monitor (`ctyun cloudmonitor`)

## Install and Configure

- Install: [CTyun CLI](https://www.ctyun.cn/act/xiaofeizhe/ctyun-cli)
- **CRITICAL:** The `ctyun` CLI reads credentials exclusively from `~/.ctyun/config` INI file, NOT from environment variables.

### Sandbox Environment Setup

```bash
export HOME=/tmp/ctyun-home
mkdir -p /tmp/ctyun-home/.ctyun

cat > /tmp/ctyun-home/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION}}
endpoint = cloudmonitor.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF

printf "%s" "default" > /tmp/ctyun-home/.ctyun/current
```

## CLI Conventions (Agent Execution)

| Convention | Rule |
|------------|------|
| `--output json` | **Top-level argument** — MUST be placed BEFORE subcommand: `ctyun --output json cloudmonitor <command> ...` |
| `--no-interactive` | **Does NOT exist** — all commands are non-interactive by default |
| Credentials | Read from `~/.ctyun/config` only; environment variables ignored |
| Region | Use `--region-id` flag for all operations |

## CLI vs API Coverage Gap

| Operation (API / SDK) | Available via `ctyun`? | Notes |
|------------------------|------------------------|-------|
| CreateAlarmRule | yes | Full support |
| DescribeAlarmRules | yes | Full support with filters |
| ModifyAlarmRule | yes | Partial: threshold, evaluation count, actions |
| DeleteAlarmRule | yes | Full support |
| EnableAlarmRule | [verify] | May be part of Modify |
| DisableAlarmRule | [verify] | May be part of Modify |
| QueryMetricData | yes | Full support |
| ListMetrics | yes | Full support |
| ListAlarmHistory | yes | Full support |

## Command Map

### Alarm Rule Operations

| Goal | Example `ctyun` invocation | Notes |
|------|---------------------------|-------|
| Create | `ctyun --output json cloudmonitor create-alarm-rule --region-id <region> --alarm-name <name> --namespace <ns> --metric-name <metric> --resource-id <id> --threshold <value>` | `--output json` BEFORE subcommand |
| List | `ctyun --output json cloudmonitor describe-alarm-rules --region-id <region> --page-number 1 --page-size 50` | Returns paginated list |
| Describe | `ctyun --output json cloudmonitor describe-alarm-rules --region-id <region> --alarm-id <id>` | Filter by alarm ID |
| Modify | `ctyun --output json cloudmonitor modify-alarm-rule --region-id <region> --alarm-id <id> --threshold <new-value>` | Specify fields to change |
| Delete | `ctyun --output json cloudmonitor delete-alarm-rule --region-id <region> --alarm-id <id>` | **Requires confirmation** |

### Metric Data Operations

| Goal | Example `ctyun` invocation | Notes |
|------|---------------------------|-------|
| Query | `ctyun --output json cloudmonitor query-metric-data --region-id <region> --namespace <ns> --metric-name <metric> --resource-id <id> --start-time <iso> --end-time <iso> --period 300` | Period: 60, 300, 3600, 86400 |
| List Metrics | `ctyun --output json cloudmonitor list-metrics --region-id <region> --namespace <ns>` | Lists available metrics |

### Alarm History Operations

| Goal | Example `ctyun` invocation | Notes |
|------|---------------------------|-------|
| List History | `ctyun --output json cloudmonitor list-alarm-history --region-id <region> --start-time <iso> --end-time <iso>` | Optional filter by alarm-id |

## JSON Output Paths (Verified)

### CreateAlarmRule Response
```json
{
  "result": {
    "alarmId": "al-xxxxxxxxxxxxxxxx"
  }
}
```
Path: `$.result.alarmId`

### DescribeAlarmRules Response
```json
{
  "result": {
    "alarms": [
      {
        "alarmId": "al-xxxxxxxxxxxxxxxx",
        "alarmName": "cpu-alert",
        "status": "enabled",
        "namespace": "ECS",
        "metricName": "CPUUtilization"
      }
    ],
    "totalCount": 1
  }
}
```
Paths:
- Alarm IDs: `$.result.alarms[*].alarmId`
- Names: `$.result.alarms[*].alarmName`
- Status: `$.result.alarms[*].status`

### QueryMetricData Response
```json
{
  "result": {
    "datapoints": [
      {"timestamp": "2026-06-05T00:00:00Z", "value": 45.2},
      {"timestamp": "2026-06-05T00:05:00Z", "value": 67.3}
    ],
    "unit": "Percent"
  }
}
```
Paths:
- Timestamps: `$.result.datapoints[*].timestamp`
- Values: `$.result.datapoints[*].value`
- Unit: `$.result.unit`

## Error Handling

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Parse JSON output |
| 1 | CLI error | Check `ctyun` installation |
| 2 | API error | Parse error message from JSON |

Common API errors in JSON:
```json
{
  "error": {
    "code": "InvalidParameter",
    "message": "Invalid threshold value"
  }
}
```

## Time Format Reference

All time parameters use ISO 8601 format:
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2026-06-05T12:00:00Z`
- Timezone: UTC (Z suffix)
