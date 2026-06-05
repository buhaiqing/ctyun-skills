# MongoDB Troubleshooting

## Common Issues

### Cannot connect to MongoDB

| Error | Likely Cause | Solution |
|---|---|---|
| `MongoNetworkError: connect ECONNREFUSED` | Instance not running or port blocked | Check instance status, security group |
| `MongoNetworkError: authentication failed` | Wrong credentials | Verify username/password, authSource |
| `MongoNetworkError: failed to connect to server` | Network issue | Check VPC, subnet, firewall |
| `MongoNetworkError: SSL handshake failed` | SSL/TLS mismatch | Check SSL settings |

### CRUD Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `MongoServerError: E11000 duplicate key` | Unique index violation | Check existing data |
| `MongoServerError: namespace not found` | Database/collection doesn't exist | Verify name, create if needed |
| `MongoServerError: BSON field too long` | Document exceeds 16MB limit | Split document or use GridFS |
| `MongoServerError: WriteConflict` | Write conflict in replica set | Retry the operation |

### Performance Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Slow queries | Missing index | Create appropriate indexes |
| High memory usage | Working set exceeds RAM | Scale up instance, optimize queries |
| High disk IO | No indexes, full collection scans | Add indexes, use covered queries |
| Connection pool full | Too many connections | Increase pool size, add connection pooling |
| Slow aggregations | No index on $match/$sort stages | Add matching/sorting indexes |

### Replica Set Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Secondary stale | Replication lag | Check network, secondary resource |
| No primary | Election failure | Check replica set health, network partition |
| Rollback | Old primary rejoins after network partition | Accept automatic rollback |

## Recovery

### Accidental deleteOne/deleteMany

1. Check if the operation was committed
2. If replica set has oplog, and deletion is recent, recover from oplog
3. Otherwise, restore from backup

### Accidental dropDatabase/drop

**Irreversible.** Restore from latest backup (CTyun API backup or mongodump).

### Corruption

1. Stop the mongod service
2. Run `mongod --repair` (may lose data)
3. If repair fails, restore from backup
