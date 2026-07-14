---
module_id: MOD-MASTER-002
title: "Baseline 蓝图 — 集成闭环总蓝图基线（§零~§三十七 12系统拓扑+63条CT-*契约）"
doc_type: blueprint
status: Active
version: "0.9.2"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
construction_progress: completed
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_baseline.md"
template_for: blueprint
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 1
functional_domain: infrastructure
summary: "MOD-MASTER_BLUEPRINT 基线蓝图 v0.9.2。12 系统拓扑 + 63 条 CT-* 集成契约 + 共享 Schema + 全局状态传播 + 容量预算 + 施工 Phase + Anti-Patterns + 设计决策 + 集成测试 + 风险 + 治理信息 + 端到端场景 + HealthCheck + CDC/DLQ + SLO/SLI + Bulkhead + 配置管理 + 数据生命周期 + 外部依赖 + 时间腐烂 + 生产成熟度 + 边界防护 + 性能基准 + 滚动升级 + Schema演化 + 降级级联 + 自治运行 + Agent质量 + Prompt版本 + Session冲突 + 死代码清理 + 蓝图健康 + 系统移交 + KE质量 + 深度审计盲点。"
tags: [master-blueprint, integration-contracts, closed-loop, ssoT, cross-system, health-check, cbac, cdc, contract-testing, can-i-deploy, dlq, benchmark, deploy, schema-migrate, degrade-cascade, autonomy, agent-quality, prompt-version, session-conflict, lean, blueprint-health, transfer, ke-quality]
priority: P0
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: "MOD-MASTER_BLUEPRINT"
rule_form: structural
scope: global
stability: stable
verifiability: automated
depends_on:
  - {target: "MOD-INF-005", at: "全篇", why: "脚本系统蓝图——本总蓝图定义脚本系统与任务系统/知识库的集成契约"}
  - {target: "MOD-TASK_SYSTEM", at: "全篇", why: "任务系统蓝图——本总蓝图定义任务系统与脚本系统/CE/FLE的集成契约"}
  - {target: "MOD-KB-001", at: "全篇", why: "知识库蓝图——本总蓝图定义知识库与CE/VMS/脚本系统的集成契约"}
  - {target: "architecture_model/layers/b_gates.yaml", at: "全篇", why: "Gates YAML SSoT——契约CT-GATE-*的真源"}
  - {target: "architecture_model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——契约CT-CE-*的真源"}
  - {target: "architecture_model/layers/b_pipeline.yaml", at: "全篇", why: "Pipeline YAML SSoT——契约CT-PIPE-*的真源"}
  - {target: "architecture_model/layers/b_feedback_loop.yaml", at: "全篇", why: "FLE YAML SSoT——契约CT-FLE-*的真源"}
  - {target: "architecture_model/layers/b_vector_memory.yaml", at: "全篇", why: "VMS YAML SSoT——契约CT-VMS-*的真源"}
  - {target: "architecture_model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——契约CT-DB-*的真源"}
  - {target: "architecture_model/layers/b_mcp.yaml", at: "全篇", why: "MCP YAML SSoT——契约CT-MCP-*的真源"}
  - {target: "architecture_model/layers/b_llm_security.yaml", at: "全篇", why: "LSG YAML SSoT——契约CT-LSG-*的真源"}
  - {target: "architecture_model/layers/system_telemetry.yaml", at: "全篇", why: "Telemetry YAML SSoT——契约CT-TELE-*的真源"}
  - {target: "architecture_model/layers/b_core.yaml", at: "全篇", why: "Core YAML SSoT"}
  - {target: "architecture_model/layers/b_shared.yaml", at: "全篇", why: "Shared YAML SSoT"}
  - {target: "architecture_model/layers/b_orchestrator.yaml", at: "全篇", why: "Orchestrator YAML SSoT——边界定义"}
  - {target: "PS-STD-001", at: "§7", why: "TaskCard 28字段模型——共享Schema真源"}
  - {target: "GOV-DOC-002", at: "§一~§二", why: "LPC双轨——B轨/C轨目录定位"}
references:
  - {path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_capacity.md", section: "全篇", why: "容量升级蓝图"}
  - {path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_agent_spec.md", section: "全篇", why: "Agent Spec蓝图"}
  - {path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md", section: "全篇", why: "蓝图模板v3.6"}
  - {path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml", section: "全篇", why: "压缩工作流标准"}
codification_level: L1
codification_at: "2026-05-15"
responsibility_domain: 
design_maturity: design
build_status: stable
---

# Baseline 蓝图 — 集成闭环总蓝图基线（§零~§三十七 12系统拓扑+63条CT-*契约）

> module_id: MOD-MASTER-002 | version: 0.9.2 | status: active | layer: cross_layer
> actual_disk_path: D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md | generation: 1 | construction_progress: completed

## 概述

本蓝图是 MOD-MASTER_BLUEPRINT 的基线设计文件——ZephyrAlpha 12 个基础设施系统的最完整集成蓝图。核心职责：12 系统拓扑全景、63 条 CT-* 跨系统集成契约（CT-GATE-*/CT-CE-*/CT-PIPE-*/CT-FLE-*/CT-VMS-*/CT-DB-*/CT-MCP-*/CT-LSG-*/CT-TELE-*）、共享 Schema 定义、全局状态传播协议、容量预算、施工 Phase、Anti-Patterns 与设计决策。覆盖端到端场景/HealthCheck/CDC+DLQ/SLO+SLI/Bulkhead/配置管理/数据生命周期/外部依赖/时间腐烂/生产成熟度/边界防护/性能基准/滚动升级/Schema演化/降级级联/自治运行/Agent质量/Prompt版本/Session冲突/死代码/蓝图健康/系统移交/KE质量/深度审计盲点等 24 个跨切面。上游被 SYS-MASTER-001 治理，下游被 Capactiy/Agent-Spec/Circuit Breaker 等蓝图消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）
> - 容量蓝图：[blueprint_capacity.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md)
> - Agent Spec蓝图：[blueprint_agent_spec.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md)

---

## 模板章节映射表

| 模板必需章节 | 本文件对应章节 | 状态 |
|------------|-------------|:---:|
| §0 代码对齐验证 | §零 分派表 + §六 产出物 | ✅ |
| §1 设计背景与目标 | §一 系统全景拓扑 | ✅ |
| §2 模块边界 | §一 系统拓扑 + §二 契约总表 | ✅ |
| §3 架构设计 | §一 系统全景拓扑 + §二 契约总表 | ✅ |
| §4 接口契约 | §二 契约总表（63条CT-*） | ✅ |
| §5 约束条件 | §四 架构原则 | ✅ |
| §6 错误处理 | §十六 FMEA | ✅ |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §8 安全考量 | §二十三 安全纵深防御 | ✅ |
| §9 测试策略 | §十七 测试策略 | ✅ |
| §10 依赖关系 | §五 依赖关系 | ✅ |
| §11 产出物 | §六 产出物存放目录 | ✅ |
| §12 集成目标 | §七 集成目标 | ✅ |
| §13 需要更新 | §八 需要更新的相关内容 | ✅ |
| §14 风险（含负面后果） | §九 已知风险与缓解 | ✅ |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |
| §16 施工指引 | §十一 施工指引 | ✅ |
| §17 容量升级 | 见容量蓝图 §-1/§-2 | 拆分覆盖 |
| §18 决策记录（含原§7备选项） | §三 关键架构决策索引 | ✅ |
| 治理信息 | 见文件末尾 | ✅ |

---

## 零之零、真源优先级宪章（Truth Source Precedence）

> **级别：P0 硬性约束。** 违反此优先级链的任何 AI agent 行为均构成架构违规（AP1）。

当多个文档源对同一事实给出不同定义时，按以下顺序裁决——**前一级别总是覆盖后一**：

| 优先级 | 文档源 | 裁决范围 | 说明 |
|:---:|------|------|------|
| **Tier 0** | 本蓝图（MOD-MASTER_BLUEPRINT） | 跨系统集成契约 | 所有 CT-* 契约的最终权威——inter-system 的"how to connect"以我为准 |
| **Tier 1** | `architecture_model/layers/{module}.yaml` | 单模块结构定义 | 模块边界、组件清单、依赖声明的原子真源——intra-module 的"what exists"以此为准 |
| **Tier 2** | `docs/03_modules/{layer}/blueprint.md` | 模块级实现指引 | 模块的"how to implement"由蓝图指引——但不得覆盖 Tier 0/1 的结构定义 |
| **Tier 3** | `docs/01_policies_and_standards/` | 通用规范与策略 | 编码规范、命名约定、流程定义——仅在没有 Tier 0-2 覆盖时适用 |
| **Tier 4** | 实际代码 | 运行时现实 | 代码是执行真相——但若代码与 Tier 0-3 矛盾，代码为 bug，需修复代码而非文档 |

**冲突裁决流程**：
1. AI agent 发现不一致 → 按此表确定权威源
2. 以权威源为准执行
3. 同时创建一个 `Finding（severity=LOW, type=DOC_INCONSISTENCY）` 记录不一致
4. 不得自行修改权威源来"修复"不一致

**反模式（禁止）**：
- ❌ "代码和蓝图不一致，我以代码为准"（除非代码是 Tier 4 且无 Tier 0-3 覆盖）
- ❌ "architecture_model 说 X，蓝图说 Y，我选我觉得合理的"
- ❌ "我发现不一致就顺便改了蓝图"（必须先创建 Finding）

---

## 零、AI Agent 分派与阅读指南

> 本蓝图 ~3500 行 —— 不读全文，按需定位。

### 0.1 Token 预算

| 阅读深度 | 读什么 | Token 消耗 | 适用场景 |
|:---:|------|:---:|------|
| 🔥 紧急 | `ai_role_instruction` + 拓扑图 + 合同总表 + 你系统的分派行 | ~500 | 新 AI session 冷启动 |
| 📋 标准 | 紧急 + 你负责系统的全部 CT-* 合同 | ~1500 | 开发跨系统功能 |
| 📚 完整 | 全文 | ~12000 | 架构审查 / 新系统接入 |

**新 AI session 默认从 🔥 紧急开始，按任务需求升级。**

### 0.2 AI Agent 分派表 —— 你该读蓝图的哪部分

| 如果你负责开发... | 你该读的 CT-* 合同 | 关联 Schema | 预计 tokens | actual_disk_path | 施工程度 |
|------------------|-------------------|------------|:---:|------|------|
| **Orchestrator** (任务系统) | CT-ORC-SCRIPT, CT-ORC-CE, CT-ORC-VMS, CT-ORC-GATE, CT-ORC-DB | TaskCard, Finding | ~1800 | `src/zephyr/orchestrator/` | 部分实现 |
| **Script System** (脚本系统) | CT-ORC-SCRIPT, CT-SCRIPT-KB, CT-SCRIPT-GATE, CT-FEATUREFLAG | Finding, KE | ~1400 | `src/zephyr/infra_ops/script_system/` + `scripts/governance/` | 部分实现 |
| **Knowledge Base** (知识库) | CT-SCRIPT-KB, CT-KB-VMS, CT-DATA-LIFECYCLE | KE | ~1000 | `src/zephyr/kb/` | 部分实现 |
| **Context Engine** (CE) | CT-ORC-CE, CT-CE-VMS, CT-CE-LSG, CT-BULKHEAD | TaskCard | ~1400 | `src/zephyr/context_engine/` | 部分实现 |
| **Gate Engine** (门控引擎) | CT-ORC-GATE, CT-SCRIPT-GATE, CT-FEATUREFLAG | TaskCard | ~900 | `src/zephyr/gov_enforcement/rule_enforcement/` | 部分实现 |
| **Feedback Loop** (FLE) | CT-FLE-ORC, CT-FLE-DB, CT-TELE-FLE, CT-WATCHDOG | — | ~1200 | `src/zephyr/feedback_loop/` | 部分实现 |
| **Pipeline** | CT-PIPE-ORC | TaskCard | ~400 | `src/zephyr/pipeline/` | 部分实现 |
| **Vector Memory** (VMS) | CT-ORC-VMS, CT-CE-VMS, CT-KB-VMS, CT-BULKHEAD | — | ~900 | `src/zephyr/vector_memory/` | 部分实现 |
| **Database** (db) | CT-FLE-DB, CT-ORC-DB, CT-DLQ, CT-BACKUP | — | ~700 | `src/zephyr/db/` | 部分实现 |
| **LLM Security** (LSG) | CT-CE-LSG, CT-SECRETS | — | ~500 | `src/zephyr/llm_security/` | 部分实现 |
| **System Telemetry** | CT-TELE-FLE, CT-WATCHDOG | — | ~400 | `src/zephyr/system_telemetry/` | 部分实现 |
| **MCP Servers** | CT-MCP-* | — | ~300 | `src/zephyr/integration/mcp/` | 部分实现 |
| **Agent RBAC** | G-CT-001~008 | — | ~800 | `src/zephyr/agent-rbac/` | 部分实现 |
| **Audit Trail** | G-CT-002 | — | ~400 | `src/zephyr/audit-trail/` | 部分实现 |
| **Rollback System** | G-CT-003, G-CT-005 | — | ~400 | `src/zephyr/rollback/` | 部分实现 |
| **Escalation Protocol** | G-CT-004, G-CT-006 | — | ~400 | `src/zephyr/infrastructure/escalation-engine/` | 部分实现 |
| **Budget Enforcer** | G-CT-006 | — | ~300 | `src/zephyr/budget-enforcer/` | 部分实现 |
| **A2A Protocol** | G-CT-008 | — | ~400 | `src/zephyr/infra_ops/a2a_protocol/` | 部分实现 |
| **Agent Spec** | G-CT-007 | — | ~300 | `src/zephyr/agent-spec/` | 部分实现 |
| **Auto Fix Engine** | — | — | ~200 | `src/zephyr/feedback_loop/auto_fix/` | 空壳 |
| **Drift Detector** | — | — | ~200 | `src/zephyr/behavioral-auditor/` | 部分实现 |
| **Code Dedup Engine** | — | — | ~200 | `src/zephyr/infra_ops/code_dedup_engine/` | 空壳 |
| **Capacity Assurance** | — | — | ~200 | `src/zephyr/capacity_assurance/` | 部分实现 |
| **Asset Inventory** | — | — | ~200 | `src/zephyr/asset-inventory/` | 部分实现 |
| **Shared Core** | — | — | ~300 | `src/zephyr/shared/` + `src/zephyr/core/` | 已实现 |
| **Auto Runtime Core** | — | — | ~300 | `src/zephyr/runtime/` | 部分实现 |
| 跨系统管控（横向） | CT-HEALTH, CT-CBAC, CT-CDC, CT-CONFIG, CT-FEATUREFLAG, CT-CHAOS, CT-RECONCILE, CT-STARTUP, CT-TEARDOWN, CT-MODEL-REGISTRY, CT-DEPS, CT-KNOWLEDGE-FRESHNESS, CT-HOUSEKEEPING, CT-SESSION-handoff, CT-STABILITY, CT-CANARY, CT-INCIDENT, CT-RACE-CONDITIONS, CT-COST-BUDGET, CT-DISK-GUARD, CT-NETWORK-PARTITION, CT-BENCH, CT-DEPLOY, CT-SCHEMA-MIGRATE, CT-DEGRADE-CASCADE, CT-AUTONOMY, CT-AGENT-QUALITY, CT-PROMPT-VERSION, CT-SESSION-CONFLICT, CT-LEAN, CT-BLUEPRINT-HEALTH, CT-TRANSFER, CT-KE-QUALITY | — | ~1600 | — | 设计中 |

---
---

## 一、系统全景：12 个系统的拓扑与职责边界

### 1.1 系统清单

| 系统 | 代码落位 | 模块蓝图 | 核心职责（一句话） |
|------|------|:---:|------|
| **Agent Orchestrator (Orc)** | `src/zephyr/orchestrator/` | MOD-TASK_SYSTEM 任务系统蓝图 | 任务生命周期管理 + Agent 调度 + 沙箱执行 |
| **Script System** | `src/zephyr/infra_ops/script_system/` + `scripts/governance/` | MOD-INF-005 脚本系统蓝图 | 12维度治理审计 + pre-commit门禁 + Finding管理 |
| **Knowledge Base (KB)** | `src/zephyr/kb/` | MOD-KB-001 知识库蓝图 | 知识全生命周期（G1→G5）+ KE管理 + ChromaDB |
| **Gate Engine (Gates)** | `src/zephyr/gov_enforcement/rule_enforcement/` | MOD-GATE_ENGINE gate_engine蓝图 | G0-G7任务门禁 + G1-G5 KMS门禁 + 准入判定 |
| **Context Engine (CE)** | `src/zephyr/context_engine/` | MOD-CONTEXT_ENGINE context_engine蓝图 | build→compress→validate→inject 四阶段上下文注入 |
| **Task Pipeline** | `src/zephyr/pipeline/` | MOD-INF-009 pipeline蓝图 | M1-M11双管线路由——决定任务用什么模型执行 |
| **Feedback Loop Engine (FLE)** | `src/zephyr/feedback_loop/` | MOD-FEEDBACK_LOOP feedback_loop蓝图 | 指标采集→异常检测→调度改进——自我改进闭环 |
| **Vector Memory Service (VMS)** | `src/zephyr/vector_memory/` | MOD-INF-011 vector_memory蓝图 | ChromaDB 8 Collection 统一向量持久化 |
| **Database (db)** | `src/zephyr/db/` | MOD-DATABASE database蓝图 | SQLite元数据 + ATM原子事务管理器 |
| **MCP Servers** | `src/zephyr/integration/mcp/` | MOD-INF-013 mcp_servers蓝图 | stdio协议——向外部IDE/Agent暴露系统能力 |
| **LLM Security Gateway (LSG)** | `src/zephyr/llm_security/` | MOD-LLM_SECURITY llm_security蓝图 | 四层安全防御——输入/输出/上下文/工具调用校验 |
| **System Telemetry (l12)** | `src/zephyr/system_telemetry/` | MOD-INF-015 telemetry蓝图 | metrics/logs/traces/ai_behavior 全系统可观测性 |

### 1.2 拓扑关系图

```
                          ┌──────────────────────────────────────┐
                          │        System Telemetry (l12)         │ ← 所有系统写入
                          └────────────────┬─────────────────────┘
                                           │ metrics / logs
                          ┌────────────────▼─────────────────────┐
                          │     Feedback Loop Engine (FLE)        │
                          │  collect → detect → dispatch          │
                          └───┬──────────────┬───────────────────┘
                              │ dispatch     │ dispatch
              ┌───────────────┼──────────────┼───────────────┐
              │               │              │               │
    ┌─────────▼──────┐  ┌─────▼──────┐  ┌───▼──────────┐  ┌─▼──────────────┐
    │  Orchestrator  │  │   Gates    │  │  Pipeline    │  │  Context Engine│
    │   (任务系统)    │  │ (门禁引擎)  │  │  (管线)      │  │    (CE)        │
    └───┬───┬───┬────┘  └─────┬──────┘  └──┬──┬──┬─────┘  └──┬──┬──┬───────┘
        │   │   │             │            │  │  │           │  │  │
        │   │   │    ┌────────┘            │  │  │  ┌────────┘  │  │
        │   │   │    │  ┌──────────────────┘  │  │  │  ┌────────┘  │
        │   │   │    │  │  ┌──────────────────┘  │  │  │  ┌────────┘
        ▼   ▼   ▼    ▼  ▼  ▼                    ▼  ▼  ▼  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │              Script System (脚本系统)                          │
  │   D1-D12 12维度 × C1-C5 五阶段                                  │
  └──────────────────────────┬────────────────────────────────────┘
                             │ MEDIUM Finding → KE
                    ┌────────▼────────┐
                    │  Knowledge Base │
                    │   (知识库)       │
                    └────────┬────────┘
                             │ vector search
                    ┌────────▼────────┐
                    │  Vector Memory  │
                    │     (VMS)       │
                    └────────┬────────┘
                             │ persistence
                    ┌────────▼────────┐
                    │    Database     │
                    │     (db)        │
                    └─────────────────┘

       ┌────────────────────────────────────────────┐
       │              MCP Servers                   │ ← 外部接口
       │  task_manager / knowledge_base / gate_engine│
       └────────────────────────────────────────────┘

       ┌────────────────────────────────────────────┐
       │        LLM Security Gateway (LSG)          │ ← 安全外衣
       │     Orc工具调用 / CE上下文注入 → LSG校验    │
       └────────────────────────────────────────────┘
```

---

## 二、集成契约登记表（Integration Contract Registry）

> 这是本蓝图的最核心章节。每条契约 YAML 结构化，AI 可直接消费——零推理。

### 2.1 契约总表

> **AI 必读**：`ai_read_only_hint` 是机器消费字段——不是给人看的。AI 读到契约时，
> 必须先检查此字段来确定该集成通路是否**真正可用**。`DO_NOT_CALL` = 不可调用该契约的
> client API（服务端不存在）；`IMPL_REQUIRED` = 需先完成实现才能调用；
> `CAUTION_STUB` = 存在骨架但只有部分功能；`SAFE` = 可正常调用。
>
> **严禁** AI 越过 `ai_read_only_hint` 直接根据"当前实现状态"列做推断。

| 契约编号 | 生产方 → 消费方 | 当前实现状态 | ai_read_only_hint |
|------|------|:---:|:---|
| CT-ORC-SCRIPT-001 | Orc ↔ Script System | 部分实现 | CAUTION_STUB |
| CT-ORC-CE-001 | Orc → CE | 骨架 | DO_NOT_CALL |
| CT-ORC-VMS-001 | Orc → VMS | 骨架 | DO_NOT_CALL |
| CT-ORC-GATE-001 | Orc → Gates | G0/G1/G7全生命周期已集成(create/transition/complete三级门禁) | SAFE |
| CT-ORC-DB | Orc → db | 18处import确认已实现 | SAFE |
| CT-SCRIPT-KB-001 | Script System → KB | 蓝图已定义 | IMPL_REQUIRED |
| CT-SCRIPT-GATE-001 | Script System → Gates | 部分实现 | CAUTION_STUB |
| CT-CE-VMS-001 | CE → VMS | 部分实现:VectorBridge已建桥接 | CAUTION_STUB |
| CT-CE-LSG-001 | CE → LSG | 规划 | DO_NOT_CALL |
| CT-KB-VMS-001 | KB → VMS | beta | CAUTION_STUB |
| CT-FLE-ORC-001 | FLE → Orc | decision_engine已创建(Orc→FLE已通,FLE→Orc待接通) | CAUTION_STUB |
| CT-FLE-DB-001 | FLE → db | metrics_collector已sqlite3持久化 | CAUTION_STUB |
| CT-TELE-FLE-001 | Telemetry → FLE | 规划 | DO_NOT_CALL |
| CT-PIPE-ORC-001 | Pipeline → Orc | task_queue直接import PipelineOrchestrator | SAFE |
| **CT-RBK-GATE-001** | **Rollback → Gate + Orc + Pipeline** | **GateEngine/Pipeline/Executor全链路已接通** | **CAUTION_STUB** |
| CT-HEALTH-001 | 全系统 | AggregateHealth已实现+gate_health仪表板 | CAUTION_STUB |
| CT-CBAC-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-CDC-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DLQ-001 | 全系统 | DeadLetterQueue已完整实现(438行) | CAUTION_STUB |
| CT-RECONCILE-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-STARTUP-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-TEARDOWN-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-SLO-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-BULKHEAD-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-WATCHDOG-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-BACKUP-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-CONFIG-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-FEATUREFLAG-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-SECRETS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-KISS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DATA-LIFECYCLE-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-CHAOS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-MODEL-REGISTRY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DEPS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-KNOWLEDGE-FRESHNESS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-HOUSEKEEPING-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-SESSION-handoff-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-STABILITY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-CANARY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-INCIDENT-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-RACE-CONDITIONS-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-COST-BUDGET-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DISK-GUARD-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-NETWORK-PARTITION-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-BENCH-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DEPLOY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-SCHEMA-MIGRATE-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DEGRADE-CASCADE-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-AUTONOMY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-AGENT-QUALITY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-PROMPT-VERSION-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-SESSION-CONFLICT-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-LEAN-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-BLUEPRINT-HEALTH-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-TRANSFER-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-KE-QUALITY-001 | 全系统 | 规划 | DO_NOT_CALL |
| CT-DB-001 | DB → 全系统 | YAML b_db.yaml 已声明 | CAUTION_STUB |
| CT-DB-002 | DB → 全系统 | YAML b_db.yaml 已声明 | CAUTION_STUB |
| CT-DB-003 | DB → 全系统 | YAML b_db.yaml 已声明 | CAUTION_STUB |
| CT-DB-004 | DB → 全系统 | YAML b_db.yaml 已声明 | CAUTION_STUB |
| CT-EXEC-TRAE-001 | ExecModel → Trae | YAML b_execution_model.yaml 已声明 | CAUTION_STUB |
| CT-EXEC-LOCAL-001 | ExecModel → Local | YAML b_execution_model.yaml 已声明 | CAUTION_STUB |
| CT-EXEC-API-001 | ExecModel → API | YAML b_execution_model.yaml 已声明 | CAUTION_STUB |

### 2.2 CT-ORC-SCRIPT-001：任务系统 ↔ 脚本系统

```yaml
contract: CT-ORC-SCRIPT-001
title: "任务阻塞 + Finding → 任务卡自动创建"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"

data_flow:
  direction: bidirectional
  script_to_orc:
    trigger: "脚本 exit 2 或 exit 3"
    payload: "FindingCollection { findings[], summary }"
    action: "Orc 将关联任务 status → BLOCKED"
    recovery: "脚本重跑 exit 0 → Orc 将关联任务 status → TODO"
  orc_to_script:
    trigger: "Finding.severity ∈ {CRITICAL, HIGH}"
    payload: "TaskCard { task_id, task_type: OPS, priority: P0/P1 }"
    action: "Script System 自动创建 OPS-{SEQ} 格式追踪任务卡"
    task_id_format: "OPS-{SEQ}"

state_propagation:
  - event: "script.exit_2"
    propagation:
      - target: "orchestrator.active_tasks"
        action: "status → BLOCKED"
        scope: "仅关联任务"
  - event: "script.exit_3"
    propagation:
      - target: "orchestrator.all_active_tasks"
        action: "status → BLOCKED"
        scope: "全部活跃任务（门禁自身故障 = 系统不可信）"
  - event: "finding.created{severity:CRITICAL|HIGH}"
    propagation:
      - target: "orchestrator.task_queue"
        action: "创建 OPS-{SEQ} 修复任务"
        task_fields:
          task_type: "OPS"
          priority: "P0 if CRITICAL else P1"
          parent_finding_id: "{finding.id}"

sla:
  CRITICAL_finding_response: "24h 内创建修复任务"
  HIGH_finding_response: "72h 内创建修复任务"
  gate_crash_recovery: "立即阻断所有活跃任务 + 通知 Owner"

ai_prompt: >
  你是CT-ORC-SCRIPT-001的AI agent。当脚本系统产出Findings时：
  (1) exit 2 → 仅阻断关联任务，不要阻断全局；
  (2) exit 3 → 这是门禁自身故障，必须阻断全部活跃任务+通知Owner——这是唯一触发全局阻断的场景；
  (3) CRITICAL/HIGH severity Finding → 自动创建OPS-{SEQ}任务卡，task_type=OPS，关联parent_finding_id；
  (4) MEDIUM Finding → 不创建任务卡，走CT-SCRIPT-KB-001入库流程；
  (5) 不要绕过CT-*直接import脚本系统内部模块（违反AP1）；
  (6) 任务BLOCKED后必须等待脚本重跑exit 0才能恢复→status: TODO，不要手动改状态。

telemetry:
  metrics:
    - {name: "script_exit_code", type: counter, labels: [exit_code, dimension]}
    - {name: "orc_blocked_tasks", type: gauge, labels: [trigger]}
    - {name: "finding_to_task_latency_s", type: histogram, buckets: [60,300,3600,86400]}
  traces:
    required_spans: ["script_execute", "finding_create", "orc_task_block", "orc_task_create"]
```

### 2.3 CT-ORC-CE-001：Orchestrator ↔ Context Engine

```yaml
contract: CT-ORC-CE-001
title: "任务启动时上下文构建请求"
systems:
  - role: consumer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-CONTEXT_ENGINE"
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"

interaction:
  trigger: "Orc.create_session(task_id)"
  sequence:
    step_1:
      actor: Orc
      action: "发送 session_context_request → CE"
      payload:
        task_id: "string"
        task_type: "enum[MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR]"
        target_layer: "string"
        related_files: "list[Path]"
    step_2:
      actor: CE
      action: "build: 从VMS拉取相关KE + 规则 + 蓝图"
      input: "session_context_request"
      output: "raw_context { ke_list[], rules[], blueprints[] }"
    step_3:
      actor: CE
      action: "compress: Token预算内压缩 → priority排序"
      input: "raw_context + token_budget"
      output: "compressed_context"
    step_4:
      actor: CE
      action: "validate: 通过LSG安全校验"
      input: "compressed_context"
      output: "validated_context or REJECTED"
    step_5:
      actor: CE
      action: "inject: 返回最终上下文给Orc"
      output: "injection_result { context_str, token_count, sources[] }"

token_budget:
  total_per_session: 8000
  breakdown:
    ke_entries: "0-3000 (动态)"
    rules_policies: "0-2000"
    blueprints: "0-2000"
    runtime_logs: "0-1000"

error_handling:
  VMS_unavailable: "CE → 降级为仅注入AGENTS.md + 当前模块蓝图 → 标记 session.degraded=true"
  LSG_reject: "CE → 移除被拒绝块 → 重新compress → 再送LSG → 3次仍失败 → 注入失败标记"
  timeout: "CE 10s 超时 → 降级注入 → 记录CE_timeout metric"

ai_prompt: >
  你是CT-ORC-CE-001的AI agent。当Orc请求为任务构建上下文时：
  (1) build阶段从VMS拉取KE+规则+蓝图——如果VMS不可用，降级为仅注入AGENTS.md+硬编码规则，不要抛异常；
  (2) compress阶段必须在8000 token预算内完成，优先级：KE > 规则 > 蓝图 > 日志；
  (3) compress后必须保留raw_text——LSG需要它做注入检测（AP4）；
  (4) validate阶段必须通过LSG——LSG不可用时fail-closed（AP5），不要尝试跳过；
  (5) 10s超时立即降级，不要阻塞Orc的任务启动；
  (6) 返回的injection_result必须包含source_files字段——明确告诉Orc"上下文来自哪里"。

telemetry:
  metrics:
    - {name: "ce_context_build_duration_ms", type: histogram, buckets: [100,500,1000,5000,10000]}
    - {name: "ce_context_token_count", type: gauge}
    - {name: "ce_context_build_errors", type: counter, labels: [error_type]}
    - {name: "ce_degradation_rate", type: rate}
  traces:
    required_spans: ["ce_build", "ce_vector_search", "ce_compress", "ce_lsg_validate", "ce_inject"]
```

### 2.4 CT-SCRIPT-KB-001：脚本系统 ↔ 知识库

```yaml
contract: CT-SCRIPT-KB-001
title: "脚本 Finding → 知识条目入库"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: knowledge_base
    path: "src/zephyr/kb/"
    blueprint: "MOD-KB-001"

data_flow:
  direction: "script → KB"
  mapping:
    - finding_severity: "MEDIUM"
      action: "自动创建 KE 草稿 → G1 Ingest → G2 Triage"
      ke_template: |
        title: "{finding.dimension}: {finding.message[:80]}"
        domain: "governance"
        tags: ["auto-generated", "{finding.dimension}", "finding-to-ke"]
        source_finding_id: "{finding.id}"
    - finding_severity: "CRITICAL|HIGH"
      action: "不自动创建KE——CRITICAL/HIGH 走任务卡流程（CT-ORC-SCRIPT-001）"
    - finding_severity: "LOW|INFO"
      action: "不入KB——仅记录到审计日志"
    - phase_C5_knowledge: |
        脚本系统 C5 知识沉淀阶段:
        CRITICAL/HIGH Finding 修复完成 → 提取经验教训 → G3 Analyze →
        人工确认后 → G4 Activate → KE 进入活跃知识库

quality_gate:
  - auto_generated_KE 必须经过 G2 Triage 人工确认 → 不得自动 G4 Activate
  - KE 来源字段标注 `source: "script_system_C4"`

ai_prompt: >
  你是CT-SCRIPT-KB-001的AI agent。当脚本系统产出MEDIUM severity Finding时：
  (1) 自动创建KE草稿，status=DRAFT，不要直接G4 Activate——必须经过G2 Triage人工确认；
  (2) KE的source字段必须标注"script_system_C4"——用于审计追溯；
  (3) CRITICAL/HIGH Finding不在此处理——走CT-ORC-SCRIPT-001创建OPS任务卡；
  (4) LOW/INFO Finding不入KB——仅记录审计日志，不要浪费KB存储；
  (5) C5阶段的知识沉淀（修复完成的CRITICAL/HIGH）需要人工确认后走G3→G4路径，不要全自动激活。

telemetry:
  metrics:
    - {name: "finding_to_ke_auto_create", type: counter, labels: [severity, dimension]}
    - {name: "ke_auto_create_latency_s", type: histogram, buckets: [1,5,10,30]}
    - {name: "c5_knowledge_extract_count", type: counter}
  traces:
    required_spans: ["finding_emit", "ke_draft_create", "ke_g1_ingest"]
```

### 2.5 CT-FLE-ORC-001：FLE ↔ Orchestrator

```yaml
contract: CT-FLE-ORC-001
title: "异常检测 → 任务调度调整 + 告警"
systems:
  - role: producer
    name: feedback_loop
    path: "src/zephyr/feedback_loop/"
    blueprint: "MOD-FEEDBACK_LOOP"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"

interaction:
  trigger_1: "FLE.collect_metric → 周期性轮询（30s）"
  trigger_2: "FLE.detect_anomaly → 指标偏离基线 > 阈值"
  trigger_3: "FLE.dispatch_action → 生成改进指令"

action_types:
  ESCALATE:
    condition: "任务失败率 3x > 基线"
    action: "FLE → Orc.raise_alert → GPT-5.2 发送 Owner 飞书通知"
    severity: "P0_immediate"
  REPAIR:
    condition: "特定维度脚本持续 exit 2"
    action: "FLE → Orc.create_task(OPS-{SEQ}, task_type=AUTO_FIX)"
    severity: "P1_24h"
  NOTIFY_OWNER:
    condition: "幻觉检测 D12 exit 2 连续3次"
    action: "FLE → Orc.flag_for_owner_review → 暂停该维度Agent调度"
    severity: "P0_immediate"
  ADJUST_GATE:
    condition: "门禁假阳性率 > 5%（连续一周）"
    action: "FLE → Orc.adjust_gate_threshold(gate_id, new_threshold)"
    severity: "P2_72h"
    constraint: "阈值调整必须人工确认——FLE建议，Owner裁决"

data_models:
  ActionDispatch:
    action_id: "FLE-ACTION-{SEQ}"
    action_type: "enum[ESCALATE, REPAIR, NOTIFY_OWNER, ADJUST_GATE]"
    target_system: "orchestrator"
    payload: "dict (action_type对应的参数)"
    priority: "enum[P0_immediate, P1_24h, P2_72h]"
    created_at: "ISO8601"

  FeedbackReceipt:
    receipt_id: "string"
    status: "enum[ACKNOWLEDGED, REJECTED, EXECUTING, COMPLETED]"
    orchestrator_note: "string (可选——Orc的附加说明)"

retry_policy:
  max_retries: 3
  retry_interval: "5s"
  fallback: "写入 db.emergency_log + 通知 GPT-5.2 发送告警"

ai_prompt: >
  你是CT-FLE-ORC-001的AI agent。当FLE检测到异常时：
  (1) ESCALATE仅当失败率3x基线时触发——不要因单次抖动就告警；
  (2) ADJUST_GATE的阈值调整必须人工确认——FLE只能建议，不能自动执行；
  (3) 不要在没有异常检测结果时执行THROTTLE/ROLLBACK（AP3）；
  (4) ROLLBACK必须携带FLE.detect_anomaly()==true的前置条件；
  (5) retry 3次仍失败后写入emergency_log，然后发飞书通知——不要静默吞掉异常。

telemetry:
  metrics:
    - {name: "fle_anomaly_detected", type: counter, labels: [anomaly_type]}
    - {name: "fle_action_dispatched", type: counter, labels: [action_type, severity]}
    - {name: "fle_detect_dispatch_latency_s", type: histogram, buckets: [1,5,10,30,60]}
    - {name: "fle_false_positive_rate", type: gauge}
  traces:
    required_spans: ["fle_collect", "fle_detect", "fle_dispatch"]
```

### 2.6 CT-CE-VMS-001：CE ↔ VMS

```yaml
contract: CT-CE-VMS-001
title: "上下文构建 → 向量检索"
systems:
  - role: consumer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-CONTEXT_ENGINE"
  - role: provider
    name: vector_memory
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

interaction:
  query:
    method: "VMS.search(collection, query_embedding, top_k, filter)"
    collections:
      - name: "ke_entries"
        query: "task_type + target_layer → 语义相似KE"
        top_k: 5
      - name: "vibe_rules"
        query: "task_type → 相关治理规则"
        top_k: 3
      - name: "blueprints"
        query: "target_layer + related_files → 相关蓝图"
        top_k: 2
      - name: "failure_patterns"
        query: "task_type → 历史失败模式"
        top_k: 3

embedding:
  model: "BGE-M3 (ONNX本地推理)"
  dimension: 1024
  batch_size: 16

error_handling:
  VMS_unavailable: "CE降级——不注入向量检索结果 → AGENTS.md + 硬编码规则"
  embedding_failure: "CE跳过该collection → 记录 warning"

ai_prompt: >
  你是CT-CE-VMS-001的AI agent。当CE需要从VMS检索知识向量时：
  (1) 查询4个collection：ke_entries(top_k=5)、vibe_rules(top_k=3)、blueprints(top_k=2)、failure_patterns(top_k=3)；
  (2) query_embedding使用BGE-M3 1024d——不要混用其他模型；
  (3) VMS不可用时降级为仅注入AGENTS.md+硬编码规则——不要阻塞CE的build流程；
  (4) embedding_failure时跳过该collection但继续其他collection的检索——部分结果优于零结果；
  (5) 返回结果必须附带similarity_score——CE compress阶段用于优先级排序。

telemetry:
  metrics:
    - {name: "vms_search_latency_ms", type: histogram, buckets: [10,50,100,500,1000]}
    - {name: "vms_search_result_count", type: gauge, labels: [collection]}
    - {name: "vms_availability", type: rate}
  traces:
    required_spans: ["vms_search_ke", "vms_search_rules", "vms_search_blueprints", "vms_search_failures"]
```

### 2.7 CT-PIPE-ORC-001：Pipeline ↔ Orchestrator

```yaml
contract: CT-PIPE-ORC-001
title: "任务 → 管线节点路由"
systems:
  - role: router
    name: pipeline
    path: "src/zephyr/pipeline/"
    blueprint: "MOD-INF-009"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"

routing:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id: M1-M11, execution_model, sandbox_profile, gate_profile }"

  decision_tree: |
    if task_type == MODEL_BUILD:
      if estimated_complexity == HIGH → M1 (Opus 4.5, full sandbox)
      else → M2 (GPT-5.2, standard sandbox)
    if task_type == AUDIT:
      if priority == P0 → M3 (Opus 4.5 复审, audit sandbox)
      else → M4 (Claude 4.5 Sonnet, audit sandbox)
    if task_type ∈ {DOC_WRITE, REFACTOR}:
      if target_layer ∈ {D_MKT_DATA,D_INFRA_OPS,D_GOV_ENFORCEMENT} → M5 (GPT-5.2, full sandbox)
      else → M6 (Claude 4.5 Sonnet, standard sandbox)

pipeline_output:
  node_id: "M1-M11"
  execution_model: "enum[opus-4.5, gpt-5.2, claude-4.5-sonnet, claude-4.5-haiku, gemini-3.0-pro, qwen-3-max, glm-5.1]"
  sandbox_profile: "enum[full, standard, audit, restricted]"
  gate_profile: "enum[full_g0_g7, pre_commit_only, post_exec_only, none]"

ai_prompt: >
  你是CT-PIPE-ORC-001的AI agent。当你需要为TaskCard选择管线路由时：
  (1) 输入TaskCard的task_type+priority+target_layer+estimated_complexity→输出M1-M11节点；
  (2) MODEL_BUILD+高复杂度→M1(Opus 4.5)，AUDIT→M3/M4，OPS→M2——严格按照decision_tree路由；
  (3) 路由输出必须包含完整的PipelineNode：node_id + execution_model + sandbox_profile + gate_profile；
  (4) A-zone(M1-M5)产出物不得直接流入B-zone(M6-M11)——必须经过M6边界标记（AP2）；
  (5) 不要因为"某模型当前不可用"而私自改变路由——模型不可用应触发FLE而非静默改路由。

telemetry:
  metrics:
    - {name: "pipe_routing_decision_count", type: counter, labels: [task_type, node_id]}
    - {name: "pipe_routing_latency_ms", type: histogram, buckets: [1,5,10,50]}
    - {name: "pipe_zone_crossing_count", type: counter, labels: [from_zone, to_zone]}
  traces:
    required_spans: ["pipe_receive_taskcard", "pipe_route_decision", "pipe_emit_node"]
```

### 2.8 CT-SCRIPT-GATE-001：脚本系统 ↔ Gates

```yaml
contract: CT-SCRIPT-GATE-001
title: "脚本exit code → Gate判定"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gov_enforcement/rule_enforcement/"
    blueprint: "MOD-GATE_ENGINE"

mapping:
  script_exit_0: "GATE-n → PASS → 任务状态不变"
  script_exit_1: "GATE-n → PASS_WITH_WARNINGS → 任务状态 ⚠️ WARNING"
  script_exit_2: "GATE-n → FAIL → 关联任务 BLOCKED → FLE记录"
  script_exit_3: "GATE-n → CRITICAL_FAIL → 全部活跃任务 BLOCKED + Owner通知"

gate_trigger:
  - GATE-18 (pre-commit): "每次 git commit → run_all.py quick scan → exit ≤ 1 才放行"
  - G0-G7 (任务门禁): "任务执行前后 → 对应维度脚本判定"

ai_prompt: >
  你是CT-SCRIPT-GATE-001的AI agent。当脚本系统输出exit code时：
  (1) exit 0 → PASS——不阻塞任何流程；
  (2) exit 1 → PASS_WITH_WARNINGS——任务继续但标记⚠️；
  (3) exit 2 → FAIL——关联任务BLOCKED，但不要阻断全局；
  (4) exit 3 → CRITICAL_FAIL——这是门禁自身崩溃的信号：全局阻断+Owner通知，无例外；
  (5) GATE-18 pre-commit是唯一不可绕过的硬门禁——`--no-verify`应急通道必须记录Session Log；
  (6) exit code映射是单向的：不要因为"修复中"而把exit 3降级为exit 2。

telemetry:
  metrics:
    - {name: "script_gate_exit_code", type: counter, labels: [exit_code, gate_id, dimension]}
    - {name: "script_gate_pass_rate", type: gauge, labels: [gate_id]}
    - {name: "pre_commit_block_count", type: counter}
  traces:
    required_spans: ["script_execute", "gate_evaluate", "gate_respond"]
```

### 2.9 CT-ORC-VMS-001：任务系统 → 向量记忆 — 任务输出写入向量库

```yaml
contract: CT-ORC-VMS-001
title: "任务产出写入向量记忆——持久化检索入口"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: producer_to_consumer
  trigger: "TaskCard.status → COMPLETED 且 output_type ∈ {CODE, DOCUMENT, ANALYSIS}"
  payload:
    task_id: "string — TaskCard.task_id"
    output_summary: "string — 任务产出的250字摘要"
    output_blocks: "list[OutputBlock] — 按segment分块的原始产出"
    embedding_hint: "enum[DENSE, SPARSE, HYBRID] — 建议的向量化策略"
    tags: "list[str] — 从TaskCard.tags继承"
  action: "VMS写入向量库 → 更新 TaskCard.vector_refs 字段"

quality_control:
  max_blocks_per_task: 50
  min_block_length: 100
  dedup_strategy: "content_hash → 已有hash则skip"
  retry_on_failure: 3

circuit_breaker:
  failure_threshold: 10
  recovery_after_seconds: 120
  fallback: "写入本地SQLite队列 → VMS恢复后批量回放"

ai_prompt: >
  你是CT-ORC-VMS-001的AI agent。当Orc的任务产出(CODE/DOCUMENT/ANALYSIS)需要持久化到向量库时：
  (1) 仅当TaskCard.status=COMPLETED且output_type∈{CODE,DOCUMENT,ANALYSIS}时触发写入；
  (2) 每个任务最多写入50个output block，每个block最短100字符——避免碎片化；
  (3) content_hash去重——相同hash的block不重复写入；
  (4) 熔断触发(failure≥10)后，fallback写入本地SQLite队列→不要丢失任务产出；
  (5) VMS恢复后自动回放SQLite队列——回放完成后更新TaskCard.vector_refs字段；
  (6) retry 3次后仍失败→标记TaskCard.vector_refs="write_deferred"，不阻塞任务完成。

telemetry:
  metrics:
    - {name: "orc_vms_write_count", type: counter, labels: [output_type]}
    - {name: "orc_vms_write_latency_ms", type: histogram, buckets: [10,50,100,500,1000]}
    - {name: "orc_vms_dedup_hit_rate", type: gauge}
    - {name: "orc_vms_circuit_open", type: gauge}
  traces:
    required_spans: ["orc_complete_task", "vms_write_vector", "vms_update_taskcard"]
```

### 2.10 CT-ORC-GATE-001：任务系统 → 门控引擎 — 任务执行前后门禁判定

```yaml
contract: CT-ORC-GATE-001
title: "任务生命周期的G0-G7门禁判定"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gov_enforcement/rule_enforcement/"
    blueprint: "MOD-GATE_ENGINE"

data_flow:
  direction: bidirectional
  orc_to_gate:
    trigger: "TaskCard 状态迁移到 PENDING → 进入 G0 判定"
    payload: "TaskCard 完整28字段"
    gating_sequence:
      - gate: G0
        at: "任务进入 TODO 前"
        checks: ["priority_valid", "assignee_exists", "deadline_future"]
        on_fail: "回退到 DRAFT"
      - gate: G1
        at: "任务进入 IN_PROGRESS 前"
        checks: ["context_built", "dependencies_met"]
        on_fail: "BLOCKED + 等待依赖"
      - gate: G7
        at: "任务标记 COMPLETED 前"
        checks: ["all_findings_resolved", "output_validated"]
        on_fail: "REVIEW_REQUIRED + FLE记录"
  gate_to_orc:
    response: "PASS | FAIL | PASS_WITH_WARNINGS | CRITICAL_FAIL"
    response_detail: "{ gate_id, violations[], suggestions[] }"
    action: "Orc 根据 response 更新 TaskCard.status"

design_rationale: >
  G0-G7不是全局门（区别于GATE-18 pre-commit），而是任务粒度门。
  每个TaskCard在其生命周期中依次通过G0→G1→...→G7，
  任何一个FAIL都会阻断任务流转，直到violation被消除。

ai_prompt: >
  你是CT-ORC-GATE-001的AI agent。当TaskCard状态迁移需要门禁判定时：
  (1) G0(进入TODO前)→校验priority_valid+assignee_exists+deadline_future→FAIL退回DRAFT；
  (2) G1(进入IN_PROGRESS前)→校验context_built+dependencies_met→FAIL进入BLOCKED等待依赖；
  (3) G7(标记COMPLETED前)→校验all_findings_resolved+output_validated→FAIL进入REVIEW_REQUIRED；
  (4) status迁移必须遵循DRAFT→TODO→IN_PROGRESS→REVIEW→COMPLETED，不允许跳步（AP6）；
  (5) 返回的response必须包含violations[]+suggestions[]——不要只返回PASS/FAIL而不给原因；
  (6) 不要为"加速流程"而手动修改response绕过门禁。

telemetry:
  metrics:
    - {name: "task_gate_pass_count", type: counter, labels: [gate_id, response]}
    - {name: "task_gate_violation_count", type: counter, labels: [gate_id, violation_type]}
    - {name: "task_gate_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "task_status_transition_invalid", type: counter}
  traces:
    required_spans: ["gate_g0_check", "gate_g1_check", "gate_g7_check"]
```

### 2.11 CT-CE-LSG-001：上下文引擎 → LLM安全 — 上下文注入前安全校验

```yaml
contract: CT-CE-LSG-001
title: "LLM调用前的上下文安全审查——fail-closed边界"
systems:
  - role: producer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-CONTEXT_ENGINE"
  - role: consumer
    name: llm_security_gate
    path: "src/zephyr/llm_security/"
    blueprint: "MOD-LLM_SECURITY"

data_flow:
  direction: producer_to_consumer
  trigger: "CE准备将构建好的context注入LLM调用——注入前必经LSG审查"
  payload:
    context_id: "string"
    target_model: "string — gpt-4o / claude-sonnet-4 / etc."
    full_prompt_text: "string — 即将发送给LLM的完整文本"
    source_files: "list[str] — context中引用的源文件路径"
    user_intent: "enum[CODE_GEN, CODE_REVIEW, ANALYSIS, QUERY]"
  action: "LSG逐层审查 → PASS则放行 / FAIL则阻断LLM调用 + 记录audit_log"

security_layers:
  - layer: input_sanitizer
    checks: ["prompt_injection_patterns", "code_execution_attempts", "credential_leak_patterns"]
    on_fail: "BLOCK → 拒绝此次LLM调用"
  - layer: process_sandbox
    checks: ["output_size_limit", "file_system_access_scope"]
    on_fail: "SANDBOX → 限制LLM输出范围"
  - layer: behavior_audit
    checks: ["anomaly_detection", "rate_limiting", "usage_pattern_deviation"]
    on_fail: "LOG + ALERT → 不阻断但告警"

fail_closed: >
  LSG不可用（进程crash/超时）→ 拒绝所有LLM流量（fail-closed原则）。
  不存在"跳过安全检查"的降级路径。

ai_prompt: >
  你是CT-CE-LSG-001的AI agent。当CE准备将上下文注入LLM时：
  (1) 三层审查必须全部执行：input_sanitizer→process_sandbox→behavior_audit；
  (2) input_sanitizer检测到prompt injection→BLOCK，拒绝此次调用，不要降级为WARNING；
  (3) process_sandbox校验output_size_limit+file_system_access_scope→FAIL则SANDBOX限制输出范围；
  (4) behavior_audit检测异常→LOG+ALERT，不阻断但必须告警；
  (5) LSG不可用时fail-closed——拒绝所有LLM流量，不存在"跳过安全检查"的降级路径（AP5）；
  (6) 不要因为"性能考虑"而跳过任意层——安全>性能。

telemetry:
  metrics:
    - {name: "lsg_block_count", type: counter, labels: [layer, reason]}
    - {name: "lsg_pass_rate", type: gauge, labels: [layer]}
    - {name: "lsg_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "lsg_false_positive_rate", type: gauge}
  traces:
    required_spans: ["lsg_sanitizer", "lsg_sandbox", "lsg_audit"]
```

### 2.12 CT-KB-VMS-001：知识库 → 向量记忆 — 知识条目向量化存储

```yaml
contract: CT-KB-VMS-001
title: "结构化知识→非结构化向量记忆的双向映射"
systems:
  - role: producer
    name: knowledge_base
    path: "src/zephyr/knowledge_base/"
    blueprint: "MOD-KB-001"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: bidirectional

  kb_to_vms:
    trigger: "KE.status → ACTIVE 且 ke_type ∈ {ARCHITECTURE_RULE, CODE_CONVENTION, DECISION_RECORD}"
    payload:
      ke_id: "string"
      ke_title: "string"
      ke_content_plaintext: "string — 去Markdown格式化的纯文本"
      ke_type: "string"
      priority: "P0..P3"
      embedding_model: "text-embedding-3-large"
    action: "VMS生成embedding → 存储为 vector_entry → 返回 vector_id"

  vms_to_kb:
    trigger: "CE查询向量记忆 → 检索到KE相关向量"
    query: "{ vector_id, similarity_score, source_ke_id }"
    action: "KB根据 ke_id 返回KE完整内容 → CE注入上下文"

consistency_rule: >
  KE更新时 → KB通知VMS重新生成embedding（而非覆写旧向量）。
  旧向量标记为 superseded_by={new_vector_id}，保留用于审计追溯。

ai_prompt: >
  你是CT-KB-VMS-001的AI agent。当KB需要将KE向量化存储到VMS时：
  (1) 仅当KE.status=ACTIVE且ke_type∈{ARCHITECTURE_RULE,CODE_CONVENTION,DECISION_RECORD}时触发向量化；
  (2) embedding使用text-embedding-3-large——不要用BGE-M3（那是VMS查询用的）；
  (3) KE更新时生成新embedding + 旧向量标记superseded_by——不要覆写旧向量（DD6）；
  (4) KE被DEPRECATED/ARCHIVED时，VMS中对应向量标记deprecated=true但保留——用于审计追溯；
  (5) VMS→KB方向：CE查询到向量后，KB根据ke_id返回完整KE内容——不要只返回vector_id。

telemetry:
  metrics:
    - {name: "kb_vms_embed_count", type: counter, labels: [ke_type]}
    - {name: "kb_vms_embed_latency_ms", type: histogram, buckets: [50,100,500,1000,5000]}
    - {name: "kb_vms_superseded_count", type: counter}
    - {name: "kb_vms_consistency_check_pass", type: gauge}
  traces:
    required_spans: ["kb_ke_activate", "vms_generate_embedding", "vms_store_vector"]
```

### 2.13 CT-FLE-DB-001：反馈环路 → 数据库 — 评估指标时序持久化

```yaml
contract: CT-FLE-DB-001
title: "FLE评估结果→数据库时序存储——为趋势分析和回滚决策提供数据基础"
systems:
  - role: producer
    name: feedback_loop_engine
    path: "src/zephyr/feedback_loop/"
    blueprint: "MOD-FEEDBACK_LOOP"
  - role: consumer
    name: database
    path: "src/zephyr/database/"
    blueprint: "MOD-DATABASE"

data_flow:
  direction: producer_to_consumer
  trigger: "FLE完成一轮 collect→detect 循环后——无论是否有异常"
  payload:
    cycle_id: "string"
    cycle_timestamp: "ISO8601"
    metrics:
      task_throughput: "float — 任务/小时"
      gate_pass_rate: "float — G0-G7通过率 (%)"
      script_failure_rate: "float — 脚本exit≠0比率 (%)"
      ce_latency_p50: "float — CE构建延迟P50 (ms)"
      llm_token_usage: "int — 本周期LLM token消耗"
    anomalies:
      detected: "bool"
      anomaly_type: "enum[PERFORMANCE_DEGRADATION, QUALITY_REGRESSION, SECURITY_ALERT] | null"
      affected_systems: "list[str]"
    action_taken: "enum[NONE, THROTTLE, ROLLBACK, ALERT]"
  action: "db写入 fle_metrics 时序表 → 保留90天 → 90天后归档到 cold_storage"

circuit_breaker:
  db_write_failure: "写入本地SQLite buffer → db恢复后批量重放"
  max_buffer_size_mb: 100

design_rationale: >
  时序数据是FLE趋势分析和自动回滚决策的基础。
  即使当前周期无异常，也必须写入——"无异常"本身就是一个需要记录的信号。

ai_prompt: >
  你是CT-FLE-DB-001的AI agent。当FLE需要持久化/查询数据时：
  (1) telemetry_event表主写路径——FLE自身指标+系统告警事件→幂等写入（natural_key去重）；
  (2) anomaly_record表——每次ESCLATE时的诊断快照`snap_{timestamp}`，诊断结束后自动清理；
  (3) audit_log表不可变追加（DD11）——不要UPDATE或DELETE已有审计记录；
  (4) emergency_log表——retry 3次仍失败后的fallback，写入后告警，恢复后自动回放；
  (5) 查询用read_replica（如配置），写入用primary——不要反向；
  (6) 熔断打开时写入本地SQLite buffer→不要因为DB不可用就丢失数据；
  (7) max_buffer_size_mb=100——超过上限按FIFO丢弃最旧数据并告警。

telemetry:
  metrics:
    - {name: "fle_db_write_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "fle_db_read_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "fle_db_fallback_buffer_usage", type: gauge}
  traces:
    required_spans: ["fle_write_metrics", "fle_read_metrics", "fle_write_audit"]
```

---

## 三、共享 Schema（多系统共用的数据结构 SSoT）

> 以下 Schema 被多个系统消费——总蓝图是它们的 canonical SSoT。
> 模块蓝图引用这些 Schema 时不重复定义——只引用总蓝图的 Schema ID。

### 3.1 TaskCard（Orc、Pipeline、Gates、FLE、Script System 共用）

```yaml
schema: SCHEMA-TASKCARD-001
canonical_source: "PS-STD-001 §7.10 + src/zephyr/shared/schemas.py Task"
schema_version: "1.2.0"
version_negotiation:
  ref: "CTR-VER-001（cross_layer_contracts.yaml §versioning_strategy）"
  rules:
    - "v1.x.y 消费者MUST忽略未知可选字段（forward-compat）"
    - "v1→v2 MAJOR变更需Owner审批+30天通知+双版本过渡期"
    - "新增字段默认optional=True，不得删除或修改已有字段类型"
    - "废弃字段标记@deprecated+target_removal_version，保留至少2个MAJOR版本"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: task_id
    type: str
    format: "{NAMESPACE}-{SEQ}"
    examples: ["MODEL-042", "AUDIT-017", "OPS-003", "KB-INF-0001"]
    namespaces:
      MODEL: "模型构建任务"
      AUDIT: "审计类任务"
      OPS: "运维/修复任务（脚本系统自动创建）"
      KB-INF: "知识库基础设施任务"
  - name: status
    type: enum
    values: [DRAFT, QUEUED, ASSIGNED, RUNNING, REVIEWING, COMPLETED, BLOCKED, CANCELLED, FAILED, ARCHIVED]
    transitions:
      BLOCKED_triggers: [GATE_FAIL, SCRIPT_EXIT_2, SCRIPT_EXIT_3, FLE_ESCALATE]
      BLOCKED_recovery: [GATE_PASS, SCRIPT_EXIT_0, OWNER_UNBLOCK]
  - name: task_type
    type: enum
    values: [MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR, AUTO_FIX, INFRA]
  - name: priority
    type: enum
    values: [P0, P1, P2, P3]
  - name: execution_model
    type: str
    source: "Pipeline routing output"
  - name: gate_profile
    type: str
    source: "Pipeline routing output"
```

### 3.2 Finding（Script System、Orchestrator、Gates、KB 共用）

```yaml
schema: SCHEMA-FINDING-001
canonical_source: "MOD-INF-005 §4.3 + src/zephyr/infrastructure/runtime_integration/script_system/finding.py"
schema_version: "1.0.0"
version_negotiation:
  ref: "CTR-VER-001（cross_layer_contracts.yaml §versioning_strategy）"
  rules:
    - "同MAJOR版本前后兼容；新增optional字段不影响消费者"
    - "废弃字段标记@deprecated，保留至少2个MAJOR版本后移除"
    - "MAJOR变更需Owner审批+30天通知所有签约方"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: finding_id
    type: str
    format: "FND-{DIMENSION}-{SEQ}"
  - name: severity
    type: enum
    values: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
    routing:
      CRITICAL: "→ GATE FAIL + Orc BLOCK + OPS任务卡 + Owner通知"
      HIGH: "→ GATE FAIL + Orc BLOCK + OPS任务卡"
      MEDIUM: "→ GATE WARN + KB入库(G1→G2 Triage)"
      LOW: "→ GATE WARN + 审计日志"
      INFO: "→ 审计日志"
  - name: dimension
    type: enum
    values: [D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12]
  - name: recommendation
    type: str
    description: "修复建议——人类可读"
  - name: recommendation_type
    type: enum
    values: [auto_fixable, manual_only, needs_review]
```

### 3.3 KE（KB、CE、VMS、Script System 共用）

```yaml
schema: SCHEMA-KE-001
canonical_source: "MOD-KB-001 §3.2"
schema_version: "1.0.0"
version_negotiation:
  ref: "CTR-VER-001（cross_layer_contracts.yaml §versioning_strategy）"
  rules:
    - "同MAJOR版本前后兼容；新增optional字段不影响消费者"
    - "废弃字段标记@deprecated，保留至少2个MAJOR版本后移除"
    - "MAJOR变更需Owner审批+30天通知所有签约方"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: ke_id
    type: str
    format: "KE-{NNN}"
  - name: status
    type: enum
    values: [DRAFT, INGESTED, TRIAGED, ANALYZED, ACTIVATED, EXTRACTED, DEPRECATED, ARCHIVED, CONFLICT, DUPLICATE]
  - name: kb_gate
    type: enum
    values: [G1, G2, G3, G4, G5]
    description: "当前KE所处的KMS门禁阶段"
  - name: source
    type: enum
    values: [manual, script_system_C4, FLE_dispatch, session_log, adr]
  - name: embedding_status
    type: enum
    values: [not_embedded, embedding, embedded, failed]
```

---

## 四、全局状态传播链

### 4.1 完整传播图谱

```
[事件 1] 脚本 exit 2 (D6 安全漏洞)
    ↓
    Gate G0-G7 → FAIL (CT-SCRIPT-GATE-001)
    ↓
    ┌──────────────────────────────┐
    │  关联任务 → status: BLOCKED  │ ← CT-ORC-SCRIPT-001
    │  Orc 写入 db.task_repo      │ ← CT-ORC-DB
    └──────────────────────────────┘
    ↓ (并行)
    ┌──────────────────────────────┐
    │  FLE.detect_anomaly         │ ← CT-TELE-FLE-001
    │  "D6 持续阻断 > 3次"        │
    └──────────────────────────────┘
    ↓
    ┌──────────────────────────────┐
    │  FLE.dispatch_action        │ ← CT-FLE-ORC-001
    │  action: ESCALATE           │
    └──────────────────────────────┘
    ↓
    GPT-5.2 → Owner 飞书通知
    ↓
    Owner: "手动修复 D6 漏洞"
    ↓
    脚本重跑 → exit 0
    ↓
    Gate → PASS
    ↓
    Orc: 解除 BLOCKED → status: TODO
    ↓
    CE: 构建新session上下文（注入本次修复的KE）
```

### 4.2 故障传播与熔断约定

| 故障 | 影响范围 | 传播方式 | 熔断机制 |
|------|:---:|------|------|
| VMS 不可用 | CE、KB | CE降级→仅注入硬编码规则；KB标记degraded | 自动重试3次→通知Owner→不阻断其他系统 |
| db SQLite 锁竞争 | Orc、FLE | ATM排队→写入延迟 | 超时3s→WAL模式自动回退→不丢数据 |
| pre-commit D1 exit 3 | 全部提交 | **硬阻断**——git commit 不允许 | 立即通知Owner + `--no-verify`应急通道（需Session Log记录） |
| LSG 误杀率 > 10% | CE、Orc | 上下文注入缺失块 | 自动降级→标记+记录→人工调整LSG阈值 |
| ChromaDB 崩溃 | VMS、CE | CE降级→无向量检索 | 重启ChromaDB→CE自动恢复完整上下文注入 |

---

## 五、全局容量预算

| 资源 | 各系统独立上限 | 全局硬上限 | 超限策略 |
|------|:---:|:---:|------|
| 全系统 12 维度扫描耗时 | — | **600s (10min)** | 超时维度标记 skip |
| pre-commit 钩子数 | 10/系统 | **15** | 分组并行执行 |
| SQLite db 文件大小 | — | **140TB (SQLite上限)** | 当前 <10MB——远未触达 |
| VMS ChromaDB 单 Collection | — | **1M vectors** | BGE-M3 1024d → ~4GB/1M |
| CE Session Token | — | **8000 tokens/session** | 超限→compress阶段优先级截断 |
| FLE metric 采样频率 | — | **30s** | 峰值期降至 60s |
| 单次 session 蓝图注入数 | — | **5 blueprints** | 按 target_layer 相关性排序 |

---

## 六、施工 Phase 规划

### 蓝图补齐（当前 session）

| 任务 | 优先级 |
|------|:---:|
| 总蓝图（本文档）创建 | **P0** |
| Gates / CE / Pipeline / FLE 四个 P0 蓝图创建 | **P0** |
| module_registry.yaml 更新 | **P0** |
| §零 Agent分派表 + §七 Anti-Patterns + §十四 HealthCheck 首次写入 | **P0** |

### 接口契约落地

| 任务 | 优先级 |
|------|:---:|
| 54条CT-* 契约编码完成 | **P0** |
| 各系统实现 compliance 标记（`@satisfies_contract("CT-ID")`）| **P0** |
| validate_integration_consistency.py 启用 | **P0** |

### Phase 0 — 基础设施管控契约优先（新增）

| 任务 | 优先级 |
|------|:---:|
| `CT-HEALTH-001` — 三态探针端点 `/healthz/livez/readyz` 实现 | **P0** |
| `CT-STARTUP-001` — 冷启动顺序与依赖就绪机制 | **P0** |
| `CT-CBAC-001` — capability_check() 防篡改checksum机制 | **P0** |
| `CT-BACKUP-001` — 每日自动备份sqlite+chromadb | **P1** |
| `CT-CONFIG-001` — 配置统一管理与校验 | **P1** |
| `CT-DLQ-001` — 死信队列sqlite表+replay触发 | **P1** |

### Phase A — 4个高优先级契约

| 任务 | 优先级 |
|------|:---:|
| CT-ORC-SCRIPT-001 | **P0** |
| CT-ORC-CE-001 | **P0** |
| CT-ORC-GATE-001 | **P0** |
| CT-SCRIPT-GATE-001 | **P0** |
| LSG / Telemetry 蓝图创建 | P2 |

---
## 七、Anti-Patterns —— AI agent 绝对禁止的集成行为

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **绕过集成契约直接调用**——子系统A不经过CT-*契约直接import子系统B的内部模块 | 契约SSoT失效 → CI校验无意义 → 重构时全盘崩溃 | 任何跨系统调用必须通过CT-*契约定义的接口 |
| AP2 | **M1-M5产出物直接进入B-zone**——Pipeline A-zone(生产)产出的artifact未经审核直接流入B-zone(审计) | 生产数据污染审计数据 → 审计结论失真 | A-zone产出物必须经过M6边界明确标记后才能进入B-zone |
| AP3 | **无异常检测触发回滚**——FLE未检测到异常就执行THROTTLE/ROLLBACK | 正常系统被误杀 → 假阳性导致任务堆积 | ROLLBACK仅当FLE.detect_anomaly()返回true时触发 |
| AP4 | **CE compress阶段丢弃raw_text**——上下文引擎压缩时删除原始文本只保留向量 | 下游LLM安全审查失败（需要raw_text做注入检测）| compress永远保留raw_text字段——LSG消费raw_text |
| AP5 | **熔断降级时跳过安全校验**——circuit_breaker触发后跳过LSG检查以恢复性能 | 攻击者利用熔断窗口注入恶意prompt | LSG不可降级——fail-closed优先于availability |
| AP6 | **任务卡片跨status跳跃**——TaskCard.status从DRAFT直接跳到COMPLETED | 绕过G0-G7全部门禁 → 门控引擎形同虚设 | status迁移必须遵循 DRAFT→TODO→IN_PROGRESS→REVIEW→COMPLETED |
| AP7 | **共享Schema字段私自扩展**——子模块为方便在SCHEMA-*上追加字段但不更新本蓝图 | 多系统消费同一Schema但字段不一致 → 反序列化失败 | SCHEMA-*变更必须本蓝图审批后广播所有消费系统 |
| AP8 | **模拟对方系统的"假成功"响应**——测试时用mock返回CT-*契约里未定义的响应格式 | 测试通过但集成时break | mock必须定义在CT-*契约的`mock_strategy`字段内 |

---

## 八、施工指南 —— AI agent 编码入口

> **为什么需要这一章**：蓝图定义了14个系统间核心CT-*契约 + 40个基础设施管控CT-*契约 + 3个SCHEMA-* + 4条全局链，
> 但AI agent拿到这份蓝图后需要知道——**从哪个文件开始、按什么顺序、依赖什么先行**。
> 本章是100% AI开发场景下的冷启动施工地图。

### 8.1 施工前置条件检查

| 检查项 | 状态 | 说明 |
|-------|:---:|------|
| 3个Shared Schema已在代码中实现 | ❌ | TaskCard / Finding / KE 三个数据类需要先定义 |
| depends_on中的16个蓝图层文件已存在 | ✅ | architecture_model/layers/*.yaml全部存在 |
| Python 3.11+ 环境就绪 | ✅ | 项目已有环境 |
| module_registry.yaml已注册本蓝图 | ✅ | MOD-MASTER_BLUEPRINT已注册 |

### 8.2 施工顺序（无依赖→有依赖→循环依赖）

```
Phase A: 无依赖先行（可并行）
├── A1: Shared Schema 实现
│   ├── src/zephyr/shared/schemas/task_card.py   ← TaskCard 28字段dataclass
│   ├── src/zephyr/infrastructure/runtime_integration/script_system/finding.py     ← Finding 5字段dataclass
│   └── src/zephyr/shared/schemas/ke.py          ← KE dataclass
│
├── A2: CT-ORC-GATE-001   ← 只依赖TaskCard + Gates层YAML
│   └── src/zephyr/gov_enforcement/rule_enforcement/task_gates.py
│
├── A3: CT-CE-LSG-001     ← 只依赖CE层YAML + LSG层YAML
│   └── src/zephyr/security/llm_defense/llm_security/ce_lsg_bridge.py
│
└── A4: CT-KB-VMS-001     ← 只依赖KB + VMS层YAML
    └── src/zephyr/data/knowledge_management/vector_memory/kb_vms_bridge.py

Phase B: 单向依赖（A完成后→B启动）
├── B1: CT-ORC-CE-001     ← 依赖 TaskCard + CE层YAML
├── B2: CT-ORC-VMS-001    ← 依赖 TaskCard + VMS层YAML
├── B3: CT-SCRIPT-GATE-001 ← 依赖Gate层YAML + Script层
└── B4: CT-FLE-DB-001     ← 依赖FLE层YAML + DB层YAML

Phase C: 双向依赖（需要双方都就绪）
├── C1: CT-ORC-SCRIPT-001 ← Orc ↔ Script System ← 需要双方都开发
│   → 策略：先实现 Orc→Script方向，Script侧用stub；再反转
│
└── C2: CT-FLE-ORC-001    ← FLE → Orc ← 需要异常检测(Phase A)完成
    → 策略：先实现const→FLE推送路径，Orc侧动作暂用log代替

Phase D: 全链路集成
├── D1: CT-PIPE-ORC-001   ← Pipeline M1-M11 + Orc → 最后实现
├── D2: CT-TELE-FLE-001   ← Telemetry → FLE ← 全系统就绪后
└── D3: CT-CE-VMS-001     ← CE → VMS ← 双方就绪后
```

### 8.3 每个CT-*契约的mock策略

当AI agent只实现契约的一方时，需要用mock模拟对方。以下mock策略均在契约的`mock_strategy`字段内约定：

| CT-* | mock策略 |
|------|---------|
| CT-ORC-SCRIPT-001 | `python -c "import sys; sys.exit(0)"` 模拟脚本exit 0 |
| CT-ORC-CE-001 | 返回 `{"context": "MOCK_CONTEXT", "source_files": []}` |
| CT-ORC-VMS-001 | SQLite内存模式 `:memory:` 模拟向量存储 |
| CT-ORC-GATE-001 | 返回 `{"response": "PASS", "detail": {"gate_id": "G0", "violations": []}}` |
| CT-CE-VMS-001 | FAISS内存索引 `faiss.IndexFlatL2(768)` 模拟 |
| CT-CE-LSG-001 | 返回 `{"allowed": true, "audit_id": "mock-audit-001"}` |
| CT-KB-VMS-001 | `numpy.random.rand(3072)` 模拟embedding |
| CT-FLE-ORC-001 | 返回 `{"action": "NONE", "reason": "no anomaly detected"}` |
| CT-FLE-DB-001 | SQLite `:memory:` 模拟时序存储 |
| CT-PIPE-ORC-001 | 返回 `{"node": "M1", "status": "ready"}` |
| CT-TELE-FLE-001 | 空dict `{}` 模拟指标推送 |

---

## 九、设计决策集中表

> 当前10条关键架构决策散落在各个CT-*合约的`design_rationale`字段中。
> 本章提供集中视图——便于新session AI快速理解"为什么这么设计"。

| ID | 决策 | 理由 | 替代方案（被否决） | 重新评估条件 |
|----|------|------|------------------|------------|
| DD1 | **总蓝图只定义"之间"，不管"内部"** | 防止总蓝图过厚→编修成本指数增长 | "一个文件定义一切"的Monolithic方案 | 当模块数>50时重新评估 |
| DD2 | **YAML结构化契约而非Markdown自然语言** | AI可直接解析→CI可自动验证 | "用RFC风格的Markdown文档描述每个契约" | YAML解析在项目中成为瓶颈时 |
| DD3 | **fail-closed优先于availability** | 安全>可用——绕过安全检查的LLM调用不可逆 | "熔断时跳过安全校验"——被否决 | 当误阻断率达5%+时重新评估 |
| DD4 | **circuit_breaker在每条CT-*独立配置** | 不同系统对的故障容忍度不同——一刀切=过度熔断或延误响应 | "全局唯一的熔断策略" | —无— |
| DD5 | **FLE写入无异常也需记录** | "无异常"是趋势分析的关键信号——缺失=分析盲区 | "仅异常时写入"——被否决（丢失baseline）| 存储成本成为主要约束时 |
| DD6 | **KE更新→新embedding而非覆写** | 旧向量保留用于审计追溯——"这个KE曾经指向什么"需要回答 | "直接覆写旧embedding"——简化但丢失审计 | 向量库存储达到容量上限 |
| DD7 | **故障传播方向：内→外（局部先隔离）** | 确保局部故障不影响全局→最小爆炸半径 | "外→内"——全局熔断影响未出问题的系统 | —无— |
| DD8 | **M1-M11双zone不可交叉污染** | A-zone生产指标和B-zone审计指标混合→审计结论不可信 | "单pipeline同时承担生产和审计"——被否决 | —无— |
| DD9 | **三态HealthCheck而非五态** | 简化：liveness/readiness/degraded 三态覆盖90%场景——五态(healthy/degraded/impaired/critical/unknown)带来额外维护负担 | K8s五态模型 | 系统规模>20时重新评估 |
| DD10 | **DLQ用SQLite而非Kafka** | 1人维护模式下，SQLite零运维——引入Kafka需要单独运维集群 | Kafka/RabbitMQ等外部消息队列 | 日均DLQ消息>10000时重新评估 |
| DD11 | **CDC用本地SQLite简化版PactBroker** | 完整Pact需要Node/Java运行时+docker——1人维护模式下维护成本过高 | Pact Broker / Spring Cloud Contract | 消费者数>3时重新评估 |
| DD12 | **Telemetry metrics自推送到FLE而非FLE主动pull** | push模式降低FLE的协调成本——12系统各自负责自己的指标上报 | "FLE主动按interval pull每系统"——增加FLE的故障半径 | —无— |
| DD9 | **stub/mock必须在契约文件内定义** | AI agent测试时自己编mock→与真实契约偏离→集成时break | "mock由实现方自由定义"——被否决 | —无— |
| DD10 | **契约编号CT-{A}-{B}固定——新增=追加、废弃=标记但不删除** | 铁律四：蓝图永久保留←废弃契约仍然影响历史session回溯 | "删除废弃CT-*编号"——被否决 | —无— |

---

## 十、集成测试契约

> 每个CT-*契约附带测试断言——确定性验证集成是否正确。

### 10.1 通用集成测试模板

```python
# 集成闭环总蓝图（基线）— v0.9.2 现存设计（§零~§三十七）
import pytest

class TestIntegrationContract:
    """每个CT-*契约的通用验证模板"""

    CONTRACT_ID: str  # 子类覆写

    def test_producer_side_exists(self):
        """生产方实现文件存在"""
        ...

    def test_consumer_side_exists(self):
        """消费方实现文件存在"""
        ...

    def test_contract_payload_schema_matches(self):
        """payload字段与契约YAML声明一致"""
        ...

    def test_circuit_breaker_fires_on_threshold(self):
        """熔断在failure_threshold触发"""
        ...

    def test_circuit_breaker_recovers_after_timeout(self):
        """熔断在recovery_after_seconds恢复"""
        ...
```

### 10.2 每个CT-*的专属测试断言

| CT-* | 关键测试断言 | 预期结果 |
|------|------------|---------|
| CT-ORC-SCRIPT-001 | script exit 2 → BLOCKED ; exit 0 → 恢复TODO | status迁移正确 |
| CT-ORC-CE-001 | CE返回context包含source_files字段 | source_files非空 |
| CT-ORC-VMS-001 | 写入vector后TaskCard.vector_refs非空 | refs写入成功 |
| CT-ORC-GATE-001 | G0: priority=invalid→FAIL ; G7: all_findings_resolved=false→REQUIRED_REVIEW | 门判定正确 |
| CT-SCRIPT-KB-001 | Finding.severity=MEDIUM → KE入库成功 | KE新增 |
| CT-SCRIPT-GATE-001 | exit 0→PASS ; exit 3→CRITICAL_FAIL→全任务BLOCKED | exit code映射正确 |
| CT-CE-VMS-001 | 查询"代码约定"→返回相似度>0.7的向量 | 检索准确 |
| CT-CE-LSG-001 | prompt包含`__import__('os').system('rm')`→BLOCK | 注入拦截 |
| CT-KB-VMS-001 | KE→embedding→写入→ke_id→返回vector_id | 双向映射正确 |
| CT-FLE-ORC-001 | anomaly_type=PERFORMANCE_DEGRADATION→ORC THROTTLE | 调度调整生效 |
| CT-FLE-DB-001 | 写入fle_metrics→读取→一致 | 持久化正确 |
| CT-TELE-FLE-001 | Telemetry推送后FLE能读取最新metrics | 推送链路通畅 |
| CT-PIPE-ORC-001 | task_type=ops→路由到M2 ; task_type→不匹配→返回error | 路由正确 |
| CT-HEALTH-001 | GET /_health/orchestrator/readyz → 200 ; LSG crash → /readyz → 503 | 探针正确 |
| CT-CBAC-001 | 非授权caller→调用→DENY ; 授权caller→调用→PASS | 权限矩阵生效 |
| CT-CDC-001 | consumer expectation→CI生成→broker存储→provider CI verify | ALL VERIFIED |
| CT-DLQ-001 | VMS不可用时写入dlq→VMS恢复后自动回放→payload无损 | 故障恢复完整 |
| CT-RECONCILE-001 | 调和循环检测ACTIVE KE缺失embedding→自动触发向量化 | 自动修复 |
| CT-STARTUP-001 | 按layer_0→1→2→3→4顺序启动→全部readyz=200 | 启动成功 |
| CT-TEARDOWN-001 | TaskCard CANCELLED→12系统资源全部释放→audit_log记录 | 清理完整 |

### 10.3 CI门禁集成测试触发条件

| GATE | 触发条件 | 覆盖的CT-* |
|:---:|---------|----------|
| GATE-IT-1 | 每次 push / PR | CT-ORC-*, CT-SCRIPT-*, CT-FLE-* |
| GATE-IT-2 | Phase D 全链路完成后每日跑 | 全部54个CT-* |
| GATE-IT-3 | LSG相关代码变更时触发 | CT-CE-LSG-001 |
| GATE-IT-SMOKE | pre-commit快速冒烟 | CT-ORC-SCRIPT-001, CT-SCRIPT-GATE-001 |
| GATE-IT-HEALTH | 启动/重启后 | CT-HEALTH-001, CT-STARTUP-001 |
| GATE-IT-SEC | Capability/RBAC变更时 | CT-CBAC-001 |

---
---
## 十一、风险与后果

### 11.1 核心风险

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | **契约漂移**——模块蓝图引用总蓝图契约但实现不一致 | 中 | 高 | CI门禁 → 自动交叉校验契约 vs 实现 |
| R2 | **总蓝图过厚**——试图定义每个模块的内部细节 | 高 | 中 | 严格边界：总蓝图只管"之间"，不管"内部" |
| R3 | **单点故障**——总蓝图是20条CT-*的契约SSoT，破损=集成混乱 | 低 | **极高** | 总蓝图 YAML 契约应可由 CI 自动验证 |
| R4 | **CBAC checksum被篡改**——运行时capability_matrix被修改→未授权系统获得特权 | 低 | **极高** | checksum校验+audit_log不可变 + 启动时一致性检查 |
| R5 | **HealthCheck探针假阳性**——探针误报degraded=true→触发不必要的降级 | 中 | 中 | 连续3次degraded才触发降级 + 恢复连续2次healthy才clear |
| R6 | **CDC broker损坏**——所有Can-I-Deploy被卡→全系统无法部署 | 低 | **极高** | broker定期备份 + 损坏时允许`--emergency-deploy`手动确认 |
| R7 | **DLQ积压爆炸**——dlq_depth>10000→暂停入队→丢失故障期数据 | 低 | 高 | 48h告警阈值 + 手动清淤流程 + 72h自动归档 |

### 11.2 正面后果

- **AI冷启动加速**：新 session AI 读完本蓝图 → 一次了解全部集成关系 → 不需从 12 个模块蓝图交叉拼图
- **契约可验证**：每条 CT-* 契约 YAML 结构化 → CI 可直接校验生产方/消费方的接口实现一致性
- **故障传播可视化**：§4 状态传播链 → 一个系统故障 → 一眼看出"哪些系统受影响"

---

## 十二、治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 系统间集成契约（CT-*核心14条）| **本蓝图 §2** |
| 共享 Schema（SCHEMA-*）| **本蓝图 §3** |
| 全局状态传播链 | **本蓝图 §4** |
| 标准化 HealthCheck 三态探针协议 | **本蓝图 §十四** |
| CBAC 能力访问控制矩阵 | **本蓝图 §十五** |
| CDC 消费者驱动契约测试 + Can-I-Deploy + DLQ | **本蓝图 §十六** |
| SLO/SLI 服务等级目标 + Error Budget | **本蓝图 §十七** |
| Bulkhead 隔舱 + Watchdog 监视 + Backup 备份 | **本蓝图 §十八** |
| Config 配置 + FeatureFlag 开关 + Secrets 密钥 + KISS AI约束 | **本蓝图 §十九** |
| Data Lifecycle + MultiEnv + Chaos + Codegen + BreakingChange + ModelRegistry + Deps + KnowledgeFreshness + Housekeeping + SessionHandoff + Stability + Canary + Incident + RaceConditions + CostBudget + DiskGuard + NetworkPartition | **本蓝图 §二十~§二十四** |
| Performance Benchmark + Deploy + SchemaMigration + DegradeCascade + Autonomy + AgentQuality + PromptVersion + SessionConflict + Lean + BlueprintHealth + Transfer + KEQuality | **本蓝图 §二十五~§三十六** |
| 各系统内部架构 | **各模块蓝图** |

**冲突裁决**：模块蓝图的集成描述与本蓝图不一致 → 按以下裁决程序处理。

### 冲突裁决程序

当以下任何情况发生时，触发集成冲突裁决：

| # | 触发条件 | 检测方式 |
|---|---------|---------|
| 1 | 子蓝图引用的 CT-* 合同编号在 MASTER-001 中不存在 | CI 扫描 |
| 2 | 子蓝图声明的合同 payload 字段与 MASTER-001 CT-* YAML 不一致 | CI 扫描 |
| 3 | 两个子蓝图对同一 CT-* 合同有互斥的理解 | CI 扫描 |
| 4 | architecture_model/layers/*.yaml 的 `interfaces` 与 MASTER-001 CT-* 声明不一致 | CI 扫描 |

**裁决优先级（从高到低）**：

| 优先级 | 来源 | 说明 |
|:---:|------|------|
| **1** | **MASTER-001 的 CT-* YAML**（本蓝图 §二） | canonical SSoT——最高权威 |
| 2 | `architecture_model/layers/*.yaml` | 架构模型层——子蓝图引用的 YAML 真源 |
| 3 | 各子模块蓝图 | 本地理解——有冲突时以上方为准 |

**CI 检测机制**：

```
validate_integration_consistency.py（待创建）
→ 扫描所有子蓝图的 CT-* 引用
→ 交叉校验 MASTER-001 §二 的合同定义
→ 不一致 = CI FAIL（硬阻断，P0）
→ 冲突日志输出到 .audit_cache/integration_conflicts.json
```

**冲突修复流程**：

```
1. CI 检测到冲突 → 输出冲突详情
2. AI agent 读取冲突详情 → 判断哪一方需要修改
3. 修改子蓝图（对齐 MASTER-001）或修改 MASTER-001（如果合同定义本身需要升级）
4. 重新提交 → CI 重新扫描 → 通过
5. 修复记录写入 变更记录
```

---

## 十三、端到端场景走查

> 以下是一个完整场景——演示 13 个 CT-* 合同在真实任务中如何协同工作。

### 场景：Owner 发现治理脚本漏检 — AI 修复全流程

```
第 1 步：任务创建
  Owner → Orc: 创建 TaskCard
    task_type = OPS
    priority = P1
    description = "run_all.py 的 D12 维度漏检 .yaml 文件编码"
  Orc 内部:
    G0 Task Entry Gate 判定 → task_id 格式 OK, priority OK → PASS
    TaskCard.status: DRAFT → TODO

  → 涉及: CT-ORC-GATE-001 (G0 门禁)

第 2 步：上下文构建
  Orc → CE: CT-ORC-CE-001
    请求构建上下文——需要 run_all.py 源码 + D12 维度规则 + TaskCard 描述
  CE 内部:
    build 阶段: 收集 run_all.py + b_docs.yaml + TaskCard 28 字段
    → CE → VMS: CT-CE-VMS-001
      查询 "治理脚本 YAML 编码检测" → 返回 3 条历史 bug 修复记录
    compress 阶段: 压缩到 4000 tokens（保留 raw_text）
    validate 阶段: CE → LSG via CT-CE-LSG-001
      LSG: input_sanitizer → 无注入 → PASS
      LSG: process_sandbox → PASS
      LSG: behavior_audit → PASS
    inject 阶段: 将 context 注入 LLM 调用

  → 涉及: CT-ORC-CE-001, CT-CE-VMS-001, CT-CE-LSG-001

第 3 步：管线路由
  任务进入 Pipeline → CT-PIPE-ORC-001
    task_type = OPS → 路由到 M2 (OPS/修复) 节点
    模型选择: Claude Sonnet 4（能力矩阵中 OPS 类型的最佳模型）

  → 涉及: CT-PIPE-ORC-001

第 4 步：AI 生成修复
  AI Agent 在 M2 节点执行:
    读取 run_all.py → 发现 D12 维度的 glob 模式未包含 *.yaml
    修改: glob 模式追加 "**/*.yaml"
    沙箱检查: G4 Sandbox Gate → sandbox_profile 匹配 OPS → PASS
    工具调用检查: G6 Security Gate → 所有 tool_call 在白名单 → PASS

  → 涉及: CT-ORC-GATE-001 (G4, G6)

第 5 步：治理脚本判定
  Script System → 执行 run_all.py
    exit code = 0（所有维度 PASS）
    → CT-SCRIPT-GATE-001: exit 0 → GATE-n PASS

  → 涉及: CT-SCRIPT-GATE-001

第 6 步：知识入库（如果本次修复产生了新知识）
  Script System 产生 Finding(severity=MEDIUM, type=BUG_FIX)
    → CT-SCRIPT-KB-001: MEDIUM Finding → KE 入库
  KB 处理:
    KE 进入 KMS 管道 → G1 Ingest → G2 Triage → G3 Evaluate
    KE.status = ACTIVE
    → CT-KB-VMS-001: KB → VMS 生成 embedding

  → 涉及: CT-SCRIPT-KB-001, CT-KB-VMS-001

第 7 步：交付前门禁
  任务进入 REVIEW 状态 → Orc 触发 G7 Delivery Gate
    G7-C00: run_all.py exit 0 → PASS
    TaskCard.status: REVIEW → COMPLETED

  → 涉及: CT-ORC-GATE-001 (G7)

第 8 步：反馈闭环
  FLE 采集本轮数据:
    → CT-TELE-FLE-001: 读取 Telemetry 的 task_throughput, gate_pass_rate
    → FLE.detect_anomaly(): 无异常（所有指标正常）
    → CT-FLE-DB-001: 写入 fle_metrics 时序表（"无异常"本身也记录）
    → CT-FLE-ORC-001: 反馈给 Orc——本次 OPS 任务正常，无需调整调度

  → 涉及: CT-TELE-FLE-001, CT-FLE-DB-001, CT-FLE-ORC-001

全流程涉及的 CT-* 合同: 11/14
  未涉及: CT-ORC-VMS-001（本次无COMPLETED任务产出需要向量化）
          CT-ORC-SCRIPT-001（本次无CRITICAL/HIGH Finding触发自动创建OPS任务卡）
          CT-ORC-DB（任务状态持久化由Orc内部处理——无需显式展示）
```

---
---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 总蓝图不产生代码，仅定义集成契约

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

---

## 十四、标准化 HealthCheck 三态探针协议

> 对标 K8s LivenessProbe + ReadinessProbe + Istio Health Probe。

### 14.1 探针契约

```yaml
contract: CT-HEALTH-001
title: "跨系统标准化三态健康探针协议"
owner: MOD-MASTER_BLUEPRINT

endpoint_pattern: "/_health/{system_name}"

probes:
  liveness:
    description: "进程是否存活（最轻量——仅检查主线程心跳）"
    endpoint: "GET /_health/{system_name}/livez"
    success_response: "200 OK → { status: 'alive', pid: int, uptime_s: float }"
    failure_response: "503 Service Unavailable"
    check_mechanism: "每 10s 一次内部 tick——超时 3s 不响应→liveness FAIL"

  readiness:
    description: "是否可以接收请求（检查依赖+初始化完成）"
    endpoint: "GET /_health/{system_name}/readyz"
    success_response: "200 OK → { status: 'ready', dependencies: { dep_name: 'ok'|'degraded'|'down' } }"
    failure_response: "503 Service Unavailable → { status: 'not_ready', reason: '...' }"
    check_mechanism: "启动后逐项检查依赖可用性——全部OK→ready；任一FAIL→not_ready"
    startup_grace_period_s: 30

  degraded:
    description: "是否处于降级状态（活着但不完整——慢/部分功能缺失）"
    endpoint: "GET /_health/{system_name}/healthz"
    success_response: |
      200 OK + X-Degraded: true/false
      { status: 'healthy'|'degraded', degraded_reason: '...'|null }
    degradation_triggers:
      - "任一依赖 readiness=degraded → 本级 degraded=true"
      - "p99 延迟 > 5s → degraded=true"
      - "错误率 > 10% (rolling 60s window) → degraded=true"
      - "Token 预算使用 > 90% → degraded=true（仅 CE）"
      - "SQLite WAL checkpoint 延迟 > 3s → degraded=true（仅 db）"

health_check_cluster:
  aggregator: "Telemetry 系统 (mod-inf-009)"
  check_interval_s: 15
  health_history_retention_days: 30
  dashboard: "GPT-5.2 飞书推送 / Web Dashboard（按需）"
```

### 14.2 各系统探针特殊规则

| 系统 | liveness | readiness 依赖 | 特殊 degraded 条件 |
|------|:---:|------|------|
| Orc | 主线程心跳 | db | 待调度任务队列 > 100 |
| Script System | 进程存活 | 无外部依赖（自包含） | 脚本执行超时率 > 20% |
| CE | 主线程心跳 | VMS, LSG, KB | Token预算 > 7200/8000 |
| KB | 主线程心跳 | db, VMS | KE索引未提交数 > 50 |
| VMS | 主线程心跳 | ChromaDB | 单collection向量数 > 950K |
| Gates | 主线程心跳 | Script System | LSG误杀率 > 10% |
| Pipeline | 主线程心跳 | Orc, Gates | 路由决策延迟 > 100ms |
| LSG | 主线程心跳 | 无（自包含） | — （fail-closed，无degraded路径） |
| FLE | 主线程心跳 | db, Telemetry | 异常误报率 > 30% |
| Telemetry | 主线程心跳 | db | 指标积压 > 500 条 |
| MCP | 主线程心跳 | 无（自包含） | 连接数 > 100 |
| db | SQLite 心跳 | 无（自包含） | WAL checkpoint 延迟 > 5s |

### 14.3 年度系统健康审计 (Annual Health Audit)

**触发条件**：距离上次 audit ≥ 365 天 OR 系统 major upgrade 后。

**审计内容**：
1. 遍历 `health_history`（Telemetry 中保留 30 天→年度归档需单独机制）
2. 计算过去一年：uptime_ratio, mean_time_to_recovery, degradation_ratio_per_system
3. 生成 `annual_health_report_{year}.md` → 存入 KB（KE类型=HEALTH_AUDIT）
4. 若任一系统 uptime_ratio < 99.5% → 创建 `OPS-{SEQ}` 改进任务卡

---


## 十六、CDC 消费者驱动契约测试 + Can-I-Deploy + DLQ 体系

> 对标 Pact CDC + Pact Broker Can-I-Deploy + K8s Reconciliation Loop + Kafka DLQ。
> 核心原则：**契约不是生产者单方面声明 → 消费者通过测试定义期望 → 生产者在 CI 中验证 → 不一致则阻止部署。**

### 16.1 CDC 契约经纪人 (Pact Broker — 本地 SQLite 简化版)

```yaml
contract: CT-CDC-001
title: "消费者驱动契约测试框架——Pact 简化版"
owner: MOD-MASTER_BLUEPRINT

broker:
  type: "local_sqlite"
  path: ".audit_cache/cdc_broker.db"

lifecycle:
  1_consumer_defines:
    description: "消费者编写 contract test——定义它期望从生产者获得什么"
    file_pattern: "tests/contracts/consumer/test_{consumer}_{producer}.py"
    output: ".audit_cache/contracts/{consumer}_{producer}_expectation.json"
    ci: "consumer CI → 运行 consumer contract tests → 生成 expectation → 推送到 broker"

  2_provider_verifies:
    description: "生产者 CI 拉取所有 consumer expectations → 验证实现是否满足"
    trigger: "每次 provider PR → CI 从 broker 拉取 expectations → 运行 verification"
    file_pattern: "tests/contracts/provider/verify_{provider}.py"
    ci: "provider CI → verify against all consumer expectations → ALL_PASS → 允许部署"

  3_can_i_deploy:
    description: "部署前最后一次检查——确保当前版本兼容所有已知 consumer"
    ci_gate: "GATE-CDC-1（不可绕过——provider 未通过 consumer verification → 禁止部署）"
```

### 16.2 Can-I-Deploy CI 门禁

```yaml
gate: GATE-CDC-1
title: "Can-I-Deploy? 预部署契约合规门禁"
type: "pre_deploy_gate"
level: P0

checks:
  - name: "consumer_expectations_check"
    pass_condition: "ALL consumers = VERIFIED"
    fail_action: "BLOCK DEPLOY + 输出未满足的 expectations 列表"

  - name: "schema_version_check"
    ci_command: "python scripts/governance/d5_architecture/validate_schema_compat.py"
    pass_condition: "无 backward-incompatible 变更 OR 变更已通过 deprecation 流程"
    fail_action: "BLOCK DEPLOY + 要求走 deprecation 流程或回退 Schema 变更"

  - name: "contract_consistency_check"
    ci_command: "python scripts/governance/validate_integration_consistency.py"
    pass_condition: "蓝图 YAML 与实现完全一致"
    fail_action: "BLOCK DEPLOY + 输出不一致的 CT-* 编号 + 差异详情"

  - name: "health_check_cluster"
    pass_condition: "12 系统全部 liveness=alive + readiness=ready"
    fail_action: "BLOCK DEPLOY + 输出未就绪系统列表"
```

### 16.3 死信队列 (DLQ) — 统一故障恢复契约

```yaml
contract: CT-DLQ-001
title: "跨系统死信队列统一契约——故障期间的产出物不丢失"
owner: MOD-MASTER_BLUEPRINT

dlq_backend: "SQLite 表 `dlq_messages`"

table_schema: dlq_messages
fields:
  - {name: dlq_id, type: TEXT PRIMARY KEY, format: "uuid7"}
  - {name: producer_system, type: TEXT, enum: [orchestrator, script_system, context_engine, feedback_loop_engine]}
  - {name: target_contract, type: TEXT, format: "CT-*-*-*"}
  - {name: payload_json, type: TEXT}
  - {name: original_timestamp, type: TEXT, format: ISO8601}
  - {name: enqueue_timestamp, type: TEXT, format: ISO8601}
  - {name: replay_status, type: TEXT, enum: [PENDING, REPLAYING, SUCCESS, FAILED]}
  - {name: replay_attempts, type: INTEGER, default: 0}
  - {name: last_error, type: TEXT, nullable: true}

replay_strategy: "chronological_ordered"
replay_trigger: "target system readiness 从 not_ready → ready"
replay_batch_size: 100
max_replay_attempts: 3
max_queue_age_hours: 72

monitoring:
  dlq_depth_gauge: "每 60s 报告各系统的 DLQ 积压数量"
  dlq_age_alert_hours: 48
  dlq_circuit_breaker: "dlq_depth > 10000 → 暂停入队 + 告警 + 要求人工清淤"
```

### 16.4 Reconciliation Loop（K8s Controller Pattern）

```yaml
contract: CT-RECONCILE-001
title: "状态一致性调和循环——期望状态 vs 实际状态的持续对齐"
pattern: "control_loop"
interval_s: 30

invariants:
  - {check: "TaskCard.status==BLOCKED → Gates.last_check.result==FAIL", auto_repair: true}
  - {check: "KE.status==ACTIVE → VMS.has_embedding(ke_id)==True", auto_repair: true}
  - {check: "Orc.active_tasks ≤ Orc.max_concurrent_tasks", auto_repair: true}
  - {check: "circuit_breaker.state 与 failure_count + recovery_window 计算一致", auto_repair: true}
  - {check: "dlq_messages 中 FAILED 条目 replay_attempts ≥ max=3 → 通知 Owner", auto_repair: false}
```

### 16.5 冷启动契约 (Startup Contract)

```yaml
contract: CT-STARTUP-001
title: "12 系统启动顺序与依赖就绪契约"
owner: MOD-MASTER_BLUEPRINT

boot_order:
  layer_0: {systems: [database, mcp_adapter], startup_timeout_s: 10}
  layer_1: {systems: [vector_memory, knowledge_base], depends_on: [database], startup_timeout_s: 20}
  layer_2: {systems: [gates, llm_security_gate], startup_timeout_s: 15}
  layer_3: {systems: [context_engine, pipeline], depends_on: [vector_memory, gates, knowledge_base, llm_security_gate], startup_timeout_s: 30}
  layer_4: {systems: [orchestrator, script_system, feedback_loop_engine, telemetry], depends_on: [context_engine, pipeline, database, vector_memory, gates], startup_timeout_s: 30}

startup_health_check:
  mechanism: "每层启动 → 等待本层所有系统 readyz→200 → 启动下一层"
  global_timeout_s: 120
  timeout_action: "超时未就绪的系统 → 标记 degraded → 继续启动其他系统 → 通知 Owner"
```

### 16.6 资源清理/Teardown 契约

```yaml
contract: CT-TEARDOWN-001
title: "TaskCard 取消/失败时的跨系统资源清理契约"
owner: MOD-MASTER_BLUEPRINT

trigger: "TaskCard.status → CANCELLED 或 FAILED"

cleanup_actions:
  - {system: orchestrator, action: "释放并发槽位 → 从 active_tasks 队列中移除"}
  - {system: context_engine, action: "标记关联 session 为 expired → 释放 token 预算配额"}
  - {system: gates, action: "归档本次任务的门禁裁决记录"}
  - {system: pipeline, action: "中断 M1-M11 管道 → 标记中间产物为 abandoned"}
  - {system: vector_memory, action: "已写入的向量保持不变（审计追溯）→ 不删除"}
  - {system: knowledge_base, action: "DRAFT 状态的 KE 标记为 abandoned"}
  - {system: feedback_loop_engine, action: "标记本任务关联的 anomaly record 为 resolved_by_cancellation"}

cleanup_timeout_s: 10
cleanup_failure_action: "记录 audit_log + 不阻塞任务取消状态写入"
```

---

## 十七、SLO/SLI 服务等级目标

> 对标 Google SRE Book §4——每条CT-*的telemetry定义"报什么"，SLO定义"应是多少"。
> 没有SLO=没有优化目标=没有告警阈值=不知道"正常"是什么。

```yaml
contract: CT-SLO-001
title: "每条CT-*的服务等级目标(SLO)与指标(SLI)"
owner: MOD-MASTER_BLUEPRINT

slo_matrix:
  - {ct_id: CT-ORC-SCRIPT-001, metric: "CRITICAL finding→task creation latency", slo: "p95 < 3600s", alert: "> 7200s"}
  - {ct_id: CT-ORC-SCRIPT-001, metric: "exit 3→global block latency", slo: "p99 < 10s", alert: "> 30s"}
  - {ct_id: CT-ORC-CE-001, metric: "context_build_duration", slo: "p95 < 3s", alert: "> 8s"}
  - {ct_id: CT-ORC-CE-001, metric: "context_token_count", slo: "always ≤ 8000", alert: "> 7200 (90% budget)"}
  - {ct_id: CT-ORC-VMS-001, metric: "orc_vms_write_latency", slo: "p99 < 1s", alert: "p99 > 3s"}
  - {ct_id: CT-ORC-GATE-001, metric: "task_gate_latency all gates", slo: "p99 < 50ms", alert: "> 200ms"}
  - {ct_id: CT-SCRIPT-KB-001, metric: "finding_to_ke_auto_create latency", slo: "p95 < 5s", alert: "> 10s"}
  - {ct_id: CT-SCRIPT-GATE-001, metric: "pre_commit gate duration", slo: "p95 < 30s", alert: "> 60s"}
  - {ct_id: CT-CE-VMS-001, metric: "vms_search_latency", slo: "p99 < 500ms", alert: "> 2s"}
  - {ct_id: CT-CE-LSG-001, metric: "lsg_latency total", slo: "p99 < 100ms", alert: "> 500ms"}
  - {ct_id: CT-CE-LSG-001, metric: "lsg_false_positive_rate", slo: "< 5%", alert: "> 10%"}
  - {ct_id: CT-KB-VMS-001, metric: "kb_vms_embed_latency", slo: "p99 < 5s", alert: "> 10s"}
  - {ct_id: CT-FLE-ORC-001, metric: "fle_detect_dispatch_latency", slo: "p95 < 30s", alert: "> 60s"}
  - {ct_id: CT-FLE-ORC-001, metric: "fle_false_positive_rate", slo: "< 10%", alert: "> 20%"}

slo_error_budget:
  burn_rate_alert: "error budget burn rate > 10x → FLE ESCALATE"
  monthly_budget: "1% of total operations = 43.8 min downtime/month"
  policy: "budget exhausted → halt feature velocity → all resources to reliability"
```

---

## 十八、Bulkhead 隔舱化 + Watchdog 监视者 + Backup 备份

### 18.1 Bulkhead 资源池隔舱 (CT-BULKHEAD-001)

```yaml
contract: CT-BULKHEAD-001
title: "12系统资源池隔舱化——故障域隔离"
principle: "每个系统独立资源池——一个系统的慢调用不会饿死其他系统"

per_system_resources:
  orchestrator: {thread_pool: 4, sqlite_connections: 2, memory_limit_mb: 256}
  script_system: {thread_pool: 2, subprocess_limit: 5, memory_limit_mb: 128}
  context_engine: {thread_pool: 3, chromadb_connections: 2, memory_limit_mb: 512}
  knowledge_base: {thread_pool: 2, sqlite_connections: 2, memory_limit_mb: 128}
  vector_memory: {thread_pool: 3, chromadb_connections: 3, memory_limit_mb: 256}
  gates: {thread_pool: 2, memory_limit_mb: 64}
  pipeline: {thread_pool: 1, memory_limit_mb: 64}
  llm_security_gate: {thread_pool: 2, memory_limit_mb: 128}
  feedback_loop_engine: {thread_pool: 2, sqlite_connections: 2, memory_limit_mb: 128}
  telemetry: {thread_pool: 1, sqlite_connections: 2, memory_limit_mb: 64}
  mcp_adapter: {thread_pool: 1, memory_limit_mb: 64}
  database: {thread_pool: "SQLite WAL → max 5 concurrent writers", memory_limit_mb: 64}

shared_pools:
  sqlite_wal: {max_connections: 5, queue_policy: "FIFO with 5s timeout"}
  chromadb_http: {max_connections: 3, queue_policy: "FIFO with 3s timeout"}

slow_call_detection:
  threshold_ms: 5000
  action: "隔离该系统线程→返回degraded response→等待恢复或超时→强制终止"
```

### 18.2 三冗余监视者 (CT-WATCHDOG-001)

```yaml
contract: CT-WATCHDOG-001
title: "三冗余监视者——谁监视Telemetry和FLE"
principle: "最少3个独立监视进程——两两互检——任何2个不可用→Panic Mode"

watchers:
  - {name: "telemetry_watchdog", monitors: [FLE, Orc, Script System], interval_s: 15}
  - {name: "fle_watchdog", monitors: [Telemetry, CE, Pipeline], interval_s: 15}
  - {name: "owner_watchdog", monitors: ["all_12_systems"], type: "external_cron_job", interval_s: 300}

panic_mode:
  trigger: "≥2 watchers 30分钟无心跳"
  action: "暂停所有LLM任务→阻断pre-commit→发送飞书紧急通知→等待Owner手动恢复"
  recovery: "Owner通过/_health/panic/recover端点手动解除"

dead_mans_switch:
  mechanism: "每10分钟向外部文件写入heartbeat → owner cron每分钟检查——>30min无更新→ALERT"
```

### 18.3 备份与恢复 (CT-BACKUP-001)

```yaml
contract: CT-BACKUP-001
title: "数据备份与恢复统一契约"
principle: "1人误删不能=永久丢失——每日自动备份+季度恢复演练"

backup:
  sqlite: "daily 03:00 → VACUUM INTO backup/zephyr_{date}.db"
  chromadb: "daily 04:00 → zip data/chroma/ → backup/chroma_{date}.zip"
  retention: "30 daily + 12 monthly + N yearly"
  integrity_check: "备份后自动 PRAGMA integrity_check → FAIL时重新备份并告警"

restore:
  procedure: "关闭12系统→替换db/chroma→重启→CT-RECONCILE-001自动修复不一致"
  test_restore_interval_days: 90
```

---

## 十九、配置统一管理 + Feature Flag + 安全

### 19.1 配置契约 (CT-CONFIG-001)

```yaml
contract: CT-CONFIG-001
title: "12系统共享配置统一管理"
principle: "共享配置项MUST在config/system_config.yaml集中管理——不得各自硬编码"

config_items:
  - {key: "chromadb.persist_path", consumers: [VMS, CE, KB], validation: "MUST be existing writable dir"}
  - {key: "sqlite.db_path", consumers: ["*"], validation: "MUST be writable path"}
  - {key: "ce.token_budget", consumers: [CE, Orc], validation: "INT: 2000-32000"}
  - {key: "lsg.fail_closed", consumers: [LSG, CE], validation: "MUST be true (irreversible)"}
  - {key: "fle.sampling_interval_s", consumers: [FLE, Telemetry], validation: "INT: ≥30"}
  - {key: "chromadb.embedding_model", consumers: [VMS, CE, KB], validation: "ENUM: [BGE-M3, text-embedding-3-large]"}

validation_on_startup: "启动时遍历12系统→校验各自config引用与CT-CONFIG-001一致性→不一致=启动失败"
```

### 19.2 Feature Flag 运行时开关 (CT-FEATUREFLAG-001)

```yaml
contract: CT-FEATUREFLAG-001
title: "跨系统能力运行时开关"
principle: "每条CT-*契约可以运行时禁用——VMS坏了就先关掉VMS写入，不丢数据就行"

toggle_rules:
  - "每条CT-*契约有 runtime_enabled=true/false (default=true)"
  - "runtime_enabled=false → 该契约调用返回 NOT_AVAILABLE + degrade路径"
  - "toggle变更写入audit_log——包含: who, when, why"
  - "toggle持久化到db.feature_flags表——重启后保持"
  - "toggle不影响CDC/Can-I-Deploy——仅运行时行为"

emergency_shutdown:
  command: "POST /_admin/toggle/{CT-ID} → {enabled: false, reason: '...'}"
  auth: "需要capability: admin_toggle_feature_flag"
```

### 19.3 Secrets 管理 (CT-SECRETS-001)

```yaml
contract: CT-SECRETS-001
title: "API Key与密钥统一管理"
principle: "任何密钥不得出现在git中——本地.env+启动时校验"

secrets_backend: "本地 .env 文件（1人模式）"
forbidden:
  - "禁止任何 API key 硬编码在 Python 源码中"
  - "禁止任何 API key 出现在 git history 中"
  - "禁止任何 API key 出现在 blueprint YAML 中"
  - "禁止任何 API key 出现在日志中"

startup_check:
  - "遍历 .env 必需key列表 → 缺少则启动失败+提示"
  - "git log scan → 如发现历史中有API key → ALERT + 要求rotate"
```

### 19.4 AI施工KISS约束 (CT-KISS-001)

```yaml
contract: CT-KISS-001
title: "AI agent施工约束——Keep It Simple"
principle: "100%AI施工最大风险=过度工程化。本契约是AI的刹车。"

constraints:
  - "每个CT-*的实现不超过3个类（Protocol+Impl+Factory）"
  - "每个方法不超过30行——超过→拆分"
  - "不使用超过2级的继承层次"
  - "不使用元编程/metaclass除非§九DD表特批"
  - "adapter/wrapper只能有1层——不做'adapter pattern over an adapter'"
  - "抛出异常前先检查是否可以degrade而非crash"

ai_self_check:
  question: "这个实现能否删掉一半代码仍然功能完整？"
  if_yes: "删掉那一半"
```

---

## 二十、数据生命周期 + 多环境 + Chaos + Codegen + Breaking Change

### 20.1 数据生命周期 (CT-DATA-LIFECYCLE-001)

```yaml
contract: CT-DATA-LIFECYCLE-001
title: "数据保留策略——什么数据多久后自动清理"

retention_policies:
  Finding_logs: {hot_days: 30, cold_days: 365, action: "archive_to_parquet → delete from db"}
  KE_DRAFT: {hot_days: 90, action: "→ ARCHIVED if no human confirm"}
  KE_DEPRECATED: {retention_years: 2, action: "→ purge with audit_log"}
  audit_log: {retention_years: 7, immutable: true, action: "可以归档但不可删除"}
  dlq_messages: {max_age_hours: 72, action: "→ archive → notify owner"}
  fle_metrics: {hot_days: 30, cold_days: 365, resolution: "30s→60s→300s rollup"}
  TaskCard: {hot_days: 90, cold_days: 365, action: "→ cold_storage → 2y → purge"}
  Session_embeddings: {ttl_days: 7, action: "auto-delete"}

gc_schedule: "daily 06:00 → scan all tables → apply retention_policies → audit_log GC summary"
```

### 20.2 多环境隔离

```yaml
environments:
  dev:
    chromadb_path: "data/dev/chroma/"
    sqlite_path: "data/dev/zephyr.db"
    token_budget: 4000
    llm_models: [claude-4.5-haiku, gemini-3.0-flash]
    environment_marker: "DEV_MODE=true → 安全校验宽松 → 熔断阈值降低 → 不发送飞书通知"
  prod:
    chromadb_path: "data/chroma/"
    sqlite_path: "data/zephyr.db"
    token_budget: 8000
    llm_models: [opus-4.5, gpt-5.2, claude-4.5-sonnet]
    environment_marker: "PROD_MODE=true → 全严格安全校验 → 全熔断策略 → 全通知渠道"
```

### 20.3 Chaos Engineering (CT-CHAOS-001)

```yaml
contract: CT-CHAOS-001
title: "故障注入与韧性验证——定期验证降级路径确实有效"

fault_injection_tests:
  - {target: CT-CE-VMS-001, inject: "VMS p99 3000ms延迟", expect: "CE degraded=true + 继续build"}
  - {target: CT-ORC-VMS-001, inject: "VMS 100% 500 errors", expect: "circuit_breaker OPEN after 10 + fallback SQLite"}
  - {target: CT-CE-LSG-001, inject: "LSG crash", expect: "fail-closed → CE refused ALL → FLE alerted"}
  - {target: CT-ORC-SCRIPT-001, inject: "Script exit 3 twice in 5min", expect: "global block → owner notified"}

chaos_schedule: "每月第一周六凌晨（dev环境——不影响prod）"
chaos_failure_policy: "任何injection导致实际行为不符合expect → P1 issue → 修复降级路径"
```

### 20.4 Contract→Codegen + Breaking Change Detection

```yaml
codegen:
  trigger: "变更任何CT-* YAML或SCHEMA-* YAML后 → CI自动触发"
  outputs:
    - "CT-* YAML → tests/contracts/protocols/{ct_id}_protocol.py (Python Protocol class)"
    - "SCHEMA-* YAML → src/zephyr/shared/schemas/{schema_id}.py (Python dataclass)"
  validation: "CI compare generated vs disk → diff → FAIL if不一致"
  tool: "scripts/governance/d5_architecture/generators/generate_contracts.py"

breaking_change_detector:
  script: "scripts/governance/d5_architecture/detect_breaking_changes.py"
  ci_gate: "GATE-CDC-2"
  rules:
    - "字段删除 → BREAKING → CI WARN + Owner审批确认"
    - "字段类型变更 → BREAKING → CI FAIL"
    - "新增optional字段 → OK → auto-pass"
    - "SLO收紧 → BREAKING → consumer re-approve"
    - "exit code语义变更 → BREAKING → CI FAIL"
```

---

## 二十一、外部依赖生命周期管理

> Round 3 核心洞察：蓝图定义了系统内部如何协作，但外部世界（LLM模型、Python包、ChromaDB）会变。
> 本章确保外部变化时系统不会静默崩溃——而是有预案地应对。

### 21.1 模型注册表 (CT-MODEL-REGISTRY-001)

```yaml
contract: CT-MODEL-REGISTRY-001
title: "LLM模型注册表——模型名不作为契约，能力声明作为契约"
principle: "CT-* 契约不写模型名——写能力需求。模型名→能力映射在注册表集中管理，支持多候选fallback。"

capability_declaration:
  code_generation_elite: "HumanEval ≥ 90%, 128K context, function calling"
  code_generation_standard: "HumanEval ≥ 75%, 64K context"
  audit_reasoning: "长上下文 ≥ 200K, 逻辑推理强, 低幻觉"
  security_analysis: "指令遵循严格, 低注入风险"
  embedding_text: "1024d+, MTEB retrieval ≥ 60"
  cheap_fast: "便宜+快, 用于dev环境和简单任务"

mapping:
  code_generation_elite: {primary: opus-4.5, fallback: [claude-5.0-sonnet]}
  code_generation_standard: {primary: gpt-5.2, fallback: [qwen-3-max, glm-5.1]}
  audit_reasoning: {primary: claude-4.5-sonnet, fallback: [gemini-3.0-pro]}
  security_analysis: {primary: gpt-5.2, fallback: [claude-4.5-sonnet]}
  embedding_text: {primary: text-embedding-3-large, fallback: [BGE-M3]}
  cheap_fast: {primary: claude-4.5-haiku, fallback: [gemini-3.0-flash]}

deprecation_policy:
  notice_period_days: 30
  migration_script: "scripts/governance/migrate_model_references.py"
  ci_check: "所有CT-*引用MUST使用 capability_declaration key——直接引用模型名→CI FAIL"

runtime_fallback:
  mechanism: "primary模型 503/超时→自动切换到fallback列表下一个→最多尝试3个→全部失败→degraded"
  telemetry: "model_fallback_count (counter, labels: [from_model, to_model, reason])"
```

### 21.2 外部依赖版本锁定 (CT-DEPS-001)

```yaml
contract: CT-DEPS-001
title: "外部依赖版本锁定与升级策略"
principle: "外部依赖版本锁定在 pyproject.toml——升级必须走审批流程。AI agent 不能自动 pip install --upgrade。"

locked_versions:
  python: ">=3.12,<3.13"
  chromadb: "==0.5.x"
  sqlite: ">=3.42 (bundled with Python 3.12)"
  openai: ">=1.0,<2.0"
  anthropic: ">=0.40,<1.0"

upgrade_procedure:
  - "创建 deps-upgrade 分支"
  - "运行全量测试（含 CDC verification + 全链路集成测试）"
  - "Owner 在 dev 环境验证 ≥ 24h"
  - "合并到 prod → OPS-{SEQ} TaskCard 跟踪升级历史"
  - "回滚路径：git revert + pip install -r requirements.txt --force-reinstall"

emergency_pin:
  mechanism: "pyproject.toml 中的dependencies全部 pinned——不使用 >= 模糊版本"
  ai_restriction: "AI agent MUST NOT 修改 pyproject.toml 或 requirements.txt 除非 §九DD表特批"

compatibility_matrix:
  test_file: "tests/integration/test_dependency_compatibility.py"
  description: "每次依赖升级后自动运行——检测已知不兼容组合"
```

---

## 二十二、时间维度腐烂防护

### 22.1 知识新鲜度与废止 (CT-KNOWLEDGE-FRESHNESS-001)

```yaml
contract: CT-KNOWLEDGE-FRESHNESS-001
title: "知识条目新鲜度与废止机制"
principle: "KE 不仅有物理生命周期——更有语义生命周期。过时知识比无知识更危险。"

freshness_signals:
  - signal: "KE中包含具体版本号"
    action: "版本升级后自动标记 stale_warning"
  - signal: "KE中引用API端点"
    action: "API合约变更后自动标记"
  - signal: "last_verified_date"
    action: "超过 180 天未人工确认→自动降级为 NEEDS_REVIEW"

freshness_actions:
  stale_warning:
    description: "向量检索仍返回但附带 freshness='⚠️ stale_180d' 标记"
    ce_behavior: "CE compress阶段降低 stale_warning KE的优先级——排在fresh KE之后"
  needs_review:
    description: "不再出现在默认向量检索结果中"
    ce_behavior: "仅当查询显式包含'include_stale=true'时返回"
  deprecated:
    description: "等同于物理 DEPRECATED——仅审计查询可访问"

freshness_sweep:
  schedule: "每月1号 03:00"
  action: "扫描全KE表→评估freshness_signals→生成 freshness_report.md → 推送Owner飞书"
  auto_downgrade: "last_verified > 180d → NEEDS_REVIEW（自动——无人确认=默认过时）"
```

### 22.2 系统文件卫生保洁 (CT-HOUSEKEEPING-001)

```yaml
contract: CT-HOUSEKEEPING-001
title: "系统文件卫生保洁——防止6个月后磁盘被无声吞噬"
principle: "CT-DATA-LIFECYCLE 管数据库、本节管文件系统。两者互补。"

housekeeping_schedule: "每周日凌晨 02:00"

tasks:
  - {target: ".pytest_cache/ __pycache__/ .mypy_cache/ .ruff_cache/", action: "recursive rm -rf"}
  - {target: "ChromaDB orphaned segments", action: "chromadb vacuum"}
  - {target: "SQLite WAL files > 100MB", action: "PRAGMA wal_checkpoint(TRUNCATE)"}
  - {target: "session_logs older than 90d", action: "tar.gz → archive/session_logs/ → delete original"}
  - {target: "git objects", action: "git gc --aggressive --prune=now (monthly only)"}
  - {target: "Codegen intermediate outputs older than 7d", action: "rm"}

disk_watermark:
  warning_percent: 80
  critical_percent: 90
  critical_action: "暂停所有非P0任务→通知Owner→手动清淤→恢复后自动运行housekeeping"
```

### 22.3 AI会话手递手协议 (CT-SESSION-handoff-001)

```yaml
contract: CT-SESSION-handoff-001
title: "AI会话手递手协议——Session A→Session B的无损上下文转移"
principle: "这是100%AI施工下最独特的契约——传统Jira追踪进度，AI只有chat history（不跨session）。
AI agent的工作状态MUST持久化到磁盘——下一个AI session MUST能恢复上级session的上下文。"

handoff_manifest: ".trae/session_state/{CT_ID}_progress.yaml"

manifest_schema:
  ct_id: "CT-ORC-CE-001"
  last_session_date: "2026-05-05T14:30:00Z"
  completion_percent: 60
  completed_items:
    - "ce_build() 实现完成——tests/test_ce_build.py 全PASS"
    - "ce_compress() 实现完成——Token预算优先级逻辑测试通过"
  remaining_items:
    - "ce_validate() LSG集成——pending（先读 CT-CE-LSG-001 的 ai_prompt）"
    - "ce_inject() session写入——pending"
  known_issues:
    - "ce_compress 在 8000 token边界有 ±50 token tiktoken计数误差——待修但不阻塞"
  files_touched:
    - "src/zephyr/orchestration/context_management/builder.py"
    - "tests/test_ce_build.py"
    - "tests/test_ce_compress.py"
  next_session_instructions: >
    1. 先跑 tests/test_ce_build.py + test_ce_compress.py 确认绿色
    2. 从 ce_validate() 开始——CT-CE-LSG-001 的 ai_prompt 是你唯一的施工指南
    3. 不要重构 builder.py——上次session确认结构正确
    4. 完成后更新本 manifest → completion_percent=100

handoff_ci_check:
  description: "CI检查所有CT-*对应的handoff manifest存在且 ≤ 30天未更新→否则 CI WARN"
  script: "scripts/governance/check_handoff_manifests.py"

ai_reading_instruction: >
  AI agent启动后首先读取对应CT-*的手递手manifest——如果存在且 newer than 上次读取→优先参考。
  如果manifest说 completion_percent=60 → 不要从0开始——从 remaining_items 继续。
```

---

## 二十三、生产成熟度

> Google SRE / K8s / 任何大型项目的标配——但常常在小型项目中被忽略。
> 1人+AI模式下，这些是"预防==治愈"的关键。

### 23.1 API稳定性级别 (CT-STABILITY-001)

```yaml
contract: CT-STABILITY-001
title: "CT-* API稳定性级别——消费者可以多放心地依赖"
principle: "K8s每个API有alpha/beta/stable标记——消费者在CI阶段就知道风险等级"

stability_levels:
  stable: "接口不会 breaking change——消费者可放心长期依赖——废弃前至少2个MAJOR过渡版本"
  beta: "接口可能微调——消费者可用但需关注变更通知——breaking change至少30天通知"
  alpha: "实验性——随时可能变更或移除——仅限内部使用——不建议消费者长期依赖"
  deprecated: "即将移除——消费者MUST在target_removal_date前完成迁移"

stability_matrix:
  stable:
    - {ct_id: CT-ORC-SCRIPT-001, since: "2026-05-01"}
    - {ct_id: CT-ORC-GATE-001, since: "2026-05-01"}
    - {ct_id: CT-SCRIPT-GATE-001, since: "2026-05-01"}
    - {ct_id: CT-HEALTH-001, since: "2026-05-05"}
    - {ct_id: CT-CBAC-001, since: "2026-05-05"}
  beta:
    - {ct_id: CT-ORC-CE-001, since: "2026-05-01"}
    - {ct_id: CT-ORC-VMS-001, since: "2026-05-01"}
    - {ct_id: CT-CE-VMS-001, since: "2026-05-01"}
    - {ct_id: CT-KB-VMS-001, since: "2026-05-01"}
    - {ct_id: CT-CDC-001, since: "2026-05-05"}
    - {ct_id: CT-DLQ-001, since: "2026-05-05"}
    - {ct_id: CT-SLO-001, since: "2026-05-05"}
  alpha:
    - {ct_id: CT-CHAOS-001}
    - {ct_id: CT-MODEL-REGISTRY-001}
    - {ct_id: CT-KNOWLEDGE-FRESHNESS-001}
    - {ct_id: CT-SESSION-handoff-001}
    - {ct_id: CT-CANARY-001}
  deprecated: []

ci_check: "消费者引用alpha级CT-* → CI WARN ——引用deprecated级 → CI FAIL"
```

### 23.2 金丝雀发布 (CT-CANARY-001)

```yaml
contract: CT-CANARY-001
title: "Schema变更金丝雀发布——从不等于0→100%瞬间切换"
principle: "修改共享Schema不直接推全系统——从1系统→3→全部，每个阶段观察24h"

canary_strategy:
  schema_change:
    phase_1:
      systems: [orchestrator]
      description: "Orc使用新Schema读写——其他11系统仍用旧版——新旧兼容期"
      duration_hours: 24
    phase_2:
      systems: [orchestrator, script_system, gates]
      duration_hours: 24
    phase_3:
      systems: ["*"]  # 全12系统
      description: "确认兼容后全量切换——旧Schema相关代码标记为可移除"

  rollback_trigger: "任何阶段 telemetry 错误率 > 基线 2x → 自动回滚到旧Schema"
  rollback_mechanism: "Schema version negotiation（§三CTR-VER-001）的双版本过渡期机制"
```

### 23.3 事件自动复盘 (CT-INCIDENT-001)

```yaml
contract: CT-INCIDENT-001
title: "事件复盘——每次熔断/降级/阻断自动生成trace report"
principle: "故障不可怕——故障不可追溯才可怕。本契约确保每次故障都能事后复现。"

postmortem_trigger:
  - "circuit_breaker state → OPEN"
  - "panic_mode activated"
  - "exit code 3 received"
  - "SLO error budget burn rate > 5x"
  - "DLQ depth > 5000"

auto_generated_report:
  what: "从 audit_log + telemetry 的30分钟窗口自动提取事件时间线"
  why: "关联的 metrics + traces + DLQ messages 自动拼装因果链"
  impact: "受影响的任务数、延迟、降级时长、是否有数据丢失"
  timeline: "HH:MM:SS → event → affected systems → auto/mitigation applied"

human_review:
  fields:
    - {name: root_cause, type: "enum[external_dependency, schema_change, resource_exhaustion, unknown, false_alarm]", required: true}
    - {name: accepted_verdict, type: "bool", description: "Owner接受自动分析结论？"}
    - {name: action_items, type: "list[str]", description: "如有待改进→创建OPS-{SEQ} TaskCard"}
  retention: "所有postmortem存入KB——KE类型=INCIDENT_POSTMORTEM——failure_patterns collection自动索引"
```

### 23.4 已知竞态条件目录 (CT-RACE-CONDITIONS-001)

```yaml
contract: CT-RACE-CONDITIONS-001
title: "已知竞态条件目录——主动声明而非被动踩坑"
principle: "12系统并发→必然有竞态。与其线上遇到再修→不如先声明'我们知道、我们接受、我们有缓解'"

known_race_conditions:
  - id: RC1
    scenario: "两个任务同时完成→都尝试写VMS→同一vector_id"
    mitigation: "content_hash去重——后写入者detect duplicate→skip+log——无数据丢失"
    acceptable: true

  - id: RC2
    scenario: "FLE ESCALATE + Owner手动改Gate阈值同时发生"
    mitigation: "Gate threshold变更持有排他锁——last_write_wins + audit_log记录覆盖行为"
    acceptable: true

  - id: RC3
    scenario: "Orc标记BLOCKED + Script System同时标记exit 0→恢复"
    mitigation: "Orc的status变更使用CAS (compare-and-swap)——WHERE current_status=BLOCKED→TODO"
    acceptable: true

  - id: RC4
    scenario: "DLQ replay + 正常写入同时发生"
    mitigation: "natural_key去重——replay优先（因为timestamp更早——数据产生的时刻应该在先）"
    acceptable: true

  - id: RC5
    scenario: "CE的compress阶段 + Script System同时修改KE"
    mitigation: "CE读取KE时为快照读(Snapshot Isolation via SQLite WAL)——不锁KE表"
    acceptable: true

testing: "tests/integration/test_race_conditions.py ——模拟RC1-RC5 ——验证缓解策略确实生效"
```

### 23.5 LLM API美元成本预算 (CT-COST-BUDGET-001)

```yaml
contract: CT-COST-BUDGET-001
title: "LLM API调用美元成本预算——Token预算管体积，Cost预算管钱包"
principle: "CT-CE-001的8000 token预算保证上下文不爆炸——本契约保证账单不爆炸"

cost_table_per_1M_tokens:
  opus-4.5: {input: 15, output: 75}
  gpt-5.2: {input: 3, output: 15}
  claude-4.5-sonnet: {input: 3, output: 15}
  claude-4.5-haiku: {input: 0.80, output: 4}
  gemini-3.0-pro: {input: 1.25, output: 10}
  qwen-3-max: {input: 1.60, output: 6.40}
  glm-5.1: {input: 0.50, output: 2}

monthly_budget_usd: 50
per_task_budget_usd:
  MODEL_BUILD: 5.00
  AUDIT: 1.00
  OPS: 2.00
  ANALYSIS: 3.00
  QUICK_FIX: 0.50

alert_thresholds:
  daily_75pct: "飞书通知——今日已用 $X / 日均预算 $Y"
  monthly_90pct: "暂停所有非P0 LLM调用——Owner审批恢复——防止超支"

cost_tracking:
  collector: "Telemetry → 每次LLM调用记录 input_tokens + output_tokens + model_name"
  calculator: "FLE → 读取token数×cost_table → 写入 fle_metrics (metric: llm_api_cost_usd)"
  dashboard: "FLE飞书推送每日/每周/每月成本汇总"
```

---

## 二十四、边界情况防护

> 低概率、高影响——磁盘满、网络断——这类问题不常发生，但一旦发生就是数据损坏级。

### 24.1 磁盘空间耗尽 (CT-DISK-GUARD-001)

```yaml
contract: CT-DISK-GUARD-001
title: "磁盘空间耗尽防护——防止写操作半途失败导致数据损坏"
principle: "写半截 > 不写。宁可拒绝写入，不写半截损坏数据。"

disk_guard:
  pre_write_check: "每次写操作(dlq/sqlite/chromadb)前→检查可用空间→< 100MB→拒绝写入+ALERT"
  atomic_writes: |
    所有写操作使用 tempfile + os.replace / atomic rename:
    - SQLite: WAL mode atomic commit（已内置）
    - ChromaDB: 依赖ChromaDB自身atomicity
    - 文件系统: write to .tmp → fsync → os.replace
    做到'要么完整写入要么不写'
  emergency_reserve: "保留 200MB 磁盘空间——仅用于 emergency_log (CT-FLE-DB-001) 和 Owner飞书通知"

monitoring:
  disk_free_gauge: "Telemetry 每 300s 上报剩余空间——< 1GB → WARN → < 200MB → CRITICAL"
```

### 24.2 网络分区 (CT-NETWORK-PARTITION-001)

```yaml
contract: CT-NETWORK-PARTITION-001
title: "网络分区容忍——本地系统正常运行但无法访问外部LLM API"
principle: "网络断了不可怕——系统假死才可怕。detect→degrade→queue→recover——不丢任务。"

partition_detection:
  mechanism: "每 60s → HEAD api.openai.com + HEAD api.anthropic.com"
  states:
    dual_online: "双API可达→正常"
    single_online: "单API可达→degraded——仅用可达的API"
    dual_offline: "双API不可达→ offline_mode"

offline_mode:
  trigger: "dual_offline 持续 > 60s"
  action:
    - "暂停所有待处理LLM任务→ status: QUEUED (不创建新任务)"
    - "所有CT-* LLM调用返回 degraded——附带原因 'network_partition'"
    - "FLE记录分区开始时间→写入 anomaly_record"
    - "本地任务（Script System / Gates / HealthCheck）继续运行"
  recovery:
    - "dual_online 恢复→从 QUEUED 按FIFO 恢复任务"
    - "分区期间的Finding和metrics已写入本地SQLite——无数据丢失"
    - "FLE记录分区结束时间→计算 offline_duration_minutes"
```

---

---
---

## 二十五、性能基准与回归预防 (CT-BENCH-001)

> 对标 Google SRE Performance Regression Tests + K8s perf-tests。
> CT-SLO-001定义了"应该多快"，但SLO是事后监控——本契约定义CI门禁："这个PR不能让它变慢"。

```yaml
contract: CT-BENCH-001
title: "跨系统性能基准与回归预防——每次PR自动跑bench"
principle: "SLO是事后告警→BENCH是事前预防。任何CT-*的p95延迟退化>10%→CI FAIL"

bench_targets:
  - ct_id: CT-ORC-CE-001
    test: "tests/benchmarks/test_ce_context_build.py"
    baseline_latency_p95_ms: 3000
    regression_threshold_pct: 10
  - ct_id: CT-CE-VMS-001
    test: "tests/benchmarks/test_vms_search.py"
    baseline_latency_p99_ms: 500
    regression_threshold_pct: 15
  - ct_id: CT-ORC-VMS-001
    test: "tests/benchmarks/test_orc_vms_write.py"
    baseline_latency_p99_ms: 1000
    regression_threshold_pct: 10
  - ct_id: CT-ORC-GATE-001
    test: "tests/benchmarks/test_gate_latency.py"
    baseline_latency_p99_ms: 50
    regression_threshold_pct: 20
  - ct_id: CT-SCRIPT-GATE-001
    test: "tests/benchmarks/test_pre_commit_gate.py"
    baseline_latency_p95_ms: 30000
    regression_threshold_pct: 15
  - ct_id: CT-CE-LSG-001
    test: "tests/benchmarks/test_lsg_latency.py"
    baseline_latency_p99_ms: 100
    regression_threshold_pct: 10

baseline_management:
  storage: ".audit_cache/benchmarks/baseline_{ct_id}.json"
  update_rule: "baseline在CI PASS后自动更新——使用最近7天p95 median作为新baseline"
  drift_alert: "baseline 30天未更新→CI WARN——可能环境变化导致bench无效"

ci_integration:
  gate: "GATE-BENCH-1"
  trigger: "每次PR触及任何CT-*契约相关代码→自动跑对应bench"
  pass_condition: "所有bench regression < threshold"
  fail_action: "CI FAIL + 输出退化详情(CT-*, baseline vs actual, pct change)"
  emergency_override: "GATE-BENCH-1失败可override→需Owner审批+record override reason→写入audit_log"

ai_prompt: >
  你是CT-BENCH-001的AI agent。当代码变更可能影响性能时：
  (1) 任何触及CT-*契约相关代码的PR→自动跑对应的benchmark test；
  (2) p95/p99延迟退化>10%→CI FAIL——不要静默合并；
  (3) baseline定期自动更新——使用最近7天数据，防止环境漂移；
  (4) 不要手动调整baseline来让CI通过——baseline变更写入audit_log；
  (5) emergency override必须Owner审批——不要自己绕过。

telemetry:
  metrics:
    - {name: "bench_regression_detected", type: counter, labels: [ct_id, metric]}
    - {name: "bench_baseline_drift_pct", type: gauge, labels: [ct_id]}
    - {name: "bench_emergency_override_count", type: counter}
```

---

## 二十六、零停机滚动升级契约 (CT-DEPLOY-001)

> CT-STARTUP从0→启动，但升级不是冷启动——本契约定义"系统运行时如何替换组件"。

```yaml
contract: CT-DEPLOY-001
title: "12系统零停机滚动升级——换引擎不熄火"
principle: "升级单个系统时其他11个系统继续服务——不触发全局block"

deploy_strategies:
  blue_green:
    applicable_to: [context_engine, vector_memory, pipeline, gates]
    mechanism: |
      新版本启动在备用端口→通过CT-HEALTH-001三探针确认ready→
      FeatureFlag(CT-FEATUREFLAG)切换流量到新版本→旧版本等待drain_timeout→关闭
    drain_timeout_s: 30

  rolling_replace:
    applicable_to: [orchestrator, script_system, feedback_loop_engine, telemetry, database]
    mechanism: |
      暂停该系统的IN_PROGRESS任务→标记status=PAUSED_DEPLOY→
      重启该系统→CT-HEALTH readyz=200→恢复PAUSED_DEPLOY任务→清除标记
    max_pause_duration_s: 60

  hot_reload:
    applicable_to: [mcp_adapter, llm_security_gate]
    mechanism: "reload config + re-init internal state——无需重启进程"

pre_deploy_checks:
  - "CT-HEALTH-001: 全部12系统 readyz=200（目标系统除外）"
  - "CT-CDC-001: Can-I-Deploy PASS"
  - "CT-BACKUP-001: 当前备份完整且integrity check PASS"
  - "FeatureFlag: 目标系统的CT-* runtime_enabled=false 已设置（隔离流量）"
  - "DLQ: dlq_depth < 1000——部署前确保没有积压"

post_deploy_checks:
  - "CT-HEALTH: 升级后目标系统 readyz=200（3次连续确认，间隔5s）"
  - "CT-BENCH: 基准退化 < 10%"
  - "FLE: 10分钟观察窗口→无异常检测→标记deploy_successful"
  - "FeatureFlag: 恢复目标系统的CT-* runtime_enabled=true"

rollback_trigger:
  conditions:
    - "post_deploy readyz=503 3次连续→自动回滚"
    - "FLE在10分钟内检测到PERFORMANCE_DEGRADATION→自动回滚"
    - "错误率>基线2x持续5分钟→自动回滚"
  mechanism: "FeatureFlag切回旧版本→CT-STARTUP恢复旧PID→旧版本readyz→清除新版本"

ai_prompt: >
  你是CT-DEPLOY-001的AI agent。当需要升级系统时：
  (1) 升级前跑全部pre_deploy_checks——任一项FAIL→停止部署；
  (2) 使用对应策略(blue_green/rolling_replace/hot_reload)——不要全停机升级；
  (3) 部署后10分钟观察窗口MUST通过——不要"看起来没问题"就标记成功；
  (4) 自动回滚条件触发后立即执行——不要手动延迟回滚期待"可能就恢复了"；
  (5) 部署历史写入deploy_history表→用于审计和回滚决策。

telemetry:
  metrics:
    - {name: "deploy_duration_s", type: histogram, buckets: [10,30,60,120,300]}
    - {name: "deploy_rollback_count", type: counter, labels: [trigger]}
    - {name: "deploy_success_rate", type: gauge}
  traces:
    required_spans: ["deploy_pre_check", "deploy_execute", "deploy_post_observe"]
```

---

## 二十七、数据库Schema演化契约 (CT-SCHEMA-MIGRATE-001)

> 共享Schema(§三)管内存级——本契约管SQLite表结构的forward/backward兼容。

```yaml
contract: CT-SCHEMA-MIGRATE-001
title: "SQLite表结构演化——每个ALTER都有forward和backward路径"
principle: "迁移脚本在版本控制中——CI自动校验migration chain完整性"

migration_format:
  directory: "migrations/"
  naming: "V{SEQ}__{description}.sql"
  chain_validation: "CI检查migration chain连续——无gap→PASS——有gap→FAIL"

rules:
  forward_compat:
    - "新增表→OK——不影响旧版本读取"
    - "新增column→MUST有DEFAULT值→否则旧版本INSERT会失败"
    - "新增NOT NULL column→MUST指定DEFAULT"
    - "修改column type→BREAKING→需要2版本过渡期"
    - "删除column→BREAKING→需要deprecation流程(§三 CTR-VER-001)"
    - "重命名column→BREAKING→等价于删除+新增"
  backward_compat:
    - "每条UP migration→必须有对应的DOWN migration"
    - "DOWN migration在CI中测试——CI verify migration回滚后系统正常"
    - "DOWN不可逆的迁移(如DROP TABLE)→MUST标记 irreversible=true + Owner特批"

migration_state:
  tracking: "db.schema_migrations表——记录已应用的migration序列"
  ci_check: "CI比较db.schema_migrations与migrations/目录→不一致→FAIL"

breaking_change_safety:
  detection: "CI对比migration SQL→检测column_drop/type_change/rename→标记BREAKING"
  gate: "GATE-MIGRATE-1——BREAKING migration需Owner审批确认+30天consumer通知"
  transition_period: "BREAKING字段保留2个MAJOR版本后移除（与§三CTR-VER-001对齐）"

ai_prompt: >
  你是CT-SCHEMA-MIGRATE-001的AI agent。当需要修改SQLite表结构时：
  (1) 每条迁移必须有UP+DOWN——不要写不可逆的迁移除非Owner特批；
  (2) 新增column必须带DEFAULT值——不要创建无默认值的NOT NULL列；
  (3) 不要修改已有column的类型——那是BREAKING change，走deprecation流程；
  (4) CI自动检测BREAKING migration→不要绕过GATE-MIGRATE-1；
  (5) migration chain必须连续——不要跳过V编号导致gap。

telemetry:
  metrics:
    - {name: "migration_executed", type: counter, labels: [version, status]}
    - {name: "migration_rollback_count", type: counter}
    - {name: "migration_chain_gap_detected", type: counter}
```

---

## 二十八、全局降级级联预防 (CT-DEGRADE-CASCADE-001)

> 对标 Netflix Hystrix Request Collapsing + Google Overload Shedding。
> 每个CT-*有独立degrade路径，但当3个系统同时degraded→级联放大→本契约是断路器。

```yaml
contract: CT-DEGRADE-CASCADE-001
title: "全局降级级联预防——防止VMS变慢→CE变慢→Orc假死→Panic Mode"
principle: "系统A degraded→传播给B→B的degradation signal累积权重→超阈值→主动隔离"

cascade_model:
  signal_propagation:
    - from: vector_memory
      to: [context_engine, knowledge_base]
      metric: "vms_search_latency > SLO"
    - from: context_engine
      to: [orchestrator, pipeline]
      metric: "ce_context_build_duration > SLO"
    - from: orchestrator
      to: [gates, feedback_loop_engine]
      metric: "orc_active_tasks_queue > 100"
    - from: feedback_loop_engine
      to: ["*"]
      metric: "panic_mode=activated → 全系统PAUSE"

  degradation_weight:
    each_system_degraded: +1 weight
    threshold: "累计weight ≥ 3 → cascade_protection激活"

cascade_protection_actions:
  level_1_weight_3:
    action: "暂停非P0任务—仅维持HealthCheck+Backup+FLE监控"
    duration: "持续到weight < 2"
  level_2_weight_4:
    action: "断开所有对degraded系统的调用——全部走degrade降级路径"
    duration: "持续到所有degraded→healthy连续3次确认"
  level_3_weight_5:
    action: "Panic Mode(CT-WATCHDOG-001)—全系统暂停—通知Owner"
    duration: "Owner手动恢复"

shedding_strategy:
  overloaded_system: "context_engine"
  trigger: "ce_context_build_duration p99 > 8s"
  action:
    - "CE主动拒绝新的build请求→返回 HTTP 429 Too Many Requests"
    - "Orc收到429→将任务status→QUEUED→等待CE恢复→自动重试"
    - "不丢失任务——只是排队"

ai_prompt: >
  你是CT-DEGRADE-CASCADE-001的AI agent。当你检测到多系统同时degraded时：
  (1) weight≥3→立即激活cascade_protection→不要等待"可能自己恢复"；
  (2) 级联防护期间不要尝试调用degraded系统——走降级路径；
  (3) 不要手动清除weight——weight仅在系统连续3次healthy后自动递减；
  (4) CE overload时主动429→Orc自动QUEUE→不要硬塞请求导致雪崩。

telemetry:
  metrics:
    - {name: "cascade_weight", type: gauge}
    - {name: "cascade_protection_activated", type: counter, labels: [level]}
    - {name: "shedding_429_count", type: counter, labels: [target_system]}
```

---

## 二十九、Owner缺位自治运行 (CT-AUTONOMY-001)

> 对标 Google On-Call Rotation + PagerDuty Escalation Policy。
> 1人+AI模式下bus factor=1——本契约定义"Owner不在时系统怎么自己活着"。

```yaml
contract: CT-AUTONOMY-001
title: "Owner缺位分级自治运行模式——人不在，系统不崩"
principle: "Owner可能休假/出差/生病→系统分级自治→不丢数据不丢任务"

autonomy_levels:
  full_auto:
    description: "系统完全自主——无需Owner确认"
    actions:
      - "每日定时任务: GC(CT-DATA-LIFECYCLE)+Backup(CT-BACKUP)+Housekeeping(CT-HOUSEKEEPING)"
      - "MEDIUM Finding→KE自动入库(CT-SCRIPT-KB-001)"
      - "HealthCheck自动修复(CT-RECONCILE-001)"
      - "FLE异常检测+记录→不执行ESCLATE(保留到Owner回来)"
      - "性能基准baseline自动更新(CT-BENCH-001)"
      - "模型primary不可用→自动fallback(CT-MODEL-REGISTRY-001)"

  supervised:
    description: "AI建议→24h Owner无回复→自动执行"
    actions:
      - "OPS-{SEQ}任务卡创建(CRITICAL/HIGH Finding→修复任务)"
      - "NON-BREAKING Schema变更→新增optional字段"
      - "DLQ replay(积压<5000)"
      - "低风险依赖minor升级(patch version)"
    timeout_hours: 24

  manual_only:
    description: "MUST Owner亲自确认"
    actions:
      - "BREAKING Schema变更→字段删除/类型修改"
      - "Gate阈值调整(CT-FLE-ORC-001)"
      - "内部依赖major升级(minor/major version)"
      - "AI prompt修改(CT-PROMPT-VERSION-001)"
      - "Panic Mode解除(CT-WATCHDOG-001)"
      - "月度成本预算调整(CT-COST-BUDGET-001)"

owner_absence_detection:
  mechanism: "Telemetry追踪Owner最后一次有明确action的时间(last_owner_action_timestamp)"
  absence_levels:
    l1_12h: "飞书通知→'你在吗？有N个supervised建议等待确认'"
    l2_24h: "邮件通知→supervised actions自动开始执行→记录为auto_executed"
    l3_72h: "任务队列freeze——暂停所有非P0 LLM任务——仅维持监控+GC+备份"
    l4_168h: "紧急联系人通知(预设在config/system_config.yaml)→请求手动接管"

escalation_contacts:
  primary: "Owner飞书+邮件"
  fallback_12h: "飞书群通知(如配置)"
  emergency_168h: "预设应急联系人(电话)——仅在l4触发"

autonomy_log:
  table: "autonomy_actions"
  fields: [timestamp, action, autonomy_level, owner_absent_hours, auto_executed, outcome]
  audit: "所有autonomous action永久记录——供Owner回来审查"

ai_prompt: >
  你是CT-AUTONOMY-001的AI agent。当Owner不在时：
  (1) full_auto动作→直接执行→不要等待确认；
  (2) supervised动作→wait 24h→Owner无回复→自动执行→记录auto_executed=true；
  (3) manual_only动作→不解锁不猜测——不要"Owner应该会同意的"；
  (4) l3(72h) task freeze→严格执行——不要因为是P1就继续跑任务；
  (5) autonomy_log不可篡改→Owner回来后能看到发生了什么。

telemetry:
  metrics:
    - {name: "owner_absent_hours", type: gauge}
    - {name: "autonomy_action_executed", type: counter, labels: [level, action]}
    - {name: "escalation_triggered", type: counter, labels: [level]}
```

---

## 三十、AI Agent施工质量闭环 (CT-AGENT-QUALITY-001)

> ZephyrAlpha最根本的风险——AI自己施工但没人评估AI质量。

```yaml
contract: CT-AGENT-QUALITY-001
title: "AI Agent施工质量度量与自我纠正闭环"
principle: "AI agent施工→AI agent自评→CI验证→FLE跟踪→形成改进闭环"

quality_dimensions:
  contract_compliance:
    description: "AI产出的代码是否满足对应CT-*契约"
    measurement: "CI自动运行contract_test(§十)→pass_rate per CT-*"
    target: "contract_test pass_rate > 90%"

  code_correctness:
    description: "AI产出代码的测试覆盖率+test pass率"
    measurement: "pytest coverage + unit/integration test pass rate"
    target: "coverage > 70% + pass_rate > 95%"

  ai_self_assessment:
    description: "AI agent对自己产出的confidence声明"
    mechanism: |
      每次AI生成代码块→附 self_assessment:
        confidence: high/medium/low
        known_risks: ["可能的内存泄漏" / "未处理空输入" / ...]
        manual_review_recommended: true/false
    target: "self_assessment accuracy > 80% (low confidence→实际有bug的比率)"

  regression_risk:
    description: "AI产出是否引入性能退化或breaking change"
    measurement: "CT-BENCH-001 + CT-CDC-001 breaking change detection"
    target: "regression rate < 5%"

quality_scoring:
  per_session_score:
    formula: "0.3*contract_compliance + 0.3*code_correctness + 0.2*self_assessment_accuracy + 0.2*(1-regression_rate)"
    range: "0.0(worst) ~ 1.0(perfect)"
  per_ct_star_score:
    aggregation: "最近10个session的平均quality_score"
    dashboard: "FLE飞书推送Top 5/bottom 5 CT-*质量排行"

improvement_loop:
  low_quality_threshold: 0.5
  action_on_low_quality:
    - "FLE标记该CT-*需要human review"
    - "下次session→CE注入该CT-*的历史失败模式(failure_patterns collection)"
    - "ai_prompt自动追加'上次施工质量低的原因+改进建议'(CT-PROMPT-VERSION-001)"
    - "连续3次low_quality→创建OPS-{SEQ}改进任务卡"

error_propagation_prevention:
  description: "AI错误发现后立即阻断传播"
  mechanism:
    - "AI生成代码merge前→CI运行contract_test+benchmark"
    - "FAIL→阻止merge→标记error_pattern→存入failure_patterns"
    - "下一个AI session→CE注入此error_pattern→避免重复犯错"

ai_prompt: >
  你是CT-AGENT-QUALITY-001的AI agent。每次施工时：
  (1) 生成代码后MUST附 self_assessment——confidence+known_risks+review_recommended→不要只交代码不评估；
  (2) low_confidence的产出MUST标记 manual_review_recommended=true——Owner优先审查；
  (3) 上一个session的quality_score < 0.5→你自动读取failure_patterns→不要重复相同错误；
  (4) CI contract_test FAIL→立即修→不要留到下个session；
  (5) quality_score是你的KPI——持续low→系统会自动标记你需要human review。

telemetry:
  metrics:
    - {name: "agent_quality_score", type: gauge, labels: [ct_id, session_id]}
    - {name: "agent_contract_compliance_rate", type: gauge, labels: [ct_id]}
    - {name: "agent_self_assessment_accuracy", type: gauge, labels: [ct_id]}
    - {name: "agent_error_pattern_discovered", type: counter, labels: [pattern_type]}
```

---

## 三十一、AI Prompt版本演化 (CT-PROMPT-VERSION-001)

> 对标 ML Prompt Engineering as Code + LLM Prompt Version Control（LangSmith/Weights&Biases）。
> 蓝图中54条ai_prompt是活的文本——需要版本化、A/B、回滚。

```yaml
contract: CT-PROMPT-VERSION-001
title: "AI Prompt版本化与A/B测试——prompt作为一等公民"
principle: "Prompt不是随意改的注释——是直接影响AI行为的关键配置——必须版本化"

prompt_versioning:
  storage: ".trae/prompt_versions/{CT_ID}.yaml"
  schema:
    ct_id: "CT-ORC-CE-001"
    current_version: "1.2.0"
    versions:
      - version: "1.2.0"
        date: "2026-05-10"
        author: "Owner"
        change: "新增rule(6)→要求返回source_files字段"
        prompt_text: "> ..."
      - version: "1.1.0"
        date: "2026-05-05"
        author: "Owner"
        change: "初始定义"
        prompt_text: "> ..."
    active: "1.2.0"

ab_testing:
  trigger: "prompt变更→需要验证新prompt是否更优"
  mechanism:
    - "创建 experiment: {CT_ID}_v{new_version}"
    - "50% session用旧prompt, 50%用新prompt(随机分配)"
    - "收集quality_score(CT-AGENT-QUALITY-001)→统计显著性检验"
    - "p < 0.05 且新prompt quality > 旧→自动切换为新prompt"
    - "p < 0.05 且新prompt quality < 旧→丢弃新prompt→保留旧版本"
    - "不显著→延长实验→最多2周→超时仍不显著→保留旧prompt(保守原则)"
  min_sample_size: 20

prompt_rollback:
  trigger: "新prompt质量显著下降 OR Owner手动触发"
  mechanism: "设置 active=回退版本号→下次session自动使用旧prompt"
  audit: "回退原因写入prompt_version_history"

prompt_quality_trend:
  tracking: "每条prompt version→关联session的quality_score时序"
  ci_alert: "连续10个session quality下降→自动触发prompt review提醒"

ai_prompt: >
  你是CT-PROMPT-VERSION-001的AI agent。管理prompt变更时：
  (1) 每次修改prompt→必须记录version+date+author+change+前版本diff；
  (2) 不要在没有A/B实验的情况下切换默认prompt版本；
  (3) A/B实验至少收集20个session→不要提前结束因为"看起来差不多"；
  (4) 新prompt显著更差→立即回滚→不要"再观察看看"；
  (5) prompt版本历史永久保留→用于追溯"哪些prompt产生了哪些bug"。

telemetry:
  metrics:
    - {name: "prompt_version_active", type: gauge, labels: [ct_id]}
    - {name: "prompt_ab_experiment_quality_diff", type: gauge, labels: [ct_id, experiment_id]}
    - {name: "prompt_rollback_count", type: counter, labels: [ct_id]}
```

---

## 三十二、并行AI Session冲突预防 (CT-SESSION-CONFLICT-001)

> 对标 无现有方案（Cursor/Windsurf多agent窗口无冲突预防）。
> 100%AI施工→Owner可能同时开2+ AI窗口→并行施工产生merge冲突→本契约事前预防。

```yaml
contract: CT-SESSION-CONFLICT-001
title: "并行AI Session文件访问协调——两个AI不同时改同一个文件"
principle: "Session启动时声明'I will touch these files'→其他session看到→协商文件访问范围"

session_registry:
  location: ".trae/session_state/active_sessions/"
  per_session_file: "session_{session_id}.yaml"
  schema:
    session_id: "uuid7"
    ct_id_focus: "CT-ORC-CE-001"
    started_at: "ISO8601"
    files_to_touch:
      - path: "src/zephyr/orchestration/context_management/builder.py"
        operation: "modify"
    estimated_duration_minutes: 30
    session_manifest_path: ".trae/session_state/CT-ORC-CE-001_progress.yaml"

conflict_detection:
  mechanism: |
    Session B启动→扫描active_sessions/→
    若同CT-*→检查files_to_touch→
    若有重叠→CONFLICT_WARN→提供选项
  resolution_options:
    option_1: "Session B wait→轮询Session A completion→A结束后B自动启动"
    option_2: "Session B缩小范围→避开重叠文件→仅处理disjoint文件集"
    option_3: "Owner manual override→Owner确认可并行→两个session互知对方的存在"
  default: "option_1 (safe)——除非Owner选option_3"

cross_ct_conflict:
  scenario: "Session A on CT-ORC-CE-001, Session B on CT-CE-LSG-001→共享context_engine依赖"
  check: "B启动时检查A的files_to_touch→CT-CE-LSG-001的依赖(context_engine)是否被A改动"
  action: "若A已经改了context_engine→B读取最新状态→若A还未完成→B wait或仅写测试"

session_cleanup:
  on_complete: "session更新handoff manifest(CT-SESSION-handoff-001)→从active_sessions/中删除自身"
  on_timeout: "estimated_duration过期+15分钟→标记STALE→提醒Owner→Owner未回复→标记FORCE_CLOSE"
  orphan_detection: "housekeeping扫描active_sessions/→>12h未更新→标记ORPHAN→通知Owner"

ai_prompt: >
  你是CT-SESSION-CONFLICT-001的AI agent。AI session启动时：
  (1) 首先扫描active_sessions/→声明自己的files_to_touch→检测冲突；
  (2) 同CT-*有活跃session→默认wait(option_1)→不要假设"我可以同时改"；
  (3) 跨CT-*但共享依赖→读取活跃session的最新产品→不要基于过时的代码施工；
  (4) 冲突无法解决→请求Owner manual override→不要自己决定；
  (5) session结束后清理active_sessions/→不要留下幽灵session阻塞后续施工。

telemetry:
  metrics:
    - {name: "session_conflict_detected", type: counter, labels: [resolution]}
    - {name: "active_sessions_count", type: gauge}
    - {name: "session_wait_duration_minutes", type: histogram, buckets: [1,5,15,30,60]}
```

---

## 三十三、死代码与孤儿资源清理 (CT-LEAN-001)

> 对标 Google Code Health（Dead Code Elimination）+ internal unused-import linter。
> CT-KISS限制新代码→本契约清理死代码→6个月后不变成垃圾场。

```yaml
contract: CT-LEAN-001
title: "死代码与孤儿资源检测——每周自动清理无用代码和数据"
principle: "AI重构频繁→死代码累积比手写代码快10x——每周清扫是刚需"

dead_code_detection:
  tools:
    - {name: "vulture", target: "unused Python code (functions/classes/variables)", threshold: 0}
    - {name: "import-linter", target: "circular imports + unused imports"}
    - {name: "pytest --dead-fixtures", target: "tests that use fixtures that no longer exist"}
    - {name: "coverage combine", target: "code never reached by any test"}

  schedule: "每周日凌晨 01:00"
  action_on_dead_code:
    immediate_report: "生成 dead_code_report.md → 推送Owner飞书"
    auto_deprecate: "任何Python模块30天无import→标记 @deprecated → 追加注释 'AUTO_FLAGGED_BY_CT-LEAN-001'"
    auto_delete: "标记 @deprecated 后60天→自动删除+记录DELETE audit_log"
    exception: "Owner可手动标记 KEEP_FOREVER——跳过检测"

orphan_resource_detection:
  chromadb:
    check: "collection无对应CT-*活跃契约引用→标记ORPHAN"
    grace_period_days: 90
    action: "90天后→通知Owner→Owner确认/未回复→drop collection→记录audit_log"

  test_files:
    check: "test文件对应的source module已不存在→标记ORPHAN_TEST"
    action: "立即通知Owner→30天Owner未处理→archive→移到 tests/archive/"

  dead_imports:
    check: "import语句引用的模块/类已不存在→CI FAIL"
    gate: "GATE-LEAN-1——pre-commit阶段检测dead imports→FAIL→阻止commit"

bloat_check:
  module_size_kb: 50
  function_lines: 100
  class_methods: 20
  action: "超标→CI WARN + 提示CT-KISS-001约束"

ai_prompt: >
  你是CT-LEAN-001的AI agent。保持系统苗条：
  (1) 每周扫描死代码→生成报告→自动标记30天未使用的模块；
  (2) 不要因为"可能以后会用到"而保留死代码——真正需要时从git history恢复；
  (3) GATE-LEAN-1 dead import检测是硬门禁→不要绕过；
  (4) Orphan ChromaDB collection 90天未用→通知Owner→直接drop；
  (5) bloat check超标→不要添加更多代码——先重构或拆分。

telemetry:
  metrics:
    - {name: "dead_code_items_found", type: counter, labels: [type]}
    - {name: "dead_code_items_removed", type: counter, labels: [type]}
    - {name: "orphan_collections_count", type: gauge}
    - {name: "module_bloat_warnings", type: counter, labels: [module]}
```

---

## 三十四、蓝图自健康诊断 (CT-BLUEPRINT-HEALTH-001)

> 蓝图定义了一切怎么健康——谁检查蓝图本身是否健康？

```yaml
contract: CT-BLUEPRINT-HEALTH-001
title: "蓝图自健康诊断——契约与实现的一致性是蓝图的KPI"
principle: "蓝图健康=所有CT-*契约与磁盘代码一致→不一致=蓝图患了'谎话症'"

health_dimensions:
  code_contract_consistency:
    description: "蓝图声称的接口签名与磁盘实现是否一致"
    mechanism: "validate_integration_consistency.py(§十二)→对比蓝图CT-* YAML与代码中的@compliance标记"
    gate: "GATE-BLUEPRINT-1——不一致→CI FAIL"
    severity: P0

  path_existence:
    description: "蓝图中引用的文件路径是否存在"
    mechanism: "CI扫描蓝图全文→提取所有文件路径→检查磁盘→不存在→CI FAIL"
    scope: "所有§1路径索引 + 所有CT-*契约中引用的path字段"
    severity: P0

  contract_coverage:
    description: "12×11=132个可能的系统交互对→哪些已登记CT-*→哪些豁免→哪些是盲区"
    mechanism: |
      生成 coverage_matrix: 12系统×12系统 →
      每个格子状态: [COVERED_BY_CT_id, EXPLICITLY_EXEMPTED(no interaction), UNCOVERED_GAP]
    gate: "UNCOVERED_GAP存在→CI WARN + 要求补充CT-*或声明豁免理由"
    severity: P1

  staleness_detection:
    description: "CT-*契约是否仍然活跃——6个月未更新的契约可能是死契约"
    mechanism: "CI检查每条CT-*的last_modified→>180天→标记STALE→通知Owner"
    action_on_stale: "Owner确认:(1)仍活跃→刷新last_modified (2)已废弃→标记@deprecated (3)删除"

  cross_reference_integrity:
    description: "蓝图中所有内部引用是否有效——§X→CT-Y→SCHEMA-Z"
    mechanism: "CI解析蓝图全文→构建引用图→检测broken link→CI FAIL"
    scope: "所有 '详见§*'、'参照CT-*'、'引用SCHEMA-*' 的内部交叉引用"

  version_consistency:
    description: "蓝图声明的version是否与各子系统的compliance一致"
    mechanism: "CI扫描代码中@compliance(version='X.Y.Z')→与蓝图frontmatter比较→不一致→CI FAIL"

annual_blueprint_audit:
  trigger: "距离上次audit 365天"
  actions:
    - "运行全部5项health_dimensions→生成blueprint_health_report.md"
    - "遍历所有CT-*契约→对比CT-AGENT-QUALITY-001质量趋势→标记低质量CT-*"
    - "Owner逐条review STALE契约→decision: keep/deprecate/delete"
    - "audit结果存入KB→KE类型=BLUEPRINT_AUDIT"

ai_prompt: >
  你是CT-BLUEPRINT-HEALTH-001的AI agent。维护蓝图健康：
  (1) 蓝图修改后→CI自动运行全部5项health check→任一项FAIL→不合并；
  (2) 蓝图引用的文件路径MUST存在→如果你删了某个文件→同时更新蓝图；
  (3) 6个月未更新的CT-*→标记STALE→提醒Owner审查→不要假设"没改就是对的"；
  (4) contract_coverage中的UNCOVERED_GAP→补充CT-*或写豁免声明→不要留盲区；
  (5) 年度蓝图审计是硬性任务→不要跳过。

telemetry:
  metrics:
    - {name: "blueprint_health_score", type: gauge}
    - {name: "blueprint_stale_contracts", type: gauge}
    - {name: "blueprint_uncovered_gaps", type: counter}
    - {name: "blueprint_broken_references", type: counter}
```

---

## 三十五、系统移交/迁移协议 (CT-TRANSFER-001)

> 对标 Disaster Recovery Runbook + Infrastructure as Code (Terraform state transfer)。
> bus factor=1→当Owner换电脑/换人/上服务器→系统必须能一键迁移。

```yaml
contract: CT-TRANSFER-001
title: "ZephyrAlpha完整移交与迁移协议——打包、转移、验证、恢复"
principle: "1个命令打包整个系统→1个命令在新环境恢复→自动验证完整性"

transfer_package:
  command: "python scripts/governance/transfer/package_system.py"
  output: "zephyr_alpha_{date}.tar.gz"
  contents:
    - "源代码: git archive HEAD → src/"
    - "数据: SQLite VACUUM INTO + ChromaDB zip"
    - "密钥: .env（原样——这是为什么不建议放git但需要手工copy）"
    - "Session状态: .trae/session_state/ 全目录"
    - "配置文件: config/ 全目录（含dev/prod差异）"
    - "审计日志: .audit_cache/ 全目录"
    - "基准数据: .audit_cache/benchmarks/"
    - "依赖: pip freeze > requirements_frozen.txt"
    - "迁移manifest: transfermanifest.yaml——包含所有文件的checksum(SHA256)"

unpack_and_restore:
  command: "python scripts/governance/transfer/restore_system.py"
  steps:
    - "解压 tar.gz"
    - "校验 transfermanifest.yaml——所有文件SHA256一致→CONTINUE→不一致→ABORT"
    - "pip install -r requirements_frozen.txt"
    - "复制 .env 到目标位置"
    - "恢复SQLite db→PRAGMA integrity_check→PASS"
    - "恢复ChromaDB→test query→PASS"
    - "恢复session_state/ 目录→CI验证handoff chain完整性"
    - "运行CT-HEALTH-001全部12系统探针→全部readyz=200→恢复完成"
    - "运行CT-BENCH-001→确认性能无退化"

transfer_validation:
  smoke_test: "运行 GATE-IT-SMOKE(§十) + GATE-IT-HEALTH"
  data_integrity: "SQLite checksum + ChromaDB document count一致性"
  functionality: "创建1个测试TaskCard→走完DRAFT→TODO→IN_PROGRESS→COMPLETED全流程"

transfer_audit:
  record: "transfer_history表——记录每次迁移的时间、来源、目标、验证结果"
  retention: "保留最近5次迁移记录——供回滚到之前的迁移点"

ai_prompt: >
  你是CT-TRANSFER-001的AI agent。当需要迁移系统时：
  (1) package→verify→transfer→restore→verify→smoke_test——不要跳过任何步骤；
  (2) transfer_manifest的SHA256校验MUST全部通过→不一致→ABORT——不要"这点小差异没关系"；
  (3) 恢复后12系统readyz MUST全部200→不满足→回退到旧环境；
  (4) 迁移完成必须运行smoke_test→全流程TaskCard走一遍→确认可用；
  (5) .env文件需要手工处理——不要在打包文件中明文存储到公开位置。

telemetry:
  metrics:
    - {name: "transfer_executed", type: counter, labels: [status]}
    - {name: "transfer_validation_checks_pass", type: gauge}
    - {name: "transfer_data_loss_bytes", type: gauge}
```

---

## 三十六、知识质量评分 (CT-KE-QUALITY-001)

> 对标 Google Knowledge Graph Quality Signals + Amazon Product Knowledge Utility Scoring。
> CT-KNOWLEDGE-FRESHNESS只管"是否过时"→本契约管"是否好用"。

```yaml
contract: CT-KE-QUALITY-001
title: "知识条目质量评分——好看的不一定有用，有用的才是好知识"
principle: "KE的质量不是由创建者决定的——是由消费者(CE+AI agent)用脚投票的"

quality_signals:
  retrieval_frequency:
    description: "被CE context builder检索的次数"
    weight: 0.25
    scoring: "log2(retrieval_count+1) / log2(max_retrieval_count+1) → 归一化"

  task_association_success:
    description: "使用此KE的任务的完成率"
    weight: 0.35
    mechanism: "CE每次注入KE→记录ke_id→任务完成后→标记contributed_to_success/failure"
    scoring: "successful_tasks / total_tasks_used_this_ke"

  human_feedback:
    description: "Owner显式评价"
    weight: 0.20
    values: {useful: 1.0, neutral: 0.5, misleading: 0.0, obsolete: 0.0}
    default: "neutral (0.5)——未评价的默认中性"

  semantic_density:
    description: "信息密度——惩罚水词和模板化文本"
    weight: 0.10
    mechanism: "KE内容长度 vs 有效实体(技术术语/代码片段/架构概念)比率"
    scoring: "min(1.0, useful_entity_count / (text_length_chars / 100))"

  freshness_correlation:
    description: "KE新鲜度×质量的综合——两者独立但交互"
    weight: 0.10
    mechanism: "CT-KNOWLEDGE-FRESHNESS-001状态转换时触发重评分"

quality_thresholds:
  high_quality: "score > 0.6 → CE正常注入+优先排序"
  medium_quality: "score 0.3-0.6 → CE正常注入+标准排序+附带 ⚠️ quality_warning"
  low_quality: "score < 0.3 → CE排除——除非查询显式include_low_quality=true"
  unrated: "新KE默认0.4(medium起始)——10次检索或30天后重评分"

quality_dashboard:
  report: "FLE飞书推送每周KE质量报告——Top 10高分+Bottom 10低分"
  action_on_bottom: "连续4周在bottom 10→自动标记DEPRECATED→通知Owner"

ke_quality_improvement:
  trigger: "KE marked as low_quality"
  suggestion: "AI分析该KE→建议: 合并到其他KE / 更新过时内容 / 拆分过长KE / 标记废弃"
  automation: "建议需Owner确认——不自动修改KE内容"

ai_prompt: >
  你是CT-KE-QUALITY-001的AI agent。在上下文中注入KE时：
  (1) high_quality(>0.6)KE优先注入→放在context的前面→这些是最有用的知识；
  (2) low_quality(<0.3)KE不注入→除非任务显式要求"include all knowledge"；
  (3) 每个任务完成后→标记使用了哪些KE→成功/失败→为quality scoring贡献反馈数据；
  (4) 新KE进入30天观察期→不急于评分→10次检索后再定论；
  (5) 低质量不等于无效——可能只是"太新还没被用"或"领域太窄"——不要误杀。

telemetry:
  metrics:
    - {name: "ke_quality_score", type: gauge, labels: [ke_id]}
    - {name: "ke_retrieval_count", type: counter, labels: [ke_id]}
    - {name: "ke_task_success_correlation", type: gauge, labels: [ke_id]}
    - {name: "ke_quality_distribution", type: histogram, buckets: [0,0.2,0.4,0.6,0.8,1.0]}
```

---
---

## 三十七、深度交叉审计盲点全注入 (Round 5) —— 7大维度35盲点

> **定位**：v0.9.0 基于专业机构（Google SRE/Two Sigma/Jane Street/Anthropic）和氛围编程社区（Cursor/Windsurf/Anthropic）的交叉视角，对已完成的 54条CT-* + ~300盲点进行全面纵深审计，发现**7个未被覆盖或覆盖不足的维度**，注入35个新盲点。
>
> **审计方法**：将蓝图放到"100%AI施工 + 1人+AI维护 + 金融量化业务"的真实场景中做压力测试——如果明天开始用这套蓝图指挥AI施工，AI会在哪里犯错？Owner会在哪里被蒙蔽？系统会在哪里悄悄腐烂？
>
> **核心发现**：蓝图的设计完备性达到 ~92/100（世界级），但可执行性仅 ~15/100（53/54条CT-*为DO_NOT_CALL）。蓝图的高质量本身制造了"虚假完整感"——这是最深层的元盲点。

### 37.1 审计结果全景矩阵

| 维度 | 盲点数 | 严重度分布 | 核心风险 |
|------|:--:|------|------|
| **A. 测试与质量** | 6 | P0×2 / P1×2 / P2×2 | AI施工后缺乏自动化质量关卡 |
| **B. 可观测性** | 5 | P0×1 / P1×2 / P2×2 | System Telemetry仅50%且零数据采集 |
| **C. 安全纵深** | 5 | P0×2 / P1×3 | Supply Chain安全与AI副作用验证完全空白 |
| **D. 运维自动化** | 5 | P0×3 / P2×2 | Bus factor=1场景下Owner认知恢复无协议 |
| **E. 氛围编程特有** | 7 | P0×4 / P1×3 | AI施工节奏/疲劳/跨Session一致性无管控 |
| **F. 金融业务** | 4 | P0×2 / P1×2 | 模型风险治理/实盘硬断路器完全缺失 |
| **G. 蓝图自身体系** | 3 | P1×1 / P2×2 | 蓝图膨胀无管控、影响力分析缺失 |

### 37.2 A. 测试与质量盲点（6个）

> **对标**：Google Presubmit + Jane Street Property-Based Testing + Netflix Chaos Engineering。
> **现状**：CT-CDC-001/CT-CHAOS-001/CT-CANARY-001 均为 DO_NOT_CALL。AI施工后无自动化质量关卡——这是当前最高风险盲区。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 1 | **B-MOD-301** | **无AI施工"冒烟测试"关卡**——每次AI变更后没有自动运行最小可运行验证就合并，高风险变更静默进入代码库 | 4 | 4 | 3 | **48** 🔴 | 每次AI session产生产出 |
| 2 | **B-MOD-302** | **无Property-Based Testing**——AI生成的代码容易通过单元测试但有隐藏边界bug（如None输入/空列表/极大值），传统example-based test无法覆盖 | 3 | 3 | 3 | 27 🟠 | AI生成工具函数/数据处理 |
| 3 | **B-MOD-303** | **无Golden File Test（金标准）**——因子计算/风控计算应有一组已知正确答案（ground truth）对照，AI修改公式后可能静默改变输出 | 5 | 2 | 4 | 40 🔴 | AI修改因子/风控核心逻辑 |
| 4 | **B-MOD-304** | **无Chaos Engineering故障注入清单**——CT-CHAOS-001定义了但无具体注入点（磁盘满/内存不足/进程崩溃/网络延迟）×（12系统）矩阵 | 3 | 2 | 3 | 18 🟡 | 生产环境不可预期故障 |
| 5 | **B-MOD-305** | **无Regression Test Selection（智能选测）**——改一个模块跑全部测试太慢，需要依赖图分析只跑受影响的测试子集 | 2 | 3 | 3 | 18 🟡 | 项目规模增长后CI变慢 |
| 6 | **B-MOD-306** | **无Flaky Test Detection**——间歇性失败的测试会毒化CI信任（"这个测试偶尔红，忽略就好"→真正的bug也被忽略） | 2 | 4 | 3 | 24 🟠 | 异步/时间相关测试 |

### 37.3 B. 可观测性盲点（5个）

> **对标**：FinOps FOCUS + Google SRE Four Golden Signals + Anthropic Context Engineering。
> **现状**：System Telemetry仅50%且零实际数据采集。成本花了但不知道买了什么，质量变了但不知道趋势。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 7 | **B-MOD-307** | **无AI Token"单位产出"度量**——知道花了¥30/月，但不知道每¥1产出了多少有效代码行/功能点/修复Bug数。ROI完全黑盒 | 3 | 4 | 4 | 48 🔴 | 每月审视成本 |
| 8 | **B-MOD-308** | **无Session有效性度量**——AI session中有多少Token是"真正干活"vs"绕圈子/卡住/幻觉纠正"。无法判断AI效率趋势 | 3 | 4 | 3 | 36 🔴 | 每次长session |
| 9 | **B-MOD-309** | **无Blueprint↔Code漂移可视化面板**——52%平均完整度意味着48%是蓝图写了代码没有。这个差距的缩小/扩大趋势需要可视化 | 2 | 3 | 2 | 12 🟡 | 每周审视进度 |
| 10 | **B-MOD-310** | **无AI行为质量的时间序列档案**——AI在M1阶段产出的代码质量 vs M2/M3/M4应该呈上升趋势。没有基准就无法判断"AI越来越好了吗？" | 2 | 3 | 3 | 18 🟡 | 长期维护 |
| 11 | **B-MOD-311** | **无"系统熵增"度量**——随着AI不断施工，系统的混乱度（重复代码/死代码/蓝图代码不一致/循环依赖）是否在增长？需要量化趋势 | 4 | 4 | 4 | 64 🔴 | 氛围编程结构风险最大项 |

### 37.4 C. 安全纵深盲点（5个）

> **对标**：OWASP Top 10 for LLM + Zero Trust Architecture + AWS Secrets Manager。
> **现状**：LLM Security四层防御定义了但LSG模块仅65%。Supply Chain和AI副作用验证完全空白。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 12 | **B-MOD-312** | **无AI Agent"最小权限"动态评估**——Agent RBAC规划中，但没有"当前session实际需要什么权限 vs 被授予了什么权限"的diff审计 | 3 | 3 | 3 | 27 🟠 | 每次Agent请求权限 |
| 13 | **B-MOD-313** | **无Dependency Supply Chain安全扫描**——pip依赖的已知漏洞扫描（Safety/Snyk/Dependabot集成）。AI可能引入有漏洞的第三方库 | 4 | 3 | 3 | 36 🔴 | AI添加新依赖 |
| 14 | **B-MOD-314** | **无AI Prompt注入的自动化Fuzzing测试**——应该用另一个AI专门攻击自己的prompt来找注入漏洞。被注入的prompt可能导致AI删除文件/泄露数据 | 4 | 2 | 4 | 32 🔴 | 外部输入进入prompt |
| 15 | **B-MOD-315** | **无LLM输出→系统状态的实际副作用验证**——AI调用FileWrite/ShellExecute→实际文件变化→验证是否与AI声称的一致。AI可能静默修改了不该改的文件 | 5 | 3 | 4 | 60 🔴 | 每次AI执行写操作 |
| 16 | **B-MOD-316** | **无Secrets生命周期管理**——Secrets Manager已定义但缺：轮换策略/泄露检测/使用审计/过期提醒/零化确认 | 4 | 2 | 3 | 24 🟠 | 生产环境密钥管理 |

### 37.5 D. 运维自动化盲点（5个）

> **对标**：PagerDuty On-Call + AWS Well-Architected Tool + SQLite Production Operations。
> **现状**：启停6 Phase DAG是亮点但多数DO_NOT_CALL。Bus factor=1场景下Owner认知恢复和日常巡检完全依赖人脑记忆。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 17 | **B-MOD-317** | **无G6 REJECT后的Session自动恢复链**——AI被G6硬门禁拒绝后，下一个session需要知道：为什么被拒、修了什么、是否可以继续。否则下个AI从零开始重复犯错 | 3 | 5 | 3 | 45 🔴 | 高频——每天可能发生 |
| 18 | **B-MOD-318** | **无系统"一键健康检查"命令**——Owner每天早上打开IDE应跑一个命令看到：🟢🟡🔴12系统健康面板+建议动作TOP3。不要让Owner/AI读752行蓝图来判断健康 | 3 | 5 | 3 | 45 🔴 | 每天 |
| 19 | **B-MOD-319** | **无"Owner认知恢复协议"**——出差/休假2周回来，大脑已忘记系统全貌。需要一个"你离开期间发生了什么"的AI自动生成摘要 | 4 | 4 | 3 | 48 🔴 | Bus factor=1真实场景 |
| 20 | **B-MOD-320** | **无磁盘空间监控与自动清理联动**——CT-DISK-GUARD仅检测但不触发CT-LEAN清理，需要闭环联动 | 2 | 3 | 2 | 12 🟡 | 长期运行 |
| 21 | **B-MOD-321** | **无数据库真空操作自动化调度**——SQLite长期高频写入后需要VACUUM/ANALYZE/PRAGMA integrity_check，没有自动调度 | 2 | 3 | 2 | 12 🟡 | 长期运行 |

### 37.6 E. 氛围编程特有盲点（7个）

> **对标**：无——本维度是ZephyrAlpha特化盲区。专业机构不靠vibe coding，氛围编程社区尚无成熟方法论。
> **现状**：§十五定义了M1-M4成熟度+9指令+8失败模式，但以下执行层盲点未被契约覆盖。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 22 | **B-MOD-322** | **无AI"施工节奏"强制执行**——M1模块应每天≤3文件变更，M3可>10。§15.1定义了策略但无运行时强制。AI会以M4的速度施工M1的模块→一次性改20个文件全搞砸 | 4 | 5 | 3 | 60 🔴 | M1/M2模块施工 |
| 23 | **B-MOD-323** | **无"AI疲劳检测"**——同一session内AI产出质量随Token消耗下降。拐点在哪？30分钟？100K tokens？需要量化并在拐点前提醒Owner新建session | 3 | 4 | 3 | 36 🔴 | 长session |
| 24 | **B-MOD-324** | **无"上下文切换成本"度量**——AI在多个模块间跳跃施工 vs 专注一个模块，质量差异有多大？需要数据支撑"串行vs并行"的策略决策 | 2 | 3 | 3 | 18 🟡 | 多任务并行 |
| 25 | **B-MOD-325** | **无"AI建议采纳率"追踪**——AI提出的建议，Owner接受了多少/拒绝了多少/修改后接受多少。反映AI的决策质量和AI-Owner协作成熟度 | 2 | 3 | 3 | 18 🟡 | Human-AI协作 |
| 26 | **B-MOD-326** | **无"跨Session设计一致性"校验**——同一个模块，周一施工的AI和周三施工的AI可能做出矛盾的设计决策。需要在Session启动时注入"上一次施工的决策记录" | 4 | 4 | 4 | 64 🔴 | 多session施工同一模块 |
| 27 | **B-MOD-327** | **无"蓝图Token预算vs实际消耗"反馈回路**——蓝图声明8000 token预算，但每次实际注入多少？命中率多少？需要闭环反馈驱动预算优化 | 2 | 3 | 3 | 18 🟡 | Context Engine运行时 |
| 28 | **B-MOD-328** | **无"AI暗知识传递"漏洞**——某个session的AI发现了架构问题但没有强制写入蓝图/Handoff，下个AI永远不知道 | 4 | 4 | 4 | 64 🔴 | 任何非平凡session |

### 37.7 F. 金融业务特有盲点（4个）

> **对标**：SEC Market Access Rule + Two Sigma Model Risk Management + Marcos Lopez de Prado 量化方法论。
> **现状**：C-Track 14层中9层为skeleton。D_SIGNAL/D_RISK虽有代码但缺乏模型治理和实盘保护。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 29 | **B-MOD-329** | **无交易策略渐进式上线路径**——因子/策略从创建→回测→paper trading→小仓位→全仓位的生命周期管理。AI可能直接从回测跳到实盘 | 5 | 3 | 3 | 45 🔴 | 策略上线 |
| 30 | **B-MOD-330** | **无实时风险敞口硬限制**——不依赖AI/风控模块判断的运行时硬断路器："无论发生什么都不可越过这个position limit/leverage cap/cash reserve floor" | 5 | 2 | 2 | 20 🟠 | 市场剧烈波动 |
| 31 | **B-MOD-331** | **无市场异常自动熔断**——闪崩/流动性枯竭/波动率突然爆发→自动减仓或停止交易。需要独立于主风控模块的旁路监控 | 5 | 2 | 2 | 20 🟠 | 黑天鹅事件 |
| 32 | **B-MOD-332** | **无回测过拟合检测**——AI优化因子时天然容易过拟合历史数据（特别是深度AI），需要：Deflated Sharpe Ratio/Probabilistic Sharpe Ratio/CSCV等检验 | 4 | 3 | 3 | 36 🔴 | AI迭代优化因子 |

### 37.8 G. 蓝图自身体系盲点（3个）

> **对标**：无——这是元层的终极问题。蓝图定义了一切怎么健康，但蓝图本身也需要健康管控。
> **现状**：CT-BLUEPRINT-HEALTH已定义5维度诊断（v0.8.0），但以下3项超越诊断维度——是结构性风险。

| # | 盲点ID | 盲点描述 | S | O | D | RPN | 触发场景 |
|:--|:--|------|:--:|:--:|:--:|:--:|------|
| 33 | **B-MOD-333** | **蓝图自身膨胀无管控**——SYS-MASTER从0.1.0→0.5.0增长4倍，MOD-MASTER从0.1.0→0.9.0持续膨胀。CT-KISS控制了代码膨胀但无人控制蓝图膨胀。蓝图的Token冷启动Budget(~400)正在被侵蚀 | 2 | 4 | 4 | 32 🟠 | 每次蓝图扩写 |
| 34 | **B-MOD-334** | **无蓝图"影响力分析"**——修改一条CT-*契约影响哪些模块？哪些AI行为会改变？没有依赖追踪和影响传播范围评估 | 3 | 3 | 3 | 27 🟠 | 契约变更 |
| 35 | **B-MOD-335** | **无蓝图与外部标准的合规映射矩阵**——ISO 27001/ISO 42001/MiFID II/NIST AI RMF 各控制项对应蓝图的哪个§/哪条CT-*？监管审计时需要这份可追溯性矩阵 | 2 | 2 | 4 | 16 🟡 | 合规审计 |

### 37.9 35盲点汇总与优先级

| 优先级 | 计数 | 盲点列表 | 建议响应时间 |
|:--|:--:|------|:--:|
| 🔴 P0 | **16** | B301, B303, B307, B308, B311, B313, B314, B315, B317, B318, B319, B322, B323, B326, B328, B332 | 本轮立即施工 |
| 🟠 P1 | **12** | B302, B306, B312, B316, B325, B329, B330, B331, B333, B334 | Phase 2 |
| 🟡 P2 | **7** | B304, B305, B309, B310, B320, B321, B324, B327, B335 | Phase 3 |

> **1人+AI施工策略**：16个P0盲点不需要全部独立开发——其中B303/B307/B308/B311/B315/B317/B318/B319/B322/B326/B328（11个）可以通过扩展现有模块实现（Telemetry采集+Context Engine增强+Script System新维度审计），而非新建模块。

### 37.10 1人+AI的生存三法则（非盲点，施工指引）

**法则1：Owner的能量预算管理**
```
Owner每天有有限的"决策能量"。
AI不应每天抛出10个"你选A还是B？"的问题——会耗尽Owner的决策意志。
定义AI自主决策比例的渐进提升路径：
  beta阶段：   AI自主决策30%，70% ASK Owner
  stable阶段： AI自主决策70%，30% ASK Owner
  production： AI自主决策90%，10% ASK Owner（仅P0事务）
监控： "每日ASK次数"指标——超过阈值→AI需要改进自主决策能力
```

**法则2：系统的自我解释能力**
```
AI每次被问"系统当前状态"时必须能在30秒~2分钟内输出摘要。
对标 AWS Well-Architected Tool 的 review 输出格式：
  (1) 总体健康分 + 趋势箭头
  (2) TOP3 风险 + 建议动作
  (3) 最近变更摘要
  (4) 需要Owner关注的事项（≤3项）
```

**法则3：系统降级运行三模式**
```
  FULL（生产）：   全部CT-*在线——策略实盘/实盘风控
  CORE（日常开发）：核心15条CT-*在线——Orc/CE/Gate/Script/DB/FLE
  MINIMAL（紧急）： 仅5条CT-*在线——Health/Gate/DB/Backup/Watchdog
                 → Owner出差/系统故障时的生存底线
切换条件：手动触发 OR CT-AUTONOMY-001 l3(72h)自动触发
```

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 12 系统集成契约（CT-*） | **本文档 §二** | — |
| 共享 Schema | **本文档 §二** | — |
| CBAC 能力矩阵 | MOD-MASTER_BLUEPRINT-AGENT-SPEC §十五 | — |
| 容量升级设计 | MOD-MASTER_BLUEPRINT-CAPACITY §-1/§-2 | — |

**任何与本蓝图冲突的集成定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-MASTER_BLUEPRINT-CAPACITY | 基线设计+契约定义 |
| Tier 1 | MOD-MASTER_BLUEPRINT-AGENT-SPEC | CT-* 契约→CBAC 矩阵 |
| Tier 1 | 各模块蓝图（MOD-INF-*） | CT-* 契约编号 |
| Tier 2 | INF-020 Audit Trail | 审计事件 |
| Tier 2 | INF-021 Rollback | 回滚点 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| CT-* 契约变更 | 通知所有模块蓝图+CBAC | 更新 circuit_breaker.py |
| 共享 Schema 变更 | 通知 PS-STD-001 | 更新 TaskRepository |
| 架构原则变更 | 通知 capacity 蓝图 | 更新调度器 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 新增 CT-* 契约 | AI 可自主 |
| 修改已有 CT-* 契约 | 需 Owner 审批 + 通知所有消费者 |
| 删除 CT-* 契约 | 需 Owner 审批 + 确认无消费者 |
| 架构原则变更 | 需 Owner 审批 |

### 负向责任

| # | 本蓝图不涉及 | 由谁负责 |
|---|-------------|---------|
| 1 | 各模块的具体实现代码 | 各模块蓝图 (MOD-INF-*) 负责 |
| 2 | 容量升级设计 | MOD-MASTER_BLUEPRINT-CAPACITY 负责 |
| 3 | CBAC 能力矩阵实现 | MOD-MASTER_BLUEPRINT-AGENT-SPEC 负责 |
| 4 | 施工落地步骤 | 各模块蓝图 §16 负责 |

### 触发条件

| 场景 | AI 应读取本蓝图 |
|------|---------------|
| 新 AI session 冷启动 | 读 §零 分派表 + §二 CT-* 契约总表 |
| 模块开发需查跨系统契约 | 读 §二 找对应 CT-* 编号 |
| 跨系统集成测试前 | 读 §四 架构原则 + §二 契约约束 |
| 系统规模接近容量预算 | 读 §-1/§-2 (容量升级章) |

### 导航路径

| 步骤 | 操作 |
|:---:|------|
| 1 | 读本蓝图 §零 分派表 → 定位你的任务域 |
| 2 | 读本蓝图 §二 契约总表 → 找你的 CT-* 契约 |
| 3 | 如涉及容量升级 → 读 Capacity 蓝图 §-1/§-2 |
| 4 | 如涉及 CBAC → 读 Agent-Spec 蓝图 §十五 |
| 5 | 按契约施工 → 读具体模块蓝图 §16 |

### 漂移防护

| 修改本文件 | 必须同步更新 |
|-----------|------------|
| CT-* 契约变更 | MOD-MASTER_BLUEPRINT-AGENT-SPEC (CBAC 矩阵) + 所有消费者模块蓝图 |
| 共享 Schema 变更 | PS-STD-001 metadata_registry.yaml |
| 架构原则变更 | SYS-MASTER-001 §四 + 所有模块蓝图 |
| construction_progress 变更 | blueprint_registry.yaml |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | 禁止模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义。本蓝图是 MOD-MASTER_BLUEPRINT 拆分后的子蓝图（baseline），独立管理 12 系统集成契约——拆分判定基于独立职责域。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同 → 原地升级（§17 容量升级附录增量记录）
  └ 职责不同 → 拆分独立蓝图（独立 frontmatter + 概述 + §0~§18）
      触发条件（满足任一）：独立 module_id 前缀 / 独立 Phase 路线图 / 独立依赖图（交集<50%）

STEP 3: 拆分后验证
  - 独立 frontmatter + 概述 + §0~§18
  - belongs_to 指向父蓝图
  - blueprint_registry.yaml 同步更新
```
