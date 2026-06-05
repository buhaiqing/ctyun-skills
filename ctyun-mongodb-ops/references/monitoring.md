# MongoDB Monitoring

## Built-in MongoDB Commands

### Server Status

```javascript
mongosh "{{user.connection_string}}" --quiet --eval 'db.serverStatus()'
```

Key fields: `connections`, `network.bytesIn/Out`, `opcounters`, `mem`, `extra_info`

### Current Operations

```javascript
mongosh "{{user.connection_string}}" --quiet --eval 'db.currentOp(true)'
```

Check for long-running operations (`secs_running > threshold`).

### Database Statistics

```javascript
mongosh "{{user.connection_string}}" --quiet --eval 'db.stats()'
```

Returns: `dataSize`, `storageSize`, `indexSize`, `collections`, `objects`

### Collection Statistics

```javascript
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.stats()
'
```

### Index Usage

```javascript
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.aggregate([
    { $indexStats: {} }
  ]).toArray()
'
```

### Replica Set Status

```javascript
mongosh "{{user.connection_string}}" --quiet --eval 'rs.status()'
```

## Performance Monitoring Tips

- Monitor **opcounters** (insert/update/delete/query rate) for workload patterns
- Check **connections.current** vs **connections.available**
- Monitor **page faults** for memory pressure
- Use `explain("executionStats")` for query performance analysis
- Watch for **slow queries** in the mongod log (set `slowOpThresholdMs`)

## CTyun Cloud Monitor Metrics

CTyun Cloud Monitor collects MongoDB instance metrics:
- CPU / Memory utilization
- Disk IOPS and throughput
- Connection count
- Ops counters (insert/update/delete/query per second)

See `ctyun-cloudmonitor-ops` for alarm rule configuration.
