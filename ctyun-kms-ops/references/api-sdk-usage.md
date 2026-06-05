# KMS API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.kms import KMSClient

client = KMSClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="kms.ctyun.cn",
    scheme="https",
    timeout=20
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method | Notes |
|---|---|---|---|
| List keys | `kms key list` | `client.list_keys()` | — |
| Describe key | `kms key get` | `client.describe_key()` | — |
| Create key | `kms key create` | `client.create_key()` | — |
| Enable key | `kms key enable` | `client.enable_key()` | — |
| Disable key | `kms key disable` | `client.disable_key()` | — |
| Schedule deletion | `kms key schedule-deletion` | `client.schedule_key_deletion()` | Irreversible after window |
| Cancel deletion | `kms key cancel-deletion` | `client.cancel_key_deletion()` | — |

## Error Handling

```python
from ctyun_sdk.exceptions import CtyunApiException

try:
    key = client.describe_key(
        region_id="{{user.region_id}}",
        key_id="{{user.key_id}}"
    )
except CtyunApiException as e:
    print(f"KMS Error: {e.status_code} - {e.message}")
```

## Response Format

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```
