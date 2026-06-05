---
name: ctyun-skills
description: 天翼云 CTyun 运维 Agent Skills 集合
license: MIT
---

> **中文版本** | **[English Version](README_EN.md)**

# Skills Farm - CTyun Skills 开发指南

本项目是**天翼云（CTyun）运维 Agent Skills 集合**，提供云产品的自动化运维、监控和管理能力。
基于标准 Markdown + [Agent Skills OpenSpec](https://agentskills.io/specification)，遵循 `ctyun`-first
with SDK fallback 策略，可被多种 AI Agent 框架接入。

## 核心价值

**Skills Farm 是一套 Meta Skill（元技能）体系**——将运维知识转化为结构化的、AI Agent 可解析、
可执行、可验证的声明式规范。

### 关键特性

| 特性 | 说明 |
|------|------|
| **占位符机制** | `{{env.*}}`（环境变量）、`{{user.*}}`（用户输入）、`{{output.*}}`（输出捕获），实现人机双通道 |
| **职责委托** | `SHOULD/SHOULD NOT Use` 定义边界，跨产品操作自动委派 |
| **ctyun-first 执行** | 优先 `ctyun` CLI，3 retry 后降级到 SDK/API；详见 [CLI-First Decision Matrix](ctyun-skill-generator/references/cli-decision-matrix.md) |
| **CLI 不满足分类** | 4-class 检测（Environment / Capability / Runtime / Business）+ **per-operation** fallback 粒度 |
| **Generator-Critic-Loop (GCL)** | 对抗式质量门：每个 skill 含 `rubric.md` + `prompt-templates.md` + trace 持久化 |
| **Token Efficiency** | 单 skill 行数预算 + 跨 skill 去重表 + "Reference, don't copy" 风格 |
| **Doc Link Integrity** | `lychee` + 占位符正则 + `## Quality Gate (GCL)` 段存在性 — 7 条 Pre-merge Gate |
| **Skill Lifecycle & Doc Sync** | Planned / Shipped / Retired 三态 + 6 项 Sync Matrix + Doc-drift 反模式 |
| **安全机制** | 凭证隔离（CLI 仅读 `~/.ctyun/config`，SDK 读 `{{env.*}}`）+ 操作安全门（删除/恢复需确认） |
| **跨平台设计** | 标准 Markdown + OpenSpec，支持 Harness / Claude Code / Cursor 等多种 Agent 框架 |

### 什么是 Meta Skill

**Meta Skill（元技能）**是"生成 Skill 的 Skill"——不是具体云产品的运维能力，而是**生产运维知识的能力**。

| 对比 | 普通 Skill | Meta Skill |
|------|-----------|------------|
| 职责 | 执行特定运维任务 | 生成 / 编排其他 Skill |
| 示例 | `ctyun-ecs-ops` 运维云主机 | `ctyun-skill-generator` 生成新 Skill |
| 输入 | 环境变量 + 用户指令 | 产品文档 URL + OpenAPI 定义 |
| 输出 | 执行结果 | 结构化的 Skill 文档 |

> 核心原则：`{{env.*}}` 标记的凭证**严禁向用户索取**，从机制上杜绝泄露。

> **一句话总结**：Skills Farm 让 AI Agent 从"能回答问题"进化到"能自主运维"——每个天翼云产品都拥有一个
> "AI 原生"的运维助手。

## 已开发 / 已规划的 Skills

| Skill 名称 | 产品 | 功能描述 | 状态 |
|------------|------|----------|------|
| [ctyun-skill-generator](ctyun-skill-generator/) | Meta Skill | 从 OpenAPI / 官方文档自动生成 `ctyun-*-ops` Skill | ✅ **已发布** |

### Planned Skills（将由 ctyun-skill-generator 依次生成）

| Skill | 产品 | GCL 等级 | max_iter | 状态 |
|-------|------|----------|----------|------|
| `ctyun-ecs-ops` | 云主机 (ECS) | required | 2 | Planned |
| `ctyun-rds-ops` | 云数据库 (RDS) | required | 2 | Planned |
| `ctyun-iam-ops` | IAM (用户/策略/密钥) | required | 2 | Planned |
| `ctyun-kms-ops` | KMS (密钥管理) | required | 2 | Planned |
| `ctyun-eip-ops` | 弹性公网 IP | required | 2 | Planned |
| `ctyun-elb-ops` | 负载均衡 (ELB) | recommended | 3 | Planned |
| `ctyun-cloudmonitor-ops` | 云监控 (告警/指标) | recommended | 3 | Planned |
| `ctyun-alert-intelligence` | 告警分析 (read-only) | optional | 5 | Planned |
| `ctyun-mysql-ops` / `ctyun-postgresql-ops` / `ctyun-mongodb-ops` | 数据库系列 | required | 2 | Planned |

> 完整 14 项 Planned 列表与 max_iter 默认值见 [`AGENTS.md` §GCL §8](AGENTS.md#8-per-skill-defaults)。

> 新 skill 落地时，**同一次 commit** 必须按 [`AGENTS.md` §Skill Lifecycle & Doc Sync Convention](AGENTS.md#skill-lifecycle--doc-sync-convention)
> 的 6 项 Sync Matrix 同步更新 AGENTS.md（Repo Layout / Cross-Skill Delegation / GCL §8 / Changelog 等）。

## 项目结构

```
ctyun-skills/
├── README.md                                       # 本文件（中文）
├── README_EN.md                                    # English version
├── AGENTS.md                                       # 仓库宪章（712 行；CLI-First Policy / Token Efficiency / Doc Integrity / GCL）
├── LICENSE                                         # MIT
├── pyproject.toml                                  # Python 项目元数据（uv 管理）
├── .env.example                                    # 凭证模板（真实 .env 已在 .gitignore）
├── docs/
│   └── GCL_RETROSPECTIVE.md                        # GCL rollout 复盘 & Phase 3 仪表盘设计契约
├── audit-results/                                  # GCL trace 持久化目录（planned）
└── ctyun-skill-generator/                          # ✅ Shipped: Meta Skill — 生成新的 ctyun-*-ops
    ├── SKILL.md
    └── references/
        ├── ctyun-skill-template.md                 #  生成器使用的目标 skill 模板
        ├── governance-and-adversarial-review.md    #  治理 + 对抗式 review 场景
        ├── prompt-templates.md                     #  GCL 的 G / C / O prompt 模板
        ├── rubric.md                               #  GCL 评分规则
        └── cli-decision-matrix.md                  #  ⭐ CLI-First 决策契约（9-item classifier + per-op fallback）
```

> 当 `ctyun-skill-generator` 生成新 skill 时，**目标布局**为 `ctyun-[product]-ops/`，含 `SKILL.md` +
> `assets/example-config.yaml` + 5 个 `references/*.md`（详见 `AGENTS.md` §Repo Layout §Planned Layout）。

## 什么是 Skill

结构化 Markdown 文档，指导 AI Agent 完成特定任务。包含：YAML frontmatter 元数据、Trigger & Scope、
占位符约定、Pre-flight → Execute → Validate → Recover 流程、Output Parsing、Failure Recovery、
Safety Gates，以及 `## Quality Gate (GCL)` 段（per-skill GCL 参数声明）。

## CTyun CLI

所有 Skill 基于天翼云官方 CLI（`ctyun`）与 API 交互。**CLI 优先**，SDK/API 仅在 CLI 不满足时回退。

### 安装

**方式一：`uv`（推荐，幂等且可重现）**

使用 [uv](https://docs.astral.sh/uv/) 进行 Python 环境管理：

```bash
# 安装 uv（一次性）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建环境并安装（幂等，可重复执行）
uv venv --python 3.10
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install ctyun-cli ctyun-sdk
```

**方式二：pip**

```bash
pip install ctyun-cli ctyun-sdk
```

**方式三：直接使用项目 pyproject.toml**

```bash
uv sync
```

### 配置凭证

> **重要**：`ctyun` CLI **不读取环境变量**，仅从 `~/.ctyun/config`（INI 格式）读取。SDK 模式才读 `{{env.*}}`。

#### 方式 1：`.env` 文件（本地开发推荐，SDK 模式）

```bash
cp .env.example .env
# 编辑填入真实凭证
```

```ini
# .env 文件内容示例（SDK 模式使用）
CTYUN_ACCESS_KEY=your_access_key_here
CTYUN_SECRET_KEY=your_secret_key_here
CTYUN_REGION=cn-gz
```

#### 方式 2：CLI 配置文件（CLI 模式）

```bash
# 交互式配置
ctyun config init

# 或手动
export HOME=/tmp/ctyun-home    # 沙箱可写 HOME
mkdir -p /tmp/ctyun-home/.ctyun
cat > /tmp/ctyun-home/.ctyun/config << 'EOF'
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region_id = cn-gz
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
EOF
printf "%s" "default" > /tmp/ctyun-home/.ctyun/current
```

> ⚠️ **CLI 凭证配置文件不接受 `{{env.*}}` 占位符**——必须先用 `envsubst` / `sed` 替换为字面值再写入。

> ⚠️ **安全警告**：**绝不**在日志、控制台输出或调试信息中打印 `CTYUN_SECRET_KEY` 的值。验证凭证时
> 仅检查存在性（如 `test -n "$CTYUN_SECRET_KEY"`），记录状态请使用脱敏占位符（如
> `CTYUN_SECRET_KEY=<masked>`）。

#### 方式 3：Shell 环境变量（**仅 SDK 模式有效**）

```bash
export CTYUN_ACCESS_KEY="your_access_key"
export CTYUN_SECRET_KEY="your_secret_key"
export CTYUN_REGION="cn-gz"
```

> **凭证优先级**（在 SDK 模式）：Shell env > `.env` > 默认值。CLI 模式仅看 `~/.ctyun/config`。

## ctyun-first with SDK Fallback

每个 `ctyun-*-ops` skill **必须**遵循以下执行策略：

```
ctyun CLI exists? ── yes ──► try CLI (3 retries, exp backoff) ──► success? continue
                                                              └─ 3 fails ──► SDK fallback (per-op)
   └─ no / unknown ──► mark `cli_applicability: sdk-only` for this op; use SDK/API
```

**完整决策表**（9-item "CLI 不满足" classifier、4-class fallback scope、session-level policy、5 条反模式）
见 [`ctyun-skill-generator/references/cli-decision-matrix.md`](ctyun-skill-generator/references/cli-decision-matrix.md)。

策略层概览见 [`AGENTS.md` §CLI-First Policy (Repository-Wide)](AGENTS.md#cli-first-policy-repository-wide)。

> 仓库级底线：**If a `ctyun <product> <op>` subcommand exists, use it. SDK/API is a contingency,
> not a parallel first choice.**

### 关键 ctyun CLI 怪癖

| 怪癖 | 错 | 对 |
|------|-----|-----|
| `--output json` 位置 | `ctyun ecs list --output json` | `ctyun --output json ecs list` |
| `--no-interactive` 标志 | `ctyun --no-interactive ecs delete` | **省略**（不支持） |
| 凭证源 | `export CTYUN_ACCESS_KEY=...`（CLI 忽略） | 写入 `~/.ctyun/config` INI 文件 |
| `~/.ctyun/current` | `echo "default" > file`（带换行） | `printf "%s" "default" > file`（无尾换行） |

## 开发新 Skill

### 1. 引用生成器

将以下文件作为输入上下文：

```
@ctyun-skill-generator/SKILL.md
@ctyun-skill-generator/references/ctyun-skill-template.md
@ctyun-skill-generator/references/cli-decision-matrix.md
@ctyun-skill-generator/references/rubric.md
```

### 2. 提供提示词

> "生成天翼云 [产品] 的 Skill，名称 `ctyun-xxx-ops`，核心功能 [描述]。OpenAPI 文档：[URL]"

### 3. 生成的结构

```
ctyun-[product]-ops/
├── SKILL.md                              # 必含 ## Quality Gate (GCL) 段
├── assets/example-config.yaml
└── references/
    ├── cli-usage.md
    ├── core-concepts.md
    ├── integration.md
    ├── monitoring.md
    └── troubleshooting.md
```

### 4. Quality Bar (P0 必须)

- **Trigger & Scope** with SHOULD-use / SHOULD-NOT-use + delegation
- **Variables**: `{{env.*}}` / `{{user.*}}` / `{{output.*}}`；不含真实 secret
- **Flows**: Pre-flight → Execute → Validate → Recover；**每个 op 同时文档化 ctyun + SDK 路径**
- **CLI fidelity**: 子命令/flag 与官方 ctyun CLI 文档一致；JSON 路径**真实 `--output json` 运行验证过**
- **Safety gates** for destructive ops（ctyun 路径和 SDK 路径都要）
- **CLI-First Decision Matrix 引用**: 在 `## Quality Gate (GCL)` 段声明 `fallback_decision_table: references/cli-decision-matrix.md`
- **Token Efficiency**: SKILL.md ≤ 600 行；references 单文件 ≤ 800 行
- **Doc Integrity**: 所有相对链接 resolve 存在；`{{var.*}}` 符合命名规范

## 验证

```bash
# 1. markdownlint
npm install -g markdownlint-cli
markdownlint ctyun-[product]-ops/SKILL.md

# 2. 链接完整性
npm install -g lychee
lychee --offline --include-fragments '**/*.md'

# 3. Python 环境
uv venv --python 3.10
source .venv/bin/activate
uv pip install ctyun-cli ctyun-sdk
ctyun --version
```

## 常见问题

| Q | A |
|---|---|
| Skill 和 MCP Server 关系？ | Skill 是文档，MCP 是执行服务 |
| 一个 Skill 覆盖多产品？ | 建议单一职责，通过 Reference 互相引用 |
| ctyun-first 是什么？ | 默认走 `ctyun` CLI；只在"CLI 不满足"时降级到 SDK/API。详见 [CLI-First Decision Matrix](ctyun-skill-generator/references/cli-decision-matrix.md) |
| GCL 是什么？ | Generator-Critic-Loop：生成-批评对抗循环质量门，每个 skill 都有 rubric + Critic。详见 [AGENTS.md §GCL](AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate) |
| 怎么知道"CLI 不满足"？ | 4-class 分类：Environment（修复重试）/ Capability（标 sdk-only）/ Runtime（per-op fallback）/ Business（永不 fallback）。详见 [Decision Matrix §2](ctyun-skill-generator/references/cli-decision-matrix.md#2-what-counts-as-cli-不满足-cli-unsatisfied) |

## 参考资源

- [仓库宪章 (AGENTS.md)](AGENTS.md)
- [Skill 生成器 (ctyun-skill-generator)](ctyun-skill-generator/SKILL.md)
- [Skill 模板](ctyun-skill-generator/references/ctyun-skill-template.md)
- [CLI-First Decision Matrix](ctyun-skill-generator/references/cli-decision-matrix.md)
- [GCL Rubric](ctyun-skill-generator/references/rubric.md)
- [GCL Prompt Templates](ctyun-skill-generator/references/prompt-templates.md)
- [GCL Retrospective & Dashboard Design](docs/GCL_RETROSPECTIVE.md)
- [CTyun 官方文档](https://www.ctyun.cn/document/)
- [Agent Skills Open Specification](https://agentskills.io/specification)

## 贡献

1. Fork
2. 按 `AGENTS.md` §Repo Layout §Planned Layout 创建 Skill 目录
3. 生成后**同一次 commit** 按 [AGENTS.md §Skill Lifecycle & Doc Sync Convention](AGENTS.md#skill-lifecycle--doc-sync-convention) 同步更新 AGENTS.md
4. 提交 PR（遵循 Conventional Commits）

---

参考 [ctyun-skill-generator](ctyun-skill-generator/) 作为唯一已发布的实现示例。
