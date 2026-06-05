# SSL Certificate Core Concepts

## Product Overview

CTyun SSL Certificate (证书管理服务/CCMS) provides centralized management for SSL/TLS certificates. It supports viewing existing certificates, applying for new certificates from CTyun CA, uploading externally obtained certificates, deploying certificates to cloud resources, and monitoring certificate expiry.

## Key Concepts

### Certificate Types

| Type | Description | Source |
|---|---|---|
| **Applied** | Certificates issued by CTyun CA (Certificate Authority) through the platform | CTyun CA |
| **Uploaded** | Certificates obtained from external CAs (e.g., DigiCert, Let's Encrypt) and uploaded manually | External |
| **Free** | Free single-domain certificates (typically 1-year validity, auto-renewable) | CTyun CA |

### Certificate Brands

| Brand | Description | Typical Use Case |
|---|---|---|
| SecureStar | CTyun's own CA brand | Standard HTTPS |
| GeoTrust | Widely trusted commercial CA | Enterprise HTTPS |
| GlobalSign | High-assurance certificates | Financial/Government |
| DigiCert | Premium CA with high trust | High-security applications |

### Validity Periods

| Period | Description |
|---|---|
| 1 year | Standard period for most certificates |
| 2 years | Available for specific brands/plans |
| 3 years | Extended period (enterprise plans only) |

### Certificate States

| State | Meaning |
|---|---|
| PENDING_APPLY | Application submitted, awaiting issue |
| ISSUED | Certificate issued and active |
| EXPIRED | Certificate validity has expired |
| PENDING_REVOKE | Revocation requested |
| REVOKED | Certificate revoked |

### Deployment Targets

SSL certificates can be deployed to:
- **ELB** (Elastic Load Balancer) — HTTPS listeners
- **CDN** — HTTPS acceleration domains
- **WAF** — HTTPS web protection
- **API Gateway** — HTTPS API endpoints
- **ECS** — Direct server deployment (requires manual config)

### Expiry Monitoring

Certificate expiry is a critical operational concern. The system can:
- Query certificates expiring within N days
- Alert before expiration (typically 30/14/7 days)
- Automatically renew eligible certificates

## SKILL.md Quick Reference

| Operation | Required Params |
|---|---|
| List Certificates | `regionId` |
| Get Certificate Detail | `regionId`, `certificateId` |
| Apply Certificate | `regionId`, `domainName`, `certType` |
| Upload Certificate | `regionId`, `name`, `certificateBody`, `privateKey` |
| Delete Certificate | `regionId`, `certificateId` |
| Deploy Certificate | `regionId`, `certificateId`, `resourceType`, `resourceId` |
| Check Expiry | `regionId` |
| Download Certificate | `regionId`, `certificateId` |

> **Safety Gate**: `Delete` and `Deploy` operations require explicit user confirmation. `Delete` is irreversible — ensure the certificate is not in use.