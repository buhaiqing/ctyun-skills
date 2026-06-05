---
name: ctyun-cce-ops
version: 1.0.0
description: >
  Manage CTyun CCE (云容器引擎) — Cloud Container Engine for Kubernetes cluster
  lifecycle, node pools, workloads, and monitoring. Primary route for any
  container/Kubernetes cluster task.
metadata:
  cli_applicability: dual-path
  cli_version_locked: ">=1.7.7"
  sdk_version_locked: ">=1.0.0"
  api_profile: cce.ctyun.cn
  api_version: v1
  lifecycle: shipped
---

# ctyun-cce-ops

## Trigger & Scope

### SHOULD Use

- List, describe, create, or delete Kubernetes clusters
- Manage node pools (create, scale, delete)
- View cluster credentials (kubeconfig)
- List and describe workloads (deployments, services, pods)
- Manage ConfigMaps and Secrets
- View cluster and node monitoring metrics
- Cluster upgrade and maintenance operations
- Any CCE/Kubernetes related tasks

### SHOULD NOT Use

- ECS instance management → delegate to `ctyun-ecs-ops`
- ELB/load balancer configuration → delegate to `ctyun-elb-ops`
- EIP allocation → delegate to `ctyun-eip-ops`
- Cloud monitor alarm rules → delegate to `ctyun-cloudmonitor-ops`
- Container image registry → delegate to `ctyun-swr-ops` (planned)
- IAM user/policy → delegate to `ctyun-iam-ops`

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "CCE" or "container engine" | Route here |
| User asks about "K8s" or "Kubernetes" | Route here |
| User asks about "cluster" | Route here (K8s context) |
| User asks about "node pool" | Route here |
| User asks about "workload" or "deployment" | Route here |
| User asks about "ELB" or "load balancer" | Route to `ctyun-elb-ops` |
| User asks about "EIP" or "public IP" | Route to `ctyun-eip-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{user.region_id}}` | Ask once, cache per session | region ID |
| `{{user.cluster_id}}` | Ask once, cache per session | cluster UUID |
| `{{user.nodepool_id}}` | Ask once, cache per session | node pool ID |
| `{{user.cluster_name}}` | Ask once, cache per session | cluster name |
| `{{output.cluster_id}}` | Parsed from JSON response | from create response |
| `{{output.kubeconfig}}` | Parsed from JSON response | cluster access config |

---

## Execution Flows

All operations follow the **ctyun-first with SDK fallback** policy.

### Pre-flight

1. Verify `ctyun` CLI (>= 1.7.7)
2. Verify credentials
3. Determine region ID

### Flow A: List Clusters

**CLI path (primary):**

```bash
ctyun --output json cce cluster list \
  --region-id {{user.region_id}}
```

**SDK fallback:**

```python
from ctyun_sdk.services.cce import CCEClient

client = CCEClient(
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
clusters = client.list_clusters(region_id="{{user.region_id}}")
```

**Validation:** Check `$.statusCode == 800`.

### Flow B: Describe Cluster

```bash
ctyun --output json cce cluster get \
  --region-id {{user.region_id}} \
  --cluster-id {{user.cluster_id}}
```

### Flow C: List Node Pools

```bash
ctyun --output json cce node-pool list \
  --region-id {{user.region_id}} \
  --cluster-id {{user.cluster_id}}
```

### Flow D: Get Cluster Credentials (Kubeconfig)

```bash
ctyun --output json cce cluster get-credentials \
  --region-id {{user.region_id}} \
  --cluster-id {{user.cluster_id}}
```

### Flow E: List Workloads

```bash
ctyun --output json cce workload list \
  --region-id {{user.region_id}} \
  --cluster-id {{user.cluster_id}} \
  --namespace {{user.namespace}}
```

---

## Output Parsing Rules

```json
{
  "statusCode": 800,
  "message": "成功",
  "returnObj": { ... }
}
```

| Operation | Data Path | Key Fields |
|---|---|---|
| List clusters | `$.returnObj[]` | `clusterId, clusterName, status, version` |
| Describe cluster | `$.returnObj` | `clusterId, clusterName, status, version, nodeCount` |
| List node pools | `$.returnObj[]` | `nodePoolId, name, nodeCount, flavor` |
| List workloads | `$.returnObj[]` | `name, namespace, replicas, status` |
| Get kubeconfig | `$.returnObj` | `config` (base64-encoded kubeconfig) |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != 800` | Business | No | Surface `$.message` |
| `ctyun: command not found` | Environment | 3x | `pip install ctyun-cli>=1.7.7` |
| `5xx` / timeout | Runtime | 1x, then SDK | Retry once; SDK fallback |
| `subcommand not found` | Capability | No | Check CLI version; SDK fallback |
| `CCE.*ClusterDelete.*` | Safety | No | Require explicit user confirmation |

> **Safety Gate:** Cluster delete and node pool delete operations are destructive and may
> cause permanent data loss. **REQUIRED:** Before executing, obtain explicit user confirmation
> including the cluster/resource ID and a clear statement of consequences. Document the
> confirmation in the execution trace.

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Cluster delete can cause data loss |
| `max_iterations` | `2` | inherited from §8 CCE default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for cluster delete operations |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-cce-ops skill — cluster, node pool, workload operations |
