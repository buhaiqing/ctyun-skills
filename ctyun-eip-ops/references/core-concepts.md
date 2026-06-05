# EIP Core Concepts

## Overview

CTyun **EIP (弹性公网IP)** — Elastic IP Address — provides static public
IPv4/IPv6 addresses that can be dynamically allocated, associated, and
released. EIPs enable internet-facing access for cloud resources.

## Elastic IP Lifecycle

```
Allocate → (unassociated) → Associate → (in use) → Disassociate → (unassociated) → Release
```

### States

| State | Description |
|---|---|
| **Available** | EIP allocated but not associated with any resource |
| **InUse** | EIP associated with a cloud resource (ECS, VIP, BM) |
| **Pending** | Transitional state during associate/disassociate |

## Association Types

| Type | Value | Description |
|---|---|---|
| **ECS VM** | 1 | Elastic Cloud Server virtual machine |
| **VIP** | 2 | High-availability virtual IP |
| **BM** | 3 | Bare Metal server |

## Key Parameters

| Parameter | Description | Required |
|---|---|---|
| `regionID` | Region identifier | Yes |
| `clientToken` | Idempotency token (UUID) | Yes (create/associate) |
| `eipID` | EIP resource identifier | Yes |
| `associationID` | Target instance identifier | Yes (associate) |
| `associationType` | Target instance type (1/2/3) | Yes (associate) |
| `projectID` | Enterprise project ID | No |
| `bandwidth` | Bandwidth in Mbps | For allocation |
| `name` | EIP name | For allocation |

## Billing

EIP pricing typically includes:
- **Hourly/Monthly** — Fixed period billing
- **By traffic** — Pay per GB of data transferred
- **By bandwidth** — Pay per Mbps of peak bandwidth

## Related Services

- **ECS** — Most common target for EIP association
- **ELB** — Public-facing load balancers use EIPs
- **VPC** — Network environment for EIP routing
- **Cloud Monitor** — Bandwidth and traffic monitoring
