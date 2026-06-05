# CTyun RDS CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support RDS operations.** Verified against
> `ctyun-cli v1.20.2` module list: ECS, Monitor, Redis, Audit, IMS,
> Billing, Security, IAM, EBS, CDA, VPC, CCE, ELB, Kafka, CSS, EMR,
> SFS, OceanFS, Aone, LTS — **no RDS subcommand exists.**

```bash
# Verify: no RDS module
ctyun --help | grep -i rds
# (empty output — RDS not available)
```

Since RDS is not available in `ctyun-cli`, the `cli_applicability` for this
skill is `sdk-only`. Use the CTyun RDS OpenAPI REST API directly via Python
`requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

While documented here, the primary execution path is Python `requests`.

```bash
# Generate EOP signature and call RDS API
# (requires a signing helper script — see api-sdk-usage.md)

curl -X POST "https://ctrds.ctapi.ctyun.cn/v4/rds/instance/list" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: {{env.CTYUN_ACCESS_KEY}}" \
  -H "X-Signature: {{output.eop_signature}}" \
  -d '{"regionId": "{{env.CTYUN_REGION_ID}}"}'
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "rds" module present.
```
