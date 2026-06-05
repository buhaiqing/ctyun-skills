---
name: ctyun-ssl-cert-ops
version: 1.0.0
description: >
  Manage CTyun SSL Certificate (证书管理服务/CCMS) resources — certificate
  lifecycle, application, upload, deployment, expiry monitoring, and download.
  Primary route for any SSL/TLS certificate management task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: cert.ctapi.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-ssl-cert-ops

## Trigger & Scope

### SHOULD Use

- List SSL certificates
- Get certificate details
- Apply for a new SSL certificate (DV/OV/EV)
- Upload an existing SSL certificate
- Delete an SSL certificate
- Deploy an SSL certificate to CDN or ELB
- Query certificate expiry information
- Download certificate files
- Monitor certificate expiration dates
- Configure certificate renewal

### SHOULD NOT Use

- Key management and encryption operations → delegate to `ctyun-kms-ops`
- DNS record management → delegate to `ctyun-dns-ops`
- CDN domain configuration → delegate to `ctyun-cdn-ops`
- Load balancer configuration → delegate to `ctyun-elb-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "SSL certificate" or "证书" or "HTTPS cert" | Route here |
| User asks about "certificate apply" or "certificate upload" | Route here |
| User asks about "certificate expiry" or "certificate renewal" | Route here |
| User asks about "deploy certificate" | Route here |
| User asks about "key management" or "KMS" or "encryption key" | Route to `ctyun-kms-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.CERT_ENDPOINT}}` | Agent runtime env | `cert.ctapi.ctyun.cn` |
| `{{user.cert_id}}` | Ask once, cache per session | `cert-xxxxxxxx` |
| `{{user.cert_name}}` | Ask once, cache per session | `example-com-cert` |
| `{{user.domain_name}}` | Ask once, cache per session | `www.example.com` |
| `{{user.cert_type}}` | Ask once, cache per session | `DV` / `OV` / `EV` |
| `{{user.brand}}` | Ask once, cache per session | `TRUSTASIA` / `GLOBALSIGN` / `SYMANTEC` |
| `{{user.validity_period}}` | Ask once, cache per session | `1` (years) |
| `{{user.certificate_body}}` | Ask once, cache per session | PEM-encoded cert body |
| `{{user.private_key}}` | Ask once, cache per session | PEM-encoded key |
| `{{output.certificate_id}}` | Parsed from JSON response | from ListCertificates |
| `{{output.certificate_status}}` | Parsed from JSON response | `ISSUED` / `EXPIRED` / `REVOKED` |
| `{{output.expire_time}}` | Parsed from JSON response | ISO 8601 timestamp |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support SSL certificate management operations (verified: `ctyun cert`
subcommand does not exist). The primary path uses direct REST API calls
to CTyun Certificate OpenAPI endpoints with EOP signature authentication.

> **Note:** This skill uses `statusCode == 200` for success (not 800 like
> many other CTyun products). All code examples reflect this difference.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and certificate endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List Certificates

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{CERT_ENDPOINT}/v1/certificate/list"
headers = sign_request(
    method="POST",
    url=url,
    body={},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "pageNumber": 1,
    "pageSize": 20
})
data = resp.json()
```

**Validation:** Check `$.statusCode == 200`. Parse `$.returnObj[]`.

### Flow B: Get Certificate Details

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/detail"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "id": "{{user.cert_id}}"
})
```

**Returns:** Full certificate metadata including brand, type, domain, issue/expire time, fingerprint, CSR, and contact information.

### Flow C: Apply for New Certificate

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/apply"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "domainName": "{{user.domain_name}}",
    "certType": "{{user.cert_type}}",    # DV | OV | EV
    "brand": "{{user.brand}}",            # certificate brand
    "validityPeriod": {{user.validity_period}},
    "contactEmail": "{{user.contact_email}}",
    "contactPhone": "{{user.contact_phone}}"
})
```

> **Note:** DV certificates require DNS TXT record verification. Use
> `ctyun-dns-ops` to create the verification TXT record if needed.

### Flow D: Upload Existing Certificate

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/upload"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "name": "{{user.cert_name}}",
    "certificateBody": "{{user.certificate_body}}",
    "privateKey": "{{user.private_key}}"
})
```

> **Security:** The private key is transmitted encrypted via HTTPS. Verify
> the certificate matches the private key before upload.

### Flow E: Delete Certificate

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "id": "{{user.cert_id}}"
})
```

> **Safety Gate:** This operation is IRREVERSIBLE.
> **REQUIRED:**
>
> 1. Verify the certificate is not currently deployed to any CDN/ELB resource
> 2. Check if the certificate is used by other services
> 3. Ask user explicitly: "Delete certificate `{{user.cert_name}}` (ID:
>    `{{user.cert_id}}`)? This cannot be undone — any services using this
>    certificate will fail to establish HTTPS connections."
> 4. Only proceed on explicit `yes` confirmation

### Flow F: Deploy Certificate

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/deploy"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "certificateId": "{{user.cert_id}}",
    "resourceType": "cdn",   # cdn | elb
    "resourceId": "{{user.resource_id}}"
})
```

### Flow G: Query Certificate Expiry

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/expiry"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "daysBeforeExpiry": 30  # filter certs expiring within 30 days
})
```

### Flow H: Download Certificate

```python
url = f"https://{CERT_ENDPOINT}/v1/certificate/download"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "id": "{{user.cert_id}}"
})
```

---

## Output Parsing Rules

Certificate API responses use `statusCode == 200` for success.

| Operation | Data Path | Key Fields |
|---|---|---|
| List Certificates | `$.returnObj[]` | `id, name, domainName, brand, type, status, expireTime` |
<!-- markdownlint-disable MD013 -->
| Certificate Detail | `$.returnObj` | `workOrderNo, resourceId, brand, type, certificateId, fingerprint, issueTime, expireTime, domainName, domainType, status` |
<!-- markdownlint-enable MD013 -->
| Apply Certificate | `$.returnObj` | `workOrderNo, resourceId, certificateId` |
| Upload Certificate | `$.returnObj` | `resourceId, certificateId, name` |
| Delete Certificate | `$.returnObj` | `resourceId, status` |
| Deploy Certificate | `$.returnObj` | `deployId, resourceType, resourceId, status` |
| Certificate Expiry | `$.returnObj[]` | `certificateId, domainName, expireTime, daysRemaining` |
| Download Certificate | `$.returnObj` | `certificateBody, privateKey, certificateChain` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 200` | Business | No | Surface `$.message` |
| `CertificateNotFound` | Business | No | Verify certificate ID |
| `DomainNotVerified` | Business | No | Complete DNS TXT verification first |
| `InvalidCertificate` | Business | No | Validate certificate format and chain |
| `PrivateKeyMismatch` | Business | No | Certificate and private key do not match |
| `SignatureNotMatch` | Environment | 1x | Check credentials and system clock |
| `5xx` / timeout | Runtime | 3x exponential backoff | Retry with 2s → 4s → 8s |
| `requests` ImportError | Environment | 1x | `pip install requests` |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Delete certificate breaks HTTPS for all deployed resources |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete certificate |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
<!-- markdownlint-disable MD013 -->
| 1.0.0 | 2026-06-05 | Initial ctyun-ssl-cert-ops skill — certificate list, apply, upload, delete, deploy, expiry, download |
<!-- markdownlint-enable MD013 -->