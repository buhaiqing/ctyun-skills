# KMS Monitoring

## Available Metrics

| Metric | Unit | Description |
|---|---|---|
| `kms.key.usage.count` | count | Number of cryptographic operations |
| `kms.key.pending_deletion.count` | count | Keys in pending deletion state |
| `kms.key.rotation.count` | count | Number of key rotations performed |
| `kms.api.latency` | ms | API response latency |

## Recommended Alarm Rules

| Metric | Condition | Threshold | Severity |
|---|---|---|---|
| `kms.key.pending_deletion.count` | > 0 | > 0 | Warning |
| `kms.api.latency` | > 1000ms for 5 min | 1000 ms | Warning |

## Related Skills

- `ctyun-cloudmonitor-ops` — Configure alarm rules for KMS metrics
