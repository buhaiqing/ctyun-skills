---
name: ctyun-kms-ops
version: 1.0.0
description: >
  Manage CTyun KMS (密钥管理服务) — Key Management Service for creating,
  enabling, disabling, scheduling deletion, and canceling deletion of
  cryptographic keys. Primary route for any encryption key task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.7.7"
  sdk_version_locked: ">=1.0.0"
  api_profile: kms.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-kms-ops

## Trigger & Scope

### SHOULD Use

- Create a new KMS key
- Describe and list KMS keys
- Enable or disable a key
- Schedule key deletion (with safety gate)
- Cancel scheduled key deletion
- View key metadata and rotation status
- Any encryption key management task

### SHOULD NOT Use

- Cloud monitor alarm rule configuration → delegate to `ctyun-cloudmonitor-ops`
- IAM user/policy management → delegate to `ctyun-iam-ops`
- ECS operations → delegate to `ctyun-ecs-ops`
- Load balancer operations → delegate to `ctyun-elb-ops`
- EIP operations → delegate to `ctyun-eip-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "KMS" or "key management" | Route here |
| User asks about "encryption key" | Route here |
| User asks about "CMK" or "customer master key" | Route here |
| User asks about "key deletion" | Route here (requires safety gate) |
| User asks about "monitor" or "alarm" | Route to `ctyun-cloudmonitor-ops` |
| User asks about "IAM" or "policy" | Route to `ctyun-iam-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | region ID |
| `{{user.key_id}}` | Ask once, cache per session | key UUID |
| `{{user.key_alias}}` | Ask once, cache per session | key alias |
| `{{user.key_description}}` | Ask once, cache per session | key description |
| `{{user.pending_window}}` | Ask once, cache per session | days before deletion (default 7) |
| `{{output.key_id}}` | Parsed from JSON | from create response |
| `{{output.key_state}}` | Parsed from JSON | enabled / disabled / pending_deletion |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy.

### Pre-flight

1. Verify `ctyun` CLI (>= 1.7.7)
2. Verify credentials
3. Determine region ID

### Flow A: List Keys

**CLI path (primary):**

```bash
ctyun --output json kms key list \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.kms import KMSClient

client = KMSClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
keys = client.list_keys(region_id="{{user.region_id}}")
```

**Validation:** Check `$.statusCode == 800`.

### Flow B: Describe Key

```bash
ctyun --output json kms key get \
  --region-id {{user.region_id}} \
  --key-id {{user.key_id}}
```

### Flow C: Create Key

```bash
ctyun --output json kms key create \
  --region-id {{user.region_id}} \
  --alias "{{user.key_alias}}" \
  --description "{{user.key_description}}"
```

### Flow D: Enable / Disable Key

```bash
ctyun --output json kms key enable \
  --region-id {{user.region_id}} \
  --key-id {{user.key_id}}

ctyun --output json kms key disable \
  --region-id {{user.region_id}} \
  --key-id {{user.key_id}}
```

### Flow E: Schedule Key Deletion

```bash
ctyun --output json kms key schedule-deletion \
  --region-id {{user.region_id}} \
  --key-id {{user.key_id}} \
  --pending-window {{user.pending_window}}
```

> **Safety Gate:** This operation is IRREVERSIBLE after the pending window
> expires. **REQUIRED**:
> 1. Display key metadata (alias, id, creation date)
> 2. List resources that depend on this key (if discoverable)
> 3. Ask user explicitly: "Schedule deletion of key `{{user.key_id}}` (alias: `{{user.key_alias}}`)? This is irreversible after `{{user.pending_window}}` days."
> 4. Only proceed on explicit `yes` confirmation

### Flow F: Cancel Scheduled Deletion

```bash
ctyun --output json kms key cancel-deletion \
  --region-id {{user.region_id}} \
  --key-id {{user.key_id}}
```

---

## Output Parsing Rules

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```

| Operation | Data Path | Key Fields |
|---|---|---|
| List keys | `$.returnObj[]` | `keyId, alias, keyState, createTime` |
| Describe key | `$.returnObj` | `keyId, alias, keyState, createTime, description` |
| Create key | `$.returnObj` | `keyId, alias, keyState` |
| Schedule deletion | `$.returnObj` | `keyId, keyState: pending_deletion, deletionDate` |
| Cancel deletion | `$.returnObj` | `keyId, keyState: enabled` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `ctyun: command not found` | Environment | 3x | `pip install ctyun-cli>=1.7.7` |
| `5xx` / timeout | Runtime | 1x, then SDK | Retry once; SDK fallback |
| `subcommand not found` | Capability | No | Check CLI version; SDK fallback |
| `KMS.KeyNotFound` | Business | No | Verify key ID exists |
| `KMS.KeyInUse` | Business | No | Surface and stop |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Schedule key deletion is irreversible |
| `max_iterations` | `2` | inherited from §8 KMS default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for schedule-deletion operations |
| `fallback_decision_table` | `references/cli-decision-matrix.md` (inline) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-kms-ops skill — create, enable, disable, schedule-deletion, cancel-deletion |
