# Troubleshooting — Alert Intelligence

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| No alarm data returned | Time range too wide (>30 days) | Narrow to 7-14 day window |
| `AccessDenied` | Missing IAM permissions | Grant `cloudmonitor:ListAlarmHistory` |
| Empty results for namespace | No alarms fired in that period | Expand time range or check namespace |
| `InvalidParameter` | Incorrect date format | Use ISO 8601 format |
| Timeout | Large data set | Apply namespace filter or shorter range |
