# Redis Monitoring

## Available Metrics

Redis instances expose the following metrics through CTyun Cloud Monitor:

| Metric | Unit | Description |
|---|---|---|
| `CPUUtilization` | % | CPU usage rate |
| `MemoryUsage` | % | Memory usage rate |
| `QPS` | count/s | Queries per second |
| `Connections` | count | Active connections |
| `KeyCount` | count | Number of keys |
| `CacheHitRate` | % | Cache hit ratio |
| `NetworkIn` | bytes/s | Inbound network traffic |
| `NetworkOut` | bytes/s | Outbound network traffic |
| `CommandLatency` | ms | Average command latency |
| `ReplicationLag` | seconds | Data replication delay (cluster edition) |

## Recommended Alarm Rules

| Metric | Condition | Threshold | Severity |
|---|---|---|---|
| MemoryUsage | > 80% for 5 min | 80% | Warning |
| MemoryUsage | > 95% for 5 min | 95% | Critical |
| CPUUtilization | > 90% for 10 min | 90% | Warning |
| CacheHitRate | < 70% for 10 min | 70% | Warning |
| QPS | > 90% of max QPS for 5 min | 90% | Warning |
| Connections | > 80% of max connections | 80% | Warning |
| ReplicationLag | > 60 seconds | 60s | Critical |

## Instance Health Indicators

| Indicator | Healthy | Warning | Critical |
|---|---|---|---|
| Memory usage | < 70% | 70–90% | > 90% |
| Cache hit rate | > 90% | 70–90% | < 70% |
| CPU usage | < 60% | 60–85% | > 85% |
| Active connections | < 60% of max | 60–85% | > 85% |
| Command latency | < 10ms | 10–50ms | > 50ms |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for Redis metrics
- `ctyun-ecs-ops` — Monitor application-side Redis connection health
