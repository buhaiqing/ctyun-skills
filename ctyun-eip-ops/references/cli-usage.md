# CTyun EIP CLI Usage

> EIP operations are available through the `ctyun vpc` module.
> The `ctyun` command is installed via `pip install ctyun-cli>=1.7.7`.

## Global Flags

| Flag | Placement | Example |
|---|---|---|
| `--output json` | **Before** subcommand | `ctyun --output json vpc list-eips` |

## EIP Commands

### `vpc list-eips` — List EIPs

```bash
ctyun --output json vpc list-eips \
  --region-id <region>
```

Output fields: `eipId, eipAddress, bandwidth, status, createTime, instanceId, instanceType`

### `vpc describe-eip` — Describe an EIP

```bash
ctyun --output json vpc describe-eip \
  --region-id <region> \
  --eip-id <eip_id>
```

Output fields: `eipId, eipAddress, bandwidth, status, instanceId, instanceType, createTime, projectId`

### `vpc create-eip` — Allocate an EIP

```bash
ctyun --output json vpc create-eip \
  --region-id <region> \
  --bandwidth <bandwidth_mbps> \
  --name <eip_name> \
  --client-token <uuid>
```

Output fields: `eipId, eipAddress, bandwidth, status, createTime`

### `vpc associate-eip` — Associate EIP to instance

```bash
ctyun --output json vpc associate-eip \
  --region-id <region> \
  --eip-id <eip_id> \
  --instance-id <instance_id> \
  --instance-type <type> \
  --client-token <uuid>
```

Instance types: 1 (ECS VM), 2 (VIP), 3 (BM)

### `vpc disassociate-eip` — Disassociate EIP from instance

```bash
ctyun --output json vpc disassociate-eip \
  --region-id <region> \
  --eip-id <eip_id>
```

### `vpc delete-eip` — Release an EIP

```bash
ctyun --output json vpc delete-eip \
  --region-id <region> \
  --eip-id <eip_id>
```

> **Warning:** This operation is IRREVERSIBLE. The released IP address is
> returned to the pool and cannot be recovered.

## API Endpoints (when using SDK directly)

| Operation | API Endpoint |
|---|---|
| Allocate EIP | `POST /v4/eip/create` |
| Associate EIP | `POST /v4/eip/associate` |
| Disassociate EIP | `POST /v4/eip/disassociate` |
| Release EIP | `POST /v4/eip/delete` |
| List EIPs | `GET /v4/eip/list` |
| Describe EIP | `GET /v4/eip/describe` |

## Output Format

```bash
ctyun --output json vpc list-eips --region-id <region>
ctyun --output json vpc create-eip --region-id <region> --bandwidth 10 --name "my-eip"
