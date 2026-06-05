# DNS Monitoring

## Cloud Monitor Metrics

CTyun Cloud Monitor collects the following DNS metrics:

| Metric | Description | Unit |
|---|---|---|
| `dns_query_count` | Total DNS queries | count/s |
| `dns_success_rate` | Query success rate | % |
| `dns_avg_resolution_time` | Average resolution time | ms |
| `dns_error_count` | Error query count | count/s |
| `dns_nxdomain_count` | NXDOMAIN response count | count/s |

## Querying Statistics

DNS statistics can be retrieved via the DNS Statistics API:

```python
url = "https://dns.ctapi.ctyun.cn/v4/dns/statistics"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

## Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| Success rate | < 99.9% | < 99.0% | Check DNS config, verify NS delegation |
| Resolution time | > 100ms | > 500ms | Optimize record sets, check upstream DNS |
| NXDOMAIN rate | > 1% | > 5% | Check for stale records or misconfigurations |
| Error count | > 10/min | > 100/min | Investigate API or system issues |

## DNS Monitoring (Health Checks)

DNS monitoring can be configured to perform periodic health checks:

- Query frequency: configurable (e.g., every 5 minutes)
- Probe locations: multiple geographic regions
- Alert on: resolution failure, slow response, unexpected answer
