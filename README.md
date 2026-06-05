# CTyun Skills Farm

A collection of **AI Agent Skill definitions** (structured Markdown documents following the
[Agent Skills OpenSpec](https://agentskills.io/specification)) that enable AI agents to perform
**CTyun (天翼云)** cloud operations. Each skill maps to one CTyun product, follows a
**CLI-first with SDK fallback** execution policy, and implements an adversarial
**Generator-Critic-Loop (GCL)** quality gate.

> This repo is the **single source of truth** for all CTyun product skills. The repository charter
> [`AGENTS.md`](AGENTS.md) defines the CLI-First Policy, Token Efficiency budgets, Doc Link
> Integrity, Generator-Critic-Loop (GCL), and the Skill Lifecycle & Doc Sync Convention.

---

## Status

| Component | Status |
|---|---|
| [`ctyun-skill-generator`](ctyun-skill-generator/) — Meta Skill | **Shipped** (v1.0.0) |
| [`ctyun-cloudmonitor-ops`](ctyun-cloudmonitor-ops/) — Cloud Monitor | **Shipped** (v1.0.0) |
| [`ctyun-ecs-ops`](ctyun-ecs-ops/) — ECS | **Shipped** (v1.0.0) |
| [`ctyun-iam-ops`](ctyun-iam-ops/) — IAM | **Shipped** (v1.0.0) |
| [`ctyun-redis-ops`](ctyun-redis-ops/) — Redis | **Shipped** (v1.0.0) |
| [`ctyun-elb-ops`](ctyun-elb-ops/) — ELB | **Shipped** (v1.0.0) |
| [`ctyun-eip-ops`](ctyun-eip-ops/) — EIP | **Shipped** (v1.0.0) |
| [`ctyun-cce-ops`](ctyun-cce-ops/) — CCE | **Shipped** (v1.0.0) |
| [`ctyun-kms-ops`](ctyun-kms-ops/) — KMS | **Shipped** (v1.0.0) |
| Other `ctyun-*-ops` product skills | **Planned** (4 skills) |
| GCL Phase 1 (validate on shipped skills) | **In Progress** |
| GCL Phase 2 (Orchestrator: `scripts/gcl_runner.py`) | Planned |
| GCL Phase 3 (Quality dashboard) | Planned |
| GCL Phase 4 (Alarm wiring) | Planned |

---

## Shipped Skills

| Skill | Product | Ops | GCL | Path |
|---|---|---|---|---|
| [ctyun-skill-generator](ctyun-skill-generator/) | Meta Skill | Generate new `ctyun-*-ops` skills from OpenAPI docs | optional | `ctyun-skill-generator/` |
| [ctyun-cloudmonitor-ops](ctyun-cloudmonitor-ops/) | Cloud Monitor | Alarm rule CRUD, metric query, alarm history analysis | recommended | `ctyun-cloudmonitor-ops/` |
| [ctyun-ecs-ops](ctyun-ecs-ops/) | Elastic Cloud Server | Instance lifecycle (create/start/stop/reboot/delete), snapshots, key pairs, images | **required** | `ctyun-ecs-ops/` |
| [ctyun-iam-ops](ctyun-iam-ops/) | IAM | User/group/policy/role/AK/enterprise-project/MFA management | **required** | `ctyun-iam-ops/` |
| [ctyun-redis-ops](ctyun-redis-ops/) | Redis | Instance lifecycle (create/describe/delete/flush/config) | **required** | `ctyun-redis-ops/` |
| [ctyun-elb-ops](ctyun-elb-ops/) | ELB | Listener/backend/certificate lifecycle management | recommended | `ctyun-elb-ops/` |
| [ctyun-eip-ops](ctyun-eip-ops/) | Elastic IP | IP lifecycle (allocate/associate/disassociate/release) | **required** | `ctyun-eip-ops/` |
| [ctyun-cce-ops](ctyun-cce-ops/) | CCE | Cluster/node/task lifecycle management | **required** | `ctyun-cce-ops/` |
| [ctyun-kms-ops](ctyun-kms-ops/) | KMS | Key lifecycle (create/encrypt/decrypt/schedule-delete) | **required** | `ctyun-kms-ops/` |

---

## Planned Skills

Skills that `ctyun-skill-generator` will produce, ordered by priority:

| Skill | Product | GCL | max_iter |
|---|---|---|---|
| `ctyun-rds-ops` | RDS | required | 2 |
| `ctyun-alert-intelligence` | Alert Analysis (read-only) | optional | 5 |
| `ctyun-mysql-ops` / `ctyun-postgresql-ops` / `ctyun-mongodb-ops` | Database series | required | 2 |

> Full 12-item list with `max_iter` defaults in [`AGENTS.md` §GCL §8](AGENTS.md#8-per-skill-defaults).

---

## Project Structure

```
ctyun-skills/
├── README.md                               # This file
├── AGENTS.md                               # Repository charter (CLI-First, GCL, Token Efficiency, Doc Integrity)
├── LICENSE                                 # MIT
├── pyproject.toml                          # Python project metadata (uv-managed)
├── .env.example                            # Credential template (.env is gitignored)
├── docs/
│   └── GCL_RETROSPECTIVE.md               # GCL rollout retrospective & Phase 3 dashboard design
├── audit-results/                          # GCL trace persistence (planned)
├── scripts/
│   ├── preflight-check.py                  # Environment verification
│   └── check_*.py                          # Validation stubs (planned)
├── ctyun-skill-generator/                  # Shipped: Meta Skill
│   ├── SKILL.md
│   └── references/
│       ├── ctyun-skill-template.md
│       ├── governance-and-adversarial-review.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── cli-decision-matrix.md
├── ctyun-cloudmonitor-ops/                 # Shipped: Cloud Monitor
│   ├── SKILL.md
│   ├── assets/
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
├── ctyun-ecs-ops/                          # Shipped: ECS
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
├── ctyun-iam-ops/                          # Shipped: IAM
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
├── ctyun-redis-ops/                        # Shipped: Redis
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
├── ctyun-elb-ops/                          # Shipped: ELB
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
├── ctyun-eip-ops/                          # Shipped: EIP
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
├── ctyun-cce-ops/                          # Shipped: CCE
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
└── ctyun-kms-ops/                          # Shipped: KMS
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

---

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- CTyun account with API credentials

### Setup

```bash
# Create virtual environment
uv venv --python 3.10
source .venv/bin/activate

# Install CTyun CLI and SDK
uv pip install ctyun-cli ctyun-sdk

# Create symlink (ctyun-cli package installs `ctyun-cli` binary)
ln -sf "$(which ctyun-cli)" ~/.local/bin/ctyun

# Run preflight check
python3 scripts/preflight-check.py --verbose --fix
```

### Credentials

Three methods (priority: shell env > `.env` > `~/.ctyun/config`):

**SDK mode** — reads from environment variables:
```bash
export CTYUN_ACCESS_KEY="your_access_key"
export CTYUN_SECRET_KEY="your_secret_key"
export CTYUN_REGION="cn-gz"
```

**CLI mode** — reads from INI file only (`~/.ctyun/config`):
```ini
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region_id = cn-gz
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
```

> **Safety**: Never print or log `CTYUN_SECRET_KEY`. Only check existence with `test -n`.

### CLI Quirks (Common Agent Mistakes)

| Rule | Wrong | Correct |
|---|---|---|
| `--output json` placement | `ctyun ecs list --output json` | `ctyun --output json ecs list` |
| `--no-interactive` flag | `ctyun --no-interactive ecs delete` | **Omit** — not supported |
| CLI credentials | `export CTYUN_ACCESS_KEY=...` (CLI ignores) | Write `~/.ctyun/config` INI file |
| `~/.ctyun/current` newline | `echo "default" > file` | `printf "%s" "default" > file` |

---

## Key Concepts

### CLI-First with SDK Fallback

Every `ctyun-*-ops` skill follows:

```
ctyun <product> <op> exists?
  ├─ yes → try CLI (3 retries, exponential backoff)
  │         ├─ success → continue
  │         └─ 3 fails → SDK fallback (per-operation)
  └─ no → mark `cli_applicability: sdk-only` for this op; use SDK
```

Fallback is **per-operation**, not per-skill. If 1 of 12 ops fails, only that op falls back; the other 11 still use CLI. The 9-item "CLI 不满足" classifier (Environment / Capability / Runtime / Business) determines fallback scope and retry behavior.

Full decision matrix: [`ctyun-skill-generator/references/cli-decision-matrix.md`](ctyun-skill-generator/references/cli-decision-matrix.md)

### Generator-Critic-Loop (GCL)

An adversarial quality gate inspired by GANs (but not a GAN). Every skill has a **rubric** (≥5 dimensions) and a **Critic** that independently scores Generator output. Loop terminates on PASS, MAX_ITER, or SAFETY_FAIL (destructive op without confirmation → abort immediately).

Each skill ships:
- `references/rubric.md` — scoring rules
- `references/prompt-templates.md` — Generator / Critic / Orchestrator prompt skeletons

Full spec: [`AGENTS.md` §Generator-Critic-Loop](AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate)

### Token Efficiency & Deduplication

| Artifact | Soft cap | Hard cap |
|---|---|---|
| `SKILL.md` (body) | 400 lines | 600 lines |
| `references/*.md` (each) | 300 lines | 800 lines |
| Total per skill | — | 3000 lines |

Common content (credential loading, CLI quirks, safety gate templates) is factored once and linked, never duplicated.

---

## Developing a New Skill

1. Load `ctyun-skill-generator` and its references as input context
2. Provide a prompt: product name, OpenAPI URL, core operations
3. Generator produces the skill directory with `SKILL.md` + `references/`
4. **Same commit**: update `AGENTS.md` per the 6-item Sync Matrix
5. Pass the 7-item Pre-merge Gate (markdownlint, link integrity, artifact existence, line budgets)

See [`AGENTS.md` §Skill Lifecycle & Doc Sync Convention](AGENTS.md#skill-lifecycle--doc-sync-convention) for the full process.

---

## Validation

```bash
# Markdown lint
npm install -g markdownlint-cli
markdownlint ctyun-*-ops/SKILL.md

# Link integrity (offline, check anchors)
npm install -g lychee
lychee --offline --include-fragments '**/*.md'

# Environment check
python3 scripts/preflight-check.py --verbose --fix
```

---

## Roadmap

| Phase | Goal | Status |
|---|---|---|
| **Phase 1** | End-to-end GCL on shipped skills (trace + Critic isolation) | In Progress |
| **Phase 2** | `scripts/gcl_runner.py` — reusable Orchestrator | Planned |
| **Phase 3** | Quality dashboard from `gcl-trace-*.json` | Planned |
| **Phase 4** | Rubric pass-rate → Cloud Monitor alarms | Planned |

---

## References

- [Repository Charter (AGENTS.md)](AGENTS.md)
- [Skill Generator](ctyun-skill-generator/SKILL.md)
- [Cloud Monitor Skill](ctyun-cloudmonitor-ops/SKILL.md)
- [ECS Skill](ctyun-ecs-ops/SKILL.md)
- [IAM Skill](ctyun-iam-ops/SKILL.md)
- [Redis Skill](ctyun-redis-ops/SKILL.md)
- [ELB Skill](ctyun-elb-ops/SKILL.md)
- [EIP Skill](ctyun-eip-ops/SKILL.md)
- [CCE Skill](ctyun-cce-ops/SKILL.md)
- [KMS Skill](ctyun-kms-ops/SKILL.md)
- [CLI-First Decision Matrix](ctyun-skill-generator/references/cli-decision-matrix.md)
- [GCL Rubric](ctyun-skill-generator/references/rubric.md)
- [GCL Prompt Templates](ctyun-skill-generator/references/prompt-templates.md)
- [GCL Retrospective](docs/GCL_RETROSPECTIVE.md)
- [Agent Skills OpenSpec](https://agentskills.io/specification)
- [CTyun Official Docs](https://www.ctyun.cn/document/)

---

## License

MIT — see [LICENSE](LICENSE).