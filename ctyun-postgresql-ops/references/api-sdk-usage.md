# PostgreSQL API / SDK Usage

## Overview

CTyun PostgreSQL data operations do not use a cloud-specific SDK or API.
All operations use the **standard PostgreSQL CLI** (`psql`, `pg_dump`,
`pg_restore`) via subprocess. There is no CTyun-specific Python SDK for
PostgreSQL.

## Connection Methods

### Option 1: psql CLI (recommended)

```bash
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -A -t -F $'\t' -c "{{user.query}}"
```

### Option 2: Python psycopg2 (alternative)

```bash
pip install psycopg2-binary
```

```python
import psycopg2

conn = psycopg2.connect(
    host="{{user.host}}",
    port={{user.port}},
    user="{{user.username}}",
    password="{{user.password}}",
    dbname="{{user.database}}"
)
cursor = conn.cursor()
cursor.execute("{{user.query}}")
for row in cursor.fetchall():
    print(row)
cursor.close()
conn.close()
```

### Option 3: SQLAlchemy (ORM access)

```bash
pip install sqlalchemy psycopg2-binary
```

```python
from sqlalchemy import create_engine, text

engine = create_engine(
    f"postgresql://{{user.username}}:{{user.password}}@{{user.host}}:{{user.port}}/{{user.database}}"
)
with engine.connect() as conn:
    result = conn.execute(text("{{user.query}}"))
    for row in result:
        print(row)
```

## When to Use Each Method

| Method | Use Case |
|---|---|
| `psql` CLI | Quick queries, DDL, DML, \d commands |
| `pg_dump` / `pg_restore` | Database backup and restore |
| `psycopg2` | Programmatic Python access, transactions |
| `SQLAlchemy` | ORM-based access, connection pooling |

## RDS Instance Connection Info

PostgreSQL instances managed by CTyun RDS provide connection information via
the RDS console or API (see [`../../ctyun-rds-ops/`](../../ctyun-rds-ops/) for
instance management). Key connection parameters:

- **Host**: RDS instance endpoint (e.g., `rds-xxx.ctrds.ctyun.cn`)
- **Port**: 5432
- **Username**: Set at instance creation
- **Password**: Set at instance creation (can be reset)
- **Default database**: `postgres` (admin database)
