# OOS API / SDK Usage

> CTyun OOS (经典版Ⅰ型) supports multiple SDK paths. The **primary path**
> is the official OOS Python SDK (v6+). The **alternative path** uses boto3
> with S3-compatible API (works for both OOS and ZOS).

## Installation

### Option 1: Official OOS Python SDK (Primary)

Download the SDK from CTyun official portal:
https://www.ctyun.cn/document/10026693/10026825

```bash
# Download oos-python-sdk-6.x.x.zip from the portal
unzip oos-python-sdk-6.x.x.zip
cd python-sdk-6.x.x
python setup.py install
```

Dependencies: `urllib3`, `jmespath`, `python-dateutil`

### Option 2: boto3 (Alternative, S3-compatible)

```bash
pip install boto3>=1.28.0
```

### Option 3: ctyun-zos-sdk (for ZOS product)

```bash
pip install ctyun-zos-sdk>=0.1.0
```

## Client Initialization

### OOS Python SDK

```python
from oos_sdk.client import Client

client = Client(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint="{{env.OOS_ENDPOINT}}",       # e.g. oos-cn.ctyunapi.cn
    region="{{env.OOS_REGION_ID}}"          # e.g. cn-gz
)

# Optional: configure signature version (OOS Classic uses v2)
client.set_signature_version("s3v2")
```

### boto3 (S3-compatible)

```python
import boto3
from botocore.config import Config

session = boto3.session.Session()

client = session.client(
    service_name="s3",
    aws_access_key_id="{{env.CTYUN_ACCESS_KEY}}",
    aws_secret_access_key="{{env.CTYUN_SECRET_KEY}}",
    endpoint_url="https://{{env.OOS_ENDPOINT}}",
    region_name="{{env.OOS_REGION_ID}}",
    config=Config(
        signature_version="s3v2",   # OOS Classic requires v2
        connect_timeout=10,
        read_timeout=30,
        retries={"max_attempts": 3}
    )
)
```

## Operation Mapping

| Operation | OOS SDK Method | boto3 Method | Notes |
|---|---|---|---|
| List Buckets | `client.list_buckets()` | `client.list_buckets()` | — |
| Create Bucket | `client.create_bucket()` | `client.create_bucket()` | Globally unique name |
| Delete Bucket | `client.delete_bucket()` | `client.delete_bucket()` | Bucket must be empty |
| List Objects | `client.list_objects()` | `client.list_objects_v2()` | Supports prefix/delimiter |
| Upload Object | `client.put_object()` | `client.upload_file()` | Supports ACL at upload |
| Download Object | `client.get_object()` | `client.download_file()` | Streams to file |
| Delete Object | `client.delete_object()` | `client.delete_object()` | — |
| Delete Multiple Objects | `client.delete_objects()` | `client.delete_objects()` | Batch up to 1000 keys |
| Copy Object | `client.copy_object()` | `client.copy_object()` | Within/between buckets |
| Head Object | `client.head_object()` | `client.head_object()` | Get metadata without download |
| Get Bucket ACL | `client.get_bucket_acl()` | `client.get_bucket_acl()` | — |
| Put Bucket ACL | `client.put_bucket_acl()` | `client.put_bucket_acl()` | private/public-read/public-read-write |
| Pre-signed URL (GET) | `client.generate_presigned_url()` | `client.generate_presigned_url()` | `method="get"` |
| Pre-signed URL (PUT) | `client.generate_presigned_url()` | `client.generate_presigned_url()` | `method="put"` |
| Get Bucket Lifecycle | `client.get_bucket_lifecycle()` | `client.get_bucket_lifecycle()` | — |
| Put Bucket Lifecycle | `client.put_bucket_lifecycle()` | `client.put_bucket_lifecycle()` | JSON/XML rules |

## Idempotency

Most OOS operations are **naturally idempotent** (S3 protocol design):

| Operation | Idempotent? | Notes |
|---|---|---|
| Create Bucket | Yes | Second call returns `BucketAlreadyExists` or succeeds |
| Put Object | Yes | Uploading same key overwrites; no duplicate |
| Delete Object | Yes | Deleting a non-existent key succeeds |
| Delete Bucket | Yes | Must be empty; fails if not |
| Set ACL | Yes | Same ACL applied repeatedly = same result |

## Error Handling

### OOS SDK

```python
from oos_sdk.exceptions import OosApiException

try:
    client.create_bucket(bucket_name="my-bucket")
except OosApiException as e:
    print(f"OOS Error: {e.status_code} - {e.message}")
    if e.status_code == 409:  # BucketAlreadyExists
        print("Bucket name already taken")
```

### boto3

```python
import botocore.exceptions

try:
    client.create_bucket(Bucket="my-bucket")
except botocore.exceptions.ClientError as e:
    error_code = e.response["Error"]["Code"]
    error_msg = e.response["Error"]["Message"]
    print(f"S3 Error: {error_code} - {error_msg}")
```

## Response Format

### OOS SDK response (Python dict)

```python
{
    "status": 200,
    "headers": {...},
    "body": {
        "Buckets": [
            {"Name": "my-bucket", "CreationDate": "2026-01-01T00:00:00Z"}
        ]
    }
}
```

### boto3 response (dict, S3-compatible)

```python
{
    "ResponseMetadata": {"HTTPStatusCode": 200, ...},
    "Buckets": [
        {"Name": "my-bucket", "CreationDate": datetime(...)}
    ]
}
```
