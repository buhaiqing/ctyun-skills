---
name: ctyun-rds-ops
version: 1.0.0
description: >
  Manage CTyun RDS (关系型数据库) instances — create, describe, delete,
  resize, backup, restore, and configure relational database instances.
  Primary route for any RDS or managed database infrastructure task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: ctrds.ctapi.ctyun.cn
  api_version: v4
  lifecycle: shipped
---

# ctyun-rds-ops

## Trigger & Scope

### SHOULD Use

- Create a new RDS instance (MySQL, PostgreSQL, SQL Server engine)
- List and describe RDS instances
- Delete an RDS instance
- Resize / modify RDS instance specification
- Create and manage database backups
- Restore an RDS instance from backup
- Modify RDS parameter group settings
- Configure RDS security group / firewall rules
- Query RDS instance monitoring metrics
- Reboot an RDS instance

### SHOULD NOT Use

- MySQL data-level operations (DROP TABLE, DELETE FROM, TRUNCATE) → delegate to `ctyun-mysql-ops`
- PostgreSQL data-level operations → delegate to `ctyun-postgresql-ops`
- MongoDB instance or data operations → delegate to `ctyun-mongodb-ops`
- ECS instance creation/management → delegate to `ctyun-ecs-ops`
- Disk/volume operations → delegate to `ctyun-evs-ops` (planned)
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "RDS" or "relational database" or "MySQL instance" (infrastructure) | Route here |
| User asks about "create database" or "delete database" (infra-level) | Route here |
| User asks about "DROP TABLE" or "SQL query" or "DELETE FROM" | Route to `ctyun-mysql-ops` or `ctyun-postgresql-ops` |
| User asks about "MongoDB" or "document database" | Route to `ctyun-mongodb-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.RDS_ENDPOINT}}` | Agent runtime env | `ctrds.ctapi.ctyun.cn` |
| `{{user.rds_id}}` | Ask once, cache per session | `rds-xxxxxxxx` |
| `{{user.engine}}` | Ask once, cache per session | `MySQL` / `PostgreSQL` / `SQLServer` |
| `{{user.engine_version}}` | Ask once, cache per session | `5.7` / `8.0` / `15` |
| `{{user.instance_type}}` | Ask once, cache per session | `rds.s1.small` |
| `{{user.storage_size}}` | Ask once, cache per session | storage in GB |
| `{{user.storage_type}}` | Ask once, cache per session | `SSD` / `ESSD` |
| `{{user.vpc_id}}` | Ask once, cache per session | VPC ID for network |
| `{{user.subnet_id}}` | Ask once, cache per session | Subnet ID |
| `{{user.backup_id}}` | Ask once, cache per session | backup identifier |
| `{{user.parameter_group_id}}` | Ask once, cache per session | parameter group ID |
| `{{output.rds_id}}` | Parsed from JSON response | from CreateInstance |
| `{{output.rds_status}}` | Parsed from JSON response | instance status string |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support RDS operations (verified: `ctyun rds` subcommand does not exist).
The primary path uses direct REST API calls to CTyun RDS OpenAPI endpoints.
There is no official CTyun Python SDK for RDS; all calls use Python
`requests` with CTyun EOP signature authentication.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and RDS endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List RDS Instances

**REST API path:**

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{RDS_ENDPOINT}/v4/rds/instance/list"
headers = sign_request(
    method="POST",
    url=url,
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={"regionId": "{{env.CTYUN_REGION_ID}}"})
data = resp.json()
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow B: Describe an RDS Instance

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/instance/detail"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.rds_id}}"
})
```

### Flow C: Create an RDS Instance

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/instance/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "engine": "{{user.engine}}",          # MySQL | PostgreSQL | SQLServer
    "engineVersion": "{{user.engine_version}}",
    "instanceType": "{{user.instance_type}}",
    "storageSize": {{user.storage_size}},
    "storageType": "{{user.storage_type}}",
    "vpcId": "{{user.vpc_id}}",
    "subnetId": "{{user.subnet_id}}",
    "name": "{{user.instance_name}}",
    "adminPassword": "{{user.admin_password}}",
    "clientToken": "{{output.client_token}}"
})
```

> **Safety Note:** Always generate a UUID `clientToken` for idempotency.
> Admin password must be provided securely (never log or echo).

### Flow D: Delete an RDS Instance

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/instance/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.rds_id}}"
})
```

> **Safety Gate:** This operation is IRREVERSIBLE.
> **REQUIRED:**
>
> 1. Confirm the instance is no longer serving production traffic
> 2. Verify a recent backup exists (if data retention is needed)
> 3. Ask user explicitly: "Delete RDS instance `{{user.rds_id}}` and all its data? This cannot be undone."
> 4. Only proceed on explicit `yes` confirmation

### Flow E: Resize an RDS Instance

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/instance/resize"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.rds_id}}",
    "instanceType": "{{user.instance_type}}",
    "storageSize": {{user.storage_size}}
})
```

> **Note:** Resize may cause a brief downtime (typically 1-5 minutes).

### Flow F: Backup an RDS Instance

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/backup/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.rds_id}}",
    "backupType": "full",       # full | increment
    "description": "{{user.backup_description}}"
})
```

### Flow G: Restore from Backup

```python
url = f"https://{RDS_ENDPOINT}/v4/rds/instance/restore"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.rds_id}}",
    "backupId": "{{user.backup_id}}"
})
```

---

## Output Parsing Rules

RDS API responses follow a standard CTyun JSON format.

| Operation | Data Path | Key Fields |
|---|---|---|
| List Instances | `$.returnObj[]` | `instanceId, name, engine, engineVersion, status, createTime` |
| Describe Instance | `$.returnObj` | `instanceId, name, engine, engineVersion, status, storageSize, vpcId` |
| Create Instance | `$.returnObj` | `instanceId, orderId, status` |
| Delete Instance | `$.returnObj` | `instanceId, status` |
| Resize Instance | `$.returnObj` | `instanceId, orderId` |
| Create Backup | `$.returnObj` | `backupId, backupName, status` |
| Restore Instance | `$.returnObj` | `instanceId, status` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `InvalidInstanceId` / 404 | Business | No | Verify RDS instance ID |
| `InsufficientBalance` | Business | No | Top up account balance |
| `InstanceStatusError` | Business | No | Instance must be in correct state |
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
| `gcl_mode` | `required` | Delete instance causes data loss |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete instance operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-rds-ops skill — instance CRUD, resize, backup/restore via REST API |
