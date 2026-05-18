---
module_id: GOV-ENG-002
title: "代码重组安全策略"
doc_type: policy
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-10"
ttl: periodic_review_90d
summary: "代码重组（文件合并/拆分/迁移/重命名）的安全铁律、价值分析方法和强制执行协议。任何涉及代码搬家的操作必须遵守本策略。供 AI 执行重组任务卡时按需加载。"
tags: [policy, engineering, restructuring, safety, merge, migration]
depends_on:
  - {target: GOV-ENG-001, at: "$", why: "代码构建标准——重组后代码必须符合构建规范"}
  - {target: GOV-DOC-007, at: "$", why: "文件操作安全策略——删除/移动文件的三问三步"}
  - {target: GOV-MOD-001, at: "$", why: "AI行为铁律——IRN-003 SSoT唯一、IRN-004 断链清零"}
---

# 代码重组安全策略

> **目的**：定义 ZephyrAlpha 代码重组（合并/拆分/迁移/重命名）的强制安全规则。AI 在执行任何涉及代码搬家的操作前必须加载本策略。
> **适用场景**：跨目录重复文件合并、大文件拆分、版本分叉归一、模块迁移、re-export shim 创建。
> **module_id**: GOV-ENG-002 | **version**: 1.0.0 | **status**: active

---

## §1 安全搬家铁律（9条）

> ⚠️ 以下铁律是重组施工的**强制约束**，违反任何一条即停止施工。

| # | 铁律 | 说明 | 验证方式 |
|---|------|------|---------|
| 1 | 执行前必须重新扫描目标文件的所有 import 引用 | 蓝图记录可能过时，必须现场确认 | `grep -rn "from zephyr.目标模块" src/` 输出完整引用清单 |
| 2 | 重复文件合并必须逐条做价值分析 | 禁止"看起来一样就直接删"——必须用diff确认 | 每个副本的独有 class/function 已列出 |
| 3 | 合并后必须验证内容完整性 | 对比合并前后的 class/function 列表，确认无遗漏 | `diff <(合并前grep class) <(合并后grep class)` 返回零差异 |
| 4 | import 更新必须全量验证 | 每次合并/迁移后，全项目搜索旧 import 路径，确认零残留 | `grep -r "from zephyr.旧路径" src/` 返回零结果 |
| 5 | 一次只搬一个文件 | 禁止批量合并多个重复文件；每个文件的合并/迁移是独立原子操作 | 每个任务卡仅涉及1个重复文件的合并 |
| 6 | 搬完一个验证一个 | 每完成一个文件的合并，立即运行相关测试验证 | `pytest tests/相关目录/` 返回 0 failed |
| 7 | 每步必提交 | 每完成一个原子操作（合并+验证），立即提交 | `git log --oneline -1` 显示该步提交 |
| 8 | 安全优先，速度第二 | 宁可慢，不可漏；宁可多拆100个任务卡，不可一次合并10个文件 | 任务卡数量无上限 |
| 9 | 做完一个，更新一个蓝图 | 重组+蓝图更新是原子操作，不可拆分；禁止批量延迟更新蓝图——AI上下文有限，延迟更新必出幻觉 | 每个任务卡 = 一次重组 + 一次蓝图更新 + 一次验证 + 一次提交 |

---

## §2 重复文件价值分析方法论（5步）

> 对每个跨目录同名文件，必须按以下步骤做价值分析后才能决定处理方案。

### 步骤1：内容对比

用 `diff` 对比两个同名文件，标记差异。

### 步骤2：分类判定

| 分类 | 判定条件 | 处理方式 |
|------|---------|---------|
| 完全相同 | 0 diff | 保留1份，其余标记 deprecated |
| re-export wrapper | 顶行含 "Backward-compatible alias" 或 "re-export" | 保留真源，wrapper 标记 deprecated |
| 版本分叉 | 有实质差异，但有共享类名 | 进入步骤3 |
| 同名不同功能 | 类名/函数名完全不同 | 两个都保留，重命名消除歧义 |

### 步骤3：价值提取（仅版本分叉）

- 列出副本A的独有 class/function（B中没有的）
- 列出副本B的独有 class/function（A中没有的）
- 列出两者共有但实现不同的 class/function

### 步骤4：归并决策

| 情况 | 决策 |
|------|------|
| 独有功能 | 迁移到真源文件 |
| 共有功能 | 保留更完整的版本，删除冗余版本 |
| 全部独有 | 两个文件都保留，重命名 |

### 步骤5：验证

归并后对比 class/function 列表，确认无遗漏。

---

## §3 强制安全协议

> 以下协议是 §1 安全搬家铁律的**执行层细化**，每个任务卡必须遵守。

### 3.1 Pre-flight Scan（执行前）

| # | 扫描项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 扫描目标文件的所有 import 引用 | `grep -rn "from zephyr.目标模块" src/` | 输出完整引用清单，无遗漏 |
| 2 | 确认目标文件与蓝图记录一致 | `wc -l 目标文件` | 行数与蓝图记录偏差<5% |
| 3 | 确认无未提交变更 | `git status` | working tree clean |

### 3.2 执行中

| # | 约束 | 说明 |
|---|------|------|
| 1 | 一次只操作1个文件 | 禁止批量操作 |
| 2 | 每步操作后立即验证 | 运行相关测试 |
| 3 | 验证通过后立即提交 | 提交信息包含任务卡编号 |

### 3.3 Post-merge Verify（合并后）

| # | 验证项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 旧 import 路径零残留 | `grep -r "from zephyr.旧路径" src/` | 返回零结果 |
| 2 | class/function 列表完整性 | `diff <(旧grep class) <(新grep class)` | 仅新增项，无删除项 |
| 3 | 相关测试全部通过 | `pytest tests/相关目录/` | 0 failed |

---

## §4 任务卡安全条款模板

> 涉及代码重组的任务卡必须包含以下安全条款。

```yaml
acceptance_criteria:
  - "旧 import 路径零残留: grep -r 'from zephyr.旧路径' src/ 返回零结果"
  - "class/function 列表完整性: 合并后对比无遗漏"
  - "相关测试通过: pytest tests/相关目录/ 返回 0 failed"

applicable_rules:
  - "GOV-ENG-002 §1 安全搬家铁律 #1-#9"
  - "GOV-ENG-002 §2 价值分析方法论 步骤1-5"
  - "GOV-ENG-002 §3 强制安全协议 Pre-flight + 执行中 + Post-merge"
```

---

## §5 真源声明（GOV-FSTR-001 重组结果）

> 以下声明记录了 GOV-FSTR-001 重组完成后的真源映射。drift_detector 和 construction_verifier 应据此判断文件角色。

| 概念 | 唯一真源路径 | 被废弃的副本/shim路径 | 处理状态 |
|------|------------|---------------------|---------|
| EventBus | `shared/event_bus.py` | `core/events/event_bus.py` | ✅ 已合并 |
| EventBusUpgrade | `shared/upgrade_strategy.py`（升级策略） / `shared/event_bus_upgrade.py`（事件版本化） | — | ✅ 已独立命名 |
| DriftDetector | `drift_detector/` | `gates/drift_detector.py` 等4个副本 | ✅ 已声明 |
| Telemetry | `l12_system_telemetry/` | `telemetry/` | ✅ shim已建立 |
| EscalationEngine | `escalation_engine/` | `escalation/` | ✅ 独立保留 |
| SafetyGate | `feedback_loop/gates/parameterized_safety_gate.py` | 所有 `safety_gate_L*.py` | ✅ 已参数化 |
| KillSwitch | `shared/kill_switch.py` | 4个副本 | ✅ 已合并 |
| UnifiedMemoryAPI | `kb/storage/unified_memory_api.py` | `kb/unified_memory_api.py`（shim） | ✅ shim已建立 |
| PipelineOrchestrator | `pipeline/pipeline_orchestrator.py` | `context_engine/pipeline_orchestrator.py`（shim） | ✅ shim已建立 |
| TriggerRouter | `orchestrator/core/trigger_router.py` | `orchestrator/trigger_router.py`（shim） | ✅ shim已建立 |
| AgentOrchestrator | `orchestrator/core/agent_orchestrator.py` | `orchestrator/agent_orchestrator.py`（shim） | ✅ shim已建立 |
| AgentHealthMonitor | `orchestrator/state/agent_health_monitor.py` | `orchestrator/agent_health_monitor.py`（shim） | ✅ shim已建立 |
| RollbackManager | `orchestrator/resilience/rollback_manager.py` | `orchestrator/rollback_manager.py`（shim） | ✅ shim已建立 |
| FailureMatcher | `orchestrator/resilience/failure_matcher.py` | `orchestrator/failure_matcher.py`（shim） | ✅ shim已建立 |
| HallucinationDetector | `orchestrator/resilience/hallucination_detector.py` | `orchestrator/hallucination_detector.py`（shim） | ✅ shim已建立 |
| SessionManager | `orchestrator/state/session_manager.py` | `orchestrator/session_manager.py`（shim） | ✅ shim已建立 |
| StateSynchronizer | `orchestrator/state/state_synchronizer.py` | `orchestrator/state_synchronizer.py`（shim） | ✅ shim已建立 |
| FileTaskMapper | `orchestrator/state/file_task_mapper.py` | `orchestrator/file_task_mapper.py`（shim） | ✅ shim已建立 |
| Context | `shared/utils/context.py` | `shared/context.py`（shim） | ✅ shim已建立 |
| BlueprintCodeSync | `core/sync/blueprint_code_sync.py` | `core/blueprint_code_sync.py`（shim） | ✅ shim已建立 |
| SessionContinuity | `core/session/session_continuity.py` | `core/session_continuity.py`（shim） | ✅ shim已建立 |
| DocCompressor | `context_engine/support/doc_compressor.py` | `context_engine/doc_compressor.py`（shim） | ✅ shim已建立 |
| PromptRegistry | `context_engine/support/prompt_registry.py` | `context_engine/prompt_registry.py`（shim） | ✅ shim已建立 |
| IntentKeywordMapper | `context_engine/parsing/intent_keyword_mapper.py` | `context_engine/intent_keyword_mapper.py`（shim） | ✅ shim已建立 |
| IntentParser | `context_engine/parsing/intent_parser.py` | `context_engine/intent_parser.py`（shim） | ✅ shim已建立 |
| CheckType | `gates/check_types/ct_*.py` + `check_type_registry.py` | gate_engine.py 内 if/elif 链 | ✅ 已注册表化 |
| AssetInventory | `asset_inventory/`（15文件） | 原22文件 | ✅ 已合并 |

---

## §6 拆分后组件映射

> 以下记录了 GOV-FSTR-001 大文件拆分后的组件映射。

### PipelineOrchestrator 拆分（2541行→7组件）

| 组件 | 路径 |
|------|------|
| PipelineOrchestrator | `pipeline/pipeline_orchestrator.py` |
| ModelRouter | `pipeline/model_router.py` |
| CircuitBreakerManager | `pipeline/circuit_breaker_manager.py` |
| CostTracker | `pipeline/cost_tracker.py` |
| DeadLetterQueue | `pipeline/dead_letter_queue.py` |
| PreemptionManager | `pipeline/preemption_manager.py` |
| PipelineLock | `pipeline/pipeline_lock.py` |

### DriftEngine 拆分（2134行→5组件）

| 组件 | 路径 |
|------|------|
| DriftEngine | `drift_detector/drift_engine.py` |
| DriftInfrastructure | `drift_detector/drift_infrastructure.py` |
| AIConstructionDetectors | `drift_detector/ai_construction_detectors.py` |
| DriftResultTypes | `drift_detector/drift_result_types.py` |
| DriftTraining | `drift_detector/drift_training.py` |

---

## 治理信息

| 字段 | 值 |
|------|-----|
| SSoT | 本文件是代码重组安全策略的唯一权威来源 |
| 消费者 | gate_engine (CheckType: restructuring_safety)、task-card-standard、drift_detector、construction_verifier |
| 修改条件 | 需 Owner + 架构师双签；任何铁律变更必须附案例说明 |
| 来源 | 提取自 GOV-FSTR-001 重组蓝图 §4.1b / §4.1c / §11.0b / §3.5 / §3.4 |
