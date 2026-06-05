# RDS API / SDK Usage

## Overview

CTyun RDS (关系型数据库) does not have an official Python SDK. All RDS
operations use the **CTyun RDS OpenAPI REST API** directly via Python
`requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `ctrds.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All RDS API requests require an EOP signature in the HTTP headers. This is
a hash-based message authentication code (HMAC-SHA256) computed from the
request body, access key, and secret key.

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

    # Build signature string
    body_str = json.dumps(body, separators=(",", ":")) if body else ""
    sign_str = f"{method}\n{url}\n{body_str}\n{access_key}\n{timestamp}"

    # HMAC-SHA256
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

### Usage

```python
import requests

url = "https://ctrds.ctapi.ctyun.cn/v4/rds/instance/list"
headers = sign_request(
    method="POST",
    url=url,
    body={"regionId": "cn-gz"},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={"regionId": "cn-gz"})
data = resp.json()
```

## API Operations

| Operation | HTTP Method | Endpoint Path | Request Body |
|---|---|---|---|
| List Instances | POST | `/v4/rds/instance/list` | `{"regionId": "..."}` |
| Describe Instance | POST | `/v4/rds/instance/detail` | `{"regionId": "...", "instanceId": "..."}` |
| Create Instance | POST | `/v4/rds/instance/create` | `{"regionId": "...", "engine": "...", ...}` |
| Delete Instance | POST | `/v4/rds/instance/delete` | `{"regionId": "...", "instanceId": "..."}` |
| Resize Instance | POST | `/v4/rds/instance/resize` | `{"regionId": "...", "instanceId": "...", ...}` |
| Create Backup | POST | `/v4/rds/backup/create` | `{"regionId": "...", "instanceId": "...", ...}` |
| Restore Instance | POST | `/v4/rds/instance/restore` | `{"regionId": "...", "instanceId": "...", "backupId": "..."}` |
| Reboot Instance | POST | `/v4/rds/instance/reboot` | `{"regionId": "...", "instanceId": "..."}` |

## Response Format

```json
{
  "statusCode": 800,
  "message": "success",
  "returnObj": { ... }
}
```

- `statusCode == 800` → success
- `statusCode != 800` → error (see `message` field)
