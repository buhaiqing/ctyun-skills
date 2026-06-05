# DNS Core Concepts

## Overview

CTyun **DNS (云解析)** — Domain Name System service — provides domain
name resolution management on CTyun cloud. It converts human-readable
domain names (e.g., `example.com`) into IP addresses that computers use
to connect to each other.

## Architecture

```
CTyun DNS
  └── DNS Domain (zone)
        ├── Domain Name: example.com
        ├── Domain Status: active | paused | deleted
        ├── NS Record Set: Name servers for delegation
        └── Record Sets (resource records)
              ├── Type: A | AAAA | CNAME | MX | TXT | NS | SRV
              ├── Name: @ | www | api | mail | ...
              ├── Value: IP address or domain target
              ├── TTL: Time-to-live (seconds)
              ├── Priority: Route priority (MX/SRV)
              └── Resolution Line: default | telecom | unicom | mobile
```

## Record Types

| Type | Purpose | Example |
|---|---|---|
| A | Map hostname to IPv4 address | `1.2.3.4` |
| AAAA | Map hostname to IPv6 address | `2001:db8::1` |
| CNAME | Alias to another domain name | `target.example.com` |
| MX | Mail exchange server | `10 mail.example.com` |
| TXT | Arbitrary text data (SPF, DKIM, verification) | `v=spf1 include:_spf.example.com ~all` |
| NS | Name server delegation | `ns1.example.com` |
| SRV | Service location (protocol, port, target) | `0 5 5060 sip.example.com` |

## Domain States

| State | Meaning | Actionable |
|---|---|---|
| `active` | Domain is resolving | Yes |
| `paused` | Resolution suspended | Resume |
| `deleted` | Domain removed | Re-create |

## Resolution Lines

CTyun DNS supports smart resolution (智能解析) — returning different
record values based on the requester's ISP:

| Line | ISP |
|---|---|
| `default` | All other ISPs (fallback) |
| `telecom` | China Telecom |
| `unicom` | China Unicom |
| `mobile` | China Mobile |

## TTL Recommendations

| Use Case | Recommended TTL |
|---|---|
| Production A/AAAA records | 600-3600s (10 min - 1 hour) |
| CNAME records | 600-3600s |
| MX records | 3600-86400s (1 hour - 1 day) |
| TXT verification records | 60-600s (1-10 min) |
| Maintenance / migration window | 60-300s (1-5 min) |

## Security

- **DNSSEC**: Optional DNS security extension (verify if supported)
- **Rate Limiting**: API has built-in rate limiting (check API docs for limits)
- **Access Control**: API access controlled via AK/SK credentials
