---
module_id: VIEW-04-TECHNOLOGY-ARCH
title: Target Architecture — Technology Architecture / 目标架构：技术架构 （被恢复）
doc_type: architecture_view
status: Active
version: 2.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-21
superseded_by: null
supersedes: null
related_rationale: R29, R30, R45, R46, R47, R48, R50, R51, R52
related_open_questions:
- OQ-067
tags:
- technology-architecture
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
summary: TOGAF Technology Architecture 视图（v2.0.0 重组织版）。技术栈决策、运行时拓扑、 第三方集成、部署运维、DR/BCP、环境矩阵、可观测性、容量模型与成本架构。
date: '2026-04-22'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Technology Architecture answers:

技术架构视图回答：

- **What** specific technology stack underpins everything? (Tech stack decisions / 技术栈决策)
- **How** is the runtime structured? (Deployment topology / 运行时拓扑)
- **How** is the system deployed and operated? (Deployment and ops / 部署与运维)
- **Which** third parties are integrated? (External integrations / 第三方集成)
- **What** is deferred? (Deferred technology decisions / 暂未决定项)

This view is **driven by** the Application Architecture (application characteristics determine technology choices). Technology cost limits also **reverse-constrain** AA → IA → BA ambition.

本视图由应用架构**驱动**（应用特性决定技术选型）。TA 的成本限制也**反向约束** AA → IA → BA 的野心。

---

## 2. Technology stack decisions / 技术栈决策

### 2.1 Already decided / 已确定的技术决策

> **📋 技术栈完整清单**：见 [`architecture_model/technology/technology_landscape.yaml`](architecture_model/technology/technology_landscape.yaml)，采用 ThoughtWorks Technology Radar 四象限分类（adopt/trial/assess/hold/build），包含 43 个技术项的版本、用途、决策状态及 KB 决策记录 引用。

### 2.1B Vibe Coding 2.0 AI 基础设施技术选型（17 项聚焦视图）

> 新增于 v2.1.0（2026-04-24）。源自 `vibe-coding-audit-merged.md` Qwen 17 项技术选型共识，是 AI 基础设施的**强约束选型**。

**权威真源**：[`architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml`](architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml)（17 项 AI 基础设施选型） + [`architecture_model/technology/technology_landscape.yaml`](architecture_model/technology/technology_landscape.yaml)（43 项全技术栈雷达）

**两者关系**：

| 维度 | `vibe_coding_infrastructure_tech_stack.yaml`（AI 基础设施聚焦）| `technology_landscape.yaml`（全技术栈雷达）|
|------|----------------------------------------------------|---------------------------------------------------------|
| 覆盖范围 | 6 大核心服务的 17 项 AI 基础设施选型 | 全技术栈 43 项（含业务层数据库、调度器等）|
| 分类方式 | 按服务分组 + 升级阈值看板 + KB 决策记录 对应 | ThoughtWorks Radar 四象限（adopt/trial/assess/hold）|
| 约束强度 | **强约束**（experimental 必须使用首选方案）| 推荐性（部分项目仍 pending）|
| 消费方 | KBG-0015 ~ KBG-0020 + 6 份接口规范 | 整体架构规划 + CI 审计 |
| 关系 | 前者是后者的**聚焦子集**（特别关注 AI 基础设施部分）| — |

**17 项核心选型按服务分组**：

| 服务 | 项数 | 代表选型 |
|------|:----:|---------|
| Context Engine | 3 | NetworkX 3.2 / Qwen2.5-3B ONNX / 规则基降级 |
| Vector Memory | 3 | ChromaDB 0.6 / BGE-M3 ONNX / 递归字符分块 |
| Agent Orchestrator | 5 | SQLite + asyncio.Queue / 状态机 Enum / filelock |
| Agent Sandbox | 1 | Windows ACL + 只读挂载 |
| Feedback Loop | 2 | SQLite 时间序列 / EMA 异常检测 |
| LLM Security Gateway | 3 | Pydantic v2 / 正则 Pattern 库 / git-secrets |

**升级阈值看板**：新 landscape 的 `upgrade_watchboard` 段定义了 8 项关键升级触发条件（如 ChromaDB > 500MB、并发任务 > 20、红队绕过率 > 5%），由 Feedback Loop Engine 自动上报。

**对应 KB 决策记录**：

- KBG-0015 Context Engine 架构
- KBG-0016 Vector Memory 技术栈
- KBG-0017 Agent Orchestrator 任务队列与状态机
- KBG-0018 Agent Sandbox 实现选择
- KBG-0019 Feedback Loop Engine 时序存储与异常检测
- KBG-0020 LLM Security Gateway 设计

### 2.2 Decided technology decisions / 已决定的技术决策

| Technology question / 技术问题 | Decision / 决策结果 | Status / 状态 |
|-------------------------------|--------------------|--------------|
| Q5-1: Data storage | **PostgreSQL + TimescaleDB** (experimental primary: time-series + relational); **DuckDB** (analytics / ad-hoc queries); Parquet (cold archive) | ✅ Decided |

### 2.3 Pending technology decisions / 待决定的技术决策

| Technology question / 技术问题 | Impact / 影响 | Priority / 优先级 |
|-------------------------------|--------------|-----------------|
| Q5-2: Scheduler? (Airflow / Prefect / Dagster / Cron?) | Memory Pipeline and async pipelines | Medium |
| Q5-3: ML framework? (PyTorch / scikit-learn / JAX?) | D_ML_TRAIN 训练域技术路径 | Medium |
| Q5-4: LLM integration? (Native API / LiteLLM / OpenRouter?) | D_FRONTEND 人机接口 | Low — deferred (OQ-011) |
| Q5-5: Deployment mode? (Local / Cloud / Hybrid? Containerized?) | SRE drawer activation depth | Low — deferred |

---

## 3. Runtime topology / 运行时拓扑

> 当前架构为**单进程演进式**，所有层在同一 Python 进程内运行，通过函数调用传递契约对象。

### 3.1 Process inventory / 进程清单（单进程）

| 进程 | 运行环境 | 职责 | 启动方式 |
|------|---------|------|---------|
| **ZephyrAlpha Main Process** | Windows / Linux (Python) | 运行 52 域全链路主业务逻辑（域分类唯一，14 层降级为域属性，见 §2.1 裁定） | `python -m src.zephyr.main` |
| **Pre-commit Guard** | Git hook（本地） | 文件治理检查（编码 / frontmatter / 命名） | `git commit` 触发 |
| **CI Audit Process** | GitHub Actions / CI | 全仓库审计扫描 | push / PR 触发 |

### 3.2 Runtime topology diagram / 运行时拓扑图

> **📊 运行时拓扑图**：见 [`diagrams/runtime_topology.mmd`](diagrams/runtime_topology.mmd)

### 3.3 Network boundary / 网络边界

| 边界 | 方向 | 协议 | 安全考量 |
|------|------|------|---------|
| Host → Market Data Provider | 出站 | HTTPS REST / WSS | API Key（本地 `.env`，不入 Git） |
| Host → Broker API | 出站 | HTTPS REST / TCP FIX | API Key + IP 白名单 |
| Host → LLM Providers | 出站 | HTTPS REST | API Key（本地 `.env`） |
| Host → Feishu Webhook | 出站 | HTTPS REST | Webhook Secret |
| Inbound（无） | — | — | 当前无入站监听 |

---

## 4. Cross-domain core data flow / 跨域核心数据流

```
D_MKT_DATA 行情数据 → D_FACTOR 因子 → D_SIGLEGACY 信号 → D_RISK 风控 → D_PF_CORE 组合构建 → D_EX_CORE 执行核心 → D_TRADING 交易运营
```

横向治理贯穿：`D_GOVERNANCE 治理` + `D_RISK 风控` + `D_FRONTEND 人机接口`

> 细颗粒度数据契约 → `application_architecture.md §7` + `architecture_model/contracts/cross_layer_contracts.yaml`
> 域分类唯一（§2.1 裁定），14 层（L00-L13）降级为域的 `layer_id` 属性，不再作为并行分类体系。

---

## 5. Third-party integrations / 第三方集成

| 契约 ID | 集成点 | 接入层 | 协议 | 状态 | 关键约束 |
|---------|--------|-------|------|------|---------|
| EXT-001 | **Broker API** | D_EX_CORE `adapters/` | REST / FIX 4.2+ | planned | 须实现 `BrokerInterface`；发单前必过 `pre_trade/` |
| EXT-002 | **Market Data** | D_MKT_DATA `connectors/` | REST / WS | planned | 须经 `quality/` 质量门禁 |
| EXT-003 | **LLM Providers** | D_FRONTEND | REST (OpenAI-compatible) | in use | D_FACTOR~D_TRADING 禁止直接调用；支持降级 |
| EXT-004 | **Feishu** | D_FRONTEND `notifications/` | REST Webhook | partial | 非关键路径；失败重试 3 次 |

**候选 Broker**：SimulationAdapter (P0) → Interactive Brokers (P1) → Futu (P1) → Longport (P2)
**候选数据源**：AKShare (P0, 免费) → Tushare (P1) → Wind (P2) → 实时 Tick (P2)
**LLM 降级顺序**：Opus → Sonnet → Haiku/Kimi → Qwen-local

---

## 6. Deployment and operations / 部署与运维

### 6.1 当前阶段拓扑：单机本地

> **📊 experimental 部署拓扑图**：见 [`diagrams/deployment_experimental.mmd`](diagrams/deployment_experimental.mmd)

### 6.2 Post-Activation 拓扑概要

> 激活触发：接入真实资金 / 外部投资人 / 多账户 / SRE 抽屉激活。

| 维度 | experimental（当前） | Post-Activation |
|------|----------------|----------------|
| 运行环境 | Windows 本地单机 | Linux 云端 / 容器化（Q5-5） |
| 数据存储 | PostgreSQL + TimescaleDB (primary) + DuckDB (analytics) + Parquet (archive) | 云端 DB + 对象存储 |
| 可观测性 | 本地日志文件 | OTel Collector + Prometheus + Grafana |
| 调度 | 手动 / 简单 cron | Airflow / Prefect（Q5-2） |
| CI/CD | GitHub Actions（lint/audit） | 完整 CI/CD Pipeline + 回滚 |

### 6.3 Security & ops 抽屉状态

| 抽屉 | 状态 | 激活条件 |
|------|------|---------|
| `06_security_and_identity` | deferred | 接入真实资金或多用户后激活 |
| `07_sre_and_platform_ops` | **planned** | 接入真实券商 API / 月可用性 >99.9% / 多 Agent >3 |

---

## 7. Deferred technology decisions / 暂未决定项清单

| Item | Reason for deferral | Trigger to revisit |
|------|--------------------|--------------------|
| LLM Gateway | 开发成本远超收益 | 月均调用量 > 1000 次 |
| Containerization | 单人开发，暂无部署复杂度 | 首次对外部署 |
| Message bus | 当前无异步通信需求 | 需要多个并发服务 |
| Compliance tech stack | 当前仅个人使用 | 外部投资人或受监管基金 |

---

## 8. DR / BCP — Disaster Recovery & Business Continuity / 灾备与业务连续性

### 8.1 RTO / RPO 核心链路分层矩阵

| 链路 | 资产级别 | RTO（市场时段） | RTO（非市场） | RPO | 激活 Tier |
|-----|---------|----------------|-------------|-----|----------|
| **D_EX_CORE 订单 + 成交回报** | 🔴 金融资金 | ≤ 5 min | ≤ 24 h | **0（零丢失）** | 热备 |
| **D_GOV_AUDIT Audit Log** | 🔴 合规审计 | ≤ 15 min | ≤ 24 h | **0（append-only）** | 热备 |
| **D_MKT_DATA 数据源 + D_PF_CORE 信号** | 🟡 业务核心 | ≤ 15 min | ≤ 4 h | ≤ 5 min | 温备 |
| **D_FACTOR 因子 + D_RISK 风控** | 🟡 业务核心 | ≤ 30 min | ≤ 4 h | ≤ 15 min（可重算） | 温备 |
| **D_TRADING 归因 + D_INTELLIGENCE 实验** | 🟢 离线分析 | ≤ 4 h | ≤ 48 h | ≤ 1 h | 冷备 |
| **D_OPS Telemetry** | 🟢 辅助 | ≤ 4 h | ≤ 24 h | ≤ 30 min | 冷备 |
| **中间缓存** | 🟢 可丢弃 | — | — | ∞ | 无备份 |

### 8.2 三级灾备预案

| 级别 | 适用链路 | 机制 | 当前阶段成本 |
|-----|---------|------|-------------|
| **Tier 1 热备** | D_EX_CORE 订单 + D_GOV_AUDIT Audit | 双实例 active-standby，数据实时同步 | Post-Activation 启用 |
| **Tier 2 温备** | D_MKT_DATA~D_PF_CORE 业务核心 | 数据层持续同步，计算层冷启动 | 文件级同步成本极低 |
| **Tier 3 冷备** | D_TRADING/D_OPS/D_INTELLIGENCE 离线 | pg_dump / Parquet 归档 + Git | 每日快照 |

### 8.3 量化特殊场景

**已挂单处置流程（资金安全红线）**：故障触发 → ① 查询 broker 订单状态 → ② 对照 audit journal → ③ 分类（已成交/部分成交/仅提交/未提交）→ ④ 处置决策写入 audit journal → ⑤ T+1 对账。幂等 Key（03-AA §9）是去重唯一依据。

**数据丢失可容忍边界**：订单/Audit Log = 0 容忍；因子 Parquet = 可重算；中间缓存/Redis = 可完全丢失。

---

## 9. Environment Matrix / 环境矩阵

### 9.1 环境定义

| 环境 | 目的 | 当前状态 |
|------|------|---------|
| **Dev** | 本地开发与单元测试 | ✅ 当前默认 |
| **UAT** | 功能验收 + 策略逻辑验证（模拟盘） | planned |
| **Staging** | 上线前预生产验证（镜像 Prod 数据） | planned |
| **Prod** | 真实资金运行 | planned |

### 9.2 4 环境 × 6 维度矩阵

| 维度 | **Dev** | **UAT** | **Staging** | **Prod** |
|------|---------|---------|-------------|----------|
| **数据源** | 模拟/AKShare 历史 | 模拟+部分真实 | 真实行情（延迟 15min） | 真实实时行情 |
| **LLM** | Cursor IDE 内置 | IDE + 少量 Runtime API | Runtime API 完整配置 | Runtime API + 降级策略 |
| **资金** | 无（SimulationAdapter） | 无（纸盘交易） | 极小仓位 / Shadow | 真实资金（个人） |
| **监控** | 本地日志 | 结构化日志 + 基础告警 | 完整 OTel + Grafana | 全量 OTel + 实时告警 |
| **审批** | 无 | Architect Review | KB 决策记录 + 回测验证 | 双重确认 + 回滚计划 |
| **回退** | `git checkout` | 重载上一版本 | 快照恢复 | Emergency Stop → 清仓 → 版本回滚 |

### 9.3 环境晋级门禁

| 门禁 | 必须满足 |
|------|---------|
| **Gate 1（Dev→UAT）** | 单元测试全通过 + 回测 ≥ 1 年 + Sharpe > 0.5 |
| **Gate 2（UAT→Staging）** | UAT 模拟盘 ≥ 2 周无重大异常 + Code Review + KB 决策记录 |
| **Gate 3（Staging→Prod）** | Shadow Trading ≥ 1 周 + SLO 验证 + 书面风险确认 + Runbook |

---

## 10. Observability Architecture / 可观测性架构

> 三支柱（Metrics / Logs / Traces）+ OTel 集成。

### 10.1 Metrics / 指标

**业务指标**：

| Metric Name | 说明 | SLO 关联 |
|-------------|------|---------|
| `zephyr_orders_total` | 订单提交总数 | SLO-3 |
| `zephyr_order_fill_rate` | 成交率 | SLO-3 |
| `zephyr_pnl_daily` | 日 PnL | — |
| `zephyr_backtest_duration_seconds` | 回测耗时 | SLO-4 |
| `zephyr_factor_refresh_lag_seconds` | 因子刷新滞后 | SLO-5 |

**技术指标**：

| Metric Name | 说明 | 告警阈值 |
|-------------|------|---------|
| `zephyr_request_duration_seconds` | API 调用延迟 | p99 > 5s |
| `zephyr_error_rate` | 错误率（分 layer） | > 1% |
| `zephyr_llm_tokens_total` | LLM Token 消耗 | 月超阈值 |
| `zephyr_data_freshness_lag_seconds` | 数据新鲜度 | SLO-1 p99 ≤180s |

**基础设施指标**：`process_cpu_seconds_total`（>80% 5min 告警）、`process_resident_memory_bytes`（>8GB）、`disk_io_time_seconds_total`（写延迟 >100ms）

### 10.2 Logs / 日志

| 级别 | 日志类型 | 保留策略 |
|------|---------|---------|
| **L1 应用日志** | 业务运行事件 | 本地 30 天；Loki 90 天 |
| **L2 审计日志** | 决策与操作记录 | **不可删除（append-only，KBG-0002）**；≥ 1 年 |
| **L3 安全日志** | 认证、API Key 使用 | 本地 90 天；Prod 加密存储 |

日志格式：结构化 JSON（含 `trace_id` / `span_id` / `layer` 字段），便于 OTel Loki 采集。

### 10.3 Traces / 分布式追踪

端到端链路：D_FACTOR → D_SIGLEGACY → D_RISK → D_PF_CORE → D_EX_CORE → [Broker API] → D_TRADING

**采样策略**：Dev/UAT 100% | Staging 20% + 错误 100% | Prod 尾部采样 10% + 错误/慢请求 100%

### 10.4 OTel Integration 概要

| 组件 | 用途 | 后端 |
|------|------|------|
| `opentelemetry-sdk` (Python) | Metrics + Traces | OTLP gRPC → Collector |
| OTel Collector (Agent) | 接收 + 路由 | 本地进程/ 独立 Gateway（Post-Activation） |
| Prometheus | Metrics 存储 | `:9090` |
| Grafana Tempo | Traces 存储 | `:3200` |
| Loki | Logs 聚合 | `:3100` |
| Grafana Dashboard | 统一看板 | `:3000` |

---

## 11. Capacity Model / 容量模型

### 11.1 按域资源预算（experimental 单机）

> 域分类唯一（§2.1 裁定），14 层降级为域属性。容量按域统计，数据源 depgraph。

| 域 | CPU (core·h/日) | Memory 峰值 (GB) | Storage 年增 (GB) | IOPS 峰值 |
|----|:-----:|:------:|:------:|:----:|
| D_MKT_DATA 行情数据 | 2 | 1.5 | 20 | 300 |
| D_INFRA_RUNTIME 基础设施 | 0.5 | 0.5 | 1 | 50 |
| D_FACTOR 因子 | 6 | 3 | 15 | 500 |
| D_SIGLEGACY 信号 | 3 | 1 | 5 | 100 |
| D_RISK 风控 | 1 | 0.5 | 2 | 150 |
| D_PF_CORE 组合核心 | 4 | 2 | 3 | 80 |
| D_EX_CORE 执行核心 | 2 | 0.8 | 8 | 200 |
| D_TRADING 交易运营 | 2 | 1 | 5 | 60 |
| D_FRONTEND 人机接口 | 1 | 0.5 | 1 | 30 |
| D_SIMULATION 仿真 | 8 | 4 | 30 | 400 |
| D_COMPLIANCE 合规 | 0.5 | 0.3 | 1 | 40 |
| D_ML_TRAIN 训练 | 3 | 4 | 10 | 200 |
| D_OPS 遥测 | 1 | 0.8 | 20 | 150 |
| D_INTELLIGENCE 实验 | 2 | 1.5 | 8 | 100 |
| D_GOV_AUDIT Audit Log | 0.3 | 0.2 | 25 | 50 |
| **合计峰值** | **~20-25** | **~12 / ~24 含 OS** | **~155** | **~1500** |

**experimental 单机建议**：16-core / 32 GB / 500 GB SSD。GPU 当前不需要，Post-Activation 触发时 1× RTX 4090 class 足够。

### 11.2 LLM Token 预算

| 类型 | 月预算（$） | 监控指标 |
|------|-----------|---------|
| Cursor IDE 内置 | $20-40（订阅固定） | Cursor 用量面板 |
| Runtime API（当前） | ~$5 | `zephyr_llm_tokens_total` |
| Runtime API（AI Operator 激活后） | ~$100-200 | 同上 |
| 便宜模型（Kimi/DeepSeek） | ~$20-50 | 同上 |
| **月度总上限** | **~$200** | Grafana 月报警板 |

### 11.3 伸缩触发点

| 触发条件 | 响应动作 |
|---------|---------|
| CPU 月均峰值 >60% | 单机升级 16→32 core |
| Memory >70% 持续 3 日 | 升级 32→64 GB |
| Storage >70% | 升级 SSD + 归档冷存 |
| Backtest TAT p95 >30min 连续 7 日 | 启用 D_SIMULATION 并行跑批 |
| LLM Token 月成本 >$200 | 触发降级顺序 |
| 订单 QPS >5（Post-Activation） | 拆分 broker-specific worker |

---

## 12. Cost Architecture / 成本架构

> **experimental 月度总预算目标 ≤ ¥3000（~$420）**。Post-Activation 接入真实资金前需重建预算。

### 12.1 三分类成本模型

| 类别 | experimental 月度估算 | 主要项目 |
|-----|-----------------|---------|
| **基础设施** | ~¥300 / $45 | 本地电费 + 外网带宽 + 备份存储 |
| **LLM & AI 服务** | ~¥1500 / $200 | Cursor 订阅 + Runtime API + 便宜模型 |
| **数据订阅** | ~¥2000 / $280 | iFinD（唯一真合同 SLA） |
| **合计** | **~¥3800 / $525** | — |

### 12.2 成本预警机制

| 阈值 | 触发动作 |
|-----|---------|
| **月度软阈值 ¥3000** | 日报 Feishu 推送成本曲线 |
| **预警阈值 ¥3500**（116%） | Feishu 告警 + 自动启用降级模式 |
| **强制阈值 ¥4500**（150%） | 🔴 人工介入 + 暂停非关键任务 |
| **单日峰值 >¥500** | 即时 Feishu 告警 |

### 12.3 成本优化策略

| 策略 | 预期节省 |
|-----|---------|
| LLM 分级路由（非关键用便宜模型） | 30-50% LLM 成本 |
| Cursor 抵扣最大化（"人在键盘前"=Cursor） | 80% Runtime API |
| 因子计算缓存 | 30% D_FACTOR CPU |
| 回测并行延迟到夜间 | 15% 白日 CPU 峰值 |
| LLM Prompt Token 压缩 | 20-40% input token |

### 12.4 成本重建触发

以下任一满足时，本节预算需**完全重写**：
- (T1) 接入真实券商 API 并启用真实资金
- (T2) 外部 LP 注资 ≥ $1M
- (T3) AI Operator ≥ 3 层同时激活
- (T4) 跨境数据订阅激活
- (T5) 连续 3 个月 >150% 预算且优化策略已全部启用

---

## 13. Revision history / 修订记录

| Date | Description |
|------|-------------|
| 2026-04-24 | **v2.1.0**：B-d-3 — 追加 §2.1B Vibe Coding 2.0 AI 基础设施技术选型（17 项聚焦视图）。引用 `architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml` 作为 AI 基础设施的**强约束选型**真源；说明与 `architecture_model/technology/technology_landscape.yaml`（43 项雷达）的"聚焦子集"关系。对应 KBG-0015~0020。 |
| 2026-04-21 | **v2.0.0**：Architecture-as-Code 重组织——代码示例/配置模板/Post-Activation Mermaid 图精简，视图从 1070 行压缩至 ≤600 行。 |
| 2026-04-19 | v1.3.0-v1.4.0：批次 C/D 深加工（Deployment + Environment Matrix + Observability + DR/BCP + Capacity + Cost + Runway）。 |
| 2026-04-18 | v1.1.0：填充 §3 运行时拓扑 + §5 第三方集成。 |

> 完整修订历史：`git log --oneline -- technology_architecture.md`

---

## 14. Architecture Runway / 架构预留通道

> 7 条基础设施/技术栈类 P3 预留（分布式计算、云原生迁移、边缘计算、多云部署、区块链审计、SSO、跨机构合规）。
> 完整条目索引 → `docs/08_knowledge/04_future_capabilities/p3-blueprint-index.md` [待创建]
