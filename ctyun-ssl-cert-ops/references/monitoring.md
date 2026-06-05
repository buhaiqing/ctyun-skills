# SSL Certificate Monitoring & Observability

## Expiry Monitoring

Certificate expiry is the primary monitoring concern. Certificates that expire cause immediate HTTPS failures.

| Check | Frequency | Action |
|---|---|---|
| Expiring within 30 days | Daily | Plan renewal or replacement |
| Expiring within 14 days | Daily | Urgent: renew or deploy replacement |
| Expiring within 7 days | Daily | Critical: immediate action required |
| Already expired | Immediate | Replace certificate immediately |

## Cloud Monitor Integration

Certificate expiry alerts can be configured through `ctyun-cloudmonitor-ops` using the CTS Certificate API as a data source (webhook or custom metric):

| Metric | Alarm Suggestion |
|---|---|
| Days until expiry ≤ 30 | Schedule renewal |
| Days until expiry ≤ 7 | Urgent renewal |
| Certificate count > expected | Verify for orphaned/duplicate certs |

## Operational Recommendations

| Task | Frequency | Description |
|---|---|---|
| List all certificates | Daily | Verify inventory is current |
| Check expiring certificates | Daily | Query certs expiring within 30 days |
| Deploy new certificates | Before expiry | Deploy to all bound resources |
| Remove expired certificates | Monthly | Clean up expired certificates |
| Backup private keys | Per upload | Store securely (outside the platform) |