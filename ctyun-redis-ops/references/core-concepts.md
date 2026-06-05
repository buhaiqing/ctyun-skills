# Redis Core Concepts

## Overview

CTyun **Redis (分布式缓存)** — Distributed Cache Service — provides
in-memory caching compatible with the Redis protocol. It supports multiple
editions, engine versions, and deployment topologies for different
performance and availability requirements.

## Redis Instance

A Redis instance is a managed cache node or cluster. Each instance has:

**Key properties:** `InstanceId`, `InstanceName`, `EngineVersion`, `Edition`,
`ShardMemSize`, `Status`, `VpcId`, `SubnetId`, `ZoneName`

### Editions

| Edition | Description | Use Case |
|---|---|---|
| **StandardSingle** | Single-node deployment, 1 replica | Dev/test, low-cost caching |
| **StandardCluster** | Master-slave with HA, automatic failover | Production workloads |
| **DistributedCluster** | Sharded cluster, data distributed across multiple shards | Large-scale caching (>32GB) |

### Engine Versions

| Version | Status |
|---|---|
| 4.0 | Legacy |
| 5.0 | Stable |
| 6.0 | Recommended (default) |
| 7.0 | Latest |

## Network & Security

Redis instances run inside a VPC:
- **VPC** — Virtual Private Cloud that contains the instance
- **Subnet** — Subnet within the VPC for IP allocation
- **Security Group** — Firewall rules controlling inbound/outbound traffic

## Backup & Restore

| Operation | Description |
|---|---|
| **Manual Backup** | Create a full backup of the instance |
| **Auto Backup** | Configurable backup window and retention period |
| **Restore** | Restore from backup to a new instance |

## Performance Metrics

| Metric | Description |
|---|---|
| `CPUUtilization` | CPU usage percentage |
| `MemoryUsage` | Memory usage percentage |
| `QPS` | Queries per second |
| `Connections` | Active connections |
| `KeyCount` | Number of keys in the instance |
| `CacheHitRate` | Cache hit ratio |
| `NetworkIn/Out` | Network throughput |

## State Transitions

```
Creating → Active → Modifying → Active
Active → Deleting → (removed)
Active → BackingUp → Active
Active → Restoring → Active
```

## Related Services

- **CTyun Cloud Monitor** — Set alarm rules for Redis metrics
- **ECS** — Application servers that connect to Redis
- **VPC** — Network environment for Redis deployment
