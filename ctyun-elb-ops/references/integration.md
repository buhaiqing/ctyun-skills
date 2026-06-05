# Integration Guide — ctyun-elb-ops

## Environment Setup

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install ctyun-cli>=1.7.7
uv pip install ctyun-sdk>=1.0.0
ctyun --version
```

### Credential Setup

```bash
mkdir -p ~/.ctyun
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION_ID|default("cn-gz")}}
endpoint = elb.ctyun.cn
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
| `{{user.region_id}}` | User prompt or env | Region for ELB operations |
| `{{user.loadbalancer_id}}` | User prompt or output | Load balancer identifier |
| `{{user.targetgroup_id}}` | User prompt or output | Target group identifier |
| `{{user.health_check_id}}` | User prompt or output | Health check identifier |
| `{{user.target_id}}` | User prompt or output | Backend server identifier |
| `{{output.loadbalancer_id}}` | Parsed from JSON | From create-lb response |
| `{{output.targetgroup_id}}` | Parsed from JSON | From create-tg response |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Monitor alarm for LB performance | `ctyun-cloudmonitor-ops` |
| Register ECS instances as backends | `ctyun-ecs-ops` |
| Bind EIP to public LB | `ctyun-eip-ops` |
| Configure VPC/subnet for LB | `ctyun-vpc-ops` (planned) |
| HTTPS certificate management | `ctyun-kms-ops` |
