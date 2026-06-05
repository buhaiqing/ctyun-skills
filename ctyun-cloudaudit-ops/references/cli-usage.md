# Cloud Audit CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` has a different `audit` module that is NOT Cloud Audit (CTS).** The `ctyun-cli` `audit` module covers a different CTyun product. Cloud Audit (CTS) is a separate service with its own API endpoint (`cts.ctapi.ctyun.cn`).

```bash
# Verify: ctyun has an "audit" module but it's for a different product
ctyun --help | grep -i audit
# Output: audit         Audit management (different product - not Cloud Audit/CTS)

# Verify: no "cts" module for Cloud Audit
ctyun --help | grep -i cts
# (empty output — CTS not available)
```

Since Cloud Audit (CTS) is not available in `ctyun-cli`, the `cli_applicability` for this skill is `sdk-only`. Use the CTyun CTS OpenAPI REST API directly via Python `requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

```bash
curl -X POST "https://cts.ctapi.ctyun.cn/v1/cts/log/list" \
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
# "audit" module exists but is for a different product.
# No "cts" module for Cloud Audit service.
```