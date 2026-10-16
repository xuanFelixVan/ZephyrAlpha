---
doc_type: index
ttl: permanent
generated_by: scripts/governance/generators/generate_rule_ai_perception_index.py
title: 规则地图（图17·治理域纵向地图）
---

# 规则地图（图17 · 治理域纵向地图）

> **派生视图（机生禁手改）**：真源=`docs/01_policies_and_standards/rules/trae_*.yaml`（规则本体）+ 环节裁定；
> 重扫：`python scripts/governance/generators/generate_rule_ai_perception_index.py`（同时产出机读路由册 `catalogs/rule_stage_routing.yaml`）。
> **用法**：先判「我现在在哪个环节」→ 进该环节读规则包+SOP 包 → 再动手。主题检索：`python -m zephyr.library.lookup <关键词>`。
> **与流程地图的关系（指针互链，不合并）**：本图答「每个环节守什么规矩」；图11 提交链答「链哪里卡」、图14 施工流答「怎么建」、图12 数据链答「数据怎么供」、TDM 答「买什么」。

## §0 环节速查（纵轴）

| 环节 | 名称 | 归属规则 | 一岗多流程指针 | 何时必读 |
|---|---|---|---|---|
| S0 | 治理与裁定 | 10 | 1 | 开裁定/审计战役前；口径争执时；判定某条规则该留该改该退役时 |
| S1 | 开工前置 | 8 | 0 | 写第一行业务代码前；新建文件/模块前；领任务卡时 |
| S2 | 施工建造 | 29 | 1 | 新模块施工前；前端拆件前；文档定稿前 |
| S3 | 提交落地 | 16 | 1 | 提交前；冲突/死信/接管时；清理 worktree 前 |
| S4 | 数据供给 | 5 | 1 | 数据回灌/坏数据修复/表结构变更/判重/缺口处置前 |
| S5 | 挖矿研究 | 0 | 1 | 全网调研/找方案/建策略前；新域开工挖骨架前 |
| S6 | 业务决策 | 1 | 0 | 回测施工/策略入库/E4 正考前；改判据/建蓝图锚前 |
| S7 | 运维自动化 | 3 | 0 | 系统应急时；排班/插单前；清理前 |
| X | 横切轴 | 15 | 3 | 任何环节都生效：写文件/调 LLM/碰密钥/输出结论时 |

## §1 横切目的标签（T1-T10，待 Owner 终审冻结）

> 同标签多钉 = 重复簇显形位（内收对审入口）。

| 标签 | 大白话 |
|---|---|
| T1 | 新建的东西必须登记姓名籍贯，否则门禁见一次拦一次 |
| T2 | 证明施工队没死，死了别让它继续代表你说话 |
| T3 | 每条规则都要说得清谁在替它出手，否则就是纸上法律 |
| T4 | 每个环节都挂着一本病历本，环节病了翻得到档案 |
| T5 | 同一事实只许一个家，其他副本都是快照 |
| T6 | AI 说的每句话都要能回到真源，不能靠记忆拍脑袋 |
| T7 | 密钥权限走专道，裸拿硬编码都是开门揖盗 |
| T8 | 非开发的人一遍能读懂这资产干嘛的、何时用它 |
| T9 | 任何动作都要留得下回头路，删之前先想好怎么活过来 |
| T10 | 同一个错犯第三次，就该把它变成机器判据而不是又写一遍提示词 |

---

## S0 · 治理与裁定

> 宪法/元规则/裁定/对齐/审计——管所有环节怎么判、怎么留痕

- **何时必读**：开裁定/审计战役前；口径争执时；判定某条规则该留该改该退役时
- **互链地图**：—

### 规则包（10 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-024 | 方法论-诊断与根因分析 | methodology_diagnosis | evolving | warning | — |
| TRAE-025 | 方法论-决策与执行 | methodology_decision | evolving | warning | — |
| TRAE-026 | 方法论-质量与度量 | methodology_quality | evolving | warning | — |
| TRAE-027 | 方法论-协作与演进 | methodology_collaboration | evolving | warning | — |
| TRAE-041 | 元规则-规则分类与裁决 | meta_rule_classification | evolving | warning | — |
| TRAE-042 | 元规则-标准体系与模板 | meta_standard_template | evolving | warning | — |
| TRAE-043 | 元规则-元数据与度量 | meta_metadata_metrics | evolving | warning | — |
| TRAE-044 | 合规治理-审计与监管 | compliance_audit | stable | error | — |
| TRAE-060 | 向内收原则（唯一真源·事件驱动·第一性原理） | global | frozen | critical | — |
| TRAE-081 | 审计审查维度框架（54 维度基座） | audit_dimensions_framework | evolving | info | — |

**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-087

### SOP 包（13 件）

- `sop/governance_sop/adjudication_routing_policy.md` — 裁定路由政策——五门流水线 × 八类路由 × 三轴价值标准（Owner 拍板带宽的标准化真源）
- `sop/governance_sop/agent_constitution_l0.md` — ZephyrAlpha AI Agent 宪法 L0（≤300 行硬规则+索引）
- `sop/governance_sop/agent_constitution_legacy_v1.md` — AI Agent 宪法 v1 归档（1639 行全文，2026-09-12 被 L0 替换）
- `sop/governance_sop/alignment_checklist.md` — 全项目对齐清单——全图全库+代码文档三层对齐规则（全图全库对齐版）
- `sop/governance_sop/commit_guide_sources/index.md` — commit_guide_sources — 目录索引
- `sop/governance_sop/commit_navigation_playbook.md` — 提交指路指南（机生版）
- `sop/governance_sop/construction_ledger_method_policy.md` — 施工台账方法论——车道存活三查·停手回流·回执六项·"永不说全绿"（多车道战役台账法）
- `sop/governance_sop/deep_adjudication_method_policy.md` — 深度裁定方法论——"只给最强模型"战场划分法 × 全仓待裁穷举扫描法（裁定/审计战役通用真源）
- `sop/governance_sop/index.md` — governance_sop — 目录索引
- `sop/review_sop/deep_review_policy.md` — 代码与算法深度审查流程标准作业规程（SOP）——六轴审查法
- `sop/review_sop/defect_pattern_checklist.md` — 缺陷模式库——深度审查强制前置 checklist（15 条，每条带真实案例锚点）
- `sop/review_sop/index.md` — review_sop — 目录索引
- `sop/review_sop/rule_disposition_policy.md` — 规则处置程序法——六道闸判定 × 六类归宿（每条规则/每台裁判的唯一判决流程）

### 政策

- `policies/workspace_governance_policy.md`

### 病历/台账挂载

- ruling_registry.yaml（裁定册）
- casebook_registry.yaml（案例册）
- alignment_checklist.md

---

## S1 · 开工前置

> 动手之前：能力反查、任务卡、预注册、新建登记——把规则前置到开工前

- **何时必读**：写第一行业务代码前；新建文件/模块前；领任务卡时
- **互链地图**：—

### 规则包（8 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-002 | 反孤儿与搜索先行协议 | feature_creation | frozen | critical | — |
| TRAE-003 | 任务粒度与完成门槛协议 | task_management | stable | critical | — |
| TRAE-034 | 任务系统-卡片标准与生命周期 | task_card_lifecycle | stable | error | — |
| TRAE-035 | 任务系统-施工与验证 | task_construction_verification | stable | error | — |
| TRAE-056 | 操作-模块/蓝图/代码创建完整工作流程 | module_creation_workflow | evolving | error | — |
| TRAE-065 | 能力反查强制铁律（RULE-CAPABILITY-LOOKUP，裁定 | capability_lookup_required | evolving | critical | CAPABILITY-LOOKUP-REQUIRED |
| TRAE-077 | capability lookup bypass 场景分类铁律（Capability Lookup Bypass Scene Classification，裁定 | capability_lookup_bypass_stats | evolving | warning | CAPABILITY-LOOKUP-HEALTH⚠️悬空、CAPABILITY-LOOKUP-REQUIRED |
| TRAE-087 | 原问题登记与基建先挖后建铁律（问题定义纪律+五要素入表+施工标准立法） | global_construction | new | high | — |

### SOP 包（3 件）

- `sop/library_sop/blood_flesh_cataloging_sop.md` — 血肉编目标准作业规程（SOP）——资产人读描述区必填与质量标准
- `sop/library_sop/index.md` — library_sop — 目录索引
- `sop/library_sop/offzone_retrieval_boundary_sop.md` — 场外区检索边界 SOP——工棚卷宗不入馆的边界登记与三源检索通道（F2 裁决落地）

### 病历/台账挂载

- creation_token 账本
- module_translation_registry.yaml

---

## S2 · 施工建造

> 写第一行业务代码到模块成型：架构/命名/测试/文档/模块登记/前端

- **何时必读**：新模块施工前；前端拆件前；文档定稿前
- **互链地图**：图14 施工流（map_build/fig14_construction/）

### 规则包（29 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-004 | 并行执行与原子事务协议 | script_execution | frozen | critical | — |
| TRAE-005 | 修改原则与治理施工协议 | code_modification | frozen | critical | — |
| TRAE-010 | 代码构建-命名与组织 | code_naming | stable | error | — |
| TRAE-011 | 代码构建-类型与导入 | code_type_import | stable | error | — |
| TRAE-012 | 代码构建-测试与安全 | code_test_security | stable | error | — |
| TRAE-013 | 架构约束-跨包依赖 | architecture_dependency | stable | error | — |
| TRAE-014 | 架构约束-蓝图对齐 | architecture_blueprint | stable | error | — |
| TRAE-015 | 架构约束-路径与注册 | architecture_path_registry | stable | error | — |
| TRAE-016 | 架构约束-漂移检测 | architecture_drift | stable | error | — |
| TRAE-017 | 架构约束-治理顺序 | architecture_governance_order | stable | error | — |
| TRAE-028 | 文档治理-结构与命名 | doc_structure_naming | stable | error | — |
| TRAE-029 | 文档治理-操作安全 | doc_operation_safety | stable | error | — |
| TRAE-030 | 文档治理-编号与元数据 | doc_numbering_metadata | stable | error | — |
| TRAE-032 | 模块治理-准入与生命周期 | module_governance | stable | error | — |
| TRAE-033 | 模块治理-注册与同步 | module_registry_sync | stable | error | — |
| TRAE-036 | 架构治理-门禁与过渡 | architecture_gate_transition | stable | error | — |
| TRAE-037 | 架构治理-合格与版本化 | architecture_qualification | stable | error | — |
| TRAE-038 | 架构治理-CTR注入规则 | architecture_ctr_injection | stable | error | — |
| TRAE-046 | 工程治理-代码重组安全 | engineering_code_restructure | stable | error | — |
| TRAE-047 | 工程治理-文件头部与扩展 | engineering_header_expansion | stable | error | — |
| TRAE-052 | 铁律补充-跨蓝图变更与项目瘦身 | cross_blueprint_change_cleanup | frozen | critical | — |
| TRAE-054 | depgraph 程序化访问协议 | depgraph_access_protocol | frozen | critical | — |
| TRAE-055 | 架构容量与域治理规则 | arch_domain_capacity_governance | stable | critical | — |
| TRAE-058 | 全景图扫描排除规则 | depgraph_scan_exclusions | evolving | error | — |
| TRAE-061 | decisiongraph 程序化访问协议 | decisiongraph_access_protocol | evolving | critical | — |
| TRAE-080 | 五图对齐铁律（设计态先行 + 派生 + 对齐验证） | panorama_alignment | evolving | critical | — |
| TRAE-082 | Symbol 约定铁律（裸码 symbol + exchange 列 + 派生 symbol_canonical） | symbol_convention | evolving | critical | — |
| TRAE-083 | 设计意图查询真源铁律（问题类型→查询源映射） | design_intent_source_discipline | evolving | critical | — |
| TRAE-086 | 前端功能模块施工铁律（拆件判据+后端盘点真源接通+命名+目录归属+四件套闭环） | frontend_construction | evolving | critical | — |

**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-001

### SOP 包（6 件）

- `sop/construction_sop/construction_workflow_policy.md` — 交易决策域施工流程标准作业规程（SOP）——端到端 17 段施工闭环
- `sop/construction_sop/document_review_and_optimization_policy.md` — 文档审查与优化流程标准作业规程（SOP）——七轮循环工作法
- `sop/construction_sop/frontend_component_split_policy.md` — 前端组件拆分与数据接通 SOP（stockq 页实证）
- `sop/construction_sop/index.md` — construction_sop — 目录索引
- `sop/construction_sop/lane_construction_discipline_policy.md` — 车道施工纪律 SOP——多车道并发施工全纪律一页册（冷启动/提交正门/新建三件套/热注册表/门禁红线/并发安全/EOL/判据交付）
- `sop/construction_sop/task_card_work_order_policy.md` — 任务卡工单制政策 v1.0——施工必开卡/两轮预审验收/闸消费/图书馆预留/豁免判据

### 政策

- `policies/c3_translation_pipeline_ruling.md`

### 病历/台账挂载

- defect_pattern_checklist.md（缺陷模式册）
- fms_deadref_baseline.yaml

---

## S3 · 提交落地

> 拿锁→验货→暂存→commit→入队→真落盘→死信归因——最痛环节的规矩集中地

- **何时必读**：提交前；冲突/死信/接管时；清理 worktree 前
- **互链地图**：图11 提交链（map_build/fig11_delivery/）

### 规则包（16 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-064 | Git 调用预算铁律（ARCH-GIT-CALL-BUDGET） | git_subprocess_budget | evolving | critical | — |
| TRAE-066 | RunCommand 命令纯洁性铁律（RULE-SEVENTEEN 外部化） | runcommand_purity | frozen | critical | — |
| TRAE-067 | AI RunCommand 窗口闪现纪律铁律（Window Flash Discipline） | runcommand_window_discipline | evolving | high | — |
| TRAE-068 | 第 6 层可预防性铁律（Preventability Layer，6 层闭环模型正式化，裁定 | preventability_layer | evolving | critical | GATE-FORGED-GW-MARKER⚠️悬空 |
| TRAE-069 | Commit Gateway 滥用监控阈值配置 |  | stable |  | — |
| TRAE-070 | 临时文件放置规范 |  | stable |  | — |
| TRAE-071 | 临时文件生命周期管理 |  | stable |  | — |
| TRAE-072 | 跨 commit 原子性铁律（Cross-Commit Atomicity，裁定 | cross_commit_atomicity | evolving | critical | GATE-IMPORT-INTEGRITY⚠️悬空 |
| TRAE-073 | pre-commit hook 离线可运行纪律铁律（Pre-commit Offline Discipline） | precommit_offline_discipline | stable | high | — |
| TRAE-074 | worktree base 新鲜度全生命周期铁律（Worktree Base Freshness Full Lifecycle，裁定 | worktree_base_freshness | evolving | critical | — |
| TRAE-075 | stash 生命周期铁律（Stash Lifecycle，裁定 | stash_lifecycle | evolving | critical | — |
| TRAE-076 | worktree commit 持久性 + start fail-closed 铁律（Worktree Commit Persistence + Start Fail-Closed，裁定 | worktree_commit_persistence | evolving | critical | WORKSPACE-CLEAN-CHECK⚠️悬空 |
| TRAE-078 | force=True 逃生通道安全分类铁律（Force Merge Safety Classification，裁定 | force_merge_safety_classification | evolving | critical | WORKSPACE-CLEAN-CHECK⚠️悬空、PRE-MERGE-TOPO-CHECK⚠️悬空、BASE-FRESHNESS-MERGE⚠️悬空、SCHRODINGER_ROLLBACK_DETECTED⚠️悬空 |
| TRAE-079 | commit 临界区文件锁串行化铁律（Commit Critical Section Serialization，裁定 | commit_critical_section_serialization | evolving | critical | HELD-OVERLAP、WORKSPACE-DRIFT⚠️悬空 |
| TRAE-084 | pre-commit hook 增量守门纪律铁律（Pre-commit Incremental Discipline） | precommit_incremental_discipline | stable | high | — |
| TRAE-085 | 陈旧基线整文件覆写禁令（Stale-Base Overwrite Prohibition） | stale_base_overwrite | stable | high | — |

**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-001

### SOP 包（5 件）

- `sop/ops_sop/emergency_runbook.md` — 保命轨 D-L1~D-L3 人工 Runbook
- `sop/ops_sop/index.md` — ops_sop — 目录索引
- `sop/ops_sop/merge_conflict_resolution_policy.md` — Merge 冲突处理 SOP——冲突三分法 + 标准 7 步流程（不盲选边，逐个读内容，结果留痕）
- `sop/ops_sop/worktree_cleanup_policy.md` — Worktree 清理 SOP——四证齐全方可删除（死亡证明/无未合并工作/统筹批准/可恢复证明）
- `sop/governance_sop/commit_navigation_playbook.md` — commit_navigation_playbook

### 政策

- `policies/branch_strategy_policy.md`
- `policies/parallel_session_coordination_policy.md`

### 病历/台账挂载

- death_cases_registry.yaml（死信册）
- landing_journey_registry.yaml

---

## S4 · 数据供给

> 数据回灌/修复/判重/口径/PIT/SSOT——业务与挖矿之上的数据地基

- **何时必读**：数据回灌/坏数据修复/表结构变更/判重/缺口处置前
- **互链地图**：图12 数据链

### 规则包（5 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-045 | 数据治理-质量与血缘 | data_governance | stable | error | — |
| TRAE-050 | 域策略-数据源与因子层 | domain_data_factor | evolving | warning | — |
| TRAE-059 | _schema_version 写入保护规范 | schema_version_write_protection | frozen | critical | — |
| TRAE-062 | SSoT 真源分类铁律（YAML vs DB） | ssot_classification | evolving | critical | — |
| TRAE-063 | 数据库破坏性操作纪律（RULE-DATA-OPS） | data_ops_discipline | frozen | critical | — |

**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-051

### SOP 包（5 件）

- `sop/data_ops_sop/data_ops_policy.md` — 数据操作 SOP——回灌/修复/判重/PIT/探针全流程方法论（三步验证+幂等回补+FINAL 逐位验证）
- `sop/data_ops_sop/data_source_onboarding_sop.md` — 数据源全生命周期 SOP——从挖矿到消费端接线（流程编排真源）
- `sop/data_ops_sop/index.md` — data_ops_sop — 目录索引
- `sop/data_audit_sop/index.md` — data_audit_sop — 目录索引
- `sop/data_audit_sop/industry_chain_data_audit_policy.md` — 产业链供应链全景图数据审计与更新SOP——夜班自主执行版

### 政策

- `policies/graph_quality_standard.md`
- `policies/expectation_consumption_design_policy.md`

### 病历/台账挂载

- 回填台账（daily_valuation/stock_basic）

---

## S5 · 挖矿研究

> 找方案/建策略/因子指标挖掘/骨架构建——无专属规则，SOP 驱动环节

- **何时必读**：全网调研/找方案/建策略前；新域开工挖骨架前
- **互链地图**：—


**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-050

### SOP 包（7 件）

- `sop/mining_sop/factor_mining_sop_policy.md` — 因子挖掘 SOP——矿脉→假设→IC筛→预注册→沙箱→E4正考→组队→入库 八段缝合册（regime 条件化强制）
- `sop/mining_sop/index.md` — mining_sop — 目录索引
- `sop/mining_sop/indicator_mining_sop_policy.md` — 指标挖矿 SOP——TASC 论文定向检索+公式可验证性唯一准入闸+时盒停手立卡（技术指标公式移植入库生产线）
- `sop/mining_sop/mining_sop_policy.md` — 挖矿 SOP——全网调研+内部反查的全面挖掘方法论（六向寻路/防噪音四闸/矿脉枯竭终止/挖后自审闸）
- `sop/mining_sop/skeleton_mining_policy.md` — 骨架构建 SOP——域骨架的挖掘、分层、判据与防腐（全域适用：数据/因子/消费端/系统功能）
- `sop/mining_sop/trading_decision_map_pathfinding_policy.md` — 交易决策全景图病菌寻路增长 SOP——六向寻路+防噪音四闸（长期增长机制真源）
- `sop/mining_sop/vertical_map_mounting_policy.md` — 纵向地图挂图 SOP——血肉挂载、病历挂载、目的标签与内收对审（纵轴地图家族通用）

### 病历/台账挂载

- experiment_registry.yaml

---

## S6 · 业务决策

> 回测体系/策略入库/TDM 地图/考试政策——业务侧怎么验证和出手

- **何时必读**：回测施工/策略入库/E4 正考前；改判据/建蓝图锚前
- **互链地图**：TDM 地图（docs/02_enterprise_architecture/10_trading_map/）

### 规则包（1 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-051 | 域策略-风控与盘后层 | domain_risk_analytics | evolving | warning | — |

### SOP 包（10 件）

- `sop/backtest_system_sop/exam_policy.md` — 考试政策 exam_policy——E4 正考准入·执行口径·成本双口径·复权降级·负结果台账
- `sop/backtest_system_sop/index.md` — backtest_system_sop — 目录索引
- `sop/backtest_system_sop/README.md` — 回测体系 SOP 总纲——分级回测金字塔 × AI 自驱循环 × 策略库入库漏斗
- `sop/backtest_system_sop/sop_a_full_map_orchestration.md` — SOP-A 全图回测编排——注册·分类·优先级·批次推进·归档升级
- `sop/backtest_system_sop/sop_b_node_loop.md` — SOP-B 单节点 AI 自驱回测七步循环——调研·数据·宽测·剪枝·窄测·归档
- `sop/backtest_system_sop/sop_c_strategy_library_intake.md` — SOP-C 外部策略入库漏斗——盘点·粗筛·翻译·快筛·去重·入库挂图
- `sop/backtest_system_sop/sop_d_run_archive_naming.md` — SOP-D 回测档案管理规范——run 目录·编号·结构·自动落盘·复现演练（图书馆规则）
- `sop/trading_decision_map_sop/index.md` — trading_decision_map_sop — 目录索引
- `sop/trading_decision_map_sop/tdm_consumption_policy.md` — 交易决策全景图·消费场景规程（TDM Consumption Policy）——什么场合必须打开地图、读什么、验证什么
- `sop/trading_decision_map_sop/trading_decision_map_layering_policy.md` — 交易决策地图逐层讨论 SOP——防撞车·防越级·防枝末先行

### 政策

- `policies/strategy_intake_acceptance6_evidence.md`

### 病历/台账挂载

- backtest_backlog.yaml（预注册 backlog）
- trial_ledger_registry.yaml（试次册）

---

## S7 · 运维自动化

> 应急/冲突/清理/班底值守/会话活性——系统活着时的日常运维规矩

- **何时必读**：系统应急时；排班/插单前；清理前
- **互链地图**：图13 日周期（map_build/fig13_daycycle/）

### 规则包（3 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-048 | 操作-Vibe Coding会话管理 | operational_vibe_coding | evolving | warning | — |
| TRAE-049 | 操作-领域操作手册 | operational_domain | evolving | warning | — |
| TRAE-053 | 铁律补充-自动化双轨判定 | automation_dual_track | frozen | critical | — |

### SOP 包（6 件）

- `sop/ops_sop/emergency_runbook.md` — 保命轨 D-L1~D-L3 人工 Runbook
- `sop/ops_sop/index.md` — ops_sop — 目录索引
- `sop/ops_sop/merge_conflict_resolution_policy.md` — Merge 冲突处理 SOP——冲突三分法 + 标准 7 步流程（不盲选边，逐个读内容，结果留痕）
- `sop/ops_sop/worktree_cleanup_policy.md` — Worktree 清理 SOP——四证齐全方可删除（死亡证明/无未合并工作/统筹批准/可恢复证明）
- `sop/automation_sop/automation_crew_policy.md` — 自动化班底值守 SOP（双引擎两班制：治理班×业务班）
- `sop/automation_sop/index.md` — 自动化班底族索引

### 病历/台账挂载

- takeover_ledger.jsonl（接管台账）
- process_reaper_keep.txt

---

## X · 横切轴

> 全域生效的规则（文件锁/反幻觉/行为禁令/密钥/AI 线）——钉在每一段上

- **何时必读**：任何环节都生效：写文件/调 LLM/碰密钥/输出结论时
- **互链地图**：—

### 规则包（15 条）

| rule_id | title | scope | stability | severity | 关联门禁 |
|---|---|---|---|---|---|
| TRAE-001 | 文件操作安全协议 | file_operation | frozen | critical | G0⚠️悬空 |
| TRAE-006 | 防幻觉-结构追溯层 | code_structure | frozen | critical | — |
| TRAE-007 | 防幻觉-行为约束层 | code_behavior | frozen | critical | — |
| TRAE-008 | 防幻觉-输出验证层 | output_verification | frozen | critical | — |
| TRAE-009 | 防幻觉-安全防护层 | security_guard | frozen | critical | — |
| TRAE-018 | 行为边界-代码操作绝对禁止 | code_operation_prohibition | frozen | critical | — |
| TRAE-019 | 行为边界-系统安全绝对禁止 | security_prohibition | frozen | critical | — |
| TRAE-020 | 行为边界-治理纪律绝对禁止 | governance_prohibition | frozen | critical | — |
| TRAE-021 | 行为边界-其余绝对禁止 | other_prohibition | frozen | critical | — |
| TRAE-022 | 行为边界-条件禁止(代码与安全) | conditional_prohibition_code_security | stable | error | — |
| TRAE-023 | 行为边界-条件禁止(治理与文档) | conditional_prohibition_governance_doc | stable | error | — |
| TRAE-031 | 安全治理-密钥与访问控制 | security_access | stable | error | — |
| TRAE-039 | AI治理-幻觉检测与自检 | ai_hallucination | stable | error | — |
| TRAE-040 | AI治理-模型路由与协作 | ai_model_routing | stable | error | — |
| TRAE-057 | AI消费优先原则 | global | frozen | error | — |

**一岗多流程指针**（他环节主挂，此处只存指针）：TRAE-062、TRAE-065、TRAE-077

### 病历/台账挂载

- ruling_registry.yaml
- casebook_registry.yaml

---

## §9 覆盖账本（机生）

- 规则总数 87：归属 87 条，未归属 0 条
- 门禁总册 191 台
- 重扫命令：`python scripts/governance/generators/generate_rule_ai_perception_index.py --check`
