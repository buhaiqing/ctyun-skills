# Integration Guide — ctyun-redis-ops

## Environment Setup

### Python Environment

```bash
# Create virtual environment (uv recommended)
uv venv --python 3.10
source .venv/bin/activate

# Install CLI
uv pip install ctyun-cli>=1.14.0
uv pip install ctyun-sdk>=1.0.0

# Verify
ctyun --version
python -c "from ctyun_sdk.services.redis import RedisClient; print('SDK OK')"
```

### Credential Setup

**Both** CLI and SDK credential paths must be configured:

```bash
# --- Method 1: .env file (for agent runtime) ---
# Add to .env:
CTYUN_ACCESS_KEY=your_access_key_here
CTYUN_SECRET_KEY=your_secret_key_here
CTYUN_REGION_ID=your_region_id_here

# --- Method 2: CLI config file (for ctyun CLI) ---
mkdir -p ~/.ctyun
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION_ID|default("cn-gz")}}
endpoint = redis.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

### Pre-flight Check

```bash
# Before any Redis operation
python3 scripts/preflight-check.py --verbose
```

## Variable Placeholders

| Variable | Source | Resolution |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | Auto-resolved, never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | Auto-resolved, never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | Auto-resolved, never prompt |
| `{{user.region_id}}` | User prompt or env | Region for Redis operations |
| `{{user.instance_name}}` | User prompt | Redis instance name |
| `{{user.instance_id}}` | User prompt or output | Instance identifier |
| `{{user.edition}}` | User prompt | StandardSingle / StandardCluster / DistributedCluster |
| `{{user.engine_version}}` | User prompt | 4.0 / 5.0 / 6.0 / 7.0 |
| `{{user.shard_mem_size}}` | User prompt | Memory size in GB |
| `{{user.zone_name}}` | User prompt | Availability zone |
| `{{user.vpc_id}}` | User prompt | VPC identifier |
| `{{user.subnet_id}}` | User prompt | Subnet identifier |
| `{{user.password}}` | User prompt | Redis instance password |
| `{{output.instance_id}}` | Parsed from JSON | From create-instance response |
| `{{output.connection_domain}}` | Parsed from JSON | Redis connection endpoint |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Set alarm rules for Redis metrics | `ctyun-cloudmonitor-ops` |
| Create ECS app server to connect to Redis | `ctyun-ecs-ops` |
| Configure VPC/network for Redis | `ctyun-vpc-ops` (planned) |
| Redis access audit | `ctyun-audit-ops` (planned) |
