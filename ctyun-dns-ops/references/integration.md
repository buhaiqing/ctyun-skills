# DNS Integration Guide

## CTyun Service Integration

### CDN + DNS

When setting up CDN acceleration, configure CNAME records through DNS:

**Setup:**
1. Get CNAME target from CDN domain creation response
2. Create a CNAME record in DNS: `cdn.example.com CNAME cdn.example.com.ctyuncdn.cn`
3. Wait for DNS propagation (TTL-dependent)
4. Verify CDN is active

### ECS + DNS

Applications on ECS can use CTyun DNS for service discovery:

**Setup:**
1. Create A records pointing to ECS instances
2. For HA, create multiple A records with same name (round-robin)
3. For failover, use monitoring-based resolution

### HTTPS Certificate Verification (KMS)

DNS TXT records are commonly used for domain ownership verification:

**Setup:**
1. Request SSL certificate (see `ctyun-kms-ops`)
2. Get TXT record value from certificate authority
3. Create TXT record in DNS
4. Certificate authority verifies ownership
5. After verification, TXT record can be removed

## Cross-Skill Integration

| Skill | Integration Point |
|---|---|
| `ctyun-cdn-ops` | CNAME records for CDN domain acceleration |
| `ctyun-kms-ops` | Domain ownership verification for SSL certificates |
| `ctyun-cloudmonitor-ops` | DNS monitoring metrics and alarm rules |
| `ctyun-elb-ops` | A records pointing to load balancer VIP |
| `ctyun-ecs-ops` | A records pointing to ECS instance IPs |
