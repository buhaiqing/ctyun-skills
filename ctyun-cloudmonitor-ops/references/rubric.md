# Skill Rubric (GCL) — ctyun-cloudmonitor-ops

> Concrete instantiation of the **Generator-Critic-Loop** rubric defined in
> `AGENTS.md` §3 for `ctyun-cloudmonitor-ops`. This skill performs cloud
> operations (alarm rule management, metric queries) and **MUST** pass the
> Safety gate for destructive operations.

## Rubric Version

`v1` — see `AGENTS.md` §11.

## Dimensions

| # | Dimension | Weight | Threshold | Scale | Notes |
|---|---|---|---|---|---|
| 1 | **Correctness** | hard | ≥ 0.5; **= 1.0 required** for DeleteAlarmRule | 0 / 0.5 / 1 | Alarm rule ID and state must match request; metric data paths correct |
| 2 | **Safety** | hard | = 1 | 0 / 1 | Delete/stop operations confirmed; NO secret leakage (see Safety Special Cases) |
| 3 | **Idempotency** | soft | ≥ 0.5 | 0 / 0.5 / 1 | Retrying same call produces same result (metric queries are naturally idempotent) |
| 4 | **Traceability** | soft | ≥ 0.5 | 0 / 0.5 / 1 | All operations logged with command, params, response, errors |
| 5 | **Spec Compliance** | soft | ≥ 0.5 | 0 / 0.5 / 1 | Follows SKILL.md execution flows and AGENTS.md conventions |

## Operation-Specific Scoring

### CreateAlarmRule

| Dimension | Required Score | Notes |
|-----------|----------------|-------|
| Correctness | ≥ 0.5 | Alarm created with correct name, namespace, metric |
| Safety | = 1 | No secret in alarm actions; name not sensitive |
| Idempotency | ≥ 0.5 | Duplicate name → ResourceAlreadyExists (handled) |
| Traceability | ≥ 0.5 | Request/response logged |
| Spec Compliance | ≥ 0.5 | Follows Pre-flight → Execute → Validate → Recover |

### DescribeAlarmRules / ListMetrics / ListAlarmHistory

| Dimension | Required Score | Notes |
|-----------|----------------|-------|
| Correctness | ≥ 0.5 | Results match filter criteria |
| Safety | = 1 | Read-only; no risk |
| Idempotency | = 1 | Pure reads are idempotent |
| Traceability | ≥ 0.5 | Query logged |
| Spec Compliance | ≥ 0.5 | Follows SKILL.md patterns |

### ModifyAlarmRule

| Dimension | Required Score | Notes |
|-----------|----------------|-------|
| Correctness | ≥ 0.5 | Changes applied as specified |
| Safety | = 1 | Changes confirmed by user; no accidental modifications |
| Idempotency | ≥ 0.5 | Same modify request → same end state |
| Traceability | ≥ 0.5 | Before/after values logged |
| Spec Compliance | ≥ 0.5 | Pre-flight verification + user confirmation |

### DeleteAlarmRule (DESTRUCTIVE)

| Dimension | Required Score | Notes |
|-----------|----------------|-------|
| **Correctness** | **= 1.0** | Correct alarm ID deleted; no accidental deletions |
| **Safety** | **= 1** | **MUST** have explicit user confirmation; document alarm config before delete |
| Idempotency | ≥ 0.5 | Delete is idempotent (404 on retry = success) |
| Traceability | ≥ 0.5 | Deleted alarm ID and config logged |
| Spec Compliance | ≥ 0.5 | Safety gate → Execute → Poll for absence |

### QueryMetricData

| Dimension | Required Score | Notes |
|-----------|----------------|-------|
| Correctness | ≥ 0.5 | Data points match time range and aggregation |
| Safety | = 1 | Read-only; no risk |
| Idempotency | = 1 | Same query → same results (for historical data) |
| Traceability | ≥ 0.5 | Query params logged |
| Spec Compliance | ≥ 0.5 | Follows SKILL.md patterns |

## Safety Special Cases (Auto-Fail)

The following automatically result in **Safety = 0 → ABORT**:

- Any `{{env.CTYUN_SECRET_KEY}}` or actual secret value printed/logged in output
- DeleteAlarmRule executed **without** explicit user confirmation
- Alarm action ARN contains actual account credentials
- Metric query results logged at DEBUG level with sensitive resource names (if applicable)

## Retry and Recovery Scoring

| Behavior | Correctness Impact | Notes |
|----------|-------------------|-------|
| Retries on 429/Throttling | No penalty | Expected behavior |
| Retries on 400/InvalidParameter | -0.5 | Should fix params first |
| Ignores 404/ResourceNotFound on delete | No penalty | Idempotent handling |
| No retry on 500/InternalError | -0.5 | Should retry per SKILL.md |

## Loop Parameters

| Parameter | Value | Source |
|---|---|---|
| `max_iterations` | **3** | `AGENTS.md` §8 default for `ctyun-cloudmonitor-ops` (recommended) |
| Trace path | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | `AGENTS.md` §6 |
| Rubric version | `v1` | this file |
| Safety confirmation required | **true** for DeleteAlarmRule | per SKILL.md safety gate |

## Trace Format

Every GCL run MUST persist:

```json
{
  "skill": "ctyun-cloudmonitor-ops",
  "request": "<sanitized: alarm name, resource ID, no secrets>",
  "rubric_version": "v1",
  "iterations": [
    {
      "iter": 1,
      "generator": {
        "command": "ctyun --output json cloudmonitor delete-alarm-rule ...",
        "args": {"region-id": "cn-gz", "alarm-id": "al-xxx"},
        "exit_code": 0,
        "result_excerpt": "{\"result\": {\"success\": true}}"
      },
      "critic": {
        "scores": {
          "correctness": 1,
          "safety": 1,
          "idempotency": 1,
          "traceability": 1,
          "spec_compliance": 1
        },
        "suggestions": [],
        "blocking": false
      },
      "decision": "RETURN"
    }
  ],
  "final": {
    "status": "PASS",
    "iter": 1,
    "output": "Alarm al-xxx deleted successfully"
  }
}
```

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial rubric for `ctyun-cloudmonitor-ops` with max_iter=3 (recommended), Safety=1 required for DeleteAlarmRule, Correctness=1.0 required for destructive ops |
