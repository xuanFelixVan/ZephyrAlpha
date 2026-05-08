---


task_id: TASK-MOD-INF-001-0018
module_id: MOD-INF-001
title: "关键关联清单、依赖图谱、需要更新的相关内容、后果预测"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:05:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0004
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
acceptance_criteria:
  - "§15 关键关联清单：9份关联文档/蓝图引用正确"
  - "§17 集成目标：4个目标模块(Agent RBAC/Budget Enforcer/Rollback System/System Telemetry)映射正确"
  - "需要更新的相关内容：metadata-registry.yaml中MOD-INF-001条目 + budget-enforcer/blueprint.md补ref"
  - "§16 依赖图谱：correctness_deps/execution_deps/distribution_deps三类依赖完整"
  - "§18 后果预测：正向3项(current_blind_spots/architecture_fit/edge_cases) + 反向3项(施工反噬/Observability复杂性/MacGyver式Patch)完整"
rollback_instructions:
  - "关联清单变更可独立回滚"
  - "metadata-registry修改回滚到上一版"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§15 关键关联", "§16 依赖图谱", "§17 集成目标", "§18 后果预测", "需要更新的相关内容", "输出目录"]
    purpose: "提取关联清单/依赖图谱/集成目标/后果预测的全部内容"
tags:
  - capacity-assurance
  - metadata-registry
  - dependency-graph
  - integration-targets
  - consequences
phase: phase_0_foundation
estimated_effort_minutes: 90
ai_autonomy: Human-Gated
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §15-§18 关键关联/依赖/集成/后果 + 后果（Consequences）"
description: "关键关联清单、依赖图谱、需要更新的相关内容、后果预测"
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 27000
timeout_minutes: 90
depends_on:
  - TASK-MOD-INF-001-0001
  - TASK-MOD-INF-001-0004
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# 关键关联清单、依赖图谱、需要更新的相关内容、后果预测

## 1. 任务来源

从蓝图 §15 "关键关联"、§16 "依赖图谱"、§17 "集成目标"、§18 "后果预测" 以及 "输出目录" 和 "需要更新的相关内容" 章节提取。

## 2. 关键关联清单（蓝图 §15）

| # | 关联对象 | 关系 | 路径 |
|---|---------|------|------|
| 1 | `metadata-registry.yaml` | MOD-INF-001 元数据注册 | `docs/01_policies_and_standards/meta/metadata-registry.yaml` |
| 2 | `task-system/blueprint.md` | 施工框架：G0-G5 门禁体系 + ContractBus 模式来源 | `docs/03_modules/l01_infrastructure/task-system/blueprint.md` |
| 3 | `context-engine/blueprint.md` | 上下文引擎为 Token Budget 提供基础设施 | `docs/03_modules/l01_infrastructure/context-engine/blueprint.md` |
| 4 | `llm-security/blueprint.md` | AI 审计守卫治理模型来源（合规审计、输入消毒、行为审计） | `docs/03_modules/l01_infrastructure/llm-security/blueprint.md` |
| 5 | `gate-engine/blueprint.md` | 阻断门门禁引擎——执行层预检 | `docs/03_modules/l01_infrastructure/gate-engine/blueprint.md` |
| 6 | `predict-router/blueprint.md` | 跨层容量联动的引航（批量执行、预算感知调度） | `docs/03_modules/l01_infrastructure/predict-router/blueprint.md` |
| 7 | `orchestrator/blueprint.md` | Agent 健康（SLO+三态）的监控目标 | `docs/03_modules/l01_infrastructure/orchestrator/blueprint.md` |
| 8 | SQLite best practices | DB schema、PRAGMA、TTL 清理等技术依据 | Supabase/Postgres best practices standard |
| 9 | `.trae/rules/project_rules.md` | Env + Agent 行为约束（R-001~R-008） | `.trae/rules/project_rules.md` |

## 3. 依赖图谱（蓝图 §16）

### 3.1 Correctness Dependencies（正确运行依赖）

| 依赖 | 具体对象 | 路径 |
|------|---------|------|
| SSoT Registry | Pydantic v2 models | `src/zephyr/shared/pydantic_v2_migrator.py` |
| Context & Doc Compressor | context docs | `src/zephyr/context_engine/doc_compressor.py` |
| Structured Logging | 结构化日志 | `src/zephyr/shared/zephyr_logger.py` |
| MCP Tool Rate Limiting | tool_contract.yaml | `src/zephyr/mcp/tool_contracts.yaml` |
| Config Auto-Reload Logic | ai_context_policy.yaml 构建规则 | `config/capacity/ai_context_policy.yaml` |

### 3.2 Execution Dependencies（执行依赖）

| 依赖 | 具体对象 | 路径 |
|------|---------|------|
| ChromaDB语义缓存 | Agent成本控制 | `src/zephyr/shared/semantic_cache.py` |
| Behavior Audit Logger | 合规审计文件 | `src/zephyr/llm_security/behavior_audit_logger.py` |
| Atomic Tx Manager (ATM) | SQLite Transaction | `src/zephyr/db/atomic_transaction_manager.py` |
| External Watchdog | 心跳服务器 | `src/zephyr/shared/heartbeat_server.py` |
| WinFS Defense | Windows FS segment | `src/zephyr/shared/winfs_defense.py` |

### 3.3 Distribution Dependencies（分布式依赖）

| 依赖 | 具体对象 |
|------|---------|
| Agent Health Monitor | 5-SLO Orchestrator |
| CBG Manager + L08 Circuit | gate-engine熔断 |
| Kill Switch Agent | 全局一键熔断 |
| Graceful-Shutdown Lifecycle | startup_guard/graceful_shutdown 协同 |
| Emergency Pool | Kill Switch启动预分配 |

## 4. 集成目标（蓝图 §17）

| # | 目标模块 | 集成方式 |
|---|---------|---------|
| 1 | **Agent RBAC** | 向 RBAC 系统注册容量保障的治理层角色（Observer/Operator/Admin），控制 hot-mode 升级权限 |
| 2 | **Budget Enforcer** | Token/Error Budget 指标注入 Budget Enforcer 的限流规则；Sandbox policy 成为 Budget Enforcer 的子策略 |
| 3 | **Rollback System** | Kill Switch 事件 + degradation chain 状态注册为 Rollback System 的回滚源；TASK-0010 risk_register.yaml 中所有 R1-R16 注册为回滚触发器 |
| 4 | **System Telemetry** | Capacity Metrics→L12 System Telemetry Pipeline；全部 OTel Metrics 输出到统一 Collector；Provenance Chain hash 审计日志注册 |

## 5. 输出目录

```
产出整体纳入以下结构：
├── src/zephyr/shared/                     # 核心共享模块
├── scripts/governance/d5_architecture/    # 蓝本 SSoT 一致性校验脚本
├── src/zephyr/llm_security/               # AI 审计守卫治理（+ 本蓝图补充拦截规则）
├── src/zephyr/orchestrator/               # Agent SLO 监控（≥ 5 项 SLO + 5 级 Error Budget Response）
├── src/zephyr/gates/                      # 阻断门门禁引擎（+ 本蓝图扩展）
├── src/zephyr/db/                         # SQLite Schema DDL + Provenance Store
├── src/zephyr/context_engine/             # 上下文引擎 + Context Doc Compressor
├── src/zephyr/mcp/                        # MCP Tools, contract 限制，Ray GCS / Metrics / API
├── config/                                # 各类运行时策略与政策
├── config/capacity/                       # 容量子配置（本蓝图专属）
└── D:\ZephyrAlpha\docs\                   # Compliance 文档（永久）
```

## 6. 需要更新的相关内容（蓝图 §[needs-update]）

### 6.1 metadata-registry.yaml

- MOD-INF-001 条目：`tag: ai-audit-guard, sli-registry` → `tag: capacity-assurance, governance-loop, kill-switch, sandbox-executor`
- 新增 `external_watchdog.yaml` 配置引用
- 更新 `legal: 无` → 依据本蓝图 §23.2 (Bus Factor=1) + §23.4 (Meta-SLO) + §23.5 (氛围编程反模式)

### 6.2 budget-enforcer/blueprint.md

- §R-?? "Capacity Constraints" 新增 ref 指向本蓝图 MOD-INF-001 §8 (Error Budget 五级响应) + §9 (Token Budget 四级体系)

## 7. 后果预测（蓝图 §18）

### 7.1 正面影响（3项 AGENTS.md §6.3 强制要求）

1. **current_blind_spots**: 本蓝图施工完成后 → 覆盖五轮盲点审计·全部67项盲点（当前仍有 §20-§24 的盲点未覆盖）
2. **architecture_fit**: 作为 L01 infrastructure + 内部治理层（internal governance layer），不会与L02 domain 模块冲突。唯一冲突点：`capacity_assurance → macro_analysis` 挂载点（参见 TASK-0012，虚拟挂载 → 宏分析器）与 `transformer` 目录规划可能竞争。
3. **edge_cases**: 1500模块+G5 门禁（Pre-Merge Gate）在模块数≥300 时，模拟时间 > 60s → 触发 Sampling Mode。以 `N` 采样率跳过轻度变更以保门禁速度（架构决策 DD-02。需要 Owner 审慎权衡）。

### 7.2 负面影响（3项 AGENTS.md §6.3 强制要求）

1. **施工反噬（Construction Backlash）**: 本蓝图附带的施工（如 SSoT validation, lazy_loader）可能存在 pydantic_v2 跨版本兼容性问题 → `Warm→Hot Block Gate` + `Regression Test` 拦截。后果为：施工运行 → 拦截 → 影响现有模块的依赖自动注入。
2. **Observability 复杂性（Complexity Cascading）**: CAP-009（Event Bus Backpressure）的引入可能引发并发容量分配的"冷冲突"
3. **MacGyver 式 Patch**: AI Agent 可能错误消除或过度消除已有的盲点闭合代码（发生在较低的 L3/L5 层级，因本蓝图原先未注册其 `.py` 归属）。后果：`circuit_breaker.py` gate-engine 模块可能被"意外修好"变为"从未存在过"的源文件，导致原始 L08 gate 失效。

### 7.3 简化后果速览（蓝图"后果（Consequences）"节）

**正面后果（3项）：**
1. **容量可量化** — 不再靠直觉估计，所有容量指标有明确数值和阈值
2. **自动化熔断** — 超预算自动保护，避免人工反应延迟导致级联故障
3. **全局统一预算模型** — 所有模块共享容量管理，消除资源分配不一致

**负面后果（3项）：**
1. **预算估算不准** — 初期依赖人为估计可能偏差，需持续校准（参见 §22 #60 ProgressiveCapacityCalibrator）
2. **熔断误触发风险** — 正常业务可能被 Kill Switch / Circuit Breaker 中断，需 Owner 确认
3. **多模块预算协调复杂** — P0 模块优先级冲突时需人工决策（参见 §21 #22 Owner决策疲劳）

## 8. 验收标准

1. 9 项关键关联在 metadata-registry.yaml 中引用正确
2. 三类依赖图谱（correctness/execution/distribution）映射完整
3. 4 个集成目标接口预先注入到位
4. 输出目录结构符合 directory-structure-standard.md
5. metadata-registry.yaml MOD-INF-001 条目已更新
6. budget-enforcer/blueprint.md ref 已补充
7. 正向 3 项 + 反向 3 项后果预测已记录