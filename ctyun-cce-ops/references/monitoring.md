# CCE Monitoring

## Available Metrics

| Metric | Unit | Description |
|---|---|---|
| `cluster.cpu.usage` | % | Cluster-wide CPU utilization |
| `cluster.memory.usage` | % | Cluster-wide memory utilization |
| `cluster.disk.usage` | % | Cluster-wide disk utilization |
| `node.cpu.usage` | % | Per-node CPU utilization |
| `node.memory.usage` | % | Per-node memory utilization |
| `node.disk.usage` | % | Per-node disk utilization |
| `pod.cpu.usage` | cores | Per-pod CPU usage |
| `pod.memory.usage` | MB | Per-pod memory usage |
| `pod.restart.count` | count | Pod restart count |

## Recommended Alarm Rules

| Metric | Condition | Threshold | Severity |
|---|---|---|---|
| cluster.cpu.usage | > 80% for 10 min | 80% | Warning |
| cluster.memory.usage | > 80% for 10 min | 80% | Warning |
| node.disk.usage | > 85% for 10 min | 85% | Warning |
| pod.restart.count | > 3 in 5 min | 3 | Critical |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for CCE metrics
