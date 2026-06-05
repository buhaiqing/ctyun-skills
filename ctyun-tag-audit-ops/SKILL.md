---
name: ctyun-tag-audit-ops
version: "1.0.0"
description: >-
  Audit and analyze resource tags across CTyun cloud resources. Query tagged
  resources, find untagged resources, enforce tagging compliance, and generate
  tag inventory reports. Read-only — does not create or modify tags.
license: MIT
compatibility: Python 3.10+, valid API credentials, network access to CTyun endpoints
metadata:
  author: ctyun
  version: "1.0.0"
  last_updated: "2026-06-05"
  runtime: Harness AI Agent
  api_profile: "CTyun Tag Management API v1.0"
  cli_applicability: sdk-only
  cli_support_evidence: >-
    Tag audit requires cross-resource queries not available via CLI.
  environment:
    - CTYUN_ACCESS_KEY
    - CTYUN_SECRET_KEY
    - CTYUN_REGION
---

# CTyun Tag Audit Operations Skill

## Overview

Tag Audit provides read-only access to CTyun resource tagging data. It queries
tagged resources across services, identifies compliance gaps (untagged or
incorrectly tagged resources), and generates tag inventory reports.

## Trigger & Scope

### SHOULD Use This Skill When

- User asks to "audit tags", "find untagged resources", or "check tag compliance"
- User needs a tag inventory report across all resources
- User asks "which resources have tag X" or "show me resources without tags"
- Keywords: tag audit, tag compliance, tag inventory, resource tagging

### SHOULD NOT Use This Skill When

- User asks to **create, modify, or delete** tags → delegate to resource-specific skills
- User asks about **IAM policies** → delegate to `ctyun-iam-ops`
- User asks about **cost allocation by tag** → not supported

## Variable Convention

| Placeholder | Resolution | Example |
|-------------|------------|---------|
| `{{env.CTYUN_ACCESS_KEY}}` | Runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Runtime env | never prompt |
| `{{env.CTYUN_REGION}}` | Runtime env | `cn-gz` |
| `{{user.tag_key}}` | Ask user once | `environment` |
| `{{user.tag_value}}` | Ask user once | `production` |
| `{{user.resource_type}}` | Ask user once | `ecs`, `rds` |

## Execution Flows

### Operation: ListTaggedResources

1. Call SDK to query resources by tag:
   ```python
   from ctyun_sdk import CtyunClient
   client = CtyunClient(access_key, secret_key, region)
   resources = client.tag.list_resources_by_tag(
       tag_key="{{user.tag_key}}",
       tag_value="{{user.tag_value}}",
   )
   ```
2. Parse response: extract resource list with `resourceId`, `resourceType`, `tags`
3. Return structured list

### Operation: FindUntaggedResources

1. Query available resource types (ECS, RDS, VPC, etc.)
2. For each type, list resources and filter those with no tags
3. Return untagged resource inventory

### Operation: GenerateTagReport

1. Query tags across all resources in the account/region
2. Compile: tag usage statistics, untagged resources, compliance score
3. Return Markdown-formatted tag audit report

## Output Parsing Rules

| Operation | Key Field | Description |
|-----------|-----------|-------------|
| ListTaggedResources | `resources[]` | Resources matching tag filter |
| FindUntaggedResources | `untagged[]` | Resources with no tags |
| GenerateTagReport | `report` | Tag audit summary |

## Failure Recovery

| Error Pattern | Retry | Agent Action |
|---------------|-------|--------------|
| `InvalidParameter` | 0 | Fix tag key/value |
| `AccessDenied` | 0 | Delegate to `ctyun-iam-ops` |
| Cross-resource timeout | 2 (2s, 4s) | Retry with narrower scope |

## Quality Gate (GCL)

| Parameter | Value | Reason |
|-----------|-------|--------|
| `gcl_mode` | `optional` | read-only |
| `max_iterations` | `5` | report quality can improve |
| `rubric_version` | `v1` | see `references/rubric.md` |
| `safety_confirm_required` | `false` | all operations read-only |

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-05 | Initial tag audit skill — list tagged resources, find untagged, generate reports |