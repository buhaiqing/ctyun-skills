# Research Findings — Database Skills

## CLI Support Check
- **ctyun-cli v1.20.2** confirmed: NO `rds` or `mongodb` subcommands exist
- Visible modules: aiserver, aone, audit, billing, cce, cda, cloudpc, configure, css, ebs, ecs, elb, emr, iam, ims, kafka, lts, monitor, network, oceanfs, redis, security, sfs, storage, test, vpc
- → All four DB skills: `cli_applicability: sdk-only`

## SDK Support Check
- `ctyun-sdk` package does NOT exist on PyPI (verified: `pip install ctyun-sdk` → "no matching distribution")
- Shipped skills reference `ctyun_sdk` but that module is NOT importable
- The `ctyun-cli` package has internal `client.py` per product module (not a public SDK)
- → Skills must use product-specific tools (REST API, DB CLI clients)

## Skill Architecture Decisions

| Skill | Method | Pattern |
|---|---|---|
| `ctyun-rds-ops` | Python `requests` → CTyun OpenAPI REST | sdk-only |
| `ctyun-mysql-ops` | `mysql` CLI client via subprocess | sdk-only |
| `ctyun-postgresql-ops` | `psql` CLI client via subprocess | sdk-only |
| `ctyun-mongodb-ops` | `mongosh` CLI + REST API | sdk-only |

## Reference Patterns (from shipped skills)
- OOS pattern: `sdk-only` — SKILL.md explains no CLI, uses product SDK
- EIP pattern: `dual-path` — CLI primary + SDK fallback
- All shipped skills have 8 reference files: rubric.md, prompt-templates.md, cli-usage.md, api-sdk-usage.md, core-concepts.md, integration.md, monitoring.md, troubleshooting.md

## GCL Parameters (from AGENTS.md §8)
- All four skills: GCL `required`, `max_iterations=2`
- Safety confirm required for destructive ops (delete, DROP, TRUNCATE, dropDatabase)

## CTyun RDS API
- Product: 关系型数据库 (CT-RDS) — supports MySQL, PostgreSQL, SQL Server
- No public OpenAPI spec found
- Common operations: Create instance, describe instances, delete instance, resize, backup, restore, parameter groups

## CTyun MongoDB API
- Product: 文档数据库服务 (Document Database Service)
- Known operations from esurfingcloud.com docs: Create instance, describe instances, delete instance, backup
