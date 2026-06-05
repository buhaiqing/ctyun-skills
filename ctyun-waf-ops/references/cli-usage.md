# CTyun WAF CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support WAF operations.** Verified against `ctyun-cli v1.20.2` module list: ECS, Monitor, Redis, Audit, IMS, Billing, Security, IAM, EBS, CDA, VPC, CCE, ELB, Kafka, CSS, EMR, SFS, OceanFS, Aone, LTS — **no WAF subcommand exists.**

```bash
# Verify: no WAF module
ctyun --help | grep -i waf
# (empty output — WAF not available)
```

Since WAF is not available in `ctyun-cli`, the `cli_applicability` for this skill is `sdk-only`. Use the CTyun WAF OpenAPI REST API directly via Python `requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

```bash
curl -X POST "https://waf.ctapi.ctyun.cn/v2/waf/instance/list" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: {{env.CTYUN_ACCESS_KEY}}" \
  -H "X-Signature: {{output.eop_signature}}" \
  -H "X-Timestamp: {{output.eop_timestamp}}" \
  -d '{"regionId": "{{env.CTYUN_REGION_ID}}"}'
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "waf" module present.
```