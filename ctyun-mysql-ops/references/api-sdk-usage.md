# MySQL API / SDK Usage

## Overview

CTyun MySQL data operations do not use a cloud-specific SDK or API.
All operations use the **standard MySQL CLI** (`mysql`, `mysqldump`)
via subprocess. There is no CTyun-specific Python SDK for MySQL.

## Connection Methods

### Option 1: MySQL CLI (recommended)

```bash
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" -e "{{user.query}}"
```

### Option 2: Python mysql-connector-python (alternative)

```bash
pip install mysql-connector-python
```

```python
import mysql.connector

conn = mysql.connector.connect(
    host="{{user.host}}",
    port={{user.port}},
    user="{{user.username}}",
    password="{{user.password}}",
    database="{{user.database}}"
)
cursor = conn.cursor()
cursor.execute("{{user.query}}")
for row in cursor.fetchall():
    print(row)
cursor.close()
conn.close()
```

### Option 3: Python PyMySQL (alternative)

```bash
pip install pymysql
```

```python
import pymysql

conn = pymysql.connect(
    host="{{user.host}}",
    port={{user.port}},
    user="{{user.username}}",
    password="{{user.password}}",
    database="{{user.database}}"
)
cursor = conn.cursor()
cursor.execute("{{user.query}}")
print(cursor.fetchall())
```

## When to Use Each Method

| Method | Use Case |
|---|---|
| `mysql` CLI | Quick queries, DDL, DML, script execution |
| `mysqldump` | Database backup (single DB) |
| `mysql-connector-python` | Programmatic Python access, complex transactions |
| `PyMySQL` | Lightweight Python MySQL access |

## RDS Instance Connection Info

MySQL instances managed by CTyun RDS provide connection information via
the RDS console or API (see [`../../ctyun-rds-ops/`](../../ctyun-rds-ops/) for
instance management). Key connection parameters:

- **Host**: RDS instance endpoint (e.g., `rds-xxx.ctrds.ctyun.cn`)
- **Port**: 3306
- **Username**: Set at instance creation
- **Password**: Set at instance creation (can be reset)
- **Default database**: `mysql` (admin database)
