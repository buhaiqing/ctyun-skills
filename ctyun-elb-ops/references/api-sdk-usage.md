# ELB API / SDK Usage

> The CTyun Python SDK is installed via `pip install ctyun-sdk>=1.0.0`.

## Installation

```bash
pip install ctyun-sdk>=1.0.0
```

## Client Initialization

```python
from ctyun_sdk.services.elb import ELBClient

client = ELBClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="elb.ctyun.cn",
    scheme="https",
    timeout=20
)
```

## Operation Mapping

| Operation | CLI Command | SDK Method | Notes |
|---|---|---|---|
| List load balancers | `elb loadbalancer list` | `client.list_load_balancers()` | Paginated |
| Get load balancer | `elb loadbalancer get` | `client.get_load_balancer()` | — |
| List target groups | `elb targetgroup list` | `client.list_target_groups()` | Paginated |
| Get target group | `elb targetgroup get` | `client.get_target_group()` | — |
| List targets | `elb targetgroup targets list` | `client.list_targets()` | — |
| Show target | `elb targetgroup targets show` | `client.get_target()` | — |
| Health check show | `elb health-check show` | `client.get_health_check()` | — |
| Monitor realtime | `elb monitor realtime` | `client.get_realtime_monitor()` | — |
| Monitor history | `elb monitor history` | `client.get_history_monitor()` | — |

### SDK-Only Operations

The following operations do not have CLI equivalents and use SDK directly:

| Operation | SDK Method |
|---|---|
| Create load balancer | `client.create_load_balancer()` |
| Delete load balancer | `client.delete_load_balancer()` |
| Create target group | `client.create_target_group()` |
| Delete target group | `client.delete_target_group()` |
| Register target | `client.register_target()` |
| Deregister target | `client.deregister_target()` |
| Update health check | `client.update_health_check()` |
| Create/update listener | `client.create_listener()` / `client.update_listener()` |

## Error Handling

```python
from ctyun_sdk.exceptions import CtyunApiException

try:
    result = client.list_load_balancers(region_id="{{user.region_id}}")
except CtyunApiException as e:
    print(f"Error: {e.status_code} - {e.message}")
```

## Response Format

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```
