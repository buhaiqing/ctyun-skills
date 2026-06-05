# DNS Troubleshooting

## Common Issues

### Domain creation fails

| Symptom | Likely Cause | Solution |
|---|---|---|
| `DomainAlreadyExists` | Domain already registered | Check existing domains list |
| `DomainNotVerified` | Domain ownership not verified | Verify via TXT record or NS delegation |
| `InvalidDomainName` | Invalid domain name format | Validate domain name syntax |
| `SignatureNotMatch` | EOP signature incorrect | Check system clock, access/secret key |
| `QuotaExceeded` | Exceeded max domains | Request quota increase |

### DNS resolution not working

| Symptom | Likely Cause | Solution |
|---|---|---|
| Domain not resolving | NS records not delegated | Configure NS records at registrar |
| Wrong IP returned | Stale DNS cache | Wait for TTL expiry or reduce TTL |
| Partial ISP failure | Smart resolution misconfiguration | Check resolution line settings |
| NXDOMAIN | Record does not exist | Verify record name and type |
| SERVFAIL | DNSSEC validation failure | Check DNSSEC configuration |

### Record creation fails

| Symptom | Likely Cause | Solution |
|---|---|---|
| `RecordConflict` | Duplicate record name/type | Modify existing record instead |
| `InvalidRecordValue` | Invalid record value format | Validate format (e.g., valid IP, FQDN) |
| `TtlOutOfRange` | TTL outside allowed range | Use TTL between 60 and 86400 |
| `LineNotSupported` | Resolution line not available | Check available resolution lines |

### Performance issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Slow resolution | High TTL causing propagation delay | Reduce TTL during migrations |
| High query latency | Too many records per domain | Consolidate or split zones |
| DNS errors spike | DDoS attack | Enable rate limiting, contact support |

## Recovery

### Accidental record deletion

1. Recreate the record immediately using the same name/type/value/TTL
2. Check DNS monitoring for impact window
3. Verify resolution is restored

### Accidental domain deletion

1. Recreate the domain
2. Re-create all record sets (use backup if available)
3. Re-configure NS delegation at registrar
4. Wait for DNS propagation (may take up to 48 hours)

### Domain hijacking suspicion

1. Immediately pause the domain
2. Audit all record sets for unauthorized changes
3. Reset API credentials
4. Re-enable with verified records only
