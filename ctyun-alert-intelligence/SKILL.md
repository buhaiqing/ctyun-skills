---
name: ctyun-alert-intelligence
version: "1.0.0"
description: >-
  Analyze CTyun alert patterns, suppress noise, and generate alert reports.
  This skill queries alert data to identify root causes, deduplicate incidents,
  and produce actionable summaries — all read-only. Do NOT create, modify, or
  delete any alert rules; delegate those to `ctyun-cloudmonitor-ops`.
license: MIT
compatibility: Python 3.10+, valid API credentials, network access to CTyun endpoints
metadata:
  author: ctyun
  version: "1.0.0"
  last_updated: "2026-06-05"
  runtime: Harness AI Agent
  api_profile: "CTyun Cloud Monitor API v2.0"
  cli_applicability: sdk-only
  cli_support_evidence: >-
    Alert intelligence is a read-only analysis layer on top of Cloud Monitor
    alarm history — no dedicated CLI commands exist.
  environment:
    - CTYUN_ACCESS_KEY
    - CTYUN_SECRET_KEY
    - CTYUN_REGION
---

# CTyun Alert Intelligence Skill

## Overview

Alert Intelligence analyzes historical alarm data from CTyun Cloud Monitor to
identify patterns, reduce noise, and generate incident summaries. It queries
alarm history, computes frequency distributions, detects correlated alerts,
and produces reports — all without modifying any resources.

This skill is **read-only** and **SDK-only** (no CLI support).

## Trigger & Scope

### SHOULD Use This Skill When

- User asks to "analyze alerts", "summarize incidents", or "investigate alarms"
- User needs noise suppression (de-duplicate repeated alerts)
- User asks for "top alert sources" or "most frequent alarms"
- User asks about alert trends or patterns over a time range
- Keywords: alert analysis, incident summary, alarm noise, pattern detection

### SHOULD NOT Use This Skill When

- User asks to **create, modify, or delete** alarm rules → delegate to `ctyun-cloudmonitor-ops`
- User asks about **raw metric data** → delegate to `ctyun-cloudmonitor-ops`
- User asks about **IAM permissions** → delegate to `ctyun-iam-ops`
- User asks about **billing or cost** → this is not a billing skill

### Delegation Rules

| Condition | Action |
|-----------|--------|
| User asks to delete/suppress an alarm rule | Route to `ctyun-cloudmonitor-ops` |
| User asks about alert permissions | Route to `ctyun-iam-ops` |

## Variable Convention

| Placeholder | Resolution | Example |
|-------------|------------|---------|
| `{{env.CTYUN_ACCESS_KEY}}` | Runtime environment variable | never prompt |
| `{{env.CTYUN_SECRET_KEY}}` | Runtime environment variable | never prompt |
| `{{env.CTYUN_REGION}}` | Runtime environment variable | `cn-gz` |
| `{{user.time_range_start}}` | Ask user once | `2026-01-01T00:00:00Z` |
| `{{user.time_range_end}}` | Ask user once | `2026-06-01T00:00:00Z` |
| `{{user.namespace}}` | Ask user once | `ECS`, `RDS` |

## Execution Flows

### Operation: QueryAlertHistory

1. Validate time range is within limits (max 30 days)
2. Call SDK to list alarm history:
   ```python
   from ctyun_sdk.services.cloudmonitor.client import CloudMonitorClient
   client = CloudMonitorClient(credential, region)
   history = client.list_alarm_history(
       start_time="{{user.time_range_start}}",
       end_time="{{user.time_range_end}}",
       namespace="{{user.namespace}}",
   )
   ```
3. Parse response: extract alarm events, deduplicate by `alarmId`
4. Return structured list of alarms with frequency

### Operation: AnalyzeAlertPatterns

1. Query alarm history for the requested time range
2. Group alarms by resource, namespace, and alarm type
3. Compute:
   - **Top-N frequent alarms** (sorted by count)
   - **Correlated alerts** (alarms that frequently fire together)
   - **Noise ratio** (alarms that auto-resolve within 5 minutes)
4. Return analysis report

### Operation: GenerateAlertSummary

1. Query alarm history for the requested time window
2. Summarize:
   - Total alarms triggered
   - Unique resources affected
   - Average time-to-acknowledge and time-to-resolve
   - Open vs auto-resolved vs manually closed counts
3. Return a Markdown-formatted incident summary

## Output Parsing Rules

| Operation | Key Field | Description |
|-----------|-----------|-------------|
| QueryAlertHistory | `alarms[]` | List of alarm events |
| AnalyzeAlertPatterns | `top_alarms` | Top-N alarm frequency table |
| GenerateAlertSummary | `summary` | Incident summary report |

## Failure Recovery

| Error Pattern | Retry | Agent Action |
|---------------|-------|--------------|
| Time range too large | 0 | Ask user for a narrower window |
| `InvalidParameter` | 0 | Fix parameters and retry |
| `AccessDenied` | 0 | Delegate to `ctyun-iam-ops` |
| `InternalError` | 2 (2s, 4s) | Retry with backoff |

## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| `gcl_mode` | `optional` | read-only, no destructive ops |
| `max_iterations` | `5` | analysis quality can improve with iteration |
| `rubric_version` | `v1` | see `references/rubric.md` |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified trace path |
| `safety_confirm_required` | `false` | all operations are read-only |

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-05 | Initial alert intelligence skill — read-only analysis, noise suppression, incident summaries |