# Troubleshooting — Cloud Monitor

## Common API Error Codes

| Code / HTTP | Meaning | Agent Action |
|-------------|---------|--------------|
| InvalidParameter / 400 | Request failed validation | Align parameters with OpenAPI spec; check data types |
| MissingParameter / 400 | Required parameter missing | Verify all required fields in request |
| ResourceNotFound / 404 | Alarm rule or resource not found | Verify alarm ID or resource ID exists |
| AlarmNameAlreadyExists / 409 | Alarm name already in use | Choose different name or modify existing alarm |
| QuotaExceeded / 403 | Alarm rule quota exceeded | Delete unused alarms or request quota increase |
| InsufficientBalance / 403 | Account balance insufficient | User must top up account |
| InternalError / 500 | Server internal error | Retry with exponential backoff; contact support if persists |
| Throttling / 429 | Rate limit exceeded | Back off; respect `Retry-After` header if present |
| InvalidTimeRange / 400 | Start time after end time | Correct time range parameters |
| InvalidPeriod / 400 | Unsupported period value | Use valid period: 60, 300, 3600, 86400 |

## Diagnostic Order

### General Problem Resolution

1. **Verify credentials:**
   ```bash
   # SDK mode
   python -c "import os; print('AK exists:', bool(os.environ.get('CTYUN_ACCESS_KEY')))"
   
   # CLI mode
   cat ~/.ctyun/config | grep access_key
   ```

2. **Check region availability:**
   - Verify `{{user.region}}` is a valid CTyun region
   - Some metrics may not be available in all regions

3. **Validate resource existence:**
   - Confirm `{{user.resource_id}}` exists in the specified namespace
   - Use the appropriate product skill to verify (e.g., `ctyun-ecs-ops`)

4. **Check API response:**
   - Capture full error response
   - Look for `$.error.message` or `$.error.code`
   - Include `requestId` when contacting support

### Alarm Rule Issues

| Symptom | Possible Cause | Resolution |
|---------|---------------|------------|
| Alarm not triggering | Threshold too high | Lower threshold based on actual metric values |
| Alarm triggering too often | Threshold too low / Evaluation count too low | Raise threshold or increase evaluation count |
| "Resource not found" error | Resource deleted or wrong ID | Verify resource still exists |
| "Invalid namespace" error | Unsupported namespace | Check valid namespaces in `core-concepts.md` |
| "Invalid metric" error | Metric not available for resource | Query available metrics with ListMetrics |

### Metric Data Issues

| Symptom | Possible Cause | Resolution |
|---------|---------------|------------|
| No data returned | Resource not yet monitored | Wait for data collection to start (5-15 min) |
| Gaps in data | Resource was stopped/restarted | Normal behavior for intermittent resources |
| Wrong values | Wrong statistic selected | Verify statistic matches metric type |
| Old data only | Time range incorrect | Check start/end time parameters |
| "Invalid period" error | Period not supported | Use valid period values: 60, 300, 3600, 86400 |

### Notification Issues

| Symptom | Possible Cause | Resolution |
|---------|---------------|------------|
| Not receiving alerts | Wrong action ARN | Verify ARN format: `arn:ctyun:{service}:{region}:{account}:alert` |
| Not receiving alerts | Alarm in INSUFFICIENT_DATA | Check metric data availability |
| Duplicate notifications | Multiple overlapping alarms | Consolidate or refine alarm rules |
| Alerts stopped | Alarm disabled | Check alarm status with DescribeAlarmRules |

## CLI-Specific Issues

| Symptom | Cause | Resolution |
|---------|-------|------------|
| `ctyun: command not found` | CLI not installed | Run `uv pip install ctyun-cli` |
| `invalid credentials` | Missing ~/.ctyun/config | Configure CLI credentials per SKILL.md |
| `--output json not valid` | Flag in wrong position | Move `--output json` BEFORE subcommand |
| Empty JSON response | API returned error | Check `$.error` in response |
| Region errors | Invalid region ID | Use valid CTyun region (e.g., cn-gz) |

## SDK-Specific Issues

| Symptom | Cause | Resolution |
|---------|-------|------------|
| `ModuleNotFoundError` | SDK not installed | Run `uv pip install ctyun-sdk` |
| `ImportError` | Wrong import path | Verify SDK module structure per `api-sdk-usage.md` |
| `CredentialError` | Missing env vars | Set CTYUN_ACCESS_KEY and CTYUN_SECRET_KEY |
| `AttributeError` | Wrong method name | Verify method exists in SDK client |
| Timeout errors | Network/connectivity | Check network; verify endpoint reachable |

## Retry Strategy

| Error Type | Retry Count | Backoff | Notes |
|------------|-------------|---------|-------|
| Throttling / 429 | 3 | Exponential (1s, 2s, 4s) | Respect `Retry-After` header |
| InternalError / 500 | 3 | 2s, 4s, 8s | Log requestId for support |
| Network timeout | 3 | 1s, 2s, 4s | Check connectivity |
| InvalidParameter | 0-1 | — | Fix params before retry |
| ResourceNotFound | 0 | — | Verify resource first |

## Getting Help

### Information to Collect

When reporting issues, include:

1. **Request ID:** From `$.requestId` in response
2. **Error Code:** From `$.error.code`
3. **Error Message:** From `$.error.message`
4. **Timestamp:** When the error occurred (ISO 8601)
5. **Region:** `{{user.region}}`
6. **Operation:** API operation attempted
7. **Environment:** Python version, SDK version, CLI version

### Support Channels

- CTyun Support Portal: https://www.ctyun.cn/help
- Documentation: https://www.ctyun.cn/document/10029510
- CLI Reference: https://www.ctyun.cn/act/xiaofeizhe/ctyun-cli
