# WAF Skill Rubric (v1)

## Dimension Scoring

| Dimension | Scale | Threshold | Description |
|---|---|---|---|
| **Correctness** | 0 / 0.5 / 1 | ≥ 0.5 (1.0 for `delete`) | WAF instance, domain, or rule state matches the request |
| **Safety** | 0 / 1 | = 1 | Destructive ops (`domain/delete`, `rule/delete`, ACL changes) were confirmed |
| **Idempotency** | 0 / 0.5 / 1 | ≥ 0.5 | Retrying the same call will not duplicate rules or domains |
| **Traceability** | 0 / 0.5 / 1 | ≥ 0.5 | Command, params, raw response, and errors are all captured |
| **Spec Compliance** | 0 / 0.5 / 1 | ≥ 0.5 | Conforms to `core-concepts.md` and API constraints |

## Scoring Guidelines

### Correctness (1.0)
- Instance list returns actual WAF instances in the region
- Domain added is confirmed present in the domain list
- Rule configuration matches the requested type and action
- ACL changes are reflected in subsequent ACL queries
- Attack logs returned match the queried time range
- Delete operations remove exactly the intended domain/rule

### Correctness (0.5)
- Domain was added but the response doesn't confirm the action
- Rule was configured but parameters cannot be verified independently
- API response is ambiguous about success/failure

### Safety (1.0)
- Every destructive operation received explicit user confirmation
- Confirmation included: what will be deleted, what the impact is
- Backup or verification step was performed before destructive action

### Idempotency
- 1.0: Same request can be safely retried without side effects
- 0.5: Some duplicates are handled via idempotency keys or error handling
- 0.0: No idempotency protection — retry will create duplicates

### Traceability
- 1.0: Full request/response captured, including error resolution steps
- 0.5: Command recorded but raw response truncated or missing error info
- 0.0: No execution trace recorded

### Spec Compliance
- 1.0: Follows all API constraints (required params, formats, limits)
- 0.5: Minor deviation from documented best practices
- 0.0: Violates API constraints or uses wrong parameters