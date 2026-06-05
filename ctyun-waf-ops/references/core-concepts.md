# WAF Core Concepts

## Product Overview

CTyun WAF (Web应用防火墙) protects web applications from common attacks including SQL injection, XSS, file inclusion, command execution, and other OWASP Top 10 threats. WAF sits between users and your web application, inspecting and filtering HTTP/HTTPS traffic.

## Key Concepts

### WAF Instance

A WAF instance is the base resource unit. It defines the compute resources (spec), region, and network configuration. Each instance can protect multiple domains.

### Protected Domain

A domain name added to a WAF instance for protection. Each domain has:
- **Domain Name**: The actual domain (e.g., `www.example.com`)
- **Protection Mode**:
  - `detect` (Detection) — logs attacks but does not block
  - `protect` (Protection) — blocks detected attacks
  - `disabled` (Disabled) — passes through without inspection
- **HTTPS Settings**: SSL certificate binding for HTTPS traffic inspection

### Protection Rules

| Type | Purpose | Typical Action |
|---|---|---|
| SQL Injection | Detect SQL injection attempts in query params, POST body | block/log |
| XSS | Detect cross-site scripting attacks | block/log |
| File Inclusion | Detect file inclusion attempts (LFI/RFI) | block/log |
| Command Execution | Detect command injection attacks | block/log |
| CSRF | Detect cross-site request forgery | block/log |
| Custom Rules | User-defined regex patterns | block/log/captcha |

### ACL (Access Control List)

IP-based access control:
- **Blacklist**: Block requests from specific IP addresses or ranges
- **Whitelist**: Allow requests from specific IP addresses (bypassing WAF rules)
- Supports both single IP (e.g., `192.168.1.1`) and CIDR (e.g., `192.168.1.0/24`)

### Attack Logs

WAF records all detected attacks with:
- Timestamp, source IP, target domain
- Attack type, matched rule
- Request details (URI, headers, body)
- Action taken (blocked/logged)

### Statistics

Aggregated metrics include:
- Total requests, blocked requests
- Top attack types
- Top source IPs
- Requests over time

## SKILL.md Quick Reference

| Operation | Required Params |
|---|---|
| Instance List | `regionId` |
| Add Domain | `regionId`, `instanceId`, `domainName`, `protectionMode` |
| Remove Domain | `regionId`, `instanceId`, `domainId` |
| Domain List | `regionId`, `instanceId` |
| Configure Rule | `regionId`, `instanceId`, `domainId`, `ruleType`, `action` |
| Configure ACL | `regionId`, `instanceId`, `domainId`, `aclType`, `ipAddress`, `action` |
| Query Logs | `regionId`, `instanceId`, `startTime`, `endTime` |
| Get Statistics | `regionId`, `instanceId`, `startTime`, `endTime` |

> **Always query `WAF Instance List` first** to discover existing instances before performing domain or rule operations.