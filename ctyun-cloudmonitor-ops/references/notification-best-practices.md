# Notification Best Practices

## Severity Levels

| Severity | Response Time | Channel | Example |
|----------|---------------|---------|---------|
| Critical | Immediate | SMS + Email + Webhook | Production outage |
| Warning | 15 minutes | Email + Webhook | High resource usage |
| Info | 1 hour | Email only | Scheduled maintenance |

## Escalation Matrix

```
T+0 min:    Alarm triggered
T+0 min:    Level 1 notification (SMS/Email)
T+5 min:    If unacknowledged → Page on-call
T+15 min:   If unresolved → Escalate to manager
T+30 min:   If unresolved → Escalate to director
```

## Notification Routing

```python
def route_notification(alarm):
    severity = alarm['severity']

    if severity == 'critical':
        send_sms(alarm, on_call_engineer)
        send_email(alarm, team_list)
        trigger_pagerduty(alarm)
        post_to_slack(alarm, '#alerts-critical')
    elif severity == 'warning':
        send_email(alarm, team_list)
        post_to_slack(alarm, '#alerts-warning')
    else:
        send_email(alarm, team_list)
```

## Best Practices

1. **Avoid alert fatigue**: Tune thresholds based on historical data
2. **Multi-channel redundancy**: Critical alerts should use multiple channels
3. **Actionable notifications**: Include runbook links in alert messages
4. **Regular review**: Review disabled alarms monthly
