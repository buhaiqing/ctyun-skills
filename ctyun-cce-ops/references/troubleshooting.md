# CCE Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

```bash
pip install ctyun-cli>=1.7.7
```

### `subcommand not found`

CCE uses `ctyun cce` module. Verify with `ctyun cce --help`.

```bash
pip install --upgrade ctyun-cli
```

## API-Level Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API error | Surface `$.message` |
| `CCE.ClusterNotFound` | Cluster does not exist | Verify cluster ID |
| `CCE.ClusterCreating` | Operation during creation | Wait and retry |
| `CCE.NodePoolScaling` | Pool currently scaling | Wait for completion |
| `HTTP_403` | Insufficient permissions | Check privileges |
| `HTTP_500` | Server error | Retry with backoff |

## CCE-Specific Issues

### Cluster Creation Fails

**Possible causes:**
- Insufficient ECS quota
- VPC/subnet CIDR conflict
- Invalid flavor specification

**Resolution:**
```bash
# Check quota
ctyun ecs quota list --region-id <region>

# Verify cluster status
ctyun cce cluster get --region-id <region> --cluster-id <cluster_id>
```

### Node Pool Scaling Fails

**Possible causes:**
- Insufficient ECS resources in the AZ
- Quota exhausted for the chosen flavor

**Resolution:**
1. Check ECS resource availability
2. Try a different flavor or AZ
3. Increase ECS quota if needed

### Pod Stuck in Pending

**Possible causes:**
- Insufficient node resources (CPU/memory)
- Node selector / taints not matched
- PersistentVolume not available

**Resolution:**
1. `kubectl describe pod <pod-name>` (via kubeconfig)
2. Check node resource usage
3. Verify PVC status

### Cannot Access Cluster (kubeconfig expired)

```bash
# Regenerate kubeconfig
ctyun cce cluster get-credentials --region-id <region> --cluster-id <cluster_id>
```

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI 5xx twice | SDK fallback |
| CLI command not found | SDK fallback |
| CLI non-JSON after retry | SDK fallback |

[Full matrix](../../ctyun-skill-generator/references/cli-decision-matrix.md)
