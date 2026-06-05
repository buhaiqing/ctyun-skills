# CTyun IAM CLI Usage

> Source of truth: `ctyun iam --help` and `ctyun-cli` v1.20.0+.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.20.0`.
>
> IAM CLI support was introduced in v1.2.0 and significantly expanded in v1.20.0
> (34 commands across 12 functional categories).

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json iam list-projects ...` |
| `--output yaml` | Before subcommand | `ctyun --output yaml iam get-project ...` |

> The CTyun CLI does NOT support `--no-interactive`. Destructive operation
> confirmations are handled via application-level safety gates (see SKILL.md).

---

## IAM Commands

### `iam list-projects` — List enterprise projects

```bash
ctyun --output json iam list-projects \
  --account-id <account_id> \
  [--page <page_no>] \
  [--page-size <page_size>]
```

Output fields: `projectId, projectName, description, status, createTime`

### `iam get-project` — Get enterprise project details

```bash
ctyun --output json iam get-project \
  --project-id <project_id>
```

Output fields: `projectId, projectName, description, status, createTime`

### `iam list-users` — List IAM users

```bash
ctyun --output json iam list-users \
  [--page <page_no>] \
  [--page-size <page_size>]
```

Output fields: `userId, userName, mobile, email, createDate, enabled`

### `iam get-user` — Get IAM user details

```bash
ctyun --output json iam get-user \
  --user-name <user_name>
```

Output fields: `userId, userName, arn, createDate, tags{}`

### `iam create-user` — Create IAM user

```bash
ctyun --output json iam create-user \
  --user-name <user_name> \
  [--tags "Key=value,Key2=value2"]
```

### `iam delete-user` — Delete IAM user

**Safety Gate required.** See SKILL.md.

```bash
ctyun --output json iam delete-user \
  --user-name <user_name>
```

### `iam list-groups` — List IAM groups

```bash
ctyun --output json iam list-groups \
  [--page <page_no>] \
  [--page-size <page_size>]
```

Output fields: `groupId, groupName, arn, createDate`

### `iam get-group` — Get IAM group details

```bash
ctyun --output json iam get-group \
  --group-name <group_name>
```

Output fields: `groupId, groupName, arn, createDate, users[].userName`

### `iam create-group` — Create IAM group

```bash
ctyun --output json iam create-group \
  --group-name <group_name>
```

### `iam delete-group` — Delete IAM group

**Safety Gate required.** See SKILL.md.

```bash
ctyun --output json iam delete-group \
  --group-name <group_name>
```

### `iam add-user-to-group` — Add user to group

```bash
ctyun --output json iam add-user-to-group \
  --user-name <user_name> \
  --group-name <group_name>
```

### `iam remove-user-from-group` — Remove user from group

```bash
ctyun --output json iam remove-user-from-group \
  --user-name <user_name> \
  --group-name <group_name>
```

### `iam list-policies` — List policies

```bash
ctyun --output json iam list-policies \
  [--page <page_no>] \
  [--page-size <page_size>] \
  [--scope All|System|Custom]
```

Output fields: `policyId, policyName, policyType, description, attachmentCount, createDate`

### `iam get-policy` — Get policy details

```bash
ctyun --output json iam get-policy \
  --policy-name <policy_name>
```

Output fields: `policyId, policyName, policyType, description, policyDocument, attachmentCount`

### `iam create-policy` — Create custom policy

```bash
ctyun --output json iam create-policy \
  --policy-name <policy_name> \
  --policy-document <json_string_or_file> \
  [--description "<description>"]
```

### `iam delete-policy` — Delete custom policy

**Safety Gate required.** See SKILL.md.

```bash
ctyun --output json iam delete-policy \
  --policy-name <policy_name>
```

### `iam attach-group-policy` — Attach policy to group

```bash
ctyun --output json iam attach-group-policy \
  --policy-name <policy_name> \
  --group-name <group_name>
```

### `iam detach-group-policy` — Detach policy from group

```bash
ctyun --output json iam detach-group-policy \
  --policy-name <policy_name> \
  --group-name <group_name>
```

### `iam list-attached-group-policies` — List policies attached to group

```bash
ctyun --output json iam list-attached-group-policies \
  --group-name <group_name>
```

### `iam list-access-keys` — List access keys for a user

```bash
ctyun --output json iam list-access-keys \
  --user-name <user_name>
```

Output fields: `accessKeyId, status, createDate`

### `iam create-access-key` — Create access key

```bash
ctyun --output json iam create-access-key \
  --user-name <user_name>
```

> **Warning:** The secret key is only shown once in the response. Save it immediately.

### `iam update-access-key` — Update access key status

Update the status of an access key (Active / Inactive).

```bash
ctyun --output json iam update-access-key \
  --user-name <user_name> \
  --access-key-id <access_key_id> \
  --status Active|Inactive
```

### `iam delete-access-key` — Delete access key

**Safety Gate required.** See SKILL.md.

```bash
ctyun --output json iam delete-access-key \
  --user-name <user_name> \
  --access-key-id <access_key_id>
```

### `iam list-roles` — List IAM roles

```bash
ctyun --output json iam list-roles \
  [--page <page_no>] \
  [--page-size <page_size>]
```

### `iam create-role` — Create IAM role

```bash
ctyun --output json iam create-role \
  --role-name <role_name> \
  --trust-policy <json_policy> \
  [--description "<description>"]
```

### `iam delete-role` — Delete IAM role

**Safety Gate required.** See SKILL.md.

```bash
ctyun --output json iam delete-role \
  --role-name <role_name>
```

### `iam list-id-providers` — List identity providers

```bash
ctyun --output json iam list-id-providers
```

---

## Non-Obvious Flags

| Command | Flag | Note |
|---|---|---|
| `list-projects` | `--account-id` | This is the **account ID** (not AK), a string like `790251264ec0480e91b9b17` |
| `list-projects` | `--page` / `--page-size` | Pagination for large project lists |
| `create-policy` | `--policy-document` | Accepts JSON string or file path; must follow CTyun IAM policy schema |
| `create-access-key` | (none) | Secret key appears only once in response |
| `update-access-key` | `--status` | Only `Active` or `Inactive` are valid values |
| `list-users` | `--page` / `--page-size` | Pagination for large user lists |

## CLI Coverage Summary

| Functional Category | CLI Support | Fallback |
|---|---|---|
| Enterprise Project | ✅ list-projects, get-project | SDK for advanced ops |
| User Management | ✅ full CRUD | — |
| Group Management | ✅ full CRUD | — |
| Policy Management | ✅ full CRUD | — |
| Access Key Management | ✅ full CRUD | — |
| Role Management | ✅ list, create, delete | SDK for update |
| Identity Provider | ✅ list | SDK for create/update/delete |
| MFA Management | ❌ | SDK only |

> CLI commands for MFA and identity provider management are available in
> ctyun-cli >=1.20.0. For older versions, fall back to SDK.
