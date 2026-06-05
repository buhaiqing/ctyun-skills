# MongoDB API / SDK Usage

## Overview

CTyun MongoDB operations use two paths:

1. **Instance operations** → CTyun MongoDB OpenAPI REST API via Python `requests`
2. **Data operations** → `mongosh` CLI or MongoDB Python driver (`pymongo`)

There is no CTyun-specific Python SDK for MongoDB.

## Instance Operations: REST API

### API Endpoint

| Environment | Endpoint |
|---|---|
| Production | `mongodb.ctapi.ctyun.cn` |

### Authentication: EOP Signature

All MongoDB instance API requests require EOP signature (same as all CTyun
OpenAPI calls). See helper below.

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

### API Operations

| Operation | Endpoint Path |
|---|---|
| List Instances | `/v4/mongodb/instance/list` |
| Create Instance | `/v4/mongodb/instance/create` |
| Delete Instance | `/v4/mongodb/instance/delete` |
| Describe Instance | `/v4/mongodb/instance/detail` |
| Create Backup | `/v4/mongodb/backup/create` |
| Restore Instance | `/v4/mongodb/instance/restore` |

## Data Operations: mongosh CLI (recommended)

```bash
# Query
mongosh "{{user.connection_string}}" --quiet --eval \
  'use("{{user.database}}"); db.{{user.collection}}.find({{user.filter}}).limit({{user.limit}}).toArray()'

# Insert
mongosh "{{user.connection_string}}" --quiet --eval \
  'use("{{user.database}}"); db.{{user.collection}}.insertOne({{user.document}})'
```

## Data Operations: pymongo (alternative)

```bash
pip install pymongo
```

```python
from pymongo import MongoClient

client = MongoClient("{{user.connection_string}}")
db = client["{{user.database}}"]
collection = db["{{user.collection}}"]

# Query
results = collection.find({{user.filter}}).limit({{user.limit}})
for doc in results:
    print(doc)

# Insert
collection.insert_one({{user.document}})

# Index
collection.create_index({{user.index_spec}})
```

## Connection String Format

```
mongodb://username:password@host:27017/database?authSource=admin
```

Parameters from RDS MongoDB instance:
- **Host**: MongoDB instance endpoint
- **Port**: 27017 (default)
- **Username**: Set at instance creation
- **Password**: Set at instance creation
- **Database**: Target database name
