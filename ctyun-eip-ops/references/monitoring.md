# EIP Monitoring

## Available Metrics

| Metric | Unit | Description |
|---|---|---|
| `OutBandwidth` | bps | Outbound bandwidth |
| `InBandwidth` | bps | Inbound bandwidth |
| `OutPackets` | count/s | Outbound packets per second |
| `InPackets` | count/s | Inbound packets per second |
| `DropPackets` | count/s | Dropped packets per second |

## Recommended Alarm Rules

| Metric | Condition | Threshold | Severity |
|---|---|---|---|
| OutBandwidth | > 80% of max for 10 min | 80% | Warning |
| InBandwidth | > 80% of max for 10 min | 80% | Warning |
| DropPackets | > 0 for 5 min | > 0 | Warning |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for EIP bandwidth
