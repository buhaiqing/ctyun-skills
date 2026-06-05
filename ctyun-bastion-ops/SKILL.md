---
name: ctyun-bastion-ops
version: 1.0.0
description: >
  Manage CTyun Cloud Bastion Host (云堡垒机原生版/OSM) resources — bastion
  instances, managed hosts, users, access policies, and audit sessions.
  Primary route for any bastion host or privileged access management task.
metadata:
  cli_applicability: sdk-only
  cli_version_locked: null
  sdk_version_locked: null
  api_profile: osm.ctapi.ctyun.cn
  api_version: v2
  lifecycle: shipped
---

# ctyun-bastion-ops

## Trigger & Scope

### SHOULD Use

- List bastion host instances
- Describe bastion instance details
- Create a new bastion host instance
- Delete a bastion host instance
- Restart a bastion host instance
- Create bastion users (local accounts)
- Add managed hosts to bastion
- Create access policies
- Query bastion audit sessions and logs
- Modify bastion instance specifications
- Manage bastion user groups

### SHOULD NOT Use

- ECS instance lifecycle → delegate to `ctyun-ecs-ops`
- VPC/subnet configuration → delegate to network skills
- Security group rules → delegate to `ctyun-ecs-ops` or similar
- IAM identity management → delegate to `ctyun-iam-ops`
- Operating system user management → delegate to OS-level tools

### Delegation Rules

| Condition | Action |
|---|---|
| User asks about "bastion" or "堡垒机" or "OSM" | Route here |
| User asks about "privileged access" or "jump host" | Route here |
| User asks about "bastion user" or "bastion host" | Route here |
| User asks about "ECS" or "云服务器" | Route to `ctyun-ecs-ops` |
| User asks about "IAM" or "identity" or "权限" | Route to `ctyun-iam-ops` |

---

## Variable Convention

| Pattern | Resolution | Example |
|---|---|---|
| `{{env.CTYUN_ACCESS_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Agent runtime env | never prompt |
| `{{env.CTYUN_REGION_ID}}` | Agent runtime env | `cn-gz` |
| `{{env.BASTION_ENDPOINT}}` | Agent runtime env | `osm.ctapi.ctyun.cn` |
| `{{user.instance_id}}` | Ask once, cache per session | `osm-xxxxxxxx` |
| `{{user.instance_name}}` | Ask once, cache per session | `prod-bastion-01` |
| `{{user.spec}}` | Ask once, cache per session | `enterprise` / `professional` |
| `{{user.assets_num}}` | Ask once, cache per session | `20` |
| `{{user.concurrent_num}}` | Ask once, cache per session | `100` |
| `{{user.vpc_id}}` | Ask once, cache per session | `vpc-xxxxxxxx` |
| `{{user.subnet_id}}` | Ask once, cache per session | `subnet-xxxxxxxx` |
| `{{user.bastion_user_name}}` | Ask once, cache per session | `operator` |
| `{{user.host_ip}}` | Ask once, cache per session | `10.0.0.1` |
| `{{output.statusCode}}` | Parsed from JSON response | `"0"` (string, not number) |
| `{{output.instance_list}}` | Parsed from JSON response | from ListInstances |
| `{{output.instance_status}}` | Parsed from JSON response | `running` / `stopped` / `error` |

---

## Execution Flows

All operations follow the **SDK-only** policy because CTyun CLI does not
support bastion host operations (verified: `ctyun bastion` subcommand does
not exist). The primary path uses direct REST API calls to CTyun Bastion
OpenAPI endpoints with EOP signature authentication.

> **Note:** This skill uses `statusCode` as a **string** `"0"` for
> success — not a number. All code examples reflect this difference.

### Pre-flight

1. Verify Python 3.10+ environment
2. Install `requests` library: `pip install requests`
3. Verify credentials (`CTYUN_ACCESS_KEY`, `CTYUN_SECRET_KEY`)
4. Determine region ID and bastion endpoint
5. Set up EOP signature helper (see [`references/api-sdk-usage.md`](references/api-sdk-usage.md) §Authentication)

### Flow A: List Bastion Instances

```python
import requests
from eop_signer import sign_request  # see api-sdk-usage.md

url = f"https://{BASTION_ENDPOINT}/osm/v2/console/listInstance"
headers = sign_request(
    method="POST",
    url=url,
    body={},
    access_key="{{env.CTYUN_ACCESS_KEY}}",
    secret_key="{{env.CTYUN_SECRET_KEY}}"
)
resp = requests.post(url, headers=headers, json={
    "pageNumber": 1,
    "pageSize": 10
})
data = resp.json()
```

**Validation:** Check `$.statusCode == "0"` (string). Parse `$.returnObj[]` and `$.page` for pagination.

### Flow B: Describe Bastion Instance Details

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/describeInstance"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}"
})
```

### Flow C: Create Bastion Instance

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/createInstance"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "regionId": "{{env.CTYUN_REGION_ID}}",
    "instanceName": "{{user.instance_name}}",
    "spec": "{{user.spec}}",              # enterprise | professional
    "assetsNum": {{user.assets_num}},      # number of managed assets
    "concurrencyNumber": {{user.concurrent_num}},  # max concurrent sessions
    "vpcId": "{{user.vpc_id}}",
    "subnetId": "{{user.subnet_id}}",
    "chargeType": "postPaid"              # postPaid | prePaid
})
```

> **Note:** Bastion instances take several minutes to provision. Use polling
> or describe instance to check status after creation.

### Flow D: Delete Bastion Instance

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/deleteInstance"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}"
})
```

> **Safety Gate:** This operation is IRREVERSIBLE and will delete all
> bastion data including users, hosts, policies, and audit logs.
> **REQUIRED:**
>
> 1. Verify no active sessions are running on this bastion
> 2. Confirm audit logs have been exported if needed
> 3. Verify all managed hosts have alternative access methods
> 4. Ask user explicitly: "Delete bastion instance
>    `{{user.instance_name}}` (ID: `{{user.instance_id}}`)? This will
>    permanently delete all bastion data including users, hosts, policies,
>    and audit logs."
> 5. Only proceed on explicit `yes` confirmation

### Flow E: Restart Bastion Instance

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/rebootInstance"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}"
})
```

> **Safety Gate:** Restarting will interrupt all active sessions.
> **REQUIRED:**
>
> 1. Confirm no critical active sessions
> 2. Ask user explicitly: "Restart bastion instance `{{user.instance_name}}`? All active sessions will be terminated."
> 3. Only proceed on explicit `yes` confirmation

### Flow F: Create Bastion User

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/createUser"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}",
    "userName": "{{user.bastion_user_name}}",
    "password": "{{user.bastion_password}}",
    "email": "{{user.email}}",
    "phone": "{{user.phone}}",
    "expireTime": "{{user.expire_time}}"  # optional: user account expiry
})
```

### Flow G: Add Managed Host

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/createHost"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}",
    "hostIp": "{{user.host_ip}}",
    "hostName": "{{user.host_name}}",
    "protocol": "SSH",                    # SSH | RDP | Telnet | VNC
    "port": 22,
    "account": "{{user.host_account}}",
    "password": "{{user.host_password}}"
})
```

### Flow H: Create Access Policy

```python
url = f"https://{BASTION_ENDPOINT}/osm/v2/console/createPolicy"
headers = sign_request("POST", url, ...)
resp = requests.post(url, headers=headers, json={
    "vmId": "{{user.instance_id}}",
    "policyName": "{{user.policy_name}}",
    "userIdList": ["{{user.bastion_user_id}}"],
    "hostIdList": ["{{user.host_id}}"],
    "accessTime": "00:00-23:59",          # allowed access time window
    "accessDays": [1,2,3,4,5],            # allowed days (1=Mon, 7=Sun)
    "commandFilter": ""                    # optional command blacklist
})
```

---

## Output Parsing Rules

Bastion API responses use `statusCode` as a **string** `"0"` for success.

| Operation | Data Path | Key Fields |
|---|---|---|
<!-- markdownlint-disable MD013 -->
| List Instances | `$.returnObj[]` | `id, instanceName, regionId, regionName, specName, assetsNum, concurrencyNumber, status, createTime, expireDate` |
| Describe Instance | `$.returnObj` | `id, instanceName, specName, assetsNum, concurrencyNumber, vpcId, subnetId, eipAddress, cpuNum, memSize, vmHd, vmHdUsed, status` |
<!-- markdownlint-enable MD013 -->
| Create Instance | `$.returnObj` | `vmId, orderId` |
| Delete Instance | `$.returnObj` | `vmId, status` |
| Restart Instance | `$.returnObj` | `vmId, status` |
| Create User | `$.returnObj` | `userId, userName, email, status` |
| Create Host | `$.returnObj` | `hostId, hostIp, hostName, protocol, port` |
| Create Policy | `$.returnObj` | `policyId, policyName, userIdList, hostIdList` |

---

## Failure Recovery

| Pattern | Class | Retry? | Action |
|---|---|---|---|
| `statusCode != "0"` | Business | No | Surface `$.message` |
| `InstanceNotFound` | Business | No | Verify instance ID |
| `UserAlreadyExists` | Business | No | Username already in use on this bastion |
| `HostAlreadyManaged` | Business | No | Host already added to this bastion |
| `InvalidPassword` | Business | No | Password does not meet complexity requirements |
| `InsufficientQuota` | Business | No | Asset/connection quota exceeded |
| `SignatureNotMatch` | Environment | 1x | Check credentials and system clock |
| `5xx` / timeout | Runtime | 3x exponential backoff | Retry with 2s → 4s → 8s |
| `requests` ImportError | Environment | 1x | `pip install requests` |

---

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` | Delete/reboot instance destroys bastion access and audit data |
| `max_iterations` | `2` | inherited from §8 destructive ops default |
| `rubric_version` | `v1` | see [`references/rubric.md`](references/rubric.md) |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` | for delete/reboot instance |
| `fallback_decision_table` | [`../ctyun-skill-generator/references/cli-decision-matrix.md`](../ctyun-skill-generator/references/cli-decision-matrix.md) | CLI-first decision table |

### Artifacts

- [`references/rubric.md`](references/rubric.md)
- [`references/prompt-templates.md`](references/prompt-templates.md)

---

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial ctyun-bastion-ops skill — instance CRUD, user/host management, access policies |
