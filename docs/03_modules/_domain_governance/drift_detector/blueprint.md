---
module_id: MOD-INF-023
title: "Drift Detector 蓝图 — 39检测器漂移检测引擎与10状态漂移生命周期"
doc_type: blueprint
status: Active
version: "3.1.0"
layer: L1_foundation
layer_name: cross_layer
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-05
submodule_path: src/zephyr/governance/drift_detection/
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/governance/drift_detection/; src/zephyr/governance/drift_detector_core/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-13"
last_verified: "2026-05-14"
last_updated: "2026-05-15"
generation: 4
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
references:
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\engineering\\code-construction-standards.md"
    section: §7
    why: 代码文件十五字段头部标准
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\04_architecture_principles_decisions\\dependency_path_panorama.md"
    section: 线3
    why: 治理闭环依赖图
depends_on:
  - target: MOD-INF-021
    at: §10
    why: 漂移→回滚桥接
  - target: MOD-INF-022
    at: §10
    why: 漂移预算耗尽升级
  - target: MOD-INF-020
    at: §10
    why: 漂移事件审计
  - target: MOD-INF-018
    at: §10
    why: 检测器权限控制
  - target: MOD-GATE_ENGINE
    at: §10
    why: 门禁持久化
  - target: MOD-INF-016
    at: §10
    why: AiAuditLogger + AbstractLock
  - target: MOD-DATABASE
    at: §10
    why: 基线+漂移结果持久化
priority: P1
tags:
  - drift-detection
  - behavioral-auditor
  - baseline-snapshot
  - drift-state-machine
  - incremental-scan
  - auto-reconciliation
  - drift-budget
  - alert-routing
  - drift-forensics
  - chaos-injection
  - tamper-proof-audit
  - cascade-detection
summary: >
  39检测器漂移检测引擎+10状态漂移生命周期+基线快照+自动对账+漂移预算+告警路由+混沌注入+漂移取证+防篡改审计。54文件，4Phase全部完成，红白对抗验证通过。

---

> module_id: MOD-INF-023 | version: 3.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/governance/drift_detection/ + src/zephyr/governance/drift_detector_core/ | generation: 4 | construction_progress: partially_implemented

# Drift Detector 蓝图+施工图 — 39检测器漂移检测引擎与10状态漂移生命周期

## 概述

本蓝图描述 ZephyrAlpha 漂移检测体系——它解决了 100% AI 施工场景下的代码/配置/架构漂移无感知问题。核心职责包括：39 检测器并行调度、10 状态漂移生命周期管理、基线快照与自动对账、漂移预算与施工门禁、告警路由与疲劳管理、混沌注入与红白对抗验证。当前规模 54 文件 39 检测器，目标容量 1500 模块 DEEP scan。上游依赖 MOD-INF-021 Rollback（漂移→回滚桥接）和 MOD-INF-022 Escalation（预算耗尽升级），下游被 MOD-GOVERNANCE 治理域蓝图和所有 AI 施工 session 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

> 防止 construction_progress 与实际代码不符。
> 每次蓝图版本变更后**必须**重新填写此表。
> **位置说明**：§0 放在概述之后——AI 进入蓝图先建立心理模型（概述），再确认文件现状（§0），再理解设计（§1-§14）。

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`

> 列出蓝图描述的**所有代码文件**。此清单 = 代码目录下的实际文件列表。
> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-023`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | drift_engine.py | §3 | 漂移检测引擎主类 | 已实现 | |
| 2 | state_machine.py | §3 2.3 | 漂移状态机 | 已实现 | |
| 3 | baseline_manager.py | §3 2.2 | 基线快照管理器 | 已实现 | |
| 4 | reconciler.py | §3 2.5 | 自动对账器 | 已实现 | |
| 5 | detector_dispatcher.py | §3 2.4 | 检测器调度器 | 已实现 | |
| 6 | incremental_scanner.py | §3 2.4 | 增量扫描器 | 已实现 | |
| 7 | correlation_engine.py | §3 6.2 | 关联分析引擎 | 已实现 | |
| 8 | trend_analyzer.py | §3 6.1 | 趋势分析器 | 已实现 | |
| 9 | roi_engine.py | §3 | ROI 优先级引擎 | 已实现 | |
| 10 | git_bisector.py | §3 6.7 | 漂移溯源器 | 已实现 | |
| 11 | runbook_generator.py | §3 6.9 | 演练手册生成器 | 已实现 | |
| 12 | ai_context_injector.py | §3 6.8 | AI 上下文注入器 | 已实现 | |
| 13 | chaos_injector.py | §3 6.13 | 混沌漂移注入器 | 已实现 | |
| 14 | handoff_manager.py | §3 6.14 | Session 交接管理器 | 已实现 | |
| 15 | canary_controller.py | §3 6.11 | 金丝雀部署控制器 | 已实现 | |
| 16 | cascade_detector.py | §3 6.15 | 级联故障检测器 | 已实现 | |
| 17 | resource_guard.py | §3 6.16 | 资源上限守护 | 已实现 | |
| 18 | forensics_engine.py | §3 6.17 | 漂移取证引擎 | 已实现 | |
| 19 | drift_models.py | §4 | 数据模型 | 已实现 | |
| 20 | self_check.py | §3 2.7 | 自漂移检测 | 已实现 | |
| 21 | dashboard.py | §3 6.3 | 覆盖率仪表板 | 已实现 | |
| 22 | alert_router.py | §3 2.21 | 告警路由器 | 已实现 | |
| 23 | orphan_scanner.py | §3 2.16 | 孤儿资源扫描器 | 已实现 | |
| 24 | symlink_checker.py | §3 2.17 | 符号链接检查器 | 已实现 | |
| 25 | file_attr_checker.py | §3 2.18 | 文件属性检查器 | 已实现 | |
| 26 | test_fixture_checker.py | §3 6.20 | 测试夹具漂移检测器 | 已实现 | |
| 27 | config_consistency.py | §3 6.21 | 配置多源一致性 | 已实现 | |
| 28 | python_compat.py | §3 6.22 | Python 版本兼容性检测器 | 已实现 | |
| 29 | backcompat_checker.py | §3 6.23 | 向后兼容性检测器 | 已实现 | |
| 30 | gitignore_auditor.py | §3 6.24 | .gitignore 审计器 | 已实现 | |
| 31 | baseline_poisoning_guard.py | §3 6.25 | 基线投毒防护 | 已实现 | |
| 32 | tamper_proof_audit.py | §3 6.26 | 防篡改审计 | 已实现 | |
| 33 | naming_magic_checker.py | §3 6.27 | 命名约定/魔数检测器 | 已实现 | |
| 34 | cold_start.py | §3 2.19 | 冷启动引导器 | 已实现 | |
| 35 | absence_manager.py | §3 2.20 | Owner 缺席管理器 | 已实现 | |
| 36 | credibility_engine.py | §3 2.21 | 告警可信度评分引擎 | 已实现 | |
| 37 | gate_persistence.py | §12 | 门禁持久化 | 已实现 | |
| 38 | headless_scanner.py | §3 | Headless 扫描器 | 已实现 | |
| 39 | cross_module_score.py | §3 | 跨模块健康度评分 | 已实现 | |
| 40 | integration_test_runner.py | §3 6.27 | 集成测试运行器 | 已实现 | |
| 41 | self_test_verifier.py | §9 | 自测验证器 | 已实现 | |
| 42 | drift_hotfix_bypass.py | §3 2.12 | 热修复绕过 | 已实现 | |
| 43 | scan_mutex.py | §3 2.15 | 扫描互斥锁 | 已实现 | |
| 44 | suppression_learner.py | §3 2.14 | 假阳性学习 | 已实现 | |
| 45 | ai_construction_detectors.py | §3 6.6 | AI 施工检测器 | 已实现 | |
| 46 | drift_cron_scheduler.py | §3 | 定时扫描调度 | 已实现 | |
| 47 | drift_infrastructure.py | §3 | 基础设施工具 | 已实现 | |
| 48 | drift_result_types.py | §4 | 结果类型定义 | 已实现 | |
| 49 | drift_training.py | §3 6.12 | 漂移训练数据闭环 | 已实现 | |
| 50 | brain_integration.py | §12 | Agent 生命周期集成 | 已实现 | |
| 51 | rollback_bridge.py | §10 G-CT-005 | 回滚桥接 | 已实现 | |
| 52 | events.py | §4 | 漂移事件+异常类 | 已实现 | |
| 53 | __init__.py | — | 包初始化 | 已实现 | |
| 54 | __main__.py | — | CLI 入口 | 已实现 | |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 代码文件清单存在（部分已实现） | `ls D:\ZephyrAlpha\src\zephyr\governance\drift_detection\` 逐文件核对 | ✅ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" D:\ZephyrAlpha\src\zephyr\governance\drift_detection\*.py` | ✅ |
| actual_disk_path = §11 业务代码路径 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\` 存在 | ✅ |
| 红白对抗验证通过 | `python tests/infrastructure/drift_red_blue_adversarial.py`（独立脚本，非pytest） | ✅ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | 54 文件 + 39 检测器 + G-CT-005/G-CT-006 契约 | — | — |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 新增§0/§16/§17/§18 + 章节重排 + Layer 2 压缩 | — | 结构重组，无功能变更 |
| v3.0.0 (模板v3.5/v3.6升级) | 同 v2.0.0 + §0前移 + §7/§15删除 + §10拆分 + 铁律#13~#15 + 时态属性 | — | 模板升级，无功能变更 |
| v3.1.0 (回填+压缩) | 同 v3.0.0 + 回填18个缺失模板章节 + 压缩临时时态内容 | — | 模板合规，无功能变更 |

### §0.4 SSoT 声明

| 内容 | 本蓝图是否真源 | 非真源时真源位置 | 说明 |
|------|:-------------:|----------------|------|
| 39 检测器维度清单（D1-D31） | ✅ 是 | — | 无其他蓝图定义此维度清单 |
| 漂移检测核心策略（2.1-2.21） | ✅ 是 | — | 无其他蓝图定义此策略集 |
| 漂移分析高级策略（6.1-6.27） | ✅ 是 | — | 无其他蓝图定义此策略集 |
| 10 状态漂移生命周期 | ✅ 是 | — | 无其他蓝图定义此状态机 |
| `src/zephyr/governance/drift_detection/` + `drift_detector_core/` 代码 | ✅ 是 | — | MOD-INF-033 已改 actual_disk_path 为 behavioral_audit/，双包路径冲突已消除（ARCH-042 裁定双包并存） |
| `src/zephyr/drift-detector/` 代码 | ✅ 已清理 | — | 消费者已迁移至 drift_detection |

### §0.5 代码目录唯一性声明

| 声明项 | 状态 | 详情 |
|--------|:----:|------|
| `actual_disk_path` 无冲突 | ✅ 无冲突 | MOD-INF-033 已改为 `behavioral_audit/`，本蓝图覆盖 `drift_detection/` + `drift_detector_core/`（ARCH-042 双包并存） |
| 代码副本存在 | ✅ 已清理 | 消费者已迁移至 drift_detection |
| 代码头部一致性 | ✅ 已修复 | 全部 `[BLUEPRINT]` 头部已统一为 MOD-INF-023 |

---

## §1 设计背景与目标

### 1.1 背景

漂移检测（Drift Detection）是 ZephyrAlpha 治理闭环的核心感知层。100% AI 施工场景下，代码/配置/架构的缓慢漂移是确定性威胁——AI 每个 session 有自己的"风格偏好"，跨 session 积累导致系统偏离设计意图。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 漂移检测覆盖率 | 39 检测器覆盖 31 维度，检测率 100%（红白对抗验证） |
| 2 | ✅ 包含 | 漂移生命周期管理 | 10 状态机完整闭环，DEAD_LETTER 升级率 < 5% |
| 3 | ✅ 包含 | 扫描性能 | LIGHT < 5s / STANDARD < 30s / DEEP < 5min（1500 模块） |
| 4 | ✅ 包含 | 自动对账成功率 | 可自动修复漂移的修复率 > 80%，回滚验证 100% 通过 |
| 5 | ✅ 包含 | 告警信噪比 | 假阳性率 < 10%（suppression_learner 自动抑制） |
| 6 | ✅ 包含 | 基线完整性 | 基线投毒检测率 100%，链式 hash 校验 0 不匹配 |
| 7 | ❌ 排除 | 回滚执行 | → MOD-INF-021 Rollback |
| 8 | ❌ 排除 | 升级决策 | → MOD-INF-022 Escalation Engine |
| 9 | ❌ 排除 | 审计日志存储 | → MOD-INF-020 Audit Trail |
| 10 | ❌ 排除 | 权限控制 | → MOD-INF-018 Agent RBAC |
| 11 | ❌ 排除 | 门禁判定 | → MOD-GATE_ENGINE Gate Engine |
| 12 | ❌ 排除 | 数据持久化基础设施 | → MOD-DATABASE DB |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| Windows 单机部署 | SQLite WAL 足够，无需分布式协调 |
| 1人+AI 运维 | 告警疲劳是最大 operational risk，必须自动抑制 |
| 39 检测器全部执行 | 不可跳过检测器（[INVARIANTS]） |
| 512MB 内存 / 2GB 磁盘上限 | resource_guard 四级优雅降级 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 + 漂移预算审批 | 设计+施工 | 审批权限 |
| AI 施工者 | 漂移检测+自动对账执行 | 施工 | AI_AUTONOMY 约束 |
| MOD-INF-021 Rollback | 漂移→回滚桥接 | 运行 | G-CT-005 契约 |
| MOD-INF-022 Escalation | 预算耗尽升级 | 运行 | G-CT-006 契约 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 检测覆盖率 | 39 检测器 31 维度 | 60+ 检测器全覆盖 | 新增检测器 | P2 |
| 扫描性能 | STANDARD < 30s | DEEP < 5min (1500模块) | 规模验证 | P1 |
| 自动对账率 | > 80% | > 90% | 假阳性抑制 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| post-commit 增量扫描 [未实现] | git commit (需配置 git hook) | scan_mutex→LIGHT scan→检测器执行→告警 | ScanResult |
| 漂移预算耗尽 | 未解决漂移≥预算 | 阻断新施工→G-CT-006升级→Owner通知 | 阻断事件 |
| 基线投毒检测 | DEEP scan | 交叉验证→多基线投票→链式hash校验 | 投毒告警 |
| 级联修复循环 | 30min内3次循环 | 锁定自动修复1h→P0告警→forensics | 锁定事件 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 39 检测器调度执行 | detector_dispatcher 并行调度 + SLO 监控 | 本模块 |
| 2 | ✅ 包含 | 漂移生命周期管理 | 10 状态机（DETECTED→TRIAGED→...→VERIFIED） | 本模块 |
| 3 | ✅ 包含 | 基线快照管理 | 拍摄/存储/对比/版本化 + 投毒防护 | 本模块 |
| 4 | ✅ 包含 | 自动对账与修复 | pre-fix 快照 + 乐观并发 + rollback 验证 | 本模块 |
| 5 | ✅ 包含 | 漂移预算与施工门禁 | SRE 式错误预算，耗尽阻断新施工 | 本模块 |
| 6 | ✅ 包含 | 告警路由与疲劳管理 | 分级通知 + 去重 + 聚合 + 静默 + 可信度评分 | 本模块 |
| 7 | ✅ 包含 | 趋势分析与关联引擎 | velocity / resolution_rate / MTTR + 共现矩阵 | 本模块 |
| 8 | ✅ 包含 | 混沌注入与红白对抗 | 主动注入 + 自动回滚 + 检测器健康验证 | 本模块 |
| 9 | ✅ 包含 | 漂移取证与防篡改 | 时间点回放 + append-only events + Git AUDIT | 本模块 |
| 10 | ✅ 包含 | 冷启动与 Owner 缺席 | bootstrap scan + LENIENT/SURVIVAL 模式 | 本模块 |
| 11 | ❌ 排除 | 回滚执行 | 漂移→回滚桥接，不执行回滚 | MOD-INF-021 Rollback |
| 12 | ❌ 排除 | 升级决策 | 预算耗尽升级，不做升级决策 | MOD-INF-022 Escalation Engine |
| 13 | ❌ 排除 | 审计日志存储 | 写入审计但不存储 | MOD-INF-020 Audit Trail |
| 14 | ❌ 排除 | 权限控制 | 检测器权限检查但不控制 | MOD-INF-018 Agent RBAC |
| 15 | ❌ 排除 | 门禁判定 | 漂移预算门禁但不判定 | MOD-GATE_ENGINE Gate Engine |
| 16 | ❌ 排除 | 数据持久化基础设施 | 使用 DB 但不维护基础设施 | MOD-DATABASE DB |

---

## §3 架构设计

### 3.1 组件架构

| 组件 | 核心类 | 依赖 | 状态 |
|------|--------|------|:---:|
| drift_engine | DriftEngine | detector_dispatcher, baseline_manager, scan_mutex | ✅ |
| state_machine | DriftStateMachine | drift_events DB | ✅ |
| baseline_manager | BaselineManager | baseline_poisoning_guard | ✅ |
| reconciler | Reconciler | baseline_manager, state_machine | ✅ |
| detector_dispatcher | DetectorDispatcher | _detector-registry.yaml | ✅ |
| incremental_scanner | IncrementalScanner | git diff | ✅ |
| correlation_engine | CorrelationEngine | drift_events DB | ✅ |
| trend_analyzer | TrendAnalyzer | drift_events DB | ✅ |
| alert_router | AlertRouter | credibility_engine | ✅ |
| roi_engine | ROIEngine | drift_events DB | ✅ |
| chaos_injector | ChaosInjector | canary_controller | ✅ |
| cascade_detector | CascadeDetector | state_machine | ✅ |
| resource_guard | ResourceGuard | psutil | ✅ |
| forensics_engine | ForensicsEngine | git, drift_events DB | ✅ |
| tamper_proof_audit | TamperProofAudit | drift_events DB, git | ✅ |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | cron / post-commit / 手动 | scan_mutex 加锁 → detector_dispatcher 调度 39 检测器 → 汇总结果 | drift_events DB | ScanResult |
| 2 | drift_events DB | correlation_engine 共现矩阵 + 因果链 | trend_analyzer | CorrelationReport |
| 3 | 新漂移事件 | alert_router 分级通知 + 去重 + 聚合 | Owner / AI session | AlertMessage |
| 4 | 可自动修复漂移 | reconciler pre-fix 快照 → 修复 → 验证 → rollback | state_machine | ReconcileResult |
| 5 | DEEP scan 完成 | tamper_proof_audit SHA256 checksum + Git commit | data/drift_audit/ | AuditManifest |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| DETECTED | 自动/人工确认 | TRIAGED | severity 已评定 |
| TRIAGED | 自动对账启动 | RECONCILING | auto_fixable=true |
| TRIAGED | 人工修复启动 | FIXING | auto_fixable=false |
| RECONCILING | 对账成功 | FIXING | pre-fix 快照已保存 |
| FIXING | 修复完成 | RESOLVED | 修复验证通过 |
| FIXING | 修复失败 | DETECTED | rollback 已执行 |
| RESOLVED | 下次 scan 验证 | VERIFIED | baseline 已更新 |
| RESOLVED | 超时未验证 | DEAD_LETTER | 超过 TTL |
| DEAD_LETTER | Owner 介入 | TRIAGED | Owner 确认 |
| VERIFIED | — | — | 终态 |

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。

### 4.1 公共 API

```python
from pydantic import BaseModel

class DriftEngine:
    """漂移检测引擎主类——编排 39 检测器执行、关联分析、报告生成"""

    async def run_detection(self, scope: list[str] | None = None, level: str = "STANDARD") -> "ScanResult":
        """
        执行漂移检测

        输入：scope=检测范围模块ID列表，level=LIGHT/STANDARD/DEEP
        输出：ScanResult 含检测器执行结果和漂移事件列表
        核心逻辑：scan_mutex 加锁 → detector_dispatcher 调度 39 检测器 → 汇总结果
        """

    def get_drift_report(self, scan_id: str) -> "DriftReport":
        """
        获取漂移检测报告

        输入：scan_id=扫描ID
        输出：DriftReport 含健康指数、Top漂移维度、活跃漂移数
        核心逻辑：从 ScanResult 构建 DriftReport
        """

    def update_baseline(self, module_id: str, force: bool = False) -> "BaselineSnapshot":
        """
        更新基线快照

        输入：module_id=模块ID，force=是否强制更新（跳过投毒检测）
        输出：BaselineSnapshot 新基线快照
        核心逻辑：baseline_poisoning_guard 校验 → baseline_manager 拍摄快照 → 存储
        """
```

### 4.2 数据模型

> 强制 **Pydantic V2 BaseModel**——禁止 `@dataclass`。
> 每个字段必须有类型注解 + Field(description) + 必要时的 validator。
> 枚举类型必须用 `str, Enum`，列出所有合法值。

```python
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional

class DriftSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class DriftResult(BaseModel):
    drift_id: str = Field(..., description="漂移事件唯一ID")
    target: str = Field(..., description="漂移目标路径")
    drift_type: str = Field(..., description="漂移类型")
    severity: DriftSeverity = Field(default=DriftSeverity.MEDIUM, description="严重程度")
    auto_fixable: bool = Field(default=False, description="是否可自动修复")
    fix_suggestion: str = Field(default="", description="修复建议")

    @field_validator("drift_type")
    @classmethod
    def validate_drift_type(cls, v: str) -> str:
        valid = {"CODE_DIVERGENCE", "CONFIG_DRIFT", "SCHEMA_DRIFT", "DEPENDENCY_DRIFT", "INTERFACE_DRIFT"}
        if v not in valid:
            raise ValueError(f"drift_type must be one of {valid}")
        return v

class BaselineSnapshot(BaseModel):
    version: str = Field(..., description="基线版本号")
    tree_hash: dict[str, str] = Field(default_factory=dict, description="文件树哈希映射")
    interface_snapshot: dict[str, str] = Field(default_factory=dict, description="接口快照")
    import_graph: dict[str, list[str]] = Field(default_factory=dict, description="导入依赖图")
    config_snapshot: dict[str, object] = Field(default_factory=dict, description="配置快照")
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `run_detection()` | `scope` | ❌ | list[str]，模块ID列表，None=全量扫描 |
| `run_detection()` | `level` | ❌ | "LIGHT"/"STANDARD"/"DEEP"，默认 STANDARD |
| `get_drift_report()` | `scan_id` | ✅ | str，UUID 格式 |
| `update_baseline()` | `module_id` | ✅ | str，合法模块ID |
| `update_baseline()` | `force` | ❌ | bool，默认 False |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `run_detection()` | `ScanResult`：scan_id + detectors_run + drift_events | `DriftError`：检测器执行异常 |
| `get_drift_report()` | `DriftReport`：health_index + top_dimensions + active_count | `BaselineError`：scan_id 不存在 |
| `update_baseline()` | `BaselineSnapshot`：version + tree_hash + interfaces | `BaselineError`：投毒检测失败 / 基线写入失败 |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |
| MCP 输入 Schema 修改 | ⚠️ 需通知 | 消费者需更新参数 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

### 4.7 OCP 扩展点

| 扩展点 | 基类/接口 | 默认实现 | 扩展契约 | 注册方式 |
|--------|----------|---------|---------|---------|
| 检测器扩展 | `_detector-registry.yaml` 条目 | 39 内置检测器 | YAML 声明式注册：id/name/dimension/severity/auto_fixable/status/script_path/timeout_s | YAML 文件添加条目 |
| 扫描策略扩展 | `IncrementalScanner` | LIGHT/STANDARD/DEEP | 新增扫描级别必须声明 SLO + 触发条件 + 检测器子集 | 代码注册 |

---

## §5 约束条件

### 5.1 技术约束

> 蓝图只保留约束本身。"为什么这样约束"属于决策过程，记录在 §18 决策记录中。

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 3.12+ | type union 语法 `X \| Y` |
| 2 | Pydantic V2 | KBG-0040 |
| 3 | 39 检测器必须全部执行 | [INVARIANTS] |
| 4 | drift_engine.py [STABILITY]=frozen | [AI_AUTONOMY]=immutable_core |
| 5 | 基线更新必须经过投毒防护 | baseline_poisoning_guard |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 检测器数 | 39 | 60 | 100 | ✅ | detector_dispatcher 动态加载 |
| 基线快照数 | 500 | 5000 | 50000 | ✅ | drift_training + 基线压缩 |
| 扫描 QPS | 5 | 20 | 100 | ✅ | 增量扫描 + 并行检测器 |
| 内存 | <384MB | 512MB | 512MB | ✅ | resource_guard 四级降级 |
| 磁盘 | <1GB | 2GB | 2GB | ✅ | GC + VACUUM + 基线压缩 |

### 5.3 迁移/废弃方案

无迁移/废弃。（governance/ 根级 15 孤儿文件迁移已执行完毕，历史见变更记录。）

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 扫描成功率 | > 99.9% | drift_events 记录 | scan_success_rate | > 99.9% | 每月≤1次扫描失败 | 连续2次失败 |
| 性能 | LIGHT扫描延迟 | < 5s | drift_engine 计时 | scan_duration_seconds | LIGHT<5s/STD<30s/DEEP<5min | 每月≤3次SLO违规 | 连续3次超SLO |
| 可维护性 | MTTR | < 30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | `for + subprocess.run()` 串行 | `ThreadPoolExecutor(max_workers=8)` | RULE-SEVEN |
| 2 | 编码模式 | `open(path, "w")` 直接写 | temp-file + `os.replace()` 原子写入 | RULE-ONE |
| 3 | 导入源 | `from zephyr.l00_* import *` | `from zephyr.governance.drift_detection import *` | 分层约束 |
| 4 | 编码模式 | 检测器跳过执行 | 39 检测器必须全部执行 | [INVARIANTS] |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 检测器执行超时 | resource_guard | 终止超时检测器 + 降级扫描 | 部分检测器结果缺失 |
| 2 | 基线投毒 | baseline_poisoning_guard | 拒绝基线更新 + 告警 | 基线不更新 |
| 3 | 扫描互斥冲突 | scan_mutex | 排队等待 + 超时告警 | 扫描延迟 |
| 4 | 关联分析循环 | correlation_engine | 深度限制 + 终止 | 关联结果不完整 |
| 5 | 回滚桥接失败 | rollback_bridge | 降级为仅告警 | 漂移不触发自动回滚 |
| 6 | 混沌注入失控 | canary_controller | 金丝雀终止 + 告警 | 混沌注入被中止 |
| 7 | 级联修复循环 | cascade_detector | 锁定自动修复 1h + P0 告警 | 自动修复暂停 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| drift_scan_duration_seconds | Histogram | drift_engine 自动埋点 | LIGHT>5s / STD>30s / DEEP>5min | P2 |
| drift_events_active_count | Gauge | drift_events DB 查询 | > 50 活跃漂移 | P1 |
| drift_detector_success_rate | Gauge | detector_dispatcher 埋点 | < 95% | P2 |
| drift_budget_remaining | Gauge | drift_engine 计算 | P0模块=0 / P1<1 / P2<3 | P0/P1/P2 |
| drift_baseline_integrity | Gauge | baseline_poisoning_guard | hash 不匹配 | P0 |
| drift_reconcile_success_rate | Gauge | reconciler 埋点 | < 80% | P1 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| baseline_manager | 增量扫描（无基线对比） | 基线对比+投毒检测 | cold_start bootstrap | 基线重建完成 |
| detector_dispatcher | 部分检测器结果 | 全量检测器执行 | 超时检测器跳过+降级扫描 | 资源恢复 |
| reconciler | 仅告警 | 自动修复 | 降级为仅告警模式 | 修复验证通过 |
| alert_router | 日志记录 | 分级通知 | 降级为仅日志 | 通知渠道恢复 |
| trend_analyzer | 当前扫描结果 | 趋势分析 | 降级为无趋势 | 时序数据积累 |
| rollback_bridge | 仅告警 | 自动回滚 | G-CT-005 降级 | MOD-INF-021 恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 基线投毒攻击 | 高 | baseline_poisoning_guard | 测试投毒检测 |
| 2 | 检测器被禁用 | 高 | drift_engine 强制执行 | 测试禁用失败 |
| 3 | 审计记录被篡改 | 高 | tamper_proof_audit | integrity 校验 |
| 4 | 混沌注入影响生产 | 中 | canary_controller + 沙箱 | 测试金丝雀终止 |
| 5 | 过度抑制导致漏检 | 中 | suppression_learner 阈值 | 测试抑制上限 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | drift_engine/baseline_manager/detector_dispatcher | 39 检测器执行 | 覆盖率 > 90% |
| 2 | 集成测试 | 触发→检测→关联→告警链路 | cron 触发→漂移检测→告警 | 端到端通过 |
| 3 | 安全测试 | baseline_poisoning_guard/tamper_proof_audit | 投毒攻击被阻止 | 安全扫描通过 |
| 4 | 混沌测试 | chaos_injector + canary_controller | 混沌注入+金丝雀保护 | 检测率 100% |
| 5 | 红白对抗 | 4 类漂移注入 | PATH_RENAME/YAML_FLIP/TODO_BOMB/IMPORT_HALLUCINATION | 检测率 100%，FN 率 0% |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-021 Rollback | 必须 | 漂移→回滚桥接(G-CT-005) | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\rollback-system\blueprint.md` |
| MOD-INF-022 Escalation | 必须 | 漂移预算耗尽升级(G-CT-006) | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-protocol\blueprint.md` |
| MOD-INF-020 Audit Trail | 必须 | 漂移事件审计 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-018 Agent RBAC | 必须 | 检测器权限控制 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-GATE_ENGINE Gate Engine | 必须 | 门禁持久化 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| MOD-INF-016 Shared | 必须 | AiAuditLogger + AbstractLock | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\shared_core\blueprint.md` |
| MOD-DATABASE DB | 必须 | 基线+漂移结果持久化 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\db\blueprint.md` |

### 10.5 概念重叠声明

> 本模块的 31 个检测维度中，部分维度在其他模块也有概念级实现。重叠不等于重复——检测域不同（代码/配置 vs Agent行为 vs LLM输出 vs 统计指标）。以下声明确保 AI 不会重复造轮子。

| 重叠模块 | 重叠维度 | 本模块检测域 | 对方检测域 | 委托关系 | 处理策略 |
|---------|---------|------------|-----------|---------|---------|
| `feedback_loop.detectors.config_drift` | D25 配置一致性 | 代码/配置文件级 | 运行时环境间配置差异 | 各自独立 | 本模块检测静态配置源一致性，对方检测运行时环境差异 |
| `feedback_loop.verifiers.cross_blueprint_contract_drift` | D14 契约实现 | 蓝图接口 vs 代码签名 | 跨蓝图接口契约一致性 | 各自独立 | 本模块检测单蓝图内契约-代码对齐，对方检测跨蓝图契约一致性 |
| `feedback_loop.forensic.guard_configuration_drift_monitor` | 基线概念 | 代码/配置基线快照 | Guard 参数基线 | 各自独立 | 本模块检测代码漂移基线，对方检测 Guard 参数基线 |
| `infrastructure.escalation_protocol.drift_detector` | 基线+漂移 | 代码/配置漂移 | Agent 行为指标漂移（欧氏距离） | 各自独立 | 不同检测域（代码 vs Agent 行为） |
| `rollback.model_drift_detector` | 基线+漂移 | 代码/配置漂移 | LLM 输出分布漂移（KL 散度） | 各自独立 | 不同检测域（代码 vs LLM 输出） |

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md) 线3:治理闭环

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐（DEP-025/025a~f 已注册） | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-023` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| baseline_manager.py | drift_engine.py | 基线快照是检测前置条件 | baseline 存在 |
| detector_dispatcher.py | drift_engine.py | 检测器调度是检测核心 | dispatcher 可加载 |
| state_machine.py | reconciler.py | 状态机驱动对账流程 | 状态转换正确 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| drift_engine.py | alert_router.py | ScanResult | 函数调用 |
| drift_engine.py | trend_analyzer.py | drift_events | SQLite |
| reconciler.py | state_machine.py | ReconcileResult | 函数调用 |
| baseline_manager.py | drift_engine.py | BaselineSnapshot | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 39 检测器+54 文件，手动维护不可持续 |
| 2 | 依赖对齐自动验证 | 是 | 7 个外部依赖需持续对齐 |
| 3 | 临时时态内容自动清理 | 是 | 有迁移方案（§5.3） |
| 4 | 施工步骤完成度自动检测 | 否 | 已施工完成 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff | 部分有 | 已施工完成，不需 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline [未实现] | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | — | — |

### 10.6 依赖链风险评级

| 依赖链 | 深度 | 级联故障风险 | 缓解措施 |
|--------|:----:|------------|---------|
| 023→021→012 | 3 | 中 | rollback 有独立 DB 连接 + 降级为仅告警 |
| 023→022→018 | 3 | 低 | escalation 有独立权限检查 |
| 023→020→012 | 3 | 中 | audit 有独立写入通道 |
| 023→007→012 | 3 | 低 | gate 有缓存 + 降级为默认放行 |
| 023→016→012 | 3 | 低 | shared_core 有本地 fallback |
| 023↔020 (peer) | 2 | 中 | 状态机守卫防无限循环 |
| 023→021→020→023 (三角) | 3 | 高 | append-only + 状态守卫 + 30min TTL |

---

## §11 产出物存放目录

> 代码文件头部要求（参照 [code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)）：
> 每个代码文件 MUST 在 docstring 首行标注十五字段头部：`[BLUEPRINT]`/`[MODULE]`/`[DOMAIN]`/`[DEPENDENCIES]`/`[CONSUMERS]`/`[STARTUP]`/`[MATURITY]`/`[INVARIANTS]`/`[MODIFY-GUARD]`/`[STABILITY]`/`[SAFETY]`/`[AI_AUTONOMY]`/`[ERROR_CONTRACT]`/`[TESTS]`/`[TTL]`。
> 蓝图 §0 列出的文件 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐。
>
> 四层路径对齐要求（参照 [dependency-graph-template.md §11](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/dependency-graph-template.md)）：
> 本蓝图 §11 声明的产出物路径 MUST 与依赖图 §19 path_mappings 规则一致。
> 验证命令：`python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-023`
> 不一致 = 路径漂移，MUST 修正蓝图 §11 或更新依赖图 §19 规则。

| 产出物类型 | 存放完整绝对路径 | 说明 | consumer_min |
|----------|---------------|------|-------------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_governance\drift_detector\blueprint.md` | 本文件（含设计和施工指引） | AI session |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\` | Python 源码（54 .py 文件） | MOD-INF-021/022/020/018/007/016 |
| 测试代码 | `D:\ZephyrAlpha\tests\behavioral-auditor\` | 单元+集成+红白对抗测试 | CI pipeline |
| 事件定义 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\events.py` | 漂移事件+异常类 | MOD-INF-020/021 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| MOD-GOVERNANCE 治理域蓝图 | 职责分派 | §2 职责分派表 | 蓝图 §2 条目存在 |
| MOD-INF-021 Rollback | 漂移→回滚桥接(G-CT-005) | rollback_bridge.py | G-CT-005 契约可调用 |
| MOD-INF-022 Escalation | 漂移预算耗尽升级(G-CT-006) | drift_engine.py | G-CT-006 契约可调用 |
| MOD-INF-020 Audit Trail | 漂移事件审计 | tamper_proof_audit.py | AiAuditLogger 写入验证 |
| MOD-INF-018 Agent RBAC | 检测器权限控制 | detector_dispatcher.py | 权限检查生效 |
| MOD-GATE_ENGINE Gate Engine | 门禁持久化 | gate_persistence.py | 门禁状态可持久化 |
| MOD-INF-016 Shared | AiAuditLogger 唯一入口 | tamper_proof_audit.py | Logger 实例唯一 |
| MOD-DATABASE DB | 基线+漂移结果持久化 | baseline_manager.py | DB 读写正常 |

### 12.1 域契约锚点

| 域契约ID | 域 | 契约内容 | 对方模块 | 同步更新规则 |
|---------|-----|---------|---------|------------|
| G-CT-005 | 治理闭环 | 漂移→回滚桥接：漂移事件触发回滚 | MOD-INF-021 Rollback | 修改此契约必须同步更新 MOD-INF-021 蓝图 |
| G-CT-006 | 治理闭环 | 漂移预算耗尽升级：预算耗尽触发升级 | MOD-INF-022 Escalation | 修改此契约必须同步更新 MOD-INF-022 蓝图 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-023 版本更新 | 版本升级同步 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | MOD-INF-023 条目更新 | 版本升级同步 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | MOD-INF-023 元数据更新 | 版本升级同步 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 线3:治理闭环 MOD-INF-023 版本 | 版本升级同步 |

---

## §14 已知风险与缓解

> 本节同时承接原 §15 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| 1 | 39 检测器执行耗时过长 | 中 | 中 | 增量扫描 + 检测器并行 + resource_guard | 风险 |
| 2 | 基线膨胀导致存储压力 | 低 | 中 | drift_training + 基线压缩 | 风险 |
| 3 | 过度抑制导致关键漂移漏检 | 低 | 高 | suppression_learner 阈值 + 人工审查 | 风险 |
| 4 | 级联修复循环 | 中 | 高 | cascade_detector 30min 窗口 + 锁定 | 风险 |
| 5 | 基线投毒 | 低 | 高 | baseline_poisoning_guard 交叉验证 + 链式 hash | 风险 |
| 6 | 39 检测器 + 54 文件维护成本高 | 中 | 中 | 检测器声明式注册 + 金丝雀部署 | 负面后果 |
| 7 | 假阳性抑制需时间积累 | 中 | 中 | suppression_learner 自动学习 + 人工审查 | 负面后果 |
| 8 | 混沌注入在生产环境有风险 | 低 | 高 | canary_controller + 沙箱 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§15 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 4 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 Phase（scaffold/experimental/beta/production）+ 1 cross-cutting |
| 施工模式 | 新建 + 整合现有 80+ 脚本 |
| 核心风险 | 39 检测器执行耗时过长；基线投毒 |
| 目标 generation | 4 — 本次从 generation 3 升级到 generation 4（模板v3.5/v3.6升级） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-INF-021 Rollback 已施工 | hard | ✅ | ✅ |
| 2 | MOD-INF-022 Escalation 已施工 | hard | ✅ | ✅ |
| 3 | Python 3.12+ 环境就绪 | hard | ✅ | ✅ |

### 16.3 实施步骤

> **时态属性**：施工步骤属于**临时时态**——执行完毕后可删除，但 MUST 先通过运行验证。
> 4 Phase 全部完成。详细步骤已通过 pytest+mypy+ruff 验证，从蓝图删除。

| Phase | 步骤数 | 状态 |
|:-----:|:-----:|:----:|
| scaffold | 11 | ✅ 已完成 |
| experimental | 16 | ✅ 已完成 |
| beta | 20 | ✅ 已完成 |
| production | 15 | ✅ 已完成 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| scaffold | 整合脚本破坏现有功能 | 保留原始脚本，新模块独立运行 |
| experimental | 状态机扩展破坏已有状态 | drift_events DB 兼容旧状态 |
| beta | 关联引擎性能不达标 | 禁用关联引擎，降级为仅告警 |
| production | 混沌注入影响生产 | canary_controller 终止注入 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 标准 | 状态 |
|---|--------|------|:----:|
| 1 | 产出物存在 | §0.1 所有文件在磁盘存在 | ✅ |
| 2 | 产出物非空 | 无空文件或仅含 pass/... 的文件 | ✅ |
| 3 | SLO 已定义 | §5.4 每个维度有 SLO 目标 | ✅ |
| 4 | 监控已埋点 | §6.1 每个指标有采集方式 | ✅ |
| 5 | 告警已配置 | §6.1 每个告警有阈值和级别 | ✅ |
| 6 | 退化策略已实现 | §6.2 每个组件有降级方案 | ✅ |
| 7 | 回滚方案已验证 | §16.4 回滚步骤可执行 | ✅ |
| 8 | 文档已更新 | §0.2 对齐验证矩阵全部 ✅ | ✅ |
| 9 | 集成测试已通过 | G-CT-005/G-CT-006 契约测试 3/3 PASSED | ✅ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | completed | 施工者 |
| verification_status | passed | 审计者 |
| code_alignment_verified | yes | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 漂移状态机存储 | SQL | `CREATE TABLE drift_events (event_id TEXT PK, module_id TEXT, detector_id TEXT, state TEXT, severity TEXT, detected_at TIMESTAMP, updated_at TIMESTAMP, auto_fixable BOOLEAN, hotfix BOOLEAN DEFAULT 0)` + `CREATE TRIGGER prevent_update BEFORE UPDATE ON drift_events BEGIN SELECT RAISE(ABORT, 'append-only'); END` | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\state_machine.py` |
| 2 | 基线快照存储 | 文件格式 | `data/drift_baselines/{module_id}/baseline_v{N}.json` 含 tree_hash/interface_snapshot/import_graph/config_snapshot + `integritymanifest.yaml` 含 SHA256 chain | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\baseline_manager.py` |
| 3 | 检测器调度并行 | 算法 | `ThreadPoolExecutor(max_workers=8)` + per-detector checkpoint + 超时终止 + 结果缓存 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\detector_dispatcher.py` |
| 4 | 告警去重与聚合 | 算法 | pattern_hash = SHA256(module_id + dimension + target_path) → 相同 hash 去重 → 同维度聚合 → 同模块聚合 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\alert_router.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m zephyr.governance.drift_detection` | 漂移检测 CLI | `--scope: 模块ID列表` `--level: LIGHT/STANDARD/DEEP` | ScanResult |
| 2 | 命令 | `python -m zephyr.governance.drift_detection --baseline-update` | 基线更新 | `--module-id: 模块ID` `--force: 跳过投毒检测` | BaselineSnapshot |
| 3 | 配置 | `_detector-registry.yaml` | 检测器注册表 | id/name/dimension/severity/auto_fixable/status/script_path/timeout_s | YAML 格式 |
| 4 | 配置 | `data/drift_baselines/` | 基线快照目录 | JSON 格式，按 module_id 分目录 | 保留最近 3 版本 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | 检测器执行超时 | 单检测器>timeout_s | 检查 detector_dispatcher 日志 | 终止超时检测器+降级 | 验证降级扫描结果 |
| 2 | 施工 | 基线投毒检测失败 | 交叉验证不一致 | 检查 baseline_poisoning_guard 日志 | 拒绝基线更新+告警 | 从 Git 恢复基线 |
| 3 | 运行 | 漂移风暴 | >50 活跃漂移 | 检查 drift_events 按维度聚合 | 批量模式+Owner通知 | 活跃漂移<10退出 |
| 4 | 运行 | 级联修复循环 | 30min内3次循环 | cascade_detector 锁定 | 锁定1h+P0告警 | 手动解锁+根因修复 |
| 5 | 运行 | 资源耗尽 | 内存>512MB | resource_guard 四级降级 | GC+checkpoint+等待 | 内存恢复后自动恢复 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同文件扫描冲突 | scan_mutex 文件锁 | 排队等待+超时告警 | 扫描范围合并 |
| 基线更新冲突 | mtime 乐观并发 | 后写者放弃+重试 | 最新mtime胜出 |
| 自动修复 vs AI施工 | ai_priority 标记 | AI施工优先，自动修复排队 | AI完成后触发修复 |
| 多session同时修复同一漂移 | drift_events 状态守卫 | 第一个更新状态的session胜出 | 状态机守卫条件 |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 检测器数 | 39 | `_detector-registry.yaml` 条目数 |
| 基线快照数 | 500 | `data/drift_baselines/` 目录统计 |
| 扫描 QPS | 5 | drift_engine 计时 |
| 内存 | <384MB | psutil RSS |
| 磁盘 | <1GB | `data/drift_baselines/` + `drift_events.db` |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 39 检测器串行扫描 | detector_dispatcher 并行度提升 | 检测器 > 60 |
| GAP-002 | 基线快照存储膨胀 | 基线压缩 + 增量快照 | 快照数 > 5000 |
| GAP-003 | SQLite 单写者瓶颈 | WAL + busy_timeout + 写队列批处理 | 并发写入 > 20 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | 54 文件 + 39 检测器 + G-CT-005/G-CT-006 | ✅ |
| v1.0.1b | 2 | 红白对抗 | BUG 修复 + 红白对抗验证 + MCP 端点 | ✅ |
| v2.0.0 | 3 | 模板v3.3重构 | 章节重排+新增§0/§16/§17/§18+Layer 2 压缩 | ✅ |
| v3.0.0 | 4 | 模板v3.5/v3.6升级 | §0前移+§7/§15删除+§10拆分+铁律#13~#15+时态属性 | ✅ |

### 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 检测器 > 60 | detector_dispatcher 动态加载优化 |
| 基线快照 > 5000 | 基线压缩 + 增量快照 |
| 模块 > 1500 | DEEP scan 分片 + 分布式扫描 |
| 漂移事件 DB > 2GB | VACUUM + 归档 + 冷热分层 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。
> **本节同时覆盖原 §7 备选方案**——§18 的"选项"列已包含备选方案信息，无需独立章节。
> **本节同时覆盖原 §15 后果**——负面后果合并到 §14 风险，正面后果与 §1 目标重复无需独立记录。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-023-01 | 整合现有脚本为检测器 | 重写/整合/声明式 | 声明式注册 | 80+ 脚本已覆盖大部分场景；声明式降低新增门槛 | 2026-05-05 |
| 2 | D-023-02 | 自动对账策略 | 仅告警/自动修复/对账+回滚 | 对账+回滚 | 与先干后验一致；回滚验证防止修坏 | 2026-05-05 |
| 3 | D-023-03 | 基线快照机制 | 无基线/基线对比 | 基线对比 | 没有基线无法检测慢蠕变漂移 | 2026-05-05 |
| 4 | D-023-04 | 漂移状态机 | 无状态机/完整状态机 | 10 状态机 | 跨 session 追踪能力；DEAD_LETTER 防遗忘 | 2026-05-05 |
| 5 | D-023-05 | 三级扫描深度 | 全量/分级 | LIGHT/STANDARD/DEEP | 80+ 脚本全量扫描不可持续 | 2026-05-05 |
| 6 | D-023-06 | 维护窗口/漂移抑制 | 无/shadow mode | shadow mode | 避免告警风暴掩盖真异常 | 2026-05-05 |
| 7 | D-023-07 | 自漂移检测 | 无/独立检测 | 纯 stdlib 独立检测 | Watcher 的 Watcher 不可用自身代码 | 2026-05-05 |
| 8 | D-023-08 | 时序存储+趋势分析 | 无/SQLite 时序 | SQLite 时序 | 趋势分析是 beta phase 承诺 | 2026-05-05 |
| 9 | D-023-09 | 关联引擎 | 无/共现矩阵+因果链 | 共现矩阵+因果链 | 系统性问题表现为多模块同时漂移 | 2026-05-05 |
| 10 | D-023-10 | Evolution Engine 反馈 | 无/反馈闭环 | 反馈闭环 | 漂移是设计质量的信号 | 2026-05-05 |
| 11 | D-023-11 | 并发控制 | 文件锁/乐观并发 | 乐观并发(mtime) | 不引入文件锁避免死锁 | 2026-05-05 |
| 12 | D-023-12 | 漂移预算 | 无/SRE 式预算 | SRE 式预算 | 无预算约束漂移无限积累 | 2026-05-05 |
| 13 | D-023-13 | 告警路由 | 无/分级+去重 | 分级+去重+聚合+静默 | 1人维护下告警疲劳是最大 risk | 2026-05-05 |
| 14 | D-023-14 | 修复 ROI | 无/优先级排序 | impact×frequency/effort | 修复资源有限，盲目排序低效 | 2026-05-05 |
| 15 | D-023-15 | Git Bisect 溯源 | 无/自动 bisect | 自动 bisect | 根因溯源比修复本身更重要 | 2026-05-05 |
| 16 | D-023-16 | AI 上下文注入 | 无/三种级别 | minimal/standard/full | 预防性措施比事后修复便宜 10 倍 | 2026-05-05 |
| 17 | D-023-17 | 崩溃恢复 | 无/per-detector checkpoint | per-detector checkpoint | DEEP scan 崩溃后重跑不可接受 | 2026-05-05 |
| 18 | D-023-18 | 漂移风暴 | 无/批量模式 | >50 漂移进入批量模式 | 大规模重构是正常事件而非灾难 | 2026-05-05 |
| 19 | D-023-19 | 热修复旁路 | 无/[HOTFIX] 识别 | [HOTFIX] + 72h TTL | 救火时 drift detector 不能阻碍 | 2026-05-05 |
| 20 | D-023-20 | 环境感知 | 无/context tags | context tags + 差异分类 | 合法环境差异不应被误标为漂移 | 2026-05-05 |
| 21 | D-023-21 | 假阳性学习 | 无/自动抑制 | pattern_hash + 3 次自动抑制 | 反复手动标记假阳性不可持续 | 2026-05-05 |
| 22 | D-023-22 | 级联故障检测 | 无/30min 窗口 | 30min 3 次循环→锁定 | AI 修复可能治标不治本 | 2026-05-05 |
| 23 | D-023-23 | 资源上限 | 无/四级降级 | 512MB/2GB + 四级降级 | 单机场景资源有限 | 2026-05-05 |
| 24 | D-023-24 | 多实例竞态 | 无/scan mutex | 文件锁 + 碰撞策略 + 合并 | 三种触发可并发 | 2026-05-05 |
| 25 | D-023-25 | 孤儿资源 | 无/三方比对 | 磁盘×注册表×引用 | AI 施工产临时文件 | 2026-05-05 |
| 26 | D-023-26 | 符号链接/子模块 | 无/完整性检查 | 断裂+目标变更+循环 | 共享 scripts/ 可能用 symlink | 2026-05-05 |
| 27 | D-023-27 | 文件底层属性 | 无/编码+换行符 | BOM+CRLF/LF+权限 | Windows/Linux 跨 session 经典痛点 | 2026-05-05 |
| 28 | D-023-28 | 测试夹具漂移 | 无/schema+mock+expected | 三轴检查 | 测试通过不代表系统正确 | 2026-05-05 |
| 29 | D-023-29 | 配置多源一致性 | 无/三源对账 | .env×YAML×硬编码→YAML SSoT | 三源不一致→幽灵 bug | 2026-05-05 |
| 30 | D-023-30 | Python 版本兼容性 | 无/三轴检查 | 语法+标准库+类型注解 | AI 用最新语法但不知道项目目标版本 | 2026-05-05 |
| 31 | D-023-31 | 向后兼容策略 | 无/API 签名变更检测 | 签名变更+下游影响 | AI 不守 SemVer | 2026-05-05 |
| 32 | D-023-32 | .gitignore 完整性 | 无/三轴检查 | 未忽略+误忽略+覆盖 | AI 生成新文件类型但不加 .gitignore | 2026-05-05 |
| 33 | D-023-33 | 冷启动 | 无/bootstrap | bootstrap scan + trust | 1500 模块上线第一天不能要求人工创建基线 | 2026-05-05 |
| 34 | D-023-34 | Owner 缺席模式 | 无/双模式 | LENIENT/SURVIVAL | 1人维护核心挑战 | 2026-05-05 |
| 35 | D-023-35 | 告警可信度评分 | 无/per detector credibility | fp_rate×precision×recency | 1人维护下最大风险是"狼来了" | 2026-05-05 |
| 36 | D-023-36 | 基线投毒防护 | 无/交叉验证+多基线 | 交叉验证+投票+链式hash | 基线被污染=所有检测失效 | 2026-05-05 |
| 37 | D-023-37 | 防篡改审计 | 无/append-only+Git AUDIT | append-only+异常检测 | 数据被攻破=失明 | 2026-05-05 |
| 38 | D-023-38 | 命名约定与魔数漂移 | 无/同义词+风格+重复字面量 | 动词同义词+大小写+重复常量 | AI 跨 session 各有风格偏好 | 2026-05-05 |
| 39 | D-023-39 | 模板v3.3重构 | 保持旧结构/按新模板重构 | 按新模板重构 | REQUIRED_SECTIONS 合规；AI 阅读顺序优化 | 2026-05-14 |
| 40 | D-023-40 | 模板v3.5/v3.6升级 | 保持v3.3/按v3.5升级 | 按v3.5/v3.6升级 | §0前移优化AI阅读顺序；§7/§15删除减少噪音；§10拆分增加依赖对齐 | 2026-05-14 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——
> AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

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
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |
| 16 | **术语表不可省略**——每个蓝图 MUST 包含术语表，定义本蓝图的关键术语和易混淆术语的区别 | AI 对术语产生理解漂移 |
| 17 | **参考实现规格 vs 已实现代码重复**——接口契约无法表达的逻辑规格（SQL并发控制/算法步骤/协议序列）MUST 保留在 §16.7；Pydantic模型字段定义等接口代码不重复（铁律#13） | 关键逻辑实现错误 / 蓝图与代码不一致 |
| 18 | **对标验证表格 vs 对标散文**——结构化的对标表格是验证基准，MUST 保留；长篇对标散文段落 MUST 删除 | 丢表格→无法验证设计完整性；留散文→噪音淹没关键信息 |
| 19 | **SLO 必须定义**——§5.4 服务水平目标不可省略。无 SLO = AI 无法设计合理的容错/降级/熔断策略 | 容错策略凭空猜测，降级阈值无依据 |
| 20 | **可观测性不可省略**——§6.1 可观测性规格不可省略。无法度量就无法改进 | 故障无法发现，性能退化无法感知 |
| 21 | **退化矩阵必须声明**——§6.2 退化矩阵不可省略。部分失败时的降级行为必须明确 | 部分失败时系统行为不可预测 |

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
| 漂移检测蓝图中"39 检测器维度清单" | **原地** | 服务对象相同 + 变更频率同步 + 依赖关系完全重叠 |
| 漂移检测蓝图中"漂移分析高级策略" | **原地** | 高级策略是漂移检测的核心能力扩展，不是独立子系统 |
| 漂移检测蓝图中"混沌注入子系统" | **原地** | 混沌注入服务于漂移检测验证，与主体 depends_on 交集 >80% |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

本蓝图涉及迁移：governance/ 根级 15 孤儿文件 → drift_detection/。迁移方案见 §5.3。

### 蓝图中的删除决策清单

> 迁移型删除已全部执行完毕。新增删除决策请在此表追加。

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
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
| 4 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 6 | 代码构建标准 | GOV-ENG-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\engineering\code-construction-standards.md` | 十五字段头部 |
| 7 | AI 压缩工作流标准 | GOV-DOC-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_030_doc_numbering_metadata.yaml` | 压缩规则 |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | governance/ 根级 15 孤儿脚本 | `D:\ZephyrAlpha\src\zephyr\governance\` | 部分漂移检测功能 | 已整合到 drift_detection/，governance/ 版本为旧版 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 漂移检测代码 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\` | 修改 | 蓝图描述的核心代码 |
| 2 | 测试代码 | `D:\ZephyrAlpha\tests\behavioral-auditor\` | 修改 | 测试用例 |
| 3 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_governance\drift_detector\blueprint.md` | 修改 | 本文件 |
| 4 | 旧治理脚本 | `D:\ZephyrAlpha\src\zephyr\governance\` | 迁移 | 孤儿文件迁移到 drift_detection/ |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| Drift 模块蓝图职责与架构 | **本文档 §1-§10** | — |
| Drift 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 漂移检测核心策略 | **本文档 §3 蓝图特有** | — |

### 负向责任

| 不涉及 | 由谁负责 |
|--------|---------|
| 回滚执行 | MOD-INF-021 Rollback |
| 升级决策 | MOD-INF-022 Escalation Engine |
| 审计日志存储 | MOD-INF-020 Audit Trail |
| 权限控制 | MOD-INF-018 Agent RBAC |
| 门禁判定 | MOD-GATE_ENGINE Gate Engine |
| 数据持久化 | MOD-DATABASE DB |

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-GOVERNANCE 治理域蓝图 | §2 职责分派 |
| Tier 1 | MOD-GATE_ENGINE Gate Engine | gates/drift-detector.py + gate_engine.py + ct_drift_budget.py |
| Tier 1 | MOD-INF-021 Rollback | rollback/drift_fix.py |
| Tier 2 | MOD-INF-020 Audit Trail | audit-trail/drift_bridge.py |
| Tier 2 | MOD-INF-013 MCP Server | mcp/governance_server.py |
| Tier 2 | governance/ shim | drift-detector/__init__.py + phase_check_registry.py |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\governance\drift_detection\` 代码 | §4 文件归属 |

### 触发条件

| 关键词/场景 | 触发动作 |
|------------|---------|
| drift / 漂移 / 检测器 / 对账 | 加载本蓝图 |
| drift_detection/ 文件迁移 | 读取 §5.3 孤儿文件清单 + §5 约束条件 |
| 治理域子蓝图查询 | 从 MOD-GOVERNANCE §2 路由到本文件 |

### 导航路径

```
registry_of_registries.yaml → blueprint_registry.yaml → MOD-GOVERNANCE → §2 → MOD-INF-023
```

### 漂移防护

| 修改此文件 | 必须同步更新 |
|-----------|------------|
| §4 接口契约 | 下游检查接口兼容性 |
| §5 约束条件 | construction_progress 字段 |
| §10 依赖模块 | blueprint_registry.yaml MOD-INF-023 条目 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步（下游蓝图） | Tier 2 同步（集成系统） |
|---------|---------|---------------------|---------------------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |

---

## 蓝图特有章节

> **硬规则**：模板章节=合规下限，可超出。超出下限的内容 MUST 写在本章节内。
> 写在本章节外 = 压缩工作流视为冗余 → 可删。写在本章节内 + 标注三要素 = 不可删。

### 蓝图特有：39 检测器维度清单

> 来源：规格化内容价值映射——蓝图特有
> 仅本蓝图需要：39 检测器维度是漂移检测的核心交付物
> 不可砍理由：砍掉=AI施工时不知道检测什么

```yaml
detector_dimensions:
  D1_IMPORT: "import 幻觉——import 了不存在的模块"
  D2_DEAD_CODE: "死码——定义了但从未被引用的函数/类/变量"
  D3_DUPLICATE_FUNC: "重复功能——语义相同但实现不同的函数"
  D4_LOGIC_BREAK: "逻辑断裂——函数 A 调用 B 但 B 不存在或签名不匹配"
  D5_YAML_DISK: "YAML 注册表 vs 磁盘文件——注册表声明但磁盘不存在，或磁盘存在但注册表未声明"
  D6_MANIFEST: "静态清单生成器一致性"
  D7_CONTRACT_CODE: "契约-代码 AST 对比——YAML 声明与代码实现不一致"
  D8_AI_HALLUCINATION: "AI 幻觉 import——import 了不存在的模块"
  D9_AI_DEAD_CODE: "AI 死码检测"
  D10_AI_DUPLICATE: "AI 重复功能检测"
  D11_AI_BROKEN_LOGIC: "AI 逻辑断裂——NotImplementedError/TODO 占比过高"
  D12_AI_STYLE_DRIFT: "AI 风格漂移——跨 session 代码风格不一致"
  D13_AI_KNOWLEDGE_POLLUTION: "AI 知识污染——命名冲突/混合命名约定"
  D14_CONTRACT_IMPLEMENTATION: "契约实现——蓝图接口 vs 代码实际签名"
  D15_SEMANTIC: "语义漂移——同一概念在两个 YAML 中矛盾"
  D16_DB_SCHEMA: "数据库 Schema 漂移——SQLite vs ORM vs migration"
  D17_DEP_VERSION: "依赖版本漂移——requirements.txt vs pip freeze"
  D18_SECURITY_POLICY: "安全策略漂移——安全规范 vs 端点实际实现"
  D19_DOC_CODE_EVOLUTION: "文档-代码协同演化——文档滞后标记"
  D20_TEST_COVERAGE: "测试覆盖率漂移——代码增长率 vs 测试增长率"
  D21_NAMING_MAGIC: "命名约定与魔数漂移——同义词+大小写+重复常量"
  D22_SYMLINK: "符号链接/子模块完整性——断裂+目标变更+循环"
  D23_FILE_ATTR: "文件底层属性——BOM+CRLF/LF+权限"
  D24_TEST_FIXTURE: "测试夹具漂移——schema+mock+expected 三轴"
  D25_CONFIG_CONSISTENCY: "配置多源一致性——.env×YAML×硬编码→YAML SSoT"
  D26_PYTHON_COMPAT: "Python 版本兼容性——语法+标准库+类型注解"
  D27_BACK_COMPAT: "向后兼容策略——API 签名变更检测"
  D28_GITIGNORE: ".gitignore 完整性——未忽略+误忽略+覆盖"
  D29_ORPHAN_RESOURCE: "孤儿资源——磁盘×注册表×引用三方比对"
  D30_COLD_START: "冷启动——bootstrap scan + trust"
  D31_OWNER_ABSENCE: "Owner 缺席模式——LENIENT/SURVIVAL"
```

### 蓝图特有：漂移检测核心策略（2.1-2.21）

> 来源：规格化内容价值映射——蓝图特有
> 仅本蓝图需要：核心策略是检测器的实现规格
> 不可砍理由：砍掉=AI施工时不知道如何实现检测器

| # | 策略ID | 策略名 | 检测维度 | 检测方法 | 自动修复 | 对应代码 |
|---|--------|--------|---------|---------|:-------:|---------|
| 1 | 2.1 | import 幻觉检测 | D1/D8 | AST 解析所有 import/from → 交叉验证目标模块存在 | ❌ | ai_construction_detectors.py |
| 2 | 2.2 | 死码检测 | D2/D9 | AST：定义未引用函数/类、声明未使用变量、仅 pass/... 空壳体 | ❌ | ai_construction_detectors.py |
| 3 | 2.3 | 重复功能检测 | D3/D10 | AST 级别函数签名相似度（SHA256 body hash）+ 跨模块查重 | ❌ | ai_construction_detectors.py |
| 4 | 2.4 | 逻辑断裂检测 | D4/D11 | NotImplementedError 无 fallback / TODO 占比过高 / 上下文截断签名 | ❌ | ai_construction_detectors.py |
| 5 | 2.5 | 风格漂移检测 | D12 | 跨模块/跨 session 代码风格不一致（dataclass vs pydantic / sync vs async / 命名规范） | ❌ | ai_construction_detectors.py |
| 6 | 2.6 | 知识污染检测 | D13 | 命名冲突（类名=函数名）、混合命名约定（snake_case+CamelCase 同文件） | ❌ | ai_construction_detectors.py |
| 7 | 2.7 | 契约实现检测 | D14 | AST 级对比——蓝图 §3 接口 vs 代码实际接口签名 | ❌ | ai_construction_detectors.py |
| 8 | 2.8 | 语义漂移检测 | D15 | YAML 之间语义一致性——同一概念的枚举值/数量/命名在两个 YAML 中是否矛盾 | ❌ | ai_construction_detectors.py |
| 9 | 2.9 | DB Schema 漂移 | D16 | SQLite schema vs ORM model vs migration 文件三方对账 | ❌ | ai_construction_detectors.py |
| 10 | 2.10 | 依赖版本漂移 | D17 | requirements.txt / pyproject.toml vs 实际 pip freeze 交叉对比 | ✅ | ai_construction_detectors.py |
| 11 | 2.11 | 安全策略漂移 | D18 | 安全规范要求 vs 所有端点实际实现 | ❌ | ai_construction_detectors.py |
| 12 | 2.12 | 文档-代码协同 | D19 | 代码文件最后修改时间 vs 对应蓝图/文档最后修改时间——文档滞后标记 | ❌ | ai_construction_detectors.py |
| 13 | 2.13 | 测试覆盖率漂移 | D20 | 模块代码行数增长率 vs 测试代码行数增长率——覆盖率趋势对比 | ❌ | ai_construction_detectors.py |
| 14 | 2.14 | 命名约定与魔数 | D21 | 动词同义词+大小写+重复常量 | ❌ | naming_magic_checker.py |
| 15 | 2.15 | 符号链接/子模块 | D22 | 断裂+目标变更+循环 | ❌ | symlink_checker.py |
| 16 | 2.16 | 文件底层属性 | D23 | BOM+CRLF/LF+权限 | ❌ | file_attr_checker.py |
| 17 | 2.17 | 测试夹具漂移 | D24 | schema+mock+expected 三轴检查 | ❌ | test_fixture_checker.py |
| 18 | 2.18 | 配置多源一致性 | D25 | .env×YAML×硬编码→YAML SSoT | ❌ | config_consistency.py |
| 19 | 2.19 | Python 版本兼容性 | D26 | 语法+标准库+类型注解三轴检查 | ❌ | python_compat.py |
| 20 | 2.20 | 向后兼容策略 | D27 | API 签名变更检测+下游影响 | ❌ | backcompat_checker.py |
| 21 | 2.21 | .gitignore 完整性 | D28 | 未忽略+误忽略+覆盖 | ❌ | gitignore_auditor.py |

### 蓝图特有：漂移分析高级策略（6.1-6.27）

> 来源：规格化内容价值映射——蓝图特有
> 仅本蓝图需要：高级策略是趋势/关联/取证的实现规格
> 不可砍理由：砍掉=AI施工时不知道如何实现高级分析

| # | 策略ID | 策略名 | 功能 | 对应代码 | 状态 |
|---|--------|--------|------|---------|:----:|
| 1 | 6.1 | 漂移速率追踪 | drift velocity（模块/天）计算与趋势 | trend_analyzer.py | ✅ |
| 2 | 6.2 | 解决率追踪 | resolution_rate（已解决/总检测）计算 | trend_analyzer.py | ✅ |
| 3 | 6.3 | MTTR 追踪 | Mean Time To Resolve 计算与趋势 | trend_analyzer.py | ✅ |
| 4 | 6.4 | 共现矩阵 | 模块间漂移共现频率矩阵 | correlation_engine.py | ✅ |
| 5 | 6.5 | 因果链推断 | 漂移事件因果链（A→B→C） | correlation_engine.py | ✅ |
| 6 | 6.6 | 修复 ROI 排序 | impact×frequency/effort 优先级排序 | roi_engine.py | ✅ |
| 7 | 6.7 | Git Bisect 溯源 | 自动 bisect 定位引入漂移的 commit | git_bisector.py | ✅ |
| 8 | 6.8 | AI 上下文注入 | minimal/standard/full 三级注入 | ai_context_injector.py | ✅ |
| 9 | 6.9 | 崩溃恢复 | per-detector checkpoint + 断点续扫 | drift_engine.py | ✅ |
| 10 | 6.10 | 漂移风暴 | >50 漂移进入批量模式 | drift_engine.py | ✅ |
| 11 | 6.11 | 热修复旁路 | [HOTFIX] 识别 + 72h TTL | drift_hotfix_bypass.py | ✅ |
| 12 | 6.12 | 环境感知 | context tags + 差异分类 | drift_engine.py | ✅ |
| 13 | 6.13 | 假阳性学习 | pattern_hash + 3 次自动抑制 | suppression_learner.py | ✅ |
| 14 | 6.14 | 级联故障检测 | 30min 3 次循环→锁定 | cascade_detector.py | ✅ |
| 15 | 6.15 | 资源上限 | 512MB/2GB + 四级降级 | resource_guard.py | ✅ |
| 16 | 6.16 | 多实例竞态 | scan_mutex 文件锁 + 碰撞策略 + 合并 | scan_mutex.py | ✅ |
| 17 | 6.17 | 孤儿资源 | 磁盘×注册表×引用三方比对 | orphan_scanner.py | ✅ |
| 18 | 6.18 | 冷启动 | bootstrap scan + trust | cold_start.py | ✅ |
| 19 | 6.19 | Owner 缺席 | LENIENT/SURVIVAL 双模式 | drift_engine.py | ✅ |
| 20 | 6.20 | 告警可信度 | fp_rate×precision×recency | credibility_engine.py | ✅ |
| 21 | 6.21 | 基线投毒防护 | 交叉验证+投票+链式hash | baseline_poisoning_guard.py | ✅ |
| 22 | 6.22 | 防篡改审计 | append-only + Git AUDIT | tamper_proof_audit.py | ✅ |
| 23 | 6.23 | 维护窗口 | shadow mode + 时间窗口声明 | canary_controller.py | ✅ |
| 24 | 6.24 | 自漂移检测 | 纯 stdlib 独立检测 | self_check.py | ✅ |
| 25 | 6.25 | 漂移事件流 | drift_events DB + 状态机守卫 | events.py | ✅ |
| 26 | 6.26 | 漂移预算门禁 | SRE 式预算 + 施工阻断 | gate_persistence.py | ✅ |
| 27 | 6.27 | 混沌注入 | 主动注入 + 自动回滚 + 检测器健康验证 | chaos_injector.py | ✅ |

---

## 变更记录

> 变更历史通过 Git log 追踪。

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 漂移(Drift) | 代码/配置/架构偏离设计意图的累积偏差 | Bug | Bug是功能错误，漂移是渐进偏离 |
| 基线(Baseline) | 某时间点的系统状态快照，作为漂移对比基准 | 检查点 | 检查点是崩溃恢复用，基线是漂移对比用 |
| 对账(Reconciliation) | 自动修复可修复漂移的过程 | 回滚 | 对账是修复，回滚是撤销 |
| 漂移预算(Drift Budget) | SRE式错误预算——允许的未解决漂移数量 | 告警阈值 | 预算是累计量，阈值是瞬时触发 |
| DEAD_LETTER | 超过TTL未验证的漂移事件状态 | SUPPRESSED | SUPPRESSED是假阳性抑制，DEAD_LETTER是超时未处理 |
| 影子模式(Shadow Mode) | 检测器运行但告警降级为仅记录 | 金丝雀 | 金丝雀是部分流量验证，影子是全量静默 |
| pattern_hash | 漂移模式的SHA256指纹，用于去重和假阳性学习 | drift_id | drift_id是事件ID，pattern_hash是模式指纹 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 语义漂移检测精度不足 | 中 | 纯AST分析无法理解语义 | 预留接口，待LLM辅助 | §3 6.18 | 待解决 |
| 2 | 跨语言检测仅Python | 低 | 其他语言解析器未实现 | 预留接口 | §3 6.18 | 待解决 |
| 3 | shallow clone场景git bisect降级 | 低 | shallow clone缺少完整历史 | cold_start 识别并降级 | §3 2.19 | 已缓解 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ✅ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ✅ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ✅ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | frozen | 高 | — | 39检测器+10状态机+基线快照已验证 |
| 接口契约 | stable | 高 | 接口变更需Owner审批 | 3个公共API已稳定 |
| 数据模型 | stable | 高 | 新增字段向后兼容 | Pydantic V2模型已定型 |
| 检测器策略 | evolving | 中 | 新检测器持续添加 | 39→60+扩展中 |
| 高级分析 | volatile | 低 | beta/production Phase验证 | 趋势/关联/取证待验证 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | 54文件+39检测器+G-CT-005/G-CT-006 | — | 已完成 |
| v1.0.1b | 红白对抗验证+BUG修复 | v1.0.0 | 已完成 |
| v2.0.0 | 模板v3.3重构+§0/§16/§17/§18 | v1.0.1b | 已完成 |
| v3.0.0 | 模板v3.5/v3.6升级+时态属性 | v2.0.0 | 已完成 |
| v3.1.0 | 回填缺失模板章节+压缩+模板合规修复 | v3.0.0 | 已完成 |
