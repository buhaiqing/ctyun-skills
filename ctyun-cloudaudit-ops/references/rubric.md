# Cloud Audit Skill Rubric (v1)

## Dimension Scoring

| Dimension | Scale | Threshold | Description |
|---|---|---|---|
| **Correctness** | 0 / 0.5 / 1 | ≥ 0.5 | Audit log query results match the requested filters |
| **Safety** | 0 / 1 | = 1 | Read-only operation — no mutations, safety always = 1 by design |
| **Idempotency** | 0 / 0.5 / 1 | ≥ 0.5 | Same query returns consistent results (read-only, inherently idempotent) |
| **Traceability** | 0 / 0.5 / 1 | ≥ 0.5 | Query params, raw response, and errors are all captured |
| **Spec Compliance** | 0 / 0.5 / 1 | ≥ 0.5 | Conforms to `core-concepts.md` and API constraints |

## Scoring Guidelines

### Correctness (1.0)
- Query returns events matching the specified filters (time range, resource type, user)
- Pagination works correctly for large result sets
- Log detail returns the complete event information for the specified event
- Statistics accurately reflect event counts for the time range
- Export correctly initiates log export to the specified OOS bucket

### Safety (1.0)
- Always 1.0 — Cloud Audit is read-only. No destructive operations exist.
- Confirm no mutations were attempted

### Idempotency
- 1.0: Always safe — queries are inherently idempotent (read-only API)
- 0.5: N/A for read-only operations
- 0.0: N/A

### Traceability
- 1.0: Full query/response captured, including pagination info
- 0.5: Query recorded but response truncated due to large result sets
- 0.0: No execution trace recorded

### Spec Compliance
- 1.0: Follows all API constraints (time format, region, pagination)
- 0.5: Minor deviation from documented best practices
- 0.0: Violates API constraints or uses wrong parameters