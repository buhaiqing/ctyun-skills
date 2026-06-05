---
name: ctyun-postgresql-ops
version: 1.0.0
description: >
  Execute PostgreSQL data-level operations — SQL queries, DDL/DML,
  schema management, user and privilege management, backup/restore
  against CTyun RDS PostgreSQL instances.
  NOT for instance infrastructure (delegate to ctyun-rds-ops).
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  tool_psql_client: psql
  lifecycle: shipped
---

# ctyun-postgresql-ops

## Trigger & Scope

### SHOULD Use

- Execute SQL queries against a PostgreSQL database
- Create, alter, or drop database tables and schemas
- Insert, update, delete, or select data
- Manage PostgreSQL roles and privileges
- Show database schema, tables, indexes, sequences
- Analyze query performance with EXPLAIN ANALYZE
- Backup/restore a single database via pg_dump / pg_restore
- Configure PostgreSQL session parameters
- Create and manage indexes, views, functions

### SHOULD NOT Use

- RDS instance lifecycle (create/delete/resize RDS) → delegate to `ctyun-rds-ops`
- MySQL data-level operations → delegate to `ctyun-mysql-ops`
- MongoDB data-level operations → delegate to `ctyun-mongodb-ops`
- Instance-level monitoring or alerting → delegate to `ctyun-cloudmonitor-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks "connect to PostgreSQL", "run query", "psql", "SELECT" | Route here |
| User asks "create RDS instance", "delete RDS" | Route to `ctyun-rds-ops` |
| User asks "MySQL query" or "mysql" | Route to `ctyun-mysql-ops` |
| User asks "MongoDB" or "mongosh" | Route to `ctyun-mongodb-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{user.host}}` | Ask once, cache per session | PostgreSQL hostname or IP |
| `{{user.port}}` | Ask once, cache per session | `5432` |
| `{{user.database}}` | Ask once, cache per session | database name |
| `{{user.username}}` | Ask once, cache per session | PostgreSQL role |
| `{{user.password}}` | Ask once, cache per session | PostgreSQL password (never log) |
| `{{user.table}}` | Ask once, cache per session | table name |
| `{{user.schema}}` | Ask once, cache per session | schema name (default: `public`) |
| `{{output.query_result}}` | Parsed from CLI stdout | query rows |

---

## Execution Flows

All operations use the **`psql` CLI** via subprocess (sdk-only policy;
no CTyun CLI module exists for PostgreSQL data operations).

### Pre-flight

1. Verify `psql` client installed: `psql --version`
2. Verify connectivity:

   ```bash
   PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
     -U "{{user.username}}" -d "{{user.database}}" -c "SELECT 1"
   ```

> **Security:** Use `PGPASSWORD` environment variable or `.pgpass` file.
> Never pass password directly in connection string when avoidable.

### Flow A: Execute SQL Query

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -c "{{user.query}}"
```

**Output Parsing:** psql with `-c` returns aligned text. Use `-A -t -F $'\t'`
for tab-separated machine-readable output, then parse via CSV DictReader.

### Flow B: Import SQL File

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -f "{{user.sql_file}}"
```

### Flow C: List Databases

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -l -A -t
```

### Flow D: Create Database

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d postgres \
  -c "CREATE DATABASE {{user.database}} WITH ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';"
```

### Flow E: DROP DATABASE (Destructive)

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d postgres \
  -c "DROP DATABASE IF EXISTS {{user.database}};"
```

> **Safety Gate:** IRREVERSIBLE. Require explicit user confirmation.
> "Are you sure you want to DROP DATABASE `{{user.database}}`? All schemas, tables, and data will be permanently deleted."

### Flow F: Create Role / Grant Privileges

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d postgres \
  -c "CREATE ROLE {{user.new_role}} WITH LOGIN PASSWORD '{{user.new_role_password}}';"
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -c "GRANT ALL PRIVILEGES ON DATABASE {{user.database}} TO {{user.new_role}};"
```

### Flow G: Backup Single Database (pg_dump)

```bash
PGPASSWORD="{{user.password}}" pg_dump -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -F c -f "{{user.backup_file}}"
```

### Flow H: Restore from Backup

```bash
PGPASSWORD="{{user.password}}" pg_restore -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  "{{user.backup_file}}"
```

---

## Output Parsing Rules

| Operation | Parse Method | Key Fields |
|---|---|---|
| SELECT query | `-A -t -F $'\t'` TSV → CSV DictReader | Column headers + rows |
| `\l` (list databases) | `-l -A -t` → lines | Database names |
| `\dt` (list tables) | `-c "\dt" -A -t` | Schema, Table, Type columns |
| `\d+ table` (describe) | `-c "\d+ {{user.table}}"` | Column info, indexes |
| EXPLAIN ANALYZE | Text parsing | Plan, cost, timing |
| pg_dump | Custom format `.dump` file | Restore via pg_restore |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `could not connect to server` | Runtime | 1x | Check host/port, network |
| `FATAL: password authentication failed` | Environment | 1x | Verify credentials |
| `FATAL: database "..." does not exist` | Business | No | Verify database name |
| `ERROR: relation "..." does not exist` | Business | No | Verify table/schema name |
| `ERROR: syntax error at or near` | Business | No | Fix SQL syntax |
| `ERROR: permission denied` | Business | No | Insufficient privileges |
| `psql: command not found` | Environment | 1x | Install postgresql-client |
| `ERROR: duplicate key` | Business | No | Check for existing data |
| Timeout (>30s) | Runtime | 1x | Check query perf; add LIMIT |

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
| 1.0.0 | 2026-06-05 | Initial ctyun-postgresql-ops skill — SQL queries, DDL, DML, role management via psql CLI |
