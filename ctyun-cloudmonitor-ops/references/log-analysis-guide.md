# Log Analysis Guide

## Key Log Patterns

```
# Alarm triggered
[ALARM] alarm_id=al-xxx resource=i-xxx metric=CPUUtilization value=95.2 threshold=90

# Alarm resolved
[OK] alarm_id=al-xxx resource=i-xxx metric=CPUUtilization value=45.1 threshold=90

# Notification sent
[NOTIFY] alarm_id=al-xxx channel=sms recipient=+86xxx status=delivered

# Notification failed
[NOTIFY_FAIL] alarm_id=al-xxx channel=webhook error=timeout
```

## Common Log Queries

### Find all critical alarms in last hour

```bash
grep "CRITICAL" /var/log/cloudmonitor/alarm.log | \
  awk '$0 >= "'$(date -d '1 hour ago' +%Y-%m-%dT%H:%M)'"'
```

### Count alarms by namespace

```bash
awk '/ALARM/ {print $5}' /var/log/cloudmonitor/alarm.log | \
  cut -d= -f2 | sort | uniq -c | sort -rn
```

### Find notification failures

```bash
grep "NOTIFY_FAIL" /var/log/cloudmonitor/alarm.log | \
  awk -F'error=' '{print $2}' | sort | uniq -c
```

## Log Analysis Tips

1. **Correlate alarms**: Look for patterns across multiple resources
2. **Track false positives**: Monitor alarms that resolve quickly
3. **Audit notification delivery**: Ensure all channels are functioning
4. **Retention planning**: Archive logs beyond retention period for compliance
