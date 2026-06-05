# CTyun ELB CLI Usage

> Source of truth: `ctyun elb --help`.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.7.7`.
>
> ELB CLI support includes 7+ commands across load balancer management,
> target groups, backend servers, health checks, and monitoring.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json elb loadbalancer list` |
| `--output yaml` | Before subcommand | `ctyun --output json elb targetgroup get ...` |

## ELB Commands

### `elb loadbalancer list` — List load balancers

```bash
ctyun --output json elb loadbalancer list \
  --region-id <region>
```

Output fields: `loadBalancerId, loadBalancerName, loadBalancerStatus, address, vpcId, subnetId, createTime`

### `elb loadbalancer get` — Describe a load balancer

```bash
ctyun --output json elb loadbalancer get \
  --region-id <region> \
  --loadbalancer-id <lb_id>
```

Output fields: `loadBalancerId, loadBalancerName, loadBalancerStatus, address, vpcId, subnetId, listenerIds[], createTime`

### `elb targetgroup list` — List target groups

```bash
ctyun --output json elb targetgroup list \
  --region-id <region>
```

Output fields: `targetGroupId, targetGroupName, protocol, healthCheckProtocol`

### `elb targetgroup get` — Describe a target group

```bash
ctyun --output json elb targetgroup get \
  --region-id <region> \
  --targetgroup-id <tg_id>
```

Output fields: `targetGroupId, targetGroupName, protocol, healthCheckProtocol, healthCheckPort, targets[]`

### `elb targetgroup targets list` — List backend servers in a target group

```bash
ctyun --output json elb targetgroup targets list \
  --region-id <region> \
  --targetgroup-id <tg_id>
```

Output fields: `targetId, targetIp, port, weight, healthStatus`

### `elb targetgroup targets show` — Show backend server details

```bash
ctyun --output json elb targetgroup targets show \
  --region-id <region> \
  --targetgroup-id <tg_id> \
  --target-id <target_id>
```

Output fields: `targetId, targetIp, port, weight, healthStatus, healthStatusReason`

### `elb health-check show` — View health check details

```bash
ctyun --output json elb health-check show \
  --region-id <region> \
  --health-check-id <hc_id>
```

Output fields: `healthCheckId, protocol, port, interval, timeout, healthyThreshold, unhealthyThreshold`

### `elb monitor realtime` — Query real-time monitoring data

```bash
ctyun --output json elb monitor realtime \
  --region-id <region> \
  --device-ids "<device_id_1>,<device_id_2>"
```

### `elb monitor history` — Query historical monitoring data

```bash
ctyun --output json elb monitor history \
  --region-id <region> \
  --device-ids "<device_ids>" \
  --metric-names "<metric_names>" \
  --start-time "2025-01-01 00:00:00" \
  --end-time "2025-01-02 00:00:00"
```

## Output Format

All commands support `--output table` (default), `--output json`, and `--output yaml`.

```bash
ctyun --output json elb loadbalancer list --region-id <region>
ctyun --output yaml elb targetgroup get --region-id <region> --targetgroup-id <id>
ctyun --output table elb targetgroup targets list --region-id <region> --targetgroup-id <id>
```
