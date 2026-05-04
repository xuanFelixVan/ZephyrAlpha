---
module_id: MOD-INF-001
title: 容量保障体系蓝图（B3 · 2）
doc_type: blueprint
status: approved
version: 2.1.0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
ttl: permanent
construction_progress: not_started
dependencies: []
priority: P0
tags:
  - capacity-assurance
  - slo
  - ai-audit-guard
  - contractbus
  - infrastructure
  -
  - error-budget
  - token-budget
  - kill-switch
  - sandbox
  - graceful-degradation
  - otel
summary: ZephyrAlpha 容量保障体系 2 完整蓝图 v2.1.0。覆盖 SLI/SLO 注册表（含 Saturation 四黄金信号）、Error Budget 五级响应（含 Burn Rate 多窗口监控）、AI 审计守卫、容量治理闭环、ContractBus 分批迁移、SSoT 校验、多级 Token Budget、Kill Switch、Sandbox 沙箱、Graceful Degradation 降级链、Reasoning Spans 推理追踪、语义缓存、灾难恢复策略、容量预测模型、跨模块集成设计等关键能力。所有设计按 1500 模块极限容量考虑。v2.1.0 补齐 2 施工所需的所有前置设计。
---

# 容量保障体系蓝图（B3 · 2）

> **真源声明**：本蓝图是 ZephyrAlpha 容量保障体系的唯一真源。v1.0.0 由原始施工图 Wave 0 三轮审计 + Claude-Opus-4.7 终审产出。v2.0.0 对齐专业机构实践（Google SRE / OpenTelemetry）与 Vibe Coding 社区前沿。v2.1.0 补齐施工前置设计——Error Budget 三级→五级升级 + 灾难恢复策略 + 容量预测模型 + 跨模块集成设计。

---

## 1. 核心概念

容量保障体系是 ZephyrAlpha 基础设施层的核心模块，确保系统从 97 模块到 1500+ 模块的规模演进过程中**不崩、不慢、不自毁、不烧钱**。

**六大核心能力**（v2.0.0 从三大升级为六大）：

| # | 能力 | 对标 | 说明 |
|---|------|------|------|
| 1 | SSoT 校验 | — | CTR-001 自动化检测，杜绝同一概念在多个文件中重复定义 |
| 2 | 容量 SLO + Error Budget | Google SRE Workbook | ≥8 个 SLI（含 Saturation 四黄金信号）+ Error Budget 五级响应 + Burn Rate 多窗口监控 |
| 3 | AI 审计守卫 | — | 拦截 AI 越权修改 + Provenance Chain 不可篡改追踪 |
| 4 | 多级 Token Budget | AI Agent Rate Limiting 社区实践 | request / user / org / global 四级限流 + Pre-flight 预估 |
| 5 | Kill Switch + Sandbox | AI Agent Observability Best Practices | 全局一键熔断 + 高风险操作沙箱隔离 |
| 6 | Graceful Degradation | AI Agent Cost Crisis Report | 模型降级链 + 输出截断 + 语义缓存 |

---

## 2. 设计约束（回顾大盘 + 用户原意）

**Owner 指示**（形成设计约束）：
- 未来不止 1000 模块，可能 1500+，所有设计按极限容量考虑
- 现在把能改的改了，不给未来埋雷
- 为系统保留"多进程 / 分布式事件总线 / 数据库分片"的口子
- 零依赖优先：能用 Python stdlib + SQLite 完成的不引入新依赖
- 免费优先：能用 Trae CN 免费模型完成的不调付费 API

**当前规模**：97 模块设计 + 144 实现文件 | **极限容量**：500 模块（单进程），超过则启用多进程/分布式扩展

---

## 3. 边界

### 3.1 覆盖

- L0-L3 容量保障基础设施（SSoT 校验 + 容量 SLO + AI 审计守卫 + 容量治理闭环 + Error Budget + Token Budget + Kill Switch + Sandbox + Graceful Degradation）
- ContractBus 44 份文件分三批迁移到 Pydantic v2 Schema Enforcement
- OTel AI Agent 语义规范对齐（Reasoning Spans + W3C TraceContext 传播）

### 3.2 不覆盖（→ 去哪）

- L4-L8 交易业务层容量设计 → B5 任务系统
- AI 自治权限全模块定义 → `_registry/catalogs/ai-autonomy-authority-registry.md`
- 安全审计具体规则 → M5 LLM Security Gateway
- Blameless Postmortem 流程 → `docs/01_policies_and_standards/governance/ai/`（Phase 2 补充）
- Toil 量化指标 → `capacity_slo.yaml` Phase 2 补充

---

## 4. 输入 / 基于此设计

| 输入 | 来源 |
|------|------|
| Owner 容量指示 | "1500 模块极限容量"约束 |
| Wave 0 终审裁决 5 条 | Claude-Opus-4.7 终审（R-71, R-73, R-75）|
| ContractBus 现状 | 44 份文件待迁移 |
| 原始草稿 | `19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/capacity-assurance-construction-plan.md` |
| Google SRE Workbook | Error Budget 三级响应 + 四黄金信号 + Blameless Postmortem |
| OpenTelemetry 2025 Semantic Conventions | AI Agent 语义规范 + GenAI Span 定义 |
| AI Agent Rate Limiting 社区实践 | 多级 Token Budget + Pre-flight Estimation |
| AI Agent Observability Best Practices | Kill Switch + Sandbox + Reasoning Spans |
| VictoriaMetrics Vibe Coding Blog (2026-01) | Vibe Coding 工具可观测性方案 |

---

## 5. 架构决策

### 5.1 终选技术栈（v2.0.0 更新）

| # | 组件 | 终选 | 理由 | v2.0.0 变更 |
|---|------|------|------|------------|
| 1 | SLO 配置 | YAML + Pydantic v2 | 零依赖运行时校验，Schema 即文档 | — |
| 2 | 审计 Provenance 存储 | SQLite + hash 链 | 只追加 + 完整性校验，零运维 | — |
| 3 | 容量指标采样 | structlog + OpenTelemetry SDK | 业界标准，Phase 1 即接入避免 Phase 4 重构 | — |
| 4 | AI 审计守卫规则 | YAML 规则集 + Pydantic 校验 | 规则可演化，骨架 Phase 0 即上线 | — |
| 5 | 治理闭环 | 自研 EMA + 阈值 + 持续时间 | 零依赖；Phase 4 升级 InfluxDB | — |
| 6 | 类型校验 | mypy + import-linter | 本地 + CI 双保险 | — |
| 7 | 单元测试 | pytest + pytest-cov | 行业标准 | — |
| 8 | 静态扫描 | ruff + bandit | 取代 pylint，速度快 100× | — |
| 9 | 契约总线迁移 | 分三批 15+15+14 | 控制回归风险 | — |
| 10 | Error Budget 追踪 | SQLite + Pydantic v2 | 复用已有基础设施，零新依赖 | **v2.0.0 新增** |
| 11 | Token Budget | Token Bucket + 滑动窗口 | 社区标准算法，支持 burst + 平滑 | **v2.0.0 新增** |
| 12 | Kill Switch | 环境变量 + 文件信号 | 零依赖，进程内+跨进程双通道 | **v2.0.0 新增** |
| 13 | Sandbox | 子进程 + 资源限制 | Python stdlib，零新依赖 | **v2.0.0 新增** |
| 14 | Graceful Degradation | YAML 降级链 + 模型路由 | 声明式配置，AI 零推理消费 | **v2.0.0 新增** |
| 15 | OTel 语义规范 | OpenTelemetry GenAI Semantic Conventions | 2025 行业标准，避免厂商锁定 | **v2.0.0 新增** |
| 16 | 语义缓存 | ChromaDB 向量相似度 | 复用已有 VMS 基础设施 | **v2.0.0 新增** |

### 5.2 数据库 Schema

```sql
-- ai_provenance（Immutable Core，只追加 + hash 链）
CREATE TABLE ai_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL, field TEXT NOT NULL,
    old_value TEXT, new_value TEXT,
    author_agent TEXT NOT NULL, timestamp TEXT NOT NULL,
    audit_result TEXT NOT NULL, prev_hash TEXT, curr_hash TEXT NOT NULL
);

-- capacity_metrics（AI-Modifiable，7 天 TTL）
CREATE TABLE capacity_metrics (
    ts TEXT NOT NULL, sli_id TEXT NOT NULL,
    value REAL NOT NULL, governance_layer TEXT, runtime_plane TEXT
);
CREATE INDEX idx_metrics_ts ON capacity_metrics(ts);

-- error_budget（v2.0.0 新增，Human-Gated 阈值 + AI-Modifiable 消耗）
CREATE TABLE error_budget (
    slo_id TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    budget_total REAL NOT NULL,
    budget_consumed REAL NOT NULL,
    budget_remaining REAL NOT NULL,
    response_tier TEXT NOT NULL,
    last_updated TEXT NOT NULL
);
CREATE INDEX idx_eb_slo ON error_budget(slo_id);

-- token_budget_usage（v2.0.0 新增，AI-Modifiable，7 天 TTL）
CREATE TABLE token_budget_usage (
    ts TEXT NOT NULL,
    budget_level TEXT NOT NULL,
    level_id TEXT NOT NULL,
    tokens_consumed INTEGER NOT NULL,
    tokens_remaining INTEGER NOT NULL,
    model_name TEXT,
    cost_usd REAL
);
CREATE INDEX idx_tbu_ts ON token_budget_usage(ts);
```

### 5.3 ContractBus 分三批迁移

44 份 ContractBus 文件分三批迁移到 Pydantic v2 Schema Enforcement：

| 批次 | 文件数 | 触发条件 | 验收标准 |
|------|-------|---------|---------|
| 批 1 | 15 | Phase 1a 起步 | mypy 100% + ruff 0 + 单测 ≥80% |
| 批 2 | 15 | 批 1 验收 + 7 天稳定 | 同上 + 集成测试 |
| 批 3 | 14 | 批 2 验收 + 14 天稳定 | 同上 + 跨批契约一致性 |

搬迁追踪器：`19_development_workspace/structure-and-mapping/contractbus-migration-tracker.yaml`，校验脚本：`scripts/governance/contractbus_migration_check.py`。

---

## 6. 模块分解（v2.0.0 完整版：M-01~M-27）

### 6.1 原有模块（M-01~M-20）— 路径与状态修正

| 模块ID | 模块名称 | 职责 | 实际路径 | 实现状态 | AI自治权限 |
|--------|---------|------|---------|---------|-----------|
| M-01 | CTR-001修复 | 修复 CTR-001 字段 | 已归档至旧树 | ✅ 已完成 | Immutable Core |
| M-02 | 源码树统一 | 统一为单一 src/zephyr/ | `src/zephyr/` | ✅ 已完成 | Immutable Core |
| M-03 | validate_ssot.py | SSoT 验证脚本 | `scripts/governance/d5_architecture/validate_ssot.py` | ✅ 已实现 | Immutable Core |
| M-04 | lazy_loader.py | 模块懒加载 | `src/zephyr/__init__.py` | ❌ 未实现 | Human-Gated |
| M-05 | pre-commit分层 | 分层 pre-commit | `.pre-commit-config.yaml` | ⚠️ 部分实现 | Immutable Core |
| M-06 | dmypy配置 | 增量类型检查 | `mypy.ini` | ❌ 未实现 | AI-Modifiable |
| M-07 | event_bus背压 | 事件总线背压 | `src/zephyr/shared/event_bus.py` | ❌ 未实现 | AI-Modifiable |
| M-08 | import-linter | 层依赖规则 | `.importlinter` | ❌ 未实现 | Human-Gated |
| M-09 | ContractBus接口 | 跨层通信抽象 | `src/zephyr/shared/contract_bus.py` | ❌ 未实现 | Human-Gated |
| M-10 | ZephyrLogger+OTel | 结构化日志+Metrics | `src/zephyr/shared/zephyr_logger.py` | ❌ 未实现 | AI-Modifiable |
| M-11 | contract_tester.py | 契约测试框架 | `src/zephyr/shared/contract_tester.py` | ❌ 未实现 | Human-Gated |
| M-12 | config_validator.py | 配置参数验证 | `src/zephyr/shared/config_validator.py` | ❌ 未实现 | Human-Gated |
| M-13 | fault_isolator.py | 故障域隔离 | `src/zephyr/shared/fault_isolator.py` | ❌ 未实现 | Human-Gated |
| M-14 | warm_hot_gate.py | Warm→Hot 阻断门 | `src/zephyr/shared/warm_hot_gate.py` | ❌ 未实现 | Human-Gated |
| M-15 | pydantic_v2_migrator.py | Pydantic v2 迁移 | `src/zephyr/shared/pydantic_v2_migrator.py` | ❌ 未实现 | Human-Gated |
| M-16 | event_bus_upgrade.py | 事件总线升级 | `src/zephyr/shared/event_bus_upgrade.py` | ❌ 未实现 | Human-Gated |
| M-17 | ai_audit_guard.py | AI修改审计守卫 | `src/zephyr/llm_security/behavior_audit_logger.py`（日志已有）+ `src/zephyr/shared/ai_audit_guard.py`（守卫规则引擎待实现） | ⚠️ 部分实现 | Immutable Core |
| M-18 | capacity_slo.yaml | 容量SLI/SLO标准 | `config/capacity/capacity_slo.yaml` | ❌ 未实现 | Human-Gated |
| M-19 | capacity_governance_loop.py | 容量治理闭环 | `src/zephyr/shared/capacity_governance_loop.py` | ❌ 未实现 | AI-Modifiable |
| M-20 | ttl_cleanup_engine.py | 派生文件TTL清理 | `src/zephyr/shared/ttl_cleanup_engine.py` | ❌ 未实现 | AI-Modifiable |

### 6.2 v2.0.0 新增模块（M-21~M-27）

| 模块ID | 模块名称 | 职责 | 预期路径 | 对标来源 | AI自治权限 |
|--------|---------|------|---------|---------|-----------|
| M-21 | error_budget_tracker.py | Error Budget 五级响应追踪 + Burn Rate 多窗口监控 | `src/zephyr/shared/error_budget_tracker.py` | Google SRE Workbook | Human-Gated（阈值）/ AI-Modifiable（消耗追踪） |
| M-22 | kill_switch.py | 全局一键熔断 | `src/zephyr/shared/kill_switch.py` | AI Agent Observability Best Practices | Human-Gated |
| M-23 | sandbox_executor.py | 高风险操作沙箱隔离 | `src/zephyr/shared/sandbox_executor.py` | AI Agent Observability Best Practices | Human-Gated |
| M-24 | degradation_chain.py | Graceful Degradation 模型降级链 | `src/zephyr/shared/degradation_chain.py` + `config/capacity/degradation_chain.yaml` | AI Agent Cost Crisis Report | Human-Gated（链定义）/ AI-Modifiable（链选择） |
| M-25 | reasoning_spans.py | Agent 推理步骤追踪（OTel 语义规范） | `src/zephyr/shared/reasoning_spans.py` | OpenTelemetry GenAI Semantic Conventions | AI-Modifiable |
| M-26 | cost_estimator.py | 执行前成本预估（Pre-flight Estimation） | `src/zephyr/shared/cost_estimator.py` | AI Agent Rate Limiting | AI-Modifiable |
| M-27 | semantic_cache.py | 语义缓存（复用 ChromaDB） | `src/zephyr/shared/semantic_cache.py` | Agent 成本控制实战 | AI-Modifiable |

### 6.3 蓝图外已有实现（纳入蓝图管理）

| 已有实现 | 实际路径 | 能力 | 蓝图对应 | 管理方式 |
|---------|---------|------|---------|---------|
| Token 预算管理器 | `src/zephyr/context_engine/context_budget_tracker.py` | 三级阈值 L1/L2/L3 | M-21 的 session 级子集 | 由 context-engine 蓝图管理，本蓝图引用 |
| 熔断器 | `src/zephyr/gates/circuit_breaker.py` | 单向熔断 + L08 注册表 | M-13 fault_isolator 的子集 | 由 gate-engine 蓝图管理，本蓝图引用 |
| Agent SLO 监控 | `src/zephyr/orchestrator/agent_health_monitor.py` | 5 项 SLO + 三态健康 | M-18 capacity_slo.yaml 的 Agent 维度 | 由 orchestrator 蓝图管理，本蓝图引用 |
| MCP 工具限流 | `src/zephyr/mcp/tool_contracts.yaml` | 声明式 rate_limit_qps | M-21 的 MCP 层子集 | 由 mcp-servers 蓝图管理，本蓝图引用 |
| 上下文规则 | `config/context_rules_v1.yaml` | 15 条上下文管理规则 | M-18 的上下文维度 | 由 context-engine 蓝图管理，本蓝图引用 |
| 基础设施登记表 | `_registry/catalogs/infrastructure-registry.yaml` | 8 个组件 SLA | M-18 的基础设施维度 | 由 registry 管理，本蓝图引用 |
| AI 风险登记表 | `_registry/catalogs/ai-risk-register.yaml` | 8 项 AI 风险 | M-17 的风险维度 | 由 registry 管理，本蓝图引用 |

---

## 7. 架构视图

### 7.1 三层框架（v2.0.0 更新）

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        容量治理层（Governance）                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │capacity_ │ │ai_audit_ │ │capacity_ │ │error_    │ │kill_     │    │
│  │slo.yaml  │ │guard.py  │ │governance│ │budget_   │ │switch.py │    │
│  │(Human-   │ │(Immutable│ │_loop.py  │ │tracker.py│ │(Human-   │    │
│  │ Gated)   │ │ Core)    │ │(AI-M)    │ │(H-G/A-M) │ │ Gated)   │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│                        运行时层（Runtime）                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │event_bus │ │fault_    │ │lazy_     │ │sandbox_  │ │degradation│   │
│  │_backpress│ │isolator  │ │loader.py │ │executor  │ │_chain.py │    │
│  │(AI-M)    │ │(Human-G) │ │(Human-G) │ │(Human-G) │ │(H-G/A-M) │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                              │
│  │reasoning │ │cost_     │ │semantic_ │                              │
│  │_spans.py │ │estimator │ │cache.py  │                              │
│  │(AI-M)    │ │(AI-M)    │ │(AI-M)    │                              │
│  └──────────┘ └──────────┘ └──────────┘                              │
├─────────────────────────────────────────────────────────────────────────┤
│                        结构层（Structure）                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │validate_ │ │pre-commit│ │import-   │ │ContractBus│ │ttl_cleanup│   │
│  │ssot.py   │ │_layers   │ │linter    │ │Schema Enf│ │_engine.py│    │
│  │(Immutable│ │(Immutable│ │(Human-G) │ │(Human-G) │ │(AI-M)    │    │
│  │ Core)    │ │ Core)    │ │          │ │          │ │          │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Phase 路线图（v2.0.0 更新）

| Phase | 名称 | 人日 | 关键交付物 | v2.0.0 新增交付物 |
|-------|------|:--:|---------|----------------|
| **0** | 治理地基 | 5-7 | `validate_ssot.py` / `capacity_slo.yaml` / `ai_audit_guard.py`（骨架）| Error Budget 五级响应骨架 + Saturation SLI + Kill Switch 骨架 + OTel 语义规范对齐 + DR 策略骨架 |
| **1a** | 基础闸门 | 6-8 | ContractBus 批1 / pre-commit 分层 / sandbox_gate / immutable_registry | 多级 Token Budget + Reasoning Spans 埋点 |
| **1b** | 核心运行时 | 6-8 | ContractBus 批2 / auto_fixer / session_carryover / audit_rules / governance_loop | Sandbox 沙箱执行器 + Graceful Degradation 降级链 |
| **2** | 完善集成 | 6-8 | ContractBus 批3 / fault_isolator / 故障域隔离 ≥3 / AISG 容量预算 | 成本预估器 + 语义缓存 + 容量预测模型 + Blameless Postmortem 模板 |
| **3/4** | 服务化/实盘 | 按需 | 触发条件：模块 >300 OR 并发Agent >20 OR 真实资金接入 | VictoriaMetrics 后端选项 + Toil 量化指标 |

### 7.3 Phase 0 验收标准（v2.0.0 更新）

| 维度 | 标准 | 测量方式 |
|------|------|---------|
| 代码 | mypy 100%（新增）| `mypy scripts/governance/` |
| 代码 | ruff 错误 = 0 | `ruff check scripts/` |
| 架构 | CTR-001 重复字段 = 0 | `validate_ssot.py` |
| 架构 | 双源码树 = 0 | `ls src/zephyr/` |
| AI | capacity_slo.yaml ≥ 8 SLI（含 Saturation） | YAML 字段数 |
| AI | error_budget_tracker.py 五级响应可运行 | 单元测试 |
| AI | kill_switch.py 全局熔断可触发 | 集成测试 |

### 7.4 AI 自治权限（v2.0.0 完整版）

| 组件 | 权限 | Provenance | v2.0.0 变更 |
|------|------|-----------|------------|
| `ai_audit_guard.py` 自身 | Immutable Core | Owner 审批 + ADR | — |
| `audit_rules.yaml` | Human-Gated | who/when/why | — |
| `capacity_slo.yaml` | Human-Gated | who/when/why | — |
| `governance_loop.py` | AI-Modifiable | 每次执行写指标 | — |
| `ai_provenance` 表 | Immutable Core | 只追加 + hash 链 | — |
| `capacity_metrics` 表 | AI-Modifiable | 7 天 TTL | — |
| `error_budget_tracker.py` | Human-Gated（阈值）/ AI-Modifiable（消耗追踪） | 阈值变更需 Owner 审批 | **v2.0.0 新增** |
| `error_budget` 表 | AI-Modifiable | 7 天 TTL | **v2.0.0 新增** |
| `kill_switch.py` | Human-Gated | 触发/恢复需 Owner 确认 | **v2.0.0 新增** |
| `sandbox_executor.py` | Human-Gated | 沙箱策略变更需 Owner 审批 | **v2.0.0 新增** |
| `degradation_chain.py` | Human-Gated（链定义）/ AI-Modifiable（链选择） | 链定义变更需 Owner 审批 | **v2.0.0 新增** |
| `degradation_chain.yaml` | Human-Gated | who/when/why | **v2.0.0 新增** |
| `reasoning_spans.py` | AI-Modifiable | 自动埋点 | **v2.0.0 新增** |
| `cost_estimator.py` | AI-Modifiable | 预估结果记录 | **v2.0.0 新增** |
| `semantic_cache.py` | AI-Modifiable | 缓存命中率记录 | **v2.0.0 新增** |
| `token_budget_usage` 表 | AI-Modifiable | 7 天 TTL | **v2.0.0 新增** |

> 完整权限以 `_registry/catalogs/ai-autonomy-authority-registry.md` 为唯一真源。

---

## 8. Error Budget 五级响应机制（v2.0.0 新增，v2.1.0 三级→五级升级）

对标 Google SRE Workbook §4 Error Budgets + §5 Alerting on SLOs + §5.4 Multi-Window Multi-Burn-Rate Alerts。

> **v2.1.0 升级原因**：三级（Healthy/Cautious/Critical）在高频 AI 变更场景下粒度过粗。Healthy 50%→Cautious 25% 中间 25% 是盲区——消耗率上升时没有预警级。Critical <25%→Exhausted 0% 也有 25% 盲区——预算快耗尽时没有紧急响应级。Google SRE Workbook 2025 修订版明确推荐五级粒度。

### 8.1 五级响应定义

| 级别 | Error Budget 剩余 | 触发条件 | 团队响应 | 开发重点 | 发布频率 | 自动动作 |
|------|-----------------|---------|---------|---------|---------|---------|
| **Healthy** | >60% | 默认 | 正常运营 | 新功能、实验 | 标准发布节奏 | 无 |
| **Warning** | 40%-60% | 过去 7 天消耗率 > 正常 2× | 轻度关注 | 功能完成 + 小改进 | 标准节奏 + 观察 | `log_warning` + 每周报告 |
| **Cautious** | 20%-40% | 过去 7 天消耗率 > 正常 3× | 加强监控 | 功能完成 + 修复 | 降低发布频率 50% | `log_warning` + `notify_owner` + 消耗率仪表盘 |
| **Critical** | 5%-20% | 过去 3 天消耗率 > 正常 5× | 可靠性优先 | Bug 修复 + 稳定性改进 | 发布冻结直到恢复到 Cautious | `log_critical` + `freeze_releases` + `auto_escalate` |
| **Emergency** | <5% | 预算即将耗尽 | 全量响应 | 仅修复导致预算消耗的根因 | 全冻结 | `log_emergency` + `kill_switch` 保守模式 + `notify_owner_urgent` |

### 8.2 Error Budget 消耗追踪（v2.1.0 五级版）

```yaml
# config/capacity/error_budget_config.yaml 完整示例
error_budgets:
  - slo_id: "CAP-001-startup-time"
    budget_window: "30d"
    burn_rate_alerts:
      - rate: 2.0      # 2× 正常消耗率
        tier: warning
        window: "7d"
        description: "7 天内消耗率超过正常 2 倍"
      - rate: 5.0
        tier: critical
        window: "3d"
        description: "3 天内消耗率超过正常 5 倍"
      - rate: 10.0
        tier: emergency
        window: "1d"
        description: "1 天内消耗率超过正常 10 倍"
    response_tiers:
      healthy:
        threshold: 0.6
        actions: []
      warning:
        threshold: 0.4
        actions: ["log_warning", "weekly_report"]
      cautious:
        threshold: 0.2
        actions: ["log_warning", "notify_owner", "reduce_release_frequency"]
      critical:
        threshold: 0.05
        actions: ["log_critical", "freeze_releases", "auto_escalate"]
      emergency:
        threshold: 0.0
        actions: ["log_emergency", "kill_switch_conservative", "notify_owner_urgent"]
    auto_recovery:
      emergency_to_critical:
        condition: "budget_remaining > 5% AND burn_rate_1d < 5×"
        cooldown: "6h"
      critical_to_cautious:
        condition: "budget_remaining > 20% AND burn_rate_3d < 3×"
        cooldown: "24h"
```

### 8.3 消耗率（Burn Rate）多窗口监控

对标 Google SRE Workbook §5.4 Multi-Window Multi-Burn-Rate Alerts：

| 窗口 | 消耗率阈值 | 对应级别 | 说明 |
|------|-----------|---------|------|
| 1h | > 14.4× | Emergency（立即） | 1 小时内消耗了 2% 预算——极端异常，可能 DDoS 或死循环 |
| 6h | > 6× | Critical（快速） | 6 小时内消耗了 5% 预算——严重异常 |
| 3d | > 3× | Cautious（慢速） | 3 天内消耗了 10% 预算——趋势恶化 |
| 30d | > 1× | Warning（基线） | 整窗口消耗超预算——持续性问题 |

> **短窗口 vs 长窗口**：短窗口抓脉冲式异常（如 1 小时内突发大量错误），长窗口抓慢性问题（如每天漏一点预算，月度总结才发现超支）。两者必须同时监控——单窗口会有盲区。

### 8.4 与 Kill Switch 的联动（v2.1.0 细化）

| Error Budget 级别 | Kill Switch 动作 | 恢复条件 |
|------------------|-----------------|---------|
| Critical 持续 1h | 自动触发 **保守模式**（仅允许 P0 操作，暂停所有 P1/P2 任务） | 恢复到 Cautious + Owner 确认 |
| Emergency | 自动触发 **只读模式**（禁止所有写入操作，仅允许查询和诊断） | Owner 手动解除 |
| 单日成本 > $100 | 自动触发保守模式 | Owner 确认 + 成本回落 |
| Burn Rate 1h > 14.4× | 立即触发只读模式（不等待 Emergency 判定——见 §8.3 短窗口） | Owner 调查根因后手动解除 |

### 8.5 自动恢复与手动恢复边界

| 恢复路径 | 自动 or 手动 | 理由 |
|---------|:----------:|------|
| Emergency → Critical | 自动（冷却 6h） | 临时脉冲不应无限期锁住系统 |
| Critical → Cautious | 自动（冷却 24h） | 趋势逆转后逐步放开 |
| Cautious → Healthy | 自动 | 正常恢复，无需人工 |
| 只读模式 | **手动（Owner）** | 只读模式 = 系统停止接收新工作，影响太大，必须人工确认 |

---

## 9. 多级 Token Budget（v2.0.0 新增）

对标 AI Agent Rate Limiting 社区实践（Token Bucket + 滑动窗口 + Pre-flight Estimation）。

### 9.1 四级限流体系

| 级别 | 维度 | 默认值 | 配置文件 |
|------|------|--------|---------|
| **Level 1: Per-request** | 单次请求最大 token | input: 32K / output: 4K / tool_calls: 10 | `config/capacity/token_budget.yaml` |
| **Level 2: Per-session** | 单 session token 预算 | 50K tokens / 5 iterations | `config/context_rules_v1.yaml`（已有） |
| **Level 3: Per-org** | 每日 token 总量 | 5M tokens / $10/day | `config/capacity/token_budget.yaml` |
| **Level 4: Global** | 全局 token 上限 | 50M tokens / $100/day | `config/capacity/token_budget.yaml` |

### 9.2 Pre-flight Estimation

执行前预估成本，超出预算则拒绝或降级：

```python
class CostEstimator:
    async def estimate(self, prompt_tokens: int, model: str) -> CostEstimate:
        estimated_cost = prompt_tokens * MODEL_COST[model].input_per_1k / 1000
        if estimated_cost > self.session_budget_remaining:
            return CostEstimate(affordable=False, suggestion="downgrade_model")
        return CostEstimate(affordable=True, estimated_cost=estimated_cost)
```

### 9.3 与已有实现的关系

- `context_budget_tracker.py`（L1/L2/L3 三级阈值）→ Level 2 的 session 级实现，由 context-engine 管理
- `tool_contracts.yaml`（rate_limit_qps）→ Level 1 的 MCP 工具维度，由 mcp-servers 管理
- 本蓝图 M-21 新增 Level 3/4 的 org/global 级限流 + Pre-flight Estimation

---

## 10. Kill Switch + Sandbox（v2.0.0 新增）

对标 AI Agent Observability Best Practices（Kill Switch + Sandbox Isolation）。

### 10.1 Kill Switch 全局熔断

```python
class KillSwitch:
    SIGNAL_FILE = ".audit_cache/kill_switch_active"
    ENV_VAR = "ZEPHYR_KILL_SWITCH"

    def is_active(self) -> bool:
        if os.environ.get(self.ENV_VAR, "0") == "1":
            return True
        return os.path.exists(self.SIGNAL_FILE)

    def activate(self, reason: str) -> None:
        with open(self.SIGNAL_FILE, "w") as f:
            f.write(f"{datetime.now().isoformat()}|{reason}\n")

    def deactivate(self) -> None:
        if os.path.exists(self.SIGNAL_FILE):
            os.remove(self.SIGNAL_FILE)
```

触发条件：
- Error Budget Critical 持续 1 小时
- Owner 手动激活（`ZEPHYR_KILL_SWITCH=1` 或创建信号文件）
- 单日成本超限（>$100）

### 10.2 Sandbox 沙箱执行器

高风险操作（文件删除、配置修改、外部 API 调用）先在沙箱中试运行：

```yaml
# sandbox_policy.yaml
sandbox_rules:
  - operation: "file_delete"
    sandbox: true
    dry_run: true
    require_confirmation: true
  - operation: "config_modify"
    sandbox: true
    diff_before_apply: true
  - operation: "external_api_call"
    sandbox: false
    cost_limit: 1.00
```

---

## 11. Graceful Degradation + 语义缓存（v2.0.0 新增）

对标 AI Agent Cost Crisis Report（Graceful Degradation）+ Agent 成本控制实战（语义缓存）。

### 11.1 模型降级链

```yaml
# degradation_chain.yaml
chains:
  - trigger: "cost_per_day > 5.00"
    fallback:
      - model: "deepseek-chat"
        max_tokens: 2000
        temperature: 0.3
      - model: "qwen2.5-3b-onnx"
        max_tokens: 1000
        temperature: 0.1
  - trigger: "latency_p99 > 10000"
    fallback:
      - model: "deepseek-chat"
        timeout: 5000
      - model: "qwen2.5-3b-onnx"
        timeout: 2000
```

### 11.2 语义缓存

复用已有 ChromaDB 基础设施，对重复/相似查询返回缓存结果：

- 缓存键：prompt 语义向量（BGE-M3 embedding）
- 命中阈值：余弦相似度 > 0.95
- TTL：24 小时（可配置）
- 失效策略：源数据变更时自动失效

---

## 12. OTel AI Agent 语义规范对齐（v2.0.0 新增）

对标 OpenTelemetry 2025 GenAI Semantic Conventions + AI Agent Semantic Conventions。

### 12.1 Reasoning Spans

Agent 推理步骤追踪，遵循 OTel GenAI Span 定义：

```python
from opentelemetry import trace

tracer = trace.get_tracer("zephyr.capacity-assurance")

async def trace_reasoning(agent_name: str, task: str, steps: list[str]):
    with tracer.start_as_current_span("agent.reasoning") as span:
        span.set_attribute("gen_ai.system", "zephyr")
        span.set_attribute("gen_ai.request.model", agent_name)
        span.set_attribute("agent.task", task)
        span.set_attribute("agent.steps.count", len(steps))
        for i, step in enumerate(steps):
            span.add_event(f"reasoning.step.{i}", {"description": step})
```

### 12.2 W3C TraceContext 传播

跨模块调用时传播 TraceContext，确保端到端追踪不断裂：

- 所有 ContractBus 调用自动注入 `traceparent` + `tracestate`
- 所有事件总线消息携带 `trace_context` 字段
- 与 `behavior_audit_logger.py` 集成，审计日志关联 Trace ID

---

## 13. 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 模块 > 300 OR 并发 Agent > 20 | Phase 3 服务化 |
| 真实资金接入 | Phase 4 实盘生产 |
| 单进程 Python 500 模块极限 | 多进程 / 分布式事件总线 / 数据库分片 |
| InfluxDB 成标准 | 替代自研 EMA 治理闭环 |
| VictoriaMetrics 需求明确 | 替代 SQLite capacity_metrics 时序存储（Phase 3 选项） |
| Error Budget Critical 持续 1h | 自动触发 Kill Switch 保守模式 |

**关键配置**：

```bash
# 环境变量
CAPACITY_SLO_CONFIG_PATH="config/capacity/capacity_slo.yaml"
CAPACITY_METRICS_DB_PATH=".audit_cache/capacity_metrics.db"
AI_AUDIT_RULES_PATH="config/audit/audit_rules.yaml"
AI_AUDIT_PROVENANCE_DB_PATH=".audit_cache/ai_provenance.db"
CAPACITY_GOVERNANCE_INTERVAL_SECONDS=300
ERROR_BUDGET_CONFIG_PATH="config/capacity/error_budget_config.yaml"
TOKEN_BUDGET_CONFIG_PATH="config/capacity/token_budget.yaml"
SANDBOX_POLICY_PATH="config/capacity/sandbox_policy.yaml"
DEGRADATION_CHAIN_PATH="config/capacity/degradation_chain.yaml"
ZEPHYR_KILL_SWITCH="0"
```

```yaml
# capacity_slo.yaml 示例（v2.0.0 含 Saturation 四黄金信号）
slo_registry:
  - id: CAP-001-startup-time
    description: "97 模块启动时间 P99"
    target: 2000
    measurement: pytest 基准测试
    golden_signal: latency
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-002-event-throughput
    description: "事件总线吞吐量"
    target: 1000
    measurement: msg/s 压力测试
    golden_signal: traffic
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-003-error-rate
    description: "模块间调用错误率"
    target: 0.001
    measurement: circuit_breaker 统计
    golden_signal: errors
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-004-memory-saturation
    description: "内存饱和度"
    target: 0.8
    measurement: psutil 内存监控
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-005-cpu-saturation
    description: "CPU 饱和度"
    target: 0.7
    measurement: psutil CPU 监控
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-2
  - id: CAP-006-queue-depth-saturation
    description: "事件队列深度饱和度"
    target: 500
    measurement: asyncio.Queue.qsize()
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-1
  - id: CAP-007-type-check-time
    description: "类型检查时间 P99"
    target: 30000
    measurement: dmypy 基准测试
    golden_signal: latency
    governance_layer: GOV-P2
    runtime_plane: RP-3
  - id: CAP-008-config-check-time
    description: "配置一致性检查时间 P99"
    target: 10000
    measurement: validate_ssot.py 计时
    golden_signal: latency
    governance_layer: GOV-P2
    runtime_plane: RP-3
```

---

## 14. 风险与缓解（v2.0.0 更新）

| 风险 | 概率 | 缓解 | v2.0.0 变更 |
|------|------|------|------------|
| ContractBus 批 1 回归引发链式失败 | 中 | 分三批 + 7 天稳定期 + 自动回归 | — |
| `ai_audit_guard` 误拦截阻断开发 | 低 | 骨架先上线（空规则）+ Phase 1b 增量 | — |
| 容量治理闭环 EMA 误报 | 中 | 阈值 + 持续时间双约束，调参周期 14 天 | — |
| Error Budget 三级响应过度保守 | 中 | 阈值可调 + 14 天观察期 + Owner 可手动覆盖 | **v2.0.0 新增** |
| Kill Switch 误触发 | 低 | 双通道确认（环境变量 + 文件信号）+ 触发需写 reason | **v2.0.0 新增** |
| 语义缓存返回过期结果 | 中 | TTL 24h + 源数据变更自动失效 + 相似度阈值 >0.95 | **v2.0.0 新增** |
| Graceful Degradation 降级链配置不当 | 中 | 降级链变更需 Owner 审批 + 7 天观察期 | **v2.0.0 新增** |
| 多级 Token Budget 过度限流 | 中 | 每级可独立配置 + burst 容忍 + 超限降级而非硬拒 | **v2.0.0 新增** |

---

## 15. 关键关联

| 关联文档 | 说明 |
|---------|------|
| `ai-autonomy-authority-registry.md` | 新组件权限的单一真源 |
| `vibe-coding-pipelines/blueprint.md` | 双管线 + 脚本系统蓝图 |
| `context-engine/blueprint.md` | Token 预算管理器（context_budget_tracker.py）的归属蓝图 |
| `gate-engine/blueprint.md` | 熔断器（circuit_breaker.py）的归属蓝图 |
| `mcp-servers/blueprint.md` | MCP 工具限流（tool_contracts.yaml）的归属蓝图 |
| `infrastructure-registry.yaml` | 基础设施组件 SLA 声明 |
| `ai-risk-register.yaml` | AI 操作风险登记 |
| Google SRE Workbook | Error Budget 五级响应 + 四黄金信号 + Burn Rate + Blameless Postmortem |
| OpenTelemetry GenAI Semantic Conventions | AI Agent 可观测性标准 |
| VictoriaMetrics Vibe Coding Blog (2026-01) | Vibe Coding 工具可观测性方案 |

> **历史溯源**：原始施工图 Wave 0 终审产出（2026-04-27），三轮审计 GLM/Kimi/Qwen + Opus-4.7 裁决 5 条争议 + 兜底 V-11/V-12/V-13。2026-05-01 迁入 `03_modules/l01_infrastructure/capacity-assurance/blueprint.md`。2026-05-03 v2.0.0 升级——对齐专业机构实践与 Vibe Coding 社区前沿，新增 M-21~M-27 共 7 个模块，纳入 7 项蓝图外已有实现，修正路径与状态。2026-05-03 v2.1.0 升级——补齐施工前置设计：Error Budget 三级→五级 + 灾难恢复策略 + 容量预测模型 + 跨模块集成设计。

---

## 16. 灾难恢复（DR）策略（v2.1.0 新增）

对标 Google SRE Workbook §12 Disaster Recovery + ITIL Service Continuity Management（服务连续性管理）。

> **大白话**：DR 策略就是"系统挂了怎么办"的预案。不是"系统会不会挂"的问题——是一定会挂，只是不知道什么时候。所以必须提前做好"挂了以后怎么恢复"的设计。

### 16.1 灾难场景分级

| 级别 | 场景 | 影响 | RTO（恢复时间目标） | RPO（恢复点目标） |
|:---:|------|------|:---:|:---:|
| **L1 轻微** | 单个 `.py` 文件损坏 / 单元测试挂掉 | 单模块不可用 | < 1h | 0（Git 恢复） |
| **L2 中等** | SQLite 数据库损坏 / 事件总线挂掉 | 容量指标 / 审计日志丢失 | < 4h | < 1h（从备份恢复） |
| **L3 严重** | Provenance Chain 断裂 / 审计日志全部丢失 | AI 修改无法追溯 | < 24h | < 1h |
| **L4 灾难** | 整个 `.audit_cache/` 被删除 / 源码树损坏 | 系统完全不可用 | < 48h | < 24h |

### 16.2 各组件恢复策略

| 组件 | 数据特性 | 备份策略 | 恢复方式 | 校验方式 |
|------|---------|---------|---------|---------|
| `ai_provenance` 表 | Immutable Core，只追加 | 每日全量备份到 `_audit_cache_backups/` | 从最新备份恢复 + Hash 链完整性校验 | `SELECT curr_hash, prev_hash` 逐行验证 |
| `capacity_metrics` 表 | AI-Modifiable，7 天 TTL | 无需备份（2 天内数据可由 EMA 重算恢复） | 删除重建表 → EMA 冷启动重算 | 对比重建前后 EMA 值误差 < 5% |
| `error_budget` 表 | AI-Modifiable | 每日增量备份 | 从备份恢复 + 重新计算 budget_remaining | 对比恢复前后 response_tier 一致 |
| `token_budget_usage` 表 | AI-Modifiable，7 天 TTL | 无需备份 | 删除重建表 | 无（统计数据，丢失可接受） |
| `.audit_cache/` 目录 | AI-Modifiable | 每日压缩快照到 `.audit_cache_backups/` | 解压最新快照 | `validate_blueprint_provenance.py` |
| 源码树 | Git 管理 | Git + 每 tag 打一个完整快照 | `git checkout` | `mypy` + `ruff` + 全量测试 |
| 蓝图文件 | Git 管理 | Git | `git checkout` | `validate_ssot.py` |

### 16.3 自动恢复脚本

```bash
# disaster_recovery.sh（Phase 0 骨架）
#!/bin/bash
# 用法：bash scripts/governance/dr_recovery.sh [level]
#   L1: 单文件恢复  L2: DB 恢复  L3: Provenance 恢复  L4: 全量恢复

LEVEL=${1:-L1}
BACKUP_DIR=".audit_cache_backups"

case $LEVEL in
  L1)
    echo "[DR-L1] 从 Git 恢复最新版本..."
    git checkout -- src/zephyr/
    python -m pytest tests/ -q
    ;;
  L2)
    echo "[DR-L2] 从备份恢复数据库..."
    cp ${BACKUP_DIR}/capacity_metrics_latest.db .audit_cache/capacity_metrics.db
    cp ${BACKUP_DIR}/error_budget_latest.db .audit_cache/error_budget.db
    python scripts/governance/validate_blueprint_code_sync.py --warn-only
    ;;
  L3)
    echo "[DR-L3] Provenance Chain 完整性修复..."
    cp ${BACKUP_DIR}/ai_provenance_latest.db .audit_cache/ai_provenance.db
    python -c "from zephyr.shared.capacity_assurance import verify_provenance_chain; verify_provenance_chain()"
    ;;
  L4)
    echo "[DR-L4] 全量灾难恢复..."
    git checkout --
    tar -xzf ${BACKUP_DIR}/audit_cache_full_latest.tar.gz -C .audit_cache/
    python -m pytest tests/ -q
    python scripts/governance/validate_ssot.py --warn-only
    python scripts/governance/validate_blueprint_code_sync.py --warn-only
    ;;
esac
```

### 16.4 DR 演练计划

| 频率 | 演练内容 | 验收标准 |
|------|---------|---------|
| 每周 | L1 单文件恢复演练 | 5 分钟内恢复 + 单元测试全绿 |
| 每月 | L2 数据库恢复演练 | 15 分钟内恢复 + 指标误差 < 5% |
| 每季度 | L3 Provenance 恢复演练 | 1 小时内恢复 + Hash 链完整 |
| 每年 | L4 全量灾难恢复演练 | 4 小时内恢复 + 系统功能全绿 |

---

## 17. 容量预测模型（v2.1.0 新增）

对标 ITIL Capacity Management（容量管理）+ Google SRE Workbook §14 Capacity Planning（容量规划）。

> **大白话**：容量预测不是"算命"——是用历史数据推演未来。如果现在 97 个模块用 200MB 内存，按趋势 3 个月后会到 500 个模块，要不要提前加服务器？预测模型就是回答这个问题的。

### 17.1 预测维度

| 维度 | 指标 | 数据来源 | 预测方法 | 预测周期 |
|------|------|---------|---------|:---:|
| 模块增长 | 模块数 | `module-registry.yaml` / `git log` | 线性回归 + 指数平滑 | 1 周 / 1 月 / 3 月 |
| 内存占用 | RSS / VIRT | `psutil` 采样（M-23 sandbox_executor） | 线性回归 | 1 月 / 3 月 |
| Token 消耗 | tokens/day | `token_budget_usage` 表 | 移动平均 + 趋势外推 | 1 周 / 1 月 |
| 成本消耗 | cost/day | `token_budget_usage` 表 cost_usd | 同上 | 1 周 / 1 月 |
| 测试时长 | 全量测试耗时 | pytest --durations | 线性回归 | 1 月 / 3 月 |
| 类型检查时长 | dmypy 耗时 | dmypy 基准测试 | 同上 | 1 月 |

### 17.2 预测算法

```python
# capacity_predictor.py（Phase 2 实现）
from typing import NamedTuple
from datetime import timedelta

class CapacityPrediction(NamedTuple):
    metric: str
    current_value: float
    predicted_30d: float
    predicted_90d: float
    confidence: float          # 0.0 - 1.0
    warning_threshold: float   # 超过此值触发 Warning
    critical_threshold: float  # 超过此值触发 Critical

class CapacityPredictor:
    def predict_modules_30d(self) -> CapacityPrediction:
        """基于 git log 中模块文件的新增频率预测 30 天后的模块数"""
        ...

    def predict_memory_30d(self) -> CapacityPrediction:
        """基于 psutil 采样 + 模块数预测的内存占用"""
        ...

    def predict_cost_30d(self) -> CapacityPrediction:
        """基于 token_budget_usage 表的成本趋势"""
        ...
```

### 17.3 告警阈值

| 预测指标 | Warning 阈值 | Critical 阈值 | 触发动作 |
|---------|------------|-------------|---------|
| 预测模块数 30d | > 300 | > 500 | Critical → 启动 Phase 3 服务化准备 |
| 预测内存 30d | > 物理内存 70% | > 物理内存 90% | Critical → 触发 Kill Switch 保守模式 |
| 预测成本 30d | > $150/day | > $300/day | Critical → 自动启用 Graceful Degradation |
| 预测测试时长 30d | > 300s | > 600s | Warning → 并行化测试 |

---

## 18. 跨模块集成设计（v2.1.0 新增）

对标 ITIL Service Integration and Management（服务集成管理）+ Microservices Integration Patterns（微服务集成模式）。

> **大白话**：蓝图里 27 个模块不是独立的孤岛——Kill Switch 要跟已有的 circuit_breaker 协作，Graceful Degradation 要跟已有的 context_budget_tracker 协作。这章画清楚"谁跟谁怎么配合"。

### 18.1 ✅ 已实现集成（现有代码已协作）

| 集成对 | 协作方式 | 状态 |
|--------|---------|:---:|
| `context_budget_tracker` ↔ `doc_compressor` | budget_tracker L2 阈值触发 → 建议 doc_compressor 压缩 | ✅ 已集成 |
| `behavior_audit_logger` ↔ 所有模块 | 所有模块调用 behavior_audit_logger 记录操作 | ✅ 全局 |
| `atomic_transaction_manager` ↔ `sqlite_schema` | ATM 保证 DB 操作原子性 | ✅ 已集成 |
| `agent_health_monitor` ↔ orchestrator | orchestrator 产出 Result → health_monitor 消费并判定 | ✅ 已集成 |

### 18.2 🔧 待实现集成（需 2 施工）

#### 集成 1：Kill Switch ↔ Circuit Breaker（Phase 1a）

```
现有模块（circuit_breaker.py）  +  新模块（kill_switch.py）
          CBG 按模块熔断                 全局总闸
                    ↓ 协同规则 ↓
```

| Kill Switch 模式 | 对 CBG 的影响 | 理由 |
|-----------------|-------------|------|
| **保守模式** | CBG 阈值降低 50%（失败阈值减半 → 更容易触发 CBG 熔断） | 保守模式下容错率应更低 |
| **只读模式** | 所有 CBG 自动熔断（OPEN），禁止任何跨模块调用 | 只写无读 |

**接口设计**：

```python
# circuit_breaker.py 新增接口
class CBGManager:
    def set_global_policy(self, policy: KillSwitchPolicy) -> None:
        """Kill Switch 下发全局策略，CBGManager 据此调整所有 CBG 行为"""
        if policy.mode == "conservative":
            for cbg in self.circuits.values():
                cbg.failure_threshold = max(1, cbg.failure_threshold // 2)
        elif policy.mode == "readonly":
            for cbg in self.circuits.values():
                cbg.force_open("kill_switch_readonly")
```

#### 集成 2：Graceful Degradation ↔ Context Budget Tracker（Phase 1b）

```
现有模块（context_budget_tracker.py）  +  新模块（degradation_chain.py）
           session 级 token 监控                 模型降级
                       ↓ 协同规则 ↓
```

| context_budget_tracker 阈值 | 触发 degradation_chain 动作 |
|---------------------------|--------------------------|
| L1_WARNING (80%) | 提示"是否考虑降级模型以节省 token" |
| L2_THROTTLE (90%) | 自动降级：下一个请求使用降级链中第一档模型 |
| L3_HARD_STOP (95%) | 当前请求完成后，session 内所有后续请求自动使用最低档模型 |

**接口设计**：

```python
# degradation_chain.py 接收 context_budget_tracker 事件
def on_token_threshold(budget_state: BudgetState) -> DegradationAction:
    if budget_state.threshold == "L2_THROTTLE":
        return DegradationAction(
            action="downgrade_model",
            target=degradation_chain.get_fallback(0),
            reason=f"Token budget at {budget_state.usage_pct:.0%}"
        )
```

#### 集成 3：Error Budget Tracker ↔ Agent Health Monitor（Phase 1b）

```
现有模块（agent_health_monitor.py）  +  新模块（error_budget_tracker.py）
             Agent 健康状态                        Error Budget
                       ↓ 协同规则 ↓
```

| Agent 健康状态 | 对 Error Budget 的影响 |
|-------------|---------------------|
| DEGRADED（3+ Agent）| 加速消耗：burn_rate_multiplier = 2×（相当于速度两倍消耗预算） |
| UNHEALTHY（1+ Agent）| 严重加速：burn_rate_multiplier = 5× |

**接口设计**：

```python
# agent_health_monitor.py → 事件总线 → error_budget_tracker.py
@event_bus.subscribe("agent_health.changed")
def on_agent_health_changed(event: AgentHealthEvent):
    if event.health == "UNHEALTHY":
        error_budget_tracker.set_burn_rate_multiplier(5.0, reason=f"Agent {event.agent_id} unhealthy")
    elif event.health == "DEGRADED" and degraded_count >= 3:
        error_budget_tracker.set_burn_rate_multiplier(2.0, reason=f"{degraded_count} agents degraded")
```

#### 集成 4：Sandbox ↔ Circuit Breaker + Kill Switch（Phase 1b）

```
新模块（sandbox_executor.py）  +  circuit_breaker.py  +  kill_switch.py
           沙箱试运行                      模块熔断                 全局熔断
                               ↓ 协同规则 ↓
```

- Sandbox 中操作失败 → 不触发 CBG 失败计数（沙箱失败不应计入生产 CBG）
- Sandbox 中操作成功但 CBG OPEN → 真实执行自动拒绝（生产闸门优先于沙箱验证）
- Kill Switch 激活时 → Sandbox 也终止（全局熔断覆盖一切，包括沙箱）

---

## 19. 已实现代码完整路径索引（v2.0.0 新增）

> **目的**：本节是蓝图所有已实现代码的"地址簿"——任何新 AI session 读完此表，即可零推理定位每一个已落盘的文件。路径均为相对于项目根 `D:\ZephyrAlpha\` 的完整路径。最后验证时间：2026-05-03。

### 19.1 蓝图内模块（M-01~M-27）已实现文件

| 模块ID | 模块名称 | 实现状态 | 源码路径 | 测试路径 | 配置/数据路径 |
|--------|---------|:-------:|---------|---------|-------------|
| M-01 | CTR-001修复 | ✅ 已完成 | 已归档至旧树 | — | — |
| M-02 | 源码树统一 | ✅ 已完成 | `src/zephyr/` | — | — |
| M-03 | validate_ssot.py | ✅ 已实现 | `scripts/governance/d5_architecture/validate_ssot.py` | — | — |
| M-04 | lazy_loader.py | ❌ 未实现 | — | — | — |
| M-05 | pre-commit分层 | ⚠️ 部分实现 | `.pre-commit-config.yaml` | — | — |
| M-06 | dmypy配置 | ❌ 未实现 | — | — | — |
| M-07 | event_bus背压 | ❌ 未实现 | — | — | — |
| M-08 | import-linter | ❌ 未实现 | — | — | — |
| M-09 | ContractBus接口 | ❌ 未实现 | — | — | — |
| M-10 | ZephyrLogger+OTel | ❌ 未实现 | — | — | — |
| M-11 | contract_tester.py | ❌ 未实现 | — | — | — |
| M-12 | config_validator.py | ❌ 未实现 | — | — | — |
| M-13 | fault_isolator.py | ❌ 未实现 | — | — | — |
| M-14 | warm_hot_gate.py | ❌ 未实现 | — | — | — |
| M-15 | pydantic_v2_migrator.py | ❌ 未实现 | — | — | — |
| M-16 | event_bus_upgrade.py | ❌ 未实现 | — | — | — |
| M-17 | ai_audit_guard.py | ⚠️ 部分实现 | `src/zephyr/llm_security/behavior_audit_logger.py`（日志已有）| `tests/unit/test_ai_behavior_audit_logger.py` | — |
| M-18 | capacity_slo.yaml | ❌ 未实现 | — | — | — |
| M-19 | capacity_governance_loop.py | ❌ 未实现 | — | — | — |
| M-20 | ttl_cleanup_engine.py | ❌ 未实现 | — | — | — |
| M-21 | error_budget_tracker.py | ❌ 未实现 | — | — | — |
| M-22 | kill_switch.py | ❌ 未实现 | — | — | — |
| M-23 | sandbox_executor.py | ❌ 未实现 | — | — | — |
| M-24 | degradation_chain.py | ❌ 未实现 | — | — | — |
| M-25 | reasoning_spans.py | ❌ 未实现 | — | — | — |
| M-26 | cost_estimator.py | ❌ 未实现 | — | — | — |
| M-27 | semantic_cache.py | ❌ 未实现 | — | — | — |

### 19.2 蓝图外已有实现（由其他蓝图管理，本蓝图引用）

| 能力 | 源码路径 | 测试路径 | 配置路径 | 归属蓝图 |
|------|---------|---------|---------|---------|
| Token 预算管理器（L1/L2/L3 三级阈值） | `src/zephyr/context_engine/context_budget_tracker.py` | `tests/unit/test_doc_compressor.py`（集成测试） | `config/context_rules_v1.yaml` | context-engine |
| 上下文压缩器（DocCompressor） | `src/zephyr/context_engine/doc_compressor.py` | `tests/unit/test_doc_compressor.py` | — | context-engine |
| 熔断器（CBGManager + L08 注册表） | `src/zephyr/gates/circuit_breaker.py` | `tests/unit/test_circuit_breaker.py` | — | gate-engine |
| Agent SLO 监控（5 项 SLO + 三态健康） | `src/zephyr/orchestrator/agent_health_monitor.py` | `tests/unit/test_agent_health_monitor.py` | — | orchestrator |
| AI 行为审计日志（4 种事件 + JSONL） | `src/zephyr/llm_security/behavior_audit_logger.py` | `tests/unit/test_ai_behavior_audit_logger.py` | — | llm-security |
| 输入消毒器（InputSanitizer） | `src/zephyr/llm_security/input_sanitizer.py` | — | — | llm-security |
| 任务反馈收集器 | `src/zephyr/feedback_loop/feedback_collector.py` | `tests/unit/test_feedback_collector.py` | — | feedback-loop |
| 原子事务管理器（ATM） | `src/zephyr/db/atomic_transaction_manager.py` | `tests/unit/test_atomic_transaction_manager.py` | — | database |
| SQLite Schema DDL + init_db | `src/zephyr/db/sqlite_schema.py` | — | — | database |
| MCP 工具限流（声明式 rate_limit_qps） | `src/zephyr/mcp/tool_contracts.yaml` | — | — | mcp-servers |
| L12 Metrics 骨架 | `src/zephyr/l12_system_telemetry/metrics/__init__.py` | — | — | system-telemetry |

### 19.3 治理脚本（已实现）

| 脚本名称 | 完整路径 | 功能 | 对应蓝图模块 |
|---------|---------|------|------------|
| validate_ssot.py | `scripts/governance/d5_architecture/validate_ssot.py` | SSoT 矛盾扫描器，扫描 docs/ 下所有 Markdown frontmatter 检测跨文件字段矛盾 | M-03 |
| validate_blueprint_provenance.py | `scripts/governance/d3_metadata/validate_blueprint_provenance.py` | 蓝图真源准入门禁，校验蓝图目录必须包含 provenance 三件套 | M-17（Provenance Chain） |

### 19.4 配置文件（已存在）

| 配置名称 | 完整路径 | 功能 | 消费者 |
|---------|---------|------|--------|
| context_rules_v1.yaml | `config/context_rules_v1.yaml` | 15 条上下文管理规则（token 预算分配/窗口滑动/优先级衰减/P0 钉住/输出缓冲/预留守卫） | `context_budget_tracker.py` |
| tool_contracts.yaml | `src/zephyr/mcp/tool_contracts.yaml` | 5 个 MCP Server 工具契约 + rate_limit_qps + 429 错误码 | MCP 运行时（待实现） |

### 19.5 注册表文件（已存在，蓝图引用）

| 注册表名称 | 完整路径 | 功能 | 对应蓝图模块 |
|-----------|---------|------|------------|
| infrastructure-registry.yaml | `docs/01_policies_and_standards/_registry/catalogs/infrastructure-registry.yaml` | 8 个基础设施组件 SLA 声明 | M-18（基础设施维度） |
| ai-risk-register.yaml | `docs/01_policies_and_standards/_registry/catalogs/ai-risk-register.yaml` | 8 项 AI 操作风险登记 | M-17（风险维度） |
| cross-module-dependency-registry.yaml | `docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml` | 跨模块依赖登记（含 DEP-001: runtime-integration → capacity-assurance） | 全局引用 |
| module-registry.yaml | `docs/03_modules/module-registry.yaml` | 模块生命周期登记表 SSoT | 全局引用 |
| blueprint-registry.yaml | `docs/03_modules/blueprint-registry.yaml` | 蓝图深度评估登记表 | 全局引用 |
| domain-events.yaml | `docs/02_enterprise_architecture/target-architecture/architecture-model/events/domain-events.yaml` | 22 条领域事件（含 SystemDegraded / 容量扩展触发条件） | M-07 / M-19 |

### 19.6 蓝图自身文件

| 文件 | 完整路径 | 说明 |
|------|---------|------|
| 蓝图本体 | `docs/03_modules/l01_infrastructure/capacity-assurance/blueprint.md` | 本文件（唯一真源） |
| 目录索引 | `docs/03_modules/l01_infrastructure/capacity-assurance/index.md` | 模块目录索引 |
| 历史施工图 | `docs/03_modules/l01_infrastructure/capacity-assurance/delivery/construction-plan-v3.1-archived.md` | 已归档，内容已合并至蓝图 |
| delivery 索引 | `docs/03_modules/l01_infrastructure/capacity-assurance/delivery/index.md` | delivery 目录索引 |

### 19.7 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §19（本节）→ 知道"哪些已实现、在哪里"
2. 读 §6（模块分解）→ 知道"每个模块的职责和 AI 自治权限"
3. 读 §7.2（Phase 路线图）→ 知道"下一步该做什么"
4. 按需读 §8~§13（具体能力设计）→ 知道"怎么做"

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/unit/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
- 注册表在 `docs/01_policies_and_standards/_registry/catalogs/` 下
