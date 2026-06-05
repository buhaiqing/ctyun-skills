# ECS Core Concepts

## Instance (云主机)

The fundamental compute unit in CTyun ECS. An instance is a virtual machine
running on CTyun's infrastructure, provisioned with a specific **flavor**
(CPU + RAM), **image** (OS), **system disk**, and optional **data disks**.

**States (common):**

| State | Meaning | Can transition to |
|---|---|---|
| `running` | VM is powered on and running | `stopped`, `stopping` |
| `stopped` | VM is powered off | `running`, `starting` |
| `starting` | VM booting (transient) | `running` |
| `stopping` | VM shutting down (transient) | `stopped` |
| `rebooting` | VM restarting (transient) | `running` |
| `deleted` | VM removed | terminal |

## Flavor (实例规格 / 云主机规格)

Defines the virtual hardware configuration: vCPU count, memory (GB), GPU,
local disk, and network performance tier.

Common flavor families:

| Family | Use Case | Example IDs |
|---|---|---|
| General-purpose | Web servers, small DBs | `s6.small`, `s6.medium`, `s6.large` |
| Compute-optimized | Batch processing, rendering | `c6.large`, `c6.xlarge` |
| Memory-optimized | Caches, in-memory DBs | `m6.large`, `m6.2xlarge` |
| GPU | ML training, video encoding | `g6.large`, `g6.xlarge` |

Use `ctyun ecs flavor-options --region-id <id>` to list available flavors
in a specific region.

## Image (镜像)

A template for the instance's boot volume. Contains an OS and optional
pre-installed software.

| Type | Description |
|---|---|
| **Public image** | Provided by CTyun (Ubuntu, CentOS, Windows Server, etc.) |
| **Custom image** | Created from an existing instance via `ecs create-image` |
| **Marketplace image** | Third-party images with pre-installed software stacks |

## Snapshot (快照)

A point-in-time backup of an instance's complete disk state (system + data disks).
Snapshots are incremental — only changes since the last snapshot consume new storage.

Key properties: `snapshotID`, `snapshotName`, `snapshotStatus`, `members[]` (per-disk snapshot).

Status values: `pending` → `available` → `restoring` → `error`.

## Security Group (安全组)

A virtual firewall that controls inbound and outbound traffic for instances.
Security groups operate at the instance level (not subnet level). Each instance
can be associated with one or more security groups.

Security group management is delegated to `ctyun-vpc-ops` (planned).

## Key Pair (密钥对)

An SSH key pair for secure password-less login to Linux instances.
CTyun stores the public key; the user retains the private key.

Properties: `keyPairID`, `keyPairName`, `fingerPrint`, `bindInstanceNum`.

## VPC & Subnet (私有网络 & 子网)

Instances are launched into a **VPC** (virtual private cloud) and assigned
to a specific **subnet** within that VPC. The subnet determines the instance's
IP address range and availability zone.

VPC/subnet management is delegated to `ctyun-vpc-ops` (planned).

## Async Job (异步任务)

Long-running operations (create, start, stop, resize, delete) return a `jobID`.
Use `ecs query-async-result` to poll for completion.

Job status codes:
| Code | Meaning |
|---|---|
| 0 | Executing |
| 1 | Success |
| 2 | Failed |

## Region & AZ (资源池 & 可用区)

- **Region** (`regionID`): A geographic area containing multiple, isolated
  availability zones. Example: `cn-gz` (Guangzhou), `cn-north-1`.
  Region IDs are numeric in API calls (e.g., `200000001852`).
- **Availability Zone** (`azName`): A physically isolated data center within
  a region. Use for fault tolerance (spread instances across AZs).

## Billing Models

| Model | Description |
|---|---|
| **包年包月 (Monthly/Yearly)** | Pre-paid, discounted; auto-renew configurable via `get-auto-renew-config` |
| **按量付费 (Pay-as-you-go)** | Per-hour billing, no upfront commitment |
