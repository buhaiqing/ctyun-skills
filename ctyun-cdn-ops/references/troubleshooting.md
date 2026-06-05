# CDN Troubleshooting

## Common Issues

### Domain creation fails

| Symptom | Likely Cause | Solution |
|---|---|---|
| `DomainAlreadyExists` | Domain already a CDN domain | Check existing CDN domains |
| `DomainNotIcpBeian` | Domain not ICP filed | Complete ICP filing first |
| `OriginUnreachable` | Origin server not accessible | Check origin IP/domain and port |
| `InvalidOriginType` | Invalid origin type | Use ip/domain/oss |
| `SignatureNotMatch` | EOP signature incorrect | Check system clock, access/secret key |

### CDN domain not working

| Symptom | Likely Cause | Solution |
|---|---|---|
| 404 from CDN | Content not found on origin | Check origin path configuration |
| 502 Bad Gateway | Origin server error | Check origin health and connectivity |
| 403 Forbidden | Access control blocking | Review referer/IP/UA ACL rules |
| CNAME not resolving | DNS CNAME not configured | Configure CNAME at DNS provider |
| Content not updating | Cache not expired | Force refresh or wait for TTL expiry |

### Cache issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Stale content | TTL too long | Reduce cache TTL or refresh URL |
| Low hit ratio | Cache rules too restrictive | Relax cache rules for static content |
| Dynamic content cached | Wrong cache rule | Set `no_cache` for dynamic paths |
| Refresh not working | Invalid URL format | Use exact URL or directory path |

### HTTPS issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| SSL certificate error | Certificate expired or invalid | Renew certificate, update config |
| Mixed content warning | HTTP resources on HTTPS page | Update all URLs to HTTPS |
| Handshake failure | TLS version mismatch | Enable TLS 1.2/1.3 |
| Certificate not matching | Wrong domain on certificate | Get certificate for correct domain |

### Performance issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Slow first load | Cache miss (cold start) | Prefetch critical content |
| High bandwidth usage | No cache for large files | Enable caching or compress |
| High origin traffic | Low hit ratio | Optimize cache rules |
| Regional slowness | Edge node not nearby | Check CDN node coverage |

## Recovery

### Accidental domain deletion

1. Re-create the CDN domain with same configuration
2. Re-configure CNAME record in DNS
3. Prefetch critical content to warm up cache
4. Verify HTTPS and access control settings

### Failed deployment

1. Check error message from deployment response
2. Verify domain has ICP filing
3. Ensure origin server is accessible from CDN nodes
4. Retry after fixing the issue

### SSL certificate about to expire

1. Renew certificate with CA
2. Upload new certificate via `ctyun-kms-ops`
3. Update CDN HTTPS configuration with new certificate ID
4. Verify HTTPS works before old certificate expires
