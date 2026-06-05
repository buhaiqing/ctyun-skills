# SSL Certificate Troubleshooting Guide

## Common Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `statusCode: 900001` | Certificate not found | Verify certificate ID |
| `statusCode: 900002` | Invalid certificate body format | PEM format required with proper headers |
| `statusCode: 900003` | Private key does not match certificate | Verify key matches the certificate |
| `statusCode: 900004` | Certificate already exists | Duplicate detected — list and verify |
| `statusCode: 100001` | Authentication failure (EOP signature) | Recompute signature with correct AK/SK |
| `statusCode: 100002` | Invalid access key or secret key | Verify credentials |
| `DomainVerifyError` | Domain verification failed for free cert | Configure domain DNS/TXT record |
| `BrandNotAvailable` | Selected brand not available in region | Choose available brand |

## Certificate Upload Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Upload fails with format error | PEM headers missing or malformed | Ensure `-----BEGIN CERTIFICATE-----` header present |
| Upload fails with key mismatch | Private key doesn't match cert | Verify certificate and key pair match |
| Upload succeeds but cert not usable | Intermediate CA missing | Include full certificate chain |
| Private key format error | Key not in PKCS#8 format | Convert key: `openssl pkcs8 -topk8 -nocrypt` |

## Deployment Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Deploy to ELB fails | ELB listener not configured for HTTPS | Configure ELB HTTPS listener first |
| Deploy to CDN fails | CDN domain not found | Verify CDN domain exists and is active |
| Certificate still shows as deployed | Deploy not yet propagated | Wait 1-5 minutes for propagation |

## CLI/SDK Fallback

Since SSL Certificate management is `sdk-only`, there is no CLI fallback path. All operations use the REST API directly.

## Debugging Checklist

1. Verify `regionId` is correct
2. Verify certificate ID exists (list certificates first)
3. For upload: verify PEM format with proper headers and no extra whitespace
4. For apply: verify domain ownership (DNS TXT record)
5. For deploy: verify target resource exists and supports HTTPS
6. Check expiry: query expiring certificates before renewal
7. Verify API endpoint URL (`cert.ctapi.ctyun.cn` + correct path)