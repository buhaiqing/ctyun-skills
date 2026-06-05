# CTyun OOS CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support OOS operations.** Verified against
> `ctyun-cli v1.20.2` module list: ECS, Monitor, Redis, Audit, IMS,
> Billing, Security, IAM, EBS, CDA, VPC, CCE, ELB, Kafka, CSS, EMR,
> SFS, OceanFS, Aone, LTS — **no OOS subcommand exists.**

```bash
# Verify: no OOS module
ctyun --help | grep -i oos
# (empty output — OOS not available)
```

Since OOS is not available in `ctyun-cli`, the `cli_applicability` for this
skill is `sdk-only`. Use the official OOS Python SDK or S3-compatible tools
(see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: AWS CLI with CTyun Endpoint

OOS is S3-compatible, so the AWS CLI can be configured to work with CTyun
OOS by pointing to the correct endpoint and using S3 v2 signatures.

### Installation

```bash
pip install awscli
```

### Configuration

```bash
aws configure set aws_access_key_id {{env.CTYUN_ACCESS_KEY}}
aws configure set aws_secret_access_key {{env.CTYUN_SECRET_KEY}}
aws configure set region {{env.OOS_REGION_ID}}
aws configure set s3.signature_version s3v2
```

### Usage

```bash
# List buckets
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 ls

# Create bucket
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 mb s3://{{user.bucket_name}}

# List objects
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 ls s3://{{user.bucket_name}}/

# Upload file
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 cp {{user.local_path}} s3://{{user.bucket_name}}/{{user.object_key}}

# Download file
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 cp s3://{{user.bucket_name}}/{{user.object_key}} {{user.local_path}}

# Delete object
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 rm s3://{{user.bucket_name}}/{{user.object_key}}

# Delete bucket (must be empty)
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 rb s3://{{user.bucket_name}}

# Sync a local directory to bucket
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 sync {{user.local_path}}/ s3://{{user.bucket_name}}/
```

### Presigned URL

```bash
# Generate a presigned URL for temporary access (expires in 3600 seconds)
aws --endpoint-url https://{{env.OOS_ENDPOINT}} s3 presign s3://{{user.bucket_name}}/{{user.object_key}} --expires-in {{user.expires_in}}
```

## Alternative: MinIO Client (mc)

```bash
# Install mc
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure OOS alias
mc alias set ctyun-oos https://{{env.OOS_ENDPOINT}} {{env.CTYUN_ACCESS_KEY}} {{env.CTYUN_SECRET_KEY}} --api S3v2

# List buckets
mc ls ctyun-oos

# List objects
mc ls ctyun-oos/{{user.bucket_name}}/

# Upload
mc cp {{user.local_path}} ctyun-oos/{{user.bucket_name}}/{{user.object_key}}

# Download
mc cp ctyun-oos/{{user.bucket_name}}/{{user.object_key}} {{user.local_path}}
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... 19 modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "oos" module present.
```

> **Note:** The AWS CLI and MinIO Client paths are **documentation-only**
> alternatives. The primary execution path for this skill is the OOS
> Python SDK.
