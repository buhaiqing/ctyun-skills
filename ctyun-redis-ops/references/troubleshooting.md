# Redis Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

**Cause:** CLI not installed or not in PATH.

**Fix:**
```bash
pip install ctyun-cli>=1.14.0
ctyun --version
```

### `not authenticated` / status 401

**Cause:** Credentials not configured.

**Fix:**
```bash
test -n "$CTYUN_ACCESS_KEY" && echo "AK set" || echo "AK missing"
test -n "$CTYUN_SECRET_KEY" && echo "SK set" || echo "SK missing"
cat ~/.ctyun/config
```

### `subcommand not found`

**Cause:** CLI version too old; Redis command doesn't exist.

**Fix:**
```bash
ctyun --version
pip install --upgrade ctyun-cli
```

### Non-JSON output

**Cause:** API gateway returned HTML error or CLI crash.

**Fix:** Add `--output json` BEFORE the subcommand.

## API-Level Errors

| Error / Code | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API returned error | Surface `$.message` to user |
| `Redis.NotFound` | Instance does not exist | Verify instance ID with `redis list-instances` |
| `Redis.CreateFailed` | Instance creation failed | Check params, resource availability |
| `Redis.DeleteFailed` | Instance has backup in progress | Wait for backup to complete |
| `HTTP_403` | Insufficient permissions | Check account privileges |
| `HTTP_500` | Server-side error | Retry with backoff; contact support |

## Redis-Specific Issues

### Connection Refused

**Symptom:** Application cannot connect to Redis.

**Possible causes:**
- Instance not in Active state
- Security group blocks the port
- Wrong connection domain or port
- Password mismatch

**Resolution:**
```bash
# 1. Check instance status
ctyun redis get-instance --region-id <region> --instance-id <id>

# 2. Verify network config
ctyun redis list-network-configs --region-id <region> --instance-id <id>

# 3. Check security group rules for port 6379
```

### Instance Creation Failed

**Symptom:** `redis create-instance` returns error.

**Possible causes:**
- Invalid edition for the selected region
- Resource quota exceeded
- Invalid password format (length, characters)
- VPC/subnet not found

**Resolution:**
```bash
# Validate with dry-run first
ctyun redis create-instance ... --dry-run

# Check available specs
ctyun redis check-resources --region-id <region>
```

### Memory Usage High

**Symptom:** Memory usage > 90%, keys evicted.

**Resolution:**
1. Check key count: `ctyun redis get-instance-metrics`
2. Scale up shard memory or switch to DistributedCluster
3. Set key TTL policies in application
4. Review memory optimization: use smaller data types

### Backup Failure

**Symptom:** Backup creation fails.

**Possible causes:**
- Disk quota exceeded
- Instance is in modifying/backing-up state
- Too many concurrent operations

**Resolution:**
```bash
# Check instance state
ctyun redis get-instance --region-id <region> --instance-id <id>
# Retry after instance becomes Active
```

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI returns 5xx twice | Fall back to SDK for that operation |
| CLI command not found | Fall back to SDK |
| CLI output non-JSON after retry | Fall back to SDK |
| SDK also fails | Surface the API error to user |

Refer to [`cli-decision-matrix.md`](../../ctyun-skill-generator/references/cli-decision-matrix.md)
for the full fallback decision tree.
