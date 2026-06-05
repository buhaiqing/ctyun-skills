# SSL Certificate API / SDK Usage

## Overview

CTyun SSL Certificate (证书管理服务/CCMS) does not have an official Python SDK. All certificate operations use the **CTyun Certificate OpenAPI REST API** directly via Python `requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `cert.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All Certificate API requests require an EOP signature in the HTTP headers. This is a hash-based message authentication code (HMAC-SHA256) computed from the request body, access key, and secret key.

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
| List Certificates | POST | `/v1/certificate/list` | `{"regionId":"...","pageNumber":1,"pageSize":20}` |
| Certificate Detail | POST | `/v1/certificate/detail` | `{"regionId":"...","id":"..."}` |
| Apply Certificate | POST | `/v1/certificate/apply` | `{"regionId":"...","domainName":"...","certType":"...","brand":"...","validityPeriod":...}` |
| Upload Certificate | POST | `/v1/certificate/upload` | `{"regionId":"...","name":"...","certificateBody":"...","privateKey":"..."}` |
| Delete Certificate | POST | `/v1/certificate/delete` | `{"regionId":"...","id":"..."}` |
| Deploy Certificate | POST | `/v1/certificate/deploy` | `{"regionId":"...","certificateId":"...","resourceType":"...","resourceId":"..."}` |
| Certificate Expiry | POST | `/v1/certificate/expiry` | `{"regionId":"...","daysBeforeExpiry":30}` |
| Download Certificate | POST | `/v1/certificate/download` | `{"regionId":"...","id":"..."}` |

## Response Format

```json
{
  "statusCode": 200,
  "message": "Success",
  "returnObj": { ... }
}
```

> **Note:** This product uses `statusCode == 200` for success (unlike most CTyun products which use 800). Verify accordingly.

- `statusCode == 200` → success
- `statusCode != 200` → error (see `message` field)