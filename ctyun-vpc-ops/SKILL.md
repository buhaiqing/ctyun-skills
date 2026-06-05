---
name: ctyun-vpc-ops
description: >-
  Use when the user needs to deploy, configure, manage, troubleshoot, or monitor
  CTyun VPC (Virtual Private Cloud) resources via API, SDK, or the ctyun CLI. Trigger when
  the user mentions VPC, Virtual Private Cloud, 虚拟私有云, 专有网络, subnet, route table, peering connection,
  network ACL, or CIDR block in an operational context — even if they do not explicitly
  mention 'CTyun' or 'API'. Also use when the user asks about ctyun CLI
  commands, ctyun SDK usage, OpenAPI operations, or automation scripts for
  VPC. Do not use for billing-only or IAM-only tasks; delegate to the
  appropriate dedicated skill.
license: MIT
compatibility: >-
  Official CTyun SDK (e.g. Python 3.10+), valid API credentials, network
  access to CTyun endpoints, and official CTyun CLI (`ctyun`) when this
  product is supported by the CLI (dual-path skills).
metadata:
  author: ctyun
  version: "1.0.0"
  last_updated: "2026-06-05"
  runtime: Harness AI Agent
  api_profile: "CTyun VPC API v2.0"
  cli_applicability: sdk-only
  cli_support_evidence: >-
    Based on CTyun CLI documentation review, VPC operations are not exposed
    through the CLI. All operations must use SDK/API.
  environment:
    - CTYUN_ACCESS_KEY
    - CTYUN_SECRET_KEY
    - CTYUN_REGION
---

> This template follows the [Agent Skill OpenSpec](https://agentskills.io/specification).

# CTyun VPC (Virtual Private Cloud) Operations Skill

## Overview

VPC (Virtual Private Cloud) on CTyun provides isolated virtual network environments within the cloud. Users can create custom network spaces, configure IP address ranges, subnets, route tables, and network ACLs. This skill is an **operational runbook** for agents: explicit scope, credential rules, pre-flight checks, **SDK/API execution** (VPC is not supported by official `ctyun` CLI), response validation, and failure recovery. **Do not use the web console as the primary agent execution path** in `SKILL.md`.

### CLI applicability (repository policy)

- **`cli_applicability: sdk-only`:** Official `ctyun` does **not** expose VPC product. **Omit** `references/cli-usage.md`. SDK/API remains mandatory for all operations.

## Trigger & Scope (Agent-Readable)

### SHOULD Use This Skill When

- User mentions **VPC**, **Virtual Private Cloud**, **虚拟私有云**, **专有网络**
- User needs to **create**, **list**, **update**, or **delete** a VPC
- User needs to manage **subnets** within a VPC
- User needs to configure **route tables** and **routes**
- User needs to set up **VPC peering connections**
- User needs to manage **network ACLs** (security groups)
- User needs to **describe** VPC resources or **query** VPC status
- User asks about **CIDR blocks**, **IP address ranges**, or **network segmentation**

### SHOULD NOT Use This Skill When

- User asks about **load balancers** → delegate to `ctyun-elb-ops`
- User asks about **elastic IPs** → delegate to `ctyun-eip-ops`
- User asks about **security groups** (EC2-level) → delegate to `ctyun-ecs-ops`
- User asks about **VPN connections** or **Direct Connect** → these are separate products
- User asks about **IAM policies** for VPC → delegate to `ctyun-iam-ops`
- User asks about **monitoring** VPC metrics → delegate to `ctyun-cloudmonitor-ops`

## Variable Convention

| Placeholder | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Runtime environment variable | `AKID...` |
| `{{env.CTYUN_SECRET_KEY}}` | Runtime environment variable | `SECRET...` |
| `{{env.CTYUN_REGION}}` | Runtime environment variable | `cn-gz` |
| `{{user.vpc_name}}` | Ask user once, cache for session | `my-production-vpc` |
| `{{user.cidr_block}}` | Ask user once, cache for session | `10.0.0.0/16` |
| `{{output.vpc_id}}` | Parse from JSON response | `vpc-12345678` |
| `{{output.subnet_id}}` | Parse from JSON response | `subnet-12345678` |
| `{{output.route_table_id}}` | Parse from JSON response | `rtb-12345678` |

**Never prompt for `{{env.*}}` variables** — they are resolved from the agent runtime.

**Ask for `{{user.*}}` only once per session** and reuse.

**Parse `{{output.*}}` from the JSON response** using `jq` or Python's `json.loads`.

## Pre-flight Environment Check

Before any VPC operation, run:

```bash
python3 scripts/preflight-check.py --verbose --fix
```

This checks:
1. ✅ Python 3.10+ compatibility
2. ✅ `ctyun-cli` installation (creates `ctyun` symlink if missing)
3. ✅ Credential configuration (`.env`, `~/.ctyun/config`, or env vars)
4. ✅ Basic CLI functionality

**Note:** For VPC operations, we rely on SDK/API as CLI does not support VPC.

## Execution Flows

### 1. Create VPC

**Inputs:** `{{user.vpc_name}}`, `{{user.cidr_block}}`, `{{user.description}}` (optional)

**Steps:**

1. **Validate inputs**: CIDR must be valid RFC 1918 private range (e.g., `10.0.0.0/16`, `172.16.0.0/12`, `192.168.0.0/16`)
2. **Call SDK**:
   ```python
   from ctyun_sdk import CtyunClient
   
   client = CtyunClient(
       access_key='{{env.CTYUN_ACCESS_KEY}}',
       secret_key='{{env.CTYUN_SECRET_KEY}}',
       region='{{env.CTYUN_REGION}}'
   )
   
   response = client.vpc.create_vpc(
       name='{{user.vpc_name}}',
       cidr_block='{{user.cidr_block}}',
       description='{{user.description}}'
   )
   ```
3. **Parse response**: Extract `vpc_id` from `response['Vpc']['VpcId']`
4. **Validate**: Ensure VPC state is `available` (poll if needed)
5. **Output**: `{{output.vpc_id}}`, `{{output.vpc_name}}`, `{{output.cidr_block}}`, `{{output.state}}`

**Safety gate:** Creating VPC is non-destructive but consumes quota. Confirm with user if quota is limited.

### 2. List VPCs

**Inputs:** None (or optional filters)

**Steps:**

1. **Call SDK**:
   ```python
   response = client.vpc.describe_vpcs(
       vpc_ids=[],  # empty list returns all
       filters=[],  # optional filters
       max_results=100
   )
   ```
2. **Parse response**: Extract VPC list from `response['Vpcs']`
3. **Format output**: Table with columns: `VpcId`, `Name`, `CidrBlock`, `State`, `CreationTime`
4. **Output**: List of VPC objects

### 3. Delete VPC

**Inputs:** `{{user.vpc_id}}`

**Steps:**

1. **Validate**: Check VPC exists and is not in use (no resources attached)
2. **Safety gate**: **REQUIRES EXPLICIT USER CONFIRMATION** - "Are you sure you want to delete VPC {{user.vpc_id}}? This action cannot be undone."
3. **Call SDK**:
   ```python
   response = client.vpc.delete_vpc(vpc_id='{{user.vpc_id}}')
   ```
4. **Verify**: Poll until VPC state is `deleted` or returns 404
5. **Output**: Confirmation message with `request_id`

### 4. Create Subnet

**Inputs:** `{{user.vpc_id}}`, `{{user.subnet_cidr}}`, `{{user.zone}}`, `{{user.subnet_name}}`

**Steps:**

1. **Validate**: Subnet CIDR must be within VPC CIDR range
2. **Call SDK**:
   ```python
   response = client.vpc.create_subnet(
       vpc_id='{{user.vpc_id}}',
       cidr_block='{{user.subnet_cidr}}',
       zone='{{user.zone}}',
       name='{{user.subnet_name}}'
   )
   ```
3. **Parse response**: Extract `subnet_id` from `response['Subnet']['SubnetId']`
4. **Validate**: Ensure subnet state is `available`
5. **Output**: `{{output.subnet_id}}`, `{{output.cidr_block}}`, `{{output.zone}}`, `{{output.state}}`

### 5. Configure Route Table

**Inputs:** `{{user.vpc_id}}`, `{{user.route_table_name}}`, `{{user.routes}}` (list of destination/target)

**Steps:**

1. **Create route table**:
   ```python
   response = client.vpc.create_route_table(
       vpc_id='{{user.vpc_id}}',
       name='{{user.route_table_name}}'
   )
   route_table_id = response['RouteTable']['RouteTableId']
   ```
2. **Add routes**:
   ```python
   for route in {{user.routes}}:
       client.vpc.create_route(
           route_table_id=route_table_id,
           destination_cidr_block=route['destination'],
           gateway_id=route['target']
       )
   ```
3. **Associate with subnet** (optional):
   ```python
   client.vpc.associate_route_table(
       route_table_id=route_table_id,
       subnet_id='{{user.subnet_id}}'
   )
   ```
4. **Output**: `{{output.route_table_id}}`, `{{output.route_count}}`

### 6. Create VPC Peering Connection

**Inputs:** `{{user.requester_vpc_id}}`, `{{user.accepter_vpc_id}}`, `{{user.peer_region}}` (optional)

**Steps:**

1. **Validate**: Both VPCs exist and are in same region (or cross-region if supported)
2. **Call SDK**:
   ```python
   response = client.vpc.create_vpc_peering_connection(
       requester_vpc_id='{{user.requester_vpc_id}}',
       accepter_vpc_id='{{user.accepter_vpc_id}}',
       peer_region='{{user.peer_region}}' if '{{user.peer_region}}' else None
   )
   ```
3. **Parse response**: Extract `vpc_peering_connection_id`
4. **Accept connection** (if cross-account or manual acceptance required):
   ```python
   client.vpc.accept_vpc_peering_connection(
       vpc_peering_connection_id=vpc_peering_connection_id
   )
   ```
5. **Update route tables** on both VPCs to route traffic
6. **Output**: `{{output.vpc_peering_connection_id}}`, `{{output.status}}`

## Output Parsing Rules

| Operation | JSON Path | Output Variable |
|---|---|---|
| Create VPC | `$.Vpc.VpcId` | `{{output.vpc_id}}` |
| List VPCs | `$.Vpcs` | Array of VPC objects |
| Delete VPC | `$.RequestId` | `{{output.request_id}}` |
| Create Subnet | `$.Subnet.SubnetId` | `{{output.subnet_id}}` |
| Create Route Table | `$.RouteTable.RouteTableId` | `{{output.route_table_id}}` |
| Create VPC Peering | `$.VpcPeeringConnection.VpcPeeringConnectionId` | `{{output.vpc_peering_connection_id}}` |

**Always validate** the response contains expected fields before using `{{output.*}}`.

## Failure Recovery

| Error Pattern | Retry Count | Backoff | Agent Action |
|---|---|---|---|
| `InvalidParameter` | 0 | N/A | Fix parameter and retry once |
| `VpcLimitExceeded` | 0 | N/A | Ask user to delete unused VPCs or request quota increase |
| `InsufficientAddresses` | 0 | N/A | Choose larger CIDR or different range |
| `DependencyViolation` | 3 | 2s, 4s, 8s | Wait for dependent resource deletion |
| `InternalError` | 3 | 1s, 2s, 4s | Retry with exponential backoff |
| `RequestTimeout` | 3 | 2s, 4s, 8s | Retry with longer timeout |
| `AccessDenied` | 0 | N/A | Check IAM permissions, delegate to `ctyun-iam-ops` |

**Critical**: If `DeleteVpc` fails with `DependencyViolation`, list dependencies first, ask user to delete them, then retry.

## Safety Gates

**P0 (ABORT if missing):**

- `DeleteVpc`: **MUST** have explicit user confirmation
- `DeleteSubnet`: **MUST** confirm subnet is not in use
- `DeleteRouteTable`: **MUST** confirm no subnets associated

**P1 (warn but continue):**

- `CreateVpc` when near quota limit
- `CreateSubnet` with small CIDR (less than /28)
- `CreateRoute` with `0.0.0.0/0` destination (default route)

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override `AGENTS.md` §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | VPC operations are network-critical; delete operations are destructive |
| `max_iterations` | `3` | Standard for destructive operations |
| `rubric_version` | `v1` | see `references/rubric.md` |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | `true` for delete operations |
| `fallback_decision_table` | `references/cli-decision-matrix.md` | SDK-only skill, no CLI fallback needed |

### Artifacts (must exist alongside this SKILL.md)

- `references/rubric.md` — the concrete scoring rules
- `references/prompt-templates.md` — G / C / O prompt skeletons
- `references/core-concepts.md` — VPC concepts and architecture
- `references/api-sdk-usage.md` — SDK usage examples
- `references/troubleshooting.md` — common issues and solutions
- `references/monitoring.md` — monitoring and metrics
- `references/integration.md` — integration with other services

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial VPC skill with create/list/delete VPC, subnet management, route tables, and VPC peering |