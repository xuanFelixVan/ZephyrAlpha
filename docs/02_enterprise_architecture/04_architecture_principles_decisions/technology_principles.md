---
module_id: VIEW-04PRINC-TECHNOLOGY
title: Architecture Principles — Technology / 架构原则：技术
doc_type: architecture_view
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-04-TECHNOLOGY-ARCH
related_rationale: R29, R30, R45, R46, R47, R48, R50, R51, R52
related_open_questions:
- OQ-067
tags:
- technology-principles
- togaf
- ta
- tech-stack
- deployment
- infrastructure
- dr
- bcp
- rto
- rpo
- capacity
- cost
- vibe-coding-2.0
- ai-infrastructure-stack
- 17-core-selections
summary: 技术架构永恒原则文档。从 target_architecture/technology_architecture.md（已删除）提取的 timeless 方法论——技术栈决策框架（ThoughtWorks Radar 四象限 + 17 项 AI 基础设施聚焦）、单进程演进式运行时拓扑、experimental vs Post-Activation 部署框架、DR/BCP RTO/RPO 分层矩阵、4 环境矩阵与晋级门禁、可观测性三支柱（Metrics/Logs/Traces + OTel）。派生数据（具体技术清单、容量数字、成本预算）不在本文档，由 technology_landscape.yaml + 自动化系统维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Technology
# 架构原则：技术（Technology Principles）

---

## §1 定位 / Position

本文档是**技术架构的永恒指导原则**，从 `target_architecture/technology_architecture.md`（已删除）提取。

**保留内容**：方法论、设计原则、不变约束——技术栈决策框架、运行时拓扑原则、DR/BCP 方法论、环境矩阵、可观测性三支柱。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 技术栈完整清单 → `architecture_model/technology/technology_landscape.yaml`（43 项 Radar）
- 17 项 AI 基础设施选型 → `architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml`
- 域资源预算数字 → depgraph（时点快照）
- LLM Token 预算 → 运营态 metrics
- 成本预算与预警阈值 → 运营态维护

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- [application_principles.md](application_principles.md)：应用架构原则
- 本文：技术架构原则（技术栈决策/运行时拓扑/DR/BCP/环境矩阵/可观测性）

---

## §2 Technology Stack Decisions / 技术栈决策框架

### 2.1 ThoughtWorks Technology Radar 四象限分类原则（永恒）

本项目技术栈采用 **ThoughtWorks Technology Radar** 四象限分类管理：

| 象限 | 含义 | 采纳策略 |
|------|------|---------|
| **Adopt** | 已经过验证，强烈推荐采用 | 主栈首选 |
| **Trial** | 值得在项目中试用 | 评估后采用 |
| **Assess** | 探索性评估，需更多信息 | 评估阶段 |
| **Hold** | 暂不采用，有特定原因 | 暂缓 |

> **注**：技术栈完整清单（43 项）见 `architecture_model/technology/technology_landscape.yaml`（真源），不在本文档硬编码。

### 2.2 Vibe Coding 2.0 AI 基础设施聚焦视图（永恒——17 项强约束）

源自 `vibe-coding-audit-merged.md` Qwen 17 项技术选型共识，是 AI 基础设施的**强约束选型**。

**权威真源**：`architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml`（17 项 AI 基础设施选型）。

**两者关系（永恒）**：

| 维度 | `vibe_coding_infrastructure_tech_stack.yaml`（AI 基础设施聚焦）| `technology_landscape.yaml`（全技术栈雷达）|
|------|----------------------------------------------------|---------------------------------------------------------|
| 覆盖范围 | 5 大核心服务的 17 项 AI 基础设施选型 | 全技术栈 43 项（含业务层数据库、调度器等）|
| 分类方式 | 按服务分组 + 升级阈值看板 + KB 决策记录对应 | ThoughtWorks Radar 四象限 |
| 约束强度 | **强约束**（experimental 必须使用首选方案）| 推荐性（部分项目仍 pending）|
| 关系 | 前者是后者的**聚焦子集** | — |

**17 项核心选型按服务分组（永恒框架）**：

| 服务 | 项数 | 代表选型 |
|------|:----:|---------|
| Context Engine | 3 | NetworkX / Qwen2.5-3B ONNX / 规则基降级 |
| Vector Memory | 3 | ChromaDB / BGE-M3 ONNX / 递归字符分块 |
| Agent Orchestrator | 5 | SQLite + asyncio.Queue / 状态机 Enum / filelock |
| Agent Sandbox | 1 | Windows ACL + 只读挂载 |
| Feedback Loop | 2 | SQLite 时间序列 / EMA 异常检测 |
| LLM Security Gateway | 3 | Pydantic v2 / 正则 Pattern 库 / git-secrets |

> **注**：具体版本号与升级阈值看板见 YAML 真源，不在本文档硬编码。

### 2.3 决策状态分类（永恒）

| 状态 | 含义 |
|------|------|
| ✅ Decided | 已决定，必须采纳 |
| 🟡 Pending | 待决定，有明确触发条件 |
| 🔴 Deferred | 暂缓，未来激活 |

---

## §3 Runtime Topology / 运行时拓扑原则

### 3.1 单进程演进式原则（永恒当前阶段定位）

**当前架构为单进程演进式**：所有层在同一 Python 进程内运行，通过函数调用传递契约对象。

**永恒约束**：
- 单进程内通过函数调用传递契约对象（不引入 IPC）
- 跨进程通信仅在边界处（外部 API、CI、git hook）

### 3.2 进程清单框架（永恒分类）

| 进程类型 | 运行环境 | 职责 | 启动方式 |
|---------|---------|------|---------|
| **Main Process** | Windows / Linux (Python) | 运行 53 域全链路主业务逻辑 | `python -m src.zephyr.main` |
| **Pre-commit Guard** | Git hook（本地） | 文件治理检查 | `git commit` 触发 |
| **CI Audit Process** | GitHub Actions / CI | 全仓库审计扫描 | push / PR 触发 |

### 3.3 网络边界原则（永恒）

**永恒约束**：
- 所有外部 API 调用强制 HTTPS/TLS 1.3
- API Key 本地 `.env`，不入 Git
- 当前无入站监听（Post-Activation 启用）

---

## §4 Deployment Framework / 部署框架

### 4.1 experimental vs Post-Activation 二阶段框架（永恒）

| 维度 | experimental（当前） | Post-Activation |
|------|----------------|----------------|
| 运行环境 | Windows 本地单机 | Linux 云端 / 容器化 |
| 数据存储 | PostgreSQL + TimescaleDB + DuckDB + Parquet | 云端 DB + 对象存储 |
| 可观测性 | 本地日志文件 | OTel Collector + Prometheus + Grafana |
| 调度 | 手动 / 简单 cron | Airflow / Prefect |
| CI/CD | GitHub Actions（lint/audit） | 完整 CI/CD Pipeline + 回滚 |

**激活触发**：接入真实资金 / 外部投资人 / 多账户 / SRE 抽屉激活。

### 4.2 Security & ops 域激活原则（永恒）

| 域 | 激活条件 |
|------|---------|
| `D_SECURITY` 对抗验证 | 接入真实资金或多用户后激活 |
| `D_OPS` 反馈循环 | 接入真实券商 API / 月可用性 >99.9% / 多 Agent >3 |
| `D_SECURITY_LLM` LLM防御 | LLM 调用量月均 > 1000 次后激活 |

---

## §5 DR / BCP — Disaster Recovery & Business Continuity

### 5.1 RTO / RPO 分层矩阵原则（永恒框架）

**永恒约束**：所有核心链路必须按资产级别分层定义 RTO/RPO，金融资金链路 RPO=0（零丢失）。

| 链路类型 | 资产级别 | RTO（市场时段） | RPO | 激活 Tier |
|---------|---------|----------------|-----|----------|
| 订单 + 成交回报 | 🔴 金融资金 | ≤ 5 min | **0（零丢失）** | 热备 |
| Audit Log | 🔴 合规审计 | ≤ 15 min | **0（append-only）** | 热备 |
| 业务核心（数据/信号/因子/风控）| 🟡 业务核心 | ≤ 15-30 min | ≤ 5-15 min | 温备 |
| 离线分析（归因/实验）| 🟢 离线分析 | ≤ 4 h | ≤ 1 h | 冷备 |
| 中间缓存 | 🟢 可丢弃 | — | ∞ | 无备份 |

### 5.2 三级灾备预案（永恒）

| 级别 | 机制 |
|-----|------|
| **Tier 1 热备** | 双实例 active-standby，数据实时同步 |
| **Tier 2 温备** | 数据层持续同步，计算层冷启动 |
| **Tier 3 冷备** | pg_dump / Parquet 归档 + Git |

### 5.3 量化特殊场景铁律（永恒）

**已挂单处置流程（资金安全红线）**：

故障触发 → ① 查询 broker 订单状态 → ② 对照 audit journal → ③ 分类（已成交/部分成交/仅提交/未提交）→ ④ 处置决策写入 audit journal → ⑤ T+1 对账。

**幂等 Key 是去重唯一依据**（详见 application_principles.md §5）。

**数据丢失可容忍边界（永恒）**：
- 订单/Audit Log = **0 容忍**
- 因子 Parquet = 可重算
- 中间缓存/Redis = 可完全丢失

---

## §6 Environment Matrix / 环境矩阵

### 6.1 四环境定义（永恒）

| 环境 | 目的 |
|------|------|
| **Dev** | 本地开发与单元测试 |
| **UAT** | 功能验收 + 策略逻辑验证（模拟盘）|
| **Staging** | 上线前预生产验证（镜像 Prod 数据）|
| **Prod** | 真实资金运行 |

### 6.2 环境晋级门禁（永恒铁律）

| 门禁 | 必须满足 |
|------|---------|
| **Gate 1（Dev→UAT）** | 单元测试全通过 + 回测 ≥ 1 年 + Sharpe > 0.5 |
| **Gate 2（UAT→Staging）** | UAT 模拟盘 ≥ 2 周无重大异常 + Code Review + KB 决策记录 |
| **Gate 3（Staging→Prod）** | Shadow Trading ≥ 1 周 + SLO 验证 + 书面风险确认 + Runbook |

**永恒约束**：跳过任一门禁=违反资金安全红线。

---

## §7 Observability Architecture / 可观测性架构

### 7.1 三支柱框架（永恒）

可观测性采用 **Metrics / Logs / Traces 三支柱** + OpenTelemetry 集成。

### 7.2 Logs 三级分类（永恒）

| 级别 | 日志类型 | 保留策略 |
|------|---------|---------|
| **L1 应用日志** | 业务运行事件 | 本地 30 天；Loki 90 天 |
| **L2 审计日志** | 决策与操作记录 | **不可删除（append-only，KBG-0002）**；≥ 1 年 |
| **L3 安全日志** | 认证、API Key 使用 | 本地 90 天；Prod 加密存储 |

**永恒约束**：
- 日志格式：结构化 JSON（含 `trace_id` / `span_id` / `layer` 字段）
- L2 审计日志 append-only，禁用删除

### 7.3 Traces 采样策略（永恒）

| 环境 | 采样策略 |
|------|---------|
| Dev/UAT | 100% |
| Staging | 20% + 错误 100% |
| Prod | 尾部采样 10% + 错误/慢请求 100% |

### 7.4 OTel 集成框架（永恒）

| 组件 | 用途 |
|------|------|
| `opentelemetry-sdk` (Python) | Metrics + Traces |
| OTel Collector (Agent) | 接收 + 路由 |
| Prometheus | Metrics 存储 |
| Grafana Tempo | Traces 存储 |
| Loki | Logs 聚合 |
| Grafana Dashboard | 统一看板 |

---

## §8 视图边界 / Boundaries

### 8.1 本文档覆盖

- ThoughtWorks Radar 四象限分类与 17 项 AI 基础设施聚焦视图（§2）
- 单进程演进式运行时拓扑原则（§3）
- experimental vs Post-Activation 部署框架（§4）
- DR/BCP RTO/RPO 分层矩阵与三级灾备（§5）
- 4 环境矩阵与晋级门禁（§6）
- 可观测性三支柱（§7）

### 8.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 技术栈完整清单（43 项）| `architecture_model/technology/technology_landscape.yaml` |
| 17 项 AI 基础设施选型 | `architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml` |
| 域资源预算数字 | depgraph（时点快照）|
| LLM Token 预算 | 运营态 metrics |
| 成本预算与预警阈值 | 运营态维护 |
| 伸缩触发点 | 运营态维护 |
| 第三方集成清单 | `integration_principles.md`（EI 系列）|
| 安全认证机制 | `security_principles.md` |
| 运维告警 | `operations_architecture.md`（待清理后→ops_principles.md）|

### 8.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- [application_principles.md](application_principles.md)：应用架构原则
- 本文：技术架构原则（技术栈决策/运行时拓扑/DR/BCP/环境矩阵/可观测性）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随技术栈升级、容量变化、成本预算调整的内容，均不应写入本文档——它们由各自自动化系统维护。
