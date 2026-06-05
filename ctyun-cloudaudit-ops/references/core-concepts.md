# Cloud Audit Core Concepts

## Product Overview

CTyun Cloud Audit (云审计/CTS) records all API operations performed on CTyun resources. It provides a complete history of account activity for security analysis, operational troubleshooting, and compliance auditing. Cloud Audit is a **read-only** service — it captures events but does not modify resources.

## Key Concepts

### Audit Events

Each audit event represents a single API call and contains:
- **Event ID**: Unique identifier for the event
- **Trace ID**: Unique identifier for the request trace
- **User**: Who performed the action (AK/SK user, IAM user, root account)
- **Resource Type**: The CTyun service (ECS, RDS, VPC, etc.)
- **Resource Name**: The specific resource affected
- **Event Time**: When the action occurred (UTC)
- **Source IP**: The IP address from which the request originated
- **Region**: The CTyun region where the operation occurred
- **Event Detail**: JSON payload with full request/response details

### Event Record States

| State | Meaning |
|---|---|
| NORMAL | Event recorded successfully |
| FAILED | The API operation failed (error event) |

### Key Query Dimensions

| Dimension | Description | Use Case |
|---|---|---|
| Time range | Start/end timestamps | Find events in a specific window |
| Resource type | CTyun service (e.g., `ecs`, `rds`) | Focus on specific services |
| Resource name | Specific resource identifier | Track changes to a resource |
| User name | AK/SK user or IAM user | Audit a specific user's actions |
| Event source | IP address or region | Security investigation |
| Operation type | API action name | Find specific operations |

### Resource Types

Cloud Audit covers operations across all major CTyun services including:

| Resource Type | Service |
|---|---|
| `ecs` | Elastic Compute Service |
| `rds` | Relational Database Service |
| `vpc` | Virtual Private Cloud |
| `elb` | Elastic Load Balancer |
| `eip` | Elastic IP |
| `cce` | Cloud Container Engine |
| `redis` | Redis Database Service |
| `kms` | Key Management Service |
| `waf` | Web Application Firewall |
| `oos` | Object-Oriented Storage |

### Log Export

Audit logs can be exported to an OOS bucket for long-term storage and analysis:
- Export format: JSON files
- Bucket must be in the same region as the audit source
- Exports include all events in the specified time range

### Retention

| Category | Retention |
|---|---|
| Console query | Recent 90 days |
| Exported logs | Configurable (depends on OOS lifecycle policy) |

## SKILL.md Quick Reference

| Operation | Required Params |
|---|---|
| List Audit Logs | `regionId` (pagination optional) |
| Query by Time Range | `regionId`, `startTime`, `endTime` |
| Query by Resource | `regionId`, `resourceType`, `startTime`, `endTime` |
| Query by User | `regionId`, `userName`, `startTime`, `endTime` |
| Log Detail | `regionId`, `traceId`, `eventId` |
| List Services | (none) |
| Export Logs | `regionId`, `bucketName`, `startTime`, `endTime` |
| Get Statistics | `regionId`, `startTime`, `endTime` |

> **Note**: Cloud Audit is a **read-only** service. No destructive operations exist. All operations only query existing data — no safety gates are needed.