---
name: ctyun-mysql-ops
version: 1.0.0
description: >
  Execute MySQL data-level operations — DDL (ALTER/CREATE/DROP TABLE),
  DML (SELECT/INSERT/UPDATE/DELETE), user and privilege management,
  and query execution against CTyun RDS MySQL instances.
  NOT for instance infrastructure (delegate to ctyun-rds-ops).
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  tool_mysql_client: mysql
  lifecycle: shipped
---

# ctyun-mysql-ops

## Trigger & Scope

### SHOULD Use

- Execute SQL queries against a MySQL database
- Create, alter, or drop database tables
- Insert, update, delete, or select data
- Manage MySQL users and privileges (CREATE USER, GRANT, REVOKE)
- Show database schema, tables, indexes
- Monitor MySQL performance (SHOW PROCESSLIST, EXPLAIN, slow query analysis)
- Backup/restore a single database via mysqldump
- Optimize MySQL queries and table maintenance (OPTIMIZE TABLE, ANALYZE TABLE)
- Configure MySQL session or global variables

### SHOULD NOT Use

- RDS instance lifecycle (create/delete/resize RDS) → delegate to `ctyun-rds-ops`
- PostgreSQL data-level operations → delegate to `ctyun-postgresql-ops`
- MongoDB data-level operations → delegate to `ctyun-mongodb-ops`
- Instance-level monitoring or alerting → delegate to `ctyun-cloudmonitor-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks "connect to MySQL", "run query", "DROP TABLE", "SELECT" | Route here |
| User asks "create RDS instance", "delete RDS", "resize MySQL" | Route to `ctyun-rds-ops` |
| User asks "PostgreSQL query" or "psql" | Route to `ctyun-postgresql-ops` |
| User asks "MongoDB query" or "mongosh" | Route to `ctyun-mongodb-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{user.host}}` | Ask once, cache per session | MySQL hostname or IP |
| `{{user.port}}` | Ask once, cache per session | `3306` |
| `{{user.database}}` | Ask once, cache per session | database name |
| `{{user.username}}` | Ask once, cache per session | MySQL user |
| `{{user.password}}` | Ask once, cache per session | MySQL password (never log) |
| `{{user.table}}` | Ask once, cache per session | table name |
| `{{output.query_result}}` | Parsed from CLI stdout | query rows |

---

## Execution Flows

All operations use the **`mysql` CLI** via subprocess (sdk-only policy;
no CTyun CLI module exists for MySQL data operations).

### Pre-flight

1. Verify `mysql` client installed: `mysql --version`
2. Verify connectivity: `mysql -h {{user.host}} -P {{user.port}} -u {{user.username}} -p{{user.password}} -e "SELECT 1"`

> **Security:** Never pass password on command line if the environment
> supports secure alternatives (e.g., `MYSQL_PWD` env var, or `--defaults-extra-file`).
> Prefer `--defaults-extra-file=<(printf '[client]\npassword=%s' "$MYSQL_PWD")`

### Flow A: Execute SQL Query

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" \
  -e "{{user.query}}"
```

**Output Parsing:** The mysql CLI returns tab-separated output with a header
row. Parse via Python `csv.DictReader` with delimiter `\t`.

### Flow B: Import SQL File

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" < "{{user.sql_file}}"
```

### Flow C: Show Databases

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" -e "SHOW DATABASES;"
```

### Flow D: Create Database

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" -e "CREATE DATABASE IF NOT EXISTS {{user.database}} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Flow E: DROP DATABASE (Destructive)

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" -e "DROP DATABASE IF EXISTS {{user.database}};"
```

> **Safety Gate:** IRREVERSIBLE. Require explicit user confirmation.
> "Are you sure you want to DROP DATABASE `{{user.database}}`? All tables and data will be permanently deleted."

### Flow F: Create User / Grant Privileges

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" -e "
CREATE USER IF NOT EXISTS '{{user.new_user}}'@'{{user.new_user_host}}' IDENTIFIED BY '{{user.new_user_password}}';
GRANT {{user.privileges}} ON {{user.database}}.* TO '{{user.new_user}}'@'{{user.new_user_host}}';
FLUSH PRIVILEGES;
"
```

### Flow G: Backup Single Database (mysqldump)

```bash
mysqldump -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" > "{{user.backup_file}}"
```

---

## Output Parsing Rules

| Operation | Parse Method | Key Fields |
|---|---|---|
| SELECT query | Tab-separated stdout → CSV DictReader | Column headers + rows |
| SHOW DATABASES | TSV → column 1 | Database names |
| SHOW TABLES | TSV → column 1 | Table names |
| DESCRIBE TABLE | TSV with header `Field,Type,Null,Key,Default,Extra` | Schema definition |
| mysqldump | Raw SQL file | SQL statements |
| DDL (CREATE/ALTER/DROP) | `ROW_COUNT()` → "0 rows affected" | success/failure message |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `ERROR 2003 (HY000)` | Runtime | 1x | Check host/port, network connectivity |
| `ERROR 1045 (28000)` | Environment | 1x | Verify username/password |
| `ERROR 1049 (42000)` | Business | No | Database doesn't exist, verify name |
| `ERROR 1146 (42S02)` | Business | No | Table doesn't exist, verify table name |
| `ERROR 1064 (42000)` | Business | No | SQL syntax error, fix query |
| `ERROR 1142 (42000)` | Business | No | Insufficient privileges |
| `mysql: command not found` | Environment | 1x | Install mysql client |
| Timeout (>30s) | Runtime | 1x | Check query performance; consider `LIMIT` |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | DROP TABLE/DATABASE causes data loss |
| `max_iterations` | `2` | inherited from §8 default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for DROP/DELETE/TRUNCATE operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-mysql-ops skill — SQL queries, DDL, DML, user management via mysql CLI |
