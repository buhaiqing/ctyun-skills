# Cloud Bastion Host Core Concepts

## Product Overview

CTyun Cloud Bastion Host (云堡垒机原生版/OSM) provides privileged access management for cloud resources. It serves as a secure gateway for administrators to manage servers, databases, and network devices with identity authentication, permission control, and operation audit capabilities.

## Key Concepts

### Bastion Instance

A bastion instance is the core resource. It includes:
- **Specification (spec)**: Defines compute capacity
- **Asset Limit (assetsNum)**: Maximum number of managed resources
- **Concurrency (concurrencyNumber)**: Maximum concurrent sessions
- **Network**: VPC and subnet where the bastion is deployed

### Instance States

| State | Meaning |
|---|---|
| RUNNING | Instance is active and operational |
| STOPPED | Instance is stopped |
| CREATING | Instance is being provisioned |
| DELETING | Instance is being deleted |
| ERROR | Instance encountered an error |
| RESTARTING | Instance is rebooting |

### Users

Bastion users are individuals who can access managed resources through the bastion:
- **Local Users**: Created directly in the bastion
- **LDAP/AD Users**: Imported from directory services (if configured)
- Each user has: username, password, email, phone

### Hosts (Managed Assets)

Resources added to the bastion for management:
- **Servers**: Linux/Windows servers accessed via SSH/RDP
- **Databases**: MySQL, PostgreSQL, Redis databases
- **Network Devices**: Routers, switches, firewalls

**Protocol types**: `SSH`, `RDP`, `VNC`, `TELNET`, `MySQL`, `PostgreSQL`, `Redis`

### Access Policies

Policies define who can access what and when:
- **User Bindings**: Which users are authorized
- **Host Bindings**: Which hosts are accessible
- **Access Windows**: Time-based restrictions (e.g., business hours only)
- **Access Days**: Day-of-week restrictions

### Operation Auditing

The bastion records all user sessions including:
- Command history (keystroke logging for SSH)
- Screen recordings (for RDP/VNC)
- File transfer logs
- Session duration and timestamps

## SKILL.md Quick Reference

| Operation | Required Params |
|---|---|
| List Instances | (none, pagination optional) |
| Describe Instance | `vmId` |
| Create Instance | `regionId`, `instanceName`, `spec`, `assetsNum`, `concurrencyNumber`, `vpcId`, `subnetId` |
| Delete Instance | `vmId` |
| Restart Instance | `vmId` |
| Create User | `vmId`, `userName`, `password`, `email`, `phone` |
| Add Host | `vmId`, `hostIp`, `hostName`, `protocol`, `port`, `account`, `password` |
| Create Policy | `vmId`, `policyName`, `accessTime`, `accessDays`, `userIdList`, `hostIdList` |

> **Safety Gate**: `Delete Instance` and `Restart Instance` require explicit user confirmation. Deleting a bastion instance is irreversible — all logs and configurations are lost.