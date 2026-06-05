# EIP Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

```bash
pip install ctyun-cli>=1.7.7
```

### `subcommand not found`

EIP uses `ctyun vpc` module. Verify with `ctyun vpc --help`.

```bash
pip install --upgrade ctyun-cli
```

## API-Level Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API error | Surface `$.message` |
| `EIP.AllocFailed` | Insufficient IP pool | Try different region |
| `EIP.AssociateConflict` | EIP already associated | Disassociate first |
| `EIP.NotFound` | EIP does not exist | Verify EIP ID |
| `HTTP_403` | Insufficient permissions | Check privileges |
| `HTTP_500` | Server error | Retry with backoff |

## EIP-Specific Issues

### Cannot Associate EIP

**Possible causes:**
- EIP already associated with another instance
- Target instance not in same region
- Instance type mismatch
- Missing clientToken causing idempotency error

**Resolution:**
```bash
# 1. Check EIP status
ctyun vpc describe-eip --region-id <region> --eip-id <eip_id>

# 2. Disassociate if already in use
ctyun vpc disassociate-eip --region-id <region> --eip-id <eip_id>

# 3. Retry association with new clientToken
```

### Cannot Release EIP

**Possible causes:**
- EIP still associated with an instance
- EIP is in Pending/Busy state

**Resolution:**
```bash
# 1. Disassociate first
ctyun vpc disassociate-eip --region-id <region> --eip-id <eip_id>

# 2. Verify status is Available
ctyun vpc describe-eip --region-id <region> --eip-id <eip_id>

# 3. Release
ctyun vpc delete-eip --region-id <region> --eip-id <eip_id>
```

### EIP Not Reachable

**Possible causes:**
- Security group not allowing inbound traffic
- No routing to the attached instance
- Bandwidth set to 0 or throttled

**Resolution:**
1. Check security group rules for the attached instance
2. Verify bandwidth configuration
3. Test connectivity from outside the VPC

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI 5xx twice | SDK fallback |
| CLI command not found | SDK fallback |
| CLI non-JSON after retry | SDK fallback |

[Full matrix](../../ctyun-skill-generator/references/cli-decision-matrix.md)
