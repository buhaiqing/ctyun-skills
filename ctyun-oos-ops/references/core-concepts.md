# OOS Core Concepts

## Overview

CTyun **OOS (对象存储 经典版Ⅰ型)** — Object-Oriented Storage — provides
S3-compatible, highly durable, cost-effective cloud object storage for
unstructured data (images, videos, backups, logs, archives).

OOS uses an S3-compatible REST API, meaning most S3-compatible tools
(AWS CLI, boto3, MinIO Client) can be used with CTyun endpoints.

## Storage Architecture

```
OOS Account
  └── Bucket (container, globally unique name)
        └── Object (file + metadata, key-based)
              ├── Data (the actual file content)
              ├── Key (the object name/path)
              ├── Metadata (key-value pairs)
              └── ACL (access control)
```

### Buckets

| Property | Constraint |
|---|---|
| Name uniqueness | **Globally unique** across all CTyun OOS users |
| Name length | 3 — 63 characters |
| Name characters | Lowercase letters, digits, hyphens (`-`) |
| Name start/end | Must start and end with a letter or digit |
| Buckets per account | Up to 100 (default, quota can be raised) |
| Objects per bucket | Unlimited |

### Objects

| Property | Constraint |
|---|---|
| Key length | 1 — 1024 bytes (UTF-8 encoded) |
| Key characters | Any valid UTF-8, avoid characters requiring URL encoding |
| Max object size | 5 TB (single PUT ≤ 5 GB; larger via multipart upload) |
| Min object size | 0 bytes (empty object) |

## Access Control

### Bucket-level ACL

| ACL | Description |
|---|---|
| `private` | Only the bucket owner has read/write access (default) |
| `public-read` | Anyone can list/read objects; owner alone can write |
| `public-read-write` | Anyone can read/write; **use with extreme caution** |

### Object-level ACL

Objects inherit their bucket's ACL by default, but individual objects can
have a different ACL set at upload time or updated later.

## S3 Compatibility

OOS supports the S3 REST API standard. This means:

- **boto3** (AWS SDK for Python) can be configured with CTyun endpoints
- **AWS CLI** can be configured with CTyun endpoints
- **MinIO Client (mc)** can be used
- Most S3-compatible tools work with minimal configuration changes

> **Key difference:** OOS Classic supports only **S3 v2 signature** (not v4).
> When configuring S3-compatible tools, set signature version to `s3v2`.

## Lifecycle

Bucket lifecycle policies allow automatic:

- **Expiration**: Delete objects after a specified number of days
- **Transition**: Move objects to lower-cost storage tiers (if supported)
- **AbortIncompleteMultipartUpload**: Clean up incomplete multipart uploads

Example lifecycle rule: "Delete objects in the `logs/` prefix after 90 days."

## Storage Tiers

| Tier | Durability | Use Case |
|---|---|---|
| Standard | 99.9999999999% (11 9s) | Frequently accessed data |
| Infrequent Access (IA) | 99.9999999999% (11 9s) | Backup, less frequent access |
| Archive | 99.9999999999% (11 9s) | Long-term archival (restore takes minutes-hours) |

## Pre-signed URLs

Pre-signed URLs grant temporary access to a specific object without sharing
credentials. Common uses:

- **GET pre-signed URL**: Allow anyone to download an object for a limited time
- **PUT pre-signed URL**: Allow anyone to upload an object to a specific key

## Related Services

- **CDN** — Accelerate object delivery via content distribution network
- **ECS** — Applications running on ECS can read/write OOS objects
- **Cloud Monitor** — Monitor bucket storage usage, request count, traffic
- **CloudTrail** — Record OOS API operations for audit

## Related CTyun Products

| Product | Description |
|---|---|
| **OOS (经典版Ⅰ型)** | Classic object storage, S3 v2 compatible (**this skill**) |
| **ZOS (原生版Ⅱ型)** | New-generation object storage, S3 v4 compatible |
| **OOS 融合版** | Hybrid deployment object storage |
