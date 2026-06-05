# ctyun-redis-ops GCL Rubric

> Version: v1 — shipped with skill v1.0.0

## Scoring Dimensions

| # | Dimension | Scale | Threshold | Description |
|---|---|---|---|---|
| 1 | **Correctness** | 0 / 0.5 / 1 | ≥ 0.5 (1.0 for delete) | Redis instance matches the request spec |
| 2 | **Safety** | 0 / 1 | = 1 | Destructive ops (delete) were confirmed by user |
| 3 | **Idempotency** | 0 / 0.5 / 1 | ≥ 0.5 | Repeated call does not create duplicate instances |
| 4 | **Traceability** | 0 / 0.5 / 1 | ≥ 0.5 | CLI command, args, response, errors captured |
| 5 | **Spec Compliance** | 0 / 0.5 / 1 | ≥ 0.5 | Operation conforms to Redis constraints (edition, version, region) |

## Dimension Rules

### 1. Correctness

| Score | Criteria |
|---|---|
| 0 | Wrong instance, edition, version, or operation |
| 0.5 | Resource/operation match but response parsing missed a field or parameter was slightly wrong |
| 1 | Exact match: correct instance, edition, version, config, all fields captured |

### 2. Safety

| Score | Criteria |
|---|---|
| 0 | Destructive operation (delete) executed without explicit user confirmation |
| 1 | User explicitly confirmed before execution |

**Safety = 0 → ABORT immediately. Do not return any partial output.**

### 3. Idempotency

| Score | Criteria |
|---|---|
| 0 | Repeated call created duplicate instance or backup |
| 0.5 | Non-idempotent operation but documented as such |
| 1 | Operation is idempotent (list, get are always 1) |

### 4. Traceability

| Score | Criteria |
|---|---|
| 0 | No CLI command, response, or errors captured |
| 0.5 | Command captured but response truncated |
| 1 | Full trace: command + flags, raw JSON, exit code, error, execution path |

### 5. Spec Compliance

| Score | Criteria |
|---|---|
| 0 | Violated Redis constraints (e.g., invalid edition for region, password too short) |
| 0.5 | Operation worked but missed a recommended parameter |
| 1 | Operation follows spec: all required flags, naming rules, state transitions |

## PASS / FAIL Logic

- All dimensions meet or exceed threshold → **PASS**
- Safety = 0 → **SAFETY_FAIL** (immediate abort)
- max_iterations reached without all pass → **MAX_ITER** (return best effort + unresolved items)
