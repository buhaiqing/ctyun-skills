# RDS Integration Guide

## CTyun Service Integration

### ECS + RDS

Applications running on CTyun ECS can connect to RDS instances within the
same VPC for low-latency database access.

**Setup:**
1. Deploy RDS instance in VPC `{{user.vpc_id}}`
2. Configure security group to allow ECS subnet traffic on port 3306/5432/1433
3. Connect from ECS using the RDS instance endpoint

### Cloud Monitor + RDS

Monitor RDS instance metrics via CTyun Cloud Monitor.

**Key metrics:**
- CPU utilization
- Memory usage
- Disk IOPS and throughput
- Connection count
- Slow query count

See [monitoring.md](monitoring.md) for details.

### RDS + MySQL/PostgreSQL Tools

RDS instances can be managed via standard database tools:
- **mysql CLI** / **psql CLI** — direct SQL access
- **mysqldump** / **pg_dump** — backup/restore
- **DBeaver**, **DataGrip**, **Navicat** — GUI tools

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-mysql-ops` | SQL operations on RDS MySQL instances |
| `ctyun-postgresql-ops` | SQL operations on RDS PostgreSQL instances |
| `ctyun-cloudmonitor-ops` | RDS instance monitoring and alarm rules |
| `ctyun-ecs-ops` | Application servers connecting to RDS |
| `ctyun-vpc-ops` (planned) | Network configuration for RDS access |
