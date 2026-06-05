# PostgreSQL Monitoring

## Built-in PostgreSQL Monitoring

### pg_stat_activity

```sql
-- Current active queries
SELECT pid, state, query_start, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - pg_stat_activity.query_start > interval '5 minutes';
```

### pg_stat_statements

```sql
-- Top queries by total execution time
SELECT query, calls, total_exec_time / 1000 AS total_sec,
       mean_exec_time AS mean_ms
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 10;
```

### Table Size & Bloat

```sql
-- Table size
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Bloat estimate (approximate)
SELECT schemaname, tablename, n_dead_tup, n_live_tup,
       round(n_dead_tup * 100.0 / (n_live_tup + 1), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### VACUUM & Autovacuum

```sql
-- Check last vacuum
SELECT relname, last_vacuum, last_autovacuum, last_analyze
FROM pg_stat_user_tables
WHERE relname = '{{user.table}}';

-- Manual vacuum (if autovacuum is delayed)
VACUUM ANALYZE {{user.table}};
```

## CTyun Cloud Monitor Metrics

See `ctyun-cloudmonitor-ops` and [`../../ctyun-rds-ops/references/monitoring.md`](../../ctyun-rds-ops/references/monitoring.md)
for infrastructure-level monitoring.
