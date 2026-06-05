# ctyun ECS CLI Usage

> Source of truth: `ctyun ecs --help` and `ctyun-cli` v1.20.2.
> The market CLI tool is installed via `pip install ctyun-cli` and exposes the `ctyun` command.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json ecs list ...` (NOT `ctyun ecs list --output json`) |
| `--output yaml` | Before subcommand | `ctyun --output yaml ecs details ...` |

Individual commands MAY accept a local `--output` flag for per-command format control. When both global and local `--output` are present, the local flag wins.

> The CTyun CLI does NOT support `--no-interactive`. Delete/power-off confirmations are handled via application-level safety gates (see SKILL.md).

---

## ECS Commands

### `ecs list` — List instances

```bash
ctyun --output json ecs list \
  --region-id <region_id> \
  [--page <page_no>] \
  [--page-size <page_size>] \
  [--az-name <az_name>] \
  [--state <instance_state>]
```

Output fields: `instanceID, displayName, instanceStatus, privateIP[], flavorName, imageName, expireTime`

### `ecs details <instance_id>` — Get instance details

```bash
ctyun --output json ecs details <instance_id> \
  --region-id <region_id>
```

Output fields: `instanceID, displayName, instanceStatusStr, regionID, azName, flavorName, imageName, privateIP[], eipAddress[], vpcName, subnetName, createTime, expireTime`

### `ecs create` — Create instance

```bash
ctyun --output json ecs create \
  --name <instance_name> \
  --instance-type <flavor_id> \
  --image-id <image_id> \
  --region-id <region_id> \
  --system-disk-type <SSD|SAS> \
  --system-disk-size <size_gb> \
  [--vpc-id <vpc_id>] \
  [--subnet-id <subnet_id>] \
  [--security-group-ids <sg_id1,sg_id2>] \
  [--key-name <keypair_name>] \
  [--password <password>] \
  [--count <1..N>]
```

### `ecs start <instance_id>` — Start instance

```bash
ctyun --output json ecs start <instance_id>
```

### `ecs stop <instance_id>` — Stop instance

```bash
ctyun --output json ecs stop <instance_id>
ctyun --output json ecs stop <instance_id> --force   # Force stop
```

### `ecs reboot <instance_id>` — Reboot instance

```bash
ctyun --output json ecs reboot <instance_id>
```

### `ecs delete <instance_id>` — Delete instance

```bash
ctyun --output json ecs delete <instance_id> \
  [--delete-disk|--keep-disk] \
  --confirm
```

> `--confirm` is MANDATORY. The safety gate in SKILL.md handles user confirmation before this CLI call.

### `ecs resize <instance_id> <flavor_id>` — Change instance type

```bash
ctyun --output json ecs resize <instance_id> <new_flavor_id>
```

### `ecs flavor-options` — List available flavors

```bash
ctyun --output json ecs flavor-options --region-id <region_id>
```

Output: `flavorNameScope[], flavorCPUScope[], flavorRAMScope[], flavorFamilyScope[]`

### `ecs instance-types` — List instance types

```bash
ctyun ecs instance-types
```

### `ecs list-snapshots` — List instance snapshots

```bash
ctyun --output json ecs list-snapshots \
  --region-id <region_id> \
  [--page <page_no>] \
  [--page-size <page_size>] \
  [--instance-id <instance_id>] \
  [--snapshot-status <status>] \
  [--snapshot-id <snapshot_id>]
```

### `ecs get-snapshot-details` — Get snapshot details

```bash
ctyun --output json ecs get-snapshot-details \
  --region-id <region_id> \
  --snapshot-id <snapshot_id>
```

Output: `snapshotID, snapshotName, snapshotStatus, instanceID, azName, members[].diskID`

### `ecs list-keypairs` — List SSH key pairs

```bash
ctyun --output json ecs list-keypairs \
  --region-id <region_id> \
  [--page <page_no>] \
  [--page-size <page_size>] \
  [--keypair-name <name>] \
  [--query-content <keyword>]
```

Output: `keyPairID, keyPairName, fingerPrint, bindInstanceNum, projectID`

### `ecs create-image` — Create custom image from instance

```bash
ctyun --output json ecs create-image <instance_id> \
  --name <image_name> \
  [--description "<description>"]
```

### `ecs get-auto-renew-config` — Query auto-renew configuration

```bash
ctyun --output json ecs get-auto-renew-config \
  --region-id <region_id> \
  --instance-id <instance_id>
```

### `ecs query-dns-record` — Query internal DNS records

```bash
ctyun --output json ecs query-dns-record \
  --region-id <region_id> \
  --instance-id <instance_id>
```

### `ecs query-async-result` — Query async job result

```bash
ctyun --output json ecs query-async-result \
  --region-id <region_id> \
  --job-id <job_id>
```

### `ecs query-jobs` — Query multiple async jobs

```bash
ctyun --output json ecs query-jobs \
  --region-id <region_id> \
  --job-ids "<job_id1,job_id2>"
```

### `ecs resources <region_id>` — Query user resource summary

```bash
ctyun --output json ecs resources <region_id>
```

### `ecs console <instance_id>` — Get VNC console URL

```bash
ctyun ecs console <instance_id>
```

### `ecs cloudshell <instance_id>` — Get CloudShell access URL

CloudShell provides a web-based terminal connection to the instance without
requiring SSH keys or public IP addresses.

```bash
ctyun ecs cloudshell <instance_id> --region-id <region_id>
```

**Example:**

```bash
# Get CloudShell URL for instance
ctyun --output json ecs cloudshell i-abc123 --region-id cn-gz

# Response includes console URL and expiration time
```

**Common Use Cases:**
- Troubleshooting when SSH is unavailable
- Accessing instances in private subnets
- Emergency access when key pairs are lost
- Quick commands without setting up SSH

**Note:** CloudShell URLs typically expire within 5 minutes. Use immediately after generation.

## Batch Operations

```bash
# Batch start
ctyun ecs batch-start <instance_id1> <instance_id2> ...

# Batch stop
ctyun ecs batch-stop <instance_id1> <instance_id2> ...

# Batch delete
ctyun ecs batch-delete <instance_id1> <instance_id2> ... --confirm
```

## Non-Obvious Flags

| Command | Flag | Note |
|---|---|---|
| `create` | `--system-disk-type` | Defaults to `SSD` if omitted |
| `create` | `--password` | Mutually exclusive with `--key-name` |
| `create` | `--count` | Default 1; multiple instances get auto-generated names |
| `stop` | `--force` | Equivalent to hard power-off; data loss risk |
| `delete` | `--delete-disk` (default) | Deletes attached data disks; use `--keep-disk` to preserve |
| `delete` | `--confirm` | Required; script fails without it |
