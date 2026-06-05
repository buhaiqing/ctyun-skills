# WAF Monitoring & Observability

## Available Metrics

| Metric | Description | Source |
|---|---|---|
| Total Requests | Total HTTP/HTTPS requests processed | WAF Statistics API |
| Blocked Requests | Requests blocked by WAF rules | WAF Statistics API |
| Attack Count | Number of detected attacks | WAF Attack Log API |
| Top Attack Types | Distribution of attack types | WAF Attack Log API |
| Top Source IPs | Most frequent attacker IP addresses | WAF Attack Log API |

## Cloud Monitor Integration

WAF metrics can be monitored through CTyun Cloud Monitor (`ctyun-cloudmonitor-ops`):

| Metric | Alarm Suggestion |
|---|---|
| Blocked request rate > threshold | Possible targeted attack |
| Attack count spike | Investigate attack logs |
| Requests to unprotected new domains | Update domain list |

## Log Analysis

WAF attack logs can be queried programmatically via the WAF API:

```
POST /v2/waf/log/attack
{
  "regionId": "...",
  "instanceId": "...",
  "domainId": "...",
  "startTime": "2026-01-01T00:00:00Z",
  "endTime": "2026-01-02T00:00:00Z",
  "pageNumber": 1,
  "pageSize": 20
}
```

## Operational Recommendations

| Check | Frequency | Action |
|---|---|---|
| Review attack logs | Daily | Investigate blocked attack patterns |
| Check WAF statistics | Weekly | Monitor traffic trends |
| Review protection mode | After new domain added | Ensure new domains are in `protect` mode |
| Update ACL rules | As needed | Block repeat attacker IPs |
| Review rule effectiveness | Monthly | Tune custom rules based on false positive rate |