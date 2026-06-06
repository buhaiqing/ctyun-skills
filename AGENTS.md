# CTyun Skills Farm

## Quick Identity

**CTyun Skills Farm** is a collection of AI Agent Skill definitions (structured Markdown documents following the Agent Skill OpenSpec) that enable AI agents to perform CTyun (天翼云) operations. Each skill maps to one CTyun product.

## Repo Layout

> **Status:** The **meta-skill**, **`ctyun-cloudmonitor-ops`**, **`ctyun-ecs-ops`**,
> **`ctyun-iam-ops`**, **`ctyun-redis-ops`**, **`ctyun-elb-ops`**, **`ctyun-eip-ops`**,
> **`ctyun-cce-ops`**, **`ctyun-kms-ops`**, **`ctyun-oos-ops`**, **`ctyun-rds-ops`**,
> **`ctyun-mysql-ops`**, **`ctyun-postgresql-ops`**, **`ctyun-mongodb-ops`**,
> **`ctyun-dns-ops`**, **`ctyun-cdn-ops`**, **`ctyun-waf-ops`**,
> **`ctyun-ssl-cert-ops`**, **`ctyun-bastion-ops`**, **`ctyun-cloudaudit-ops`**,
> and **`ctyun-vpc-ops`** are shipped.
> Most other product skills are **planned** and will be produced
> by `ctyun-skill-generator`. The layout here reflects what is **currently on disk**.

```
ctyun-skills/
├── README.md                                       # Project readme (full documentation)
├── AGENTS.md                                       # ← this file (repo constitution)
├── LICENSE                                         # MIT
├── pyproject.toml                                  # Project metadata (uv-managed)
├── .env.example                                    # Credential template (gitignored real .env)
├── docs/
│   └── GCL_RETROSPECTIVE.md                        # GCL rollout retrospective & dashboard design
├── ctyun-skill-generator/                          # Shipped: meta-skill
│   ├── SKILL.md
│   └── references/
│       ├── ctyun-skill-template.md
│       ├── governance-and-adversarial-review.md
│       ├── prompt-templates.md
│       └── rubric.md
├── ctyun-cloudmonitor-ops/                         # Shipped: Cloud Monitor operations
│   ├── SKILL.md
│   └── references/
│       ├── alarm-rules-examples.md
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── log-analysis-guide.md
│       ├── monitoring.md
│       ├── notification-best-practices.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-ecs-ops/                                  # Shipped: ECS operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-iam-ops/                                  # Shipped: IAM operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-redis-ops/                                # Shipped: Redis operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-elb-ops/                                  # Shipped: ELB operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-eip-ops/                                  # Shipped: EIP operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-cce-ops/                                  # Shipped: CCE operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-oos-ops/                                  # Shipped: OOS operations
│   ├── SKILL.md
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-rds-ops/                                  # Shipped: RDS operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-mysql-ops/                                # Shipped: MySQL data operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-postgresql-ops/                           # Shipped: PostgreSQL data operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-dns-ops/                                   # Shipped: DNS operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-cdn-ops/                                   # Shipped: CDN operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-waf-ops/                                   # Shipped: WAF operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-ssl-cert-ops/                              # Shipped: SSL Certificate operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-bastion-ops/                               # Shipped: Cloud Bastion Host operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-cloudaudit-ops/                            # Shipped: Cloud Audit operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── cli-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
├── ctyun-vpc-ops/                                     # Shipped: VPC operations
│   ├── SKILL.md
│   ├── assets/
│   └── references/
│       ├── api-sdk-usage.md
│       ├── core-concepts.md
│       ├── integration.md
│       ├── monitoring.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── troubleshooting.md
└── ctyun-mongodb-ops/                              # Shipped: MongoDB operations
    ├── SKILL.md
    ├── assets/
    └── references/
        ├── api-sdk-usage.md
        ├── cli-usage.md
        ├── core-concepts.md
        ├── integration.md
        ├── monitoring.md
        ├── prompt-templates.md
        ├── rubric.md
        └── troubleshooting.md
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

> The schema above is the **target layout** for new skills that the meta-skill
> will scaffold; it is documented here for the generator's contract,
> not as a current inventory. `ctyun-cloudmonitor-ops` does not follow this
> exact layout (no `assets/` directory) — see [§Token Efficiency & Skill Deduplication](#token-efficiency--skill-deduplication) for the actual structure.

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

# Create symlink for compatibility (ctyun-cli → ctyun)
ln -sf $(which ctyun-cli) ~/.local/bin/ctyun

# Verify installation
python3 scripts/preflight-check.py --verbose
```

`pyproject.toml` pins `ctyun-cli>=1.0.0`. The default pip index is `https://pypi.org/simple/` (configured under `[tool.uv]`).

**Note**: The `ctyun-cli` package installs `ctyun-cli` binary, not `ctyun`. The symlink ensures backward compatibility with documentation.

### Git Worktree Development Workflow

> See full conventions in [`docs/git-worktree-workflow.md`](docs/git-worktree-workflow.md).
>
> All development **MUST** use isolated git worktrees to protect the `main` branch.
> Direct edits on `main` are discouraged for non-trivial changes.

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
| **Command name** | `ctyun` (assumed) | `ctyun-cli` (actual binary); create symlink: `ln -sf $(which ctyun-cli) ~/.local/bin/ctyun` |
| `--output json` placement | `ctyun-cli ecs list --output json` | `ctyun-cli --output json ecs list` |
| `--no-interactive` flag | `ctyun-cli --no-interactive ecs delete` | **Omit entirely** — not supported |
| Credentials | `export CTYUN_ACCESS_KEY=...` (CLI ignores) | Must write `~/.ctyun/config` INI file |
| `~/.ctyun/current` newline | `echo "default" > file` (adds newline) | `printf "%s" "default" > file` (no trailing newline) |

## Execution Strategy

**ctyun-first with SDK fallback** — the repository-wide policy:

### Pre-flight Environment Check (Mandatory)

Before any operation, run the intelligent preflight check:
```bash
python3 scripts/preflight-check.py --verbose --fix
```

This checks:
1. ✅ Python 3.10+ compatibility
2. ✅ `ctyun-cli` installation (creates `ctyun` symlink if missing)
3. ✅ Credential configuration (`.env`, `~/.ctyun/config`, or env vars)
4. ✅ Basic CLI functionality

### CLI Execution Flow

1. **Pre-flight**: Run `scripts/preflight-check.py`; fix any Environment-class issues
2. **Primary path**: Try `ctyun-cli --output json <command>` first (or `ctyun` if symlink exists)
3. **Retry**: On failure, retry up to 3 times with exponential backoff (0s → 2s → 4s)
4. **Fallback**: After 3 consecutive failures, fall back to Python SDK (`ctyun_sdk`)
5. **Documentation**: Record which path was used in execution trace

### Command Name Resolution

The `ctyun-cli` package installs `ctyun-cli` binary, not `ctyun`. For compatibility:
- **Option A (recommended)**: Create symlink: `ln -sf $(which ctyun-cli) ~/.local/bin/ctyun`
- **Option B**: Update all commands to use `ctyun-cli` explicitly
- **Option C**: Use `scripts/preflight-check.py --fix` to auto-create symlink

All documentation uses `ctyun` for readability, but agents must resolve to `ctyun-cli`.

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
> [§Validation](#validation)). Soft cap is a PR comment; hard cap is a
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

> **Status:** `ctyun-skill-generator`, `ctyun-cloudmonitor-ops`,
> `ctyun-ecs-ops`, `ctyun-iam-ops`, `ctyun-redis-ops`, `ctyun-elb-ops`,
> `ctyun-eip-ops`, `ctyun-cce-ops`, `ctyun-kms-ops`, `ctyun-oos-ops`,
> `ctyun-rds-ops`, `ctyun-mysql-ops`, `ctyun-postgresql-ops`,
> `ctyun-mongodb-ops`, `ctyun-dns-ops`, `ctyun-cdn-ops`,
> `ctyun-waf-ops`, `ctyun-ssl-cert-ops`, `ctyun-bastion-ops`, and
> `ctyun-cloudaudit-ops` are **Shipped**.

| If they ask about | Delegate to | Status |
|---|---|---|
| Generate a new product skill | `ctyun-skill-generator` | **Shipped** |
| Monitoring metrics, alarm rules | `ctyun-cloudmonitor-ops` | **Shipped** |
| ECS create/stop/delete | `ctyun-ecs-ops` | **Shipped** |
| IAM users, policies, keys | `ctyun-iam-ops` | **Shipped** |
| Redis instance CRUD | `ctyun-redis-ops` | **Shipped** |
| Load balancer config | `ctyun-elb-ops` | **Shipped** |
| Elastic IP lifecycle (allocate/associate/disassociate/release) | `ctyun-eip-ops` | **Shipped** |
| CCE cluster/node/task management | `ctyun-cce-ops` | **Shipped** |
| Key management, encryption | `ctyun-kms-ops` | **Shipped** |
| Object storage, bucket CRUD, file upload/download | `ctyun-oos-ops` | **Shipped** |
| RDS instance CRUD | `ctyun-rds-ops` | **Shipped** |
| MySQL SQL queries, DDL/DML, user management | `ctyun-mysql-ops` | **Shipped** |
| PostgreSQL SQL queries, DDL/DML, role management | `ctyun-postgresql-ops` | **Shipped** |
| MongoDB instance CRUD, queries, aggregations | `ctyun-mongodb-ops` | **Shipped** |
| DNS domain management, record set CRUD | `ctyun-dns-ops` | **Shipped** |
| CDN acceleration domain lifecycle, cache config, refresh/prefetch, HTTPS | `ctyun-cdn-ops` | **Shipped** |
| WAF instance/domain/rule/ACL management | `ctyun-waf-ops` | **Shipped** |
| SSL certificate lifecycle (apply/upload/delete/deploy/expiry) | `ctyun-ssl-cert-ops` | **Shipped** |
| Cloud Bastion Host instance/user/host/policy management | `ctyun-bastion-ops` | **Shipped** |
| Cloud Audit log query, export, statistics (read-only) | `ctyun-cloudaudit-ops` | **Shipped** |
| VPC lifecycle, subnet, route table, peering management | `ctyun-vpc-ops` | **Shipped** |
| Alert analysis, suppression, reporting | `ctyun-alert-intelligence` | **Shipped** |
| Audit log query, filtering, export, compliance reports | `ctyun-audit-ops` | **Shipped** |
| Tag compliance audit, untagged resource discovery | `ctyun-tag-audit-ops` | **Shipped** |
| _(no skills currently planned)_ | — | — |

- `ctyun-alert-intelligence`, `ctyun-audit-ops`, and `ctyun-tag-audit-ops` are **read-only** — they analyze/trace/audit but delegate resource mutations back to the appropriate CRUD skill.
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

> **Status:** `ctyun-skill-generator`, `ctyun-cloudmonitor-ops`, `ctyun-ecs-ops`,
> `ctyun-iam-ops`, `ctyun-redis-ops`, `ctyun-elb-ops`, `ctyun-eip-ops`,
> `ctyun-cce-ops`, `ctyun-kms-ops`, `ctyun-oos-ops`, `ctyun-rds-ops`,
> `ctyun-mysql-ops`, `ctyun-postgresql-ops`, `ctyun-mongodb-ops`,
> `ctyun-dns-ops`, `ctyun-cdn-ops`, `ctyun-waf-ops`, `ctyun-ssl-cert-ops`,
> `ctyun-bastion-ops`, `ctyun-cloudaudit-ops`, and `ctyun-vpc-ops` are **Shipped**.
> All other rows are **Planned** defaults the meta-skill will apply when it
> produces the corresponding `ctyun-*-ops` skill. They are documented here so
> the generator has a single source of truth — **not** as a current inventory.

#### Shipped

| Skill | GCL | Default max_iter | Notes |
|---|---|---|---|
| `ctyun-skill-generator` | optional | 3 | meta operation; see [`ctyun-skill-generator/SKILL.md` §Quality Gate](ctyun-skill-generator/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-cloudmonitor-ops` | recommended | 3 | alarm rule delete; see [`ctyun-cloudmonitor-ops/SKILL.md` §Quality Gate](ctyun-cloudmonitor-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-ecs-ops` | **required** | 2 | delete/stop are destructive; see [`ctyun-ecs-ops/SKILL.md` §Quality Gate](ctyun-ecs-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-iam-ops` | **required** | 2 | delete user/group/policy/role/AK are destructive; see [`ctyun-iam-ops/SKILL.md` §Quality Gate](ctyun-iam-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-redis-ops` | **required** | 2 | delete/flush are destructive; see [`ctyun-redis-ops/SKILL.md` §Quality Gate](ctyun-redis-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-elb-ops` | recommended | 3 | listener / backend delete; see [`ctyun-elb-ops/SKILL.md` §Quality Gate](ctyun-elb-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-eip-ops` | **required** | 2 | release EIP can break production; see [`ctyun-eip-ops/SKILL.md` §Quality Gate](ctyun-eip-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-cce-ops` | **required** | 2 | cluster delete / node drain are destructive; see [`ctyun-cce-ops/SKILL.md` §Quality Gate](ctyun-cce-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-kms-ops` | **required** | 2 | schedule key deletion is irreversible; see [`ctyun-kms-ops/SKILL.md` §Quality Gate](ctyun-kms-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-oos-ops` | **required** | 2 | delete bucket/object can cause data loss; see [`ctyun-oos-ops/SKILL.md` §Quality Gate](ctyun-oos-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-rds-ops` | **required** | 2 | instance delete can cause data loss; see [`ctyun-rds-ops/SKILL.md` §Quality Gate](ctyun-rds-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-mysql-ops` | **required** | 2 | DROP / DELETE / TRUNCATE; see [`ctyun-mysql-ops/SKILL.md` §Quality Gate](ctyun-mysql-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-postgresql-ops` | **required** | 2 | DROP / DELETE / TRUNCATE; see [`ctyun-postgresql-ops/SKILL.md` §Quality Gate](ctyun-postgresql-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-mongodb-ops` | **required** | 2 | dropDatabase / delete; see [`ctyun-mongodb-ops/SKILL.md` §Quality Gate](ctyun-mongodb-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-dns-ops` | **required** | 2 | delete domain/record can disrupt production DNS; see [`ctyun-dns-ops/SKILL.md` §Quality Gate](ctyun-dns-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-cdn-ops` | **required** | 2 | delete/disable domain can break live traffic; see [`ctyun-cdn-ops/SKILL.md` §Quality Gate](ctyun-cdn-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-waf-ops` | **required** | 2 | domain/rule/ACL delete can disrupt protection; see [`ctyun-waf-ops/SKILL.md` §Quality Gate](ctyun-waf-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-ssl-cert-ops` | **required** | 2 | delete certificate can break HTTPS; see [`ctyun-ssl-cert-ops/SKILL.md` §Quality Gate](ctyun-ssl-cert-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-bastion-ops` | **required** | 2 | delete/restart instance can block access; see [`ctyun-bastion-ops/SKILL.md` §Quality Gate](ctyun-bastion-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-cloudaudit-ops` | optional | 3 | read-only; see [`ctyun-cloudaudit-ops/SKILL.md` §Quality Gate](ctyun-cloudaudit-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-vpc-ops` | **required** | 3 | VPC delete is destructive; see [`ctyun-vpc-ops/SKILL.md` §Quality Gate](ctyun-vpc-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-alert-intelligence` | optional | 5 | read-only; see [`ctyun-alert-intelligence/SKILL.md` §Quality Gate](ctyun-alert-intelligence/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-audit-ops` | optional | 5 | read-only; see [`ctyun-audit-ops/SKILL.md` §Quality Gate](ctyun-audit-ops/SKILL.md#quality-gate-gcl) for the live parameters |
| `ctyun-tag-audit-ops` | optional | 5 | read-only; see [`ctyun-tag-audit-ops/SKILL.md` §Quality Gate](ctyun-tag-audit-ops/SKILL.md#quality-gate-gcl) for the live parameters |

#### Planned (generator will apply on first creation)

| Skill | GCL | Default max_iter | Notes |
|---|---|---|---|
| _(no skills currently planned)_ | — | — | — |

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

> **Status:** Phase 1 **Complete** (2026-06-05). All 20 shipped skills validated:
> `gcl_runner.py` dry-run produces trace files; rubric + Critic run in isolated
> mock contexts; Safety=0 → ABORT verified. 19/20 skills parse operations from
> SKILL.md; cloudmonitor, vpc, and 3 new read-only skills use alternative
> and fall back to inference. No real cloud credentials required.
> **Phase 4 Complete** (2026-06-05): `scripts/gcl_monitor_alarms.py`
> evaluates trace metrics against thresholds (P0: safety>0, P1: pass rate<70%,
> P2: avg iterations>2.8) with cooldown and auto-mute logic.
>
> **Status:** All phases complete below:

- **Phase 1 — Validate on shipped skills.** Exercise GCL end-to-end on
  `ctyun-skill-generator` and `ctyun-cloudmonitor-ops` requests: produce
  `gcl-trace-*.json` files, confirm the rubric + Critic prompts run in isolated
  contexts, and verify the Safety=0 → ABORT behavior. Goal: prove the framework
  works before any destructive ops skill is built on top of it.
- **Phase 2 — Orchestrator.** Added `scripts/gcl_runner.py` as a reusable
  Orchestrator that any `ctyun-*-ops` skill can import. Supports dry-run
  (mock) and plugin (subprocess) modes. Reads SKILL.md operations and
  rubric.md thresholds for realistic scoring. **Complete.**
- **Phase 3 — Quality dashboard.** Added `scripts/gcl_dashboard.py` that
  consumes `gcl-trace-*.json` files for quality dashboards (see
  [`docs/GCL_RETROSPECTIVE.md`](docs/GCL_RETROSPECTIVE.md)). Supports text and
  JSON output modes. **Complete.**
- **Phase 4 — Alarm wiring.** Wire rubric pass-rate to Cloud Monitor alarms
  (real incidents refine thresholds). **Complete:** `scripts/gcl_monitor_alarms.py`
  evaluates traces against P0/P1/P2 thresholds with cooldown and auto-mute.

### 11. Changelog

| Version | Date | Change |
|---|---|---|
| 1.21.0 | 2026-06-05 | Ship `ctyun-alert-intelligence`, `ctyun-audit-ops`, `ctyun-tag-audit-ops`: 3 read-only analysis skills (optional GCL, max_iter=5) |
| 1.20.0 | 2026-06-05 | Ship `ctyun-vpc-ops`: VPC lifecycle (create/list/delete), subnet, route table, peering via SDK-only with GCL quality gate (required) |
| 1.19.0 | 2026-06-05 | Ship `ctyun-cloudaudit-ops`: Cloud Audit log query, export, statistics via REST API with SDK-only and GCL quality gate (read-only, optional GCL) |
| 1.18.0 | 2026-06-05 | Ship `ctyun-bastion-ops`: Cloud Bastion Host instance/user/host/policy management via REST API with SDK-only and GCL quality gate |
| 1.17.0 | 2026-06-05 | Ship `ctyun-ssl-cert-ops`: SSL certificate lifecycle (apply/upload/delete/deploy/expiry) via REST API with SDK-only and GCL quality gate |
| 1.16.0 | 2026-06-05 | Ship `ctyun-waf-ops`: WAF instance/domain/rule/ACL management via REST API with SDK-only and GCL quality gate |
| 1.15.0 | 2026-06-05 | Ship `ctyun-cdn-ops`: CDN acceleration domain lifecycle, cache config, refresh/prefetch, HTTPS, ACL via REST API with SDK-only and GCL quality gate |
| 1.14.0 | 2026-06-05 | Ship `ctyun-dns-ops`: DNS domain management and record set CRUD via REST API with SDK-only and GCL quality gate |
| 1.13.0 | 2026-06-05 | Ship `ctyun-mongodb-ops`: MongoDB instance CRUD via REST API + data operations via mongosh CLI with SDK-only and GCL quality gate |
| 1.12.0 | 2026-06-05 | Ship `ctyun-postgresql-ops`: PostgreSQL SQL queries, DDL/DML, role management via psql CLI with SDK-only and GCL quality gate |
| 1.11.0 | 2026-06-05 | Ship `ctyun-mysql-ops`: MySQL SQL queries, DDL/DML, user management via mysql CLI with SDK-only and GCL quality gate |
| 1.10.0 | 2026-06-05 | Ship `ctyun-rds-ops`: RDS instance lifecycle (create/delete/resize/backup/restore) via REST API with SDK-only and GCL quality gate |
| 1.9.0 | 2026-06-05 | Ship `ctyun-oos-ops`: Object-Oriented Storage bucket/object lifecycle operations with SDK-only and GCL quality gate |
| 1.8.0 | 2026-06-05 | Ship `ctyun-kms-ops`: KMS key lifecycle operations (create/encrypt/decrypt/schedule-delete) with dual-path and GCL quality gate |
| 1.7.0 | 2026-06-05 | Ship `ctyun-cce-ops`: CCE cluster node/task operations (create/delete/resize/list) with dual-path and GCL quality gate |
| 1.6.0 | 2026-06-05 | Ship `ctyun-eip-ops`: Elastic IP lifecycle operations (allocate/associate/disassociate/release) with dual-path and GCL quality gate |
| 1.5.0 | 2026-06-05 | Ship `ctyun-elb-ops`: ELB lifecycle operations (listeners, backends, certificates) with dual-path and GCL quality gate |
| 1.4.0 | 2026-06-05 | Ship `ctyun-redis-ops`: Redis instance lifecycle (create/describe/delete/flush/config) with dual-path and GCL quality gate |
| 1.3.0 | 2026-06-05 | Ship `ctyun-iam-ops`: IAM identity/access management (user/group/policy/role/AK/enterprise-project/MFA) with dual-path and GCL quality gate |
| 1.2.0 | 2026-06-05 | Ship `ctyun-ecs-ops`: ECS lifecycle operations (create/start/stop/delete) with CLI-first policy and GCL quality gate |
| 1.1.0 | 2026-06-05 | Ship `ctyun-cloudmonitor-ops`: Cloud Monitor alarm rule operations with dual-path (SDK + CLI) and GCL quality gate |
| 1.0.0 | 2026-06-05 | Initial AGENTS.md for CTyun Skills Farm — adapted from JD Cloud Skills pattern with CTyun-specific naming and conventions |

### 12. See also

- [`docs/GCL_RETROSPECTIVE.md`](docs/GCL_RETROSPECTIVE.md) — post-rollout retrospective and Phase 3 dashboard design contract
- Each skill's `references/rubric.md` — the rubric instance
- Each skill's `references/prompt-templates.md` — the G/C/O prompt skeletons
