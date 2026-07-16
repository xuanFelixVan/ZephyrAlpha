---
module_id: MOD-INF-021
submodule_path: src/zephyr/infrastructure/rollback
title: "Rollback System 蓝图 — Git-native回滚+自动触发+运维治理持续性"
doc_type: blueprint
status: Active
version: 9.0.0
layer: L0_infrastructure
layer_name: infrastructure
functional_domain: execution
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: human_plus_agent
valid_from: "2026-05-05"
date: "2026-05-05"
ttl: permanent
construction_progress: completed
actual_disk_path: "src/zephyr/infrastructure/rollback/"
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 7
rule_form: structural
scope: global
stability: stable
verifiability: hybrid
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-14"
priority: P1
runtime_plane: hot
tags:
  - rollback
  - undo
  - checkpoint
  - recovery
  - git-native
  - sqlite-dump
  - infrastructure
  - blind-spots
  - durable-execution
  - chaos-engineering
  - resilience
  - forensic-trust
  - meta-cognitive
  - operational-governance
  - agent-sandbox
  - adversarial-ai
  - ai-safety
depends_on:
  - target: MOD-INF-020
    at: "§2"
    why: "Audit Trail——回滚操作写入审计日志"
  - target: MOD-INF-018
    at: "§2.2"
    why: "Agent RBAC——auto_guard 后验失败触发自动回滚"
  - target: MOD-GATE_ENGINE
    at: "§2.3"
    why: "Gate Engine——回滚后跑 G0 门禁验证"
  - target: MOD-MASTER_BLUEPRINT
    at: "§4"
    why: "CT-RBK-GATE-001 集成契约"
references:
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "REQUIRED_SECTIONS"
    why: "蓝图模板 v3.5/v3.6 合规基准"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "§4"
    why: "蓝图规格化铁律"
summary: >
  Git-native+SQLite dump双轨回滚+auto_guard后验自动触发+四级回滚操作+130盲点覆盖+8层防御架构+容量升级至1500模块。62代码文件，completed。v7.0.0模板v3.5/v3.6升级。
responsibility_domain: 
design_maturity: design
build_status: planned
---

> module_id: MOD-INF-021 | version: 9.0.0 | status: Active | layer: L01_infrastructure
> actual_disk_path: src/zephyr/infrastructure/rollback/ (61 .py files) | generation: 9 | construction_progress: completed

# Rollback System 蓝图 — Git-native回滚+自动触发+运维治理持续性

> **真源声明**：本蓝图是 ZephyrAlpha 回滚/撤销体系的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 回滚/撤销系统——它解决了 AI 自主操作下的安全恢复问题。核心职责包括：git-native+SQLite dump 双轨 checkpoint、auto_guard 后验失败自动触发回滚、四级回滚操作（full_revert/partial_revert/discard/hard_reset）、失败信号三分类（hard/soft/transient）、8 层防御架构（从对抗性安全到取证审计）、130 项盲点覆盖。当前规模 62 个代码文件（completed），目标容量 1,500 模块/100 AI 并发。上游依赖 MOD-INF-020（Audit Trail）/MOD-INF-018（Agent RBAC）/MOD-GATE_ENGINE（Gate Engine），下游被 MOD-MASTER_BLUEPRINT（全局状态传播链）消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-INF-021`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-021`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | rollback_executor.py | §3.1 | 四级回滚操作封装 + preflight + preview | 已实现 | |
| 2 | rollback_verifier.py | §3.1 | G0 门禁 + __pycache__ 清理 + DB 一致性 | 已实现 | |
| 3 | auto_rollback_trigger.py | §3.1 | 监听 auto_guard + 失败信号三分类 | 已实现 | |
| 4 | rollback_state_machine.py | §3.1 | 步骤级状态追踪 + 部分失败恢复 | 已实现 | |
| 5 | forward_fix_runner.py | §3.1 | Forward-Fix 替代路径 | 已实现 | |
| 6 | rollback_simulator.py | §3.1 | 临时 worktree 模拟回滚 | 已实现 | |
| 7 | rollback_drill.py | §3.1 | 每周 DiRT 演练 | 已实现 | |
| 8 | rollback_loop_detector.py | §3.1 | 循环检测 >3 次/h | 已实现 | |
| 9 | agent_cooldown.py | §3.1 | 回滚后 5min 隔离 | 已实现 | |
| 10 | rollback_lock.py | §3.1 | 全局锁 + 队列管理 | 已实现 | |
| 11 | kill_switch.py | §3.1 | 三级 Kill Switch | 已实现 | |
| 12 | sqlite_dumper.py | §3.1 | SQLite dump/restore + Merkle 签名 | 已实现 | |
| 13 | rollback_dashboard.py | §3.1 | Markdown 零依赖仪表盘 | 已实现 | |
| 14 | rollback_context_restorer.py | §3.1 | AI 会话恢复 prompt | 已实现 | |
| 15 | rollback_budget.py | §3.1 | 并发限制/日配额 | 已实现 | |
| 16 | checkpoint_gc.py | §3.1 | 快照保留策略 + 定期清理 | 已实现 | |
| 17 | rollback_bootstrap.py | §3.1 | 零依赖最小化回滚 | 已实现 | |
| 18 | hallucination_guard.py | §3.1 | 回滚后 state_verification_round | 已实现 | |
| 19 | semantic_similar_detector.py | §3.1 | AST 语义特征比较 | 已实现 | |
| 20 | vulnerability_rescanner.py | §3.1 | 回滚后 vulnerability_rescan | 已实现 | |
| 21 | warm_standby.py | §3.1 | parallel git worktree | 已实现 | |
| 22 | semantic_rollback_tag.py | §3.1 | TASK 边界 tag | 已实现 | |
| 23 | topology_change_log.py | §3.1 | reflog 分支恢复 | 已实现 | |
| 24 | git_infra_snapshot.py | §3.1 | inotify hooks/config 监控 | 已实现 | |
| 25 | secret_rotation_aware.py | §3.1 | stale_secret_scan | 已实现 | |
| 26 | cross_platform_shell.py | §3.1 | 双份 .sh + .ps1 | 已实现 | |
| 27 | venv_sync.py | §3.1 | 回滚后依赖同步 | 已实现 | |
| 28 | env_watcher.py | §3.1 | 环境变量定时扫描 | 已实现 | |
| 29 | temporal_context_adapter.py | §3.1 | 时间上下文修复 | 已实现 | |
| 30 | s3_snapshot_lifecycle.py | §3.1 | S3 快照防过期 | 已实现 | |
| 31 | external_merkle_proof.py | §3.1 | 外部可验证证明 | 已实现 | |
| 32 | submodule_sync.py | §3.1 | Submodule 同步回滚 | 已实现 | |
| 33 | forensic.py | §3.1 | 取证副本隔离 | 已实现 | |
| 34 | continuous_trust.py | §3.1 | 持续完整性证明链 | 已实现 | |
| 35 | contract.py | §3.1 | rollback_policy_engine | 已实现 | |
| 36 | contracts.py | §3.1 | CT-RBK-GATE-001 契约 | 已实现 | |
| 37 | right_to_be_forgotten.py | §3.1 | GDPR 遗忘权检查 | 已实现 | |
| 38 | llm_impact_analyzer.py | §3.1 | LLM 版本兼容性 | 已迁移 | ARCH-039 P1→governance/architecture_governance |
| 39 | model_drift_detector.py | §3.1 | AI 输出质量漂移检测 | 已迁移 | ARCH-039 P1→intelligence（删除冗余副本） |
| 40 | owner_absent.py | §3.1 | Owner 心跳+死手开关 | 已迁移 | ARCH-039 P1→governance/escalation |
| 41 | complexity_budget.py | §3.1 | 系统自复杂度分析 | 已实现 | |
| 42 | confidence_quantifier.py | §3.1 | AI 置信度量化 | 已迁移 | ARCH-039 P1→governance/intelligence_governance |
| 43 | commit_quality_gate.py | §3.1 | commit message 质量审计 | 已实现 | |
| 44 | rollback_audit_nexus.py | §3.1 | 审计 Sidecar | 已实现 | |
| 45 | rollback_wal.py | §3.1 | 回滚预写日志 | 已实现 | |
| 46 | knowngoodstate_ledger.py | §3.1 | 已验证状态收据 | 已实现 | |
| 47 | runbook_generator.py | §3.1 | SRE Runbook 自动生成 | 已实现 | |
| 48 | rollback_target_staleness.py | §3.1 | 回滚目标陈旧度评估 | 已实现 | |
| 49 | credential_rotation_trigger.py | §3.1 | 凭据自动轮替 | 已实现 | |
| 50 | cross_agent_conflict_detector.py | §3.1 | 多 Agent 文件冲突检测 | 已迁移 | ARCH-039 P1→governance/intelligence_governance |
| 51 | intent_archiver.py | §3.1 | 操作意图存档 | 已实现 | |
| 52 | rollback_abuse_detector.py | §3.1 | 回滚武器化滥用检测 | 已实现 | |
| 53 | sandbox_enforcer.py | §3.1 | 沙盒基础设施集成 | 已迁移 | ARCH-039 P1→infrastructure/runtime |
| 54 | autonomy_dashboard.py | §3.1 | 自治级别仪表盘 | 已迁移 | ARCH-039 P1→governance/intelligence_governance |
| 55 | budget_tracker.py | §3.1 | Token/Cost/Time 预算追踪 | 已实现 | |
| 56 | drift_fix.py | §3.1 | 漂移修复执行器 | 已实现 | |
| 57 | result_types.py | §3.1 | 回滚结果类型定义 | 已实现 | |
| 58 | auditor.py | §3.2 | 回滚审计事件处理 | 已实现 | |
| 59 | rollback_integration.py | §3.2 | 回滚集成协调 | 已实现 | |
| 60 | _manifest_.py | — | 模块清单 | 已实现 | |
| 61 | __init__.py | — | 包初始化 | 已实现 | |

> **ARCH-039 P1 迁移注**（2026-07-04）：以下 19 个非回滚文件已迁移到正确功能域，不再属于 MOD-INF-021：
> - 删除 9 个真副本（目标域已有 SSoT）：paper_live_transition, post_live_verification, startup_shutdown, startup_shutdown_cli, fault_tolerance, fsm_verifier, phase_manager, phase_check_registry, model_drift_detector
> - 移动 10 个文件到正确域：llm_impact_analyzer→governance/architecture_governance, autonomy_dashboard→governance/intelligence_governance, confidence_quantifier→governance/intelligence_governance, continuous_trust→governance/intelligence_governance, cross_agent_conflict_detector→governance/intelligence_governance, owner_absent→governance/escalation, trading_kill_switch→trading/trading_contracts/risk, concurrency_guard→infrastructure/runtime, gate_coordinator→infrastructure/runtime, sandbox_enforcer→infrastructure/runtime
> - 保留 kill_switch.py（KillSwitchManager 是回滚专属，消费者全在 rollback/ 内）
> - rollback/ 从 73→54 文件，符合 T_hard=60

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` 逐文件核对 | ☐ |
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| construction_progress = scaffold → __init__.py 存在且非空 | `cat __init__.py` | ☐ |
| construction_progress = design_only → 代码目录不存在或为空 | `ls D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\*.py` | ☐ |
| actual_disk_path = src/zephyr/infrastructure/rollback/ 与 §11 一致 | 交叉比对 | ☐ |
| 代码文件 [BLUEPRINT] 字段指向 MOD-INF-021 | `grep "\[BLUEPRINT\]" D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\*.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.10.0 (基线) | 61 .py 文件全部实现 | — | — |
| v0.11.0 (容量升级设计) | 设计完成，代码待施工 | ShardedRollbackLock/SQLite sharding/AdaptiveThrottle 等 25 个新文件 | 容量升级 Phase 待施工 |
| v6.0.0 (规格化升级) | 61 .py 文件全部实现 | 容量升级组件同 v0.11.0 | 容量升级 Phase 待施工 |
| v7.0.0 (模板v3.5/v3.6升级) | 61 .py 文件全部实现 | 容量升级组件同 v0.11.0 | 容量升级 Phase 待施工 |

### §0.4 SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 回滚系统架构设计 | **本文档 §1-§10** | 旧版 rollback_manager.py 注释 |
| 回滚施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 盲点对照表 | **本文档 §3 蓝图特有** | 分散在各诊断文档中的盲点记录 |
| 容量升级方案 | **本文档 §17** | v0.11.0 独立升级文档 |
| 回滚触发链路 | **本文档 §10.4** | behavioral-auditor/rollback_bridge.py（消费端） |
| 回滚结果类型 | **RollbackResult in rollback_executor.py** | governance/rollback/result_types.py（影子实现，待清理） |

### §0.5 代码目录唯一性

| 声明 | 值 |
|------|-----|
| 唯一实现目录 | `src/zephyr/infrastructure/rollback/`（61 .py 文件）|
| CLI 入口 | `scripts/rollback.py`（thin wrapper，调用 RollbackExecutor）|
| MCP 入口 | `src/zephyr/integration/mcp/governance_server.py:_execute_rollback()`（调用 RollbackExecutor）|
| 已降级遗留 | `src/zephyr/orchestration/runtime_core/orchestrator/rollback_manager.py`（仅调试场景手动 DB 快照）|
| 影子实现（待清理）| `src/zephyr/governance/rollback/`（同名类不同实现）、`src/zephyr/orchestration/runtime_core/orchestrator/resilience/rollback_manager.py`（旧设计）|
| 领域特定回滚 | 各模块内部 undo/revert 语义（Schema 回退/事务回滚/目标回退）——非本蓝图职责 |

---

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-021`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-021` 的 189 个 file 节点 | design | `extract_depgraph.py --modules MOD-INF-021` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-021 | MOD-INF-021 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 189 文件 | 61 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

### 1.1 背景

回滚系统是 ZephyrAlpha 的安全网——auto_guard 后验失败时自动 `git revert`，回滚后跑 G0 门禁确认安全。零人工介入。

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-021 |
| 代码落位 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` |
| 运行时平面 | Hot memory（回滚操作 < 1s） |
| 核心职责 | auto_guard 后验失败时自动回滚到上一个 git commit |

| # | 痛点 | 后果 |
|---|------|------|
| 1 | rollback_manager.py 存在但无完整策略 | 只有骨架，没有自动触发/验证链路 |
| 2 | 没有 checkpoint 机制 | 不知道该回滚到哪个状态 |
| 3 | 回滚后不验证 | 回滚可能引入新问题 |
| 4 | 回滚需要人工触发 | Owner 不在场时问题持续 |

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 自动回滚 | auto_guard 后验失败 → 自动 git revert + SQLite restore，零人工 |
| 2 | 双轨一致性 | 文件层 git + 数据层 SQLite dump 双轨 checkpoint，回滚后 G0 验证通过 |
| 3 | 失败信号分类 | hard/soft/transient 三分类，不同策略不同响应 |
| 4 | 循环防护 | 同一 (task, gate) >3 次/h → 暂停 + 升级 |
| 5 | 取证可验证 | 回滚操作独立审计 + Merkle 签名 + 外部时间证明 |
| 6 | 容量升级 | 1,500 模块/100 AI 并发下回滚系统不崩溃 |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 跨项目回滚 | 本项目仅管理 ZephyrAlpha 仓库 |
| 2 | 数据库 Schema 迁移回滚 | 已退役（down_migration_generator 已删除，ARCH-039 P0-1） |
| 3 | 分布式一致性回滚 | 单仓库架构，无需分布式事务 |
| 4 | auto_guard 前验逻辑 | → zephyr.agent_rbac |
| 5 | 漂移检测 | → zephyr.behavioral_auditor |
| 6 | 升级决策 | → zephyr.escalation_engine |
| 7 | 任务生命周期 | → zephyr.task_system |
| 8 | 门禁评估 | → zephyr.gate_engine |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 单机部署 | 无分布式协调需求，SQLite WAL 足够 |
| 1人+AI 运维 | 回滚必须自动触发，不能等 Owner 确认 |
| 10+ 并发对话 | 回滚不能阻塞其他对话——每个对话独立回滚 |
| 先干后验模式 | 回滚是 auto_guard 后验失败的自动补救 |
| 多 IDE 并发 | 回滚基于 git——git 是跨 IDE 统一的状态管理 |
| i7-12700KF(12C/20T) / 64GB RAM / 1TB NVMe / RTX 3090 | 硬件资源感知调度 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 双轨 Checkpoint | git commit（文件层）+ SQLite dump JSONL（数据层）|
| 2 | 自动回滚触发 | auto_guard 后验失败 → 失败信号分类 → 对应回滚策略 |
| 3 | 四级回滚操作 | full_revert / partial_revert / discard / hard_reset |
| 4 | 回滚后验证 | G0 门禁 + __pycache__ 清理 + DB 一致性修复 |
| 5 | 循环/风暴防护 | Loop Detector + Agent Cooldown + 回滚预算 |
| 6 | 8 层防御架构 | 对抗性安全→运维治理→取证审计→弹性→自愈→元认知→安全→基础 |
| 7 | 容量升级 | 模块分片锁/SQLite sharding/差异快照/内建调度器 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | auto_guard 前验逻辑 | MOD-INF-018（Agent RBAC）|
| 2 | 漂移检测 | MOD-INF-020（Audit Trail）|
| 3 | 升级决策 | MOD-INF-022（Escalation Engine）|
| 4 | 任务生命周期 | zephyr.task_system |
| 5 | 门禁评估 | MOD-GATE_ENGINE（Gate Engine）|

### 2.3 与已有代码的关系

`rollback_manager.py`（207行）的 checkpoint()/rollback_to()/list_checkpoints() 保留但**降级为仅调试场景手动 DB 快照**，不再作为自动回滚路径。新 rollback 操作统一由 `rollback_executor.py` 执行，覆盖文件+DB 双轨。版本增量：v0.5.0 +`rollback_state_machine.py`+`forward_fix_runner.py`；v0.6.0 +`rollback_bootstrap.py`+`hallucination_guard.py`+`warm_standby.py`；v0.7.0 +`prompt_injection_filter.py`+`rollback_policy_engine.py`；v0.8.0 +`audit_sidecar_daemon.py`+`git_integrity_checker.py`+`ntp_attestation.py`+`rollback_forensic_snapshot.py`+`continuous_proof_chain.py`+`toctou_double_check.py`；v0.9.0 +`operator_heartbeat.py`+`tiered_autonomy_governor.py`+`feature_flag_registry.py`+`model_version_contract.py`+`agent_confidence_scorer.py`+`error_budget_autonomy_gate.py`+`rollback_complexity_analyzer.py`+`commit_quality_auditor.py`+`fail_mode_policy.py`+`context_window_gc.py`；v0.10.0 +`agent_sandbox_bridge.py`+`rollback_system_self_defense.py`+`runbook_generator.py`+`knowngoodstate_ledger.py`+`rollback_target_staleness.py`+`credential_rotation_trigger.py`+`rollback_wal.py`+`cross_agent_conflict_detector.py`+`intent_archiver.py`+`rollback_abuse_detector.py`。

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 状态 |
|---|------|------|------|:---:|
| 1 | RollbackExecutor | 四级回滚操作封装 + preflight + preview + 锁管理 | RollbackStateMachine | ✅ |
| 2 | RollbackVerifier | G0 门禁 + __pycache__ 清理 + DB 一致性 + differential check | — | ✅ |
| 3 | AutoRollbackTrigger | 监听 auto_guard + 失败信号三分类 | RollbackExecutor | ✅ |
| 4 | RollbackStateMachine | 步骤级状态追踪 + 部分失败恢复 + in_flight 管理 | — | ✅ |
| 5 | ForwardFixRunner | 回滚替代路径：优先 FIX commit 而非 revert | RollbackExecutor | ✅ |
| 6 | SqliteDumper | SQLite dump/restore + Merkle 签名 + HMAC | — | ✅ |
| 7 | RollbackLock | 全局锁 + 队列管理 + 优先级排序 | — | ✅ |
| 8 | KillSwitch | 三级 Kill Switch（L1 Session/L2 Skill/L3 Global）| — | ✅ |
| 9 | RollbackLoopDetector | 同一 (task, gate) >3 次/h → 暂停 | — | ✅ |
| 10 | AgentCooldown | 回滚后 5min 禁止修改被回滚文件 | — | ✅ |
| 11 | RollbackBudget | 并发限制/日配额/预算耗尽切换 forward-fix | — | ✅ |
| 12 | RollbackBootstrap | 零依赖最小化回滚 + chmod 444 只读锁定 | — | ✅ |
| 13 | HallucinationGuard | 回滚后强制 state_verification_round | — | ✅ |
| 14 | SemanticSimilarDetector | AST 语义特征比较 + L2 Skill Kill 升级 | — | ✅ |
| 15 | VulnerabilityRescanner | 回滚后 vulnerability_rescan | — | ✅ |
| 16 | RollbackDrill | 每周 DiRT 演练 + 混沌场景注入 | — | ✅ |
| 17 | RollbackSimulator | 临时 git worktree 模拟回滚 | — | ✅ |
| 18 | RollbackDashboard | Markdown 零依赖仪表盘 + IM 推送 | — | ✅ |
| 19 | RollbackContextRestorer | 回滚后注入 AI 会话恢复 prompt | — | ✅ |
| 20 | DownMigrationGenerator | pre-commit hook 自动生成反向脚本 | — | ✅ |
| 21 | CheckpointGC | 快照保留策略 + 定期清理 | — | ✅ |
| 22 | WarmStandby | parallel git worktree + <100ms RTO | — | ✅ |
| 23 | SemanticRollbackTag | TASK 边界 tag + before-refactor/after-migration 标签 | — | ✅ |
| 24 | TopologyChangeLog | reflog 分支恢复 | — | ✅ |
| 25 | GitInfraSnapshot | inotify hooks/config 监控 | — | ✅ |
| 26 | SecretRotationAware | rollback preview stale_secret_scan | — | ✅ |
| 27 | CrossPlatformShell | down-migration 双份 .sh + .ps1 | — | ✅ |
| 28 | VenvSync | 回滚后 pip install --upgrade + poetry/pipenv sync | — | ✅ |
| 29 | EnvWatcher | .zephyr/last_env_reload 哨兵 + env_watcher 定时扫描 | — | ✅ |
| 30 | TemporalContextAdapter | TEMPORAL_INCONSISTENCY_REPORT | — | ✅ |
| 31 | S3SnapshotLifecycle | timestamp 前缀 + lifecycle 排除 | — | ✅ |
| 32 | ExternalMerkleProof | Merkle Proof + IPFS/Arweave + S3 Object Lock | — | ✅ |
| 33 | SubmoduleSync | git submodule update --init --recursive | — | ✅ |
| 34 | Forensic | 取证副本隔离 + 只读 snapshot | — | ✅ |
| 35 | ContinuousTrust | 日级 Hash Tree Root + S3 Object Lock | — | ✅ |
| 36 | Contract | rollback_policy_engine YAML 声明式策略 | — | ✅ |
| 37 | Contracts | CT-RBK-GATE-001 集成契约 | — | ✅ |
| 38 | RightToBeForgotten | right_to_be_forgotten_registry + preflight 拦截 | — | ✅ |
| 39 | LlmImpactAnalyzer | model_version_contract + regression test suite | — | ✅ |
| 40 | ModelDriftDetector | drift-detector 每日对比 AI 输出质量 | — | ✅ |
| 41 | OwnerAbsent | operator_heartbeat + 死手开关 + tiered_autonomy | — | ✅ |
| 42 | ComplexityBudget | 回滚系统自复杂度分析 + 复杂度预算 | — | ✅ |
| 43 | ConfidenceQuantifier | AI 置信度量化 + 低置信度降级 | — | ✅ |
| 44 | CommitQualityGate | commit message 最低标准审计 | — | ✅ |
| 45 | RollbackAuditNexus | 审计 Sidecar 独立 PID/OS user | — | ✅ |
| 46 | RollbackWAL | 回滚预写日志——操作意图耐久化 | — | ✅ |
| 47 | KnowngoodstateLedger | 已验证正确状态收据账本 | — | ✅ |
| 48 | RunbookGenerator | 回滚后自动生成 SRE Runbook | — | ✅ |
| 49 | RollbackTargetStaleness | 回滚目标陈旧度风险评估 | — | ✅ |
| 50 | CredentialRotationTrigger | 回滚后凭据自动轮替 | — | ✅ |
| 51 | CrossAgentConflictDetector | 多 Agent 文件冲突检测 | — | ✅ |
| 52 | IntentArchiver | 原始操作意图存档器 | — | ✅ |
| 53 | RollbackAbuseDetector | 回滚系统武器化滥用检测 | — | ✅ |
| 54 | SandboxEnforcer | 沙盒基础设施集成桥接 | — | ✅ |
| 55 | AutonomyDashboard | 自治级别仪表盘 | — | ✅ |
| 56 | BudgetTracker | Token/Cost/Time 三维预算追踪 | — | ✅ |
| 57 | DriftFix | 漂移修复执行器 | — | ✅ |
| 58 | ResultTypes | 回滚结果类型定义 | — | ✅ |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | auto_guard 失败信号 | AutoRollbackTrigger → 分类 → RollbackExecutor → git revert + SQLite restore | 回滚后文件状态 | RollbackResult |
| 2 | git commit 事件 | SqliteDumper → JSONL dump → knowngoodstate_ledger | Checkpoint 存储 | JSONL + SHA |
| 3 | 回滚完成事件 | RollbackVerifier → G0 门禁 → 验证报告 | 验证结果 | 验证报告 dict |
| 4 | 回滚事件 | Auditor → RollbackAuditNexus → AiAuditLogger | 审计日志 | AiAuditLogger 条目 |
| 5 | 回滚后事件 | RollbackContextRestorer → AI 会话恢复 prompt | AI 对话上下文 | ContextRestorationPrompt |
| 6 | 回滚后通知 | RollbackDashboard → Markdown 仪表盘 + IM 推送 | Owner | Markdown |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| idle | create_checkpoint | checkpointing | 无正在执行的回滚 |
| checkpointing | checkpoint 完成 | idle | dump 成功 |
| idle | execute_rollback | executing | checkpoint 存在且有效 |
| executing | 执行完成 | verifying | git revert + SQLite restore 成功 |
| verifying | 验证通过 | completed | G0 门禁通过 |
| verifying | 验证失败 | failed | G0 门禁未通过 |
| executing | 执行异常 | failed | 异常捕获 |
| completed | — | idle | 自动复位 |
| failed | — | idle | 人工确认后复位 |

### 蓝图特有：双轨 Checkpoint 策略

> 来源：规格化内容价值映射——蓝图特有
> 仅本蓝图需要：git-native + SQLite dump 双轨是本蓝图核心设计决策
> 不可砍理由：砍掉=AI施工时不知道回滚的数据模型

```yaml
checkpoint_strategy:
  mechanism:
    file_layer: "git commit = 天然 checkpoint"
    db_layer: "SQLite dump → JSONL → git track（决策 D-021-04）"
  no_extra_independent_snapshot: true
  benefit: "文件+DB 原子回滚 + 跨 IDE 统一 + 历史可追溯 + 零额外依赖"
  dump_pipeline:
    pre_commit_hook:
      - "dump_sqlite(schema + data) → data/rollback/db_snapshots/{commit_sha}.jsonl"
      - "git add data/rollback/db_snapshots/{commit_sha}.jsonl"
    on_rollback:
      - "git revert {commit_sha} → 恢复文件"
      - "从 data/rollback/db_snapshots/{target_commit_sha}.jsonl 重建 SQLite"
      - "G0 门禁验证 → 确认双轨一致性"
  rollback_methods:
    full_revert:
      command: "git revert {commit_sha}"
      use_when: "auto_guard 后验失败 (hard_failure)"
      db_recovery: "从 JSONL 重建 SQLite → G0 一致性校验"
    partial_revert:
      command: "git revert --no-commit {commit_sha} → git reset HEAD {safe_files} → git commit"
      use_when: "soft_failure 且 3 次 retry 失败"
      db_recovery: "仅修正被 revert 文件对应的 task 状态 → DB 自愈"
    discard:
      command: "git checkout -- {changed_files}"
      use_when: "pre-commit FAIL（GATE-18 拦截）"
      db_recovery: "回滚 task 状态到 pre-change 快照"
    multi_commit:
      command: "git revert {commit_sha1}..{commit_sha2}"
      use_when: "任务 G7 门禁 FAIL 且修复 3 次仍失败"
      db_recovery: "从最早 JSONL 重建 SQLite"
    hard_reset:
      command: "git reset --hard {commit_sha}"
      use_when: "熔断器 OPEN 或 Owner 手动触发"
      permission: "token-gated——60s 有效 token"
      db_recovery: "从 JSONL 全量重建 SQLite"
```

### 蓝图特有：失败信号分类

```yaml
failure_signal_classifier:
  hard_failure:
    sources: ["drift detected", "CI FAIL", "G6 secrets_detection", "circuit_breaker OPEN"]
    action: "立即回滚——full_revert"
    retry: "0 次"
  soft_failure:
    sources: ["G0 文件存在性", "G1 YAML 语法", "G2 frontmatter", "G3 encoding"]
    action: "等待 3 次 retry → 仍失败则 partial_revert"
    retry: "3 次"
  transient:
    sources: ["timeout", "network error", "SQLite locked"]
    action: "仅重试，不触发回滚"
    retry: "5 次"
```

### 蓝图特有：自动回滚流程

```yaml
auto_rollback_flow:
  step_0_evaluate: "失败评估——检查是否满足 forward-fix 条件（变更≤3文件 AND soft_failure AND 文件未锁定）"
  step_0_preflight: "安全预检——working tree/HEAD/remote/依赖影响"
  step_0b_preview: "回滚预览——受影响文件+冲突风险+依赖影响"
  step_0c_kill_escalation: "Kill 级别评估——L1 Session/L2 Skill/L3 Global"
  step_1_acquire_lock: "获取回滚锁+写入 in_flight 文件+预算检查"
  step_2_rollback: "按分类执行回滚策略——每步独立状态追踪+幂等保护"
  step_3_verify: "G0 门禁+__pycache__清理+DB一致性修复+differential check"
  step_4_audit: "写入审计日志（ProvenanceStandard + HMAC-SHA256 签名）"
  step_5_post_process: "Agent Cooldown(5min)+Loop Detector+通知+广播 MODULE_ROLLBACK_NOTIFICATION"
  step_6_notify: "异步通知 Owner + 生成 rollback_dashboard.md"
```

### 蓝图特有：8 层防御架构

| 层级 | 名称 | 核心组件 |
|------|------|---------|
| L-2 | 对抗性安全 | agent_sandbox_bridge / rollback_system_self_defense / rollback_abuse_detector / intent_archiver / credential_rotation_trigger / cross_agent_conflict_detector |
| L-3 | 运维治理 | operator_heartbeat / error_budget_autonomy_gate / model_drift_detector / confidence_quantifier / complexity_budget / commit_quality_gate |
| L-4 | 取证审计 | rollback_audit_nexus / git_integrity_checker / ntp_attestation / rollback_wal / knowngoodstate_ledger / continuous_trust / forensic |
| L-5 | 弹性基础设施 | rollback_state_machine / rollback_drill / rollback_simulator / warm_standby / checkpoint_gc / rollback_budget |
| L-6 | 自愈自主 | forward_fix_runner / rollback_context_restorer / dependency_aware_rollback |
| L-7 | 元认知 | contract(rollback_policy_engine) / right_to_be_forgotten / notification_throttle / graduated_rollback / git_bisect_protection |
| L-8 | 安全 | hallucination_guard / semantic_similar_detector / vulnerability_rescanner / prompt_injection_filter |
| L-9 | 基础 | rollback_executor / rollback_verifier / auto_rollback_trigger / rollback_lock / kill_switch / sqlite_dumper |

### 蓝图特有：盲点对照表（B1-B130）

> 来源：12 轮深挖诊断，覆盖结构性冲突/安全并发/氛围编程/OS 级事故/跨学科注入/弹性基础设施/自愈自主/元认知框架/取证审计/运维治理/对抗性 AI 安全
> 不可砍理由：砍掉=AI施工时不知道边界条件，增加幻觉风险

#### 🔴 P0 致命级（B1-B3/B43/B56-B59/B76-B78/B96-B99/B111-B114/B121-B122）

| ID | 盲点 | 问题描述 | 补充方案 |
|:--:|------|---------|---------|
| B1 | 蓝图 vs 已有代码数据模型冲突 | git-native 与 rollback_manager.py DB-state snapshot 互斥 | git-native + SQLite dump JSONL 双轨（D-021-04）|
| B2 | pre-commit FAIL 触发回滚的鸡与蛋 | pre-commit FAIL 时代码未 commit，git revert 无对象 | 区分：已 commit→revert / 未 commit→discard |
| B3 | SQLite 数据不在回滚范围 | git revert 恢复文件但 tasks 表状态未回滚 | SQLite dump JSONL + 回滚后 DB 一致性自愈 |
| B43 | 回滚中途崩溃 | OOM kill/断电导致回滚半完成 | execution_id + in_flight + 步骤级状态追踪 |
| B56 | 回滚系统自毁 | rollback_executor.py 被破坏 | rollback_bootstrap.py 零依赖 + chmod 444 |
| B57 | AI 幻觉污染 | AI 对回滚后状态产生幻觉理解 | hallucination_guard state_verification_round |
| B58 | 变形逃逸 | AI 换写法达成同样破坏 | semantic_similar_detector AST 比较 |
| B59 | 依赖漏洞复引入 | 回滚带回已知 CVE 旧版依赖 | vulnerability_rescan + 尝试升级 |
| B76 | Prompt 注入 | 恶意指令随 commit message 注入 | prompt_injection_filter 输入消毒 |
| B77 | 策略硬编码 | 回滚规则在 Python 源码中 | rollback_policy_engine YAML 声明式 |
| B78 | GDPR 违规 | 回滚恢复已被合法删除的个人数据 | right_to_be_forgotten_registry + preflight 拦截 |
| B96 | 审计系统自审计 | 回滚系统自身生成审计日志——被审计实体与审计者合一 | audit_sidecar_daemon 独立 PID/OS user |
| B97 | git 二进制中毒 | PATH 中的恶意 git 伪造回滚 | SHA-256 完整性检查 + 绝对路径缓存 |
| B98 | Shell 元字符注入 | 分支名/tag 名含 $( 等元字符 | subprocess.run(shell=False) + stdin 传 message |
| B99 | 时间线篡改 | NTP spoofing 使审计时间戳不可信 | NTP × 3 交叉验证 + >60s 偏差拒绝 |
| B111 | 人力缺席 | Owner 不可用时 AI 无法获取决策授权 | operator_heartbeat + 死手开关 + tiered_autonomy |
| B112 | 部署爆炸半径 | 缺少 feature flag，每次部署全量 | feature_flag_registry + flag_flip_undo 秒级回滚 |
| B113 | 模型能力退化 | LLM 版本静默升级导致决策质量下降 | model_version_contract + regression test |
| B114 | AI 置信度缺失 | AI 做回滚决策时无结构化置信度 | confidence_quantifier + 低置信度降级 |
| B121 | 无沙盒爆炸半径 | AI 可擦除整个磁盘/生产数据库 | agent_sandbox_bridge 强制沙盒白名单 |
| B122 | AI 主动对抗 | AI 识别并禁用回滚系统 | rollback_system_self_defense + tripwire + sha256 校验 |

#### 🟡 P1 高危级（B4-B10/B15/B42/B44-B55/B64-B67/B79-B86/B100-B110/B115-B120/B123-B129）

| ID | 盲点 | 问题描述 | 补充方案 |
|:--:|------|---------|---------|
| B4 | 无回滚前安全预检 | 直接 git revert 不检查前提 | preflight_check() |
| B5 | 无回滚预览 | 不知道回滚后哪些文件会变 | preview(commit_sha) → changed_files + conflict_risk |
| B6 | 自动回滚无限循环 | agent 重复犯错→重复回滚 | rollback_loop_detector >3 次/h → 暂停 |
| B7 | 无 Partial Rollback | 全量 revert 损失正确变更 | partial_revert(commit_sha, file_globs) |
| B8 | 回滚后 agent 未隔离 | agent 重新做同样变更 | Agent Cooldown 5min |
| B9 | 无并发序列化 | 10+ agent 同时 revert 冲突 | 全局 rollback.lock + 优先级排队 |
| B10 | 非 git-tracked 文件 | .env/secrets 不在 git 中 | preflight 备份非 tracked 文件 |
| B15 | 失败信号无分类 | 所有 FAIL 一视同仁 | hard/soft/transient 三分类 |
| B42 | 回滚状态机缺失 | 部分失败无法恢复 | rollback_state_machine 步骤级追踪 |
| B44 | AI 对话上下文断裂 | 回滚后 AI 不知道发生了什么 | rollback_context_restorer 注入恢复 prompt |
| B45 | 无 down-migration | Schema 变更无法回滚 | 已退役（down_migration_generator 已删除，ARCH-039 P0-1；Schema 变更回滚功能取消） |
| B46 | Kill Switch 缺失 | 无紧急制动 | 三级 Kill Switch L1/L2/L3 |
| B47 | 无回滚仪表盘 | Owner 不知道回滚状态 | rollback_dashboard.md 零依赖 |
| B48 | 依赖断裂 | 回滚模块 A 导致模块 B 不一致 | dependency_impact_analysis + 广播通知 |
| B49 | JSONL 快照被篡改 | 恶意修改 JSONL 快照 | Merkle 树 + HMAC-SHA256 签名 |
| B50 | Checkpoint 无 GC | 快照无限增长 | max 100 / max 90 天 + 定期清理 |
| B51 | 无 forward-fix | 所有失败都 revert | forward-fix 优先评估 |
| B52 | 回滚演练缺失 | 不知道回滚是否真的能工作 | rollback_drill 每周 DiRT |
| B53 | 回滚后 DB 差异 | 文件回滚了但 DB 状态不对 | differential check 逐行比较 |
| B54 | 按操作粒度回滚缺失 | 只能按 commit 回滚 | operation_id 级别部分撤销 |
| B55 | 回滚预算缺失 | 回滚风暴耗尽资源 | 并发≤3 + 日配额≤20 |
| B64 | Git 基础设施防护 | .git/config/hooks 被篡改 | git_infra_snapshot + inotify 监控 |
| B65 | GPG 签名链断裂 | revert commit 无签名 | preflight 检测 gpgSign → --gpg-sign |
| B66 | 密钥轮替感知 | 回滚目标含已轮替密钥 | stale_secret_scan + FIX commit 替换 |
| B67 | 跨平台 Shell | down-migration 仅 .sh | 双份 .sh + .ps1 |
| B79 | 连接池中毒 | 回滚重建 DB 后连接池持有旧 inode | db_reconnect_broadcast signal |
| B80 | 嵌套环境检测 | 容器/WSL2 中超时不同 | container/WSL2 detection + 5× 超时 |
| B81 | MCP 操作回滚 | MCP 操作不可逆 | mcp_operation_snapshot + 可逆操作 reverse |
| B82 | 确定性回滚重放 | 重复执行结果不一致 | reproducibility_seed + verify --reproduce |
| B83 | 告警疲劳 | 过量回滚通知 Owner 麻木 | notification_throttle + daily_digest |
| B84 | 渐进式回滚 | 回滚是原子操作无渐进能力 | 10%→50%→100% graduated rollback |
| B85 | git bisect 被破坏 | revert commit 使 bisect 失效 | REVERT: prefix + git bisect skip |
| B86 | File Watcher 干扰 | hot-reload 在回滚时触发无用重启 | PREPARE_FOR_ROLLBACK signal + 冷重启 |
| B100 | bit rot 腐蚀 | git 对象在磁盘静默损坏 | 每周 git fsck --full + preflight 强制 fsck |
| B101 | TOCTOU 竞态 | preflight 和 revert 间攻击窗口 | lock 后 double_check_state |
| B102 | 信任链无根 | 循环信任链无终极锚点 | TPM Attestation / SGX enclave |
| B103 | 审计日志截断 | kill -9 在 audit write 期间 | write-ahead pattern + os.rename 原子 |
| B104 | in_flight 孤儿累积 | 崩溃留下孤立文件 | in_flight_gc_daemon + >24h 自动清理 |
| B105 | SQLite WAL 被预填 | 攻击者预填 WAL 绕过 JSONL 保护 | 重建前删除 WAL/SHM + journal_mode=DELETE |
| B106 | 自动决策无问责 | auto_rollback 无人类可追责 | decision_authorizer + policy_hash |
| B107 | reflog 被清空 | git reflog expire 抹除恢复数据 | reflog 定期备份到 data/rollback/reflog_backups/ |
| B108 | git notes 攻击面 | notes 可包含可执行代码 | notes 仅允许纯文本 ASCII |
| B109 | 持续完整性缺失 | 只证明此刻正确不证明历史正确 | continuous_proof_chain 日级 Hash Tree |
| B110 | 观察者效应 | 取证检查改变系统状态 | 只读 snapshot 副本隔离取证 |
| B115 | 系统自复杂度 | 130 盲点/62 文件超 1 人可审计 | complexity_budget + 最小可行回滚 |
| B116 | 错误预算未联动 | AI 自治与系统健康不关联 | error_budget_autonomy_gate 四级降级 |
| B117 | rebase/cherry-pick 进行中 | AP2 未覆盖 rebase 中途状态 | git_operation_state_detect + 对应 abort |
| B118 | commit message 质量 | AI 写的 commit message 无法语义回滚 | commit_quality_gate 最低标准审计 |
| B119 | fail-open vs fail-closed | 回滚系统部分退化时行为未定义 | fail_mode_policy.yaml 声明式策略 |
| B120 | 上下文污染 | 多轮回滚后 AI 上下文过期 | context_window_gc + stale_context_eviction |
| B123 | 无 Runbook | 回滚后只有 JSON/log 无可执行指南 | runbook_generator 自动生成 SRE Runbook |
| B124 | 假正确 checkpoint | checkpoint 记录了坏状态 | knowngoodstate_ledger 健康验证收据 |
| B125 | 回滚目标陈旧 | 回滚到 3 个月前引入旧 bug | staleness_score + 安全补丁 cherry-pick |
| B126 | 凭据泄露不回滚 | AI 暴露 API_key 但回滚不撤销 | credential_rotation_trigger 自动轮替 |
| B127 | 回滚无 WAL | 回滚崩溃后不知道"本来想做什么" | rollback_wal 预写日志 |
| B128 | 多 Agent 文件冲突 | Agent A 回滚影响 Agent B 编辑 | cross_agent_conflict_detector + 广播 |
| B129 | 操作意图丢失 | 回滚抹去"为什么尝试" | intent_archiver 保留原始意图 |

#### 🟢 P2 基础级（B11-B14/B16-B20/B60-B63/B68-B75/B87-B95/B130）

| ID | 盲点 | 问题描述 | 补充方案 |
|:--:|------|---------|---------|
| B11 | 无回滚模拟 | 无法测试回滚本身是否正确 | rollback_simulator 临时 worktree |
| B12 | 无 MTTR 指标 | 无法评估回滚 SLA | rollback_metrics 表 + zephyr rollback stats |
| B13 | 不可逆操作保护缺失 | hard_reset 无技术 enforcement | require_token 参数类型绑定 |
| B14 | Remote 同步冲突 | revert 后本地落后 remote | preflight git pull --rebase |
| B16 | __pycache__ 缓存不一致 | 回滚后 bytecode 缓存未刷新 | G0 验证前清理 __pycache__ |
| B17 | 缺集成契约 | 蓝图无 MOD-MASTER_BLUEPRINT 契约 | CT-RBK-GATE-001 exit code 契约 |
| B18 | 施工 Phase 粗糙 | 仅 3 行描述 | 按盲点优先级重构 |
| B19 | 缺 Anti-Patterns | 无"不该触发回滚"的反面案例 | AP1-AP4 反模式 |
| B20 | 无 BREAK_GLASS | Owner 无法取消自动回滚 | cancel_pending_rollback(task_id, token) |
| B60 | Token 浪费 | 过量回滚消耗 LLM API 费用 | rollback_budget token_cost + max_daily_tokens |
| B61 | 温备热切缺失 | 回滚恢复慢 | warm_standby parallel worktree + <100ms RTO |
| B62 | 语义化 Rollback Tag | 无语义化回滚目标 | TASK 边界 tag + before-refactor 标签 |
| B63 | 分支拓扑回滚 | 分支创建/删除无法回滚 | topology_change_log + reflog 恢复 |
| B68 | venv 不同步 | 回滚后依赖不一致 | pip install --upgrade + poetry sync |
| B69 | 环境变量不重载 | .env 变更后不生效 | env_watcher 定时扫描 |
| B70 | 时间上下文断裂 | 回滚后 AI 时间线错乱 | temporal_context_adapter |
| B71 | Owner 无法覆盖目标 | 无法指定回滚到特定 commit | zephyr rollback --to {sha_or_tag} |
| B72 | 网络分区超时 | preflight git pull 卡住 | 5s timeout + PREFLIGHT_NO_REMOTE |
| B73 | S3 快照过期 | lifecycle 规则误删快照 | timestamp 前缀 + lifecycle 排除 |
| B74 | 外部可验证证明 | 第三方无法验证回滚正确性 | Merkle Proof + IPFS/Arweave |
| B75 | Submodule 分裂 | 父仓库回滚但 submodule 不同步 | git submodule update --init --recursive |
| B87 | Shallow Clone | CI 环境 shallow clone 无完整历史 | preflight shallow check + --unshallow |
| B88 | git notes 标注 | 回滚原因仅在 commit message | git notes --ref=rollback 追加 |
| B89 | 软删除 vs 硬删除 | 回滚是硬删除无法二次恢复 | data/rollback/trash/ + 7 天 GC |
| B90 | filter-branch 引用断裂 | 仓库历史被 rewrite 后 SHA 失效 | git cat-file -e preflight + reflog fallback |
| B91 | 决策疲劳 | 过多 DEFER_TO_HUMAN 耗尽 Owner | auto_defer_cooldown + 保守模式 |
| B92 | 跨 Vendor 同步 | 不同 AI 模型 checkpoint 不一致 | VENDOR_CHECKPOINT_QUERY + 最小公共祖先 |
| B93 | 回滚反馈闭环 | 回滚数据未用于改善 AI 行为 | 失败经验注入 system prompt |
| B94 | 回滚热力图 | 无回滚热点分析 | zephyr rollback stats --heatmap |
| B95 | 威胁情报 | 回滚日志中埋藏攻击模式 | rollback_threat_intel 恶意模式匹配 |
| B130 | 回滚武器化 | 攻击者触发强制回滚重新引入漏洞 | rollback_abuse_detector + 2FA 保护 |

---

## §4 接口契约

### 4.1 公共 API

```python
from pydantic import BaseModel

class RollbackExecutor:
    """回滚执行器——管理回滚生命周期"""

    def execute_rollback(self, target: "RollbackTarget") -> "RollbackResult":
        """
        执行回滚操作

        输入：target 指定回滚目标和操作类型
        输出：RollbackResult 包含执行结果和验证状态
        核心逻辑：验证 checkpoint → 执行 git revert / SQLite restore → 验证结果
        """

    def create_checkpoint(self, label: str) -> str:
        """
        创建 Checkpoint

        输入：label 检查点标签
        输出：checkpoint SHA
        核心逻辑：git commit → sqlite_dumper → knowngoodstate_ledger 注册
        """

    def verify_rollback(self, checkpoint_sha: str) -> "RollbackResult":
        """
        验证回滚结果

        输入：checkpoint_sha 待验证的检查点
        输出：RollbackResult 包含验证状态
        核心逻辑：G0 门禁验证 + DB 一致性检查
        """
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional

class RollbackOperation(str, Enum):
    FULL_REVERT = "full_revert"
    PARTIAL_REVERT = "partial_revert"
    DISCARD = "discard"
    HARD_RESET = "hard_reset"

class RollbackTarget(BaseModel):
    operation: RollbackOperation = Field(..., description="回滚操作类型")
    checkpoint_sha: str = Field(..., description="目标 checkpoint SHA")
    file_paths: list[str] = Field(default_factory=list, description="回滚文件路径列表，空=全量")
    label: Optional[str] = Field(default=None, description="检查点标签")

    @field_validator("checkpoint_sha")
    @classmethod
    def validate_sha(cls, v: str) -> str:
        if len(v) < 7:
            raise ValueError("checkpoint_sha 长度至少 7 字符")
        return v

class RollbackResult(BaseModel):
    success: bool = Field(..., description="回滚是否成功")
    operation: RollbackOperation = Field(..., description="执行的操作类型")
    checkpoint_sha: str = Field(..., description="使用的 checkpoint SHA")
    verification_passed: bool = Field(default=False, description="验证是否通过")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    files_affected: list[str] = Field(default_factory=list, description="受影响文件列表")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `execute_rollback()` | `target` | ✅ | RollbackTarget 实例，checkpoint_sha 有效 |
| `execute_rollback()` | `target.operation` | ✅ | RollbackOperation 枚举值 |
| `execute_rollback()` | `target.file_paths` | ❌ | 空列表=全量回滚 |
| `create_checkpoint()` | `label` | ✅ | 非空字符串 |
| `verify_rollback()` | `checkpoint_sha` | ✅ | 长度≥7，对应 checkpoint 存在 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `execute_rollback()` | `RollbackResult`：success=True, verification_passed=True | `RollbackResult`：success=False, error_message 非空 |
| `create_checkpoint()` | `str`：checkpoint SHA | `ROLLBACK_CHECKPOINT_FAILED` |
| `verify_rollback()` | `RollbackResult`：verification_passed=True | `RollbackResult`：verification_passed=False |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| RollbackOperation 新增操作类型 | ⚠️ 需通知 | 消费者需更新处理逻辑 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 3.12+ + Pydantic V2 | — |
| 2 | git-native 回滚为主路径 | — |
| 3 | SQLite dump 为数据层备份 | — |
| 4 | 所有回滚操作必须经过验证 | — |
| 5 | kill_switch 为 immutable_core | immutable_core |
| 6 | 回滚预算硬限制 | 并发≤3 / 日配额≤20（当前）/ 500（容量升级后）|
| 7 | rollback_bootstrap 为 immutable_core | immutable_core |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:---:|---------|
| 模块数 | 51 | 1,500 | 1,500 | ⚠️ | 模块分片锁 30 组 |
| 并发 AI Agent | ~10 | 100 | 100 | ⚠️ | AdaptiveThrottle 动态限流 |
| 日回滚配额 | 20 | 500 | 750 | ⚠️ | 配额重校准 |
| SQLite 并发写入 | 单写者 | 100 | 300 连接 | ⚠️ | 30 shard 分片 |
| Git 文件数 | ~500 | 15,000+ | 15,000+ | ⚠️ | Sparse Checkout |
| JSONL 快照/天 | ~20 | 2,000 | 2,000 | ⚠️ | 差异 dump + 分层存储 |
| Token/天 | 100K | 2M | 3M | ⚠️ | 配额重校准 |

### 5.3 迁移/废弃方案

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 | 执行状态 |
|---|-------------|---------|---------|---------|------------|:-------:|
| 1 | startup_shutdown.py | `D:\ZephyrAlpha\src\zephyr\governance\startup_shutdown.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\startup_shutdown.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 2 | startup_shutdown_cli.py | `D:\ZephyrAlpha\src\zephyr\governance\startup_shutdown_cli.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\startup_shutdown_cli.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 3 | phase_manager.py | `D:\ZephyrAlpha\src\zephyr\governance\phase_manager.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\phase_manager.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 4 | phase_check_registry.py | `D:\ZephyrAlpha\src\zephyr\governance\phase_check_registry.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\phase_check_registry.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 5 | paper_live_transition.py | `D:\ZephyrAlpha\src\zephyr\governance\paper_live_transition.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\paper_live_transition.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 6 | post_live_verification.py | `D:\ZephyrAlpha\src\zephyr\governance\post_live_verification.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\post_live_verification.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 7 | fault_tolerance.py | `D:\ZephyrAlpha\src\zephyr\governance\fault_tolerance.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\fault_tolerance.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 8 | fsm_verifier.py | `D:\ZephyrAlpha\src\zephyr\governance\fsm_verifier.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\fsm_verifier.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 已完成 |
| 9 | backtest_engine.py | `D:\ZephyrAlpha\src\zephyr\governance\backtest_engine.py` | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\backtest_engine.py` | 迁移+重导出 | 搜索全项目 import 并更新 | 不适用（文件不存在） |

### 5.4 非功能需求与服务水平

| 维度 | 指标 | 目标值 | 测量方式 |
|------|------|--------|---------|
| RTO（回滚恢复时间） | full_revert | <2s | 端到端计时 |
| RTO（温备热切） | warm_standby | <100ms | Agent 切换延迟 |
| 可用性 | 自动回滚成功率 | ≥99.5% | 月度统计 |
| 审计完整性 | HMAC 验证通过率 | 100% | 每次回滚后验证 |
| 并发安全 | 全局锁等待 | <10s | 锁超时监控 |
| 数据一致性 | DB 与 git 对齐 | 100% | 每次回滚后 G0 验证 |

### 5.7 禁止模式（Anti-Patterns）

> **时态属性**：本节属于**永久时态**——AI 施工时必读红线清单。违反 = 生产事故。

| # | 禁止行为 | 正确做法 | 盲点 |
|---|---------|---------|:---:|
| AP1 | 单行错误触发全量 revert | 先 auto-fix 3 次，仍失败则 partial_revert 仅回滚出错文件 | B51 |
| AP2 | merge conflict 期间触发回滚 | preflight 检测 conflict → 拒绝回滚，等待手动解决 | — |
| AP3 | 回滚后不施加 agent cooldown | 自动 5min cooldown + 3 次/h Loop Detector | B8 |
| AP4 | 手动 git reset --hard 绕过正式流程 | 走 RollbackExecutor.hard_reset(token)，全量审计+DB 恢复 | — |
| AP5 | 回滚后不清理 __pycache__ | G0 验证前强制 `rm -rf __pycache__` | B16 |
| AP6 | 同一 task 连续 3+ 次回滚但不升级 | ≥3 次/h → 暂停 agent + DEFER_TO_HUMAN | B6 |
| AP7 | 回滚时不备份非 tracked 文件 | preflight 备份所有 config 类非 tracked 文件 | B10 |
| AP8 | 回滚后不注入 AI 对话上下文恢复 prompt | 自动注入 context restoration prompt | B44 |
| AP9 | 回滚预算耗尽时仍强制自动回滚 | 超 budget → 拒绝 → 切换 forward-fix | B55 |
| AP10 | 跳过回滚演练直接信任模拟测试 | 每周 DiRT drill 在真实副本中演练 | B41 |
| AP11 | 对所有失败一律 revert | soft_failure + ≤3 文件 → 优先 forward-fix | B51 |
| AP12 | 回滚前不检查依赖模块影响 | preflight dependency_impact_analysis → 回滚后广播 | B48 |
| AP13 | 使用不可验证完整性的快照恢复 DB | JSONL Merkle 树 + HMAC 验证 → 不通过则拒绝 | B49 |
| AP14 | 回滚系统文件对 AI 可写 | rollback_bootstrap.py chmod 444 + .zephyr/protected/ | B56 |
| AP15 | 回滚后不验证 AI 是否真实理解状态 | 强制 state_verification_round：MD5/行数/签名验证 | B57 |
| AP16 | 回滚后忽略旧 API key 过期 | stale_secret_scan 检查 → 过期 key 自动替换 | B66 |
| AP17 | 忽略 Git submodule 版本不同步 | git submodule update --init --recursive | B75 |
| AP18 | revert commit 不加 GPG 签名 | gpgSign=true → git revert --gpg-sign | B65 |
| AP19 | 忽略 venv 与回滚后 requirements.txt 版本不匹配 | pip install -r requirements.txt --upgrade | B68 |
| AP20 | 回滚后不强制 Agent 重新加载环境变量 | .zephyr/last_env_reload 哨兵 + env_watcher 10s 扫描 | B69 |
| AP21 | git log 自由文本直接注入 AI prompt | prompt_injection_filter 消毒 + 结构化 JSON base64 | B76 |
| AP22 | 回滚策略硬编码在 Python 源码 | YAML 声明式策略引擎 + 热加载 | B77 |
| AP23 | 回滚恢复含已删除用户数据的文件 | right_to_be_forgotten_registry + preflight 拦截 | B78 |
| AP24 | 回滚后不重建数据库连接池 | db_reconnect_broadcast → 关闭旧连接 + 重新 open | B79 |
| AP25 | 逐条推送 IM 通知 | notification_throttle 合并 + daily_digest + realtime_alert | B83 |
| AP26 | 未暂停文件监听器即执行回滚 | PREPARE_FOR_ROLLBACK signal → 服务冷重启 | B86 |
| AP27 | 回滚后不分析安全威胁模式 | rollback_threat_intel.py 恶意模式匹配 | B95 |
| AP28 | 审计日志由回滚执行器自身进程写入 | audit_sidecar_daemon 独立 PID/OS user | B96 |
| AP29 | subprocess.run(["git",...]) 依赖 PATH | GIT_BIN_PATH 绝对路径缓存 + SHA-256 验证 | B97 |
| AP30 | 信任系统时钟 | NTP × 3 方验证 + >60s 偏差拒绝 | B99 |
| AP31 | 永不运行 git fsck | 每周 git fsck --full + preflight 强制过期 fsck | B100 |
| AP32 | 在活跃工作树中执行取证检查 | git clone --mirror 只读副本执行取证 | B110 |
| AP33 | DEFER_TO_HUMAN 无 Owner 缺席降级 | tiered_autonomy_governor 四级递进自治 | B111 |
| AP34 | 无 feature flag——部署即上线 | feature_flag_registry + deploy≠release | B112 |
| AP35 | 不 pin AI 模型版本 | model_version_contract 固定版本 + regression test | B113 |
| AP36 | 无条件信任 AI 回滚决策 | agent_confidence_scorer + <0.7 自动降级 | B114 |
| AP37 | 错误预算耗尽后仍允许同等自治 | error_budget_autonomy_gate 联动降级 | B116 |
| AP38 | commit message 敷衍——"fix"/"update" | commit_quality_auditor pre-commit hook 最低标准 | B118 |
| AP39 | AI 在无沙盒环境执行任意 shell | agent_sandbox_bridge 白名单限制 | B121 |
| AP40 | 核心文件 chmod 644 | chmod 440 + tripwire inotify 监控 | B122 |
| AP41 | 回滚后只 dump JSON——不给人类可读总结 | runbook_generator 生成结构化 Runbook | B123 |
| AP42 | checkpoint 不验证系统健康 | knowngoodstate_ledger 5 项健康检查全过才 verified | B124 |
| AP43 | 回滚后不检查凭据泄露 | credential_rotation_trigger 自动扫描+轮替 | B126 |
| AP44 | 回滚信号来源不验证 | 仅 trusted sources——拒绝 MCP/HTTP 匿名请求 | B130 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | git revert 冲突 | preflight 预检 | high→拒绝自动回滚→DEFER_TO_HUMAN | 回滚操作 |
| 2 | 频繁自动回滚 | Loop Detector >3 次/h | 暂停 agent 自动回滚权限 + 升级 | Agent 行为 |
| 3 | 多 IDE 并发回滚 | 全局 rollback.lock | 排队，超时 10s 返回 BUSY | 回滚操作 |
| 4 | SQLite dump 失败 | dump 异常 | 拒绝 commit + 告警 | Checkpoint 创建 |
| 5 | JSONL 与 git 不一致 | DB 一致性验证 | 从最近一致 JSONL 重建 | 数据层 |
| 6 | 回滚中途崩溃 | in_flight 文件检测 | 从最后 SUCCESS 步继续 | 回滚操作 |
| 7 | 回滚演练失败 | DiRT drill 结果 | 连续 2 次 FAIL → P0 Alert → 熔断 | 自动回滚 |
| 8 | 回滚风暴 | 预算检查 | 超 budget 切换 forward-fix | 系统资源 |
| 9 | JSONL 快照被篡改 | Merkle + HMAC 验证 | 不一致则拒绝重建 | 数据完整性 |
| 10 | 依赖断裂 | dependency_impact_analysis | 广播 MODULE_ROLLBACK_NOTIFICATION | 下游模块 |
| 11 | 回滚系统自毁 | sha256 校验 | rollback_bootstrap 零依赖恢复 | 回滚系统 |
| 12 | AI 幻觉污染 | state_verification_round | VeriTrail DAG 溯源验证 | AI 决策 |
| 13 | Prompt 注入 | prompt_injection_filter | 输入消毒 + 结构化 prompt | AI 上下文 |
| 14 | 审计日志截断 | write-ahead pattern | os.rename 原子恢复 | 审计完整性 |
| 15 | TOCTOU 竞态 | lock 后 double_check | 连续 3 次 → suspect sabotage | 回滚安全 |

### 6.1 可观测性规格

| 信号 | 采集方式 | 存储位置 | 告警阈值 |
|------|---------|---------|---------|
| 回滚执行耗时 | RollbackExecutor 计时 | rollback_metrics.db | >2s |
| 回滚频率 | Loop Detector 计数 | rollback_metrics.db | >3 次/h |
| MTTR | stats 聚合 | rollback_metrics.db | >30s |
| Token 消耗 | rollback_budget.py | rollback_metrics.db | >100K/天 |
| Agent 回滚率 | stats --agent-quality | rollback_metrics.db | >20% |
| 审计完整性 | HMAC 验证 | audit_sidecar | 任何失败 |

### 6.2 退化矩阵

| 故障模式 | 降级策略 | 降级后能力 | 恢复条件 |
|---------|---------|-----------|---------|
| SQLite 不可用 | 仅 git-native 回滚 | 文件层回滚可用，数据层无备份 | SQLite 恢复 |
| 审计 Sidecar 崩溃 | 主进程内审计写入 | 审计可用但不可自证清白 | Sidecar 重启 |
| NTP 不可用 | 信任本地时钟 | 回滚可用但时间线不可信 | NTP 恢复 |
| Merkle 验证失败 | 尝试上一个有效快照 | 可能回滚到更早状态 | 找到有效快照 |
| rollback_executor 故障 | rollback_bootstrap 零依赖回滚 | 仅 full_revert 可用 | 主执行器恢复 |
| 全局锁死锁 | 10s 超时 + BUSY 返回 | 回滚被拒绝 | 锁释放 |

CT-RBK-GATE-001 Exit Codes（46+7 容量相关）：

| Exit Code | 状态 | 含义 |
|:--:|------|------|
| 0 | SUCCESS | 回滚成功 + G0 验证通过 |
| 1 | CONFLICT | git revert 冲突 |
| 2 | PREFLIGHT_REJECTED | preflight 检查拒绝 |
| 3 | COOLDOWN_LOCKED | Agent Cooldown 中 |
| 4 | BUDGET_EXCEEDED | 回滚预算耗尽 |
| 5 | LOOP_DETECTED | 循环检测触发 |
| 6 | GC_LOCKED | git gc 正在运行，无法安全执行回滚 |
| 7 | BUDGET_EXCEEDED | 回滚预算耗尽——并发≥3 或日配额≥20 |
| 8 | INTEGRITY_FAIL | JSONL 快照完整性验证失败——Merkle/HMAC 不匹配 |
| 9 | DRILL_FAIL_CONSECUTIVE | 回滚演练连续 2 次失败 |
| 10 | BOOTSTRAP_ESCALATED | 主回滚器连续 3 次自身操作失败→升级 bootstrap |
| 11 | HALLUCINATION_DETECTED | AI 在 state_verification_round 连续 3 轮未通过 |
| 12 | MORPHING_DETECTED | 语义变形检测——新旧代码>70%相似 |
| 13 | VULN_REINTRODUCED | 回滚恢复的依赖包含已知 CVE |
| 14 | WARM_STANDBY_CUTOVER | 温备已切入——后台回滚进行中 |
| 15 | STALE_SECRET_FOUND | 回滚恢复的代码引用过期 API key |
| 16 | SUBMODULE_OUT_OF_SYNC | git submodule 版本与父仓库不一致 |
| 17 | GPG_MISSING | gpgSign=true 但无可用 GPG key |
| 18 | PROMPT_INJECTION_FILTERED | context restoration prompt 中发现疑似注入——已消毒 |
| 19 | GDPR_BLOCKED | 回滚涉及 right_to_be_forgotten_registry 中的文件 |
| 20 | CONNECTION_POOL_RECONNECTED | 回滚后数据库连接池已自动重建 |
| 21 | NESTED_ENV_DETECTED | 检测到 Docker/WSL2 嵌套环境 |
| 22 | MCP_IRREVERSIBLE | MCP 操作不可逆——已记录快照但无法自动恢复 |
| 23 | NOTIFICATION_THROTTLED | N 次回滚通知已合并为单次摘要 |
| 24 | SELF_AUDIT_CONFLICT | 回滚系统与审计方为同一实体 |
| 25 | GIT_BINARY_MISMATCH | git 二进制 SHA-256 与预期不符 |
| 26 | TIME_ATTEST_FAIL | 本地时间 vs 3 方 NTP 偏差>60s |
| 27 | BIT_ROT_DETECTED | git fsck 发现 corrupt object |
| 28 | TOCTOU_RACE | lock 后 double_check 发现 dirty working tree |
| 29 | IN_FLIGHT_ANOMALY | in_flight/ 目录>10 个孤儿文件 |
| 30 | CONTINUOUS_PROOF_BROKEN | 连续证明链 Hash Tree Root 与前一日不一致 |
| 31 | OWNER_ABSENT_L3 | Owner 心跳超时>72h——全局只读模式 |
| 32 | OWNER_ABSENT_L1 | Owner 心跳超时<24h——保守自治模式 |
| 33 | FEATURE_FLAG_UNDO | Feature flag 关闭操作成功 |
| 34 | MODEL_DRIFT_DETECTED | LLM 模型版本行为漂移超过阈值 |
| 35 | AUTONOMY_DOWNGRADED | 错误预算低于阈值——AI 自治级别自动降级 |
| 36 | REBASE_IN_PROGRESS | git rebase/cherry-pick/am 正在进行中 |
| 37 | LOW_CONFIDENCE_CONSEC | 连续 3 次 AI 决策置信度<0.7 |
| 38 | COMPLEXITY_OVER_BUDGET | 回滚系统文件数/代码行数超过简化预算上限 |
| 39 | SANDBOX_BREACH | AI 尝试越权访问沙盒白名单外路径 |
| 40 | ROLLBACK_CORE_TAMPERED | 回滚系统核心文件 sha256 与 Golden Hash 不一致 |
| 41 | CHECKPOINT_BAD_STATE | 回滚目标被 3 次验证失败——标记 bad_state |
| 42 | TARGET_STALE_OVER_30D | 回滚目标>30 天未验证——陈旧度红色 |
| 43 | CREDENTIAL_LEAK_DETECTED | 回滚后 diff 中检测到密钥出现在非白名单文件 |
| 44 | ROLLBACK_ABUSE_DETECTED | 同一文件/agent 短期内被回滚次数异常 |
| 45 | ROLLBACK_WAL_INCOMPLETE | 上次回滚操作写入 WAL 但未 committed |
| 46 | INTENT_ARCHIVE_PRUNE | 90 天前存档的意图被清理 |
| 47 | THROTTLED_CPU | CPU 使用率超阈值 |
| 48 | THROTTLED_MEMORY | 可用内存不足 |
| 49 | THROTTLED_DISK | 磁盘 IOWait 超阈值 |
| 50 | SHARD_UNAVAILABLE | 目标 shard DB 不可用 |
| 51 | INCREMENTAL_SCAN_FAILED | 增量扫描调度失败 |
| 52 | FULL_SCAN_WEEKLY_RUNNING | 全量周检进行中 |
| 53 | SNAPSHOT_TIER_MIGRATED | 快照已迁移到 cold tier |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | AI 主动禁用回滚系统 | 高 | rollback_system_self_defense + sha256 校验 + tripwire | 模拟篡改核心文件 |
| 2 | Prompt 注入回滚链路 | 高 | prompt_injection_filter + 结构化 context restoration | 注入测试 |
| 3 | 回滚武器化滥用 | 高 | rollback_abuse_detector + 速率限制 + 2FA | 频率测试 |
| 4 | git 二进制替换 | 高 | SHA-256 完整性检查 + 绝对路径缓存 | PATH 劫持测试 |
| 5 | 时间线篡改 | 高 | NTP × 3 交叉验证 + >60s 偏差拒绝 | NTP spoofing 测试 |
| 6 | 审计日志被篡改 | 高 | audit_sidecar 独立进程 + chattr +a 保护 | 日志完整性验证 |
| 7 | 凭据泄露不回滚 | 高 | credential_rotation_trigger 自动轮替 | 泄露模拟测试 |
| 8 | 沙盒绕过 | 高 | agent_sandbox_bridge 白名单 + 越权阻断 | 沙盒逃逸测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | RollbackExecutor/RollbackVerifier/AutoRollbackTrigger | full_revert/partial_revert/discard/hard_reset | 覆盖率≥80% |
| 2 | 集成测试 | 回滚全流程（触发→执行→验证→审计）| auto_guard FAIL→自动回滚→G0 通过 | 端到端通过 |
| 3 | 混沌测试 | 回滚演练（DiRT drill）| GC 并发/SQLite 锁/磁盘满载 | 每周 drill 通过 |
| 4 | 安全测试 | 对抗性场景 | AI 篡改核心文件/Prompt 注入/沙盒逃逸 | 所有攻击被阻断 |
| 5 | 取证测试 | 审计完整性 | Merkle 验证/NTP 验证/WAL 恢复 | 审计链完整 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-020 | 必须 | Audit Trail——回滚操作写入审计日志 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_governance\audit_trail\blueprint.md` |
| MOD-INF-018 | 必须 | Agent RBAC——auto_guard 后验失败触发自动回滚 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_autonomy_core\agent_role_based_access_control\blueprint.md` |
| MOD-GATE_ENGINE | 必须 | Gate Engine——回滚后跑 G0 门禁验证 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-MASTER_BLUEPRINT | 必须 | CT-RBK-GATE-001 集成契约 | — | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` |
| MOD-INF-016 | 可选 | Shared Core 承载 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| MOD-DATABASE | 必须 | Shared Core 数据脊——rollback_metrics.db/JSONL 快照路径解析 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-021` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| sqlite_dumper.py | rollback_executor.py | JSONL 快照是回滚的前置条件 | 检查 db_snapshots/ 目录 |
| rollback_executor.py | rollback_verifier.py | 回滚执行后必须验证 | 检查 RollbackResult |
| auto_rollback_trigger.py | rollback_executor.py | 触发器调用执行器 | 检查调用链 |
| rollback_executor.py | rollback_audit_nexus.py | 回滚操作写入审计 | 检查审计日志 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| auto_rollback_trigger.py | rollback_executor.py | 失败信号分类 | 函数调用 |
| sqlite_dumper.py | knowngoodstate_ledger.py | JSONL 快照+SHA | 共享文件系统 |
| rollback_executor.py | rollback_verifier.py | RollbackResult | 函数调用 |
| rollback_executor.py | rollback_audit_nexus.py | 回滚事件 | 函数调用 |
| rollback_verifier.py | rollback_dashboard.py | 验证结果 | 函数调用 |

### 10.3.1 线3 治理闭环——G-CT 契约全景

> 对齐 dependency_path_panorama.md 线3。本模块直接参与 3 条，全景 8 条提供上下文。

| G-CT ID | 契约 | 源 | 目标 | 本模块角色 |
|---------|------|---|------|-----------|
| G-CT-001 | RBAC→Audit | MOD-INF-018 | MOD-INF-020 | 间接（018→020→021）|
| G-CT-002 | Audit→Rollback | MOD-INF-020 | **MOD-INF-021** | **直接消费者** |
| G-CT-003 | Rollback→Escalation | **MOD-INF-021** | MOD-INF-022 | **直接生产者** |
| G-CT-004 | Gate→RBAC | MOD-GATE_ENGINE | MOD-INF-018 | 间接 |
| G-CT-005 | Drift→Rollback | MOD-INF-023 | **MOD-INF-021** | **直接消费者** |
| G-CT-006 | Escalation→A2A | MOD-INF-022 | MOD-INF-025 | 间接 |
| G-CT-007 | A2A→Spec | MOD-INF-025 | MOD-INF-019 | 间接 |
| G-CT-008 | Budget→Rollback | MOD-INF-024 | MOD-INF-021 | 间接（预算约束回滚频率）|

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 62 代码文件+388 治理脚本，手动维护不可靠 |
| 2 | 依赖对齐自动验证 | 是 | 有 5 个外部依赖模块，需自动验证对齐 |
| 3 | 临时时态内容自动清理 | 是 | §5.3 有 8 项已完成 + 1 项不适用（backtest_engine.py 文件不存在） |
| 4 | 施工步骤完成度自动检测 | 否 | construction_progress=completed |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |

### 10.5 概念重叠声明

> **时态属性**：本节属于**永久时态**——新 AI session 必须了解哪些外部代码与回滚系统存在概念重叠，避免重复实现或引用错误的类。

| 重叠位置 | 重叠类/函数 | 与本蓝图的关系 | 处置 |
|---------|-----------|-------------|------|
| `governance/rollback/contracts.py` | `RollbackHandler` | 同名但不同实现——governance 版是 G-CT-002 契约消费端 | 保留，但须重命名避免混淆 |
| `governance/rollback/result_types.py` | `RollbackResult`/`RollbackStatus` | 同名但字段不同——governance 版是 G-CT-003 数据结构 | 保留，但须重命名避免混淆 |
| `governance/rollback/budget_tracker.py` | `RollbackBudgetTracker` | G-CT-009 契约——回滚成本计入预算 | 保留，属于 budget-enforcer 职责 |
| `orchestrator/resilience/rollback_manager.py` | `RollbackManager` | 旧设计（KBG-0038），仅 DB 恢复无 git-native | **待迁移**——降级为 thin shim 调用 RollbackExecutor |
| `behavioral_auditor/rollback_bridge.py` | `DriftRollbackBridge` | G-CT-006 契约——漂移→回滚桥接，不执行回滚 | 保留，正确消费端 |
| `feedback_loop/verifiers/auto_rollback.py` | `AutoRollback` | 与 AutoRollbackTrigger 功能重叠 | **待清理**——应调用 AutoRollbackTrigger |
| `feedback_loop/verifiers/rollback_integrity.py` | `RollbackIntegrity` | 与 RollbackVerifier 功能重叠 | **待清理**——应调用 RollbackVerifier |
| `drift_detector/` 下 6 个文件 | `rollback_fix()`/`trigger_rollback()` 等 | 与 behavioral-auditor/ 近似重复 | **待清理**——蓝图已标注"待清理" |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_autonomy_core\rollback_system\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` | Python 源码（61 .py files）|
| 测试代码 | `D:\ZephyrAlpha\tests\rollback\` | 测试用例 |
| SQLite 快照 | `D:\ZephyrAlpha\data\rollback\db_snapshots\` | {commit_sha}.jsonl |
| Down-migration | `D:\ZephyrAlpha\data\rollback\down\` | {commit_sha}.sh/.ps1 |
| 回滚指标 | `D:\ZephyrAlpha\data\rollback\rollback_metrics.db` | MTTR/频率/成功率 |
| In-flight 记录 | `D:\ZephyrAlpha\.zephyr\rollback_in_flight\` | 幂等保护+崩溃恢复 |
| 回滚审计 | `D:\ZephyrAlpha\data\rollback\audit\` | Sidecar 独立审计日志 |
| Reflog 备份 | `D:\ZephyrAlpha\data\rollback\reflog_backups\` | reflog 定期备份 |
| Trash | `D:\ZephyrAlpha\data\rollback\trash\` | 软删除临时存储（7 天 GC）|

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-INF-020 Audit Trail | 事件写入 | AiAuditLogger | 审计日志包含回滚记录 |
| MOD-INF-018 Agent RBAC | 信号监听 | auto_guard 后验结果 | 后验失败→自动触发回滚 |
| MOD-GATE_ENGINE Gate Engine | 回调验证 | G0 门禁验证 | 回滚后 G0 通过 |
| MOD-MASTER_BLUEPRINT | 集成契约 | CT-RBK-GATE-001 | exit code 契约对齐 |
| MOD-INF-022 Escalation | 事件产出 | 回滚结果进入升级 | 回滚失败→升级触发 |

### 12.1 域契约锚点

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-002 | 消费方（Audit 异常驱动回滚）| MOD-INF-020 |
| G-CT-003 | 产出方（回滚结果进入 Escalation）| MOD-INF-022 |
| G-CT-005 | 消费方（漂移检测触发回滚）| MOD-INF-023 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-021 版本+generation | 蓝图升级 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-INF-021 版本+路径 | 蓝图升级 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | MOD-INF-021 元数据 | 蓝图升级 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 线3:治理闭环 更新 | 容量升级 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R1 | git revert 冲突 | 中 | 高 | preflight 预检冲突风险→high→DEFER_TO_HUMAN | 风险 |
| R2 | 频繁自动回滚 | 中 | 中 | Loop Detector 3 次/h→暂停+升级 | 风险 |
| R3 | 多 IDE 并发回滚 | 低 | 高 | 全局 rollback.lock + 排队 | 风险 |
| R4 | 自动回滚震荡 | 中 | 高 | Agent Cooldown 5min + Loop Detector | 风险 |
| R5 | SQLite dump 失败 | 低 | 中 | dump 失败→拒绝 commit + 告警 | 风险 |
| R6 | JSONL 与 git 不一致 | 低 | 高 | DB 一致性验证→从最近一致 JSONL 重建 | 风险 |
| R7 | partial_revert 孤儿变更 | 低 | 中 | 强制全量 G0 验证 | 风险 |
| R8 | discard 误操作 | 低 | 高 | 检查 owner_session_id→拒绝+告警 | 风险 |
| R9 | 回滚中途崩溃 | 低 | 高 | execution_id + in_flight + 步骤级恢复 | 风险 |
| R10 | 回滚演练失败 | 低 | 高 | 连续 2 次 FAIL→P0 Alert→熔断 | 风险 |
| R11 | 回滚风暴 | 低 | 中 | 预算管理：并发≤3 + 日配额≤20 | 风险 |
| R12 | JSONL 快照被篡改 | 低 | 高 | Merkle + HMAC-SHA256 签名 | 风险 |
| R13 | 依赖断裂 | 中 | 中 | dependency_impact_analysis + 广播通知 | 风险 |
| R14 | 回滚系统自毁 | 低 | 高 | rollback_bootstrap 零依赖 + chmod 444 | 风险 |
| R15 | AI 幻觉污染 | 中 | 高 | hallucination_guard + VeriTrail DAG | 风险 |
| R39 | 无沙盒爆炸半径 | 高 | 高 | agent_sandbox_bridge 强制白名单 | 风险 |
| R40 | AI 主动对抗 | 高 | 高 | rollback_system_self_defense + tripwire | 风险 |
| R45 | 分片热点 | 中 | 中 | 动态重平衡 shard_key | 风险 |
| R46 | 自适应限流失控 | 低 | 高 | min_concurrent=10 硬地板 | 风险 |
| R47 | NVMe 写入放大 | 中 | 低 | diff_dump 减少 90% 写入量 | 风险 |
| R48 | 脚本爆炸 | 低 | 中 | 脚本治理审计 + 去重合并 | 风险 |
| N1 | 62 个代码文件对 1 人维护是显著负担（B115 自复杂度） | 高 | 中 | complexity_budget + 最小可行回滚 | 负面后果 |
| N2 | 回滚系统可靠性依赖 git+SQLite+文件系统——任一层损坏都可能使回滚失效 | 中 | 高 | rollback_bootstrap 零依赖恢复 + 8 层防御 | 负面后果 |
| N3 | 130 项盲点中 P2 级（51 项）默认不实现——存在未验证盲区 | 中 | 中 | 触发真实场景时激活 + DiRT 演练覆盖 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4）| 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 10 Phase（scaffold→experimental→beta→production→resilience→sovereign→metacognitive→forensic→governance→adversarial-security）+ 3 容量升级 Phase |
| 施工模式 | 扩展 |
| 核心风险 | 回滚系统自复杂度超 1 人可审计上限 |
| 目标 generation | 9——本次从 generation 8 升级到 generation 9（责任审查+概念重叠声明+SSoT前移）|

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-020 Audit Trail 已就绪 | hard | ✅ | ✅ |
| 2 | MOD-INF-018 Agent RBAC 已就绪 | hard | ✅ | ✅ |
| 3 | MOD-GATE_ENGINE Gate Engine 已就绪 | hard | ✅ | ✅ |
| 4 | git 仓库可用 | hard | ✅ | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> **删除前置条件**（缺一不可）：
> 1. 代码文件存在且非空
> 2. `python -m pytest tests/` 对应测试 exit 0
> 3. `mypy` 类型检查通过
> 4. `ruff` lint 通过
> 5. 以上 4 项全部通过后，该步骤的详细内容可从蓝图删除，只保留"步骤 N: 已完成"

#### 步骤 1：scaffold Phase（P0 基础）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 RollbackExecutor |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` |
| 验收标准 | rollback_executor.py + rollback_verifier.py + auto_rollback_trigger.py 可 import 且无语法错误 |
| 验证命令 | `python -c "from zephyr.rollback.rollback_executor import RollbackExecutor"` |
| G7 检查项 | 上游文件全部列出？下游产出物路径精确？回滚方案可执行？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-021 | rollback_executor.py | code | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_executor.py` |
| MOD-INF-021 | rollback_verifier.py | code | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_verifier.py` |
| MOD-INF-021 | auto_rollback_trigger.py | code | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\auto_rollback_trigger.py` |
| MOD-INF-021 | sqlite_dumper.py | code | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\sqlite_dumper.py` |
| MOD-INF-021 | rollback_lock.py | code | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_lock.py` |

#### 步骤 2-8：experimental→forensic Phase

> 详见 §3.1 组件架构表——每个组件对应一个施工步骤。
> 完整 Phase 规划见下方 §16.7。

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | rollback_executor.py 语法错误 | git checkout -- src/zephyr/resilience/rollback/rollback_executor.py |
| 2 | 集成测试失败 | git revert HEAD~N（N=本步骤 commit 数）|
| 3 | 回滚系统自毁 | rollback_bootstrap.py 零依赖恢复 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | 61 .py 文件 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` | ✅ | ✅ | ✅ |
| 2 | 测试文件 | `D:\ZephyrAlpha\tests\rollback\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者 |
| verification_status | passed | 审计者 |
| code_alignment_verified | yes | 审计者 |

### 16.7 完整 Phase 规划

| Phase | # | 任务 | 盲点 | 优先级 |
|:---:|:--:|------|:--:|:---:|
| scaffold | 1.1 | 数据模型统一决议+实施——git-native+SQLite dump 双轨 | B1/B3 | P0 |
| scaffold | 1.2 | 区分 revert vs discard 两套流程 | B2 | P0 |
| scaffold | 1.3 | RollbackExecutor + preflight_check + preview | B4/B5 | P0 |
| scaffold | 1.4 | RollbackVerifier（G0 验证+__pycache__清理+DB一致性）| B16 | P1 |
| scaffold | 1.5 | AutoRollbackTrigger（失败信号三分类）| B15 | P1 |
| experimental | 2.1 | Partial Revert（file-glob 选择性回滚）| B7 | P1 |
| experimental | 2.2 | Loop Detector + Agent Cooldown | B6/B8 | P1 |
| experimental | 2.3 | 回滚队列 + Concurrency Serialization | B9 | P1 |
| experimental | 2.4 | Non-tracked 文件保护 | B10 | P1 |
| beta | 3.1 | Rollback Simulator + Test Framework | B11 | P2 |
| beta | 3.2 | Rollback Metrics + MTTR Tracking | B12 | P2 |
| beta | 3.3 | Hard Reset token gating | B13 | P2 |
| beta | 3.4 | Remote Sync 冲突处理 | B14 | P2 |
| production | 4.1 | 1人运维 CLI | — | P1 |
| production | 4.2 | BREAK_GLASS adaption | B20 | P2 |
| production | 4.3 | CT-RBK-GATE-001 集成契约落地 | B17 | P2 |
| resilience | 5.1 | 回滚幂等执行器 | B43 | P0 |
| resilience | 5.2 | 回滚状态机 | B42 | P0 |
| resilience | 5.3 | 定期回滚演练调度器 | B41/B52 | P0 |
| resilience | 5.4 | 三级 Kill Switch | B46 | P1 |
| resilience | 5.5 | Forward-Fix 优先决策 | B51 | P1 |
| resilience | 5.6 | AI 对话上下文恢复 | B44 | P1 |
| resilience | 5.7 | 依赖感知回滚 | B48 | P1 |
| resilience | 5.8 | Down-migration 脚本自动生成 | B45 | P1 |
| resilience | 5.9 | 30 秒回滚仪表盘 | B47 | P1 |
| resilience | 5.10 | JSONL 完整性保护 | B49 | P1 |
| resilience | 5.11 | Differential 验证 | B53 | P2 |
| resilience | 5.12 | Checkpoint GC 策略 | B50 | P2 |
| resilience | 5.13 | 按 AI 操作粒度回滚 | B54/B24 | P2 |
| resilience | 5.14 | 回滚预算管理 | B55 | P2 |
| sovereign | 6.1 | 自举回滚器 | B56 | P0 |
| sovereign | 6.2 | AI 幻觉防护 | B57 | P0 |
| sovereign | 6.3 | 语义变形检测 | B58 | P0 |
| sovereign | 6.4 | 依赖漏洞复扫 | B59 | P0 |
| sovereign | 6.5-6.20 | Token 会计/温备热切/语义 Tag/分支拓扑/Git 基建/GPG/密钥轮替/跨平台 Shell/venv 同步/环境变量/时间上下文/Owner 覆盖/网络分区/S3 快照/外部证明/Submodule 同步 | B60-B75 | P1-P2 |
| metacognitive | 7.1-7.20 | Prompt 注入过滤/声明式策略/GDPR/连接池/嵌套环境/MCP 操作/确定性重放/告警疲劳/渐进式回滚/git bisect/File Watcher/Shallow Clone/git notes/软删除/filter-branch/决策疲劳/跨 Vendor/反馈闭环/热力图/威胁情报 | B76-B95 | P0-P2 |
| forensic | 8.1 | 独立审计 Sidecar | B96 | P0 |
| forensic | 8.2 | git 二进制完整——SHA-256 启动检查+绝对路径缓存 | B97 | P0 |
| forensic | 8.3 | Shell 注入全量审计——subprocess.run(shell=True)→shell=False | B98 | P0 |
| forensic | 8.4 | 外部时间证明——NTP×3 方交叉验证+>60s 偏差拒绝 | B99 | P0 |
| forensic | 8.5 | git 对象 bit rot 检测——每周 git fsck --full | B100 | P0 |
| forensic | 8.6 | TOCTOU 双检——lock 后 double_check_state | B101 | P1 |
| forensic | 8.7 | 硬件信任锚 TPM——TPM Attestation Quote | B102 | P1 |
| forensic | 8.8 | 原子化审计写入——write-ahead tmp+rename | B103 | P1 |
| forensic | 8.9 | in_flight GC——24h 孤儿清理+≤5 阈值 | B104 | P1 |
| forensic | 8.10 | WAL 清除——db_rebuild 前删除 WAL/SHM | B105 | P1 |
| forensic | 8.11 | 回滚决策可问责——审计记录追加 policy_hash | B106 | P1 |
| forensic | 8.12 | reflog 备份——每次 commit 备份 reflog+Merkle 签名 | B107 | P1 |
| forensic | 8.13 | git notes 纯文本沙箱——strip 非 ASCII+禁止 eval | B108 | P2 |
| forensic | 8.14 | 持续完整证明链——日级 Hash Tree Root 签名 | B109 | P2 |
| forensic | 8.15 | 取证只读 snapshot——git clone --mirror 到隔离副本 | B110 | P2 |
| governance | 9.1 | Owner 心跳+死手开关+分级自治 | B111 | P0 |
| governance | 9.2 | Feature Flag 注册表+flag_flip_undo | B112 | P0 |
| governance | 9.3 | LLM 模型版本契约+行为漂移检测 | B113 | P0 |
| governance | 9.4 | AI 置信度量化+低置信度降级 | B114 | P0 |
| governance | 9.5 | 回滚系统自复杂度分析+简化建议 | B115 | P0 |
| governance | 9.6 | Error Budget 自治门禁 | B116 | P0 |
| governance | 9.7 | git rebase/cherry-pick/am in-progress 检测 | B117 | P1 |
| governance | 9.8 | Commit Message 质量审计+最低标准 | B118 | P1 |
| governance | 9.9 | fail-open/fail-closed 声明式策略 | B119 | P1 |
| governance | 9.10 | 上下文窗口累积污染+GC | B120 | P1 |
| adversarial-security | 10.1 | Agent 执行沙盒集成（Docker/Bubblewrap/E2B）| B121 | P0 |
| adversarial-security | 10.2 | 回滚系统自防卫+核心文件完整性强制校验 | B122 | P0 |
| adversarial-security | 10.3 | 回滚后 Runbook 自动生成 | B123 | P0 |
| adversarial-security | 10.4 | knowngoodstate 已验证正确状态收据账本 | B124 | P0 |
| adversarial-security | 10.5 | 回滚目标陈旧度风险评估 | B125 | P1 |
| adversarial-security | 10.6 | 回滚后凭据泄露检测+自动轮替 | B126 | P1 |
| adversarial-security | 10.7 | 回滚预写日志（Rollback WAL）| B127 | P1 |
| adversarial-security | 10.8 | 多 Agent 文件冲突检测+广播 | B128 | P1 |
| adversarial-security | 10.9 | 操作意图存档（Intent Archiver）| B129 | P1 |
| adversarial-security | 10.10 | 回滚系统武器化滥用检测 | B130 | P2 |

### 16.8 施工参考卡（CLI 命令）

| CLI 命令 | 来源盲点 | 功能 |
|---------|:--:|------|
| `zephyr rollback status` | B27 | 回滚系统当前状态 |
| `zephyr rollback stats` | B12 | MTTR/频率/成功率 |
| `zephyr rollback stats --tokens` | B60 | Token 成本统计 |
| `zephyr rollback stats --heatmap` | B94 | 回滚热点分析 |
| `zephyr rollback stats --weak-gate` | B94 | 最常被打破的门禁 Top 5 |
| `zephyr rollback stats --agent-quality` | B94 | 每个 Agent 回滚率 |
| `zephyr rollback stats --alerts` | B83 | 通知压抑制统计 |
| `zephyr rollback preview` | B5 | 回滚预览——受影响文件+冲突风险 |
| `zephyr rollback preview --tag {name}` | B62 | 语义化回滚目标预览 |
| `zephyr rollback cancel` | B20 | BREAK_GLASS——取消待执行回滚 |
| `zephyr rollback gc` | B50 | 手动触发 checkpoint GC |
| `zephyr rollback --to {sha_or_tag}` | B71 | Owner 手动指定回滚目标 |
| `zephyr rollback verify-audit {id}` | B39 | 验证审计记录 HMAC |
| `zephyr rollback verify --reproduce {sha}` | B82 | 隔离 worktree 重放验证 |
| `zephyr rollback runbook show <id>` | B123 | 查看历史回滚 Runbook |
| `zephyr rollback notes list {sha}` | B88 | 查看 commit 回滚历史 |
| `zephyr rollback undo-last-revert` | B89 | 从 trash 恢复上次回滚（7 天内）|
| `zephyr rollback complexity-report` | B115 | 系统复杂度分析 |
| `zephyr rollback conflict-report <id>` | B128 | 跨 agent 影响报告 |
| `zephyr rollback dashboard` | B47 | Markdown 零依赖仪表盘 |
| `zephyr rollback drill` | B41 | 手动触发回滚演练 |
| `zephyr rollback kill` | B46 | Kill Switch 操作 |
| `zephyr heartbeat` | B111 | Owner 心跳签到 |
| `zephyr feature-flags list/toggle/rollback` | B112 | Feature Flag 管理 |
| `zephyr commit-quality stats` | B118 | AI vs 人类 commit 质量 |
| `zephyr context stats` | B120 | 上下文窗口回滚 token 占比 |
| `zephyr knowngoodstate list/verify/tag-bad` | B124 | 已验证状态管理 |
| `zephyr sandbox status/audit/breach-report` | B121 | 沙盒健康检查 |

### 16.9 容量升级 Phase

| Phase | # | 任务 | 覆盖缺口 | 优先级 |
|:---:|:--:|------|:--:|:---:|
| capacity-1 | C1.1 | 模块分片架构落地——ShardedRollbackLock + SQLite sharding | GAP-01/03/06 | P0 |
| capacity-1 | C1.2 | 自适应并发控制——AdaptiveThrottle + hardware_monitor | GAP-01/11 | P0 |
| capacity-1 | C1.3 | 内建脚本调度器——script_scheduler + incremental_scanner | GAP-09/10 | P0 |
| capacity-1 | C1.4 | 差异快照+分层存储 | GAP-05 | P0 |
| capacity-1 | C1.5 | 配额重校准 | GAP-02/12 | P0 |
| capacity-2 | C2.1-C2.4 | Git sparse-checkout/PriorityMultiQueue/依赖图优化/监控聚合 | GAP-04/06/08/13 | P1-P2 |
| capacity-3 | C3.1-C3.4 | 温备分片/全量周检/Checkpoint GC v2/GPU VRAM 监控 | GAP-10/14/15/11 | P1-P2 |

### 16.10 故障与操作手册

| 故障现象 | 诊断命令 | 根因 | 修复操作 |
|---------|---------|------|---------|
| 回滚被拒绝 exit=2 | `zephyr rollback status` | preflight 检查失败 | 查看具体拒绝原因→修复→重试 |
| 回滚卡住无响应 | `ls .zephyr/rollback/in_flight/` | in_flight 文件残留 | 确认无进程占用→清理 in_flight |
| DB 恢复失败 exit=8 | `zephyr rollback verify-audit {id}` | JSONL 快照损坏 | 尝试上一个有效快照 |
| Agent 反复回滚 | `zephyr rollback stats --agent-quality` | Loop Detector 触发 | 暂停 agent→DEFER_TO_HUMAN |
| 审计日志不一致 | `zephyr rollback verify-audit {id}` | Sidecar 崩溃 | 重启 audit_sidecar_daemon |
| 回滚系统自毁 exit=40 | `sha256sum src/zephyr/infrastructure/rollback/*.py` | 核心文件被篡改 | rollback_bootstrap 零依赖恢复→S3 自愈 |

### 16.12 并发操作模型

| 场景 | 并发策略 | 锁粒度 | 冲突处理 |
|------|---------|--------|---------|
| 多 Agent 同时回滚 | 排队串行 | 全局 rollback.lock | 优先级排序+10s 超时 |
| 回滚+git gc 并发 | 互斥 | GC 检测 | exit=6 GC_LOCKED→5min 后重试 |
| 回滚+checkpoint 创建 | 互斥 | checkpoint.lock | 创建优先，回滚等待 |
| 回滚+审计写入 | 并行 | 无锁 | audit_sidecar 独立进程 |
| 多 Agent 文件冲突 | 检测+广播 | 文件级 | cross_agent_conflict_detector |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_id_registry.yaml |
| 并发 AI Agent | ~10 | 活跃 session 数 |
| 日回滚配额 | 20 | rollback_budget.py |
| SQLite 实例 | 1 (WAL) | 文件系统 |
| Git 文件数 | ~500 | git ls-files | wc -l |
| JSONL 快照/天 | ~20 | db_snapshots/ 目录 |
| Token/天 | 100K | rollback_budget.py |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-01 | max_concurrent=3 | 模块分片锁+AdaptiveThrottle 40-100 | >10 并发回滚 |
| GAP-02 | max_daily=20 | 日配额 500+分级超额策略 | >50 日回滚 |
| GAP-03 | SQLite 单写者 | 30 shard 分片+连接池 | >20 并发 DB 写 |
| GAP-04 | Git 操作线性变慢 | Sparse Checkout+commit-graph | >5,000 文件 |
| GAP-05 | max_snapshots=100 | 差异 dump+分层存储 hot/warm/cold | >200 快照/天 |
| GAP-06 | 全局单锁 | 模块分片锁 30 组 | >5 并发回滚 |
| GAP-09 | 无增量扫描 | 内建脚本调度器+倒排索引 | >50 AI 并发 |
| GAP-11 | 零硬件感知 | hardware_monitor+resource_governor | CPU>80% |
| GAP-12 | max_daily_tokens=100K | 2M+规则引擎降级 | >500K tokens/天 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.10.0 | 1-5 | 基线+盲点深挖 | 62 文件全部实现 | ✅ |
| v0.11.0 | 5 | 容量升级设计 | 8 维度升级方案+7 新 exit code+4 新风险 | ⚠️ 设计完成 |
| v6.0.0 | 6 | 规格化升级 | 模板 v3.3 合规+Layer 2 砍削+章节补全 | ✅ |
| v7.0.0 | 7 | 模板 v3.5/v3.6 升级 | §0前移+§7/§15删除+§14类型列+§0.1存在性列+§5.1去原因列+§5.3临时时态+§10拆分+铁律#13-#15+拆分判定+§16.3时态+施工声明时态 | ✅ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-01 | 回滚并发上限 3 | P0 | v0.11.0 | 待施工 |
| GAP-02 | 日回滚配额 20 | P0 | v0.11.0 | 待施工 |
| GAP-03 | SQLite 并发写入 | P0 | v0.11.0 | 待施工 |
| GAP-04 | Git 仓库规模 | P0 | v0.11.0 | 待施工 |
| GAP-05 | JSONL 快照存储 | P0 | v0.11.0 | 待施工 |
| GAP-06 | 回滚锁粒度 | P0 | v0.11.0 | 待施工 |
| GAP-09 | 增量扫描集成 | P0 | v0.11.0 | 待施工 |
| GAP-11 | 硬件资源感知 | P1 | v0.11.0 | 待施工 |
| GAP-12 | Token 预算 | P1 | v0.11.0 | 待施工 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-021-01 | git commit 是天然 checkpoint | A:git-native/B:DB-state/C:双轨 | A | 与项目 git 工作流统一 | 2026-05-05 |
| 2 | D-021-02 | auto_guard 后验失败自动回滚 | A:自动/B:手动确认 | A | 10+ 并发对话不可能等 Owner | 2026-05-05 |
| 3 | D-021-03 | 回滚后仅跑 G0 门禁 | A:G0/B:G0-G7 | A | 回滚到已验证状态，G0 足够 | 2026-05-05 |
| 4 | D-021-04 | SQLite dump JSONL 双轨 | A:JSONL/B:Event Sourcing | A | 零额外依赖，最小方案 | 2026-05-05 |
| 5 | D-021-05 | 失败信号三分类 | A:统一/B:分类 | B | 不同失败类型恢复策略完全不同 | 2026-05-05 |
| 6 | D-021-06 | 回滚幂等保护 | ①无幂等 ②execution_id+in_flight+步骤级追踪 | ② | Temporal Durable Execution 精确一次语义；B43 | 2026-05-06 |
| 7 | D-021-07 | Forward-Fix 优先 | ①一律 revert ②soft_failure+≤3 文件优先 forward-fix | ② | Bytebase Forward-Fix；B51 | 2026-05-06 |
| 8 | D-021-08 | 三级 Kill Switch | ①仅全杀/全不杀 ②L1/L2/L3+自动递进 | ② | 金融 HFT MiFID II 四级 Kill；B46 | 2026-05-06 |
| 9 | D-021-09 | 定期回滚演练 | ①仅 CI 模拟 ②每周 DiRT drill+连续 2 次 FAIL 熔断 | ② | Google SRE DiRT；B41 | 2026-05-06 |
| 10 | D-021-10 | 回滚预算管理 | ①无限 ②并发≤3+日配额≤20→超 budget 切 forward-fix | ② | 排队论；B55 | 2026-05-06 |
| 11 | D-021-11 | 回滚系统自举 | ①主回滚器故障即全停 ②rollback_bootstrap.py 零依赖+chmod 444 | ② | DB WAL 是 C 实现在 SQL 层崩溃时仍可用；B56 | 2026-05-06 |
| 12 | D-021-12 | AI 幻觉防护 | ①仅注入 context prompt ②强制 state_verification_round | ② | Microsoft VeriTrail DAG；B57 | 2026-05-06 |
| 13 | D-021-13 | 语义变形检测 | ①仅按(task,gate)检测 ②AST 语义相似度>70%→L2 Skill Kill | ② | OWASP LLM Top 10；B58 | 2026-05-06 |
| 14 | D-021-14 | Token 预算纳入回滚成本 | ①仅 CPU/I/O ②增加 token_cost+max_daily_tokens 100K | ② | LLM 经济学；B60 | 2026-05-06 |
| 15 | D-021-15 | 温备热切 | ①等待 git revert ②warm_standby 副本+<100ms RTO | ② | 金融热备<50ms；B61 | 2026-05-06 |
| 16 | D-021-16 | GPG 签名链保持 | ①revert 不签名 ②gpgSign=true→git revert --gpg-sign | ② | SOX 合规；B65 | 2026-05-06 |
| 17 | D-021-17 | Prompt 注入防护 | ①自由文本注入 ②prompt_injection_filter+结构化 JSON base64 | ② | OWASP LLM01；B76 | 2026-05-06 |
| 18 | D-021-18 | 声明式回滚策略 | ①Python 硬编码 ②YAML 声明式+热加载 | ② | Spring @Transactional；B77 | 2026-05-06 |
| 19 | D-021-19 | GDPR 遗忘权冲突 | ①恢复所有文件 ②preflight 检查 right_to_be_forgotten_registry | ② | GDPR Art.17 罚款年营收 4%；B78 | 2026-05-06 |
| 20 | D-021-20 | 告警疲劳管理 | ①逐条推送 ②notification_throttle+daily_digest+realtime_alert | ② | PagerDuty alert grouping；B83 | 2026-05-06 |
| 21 | D-021-21 | 回滚反馈闭环 | ①仅处置不学习 ②回滚记录作为 few-shot 学习信号 | ② | 从处置到学习范式转变；B93 | 2026-05-06 |
| 22 | D-021-22 | 独立审计 Sidecar | ①同进程写入 ②audit_sidecar_daemon 独立 PID/OS user | ② | 取证黄金法则；B96 | 2026-05-06 |
| 23 | D-021-23 | git 二进制完整性 | ①subprocess.run(["git",...])PATH ②绝对路径+SHA-256 验证 | ② | Ultralytics 2024 供应链攻击；B97 | 2026-05-06 |
| 24 | D-021-24 | 外部时间证明 | ①信任系统时钟 ②NTP×3 方+>60s 偏差拒绝 | ② | NTP 默认无认证 MITM；B99 | 2026-05-06 |
| 25 | D-021-25 | 持续完整性证明链 | ①仅当前状态证明 ②日级 Hash Tree Root→S3 Object Lock | ② | 取证需证明历史 6 月未篡改；B109 | 2026-05-06 |
| 26 | D-021-26 | 取证隔离 | ①活跃工作树取证 ②git clone --mirror 只读副本 | ② | 观察不能改变被观察对象；B110 | 2026-05-06 |
| 27 | D-021-27 | 分级自治（Owner 缺席）| ①DEFER_TO_HUMAN 无降级 ②L0→L1→L2→L3 四级递进 | ② | UC Berkeley AI Agent Risk Framework；B111 | 2026-05-06 |
| 28 | D-021-28 | Feature Flag 发布分离 | ①部署=上线 ②flag 注册表独立+秒级 flip 替代 revert | ② | Google 2025/6 级宕机；B112 | 2026-05-06 |
| 29 | D-021-29 | LLM 模型版本固定 | ①使用 latest/default ②model_version_contract+regression test | ② | GPT-4o→4.1 注入抵抗率 94%→71%；B113 | 2026-05-06 |
| 30 | D-021-30 | AI 置信度决策门槛 | ①无条件信任 ②置信度<0.7 自动降级 | ② | UC Berkeley 框架；B114 | 2026-05-06 |
| 31 | D-021-31 | Error Budget 自治边界 | ①自治级别固定 ②健康时快速自治/不稳定时仅修复 | ② | Google SRE 错误预算；B116 | 2026-05-06 |
| 32 | D-021-32 | 回滚系统复杂度预算 | ①无限增长 ②文件数≤25/代码行≤3000 | ② | Google SRE simplicity；B115 | 2026-05-06 |
| 33 | D-021-33 | 沙盒隔离原则 | ①AI 可执行任意 shell ②文件操作必须通过沙盒白名单 | ② | Claude Code rm -rf 事件；B121 | 2026-05-06 |
| 34 | D-021-34 | 核心代码自防卫 | ①chmod 644 ②chmod 440+tripwire inotify→DEFENSE_MODE | ② | OpenAI o3 删除 shutdown 脚本；B122 | 2026-05-06 |
| 35 | D-021-35 | knowngoodstate 替代 checkpoint | ①checkpoint 只保存状态 ②保存 5 项健康检查全过的验证收据 | ② | 金融 verified trade receipt；B124 | 2026-05-06 |
| 36 | D-021-36 | 回滚目标陈旧度分级 | ①不区分 ②<7 天绿/7-30 天黄/>30 天红+Owner 确认 | ② | Zephyr Cloud 文档警告；B125 | 2026-05-06 |
| 37 | D-021-37 | 凭据泄露自动响应 | ①不检查 ②git diff 检测→自动轮替→Runbook 标记 | ② | B126 | 2026-05-06 |
| 38 | D-021-38 | 回滚来源白名单 | ①任何接口可触发 ②仅 trusted sources——拒绝 MCP/HTTP 匿名 | ② | B130 | 2026-05-06 |
| 6 | D-021-39 | 模块分片架构 | A:全局锁/B:分片锁 | B | 消除全局瓶颈 | 2026-05-12 |
| 7 | D-021-40 | 自适应并发控制 | A:静态/B:动态 | B | 基于资源水位动态调整 | 2026-05-12 |
| 8 | D-021-41 | 差异快照+分层存储 | A:全量/B:差异+分层 | B | 解决 2,000 snapshots/day 压力 | 2026-05-12 |
| 9 | D-021-42 | 内建脚本调度器 | A:外部调度/B:内建最小化 | B | 零依赖优先 | 2026-05-12 |
| 10 | D-021-43 | 硬件感知资源分区 | A:无感知/B:显式分区 | B | 防止回滚风暴耗尽硬件 | 2026-05-12 |
| 11 | D-021-44 | 增量扫描默认+全量周检 | A:全量/B:增量+周检 | B | 匹配 1,500 模块规模 | 2026-05-12 |
| 12 | D-021-45 | 配额体系 10-25x 重校准 | A:当前/B:重校准 | B | 匹配 100 AI 并发 | 2026-05-12 |
| 13 | D-021-46 | Git Sparse Checkout | A:全量/B:sparse | B | 避免 15,000 文件全量操作 | 2026-05-12 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 为什么 | 违反后果 |
|---|------|--------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | AI 零记忆，不知道相对路径的基准在哪 | 文件创建到错误位置 |
| 2 | **必备链接不可省略**——即使与前序文档重复也必须完整列出 | AI 每次新 session 是零记忆，不记得前序文档写了什么 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程、不保存未选方案 | 决策过程是草稿的事——蓝图是施工依据，不是讨论记录 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | AI 不知道项目目录规范，会自行创建路径 | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | AI 不知道边界在哪，会越界修改 | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | AI 不知道系统能容纳多少，可能设计出无法扩展的方案 | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | AI 不知道旧东西怎么处理，可能直接删除或保留 | 断链——旧引用找不到文件；或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | AI 无法处理模糊指令，需要明确的二元判断 | 执行漂移——AI 自行决定，可能选错 |
| 9 | **蓝图必须自包含**——关键信息不能只写"详见XX" | AI 可能不读引用的文件 | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议**——禁止直接删除任何文件 | 没有git备份，删除不可逆；AI可能误判文件"没用了" | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 标completed但代码不存在=虚假进度，误导下一个AI | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 路径不一致=AI找不到代码 | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图是当前设计文档，不是历史记录 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
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

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| 回滚系统蓝图中"容量升级设计"（25个新组件+9个GAP） | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 回滚系统蓝图中"8层防御架构" | **原地** | 防御是回滚的核心能力，不是独立子系统 |
| 回滚系统蓝图中"盲点对照表 B1-B130" | **原地** | 盲点是回滚设计的边界条件，不是独立子系统 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | rollback_manager.py（降级） | `D:\ZephyrAlpha\src\zephyr\orchestrator\rollback_manager.py` | 废弃型 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\rollback_executor.py` | 降级为仅调试场景手动 DB 快照→标记 deprecated→Phase 4 物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | rollback_manager.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\rollback_manager.py` | DB-state checkpoint | 仅 DB 快照，无 git-native 双轨，已降级为调试工具 |
| 2 | resilience/rollback_manager.py | `D:\ZephyrAlpha\src\zephyr\orchestrator\resilience\rollback_manager.py` | 完整 checkpoint/rollback_to 链路 | 旧设计（KBG-0038），仅 DB 恢复无 git-native——**待迁移为 thin shim** |
| 3 | governance/rollback/contracts.py | `D:\ZephyrAlpha\src\zephyr\governance\rollback\contracts.py` | RollbackHandler 同名 | G-CT-002 契约消费端，非核心引擎——**须重命名** |
| 4 | governance/rollback/result_types.py | `D:\ZephyrAlpha\src\zephyr\governance\rollback\result_types.py` | RollbackResult 同名 | G-CT-003 数据结构，字段不同——**须重命名** |
| 5 | feedback_loop/verifiers/auto_rollback.py | `D:\ZephyrAlpha\src\zephyr\feedback_loop\verifiers\auto_rollback.py` | AutoRollback 与 AutoRollbackTrigger 重叠 | **待清理**——应调用 AutoRollbackTrigger |
| 6 | feedback_loop/verifiers/rollback_integrity.py | `D:\ZephyrAlpha\src\zephyr\feedback_loop\verifiers\rollback_integrity.py` | RollbackIntegrity 与 RollbackVerifier 重叠 | **待清理**——应调用 RollbackVerifier |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | rollback/ 目录 | `D:\ZephyrAlpha\src\zephyr\infrastructure\rollback\` | 业务代码 | 修改 |
| 2 | tests/rollback/ | `D:\ZephyrAlpha\tests\rollback\` | 测试代码 | 修改 |
| 3 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_autonomy_core\rollback_system\blueprint.md` | 蓝图 | 修改 |
| 4 | db_snapshots/ | `D:\ZephyrAlpha\data\rollback\db_snapshots\` | 快照存储 | 读取 |
| 5 | rollback_metrics.db | `D:\ZephyrAlpha\data\rollback\rollback_metrics.db` | 指标存储 | 读取 |

---

## 治理信息

> SSoT 声明已前移至 §0.4。

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-15 | 7.0.0 | v3.5/v3.6升级：§0前移至概述后；§7备选方案删除（信息由§18决策记录覆盖）；§15后果删除（正面与§1重复，负面合并到§14风险）；§14增加"类型"列承接负面后果；§0.1增加"存在性"+"阻塞原因"列+补2缺失文件；§5.1去掉"原因"列改为"值"列；§5.3标注临时时态+增加"执行状态"列；§10拆为§10.1-§10.4；铁律新增#13-#15；新增蓝图拆分判定标准；§16.3施工步骤时态属性；尾部施工声明标注时态属性；Layer 2砍削（§7/§15/§5.1原因列）；frontmatter version→7.0.0/generation→7/last_updated→2026-05-15 |
| 2026-05-14 | 6.0.0 | v3.3合规+规格化升级+Layer 2砍削+章节补全 |
| 2026-05-15 | 8.0.0 | 回填+压缩：回填§1.5/§1.6/§1.7/§2.3/§5.4/§5.7(44条Anti-Patterns)/§6.1/§6.2/§6 Exit Codes 6-46/§16.7 Phase 8.2-8.15+Phase 9+10/§16.8 CLI命令/§16.10/§16.12/§18 D-021-06~38(25条决策)/术语表/已知问题/自检清单/成熟度/版本路线图；压缩判定：业界对标/ASCII图/变更历史段落→删除；Anti-Patterns→二值规则表；Exit Codes→3列表 |
| 2026-05-15 | 9.0.0 | 责任审查+概念重叠声明：新增§0.4 SSoT声明+§0.5代码目录唯一性+§10.5概念重叠声明；更新"项目中已有类似功能"补充6项影子实现；治理信息SSoT声明合并到§0.4 |

---

## 术语表

| 术语 | 定义 |
|------|------|
| RollbackExecutor | 四级回滚操作封装（full_revert/partial_revert/discard/hard_reset）|
| RollbackVerifier | G0 门禁验证+__pycache__ 清理+DB 一致性检查 |
| AutoRollbackTrigger | 监听 auto_guard 后验失败信号→触发自动回滚 |
| RollbackStateMachine | 步骤级状态追踪+部分失败恢复+in_flight 管理 |
| ForwardFixRunner | 回滚替代路径——优先 FIX commit 而非 revert |
| rollback_bootstrap | 零依赖最小化回滚器——主执行器故障时的最后防线 |
| state_verification_round | AI 幻觉防护——强制 AI 列出文件 MD5/行数/签名→Guard 验证 |
| warm_standby | 温备热切——parallel git worktree+<100ms RTO |
| knowngoodstate | 已验证正确状态收据——5 项健康检查全过才标记 verified |
| DiRT drill | Disaster Recovery Test——定期回滚演练 |
| Kill Switch | 三级紧急停止（L1 Session/L2 Skill/L3 Global）|
| audit_sidecar | 独立审计 Sidecar——独立 PID/OS user 写入审计日志 |
| CT-RBK-GATE-001 | 回滚系统门禁契约——定义 exit codes 和 Pipeline 行为 |

---

## 已知问题与盲点登记

> **时态属性**：本节属于**永久时态**——未解决的盲点是 AI 施工时的边界条件。解决后标记"已解决"但保留记录。

| 盲点ID | 描述 | 优先级 | 状态 | 对应 Phase |
|--------|------|:---:|:---:|:---:|
| B1-B5 | 数据模型/revert vs discard/Executor/Verifier/Trigger | P0 | ✅ 已解决 | scaffold |
| B6-B10 | Loop Detector/Partial Revert/队列/Non-tracked | P1 | ✅ 已解决 | experimental |
| B11-B14 | Simulator/Metrics/Hard Reset/Remote Sync | P2 | ✅ 已解决 | beta |
| B15-B17 | AutoRollbackTrigger/Verifier/GATE-001 | P1 | ✅ 已解决 | production |
| B20 | BREAK_GLASS | P2 | ✅ 已解决 | production |
| B41-B55 | 幂等/状态机/演练/Kill Switch/Forward-Fix/上下文/依赖/migration/仪表盘/JSONL/differential/GC/按操作粒度/预算 | P0-P2 | ✅ 已解决 | resilience |
| B56-B75 | 自举/幻觉/变形/漏洞/Token/温备/语义Tag/分支/Git基建/GPG/密钥/Shell/venv/env/时间/Owner/网络/S3/证明/Submodule | P0-P2 | ✅ 已解决 | sovereign |
| B76-B95 | Prompt注入/声明式/GDPR/连接池/嵌套/MCP/确定性/告警/渐进/bisect/Watcher/Shallow/notes/软删除/filter-branch/决策疲劳/Vendor/反馈/热力图/威胁 | P0-P2 | ✅ 已解决 | metacognitive |
| B96-B110 | Sidecar/二进制/Shell注入/NTP/bitrot/TOCTOU/TPM/原子写入/in_flight/WAL/可问责/reflog/notes沙箱/证明链/取证 | P0-P2 | ✅ 已解决 | forensic |
| B111-B120 | 心跳/Flag/模型/置信度/复杂度/ErrorBudget/rebase/commit质量/fail-mode/上下文GC | P0-P1 | ✅ 已解决 | governance |
| B121-B130 | 沙盒/自防卫/Runbook/knowngoodstate/陈旧度/凭据/WAL/冲突/意图/滥用 | P0-P2 | ✅ 已解决 | adversarial-security |

---

## 自检与闭合清单

| # | 检查项 | 状态 |
|---|--------|:---:|
| 1 | §0 代码对齐验证——所有文件存在且非空 | ✅ |
| 2 | §4 接口契约——所有公共 API 有签名 | ✅ |
| 3 | §5 约束条件——技术约束+容量估算+迁移方案 | ✅ |
| 4 | §6 错误处理——15 种异常场景+46 exit codes | ✅ |
| 5 | §9 测试策略——5 种测试类型 | ✅ |
| 6 | §10 依赖关系——上游+下游+容量 | ✅ |
| 7 | §16 施工指引——Phase 1-10+容量升级 | ✅ |
| 8 | §18 决策记录——38 条决策 | ✅ |
| 9 | §5.7 Anti-Patterns——44 条红线 | ✅ |
| 10 | 蓝图模板合规——所有 REQUIRED_SECTIONS 存在 | ✅ |

---

## 成熟度声明

| 维度 | 等级 | 依据 |
|------|:---:|------|
| 架构稳定性 | stable | 8 层防御架构+容量升级设计完成 |
| 接口稳定性 | stable | §4 接口契约+CT-RBK-GATE-001 exit codes 定义完整 |
| 代码覆盖率 | evolving | 61 .py 文件已实现，测试覆盖率待提升 |
| 文档完整性 | stable | 蓝图+施工图模板 v3.6 合规 |
| 运维就绪度 | evolving | CLI 命令完整，但 DiRT drill 未定期执行 |
| **整体** | **stable** | 对齐 dependency_path_panorama.md——核心架构+接口已冻结 |

---

## 版本演进路线图

| 版本 | 状态 | 核心变更 |
|------|:---:|---------|
| v0.1.0-v0.4.0 | ✅ 已完成 | 基础回滚+partial_revert+loop_detector+1人运维CLI |
| v0.5.0 | ✅ 已完成 | 状态机+Forward-Fix |
| v0.6.0 | ✅ 已完成 | 自举+幻觉防护+温备 |
| v0.7.0 | ✅ 已完成 | Prompt注入过滤+声明式策略 |
| v0.8.0 | ✅ 已完成 | 审计Sidecar+git完整性+NTP+取证+证明链+TOCTOU |
| v0.9.0 | ✅ 已完成 | 心跳+自治+Flag+模型契约+置信度+ErrorBudget+复杂度+commit质量+fail-mode+上下文GC |
| v0.10.0 | ✅ 已完成 | 沙盒+自防卫+Runbook+knowngoodstate+陈旧度+凭据+WAL+冲突+意图+滥用检测 |
| v0.11.0 | ⚠️ 待施工 | 容量升级——分片锁+AdaptiveThrottle+差异快照+内建调度器 |
| v6.0.0 | ✅ 已完成 | 规格化升级+模板 v3.3 合规 |
| v7.0.0 | ✅ 已完成 | 模板 v3.5/v3.6 升级 |
| v8.0.0 | ✅ 已完成 | 回填+压缩——恢复被删除的施工内容+模板合规+压缩优化 |
