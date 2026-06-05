# Integration Guide

## Environment Setup

### Python Environment

This skill requires Python 3.10+ and the `ctyun-cli` package:

```bash
# Create virtual environment (uv recommended)
uv venv --python 3.10
source .venv/bin/activate

# Install CLI + SDK
uv pip install ctyun-cli>=1.18.4
uv pip install ctyun-sdk>=1.0.0

# Verify
ctyun --version
python -c "from ctyun_sdk.services.ecs import ECSClient; print('SDK OK')"
```

### Credential Setup

**Both** CLI and SDK credential paths must be configured:

```bash
# --- Method 1: .env file (for agent runtime) ---
# Add to .env:
CTYUN_ACCESS_KEY=your_access_key_here
CTYUN_SECRET_KEY=your_secret_key_here
CTYUN_REGION_ID=cn-gz

# --- Method 2: CLI config file (for ctyun CLI) ---
mkdir -p ~/.ctyun
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION_ID|default("cn-gz")}}
endpoint = ecs.ctyun.cn
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
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | Default: `cn-gz` |
| `{{user.region_id}}` | User prompt | Ask once per session |
| `{{user.instance_id}}` | User prompt or output | Ask once per session or parse from prior output |
| `{{user.instance_name}}` | User prompt | Required for create |
| `{{user.flavor_id}}` | User prompt | Required for create/resize |
| `{{user.image_id}}` | User prompt | Required for create |
| `{{user.page_no}}` | User prompt | Default: 1 |
| `{{user.page_size}}` | User prompt | Default: 20 |
| `{{user.count}}` | User prompt | Default: 1 |
| `{{output.instance_id}}` | Parsed from JSON | From create-instance response |
| `{{output.job_id}}` | Parsed from JSON | From async operation response |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Monitor alarm rule CRUD | `ctyun-cloudmonitor-ops` |
| VPC / subnet / SG management | `ctyun-vpc-ops` (planned) |
| Elastic IP attachment | `ctyun-eip-ops` (planned) |
| Block storage management | `ctyun-ebs-ops` (planned) |
| Audit log query | `ctyun-audit-ops` (planned) |
| Load balancer config | `ctyun-elb-ops` (planned) |
| Container engine | `ctyun-cce-ops` (planned) |
