# GCL Retrospective & Dashboard Design Contract

> **Status:** Draft  
> **Version:** 1.0.0  
> **Last Updated:** 2026-06-05  
> **Scope:** CTyun Skills Farm GCL rollout phases 1–4

---

## 1. Purpose

This document serves two purposes:

1. **Retrospective Template:** Capture lessons learned from each GCL (Generator-Critic-Loop) rollout phase
2. **Dashboard Design Contract:** Define the schema and queries for the Phase 3 quality dashboard

---

## 2. Rollout Phases

| Phase | Target | Status | Completion Date |
|-------|--------|--------|-----------------|
| 1 | `ctyun-ecs-ops` pilot | Planned | — |
| 2 | `scripts/gcl_runner.py` orchestrator | Planned | — |
| 3 | Quality dashboard (`ctyun-audit-ops` integration) | Planned | — |
| 4 | Cloud Monitor alarm wiring | Planned | — |

---

## 3. Retrospective Template (Per Phase)

After each phase completes, append a section here using this template:

```markdown
### Phase X Retrospective — [Date]

#### What Worked
- 

#### What Didn't Work
- 

#### Metrics
| Metric | Target | Actual |
|--------|--------|--------|
| GCL pass rate | ≥80% | — |
| Avg iterations | ≤2.5 | — |
| Safety failures | 0 | — |

#### Adjustments for Next Phase
- 
```

---

## 4. Dashboard Design Contract (Phase 3)

### 4.1 Data Sources

The dashboard consumes `audit-results/gcl-trace-*.json` files produced by `scripts/gcl_runner.py`.

### 4.2 Trace Schema (v1)

```json
{
  "skill": "string",
  "request": "string (sanitized)",
  "rubric_version": "string",
  "iterations": [
    {
      "iter": "integer",
      "generator": {
        "command": "string",
        "args": "object",
        "exit_code": "integer",
        "result_excerpt": "string"
      },
      "critic": {
        "scores": {
          "correctness": "0|0.5|1",
          "safety": "0|0.5|1",
          "idempotency": "0|0.5|1",
          "traceability": "0|0.5|1",
          "spec_compliance": "0|0.5|1"
        },
        "suggestions": ["string"],
        "blocking": "boolean"
      },
      "decision": "RETRY|ABORT|RETURN"
    }
  ],
  "final": {
    "status": "PASS|FAIL|ABORT",
    "iter": "integer",
    "output": "string"
  }
}
```

### 4.3 Dashboard Queries

#### Query 1: Pass Rate by Skill (Last 7 Days)

```python
# Pseudocode for ctyun-audit-ops integration
def query_pass_rate_by_skill(traces, days=7):
    """
    Returns: [{skill, total_runs, pass_count, pass_rate}, ...]
    """
    filtered = [t for t in traces if t.date >= now() - days]
    grouped = group_by(filtered, key='skill')
    
    results = []
    for skill, items in grouped.items():
        total = len(items)
        passes = len([i for i in items if i.final.status == 'PASS'])
        results.append({
            'skill': skill,
            'total_runs': total,
            'pass_count': passes,
            'pass_rate': passes / total if total > 0 else 0
        })
    return results
```

#### Query 2: Average Iterations by Skill

```python
def query_avg_iterations(traces):
    """
    Returns: [{skill, avg_iterations}, ...]
    """
    grouped = group_by(traces, key='skill')
    
    results = []
    for skill, items in grouped.items():
        avg = mean([i.final.iter for i in items])
        results.append({'skill': skill, 'avg_iterations': avg})
    return results
```

#### Query 3: Safety Failure Heatmap

```python
def query_safety_failures(traces, days=30):
    """
    Returns: [{skill, date, count}, ...] for safety=0 events
    """
    filtered = [t for t in traces if t.date >= now() - days]
    
    failures = []
    for trace in filtered:
        for iter in trace.iterations:
            if iter.critic.scores.safety == 0:
                failures.append({
                    'skill': trace.skill,
                    'date': trace.date,
                    'iteration': iter.iter
                })
    return failures
```

### 4.4 Dashboard UI Mockup

```
┌─────────────────────────────────────────────────────────────┐
│ CTyun Skills Farm — GCL Quality Dashboard                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Pass Rate (7d)          Avg Iterations    Safety Events    │
│  ┌─────────┐             ┌─────────┐       ┌─────────┐     │
│  │  87%    │             │  2.1    │       │   0     │     │
│  └─────────┘             └─────────┘       └─────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Pass Rate by Skill (Bar Chart)                      │   │
│  │                                                     │   │
│  │ ctyun-ecs-ops    ████████████████████  92%         │   │
│  │ ctyun-rds-ops    ██████████████████    88%         │   │
│  │ ctyun-elb-ops    ████████████████      85%         │   │
│  │ ctyun-iam-ops    ██████████████        80%         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Iteration Distribution (Histogram)                  │   │
│  │                                                     │   │
│  │ 1 iter:  ████████████████████████  45%             │   │
│  │ 2 iter:  ██████████████████        35%             │   │
│  │ 3 iter:  ██████████                20%             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Cloud Monitor Alarm Wiring (Phase 4)

### 5.1 Alarm Rules

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Pass rate < 70% | 15 min | P1 | Page on-call |
| Safety failures > 0 | immediate | P0 | Page on-call + auto-disable skill |
| Avg iterations > 2.8 | 1 hour | P2 | Slack alert |

### 5.2 Metric Namespace

```
Namespace: CTyun/AgentSkills/GCL
Metrics:
  - PassRate (Percent)
  - AvgIterations (Count)
  - SafetyFailures (Count)
  - TotalRuns (Count)
Dimensions:
  - SkillName
  - RubricVersion
```

---

## 6. Open Questions

1. Should we persist traces to a database (SQLite/PostgreSQL) or keep as JSON files?
2. What's the retention policy for trace files? (suggest: 90 days)
3. Should the dashboard be a standalone Streamlit app or integrated into existing tooling?

---

## 7. Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial dashboard design contract for CTyun Skills Farm |
