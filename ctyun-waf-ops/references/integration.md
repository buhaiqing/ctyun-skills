# WAF Integration Guide

## Cross-Skill Delegation

WAF operations are self-contained within `ctyun-waf-ops`. However, WAF may be relevant in these contexts:

| Context | Skill | Interaction |
|---|---|---|
| Domain/Endpoint Protection | `ctyun-cdn-ops` | WAF can protect CDN acceleration domains |
| Certificate Management | `ctyun-ssl-cert-ops` | SSL certificates from CCMS can be bound to WAF domains |
| Load Balancer | `ctyun-elb-ops` | WAF is often deployed in front of ELB |

## Skill Boundary

| In scope (this skill) | Out of scope (delegate) |
|---|---|
| WAF instance lifecycle (list, create, delete) | SSL certificate lifecycle → `ctyun-ssl-cert-ops` |
| Domain protection management (add, remove, configure) | ELB configuration → `ctyun-elb-ops` |
| Protection rule configuration | CDN management → `ctyun-cdn-ops` |
| ACL (IP blacklist/whitelist) | IAM authorization → `ctyun-iam-ops` |
| Attack log query and analysis | |
| WAF statistics | |

## Common Integration Patterns

### WAF + SSL Certificate + CDN

```
User Request → CDN (HTTPS) → WAF (Protection) → Origin Server
```

Workflow:
1. Apply/upload SSL certificate via `ctyun-ssl-cert-ops`
2. Configure CDN HTTPS via `ctyun-cdn-ops`
3. Add WAF protection for the CDN domain via `ctyun-waf-ops`
4. Configure WAF rules and ACL as needed

### WAF + ELB

```
User Request → ELB (HTTPS Listener) → WAF (Protection) → Backend ECS
```

Workflow:
1. Configure ELB HTTPS listener via `ctyun-elb-ops`
2. Add the ELB domain to WAF protection via `ctyun-waf-ops`
3. Configure WAF protection mode and rules