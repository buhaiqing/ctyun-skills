# EIP API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.vpc import VPCClient

client = VPCClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="vpc.ctyun.cn",
    scheme="https",
    timeout=20
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method | Notes |
|---|---|---|---|
| List EIPs | `vpc list-eips` | `client.list_eips()` | Paginated |
| Describe EIP | `vpc describe-eip` | `client.describe_eip()` | — |
| Allocate EIP | `vpc create-eip` | `client.create_eip()` | Requires clientToken |
| Associate EIP | `vpc associate-eip` | `client.associate_eip()` | associationType: 1=ECS, 2=VIP, 3=BM |
| Disassociate EIP | `vpc disassociate-eip` | `client.disassociate_eip()` | — |
| Release EIP | `vpc delete-eip` | `client.delete_eip()` | Irreversible |

## Idempotency

Create and associate operations require a `clientToken` (UUID) to ensure
idempotency. If the same token is reused within a short window, the API
returns the original result instead of creating a duplicate.

```python
import uuid

client_token = str(uuid.uuid4())
result = client.create_eip(
    region_id="{{user.region_id}}",
    bandwidth=10,
    name="my-eip",
    client_token=client_token
)
```

## Error Handling

```python
from ctyun_sdk.exceptions import CtyunApiException

try:
    result = client.associate_eip(
        region_id="{{user.region_id}}",
        eip_id="{{user.eip_id}}",
        association_id="{{user.instance_id}}",
        association_type=1,
        client_token=str(uuid.uuid4())
    )
except CtyunApiException as e:
    print(f"EIP Error: {e.status_code} - {e.message}")
```

## Response Format

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```
