# CTyun CCE CLI Usage

> CCE operations are available through the `ctyun cce` module.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.7.7`.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json cce cluster list` |

## CCE Commands

### Cluster Operations

```bash
# List all clusters
ctyun --output json cce cluster list --region-id <region>

# Describe a cluster
ctyun --output json cce cluster get --region-id <region> --cluster-id <cluster_id>

# Create a cluster
ctyun --output json cce cluster create --region-id <region> --name <name> --spec <spec> ...

# Delete a cluster
ctyun --output json cce cluster delete --region-id <region> --cluster-id <cluster_id>

# Get cluster kubeconfig
ctyun --output json cce cluster get-credentials --region-id <region> --cluster-id <cluster_id>
```

### Node Pool Operations

```bash
# List node pools
ctyun --output json cce node-pool list --region-id <region> --cluster-id <cluster_id>

# Get node pool details
ctyun --output json cce node-pool get --region-id <region> --cluster-id <cluster_id> --nodepool-id <nodepool_id>
```

### Workload Operations

```bash
# List workloads (deployments)
ctyun --output json cce workload list --region-id <region> --cluster-id <cluster_id> --namespace <namespace>

# Describe a workload
ctyun --output json cce workload get --region-id <region> --cluster-id <cluster_id> --namespace <namespace> --workload-name <name>

# List pods
ctyun --output json cce pod list --region-id <region> --cluster-id <cluster_id> --namespace <namespace>
```

### Monitoring

```bash
# Get cluster monitoring metrics
ctyun --output json cce monitor cluster --region-id <region> --cluster-id <cluster_id>

# Get node monitoring metrics
ctyun --output json cce monitor node --region-id <region> --cluster-id <cluster_id> --node-name <node_name>
```

## Output Format

```bash
ctyun --output json cce cluster list --region-id <region>
ctyun --output json cce cluster get --region-id <region> --cluster-id <cluster_id>
```
