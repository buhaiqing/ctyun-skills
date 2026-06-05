# OOS Troubleshooting Guide

## Common Errors

### Bucket Operations

| Error | Likely Cause | Resolution |
|---|---|---|
| `BucketAlreadyExists` (409) | Bucket name taken globally | Choose a different name |
| `BucketNotEmpty` (409) | Bucket has objects/lifecycle rules | Delete all objects first |
| `AccessDenied` (403) | Wrong AK/SK or bucket ACL | Verify credentials, check bucket policy |
| `InvalidBucketName` (400) | Name violates naming rules | 3-63 chars, lowercase, start/end with letter/digit |

### Object Operations

| Error | Likely Cause | Resolution |
|---|---|---|
| `NoSuchKey` (404) | Object key does not exist | Verify the key path |
| `NoSuchBucket` (404) | Bucket does not exist | Create bucket first |
| `AccessDenied` (403) | Object or bucket ACL blocks access | Check ACL configuration |
| `EntityTooLarge` (400) | Object > 5 GB (single PUT) | Use multipart upload instead |
| `InvalidObjectState` (403) | Object is in Archive tier | Restore before reading |
| `SignatureDoesNotMatch` (403) | Wrong signature version | OOS Classic uses S3 v2; set `signature_version=s3v2` |

### SDK/Client Issues

| Issue | Likely Cause | Resolution |
|---|---|---|
| ImportError: `oos_sdk` | SDK not installed | Download from CTyun portal and `python setup.py install` |
| Connection timeout | Wrong endpoint URL | Verify endpoint: `oos-cn.ctyunapi.cn` |
| Clock skew error | System clock out of sync | Sync NTP: `ntpdate pool.ntp.org` |
| boto3: `InvalidRequest` | Signature version mismatch | Set `Config(signature_version="s3v2")` |

## Diagnostic Commands

### Verify Connectivity

```python
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url="https://oos-cn.ctyunapi.cn",
    aws_access_key_id="***",
    aws_secret_access_key="***",
    config=Config(signature_version="s3v2")
)

# Test: list buckets
try:
    response = client.list_buckets()
    print("Buckets:", [b["Name"] for b in response.get("Buckets", [])])
except Exception as e:
    print(f"Connection failed: {e}")
```

### Check Bucket Existence

```bash
aws --endpoint-url https://oos-cn.ctyunapi.cn s3 ls s3://{{user.bucket_name}}
```

## Support

- CTyun OOS documentation: https://www.ctyun.cn/document/10026693
- CTyun OOS developer guide: https://oos-cn.ctyunapi.cn/docs/oos/
- Technical support: 400-826-7010
