---
name: ctyun-elb-ops
version: 1.0.0
description: >
  Manage CTyun ELB (弹性负载均衡) resources — load balancers, target groups,
  backend servers, health checks, and monitoring. Primary route for any
  load balancing or traffic distribution task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.7.7"
  sdk_version_locked: ">=1.0.0"
  api_profile: elb.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-elb-ops

## Trigger & Scope

### SHOULD Use

- List, describe, create, or delete load balancers (internal/public)
- List and manage target groups
- Register or deregister backend servers (targets)
- Configure and view health checks
- Query real-time and historical monitoring metrics
- List and manage listeners
- Any ELB troubleshooting (502 errors, health check failures)

### SHOULD NOT Use

- Cloud monitor alarm rule configuration → delegate to `ctyun-cloudmonitor-ops`
- ECS instance operations → delegate to `ctyun-ecs-ops`
- EIP allocation/association → delegate to `ctyun-eip-ops`
- Redis cache operations → delegate to `ctyun-redis-ops`
- VPC/network operations → delegate to `ctyun-vpc-ops` (planned)
- Certificate/KMS operations → delegate to `ctyun-kms-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "load balancer" or "ELB" | Route here |
| User asks about "target group" or "backend" | Route here |
| User asks about "health check" | Route here |
| User asks about "monitor alarm" | Route to `ctyun-cloudmonitor-ops` |
| User asks about "ECS" or "server" | Route to `ctyun-ecs-ops` |
| User asks about "EIP" or "elastic IP" | Route to `ctyun-eip-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | region ID string |
| `{{user.loadbalancer_id}}` | Ask once, cache per session | `lb-xxxxxxxx` |
| `{{user.targetgroup_id}}` | Ask once, cache per session | `tg-xxxxxxxx` |
| `{{user.health_check_id}}` | Ask once, cache per session | `hc-xxxxxxxx` |
| `{{user.target_id}}` | Ask once, cache per session | target identifier |
| `{{output.loadbalancer_id}}` | Parsed from JSON output | from create response |
| `{{output.targetgroup_id}}` | Parsed from JSON output | from create response |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy.

### Pre-flight

1. Verify `ctyun` CLI (>= 1.7.7)
2. Verify credentials
3. Determine region ID

### Flow A: List Load Balancers

**CLI path (primary):**

```bash
ctyun --output json elb loadbalancer list \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.elb import ELBClient

client = ELBClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
lbs = client.list_load_balancers(region_id="{{user.region_id}}")
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Describe Load Balancer

```bash
ctyun --output json elb loadbalancer get \
  --region-id {{user.region_id}} \
  --loadbalancer-id {{user.loadbalancer_id}}
```

### Flow C: List / Get Target Groups

**List:**
```bash
ctyun --output json elb targetgroup list \
  --region-id {{user.region_id}}
```

**Get:**
```bash
ctyun --output json elb targetgroup get \
  --region-id {{user.region_id}} \
  --targetgroup-id {{user.targetgroup_id}}
```

### Flow D: Manage Backend Servers (Targets)

**List targets:**
```bash
ctyun --output json elb targetgroup targets list \
  --region-id {{user.region_id}} \
  --targetgroup-id {{user.targetgroup_id}}
```

**Show target details:**
```bash
ctyun --output json elb targetgroup targets show \
  --region-id {{user.region_id}} \
  --targetgroup-id {{user.targetgroup_id}} \
  --target-id {{user.target_id}}
```

> **Note:** Register/deregister targets are SDK-only operations (see API/SDK reference).

### Flow E: Health Check

```bash
ctyun --output json elb health-check show \
  --region-id {{user.region_id}} \
  --health-check-id {{user.health_check_id}}
```

### Flow F: Monitoring

**Realtime:**
```bash
ctyun --output json elb monitor realtime \
  --region-id {{user.region_id}} \
  --device-ids "{{user.device_ids}}"
```

**History:**
```bash
ctyun --output json elb monitor history \
  --region-id {{user.region_id}} \
  --device-ids "{{user.device_ids}}" \
  --metric-names "{{user.metric_names}}" \
  --start-time "{{user.start_time}}" \
  --end-time "{{user.end_time}}"
```

---

## Output Parsing Rules

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```

| Operation | Data Path | Key Fields |
|---|---|---|
| List LBs | `$.returnObj[]` | `loadBalancerId, loadBalancerName, status, address, vpcId` |
| Get LB | `$.returnObj` | `loadBalancerId, loadBalancerName, status, address, listenerIds[]` |
| List target groups | `$.returnObj[]` | `targetGroupId, targetGroupName, protocol` |
| List targets | `$.returnObj[]` | `targetId, targetIp, port, weight, healthStatus` |
| Health check | `$.returnObj` | `healthCheckId, protocol, port, interval, timeout` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `ctyun: command not found` | Environment | 3x | `pip install ctyun-cli>=1.7.7` |
| `5xx` / timeout | Runtime | 1x, then SDK | Retry once; SDK fallback |
| `subcommand not found` | Capability | No | Check CLI version; SDK fallback |
| `ELB.*` errors | Business | No | Surface specific error code |

> **Safety Gate:** Listener/backend delete and target deregistration operations are destructive.
> **REQUIRED:** Before executing, obtain explicit user confirmation including the
> resource ID and planned impact. Document the confirmation in the execution trace.

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `recommended` | Listener/backend delete has side effects |
| `max_iterations` | `3` | inherited from §8 ELB default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-elb-ops skill — load balancer, target group, health check, monitoring operations |
