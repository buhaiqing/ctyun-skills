# ELB Troubleshooting Guide

## CLI-Level Errors

### `ctyun: command not found`

```bash
pip install ctyun-cli>=1.7.7
```

### `subcommand not found`

```bash
pip install --upgrade ctyun-cli
```

### `not authenticated`

Check `~/.ctyun/config` and credentials.

## API-Level Errors

| Error | Likely Cause | Resolution |
|---|---|---|
| `statusCode != 800` | API error | Surface `$.message` |
| `ELB.NotFound` | LB/target group not found | Verify IDs |
| `ELB.CreateFailed` | Invalid params or quota | Check params |
| `HTTP_403` | Insufficient permissions | Check privileges |
| `HTTP_500` | Server error | Retry with backoff |

## ELB-Specific Issues

### 502/503 Errors from Load Balancer

**Possible causes:**
- Backend targets all unhealthy
- Health check configuration incorrect
- Backend server not listening on the expected port

**Resolution:**
```bash
# 1. Check target health
ctyun elb targetgroup targets list --region-id <region> --targetgroup-id <tg_id>

# 2. Check health check config
ctyun elb health-check show --region-id <region> --health-check-id <hc_id>

# 3. Verify backend server is running
```

### Backend Server Unhealthy

**Possible causes:**
- Server is stopped or overloaded
- Security group blocks health check traffic
- Application on backend crashed

**Resolution:**
1. Verify ECS instance is running
2. Check security group allows health check traffic
3. Verify application is listening on the correct port

### Target Registration Fails

**Possible causes:**
- Target already registered
- Target in different VPC
- Target network unreachable

**Resolution:**
- Verify target IP and VPC membership
- Use SDK (SDK-only operation if CLI unavailable)

## SDK Fallback Triggers

| Condition | Action |
|---|---|
| CLI 5xx twice | SDK fallback for op |
| CLI command not found | SDK fallback |
| CLI non-JSON after retry | SDK fallback |
| Create/delete/update (SDK-only) | Use SDK directly |

[Full matrix](../../ctyun-skill-generator/references/cli-decision-matrix.md)
