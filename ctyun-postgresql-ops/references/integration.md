# PostgreSQL Integration Guide

## CTyun Service Integration

### RDS + PostgreSQL

CTyun RDS PostgreSQL instances are the primary platform for PostgreSQL
operations. The `ctyun-rds-ops` skill manages instance infrastructure,
while this skill handles data-level operations.

**Typical workflow:**
1. Create RDS PostgreSQL instance via `ctyun-rds-ops`
2. Configure security group for client access
3. Connect via `psql` CLI and execute SQL operations

### Application Integration

**Common application stacks on CTyun ECS:**
- **Python** — psycopg2 / SQLAlchemy / Django ORM
- **Java** — PostgreSQL JDBC driver
- **Node.js** — node-postgres / pg / Prisma
- **Ruby** — pg gem / ActiveRecord
- **Go** — pgx / GORM
- **Rust** — sqlx / diesel

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-rds-ops` | Provision/manage RDS PostgreSQL instances |
| `ctyun-ecs-ops` | Application servers running psql clients |
| `ctyun-cloudmonitor-ops` | PostgreSQL monitoring via Cloud Monitor |
| `ctyun-mysql-ops` | Similar workflow for MySQL databases |
