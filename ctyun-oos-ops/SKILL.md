---
name: ctyun-oos-ops
version: 1.0.0
description: >
  Manage CTyun OOS (对象存储 经典版Ⅰ型) resources — buckets, objects, ACLs,
  lifecycle policies, and pre-signed URLs. Primary route for any object
  storage or file upload/download task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: ">=6.5.7"
  api_profile: oos.ctyunapi.cn
  api_version: v6
  lifecycle: shipped
---

# ctyun-oos-ops

## Trigger & Scope

### SHOULD Use

- Create (put) a new storage bucket
- List all buckets
- Delete a bucket
- Set or update bucket ACL (private, public-read, public-read-write)
- Upload objects (single file)
- Download objects
- Delete objects (single or batch)
- List objects in a bucket
- Copy objects within/between buckets
- Generate pre-signed URLs for temporary access
- Set object ACL
- Configure bucket lifecycle policies
- Query bucket usage statistics

### SHOULD NOT Use

- ECS instance creation/management → delegate to `ctyun-ecs-ops`
- Disk/volume operations → delegate to `ctyun-evs-ops` (planned)
- CDN configuration → delegate to `ctyun-cdn-ops` (planned)
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- Object storage (ZOS, 原生版Ⅱ型) → this skill covers **OOS (经典版Ⅰ型)** only
- Database backup/restore → delegate to the respective DB ops skill

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "OOS" or "object storage" or "bucket" | Route here |
| User asks about "upload file" or "download file" | Route here |
| User asks about "presigned URL" or "temporary URL" | Route here |
| User asks about "file storage" or "cloud storage" | Route here (verify OOS vs. other) |
| User asks about "ECS" or "server" | Route to `ctyun-ecs-ops` |
| User asks about "CDN" or "content delivery" | Route to `ctyun-cdn-ops` (planned) |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.OOS_ENDPOINT}}` | Agent runtime env | `oos-cn.ctyunapi.cn` (default) |
| `{{env.OOS_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.bucket_name}}` | Ask once, cache per session | `my-app-assets` |
| `{{user.object_key}}` | Ask once, cache per session | `images/logo.png` |
| `{{user.local_path}}` | Ask once, cache per session | `/tmp/upload.jpg` |
| `{{user.acl}}` | Ask once, cache per session | `private` / `public-read` |
| `{{user.expires_in}}` | Ask once, cache per session | `3600` (seconds) |
| `{{output.bucket_name}}` | Parsed from SDK response | from CreateBucket |
| `{{output.object_key}}` | Parsed from SDK response | from PutObject |
| `{{output.object_url}}` | Parsed from SDK response | generated download URL |
| `{{output.presigned_url}}` | Parsed from SDK response | temporary access URL |
| `{{output.bucket_list}}` | Parsed from SDK response | from ListBuckets |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support OOS operations (verified: `ctyun oos` subcommand does not exist).
The primary path uses the OOS Python SDK (v6+). An alternative path uses
boto3 S3-compatible API with CTyun endpoints (see [`references/cli-usage.md`](references/cli-usage.md)).

### Pre-flight

1. Verify Python 3.10+ environment
2. Verify OOS SDK is installed (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Installation)
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and endpoint

### Flow A: List Buckets

**SDK path:**

```python
from oos_sdk.client import Client

client = Client(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="{{env.OOS_ENDPOINT}}",
    region="{{env.OOS_REGION_ID}}"
)
buckets = client.list_buckets()
```

**Validation:** Check response. Parse `$.Buckets[]`.

### Flow B: Create Bucket

```python
client.create_bucket(
    bucket_name="{{user.bucket_name}}",
    acl="{{user.acl}}"  # private | public-read | public-read-write
)
```

> **Note:** Bucket names must be globally unique across all CTyun OOS users.
> Naming rules: 3-63 characters, lowercase letters/numbers/hyphens, must
> start and end with a letter or number.

### Flow C: Delete Bucket

```python
client.delete_bucket(bucket_name="{{user.bucket_name}}")
```

> **Safety Gate:** This operation is IRREVERSIBLE. **REQUIRED**:
> 1. Confirm the bucket is empty (no objects)
> 2. Ask user explicitly: "Delete bucket `{{user.bucket_name}}` and all its contents? This cannot be undone."
> 3. Only proceed on explicit `yes` confirmation

### Flow D: List Objects

```python
objects = client.list_objects(
    bucket_name="{{user.bucket_name}}",
    prefix="{{user.object_key}}"  # optional prefix filter
)
```

### Flow E: Upload Object

```python
client.put_object(
    bucket_name="{{user.bucket_name}}",
    object_key="{{user.object_key}}",
    file_path="{{user.local_path}}",
    acl="{{user.acl}}"  # optional per-object ACL
)
```

### Flow F: Download Object

```python
client.get_object(
    bucket_name="{{user.bucket_name}}",
    object_key="{{user.object_key}}",
    file_path="{{user.local_path}}"
)
```

### Flow G: Delete Object

```python
client.delete_object(
    bucket_name="{{user.bucket_name}}",
    object_key="{{user.object_key}}"
)
```

> **Safety Gate:** Ask user to confirm before deleting objects, especially
> in production buckets.

### Flow H: Generate Pre-signed URL

```python
url = client.generate_presigned_url(
    bucket_name="{{user.bucket_name}}",
    object_key="{{user.object_key}}",
    method="get",                    # get | put
    expires_in={{user.expires_in}}   # seconds
)
```

---

## Output Parsing Rules

OOS API responses follow S3-compatible XML or JSON formats depending on the
SDK version. The Python SDK returns Python dicts.

| Operation | Data Key | Key Fields |
|---|---|---|
| List Buckets | `Buckets` | `Name, CreationDate` |
| Create Bucket | `Location` | `bucket_name, location` |
| Delete Bucket | `status` | `HTTPStatusCode: 204` |
| List Objects | `Contents[]` | `Key, Size, LastModified, ETag` |
| Upload Object | `ETag` | `ETag, HTTPStatusCode` |
| Download Object | `Body` | streamed to file |
| Delete Object | `status` | `HTTPStatusCode: 204` |
| Pre-signed URL | `url` | full temporary URL string |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `AccessDenied` / 403 | Business | No | Check credentials and bucket ACL |
| `NoSuchBucket` / 404 | Business | No | Verify bucket name exists |
| `BucketAlreadyExists` / 409 | Business | No | Bucket name taken; suggest alternative |
| `BucketNotEmpty` / 409 | Business | No | Empty bucket before deletion |
| `InvalidAccessKeyId` | Environment | 1x | Verify AK/SK or regenerate |
| `SignatureDoesNotMatch` | Environment | 1x | Check credentials and clock sync |
| `RequestTimeout` / 5xx | Runtime | 3x exponential backoff | Retry with backoff (2s, 4s, 8s) |
| SDK import error | Environment | 1x | Install OOS SDK (see api-sdk-usage.md) |
| `Endpoint` or connection error | Runtime | 2x | Verify endpoint URL and region |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Delete bucket/object can cause data loss |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete bucket/object operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-oos-ops skill — bucket CRUD, object CRUD, ACL, pre-signed URLs, lifecycle |
