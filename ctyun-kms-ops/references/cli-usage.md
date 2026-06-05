# CTyun KMS CLI Usage

> KMS operations are available through the `ctyun kms` module.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.7.7`.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json kms key list` |

## KMS Commands

### Key Operations

```bash
# List all keys
ctyun --output json kms key list --region-id <region>

# Describe a key
ctyun --output json kms key get --region-id <region> --key-id <key_id>

# Create a key
ctyun --output json kms key create --region-id <region> --alias <alias> --description <desc>

# Enable a key
ctyun --output json kms key enable --region-id <region> --key-id <key_id>

# Disable a key
ctyun --output json kms key disable --region-id <region> --key-id <key_id>

# Schedule key deletion (irreversible after pending window)
ctyun --output json kms key schedule-deletion --region-id <region> --key-id <key_id> --pending-window <days>

# Cancel scheduled deletion
ctyun --output json kms key cancel-deletion --region-id <region> --key-id <key_id>
```

## Output Format

```bash
ctyun --output json kms key list --region-id <region>
ctyun --output json kms key get --region-id <region> --key-id <key_id>
ctyun --output json kms key create --region-id <region> --alias "my-key" --description "My encryption key"
```
