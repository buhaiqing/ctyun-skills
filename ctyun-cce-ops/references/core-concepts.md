# CCE Core Concepts

## Overview

CTyun **CCE (云容器引擎)** — Cloud Container Engine — provides managed
Kubernetes clusters for containerized application deployment, scaling,
and management.

## Architecture

```
Internet → ELB → Node (ECS VM) → Pod (Container)
                                    ↓
                              Workload (Deployment/StatefulSet/DaemonSet)
                                    ↓
                              ConfigMap / Secret
```

## Cluster Types

| Type | Description | Use Case |
|---|---|---|
| **Standard** | Managed control plane, user-managed nodes | Production workloads |
| **Trial** | Single-node cluster | Development / testing |

## Key Resources

| Resource | Description |
|---|---|
| **Cluster** | Kubernetes control plane + node group |
| **Node Pool** | Group of worker nodes with same flavor |
| **Workload** | Deployment, StatefulSet, DaemonSet, Job |
| **Service** | Stable network endpoint for pods |
| **ConfigMap** | Non-sensitive configuration data |
| **Secret** | Sensitive data (passwords, tokens) |
| **Namespace** | Virtual cluster for resource isolation |

## Cluster Lifecycle

```
Creating → Running → Upgrading → Running
                          ↓
                      Deleting → Deleted
```

## Billing

- **Master nodes** — billed by cluster specification
- **Worker nodes** — billed by ECS instance type
- **Storage** — billed by EVS disk usage
- **Network** — billed by ELB/EIP usage

## Related Services

- **ECS** — Worker nodes are ECS instances under the cluster
- **ELB** — Services exposed via load balancer
- **EIP** — Public access for cluster API
- **EVS** — Persistent storage for workloads
