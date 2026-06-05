---
name: ctyun-redis-ops
version: 1.0.0
description: >
  Manage CTyun Redis (分布式缓存) instances — create, describe, delete,
  backup, monitor, and configure Redis cache instances. Primary route for
  any Redis or distributed caching task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.14.0"
  sdk_version_locked: ">=1.0.0"
  api_profile: redis.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-redis-ops

## Trigger & Scope

### SHOULD Use

- Create, list, describe, or delete Redis instances
- Create and manage backups
- Query instance performance metrics and topology
- List and manage network configurations
- Check available resource specifications and zones
- Any Redis-related troubleshooting (connection issues, high memory, backup failures)

### SHOULD NOT Use

- Cloud monitor alarm rule configuration → delegate to `ctyun-cloudmonitor-ops`
- ECS instance operations (app servers connecting to Redis) → delegate to `ctyun-ecs-ops`
- ELB load balancer operations → delegate to `ctyun-elb-ops`
- VPC/network operations → delegate to `ctyun-vpc-ops` (planned)
- EIP elastic IP operations → delegate to `ctyun-eip-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "Redis" or "cache" | Route here |
| User asks about "Redis instance" or "create instance" | Route here |
| User asks about "Redis backup" | Route here |
| User asks about "Redis metrics" or "monitor" | Route here |
| User asks about "monitor alarm" | Route to `ctyun-cloudmonitor-ops` |
| User asks about "ECS" or "server" | Route to `ctyun-ecs-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | `81f7728662dd11ec810800155d307d5b` |
| `{{user.instance_name}}` | Ask once, cache per session | `my-redis-cache` |
| `{{user.instance_id}}` | Ask once, cache per session | `redis-xxxxxxxx` |
| `{{user.edition}}` | Ask once, cache per session | `StandardSingle` |
| `{{user.engine_version}}` | Ask once, cache per session | `6.0` |
| `{{user.shard_mem_size}}` | Ask once, cache per session | `8` (GB) |
| `{{user.zone_name}}` | Ask once, cache per session | `cn-huabei2-tj-1a-public-ctcloud` |
| `{{user.vpc_id}}` | Ask once, cache per session | `vpc-grqvu4741a` |
| `{{user.subnet_id}}` | Ask once, cache per session | `subnet-gr36jdeyt0` |
| `{{user.password}}` | Ask once, cache per session | instance password |
| `{{output.instance_id}}` | Parsed from JSON output | from create-instance result |
| `{{output.connection_domain}}` | Parsed from JSON output | Redis endpoint address |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy defined in
[`AGENTS.md`](../AGENTS.md#execution-strategy).

### Pre-flight (shared)

1. Verify `ctyun` CLI is installed (`ctyun --version`; require >= 1.14.0)
2. Verify credentials configured (`test -n "$CTYUN_ACCESS_KEY"` and `test -n "$CTYUN_SECRET_KEY"`)
3. Determine `{{user.region_id}}` — from env `CTYUN_REGION_ID` or ask user if not set
4. Set `CTYUN_FORCE_CLI=1` or `CTYUN_FORCE_SDK=1` if overrides present

### Flow A: List Redis Instances

**CLI path (primary):**

```bash
ctyun --output json redis list-instances \
  {{user.region_id|"--region-id " + user.region_id}} \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.redis import RedisClient

client = RedisClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
instances = client.list_instances(
    region_id="{{user.region_id}}",
    page={{user.page_no|default(1)}},
    page_size={{user.page_size|default(20)}}
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Describe Redis Instance

**CLI path (primary):**

```bash
ctyun --output json redis get-instance \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}}
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for instance details.

### Flow C: Create Redis Instance

**CLI path (primary):**

```bash
ctyun --output json redis create-instance \
  --instance-name {{user.instance_name}} \
  --edition {{user.edition}} \
  --engine-version {{user.engine_version}} \
  --shard-mem-size {{user.shard_mem_size}} \
  --zone-name {{user.zone_name}} \
  --vpc-id {{user.vpc_id}} \
  --subnet-id {{user.subnet_id}} \
  --secgroups {{user.secgroup_id}} \
  --password {{user.password}}
```

**Dry-run validation (recommended before actual create):**

```bash
ctyun --output json redis create-instance \
  ...same params... --dry-run
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for `instanceId`.
**Idempotency:** Use `--dry-run` first to validate parameters without creating.

### Flow D: Delete Redis Instance

**CLI path (primary):**

```bash
ctyun --output json redis delete-instance \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}}
```

**Safety Gate (CRITICAL):** Before deletion, MUST:
1. Warn that this is **IRREVERSIBLE** — all data will be permanently deleted
2. Check instance status and whether it has active backups
3. Get explicit user confirmation

> "Delete Redis instance '{{user.instance_id}}' ({{user.instance_name}})?
> This is IRREVERSIBLE. All data in this instance will be permanently lost.
> Type 'yes' to confirm:"

### Flow E: Create Backup

**CLI path (primary):**

```bash
ctyun --output json redis create-backup \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}} \
  --backup-name {{user.backup_name|default("manual-backup-" + now())}}
```

**Validation:** Check `$.statusCode == 800`.

### Flow F: List Network Configurations

```bash
ctyun --output json redis list-network-configs \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}}
```

### Flow G: Get Instance Metrics

```bash
ctyun --output json redis get-instance-metrics \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}} \
  [--metric {{user.metric|default("MemoryUsage")}}]
```

### Flow H: Check Resources / Zones

**Check available resource specs:**

```bash
ctyun --output json redis check-resources \
  --region-id {{user.region_id}}
```

**List available zones:**

```bash
ctyun --output json redis zones \
  --region-id {{user.region_id}}
```

---

## Output Parsing Rules

All CLI responses follow the CTyun API envelope format:

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... },
  "_mock": false
}
```

### Common JSON Paths

| Operation | Data Path | Key Fields |
|---|---|---|
| List instances | `$.returnObj[]` | `instanceId, instanceName, engineVersion, edition, status, zoneName` |
| Get instance | `$.returnObj` | `instanceId, instanceName, engineVersion, edition, shardMemSize, vpcId, subnetId, securityGroupId, status, connectionDomain, port` |
| Create instance | `$.returnObj` | `instanceId, instanceName, connectionDomain, port` |
| List network configs | `$.returnObj[]` | `vpcId, subnetId, securityGroupId, networkType` |
| Check resources | `$.returnObj[]` | `edition, engineVersion, maxShardMemSize, availableZones[]` |
| List zones | `$.returnObj[]` | `zoneId, zoneName, status` |

### State Transition Table

| Operation | Previous State | Expected Next State |
|---|---|---|
| Create instance | — | `Creating` → `Active` |
| Delete instance | any | removed |
| Create backup | `Active` | `BackingUp` → `Active` |
| Modify config | `Active` | `Modifying` → `Active` |

---

## Failure Recovery

### Error Pattern Table

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` to user |
| `ctyun: command not found` | Environment | 3x | (re)install: `pip install ctyun-cli>=1.14.0` |
| `not authenticated` / `401` | Credentials | 3x | Check credentials; rewrite `~/.ctyun/config` |
| `5xx` / timeout / non-JSON | Runtime | 1x, then fallback | Retry once; if fails → SDK fallback |
| `subcommand not found` | Capability | No fallback | Upgrade CLI: `pip install --upgrade ctyun-cli` |
| `Redis.*` error codes | Business | No | Surface the specific error code |

### Common Redis Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| Instance not found | Wrong instance ID | Verify with `redis list-instances` |
| Insufficient resources | Region quota exceeded | Choose different region or edition |
| VPC/subnet not found | Wrong VPC ID | Verify VPC exists in the region |
| Password validation | Invalid password format | Min 8 chars, must contain letters and numbers |
| Deletion failed | Backup in progress | Wait for backup to complete |

---

## Prerequisites

### Environment

```bash
# Python 3.10+
pip install ctyun-cli>=1.14.0

# Verify
ctyun --version
```

### Credentials (two methods)

**Method A — Environment variables (recommended):**

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
export CTYUN_REGION_ID=your_region_id
```

**Method B — CLI config file:**

```bash
ctyun config init
# OR write manually:
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

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | delete operation is destructive and irreversible |
| `max_iterations` | `2` | inherited from §8 Redis default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with audit skills |
| `safety_confirm_required` | `true` | delete instance is irreversible |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first policy matrix |

### Artifacts

- [`references/rubric.md`](references/rubric.md) — concrete scoring rules
- [`references/prompt-templates.md`](references/prompt-templates.md) — G/C/O prompt skeletons

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-redis-ops skill — instance lifecycle, backup, monitoring operations |
