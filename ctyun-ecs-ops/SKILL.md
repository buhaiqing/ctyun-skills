---
name: ctyun-ecs-ops
version: 1.0.0
description: >
  Manage CTyun Elastic Compute Service (ECS) instances —
  create, list, start, stop, reboot, resize, delete, snapshot,
  keypair, and image operations. Primary route for any ECS
  lifecycle task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.18.4"
  sdk_version_locked: ">=1.0.0"
  api_profile: ecs-global.ctapi.ctyun.cn
  api_version: v2.0
  lifecycle: shipped
---

# ctyun-ecs-ops

## Trigger & Scope

### SHOULD Use

- Create, list, describe, start, stop, reboot, resize, or delete ECS instances
- Manage ECS instance snapshots and custom images
- Manage SSH key pairs for ECS authentication
- Connect to instances via CloudShell (web-based terminal)
- Query ECS monitoring metrics, auto-renew config, or async job results
- Any ECS-related troubleshooting (instance stuck, launch failure, connectivity)

### SHOULD NOT Use

- VPC/subnet/security-group management → delegate to `ctyun-vpc-ops` (planned)
- Elastic IP management → delegate to `ctyun-eip-ops` (planned)
- Cloud monitor metric configuration (alarm rules) → delegate to `ctyun-cloudmonitor-ops`
- Block storage (cloud disk) CRUD beyond instance-attached disks → delegate to `ctyun-ebs-ops` (planned)
- Load balancer configuration → delegate to `ctyun-elb-ops` (planned)

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "create server" or "launch instance" | Route here |
| User asks about "stop/start/reboot instance" | Route here |
| User asks about "instance snapshot" or "instance image" | Route here |
| User asks about "SSH key pair" | Route here |
| User asks about "VPC" or "subnet" | Route to `ctyun-vpc-ops` |
| User asks about "monitor alarm rule" | Route to `ctyun-cloudmonitor-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | `200000001852` |
| `{{user.instance_id}}` | Ask once, cache per session | `8f284184-7df9-4b68-a2c1-f188541c23b2` |
| `{{user.instance_name}}` | Ask once, cache per session | `web-server-01` |
| `{{user.flavor_id}}` | Ask once, cache per session | `s6.small` |
| `{{user.image_id}}` | Ask once, cache per session | `8fd2f43b-af20-4aab-9a04-1a62972f4de9` |
| `{{output.instance_id}}` | Parsed from JSON output | from create-instance result |
| `{{output.job_id}}` | Parsed from JSON output | async job tracking |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy defined in
[`AGENTS.md`](../AGENTS.md#execution-strategy) and the [CLI-First Decision Matrix](../AGENTS.md#cli-first-policy-repository-wide).

### 1. Common Patterns

| Pattern | Detail |
|---|---|
| **SDK client init** | `client = ECSClient(access_key="{{env.CTYUN_ACCESS_KEY}}", secret_key="{{env.CTYUN_SECRET_KEY}}", region_id="{{user.region_id}}")` — full code in `references/api-sdk-usage.md` |
| **Response validation** | Check `$.statusCode == 800`. JSON envelope: `{"statusCode": 800, "message": "成功", "returnObj": {...}}` |
| **Pre-flight (shared)** | (1) `ctyun --version`, (2) `test -n "$CTYUN_ACCESS_KEY" && test -n "$CTYUN_SECRET_KEY"`, (3) resolve `{{user.region_id}}`, (4) apply `CTYUN_FORCE_CLI` / `CTYUN_FORCE_SDK` overrides |

### 2. Operation Summary

| Flow | Operation | CLI command | Safety Gate | Output path |
|---|---|---|---|---|
| A | List instances | `ctyun --output json ecs list --region-id {{user.region_id}} --page N --page-size N` | — | `$.returnObj.results[]` |
| B | Describe instance | `ctyun --output json ecs details {{user.instance_id}} --region-id {{user.region_id}}` | — | `$.returnObj` (instanceID, displayName, instanceStatus, privateIP, flavorName) |
| C | **Create instance** | `ctyun --output json ecs create --name "..." --instance-type ... --image-id ... --region-id ... --vpc-id ... --subnet-id ... --security-group-ids ... --count 1` | ✅ cost confirm | `$.returnObj.instanceID` |
| D | Start / Stop / Reboot | `ctyun --output json ecs start\|stop\|reboot {{user.instance_id}}` | ✅ stop/reboot confirm | `$.returnObj.jobID` |
| E | **Delete instance** | `ctyun --output json ecs delete {{user.instance_id}} --confirm` | ✅ **irreversible** | `$.returnObj` |
| F | Resize instance | `ctyun --output json ecs resize {{user.instance_id}} {{user.flavor_id}}` | — | `$.returnObj.jobID` |
| G | Snapshot management | `ctyun --output json ecs list-snapshots\|get-snapshot-details ... --instance-id ...` | — | `$.returnObj.results[]` |
| H | Key pair management | `ctyun --output json ecs list-keypairs --region-id ...` | — | `$.returnObj.results[]` |
| I | Create image from instance | `ctyun --output json ecs create-image {{user.instance_id}} --name "..."` | — | `$.returnObj` |
| J | List available flavors | `ctyun --output json ecs flavor-options --region-id {{user.region_id}}` | — | `$.returnObj` |
| K | Async job query | `ctyun --output json ecs query-async-result --region-id ... --job-id ...` | — | `$.returnObj.jobList[]` |
| L | Connect via CloudShell | `ctyun --output json ecs cloudshell {{user.instance_id}} --region-id ...` | — | `$.returnObj.consoleUrl` (expires 5min) |

> **Execution preference:** Prefer `ctyun` CLI per [CLI-First Policy](../../AGENTS.md#cli-first-policy-repository-wide). SDK init one-liner above; full SDK code in `references/api-sdk-usage.md`.

### 3. Per-Flow Details

#### A: List ECS Instances (read-only)

| CLI | `ctyun --output json ecs list --region-id {{user.region_id}} --page {{user.page_no\|default(1)}} --page-size {{user.page_size\|default(20)}}` |
|---|---|
| SDK | `client.list_instances(page_no={{user.page_no\|default(1)}}, page_size={{user.page_size\|default(20)}})` |

#### B: Describe Instance Details (read-only)

| CLI | `ctyun --output json ecs details {{user.instance_id}} --region-id {{user.region_id}}` |
|---|---|
| SDK | `client.get_instance(instance_id="{{user.instance_id}}", region_id="{{user.region_id}}")` |
| Fields | `$.returnObj.instanceID, displayName, instanceStatus, privateIP[], flavorName, imageName, expireTime` |

#### C: Create Instance (cost-incurring, requires safety gate)

| Aspect | Detail |
|---|---|
| ✅ Safety Gate | Confirm: "Create N instance(s) named '{{user.instance_name}}' (flavor: {{user.flavor_id}}, image: {{user.image_id}})? This will incur charges. (y/N)" |
| CLI | `ctyun --output json ecs create --name {{user.instance_name}} --instance-type {{user.flavor_id}} --image-id {{user.image_id}} --region-id {{user.region_id}} --system-disk-type SSD --system-disk-size 40 --vpc-id {{user.vpc_id}} --subnet-id {{user.subnet_id}} --security-group-ids {{user.security_group_ids}} --count {{user.count\|default(1)}}` |
| SDK | `client.create_instance(name="{{user.instance_name}}", instance_type="{{user.flavor_id}}", image_id="{{user.image_id}}", system_disk_type="SSD", system_disk_size=40, vpc_id="{{user.vpc_id}}", subnet_id="{{user.subnet_id}}", security_group_ids=["..."], count={{user.count\|default(1)}})` |
| Output | `$.returnObj.instanceID, jobID` |

#### D: Start / Stop / Reboot Instance

| Action | CLI | SDK | State transition |
|---|---|---|---|
| Start | `ctyun --output json ecs start {{user.instance_id}}` | `client.start_instance(instance_id="{{user.instance_id}}")` | stopped → running |
| Stop | `ctyun --output json ecs stop {{user.instance_id}}` | `client.stop_instance(instance_id="{{user.instance_id}}", force=False)` | running → stopped |
| Stop (force) | `ctyun --output json ecs stop {{user.instance_id}} --force` | `client.stop_instance(... force=True)` | any → stopped |
| Reboot | `ctyun --output json ecs reboot {{user.instance_id}}` | `client.reboot_instance(...)` | running → running |

#### E: Delete Instance (IRREVERSIBLE)

| Aspect | Detail |
|---|---|
| ✅ Safety Gate | MUST confirm: "Delete ECS instance {{user.instance_id}}? IRREVERSIBLE. Associated data disks will also be deleted. Type 'yes' to confirm." |
| CLI | `ctyun --output json ecs delete {{user.instance_id}} --confirm` |
| SDK | `client.delete_instance(instance_id="{{user.instance_id}}", delete_disk=True)` |

#### F: Resize Instance

| CLI | `ctyun --output json ecs resize {{user.instance_id}} {{user.flavor_id}}` |
|---|---|
| SDK | `client.resize_instance(instance_id="{{user.instance_id}}", instance_type="{{user.flavor_id}}")` |
| Pre-condition | Instance must be in `stopped` state |

#### G: Snapshot Management (read-only operations)

| Operation | CLI |
|---|---|
| List snapshots | `ctyun --output json ecs list-snapshots --region-id {{user.region_id}} --instance-id {{user.instance_id}} --page N --page-size N` |
| Get snapshot details | `ctyun --output json ecs get-snapshot-details --region-id {{user.region_id}} --snapshot-id {{user.snapshot_id}}` |

#### H: Key Pair Management (read-only)

| CLI | `ctyun --output json ecs list-keypairs --region-id {{user.region_id}} --page N` |
|---|---|
| Output | `$.returnObj.results[]` → keyPairID, keyPairName, fingerPrint, bindInstanceNum |

#### I: Create Image from Instance

| CLI | `ctyun --output json ecs create-image {{user.instance_id}} --name {{user.image_name}} --description "..."` |
|---|---|
| SDK | `client.create_image(instance_id="{{user.instance_id}}", name="{{user.image_name}}")` |

#### J: List Available Flavors (read-only)

| CLI | `ctyun --output json ecs flavor-options --region-id {{user.region_id}}` |
|---|---|
| SDK | `client.query_flavor_options()` |
| Output | `$.returnObj` → flavorNameScope[], flavorCPUScope[], flavorRAMScope[], flavorFamilyScope[] |

#### K: Async Job Query

| Operation | CLI |
|---|---|
| Single job | `ctyun --output json ecs query-async-result --region-id {{user.region_id}} --job-id {{user.job_id}}` |
| Multiple jobs | `ctyun --output json ecs query-jobs --region-id {{user.region_id}} --job-ids "[...]"` |
| Status | `$.returnObj.jobList[*].jobStatus` — 0=executing, 1=success, 2=fail |

#### L: Connect via CloudShell

CloudShell provides web-based terminal access to ECS instances (no SSH/public IP needed). Useful for troubleshooting, private subnet access, lost keys.

| CLI | `ctyun --output json ecs cloudshell {{user.instance_id}} --region-id {{user.region_id}}` |
|---|---|
| SDK | `client.get_instance_cloudshell(instance_id="{{user.instance_id}}", region_id="{{user.region_id}}")` |
| Output | `$.returnObj.consoleUrl` (expires in 5 minutes) |

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
| List instances | `$.returnObj.results[]` | `instanceID, displayName, instanceStatus, privateIP[], flavorName, imageName, expireTime` |
| Instance details | `$.returnObj` | `instanceID, displayName, instanceStatusStr, regionID, azName, flavorName, imageName, privateIP[], eipAddress[], vpcName, subnetName, createTime` |
| Create instance | `$.returnObj` | `instanceID, jobID` |
| Start/Stop/Reboot | `$.returnObj` | `instanceID, jobID` |
| List snapshots | `$.returnObj.results[]` | `snapshotID, snapshotName, snapshotStatus, instanceID, azName, createTime, members[]` |
| List keypairs | `$.returnObj.results[]` | `keyPairID, keyPairName, fingerPrint, bindInstanceNum, projectID` |
| Flavor options | `$.returnObj` | `flavorNameScope[], flavorCPUScope[], flavorRAMScope[], flavorFamilyScope[]` |
| Async job result | `$.returnObj.jobList[]` | `jobID, jobStatus (0=执行中/1=成功/2=失败)` |
| CloudShell URL | `$.returnObj` | `consoleUrl, expireTime` |

### State Transition Table

| Operation | Previous State | Expected Next State |
|---|---|---|
| Start | `stopped` / `stopping` | `running` |
| Stop (soft) | `running` | `stopped` |
| Stop (force) | `running` / any | `stopped` |
| Reboot | `running` | `running` (briefly `stopping` → `starting`) |
| Resize | `stopped` | `stopped` |
| Delete | any | removed |

---

## Failure Recovery

### Error Pattern Table

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` to user |
| `ctyun: command not found` | Environment | 3x | (re)install: `pip install ctyun-cli` |
| `not authenticated` / `401` | Credentials | 3x | Check `CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY` env vars; rewrite `~/.ctyun/config` |
| `5xx` / timeout / non-JSON | Runtime | 1x, then fallback | Retry once; if fails → SDK fallback for that operation |
| `subcommand not found` | Capability | No fallback | Check CLI version (`ctyun --version`); upgrade: `pip install --upgrade ctyun-cli` |
| Instance stuck in `stopping` | Business | 3x | Attempt `stop --force` |

### Common ECS Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `instanceStatus not in (stopped)` | Resize called on running instance | Stop instance first |
| `flavorQuotaExceeded` | Insufficient region quota | Choose different flavor or region |
| `securityGroupNotExist` | Security group ID invalid | Verify VPC/security group in that region |
| `imageNotExist` | Image ID invalid | List available images via `ctyun ims list-available` |
| `invalidInstanceType` | Flavor unavailable in region | Run `flavor-options` to list available flavors |
| `vpcQuotaExceeded` | VPC limit reached | Delete unused VPCs or request quota increase |

---

## Prerequisites

### Environment

```bash
# Python 3.10+
pip install ctyun-cli>=1.18.4

# Verify
ctyun --version
```

### Credentials (two methods)

**Method A — Environment variables (recommended):**

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
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
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

> **CRITICAL:** The `ctyun` CLI reads credentials from `~/.ctyun/config` INI file, NOT from environment variables. The SDK reads from `CTYUN_ACCESS_KEY`/`CTYUN_SECRET_KEY` env vars. Both paths must be configured.

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | delete/stop are destructive ECS operations |
| `max_iterations` | `2` | inherited from §8 ECS default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with audit skills |
| `safety_confirm_required` | `true` | delete, stop, resize, create-image are destructive |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first policy matrix |

### Artifacts

- [`references/rubric.md`](references/rubric.md) — concrete scoring rules
- [`references/prompt-templates.md`](references/prompt-templates.md) — G/C/O prompt skeletons

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-ecs-ops skill — create/list/start/stop/reboot/resize/delete/snapshot/keypair/image operations |
