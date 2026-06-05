# OOS Integration Guide

## Integrating with ECS (Cloud Server)

### Mount OOS as Filesystem (via s3fs)

```bash
# Install s3fs
pip install s3fs

# Mount bucket
s3fs {{user.bucket_name}} /mnt/oos \
    -o endpoint={{env.OOS_ENDPOINT}} \
    -o url=https://{{env.OOS_ENDPOINT}} \
    -o passwd_file=/etc/passwd-s3fs \
    -o use_path_request_style \
    -o sigv2
```

### Access OOS from ECS Application

```python
import boto3
from botocore.config import Config

# Configure with CTyun OOS endpoint
s3 = boto3.client(
    "s3",
    endpoint_url="https://{{env.OOS_ENDPOINT}}",
    aws_access_key_id="{{env.CTYUN_ACCESS_KEY}}",
    aws_secret_access_key="{{env.CTYUN_SECRET_KEY}}",
    region_name="{{env.OOS_REGION_ID}}",
    config=Config(signature_version="s3v2")
)
```

## Integrating with CDN

OOS can serve as the **origin** for CDN acceleration:

1. Create a bucket with `public-read` ACL or use pre-signed URLs
2. Configure CDN domain to point to OOS bucket endpoint
3. CDN caches objects at edge nodes for faster delivery

Common use case: static website assets (images, CSS, JS) served via CDN
with OOS as origin.

## Integrating with Cloud Monitor

OOS metrics can be monitored through CTyun Cloud Monitor (see
[`monitoring.md`](monitoring.md) for details). Set up alarm rules to
notify on storage usage thresholds or request rate anomalies.

## Integrating with Applications

### Python Web App (Django/Flask)

```python
from django.core.files.storage import Storage
import boto3

class OOSStorage(Storage):
    """Custom Django storage backend for CTyun OOS."""
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url="https://{{env.OOS_ENDPOINT}}",
            aws_access_key_id="{{env.CTYUN_ACCESS_KEY}}",
            aws_secret_access_key="{{env.CTYUN_SECRET_KEY}}",
            config=Config(signature_version="s3v2")
        )

    def _save(self, name, content):
        self.client.upload_fileobj(content, "{{user.bucket_name}}", name)
        return name

    def url(self, name):
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "{{user.bucket_name}}", "Key": name},
            ExpiresIn=3600
        )
```

### Backup Script

```python
#!/usr/bin/env python3
"""Simple backup script: archive directory → OOS bucket."""
import os
import boto3
from botocore.config import Config

BUCKET = "{{user.bucket_name}}"
BACKUP_DIR = "{{user.local_path}}"

client = boto3.client(
    "s3",
    endpoint_url="https://{{env.OOS_ENDPOINT}}",
    aws_access_key_id=os.environ["CTYUN_ACCESS_KEY"],
    aws_secret_access_key=os.environ["CTYUN_SECRET_KEY"],
    config=Config(signature_version="s3v2")
)

for root, dirs, files in os.walk(BACKUP_DIR):
    for file in files:
        local_path = os.path.join(root, file)
        object_key = os.path.relpath(local_path, BACKUP_DIR)
        client.upload_file(local_path, BUCKET, object_key)
        print(f"Uploaded {local_path} → {object_key}")
```
