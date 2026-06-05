# Redis API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.redis import RedisClient

client = RedisClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="redis.ctyun.cn",
    scheme="https",
    timeout=20
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method | Notes |
|---|---|---|---|
| List instances | `redis list-instances` | `client.list_instances()` | Paginated |
| Get instance | `redis get-instance` | `client.get_instance()` | — |
| Create instance | `redis create-instance` | `client.create_instance()` | 25+ params; supports dry-run |
| Delete instance | `redis delete-instance` | `client.delete_instance()` | Irreversible |
| Create backup | `redis create-backup` | `client.create_backup()` | — |
| List network configs | `redis list-network-configs` | `client.list_network_configs()` | — |
| Get metrics | `redis get-instance-metrics` | `client.get_metrics()` | Time range filtering |
| Check resources | `redis check-resources` | `client.check_resources()` | Edition/version filtering |
| List zones | `redis zones` | `client.list_zones()` | — |
| Topology | `redis topology` | `client.get_topology()` | Cluster topology view |
| Cluster nodes | `redis cluster-nodes` | `client.list_cluster_nodes()` | Distributed edition only |

## Error Handling

```python
from ctyun_sdk.exceptions import CtyunApiException

try:
    result = client.create_instance(
        instance_name="my-redis",
        edition="StandardSingle",
        engine_version="6.0",
        shard_mem_size=8,
        ...
    )
except CtyunApiException as e:
    # Handle API errors (statusCode != 800)
    print(f"Error: {e.status_code} - {e.message}")
```

## Response Format

All API responses follow the standard CTyun envelope:

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```
