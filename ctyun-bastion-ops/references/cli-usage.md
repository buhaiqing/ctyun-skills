# Cloud Bastion Host CLI Usage

## Primary CLI: `ctyun`

> **`ctyun-cli` does not support Cloud Bastion Host operations.** Verified against `ctyun-cli v1.20.2` module list — **no bastion host subcommand exists.**

```bash
# Verify: no bastion module
ctyun --help | grep -i bastion
# (empty output — Bastion not available)
```

Since Bastion Host management is not available in `ctyun-cli`, the `cli_applicability` for this skill is `sdk-only`. Use the CTyun OSM OpenAPI REST API directly via Python `requests` with EOP signature authentication (see [`api-sdk-usage.md`](api-sdk-usage.md)).

## Alternative: curl with EOP Signature

```bash
curl -X POST "https://osm.ctapi.ctyun.cn/osm/v2/console/listInstance" \
  -H "Content-Type: application/json" \
  -H "X-Access-Key: {{env.CTYUN_ACCESS_KEY}}" \
  -H "X-Signature: {{output.eop_signature}}" \
  -H "X-Timestamp: {{output.eop_timestamp}}" \
  -d '{"pageNumber": 1, "pageSize": 10}'
```

## Evidence for `sdk-only` Tag

```
$ ctyun --help
# ... modules: ecs, monitor, redis, audit, ims, billing,
#     security, iam, ebs, cda, vpc, cce, elb, kafka, css,
#     emr, sfs, oceanfs, aone, lts ...
# No "bastion" or "osm" module present.
```