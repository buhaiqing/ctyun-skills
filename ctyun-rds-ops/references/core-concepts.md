# RDS Core Concepts

## Overview

CTyun **RDS (关系型数据库)** — Relational Database Service — provides
managed relational database instances on CTyun cloud. It supports MySQL,
PostgreSQL, and SQL Server engines.

## Architecture

```
CTyun RDS
  └── RDS Instance (virtualized database server)
        ├── Engine: MySQL | PostgreSQL | SQL Server
        ├── Engine Version: 5.7, 8.0 (MySQL) | 13, 15 (PG) | 2019 (SQL Server)
        ├── Instance Type: CPU + Memory spec
        ├── Storage: SSD / ESSD, configurable size (GB)
        ├── VPC + Subnet: Network isolation
        ├── Security Group: Firewall rules
        ├── Parameter Group: Engine configuration
        └── Backups: Automated + Manual snapshots
```

## Instance States

| State | Meaning | Actionable |
|---|---|---|
| `RUNNING` | Instance is active | Yes |
| `BUILD` | Instance being provisioned | Wait |
| `STOPPED` | Instance is stopped | Start |
| `DELETING` | Instance being deleted | Wait |
| `DELETED` | Instance removed | Re-create |
| `ERROR` | Instance in error state | Check logs |
| `BACKING_UP` | Backup in progress | Wait |
| `RESTORING` | Restoring from backup | Wait |
| `RESIZING` | Spec change in progress | Wait |

## Instance Types

Instance types define the CPU and memory allocation. Format: `rds.<family>.<size>`.

| Family | Example | vCPU | Memory (GB) |
|---|---|---|---|
| s1.small | `rds.s1.small` | 1 | 2 |
| s1.medium | `rds.s1.medium` | 2 | 4 |
| s1.large | `rds.s1.large` | 4 | 8 |
| s2.xlarge | `rds.s2.xlarge` | 8 | 16 |
| s2.2xlarge | `rds.s2.2xlarge` | 16 | 32 |

> Exact types vary by region. Use the RDS Describe Specifications API for
> current availability.

## Storage

| Type | Description |
|---|---|
| SSD | General-purpose SSD, up to 6000 IOPS |
| ESSD | Enhanced SSD, up to 50000 IOPS |

Storage is billed per GB per hour. Minimum: 20 GB. Maximum: 6000 GB (varies by instance type).

## Backup

| Backup Type | Description | Retention |
|---|---|---|
| Automated | Daily automatic backup | Configurable (7-35 days) |
| Manual | User-initiated snapshot | Until manually deleted |

## Security

- **VPC Isolation**: Each instance is deployed in a customer VPC
- **Security Groups**: IP-based firewall rules (inbound/outbound)
- **SSL Connection**: TLS encryption for data in transit
- **Account Management**: Master account credentials set at creation
