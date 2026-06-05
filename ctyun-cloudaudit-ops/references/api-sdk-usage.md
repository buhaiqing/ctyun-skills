# Cloud Audit API / SDK Usage

## Overview

CTyun Cloud Audit (云审计/CTS) does not have an official Python SDK. All audit operations use the **CTyun CTS OpenAPI REST API** directly via Python `requests` with **EOP (Enterprise Open Platform) signature** authentication.

**No SDK package exists on PyPI** — verified: `pip install ctyun-sdk` fails.

## API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `cts.ctapi.ctyun.cn` |
| HTTPS scheme | `https://` |

## Authentication: EOP Signature

All Cloud Audit API requests require an EOP signature in the HTTP headers. This is a hash-based message authentication code (HMAC-SHA256) computed from the request body, access key, and secret key.

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
| List Audit Logs | POST | `/v1/cts/log/list` | `{"regionId":"...","pageNumber":1,"pageSize":20}` |
| Query by Time | POST | `/v1/cts/log/query` | `{"regionId":"...","startTime":"...","endTime":"...","pageNumber":1,"pageSize":50}` |
| Query by Resource | POST | `/v1/cts/log/query` | `{"regionId":"...","startTime":"...","endTime":"...","resourceType":"...","pageNumber":1,"pageSize":50}` |
| Query by User | POST | `/v1/cts/log/query` | `{"regionId":"...","startTime":"...","endTime":"...","userName":"...","pageNumber":1,"pageSize":50}` |
| Log Detail | POST | `/v1/cts/log/detail` | `{"regionId":"...","traceId":"...","eventId":"..."}` |
| List Services | GET | `/v1/cts/services/list` | query params |
| Export Logs | POST | `/v1/cts/log/export` | `{"regionId":"...","bucketName":"...","startTime":"...","endTime":"..."}` |
| Audit Statistics | POST | `/v1/cts/statistics` | `{"regionId":"...","startTime":"...","endTime":"..."}` |

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