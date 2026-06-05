# CDN Monitoring

## Cloud Monitor Metrics

CTyun Cloud Monitor collects the following CDN metrics:

| Metric | Description | Unit |
|---|---|---|
| `cdn_traffic` | Total traffic delivered | bytes |
| `cdn_bandwidth` | Peak bandwidth | bps |
| `cdn_requests` | Total request count | count |
| `cdn_hit_ratio` | Cache hit ratio | % |
| `cdn_4xx_count` | 4xx error count | count |
| `cdn_5xx_count` | 5xx error count | count |
| `cdn_avg_speed` | Average download speed | KB/s |
| `cdn_origin_traffic` | Traffic back to origin | bytes |

## Querying Statistics

CDN statistics can be retrieved via the Statistics API:

```python
url = "https://cdn.ctapi.ctyun.cn/v2/cdn/statistics"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "metrics": "traffic,bandwidth,requests,hit_ratio"
})
```

## Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| Traffic spike | +200% vs baseline | +500% vs baseline | Check origin, scale up |
| Hit ratio | < 80% | < 60% | Optimize cache rules |
| 5xx errors | > 1% of total | > 5% of total | Check origin health |
| 4xx errors | > 5% of total | > 10% of total | Review access config |
| Bandwidth | > 80% of limit | > 95% of limit | Upgrade CDN plan |
| Origin latency | > 2s | > 5s | Optimize origin server |

## Access Logs

CDN access logs can be downloaded for detailed analysis:

```python
url = "https://cdn.ctapi.ctyun.cn/v2/cdn/logs"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

Log format typically includes: timestamp, client IP, request method, URL,
HTTP status, response size, referer, user-agent, edge node location.
