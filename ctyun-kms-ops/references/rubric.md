# ctyun-kms-ops GCL Rubric

> Version: v1 — shipped with skill v1.0.0

## Scoring Dimensions

| # | Dimension | Scale | Threshold | Description |
|---|---|---|---|---|
| 1 | Correctness | 0/0.5/1 | ≥0.5 (1 for delete) | Key resource matches request |
| 2 | Safety | 0/1 | =1 | Schedule deletion confirmed by user |
| 3 | Idempotency | 0/0.5/1 | ≥0.5 | Retry-safe operations |
| 4 | Traceability | 0/0.5/1 | ≥0.5 | Command/response/errors captured |
| 5 | Spec Compliance | 0/0.5/1 | ≥0.5 | Follows KMS constraints (key spec, region) |

## Dimension Rules

### 1. Correctness

| Score | Criteria |
|---|---|
| 0 | Wrong key, operation, or param |
| 0.5 | Match but missing parameter |
| 1 | Exact match: correct key ID, spec, operation |

### 2. Safety

| Score | Criteria |
|---|---|
| 0 | Schedule key deletion without explicit confirmation |
| 1 | User explicitly confirmed with warning acknowledged |

**Safety = 0 → ABORT.**

### 3. Idempotency

| Score | Criteria |
|---|---|
| 0 | Duplicate create (no idempotency) |
| 0.5 | Idempotent but not documented |
| 1 | Create uses idempotency token |

### 4. Traceability

| Score | Criteria |
|---|---|
| 0 | No command/response captured |
| 0.5 | Partial trace |
| 1 | Full trace: command, raw JSON, exit code, path |

### 5. Spec Compliance

| Score | Criteria |
|---|---|
| 0 | Invalid key spec or pending window (<7 or >30) |
| 0.5 | Missed recommended parameter |
| 1 | Follows spec: valid key spec, pending window 7-30, naming rules |

## PASS / FAIL Logic

- All pass threshold → PASS
- Safety=0 → SAFETY_FAIL (abort)
- max_iter reached → MAX_ITER
