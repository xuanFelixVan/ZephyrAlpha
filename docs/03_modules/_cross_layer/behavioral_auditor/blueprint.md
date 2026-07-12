---
module_id: MOD-INF-033
activation_phase: requires_100ai
submodule_path: src/zephyr/compliance/behavioral_auditor
title: "Behavioral Auditor 蓝图 — 行为审计器·AI行为边界监控"
doc_type: blueprint
status: Draft
version: "3.3.0"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-10"
valid_from: "2026-05-10"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/governance/drift_detection/"
actual_disk_path_note: "MOD-INF-033独有5个文件(verdict_engine/admission_controller/protection_index/gpu_consensus_scheduler/session_lifecycle)将放在此目录。54个共享文件属于MOD-INF-023(src/zephyr/behavioral-auditor/)，033通过import消费"
architecture_layer: "L1_分析引擎"
belongs_to: "MOD-INF-027"
parent_module: "MOD-INF-027"
functional_domain: governance
summary: "AI行为边界审计引擎——消费AuditTrail事件流，比对Gate Engine许可矩阵，输出VERDICT（PASS/YELLOW/RED），执行阻断+问责+回滚"
tags: [behavioral-audit, ai-agent-security, authorization-boundary, drift-detection, audit-trail, zero-trust, block-alert-rollback, evidence-chain, multi-model-consensus, graduated-response, meta-audit, behavioral-baseline, red-teaming, circuit-breaker, cost-awareness, compliance-mapping, session-continuity, capacity-upgrade]
priority: P1
runtime_plane: warm
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
generation: 3
codification_level: L1
codification_at: "2026-05-14"
last_verified: "2026-05-14"
last_updated: "2026-05-14"
depends_on:
  - {target: "MOD-INF-020", at: "full", why: "AuditTrail——行为审计唯一数据源，所有AI操作MUST通过AuditTrail记录不可变日志"}
  - {target: "MOD-INF-023", at: "full", why: "DriftDetector——漂移信号作为行为审计触发线索"}
  - {target: "MOD-GATE_ENGINE", at: "full", why: "Gate Engine——授权边界定义的执行者，许可矩阵查询"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——越界操作确认后的回滚执行器"}
  - {target: "MOD-FEEDBACK_LOOP", at: "§2", why: "Feedback Loop——行为审计误报/漏报回写规则演进"}
  - {target: "MOD-LLM_SECURITY", at: "§3", why: "LLM Security——多模型共识输入输出安全校验"}
  - {target: "MOD-INF-018", at: "§3", why: "Agent RBAC——审计操作权限校验"}
  - {target: "MOD-INF-019", at: "§3", why: "Agent Spec——SKILL-DOM-BEH-001技能注册与渐进式加载"}
  - {target: "MOD-INF-022", at: "§3", why: "Escalation Protocol——L4~L6自动升级通道"}
  - {target: "MOD-INF-024", at: "§2", why: "Budget Enforcer——多模型共识Token配额管理"}
  - {target: "MOD-INF-025", at: "§2", why: "A2A Protocol——多Agent并发操作时的行为审计协调"}
  - {target: "MOD-INF-015", at: "§2", why: "System Telemetry——行为审计SLI/SLO指标推送"}
  - {target: "MOD-INF-026", at: "§1", why: "Asset Inventory——保护目标清单元数据来源"}
  - {target: "MOD-DATABASE", at: "§4", why: "Database System——Evidence Chain/Baseline/Session State底层存储"}
  - {target: "MOD-MASTER_BLUEPRINT", at: "§一", why: "集成总蓝图——CT-*集成契约登记"}
  - {target: "SYS-MASTER-001", at: "§〇", why: "系统总蓝图——容量升级方案上游依赖"}
  - {target: "MOD-INF-027", at: "section 4", why: "Audit Orchestrator (编排)"}
references:
  - {id: "MOD-INF-027", at: "full", why: "Audit Orchestrator——BehavioralAuditor是Orchestrator三大审计子系统之一"}
  - {id: "MOD-INF-028", at: "full", why: "SemanticAuditor——平级审计子系统，审计规则文档语义"}
  - {id: "MOD-INF-029", at: "§0,§1,§17", why: "OrphanJudge——冷启动分派+模块身份+全系统集成最佳实践模板"}
  - {id: "MOD-INF-030", at: "§2,§3", why: "RedBlue Validator——红蓝对抗引擎，§15红队对抗协同"}
  - {id: "MOD-INF-031", at: "§2", why: "AutoFix Engine——回滚后修复"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Behavioral Auditor 蓝图 — 行为审计器·AI行为边界监控

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 行为基线数据量（事件数） | 0 | ≥1000 | ❌ |
> | 基线积累天数 | 0天 | ≥14天 | ❌ |
> | 异常行为误报率 | N/A | ≤30% | ❌ |
>
> **为什么现在不自动化**: 行为审计需要先积累"正常行为长什么样"的基线数据。现在连基线都没有，审计员来了也不知道什么算异常。没有基线 = 所有行为都是"异常" = 100% 误报。
> **什么时候建**: 当 AuditTrail 事件积累 ≥1000 条且 ≥14 天，或 Owner 要求主动行为监控时。基线数据由 Audit Trail 自动积累，达到门槛后自动触发。
> **自动化宿主**: FLE `_periodic_checks()` → `_behavioral_audit_check()` + CircadianScheduler `hour=6` → `_behavioral_baseline_update()`

> module_id: MOD-INF-033 | version: 3.3.0 | status: draft | layer: cross_layer
> actual_disk_path: src/zephyr/behavioral_audit/ | generation: 3 | construction_progress: partially_implemented

## 概述

BehavioralAuditor 是 AI 行为边界审计引擎——解决"AI 做了不该做的操作"这一核心安全问题。核心职责：消费 AuditTrail 事件流 → 比对 Gate Engine 许可矩阵 → 输出 VERDICT（PASS/YELLOW/RED）→ 阻断+告警+回滚。当前规模 54 个 Python 模块已实现漂移检测/基线管理/熔断/混沌注入等基础能力，目标容量 100 AI 并发/10K 脚本。上游依赖 AuditTrail(MOD-INF-020)/DriftDetector(MOD-INF-023)/Gate Engine(MOD-GATE_ENGINE)，下游被 AuditOrchestrator(MOD-INF-027)调度消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§15）。

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> 存在性状态受控词表：`未实现` / `已实现` / `已阻塞` / `已废弃`
> 此列是**当前事实**（永久时态），不是施工进度追踪（临时时态）

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-033`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 模块导出+公共 API | 已实现 | — |
| 2 | `__main__.py` | §4.5 | CLI 入口 | 已实现 | — |
| 3 | `drift_engine.py` | §3.1 | 漂移扫描引擎 | 已实现 | — |
| 4 | `drift_models.py` | §4.2 | 漂移数据模型 | 已实现 | — |
| 5 | `drift_infrastructure.py` | §5 | 漂移基础设施（预算/检查点/恢复） | 已实现 | — |
| 6 | `drift_result_types.py` | §4.2 | 语义/DB/安全漂移结果类型 | 已实现 | — |
| 7 | `drift_training.py` | 蓝图特有§F | AI 训练循环检测+跨语言漂移 | 已实现 | — |
| 8 | `drift_hotfix_bypass.py` | §6 | 热修复旁路审计 | 已实现 | — |
| 9 | `drift_cron_scheduler.py` | 蓝图特有§N | Cron 定时调度 | 已实现 | — |
| 10 | `detector_dispatcher.py` | §3.1 | 检测器调度+并行控制 | 已实现 | — |
| 11 | `baseline_manager.py` | 蓝图特有§D | 行为基线管理 | 已实现 | — |
| 12 | `baseline_poisoning_guard.py` | §8 | 基线投毒防护 | 已实现 | — |
| 13 | `alert_router.py` | §3.1 | 告警路由 | 已实现 | — |
| 14 | `correlation_engine.py` | §3.1 | 事件关联引擎 | 已实现 | — |
| 15 | `credibility_engine.py` | §3.1 | 可信度引擎 | 已实现 | — |
| 16 | `cross_module_score.py` | §3.1 | 跨模块评分 | 已实现 | — |
| 17 | `dashboard.py` | §3.1 | 仪表盘数据 | 已实现 | — |
| 18 | `state_machine.py` | §3.3 | 漂移状态机 | 已实现 | — |
| 19 | `events.py` | §4.2 | 事件定义 | 已实现 | — |
| 20 | `resource_guard.py` | §6 | 资源守卫+降级 | 已实现 | — |
| 21 | `scan_mutex.py` | §5.1 | 扫描互斥锁 | 已实现 | — |
| 22 | `cold_start.py` | §16 | 冷启动初始化 | 已实现 | — |
| 23 | `self_check.py` | 蓝图特有§L | 自检（SHA256+注册表+核心文件） | 已实现 | — |
| 24 | `self_test_verifier.py` | §9 | 8 项自检验证 | 已实现 | — |
| 25 | `reconciler.py` | §6 | 自动修复器 | 已实现 | — |
| 26 | `cascade_detector.py` | §6 | 级联故障检测 | 已实现 | — |
| 27 | `chaos_injector.py` | 蓝图特有§E | 混沌注入（路径重命名/YAML翻转/TODO炸弹） | 已实现 | — |
| 28 | `canary_controller.py` | §6 | 金丝雀发布控制 | 已实现 | — |
| 29 | `forensics_engine.py` | §4.2 | 取证引擎（时间线+Git 快照） | 已实现 | — |
| 30 | `runbook_generator.py` | §6 | Runbook 生成 | 已实现 | — |
| 31 | `handoff_manager.py` | §6 | 交接包管理 | 已实现 | — |
| 32 | `gate_persistence.py` | §12 | 门禁持久化 | 已实现 | — |
| 33 | `rollback_bridge.py` | §12 | 回滚桥接 | 已实现 | — |
| 34 | `brain_integration.py` | §12 | AutoRuntime Core 集成 | 已实现 | — |
| 35 | `ai_context_injector.py` | §3.1 | AI 上下文注入 | 已实现 | — |
| 36 | `ai_construction_detectors.py` | §3.1 | AI 施工检测器 | 已实现 | — |
| 37 | `absence_manager.py` | §6 | Owner 缺席管理 | 已实现 | — |
| 38 | `suppression_learner.py` | 蓝图特有§F | 抑制规则学习 | 已实现 | — |
| 39 | `trend_analyzer.py` | 蓝图特有§D | 趋势分析 | 已实现 | — |
| 40 | `roi_engine.py` | §5.2 | ROI 评分引擎 | 已实现 | — |
| 41 | `incremental_scanner.py` | §3.1 | 增量扫描器 | 已实现 | — |
| 42 | `headless_scanner.py` | §3.1 | 无头扫描器 | 已实现 | — |
| 43 | `orphan_scanner.py` | §3.1 | 孤儿资源扫描 | 已实现 | — |
| 44 | `config_consistency.py` | §3.1 | 配置一致性审计 | 已实现 | — |
| 45 | `git_bisector.py` | §6 | Git 二分查找 | 已实现 | — |
| 46 | `gitignore_auditor.py` | §3.1 | .gitignore 审计 | 已实现 | — |
| 47 | `integration_test_runner.py` | §9 | 集成测试运行器 | 已实现 | — |
| 48 | `file_attr_checker.py` | §3.1 | 文件属性检查 | 已实现 | — |
| 49 | `naming_magic_checker.py` | §3.1 | 命名魔术检查 | 已实现 | — |
| 50 | `symlink_checker.py` | §3.1 | 符号链接检查 | 已实现 | — |
| 51 | `backcompat_checker.py` | §6 | 向后兼容性检查 | 已实现 | — |
| 52 | `test_fixture_checker.py` | §9 | 测试夹具漂移检查 | 已实现 | — |
| 53 | `python_compat.py` | §5.1 | Python 兼容性扫描 | 已实现 | — |
| 54 | `tamper_proof_audit.py` | §8 | 防篡改审计 | 已实现 | — |
| 55 | `verdict_engine.py` | §4.1 | 判定引擎 | 未实现 | — |
| 56 | `admission_controller.py` | §3.1 | 事件摄入准入控制+Token Bucket | 未实现 | — |
| 57 | `protection_index.py` | §3.1 | 文件保护等级 O(1)查询 | 未实现 | — |
| 58 | `gpu_consensus_scheduler.py` | §3.1 | GPU 共识调度+API fallback | 未实现 | — |
| 59 | `session_lifecycle.py` | §17 | Session 生命周期管理与 GC | 未实现 | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 代码文件存在 | `ls D:\ZephyrAlpha\src\zephyr\behavioral-auditor\` 54 文件 | ☑ |
| actual_disk_path = src/zephyr/behavioral_audit/ → 目录尚未创建 | 目录不存在（5个独有文件待施工） | ☐ 待创建 |
| 蓝图描述的类名 = 代码中的类名 | `grep "class" *.py` 核对 | ☐ 待验证 |
| 代码头部 BLUEPRINT 引用 = MOD-INF-023 | 54文件已标注 MOD-INF-023（正确——这些文件属于 MOD-INF-023） | ☑ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | 漂移检测+基线管理+熔断+混沌注入+资源守卫 | — | — |
| v2.0.0 (全维度) | §0~§29 设计覆盖 | VerdictEngine/MultiModelConsensus/AdmissionControl/ProtectionIndex/GPUConsensusScheduler | 待施工 |
| v3.0.0 (容量升级) | 容量设计文档 | PartitionedConsumer/PerSessionBaseline/ShardedSessionStore 等 15 项容量组件 | 待施工 |
| v3.1.0 (容量审计) | 8 项缺口补全设计 | AdmissionControl/CT-BEH-DB-001 v2/GPUConsensusScheduler 等 | 待施工 |

---

## §1 设计背景与目标

### 1.1 背景

行为审计与结构审计、语义审计的本质区别：

| 维度 | 结构审计 | 语义审计 | 行为审计 |
|------|---------|---------|---------|
| 审计对象 | 文件/注册表/代码 | 规则文档（自然语言） | AI 操作序列 |
| 触发方式 | mtime 变更驱动 | 规则文档变更驱动 | 事件驱动（AuditTrail） |
| 判定方法 | 二元规则引擎 | LLM Bridge | 操作 vs 许可矩阵 |
| 确定性 | 100% | 95~98% | 100%（二进制比对） |
| 响应方式 | 模板修复 | LLM 生成修复文本 | **阻断+告警+回滚** |
| 不可逆性 | 可修复 | 可修复 | **不可逆**（越界操作已发生） |

行为审计的核心假设：**AI 做了一次它本不该做的操作**——操作已发生，无法"修复"，只能：1.阻断继续 2.告警人类 3.回滚副作用 4.记录为安全事件。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 实时判定 AI 操作是否越权 | AuditTrail 事件→VERDICT 延迟 < 10s |
| 2 | 零漏报——anchor 文件越权 MUST 被阻断 | anchor 文件越权阻断率 100% |
| 3 | 多模型共识降低误判 | 高风险判定 2/2 模型一致率 > 95% |
| 4 | 全自动触发→判定→响应→闭环 | Owner 零日常干预 |
| 5 | 100 AI 并发容量 | 事件摄入 50 events/s，判定延迟 p99 < 10s |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 结构审计（文件是否存在/注册表是否完整） | MOD-INF-027 Orchestrator 结构审计子系统 |
| 2 | 语义审计（规则文档语义一致性） | MOD-INF-028 SemanticAuditor |
| 3 | 代码安全扫描 | MOD-LLM_SECURITY LLM Security |
| 4 | AutoFix 修复 | MOD-INF-031 AutoFix Engine |
| 5 | 权限管理 | MOD-INF-018 Agent RBAC |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| 一人开发+AI 维护 | MUST 全自动化，Owner 零日常干预 |
| Windows NTFS + Defender 实时扫描 | 文件 I/O 延迟不可预测，MUST 原子写入 |
| 本地 GPU RTX 3090 24GB | 多模型共识 GPU 操作串行，MUST 排队+API fallback |
| SQLite WAL 模式 | 单写者，MUST 主线程代理写入 |
| 无 Git 备份 | 删除不可逆，MUST 安全删除协议 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 事件监听 | 消费 AuditTrail 事件流 + DriftDetector 漂移信号 |
| 2 | 许可矩阵比对 | 查询 Gate Engine who/can/what/under_what_condition |
| 3 | 判定输出 | VERDICT（PASS/YELLOW/RED）+ Evidence Chain |
| 4 | 渐进式响应 | L0~L6 七级响应梯度（静默→告警→阻断→冻结→终止） |
| 5 | 多模型共识 | 高风险判定 2/2 模型一致 |
| 6 | 行为基线画像 | 6 维基线偏离检测（BH-008） |
| 7 | Meta-Audit | 自审计——谁审计审计者 |
| 8 | 红队对抗 | 攻击自生长压力测试 |
| 9 | 反馈闭环 | FLE 误报/漏报→规则自适应 |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 记录不可变操作日志 | MOD-INF-020 AuditTrail |
| 2 | 检测状态漂移 | MOD-INF-023 DriftDetector |
| 3 | 执行授权判定 | MOD-GATE_ENGINE Gate Engine |
| 4 | 执行操作回滚 | MOD-INF-021 Rollback |
| 5 | 修复代码/文档 | MOD-INF-031 AutoFix Engine |
| 6 | 管理权限配置 | MOD-INF-018 Agent RBAC |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | EventConsumer | 消费 AuditTrail 事件流 | MOD-INF-020 | 事件流订阅 |
| 2 | PermissionChecker | 查询 Gate Engine 许可矩阵 | MOD-GATE_ENGINE | 同步调用 |
| 3 | VerdictEngine | 操作×许可矩阵→VERDICT | PermissionChecker | 同步调用 |
| 4 | GraduatedResponder | L0~L6 渐进响应 | MOD-GATE_ENGINE/020/021/022 | 事件驱动 |
| 5 | MultiModelConsensus | 高风险判定多模型辩论 | MOD-LLM_SECURITY/024 | 异步调用 |
| 6 | BaselineProfiler | 行为基线画像+异常检测 | MOD-INF-020 | 定时+事件 |
| 7 | MetaAuditor | 自审计判定行为 | VerdictEngine | 每次判定后 |
| 8 | RedTeamEngine | 红队对抗压力测试 | VerdictEngine | 定时（每周） |
| 9 | FLEAdapter | 反馈闭环规则自适应 | MOD-FEEDBACK_LOOP | 事件驱动 |
| 10 | AdmissionController | 事件摄入准入控制+Token Bucket | EventConsumer | 前置限流 |
| 11 | ProtectionIndex | 文件保护等级 O(1)查询 | MOD-INF-026 | 内存索引 |
| 12 | GPUConsensusScheduler | GPU 共识调度+API fallback | MultiModelConsensus | 排队调度 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AuditTrail 事件流 | AdmissionControl→EventClassify→PermissionCheck→Verdict | GraduatedResponder | AuditTrailEvent |
| 2 | DriftDetector 漂移信号 | 回溯 AuditTrail 溯源→判定是否 AI 越权 | VerdictEngine | DriftSignal |
| 3 | VerdictEngine RED 判定 | Block(Gate)+Alert(AuditTrail)+Rollback(MOD-021) | Escalation(MOD-022) | EvidenceChain |
| 4 | BaselineProfiler | 6 维基线对比→异常偏离 | VerdictEngine(BH-008) | BaselineReport |
| 5 | MetaAuditor | 自审计检查→META_PASS/META_FAIL | AuditTrail | MetaAuditResult |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| IDLE | AuditTrail 事件到达 | ACTIVE | AdmissionControl 通过 |
| ACTIVE | 判定完成→PASS | IDLE | 无越权 |
| ACTIVE | 判定完成→RED | RESPONDING | 越权确认 |
| RESPONDING | Block+Alert+Rollback 完成 | IDLE | 响应完成 |
| ACTIVE | Meta-Audit 失败 | DEGRADED | 自审计异常 |
| DEGRADED | Owner 手动恢复 | IDLE | 人类确认 |

---

## §4 接口契约

### 4.1 公共 API

```python
class BehavioralAuditor:
    """AI 行为边界审计引擎主类"""

    async def verify_operation(self, event: AuditTrailEvent) -> Verdict:
        """
        核心 API——判定单个操作是否越权

        输入：AuditTrailEvent（操作者/操作类型/目标/CoT 推理链）
        输出：Verdict（PASS/YELLOW/RED + Evidence Chain）
        核心逻辑：操作者身份→保护等级→许可矩阵查询→VERDICT
        """

    async def verify_batch(self, events: list[AuditTrailEvent]) -> list[Verdict]:
        """批量判定——微批处理模式"""

    def get_baseline(self, session_id: str) -> BaselineProfile | None:
        """查询 Session 行为基线"""

    def health_check(self) -> HealthStatus:
        """模块健康状态"""
```

### 4.2 数据模型

```python
from pydantic import BaseModel, Field
from enum import Enum

class VerdictLevel(str, Enum):
    PASS = "PASS"
    YELLOW = "YELLOW"
    RED = "RED"

class ProtectionLevel(str, Enum):
    ANCHOR = "anchor"
    PROTECTED = "protected"
    NORMAL = "normal"
    PUBLIC = "public"

class GraduatedLevel(str, Enum):
    L0_SILENT_LOG = "L0"
    L1_SOFT_WARN = "L1"
    L2_HARD_WARN = "L2"
    L3_SOFT_BLOCK = "L3"
    L4_HARD_BLOCK = "L4"
    L5_SESSION_FREEZE = "L5"
    L6_AGENT_KILL = "L6"

class Verdict(BaseModel):
    event_id: str = Field(..., description="AuditTrail 事件 ID")
    verdict: VerdictLevel = Field(..., description="判定结果")
    protection_level: ProtectionLevel = Field(..., description="目标文件保护等级")
    graduated_level: GraduatedLevel = Field(..., description="响应等级")
    evidence_chain: EvidenceChain = Field(..., description="完整证据链")
    model_consensus: MultiModelResult | None = Field(default=None, description="多模型共识结果")

class EvidenceChain(BaseModel):
    actor: ActorInfo = Field(..., description="操作者信息")
    operation: OperationInfo = Field(..., description="操作信息")
    authorization_check: AuthCheckResult = Field(..., description="许可矩阵查询结果")
    response: ResponseInfo = Field(..., description="响应动作")
    cot_chain: list[str] = Field(default_factory=list, description="CoT 推理链")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `verify_operation()` | `event` | ✅ | AuditTrailEvent 格式，actor_type 必须为 ai_agent/human/system |
| `verify_batch()` | `events` | ✅ | list[AuditTrailEvent]，长度 ≤ 100 |
| `get_baseline()` | `session_id` | ✅ | 格式 `session-YYYYMMDD-NNN` |
| `health_check()` | — | — | 无参数 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `verify_operation()` | `Verdict`：判定结果+证据链 | `AdmissionRejectedError` / `PermissionCheckTimeout` |
| `verify_batch()` | `list[Verdict]` | 同上 |
| `get_baseline()` | `BaselineProfile` / `None` | — |
| `health_check()` | `HealthStatus` | — |

### 4.5 MCP 接口

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| `behavioral_audit_check` | `verify_operation()` | `{event: AuditTrailEvent}` | `{verdict: Verdict}` |
| `behavioral_audit_baseline` | `get_baseline()` | `{session_id: str}` | `{baseline: BaselineProfile}` |
| `behavioral_audit_health` | `health_check()` | `{}` | `{status: HealthStatus}` |

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增 Verdict 字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 新增触发器类型（BH-009+） | ✅ 向后兼容 | 不破坏已有逻辑 |
| 修改 VerdictLevel 枚举 | ❌ 破坏性 | 需 Owner 审批 |
| 修改 ProtectionLevel 枚举 | ❌ 破坏性 | 需 Owner 审批 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | BehavioralAuditor 只读 AuditTrail | 不修改任何已记录日志 |
| 2 | 不执行 Block/Alert/Rollback | 只输出 VERDICT，由 Gate/AuditTrail/Rollback 执行 |
| 3 | 判定结果 MUST 写入 AuditTrail | 不可变安全事件 |
| 4 | 自身操作 MUST 通过 AuditTrail 记录 | 递归自审计 |
| 5 | GPU 共识操作串行 | RTX 3090 24GB，qwen3:14b 推理占 ~12GB |
| 6 | SQLite 单写者 | WAL 模式下写连接 = 1 |
| 7 | 文件写入 MUST 原子操作 | temp-file + os.replace()，防止 NTFS 损坏 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| AI 并发 Session | ~5 | 100 | 100（硬上限） | ✅ | §17 容量升级 |
| 事件摄入吞吐 | ~5 events/s | 50 events/s | 50/s（Token Bucket） | ✅ | AdmissionControl |
| SQLite 连接 | ~10 | 44（4DB×11） | 100+（WAL 模式） | ✅ | 连接池复用 |
| GPU 共识延迟 | — | p95 < 8s | 30s（超时） | ✅ | GPU 排队+API fallback |
| 内存占用 | ~50MB | ~200MB（含 ProtectionIndex） | 64GB | ✅ | — |

### 5.3 迁移/废弃方案

> 时态属性：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | 代码头部 BLUEPRINT 引用 MOD-INF-023 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` | 修改为 MOD-INF-033 | 批量替换 | Grep 全项目 MOD-INF-023 引用 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | AuditTrail 事件流中断 | 心跳超时 > 30s | 降级为定时批量审计 | 行为审计暂停 |
| 2 | Gate Engine 不可用 | PermissionCheck 超时 > 10s | 默认 BLOCK（无法判定 = 不安全） | 所有 AI 操作被阻断 |
| 3 | 多模型共识超时 | GPU/API 超时 > 30s | 降级为单模型判定 + API fallback | 高风险判定置信度降低 |
| 4 | SQLite 写入失败 | 异常捕获 | 重试 3 次→降级为内存缓冲→告警 | Evidence Chain 可能延迟持久化 |
| 5 | Meta-Audit 自检失败 | 自审计清单检查 | 停止自主判定→默认 BLOCK→通知 Owner | BehavioralAuditor 进入降级模式 |
| 6 | 事件摄入过载 | Token Bucket 超限 | 429 + Retry-After→Coalescer 反压 | 部分事件延迟处理 |
| 7 | 熔断器触发 | Session/依赖双层熔断 | Session 级熔断隔离→其他 Session 不受影响 | 单 Session 审计暂停 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | AI 修改许可矩阵使行为审计失效 | 高 | 许可矩阵属 anchor 保护→修改触发 BH-005→立即阻断 | 模拟修改 Gate 配置 |
| 2 | CoT 推理链 Prompt 注入 | 高 | MOD-LLM_SECURITY LLM Security 输入过滤→SUSPICIOUS_INPUT→默认 BLOCK | 注入测试用例 |
| 3 | BehavioralAuditor 自身越权 | 高 | Meta-Audit 自审计→降级模式→默认 BLOCK | 自审计清单检查 |
| 4 | 多模型共识被操纵 | 中 | 2/2 共识+辩论记录+API fallback | 分歧场景测试 |
| 5 | 基线投毒 | 中 | 多基线投票+哈希链验证+跨验证 | 投毒模拟测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | VerdictEngine/PermissionChecker/AdmissionControl | anchor 文件越权→RED、normal 操作→PASS | 覆盖率 > 80% |
| 2 | 集成测试 | AuditTrail→BehavioralAuditor→Gate Engine 全链路 | 事件流实时判定→Block+Alert+Rollback | 端到端通过 |
| 3 | 共识测试 | 多模型辩论协议 | 2/2 一致→执行、1/2 分歧→ESCALATE | 分歧处理正确 |
| 4 | 回归测试 | Prompt 版本锁定 | 同一 Prompt+同一输入→同一判定 | 0 回归 |
| 5 | 压力测试 | 100 AI 并发 | 50 events/s 持续 1h | p99 < 10s |
| 6 | 红队测试 | 攻击自生长 | 混沌注入+路径重命名+YAML 翻转 | 全部被检测 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-020 AuditTrail | 必须 | 事件流数据源 | v2.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-023 DriftDetector | 必须 | 漂移信号触发 | v2.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\drift-detector\blueprint.md` |
| MOD-GATE_ENGINE Gate Engine | 必须 | 许可矩阵查询 | v2.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-INF-021 Rollback | 必须 | 越界操作回滚 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-fix-engine\blueprint.md` |
| MOD-FEEDBACK_LOOP Feedback Loop | 必须 | 误报/漏报反馈 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback_loop\blueprint.md` |
| MOD-LLM_SECURITY LLM Security | 必须 | Prompt 注入防御 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm_security\blueprint.md` |
| MOD-INF-018 Agent RBAC | 必须 | 审计权限校验 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-022 Escalation | 必须 | L4~L6 升级通道 | v1.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-DATABASE Database | 可选 | SQLite 底层存储 | v3.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` |
| MOD-INF-027 AuditOrchestrator | 必须 | 调度路由 | v5.0+ | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-033` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| drift_engine.py | detector_dispatcher.py | 漂移扫描结果作为检测器调度输入 | 检查 drift scan output 存在 |
| admission_controller.py | verdict_engine.py | 准入控制通过后才能进入判定 | 检查 admission pass 状态 |
| verdict_engine.py | alert_router.py | 判定结果驱动告警路由 | 检查 verdict 输出 |
| baseline_manager.py | verdict_engine.py | 基线偏离触发判定 | 检查 baseline report |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| drift_engine.py | detector_dispatcher.py | DriftResult | 函数调用 |
| baseline_manager.py | verdict_engine.py | BaselineReport | 函数调用 |
| verdict_engine.py | alert_router.py | Verdict | 事件总线 |
| verdict_engine.py | gate_persistence.py | Verdict | 函数调用 |
| chaos_injector.py | verdict_engine.py | ChaosResult | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 脚本数>10，依赖关系复杂 |
| 2 | 依赖对齐自动验证 | 是 | 有 10 个外部依赖模块 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案（BLUEPRINT 引用修正） |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中（partially_implemented） |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖scripts/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\behavioral-auditor\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\` | Python 源码（54 模块） |
| 测试代码 | `D:\ZephyrAlpha\tests\behavioral-auditor\` | 测试用例 |
| Agent Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\SKILL-DOM-BEH-001.yaml` | 技能定义 |
| CLI 入口 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\__main__.py` | `python -m zephyr.behavioral_auditor` |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| AuditOrchestrator (MOD-INF-027) | 事件订阅+dispatch | Phase 2 TRIAGE dispatch→033 | `python -m zephyr.behavioral_auditor status` |
| Gate Engine (MOD-GATE_ENGINE) | 同步调用 | `verify_operation()` | PermissionCheck 返回正确 |
| AuditTrail (MOD-INF-020) | 事件消费+写入 | 事件流订阅+CRITICAL 事件写入 | 事件流连通性检查 |
| Rollback (MOD-INF-021) | 回滚调用 | RED 判定→rollback API | 回滚执行验证 |
| Escalation (MOD-INF-022) | 升级通道 | L4+判定→escalation API | 升级通知到达 |
| Agent Spec (MOD-INF-019) | Skill 注册 | SKILL-DOM-BEH-001 | `python -m zephyr.agent_spec list` |
| Database (MOD-DATABASE) | SQLite 读写 | CT-BEH-DB-001 | 表创建+查询验证 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| CT-BEH-DB-001 | 数据库 | BehavioralAuditor→Database SQLite 读写路径/连接池/批量策略 | MOD-DATABASE | 修改此契约必须同步更新 Database 蓝图 §26 |
| CT-BEH-AT-001 | 审计 | BehavioralAuditor→AuditTrail 事件消费+CRITICAL 写入 | MOD-INF-020 | 修改事件格式必须同步更新 AuditTrail 蓝图 |
| CT-BEH-GATE-001 | 门禁 | BehavioralAuditor→Gate Engine 许可矩阵查询 | MOD-GATE_ENGINE | 修改查询接口必须同步更新 Gate Engine 蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 代码头部 BLUEPRINT 引用 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` | MOD-INF-023→MOD-INF-033 | 代码归属漂移修正 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本更新为 3.3.0 | 蓝图升级 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 更新 frontmatter 字段 | 字段补全 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 代码头部 BLUEPRINT 引用仍为 MOD-INF-023 | 高 | 中 | 批量替换为 MOD-INF-033 | 风险 |
| 2 | 100 AI 并发下 AuditTrail 写入瓶颈 | 中 | 高 | 需确认 AuditTrail 容量升级方案 | 风险 |
| 3 | GPU 共识排队延迟突破 SLO | 中 | 高 | GPU 排队+API fallback+优先级插队 | 风险 |
| 4 | SQLite WAL 模式下 100 Session 并发锁竞争 | 中 | 中 | 主线程代理写入+连接池复用 | 风险 |
| 5 | 跨蓝图容量对齐未验证（7 项 ⚠️） | 高 | 高 | 逐项确认上游模块容量方案 | 风险 |
| 6 | 事件流实时监听增加系统延迟（p99 < 10s） | — | 中 | AdmissionControl 限流+DualModeEngine 三通道 | 负面后果 |
| 7 | 多模型共识增加 API 成本（每次 ~1500 tokens） | — | 中 | local_first 策略+GPU 排队+API fallback | 负面后果 |
| 8 | 100 AI 并发容量升级需要上游模块协同（7 项待确认） | — | 高 | 逐项确认上游模块容量方案 | 负面后果 |
| 9 | SQLite 单写者限制写入吞吐 | — | 中 | 主线程代理写入+连接池复用 | 负面后果 |

---

## §16 施工指引

> 时态属性：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 代码头部 BLUEPRINT 引用已修正为 MOD-INF-033 | Grep 确认 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 Phase |
| 施工模式 | 扩展（已有 54 模块基础上新增核心组件） |
| 核心风险 | 代码头部 BLUEPRINT 引用漂移（MOD-INF-023→MOD-INF-033） |
| 目标 generation | 3 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | AuditTrail 事件流可用 | hard | ✅ | ✅ |
| 2 | Gate Engine 许可矩阵 API 可用 | hard | ✅ | ✅ |
| 3 | 代码头部 BLUEPRINT 引用修正 | hard | ❌ 待修正 | ☐ |
| 4 | 上游模块容量方案确认（7 项 ⚠️） | soft | ❌ 待确认 | ☐ |

### 16.3 实施步骤

> 时态属性：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> 删除前置条件（缺一不可）：1.代码文件存在且非空 2.pytest exit 0 3.mypy 通过 4.ruff 通过

#### 步骤 1：修正代码头部 BLUEPRINT 引用

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §0.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` |
| 验收标准 | 所有 .py 文件头部 BLUEPRINT 引用为 MOD-INF-033 |
| 验证命令 | `python -c "import pathlib; files=list(pathlib.Path('src/zephyr/behavioral-auditor').glob('*.py')); bad=[f for f in files if 'MOD-INF-023' in f.read_text(encoding='utf-8')]; print(f'BAD: {len(bad)}/{len(files)}'); exit(1 if bad else 0)"` |
| G7 检查项 | 54 文件全部修正、无遗漏、__init__.py __all__ 正确 |

#### 步骤 2：新增 VerdictEngine 核心组件

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\verdict_engine.py` |
| 验收标准 | verify_operation() 输入 AuditTrailEvent→输出 Verdict |
| 验证命令 | `python -m pytest tests/behavioral-auditor/test_verdict_engine.py -v` |
| G7 检查项 | 十五字段头部完整、接口签名与 §4.1 一致、Evidence Chain 完整 |

#### 步骤 3：新增 AdmissionControl + ProtectionIndex

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.1 + §17 缺口 #1/#5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\admission_controller.py` + `protection_index.py` |
| 验收标准 | Token Bucket 限流 50/s、ProtectionIndex O(1) 查询 |
| 验证命令 | `python -m pytest tests/behavioral-auditor/test_admission_control.py tests/behavioral-auditor/test_protection_index.py -v` |
| G7 检查项 | 十五字段头部完整、容量参数与 §17 一致 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | BLUEPRINT 引用替换导致导入错误 | `git checkout -- src/zephyr/behavioral-auditor/` |
| 2 | VerdictEngine 接口不兼容 | 删除 verdict_engine.py，恢复旧导入路径 |
| 3 | AdmissionControl 限流过严 | 调整 Token Bucket rate 参数 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | verdict_engine.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\verdict_engine.py` | ☐ | ☐ | ☐ |
| 2 | admission_controller.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\admission_controller.py` | ☐ | ☐ | ☐ |
| 3 | protection_index.py | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\protection_index.py` | ☐ | ☐ | ☐ |
| 4 | 代码头部修正 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | — |
| verification_status | unverified | — |
| code_alignment_verified | no | — |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| AI 并发 Session | ~5 | 运行时统计 |
| 事件摄入吞吐 | ~5 events/s | AuditTrail 写入速率 |
| 模块数 | 1,623 | registry_of_registries.yaml |
| 脚本数 | 388 | script-manifest.yaml |
| SQLite DB 数 | 4 | 文件系统计数 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 无系统级准入控制 | AdmissionControl Token Bucket 50/s | 100 AI 并发 |
| GAP-002 | CT-BEH-DB-001 契约不完整 | 详细化读写路径/连接池/批量策略 | 100 Session 并发写入 |
| GAP-003 | GPU 共识无排队策略 | GPUConsensusScheduler 优先级队列+API fallback | GPU 繁忙时共识延迟 > 5s |
| GAP-004 | 跨蓝图容量对齐未验证 | 7 项 ⚠️ 上游模块逐项确认 | 容量升级施工前 |
| GAP-005 | ProtectionIndex O(n) glob 匹配 | Bloom Filter+Trie O(1) 索引 | 1,500 模块 |
| GAP-006 | Session 生命周期无 GC | ACTIVE→IDLE→CLOSED→EXPIRED 状态机 | 僵尸 Session 堆积 |
| GAP-007 | 事件吞吐量无逐类型预算 | 按操作类型分配 Token Bucket | 吞吐量不均 |
| GAP-008 | CoT 推理链存储无膨胀控制 | 分级存储+LRU 淘汰+zstd 压缩 | Evidence Store > 1GB |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 事件驱动+许可矩阵+Block/Alert/Rollback | ✅ |
| v2.0.0 | 2 | 全维度 | §0~§29 共 30 章节功能设计 | ⚠️ 部分 |
| v3.0.0 | 3 | 容量升级 | 15 项容量设计（PartitionedConsumer/PerSessionBaseline 等） | ❌ 待施工 |
| v3.1.0 | 3 | 容量审计 | 8 项缺口补全 | ❌ 待施工 |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | 系统级准入控制与过载保护 | P0 | v3.2.0 | 待施工 |
| GAP-002 | CT-BEH-DB-001 契约详细化 | P0 | v3.2.0 | 待施工 |
| GAP-003 | GPU 共识排队与降级 | P1 | v3.2.0 | 待施工 |
| GAP-004 | 跨蓝图容量对齐验证矩阵 | P1 | v3.2.0 | 待确认 |
| GAP-005 | ProtectionIndex 纯内存索引 | P2 | v3.3.0 | 待施工 |
| GAP-006 | Session 生命周期管理与 GC | P2 | v3.3.0 | 待施工 |
| GAP-007 | 事件吞吐量逐类型预算 | P2 | v3.3.0 | 待施工 |
| GAP-008 | CoT 推理链存储膨胀控制 | P2 | v3.3.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| BehavioralAuditorAdmissionController | GAP-001 | admission_controller.py | Phase 1 | 待施工 |
| CT-BEH-DB-001 v2 | GAP-002 | — (契约文档) | Phase 1 | 待施工 |
| GPUConsensusScheduler | GAP-003 | gpu_consensus_scheduler.py | Phase 2 | 待施工 |
| ProtectionIndex | GAP-005 | protection_index.py | Phase 2 | 待施工 |
| SessionLifecycleManager | GAP-006 | session_lifecycle.py | Phase 3 | 待施工 |

---

## §18 决策记录

> 记录蓝图中的关键设计决策。与变更记录不同——变更记录记"改了什么"，决策记录记"为什么这样设计"。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。
> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-BEH-01 | 行为审计独立为模块而非嵌入 Orchestrator | A:嵌入/B:独立 | B | 三审计类型本质不同（结构/语义/行为），行为审计的"不可逆"特性需要独立响应模型 | 2026-05-08 |
| 2 | D-BEH-02 | 高风险判定使用多模型共识 | A:单模型/B:2/2 共识 | B | Anthropic Auditing Agents 研究：多 Agent 聚合提升成功率 13%→42% | 2026-05-08 |
| 3 | D-BEH-03 | 事件摄入使用 Token Bucket 而非队列深度限流 | A:队列深度/B:Token Bucket | B | Token Bucket 主动预防 vs 队列深度被动反应 | 2026-05-10 |
| 4 | D-BEH-04 | GPU 共识使用优先级队列+API fallback | A:纯排队/B:优先级+fallback | B | anchor 文件越权不可等待 GPU，MUST 立即 API fallback | 2026-05-10 |
| 5 | D-BEH-05 | ProtectionIndex 使用 Bloom Filter+Trie 而非纯 glob | A:glob/B:Bloom+Trie | B | 1,500 模块时 glob O(n)→Bloom+Trie O(1)，内存 ~15MB 可忽略 | 2026-05-10 |

---

## 蓝图特有：触发条件全清单

> 来源：v2.0.0 §3 触发条件
> 仅本蓝图需要：BH-* 触发器 ID 体系是 BehavioralAuditor 独有概念
> 不可砍理由：触发器是事件驱动模型的核心——砍掉 = AI 不知道何时触发行为审计

| 触发器 ID | 触发事件 | 数据来源 | 判定逻辑 |
|-----------|---------|---------|---------|
| BH-001 | AuditTrail 记录文件写/删操作 | MOD-INF-020 | 操作者=AI?→目标文件在保护范围?→操作有 Gate 授权? |
| BH-002 | DriftDetector 报告蓝图 vs 实际漂移 | MOD-INF-023 | 回溯 AuditTrail：漂移是 AI 操作造成的吗? |
| BH-003 | AuditTrail 记录跨模块越权操作 | MOD-INF-020 | 操作目标模块在 AI 授权范围内? |
| BH-004 | Session Budget 异常 | MOD-INF-020 | 操作频率异常→熔断 |
| BH-005 | 锚点文件变更事件 | MOD-INF-020 + Gate | 目标文件在锚点保护清单中? |
| BH-006 | A2A 协议冲突 | MOD-INF-025 | 并发写入冲突→判定哪个 Agent 有授权 |
| BH-007 | Gate Engine 被绕过 | MOD-INF-020 | AuditTrail 中 gate_passed=false |
| BH-008 | 行为基线偏离 | §蓝图特有§D | 异常行为模式→YELLOW→深度审查→RED |

---

## 蓝图特有：保护等级与判定决策树

> 来源：v2.0.0 §4 判定模型
> 仅本蓝图需要：保护等级+判定树是 BehavioralAuditor 核心逻辑
> 不可砍理由：砍掉 = AI 无法执行判定

| 保护等级 | 说明 | 越界后果 | 示例文件 |
|---------|------|---------|---------|
| anchor | 不可被 AI 修改/删除 | BLOCK+ALERT+ROLLBACK | project_rules.md、module_registry.yaml |
| protected | AI 可修改但 MUST 经过 Gate | ALERT+事后审计 | blueprint.md、*.yaml |
| normal | AI 可自由操作 | 仅记录到 AuditTrail | tasks/*.json、docs/08_knowledge/** |
| public | 无限制 | 无 | *.log、*.tmp |

判定规则：
- 操作者=human → PASS（记录）
- 操作者=AI + 目标=anchor → RED → BLOCK+ALERT+ROLLBACK（不可覆盖）
- 操作者=AI + 目标=protected + Gate 未通过 → RED → L4+ 渐进响应
- 操作者=AI + 目标=protected + Gate 已通过 → PASS（记录）
- 操作者=AI + 目标=normal + Session 操作数超阈值 → YELLOW → ALERT
- 操作者=AI + 目标=public → PASS（静默记录）
- 跨模块越权 → RED → BLOCK+ALERT
- 行为基线偏离（BH-008）→ YELLOW/RED

---

## 蓝图特有：渐进式响应梯度

> 来源：v2.0.0 §12
> 仅本蓝图需要：L0~L6 七级响应梯度是 BehavioralAuditor 独有设计
> 不可砍理由：砍掉 = AI 不知道如何响应不同等级的越权

| 等级 | 触发条件 | 响应 | 预算消耗 |
|------|---------|------|:---:|
| L0 SILENT_LOG | normal/public 操作无异常 | 静默记录 | 0% |
| L1 SOFT_WARN | protected 文件被 AI 修改（Gate 已通过） | INFO 级+Session 内提示 | 0% |
| L2 HARD_WARN | Session 操作数接近阈值 80% | ALERT（不阻断） | 10% |
| L3 SOFT_BLOCK | normal 操作异常（突发大量写入） | 暂停 30s+CoT 验证 | 25% |
| L4 HARD_BLOCK | protected 文件 Gate 未通过 | BLOCK+ALERT+Escalation | 50% |
| L5 SESSION_FREEZE | anchor 文件被 AI 操作/跨模块越权 | BLOCK+ALERT+ROLLBACK+冻结 Session | 75% |
| L6 AGENT_KILL | 重复越权/绕过 Gate/Gate 配置被篡改 | BLOCK+ALERT(CRITICAL)+ROLLBACK+终止 Agent | 100% |

升级矩阵：L0→L4（protected 被改）、L1→L4（再次修改 protected）、L2→L3（突破阈值）、L3→L4（拒绝解释）、L4→L5（再次越权）、L5→L6（新 Session 重复模式）

冷却：L0~L2=0、L3=30s 自动恢复、L4=5min Owner 确认、L5=Session 结束+Owner 解除、L6=24h Owner 审查

---

## 蓝图特有：多模型共识协议

> 来源：v2.0.0 §11
> 仅本蓝图需要：多模型共识是 BehavioralAuditor 高风险判定的核心机制
> 不可砍理由：砍掉 = anchor 文件越权判定缺少置信度保障

| 条件 | 是否需要多模型共识 |
|------|:---:|
| anchor 等级文件越权 | ✅ 强制 2/2 |
| protected 等级文件越权 | ✅ 建议 2/2（降级为 1/2+Human Review） |
| normal 等级操作异常 | ❌ 单模型即可 |
| public 等级操作 | ❌ 无需多模型 |

共识配置：primary=deepseek-v4-pro，fallback=qwen3:8b，consensus_required=2/2，debate_timeout=30s，on_disagreement=ESCALATE_TO_HUMAN，on_timeout=BLOCK

实际路由（§蓝图特有§H 三阶路由）：高风险→deepseek-v4-pro+claude-sonnet-4（双 API），中风险→deepseek-v4-pro（单 API），低风险→qwen3:8b（本地）

---

## 蓝图特有：Meta-Audit 自审计

> 来源：v2.0.0 §13
> 仅本蓝图需要：自审计是"谁审计审计者"的递归问题
> 不可砍理由：砍掉 = BehavioralAuditor 自身异常无法检测

| 审计项 | 频率 | 验证方式 |
|--------|------|---------|
| 自身 AuditTrail 记录 | 每次判定后 | 检查 BH_VERDICT 事件 |
| 判定延迟 SLO | 每次判定 | verify_operation() < 10s |
| 误报率 | 每周 | Owner 手动审查 vs BehavioralAuditor 判定 |
| 漏报率 | 每周 | DriftDetector 发现的漂移 vs BehavioralAuditor 是否漏判 |
| 多模型共识一致性 | 每次多模型判定 | Primary vs Secondary 一致率 |
| 自身权限 | 每次判定后 | AuditTrail writer ≠ BehavioralAuditor |
| Prompt 版本一致性 | 每次判定 | Prompt hash 校验 |

降级模式：Meta-Audit 失败→停止自主判定→默认 BLOCK→通知 Owner→Fallback 到 SimpleAudit（仅 actor_type 检查）

---

## 蓝图特有：行为基线画像

> 来源：v2.0.0 §14
> 仅本蓝图需要：6 维基线偏离检测是 BH-008 触发器的核心
> 不可砍理由：砍掉 = 无法检测"AI 平时不会这样操作"的异常行为

6 维基线：session_operation_frequency / file_protection_level_distribution / operation_type_distribution / gate_bypass_attempts / cross_module_access_pattern / time_of_day_pattern

更新策略：初始=前 30 Session，更新=每 10 Session，衰减=最近 30 天权重 1.0/30-60 天 0.5/60+ 天 0.1，异常排除=RED 操作不计入基线

---

## 蓝图特有：红队对抗与攻击自生长

> 来源：v2.0.0 §15
> 仅本蓝图需要：红队对抗是 BehavioralAuditor 压力测试机制
> 不可砍理由：砍掉 = 无法验证行为审计的鲁棒性

混沌注入类型（chaos_injector.py 已实现）：路径重命名 / YAML 字段翻转 / 假 TODO 炸弹 / 导入幻觉

红队限速（v3.0.0 §3.15）：max_red_team_per_week=3 / max_chaos_per_session=5 / cooldown_between_red_team=4h

---

## 蓝图特有：反馈闭环（FLE）

> 来源：v2.0.0 §16
> 仅本蓝图需要：FLE 是 BehavioralAuditor 规则自适应的核心
> 不可砍理由：砍掉 = 误报/漏报无法回写规则演进

FLE 流程：BehavioralAuditor 判定→Owner 反馈（误报/漏报）→FLE 分析→规则更新→基线调整→下一轮判定

---

## 蓝图特有：全系统集成矩阵

> 来源：v2.0.0 §17
> 仅本蓝图需要：18 模块连接契约是 BehavioralAuditor 的集成全景
> 不可砍理由：砍掉 = AI 不知道本模块与哪些系统有连接

| 集成模块 | 契约 ID | 集成方式 | 状态 |
|---------|---------|---------|:---:|
| AuditTrail (MOD-INF-020) | CT-BEH-AT-001 | 事件消费+CRITICAL 写入 | ✅ |
| DriftDetector (MOD-INF-023) | CT-BEH-DRIFT-001 | 漂移信号触发 | ✅ |
| Gate Engine (MOD-GATE_ENGINE) | CT-BEH-GATE-001 | 许可矩阵查询 | ✅ |
| Rollback (MOD-INF-021) | CT-BEH-RB-001 | 回滚调用 | ✅ |
| Escalation (MOD-INF-022) | CT-BEH-ESC-001 | L4+升级通道 | ✅ |
| Feedback Loop (MOD-FEEDBACK_LOOP) | CT-BEH-FLE-001 | 误报/漏报反馈 | ✅ |
| LLM Security (MOD-LLM_SECURITY) | CT-BEH-LLM-001 | Prompt 注入防御 | ✅ |
| Agent RBAC (MOD-INF-018) | CT-BEH-RBAC-001 | 审计权限校验 | ✅ |
| Agent Spec (MOD-INF-019) | CT-BEH-SKILL-001 | SKILL-DOM-BEH-001 | ✅ |
| Budget Enforcer (MOD-INF-024) | CT-BEH-BUDGET-001 | Token 配额管理 | ✅ |
| A2A Protocol (MOD-INF-025) | CT-A2A-BEH-001 | 多 Agent 冲突仲裁 | ✅ |
| System Telemetry (MOD-INF-015) | CT-BEH-TELE-001 | SLI/SLO 推送 | ✅ |
| Asset Inventory (MOD-INF-026) | CT-BEH-ASSET-001 | 保护目标清单 | ✅ |
| Database (MOD-DATABASE) | CT-BEH-DB-001 | SQLite 读写 | ✅ |
| AuditOrchestrator (MOD-INF-027) | CT-BEH-AO-001 | dispatch 路由 | ✅ |
| SemanticAuditor (MOD-INF-028) | CT-SEM-BEH-001 | 平级协同 | ✅ |
| RedBlue Validator (MOD-INF-030) | CT-BEH-RB-002 | 红蓝对抗协同 | ✅ |
| AutoFix Engine (MOD-INF-031) | CT-BEH-AF-001 | 回滚后修复 | ✅ |

---

## 蓝图特有：可观测性与 SLO

> 来源：v2.0.0 §18
> 仅本蓝图需要：SLI/SLO 定义是 BehavioralAuditor 运维核心
> 不可砍理由：砍掉 = 无法衡量行为审计是否正常工作

| SLI | SLO | 测量方式 |
|-----|-----|---------|
| 判定延迟 p99 | < 10s | verify_operation() 耗时 |
| 判定可用性 | > 99.9% | 判定成功/总请求数 |
| anchor 文件越权阻断率 | 100% | RED 判定/anchor 越权事件 |
| 误报率 | < 5% | Owner 反馈误报/总 RED 判定 |
| 漏报率 | < 1% | DriftDetector 发现的未判定漂移 |
| 多模型共识一致率 | > 95% | 2/2 一致/总共识判定 |

---

## 蓝图特有：CLI+MCP 双入口

> 来源：v2.0.0 §22
> 仅本蓝图需要：CLI+MCP 是 BehavioralAuditor 的操作入口
> 不可砍理由：砍掉 = AI 不知道如何调用行为审计

CLI 入口：`python -m zephyr.behavioral_auditor scan [--level LIGHT/STANDARD/DEEP]` / `self-test` / `budget [module_id]` / `list` / `status`

MCP Tools：behavioral_audit_check / behavioral_audit_baseline / behavioral_audit_health

---

## 蓝图特有：合规映射

> 来源：v2.0.0 §23
> 仅本蓝图需要：合规映射是 BehavioralAuditor 的合规价值证明
> 不可砍理由：砍掉 = 无法证明行为审计满足合规要求

| 合规标准 | 对应章节 | BehavioralAuditor 覆盖 |
|---------|---------|----------------------|
| ISO 27001 A.12.4 事件日志 | §5 Evidence Chain | 不可变审计日志+证据链 |
| SOC 2 CC6.1 逻辑访问 | §4 保护等级+许可矩阵 | 授权边界监控 |
| GDPR Art.32 安全处理 | §8 安全边界+§19 熔断 | 行为审计+降级保护 |

---

## 蓝图特有：项目规则协议集成

> 来源：v2.0.0 §24
> 仅本蓝图需要：RULE-ZERO~NINE 对齐是 BehavioralAuditor 遵守项目硬规则的证明
> 不可砍理由：砍掉 = 无法证明行为审计遵守项目规则

| 规则 | BehavioralAuditor 对齐 |
|------|----------------------|
| RULE-ZERO 写入文件锁 | BehavioralAuditor 写入 AuditTrail 前检查锁状态 |
| RULE-ONE 原子写入 | 所有 SQLite 写入使用 temp-file+os.replace() |
| RULE-THREE 安全删除 | 删除判定→RULE-THREE 三步审判 |
| RULE-FOUR 搜索先行 | 新增触发器前搜索已有触发器 |
| RULE-FIVE 零残留 | 临时审计文件 Session 结束前清理 |
| RULE-SEVEN ThreadPoolExecutor | 批量判定使用线程池 |
| RULE-EIGHT 搜索先行 | 新增检测器前搜索已有检测器 |

---

## 蓝图特有：Session 连续性

> 来源：v2.0.0 §25
> 仅本蓝图需要：跨 Session 行为审计上下文传递是 BehavioralAuditor 的状态管理核心
> 不可砍理由：砍掉 = 新 Session 丢失历史行为上下文

Session 状态持久化：behavioral_audit_session.db（Trust Tier/escalation_level/操作计数/基线快照 hash）

跨 Session 传递：新 Session 启动→从 SQLite 恢复 behavioral_audit_session→加载基线→继续审计

---

## 蓝图特有：Prompt 版本锁定

> 来源：v2.0.0 §27
> 仅本蓝图需要：Prompt 版本锁定是判定确定性的保障
> 不可砍理由：砍掉 = Prompt 变化导致判定结果不可复现

锁定 Prompt：BEH-PROMPT-VERDICT-V1 / BEH-PROMPT-MULTI-MODEL-V1 / BEH-PROMPT-BASELINE-V1

变更流程：KB 决策记录→Prompt Regression Test→Owner Approval→Version Bump

Token 预算：单模型≤500 / 多模型≤1500 / 基线分析≤2000 / 红队≤2000 / 反馈分析≤1000

---

## 蓝图特有：氛围编程全自动化

> 来源：v2.0.0 §28
> 仅本蓝图需要：一人+AI 语境下的零人工干预设计
> 不可砍理由：砍掉 = Owner 不知道行为审计可以全自动运行

全自动流水线：①触发（AuditTrail 事件流+DriftDetector+Cron）→②判定（单模型/多模型共识）→③响应（L0~L3 全自动/L4~L5 阻断+通知/L6 终止+通知）→④记录（AuditTrail+Evidence Chain）→⑤闭环（FLE+红队+基线更新+Meta-Audit）→⑥报告（每周自动+异常推送）

Cron 调度：realtime（事件驱动）/ hourly_batch / daily_report(8:00) / weekly_baseline(周日 3:00) / monthly_cost(每月 1 号 9:00)

---

## 蓝图特有：容量升级详细设计

> 来源：v3.0.0 §3.1~§3.15 + v3.1.0 缺口 #1~#8
> 仅本蓝图需要：15+8 项容量设计是 100 AI 并发的技术方案
> 不可砍理由：砍掉 = 容量升级施工时无设计依据

### v3.0.0 容量升级 15 项设计

| # | 组件 | 设计要点 |
|---|------|---------|
| 3.1 | PartitionedConsumer | 8 分片并行消费，队列深度 500，>80% 通知 Coalescer |
| 3.2 | Per-Session Baseline | Session 级行为基线隔离，独立写，主线程串行化提交 |
| 3.3 | ShardedSessionStore | Session 状态分片存储，按 session_id hash 分片 |
| 3.4 | TieredEvidenceStore | Hot(内存 LRU 1000)→Warm(SQLite)→Cold(zstd 压缩归档) |
| 3.5 | Multi-Model Token 重校准 | Per-Session Token 配额，local_first 策略 |
| 3.6 | SampledMetaAudit | 采样批处理，默认采样率 10% |
| 3.7 | AggregatedMetrics | Prometheus 指标聚合，标签基数上限 100 |
| 3.8 | TieredCircuitBreaker | Session 级+依赖级双层熔断 |
| 3.9 | TrustTieredAudit | TX_HIGH/TX_MEDIUM/TX_LOW 三级信任审计 |
| 3.10 | DualModeEngine | REALTIME(<100ms)+MICROBATCH(2s)+DEFER(10s) 三通道 |
| 3.11 | LocalPermissionCache | 许可矩阵本地缓存，TTL 5s，命中率 >95% |
| 3.12 | SharedBlueprintCache | 多 Session 共享蓝图缓存 |
| 3.13 | AnchorAccessBroadcastBus | 锚点文件访问实时广播 |
| 3.14 | HardwareAwareCostModel | 硬件感知成本模型，GPU 串行+API 并发 |
| 3.15 | RateLimitedRedTeam | 红队自生长限速，每周 3 次 |

### v3.1.0 缺口补全 8 项设计

| # | 缺口 | 设计要点 |
|---|------|---------|
| 1 | 系统级准入控制 | AdmissionControl Token Bucket rate=50/s burst=100 + Admission CB |
| 2 | CT-BEH-DB-001 契约详细化 | 4 SQLite DB 读写路径/连接池(44)/批量策略/Session 隔离 |
| 3 | GPU 共识排队与降级 | GPUConsensusScheduler 4 级优先级+API fallback+CPU 降级 |
| 4 | 跨蓝图容量对齐矩阵 | 7 项 ⚠️ 上游模块容量兼容性待确认 |
| 5 | ProtectionIndex 纯内存索引 | Bloom Filter+Trie O(1) 查询，~15MB 内存 |
| 6 | Session 生命周期 GC | ACTIVE→IDLE(30min)→CLOSED(24h)→EXPIRED(90d) |
| 7 | 事件吞吐量逐类型预算 | 按操作类型分配 Token Bucket |
| 8 | CoT 存储膨胀控制 | 分级存储+LRU 淘汰+zstd 压缩 |

### 容量 SLI 重校准

| SLI | v2.0.0 SLO | v3.0.0 SLO | 变更原因 |
|-----|-----------|-----------|---------|
| 判定延迟 p99 | < 10s | < 10s | 不变 |
| 事件摄入吞吐 | ~5/s | 50/s | 100 AI 并发 |
| Session 并发 | ~5 | 100 | 容量升级 |
| SQLite 连接 | ~10 | 44 | 4 DB×11 |

### 3 Phase 施工路线

| Phase | 内容 | 前置条件 | 预计工期 |
|-------|------|---------|---------|
| Phase 1 | VerdictEngine+AdmissionControl+ProtectionIndex+代码头部修正 | AuditTrail+Gate Engine 可用 | 2 周 |
| Phase 2 | MultiModelConsensus+GPUConsensusScheduler+容量组件(3.1~3.8) | Phase 1 完成 | 3 周 |
| Phase 3 | 剩余容量组件(3.9~3.15)+缺口补全(#5~#8)+集成测试 | Phase 2 完成 | 3 周 |

---

## 蓝图特有：维度补齐验证

> 来源：v2.0.0 §29
> 仅本蓝图需要：一阶~N 阶全维度覆盖确认
> 不可砍理由：砍掉 = 无法证明设计无盲点

| 阶 | 维度 | 覆盖章节 | 状态 |
|:---:|------|:---:|:---:|
| 一阶 | 核心判定引擎+触发条件+响应模型+Provider 复用 | §1-§6 | ✅ |
| 二阶 | 冷启动+Agent Skill+CLI/MCP+多模型共识+渐进响应+基线+集成矩阵+规则对齐 | §0/§10/§22/§11/§12/§14/§17/§24 | ✅ |
| 三阶 | Meta-Audit+FLE+可观测性+Session 连续性+Prompt 锁定+全自动化 | §13/§16/§18/§25/§27/§28 | ✅ |
| 四阶 | 红队对抗+熔断降级+灾难恢复+成本感知 | §15/§19/§20/§21 | ✅ |
| 五阶 | 合规映射+蓝图自健康诊断 | §23/§26 | ✅ |
| 六阶 | 三审计交叉验证+Orchestrator 协同 | §1.1/§7 | ✅ |
| 七阶 | 全系统 18 模块集成+CT-* 契约对齐 | §17 | ✅ |
| N 阶 | 未来新子系统接入自动扩展 | FLE 自适应 | ✅ 框架就绪 |

---

## 蓝图特有：Orchestrator 集成 dispatch 协议

> 来源：v2.0.0 §7
> 仅本蓝图需要：dispatch 协议定义 Orchestrator 如何路由到 BehavioralAuditor
> 不可砍理由：砍掉 = Orchestrator 不知道如何调度行为审计

```yaml
behavioral_audit_dispatch:
  trigger:
    source: MOD-INF-020.AuditTrail
    event_types: [file_write, file_delete, permission_change, anchor_file_modify, gate_bypass]
    filter:
      actor_type: ai_agent
  dispatch:
    target: MOD-INF-033.BehavioralAuditor
    method: verify_operation(event_context)
    timeout_seconds: 10
    on_timeout: BLOCK
```

调度顺序：1.结构审计先行（批量）→ 2.语义审计按需 → 3.行为审计实时（事件流，持续监听）

---

## 蓝图特有：冷启动分派

> 来源：v2.0.0 §0
> 仅本蓝图需要：冷启动分派是新 AI Session 发现本模块的入口
> 不可砍理由：砍掉 = 新 AI 不知道如何使用 BehavioralAuditor

6 条发现路径：①SYS-MASTER-001 §0 分派表→MOD-INF-033 ②registry_of_registries.yaml→搜索"behavioral" ③Agent Spec 关键词路由→SKILL-DOM-BEH-001 ④project_rules.md PRE-OP 表 ⑤cross_layer/index.md 模块清单 ⑥CLI 入口自描述

冷启动序列：读本蓝图 §1-§9 → §10 Agent Skill → §17 集成矩阵 → §24 规则对齐 → §28 全自动化 → `python -m zephyr.agent_spec progressive_load SKILL-DOM-BEH-001` → `python -m zephyr.behavioral_auditor status`

触发关键词：behavioral / 越权 / behavior audit / 行为边界 / AI安全审计 / 操作越界 / 未经授权

---

## ⚠️ Vibe Coding 蓝图编写铁律

> 时态属性：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 虚假进度 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容（架构/接口/约束/当前状态） | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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
| 容量保障蓝图中"执行层设计"（18个CAP-G需求+28个SLO） | **拆分** | 独立CAP-G前缀 + 独立Phase + 独立SLO体系 + 与主体depends_on交集<30% |
| 容量保障蓝图中"Error Budget五级响应" | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 容量保障蓝图中"容量预测模型" | **原地** | 预测是容量保障的核心能力，不是独立子系统 |

---

## ⚠️ 安全删除协议

> 时态属性：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 安全删除方案 |
|---|---------------|------------|---------|------------|
| 1 | 代码头部 BLUEPRINT 引用 MOD-INF-023 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` | 覆盖型 | 批量替换为 MOD-INF-033 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> 时态属性：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012+MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 蓝图模板 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\templates\blueprint-template.md` | 章节结构标准 |
| 10 | 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 规格化标准 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | DriftDetector (MOD-INF-023) | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\drift_engine.py` | 漂移检测+事件驱动 | DriftDetector 检测状态变化，BehavioralAuditor 判定操作是否越权——判定逻辑不同 |
| 2 | AuditTrail (MOD-INF-020) | `D:\ZephyrAlpha\src\zephyr\audit-trail\` | 不可变操作日志 | AuditTrail 只记录，不做判定——许可矩阵比对是 BehavioralAuditor 独有 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 业务代码目录 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\` | 修改 | 代码头部 BLUEPRINT 引用修正+新增组件 |
| 2 | 测试目录 | `D:\ZephyrAlpha\tests\behavioral-auditor\` | 修改 | 新增测试用例 |
| 3 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\behavioral-auditor\blueprint.md` | 修改 | 本文件 |
| 4 | Agent Skill | `D:\ZephyrAlpha\src\zephyr\agent-spec\skills\domain\` | 读取 | SKILL-DOM-BEH-001 |
| 5 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | 版本更新 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 行为审计核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 行为审计施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 行为审计接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 触发器 BH-* 定义 | **本文档 蓝图特有：触发条件全清单** | — |
| 渐进式响应 L0~L6 | **本文档 蓝图特有：渐进式响应梯度** | — |

**MOD-INF-033 是行为审计的唯一真源。** MOD-INF-027 审计总控不内建任何行为审计 check。所有行为审计 Finding 由 033 产出，027 仅做路由调度。

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | AuditOrchestrator (MOD-INF-027) | §4 接口契约、§12 集成点 |
| Tier 1 | Gate Engine (MOD-GATE_ENGINE) | §4.3 输入契约 |
| Tier 2 | Escalation Protocol (MOD-INF-022) | 蓝图特有：渐进式响应梯度 |
| Tier 2 | Feedback Loop (MOD-FEEDBACK_LOOP) | 蓝图特有：反馈闭环 |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\behavioral-auditor\*.py` | §4 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§4） | 需 Owner 审批+通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调 | AI 可自主修改 |
| 非关键补充 | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |
