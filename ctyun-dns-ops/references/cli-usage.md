# CTyun DNS CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support DNS operations.** Verified against
> `ctyun-cli v1.20.2` module list: ECS, Monitor, Redis, Audit, IMS,
> Billing, Security, IAM, EBS, CDA, VPC, CCE, ELB, Kafka, CSS, EMR,
> SFS, OceanFS, Aone, LTS — **no DNS subcommand exists.**

```bash
# Verify: no DNS module
ctyun --help | grep -i dns
# (empty output — DNS not available)
```

Since DNS is not available in `ctyun-cli`, the `cli_applicability` for this
skill is `sdk-only`. Use the CTyun DNS OpenAPI REST API directly via Python
`requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

While documented here, the primary execution path is Python `requests`.

```bash
# Generate EOP signature and call DNS API
# (requires a signing helper script — see api-sdk-usage.md)

curl -X GET "https://dns.ctapi.ctyun.cn/v4/dns/domain/list" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: {{env.CTYUN_ACCESS_KEY}}" \
  -H "X-Signature: {{output.eop_signature}}" \
  -H "X-Timestamp: {{output.eop_timestamp}}"
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "dns" module present.
```
