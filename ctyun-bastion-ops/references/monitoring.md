# Cloud Bastion Host Monitoring & Observability

## Available Metrics

| Metric | Description | Source |
|---|---|---|
| CPU Utilization | Bastion ECS CPU usage | ECS Metrics |
| Memory Utilization | Bastion ECS memory usage | ECS Metrics |
| Disk Utilization | Bastion ECS disk usage | ECS Metrics |
| Network In/Out | Network throughput | ECS Metrics |
| Active Sessions | Current concurrent user sessions | Bastion API |
| User Login Count | Number of user logins in time period | Bastion API |

## Cloud Monitor Integration

Bastion host metrics can be monitored through `ctyun-cloudmonitor-ops`. Since the bastion is an ECS instance, standard ECS monitoring applies:

| Metric | Alarm Suggestion |
|---|---|
| CPU > 80% for 5 min | Consider spec upgrade |
| Memory > 85% for 5 min | Consider spec upgrade |
| Disk > 85% | Clean up logs or expand storage |
| Instance STOPPED state | Investigate immediately |

## Operational Recommendations

| Check | Frequency | Action |
|---|---|---|
| Instance status | Daily | Verify all bastion instances are RUNNING |
| CPU/memory usage | Weekly | Plan for capacity if trending up |
| Active user count | Weekly | Verify against expected usage |
| Review access logs | Monthly | Audit for unusual access patterns |
| Check host asset list | Monthly | Remove orphaned hosts |
| Verify user access | Quarterly | Remove inactive users |