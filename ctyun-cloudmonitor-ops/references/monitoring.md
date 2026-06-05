# Monitoring Cloud Monitor

## Key Metrics for Cloud Monitor Service

### Service Health Metrics

| Metric | Description | Normal Range | Alert Threshold |
|--------|-------------|--------------|-----------------|
| API Success Rate | Percentage of successful API calls | > 99% | < 95% |
| API Latency P99 | 99th percentile API response time | < 500ms | > 1s |
| Webhook Delivery Rate | Percentage of successful webhook deliveries | > 99% | < 90% |
| Notification Delay | Time from alarm trigger to notification | < 30s | > 60s |

### Alarm Rule Health

| Metric | Description | Recommended Action |
|--------|-------------|-------------------|
| Alarm Rule Count | Total number of alarm rules | Monitor for quota approach |
| Enabled Alarm Ratio | Percentage of enabled alarms | Investigate disabled alarms |
| Alarm Trigger Rate | Frequency of alarm state changes | Tune thresholds if too high |
| False Positive Rate | Alarms that resolve without intervention | Increase evaluation count |

## Metric Namespaces

| Namespace | Service | Key Metrics |
|-----------|---------|-------------|
| ECS | Elastic Compute Service | CPUUtilization, MemoryUtilization, DiskUsage, NetworkIn, NetworkOut |
| RDS | Relational Database Service | CPUUtilization, ConnectionCount, QPS, TPS, StorageUsage |
| OSS | Object Storage Service | StorageSize, RequestCount, InternetTraffic, IntranetTraffic |
| SLB | Server Load Balancer | ActiveConnections, NewConnections, RequestCount, HTTPCode_5xx |
| VPC | Virtual Private Cloud | NetworkIn, NetworkOut, PacketLoss |

## Dashboard KPIs

| KPI | Target |
|-----|--------|
| MTTD (Mean Time to Detect) | < 5 minutes |
| MTTR (Mean Time to Resolve) | < 30 minutes |
| Alarm Fatigue Index | < 2 false alarms/day |
| Coverage Ratio | > 95% resources monitored |

## Metric Retention

| Granularity | Retention Period |
|-------------|-----------------|
| 1 minute | 15 days |
| 5 minutes | 31 days |
| 1 hour | 93 days |
| 1 day | 1 year |

## Alert Payload Structure

```json
{
  "alarmId": "al-xxxxxxxxxxxxxxxx",
  "alarmName": "ecs-high-cpu-critical",
  "namespace": "ECS",
  "metricName": "CPUUtilization",
  "resourceId": "i-xxxxxxxx",
  "status": "ALARM",
  "stateReason": "Threshold Crossed: 1 datapoint (95.2) was greater than the threshold (90.0).",
  "timestamp": "2026-06-05T12:00:00Z",
  "metricValue": 95.2,
  "threshold": 90.0,
  "unit": "Percent"
}
```

## See Also

- [Alarm Rules Examples](alarm-rules-examples.md) - Detailed YAML configurations for common scenarios
- [Notification Best Practices](notification-best-practices.md) - Routing, escalation, and severity guidelines
- [Log Analysis Guide](log-analysis-guide.md) - Log patterns and analysis queries
