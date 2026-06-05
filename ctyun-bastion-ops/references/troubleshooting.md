# Cloud Bastion Host Troubleshooting Guide

## Common Errors

| Error | Likely Cause | Solution |
|---|---|---|
| `statusCode: "1"` | Authentication failure (EOP signature) | Recompute signature with correct AK/SK |
| `statusCode: "1000"` | Invalid parameter | Verify all required parameters are present |
| `statusCode: "2001"` | Resource not found | Verify `vmId` is correct |
| `statusCode: "2002"` | Resource already exists | Duplicate instance name or asset |
| `statusCode: "3001"` | Insufficient quota | Request quota increase from CTyun console |
| `statusCode: "4001"` | Operation not allowed in current state | Check instance status (e.g., cannot restart a CREATING instance) |
| `TimeoutError` | Bastion API not responding | Retry with exponential backoff |

## Instance Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| Create instance stuck in CREATING | Resource provisioning in progress | Wait 5-10 minutes, check status |
| Delete instance failed | Instance has active connections | Verify no users are logged in |
| Restart instance takes long | Operating system shutdown | Wait up to 5 minutes, check status |
| Instance in ERROR state | Underlying infrastructure issue | Contact CTyun support |

## User & Host Issues

| Symptom | Likely Cause | Solution |
|---|---|---|
| User cannot log in | User not yet created in bastion | Verify user creation succeeded |
| Host not accessible | Host credentials incorrect | Verify host account/password |
| Policy not working | Policy not applied to user/host | Verify user and host are bound to policy |
| Connection refused | Host firewall blocking bastion IP | Add bastion IP to host security group allowlist |

## CLI/SDK Fallback

Since Bastion Host is `sdk-only`, there is no CLI fallback path. All operations use the REST API directly.

## Debugging Checklist

1. Verify `vmId` is correct (list instances first)
2. Check instance status is RUNNING before operations
3. Verify VPC/subnet routing allows bastion access to hosts
4. For user creation: verify password meets complexity requirements
5. For host addition: verify the host is reachable from the bastion
6. For policy creation: verify both users and hosts exist
7. Verify API endpoint URL (`osm.ctapi.ctyun.cn` + correct path)