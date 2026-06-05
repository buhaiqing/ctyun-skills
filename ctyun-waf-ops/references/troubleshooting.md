# WAF Troubleshooting Guide

## Common Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `statusCode: 800` failure | Invalid `regionId` or missing parameter | Verify region and required parameters |
| `statusCode: 100001` | Authentication failure (EOP signature) | Recompute signature with correct AK/SK |
| `statusCode: 100002` | Invalid access key or secret key | Verify `CTYUN_ACCESS_KEY` and `CTYUN_SECRET_KEY` |
| `statusCode: 200001` | Resource not found | Verify instance ID or domain ID exists |
| `statusCode: 200002` | Duplicate domain name | Domain already added to this instance |
| `SSL_ERROR` | HTTPS request to WAF API endpoint failed | Verify API endpoint URL is correct |
| `TimeoutError` | WAF API not responding | Retry with exponential backoff |

## Domain Protection Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| New domain not showing after add | Polling delay | Wait 10-30 seconds and query domain list |
| Domain still in `detect` mode | Protection mode not changed | Update to `protect` mode |
| HTTPS domain not protected | SSL cert not bound | Bind certificate to the domain |
| False positives (legit traffic blocked) | Overly aggressive rules | Switch to `detect` mode temporarily, tune rules |
| Attack traffic not blocked | WAF in `detect` mode | Change to `protect` mode |

## CLI/SDK Fallback

Since WAF is `sdk-only`, there is no CLI fallback path. All operations use the REST API directly.

## Debugging Checklist

1. Verify `regionId` is correct for the WAF instance
2. Check EOP signature generation (AK/SK values, timestamp)
3. Verify instance is in RUNNING state
4. Confirm domain is correctly added to the instance
5. Check protection mode for the domain
6. Review attack logs for false positives
7. Verify API endpoint URL (`waf.ctapi.ctyun.cn` + correct path)