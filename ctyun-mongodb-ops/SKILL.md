---
name: ctyun-mongodb-ops
version: 1.0.0
description: >
  Manage CTyun MongoDB (文档数据库服务) — instance lifecycle (create,
  describe, delete, backup, restore) via REST API AND data-level operations
  (queries, indexes, aggregations, DDL) via mongosh CLI.
  Combines infra and data operations in one skill.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: mongodb.ctapi.ctyun.cn
  tool_mongosh_client: mongosh
  lifecycle: shipped
---

# ctyun-mongodb-ops

## Trigger & Scope

### SHOULD Use

- Create a new MongoDB (文档数据库) instance
- List and describe MongoDB instances
- Delete a MongoDB instance
- Backup a MongoDB instance
- Restore a MongoDB instance from backup
- Execute MongoDB queries, aggregations, or commands
- Create, drop, or manage MongoDB collections
- Create and manage MongoDB indexes
- Manage MongoDB users and roles
- Drop a MongoDB collection or database
- Monitor MongoDB instance metrics

### SHOULD NOT Use

- RDS MySQL instance lifecycle → delegate to `ctyun-rds-ops`
- MySQL data-level operations → delegate to `ctyun-mysql-ops`
- PostgreSQL data-level operations → delegate to `ctyun-postgresql-ops`
- ECS instance management → delegate to `ctyun-ecs-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User mentions "MongoDB" or "document database" or "mongosh" | Route here |
| User asks "create instance", "delete MongoDB", "backup MongoDB" | Route here (infra path) |
| User asks "find()", "aggregate", "drop collection", "createIndex" | Route here (data path) |
| User asks "MySQL" or "RDS" | Route to `ctyun-rds-ops` or `ctyun-mysql-ops` |
| User asks "PostgreSQL" | Route to `ctyun-postgresql-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.MONGODB_ENDPOINT}}` | Agent runtime env | `mongodb.ctapi.ctyun.cn` |
| `{{user.mongodb_id}}` | Ask once, cache per session | MongoDB instance ID |
| `{{user.instance_type}}` | Ask once, cache per session | `mongo.s1.small` |
| `{{user.storage_size}}` | Ask once, cache per session | storage in GB |
| `{{user.vpc_id}}` | Ask once, cache per session | VPC ID for network |
| `{{user.subnet_id}}` | Ask once, cache per session | Subnet ID |
| `{{user.host}}` | Ask once, cache per session | MongoDB connection host |
| `{{user.port}}` | Ask once, cache per session | `27017` (default) |
| `{{user.database}}` | Ask once, cache per session | MongoDB database name |
| `{{user.collection}}` | Ask once, cache per session | collection name |
| `{{user.username}}` | Ask once, cache per session | MongoDB user |
| `{{user.password}}` | Ask once, cache per session | MongoDB password (never log) |
| `{{user.connection_string}}` | Ask once, cache per session | `mongodb://user:pass@host:27017/db` |
| `{{output.mongodb_id}}` | Parsed from JSON response | from CreateInstance |
| `{{output.query_result}}` | Parsed from mongosh output | query documents |

---

## Execution Flows

This skill uses two execution paths:

1. **Instance operations** → REST API (CTyun MongoDB OpenAPI)
2. **Data operations** → `mongosh` CLI

### Pre-flight

**For instance operations:**

1. Install `requests`: `pip install requests`
2. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
3. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

**For data operations:**

1. Verify `mongosh` installed: `mongosh --version`
2. Verify connectivity:

   ```bash
   mongosh "{{user.connection_string}}" --eval "db.runCommand({ping:1})"
   ```

---

### Flow A: List MongoDB Instances

```python
import requests
from eop_signer import sign_request

url = f"https://{MONGODB_ENDPOINT}/v4/mongodb/instance/list"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={"regionId": "{{env.CTYUN_REGION_ID}}"})
data = resp.json()
```

**Validation:** Check `$.statusCode == 800`.

### Flow B: Create MongoDB Instance

```python
url = f"https://{MONGODB_ENDPOINT}/v4/mongodb/instance/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceType": "{{user.instance_type}}",
    "storageSize": {{user.storage_size}},
    "vpcId": "{{user.vpc_id}}",
    "subnetId": "{{user.subnet_id}}",
    "name": "{{user.instance_name}}",
    "adminPassword": "{{user.admin_password}}",
    "engineVersion": "{{user.engine_version}}",    # e.g. 6.0, 7.0
    "clientToken": "{{output.client_token}}"
})
```

> **Note:** Always generate a UUID `clientToken` for idempotency.

### Flow C: Delete MongoDB Instance

```python
url = f"https://{MONGODB_ENDPOINT}/v4/mongodb/instance/delete"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.mongodb_id}}"
})
```

> **Safety Gate:** IRREVERSIBLE.
>
> 1. Confirm instance no longer serves production traffic
> 2. Verify a recent backup exists
> 3. Ask user explicitly: "Delete MongoDB instance `{{user.mongodb_id}}` and all its data? This cannot be undone."
> 4. Only proceed on explicit `yes`

---

### Flow D: Execute MongoDB Query (mongosh)

```bash
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.find({{user.filter}}).limit({{user.limit}}).toArray()
'
```

**Output:** JSON document array on stdout. Parse via `JSON.parse`.

### Flow E: Create / Drop Collection

```bash
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.createCollection("{{user.collection}}");
'
```

```bash
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.drop();
'
```

> **Safety Gate for drop():** Confirm with user before dropping collection.

### Flow F: Create Index

```bash
mongosh "{{user.connection_string}}" --quiet --eval '
  use("{{user.database}}");
  db.{{user.collection}}.createIndex({{user.index_spec}});
'
```

### Flow G: Drop Database (Destructive)

```bash
mongosh "{{user.connection_string}}" --quiet --eval '
  db.getSiblingDB("{{user.database}}").dropDatabase();
'
```

> **Safety Gate:** IRREVERSIBLE. Require explicit confirmation.

### Flow H: Backup Instance (REST API)

```python
url = f"https://{MONGODB_ENDPOINT}/v4/mongodb/backup/create"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceId": "{{user.mongodb_id}}",
    "backupType": "full"
})
```

---

## Output Parsing Rules

**Instance operations:**

| Operation | Data Path | Key Fields |
|---|---|---|
| List Instances | `$.returnObj[]` | `instanceId, name, engineVersion, status, createTime` |
| Create Instance | `$.returnObj` | `instanceId, orderId, status` |
| Delete Instance | `$.returnObj` | `instanceId, status` |
| Create Backup | `$.returnObj` | `backupId, backupName, status` |

**Data operations:**

| Operation | Output Source | Key Fields |
|---|---|---|
| find() | mongosh stdout → JSON array | Matching documents |
| aggregate() | mongosh stdout → JSON array | Aggregation pipeline results |
| createIndex() | mongosh stdout | `ok: 1` or error |
| drop() / dropDatabase() | mongosh stdout | `ok: 1` |
| count() | mongosh stdout → integer | Count value |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `InvalidInstanceId` | Business | No | Verify instance ID |
| `SignatureNotMatch` | Environment | 1x | Check credentials/system clock |
| 5xx / timeout (instance API) | Runtime | 3x | Exponential backoff |
| `mongosh: command not found` | Environment | 1x | Install mongosh |
| `MongoNetworkError` | Runtime | 1x | Check host/port/firewall |
| `Authentication failed` | Environment | 1x | Verify credentials |
| `MongoServerError: namespace not found` | Business | No | Verify db/collection name |
| `MongoBulkWriteError` (index) | Business | No | Check index spec |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Delete instance and dropDatabase cause data loss |
| `max_iterations` | `2` | inherited from §8 default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete instance and dropDatabase |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-mongodb-ops skill — instance CRUD via REST API + data operations via mongosh CLI |
