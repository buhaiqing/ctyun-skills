# CTyun MySQL CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support MySQL data operations.** The `ctyun-cli`
> has no MySQL or SQL-related subcommands. MySQL data-level operations
> are performed via the standard `mysql` CLI client.

## Standard MySQL CLI (`mysql`)

### Installation

```bash
# macOS
brew install mysql-client

# Ubuntu/Debian
apt-get install mysql-client

# Verify
mysql --version
```

### Connection

Connect to a CTyun RDS MySQL instance:

```bash
# Method 1: Password on command line (simple, less secure)
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}"

# Method 2: defaults-extra-file (recommended, more secure)
# Create a temp config file
printf '[client]\npassword=%s' "{{user.password}}" > /tmp/mysql.cnf
mysql --defaults-extra-file=/tmp/mysql.cnf \
  -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" "{{user.database}}"
rm /tmp/mysql.cnf
```

### Common Operations

```bash
# Show databases
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" -e "SHOW DATABASES;"

# Show tables
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" -e "SHOW TABLES;"

# Describe table
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" -e "DESCRIBE {{user.table}};"

# Execute query
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" -e "{{user.query}}"

# Import SQL file
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" < "{{user.sql_file}}"
```

### Backup & Restore

```bash
# mysqldump single database
mysqldump -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" > "{{user.backup_file}}"

# Restore from dump
mysql -h "{{user.host}}" -P "{{user.port}}" -u "{{user.username}}" \
  -p"{{user.password}}" "{{user.database}}" < "{{user.backup_file}}"
```
