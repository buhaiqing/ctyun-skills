# MySQL Integration Guide

## CTyun Service Integration

### RDS + MySQL

CTyun RDS MySQL instances are the primary platform for MySQL operations.
The `ctyun-rds-ops` skill manages instance infrastructure (create, delete,
resize), while this skill handles data-level operations.

**Typical workflow:**
1. Create RDS MySQL instance via `ctyun-rds-ops`
2. Configure security group for client access
3. Connect via `mysql` CLI and execute SQL operations

### Application Integration

**Common application stacks on CTyun ECS:**
- **Java** — Connector/J JDBC driver
- **Python** — mysql-connector-python / PyMySQL
- **PHP** — mysqli / PDO_MySQL
- **Node.js** — mysql2 / sequelize
- **Go** — go-sql-driver/mysql / GORM

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-rds-ops` | Provision/manage RDS MySQL instances |
| `ctyun-ecs-ops` | Application servers running MySQL clients |
| `ctyun-cloudmonitor-ops` | MySQL monitoring via Cloud Monitor |
| `ctyun-postgresql-ops` | Similar workflow for PostgreSQL databases |
