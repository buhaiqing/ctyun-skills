# IAM API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.
> Import paths follow PascalCase module naming.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.iam import IAMClient

client = IAMClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="iam.ctyun.cn",
    scheme="https",
    timeout=20
)
```

**Note:** Unlike ECS, IAM operations are typically **account-level** and do not
require a region ID.

## Operation Mapping

| Operation | CLI Command | SDK Method | Docs |
|---|---|---|---|
| List enterprise projects | `iam list-projects` | `client.list_enterprise_projects()` | [API docs](https://www.ctyun.cn/document/10026693) |
| Get enterprise project | `iam get-project` | `client.get_enterprise_project()` | ^ |
| List IAM users | `iam list-users` | `client.list_users()` | ^ |
| Get IAM user | `iam get-user` | `client.get_user()` | ^ |
| Create IAM user | `iam create-user` | `client.create_user()` | ^ |
| Delete IAM user | `iam delete-user` | `client.delete_user()` | ^ |
| List IAM groups | `iam list-groups` | `client.list_groups()` | ^ |
| Get IAM group | `iam get-group` | `client.get_group()` | ^ |
| Create IAM group | `iam create-group` | `client.create_group()` | ^ |
| Delete IAM group | `iam delete-group` | `client.delete_group()` | ^ |
| Add user to group | `iam add-user-to-group` | `client.add_user_to_group()` | ^ |
| Remove user from group | `iam remove-user-from-group` | `client.remove_user_from_group()` | ^ |
| List policies | `iam list-policies` | `client.list_policies()` | ^ |
| Get policy | `iam get-policy` | `client.get_policy()` | ^ |
| Create policy | `iam create-policy` | `client.create_policy()` | ^ |
| Delete policy | `iam delete-policy` | `client.delete_policy()` | ^ |
| Attach policy to group | `iam attach-group-policy` | `client.attach_group_policy()` | ^ |
| Detach policy from group | `iam detach-group-policy` | `client.detach_group_policy()` | ^ |
| List attached group policies | `iam list-attached-group-policies` | `client.list_attached_group_policies()` | ^ |
| List access keys | `iam list-access-keys` | `client.list_access_keys()` | ^ |
| Create access key | `iam create-access-key` | `client.create_access_key()` | ^ |
| Update access key | `iam update-access-key` | `client.update_access_key()` | ^ |
| Delete access key | `iam delete-access-key` | `client.delete_access_key()` | ^ |
| List roles | `iam list-roles` | `client.list_roles()` | ^ |
| Create role | `iam create-role` | `client.create_role()` | ^ |
| Delete role | `iam delete-role` | `client.delete_role()` | ^ |
| List ID providers | `iam list-id-providers` | `client.list_id_providers()` | ^ |

## MFA Operations (SDK Only)

These operations have no CLI equivalent and MUST use the SDK:

| Operation | SDK Method |
|---|---|
| Enable MFA device | `client.enable_mfa_device()` |
| List MFA devices | `client.list_mfa_devices()` |
| Deactivate MFA device | `client.deactivate_mfa_device()` |
| List virtual MFA devices | `client.list_virtual_mfa_devices()` |

## Error Handling

```python
from ctyun_sdk.core import CTYUNAPIError

try:
    result = client.list_users()
except CTYUNAPIError as e:
    print(f"IAM API Error [{e.code}]: {e.message}")
    if e.request_id:
        print(f"Request ID: {e.request_id}")
```

## Response Envelope

All SDK responses follow the same structure:

```python
{
    "statusCode": 800,      # 800 = success
    "message": "成功",
    "returnObj": { ... },   # operation-specific payload
    "_mock": False
}
```

IAM-specific error codes (non-800):

| statusCode | Message | Meaning |
|---|---|---|
| `CTIAM_0113` | 请求头账号ID与请求参数账号ID不同 | accountId mismatch |
| `CTIAM_0201` | 用户不存在 | User not found |
| `CTIAM_0301` | 用户组不存在 | Group not found |
| `CTIAM_0401` | 策略不存在 | Policy not found |
| `CTIAM_0501` | 访问密钥不存在 | Access key not found |
| `CTIAM_0601` | 角色不存在 | Role not found |
