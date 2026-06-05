# CLI-First Decision Matrix

> **Authoritative executable contract** for "when to consider SDK/API" in any
> `ctyun-*-ops` skill generated from this repo. The policy header lives in
> [`AGENTS.md` §CLI-First Policy](../../AGENTS.md#cli-first-policy-repository-wide);
> this file is the **decision logic** the policy refers to. The
> `ctyun-skill-generator/SKILL.md` §CLI-First Decision Matrix is a short entry
> point that links here.
>
> **Do not modify the rules in this file without also updating the AGENTS.md
> policy header and the `ctyun-skill-generator` SKILL.md entry point.**
> These three locations MUST stay aligned.

---

## 1. Per-Operation Decision Tree

```text
   Does `ctyun <product> <op>` exist in
   `ctyun --output json <product> --help`?
        │
        ├── yes ──► try CLI (3 retries, exp backoff) ──► success? continue
        │                                                  │
        │                                                  └─ 3 fails ──► fall back to SDK (per-op)
        │
        └── no / unknown ──► mark `cli_applicability: sdk-only` for this op; use SDK/API
```

> **The tree runs per operation, not per skill.** A 12-op skill MUST NOT
> degrade to "all-SDK" just because one operation is unsupported by `ctyun`.

## 2. What counts as "CLI 不满足" (CLI unsatisfied)

A `ctyun` command is considered **unsatisfied** on a real `--output json`
run when any of the following is true. The "Class" column drives the
action in §3.

| # | Condition | Detection (real run) | Class | Action |
|---|---|---|---|---|
| 1 | `ctyun` not installed | `command -v ctyun` returns non-zero | **Environment** | `uv pip install ctyun-cli ctyun-sdk`; retry up to 3 times |
| 2 | `ctyun --version` crashes | non-zero exit OR stderr contains `Traceback` | **Environment** | retry install up to 3 times; if still broken, **skill-wide SDK fallback** |
| 3 | Subcommand not found | stderr matches `Error: No such command '.*'` (exit code 44) | **Capability** | **mark `cli_applicability: sdk-only` for this op**; **do not retry CLI** |
| 4 | Subcommand exists, required flag missing | stderr matches `Error: Missing option '.*'` | **Capability** | consult OpenAPI for the flag; **fall back to SDK for this op** (no retry) |
| 5 | Subcommand returns a 5xx-style error | `{"errorCode": "5xx", ...}` in JSON body | **Runtime** | retry once; if persists, **fall back to SDK for this op** |
| 6 | Subcommand returns a 4xx-style error | `{"errorCode": "4xx", ...}` in JSON body | **Business** | **surface to user**; do **not** fall back (the call is wrong, the path is irrelevant) |
| 7 | Subcommand hangs > timeout | no stdout within `cli_timeout_seconds` (default 30) | **Runtime** | kill; **fall back to SDK for this op**; do not retry CLI in this session |
| 8 | Subcommand returns non-JSON under `--output json` | stdout is not parseable as JSON | **Runtime** | retry once; if persists, **fall back to SDK for this op** |
| 9 | Credentials not configured | `~/.ctyun/config` missing OR `~/.ctyun/current` empty | **Environment** | bootstrap credentials (see ctyun-skill-generator/SKILL.md §Phase 1) — **does not** trigger SDK fallback |

> **Class summary:**
> - **Environment (1, 2, 9)** — fix and retry the CLI; do not jump to SDK.
> - **Capability (3, 4)** — CLI cannot do this; switch to SDK for that op.
> - **Runtime (5, 7, 8)** — CLI failed mid-flight; try SDK for that op.
> - **Business (6)** — wrong is wrong; surface the error, do not mask it.

## 3. Fallback Scope (per-Operation, not per-Skill)

| Trigger class (from §2) | Scope of fallback |
|---|---|
| Environment (1, 2) | **Skill-wide** for the rest of the session — every op falls back to SDK |
| Capability (3, 4) | **Operation-wide** — that single op falls back; other ops still try CLI |
| Runtime (5, 7, 8) | **Operation-wide** — that single op falls back; other ops re-attempt CLI |
| Business (6) | **No fallback** — surface the error to the user (P0 safety gate) |
| Credentials (9) | Fix credentials first, then re-run; do not fall back yet |

> **Worked example:** `ctyun-iam-ops` has 12 operations. 11 work via CLI; op
> #7 (`create-access-key`) returns a `5xx` and triggers §2 item 5. The
> generator MUST route op #7 to the SDK path while keeping the other 11 on
> CLI. The generated `SKILL.md` MUST document both paths for op #7, with a
> one-line note in the trace: `executed via SDK fallback after 1 CLI 5xx`.

## 4. Session-Level Policy

| Situation | Policy |
|---|---|
| Skill-wide CLI failure (§2 items 1, 2) | Stay on SDK for the rest of the session. Re-attempt CLI **only** at the start of a new run. |
| Operation-wide CLI failure (§2 items 3, 4, 5, 7, 8) | That op stays on SDK for the rest of the session. Other ops re-attempt CLI normally. |
| User explicitly requests CLI only | Skip fallback; HALT on failure with the error surfaced. |
| User explicitly requests SDK only | Skip CLI entirely; set `cli_applicability: sdk-only` for the skill. |
| Env var `CTYUN_FORCE_SDK=1` (sandbox / CI) | Disables the CLI path entirely. |
| Env var `CTYUN_FORCE_CLI=1` (debug) | Disables fallback; HALT on §2 items 3-8 instead of switching to SDK. |

## 5. Anti-Patterns (CLI-first violations)

- ❌ **Using SDK by default because "it's easier to test"** — the generated
  skill MUST be exercisable via `ctyun` first; SDK-only is a **fallback
  label**, not a default.
- ❌ **Tagging `cli_applicability: sdk-only` without evidence** — show the
  `ctyun <product> --help` excerpt (or the absence of the operation) in
  `references/cli-usage.md` for any SDK-only op. No evidence, no tag.
- ❌ **Mixing CLI and SDK output for the same operation without trace
  annotation** — if a destructive op succeeds via SDK, the trace MUST
  record `executed via SDK fallback after N CLI failures (class=...)` so
  the GCL Critic can re-verify.
- ❌ **Caching the "CLI is broken" decision across runs** — every new
  session re-attempts CLI per §4; the failure state is **session-scoped**,
  not persistent.
- ❌ **Hiding the fallback path in a footnote** — both paths MUST be
  documented **inline** in the generated skill (under each operation's
  "Execution" subsection), not only in `references/troubleshooting.md`.

---

## Cross-Reference

This file is the **executable contract** referenced from:

- [`AGENTS.md` §CLI-First Policy](../../AGENTS.md#cli-first-policy-repository-wide) — repo-wide policy header
- [`ctyun-skill-generator/SKILL.md` §CLI-First Decision Matrix](../SKILL.md#cli-first-decision-matrix) — entry point in the meta-skill
- Each generated `ctyun-*-ops` skill's `## Quality Gate (GCL)` section, via the
  `fallback_decision_table` parameter
