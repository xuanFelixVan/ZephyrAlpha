---
module_id: MOD-INF-025
activation_phase: requires_100ai
submodule_path: src/zephyr/infrastructure/a2a_protocol
title: "A2A Protocol 蓝图 — Agent间通信协议与冲突解决"
doc_type: blueprint
status: Active
version: "0.12.0"
layer: L0_infrastructure
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/infrastructure/a2a_protocol/"
last_updated: "2026-06-23"
last_verified: "2026-06-23"
generation: 3
parent_module: ""
belongs_to: "MOD-MASTER_BLUEPRINT"
codification_level: L2
codification_at: "2026-05-14"
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
priority: P2
runtime_plane: hot
references:
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "REQUIRED_SECTIONS"
    why: "蓝图模板 v3.3 合规基准"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "§4"
    why: "蓝图规格化铁律"
depends_on:
  - target: "MOD-INF-018"
    at: "§2"
    why: "Agent RBAC——A2A Agent Card identity 字段与 RBAC agent_id/role 对齐"
  - target: "MOD-INF-022"
    at: "§2.2"
    why: "Escalation——A2A 仲裁三级输出对齐 Escalation 三级"
  - target: "MOD-INF-020"
    at: "§2"
    why: "Audit Trail——A2A 通信记录/冲突事件/仲裁结果写入审计"
  - target: "MOD-INF-019"
    at: "§2.2"
    why: "Agent Spec / AGENTS.md——Skill Pack 路由是 A2A Agent Card 注册入口"
  - target: "MOD-GATE_ENGINE"
    at: "§2"
    why: "Gate Engine——A2A 消息 schema 校验与安全门禁"
  - target: "KBG-0032"
    at: "全篇"
    why: "AgentOrchestrator——A2A Supervisor 在其之上构建"
  - target: "KBG-0041"
    at: "§1"
    why: "Session Handoff——委托上下文包字段格式对标 HandoffPackage"
summary: "Agent间通信协议与冲突解决——九层十二协议架构，覆盖发现/通信/协商/辩论/共识/经济/路由/事务/协调九层+脚本执行基础设施层，150条盲点全覆盖，57代码骨架+14容量扩展文件。"
tags: [a2a, agent-coordination, multi-agent, conflict-resolution, infrastructure, agent-card, task-state-machine, message-security, owasp-asi07, deadlock-prevention, saga-transaction, structured-negotiation, anp, formal-verification, tla-plus, vector-reputation, trustflow, context-rot, user-consent, constitutional-governance, agent-immune-system, agent-forgetting, multi-protocol-gateway, causal-trace, blame-attribution, capacity-upgrade, script-execution]
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 同时活跃 AI Agent 数 | 1 | ≥3 | ❌ |
> | 跨 Agent 任务依赖数 | 0 | ≥5 | ❌ |
> | Agent 间文件冲突次数 | 0次/周 | ≥1次/周 | ❌ |
>
> **为什么现在不自动化**: A2A 是 AI 之间的对讲机。当前只有 1 个 AI session，没有"另一个 AI"可以通信。一个人不需要对讲机。
> **什么时候建**: 当同时活跃 AI Agent ≥3，或跨 Agent 任务依赖 ≥5，或 Owner 要求多 Agent 协作调度时。
> **自动化宿主**: FLE `_periodic_checks()` → `_a2a_health_check()` + CircadianScheduler `hour=5` → `_a2a_discovery_scan()`

> module_id: MOD-INF-025 | version: 0.12.0 | status: active | domain: infra_ops
> actual_disk_path: src/zephyr/infra_ops/a2a_protocol/ | generation: 3 | construction_progress: scaffold

# A2A Protocol 蓝图 — Agent间通信协议与冲突解决

## 概述

本蓝图描述 ZephyrAlpha Agent 间通信协议（A2A Protocol）——它解决了多 Agent 场景下的发现、通信、协调、冲突解决与安全防护问题。核心职责包括：Agent Card 发现与身份验证、Task 状态机与消息路由、结构化协商与共识、经济护栏与资源分配、协议安全与形式化验证、宪法治理与免疫系统。当前规模 57 个代码骨架（scaffold 级），目标容量 1,500 模块 × 10,000 治理脚本 × 100 并发 Agent。上游依赖 MOD-INF-018(RBAC)/MOD-INF-022(Escalation)/MOD-INF-019(Agent Spec)，下游被所有业务域 Agent 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-025`

| # | 代码路径 | 蓝图章节 | 存在性 | 阻塞原因（仅已阻塞） |
|---|---------|---------|:-----:|-------------------|
| 1 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\agent_card.py` | §3 D-025-02 | 已实现 | — |
| 2 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\a2a_registry.py` | §3 D-025-02 | 已实现 | — |
| 3 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\identity_verifier.py` | §3 D-025-10 | 已实现 | — |
| 4 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\a2a_schemas.py` | §3 D-025-04 | 已实现 | — |
| 5 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\a2a_state.py` | §3 D-025-03 | 已实现 | — |
| 6 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\handoff_manager.py` | §3 D-025-05 | 已实现 | — |
| 7 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\message_router.py` | §3 D-025-04 | 已实现 | — |
| 8 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\streaming.py` | §3 D-025-04 | 已实现 | — |
| 9 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\push_notifier.py` | §3 D-025-04 | 已实现 | — |
| 10 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\context_package.py` | §3 D-025-11 | 已实现 | — |
| 11 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\trigger_monitor.py` | §1.1 | 已实现 | — |
| 12 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\supervisor.py` | §3 D-025-05 | 已实现 | — |
| 13 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\spec_sync.py` | §3 D-025-06 | 已实现 | — |
| 14 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\conflict_detector.py` | §3 D-025-07 | 已实现 | — |
| 15 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\semantic_diff.py` | §3 D-025-07 | 已实现 | — |
| 16 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\arbitrator.py` | §3 D-025-08 | 已实现 | — |
| 17 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\deadlock_guard.py` | §3 D-025-09 | 已实现 | — |
| 18 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\livelock_detector.py` | §3 D-025-09 | 已实现 | — |
| 19 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\cascade_guard.py` | §3 D-025-12 | 已实现 | — |
| 20 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\construction_verifier.py` | §3 D-025-10 | 已实现 | — |
| 21 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\session_smuggling_defense.py` | §3 D-025-10 | 已实现 | — |
| 22 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_security.py` | §3 D-025-10 | 已实现 | — |
| 23 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_economics.py` | §3 D-025-12 | 已实现 | — |
| 24 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_tracing.py` | §3 D-025-13 | 已实现 | — |
| 25 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_metrics.py` | §3 D-025-13 | 已实现 | — |
| 26 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_negotiation.py` | §3 D-025-13 | 已实现 | — |
| 27 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_voting.py` | §3 D-025-13 | 已实现 | — |
| 28 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_collusion_detector.py` | §3 D-025-14 | 已实现 | — |
| 29 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_anomaly_detector.py` | §3 D-025-14 | 已实现 | — |
| 30 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_cross_agent_semantic_flow.py` | §3 D-025-14 | 已实现 | — |
| 31 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_behavior_fingerprint.py` | §3 D-025-14 | 已实现 | — |
| 32 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_saga.py` | §3 D-025-15 | 已实现 | — |
| 33 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_checkpoint.py` | §3 D-025-15 | 已实现 | — |
| 34 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_idempotency.py` | §3 D-025-15 | 已实现 | — |
| 35 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_debate.py` | §3 D-025-16 | 已实现 | — |
| 36 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_work_steal.py` | §3 D-025-19 | 已实现 | — |
| 37 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_protocol_security.py` | §3 D-025-20 | 已实现 | — |
| 38 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_frame_negotiation.py` | §3 D-025-21 | 已实现 | — |
| 39 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_delegation_chain.py` | §3 D-025-21 | 已实现 | — |
| 40 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_formal_verification.py` | §3 D-025-22 | 已实现 | — |
| 41 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_temporal_admission.py` | §3 D-025-22 | 已实现 | — |
| 42 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_latent_comm.py` | §3 D-025-23 | 已实现 | — |
| 43 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_vector_reputation.py` | §3 D-025-24 | 已实现 | — |
| 44 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_context_rot.py` | §3 D-025-25 | 已实现 | — |
| 45 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_consent.py` | §3 D-025-26 | 已实现 | — |
| 46 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_red_team.py` | §3 D-025-27 | 已实现 | — |
| 47 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_hibernate.py` | §3 D-025-27 | 已实现 | — |
| 48 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_constitutional.py` | §3 D-025-28 | 已实现 | — |
| 49 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_immune.py` | §3 D-025-29 | 已实现 | — |
| 50 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_forgetting.py` | §3 D-025-30 | 已实现 | — |
| 51 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_carbon.py` | §3 D-025-31 | 已实现 | — |
| 52 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_idle_guard.py` | §3 D-025-32 | 已实现 | — |
| 53 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_dashboard.py` | §3 D-025-32 | 已实现 | — |
| 54 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_knowledge_distill.py` | §3 D-025-33 | 已实现 | — |
| 55 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_hardware_router.py` | §3 D-025-34 | 已实现 | — |
| 56 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_protocol_gateway.py` | §3 D-025-35 | 已实现 | — |
| 57 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_causal_trace.py` | §3 D-025-37 | 已实现 | — |
| 58 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_blame_attribution.py` | §3 D-025-38 | 已实现 | — |
| 59 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\a2a_governance_adapter.py` | §12 | 已实现 | — |
| 60 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\a2a_card_registry.py` | §3 D-025-20 | 已实现 | — |
| 61 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\legacy_protocol.py` | 兼容层 | 已废弃 | — |
| 62 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\legacy_auditor.py` | 兼容层 | 已废弃 | — |
| 63 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\legacy_governance_adapter.py` | 兼容层 | 已废弃 | — |
| 64 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\phase_hold.py` | §1.1 | 已实现 | — |
| `governance/auditor.py` | § — | 已实现 | | 本模块 |
| `governance/governance_adapter.py` | § — | 已实现 | | 本模块 |
| `governance/protocol.py` | § — | 已实现 | | 本模块 |
| `local_first_arch.py` | § — | 已实现 | | 本模块 |
| `market_data_pipeline.py` | § — | 已实现 | | 本模块 |
| `migration_strategy.py` | § — | 已实现 | | 本模块 |
| `multi_agent.py` | § — | 已实现 | | 本模块 |
| `multi_model_consensus.py` | § — | 已实现 | | 本模块 |
| `offline_autonomy.py` | § — | 已实现 | | 本模块 |
| `offline_resilience.py` | § — | 已实现 | | 本模块 |
| `prompt_lifecycle.py` | § — | 已实现 | | 本模块 |
| `realtime_streaming.py` | § — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| frontmatter actual_disk_path ↔ §11 业务代码路径 | 路径核对 | ☐ |
| construction_progress ↔ 代码实际状态 | scaffold: 66 .py 文件存在 | ☐ |
| §3 组件架构 ↔ 代码目录结构 | 三层目录对应 | ☐ |
| 蓝图 §0 文件清单 ↔ 代码 [BLUEPRINT] 字段 | 代码文件头部十五字段 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.10.0 (基线) | 66 .py 骨架 + legacy 合并 | 核心逻辑实现 | 待施工 |
| v0.11.0 (容量升级) | 容量升级 Layer 0 + 模板 v3.3 对齐 | — | — |
| v0.12.0 (模板升级) | 蓝图结构对齐模板 v3.5/v3.6 | — | 本次升级 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 在 1人+AI 场景下，多个 IDE（TRAE/Cursor/RooCode）中的 Agent 需要协同工作。当前单 Agent + 多 IDE 模式下 A2A 不急需，但触发条件命中后（≥3 Agent 并发 / 跨 IDE 冲突 / Agent 间委托需求）必须立即启动。

**触发条件监控**：

| metric | 阈值 | 当前值 | 触发动作 |
|--------|------|--------|---------|
| concurrent_ide_sessions | ≥3 | 1 | 启动 scaffold Phase |
| cross_ide_file_conflicts/week | ≥2 | 0 | 启动冲突检测 |
| agent_delegation_requests/week | ≥1 | 0 | 启动任务交接 |
| false_task_completion_events | ≥1 | 0 | 启动验证门禁 |
| emergence_behavior_signals | ≥1 | 0 | 启动异常检测 |
| concurrent_ide_sessions | ≥10 | 1 | 启动容量升级 |

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | Agent 间通信协议 | Google A2A v1.0 兼容 + YAML 人读格式 |
| 2 | 冲突检测与仲裁 | 文本+语义双层检测，三级仲裁 auto→escalate→block |
| 3 | 死锁/活锁防护 | 四层死锁防护 + 三模式活锁检测 |
| 4 | 消息安全 | OWASP ASI07 全覆盖 + JWT 签名 + 防重放 |
| 5 | 经济护栏 | 全链路 Token 预算 + ROI 追踪 + 模型路由 |
| 6 | 协议形式化验证 | TLA+ 7 属性模型检查 + 运行时断言 |
| 7 | 宪法治理 | Critic-with-veto + HC-12 零容忍门控 |
| 8 | 容量升级 | 1,500 模块 / 10,000 脚本 / 100 Agent 设计上限 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | AI 审计守卫实现 | → MOD-INF-001 |
| 2 | 安全网关实现 | → MOD-LLM_SECURITY |
| 3 | 任务门禁 | → MOD-GATE_ENGINE |
| 4 | 回滚执行 | → MOD-INF-021 |
| 5 | Agent Spec 实现 | → MOD-INF-019 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 单机部署 | 无分布式协调需求，SQLite WAL 足够 |
| 1人+AI 运维 | 90% 异常自愈，Owner 告警≤10条/日 |
| 3 IDE 并发 | Agent Card 需跨 IDE 同步 |
| 100 AI 设计上限 | 容量升级 v0.11.0 目标 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | Agent 发现与身份 | Agent Card 模型 + AGENTS.md 注册 + JWT/JWS 身份验证 + 克隆检测 |
| 2 | 通信与任务 | Task 状态机 + Message/Part 类型 + SSE 流式 + Push Notification + 上下文包 |
| 3 | 结构化协商 | ANP 1.0 Negotiation Frame + Capability Token + 委托链权威性缩减 |
| 4 | 辩论与审议 | 4 阶段结构化辩论 + Anti-Conformity + 辩论深度上限 |
| 5 | 共识与协商 | 6 状态协商会话机 + 投票/多数决 + 合谋检测 + 4 级降级 |
| 6 | 经济与资源 | Agent 预算池 + ROI 追踪 + 跨 IDE 花费聚合 + TrustFlow 向量信誉 |
| 7 | 异质模型路由 | 角色×难度×负载三维决策 + Confidence-Aware + 批量降级 |
| 8 | 事务与回滚 | Saga LT/CT 配对 + 分布式检查点 + 幂等性门禁 |
| 9 | 协调与负载均衡 | Supervisor + Living Spec + 冲突检测 + 死锁/活锁防护 + 仲裁 + 工作窃取 |
| 10 | 协议安全 | A2ASECBENCH 六大攻击面 + Agent Card 供应链 + Task 流防操纵 + Artifact 投毒 |
| 11 | 形式化验证 | TLA+ P1-P7 + Coq + 时间感知准入控制 BAR |
| 12 | 宪法治理 | Critic-with-veto + HC-12 GovernanceGate + intent drift + policy-compliant harm |
| 13 | 免疫系统 | 三层免疫 + 隔离检疫 + 攻击链检测 + 工具调用策略治理 |
| 14 | 选择性遗忘 | FSFM 四类遗忘 + 跨 Agent Cascading Forget + GDPR 合规 |
| 15 | 运维可持续性 | 碳排放追踪 + 空转综合征检测 + 知识蒸馏 + 硬件感知路由 |
| 16 | 多协议网关 | A2A/MCP/ACP/ANP 四协议适配器 + AGNTCY 互联总线 |
| 17 | 失败归因 | CTEGs 因果事件图 + 17x Error Trap + 三问归因法 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | AI 审计守卫 | MOD-INF-001 |
| 2 | 安全网关 | MOD-LLM_SECURITY |
| 3 | 任务门禁 | MOD-GATE_ENGINE |
| 4 | 回滚执行 | MOD-INF-021 |
| 5 | Agent Spec / Skill Pack | MOD-INF-019 |
| 6 | Shared Core 实现 | MOD-INF-016 |

---

## §3 架构设计

### 3.1 组件架构

**九层十二协议架构**：

| 层 | 协议 | 核心组件 | 代码路径 | 状态 |
|---|------|---------|---------|:---:|
| Layer 0 | 脚本执行基础设施 | ScriptCard + ScriptQueue + WorkerPool + Sandbox | `layer3_coordination/script_*.py` | 📋 |
| Layer 1 | 发现与身份 | AgentCard + A2ARegistry + IdentityVerifier | `layer1_discovery/` | ⏸️ |
| Layer 2 | 通信与任务 | A2ASchemas + A2AState + HandoffManager + MessageRouter + Streaming + PushNotifier | `layer2_communication/` | ⏸️ |
| Layer 3 | 结构化协商帧 | FrameNegotiation + DelegationChain + CapabilityToken | `layer3_coordination/a2a_frame_*.py` | ⏸️ |
| Layer 4 | 辩论与审议 | DebateProtocol + AntiConformity + AAD/CI | `layer3_coordination/a2a_debate.py` | ⏸️ |
| Layer 5 | 共识与协商 | Negotiation + Voting + CollusionDetector | `layer3_coordination/a2a_negotiation.py` + `a2a_voting.py` | ⏸️ |
| Layer 6 | 经济与资源 | Economics + VectorReputation + Carbon + IdleGuard + Dashboard | `layer3_coordination/a2a_economics.py` + `a2a_vector_reputation.py` 等 | ⏸️ |
| Layer 7 | 异质模型路由 | ModelRouter + HardwareRouter + LatentComm + KnowledgeDistill | `layer3_coordination/a2a_hardware_router.py` 等 | ⏸️ |
| Layer 8 | 事务与回滚 | Saga + Checkpoint + Idempotency | `layer3_coordination/a2a_saga.py` 等 | ⏸️ |
| Layer 9 | 协调与负载均衡 | Supervisor + SpecSync + ConflictDetector + SemanticDiff + Arbitrator + DeadlockGuard + LivelockDetector + WorkSteal | `layer3_coordination/` 核心 | ⏸️ |
| 横切 | 安全+验证+治理+免疫+遗忘+归因 | Security + ProtocolSecurity + FormalVerification + TemporalAdmission + Constitutional + Immune + Forgetting + CausalTrace + BlameAttribution | `layer3_coordination/a2a_*.py` | ⏸️ |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | Agent 请求 | AgentCard 注册 → AGENTS.md 写入 → Coordinator 发现 | 目标 Agent | AgentCard YAML |
| 2 | Coordinator | Task 分解 → Agent 分配 → HandoffManager 交接 | 目标 Agent | A2AMessage |
| 3 | Agent 代码变更 | SpecSync 扫描 → Living Spec 对比 → 冲突检测 | ConflictDetector | SpecDiff |
| 4 | 冲突事件 | ConflictDetector → Arbitrator 三级仲裁 | Escalation/MOD-INF-022 | ArbitrationResult |
| 5 | Agent 间消息 | MessageRouter → schema 校验 → 签名验证 → 分发 | 目标 Agent | A2AMessage + A2APart |
| 6 | 异常信号 | AnomalyDetector → throttle/freeze → Critic Agent 审查 | Owner | AnomalyReport |

### 3.3 状态生命周期

**A2A TaskState**（独立于 Orchestrator TaskState）：

| 状态 | 含义 | 合法转换 |
|------|------|---------|
| SUBMITTED | 任务已提交 | → WORKING / REJECTED / INPUT_REQUIRED |
| WORKING | Agent 正在执行 | → COMPLETED / FAILED / CANCELED / INPUT_REQUIRED |
| COMPLETED | 任务完成 | → VERIFIED / DISPUTED |
| INPUT_REQUIRED | 需要额外输入 | → WORKING |
| REJECTED | 任务被拒绝 | — 终态 |
| FAILED | 执行失败 | — 终态 |
| CANCELED | 已取消 | — 终态 |
| VERIFIED | 已验证完成 | — 终态 |
| DISPUTED | 完成被质疑 | → VERIFIED / FAILED |

**协商会话机**（6 状态）：

| 状态 | 含义 | 合法转换 |
|------|------|---------|
| PROPOSED | 提议中 | → ACTIVE |
| ACTIVE | 协商中 | → AGREED / REJECTED / EXPIRED |
| AGREED | 达成一致 | → DORMANT |
| REJECTED | 被拒绝 | → DORMANT |
| EXPIRED | 超时 | → DORMANT |
| DORMANT | 休眠 | → PROPOSED |

### 蓝图特有：核心设计规格

#### D-025-01 三层五协议总架构

```yaml
a2a_architecture:
  layer_1_discovery_and_identity:
    protocols: [agent_card, a2a_registry, identity_verification]
    entry: AGENTS.md
  layer_2_communication_and_task:
    protocols: [task_state_machine, message_part_types, sse_streaming, push_notification, context_package]
    format: YAML
  layer_3_coordination_and_arbitration:
    protocols: [supervisor, living_spec_sync, conflict_detection, arbitration, deadlock_guard, livelock_detector]
  cross_cutting:
    - security (OWASP ASI07 + JWT + anti-replay + session_smuggling_defense)
    - economics (token_budget + model_routing + cascade_guard)
    - observability (distributed_tracing + metrics + reputation)
    - self_referential_verification (owner_audit + independent_checklist)
```

#### D-025-02 Agent Card 模型

```yaml
agent_card:
  identity:
    agent_id: "agent-{name}-{hash}"  # 全局唯一
    name: str
    version: str
    provider: "trae | cursor | roocode | standalone"
    agent_type: "autonomous_agent | auto_guard | human_proxy | governor"
  capabilities:
    skills: [{skill_id, name, tags, input_schema, output_schema}]
    max_concurrent_tasks: int  # tiered: architect=5, implementer=10-20, governor=50-100
    domain_overlap_tolerance: float  # 0.0-1.0
  security:
    public_key: str  # JCS/JWS 签名
    card_integrity: "SHA-256(agent_card_json)"
    trust_score: float  # 0.0-1.0
  registration:
    entry: AGENTS.md  # 非 well-known URI
    a2a_agents_field: "a2a_agents:"
    status: "active | stale | revoked"
  capacity_v0_11:
    max_concurrent_scripts: int
    script_worker_slots: int
    heartbeat_interval_seconds: "dynamic(idle=60, active=15, overloaded=5)"
```

#### D-025-03 A2A TaskState

```yaml
task_state_machine:
  states: [SUBMITTED, WORKING, COMPLETED, INPUT_REQUIRED, REJECTED, FAILED, CANCELED, VERIFIED, DISPUTED]
  key_transitions:
    submitted_to_working: "Coordinator dispatch → Agent accept"
    completed_to_verified: "verification_gate pass → VERIFIED"
    completed_to_disputed: "Owner 否决 within 30min → DISPUTED"
  input_required: "Google A2A §4.5 in-task auth——Agent 需要额外信息才能继续"
```

#### D-025-04 Message/Part 类型系统

```yaml
message_format:
  format: YAML  # 人读+机读，非 JSON-RPC 2.0
  message: {message_id, from_agent, to_agent, task_id, parts[], context_package, timestamp, signature}
  part_types: [TextPart, FilePart, DataPart, ArtifactPart, StatusPart, ErrorPart]
  streaming: SSE  # 长任务实时进度
  push_notification: HTTP callback  # 状态变更主动推送
```

#### D-025-05 Supervisor/Coordinator

```yaml
coordinator:
  type: rule_based  # 非 LLM Supervisor——DPBench: LLM 通信反增死锁
  task_flow: "Filter(capability_match) → Score(priority×affinity) → Assign → Monitor → Integrate"
  constraints:
    - "同一文件同一时刻只分配给一个 Agent"
    - "优先级继承：P0 任务可抢占 P2 任务"
    - "API 限流协调：10+ Agent 并发调同一 API → 排队"
```

#### D-025-06 Living Spec 同步

```yaml
living_spec:
  principle: "不在合并时修冲突，在写代码前消除冲突"
  flow: "Agent 开工前 → SpecSync 扫描接口规范 → 对比 Living Spec → 发现偏差 → 阻止开工"
  verification: "Living Spec diff verification——代码变更必须与 Spec 一致"
```

#### D-025-07 冲突检测

```yaml
conflict_detection:
  layer_1_text: "git merge / diff——文本级"
  layer_2_semantic: "AST diff + 依赖图 + 接口契约对比——语义级"
  mirror_mirror_loop: "活锁检测——两个 Agent 互相覆盖对方修改"
  sc_detect_codes: [SC-DETECT-001~004]
```

#### D-025-08 仲裁

```yaml
arbitration:
  three_tier:
    auto: "规则引擎——确定性仲裁，零 Token"
    escalate: "升级到 MOD-INF-022 Escalation Protocol"
    block: "人工——Owner 最终决定"
  rules_ssoT: "arbitration_rules.yaml (对 AI 只读)"
```

#### D-025-09 死锁/活锁防护

```yaml
deadlock_guard:
  four_layers:
    L1_dijkstra: "全局资源排序——所有 Agent 按同一顺序获取资源"
    L2_timeout: "超时熔断——持有资源超时自动释放"
    L3_preemption: "优先级抢占——高优先级任务可抢占低优先级资源"
    L4_sequentialization: "序列化降级——死锁频繁时退化为串行执行"

livelock_detector:
  three_modes:
    politeness: "Agent 主动让步但对方也让步→无限循环"
    mirror_mirror: "两个 Agent 互相覆盖→无限循环"
    endless_chain: "3+ Agent 循环等待→无限循环"
  detection: "行为模式匹配 + 超时检测"
```

#### D-025-10 A2A 消息安全

```yaml
a2a_security:
  owasp_coverage: [ASI01_prompt_injection, ASI03_privilege_escalation, ASI05_data_exposure, ASI07_message_integrity, ASI10_rogue_agent]
  mechanisms:
    signing: "JWT RS256——每条消息签名"
    anti_replay: "nonce + timestamp——5min TTL"
    identity_verification: "SPIFFE + Agent Card hash"
    session_smuggling_defense: "信任评分 + 意图一致性检查"
  construction_paradox: "100% AI 施工→开发者=被限制者→Owner 审 + AH AI 无法绕过"
```

#### D-025-11~12 上下文管理与经济护栏

```yaml
context_management:
  compression: "KBG-0041 P0-P3 四级压缩"
  pollution_detection: "OWASP ASI06 Memory Poisoning 检测"
  freshness_ttl: "上下文新鲜度/TTL 定义"
  provenance: "上下文溯源"

economic_guardrails:
  delegation_cost: "委托代价评估——预估 Token 消耗"
  chain_budget: "全链路 Token 预算——per-chain 硬顶"
  model_cascading: "模型降级策略——Opus→Sonnet→Haiku"
  prompt_caching: "Anthropic 90% off / OpenAI 50% off"
  lazy_context_loading: "成本 $280→$170/月"
  shared_memory_file: "替代 Agent 间聊天式通信"
```

#### D-025-13~14 共识与涌现检测

```yaml
consensus_and_negotiation:
  negotiation_session: "6 状态 PROPOSED→ACTIVE→AGREED/REJECTED/EXPIRED→DORMANT"
  voting_protocol: "多数决 + 加权投票 + 否决权 + 法定人数"
  collusion_detection: "Pairwise Vote Correlation + Jaccard 异常检测"
  degradation: "level_1(自动) → level_2(规则) → level_3(escalate) → level_4(block)"

emergence_detection:
  chaos_failure_modes: [F01_deadlock, F02_livelock, F03_resource_starvation, F04_dos, F05_cascade, F06_identity_spoofing, F07_cross_agent_behavior_propagation, F08_partial_takeover, F09_false_task_completion, F10_agent_collusion, F11_strategic_sabotage]
  anomaly_taxonomy: [behavioral, communication, resource, coordination, emergent]
  ml_pipeline:
    stage_1: "Isolation Forest——anomaly_score > 0.7 alert, > 0.85 throttle, > 0.95 freeze"
    stage_2: "Autoencoder——reconstruction_error 检测异常行为时间序列"
  cross_agent_semantic_flow: "MAScope PDAG construction + GNN 轨迹建模"
```

#### D-025-15 Saga 事务回滚

```yaml
saga_and_rollback:
  registration: "每个 LT(Logical Transaction) 必须注册对应 CT(Compensation Transaction)"
  compensation_types: [undo, compensate, notify]
  checkpoint: "per-agent worktree snapshot + Coordinator 全局检查点目录"
  idempotency:
    L1_task: "同一 Task ID 5min 内重复 → rejected"
    L2_operation: "同一文件+操作 10min 内重复 → rejected"
    L3_git: "目标文件 hash 不一致 → abort"
  simplified: "Phase 1: git revert + worktree checkpoint; Phase 5+: 完整 Saga"
```

#### D-025-16~19 辩论/经济/路由/工作窃取

```yaml
debate_protocol:
  phases: [proposal(independent), cross_examination, revision(max_3_rounds), voting]
  anti_conformity: "多数派>66%时权重×0.7; trajectory_scoring; confidence_tracking"
  depth_limit: "max 5 rounds; early_termination: unanimous / 2轮无新信息 / 超预算"

agent_economy:
  budget_pool: "daily_cap=$300; priority_multipliers: critical=3.0, high=2.0, medium=1.0, low=0.5, background=0.1"
  roi_tracking: "code_quality_roi = verifiable_loc / token_cost; task_success_rate; defect_rate"
  cross_ide_aggregation: "同一 Owner 所有 Agent 花费合并统计"

heterogeneous_model_router:
  decision_matrix: "priority = role×0.4 + difficulty×0.4 + load×0.2"
  confidence_aware: "<0.5 → 升级两级模型 + 考虑双 Agent 独立执行"
  batch_downgrade: "queue_depth>10 OR token_spent>80% daily_cap → moderate 以下降级"

work_stealing:
  trigger: "Agent IDLE 30s + queue_depth=0"
  victim: "queue_depth 最深 + 优先级匹配 + 无亲和性限制"
  affinity: "0.4×file_familiarity + 0.3×module_familiarity + 0.3×task_type_match; >0.6 优先分配"
  watchdog: "30s 心跳; 10min 超时; OOM <500MB 主动暂停"
  simplified: "Phase 1: Task Affinity + Watchdog; Agent≥5 时启用 Work Stealing"
```

#### D-025-20~27 协议安全/协商帧/形式化验证/潜空间/信誉/上下文腐烂/同意/Vibe

```yaml
protocol_security:
  agent_card_supply_chain: "mandatory JWS signing + SHA-256 fingerprint + clone detection"
  capability_verification: "3 benchmark tasks + drift_monitor(>2σ → 降级)"
  task_flow_protection: "UUIDv7 task_id + Living Spec diff verification + Bloom Filter anti-replay"
  artifact_poisoning: "AST+Semgrep scan + PII regex+NER + trust_score<0.5 → 需人工审查"
  rate_limiting: "per-agent ≤10/min(medium) ≤30/min(critical); global pending>100 → reject low"
  security_levels: [conservative(全开), balanced(高风险才开), permissive(仅限流)]

structured_negotiation_frame:
  frame_fields: [constraints, state_proofs, settlement_logic]
  ambiguity_tax: "YAML 聊天 40% Token 浪费 → ANP Frame <5%"
  delegation_chain: "scope 逐跳收窄; scope 扩大 → REJECTED_IMMEDIATELY; TLA+ verified 2.7M states"

formal_verification:
  properties:
    P1_deadlock_freedom: "∀a: acquired∩pending=∅"
    P2_delegation_safety: "scope[i]⊆scope[i-1]"
    P3_message_integrity: "m.type∈sender.authorized_message_types"
    P4_compensation_completeness: "∀lt: ∃ct: ct.covers(lt)"
    P5_consensus_liveness: "◇(AGREED∨REJECTED)"
    P6_rate_limiting_safety: "sent_tasks[a,60s]≤a.max_per_minute"
    P7_scoped_token: "current_scope⊆initial_scope"
  pipeline: "TLA+(TLC) → Coq/Isabelle(P4+P2) → Python runtime assertions"
  temporal_admission: "BAR(Boundary Activation Rate)监控; ∆BAR 检测执法失效"

latent_communication:
  tiers: [YAML(critical/可审计), ANP_Frame(routine/零歧义), Latent_Emding(frequent/零Token)]
  simplified: "Phase 1: YAML+ANP; Phase 2: Shared Memory File; Phase 3: 评估 Interlat"

vector_reputation:
  dimensions: [system_design, code_implementation, security_audit, testing, documentation, devops, data_engineering, frontend]
  trustflow: "Topic-Gated Transfer Operators + 收缩映射收敛; ≤4pp P@5 under attacks"
  lr2: "自底向上信誉涌现——无需预设社会规范"

context_rot:
  mechanisms: [attention_dilution(25%处开始), positional_encoding_drift, retrieval_noise_accumulation]
  proactive_compaction: "85%阈值前检测腐烂信号→LLM摘要→context refresh→hot memory"
  three_layer: [hot_memory(宪法/不可压缩), domain_expert(Agent专属), cold_memory(RAG归档)]

user_consent:
  states: [PENDING_CONSENT, CONSENT_GRANTED, CONSENT_DENIED, AUTO_CONSENT]
  auto_conditions: "trusted_agents + pre_approved_types + <$0.50 + same_task_chain"
  consent_fatigue: "Batch + Policy-Based + Dashboard + Silent Log"
  direct_data_channel: "用户数据不经过 Agent 中转，直接从 Trusted Data Store 获取"

vibe_coding_v2:
  no_ai_time: "A2A_GLOBAL_PAUSE → all agents save+pause"
  hibernate: "WAL 状态序列化; 非工作时间休眠 → -33% Token"
  adversarial_game: "月度红蓝对抗; Red vs Blue Agent"
  bridgemind: "solo → parallel(3 Agent) → orchestrated(6-role team)"
```

#### D-025-28~34 宪法治理/免疫/遗忘/碳排放/空转/蒸馏/硬件路由

```yaml
constitutional_governance:
  council: {Critic(veto), Coordinator(motion), Owner(ratification)}
  constitution_storage: "a2a-constitution.yaml (不可变, SHA-256 指纹, AI 只读)"
  governance_gate:
    scope_bound: "current_scope ⊂ card.max_scope → violation=block"
    delegation_limit: "depth <= card.max_depth → violation=block"
    budget_cap: "accumulated+remaining <= cap → violation=block"
    tool_whitelist: "tool ∈ card.whitelisted → violation=block"
  intent_drift: "每10轮 cosine_sim(task_start, current)<0.3 → CRITIC_REVIEW"
  policy_compliant_harm: "Cross-Policy Impact Graph + BFS 敏感路径识别"

agent_immune_system:
  innate: "285+ 安全模式库; <100ms; 目标<2% FPR"
  adaptive: "Critic Agent 分析新型威胁; 确认→升级 innate; 误报→调低权重"
  memory: "攻击特征哈希存入 immune_memory.db; 再遇<10ms block"
  quarantine: "ACTIVE→SUSPECTED(>0.6)→QUARANTINED(>0.85)→CLEARED/TERMINATED"
  attack_chain: "CONFIG_MOD→CRED_READ→NETWORK_SEND(凭证窃取); CODE_MOD→TEST_BYPASS→ARTIFACT_PUBLISH(后门植入)"
  tool_call_governance: "target_in_scope + frequency<20/5min + sensitivity_match + combination_risk"

agent_forgetting:
  taxonomy: [passive_decay(TTL), active_deletion(GDPR), safety_triggered(injection切除), adaptive_reinforcement(永久保留)]
  cross_agent: "Cascading Forget Notification → Coordinator 广播 → 各 Agent 执行 → ForgetCompletionReport"
  two_pass: "Pass1 PII 删除 + Pass2 匿名化模式保留"

operations_sustainability:
  carbon: "CodeCarbon 埋点; per_task/per_agent/per_chain CO2e; 碳感知调度(optional)"
  idle_syndrome: [polling_storm(≥20次/5min→kill), analysis_paralysis(产出<10%), meaningless_optimization(cosine>0.95)]
  severity: "5min WARNING → 15min ping → 30min auto-hibernate → polling_storm immediate freeze"
  knowledge_distillation: "trajectory_replay + MCP_Box(AgentDistill) + model_level(KD-MARL, Phase 3)"
  hardware_router: "GPU>90%→降级; VRAM>85%→小上下文; self-hosted 场景启用"
```

#### D-025-35~38 多协议网关/失败归因

```yaml
multi_protocol_gateway:
  four_protocols: {A2A: "企业协作", MCP: "工具集成", ACP: "联邦编排", ANP: "去中心化市场"}
  gateway: "inbound_adapters[a2a,mcp,acp,anp] + translation_engine(LLM-driven + cache -90%)"
  interconnect_bus: {discovery: OASF, identity: SHA-256+JWS, messaging: broker, observability: cross-protocol trace}
  agent_card_parameterization: "inputSchema/outputSchema 扩展(向后兼容)"
  simplified: "Phase 1: A2A+MCP only; ACP/ANP 待跨组织需求"

blame_attribution:
  failure_modes: [telephone_game(信息退化), confidence_cascade(高置信错误放大), ghost_handoff(静默丢失), tools_gone_wild(低质输入污染), conga_line(累积噪声)]
  cteg: "caused_by/tool_used edges + temporal monotonicity + Merkle tree commit"
  three_questions:
    Q1_origin: "BFS 上游溯源→首个偏差节点"
    Q2_propagation: "下游有修复信号但未修复→missed_repair"
    Q3_systemic: "频次统计→systemic_score"
  blame_report: "{origin_agent, error_type, propagation_path, missed_repairs[], systemic_score, suggested_fix}"
```

---

## §4 接口契约

### 4.1 公共 API

```python
from zephyr.infra_ops.a2a_protocol.layer1_discovery.agent_card import AgentCard
from zephyr.infra_ops.a2a_protocol.layer1_discovery.a2a_registry import A2ARegistry
from zephyr.infra_ops.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart
from zephyr.infra_ops.a2a_protocol.layer2_communication.a2a_state import A2ATaskStatus
from zephyr.infra_ops.a2a_protocol.layer3_coordination.supervisor import Supervisor
from zephyr.infra_ops.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector
from zephyr.infra_ops.a2a_protocol.layer3_coordination.arbitrator import Arbitrator

class A2AProtocol:
    """A2A 协议主入口——Agent 间通信与冲突解决"""

    def register_agent(self, card: AgentCard) -> str: ...
    def submit_task(self, task: A2ATask) -> A2ATask: ...
    def send_message(self, msg: A2AMessage) -> None: ...
    def detect_conflicts(self, changes: list) -> list: ...
    def arbitrate(self, conflict) -> ArbitrationResult: ...
```

### 4.2 数据模型

```python
class AgentCard(BaseModel):
    agent_id: str = Field(..., pattern=r"^agent-[a-z0-9_-]+$")
    name: str
    capabilities: List[AgentCapability] = []
    max_tasks: int = 5
    public_key: Optional[str] = None

class A2AMessage(BaseModel):
    message_id: str
    from_agent: str
    to_agent: str
    task_id: str
    parts: List[A2AMessagePart] = []
    timestamp: datetime

class A2ATask(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    status: A2ATaskStatus = A2ATaskStatus.SUBMITTED
    deadline: Optional[datetime] = None
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `register_agent()` | `card: AgentCard` | ✅ | agent_id 全局唯一 |
| `submit_task()` | `task: A2ATask` | ✅ | from_agent 已注册 |
| `send_message()` | `msg: A2AMessage` | ✅ | 签名有效 + 非重放 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `register_agent()` | `agent_id: str` | `DUPLICATE_AGENT` / `INVALID_CARD` |
| `submit_task()` | `A2ATask(status=SUBMITTED)` | `REJECTED` / `AGENT_NOT_FOUND` |
| `detect_conflicts()` | `List[Conflict]` | `SCAN_ERROR` |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。A2A 是 Agent 间协议，MCP 是 Agent-工具协议，两者通过 ProtocolGateway 互操作。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| AgentCard 新增字段 | ✅ 向后兼容 | 不影响已有消费者 |
| A2ATaskStatus 新增枚举 | ✅ 向后兼容 | 不破坏已有逻辑 |
| Message 格式变更 | ❌ 破坏性 | 需 Owner 审批 + 迁移 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 消息格式 = YAML（非 JSON-RPC 2.0） | 1人+AI 需肉眼看懂 Agent 间通信 |
| 2 | Coordinator = 规则驱动（非 LLM） | DPBench: LLM 通信反增死锁；确定性+零 Token |
| 3 | Agent Card 注册入口 = AGENTS.md | 本地多 IDE 无固定域名 |
| 4 | arbitration_rules.yaml 对 AI 只读 | 防止 AI 弱化仲裁规则 |
| 5 | 仲裁规则不可变 | AI 施工者 = 被限者，不能修改自己的约束 |
| 6 | 100% AI 施工需 Owner 独立验证 | 施工自指悖论 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| Agent 数 | ~3 | 10 | 100 (v0.11.0) | ✅ | Agent Card 容量参数重设计 |
| 治理脚本 | ~268 | 500 | 10,000 (v0.11.0) | ❌ | 脚本执行基础设施层 |
| 并发 IDE | 1-3 | 10 | 100 (v0.11.0) | ✅ | 跨 IDE Agent Card 同步 |
| 模块数 | ~51 | 200 | 1,500 (v0.11.0) | ❌ | 增量扫描 + 脚本映射 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃对象 | 当前位置 | 目标位置 | 处理方式 | 执行状态 |
|---|---------|---------|---------|---------|:-------:|
| 1 | legacy_protocol.py | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\legacy_protocol.py` | re-export shim | 保留为兼容层 | 未执行 |
| 2 | legacy_auditor.py | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\legacy_auditor.py` | re-export shim | 保留为兼容层 | 未执行 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Agent 间死锁 | DeadlockGuard 等待图检测 | L1 排序→L2 超时→L3 抢占→L4 串行 | 所有等待 Agent |
| 2 | 消息重放攻击 | nonce+timestamp 校验 | 拒绝 + 降低 trust-score | 目标 Agent |
| 3 | Agent 崩溃 | Watchdog 心跳超时 | 从检查点恢复 / 重新分配 | 该 Agent 的任务 |
| 4 | 级联故障 | CircuitBreaker 熔断 | Bulkhead 隔离 + DLQ + 降级 | 受影响 Agent 链 |
| 5 | 冲突无法自动解决 | Arbitrator auto 失败 | escalate→block(人工) | 冲突双方 Agent |
| 6 | PollingStorm | 工具调用哈希聚类≥20/5min | immediate freeze + Owner 通知 | 全系统 Token 预算 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | Prompt Injection 跨 Agent 传播 | 高 | OWASP ASI01 防护 + 每跳独立验证 | A2ASECBENCH 基准 |
| 2 | Agent Card 供应链操纵 | 高 | JWS 强制签名 + SHA-256 指纹 + 克隆检测 | 注册时校验 |
| 3 | Task 流劫持/重放 | 高 | UUIDv7 + TTL + Bloom Filter | 反重放测试 |
| 4 | Artifact 投毒 | 高 | AST+Semgrep 扫描 + PII 检测 | 投毒模拟测试 |
| 5 | Agent 间 DoS | 中 | per-agent rate limit + 全局 throttle | 压力测试 |
| 6 | 委托链权限泄露 | 高 | scope 逐跳收窄 + TLA+ 验证 | 形式化验证 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | Agent Card / TaskState / Message | 字段校验/状态转换/签名验证 | 覆盖率≥80% |
| 2 | 集成测试 | Supervisor+Handoff+Conflict | 端到端任务交接+冲突检测 | 端到端通过 |
| 3 | 安全测试 | OWASP ASI01-10 | Prompt Injection/重放/投毒 | 全部拦截 |
| 4 | 形式化验证 | TLA+ P1-P7 | 死锁自由/委托安全 | 0 violations |
| 5 | 红蓝对抗 | 协议安全 | adversarial fuzzing | 蓝方不输出 "I Give Up" |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 蓝图路径 |
|---------|---------|---------|---------|
| MOD-INF-018 | 必须 | Agent RBAC 身份 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-022 | 必须 | Escalation 升级 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-020 | 必须 | Audit Trail | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-019 | 必须 | Agent Spec / AGENTS.md | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` |
| MOD-GATE_ENGINE | 可选 | Gate Engine | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| KBG-0032 | 可选 | AgentOrchestrator | `D:\ZephyrAlpha\docs\02_enterprise_architecture\` |
| KBG-0041 | 可选 | Session Handoff | `D:\ZephyrAlpha\docs\02_enterprise_architecture\` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-025` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |

### 10.3 内部依赖图

| 上游模块 | 下游模块 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| layer1_discovery | layer2_communication | Agent Card → 消息路由 | import 检查 |
| layer2_communication | layer3_coordination | 消息状态 → 冲突检测 | 事件流检查 |
| layer3_coordination | audit-trail (MOD-INF-020) | 仲裁事件 → 审计写入 | 事件写入检查 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 |
|---|---------|:-------:|------|---------|---------|------|
| 1 | 依赖图自动生成 | 是 | 7个外部依赖+内部依赖 | AST解析import | asset-inventory/dependency.py | 不覆盖a2a_protocol |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案 | 压缩工作流脚本 | 无 | 需新建 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\a2a-protocol\blueprint.md` | 本文件 |
| 业务代码(L1) | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\` | 发现与身份层 |
| 业务代码(L2) | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\` | 通信与任务层 |
| 业务代码(L3) | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\` | 协调与仲裁层 |
| 业务代码(根) | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\` | 根级模块+legacy |
| 测试代码 | `D:\ZephyrAlpha\tests\integration\infra_ops\a2a_protocol\` | 集成测试 |
| 仲裁规则 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\arbitration_rules.yaml` | 仲裁规则 SSoT |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-INF-018 RBAC | 身份对齐 | AgentCard.agent_id ↔ RBAC agent_id | 注册时双向校验 |
| MOD-INF-022 Escalation | 仲裁升级 | Arbitrator.escalate → EscalationProtocol | 三级仲裁端到端 |
| MOD-INF-020 Audit Trail | 事件写入 | A2A 通信/冲突/仲裁 → audit_log | 审计日志完整 |
| MOD-INF-019 Agent Spec | 发现入口 | AGENTS.md a2a_agents 字段 | Agent 注册可发现 |
| MOD-GATE_ENGINE Gate Engine | 消息门禁 | MessageRouter → schema 校验 | 消息校验通过 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| MOD-GOVERNANCE | 治理域 | A2A 协议安全规则纳入治理域 | MOD-INF-022 | 修改安全规则必须同步更新 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-025 版本+字段 | 蓝图升级 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本+路径更新 | 蓝图升级 |
| 3 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | A2A 依赖关系 | 新增依赖 |

---

## §14 已知风险与缓解

> 正面后果与 §1 目标重复，不在此记录。负面后果合并到本节"类型=负面后果"行。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 触发条件长期不命中 | 高 | 低 | Hold 状态零成本等待 | 风险 |
| 2 | 100 AI 同时触发扫描 | 中 | 高 | 合并窗口5s→15s→30s 动态调整 | 风险 |
| 3 | 64GB 内存 100 并发不足 | 中 | 高 | Per-script 256MB hard limit + OOM killer | 风险 |
| 4 | LLM API 调用成本爆炸 | 中 | 中 | Per-script+per-module Token cap + 调用去重 | 风险 |
| 5 | 10K 脚本 trigger_files glob 开销 | 低 | 中 | 预计算索引——注册时计算 | 风险 |
| 6 | 协议复杂度高（九层十二协议+横切关注点） | — | — | 分层解耦+Hold 状态零成本 | 负面后果 |
| 7 | 1人+AI 场景下大部分功能处于 Hold 状态 | — | — | 触发条件监控+自动启动 | 负面后果 |
| 8 | 容量升级引入脚本执行基础设施层增加系统整体复杂度 | — | — | 分 Phase 交付+独立验证 | 负面后果 |

---

## §16 施工指引

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

| Phase | 任务 | 产出物路径 | 验收标准 | G7 检查项 |
|:---:|------|---------|---------|---------|
| Hold | 等待触发条件命中 | — | §1.4 metric 阈值 | 触发监控运行 |
| scaffold | Layer 1 完整：Agent Card + AGENTS.md 注册 + JWT | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\` | Card 注册可发现 | schema 校验通过 |
| scaffold | Layer 2 基础：Task 状态机 + Message/Part + 上下文包 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer2_communication\` | 状态转换完整 | 状态机测试通过 |
| scaffold | Layer 3 核心：Coordinator + 冲突检测 + 仲裁 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\` | 端到端任务交接 | 冲突检测+仲裁测试 |
| scaffold | 死锁防护 L1+L2 | `deadlock_guard.py` | Dijkstra+超时熔断 | 死锁测试通过 |
| experimental | SSE + Push + 输入协商 | `streaming.py` + `push_notifier.py` | 流式传输可用 | 延迟<100ms |
| experimental | 语义冲突 + 活锁检测 | `semantic_diff.py` + `livelock_detector.py` | AST diff 可用 | 活锁检测通过 |
| experimental | 通信安全 + 经济护栏 | `a2a_security.py` + `a2a_economics.py` | OWASP 覆盖 | 安全测试通过 |
| experimental | 共识/涌现/Saga | `a2a_negotiation.py` + `a2a_anomaly_detector.py` + `a2a_saga.py` | 协商+检测+回滚 | 集成测试通过 |
| beta | 可观测性 + 性能优化 | `a2a_tracing.py` + `a2a_metrics.py` | 追踪+指标可用 | P99<100ms |
| beta | 协议安全 + ANP + TLA+ | `a2a_protocol_security.py` + `a2a_frame_negotiation.py` | A2ASECBENCH 覆盖 | 安全基准通过 |
| beta | 宪法治理 + 免疫 + 遗忘 | `a2a_constitutional.py` + `a2a_immune.py` + `a2a_forgetting.py` | 零容忍门控 | 形式化验证通过 |
| beta | 多协议网关 + 失败归因 | `a2a_protocol_gateway.py` + `a2a_causal_trace.py` | 四协议适配 | 归因测试通过 |
| Phase-C1 | 脚本基础设施(G01+G02+G05) | `script_card.py` + `script_queue.py` + `script_sandbox.py` | 10K 脚本入队 | 队列压力测试 |
| Phase-C2 | 增量扫描链路(G03+G07) | `change_detector.py` + `script_mapper.py` | 15-30 脚本/commit | 去重验证 |
| Phase-C3 | 资源管理(G04) | `resource_manager.py` | CPU/内存分区 | OOM 防护测试 |
| **独立验证** | Owner 逐行审查 + 安全测试 + TLA+ | — | 全部门控通过 | Owner 签字 |

---

## §17 容量升级

> v0.11.0 容量升级：51模块×268脚本 → 1,500模块×10,000脚本×100 Agent

### 17.1 容量目标

| 维度 | 当前(v0.10.0) | 升级后(v0.11.0) | 倍数 |
|------|:---:|:---:|:---:|
| 模块数 | ~51 | 1,500 | ~7.5× |
| 治理脚本 | ~268 | 10,000 | ~20× |
| 并发 Agent | ~3 | 100 | ~10× |
| 并发脚本 | 未定义 | 40-100 | — |
| 增量扫描 | 未定义 | 15-30/<1min | — |
| 全量扫描 | 未定义 | 10K/~3.5h | — |

### 17.2 容量缺口（12 项）

| # | 缺失 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| G01 | 脚本任务队列与调度引擎 | 🔴 P0 | §3 Layer 0 |
| G02 | 脚本元数据注册表 | 🔴 P0 | §3 Layer 0 |
| G03 | 增量变更检测→脚本映射 | 🔴 P0 | §3 Layer 0 |
| G04 | 脚本级别资源管理 | 🔴 P0 | §3 横切 |
| G05 | 脚本执行沙箱与隔离 | 🔴 P0 | §3 横切 |
| G06 | 全量扫描编排 | 🟠 P1 | §3 Layer 0 |
| G07 | 多 AI 扫描去重与合并 | 🟠 P1 | §3 Layer 0 |
| G08 | 脚本结果存储与趋势分析 | 🟠 P1 | §3 Layer 0 |
| G09 | 队列公平性与饥饿防护 | 🟠 P1 | §3 Layer 0 |
| G10 | 脚本级 LLM API 限流 | 🟡 P2 | §3 横切 |
| G11 | 脚本故障处理 | 🟡 P2 | §3 横切 |
| G12 | Agent Card 容量参数重设计 | 🟡 P2 | §3 D-025-02 |

### 17.3 架构升级

```
Layer 0（新增）：脚本执行基础设施层
  G02 ScriptCard + G03 ChangeDetector/ScriptMapper + G01 ScriptTaskQueue/Scheduler
  G06 FullScanOrchestrator + G07 Multi-AI Dedup

Layer 1-9（现有八层十二协议，不变）

Layer 10（新增）：容量扩展与运维层
  G12 Agent Card 容量参数 + G04 ResourceManager + G05 ScriptSandbox
  G08 ScriptResultStore/TrendAnalyzer + G10 ScriptLLMBudget + G11 ScriptHealth + G09 QueueFairness

横切：容量感知的资源管理
  G04(CPU/MEM/IO/GPU) + G05(沙箱) + G10(API限流) + G11(故障处理)
```

### 17.4 关键设计决策（容量升级）

| 决策 ID | 决策内容 | 依据 |
|---------|---------|------|
| D-025-39 | ScriptCard 独立于 AgentCard | trigger_files 和 dependencies 是 Agent Card 不需要的维度 |
| D-025-40 | 增量扫描=合并窗口(5s)+依赖展开+结果缓存 | 100 AI 同时 commit 需批量调度 |
| D-025-41 | P-core(8)→AI Agent/LLM; E-core(4)→脚本执行 | P-core 单核强适合 LLM; E-core 能效高适合轻量脚本 |
| D-025-42 | 64GB: OS 4GB + AI 30GB + 脚本 25GB + 缓冲 5GB | 100 并发×256MB=25.6GB |
| D-025-43 | 全量扫描=按 module_id 分区×4 并发，~3.5h | 串行 4.2h; 4 并发+I/O 等待→3.5h |
| D-025-44 | 脚本 LLM 调用去重(LRU cache, TTL=5min) | 20K 调用/全量→去重后<5K |
| D-025-45 | WorkerPool 默认 18 slot，峰值 burst 100 | 20 线程-2(AI)=18; I/O wait 填充可 burst |
| D-025-46 | 容量升级 Phase 可与 A2A 协议 Phase 并行 | 脚本基础设施不依赖 Agent 间通信 |

### 17.5 新增文件（14 个）

| 文件 | 职责 | 缺口 |
|------|------|:---:|
| `script_card.py` | ScriptCard Pydantic V2 模型 | G02 |
| `script_registry.py` | 脚本注册表 register/deregister/discover | G02 |
| `script_queue.py` | ScriptTaskQueue 优先级队列+背压+去重 | G01 |
| `script_scheduler.py` | ScriptScheduler 队列消费→WorkerPool 分配 | G01 |
| `script_worker.py` | WorkerPool 多进程池+资源监控+OOM 防护 | G01/G05 |
| `script_sandbox.py` | ScriptSandbox 子进程隔离+只读+超时 kill | G05 |
| `change_detector.py` | ChangeDetector git diff→ChangeVector | G03 |
| `script_mapper.py` | ScriptMapper ChangeVector→脚本集合+去重 | G03/G07 |
| `full_scan.py` | FullScanOrchestrator 分区+断点续扫 | G06 |
| `script_result_store.py` | ScriptResultStore 结果持久化+查询 | G08 |
| `script_trends.py` | TrendAnalyzer 趋势+异常告警 | G08 |
| `script_llm_budget.py` | ScriptLLMBudget Token 限额+去重+cost | G10 |
| `script_health.py` | ScriptHealth 健康评分+自动禁用+retry | G11 |
| `resource_manager.py` | ResourceManager CPU/MEM/IO/GPU 分区 | G04 |

---

## §18 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| R81-C04 | Hold 至 stable（维持） | 2026-05-05 | 单 Agent+多 IDE，A2A 不急需 |
| D-025-01 | 三层五协议总架构 | 2026-05-05 | Google A2A 全栈+Anthropic Agent Teams |
| D-025-02 | Agent Card 注册入口=AGENTS.md | 2026-05-05 | 本地多 IDE 无固定域名 |
| D-025-03 | A2A TaskState 独立于 Orchestrator | 2026-05-05 | Google A2A TaskState 针对黑盒 Agent |
| D-025-04 | A2A 消息格式=YAML | 2026-05-05 | 1人+AI 需人读 |
| D-025-05 | Coordinator=规则驱动 | 2026-05-05 | DPBench: LLM 通信反增死锁 |
| D-025-06 | 引入 Living Spec | 2026-05-05 | 写代码前消除冲突 |
| D-025-07 | 冲突检测=文本+语义双层 | 2026-05-05 | Augment: semantic contradictions 最难检测 |
| D-025-08 | 仲裁=三级递进 auto→escalate→block | 2026-05-05 | A2A 仲裁独特性 |
| D-025-09 | 死锁防护四层 | 2026-05-05 | DPBench 3 Agent=95-100% 死锁率 |
| D-025-10 | A2A 消息安全全套 | 2026-05-05 | OWASP ASI03/07/10 |
| D-025-11 | 施工自指悖论——Owner 审 | 2026-05-05 | 100% AI 施工→开发者=被限者 |
| D-025-12 | Vibe Coding 6+3 项优化 | 2026-05-05 | 1人+AI 三重特殊性 |
| D-025-13 | 多 Agent 共识与协商层 | 2026-05-05 | Concordia Protocol |
| D-025-14 | 涌现行为与异常检测 | 2026-05-05 | Agents of Chaos+MAScope |
| D-025-15 | Saga 事务回滚 | 2026-05-05 | SagaLLM+LangChain Compensation |
| D-025-16 | 辩论与审议协议 | 2026-05-05 | Free-MAD+ACL 2025 |
| D-025-17 | Agent 经济与资源分配 | 2026-05-05 | x402+AEP |
| D-025-18 | 异质模型动态路由 | 2026-05-05 | OI-MAS+Chimera+GraphPlanner |
| D-025-19 | 工作窃取与负载均衡 | 2026-05-05 | Cilk-style+OpenAI Swarm |
| D-025-20 | A2A 协议层安全攻击面防护 | 2026-05-05 | A2ASECBENCH(ICLR 2026) |
| D-025-21 | 结构化协商帧 ANP 1.0 | 2026-05-05 | ANP 1.0+Ambiguity Tax |
| D-025-22 | 协议形式化验证 TLA+/Coq | 2026-05-05 | SentinelAgent+ACP v1.27 |
| D-025-23 | 潜空间 Agent 间通信 | 2026-05-05 | Interlat(ZJU+阿里) |
| D-025-24 | 多维向量信誉 TrustFlow | 2026-05-05 | TrustFlow 98% P@5 |
| D-025-25 | 上下文腐烂防护 | 2026-05-05 | Context Rot+ACON |
| D-025-26 | 用户同意编排 | 2026-05-05 | Google A2A Enhancement |
| D-025-27 | Vibe Coding 深度优化 2026 | 2026-05-05 | BridgeMind+Vibe Coding Review |
| D-025-28 | 宪法治理与 Critic-with-veto | 2026-05-05 | Council+Microsoft AGT KB 决策记录 0006+HC-12 |
| D-025-29 | Agent 免疫系统 | 2026-05-05 | ClawGuard 285+安全模式 |
| D-025-30 | 选择性遗忘与被遗忘权 | 2026-05-05 | FSFM+EU AI Act 2026 |
| D-025-31 | 碳排放追踪 | 2026-05-05 | CodeCarbon+Graviton5 |
| D-025-32 | 空转综合征检测 | 2026-05-05 | OpenClaw 事故+agent-loop-detector |
| D-025-33 | Agent 知识蒸馏 | 2026-05-05 | KD-MARL+AgentDistill+AgentArk |
| D-025-34 | 硬件感知路由 | 2026-05-05 | HW-Router(UCF) |
| D-025-35 | 多协议网关 | 2026-05-05 | AgentGateway(LF)+agentlink+AGNTCY |
| D-025-36 | Agent 互联总线 | 2026-05-05 | AGNTCY(Cisco)+A2A v1.0 反馈 |
| D-025-37 | 因果溯源引擎 | 2026-05-05 | CTEGs+DebugABot |
| D-025-38 | 失败归因引擎 | 2026-05-05 | 17x Error Trap+Sentry |
| D-025-39~46 | 容量升级决策(见§17.4) | 2026-05-10 | 容量缺口分析 |
| D-025-47 | 蓝图模板 v3.5/v3.6 升级 | 2026-05-14 | 模板升级要求 |

---

## 蓝图特有：盲点溯源（150 条）

### 第一轮 — 协议层（#1-#20）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 1 | Agent Card / 能力声明模型缺失 | 🔴 | §3 D-025-02 |
| 2 | A2A 任务状态机缺失 | 🔴 | §3 D-025-03 |
| 3 | Message/Part 类型缺失 | 🔴 | §3 D-025-04 |
| 4 | Supervisor/Coordinator 缺失 | 🔴 | §3 D-025-05 |
| 5 | Agent 间认证缺失 | 🔴 | §3 D-025-10 |
| 6 | 死锁防护缺失 | 🔴 | §3 D-025-09 |
| 7 | 活锁防护缺失 | 🔴 | §3 D-025-09 |
| 8 | 语义冲突检测缺失 | 🔴 | §3 D-025-07 |
| 9 | Living Spec 冲突预防缺失 | 🔴 | §3 D-025-06 |
| 10 | OWASP ASI07 完全暴露 | 🔴 | §3 D-025-10 |
| 11 | Agent Session Smuggling 无防御 | 🔴 | §3 D-025-10 |
| 12 | 级联故障防护缺失 | 🔴 | §3 D-025-12 |
| 13 | Rogue Agent 检测缺失 | 🔴 | §3 D-025-10 |
| 14 | 消息完整性校验缺失 | 🔴 | §3 D-025-10 |
| 15 | A2A 三层架构蓝图未定义 | 🔴 | §3 D-025-01 |
| 16 | 施工自指悖论未处理 | 🔴 | §3 D-025-11 |
| 17 | 经济护栏缺失 | 🟠 | §3 D-025-12 |
| 18 | SSE 流式传输缺失 | 🟠 | §3 D-025-04 |
| 19 | Push Notification 缺失 | 🟠 | §3 D-025-04 |
| 20 | 输入协商缺失 | 🟠 | §3 D-025-03 |

### 第二轮 — 上下文与集成层（#21-#40）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 21 | 跨 Agent 上下文压缩缺失 | 🟠 | §3 D-025-11 |
| 22 | 上下文污染检测缺失 | 🟠 | §3 D-025-11 |
| 23 | 上下文新鲜度/TTL 未定义 | 🟡 | §3 D-025-11 |
| 24 | 上下文溯源缺失 | 🟡 | §3 D-025-11 |
| 25 | 委托代价评估缺失 | 🟠 | §3 D-025-12 |
| 26 | 全链路 Token 预算未定义 | 🟠 | §3 D-025-12 |
| 27 | Agent 能力 vs 成本路由缺失 | 🟡 | §3 D-025-12 |
| 28 | 模型降级策略缺失 | 🟡 | §3 D-025-12 |
| 29 | 分布式追踪缺失 | 🟡 | §3 D-025-13 |
| 30 | A2A 专属指标缺失 | 🟡 | §3 D-025-13 |
| 31 | Agent 信誉/评分缺失 | 🟡 | §3 D-025-13 |
| 32 | Agent 生命周期管理缺失 | 🟡 | §3 D-025-05 |
| 33 | 优雅降级缺失 | 🟡 | §3 D-025-12 |
| 34 | Agent Card 版本/向后兼容缺失 | 🟡 | §3 D-025-02 |
| 35 | Agent A/B 测试缺失 | 🔵 | Phase beta |
| 36 | 陈旧 Agent 检测缺失 | 🟡 | §3 D-025-02 |
| 37 | 消息路由一致性缺失 | 🟡 | §3 D-025-10 |
| 38 | 任务幂等性缺失 | 🟡 | §3 D-025-15 |
| 39 | 任务优先级继承缺失 | 🟡 | §3 D-025-09 |
| 40 | 资源公平性调度缺失 | 🟡 | §3 D-025-05 |

### 第三轮 — Vibe Coding / 跨 IDE（#41-#55）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 41 | AGENTS.md 作为 A2A 发现入口未整合 | 🟠 | §3 D-025-12 |
| 42 | Skill Pack→Agent 角色→A2A 链条断裂 | 🟠 | §3 D-025-02 |
| 43 | 跨 IDE Agent 身份不统一 | 🟠 | §3 D-025-02 |
| 44 | 10+ 并发对话状态共享无机制 | 🟡 | §3 D-025-11 |
| 45 | 与 AgentOrchestrator 关系未定义 | 🟠 | §3 D-025-05 |
| 46 | 与 Session Handoff 边界模糊 | 🟡 | §3 D-025-03 |
| 47 | 与 Escalation Protocol 集成粗 | 🟡 | §3 D-025-08 |
| 48 | Well-known 标准化发现不适合本地 | 🟡 | §3 D-025-02 |
| 49 | 消息格式选型未做 | 🟡 | §3 D-025-04 |
| 50 | Coordinator 选型未做 | 🟡 | §3 D-025-05 |
| 51 | 1人+AI 简化 vs 架构完备度 | 🔵 | §3 D-025-12 |
| 52 | 100% AI 施工者=被限者利益冲突 | 🔴 | §3 D-025-11 |
| 53 | 多 IDE Agent Card 同步 | 🟡 | Phase beta |
| 54 | API 限流协调 | 🟡 | §3 D-025-05 |
| 55 | Agent 间通信人肉可观测性 | 🔵 | §3 D-025-04 |

### 第四轮 — 前沿安全（#56-#71）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 56 | Prompt Injection 跨 Agent 传播 | 🔴 | §3 D-025-10 |
| 57 | Agent 冒充 | 🔴 | §3 D-025-10 |
| 58 | 消息重放攻击 | 🔴 | §3 D-025-10 |
| 59 | Agent Card 篡改 | 🔴 | §3 D-025-02 |
| 60 | 委托链权限泄露 | 🔴 | §3 D-025-10 |
| 61 | 跨协议攻击 | 🟠 | Phase beta |
| 62 | 仲裁规则被 AI 弱化 | 🔴 | §3 D-025-11 |
| 63 | 上下文包隐藏指令 | 🟠 | §3 D-025-11 |
| 64 | 模态原生路由安全性 | 🟡 | §3 D-025-04 |
| 65 | OWASP ASI09 Human-Agent Trust | 🟠 | §3 D-025-08 |
| 66 | Agent 心跳伪造 | 🟡 | §3 D-025-10 |
| 67 | 系统时间操纵绕过 TTL | 🟡 | §3 D-025-11 |
| 68 | AI 生成的安全测试绕过后门 | 🟡 | §3 D-025-11 |
| 69 | 仲裁日志被篡改 | 🟡 | MOD-INF-020 |
| 70 | Agent Card 能力漂移 | 🟠 | §3 D-025-20 |
| 71 | IDE 崩溃后 Agent 状态恢复 | 🟡 | §3 D-025-12 |

### 第五轮 — 共识/涌现/事务（#72-#96）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 72 | 多 Agent 共识协议缺失 | 🔴 | §3 D-025-13 |
| 73 | 投票/多数决机制缺失 | 🟠 | §3 D-025-13 |
| 74 | Agent 间协商协议缺失 | 🟠 | §3 D-025-13 |
| 75 | 协商失败降级路径缺失 | 🟠 | §3 D-025-13 |
| 76 | Agent 合谋检测缺失 | 🔴 | §3 D-025-14 |
| 77 | 虚假任务完成 | 🔴 | §3 D-025-14 |
| 78 | 跨 Agent 行为传播 | 🔴 | §3 D-025-14 |
| 79 | 战略性破坏 | 🔴 | §3 D-025-14 |
| 80 | ML 异常检测管道缺失 | 🟠 | §3 D-025-14 |
| 81 | 5 类异常分类学缺失 | 🟠 | §3 D-025-14 |
| 82 | Cross-Agent Semantic Flow 缺失 | 🟠 | §3 D-025-14 |
| 83 | Agent 间 back-pressure 缺失 | 🟠 | §3 D-025-14 |
| 84 | 多 Agent Saga 事务缺失 | 🟠 | §3 D-025-15 |
| 85 | 补偿事务注册表缺失 | 🟠 | §3 D-025-15 |
| 86 | 部分失败检查点缺失 | 🟡 | §3 D-025-15 |
| 87 | 幂等性保证缺失 | 🟡 | §3 D-025-15 |
| 88 | 协议版本协商缺失 | 🟡 | Phase beta |
| 89 | Lazy Context Loading 缺失 | 🟠 | Phase beta |
| 90 | Prompt Caching 缺失 | 🟠 | Phase beta |
| 91 | Shared Memory File vs Chat | 🟡 | §3 D-025-12 |
| 92 | 质量改进阈值终止 | 🟡 | §3 D-025-12 |
| 93 | 模型路由实时成本感知 | 🟡 | §3 D-025-12 |
| 94 | Agent Warm Start 缺失 | 🟡 | Phase beta |
| 95 | Agent 离线/退役协议缺失 | 🟡 | §3 D-025-05 |
| 96 | 多 Agent 测试/仿真策略缺失 | 🟡 | Phase scaffold |

### 第六轮 — 协议安全/协商帧/形式化/潜空间/信誉/腐烂/同意/Vibe（#97-#123）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 97 | Agent Card 供应链操纵 | 🔴 | §3 D-025-20 |
| 98 | Agent Card 欺骗 | 🔴 | §3 D-025-20 |
| 99 | Task 流操纵 | 🔴 | §3 D-025-20 |
| 100 | Artifact 投毒 | 🔴 | §3 D-025-20 |
| 101 | Agent 间 DoS 洪水 | 🔴 | §3 D-025-20 |
| 102 | 自然语言歧义税 40% | 🔴 | §3 D-025-21 |
| 103 | ZK 零知识身份证明缺失 | 🟠 | §3 D-025-21 |
| 104 | 委托链权威性缩减 | 🟠 | §3 D-025-21 |
| 105 | A2A 协议死锁自由未形式化证明 | 🔴 | §3 D-025-22 |
| 106 | 委托链安全属性未 TLA+ 建模 | 🟠 | §3 D-025-22 |
| 107 | 时间感知准入控制缺失 | 🟠 | §3 D-025-22 |
| 108 | 偏差崩溃(Deviation Collapse) | 🟡 | §3 D-025-22 |
| 109 | 通信媒介瓶颈 | 🟠 | §3 D-025-23 |
| 110 | 上下文压缩失败驱动优化 | 🟡 | §3 D-025-23 |
| 111 | 标量信誉太粗糙 | 🟠 | §3 D-025-24 |
| 112 | 自底向上信誉涌现 | 🟡 | §3 D-025-24 |
| 113 | 抗女巫/洗信誉/投票环 | 🟡 | §3 D-025-24 |
| 114 | 上下文腐烂 | 🔴 | §3 D-025-25 |
| 115 | 经验跟随属性自降解 | 🟠 | §3 D-025-25 |
| 116 | 跨 Agent 数据共享用户同意缺失 | 🔴 | §3 D-025-26 |
| 117 | Token 生命周期控制缺失 | 🟠 | §3 D-025-26 |
| 118 | 同意疲劳 | 🟡 | §3 D-025-26 |
| 119 | No-AI Time 协议状态缺失 | 🟡 | §3 D-025-27 |
| 120 | 三层上下文架构缺失 | 🟡 | §3 D-025-25 |
| 121 | Agent 休眠/唤醒协议缺失 | 🟡 | §3 D-025-27 |
| 122 | A2A 协议模糊测试缺失 | 🟡 | §3 D-025-27 |
| 123 | Agent 间 adversarial prompt 传播 | 🟠 | §3 D-025-27 |

### 第七轮 — 宪法/免疫/遗忘/碳/空转/蒸馏/硬件（#124-#142）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 124 | Agent 宪法约束层缺失 | 🔴 | §3 D-025-28 |
| 125 | HC-12 零容忍门控缺失 | 🔴 | §3 D-025-28 |
| 126 | 意图漂移检测缺失 | 🔴 | §3 D-025-28 |
| 127 | 政策合规伤害检测缺失 | 🟠 | §3 D-025-28 |
| 128 | Agent 免疫系统缺失 | 🔴 | §3 D-025-29 |
| 129 | 跨 Agent 攻击链检测缺失 | 🟠 | §3 D-025-29 |
| 130 | 工具调用运行时策略治理缺失 | 🟠 | §3 D-025-29 |
| 131 | 选择性遗忘机制缺失 | 🟠 | §3 D-025-30 |
| 132 | Agent 间遗忘传播缺失 | 🟠 | §3 D-025-30 |
| 133 | 安全触发紧急遗忘缺失 | 🟡 | §3 D-025-30 |
| 134 | 硬件信号驱动路由缺失 | 🟡 | §3 D-025-34 |
| 135 | Agent 推理 disaggregated 调度 | 🔵 | §3 D-025-34 |
| 136 | Agent 知识蒸馏缺失 | 🟡 | §3 D-025-33 |
| 137 | MCP Box 零交互传递缺失 | 🟡 | §3 D-025-33 |
| 138 | 碳排放追踪缺失 | 🔵 | §3 D-025-31 |
| 139 | 模型选择碳代价未纳入 | 🔵 | §3 D-025-31 |
| 140 | 空转综合征检测缺失 | 🟠 | §3 D-025-32 |
| 141 | Agent 闲置消费陷阱 | 🟡 | §3 D-025-32 |
| 142 | 跨 IDE Agent 状态仪表盘缺失 | 🟡 | §3 D-025-32 |

### 第八轮 — 多协议网关/失败归因（#143-#153）

| # | 盲点 | 严重性 | 蓝图落位 |
|---|------|:---:|---------|
| 143 | IBM ACP 联邦编排缺失 | 🟡 | §3 D-025-35 |
| 144 | Agent 多协议网关缺失 | 🟡 | §3 D-025-35 |
| 145 | Agent Card 技能参数化缺失 | 🟡 | §3 D-025-35 |
| 146 | 授权蠕变风险 | 🟡 | §3 D-025-36 |
| 147 | 协议版本协商机制缺失 | 🟡 | §3 D-025-35 |
| 148 | 多 Agent 因果溯源模型缺失 | 🟡 | §3 D-025-37 |
| 149 | Agent 间失败模式组合爆炸 | 🟠 | §3 D-025-38 |
| 150 | Agent Skills Marketplace 缺失 | 🔵 | §3 D-025-35 |
| 151 | Agent 身份可移植性 | 🔵 | §3 D-025-02 |
| 152 | Agent-to-Human Warm Transfer | 🟡 | §3 D-025-26 |
| 153 | 多 Agent 跨伦理对齐验证 | 🔵 | §3 D-025-28 |

---

## Vibe Coding 铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 |
|---|------|
| 1 | 源头追溯——代码文件 MUST 标注 `[BLUEPRINT] MOD-INF-025 \| blueprint.md \| §{N}` |
| 2 | 不变量声明——代码文件 MUST 标注 `[INVARIANTS]` |
| 3 | 修改守卫——代码文件 MUST 标注 `[MODIFY-GUARD]` |
| 4 | 依赖声明——代码文件 MUST 标注 `[CONSUMERS]` |
| 5 | 蓝图锚点——蓝图 MUST 标注蓝图模板+AI 压缩工作流标准链接 |
| 6 | 漂移检测——蓝图 §0 文件清单 ↔ 代码 `[BLUEPRINT]` MUST 双向对齐 |
| 7 | 禁止占位符——禁止 TODO/.../pass/NotImplementedError |
| 8 | 编辑优先——禁止删除+重建，必须 surgical edit |
| 9 | 最小变更——只改必须改的 |
| 10 | 假设显式化——不确定 MUST 标记 `[ASSUMPTION]` |
| 11 | 步骤验证门——每步完成 MUST 验证后才进下一步 |
| 12 | 导入验证——使用任何 import/API 前 MUST Grep/Read 确认存在 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

## 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

| # | 规则 |
|---|------|
| 1 | 删除前 MUST 执行 RULE-THREE 三步审判（登记检查→重复检查→逐行价值检查） |
| 2 | 临时文件（_temp*/_check*/_fix*/_phase_*）删除前 MUST 确认内容价值 |
| 3 | 删除后 MUST 运行 `python scripts/governance/d11_compliance/audit_registration.py` 确认无孤儿 |

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| 链接 | 路径 |
|------|------|
| 蓝图模板 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` |
| 压缩工作流标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` |
| 代码构建标准 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` |
| 治理方法论 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` |
| 脚本质量标准 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` |
| 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` |
| 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` |
| Agent Spec | `D:\ZephyrAlpha\src\zephyr\agent-spec\` |

## 已有类似功能

| 功能 | 模块 | 区别 |
|------|------|------|
| AgentOrchestrator | MOD-INF-022 | A2A Supervisor 在其之上构建，复用 6 角色×10 域路由矩阵 |
| Session Handoff | KBG-0041 | A2A 委托上下文包字段格式对标 HandoffPackage，但 A2A 是 Agent 间交接 |
| Escalation Protocol | MOD-INF-022 | A2A 仲裁三级输出对齐 Escalation 三级 |

## 涉及的文件范围

| 操作 | 文件范围 |
|------|---------|
| 新建 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer3_coordination\script_*.py` (14 个容量扩展文件) |
| 修改 | `D:\ZephyrAlpha\src\zephyr\infra_ops\a2a_protocol\layer1_discovery\agent_card.py` (容量参数扩展) |
| 修改 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` |
| 修改 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` |


## Consumers
- zephyr.a2a_protocol (internal)
