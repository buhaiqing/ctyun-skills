---
name: ctyun-dns-ops
version: 1.0.0
description: >
  Manage CTyun DNS (云解析) resources — domains, record sets, resolution
  policies, and DNS monitoring. Primary route for any DNS management or
  domain name resolution task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: dns.ctapi.ctyun.cn
  api_version: v4
  lifecycle: shipped
---

# ctyun-dns-ops

## Trigger & Scope

### SHOULD Use

- Create a new DNS domain
- List all DNS domains
- Describe domain details
- Delete a DNS domain
- Create DNS record sets (A, AAAA, CNAME, MX, TXT, NS, SRV)
- List record sets for a domain
- Update DNS record sets
- Delete DNS record sets
- Configure smart resolution lines
- Set up DNS monitoring (health checks, alarm rules)
- Query DNS resolution logs and statistics
- Configure domain NS records
- Enable/disable DNS resolution for a domain

### SHOULD NOT Use

- CDN domain configuration → delegate to `ctyun-cdn-ops`
- Load balancer configuration → delegate to `ctyun-elb-ops`
- EIP lifecycle → delegate to `ctyun-eip-ops`
- SSL certificate management → delegate to `ctyun-kms-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- ECS instance creation/management → delegate to `ctyun-ecs-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "DNS" or "domain resolution" or "record set" | Route here |
| User asks about "A record" or "CNAME" or "MX record" | Route here |
| User asks about "smart resolution" or "DNS monitoring" | Route here |
| User asks about "CDN" or "content delivery" | Route to `ctyun-cdn-ops` |
| User asks about "SSL" or "certificate" | Route to `ctyun-kms-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.DNS_ENDPOINT}}` | Agent runtime env | `dns.ctapi.ctyun.cn` |
| `{{user.domain_id}}` | Ask once, cache per session | `dns-xxxxxxxx` |
| `{{user.domain_name}}` | Ask once, cache per session | `example.com` |
| `{{user.record_id}}` | Ask once, cache per session | `record-xxxxxxxx` |
| `{{user.record_type}}` | Ask once, cache per session | `A` / `AAAA` / `CNAME` / `MX` / `TXT` |
| `{{user.record_name}}` | Ask once, cache per session | `www` / `@` / `api` |
| `{{user.record_value}}` | Ask once, cache per session | `1.2.3.4` / `target.example.com` |
| `{{user.ttl}}` | Ask once, cache per session | `600` (seconds) |
| `{{user.priority}}` | Ask once, cache per session | `10` (MX/SRV priority) |
| `{{user.resolution_line}}` | Ask once, cache per session | `default` / `telecom` / `unicom` / `mobile` |
| `{{output.domain_id}}` | Parsed from JSON response | from CreateDomain |
| `{{output.domain_status}}` | Parsed from JSON response | `active` / `paused` / `deleted` |
| `{{output.record_id}}` | Parsed from JSON response | from CreateRecord |
| `{{output.record_list}}` | Parsed from JSON response | from ListRecords |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support DNS operations (verified: `ctyun dns` subcommand does not exist).
The primary path uses direct REST API calls to CTyun DNS OpenAPI endpoints
with EOP signature authentication.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and DNS endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List DNS Domains

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{DNS_ENDPOINT}/v4/dns/domain/list"
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

### Flow B: Create a DNS Domain

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/domain/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainName": "{{user.domain_name}}",
    "description": "{{user.domain_description}}"
})
```

> **Note:** Verify domain ownership before creating. The domain must not be
> already managed by another DNS provider's NS records.

### Flow C: Delete a DNS Domain

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/domain/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}"
})
```

> **Safety Gate:** This operation is IRREVERSIBLE.
> **REQUIRED:**
>
> 1. Confirm the domain is no longer serving production traffic
> 2. Verify all dependent subdomains and records are documented
> 3. Ask user explicitly: "Delete DNS domain `{{user.domain_name}}` and all its record sets? This cannot be undone."
> 4. Only proceed on explicit `yes` confirmation

### Flow D: Create Record Set

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/record/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}",
    "recordName": "{{user.record_name}}",
    "recordType": "{{user.record_type}}",
    "recordValue": "{{user.record_value}}",
    "ttl": {{user.ttl}},
    "priority": {{user.priority}},     # MX/SRV only
    "resolutionLine": "{{user.resolution_line}}"
})
```

**Supported record types:**

| Type | Usage | Example Value |
|---|---|---|
| A | IPv4 address | `1.2.3.4` |
| AAAA | IPv6 address | `2001:db8::1` |
| CNAME | Canonical name | `target.example.com` |
| MX | Mail exchange | `mail.example.com` |
| TXT | Text record | `v=spf1 include:_spf.example.com ~all` |
| NS | Name server | `ns1.example.com` |
| SRV | Service locator | `0 5 5060 sipserver.example.com` |

### Flow E: List Record Sets

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/record/list"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}"
})
```

### Flow F: Update Record Set

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/record/update"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}",
    "recordId": "{{user.record_id}}",
    "recordValue": "{{user.record_value}}",
    "ttl": {{user.ttl}},
    "priority": {{user.priority}},
    "resolutionLine": "{{user.resolution_line}}"
})
```

### Flow G: Delete Record Set

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/record/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}",
    "recordId": "{{user.record_id}}"
})
```

> **Safety Gate:** Confirm before deleting record sets in production domains.
> Deleting critical records (MX, NS, A for active services) will cause
> service disruption.

### Flow H: Query DNS Monitoring / Statistics

```python
url = f"https://{DNS_ENDPOINT}/v4/dns/statistics"
headers = sign_request("GET", url, ...)
resp = requests.get(url, headers=headers, params={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainId": "{{user.domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

---

## Output Parsing Rules

DNS API responses follow a standard CTyun JSON format.

| Operation | Data Path | Key Fields |
|---|---|---|
| List Domains | `$.returnObj[]` | `domainId, domainName, status, createTime, expireTime` |
| Create Domain | `$.returnObj` | `domainId, domainName, status` |
| Delete Domain | `$.returnObj` | `domainId, status` |
| Create Record | `$.returnObj` | `recordId, recordName, recordType, recordValue` |
| List Records | `$.returnObj[]` | `recordId, recordName, recordType, recordValue, ttl, status` |
| Update Record | `$.returnObj` | `recordId, recordValue, ttl` |
| Delete Record | `$.returnObj` | `recordId, status` |
| DNS Statistics | `$.returnObj` | `totalQueries, successRate, avgResolutionTime, errorCount` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `DomainNotFound` / 404 | Business | No | Verify domain ID and name |
| `DomainAlreadyExists` | Business | No | Domain name already registered |
| `RecordNotFound` / 404 | Business | No | Verify record ID |
| `RecordConflict` | Business | No | Record with same name/type already exists |
| `InvalidRecordValue` | Business | No | Validate record value format |
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
| `gcl_mode` | `required` | Delete domain removes all DNS records |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete domain/record operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-dns-ops skill — domain CRUD, record set management, DNS monitoring |
