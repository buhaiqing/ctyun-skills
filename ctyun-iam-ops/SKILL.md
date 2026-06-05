---
name: ctyun-iam-ops
version: 1.0.0
description: >
  Manage CTyun IAM (Identity and Access Management) resources —
  users, groups, policies, roles, access keys, enterprise projects,
  MFA devices, and identity providers. Primary route for any IAM
  or identity/access control task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.20.0"
  sdk_version_locked: ">=1.0.0"
  api_profile: iam.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-iam-ops

## Trigger & Scope

### SHOULD Use

- Create, list, describe, or delete IAM users
- Create, list, describe, or delete IAM user groups
- Add or remove users from groups
- Create, list, describe, or delete IAM policies (system & custom)
- Attach or detach policies to/from groups
- Create, list, update, or delete access keys (AK/SK) for IAM users
- Create, list, or delete IAM roles
- List and manage enterprise projects
- List identity providers
- Manage MFA devices (SDK-only)
- Any IAM-related troubleshooting (user not found, permission denied, policy syntax)

### SHOULD NOT Use

- Cloud monitor alarm rule configuration → delegate to `ctyun-cloudmonitor-ops`
- KMS key management (key creation, rotation, encryption) → delegate to `ctyun-kms-ops` (planned)
- Audit log query for IAM events → delegate to `ctyun-audit-ops` (planned)
- Resource tagging → delegate to `ctyun-tag-audit-ops` (planned)
- ECS instance operations → delegate to `ctyun-ecs-ops`
- RDS instance operations → delegate to `ctyun-rds-ops` (planned)

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "IAM user" or "create user" | Route here |
| User asks about "IAM group" or "user group" | Route here |
| User asks about "policy" or "permission" | Route here |
| User asks about "access key" or "AK/SK" | Route here |
| User asks about "IAM role" | Route here |
| User asks about "enterprise project" | Route here |
| User asks about "identity provider" or "federation" | Route here |
| User asks about "MFA" or "multi-factor" | Route here |
| User asks about "monitor alarm" | Route to `ctyun-cloudmonitor-ops` |
| User asks about "KMS key" | Route to `ctyun-kms-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_ACCOUNT_ID}}` | Agent runtime env | `790251264ec0480e91b9b17` |
| `{{user.account_id}}` | Ask once, cache per session | `790251264ec0480e91b9b17` |
| `{{user.user_name}}` | Ask once, cache per session | `svc-deploy` |
| `{{user.group_name}}` | Ask once, cache per session | `DevOps` |
| `{{user.policy_name}}` | Ask once, cache per session | `ECSAccessPolicy` |
| `{{user.policy_document}}` | Ask once, cache per session | JSON policy string |
| `{{user.role_name}}` | Ask once, cache per session | `ECSCrossAccountRole` |
| `{{user.access_key_id}}` | Ask once, cache per session | `AKID1234567890` |
| `{{output.user_id}}` | Parsed from JSON output | from create-user result |
| `{{output.group_id}}` | Parsed from JSON output | from create-group result |
| `{{output.policy_id}}` | Parsed from JSON output | from create-policy result |
| `{{output.access_key_secret}}` | Parsed from JSON output | from create-access-key (shown once) |
| `{{output.project_id}}` | Parsed from JSON output | from list-projects result |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy defined in
[`AGENTS.md`](../AGENTS.md#execution-strategy).

### Pre-flight (shared)

1. Verify `ctyun` CLI is installed (`ctyun --version`; require >= 1.20.0 for full IAM support)
2. Verify credentials configured (`test -n "$CTYUN_ACCESS_KEY"` and `test -n "$CTYUN_SECRET_KEY"`)
3. Determine `{{user.account_id}}` — from env `CTYUN_ACCOUNT_ID` or ask user if not set
4. Set `CTYUN_FORCE_CLI=1` or `CTYUN_FORCE_SDK=1` if overrides present

### Flow A: List / Get Enterprise Projects

**CLI path (primary):**

```bash
ctyun --output json iam list-projects \
  --account-id {{user.account_id}} \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

```bash
ctyun --output json iam get-project --project-id {{user.project_id}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.iam import IAMClient

client = IAMClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
projects = client.list_enterprise_projects(
    account_id="{{user.account_id}}",
    current_page={{user.page_no|default(1)}},
    page_size={{user.page_size|default(20)}}
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj.recordList[]`.

### Flow B: List IAM Users

**CLI path (primary):**

```bash
ctyun --output json iam list-users \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

**SDK fallback:**

```python
client = IAMClient(...)
users = client.list_users(
    page_no={{user.page_no|default(1)}},
    page_size={{user.page_size|default(20)}}
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj[]`.

### Flow C: Create IAM User

**CLI path (primary):**

```bash
ctyun --output json iam create-user \
  --user-name {{user.user_name}} \
  {{user.tags|default("")}}
```

**SDK fallback:**

```python
client = IAMClient(...)
result = client.create_user(
    user_name="{{user.user_name}}"
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for `UserId`, `Arn`.
**Idempotency:** User name must be unique within the account. Duplicate names fail.

### Flow D: Delete IAM User

**CLI path (primary):**

```bash
ctyun --output json iam delete-user \
  --user-name {{user.user_name}}
```

**Safety Gate (CRITICAL):** Before deletion, MUST:
1. Warn that this is **IRREVERSIBLE**
2. Check if user has active access keys, group memberships, or MFA devices
3. Get explicit user confirmation

> "Delete IAM user '{{user.user_name}}'? This is IRREVERSIBLE.
> The user must first be removed from all groups and all access keys must be deleted.
> Type 'yes' to confirm:"

### Flow E: List / Get IAM Groups

**CLI path (primary):**

```bash
ctyun --output json iam list-groups \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

```bash
ctyun --output json iam get-group --group-name {{user.group_name}}
```

### Flow F: Create IAM Group

**CLI path (primary):**

```bash
ctyun --output json iam create-group \
  --group-name {{user.group_name}}
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for `GroupId`, `Arn`.

### Flow G: Delete IAM Group

**CLI path (primary):**

```bash
ctyun --output json iam delete-group \
  --group-name {{user.group_name}}
```

**Safety Gate (CRITICAL):** Before deletion:
1. Check if group has attached policies or contains users
2. Warn that deletion is IRREVERSIBLE
3. Get explicit user confirmation

> "Delete IAM group '{{user.group_name}}'? This is IRREVERSIBLE.
> All policies and users must first be removed from the group.
> Type 'yes' to confirm:"

### Flow H: Add / Remove User from Group

**Add user:**

```bash
ctyun --output json iam add-user-to-group \
  --user-name {{user.user_name}} \
  --group-name {{user.group_name}}
```

**Remove user:**

```bash
ctyun --output json iam remove-user-from-group \
  --user-name {{user.user_name}} \
  --group-name {{user.group_name}}
```

### Flow I: List / Get Policies

**CLI path (primary):**

```bash
ctyun --output json iam list-policies \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}} \
  --scope {{user.policy_scope|default("All")}}
```

```bash
ctyun --output json iam get-policy --policy-name {{user.policy_name}}
```

### Flow J: Create Custom Policy

**CLI path (primary):**

```bash
ctyun --output json iam create-policy \
  --policy-name {{user.policy_name}} \
  --policy-document '{{user.policy_document}}' \
  --description "{{user.policy_description|default('')}}"
```

**SDK fallback:**

```python
client = IAMClient(...)
result = client.create_policy(
    policy_name="{{user.policy_name}}",
    policy_document="{{user.policy_document}}",
    description="{{user.policy_description|default('')}}"
)
```

**Validation:** Check `$.statusCode == 800`. Parse `$.returnObj` for `PolicyId`, `Arn`.

### Flow K: Delete Custom Policy

**CLI path (primary):**

```bash
ctyun --output json iam delete-policy \
  --policy-name {{user.policy_name}}
```

**Safety Gate (CRITICAL):** Before deletion:
1. Check policy is not attached to any group
2. Warn that deletion is IRREVERSIBLE
3. Get explicit user confirmation

> "Delete custom policy '{{user.policy_name}}'? This is IRREVERSIBLE.
> Type 'yes' to confirm:"

### Flow L: Attach / Detach Policy to/from Group

**Attach:**

```bash
ctyun --output json iam attach-group-policy \
  --policy-name {{user.policy_name}} \
  --group-name {{user.group_name}}
```

**Detach:**

```bash
ctyun --output json iam detach-group-policy \
  --policy-name {{user.policy_name}} \
  --group-name {{user.group_name}}
```

**Validation:** Check `$.statusCode == 800`.

### Flow M: List Attached Group Policies

```bash
ctyun --output json iam list-attached-group-policies \
  --group-name {{user.group_name}}
```

### Flow N: Access Key Management

**List keys:**

```bash
ctyun --output json iam list-access-keys \
  --user-name {{user.user_name}}
```

**Create key:**

```bash
ctyun --output json iam create-access-key \
  --user-name {{user.user_name}}
```

> **Important:** The secret key is displayed only once. Save it immediately.

**Update key status:**

```bash
ctyun --output json iam update-access-key \
  --user-name {{user.user_name}} \
  --access-key-id {{user.access_key_id}} \
  --status {{user.access_key_status}}
```

**Delete key:**

```bash
ctyun --output json iam delete-access-key \
  --user-name {{user.user_name}} \
  --access-key-id {{user.access_key_id}}
```

**Safety Gate (CRITICAL):** Before key deletion:
> "Delete access key '{{user.access_key_id}}' for user '{{user.user_name}}'?
> Any service using this key will lose access immediately. Type 'yes' to confirm:"

### Flow O: Role Management

**List roles:**

```bash
ctyun --output json iam list-roles \
  --page {{user.page_no|default(1)}} \
  --page-size {{user.page_size|default(20)}}
```

**Create role:**

```bash
ctyun --output json iam create-role \
  --role-name {{user.role_name}} \
  --trust-policy '{{user.trust_policy}}' \
  --description "{{user.role_description|default('')}}"
```

**Delete role:**

```bash
ctyun --output json iam delete-role \
  --role-name {{user.role_name}}
```

**Safety Gate (CRITICAL):** Before role deletion:
> "Delete IAM role '{{user.role_name}}'? This is IRREVERSIBLE.
> Services assuming this role will lose access. Type 'yes' to confirm:"

---

## Output Parsing Rules

All CLI responses follow the CTyun API envelope format:

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... },
  "_mock": false
}
```

### Common JSON Paths

| Operation | Data Path | Key Fields |
|---|---|---|
| List projects | `$.returnObj.recordList[]` | `projectId, projectName, description, status, createTime` |
| List users | `$.returnObj[]` | `userId, userName, mobile, email, createDate, enabled` |
| Get user | `$.returnObj` | `userId, userName, arn, createDate, tags{}` |
| Create user | `$.returnObj` | `userId, arn` |
| List groups | `$.returnObj[]` | `groupId, groupName, arn, createDate` |
| Get group | `$.returnObj` | `groupId, groupName, arn, createDate, users[].userName` |
| Create group | `$.returnObj` | `groupId, groupName, arn` |
| List policies | `$.returnObj[]` | `policyId, policyName, policyType, description, attachmentCount` |
| Get policy | `$.returnObj` | `policyId, policyName, policyType, description, policyDocument, attachmentCount` |
| List access keys | `$.returnObj[]` | `accessKeyId, status, createDate` |
| Create access key | `$.returnObj` | `accessKeyId, secretAccessKey, status, createDate` |
| List roles | `$.returnObj[]` | `roleId, roleName, description, createDate` |

### State Transition Table

| Operation | Previous State | Expected Next State |
|---|---|---|
| Create user | — | `Active` |
| Delete user | any | removed |
| Create group | — | exists |
| Delete group | any | removed |
| Create policy | — | exists |
| Delete policy | any | removed |
| Update AK status | `Active` | `Inactive` |
| Update AK status | `Inactive` | `Active` |
| Delete AK | any | removed |
| Add user to group | user not in group | user in group |
| Remove user from group | user in group | user not in group |

---

## Failure Recovery

### Error Pattern Table

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` to user |
| `ctyun: command not found` | Environment | 3x | (re)install: `pip install ctyun-cli>=1.20.0` |
| `not authenticated` / `401` | Credentials | 3x | Check `CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY` env vars; rewrite `~/.ctyun/config` |
| `5xx` / timeout / non-JSON | Runtime | 1x, then fallback | Retry once; if fails → SDK fallback for that operation |
| `subcommand not found` | Capability | No fallback | Check CLI version; upgrade: `pip install --upgrade ctyun-cli` |
| `CTIAM_*` error codes | Business | No | Surface the specific IAM error code and message |

### Common IAM Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `CTIAM_0113` | accountId mismatch in header vs body | Verify `--account-id` is the correct account ID (not Access Key) |
| `CTIAM_0202` (user exists) | Duplicate user name | Choose a different user name |
| `CTIAM_0302` (group exists) | Duplicate group name | Choose a different group name |
| `HTTP_403` | Insufficient permissions | Must use main account or request elevated privileges |
| Policy validation failure | Malformed JSON or invalid Action | Validate JSON; use correct `service:Operation` format |

---

## Prerequisites

### Environment

```bash
# Python 3.10+
pip install ctyun-cli>=1.20.0

# Verify
ctyun --version
```

### Credentials (two methods)

**Method A — Environment variables (recommended):**

```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
export CTYUN_ACCOUNT_ID=your_account_id  # for enterprise project ops
```

**Method B — CLI config file:**

```bash
ctyun config init
# OR write manually:
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = {{env.CTYUN_REGION_ID|default("cn-gz")}}
endpoint = iam.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

> **CRITICAL:** The `ctyun` CLI reads credentials from `~/.ctyun/config` INI file,
> NOT from environment variables. The SDK reads from `CTYUN_ACCESS_KEY`/
> `CTYUN_SECRET_KEY` env vars. Both paths must be configured.

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | delete user/group/policy/role/AK are destructive IAM operations |
| `max_iterations` | `2` | inherited from §8 IAM default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with audit skills |
| `safety_confirm_required` | `true` | delete user/group/policy/role/AK are irreversible |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first policy matrix |

### Artifacts

- [`references/rubric.md`](references/rubric.md) — concrete scoring rules
- [`references/prompt-templates.md`](references/prompt-templates.md) — G/C/O prompt skeletons

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-iam-ops skill — user/group/policy/role/AK/enterprise-project/MFA operations |
