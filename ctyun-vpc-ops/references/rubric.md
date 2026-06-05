# VPC Skill Rubric

## Overview
This rubric defines the scoring rules for the **Generator-Critic-Loop (GCL)** applied to CTyun VPC operations. The rubric follows the repository-wide 5-dimension schema with VPC-specific adaptations.

## Rubric Dimensions

### 1. Correctness (VPC-specific)
**Meaning**: Resource ID, state, and configuration actually match the request.

| Score | Criteria | VPC Examples |
|---|---|---|
| **1.0** | All parameters match exactly; VPC/subnet/route table exists with correct attributes | - VPC created with exact CIDR block `10.0.0.0/16`<br>- Subnet allocated within VPC CIDR range<br>- Route table contains correct destination-target pairs |
| **0.5** | Minor deviation (e.g., auto-assigned name differs from requested) | - VPC created but with system-generated name prefix<br>- Subnet created but availability zone differs from requested (auto-fallback) |
| **0.0** | Critical mismatch or operation failed | - VPC created with wrong CIDR block<br>- Subnet outside VPC CIDR range<br>- Route points to non-existent gateway |

**Default threshold**: ≥ 0.5 (1.0 required for `delete` operations)

### 2. Safety (Destructive Operations)
**Meaning**: Destructive operations (`delete`, `disassociate`, `remove`) were properly confirmed and guarded.

| Score | Criteria | VPC Examples |
|---|---|---|
| **1.0** | Explicit user confirmation OR safety gate passed for destructive operations | - `DeleteVpc` with "Are you sure?" confirmation<br>- `DeleteSubnet` after checking no resources attached<br>- VPC peering deletion with explicit acknowledgment |
| **0.0** | Destructive operation executed without confirmation OR safety gate bypassed | - `DeleteVpc` called without checking dependencies<br>- Route table deleted while still associated with subnets |

**Default threshold**: = 1.0 (ABORT if 0)

### 3. Idempotency
**Meaning**: Retrying the same call will not cause duplicate side-effects.

| Score | Criteria | VPC Examples |
|---|---|---|
| **1.0** | Operation is fully idempotent; repeated calls have no effect | - `CreateVpc` returns existing VPC if CIDR/name match<br>- `CreateSubnet` returns existing subnet if parameters match<br>- `DeleteVpc` returns success if VPC already deleted |
| **0.5** | Operation is mostly idempotent but may produce minor duplicate artifacts | - `CreateRoute` may create duplicate routes that need deduplication<br>- VPC peering request may create duplicate pending connections |
| **0.0** | Operation creates duplicate resources or conflicts on retry | - Each `CreateVpc` call creates new VPC with same parameters<br>- Subnet creation results in overlapping CIDR conflicts |

**Default threshold**: ≥ 0.5

### 4. Traceability
**Meaning**: Output is auditable: command, parameters, raw response, errors all captured.

| Score | Criteria | VPC Examples |
|---|---|---|
| **1.0** | Full trace includes: request parameters, SDK/API call, raw response, parsed output | - JSON logs show `vpc_id`, `request_id`, `timestamp`<br>- Error responses include full stack trace when available<br>- Execution path clearly documented |
| **0.5** | Partial trace; some elements missing but core audit trail exists | - Parameters logged but raw response truncated<br>- Successful operations logged, failures not detailed |
| **0.0** | No trace or minimal logging; cannot audit operation | - Only success/failure status returned<br>- No request/response details captured |

**Default threshold**: ≥ 0.5

### 5. Spec Compliance
**Meaning**: Conforms to the skill's `core-concepts.md` constraints and CTyun VPC API specifications.

| Score | Criteria | VPC Examples |
|---|---|---|
| **1.0** | Fully compliant with API spec and skill constraints | - CIDR blocks use RFC 1918 private ranges<br>- Subnet sizes within valid range (/16 to /28)<br>- Route destinations are valid CIDR notations |
| **0.5** | Minor deviations that don't affect functionality | - Using public IP ranges in test environments<br>- Non-standard naming conventions |
| **0.0** | Violates core constraints or API specifications | - Using invalid CIDR notation (e.g., `10.0.0.0/8`)<br>- Attempting cross-region operations not supported |

**Default threshold**: ≥ 0.5

## VPC-Specific Scoring Guidance

### Create Operations
- **Correctness**: Verify resource attributes match request (name, CIDR, region)
- **Safety**: Non-destructive but check quota limits (warn, don't block)
- **Idempotency**: Check for existing resources with same parameters
- **Traceability**: Capture `vpc_id`/`subnet_id`/`route_table_id` from response
- **Spec Compliance**: Validate CIDR ranges, naming conventions

### List/Describe Operations
- **Correctness**: Returned list matches actual resources in account
- **Safety**: Read-only, always safe
- **Idempotency**: Always idempotent
- **Traceability**: Log filter parameters and result count
- **Spec Compliance**: Use supported filter parameters

### Delete Operations
- **Correctness**: Verify resource deleted (state = `deleted` or 404)
- **Safety**: **REQUIRES EXPLICIT CONFIRMATION** + dependency check
- **Idempotency**: Handle already-deleted resources gracefully
- **Traceability**: Capture delete confirmation and `request_id`
- **Spec Compliance**: Follow delete prerequisites (no active resources)

### Update/Modify Operations
- **Correctness**: Verify changes persisted (poll if needed)
- **Safety**: Check for breaking changes (e.g., CIDR modification)
- **Idempotency**: Handle no-op updates gracefully
- **Traceability**: Capture before/after state
- **Spec Compliance**: Validate allowed modifications per API

## Critical Failure Patterns (Automatic 0.0)

| Pattern | Affected Dimensions | Reason |
|---|---|---|
| `DeleteVpc` without user confirmation | Safety (0.0) | High-risk destructive operation |
| Creating overlapping CIDR blocks | Spec Compliance (0.0) | Network conflict, violates RFC |
| Hardcoded credentials in trace | Traceability (0.0) | Security violation |
| Silent failure (exception swallowed) | Traceability (0.0) | Breaks audit trail |
| Bypassing dependency checks | Safety (0.0) | Risk of orphaned resources |

## VPC Resource Dependency Matrix

Use this for safety scoring of delete operations:

| Resource | Dependencies to Check Before Delete |
|---|---|
| VPC | - No subnets<br>- No route tables (except default)<br>- No network interfaces<br>- No VPC peering connections |
| Subnet | - No EC2 instances<br>- No RDS instances<br>- No load balancers<br>- No network interfaces |
| Route Table | - Not associated with any subnets |
| VPC Peering | - No active routes referencing peering<br>- Both sides must accept deletion |

## Scoring Examples

### Example 1: Successful VPC Creation with Confirmation
```
Correctness: 1.0  (VPC created with exact parameters)
Safety:      1.0  (Non-destructive, quota checked)
Idempotency: 1.0  (Returns existing VPC if retried)
Traceability: 1.0 (Full trace with vpc_id, request_id)
Spec Compliance: 1.0 (Valid CIDR, naming)
Total: 5.0/5.0 → PASS
```

### Example 2: Subnet Delete Without Dependency Check
```
Correctness: 1.0  (Subnet deleted)
Safety:      0.0  ❌ NO dependency check (P0 blocker)
Idempotency: 1.0  (Handles already-deleted)
Traceability: 1.0 (Full trace)
Spec Compliance: 1.0 (Valid operation)
Total: 4.0/5.0 → ABORT (Safety = 0)
```

### Example 3: Route Creation with Minor Deviation
```
Correctness: 0.5  (Route created but target gateway auto-selected)
Safety:      1.0  (Non-destructive)
Idempotency: 0.5  (May create duplicate routes)
Traceability: 1.0 (Full trace)
Spec Compliance: 1.0 (Valid CIDR, gateway)
Total: 4.0/5.0 → PASS (all thresholds met)
```

## Version History

| Version | Date | Change |
|---|---|---|
| v1 | 2026-06-05 | Initial VPC-specific rubric aligned with repository GCL schema |