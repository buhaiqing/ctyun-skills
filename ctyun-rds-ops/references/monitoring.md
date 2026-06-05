# RDS Monitoring

## Cloud Monitor Metrics

CTyun Cloud Monitor collects the following RDS metrics:

| Metric | Description | Unit |
|---|---|---|
| `cpu_util` | CPU usage | % |
| `memory_util` | Memory usage | % |
| `disk_util` | Disk usage | % |
| `disk_iops_read` | Disk read IOPS | count/s |
| `disk_iops_write` | Disk write IOPS | count/s |
| `network_in_rate` | Network inbound rate | bps |
| `network_out_rate` | Network outbound rate | bps |
| `connection_count` | Active connections | count |
| `slow_query_count` | Queries exceeding slow_query_log_time | count/min |

## Querying Metrics

Metrics can be retrieved via Cloud Monitor API (see `ctyun-cloudmonitor-ops`).

## Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| CPU | > 80% for 5 min | > 95% for 5 min | Scale up or optimize queries |
| Memory | > 80% for 5 min | > 95% for 5 min | Scale up or tune memory params |
| Disk | > 80% | > 90% | Increase storage or clean data |
| Connections | > 80% of max | > 95% of max | Add connection pooling |
| Slow queries | > 50/min | > 200/min | Optimize queries, add indexes |
