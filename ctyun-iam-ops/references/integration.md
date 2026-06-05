# Integration Guide

## Environment Setup

### Python Environment

This skill requires Python 3.10+ and the `ctyun-cli` package (v1.20.0+ for
full IAM support):

```bash
# Create virtual environment (uv recommended)
uv venv --python 3.10
source .venv/bin/activate

# Install CLI + SDK
uv pip install ctyun-cli>=1.20.0
uv pip install ctyun-sdk>=1.0.0

# Verify
ctyun --version
python -c "from ctyun_sdk.services.iam import IAMClient; print('SDK OK')"
```

### Credential Setup

**Both** CLI and SDK credential paths must be configured:

```bash
# --- Method 1: .env file (for agent runtime) ---
# Add to .env:
CTYUN_ACCESS_KEY=your_access_key_here
CTYUN_SECRET_KEY=your_secret_key_here
CTYUN_ACCOUNT_ID=your_account_id_here

# --- Method 2: CLI config file (for ctyun CLI) ---
mkdir -p ~/.ctyun
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = cn-gz
endpoint = iam.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

> The CLI reads from `~/.ctyun/config` (INI format). The SDK reads from
> `CTYUN_ACCESS_KEY` / `CTYUN_SECRET_KEY` environment variables.

## Variable Placeholders

Variables used in the skill flows:

| Variable | Source | Resolution |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | Auto-resolved, never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | Auto-resolved, never prompt |
| `{{env.CTYUN_ACCOUNT_ID}}` | Agent runtime env | Account ID for enterprise project operations |
| `{{user.account_id}}` | User prompt or env | Ask once per session if not in env |
| `{{user.user_name}}` | User prompt | Required for user operations |
| `{{user.group_name}}` | User prompt | Required for group operations |
| `{{user.policy_name}}` | User prompt | Required for policy operations |
| `{{user.policy_document}}` | User prompt | JSON policy definition |
| `{{user.role_name}}` | User prompt | Required for role operations |
| `{{user.access_key_id}}` | User prompt or output | Required for AK operations |
| `{{output.user_id}}` | Parsed from JSON | From create-user response |
| `{{output.group_id}}` | Parsed from JSON | From create-group response |
| `{{output.policy_id}}` | Parsed from JSON | From create-policy response |
| `{{output.role_id}}` | Parsed from JSON | From create-role response |
| `{{output.access_key_secret}}` | Parsed from JSON | From create-access-key (shown once) |
| `{{output.project_id}}` | Parsed from JSON | From list-projects response |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| IAM user event audit (login history, API call records) | `ctyun-audit-ops` (planned) |
| KMS key permission policy attached via IAM | `ctyun-kms-ops` (planned) |
| Monitor alarm rule for IAM access key expiry | `ctyun-cloudmonitor-ops` |
| IAM user resource tagging | `ctyun-tag-audit-ops` (planned) |
