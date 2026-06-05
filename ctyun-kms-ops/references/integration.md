# Integration Guide — ctyun-kms-ops

## Environment Setup

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install ctyun-cli>=1.7.7
uv pip install ctyun-sdk>=1.0.0
```

### Credential Setup

```bash
mkdir -p ~/.ctyun
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION_ID|default("cn-gz")}}
endpoint = kms.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

## Variable Placeholders

| Variable | Source | Resolution |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | Auto-resolved |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | Auto-resolved |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | Auto-resolved |
| `{{user.region_id}}` | User prompt or env | Region for KMS operations |
| `{{user.key_id}}` | User prompt or output | Key identifier |
| `{{user.key_name}}` | User prompt | Key alias name |
| `{{user.key_spec}}` | User prompt | SYMMETRIC_DEFAULT / RSA_2048 / EC_P256 |
| `{{user.pending_days}}` | User prompt | Days until deletion (7-30) |
| `{{output.key_id}}` | Parsed from JSON | From create response |
| `{{output.key_arn}}` | Parsed from JSON | Key ARN |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Set IAM policy for key access | `ctyun-iam-ops` |
| Configure key usage alarm | `ctyun-cloudmonitor-ops` |
| Enable EVS disk encryption | `ctyun-evs-ops` (planned) |
| Enable RDS database encryption | `ctyun-rds-ops` (planned) |
