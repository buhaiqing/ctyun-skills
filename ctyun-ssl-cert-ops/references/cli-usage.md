# SSL Certificate CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support SSL Certificate management operations.** Verified against `ctyun-cli v1.20.2` module list — **no certificate management subcommand exists.**

```bash
# Verify: no cert module
ctyun --help | grep -i cert
# (empty output — SSL Certificate not available)
```

Since SSL Certificate management is not available in `ctyun-cli`, the `cli_applicability` for this skill is `sdk-only`. Use the CTyun Certificate OpenAPI REST API directly via Python `requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

```bash
curl -X POST "https://cert.ctapi.ctyun.cn/v1/certificate/list" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: {{env.CTYUN_ACCESS_KEY}}" \
  -H "X-Signature: {{output.eop_signature}}" \
  -H "X-Timestamp: {{output.eop_timestamp}}" \
  -d '{"regionId": "{{env.CTYUN_REGION_ID}}", "pageNumber": 1, "pageSize": 20}'
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "cert" or "certificate" module present.
```