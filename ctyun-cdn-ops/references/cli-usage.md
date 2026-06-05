# CTyun CDN CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support CDN operations.** Verified against
> `ctyun-cli v1.20.2` module list: ECS, Monitor, Redis, Audit, IMS,
> Billing, Security, IAM, EBS, CDA, VPC, CCE, ELB, Kafka, CSS, EMR,
> SFS, OceanFS, Aone, LTS — **no CDN subcommand exists.**

```bash
# Verify: no CDN module
ctyun --help | grep -i cdn
# (empty output — CDN not available)
```

Since CDN is not available in `ctyun-cli`, the `cli_applicability` for this
skill is `sdk-only`. Use the CTyun CDN OpenAPI REST API directly via Python
`requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

While documented here, the primary execution path is Python `requests`.

```bash
# Generate EOP signature and call CDN API
# (requires a signing helper script — see api-sdk-usage.md)

curl -X GET "https://cdn.ctapi.ctyun.cn/v2/cdn/domain/list" \
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
# No "cdn" module present.
```
