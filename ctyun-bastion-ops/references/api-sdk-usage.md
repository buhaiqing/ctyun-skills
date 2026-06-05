# Cloud Bastion Host API / SDK Usage

## Overview

CTyun Cloud Bastion Host (云堡垒机原生版/OSM) does not have an official Python SDK. All bastion operations use the **CTyun OSM OpenAPI REST API** directly via Python `requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `osm.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All Bastion API requests require an EOP signature in the HTTP headers. This is a hash-based message authentication code (HMAC-SHA256) computed from the request body, access key, and secret key.

### Python EOP Signer

```python
import hashlib
import hmac
import json
import time

def sign_request(method: str, url: str, body: dict,
                 access_key: str, secret_key: str) -> dict:
    """Generate EOP authentication headers for CTyun API calls."""
    timestamp = str(int(time.time() * 1000))

    body_str = json.dumps(body, separators=(",", ":")) if body else ""
    sign_str = f"{method}\n{url}\n{body_str}\n{access_key}\n{timestamp}"

    sign_bytes = hmac.new(
        secret_key.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return {
        "Content-Type": "application/json",
        "X-Access-Key": access_key,
        "X-Signature": sign_bytes,
        "X-Timestamp": timestamp
    }
```

## API Operations

| Operation | HTTP Method | Endpoint Path | Request Body / Params |
|---|---|---|---|
| List Instances | POST | `/osm/v2/console/listInstance` | `{"pageNumber":1,"pageSize":10}` |
| Describe Instance | POST | `/osm/v2/console/describeInstance` | `{"vmId":"..."}` |
| Create Instance | POST | `/osm/v2/console/createInstance` | `{"regionId":"...","instanceName":"...","spec":"...","assetsNum":...,"concurrencyNumber":...,"vpcId":"...","subnetId":"..."}` |
| Delete Instance | POST | `/osm/v2/console/deleteInstance` | `{"vmId":"..."}` |
| Restart Instance | POST | `/osm/v2/console/rebootInstance` | `{"vmId":"..."}` |
| Create User | POST | `/osm/v2/console/createUser` | `{"vmId":"...","userName":"...","password":"...","email":"...","phone":"..."}` |
| Add Host | POST | `/osm/v2/console/createHost` | `{"vmId":"...","hostIp":"...","hostName":"...","protocol":"...","port":...,"account":"...","password":"..."}` |
| Create Policy | POST | `/osm/v2/console/createPolicy` | `{"vmId":"...","policyName":"...","userIdList":["..."],"hostIdList":["..."],"accessTime":"...","accessDays":[...]}` |

## Response Format

```json
{
  "statusCode": "0",
  "message": "操作成功",
  "page": {
    "current": 1,
    "size": 10,
    "total": 54
  },
  "returnObj": [ ... ]
}
```

> **Note:** This product uses `statusCode` as a **string** `"0"` for success (not a number). List operations return pagination info in the `page` object.

- `statusCode == "0"` (string) → success
- `statusCode != "0"` → error (see `message` field)