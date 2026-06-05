# RDS Troubleshooting

## Common Issues

### Instance creation fails

| Symptom | Likely Cause | Solution |
|---|---|---|
| `InsufficientBalance` | Account balance too low | Top up account |
| `InvalidInstanceType` | Instance type not available in region | Check available types |
| `QuotaExceeded` | Exceeded max instances per account | Request quota increase |
| `VpcIdInvalid` | VPC does not exist | Verify VPC ID |
| `SignatureNotMatch` | EOP signature incorrect | Check system clock, access/secret key |

### Cannot connect to RDS

| Symptom | Likely Cause | Solution |
|---|---|---|
| Connection timeout | Security group not configured | Add inbound rule for your IP |
| Connection refused | Instance not running | Check instance status |
| Authentication failed | Wrong username/password | Reset password via RDS console |
| SSL error | SSL mode mismatch | Check client SSL settings |

### Performance issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| High CPU | Inefficient queries, missing indexes | Optimize queries, add indexes |
| High memory | Insufficient instance spec | Scale up instance type |
| Slow queries | Missing indexes, table bloat | Use EXPLAIN, add indexes, VACUUM |
| Disk full | Data growth, logs | Increase storage, clean old data |

## Recovery

### Instance stuck in BUILD or BACKING_UP

1. Wait up to 20 minutes (initial build can take 10-30 min)
2. If still stuck after 30 min, contact CTyun support

### Accidental deletion

RDS instances are deleted permanently. Recovery requires restoring from
the latest automated or manual backup.

### Failed resize

If resize operation fails:
1. Check instance is in RUNNING state
2. Verify new spec is valid for the engine
3. Retry after 5 minutes
