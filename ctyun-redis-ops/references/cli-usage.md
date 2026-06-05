# CTyun Redis CLI Usage

> Source of truth: `ctyun redis --help`.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.14.0`.
>
> Redis CLI support includes 14+ commands across instance lifecycle, backup,
> network configuration, performance monitoring, and topology inspection.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json redis list-instances` |
| `--output yaml` | Before subcommand | `ctyun --output json redis get-instance ...` |

> The CTyun CLI does NOT support `--no-interactive`. Destructive operations
> are guarded by application-level safety gates (see SKILL.md).

## Redis Commands

### `redis list-instances` — List Redis instances

```bash
ctyun --output json redis list-instances \
  [--region-id <region>] \
  [--page <page_no>] \
  [--page-size <page_size>]
```

Output fields: `instanceId, instanceName, engineVersion, edition, status, zoneName, createTime`

### `redis get-instance` — Describe a single Redis instance

```bash
ctyun --output json redis get-instance \
  --region-id <region> \
  --instance-id <instance_id>
```

Output fields: `instanceId, instanceName, engineVersion, edition, shardMemSize, vpcId, subnetId, securityGroupId, status, connectionDomain, port, createTime`

### `redis create-instance` — Create a Redis instance

```bash
ctyun --output json redis create-instance \
  --instance-name <name> \
  --edition <edition> \
  --engine-version <version> \
  --shard-mem-size <size_gb> \
  --zone-name <zone> \
  --vpc-id <vpc_id> \
  --subnet-id <subnet_id> \
  --secgroups <sg_id> \
  --password <password> \
  [--dry-run]
```

Supported editions: `StandardSingle`, `StandardCluster`, `DistributedCluster`
Engine versions: `4.0`, `5.0`, `6.0`, `7.0`

> `--dry-run` validates parameters without actually creating the instance.

### `redis delete-instance` — Delete a Redis instance

```bash
ctyun --output json redis delete-instance \
  --region-id <region> \
  --instance-id <instance_id>
```

> **Warning:** This operation is IRREVERSIBLE. Data will be permanently deleted.

### `redis create-backup` — Create a manual backup

```bash
ctyun --output json redis create-backup \
  --region-id <region> \
  --instance-id <instance_id> \
  --backup-name <name> \
  [--backup-mode <mode>]
```

### `redis list-network-configs` — List network configurations

```bash
ctyun --output json redis list-network-configs \
  --region-id <region> \
  --instance-id <instance_id>
```

Output fields: `vpcId, subnetId, securityGroupId, networkType`

### `redis get-instance-metrics` — Get instance performance metrics

```bash
ctyun --output json redis get-instance-metrics \
  --region-id <region> \
  --instance-id <instance_id> \
  [--metric <metric_name>] \
  [--start-time <time>] \
  [--end-time <time>]
```

### `redis check-resources` — Check available resource specifications

```bash
ctyun --output json redis check-resources \
  --region-id <region> \
  [--edition <edition>] \
  [--engine-version <version>]
```

### `redis zones` — Query available zones

```bash
ctyun --output json redis zones \
  --region-id <region>
```

### `redis topology` — View instance logical topology

```bash
ctyun --output json redis topology \
  --region-id <region> \
  --instance-id <instance_id>
```

### `redis cluster-nodes` — Query cluster nodes

```bash
ctyun --output json redis cluster-nodes \
  --region-id <region> \
  --instance-id <instance_id>
```

## Output Format

All commands support `--output table` (default), `--output json`, and `--output yaml`.

```bash
ctyun --output json redis list-instances
ctyun --output yaml redis get-instance --region-id <region> --instance-id <id>
ctyun --output table redis check-resources --region-id <region>
```
