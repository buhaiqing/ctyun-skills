# Task Plan: Build 4 Database CTyun Skills

## Goal
Create `ctyun-rds-ops`, `ctyun-mysql-ops`, `ctyun-postgresql-ops`, and `ctyun-mongodb-ops` skills following shipped skill patterns (OOS, EIP, KMS).

## Research Summary
- **ctyun-cli v1.20.2** has NO `rds` or `mongodb` subcommands → `sdk-only` for all four
- **ctyun-sdk** does NOT exist on PyPI → no unified SDK; skills use product-specific tools
- All four skills: `cli_applicability: sdk-only`
- AGENTS.md GCL §8 says all four have GCL `required`, `max_iter=2`
- Cross-skill delegation: `ctyun-rds-ops` already listed as Planned in AGENTS.md line 425

## Skill Architecture

| Skill | Operations | Execution Method | GCL |
|---|---|---|---|
| `ctyun-rds-ops` | RDS instance lifecycle (create/describe/delete/resize/backup) | CTyun OpenAPI (REST) | required |
| `ctyun-mysql-ops` | MySQL data ops (DROP/DELETE/TRUNCATE/ALTER) | MySQL CLI client | required |
| `ctyun-postgresql-ops` | PostgreSQL data ops (DROP/DELETE/TRUNCATE/ALTER) | psql CLI client | required |
| `ctyun-mongodb-ops` | MongoDB instance + data ops | mongosh + CTyun OpenAPI | required |

## Phases

### Phase 1: Create task_plan.md + findings.md ✅
- Research complete
- Create findings.md

### Phase 2: Build Skills (parallel)
- 2a: `ctyun-rds-ops` — SKILL.md + references/
- 2b: `ctyun-mysql-ops` — SKILL.md + references/
- 2c: `ctyun-postgresql-ops` — SKILL.md + references/
- 2d: `ctyun-mongodb-ops` — SKILL.md + references/

Each skill needs: SKILL.md + references/{rubric,prompt-templates,cli-usage,api-sdk-usage,core-concepts,integration,monitoring,troubleshooting}.md

### Phase 3: Update Charter Files
- Update AGENTS.md (Sync Matrix: 6 locations per skill)
- Update README.md (Shipped Skills table + Planned table)

### Phase 4: Verification
- markdownlint
- Link integrity check
- Line budget check

## Key Design Decisions
- `sdk-only` for all four (no CLI module exists for RDS/MongoDB)
- `ctyun-rds-ops` uses Python `requests` for REST API calls
- `ctyun-mysql-ops` uses `mysql` CLI via subprocess
- `ctyun-postgresql-ops` uses `psql` CLI via subprocess
- `ctyun-mongodb-ops` uses `mongosh` for data ops + REST for instance mgmt
- Safety gates required for all destructive ops (delete instance, DROP TABLE, DROP DATABASE, etc.)
