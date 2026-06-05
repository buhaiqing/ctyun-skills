# Integration — Alert Intelligence

## Cross-Skill Workflows

| Use Case | Primary Skill | Secondary Skill |
|----------|--------------|-----------------|
| Investigate alert → fix resource | `ctyun-alert-intelligence` | `ctyun-ecs-ops` / `ctyun-rds-ops` |
| Alert pattern → create alarm rule | `ctyun-alert-intelligence` | `ctyun-cloudmonitor-ops` |
| Alert audit trail | `ctyun-alert-intelligence` | `ctyun-cloudaudit-ops` |

## Data Flow

```
Alert Data (Cloud Monitor) → QueryAlertHistory → Pattern Analysis → Summary Report
```
