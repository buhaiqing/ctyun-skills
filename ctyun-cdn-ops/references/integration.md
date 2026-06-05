# CDN Integration Guide

## CTyun Service Integration

### OOS + CDN

Use OOS (object storage) as the origin for CDN acceleration:

**Setup:**
1. Upload static assets to OOS bucket
2. Set bucket ACL to `public-read` or use OOS domain as origin
3. Create CDN domain with `originType: oss`
4. Configure cache rules for optimal TTL
5. Set up CNAME record in DNS (see `ctyun-dns-ops`)

### DNS + CDN

Configure CNAME records to point CDN domains to CTyun CDN:

**Setup:**
1. Get CNAME target from CDN API response
2. Create CNAME record via `ctyun-dns-ops`
3. Verify CNAME resolution before CDN domain goes live

### KMS + CDN

SSL certificates stored in KMS can be used for CDN HTTPS:

**Setup:**
1. Upload SSL certificate (see `ctyun-kms-ops`)
2. Get certificate ID from upload response
3. Configure CDN domain HTTPS with that certificate ID

### ECS + CDN

Use ECS as origin server for dynamic content:

**Setup:**
1. Deploy application on ECS
2. Create CDN domain with `originType: ip` pointing to ECS IP
3. Configure cache rules to bypass dynamic paths (no_cache)
4. Set up health checks for origin monitoring

### Cloud Monitor + CDN

Monitor CDN performance metrics and set up alarms:

- **Bandwidth alerts**: Traffic spike notification
- **Hit ratio alerts**: Low cache hit ratio
- **Error rate alerts**: 5xx origin errors
- **Status code alerts**: 4xx/5xx threshold breaches

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-dns-ops` | CNAME records for CDN domain |
| `ctyun-kms-ops` | SSL certificate for CDN HTTPS |
| `ctyun-oos-ops` | OOS bucket as CDN origin |
| `ctyun-cloudmonitor-ops` | CDN monitoring metrics and alarms |
| `ctyun-ecs-ops` | ECS server as CDN origin |
