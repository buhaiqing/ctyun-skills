# MySQL Troubleshooting

## Common Issues

### Cannot connect to MySQL

| Error | Likely Cause | Solution |
|---|---|---|
| `ERROR 2003 (HY000): Can't connect to MySQL server` | Host/port unreachable | Check network, firewall, security group |
| `ERROR 1045 (28000): Access denied` | Wrong username/password | Verify credentials |
| `ERROR 1130 (HY000): Host not allowed` | User not authorized from this host | GRANT access from your IP range |
| `ERROR 2002 (HY000): Can't connect to local server` | MySQL not running locally | Start MySQL service |

### SQL Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `ERROR 1049 (42000): Unknown database` | Database does not exist | CREATE DATABASE or verify name |
| `ERROR 1146 (42S02): Table doesn't exist` | Table not found | Verify table name and database |
| `ERROR 1064 (42000): SQL syntax error` | Invalid SQL | Check SQL syntax near the error position |
| `ERROR 1054 (42S22): Unknown column` | Column does not exist | Verify column names |
| `ERROR 1062 (23000): Duplicate entry` | Duplicate key violation | Check for existing data, use INSERT IGNORE or ON DUPLICATE KEY UPDATE |

### Performance Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Query too slow | Missing index | Add index on columns in WHERE/JOIN |
| High CPU | Full table scans | Add indexes, optimize queries |
| Lock wait timeout | Concurrent DML on same rows | Reduce transaction duration, use row-level locks |
| Too many connections | Application connection leak | Add connection pooling, increase max_connections |

## Recovery

### Lost connection during UPDATE/DELETE

1. Check if query was committed (auto-commit mode)
2. Verify affected rows
3. If uncertain, use SELECT to check before re-executing

### Corrupted table

```sql
CHECK TABLE {{user.table}};
REPAIR TABLE {{user.table}};  -- MyISAM only
```

For InnoDB corruption, restore from backup or use mysqldump/slave.

### Forgotten password

Reset via RDS console (see `ctyun-rds-ops`).
