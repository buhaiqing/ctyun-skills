# ECS API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk`. Import
> paths follow PascalCase module naming.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.ecs import ECSClient

client = ECSClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    region_id="{{user.region_id}}",
    endpoint="ecs.ctyun.cn",
    scheme="https",
    timeout=20
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method | Docs Link |
|---|---|---|---|
| List instances | `ecs list` | `client.list_instances()` | [API docs](https://eop.ctyun.cn/ebp/searchCtapi/index) |
| Get instance | `ecs details` | `client.get_instance()` | ^ |
| Create instance | `ecs create` | `client.create_instance()` | ^ |
| Start instance | `ecs start` | `client.start_instance()` | ^ |
| Stop instance | `ecs stop` | `client.stop_instance()` | ^ |
| Reboot instance | `ecs reboot` | `client.reboot_instance()` | ^ |
| Delete instance | `ecs delete` | `client.delete_instance()` | ^ |
| Resize instance | `ecs resize` | `client.resize_instance()` | ^ |
| List flavors | `ecs flavor-options` | `client.query_flavor_options()` | ^ |
| List snapshots | `ecs list-snapshots` | `client.list_snapshots()` | ^ |
| Get snapshot details | `ecs get-snapshot-details` | `client.get_snapshot_details()` | ^ |
| List keypairs | `ecs list-keypairs` | `client.list_keypairs()` | ^ |
| Create image | `ecs create-image` | `client.create_instance_image()` | ^ |
| Get auto-renew | `ecs get-auto-renew-config` | `client.get_auto_renew_config()` | ^ |
| Query DNS record | `ecs query-dns-record` | `client.query_dns_record()` | ^ |
| Query async job | `ecs query-async-result` | `client.query_async_result()` | ^ |
| Query multiple jobs | `ecs query-jobs` | `client.query_jobs()` | ^ |
| Query resources | `ecs resources` | `client.get_customer_resources()` | ^ |
| VNC console | `ecs console` | `client.get_instance_console()` | ^ |
| CloudShell | `ecs cloudshell` | `client.get_instance_cloudshell()` | ^ |
| Batch start | `ecs batch-start` | `client.batch_start_instances()` | ^ |
| Batch stop | `ecs batch-stop` | `client.batch_stop_instances()` | ^ |
| Batch delete | `ecs batch-delete` | `client.batch_delete_instances()` | ^ |

## Error Handling

The SDK raises `CTYUNAPIError` for API-level failures:

```python
from ctyun_sdk.core import CTYUNAPIError

try:
    result = client.list_instances(region_id="...")
except CTYUNAPIError as e:
    print(f"API Error [{e.code}]: {e.message}")
    if e.request_id:
        print(f"Request ID: {e.request_id}")
```

## Response Envelope

All SDK responses share the same envelope structure as the CLI:

```python
{
    "statusCode": 800,      # 800 = success
    "message": "成功",
    "returnObj": { ... },   # operation-specific payload
    "_mock": False          # True when fallback mock data is used
}
```
