---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 交易决策域施工流程标准作业规程（SOP）——端到端 17 段施工闭环
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.7.2"
date: 2026-09-15
topic: construction_workflow_sop
scope: global
depends_on:
  - 01_design_memo_management_spec
  - AI_review_instructions
  - mining_sop_policy
related_issues:
  - "#ARCH-CONSTRUCTION-SOP-001（施工 SOP 端到端编排载体）"
related_modules:
  - scripts/governance/apply_depgraph.py
  - scripts/governance/sync_panorama_module.py
  - scripts/governance/d5_architecture/generators/align_all.py
  - scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py
  - scripts/governance/d11_compliance/audit_registration.py
  - scripts/governance/generate_project_depgraph.py
  - scripts/governance/generate_project_path_tree.py
  - scripts/governance/d5_architecture/diagnose_depgraph.py
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
  - scripts/session_worktree.py
  - scripts/lock_files.py
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
  - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
---

# 交易决策域施工流程标准作业规程（SOP）——端到端 17 段施工闭环

> 本 SOP 是 **07_trading_decision_architecture** 域施工流程的**编排层真源**，把散落在 86 个 trae_xxx 规则文件（实数以 rules/ 目录为准）+ 多个 design_memo 中的流程性内容串联成端到端 17 段施工闭环（Step 0-12 含小数步）。
> **性质**：编排层，**只串联流程+引用真源规则，不重复规则内容**。每一步明确"何时触发 / 做什么 / 怎么做 / 产出什么 / 不通过怎么办"。
> **适用范围**：仅交易决策域施工（regime/选股/仓位/风控/买卖/执行/对账/治理——对应 docs/02_enterprise_architecture/07_trading_decision_architecture 业务族，"07"只是目录编号勿再当域名使用）。数据层/基础设施/治理脚本走全局规则；数据回灌/修复/判重另必读 [data_ops_policy](../data_ops_sop/data_ops_policy.md)。
> **管理规范**：[01_design_memo_management_spec](../../../_working/archive/2026-09/design_memos/01_design_memo_management_spec.md)。
> **关联**：[AI_review_instructions](../../../_archive/AI_review_instructions.md)（文档审查指令集，Step 1 真源）｜ [60_cross_cutting_cleanup](../../../_archive/60_cross_cutting_cleanup.md)｜ [65_git_safety_governance](../../../_working/archive/2026-09/design_memos/65_git_safety_governance.md)｜ [66_commit_queue_serialization](../../../_working/archive/2026-09/design_memos/66_commit_queue_serialization.md)｜ [mining_sop_policy](../mining_sop/mining_sop_policy.md)（挖矿方法论真源，Step 1.9 方案挖矿）｜ [skeleton_mining_policy](../mining_sop/skeleton_mining_policy.md)（骨架构建——新域开工先挖骨架，先于 Step 1.9）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G02 施工流程 SOP（meta 类·编排层） |
| 创建 | 2026-08-12 |
| 优先级 | P0（施工前置依赖） |
| 状态 | active v1.0.0 |
| 上游 | [01_design_memo_management_spec](../../../_working/archive/2026-09/design_memos/01_design_memo_management_spec.md)（设计备忘管理规范） |
| 下游 | 所有交易决策域施工 AI session（必读） |
| 真源边界 | 本文件只编排流程步骤+命令+通过条件+失败处置；规则约束（禁止/必须/约束条件）以原 trae_xxx 文件为准 |
| 冲突解决 | 规则约束以原文件为准，流程编排以本文件为准 |

## 2. 背景与定位

### 2.1 痛点

现有规则**片段化**——86 个 trae_xxx 规则文件 + 48 个 design_memo（2026-09-20 裁定#384 后 49 件归档至 docs/_working/archive/2026-09/design_memos/，仅 16 号留置），每份各管一段，没有端到端把"施工流程"串起来的载体：

| 现有文档 | 覆盖环节 | 缺口 |
|---|---|---|
| [trae_035_task_construction_verification.yaml](../../rules/trae_035_task_construction_verification.yaml) | 搬家规则/前置检查/循环验收/全景图对齐/门禁命令 | ❌ 缺文档审查+长清单审查+施工完毕文档更新+worktree 合并+只清理自己 |
| [trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) | 模块创建 11 phase（phase_0~phase_10）完整工作流（冷启动→搜索→设计态→准入→蓝图→文件→路径→文件头→启动→注册表→三方对齐） | ❌ 仅"新建模块"流程，不含文档审查/测试/commit/清理/merge |
| [trae_080_panorama_alignment.yaml](../../rules/trae_080_panorama_alignment.yaml) | 五图对齐铁律（设计态先行+派生+对齐验证） | ❌ 仅五图对齐环节（第六图 frontend_map 对齐规则在 alignment_checklist §3） |
| [AI_review_instructions.md](../../../_archive/AI_review_instructions.md) | 文档审查指令集 | ❌ 只是审查指令，不是端到端施工流程 |
| [65_git_safety_governance.md](../../../_working/archive/2026-09/design_memos/65_git_safety_governance.md) | git 安全防护层 | ❌ 只管 git 安全 |
| [66_commit_queue_serialization.md](../../../_working/archive/2026-09/design_memos/66_commit_queue_serialization.md) | 多 AI 并发提交队列 | ❌ 只管提交期串行化 |
| [01_design_memo_management_spec.md](../../../_working/archive/2026-09/design_memos/01_design_memo_management_spec.md) | 设计备忘三层分治原则 | ❌ 是文档管理规范，不是施工流程 |

### 2.2 定位

本 SOP 是**编排层**，把上述真源规则按施工时间序串成端到端流程：

- **不重复**规则内容（禁止/必须/约束条件以原文件为准）
- **只编排**：步骤序列 + 触发条件 + 执行命令 + 通过判据 + 失败处置
- **每一步**指向真源规则文件路径，AI 可按需回溯细节

### 2.3 与现有规则的关系矩阵

| SOP 步骤 | 引用真源 | 引用方式 |
|---|---|---|
| Step 0 Session 冷启动 | trae_056 phase_0 / trae_048 | 不重复，引用 |
| Step 1 文档审查 | AI_review_instructions | 不重复，引用 |
| Step 1 前置·地图逐层讨论闸（涉地图任务） | trading_decision_map_layering_sop | 不重复，引用（四道前置检查：已有资产盘点/四路调研/上层完整性/枝干分级） |
| Step 1.5 创建前搜索 | trae_056 phase_1 / trae_002 | 不重复，引用 |
| Step 1.8 架构评审门控 | trae_036 gov_arch_002 | 不重复，引用 |
| Step 1.9 方案挖矿 | mining_sop_policy | 不重复，引用（六向寻路/矿脉枯竭封矿/防噪音四闸/时间盒/挖后自审闸） |
| Step 2 全景图登记 | trae_080 / trae_056 phase_2 / trae_032 | 不重复，引用 |
| Step 3 五图对齐 | trae_080 panorama_alignment | 不重复，引用 |
| Step 3.5 后端盘点与拆件判定 | trae_086 / frontend_component_split_policy | 不重复，引用（2026-10-04 补行——CV-11/R-15 矩阵闭合） |
| Step 4 施工编码 | trae_056 phase_4-9 / trae_047 / trae_053 / trae_064 | 不重复，引用 |
| Step 5 单元测试+循环验收 | trae_035 task_003 / trae_084 | 不重复，引用 |
| Step 6 长清单审查 | 附录 A + trae_081 | 全文收录+引用基座 |
| Step 7 更新施工文档 | trae_052 rule_eleven / 01_design_memo_management_spec §5.3 | 不重复，引用 |
| Step 8 全景图状态流转 | trae_080 / trae_056 phase_10 / trae_035 task_003_panorama_alignment | 不重复，引用 |
| Step 9 文件完整性检查 | 65_git_safety_governance §备份先行 | 不重复，引用 |
| Step 10 GitCommitGateway 落地 | 66_commit_queue_serialization / trae_075 / trae_084 | 不重复，引用 |
| Step 11 临时文件清理 | trae_071 / trae_035 task_closure_standard 清扫三步法 | 不重复，引用 |
| Step 12 worktree 合并与清理 | trae_078 / trae_076 / project_memory session_worktree 教训 | 不重复，引用 |

## 3. 施工流程 17 段（Step 0-12 含小数步）

### Step 0 · Session 冷启动（前置必做）

**何时触发**：任何新 AI session 开始施工前
**前置条件**：无
**操作摘要**：守护进程启动 + 必看文件加载 + Session Continuity 恢复 + Phase Manager 检查
**引用真源**：[trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) §phase_0_cold_start / [trae_048_ops_vibe_coding_session.yaml](../../rules/trae_048_ops_vibe_coding_session.yaml) §ops_vc_005
**执行命令**：

```powershell
# 1. 守护进程启动
python scripts/lock_files.py cleanup
python scripts/governance/meta/session_startup_check.py --json
# （2026-10-04 更正：原列 scripts/ide_health_service.py 全仓不存在（R-01）；
#   冷启动可机验锚=session_startup_check.py（--json/--phase），守护/门控检查经其覆及）

# 2. 必看文件加载
# - docs/registry_of_registries.yaml（全项目注册表索引）
# - docs/03_modules/template_registry.yaml（可用模板清单）
# - python scripts/governance/extract_depgraph.py --summary（全景图架构全景）
# - python scripts/governance/extract_depgraph.py --paths（文件级依赖关系）
# - docs/03_modules/_system_master/blueprint.md §0（子系统任务域定位）
# - .trae/rules/project_rules.md（L0 硬规则，FIRST-READ 6 步）
# - 本 SOP（construction_workflow_sop.md）
# - alignment_checklist.md（全项目对齐清单——六图+注册表+代码文档三层对齐规则，新 AI 必知）
# - 涉前端施工加读：docs/03_modules/_domain_frontend/frontend_handbook/（避坑事实库）+ trae_086_frontend_module_construction.yaml（拆件铁律）+ sop/construction_sop/frontend_component_split_policy.md（拆件操作闭环——Step 3.5 判定"有得拆"时的施工路径真源）
# - 交易决策地图逐层讨论/血肉填充任务加读：sop/trading_decision_map_sop/trading_decision_map_layering_policy.md（防撞车·防越级·防枝末先行——六步流程+层位状态表，每层讨论 MUST 先过四道前置检查：已有资产盘点五选一处置/四路外部调研/上层完整性/枝干分级）
# - 方案/策略/设计文档类施工任务加读：sop/mining_sop/mining_sop_policy.md（挖矿方法论真源——施工前先做方案，方案先挖矿，把矿挖干再施工；Step 1.9 真源）

# 3. Session Continuity 恢复
python scripts/lock_files.py status

# 4. Phase Manager 检查（2026-09-24 实测 58 个 gate_* 唯一名；实数以 phase_manager 运行时为准）

# 5. LifecycleManager.boot_sequence() 11 步启动序列（系统级 boot，自动执行）：
#    01_config_validate → 02_stop_gate_init → 03_audit_logger_start →
#    04_registry_load → 05_work_orch_load_dags → 07_health_monitor_start →
#    08_integration_validate → 09_audit_self_monitor_start → 09a_governance_watchdog_start
#    （06_circadian/08a/08b 已移除；任一步失败则 break 跳过剩余）
#    真源：src/zephyr/trading/lifecycle_manager.py §boot_sequence（符号锚）

# 6. boot_hooks 已注册的自动钩子（AI 无需手动注册，但需知道哪些 hook 在后台运行）：
#    真源：src/zephyr/trading/boot_hooks.py §register_boot_hooks（符号锚）
#    - Task system hooks（6 个）：auto_unblock_dependents/auto_retry_on_failure/
#      triple_alignment_on_verified/cleanup_task_processes/orc_vms_archive/rbk_gate_freeze
#    - Event-driven hooks（6 个）：escalation_check/timeout_check/budget_delta/
#      session_startup_init_budget/session_shutdown_budget_close/triple_align_event
#    - 永久系统启动钩子（6 个）：RollbackBootIntegration/SLAMonitor/Notifier/
#      HealthAggregator/F5BootIntegration/IdeHealthDaemon
#    注意：triple_alignment_on_verified 会在任务 VERIFIED 时自动触发三方对齐，
#         AI 不需要手动跑 align——但 SOP Step 3/8 仍需手动验证五图对齐
```

**通过判据**：守护进程 running=true / 必看文件全部加载 / Session 状态恢复 / 当前阶段已确认 / boot_sequence 11 步全 PASS
**不通过处置**：守护进程未运行 → **禁止执行任何后续步骤**（trae_056 明示：非协商必做）/ boot_sequence 失败 → 查 lifecycle_manager 日志
**产出物**：Session 就绪状态
**HookRegistry 说明**：任务状态变更回调注册表（`src/zephyr/governance/ops_governance/event_hook.py` §HookRegistry（符号锚），单例 `hook_registry`），按 priority 排序执行，异常隔离。AI 触发任务状态变更时相关 hook 自动执行
**handoff 交接包读取**（[parallel_session_coordination_policy.md](../../policies/parallel_session_coordination_policy.md)）：Session Continuity 恢复时 MUST 读取上一 session 的 handoff 交接包 `.runtime/handoffs/handoff_<sid>.json`（含 pending_tasks/warnings），否则状态丢失
**ABS 绝对禁止清单**（[trae_018_behavior_code_prohibition.yaml](../../rules/trae_018_behavior_code_prohibition.yaml) ABS-01~08，全流程红线）：
- ABS-01：禁止修改 immutable_core 文件（safety_level=H 且 ai_autonomy=immutable_core）
- ABS-02：禁止删除任何文档（删除走 [trae_029](../../rules/trae_029_doc_operation_security.yaml) 三步审判）
- ABS-03：禁止裁决规则冲突（MUST 报告 Owner）
- ABS-04：禁止忽略高优先级规则
- ABS-05：禁止执行 P0 变更（Level 1-4 规则，需 Owner 执行）
- ABS-06：禁止改 P0 条款
- ABS-07：禁止自行判断紧急绕过审批
- ABS-08：禁止改 .cursor/rules
**SECRETS.md 密钥管理**（AGENTS.md 入口）：新 AI 冷启动 MUST 先读 SECRETS.md（密钥文件分布/读取接口决策树/新增密钥三步流程），否则用裸 `os.getenv` 会被 `bare_getenv_gate` 拦截

---

### Step 1 · 文档审查

**何时触发**：施工 AI 接到施工任务后第一步
**前置条件**：Step 0 完成 / 待施工文档 frontmatter status=active（draft 文档先回讨论环节补齐）
**操作摘要**：按 AI_review_instructions 12 节指令审查文档完整性 / 施工算法成熟度 / 四图对齐情况
**引用真源**：[AI_review_instructions.md](../../../_archive/AI_review_instructions.md)（审查指令集真源，不重复内容；**status=deprecated**——2026-08-28 Owner 裁定归档不删不再更新，现行审查机制=本 SOP+68 号审查流水线 `code_review_ai.py` active）
**执行要点**：
1. 按改动分类（A/B/C/D/E）跳过不适用的审查条款
2. 逐节核查：工作完成性 / 责任唯一 / 向内收 / 文件夹容量 / AI 可发现性 / 红蓝对抗 / 命名路径 / 影响同步 / 版本控制 / 文件元数据 / depgraph 登记审查结论与零问题闭环
3. 审查结论**直接在对话里给出**，禁止创建任何报告文件（MD/txt/json 等一律不创建）

**通过判据**：AI_review 12 节全部 PASS / 已知 GAP 已记录在 design_memo 或 ARCH 条目
**不通过处置**：发现 GAP → 回讨论备忘补齐施工算法/接口签名/状态机 → 重新审查（禁止边审边改，按"先报告→再修复→再自检"分轮处理）
**产出物**：审查结论（对话内）+ GAP 清单（如需回补则登记在 design_memo 或新建 ARCH 条目）
**交易决策地图逐层讨论任务加读**（2026-09-05 v1.5.5）：地图血肉填充的每层讨论（板块层/个股层/买卖点层/持仓流/离场流/组合流/币圈）MUST 先过 [trading_decision_map_layering_sop.md](../trading_decision_map_sop/trading_decision_map_layering_policy.md) 四道前置检查（①已有资产盘点五选一处置 ②四路外部调研 ③上层完整性检查 ④枝干分级检查）——检查通过后的落盘与提交回归本 SOP Step 2-12 标准施工闭环。防撞车/防越级/防枝末先行（事故案例：情绪六段 vs 已有情绪周期五态词汇撞车）。
**地图定位声明**（layering SOP §2，2026-09-05 Owner 裁定）：交易决策地图=**唯一动作流程真源**（"这个项目怎么交易的就看这张图"）——同等职责文档一律按第一性原理判定后吸收进节点；节点规范 v1.3 七要素+五联锚（strategy_refs/factor_refs/data_refs/algo_refs/module_id+module_ref），algo_refs 指向算法库条目（REG-IND-001 IND-* / REG-EXA-001 EXA-*，条目自身索引代码）而非文档，公式细节走 doc_ref 指向算法附件。

---

### Step 1.5 · 创建前搜索（仅新建模块触发）

**何时触发**：施工涉及新建模块/蓝图/代码文件/门禁时
**前置条件**：Step 1 通过
**操作摘要**：三重搜索（SearchCodebase+Grep+注册表）+ 复用决策
**引用真源**：[trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) §phase_1_search / [trae_002_anti_orphan_search_first.yaml](../../rules/trae_002_anti_orphan_search_first.yaml) §search_first（2026-10-04 更正：原引 §rule_eight 该册无此锚——R-09）
**执行要点**：
1. 关键词全局搜索（SearchCodebase + Grep on scripts/+src/zephyr/+tests/）
2. 注册表精确匹配（读 [docs/registry_of_registries.yaml](../../_registry/catalogs/registry_master_index.yaml) → 对应 REG-* → 对照）
3. 复用决策（按覆盖率四档：完全覆盖→直接用 / 80%→扩展已有 / 50%→重构+扩展 / 完全不覆盖→进 Step 2）

**通过判据**：[REUSE-DECISION] 标注 + 覆盖率证据
**不通过处置**：找到覆盖 → 走复用决策；完全覆盖 → 放弃新建
**产出物**：复用决策记录（对话内）
**修改已有文件场景**：跳过本步（走 [trae_001_file_operation_security.yaml](../../rules/trae_001_file_operation_security.yaml) RULE-ZERO 锁协议）
**设计意图查询真源**（[trae_083_design_intent_source_discipline.yaml](../../rules/trae_083_design_intent_source_discipline.yaml)）：问题类型三分法——结构状态→depgraph / 设计意图→`D:\临时工作区\依赖图\*.md` / 规则数据→YAML；弃用/重复判定 MUST 双源对比（设计文档 vs depgraph），禁单凭 depgraph 或孤立信号直接弃用（2026-08-01 D_REPORTING 7 模块误删事故根因）
**向内收三原则**（[trae_060_inward_consolidation.yaml](../../rules/trae_060_inward_consolidation.yaml)）：①能现成不创造（先搜索，禁止同步复制）②创造必全自动（事件驱动，禁 cron/Timer/CircadianScheduler/进程内调度器）③第一性原理治本（质疑元问题，禁只治标）

---

### Step 1.8 · 架构评审门控判定（4 种变更触发）

**何时触发**：变更类型为以下 4 种之一时
- 新增模块
- 删除模块
- 修改模块间接口
- 更换核心技术栈
- 修改数据流方向

**前置条件**：Step 1.5 通过
**操作摘要**：架构评审 6 项清单（KB 冲突/循环依赖/可观测性/数据一致性/回滚方案/性能/文档清单）
**引用真源**：[trae_036_arch_gate_transition.yaml](../../rules/trae_036_arch_gate_transition.yaml) §gov_arch_002
**执行要点**：
1. 逐项检查 6 项清单（KB 决策冲突/跨层循环/可观测性/数据一致性/回滚方案/性能退化/文档更新清单）
2. 评审记录存放于 `docs/_working/archive/2026-09/audit/architecture-reviews/YYYY-MM-DD-变更简述.md`（2026-09-24 实测在档位置；原写路径 docs/_working/audit/architecture-reviews/ 不存在——R-11）
3. 评审必须由 Owner 亲自执行或书面委托

**通过判据**：6 项清单全 PASS + 评审记录已落盘
**不通过处置**：任一否决条件命中 → 重新设计消除冲突 → 重新评审
**产出物**：评审记录 MD 文件
**豁免场景**：纯内容修改（不改文件结构/不改路径/不改接口契约）可豁免
**架构变更分级**（[trae_049_ops_domain_manual.yaml](../../rules/trae_049_ops_domain_manual.yaml) OPS-DEV-002）：
- **L1 微调**：无需审批，PATCH+1
- **L2 局部变更**：同层 Owner 审批，MINOR+1
- **L3 跨层变更**：KB 决策记录+Owner 审批+更新 `cross_layer_contracts.yaml`+全量集成测试，MAJOR+1
- **L4 架构变更**：Emergency Change Board+分阶段执行+全量回归
- 每级含回滚方案
**治理顺序因果链**（[trae_017_arch_governance_order.yaml](../../rules/trae_017_arch_governance_order.yaml)）：治理按因果链执行——架构决定→结构重构→元数据对齐→质量补全（前层决定后层是否还需做）；先架构后测试（重构改代码测试白写）；价值判定三步审判（独立功能价值/客观原因/重建成本，ANY 为 YES 则保留，禁用"零消费者"判删除）

---

### Step 1.9 · 方案挖矿（施工前先做方案：方案先挖矿，把矿挖干再施工）

**何时触发**：任务涉及“建策略/建方案/建设计文档/调研选型”等**内容产出**时（[mining_sop_policy.md](../mining_sop/mining_sop_policy.md) §1 触发表）——施工编码（Step 4）前 MUST 有已挖干的方案背书；纯代码修改、已有 active 方案且方案含挖矿日志的任务可跳过本步

**前置分支（新域开工/新建骨架）**：任务若属「新建某域骨架/域开工」类（先有分类学清单，再有方案），先走 [skeleton_mining_policy.md](../mining_sop/skeleton_mining_policy.md)（骨架先挖根：四层分层/三问停止判据/状态纪律/封矿判据）——骨架产出的 ⬜ 条目才是本步挖矿的对象；骨架未建即提方案 = 无根方案
**前置条件**：Step 1 文档审查完成（方案缺失或仍是 draft → 先回本步产出/补齐方案，禁止边施工边写方案）
**操作摘要**：方案动笔前先按六向寻路挖矿（每向=内部反查+全网搜索双动作）→ 防噪音四闸过滤 → 矿脉枯竭封矿（挖干）→ 挖矿日志写进方案 → 挖后自审闸（mining_sop §6：按终局全貌判过度工程）→ 方案定稿后才进 Step 2 设计态登记
**引用真源**：[mining_sop_policy.md](../mining_sop/mining_sop_policy.md)（通用研究方法论真源，不重复内容）；TDM 地图域专用实例=[trading_decision_map_pathfinding_policy.md](../mining_sop/trading_decision_map_pathfinding_policy.md)（方法论冲突时地图域以 TDM 版为准，其余域以本真源为准）
**执行要点**：
1. **先方案后施工**：Step 4 施工编码前 MUST 存在定稿方案（design_memo/施工图），禁止无方案直接施工
2. **方案先挖矿**：按六向寻路扫全（①上游 ②下游 ③算法/机制 ④后端 ⑤前端 ⑥数据字段），内部反查优先、全网搜索补盲，每向产出 ≥1 条发现或“已查无”（查无也是有效结论，记档）
3. **挖干判据（唯一）**：矿脉枯竭=六向全部“已查无”+无未挖长尾（无轮数/深度/候选数上限，noise 只记档不终止）；时间盒封批 ≠ 挖干，封批 MUST 登记长尾矿脉清单排下批
4. **日志纪律**：挖矿日志表（轮次/矿脉/判定/关键产出）MUST 写进方案的“挖矿增补”章节——无日志=没挖过，Step 6 长清单审查按无方案回炉
5. **防噪音四闸**：来源可溯（URL+发布方+年份，禁模型记忆 fallback 假引文）/交叉验证（关键结论 ≥2 独立来源）/A 股适配（T+1/涨跌停改造检验）/可回测+数据可得，逐条过闸后才算发现
6. **世界地图完备优先**：挖矿阶段禁以“先施工”中断（候选数不是停止判据，候选多=富矿信号，禁因多停挖）；全貌地图挖尽后由挖后自审闸统盘裁定建/合/废/挂，防边挖边建返工；明确“不做”的也要留痕防重复挖
7. **挖后自审闸**：方案成稿、施工立项前 MUST 过 mining_sop §6——量尺=终局全貌（Owner 终局只做四类事：账号注册/API 申请/各类充值/策略转正审批，其余全自动化），主判据=是否消灭人工参与，“现状规模小/频次低”禁作封矿理由；三态裁定=施工/挂起排期/方案封矿，裁定留痕进方案
**通过判据**：方案已定稿 + 挖矿日志齐全 + 矿脉枯竭封矿（六向全查无+无未挖长尾）或封批长尾已登记 + 挖后自审闸三态裁定已出并留痕（施工/挂起排期/方案封矿）
**不通过处置**：方案缺失/无挖矿日志 → 回本步补挖，禁止进 Step 2；搜索受阻（429）→ 60-130 秒间隔单发重试（禁连发硬砸），受阻记档不算查无
**产出物**：含“挖矿增补”章节与“挖后自审”三态裁定的定稿方案
**与相邻步骤的边界**：Step 1.5 创建前搜索=代码/模块复用反查（RULE-CAPABILITY-LOOKUP 管辖，写代码前）；本步=内容方法论挖掘（写方案前）——写代码之前不挖、写内容之前必挖（mining_sop §1 明示）


---

### Step 2 · 全景图登记（设计态先行）

**何时触发**：Step 1.8 通过（或豁免）
**前置条件**：文档审查通过 + 创建前搜索已完成 + 架构评审已通过（涉方案/策略/设计文档产出的任务，另需 Step 1.9 方案挖矿已挖干）
**操作摘要**：apply_depgraph 登记模块依赖到设计态 status=planned + 模块准入四级筛选
**引用真源**：[trae_080_panorama_alignment.yaml](../../rules/trae_080_panorama_alignment.yaml) §panorama_alignment / [trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) §phase_2_design_state / [trae_032_module_lifecycle.yaml](../../rules/trae_032_module_lifecycle.yaml) §mod_001
**执行命令**：

```powershell
# 1. depgraph 设计态节点创建（L1 依赖关系先行铁律）
python scripts/governance/apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID planned
python scripts/governance/apply_depgraph.py --add-edge ...

# 2. 模块准入四级筛选（MAD-001~005）
# MAD-001 层归属 / MAD-002 Phase 相关性 / MAD-003 依赖合规 / MAD-004 接口来源 / MAD-005 P0 额外条件
# 准入记录：原定 module-id-registry.json admission_records 全仓无此件（R-05）——
# 四级筛选结论现行留痕=depgraph 设计态节点 + 任务卡/ARCH 条目
```

**通过判据**：depgraph planned 节点已创建 / 依赖关系完整 / 启动方式已设计 / 路径预审通过 / 模块准入 PASS
**不通过处置**：依赖缺失 → 回 design_memo 补设计 / 准入未通过 → 暂停等待 Owner 确认
**产出物**：depgraph planned 节点
**L1 铁律**：每个模块施工前（写第 1 行业务代码前）必须已登记到 depgraph 设计态。禁止"先施工后补登记"
**L2 铁律**：写入设计态前确保运营态已就绪（快照对比：apply_depgraph 无 --query-production flag——R-04 实测；现行手段=generate_project_depgraph.py 重建即运营态真源 + diagnose_depgraph.py 诊断，程序化直查走 DatabaseService）
**禁止**：直接 SQL 写入 depgraph（必须通过 apply_depgraph.py）
**架构升级期保护**：depgraph 生成器（generate_project_depgraph.py）在重建运营态时保护设计态节点不被覆盖——`restore_design_data` 恢复 design edges，DELETE 只删非设计态且设计态有同路径的节点（`scripts/governance/generate_project_depgraph.py` §restore_design_data（符号锚））。但**架构升级期仍禁止运行** `--force`，会覆盖全景图（[trae_005_modification_governance.yaml](../../rules/trae_005_modification_governance.yaml)）

---

### Step 3 · 全图全库对齐（align_all 单命令；简称裁定 #ARCH-ALIGN-NAMING-001）

**何时触发**：Step 2 完成
**前置条件**：depgraph planned 节点已登记
**操作摘要**：sync_panorama_module 派生其余三图 + align_all 验证五图对齐 + frontend_map 人工核对（涉前端施工时）
**引用真源**：[trae_080_panorama_alignment.yaml](../../rules/trae_080_panorama_alignment.yaml) §panorama_alignment + [alignment_checklist.md](../governance_sop/alignment_checklist.md) §3（六图对齐规则真源）
**执行命令**：

```powershell
# 1. sync 派生其余三图（apply_depgraph 执行后默认自动触发，也可手动）
python scripts/governance/sync_panorama_module.py --all

# 2. align 六图对齐统一入口（图 1-5 自动 + 图 6 frontend_map 校验内嵌，2026-09-04 六图升级）
python scripts/governance/d5_architecture/generators/align_all.py
```

**对齐图族定义**（张数以 alignment_checklist.md §3 为准，2026-09-05 七图定名后图族继续扩容；简称"全图全库对齐"=#ARCH-ALIGN-NAMING-001）：
1. **depgraph**（真源 PostgreSQL，工具 apply_depgraph.py）
2. **dataflowgraph**（真源 PostgreSQL 3 表，工具 apply_dataflowgraph.py）
3. **decisiongraph**（真源 PostgreSQL 3 表，工具 apply_decisiongraph.py）
4. **blueprint.md**（真源 MD frontmatter，sync_panorama_module 单向派生 4 字段）
5. **battle_map**（真源 PostgreSQL 3 表 battle_map_steps/anchors/edges，工具 apply_battle_map.py）
6. **frontend_map**（真源 `web/frontend_map.yaml` git YAML，2026-09-01 已建；对齐 key=feature_id；FRONTEND-MAP gate 137）
7. **trading_decision_map**（真源 `config/trading_decision_map.yaml` git YAML，2026-09-05 七图升级；对齐 key=TDM-node_id；R1-R12 校验+DECISION-MAP gate 138 恒跑）

**对齐 key**：前四图以 module_id 为对齐 key / 第五图 battle_map 以 step_id 为对齐 key（通过 battle_map_anchors 双向校验）/ 第六图 frontend_map 以 feature_id 为对齐 key / 第七图 trading_decision_map 以 node_id 为对齐 key
**通过判据**：module_id 轴四类问题（孤儿/状态漂移/域不一致/设计态孤立）为 0 或已知可接受 + step_id 轴 BM-INV-001~007 为 0 或 warn-only + frontend_map 功能点 backend_ref 全类型化挂载、与 manifest 无漂移（涉前端时）
**硬阻断**：domain_mismatches>0 / ghost_anchors>0 直接阻断；frontend_ref 悬空=阻断（门禁建成后自动，建成前 Step 10 提交时人工确认）
**不通过处置**：domain 不一致 → 回 Step 2 修正 / 孤儿或状态漂移 → 重跑 sync + align / frontend_ref 悬空 → 挂载 backend_ref 或声明 none+理由
**产出物**：align_all 通过报告（+ 涉前端时 frontend_map 核对结论）
**禁止**：手编派生三图的设计态行（会被下次 sync 覆盖且制造全景分裂）

---

### Step 3.5 · 后端盘点与拆件判定（前端施工前置，Owner 2026-09-04 立规，TRAE-086 §truth_source_wiring + §split_judgment）

**何时触发**：前端页面新建/改造/加数据区块（UI 动了数据面的每一刀）
**前置条件**：Step 1 文档审查完成
**操作摘要**：取数清单 → 后端三查+前端一查 → 三分支决策 → 拆件判定 → 接线验收
**引用真源**：
- [trae_086_frontend_module_construction.yaml](../../rules/trae_086_frontend_module_construction.yaml) §truth_source_wiring（铁律全文）+ §split_judgment（拆件判据）
- [frontend_component_split_sop.md](frontend_component_split_policy.md)（拆件操作闭环——"有得拆"分支的施工路径真源）
- [data_asset_registry.yaml](../../_registry/catalogs/data_asset_registry.yaml)（数据资产登记，查"后端有没有"第二查）
- [alignment_checklist.md](../governance_sop/alignment_checklist.md) §3（frontend_map 前端全景图——查"前端有没有重复造轮子"）
- FRONTEND-TRUTH-SOURCE gate（commit 阶段 warn 兜底，审计 .runtime/gate_audit/frontend_truth_source.jsonl）

**执行要点**：
1. **取数清单**：列出页面需要的全部数据（字段/粒度/刷新节奏）；页面加新区块=重新走本步
2. **后端三查+前端一查**（每条数据需求逐项过）：①`api_server.py` 现有 `/api/` 端点 ②`data_asset_registry.yaml` 数据资产登记 ③其他服务端点 + depgraph 同功能模块 ④`web/frontend_map.yaml` 前端全景图查重（同/近功能点已存在=**复用或扩展**该组件，禁止重复造轮子）→ 后端结论三选一：**有且唯一 / 有重复 / 没有**
3. **三分支决策**：
   - 有且唯一 → `services/api.js` 加 fetch 助手，页面只消费
   - 有重复 → **先治后端**：裁定唯一真源、废弃其余，再接（禁止前端"挑一个好用的接着用"）
   - 没有 → **先建后端**：立项加端点（真源走 registry 登记），端点验收后前端才接线；此前最多画占位骨架，**禁止造数据顶上**
4. **拆件判定**（后端盘点先行供输入——拆件第一判据=数据源边界，没有数据源清单就没法判）：按 TRAE-086 §split_judgment 四判据逐区块过（判据真源=TRAE-086 §split_judgment 单源，此处括注仅导航索引勿独立引用——裁定#372 闸3 D1）：
   - **有得拆** → 转入 [frontend_component_split_sop.md](frontend_component_split_policy.md) 8 步拆件闭环施工（其 Step 3 API 接口=本步"没有→先建后端"分支的落地），拆完回本 SOP Step 4 续行
   - **没得拆** → 直接进 Step 4 施工编码
5. **接线验收**：页面真源徽章亮 + 端点实测返回；演示回退（若有）必须标"断线·演示"（演示诚实纪律，15s 自动重试至真源）
**通过判据**：每条数据需求都有唯一后端真源且前端已接线 + 拆件判定结论留痕（拆/不拆+判据）
**不通过处置**：发现重复真源 → 先治理合并；后端缺失 → 立项建端点，禁止前端自建数据；该拆不拆 → 回拆件闭环
**产出物**：盘点结论+拆件判定留痕（进设计备忘或验收单 ACC-*.yaml）

### Step 4 · 施工编码

**何时触发**：Step 3 五图对齐通过
**前置条件**：depgraph planned 已登记 + 五图对齐干净
**操作摘要**：按设计备忘伪代码/接口签名/状态机落码 + 文件头锚定 + 双轨判定 + git 预算
**引用真源**：
- [trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) §phase_4_blueprint ~ §phase_9
- [trae_047_engineering_file_header.yaml](../../rules/trae_047_engineering_file_header.yaml) §gov_eng_002
- [trae_053_automation_dual_track.yaml](../../rules/trae_053_automation_dual_track.yaml) §rule_fifteen
- [trae_064_git_call_budget.yaml](../../rules/trae_064_git_call_budget.yaml) §git_call_budget
- 各设计备忘 §施工算法章节

**执行要点**：
1. **蓝图创建**（仅新建模块）：按 [blueprint_construction_template.md](../../templates/blueprint_construction_template.md) 模板
2. **文件创建**：用 scaffold.py + 锁协议（[trae_001_file_operation_security.yaml](../../rules/trae_001_file_operation_security.yaml) RULE-ZERO）
3. **路径多维审查**：名字+路径+上层文件夹+容量对齐（[trae_055_arch_domain_capacity.yaml](../../rules/trae_055_arch_domain_capacity.yaml) ARCH-CAP-002：≤150 通过 / >150 必须拆分）
4. **文件头部锚定**：15 字段注释头部（[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]）
5. **启动方式设计**：⚡事件轨（boot_hooks.py 注册 hook_registry.register 或 event_bus.subscribe）+ CI 批量兜底（.github/workflows schedule），禁止 CircadianScheduler/Timer/cron
6. **多注册表同步**：MRS-001~003（[trae_033_module_registration_sync.yaml](../../rules/trae_033_module_registration_sync.yaml)）
7. **git 调用预算**：禁止循环内 subprocess.run(["git", ...])，必须用 GitCommandBatcher 批量化

**通过判据**：代码按设计备忘伪代码落码 + 文件头 15 字段齐全 + 启动方式事件驱动 + 无 git 子进程循环
**不通过处置**：算法缺失 → 回 Step 1 补文档 / 文件头缺失 → 补齐 / 启动方式违规 → 改为事件轨
**产出物**：代码文件（含 15 字段文件头）
**铁律**：每改完一个文件立即 `python scripts/git_guard.py add <file>`（多会话防护，project_memory 教训）
**git 自伤防护**（[scripts/git_guard.py](../../../../scripts/git_guard.py)）：
- L1 止血：`git reset --hard` 有 tracked 未提交修改且未授权 → fail-closed 阻断
- L2 治本：`git checkout --`/`git restore` 文件级自伤检测
- 逃生：`ZEPHYR_FORCE_STASH=1` 环境变量授权放行+记审计
**任务卡系统**（[trae_034_task_card_standard.yaml](../../rules/trae_034_task_card_standard.yaml)，若施工需要任务卡载体）：
- 唯一创建入口：`TaskRepository.create()` 写入 SQLite（`data/databases/governance.db`），.md 为伴读副本
- 33 字段（21 必填+12 选填）：task_id/namespace/title/description/status/priority/phase/execution_model/files_in_scope/deliverables/source_blueprint/source_section/safety_level/directive/classification/ai_autonomy_level/applicable_rules/allowed_touch 等
- 粒度约束（RULE-THIRTEEN，代码强制）：deliverables≤1 / files_in_scope≤3 / acceptance≤1 / 不跨 Phase
- P0 冻结：活跃 P0 任务≥5 冻结新增（P0InflationFrozenError），≥3 黄色警戒需附论证
- 蓝图拆解入口：`BlueprintDecomposer` 从蓝图 §16 施工指引拆解为任务卡（`src/zephyr/governance/persistence/task_repo.py`）
**八指标机械门**（[trae_003_task_granularity_threshold.yaml](../../rules/trae_003_task_granularity_threshold.yaml)）：新代码>50行/涉及>3文件/需读蓝图/Schema变更/depgraph操作/消费者影响>50文件/跨域操作/多步骤>3，任一 YES→走任务系统建卡（TaskRepository.create，禁手写 .md）；建卡后立刻施工不等确认
**并行执行+原子事务**（[trae_004_parallel_atomic_transaction.yaml](../../rules/trae_004_parallel_atomic_transaction.yaml)）：for 循环中 subprocess/多文件独立读写/多 URL 请求 MUST 用 ThreadPoolExecutor(max_workers=8)，禁 multiprocessing；关联修改同一批文件 MUST 同一批完成，禁分多次提交（事务断裂）
**防幻觉四件套**（[trae_006-009](../../rules/trae_006_anti_hallucination_structure.yaml)）：
- 结构追溯：15 字段完整性
- 行为约束：禁 TODO/pass/NotImplementedError，编辑优先禁删+建，最小变更禁顺手重构，假设显式化标记 [ASSUMPTION]
- 输出验证：步骤验证门每步 exit 0 才进下一步，导入前 Grep/Read 确认，自审闭环 5 项，新代码必测
- 安全防护：认证/注入/数据暴露三检查，>3文件/>50行先计划，改前读 [CONSUMERS]+Grep 引用，>30 轮开新会话
**代码组织+类型导入**（[trae_010+011](../../rules/trae_010_code_naming_organization.yaml)）：
- 文件≤300行/函数≤50行/类≤200行/文档≤60K tokens(1200行)超限拆分
- 类型注解分层 mypy（L00-01 strict/L02-08 关键接口 strict/L09-15 public API strict），金额用 Decimal/时间戳用 Timestamp
- 禁 import */禁下层导入上层
- SSoT 守卫：改数据结构先改 YAML→运行生成脚本→审计下游→KB 决策记录
**数据库破坏性操作三步验证**（[trae_063_data_ops_discipline.yaml](../../rules/trae_063_data_ops_discipline.yaml)）：DELETE/REPLACE PARTITION/TRUNCATE/ALTER DELETE 等破坏性操作执行前 MUST 三步验证——①必要性（能否非破坏性替代）②真实性（全字段 GROUP BY HAVING count()>1 查看实际重复行，禁用 count()-uniqExact(排序键)）③可逆性（pg_dump/clickhouse-backup 备份，无备份禁止执行）；证据留档到任务卡 description（2026-07-16 tick_data 21 个月数据误删事故根因）
**RunCommand 命令纯洁性**（[trae_066_rule_seventeen_runcommand_purity.yaml](../../rules/trae_066_rule_seventeen_runcommand_purity.yaml)）：RunCommand 仅允许裸命令格式（python <脚本>.py）；禁 PowerShell 语法（管道/引号/$变量/cmdlet/>重定向/;串联）；禁裸 git 命令（走 git_guard.py 封装）；文件操作用 Read/Write/Edit/Glob/Grep/DeleteFile 工具
**Symbol 约定**（[trae_082_symbol_convention.yaml](../../rules/trae_082_symbol_convention.yaml)）：securities 表三字段——symbol 裸码+exchange 列（SH/SZ/HK/US/CFFEX）+symbol_canonical 派生列；跨表 JOIN MUST 用 symbol_canonical（000001 平安银行 vs 000001 上证指数碰撞）；历史数据零改写（ADD COLUMN MATERIALIZED，禁 ALTER UPDATE）

---

### Step 5 · 单元测试 + 循环验收

**何时触发**：Step 4 代码施工完成
**前置条件**：代码已落码
**操作摘要**：按 trae_035 循环验收协议连续 2 轮 0 错误 + pre-commit 增量守门
**引用真源**：[trae_035_task_construction_verification.yaml](../../rules/trae_035_task_construction_verification.yaml) §task_003_circular_acceptance / [trae_084_precommit_incremental_discipline.yaml](../../rules/trae_084_precommit_incremental_discipline.yaml)
**执行命令**：

```powershell
# 1. 运行验收命令（acceptance 中的命令 + post_sync_standard 中的命令）
# 典型：pytest tests/<模块路径>
pytest tests/path/to/test_xxx.py -v

# 2. 记录错误数 E1
# 3. 若 E1>0 修复所有错误 → 重新运行 → 记录错误数 E2
# 4. 直到连续两次验收错误数=0 才算 COMPLETED（CIRCULAR_ACCEPTANCE_ROUNDS=2）
```

**pre-commit 增量守门**（[trae_084](../../rules/trae_084_precommit_incremental_discipline.yaml)）：
- commit 阶段 hook 只检查 staged 新增文件（pass_filenames: true + 增量模式参数）
- 全仓扫描移至 stages:[manual]（仅手动/CI 触发）
- 历史违规归档为已知技术债，登记在 ARCH 条目 impact 字段，不卡日常 commit
- 显示二元化：actual_blocking vs warn_only_count

**测试面清单**（2026-09-06 立规，Flash 批二 A 项域测试执行偏差教训固化）：
- 批量施工（driver/逐前缀/逐模块循环）启动前，必须先罗列本批改动的**测试面清单**：受影响域的测试文件/目录全集（`rg -l "<改动模块名>" tests/` 或按 `tests/<域路径>/` 圈定）
- 每施工单元的验证 = 六断言（若涉错误码）+ 语法校验 + **测试面清单全量 pytest**，三者缺一不可；仅跑前两项即声明完成 = 执行偏差
- 批量收尾必须留存测试面清单文件（如 `.runtime/tmp/<批次>_tests.txt`）+ 全量结果（passed 数）供复查——当日实证：227 文件 4991 passed 补课即靠此清单复跑

**状态词表出厂纪律**（2026-09-22 立规，裁定#398五①+#399四授权，真源=docs/_working/vocab_legislation/01_official_state_vocabulary.md + 02_state_vocabulary_mapping_register.md；执法门观察期由 rule_audit 线另行施工）：
- 新模块状态输出必须引用官方词表（`zephyr.shared.vocab.market_state` 四轴常量）或在词表映射登记册登记映射；描述"市场最坏状态"一律走官方归一表 EXTREME_STATE_ALIASES→m.regime.r10，禁裸字符串 r1-r4 跨轴使用（C1 撞名）；无登记的新封闭状态枚举=验收不通过（W3 观察期先 warn）

**通过判据**：连续 2 次验收 0 错误（CIRCULAR_ACCEPTANCE_ROUNDS=2）
**不通过处置**：3 轮修复仍无法归零 → 标记 FAILED 升级 Owner
**产出物**：测试报告（对话内）
**禁止**：单次 0 错误就声明 COMPLETED
**测试残留清理**（[trae_071_temporary_file_lifecycle.yaml](../../rules/trae_071_temporary_file_lifecycle.yaml) §test_residue_reclaim L414）：
- 双层清理：①`tests/conftest.py:pytest_sessionfinish` 源头清 basetemp ②`GATE-RUNTIME-CLEANUP` post-commit reconciler 兜底（shutil.rmtree + PID 存活+TTL 双判定，ttl_seconds=7200）
- 测试残留目录前缀：pytest_<PID>/git_guard_test_*/conc_mv_*/rb1_ 等
- TEST-SOURCE-CONSISTENCY gate：检测 staged tests/ .py 文件中 `from zephyr.xxx import yyy` 的 yyy 符号是否在源码中存在（防测试漂移，module-level pytest.skip/importorskip 豁免）
- TEST-RESIDUE-SSOT gate：检测 src/zephyr/ 下 .py 文件是否硬编码测试残留目录前缀（真源从 trae_071 YAML 动态加载）

---

### Step 6 · 长清单审查（12 节全维度对抗审查）

**何时触发**：Step 5 测试通过
**前置条件**：循环验收已通过
**操作摘要**：按附录 A 长清单审查 12 节执行对抗审查（改动分类/完成性/责任唯一/向内收/容量/AI 可发现/红蓝对抗/命名/影响同步/版本控制/元数据/depgraph 登记）
**引用真源**：本 SOP §附录 A（全文收录用户提供的 12 节审查清单）+ [trae_081_audit_dimensions_framework.yaml](../../rules/trae_081_audit_dimensions_framework.yaml)（54 维度基座，长清单是子集）
**执行要点**：
1. **先做改动分类**（0.5 节）：A 类轻量/B 类新建功能/C 类永久系统/D 类依赖变更/E 类规则契约——决定后续每条 [适用:X类] 执行与否
2. **逐节执行**：每节标注 PASS/FAIL/N/A，FAIL 项就地修复
3. **分轮处理**：先报告→再修复→再自检，禁止边审边改
4. **审查结论在对话内给出**，禁止创建报告文件

**通过判据**：12 节全部 PASS / FAIL 项已就地修复并自检通过
**不通过处置**：FAIL 项无法就地修复 → 回 Step 4 修复 → 重审该节
**产出物**：审查结论（对话内）+ 跳过条款清单+跳过理由（来自 0.5 分类）
**遗留项登记**（防止遗忘）：审查中发现的遗留项（如文件被其他会话占用无法同步、无法访问 worktree 验证等）MUST 登记到统筹会话的 `docs/_working/archive/2026-09/design_memos/construction_progress_tracker.md` §六遗留项登记表（该登记面已随裁定#384 归档；活跃会话的遗留项现行留痕=handoff 交接包，见 Step 0），含：遗留项描述/来源施工队/原因/待办条件/状态。bm-fill 或其他会话释放后逐项闭环。**禁止不登记就跳过——未登记的遗留项=必忘项**
**方法论根因分析**（[trae_024_methodology_diagnosis.yaml](../../rules/trae_024_methodology_diagnosis.yaml) MTH-006）：修复问题时修改既有产物即触发——追问到底+诊断反转验证，禁第一个为什么就停（治本关键）；标准先行（查专业框架映射表）+架构上下文自检（文件操作前定位架构层）+决策质量四问（埋雷/容量/对标/建议）+SSoT 冲突裁决（时序/职责/先例）+补漏与终止双检
**漂移检测套件**（[trae_016_arch_drift_detection.yaml](../../rules/trae_016_arch_drift_detection.yaml) + 脚本）：
- 契约代码漂移：`scripts/governance/d5_architecture/checkers/check_contract_code_drift.py`
- LoadPath 完整性：`scripts/governance/d5_architecture/validators/validate_load_path_integrity.py`（改 AGENTS.md 后必跑）
- 配置漂移：`scripts/governance/d1_structure/validate_config_integrity.py`
- 断链/相对引用检测：`scripts/governance/d2_links/`
- 废弃路径写入/分裂删除引用：`scripts/governance/d4_paths/`
- 孤儿文档/重复规范语言：`scripts/governance/d9_knowledge/`

---

### Step 7 · 更新施工文档

**何时触发**：Step 6 长清单审查通过
**前置条件**：审查遗留项已登记（tracker 原登记面已随裁定#384 归档至 docs/_working/archive/2026-09/design_memos/；现行留痕=handoff 交接包，见 Step 0——不要求零遗留，但要求已登记）
**操作摘要**：设计备忘 frontmatter 升版 + 正文施工完毕标注 + 已施工设施盘点补模块路径 + 00_index 同步
**引用真源**：[01_design_memo_management_spec.md](../../../_working/archive/2026-09/design_memos/01_design_memo_management_spec.md) §5.3 + [trae_052_cross_blueprint_change_cleanup.yaml](../../rules/trae_052_cross_blueprint_change_cleanup.yaml) §rule_eleven（跨蓝图变更通知）
**执行要点**：
1. **设计备忘 frontmatter**：status→active（如原 draft）/ version+1（如 v1.0.0→v1.1.0）/ last_updated→今日
2. **正文 §施工完毕标注**：在 §施工算法章节顶部加 "**已施工**（commit XXXXX）" 标注
3. **§已施工设施盘点补模块路径**：补 `src/zephyr/...` 实际路径 + 测试数 + commit hash
4. **00_index §0 目录同步**：状态列版本号对齐 + §7.3 占用表状态列对齐（00_index_trading_decision.md 已随裁定#384 归档至 docs/_working/archive/2026-09/design_memos/；活跃施工文档索引面现由各册 index.md 与 alignment_checklist.md 承担）
5. **跨蓝图变更通知**（RULE-ELEVEN，[trae_052](../../rules/trae_052_cross_blueprint_change_cleanup.yaml)）：修改任何蓝图的接口契约（Collection 名/API 签名/数据格式/依赖方向）时
   - STEP1 识别消费方：Grep 全项目引用该接口的所有蓝图/代码
   - STEP2 同步更新：所有消费方蓝图 §4 + 代码常量/调用同步修改
   - STEP3 验证：端到端测试确认消费方仍能正常调用

**通过判据**：设计备忘 frontmatter/正文/设施盘点三处对齐 + 00_index 同步 + 跨蓝图消费方已同步
**不通过处置**：文档与代码漂移 → 回 Step 4 修正 / 跨蓝图未同步 → 补 STEP2
**产出物**：更新后的设计备忘 + 更新后的 00_index
**禁止**：改了接口但不 Grep 消费方（遗漏消费方→生产故障）
**文档规格化三清单**（[trae_030_doc_numbering_metadata.yaml](../../rules/trae_030_doc_numbering_metadata.yaml) GOV-DOC-011/016/017）：
- 产出物规格化三清单：可删 11 类/不可删 18 类/必须补充 10 类
- 纯陈述原则：正文只承载当前真实值，禁过渡文本标注，历史差异走 git log
- 规则抽象性：规则中数字 MUST 是阈值非事实状态（文件大小/节点数通过动态查询获取）
**删除安全门禁**（[trae_029_doc_operation_security.yaml](../../rules/trae_029_doc_operation_security.yaml) GOV-DOC-007）：删除文件强制三问（不在锚点列表/已提取价值/无引用）+三步（Grep 引用→同 commit 更新→确认断链）+7 个锚点文件禁删（rule_catalog_registry.yaml/architecture_contract.yaml/trae_041/index.yaml/AGENTS.md/.pre-commit-config.yaml/.roomodes）+断链阈值（生产≤100/过渡≤500/>500 阻断 commit）
**架构版本化**（[trae_037_arch_qualification_versioning.yaml](../../rules/trae_037_arch_qualification_versioning.yaml) GOV-ARCH-003）：version X.Y.Z 递增——Patch 文字修正/Minor 新增章节/Major 架构方向变更；Minor 及以上记修订记录；代码 PR 必须引用架构文档版本

---

### Step 8 · 全景图状态流转（design→production）

**何时触发**：Step 7 文档更新完成（**仅限主工作区直接施工场景**；worktree 隔离施工见下方分流）
**前置条件**：文档已对齐
**操作摘要**：apply_depgraph 状态流转 + 重生成 battle_map + 重生成 path_tree + 三方对齐验证 + diagnose
**引用真源**：[trae_080_panorama_alignment.yaml](../../rules/trae_080_panorama_alignment.yaml) §panorama_alignment（转正流程） / [trae_056_module_creation_workflow.yaml](../../rules/trae_056_module_creation_workflow.yaml) §phase_10 / [trae_035_task_construction_verification.yaml](../../rules/trae_035_task_construction_verification.yaml) §task_003_panorama_alignment

**场景分流（2026-08-14 裁定，#ARCH-SELL-001 / #ARCH-70 实证）**：

- **worktree 隔离施工（默认，#ARCH-AICOLLAB-001）**：会话内**只登记不流转**——
  `apply_depgraph.py --add-design-node/--add-design-edge` 登记 design 态节点与设计态边
  （design 行被全量重建 DELETE 豁免保护），并在完工反馈登记遗留项。
  **禁止会话内流转 production**：运营态节点以主工作区磁盘为锚，worktree 内流转后
  下一次 GATE-DEPGRAPH-OPS 重建会把节点 DELETE（文件不在主工作区磁盘）。
  merge 回 dev 后无需手工动作——#ARCH-70 同身份 UPDATE 通道在第一次重建时自动
  转 production（node_id 不变、edges 不断链、build_status 按"production+test→stable"
  推导）。**merge 执行人职责**：重建后实证核验节点双态 + 闭环 tracker 遗留项
  （2026-08-14 SELL 4 节点 + POS-020/021 实证通过）。
- **主工作区直接施工（非 worktree）**：手工流转用合法命令——
  `python scripts/governance/apply_depgraph.py --transition-design-maturity <NODE_ID> production`。
  ⚠️ 注意 `production` 同时是 `design_maturity` 与 `build_status` 两字段的合法值，
  两字段正交——design_maturity 管"纸面 vs 物理存在"，build_status 管生命周期成熟度。
  `build_status` 合法值为 planned/generated/testing/stable/deprecated/production 六态
  （B-007 前置批 P0 2026-08-26 扩展，单调推进链，trae_054 §build_status）：
  `--transition-build-status <NODE_ID> production` 仅 stable 节点可转
  （testing 节点须先转 stable 再走 stable→production 两步法，禁跳态）。
  稳定度提升用 `--transition-build-status <NODE_ID> testing|stable`。

**执行命令**（主工作区场景）：

```powershell
# 1. depgraph 双态流转 design→production（合法命令，2026-08-14 勘正）
python scripts/governance/apply_depgraph.py --transition-design-maturity NODE_ID production

# 2. sync 自动把 production 状态同步到其余三图
python scripts/governance/sync_panorama_module.py --all

# 3. 重生成 battle_map（从 depgraph 派生当前状态视图）
python scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py

# 4. 重生成 path_tree
python scripts/governance/generate_project_path_tree.py --write

# 5. 三方对齐验证（蓝图↔代码↔路径树）
python scripts/governance/d5_architecture/generators/align_all.py

# 6. 依赖图诊断
python scripts/governance/d5_architecture/diagnose_depgraph.py
```

**通过判据**：depgraph design_maturity=production / 五图对齐通过 / path_tree 无旧引用 / diagnose exit 0
**不通过处置**：对齐失败 → 回 Step 7 修正 / diagnose 错误 → 修复后重跑
**产出物**：全景图对齐通过报告
**禁止**：架构升级期运行 `generate_project_depgraph.py --force`（会覆盖 depgraph 全景图，详见 [trae_005_modification_governance.yaml](../../rules/trae_005_modification_governance.yaml)）

---

### Step 9 · 文件完整性检查

**何时触发**：Step 8 全景图流转完成
**前置条件**：全景图对齐通过
**操作摘要**：git status 确认无回退/无清理 + 对比施工前后 staged 文件清单 + 验证 worktree 修改已 merge 到主树 + held_files 检查
**引用真源**：[65_git_safety_governance.md](../../../_working/archive/2026-09/design_memos/65_git_safety_governance.md) §备份先行 / project_memory #ARCH-GIT-CLEAN-GUARD-FIX 灾难教训
**执行命令**：

```powershell
# 1. git status 确认无回退
git status
git log --oneline -5

# 2. 对比施工前后 staged 文件清单
git diff --cached --stat

# 3. 验证 worktree 修改已 merge 到主树（若使用 worktree）
python scripts/session_worktree.py list
# （2026-10-04 更正：session_worktree CLI 实测子命令=create/exec/merge/abort/list——
#   status 有库函数无 CLI（R-06），worktree 状态经 list 查看机制真源=图11 D11-C11/D11-S07）

# 4. held_files 检查
python scripts/lock_files.py status
```

**通过判据**：所有 staged 文件存在 / 无 git clean 痕迹 / worktree 已 merge（若使用）/ held_files 无冲突
**不通过处置**：文件丢失 → git reflog / dangling blob 恢复（[65_git_safety_governance.md](../../../_working/archive/2026-09/design_memos/65_git_safety_governance.md) §灾难恢复）
**产出物**：完整性确认
**铁律**：所有新建/修改文件必须立即 `git add`（project_memory #ARCH-GIT-CLEAN-GUARD-FIX 教训——git clean -fd 会物理删除 untracked 文件不进回收站）
**工作区治理**（[workspace_governance_policy.md](../../policies/workspace_governance_policy.md) + [scripts/rollback.py](../../../../scripts/rollback.py)）：
- auto-sync 产物还原优先：git checkout 还原 auto-sync 产物，禁手动提交残留（工作区永远有 modified 噪音）
- .gitignore 维护：.aidrafts/access/metadata/.ailocks 等必忽略
- 会话开始/提交前检查清单
- 回滚系统 CLI：`python scripts/rollback.py full_revert|partial_revert|discard|hard_reset|preview|preflight|forward_fix_evaluate|dependency_impact`

---

### Step 10 · GitCommitGateway 落地

**何时触发**：Step 9 完整性确认
**前置条件**：文件完整性已确认
**操作摘要**：走 GitCommitGateway 网关提交 + stash 生命周期检查 + pre-commit 增量守门
**引用真源**：[66_commit_queue_serialization.md](../../../_working/archive/2026-09/design_memos/66_commit_queue_serialization.md) / [trae_075_stash_lifecycle.yaml](../../rules/trae_075_stash_lifecycle.yaml) / [trae_084_precommit_incremental_discipline.yaml](../../rules/trae_084_precommit_incremental_discipline.yaml)
**执行命令**：

```powershell
# 1. 走 GitCommitGateway 网关提交（禁止裸 git commit；正门 CLI=scripts/git_commit.py，
#    原 scripts/git_commit_gateway.py 不存在——R-03）
python scripts/git_commit.py --session <sid> --files <清单>
# （worktree 模式同样走 git_commit.py；session_worktree 无 commit/status 子命令——R-06，
#   库函数 session_worktree_commit 由网关内部调用）

# 2. stash 生命周期检查（STASH-ACCUMULATION gate）
# - stash list > 40 → 阻断 commit
# - 20 < count <= 40 → warn 不阻断
# - AI 前缀 + age > 4h 的 stash 自动清理（GATE-STASH-LIFECYCLE reconciler）
```

**提交方式优先级**（[project_memory](file:///c:\Users\fanzi\.trae-cn\memory\projects\-d-ZephyrAlpha--p2-1c552864b6a6a396cfb0\project_memory.md)）：
1. worktree session_worktree_commit（首选）
2. GitCommitGateway（次选）
3. 裸 git commit（**禁止**）

**GitCommitGateway 工作流详解**（[src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py](../../../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)）：
- **入队前**：
  - `claim_files`：为 session 声明持有本次 commit 的文件，捕获基线快照（`git diff HEAD -- <file>`）供 FOREIGN-CHANGE gate 检测搭便车，持久化到 `.runtime/claim_snapshots/{session_id}.json`（S3-C 治本：进程崩溃可恢复）
  - `adopt_prior_work=True`：认领前序未提交变更——审计记录基线 diff_size+sha256+domain 到 `.runtime/claim_snapshots/{sid}_adopted.jsonl` 但存储空基线让 FOREIGN-CHANGE gate 放行（替代 stash 舞蹈/逃生通道）
- **队列处理**：
  - `_GlobalCommitLock` 跨进程串行锁（`.ailocks/git_commit_global.lock`，TTL=1800s），os.open O_CREAT|O_EXCL 原子创建
  - 僵尸锁检测：持有进程 PID 已死亡时立即清理零窗口期
  - fail-open 降级：锁获取失败时落审计 `.runtime/gate_audit/commit_lock_fallback.jsonl`
  - `run_git` commit 守卫：检测裸 `git commit` 且 `in_commit_flow` 标志 False 时拒绝执行（红攻 1 治本）
  - git 命令 timeout 分级：read 类 15s / write 类 60s / 其他 30s
- **入队前 gate 检查**（in-process gate 总数以 in_process_gate_registry.yaml 计数字段为准，勿在散文写死——[src/zephyr/gov_enforcement/commit_gates/](../../../../src/zephyr/gov_enforcement/commit_gates)）：
  - 注册制：`gate_auto_registrar.auto_register_gates` YAML 驱动自动注册，替代硬编码 `_check_*`
  - 关键 gate（按 priority 排序）：HELD-OVERLAP(50)/CLAIM-REQUIRED/WORKTREE-REQUIRED(44)/FOREIGN-CHANGE(45)/COMMIT-SCOPE(48)/NEW-FILE-DEPGRAPH-ENFORCEMENT(58)/DIRECTORY-CONTRACT/TTL-METADATA/FILE-PLACEMENT-TTL/RENAME-DEPGRAPH-SYNC(39)/BLUEPRINT-NODE-ID-HARDCODE(57)/CAPABILITY-LOOKUP-REQUIRED/TEST-RESIDUE-SSOT/TEST-SOURCE-CONSISTENCY/NO-SECRET-HARDCODE（2026-10-04 更正实名——R-14）/PURE-SHIM 等
- **出队后 post-commit reconciler**（40+ 个，[git_commit_gateway.py](../../../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) §`_register_default_reconcilers`（符号锚））：
  - 异步执行框架：`reconcile_runner.launch_reconcile_async` spawn detached worker subprocess（DETACHED_PROCESS on Windows）
  - status file 持久化：`.runtime/reconcile_reports/reconcile_status_<sha>.json`
  - 孤儿扫描：`sweep_stale_workers` 主动扫描（running 超 30min + PID 死→改 stale）
  - 心跳信号：`write_heartbeat` 每个 reconciler 执行前刷新 `last_heartbeat_at` + `current_reconciler`
  - AI 查询进度：`query_reconcile_status` 命令
  - 完整 reconciler 清单见 §附录 C

**通过判据**：commit hash 已生成 / pre-commit 全量通过 / stash list 正常 / 40+ reconciler 异步执行中
**不通过处置**：网关拒绝 → 回 Step 6 长清单审查 / stash 阻断 → 清理 stash 后重试 / reconciler 失败 → 查 `.runtime/reconcile_reports/` 日志
**产出物**：commit hash
**铁律**：
- 禁止 `--no-verify` 绕过 pre-commit（[project_memory](file:///c:\Users\fanzi\.trae-cn\memory\projects\-d-ZephyrAlpha--p2-1c552864b6a6a396cfb0\project_memory.md)）
- 禁止裸 `git commit`（pre-commit 框架全树 stash 会冲掉其他会话暂存，[66_commit_queue_serialization.md](../../../_working/archive/2026-09/design_memos/66_commit_queue_serialization.md) §2.1 事故 1）
**commit 四件套**（[trae_072](../../rules/trae_072_cross_commit_atomicity.yaml)+[trae_073](../../rules/trae_073_precommit_offline_discipline.yaml)+[trae_068](../../rules/trae_068_preventability_layer.yaml)+[trae_069](../../rules/trae_069_commit_gateway_abuse_thresholds.yaml)）：
- 跨 commit 原子性：同功能多文件同 commit，跨 session 依赖登记 depends_on_sessions，GATE-IMPORT-INTEGRITY 硬阻断悬空 import
- pre-commit hook 离线纪律：禁外部 repo/local hook language:system/纯 stdlib，删"双防线"（网络依赖会卡死 commit）
- 第 6 层可预防性：post-only reconciler MUST 评估前移 pre-commit gate
- 滥用监控 6 维阈值：warn_only 50/24h、emergency_commit 5/24h、allow_overlap 30/7d、forged_gw_marker 3/24h、non_gw_commit 10/24h、force_merge 5/7d+健康度评分

---

### Step 11 · 临时文件清理（只清自己，不动他人）

**何时触发**：Step 10 commit 落地
**前置条件**：commit 已落地
**操作摘要**：按三级分类清理本会话产生的临时文件 + .ailocks 释放 + session_worktree 标记可清理
**引用真源**：[trae_071_temporary_file_lifecycle.yaml](../../rules/trae_071_temporary_file_lifecycle.yaml) / [trae_035_task_construction_verification.yaml](../../rules/trae_035_task_construction_verification.yaml) §task_closure_standard 清扫三步法
**三级分类**（[trae_071](../../rules/trae_071_temporary_file_lifecycle.yaml)）：

| 层级 | 内容 | 去向 | 治理 |
|---|---|---|---|
| 成果层 | 分析报告/选股清单/工作文档 | docs/_working/ | git 跟踪 + front-matter + 归档 |
| 暂存层 | 计算中间产物/缓存/调试脚本 | .runtime/sessions/<sid>/staging/ | 免跟踪 + 会话结束自动清理 |
| 系统层 | 锁/会话注册/审计/pid/heartbeat | .runtime/ 现有系统子目录 | 免跟踪 + 现有 reconciler 维护 |

**执行命令**：

```powershell
# 1. 只清理本会话暂存层（.runtime/sessions/<sid>/staging/）
# post-commit reconciler（make_session_staging_lifecycle_reconciler, priority=802）自动触发
# 事件驱动（session_worktree_merge / session_worktree_abort 事件），非时间触发

# 2. 释放本会话 .ailocks
python scripts/lock_files.py release <file> <owner>（逐件释放；会话整体释放=release-all <owner>——2026-10-04 更正命令契约 R-07）

# 3. worktree 可清理判定（若使用 worktree）
# （2026-10-04 更正：mark-completed 子命令全仓无此命令——R-06；
#   可清理判定由 session_worktree_sweep 三重判据自动承担，见 Step 12）
```

**通过判据**：本会话 staging 目录已清空 / .ailocks 已释放 / worktree 标记可清理
**不通过处置**：误删 → git checkout 恢复（仅限 tracked 文件）
**产出物**：清理报告
**铁律**：
- **只清理本会话产生的临时文件，不删其他会话 WIP**（用户原话）
- 禁止根目录直写 .runtime/（必须走 .runtime/sessions/<sid>/staging/ 会话级隔离）
- 系统层文件（锁/pid/heartbeat）由现有 reconciler 维护，AI 不手动清理
**临时文件放置 5 铁律**（[trae_070_temporary_file_placement.yaml](../../rules/trae_070_temporary_file_placement.yaml)）：
- 任务文档→docs/_working/（.md/.csv/.yaml，auto_archive 归档）
- 运行时脚本→.runtime/tmp/（.ps1/.py/.sh/.txt/.log，禁 .md）
- worktree→.aidrafts/{sid}/
- 测试输出分类
- 禁凭方便选择（MUST 查 directory_purpose_classification 表）
- 配 GATE-DIRECTORY-CONTRACT (DCR-008) 硬阻断跨类乱放

---

### Step 12 · worktree 合并与清理（有风险暂不清理）

**何时触发**：Step 11 临时文件清理完成
**前置条件**：临时文件已清理
**操作摘要**：session_worktree merge 回 dev + merge 成功后清理 worktree + 有风险暂保留逃生通道
**引用真源**：[trae_078_force_merge_safety.yaml](../../rules/trae_078_force_merge_safety.yaml) / [trae_076_worktree_commit_persistence.yaml](../../rules/trae_076_worktree_commit_persistence.yaml) / [project_memory session_worktree 隔离施工可靠路径](file:///c:\Users\fanzi\.trae-cn\memory\projects\-d-ZephyrAlpha--p2-1c552864b6a6a396cfb0\project_memory.md)
**冲突处理**：merge 遇冲突 MUST 按 [merge_conflict_resolution_sop.md](../ops_sop/merge_conflict_resolution_policy.md) 执行——冲突三分法（叠加型合并/迭代型取新/互斥型升级用户裁定）+标准 7 步流程，禁止盲选边
**执行命令**：

```powershell
# 1. worktree merge 回 dev
python scripts/session_worktree.py merge <sid>

# 2. merge 成功后清理 worktree
# （2026-10-04 更正：无 cleanup 子命令——R-06；放弃会话=abort <sid>，
#   正常收尾由 sweep 按 stale 判据清理，禁裸 git worktree remove）
python scripts/session_worktree.py abort <sid>
```

**force merge 安全分类**（[trae_078](../../rules/trae_078_force_merge_safety.yaml)）：
- **不可绕过类**（force=True 也不跳过）：
  - commit 持久性验证（_read_commit_persisted_marker + tip hash 对比，[trae_076](../../rules/trae_076_worktree_commit_persistence.yaml)）
  - base 新鲜度检测（_ensure_worktree_base_fresh(stage="merge")）
- **可绕过类**（force=True 可跳过，有 post-merge reconciler 兜底）：
  - WORKSPACE-CLEAN-CHECK（post-commit workspace_hygiene_reconciler 兜底）
  - PRE-MERGE-TOPO-CHECK（post-merge blueprint_frontmatter_reconciler 部分兜底）

**commit 持久性标记**（[trae_076](../../rules/trae_076_worktree_commit_persistence.yaml)）：
- commit 成功后写 `.runtime/locks/commit_persisted_<sid>.json`（含 commit_hash + timestamp）
- sweep 检查 stale worktree 时，24h 内的持久性标记 → sweep 免疫（跳过，不删除 worktree + 分支）

**session_worktree 完整工作流**（[src/zephyr/gov_enforcement/rule_bridge/session_worktree.py](../../../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)）：
- **start**：
  - 自动 spawn detached heartbeat daemon（`heartbeat_daemon.py`），每 30s 调 `registry.heartbeat(session_id)` 刷新 `last_heartbeat`
  - `last_activity` 是独立活性锚点（只由真实治理操作刷新：register/claim_file/register_dependency），daemon 不刷新
  - daemon 主循环 idle 超 `_ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s`（30min）自动退出→90s 后 registry 过期→held_files 释放
  - **三类并发阻断**：
    - ①任务去重（裁定#D）：`task_files` 作为任务文件指纹注册，与活跃 session 的 task_files Jaccard 重叠≥50% 时阻断（DUPLICATE_TASK_BLOCKED），逃生 `allow_duplicate=True`
    - ②治本变更并发阻断（§9.7）：`breaking_change=True` 检查其他活跃 session→有则阻断；`breaking_change=False` 检查是否有其他 session 声明 breaking_change=True→有则阻断避让，逃生 `allow_concurrent=True`
    - ③CROSS-COMMIT-DEP（TRAE-072）：commit 时 `_check_cross_commit_deps` 检查 `depends_on_sessions` 中是否仍有活跃 session→有则阻断（CROSS_COMMIT_DEP_BLOCKED）
- **commit**：在 worktree 内提交，触发 STASH-ACCUMULATION gate（stash list>40 阻断/20-40 warn）+ GATE-STASH-LIFECYCLE reconciler（清理 AI 前缀+age>4h 的 stash）
- **merge**：见上方 force merge 安全分类
- **abort**（[session_worktree.py](../../../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) §session_worktree_abort（符号锚））：
  - 传入 `files` 参数可同时清理主工作区残留
  - tracked 文件 `git stash push` 保存到 stash 栈（可恢复 via `git stash pop`）+ 文件还原到 HEAD
  - untracked 文件物理删除
  - 每次 stash push 后写入 `.runtime/workspace_alerts/stash_notice.json`（含 stash 文件列表 + 恢复命令）
  - **AI 发现编辑"消失"时 MUST 先检查此文件**
  - 执行 `_clean_main_workdir_on_abort` 清理主工作区
- **sweep**（[session_worktree.py](../../../../src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) §session_worktree_sweep（符号锚））：
  - on-demand 清理 stale session worktree 残留
  - 三重保护判据：①目录 age > max_age_minutes（默认 30）②session 不在 active 注册表 ③分支 tip 在 HEAD 祖先或无分支
  - `force_clean_hours > 0` 时对超龄且有未合并提交的 worktree，先保存分支 tip 到 `refs/quarantine/<sid>`（72h 可恢复），再强制清理
  - AI 可主动调用清理崩溃/放弃 session 的残留

**通过判据**：merge 成功 + worktree 已清理 / 或 merge 失败但已走逃生通道
**不通过处置**：
- merge 冲突 → **暂不清理 worktree，保留逃生通道**（用户原话）
- 走 `git checkout <branch> -- <file>` + 主树网关提交（[project_memory session_worktree 教训](file:///c:\Users\fanzi\.trae-cn\memory\projects\-d-ZephyrAlpha--p2-1c552864b6a6a396cfb0\project_memory.md)）
- merge 失败 → 登记 ARCH 条目 + 保留 worktree

**产出物**：worktree 清理确认
**铁律**：
- 1 任务 = 1 start + 多次 Edit/Write + 1 commit + 1 merge（worktree 君子协定）
- held_files 重叠走逃生通道（2026-08-13 裁定更新：`--allow-overlap` AI 可默认使用，前置=已读对方改动按 [67 号](../ops_sop/merge_conflict_resolution_policy.md)三分法判定非互斥；[GW:<sid>:overlap] 留痕 + trae_069 阈值监控兜底，替代原"不当正门用"的事前禁用口径）
**worktree base 新鲜度全生命周期**（[trae_074_worktree_base_freshness.yaml](../../rules/trae_074_worktree_base_freshness.yaml)）：
- 三阶段检测：start(fail-open warning)/commit(fail-closed 阻断)/merge(fail-closed 阻断，薛定谔的回退高发点)
- emergency_commit 主工作区 vs HEAD 一致性检查（warn-only）+reflog 审计标记
- force=True 不可绕过 base freshness（#ARCH-FORCE-MERGE-SAFETY-001 治本）
**分支策略**（[branch_strategy_policy.md](../../policies/branch_strategy_policy.md)）：
- dev 即主分支/master FF 镜像/session/* 命名（sess-NNNNN-YYYYMMDDHHMMSS）
- 3 个月未合并废弃
- 6 条禁止：禁 master commit/禁裸 git commit/禁 push --force/禁议题性分支名

## 4. 关键检查清单（Checklist）

施工闭环 16 项 Yes/No 检查（行数以本表为准，勿在别处写死），全部 Yes 才算施工闭环：

| # | 检查项 | Yes/No |
|---|---|---|
| 1 | Step 0 Session 冷启动完成（守护进程 running=true） | ☐ |
| 2 | Step 1 文档审查 PASS（AI_review 12 节全 PASS） | ☐ |
| 3 | Step 2 depgraph planned 节点已登记 + 模块准入 PASS | ☐ |
| 4 | Step 3 六图对齐通过（align_all.py exit 0 + frontend_map 对齐规则，详见 alignment_checklist.md） | ☐ |
| 5 | Step 4 代码落码 + 文件头 15 字段齐全 + 事件驱动启动 | ☐ |
| 6 | Step 5 循环验收连续 2 轮 0 错误 | ☐ |
| 7 | Step 6 长清单审查 12 节全 PASS | ☐ |
| 8 | Step 7 设计备忘+00_index 同步更新 + 跨蓝图消费方已同步 | ☐ |
| 9 | Step 8 全景图 status=production + 六图对齐 + diagnose exit 0 + 注册表对齐（详见 alignment_checklist.md §4） | ☐ |
| 10 | Step 9 文件完整性确认（无回退/无清理/无丢失） | ☐ |
| 11 | Step 10 GitCommitGateway 落地（commit hash 已生成） | ☐ |
| 12 | Step 11+12 临时文件清理 + worktree 合并完成（或暂保留逃生通道） | ☐ |
| 13 | **Step 3.5 后端盘点与拆件判定完成（前端任务必做）**：每条数据需求有唯一后端真源且前端已接线；有重复真源先治后端；缺端点先建后端；拆件判定结论已留痕（有得拆→拆件 SOP 8 步闭环施工，没得拆→直接施工）；演示回退（若有）已标"断线·演示"（TRAE-086 §truth_source_wiring + §split_judgment + FRONTEND-TRUTH-SOURCE gate） | ☐ |
| 14 | **新建注册表/全景图已挂轴（D38 全图全库对齐铁律）**：本次施工若新建了业务资产库（catalogs/*.yaml）→ 已在 `src/zephyr/trading/decision_map.py` `_XREF_SPECS` 加交叉轴（两行）+ 真源挂载；若新建治理类库 → 已在 `tests/trading/test_decision_map.py::TestNewRegistryGate._GOVERNANCE_EXEMPT` 登记豁免；若新建全景图 → 已以 module_id 为对齐 key 挂入七图体系并在 alignment_checklist.md §3 登记（`tests/trading/test_decision_map.py` 门禁测试强制二选一，漏做必红） | ☐ |
| 15 | **派生残留已收口（2026-09-07 triage 根治）**：会话收尾时跑 `python scripts/governance/commit_derived_sync.py`（先 `--dry-run` 目检）——blueprint 统计区/注册表索引/金标哈希/手册统计块等跨域派生文件一条命令收口；纯信息类（手册 AUTO 块/README 快照）已由 workspace_hygiene_reconciler post-commit 自动还原自愈，无需人工；若 dry-run 显示非派生脏文件，属于未闭环任务须回表处理，禁止搭便车 | ☐ |
| 16 | **Step 1.9 方案挖矿完成（方案/策略/设计文档类任务必做）**：施工前已有定稿方案；方案动笔前已按 mining_sop 六向寻路挖矿；挖干判据=矿脉枯竭（六向全查无+无未挖长尾，无轮数/深度/候选数上限；时间盒封批≠挖干，长尾已登记）；挖矿日志已写进方案“挖矿增补”章节（无日志=没挖过）；世界地图已挖尽（禁边挖边建，建/合/废/挂由自审闸统盘裁定留痕）；挖后自审闸已过（按终局全貌判，三态裁定留痕进方案） | ☐ |

## 5. 边界与不做

### 5.1 不做的事
- **不重复** trae_035/056/080 等规则内容（禁止/必须/约束条件以原文件为准）
- **不替代**任务卡系统（[trae_034_task_card_standard.yaml](../../rules/trae_034_task_card_standard.yaml)，33 字段+粒度约束）
- **不引入**新门禁脚本（复用现有 GitCommitGateway/session_worktree 等）
- **不扩展**到交易决策域外（数据层/基础设施/治理脚本走全局规则）
- **不创建**审查报告文件（审查结论在对话内给出，禁止 MD/txt/json 报告文件）

### 5.2 适用边界
- **适用**：07_trading_decision_architecture 域施工（regime/选股/仓位/风控/买卖/执行/对账/治理）
- **不适用**：数据层（c1_market 等）/基础设施（runtime/locks 等）/治理脚本（scripts/governance）—— 走全局规则

### 5.3 与 trae_056 的边界
- trae_056 是"新建模块"的完整工作流（11 phase，phase_0~phase_10）
- 本 SOP 是"端到端施工流程"（审查→登记→对齐→施工→测试→审查→更新→commit→清理→merge）
- **关系**：Step 4 施工编码时，若涉及新建模块则引用 trae_056 的 phase_4-9；若只是修改已有文件则不触发 trae_056

## 6. 开放问题

| # | 问题 | 决策状态 |
|---|---|---|
| 1 | 是否需要"施工准入"自动门禁（开工前检查前置文档已 active） | 待讨论 |
| 2 | 是否需要"施工完毕"自动回写脚本（自动更新 frontmatter/00_index） | 待讨论 |
| 3 | 长清单审查 12 节是否需要分文档承载（避免 SOP 过大） | 待讨论（当前作为附录 A 全文收录） |
| 4 | 是否在 architecture_issue_registry.yaml 登记 #ARCH-CONSTRUCTION-SOP-001 | 待 Owner 裁定 |
| 5 | 是否需要把 SOP 注册到 [registry_of_registries.yaml](../../_registry/catalogs/registry_master_index.yaml) | 待讨论 |

## 7. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-12 | 1.0.0 | 初稿落盘 | 端到端 15 步施工闭环 SOP 初版，整合 18 项盲点（Session 冷启动/创建前搜索/架构评审门控/五图对齐/模块准入/文件头/双轨/git 预算/跨蓝图通知/三方对齐/临时文件分类/force merge/commit 持久性/stash 生命周期/pre-commit 增量/54 维度/模块创建 10 phase/任务卡 33 字段）；附录 A 全文收录用户提供的长清单审查 12 节 |
| 2026-08-12 | 1.1.0 | 第三轮扫描补充 22 项盲点 | 补充：handoff 交接包/ABS 绝对禁止清单/SECRETS.md 密钥管理/设计意图真源/向内收三原则/架构变更分级 L1-L4/治理顺序因果链/八指标机械门/并行执行原子事务/防幻觉四件套/代码组织类型导入/数据库破坏性操作三步验证/RunCommand 命令纯洁性/Symbol 约定/方法论根因分析/漂移检测套件/文档规格化三清单/删除安全门禁/架构版本化/工作区治理+回滚系统/commit 四件套/临时文件放置 5 铁律/worktree base 新鲜度+分支策略；附录 B 补充 d2/d4/d9 检测脚本 |
| 2026-08-13 | 1.2.0 | Step 6 补遗留项登记机制 | AI-STD-001 审查实践发现：审查遗留项（如文件被占用无法同步）不登记=必忘项。Step 6 新增"遗留项登记"铁律（MUST 登记到 construction_progress_tracker.md §七）；Step 7 前置条件从"审查无遗留"改为"审查遗留项已登记"（不要求零遗留，但要求已登记） |
| 2026-08-13 | 1.3.0 | 附录 A 升级：新增 A.13 五图对齐验证 + A.14 代码质量专项 | 用户提出审查清单老化。对比 trae_081 的 54 维度发现附录 A 12 节未覆盖五图对齐验证和代码质量具体检查点。新增 A.13（五图对齐 7 项，引用 trae_080）+ A.14（代码质量 10 项，从 54 维度选取最关键的 10 个）。附录 A 从 12 节升级到 14 节 |
| 2026-08-13 | 1.4.0 | **搬迁**：从 design_memos/02_construction_workflow_sop.md 迁至 docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md | 用户裁定：design_memos 是施工图纸临时区（施工完毕后清理），SOP 是永久规则，生命周期不匹配。迁入规则管理区新建 sop/ 专区；doc_type architecture_view→policy（rule_form: procedural + verifiability: manual，01 目录契约合规）；去编号改名；全部相对链接按新基址重写 |
| 2026-08-31 | 1.5.0 | **对齐体系升级**：Step 0 必看文件清单新增 alignment_checklist.md；Step 3 从"五图对齐"升级为"六图对齐"（新增 frontend_map 前端全景图，待建）；Step 4/8 检查清单同步升级；新增注册表对齐要求 | 项目对齐体系片段化，缺前端全景图和注册表统一对齐规则；新 AI 进项目不知道要对齐什么。配合《全项目对齐清单》（alignment_checklist.md）落地三层对齐体系（六图+40+注册表+代码文档） |
| 2026-09-04 | 1.5.1 | 新增 Step 3.5 后端盘点（前端施工前置）+ Checklist 第 13 项 | Owner 2026-09-04 裁定"前端不许自建数据世界"（TRAE-086 v1.2.0 §truth_source_wiring 配套）：执行前端任务前 MUST 后端盘点四步（取数清单→后端三查→三分支决策→接线验收），FRONTEND-TRUTH-SOURCE gate warn 兜底；红蓝对抗 9 手法实测（4 击穿已修+2 接受风险文档化） |
| 2026-09-04 | 1.5.2 | Step 3.5 升级"后端盘点与拆件判定"——拆件 SOP 正式接入总流程 | Owner 追问"拆件判定在哪一步"发现两 SOP 断链：Step 0 必看清单+Step 3.5 补 frontend_component_split_sop.md 引用；新增执行要点 4 拆件判定（盘点先行供输入——拆件第一判据=数据源边界；有得拆→拆件 8 步闭环，没得拆→直接施工）；Checklist 13 同步 |
| 2026-09-04 | 1.5.3 | Step 3 正文"五图"→"六图"（frontend_map 已建未入正文）+ Step 3.5 补前端一查 | Owner 追问发现 frontend_map.yaml 已建（2026-09-01）但 Step 3 正文仍是五图对齐——正文与 Checklist"六图通过"自相矛盾；Step 3 标题/定义/对齐 key/通过判据/处置全量六图化（frontend_map=git YAML 真源+feature_id 对齐 key+人工核对，自动门禁待建）；Step 3.5 三查扩"三查+前端一查"（frontend_map 查重：同功能点已存在=复用/扩展，禁重复造轮子） |
| 2026-09-04 | 1.5.4 | Step 3 frontend_map 校验器落地——人工核对升级脚本校验 | Owner 裁定双真源合并+补登专项：check_frontend_map.py 落地（R0 重复/R1 类型化/R2 manifest 双向/R3 file 存在，auto 条目宽严分级）；frontend_map v2.0.0 唯一真源+302 功能点/44 页（详见 alignment_checklist v1.2.0）；Step 3 命令块同步 |
| 2026-09-05 | 1.5.5 | Step 1 新增"交易决策地图逐层讨论任务加读"+Step 0 必读清单/§2.3 关系矩阵同步挂接（三挂接点） | Owner 指令（情绪六段撞车事故后）：地图血肉填充每层讨论 MUST 先过 trading_decision_map_layering_sop.md 四道前置检查（已有资产盘点/四路调研/上层完整性/枝干分级），检查通过回归本 SOP 标准闭环——两 SOP 上下游衔接（讨论层闸→施工层闭环） |
| 2026-09-05 | 1.5.5 | **"全图全库对齐"简称裁定（#ARCH-ALIGN-NAMING-001）+ Step 3 七图化**：计数无关命名（五图→六图→七图三次改名腐化史）；Step 3 定义表新增图 7 trading_decision_map（TDM-node_id 轴+DECISION-MAP gate 138）；配合 alignment_checklist v1.3.0 | Owner 2026-09-05 裁定；七图对齐 exit 0 实证 |
| 2026-09-14 | 1.6.0 | **新增 Step 1.9 方案挖矿**（施工前先做方案：方案先挖矿，把矿挖干再施工）+ Checklist 第 16 项 + §2.3 关系矩阵/Step 2 前置条件/Step 0 必读清单/frontmatter depends_on 四处同步挂接；mining_sop_policy.md 加施工闭环回链 | Owner 指令：挖矿 SOP（2026-09-14 立）接进施工闭环——方案阶段先挖矿、双噪音挖干再施工，堵“无方案/拍脑袋方案直接施工”缺口 |
| 2026-09-15 | 1.7.0 | Step 1.9 挂接 mining_sop v1.1.0 新增“挖后自审闸”：操作摘要/执行要点 7/通过判据/产出物/关系矩阵/Checklist 16 六处同步——方案成稿后 MUST 过过度工程三问，三态=施工/降级/方案封矿（成例=dead/ 自动清理方案封矿 9bbc01472f） | Owner 指令“挖完自己审一遍是否过度工程，写进挖矿 SOP” |
| 2026-09-15 | 1.7.1 | Step 1.9 随 mining_sop v1.2.0 判据重铸同步四处措辞（操作摘要/执行要点 7/通过判据/Checklist 16）：量尺改“终局全貌”，三态改施工/挂起排期/方案封矿 | Owner 指正：项目进化极快（2-3 天~1 周可长成终局形态），按现状模块/数据判过度工程=系统性低估，量尺必须是终局全貌 |
| 2026-09-15 | 1.7.2 | Step 1.9 随 mining_sop v1.3.0 终止判据重铸同步六处（关系矩阵/操作摘要/执行要点 3/执行要点 6/通过判据/Checklist 16）：挖干判据改“矿脉枯竭=六向全查无+无未挖长尾”（废双噪音轮数上限，无轮数/深度/候选数上限）；执行要点 6 改“世界地图完备优先”（禁以先施工中断挖矿，自审闸统盘裁定建/合/废/挂，废候选>20 停挖转施工） | Owner 指正：挖两轮后继续挖仍出新矿脉；先挖全世界地图再统盘定建/合/废/挂，防建完挖出更优解返工 |
| 2026-10-04 | 1.7.3 | 图14 整编批真源修复：①本件嵌入 D14 步骤锚机读锚块（新增附录 D，91 提案件整编，锚块真源自本件承载）；②§2.3 矩阵补 Step 3.5 行（CV-11 清零）；③断链修复 98 处（design_memos 五件按裁定#384 归档位重指 12 处＋../rules 基址 73 处＋代码/注册表链接基址 13 处）；④背离修复 R-01/02/03/04/05/06/07/09/10/13/14（幽灵脚本换实锚/计数实测/路径正名/flag 与子命令契约更正/行号锚改符号锚/门实名 NO-SECRET-HARDCODE）；⑤计数漂移 15 步→17 段、13 项→16 项、10 phase→11、七图与 100 gate 改指针口径（A.13 随之改名全图全库对齐验证） | Owner 令"死会话工作代做"（st-tclose-integ-20261004 整合批；工单=docs/_working/fullcirc_closeout_chief/integ_workorder.md；图14 本体零改动） |

## 附录 A：长清单审查全文（用户提供的 12 节审查清单）

> 本附录是长清单审查（Step 6）的真源清单，源自用户 2026-08-12 提供。54 维度基座见 [trae_081_audit_dimensions_framework.yaml](../../rules/trae_081_audit_dimensions_framework.yaml)，本清单是其子集。
> 审查逻辑：审查本会话首条至当前全部对话，核查工作是否全部完成无遗留，大白话汇报成果（功能作用/达成目标/解决痛点/自动启动/自动运行/自动关闭）。

### A.0 执行前提
- 仅审查本会话已完成工作，禁止新建任何文件/规则/脚本/登记。发现问题按"先报告→再修复→再自检"分轮处理，禁止边审边改
- 所有路径用绝对路径；中文输出，术语中英并列；只给结果不描述过程
- 规则自包含；每条结论基于实际读取/检索/验证

### A.0.5 改动分类与跳过门（先于一切审查）
判定本会话改动属于哪类（可多选）：
- A 类·轻量改动：单文件/小改动/无新文件/无依赖变更
- B 类·新建功能/脚本：新建文件，非永久系统
- C 类·永久系统/常驻服务
- D 类·依赖变更：模块间/契约/事件/外部域
- E 类·规则/契约/登记表变更

输出"适用条款清单+跳过条款清单+跳过理由"。后续每条[适用:X类]决定执行与否；不适用一行 N/A 禁止展开。

### A.1 工作完成性核查 [全类]
- A.1.1 功能作用（一句话）
- A.1.2 达成目标（可验证完成标志）
- A.1.3 解决痛点
- A.1.4 自动启动机制 [仅 C 类]（事件触发源；禁止时间/手工触发）
- A.1.5 自动运行机制 [仅 C 类]
- A.1.6 自动关闭机制 [仅 C 类]
- A.1.7 完成度判定（已完成/部分完成/未完成+遗留项清单）

非 C 类对 A.1.4-A.1.6 声明 N/A，禁止编造。

### A.2 责任唯一与真源唯一 [全类]
- A.2.1 责任唯一：文件名即责任
- A.2.2 真源唯一：检查多真源同步（YAML↔DB↔常量↔文档）。多真源同步成本高且 AI 不可能可靠同步，能用一个的绝对不用多个，根因是减少幻觉和漂移；多真源须收敛为单真源+派生缓存，禁止双向同步。重点：是否引入第二决策点
- A.2.3 派生关系：缓存/索引是否标注真源，单向派生
- A.2.4 死代码：迁移/重构后是否遗留定义点

### A.3 向内收原则 [全类]
- A.3.1 能现成不创造：动手前是否搜索现有脚本/模块/词表/注册表？优先扩展而非复制。反查=capability registry+全文检索+语义搜索三重验证，禁止凭印象
  - 反查第四口（裁定#460 ②，2026-09-30）：图书馆总口 `python -m zephyr.library.lookup <关键词>`——资产/路径反查必过（别名轴内建；携 `--session <sid>` 留审计），与上三口并列
- A.3.2 创造必全自动 [仅 C 类]：永久系统是否满足"自动事件触发→自动运行→自动维护→自动关闭"四要素？禁止时间驱动（cron/Timer/sleep-loop/periodic/CircadianScheduler/轮询守护），禁止 manual-only，事件钩子必须在 boot_hooks 注册。例外：退避重试/锁轮询/启动等待/就绪探针不算时间触发；CI 定期 job 只能兜底
- A.3.3 第一性原理治本：是否质疑元问题（该不该存在？能否删除/合并？）？背景：100% AI 开发项目里，AI 上下文有限、依靠对话触发工作，故能删除/合并的绝不保留。重复簇是否收敛为唯一实现？
- A.3.4 创建/维护时元思考（先于第五节测试）：①刚进项目 AI 如何知道此功能并使用？②AI 涉及此工作时如何知道存在而不另行创造？是否 capability 反查+命名前缀+门禁阻断三重防御？

### A.4 文件夹容量治理 [B/C/D/E 类·仅当新增或删除文件时]
- A.4.1 增量速度否决：封顶型（完成即停止增长）→步骤 2；线性无封顶型→必须建子目录
- A.4.2 数量阈值（仅封顶型）：N=终局文件数（排除__init__.py），评估命名前缀：
  - N≤60 平铺 OK
  - 60<N≤120 且有稳定命名前缀→平铺 OK
  - 60<N≤120 且无稳定命名前缀→必须建子目录
  - N>120 必须建子目录
- A.4.3 子目录校验（若已建）：子目录内≤60 通过，>120 必须再拆；划分维度须功能相关
- A.4.4 输出：裁定/依据（命中规则+N+增长类型+命名前缀）/建议。建议须包含：若必须建子目录给出划分维度；若 60<N≤120 无前缀，提示先立命名前缀规则可豁免

A 类无文件增删时一行 N/A。

### A.5 AI 可发现性对抗测试 [全类]
- A.5.1 模拟"刚进项目无上下文 AI"对每项功能测试：
  - 可被发现性 [全类]：通过哪些入口找到？（capability registry/AGENTS.md/索引文件/命名前缀）
  - 可被使用性 [全类]：找到后能否正确使用？（接口/参数/返回值是否清晰）
  - 可被绕过性 [仅 B/C/D/E 类]：是否存在绕过路径？
  - 可被重复造轮子性 [仅 B/C/D/E 类]：是否存在 AI 误判"不存在"而重建风险？
- A.5.2 每项给出：通过/不通过 + 证据（绝对路径或反查命令）

A 类仅测前两项。

### A.6 红蓝极限对抗测试 [全类]
- A.6.1 必做维度（不可跳过）：
  - 跨层契约违反（最高危）：接口签名/退出码/调用方假设变更。执行：Grep 检索被改接口所有调用点，逐个验证调用方假设；调用方≥10 个则抽样 5 个最关键并说明抽样依据
  - 真源失效：第二决策点/死代码/多真源。执行：对比改动前后决策路径，确认收敛到唯一真源点
  - 依赖未登记 [仅 C/D 类]：模块间/契约/事件/外部域依赖是否在 depgraph 登记。执行：apply_depgraph 查询本模块节点依赖列表，对比代码实际 import/订阅/调用
- A.6.2 自由发挥维度：按任务特性选择最有价值攻击向量（输入边界/并发/状态机/缓存/容量/命名等）
- A.6.3 红队构造攻击，蓝队验证门禁/校验/真源机制是否阻断
- A.6.4 输出：每项红队攻击→蓝队防御结果→通过/不通过（表格）

### A.7 命名与路径合规 [全类]
- A.7.1 文件/文件夹全部 snake_case（豁免：docker-compose.yml/.yaml、AGENTS.md、Dockerfile、README.md、LICENSE、CONTRIBUTING.md、SECURITY.md）
- A.7.2 命名=责任：是否清晰无歧义，便于 AI 查找
- A.7.3 物理路径：平铺优先无不当嵌套；功能域平级→物理路径平级
- A.7.4 强制性：未来 AI 是否被门禁强制按规则命名，无法绕过
- A.7.5 绝对路径：代码/配置/脚本中所有路径引用绝对
- A.7.6 BOM/换行符：新建文件是否含意外 BOM；换行符是否一致（LF）

### A.8 影响同步 [全类·子项按类型触发]
- A.8.1 AGENTS.md 同步：新建/修改功能/规则/门禁是否在 AGENTS.md 有对应说明；是否仍为"新 AI 第一读"准确入口
- A.8.2 索引源与文档索引同步：变更是否同步到 capability registry/blueprint registry/architecture_issue_registry/文档索引/跨层契约文件
  - 蓝图同步判定（A.8.2 必做子项）：判定本会话是否涉及蓝图，满足任一即"涉及"：
    - 改动落在某模块 blueprint.md 范围
    - 改动影响蓝图间引用关系（迁移/重命名/契约/依赖变化）
    - 新建模块需新建蓝图，或退役模块需状态流转
  - 涉及→核查同步点（未同步列入问题清单）：
    ① 物理 blueprint.md 内容是否与代码现状一致（接口/退出码/依赖/契约是否落图）
    ② blueprint_registry.yaml 单向派生（物理→registry，禁止反向手改）
    ③ 蓝图声明依赖是否同步到 cross_module_dependency_registry.yaml（被 generate_project_depgraph.py 消费喂 depgraph）
    ④ frontmatter 状态字段流转（status/construction_progress/version/last_updated）
  - 不涉及→一行 N/A
- A.8.3 词表硬编码检测 [仅当改动涉及词表/枚举/合法值集合时]：新建代码是否硬编码词表（应动态加载 YAML）；DDL 里 CHECK 枚举属 DDL-as-Code 例外
- A.8.4 能力/架构/hash 登记同步 [仅 B/C/E 类·当新增 capability/ARCH 引用/治理脚本时]：
  - 新建功能性脚本是否登记到 capability registry（含 aliases+creation_tokens）
  - #ARCH-NNN 引用是否在 architecture_issue_registry 有对应条目
  - 完整性校验数据库是否登记新增/变更脚本的 golden hash

### A.9 版本控制 [全类]
- A.9.1 全部变更是否已 git commit
- A.9.2 提交方式优先级：worktree session_worktree_commit > GitCommitGateway > 裸 git commit（禁止）
- A.9.3 是否经过 pre-commit 门禁全量通过
- A.9.4 备份先行：改 depgraph 前是否 git commit 备份 [仅 D 类]
- A.9.5 worktree 君子协定：1 任务=1 start+多次 Edit/Write+1 commit+1 merge；held_files 重叠是否走逃生通道
- A.9.6 时间序依赖：多文件或多轮改动同一文件最终状态是否正确 [仅当多文件或多轮改动时]。注：时序违规判定依赖 A.11.1 L1 铁律
- A.9.7 并发冲突：与其他活跃会话 held_files 重叠或 worktree merge 失败遗留；治本变更未提交前是否启动并发 AI 对话（禁止）[仅当多会话场景]

### A.10 文件元数据（表头） [B/C 类·新建必审；A/D/E 类·修改时同步更新]
- A.10.1 新建代码/文件是否填写表头字段（字段列表从工程文件头规则动态读取，禁止硬编码）
- A.10.2 字段值是否正确（责任主体/创建时间/真源/派生关系/creation_tokens 等）
- A.10.3 是否存在硬编码字段列表（应从 YAML 动态读取）

A/D/E 类修改文件若原本无表头则 N/A。

### A.11 depgraph 全景图依赖登记（治本铁律 L1+L2） [仅 C/D 类·当新建永久系统或依赖变更时]
- A.11.1 L1 铁律（依赖关系先行）：每个模块施工前（写第 1 行业务代码前）是否已通过 apply_depgraph 将依赖关系登记到 depgraph 设计态（status=planned）。禁止"先施工后补登记"或"临时编造依赖"
- A.11.2 L2 铁律（设计态基于最新运营态）：写入设计态前是否确保运营态已就绪。执行：apply_depgraph --query-production 拉取当前运营态节点快照，对比本次设计态依赖是否在运营态中存在对应实体；若运营态空或过期，必须先运行 generate_project_depgraph.py 刷新再写入设计态
- A.11.3 状态流转：施工完成并通过验证后，status 是否 planned→production
- A.11.4 禁止直连+访问协议：depgraph 修改必须通过 apply_depgraph，禁止直接改数据库
- A.11.5 测试隔离：测试域是否污染生产 depgraph
- A.11.6 备份先行：改 depgraph 前是否 git commit

非 C/D 类一行 N/A。

### A.12 审查结论与零问题闭环 [全类]
- A.12.1 审查结论直接在对话里给出，禁止创建任何报告文件（MD/txt/json 等一律不创建）
- A.12.2 结论必须包含：
  - 本会话工作完成度总览（已完成/部分完成/未完成项数）
  - 本次跳过条款清单+跳过理由（来自 0.5 分类）

### A.13 全图全库对齐验证 [全类·当改动涉及模块/依赖/路径/蓝图时]

> 全图全库对齐是项目治本铁律（[trae_080](../../rules/trae_080_panorama_alignment.yaml)），施工后 MUST 经 align_all 验证图族一致（张数以 alignment_checklist.md §3 为准）。

- A.13.1 **depgraph**（依赖全景图）：改动模块的 design_maturity/build_status/domain_id 是否与代码现状一致？apply_depgraph 查询本模块节点是否 production
- A.13.2 **dataflowgraph**（数据流向全景图）：sync_panorama_module 是否已从 depgraph 单向派生？数据流 job 是否与代码实际 dataflow 一致
- A.13.3 **decisiongraph**（决策流全景图）：sync 派生的 decision_layer 是否与代码实际决策路径一致
- A.13.4 **blueprint.md**（蓝图）：物理 blueprint.md frontmatter 4 字段（module_id/responsibility_domain/design_maturity/build_status）是否与 depgraph 一致
- A.13.5 **battle_map**（作战全景图）：改动涉及 BM-XXX 环节时，battle_map_anchors 是否与前四图双向校验通过
- A.13.6 **对齐验证命令**：`python scripts/governance/d5_architecture/generators/align_all.py` exit 0
- A.13.7 **硬阻断条件**：domain_mismatches>0 / ghost_anchors>0 直接阻断施工闭环

不涉及模块/依赖/路径/蓝图改动的纯文档修改一行 N/A。

### A.14 代码质量专项 [仅 B/C 类·当改动涉及代码文件时]

> 从 [trae_081_audit_dimensions_framework.yaml](../../rules/trae_081_audit_dimensions_framework.yaml) 54 维度中选取 10 个最关键的代码质量检查点。按改动特性选用，非全量必做。

- A.14.1 **状态机正确性**（5.41）：有无转换校验？有无锁？force_state 是否绕过终态？
- A.14.2 **类型注解准确性**（5.94/5.145）：public API 有无注解？Any 滥用（>5 处/文件）？返回类型与实际不符？
- A.14.3 **函数复杂度**（5.97/5.140）：文件≤300 行/函数≤50 行/类≤200 行？圈复杂度<15？
- A.14.4 **变量遮蔽**（5.101）：参数是否遮蔽 id/字段是否遮蔽内置名/模块名是否冲突标准库？
- A.14.5 **序列化/反序列化安全**（5.147）：joblib.load 有无校验？Content-Length 有无上限？json.dumps 有无 default=str 类型丢失？
- A.14.6 **全局状态管理**（5.165）：模块级单例有无锁 double-check？import 时有无启 Timer？asyncio+全局状态冲突？
- A.14.7 **文件句柄/资源泄漏**（5.169）：fd 有无泄漏？urlopen 有无 close？sqlite3 有无 try/finally？os.open 有无泄漏？
- A.14.8 **导入循环/模块耦合**（5.174/5.138）：shared 有无退化代理壳？有无双向耦合？有无延迟导入堆叠？
- A.14.9 **时间与时区处理**（5.46）：time.time() 是否用于 TTL？naive/aware datetime 是否混用？
- A.14.10 **资源清理顺序**（5.144）：核心关闭路径有无异常隔离？sqlite 清理有无 finally？子进程管道关闭顺序对不对？

A/D/E 类不涉及代码时一行 N/A。

## 附录 B：验证脚本索引（scripts/governance/）

> 施工过程中可调用的验证类脚本清单（9 大类 90+ 脚本）。按 Step 5/6/8 验证需求选用。

| 类别 | 路径 | 用途 | SOP 步骤 |
|---|---|---|---|
| **d1_structure** | `scripts/governance/d1_structure/` | 结构验证（路径/命名/容量） | Step 6 A.7 命名与路径合规 |
| **d3_metadata** | `scripts/governance/d3_metadata/` | 元数据验证（frontmatter/文件头） | Step 6 A.10 文件元数据 |
| **d5_architecture** | `scripts/governance/d5_architecture/` | 架构验证（depgraph/五图对齐/blueprint） | Step 3/Step 8 |
| **d5_architecture/generators/align_all.py** | 同上 | 五图对齐统一入口 | Step 3/Step 8 |
| **d5_architecture/generators/generate_battle_map_diagram.py** | 同上 | 重生成 battle_map | Step 8 |
| **d6_security** | `scripts/governance/d6_security/` | 安全验证（密钥/敏感信息） | Step 6 A.6 红蓝对抗 |
| **d7_code** | `scripts/governance/d7_code/` | 代码验证（import/未定义符号/重复簇） | Step 6 A.2 真源唯一 |
| **d8_doc_sync** | `scripts/governance/d8_doc_sync/` | 文档同步验证（蓝图↔代码↔路径树） | Step 7/Step 8 三方对齐 |
| **d11_compliance** | `scripts/governance/d11_compliance/audit_registration.py` | G7 注册审计 | Step 8 |
| **d12_ai_hallucination** | `scripts/governance/d12_ai_hallucination/` | AI 幻觉检测 | Step 6 A.5 AI 可发现性 |
| **meta** | `scripts/governance/meta/` | 元治理（规则一致性/执行追踪） | Step 6 A.8 影响同步 |
| **apply_depgraph.py** | `scripts/governance/` | depgraph 写入（设计态/状态流转） | Step 2/Step 8 |
| **sync_panorama_module.py** | `scripts/governance/` | 派生其余三图 | Step 3/Step 8 |
| **extract_depgraph.py** | `scripts/governance/` | depgraph 只读查询（--summary/--paths） | Step 0 冷启动 |
| **generate_project_depgraph.py** | `scripts/governance/` | 重生成 depgraph（⚠️架构升级期禁用 --force） | Step 8 |
| **generate_project_path_tree.py** | `scripts/governance/` | 重生成 path_tree | Step 8 |
| **diagnose_depgraph.py** | `scripts/governance/` | depgraph 诊断 | Step 8 |
| **git_commit_gateway.py** | `scripts/` | 网关提交入口 | Step 10 |
| **session_worktree.py** | `scripts/` | worktree 管理（create/start/commit/merge/abort/sweep） | Step 10/Step 12 |
| **lock_files.py** | `scripts/` | 文件锁管理（cleanup/status/release） | Step 0/Step 11 |
| **git_guard.py** | `scripts/` | git 危险命令拦截+自伤防护 | Step 4/Step 9 |

## 附录 C：post-commit reconciler 清单（40+ 个）

> 真源：[src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py](../../../../src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) §`_register_default_reconcilers`（符号锚）
> 异步执行框架：[src/zephyr/governance/audit/reconcile_runner.py](../../../../src/zephyr/governance/audit/reconcile_runner.py) §`launch_reconcile_async`
> 查询进度：`.runtime/reconcile_reports/reconcile_status_<sha>.json` 或 `query_reconcile_status` 命令

| 类别 | reconciler 名称 | 用途 |
|---|---|---|
| **结构同步** | manifest / path_tree / path_ownership | 路径树/清单同步 |
| **架构同步** | depgraph_ops / blueprint_frontmatter / regenerate / arch_diagram | depgraph/蓝图/架构图同步 |
| **漂移检测** | drift_scan / drift_fix / module_id_recommend / undefined_name_baseline | 漂移扫描与修复 |
| **YAML 同步** | yaml_sync / vocab_change / deprecated_directory | YAML/词表/废弃目录同步 |
| **审计** | delete_audit / integrity_audit / rule_audit / architecture_health | 各类审计 |
| **注册表同步** | registry_sync / gate_inventory_sync / gate_registry_sync / in_process_gate_registry_drift | 注册表与门禁同步 |
| **索引** | session_log_index / index_generator | 索引生成 |
| **运行时清理** | runtime_cleanup / tmp_cleanup / worktree_lifecycle / stash_lifecycle / session_staging_lifecycle / root_temp_sweep | 运行时/临时文件/worktree/stash 清理 |
| **基线** | consumers_accuracy_baseline / capability_lookup_health / translation_coverage / cross_layer_contract_signature | 基线检测 |
| **蓝图** | blueprint_id_legacy / blueprint_status_transition / remediation_progress | 蓝图状态流转 |
| **约束检测** | constraint_detect | 约束检测 |
| **测试** | test_residue_reclaim | 测试残留清理（[trae_071](../../rules/trae_071_temporary_file_lifecycle.yaml) §test_residue_reclaim） |
| **Git 安全** | git_guard_bypass / scripts_import_integrity / git_performance_monitor / commit_gateway_abuse_monitor | Git 安全与性能 |
| **错误** | error_pattern_consumer | 错误模式消费 |
| **工作区** | workspace_hygiene / dead_public_wrapper | 工作区卫生 |
| **文档** | readme_version_sync / requirements_version_sync | README/requirements 版本同步 |
| **指标** | metric_count_drift / runtime_violation_snapshot | 指标漂移与运行时违规快照 |
| **备份** | backup | 备份 |

**执行顺序**：按 priority 排序（数字越小越先执行），异常隔离（一个 reconciler 崩溃不影响其他）。

---

## 附录 D：图14 步骤锚机读锚块（D14-STEP-ANCHORS·真源承载）

> 本节为图14（AI 施工升级流图）步骤锚的**唯一真源承载位**（2026-10-04 由 91 号提案件
> docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml 逐字节整编入位，
> 政策散文语义零改动；定界标记两键为提案件自描述元数据，嵌入态省略——本节的定界标记行即其承载）。
> 消费方=scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py
> load_anchor_block（政策内嵌块优先，本节缺席才回落提案件；两源 payload 同构已验）。
> 纪律：本节为机读面，人工修订只改下方 yaml 并同批回生成图（锚块→图单向派生，禁手改图后不回生成）；
> verifiability 值集动态取受控词表，禁写死。

# <<<CONSTRUCTION_STEP_ANCHORS>>>
```yaml
schema_version: '0.1'
block_id: CONSTRUCTION_STEP_ANCHORS
host_policy: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
skeleton_source: docs/_working/map_build/fig14_construction/00_skeleton.md
anchor_source_note_zh: verifiability 值集动态取 _registry/vocabularies/verifiability_vocabulary.yaml （automated/inspection/manual），禁在本件或校验器里写死字典；
  exec_source 形态=gate:<GATE_ID> | script:<相对路径> | cli:<相对路径>#<选项名（去前导 连字符）> | null； anchor_kind 值集=gate_id|script|cli|doc|handoff|none（doc/handoff/none
  三值表示本段没有 可执行真相源，只能靠文档锚或他图机制）；null 只允许出现在 role=handoff 或 verifiability=manual 的段上，否则校验器判红。
step_anchors:
- step_id: D14-01
  policy_step: Step 0
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-0-session-冷启动前置必做
  name_zh: Session 冷启动
  segment: 前置
  role: handoff
  handoff_to:
  - D11-S01
  - D11-S02
  - D11-S09
  order: 1
  conditional: false
  verifiability: manual
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: handoff
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md
    symbol: 全景图
  decision_question: 会话是否已就绪到"可以开始施工"？就绪结论落在哪个面？
  note_zh: 就绪判据实体在图11 D11-S01（门控引擎+会话注册表），本段只作交接；政策点名的守护件为幽灵（D14-G01），实测可跑入口未被政策指认（D14-G02）
  fallback: 就绪判据不可用时按宪法冷启动序列逐项人工核，不阻塞进 D14-02
  invalidation: 图11 D11-S01 环节改号或门控入口换件 ⇒ 本段 handoff 引用作废
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-01 行实扫：phase_manager 内 gate_* 唯一名 58（政策称 46）；session_startup_check.py --json 实跑 overall=GREEN
  - 2026-09-25 本车道只读复跑：ls scripts/ide_health_service.py → No such file（D14-G01 成立）
  red_findings:
  - R-01
  - R-02
  - WJ-R-01
  - WJ-R-13
  - WJ-R-14
  red_reason: terminal
  wiring_status: partial
- step_id: D14-02
  policy_step: Step 1
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-1-文档审查
  name_zh: 文档审查
  segment: 前置
  role: internal
  handoff_to: []
  order: 2
  conditional: false
  verifiability: manual
  skeleton_verifiability: false
  build_status: pending
  anchor_kind: doc
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/_archive/AI_review_instructions.md
    symbol: 审查
  decision_question: 待施工文档现在可施工吗？GAP 清单产在哪、由谁签收？
  note_zh: 审查清单宿主实为政策附录 A（与 D14-11 同物，簿01 WJ-R-03）；被指认的真源件已 deprecated，审查结论政策明禁留痕 ⇒ 结构性无机验面
  fallback: 无留痕面时以对话内 GAP 清单为准，图不代主张
  invalidation: 若裁定允许 .runtime 会话内留痕，本段可升 inspection；现按 manual 记
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-02 行 + 簿01 §2：AI_review_instructions.md 在盘但 status=deprecated；全仓无 12 节结构
  - 2026-09-25 本车道只读复跑：docs/_archive/AI_review_instructions.md 存在（deprecated 真源，故本段 anchor_kind=doc 而非 exec）
  red_findings:
  - R-10
  - WJ-R-03
  - WJ-R-06
  red_reason: broken_supply
  wiring_status: unwired_no_caller
- step_id: D14-03
  policy_step: Step 1.5
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-15-创建前搜索仅新建模块触发
  name_zh: 创建前搜索
  segment: 前置
  role: internal
  handoff_to: []
  order: 3
  conditional: true
  trigger_when: 仅新建模块/蓝图/代码文件/门禁时触发
  verifiability: inspection
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: gate_id
  exec_source: gate:CAPABILITY-LOOKUP-REQUIRED
  gates:
  - CAPABILITY-LOOKUP-REQUIRED
  executable:
  - src/zephyr/governance/capability_lookup.py
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml
    symbol: search_first
  - path: docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml
    symbol: phase_1_search
  decision_question: 拟新建的东西是否已有现成件？反查发生过与复用决策分别留在哪？
  note_zh: 反查留痕面实测存在（lookup_audit jsonl + 执法台在册）；复用决策标注政策只说"对话内"⇒ 无结构落点
  fallback: 逃生通道=提交标记 no-lookup 白名单理由（真源=能力反查规则册，本图不重述）
  invalidation: 反查审计面停写 ⇒ 本段 automated 主张作废（降 manual）
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 簿01 §3：capability_lookup.py 审计写入函数在位；主区 .runtime/lookup_audit/ 实测 363 件
  - 2026-09-25 本车道只读复跑：CAPABILITY-LOOKUP-REQUIRED 在两册各 1 条在册
  module_ref: src/zephyr/governance/capability_lookup.py
  exec_evidence:
  - 2026-09-25 只读复跑 grep -n 'def write_lookup_audit_log' src/zephyr/governance/capability_lookup.py 命中
  - 2026-09-25 只读复跑：CAPABILITY-LOOKUP-REQUIRED 两册各 1 条在册
  store_refs:
  - artifact: 能力反查审计流水
    location: .runtime/lookup_audit/<sid>.jsonl
    key: session_id
    retention: 按运行时回收策略
  runtime_refs:
  - .runtime/lookup_audit/
  red_findings:
  - R-09
  red_reason: null
  wiring_status: partial
- step_id: D14-04
  policy_step: Step 1.8
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-18-架构评审门控判定-4-种变更触发
  name_zh: 架构评审门控判定
  segment: 判定
  role: internal
  handoff_to: []
  order: 4
  conditional: true
  trigger_when: 变更类型命中架构评审触发清单时
  verifiability: manual
  skeleton_verifiability: false
  build_status: pending
  anchor_kind: doc
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml
    symbol: gov_arch_002
  - path: docs/01_policies_and_standards/rules/trae_049_ops_domain_manual.yaml
    symbol: OPS-DEV-002
  - path: docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml
    symbol: ''
  decision_question: 本次变更要不要动架构？要动的门位由谁签、记录落哪？
  note_zh: 人门位=Owner（执行或书面委托），设计上不可自动化；政策指认的评审记录目录不在盘，实际落点在归档侧且仅 2 条
  fallback: 门位不可用时按高危域人工门位停等，不自动放行
  invalidation: 评审记录唯一落点由总包裁定后，本段 anchor 须改写；裁定前不得升 inspection
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §6 L-1 + 簿01 §4：docs/_working/audit/architecture-reviews/ 不存在；archive 侧实测 2 条记录
  - 2026-09-25 本车道只读复跑：三份规则锚件俱在盘（gov_arch_002 / OPS-DEV-002 符号命中）
  red_findings:
  - R-11
  - WJ-R-04
  red_reason: broken_supply
  wiring_status: unwired_no_caller
- step_id: D14-05
  policy_step: Step 1.9
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-19-方案挖矿施工前先做方案方案先挖矿把矿挖干再施工
  name_zh: 方案挖矿
  segment: 判定
  role: internal
  handoff_to: []
  order: 5
  conditional: true
  trigger_when: 内容产出类任务（方案/策略/设计文档）
  verifiability: manual
  skeleton_verifiability: false
  build_status: pending
  anchor_kind: doc
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md
    symbol: 挖矿
  - path: docs/01_policies_and_standards/sop/mining_sop/skeleton_mining_policy.md
    symbol: 骨架
  decision_question: 方案挖干了吗？挖矿日志进了章节、自审三态留了痕吗？
  note_zh: 三条子判据全仓零 checker（挖矿增补在 .py 命中 0，两册 gate 零条目）⇒ 执法率 0 是设计后果；可 auto 化的上限只是 MD 结构断言
  fallback: 无 checker 期间由施工会话在方案 MD 内自审留痕，图不代证
  invalidation: 结构 checker 落地（建议挂 d9_knowledge 目录，零新目录）后本段可升 inspection
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §7-C6 + 簿01 §5：grep -rl 挖矿增补 --include=*.py src scripts → 0 命中
  - 2026-09-25 本车道只读复跑：mining_sop_policy.md / skeleton_mining_policy.md 两真源在盘
  red_findings:
  - R-12
  red_reason: unwired
  wiring_status: unwired_no_caller
- step_id: D14-06
  policy_step: Step 2
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-2-全景图登记设计态先行
  name_zh: 全景图登记（设计态先行）
  segment: 设计登记
  role: internal
  handoff_to: []
  order: 6
  conditional: false
  verifiability: automated
  skeleton_verifiability: true
  build_status: built
  anchor_kind: cli
  exec_source: cli:scripts/governance/apply_depgraph.py#add-design-node
  gates:
  - DEPGRAPH-ENFORCEMENT
  - DEPGRAPH-PRE-REGISTRATION
  - NEW-FILE-DEPGRAPH-ENFORCEMENT
  executable:
  - scripts/governance/apply_depgraph.py
  cli_anchors:
  - script: scripts/governance/apply_depgraph.py
    option: --add-design-node
  - script: scripts/governance/apply_depgraph.py
    option: --add-design-edge
  docs:
  - path: docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml
    symbol: panorama_alignment
  - path: docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml
    symbol: depgraph_access_protocol
  decision_question: 施工前设计态节点登记上了吗？运营态就绪与否有可读的回读面吗？
  note_zh: 登记面（两选项 + 三台在册 gate）机验成立；L2 铁律的"先查运营态"无执行面（D14-G05）、准入记录面无宿主（D14-G06）
  fallback: 设计态不可读时由施工会话人工核 depgraph，不替代登记动作
  invalidation: depgraph 存储面（PG）不可达 ⇒ 本段"已登记"断言不可证，降 inspection
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-06 行 + 簿01 §6：apply_depgraph.py 选项集实测含 --add-design-node/--add-design-edge；三台 gate 在册
  - 2026-09-25 本车道只读复跑：grep -oE 选项集 apply_depgraph.py 无含 query 的选项（D14-G05 成立）
  module_ref: scripts/governance/apply_depgraph.py
  exec_evidence:
  - 复跑 grep -oE add-design 选项集 scripts/governance/apply_depgraph.py 命中 --add-design-node/--add-design-edge
  - 2026-09-25 只读复跑：DEPGRAPH-ENFORCEMENT/DEPGRAPH-PRE-REGISTRATION/NEW-FILE-DEPGRAPH-ENFORCEMENT 在册
  store_refs:
  - artifact: depgraph 设计态节点
    location: PostgreSQL depgraph.nodes
    key: module_id
    retention: 在册期间存续
  red_findings:
  - R-04
  - R-05
  - R-11
  - WJ-R-08
  - WJ-R-11
  red_reason: null
  wiring_status: partial
- step_id: D14-07
  policy_step: Step 3
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-3-全图全库对齐七图自动align_all-单命令简称裁定-arch-align-naming-001
  name_zh: 全图全库对齐
  segment: 设计登记
  role: internal
  handoff_to: []
  order: 7
  conditional: false
  verifiability: automated
  skeleton_verifiability: true
  build_status: built
  anchor_kind: gate_id
  exec_source: gate:MAP-ALIGNMENT
  gates:
  - MAP-ALIGNMENT
  executable:
  - scripts/governance/d5_architecture/generators/align_all.py
  - scripts/governance/sync_panorama_module.py
  cli_anchors:
  - script: scripts/governance/sync_panorama_module.py
    option: --all
  docs:
  - path: docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md
    symbol: 全景图
  - path: docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml
    symbol: panorama_alignment
  decision_question: 全景图与库对上了吗？对齐不通过是谁拦、拦在哪一层？
  note_zh: 三证齐（单入口聚合器可跑 + sync 派生 + 聚合台在册触发式）；张数读 alignment_checklist，政策"七图定义"表为过期散文，本图不引
  fallback: 对齐工具不可用时禁止进施工段（先登记后施工）
  invalidation: 聚合台 subs 增删或单入口聚合器节数变化 ⇒ 本段 evidence 作废需重扫
  rollback_to:
  - D14-06
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §7-C4 + 簿01 §7：align_all.py 九节实测、sync_panorama_module.py --all 在册、MAP-ALIGNMENT 聚合 6 子台
  - 2026-09-25 本车道只读复跑：MAP-ALIGNMENT 在册；两执行体含 argparse/def main
  module_ref: scripts/governance/d5_architecture/generators/align_all.py
  exec_evidence:
  - 复跑 ls scripts/governance/d5_architecture/generators/align_all.py scripts/governance/sync_panorama_module.py 两件在盘
  - 2026-09-25 只读复跑：MAP-ALIGNMENT 在 in_process_gate_registry 条目集合内
  red_findings:
  - R-12
  - WJ-R-09
  - WJ-R-10
  red_reason: null
  wiring_status: wired
- step_id: D14-08
  policy_step: Step 3.5
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-35-后端盘点与拆件判定前端施工前置
  name_zh: 后端盘点与拆件判定
  segment: 设计登记
  role: internal
  handoff_to: []
  order: 8
  conditional: true
  trigger_when: 前端页面新建/改造/加数据区块时触发
  verifiability: inspection
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: gate_id
  exec_source: gate:FRONTEND-TRUTH-SOURCE
  gates:
  - FRONTEND-TRUTH-SOURCE
  - FRONTEND-MAP
  executable:
  - scripts/governance/d5_architecture/generators/check_frontend_map.py
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_086_frontend_module_construction.yaml
    symbol: truth_source_wiring
  - path: docs/01_policies_and_standards/sop/construction_sop/frontend_component_split_policy.md
    symbol: 拆件
  decision_question: 前端这块的数据真源在哪、有没有可拆的既有件？判定结论落在哪个可查面？
  note_zh: 台子在册但阻断位关闭（源码常量 _HARD_BLOCK=False）⇒ 有台不等于有门禁，本段 verifiability 记 inspection 不记 automated
  fallback: 盘留痕无结构落点时以 gate_audit jsonl 作次级证据面
  invalidation: 阻断位翻硬（Owner 门位）后本段可升 automated；两真源件收敛唯一前不得升
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-08 行 + 簿01 §8：FRONTEND-TRUTH-SOURCE 在册且 _HARD_BLOCK=False；ACC-*.yaml 实测 69 张无读方
  - 2026-09-25 本车道只读复跑：frontend_map.yaml 政策路径 web/ 不存在，真身两份并存在册（双真源嫌疑 D14-G09）
  module_ref: scripts/governance/d5_architecture/generators/check_frontend_map.py
  exec_evidence:
  - 复跑 grep -n '_HARD_BLOCK' src/zephyr/gov_enforcement/commit_gates/frontend_truth_source_gate.py 命中（阻断位关闭）
  - 2026-09-25 只读复跑：FRONTEND-TRUTH-SOURCE / FRONTEND-MAP 两台在册
  runtime_refs:
  - .runtime/gate_audit/frontend_truth_source.jsonl
  red_findings:
  - R-11
  - WJ-R-02
  - WJ-R-05
  red_reason: null
  wiring_status: unwired_slot_hollow
- step_id: D14-09
  policy_step: Step 4
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-4-施工编码
  name_zh: 施工编码
  segment: 施工
  role: internal
  handoff_to: []
  order: 9
  conditional: false
  verifiability: automated
  skeleton_verifiability: true
  build_status: built
  anchor_kind: gate_id
  exec_source: gate:CREATE-GUARD
  gates:
  - BLUEPRINT-FORMAT
  - BLUEPRINT-HEADER
  - GIT-CALL-BUDGET
  - FOLDER-CAPACITY-HARD-LIMIT
  - COMPLEXITY-GUARD
  - CREATE-GUARD
  executable:
  - scripts/git_guard.py
  - scripts/scaffold.py
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml
    symbol: A_full
  - path: docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml
    symbol: phase_4_blueprint
  - path: docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml
    symbol: mod_001
  sub_workflow: docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml#phase_4_blueprint
  decision_question: 落码动作本身合规吗（文件头/容量/git 预算/复杂度/新建前置）？哪些判据其实没台子拦？
  note_zh: 六台在册且新建路径执法；启动方式事件驱动与存量修改的字段齐全两条判据零执法面；容量口径分三对象不可压一列
  fallback: gate 不可用时由 pre-commit 通道兜底，兜底面归属交付流水线（本图不重述）
  invalidation: 六台中任一台退役或执法面转读硬编码 ⇒ 本段 automated 主张作废
  rollback_to:
  - D14-02
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-09 行 + 簿02 §1：六台 gate 双册对账在册；git_guard.py 危险子命令清单在 :90；create_guard 动态读字段集 :757
  - 2026-09-25 本车道只读复跑：BLUEPRINT-FORMAT/BLUEPRINT-HEADER/GIT-CALL-BUDGET/FOLDER-CAPACITY-HARD-LIMIT/COMPLEXITY-GUARD/CREATE-GUARD
    全命中 gate_id 集合
  module_ref: src/zephyr/gov_enforcement/commit_gates/create_guard.py
  exec_evidence:
  - 复跑 grep -n 'a_full' src/zephyr/gov_enforcement/commit_gates/create_guard.py 命中（字段集动态读规则）
  - 2026-09-25 只读复跑：六台 gate_id 全命中两册集合（BLUEPRINT-FORMAT/BLUEPRINT-HEADER/GIT-CALL-BUDGET/FOLDER-CAPACITY-HARD-LIMIT/COMPLEXITY-GUARD/CREATE-GUARD）
  red_findings:
  - R-11
  - R-13
  - WJ-R-12
  - WJ-R-15
  - WJ-R-16
  - WJ-R-17
  red_reason: null
  wiring_status: partial
- step_id: D14-10
  policy_step: Step 5
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-5-单元测试--循环验收
  name_zh: 单元测试与循环验收
  segment: 验收
  role: internal
  handoff_to: []
  order: 10
  conditional: false
  verifiability: inspection
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: gate_id
  exec_source: gate:TEST-RESIDUE-SSOT
  gates:
  - TEST-SOURCE-CONSISTENCY
  - TEST-RESIDUE-SSOT
  executable:
  - src/zephyr/governance/persistence/task_repo.py
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml
    symbol: test_residue_reclaim
  - path: docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml
    symbol: task_card
  decision_question: 连续两轮零错误这条验收判据由谁强制？没任务卡的施工谁来强制？
  note_zh: 循环验收是真执行（代码常量+子进程），但只在任务卡转终态且验收命令集非空时触发；无卡施工形态下永不相触
  fallback: 无卡施工现无等价面（簿02 X-16 待裁），本段按 inspection 记不放宽
  invalidation: 常量改名或触发条件变化 ⇒ max_rounds_ref 符号锚作废，本段连带判红
  rollback_to:
  - D14-10
  max_rounds_ref: zephyr.governance.persistence.task_repo#CIRCULAR_ACCEPTANCE_ROUNDS
  evidence:
  - 2026-09-24 骨架 §1 D14-10 行 + 簿02 §2：task_repo.py 常量与循环函数四锚链条实测在位
  - 2026-09-25 本车道只读复跑：TEST-SOURCE-CONSISTENCY / TEST-RESIDUE-SSOT 两册在册；词表模块 zephyr.shared.vocab 不存在（D14-G10）
  - 2026-10-02 终局复跑：词表模块已于 2026-09-26 复活落仓（a2e820034bd 词表读取层落仓，market_state+EXTREME_STATE_ALIASES 实测在盘），D14-G10 幽灵断言失效按其 invalidation
    条款作废（R-08 闭合）
  module_ref: src/zephyr/governance/persistence/task_repo.py
  exec_evidence:
  - 复跑 grep -n 'CIRCULAR_ACCEPTANCE_ROUNDS' src/zephyr/governance/persistence/task_repo.py 命中常量与循环函数
  - 2026-09-25 只读复跑：TEST-SOURCE-CONSISTENCY / TEST-RESIDUE-SSOT 在册
  red_findings:
  - R-08
  - WJ-R-19
  red_reason: null
  wiring_status: partial
- step_id: D14-11
  policy_step: Step 6
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-6-长清单审查12-节全维度对抗审查
  name_zh: 长清单审查
  segment: 验收
  role: internal
  handoff_to: []
  order: 11
  conditional: false
  verifiability: manual
  skeleton_verifiability: false
  build_status: pending
  anchor_kind: doc
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml
    symbol: dimensions
  - path: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md
    symbol: 附录 A
  decision_question: 逐节对抗审查的结论留在哪？遗留项登记目的地还在吗？
  note_zh: 政策明文禁创建审查报告文件 ⇒ 主判据结构性不可机验（与门④互斥，待裁定）；基座维度册在盘，漂移六件套在盘但未接入判据
  fallback: 结论留在对话内（政策口径），图不代证；遗留项登记目的地已随上游真源归档（D14-G12）
  invalidation: 若裁定允许会话内留痕，本段可升 inspection；禁以删政策句的方式变绿
  rollback_to:
  - D14-09
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-11 行 + 簿02 §3：附录 A 实测 16 个 A.* 小节（政策称 12 节/修订记 14 节并存）；漂移套件六件在盘
  - 2026-09-25 本车道只读复跑：trae_081 维度册在盘
  red_findings:
  - R-11
  - WJ-R-09
  red_reason: unwired
  wiring_status: unwired_no_caller
- step_id: D14-12
  policy_step: Step 7
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-7-更新施工文档
  name_zh: 更新施工文档
  segment: 文档转正
  role: internal
  handoff_to: []
  order: 12
  conditional: false
  verifiability: inspection
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: script
  exec_source: script:scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py
  gates:
  - TTL-METADATA
  - FILE-PLACEMENT-TTL
  executable:
  - scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py
  - scripts/governance/d8_doc_sync/update_progress.py
  - scripts/governance/d8_doc_sync/auto_sync_all_registries.py
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml
    symbol: rule_eleven
  - path: docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml
    symbol: GOV-DOC-011
  - path: docs/01_policies_and_standards/rules/trae_037_arch_qualification_versioning.yaml
    symbol: GOV-ARCH-003
  decision_question: 文档与代码对齐了吗？要同步的那两处目标件还在原位置吗？
  note_zh: 元数据/放置子判据有台有脚本；"三处对齐 + 索引同步"的两个目标件已整体归档 ⇒ 判据结构上不可满足（不是没人做，是目的地没了）
  fallback: 目标件缺位时以文档生命周期脚本的 exit 码作子判据，不代证整体对齐
  invalidation: 设计备忘体系存续性被裁定为终止 ⇒ 本段判据须改写（属改政策，本车道不主张）
  rollback_to:
  - D14-09
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-12 行 + 簿02 §4：d8_doc_sync 三件实测在盘；两目标件在 archive 不在原目录
  - 2026-09-25 本车道只读复跑：TTL-METADATA / FILE-PLACEMENT-TTL 在册；三件规则锚符号命中
  module_ref: scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py
  exec_evidence:
  - 复跑 ls scripts/governance/d8_doc_sync/ 三件俱在（生命周期校验/进度更新/册同步）
  - 2026-09-25 只读复跑：TTL-METADATA / FILE-PLACEMENT-TTL 在册
  red_findings:
  - R-11
  red_reason: null
  wiring_status: partial
- step_id: D14-13
  policy_step: Step 8
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-8-全景图状态流转designproduction
  name_zh: 全景图状态流转
  segment: 文档转正
  role: internal
  handoff_to: []
  order: 13
  conditional: false
  verifiability: automated
  skeleton_verifiability: true
  build_status: built
  anchor_kind: cli
  exec_source: cli:scripts/governance/apply_depgraph.py#transition-design-maturity
  gates:
  - DEPGRAPH-FRESHNESS
  executable:
  - scripts/governance/apply_depgraph.py
  - scripts/governance/d5_architecture/diagnose_depgraph.py
  - scripts/governance/generate_project_path_tree.py
  cli_anchors:
  - script: scripts/governance/apply_depgraph.py
    option: --transition-design-maturity
  - script: scripts/governance/apply_depgraph.py
    option: --transition-build-status
  docs:
  - path: docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml
    symbol: planned
  - path: docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml
    symbol: phase_9
  decision_question: 设计态到运营态的双态流转真的发生了吗？谁来证明核验过？
  note_zh: 两流转选项 + 六态词表由 DB CHECK 强制 + 同身份转换通道在代码；worktree 分流后的人工核验零留痕面
  fallback: 诊断件路径与政策所指不一致时以在册真身为准（D14-G04）
  invalidation: PG 不可达 ⇒ 双态读不到，本段 automated 主张降 inspection
  rollback_to:
  - D14-12
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-13 行 + 簿02 §5：两选项实测在册、DB CHECK 六态、生成器通道注释在 :396-428
  - 2026-09-25 本车道只读复跑：DEPGRAPH-FRESHNESS 在册；diagnose_depgraph 真身在 d5_architecture 下
  module_ref: scripts/governance/d5_architecture/diagnose_depgraph.py
  exec_evidence:
  - 复跑 grep -oE transition 选项集 scripts/governance/apply_depgraph.py 命中 --transition-design-maturity/--transition-build-status
  - 2026-09-25 只读复跑：DEPGRAPH-FRESHNESS 在册；诊断件真身在 d5_architecture 目录（政策路径见 D14-G04）
  store_refs:
  - artifact: depgraph 双态字段
    location: PostgreSQL depgraph.nodes
    key: module_id
    retention: design_maturity 与 build_status 两列
  red_findings:
  - R-03
  - WJ-R-18
  red_reason: null
  wiring_status: wired
- step_id: D14-14
  policy_step: Step 9
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-9-文件完整性检查
  name_zh: 文件完整性检查
  segment: 落地收尾
  role: handoff
  handoff_to:
  - D11-C11
  - D11-S07
  - D11-S04
  order: 14
  conditional: false
  verifiability: manual
  skeleton_verifiability: false
  build_status: partial
  anchor_kind: handoff
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/policies/workspace_governance_policy.md
    symbol: 临时
  decision_question: 提交前工作区是否自证完整？丢失件从哪恢复？
  note_zh: 三条判据里两条实体在图11（对账/pre-merge/claim 快照）；本域只剩"本任务改动清单与 staged 差集为空"，且无阈值判据；政策所指 CLI 子命令不存在（D14-G07）
  fallback: 无阈值判据时按交付流水线侧的完整性守卫处置（引用不重述）
  invalidation: 图11 侧对账环节改号 ⇒ 本段 handoff 引用作废
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 簿03 §1 实弹：lock_files.py status 可跑（输出 CLEAN）；session_worktree.py status 报 invalid choice
  - 2026-09-25 本车道只读复跑：scripts/rollback.py 在盘（政策所列子命令为在册件，本段不登记为机制锚）
  red_findings:
  - R-06
  - R-11
  red_reason: terminal
  wiring_status: partial
- step_id: D14-15
  policy_step: Step 10
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-10-gitcommitgateway-落地
  name_zh: 提交网关落地
  segment: 落地收尾
  role: handoff
  handoff_to:
  - D11-C01
  - D11-C03
  - D11-C04
  - D11-C05
  - D11-C07
  - D11-C08
  - D11-C09
  - D11-C10
  - D11-C11
  - D11-C12
  - D11-C13
  order: 15
  conditional: false
  verifiability: manual
  skeleton_verifiability: true
  build_status: built
  anchor_kind: handoff
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_075_stash_lifecycle.yaml
    symbol: stash
  decision_question: 本施工任务的改动在哪一步把控制权交给交付正门？交接前必须满足什么？
  note_zh: 机制真源全归图11（政策自标"不重复，引用"）；module_ref 仅为交接正门指针，本段不得重述锁/队列/落地/对账，也不借图11 的 auto 抬本段分数
  fallback: 正门不可用时按交付侧退道入队语义处置（引用不重述）
  invalidation: 图11 C 车道环节改号 ⇒ 本段 handoff_to 作废；本段 verifiability 恒 manual
  rollback_to:
  - D14-11
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-15 行 + 簿03 §2：政策所指正门脚本不存在（D14-G03）；gate 实名两条漂移
  - 2026-09-25 本车道只读复跑：scripts/git_commit.py 在盘（交接正门指针）；11 个 D11-C* 引用全部命中图11 骨架 §1
  module_ref: scripts/git_commit.py
  exec_evidence:
  - 复跑 ls scripts/git_commit.py 在盘（交接正门指针；政策所指 gateway 件不存在=D14-G03）
  - 2026-09-25 只读复跑：handoff_to 的 11 个 D11-C* 全部命中图11 骨架 §1 环节集合
  red_findings:
  - R-03
  - R-06
  - R-12
  - R-14
  - WJ-R-21
  - WJ-R-22
  - WJ-R-24
  red_reason: terminal
  wiring_status: wired
- step_id: D14-16
  policy_step: Step 11
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-11-临时文件清理只清自己不动他人
  name_zh: 临时文件清理
  segment: 落地收尾
  role: handoff
  handoff_to:
  - D11-S05
  - D11-S08
  - D11-C11
  order: 16
  conditional: false
  verifiability: manual
  skeleton_verifiability: partial
  build_status: partial
  anchor_kind: handoff
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_070_temporary_file_placement.yaml
    symbol: DCR-008
  decision_question: 提交之后暂存与锁归谁清？"我清完了"有没有凭据？
  note_zh: 清理由事件触发的对账件承担（在册，机制归图11）；政策两条命令一条元数不符、一条全仓零实现（D14-G07/G08）；产出物"清理报告"无落点
  fallback: 凭据缺位时按交付侧回收语义处置，本图只保顺序
  invalidation: 簿03 §5 判本段"真切不开"，若总包裁定与 D14-17 合并则本节点作废（X-20）
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-16 行 + 簿03 §3：staging 生命周期对账件在位、priority=802 口径与政策一致
  - 2026-09-25 本车道只读复跑：lock_files.py 命令集含 release/release-all（政策命令形态需 3 参，D14-G08 成立）
  red_findings:
  - R-06
  - R-07
  - R-14
  red_reason: terminal
  wiring_status: partial
- step_id: D14-17
  policy_step: Step 12
  policy_anchor: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-12-worktree-合并与清理有风险暂不清理
  name_zh: worktree 合并与清理
  segment: 落地收尾
  role: handoff
  handoff_to:
  - D11-S07
  - D11-S08
  - D11-S03
  order: 17
  conditional: false
  verifiability: manual
  skeleton_verifiability: true
  build_status: built
  anchor_kind: handoff
  exec_source: null
  gates: []
  executable: []
  cli_anchors: []
  docs:
  - path: docs/01_policies_and_standards/rules/trae_078_force_merge_safety.yaml
    symbol: force_merge
  - path: docs/01_policies_and_standards/rules/trae_076_worktree_commit_persistence.yaml
    symbol: commit_persist
  - path: docs/01_policies_and_standards/rules/trae_074_worktree_base_freshness.yaml
    symbol: base_fresh
  decision_question: 施工任务到本域终态了吗？合并失败时逃生通道在哪？
  note_zh: merge/abort/sweep 机制归图11；本段独有语义只剩"合并冲突暂不清理=终止分支"（非回边）；政策所指 cleanup 子命令不存在（D14-G07）
  fallback: 合并冲突时保留现场，不清理、不 abort（终止分支）
  invalidation: 图11 S07/S08 环节改号 ⇒ handoff 引用作废
  rollback_to: []
  max_rounds_ref: null
  evidence:
  - 2026-09-24 骨架 §1 D14-17 行 + 簿03 §4：CLI 实测子命令 create/exec/merge/abort/list；两符号锚实测命中
  - 2026-09-25 本车道只读复跑：scripts/session_worktree.py 在盘（交接正门指针）；三份规则件在册在盘
  module_ref: scripts/session_worktree.py
  exec_evidence:
  - 复跑 grep -n add_parser scripts/session_worktree.py 命中 create/exec/merge/abort/list 五项
  - 2026-09-25 只读复跑：handoff_to 的 D11-S07/S08/S03 全部命中图11 骨架 §1 环节集合
  red_findings:
  - R-03
  - R-06
  - R-11
  - R-13
  - WJ-R-23
  - WJ-R-25
  red_reason: terminal
  wiring_status: wired
gap_anchors:
- gap_id: D14-G01
  host_step: D14-01
  finding: R-01
  name_zh: 政策指认的守护件不存在（幽灵脚本）
  decision_question: 政策写死的启动件到底存不存在？不存在时施工准入靠什么判？
  note_zh: 政策两行命令的执行体全仓零命中；实测可跑入口是另一件且未被政策指认（本图不把它当政策锚用）
  red_reason: ghost_ref
  ghost_refs:
  - scripts/ide_health_service.py
  evidence:
  - 2026-09-24 骨架 §7-C3：find -iname "*ide_health*" 零文件
  - 2026-09-25 本车道只读复跑：ls scripts/ide_health_service.py → No such file
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-01
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §1
- gap_id: D14-G02
  host_step: D14-01
  finding: WJ-R-14
  name_zh: 幽灵脚本已进注册表（引用面）
  decision_question: 一件不存在的脚本被多少在册条目引用？退役要不要走净删门位？
  note_zh: 引用面实测覆盖规则册/宪章归档/模块蓝图/注册表等多族；其中**在册可证部分**=catalogs 册内命中（机扫计数进 machine_facts），退役须走注册表净删高危门位
  red_reason: ghost_ref
  ghost_refs:
  - scripts/ide_health_service.py
  evidence:
  - 2026-09-24 簿01 §9 WJ-R-14：引用文件实测 39 个（骨架原判 5 份文档，面积低估）
  - 2026-09-25 本车道只读复跑：machine_facts 由生成器按声明口径重扫（排除案卷与归档目录）
  doc_refs:
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §9 WJ-R-14
- gap_id: D14-G03
  host_step: D14-15
  finding: R-03
  name_zh: 政策所指正门脚本不存在
  decision_question: 政策给的提交正门件跑不起来时，交付动作的真门是哪一件？
  note_zh: 与 D14-G04 同族（路径失效类）；真门在交付流水线侧（引用不重述），本图只在 gap 节点钉"政策所指件不存在"这一事实
  red_reason: ghost_ref
  ghost_refs:
  - scripts/git_commit_gateway.py
  evidence:
  - 2026-09-24 骨架 R-03 + 簿03 §2 实弹：ls scripts/git_commit_gateway.py → No such file，真门 scripts/git_commit.py 在盘
  - 2026-09-25 本车道只读复跑：同上结论一致
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-03
  - docs/_working/map_build/fig14_construction/03_验收与收尾段.md §2
- gap_id: D14-G04
  host_step: D14-13
  finding: R-03
  name_zh: 政策所指诊断件路径失效
  decision_question: 诊断入口按政策路径找得到吗？找不到时谁是唯一真身？
  note_zh: 政策两处 + frontmatter 一处均指旧路径；真身在 d5_architecture 子目录下（find 唯一命中），图节点锚取真身、政策纠偏由总包落
  red_reason: ghost_ref
  ghost_refs:
  - scripts/governance/diagnose_depgraph.py
  evidence:
  - 2026-09-24 骨架 R-03 + 簿02 §5：find 唯一命中 scripts/governance/d5_architecture/diagnose_depgraph.py
  - 2026-09-25 本车道只读复跑：政策路径件不存在、真身件在盘
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-03
  - docs/_working/map_build/fig14_construction/02_施工与门禁段.md §5
- gap_id: D14-G05
  host_step: D14-06
  finding: R-04
  name_zh: 设计态先行铁律无执行面（选项不存在）
  decision_question: 写入设计态前确保运营态已就绪这条铁律由哪条命令保证？
  note_zh: 政策两处声明的选项实测不存在（argparse 直接拒绝）⇒ 该铁律无可执行工具面；补法应复用既有只读通道而非新造选项（净零）
  red_reason: broken_supply
  ghost_refs: []
  ghost_options:
  - script: scripts/governance/apply_depgraph.py
    option: --query-production
  evidence:
  - 2026-09-24 骨架 R-04 + 簿01 §6 实弹：python scripts/governance/apply_depgraph.py --query-production → usage 报错 exit 2
  - 2026-09-25 本车道只读复跑：选项全集内无含 query 的选项
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-04
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §6
- gap_id: D14-G06
  host_step: D14-06
  finding: R-05
  name_zh: 准入记录面不存在
  decision_question: 模块准入四级筛选的留痕落到哪件里？没有宿主时 MAD 判据怎么回溯？
  note_zh: 政策与多份规则册同源声明的记录件与字段在盘上均无（近似册也无该字段）⇒ 留痕无处可落；本图只点名不修（跨车道纠偏）
  red_reason: ghost_ref
  ghost_refs:
  - module-id-registry.json
  evidence:
  - 2026-09-24 骨架 R-05：find -name module-id-registry.json 零命中；architecture_model/module_id_registry.yaml 无该字段
  - 2026-09-25 本车道只读复跑：同结论
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-05
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §6
- gap_id: D14-G07
  host_steps:
  - D14-14
  - D14-15
  - D14-17
  finding: R-06
  name_zh: 会话工作树 CLI 子命令不存在（四条）
  decision_question: 政策写的四条子命令哪几条真能跑？跑不通时施工收尾怎么落？
  note_zh: 实测 CLI 子命令集仅五种；status/commit 只有库函数未暴露、mark-completed 全仓唯一命中=政策行本身、cleanup 正解为另一子命令（簿03 附实弹 usage 报错）
  red_reason: ghost_ref
  ghost_refs: []
  ghost_cli_anchors:
  - script: scripts/session_worktree.py
    option: status
  - script: scripts/session_worktree.py
    option: commit
  - script: scripts/session_worktree.py
    option: mark-completed
  - script: scripts/session_worktree.py
    option: cleanup
  evidence:
  - '2026-09-24 骨架 R-06 + 簿03 §1/§4 实弹：invalid choice: status（choose from create, exec, merge, abort, list）'
  - 2026-09-25 本车道只读复跑：add_parser 子命令集实测五项
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-06
  - docs/_working/map_build/fig14_construction/03_验收与收尾段.md §1
- gap_id: D14-G08
  host_step: D14-16
  finding: R-07
  name_zh: 锁释放命令契约与实现不符
  decision_question: 照政策抄下来的清理命令能跑吗？参数元数谁定的？
  note_zh: 政策写单参形态，实现要求两参以上；意图对应命令是另一子命令 ⇒ 照抄必失败（属命令契约错，不是件不存在）
  red_reason: unwired
  ghost_refs: []
  mismatch_anchors:
  - script: scripts/lock_files.py
    option: release
    policy_form: release-single-arg
    actual_form: file-and-owner
  evidence:
  - 2026-09-24 骨架 R-07 + 簿03 §3：lock_files.py release 分支要求参数不少于 3
  - 2026-09-25 本车道只读复跑：命令集含 release/release-all/release-batch（语义与政策口径不同）
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-07
  - docs/_working/map_build/fig14_construction/03_验收与收尾段.md §3
- gap_id: D14-G09
  host_step: D14-08
  finding: WJ-R-02
  name_zh: 前端真源图路径三份不一（双真源嫌疑）
  decision_question: 政策所指前端真源图路径存在吗？存在几份、字节相同吗？
  note_zh: 政策路径仓根不存在；两处真身并存且字节不同 ⇒ 骨架把该锚标 ✅ 需纠；唯一宿主待裁（X-13），本图不选边
  red_reason: broken_supply
  ghost_refs:
  - web/frontend_map.yaml
  evidence:
  - 2026-09-24 簿01 §8 WJ-R-02：ls web/frontend_map.yaml 不存在；两真身字节不同（113652 vs 71738）
  - 2026-09-25 本车道只读复跑：政策路径件确认不存在（幽灵）
  doc_refs:
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §8
  - docs/_working/map_build/fig14_construction/01_冷启动与设计段.md §9 WJ-R-02
- gap_id: D14-G11
  host_step: D14-03
  finding: R-09
  name_zh: 规则册符号锚不存在
  decision_question: 政策引用的规则节名在那本册里真的存在吗？
  note_zh: 该册节名仅两项，被引节名全文件零命中 ⇒ 引用锚断链（与 gate 实名漂移同族但对象是规则册）
  red_reason: ghost_ref
  ghost_refs: []
  ghost_doc_anchor: docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml#rule_eight
  evidence:
  - 2026-09-24 骨架 R-09 + 簿01 §3：grep -c rule_eight 该册 = 0
  - 2026-09-25 本车道只读复跑：同结论
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-09
- gap_id: D14-G12
  host_steps:
  - D14-04
  - D14-09
  - D14-11
  - D14-12
  - D14-14
  finding: R-11
  name_zh: 上游真源整体归档未跟进（十二处链接）
  decision_question: 本段判据指向的上游真源还在原位置吗？搬走之后判据由谁满足？
  note_zh: 设计备忘体系一次整体搬家早于政策改版 5 天未跟进；全仓仍有大批文件引旧路径；blast radius 实测进 machine_facts（在册可证部分=旧路径引用文件计数）
  red_reason: broken_supply
  ghost_refs:
  - docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/01_design_memo_management_spec.md
  - docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/65_git_safety_governance.md
  - docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md
  - docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/construction_progress_tracker.md
  - docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/00_index_trading_decision.md
  evidence:
  - 2026-09-24 骨架 R-11 + §7-C7：原目录仅剩 README + 16 号，archive 侧实测 49 件
  - 2026-09-25 本车道只读复跑：政策所引五件旧路径全部不在原位
  doc_refs:
  - docs/_working/map_build/fig14_construction/00_skeleton.md §1 红条目 R-11
  - docs/_working/map_build/fig14_construction/02_施工与门禁段.md §4
matrix_gaps:
- policy_row: Step 1 前置·地图逐层讨论闸
  kind: 矩阵有多余行
  note_zh: 正文无同名 Step 段，属矩阵侧冗行
- policy_row: Step 3.5
  kind: 矩阵缺行
  note_zh: 正文有 Step 3.5 段、矩阵无对应行（R-15）；2026-09-26 本车道 L-POL14 已按 Step 3.5 正文实测工序在政策 §2.3 补行，本差集已消，待生成器随下次再生刷新 machine_facts
loops:
- loop_id: B5
  from: D14-07
  to: D14-06
  kind: in_graph
  note_zh: domain 不一致回登记
- loop_id: B8
  from: D14-09
  to: D14-02
  kind: in_graph
  note_zh: 算法缺失回补文档（本图最长回边）
- loop_id: B9
  from: D14-10
  to: D14-10
  kind: in_graph_self_loop
  max_rounds_ref: zephyr.governance.persistence.task_repo#CIRCULAR_ACCEPTANCE_ROUNDS
  note_zh: 循环验收真自环，轮次由代码常量定
- loop_id: B10
  from: D14-11
  to: D14-09
  kind: in_graph
  note_zh: FAIL 无法就地修回施工
- loop_id: B11
  from: D14-12
  to: D14-09
  kind: in_graph
  note_zh: 文档代码漂移回施工
- loop_id: B12
  from: D14-13
  to: D14-12
  kind: in_graph
  note_zh: 对齐失败回文档
- loop_id: B13
  from: D14-15
  to: D14-11
  kind: in_graph
  note_zh: 网关拒绝回长清单审查（跨段长回边）
- loop_id: B1
  from: D14-02
  to: null
  kind: out_of_graph
  red_reason: terminal
  note_zh: GAP 回讨论环节，目的地是设计备忘/架构条目（上游已归档，见 D14-G12）
- loop_id: B2
  from: D14-04
  to: D14-04
  kind: pending
  red_reason: unwired
  note_zh: 否决后重设计再评审=自环，无轮次常量 ⇒ 不得进图
- loop_id: B3
  from: D14-05
  to: D14-05
  kind: pending
  red_reason: unwired
  note_zh: 无日志回本步补挖（阻塞前进）=自环，无轮次常量
- loop_id: B4
  from: D14-06
  to: null
  kind: out_of_graph
  red_reason: terminal
  note_zh: 依赖缺失回设计备忘补设计（出图，同 B1 目的地）
- loop_id: B6
  from: D14-07
  to: D14-07
  kind: pending
  red_reason: unwired
  note_zh: 孤儿/状态漂移重跑同步与对齐=自环，无轮次常量
- loop_id: B7
  from: D14-08
  to: null
  kind: out_of_graph
  red_reason: terminal
  note_zh: 该拆不拆转前端拆件子 SOP 闭环（子流程真源另册）
- loop_id: B14
  from: D14-17
  to: null
  kind: terminal_branch
  red_reason: terminal
  note_zh: 合并冲突暂不清理=终止分支，非回边
- loop_id: B15
  from: D14-14
  to: null
  kind: recovery_branch
  red_reason: terminal
  note_zh: 文件丢失经版本库恢复后重走，恢复机制归交付流水线
laws:
- 图只存 step_id 与引用，禁复制政策正文——政策自述是编排层，本图同构承接
- 每个环节必须有可执行真相源或已登记门禁作锚，否则记 manual 并计入红账
- 落地收尾机制属交付流水线（图11），本图只挂 handoff 引用，禁重复登记
- 状态列与可机验列两列口径独立，禁压成一列；production 数恒等骨架 ✅ 数
- handoff 段不得借图11 的 auto 结论抬本图分数（反洗白，取簿03 实测口径）
boundary:
- 不画提交门禁体系与队列落地机制——config/governance_operations_map.yaml 的 out_of_scope_refs 原文已排除，归属图11
- 不含数据运维流——政策边界节明令数据运维另必读 data_ops 规程
- 轴区分：本图 step_id=D14-* ；作战地图 step_id=BM-*（交易 flow_stage 值域闭集，施工步骤挂入必被判域漂移）
- 不裁域宽：政策 scope 声明与正文收窄口径矛盾（骨架 R-16），本图按正文收窄口径建，矛盾交总包裁定
```
# >>>CONSTRUCTION_STEP_ANCHORS<<<
