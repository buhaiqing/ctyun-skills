# CCE API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.cce import CCEClient

client = CCEClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="cce.ctyun.cn",
    scheme="https",
    timeout=30  # cluster ops can be slow
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method |
|---|---|---|
| List clusters | `cce cluster list` | `client.list_clusters()` |
| Get cluster | `cce cluster get` | `client.get_cluster()` |
| Create cluster | `cce cluster create` | `client.create_cluster()` |
| Delete cluster | `cce cluster delete` | `client.delete_cluster()` |
| Get kubeconfig | `cce cluster get-credentials` | `client.get_kubeconfig()` |
| List node pools | `cce node-pool list` | `client.list_node_pools()` |
| List pods | `cce pod list` | `client.list_pods()` |

## Error Handling

```python
from ctyun_sdk.exceptions import CtyunApiException

try:
    clusters = client.list_clusters(region_id="{{user.region_id}}")
except CtyunApiException as e:
    print(f"CCE Error: {e.status_code} - {e.message}")
```

## Response Format

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```
