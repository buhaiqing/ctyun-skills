# CDN Core Concepts

## Overview

CTyun **CDN (内容分发网络)** — Content Delivery Network — accelerates
content delivery by caching static and dynamic resources at edge nodes
closer to end users, reducing latency and origin server load.

## Architecture

```
User Request
     │
     ▼
  ┌─────────┐      ┌─────────────────┐      ┌──────────────┐
  │  Edge   │─────▶│  CDN Node Cache  │─────▶│ Origin Server │
  │ Client  │      │  (Pop edge node) │      │ (ECS/OOS/...)│
  └─────────┘      └─────────────────┘      └──────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  CNAME DNS   │
                 │  Resolution  │
                 └──────────────┘
```

## Domain States

| State | Meaning | Actionable |
|---|---|---|
| `deploying` | Domain being provisioned | Wait |
| `running` | Domain is active and accelerating | Yes |
| `stopped` | Domain acceleration suspended | Start |
| `deploy_failed` | Deployment failed | Check logs, recreate |
| `deleted` | Domain removed | Re-create |

## Origin Types

| Type | Description | When to Use |
|---|---|---|
| `ip` | Origin server IP address (with port) | Direct ECS or on-premises servers |
| `domain` | Origin server domain name | Load-balanced or multi-IP origins |
| `oss` | CTyun OOS bucket | Static content from object storage |

## Cache Behaviors

| Behavior | Description |
|---|---|
| `cache_if_origin` | Cache if origin sends Cache-Control headers |
| `cache_always` | Force cache regardless of origin headers |
| `no_cache` | Bypass cache, always fetch from origin |

## HTTPS Configuration

| Feature | Description |
|---|---|
| HTTPS | Enable/disable HTTPS for CDN domain |
| HTTP/2 | Enable HTTP/2 protocol (better performance) |
| Redirect | HTTP → HTTPS automatic redirect |
| Certificate | Upload/manage SSL certificates |

## Access Control

| Feature | Description |
|---|---|
| Referer ACL | Allow/block requests based on HTTP Referer header |
| IP Blacklist | Block requests from specific IPs or CIDR ranges |
| IP Whitelist | Only allow requests from specific IPs |
| UA Filter | Block requests based on User-Agent |

## Service Types

| Type | Use Case | Optimization |
|---|---|---|
| `web` | Static website, images, JS, CSS | General web acceleration |
| `download` | Software packages, large files | Large file optimization |
| `vod` | Video-on-demand streaming | Video streaming optimization |
| `live` | Live video streaming | Live streaming acceleration |

## Billing & Quotas

- **Traffic**: Billed per GB of cached content delivered
- **Bandwidth**: Billed per Mbps (peak or 95th percentile)
- **Refresh Quota**: URL/directory refreshes per day (check plan)
- **Prefetch Quota**: Prefetch requests per day (check plan)
