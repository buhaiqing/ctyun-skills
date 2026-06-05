---
name: ctyun-waf-ops
version: 1.0.0
description: >
  Manage CTyun WAF (Web应用防火墙) resources — domain protection, rule
  configuration, IP blacklist/whitelist, attack log query, and statistics.
  Primary route for any web application firewall or WAF security task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: waf.ctapi.ctyun.cn
  api_version: v2
  lifecycle: shipped
---

# ctyun-waf-ops

## Trigger & Scope

### SHOULD Use

- Add a domain to WAF protection
- Remove a domain from WAF protection
- List domains protected by WAF
- Configure Web protection rules (SQL injection, XSS, etc.)
- Configure CC attack protection rules
- Configure IP blacklist/whitelist
- Query WAF attack logs
- Query WAF statistics and metrics
- View WAF instance details
- Modify protection mode (detection/block)
- Manage WAF rule groups and policies

### SHOULD NOT Use

- CDN domain configuration → delegate to `ctyun-cdn-ops`
- Load balancer configuration → delegate to `ctyun-elb-ops`
- DNS record management → delegate to `ctyun-dns-ops`
- SSL certificate management → delegate to `ctyun-ssl-cert-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- DDoS protection → delegate to appropriate DDoS skill if available

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "WAF" or "Web应用防火墙" or "web firewall" | Route here |
| User asks about "IP blacklist" or "IP whitelist" for WAF | Route here |
| User asks about "CC protection" or "rate limiting" | Route here |
| User asks about "attack log" or "WAF log" | Route here |
| User asks about "DDoS" or "DDoS高防" | Do NOT route here |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.WAF_ENDPOINT}}` | Agent runtime env | `waf.ctapi.ctyun.cn` |
| `{{user.instance_id}}` | Ask once, cache per session | `waf-xxxxxxxx` |
| `{{user.domain_name}}` | Ask once, cache per session | `www.example.com` |
| `{{user.rule_id}}` | Ask once, cache per session | `rule-xxxxxxxx` |
| `{{user.protection_mode}}` | Ask once, cache per session | `detect` / `block` |
| `{{user.ip_address}}` | Ask once, cache per session | `1.2.3.4` |
| `{{user.acl_action}}` | Ask once, cache per session | `allow` / `deny` |
| `{{output.instance_id}}` | Parsed from JSON response | from ListInstances |
| `{{output.domain_id}}` | Parsed from JSON response | from AddDomain |
| `{{output.rule_id}}` | Parsed from JSON response | from CreateRule |
| `{{output.attack_logs}}` | Parsed from JSON response | from QueryAttackLogs |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support WAF operations (verified: `ctyun waf` subcommand does not exist).
The primary path uses direct REST API calls to CTyun WAF OpenAPI endpoints
with EOP signature authentication.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and WAF endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List WAF Instances

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{WAF_ENDPOINT}/v2/waf/instance/list"
headers = sign_request(
    method="POST",
    url=url,
    body={},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}"
})
data = resp.json()
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Add Domain Protection

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/domain/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainName": "{{user.domain_name}}",
    "protectionMode": "{{user.protection_mode}}"  # detect | block
})
```

> **Note:** The domain must have a valid DNS resolution before adding to WAF.
> Verify the domain resolves to the WAF-protected IP or CNAME first.

### Flow C: Remove Domain Protection

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/domain/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainId": "{{user.domain_id}}"
})
```

> **Safety Gate:** This operation removes WAF protection from the domain.
> **REQUIRED:**
>
> 1. Confirm the domain will have alternative protection in place
> 2. Verify removing WAF will not expose production services to attacks
> 3. Ask user explicitly: "Remove WAF protection for domain
>    `{{user.domain_name}}`? The domain will be directly exposed to the internet."
> 4. Only proceed on explicit `yes` confirmation

### Flow D: Configure Protection Rules

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/rule/config"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainId": "{{user.domain_id}}",
    "ruleType": "web_protection",  # web_protection | cc_protection
    "action": "{{user.protection_mode}}",  # detect | block
    "ruleConfig": {
        # Rule-specific configuration parameters
    }
})
```

**Supported rule types:**

| Type | Protection | Config Options |
|---|---|---|
| `web_protection` | SQL injection, XSS, command injection, file inclusion | `detect` / `block` per category |
| `cc_protection` | Rate limiting, challenge | `threshold` (req/s), `action` (block/challenge) |

### Flow E: Configure IP Blacklist/Whitelist

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/acl/config"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainId": "{{user.domain_id}}",
    "aclType": "blacklist",   # blacklist | whitelist
    "ipAddress": "{{user.ip_address}}",
    "action": "{{user.acl_action}}"  # allow | deny
})
```

### Flow F: Query Attack Logs

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/log/attack"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainId": "{{user.domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}",
    "pageNumber": 1,
    "pageSize": 20
})
```

### Flow G: Query WAF Statistics

```python
url = f"https://{WAF_ENDPOINT}/v2/waf/statistics"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.instance_id}}",
    "domainId": "{{user.domain_id}}",
    "startTime": "{{user.start_time}}",
    "endTime": "{{user.end_time}}"
})
```

---

## Output Parsing Rules

WAF API responses follow a standard CTyun JSON format.

| Operation | Data Path | Key Fields |
|---|---|---|
| List Instances | `$.returnObj[]` | `instanceId, instanceName, status, regionId` |
| Add Domain | `$.returnObj` | `domainId, domainName, protectionMode, status` |
| Remove Domain | `$.returnObj` | `domainId, status` |
| Configure Rule | `$.returnObj` | `ruleId, ruleType, action, status` |
| Configure ACL | `$.returnObj` | `aclId, aclType, ipAddress, action` |
| Query Attack Logs | `$.returnObj[]` | `logId, attackType, srcIp, srcPort, dstIp, dstPort, action, time` |
| Query Statistics | `$.returnObj` | `totalRequests, blockedRequests, attackCount, qps, peakQps` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `DomainNotFound` / 404 | Business | No | Verify domain name and DNS resolution |
| `InstanceNotFound` | Business | No | Verify instance ID |
| `RuleAlreadyExists` | Business | No | Rule with same name already configured |
| `InvalidIPFormat` | Business | No | Validate IP address format |
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
| `gcl_mode` | `required` | Remove domain protection exposes services to attacks |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for remove domain protection and disable rules |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
<!-- markdownlint-disable MD013 -->
| 1.0.0 | 2026-06-05 | Initial ctyun-waf-ops skill — domain protection, rule config, IP ACL, attack log query, statistics |
<!-- markdownlint-enable MD013 -->