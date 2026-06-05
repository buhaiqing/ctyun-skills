# KMS Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

```bash
pip install ctyun-cli>=1.7.7
```

### `subcommand not found`

KMS uses `ctyun kms` module. Verify with `ctyun kms --help`.

```bash
pip install --upgrade ctyun-cli
```

## API-Level Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API error | Surface `$.message` |
| `KMS.KeyNotFound` | Key ID does not exist | Verify the key ID |
| `KMS.KeyDeleting` | Key already in pending deletion | Wait or check status |
| `KMS.InvalidKeySpec` | Invalid key specification | Use: SYMMETRIC_DEFAULT, RSA_2048, EC_P256 |
| `KMS.InvalidPendingWindow` | Pending window out of range | Must be 7-30 days |
| `KMS.AccessDenied` | Insufficient permissions | Check IAM policy |
| `HTTP_500` | Server error | Retry with backoff |

## KMS-Specific Issues

### Cannot Create Key

**Possible causes:**
- Invalid key spec value
- Key name already exists (in some implementations)
- Region not supported for KMS

**Resolution:**
```bash
# Verify valid key specs
ctyun kms key create --help

# Check existing keys
ctyun kms key list --region-id <region>
```

### Cannot Schedule Deletion

**Possible causes:**
- Key is already in PendingDeletion state
- Invalid pending window value (<7 or >30 days)

**Resolution:**
```bash
# Check current key state
ctyun kms key get --region-id <region> --key-id <key_id>

# Cancel if already pending deletion
ctyun kms key cancel-deletion --region-id <region> --key-id <key_id>
```

### Key Not Showing Up in List

**Possible causes:**
- Key created in a different region
- Key has been deleted
- Filtered by different key state

**Resolution:**
```bash
# Check all regions if applicable
ctyun kms key list --region-id <another_region>
```

### Rotation Not Working

**Possible causes:**
- Key is disabled or pending deletion
- Key type doesn't support rotation

**Resolution:**
```bash
# Check key state
ctyun kms key get --region-id <region> --key-id <key_id>

# Verify key is Enabled
ctyun kms key enable --region-id <region> --key-id <key_id>

# Re-enable rotation
ctyun kms key enable-rotation --region-id <region> --key-id <key_id>
```

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI 5xx twice | SDK fallback |
| CLI command not found | SDK fallback |
| CLI non-JSON after retry | SDK fallback |

[Full matrix](../../ctyun-skill-generator/references/cli-decision-matrix.md)
