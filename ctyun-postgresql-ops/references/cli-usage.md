# CTyun PostgreSQL CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support PostgreSQL data operations.** The `ctyun-cli`
> has no PostgreSQL or SQL-related subcommands. PostgreSQL data-level operations
> are performed via the standard `psql` CLI client.

## Standard PostgreSQL CLI (`psql`)

### Installation

```bash
# macOS
brew install postgresql-client

# Ubuntu/Debian
apt-get install postgresql-client

# Verify
psql --version
```

### Connection

Connect to a CTyun RDS PostgreSQL instance:

```bash
# Using PGPASSWORD environment variable (recommended)
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}"

# One-shot query (machine-readable output)
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -A -t -F $'\t' -c "{{user.query}}"
```

### Common Operations

```bash
# List databases
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -l -A -t

# List tables in schema
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -c "\dt {{user.schema}}.*"

# Describe table
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -c "\d+ {{user.table}}"

# Execute SQL file
PGPASSWORD="{{user.password}}" psql -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -f "{{user.sql_file}}"
```

### Backup & Restore

```bash
# pg_dump single database (custom format)
PGPASSWORD="{{user.password}}" pg_dump -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  -F c -f "{{user.backup_file}}"

# pg_dump plain SQL format
PGPASSWORD="{{user.password}}" pg_dump -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" > "{{user.sql_file}}"

# pg_restore from custom format
PGPASSWORD="{{user.password}}" pg_restore -h "{{user.host}}" -p "{{user.port}}" \
  -U "{{user.username}}" -d "{{user.database}}" \
  "{{user.backup_file}}"
```
