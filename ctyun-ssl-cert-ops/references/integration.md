# SSL Certificate Integration Guide

## Cross-Skill Delegation

SSL Certificate operations integrate with multiple CTyun services for certificate deployment:

| Context | Skill | Interaction |
|---|---|---|
| Certificate Deployment | `ctyun-elb-ops` | Deploy certificate to ELB HTTPS listeners |
| Certificate Deployment | `ctyun-cdn-ops` | Deploy certificate to CDN acceleration domains |
| Certificate Deployment | `ctyun-waf-ops` | Bind certificate to WAF protected domains |
| Monitoring | `ctyun-cloudmonitor-ops` | Set up certificate expiry alarms |

## Skill Boundary

| In scope (this skill) | Out of scope (delegate) |
|---|---|
| List/view certificates | ELB HTTPS listener config → `ctyun-elb-ops` |
| Apply new certificates | CDN HTTPS config → `ctyun-cdn-ops` |
| Upload external certificates | WAF domain config → `ctyun-waf-ops` |
| Delete certificates | Alarm rule management → `ctyun-cloudmonitor-ops` |
| Deploy certificates to resources | |
| Check certificate expiry | |
| Download certificate files | |

## Common Integration Patterns

### Certificate Lifecycle Management

```
Apply/Upload → Deploy to ELB/CDN → Monitor Expiry → Renew
```

1. Apply new certificate or upload external cert via `ctyun-ssl-cert-ops`
2. Deploy to ELB listeners via `ctyun-elb-ops`
3. Deploy to CDN domains via `ctyun-cdn-ops`
4. Set up Cloud Monitor alarms for 30-day expiry warning via `ctyun-cloudmonitor-ops`
5. Before expiry: apply renewal or upload new certificate

### Automated Certificate Rotation

```
Detect Expiring → Order New → Deploy → Delete Old
```

1. Query certificates expiring within 30 days via `ctyun-ssl-cert-ops`
2. Apply new certificate via `ctyun-ssl-cert-ops`
3. Deploy new certificate to resources (ELB/CDN/WAF)
4. Delete expired certificate via `ctyun-ssl-cert-ops`