---
name: ctyun-eip-ops
version: 1.0.0
description: >
  Manage CTyun EIP (弹性公网IP) resources — allocate, associate, disassociate,
  release, and monitor elastic public IP addresses. Primary route for any
  public IP or internet-facing access task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.7.7"
  sdk_version_locked: ">=1.0.0"
  api_profile: vpc.ctyun.cn
  api_version: v4/eip
  lifecycle: shipped
---

# ctyun-eip-ops

## Trigger & Scope

### SHOULD Use

- Allocate (create) a new elastic public IP
- Associate an EIP to an ECS instance, VIP, or BM
- Disassociate an EIP from a resource
- Release (delete) an unassociated EIP
- List and describe EIPs
- Change EIP bandwidth
- Query monitoring metrics for EIP

### SHOULD NOT Use

- ECS instance creation/management → delegate to `ctyun-ecs-ops`
- Load balancer operations → delegate to `ctyun-elb-ops`
- VPC/network operations → delegate to `ctyun-vpc-ops` (planned)
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- Cloud disk operations → delegate to `ctyun-evs-ops` (planned)

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "EIP" or "elastic IP" | Route here |
| User asks about "public IP" | Route here |
| User asks about "IP address" | Route here |
| User asks about "release EIP" | Route here (requires safety gate) |
| User asks about "ECS" or "server" | Route to `ctyun-ecs-ops` |
| User asks about "ELB" or "load balancer" | Route to `ctyun-elb-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | region ID string |
| `{{user.eip_id}}` | Ask once, cache per session | `eip-xxxxxxxx` |
| `{{user.instance_id}}` | Ask once, cache per session | target instance ID |
| `{{user.instance_type}}` | Ask once, cache per session | 1 (ECS) / 2 (VIP) / 3 (BM) |
| `{{user.bandwidth}}` | Ask once, cache per session | bandwidth in Mbps |
| `{{output.eip_id}}` | Parsed from JSON response | from create response |
| `{{output.eip_address}}` | Parsed from JSON response | allocated IP address |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy.

### Pre-flight

1. Verify `ctyun` CLI (>= 1.7.7)
2. Verify credentials
3. Determine region ID

### Flow A: List EIPs

**CLI path (primary):**

```bash
ctyun --output json vpc list-eips \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.vpc import VPCClient

client = VPCClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
eips = client.list_eips(region_id="{{user.region_id}}")
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Describe an EIP

```bash
ctyun --output json vpc describe-eip \
  --region-id {{user.region_id}} \
  --eip-id {{user.eip_id}}
```

### Flow C: Allocate (Create) an EIP

```bash
ctyun --output json vpc create-eip \
  --region-id {{user.region_id}} \
  --bandwidth {{user.bandwidth}} \
  --name "{{user.eip_name}}" \
  --client-token "{{output.client_token}}"
```

> **Safety Note:** Always generate a UUID `clientToken` for idempotency.

### Flow D: Associate EIP to Instance

```bash
ctyun --output json vpc associate-eip \
  --region-id {{user.region_id}} \
  --eip-id {{user.eip_id}} \
  --instance-id {{user.instance_id}} \
  --instance-type {{user.instance_type}} \
  --client-token "{{output.client_token}}"
```

### Flow E: Disassociate EIP

```bash
ctyun --output json vpc disassociate-eip \
  --region-id {{user.region_id}} \
  --eip-id {{user.eip_id}}
```

### Flow F: Release an EIP

```bash
ctyun --output json vpc delete-eip \
  --region-id {{user.region_id}} \
  --eip-id {{user.eip_id}}
```

> **Safety Gate:** This operation is IRREVERSIBLE. **REQUIRED**:
> 1. Confirm the EIP is disassociated
> 2. Ask user explicitly: "Release EIP `{{user.eip_id}}` (IP: `{{output.eip_address}}`)? This cannot be undone."
> 3. Only proceed on explicit `yes` confirmation

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
| List EIPs | `$.returnObj[]` | `eipId, eipAddress, bandwidth, status` |
| Describe EIP | `$.returnObj` | `eipId, eipAddress, bandwidth, status, instanceId` |
| Create EIP | `$.returnObj` | `eipId, eipAddress, bandwidth, createTime` |
| Associate | `$.returnObj` | `eipId, instanceId, status` |
| Disassociate | `$.returnObj` | `eipId, status` |
| Release | `$.returnObj` | `eipId, deleteTime` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `ctyun: command not found` | Environment | 3x | `pip install ctyun-cli>=1.7.7` |
| `5xx` / timeout | Runtime | 1x, then SDK | Retry once; SDK fallback |
| `subcommand not found` | Capability | No | Check CLI version; SDK fallback |
| `EIP.*` errors | Business | No | Surface specific error code |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Release EIP can break production |
| `max_iterations` | `2` | inherited from §8 EIP default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for release (delete) operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-eip-ops skill — allocate, associate, disassociate, release, monitor |
