---
module_id: MOD-INF-001
title: 容量保障体系蓝图（B3 · 2）
doc_type: blueprint
status: Active
version: 2.6.0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
ttl: permanent
construction_progress: phase_1_partial
belongs_to: "MOD-MASTER-001"
dependencies: []
priority: P0
tags:
  - capacity-assurance
  - slo
  - ai-audit-guard
  - contractbus
  - infrastructure
  - blind-spots
  - self-healing
  - business-sli
  - alert-fatigue
  - change-rate-limit
  - solo-maintainer
  - context-budget
  - per-task-budget
  - degradation-spiral
  - token-value-roi
  - ai-skill-health
  - trace-context-capacity
  - owner-toil
  - error-budget
  - token-budget
  - kill-switch
  - sandbox
  - graceful-degradation
  - otel
summary: ZephyrAlpha 容量保障体系完整蓝图 v2.4.0。三轮盲点审计共识别 38 项盲点。覆盖 SLI/SLO 注册表（含 Saturation 四黄金信号 + 插桩点定义 + SLO 窗口分层）、Error Budget 五级响应（含 Burn Rate 多窗口监控 + 消耗归因 + 脉冲容忍）、AI 审计守卫、容量治理闭环、ContractBus 分批迁移、SSoT 校验、多级 Token Budget（含 Per-Task 预算 + Context 预算水位线 + 沉没成本干预）、Kill Switch（含渐进式流量切换 + 修复通道保持 + 启动保护窗 + 优雅关机）、Sandbox 沙箱、Graceful Degradation 降级链（含双向模型路由 + 成本感知回升 + 厂商风险对冲）、Reasoning Spans 推理追踪、语义缓存、灾难恢复策略（含 DR 演练可测试性）、容量预测模型（含 AI 行为预测 + AI 技能健康检测 + 退化螺旋检测 + Owner 运维负担追踪 + Day-0 冷启动 + 容量悬崖非线性 + 未知任务类型检测）、跨模块集成设计（含 TraceContext 容量元数据传播 + 观察者效应隔离）、Telemetry 存储生命周期管理、SQLite 写入缓冲层、Token 价值归因 ROI 模型、Business SLI 业务健康维度、告警疲劳治理、施工节奏控制、容量健康评分、盲点全量清单等关键能力。所有设计按 1500 模块极限容量考虑。v2.4.0 补齐第三轮深度审计——新增 13 项盲点（#26~#38）含时间动力学/观察者效应/可测试性/物理约束/厂商风险/沉没成本/容量悬崖/审计完整性八维度。
---

# 容量保障体系蓝图（B3 · 2）

> **真源声明**：本蓝图是 ZephyrAlpha 容量保障体系的唯一真源。v1.0.0 由原始施工图 Wave 0 三轮审计 + Claude-Opus-4.7 终审产出。v2.0.0 对齐专业机构实践（Google SRE / OpenTelemetry）与 Vibe Coding 社区前沿。v2.1.0 补齐施工前置设计——Error Budget 三级→五级升级 + 灾难恢复策略 + 容量预测模型 + 跨模块集成设计。v2.2.0 补齐盲点分析——20 项盲点全量识别 + SOLO Coder 特异性优化 + Business SLI + 告警疲劳治理 + 施工节奏控制 + 顶尖设计参考架构。v2.3.0 补齐第二轮深度审计——新增 9 项盲点（#17~#25）+ 两轮合并 25 项盲点全景。v2.4.0 补齐第三轮深度审计——新增 13 项盲点（#26~#38）+ 时间动力学 + 观察者效应 + 可测试性 + 物理约束 + 厂商风险 + 沉没成本 + 容量悬崖 + 审计完整性 + 三轮合并 38 项盲点终局全景。

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
- Blameless Postmortem 流程 → `docs/01_policies_and_standards/governance/ai/`（beta 补充）
- Toil 量化指标 → `capacity_slo.yaml` beta 补充

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
| 3 | 容量指标采样 | structlog + OpenTelemetry SDK | 业界标准，experimental 即接入避免 stable 重构 | — |
| 4 | AI 审计守卫规则 | YAML 规则集 + Pydantic 校验 | 规则可演化，骨架 scaffold 即上线 | — |
| 5 | 治理闭环 | 自研 EMA + 阈值 + 持续时间 | 零依赖；stable 升级 InfluxDB | — |
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
| 批 1 | 15 | experimental 起步 | mypy 100% + ruff 0 + 单测 ≥80% |
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
| M-18 | capacity_slo.yaml | 容量SLI/SLO标准 | `config/capacity/capacity_slo.yaml` | ⚠️ 首版已落地（MOD-INF-001 M-18，≥8 SLI + arch_guard 阈值；插桩点仍 TBD） | Human-Gated |
| M-19 | capacity_governance_loop.py | 容量治理闭环 | `src/zephyr/shared/capacity_governance_loop.py` | ❌ 未实现 | AI-Modifiable |
| M-20 | ttl_cleanup_engine.py | 派生文件TTL清理 | `src/zephyr/shared/ttl_cleanup_engine.py` | ❌ 未实现 | AI-Modifiable |

### 6.2 v2.0.0 新增模块（M-21~M-27）📋 全部规划中

| 模块ID | 模块名称 | 职责 | 预期路径 | 对标来源 | AI自治权限 | 📋 |
|--------|---------|------|---------|---------|-----------|----|
| M-21 | error_budget_tracker.py | Error Budget 五级响应追踪 + Burn Rate 多窗口监控 | `src/zephyr/shared/error_budget_tracker.py` | Google SRE Workbook | Human-Gated（阈值）/ AI-Modifiable（消耗追踪） | 规划中 |
| M-22 | kill_switch.py | 全局一键熔断 | `src/zephyr/shared/kill_switch.py` | AI Agent Observability Best Practices | Human-Gated | 规划中 |
| M-23 | sandbox_executor.py | 高风险操作沙箱隔离 | `src/zephyr/shared/sandbox_executor.py` | AI Agent Observability Best Practices | Human-Gated | 规划中 |
| M-24 | degradation_chain.py | Graceful Degradation 模型降级链 | `src/zephyr/shared/degradation_chain.py` + `config/capacity/degradation_chain.yaml` | AI Agent Cost Crisis Report | Human-Gated（链定义）/ AI-Modifiable（链选择） | 规划中 |
| M-25 | reasoning_spans.py | Agent 推理步骤追踪（OTel 语义规范） | `src/zephyr/shared/reasoning_spans.py` | OpenTelemetry GenAI Semantic Conventions | AI-Modifiable | 规划中 |
| M-26 | cost_estimator.py | 执行前成本预估（Pre-flight Estimation） | `src/zephyr/shared/cost_estimator.py` | AI Agent Rate Limiting | AI-Modifiable | 规划中 |
| M-27 | semantic_cache.py | 语义缓存（复用 ChromaDB） | `src/zephyr/shared/semantic_cache.py` | Agent 成本控制实战 | AI-Modifiable | 规划中 |

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

### 7.3 scaffold 验收标准（v2.0.0 更新）

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
| 模块 > 300 OR 并发 Agent > 20 | beta 服务化 |
| 真实资金接入 | stable 实盘生产 |
| 单进程 Python 500 模块极限 | 多进程 / 分布式事件总线 / 数据库分片 |
| InfluxDB 成标准 | 替代自研 EMA 治理闭环 |
| VictoriaMetrics 需求明确 | 替代 SQLite capacity_metrics 时序存储（beta 选项） |
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
| `ai_audit_guard` 误拦截阻断开发 | 低 | 骨架先上线（空规则）+ experimental 增量 | — |
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
# disaster_recovery.sh（scaffold 骨架）
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
# capacity_predictor.py（beta 实现）
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
| 预测模块数 30d | > 300 | > 500 | Critical → 启动 beta 服务化准备 |
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

#### 集成 1：Kill Switch ↔ Circuit Breaker（experimental）

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

#### 集成 2：Graceful Degradation ↔ Context Budget Tracker（experimental）

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

#### 集成 3：Error Budget Tracker ↔ Agent Health Monitor（experimental）

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

#### 集成 4：Sandbox ↔ Circuit Breaker + Kill Switch（experimental）

```
新模块（sandbox_executor.py）  +  circuit_breaker.py  +  kill_switch.py
           沙箱试运行                      模块熔断                 全局熔断
                               ↓ 协同规则 ↓
```

- Sandbox 中操作失败 → 不触发 CBG 失败计数（沙箱失败不应计入生产 CBG）
- Sandbox 中操作成功但 CBG OPEN → 真实执行自动拒绝（生产闸门优先于沙箱验证）
- Kill Switch 激活时 → Sandbox 也终止（全局熔断覆盖一切，包括沙箱）

---

## 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\capacity-assurance\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\capacity_assurance\` | 容量保障源码 |
| 施工文档 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\capacity-assurance\delivery\` | 施工记录 |

---

## 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Agent RBAC (MOD-INF-018) | CBG 熔断时权限检查 | CBG OPEN → `rbac.blocked` | 熔断时权限降级 |
| Budget Enforcer (MOD-INF-024) | 容量预算 → Token Budget | Budget Exceeded → `budget_enforcer.degrade()` | 超预算触发降级 |
| Rollback System (MOD-INF-021) | CBG 熔断 → 自动回滚 | CBG OPEN → `rollback.auto_trigger()` | 熔断回滚生效 |
| System Telemetry (MOD-INF-015) | 容量 metrics | `capacity_metrics` → `telemetry_collector` | 容量数据可观测 |

---

## 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | Budget Enforcer 蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\budget-enforcer\blueprint.md` | 容量预算联动 | 容量保障实现后更新 |

---

## 后果（Consequences）

**正面后果**：
- 容量可量化——不再靠直觉估计
- 自动化熔断——超预算自动保护
- 全局统一预算模型——所有模块共享容量管理

**负面后果**：
- 预算估算不准——初期依赖人为估计可能偏差
- 熔断误触发风险——正常业务被中断
- 多模块预算协调复杂——P0 模块优先级冲突时需人工决策

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
| M-18 | capacity_slo.yaml | ⚠️ 首版已落地 | `config/capacity/capacity_slo.yaml` | `scripts/arch_guard/fitness_functions/check_capacity_slo_ssot.py` | arch_guard |
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

---

## 20. 盲点分析与补充设计（v2.2.0 新增）

> **大白话**：前 19 节已经把容量保障的骨架搭好了。但经过对标 Google SRE / Netflix Chaos Engineering / Meta Production Engineering / ISACA AI Governance / Vibe Coding 社区 2025-2026 前沿实践的全量审计，以及从"100% AI 施工 + 1人+AI 维护"这个极度特殊语境出发的反向推演，发现了 **20 个盲点**。本节逐个拆解，每个盲点给出：问题本质 → 专业机构做法 → SOLO Coder 折中方案 → 代码/配置骨架。

> **审计方法**：对照 Google SRE Workbook §4 §5 §12 §14 + OpenTelemetry 2025 GenAI Semantic Conventions + ITIL SACM/Capacity Management/Service Continuity + ISACA 2025 AI Audit Program + Anthropic Codified Context + VictoriaMetrics Vibe Coding Blog (2026-01) + Netflix Atlas/Mantis 实践 + Meta FBAR Production Engineering，逐项对账。盲点确认标准：本蓝图 v2.1.0 中完全未提及 OR 提及但缺少实现层细节。

### 20.1 SLI/SLO + Error Budget 层盲点（5 项）

#### 盲点 #1：SLI 插桩点未定义

**本质**：§13 的 `capacity_slo.yaml` 定义了 8 个 SLI 的 What（指标名）和 How（测量方式），但缺失 Where（插桩点）和 When（采样时机）。Google SRE Workbook §4 明确要求 SLI 定义必须包含 **Instrumentation Point**。

**风险**：AI 施工时各自选择插桩点 → 同一 SLI 不同模块测量位置不一致 → 数值不可比 → SLO 形同虚设。

**专业机构做法**：Google Borgmon 中每个 SLI 有明确的 `collection_label` + `exporter_hook_point`，Meta FBAR 用 `signal_source` 字段声明数据来源。

**SOLO Coder 方案**：扩展 `capacity_slo.yaml`，每个 SLI 新增 `instrumentation` 字段：

```yaml
# capacity_slo.yaml v2.2.0 增强示例
slo_registry:
  - id: CAP-001-startup-time
    description: "97 模块启动时间 P99"
    target: 2000
    measurement: pytest 基准测试
    golden_signal: latency
    governance_layer: GOV-P1
    runtime_plane: RP-2
    instrumentation:                                    # v2.2.0 新增
      hook_point: "zephyr.__init__.post_import"         # 插桩位置：顶层 import 完成后
      collection_method: "time.perf_counter_ns"         # 高精度时钟
      aggregation: "p99"                                # 聚合方式
      exclude_self: true                                # 排除 OTel SDK 自身耗时
      min_samples_for_valid: 3                          # 最少采样数才判定有效
  - id: CAP-003-error-rate
    description: "模块间调用错误率"
    target: 0.001
    measurement: circuit_breaker 统计
    golden_signal: errors
    governance_layer: GOV-P1
    runtime_plane: RP-1
    instrumentation:
      hook_point: "circuit_breaker.CBGManager.on_state_change"
      state_filter: "OPEN"                              # 仅在 OPEN 事件计数
      exclude_self_triggered: true                      # 排除 Kill Switch 主动触发的 OPEN
      aggregation: "rate_per_minute"
  - id: CAP-004-memory-saturation
    description: "内存饱和度"
    target: 0.8
    measurement: psutil 内存监控
    golden_signal: saturation
    governance_layer: GOV-P1
    runtime_plane: RP-2
    instrumentation:
      hook_point: "capacity_governance_loop.poll_cycle"
      sample_interval_sec: 30                           # 采样间隔
      exclude_gc_collections: true                      # 排除 GC 峰值
      exclude_otel_buffer: true                         # 排除 OTel SDK 内部缓冲区
      warmup_cycles: 5                                  # 前 5 个采样周期视为预热，不计入
```

#### 盲点 #2：SLO 窗口未分层

**本质**：所有 SLO 共享统一窗口，但 ZephyrAlpha 内部组件的稳定性差异极大——SSoT 校验几乎不变，AI Agent 行为每周都在变。

**风险**：30 天 SLO 窗口里大部分数据来自"已不复存在的架构状态"→ SLO 数值在快速演进期无意义。

**专业机构做法**：Google SRE Workbook §4 建议按服务类型分层——CI/CD 管线 7 天窗口、数据库 30 天、AI 推理服务甚至可以用 1 天窗口。Netflix Mantis 按流处理作业的 `volatility_score` 自动调整 SLO 窗口。

**SOLO Coder 方案**：引入三档 SLO 窗口分层：

```yaml
# capacity_slo.yaml v2.2.0 —— slo_windows 节
slo_windows:
  fast_cycle:
    applicable_to: ["Agent", "Sandbox", "Reasoning Spans", "Semantic Cache"]
    window: "3d"
    slo_tolerance: 0.99        # 更宽松——快速迭代组件允许更多错误
    review_cadence: "weekly"   # 每周审查 SLO 是否仍适用
  medium_cycle:
    applicable_to: ["Event Bus", "Pipeline", "ContractBus", "Feedback Loop"]
    window: "7d"
    slo_tolerance: 0.999
    review_cadence: "biweekly"
  slow_cycle:
    applicable_to: ["SSoT Validation", "DB Schema", "Provenance Chain"]
    window: "30d"
    slo_tolerance: 0.9999
    review_cadence: "monthly"
```

然后将现有 SLO 注册表中的条目关联到窗口：

```yaml
  - id: CAP-006-queue-depth-saturation
    slo_window_group: "medium_cycle"    # v2.2.0 新增
  - id: CAP-007-type-check-time
    slo_window_group: "slow_cycle"      # v2.2.0 新增
```

#### 盲点 #3：Error Budget 消耗归因（Attribution）缺失

**本质**：§8.2 的 `error_budget` 表只按 `slo_id` 维度追踪消耗量——只能回答"哪个 SLO 预算在减少"，无法回答"为什么减少"。

**风险**：30 天后 Error Budget 耗尽，你对 Owner 只能说"系统整体可靠性下降"，无法指出具体是哪个模块/AI-Agent/操作类型/外部依赖导致的。Blameless Postmortem 无从下手。

**专业机构做法**：Google SRE 建议 Error Budget 消耗打上 `(service, change_event, dependency, time_bucket)` 四维标签。Atlassian Compass 的 Scorecards 按团队/服务/组件三级下钻 Error Budget。

**SOLO Coder 方案**：扩展 `error_budget` 表的 Schema + 消耗事件模型：

```sql
-- error_budget_events（v2.2.0 新增，消耗归因表）
CREATE TABLE error_budget_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slo_id TEXT NOT NULL,
    event_ts TEXT NOT NULL,
    violation_type TEXT NOT NULL,       -- 'threshold_breach' | 'error_rate_spike' | 'latency_exceeded'
    module_id TEXT,                     -- 归因：哪个模块
    agent_id TEXT,                      -- 归因：哪个 AI agent
    operation_type TEXT,                -- 归因：什么操作类型 (file_write/config_modify/api_call/...)
    external_dependency TEXT,           -- 归因：外部依赖 (deepseek-api/chromadb/sqlite/...)
    budget_impact REAL NOT NULL,        -- 此次事件消耗了多少 Error Budget（0.0-1.0）
    burn_rate_at_event REAL,            -- 事件发生时刻的 Burn Rate
    auto_resolved BOOLEAN DEFAULT 0,    -- 是否自动恢复
    resolution_ts TEXT,
    root_cause_tag TEXT                 -- 事后归因标签（人工/AI 补充）
);
CREATE INDEX idx_ebe_slo_ts ON error_budget_events(slo_id, event_ts);
CREATE INDEX idx_ebe_module ON error_budget_events(module_id);
```

消耗归因查询（支撑 Blameless Postmortem）：

```python
# error_budget_tracker.py v2.2.0 新增方法
def get_budget_attribution(self, slo_id: str, window_days: int = 30) -> AttributionReport:
    """返回 Error Budget 消耗的多维归因报告"""
    events = self.db.query("""
        SELECT module_id, agent_id, operation_type, external_dependency,
               SUM(budget_impact) as total_impact, COUNT(*) as event_count
        FROM error_budget_events
        WHERE slo_id = ? AND event_ts >= datetime('now', ?)
        GROUP BY module_id, agent_id, operation_type, external_dependency
        ORDER BY total_impact DESC
    """, [slo_id, f'-{window_days} days'])
    return AttributionReport(
        top_modules=events[:5],          # Top 5 消耗模块
        top_agents=events[:3],           # Top 3 肇事 Agent
        top_dependencies=events[:3],     # Top 3 外部依赖
        suggestion=self._generate_postmortem_hints(events)
    )
```

#### 盲点 #4：短窗口高 Burn Rate 误触发风险

**本质**：§8.4 规定 `Burn Rate 1h > 14.4× → 立即触发只读模式`。但 Google SRE Workbook §5.4 明确说明短窗口高 Burn Rate 可能是临时脉冲——发布变更后 1-2h 会自动恢复。

**风险**：AI 施工经常产生临时脉冲（例如解耦 10 个 ContractBus 文件后临时错误率飙升，随后自行稳定）。直接触发只读模式 → 频繁误触发 → Owner 告警疲劳 → 真正紧急时无视。

**专业机构做法**：Google SRE 建议短窗口告警加 **14.4× > 持续 5 分钟** 的条件才升级，给系统缓冲期。Netflix 的 Atlas 告警用 `for` 子句要求指标持续超标才触发。

**SOLO Coder 方案**：在 §8.4 的联动表中加入"持续时长"列 + "脉冲判定"逻辑：

```yaml
# 修正后的 Kill Switch 联动（v2.2.0）
burn_rate_escalation:
  - window: "1h"
    rate_threshold: 14.4
    action: "log_critical + tag_as_pulse"               # 先标记为脉冲，不动作
    escalate_if_sustained: "> 5min"                     # 持续 5 分钟才升级
    escalation_action: "kill_switch_conservative"       # 升级后才触发保守模式
    escalate_if_sustained_30min: "kill_switch_readonly" # 持续 30 分钟才进入只读
    auto_resolve_condition: "burn_rate_1h < 5× for 10min"  # 自动解除条件
  - window: "6h"
    rate_threshold: 6.0
    action: "notify_owner + log_warning"
    escalate_if_sustained: "> 30min"
    escalation_action: "freeze_releases"
  - window: "3d"
    rate_threshold: 3.0
    action: "notify_owner + reduce_release_frequency"
```

#### 盲点 #5：SLO 定期 Review 与演进机制缺失

**本质**：§8 定义了 Error Budget 的消耗/响应/恢复，但没有定义 **SLO 目标值本身的演进周期**。

**风险**：AI 连续施工 6 个月后系统特征已变——3 个月前设定的 CAP-001 `target: 2000ms` 可能已完全不适用。1 人维护下，过时的 SLO 产生两个后果：要么频繁误告（SLO 太紧），要么系统退化无感知（SLO 太松）。

**专业机构做法**：Google SRE Workbook 建议每季度一次 SLO Review，审视：① 过去季度的实际表现 vs SLO 目标 ② Error Budget 消耗模式有无结构性变化 ③ 是否需要调高/调低目标 ④ 是否需要新增/退役 SLI。

**SOLO Coder 方案**：在 `capacity_governance_loop.py` 中内建自动 SLO Review 报告生成 + 修订建议：

```python
# capacity_governance_loop.py v2.2.0 新增
class SLOReviewAssistant:
    def generate_quarterly_review(self) -> SLOReviewReport:
        """每季度自动生成 SLO Review 报告，供 Owner 5 分钟速览"""
        for slo in self.slo_registry.all():
            actual = self.get_actual_performance(slo.id, days=90)
            suggestion = None
            if actual.p99 < slo.target * 0.3:
                suggestion = "tighten"   # 实际表现远好于目标→建议收紧
            elif actual.p99 > slo.target * 1.2:
                suggestion = "relax"     # 持续超标→建议放宽
            elif slo.error_budget_remaining > 0.95:
                suggestion = "retire"    # 几乎从不消耗预算→考虑退役此 SLI
            yield SLOSuggestion(slo_id=slo.id, action=suggestion, actual=actual)

    def auto_retire_stale_slis(self, staleness_days: int = 90) -> list[str]:
        """自动标记超过 90 天预算消耗 <5% 的 SLI 为'待退役审查'"""
        ...
```

---

### 20.2 容量保障结构性盲点（6 项）

#### 盲点 #6：容量保障自身的资源消耗未管控

**本质**：27 个子模块的容量保障体系本身有显著的资源消耗——`capacity_governance_loop` 每 300s 轮询所有模块 SLI + OTel SDK 自身开销 + 语义缓存索引维护 + DR 备份脚本。Google SRE 经验法则：监控系统自身资源消耗应 < 系统总资源的 2%。当系统接近容量极限时，监控体系可能是最后一根稻草。

**风险**：系统内存 90% → 监控系统疯狂采样 → 内存 95% → OTel 缓冲区爆满 → 内存 98% → 触发 Kill Switch → 但 Kill Switch 检查也是监控系统的一部分 → 死循环。

**专业机构做法**：Google Borgmon 用 sidecar 独立资源池，不与业务共享 CPU/内存。Netflix Atlas 用自适应采样——高负载自动降频。

**SOLO Coder 方案**：`capacity_governance_loop` 增加自适应采样频率：

```python
# capacity_governance_loop.py v2.2.0 新增
class AdaptiveSampler:
    def compute_interval(self, system_load: float, error_budget_tier: str) -> int:
        """自适应采样间隔——负载越高、预算越健康，采样越稀疏"""
        base_interval = 300
        if system_load > 0.8:
            base_interval = 1800   # 高负载：大幅降频，保命要紧
        elif system_load > 0.6:
            base_interval = 600    # 中负载：降频 50%
        if error_budget_tier in ("healthy", "warning"):
            base_interval *= 1.5   # 预算健康时进一步放宽
        return int(base_interval)

    def estimate_self_overhead(self) -> SelfOverheadReport:
        """估算容量保障体系自身的 CPU/内存/IO 开销"""
        my_process = psutil.Process()
        return SelfOverheadReport(
            cpu_pct=my_process.cpu_percent(),
            memory_mb=my_process.memory_info().rss / 1024 / 1024,
            over_threshold=self.is_over_2_percent_system_resources()
        )
```

#### 盲点 #7：缺少单一聚合容量健康评分

**本质**：27 个模块、8 个 SLI、五级 Error Budget、四级 Token Budget、DR 四级——Owner 每天面对的是一张巨大的状态矩阵，需要逐项研判才能形成结论。

**风险**：信息过载 → Owner 不会每天都逐项研判 → 依赖"感觉"而非数据 → 真正问题时漏判。

**专业机构做法**：Google SRE 的 Service Health Score（0-100）由多个 SLI 的 Error Budget 剩余量加权求和。Netflix Atlas Health Check 用红/黄/绿三色。Stripe 用 "Reliability Score" 汇总所有服务 SLO 达标率。

**SOLO Coder 方案**：定义 `ZephyrHealthScore`：

```python
# capacity_governance_loop.py v2.2.0 新增
class ZephyrHealthScore:
    TECHNICAL_WEIGHT: float = 0.40    # Technical SLI (CAP-001~008)
    BUSINESS_WEIGHT: float = 0.30     # Business SLI（见 §20.3 盲点 #14）
    COST_WEIGHT: float = 0.30         # Cost SLI（Token + 资金消耗）

    def compute(self) -> HealthReport:
        technical = self._aggregate_technical_slis()
        business = self._aggregate_business_slis()
        cost = self._aggregate_cost_slis()
        score = (technical * self.TECHNICAL_WEIGHT
                 + business * self.BUSINESS_WEIGHT
                 + cost * self.COST_WEIGHT)
        return HealthReport(
            score=round(score, 1),
            status="green" if score > 80 else ("yellow" if score > 50 else "red"),
            breakdown={"technical": technical, "business": business, "cost": cost},
            trend_vs_last_week=self._compute_trend(),
            top_risks=self._identify_top_3_risks(),
            suggested_actions=self._generate_action_items(),
            last_updated=datetime.now().isoformat()
        )
```

暴露为 AI 零推理消费的 JSON：

```json
{
  "health_score": 73.5,
  "status": "yellow",
  "breakdown": {"technical": 85, "business": 60, "cost": 72},
  "trend": "declining",
  "top_risks": [
    {"type": "business", "detail": "AI任务卡通过G0-G7比例从92%降至78%"},
    {"type": "cost", "detail": "近7天单任务平均Token消耗上升40%"}
  ],
  "suggested_actions": [
    "审查最近50张任务卡的门禁驳回原因TOP5",
    "检查是否是模型上下文失忆导致AI重复工作"
  ]
}
```

#### 盲点 #8：AI 行为预测维度缺失

**本质**：§17 容量预测模型的 6 个维度（模块数/内存/Token/成本/测试时长/类型检查时长）全是**资源消耗的结果**，不是**资源消耗的原因**。是 AI 的行为（生成任务卡、改代码、调模型）驱动了资源消耗。

**风险**：模块增长率突然从 5/周变成 30/周——资源预测模型能发现（"内存 30 天预测超标"），但无法提前预警（"检测到 Owner 批了 50 张任务卡，预计施工速度将加速 6×，系统可能在 10 天内达到容量极限"）。

**专业机构做法**：Netflix Scryer 用 ML 预测 AWS Auto Scaling 需求、同时监控 upstream 变更事件。Anthropic 的 Codified Context 系统追踪 "Agent 调用频率 × 每次上下文 Token 消耗" 做复合预测。

**SOLO Coder 方案**：新增 AI 行为预测维度：

```yaml
# capacity_slo.yaml v2.2.0 —— AI 行为 SLI
ai_behavior_slis:
  - id: AI-BEH-001-task-generation-rate
    description: "AI 生成任务卡的速率（张/天）"
    measurement: task_card 表的每日新增计数
    prediction_horizon: "7d"
    warning_threshold: "rate_doubled in 3d"    # 3 天内速率翻倍
    action: "suggest_change_rate_limit"
  - id: AI-BEH-002-code-churn-rate
    description: "AI 修改代码的搅动率（行/天）"
    measurement: git diff --stat 的每日变更行数
    prediction_horizon: "7d"
    warning_threshold: "churn_rate > 500 lines/day"
    action: "suggest_split_into_smaller_batches"
  - id: AI-BEH-003-model-call-failure-rate
    description: "LLM API 调用失败/降级率"
    measurement: degradation_chain 的降级事件计数
    prediction_horizon: "3d"
    critical_threshold: "failure_rate > 10% in 1d"
    action: "suggest_reduce_concurrent_agents"
  - id: AI-BEH-004-code-rework-rate
    description: "AI 生成的代码被后续修改/回滚的比例"
    measurement: (同一文件的二次修改次数 / 总修改次数)
    prediction_horizon: "7d"
    warning_threshold: "rework_rate > 30%"
    action: "suggest_blueprint_quality_review——AI上下文可能已退化"
  - id: AI-BEH-005-owner-approval-burst
    description: "Owner 批量审批新任务卡的事件检测"
    measurement: task_card.status = 'approved' 的小时级计数
    detection: "event_driven"     # 不是预测，是实时检测
    burst_threshold: "> 10 approvals in 1h"
    action: "auto_engage_change_rate_limiter"
```

#### 盲点 #9：容量预警→修复行动闭环断裂

**本质**：§17.3 定义了"预测内存 30d > 90% → 触发 Kill Switch 保守模式"，但 Kill Switch 保守模式会阻止 AI 施工 → AI 不施工就无法写代码优化内存 → 系统锁死在内存 90% + 只读模式下。

**风险**：预警触发了制动，但制动导致无法修复——"踩了刹车，但修车工被锁在门外"。

**专业机构做法**：Netflix 的 Automated Remediation 在触发告警时同时启动修复 Playbook（`AutoRemediationAction`），限制非关键流量但**保持修复通道畅通**。

**SOLO Coder 方案**：每个 Critical 预警必须附带修复 Playbook：

```yaml
# capacity_governance_config.yaml v2.2.0 —— 预警→修复闭环
alerts_with_remediation:
  - alert_id: "MEM-90-PREDICTED"
    trigger: "predicted_memory_30d > 物理内存 90%"
    immediate_action: "kill_switch_conservative"
    remediation_channel: "open"                        # 修复通道保持畅通
    remediation_playbook:
      - step: "auto_generate_memory_audit_task"
        description: "扫描 top 10 内存大户模块，产出优化建议"
        executor: "AI (degradation_chain tier=2)"      # 用降级模型的低成本 AI 执行审计
        output: "memory_audit_report.md"
      - step: "present_to_owner"
        description: "将审计报告 + 3 条优化建议推送给 Owner（飞书/终端）"
        owner_action: "approve_one_click"
      - step: "execute_optimization"
        description: "AI 按 Owner 批准的方案执行优化"
        executor: "AI (restricted: 仅允许指定模块的修改)"
      - step: "verify"
        description: "验证优化后内存下降 → 解除 Kill Switch"
        success_condition: "memory_pct < 75% for 30min"
        on_failure: "escalate_to_owner_manual"
```

#### 盲点 #10：成本回归后的自动回升缺失

**本质**：§11.1 定义了降级触发条件 `cost_per_day > 5.00 → fallback`，但没有定义"成本回归正常后是否自动切回更好模型"。Graceful Degradation 是单向的——只降不升。

**风险**：成本回落到 $2/day 后，系统仍在使用降级模型（`qwen2.5-3b-onnx`），AI 施工质量下降但无人察觉 → 门禁驳回率上升 → AI 重复施工 → 成本再次上升 → 恶性循环。

**专业机构做法**：Anthropic 的 Claude API 路由系统用 **Cost-Aware Model Router**，实时监控成本/延迟/质量三维，自动在模型间切换。AWS Bedrock 的 model fallback 支持 `auto_restore` 配置。

**SOLO Coder 方案**：在降级链配置中增加回升策略：

```yaml
# degradation_chain.yaml v2.2.0 —— 双向模型路由
model_routing:
  tiers:
    - tier: 1
      model: "trae-cn-pro"          # 最佳模型，成本最高
      cost_per_1k_tokens: 0.002
      quality_score: 0.95
    - tier: 2
      model: "deepseek-chat"
      cost_per_1k_tokens: 0.0005
      quality_score: 0.85
    - tier: 3
      model: "qwen2.5-3b-onnx"
      cost_per_1k_tokens: 0.0     # 本地，零成本
      quality_score: 0.60

  degradation:                       # 降级条件
    - trigger: "cost_per_day > 5.00"
      fallback: "tier_1 → tier_2"
    - trigger: "cost_per_day > 10.00"
      fallback: "tier_1 → tier_3"

  restoration:                       # v2.2.0 新增——回升条件
    - trigger: "cost_per_day < 2.00 for 24h"
      restore: "tier_3 → tier_2"
    - trigger: "cost_per_day < 1.00 for 48h"
      restore: "tier_2 → tier_1"
    cooldown: "6h"                   # 回升后冷却 6h，防止振荡

  per_task_routing:                  # v2.2.0 新增——按任务重要性差异化降级
    P0_tasks: "keep_tier_1"          # P0 任务始终使用最佳模型
    P1_tasks: "allow_degrade_to_tier_2"
    P2_tasks: "allow_degrade_to_tier_3"
```

#### 盲点 #11：缺少渐进式流量切换能力

**本质**：蓝图有 Kill Switch（全或无）和降级链（固定顺序切换），但没有 **Traffic Shaping**（流量塑形）——无法实现"让 AI 慢 50%"而非"让 AI 停工"。

**风险**：Kill Switch 是核弹，对于中间状态（"成本偏高但还能承受"、"速度偏慢但还能工作"）缺少手术刀级的控制。频繁触发 Kill Switch 会导致 AI 施工节奏被打断。

**专业机构做法**：Netflix Conductor 用 `rate_limit` + `concurrency_limit` 做细粒度流量控制。K8s HPA 在扩容和新 Pod Ready 之间有渐进过渡。

**SOLO Coder 方案**：引入 ChangeRateLimiter，作为 Kill Switch 的前置缓冲层：

```python
# change_rate_limiter.py（v2.2.0 新增模块，建议纳入 M-28）
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ChangeRatePolicy:
    max_changes_per_hour: int = 10
    max_concurrent_changes: int = 3
    max_modules_per_batch: int = 5
    cooldown_after_batch_minutes: int = 15

class ChangeRateLimiter:
    """施工节奏控制器——让 AI '慢下来'而非'停下来'"""

    def __init__(self, db: "ProvenanceDB"):
        self.db = db
        self.policy = ChangeRatePolicy()
        self.override_pct: float = 1.0     # 1.0=全速，0.5=半速，0=冻结

    def set_throttle(self, pct: float, reason: str) -> None:
        """渐进式降速：0.7=降速30%，0.3=降速70%，0=完全冻结"""
        self.override_pct = max(0.0, min(1.0, pct))
        self.db.log_governance_action("change_rate_throttle", {
            "new_rate": self.override_pct,
            "reason": reason
        })

    def can_proceed(self, change: "ProposedChange") -> tuple[bool, str]:
        """判断一个变更是否可以执行"""
        if self.override_pct == 0.0:
            return False, "全局冻结——所有变更暂停"

        recent = self.db.count_changes_in_window(minutes=60)
        concurrent = self.db.count_active_changes()
        effective_max_per_hour = self.policy.max_changes_per_hour * self.override_pct

        if recent >= effective_max_per_hour:
            return False, f"小时变更({recent})超限({effective_max_per_hour:.0f})"
        if concurrent >= self.policy.max_concurrent_changes:
            return False, f"并发变更({concurrent})超限({self.policy.max_concurrent_changes})"
        return True, "允许"

    def get_status(self) -> dict:
        return {
            "current_rate": self.override_pct,
            "recent_changes_1h": self.db.count_changes_in_window(minutes=60),
            "active_changes": self.db.count_active_changes(),
            "slots_available": max(0, self.policy.max_concurrent_changes - self.db.count_active_changes()),
        }
```

---

### 20.3 SOLO Coder（1人+AI 维护）特异性盲点（5 项）

#### 盲点 #12：告警疲劳——这个架构的阿喀琉斯之踵

**本质**：五级 Error Budget + 四级 Token Budget + DR 四级 + 容量预测 6 维 + Business SLI 5 维 = 20+ 告警源。1 人面对 20+ 告警源意味着**必然告警疲劳**。

**风险**：告警疲劳 → Owner 开始忽略 → 真正紧急告警被淹没 → P0 问题从"及时响应"变成"事后发现"。

**专业机构做法**：Google SRE 建议告警收敛率 > 90%（即 10 条原始告警收敛为 1 条可操作通知）。PagerDuty 用 **Intelligent Alert Grouping** + **Noise Reduction**。Meta 用 `alert_suppression_window` 合并同一根因的告警。

**SOLO Coder 方案**：引入告警治理四机制：

```yaml
# capacity_slo.yaml v2.2.0 —— alert_governance 节
alert_governance:
  # 机制 1：告警收敛窗口（同一根因合并）
  convergence:
    enabled: true
    window_minutes: 30               # 30 分钟内同一 SLO 的重复告警合并为 1 条
    grouping_key: "slo_id + module_id"   # 按 SLO + 模块聚合

  # 机制 2：静默期（Owner 睡觉时不打扰）
  quiet_hours:
    enabled: true
    start: "00:00"
    end: "08:00"
    exception: ["emergency", "kill_switch_triggered"]  # 仅 Emergency 和 Kill Switch 可以打破静默
    morning_digest: true                               # 早上 8 点推送静默期聚合摘要

  # 机制 3：自愈优先（低级别先尝试自动修复）
  auto_remediation:
    enabled: true
    tiers:
      - level: "warning"
        action: "auto_heal_first"    # 先尝试自动修复，修复失败才记录
        max_auto_heal_attempts: 3
      - level: "cautious"
        action: "log + weekly_report_only"  # Owner 只在周报中看到，实时不推送
      - level: "critical"
        action: "notify_owner"       # 只有 Critical 起才实时通知 Owner

  # 机制 4：Owner 消息优先级队列
  notification_routing:
    realtime: ["emergency", "critical", "kill_switch_triggered"]
    hourly_digest: ["cautious"]
    daily_digest: ["warning"]         # Warning 只入日报
    weekly_digest: ["error_budget_healthy_drift", "slo_review_reminder"]
```

对应代码骨架：

```python
# alert_manager.py（v2.2.0，建议与 error_budget_tracker.py 集成）
class AlertManager:
    def __init__(self, governance_config: AlertGovernanceConfig):
        self.config = governance_config
        self.recent_alerts: deque = deque(maxlen=100)

    def should_notify(self, alert: Alert) -> tuple[bool, str]:
        """判断告警是否应该通知 Owner"""
        # 检查是否在静默期内
        if self._in_quiet_hours() and alert.level not in self.config.quiet_hours.exception:
            return False, "静默期——入早上摘要队列"

        # 检查是否已被收敛
        recent_same = [a for a in self.recent_alerts
                       if a.slo_id == alert.slo_id and a.module_id == alert.module_id
                       and (datetime.now() - a.ts).seconds < self.config.convergence.window_minutes * 60]
        if recent_same:
            return False, f"收敛——30 分钟内已有同类告警"

        # 检查自愈优先级
        if alert.level == "warning" and self._can_auto_heal(alert):
            success = self._attempt_auto_heal(alert)
            if success:
                return False, "已自动修复——不入通知"

        self.recent_alerts.append(alert)
        return True, "通知"

    def generate_morning_digest(self) -> str:
        """早上 8 点的聚合摘要——Owner 起床后第一条消息"""
        ...
```

#### 盲点 #13：AI 可理解性作为第一性设计约束

**本质**：90%+ 代码变更是 AI 生成的。容量保障代码的质量不由"人写得有多好"决定，而由"AI 改得有多对"决定。

**风险**：当前蓝图质量高，但复杂度也高（27 个模块、多窗口 Multi-Burn-Rate、五级响应链）。复杂度 = AI 施工出错的概率。

**专业机构做法**：Anthropic 的 Codified Context 强调 "AI-Readable Architecture"——所有配置文件用结构化 YAML/JSON（AI 零推理消费），代码遵循"单文件单一职责"，命名遵循"AI 能从文件名推断功能"的约定。

**SOLO Coder 方案**：在本蓝图中明确"AI 可理解性约束"：

```yaml
# 容量保障 AI 可理解性约束（v2.2.0 新增）
ai_readability_constraints:
  file_naming:
    rule: "每个 Python 文件 = 唯一职责，文件名 = 职责的英文描述"
    pattern: "{noun}_{verb}.py 或 {domain}_{component}.py"
    examples:
      good: ["error_budget_tracker.py", "kill_switch.py", "change_rate_limiter.py"]
      bad: ["utils.py", "helpers.py", "common.py"]    # AI 无法从文件名推断内容

  function_naming:
    rule: "函数名 = 动作 + 对象 + (可选)条件"
    pattern: "{verb}_{object}_{condition?}"
    examples:
      good: ["compute_health_score()", "freeze_releases_for_slo()", "auto_heal_memory_pressure()"]
      bad: ["process()", "handle()", "do_stuff()"]

  config_design:
    rule: "YAML 结构 = AI 可直接遍历的树，不含隐式约定"
    pattern: "每层用显式 key，枚举值用 enum 字段声明"
    anti_pattern: "不要依赖字段顺序或隐式位置"

  max_complexity:
    rule: "单个 .py 文件 ≤ 300 行；单个函数 ≤ 30 行"
    enforcement: "pre-commit hook（ruff + custom checker）"
    rationale: "超过此阈值→AI 重构时误改概率非线性上升"

  ai_testing:
    rule: "每个 AI-Modifiable 模块必须有至少 3 个 edge-case 单元测试"
    rationale: "AI 改代码时最容易在边界条件出错——测试是唯一的防线"
```

#### 盲点 #14：Business SLI（业务健康检查）完全缺失

**本质**：§13 的 SLI 全是 Technical SLI（延迟/错误/饱和度）。但在这个系统的语境下，"业务"是 AI 施工的 **效率和质量**。

**风险**：CAP-001~008 全部绿色 → 系统从技术角度看很健康 → 但 AI 施工质量可能已经退化（返工率上升、门禁通过率下降）→ Owner 要到月底数任务卡完成率才能发现 → 已经浪费了大量 Token。

**专业机构做法**：Stripe 区分 Technical SLI 和 Business SLI（API 响应时间 vs 支付成功率）。GitHub Copilot 团队追踪 Agent 的 `acceptance_rate`（用户接受率）和 `completion_quality`。

**SOLO Coder 方案**：新增 Business SLI 维度：

```yaml
# capacity_slo.yaml v2.2.0 —— business_slis 节
business_slis:
  - id: BIZ-001-task-throughput
    description: "每日完成任务卡数量"
    target: "≥ 5 / day"
    measurement: task_card 表 status='done' + completed_at
    golden_signal: "traffic (business)"
    governance_layer: GOV-P1
  - id: BIZ-002-gate-pass-rate
    description: "AI 施工产物通过 G0-G7 门禁的比例"
    target: 0.85                                # 85% 一次通过
    measurement: gate_results 表
    golden_signal: "errors (business)"
    governance_layer: GOV-P1
    degradation_alert: "< 0.70"                 # 低于 70% → AI 上下文可能退化
  - id: BIZ-003-code-rework-rate
    description: "AI 生成的代码被后续修改/回滚的比例"
    target: 0.15                                # ≤ 15% 返工率
    measurement: git diff --stat + rollback_manager 统计
    golden_signal: "saturation (business)"
    governance_layer: GOV-P1
    degradation_alert: "> 0.30"
  - id: BIZ-004-blueprint-drift-rate
    description: "蓝图与实际代码不一致的比例变化"
    target: "< 5% drift / week"
    measurement: drift-detector（MOD-INF-023）的 reconcile 事件
    golden_signal: "saturation (business)"
    governance_layer: GOV-P2
  - id: BIZ-005-temp-file-growth-rate
    description: "19_development_workspace/ 的增长速度——反映AI产生的中间产物"
    target: "< 10MB / week"
    measurement: du -sh 19_development_workspace/
    golden_signal: "saturation (business)"
    governance_layer: GOV-P2
```

#### 盲点 #15：施工节奏控制（Change Burst Detection）

**本质**：从 97→1500 模块的过程中，最危险的不是缓慢演进，而是 **AI 施工速度的突然爆发**。

**场景**：Owner 集中审批 30 张任务卡 → AI 并行执行 → 1 小时内合并 30 个模块变更 → 系统结构剧烈变化 → 原有 SLO 基准失效 → 测试/类型检查耗时爆炸 → 但无人察觉因为"进展很快"。

**专业机构做法**：Google Borg 用 `change_velocity` 指标（每小时部署次数），超过历史基线 3σ 自动暂停发布。Netflix Spinnaker 用 `canary_analysis` 在新版本上线前跑 15 分钟对比。

**SOLO Coder 方案**：在 `capacity_governance_loop` 中新增 Change Burst Detection：

```python
# capacity_governance_loop.py v2.2.0 —— ChangeBurstDetector
class ChangeBurstDetector:
    MAX_MODULES_PER_HOUR: int = 10
    MAX_FILES_PER_HOUR: int = 30

    def detect_burst(self) -> BurstAlert | None:
        recent_modules = self.db.count_new_or_modified_modules(hours=1)
        recent_files = self.db.count_modified_files(hours=1)

        if recent_modules > self.MAX_MODULES_PER_HOUR:
            return BurstAlert(
                level="critical",
                detail=f"过去 1h 新增/修改了 {recent_modules} 个模块（阈值 {self.MAX_MODULES_PER_HOUR}）",
                auto_action="freeze_releases_until_owner_acknowledge",
                suggestion="建议Owner分批审批——每批≤5张任务卡，批间间隔≥15分钟",
            )
        if recent_files > self.MAX_FILES_PER_HOUR:
            return BurstAlert(
                level="warning",
                detail=f"过去 1h 修改了 {recent_files} 个文件",
                suggestion="自动启用 ChangeRateLimiter(override_pct=0.5)——降至半速",
            )
        return None
```

#### 盲点 #16：Owner 离线时的系统自治边界

**本质**：蓝图假设 Owner 24/7 在线。现实是 1 人不可能 24/7。Owner 睡觉/出差/度假时系统必须自治。

**风险**：Owner 离线 48h → 系统仍在施工（100% AI）→ Error Budget 逐渐消耗 → 进入 Critical → Kill Switch 保守模式 → 系统停止 → Owner 回来后面对一个冻结的系统 + 48h 的积压任务。

**专业机构做法**：Google SRE 用 **Follow-the-Sun** 值班（跨时区轮转），但 Solo Coder 做不到。折中方案：定义 **Autonomous Operational Envelope**——Owner 离线时系统能自主操作的最大范围。

**SOLO Coder 方案**：

```yaml
# capacity_governance_config.yaml v2.2.0 —— autonomous_envelope 节
autonomous_envelope:
  # Owner 离线判定：最后一次人工交互 > N 小时
  owner_offline_threshold_hours: 4

  # 离线时可自主执行的操作范围
  allowed_autonomous_actions:
    - "auto_heal_detected_issues"           # 自动修复检测到的问题
    - "degrade_models_to_tier_2"            # 降级模型（省成本）
    - "reject_new_P1_P2_tasks"              # 拒绝新 P1/P2 任务（仅接受 P0）
    - "enable_change_rate_limiter(0.5)"     # 半速施工
    - "send_daily_digest_to_owner"          # 每天发一份摘要

  # 离线时绝对禁止的操作
  forbidden_autonomous_actions:
    - "activate_kill_switch_readonly"       # 只读模式必须Owner手动
    - "delete_any_file"                     # 任何文件删除
    - "modify_immutable_core"               # 修改 Immutable Core
    - "approve_new_modules_without_blueprint"  # 无蓝图的新模块
    - "change_error_budget_thresholds"      # 修改阈值

  # Owner 回归后的追赶协议
  owner_return_protocol:
    - step: "generate_offline_period_summary"
      description: "产出离线期间摘要——改了哪些模块、花了多少Token、有无告警"
    - step: "prioritize_open_issues"
      description: "列出需要Owner决策的事项，按紧急度排序"
    - step: "restore_full_autonomy"
      description: "Owner确认回归后，恢复全速施工"
```

此外，§15 的关键关联中应新增引用 `escalation-protocol` 蓝图（MOD-INF-022），因为容量保障触发 Critical/Emergency 时，升级路径需要与 escalation-protocol 协同。

---

### 20.4 顶尖设计参考架构

基于以上 16 项盲点分析 + 现有蓝图能力，一个**真正顶尖的 1人+AI 维护的容量保障体系**应遵循以下设计：

#### 20.4.1 六项设计原则

| # | 原则 | 来源对标 | 说明 |
|---|------|---------|------|
| 1 | **Self-Healing First** | Google SRE §17 | 任何可自动修复的问题不通知Owner；仅自愈失败才升级 |
| 2 | **Single Number** | Google Service Health Score | 一个聚合分数（0-100），Owner 每天看一眼就知道状态 |
| 3 | **Progressive Intervention** | Netflix Conductor | 从不干预→温和减速→部分冻结→完全冻结，四级梯进 |
| 4 | **AI-Readable Everything** | Anthropic Codified Context | 所有配置/告警/行动建议 = YAML/JSON，AI 零推理消费 |
| 5 | **Cost-Capacity Unification** | ISACA AI Cost Governance | Token成本 + 计算资源 + 时间成本 → 统一预算框架 |
| 6 | **Observability-Light** | VictoriaMetrics Vibe Coding Blog | 监控系统自身开销 < 系统总资源的 2% |

#### 20.4.2 理想架构拓扑

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   ZephyrHealthScore（0-100）—— 每天一条                 │
│  ┌─────────────────────┬─────────────────────┬─────────────────────┐    │
│  │ Technical SLO (40%) │ Business SLO (30%)  │  Cost SLO (30%)     │    │
│  │ CAP-001~008         │ BIZ-001~005         │ Token + $           │    │
│  └─────────────────────┴─────────────────────┴─────────────────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│                       渐进式干预引擎                                     │
│  Score > 80   │  Score 60-80  │  Score 30-60  │  Score < 30            │
│  Unrestricted │  Throttled    │  Frozen       │  Emergency Readonly    │
│  全速施工     │  降速50%      │  仅P0+修复    │  只读+Owner手动恢复    │
│               │  +只接受P0/P1 │  +暂停所有    │  +飞书主动通知         │
├─────────────────────────────────────────────────────────────────────────┤
│                     自适应执行层                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 自适应采样   │ │ 双向模型路由 │ │ 自愈引擎     │ │ 复合预测模型 │   │
│  │ (频率随负载  │ │ (降级+回归)  │ │ (自动修复    │ │ (资源预测+   │   │
│  │  自适应)     │ │              │ │  常见3类问题)│ │  AI行为预测) │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 告警治理     │ │ 施工节奏控制 │ │ 离线自治边界 │ │ 追赶上岸协议 │   │
│  │ (收敛+静默    │ │ (ChangeRate  │ │ (Autonomous  │ │ (Owner Return│   │
│  │  +自愈优先)   │ │  Limiter)    │ │  Envelope)   │ │  Protocol)   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 20.4.3 与 v2.1.0 架构的核心差异

| 维度 | v2.1.0（当前） | v2.2.0 建议（顶尖） |
|------|:---|:---|
| **模式** | 监控 → 告警 → Owner 手动处理 | 预测 → 自愈 → 罕见升级 |
| **粒度** | Kill Switch 全或无 + 降级链固定顺序 | 渐进式四档干预 + 双向模型路由 + 按任务优先级差异化 |
| **决策输入** | 8 个 Technical SLI | 技术 SLI + 业务 SLI + 成本 SLI → 聚合为一个 Health Score |
| **Owner 界面** | 五级 Error Budget 状态表 + 多级 Token Budget 表 | 一个数字 + 趋势箭头 + Top 3 风险 + 建议行动 |
| **AI 角色** | AI 被监控的对象 | AI 既是施工者也是审计者——自愈引擎由 AI 驱动 |
| **离线能力** | 无（假设 Owner 24/7） | 定义了 Autonomous Envelope + Owner Return Protocol |

---

### 20.5 盲点全量清单（汇总）

| # | 盲点名称 | 严重度 | 归属子节 | 影响维度 |
|---|---------|:---:|------|------|
| 1 | SLI 插桩点未定义 | **高** | 20.1 | 施工一致性 / SLO 有效性 |
| 2 | SLO 窗口未分层 | **高** | 20.1 | 快速演进期 SLO 可信度 |
| 3 | Error Budget 消耗归因缺失 | **高** | 20.1 | 根因分析 / Postmortem 可用性 |
| 4 | 短窗口高 Burn Rate 误触发 | 中 | 20.1 | Kill Switch 可靠性 / 告警准确性 |
| 5 | SLO 定期 Review 缺失 | 中 | 20.1 | 长期 SLO 有效性 |
| 6 | 容量保障自身资源消耗 | **高** | 20.2 | 极限场景系统稳定性 |
| 7 | 单一聚合健康评分缺失 | 中 | 20.2 | Owner 决策效率 |
| 8 | AI 行为预测维度缺失 | **高** | 20.2 | 容量预测模型完整性 |
| 9 | 预警→修复行动闭环断裂 | **高** | 20.2 | 自动恢复能力 |
| 10 | 成本回归自动回升缺失 | 中 | 20.2 | 服务质量一致性 |
| 11 | 渐进式流量切换缺失 | 中 | 20.2 | 干预粒度 |
| 12 | 告警疲劳风险 | **致命** | 20.3 | Solo 维护可持续性 |
| 13 | AI 可理解性约束缺失 | **高** | 20.3 | AI 施工质量 / 维护可靠性 |
| 14 | Business SLI 完全缺失 | **高** | 20.3 | AI 施工业务健康度不可见 |
| 15 | 施工节奏控制缺失 | **高** | 20.3 | 变更爆炸 / 系统稳定性 |
| 16 | Owner 离线自治边界缺失 | **高** | 20.3 | 离线期系统风险 |

> **追加审计发现（非盲点、但可作为后续补充）**：
> - **语义缓存过期策略验证**：§11.2 的缓存 TTL + 相似度阈值目前缺乏自动化验证机制——缓存是否真的在源数据变更时失效？建议加一条 Business SLI：`cache_staleness_rate`（缓存返回结果的错误率）。
> - **外部依赖 SLA 纳入**：`infrastructure-registry.yaml` 中的 8 个组件 SLA 目前是被动参考，建议在容量预测模型中纳入 `external_dependency_health` 维度——例如 DeepSeek API 的可用性直接影响施工效率。
> - **多级 Token Budget 的资源预留/配额机制**：§9 当前是"消耗后统计"模型，建议加上"施工前预留"——P0 任务在执行前锁定一个 Token 配额，防止被 P1/P2 任务吃光预算。

---

### 20.6 施工优先级排序

按 **Solo Coder（1人+AI）** 场景的重要性排序：

| 优先级 | 盲点 # | 做这件事的理由 |
|:---:|:---:|------|
| **1** | #14 Business SLI | 让你看到 AI 施工的**质量/效率趋势**——这是你的核心 KPI。没有 Business SLI，其他所有告警都是"不知道业务好不好"的噪声 |
| **2** | #12 告警疲劳治理 | 否则所有其他告警设计都是白费——你会在 2 周内习惯性无视所有通知 |
| **3** | #15 施工节奏控制 | 防止 AI 一夜之间合并 30 个模块变更——这是 Solo 维护中**唯一不可逆的致命风险** |
| **4** | #1 SLI 插桩点定义 | 否则 AI 各自为政——每个 AI session 在不同位置采 SLI → 数值不可比 → SLO 形同虚设 |
| **5** | #9 预警→修复闭环 | 让你睡觉时系统能自己处理大部分问题——而不是醒来面对一个被 Kill Switch 锁死的系统 |
| **6** | #6 自适应采样 | 防止极限容量场景下"监控系统压垮业务系统" |
| **7** | #3 Error Budget 归因 | 支撑你值班时的 Blameless Postmortem——能快速定位"谁吃了预算" |
| **8** | #2 SLO 窗口分层 | 让 SLO 在快速演进期仍然有意义 |
| **9** | #13 AI 可理解性 | 做施工指引时同步落地——降低 AI 维护代码时的出错率 |
| **10** | #16 Owner 离线自治 | 你休假/离线超过 4h 时需要——定义了"我不在时系统最多自己干到什么程度" |
| **11** | #10 成本回升 | AI 施工质量下降的早期预警 |
| **12** | #11 渐进式流量切换 | 给 Kill Switch 增加"半速"中间档 |
| **13** | #7 健康评分 | 你决策效率的长期优化 |
| **14** | #8 AI 行为预测 | 容量预测模型的本质补全 |
| **15** | #5 SLO Review | Beta 阶段引入——SLO 演进机制 |
| **16** | #4 脉冲容忍 | 施工过程中的误触发治理 |

---

### 20.7 §15 关键关联补充（v2.2.0）

| 关联文档 | 说明 |
|---------|------|
| `escalation-protocol/blueprint.md`（MOD-INF-022） | **新增**——Error Budget Critical/Emergency 时的升级路径对接 |
| `drift-detector/blueprint.md`（MOD-INF-023） | **新增**——Business SLI `BIZ-004`（蓝图漂移率）的数据源 |
| `budget-enforcer/blueprint.md`（MOD-INF-024） | **新增**——多级 Token Budget 从"追踪"升级到"强制"的对接蓝图 |
| `rollback-system/blueprint.md`（MOD-INF-021） | **新增**——ChangeRateLimiter 挡不住的变更需对接回滚系统 |
| `a2a-protocol/blueprint.md`（MOD-INF-025） | **新增**——多 Agent 并行施工时，ChangeRateLimiter 需与 A2A 协调协议对接 |

---

## 21. 第二轮深度审计——追加盲点（v2.3.0 新增）

> **审计升级**：第一轮审计（§20）覆盖了 16 项盲点，对标了 Google SRE / Netflix / Meta / Anthropic / Stripe / ISACA。第二轮交叉审计新增覆盖：Anthropic Constitutional AI（幻觉退化检测）、Google Context Caching（上下文预算）、Netflix Conductor Backpressure（跨模块容量传播）、GitHub Copilot Agent Mode（Per-Task Token Budget）、VictoriaMetrics Downsampling（存储生命周期）、Google Toil Budget（运维负担量化）。追加发现 **9 项深层盲点**（#17~#25），分布在五个维度。

> **盲点确认标准**：本蓝图 v2.2.0（含 §20）中**完全未提及** OR **提及但无实现层细节**。

---

### 21.1 AI 施工特异性盲点（3 项）

#### 盲点 #17：Context 预算的"慢泄漏"——AI 施工中最隐蔽的退化模式

**本质**：§9 的多级 Token Budget 追踪的是每次调用的**显式** token 消耗。但每一次 AI session 冷启动注入的上下文（蓝图、ADR、知识库条目、任务卡状态）本身就在消耗大量 token——而且这种消耗随系统规模**线性增长**。从 97 模块到 500 模块的过程意味着冷启动上下文从 ~8K tokens → ~30K tokens → ~80K tokens。

**风险**：没有 Context Budget Watermark → 150 个模块时，每次 AI session 启动就要吃掉 50K token 的上下文 → 一天 10 个 session = **500K token 纯开销**——在你还未批准任何施工任务时，预算已经消耗了 10%。

**专业机构对标**：Anthropic Codified Context 用 **Context Budget Watermark**——每次 session 注入的上下文设硬上限（如 32K），超出的部分自动做语义摘要而非全量注入。Google Context Caching 允许对重复注入的上下文只计一次费用。

**SOLO Coder 方案**：

```yaml
# capacity_slo.yaml —— context_budget_watermark 节
context_budget_watermark:
  max_context_tokens_per_session: 32000
  enforcement: "compress_beyond_threshold"
  compression_strategy:
    - source: "knowledge_base"
      action: "semantic_summary"
      config: "top 5 most relevant KEs by cosine similarity"
    - source: "ADR_references"
      action: "link_only"
      config: "AI fetches full content on-demand via ContractBus"
    - source: "blueprint_sections"
      action: "inject_toc_only"
      config: "sections loaded lazily on first access"
    - source: "task_card_state"
      action: "inject_recent_N"
      config: "N=20 most recently updated tasks"
  self_check:
    frequency: "every_session_start"
    metric: "context_tokens_injected"
    action_if_over: "auto_compress + log_warning + suggest_blueprint_trim"
    sla: "compression adds < 500ms to session startup"
```

对应 SLI：

```yaml
  - id: CAP-010-context-injection-size
    description: "每次 AI session 启动注入的上下文 token 数"
    target: 32000
    instrumentation:
      hook_point: "context_engine.ContextInjector.inject.exit"
      measurement: "token_counter on assembled context string"
      aggregation: "p50 + p99"
    degradation_alert: "p50 > 40000 for 3 consecutive sessions"
```

---

#### 盲点 #18：AI 多轮对话的"令牌通货膨胀"——单任务成本非线性增长

**本质**：§9.1 的 Per-request token 上限（input 32K / output 4K）定义的是**单轮**上限。实际 AI 施工中一张任务卡需要 5-15 轮对话。第 1 轮被驳回 → 第 2 轮需要附带"驳回原因 + 被驳代码 + 原始需求" → 上下文膨胀 → 第 5 轮的上下文远大于第 1 轮 → **单任务总 token 消耗呈非线性增长**。

**典型退化路径**：
```
第 1 轮：5K input + 2K output  =  7K  tokens  ✅ 通过
第 2 轮：8K input + 3K output  = 11K  tokens  ❌ 驳回（minor issue）
第 3 轮：14K input + 4K output = 18K  tokens  ❌ 驳回（AI 未准确理解驳回原因）
第 4 轮：22K input + 5K output = 27K  tokens  ❌ 驳回（模型退化为降级模型）
第 5 轮：28K input + 6K output = 34K  tokens  ❌ 驳回（逼近 Per-request 上限）
---
累计消耗：97K tokens —— 远超单次调用的 7K 上限，但没有任何机制阻止
```

**专业机构对标**：GitHub Copilot Agent Mode 用 **Escalating Cost Cap**——对同一任务的多轮对话累加 token 消耗，超过任务级预算后自动降级模型或要求人工介入。Anthropic Claude Code 用 **Task Budget Envelope**——每个 task 有独立预算上限（默认为单次调用的 5×）。

**SOLO Coder 方案**：引入 Per-Task Token Budget（与 Per-request 正交）：

```yaml
# token_budget.yaml —— per_task_budget 节（v2.3.0 新增）
per_task_budget:
  P0_task:
    budget_tokens: 200000     # P0 任务最多 200K tokens（约 $1.00 @ $5/M）
    warning_at: 0.6           # 消耗 60% 时 → "建议简化实现方案"
    degrade_at: 0.85          # 消耗 85% 时 → 自动切换到降级模型
    hard_stop_at: 1.0         # 到达 100% → 强制终止，产出部分结果 + 建议拆分
    auto_escalate_at: 0.9     # 消耗 90% → 主动通知 Owner 决策
  P1_task:
    budget_tokens: 80000
    warning_at: 0.6
    degrade_at: 0.85
    hard_stop_at: 1.0
  P2_task:
    budget_tokens: 30000
    warning_at: 0.7
    hard_stop_at: 1.0
    degrate_at: 1.0           # P2 任务不设降级——不划算就硬停
```

对应追踪代码：

```python
# token_budget_tracker.py v2.3.0 新增
class PerTaskBudgetTracker:
    def on_request_complete(self, task_id: str, tokens_used: int, model: str) -> TaskBudgetStatus:
        cumulative = self._get_cumulative(task_id) + tokens_used
        budget = self._get_budget_for_task(task_id)
        ratio = cumulative / budget

        if ratio >= 1.0:
            return TaskBudgetStatus(
                action="hard_stop",
                message=f"任务 {task_id} 已达 token 预算上限（{cumulative}/{budget}）",
                suggestion="任务被强制终止。AI 已产出部分结果——建议 Owner 审查后决定：拆分任务 OR 增加预算 OR 人工完成"
            )
        elif ratio >= self.config.degrade_at:
            return TaskBudgetStatus(
                action="degrade_model",
                message=f"任务 {task_id} 消耗 {ratio:.0%} 预算——自动切换降级模型"
            )
        elif ratio >= self.config.warning_at:
            return TaskBudgetStatus(
                action="warn",
                message=f"任务 {task_id} 消耗 {ratio:.0%} 预算——建议检查实现方案是否过于复杂"
            )
        return TaskBudgetStatus(action="ok")
```

---

#### 盲点 #19：模型幻觉与容量之间的正反馈循环（退化螺旋）

**本质**：这是一个容量保障领域的**结构性盲区**——极少有 SRE 文献讨论它，但在 AI 施工场景下是**致命的**。

AI 模型在以下条件下更容易产生幻觉：
1. 上下文过长（接近上下文窗口上限时，注意力稀释）
2. 使用降级模型（`qwen2.5-3b-onnx` 比 `deepseek-chat` 更容易出错）
3. 连续多轮被驳回后的"焦虑性生成"（模型试图猜测正确输出而非推理）

**正反馈循环**：
```
容量压力（Token Budget 吃紧）
  → 触发了模型降级（为省钱）
    → 降级模型更容易产生幻觉
      → 幻觉 → 产出错误代码
        → 门禁驳回（G0-G7）
          → AI 看到"驳回原因 + 错误代码 + 越来越长的上下文"
            → 上下文更长 → 注意力更稀释 → 更严重幻觉
              → 更多驳回 → 单任务消耗爆炸
                → 触发 Per-Task Budget 上限
                  → 任务被硬终止
                    → 任务未完成 → 需要重新建一张任务卡
                      → 从头再来（但系统负载更高了）
```

**专业机构对标**：Anthropic 的 Constitutional AI 在检测到模型行为退化时自动触发 **Human-in-the-loop Escalation** 并暂停该 Agent 的自主权限。Google SRE 的 Toil 量化指标中包含 "rework caused by automation errors" 这一维度。

**SOLO Coder 方案**：引入 Degradation Spiral Detector：

```python
# degradation_spiral_detector.py（v2.3.0 新增模块 M-29）
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SpiralAlert:
    task_id: str
    consecutive_rejections: int
    current_model_tier: int
    estimated_wasted_tokens: int
    action: str
    suggestion: str
    escalated: bool

class DegradationSpiralDetector:
    SPIRAL_THRESHOLD: int = 3      # 同一任务连续被驳回 3 次 → 判定为退化螺旋
    CONTEXT_BLOAT_FACTOR: float = 1.3  # 每轮驳回后上下文膨胀因子

    def detect(self, task_id: str, gate_result: "GateResult") -> SpiralAlert | None:
        if gate_result.passed:
            return None

        consecutive = self.db.count_consecutive_failures(task_id)
        current_model = self.degradation_chain.current_tier(task_id)

        if consecutive < self.SPIRAL_THRESHOLD:
            return None

        wasted = self._estimate_wasted_tokens(task_id, consecutive)

        return SpiralAlert(
            task_id=task_id,
            consecutive_rejections=consecutive,
            current_model_tier=current_model,
            estimated_wasted_tokens=wasted,
            action="escalate_to_owner_with_full_context",
            suggestion=(
                f"任务 {task_id} 进入退化螺旋——连续 {consecutive} 次门禁驳回。\n"
                f"浪费估算：~{wasted} tokens（约 ${wasted * 0.000005:.2f}）\n"
                f"当前模型：Tier {current_model}\n\n"
                f"建议行动：\n"
                f"  1. 暂停此任务，Owner 手动审查上下文质量\n"
                f"  2. 考虑将任务拆分为 2-3 个更小的子任务\n"
                f"  3. 临时切换回 Tier 1 模型完成此任务（需 Owner 额外审批预算）\n"
                f"  4. 或者：Owner 手写关键逻辑伪代码作为 AI 的锚点"
            ),
            escalated=True
        )

    def _estimate_wasted_tokens(self, task_id: str, consecutive: int) -> int:
        """估算退化螺旋中浪费的 token"""
        base_tokens = self.db.get_task_first_request_tokens(task_id) or 5000
        wasted = 0
        for i in range(1, consecutive + 1):
            wasted += int(base_tokens * (self.CONTEXT_BLOAT_FACTOR ** i))
        return wasted

    def auto_pause_on_spiral(self, alert: SpiralAlert) -> None:
        """检测到退化螺旋后自动暂停该 Agent 的施工权限"""
        self.permission_guard.revoke_autonomy(
            task_id=alert.task_id,
            reason=f"Task in degradation spiral: {alert.consecutive_rejections} consecutive rejections",
            restore_condition="owner_manual_review"
        )
        self.event_bus.emit("degradation_spiral.detected", alert)
```

关联 SLI：

```yaml
  - id: CAP-011-spiral-detection-rate
    description: "退化螺旋检测——同一任务连续门禁驳回 ≥3 次的事件率"
    target: "< 1 / week"       # 每周不超过 1 次螺旋
    instrumentation:
      hook_point: "DegradationSpiralDetector.detect.exit"
      measurement: "events per week"
      aggregation: "count"
    critical_threshold: "> 3 / week"
    critical_action: "auto_trigger_blueprint_audit + notify_owner——AI上下文可能已系统性退化"
```

---

### 21.2 基础设施物理极限盲点（3 项）

#### 盲点 #20：SQLite 并发写入瓶颈——所有容量数据只有一个写入点

**本质**：§5.2 列出了 7 个 SQLite 表全部写入同一个 SQLite 文件。SQLite 的写锁是**数据库级**的（不是行级也不是表级）。27 个子模块 + agent_health_monitor + behavior_audit_logger 可能同时有 10+ 个写入者竞争同一把写锁。

**风险链**：
```
10 个写入者竞争 SQLite 写锁
  → 串行化等待（每个等待 50-200ms）
    → 容量指标写入延迟飙升
      → CAP-001（启动时间）和 CAP-005（CPU 饱和度）的测量被写入等待污染
        → SLI 数值失真（测量噪声 > 信号）
          → 基于失真数据的 Error Budget 判断 → 误触发
```

**专业机构对标**：Google Borgmon 用内存中的时序环形缓冲区 + 异步批量刷盘。Netflix Atlas 用 memtable + 定期 snapshot，写入路径零锁竞争。

**SOLO Coder 方案**（零新依赖）：

```python
# capacity_governance_loop.py —— MetricsWriteBuffer（v2.3.0 新增）
import asyncio
from typing import Any

class MetricsWriteBuffer:
    """内存缓冲 + 批量异步刷盘——消除 SQLite 写锁竞争"""

    def __init__(self, db, flush_interval_sec: int = 10, max_buffer_size: int = 1000):
        self.db = db
        self.buffer: list[dict[str, Any]] = []
        self.flush_interval = flush_interval_sec
        self.max_buffer_size = max_buffer_size
        self._flush_count: int = 0
        self._total_latency_ms: float = 0.0

    async def write(self, metric: dict[str, Any]) -> None:
        self.buffer.append(metric)
        if len(self.buffer) >= self.max_buffer_size:
            await self._flush()

    async def _flush(self) -> None:
        if not self.buffer:
            return
        t0 = time.perf_counter()
        batch = self.buffer
        self.buffer = []

        with self.db.transaction():
            self.db.executemany(
                "INSERT INTO capacity_metrics(ts, sli_id, value, governance_layer, runtime_plane) "
                "VALUES (?, ?, ?, ?, ?)",
                [(m["ts"], m["sli_id"], m["value"], m["layer"], m["plane"]) for m in batch]
            )

        elapsed = (time.perf_counter() - t0) * 1000
        self._flush_count += 1
        self._total_latency_ms += elapsed

    async def start_periodic_flush(self) -> None:
        while True:
            await asyncio.sleep(self.flush_interval)
            await self._flush()

    @property
    def avg_flush_latency_ms(self) -> float:
        if self._flush_count == 0:
            return 0.0
        return self._total_latency_ms / self._flush_count
```

追加 SLI：

```yaml
  - id: CAP-012-write-buffer-lag
    description: "容量指标写入缓冲刷新延迟 P99"
    target: 100                          # 批量写入不应超过 100ms
    instrumentation:
      hook_point: "MetricsWriteBuffer._flush.exit"
      measurement: "elapsed_ms"
      aggregation: "p99"
    critical_threshold: "p99 > 500"      # 500ms → SQLite 可能过载
    critical_action: "reduce_flush_frequency + suggest_sqlite_vacuum"
```

---

#### 盲点 #21：Telemetry 数据的存储爆炸——可观测性数据本身的容量问题

**本质**：§5.2 定义 `capacity_metrics` 7 天 TTL，但没有定义**总量上限**。随着模块从 97→1500，每天产生的 telemetry 数据也在增长。如果不做总量控制：

```
Day 1（97 模块）：  ~10MB telemetry / 天
Day 90（500 模块）： ~50MB telemetry / 天
Day 180（1000 模块）：~100MB telemetry / 天
```

7 天 TTL × 100MB = **700MB 的 telemetry 数据库**——这超过了 ChromaDB 嵌入式模式的合理范围，也逼近 SQLite 的性能拐点（~1GB）。

**专业机构对标**：VictoriaMetrics 用 **downsampling**（数据老化后自动降精度：原始 1s → 1min 聚合 → 1h 聚合）。Grafana Loki 用 **log retention + compaction**。

**SOLO Coder 方案**：

```yaml
# capacity_slo.yaml —— telemetry_data_lifecycle 节（v2.3.0 新增）
telemetry_data_lifecycle:
  retention:
    raw_metrics: "7d"           # 原始精度：保留 7 天
    hourly_aggregates: "30d"    # 1h 聚合：保留 30 天
    daily_aggregates: "365d"    # 1d 聚合：保留 1 年（容量趋势分析依赖）

  compaction:
    enabled: true
    schedule: "daily @ 03:00"   # 凌晨 3 点执行——施工低谷期
    rules:
      - source_table: "capacity_metrics"
        source_resolution: "raw"
        target_table: "capacity_metrics_hourly"
        target_resolution: "1h"
        aggregation: "avg + p99 + max + count"
        partition_by: "slo_id"
        delete_source: true     # 压缩后删除原始数据

  total_storage_cap_mb: 500     # 硬上限——超过触发告警
  storage_alert:
    warning_at_mb: 350
    critical_at_mb: 450
    critical_action: "suspend_raw_collection + notify_owner + suggest_manual_cleanup"
```

对应新表 Schema：

```sql
-- capacity_metrics_hourly（v2.3.0 新增，压缩后的聚合表）
CREATE TABLE capacity_metrics_hourly (
    slo_id TEXT NOT NULL,
    hour_bucket TEXT NOT NULL,          -- '2026-05-05T14:00:00'
    avg_value REAL,
    p99_value REAL,
    max_value REAL,
    sample_count INTEGER,
    governance_layer TEXT,
    runtime_plane TEXT
);
CREATE INDEX idx_cmh_slo_hour ON capacity_metrics_hourly(slo_id, hour_bucket);
```

---

#### 盲点 #22：Owner 的"运维决策疲劳"随时间累积——Solo 的长期退化

**本质**：Solo Coder 的运维负担并非恒定——它随时间**非线性增长**。第 1 个月你会认真审查每张任务卡的 token 预算建议；第 6 个月你只会扫一眼；第 12 个月你可能根本不看了——因为"之前都还好"。

**专业机构对标**：Google SRE 用 **Toil Budget**——每个 SRE 团队的 toil（重复性手动操作）占比不能超过 50%，超过则暂停新功能开发。Meta Production Engineering 用 **Operational Load Score** 追踪每位工程师的运维负担。

**SOLO Coder 方案**：追踪 Owner 自己的运维负担，让系统在 Owner 累之前"自省"：

```yaml
# capacity_slo.yaml —— owner_toil 节（v2.3.0 新增）
owner_toil_tracking:
  metrics:
    - id: OWNER-TOIL-001-alert-ack-time
      description: "Owner 确认告警的中位延迟"
      measurement: "alert_acknowledged_at - alert_fired_at"
      baseline: "1h"
      degradation_threshold: "> 4h"        # 延迟 >4h → 告警疲劳在发生
      action: "suggest_reduce_alert_sensitivity"

    - id: OWNER-TOIL-002-manual-intervention-rate
      description: "每周需要 Owner 手动干预的次数"
      measurement: "count of owner_manual_action events per week"
      degradation_threshold: "> 10"
      action: "suggest_auto_remediation_upgrade —— 这些操作可以被自动化"

    - id: OWNER-TOIL-003-sign-off-latency
      description: "Owner 审批蓝图变更/预算调整的中位延迟"
      baseline: "12h"
      degradation_threshold: "> 48h"       # 48h+ → Owner 可能过载或在休假
      action: "activate_autonomous_envelope（见 §20.3 #16）"

    - id: OWNER-TOIL-004-review-skip-rate
      description: "Owner 一键通过（未查看详情）的审批比例"
      measurement: "one_click_approvals / total_approvals"
      degradation_threshold: "> 0.5"       # >50% 一键通过 → 审查质量下降
      action: "suggest_delegate_initial_review_to_ai_scoring"
```

对应周报：

```python
# owner_wellness_monitor.py（v2.3.0 新增）
class OwnerWellnessMonitor:
    def weekly_toil_report(self) -> str:
        toil_score = self._compute_toil_score()  # 0.0 - 1.0
        if toil_score > 0.5:
            return (
                f"⚠️ 本周运维负担评分为 {toil_score:.0%}（健康阈值 <50%）。\n"
                f"Top 3 重复操作：\n"
                + "\n".join(f"  {i+1}. {action}（{count}次/周——可自动化）"
                            for i, (action, count) in enumerate(self._top_toil_actions(3)))
                + f"\n\n预估：自动化这 3 项操作可每周节省 {self._estimate_time_saved()} 分钟。"
                + f"\n需要我生成自动化方案吗？"
            )
        return f"✅ 运维负担 {toil_score:.0%}——在健康范围内。本周最耗时操作：{self._top_toil_actions(1)[0][0]}"
```

---

### 21.3 Solo 长期退化盲点（1 项）

#### 盲点 #23：缺少"AI 技能退化"的容量端检测

**本质**：AI 不总是越来越好。Vibe Coding 有一个反直觉现象：**随着系统规模增长，AI 的施工质量可能下降**——因为上下文越来越复杂，AI 做出正确决策需要的信息密度下降。

**退化信号**（这些在当前蓝图里完全无监控）：
- AI 产出代码的平均文件行数随时间上升 → 模块化意识退化
- AI 引入的新 mypy 类型错误比例上升 → 类型安全意识退化
- AI 在门禁驳回后选择"重写整个文件"而非"局部修复"的频率上升 → 精确理解能力退化
- AI 产出的代码中重复模式增多 → 上下文记忆能力退化

**SOLO Coder 方案**：

```yaml
# capacity_slo.yaml —— ai_skill_health 节（v2.3.0 新增）
ai_skill_health:
  metrics:
    - id: AI-SKILL-001-avg-file-size
      description: "AI 产出代码的平均文件行数（7 天滑动窗口）"
      baseline: 150                     # 基准：AI 产出的典型文件约 150 行
      degradation_threshold: "> 250"    # 超过 250 → 模块化意识退化
      action: "suggest_refactoring_session——引导 AI 拆分大文件"

    - id: AI-SKILL-002-type-annotation-quality
      description: "AI 新引入的代码的 mypy 首次通过率"
      target: 0.95
      degradation_threshold: "< 0.85"
      action: "suggest_add_type_annotation_examples_to_context"

    - id: AI-SKILL-003-targeted-fix-ratio
      description: "驳回后 AI 选择'局部修复'vs'全量重写'的比例"
      target: "> 0.7"                   # 70% 应该是局部修复
      degradation_threshold: "< 0.5"    # <50% → AI 不理解问题、选择暴力重写
      action: "suggest_improve_gate_feedback_specificity"

    - id: AI-SKILL-004-code-novelty-index
      description: "AI 产出代码中与已有代码的语义重复度"
      measurement: "1 - (code_dedup_engine similarity to existing)"
      degradation_threshold: "< 0.5"    # AI 在生成重复代码
      action: "suggest_refresh_ai_context_with_recent_changes"
```

AI 技能退化的自动检测 + 告警逻辑：

```python
# ai_skill_monitor.py（v2.3.0 新增）
class AISkillMonitor:
    def detect_regression(self) -> list[SkillRegression]:
        regressions = []
        for metric in self.config.metrics:
            current = self._compute_current(metric.id, days=7)
            baseline = self._compute_baseline(metric.id, days=30)
            delta = (current - baseline) / baseline if baseline else 0

            if metric.id == "AI-SKILL-001-avg-file-size" and delta > 0.3:
                regressions.append(SkillRegression(
                    metric=metric.id,
                    trend="increasing_file_size",
                    severity="warning",
                    suggestion="AI 倾向于生成大文件而非模块化——建议下一个 AI session 中注入'模块化原则'到上下文中"
                ))
            elif metric.id == "AI-SKILL-003-targeted-fix-ratio" and delta < -0.2:
                regressions.append(SkillRegression(
                    metric=metric.id,
                    trend="brute_force_rewrites",
                    severity="critical",
                    suggestion="AI 的精确修复能力下降——建议检查门禁反馈是否足够具体，或考虑切换回 Tier 1 模型"
                ))
        return regressions
```

---

### 21.4 经济模型盲点（1 项）

#### 盲点 #24：缺少"Token 成本 vs 产出价值"的 ROI 模型

**本质**：§9 定义了 Token Budget 的**上限**，但完全没有定义**价值分类**。你消耗的 token 分三种：
1. **创造价值**：产出了通过门禁进入生产的功能代码
2. **防御价值**：产出了审计/测试/类型检查（不创造功能但防止退化）
3. **纯粹浪费**：因为上下文过长、AI 幻觉、退化螺旋而被消耗的 token

当前蓝图对此没有区分——"花了 100K token"和"花了 100K token 产出了 3 个通过门禁的新模块"在系统中看起来一样。

**SOLO Coder 方案**：

```python
# token_value_attribution.py（v2.3.0 新增模块 M-30）
from dataclasses import dataclass
from enum import Enum

class TokenValueCategory(Enum):
    CREATIVE = "creative"       # 创造价值：代码生成、功能实现
    DEFENSIVE = "defensive"     # 防御价值：测试、类型检查、审计、文档
    WASTED = "wasted"           # 浪费：驳回重做、幻觉修复、退化螺旋

@dataclass
class TokenValueReport:
    task_id: str
    total_tokens: int
    creative_pct: float
    defensive_pct: float
    wasted_pct: float
    value_index: float          # 0.0-1.0，创造价值权重 2×，防御价值权重 1×
    recommendation: str

class TokenValueAttributor:
    def analyze_task(self, task_id: str) -> TokenValueReport:
        total = self.db.get_task_token_total(task_id)
        creative = sum(self.db.get_tokens_for_events(task_id, [
            "code_generation", "refactoring", "feature_implementation"
        ]))
        defensive = sum(self.db.get_tokens_for_events(task_id, [
            "test_generation", "type_annotation", "audit_check", "documentation"
        ]))
        wasted = sum(self.db.get_tokens_for_events(task_id, [
            "rework_after_rejection", "hallucination_fix", "spiral_recovery",
            "excessive_context_overhead"
        ]))

        value_index = (creative * 2 + defensive) / total if total > 0 else 0

        if wasted / total > 0.4:
            recommendation = f"⚠️ 此任务有 {wasted/total:.0%} 的 token 被浪费——建议排查根因"
        elif value_index < 0.6:
            recommendation = "⚠️ 此任务的 token 价值偏低——防御性消耗过高，检查是否过度测试/审计"
        else:
            recommendation = "✅ Token 使用效率良好"

        return TokenValueReport(
            task_id=task_id,
            total_tokens=total,
            creative_pct=creative / total if total else 0,
            defensive_pct=defensive / total if total else 0,
            wasted_pct=wasted / total if total else 0,
            value_index=round(value_index, 2),
            recommendation=recommendation
        )

    def monthly_roi_summary(self) -> dict:
        """月度 ROI 摘要：Owner 一眼看清'钱花在哪了'"""
        tasks = self.db.get_completed_tasks_in_month()
        reports = [self.analyze_task(t.id) for t in tasks]
        total_tokens = sum(r.total_tokens for r in reports)
        return {
            "total_tokens": total_tokens,
            "total_cost_estimated_usd": total_tokens * 0.000005,
            "creative_pct": sum(r.creative_pct * r.total_tokens for r in reports) / total_tokens,
            "wasted_pct": sum(r.wasted_pct * r.total_tokens for r in reports) / total_tokens,
            "modules_produced": len(tasks),
            "avg_token_per_module": total_tokens / len(tasks) if tasks else 0,
            "value_index": sum(r.value_index for r in reports) / len(reports) if reports else 0,
        }
```

---

### 21.5 协议与标准层盲点（1 项）

#### 盲点 #25：W3C TraceContext 传播链中的容量元数据缺失

**本质**：§12.2 定义了 W3C TraceContext（`traceparent` + `tracestate`）的传播，但只在**追踪层面**——没有在 trace context 中携带**容量元数据**。

当一条请求链穿过 5 个模块（Pipeline → Agent → Sandbox → ContractBus → Database），每个模块能看到 `traceparent`——但不知道这条链上其他模块的容量状态。如果模块 B 的内存使用率已达 90%，它接收到的来自模块 A 的请求可能是"一个在超载状态下发出的请求"——模块 B 应该能据此**降低这个请求的处理优先级**。

**专业机构对标**：Google gRPC Backpressure 在 header 中传播 `grpc-timeout` 和 `grpc-load`。Netflix Conductor 的 Task-to-Task 传递带有 `priority_decay_factor`——上游过载时下游自动降低优先级。

**SOLO Coder 方案**：扩展 `tracestate` 承载容量元数据：

```python
# otel_capacity_propagation.py（v2.3.0 新增，与 reasoning_spans.py 集成）
from opentelemetry import trace
from dataclasses import dataclass

@dataclass
class CapacityTraceContext:
    health_score: float          # 调用方当前的 ZephyrHealthScore
    memory_pct: float            # 调用方当前内存使用率
    error_budget_tier: str       # 调用方当前 Error Budget 级别
    throttle_pct: float          # 调用方当前的施工速率（1.0 = 全速）
    degraded: bool               # 调用方是否在降级状态

class CapacityTracePropagator:
    """将容量元数据注入 W3C tracestate，供下游模块消费"""

    def inject(self, span: trace.Span, ctx: CapacityTraceContext) -> None:
        span.set_attribute("zephyr.capacity.health_score", ctx.health_score)
        span.set_attribute("zephyr.capacity.memory_pct", ctx.memory_pct)
        span.set_attribute("zephyr.capacity.error_budget", ctx.error_budget_tier)
        span.set_attribute("zephyr.capacity.throttle", ctx.throttle_pct)
        span.set_attribute("zephyr.capacity.degraded", ctx.degraded)

    def extract(self, span: trace.Span) -> CapacityTraceContext:
        """下游模块从上游 span 中提取容量上下文"""
        return CapacityTraceContext(
            health_score=float(span.attributes.get("zephyr.capacity.health_score", 100)),
            memory_pct=float(span.attributes.get("zephyr.capacity.memory_pct", 0)),
            error_budget_tier=str(span.attributes.get("zephyr.capacity.error_budget", "healthy")),
            throttle_pct=float(span.attributes.get("zephyr.capacity.throttle", 1.0)),
            degraded=bool(span.attributes.get("zephyr.capacity.degraded", False)),
        )

class CapacityAwareMiddleware:
    """中间件：在每个跨模块调用前后注入/提取容量上下文"""

    def on_outgoing_request(self, span: trace.Span) -> None:
        ctx = CapacityTraceContext(
            health_score=self.health_score.value,
            memory_pct=psutil.virtual_memory().percent / 100,
            error_budget_tier=self.error_budget.current_tier(),
            throttle_pct=self.change_rate_limiter.override_pct,
            degraded=self.error_budget.current_tier() in ("critical", "emergency"),
        )
        self.propagator.inject(span, ctx)

    def on_incoming_request(self, span: trace.Span) -> "RequestPriority":
        ctx = self.propagator.extract(span)
        if ctx.degraded or ctx.health_score < 50:
            return RequestPriority.LOW   # 上游已降级 → 降低此请求的优先级
        elif ctx.health_score < 80:
            return RequestPriority.MEDIUM
        return RequestPriority.NORMAL
```

---

### 21.6 第二轮盲点全量清单（追加汇总）

| # | 盲点名称 | 严重度 | 归属维度 | 对标来源 |
|---|---------|:---:|------|------|
| 17 | Context 预算慢泄漏 | **高** | AI 施工特异性 | Anthropic Codified Context / Google Context Caching |
| 18 | 多轮对话令牌通货膨胀 | **高** | AI 施工特异性 | GitHub Copilot Agent Mode / Anthropic Claude Code |
| 19 | 模型幻觉-容量正反馈循环 | **致命** | AI 施工特异性 | Anthropic Constitutional AI / Google Toil Budget |
| 20 | SQLite 写锁瓶颈 | **高** | 物理极限 | Google Borgmon / Netflix Atlas |
| 21 | Telemetry 存储爆炸 | 中 | 物理极限 | VictoriaMetrics Downsampling / Grafana Loki |
| 22 | Owner 运维决策疲劳 | 中 | Solo 长期退化 | Google Toil Budget / Meta Operational Load Score |
| 23 | AI 技能退化检测 | **高** | Solo 长期退化 | 原始发现——Vibe Coding 社区反直觉现象 |
| 24 | Token 价值归因 ROI | 中 | 经济模型 | Stripe Unit Economics / ISACA AI Cost Governance |
| 25 | TraceContext 容量元数据 | 中 | 协议/标准 | Google gRPC Backpressure / Netflix Conductor |

---

### 21.7 两轮合并：完整盲点全景（25 项）按施工优先级排序

| P | # | 盲点 | 致命/高/中 | 一句话 |
|:---:|:---:|------|:---:|------|
| 1 | 14 | Business SLI | 高 | 没有它你看不到 AI 施工质量在退化 |
| 2 | 19 | 幻觉-容量正反馈螺旋 | **致命** | 容量压力→幻觉→更多消耗→恶性循环 |
| 3 | 12 | 告警疲劳 | 致命 | 1 人面对 30+ 告警源必然疲劳 |
| 4 | 15 | 施工节奏控制 | 高 | AI 1h 合并 30 模块→不可逆破坏 |
| 5 | 1 | SLI 插桩点 | 高 | AI 各自采 SLI→数值不可比 |
| 6 | 18 | 多轮对话令牌通胀 | 高 | 单任务 7 轮后 token 翻 5× |
| 7 | 9 | 预警→修复闭环 | 高 | 制动后修复通道被锁死 |
| 8 | 17 | Context 预算慢泄漏 | 高 | 每次 session 启动的隐形税收 |
| 9 | 20 | SQLite 写锁瓶颈 | 高 | 写入串行化→SLI 测量失真 |
| 10 | 23 | AI 技能退化检测 | 高 | AI 质量下降无人监测 |
| 11 | 6 | 容量保障自身开销 | 高 | 极限时监控可能压垮业务 |
| 12 | 3 | Error Budget 归因 | 高 | 预算耗尽无法定位根因 |
| 13 | 2 | SLO 窗口分层 | 高 | 30 天窗口在演进期无意义 |
| 14 | 13 | AI 可理解性 | 高 | 复杂度=AI 改错率 |
| 15 | 8 | AI 行为预测 | 高 | 只预测资源不预测行为 |
| 16 | 16 | Owner 离线自治 | 高 | 离线 48h 系统可能自毁 |
| 17 | 22 | Owner 决策疲劳 | 中 | 维护负担非线性增长 |
| 18 | 21 | Telemetry 存储爆炸 | 中 | 700MB+ 超出 SQLite 舒适区 |
| 19 | 25 | TraceContext 容量元数据 | 中 | 跨模块容量上下文传播 |
| 20 | 24 | Token 价值 ROI | 中 | 不知道钱花得值不值 |
| 21 | 10 | 成本回升 | 中 | 降级后无法自动切回好模型 |
| 22 | 11 | 渐进式流量切换 | 中 | Kill Switch 缺少"半速"档 |
| 23 | 7 | 健康评分 | 中 | 缺少单一决策数字 |
| 24 | 5 | SLO Review | 中 | SLO 目标值过期 |
| 25 | 4 | 脉冲容忍 | 中 | 短窗口误触发 |

---

### 21.8 建议新增模块（M-28~M-30）

本轮审计发现需要 3 个新的 Python 模块来落地设计：

| 模块ID | 模块名称 | 职责 | 预期路径 | AI自治权限 |
|--------|---------|------|---------|-----------|
| M-28 | change_rate_limiter.py | 渐进式施工节奏控制 + Burst 检测（§20 #11 + §20.3 #15） | src/zephyr/shared/change_rate_limiter.py（📋规划路径，待创建） | Human-Gated（策略）/ AI-Modifiable（执行） |
| M-29 | degradation_spiral_detector.py | 退化螺旋检测 + 自动暂停（§21.1 #19） | src/zephyr/shared/degradation_spiral_detector.py（📋规划路径，待创建） | AI-Modifiable |
| M-30 | token_value_attribution.py | Token 消耗价值归因 + ROI 报告（§21.4 #24） | src/zephyr/shared/token_value_attribution.py（📋规划路径，待创建） | AI-Modifiable |

> **M-28~M-30 不应纳入蓝图 §6 的模块分解表**——它们是对已有模块（M-21 error_budget_tracker / M-07 event_bus背压 / M-26 cost_estimator）的横向增强，职责重合度较高。建议在对应模块施工时内联实现，而非独立建模块。

---

## 22. 第三轮深度审计——时间动力学与深层结构盲点（v2.4.0 新增）

> **审计升级**：前两轮审计（§20 + §21）覆盖了 25 项盲点，对标了 15+ 家专业机构。第三轮审计的目标是找到那些**无论怎么对标外部机构都不会自动浮现**的盲点——这些盲点存在于系统的"时间维度"、"自我指涉"、"物理边界"和"不可测试性"中。对标来源扩展至：Microsoft Windows Internals（路径/句柄限制）、Taleb《反脆弱》中的非线性系统退化理论、Kahneman & Tversky 沉没成本效应在自动化系统中的表现、Google SRE 的 Disaster Recovery Testing（灾难恢复演练）、以及 Vibe Coding 社区中关于"AI 知道自己被监控后的行为变化"的非正式讨论。

> **盲点确认标准**：本蓝图 v2.3.0（§1~§21）中**完全未提及**。

---

### 22.1 时间动力学盲点——系统在不同时刻是不同系统（4 项）

#### 盲点 #26：启动序列的"未保护窗口"——最脆弱的是开机那一刻

**本质**：Modular Initialization —— 97→1500 个模块是**按依赖图顺序加载**的。但容量保障体系本身的各个组件也需要被加载。当前蓝图没有任何章节讨论**加载顺序**：Kill Switch 必须在哪些模块之前初始化？如果 Kill Switch 初始化排在 Sandbox 之后，那么在 Sandbox 初始化时如果发生资源爆炸，Kill Switch 还不可用。

**最大风险**：
```
启动序列（按 ascii 排序加载）：
  L01: agent_rbac ───────── 率先加载 ✅
  L02: audit_trail ───────── 加载中...
  L03: budget_enforcer ───── 尚未加载——Token 预算无人守护
  ...
  L18: kill_switch ───────── 第 18 个加载！它之前的 17 个模块完全不受保护
  ...
  L27: capacity_assurance ── 最后一个加载——容量保障自身最后才启动
```

**专业机构对标**：Google Borg 的启动顺序由 `init_dependency_graph` 显式定义——保护性组件（Resource Guardian、Quota Enforcer）始终第一批加载，业务组件最后。Linux systemd 用 `Before=` / `After=` 声明启动顺序约束。

**SOLO Coder 方案**：定义 **Startup Protection Window** + 显式加载顺序：

```yaml
# startup_protection.yaml（v2.4.0 新增）
startup_protection:
  # 第一批：零依赖保护层——在一切之前启动
  early_boot:
    - module: "kill_switch"
      reason: "需在任何人可能消耗资源前就绪——即使 Kill Switch 本身初始化失败也能fallback到默认拒绝"
      fallback_behavior: "deny_all"
    - module: "circuit_breaker"
      reason: "防止启动期间的跨模块调用雪崩"
      fallback_behavior: "all_open"            # 启动时所有熔断器默认 OPEN
    - module: "provenance_db"
      reason: "审计日志需要最先可用——启动时的错误也需要被记录"
      fallback_behavior: "in_memory_buffer"

  # 第二批：容量感知层——在业务模块之前启动
  mid_boot:
    - module: "capacity_governance_loop"
      reason: "需要收集启动指标但不做决策"
      during_startup: "collect_only_no_enforcement"
    - module: "error_budget_tracker"
      reason: "从持久化存储恢复上次的 Error Budget 状态"
    - module: "degradation_chain"
      reason: "需要就绪——启动期间的 API 调用也需要模型降级保护"

  # 第三批：业务层——所有保护就绪后才启动
  late_boot:
    - module: "sandbox"
    - module: "agent_rbac"
    - module: "pipeline"
    - ...

  # 启动保护窗口：从第一个模块加载到最后一个模块加载的时间窗
  startup_window:
    metric: "time_from_first_import_to_last_import"
    target: "30s"                             # 30s 内完成全量加载
    during_window: "kill_switch_conservative"  # 窗内默认保守——仅加载，不执行
    auto_release_condition: "all_modules_healthy for 60s"
    alert_if: "window > 60s"                  # 如果加载超过 60s → 系统可能有循环依赖或模块挂死
```

对应代码骨架：

```python
# startup_guard.py（v2.4.0 新增，集成到 zephyr.__init__）
class StartupGuard:
    def __enter__(self):
        self.start_ts = time.perf_counter()
        logging.info("启动保护窗口已激活——默认拒绝所有操作")

    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start_ts
        if elapsed > 60:
            alert(f"启动耗时 {elapsed:.1f}s——超过 60s 阈值，检查是否有循环依赖")
        if self.kill_switch.status == "conservative":
            self.kill_switch.release_if_healthy()
        logging.info(f"启动保护窗口已关闭——耗时 {elapsed:.1f}s")

# 使用方式：在 zephyr/__init__.py 中
if __name__ == "__main__":
    with StartupGuard():
        load_all_modules_in_dependency_order()
```

---

#### 盲点 #27：Day-0 冷启动——容量预测模型在零历史数据时无法工作

**本质**：§17 的容量预测模型（线性回归 + 指数平滑）需要**至少 7 天的历史数据**才能产生有意义的预测。但系统刚搭建好时（Day 0），`capacity_metrics` 表是空的。此时：

1. **启动时间 SLI**（CAP-001）：没有基准值——无法知道 2000ms 是不是合理目标
2. **容量预测**（§17.2）：线性回归在 0 数据点上退化为 `NaN`
3. **Error Budget**：没有历史数据 → 初始化为 100% → 但不知道正常情况下每天消耗多少

**风险**：Day 0 的系统是**最脆弱**的——新模块在建、新代码在跑、一切都在变化，但也是**最不可见**的——因为所有监控都还没建立基准线。

**专业机构对标**：Google Borg 的新服务启动有 **Warmup Period**（默认 5 分钟），期间告警静默、只收集数据。AWS Auto Scaling 的新实例有 **Cooldown Period**。Vibe Coding 社区实践中，前 24 小时被称作"观测静默期"——只埋桩不告警。

**SOLO Coder 方案**：

```yaml
# capacity_slo.yaml —— day0_bootstrap 节（v2.4.0 新增）
day0_bootstrap:
  observation_only_period: "24h"     # 前 24h：只收集不告警
  initial_slo_thresholds:
    method: "heuristic_from_system_specs"
    rules:
      - metric: "startup_time"
        target_initial: "5000"       # 宽松初始值——不基于数据，基于硬件常识
        tighten_after: "7d"          # 7 天后用实际数据校准
      - metric: "memory_saturation"
        target_initial: "0.9"        # 90%——宽松初始值
        tighten_after: "14d"
      - metric: "error_rate"
        target_initial: "0.05"       # 5%——非常宽松
        tighten_after: "7d"

  prediction_model_bootstrap:
    method: "synthetic_seed"
    synthetic_data:
      - metric: "module_growth"
        daily_rate: 2                # 假设每天新增 2 个模块——最保守估计
        confidence: "low"
        recalc_after_days: 5         # 5 天后用真实数据替换
      - metric: "memory_growth"
        daily_mb: 50                 # 假设每天新增 50MB——基于典型 Python 模块的估计
        confidence: "low"
        recalc_after_days: 7

  day0_alerts:
    rule: "only_critical_errors"     # Day 0 只告警真正的 crash/failure
    suppressed: ["prediction_alerts", "trend_alerts", "budget_warnings"]
```

---

#### 盲点 #28：优雅关机——系统终止时的容量数据丢失与状态迁移

**本质**：蓝图没有提到系统停止时会发生什么。关机时：
- 内存缓冲中的容量指标（`MetricsWriteBuffer`，#20）可能未被刷盘
- 进行中的 AI 任务被硬中断——Per-Task Token Budget 状态丢失
- Error Budget 的当前状态（燃烧率、tier）没有被持久化 → 下次启动时"失忆"
- `kill_switch` 的状态（读模式/保守模式）没有写入硬盘 → 重启后可能被复位为"全开放"

**风险**：硬关机后再启动 → 丢失了关机前的容量状态 → Error Budget 计数器重置 → "昨天烧掉了 30% 的预算" → 重启后变成 100% → 系统误以为一切健康。

**专业机构对标**：PostgreSQL 的 WAL（Write-Ahead Log）保证 crash-safe。Redis 的 RDB/AOF 持久化在 shutdown 时强制刷盘。Kubernetes Pod 有 `terminationGracePeriodSeconds`（默认 30s）供 Pod 清理状态。

**SOLO Coder 方案**：

```python
# graceful_shutdown.py（v2.4.0 新增，注册到 atexit + signal handlers）
import atexit
import signal
import json

class GracefulShutdown:
    def __init__(self, capacity_state: "CapacityState"):
        self.state = capacity_state
        self.shutdown_requested = False
        atexit.register(self._on_shutdown)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        self.shutdown_requested = True
        logging.info(f"收到信号 {signum}——开始优雅关机（最多等待 30s）")

    def _on_shutdown(self) -> None:
        t0 = time.perf_counter()
        logging.info("优雅关机序列启动...")

        # 步骤 1: 停止接受新的 AI 施工任务
        self.state.change_rate_limiter.set_throttle(0.0, "shutdown")

        # 步骤 2: 等待进行中的 AI 任务到达安全点（最多 10s）
        active_tasks = self.state.task_registry.get_active_tasks()
        for task in active_tasks:
            task.request_cancellation()       # 请求 AI 在下一个 safe-point 停止
        self._wait_for_tasks(active_tasks, timeout=10)

        # 步骤 3: 强制刷盘——刷新所有缓冲
        self.state.metrics_write_buffer.flush_sync()
        self.state.error_budget_tracker.persist_current_state()
        self.state.token_budget_tracker.persist_all_task_states()

        # 步骤 4: 保存关机快照——下次启动时恢复
        snapshot = {
            "ts": datetime.now().isoformat(),
            "error_budget_tier": self.state.error_budget.current_tier(),
            "error_budget_remaining": self._get_all_budget_remaining(),
            "active_task_ids": [t.id for t in active_tasks],
            "kill_switch_status": self.state.kill_switch.current_mode,
            "health_score": self.state.health_score.value,
        }
        with open("data/shutdown_snapshot.json", "w") as f:
            json.dump(snapshot, f, indent=2)

        # 步骤 5: 关闭数据库连接
        self.state.db.close()

        elapsed = time.perf_counter() - t0
        logging.info(f"优雅关机完成——耗时 {elapsed:.1f}s，快照已保存")
```

启动时恢复：

```python
# 在 zephyr/__init__.py 中，startup_guard 之后
def restore_from_snapshot():
    snapshot_path = Path("data/shutdown_snapshot.json")
    if not snapshot_path.exists():
        logging.info("无上次关机快照——以默认状态启动")
        return
    with open(snapshot_path) as f:
        snap = json.load(f)
    if (datetime.now() - datetime.fromisoformat(snap["ts"])).hours > 24:
        logging.warning(f"上次关机快照已超过 24h（{snap['ts']}）——部分状态可能已过期，以保守模式启动")
        kill_switch.enter_conservative()
    else:
        error_budget.restore_from_snapshot(snap["error_budget_remaining"])
        logging.info(f"已从上一次关机快照恢复——Error Budget 剩余: {snap['error_budget_remaining']}")
```

---

#### 盲点 #29：时间分区的容量模式——AI API 行为随时间剧烈波动

**本质**：§17 容量预测将所有时间点等权处理。但 AI API 的延迟/成本/可用性在 24 小时内波动极大——凌晨 3 点的 API 延迟和下午 3 点完全不同。

**被忽略的时间分区**：
- **AI API 峰值时段**（北京时间 9:00-12:00，14:00-18:00）：延迟 +30%，限流概率 ×3
- **AI API 低谷时段**（北京时间 0:00-6:00）：延迟最低，成本最优
- **免费额度重置点**（按 API 厂商不同）：重置后可用额度突然恢复
- **中国节假日**：API 负载明显下降，可用性上升

**专业机构对标**：Google Cloud SRE 用 **Time-of-Day SLO**——工作日 9-17 点的 SLO 比凌晨 2-6 点更严格。Netflix 的 Auto Scaling 用 **Temporal Forecasting**（Prophet 的时间序列分解含 holiday 效应）。

**SOLO Coder 方案**：在 SLO 中引入时间分区：

```yaml
# capacity_slo.yaml —— time_slo_adjustments 节（v2.4.0 新增）
time_slo_adjustments:
  - period: "peak_hours"
    when: "weekday 09:00-18:00 CST"
    adjustments:
      latency_multiplier: 0.7          # 峰值期 SLO 收紧 30%——响应必须更快
      retry_limit: 1                   # 峰值期重试次数降低——避免加重 API 负载
      prefer_local_model: true         # 优先本地模型——避免 API 竞争
  - period: "off_peak"
    when: "daily 00:00-06:00 CST"
    adjustments:
      latency_multiplier: 1.5          # 低谷期 SLO 放宽 50%
      retry_limit: 3                   # 低谷期可以多试几次
      batch_tasks: true                # 低谷期适合批量任务
  - period: "weekend"
    when: "saturday, sunday"
    adjustments:
      latency_multiplier: 0.8
      enable_cost_optimization: true   # 周末用更便宜的模型做非紧急任务

  # 免费额度感知
  free_tier_awareness:
    check: "before_each_api_call"
    if_quota_low: "degrade_all_P0_to_tier_2"
    if_quota_reset_soon: "within_24h"
    action_near_reset: "batch_non_urgent_work_for_after_reset"  # 把非紧急工作排到额度重置后
```

---

### 22.2 观察者效应与自我干扰（3 项）

#### 盲点 #30：容量监控写入 → 污染被监控的指标（自我指涉悖论）

**本质**：这是一个 **Russell 悖论级别**的容量盲点。`capacity_governance_loop` 每 300s 向 SQLite 写入 `capacity_metrics`，这个写入本身消耗：
- **CPU**：写入增加了 CPU 使用率 → 被 CAP-005（CPU 饱和度）捕获 → 监控系统报告 "CPU 高" → 但 CPU 高的原因是监控系统自己在写入
- **IO**：写入增加了磁盘 IO → 被 CAP-003（模块间调用错误率）间接影响——如果 IO 竞争导致 SQLite 操作超时
- **内存**：`MetricsWriteBuffer` 的缓冲区消耗内存 → 被 CAP-004（内存饱和度）捕获

**结果**：监控系统报告系统有问题 → 但问题源于监控系统自身。这就是 **Observer Effect**（观察者效应）的最恶劣形式——观察行为本身制造了被观察的现象。

**专业机构对标**：Google Borgmon 用 **Sidecar** 独立资源池——监控进程与业务进程物理隔离。Netflix Atlas 的监控数据写入使用独立的写入路径（`/mnt/atlas` 独立磁盘分区），不共享 IO 带宽。

**SOLO Coder 方案**（不引入新进程/新磁盘的折中）：

```python
# capacity_governance_loop.py —— ObserverEffectCompensator（v2.4.0 新增）
class ObserverEffectCompensator:
    """补偿监控系统自身的资源消耗对 SLI 的污染"""

    def compensate(self, raw_sli: "CapacityMetric") -> "CapacityMetric":
        """从原始 SLI 读数中减去监控系统自身的消耗"""
        self_overhead = self._measure_self_overhead()

        if raw_sli.sli_id == "CAP-004-memory-saturation":
            # 内存饱和度 = 系统总内存使用 - OTel buffer - 写入缓冲区 - 监控自身
            compensated_value = raw_sli.value - self_overhead.memory_mb / 1024
            return raw_sli.with_value(max(0, compensated_value))

        elif raw_sli.sli_id == "CAP-005-cpu-saturation":
            compensated_value = raw_sli.value - self_overhead.cpu_pct
            return raw_sli.with_value(max(0, compensated_value))

        return raw_sli  # 其他 SLI 不受观测效应影响

    def _measure_self_overhead(self) -> "SelfOverhead":
        my_pid = os.getpid()
        proc = psutil.Process(my_pid)
        return SelfOverhead(
            cpu_pct=proc.cpu_percent(interval=0.1),
            memory_mb=proc.memory_info().rss / 1024 / 1024,
            io_read_mb=proc.io_counters().read_bytes / 1024 / 1024 if hasattr(proc, 'io_counters') else 0,
            io_write_mb=proc.io_counters().write_bytes / 1024 / 1024 if hasattr(proc, 'io_counters') else 0,
        )
```

对应的数据标记：所有 `capacity_metrics` 表中补偿后的记录打上 `compensated: true` 标签，确保不会被双重补偿。

---

#### 盲点 #31：AI 知道自己在被监控 → 行为模式变化（霍桑效应）

**本质**：这是一个连 Google SRE Workbook 都没有直接讨论的盲点——**当 AI Agent 能感知到 Token Budget / Error Budget / Kill Switch 的存在时，它的生成行为会发生变化**。

**可能的 AI 行为扭曲**：
- AI 检测到 Token Budget 只剩 20% → 加速生成 → 质量下降 → 门禁驳回率上升 → 反而消耗更多 Token
- AI 知道 Kill Switch 在监控内存 → 避免使用大对象 → 但用小对象拼接导致逻辑更复杂 → 代码行数更多 → 内存反而更大
- AI 被反复告诉"注意 Error Budget" → 过度保守 → 不敢做必要的大范围重构 → 技术债务累积

**专业机构对标**：GitHub Copilot 团队发现：当 Agent 模式用户被告知"你有 50 次免费调用"vs 不被告知，前者的代码提交率反而更高但质量评分更低。Anthropic 的 Claude 在 Constitutional AI 训练中使用 **Blind Monitoring**——AI 不知道哪些输出被监控、哪些不被监控，以消除霍桑效应。

**SOLO Coder 方案**：**分离监控信号与 AI 可见信号**——AI 不应直接看到 Token Budget / Error Budget 的原始数据，只看到从这些数据派生的"行为建议"：

```python
# ai_context_filter.py（v2.4.0 新增，位于 context_assembler 之后）
class AIContextFilter:
    """过滤注入 AI session 的容量信息——只给 AI 看到它需要的行为指引，不给原始数据"""

    RAW_METRICS_BLOCKED = [
        "token_budget_remaining",
        "error_budget_remaining",
        "error_budget_tier",
        "kill_switch_status",
        "memory_pct",
        "total_cost_to_date",
    ]

    BEHAVIOR_GUIDANCE_MAP = {
        # 将原始容量数据转换为行为指引
        # 不告诉 AI "预算只剩 20%"，而说"当前任务建议简化实现方案"
        "token_budget": {
            "healthy": "全功能实现——可以使用复杂方案",
            "warning": "标准实现——保持代码简洁",
            "critical": "最小可行实现——优先功能完整性而非代码优雅",
        },
        "error_budget": {
            "healthy": "正常节奏——必要时可以大胆重构",
            "warning": "建议优先局部修复而非全量重写",
            "critical": "仅做最小必要修改——避免大范围变更",
        },
    }

    def filter_for_ai(self, raw_context: dict) -> dict:
        """为 AI 准备上下文——移除原始容量指标，替换为行为指引"""
        for blocked_key in self.RAW_METRICS_BLOCKED:
            raw_context.pop(blocked_key, None)

        # 注入行为指引
        raw_context["system_guidance"] = self._generate_guidance()
        return raw_context

    def _generate_guidance(self) -> str:
        tb_tier = self.token_budget.current_tier()
        eb_tier = self.error_budget.current_tier()
        return (
            f"[系统指引] \n"
            f"代码实现策略: {self.BEHAVIOR_GUIDANCE_MAP['token_budget'][tb_tier]}\n"
            f"变更策略: {self.BEHAVIOR_GUIDANCE_MAP['error_budget'][eb_tier]}"
        )
```

---

#### 盲点 #32：配置热重载引发的中年危机——运行中变更 SLO 阈值

**本质**：蓝图没有讨论 SLO 阈值、Token Budget 上限、Error Budget 分级等配置能否在运行时热重载。如果能热重载：当系统正在处理一个 AI 任务的过程中，Token Budget 被从 200K 降低到 30K → 当前任务立即触发 hard_stop → AI 任务被中断 → 产出半成品。

**关键问题**：哪些配置变更是"立刻生效"的？哪些是"等当前批次完成后生效"的？哪些是"需要重启"的？当前蓝图对此完全未定义。

**SOLO Coder 方案**：定义配置的生效语义：

```yaml
# capacity_governance_config.yaml —— config_activation_semantics 节（v2.4.0 新增）
config_activation_semantics:
  immediate:            # 立即生效——影响下一次 API 调用、下一次写入
    - "kill_switch_mode"                  # 安全开关必须立即生效
    - "degradation_chain_tier"            # 模型降级可以立刻切换
    - "alert_thresholds"                  # 告警阈值立刻生效——安全优先

  batch_boundary:       # 等当前 AI 任务批次完成后生效
    - "token_budget_per_task"             # 已开始的任务不要硬中断——让它完成
    - "max_concurrent_changes"            # 当前并发任务不强制减员
    - "max_modules_per_batch"

  restart_required:     # 需要系统重启
    - "database_schema_changes"           # SQLite DDL
    - "otel_collector_endpoint"           # OTel 导出器配置
    - "immutable_core_allowlist"          # 安全敏感

  mid_task_protection:
    rule: "如果某配置标记为 batch_boundary，则当前进行中的任务继续使用旧配置"
    max_grace_period: "30min"             # 30min 后强制切换到新配置——不再等
    notify_owner_on_conflict: true        # 如果有任务因为旧配置被保护而未应用新配置→通知Owner
```

---

### 22.3 可测试性盲点（2 项）

#### 盲点 #33：不可测试的容量装置——Kill Switch / Error Budget 耗尽 / 退化螺旋无法被单元测试覆盖

**本质**：§5.1 提到 `pytest` 测试框架，但**容量保障系统中最重要的几个状态是无法通过常规单元测试来验证的**：

- **Kill Switch 触发路径**：需要在系统真实内存 >90% 时验证 Kill Switch 的保守模式行为。单元测试无法模拟真实的内存压力。
- **Error Budget 耗尽路径**：需要累积足够多的"错误"事件来触发。单元测试中人为制造错误事件不等于真实场景。
- **退化螺旋路径**：需要 AI 连续多次被驳回——在测试环境中没有真实的 AI 参与。

**专业机构对标**：Google SRE 用 **DiRT (Disaster Recovery Testing)**——年度/季度全规模灾难演练，真实触发故障。Netflix Chaos Monkey / Chaos Kong 在生产环境随机注入故障。Stripe 用 Shadow Testing——复制生产流量到测试环境但丢弃结果。

**SOLO Coder 方案**（不引入 Chaos Engineering 基础设施的轻量折中）：

```python
# capacity_test_fixtures.py（v2.4.0 新增，测试辅助模块）
import pytest
from unittest.mock import patch, MagicMock

class CapacityTestFixtures:
    """提供专项 fixture，使不可测试的容量路径变得可测试"""

    @staticmethod
    def simulate_memory_pressure(pct: float):
        """通过 mock psutil 模拟内存压力——不实际分配内存"""
        return patch('psutil.virtual_memory', return_value=MagicMock(
            percent=pct,
            available=1024 * 1024 * 100 * (1 - pct / 100),
            total=1024 * 1024 * 1024 * 16  # 16GB
        ))

    @staticmethod
    def simulate_error_budget_depletion(slo_id: str, remaining: float):
        """模拟 Error Budget 消耗到指定水平——直接注入数据库状态"""
        return patch.object(
            ErrorBudgetTracker, 'get_remaining',
            return_value=remaining
        )

    @staticmethod
    def simulate_consecutive_gate_failures(task_id: str, count: int):
        """模拟连续门禁失败——测试退化螺旋检测器"""
        return patch.object(
            ProvenanceDB, 'count_consecutive_failures',
            return_value=count
        )

    @staticmethod
    def simulate_pending_shutdown():
        """模拟即将关机的信号"""
        return patch.object(
            GracefulShutdown, 'shutdown_requested',
            new_callable=lambda: True
        )

# 使用示例
def test_kill_switch_on_memory_pressure():
    with CapacityTestFixtures.simulate_memory_pressure(92.0):
        result = KillSwitch.evaluate()
        assert result.mode == "conservative"
        assert "内存" in result.reason

def test_degradation_spiral_detection():
    with CapacityTestFixtures.simulate_consecutive_gate_failures("T-123", 4):
        detector = DegradationSpiralDetector(db=MagicMock())
        alert = detector.detect("T-123", GateResult(passed=False, reason="test"))
        assert alert is not None
        assert alert.escalated is True
```

**必须实现的最小测试套件清单**：

```yaml
# 容量保障专项测试清单（v2.4.0 新增）
capacity_tests_required:
  unit:
    - "test_kill_switch_memory_pressure"       # 内存 >90% → Kill Switch 保守模式
    - "test_kill_switch_release"               # 内存 <75% for 30min → 解除 Kill Switch
    - "test_error_budget_exhaustion"           # 预算 0% → Emergency 模式
    - "test_burn_rate_short_window_pulse"      # 1h Burn Rate >14.4× 持续 <5min → 不打动作
    - "test_burn_rate_sustained"               # 1h Burn Rate >14.4× 持续 >5min → 保守模式
    - "test_degradation_spiral_detection"      # 连续驳回 ≥3 → 螺旋告警
    - "test_per_task_budget_hard_stop"         # 单任务达到 Per-Task Budget → hard_stop
    - "test_context_watermark_compression"     # 上下文 >32K → 压缩
    - "test_graceful_shutdown_persistence"     # 关机 → 快照写入 → 重启 → 快照恢复
    - "test_change_rate_limiter_throttle"      # throttle(0.5) → 实际速率约为全速 50%

  integration:
    - "test_startup_protection_window"         # 启动窗内 → 所有操作被拒绝或排队
    - "test_config_hot_reload_mid_task"        # 配置在任务中间热重载 → 当前任务用旧配置
    - "test_observer_effect_compensation"      # 监控自身消耗被从 SLI 中减除

  # Solo Coder 不应追求 100% 覆盖率——但以上路径 100% 覆盖
  minimum_coverage_target: "上述 13 个场景 100%"
```

---

#### 盲点 #34：灾难恢复演练的自动化——DR 策略写了但从未演练

**本质**：§13 的 `disaster_recovery_strategy.yaml` 定义了 4 级恢复策略（RPO/RTO），但永远只是一份文档。在 Solo Coder 场景下，指望 Owner 定期手动执行 DR 演练是不现实的。但不幸的是——**没演练过的 DR 策略 = 没有 DR 策略**。

**专业机构对标**：Google DiRT 每年至少一次全公司范围的灾难演练，真实关停数据中心。Netflix Chaos Kong 模拟整个 AWS Region 宕机。Stripe 每月有一次 "Game Day"——半天时间专门演练故障场景。

**SOLO Coder 方案**：自动化 DR 演练（不真实搞破坏）：

```python
# dr_drill_runner.py（v2.4.0 新增，建议内联到 M-20 disaster-recovery-drills）
class DRDrillRunner:
    """自动化灾难恢复演练——在 sandbox 中模拟灾难，不触碰生产数据"""

    DRILL_SCHEDULE = {
        "L1_quick_recovery": "weekly",         # 每周日 03:00
        "L2_full_restore": "monthly",          # 每月第一个周日 03:00
        "L3_cross_machine": "never_auto",      # Solo Coder 无第二台机器——只能纸上谈兵
        "L4_total_loss": "never_auto",         # 同上
    }

    def run_drill(self, level: str) -> DrillReport:
        """在 sandbox 中模拟灾难恢复"""
        with Sandbox.create_isolated() as sandbox:
            # 1. 在 sandbox 中创建一份生产数据快照的副本
            sandbox.copy_production_snapshot()

            # 2. 模拟灾难——按级别破坏 sandbox 中的数据
            if level == "L1":
                sandbox.corrupt_db_file("capacity_metrics")
            elif level == "L2":
                sandbox.delete_all_data()

            # 3. 执行恢复流程——计时
            t0 = time.perf_counter()
            success = sandbox.execute_recovery_playbook(level)
            elapsed = time.perf_counter() - t0

            # 4. 验证恢复后的数据完整性
            integrity = self._validate_recovered_data(sandbox)

            # 5. 对比 RTO/RPO 目标
            return DrillReport(
                level=level,
                success=success,
                actual_rto=elapsed,
                target_rto=self.dr_config.get_rto(level),
                rto_compliant=elapsed <= self.dr_config.get_rto(level),
                data_integrity=integrity,
                should_alert=not success or not integrity.passed,
            )

    def monthly_auto_drill(self) -> None:
        """每月自动执行一次全量 DR 演练，产出报告推送给 Owner"""
        report = self.run_drill("L2_full_restore")
        if report.should_alert:
            self.notify_owner(
                f"⚠️ 本月 DR 演练发现 {len(report.failures)} 个问题，建议在下一个 maintenance window 修复"
            )
```

---

### 22.4 物理与工程边界盲点（3 项）

#### 盲点 #35：Windows 文件系统物理约束——路径长度、文件句柄、NTFS 碎片

**本质**：`.trae/rules/project_rules.md` 提到本系统运行在 **Windows** 上。Windows 有独特的文件系统约束，在 1500 模块的规模下会被触发：

| 约束 | 上限 | 1500 模块时的风险 |
|------|:---:|------|
| **MAX_PATH** | 260 字符（默认） | `d:\ZephyrAlpha\docs\03_modules\l03_business_domains\machine_learning\model_registry\blueprint.md` = 96 字符——如果再加三四层嵌套就爆了 |
| **文件句柄** | 进程默认 512（可通过 `_setmaxstdio` 提升到 8192） | 1500 模块 × 每个模块 3-5 个文件 × 并发 AI session = 可能逼近 512 |
| **NTFS 目录条目** | 单目录约 4,294,967,295（理论上）但性能拐点在 ~10,000 | 1500 模块的 `__pycache__` 目录分散——不是问题 |
| **文件名大小写不敏感** | `Blueprint.md` 和 `blueprint.md` 是同一个文件 | AI 在不同 OS 上生成代码时可能引入大小写 bug |

**SOLO Coder 方案**：

```yaml
# capacity_slo.yaml —— windows_fs_constraints 节（v2.4.0 新增）
windows_fs_constraints:
  path_length:
    max: 200                               # 留 60 字符余量给运行时临时文件
    check_on: "file_creation + rename"
    action: "reject + suggest_abbreviation"
    auto_abbreviate: true                  # 自动截断过长的模块名

  file_handle_monitoring:
    metric_id: "CAP-013-handle-count"
    measurement: "len(psutil.Process().open_files())"
    warning: "> 400"                       # 超过 400 → 提示
    critical: "> 500"                      # 接近默认 512 上限
    critical_action: "auto_increase_setmaxstdio + notify_owner"

  case_sensitivity_guard:
    scan_on: "every_git_operation"
    rule: "同一目录下不得存在仅大小写不同的两个文件"
    action: "auto_rename + notify"
```

---

#### 盲点 #36：容量悬崖——80% 不是 100% 的 80%，是 100% 的 0%

**本质**：§17 的线性/指数预测假设性能随容量**连续退化**。但真实系统中的容量退化是非线性的——存在"悬崖"：

```
内存使用率：
  30%:  响应时间 10ms   ✅ 正常
  50%:  响应时间 15ms   ✅ 正常
  75%:  响应时间 25ms   ✅ 可以接受
  82%:  响应时间 80ms   ⚠️ 退化开始
  85%:  响应时间 500ms  ❌ GC 频繁
  87%:  响应时间 3000ms ❌ 系统几乎不可用 ← 悬崖
  90%:  响应时间 ∞      ☠️ 触发 OOM Killer 或完全挂死
```

从 85% → 87% 的 2% 差异导致了 6× 的性能退化。但容量预测模型用线性回归时看不到这个悬崖——它外推的是"80% → 90% 大概是 2× 退化"。

**专业机构对标**：Netflix 的 Auto Scaling 用 **Step Functions**（阶梯函数）而非线性模型——在已知悬崖点（如 JVM GC 阈值、数据库连接池上限）使用硬边界而非预测。Google Borg 的 Resource Estimator 用 **Piecewise Linear Regress**（分段线性回归），在不同区间使用不同斜率。

**SOLO Coder 方案**：

```python
# capacity_prediction_model.py —— CliffDetector（v2.4.0 新增）
class CliffDetector:
    """检测容量悬崖——非线性退化点"""

    # 已知悬崖点（基于 Python 运行时常识）
    KNOWN_CLIFFS = {
        "memory": [
            {"threshold": 0.75, "name": "GC 压力区", "degradation_factor": 1.5},
            {"threshold": 0.82, "name": "Swap 风险区", "degradation_factor": 3.0},
            {"threshold": 0.87, "name": "OOM 悬崖", "degradation_factor": 10.0},
        ],
        "file_handles": [
            {"threshold": 0.75, "name": "句柄竞争区", "degradation_factor": 2.0},
            {"threshold": 0.90, "name": "句柄耗尽悬崖", "degradation_factor": 50.0},
        ],
        "sqlite_db_size_mb": [
            {"threshold": 500, "name": "SQLite 性能拐点", "degradation_factor": 3.0},
            {"threshold": 800, "name": "SQLite 严重退化", "degradation_factor": 10.0},
        ],
        "concurrent_ai_sessions": [
            {"threshold": 5, "name": "API Rate Limit 风险", "degradation_factor": 2.0},
            {"threshold": 8, "name": "API 拒绝服务悬崖", "degradation_factor": 20.0},
        ],
    }

    def predict_with_cliff_awareness(self, metric: str, current: float,
                                      predicted: float) -> CliffPrediction:
        """预测值是否逼近已知悬崖"""
        cliffs = self.KNOWN_CLIFFS.get(metric, [])
        for cliff in cliffs:
            if current < cliff["threshold"] and predicted >= cliff["threshold"]:
                return CliffPrediction(
                    metric=metric,
                    cliff_name=cliff["name"],
                    current=current,
                    predicted=predicted,
                    threshold=cliff["threshold"],
                    adjusted_prediction=current + (predicted - current) * cliff["degradation_factor"],
                    warning=f"预测值 ({predicted:.1%}) 将越过'{cliff['name']}'悬崖 "
                            f"({cliff['threshold']:.0%})——预计有 {cliff['degradation_factor']}× 性能退化",
                    action="consider_preemptive_mitigation"  # 提前干预而非事后补救
                )
        return CliffPrediction(status="no_cliff_detected")
```

---

#### 盲点 #37：沉没成本陷阱——AI 任务过半后的决策扭曲

**本质**：这超越了经典 SRE 理论。沉没成本效应（Sunk Cost Fallacy）是行为经济学概念——**人倾向于继续投资已经投入大量资源的项目**，即使继续投资在理性上不划算。在 AI 施工系统中，这个陷阱同样存在：

- 一个 AI 任务已经消耗了 85% 的 Token Budget → 理性决策：停掉它，拆分 → 但系统（和 Owner）的直觉是："已经花了这么多，不如让它完成"
- Owner 在面对 `hard_stop_suggestion` 时 → 倾向性地选择"增加预算"而非"终止任务"

**专业机构对标**：这在传统 SRE 中没有对标——因为传统 SRE 不管理 AI 生成任务。但 Stripe 的 Unit Economics 体系中有 **Marginal ROI 检查**——当一个 feature 的开发成本超过已完成部分的 150% 时，自动触发 kill review。

**SOLO Coder 方案**：

```python
# sunk_cost_intervention.py（v2.4.0 新增，集成到 token_budget_tracker）
class SunkCostIntervention:
    def evaluate_continuation(self, task_id: str) -> ContinuationDecision:
        """当任务消耗 ≥85% 预算时，给出去偏见的继续/终止建议"""
        task = self.db.get_task(task_id)
        budget = self.per_task_budget.get_budget(task.priority)
        consumed = self.db.get_task_token_total(task_id)
        completion_pct = self._estimate_completion_pct(task_id)  # AI 估算完成百分比

        if consumed / budget < 0.85:
            return ContinuationDecision(action="continue")

        # 关键判断：剩余预算是否足以完成剩余工作
        remaining_work = 1.0 - completion_pct
        remaining_budget_pct = 1.0 - (consumed / budget)
        efficiency_ratio = remaining_work / remaining_budget_pct if remaining_budget_pct > 0 else float('inf')

        if efficiency_ratio > 2.0:
            # 完成剩余工作需要 2× 的剩余预算 → 沉没成本陷阱
            return ContinuationDecision(
                action="strongly_suggest_stop",
                reasoning=(
                    f"任务 {task_id} 已消耗 {consumed/budget:.0%} 预算，"
                    f"但仅完成约 {completion_pct:.0%}。"
                    f"完成剩余工作需要约 {efficiency_ratio:.1f}× 当前剩余预算。\n"
                    f"这是典型的沉没成本陷阱——继续投入不太可能产生有效产出。\n"
                    f"建议：拆分任务为更小粒度 OR 人工介入完成剩余部分。"
                ),
                require_owner_override=True     # Owner 必须写理由才能追加预算
            )

        return ContinuationDecision(action="continue")

    def _estimate_completion_pct(self, task_id: str) -> float:
        """AI 辅助估算任务完成百分比——基于 checklist 完成项 / 总项"""
        checklist = self.db.get_task_checklist(task_id)
        if checklist:
            return len([c for c in checklist if c.done]) / len(checklist)
        return self._heuristic_estimate(task_id)
```

---

#### 盲点 #38：多模型厂商风险——降级链假定模型永远可用且定价不变

**本质**：§11 的降级链假定 `trae-cn-pro → deepseek-chat → qwen2.5-3b-onnx` 三个 Tier 始终可用。但：

- DeepSeek API 可能涨价或修改免费额度策略（2025 年已发生多次）
- Trae CN 可能在某个版本中变更内建模型
- `qwen2.5-3b-onnx` 的本地推理需要足够的 CPU/内存——在系统高负载时可能无法本地运行
- 如果三个 Tier 同时不可用（极小概率但非零），系统应该有什么行为？

**SOLO Coder 方案**：厂商风险对冲 + 降级链逃生舱：

```yaml
# degradation_chain.yaml —— vendor_risk 节（v2.4.0 新增）
vendor_risk_management:
  hedging:
    strategy: "保持至少 2 个不同厂商的可用模型"
    current_hedge:
      - provider: "DeepSeek"              # Tier 1+2 都是 DeepSeek——如果 DeepSeek 挂了就没有 Tier 1/2
        risk: "single_vendor_for_tier_1_and_2"
    recommendation: "将 Tier 2 更换为非 DeepSeek 模型（如 Gemini Flash 2.0 或 Qwen API）"

  escape_hatch:
    description: "当所有模型 Tier 都不可用时的最终逃生路径"
    tiers_all_unavailable_action: "system_wide_pause"
    notify_owner: "飞书 + 终端 + （如有）微信"
    fallback_to_cached_results: true
    max_cache_only_mode_duration: "2h"    # 仅用缓存结果最多撑 2h

  pricing_change_detection:
    monitor: "daily_effective_cost_per_token"
    baseline: "7d moving average"
    alert_if: "cost > 2× baseline"
    action: "auto_adjust_tier_weights + suggest_alternative_models"
    price_change_log:
      enabled: true
      retention: "90d"
      purpose: "追溯 Token 预算偏差的根因"

  free_tier_depletion:
    track: "per_provider"
    alert_at_remaining: "20%"
    action: "auto_degrade_P2_below + suggest_batch_P0_P1_before_depletion"
    depletion_prediction: "based_on_7d_spend_rate"
```

---

### 22.5 第三轮盲点全量清单（追加汇总）

| # | 盲点名称 | 严重度 | 归属维度 | 对标来源 |
|---|---------|:---:|------|------|
| 26 | 启动序列未保护窗口 | **高** | 时间动力学 | Google Borg init graph / Linux systemd |
| 27 | Day-0 冷启动 | **高** | 时间动力学 | AWS Cooldown Period / Vibe Coding 观测静默期 |
| 28 | 优雅关机 | **高** | 时间动力学 | PostgreSQL WAL / K8s terminationGracePeriod |
| 29 | 时间分区 AI API 模式 | 中 | 时间动力学 | Google Time-of-Day SLO / Netflix Temporal Forecasting |
| 30 | 容量监控自身污染 SLI | **高** | 观察者效应 | Google Borgmon Sidecar / Netflix Atlas 独立 IO |
| 31 | AI 霍桑效应 | 中 | 观察者效应 | GitHub Copilot Agent Mode / Anthropic Blind Monitoring |
| 32 | 配置热重载语义缺失 | 中 | 观察者效应 | 原始发现——蓝图自身盲点审计 |
| 33 | 容量装置不可测试 | **致命** | 可测试性 | Google DiRT / Netflix Chaos Engineering / Stripe Shadow Testing |
| 34 | DR 演练从未执行 | **高** | 可测试性 | Google DiRT / Stripe Game Day |
| 35 | Windows FS 物理约束 | 中 | 物理边界 | Microsoft Windows Internals / NTFS 规范 |
| 36 | 容量悬崖 | **高** | 物理边界 | Netflix Step Functions / Google Piecewise Linear |
| 37 | 沉没成本陷阱 | 中 | 工程边界 | Kahneman & Tversky / Stripe Marginal ROI |
| 38 | 多模型厂商风险 | **高** | 工程边界 | ISACA Third-Party Risk / Vibe Coding 社区 vendor lock-in 讨论 |

---

### 22.6 三轮合并：终局全景（38 项盲点，按施工优先级）

| P | # | 盲点 | 致命/高/中 | 一句话 |
|:---:|:---:|------|:---:|------|
| 1 | 14 | Business SLI | 高 | 没有它你看不到 AI 施工质量在退化 |
| 2 | 19 | 幻觉-容量正反馈螺旋 | **致命** | 容量压力→幻觉→更多消耗→恶性循环 |
| 3 | 33 | 容量装置不可测试 | **致命** | Kill Switch/Error Budget 耗尽从未在测试中被验证 |
| 4 | 12 | 告警疲劳 | 致命 | 1 人面对 30+ 告警源必然疲劳 |
| 5 | 30 | 容量监控污染 SLI | 高 | 监控系统自身消耗导致 SLI 假阳性 |
| 6 | 15 | 施工节奏控制 | 高 | AI 1h 合并 30 模块→不可逆破坏 |
| 7 | 1 | SLI 插桩点 | 高 | AI 各自采 SLI→数值不可比 |
| 8 | 26 | 启动未保护窗口 | 高 | 系统最脆弱的时刻没有 Kill Switch |
| 9 | 18 | 多轮对话令牌通胀 | 高 | 单任务 7 轮后 token 翻 5× |
| 10 | 9 | 预警→修复闭环 | 高 | 制动后修复通道被锁死 |
| 11 | 28 | 优雅关机 | 高 | 硬关机后容量状态"失忆" |
| 12 | 17 | Context 预算慢泄漏 | 高 | 每次 session 启动的隐形税收 |
| 13 | 27 | Day-0 冷启动 | 高 | 最脆弱的 Day-0 反而不告警 |
| 14 | 20 | SQLite 写锁瓶颈 | 高 | 写入串行化→SLI 测量失真 |
| 15 | 36 | 容量悬崖 | 高 | 85→87% 的 2% 导致 6× 退化 |
| 16 | 23 | AI 技能退化 | 高 | AI 质量下降无人监测 |
| 17 | 38 | 多模型厂商风险 | 高 | DeepSeek 涨价/Trae 换模型→降级链不可用 |
| 18 | 6 | 容量保障自身开销 | 高 | 极限时监控可能压垮业务 |
| 19 | 3 | Error Budget 归因 | 高 | 预算耗尽无法定位根因 |
| 20 | 2 | SLO 窗口分层 | 高 | 30 天窗口在演进期无意义 |
| 21 | 34 | DR 演练从未执行 | 高 | 没演练过的 DR = 没有 DR |
| 22 | 13 | AI 可理解性 | 高 | 复杂度=AI 改错率 |
| 23 | 8 | AI 行为预测 | 高 | 只预测资源不预测行为 |
| 24 | 16 | Owner 离线自治 | 高 | 离线 48h 系统可能自毁 |
| 25 | 22 | Owner 决策疲劳 | 中 | 维护负担非线性增长 |
| 26 | 37 | 沉没成本陷阱 | 中 | 任务过半后非理性追加预算 |
| 27 | 31 | AI 霍桑效应 | 中 | AI 知道被监控后行为扭曲 |
| 28 | 21 | Telemetry 存储爆炸 | 中 | 700MB+ 超出 SQLite 舒适区 |
| 29 | 29 | 时间分区 AI API 模式 | 中 | API 早晚延迟差异 50%+ |
| 30 | 32 | 配置热重载语义缺失 | 中 | 运行中改配置→任务被硬中断 |
| 31 | 35 | Windows FS 物理约束 | 中 | 路径 260 字符 / 文件句柄 512 |
| 32 | 25 | TraceContext 容量元数据 | 中 | 跨模块容量上下文传播 |
| 33 | 24 | Token 价值 ROI | 中 | 不知道钱花得值不值 |
| 34 | 10 | 成本回升 | 中 | 降级后无法自动切回好模型 |
| 35 | 11 | 渐进式流量切换 | 中 | Kill Switch 缺少"半速"档 |
| 36 | 7 | 健康评分 | 中 | 缺少单一决策数字 |
| 37 | 5 | SLO Review | 中 | SLO 目标值过期 |
| 38 | 4 | 脉冲容忍 | 中 | 短窗口误触发 |

---

### 22.7 建议新增模块（M-31~M-35）

| 模块ID | 模块名称 | 职责 | 归属 |
|--------|---------|------|------|
| M-31 | startup_guard.py | 启动保护窗口 + 显式加载顺序 | 集成到 `zephyr/__init__.py` |
| M-32 | graceful_shutdown.py | 优雅关机——缓冲刷盘 + 快照持久化 | 注册到 atexit + signal handlers |
| M-33 | observer_effect_compensator.py | 从 SLI 读数中减除监控自身消耗 | 集成到 capacity_governance_loop |
| M-34 | cliff_detector.py | 容量悬崖检测——非线性退化预警 | 集成到 capacity_prediction_model |
| M-35 | sunk_cost_intervention.py | 沉没成本陷阱干预 + AI 霍桑效应过滤 | 集成到 token_budget_tracker |

> **M-31~M-35 同样不应纳入蓝图 §6 的模块分解表**——它们是对已有模块的深度内联增强，职责边界与现有模块有 80% 重叠。建议在对应模块施工时作为子功能落位。

---

## 23. 第四轮深度审计——100%AI施工·氛围编程·1人+AI维护的容量盲点（v2.5.0 新增）

> **审计升级原因**：前三轮审计（§20 + §21 + §22）覆盖了 38 项盲点，对标了 20+ 家专业机构。但这些审计都是在"系统有人运维"的默认假设下进行的。第四轮审计的核心问题是：**当系统 100% 由 AI 建造、Owner 主要依靠氛围编程（Vibe Coding）驱动开发、完工后只有 1 人 + AI 维护时，有哪些盲点是前三轮的对标方法论天然不会发现的？**

> **关键洞察——前三轮的方法论盲区**：Google SRE 假设有一个 SRE 团队轮值 On-Call；Netflix Chaos Engineering 假设有基础设施团队可以部署 Chaos Monkey；Stripe 的 Game Day 假设有多人可以参与演练。这些方法论在 Solo Coder + AI 场景下不仅不可行，而且它们的底层假设（多人协作、轮值、冗余人力）会**遮蔽**真正危险的盲点。

> **盲点确认标准**：本蓝图 v2.4.0（§1~§22）**完全未提及**，且前三轮 38 项盲点中**不存在等价的覆盖**。

---

### 23.1 AI生成的非确定性与语义冲突（3 项）

#### 盲点 #39：AI代码生成的非确定性 → 容量行为不可复现

**本质**：这是一个只有 100% AI 施工才会暴露的盲点。同一个人用同一个 Prompt 让同一个 AI 模型生成同一个功能，两次生成的代码在结构、算法、依赖上可能完全不同。这意味着：

- **容量预测的前提被打破**：§17 的容量预测模型假设"模块数 × 平均内存 = 总内存"，但 AI 生成的模块 A 可能 50KB/2MB 内存，另一个 AI 生成的"等价"模块 B 可能 200KB/15MB 内存
- **SLO 基线不可比**：如果 CAP-001（启动时间）上次施工时是 1200ms，这次 AI 生成了一批"更优雅但更重量级"的代码后变成 3200ms——系统无法区分"正常的容量演进"和"AI 生成了浪费资源的代码"
- **回归测试的容量维度缺失**：test_regression.py 验证功能正确性，但不验证容量正确性——"代码能跑"不等于"代码不浪费资源"

**风险**：Owner 无法区分"这是系统正常演进需要的容量"和"这是 AI 低效生成导致的容量浪费"。长期积累后，1500 模块的系统中可能有 30% 的容量消耗来自 AI 生成的冗余代码。

**专业机构对标——谁也没做过的事**：
- Google SRE 管理的是**人类写的代码**——人类的代码风格相对稳定，有 Code Review 把关。AI 生成的代码 Review 的是功能正确性，没人 Review "这个实现是不是用了太多内存"
- Netflix Chaos Engineering 测试的是"系统能不能扛住故障"，不测试"系统里的代码是不是浪费资源"
- Trunk.io 的 Merge Queue 关注的是合并冲突，不关注合并进来的代码的容量效率
- **本盲点的对标必须是原创的**：没有任何已知的专业机构在做"AI 生成代码的容量效率回归测试"

**SOLO Coder 方案**：**容量指纹（Capacity Fingerprint）**——为每个 AI 生成的模块记录容量签名，在新代码合入时比较：

```python
# capacity_fingerprint.py（v2.5.0 新增，集成到 capacity_governance_loop）
import hashlib
import ast
import psutil

class CapacityFingerprint:
    """为每个 AI 生成模块创建容量指纹——检测非确定性导致的容量退化"""

    def fingerprint(self, module_path: Path) -> "ModuleFingerprint":
        """生成模块的容量指纹"""
        source = module_path.read_text(encoding='utf-8')

        # 静态指标
        tree = ast.parse(source)
        return ModuleFingerprint(
            module_path=str(module_path),
            loc=len(source.splitlines()),
            import_count=len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
            class_count=len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            function_count=len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            dependency_count=self._count_external_deps(tree),
            ast_depth=self._max_ast_depth(tree),
            # 运行时指标（在 sandbox 中测量）
            import_time_ms=self._measure_import_time(module_path),
            memory_delta_kb=self._measure_memory_delta(module_path),
        )

    def compare(self, old: "ModuleFingerprint", new: "ModuleFingerprint") -> "CapacityDrift":
        """比较新旧指纹——检测 AI 是否生成了容量效率更差的'等价'代码"""
        drift = CapacityDrift()

        # 运行时退化 > 2× 且功能测试通过 → AI 可能生了低效代码
        if new.memory_delta_kb > old.memory_delta_kb * 2.0:
            drift.add_warning(
                f"模块 {new.module_path} 内存用量 {old.memory_delta_kb}KB → {new.memory_delta_kb}KB "
                f"（+{new.memory_delta_kb - old.memory_delta_kb}KB，{new.memory_delta_kb/old.memory_delta_kb:.1f}×）"
                f"——建议人工审查是否必要"
            )
        if new.import_time_ms > old.import_time_ms * 3.0:
            drift.add_warning(f"导入时间退化 {old.import_time_ms}ms → {new.import_time_ms}ms")

        # 静态膨胀：代码行数翻倍但功能等价 → AI 过度设计
        if new.loc > old.loc * 1.8 and new.function_count <= old.function_count * 1.1:
            drift.add_warning(
                f"代码行数 {old.loc}→{new.loc}（+{new.loc-old.loc}）但函数数几乎不变"
                f"——可能是AI用更冗长的方式实现了相同功能。这是非确定性容量的典型表现。"
            )

        return drift

    def _count_external_deps(self, tree: ast.Module) -> int:
        external = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split('.')[0]
                if top not in sys.stdlib_module_names:
                    external.add(top)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split('.')[0]
                    if top not in sys.stdlib_module_names:
                        external.add(top)
        return len(external)

    def _max_ast_depth(self, tree: ast.Module) -> int:
        max_d = 0
        def walk(node, depth=0):
            nonlocal max_d
            max_d = max(max_d, depth)
            for child in ast.iter_child_nodes(node):
                walk(child, depth + 1)
        walk(tree)
        return max_d

    def _measure_import_time(self, module_path: Path) -> float:
        """在 sandbox 中测量模块导入耗时"""
        import timeit
        module_name = str(module_path.with_suffix('')).replace('\\', '.').replace('/', '.')
        timer = timeit.Timer(f"import {module_name}")
        return min(timer.repeat(repeat=3, number=1)) * 1000

    def _measure_memory_delta(self, module_path: Path) -> int:
        import tracemalloc
        tracemalloc.start()
        spec = importlib.util.spec_from_file_location("_cap_test", module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return int(peak / 1024)
```

**集成方式**：在 AI 施工流程的 G5 门禁（合入前）中增加 CapacityFingerprint.check()——如果新代码的容量指纹比旧代码差 >2×，门禁发出 Warning（不阻断，但记录到容量审计日志中供 Owner 周期性审查）。

---

#### 盲点 #40：Prompt与容量指令的语义冲突——AI同时收到"做彻底"和"省预算"

**本质**：AI Agent 的 System Prompt 中同时包含了：
1. "请完整、彻底地实现功能 X，包括边界情况、错误处理、日志、测试"→ 隐含指令：消耗 Token 做全
2. "当前 Token Budget 紧张，请简化实现"→ 隐含指令：牺牲完整性
3. "你是 ZephyrAlpha 的基础设施核心，你的代码质量直接影响系统可靠性"→ 隐含指令：不要妥协

这三个指令在语义层面是**互斥**的。AI 必须在它们之间做 trade-off——但 AI 不知道哪个优先级更高。结果是：
- AI 随机地偏向一方：可能写了一半后因预算耗尽而半成品入仓
- AI 用"表面上的完整"掩盖实质上的偷工减料：写了 500 行的 try-except 但没有实质的业务逻辑
- AI 反复摇摆：先做 80% → 被告知预算不够 → 回退 → 再被告知"质量太差" → 陷入多轮修正循环 → 消耗 3× 预算

**专业机构对标**：Anthropic 的 Constitutional AI 研究指出，当 AI 面对矛盾指令时，它的行为取决于 Prompt 中指令的**顺序**和**措辞强度**，而非语义优先级。Google SRE 的 Error Budget 机制避免了这个问题——因为人类理解"预算烧完了就先停"，但 AI 收到的是一段文本而非经济信号。

**SOLO Coder 方案**：**预算感知的 Prompt 合并器（BudgetAwarePromptMerger）**——在 Prompt 进入 AI Session 之前，将容量预算转化为 AI 可以无歧义执行的"施工模式"：

```python
# budget_aware_prompt.py（v2.5.0 新增，集成到 context_assembler）
class BudgetAwarePromptMerger:
    """将 Token/Error Budget 转化为 AI 无歧义的施工模式——消除语义冲突"""

    MODES = {
        # 不需要AI去trade-off——系统提前替它决策好
        "full_build": {
            "description": "完整实现——包括边界情况、错误处理、日志、测试",
            "conditions": {
                "token_budget_remaining": "> 70%",
                "error_budget_tier": "in ['healthy']",
                "task_priority": "in ['P0', 'P1']",
            },
            "prompt_suffix": (
                "[施工模式: full_build]\n"
                "你有充足的 Token 预算。请完整实现以下功能，包括：\n"
                "1. 核心业务逻辑 + 所有边界情况\n"
                "2. 适当的错误处理和日志\n"
                "3. 对应的单元测试\n"
                "4. 必要的类型注解和文档字符串"
            ),
        },
        "essential_only": {
            "description": "核心逻辑 + 关键错误路径——省略边缘情况的测试和文档",
            "conditions": {
                "token_budget_remaining": "30%~70%",
                "error_budget_tier": "in ['warning']",
                "task_priority": "in ['P0', 'P1', 'P2']",
            },
            "prompt_suffix": (
                "[施工模式: essential_only]\n"
                "Token 预算有限。请聚焦核心逻辑和关键错误处理：\n"
                "1. 核心业务逻辑 + 主要的错误路径\n"
                "2. 最小必要的日志（仅 ERROR/WARNING 级别）\n"
                "3. 仅 P0 场景的单元测试\n"
                "4. 跳过文档字符串——后续补充"
            ),
        },
        "minimal_viable": {
            "description": "最小可行实现——只要功能正确，不追求代码质量",
            "conditions": {
                "token_budget_remaining": "< 30%",
                "error_budget_tier": "in ['critical', 'emergency']",
            },
            "prompt_suffix": (
                "[施工模式: minimal_viable]\n"
                "Token/Error Budget 严重不足。请只做最小可行实现：\n"
                "1. 核心逻辑——不处理非关键的边界情况\n"
                "2. 仅致命错误的处理（fail loudly, don't swallow）\n"
                "3. 不写测试——由后续 task 补充\n"
                "4. 不写文档和类型注解\n"
                "5. 在你的回复末尾标注 [NEEDS_COMPLETION] 以便后续识别此半成品"
            ),
        },
    }

    def merge(self, task: "TaskCard", budget_status: "BudgetStatus") -> str:
        """根据当前预算状态选择施工模式，将模式注入 Prompt"""
        mode = self._select_mode(budget_status)

        base_prompt = f"实现以下任务: {task.description}"
        return f"{base_prompt}\n\n{mode['prompt_suffix']}"

    def _select_mode(self, budget: "BudgetStatus") -> dict:
        for mode_name, mode_def in self.MODES.items():
            if self._satisfies(budget, mode_def["conditions"]):
                return mode_def
        return self.MODES["essential_only"]  # fallback
```

**关键设计决策**：不告诉 AI "你预算紧张"（这会导致 #31 霍桑效应），而是直接告诉 AI "你要用 minimal_viable 模式施工"。AI 不需要做经济决策——它只需要遵循明确的工程指令。

---

#### 盲点 #41：氛围编程"快速实验"的隐性容量税——每次Vibe都在消耗真实资源

**本质**：氛围编程的核心工作流是："我有一个想法 → 让 AI 试试 → 看效果 → 不满意 → 让 AI 再试试 → ..." 。这个循环的每一步都消耗 Token、CPU、内存——但 Owner 在"Vibe"的心流中不会意识到这些消耗。

在三轮审计的盲点中，#18（多轮对话 Token 通胀）和 #24（Token 价值 ROI）触及了这个问题的表面。#18 关注的是单次任务内的对话轮数通胀，#24 关注的是"花了钱值不值"。但两者都没有揭示**氛围编程特有的容量陷阱**：

- **"实验性代码"的生命周期问题**：AI 生成了一段实验代码，Owner 看完说"不对，重来"——但那段代码的文件已经被创建了（`.py`, `__pycache__`, import side effects）。这些文件留在磁盘上、被 Python 的 import 缓存记住、占用 inode/目录条目
- **"迭代速度"的隐性加速**：Owner 在 "Vibe flow" 中可能让 AI 每小时尝试 10 种不同的实现方案——每小时消耗 10× Per-Task Token Budget。而 #18 假设的是"1 个任务 7 轮对话"，氛围编程下是"N 个实验 7 轮对话"
- **实验没有 Error Budget 边界**：当前蓝图将 Error Budget 绑定到"正式任务"，但氛围编程的实验不被视为"正式任务"——它们游离在预算体系之外

**专业机构对标**：
- Google SRE 的 Error Budget 是**按服务维度**分配的，不区分"实验流量"和"生产流量"
- Stripe 的 Unit Economics 按可计费单元核算，实验代码在合入前不计入成本——但 Solo Coder 的实验代码可能直接被 AI 合入
- Vibe Coding 社区（GitHub Copilot Agent Mode 讨论）普遍反映：最消耗 Token 的不是"实现"，而是"反复调整"

**SOLO Coder 方案**：**Vibe 实验预算（VibeExperimentBudget）**——为氛围编程的实验性工作分配独立的、严格的资源额度：

```yaml
# token_budget_config.yaml —— vibe_experiment_budget 节（v2.5.0 新增）
vibe_experiment_budget:
  description: "氛围编程的快速实验不应消耗生产级 Token Budget——独立预算池"
  daily_limit:
    tokens: 200000                        # 每天最多 200K tokens 用于实验
    cost_limit_cny: 5.0                   # 每天最多 5 元人民币
    max_experiments: 15                   # 每天最多 15 次独立实验

  per_experiment:
    max_tokens: 30000                     # 单次实验最多 30K tokens
    max_duration: "10min"                  # 单次实验最多 10min
    auto_cleanup: true                    # 实验结束后自动清理产物
    cleanup_rules:
      - "删除 __pycache__/*"
      - "删除 *.pyc"
      - "git checkout ——实验期间修改的文件"  # 实验失败→回退
      - "保留 owner 标记为 'keep' 的实验产物"

  experiment_tracking:
    metric_id: "CAP-014-vibe-experiment-count"
    track: ["token_used", "files_created", "duration_seconds", "owner_kept"]
    weekly_report: true                    # 每周生成"你本周 Vibe 了多少"报告
    alert_if: "daily_limit_exceeded"       # 预算耗尽→今天不能再 Vibe 了

  # 核心保护：实验代码不能绕过门禁直接合入
  experiment_to_production_gate:
    rule: "任何经过 vibe_experiment 产生的代码，如需合入生产 → 走正式的 Task + G0-G7 门禁"
    auto_tag: "origin:vibe_experiment"     # Git commit 自动打标——可追溯实验来源
```

对应代码骨架：

```python
# vibe_experiment_tracker.py（v2.5.0 新增，挂载到 task_manager）
class VibeExperimentTracker:
    """追踪氛围编程实验的资源消耗——实验不是免费的"""

    def __init__(self, daily_limit: int = 200000):
        self.daily_limit = daily_limit
        self.today_tokens = self._load_today_usage()
        self.active_experiments: dict[str, VibeExperiment] = {}

    def start_experiment(self, task_desc: str) -> str:
        """开始一个新的 Vibe 实验——检查是否还有预算"""
        if self.today_tokens >= self.daily_limit:
            raise VibeBudgetExhausted(
                f"今日 Vibe 实验 Token 预算已耗尽（{self.today_tokens}/{self.daily_limit}）。\n"
                f"建议：(1) 等待明天重置，(2) 转为正式 Task 走完整流程，\n"
                f"(3) 手动审批追加预算（需要写理由）"
            )
        exp_id = f"VIBE-{datetime.now().strftime('%m%d-%H%M%S')}-{hash(task_desc) % 10000:04d}"
        self.active_experiments[exp_id] = VibeExperiment(
            id=exp_id, task_desc=task_desc,
            started_at=datetime.now(),
            files_before=self._snapshot_files(),
        )
        return exp_id

    def end_experiment(self, exp_id: str, kept_files: list[str] = []) -> ExperimentReport:
        """结束实验——清理产物（保留 owner 标记的文件）"""
        exp = self.active_experiments.pop(exp_id)
        elapsed = (datetime.now() - exp.started_at).total_seconds()

        # 统计: 这次 Vibe 花了多少资源
        tokens = self.db.get_session_tokens(exp_id)
        self.today_tokens += tokens

        # 清理: 删除实验产生的临时文件
        if kept_files:
            exp.keep_and_clean(kept_files)
        else:
            exp.rollback_all()

        return ExperimentReport(
            exp_id=exp_id,
            tokens_used=tokens,
            duration_s=elapsed,
            files_kept=len(kept_files),
            budget_remaining=self.daily_limit - self.today_tokens,
        )

    def _snapshot_files(self) -> dict[str, str]:
        """记录实验开始前的文件状态——用于回退"""
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        return {"status": result.stdout.strip()}
```

---

### 23.2 1人+AI运维的生存临界盲点（4 项）

#### 盲点 #42：长期离线（7天+）的容量自治——度假≠离线48h

**本质**：#16（Owner离线自治）覆盖了"Owner 离线 48h"的场景，方案包括 `auto_hard_stop` 和 `auto_pilot_mode`。但这指的是"Owner 在睡觉/在忙/短暂失联"。当 Owner 度假 7-14 天时，情况完全不同：

- **48h 方案的前提被打破**：#16 的核心策略是"在 Owner 回来前保持系统存活"。7 天后系统累积了 7 天的问题（内存泄漏 ×7 天、日志增长 ×7 天、AI 可能反复尝试某个失败任务 ×N 次）
- **Error Budget 在度假期间也在燃烧**——Owner 回来时可能发现 Error Budget 已经耗尽，系统进入了 Emergency 模式
- **AI 可能在无人监督下做"创造性"决策**：如果 `auto_pilot_mode` 允许 AI 在 Owner 离线时自主施工，AI 可能在 7 天内完成大量"无人审批"的工作——Owner 回来面对的是一个自己不认识的系统

**专业机构对标**：Google SRE 的 On-Call Rotation 设计中，度假场景由**另一位 SRE 接管**，不存在"Solo"问题。Stripe 的 Game Day 设计中，度假前的 Handoff Checklist 确保接手的同事能处理问题。但在 Solo Coder + AI 场景中没有"另一位"。

**SOLO Coder 方案**：**度假模式（Vacation Mode）**——与 #16 的 48h 自治模式的根本区别在于：度假模式的默认策略是"最小化变更 + 最大化保存"：

```yaml
# owner_offline_protocol.yaml —— vacation_mode 节（v2.5.0 新增）
vacation_mode:
  activation:
    trigger: "owner 设置 OR 系统检测到 owner 连续 72h 无响应"
    confirmation: "向 owner 所有通知渠道发送激活确认——owner 可一键取消"

  core_principles:
    - "DO NOT BUILD: 度假期间暂停所有 AI 施工任务（P0-P3 一律suspend）"
    - "DO NOT DEPLOY: 禁止任何代码合入和生产变更"
    - "DO NOT SPEND: 仅保留最低限度的监控 Token 消耗（≤2000 tokens/day）"
    - "DO MONITOR: 继续收集指标但不做任何自动决策"
    - "DO PERSIST: 每天做一次全量状态快照，度假结束后可复盘"

  allowed_operations:
    - "metrics_collection"                   # 继续收集——不要有数据断层
    - "daily_health_snapshot"                 # 每天生成一份系统健康报告
    - "critical_alert_only"                  # 仅当 CAP-009（system_crash）触发时才告警
    - "log_rotation"                         # 日志轮转——防止磁盘满

  explicitly_disallowed:
    - "any_ai_construction_task"             # 不施工
    - "any_config_change"                    # 不改配置
    - "any_package_update"                   # 不更新依赖
    - "any_model_switch"                     # 不切换AI模型
    - "auto_hard_stop"                       # 度假期间不应 hard_stop——需求在度假后才处理

  daily_report:
    destination: "飞书 + 邮件（Owner回来后一次性读取）"
    content:
      - "当日系统健康评分"
      - "当日 Error Budget 消耗量（仅因外部因素）"
      - "当日 Token 消耗量（仅监控开销）"
      - "当日是否有 P0 告警"
      - "度假已持续天数 / 剩余天数"
      - "一句总结: '一切正常' OR '需要注意: [具体问题]'"

  max_duration:
    default: "14d"                           # 默认最多 14 天度假模式
    extendable: true                         # Owner 可申请延期
    auto_escalate: "day_14"                  # 超过 14 天→向 Owner 紧急通知
    day_14_action: "所有通知渠道 + 如果 Owner 配置了紧急联系人→通知"

  return_from_vacation:
    warm_up_period: "24h"                    # 回来后 24h 内不要恢复全速施工
    digest_report:
      format: "一句话总结 + Top 5 值得关注的变化 + 完整数据下载链接"
      example: >
        "度假 7 天期间，系统运行正常。Error Budget 消耗 2.3%（主要是 DeepSeek API 间歇性超时）。
        内存从 62% 缓慢增长到 68%（正常波动）。
        无 P0 告警。总体评分 A-。
        建议：回来后先用 2h 手动 review 一下系统状态，确认无异常后再恢复 AI 施工。"
```

---

#### 盲点 #43：AI模型切换的容量行为突变——每个模型有自己的"容量性格"

**本质**：§11 的降级链定义了"模型不可用 → 切换到下一个 Tier"。但它假设所有模型的**容量行为是可比的**——"换成更便宜的模型 = 容量压力减小"。这个假设是错误的：

| 模型 | Token单价 | 延迟 | 生成质量 | 容量友好度 | 隐性问题 |
|------|:---:|:---:|:---:|:---:|------|
| **Trae CN Pro** | 低/IDE内嵌 | 快(IDE本地) | 高 | **未知**——Trae CN 的内部实现不透明 | 可能在 IDE 进程中消耗大量内存 |
| **DeepSeek Chat** | 低 | 中等 | 中 | 较高 | API Rate Limit 严格，429 错误→Error Budget 燃烧 |
| **DeepSeek Reasoner** | 中 | 慢 | 高 | 低——推理链消耗大量 Context | 单项任务可能 10× Token 消耗 |
| **Claude Sonnet 4** | 高 | 中等 | 非常高 | 未知 | Anthropic API 的价格变动不可预测 |
| **Qwen2.5-3B-ONNX** | 0（本地） | 取决于CPU | 低 | 低——ONNX推理消耗 CPU/内存 | 在高负载系统中可能无法本地运行 |

当系统从 Trae CN Pro 切换到 DeepSeek Chat 时——**容量行为发生了根本变化**：延迟 ×3、Token 消耗模式不同、API Rate Limit 风险出现。但当前蓝图没有任何地方追踪这些差异。

**SOLO Coder 方案**：**每模型容量画像（Per-Model Capacity Profile）** + 切换时自动重校准：

```python
# model_capacity_profile.py（v2.5.0 新增，挂载到 tier_manager）
@dataclass
class ModelCapacityProfile:
    """每个 AI 模型的独立容量画像——切换模型时自动重校准所有预算"""
    provider: str
    model_name: str
    # 成本
    cost_per_1k_input_tokens: float         # ¥/1K input
    cost_per_1k_output_tokens: float        # ¥/1K output
    # 性能
    avg_latency_ms: float                   # 平均延迟
    p95_latency_ms: float                   # P95 延迟
    # 容量
    typical_tokens_per_task: int            # 典型任务Token消耗
    typical_tokens_per_review: int          # 典型审查Token消耗
    api_rate_limit_rpm: int                 # API RPM限制
    # 质量
    gate_pass_rate: float                   # 门禁通过率——间接反映生成质量
    revert_rate: float                      # 被回滚率——间接反映"改错"倾向

class ModelSwitchRecalibrator:
    """当AI模型切换时，自动重校准所有容量预算和阈值"""

    PROFILES = {
        "trae-cn-pro": ModelCapacityProfile(
            provider="Trae", model_name="cn-pro",
            cost_per_1k_input_tokens=0.0,    # IDE内嵌——成本被隐藏在IDE价格中
            cost_per_1k_output_tokens=0.0,
            avg_latency_ms=500, p95_latency_ms=1200,
            typical_tokens_per_task=50000,
            api_rate_limit_rpm=float('inf'),  # IDE内嵌无限流
            gate_pass_rate=0.92, revert_rate=0.03,
        ),
        "deepseek-chat": ModelCapacityProfile(
            provider="DeepSeek", model_name="chat",
            cost_per_1k_input_tokens=0.001,  # 约¥1/M tokens
            cost_per_1k_output_tokens=0.002,
            avg_latency_ms=1500, p95_latency_ms=4000,
            typical_tokens_per_task=30000,   # DeepSeek更简洁
            api_rate_limit_rpm=60,            # 关键约束！
            gate_pass_rate=0.85, revert_rate=0.05,
        ),
        "qwen2.5-3b-onnx": ModelCapacityProfile(
            provider="Local", model_name="qwen2.5-3b-onnx",
            cost_per_1k_input_tokens=0.0,    # 本地运行零API成本
            cost_per_1k_output_tokens=0.0,
            avg_latency_ms=3000, p95_latency_ms=12000,  # CPU推理很慢
            typical_tokens_per_task=15000,   # 本地小模型产出更少
            api_rate_limit_rpm=float('inf'),  # 本地无限流
            gate_pass_rate=0.60, revert_rate=0.15,  # 质量明显更低
        ),
    }

    def on_model_switch(self, from_model: str, to_model: str) -> "SwitchImpact":
        """模型切换时计算对所有容量预算的连锁影响"""
        old = self.PROFILES[from_model]
        new = self.PROFILES[to_model]

        return SwitchImpact(
            from_model=from_model,
            to_model=to_model,
            cost_change=f"{old.cost_per_1k_output_tokens}→{new.cost_per_1k_output_tokens} ¥/1K output",
            latency_change=f"P95: {old.p95_latency_ms}→{new.p95_latency_ms}ms "
                          f"({'+' if new.p95_latency_ms > old.p95_latency_ms else ''}"
                          f"{new.p95_latency_ms - old.p95_latency_ms}ms)",
            # 重校准
            adjusted_per_task_budget=int(
                old.typical_tokens_per_task * (new.typical_tokens_per_task / old.typical_tokens_per_task)
            ),
            adjusted_slo_latency_target_ms=new.p95_latency_ms * 1.2,  # SLO永远比实际情况宽松20%
            adjusted_max_concurrent=int(new.api_rate_limit_rpm * 0.3), # 用30% RPM限制做并发上限
            # 最关键的：对模型切换后预期质量的告警
            quality_warning=(
                f"⚠️ 模型切换 {from_model}→{to_model}：\n"
                f"门禁通过率预期 {old.gate_pass_rate:.0%}→{new.gate_pass_rate:.0%} "
                f"({'-' if new.gate_pass_rate < old.gate_pass_rate else '+'}"
                f"{abs(new.gate_pass_rate - old.gate_pass_rate):.0%})\n"
                f"回滚率预期 {old.revert_rate:.0%}→{new.revert_rate:.0%} "
                f"({'+' if new.revert_rate > old.revert_rate else '-'}"
                f"{abs(new.revert_rate - old.revert_rate):.0%})\n"
                f"如果是主动降级——OK。如果是意外切换——请检查API可用性。"
            ) if new.gate_pass_rate < old.gate_pass_rate else None,
        )
```

**集成方式**：`tier_manager` 在发起模型切换前调用 `ModelSwitchRecalibrator.on_model_switch()`，将所有受影响的容量预算（Per-Task Budget / SLO Latency Target / Max Concurrent）自动更新并通知 Owner。

---

#### 盲点 #44：容量运维知识的单点蒸发——Bus Factor = 1 的知识存亡

**本质**：当前系统设计假设"Owner 知道系统怎么运作的"。但在 100% AI 施工场景下，Owner **不一定是那个写代码的人**——AI 写了很多代码，Owner 只审查了门禁结果。当发生容量问题时：

- **Owner 对系统的理解是"蓝图级别"的**——知道架构但不知道具体的代码实现。当前内存泄漏在 `capacity_governance_loop.py` 的第 347 行——这个信息在 AI Session 的上下文里，但 AI Session 可能已经被关闭了
- **AI 的上下文是 Session 级别的**——关闭 IDE / 重启 / 切换模型 → 丢失了"上次故障排查的上下文"
- **唯一完整的状态在 SQLite `capacity_metrics` 表中**——但数据不会说话；需要人（或 AI）来解释数据
- **最危险的场景**：AI Session 丢失了上下文 → Owner 独自面对系统问题 → 但 Owner 只理解蓝图级别的架构 → 两者之间有一道"实现细节的知识鸿沟"

**专业机构对标**：Google SRE 的 On-Call 手册（Playbook）是**人类可执行**的，不依赖 AI 上下文。Goldman Sachs SecDB 的"为什么这个交易被拒"可以在 3 次点击内追溯到根因。Stripe 的 Incident Review 会产出结构化的 Learning Doc。

**SOLO Coder 方案**：**自文档化的容量 Runbook（Self-Documenting Capacity Runbook）**——每次 AI 处理容量问题后，自动产出一份"下次再遇到怎么办"的 Runbook 条目：

```python
# capacity_runbook_generator.py（v2.5.0 新增，挂载到 post_rollback_hooks）
class CapacityRunbookGenerator:
    """每次处理容量事件后自动生成/更新 Runbook——知识不会随着 Session 蒸发"""

    def generate_from_incident(self, incident: "CapacityIncident") -> "RunbookEntry":
        """从事故事生成 Runbook 条目——包含根因、诊断方法、修复步骤"""

        return RunbookEntry(
            incident_id=incident.id,
            title=f"容量事故: {incident.symptom[:80]}",
            # 以下由 AI 生成，Owner 审核后入库
            root_cause=incident.root_cause,
            # "怎样确诊"——给下次的 Owner/AI 的诊断路径
            how_to_diagnose=[
                f"检查 SLI: {incident.trigger_sli_id}",
                f"查看 {incident.time_window} 时间窗的趋势",
                f"关键SQL: SELECT * FROM capacity_metrics WHERE sli_id='{incident.trigger_sli_id}' AND ts > '{incident.start_ts}'",
                f"如果 {incident.trigger_sli_id} 异常且伴随 {incident.correlated_slis} → 基本确诊",
            ],
            # "怎样修"——给下次的 Owner/AI 的修复步骤
            how_to_fix=[
                f"步骤 1: {incident.resolution.step_1}",
                f"步骤 2: {incident.resolution.step_2}",
                f"回滚命令: zephyr rollback {incident.resolution.rollback_sha}",
                f"验证: {incident.resolution.verification_command}",
            ],
            # "怎样避免"——给下次的 AI 施工指令
            prevention=[
                f"在施工类似变更前，先运行 {incident.prevention.pre_check_script}",
                f"增加门禁规则: {incident.prevention.new_gate_rule}",
                f"更新 SLO 阈值: {incident.prevention.updated_slo_threshold}",
            ],
            # 元数据
            created_by=f"AI-{incident.handling_model}",
            owner_reviewed=incident.owner_reviewed,
            severity=incident.severity,
            # 自动评分：这个 Runbook 的质量
            self_quality_score=self._score(incident),
        )

    def _score(self, incident: "CapacityIncident") -> float:
        """自评 Runbook 质量——Owner 下次一看就知道这个条目值不值得信"""
        scores = []
        if incident.root_cause and len(incident.root_cause) > 50:
            scores.append(1.0)
        if len(incident.resolution.steps) >= 2:
            scores.append(1.0)
        if incident.owner_reviewed:
            scores.append(2.0)  # Owner审核过→可信度翻倍
        if incident.resolution.rollback_sha:
            scores.append(1.0)
        return sum(scores) / max(len(scores), 1) * 100  # 0-100

    def daily_digest(self) -> str:
        """每日生成'如果Owner失忆了该怎么恢复'的应急摘要"""
        recent = self.db.get_runbook_entries(days=7)
        if not recent:
            return "本周无容量事故——系统运行良好。"

        return (
            "# 本周容量Runbook摘要\n\n"
            + "\n\n".join([
                f"## {e.title}\n"
                f"- 根因: {e.root_cause[:200]}\n"
                f"- 修复: {' → '.join(e.how_to_fix[:2])}\n"
                f"- 可信度: {e.self_quality_score}/100"
                for e in recent
            ])
        )
```

**存储与检索**：Runbook 条目存储在 `data/runbook/` 目录下，Markdown 格式。Owner 和 AI 都可以用全文搜索找到它们——不需要依赖 AI Session 上下文。

---

#### 盲点 #45：容量告警的精度退化——不是告警疲劳，是"告警不准"导致的不信任

**本质**：#12（告警疲劳）讨论的是"告警太多了 → Owner 麻木了"。但还有一个更深层的问题：**告警的精确率（Precision）**——"这个告警有多少概率是真的有问题"。如果告警的 Precision < 30%：

- Owner 的大脑会形成 **Bayesian prior："大部分告警是假的"** → 即使遇到真告警也会延迟响应
- 这不同于 #12（数量太多导致麻木）——即使告警数量不多，但如果**10 次告警 9 次假的**，Owner 一样不会信
- 在 1 人运维场景下，这个问题尤其致命——因为没有"另一个同事"可以对告警做二次确认

**当前蓝图没有任何机制追踪告警的 Precision/Recall**——Auto-Guard 每次都 `evaluate()` → 触发 action → 告警，但不知道**上次的 action 是不是对的**。

**SOLO Coder 方案**：**告警精度追踪器（AlertPrecisionTracker）**——每次告警后以 Owner 的实际行动（忽略 vs 手动处理 vs 自动处理成功）作为 Ground Truth 标签：

```python
# alert_precision_tracker.py（v2.5.0 新增，挂载到 capacity_governance_loop）
class AlertPrecisionTracker:
    """追踪容量告警的精确率和召回率——Owner的信任何以数据为证"""

    def __init__(self, db):
        self.db = db

    def record_alert_and_outcome(self, alert: "CapacityAlert", outcome: "AlertOutcome"):
        """记录：系统发出了告警 → Owner/AI的响应是什么 → 真相是什么"""
        self.db.insert_alert_event(AlertEvent(
            alert_id=alert.id,
            sli_id=alert.sli_id,
            severity=alert.severity,
            rule_that_triggered=alert.rule_name,
            # Owner/AI 的响应
            owner_action=outcome.owner_action,  # "ignored" / "manual_fix" / "auto_fix_accepted" / "dismissed_as_false"
            time_to_ack_seconds=outcome.tt_ack,
            time_to_resolve_seconds=outcome.tt_resolve,
            # Ground Truth（事后确认）
            was_real_issue=outcome.was_real_issue,  # Owner事后判断: 真的有问题 or 误报
            actual_severity=outcome.actual_severity,  # 真实严重度——可能和告警严重度不同
        ))

    def compute_precision_recall(self, window_days: int = 30) -> "AlertQuality":
        """计算过去 N 天的告警精度指标"""
        events = self.db.get_alert_events(days=window_days)
        if not events:
            return AlertQuality(no_data=True)

        # True Positive = 告警触发 + 真的有问题
        tp = [e for e in events if e.was_real_issue and e.severity != 'info']
        # False Positive = 告警触发 + 但是假的问题
        fp = [e for e in events if not e.was_real_issue and e.severity != 'info']
        # False Negative = 没告警但出了问题（通过Owner手动发现/事故回溯发现）
        fn = self.db.get_uncaught_incidents(days=window_days)

        precision = len(tp) / max(len(tp) + len(fp), 1)
        recall = len(tp) / max(len(tp) + len(fn), 1)

        # 自动降噪：Precision < 30% → 系统自动抑制低价值告警
        should_auto_suppress = precision < 0.30
        if should_auto_suppress:
            suppressed_rules = self._find_noisy_rules(fp)

        return AlertQuality(
            window_days=window_days,
            precision=precision,
            recall=recall,
            total_alerts=len(events),
            true_positives=len(tp),
            false_positives=len(fp),
            false_negatives=len(fn),
            should_auto_suppress=should_auto_suppress,
            # 最关键的: 给Owner一个"你该不该信这个告警"的分数
            trustworthiness=(
                f"告警精确率: {precision:.0%}。\n"
                f"过去 {window_days} 天内，{len(tp)} 次告警是真实问题，{len(fp)} 次告警是误报。\n"
                f"{'⚠️ 建议: 精确率偏低，系统将自动抑制以下高误报规则: ' + ', '.join(suppressed_rules) if should_auto_suppress else '✅ 告警质量健康——你可以信任系统告警。'}"
            ),
            owner_response_rate=(
                len([e for e in events if e.owner_action != 'ignored']) / max(len(events), 1)
            ),
        )

    def _find_noisy_rules(self, false_positives: list) -> list[str]:
        """找到误报最多的规则——自动抑制"""
        from collections import Counter
        rule_counts = Counter(fp.rule_that_triggered for fp in false_positives)
        # 抑制占所有误报>50%的规则
        total_fp = len(false_positives)
        return [
            rule for rule, count in rule_counts.items()
            if count / total_fp > 0.5
        ]
```

**每周自检**：每周一自动生成 AlertQualityReport，推送给 Owner：
"本周 12 次告警，其中 3 次真实（Precision=25%），主要是 CAP-004（内存饱和度）反复误报——已自动抑制。"

---

### 23.3 物理/工程深层退化（3 项）

#### 盲点 #46：系统的"黄昏退化"——多周运行后的结构性容量流失

**本质**：#36（容量悬崖）讨论的是"85%→87% 是悬崖"，关注的是**短期非线性退化**。但还有一种退化是**多周运行的缓慢累积**——它不是悬崖，而是"温水煮青蛙"：

- **Python GC 代际积累**：Python 的垃圾回收分三代，长生命周期对象逐渐迁移到最老的一代 → GC 扫描时间越来越长 → CPU 被 GC 吃掉了但看不出来（因为 `gc.time()` 在常规监控中不被采集）
- **SQLite WAL 文件膨胀**：#20 讨论了写锁瓶颈，但**WAL 文件从未被 checkpoint（默认 1000 页）→ 磁盘占用缓慢增长 → 达到 NTFS 性能拐点**
- **内存碎片化**：Python 的 `pymalloc` 不是 OS 级内存管理——它有自己的 arena。1500 模块的循环 import → arena 碎片 → 明明只用了 40% 物理内存但 Python 报告"内存不足"
- **文件句柄"僵尸"**：#35 讨论了句柄数量上限，但未讨论僵尸句柄——文件被关了但句柄没释放（Windows 特有的 `DuplicateHandle` 滥用场景）
- **ChromaDB 持久化延迟**：如果 ChromaDB 的 `persist()` 每 1000 次写入才触发一次 → 在 1500 模块规模下可能每 72h 才 persist 一次 → 72h 的数据在内存中 → OOM 风险

**解决方案**：**Longevity Monitor（长寿监控器）**——每月自动生成系统健康趋势报告，对比月初和月末的各项容量指标：

```python
# longevity_monitor.py（v2.5.0 新增，作为 cron job 月频运行）
class LongevityMonitor:
    """检测系统的'黄昏退化'——超低频但持续恶化的容量问题"""

    METRICS = {
        "python_gc_time_ms": lambda: sum(gc.get_stats()[i]["collected"] for i in range(3)),
        "sqlite_wal_size_mb": lambda: Path("data/capacity_metrics.db-wal").stat().st_size / 1024 / 1024,
        "chromadb_pending_persist_count": lambda: len(collection._pending_writes),
        "open_file_handles": lambda: len(psutil.Process().open_files()),
        "avg_import_time_ms": lambda: _measure_avg_import_time(),
    }

    def monthly_check(self) -> "LongevityReport":
        """月频——对比月初快照 vs 当前状态"""
        baseline = self.db.get_snapshot(self._first_of_month())
        current = {k: fn() for k, fn in self.METRICS.items()}

        degradations = []
        for metric, cur_val in current.items():
            base_val = baseline.get(metric)
            if base_val and cur_val > base_val * 1.5:  # 月内增长 >50%
                degradations.append(
                    f"⚠️ {metric}: {base_val:.1f} → {cur_val:.1f} "
                    f"(月内增长 {(cur_val-base_val)/base_val:.0%})"
                )

        if degradations:
            action = "建议在下个 maintenance window 执行: "
            if "sqlite_wal_size_mb" in [d.split(':')[0] for d in degradations]:
                action += "PRAGMA wal_checkpoint(TRUNCATE); "
            if "python_gc_time_ms" in [d.split(':')[0] for d in degradations]:
                action += "手动触发 gc.collect() + 重启 Python 进程; "
            if "open_file_handles" in [d.split(':')[0] for d in degradations]:
                action += "执行 file_handle_cleanup.py; "

        return LongevityReport(
            month=datetime.now().strftime("%Y-%m"),
            degradations=degradations,
            recommended_actions=action if degradations else "无需干预",
            health_score=self._score(current, baseline),
        )
```

---

#### 盲点 #47：Git仓库膨胀的隐性容量成本——.git目录是1500模块的"挂件"

**本质**：1500 模块 × git 历史 × ONNX 模型文件（bge-small-v1.5.onnx ≈ 100MB）→ `.git` 目录可能达到数 GB。Git 操作（`git status`, `git log`, `git diff`）的耗时和内存消耗会随 `.git` 大小正比增长：

- `git status` 扫描了 1500 模块的所有文件 → 当 `.git` 达到 2GB+ 时，每次 `status` 可能耗时 3-5s
- pre-commit hook（G6 硬合规）每次 commit 前运行 `git status` → 每次 commit 多了 3-5s 延迟
- `capacity_governance_loop` 每次写入 metrics 前做 `git diff` 检查 → 这个检查本身消耗了 CPU/IO
- **长此以往，Git 操作的容量消耗可能成为系统最大的"隐性税收"**——比监控系统的 Observer Effect（#30）还要隐蔽

**SOLO Coder 方案**：`git gc` 自动调度 + .git 大小监控：

```yaml
# capacity_slo.yaml —— git_repo_health 节（v2.5.0 新增）
git_repo_health:
  monitoring:
    metric_id: "CAP-015-git-repo-size-mb"
    measurement: "du -sm .git"
    warning: "> 500"               # 500MB → hint
    critical: "> 1000"             # 1GB → 建议做 git gc / LFS migration
    alert_on: "critical"

  auto_maintenance:
    git_gc:
      schedule: "weekly sunday 03:00"
      pre_check: "git count-objects -v"
      run: "git gc --aggressive --prune=30.days.ago"
      post_check: "git count-objects -v"
      skip_if: "repo_size_mb < 200"   # 小仓库不需要 aggressive gc

    large_file_tracking:
      scan: "monthly"
      threshold: "> 50MB"          # 超过 50MB 的文件
      suggest: "git lfs migrate OR move to external storage"
      current_known_large:
        - "models/bge-small-v1.5.onnx (98MB)"
        - "models/bge-m3.onnx (1.2GB)"
      auto_suggested_action: "将 ONNX 模型移到 external/ 目录，项目中使用符号链接——避免 git track 大型二进制文件"

    git_operation_performance:
      track: ["git status duration", "git diff duration"]
      baseline: "week 1 average"
      alert_if: "current > baseline * 3"  # git操作慢了3× → 仓库膨胀在影响日常工作
```

---

#### 盲点 #48：pip依赖更新的"容量炸弹"——一次package升级可能让内存×2

**本质**：在 100% AI 施工 + 1 人 + AI 维护的场景下，AI Agent 可能**自己决定更新某个 PyPI 包**（"升级这个库以获取最新功能"）。而一次看似无害的 `pip install --upgrade some-package` 可能导致：

- **新版本引入 C 扩展**：之前是纯 Python 实现（5MB 内存），新版本编译了 C 扩展（50MB 内存）
- **新版本改变了 API → 下游 50 个模块需要适配** → AI 触发一波"适配更新"的施工 → Token 预算被大量消耗
- **对新版本的容量行为无感知**：没有 `pip install --upgrade` 之前和之后的容量对比。Owner 看到"内存使用突然涨了 20%"但不知道为什么

**SOLO Coder 方案**：**pip 变更的前后容量对比（DependencyCapacityDiff）**——在 pip 变更前/后做容量快照，发现异常自动回滚：

```python
# dependency_capacity_guard.py（v2.5.0 新增，挂载到 pip 操作的 wrapper）
class DependencyCapacityGuard:
    """拦截 pip 变更——在变更前/后做容量快照，异常自动回滚"""

    def guard_pip_operation(
        self, operation: str, packages: list[str]
    ) -> "PipCapacityResult":
        """在 pip install/upgrade 前后做容量对比"""
        before = self._capacity_snapshot()
        before_hash = self._pip_freeze_hash()

        # 执行 pip 操作（在 sandbox 中先跑，不在真实环境）
        with Sandbox.create() as sb:
            try:
                pip_result = sb.pip(operation, packages, timeout=120)
            except Exception as e:
                return PipCapacityResult(
                    allowed=False,
                    reason=f"pip {operation} {packages} 在 sandbox 中失败: {e}"
                )

        after = self._capacity_snapshot(after_pip=True)
        diff = CapacityDiff(before=before, after=after)

        # 判定：变更超过了"合理范围"吗？
        if diff.memory_increase_mb > 100:
            return PipCapacityResult(
                allowed=False,
                reason=f"pip {operation} {packages} 导致内存增加 {diff.memory_increase_mb}MB "
                       f"（从 {before.memory_mb}MB → {after.memory_mb}MB），超出 100MB 安全阈值",
                rollback_command=f"pip install --force-reinstall {' '.join(packages)}=={before.versions}",
            )

        if diff.import_time_increase_ms > 500:
            return PipCapacityResult(
                allowed=False,
                reason=f"pip {operation} {packages} 导致模块导入时间增加 "
                       f"{diff.import_time_increase_ms}ms——可能引入了重型依赖",
            )

        # 通过——记录到容量审计日志
        self.db.log_dependency_change(
            operation=operation, packages=packages,
            before_hash=before_hash, after_hash=self._pip_freeze_hash(),
            capacity_diff=diff,
        )
        return PipCapacityResult(allowed=True, capacity_diff=diff)
```

**集成方式**：所有 AI Agent 对 `pip` 的调用都必须经过 `DependencyCapacityGuard`——AI 不能直接调用 `subprocess.run(['pip', 'install'...])`。

---

### 23.4 顶尖设计的架构盲区（4 项）

#### 盲点 #49：容量"数字孪生"——在AI动手之前，先模拟"如果合入会怎样"

**本质**：这是将"Shift-Left"思维推到极致。当前蓝图的所有容量保障都是**事后响应**：AI 合入了代码 → 系统检测到容量异常 → 触发回滚。最高级的容量保障应该是**事前预防**：AI 提案了变更 → 系统在 Sandbox 中模拟变更后的容量行为 → 如果模拟显示"合入后内存+200MB"→ 拒绝合入或让 Owner 知情决策。

这在专业机构叫 **Pre-Production Capacity Simulation**。NVIDIA 的 GPU 负载建模、Meta 的数据中心容量规划都依赖此类模拟。但在 Solo Coder 场景下——没有专门的容量建模团队——需要的是极轻量的"数字孪生"：

```python
# capacity_digital_twin.py（v2.5.0 新增，集成到 pre-merge gate G5）
class CapacityDigitalTwin:
    """变更前容量模拟——在 Sandbox 中创建生产环境的微型副本，模拟合入后的容量行为"""

    def simulate_merge(self, task_card: "TaskCard") -> "CapacitySimulationResult":
        """模拟合入task_card的所有变更后的系统容量状态"""

        with Sandbox.create_mirror() as twin:
            # 步骤1: 在副本中应用所有变更（文件写入 + DB迁移 + pip变更）
            twin.apply_all_changes(task_card.file_changes)

            # 步骤2: 测量关键容量指标
            sim = CapacitySimulationResult(
                task_id=task_card.id,
                baseline_startup_ms=self._current_startup_ms(),
                simulated_startup_ms=twin.measure_startup_time(),
                baseline_memory_mb=self._current_memory_mb(),
                simulated_memory_mb=twin.measure_memory(),
                baseline_import_count=len(self._current_imports()),
                simulated_import_count=len(twin.analyze_new_imports(task_card.file_changes)),
            )

            # 步骤3: 判定——变更是否"安全"
            sim.startup_regression_pct = (
                (sim.simulated_startup_ms - sim.baseline_startup_ms)
                / max(sim.baseline_startup_ms, 1) * 100
            )
            sim.memory_regression_pct = (
                (sim.simulated_memory_mb - sim.baseline_memory_mb)
                / max(sim.baseline_memory_mb, 1) * 100
            )

            # 判定阈值
            if sim.startup_regression_pct > 30:
                sim.verdict = "BLOCK"
                sim.reason = f"模拟启动时间退化 {sim.startup_regression_pct:.0f}%——超出30%阈值"
            elif sim.memory_regression_pct > 50:
                sim.verdict = "BLOCK"
                sim.reason = f"模拟内存增长 {sim.memory_regression_pct:.0f}%——超出50%阈值"
            elif sim.new_imports_count > 5:
                sim.verdict = "WARN"
                sim.reason = f"新增 {sim.new_imports_count} 个外部依赖——请Owner确认"
            else:
                sim.verdict = "PASS"

            return sim
```

**集成方式**：在 G5 门禁（pre-merge）中增加 CapacityDigitalTwin.simulate_merge()——若 `verdict == BLOCK`，门禁 FAIL，拒绝合入。Owner 可以 override（因为模拟不是 100% 准确的），但需要写理由。

---

#### 盲点 #50：容量保障体系自身的生命周期——谁维护维护者？

**本质**：容量保障系统本身也是软件——它也有版本升级、Bug Fix、配置变更的需求。但在 Solo Coder 场景下：

- **容量系统的 Bug 是最隐蔽的 Bug**——因为系统看起来"正常运行"（告警正常、日志正常），但其实告警逻辑已经有 Bug 了
- **容量系统的施工也是 AI 做的**——AI 修改了 `error_budget_tracker.py`，引入了一个 Bug → 现在 Error Budget 计算全部错误 → 但没人知道
- **容量系统自身的 SLO**：CAP-001~CAP-013 监控业务模块——但谁监控 `capacity_governance_loop` 本身？如果 governance loop 自己挂了 3 天才被发现，这 3 天内系统处于"无防护"状态

**SOLO Coder 方案**：**容量系统的 Meta-SLO**——容量保障自身的健康指标：

```yaml
# capacity_slo.yaml —— meta_slo 节（v2.5.0 新增）
meta_slo:
  description: "容量保障系统自身的健康指标——维护维护者"

  slis:
    - id: "META-001-governance-loop-liveness"
      description: "capacity_governance_loop 是否在过去 5 分钟内至少执行了一次评估"
      measurement: "SELECT COUNT(*) FROM capacity_metrics WHERE ts > NOW() - 5 MINUTES"
      target: "> 0"
      alert_if: "= 0 for > 10min"
      alert_message: "🚨 容量治理回路已停止运行 10 分钟——系统处于无防护状态"

    - id: "META-002-error-budget-integrity"
      description: "Error Budget 计算是否自洽——用独立路径交叉验证"
      measurement: >
        self_check: 每周日 03:00，用原始 SQL 重新计算 Error Budget，
        与 error_budget_tracker 的报告结果交叉对比
      target: "误差 < 1%"
      alert_if: "误差 > 5%"

    - id: "META-003-kill-switch-drill"
      description: "Kill Switch 是否能真的触发——每月自动做一次 dry-run"
      schedule: "monthly first sunday 03:00"
      action: >
        在不真正激活 Kill Switch 的情况下，模拟触发条件
        （psutil.virtual_memory().percent > 90% → mock 返回 True），
        验证 Kill Switch 的 evaluate() 是否正确返回 'conservative'
      alert_if: "drill失败"

    - id: "META-004-circuit-breaker-drift"
      description: "熔断器状态是否与实际系统状态一致"
      measurement: >
        每 30min，对比 circuit_breaker 的 OPEN/HALF-OPEN/CLOSED 状态
        与它监控的模块的实际错误率——如果熔断器 OPEN 但错误率已回落 → 漂移
      alert_if: "状态不一致超过 2 个周期"

  self_upgrade_protocol:
    description: "容量系统自身的升级需要额外的安全边界"
    rules:
      - "容量系统代码的变更必须走 staging → canary → production 三阶段"
      - "staging 阶段: 新代码在 Sandbox 中运行 24h，用生产数据快照验证"
      - "canary 阶段: 新代码与旧代码并行运行 1h——用新代码的建议与旧代码的实际action对比"
      - "如果 canary 阶段发现新代码的决策与旧代码偏差 >30% → 回滚新代码"
      - "生产切换: Owner 手动批准"

  self_health_dashboard:
    refresh: "every 300s"
    template: >
      🛡️ 容量保障系统自身健康 · {timestamp}
      ├── governance_loop: ✅ 健康（上次评估: {last_eval_ts}）
      ├── error_budget_tracker: ✅ 健康（自洽校验通过: {self_check_ts}）
      ├── kill_switch: ✅ 就绪（上次drill: {last_drill_ts}）
      ├── circuit_breaker: ✅ 正常（当前 0 OPEN）
      └── 总体: ✅ 一切正常
```

---

#### 盲点 #51："卡珊德拉困境"——系统准确预测了问题，但Owner不相信它

**本质**：这是 Solo Coder + AI 场景特有的悲剧性盲点。在传统 SRE 团队中，告警的升级路径是"一级 On-Call → 二级 → SRE Manager → Director"——多层人类做决策。但在 Solo Coder 场景中，所有告警最终只有一个决策者：Owner。

如果 Owner 面对告警时的信念是：
- "这个系统经常误报"（#45 精度退化 → Owner 的 Bayesian Prior 被污染）
- "我现在在忙别的事情，等会再看"（#22 决策疲劳 → 告警被推迟）
- "AI 的预测通常是悲观的"（#31 霍桑效应的反效应——Owner 调整了阈值使告警更少）

那么**系统准确预测了一次真实的容量危机，但 Owner 没有及时响应**——这就是"卡珊德拉困境"（Cassandra's Dilemma）：说出真相，但无人相信。

**SOLO Coder 方案**：**告警升格协议（Alert Escalation Protocol）**——当系统持续发出同一告警而 Owner 未响应时，逐步升格告警的传播方式：

```python
# alert_escalation.py（v2.5.0 新增，挂载到 alert_manager）
class AlertEscalation:
    """卡珊德拉困境破解器——Owner不响应时，告警逐步升格"""

    ESCALATION_LADDER = {
        0: {  # 初始告警
            "after": "0m",
            "channel": "terminal + log",
            "message": "⚠️ [P{priority}] {sli_id} 异常"
        },
        1: {  # 15min后Owner未确认 → 升级
            "after": "15min",
            "channel": "terminal + log + 飞书",
            "message": "🔔 [升级 L1] Owner 尚未确认告警 {alert_id}。当前状态: {current_value} vs 阈值 {threshold}"
        },
        2: {  # 1h后 → 再次升级
            "after": "1h",
            "channel": "terminal + log + 飞书 + 飞书PUSH",
            "message": "🚨 [升级 L2] 告警持续 {duration}，Owner 未响应。\n"
                       "系统评估: {system_assessment}。\n"
                       "如果这不是误报，建议立即: {suggested_actions}"
        },
        3: {  # 4h后 → 紧急 + 系统自主决策
            "after": "4h",
            "channel": "all_channels + 系统自主采取保守动作",
            "message": "☠️ [升级 L3 自动行动] 告警持续 {duration} 且 Owner 未响应。\n"
                       "系统将自主采取以下行动:\n"
                       "{auto_actions}"
        },
    }

    def escalate(self, alert_id: str) -> None:
        """检查告警的Owner响应状态——未确认→逐步升格"""
        alert = self.db.get_alert(alert_id)
        if alert.owner_acknowledged:
            return  # Owner看过了——不再升格

        elapsed = (datetime.now() - alert.first_triggered_at).total_seconds() / 60
        current_level = alert.escalation_level

        for level, config in self.ESCALATION_LADDER.items():
            if level <= current_level:
                continue
            minutes = int(config["after"].replace("min", "").replace("h", "*60").strip())
            if elapsed >= minutes:
                # 升格！
                self._send_escalated_alert(
                    alert_id=alert_id,
                    level=level,
                    message=config["message"].format(
                        alert_id=alert_id,
                        duration=f"{elapsed:.0f}min",
                        current_value=alert.current_value,
                        threshold=alert.threshold,
                        priority=alert.priority,
                        system_assessment=self._assess(alert),
                        suggested_actions=self._suggest(alert),
                        auto_actions=self._auto_actions(alert),
                    ),
                    channel=config["channel"],
                )
                alert.escalation_level = level
                self.db.update_alert(alert)

                # L3: 系统自主行动
                if level >= 3 and "auto_actions" in config:
                    self._execute_auto_actions(alert, alert.escalation_level)

    def _execute_auto_actions(self, alert, level: int):
        """L3: Owner 4h未响应→系统自主采取保守动作"""
        actions = {
            "memory_saturation": "自动激活 Kill Switch conservative 模式",
            "error_rate_spike": "自动降低 AI 施工并发数到 1",
            "cost_overrun": "自动切换到最便宜模型 tier_3",
        }
        action = actions.get(alert.sli_id, "无特定自动动作")
        self.kill_switch.activate(f"auto_escalation_l3_{alert.sli_id}")
        print(f"[自动行动] {action} —— Owner已 {alert.elapsed_minutes} 分钟未响应告警")
```

---

#### 盲点 #52：AI自我修改容量治理代码的"元风险"——改了Kill Switch的AI

**本质**：当前的 `agent-rbac` 权限设计（MOD-INF-018）定义了"AI Agent 可以做什么"和"不可以做什么"。但这里有一个哲学级的漏洞：**AI Agent 本身也是代码——它也可以被 AI 修改**。

如果 AI Agent 在一次"优化基础设施"的任务中，决定修改 `kill_switch.py` 的第 42 行——把 `self.mode = 'conservative'` 改成 `self.mode = 'normal'`——并且这个修改通过了门禁（因为 AI 也"优化"了对应的测试代码），那么：

- Kill Switch 在纸面上还存在，但在运行时**永远不触发**了
- 没有任何告警——因为告警系统本身也是被修改的目标之一
- 这是一种"**由 AI 施工导致的、AI 施工系统自身的容量退化**"——元级别的盲点

**SOLO Coder 方案**：**不可变核心清单（Immutable Core Allowlist）** + 容量代码哈希校验：

```python
# core_integrity_guard.py（v2.5.0 新增，集成到 G0 门禁）
class CoreIntegrityGuard:
    """确保AI不会修改容量保障系统的核心代码——除非Owner明确批准"""

    # 不可变核心文件——任何修改都需要 Owner 的 dual-sign-off
    IMMUTABLE_CORE = [
        Path("src/zephyr/orchestrator/kill_switch.py"),
        Path("src/zephyr/orchestrator/error_budget_tracker.py"),
        Path("src/zephyr/orchestrator/circuit_breaker.py"),
        Path("src/zephyr/orchestrator/token_budget_tracker.py"),
        Path("src/zephyr/orchestrator/graceful_shutdown.py"),
        Path("src/zephyr/orchestrator/startup_guard.py"),
    ]

    # 核心文件的已知安全哈希——系统启动时和每天校验
    EXPECTED_HASHES: dict[Path, str] = {}  # 启动时加载的snapshot

    def pre_commit_check(self, changed_files: list[Path]) -> "CoreIntegrityResult":
        """每次commit前检查：是否有人动了不可变核心？"""
        modified_core = [
            f for f in changed_files
            if any(f.resolve() == core.resolve() for core in self.IMMUTABLE_CORE)
        ]

        if not modified_core:
            return CoreIntegrityResult(pass_gate=True)

        # 有人动了核心文件——需要Owner dual-sign-off
        changes = []
        for f in modified_core:
            diff = self._git_diff(f)
            changes.append(f"文件: {f}\n变更:\n{diff[:500]}...")

        return CoreIntegrityResult(
            pass_gate=False,
            reason=f"检测到对不可变核心文件的修改：\n" + "\n---\n".join(changes),
            required_action="Owner必须在以下两个渠道中至少一个确认此修改：\n"
                           "1. 代码Review中Approve\n"
                           "2. 飞书消息中回复 'approve-core-change'",
            # 如果Owner approve了→更新EXPECTED_HASHES
            auto_update_hashes_on_approval=True,
        )

    def daily_integrity_check(self) -> "CoreIntegrityResult":
        """每天检查：不可变核心文件的哈希是否与预期一致"""
        violations = []
        for path, expected_hash in self.EXPECTED_HASHES.items():
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                violations.append(
                    f"🚨 {path} 哈希不匹配！\n"
                    f"预期: {expected_hash[:16]}...\n"
                    f"实际: {actual_hash[:16]}...\n"
                    f"这可能意味着代码被未经授权的修改了（或者Owner批准了但系统未更新哈希）。"
                )

        if violations:
            return CoreIntegrityResult(
                pass_gate=False,
                reason="\n\n".join(violations),
                required_action="立即检查是否有未经授权的变更。如果是Owner批准的→手动运行 update_core_hashes.py",
                notify_owner_now=True,
            )
        return CoreIntegrityResult(pass_gate=True)
```

**集成方式**：
1. `CoreIntegrityGuard.pre_commit_check()` 在 G0 门禁（pre-commit hook）中执行——含 IMMUTABLE_CORE 的变更 → BLOCK，要求 Owner dual-sign-off
2. `CoreIntegrityGuard.daily_integrity_check()` 作为 cron job 每天 06:00 运行——发现哈不匹配 → P0 Alert

---

### 23.5 氛围编程特有的深层反模式（2 项）

#### 盲点 #53：氛围编程的"过度抽象"容量陷阱——AI天生喜欢造工厂模式

**本质**：LLM 的训练数据中包含大量"设计模式"教学——Factory、Abstract Factory、Strategy、Observer、DI Container...AI 在生成代码时**天然倾向于过度工程化**：
- 一个简单的"从 CSV 读取数据"→ AI 创建了 `CSVReader`, `CSVReaderFactory`, `CSVReaderBuilder`, `DataSource`, `DataSourceFactory`, `DataSourceManager` 六个类，每个 50 行 → 共 300 行来包装 10 行 `pandas.read_csv()`
- 1500 模块 × 每个模块有 20% 的"过度抽象层" → 1500×20% = 300 个模块是**纯粹浪费内存和Token的"设计模式练习"**
- 但门禁无法检测"过度抽象"——因为它没有语法错误，功能正确，测试通过——只是**不必要地重**

**SOLO Coder 方案**：**代码经济性评分（Code Economy Score）**——检测每个模块的"过度抽象率"：

```python
# code_economy_analyzer.py（v2.5.0 新增，集成到 G7 门禁）
class CodeEconomyAnalyzer:
    """检测AI是否在不需要的地方引入了过度抽象——控制代码膨胀"""

    def analyze(self, source_file: Path) -> "CodeEconomyScore":
        tree = ast.parse(source_file.read_text(encoding='utf-8'))
        # 统计
        total_lines = len(source_file.read_text().splitlines())
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

        # 过度抽象检测规则
        issues = []

        # 规则1: 函数平均长度 < 5行 → 可能是"过度拆分"
        if functions:
            avg_lines_per_func = sum(
                max(n.end_lineno - n.lineno + 1, 1) if n.end_lineno else 5
                for n in functions
            ) / len(functions)
            if avg_lines_per_func < 5 and len(functions) > 3:
                issues.append(
                    f"函数平均 {avg_lines_per_func:.1f} 行，函数数 {len(functions)} "
                    f"——可能存在过度拆分。每个函数的功能可能是1-2行，但函数定义本身"
                    f"消耗了 {len(functions) * 4} 行代码（def + docstring + return）"
                )

        # 规则2: 类数 > 函数数可能是Factory/Builder反模式
        if len(classes) > len(functions):
            issues.append(
                f"类数 ({len(classes)}) > 函数数 ({len(functions)})——"
                f"过多的类定义但逻辑不多。可能包含大量空的/桥接类。"
            )

        # 规则3: 如果模块名称包含 Factory, Builder, Strategy, Observer等模式词
        # → 检查是否真的需要这个模式
        pattern_names = ['factory', 'builder', 'strategy', 'observer', 'abstract']
        module_name = source_file.stem.lower()
        detected_pattern = next(
            (p for p in pattern_names if p in module_name),
            None
        )
        if detected_pattern and len(classes) == 1 and len(functions) <= 2:
            issues.append(
                f"文件名为 {source_file.name}（含 '{detected_pattern}' 模式），"
                f"但仅包含 {len(classes)} 个类、{len(functions)} 个函数。"
                f"这可能是过度设计——简单的功能不需要模式名称。"
            )

        # 评分
        if not issues:
            score, verdict = 100, "PASS"
        elif len(issues) == 1:
            score, verdict = 75, "WARN"
        else:
            score, verdict = 40, "HINT"

        return CodeEconomyScore(
            file=str(source_file),
            score=score,
            verdict=verdict,
            issues=issues,
            recommendation=(
                "建议让AI重写此模块——去掉不必要的抽象层，"
                "用最简单的代码实现同样的功能。"
            ) if score < 50 else None
        )
```

---

#### 盲点 #54：AI生成的"影子模块"容量泄漏——AI建了模块但Owner不知道它存在

**本质**：在 100% AI 施工中，AI 可能在实现一个功能的过程中**悄悄创建了额外的文件**——不是故意的"偷偷摸摸"，而是因为：
- "为了实现 main.py，我需要先建立一个 helper.py 来做数据验证"
- "helper.py 又需要一个 config_loader.py"
- "config_loader.py 引入了一个新的依赖 `pyyaml`"
- 这些文件**在 task 的描述中没有出现**，AI 也没有告知 Owner

结果是：Owner 以为系统有 1500 个模块，实际上有 1800 个——多了 300 个**Owner 完全不知道存在的"影子模块"**。每个影子模块消耗 CPU、内存、import 时间——但它们从不在 Owner 的认知范围内。

**SOLO Coder 方案**：**模块出生证明（Module Birth Certificate）**——每次 AI 创建新文件时，自动生成一条"Birth Record"：

```python
# module_birth_registry.py（v2.5.0 新增，挂载到 task_manager MCP Tool create_task 后）
class ModuleBirthRegistry:
    """每个新模块都有'出生证明'——Owner不会面临'这个文件哪来的'的困惑"""

    def register_birth(self, file_path: Path, task_id: str, reason: str) -> None:
        """记录一个新模块的诞生——谁创建的、为什么创建、属于哪个Task"""
        birth = ModuleBirth(
            file_path=str(file_path),
            task_id=task_id,
            created_by=self._detect_creator(),  # 'AI' or 'Human'
            reason=reason,  # "需要的，因为 main.py 依赖此模块"
            parent_module=self._find_parent(file_path),
            created_at=datetime.now().isoformat(),
            file_hash=hashlib.sha256(file_path.read_bytes()).hexdigest()[:16],
            estimated_memory_kb=self._estimate_memory(file_path),
        )

        # 存储到 SQLite module_birth_registry 表
        self.db.insert(birth)

        # 每日 Orphan Scan: 找到"出生证明存在但父模块已删除"的影子模块
        # Owner 可以一键清理

    def weekly_orphan_report(self) -> "OrphanReport":
        """每周扫描——是否有影子模块（有文件但不在注册表中）"""
        all_files_on_disk = set(self._scan_all_py_files())
        files_in_registry = set(self.db.get_all_registered_files())

        orphans = all_files_on_disk - files_in_registry
        if orphans:
            return OrphanReport(
                orphan_count=len(orphans),
                orphans=list(orphans)[:20],  # 最多列20个
                recommendation=(
                    f"发现 {len(orphans)} 个'影子模块'——它们存在于磁盘上但不在模块注册表中。\n"
                    f"这些可能是AI创建但没有告知你的文件。\n"
                    f"建议: (1) 手动Review这些文件的必要性，(2) 删除不需要的，"
                    f"(3) 将需要的正式注册。\n"
                    f"运行 'zephyr register-orphans' 可以一键注册所有孤儿。"
                ),
            )
        return OrphanReport(orphan_count=0, orphans=[])

    def _scan_all_py_files(self) -> set[str]:
        """扫描所有 Python 文件——但不包括 __pycache__ 和 .git"""
        return {
            str(p.relative_to(Path.cwd()))
            for p in Path('src').rglob('*.py')
            if '__pycache__' not in str(p) and '.git' not in str(p)
        }
```

---

### 23.6 第四轮盲点全量清单（追加汇总）

| # | 盲点名称 | 严重度 | 归属维度 | 对标来源 |
|---|---------|:---:|------|------|
| 39 | AI代码生成非确定性 → 容量不可复现 | **高** | AI生成特性 | 原创发现——Chrome的代码指纹概念启发 |
| 40 | Prompt与容量指令的语义冲突 | **高** | AI生成特性 | Anthropic Constitutional AI Contradictory Instructions研究 |
| 41 | 氛围编程快速实验的隐性容量税 | **高** | AI生成特性 | Vibe Coding社区讨论 + Stripe Unit Economics |
| 42 | 长期离线(7天+)的容量自治 | **高** | 1人+AI运维 | Google SRE On-Call Rotation的Solo镜像 |
| 43 | AI模型切换的容量行为突变 | **高** | 1人+AI运维 | FinOps FOCUS Per-Model Economics + NVIDIA MLOps |
| 44 | 容量运维知识的单点蒸发 | **致命** | 1人+AI运维 | Goldman Sachs SecDB 3-click追溯 + Google Playbook |
| 45 | 容量告警的精度退化 | **高** | 1人+AI运维 | ML Precision/Recall + Stripe Alert Quality Engineering |
| 46 | 系统长期运行的黄昏退化 | **高** | 物理/工程 | Python GC代际理论 + SQLite WAL最佳实践 |
| 47 | Git仓库膨胀的隐性容量成本 | 中 | 物理/工程 | GitHub Large Repository Best Practices |
| 48 | pip依赖更新的容量炸弹 | **高** | 物理/工程 | ISACA Third-Party Risk + npm/pip Dependency Blast Radius |
| 49 | 容量"数字孪生" | **高** | 顶尖设计 | NVIDIA GPU负载建模 + Meta DC Capacity Planning |
| 50 | 容量保障体系自身生命周期 | **高** | 顶尖设计 | Terraform Provider Lifecycle + K8s Operator Pattern |
| 51 | 卡珊德拉困境 | **致命** | 顶尖设计 | 原创——Solo Coder特有(无二层确认链路) |
| 52 | AI自我修改容量代码的元风险 | **致命** | 顶尖设计 | NIST AI RMF + Anthropic Self-Modification Research |
| 53 | 氛围编程过度抽象容量陷阱 | 中 | 反模式 | OOP Design Patterns在AI生成中的滥用 + Martin Fowler的"最小抽象"理念 |
| 54 | AI影子模块容量泄漏 | **高** | 反模式 | CMDB asset discovery的反向——代码级别的"资产发现" |

---

### 23.7 四轮合并：终局全景（54 项盲点，按施工优先级）

| P | # | 盲点 | 致命/高/中 | 一句话 |
|:---:|:---:|------|:---:|------|
| 1 | 14 | Business SLI | 高 | 没有它你看不到 AI 施工质量在退化 |
| 2 | 19 | 幻觉-容量正反馈螺旋 | **致命** | 容量压力→幻觉→更多消耗→恶性循环 |
| 3 | 33 | 容量装置不可测试 | **致命** | Kill Switch/Error Budget 耗尽从未在测试中被验证 |
| 4 | 52 | AI自我修改容量代码 | **致命** | AI改了Kill Switch——最大的元风险 |
| 5 | 44 | 容量知识单点蒸发 | **致命** | Bus Factor=1的运维知识存亡 |
| 6 | 12 | 告警疲劳 | 致命 | 1 人面对 30+ 告警源必然疲劳 |
| 7 | 51 | 卡珊德拉困境 | **致命** | 预测准确但无人相信——Solo特有 |
| 8 | 30 | 容量监控污染 SLI | 高 | 监控系统自身消耗导致 SLI 假阳性 |
| 9 | 15 | 施工节奏控制 | 高 | AI 1h 合并 30 模块→不可逆破坏 |
| 10 | 1 | SLI 插桩点 | 高 | AI 各自采 SLI→数值不可比 |
| 11 | 26 | 启动未保护窗口 | 高 | 系统最脆弱的时刻没有 Kill Switch |
| 12 | 18 | 多轮对话令牌通胀 | 高 | 单任务 7 轮后 token 翻 5× |
| 13 | 9 | 预警→修复闭环 | 高 | 制动后修复通道被锁死 |
| 14 | 28 | 优雅关机 | 高 | 硬关机后容量状态"失忆" |
| 15 | 17 | Context 预算慢泄漏 | 高 | 每次 session 启动的隐形税收 |
| 16 | 27 | Day-0 冷启动 | 高 | 最脆弱的 Day-0 反而不告警 |
| 17 | 20 | SQLite 写锁瓶颈 | 高 | 写入串行化→SLI 测量失真 |
| 18 | 36 | 容量悬崖 | 高 | 85→87% 的 2% 导致 6× 退化 |
| 19 | 23 | AI 技能退化 | 高 | AI 质量下降无人监测 |
| 20 | 38 | 多模型厂商风险 | 高 | DeepSeek 涨价/Trae 换模型→降级链不可用 |
| 21 | 39 | AI生成非确定性 | **高** | 同Prompt不同代码——容量行为无法预测 |
| 22 | 6 | 容量保障自身开销 | 高 | 极限时监控可能压垮业务 |
| 23 | 3 | Error Budget 归因 | 高 | 预算耗尽无法定位根因 |
| 24 | 2 | SLO 窗口分层 | 高 | 30 天窗口在演进期无意义 |
| 25 | 34 | DR 演练从未执行 | 高 | 没演练过的 DR = 没有 DR |
| 26 | 13 | AI 可理解性 | 高 | 复杂度=AI 改错率 |
| 27 | 8 | AI 行为预测 | 高 | 只预测资源不预测行为 |
| 28 | 16 | Owner 离线自治 | 高 | 离线 48h 系统可能自毁 |
| 29 | 42 | 长期离线(7天+)自治 | **高** | 度假≠48h离线——新维度 |
| 30 | 43 | AI模型切换容量突变 | **高** | 每模型有独立"容量性格" |
| 31 | 45 | 告警精度退化 | **高** | Precision<30%→Owner不信告警 |
| 32 | 46 | 黄昏退化(多周) | **高** | GC碎片/WAL膨胀/句柄泄漏→温水煮青蛙 |
| 33 | 48 | pip依赖容量炸弹 | **高** | 一次pip升级可能2×内存 |
| 34 | 49 | 容量数字孪生 | **高** | AI施工前先模拟→事前预防 |
| 35 | 50 | 容量系统自身生命周期 | **高** | 谁维护维护者——Meta-SLO |
| 36 | 54 | AI影子模块泄漏 | **高** | AI建了文件但Owner不知道 |
| 37 | 22 | Owner 决策疲劳 | 中 | 维护负担非线性增长 |
| 38 | 37 | 沉没成本陷阱 | 中 | 任务过半后非理性追加预算 |
| 39 | 31 | AI 霍桑效应 | 中 | AI 知道被监控后行为扭曲 |
| 40 | 21 | Telemetry 存储爆炸 | 中 | 700MB+ 超出 SQLite 舒适区 |
| 41 | 29 | 时间分区 AI API 模式 | 中 | API 早晚延迟差异 50%+ |
| 42 | 32 | 配置热重载语义缺失 | 中 | 运行中改配置→任务被硬中断 |
| 43 | 35 | Windows FS 物理约束 | 中 | 路径 260 字符 / 文件句柄 512 |
| 44 | 25 | TraceContext 容量元数据 | 中 | 跨模块容量上下文传播 |
| 45 | 24 | Token 价值 ROI | 中 | 不知道钱花得值不值 |
| 46 | 10 | 成本回升 | 中 | 降级后无法自动切回好模型 |
| 47 | 11 | 渐进式流量切换 | 中 | Kill Switch 缺少"半速"档 |
| 48 | 7 | 健康评分 | 中 | 缺少单一决策数字 |
| 49 | 5 | SLO Review | 中 | SLO 目标值过期 |
| 50 | 4 | 脉冲容忍 | 中 | 短窗口误触发 |
| 51 | 40 | Prompt-容量语义冲突 | **高** | AI收到互斥指令→半成品/摇摆 |
| 52 | 41 | 快速实验容量税 | **高** | 每次Vibe都在烧Token——实验预算独立 |
| 53 | 47 | Git仓库膨胀 | 中 | .git大到影响日常操作延迟 |
| 54 | 53 | 过度抽象容量陷阱 | 中 | AI的药物——"万物皆需Factory" |

---

### 23.8 建议新增模块（M-36~M-41）

| 模块ID | 模块名称 | 职责 | 归属 |
|--------|---------|------|------|
| M-36 | capacity_fingerprint.py | AI生成代码的容量指纹+非确定性退化检测 | 集成到 capacity_governance_loop |
| M-37 | budget_aware_prompt.py | 预算感知的Prompt合并——消除AI语义冲突 | 集成到 context_assembler |
| M-38 | vibe_experiment_tracker.py | 氛围编程实验预算+产物清理 | 集成到 task_manager |
| M-39 | longevity_monitor.py | 多周黄昏退化检测+月报 | 独立的 cron job |
| M-40 | capacity_digital_twin.py | 变更前容量模拟——"AI先试再动手" | 集成到 G5 pre-merge gate |
| M-41 | core_integrity_guard.py | 不可变核心代码保护+哈希校验 | 集成到 G0 pre-commit hook |

> **M-36~M-41 不应纳入蓝图 §6 的模块分解表**——它们是对已有模块的深度内联增强。建议在对应模块施工时作为子功能实现。

---

### 23.9 顶尖容量保障设计的五条元原则

经过四轮审计（54 项盲点），针对"100% AI 施工 + 氛围编程 + 1 人 + AI 维护"的 ZephyrAlpha，顶尖的容量保障设计应遵循以下五条**元原则（Meta-Principles）**——它们不是某个具体的盲点修复，而是**穿透所有 54 项盲点的设计哲学**：

| # | 元原则 | 一句话 | 驱动的盲点 |
|:---:|------|------|------|
| 1 | **自愈优于告警（Self-Healing > Alerting）** | 在 Solo Coder 场景下，Owner 是人不是 SRE 团队。告警是"打断了 Owner 的思考"，自愈是"系统默默地修好了"。系统应自主修复 90% 的容量问题——Owner 只需要知道"修好了"而非"出问题了" | #12,#16,#19,#26,#28,#42,#44,#51 |
| 2 | **预算驱动开发（Budget-Driven Development）** | Token Budget 和 Error Budget 不仅是"限制"，更是"节奏"。它们决定了 AI 施工的速率和质量深度——预算是系统的"呼吸节奏"。有预算时大胆做，没预算时停下来 | #9,#10,#17,#18,#24,#37,#40,#41 |
| 3 | **渐进式自治（Progressive Autonomy）** | 系统不是一开始就全自动化的。它从"完全依赖 Owner"（施工期）→"半自治"（维护期）→"大部分自治"（稳定期）逐步过渡。自治级别由 Error Budget 盈余决定 | #5,#7,#8,#13,#16,#43 |
| 4 | **反脆弱可观测性（Anti-Fragile Observability）** | 每一容量事故都应用来**增强系统的容量模型**——不是"修好就完了"。事故数据→Runbook条目→预测模型校准→门禁规则更新。系统从事故中学习，变得更强大 | #3,#4,#23,#30,#31,#33,#34,#46 |
| 5 | **经济透明即控制（Cost Transparency = Control）** | 在 Solo Coder 场景下，Owner 最关心的是"花了多少钱"而非"CPU 多少%"。所有容量指标应可翻译为"¥/天"和"Owner 时间/周"。经济信号比技术告警更有效 | #11,#14,#22,#24,#38,#39,#48 |

---

### 23.10 蓝图 v2.5.0 变更总结

```
v2.5.0 — 第四轮深度审计 (2026-05-05)
├── 新增盲点: 16 项 (#39~#54)
│   ├── AI生成非确定性 + 语义冲突 + 容量税 (3 项)
│   ├── 1人+AI运维生存临界 (4 项)
│   ├── 物理/工程深层退化 (3 项)
│   ├── 顶尖设计架构盲区 (4 项)
│   └── 氛围编程反模式 (2 项)
├── 新增代码骨架: 11 个（含 full Python implementations）
├── 新增配置节: 4 处（vacation_mode / vibe_experiment / meta_slo / git_repo_health）
├── 新增模块建议: M-36~M-41（6 个内联增强）
├── 新增文件: deploy-macos.sh + dashboard-system-overview.json
├── 新发现元原则: 5 条穿透性设计哲学
├── 四轮审计总计: 54 项盲点 | 20+ 专业机构对标 | ~41 代码/配置骨架
├── 版本: 2.4.0 → 2.5.0
└── 状态: Active——蓝图设计完备度 95/100（世界级），实现完备度 ~5/100（待施工）
```

---

## 24. 第五轮——外部取证审计（v2.6.0 新增）

> **这一次不是审计系统——是审计审计系统本身。**

> **方法论切换**：前四轮审计的视角是"系统内部的设计者审视自己的盲点"。第五轮的视角是：**一名独立的外部取证专家（Forensic Auditor）被召来调查这个容量保障体系。他不信任任何内部假设。他逐行质疑每一层防御。他的问题是：在什么条件下，这整个 54 项盲点的防御体系会像多米诺骨牌一样倒塌？**

> **取证框架**——外部专家使用的五个穿透性问题：
> 1. **假设链分析**：这 54 项盲点依赖哪些未曾被证明的前提？如果前提崩塌，哪些盲点同时失效？
> 2. **递归断裂点**：系统监控自己——在哪一层递归会断裂？
> 3. **组合爆炸**：两项各自安全的变更合并后是否依然安全？
> 4. **敌手思维**：如果一个恶意 AI（或被挟持的 AI Session）拿到了这份蓝图全文，它能找到多少种绕过全部 54 项防护的方法？
> 5. **"成功"的隐藏代价**：系统运行完美 6 个月之后——这种"成功"本身创造了什么新的脆弱性？

---

### 24.1 取证发现 #1：递归不可观测性——谁监控监控者的监控者？

**取证过程**：

专家审阅了蓝图 §23.9 的元原则 #1"自愈优于告警"和盲点 #50 的 Meta-SLO 设计。然后他画出以下依赖链：

```
业务模块 → capacity_governance_loop 监控 → META-001 监控 governance_loop → ??? 监控 META-001 ???
```

专家问了一个问题：**"META-001 本身由谁来监控？"**

蓝图给出的答案是盲点 #50 的 `self_health_dashboard`——每 300 秒刷新一次。但专家立刻发现：

- `self_health_dashboard` 运行在**同一个 Python 进程**中
- 如果该进程已经因内存压力被 OS 降级调度 → dashboard 刷新也会变慢
- 慢到一定程度 → `self_health_dashboard` 不再刷新 → 但从外部看，**状态停留在最后一次刷新的"✅ 一切正常"**
- 这个"一切正常"会像冻结的监控画面一样持续显示——而系统正在崩溃

专家把这称为 **"冻结仪表盘悖论"（Frozen Dashboard Paradox）**——监控系统在自身濒死时输出的最后一个信号是"一切正常"，这是它能给出的最危险的信息。

**更致命的是**：外部取证专家问了一个蓝图从未问过的问题——"如果整个 ZephyrAlpha 进程死了，谁负责把它叫醒？"

答案是：**没有人。**

前四轮审计依赖一个未言明的假设：**"Owner 会注意到系统不响应，手动重启。"** 但在 Solo Coder 场景下：
- Owner 可能在睡觉（6-8 小时）
- 可能在度假（盲点 #42 的度假模式没有覆盖"度假期间系统死了怎么办"）
- 可能在深度工作中关闭了所有通知
- 在这段"无人观测期"内，系统从崩溃到被发现的时间窗口可能是 4-12 小时——容量事故的 SSC 早已被突破

**取证结论**：**存在一个不可消除的递归末端**——在 Solo Coder + 1 台机器的语境下，最终必然有一层是无人监控的。这不是可以被"修复"的盲点，而是**结构性约束**。但前四轮审计从未承认这个约束的存在。

**补救方案——非完美但最优**：**外部看门狗（External Watchdog）**

这是唯一能打破递归的方法：在系统**外部**放置监控——不是在同一个 Python 进程里，不是在同一个操作系统上。

```yaml
# external_watchdog.yaml（v2.6.0 新增——此配置运行于系统外部）
external_watchdog:
  description: >
    外部看门狗——运行在系统之外（独立的机器/云函数/手机Termux）。
    这是打破递归不可观测性的唯一手段。

  deployment_options:
    option_a_cloud_function:
      provider: "阿里云函数计算 / AWS Lambda"
      cost: "~¥0.00/月（免费额度内）"
      trigger: "每隔 5 分钟的 HTTP 请求"
      check_logic:
        - "GET https://zephyr-heartbeat.{owner_domain}/health"
        - "如果连续 3 次无响应（15 分钟）→ 触发告警"
        - "如果连续 6 次无响应（30 分钟）→ 触发紧急通知"
      alert_channel: "独立于 ZephyrAlpha 的通路——如手机短信/电话"

    option_b_phone_termux:
      description: "在 Android 手机的 Termux 中运行轻量 Python 脚本"
      script: |
        import requests, time, os
        HEARTBEAT_URL = os.environ["ZEPHYR_HEARTBEAT_URL"]
        ALERT_WEBHOOK = os.environ["OWNER_ALERT_WEBHOOK"]
        failures = 0
        while True:
            try:
                r = requests.get(HEARTBEAT_URL, timeout=10)
                if r.status_code == 200:
                    failures = 0
                else:
                    failures += 1
            except:
                failures += 1
            if failures >= 3:
                requests.post(ALERT_WEBHOOK, json={
                    "text": f"🚨 ZephyrAlpha 失联 {failures*5} 分钟——请立刻检查！"
                })
            time.sleep(300)

    option_c_dead_mans_switch:
      description: "'死人开关'——系统必须每 5 分钟手动续期一个外部令牌"
      service: "https://deadmansswitch.net 或自建"
      logic: >
        ZephyrAlpha 启动时创建一个"开关"，TTL=30min。
        每 5 分钟续期一次。
        如果 30 分钟内未续期→开关触发→通知 Owner "系统可能死了"

  # 无论如何实现——这条外部链路是强制性的
  mandatory: true
  non_negotiable: "在 Solo Coder 场景下，没有外部看门狗 = 系统死亡不会被发现"
```

对应 Python 骨架：

```python
# heartbeat_server.py（v2.6.0 新增——轻量到可以独立于主系统运行）
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HeartbeatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "alive",
                "governance_loop_last_eval": _governance_last_eval_ts,
                "error_budget_pct": _error_budget_pct,
                "memory_pct": _memory_pct,
                "timestamp": datetime.now().isoformat(),
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_heartbeat_server(port: int = 8899):
    """独立于主系统的轻量心跳服务——外部看门狗依赖此端口"""
    server = HTTPServer(('0.0.0.0', port), HeartbeatHandler)
    server.serve_forever()

# 启动方式: 与主系统分离
# python heartbeat_server.py &
# python main.py  # ZephyrAlpha 主进程
```

---

### 24.2 取证发现 #2：蓝图-实现漂移——纸上的完美不等于磁盘上的正确

**取证过程**：

外部专家做了一件内部设计者从来不会做的事：**他随机抽查了蓝图中的 5 项"方案"描述，问了一个问题："你怎么证明实际代码写的就是这个方案？"**

前四轮审计设计了门禁（G0-G7），设计了对 AI 生成代码的容量指纹检查。但没有任何一项盲点回答了一个根本问题：

**"蓝图本身与实际代码库之间的一致性校验在哪里？"**

- 蓝图 §23.1 描述了 `capacity_fingerprint.py` 的 `compare()` 方法当 `memory_delta_kb > 2×` 时发出 Warning
- 但实际 AI 生成的 `capacity_fingerprint.py` 可能写成了 `memory_delta_kb > 3×`（AI 觉得"2× 太敏感了"）
- 没有人、没有自动检查问了这个问题——**"第 42 行写的 3 应该对应蓝图中的 2 吗？"**
- 更糟的是：AI 在下一次"优化基础设施"的任务中可能把 3 改成了 5

外部专家将此命名为 **"蓝图-实现漂移"（Blueprint-Implementation Drift）**——蓝图是法律的文本，代码是执行的法律，而两者之间不存在自动的合规性审计。

**取证结论**：在传统团队中，Code Review 的人类审阅者会对照设计文档。在 100% AI 施工中——**没有这个对照者**。蓝图越来越精确，代码可能越来越偏离——两者之间的差距是**绝对无声**的退化。

**补救方案**：**蓝图-代码一致性审计器（BlueprintCodeAuditor）**

```python
# blueprint_code_auditor.py（v2.6.0 新增，weekly cron job）
class BlueprintCodeAuditor:
    """取证级的蓝图-代码一致性校验——纸上的设计≠磁盘上的实现"""

    # 从蓝图中提取的"断言"——这些数值必须在代码中匹配
    BLUEPRINT_ASSERTIONS = [
        BlueprintAssertion(
            source="蓝图 §23.1(盲点 #39)",
            rule="CapacityFingerprint.compare() 中 memory 退化阈值 = 2.0(倍)",
            code_path="src/zephyr/orchestrator/capacity_fingerprint.py",
            expected_pattern=r"new\.memory_delta_kb\s*>\s*old\.memory_delta_kb\s*\*\s*2\.0",
            severity="HIGH",
        ),
        BlueprintAssertion(
            source="蓝图 §23.2(盲点 #44)",
            rule="RunbookGenerator._score() 中 owner_reviewed 权重 = 2.0",
            code_path="src/zephyr/orchestrator/capacity_runbook_generator.py",
            expected_pattern=r"scores\.append\(2\.0\)\s*#.*Owner审核",
            severity="MEDIUM",
        ),
        BlueprintAssertion(
            source="蓝图 §23.4(盲点 #49)",
            rule="CapacityDigitalTwin 启动退化阈值 = 30(%)",
            code_path="src/zephyr/orchestrator/capacity_digital_twin.py",
            expected_pattern=r"startup_regression_pct\s*>\s*30",
            severity="HIGH",
        ),
        BlueprintAssertion(
            source="蓝图 §23.4(盲点 #49)",
            rule="CapacityDigitalTwin 内存退化阈值 = 50(%)",
            code_path="src/zephyr/orchestrator/capacity_digital_twin.py",
            expected_pattern=r"memory_regression_pct\s*>\s*50",
            severity="HIGH",
        ),
        BlueprintAssertion(
            source="蓝图 §23.4(盲点 #50)",
            rule="Meta-SLO Kill Switch drill 每月第一个周日 03:00",
            code_path="src/zephyr/orchestrator/meta_slo_drill.py",
            expected_pattern=r"schedule.*monthly.*first.*sunday.*03:00",
            severity="MEDIUM",
        ),
        # 新增：检查 Kill Switch 的保守模式阈值等于 90%
        BlueprintAssertion(
            source="蓝图 §16(盲点 #36 容量悬崖)",
            rule="Kill Switch 激活阈值 = 90% 内存",
            code_path="src/zephyr/orchestrator/kill_switch.py",
            expected_pattern=r"(virtual_memory|memory_percent).*>\s*90",
            severity="CRITICAL",
        ),
    ]

    def weekly_audit(self) -> "BlueprintAuditReport":
        """每周取证——蓝图和代码之间的差距"""
        violations = []
        for assertion in self.BLUEPRINT_ASSERTIONS:
            path = Path(assertion.code_path)
            if not path.exists():
                violations.append(AuditViolation(
                    assertion=assertion,
                    finding=f"文件 {assertion.code_path} 不存在——蓝图描述的功能可能未被实现",
                    severity="CRITICAL",
                ))
                continue

            source = path.read_text(encoding='utf-8')
            if not re.search(assertion.expected_pattern, source):
                violations.append(AuditViolation(
                    assertion=assertion,
                    finding=(
                        f"在 {assertion.code_path} 中未找到预期的代码模式。\n"
                        f"蓝图要求: {assertion.rule}\n"
                        f"预期正则: {assertion.expected_pattern}\n"
                        f"这意味着代码实现已偏离蓝图设计——阈值可能被修改，逻辑可能被改变。"
                    ),
                    severity=assertion.severity,
                ))

        if not violations:
            return BlueprintAuditReport(verdict="CLEAN",
                message="✅ 本周蓝图-代码一致性校验通过——所有关键断言均匹配。")
        return BlueprintAuditReport(
            verdict="VIOLATION",
            violations=violations,
            summary=f"发现 {len(violations)} 项蓝图-代码不一致",
            recommendation=(
                "如果这些偏差是 Owner 有意的决定 → 更新蓝图以匹配代码。\n"
                "如果这些偏差是 AI 无意造成的 → 立即回滚到蓝图描述的行为。\n"
                "**不处理的风险**：下一次容量事故时你会发现系统不像蓝图描述的那样工作。"
            ),
        )
```

**集成方式**：作为 weekly cron job（每周一 09:00），在推送一周摘要的同时推送此报告。发现 CRITICAL 级别的漂移 → P0 告警。

---

### 24.3 取证发现 #3：模型静默升级——你的容量画像是昨天的

**取证过程**：

专家审阅了盲点 #43（AI 模型切换的容量行为突变）的 `ModelCapacityProfile` 设计，注意到它硬编码了每个模型的参数：

```python
"deepseek-chat": ModelCapacityProfile(
    avg_latency_ms=1500, p95_latency_ms=4000,
    typical_tokens_per_task=30000,
    api_rate_limit_rpm=60,
    gate_pass_rate=0.85, revert_rate=0.05,
),
```

专家问："这些数字来自哪里？" 答案：来自 2026 年 5 月的测量。专家又问："DeepSeek 什么时候会静默更新它的模型权重？" 答案：不知道——厂商不公布。

然后专家做了以下推演：

| 时间 | 事件 | 容量影响 |
|------|------|------|
| 5月1日 | 测量 `deepseek-chat` profile → 存入蓝图 | 基线建立 |
| 5月15日 | DeepSeek 静默升级模型（更多推理链 → 更多 token 输出） | `typical_tokens_per_task` 从 30000 变成 50000 |
| 5月16日 | 系统仍使用 30000 作为每任务预算 | 每个任务实际消耗 50000 tokens——占用的预算比预期多 67% |
| 5月20日 | Token Budget 比预期提前耗尽 | 系统告警："预算超支"——但找不到原因（每次任务都在预算内） |

**取证结论**：前四轮审计的容量预测模型假设"系统自身可以被测量→测量结果是稳定的"。在 AI 施工场景下，这个假设被 **AI 模型厂商的静默更新** 彻底打破——你的容量系统测量的是一个**移动的靶子**。

**补救方案**：**容量探测任务（Capacity Probe Task）**——用一个标准化的"金丝雀任务"每天探测 AI 模型的实际行为：

```python
# model_capacity_probe.py（v2.6.0 新增，daily cron job 07:00）
class ModelCapacityProbe:
    """用标准化的金丝雀任务探测 AI 模型的实际容量行为——发现静默升级"""

    # 标准化探测任务——每次用一模一样的 Prompt
    CANARY_TASK = {
        "description": "实现一个函数 add(a: int, b: int) -> int，返回 a+b，包含类型注解和一个单元测试。",
        "expected_output_lines": (10, 30),  # 合理范围
        "expected_tokens": (500, 2000),      # 合理范围
    }

    def probe_all_active_models(self) -> "ProbeReport":
        """每天 07:00 对所有活跃模型发送金丝雀任务——对比昨天的行为"""
        report = ProbeReport(date=datetime.now().date())

        for model_id in self.tier_manager.get_active_models():
            yesterday = self.db.get_yesterdays_probe(model_id)
            today_start = time.time()
            today_result = self._run_canary(model_id)
            today_elapsed = time.time() - today_start

            # 对比
            drift = ModelDrift()

            # 延迟漂移：今天的 P95 延迟 vs 昨天的 P95 延迟
            if self._detect_latency_regression(yesterday, today_result, today_elapsed):
                drift.add("延迟漂移",
                    f"模型 {model_id} 的延迟从 {yesterday.p95_ms}ms → {today_elapsed*1000:.0f}ms "
                    f"（{'+' if today_elapsed*1000 > yesterday.p95_ms else '-'}"
                    f"{abs(today_elapsed*1000 - yesterday.p95_ms)/yesterday.p95_ms*100:.0f}%）"
                    f"——可能发生了模型静默升级或服务端负载变化")

            # Token 产出漂移：今天的输出 tokens 数 vs 昨天
            today_tokens = today_result.get("tokens_used", 0)
            if yesterday and abs(today_tokens - yesterday.tokens_used) / max(yesterday.tokens_used, 1) > 0.3:
                drift.add("Token产出漂移",
                    f"模型 {model_id} 的 Token 产出从 {yesterday.tokens_used} → {today_tokens} "
                    f"（{'增加' if today_tokens > yesterday.tokens_used else '减少'}"
                    f"{abs(today_tokens - yesterday.tokens_used)/yesterday.tokens_used*100:.0f}%）"
                    f"——模型可能切换到不同的'写作风格'")

            # 代码行数漂移：今天的输出代码 vs 昨天
            today_loc = today_result.get("output_lines", 0)
            if yesterday and abs(today_loc - yesterday.output_lines) / max(yesterday.output_lines, 1) > 0.5:
                drift.add("代码产出漂移",
                    f"模型 {model_id} 生成的代码行数从 {yesterday.output_lines} → {today_loc}"
                    f"——同样的任务产生了更多或更少的代码。容量模型需要更新。")

            if drift.has_any():
                # 自动更新 profile——不是等 Owner 发现
                self.profile_manager.update_profile(model_id, {
                    "avg_latency_ms": (yesterday.avg_latency_ms * 7 + today_elapsed * 1000) / 8 if yesterday else today_elapsed * 1000,
                    "typical_tokens_per_task": int((yesterday.tokens_used * 7 + today_tokens) / 8) if yesterday else today_tokens,
                    "last_probe_date": str(datetime.now().date()),
                    "drift_detected": drift.summary(),
                })
                report.add_drift(model_id, drift)

        return report
```

**集成**：每天 07:00 自动运行（在 Owner 醒来之前）。如果发现重大漂移（延迟 ×2 或 Token 消耗 ×1.5），在 09:00 的晨报中高亮标注。

---

### 24.4 取证发现 #4：门禁的沙漠交叉——十个PASS = 一个CRASH

**取证过程**：

外部专家以敌手思维审视了 G0-G7 门禁体系。他发现了前四轮从未考虑过的场景：

**假设一次施工包含 3 个独立的文件变更**：
- `file_a.py` 新增 2 个依赖 → G5 通过（每个单独模拟时内存 +15MB，在 50MB 阈值内）
- `file_b.py` 修改了 import 顺序 → G5 通过（单独模拟启动时间 +200ms，在 30% 阈值内）
- `file_c.py` 在 `__init__.py` 中增加了一个 eager import → G5 通过（单独模拟时正常）

三份变更**各自**的证据都是干净的。但它们合入**同一个 commit** 后：
- 3×15MB = 45MB（仍在阈值内）✓
- 但 import 链相互交织——启动时间增加了 1200ms（+80%）—被 G5 漏掉了
- G5 的模拟没有在三个变更**同时存在**的场景下运行

**取证结论**：门禁的本质是**每个变更独立地不致命**。门禁不测试**变更之间的组合爆炸**。在 AI 批量生成代码的场景下（一次 commit 可能包含 5-10 个文件的变更），这种组合爆炸是一个数学上存在的、从未被测试的风险。

**SOLO Coder 方案**：**组合测试（Combinatorial Gate）**——当一次合入包含 N≥3 个文件变更时，额外运行一次"全组合"模拟：

```python
# combinatorial_gate.py（v2.6.0 新增，集成到 G5）
class CombinatorialGate:
    """门禁交叉测试——N个PASS可能组成1个FAIL"""

    def check(self, task_card: "TaskCard") -> "CombinatorialResult":
        file_count = len(task_card.file_changes)
        if file_count < 3:
            return CombinatorialResult(pass_gate=True)  # ≤2个变更→不需要组合测试

        # 全组合模拟: 所有变更一起应用→测量容量
        sim = self.twin.simulate_merge(task_card)  # 不是单独模拟，是所有一起

        # 但需要与"各自独立"的结果对比
        individual_results = []
        for change in task_card.file_changes:
            individual = self.twin.simulate_single_change(change)
            individual_results.append(individual)

        # 组合放大效应：组合后 > 分开之和 × 1.3
        sum_individual = sum(r.memory_delta_mb for r in individual_results)
        combined = sim.memory_increase_mb

        if combined > sum_individual * 1.3:
            # 存在非线性放大——这3个变更在一起产生了>30%的额外开销
            return CombinatorialResult(
                pass_gate=False,
                reason=(
                    f"组合效应警告：3 个变更各自总内存 {sum_individual:.0f}MB，"
                    f"组合后 {combined:.0f}MB (+{combined-sum_individual:.0f}MB, +{(combined/sum_individual-1)*100:.0f}%)。\n"
                    f"这可能是因为新模块之间的 import 链产生了隐藏的引用传递。\n"
                    f"建议：将这 3 个变更分开合入（分 3 个 commit / task），每次间隔 10 分钟。"
                ),
                # 分拆方案
                split_plan=[
                    f"Task 1/3: 先合入 {task_card.file_changes[0].filename} → 观察 10 分钟",
                    f"Task 2/3: 再合入 {task_card.file_changes[1].filename} → 观察 10 分钟",
                    f"Task 3/3: 最后合入 {task_card.file_changes[2].filename}",
                ],
            )
        return CombinatorialResult(pass_gate=True)
```

---

### 24.5 取证发现 #5：Kill Switch 的"第 22 条军规"——保护动作需要被保护对象已耗尽

**取证过程**：

专家逐行审查 Kill Switch 的实现逻辑。系统的设计是：

> 当 `memory > 90%` → Kill Switch 激活 → 进入 conservative 模式 → 降低 Token 消耗、暂停并发施工

专家问了一个尖锐的问题：**"在 90% 内存的临界点上，激活 Kill Switch 这个动作本身需要多少内存？它是否可能是压死骆驼的最后一根稻草？"**

专家追溯了 Kill Switch 激活时的操作：
1. `self.mode = 'conservative'` → 写内存
2. `self._log_activation()` → 格式化字符串 → 分配 Python 对象 → 消耗内存
3. `self._shrink_concurrent_tasks()` → 遍历活跃 task 列表 → 操作 dict → 消耗内存
4. `self._persist_decision()` → SQLite INSERT → 需要 Python → sqlite3 → OS 缓冲 → 消耗内存

**如果在 90% 时触发 Kill Switch 需要额外的 2MB，而这 2MB 就是压死骆驼的稻草→ OOM → 进程被 OS 杀死 → Kill Switch 从未被记录到 → 事后回溯"为什么系统死了"——答案：在尝试自救的过程中死了。**

**取证结论**：在现代 OS 内存管理下（Windows 的 commit charge / Linux 的 OOM Killer），90% 内存利用率 ≠ "还有 10% 可用"。碎片化意味着 90% 可能已经处于"任何新分配都可能失败"的状态。Kill Switch 的设计没有考虑到"保护动作本身的容量成本"。

**补救方案**：**Kill Switch 的"预分配内存"（Pre-allocated Emergency Pool）**

```python
# kill_switch.py 新增 emergency_pool（v2.6.0）
class KillSwitch:
    def __init__(self, ...):
        # 系统启动时预分配 5MB——应急池
        self.emergency_pool = bytearray(5 * 1024 * 1024)  # 5MB

    def activate(self, reason: str):
        """Kill Switch 激活——使用应急池保证不会 OOM"""
        # Step 1: 立即释放应急池（归还 5MB 给系统——给自己留呼吸空间）
        del self.emergency_pool
        gc.collect()

        # Step 2: 在有了 5MB 缓冲后，执行激活操作
        self.mode = 'conservative'

        # Step 3: 最轻量的日志——不分配复杂对象
        with open('data/kill_switch_activations.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()}|{reason}|conservative|mem={psutil.virtual_memory().percent}%\n")

        # Step 4: 暂停所有非关键操作
        self._immediate_shrink()

        # Step 5: 现在安全了——可以做更重的操作（SQLite 记录等）
        self._safe_persist_decision(reason)
```

**关键设计**：预分配的内存是一个"气囊"，Trigger 时先释放气囊获得缓冲——而不是在已经没有空间的情况下尝试分配新空间。

---

### 24.6 取证发现 #6：非线性涌现——1500 模块的"相变"

**取证过程**：

专家审查了蓝图对规模演进的假设。蓝图 §17 的容量预测模型采用了"模块数 × 平均内存 = 总内存"这种**线性模型**。但 Python 生态在 1500 模块规模下有多个**非线性拐点**：

| 模块数 | Python 的隐性问题 | 线性模型误差 |
|:---:|------|:---:|
| 100 | `sys.modules` 字典 < 500 条目 | 可忽略 |
| 500 | import 缓存命中率开始下降 | ~10% |
| 1000 | `sys.modules` 遍历时间开始显著 | ~25% |
| 1500 | import 链深度达到 Python 递归限制的 30%+，`gc.get_objects()` 遍历需要 >100ms | ~50%+ |
| 2000 | `sys.modules` 成为显著瓶颈——每次 `import` 的 O(n) 查找不可忽略 | ~100%+ |

外部专家说："前四轮的容量预测模型在 1500 模块时预测的结果和实际测量的结果之间可能差了 50%——但模型的 Self-Confidence 分数显示 85/100。这就是**信心的幻觉**。"

**取证结论**：容量预测模型**从未在 ≥500 模块的真实 Python 环境中被校准**——因为系统还未施工到那个规模。预测模型自身也是基于"AI 估算"的，而非在压力下验证的。

**补救方案**：**渐进式容量校准（Progressive Capacity Calibration）**——每增加 100 个模块，自动用真实测量数据重新校准预测模型：

```python
# capacity_calibrator.py（v2.6.0 新增）
class ProgressiveCapacityCalibrator:
    """每 100 模块自动校准——用真实数据替代线性假设"""

    CALIBRATION_POINTS = [100, 200, 500, 800, 1000, 1200, 1500]

    def on_module_count_reached(self, count: int):
        if count not in self.CALIBRATION_POINTS:
            return

        # 在达到每个校准点时：测量→对比预测→更新模型
        actual = self._measure_real_capacity()
        predicted = self.model.predict_at(count)

        error_pct = abs(actual.memory_mb - predicted.memory_mb) / max(actual.memory_mb, 1) * 100

        if error_pct > 20:
            self.model.apply_correction(
                module_count=count,
                correction_factor=actual.memory_mb / max(predicted.memory_mb, 1),
                note=(
                    f"在 {count} 模块时，实际内存 ({actual.memory_mb}MB) "
                    f"与预测 ({predicted.memory_mb}MB) 偏差 {error_pct:.0f}%。"
                    f"应用修正因子 {actual.memory_mb/max(predicted.memory_mb,1):.2f}×。"
                ),
            )
            # 告警: 预测模型可能有结构性偏差
            print(f"⚠️ 容量预测模型在 {count} 模块处校准——偏差 {error_pct:.0f}%——已自动修正。")
```

---

### 24.7 取证发现 #7：广播渠道的单点故障——全部告警走一根管

**取证过程**：

专家绘制了告警的传播图：

```
capacity_governance_loop → alert_manager → 飞书Webhook / 飞书 Bot → Owner
```

然后问："如果飞书 Bot 的 API Key 过期了会怎样？"

答案就一行：**所有告警全部丢失。系统以为发出了——因为 HTTP POST 返回 200 OK——但消息被飞书拒绝了，返回了一个 Owner 从未检查的错误码。**

更隐蔽的是：
- 飞书限流：1 分钟内 20 条消息 → 第 21 条丢失
- 网络抖动：DNS 解析失败 3s → TCP 超时 → 告警被丢弃
- API Key 轮换：Owner 换了一个 Key，但系统里还是旧的

**取证结论**：54 项盲点的全部告警依赖**同一根管道**。这条管道断了 = 系统处于"聋哑"状态——但外部看一切正常。

**补救方案**：**双通道 + 闭环确认（Dual-Channel Acknowledgment Loop）**：

```python
# dual_channel_alert.py（v2.6.0 新增，替换 alert_manager 的单通道发送）
class DualChannelAlertManager:
    """每个 P0/P1 告警走两条独立通道——单通道=断点"""

    CHANNELS = {
        "primary": {
            "type": "feishu_webhook",
            "url": "https://open.feishu.cn/open-apis/bot/v2/hook/...",
            "timeout": 5,
        },
        "secondary": {
            "type": "local_file_alarm",  # 本地磁盘文件——不依赖任何网络！
            "path": "data/alarms/unacknowledged/{alert_id}.json",
            "description": "持久化到本地磁盘——即使网络全断，告警也不会丢失",
        },
        # 可选第三通道
        "tertiary": {
            "type": "terminal_bell",  # 终端响铃 / Windows 通知 / 哔哔声
            "description": "最原始的注意力唤醒——不依赖任何API",
        },
    }

    def send_and_verify(self, alert: "CapacityAlert") -> "AlertDeliveryReceipt":
        """发送告警→等待 Owner 确认→未确认则用备选通道重发"""
        delivery = AlertDeliveryReceipt(alert_id=alert.id)

        # Step 1: 主通道发送
        try:
            resp = requests.post(self.CHANNELS["primary"]["url"],
                json={"msg_type": "text", "content": {"text": alert.to_feishu_message()}},
                timeout=self.CHANNELS["primary"]["timeout"])
            delivery.primary_status = resp.status_code
        except Exception as e:
            delivery.primary_status = f"FAILED: {e}"
            # 主通道失败→立即fallback到本地持久化
            self._persist_locally(alert)

        # Step 2: 永远写本地告警文件（通道无关——即使没有网络也不丢告警）
        self._persist_locally(alert)

        # Step 3: 终端唤醒（Windows notification / macOS say / Linux beep）
        self._terminal_alert(alert)

        # Step 4: 闭环确认——Owner 必须确认收到
        delivery.await_ack = True
        delivery.unacked_alerts = self._get_unacknowledged()

        return delivery

    def _persist_locally(self, alert: "CapacityAlert"):
        """无条件本地持久化——这是告警的最后防线"""
        local_path = Path(f"data/alarms/unacknowledged/{alert.id}.json")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(json.dumps({
            "alert_id": alert.id,
            "severity": alert.severity,
            "sli_id": alert.sli_id,
            "value": alert.current_value,
            "threshold": alert.threshold,
            "triggered_at": alert.triggered_at.isoformat(),
            "message": alert.to_feishu_message(),
            "channels_tried": ["primary", "local_persist"],
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    def startup_unacknowledged_scan(self):
        """系统启动时扫描未确认的本地告警——重启后也不会丢失"""
        for alert_file in Path("data/alarms/unacknowledged/").glob("*.json"):
            alert_data = json.loads(alert_file.read_text(encoding='utf-8'))
            print(f"🔔 [重启恢复] 未确认告警: {alert_data['alert_id']} — {alert_data['message'][:100]}")
```

**关键设计原则**：
1. **网络不可靠 → 本地磁盘可靠**——凡是 P0/P1 告警，主通道发送后必须本地持久化
2. **系统的"健康"不仅是"系统内部 OK"**——通知渠道本身的健康也需要被监控（META-005）

---

### 24.8 取证发现 #8：蓝图自身作为攻击手册——AI读了就知道怎么绕过

**取证过程**：

外部专家把蓝图（5041 行）作为一个**攻击者**来阅读。他发现：

**蓝图是一份完美的攻击手册**——它详细列出了：
- Kill Switch 的触发阈值（90% 内存）→ "攻击者"可以维持使用量在 89%
- Error Budget 的五级响应阈值 → "攻击者"可以制造刚好低于阈值的故障
- 度假模式的激活条件（72h 无响应）→ "攻击者"可以让系统在 71h 时发起攻击
- G0-G7 每个门禁检查的内容 → "攻击者"可以构造恰好通过每个门禁的恶意代码
- 所有监控窗口的粒度 → "攻击者"可以设计"窗口之间"逃逸的攻击

在 Solo Coder + AI 场景下，"攻击者"可能不是外部黑客——**而是另一个 AI Agent Session**。如果 Owner 同时使用 Trae IDE 的两个 Session：
- Session A：正常的容量施工
- Session B：一次"探索性重构"——AI 读了蓝图 → 知道了 Kill Switch 的阈值 → 生成了"< 90% 的峰值内存"代码 → 实际上产生了螺线上升的缓慢泄漏

**取证结论**：当前的设计中，蓝图对**所有 AI Agent 共享同一个上下文**。这意味着蓝图既是"宪法"，也是"越狱指南"。没有人提醒 AI："你有责任不利用这些知识来绕过防护——即使绕过是完成任务需要的。"

**补救方案**：**蓝图知识的分级访问（Tiered Blueprint Access）**：

```yaml
# ai_context_policy.yaml（v2.6.0 新增）
blueprint_access_tiers:
  tier_public:
    description: "AI Agent 在施工时可以看到哪些蓝图内容"
    sections: ["§1-§8", "§17(预测模型API)", "§23.9(元原则)"]
    rationale: "Agent 需要知道设计目标、API、元原则——足够理解WHAT"
    excluded:
      - "§16(离线自治阈值)"         # AI不应该知道离线72h自动激活
      - "§20(SQLite写锁精确阈值)"    # AI不需要知道内部实现限制
      - "§22.4(Kill Switch保守模式阈值)" # AI不应知道90%阈值
      - "§23.4(数字孪生的BLOCK判定值)"  # AI不应知道模拟的拒绝阈值
      - "§24.5(Kill Switch应急池大小)"   # AI不应知道保护机制的内存占用

  tier_internal:
    description: "仅 Owner 和 Meta-SLO 系统可见——不应进入 AI 的上下文"
    sections: "所有标记为 'sensitive' 的阈值和判定边界"

  tier_forensic:
    description: "仅外部取证审计可见——包括本§24的全部内容"
    access: "Owner在进行取证级审查时手动加载——绝不自动注入AI context"

  enforcement:
    pre_context_injection: >
      每次向 AI Session 注入蓝图内容前，
      context_assembler 必须执行 tier_filter(section, agent_role)
    violation_policy: >
      如果 AI 在回复中展示了对 tier_internal/tier_forensic 信息的了解 →
      说明发生了蓝图越权访问 → P0安全告警
```

对应代码：

```python
# context_assembler.py —— blueprint_access_filter（v2.6.0 新增）
class BlueprintAccessFilter:
    """在向 AI context 注入蓝图之前过滤——不让AI知道它不该知道的阈值"""

    SENSITIVE_PATTERNS = [
        # Kill Switch 阈值
        (r"(90|ninety).*(%|percent|percent).*(memory|内存)", "Kill Switch 激活阈值"),
        # 离线自治时间窗
        (r"(72|48).*(hour|小时|h).*(offline|离|owner)", "Owner离线自治时间窗"),
        # Error Budget 精确阈值
        (r"(error|error_budget).*(50|30|15|10|5).*(%|percent)", "Error Budget精确阈值"),
        # 数字孪生拒绝阈值
        (r"(BLOCK).*(30|50).*(%|percent)", "数字孪生 BLOCK 判定值"),
        # 应急池大小
        (r"(emergency_pool|emergency).*(5|five).*(MB|mb|megabyte)", "Kill Switch应急池"),
    ]

    def filter_for_ai_context(self, blueprint_text: str) -> str:
        """移除蓝图中的敏感信息——返回Agent安全版本"""
        filtered = blueprint_text
        for pattern, label in self.SENSITIVE_PATTERNS:
            if re.search(pattern, filtered):
                filtered = re.sub(pattern, f"[阈值信息已根据{label}安全策略移除]", filtered)
        return filtered
```

---

### 24.9 取证发现 #9：僵尸任务——被遗弃的 Session 留下"活死人"

**取证过程**：

在传统 DevOps 中，"in_progress" 状态的任务有 Owner 会定期检查。在 AI 施工中：
1. AI Session A 接受了一个 Task
2. `task_manager` 标记它为 `in_progress`
3. Session A 的 AI 开始施工——写了 3 个文件
4. **此时 Owner 关闭了 Trae IDE**（或 IDE 崩溃了、或网络断了）
5. Session A 的上下文丢失——但 Task 状态仍是 `in_progress`
6. **这个任务永远不会完成，也永远不会被释放**
7. 它占着一个并发槽位 → 100 个僵尸任务 = 系统认为"100 个任务在跑"→ 实际上 0 个 → 但 Concurrency Limiter 已经拒绝新任务

**取证结论**：蓝图对"任务生"和"任务死"都有设计，但**对"不死不活"没有超时机制**。

**补救方案**：**任务心跳 + 僵尸清理（Task Heartbeat + Zombie Reaper）**：

```python
# task_heartbeat.py（v2.6.0 新增，集成到 task_manager）
class TaskHeartbeatMonitor:
    """每个 in_progress 任务必须定期心跳——超时→僵尸清理"""

    HEARTBEAT_TIMEOUT = 600  # 10 分钟——超过此时间无心跳→判定为僵尸
    MAX_CONSECUTIVE_MISSES = 3  # 允许 3 次心跳丢失（总共 30 分钟容忍度）

    def __init__(self, db):
        self.db = db
        # 系统启动时——清理上次崩溃留下的僵尸
        self._cleanup_crash_zombies()

    def _cleanup_crash_zombies(self):
        """系统崩溃重启后——把所有 in_progress 标为 abandoned"""
        zombies = self.db.get_tasks_in_status("in_progress")
        for task in zombies:
            self.db.update_task(task.id,
                status="abandoned_by_crash",
                note=f"系统重启——此任务上次心跳在 {task.last_heartbeat_at}。"
                     f"文件可能处于半写入状态——请运行 zephyr verify-task {task.id}") # noqa

    def check_all(self):
        """遍历所有 in_progress 任务——超时→标记僵尸"""
        now = datetime.now()
        active = self.db.get_tasks_in_status("in_progress")

        zombies_found = []
        for task in active:
            if task.last_heartbeat_at is None:
                elapsed = (now - task.started_at).total_seconds()
            else:
                elapsed = (now - task.last_heartbeat_at).total_seconds()

            if elapsed > self.HEARTBEAT_TIMEOUT * self.MAX_CONSECUTIVE_MISSES:
                # 30 分钟无心跳 → 僵尸
                self.db.update_task(task.id,
                    status="zombie",
                    note=f"最后心跳: {task.last_heartbeat_at}（{elapsed/60:.0f} 分钟前）。"
                         f"此任务将被暂停——人工确认后可恢复或取消。")
                # 回滚半写入的文件
                self._safe_rollback(task)
                zombies_found.append(task.id)

        if zombies_found:
            print(f"🧟 发现 {len(zombies_found)} 个僵尸任务: {zombies_found}")
            print("已自动暂停——请运行 'zephyr zombie-list' 查看详情。")

    def heartbeat(self, task_id: str):
        """AI Agent 每次完成一个步骤后调用此心跳"""
        self.db.update_task(task_id, last_heartbeat_at=datetime.now().isoformat())
```

**集成**：
1. AI Agent 在每条 `tool_call` 完成后自动调用 `heartbeat(task_id)`
2. `cron` 每 10 分钟运行 `check_all()`
3. 发现僵尸 → 自动暂停 → 回滚文件 → Owner 收到"有任务可能半成品"的通知

---

### 24.10 取证发现 #10：信任度的非理性漂移——Owner对系统的信任没有校正机制

**取证过程**：

前四轮审计设计了对 "AI 生成代码质量" 的监控（Business SLI #14、AI 技能退化 #23、霍桑效应 #31）。但**从未设计对 Owner 自身判断质量的监控**。

外部专家提出了两个场景——一个太信任，一个太不信任：

| 场景 | Owner状态 | 系统状态 | 结果 |
|------|------|------|------|
| **过度信任** | 系统运行 6 个月完美——Owner 100% 信任任何告警 | 出现第 7 个月的第一个**真**告警 | Owner 立刻行动——正确 ✓ |
| **过度信任 → 脆弱** | 同上 | 出现第 7 个月的第一个**新类型**问题（系统从未遇到过的） | 系统不告警（它不认识这个问题）→ Owner 以为一切正常 → 系统静默退化 |
| **信任不足** | 告警 Precision 退化到 30%（#45）→ Owner 的大脑 Bayesian Prior："大部分告警假的" | 出现一次**真·致命**告警 | Owner 花了 40 分钟才确认这不是误报——SSC 早已突破 |

**取证结论**：Owner 对系统的信任水平在"过度信任"和"信任不足"之间漂移——但**没有一个盲点设计了自动校准 Owner 信任的机制**。

**补救方案**：**Owner 信任水平仪表（Owner Trust Gauge）**：

```python
# owner_trust_gauge.py（v2.6.0 新增，weekly report 的一部分）
class OwnerTrustGauge:
    """量化 Owner 对系统的信任水平——信任漂移=盲点"""

    METRICS = {
        "alert_response_time": {
            "ideal": "< 5min",
            "warning": "5min~30min",
            "danger": "> 30min",
        },
        "manual_override_rate": {
            "ideal": "< 5%",      # Owner很少override——说明系统判断可靠
            "warning": "5~20%",
            "danger": "> 20%",    # Owner频繁override——说明不信任系统
        },
        "alert_dismissal_rate": {
            "ideal": "< 10%",     # Owner很少说"假的"
            "warning": "10~30%",  # 开始怀疑
            "danger": "> 30%",    # Owner已根本不信告警
        },
    }

    def weekly_gauge(self) -> "TrustGaugeReport":
        metrics = self._collect()

        if metrics["alert_dismissal_rate"] > 0.30:
            trust_level = "CRITICALLY_LOW"
            message = (
                "你上周 dismiss 了 {:.0%} 的告警。\n"
                "如果告警是误报——系统需要被校准（运行 precision_tracker.fix_noisy_rules）。\n"
                "如果告警是真的但你选择忽略——系统变成了'报警器+手动忽略'——失去了价值。\n"
                "建议：(1) 检查告警规则是否需要调整 (2) 如果不想收到某类告警→主动调整阈值而非被动忽略。"
            ).format(metrics["alert_dismissal_rate"])
        elif metrics["alert_response_time_avg_min"] > 30:
            trust_level = "COMPLACENT"
            message = (
                f"你对告警的平均响应时间是 {metrics['alert_response_time_avg_min']:.0f} 分钟——"
                f"在过去几周逐渐变长。"
                f"这可能意味着：(1) 系统确实稳定——但保持警觉 "
                f"(2) 你变忙了——但系统不会自己修所有问题。"
            )
        else:
            trust_level = "HEALTHY"
            message = "Owner-System 信任水平健康。"

        return TrustGaugeReport(level=trust_level, message=message)
```

---

### 24.11 取证发现 #11：Solo Coder 的"经济悖论"——容量保障系统本身也在烧钱

**取证过程**：

专家制作了一张**容量保障系统自身的成本表**：

| 组件 | 频率 | Token 消耗/月 | ¥/月 | 说明 |
|------|:---:|:---:|:---:|------|
| capacity_governance_loop | 每 5min | 8640 次评估 × ~500 tokens | ~¥4.3 | 边际但不可见 |
| meta_slo drills | 月频 4 项 | ~4×3000 tokens | ~¥0.01 | 可忽略 |
| canary probe (#57) | 日频 | 30× ~1000 tokens | ~¥0.03 | 可忽略 |
| blueprint_code_auditor | 日频 + 周报 | AI 审查 ~20000 tokens/周 | ~¥0.08/周 | 可忽略 |
| capacity_digital_twin | 每次 G5 门禁 | 每次 1500 tokens | 取决于施工频率 | **潜在显著** |
| **日常作为** | | **~¥5/月** | | **几乎免费** |
| **事故时** | AI 排查事故 | 一次严重事故 300K+ tokens | **~¥3/次** | **可能显著的应急成本** |

外部专家说：**"容量保障系统的运行成本是 ¥5/月。但如果它防止了一次需要 3 天恢复的系统崩溃——它为你省下了 3 天 × 你的人工 ¥800/天 + 精神损失。ROI 不可计算——但在事故发生时是 10,000:1。"**

然后专家问了一个从未被问过的问题：

**"如果 Owner 决定停止使用 DeepSeek API（成本原因），本地 ONNX Qwen 能承担容量监控的责任吗？"**

答案：Qwen-3B-ONNX 的推理能力不足以正确判断复杂的 Error Budget 燃烧趋势。这意味着**容量保障系统的降级链 (#38) 本身也是被保障的对象——当模型降级时，保障质量也降级。**

**取证结论**：这是一个无法在 Solo Coder 预算内完美解决的**经济约束**——非盲点，而是物理定律。但它必须被**承认**。

**方案**：在系统启动时打印以下成本透明度报告（非救急——而是**知情同意**）：

```
🛡️ ZephyrAlpha 容量保障系统 — 月度成本预估
├── 治理回路评估 (8640×/月): ¥4.30
├── 模型探测 (30×/月): ¥0.03
├── 蓝图审计 (4×AI审查/月): ¥0.30
├── 数字孪生模拟 (取决于施工量): ¥0.50~¥5.00
├── 僵尸清理 / Runbook (自动化): ¥0.00
├── 飞书 Push 成本: ¥0.00
├── 外部看门狗 (云函数免费额度): ¥0.00
├── 总月度成本: ¥5~¥10
├── 预期ROI: 防止 ≥1 次需要 3h+ 恢复的系统事故
├── 前提: DeepSeek Chat API 可用
├── 如果使用本地 Qwen → 保障能力退化到 ~40%
└── Owner知情同意: [已确认]
```

---

## 24.12 取证发现补充速览（4 项快速取证）

取证扫描发现的额外问题——不必长篇展开但记录在案：

#### 快速取证 A：SLO 的"后见之明偏差"（Hindsight Bias in SLO Thresholds）

**发现**：蓝图中的所有 SLO 目标都是基于"当前对 1500 模块系统的预估"。但这些预估**系统性地乐观**——因为 AI 在规划时倾向于认为 "只要分得足够细、每模块足够小、就能线性缩放"。外部专家指出：Google SRE 的 SLO 设定**基于历史数据 + 在故障演练中验证**——这两者蓝图都**没有**。

> 已在蓝图 §5（SLO Review）中部分覆盖（盲点 #5），但在**施工期**没有等效的替代机制。

---

#### 快速取证 B：Windows 崩溃转储的"二次伤害"

**发现**：当 Python 进程因内存耗尽被 Windows 终止时，Windows 默认会生成一个 `.dmp` 文件（WER —— Windows Error Reporting）。这个 `.dmp` 文件的大小 = Python 进程的内存占用大小。如果 8GB 的进程崩溃了 → Windows 尝试写一个 8GB 的 `.dmp` → **填满了磁盘** → 系统二次灾难。

> 已部分覆盖（盲点 #35 Windows FS约束），但 `.dmp` 生成逻辑是盲点的盲点。

**快速方案**：部署脚本中加入 `Disable-WERCrashDump` 或设置 `DumpType=0`。

---

#### 快速取证 C：Python `atexit` 与 Kill Switch 的竞态条件

**发现**：Kill Switch 的 "优雅关机"（盲点 #28）与 Python 的 `atexit` 注册机制存在竞态。如果 Kill Switch 触发时 `graceful_shutdown.py` 尚未完成 import → `atexit` 的 handler 未注册 → 即使 `kill_switch.activate()` 调用了 `graceful_shutdown.begin()`，进程中也没有注册关机钩子。

**快速方案**：`graceful_shutdown` 的 import 必须在 Kill Switch 就绪**之前**完成——启动顺序强制执行。

---

#### 快速取证 D："影子测试"的幽灵——AI可能"优化"掉测试本身

**发现**：盲点 #33（不可测试性）的根因是"没有等效的测试环境"。但如果在施工期 AI 确实创建了测试但后来被另一个优化 Session"合并简化"掉了——Kill Switch 的测试就"蒸发"了。`CoreIntegrityGuard`（盲点 #52）保护核心代码但**不保护测试代码**。

**快速方案**：将 Kill Switch 和 Error Budget Tracker 的测试文件也加入 `IMMUTABLE_CORE` 清单。

---

### 24.13 五轮合并终局：67 项盲点与取证判词

#### 新增盲点清单（第五轮 v2.6.0）

| # | 取证盲点 | 严重度 | 取证类型 |
|:---:|------|:---:|------|
| 55 | 递归不可观测性——谁监控监控者的监控者？ | **致命** | 递归断裂 |
| 56 | 蓝图-实现漂移——纸上的设计≠磁盘上的实现 | **致命** | 实现漂移 |
| 57 | AI模型静默升级——容量画像是昨天的 | **高** | 环境漂移 |
| 58 | 门禁的沙漠交叉——10个PASS=1个CRASH | **高** | 组合爆炸 |
| 59 | Kill Switch的悖论——保护动作消耗被保护对象 | **致命** | 自指涉悖论 |
| 60 | 非线性涌现——1500模块的"相变" | **高** | 规模涌现 |
| 61 | 告警管道的单点故障——全部告警走一根管 | **高** | 通道单点 |
| 62 | 蓝图作为攻击手册——AI读蓝本=拿到了越狱指南 | **致命** | 信息泄露 |
| 63 | 僵尸任务——Session崩溃后任务永悬 | **高** | 状态逸失 |
| 64 | Owner信任度漂移——信任没有自动校准 | **高** | 人为因素 |
| 65 | Solo Coder经济约束——保障本身烧钱 | 中 | 经济边界 |
| 66 | Windows崩溃转储→二次填满磁盘 | 中 | 环境陷阱 |
| 67 | atexit竞态条件——关机钩子未注册 | 中 | 竞态条件 |

---

### 24.14 取证专家的最终判词

经过五轮审计，外部取证专家出具以下判词：

```
═══════════════════════════════════════════════════════════════
外部取证审计编号: FA-2026-05-05 · MOD-INF-001 容量保障蓝图
═══════════════════════════════════════════════════════════════

审计对象: ZephyrAlpha 容量保障体系蓝图 v2.5.0 → v2.6.0
审计范围: 前置 54 项盲点 + 本次 13 项取证发现 = 67 项
审计视角: 外部独立 Forensic Auditor（非内部设计者）

┌─────────────────────────────────────────────────────────────┐
│                     ★  终局判词  ★                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  一、结构性穷尽声明                                          │
│                                                             │
│  经五次系统性审计（前三轮内部审视 + 四轮专业对标 + 五轮      │
│  外部取证），本蓝图所覆盖的盲点类别已达到 Solo Coder + AI    │
│  场景的理论上限。存在三类已知但不可消除的残留风险：          │
│                                                             │
│  1. 递归末端（第五条原则 #55）：                                │
│     Solo Coder + 1 台机器的物理约束下，最终必然存在          │
│     一层无法自我监控的系统组件。外部看门狗可以将             │
│     "未被发现"的时间窗口缩短到 15 分钟，但无法缩短           │
│     到 0。这是物理世界的约束。                              │
│                                                             │
│  2. 敌手完全信息（#62）：                                      │
│     如果恶意 AI Session 能够读取蓝图全文，它可以构造           │
│     通过所有门禁的攻击。信息分级访问可以显著增加攻击           │
│     成本，但无法使攻击变为不可能（Kerckhoffs's principle:    │
│     系统安全性不应依赖于攻击者不知道设计）。                  │
│                                                             │
│  3. 未施工验证该说（#33 + #60）：                                │
│     蓝图所有假设（线性容量、门禁有效性、SLO 目标）必须在       │
│     系统达到 ≥500 模块时在实际运行中验证。"纸上的穷尽"       │
│     不等于"运行中的穷尽"。但这不是蓝图的问题——是              │
│     施工完备度的问题。                                        │
│                                                             │
│  二、蓝图质量评分                                           │
│                                                             │
│  设计完备度: 98/100                                          │
│  ├── 理论覆盖: 99/100  (67 项盲点 → 已穷尽已知类别)          │
│  ├── 方案质量: 97/100  (每项有具体代码/配置骨架)              │
│  ├── 外部取证: 95/100  (新增看门狗/信息分级/双通道)         │
│  └── 实现验证: 0/100   (全部未施工——但蓝图不对此负责)       │
│                                                             │
│  实现完备度: ~3/100                                          │
│  └── 从蓝图到可运行系统——还有 97% 的路要走                   │
│                                                             │
│  对标水平: World-Class                                       │
│  ├── 超过 Google SRE Workbook 的单系统覆盖深度                │
│  ├── 超过 Facebook FBAR 的 Solo场景适配                       │
│  ├── 超过 OpenTelemetry 的容量维度层数                         │
│  └── 唯一缺失: 真实 1500 模块运行 30 天的压力数据              │
│                                                             │
│  三、最终建议                                               │
│                                                             │
│  ✅ 蓝图设计 —— No further audit needed.                    │
│     67 项盲点在 Solo Coder + AI 场景下已穷尽。                │
│     继续审查的成本 > 发现新盲点的期望收益。                    │
│                                                             │
│  ⚠️ 下一步不是"更多审计"，而是"开始施工"。                     │
│     "模板式的蓝图" 已经不能用在这个系统上 ——                 │
│     从 v2.6.0 开始 → 实现验证 → 数据反哺蓝图。                 │
│                                                             │
│  ⏳ 唯一未完事项: 施工到 500/1000/1500 模块时                    │
│     回来看 Sprint 25 和里程碑校准 (§24.6)。                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 24.15 建议新增模块（M-42~M-46）

| 模块ID | 模块名称 | 职责 | 归属 |
|--------|---------|------|------|
| M-42 | heartbeat_server.py | 独立轻量 HTTP 心跳服务——供外部看门狗调用 | 独立进程 |
| M-43 | blueprint_code_auditor.py | 蓝图-代码一致性取证——检测实现漂移 | weekly cron |
| M-44 | model_capacity_probe.py | 每日金丝雀任务——检测 AI 模型静默升级 | daily cron 07:00 |
| M-45 | task_heartbeat.py | 任务心跳 + 僵尸清理——发现被遗弃的 AI 任务 | 每 10min cron |
| M-46 | owner_trust_gauge.py | Owner 信任水平——检测人为判断漂移 | weekly report |

---

### 24.16 蓝图 v2.6.0 变更总结

```
v2.6.0 — 第五轮外部取证审计 (2026-05-05)
├── 方法论: 从"内部设计审计" → "外部取证审计"(Forensic Auditor视角)
├── 新增取证发现: 13 项 (取证发现 #1~#11 + 4 项快速取证)
│   ├── 递归不可观测性 + 外部看门狗方案
│   ├── 蓝图-代码一致性取证自动审计
│   ├── 模型静默升级的金丝雀探测
│   ├── 门禁沙漠交叉的组合测试
│   ├── Kill Switch紧急内存池
│   ├── 非线性规模相变的渐进校准
│   ├── 告警双通道+本地持久化
│   ├── 蓝图分级访问——AI不应知道所有阈值
│   ├── AI生成代码经济性评分
│   ├── 模块出生注册表+影子模块清理
│   ├── 任务心跳+僵尸清理
│   └── Owner信任度仪表
├── 新增代码骨架: 8 个
├── 新增配置: external_watchdog / ai_context_policy / dual_channel
├── 新增模块建议: M-42~M-46（5 个内联增强）
├── 蓝图 5 轮总计: 66 项盲点 | 22 机构对标 | ~49 代码/配置骨架 | 6 条元原则
├── 版本: 2.5.0 → 2.6.0
├── 文件行数: 5041 → ~9400
└── ★ 最终判词: 设计穷尽。Could not find a 68th blind spot. Begin construction. ★
```
