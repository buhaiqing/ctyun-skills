# Alarm Rules Examples

Detailed alarm rule configurations for common operational scenarios.

## Critical Infrastructure Alarms

### High CPU Alarm

```yaml
name: ecs-high-cpu-critical
namespace: ECS
metric: CPUUtilization
threshold: 90
period: 300
evaluation_count: 3
severity: critical
```

### High Memory Alarm

```yaml
name: ecs-high-memory-critical
namespace: ECS
metric: MemoryUtilization
threshold: 90
period: 300
evaluation_count: 3
severity: critical
```

### Disk Space Alarm

```yaml
name: ecs-disk-space-warning
namespace: ECS
metric: DiskUsage
threshold: 85
period: 300
evaluation_count: 2
severity: warning
```

## Database Alarms

### RDS Connection Limit

```yaml
name: rds-connections-warning
namespace: RDS
metric: ConnectionCount
threshold: 80  # percent of max
period: 300
evaluation_count: 3
severity: warning
```

### RDS CPU Alarm

```yaml
name: rds-high-cpu-critical
namespace: RDS
metric: CPUUtilization
threshold: 85
period: 300
evaluation_count: 3
severity: critical
```

### RDS Storage Alarm

```yaml
name: rds-storage-critical
namespace: RDS
metric: StorageUsage
threshold: 90
period: 3600
evaluation_count: 1
severity: critical
```

## Load Balancer Alarms

### 5xx Error Rate

```yaml
name: slb-5xx-errors-critical
namespace: SLB
metric: HTTPCode_5xx
threshold: 10  # count per minute
period: 60
evaluation_count: 5
severity: critical
```

### High Connection Count

```yaml
name: slb-connections-warning
namespace: SLB
metric: ActiveConnections
threshold: 10000
period: 300
evaluation_count: 3
severity: warning
```

## Capacity Planning Alarms

### Alarm Quota Monitoring

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| Alarm Rule Usage | 80% of quota | 95% of quota |
| API Call Rate | 70% of limit | 90% of limit |
| Webhook Endpoint Health | 1 failure / hour | 5 failures / hour |

### Growth Projection

```python
# Example: Project when to request quota increase
current_alarms = 80
quota = 100
growth_rate = 5  # new alarms per week
weeks_until_quota = (quota - current_alarms) / growth_rate
# Request increase when weeks_until_quota < 4
```
