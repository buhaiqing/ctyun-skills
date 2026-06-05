# ELB Core Concepts

## Overview

CTyun **ELB (弹性负载均衡)** — Elastic Load Balancer — automatically
distributes incoming traffic across multiple backend servers (ECS instances)
to improve application availability and fault tolerance.

## Load Balancer

A load balancer is the entry point for traffic distribution.

**Key properties:** `LoadBalancerId`, `LoadBalancerName`, `LoadBalancerStatus`,
`Address`, `VpcId`, `SubnetId`, `CreateTime`

### Types

| Type | Description | Use Case |
|---|---|---|
| **Internal** | Private IP only, accessible within VPC | Internal microservices |
| **Public** | Public IP address, internet-facing | Web applications, APIs |

## Listener

A listener checks for connection requests from clients and forwards them to
backend servers. Each load balancer can have multiple listeners.

**Supported protocols:** `HTTP`, `HTTPS`, `TCP`

**Key properties:** `ListenerId`, `Protocol`, `Port`, `LoadBalancerId`

## Target Group

A target group routes requests to registered backend servers and performs
health checks.

**Key properties:** `TargetGroupId`, `TargetGroupName`, `Protocol`,
`HealthCheckProtocol`, `HealthCheckPort`

### Backend Server

A target (backend server) registered with a target group.

**Key properties:** `TargetId`, `TargetIp`, `Port`, `Weight`, `HealthStatus`

| Health Status | Meaning |
|---|---|
| `healthy` | Server is accepting traffic |
| `unhealthy` | Server is not accepting traffic |
| `unknown` | Health check not yet performed |

## Health Check

Health checks monitor the availability of backend servers.

**Parameters:**
- `HealthCheckProtocol` — Protocol used (HTTP/HTTPS/TCP)
- `HealthCheckPort` — Port to check
- `HealthyThreshold` — Consecutive successes to mark healthy
- `UnhealthyThreshold` — Consecutive failures to mark unhealthy
- `Interval` — Check interval (seconds)
- `Timeout` — Response timeout (seconds)

## Load Balancing Algorithms

| Algorithm | Description |
|---|---|
| **Round Robin** | Distributes requests evenly across servers |
| **Least Connections** | Sends to server with fewest active connections |
| **Source IP Hash** | Routes based on client source IP for session persistence |

## Session Persistence

When enabled, the load balancer binds a user's session to a specific backend
server, ensuring requests from the same client go to the same server.

## Related Services

- **ECS** — Backend servers for traffic
- **VPC** — Network for internal load balancers
- **EIP** — Public IP binding for internet-facing LBs
- **Cloud Monitor** — Metrics and alarms for LB performance
