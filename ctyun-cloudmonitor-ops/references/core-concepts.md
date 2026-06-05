# Core Concepts — Cloud Monitor

## Overview

CTyun Cloud Monitor (云监控) is a comprehensive monitoring service that provides metric collection, alarm management, and historical analysis for cloud resources. It enables proactive monitoring of resource health and performance through customizable alarm rules.

## Key Concepts

### 1. Namespace

A **namespace** is a container for metrics related to a specific service or resource type.

| Namespace | Description | Example Metrics |
|-----------|-------------|-----------------|
| ECS | Elastic Compute Service | CPUUtilization, MemoryUtilization, DiskUsage |
| RDS | Relational Database Service | ConnectionCount, QPS, TPS |
| OSS | Object Storage Service | StorageSize, RequestCount |
| SLB | Server Load Balancer | ActiveConnections, RequestCount |

### 2. Metric

A **metric** represents a time-series measurement from a cloud resource.

**Metric Structure:**
```
{namespace}/{metricName}/{dimension}
```

**Example:**
- `ECS/CPUUtilization/InstanceId=i-xxxxxxxx`

**Common Metric Names:**

| Service | Metric Name | Unit | Description |
|---------|-------------|------|-------------|
| ECS | CPUUtilization | Percent | CPU usage percentage |
| ECS | MemoryUtilization | Percent | Memory usage percentage |
| ECS | DiskUsage | Percent | Disk usage percentage |
| ECS | NetworkIn | Bytes | Incoming network traffic |
| ECS | NetworkOut | Bytes | Outgoing network traffic |
| RDS | ConnectionCount | Count | Current connections |
| RDS | QPS | Count/Second | Queries per second |
| RDS | TPS | Count/Second | Transactions per second |

### 3. Dimension

**Dimensions** are key-value pairs that identify the specific resource for a metric.

| Dimension Key | Description | Example |
|---------------|-------------|---------|
| InstanceId | ECS instance ID | i-xxxxxxxx |
| DBInstanceId | RDS instance ID | rm-xxxxxxxx |
| BucketName | OSS bucket name | my-bucket |

### 4. Alarm Rule

An **alarm rule** defines conditions for triggering alerts based on metric values.

**Alarm Rule Components:**

| Component | Description |
|-----------|-------------|
| Alarm Name | Human-readable identifier |
| Metric | Namespace + MetricName + Dimensions |
| Period | Evaluation interval (60s, 300s, 3600s, 86400s) |
| Statistic | Aggregation function (Average, Minimum, Maximum, Sum, SampleCount) |
| Comparison Operator | Threshold comparison (>, <, >=, <=) |
| Threshold | Trigger value |
| Evaluation Count | Consecutive periods before alerting (1-10) |
| Actions | Notification channels for each state |

### 5. Alarm States

| State | Description | Color |
|-------|-------------|-------|
| ALARM | Metric threshold breached | Red |
| OK | Metric within threshold | Green |
| INSUFFICIENT_DATA | Not enough data to evaluate | Gray |

### 6. Period

The **period** defines the time window for metric aggregation.

| Period | Use Case |
|--------|----------|
| 60 seconds | High-frequency monitoring, critical systems |
| 300 seconds (5 min) | Standard monitoring |
| 3600 seconds (1 hour) | Long-term trends |
| 86400 seconds (24 hours) | Daily summaries |

### 7. Statistic

**Statistics** aggregate metric data over the period.

| Statistic | Description | Use Case |
|-----------|-------------|----------|
| Average | Mean value | General trends |
| Minimum | Lowest value | Peak detection (inverse) |
| Maximum | Highest value | Peak detection |
| Sum | Total value | Cumulative metrics |
| SampleCount | Number of samples | Data availability |

### 8. Comparison Operators

| Operator | Symbol | Example |
|----------|--------|---------|
| GreaterThanThreshold | > | CPU > 80% |
| LessThanThreshold | < | Disk < 10% |
| GreaterThanOrEqualToThreshold | >= | Connections >= 1000 |
| LessThanOrEqualToThreshold | <= | Memory <= 20% |

### 9. Evaluation Count

**Evaluation Count** prevents false positives by requiring multiple consecutive breaches.

- **Count = 1:** Alert immediately on first breach (sensitive)
- **Count = 3:** Alert after 3 consecutive breaches (balanced)
- **Count = 5:** Alert after 5 consecutive breaches (conservative)

Example with 300s period:
- Count=3 means alert after 15 minutes of continuous breach

### 10. Alarm Actions

**Actions** define notification channels for alarm state changes.

| Action Type | ARN Format | Description |
|-------------|------------|-------------|
| SMS | `arn:ctyun:sms:{region}:{account}:alert` | SMS notification |
| Email | `arn:ctyun:email:{region}:{account}:alert` | Email notification |
| Webhook | `arn:ctyun:webhook:{region}:{account}:endpoint` | HTTP callback |

### 11. Alarm History

**Alarm History** records state transitions over time.

| Field | Description |
|-------|-------------|
| Timestamp | When the state change occurred |
| Alarm ID | Associated alarm rule |
| Old State | Previous alarm state |
| New State | Current alarm state |
| Metric Value | Value at time of transition |
| Reason | Human-readable explanation |

## Architecture

```
┌─────────────────┐
│  Cloud Resources │
│  (ECS, RDS, ...) │
└────────┬────────┘
         │
         ▼ Metrics
┌─────────────────┐
│  Cloud Monitor  │
│  - Collect      │
│  - Store        │
│  - Analyze      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Alarms  │ │ History │
└────┬────┘ └─────────┘
     │
     ▼ Actions
┌─────────────────┐
│  Notifications  │
│  (SMS, Email)   │
└─────────────────┘
```

## Quotas and Limits

| Resource | Default Limit | Adjustable |
|----------|---------------|------------|
| Alarm Rules per Region | 100 | Yes (support ticket) |
| Alarms per Resource | 10 | No |
| Metric Retention | 15 days | No |
| API Rate Limit (Write) | 10/s | Yes |
| API Rate Limit (Read) | 100/s | Yes |

## Best Practices

### Alarm Configuration

1. **Use descriptive names:** `prod-ecs-web01-cpu-alert`
2. **Set appropriate thresholds:** Based on historical data, not guesses
3. **Tune evaluation counts:** Balance sensitivity vs. false positives
4. **Group related alarms:** Same resource, similar metrics
5. **Document alarm purposes:** Comment or tag alarms

### Metric Selection

1. **Monitor what matters:** Focus on user-impacting metrics
2. **Use appropriate periods:** Match to metric volatility
3. **Consider seasonality:** Business hours vs. off-hours
4. **Track trends, not just thresholds:** Use history for capacity planning

### Notification Strategy

1. **Multiple channels:** SMS for critical, email for informational
2. **Escalation paths:** On-call rotation for unacknowledged alerts
3. **Quiet hours:** Suppress non-critical alerts during maintenance
4. **Alarm grouping:** Prevent notification storms
