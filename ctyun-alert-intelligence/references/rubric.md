# ctyun-alert-intelligence GCL Rubric

> Version: v1 — shipped with skill v1.0.0

## Scoring Dimensions

| # | Dimension | Scale | Threshold | Description |
|---|---|---|---|---|
| 1 | **Correctness** | 0 / 0.5 / 1 | ≥ 0.5 | Alert data is correctly queried and parsed |
| 2 | **Safety** | 0 / 1 | = 1 | Read-only; no modification of alarm rules |
| 3 | **Idempotency** | 0 / 0.5 / 1 | ≥ 0.5 | Repeated queries produce consistent results |
| 4 | **Traceability** | 0 / 0.5 / 1 | ≥ 0.5 | Query params, time range, and response captured |
| 5 | **Spec Compliance** | 0 / 0.5 / 1 | ≥ 0.5 | Analysis follows documented patterns |

## PASS / FAIL Logic

- All dimensions meet or exceed threshold → **PASS**
- Safety = 0 → **SAFETY_FAIL** (immediate abort)
- max_iterations reached without all pass → **MAX_ITER**