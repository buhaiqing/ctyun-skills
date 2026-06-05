# Cloud Bastion Host Integration Guide

## Cross-Skill Delegation

Bastion Host operations primarily integrate with core CTyun infrastructure services:

| Context | Skill | Interaction |
|---|---|---|
| VPC/Network | `ctyun-ecs-ops` | Bastion manages access to ECS instances |
| Monitoring | `ctyun-cloudmonitor-ops` | Monitor bastion instance health metrics |
| IAM | `ctyun-iam-ops` | Sync IAM users to bastion user list |
| Security Audit | `ctyun-cloudaudit-ops` | Cross-reference bastion access logs with CTS audit logs |

## Skill Boundary

| In scope (this skill) | Out of scope (delegate) |
|---|---|
| Bastion instance lifecycle (list, create, delete, restart) | ECS instance management → `ctyun-ecs-ops` |
| User management (create) | IAM user/group management → `ctyun-iam-ops` |
| Host asset management (add managed servers/databases) | Cloud Monitor alarm rules → `ctyun-cloudmonitor-ops` |
| Access policy management (create) | Cloud Audit log analysis → `ctyun-cloudaudit-ops` |
| | VPC/subnet management → `ctyun-vpc-ops` |

## Common Integration Patterns

### Bastion + ECS Security Flow

```
Create Bastion → Add ECS Hosts → Create Users → Create Policy
```

1. Create bastion instance in target VPC/subnet via `ctyun-bastion-ops`
2. List ECS instances in the same VPC via `ctyun-ecs-ops`
3. Add ECS instances as managed hosts in the bastion via `ctyun-bastion-ops`
4. Create users who need access via `ctyun-bastion-ops`
5. Create access policies binding users to hosts via `ctyun-bastion-ops`

### Bastion + Cloud Monitor

Monitor key bastion instance metrics:
- CPU/memory utilization (via `ctyun-cloudmonitor-ops`)
- Disk usage
- Network throughput
- Active session count