# MySQL Monitoring

## Built-in MySQL Monitoring

### SHOW PROCESSLIST

```sql
SHOW FULL PROCESSLIST;
-- Shows all active connections with their current queries
-- Check for long-running queries, lock waits
```

### SHOW STATUS

```sql
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Slow_queries';
SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_current_waits';
SHOW GLOBAL STATUS LIKE 'Qps';
```

### SHOW VARIABLES

```sql
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
```

### Performance Schema

```sql
-- Top queries by execution time
SELECT DIGEST_TEXT, COUNT_STAR, AVG_TIMER_WAIT/1000000000 AS avg_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY AVG_TIMER_WAIT DESC LIMIT 10;
```

### Slow Query Log

```sql
-- Check number of slow queries
SHOW GLOBAL STATUS LIKE 'Slow_queries';

-- Analyze slow queries (requires slow_query_log enabled)
mysqldumpslow -s t -t 10 /var/lib/mysql/*-slow.log
```

## CTyun Cloud Monitor Metrics

See `ctyun-cloudmonitor-ops` and [`../../ctyun-rds-ops/references/monitoring.md`](../../ctyun-rds-ops/references/monitoring.md)
for infrastructure-level monitoring.
