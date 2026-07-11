---
module_id: MOD-INF-019
submodule_path: src/zephyr/autonomy_core
title: "可执行 Agent Spec 蓝图 — 蓝图→Skill 升级引擎"
doc_type: blueprint
status: Active
version: "0.19.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
last_updated: "2026-05-15"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/autonomy_core/
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "可执行 Agent Spec——将蓝图转化为 AI Agent 可执行操作手册，按领域+角色双维度组织，通过 AGENTS.md 路由 + Progressive Disclosure 按需加载。"
tags: [agent-spec, skill, executable-blueprint, codified-context, progressive-disclosure, skill-security, canary-deployment, skill-lifecycle, kill-switch, skill-economics, compliance, kya, sandbox, cross-model, skill-ontology, prompt-engineering, attention-economics, idempotency, circuit-breaker, shadow-deploy, skill-contract, self-learning, feature-flags, model-evolution, silent-failure, xai-explainability, confidence-calibration, context-isolation, multi-skill-consensus, cognitive-preservation, workflow-orchestration, prompt-caching, skill-knowledge_base, dependency-injection, output-guardrails, team-composition, skill-discovery]
priority: P0
runtime_plane: hot
depends_on:
  - {target: "MOD-GATE_ENGINE", at: "全篇", why: "Gate Engine——门禁验证"}
  - {target: "MOD-CONTEXT_ENGINE", at: "全篇", why: "Context Engine——上下文注入"}
  - {target: "MOD-INF-009", at: "全篇", why: "Pipeline——多模型路由"}
  - {target: "MOD-INF-018", at: "§2", why: "Agent RBAC——Skill 加载权限检查"}
  - {target: "MOD-INF-020", at: "§2", why: "Audit Trail——Skill 执行审计闭环"}
  - {target: "MOD-FEEDBACK_LOOP", at: "§4", why: "Feedback Loop——预测-诊断-修复闭环"}
  - {target: "MOD-INF-021", at: "§3", why: "Rollback System——Skill 执行失败回滚"}
  - {target: "MOD-INF-022", at: "§3", why: "Escalation Protocol——升级/委托路线"}
  - {target: "MOD-INF-024", at: "§2", why: "Budget Enforcer——token 预算管控"}
  - {target: "MOD-INF-023", at: "全篇", why: "Drift Detector——漂移检测"}
  - {target: "MOD-INF-005", at: "§2", why: "Script System——审计管线整合"}
  - {target: "MOD-KB-001", at: "§4", why: "Knowledge Base——新模式沉淀为 KE"}
  - {target: "MOD-LLM_SECURITY", at: "§8", why: "LLM Security Gateway——注入攻击检测"}
  - {target: "MOD-INF-025", at: "§3", why: "A2A Protocol——Agent间协调后加载规格"}
  - {target: "MOD-DATABASE", at: "§10", why: "Database——间接依赖(019→018→007→005→012)"}
ssot_claims:
  - {content: "Agent Spec 核心架构设计", source: "本蓝图 §1-§10"}
  - {content: "Agent Spec 接口契约", source: "本蓝图 §4"}
  - {content: "Domain Skill 列表", source: "skill-registry.yaml"}
  - {content: "四层架构定义", source: "本蓝图 蓝图特有"}
  - {content: "可观测性 Skill 是 MOD-INF-015 (System Telemetry) 的代理封装，非独立可观测性实现", source: "skill_observability.py + skill_telemetry.py → MOD-INF-015"}
template_for: blueprint
codification_level: L2
last_verified: "2026-05-15"
codification_at: "2026-05-15"
generation: 2
functional_domain: intelligence
value_stream: line3
value_stream_role: Skill加载
governance_domain: MOD-GOVERNANCE
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
references: []
responsibility_domain: 
design_maturity: design
build_status: planned
---

# Agent Spec 蓝图+施工图 — 蓝图→Skill 升级引擎

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 未注册 Skill 数 | 0 | ≥3 | ❌ |
> | Skill 加载失败率 | 0% | ≥10% | ❌ |
> | 新模块无 Skill 覆盖率 | 0% | ≥20% | ❌ |
>
> **为什么现在不自动化**: Agent Spec 是一次性注册系统——Skill 注册完就完了，不需要周期性自动运行。当前 21 Domain + 3 Role Skill 已覆盖核心场景。
> **什么时候建**: 当未注册 Skill ≥3（新模块大量增加），或 Skill 加载失败率 ≥10%，或 Owner 要求 Skill 自发现自注册时。
> **自动化宿主**: CircadianScheduler `hour=4` → `_skill_registration_scan()` + FLE `_periodic_checks()` → `_skill_health_check()`

> module_id: MOD-INF-019 | version: 0.19.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/agent-spec/ | generation: 2 | construction_progress: partially_implemented

## 概述

本蓝图描述 Agent Spec——ZephyrAlpha 的 AI 能力发现与路由系统，采用 L0/L1/L2/L3 四层渐进披露架构。L0 永久加载核心规则（~500 token），L1 触发加载领域 Skill，L2 按需组合，L3 动态发现。通过关键词匹配 + BGE-M3 语义路由实现 O(log N) 能力发现。当前管理 21 个 Domain Skill + 3 个 Role Skill，目标覆盖全项目 55 模块。上游依赖 MOD-GATE_ENGINE/008/009/018，下游被 MOD-INF-020/026 消费。

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证 {temporal_type=permanent}

> 版本变更后 MUST 重新填写。

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> 存在性：未实现/已实现/已阻塞（MUST注明原因）/已废弃（MUST在§5.3说明）

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-019`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | spec_engine.py | §3.1 | SpecEngine 四阶段升级引擎 | 已实现 | — |
| 2 | skills/skill_model.py | §4.2 | Skill 数据模型（Pydantic V2） | 已实现 | — |
| 3 | skills/skill_loader.py | §3.1 | Skill 加载器 + Progressive Disclosure | 已实现 | — |
| 4 | skills/skill_executor.py | §3.1 | Skill 执行器 + 门禁 + 审计 | 已实现 | — |
| 5 | skills/skill_router.py | §3.1 | Skill 路由（原 trigger_router.py，重命名消除与 orchestrator 命名冲突） | 已实现 | — |
| 6 | skills/skill_rbac_registry.py | §3.1 | SpecRegistry 注册表 | 已实现 | — |
| 7 | skills/skill_factory.py | §3.1 | Skill 自动生成 | 已实现 | — |
| 8 | skills/skill_freshness.py | §3.1 | 新鲜度管理（720h 衰减） | 已实现 | — |
| 9 | skills/skill_lifecycle.py | §3.1 | 四阶段生命周期状态机 | 已实现 | — |
| 10 | skills/skill_security.py | §8 | Defense in Depth 四层防护 | 已实现 | — |
| 11 | skills/skill_evaluator.py | §9 | L1+L2+L3 三层评估 | 已实现 | — |
| 12 | skills/skill_canary.py | 蓝图特有 | 灰度部署 + A/B Test | 已实现 | — |
| 13 | skills/skill_kill_switch.py | §8 | 三种 kill 机制 | 已实现 | — |
| 14 | skills/skill_contract.py | §4.7 | Pre/Post/Invariant 契约 | 已实现 | — |
| 15 | skills/skill_observability.py | §6.1 | Trace/Span/Metric/Log | 已实现 | — |
| 16 | skills/skill_telemetry.py | §6.1 | 18 字段遥测 | 已实现 | — |
| 17 | skills/skill_resilience.py | §6.2 | 熔断器 + 隔离舱 + 降级 | 已实现 | — |
| 18 | skills/skill_cross_model.py | 蓝图特有 | 跨模型兼容性矩阵 | 已实现 | — |
| 19 | skills/skill_ontology.py | 蓝图特有 | 语义本体 + 知识图谱 | 已实现 | — |
| 20 | skills/skill_prompt_opt.py | 蓝图特有 | Token 优化 + 对抗鲁棒性 | 已实现 | — |
| 21 | skills/skill_model_evolution.py | 蓝图特有 | Model Fingerprint + Output Signature | 已实现 | — |
| 22 | skills/skill_explain.py | 蓝图特有 | XAI 可解释性 | 已实现 | — |
| 23 | skills/skill_calibration.py | 蓝图特有 | 置信度校准 + ECE | 已实现 | — |
| 24 | skills/skill_context_isolation.py | 蓝图特有 | Per-Skill Namespace 隔离 | 已实现 | — |
| 25 | skills/skill_consensus.py | 蓝图特有 | 多 Skill 共识辩论 | 已实现 | — |
| 26 | skills/skill_cognitive_preservation.py | 蓝图特有 | ADI Tracker + 认知退化防护 | 已实现 | — |
| 27 | skills/skill_temperature.py | 蓝图特有 | 每 Skill 温度策略 | 已实现 | — |
| 28 | skills/skill_workflow.py | 蓝图特有 | StateGraph + Gate Enforcer | 已实现 | — |
| 29 | skills/skill_durable.py | 蓝图特有 | 持久执行 + 中断恢复 | 已实现 | — |
| 30 | skills/skill_prompt_cache.py | 蓝图特有 | 三级 Prompt 缓存 | 已实现 | — |
| 31 | skills/skill_cache_provider.py | 蓝图特有 | 跨 Provider 缓存自适应 | 已实现 | — |
| 32 | skills/skill_knowledge_base.py | 蓝图特有 | 跨 Skill 经验知识库 | 已实现 | — |
| 33 | skills/skill_di.py | 蓝图特有 | Skill 依赖注入 | 已实现 | — |
| 34 | skills/skill_guardrails.py | §8 | 输出护栏三层校验 | 已实现 | — |
| 35 | skills/skill_team_optimizer.py | 蓝图特有 | SCI 三维团队选择 | 已实现 | — |
| 36 | skills/skill_discovery.py | §3.1 | 语义发现 + Embedding Index | 已实现 | — |
| 37 | skills/skill_sandbox.py | §8 | Docker 隔离沙箱 | 已实现 | — |
| 38 | skills/skill_compliance.py | §8 | EU AI Act/MiFID II 合规 | 已实现 | — |
| 39 | skills/skill_kya.py | §8 | KYA JWT 凭证管理 | 已实现 | — |
| 40 | skills/skill_lineage.py | §6.1 | 血缘追踪 | 已实现 | — |
| 41 | skills/skill_economics.py | §5.4 | Token×模型×会话成本 | 已实现 | — |
| 42 | skills/skill_postmortem.py | §6 | 事故复盘引擎 | 已实现 | — |
| 43 | skills/skill_gitops.py | 蓝图特有 | CI/CD 管线 | 已实现 | — |
| 44 | skills/skill_translator.py | 蓝图特有 | Cross-IDE 翻译 | 已实现 | — |
| 45 | skills/skill_breakage_checker.py | §4.6 | 语义版本断裂检测 | 已实现 | — |
| 46 | skills/skill_learning.py | 蓝图特有 | 自学习环 | 已实现 | — |
| 47 | skills/skill_feature_flags.py | 蓝图特有 | Feature Flag 渐进发布 | 已实现 | — |
| 48 | skills/skill_idempotency.py | §6.2 | 幂等性 + 去重 | 已实现 | — |
| 49 | skills/skill_shadow.py | 蓝图特有 | Shadow Mode 并行执行 | 已实现 | — |
| 50 | skills/skill_silent_failure.py | §6.2 | 静默失败检测 | 已实现 | — |
| 51 | skills/skill_locking.py | §16.12 | Skill 文件锁 | 已实现 | — |
| 52 | skills/skill_feedback.py | §3.1 | 反馈信号模型 | 已实现 | — |
| 53 | skills/skill_tokenomics.py | §5.4 | Token 经济学 | 已实现 | — |
| 54 | skills/skill_schema_registry.py | §4.7 | Schema 注册 | 已实现 | — |
| 55 | skills/skill_constructor.py | §3.1 | Skill 构造器 | 已实现 | — |
| 56 | skills/skill_risk_mitigator.py | §14 | 风险缓解 | 已实现 | — |
| 57 | skills/skill_efficacy_calibrator.py | §9 | 效能校准 | 已实现 | — |
| 58 | self_evolution_fidelity_gate.py | §9 | 自进化保真度门控 | 已实现 | — |
| 61 | file_autoregister.py | §3.1 | 文件自动注册（正确拼写版） | 已实现 | — |
| 62 | ide_watcher.py | §3.1 | IDE 热重载（CircadianScheduler hour=2 调度） | 已实现 | — |
| 63 | phase_planner.py | §16 | Phase 规划（CLI `python -m zephyr.agent_spec phase`） | 已实现 | — |
| 64 | agent_observability.py | §6.1 | Agent 可观测性（re-export shim → skill_observability.py） | 已实现 | — |
| 66 | all_skill_modules.py | §3.1 | 全量模块索引 | 已实现 | 本模块 |
| 67 | integration/pipeline_bridge.py | §12 | Pipeline 桥接 | 已实现 | 本模块 |
| 68 | __main__.py | §4.1 | CLI 入口 | 已实现 | 本模块 |
| 76 | skills/skill_attention.py | §3.1 | 注意力权重 | 已实现 | 本模块 |
| 77 | skills/skill_freshness_ext.py | §3.1 | 新鲜度扩展 | 已实现 | 本模块（3个消费者） |
| 79 | trigger_router.py | §3.1 | 触发表路由 | 已实现 | 本模块（2个消费者） |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| 代码 [BLUEPRINT] 头部指向 = 本蓝图 module_id | `grep "\[BLUEPRINT\]" *.py` 核对 module_id | ☐ |
| actual_disk_path 与 §11 产出物路径一致 | 路径核对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.19.0 (基线) | 80 个 .py + 21 Domain Skill + 3 Role Skill | — | — |

### §0.4 SSoT与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处（委托） | 委托目标 |
|---|---------|:----------:|:---------------:|---------|
| 1 | Agent Spec 核心架构设计（§1-§10） | ✅ | ❌ | — |
| 2 | Agent Spec 接口契约（§4） | ✅ | ❌ | — |
| 3 | Domain Skill 列表 | ❌ | ✅ | skill-registry.yaml |
| 4 | 四层架构定义 | ✅ | ❌ | AGENTS.md 以本蓝图为准 |
| 5 | Skill 注册/发现 Schema | ✅ | ❌ | MOD-INF-035 CapabilityRegistry 概念重叠（见 §10.5） |
| 6 | 触发表路由规则 | ❌ | ✅ | skill-registry.yaml task_keywords |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/agent-spec/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |

---

## MOD-GOVERNANCE 集成契约锚点 {temporal_type=permanent}

> 权威定义见 [`../../_domain_governance/blueprint.md`](../../_domain_governance/blueprint.md) §3。

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-007 | 产出方（Spec → RBAC / Audit 消费） | MOD-INF-018 / MOD-INF-020 |

---

## §1 设计背景与目标 {temporal_type=permanent}

### 1.1 背景

蓝图是纯文档，AI 每次需人类口头指挥"下一步做什么"；蓝图没有加载机制，AI 不知道该读哪份蓝图；蓝图没有版本化执行，AI 可能用过期蓝图施工；蓝图没有审计闭环，无法验证 AI 是否按蓝图执行。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 蓝图→Skill 自动升级引擎 | SpecEngine 四阶段 |
| 2 | ✅ 包含 | 四层渐进披露加载 | L0→L1→L2→L3 |
| 3 | ✅ 包含 | 关键词+语义路由 | O(log N) 能力发现 |
| 4 | ✅ 包含 | Skill 全生命周期管理 | active→deprecated→retired→removed |
| 5 | ✅ 包含 | Skill 安全防护 | Defense in Depth 四层 |
| 6 | ✅ 包含 | Skill 执行审计闭环 | 对接 MOD-INF-020 |
| 7 | ❌ 排除 | 具体业务逻辑实现 | 各 Domain Skill 自身负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 施工轨道：T轨可施工 | AI 可自主修改 ai_modifiable 部分 |
| 多 IDE 并发（TRAE/Cursor/RooCode） | Skill 加载机制 MUST 跨 IDE 统一——AGENTS.md 是唯一所有 IDE 都读的文件 |
| 10+ 并发对话 | 不能加载全部 Skill——Progressive Disclosure 三层递进 |
| 1 人 + AI 施工 + AI 维护 | Domain Skill 按模块创建，Role Skill 固定 3 个角色模式 |
| 14 层 × 多模块扩展 | 新模块创建时同步创建 Domain Skill |
| 跨 AI 模型（DeepSeek/GLM/Kimi/Qwen/Claude） | Skill 格式 MUST 对多模型友好——结构化表格 > 长篇散文 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 + 安全审批 | 设计+施工 | 审批权限 |
| AI 施工者 | Skill 加载→执行→产出 | 施工 | 遵循 Skill 指令 |
| 下游模块（RBAC/Audit） | Skill 事件格式 | 集成 | 契约兼容 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| Skill 覆盖 | 3 Role Skill | 19 Domain + 3 Role | Domain Skill 未创建 | P0 |
| 路由方式 | 关键词匹配 | 语义路由 BGE-M3 | 语义路由未实现 | P1 |
| 安全防护 | 基础校验 | Defense in Depth 四层 | 沙箱+审计未集成 | P1 |
| 审计闭环 | 无 | Skill 事件→Audit Trail | 集成未完成 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 新模块接入 | 创建新蓝图 | Factory Agent 问3问题→生成 SKILL.md→注册→更新触发表 | Domain Skill |
| Skill 加载 | AI session 启动 | AGENTS.md 触发表匹配→L1 metadata→L2 body→L3 references | Skill 指令注入上下文 |
| Skill 漂移 | 蓝图变更 | FreshnessScore 降分→触发重审→更新 Skill | 更新后的 Skill |
| Skill 执行失败 | 门禁 FAIL | Checkpoint 回滚→Escalation→人工审查 | 修复方案 |

---

## §2 模块边界 {temporal_type=permanent}

### 2.1 职责边界

**核心职责声明**：将静态蓝图转化为 AI Agent 可执行操作手册（Skill），按领域+角色双维度组织，通过 AGENTS.md 路由 + Progressive Disclosure 按需加载。（职责数=5）

| # | 类型 | 职责 | 详情 | 负责方 | 与其他蓝图重叠？ |
|---|:----:|------|------|--------|---------------|
| 1 | ✅ 包含 | 蓝图→Skill 升级引擎 | SpecEngine 四阶段：discover→generate→validate→register | 本模块 | 无 |
| 2 | ✅ 包含 | Skill 渐进加载 | Progressive Disclosure L1→L2→L3 | 本模块 | ⚠️ MOD-CONTEXT_ENGINE Context Engine 概念重叠（上下文注入），但粒度不同 |
| 3 | ✅ 包含 | Skill 路由 | 关键词 + 语义 fallback | 本模块 | 无 |
| 4 | ✅ 包含 | Skill 生命周期管理 | 四阶段状态机 + 新鲜度 | 本模块 | 无 |
| 5 | ✅ 包含 | Skill 安全防护 | 注入检测 + 沙箱 + 审计 | 本模块 | 无 |
| 6 | ❌ 排除 | 具体业务逻辑 | 各 Domain Skill 自身负责 | 各模块 | — |
| 7 | ❌ 排除 | 权限判定 | MOD-INF-018 负责 | MOD-INF-018 | — |
| 8 | ❌ 排除 | 审计存储 | MOD-INF-020 负责 | MOD-INF-020 | — |
| 9 | ❌ 排除 | 运行时能力发现 | MOD-INF-035 CapabilityRegistry 负责 | MOD-INF-035 | ⚠️ 概念重叠——Spec=蓝图→Skill升级，CR=运行时能力查询 |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 蓝图→Skill 升级引擎 | [MOD-INF-018, MOD-INF-035] | `python scripts/governance/check_ssot_uniqueness.py --blueprint MOD-INF-019` |
| Skill 渐进加载 | [MOD-CONTEXT_ENGINE] | 同上 |
| Skill 路由 | [MOD-MASTER_BLUEPRINT] | 同上（MOD-MASTER_BLUEPRINT 已声明委托） |
| Skill 生命周期管理 | [MOD-INF-035] | 同上 |
| Skill 安全防护 | [MOD-INF-018, MOD-INF-020] | 同上 |

---

## §3 架构设计 {temporal_type=permanent}

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | SpecEngine | 蓝图→Skill 升级引擎 | MOD-GATE_ENGINE, MOD-CONTEXT_ENGINE | 同步调用 |
| 2 | SkillLoader | Skill 加载与缓存 | MOD-INF-018 (RBAC) | 同步调用 |
| 3 | SkillRouter | 关键词/语义路由 | MOD-INF-011 (VectorMemory) | 同步调用 |
| 4 | ProgressiveDisclosure | 三层递进加载 | — | 同步调用 |
| 5 | SkillFactory | Skill 自动生成 | MOD-INF-009 (Pipeline) | 同步调用 |
| 6 | FreshnessTracker | Skill 新鲜度管理 | MOD-INF-023 (Drift) | 事件 |
| 7 | SkillExecutor | Skill 执行编排 | MOD-INF-020, MOD-INF-021 | 同步调用 |
| 8 | SkillLifecycle | 四阶段生命周期 | — | 状态机 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | AGENTS.md | 触发表匹配→skill_id | SkillLoader | YAML→Dict | 正则+关键词→skill_id |
| 2 | SkillLoader | L1→L2→L3 渐进加载 | SkillExecutor | SkillModel(Dict) | YAML frontmatter→Pydantic |
| 3 | SpecEngine | discover→generate→validate→register | SkillFactory | UpgradeResult(Dict) | 蓝图章节→SKILL.md |
| 4 | SkillExecutor | 执行+门禁+审计 | Audit Trail | AuditEvent(Dict) | 执行结果→审计条目 |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| unloaded | 路由匹配 | loading | 触发表有匹配项 |
| loading | 加载完成 | active | YAML frontmatter 合法 |
| loading | 加载失败 | unloaded | FileNotFoundError/TimeoutError |
| active | 会话结束 | unloaded | — |
| active | 蓝图变更 | stale | freshness_score < 阈值 |
| stale | 重审通过 | active | freshness_score ≥ 阈值 |
| active | 废弃决策 | deprecated | Owner 审批 |
| deprecated | 30d 过渡期结束 | retired | 无下游引用 |
| retired | 清理决策 | removed | Owner 审批 |

---

## §4 接口契约 {temporal_type=permanent}

> 强制 Pydantic V2 BaseModel（KBG-0040），禁止 `@dataclass`。

### 4.1 公共 API

```python
class SpecEngine:
    """蓝图→Skill 升级引擎"""
    def upgrade(self, blueprint_path: str) -> UpgradeResult: ...
    def upgrade_batch(self, blueprint_paths: List[str]) -> List[UpgradeResult]: ...
    def status(self, skill_id: Optional[str] = None) -> Dict[str, Any]: ...
    def validate_skill(self, skill_id: str) -> Dict[str, Any]: ...

class SkillLoader:
    """Skill 渐进加载器"""
    def load_l0(self) -> Dict[str, Any]: ...
    def progressive_load(self, skill_id: str) -> Dict[str, Any]: ...
    def progressive_load_full(self, skill_id: str) -> Dict[str, Any]: ...
    def load_l3_reference(self, skill_id: str, ref_name: str) -> str: ...
    def check_token_budget(self, domain_skill_id: str, role_skill_id: str) -> Dict[str, Any]: ...

class SkillExecutor:
    """Skill 执行编排器"""
    def execute(self, skill_id: str, task_description: str = "") -> Dict[str, Any]: ...
    def get_audit_trail(self) -> List[Dict[str, Any]]: ...

class SkillRouter:
    """触发表路由"""
    def route(self, stage: Optional[ConstructionStage], task_description: str) -> Tuple[str, Optional[str]]: ...

class SpecRegistry:
    """Skill 注册表"""
    def register(self, capability: AgentCapability) -> None: ...
    def get(self, agent_id: str) -> Optional[AgentCapability]: ...
    def list_all(self) -> List[Dict[str, Any]]: ...
    def list_by_category(self, category: str) -> List[Dict[str, Any]]: ...
    def reload(self) -> None: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `SpecEngine.upgrade()` | ①discover 蓝图章节 → ②generate SKILL.md → ③validate 格式 → ④register 到注册表 | validate 失败→降级为 draft |
| `SkillLoader.progressive_load()` | ①加载 L1 frontmatter → ②加载 L2 body → ③压缩 CRITICAL 规则 → ④返回分层结果 | token 超预算→降级跳过 L3 |
| `SkillExecutor.execute()` | ①创建checkpoint → ②加载Skill → ③RBAC检查 → ④门禁检查 → ⑤执行 → ⑥审计写入 → ⑦反馈闭环 → ⑧返回结果 | RBAC拒绝→升级；门禁FAIL→回滚+升级；执行异常→熔断 |
| `SkillRouter.route()` | ①施工阶段匹配 → ②正则匹配任务描述 → ③语义fallback BGE-M3 → ④返回(role, domain) | 无匹配→fallback implementer |

### 4.2 数据模型

```python
class SkillTier(str, Enum):
    L0_CONSTITUTION = "L0"
    L1_DOMAIN = "L1"
    L2_ROLE = "L2"
    L3_COLD_MEMORY = "L3"

class SkillType(str, Enum):
    DOMAIN = "domain"
    ROLE = "role"

class SkillStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    REMOVED = "removed"

class ProgressiveLevel(str, Enum):
    L1_METADATA = "L1"
    L2_BODY = "L2"
    L3_REFERENCES = "L3"

class SkillModel(BaseModel):
    skill_id: str = Field(pattern=r"^SKILL-[A-Z]{3}-[A-Z]{2,3}-\d{3}$")
    name: str
    description: str
    skill_type: SkillType
    tier: SkillTier
    status: SkillStatus = SkillStatus.ACTIVE
    allowed_tools: List[str]
    model_hint: Optional[str] = None
    freshness_score: float = Field(default=100.0, ge=0.0, le=100.0)
    last_validated: Optional[datetime] = None
    version: str = "0.1.0"
    token_budget_l1: int = 50
    token_budget_l2: int = 500
    path: str
    references: List[str] = []
    upstream_modules: List[str] = []

class AgentCapability(BaseModel):
    agent_id: str
    capabilities: list[str] = []
    version: str = "1.0.0"
    spec_hash: str = ""

class ConstructionStage(str, Enum):
    IDEA = "idea"
    PRE_AUDIT = "pre_audit"
    BLUEPRINT = "blueprint"
    CONSTRUCTION = "construction"
    VERIFICATION = "verification"
    POST_AUDIT = "post_audit"
```


### 4.2b 数据模型 SSoT 声明

| 模型名 | 唯一真源文件 | 多文件同名？ | 处置 |
|--------|------------|:----------:|------|
| SkillModel | skill_model.py | 否 | — |
| SkillStatus | skill_model.py | ✅ 已解决 | guard 版本已重命名为 SkillSecurityStatus（F12） |
| AgentCapability | registry.py | 否 | — |
| ConstructionStage | skill_router.py | 否 | — |
| SkillTier/SkillType/ProgressiveLevel | skill_model.py | 否 | — |
### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `SpecEngine.upgrade()` | `blueprint_path` | ✅ | MUST 是存在的 .md 文件 |
| `SkillLoader.progressive_load()` | `skill_id` | ✅ | MUST 匹配 `SKILL-[A-Z]{3}-[A-Z]{2,3}-\d{3}` |
| `SkillExecutor.execute()` | `skill_id` | ✅ | 同上；`task_description` 可选 |
| `SkillRouter.route()` | `stage`, `task_description` | ❌/✅ | stage 可为 None；task_description MUST 非空 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `SpecEngine.upgrade()` | `UpgradeResult`：phase=complete, skill_id, skill_path | `UpgradeResult`：phase=failed, errors 列表 |
| `SkillLoader.progressive_load()` | `Dict`：l1/l2/l3 分层数据 | `FileNotFoundError` / `TimeoutError` |
| `SkillExecutor.execute()` | `Dict`：status=success, audit-trail, gate_results | `Dict`：status=failed, rollback_info |
| `SkillRouter.route()` | `Tuple[role, domain]` | `("implementer", None)` fallback |


### 4.3b Domain Skill 接口契约 Schema

> 时态属性：permanent——接口契约是永久时态，压缩时不可删除。

| 契约ID | Skill | 版本 | 输入Schema | 输出Schema | 关键约束 |
|--------|-------|:---:|-----------|-----------|---------|
| CT-001 | database-specialist | v1.0.0 | {blueprint_path: str, migration_type: enum[create|alter|drop]} | {sql_script: str, rollback_script: str, affected_tables: List[str]} | migration_type MUST 在 allowed-tools 白名单中 |
| CT-002 | mcp-specialist | v1.0.0 | {tool_name: str, tool_schema: dict, transport: enum[stdio|sse|streamable_http]} | {registration_id: str, validation_result: GateResult} | tool_schema MUST 符合 JSON Schema draft-07 |
| CT-003 | context-specialist | v2.0.0 | {session_id: str, max_tokens: int, priority_topics: List[str]} | {injected_context: str, token_count: int, compression_ratio: float} | max_tokens MUST ≤ 800 (combined L2 budget) |
| CT-004 | feedback-specialist | v1.0.0 | {skill_id: str, event_type: enum[predict|detect|diagnose|act|verify]} | {score: float, root_cause: str, fix_suggestion: str, verified: bool} | predict→float, detect→GateResult, diagnose→RootCauseAnalysis |
| CT-005 | gate-specialist | v1.0.0 | {check_id: str, target_path: str, check_type: enum[format|content|alignment]} | {passed: bool, score: float, findings: List[str]} | 3× consecutive FAIL → escalate to Owner |
| CT-006 | agent-specialist | v1.0.0 | {skill_id: str, requested_tools: List[str], operation: enum[load|execute|modify]} | {permission_level: enum[read_only|code_modify|admin], allowed: bool} | allowed-tools per Skill MUST be whitelist-validated |
| CT-007 | master-blueprint | v1.0.0 | {blueprint_path: str, section: str, action: enum[read|validate|upgrade]} | {content: str, validation_result: Dict, upgrade_result: UpgradeResult} | blueprint_path MUST exist on disk |
| CT-008 | drift-detector | v2.0.0 | {source_type: enum[blueprint|code|registry], source_id: str} | {drift_found: bool, drift_score: float, findings: List[DriftFinding]} | drift_score > 50 → emit skill.freshness_warning |
| CT-009 | knowledge-specialist | v1.5.0 | {topic: str, operation: enum[search|write|sync], provenance: dict} | {entries: List[KEEntry], sync_result: Dict} | provenance MUST contain build_provenance() output |
| CT-010 | architect (Role) | v1.0.0 | {module_id: str, design_question: str, constraints: List[str]} | {design_decision: str, adr_record: KB 决策记录_Record, affected_blueprints: List[str]} | design_decision MUST be traceable to §18 decision record |
| CT-011 | governor (Role) | v1.0.0 | {audit_scope: str, audit_type: enum[pre|post|drift], target_paths: List[str]} | {audit_report: AuditReport, findings: List[Finding], gate_results: List[GateResult]} | audit_report MUST be written to Audit Trail |
| CT-012 | implementer (Role) | v1.0.0 | {task_id: str, blueprint_section: str, code_change: CodeDiff} | {implementation_result: ImplResult, tests_passed: bool, gate_result: GateResult} | code_change MUST pass G7 gate before commit; no TODO/pass/NotImplementedError |
| CT-013 | lsg-security (LSG) | v1.0.0 | {input_text: str, scan_level: enum[L1_input|L3_output|L4_agent|L0_full]} | {scan_result: ScanResult, threats: List[ThreatFinding], blocked: bool} | blocked=true → MUST emit security.blocked event; MAX_INPUT_TOKENS=32768 |
| CT-014 | task_system (TSK) | v1.0.0 | {operation: enum[create|read|update|delete|dispatch], task_data: TaskCard} | {task_id: str, state: enum[draft|ready|in_progress|completed|closed], gate_result: GateResult} | dispatch MUST pass G7 gate; MAX_TASK_DEPTH=10 |
| CT-015 | system_telemetry (TEL) | v1.0.0 | {operation: enum[emit_metric|check_health|generate_alert|archive_rotate], payload: dict} | {result: TelemetryResult, health_status: HealthStatus} | check_health min interval 30s; ARCHIVE_RETENTION_DAYS=90 |
| CT-016 | code-dedup-engine (DED) | v1.0.0 | {scan_level: enum[lexical|ast|semantic], target_paths: List[str]} | {brs_score: float, duplicates: List[DupGroup], auto_fixed: bool} | BRS < 70 → 禁止 auto_fix; 3-wave scan: lexical→AST→semantic |
| CT-017 | budget-enforcer (BGT) | v1.0.0 | {operation: enum[pre_flight|track|degrade], budget_claim: BudgetClaim} | {decision: GateDecision, degradation_level: enum[NORMAL..HALT]} | 6-level degradation; trust_ring 2-of-3; pre_flight MUST before LLM call |
| CT-018 | auto-fix-engine (AFX) | v1.0.0 | {fix_level: enum[L1_rule|L2_llm|L3_ooda], error_context: ErrorContext} | {fix_result: FixResult, shadow_verified: bool, gray_fraction: float} | cascade_breaker threshold=3; shadow_timeout=30s; gray_default=0.1 |
| CT-019 | a2a-protocol (A2A) | v1.0.0 | {layer: enum[discovery|communication|coordination], agent_id: str, message: A2AMessage} | {routing_result: RouteResult, deadlock_detected: bool, cascade_guard: bool} | cascade_break_threshold=3; identity HMAC-SHA256; 3-layer protocol |
| CT-020 | behavioral-auditor (BEH) | v1.0.0 | {audit_scope: str, target_agent: str, operation_matrix: dict} | {verdict: AuditVerdict, findings: List[BehaviorFinding]} | verdict MUST write to AuditTrail as immutable event; self-audit recursive |
### 4.5 MCP 接口

本模块不暴露 MCP 接口。CLI 入口：`python -m zephyr.agent_spec [list|status|help]`

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Skill 文件 | ✅ 向后兼容 | 不影响已有消费者 |
| SkillModel 字段新增 | ✅ 向后兼容 | Pydantic 有默认值 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| SkillModel 字段删除/重命名 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| skill_id 格式变更 | ❌ 破坏性 | 正则匹配全项目 |
| 触发表路由规则变更 | ⚠️ 需通知 | 消费者需更新匹配逻辑 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### 4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| Skill 评估策略 | `SkillEvaluator` | L1+L2+L3 三层 | MUST 返回 pass/fail + score | 工厂注册 |
| 路由策略 | `SkillRouter` | 关键词 + 正则 | MUST 返回 (role, domain) | 配置注入 |
| 新鲜度衰减模型 | `FreshnessDecayModel` | 720h 线性衰减 | MUST 返回 0-100 分数 | 配置注入 |

---

## §5 约束条件 {temporal_type=permanent}

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Skill ID 格式 | `SKILL-[A-Z]{3}-[A-Z]{2,3}-\d{3}` |
| 2 | Skill 文件格式 | agentskills.io SKILL.md 标准 |
| 3 | 数据模型框架 | Pydantic V2 BaseModel（KBG-0040） |
| 4 | Skill Chain 深度上限 | 3 层 |
| 5 | 组合 token 预算 | Domain L2 + Role L2 ≤ 800 tokens |
| 6 | 新鲜度衰减周期 | 720h（30天） |
| 7 | 废弃过渡期 | 30d |
| 8 | Kill Switch 响应 | ≤ 5s 硬停止 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| .py 文件数 | 67 | 100 | — | ✅ | — |
| Domain Skill | 19 | 200 | — | ❌ | Factory Agent 批量生成 |
| 并发 AI | 10+ | 30 | — | ❌ | 三级缓存 |
| 路由条目 | 9 条正则 | 50 | — | ✅ | 语义路由升级 |

### 5.3 迁移/废弃方案

无迁移/废弃。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | Skill 加载成功率 | ≥ 99% | SkillLoader 日志 | 加载成功/总请求 | 99% | 每月≤7h | < 95% 告警 |
| 可维护性 | MTTR | < 30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |
| 性能 | Skill 加载延迟 | < 2s | 遥测 | P95 延迟 | 2s | — | > 5s 告警 |


### 5.5 自动化触发机制

| 操作 | 触发方式 | 调度策略 | 当前状态 |
|------|---------|---------|---------|
| Skill 新鲜度扫描 | auto_scheduled | CircadianScheduler hour=1 | ✅已实现 |
| IDE Skill 热重载 | auto_scheduled | CircadianScheduler hour=2 | ✅已实现 |
| Skill 自动废弃 | auto_event | freshness_critical 事件 | ✅已实现 |
| Skill 路由 | on_demand | — | ✅已实现 |
| Skill 渐进加载 | on_demand | — | ✅已实现 |
| 蓝图→Skill 升级 | on_demand | — | ✅已实现 |
| 语义路由（BGE-M3） | auto_boot | EmbeddingRouter local后端，复用 vector_memory 基础设施 | ⚠️待实现 |

#### 语义路由实现方案

| 维度 | 决策 | 依据 |
|------|------|------|
| 嵌入后端 | local（SentenceTransformer） | 零外部依赖、离线可用、延迟~50ms |
| 降级链 | BGE-M3→bge-small-zh→InMemory | 复用 EmbeddingRouter 已有降级链 |
| 依赖 | MOD-INF-011 vector_memory | EmbeddingRouter.embed_batch() |
| 路由策略 | 关键词精确匹配优先→语义余弦相似度 fallback | 关键词匹配=确定性，语义=模糊补位 |
| 相似度阈值 | cosine ≥ 0.7 | 低于阈值返回 None（走默认路由） |
| Skill 描述向量缓存 | 启动时预计算，存内存 | 22个Skill描述→22×1024矩阵，~90KB |
### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | `open(path, "w")` 省略 encoding | `open(path, "w", encoding="utf-8")` | 编码一致性 |
| 2 | 编码模式 | `for + subprocess.run()` 串行 | `ThreadPoolExecutor(max_workers=8)` | 性能 |
| 3 | 导入源 | `zephyr.infra_ops.*` 跨层导入 | `zephyr.agent_spec.*` 本包内 | 分层约束 |
| 4 | 编码模式 | Skill 指令使用"建议/最好/推荐" | 强制 Checklist + CRITICAL 前缀 | 弱指令=执行不可靠 |

---

## §6 错误处理 {temporal_type=permanent}

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | Skill 文件不存在 | FileNotFoundError | 降级到 L3 冷记忆检索 | 当前 Skill 不可用 |
| 2 | Skill 加载超时 | TimeoutError (>2s) | 返回默认 Role Skill | 功能降级 |
| 3 | 路由匹配失败 | NoMatchError | 语义 fallback BGE-M3 | 可能加载错误 Skill |
| 4 | RBAC 权限不足 | PermissionDenied | 升级到人类审批 | 当前操作阻塞 |
| 5 | 蓝图-Skill 漂移 | DriftDetected | FreshnessScore 降分 | 触发重审流程 |
| 6 | 循环 Skill 调用 | CircularDependency | 检测+中断 | Chain 终止 |
| 7 | 上下文溢出 | ContextOverflow | 释放最旧 Skill | LRU 驱逐 |
| 8 | 门禁连续 FAIL | 3× GateResult(passed=False) | 升级到 Owner | 执行暂停 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| skill_load_duration_seconds | Histogram | 自动埋点 | P95 > 5s | P2 |
| skill_load_total | Counter | 自动埋点 | — | — |
| skill_load_fail_total | Counter | 自动埋点 | > 5/min | P1 |
| skill_freshness_score | Gauge | 自动上报 | < 50 | P2 |
| skill_execution_gate_fail_total | Counter | 自动埋点 | > 3/min | P1 |
| skill_chain_depth | Gauge | 自动上报 | > 3 | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| SkillLoader | L1 metadata | L2 body + L3 references | 只返回 frontmatter | 组件恢复健康 |
| SkillRouter | 默认 implementer | 精确路由 | fallback 规则 | 路由表更新 |
| SpecEngine | — | 全部升级功能 | 人工创建 Skill | 引擎恢复 |
| SkillExecutor | 只读操作 | 写入+执行 | 熔断+缓存回退 | 门禁通过 |
| FreshnessTracker | 全部（分数不更新） | 新鲜度评估 | 使用缓存分数 | 蓝图同步 |

---

## §8 安全考量 {temporal_type=permanent}

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | Skill 文件注入 | 恶意指令执行 | Defense in Depth 四层（Parse→Validate→Simulate→Audit） | 沙箱测试 |
| 2 | 跨 Skill 上下文污染 | 信息泄露 | Per-Skill namespace 隔离 | 隔离测试 |
| 3 | 权限越权 | 未授权操作 | RBAC per-tool-call 验证 | 权限矩阵测试 |
| 4 | 审计日志篡改 | 追溯失效 | Merkle Tree 防篡改 | 完整性校验 |
| 5 | Kill Switch 失效 | 紧急停止失败 | 5s 硬停止 + 多层触发 | 故障注入测试 |
| 6 | 模型幻觉注入 | 产出错误代码 | 输出护栏 + 运行时校验 | 对抗测试 |
| T1 | Skill文件篡改 | 恶意修改Skill内容 | 哈希校验+Audit Trail+pre-commit diff review | 完整性校验 |
| T2 | Skill权限提升 | 绕过allowed-tools限制 | allowed-tools白名单+CBAC | 权限矩阵测试 |
| T3 | Skill数据泄露 | PII/敏感信息泄露 | PII Masker+敏感模式匹配 | 数据扫描 |
| T4 | Skill链感染 | L3引用被污染 | L3 reference单独哈希+引用隔离 | 隔离测试 |
| T5 | Skill幻觉注入 | L1指令被注入无效规则 | L1指令有效性校验+人工复核 | 对抗测试 |

---

## §9 测试策略 {temporal_type=permanent}

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | SkillModel/SpecEngine/SkillLoader | 模型验证、升级流程、渐进加载 | 覆盖率 ≥ 80% |
| 2 | 集成测试 | SkillExecutor + 门禁 + 审计 | 执行→门禁→审计全链路 | 端到端通过 |
| 3 | 对抗测试 | 路径遍历/注入/空输入/损坏YAML | A1-A6 攻击面 | 全部拦截 |
| 4 | E2E 测试 | CLI 全流程 | discover→status→validate→upgrade | exit 0 |
| 5 | 回归测试 | Skill 更新后产出不退化 | SkillsBench paired eval | 通过率 ≥ 95% |

测试文件：
- `D:\ZephyrAlpha\tests\unit\test_agent_spec_backlog_phase1.py`
- `D:\ZephyrAlpha\tests\unit\test_agent_spec_backlog_phase2.py`
- `D:\ZephyrAlpha\tests\adversarial\test_agent_spec_adversarial.py`
- `D:\ZephyrAlpha\tests\adversarial\test_agent_spec_e2e.py`

### 三层评估体系

| 层级 | 评估维度 | 检查项/Metrics | 通过标准 |
|:---:|---------|---------------|---------|
| L1 | Instruction Validity | ①YAML格式合法 ②CRITICAL规则非空 ③allowed-tools合法 ④无占位符 | 4/4 pass |
| L2 | Execution Trajectory | ①trajectory_exact_match ②trajectory_precision ③step_completion_rate ④tool_call_overhead | step_completion_rate ≥ 0.8 |
| L3 | Outcome Quality | ①gate_pass_rate ②test_pass_rate ③lint_zero_rate ④semantic_fidelity | gate_pass_rate ≥ 0.95 |

---

## §10 依赖关系 {temporal_type=permanent}

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-GATE_ENGINE | 必须 | Gate Engine——门禁验证 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-CONTEXT_ENGINE | 必须 | Context Engine——上下文注入 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context_engine\blueprint.md` |
| MOD-INF-009 | 必须 | Pipeline——多模型路由 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\pipeline\blueprint.md` |
| MOD-INF-018 | 必须 | Agent RBAC——权限检查 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-020 | 必须 | Audit Trail——审计闭环 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-023 | 必须 | Drift Detector——漂移检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\drift-detector\blueprint.md` |
| MOD-INF-025 | 必须 | A2A Protocol——Agent间协调后加载规格 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\a2a-protocol\blueprint.md` |
| MOD-INF-005 | 必须 | Governance Automation——审计管线整合 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\governance-automation\blueprint.md` |
| MOD-FEEDBACK_LOOP | 可选 | Feedback Loop——预测-诊断-修复闭环 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` |
| MOD-DATABASE | 间接 | Database——间接依赖(019→018→007→005→012) | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` |
| MOD-LLM_SECURITY | 可选 | LLM Security Gateway——注入攻击检测 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm_security\blueprint.md` |
| MOD-INF-021 | 可选 | Rollback System——Skill 执行失败回滚 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |
| MOD-INF-022 | 可选 | Escalation Protocol——升级/委托路线 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-024 | 可选 | Budget Enforcer——token 预算管控 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\budget-enforcer\blueprint.md` |
| MOD-KB-001 | 可选 | Knowledge Base——KE 沉淀 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\knowledge_base\blueprint.md` |
| MOD-INF-011 | 可选 | Vector Memory——VMS存储服务（嵌入路由已迁至MOD-INF-039） | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\vector_memory\blueprint.md` |
| MOD-INF-039 | 必须 | Local Model——BGE-M3 语义路由嵌入 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\local-model\blueprint.md` |

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | ✅ 已对齐（DEP-019-001~015） | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-019` |
| 2 | §11 产出物路径 ↔ 依赖图模块归属表 code_path 列 | 路径一致 | ✅ 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | ⚠️ 部分对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.5 概念重叠声明

| # | 重叠概念 | 重叠维度 | 对方模块 | 委托关系 | 处置状态 |
|---|---------|---------|---------|---------|---------|
| 1 | 能力注册/发现 | 注册Schema+发现接口 | MOD-INF-035 CapabilityRegistry | 共存（需协调） | 已处置——Spec=编译时蓝图→Skill，CR=运行时能力发现 |
| 2 | 上下文注入 | 加载通知+上下文刷新 | MOD-CONTEXT_ENGINE Context Engine | 共存（需协调） | 已处置——Spec=Skill内容加载，CE=上下文窗口装配 |
| 3 | 触发路由 | 路由表+分派 | orchestrator.SkillRouter | 共存（需协调） | 已处置——命名已消除歧义：skill_router.py vs event_router |
| 4 | Skill 路由接口 | CBAC授权矩阵+路由接口 | MOD-MASTER_BLUEPRINT | 对方委托本模块 | 已处置——MOD-MASTER_BLUEPRINT 已声明委托 |

### 10.6 依赖链风险评级

| # | 依赖链 | 链深度 | 风险等级 | 熔断机制 | 处置状态 |
|---|--------|:-----:|---------|---------|---------|
| 1 | 019→018→007→005→012 | 5 | L3 | 有——skill_resilience.py 熔断器+本地缓存 fallback | 已有熔断 |
| 2 | 019→008→007→005→012 | 5 | L3 | 有——同上 | 已有熔断 |
| 3 | 019→020 | 1 | L1 | 无 | 不适用 |
| 4 | 019→018 | 1 | L1 | 无 | 不适用 |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `skill_model.py` | `skill_loader.py` | 数据模型定义 | import 检查 |
| `skill_loader.py` | `skill_executor.py` | Skill 加载后执行 | import 检查 |
| `skill_registry.yaml` | `trigger_router.py` | 路由表数据 | 文件存在检查 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `skill_model.py` | 全模块 | Pydantic 模型 | import |
| `skill_registry.yaml` | `skill_loader.py` | Skill 注册信息 | YAML 文件读取 |
| `trigger_router.py` | `skill_loader.py` | 路由结果(skill_id) | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 是 | 67+ 文件手动不可行 | AST解析import | `asset_inventory/dependency.py` | 不覆盖scripts/ | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | 是 | 7+ 外部依赖 | CI门禁 | `validate_path_alignment.py` | 无 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 是 | 施工步骤属临时时态 | 压缩工作流脚本 | — | 需新建 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中需状态追踪 | pytest+mypy+ruff | 部分有 | 需整合 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录 {temporal_type=permanent}

| 产出物类型 | 存放完整绝对路径 | 说明 | consumer_min |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\agent-spec\` | Python 源码（80 个 .py） |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\` + `D:\ZephyrAlpha\tests\adversarial\` | 测试用例 |
| Skill 注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | Skill 索引 |
| Domain Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\` | 领域 Skill 定义 |
| Role Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\role\` | 角色 Skill 定义 |

---

## §12 集成目标 {temporal_type=permanent}

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Audit Trail (MOD-INF-020) | 事件写入 | `SkillExecutor._write_audit()` → AuditEvent | 集成测试 |
| Agent RBAC (MOD-INF-018) | 权限检查 | `SkillLoader` 加载前检查 allowed-tools | 权限矩阵测试 |
| Rollback (MOD-INF-021) | Checkpoint | `RollbackManager.create_checkpoint()` | 回滚测试 |
| Feedback Loop (MOD-FEEDBACK_LOOP) | 五阶段闭环 | `SkillFeedbackLoop.predict→detect→diagnose→act→verify` | 闭环测试 |
| Budget Enforcer (MOD-INF-024) | 预算检查 | `BudgetEnforcer.check()` | 预算溢出测试 |
| Escalation (MOD-INF-022) | 升级委托 | `EscalationHandler.escalate()` | 升级路径测试 |
| Knowledge Base (MOD-KB-001) | 双向同步 | `KBIntegration.skill_to_kb()` / `kb_to_skill()` | 同步测试 |
| Pipeline (MOD-INF-009) | 桥接 | `PipelineSkillBridge` | 桥接测试 |
| 资产盘点 (MOD-INF-026) | Skill 注册 | Spec → INV | 注册验证 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-007 | 治理域 | Spec→RBAC/Audit 事件格式 | MOD-INF-018/MOD-INF-020 | 修改事件格式 MUST 同步更新对方蓝图 |

---

## §13 需要更新的相关内容 {temporal_type=permanent}

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-019 条目 | 模块存在 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-INF-019 条目 | 蓝图存在 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | MOD-INF-019 文档元数据 | 文档注册 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | MOD-INF-019 节点+依赖边 | 依赖关系 |
| 4 | AGENTS.md | `D:\ZephyrAlpha\AGENTS.md` | Skill 触发表 | 路由入口 |
| 5 | __init__.py | `D:\ZephyrAlpha\src\zephyr\agent-spec\__init__.py` | __all__ 导出 | 模块注册 |

---

## §14 已知风险与缓解 {temporal_type=permanent}

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R1 | 蓝图与 Skill 漂移——蓝图更新但 Skill 未同步 | 高 | 高 | freshness_score 机制 + CI 门禁 | 风险 |
| R2 | Skill 指令模糊——AI 执行时歧义导致错误 | 高 | 中 | 强制 Checklist 格式 + CRITICAL 前缀 | 风险 |
| R3 | Domain Skill 爆炸——100+ 模块维护成本 | 中 | 中 | Factory Agent 自举 + freshness_score 排序 | 风险 |
| R4 | 多 Skill 组合冲突——Domain 和 Role 对同一操作给出不同指令 | 中 | 中 | Domain > Role 优先级规则 | 风险 |
| R5 | Token 预算在组合加载下超限 | 中 | 高 | Progressive Disclosure + 组合预算 ≤ 800 tokens | 风险 |
| R6 | Skill Chain 死锁——A→B→A 循环 | 中 | 高 | Chain depth limit=3 + 循环检测 | 风险 |
| R7 | 上下文碎片化——多 Skill 分散导致注意力稀释 | 高 | 中 | Skill Compact 合并 + Attention Weighting | 风险 |
| R8 | Skill 注入攻击——Skill 文件被污染 | 低 | 高 | Defense in Depth 四层防护 | 风险 |
| R9 | 废弃 Skill 静默腐烂——过时 Skill 继续被 Agent 执行 | 高 | 中 | Deprecation Lifecycle 四阶段 + 自动检测 | 风险 |
| R10 | 依赖深度=5（019→018→007→005→012）链路故障传导 | 高 | 高 | circuit breaker + 本地缓存 fallback | 负面后果 |
| R11 | Skill执行无状态——跨session丢失进度 | 高 | 中 | skill_durable.py 持久执行+中断恢复 | 风险 |
| R12 | Skill成本无边——100+ Skills无限制加载 | 高 | 高 | skill_economics.py 成本模型+Budget Enforcer | 风险 |
| R13 | AI自主修改Skill导致门禁下降 | 中 | 高 | immutable_core/human_gated 分级+修改审计 | 风险 |
| R14 | Agent事故无法追溯Skill | 高 | 高 | skill_lineage.py 血缘追踪+skill_postmortem.py 闭环 | 风险 |

---

## §16 施工指引 {temporal_type=construction_temporary}

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 14 Phase（scaffold-0 到 expand） |
| 施工模式 | 新建 |
| 核心风险 | Domain Skill 爆炸 + 依赖深度=5 |
| 目标 generation | 2 — 本次施工将蓝图从 generation 1 升级到 generation 2 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-GATE_ENGINE Gate Engine | hard | ✅ | ✅ |
| 2 | MOD-INF-018 Agent RBAC | hard | ✅ | ✅ |
| 3 | MOD-INF-020 Audit Trail | hard | ✅ | ✅ |
| 4 | Domain Skill 目录结构 | soft | ❌ | ❌ |

### 16.3 实施步骤

#### 步骤 1：scaffold-0 — Factory Agent + Skill 模板

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SpecEngine.upgrade() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\factory\` |
| 验收标准 | Factory Agent 可生成 SKILL.md 骨架 |
| 验证命令 | `python -m pytest tests/ -k "factory" -v` |
| G7 检查项 | 产出文件存在+非空+格式合法 |
| AI 自治范围 | ai_modifiable |
| 检查点 | skills/factory/ 目录存在且包含 SKILL.md 模板 |
| 状态 | 📋 Backlog |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-019 | factory_agent.py | code | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\factory\factory_agent.py` |
| MOD-INF-019 | SKILL.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\factory\SKILL.md` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| factory_agent.py | Factory Agent 问3问题→生成SKILL.md | ①Q1核心操作 ②Q2独特约束 ③Q3常见错误模式 ④SKILL.md骨架生成逻辑 |
| SKILL.md | Skill 模板骨架 | ①YAML frontmatter ②CRITICAL Rules ③操作Checklist ④Reference列表 |

#### 步骤 2：scaffold-1 — 3 个 Role Skills + AGENTS.md 触发表

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SkillLoader.progressive_load() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\role\` |
| 验收标准 | 3 个 Role Skill 可被 SkillLoader 加载 |
| 验证命令 | `python -m pytest tests/ -k "role_skill" -v` |
| AI 自治范围 | ai_modifiable |
| 检查点 | skills/role/ 下 3 个 SKILL.md 文件存在且 SkillLoader 可加载 |
| 状态 | 🔧 部分实现 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-019 | architect.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\role\architect\SKILL.md` |
| MOD-INF-019 | implementer.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\role\implementer\SKILL.md` |
| MOD-INF-019 | governor.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\role\governor\SKILL.md` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| architect.md | 架构师角色 Skill | ①设计审查Checklist ②蓝图编写规则 ③拆分判定标准 |
| implementer.md | 实现者角色 Skill | ①编码铁律 ②十五字段头部模板 ③测试要求 |
| governor.md | 治理者角色 Skill | ①门禁检查清单 ②审计规则 ③漂移检测 |

#### 步骤 3：scaffold-2 — 5 个核心 Domain Skills

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SpecEngine.upgrade() |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\` |
| 验收标准 | 5 个 Domain Skill 可被路由匹配+加载 |
| 验证命令 | `python -m pytest tests/ -k "domain_skill" -v` |
| AI 自治范围 | human_gated |
| 检查点 | skills/domain/ 下 5 个子目录存在且 SkillRouter 可路由 |
| 状态 | 🔧 部分实现 |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-019 | database-specialist.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\database-specialist\SKILL.md` |
| MOD-INF-019 | mcp-specialist.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\mcp-specialist\SKILL.md` |
| MOD-INF-019 | gate-specialist.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\gate-specialist\SKILL.md` |
| MOD-INF-019 | agent-specialist.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\agent-specialist\SKILL.md` |
| MOD-INF-019 | knowledge-specialist.md | skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\knowledge-specialist\SKILL.md` |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| database-specialist.md | 数据库领域 Skill | ①Schema变更流程 ②迁移脚本模板 ③回滚策略 |
| mcp-specialist.md | MCP协议领域 Skill | ①Tool注册流程 ②Schema验证 ③错误码规范 |
| gate-specialist.md | 门禁领域 Skill | ①门禁检查清单 ②PASS/FAIL判定 ③升级路径 |
| agent-specialist.md | Agent权限领域 Skill | ①RBAC规则 ②PermissionLevel映射 ③审计事件 |
| knowledge-specialist.md | 知识库领域 Skill | ①KE写入流程 ②搜索策略 ③Provenance规范 |

#### 步骤 4：test-infra — Skill Testing Framework

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 测试策略 L1+L2+L3 三层评估 |
| 产出文件 | skill_evaluator.py（已存在，扩展L2/L3） |
| 验证命令 | `python -m pytest tests/ -k "skill_eval" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 5：security — Skill Security Shield

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §8 安全考量 T1-T5 威胁向量 |
| 产出文件 | skill_security.py + skill_sandbox.py + skill_guardrails.py（均已存在，扩展T1-T5） |
| 验证命令 | `python -m pytest tests/adversarial/ -k "security" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 6：integrate — 跨模块集成

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 集成目标 |
| 产出文件 | integration/pipeline_bridge.py（已存在，扩展7个集成点） |
| 验证命令 | `python -m pytest tests/ -k "integration" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 7：deploy — Canary Deployment + A/B Testing + Cross-IDE Translation + GitOps CI/CD

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.7 OCP 扩展点 |
| 产出文件 | skill_canary.py + skill_gitops.py + skill_translator.py（均已存在，扩展） |
| 验证命令 | `python -m pytest tests/ -k "canary or gitops or translator" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 8：lifecycle — Skill Deprecation Lifecycle + Economics + Kill Switch + SLO + Lineage

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 SkillStatus 状态机 + §5.4 NFR |
| 产出文件 | skill_lifecycle.py + skill_kill_switch.py + skill_lineage.py（均已存在，扩展） |
| 验证命令 | `python -m pytest tests/ -k "lifecycle or economics or kill_switch or lineage" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 9：autonomy — Human-AI Autonomy Spectrum + Skill Modification Authority + Zero-Trust

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 [AI_AUTONOMY] 字段 |
| 产出文件 | skill_model.py（已存在，扩展ai_autonomy字段） |
| 验证命令 | `python -m pytest tests/ -k "autonomy or rbac" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 10：incident — Incident→Postmortem→Skill Fix 闭环

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §6 错误处理 + §12 集成目标 |
| 产出文件 | skill_postmortem.py（已存在，扩展闭环） |
| 验证命令 | `python -m pytest tests/ -k "postmortem" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 11：cold-start — Onboarding Skill + Session Warm-Up

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SkillLoader.load_l0() |
| 产出文件 | skills/domain/onboarding-specialist/SKILL.md |
| 验证命令 | `python -m pytest tests/ -k "onboarding or warm" -v` |
| 状态 | 📋 Backlog |

#### 步骤 12：expand — 14层扩展路线渐进创建新 Domain Skill

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SpecEngine.upgrade_batch() |
| 产出文件 | rollback/blueprint/a2a/vms/context/feedback/drift-specialist SKILL.md（7个） |
| 验证命令 | `python -m pytest tests/ -k "domain_skill" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 13：optimize — Skill Discovery/Recommendation Engine + Knowledge Distillation

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 SkillRouter + §4.7 扩展点 |
| 产出文件 | skill_discovery.py + skill_knowledge_base.py（均已存在，扩展） |
| 验证命令 | `python -m pytest tests/ -k "discovery or recommend" -v` |
| 状态 | 🔧 部分实现 |

#### 步骤 14：verify — 全量 Benchmark Cycle + Regression Test

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §9 测试策略 + §16.5 施工完成标准 |
| 产出文件 | skill_efficacy_calibrator.py + self_evolution_fidelity_gate.py（均已存在，扩展） |
| 验证命令 | `python -m pytest tests/ -v --benchmark` |
| 状态 | 🔧 部分实现 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | Factory Agent 生成质量差 | 删除 skills/factory/ 目录 |
| 2 | Role Skill 格式不兼容 | 回退到上一版本 SKILL.md |
| 3 | Domain Skill 路由错误 | 移除触发表条目 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | 80 个 .py 文件存在 | `ls src/zephyr/agent-spec/` | 完成 | ✅ |
| 2 | pytest 通过 | `python -m pytest tests/ -v` exit 0 | 完成 | ☐ |
| 3 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 4 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 5 | 告警已配置 | §6.1 每项阈值有告警规则 | 就绪 | ☐ |
| 6 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 7 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 8 | 文档已更新 | §13 需要更新的文件全部更新 | 就绪 | ☐ |
| 9 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | Progressive Disclosure 三层加载 | 协议 | L1 frontmatter(~50t)→L2 body(~300-500t)→L3 references(按需) | `skill_loader.py` |
| 2 | Skill Chain 循环检测 | 算法 | 已加载 Skill id 集合 O(1) lookup，depth>3 终止 | `skill_executor.py` |
| 3 | Freshness 720h 衰减模型 | 算法 | score = 100 × max(0, 1 - elapsed_hours/720) | `skill_freshness.py` |
| 4 | Budget 组合检查 | 协议 | domain_l2 + role_l2 ≤ 800 tokens，超出→降级 | `skill_executor.py` |
| 5 | Defense in Depth 四层防护 | 协议 | Parse→Validate→Simulate→Audit | `skill_security.py` |
| 6 | Skill Economics 成本模型 | 算法 | cost_components: load_cost + execution_cost + tool_call_overhead + model_rate_multiplier | `skill_economics.py` |
| 7 | Skill Deprecation 四阶段自动触发 | 算法 | T1_blueprint_breaking_change / T2_evidence_dead / T3_unused / T4_freshness_zero | `skill_lifecycle.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m zephyr.agent_spec list` | 列出所有已注册 Skill | — | Skill 列表 |
| 2 | 命令 | `python -m zephyr.agent_spec status` | 显示模块健康状态 | — | 健康报告 |
| 3 | 命令 | `python -m zephyr.agent_spec` | CLI 入口 | `[list\|status\|help]` | exit code |
| 4 | 命令 | `python -c "from zephyr.agent_spec.engine import SpecEngine; SpecEngine().upgrade('blueprint_path')"` | 蓝图→Skill升级 | blueprint_path | UpgradeResult |
| 5 | 命令 | `python -c "from zephyr.agent_spec.skill_executor import SkillExecutor; SkillExecutor().execute('SKILL-ID')"` | Skill执行 | skill_id | 执行结果Dict |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | Skill 加载失败 | FileNotFoundError | 检查 skill-registry.yaml 路径 | 修正路径 | 重新加载 |
| 2 | 运行 | 门禁连续 FAIL | 3× GateResult(passed=False) | 检查 Skill 指令+代码 | 修复后重试 | 回滚 checkpoint |
| 3 | 运行 | 新鲜度降分 | freshness_score < 50 | 检查蓝图版本变更 | 重审 Skill | 降级为 deprecated |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同 Skill 文件写入 | SHA256 校验 | 后写者重试 | 字段级合并 |
| 同注册表更新 | 文件锁 | 排队等待 | FIFO |
| 同 Skill 加载 | 缓存命中 | 直接返回缓存 | — |

---

## §17 容量升级附录 {temporal_type=permanent}

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| .py 文件数 | 67 | `ls src/zephyr/agent-spec/*.py \| wc -l` |
| Domain Skill | 19 | `ls skills/domain/` |
| Role Skill | 3 | `ls skills/role/` |
| 依赖深度 | 5 | dependency_path_panorama.md |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-019-01 | 关键词路由歧义 | 语义路由 BGE-M3 | P1 | 关键词冲突率 > 5% | v0.20.0 | 待施工 |
| GAP-019-02 | Domain Skill 未创建 | Factory Agent 批量生成 | P0 | 新模块上线 | v0.20.0 | 待施工 |
| GAP-019-03 | 无 Onboarding Skill | 冷启动 Skill | P2 | 前3次 session | v0.21.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.19.0 | 1 | 基线 | 四层架构+77个.py+3 Role Skill | ✅ |
| v0.20.0 | 2 | 容量升级 | 12 Domain Skill + 语义路由 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| Domain Skill 目录 | GAP-019-02 | skills/domain/ | scaffold-2 | 待施工 |
| 语义路由 | GAP-019-01 | trigger_router.py | scaffold-2 | 待施工 |

---

## §18 决策记录 {temporal_type=permanent}

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-019-01 | 四层架构：L0 AGENTS.md → L1 Domain Skills → L2 Role Skills → L3 Cold Memory | A:四层架构 / B:3个Skill Pack / C:单体 | A | 领域/角色解耦，渐进加载，支持100+模块扩展 | 2026-05-05 |
| 2 | D-019-04 | Progressive Disclosure 三层递进加载 | D:关键词路由O(1) / E:语义路由BGE-M3 O(log N) | E | O(log N)无歧义，关键词升级为语义路由 | 2026-05-05 |
| 3 | D-019-07 | Skill Security Defense in Depth | Parse/Validate/Simulate/Audit 四层 | 四层 | OWASP MCP Top 10 对齐 | 2026-05-05 |
| 4 | D-019-11 | Skill 废弃四阶段生命周期 | 四阶段 / 二阶段 / 直接删除 | 四阶段 | 30d过渡期保证下游适配 | 2026-05-05 |
| 5 | D-019-12 | Human-AI 自主光谱 L0-L4 | L0-L4五级 / 二元开关 | L0-L4 | 不同Skill类型需不同自主程度 | 2026-05-05 |
| 6 | D-019-84 | MVSS 基线——4-folder+3 Role+153盲点 | 微Agent基线 / 全量一次性 | 微Agent | ScaffoldPhaseBuilder验证 | 2026-05-05 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| Skill | AI Agent 可执行的操作手册，按 agentskills.io 标准格式 | 蓝图 | 蓝图=架构文档，Skill=操作手册 |
| Progressive Disclosure | 三层递进加载策略：L1 metadata→L2 body→L3 references | 懒加载 | 懒加载无预算控制，PD 有 token 预算 |
| Domain Skill | 按模块领域组织的 Skill（如 database-specialist） | Role Skill | Domain=领域知识，Role=操作模式 |
| Role Skill | 按角色组织的 Skill（architect/implementer/governor） | Domain Skill | Role=跨领域通用操作，Domain=领域专属 |
| Freshness Score | 0-100 分数，衡量 Skill 与蓝图的对齐程度 | 版本号 | 版本号=人工标记，freshness=自动计算 |
| Skill Chain | 多 Skill 串联执行，深度上限=3 | Skill 组合 | Chain=串行依赖，组合=并行加载 |
| Kill Switch | 紧急停止机制，5s 内终止 Skill 执行 | 熔断器 | Kill Switch=人工触发，熔断器=自动触发 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | Domain Skill 目录为空 | 高 | 未施工 | scaffold-2 Phase 创建 | §5.2 | 待解决 |
| 2 | 语义路由未实现 | 中 | BGE-M3 集成未完成 | trigger_router.py 升级 | §5.1 #2 | 待解决 |
| 3 | 依赖深度=5 风险 | 高 | 架构决定 | circuit breaker + 本地缓存 | §5.1 | 已缓解 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 13 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 四层架构+渐进披露经过2轮验证 | — |
| 接口契约 | evolving | 中 | 77个.py已实现，接口稳定 | 部分方法签名可能调整 |
| 数据模型 | stable | 高 | Pydantic V2 模型已固化 | — |
| 施工步骤 | evolving | 中 | scaffold-0/1/2 待施工 | Phase 规划可能调整 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.19.0 | 四层架构+77个.py+3 Role Skill | — | 已完成 |
| v0.20.0 | 12 Domain Skill + 语义路由 | v0.19.0 | 待施工 |
| v0.21.0 | Onboarding Skill + 冷启动优化 | v0.20.0 | 待施工 |
| v0.22.0 | 跨模型兼容性 + 模型进化 | v0.21.0 | 待施工 |
| v0.23.0 | 合规体系 + KYA 凭证 | v0.22.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：施工声明——永久保留，不可改为链接引用。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径基准 | 文件创建到错误位置 |
| 2 | **必备链接不可省略** | AI 每次新 session 是零记忆 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果** | — | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范 | 路径幻觉 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界 | 范围漂移 |
| 6 | **容量估算必须写** | — | 容量瓶颈 |
| 7 | **迁移/废弃方案必须写** | — | 断链或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令 | 执行漂移 |
| 9 | **蓝图必须自包含** | AI 可能不读引用文件 | 信息缺失 |
| 10 | **删除文件必须遵守安全删除协议** | 没有git备份，删除不可逆 | 永久丢失 |
| 11 | **construction_progress 必须与代码实际状态一致** | — | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | — | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复** | 代码文件是 SSoT | 双源漂移 |
| 14 | **临时时态内容执行完毕后从蓝图删除** | 蓝图是当前设计文档 | 蓝图膨胀 |
| 15 | **蓝图内容拆分判定** | — | AI 不知道该读哪个蓝图 |
| 16 | **术语表不可省略** | AI 对术语产生理解漂移 | 设计与蓝图意图不一致 |
| 17 | **参考实现规格 vs 已实现代码重复** | 删掉规格→AI编造实现逻辑 | 关键逻辑实现错误 |
| 18 | **对标验证表格 vs 对标散文** | 表格=验证基准，散文=噪音 | 丢表格→无法验证 |
| 19 | **SLO 必须定义** | AI 需要量化目标做可靠性决策 | 容错策略凭空猜测 |
| 20 | **可观测性不可省略** | 无法度量就无法改进 | 故障无法发现 |
| 21 | **退化矩阵必须声明** | 部分失败时系统行为不可预测 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

| 判定条件 | 结果 | 操作 |
|---------|------|------|
| 服务对象相同 + 变更频率同步 + 依赖关系重叠 | 原地升级 | 在 §17 容量升级附录中增量记录 |
| 有独立 module_id 前缀 | 拆分 | 创建子蓝图，belongs_to=本蓝图 |
| 有独立 Phase 路线图和交付节奏 | 拆分 | 同上 |
| 有独立依赖关系图（与主体 depends_on 交集<50%） | 拆分 | 同上 |
| 内容超100行且与主体无直接数据流 | 拆分 | 同上 |

---

## ⚠️ 安全删除协议

> **时态属性**：施工声明——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 无 | — | — | — | — |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | 给足缓冲期 |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

> **时态属性**：施工声明——AI 进入蓝图时必读。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 模块ID注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 4 | AI自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI操作权限 |
| 5 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 十五字段头部 |
| 6 | 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 压缩规则 |
| 7 | 依赖图 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 依赖对齐 |
| 8 | 蓝图+施工图模板 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-construction-template.md` | 模板合规 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | CapabilityRegistry | `D:\ZephyrAlpha\src\zephyr\runtime\capability_registry.py` | 能力注册 | CapabilityRegistry=运行时能力发现，Agent Spec=蓝图→Skill升级+渐进加载 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | agent-spec/ 全目录 | `D:\ZephyrAlpha\src\zephyr\agent-spec\` | 修改 | 代码维护 |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-spec\blueprint.md` | 修改 | 本文件 |
| 3 | 测试文件 | `D:\ZephyrAlpha\tests\unit\` + `D:\ZephyrAlpha\tests\adversarial\` | 修改 | 测试更新 |
| 4 | AGENTS.md | `D:\ZephyrAlpha\AGENTS.md` | 读取 | 触发表路由 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| Agent Spec 核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| Agent Spec 施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| Agent Spec 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 四层架构定义 | **本文档 蓝图特有** | ⚠️ AGENTS.md 重复定义——AGENTS.md 是运行时入口，架构定义以本蓝图为准 |
| Domain Skill 列表 | **skill_registry.yaml** | ⚠️ AGENTS.md 硬编码列表——以 skill-registry.yaml 为准（当前 19 Domain + 3 Role） |
| Skill 注册/发现 | **本文档 §4 + skill-registry.yaml** | ⚠️ CapabilityRegistry（运行时能力发现，职责不同但接口重叠） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-INF-018 Agent RBAC 蓝图 | §4 接口契约、G-CT-007 |
| Tier 1 | MOD-INF-020 Audit Trail 蓝图 | §4 接口契约、G-CT-007 |
| Tier 2 | MOD-INF-026 资产盘点 | Skill 注册事件 |
| Tier 2 | MOD-CONTEXT_ENGINE Context Engine | CE 刷新通知 |
| Tier 3 | `src/zephyr/agent-spec/*.py` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |

---

## 蓝图特有章节

### 蓝图特有：四层架构与 Skill 触发表

| 要素 | 内容 |
|------|------|
| 来源 | 规格化回填 |
| 仅本蓝图 | 四层架构+触发表是 Agent Spec 独有设计 |
| 不可砍 | 砍掉后 AI 不知道 Skill 怎么被发现和加载 |

**四层架构**：

| 层级 | 名称 | Token 预算 | 加载条件 | 职责 |
|:---:|------|:---:|------|------|
| L0 | AGENTS.md 宪法 | ~800 | always loaded | 项目拓扑+触发表+编码铁律+Session交接 |
| L1 | Domain Skills | ~500/Skill | 触发条件匹配 | 模块领域知识+代码模式+bug清单+专属门禁 |
| L2 | Role Skills | ~300/Skill | 与Domain组合 | 跨领域操作规范 |
| L3 | Cold Memory | ~8000/模块 | 按需MCP检索 | 蓝图全文 |

**冲突消除**：Domain Skill > Role Skill（更具体优先）。

**触发表路由**（6 施工阶段 + 22 任务类型）：

| 施工阶段 | 角色 | 默认 Domain |
|---------|------|-----------|
| 想法/草稿 | architect | master-blueprint |
| 审计（施工前） | governor | gate_engine |
| 蓝图/设计 | architect | topic 匹配 |
| 施工/实现 | implementer | module 匹配 |
| 验收/验证 | governor | module 匹配 |
| 审计（施工后） | governor | drift-detector |

| 任务类型触发 | Domain | Role |
|------------|--------|------|
| 数据库模型/迁移/SQL | database-specialist | implementer |
| MCP Server/工具/协议 | mcp-specialist | implementer |
| 上下文引擎/Context Pipeline | context-specialist | implementer |
| 反馈环/根因/追问到底/治根 | feedback-specialist | implementer |
| 门禁/规则/Policy | gate-specialist | governor |
| Agent 权限/RBAC | agent-specialist | governor |
| 蓝图/架构 | master-blueprint | architect |
| 审计/治理/合规/漂移 | drift-detector | governor |
| 知识库/KE | knowledge-specialist | implementer |
| 回滚/撤销/检查点 | rollback-specialist | governor |
| 安全/注入/LSG | lsg-security | governor |
| 向量/嵌入/VMS/ChromaDB | vector_memory | implementer |
| 任务/TaskCard | task_system | implementer |
| 遥测/可观测/指标 | system_telemetry | implementer |
| 去重/重复/单物种 | code-dedup-engine | implementer |
| 预算/成本限制/Token限制 | budget-enforcer | governor |
| 修复/自愈/故障 | auto-fix-engine | implementer |
| A2A/Agent间通信/冲突 | a2a-protocol | governor |
| 行为审计/安全审计 | behavioral-auditor | governor |
| 资源优化/GPU/分片 | resource-optimization | implementer |
| 蓝图/架构设计 | blueprint-specialist | architect |
| 管控/策略执行 | governor | governor |

SSoT：`skill_registry.yaml task_keywords`（蓝图此表为摘要，完整关键词以 YAML 为准）

**默认 fallback**：role=implementer, domain=null（不加载 Domain Skill）。

### 蓝图特有：Progressive Disclosure 加载策略

| 要素 | 内容 |
|------|------|
| 来源 | 规格化回填 |
| 仅本蓝图 | 三层递进加载是 Agent Spec 独有 |
| 不可砍 | 砍掉后 AI 不知道 Skill 怎么按需加载 |

| 层级 | 内容 | Token | 加载条件 |
|:---:|------|:---:|------|
| L1 | YAML frontmatter：skill_id+name+description+allowed-tools+model_hint+freshness_score | ~50 | 触发表匹配→常驻 |
| L2 | SKILL.md body：CRITICAL 规则+操作 Checklist+领域常量+reference 列表 | ~300-500 | 任务匹配→加载 |
| L3 | 关联文件：蓝图章节+代码样例+bug 模式库 | ~2000-8000/file | AI 主动读取 |

**预算控制**：Domain L2 + Role L2 ≤ 800 tokens。超出→降级（只保留 CRITICAL 规则，L3 全跳过）。

### 蓝图特有：Skill Factory 自举机制

| 要素 | 内容 |
|------|------|
| 来源 | 规格化回填 |
| 仅本蓝图 | Factory Agent 是 Agent Spec 独有 |
| 不可砍 | 砍掉后 AI 不知道新模块如何创建 Domain Skill |

Factory Agent 问 3 个问题：Q1 核心操作？Q2 独特约束/模式？Q3 常见错误模式？→ 生成 SKILL.md 骨架 → 人工审查 → 注册到 skill-registry.yaml → 更新 AGENTS.md 触发表。

### 蓝图特有：跨模块集成设计

| 要素 | 内容 |
|------|------|
| 来源 | 规格化回填 |
| 仅本蓝图 | 8 个集成点是 Agent Spec 独有 |
| 不可砍 | 砍掉后 AI 不知道 Skill 如何与外部系统交互 |

| 集成模块 | 集成点 | 数据格式 |
|---------|--------|---------|
| MOD-INF-020 Audit Trail | skill_loaded/applied/drift_detected/unloaded 事件 | AuditEvent Dict |
| MOD-INF-021 Rollback | Checkpoint per Skill 执行 | VersionCheckpoint |
| MOD-FEEDBACK_LOOP Feedback Loop | predict→detect→diagnose→act→verify 五阶段 | GateResult |
| MOD-INF-018 RBAC | allowed-tools per Skill | PermissionLevel |
| MOD-INF-024 Budget | token 消耗计入会话预算 | BudgetEnforcer |
| MOD-INF-005 Script System | Skill 脚本 exit code→Finding | exit 0=pass,1=fail,2=warn,3=error |
| MOD-INF-022 Escalation | light/moderate/critical 三级升级 | EscalationHandler |
| MOD-KB-001 Knowledge Base | Skill↔KE 双向同步 | KBIntegration |

---

## 变更记录

> 变更历史通过 Git log 追踪。


## Consumers
- zephyr.agent_spec (internal)
