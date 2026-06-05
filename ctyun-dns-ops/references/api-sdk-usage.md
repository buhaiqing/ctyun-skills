# DNS API / SDK Usage

## Overview

CTyun DNS (云解析) does not have an official Python SDK. All DNS
operations use the **CTyun DNS OpenAPI REST API** directly via Python
`requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `dns.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All DNS API requests require an EOP signature in the HTTP headers. This is
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

url = "https://dns.ctapi.ctyun.cn/v4/dns/domain/list"
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
| List Domains | GET | `/v4/dns/domain/list` | `?regionId=...` |
| Create Domain | POST | `/v4/dns/domain/create` | `{"regionId":"...","domainName":"...","description":"..."}` |
| Delete Domain | POST | `/v4/dns/domain/delete` | `{"regionId":"...","domainId":"..."}` |
| List Records | GET | `/v4/dns/record/list` | `?regionId=...&domainId=...` |
| Create Record | POST | `/v4/dns/record/create` | `{"regionId":"...","domainId":"...","recordName":"...","recordType":"...","recordValue":"...","ttl":...}` |
| Update Record | POST | `/v4/dns/record/update` | `{"regionId":"...","domainId":"...","recordId":"...","recordValue":"...","ttl":...}` |
| Delete Record | POST | `/v4/dns/record/delete` | `{"regionId":"...","domainId":"...","recordId":"..."}` |
| DNS Statistics | GET | `/v4/dns/statistics` | `?regionId=...&domainId=...&startTime=...&endTime=...` |

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
