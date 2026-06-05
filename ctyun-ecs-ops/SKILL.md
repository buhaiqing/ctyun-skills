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
[`AGENTS.md`](../AGENTS.md#execution-strategy).

### Pre-flight (shared)

1. Verify `ctyun` CLI is installed (`ctyun --version`)
2. Verify credentials configured (`test -n "$CTYUN_ACCESS_KEY"` and `test -n "$CTYUN_SECRET_KEY"`)
3. Determine `{{user.region_id}}` — ask user if not already cached
4. Set `CTYUN_FORCE_CLI=1` or `CTYUN_FORCE_SDK=1` if overrides present

### Flow A: List ECS Instances

**CLI path (primary):**

```bash
ctyun --output json ecs list \
  --region-id {{user.region_id}} \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.ecs import ECSClient

client = ECSClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    region_id="{{user.region_id}}"
)
instances = client.list_instances(
    page_no={{user.page_no|default(1)}},
    page_size={{user.page_size|default(20)}}
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj.results[]`.

### Flow B: Describe Instance Details

**CLI path (primary):**

```bash
ctyun --output json ecs details {{user.instance_id}} \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
client = ECSClient(...)
instance = client.get_instance(
    instance_id="{{user.instance_id}}",
    region_id="{{user.region_id}}"
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for `instanceID`, `displayName`, `instanceStatus`, `privateIP`, `flavorName`.

### Flow C: Create Instance

**CLI path (primary):**

```bash
ctyun --output json ecs create \
  --name {{user.instance_name}} \
  --instance-type {{user.flavor_id}} \
  --image-id {{user.image_id}} \
  --region-id {{user.region_id}} \
  --system-disk-type {{user.system_disk_type|default("SSD")}} \
  --system-disk-size {{user.system_disk_size|default(40)}} \
  --vpc-id {{user.vpc_id}} \
  --subnet-id {{user.subnet_id}} \
  --security-group-ids {{user.security_group_ids}} \
  --count {{user.count|default(1)}}
```

**SDK fallback:**

```python
client = ECSClient(...)
result = client.create_instance(
    name="{{user.instance_name}}",
    instance_type="{{user.flavor_id}}",
    image_id="{{user.image_id}}",
    system_disk_type="{{user.system_disk_type|default('SSD')}}",
    system_disk_size={{user.system_disk_size|default(40)}},
    vpc_id="{{user.vpc_id}}",
    subnet_id="{{user.subnet_id}}",
    security_group_ids=["{{user.security_group_ids}}"],
    count={{user.count|default(1)}}
)
```

**Safety Gate:** Instance creation incurs cost. Confirm with user before proceeding:
> "Create {{user.count|default(1)}} ECS instance(s) named '{{user.instance_name}}'
> (flavor: {{user.flavor_id}}, image: {{user.image_id}})? This will incur charges. (y/N)"

### Flow D: Start / Stop / Reboot Instance

**Start:**

```bash
ctyun --output json ecs start {{user.instance_id}}
```

**Stop:**

```bash
ctyun --output json ecs stop {{user.instance_id}}
```

**Stop (force):**

```bash
ctyun --output json ecs stop {{user.instance_id}} --force
```

**Reboot:**

```bash
ctyun --output json ecs reboot {{user.instance_id}}
```

**SDK fallback (all three):**

```python
client = ECSClient(...)
client.start_instance(instance_id="{{user.instance_id}}")
client.stop_instance(instance_id="{{user.instance_id}}", force=False)
client.reboot_instance(instance_id="{{user.instance_id}}", force=False)
```

**Validation:** Check `$.statusCode == 800`.

### Flow E: Delete Instance

**CLI path (primary):**

```bash
ctyun --output json ecs delete {{user.instance_id}} --confirm
```

**SDK fallback:**

```python
client = ECSClient(...)
client.delete_instance(
    instance_id="{{user.instance_id}}",
    delete_disk=True
)
```

**Safety Gate (CRITICAL):** Before deletion, MUST confirm with user:
> "Delete ECS instance {{user.instance_id}}? This is IRREVERSIBLE.
> Associated data disks will also be deleted. Type 'yes' to confirm:"

### Flow F: Resize Instance

**CLI path (primary):**

```bash
ctyun --output json ecs resize {{user.instance_id}} {{user.flavor_id}}
```

**SDK fallback:**

```python
client = ECSClient(...)
client.resize_instance(
    instance_id="{{user.instance_id}}",
    instance_type="{{user.flavor_id}}"
)
```

**Note:** Instance must be in `stopped` state before resize.

### Flow G: Snapshot Management

**List snapshots:**

```bash
ctyun --output json ecs list-snapshots \
  --region-id {{user.region_id}} \
  --instance-id {{user.instance_id}} \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(10)}}
```

**Get snapshot details:**

```bash
ctyun --output json ecs get-snapshot-details \
  --region-id {{user.region_id}} \
  --snapshot-id {{user.snapshot_id}}
```

### Flow H: Key Pair Management

**List key pairs:**

```bash
ctyun --output json ecs list-keypairs \
  --region-id {{user.region_id}} \
  --page {{user.page_no|default(1)}}
```

### Flow I: Create Image from Instance

**CLI path (primary):**

```bash
ctyun --output json ecs create-image {{user.instance_id}} \
  --name {{user.image_name}} \
  --description "{{user.image_description|default('')}}"
```

### Flow J: List Available Flavors

**CLI path (primary):**

```bash
ctyun --output json ecs flavor-options --region-id {{user.region_id}}
```

**SDK fallback:**

```python
client = ECSClient(...)
client.query_flavor_options()
```

### Flow K: Async Job Query

**Query single job:**

```bash
ctyun --output json ecs query-async-result \
  --region-id {{user.region_id}} \
  --job-id {{user.job_id}}
```

**Query multiple jobs:**

```bash
ctyun --output json ecs query-jobs \
  --region-id {{user.region_id}} \
  --job-ids "{{user.job_ids}}"
```

### Flow L: Connect via CloudShell

CloudShell provides a web-based terminal connection to ECS instances without
requiring SSH keys or public IP addresses. Useful for:
- Quick troubleshooting when SSH is unavailable
- Accessing instances in private subnets
- Emergency access when key pairs are lost

**CLI path (primary):**

```bash
ctyun --output json ecs cloudshell {{user.instance_id}} \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
client = ECSClient(...)
result = client.get_instance_cloudshell(
    instance_id="{{user.instance_id}}",
    region_id="{{user.region_id}}"
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj.consoleUrl` for
the CloudShell access URL. URL typically expires in 5 minutes.

**Output:**
```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": {
    "consoleUrl": "https://cloudshell.ctyun.cn/vnc/...",
    "expireTime": "2026-06-05T12:00:00Z"
  }
}
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
