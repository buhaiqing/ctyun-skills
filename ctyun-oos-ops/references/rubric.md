# ctyun-oos-ops GCL Rubric

> Version: v1 — shipped with skill v1.0.0

## Scoring Dimensions

| # | Dimension | Scale | Threshold | Description |
|---|---|---|---|---|
| 1 | Correctness | 0/0.5/1 | ≥0.5 (1 for delete) | Bucket/object matches request |
| 2 | Safety | 0/1 | =1 | Delete operations confirmed by user |
| 3 | Idempotency | 0/0.5/1 | ≥0.5 | No duplicate side-effects |
| 4 | Traceability | 0/0.5/1 | ≥0.5 | SDK call/response/errors captured |
| 5 | Spec Compliance | 0/0.5/1 | ≥0.5 | Follows naming rules, ACL constraints, region |

## Dimension Rules

### 1. Correctness

| Score | Criteria |
|---|---|
| 0 | Wrong bucket, object, or operation |
| 0.5 | Match but missing field or param |
| 1 | Exact match: correct bucket, object, ACL, region |

### 2. Safety

| Score | Criteria |
|---|---|
| 0 | Delete bucket/object without explicit user confirmation |
| 1 | User explicitly confirmed |

**Safety = 0 → ABORT.**

### 3. Idempotency

| Score | Criteria |
|---|---|
| 0 | Created duplicate resource due to missing checks |
| 0.5 | Non-idempotent but documented safe |
| 1 | Natural idempotency respected (overwrite, no-op on re-delete) |

### 4. Traceability

| Score | Criteria |
|---|---|
| 0 | No call/response/errors captured |
| 0.5 | Call captured but response truncated |
| 1 | Full trace: SDK method + params, raw response, exit code, execution path |

### 5. Spec Compliance

| Score | Criteria |
|---|---|
| 0 | Invalid bucket name, ACL, or region |
| 0.5 | Missed recommended parameter (e.g., no ACL set) |
| 1 | Follows spec: valid naming, correct ACL, correct signature version |

## PASS / FAIL Logic

- All pass threshold → PASS
- Safety=0 → SAFETY_FAIL (abort)
- max_iter reached → MAX_ITER
