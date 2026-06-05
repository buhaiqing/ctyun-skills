# CDN API / SDK Usage

## Overview

CTyun CDN (内容分发网络) does not have an official Python SDK. All CDN
operations use the **CTyun CDN OpenAPI REST API** directly via Python
`requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `cdn.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All CDN API requests require an EOP signature in the HTTP headers. This is
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

url = "https://cdn.ctapi.ctyun.cn/v2/cdn/domain/list"
headers = sign_request(
    method="GET",
    url=url,
    body=None,
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.get(url, headers=headers, params={"regionId": "{{env.CTYUN_REGION_ID}}"})
data = resp.json()
```

## API Operations

| Operation | HTTP Method | Endpoint Path | Request Body / Params |
|---|---|---|---|
| List Domains | GET | `/v2/cdn/domain/list` | `?regionId=...` |
| Create Domain | POST | `/v2/cdn/domain/create` | `{"regionId":"...","domainName":"...","originType":"...","originAddr":"...","originPort":...}` |
| Describe Domain | GET | `/v2/cdn/domain/detail` | `?regionId=...&domainId=...` |
| Start Domain | POST | `/v2/cdn/domain/start` | `{"regionId":"...","domainId":"..."}` |
| Stop Domain | POST | `/v2/cdn/domain/stop` | `{"regionId":"...","domainId":"..."}` |
| Delete Domain | POST | `/v2/cdn/domain/delete` | `{"regionId":"...","domainId":"..."}` |
| Set Cache Rules | POST | `/v2/cdn/cache/rule/set` | `{"regionId":"...","domainId":"...","rules":[...]}` |
| Refresh Cache | POST | `/v2/cdn/cache/refresh` | `{"regionId":"...","domainId":"...","type":"...","urls":[...]}` |
| Prefetch | POST | `/v2/cdn/cache/prefetch` | `{"regionId":"...","domainId":"...","urls":[...]}` |
| Configure HTTPS | POST | `/v2/cdn/https/config` | `{"regionId":"...","domainId":"...","httpsStatus":"...","certificateId":"..."}` |
| Configure ACL | POST | `/v2/cdn/acl/config` | `{"regionId":"...","domainId":"...","refererEnabled":...,"ipBlacklistEnabled":...}` |
| Query Statistics | GET | `/v2/cdn/statistics` | `?regionId=...&domainId=...&startTime=...&endTime=...&metrics=...` |
| Query Logs | GET | `/v2/cdn/logs` | `?regionId=...&domainId=...&startTime=...&endTime=...` |

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
