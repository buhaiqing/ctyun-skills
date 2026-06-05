# ECS Monitoring

## Available Metrics

CTyun Cloud Monitor collects the following metrics for ECS instances.
Full alarm rule configuration is delegated to `ctyun-cloudmonitor-ops`.

### Basic Metrics

| Metric | Description | Unit | Granularity |
|---|---|---|---|
| `cpu_util` | CPU usage | Percent (%) | 1 min / 5 min |
| `cpu_iowait` | CPU I/O wait | Percent (%) | 5 min |
| `mem_util` | Memory usage | Percent (%) | 1 min / 5 min |
| `mem_used` | Used memory | MB | 5 min |
| `disk_read_bytes` | Disk read throughput | Bytes/s | 1 min / 5 min |
| `disk_write_bytes` | Disk write throughput | Bytes/s | 1 min / 5 min |
| `disk_read_iops` | Disk read IOPS | Count/s | 1 min / 5 min |
| `disk_write_iops` | Disk write IOPS | Count/s | 1 min / 5 min |
| `network_in` | Inbound network traffic | Bytes/s | 1 min / 5 min |
| `network_out` | Outbound network traffic | Bytes/s | 1 min / 5 min |
| `net_packet_in` | Inbound packets | Count/s | 5 min |
| `net_packet_out` | Outbound packets | Count/s | 5 min |

### GPU Metrics (GPU instances only)

| Metric | Description | Unit |
|---|---|---|
| `gpu_util` | GPU utilization | Percent (%) |
| `gpu_mem_util` | GPU memory utilization | Percent (%) |
| `gpu_temp` | GPU temperature | Celsius |

## Querying Metrics

**Via ECS monitoring command:**

```bash
ctyun ecs monitoring <instance_id> <metric_name> <start_time> <end_time> \
  --period 300
```

Parameters:
- `metric_name`: One of the metric names above
- `start_time` / `end_time`: Format `YYYY-MM-DD HH:mm:ss`
- `period`: Aggregation period in seconds (300 = 5 minutes)

**Via Cloud Monitor (delegated):**

For alarm rules, dashboards, and historical trend analysis, delegate to
`ctyun-cloudmonitor-ops`.

## Health Indicators

| Indicator | Healthy | Warning | Critical |
|---|---|---|---|
| `cpu_util` | < 70% | 70–90% | > 90% |
| `mem_util` | < 70% | 70–85% | > 85% |
| `disk_read_iops` | Below instance type limit | > 80% of limit | > 95% of limit |
| `disk_write_iops` | Below instance type limit | > 80% of limit | > 95% of limit |
| `network_in/out` | Below bandwidth limit | > 80% of limit | > 95% of limit |

## Instance Status Monitoring

The instance's lifecycle state (`running`, `stopped`, `starting`, `stopping`)
can be monitored via `ecs list` or `ecs details`. For real-time alerting
on state transitions, delegate to `ctyun-cloudmonitor-ops` for event-based
alarm rules.
