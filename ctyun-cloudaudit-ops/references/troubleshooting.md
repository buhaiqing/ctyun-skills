# Cloud Audit Troubleshooting Guide

## Common Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `statusCode: 800` failure | Invalid `regionId` or missing parameter | Verify region and required parameters |
| `statusCode: 100001` | Authentication failure (EOP signature) | Recompute signature with correct AK/SK |
| `statusCode: 100002` | Invalid access key or secret key | Verify `CTYUN_ACCESS_KEY` and `CTYUN_SECRET_KEY` |
| `statusCode: 200001` | No events found for the query | Expand time range or check parameters |
| `statusCode: 200002` | Invalid time range format | Use ISO 8601 format (e.g., `2026-01-01T00:00:00Z`) |
| `statusCode: 400001` | Log export bucket not found | Verify OOS bucket name and region |
| `TimeoutError` | Large time range query | Reduce time range or paginate |

## Query Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Empty results | No events match the filter | Expand time range or remove filters |
| Missing expected events | Event retention period exceeded | Events older than 90 days not available via API |
| Incomplete results | Large result set not paginated | Use `pageNumber` and `pageSize` for pagination |
| Wrong resource events | Resource type filter incorrect | Verify the correct resource type name (e.g., `ecs`, not `ECS`) |

## Export Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Export fails | OOS bucket not in same region | Create bucket in same region as audit source |
| Export completes but empty | No events in the time range | Expand time range |
| Export takes long | Large time range | Split into smaller time windows |

## CLI/SDK Fallback

Since Cloud Audit (CTS) is `sdk-only`, there is no CLI fallback path. Note that `ctyun-cli` has a different `audit` module that is NOT Cloud Audit.

## Debugging Checklist

1. Verify `regionId` is correct
2. Check time range is within 90-day retention window
3. For empty results: remove resource type filter and query all events
4. For large result sets: use pagination (`pageNumber`, `pageSize`)
5. For export: verify OOS bucket exists in the same region
6. Check if CTS is enabled in the target region
7. Verify API endpoint URL (`cts.ctapi.ctyun.cn` + correct path)