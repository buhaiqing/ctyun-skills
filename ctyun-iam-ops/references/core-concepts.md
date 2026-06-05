# IAM Core Concepts

## Overview

CTyun **Identity and Access Management (IAM)** — 统一身份认证 — provides
fine-grained access control over CTyun cloud resources. IAM enables you to
create and manage **users**, **groups**, **roles**, **policies**, and
**enterprise projects** to securely control access to your cloud resources.

## IAM User (IAM用户)

An IAM user represents a person or service that needs access to your CTyun
resources. Each user has a unique name within the account and can be assigned
credentials (password, access key) for authentication.

**Key properties:** `UserName`, `UserId`, `Arn`, `CreateDate`, `Tags`

**User states:**

| State | Meaning |
|---|---|
| `Active` | User can authenticate and access authorized resources |
| `Inactive` | User exists but cannot authenticate |

## IAM User Group (IAM用户组)

A group is a collection of IAM users. Attaching a policy to a group grants
all members of that group the permissions defined in the policy.

**Key properties:** `GroupName`, `GroupId`, `Arn`, `CreateDate`

**Relationships:**

```
Policy ────attached to───→ Group ────contains───→ Users
```

## Policy (权限策略)

A policy defines a set of permissions. CTyun supports two types:

| Type | Description |
|---|---|
| **System Policy (系统策略)** | Pre-defined by CTyun, covers common service permissions |
| **Custom Policy (自定义策略)** | User-defined, written in JSON policy syntax |

**Policy structure (JSON):**

```json
{
  "Version": "1.0",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ecs:Start", "ecs:Stop"],
      "Resource": ["*"]
    }
  ]
}
```

**Key properties:** `PolicyName`, `PolicyId`, `CreateDate`, `AttachmentCount`

## Role (角色)

An IAM role is an identity with specific permissions that can be assumed by
trusted entities (users, services, or federated identities). Roles do not have
standard long-term credentials — they get temporary credentials when assumed.

**Use cases:**
- Cross-account access
- Service-to-service authorization
- Federation with external identity providers

## Enterprise Project (企业项目)

Enterprise projects provide logical isolation and management of cloud resources.
IAM users and groups can be assigned policies scoped to specific enterprise
projects, enabling resource-level access control.

**Key properties:** `ProjectId`, `ProjectName`, `Status`, `CreateTime`

## Access Key (访问密钥 / AK-SK)

Access keys consist of an Access Key ID (AK) and Secret Access Key (SK).
Used for API/SDK/CLI authentication. Each IAM user can have multiple access
keys (typically up to 2 active keys).

**Key properties:** `AccessKeyId`, `Status` (Active/Inactive), `CreateDate`

## Identity Provider (身份供应商)

IAM supports federated identity by integrating with external identity providers
(IdPs). This enables users from your organization's identity system to access
CTyun resources without creating a dedicated IAM user.

## Sensitive Operation Protection (敏感操作保护)

CTyun IAM supports sensitive operation protection — certain high-risk
operations (delete, modify critical resources) can require additional
verification (MFA) before execution.

## Resource Hierarchy

```
Account (主账号)
├── Enterprise Projects
│   ├── IAM Users
│   ├── IAM Groups
│   └── Policies
├── Roles
├── Identity Providers
└── Access Keys (per user)
```

## Permission Evaluation Logic

1. By default, all requests are **denied** (implicit deny)
2. If a policy explicitly **allows** the action, it is allowed
3. If a policy explicitly **denies** the action, it is denied (deny always wins)
4. If no policy applies, the default deny stands

## Common Error Codes

| Code | Message | Meaning |
|---|---|---|
| `CTIAM_0113` | 请求头账号ID与请求参数账号ID不同 | accountId mismatch in header vs body |
| `CTIAM_0201` | 用户不存在 | User not found |
| `CTIAM_0301` | 用户组不存在 | Group not found |
| `CTIAM_0401` | 策略不存在 | Policy not found |
| `CTIAM_0501` | 访问密钥不存在 | Access key not found |

## See Also

- [CLI Usage](cli-usage.md) — IAM CLI commands
- [API/SDK Usage](api-sdk-usage.md) — SDK operations map
- [Troubleshooting](troubleshooting.md) — common issues and fixes
