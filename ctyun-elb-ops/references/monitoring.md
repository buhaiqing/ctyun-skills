# ELB Monitoring

## Available Metrics

| Metric | Unit | Description |
|---|---|---|
| `ActiveConnections` | count | Current active connections |
| `NewConnections` | count/s | New connections per second |
| `InboundTraffic` | bytes/s | Inbound traffic rate |
| `OutboundTraffic` | bytes/s | Outbound traffic rate |
| `RequestCount` | count/s | Request rate |
| `HTTPCode_ELB_4XX` | count | ELB-generated 4XX errors |
| `HTTPCode_ELB_5XX` | count | ELB-generated 5XX errors |
| `HTTPCode_Backend_2XX` | count | Backend 2XX responses |
| `HTTPCode_Backend_4XX` | count | Backend 4XX responses |
| `HTTPCode_Backend_5XX` | count | Backend 5XX responses |
| `Latency` | ms | Average request latency |
| `HealthyHostCount` | count | Number of healthy targets |
| `UnHealthyHostCount` | count | Number of unhealthy targets |

## Recommended Alarm Rules

| Metric | Condition | Threshold | Severity |
|---|---|---|---|
| UnHealthyHostCount | > 0 for 2 min | > 0 | Critical |
| HTTPCode_ELB_5XX | > 1% for 5 min | 1% | Critical |
| HTTPCode_Backend_5XX | > 5% for 5 min | 5% | Warning |
| Latency | > 5000ms for 5 min | 5000 | Warning |
| ActiveConnections | > 80% of max | 80% | Warning |

## Health Indicators

| Indicator | Healthy | Warning | Critical |
|---|---|---|---|
| Healthy host ratio | 100% | 80–99% | < 80% |
| Avg latency | < 200ms | 200–1000ms | > 1000ms |
| 5XX error rate | < 0.1% | 0.1–1% | > 1% |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for ELB metrics
- `ctyun-ecs-ops` — Monitor backend server health
