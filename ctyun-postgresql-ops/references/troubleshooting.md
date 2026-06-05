# PostgreSQL Troubleshooting

## Common Issues

### Cannot connect to PostgreSQL

| Error | Likely Cause | Solution |
|---|---|---|
| `could not connect to server: Connection refused` | PostgreSQL not running or port blocked | Check instance status, security group |
| `FATAL: password authentication failed` | Wrong password | Verify credentials |
| `FATAL: no pg_hba.conf entry` | Host not authorized | Check pg_hba.conf or RDS security settings |
| `FATAL: database "..." does not exist` | Wrong database name | Verify database name |
| `psql: error: connection to server at...: received invalid response` | SSL mismatch | Check SSL settings |

### SQL Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `ERROR: relation "..." does not exist` | Table not found | Check table name, include schema prefix |
| `ERROR: column "..." does not exist` | Wrong column name | Verify column names |
| `ERROR: syntax error at or near "..."` | Invalid SQL | Check SQL syntax |
| `ERROR: duplicate key value violates unique constraint` | Duplicate key | Use ON CONFLICT handling |
| `ERROR: null value in column "..." violates not-null constraint` | Missing required field | Provide value or set default |

### Performance Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Slow queries | Missing index | Create index, use EXPLAIN ANALYZE |
| High CPU/IO | Inefficient query plans | Run ANALYZE, VACUUM, update stats |
| Lock contention | Long-running transactions | Keep transactions short, use NOWAIT |
| Bloat/disk growth | Dead tuples not vacuumed | Tune autovacuum, manual VACUUM |
| Memory pressure | Low shared_buffers / work_mem | Increase memory parameters |

## Recovery

### Transaction rollback

If a transaction was aborted, the entire transaction is rolled back.
PostgreSQL is crash-safe — no manual recovery needed.

### pg_dump/restore failures

| Issue | Solution |
|---|---|
| Version mismatch | Use matching pg_dump/pg_restore version |
| Out of memory | Use `-j` parallel jobs sparingly, increase work_mem |
| Disk full during restore | Ensure enough disk space for data and indexes |

### Forgotten password

Reset via RDS console (see `ctyun-rds-ops`).
