# OOS Monitoring

## Available Metrics

CTyun Cloud Monitor provides the following OOS metrics. Alarms can be
configured via `ctyun-cloudmonitor-ops`.

### Bucket-level Metrics

| Metric | Description | Unit | Typical Threshold |
|---|---|---|---|
| `StorageBytes` | Total bucket storage size | Bytes | Alert if > 80% quota |
| `ObjectCount` | Total number of objects | Count | — |
| `GetRequests` | GET/HEAD request count | Count/min | Alert on sudden spikes |
| `PutRequests` | PUT/POST request count | Count/min | — |
| `DeleteRequests` | DELETE request count | Count/min | — |
| `TotalRequests` | All request types | Count/min | Rate limit: 1000/s per bucket |
| `IngressBytes` | Inbound traffic | Bytes/min | Monitor costs |
| `EgressBytes` | Outbound traffic | Bytes/min | Monitor costs |
| `4xxErrors` | Client error count | Count/min | Investigate > 1% of requests |
| `5xxErrors` | Server error count | Count/min | Alert on any |

## Monitoring via boto3

```python
import boto3
from botocore.config import Config

# OOS does not expose native S3 metrics via boto3;
# use CTyun Cloud Monitor API instead.
```

## Monitoring via Cloud Monitor

Delegate alarm rules to `ctyun-cloudmonitor-ops`:

```text
"Create an alarm rule for bucket my-bucket: alert when StorageBytes
 exceeds 1TB for 5 consecutive minutes."
```

## Grafana Dashboard

If Grafana is configured with CTyun Cloud Monitor as a data source, create
a dashboard panel with:

- **Storage growth** (StorageBytes over 7/30 days)
- **Request rate** (TotalRequests per minute)
- **Error rate** (4xx/5xx percentage)
- **Traffic** (Ingress/Egress daily totals)

## Key Practices

1. **Set budget alerts**: Monitor `StorageBytes` and `EgressBytes` to
   avoid unexpected bills
2. **Monitor 4xx errors**: A sudden rise indicates client-side issues
   (expired tokens, wrong permissions)
3. **Monitor 5xx errors**: Rare; contact CTyun support if persistent
4. **Use lifecycle policies**: Automatically expire or transition old
   data to reduce costs
