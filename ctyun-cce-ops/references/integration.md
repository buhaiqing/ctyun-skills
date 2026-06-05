# Integration Guide — ctyun-cce-ops

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
endpoint = cce.ctyun.cn
scheme = https
timeout = 30
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

## Variable Placeholders

| Variable | Source | Resolution |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | Auto-resolved |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | Auto-resolved |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | Auto-resolved |
| `{{user.region_id}}` | User prompt or env | Region for CCE operations |
| `{{user.cluster_id}}` | User prompt or output | Cluster identifier |
| `{{user.nodepool_id}}` | User prompt or output | Node pool identifier |
| `{{output.cluster_id}}` | Parsed from JSON | From create response |
| `{{output.kubeconfig}}` | Parsed from JSON | Base64 kubeconfig |

## Cross-Skill Integration

| Scenario | Delegate to |
|---|---|
| Create ECS for worker nodes | `ctyun-ecs-ops` |
| Expose service via load balancer | `ctyun-elb-ops` |
| Assign public IP to cluster API | `ctyun-eip-ops` |
| Monitor cluster metrics | `ctyun-cloudmonitor-ops` (planned) |
| Attach EVS persistent volume | `ctyun-evs-ops` (planned) |
