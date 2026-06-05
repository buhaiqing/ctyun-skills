# WAF API / SDK Usage

## Overview

CTyun WAF (Web应用防火墙) does not have an official Python SDK. All WAF operations use the **CTyun WAF OpenAPI REST API** directly via Python `requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `waf.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All WAF API requests require an EOP signature in the HTTP headers. This is a hash-based message authentication code (HMAC-SHA256) computed from the request body, access key, and secret key.

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

url = "https://waf.ctapi.ctyun.cn/v2/waf/instance/list"
headers = sign_request(
    method="POST",
    url=url,
    body={},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={"regionId": "{{env.CTYUN_REGION_ID}}"})
data = resp.json()
```

## API Operations

| Operation | HTTP Method | Endpoint Path | Request Body / Params |
|---|---|---|---|
| List Instances | POST | `/v2/waf/instance/list` | `{"regionId":"..."}` |
| Add Domain | POST | `/v2/waf/domain/create` | `{"regionId":"...","instanceId":"...","domainName":"...","protectionMode":"..."}` |
| Remove Domain | POST | `/v2/waf/domain/delete` | `{"regionId":"...","instanceId":"...","domainId":"..."}` |
| List Protected Domains | GET | `/v2/waf/domain/list` | `?regionId=...&instanceId=...` |
| Configure Rule | POST | `/v2/waf/rule/config` | `{"regionId":"...","instanceId":"...","domainId":"...","ruleType":"...","action":"..."}` |
| Configure ACL | POST | `/v2/waf/acl/config` | `{"regionId":"...","instanceId":"...","domainId":"...","aclType":"...","ipAddress":"...","action":"..."}` |
| Query Attack Logs | POST | `/v2/waf/log/attack` | `{"regionId":"...","instanceId":"...","domainId":"...","startTime":"...","endTime":"...","pageNumber":1,"pageSize":20}` |
| Query Statistics | POST | `/v2/waf/statistics` | `{"regionId":"...","instanceId":"...","domainId":"...","startTime":"...","endTime":"..."}` |

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