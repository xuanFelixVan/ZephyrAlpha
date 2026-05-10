---
module_id: "GOV-RSTR-001"
title: "系统重组总蓝图 v3.3 — 大文件拆分·跨目录重复合并·按需激活·LLM接入·版本分叉审计·安全搬家"
doc_type: blueprint
status: active
version: "3.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
ttl: permanent
construction_progress: in_progress
summary: "ZephyrAlpha 系统重组总蓝图 v3.0 —— 将已达成共识的重组动作文档化为蓝图真源。核心策略：(1)大文件拆分为可维护组件（含PipelineOrchestrator 2541行→7组件+drift_engine 2134行→5组件+10个>650行文件拆分评估）；(2)重复模块合并为单一真源——含75个跨目录同名文件（kill_switch×5/circuit_breaker×4/models×4等）+15对目录内部版本分叉+4对context_engine模块内部同名文件；(3)昂贵/高耦合子系统改为按需激活；(4)接入真实LLM API替代simulated占位；(5)未完工占位模块标记phase:future；(6)安全搬家铁律9条+价值分析方法论5步+强制安全协议(Pre-flight/执行中/Post-merge)。本蓝图是重组方案的canonical SSoT——所有子蓝图应与本蓝图对齐，冲突时以本蓝图为准。"
tags: [restructuring, refactoring, consolidation, on-demand-activation, llm-integration, capabilities, split, merge, master-plan]
priority: P0
belongs_to: "SYS-MASTER-001"
rule_form: structural
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: "MOD-MASTER-001", at: "全篇", why: "集成总蓝图——本蓝图的重组动作会影响其定义的集成契约"}
  - {target: "MOD-INF-006", at: "全篇", why: "任务系统蓝图——PipelineOrchestrator拆分需对齐"}
  - {target: "MOD-INF-005", at: "全篇", why: "脚本系统蓝图——与门禁系统契约相关"}
  - {target: "architecture-model/layers/b_gates.yaml", at: "全篇", why: "GateEngine CheckType注册表化的架构真源"}
---

# 系统重组总蓝图

> module_id: GOV-RSTR-001 | version: 3.3.0 | status: active | layer: cross_layer

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 本蓝图是否遵守 |
|---|------|:---:|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | ✅ |
| 2 | 必备链接不可省略 | ✅ |
| 3 | 蓝图必须是最终设计结果——不记录决策过程 | ✅ |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | ✅ |
| 5 | 涉及文件范围必须明确列出 | ✅ |
| 6 | 容量估算必须写 | ✅ |
| 7 | 迁移/废弃方案必须写 | ✅ |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | ✅ |
| 9 | 蓝图必须自包含 | ✅ |
| 10 | 删除文件必须遵守安全删除协议 | ✅ |

---

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

> ⚠️ 本蓝图涉及大量文件废弃/迁移/合并。以下为完整的删除/迁移清单。

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | 重复 event_bus 副本 | `D:\ZephyrAlpha\src\zephyr\core\events\event_bus.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` | 迁移→交叉验证→标记deprecated→Phase 4 物理删除 |
| 2 | event_bus_upgrade 版本分叉 | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\event_bus_upgrade.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\shared\upgrade_strategy.py`（重命名） | 默认方案：l01版重命名为 shared/upgrade_strategy.py 独立保留（升级策略），shared/event_bus_upgrade.py 保留（事件版本化） |
| 3 | 重复 telemetry 系统 | `D:\ZephyrAlpha\src\zephyr\telemetry\` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\` | 逐模块迁移→验证→废弃旧目录 |
| 4 | 重复 drift_detector 副本 | `D:\ZephyrAlpha\src\zephyr\gates\drift_detector.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_engine.py` | 引用重定向→标记deprecated→Phase 4 物理删除 |
| 5 | drift_bridge | `D:\ZephyrAlpha\src\zephyr\governance\audit_trail\drift_bridge.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\drift_detector\` | 改为桥接引用→验证→Phase 4 物理删除 |
| 6 | drift_fix | `D:\ZephyrAlpha\src\zephyr\governance\rollback\drift_fix.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\drift_detector\` | 改为桥接引用→验证→Phase 4 物理删除 |
| 7 | escalation_protocol drift_detector | `D:\ZephyrAlpha\src\zephyr\infrastructure\escalation_protocol\drift_detector.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_engine.py` | 迁移→交叉验证→标记deprecated→Phase 4 物理删除 |
| 8 | 旧 escalation 系统 | `D:\ZephyrAlpha\src\zephyr\escalation\` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\infrastructure\escalation_protocol\` | 逐模块对比→保留功能完整的那套→合并→废弃旧目录 |
| 9 | Feedback Loop 独立 safety_gate 文件 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_L*.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\parameterized_safety_gate.py`（新建） | 逐文件提取规则→写入YAML配置→新参数化类替换→旧文件标记deprecated→Phase 4 物理删除 |
| 10 | kill_switch×4副本 | `agent_rbac/kill_switch.py`, `context_engine/kill_switch.py`, `governance/kill_switch.py`, `rollback/kill_switch.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\shared\kill_switch.py`（真源） | 引用重定向→标记deprecated→Phase 4 物理删除 |
| 11 | kb/unified_memory_api.py 顶层副本 | `D:\ZephyrAlpha\src\zephyr\kb\unified_memory_api.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\kb\storage\unified_memory_api.py`（真源） | 确认为相同副本→标记deprecated→Phase 4 物理删除 |
| 12 | context_engine/pipeline_orchestrator.py 轻量版 | `D:\ZephyrAlpha\src\zephyr\context_engine\pipeline_orchestrator.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py`（完整版真源） | 版本分叉→默认保留 pipeline/ 版→context_engine 版标记deprecated→Phase 4 物理删除 |
| 13 | context_engine/doc_compressor.py 顶层版 | `D:\ZephyrAlpha\src\zephyr\context_engine\doc_compressor.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\context_engine\support\doc_compressor.py`（真源） | 版本分叉→默认保留子目录版→顶层版标记deprecated→Phase 4 物理删除 |
| 14 | context_engine/prompt_registry.py 顶层版 | `D:\ZephyrAlpha\src\zephyr\context_engine\prompt_registry.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\context_engine\support\prompt_registry.py`（真源） | 版本分叉→默认保留子目录版→顶层版标记deprecated→Phase 4 物理删除 |
| 15 | context_engine/intent_keyword_mapper.py 顶层版 | `D:\ZephyrAlpha\src\zephyr\context_engine\intent_keyword_mapper.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\context_engine\parsing\intent_keyword_mapper.py`（真源） | 版本分叉→默认保留子目录版→顶层版标记deprecated→Phase 4 物理删除 |
| 16 | context_engine/intent_parser.py 顶层版 | `D:\ZephyrAlpha\src\zephyr\context_engine\intent_parser.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\context_engine\parsing\intent_parser.py`（真源） | 版本分叉→默认保留子目录版→顶层版标记deprecated→Phase 4 物理删除 |

### 删除铁律

| # | 铁律 | 说明 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 使用diff工具验证迁移完整性；删除前必须 git commit 确保可回滚 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 项目已有 git 仓库（分支 `trae-redteam-deadly-5`，有完整提交历史），`git revert` 可回滚 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 2.1.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | 1.3.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 1.0.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\governance-methodology-standard.md` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | 1.1.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\file-naming-standard.md` | 命名规则 |
| 5 | 模块 ID 注册表 | — | 2.2.0 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 编号注册、分配规则 |
| 6 | 架构总览 | VIEW-00-OVERVIEW | 1.4.1 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 集成总蓝图 | MOD-MASTER-001 | 0.9.2 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | 集成契约真源——重组动作需与现有CT-*契约对齐 |
| 8 | 蓝图模板 | — | 1.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` | 本蓝图的格式标准 |
| 9 | AI 自治权限注册表 | GOV-AI-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | AI 操作权限边界 |
| 10 | 蓝图注册表 | — | 2.5.3 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 现有蓝图索引——需新增本蓝图条目 |
| 11 | Pipeline Orchestrator | — | — | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | 被拆分的主要目标文件 |
| 12 | Gate Engine | — | — | `D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py` | 被注册表化的目标文件 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | 集成总蓝图 (§二 契约总表) | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | 定义了CT-*集成契约 | 集成总蓝图定义"模块间怎么连"，本蓝图定义"模块本身怎么改"——正交关系，不重叠 |
| 2 | ADR 决策记录 | `D:\ZephyrAlpha\docs\09_audit\` | 历史架构决策 | ADR 记录历史决策过程，本蓝图是执行方案——用途不同 |
| 3 | 无 | — | — | 此前无系统性重组蓝图 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | Pipeline Orchestrator | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | 修改 | 拆分为编排器+6个独立组件 |
| 2 | Pipeline 模型 | `D:\ZephyrAlpha\src\zephyr\pipeline\models.py` | 修改 | 新增拆分后的组件数据模型 |
| 3 | Gate Engine | `D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py` | 修改 | CheckType 拆分为独立文件+注册表 |
| 4 | Gates YAML 配置 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 修改 | 新增 CheckType 注册表条目 |
| 5 | Feedback Loop Gates | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\` | 修改 | 18个safety_gate_L*.py文件→2-3个参数化类 |
| 6 | Shared EventBus | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` | 修改 | 确认为唯一真源，移除重复副本 |
| 7 | Core EventBus 副本 | `D:\ZephyrAlpha\src\zephyr\core\events\event_bus.py` | 废弃 | 迁移引用到 shared/event_bus.py |
| 8 | L01 EventBus Upgrade | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\event_bus_upgrade.py` | 废弃 | 版本分叉——默认方案：l01版重命名为 shared/upgrade_strategy.py（升级策略），shared/event_bus_upgrade.py 保留（事件版本化） |
| 9 | Drift Detector | `D:\ZephyrAlpha\src\zephyr\drift_detector\` | 修改 | 确认为唯一真源，吸收4处重复副本 |
| 10 | Escalation → EscalationEngine | `D:\ZephyrAlpha\src\zephyr\escalation\` → 重命名为 `escalation_engine/` | 修改 | ⚠️ 功能不同不能简单合并——escalation/ 是运行时升级引擎，重命名为 escalation_engine/ 独立保留 |
| 11 | Escalation Protocol | `D:\ZephyrAlpha\src\zephyr\infrastructure\escalation_protocol\` | 修改 | 安全策略集，保持不变 |
| 12 | Telemetry (旧) | `D:\ZephyrAlpha\src\zephyr\telemetry\` | 废弃 | 合并到 l12_system_telemetry/ |
| 13 | L12 Telemetry | `D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\` | 修改 | 吸收旧 telemetry 系统的功能 |
| 14 | Asset Inventory | `D:\ZephyrAlpha\src\zephyr\asset_inventory\` | 修改 | 22文件→约14文件，合并同类模块 |
| 15 | Capabilities 配置 | `D:\ZephyrAlpha\src\zephyr\capabilities.yaml` | 新建 | 按需激活机制的全局配置中心 |
| 15a | **目录内部版本分叉审计** | `D:\ZephyrAlpha\src\zephyr\orchestrator\` + `shared\` + `core\` | **审计** | **15对同名文件已全部分类：orchestrator/ 1个re-export+2个相同副本+9个版本分叉；shared/ 1个版本分叉(context.py)；core/ 2个版本分叉(blueprint_code_sync+session_continuity)——详见Phase 3b审计表** |
| 16 | A2A Protocol | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\a2a_protocol\` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 17 | Code Dedup Engine | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 18 | Chaos Engine | `D:\ZephyrAlpha\src\zephyr\orchestrator\chaos_engine.py` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 19 | Canary Manager | `D:\ZephyrAlpha\src\zephyr\orchestrator\canary_manager.py` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 20 | LSG L4-L8 | `D:\ZephyrAlpha\src\zephyr\llm_security\` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 21 | Budget Enforcer | `D:\ZephyrAlpha\src\zephyr\budget_enforcer\` | 读取 | 不做代码改动，通过 capabilities.yaml 控制激活 |
| 22 | L07 Post-Trade | `D:\ZephyrAlpha\src\zephyr\l07_post_trade_analytics\` | 读取 | 不做代码改动，标记 phase:future |
| 23 | L09 Research | `D:\ZephyrAlpha\src\zephyr\l09_research_innovation\` | 读取 | 不做代码改动，标记 phase:future |
| 24 | L11 ML Platform | `D:\ZephyrAlpha\src\zephyr\l11_ml_platform\` | 读取 | 不做代码改动，标记 phase:future |
| 25 | Cross Layer | `D:\ZephyrAlpha\src\zephyr\_cross_layer\` | 读取 | 不做代码改动，标记 phase:future |

---

## 1. 设计背景与目标

### 1.1 背景

| 问题 | 严重程度 | 说明 |
|------|:---:|------|
| 系统未接入真实LLM | 🔴 致命 | `PipelineOrchestrator._call_model()` 返回 `simulated: True`，M1-M11 全线空转 |
| 蓝图严重滞后于代码 | 🔴 严重 | core蓝图2文件→实际59文件；shared蓝图10文件→实际208文件 |
| PipelineOrchestrator 单一巨型类 | 🟠 高 | 2541行一个类承载路由+断路器+成本+死信+抢占+LSG+锁+遥测等20+职责 |
| 多套重复模块真源分裂 | 🟡 中 | event_bus×2(1真源+1副本) + event_bus_upgrade×2(版本分叉), drift相关文件17个(含同名重复5处+语义相关12处), telemetry×2(15+23), escalation×2(10+83, ⚠️ 功能不同不能简单合并)——同名概念多处定义 |
| Feedback Loop Gates 文件爆炸 | 🟡 中 | 18个 safety_gate_L*.py（覆盖L1-L67共67个gate level），内容高度同质，可通过参数化压缩 |
| 高成本子系统全部常驻运行 | 🟡 中 | A2A(64文件)、CodeDedup(67文件)、Chaos/Canary等无论是否需要都在加载 |
| orchestrator/ 版本分叉 | 🟡 中 | 部分文件在 `orchestrator/` 顶层和 `core/`/`state/`/`resilience/` 子目录存在不同版本的实现（非完全重复，是版本分叉） |
| 未完工模块状态不明确 | 🟢 低 | L07/L09/L11有完整接口契约但被误判为"空壳"，需明确标记 |
| 蓝图vs代码差距递增 | 🔴 严重 | 音频中提到"三天内建立了164K行"——增长速度远超蓝图更新速度，需先立蓝图再改代码 |
| 75个跨目录同名文件真源分裂 | 🟡 中 | kill_switch×5/circuit_breaker×4/models×4等75个同名文件跨目录存在 |
| drift_engine.py 2134行巨型文件 | 🟠 高 | 仅次于PO的第二大文件，16个class需拆分 |
| 19个>650行大文件未评估拆分 | 🟡 中 | 除PO和drift外还有10个>650行文件待拆分评估 |

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 接入真实 LLM API，让 `_call_model()` 产出真实 AI 输出 | `PipelineResult` 中 `simulated: False`，M3 成功生成真实代码 |
| 2 | PipelineOrchestrator 从1个2335行类拆为7个独立组件 | 每个组件 ≤400行，单一职责 |
| 3 | GateEngine 24种 CheckType 注册表化 | 每种检查独立文件，registry.py 统一管理 |
| 4 | 消除所有跨目录重复模块真源分裂 | 每类概念仅有1个真源目录；event_bus×2→1, event_bus_upgrade×2→2个独立命名文件（l01版重命名为 upgrade_strategy.py）, drift同名重复5处→1, telemetry×2→1, escalation×2→2个独立命名目录（escalation/ 重命名为 escalation_engine/，与 escalation_protocol/ 功能不同需独立保留） |
| 5 | Feedback Loop Gates 从18文件压缩为2-3个参数化类 | 文件数 ≤5 |
| 6 | 引入 capabilities.yaml 按需加载机制 | 所有昂贵/实验性子系统通过配置控制激活 |
| 7 | 未完工模块明确标记 phase:future | 搜索 "phase:future" 可列出所有延迟模块 |
| 8 | 蓝图与实际状态完全一致 | 蓝图文件数 ≈ 实际模块数（偏差<20%） |
| 9 | >1000行文件全部有拆分方案 | pipeline/models.py(1001行)等6个>1000行文件均有拆分方案或不拆分理由 |
| 10 | 75个跨目录同名文件全面审计 | 每个同名文件分类为re-export/相同副本/版本分叉/同名不同功能 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 新增模块功能 | 本蓝图仅重组现有模块，不增加新功能 |
| 2 | 修改 LLM 安全网关核心逻辑 | LSG 九层防线已完整实现，仅调整激活策略 |
| 3 | 重写业务层（L00/L02/L04/L10） | 业务层与重组正交，不在此蓝图范围 |
| 4 | 数据库 schema 变更 | 合并/拆分不影响 SQLite 表结构 |

---

## 2. 模块边界

### 2.1 职责范围

| # | 职责 | 说明 |
|---|------|------|
| 1 | 定义重组动作的精确范围 | 每次动作的源文件、目标文件、变更类型 |
| 2 | 定义 capabilities.yaml 的 schema 和激活规则 | 各子系统的默认状态、自动激活条件、手动覆盖方式 |
| 3 | 定义合并/拆分后的新模块接口契约 | 拆分后组件的公共API、合并后的统一入口 |
| 4 | 定义重组施工的顺序和依赖 | 哪步先做、哪步依赖哪步 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | PipelineOrchestrator 拆分后的具体实现 | Pipeline 模块蓝图（MOD-INF-006） |
| 2 | GateEngine CheckType 注册后的检查逻辑实现 | Gates 模块蓝图（MOD-INF-005 相关） |
| 3 | capabilities.yaml 的运行时读取逻辑 | L01 Infrastructure（config.py） |
| 4 | 合并后模块的回归测试 | 各模块对应的 test/ 目录 |

---

## 3. 接口契约

### 3.1 公共 API — capabilities.yaml

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class ActivationMode(str, Enum):
    ON = "on"
    OFF = "off"
    WARN_ONLY = "warn_only"
    AUTO = "auto"

class CapabilityEntry(BaseModel):
    capability_id: str = Field(..., description="子系统唯一标识，如 a2a_protocol")
    default_mode: ActivationMode = Field(..., description="默认激活模式")
    auto_activation_condition: Optional[str] = Field(
        default=None,
        description="自动激活条件表达式，如 'module_count > 100'"
    )
    description: str = Field(..., description="子系统功能说明")
    file_count: int = Field(..., description="涉及文件数（供容量估算）")

class CapabilitiesManifest(BaseModel):
    version: str = Field(default="1.0.0")
    capabilities: dict[str, CapabilityEntry] = Field(..., description="子系统名→配置")

    def is_active(self, capability_id: str, context: dict) -> bool:
        """给定运行时上下文，判断某能力是否应激活"""
        ...
```

### 3.2 按需激活规则表

| 子系统 | capability_id | 默认模式 | 自动激活条件 | 说明 |
|--------|-------------|:---:|------|------|
| A2A Protocol | `a2a_protocol` | OFF | `agent_count > 3` | Agent间通信协议（64文件三层架构） |
| Code Dedup Engine | `code_dedup_engine` | OFF | `ai_code_duplication_rate > 0.15` | AI生成代码去重引擎（67文件） |
| Chaos Engine | `chaos_engine` | OFF | `module_count > 500 OR cascade_failure_count > 2` | 混沌工程故障注入 |
| Canary Manager | `canary_manager` | OFF | `module_count > 500` | 金丝雀发布管理 |
| Feature Flag | `feature_flag` | OFF | `experiment_count > 10` | 功能开关管理 |
| LSG L4-L8 | `lsg_advanced` | OFF | `agent_count > 5` | LSG 高级安全层（Agent安全+多Agent） |
| Budget Enforcer | `budget_enforcer_strict` | WARN_ONLY | `daily_cost_usd > 10` | 成本严格限制模式 |

### 3.3 拆分后 PipelineOrchestrator 组件接口

```
PipelineOrchestrator (编排器, ~200行)
  └── dispatch(task_card: TaskCard) -> PipelineResult

ModelRouter (模型路由器, ~150行)
  └── resolve_model(module_id, task, failure_history) -> str
  └── fallback_chain_for(model) -> list[str]

CircuitBreakerManager (断路器, ~100行)
  └── allow_request(model) -> bool
  └── record_result(model, success)

CostTracker (成本追踪, ~100行)
  └── estimate_cost(model, tokens) -> float
  └── total_cost() -> float

DeadLetterQueue (死信队列, ~80行)
  └── enqueue(task_card, error) -> None
  └── drain() -> list[DeadLetterEntry]

PreemptionManager (优先级抢占, ~100行)
  └── should_preempt(new_priority, current_priority) -> bool
  └── preempt(task_id) -> None

PipelineLock (双管线并发锁, 已存在——仅需验证接口对齐)
  └── acquire(task_id, file_paths, timeout_s) -> LockResult
  └── release(task_id) -> None
```

### 3.4 拆分后文件映射

| 组件 | 完整绝对路径 |
|------|------------|
| PipelineOrchestrator | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` |
| ModelRouter | `D:\ZephyrAlpha\src\zephyr\pipeline\model_router.py` |
| CircuitBreakerManager | `D:\ZephyrAlpha\src\zephyr\pipeline\circuit_breaker_manager.py` |
| CostTracker | `D:\ZephyrAlpha\src\zephyr\pipeline\cost_tracker.py` |
| DeadLetterQueue | `D:\ZephyrAlpha\src\zephyr\pipeline\dead_letter_queue.py` |
| PreemptionManager | `D:\ZephyrAlpha\src\zephyr\pipeline\preemption_manager.py` |
| PipelineLock | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_lock.py`（已存在——验证接口对齐） |

### 3.3b 拆分后 drift_engine.py 组件接口

> drift_engine.py（2,134行，16个class）按职责域拆为5个组件。

```
DriftEngine (编排器, ~200行)
  └── run_full_scan(scope, config) -> DriftReport
  └── get_detector(detector_type) -> BaseDetector

DriftInfrastructure (基础设施, ~400行)
  └── MaintenanceWindow, CheckpointWriter, RecoveryManager
  └── EnvDiffReport, PartialDeploymentRecord
  └── save_checkpoint() / restore_checkpoint()

AIConstructionDetectors (AI施工检测, ~400行)
  └── AIConstructionDetectors
  └── detect_construction_anomalies() -> list[Anomaly]

DriftResultTypes (漂移结果类型, ~600行)
  └── SemanticDriftResult, DBSchemaDriftResult, DepVersionDriftResult
  └── SecurityPolicyDriftResult, DocCodeCoevolutionResult
  └── TestCoverageDriftResult, KnowledgeGraphSyncResult
  └── to_report() -> DriftReport

DriftTraining (训练/学习, ~300行)
  └── DriftTrainingPattern, AITrainingLoopResult
  └── CrossLanguageConfig
  └── train_from_history() -> TrainingResult
```

### 3.4b 拆分后 drift_engine 文件映射

| 组件 | 完整绝对路径 |
|------|------------|
| DriftEngine | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_engine.py`（精简后） |
| DriftInfrastructure | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_infrastructure.py`（新建） |
| AIConstructionDetectors | `D:\ZephyrAlpha\src\zephyr\drift_detector\ai_construction_detectors.py`（新建） |
| DriftResultTypes | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_result_types.py`（新建） |
| DriftTraining | `D:\ZephyrAlpha\src\zephyr\drift_detector\drift_training.py`（新建） |

### 3.5 合并后真源声明

| 概念 | 唯一真源路径 | 被废弃的副本路径 | 版本分叉（默认保留子目录版，Owner 可覆盖） |
|------|------------|----------------|-------------------------------|
| EventBus | `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py` | `core/events/event_bus.py`（重复副本） | — |
| EventBusUpgrade | 默认保留 `shared/event_bus_upgrade.py`（事件版本化）；l01版功能（升级策略）重命名为 `shared/upgrade_strategy.py` 独立保留 | — | `l01_infrastructure/event_bus_upgrade.py`（升级策略） vs `shared/event_bus_upgrade.py`（事件版本化） |
| DriftDetector | `D:\ZephyrAlpha\src\zephyr\drift_detector\` | `gates/drift_detector.py`, `governance/audit_trail/drift_bridge.py`, `governance/rollback/drift_fix.py`, `infrastructure/escalation_protocol/drift_detector.py` | — |
| Telemetry | `D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\` | `telemetry/` | — |
| Escalation | `D:\ZephyrAlpha\src\zephyr\infrastructure\escalation_protocol\` | `escalation/`（⚠️ 功能不同——escalation/ 是运行时升级引擎，escalation_protocol/ 是安全策略集，不能简单合并；默认方案：escalation/ 重命名为 escalation_engine/ 独立保留） | — |
| SafetyGate | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\parameterized_safety_gate.py`（新建） | 所有 `safety_gate_L*.py` | — |
| KillSwitch | `D:\ZephyrAlpha\src\zephyr\shared\kill_switch.py` | `agent_rbac/kill_switch.py`, `context_engine/kill_switch.py`, `governance/kill_switch.py`, `rollback/kill_switch.py` | 默认保留 shared/ 版，其余4个副本标记 deprecated→Phase 4 物理删除 |
| UnifiedMemoryAPI | `D:\ZephyrAlpha\src\zephyr\kb\storage\unified_memory_api.py` | `kb/unified_memory_api.py`（完全相同副本） | 顶层版为 re-export wrapper→标记 deprecated→Phase 4 物理删除 |
| ContextEngine PipelineOrchestrator | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py`（2541行真源） | `context_engine/pipeline_orchestrator.py`（69行轻量版——版本分叉） | 版本分叉：默认保留 pipeline/ 版，context_engine 版标记 deprecated |
| ContextEngine DocCompressor | 默认保留 `context_engine/support/doc_compressor.py` | `context_engine/doc_compressor.py`（顶层584行 vs support/584行——版本分叉） | 版本分叉：默认保留子目录版（support/），顶层版标记 deprecated |
| ContextEngine PromptRegistry | 默认保留 `context_engine/support/prompt_registry.py` | `context_engine/prompt_registry.py`（顶层483行 vs support/482行——版本分叉） | 版本分叉：默认保留子目录版（support/），顶层版标记 deprecated |
| ContextEngine IntentKeywordMapper | 默认保留 `context_engine/parsing/intent_keyword_mapper.py` | `context_engine/intent_keyword_mapper.py`（顶层623行 vs parsing/460行——版本分叉） | 版本分叉：默认保留子目录版（parsing/），顶层版标记 deprecated |
| ContextEngine IntentParser | 默认保留 `context_engine/parsing/intent_parser.py` | `context_engine/intent_parser.py`（顶层573行 vs parsing/439行——版本分叉） | 版本分叉：默认保留子目录版（parsing/），顶层版标记 deprecated |

### 3.6 MCP 接口

本蓝图不暴露 MCP 接口。capabilities.yaml 由 config.py 直接读取，不通过 MCP 协议。

### 3.7 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| capabilities.yaml Schema 新增字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 拆分后组件的公开 API | ✅ 向后兼容 | PipelineOrchestrator.dispatch() 签名不变 |
| 删除旧模块路径 | ❌ 破坏性 | 需更新所有 import 语句 |
| telemetry→l12 合并 | ❌ 破坏性 | 所有 `from zephyr.telemetry` 需改为 `from zephyr.l12_system_telemetry` |

---

## 4. 约束条件

### 4.1 技术约束

| # | 约束 | 原因 |
|---|------|------|
| 1 | 所有新建文件必须使用 Pydantic V2 BaseModel | ADR-0040 强制要求 |
| 2 | 所有新建文件必须在 `D:\ZephyrAlpha\src\zephyr\` 下 | L01 基础设施层代码位置 |
| 3 | 删除操作必须遵守安全删除协议 | 项目已有 git 仓库，但仍需谨慎操作 |
| 4 | 每次修改不超过5个文件（Phase 2 拆分除外，允许单次创建≤7个新文件+修改≤3个现有文件） | 降低单次故障影响范围；Phase 2 因拆分性质需放宽 |
| 5 | 每步必须有回滚方案 | 见 §11.4 |

### 4.1b 安全搬家铁律

> ⚠️ 以下铁律是重组施工的**强制约束**，违反任何一条即停止施工。

| # | 铁律 | 说明 | 验证方式 |
|---|------|------|---------|
| 1 | 执行前必须重新扫描目标文件的所有 import 引用 | 蓝图记录可能过时，必须现场确认 | `grep -rn "from zephyr.目标模块" src/` 输出完整引用清单 |
| 2 | 重复文件合并必须逐条做价值分析 | 禁止"看起来一样就直接删"——必须用diff确认 | 每个副本的独有 class/function 已列出 |
| 3 | 合并后必须验证内容完整性 | 对比合并前后的 class/function 列表，确认无遗漏 | `diff <(合并前grep class) <(合并后grep class)` 返回零差异 |
| 4 | import 更新必须全量验证 | 每次合并/迁移后，全项目搜索旧 import 路径，确认零残留 | `grep -r "from zephyr.旧路径" src/` 返回零结果 |
| 5 | 一次只搬一个文件 | 禁止批量合并多个重复文件；每个文件的合并/迁移是独立原子操作 | 每个任务卡仅涉及1个重复文件的合并 |
| 6 | 搬完一个验证一个 | 每完成一个文件的合并，立即运行相关测试验证 | `pytest tests/相关目录/` 返回 0 failed |
| 7 | git commit 每步必做 | 每完成一个原子操作（合并+验证），立即 git commit | `git log --oneline -1` 显示该步提交 |
| 8 | 安全优先，速度第二 | 宁可慢，不可漏；宁可多拆100个任务卡，不可一次合并10个文件 | 任务卡数量无上限 |
| 9 | 做完一个，更新一个蓝图 | 重组+蓝图更新是原子操作，不可拆分；禁止批量延迟更新蓝图——AI上下文有限，延迟更新必出幻觉 | 每个任务卡 = 一次重组 + 一次蓝图更新 + 一次验证 + 一次提交 |

### 4.1c 重复文件价值分析方法论

> 对每个跨目录同名文件，必须按以下步骤做价值分析后才能决定处理方案。

**步骤**：

1. **内容对比**：用 `diff` 对比两个同名文件，标记差异
2. **分类判定**：
   - **完全相同**（0 diff）→ 确认后保留1份，其余标记 deprecated
   - **re-export wrapper**（顶行含 "Backward-compatible alias"）→ 保留真源，wrapper 标记 deprecated
   - **版本分叉**（有实质差异）→ 进入步骤3
   - **同名不同功能**（类名/函数名完全不同）→ 两个都保留，重命名消除歧义
3. **价值提取**（仅版本分叉）：
   - 列出副本A的独有 class/function（B中没有的）
   - 列出副本B的独有 class/function（A中没有的）
   - 列出两者共有但实现不同的 class/function
4. **归并决策**：
   - 独有功能 → 迁移到真源文件
   - 共有功能 → 保留更完整的版本，删除冗余版本
   - 全部独有 → 两个文件都保留，重命名
5. **验证**：归并后对比 class/function 列表，确认无遗漏

### 4.2 容量估算

| 维度 | 当前规模 | 重组后目标 | 1500模块峰值 | 是否够用 |
|------|:------:|:------:|:------:|:---:|
| Python 文件总数 | 1,791 | ~1,570 | ~3,000 | ✅ |
| 总代码行数 | ~218,000 | ~148,000 | ~300,000 | ✅ |
| capabilities.yaml 条目 | 0 | 7 | ~50 | ✅ |
| GateEngine CheckType | 24 | 24（注册表化） | ~100 | ✅ |
| 最大单文件行数 | ~2,541 | ≤400 | ≤500 | ✅ |
| 跨目录重复概念数 | 75个（含5副本×1、4副本×2、3副本×8、2副本×50+） | 0（每类1真源） | — | ✅ |
| 目录内部版本分叉 | 15对（9+1+2相同+1 re-export） | ≤3对保留双版本（人类决策后） | — | ✅ |
| >400行文件数 | 82 | ≤20 | ≤50 | ✅ |
| >1000行文件数 | 6 | 0 | ≤5 | ✅ |

### 4.3 迁移/废弃方案

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | 全部重复模块 | 见 §3.5 | 各自真源路径 | 迁移内容→验证→废弃 | 全项目搜索 import / from 语句并更新 |
| 2 | 旧 telemetry/ | `D:\ZephyrAlpha\src\zephyr\telemetry\` | 删除 | 标记 deprecated→Phase 4 物理删除 | search: `from zephyr.telemetry` / `import zephyr.telemetry` |
| 3 | 旧 escalation/ | `D:\ZephyrAlpha\src\zephyr\escalation\` | 删除 | 合并→标记 deprecated→Phase 4 物理删除 | search: `from zephyr.escalation` / `import zephyr.escalation` |
| 4 | safety_gate_L*.py | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\` | 标记 deprecated | 提取规则→新建参数化类→旧文件标记 deprecated | search: `from zephyr.feedback_loop.gates.safety_gate` |

---

## 5. 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 |
|---------|---------|---------|---------|
| MOD-MASTER-001（集成总蓝图） | 必须 | CT-PIPE-ORC-001 等集成契约——拆分后需确认契约仍有效 | 0.9.2 |
| MOD-INF-006（任务系统蓝图） | 必须 | TaskCard模型、PipelineResult模型 | 当前版本 |
| MOD-INF-005（脚本系统蓝图） | 必须 | GateEngine 对脚本的依赖 | 当前版本 |
| GOV-AI-001（AI自治权限） | 必须 | AI 可自主修改的范围边界 | 当前版本 |
| GOV-DOC-002（目录结构标准） | 必须 | 产出物存放路径规范 | 1.3.0 |
| openai（Python包） | 软依赖 | 接入 DeepSeek/GLM API 需要 | >=1.0.0 |

---

## 6. 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 本蓝图 | `D:\ZephyrAlpha\docs\03_modules\_restructuring\blueprint.md` | 重组方案真源 |
| capabilities.yaml | `D:\ZephyrAlpha\src\zephyr\capabilities.yaml` | 全局按需激活配置（新建） |
| 拆分后组件 | `D:\ZephyrAlpha\src\zephyr\pipeline\` | model_router.py, circuit_breaker_manager.py 等（新建） |
| 参数化 SafetyGate | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\parameterized_safety_gate.py` | 新建 |
| SafetyGate 配置 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\safety_gate_config.yaml` | 新建 |
| CheckType 独立文件 | `D:\ZephyrAlpha\src\zephyr\gates\check_types\` | 每种检查独立 .py（新建目录） |
| CheckType 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\check_type_registry.py` | 新建 |

---

## 7. 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| PipelineOrchestrator | 拆分 | 原 `dispatch()` 改为调用拆分后的子组件 | `dispatch()` 端到端测试通过 |
| GateEngine | 注册表化 | `load_gates()` 改为从 registry 加载 CheckType | 所有现有 G0-G12 门禁测试通过 |
| L01 config.py | 读取 capabilities | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\config.py` 新增 `load_capabilities()` | `CapabilitiesManifest` 成功解析 |
| LLM Security Gateway | 激活控制 | LSG L4-L8 初始化时检查 capabilities | L4-L8 在 OFF 模式不执行 |

---

## 8. 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | 新增 GOV-RSTR-001 | 新蓝图需注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 新增 _restructuring/blueprint.md | 蓝图总数+1 |
| 3 | 架构总览 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 新增重组蓝图引用 | 架构文档入口需更新 |
| 4 | 文档元数据索引 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index.yaml` | 新增本蓝图条目 | 治理资产清单完整性 |
| 5 | 集成总蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | depends_on 新增 GOV-RSTR-001 | 集成蓝图需引用重组蓝图 |
| 6 | Pipeline 蓝图 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\pipeline\blueprint.md` | depends_on 新增 GOV-RSTR-001；接口契约更新 | PipelineOrchestrator拆分后接口变更 |
| 7 | Gates 蓝图 (MOD-INF-007) | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md` | depends_on 新增 GOV-RSTR-001 | CheckType注册表化 |
| 8 | Feedback Loop 蓝图 (MOD-INF-010) | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md` | depends_on 新增 GOV-RSTR-001 | Gates 参数化合并 |
| 9 | requirements.txt | `D:\ZephyrAlpha\requirements.txt` | 新增 `openai>=1.0.0` | LLM API 接入需要 |
| 10 | pyproject.toml | `D:\ZephyrAlpha\pyproject.toml` | dependencies 新增 `openai>=1.0.0` | LLM API 接入需要 |

---

## 9. 已知风险与缓解

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| 1 | 合并重复模块时遗漏引用→运行时 ImportError | 中 | 高 | 全项目 grep 搜索后列清单，逐条验证 |
| 2 | PipelineOrchestrator 拆分后循环依赖 | 低 | 高 | 组件间通过接口通信，禁止互相导入 |
| 3 | capabilities.yaml 解析失败→系统全部以默认模式运行 | 低 | 中 | fail-safe：解析失败时全部使用 default_mode |
| 4 | LLM API 调用失败→管线中断 | 中 | 高 | 保留 simulated fallback；断路器自动降级 |
| 5 | 重组过程中破坏已有测试 | 中 | 中 | 每步完成后运行全量测试 |
| 6 | Phase:future 模块被 AI 误解为"可以删" | 低 | 中 | 在代码中加显式注释 `# phase:future — DO NOT DELETE` |

---

## 10. 后果

### 正面

- AI 维护成本大幅降低：大文件拆小后，AI 一次 session 可以完整理解一个组件
- 消除真源分裂后，AI 不再困惑"同一个概念哪个文件才是对的"
- 按需激活后，系统启动速度更快，内存占用更低
- 接入真实 LLM 后，系统从"空转模型"变为"真实生产系统"
- 蓝图首次领先于代码，后续 AI 施工有明确的蓝图参照

### 负面

- 重组期间系统不可用（预计1-2周施工期）
- 合并重复模块是破坏性变更，会短暂破坏 import 链
- capabilities.yaml 增加了系统配置复杂度
- 如果 LLM API 费用失控，月成本可能超预期

---

## 11. 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（§1-§10 架构 + §11 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 已读取 MOD-MASTER-001，确认受影响的 CT-* 契约 | CT-PIPE-ORC-001 等 | ☐ |
| 4 | 已确认安全删除协议理解 | 能列出删除步骤顺序 | ☐ |
| 5 | 已有 DeepSeek API Key 或 GLM API Key | 确认环境变量 | ☐ |

### 11.0b 强制安全协议

> 以下协议是 §4.1b 安全搬家铁律的**执行层细化**，每个任务卡必须遵守。

**Pre-flight Scan（执行前）**：

| # | 扫描项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 扫描目标文件的所有 import 引用 | `grep -rn "from zephyr.目标模块" src/` | 输出完整引用清单，无遗漏 |
| 2 | 确认目标文件与蓝图记录一致 | `wc -l 目标文件` | 行数与蓝图记录偏差<5% |
| 3 | 确认无未提交变更 | `git status` | working tree clean |

**执行中**：

| # | 约束 | 说明 |
|---|------|------|
| 1 | 一次只操作1个文件 | 禁止批量操作 |
| 2 | 每步操作后立即验证 | 运行相关测试 |
| 3 | 验证通过后立即 git commit | 提交信息包含任务卡编号 |

**Post-merge Verify（合并后）**：

| # | 验证项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 旧 import 路径零残留 | `grep -r "from zephyr.旧路径" src/` | 返回零结果 |
| 2 | class/function 列表完整性 | `diff <(旧grep class) <(新grep class)` | 仅新增项，无删除项 |
| 3 | 相关测试全部通过 | `pytest tests/相关目录/` | 0 failed |

### 11.0c 任务卡安全条款模板

> 每个任务卡必须包含以下安全条款。

```yaml
acceptance_criteria:
  - "旧 import 路径零残留: grep -r 'from zephyr.旧路径' src/ 返回零结果"
  - "class/function 列表完整性: 合并后对比无遗漏"
  - "相关测试通过: pytest tests/相关目录/ 返回 0 failed"

applicable_rules:
  - "§4.1b 安全搬家铁律 #1-#9"
  - "§4.1c 价值分析方法论 步骤1-5"
  - "§11.0b 强制安全协议 Pre-flight + 执行中 + Post-merge"
```

### 11.0d 细化任务卡完整清单（51个卡）

> 所有重组任务卡按 Phase 分组，每个卡包含：编号、名称、是否依赖前置卡、前置卡编号。

**Phase 1（2卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0021 | 修复resource_optimization测试失败 | false | 无 |
| SRC-0022 | 接入真实LLM API | false | SRC-0021 |

**Phase 2（12卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0023 | PO拆分：ModelRouter | true | SRC-0022 |
| SRC-0024 | PO拆分：CircuitBreakerManager | true | SRC-0023 |
| SRC-0025 | PO拆分：CostTracker | true | SRC-0023 |
| SRC-0026 | PO拆分：DeadLetterQueue | true | SRC-0023 |
| SRC-0027 | PO拆分：PreemptionManager | true | SRC-0023 |
| SRC-0028 | PO拆分：PipelineLock验证对齐 ✅ | true | SRC-0023 |
| SRC-0029 | PO拆分：精简PO为dispatch-only编排器 ✅ | true | SRC-0023 |
| SRC-0030 | drift拆分：DriftEngine编排器 ✅ | true | SRC-0021 |
| SRC-0031 | drift拆分：DriftInfrastructure ✅ | true | SRC-0030 |
| SRC-0032 | drift拆分：AIConstructionDetectors ✅ | true | SRC-0030 |
| SRC-0033 | drift拆分：DriftResultTypes ✅ | true | SRC-0030 |
| SRC-0034 | drift拆分：DriftTraining ✅ | true | SRC-0030 |

**Phase 2b（1卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0068 | 10个>650行大文件拆分评估 ✅ | false | SRC-0021 |

**Phase 3a（9卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0035 | 合并：telemetry→l12 ✅ | true | SRC-0021 |
| SRC-0036 | 合并：event_bus副本→shared | true | SRC-0035 |
| SRC-0037 | 合并：event_bus_upgrade版本分叉→独立命名 | true | SRC-0036 |
| SRC-0038 | 合并：drift_detector副本→真源 ✅ | true | SRC-0035 |
| SRC-0039 | 合并：escalation→escalation_engine独立保留 | true | SRC-0035 |
| SRC-0040 | 合并：asset_inventory同类合并 | true | SRC-0035 |
| SRC-0041 | 合并：kill_switch×4副本→shared真源 | true | SRC-0035 |
| SRC-0042 | 合并：unified_memory_api顶层副本→storage真源 | true | SRC-0035 |
| SRC-0043 | 合并：context_engine/pipeline_orchestrator轻量版→pipeline真源 | true | SRC-0035 |

**Phase 3b（1卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0044 | 75个同名文件审计 | false | SRC-0021 |

**Phase 3c（12卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0045 | 版本分叉归一：orchestrator/trigger_router | true | SRC-0035 |
| SRC-0046 | 版本分叉归一：orchestrator/agent_orchestrator | true | SRC-0035 |
| SRC-0047 | 版本分叉归一：orchestrator/agent_health_monitor | true | SRC-0035 |
| SRC-0048 | 版本分叉归一：orchestrator/rollback_manager | true | SRC-0035 |
| SRC-0049 | 版本分叉归一：orchestrator/failure_matcher | true | SRC-0035 |
| SRC-0050 | 版本分叉归一：orchestrator/hallucination_detector | true | SRC-0035 |
| SRC-0051 | 版本分叉归一：orchestrator/session_manager | true | SRC-0035 |
| SRC-0052 | 版本分叉归一：orchestrator/state_synchronizer | true | SRC-0035 |
| SRC-0053 | 版本分叉归一：orchestrator/file_task_mapper | true | SRC-0035 |
| SRC-0054 | 版本分叉归一：shared/context.py | true | SRC-0035 |
| SRC-0055 | 版本分叉归一：core/blueprint_code_sync.py | true | SRC-0035 |
| SRC-0056 | 版本分叉归一：core/session_continuity.py | true | SRC-0035 |

**Phase 3d（4卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0069 | context_engine归一：doc_compressor | true | SRC-0035 |
| SRC-0070 | context_engine归一：prompt_registry | true | SRC-0035 |
| SRC-0071 | context_engine归一：intent_keyword_mapper | true | SRC-0035 |
| SRC-0072 | context_engine归一：intent_parser | true | SRC-0035 |

**Phase 4（1卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0057 | CheckType注册表化 | true | SRC-0021 |

**Phase 5（6卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0058 | SafetyGate参数化：框架搭建 | true | SRC-0021 |
| SRC-0059 | SafetyGate参数化：L1-L10规则提取 | true | SRC-0058 |
| SRC-0060 | SafetyGate参数化：L11-L20规则提取 | true | SRC-0058 |
| SRC-0061 | SafetyGate参数化：L21-L40规则提取 | true | SRC-0058 |
| SRC-0062 | SafetyGate参数化：L41-L67规则提取 | true | SRC-0058 |
| SRC-0063 | SafetyGate参数化：旧文件deprecated标记 | true | SRC-0059 |

**Phase 6-7（2卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0064 | capabilities.yaml | false | SRC-0035 |
| SRC-0065 | phase:future标记 | false | SRC-0064 |

**评估类（2卡）**：

| 卡号 | 名称 | 依赖前置 | 前置卡号 |
|------|------|:---:|---------|
| SRC-0066 | task_repo评估 | false | SRC-0021 |
| SRC-0067 | _gen_inherited评估 | false | SRC-0021 |

### 11.0e 重组-蓝图同步工作流

> 每个任务卡执行时，必须按以下工作流同步更新蓝图。

```
任务卡执行 → 代码变更 → 验证通过 → git commit → 蓝图更新 → git commit → 下一个任务卡
     ↑                                                              |
     └──────────── 验证失败则回滚，不更新蓝图 ─────────────────────────┘
```

**关键约束**：
- 代码变更和蓝图更新是**两个独立 commit**，不可合并
- 蓝图更新必须包含：变更记录条目、受影响章节的数值更新、安全删除协议状态更新
- 禁止"先做5个任务卡再统一更新蓝图"——AI上下文有限，延迟更新必出幻觉

### 11.0f GOV-RSTR-001 生命周期与归档

| 阶段 | 状态 | 触发条件 | 产出 |
|------|------|---------|------|
| 规划 | active | Owner审批 | 本蓝图 |
| 施工中 | active | 第一个任务卡开始执行 | 任务卡执行记录 |
| 施工完成 | completed | 所有任务卡执行完毕+全量测试通过 | 施工完成报告 |
| 归档 | archived | 重组后稳定运行≥2周 | 归档至 `docs/09_audit/` |

**归档条件**：
1. 所有任务卡状态为 completed 或 cancelled
2. 全量测试连续通过≥3次
3. 蓝图与代码状态一致（偏差<5%）
4. Owner确认归档

### 11.0g GOV-RSTR-001 范围边界

**GOV-RSTR-001负责**：
- 大文件拆分（PipelineOrchestrator 2541行→7组件、drift_engine 2134行→5组件）
- 跨目录重复合并（75个同名文件→每类1真源）
- 版本分叉归一（15对目录内部版本分叉+4对context_engine内部同名文件）
- 参数化替代膨胀（18个safety_gate_L*.py→2-3个参数化类）
- 注册表替代if-elif（GateEngine 24种CheckType注册表化）
- 按需激活（capabilities.yaml）
- 占位标记（phase:future）

**GOV-RSTR-001不负责**：
- 蓝图-代码脱节（其他蓝图需自行与本蓝图对齐）
- 盲点膨胀（新增模块的蓝图缺失由GOV-DOC-002管辖）
- 新模块蓝图缺失（由模块ID注册表管辖）
- 功能性bug（由各模块蓝图管辖）
- 性能优化（非重组范畴）
- 代码质量（lint/type hint等非重组范畴）

### 11.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 9 个 Phase（含Phase 2b大文件评估+Phase 3d context_engine归一） |
| 施工模式 | 重构迁移 |
| 核心风险 | 合并重复模块时 import 链断裂 |

### 11.2 前置条件

| # | 依赖项 | 依赖类型 | 说明 |
|---|--------|---------|------|
| 1 | Python 3.12+ 环境 | hard | `python --version` 返回 3.12+ |
| 2 | 现有测试全部通过 | hard | `pytest tests/` 返回 0 failed（⚠️ 当前有1个测试失败：test_self_heal_succeeds_on_first_try StopIteration，需先修复） |
| 3 | git 仓库可用 | hard | `git status` 正常返回（分支 `trae-redteam-deadly-5`） |
| 4 | DeepSeek API Key 已就绪 | hard | 环境变量 `DEEPSEEK_API_KEY` |
| 5 | GLM API Key 已就绪 | soft | Phase 5 后需要，可后置 |
| 6 | 本蓝图已被 Owner 审批 | hard | status: active |
| 7 | 已确认 §4.1b 安全搬家铁律全部理解 | hard | 能列出9条铁律 |
| 8 | 已确认 §4.1c 价值分析方法论理解 | hard | 能列出5个步骤 |

---

### 11.3 实施步骤

#### Phase 1：接入真实 LLM API

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §1.2 目标 #1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py`（修改 `_call_model()`） |
| 验收标准 | `dispatch()` 执行后 `PipelineResult.modules[*].output.simulated == False` |
| G7 检查项 | M3输出是否为真实AI生成的代码？token计数是否正确？成本是否在预算内？ |

**变更内容**：
- `_call_model()` 方法，在第 ~1502 行，`simulated: True` 之前插入真实 API 调用
- 模型映射：`DeepSeek-V4-Pro` → `deepseek-chat`，`GLM-5.1` → `glm-4-flash`
- 新增依赖：`openai>=1.0.0`

#### Phase 2：PipelineOrchestrator 拆分

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.3 拆分后组件接口 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\pipeline\` |
| 验收标准 | `dispatch()` 端到端测试通过；每个组件 ≤400行；无循环导入 |
| G7 检查项 | 所有 `from zephyr.pipeline.pipeline_orchestrator import` 语句是否更新？旧方法是否完全移除？ |
| ⚠️ 依赖 | Phase 1 必须先完成——Phase 1 在单体文件中插入 LLM 调用代码，Phase 2 拆分时该代码需迁移到对应组件（ModelRouter）中 |

**创建文件清单**（PipelineLock 已存在——仅需验证对齐）：

| module_id | 文件名 | doc_type | 完整绝对路径 | 说明 |
|-----------|--------|----------|------------|------|
| MOD-INF-006-ROUTER | model_router.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\model_router.py` | 新建 |
| MOD-INF-006-BREAKER | circuit_breaker_manager.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\circuit_breaker_manager.py` | 新建 |
| MOD-INF-006-COST | cost_tracker.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\cost_tracker.py` | 新建 |
| MOD-INF-006-DLQ | dead_letter_queue.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\dead_letter_queue.py` | 新建 |
| MOD-INF-006-PREEMPT | preemption_manager.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\preemption_manager.py` | 新建 |
| MOD-INF-006-LOCK | pipeline_lock.py | code | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_lock.py` | 已存在——仅需验证接口 |

**注意**：`route-manifest.yaml` 在此 Phase 一并删除（保留 `route_manifest.yaml`）。

#### Phase 3a：消除跨目录重复模块——合并真源

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.5 合并后真源声明（跨目录部分） |
| 产出位置 | 各真源路径 |
| 验收标准 | `grep -r "from zephyr.telemetry" src/` 返回零结果；全量测试通过 |
| 优先级建议 | 先做跨目录（影响面小），再做内部（影响面大） |
| G7 检查项 | 每个废弃路径是否已搜索全项目确认无残留引用？旧 import 是否全部更新？ |

**执行顺序**：
1. telemetry/ → l12_system_telemetry/（2→1）
2. event_bus 副本 → shared/event_bus.py（2→1）；event_bus_upgrade 版本分叉 → 默认方案：保留 shared/event_bus_upgrade.py（事件版本化），l01版重命名为 shared/upgrade_strategy.py（升级策略）独立保留（2→2，独立命名）
3. drift_detector 副本 → drift_detector/（5→1）
4. escalation/ → ⚠️ 功能不同不能简单合并——escalation/（运行时升级引擎，10文件）重命名为 escalation_engine/ 独立保留，escalation_protocol/（安全策略集，83文件）保持不变
5. asset_inventory 同类合并（22→约14）

#### Phase 3b：目录内部版本分叉审计与归一**

**⚠️ 重要：经逐对审计确认，`shared/` 顶层36个同名文件中35个是 `Re-export wrapper`（顶行明确写了"Backward-compatible alias, canonical at subdir/..."），1个是版本分叉（`context.py`——顶层与 `utils/context.py` 内容不同，均非 wrapper）——re-export 无需处理，context.py 默认保留子目录版（utils/），顶层版标记 deprecated。**

**⚠️ 补充：`core/` 顶层也有2对版本分叉（`blueprint_code_sync.py` 112处差异、`session_continuity.py` 571处差异），均非 re-export wrapper。**

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §1.2 目标 #4（跨目录重复消除——目录内部版本分叉情况复杂于预期） |
| 审计结论 | orchestrator/ + shared/ + core/ 顶层与子目录同名文件，情况分为三类： |
| 风险等级 | 低——仅需理清版本关系，不需大规模删除 |

**分类审计结果**：

**A. orchestrator/（12对已验证完毕）**：

| 文件 | 顶层状态 | 子目录版本 | 分类 | 差异量 | 建议动作 |
|------|---------|----------|------|-------|---------|
| `task_queue.py` | re-export wrapper | `core/task_queue.py`（真源） | **re-export** | — | 无需改动 |
| `deferred_queue.py` | 内容相同 | `resilience/deferred_queue.py` | **相同副本** | 0 diff | 确认后废弃顶层 |
| `wave_generator.py` | 内容相同 | `core/wave_generator.py` | **相同副本** | 0 diff | 确认后废弃顶层 |
| `trigger_router.py` | 不同实现 | `core/trigger_router.py` | **版本分叉** | 68 diff | 默认保留子目录版（core/），顶层版标记 deprecated |
| `agent_orchestrator.py` | 不同导入路径/返回类型 | `core/agent_orchestrator.py` | **版本分叉** | 大 | 默认保留子目录版（core/），顶层版标记 deprecated |
| `agent_health_monitor.py` | 无 `from __future__`/`Self` | `state/agent_health_monitor.py`（有 `from __future__`/`Self`） | **版本分叉** | 14 diff | 默认保留子目录版（state/，有类型注解），顶层版标记 deprecated |
| `rollback_manager.py` | "仅调试用途" | `resilience/rollback_manager.py`（"实现状态回滚 T-2-05"） | **版本分叉** | 大 | 用途不同——可能都应保留 |
| `failure_matcher.py` | 不同实现 | `resilience/failure_matcher.py` | **版本分叉** | 12 diff | 默认保留子目录版（resilience/），顶层版标记 deprecated |
| `hallucination_detector.py` | 不同实现 | `resilience/hallucination_detector.py` | **版本分叉** | 22 diff | 默认保留子目录版（resilience/），顶层版标记 deprecated |
| `session_manager.py` | 不同实现（158行） | `state/session_manager.py`（254行） | **版本分叉** | 322 diff | 默认保留子目录版（state/，更完整），顶层版标记 deprecated |
| `state_synchronizer.py` | 不同实现 | `state/state_synchronizer.py` | **版本分叉** | 2 diff | 微小差异，建议保留子目录版 |
| `file_task_mapper.py` | 不同实现 | `state/file_task_mapper.py` | **版本分叉** | 5 diff | 微小差异，建议保留子目录版 |

**B. shared/（1对版本分叉）**：

| 文件 | 顶层状态 | 子目录版本 | 分类 | 差异量 | 建议动作 |
|------|---------|----------|------|-------|---------|
| `context.py` | 实际实现 | `utils/context.py` | **版本分叉** | 不同 | 默认保留子目录版（utils/），顶层版标记 deprecated |

**C. core/（2对版本分叉）**：

| 文件 | 顶层状态 | 子目录版本 | 分类 | 差异量 | 建议动作 |
|------|---------|----------|------|-------|---------|
| `blueprint_code_sync.py` | 实际实现 | `sync/blueprint_code_sync.py` | **版本分叉** | 112 diff | 默认保留子目录版（sync/），顶层版标记 deprecated |
| `session_continuity.py` | 实际实现 | `session/session_continuity.py` | **版本分叉** | 571 diff | 默认保留子目录版（session/），顶层版标记 deprecated |

**执行建议**：
- 此 Phase 可在 Phase 3a 完成后、Phase 4 之前插空执行
- 优先级低于 Phase 3a（跨目录合并）——但不可忽略
- 已验证的 15 对中：orchestrator/ 1对re-export + 2对相同副本 + 9对版本分叉；shared/ 1对版本分叉(context.py)；core/ 2对版本分叉
- 人类决策后，版本分叉文件统一到子目录层级

#### Phase 4：GateEngine CheckType 注册表化

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §1.2 目标 #3 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\gates\check_types\`（新建目录） |
| 验收标准 | 24种 CheckType 各有独立文件；registry.py 可通过 `get_check_type()` 获取 |
| G7 检查项 | GateEngine.evaluate() 是否仍正常工作？YAML 配置引用是否更新？ |

#### Phase 5：Feedback Loop Gates 参数化

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §1.2 目标 #5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\` |
| 验收标准 | `parameterized_safety_gate.py` 可替代所有 safety_gate_L*.py；旧文件标记 deprecated |
| G7 检查项 | 所有 gate_id 是否能正确映射？YAML 配置是否完整？ |

**内容编写指引**：

| 文件 | 核心内容 | 必须包含 |
|------|---------|---------|
| parameterized_safety_gate.py | 1个类 `ParameterizedSafetyGate(gate_id, rule_set)` | `evaluate(context) -> GateResult` |
| safety_gate_config.yaml | 现有67个gate的规则提取为YAML配置 | gate_id, rules, severity, activation_condition |

#### Phase 6：引入 capabilities.yaml 按需加载

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.1 capabilities.yaml schema |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\capabilities.yaml`（新建） |
| 验收标准 | A2A/CodeDedup/Chaos/Canary/LSG L4-L8/Budget 均处于默认 OFF/WARN 状态 |
| G7 检查项 | 默认 OFF 的子系统是否确实不执行？config.py 是否正确解析？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| GOV-RSTR-001-CAP | capabilities.yaml | config | `D:\ZephyrAlpha\src\zephyr\capabilities.yaml` |

#### Phase 7：占位模块标记 phase:future

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §1.2 目标 #7 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\l07_post_trade_analytics\__init__.py`, `l09_research_innovation\__init__.py`, `l11_ml_platform\__init__.py`, `_cross_layer\__init__.py` |
| 验收标准 | 每个文件 frontmatter/注释中包含 `phase:future` 标记；搜索 `phase:future` 可列出所有延迟模块 |
| G7 检查项 | 标记是否清晰？AI 是否能区分 "phase:future" 和 "abandoned"？ |

---

### 11.4 回滚方案

| Phase | 如果出问题 | 回滚操作 |
|-------|----------|---------|
| 1 | LLM API 调用持续失败 | 恢复 `simulated: True` fallback |
| 2 | 拆分后 dispatch() 行为不一致 | `git revert` PipelineOrchestrator；恢复原单体文件 |
| 3a | 合并后跨目录 import 链断裂 | 逐模块撤销合并；恢复被废弃目录 |
| 3b | 版本分叉文件误删导致功能丢失 | 回退文件删除操作；人类决策前不执行任何删除；保留被废弃版本的备份 |
| 4 | 注册表化后门禁行为不一致 | 回退到 gate_engine.py 内联 CheckType |
| 5 | 参数化后个别 gate 行为异常 | 为异常 gate 保留独立文件；其余用参数化类 |
| 6 | capabilities.yaml 解析失败 | config.py fallback：全部 ON（与当前行为一致） |
| 7 | 标记错误导致模块被误删 | 恢复被标记模块的 phase:active 状态 |

### 11.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 |
|---|--------|---------------|
| 1 | 真实 LLM 调用 | `_call_model()` 返回 non-simulated 结果 |
| 2 | 6个Pipeline组件 | `D:\ZephyrAlpha\src\zephyr\pipeline\model_router.py` 等5新建 + `pipeline_lock.py` 对齐 |
| 3 | 合并后telemetry | `D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\`（旧目录已废弃） |
| 3b | 版本分叉归一结果 | 15对同名文件中：2对相同副本顶层文件已废弃；9对版本分叉已人类决策并统一到保留版本；shared/context.py 已决策；core/ 2对已决策 |
| 4 | CheckType注册表 | `D:\ZephyrAlpha\src\zephyr\gates\check_type_registry.py` |
| 5 | 参数化SafetyGate | `D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\parameterized_safety_gate.py` |
| 6 | capabilities.yaml | `D:\ZephyrAlpha\src\zephyr\capabilities.yaml` |
| 7 | phase:future 标记 | 4个占位模块注释完成 |
| 8 | pipeline/ route 文件 | `route-manifest.yaml` 已删除，仅保留 `route_manifest.yaml` |

### 11.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | — |
| verification_status | unverified | — |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 系统重组方案（拆分/合并/按需激活/LLM接入） | **本文档 §1-§10** |
| 重组施工步骤 | **本文档 §11** |
| 按需激活配置的 Schema | **本文档 §3.1-§3.2** |
| 拆分后的组件接口 | **本文档 §3.3** |
| 合并后的模块真源 | **本文档 §3.5** |
| 受影响的蓝图清单 | **本文档 §8** |

**任何与本蓝图冲突的重组决策，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | §3 接口契约、§5 依赖关系 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\pipeline\blueprint.md` | §3.3 PipelineOrchestrator 拆分 |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\` gates 相关蓝图 | §3.5 合并、Phase 4 CheckType 注册表 |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\config.py` | §3.1 capabilities.yaml |
| Tier 2 | `D:\ZephyrAlpha\src\zephyr\pipeline\__init__.py` | §3.3 拆分后新模块的导出 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\pipeline\pipeline_orchestrator.py` | Phase 1-2 施工目标 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改重组项 | 下游蓝图更新 depends_on | — |
| 修改施工步骤 | 下游蓝图更新产出物引用 | 代码模块更新 import |
| 修改合并真源路径 | 下游蓝图全量引用更新 | 代码模块全量路径更新 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 新增重组项 | 需 Owner 审批 |
| 修改拆分/合并目标 | 需 Owner 审批 + Tier 1 消费者通知 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| Phase 优先级调整 | AI 可自主修改 |

---

## 附录 A：75个跨目录同名文件完整清单

> 扫描范围：`D:\ZephyrAlpha\src\zephyr\` 下所有 `.py` 文件（不含 `__init__.py`）
> 定义：同名文件出现在 2+ 个不同顶层模块目录中
> 详细清单见数据库任务卡 SRC-0044 的审计结果

### A.1 高副本数（≥3副本）：kill_switch×5, circuit_breaker×4, models×4, cli×3, config×3, failure_matcher×3, health×3, phase_executor×3, secrets×3, task_queue×3, trigger_router×3

### A.2 2副本（50+个）：alert_router, alerts, anomaly, anomaly_detector, anti_pattern_guard, app, blind_spot_tracker, blueprint_metrics, budget_tracker, cache_invalidation, canary_manager, checkpoint_manager, cold_start, cold_stub, complexity_budget, config_validator, construction_verifier, context_package, contract_bus, contract_metrics, contract_tester, cost_tracker, cross_module_integration, dashboard, data_lifecycle, drift_detector(✅已声明), escalation_engine, event_bus(✅已声明), event_bus_upgrade(✅已声明), event_sink, event_store, exceptions, finding, fitness_functions, handoff_manager, health_monitor, identity_verifier, integration_test_runner, integrity, knowledge_freshness, llm_impact_analyzer, pipeline_orchestrator(✅已声明), protocol, pydantic_v2_migrator, reconciler, regime_detector, registry, risk_limits, risk_mitigation, runbook_generator, saga_compensator, scanner, schema, schema_evolution, schema_migration, self_test, semantic_cache, span_stub, structured_sink, toctou_guard, token_budget, vector_bridge, warm_hot_gate

---

## 附录 B：82个>400行文件完整清单

> 扫描范围：`D:\ZephyrAlpha\src\zephyr\` 下所有 `.py` 文件

### B.1 >1000行（6个——必须有拆分方案或明确不拆分理由）

| 行数 | 文件 | 蓝图处理状态 |
|:----:|------|:----------:|
| 2303 | pipeline/pipeline_orchestrator.py | ✅ §3.3拆分为7组件（原2541行→2303行，-9%） |
| 443 | drift_detector/drift_engine.py | ✅ §3.3b拆分为5组件（原2134行→443行，-79%） |
| 1743 | db/task_repo.py | ⚠️ SRC-0066评估中 |
| 1494 | feedback_loop/_gen_inherited.py | ⚠️ SRC-0067评估中 |
| 1167 | gates/gate_engine.py | ✅ Phase 4 注册表化 |
| 1001 | pipeline/models.py | ⚠️ 建议 SRC-0068a |

### B.2 650-1000行（13个——需评估是否拆分）

| 行数 | 文件 | 蓝图处理状态 |
|:----:|------|:----------:|
| 995 | pipeline/pipeline_roadmap.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 1023 | orchestrator/contract_registry.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 923 | mcp/task_manager_server.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 918 | orchestrator/agent_orchestrator.py | ✅ 已知版本分叉 |
| 877 | orchestrator/resilience/hallucination_detector.py | ✅ 已知版本分叉 |
| 877 | orchestrator/hallucination_detector.py | ✅ 已知版本分叉 |
| 861 | governance/phase_check_registry.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 858 | orchestrator/core/agent_orchestrator.py | ✅ 已知版本分叉 |
| 827 | feedback_loop/scheduler.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 843 | rollback/rollback_executor.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 835 | shared/lifecycle/resource_optimization_engine.py | ✅ SRC-0021相关 |
| 824 | db/sqlite_schema.py | ⚠️ SRC-0068 已评估（见 §3.4） |
| 777 | mcp/governance_server.py | ⚠️ SRC-0068 已评估（见 §3.4） |

---

### §3.4 10个大文件拆分评估（SRC-0068）

**评估日期**: 2026-05-10
**总扫描数**: src/ 下 91 个 >300行文件
**评估目标**: 10个 >650行 文件

#### 拆分优先级建议

| 优先级 | 文件 | 当前行数 | 建议策略 | 预估产出 |
|:----:|------|:-------:|----------|:-------:|
| 1 | `db/task_repo.py` | 1743 | 拆为 base_repo.py + transition.py + query.py + file_mapper.py | 4-5个组件 |
| 2 | `feedback_loop/_gen_inherited.py` | 1494 | 拆为 generator.py + template.py + validator.py | 3个组件 |
| 3 | `orchestrator/contract_registry.py` | 1023 | 拆为 registry.py + contract_defs.py + validation.py | 3个组件 |
| 4 | `pipeline/models.py` | 1001 | 按领域拆为 task_models.py + result_models.py + config_models.py | 3-4个文件 |
| 5 | `pipeline/pipeline_roadmap.py` | 995 | 拆为 roadmap.py + stage_defs.py + routing.py | 3个组件 |
| 6 | `mcp/task_manager_server.py` | 923 | 拆为 server.py + handlers.py + business_logic.py | 3个组件 |
| 7 | `governance/phase_check_registry.py` | 861 | 注册表化：check_defs.py + registry.py | 2个组件 |
| 8 | `rollback/rollback_executor.py` | 843 | 拆为 executor.py + strategies.py + verifier.py | 3个组件 |
| 9 | `feedback_loop/scheduler.py` | 827 | 拆为 scheduler.py + policies.py + triggers.py | 3个组件 |
| 10 | `db/sqlite_schema.py` | 824 | 拆为 schema.py + migrations.py + indices.py | 3个文件 |

**说明**: 以上10个文件均未进行拆分，建议在 Phase 3-7 中依次处理。每个文件的拆分将创建独立的 SRC 任务卡。

#### 已完成的拆分（作为参照基准）

| 文件 | 原行数 | 现行数 | 缩减率 | 拆分产出 |
|------|:----:|:-----:|:-----:|---------|
| `drift_engine.py` | 2134 | 443 | -79% | 4组件 |
| `pipeline_orchestrator.py` | 2541 | 2303 | -9% | 6组件（仍有优化空间） |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-10 | 3.3.0 | **Phase 2c 完成！SRC-0068 10个大文件拆分评估**：附录B大文件行数更新为当前实际值（pipeline_orchestrator.py 2303行、drift_engine.py 443行、task_repo.py 1743行、gate_engine.py 1167行等）。新增 §3.4 评估报告——10个目标文件拆分优先级排序、策略建议、预估产出。B.1/B.2 状态全部刷新为"已评估（见 §3.4）"或当前实际处理状态。 |
| 2026-05-10 | 3.2.0 | **Phase 2b 完成！SRC-0030~0034 drift拆分5组件全部完成**：SRC-0030 DriftEngine编排器精简 + SRC-0031 DriftInfrastructure修复导入路径 + SRC-0032 AIConstructionDetectors（7个detect_*方法全部补充docstring，455行）+ SRC-0033 DriftResultTypes（7个*Result数据类+9个detect_*函数全部补充docstring，937行）+ SRC-0034 DriftTraining（3个数据类+8个函数全部补充docstring，407行）。修复 `a2a_red_team.py` 截断的 `_attack_session_smuggling` 方法并补充完整实现。更新 `test_trigger_router.py` 中 `handle_drift_stub` 测试以匹配 operational 阶段行为。28个 drift 相关测试全部通过。 |
| 2026-05-10 | 3.1.0 | **Phase 2 全部完成！SRC-0029: 精简 PO 为 dispatch-only**——修复 2 处 Phase 2 拆分残留致命 Bug：(1) `health_check()` L1534 `self._cost_total`→`self._cost_tracker.total_cost()`（SRC-0025 残留引用）；(2) `_run_with_fallback()` L1048 `self._FALLBACK_CHAIN`→`ModelRouter.FALLBACK_CHAIN`（SRC-0023 漏改）。清理死代码 `_glm_reject_log`（仅在 `save_state()`/`load_state()` 中引用，从未写入）。PO 行数 2307→2303。Phase 2 总成果：7 组件全部提取完成（ModelRouter + CircuitBreakerManager + CostTracker + DeadLetterQueue + PreemptionManager + PipelineLock + 本次精简），PO 从原始 ~2541 行降至 ~2303 行。 |
| | 2026-05-10 | 3.0.4 | **SRC-0028: PipelineLock 验证通过**——已是独立组件（`src/zephyr/pipeline/pipeline_lock.py`, 490行），无需提取。蓝图 §3.3 将其列为"已存在——仅需验证接口对齐"完全正确。 |
| 2026-05-10 | 3.0.3 | **Phase 2 SRC-0026 完成**：DeadLetterQueue 从 PipelineOrchestrator 提取为独立组件（`src/zephyr/pipeline/dead_letter_queue.py`, ~80行）。接口：`enqueue(task_card, results, status, max_retries)` / `drain()` / `entries`（只读属性）/ `count`（只读属性）/ `save_state()` / `load_state()`。PipelineOrchestrator 内部 `_dead_letters` 替换为 `_dlq`，`_maybe_dead_letter()` 委托至 `_dlq.enqueue()`，`get_dead_letters()` 委托至 `_dlq.entries`，`save_state()`/`load_state()`/`health_check()` 中死信相关逻辑全部委托至 DLQ。`__init__.py` 新增 DeadLetterQueue 导出。 |
| 2026-05-10 | 3.0.2 | **Phase 2 SRC-0025 完成**：CostTracker 从 PipelineOrchestrator 提取为独立组件（`src/zephyr/pipeline/cost_tracker.py`, ~135行）。接口：`record_call(model, tokens_input, cost_usd)` / `estimate_cost(model, tokens)` / `total_cost()` / `summary()` / `save_state()` / `load_state()` + `records` 只读属性。PipelineOrchestrator 内部 `_cost_total`/`_cost_records` 替换为 `_cost_tracker`，`get_cost_summary()` 委托至 `_cost_tracker.summary()`，`_compute_module_costs()` 方法删除（dispatch() 改用 `_cost_tracker.records`）。`__init__.py` 新增 CostTracker 导出。同时修正蓝图任务表中 SRC-0023~SRC-0029 编号以对齐 TaskRepository 权威数据。 |
| 2026-05-10 | 3.0.1 | **Phase 2 SRC-0023 完成**：ModelRouter 从 PipelineOrchestrator 提取为独立组件（`src/zephyr/pipeline/model_router.py`, ~175行）。包含 5 个公共类属性（FALLBACK_CHAIN / MODEL_VERSION_MAP / MODEL_CONTEXT_LIMITS / MODEL_COST_PER_1K_INPUT / MODEL_COST_PER_1K_OUTPUT）和 5 个静态方法（resolve_model / fallback_chain_for / estimate_cost / model_version_for / context_limit_for）。PipelineOrchestrator._route_model() 委托至 ModelRouter.resolve_model()，_FALLBACK_CHAIN / _MODEL_* 属性全部移除。 |
| 2026-05-10 | 3.0.0 | **v1.5→v3.0全面重建**（major：整合v2.0/v2.1所有内容+脱节修复后数据更新）：(1)§4.1b安全搬家铁律9条+§4.1c价值分析方法论5步；(2)§3.3b drift_engine拆分5组件接口+§3.4b文件映射；(3)§3.5新增7条真源声明（KillSwitch/UnifiedMemoryAPI/ContextEngine PO/DocCompressor/PromptRegistry/IntentKeywordMapper/IntentParser）；(4)安全删除协议新增7条(#10-#16)；(5)§11.0b强制安全协议+§11.0c任务卡安全条款模板+§11.0d 51个任务卡(SRC-0021~0072)+§11.0e蓝图同步工作流+§11.0f生命周期归档+§11.0g范围边界；(6)容量估算更新：1791文件/218K行/82个>400行/6个>1000行/75个同名文件；(7)施工阶段9个Phase；(8)附录A 75同名文件+附录B 82大文件；(9)PO行数2335→2541/_call_model 1293→1502 |
| 2026-05-08 | 1.5.0 | **操作安全审查修正**（minor→major：含策略级变更）：(1)蓝图声称"没有 git 备份仓库"——实际有 git（分支 trae-redteam-deadly-5，有完整提交历史），安全删除协议重写为"删除前必须 git commit"；(2)escalation/ 和 escalation_protocol/ 功能不同不能简单合并——escalation/ 是运行时升级引擎，escalation_protocol/ 是安全策略集，默认方案改为 escalation/ 重命名为 escalation_engine/ 独立保留；(3)铁律#4 "5文件约束"与 Phase 2 冲突（拆分需10+文件），放宽为"Phase 2 允许≤7新文件+≤3修改文件"；(4)前置条件新增"现有测试全部通过"和"git仓库可用"——当前有2个 CircuitBreaker 测试失败需先修复；(5)铁律#5 说明从"删了就没了"更新为"git revert 可回滚" |
| 2026-05-08 | 1.4.3 | **铁律#8合规性修正**：(1)全文消除"需人类决策""待决策"等模糊词——版本分叉统一给出默认建议"保留子目录版，顶层版标记 deprecated"；(2)EventBusUpgrade 给出明确默认方案"l01版重命名为 shared/upgrade_strategy.py 独立保留"；(3)§3.4 文件映射补充 PipelineLock 行（7个组件此前只映射6个）；(4)§8 #8 Feedback Loop 蓝图路径修正为 MOD-INF-010 精确路径；(5)Phase 2 新增依赖说明——Phase 1 LLM代码需在 Phase 2 拆分时迁移到 ModelRouter |
| 2026-05-08 | 1.4.2 | **方案逻辑审查修正**：(1)§3.3 补充 PipelineLock 接口定义（7个组件此前只定义6个）；(2)§3.5 拆分"被废弃的副本路径"和"版本分叉"为独立列——EventBusUpgrade 不再被错误归类为"被废弃副本"；(3)§1.2 目标#4 "需决策"改为可衡量标准"→1个合并文件或2个独立命名文件（人类决策后确定）"——消除违反铁律#8的模糊词；(4)§11.5 补充 Phase 3b 完成标准（此前遗漏）；(5)§4.2 新增"目录内部版本分叉"容量估算行；(6)§11.4 Phase 3b 回滚方案更新过时条件；(7)§8 #7 Gates 蓝图路径从模糊的"如有"修正为实际存在的 MOD-INF-007 精确路径 |
| 2026-05-08 | 1.4.1 | **二次深度审计修正**：(1)Python文件总数 1724→1725（代码持续增长）；(2)§涉及文件范围#15a更新为完整审计结果（替换过时的"部分文件需确认"描述）；(3)event_bus_upgrade 从"简单副本"重分类为"版本分叉"——l01版是"升级策略(生成升级计划)"，shared版是"事件版本化+增量升级"，功能不同需人类决策；(4)Phase 3a asset_inventory 数字统一为"22→约14"（原"20→12"与§涉及文件范围不一致）；(5)event_bus×4 细化为 event_bus×2(1真源+1副本) + event_bus_upgrade×2(版本分叉)；(6)"14项重组动作"删除硬编码数字（实际计数与描述不符）；(7)Phase 3b 从"Orchestrator版本分叉审计"扩展为"目录内部版本分叉审计"——新增 shared/context.py 和 core/ 2对版本分叉（此前遗漏） |
| 2026-05-08 | 1.4.0 | **深度审计修正**：(1)总代码行数 ~160K→~164K(实际164,074)；(2)PipelineOrchestrator 2292→2335行；(3)Feedback Loop Gates 44→18个safety_gate_L*.py文件(覆盖L1-L67共67个gate level)；(4)Phase 4 CheckType 19→24种；(5)_call_model() 行号 ~1188→~1293；(6)shared/ "全部re-export"→"35/36 re-export + context.py版本分叉"；(7)orchestrator/ trigger_router "相同副本"→"版本分叉(68 diff)"；(8)wave_generator "未验证"→"相同副本(0 diff)"；(9)6个"未验证"文件全部分类完毕(9对版本分叉+2对相同副本+1个re-export)；(10)core/实际59文件、shared/实际208文件；(11)蓝图标题版本 v1.2→v1.4 对齐 |
| 2026-05-08 | 1.3.0 | **数据修正**：PipelineOrchestrator 2046→2292行、Python文件 1713→1724、CheckType 19→24种、asset_inventory 20→22文件、drift_detector×5→drift相关17文件(同名重复5+语义相关12) |
| 2026-05-08 | 1.2.0 | **关键修正**：经逐对文件内容审计发现——shared/ 顶层文件全部是 Re-export wrapper（非重复），删除 30+ 条幻觉数据。orchestrator 重分类：re-export ×1、相同副本 ×2、版本分叉 ×3、未验证 ×6。重修 Phase 3b 为"版本分叉审计"。修正容量估算和完成标准。 |
| 2026-05-08 | 1.1.0 | 三方交叉审计（重组蓝图↔MOD-MASTER-001↔实际代码）——已废弃：orchestrator/shared/core 内部重复诊断基于"同名=重复"的错误假设。详见 v1.2.0 勘误。 |
| 2026-05-08 | 1.0.0 | 初始版本——重组动作完整文档化 |
