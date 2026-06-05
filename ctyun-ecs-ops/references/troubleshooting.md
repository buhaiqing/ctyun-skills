# ECS Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

**Cause:** CLI not installed or not in PATH.

**Fix:**
```bash
pip install ctyun-cli>=1.18.4
# Verify
ctyun --version
```

### `not authenticated` / status 401

**Cause:** Credentials not configured.

**Fix:**
```bash
# Check env vars
test -n "$CTYUN_ACCESS_KEY" && echo "AK set" || echo "AK missing"
test -n "$CTYUN_SECRET_KEY" && echo "SK set" || echo "SK missing"

# Check config file
cat ~/.ctyun/config

# Rewrite if needed
cat > ~/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = cn-gz
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > ~/.ctyun/current
```

> **CRITICAL:** Unlike SDK, the `ctyun` CLI reads credentials ONLY from `~/.ctyun/config`, NOT from environment variables.

### `subcommand not found` / no such option

**Cause:** CLI version too old; command or flag doesn't exist in this version.

**Fix:**
```bash
# Check version
ctyun --version

# Upgrade
pip install --upgrade ctyun-cli

# Minimum required: 1.18.4 for full ECS support
```

### Non-JSON output

**Cause:** API gateway returned HTML error page or CLI encountered a crash.

**Fix:** Add `--output json` flag BEFORE the subcommand, not after.

---

## API-Level Errors

| Error Code / Message | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API returned error | Surface `$.message` to user |
| `instanceStatus not in (stopped)` | Resize on running instance | `ctyun ecs stop <id>` first |
| `flavorQuotaExceeded` | Region flavor quota exceeded | Choose different flavor or contact CTyun to increase quota |
| `securityGroupNotExist` | Bad security group ID | Verify SG exists in the target region |
| `imageNotExist` | Bad image ID | List available images: `ctyun ims list-available` |
| `invalidInstanceType` | Flavor not available in this region | Run `ecs flavor-options --region-id <id>` to see valid options |
| `vpcQuotaExceeded` | VPC limit reached | Delete unused VPCs or request quota increase |
| `subnetNotExist` | Bad subnet ID | Verify subnet exists in the specified VPC/region |
| `instanceNotFound` | Instance ID does not exist | Verify instance ID and region |
| `snapshotNotFound` | Snapshot ID does not exist | Verify snapshot ID and region |

---

## Instance State Issues

### Instance stuck in `stopping`

**Symptom:** Instance remains in `stopping` state for >5 minutes.

**Fix:**
```bash
ctyun --output json ecs stop <instance_id> --force
```

### Instance stuck in `starting`

**Symptom:** Instance remains in `starting` state for >10 minutes.

**Actions:**
1. Check system log via console: `ctyun ecs console <instance_id>`
2. Verify image integrity — try launching with a different image
3. Force stop and retry: `stop --force` → `start`

### Cannot SSH into instance

**Actions:**
1. Verify instance is `running`: `ctyun ecs list --state running`
2. Check security group allows inbound SSH (port 22)
3. Verify key pair fingerprint matches your local key
4. Check EIP is attached: `ctyun ecs details <instance_id>` → `eipAddress[]`
5. If no EIP, instance only accessible within VPC

### Instance terminated unexpectedly

**Actions:**
1. Check if `stop` or `delete` was called by another operator
2. Check billing status: `ctyun ecs get-auto-renew-config` for expiry info
3. For pay-as-you-go instances, insufficient balance causes automatic termination
4. Review audit logs: delegate to `ctyun-audit-ops` (planned)

---

## Snapshot Issues

| Issue | Cause | Resolution |
|---|---|---|
| Snapshot stuck in `pending` | Large disk still initializing | Wait; large disks (>500GB) take time |
| Snapshot in `error` | Disk I/O error during capture | Delete failed snapshot (`ecs delete-snapshot` — planned) and retry |
| `snapshotNotFound` | Wrong region | Snapshots are region-scoped; verify `--region-id` |

---

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI returns `5xx` for same operation twice | Fall back to SDK for that operation |
| CLI command not found | Fall back to SDK for that operation |
| CLI output is non-JSON after retry | Fall back to SDK for that operation |
| SDK also fails | Surface the API error to user |

Refer to [`cli-decision-matrix.md`](../../ctyun-skill-generator/references/cli-decision-matrix.md) for the full fallback decision tree.

---

## File Transfer via OSS (Universal Solution)

When CloudShell doesn't support direct file upload/download, **OSS (Object Storage Service)** provides a universal cross-cloud solution that works with all major cloud providers.

### Why OSS Transfer?

| Limitation | OSS Solution |
|------------|--------------|
| CloudShell has no file upload UI | Upload to OSS bucket, then `wget` from ECS |
| CloudShell has no file download UI | `curl` from ECS to OSS, then download from OSS console |
| Instance has no public IP | Internal VPC endpoint access to OSS (free) |
| Large file transfer | OSS supports resumeable multipart uploads |
| Cross-region transfer | OSS has CDN acceleration |

### Universal Workflow (Works on All Clouds)

```
┌─────────────┐    Upload     ┌─────────────┐    Download     ┌─────────────┐
│ Local File  │ ─────────────→│  OSS Bucket │ ───────────────→│ ECS Instance│
│ (script.sh) │   via Console │  (public)   │  wget/curl/     │ (via        │
│             │   or CLI      │             │  SDK            │ CloudShell) │
└─────────────┘               └─────────────┘                 └─────────────┘
```

### Step-by-Step (Cloud-Agnostic)

**Step 1: Upload file to OSS** (via Web Console or CLI)

```bash
# AWS S3
aws s3 cp script.sh s3://my-bucket/scripts/

# Alibaba Cloud OSS
ossutil cp script.sh oss://my-bucket/scripts/

# Huawei Cloud OBS
obsutil cp script.sh obs://my-bucket/scripts/

# CTyun OOS (via console or API)
# Upload via web console: https://oos.ctyun.cn
```

**Step 2: Generate public URL** (temporary or permanent)

```bash
# AWS - presigned URL (valid 1 hour)
aws s3 presign s3://my-bucket/scripts/script.sh --expires-in 3600
# Result: https://my-bucket.s3.amazonaws.com/scripts/script.sh?X-Amz-...

# Alibaba Cloud - signed URL
ossutil sign oss://my-bucket/scripts/script.sh --timeout 3600

# Huawei Cloud - temporary URL
obsutil sign obs://my-bucket/scripts/script.sh -e 3600
```

**Step 3: Download to ECS via CloudShell**

```bash
# Connect via CloudShell
ctyun ecs cloudshell i-abc123 --region-id cn-gz

# Inside ECS, download from OSS
cd /tmp
wget "https://my-bucket.oos-cn-gz.ctyun.cn/scripts/script.sh?Signature=..."

# Or use curl
curl -O "https://my-bucket.oos-cn-gz.ctyun.cn/scripts/script.sh?Signature=..."

# Execute
bash script.sh
```

### Cloud Provider OSS Naming

| Cloud Provider | OSS Service Name | CLI Tool | Internal Endpoint Pattern |
|----------------|------------------|----------|---------------------------|
| **阿里云** | Object Storage Service (OSS) | `ossutil` | `oss-{region}.aliyuncs.com` |
| **腾讯云** | Cloud Object Storage (COS) | `coscli` | `cos.{region}.myqcloud.com` |
| **华为云** | Object Storage Service (OBS) | `obsutil` | `obs.{region}.myhuaweicloud.com` |
| **天翼云** | Object-Oriented Storage (OOS) | Web/API | `oos-{region}.ctyun.cn` |
| **AWS** | Simple Storage Service (S3) | `aws s3` | `s3.{region}.amazonaws.com` |
| **Azure** | Blob Storage | `az storage blob` | `{account}.blob.core.windows.net` |
| **GCP** | Cloud Storage | `gsutil` | `storage.googleapis.com` |
| **火山云** | TOS (Tinder Object Storage) | `tosutil` | `tos-{region}.volces.com` |
| **京东云** | Object Storage Service (OSS) | `ossutil` | `s3.{region}.jcloudcs.com` |

### Security Best Practices

```bash
# 1. Use presigned URLs (temporary, expires)
wget "https://bucket.oos.ctyun.cn/file.sh?Expires=...&Signature=..."

# 2. Use VPC internal endpoint (no public internet, free)
wget "http://oos-cn-gz-internal.ctyun.cn/file.sh"  # Internal traffic

# 3. Limit bucket policy to specific IP ranges
# 4. Enable HTTPS for all transfers
# 5. Delete file from OSS after successful download
```

### One-Liner Transfer Pattern

```bash
# From local → OSS → ECS (all in one command chain)
# Local terminal:
FILE="script.sh" BUCKET="my-bucket" && \
  ossutil cp $FILE oss://$BUCKET/tmp/ && \
  URL=$(ossutil sign oss://$BUCKET/tmp/$FILE --timeout 300 | tail -1) && \
  echo "Run this in CloudShell: wget '$URL' -O /tmp/$FILE && bash /tmp/$FILE"
```

### Comparison: Direct SSH vs OSS Transfer

| Scenario | Direct SSH/SCP | OSS Transfer | Recommendation |
|----------|---------------|--------------|----------------|
| Instance has public IP + SSH key | ✅ Fast | ⚠️ Extra steps | Use SSH/SCP |
| Instance in private subnet | ❌ Not possible | ✅ Works | Use OSS |
| Large file (>1GB) | ⚠️ Slow, may fail | ✅ Resumeable | Use OSS |
| Batch file distribution | ❌ 1-by-1 | ✅ Parallel URLs | Use OSS |
| No SSH key available | ❌ Cannot access | ✅ CloudShell + OSS | Use OSS |
| Temporary/emergency access | ❌ Setup required | ✅ Immediate | Use OSS |

### Summary

**OSS transfer is the universal fallback** when:
- CloudShell lacks file upload/download UI
- Instance has no public IP or SSH access
- Large files need reliable transfer
- Cross-cloud or cross-region file sharing

This pattern works identically across all cloud providers — just change the endpoint and CLI tool name.
