---
name: ctyun-cdn-ops
version: 1.0.0
description: >
  Manage CTyun CDN (内容分发网络) resources — acceleration domains, cache
  policies, content refresh/prefetch, HTTPS configuration, access control,
  and CDN statistics. Primary route for any CDN or content delivery task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: cdn.ctapi.ctyun.cn
  api_version: v2
  lifecycle: shipped
---

# ctyun-cdn-ops

## Trigger & Scope

### SHOULD Use

- Add a CDN acceleration domain
- List all CDN acceleration domains
- Describe CDN domain configuration details
- Start / stop / delete a CDN acceleration domain
- Configure CNAME for CDN domain
- Set up cache rules (expiration policies, cache behaviors)
- Refresh CDN cache (URL refresh, directory refresh)
- Prefetch content to CDN nodes
- Configure HTTPS certificate for CDN domain
- Configure access control (referer, IP blacklist/whitelist, UA filter)
- Query CDN monitoring metrics (traffic, bandwidth, requests, hit ratio)
- Query CDN access logs
- Configure origin server settings
- Configure HTTP/HTTPS redirect rules

### SHOULD NOT Use

- DNS domain/record management → delegate to `ctyun-dns-ops`
- Load balancer configuration → delegate to `ctyun-elb-ops`
- SSL certificate management/deletion → delegate to `ctyun-kms-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- Object storage file operations → delegate to `ctyun-oos-ops`
- ECS instance creation/management → delegate to `ctyun-ecs-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "CDN" or "content delivery" or "acceleration" | Route here |
| User asks about "cache refresh" or "content prefetch" | Route here |
| User asks about "CDN statistics" or "bandwidth" or "traffic" | Route here |
| User asks about "HTTPS certificate" on CDN | Route here (SSL key management → `ctyun-kms-ops`) |
| User asks about "DNS" or "domain resolution" | Route to `ctyun-dns-ops` |
| User asks about "OOS" or "object storage" | Route to `ctyun-oos-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.CDN_ENDPOINT}}` | Agent runtime env | `cdn.ctapi.ctyun.cn` |
| `{{user.cdn_domain_id}}` | Ask once, cache per session | `cdn-xxxxxxxx` |
| `{{user.cdn_domain_name}}` | Ask once, cache per session | `cdn.example.com` |
| `{{user.origin_type}}` | Ask once, cache per session | `ip` / `domain` / `oss` |
| `{{user.origin_addr}}` | Ask once, cache per session | `origin.example.com` or `1.2.3.4` |
| `{{user.origin_port}}` | Ask once, cache per session | `443` |
| `{{user.cache_rule_id}}` | Ask once, cache per session | `rule-xxxxxxxx` |
| `{{user.cache_ttl}}` | Ask once, cache per session | `3600` (seconds) |
| `{{user.refresh_urls}}` | Ask once, cache per session | `["https://cdn.example.com/images/logo.png"]` |
| `{{user.prefetch_urls}}` | Ask once, cache per session | `["https://cdn.example.com/js/app.js"]` |
| `{{user.certificate_id}}` | Ask once, cache per session | `cert-xxxxxxxx` |
| `{{user.referer_list}}` | Ask once, cache per session | `["*.example.com"]` |
| `{{user.ip_blacklist}}` | Ask once, cache per session | `["1.2.3.0/24"]` |
| `{{output.cdn_domain_id}}` | Parsed from JSON response | from CreateDomain |
| `{{output.cdn_domain_status}}` | Parsed from JSON response | `running` / `stopped` / `deploying` |
| `{{output.cdn_cname}}` | Parsed from JSON response | CNAME value for DNS resolution |
| `{{output.refresh_task_id}}` | Parsed from JSON response | from RefreshCache |
| `{{output.traffic_data}}` | Parsed from JSON response | from GetStatistics |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support CDN operations (verified: `ctyun cdn` subcommand does not exist).
The primary path uses direct REST API calls to CTyun CDN OpenAPI endpoints
with EOP signature authentication.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and CDN endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List CDN Domains

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{CDN_ENDPOINT}/v2/cdn/domain/list"
headers = sign_request(
    method="GET",
    url=url,
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.get(url, headers=headers, params={"regionId": "{{env.CTYUN_REGION_ID}}"})
data = resp.json()
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Add CDN Acceleration Domain

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/domain/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainName": "{{user.cdn_domain_name}}",
    "originType": "{{user.origin_type}}",    # ip | domain | oss
    "originAddr": "{{user.origin_addr}}",
    "originPort": {{user.origin_port}},
    "serviceType": "web",                    # web | download | vod | live
    "httpsStatus": "off"                     # off | on (configure later)
})
```

> **Note:** After creation, configure CNAME at your DNS provider
> (see Flow C). CDN domain will not be active until CNAME resolution is
> correctly set.

### Flow C: Configure CNAME

After CDN domain creation, the API returns a CNAME value. The agent must
guide the user to configure a CNAME record at their DNS provider:

```text
CDN domain: cdn.example.com
CNAME target: cdn.example.com.ctyuncdn.cn
```

> **Best practice:** Use `ctyun-dns-ops` to configure the CNAME record if
> the domain is managed through CTyun DNS.

### Flow D: Start / Stop / Delete CDN Domain

```python
# Start
resp = requests.post(f"https://{CDN_ENDPOINT}/v2/cdn/domain/start", headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}"
})

# Stop
resp = requests.post(f"https://{CDN_ENDPOINT}/v2/cdn/domain/stop", headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}"
})

# Delete
resp = requests.post(f"https://{CDN_ENDPOINT}/v2/cdn/domain/delete", headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}"
})
```

> **Safety Gate (Delete):** Deleting a CDN domain is IRREVERSIBLE.
> **REQUIRED:**
>
> 1. Confirm the CDN domain is no longer serving production traffic
> 2. Verify DNS CNAME has been removed or redirected
> 3. Ask user explicitly: "Delete CDN domain `{{user.cdn_domain_name}}`? This cannot be undone."
> 4. Only proceed on explicit `yes` confirmation

### Flow E: Configure Cache Rules

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/cache/rule/set"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "rules": [
        {
            "path": "/images/*",
            "ttl": 86400,           # 1 day
            "cacheBehavior": "cache_if_origin"  # cache_if_origin | cache_always | no_cache
        },
        {
            "path": "/api/*",
            "ttl": 0,
            "cacheBehavior": "no_cache"
        }
    ]
})
```

### Flow F: Refresh CDN Cache

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/cache/refresh"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "type": "url",                   # url | directory
    "urls": {{user.refresh_urls}}    # list of URLs or directories
})
```

### Flow G: Prefetch Content

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/cache/prefetch"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "urls": {{user.prefetch_urls}}    # list of URLs to pre-cache
})
```

> **Note:** Prefetch is best used for content expected to receive high
> traffic. Most CDN providers charge for prefetch traffic.

### Flow H: Configure HTTPS

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/https/config"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "httpsStatus": "on",
    "certificateId": "{{user.certificate_id}}",
    "redirectType": "https",         # https (redirect all HTTP to HTTPS)
    "http2Status": "on"              # enable HTTP/2
})
```

> **Note:** Certificate must be uploaded first (see `ctyun-kms-ops` or
> CTyun SSL certificate service). Use the certificate ID from the upload
> response.

### Flow I: Configure Access Control

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/acl/config"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "refererEnabled": true,
    "refererList": {{user.referer_list}},
    "refererType": "blacklist",      # blacklist | whitelist
    "ipBlacklistEnabled": true,
    "ipBlacklist": {{user.ip_blacklist}}
})
```

### Flow J: Query CDN Statistics

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/statistics"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "metrics": "traffic,bandwidth,requests,hit_ratio"
})
```

### Flow K: Query Access Logs

```python
url = f"https://{CDN_ENDPOINT}/v2/cdn/logs"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.cdn_domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

---

## Output Parsing Rules

CDN API responses follow a standard CTyun JSON format.

| Operation | Data Path | Key Fields |
|---|---|---|
| List Domains | `$.returnObj[]` | `domainId, domainName, cname, status, createTime, serviceType` |
| Create Domain | `$.returnObj` | `domainId, domainName, cname, status` |
| Describe Domain | `$.returnObj` | `domainId, domainName, cname, originAddr, originType, status, httpsStatus` |
| Start Domain | `$.returnObj` | `domainId, status (running)` |
| Stop Domain | `$.returnObj` | `domainId, status (stopped)` |
| Delete Domain | `$.returnObj` | `domainId, status (deleted)` |
| Cache Config | `$.returnObj` | `domainId, rules[]` |
| Refresh Cache | `$.returnObj` | `taskId, status, urls[]` |
| Prefetch | `$.returnObj` | `taskId, status, urls[]` |
| HTTPS Config | `$.returnObj` | `domainId, httpsStatus` |
| ACL Config | `$.returnObj` | `domainId, refererEnabled, ipBlacklistEnabled` |
| Statistics | `$.returnObj` | `traffic, bandwidth, requests, hitRatio` |
| Access Logs | `$.returnObj[]` | `logName, logSize, logUrl, startTime, endTime` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `DomainNotFound` / 404 | Business | No | Verify CDN domain ID |
| `DomainAlreadyExists` | Business | No | Domain already configured as CDN |
| `DomainDeploying` | Business | No | Wait for previous deployment to complete |
| `OriginUnreachable` | Business | No | Verify origin server is accessible |
| `CertificateNotFound` | Business | No | Upload certificate first (see ctyun-kms-ops) |
| `InvalidUrl` | Business | No | Validate URL format |
| `RefreshQuotaExceeded` | Business | No | Wait for quota reset or reduce refresh batch |
| `SignatureNotMatch` | Environment | 1x | Check credentials and system clock |
| `5xx` / timeout | Runtime | 3x exponential backoff | Retry with 2s → 4s → 8s |
| `requests` ImportError | Environment | 1x | `pip install requests` |
| Connection error | Runtime | 2x | Verify endpoint and network |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Delete/stop CDN domain can disrupt production |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete domain operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-cdn-ops skill — domain CRUD, cache config, refresh/prefetch, HTTPS, ACL, stats |
