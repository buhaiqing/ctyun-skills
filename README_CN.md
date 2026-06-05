# CTyun Skills Farm

[![English](https://img.shields.io/badge/English-README.md-blue)](README.md)

**AI Agent 技能定义集合**（遵循 [Agent Skills OpenSpec](https://agentskills.io/specification) 的结构化 Markdown 文档），用于使 AI Agent 能够执行 **CTyun（天翼云）** 云操作。每个技能对应一个 CTyun 产品，遵循 **CLI 优先、SDK 兜底** 的执行策略，并实现了对抗性的 **生成器-评审器-循环（GCL）** 质量门禁。

> 本仓库是所有 CTyun 产品技能的 **单一事实来源**。仓库章程 [`AGENTS.md`](AGENTS.md) 定义了 CLI 优先策略、Token 效率预算、文档链接完整性、生成器-评审器-循环（GCL）以及技能生命周期与文档同步约定。

---

## 状态

| 组件 | 状态 |
|---|---|
| [`ctyun-skill-generator`](ctyun-skill-generator/) — 元技能 | **已发布**（v1.0.0） |
| [`ctyun-cloudmonitor-ops`](ctyun-cloudmonitor-ops/) — 云监控 | **已发布**（v1.0.0） |
| [`ctyun-ecs-ops`](ctyun-ecs-ops/) — 弹性云服务器 | **已发布**（v1.0.0） |
| [`ctyun-iam-ops`](ctyun-iam-ops/) — IAM 身份与访问管理 | **已发布**（v1.0.0） |
| [`ctyun-redis-ops`](ctyun-redis-ops/) — Redis | **已发布**（v1.0.0） |
| [`ctyun-elb-ops`](ctyun-elb-ops/) — 弹性负载均衡 | **已发布**（v1.0.0） |
| [`ctyun-eip-ops`](ctyun-eip-ops/) — 弹性公网 IP | **已发布**（v1.0.0） |
| [`ctyun-cce-ops`](ctyun-cce-ops/) — 云容器引擎 | **已发布**（v1.0.0） |
| [`ctyun-kms-ops`](ctyun-kms-ops/) — 密钥管理服务 | **已发布**（v1.0.0） |
| [`ctyun-oos-ops`](ctyun-oos-ops/) — 对象存储服务 | **已发布**（v1.0.0） |
| [`ctyun-rds-ops`](ctyun-rds-ops/) — RDS 关系型数据库 | **已发布**（v1.0.0） |
| [`ctyun-mysql-ops`](ctyun-mysql-ops/) — MySQL | **已发布**（v1.0.0） |
| [`ctyun-postgresql-ops`](ctyun-postgresql-ops/) — PostgreSQL | **已发布**（v1.0.0） |
| [`ctyun-mongodb-ops`](ctyun-mongodb-ops/) — MongoDB | **已发布**（v1.0.0） |
| [`ctyun-dns-ops`](ctyun-dns-ops/) — DNS | **已发布**（v1.0.0） |
| [`ctyun-cdn-ops`](ctyun-cdn-ops/) — CDN | **已发布**（v1.0.0） |
| [`ctyun-waf-ops`](ctyun-waf-ops/) — WAF Web 应用防火墙 | **已发布**（v1.0.0） |
| [`ctyun-ssl-cert-ops`](ctyun-ssl-cert-ops/) — SSL 证书 | **已发布**（v1.0.0） |
| [`ctyun-bastion-ops`](ctyun-bastion-ops/) — 云堡垒机 | **已发布**（v1.0.0） |
| [`ctyun-cloudaudit-ops`](ctyun-cloudaudit-ops/) — 云审计 | **已发布**（v1.0.0） |
| [`ctyun-vpc-ops`](ctyun-vpc-ops/) — 虚拟私有云 | **已发布**（v1.0.0） |
| [`ctyun-alert-intelligence`](ctyun-alert-intelligence/) — 告警智能分析 | **已发布**（v1.0.0） |
| [`ctyun-audit-ops`](ctyun-audit-ops/) — 审计运维 | **已发布**（v1.0.0） |
| [`ctyun-tag-audit-ops`](ctyun-tag-audit-ops/) — 标签审计 | **已发布**（v1.0.0） |
| 其他 `ctyun-*-ops` 产品技能 | **计划中** |
| GCL 第一阶段（对已发布技能进行验证） | **已完成** |
| GCL 第二阶段（编排器：`scripts/gcl_runner.py`） | **已发布** |
| GCL 第三阶段（质量看板） | **已发布** |
| GCL 第四阶段（告警接入） | **已发布** |

---

## 已发布技能

| 技能 | 产品 | 运维操作 | GCL | 路径 |
|---|---|---|---|---|
| [ctyun-skill-generator](ctyun-skill-generator/) | 元技能 | 从 OpenAPI 文档生成新的 `ctyun-*-ops` 技能 | 可选 | `ctyun-skill-generator/` |
| [ctyun-cloudmonitor-ops](ctyun-cloudmonitor-ops/) | 云监控 | 告警规则 CRUD、指标查询、告警历史分析 | 推荐 | `ctyun-cloudmonitor-ops/` |
| [ctyun-ecs-ops](ctyun-ecs-ops/) | 弹性云服务器 | 实例生命周期（创建/启停/重启/删除）、快照、密钥对、镜像 | **必需** | `ctyun-ecs-ops/` |
| [ctyun-iam-ops](ctyun-iam-ops/) | IAM 身份与访问管理 | 用户/用户组/策略/角色/AK/企业项目/MFA 管理 | **必需** | `ctyun-iam-ops/` |
| [ctyun-redis-ops](ctyun-redis-ops/) | Redis | 实例生命周期（创建/查询/删除/清空/配置） | **必需** | `ctyun-redis-ops/` |
| [ctyun-elb-ops](ctyun-elb-ops/) | 弹性负载均衡 | 监听器/后端/证书生命周期管理 | 推荐 | `ctyun-elb-ops/` |
| [ctyun-eip-ops](ctyun-eip-ops/) | 弹性公网 IP | IP 生命周期（申请/绑定/解绑/释放） | **必需** | `ctyun-eip-ops/` |
| [ctyun-cce-ops](ctyun-cce-ops/) | 云容器引擎 | 集群/节点/任务生命周期管理 | **必需** | `ctyun-cce-ops/` |
| [ctyun-kms-ops](ctyun-kms-ops/) | 密钥管理服务 | 密钥生命周期（创建/加密/解密/计划删除） | **必需** | `ctyun-kms-ops/` |
| [ctyun-oos-ops](ctyun-oos-ops/) | 对象存储服务 | 对象存储、存储桶 CRUD、文件上传/下载 | **必需** | `ctyun-oos-ops/` |
| [ctyun-dns-ops](ctyun-dns-ops/) | DNS | 域名管理、记录集 CRUD（通过 REST API） | **必需** | `ctyun-dns-ops/` |
| [ctyun-cdn-ops](ctyun-cdn-ops/) | CDN | 加速域名生命周期、缓存配置、刷新/预热、HTTPS、ACL | **必需** | `ctyun-cdn-ops/` |
| [ctyun-waf-ops](ctyun-waf-ops/) | WAF Web 应用防火墙 | 实例/域名/规则/ACL 管理、攻击日志查询 | **必需** | `ctyun-waf-ops/` |
| [ctyun-ssl-cert-ops](ctyun-ssl-cert-ops/) | SSL 证书 | 证书生命周期（申请/上传/删除/部署/到期提醒） | **必需** | `ctyun-ssl-cert-ops/` |
| [ctyun-bastion-ops](ctyun-bastion-ops/) | 云堡垒机 | 实例/用户/主机/策略管理 | **必需** | `ctyun-bastion-ops/` |
| [ctyun-cloudaudit-ops](ctyun-cloudaudit-ops/) | 云审计 | 日志查询、导出、统计（只读） | 可选 | `ctyun-cloudaudit-ops/` |
| [ctyun-vpc-ops](ctyun-vpc-ops/) | 虚拟私有云 | VPC 生命周期（创建/查询/删除）、子网、路由表、对等连接 | **必需** | `ctyun-vpc-ops/` |
| [ctyun-alert-intelligence](ctyun-alert-intelligence/) | 告警智能分析 | 告警模式分析、噪声抑制、事件摘要 | 可选 | `ctyun-alert-intelligence/` |
| [ctyun-audit-ops](ctyun-audit-ops/) | 审计运维 | 审计日志查询、过滤、导出、合规报告 | 可选 | `ctyun-audit-ops/` |
| [ctyun-tag-audit-ops](ctyun-tag-audit-ops/) | 标签审计 | 标签合规审计、未标记资源发现、标签报告 | 可选 | `ctyun-tag-audit-ops/` |

---

## 计划中技能

`ctyun-skill-generator` 后续将生成的技能，按优先级排序：

| 技能 | 产品 | GCL | max_iter |
|---|---|---|---|
| _（当前无计划）_ |

> 完整的 12 项列表及 `max_iter` 默认值见 [`AGENTS.md` §GCL §8](AGENTS.md#8-per-skill-defaults)。

---

## 项目结构

```
ctyun-skills/
├── README.md                               # 英文版自述文档
├── README_CN.md                            # 本文件（中文版）
├── AGENTS.md                               # 仓库章程（CLI 优先、GCL、Token 效率、文档完整性）
├── LICENSE                                 # MIT
├── pyproject.toml                          # Python 项目元数据（uv 管理）
├── .env.example                            # 凭证模板（.env 已 gitignore）
├── docs/
│   └── GCL_RETROSPECTIVE.md               # GCL 上线回顾与第三阶段看板设计
├── audit-results/                          # GCL 追踪持久化存储（规划中）
├── scripts/
│   ├── preflight-check.py                  # 环境验证
│   └── check_*.py                          # 验证存根（规划中）
├── ctyun-skill-generator/                  # 已发布：元技能
│   ├── SKILL.md
│   └── references/
│       ├── ctyun-skill-template.md
│       ├── governance-and-adversarial-review.md
│       ├── prompt-templates.md
│       ├── rubric.md
│       └── cli-decision-matrix.md
├── ctyun-cloudmonitor-ops/                 # 已发布：云监控
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
├── ctyun-ecs-ops/                          # 已发布：弹性云服务器
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
├── ctyun-iam-ops/                          # 已发布：IAM 身份与访问管理
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
├── ctyun-redis-ops/                        # 已发布：Redis
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
├── ctyun-elb-ops/                          # 已发布：弹性负载均衡
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
├── ctyun-eip-ops/                          # 已发布：弹性公网 IP
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
├── ctyun-cce-ops/                          # 已发布：云容器引擎
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
├── ctyun-oos-ops/                          # 已发布：对象存储服务
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
├── ctyun-dns-ops/                          # 已发布：DNS
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
├── ctyun-cdn-ops/                          # 已发布：CDN
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
├── ctyun-waf-ops/                          # 已发布：WAF
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
├── ctyun-ssl-cert-ops/                     # 已发布：SSL 证书
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
├── ctyun-bastion-ops/                      # 已发布：云堡垒机
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
├── ctyun-cloudaudit-ops/                   # 已发布：云审计
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
├── ctyun-vpc-ops/                           # 已发布：虚拟私有云
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
├── ctyun-alert-intelligence/              # 已发布：告警智能分析
│   ├── SKILL.md
│   └── references/
├── ctyun-audit-ops/                      # 已发布：审计运维
│   ├── SKILL.md
│   └── references/
├── ctyun-tag-audit-ops/                  # 已发布：标签审计
│   ├── SKILL.md
│   └── references/
└── ctyun-kms-ops/                          # 已发布：密钥管理服务
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

## 快速开始

### 前置条件

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)（推荐使用的包管理器）
- 拥有 API 凭证的天翼云账号

### 环境配置

```bash
# 创建虚拟环境
uv venv --python 3.10
source .venv/bin/activate

# 安装 CTyun CLI 和 SDK
uv pip install ctyun-cli ctyun-sdk

# 创建符号链接（ctyun-cli 包安装 ctyun-cli 二进制文件）
ln -sf "$(which ctyun-cli)" ~/.local/bin/ctyun

# 运行前置检查
python3 scripts/preflight-check.py --verbose --fix
```

### 凭证配置

三种方式（优先级：shell 环境变量 > `.env` > `~/.ctyun/config`）：

**SDK 模式** — 从环境变量读取：
```bash
export CTYUN_ACCESS_KEY="your_access_key"
export CTYUN_SECRET_KEY="your_secret_key"
export CTYUN_REGION="cn-gz"
```

**CLI 模式** — 仅从 INI 文件读取（`~/.ctyun/config`）：
```ini
[default]
access_key = YOUR_ACCESS_KEY
secret_key = YOUR_SECRET_KEY
region_id = cn-gz
endpoint = ecs.ctyun.cn
scheme = https
timeout = 20
```

> **安全提示**：永远不要打印或记录 `CTYUN_SECRET_KEY`。仅使用 `test -n` 检查是否存在。

### CLI 常见误用（Agent 容易出错的地方）

| 规则 | 错误用法 | 正确用法 |
|---|---|---|
| `--output json` 放置位置 | `ctyun ecs list --output json` | `ctyun --output json ecs list` |
| `--no-interactive` 参数 | `ctyun --no-interactive ecs delete` | **省略** — 不支持此参数 |
| CLI 凭证配置 | `export CTYUN_ACCESS_KEY=...`（CLI 忽略环境变量） | 写入 `~/.ctyun/config` INI 文件 |
| `~/.ctyun/current` 换行符 | `echo "default" > file` | `printf "%s" "default" > file` |

---

## 核心概念

### CLI 优先，SDK 兜底

每个 `ctyun-*-ops` 技能遵循以下策略：

```
ctyun <product> <op> 是否存在？
  ├─ 是 → 尝试 CLI（3 次重试，指数退避）
  │         ├─ 成功 → 继续执行
  │         └─ 3 次失败 → SDK 兜底（按操作维度）
  └─ 否 → 标记此操作为 `cli_applicability: sdk-only`；使用 SDK
```

兜底是按 **操作维度** 而非技能维度。如果 12 个操作中有 1 个失败，仅该操作使用 SDK 兜底，其余 11 个仍使用 CLI。9 项 "CLI 不满足" 分类器（环境/能力/运行时/业务）决定了兜底范围和重试行为。

完整决策矩阵：[`ctyun-skill-generator/references/cli-decision-matrix.md`](ctyun-skill-generator/references/cli-decision-matrix.md)

### 生成器-评审器-循环（GCL）

受 GAN 启发（但不是 GAN）的对抗性质量门禁。每个技能都有一份 **评审规则（rubric）**（≥5 个维度）和一个 **评审器（Critic）**，独立对生成器输出进行评分。循环在以下任一条件满足时终止：通过（PASS）、达到最大迭代次数（MAX_ITER）或安全失败（SAFETY_FAIL）（破坏性操作未经确认时立即中止）。

每个技能包含：
- `references/rubric.md` — 评分规则
- `references/prompt-templates.md` — 生成器/评审器/编排器提示词模板

完整规范：[`AGENTS.md` §生成器-评审器-循环](AGENTS.md#generator-critic-loop-gcl--adversarial-quality-gate)

### Token 效率与去重

| 产物 | 软上限 | 硬上限 |
|---|---|---|
| `SKILL.md`（正文） | 400 行 | 600 行 |
| `references/*.md`（每个） | 300 行 | 800 行 |
| 每个技能总计 | — | 3000 行 |

公共内容（凭证加载、CLI 常见误用、安全门禁模板）只抽取一次并通过链接引用，绝不重复编写。

---

## 开发新技能

1. 加载 `ctyun-skill-generator` 及其参考资料作为输入上下文
2. 提供提示词：产品名称、OpenAPI URL、核心操作
3. 生成器生成技能目录，包含 `SKILL.md` + `references/`
4. **同一次提交**：按 6 项同步矩阵更新 `AGENTS.md`
5. 通过 7 项合并前门禁检查（markdownlint、链接完整性、产物存在性、行数预算）

完整流程见 [`AGENTS.md` §技能生命周期与文档同步约定](AGENTS.md#skill-lifecycle--doc-sync-convention)

---

## 验证

```bash
# Markdown 格式检查
npm install -g markdownlint-cli
markdownlint ctyun-*-ops/SKILL.md

# 链接完整性检查（离线，检查锚点）
npm install -g lychee
lychee --offline --include-fragments '**/*.md'

# 环境检查
python3 scripts/preflight-check.py --verbose --fix
```

---

## 路线图

| 阶段 | 目标 | 状态 |
|---|---|---|
| **第一阶段** | 在已发布技能上实现端到端 GCL（追踪 + 评审器隔离） | 进行中 |
| **第二阶段** | `scripts/gcl_runner.py` — 可复用编排器 | 计划中 |
| **第三阶段** | 基于 `gcl-trace-*.json` 的质量看板 | 计划中 |
| **第四阶段** | 评审规则通过率 → 云监控告警 | 计划中 |

---

## 参考资料

- [仓库章程（AGENTS.md）](AGENTS.md)
- [技能生成器](ctyun-skill-generator/SKILL.md)
- [云监控技能](ctyun-cloudmonitor-ops/SKILL.md)
- [ECS 技能](ctyun-ecs-ops/SKILL.md)
- [IAM 技能](ctyun-iam-ops/SKILL.md)
- [Redis 技能](ctyun-redis-ops/SKILL.md)
- [ELB 技能](ctyun-elb-ops/SKILL.md)
- [EIP 技能](ctyun-eip-ops/SKILL.md)
- [CCE 技能](ctyun-cce-ops/SKILL.md)
- [OOS 技能](ctyun-oos-ops/SKILL.md)
- [DNS 技能](ctyun-dns-ops/SKILL.md)
- [CDN 技能](ctyun-cdn-ops/SKILL.md)
- [WAF 技能](ctyun-waf-ops/SKILL.md)
- [SSL 证书技能](ctyun-ssl-cert-ops/SKILL.md)
- [云堡垒机技能](ctyun-bastion-ops/SKILL.md)
- [云审计技能](ctyun-cloudaudit-ops/SKILL.md)
- [KMS 技能](ctyun-kms-ops/SKILL.md)
- [CLI 优先决策矩阵](ctyun-skill-generator/references/cli-decision-matrix.md)
- [GCL 评审规则](ctyun-skill-generator/references/rubric.md)
- [GCL 提示词模板](ctyun-skill-generator/references/prompt-templates.md)
- [GCL 上线回顾](docs/GCL_RETROSPECTIVE.md)
- [Agent Skills OpenSpec](https://agentskills.io/specification)
- [天翼云官方文档](https://www.ctyun.cn/document/)

---

## 许可协议

MIT — 详见 [LICENSE](LICENSE)。