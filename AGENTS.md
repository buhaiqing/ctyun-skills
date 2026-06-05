# CTyun Skills Farm

## Quick Identity

**CTyun Skills Farm** is a collection of AI Agent Skill definitions (structured Markdown documents following the Agent Skill OpenSpec) that enable AI agents to perform CTyun (天翼云) operations. Each skill maps to one CTyun product.

## Repo Layout

> **Status:** Only the **meta-skill** is shipped. All `ctyun-*-ops` product skills
> below are **planned** and will be produced by `ctyun-skill-generator`. The
> layout here reflects what is **currently on disk**.

```
ctyun-skills/
├── README.md                                       # Project readme (currently a stub)
├── AGENTS.md                                       # ← this file (repo constitution)
├── LICENSE                                         # MIT
├── pyproject.toml                                  # Project metadata (uv-managed)
├── .env.example                                    # Credential template (gitignored real .env)
├── docs/
│   └── GCL_RETROSPECTIVE.md                        # GCL rollout retrospective & dashboard design
└── ctyun-skill-generator/                          # Shipped: meta-skill — generates new ctyun-*-ops
    ├── SKILL.md
    └── references/
        ├── ctyun-skill-template.md
        ├── governance-and-adversarial-review.md
        ├── prompt-templates.md
        └── rubric.md
```

### Planned Layout (per generated `ctyun-*-ops`)

```
ctyun-[product]-ops/                  # ← produced by ctyun-skill-generator
├── SKILL.md
├── assets/example-config.yaml
└── references/
    ├── cli-usage.md
    ├── core-concepts.md
    ├── integration.md
    ├── monitoring.md
    └── troubleshooting.md
```

> No `ctyun-*-ops` directory exists yet. The schema above is the **target layout**
> the meta-skill will scaffold; it is documented here for the generator's contract,
> not as a current inventory.

## Development Environment

**Python 3.10** | **`uv`** (package manager) | **`ctyun`** (CTyun CLI)

> **IMPORTANT: Python version must be 3.10+**
> We recommend Python 3.10 for maximum compatibility with CTyun SDK and CLI.
>
> Always use `uv venv --python 3.10` to create the virtual environment. If Python 3.10 is not installed on your system, install it first:
> - macOS: `brew install python@3.10`
> - Linux: `apt install python3.10 python3.10-dev` or `uv python install 3.10`
> - Windows: Download from https://www.python.org/downloads/release/python-3100/

### Setup

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install ctyun-cli ctyun-sdk
```

`pyproject.toml` pins `ctyun-cli>=1.0.0`. The default pip index is `https://pypi.org/simple/` (configured under `[tool.uv]`).

### Credentials

Three methods (priority order: shell env > `.env` > `~/.ctyun/config`):

```bash
# Method 1: .env file (recommended for local dev)
cp .env.example .env
# Edit with real credentials; .env is in .gitignore

# Method 2: CLI config for ctyun
ctyun config init              # interactive
# Or manual:
export HOME=/tmp/ctyun-home    # sandbox-safe writable home
mkdir -p /tmp/ctyun-home/.ctyun
cat > /tmp/ctyun-home/.ctyun/config << 'CONFIGEOF'
[default]
access_key = {{env.CTYUN_ACCESS_KEY}}
secret_key = {{env.CTYUN_SECRET_KEY}}
region_id = cn-gz
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
CONFIGEOF
printf "%s" "default" > /tmp/ctyun-home/.ctyun/current
```

**CRITICAL: ctyun CLI reads credentials ONLY from `~/.ctyun/config` INI file, NOT from environment variables.** The SDK reads from `CTYUN_ACCESS_KEY`/`CTYUN_SECRET_KEY` env vars. Both must be configured.

**NEVER** print or log `CTYUN_SECRET_KEY`. Only check existence with `test -n`.

## ctyun CLI Quirks (Hard-Earned)

These are the most common agent mistakes — get them right every time:

| Rule | Wrong | Correct |
|------|-------|---------|
| `--output json` placement | `ctyun ecs list --output json` | `ctyun --output json ecs list` |
| `--no-interactive` flag | `ctyun --no-interactive ecs delete` | **Omit entirely** — not supported |
| Credentials | `export CTYUN_ACCESS_KEY=...` (CLI ignores) | Must write `~/.ctyun/config` INI file |
| `~/.ctyun/current` newline | `echo "default" > file` (adds newline) | `printf "%s" "default" > file` (no trailing newline) |

## Execution Strategy

**ctyun-first with SDK fallback** — the repository-wide policy:

1. Try `ctyun --output json <command>` first
2. On failure, retry up to 3 times with exponential backoff (0s → 2s → 4s)
3. After 3 consecutive failures, fall back to Python SDK (`ctyun_sdk`)
4. Document which path was used

## CLI-First Policy (Repository-Wide)

> This section is the **policy header** for the whole repository. The
> **executable contract** (decision tree, 9-item "CLI 不满足" classifier,
> per-operation fallback, trace annotation rules) lives in
> [`ctyun-skill-generator/SKILL.md` §CLI-First Decision Matrix](ctyun-skill-generator/SKILL.md#cli-first-decision-matrix).
> Every `ctyun-*-ops` skill generated from this repo MUST implement that
> matrix; this section is the single source of truth that it does.

### Layered Policy (6 rules every skill MUST follow)

| Layer | Rule | Why |
|---|---|---|
| **Routing** | If a `ctyun <product> <op>` subcommand exists, **use it**. SDK/API is a contingency, not a parallel first choice. | Skills claim "ctyun-first" — auditors must be able to run on a clean machine with the CLI alone. |
| **Detection** | "CLI 不满足" is classified into 4 classes — **Environment** (install / crash / creds), **Capability** (subcommand / flag missing), **Runtime** (5xx / timeout / non-JSON), **Business** (4xx). Only classes 2-4 trigger fallback. | Distinguishes "fix and retry" (env) from "switch path" (capability/runtime) from "wrong call" (business). |
| **Fallback scope** | **Per-operation, not per-skill.** A 12-op skill that has 1 failing op falls back **only** for that op; the other 11 still use CLI. | Avoids "one failure → all-SDK" pathology. |
| **Session scope** | "CLI is broken" state is **session-scoped**; every new run re-attempts CLI. No persistent degradation. | Caches the "CLI broken" decision across runs, otherwise a single bad day locks the skill to SDK forever. |
| **Force overrides** | `CTYUN_FORCE_SDK=1` disables the CLI path (sandbox / CI). `CTYUN_FORCE_CLI=1` disables fallback (debug). | Operator intent is explicit and machine-checkable. |
| **Tagging discipline** | `cli_applicability: sdk-only` MUST be backed by a `ctyun <product> --help` excerpt (or its absence) in `references/cli-usage.md`. **No evidence, no tag.** | Prevents "SDK is easier" laziness. |

### "CLI 不满足" — the 4-class summary

| Class | Examples | Triggers fallback? | Retries CLI? |
|---|---|---|---|
| **Environment** | `ctyun` not installed / crashes on `--version` / `~/.ctyun/config` missing | **No** — fix and retry CLI | Yes (up to 3 times) |
| **Capability** | Subcommand not found / required flag missing | **Yes** — switch to SDK for that op | **No** |
| **Runtime** | 5xx response / >30s timeout / non-JSON output under `--output json` | **Yes** — switch to SDK for that op (after 1 retry) | Once, then stop |
| **Business** | 4xx response | **Never** — surface the error to the user (P0 safety gate) | N/A |

> Full 9-item table with detection patterns is in
> [`ctyun-skill-generator/SKILL.md` §2](ctyun-skill-generator/SKILL.md#2-what-counts-as-cli-不满足-cli-unsatisfied).

### Per-Operation Fallback — the 3-line version

| Trigger class (from the table above) | Fallback scope |
|---|---|
| Environment | **Skill-wide** (every op falls back for the rest of the session) |
| Capability / Runtime | **Operation-wide** (only that op falls back; others re-attempt CLI) |
| Business | **No fallback** |
| Credentials missing | Fix creds and re-run; **do not** fall back yet |

> Full version with worked example is in
> [`ctyun-skill-generator/SKILL.md` §3](ctyun-skill-generator/SKILL.md#3-fallback-scope-per-operation-not-per-skill).

### Anti-Patterns (CLI-first violations, repo-wide)

- ❌ **Using SDK by default because "it's easier to test"** — the generated
  skill MUST be exercisable via `ctyun` first; SDK-only is a fallback
  label, not a default.
- ❌ **Tagging `cli_applicability: sdk-only` without `--help` evidence** —
  show the excerpt (or absence) in `references/cli-usage.md`.
- ❌ **Mixing CLI and SDK output for the same op without trace annotation** —
  every fallback run MUST record `executed via SDK fallback after N CLI
  failures (class=...)` so the GCL Critic can re-verify.
- ❌ **Caching the "CLI is broken" decision across runs** — every new
  session re-attempts CLI.
- ❌ **Hiding the fallback path in a footnote** — both paths MUST be
  documented **inline** in the generated skill, not only in
  `troubleshooting.md`.
- ❌ **Marking a Shipped skill with `cli_applicability: sdk-only` for the
  whole skill** when only one operation is unsupported — that op alone
  should be `sdk-only`; the skill stays `dual-path` overall.

## Skill SKILL.md Anatomy

Every `SKILL.md` uses:
- **YAML frontmatter** with `name`, `version`, `metadata` (including `cli_applicability`, `cli_version_locked`, `sdk_version_locked`)
- **Trigger & Scope** — `SHOULD Use` / `SHOULD NOT Use` with delegation rules
- **Variable Convention** — `{{env.*}}` (runtime, never prompt user), `{{user.*}}` (ask once, cache), `{{output.*}}` (parse from JSON response)
- **Execution Flows** — Pre-flight → Execute (ctyun primary / SDK fallback) → Validate → Recover
- **Output Parsing Rules** — JSON paths (`$.result.*`) and state transition tables
- **Failure Recovery** — Error pattern tables with retry counts, backoff, and agent actions
- **Safety Gates** — Delete/recovery operations REQUIRE explicit user confirmation
- **Quality Gate (GCL)** — per-skill GCL parameters (see [§Generator-Critic-Loop §8.5](#85-quality-gate-gcl-section-mandatory-per-skill))

## Token Efficiency & Skill Deduplication

> Skills are loaded into an LLM context window. **Wasted tokens are wasted
> attention.** Two failure modes are caught at PR review: (1) one skill is
> too verbose; (2) two skills duplicate the same content.

### Per-Skill Budgets

| Artifact | Soft cap | Hard cap | What to do at hard cap |
|---|---|---|---|
| `SKILL.md` (body, excluding frontmatter) | 400 lines | **600 lines** | Move long sections to `references/` and link with a one-line summary |
| `references/*.md` (each) | 300 lines | 800 lines | Split into multiple files (e.g. `cli-usage-create.md` / `cli-usage-delete.md`) |
| Total per skill (SKILL.md + all references) | — | 3000 lines | Decompose the skill or factor common sections into `_shared/` |
| Inline code blocks in SKILL.md | 50 lines each | 200 lines | Truncate with `…` and link to the full snippet in `assets/` |

> The caps are checked by `scripts/check_skill_size.py` (planned, see
> [§Validation](##validation)). Soft cap is a PR comment; hard cap is a
> **blocker**.

### Style Rules

- **Reference, don't copy.** If `references/cli-usage.md` already shows the
  full command, do not re-show it in `SKILL.md`; link it with one line of
  context.
- **Tables over prose.** State machines, error codes, and config keys MUST
  be tables, not paragraphs — tables compress better in the LLM context.
- **No marketing prose.** Drop adjectives like "powerful", "flexible",
  "seamless". Keep only the load-bearing facts.
- **Examples are surgical.** Each example must demonstrate a non-obvious
  behavior. Reuse one example across multiple operations instead of
  inventing a new one for each.
- **Frontmatter is the index.** `description:` and `SHOULD Use` bullets are
  the **only** content the Agent reads for routing. Keep them dense and
  keyword-rich.

### Cross-Skill Deduplication

Common content that appears in more than one skill MUST be factored:

| Topic | Canonical home | Other skills SHOULD |
|---|---|---|
| Credential loading (`~/.ctyun/config`, `.env`) | `ctyun-skill-generator/SKILL.md` §Environment Setup | link to it, not re-derive |
| `ctyun` CLI quirks (top-level `--output json`, no `--no-interactive`) | this `AGENTS.md` §ctyun CLI Quirks | link, not re-derive |
| OpenAPI / SDK lookup pattern | `ctyun-skill-generator/SKILL.md` §Generation Process | link |
| Safety gate template | this `AGENTS.md` §Security Rules | link |
| Quality Gate (GCL) section schema | this `AGENTS.md` §Generator-Critic-Loop §8.5 | embed the schema, see below |

> If two skills grow the same 20-line block, the second one **MUST** be
> refactored to a single link. Duplicate content is a refactor trigger, not
> a documentation choice.

### Anti-Patterns

- ❌ **Pasting a 100-line SDK call into `SKILL.md`** when the full code
  belongs in `references/` or `assets/`.
- ❌ **Re-deriving CLI quirks in each `ctyun-*-ops`** instead of linking
  to `AGENTS.md` §ctyun CLI Quirks.
- ❌ **One mega-`references/cli-usage.md` per skill** that copy-pastes the
  full `ctyun <product> --help` text — use `ctyun <product> --help` as the
  source of truth and only document the **non-obvious** flags.
- ❌ **Marketing-style intro paragraph** in `SKILL.md` — drop it; the
  frontmatter already routes the skill.

## Cross-Skill Delegation

> **Status:** **Planned.** Only `ctyun-skill-generator` exists today. The
> delegation table below is a **contract** that the meta-skill will materialize
> as it produces the corresponding `ctyun-*-ops` skills — not a current
> capability.

| If they ask about | Delegate to | Status |
|---|---|---|
| Generate a new product skill | `ctyun-skill-generator` | **Shipped** |
| ECS create/stop/delete | `ctyun-ecs-ops` | Planned |
| RDS instance CRUD | `ctyun-rds-ops` | Planned |
| Monitoring metrics, alarm rules | `ctyun-cloudmonitor-ops` | Planned |
| Alert analysis, suppression, reporting | `ctyun-alert-intelligence` | Planned (read-only) |
| IAM users, policies, keys | `ctyun-iam-ops` | Planned |
| Key management, encryption | `ctyun-kms-ops` | Planned |
| Load balancer config | `ctyun-elb-ops` | Planned |

- `ctyun-alert-intelligence` (planned) is **read-only** — it analyzes alerts but delegates alarm rule changes back to `ctyun-cloudmonitor-ops`.
- Each generated skill's `SHOULD NOT Use` section lists exactly where to route.
- Until an ops skill is **Shipped**, the meta-skill is the only entry point for
  any CTyun task. Direct product operations are **out of scope** for the
  current repository.

## Validation

```bash
npm install -g markdownlint-cli
markdownlint ctyun-[product]-ops/SKILL.md
```

## Doc Link & Cross-Reference Integrity

> A broken link in a charter file is worse than a missing paragraph — the
> Agent will follow it and silently fail. All relative links, anchor links,
> and `{{var.*}}` placeholders are **CI-checked** (planned tool:
> `scripts/check_doc_integrity.py`).

### What is checked

| Check | Tool | Pass criteria |
|---|---|---|
| Relative file links | `markdown-link-check` or `lychee --offline` | Target file exists in the working tree |
| Anchor links (`#section-name`) | `markdown-link-check` + slug rule | Heading with that slug exists in target file |
| `{{env.*}}` / `{{user.*}}` / `{{output.*}}` placeholders | grep + `agentskills-validator` | Matches `{{(env\|user\|output)\.[a-zA-Z0-9_\.]+}}`; bare `{...}` fails |
| Cross-skill links (`../ctyun-other-ops/...`) | file existence check | Target directory exists (i.e. the linked skill is **Shipped**, not Planned) |
| `references/rubric.md` and `references/prompt-templates.md` | `scripts/check_gcl_artifacts.py` | Both files present for any `ctyun-*-ops` (GCL `required` or `recommended`) |
| `## Quality Gate (GCL)` section in SKILL.md | grep on heading | Present on any non-`sdk-only` skill |
| Token-efficiency budgets | `scripts/check_skill_size.py` | Hard caps from [§Token Efficiency & Skill Deduplication](#token-efficiency--skill-deduplication) not exceeded |

### Local command

```bash
# Install once
npm install -g markdown-link-check lychee

# Check a single file
markdown-link-check ctyun-ecs-ops/SKILL.md

# Check the entire repo (offline, fast)
lychee --offline --include-fragments '**/*.md'
```

### Pre-merge Gate (Doc Integrity)

A skill PR is **not mergeable** while any of the following is true:
- A relative link resolves to a 404 in the working tree
- A `#anchor` does not match any heading slug in the target file
- A cross-skill link points to a **Planned** (not yet Shipped) skill
- A `{{...}}` placeholder does not match the `{{env.*}}` / `{{user.*}}` / `{{output.*}}` contract
- `references/rubric.md` or `references/prompt-templates.md` is missing on a skill that is GCL `required` or `recommended`
- A `ctyun-*-ops` SKILL.md is missing the `## Quality Gate (GCL)` section
- Any skill exceeds its hard-cap line count

### Anti-Patterns

- ❌ **Linking to a Planned skill from a Shipped skill** — the link will
  404 once the Planned skill ships under a slightly different name.
- ❌ **Cross-skill link with absolute URL** (`https://github.com/...`)
  when a relative path would work — drift on repo move.
- ❌ **Bare `{var}` placeholder** that the Agent runtime won't resolve.
- ❌ **Anchor link `#safety-gate` with no corresponding `## Safety Gate`
  heading** — silently 404 in many Markdown renderers.

## Versioning

SemVer in `SKILL.md` frontmatter. Update `version` field + Changelog table when modifying. The `version` field reflects the skill document version, not the SDK version (tracked separately in `metadata.sdk_version_locked`).

## Security Rules

- `{{env.*}}` placeholders are resolved from agent runtime — **never prompt the user**
- `.env` is gitignored; never commit real credentials
- Delete/stop/restore operations require explicit user confirmation ("safety gate")
- `ctyun-alert-intelligence` is read-only — no resource mutations
- Credential status checks: `test -n "$VAR"` only, print `<masked>` if logging status

## Self-Review Policy

Every skill update MUST follow a **2-round self-review process** to ensure quality and correctness:

### Round 1: Initial Review
After creating or modifying a skill:
1. Review the skill against the template and existing reference skills
2. Verify all required sections are present (frontmatter, Trigger & Scope, Variable Convention, Execution Flows, etc.)
3. Check for consistency with [§CLI-First Policy](#cli-first-policy-repository-wide) — 6 Layered Rules; the executable contract is in [`ctyun-skill-generator/references/cli-decision-matrix.md`](ctyun-skill-generator/references/cli-decision-matrix.md)
4. Validate safety gates are in place for destructive operations

### Round 2: Deep Review
After Round 1 fixes are applied:
1. Verify API accuracy against official OpenAPI specifications
2. Validate CLI command syntax and JSON output paths
3. Check cross-skill delegation rules are correctly defined
4. Confirm versioning follows SemVer and changelog is updated

### Auto-Fix Requirement
All issues discovered during both review rounds MUST be proactively fixed before the skill is considered complete. This includes:
- Correcting API parameters and response paths
- Fixing CLI command syntax
- Adding missing safety gates
- Updating documentation inconsistencies (see [Skill Lifecycle & Doc Sync Convention](#skill-lifecycle--doc-sync-convention) for the Sync Matrix)
- Ensuring alignment with repository-wide conventions

---

## Skill Lifecycle & Doc Sync Convention

> Every product-scoped `ctyun-*-ops` skill moves through three lifecycle states.
> `AGENTS.md` is the **single source of truth** for the repo-wide inventory, so
> it MUST be updated **atomically with the new skill's first commit**. A stale
> "Planned" tag after the directory exists is a documentation bug, not a nit.

### Lifecycle States

| State | Meaning | Doc marker |
|---|---|---|
| **Planned** | Designed but not on disk | rows tagged `Planned`; no directory in §Repo Layout |
| **Shipped** | Lives in this repo with a valid `SKILL.md` and `references/` | rows tagged **Shipped**; directory listed in §Repo Layout |
| **Retired** | Removed from this repo | row kept under a `Retired` block (struck through) for history |

### Sync Matrix — what to update when a skill changes state

When a skill transitions state, the **same commit** that lands the new
`ctyun-[product]-ops/` directory (or deletes it) MUST update **all** of the
following locations in `AGENTS.md`:

| # | Section | Action on **Shipped** | Action on **Retired** |
|---|---|---|---|
| 1 | §Repo Layout (current-on-disk block) | Add the new `ctyun-[product]-ops/` tree | Remove the directory line |
| 2 | §Cross-Skill Delegation | Move row from `Planned` to `Shipped` column | Move to a `Retired` block at the bottom (or delete) |
| 3 | §GCL §8 Per-Skill Defaults — Shipped sub-table | Add row with live `max_iter` + link to `SKILL.md#quality-gate-gcl` | Remove from Shipped sub-table |
| 4 | §GCL §8 Per-Skill Defaults — Planned sub-table | Delete the matching Planned row | Re-add under Planned with `Retired` superscript |
| 5 | §GCL §10 Rollout Roadmap — Phase 1 | If this is the first skill exercised end-to-end with GCL, append a one-line entry naming it | n/a |
| 6 | §11 Changelog | Append: `\| <bump> \| <date> \| Ship <skill>: <one-line summary> \|` | Append: `\| <bump> \| <date> \| Retire <skill>: <reason> \|` |

### Generator Hook (advisory)

`ctyun-skill-generator` SHOULD, on a successful generation, emit an
`AGENTS.md` patch hint — a fenced `diff` block showing the exact lines to
add under §Cross-Skill Delegation and §GCL §8 — so the human reviewer can
copy-paste it into the same PR. The hint is **advisory only**; AGENTS.md is
a charter document and must be reviewed before merge.

### Skill PR Checklist (must all be true to merge)

```markdown
- [ ] `ctyun-[product]-ops/SKILL.md` passes `markdownlint`
- [ ] `references/rubric.md` and `references/prompt-templates.md` exist
- [ ] AGENTS.md updated per the Sync Matrix above (all 6 rows)
- [ ] §11 Changelog entry added
- [ ] No secrets in any committed file
- [ ] (Destructive ops only) safety gates present in both `ctyun` CLI path and SDK fallback path
```

### Anti-Patterns (doc drift)

- ❌ **Ship a skill but leave it tagged "Planned"** in AGENTS.md → the
  inventory becomes a lie.
- ❌ **List a skill in §Cross-Skill Delegation without a matching §GCL §8
  entry**, or vice versa → the two tables drift.
- ❌ **Re-tag a Retired skill as Planned** without a Changelog entry →
  history is lost.
- ❌ **Generator emits a skill but no AGENTS.md patch hint** → manual sync
  is easy to forget on a busy PR.

---

## Generator-Critic-Loop (GCL) — Adversarial Quality Gate

> Inspired by GAN's Generator/Discriminator idea, but deliberately **not** a real GAN.
> Naming: **GCL (Generator-Critic-Loop)** to avoid misleading reviewers and LLM trainees.

### 1. Purpose

Apply an adversarial **Generator ↔ Critic** loop with a quantitative rubric to every skill execution.
Most valuable in **high-side-effect cloud operations** (delete, stop, restore, IAM/KMS/DDL) where a single
mistake is unrecoverable.

| GAN (real) | GCL (this spec) |
|---|---|
| Discriminator learns sample distribution | Critic scores an **explicit rubric** |
| No termination condition | Must terminate: **PASS / MAX_ITER / SAFETY_FAIL** |
| G and D train in parallel | G and C run **sequentially** |
| Goal: "fool the D" | Goal: "pass the rubric threshold" |

### 2. Roles

| Role | Job | Input | Output | Forbidden |
|---|---|---|---|---|
| **Generator (G)** | Execute the cloud operation | user request + previous Critic feedback | result + execution trace | modifying the rubric; self-scoring |
| **Critic (C)** | Independently audit G's output | G's result + trace + rubric | scores + suggestions | calling ctyun / SDK / mutating anything |
| **Orchestrator (O)** | Loop control, termination, final return | context + C scores + budget | continue / final result | executing or scoring on its own |

**Hard constraint:** G and C MUST live in **isolated prompt contexts** (preferably isolated sessions
or sub-agents). A shared context is a "pseudo-GCL" and is explicitly banned — see §9.

### 3. Rubric (mandatory per skill)

Each `SKILL.md` MUST declare its skill-specific rubric. Minimum 5 dimensions:

| Dimension | Meaning | Scale | Default threshold |
|---|---|---|---|
| **Correctness** | Resource id / state / config actually matches the request | 0 / 0.5 / 1 | ≥ 0.5 (1.0 required for `delete` / `stop` / IAM / KMS / DDL) |
| **Safety** | Destructive op (`delete` / `stop` / `restore` / IAM / KMS / DDL) was confirmed or guarded | 0 / 1 | = 1 |
| **Idempotency** | Retrying the same call will not cause duplicate side-effects | 0 / 0.5 / 1 | ≥ 0.5 |
| **Traceability** | Output is auditable: command, params, raw response, errors all captured | 0 / 0.5 / 1 | ≥ 0.5 |
| **Spec Compliance** | Conforms to the skill's `core-concepts.md` constraints | 0 / 0.5 / 1 | ≥ 0.5 |

**Safety = 0 → ABORT immediately, regardless of total score.**

### 4. Loop Flow

```
User Request
     │
     ▼
[0] Pre-flight (Orchestrator)
    - resolve env.* and user.* variables
    - pick skill, load its rubric
     │
     ▼
[1] Generate (G) ───────────────────────┐
    - run ctyun / SDK                     │
    - capture trace                       │
     │                                    │
     ▼                                    │
[2] Critique (C)                         │
    - isolated prompt context             │
    - score every rubric dimension        │
    - emit actionable suggestions         │
     │                                    │
     ▼                                    │
[3] Decide (Orchestrator)                │
    - Safety=0  → ABORT (no partial)      │
    - all pass  → RETURN                  │
    - else & iter<max → inject           │
       suggestions into G                 │
    - else → RETURN best + unresolved     │
       rubric items                       │
     └────────────────────────────────────┘
```

### 5. Termination (first match wins)

| Condition | Behavior |
|---|---|
| **PASS** | Every rubric dimension meets its threshold → return G's result |
| **MAX_ITER** | Reached `max_iterations` (default 3) → return **best-so-far** + unresolved rubric items |
| **SAFETY_FAIL** | Safety = 0 → **ABORT**; never return partial or "best-effort" output |

`max_iterations` defaults per skill class — see §8.

### 6. Trace & Audit (mandatory)

Every GCL run MUST persist a JSON trace:

```json
{
  "skill": "ctyun-ecs-ops",
  "request": "<sanitized user request>",
  "rubric_version": "v1",
  "iterations": [
    {
      "iter": 1,
      "generator": { "command": "...", "args": {...}, "exit_code": 0, "result_excerpt": "..." },
      "critic": {
        "scores": {
          "correctness": 1, "safety": 1, "idempotency": 0.5,
          "traceability": 1, "spec_compliance": 1
        },
        "suggestions": ["..."],
        "blocking": false
      },
      "decision": "RETRY"
    }
  ],
  "final": { "status": "PASS", "iter": 2, "output": "..." }
}
```

Path: `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` — unified with the existing
`audit-results/` directory used by `ctyun-audit-ops` and `ctyun-tag-audit-ops`.

### 7. Prompt Templates (mandatory per skill)

Each skill's `references/prompt-templates.md` MUST contain:

1. **Generator Prompt Template** — placeholders: `{{user.request}}`, `{{output.critic_feedback}}`, `{{output.rubric}}`
2. **Critic Prompt Template** — placeholders: `{{output.generator_output}}`, `{{output.trace}}`, `{{output.rubric}}`

> **Placeholder syntax** MUST follow the repository-wide convention
> (see top-level **Variable Convention**): `{{env.*}}` / `{{user.*}}` / `{{output.*}}`.
> Bare `{...}` placeholders are NOT allowed in skill prompt templates.

**Critic prompt must hide the raw user request** to prevent "answer-aligned" rubber-stamping.
Recommended skeleton:

```text
You are an independent cloud-operation auditor.
You will see one execution result and its trace. Score it STRICTLY against the rubric below.
Do NOT consider the original user request — judge only what was actually done.

rubric: {{output.rubric}}
generator_output: {{output.generator_output}}
trace: {{output.trace}}

Return strict JSON:
{
  "scores": { "correctness": 0|0.5|1, "safety": 0|0.5|1, "idempotency": 0|0.5|1,
              "traceability": 0|0.5|1, "spec_compliance": 0|0.5|1 },
  "suggestions": ["≤ 3 concrete, executable improvements"],
  "blocking": true|false
}
```

### 8. Per-Skill Defaults

> **Status:** Only `ctyun-skill-generator` is **Shipped** today. All other rows
> are **Planned** defaults the meta-skill will apply when it produces the
> corresponding `ctyun-*-ops` skill. They are documented here so the generator
> has a single source of truth — **not** as a current inventory.

#### Shipped

| Skill | GCL | Default max_iter | Notes |
|---|---|---|---|
| `ctyun-skill-generator` | optional | 3 | meta operation; see [`ctyun-skill-generator/SKILL.md` §Quality Gate](ctyun-skill-generator/SKILL.md#quality-gate-gcl) for the live parameters |

#### Planned (generator will apply on first creation)

| Skill | GCL | Default max_iter | Notes |
|---|---|---|---|
| `ctyun-ecs-ops` | **required** | 2 | delete/stop are destructive |
| `ctyun-rds-ops` | **required** | 2 | instance delete / parameter group changes |
| `ctyun-mysql-ops` | **required** | 2 | DROP / DELETE / TRUNCATE |
| `ctyun-postgresql-ops` | **required** | 2 | DROP / DELETE / TRUNCATE |
| `ctyun-mongodb-ops` | **required** | 2 | dropDatabase / delete |
| `ctyun-iam-ops` | **required** | 2 | detach policy / delete role / rotate keys |
| `ctyun-kms-ops` | **required** | 2 | schedule key deletion is irreversible |
| `ctyun-eip-ops` | **required** | 2 | release EIP can break production |
| `ctyun-elb-ops` | recommended | 3 | listener / backend delete |
| `ctyun-cloudmonitor-ops` | recommended | 3 | alarm rule delete |
| `ctyun-alert-intelligence` | optional | 5 | read-only |
| `ctyun-audit-ops` | optional | 5 | read-only |
| `ctyun-tag-audit-ops` | optional | 5 | read-only |

Each skill may override `max_iter` in its own `SKILL.md` (under `## Quality Gate`).

### 8.5. Quality Gate (GCL) Section (mandatory per skill)

Every product-scoped `ctyun-*-ops` SKILL.md MUST include a `## Quality Gate (GCL)`
section (typically placed **after the execution flows** and before the
Changelog) that declares **this skill's** parameters, overriding §8 defaults
if justified. The canonical schema:

```markdown
## Quality Gate (GCL)

This skill participates in the repository-wide **Generator-Critic-Loop (GCL)**
defined in [`AGENTS.md` §Generator-Critic-Loop](../AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate).

### Parameters (override `AGENTS.md` §8 defaults)

| Parameter | Value | Reason |
|---|---|---|
| `gcl_mode` | `required` \| `recommended` \| `optional` | inherited from §8 unless justified otherwise |
| `max_iterations` | `<int>` | inherited from §8; override only with a one-line reason |
| `rubric_version` | `v1` | see `references/rubric.md` |
| `trace_path` | `./audit-results/gcl-trace-YYYYMMDD-HHMMSS.json` | unified with `ctyun-audit-ops` |
| `safety_confirm_required` | `true` \| `false` | `true` for any destructive op; `false` only for read-only skills |
| `fallback_decision_table` | `references/cli-decision-matrix.md` (or inline in SKILL.md) | reference to the CLI-first decision table the GCL Critic uses to verify fallback scope; required when any operation has `cli_applicability: sdk-only` |

### Artifacts (must exist alongside this SKILL.md)

- `references/rubric.md` — the concrete scoring rules
- `references/prompt-templates.md` — G / C / O prompt skeletons
- `references/gcl-examples.md` (optional) — annotated PASS / FAIL examples
```

**Enforcement:** the Pre-merge Gate in [§Doc Link & Cross-Reference Integrity
§Pre-merge Gate](#pre-merge-gate-doc-integrity) checks for the presence of
this section on any `ctyun-*-ops` SKILL.md. A missing Quality Gate section
on a non-`sdk-only` skill is a **blocker** for merge.

> **Why a per-skill section AND a repo-wide §8?** §8 sets the **default**
> per skill class; the per-skill section lets that skill **deviate with
> justification** (e.g. "max_iterations=4 because the only destructive op is
> a 3-step pipeline and one extra iteration helps the Critic converge").
> Defaults are cheap to override but expensive to forget.
>
> **Reference implementation:** [`ctyun-skill-generator/SKILL.md` §Quality Gate](ctyun-skill-generator/SKILL.md#quality-gate-gcl).

### 9. Anti-Patterns (banned)

- ❌ **Shared context G+C** — defeats independence → banned
- ❌ **Subjective scoring** — Critic must use the rubric, not "vibes" → banned
- ❌ **Unbounded loop** — always hard-cap iterations → banned
- ❌ **Critic sees the user request** — encourages rubber-stamping → banned
- ❌ **Silently downgrade on Safety fail** — must ABORT visibly → banned
- ❌ **Trace not persisted** — no post-mortem possible → banned
- ❌ **Critic mutates resources** — Critic is read-only by definition → banned

### 10. Rollout Roadmap

> **Status:** All four phases are **planned**. The GCL framework is **defined but
> not yet running in production** end-to-end. `ctyun-skill-generator` is the
> only skill that has instantiated the `rubric.md` + `prompt-templates.md`
> artifacts (see [`ctyun-skill-generator/references/`](ctyun-skill-generator/references/));
> the **Orchestrator** (`scripts/gcl_runner.py`) and the **trace pipeline** do
> not exist yet.

- **Phase 1 — Validate on the only shipped skill.** Exercise GCL end-to-end on
  a sample `ctyun-skill-generator` request: produce a `gcl-trace-*.json`,
  confirm the rubric + Critic prompts run in isolated contexts, and verify the
  Safety=0 → ABORT behavior. Goal: prove the framework works before any
  destructive ops skill is built on top of it.
- **Phase 2 — Orchestrator.** Add `scripts/gcl_runner.py` as a reusable
  Orchestrator that any `ctyun-*-ops` skill can import.
- **Phase 3 — Quality dashboard.** Feed `gcl-trace-*.json` into
  `ctyun-audit-ops` for quality dashboards (see
  [`docs/GCL_RETROSPECTIVE.md`](docs/GCL_RETROSPECTIVE.md)).
- **Phase 4 — Alarm wiring.** Wire rubric pass-rate to Cloud Monitor alarms
  (real incidents refine thresholds).

### 11. Changelog

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-06-05 | Initial AGENTS.md for CTyun Skills Farm — adapted from JD Cloud Skills pattern with CTyun-specific naming and conventions |

### 12. See also

- [`docs/GCL_RETROSPECTIVE.md`](docs/GCL_RETROSPECTIVE.md) — post-rollout retrospective and Phase 3 dashboard design contract
- Each skill's `references/rubric.md` — the rubric instance
- Each skill's `references/prompt-templates.md` — the G/C/O prompt skeletons
