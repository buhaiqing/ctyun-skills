# Integration Guide — ctyun-eip-ops

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
endpoint = vpc.ctyun.cn
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
| `{{user.region_id}}` | User prompt or env | Region for EIP operations |
| `{{user.eip_id}}` | User prompt or output | EIP identifier |
| `{{user.instance_id}}` | User prompt | Target instance ID |
| `{{user.instance_type}}` | User prompt | 1(ECS)/2(VIP)/3(BM) |
| `{{user.bandwidth}}` | User prompt | Bandwidth in Mbps |
| `{{output.eip_id}}` | Parsed from JSON | From create response |
| `{{output.eip_address}}` | Parsed from JSON | Public IP address |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Create ECS instance for EIP association | `ctyun-ecs-ops` |
| Attach EIP to public load balancer | `ctyun-elb-ops` |
| Set bandwidth alarm for EIP | `ctyun-cloudmonitor-ops` |
| VPC/network configuration | `ctyun-vpc-ops` (planned) |
