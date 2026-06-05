# ctyun-elb-ops GCL Rubric

> Version: v1 — shipped with skill v1.0.0

## Scoring Dimensions

| # | Dimension | Scale | Threshold | Description |
|---|---|---|---|---|
| 1 | Correctness | 0/0.5/1 | ≥0.5 (1 for delete) | ELB resource matches request |
| 2 | Safety | 0/1 | =1 | Destructive ops confirmed |
| 3 | Idempotency | 0/0.5/1 | ≥0.5 | Repeated call safe |
| 4 | Traceability | 0/0.5/1 | ≥0.5 | Command/response/errors captured |
| 5 | Spec Compliance | 0/0.5/1 | ≥0.5 | Follows ELB constraints |

## Dimension Rules

### 1. Correctness

| Score | Criteria |
|---|---|
| 0 | Wrong LB/target group/target or operation |
| 0.5 | Match but missing field or slightly wrong param |
| 1 | Exact match: correct resource, operation, all fields |

### 2. Safety

| Score | Criteria |
|---|---|
| 0 | Delete without explicit user confirmation |
| 1 | User explicitly confirmed before execution |

**Safety = 0 → ABORT.**

### 3. Idempotency

| Score | Criteria |
|---|---|
| 0 | Repeated call created duplicate |
| 0.5 | Non-idempotent but documented |
| 1 | Operation is idempotent (list/get always 1) |

### 4. Traceability

| Score | Criteria |
|---|---|
| 0 | No command/response/errors captured |
| 0.5 | Command captured but response truncated |
| 1 | Full trace: command + flags, raw JSON, exit code, execution path |

### 5. Spec Compliance

| Score | Criteria |
|---|---|
| 0 | Violated ELB constraints (invalid protocol, port range) |
| 0.5 | Worked but missed recommended parameter |
| 1 | Follows spec: all required flags, naming rules |

## PASS / FAIL Logic

- All pass threshold → PASS
- Safety=0 → SAFETY_FAIL (abort)
- max_iter reached → MAX_ITER
