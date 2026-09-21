---
ttl: permanent
doc_type: policy
rule_form: checklist
verifiability: manual
title: 全项目对齐清单——全图全库+代码文档三层对齐规则（全图全库对齐版）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.6.0"
date: 2026-09-15
topic: full_project_alignment_checklist
scope: global
depends_on:
  - construction_workflow_sop
  - document_review_and_optimization_sop
  - trae_080_panorama_alignment
related_issues:
  - "#ARCH-ALIGN-NAMING-001（全图全库对齐简称，计数无关命名裁定）"
related_modules:
  - scripts/governance/d5_architecture/generators/align_all.py
  - scripts/governance/d5_architecture/generators/align_panoramas.py
  - src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py
---

# 全项目对齐清单——全图全库+代码文档三层对齐规则

> **简称：全图全库对齐**（Owner 2026-09-05 裁定 #ARCH-ALIGN-NAMING-001——计数无关命名：本体系历经五图→六图→七图三次改名，每次都迫使文档返工；本名不随全景图/注册表数量增长腐化。口语"跑一下全图全库对齐"=`python scripts/governance/d5_architecture/generators/align_all.py`。当前实际数量：全景图现 10 张+注册表 49 个，见 §3/§4）
> 本清单是 **全项目对齐** 的**资产清单层真源**，列出"要对齐哪些东西、每个东西的对齐规则、用什么工具、不一致怎么办"。
> **性质**：清单层，只列对齐对象+规则+工具+处置，不编排流程。流程见 [construction_workflow_sop](../construction_sop/construction_workflow_policy.md)（施工 SOP，管"什么时候对齐、怎么对齐"）。
> **适用范围**：**全项目所有模块/前端/文档/注册表**，不限于 07 域。新 AI 进项目必读。
> **管理规范**：[01_design_memo_management_spec](../../../_working/archive/2026-09/design_memos/01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G06 全项目对齐清单 |
| 创建 | 2026-08-31 |
| 优先级 | P0（所有施工的前置依赖） |
| 状态 | active v1.1.0 |
| 上游 | [construction_workflow_sop](../construction_sop/construction_workflow_policy.md)（施工流程）、[trae_080_panorama_alignment](../rules/trae_080_panorama_alignment.yaml)（五图对齐铁律） |
| 下游 | 所有施工 AI session（必读）、panorama_alignment_gate（门禁扩展依据） |
| 真源边界 | 本文件只列对齐对象+规则+工具+处置；流程步骤以 construction_workflow_sop 为准 |
| 冲突解决 | 流程以 SOP 为准，清单以本文件为准 |

## 2. 背景与定位

### 2.1 痛点

项目对齐体系**片段化**：
- 全景图对齐只有五图（depgraph/dataflowgraph/decisiongraph/blueprint/battle_map），**缺前端全景图**（frontend_map）
- 注册表有 40+ 个（因子库/策略库/技术指标库/候选池/能力注册表等），**注册表之间的对齐规则散落在各处**，没有统一清单
- 代码↔文档↔测试的对齐靠人工自觉，**无系统化检查**
- 新 AI 进项目**不知道要对齐哪些东西**，做完才发现漏了对齐

### 2.2 本清单的解法

- **三层分类**：全图（第一层，现 7 张）+ 注册表（第二层）+ 代码文档（第三层），每层列出全量对象+对齐规则
- **每个对象四要素**：对齐对象（和什么对齐）/ 对齐时机（什么时候检查）/ 对齐工具（用什么脚本/门禁）/ 失败处置（不一致怎么办）
- **新 AI 入口**：本文档列入 [construction_workflow_sop](../construction_sop/construction_workflow_policy.md) Step 0 必看文件清单，新 AI 冷启动时强制加载

## 3. 第一层：全景图对齐（全图全库对齐之"图"）

> 全景图现 10 张：depgraph/dataflowgraph/decisiongraph/blueprint/battle_map/frontend_map/trading_decision_map/industry_chain_map + 策略生产全景图（strategy_production_map，2026-09-13 九图升级：E0-E9 供给端全景 `config/strategy_production_map.yaml`，D38"新图必挂总线"同源——结构校验器/对抗测试先行落地 681a7fc806，FACTORY-MAP gate+本挂轴同批闭环）+ 治理运行地图（governance_operations_map，2026-09-15 十图升级 #ARCH-312：治理运行时流水线骨架机生+人工语义层，`config/governance_operations_map.yaml`，D38"新图必挂总线"同源挂轴）

| 图名 | 真源 | 对齐 key | 对齐规则 | 对齐时机 | 对齐工具 | 失败处置 |
|---|---|---|---|---|---|---|
| **depgraph**（依赖全景图） | PostgreSQL `dep_` 表组 | module_id | 模块间 import 关系必须与代码实际 import 一致 | commit 前 / 新模块注册时 | [apply_depgraph.py](../../../scripts/governance/apply_depgraph.py) | 孤儿模块→阻断 commit |
| **dataflowgraph**（数据流全景图） | PostgreSQL 3 表 | module_id | 数据流 job 必须与代码实际 dataflow 一致 | commit 前 / sync 时 | [sync_panorama_module.py](../../../scripts/governance/sync_panorama_module.py)（单向派生） | 派生失败→阻断 |
| **decisiongraph**（决策流全景图） | PostgreSQL 3 表 | module_id | decision_layer 必须与代码实际决策路径一致 | commit 前 / sync 时 | sync_panorama_module.py（单向派生） | 派生失败→阻断 |
| **blueprint.md**（蓝图） | MD frontmatter | module_id | frontmatter 4 字段（module_id/responsibility_domain/design_maturity/build_status）必须与 depgraph 一致 | commit 前 / sync 时 | sync_panorama_module.py（单向派生） | frontmatter 漂移→warn |
| **battle_map**（作战地图） | PostgreSQL 3 表（battle_map_steps/anchors/edges） | step_id | BM-XXX 环节必须与前四图双向校验 | commit 前 / 改动涉及 BM 环节时 | [generate_battle_map_diagram.py](../../../scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py) | ghost_anchors>0→阻断 |
| **frontend_map**（前端全景图，已建 2026-09-01；v2.0.0 双真源合并+302 功能点补登） | `src/zephyr/frontend/dashboard/web/frontend_map.yaml`（git YAML 真源） | feature_id（F-页面-名） | 前端功能必须挂 backend_ref 到模块注册表（类型化：module:/registry:/table:/api:/none:）；模块必须声明 has_frontend；与 features/manifest.yaml 双向一致 | commit 前 / 新前端功能上线时 | [check_frontend_map.py](../../../scripts/governance/d5_architecture/generators/check_frontend_map.py) 校验器 + **FRONTEND-MAP gate（commit 自动阻断，priority=137）** + scan_frontend_pages.py 半自动补登 | frontend_ref 空→阻断（commit gate 已闭环 2026-09-04） |
| **trading_decision_map**（交易决策地图，2026-09-05 七图升级） | `config/trading_decision_map.yaml`（git YAML 真源） | node_id（TDM-*） | R1-R12 引用校验（策略挂载/因子/数据/module_ref 断链=error 阻断；数据实存性四态=warn）+R8 sequence 成环检测 | commit 前（恒跑 gate）/ align_all 第 7 项 | [check_decision_map.py](../../../scripts/governance/d5_architecture/generators/check_decision_map.py) 校验器 + **DECISION-MAP gate（commit 自动阻断，priority=138）**（校验单一真源=zephyr.trading.decision_map.validate_decision_map） | R1-R8/R10/R12 error>0→阻断；module_ref 缺失→warn（红节点占位） |

**全图统一验证命令（单命令跑全图+注册表层+代码文档抽查）**：
```powershell
python scripts/governance/d5_architecture/generators/align_all.py  # 全图全库统一入口：图 1-5 自动 + 图 6/7 校验内嵌 + 第五节注册表层满贯（19 文件/21 段+字典FK+CAND 转正链+治理双向）+ 第六节文档抽查 + 第七节产业链图 8 + 第八节策略工厂图 9 + 第九节治理运行地图图 10，硬>0=exit 1
python scripts/governance/d5_architecture/generators/check_frontend_map.py  # 图 6 单独跑（快速诊断用）
python scripts/governance/d5_architecture/generators/check_decision_map.py  # 图 7 单独跑（快速诊断用）
python scripts/industry_graph/graph_quality_check.py --json -  # 图 8 数据层单独跑（引擎判定权）
python scripts/governance/d5_architecture/validators/validate_strategy_production_map.py  # 图 9 单独跑（结构+仓储存在性全量，快速诊断用）
```

| **industry_chain_map**（产业链全景图，图 8，2026-09-11 八图升级） | PG industry_chain 表组 + `config/chainmap_cluster_names.yaml` | chain_id（节点经锚点链挂 module_id，MOD 总线两跳） | git 侧：字典↔DDL↔引擎三方同 commit 同步（结构四边）+簇名词表 sanity；数据层：S1-S21 合格线引擎体检（判定权=graph_quality_check，AI 只修复不判定） | align_all 第 7 节恒跑 / 链数据 apply 后 / 触及 git 侧工件 commit 时 | [graph_quality_check.py](../../../scripts/industry_graph/graph_quality_check.py)（数据层）+ **INDUSTRY-CHAIN-MAP gate（priority=141）**（git 侧硬阻断）+ [check_registry_code_anchor 同源共享核心 registry_alignment](../../../src/zephyr/gov_enforcement/registry_alignment.py) | git 侧违规→阻断 commit；数据层违规→引擎判定+align_all 报告（长城专项清欠中，非 advisory 清零后升硬） |
| **strategy_production_map**（策略生产全景图/策略工厂，图 9，2026-09-13 九图升级） | `config/strategy_production_map.yaml`（git YAML 真源） | node_id（FAC-*） | 结构十项校验（字段完整性/边引用闭合/E0-E9 层位/laws/产品清单/built 必有代码锚/lane 归属/未声明反馈环/自环/store_refs 三要素）error>0=阻断；仓储存在性（磁盘路径+CH 表）error=硬、CH 连接异常=warn、待定入库位=warn | commit 前（触发式 gate：图 YAML/校验器变更）/ align_all 第 8 节 | [validate_strategy_production_map.py](../../../scripts/governance/d5_architecture/validators/validate_strategy_production_map.py) 校验器 + **FACTORY-MAP gate（commit 自动阻断，priority=142）**（校验单一真源=validate_structure 动态复用；仓储存在性归 align_all/CLI，CH 环境异常不误伤提交） | 结构 error>0→阻断 commit；仓储缺失→align_all 硬报告 |
| **governance_operations_map**（治理运行地图，图 10，2026-09-15 十图升级 #ARCH-312） | `config/governance_operations_map.yaml`（git YAML 真源，机生，生成器=[generate_governance_map.py](../../../../scripts/governance/generate_governance_map.py)） | module_id（机生层）/ import spec（人工层） | 机生层 families 与生成器 scan() 重建逐模块比对（忽略 generated_at/counts）；人工层 mounts/disconnected import spec 磁盘实存（已删墓碑凭 note 豁免计软）+GOM-L0..L6 层位合法+disconnected 必带 note | commit 前 / align_all 第九节 | align_all 第九节（免独立校验器/免 gate，触发率实证后再议） | error>0 阻断（align_all exit 1）；已删墓碑 warn 待清理 |

**硬阻断条件**：domain_mismatches>0 / ghost_anchors>0 / frontend_ref 悬空（自动门禁建成后；建成前人工确认）；全景图 git 侧工件违规（FRONTEND-MAP/DECISION-MAP/INDUSTRY-CHAIN-MAP/FACTORY-MAP gate）；治理运行地图 error>0（align_all 第九节，图 10 行）

## 4. 第二层：注册表对齐

> 40+ 注册表全量清单见 [registry_master_index.yaml](../_registry/catalogs/registry_master_index.yaml)，此处按域分组列出对齐规则

### 4.1 业务资产库（16 个，全部挂 TDM 交叉轴）

> 2026-09-05 G1 落地（#ARCH-BUSINESS-REG-GATE-001）：六库对齐工具从"门禁（待建）"转正式——**BUSINESS-REGISTRY gate（priority=139）**：条目 id 唯一+module_id 非空 MOD-* 格式（确定性硬）+depgraph 存在性（PG fail-open）；基线 735 条目 module_id 填充率 100% 实证
>
> **2026-09-07 D38 全库满贯**（Owner 裁定）：16 业务库全部挂 trading_decision_map 交叉轴（表驱动 `_XREF_SPECS`，门禁 R3-R36）——策略/因子/数据/指标/执行算法+形态/席位/宏观/周期/宇宙/成本/事件/风险限额/组合模型/基准/告警阈值；**新库必挂铁律**：新建业务库必须同 commit 加轴+挂载，治理库必须在 `tests/trading/test_decision_map.py::TestNewRegistryGate._GOVERNANCE_EXEMPT` 登记豁免——二选一必做，否则测试红（机制化强制每个新 AI 知晓）

> 2026-09-11 满贯扩容（全图全库对齐施工批）：BUSINESS-REGISTRY gate 从 6 库扩至 **19 文件/21 段全量**（data_asset 三段拆分；基线 1463 条目 module_id 填充率+MOD-* 格式 100% 实证后纳入）；校验逻辑唯一真源=[registry_alignment.py](../../../src/zephyr/gov_enforcement/registry_alignment.py)（gate/align_all/pytest 三方同源）。下表列关键库，全量以 REGISTRY_SPECS 为准：

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **factor_registry**（因子库） | depgraph / blueprint / field_dictionary | 模块锚点 + inputs FK 闭环（字段字典可解析） | 新因子注册时 | BUSINESS-REGISTRY gate + test_field_dictionary_fk |
| **strategy_registry**（策略库） | depgraph / blueprint / battle_map | 模块锚点 + 挂 BM-XXX 环节（production 硬/design warn） | 新策略注册时 | BUSINESS-REGISTRY gate |
| **technical_indicator_registry**（技术指标库） | depgraph / blueprint / field_dictionary | 模块锚点 + inputs FK 闭环 | 新指标注册时 | BUSINESS-REGISTRY gate + test_field_dictionary_fk |
| **chart_pattern_registry / portfolio_model_registry / risk_limit_registry / universe / benchmark / cost_model / execution_algo / data_asset(3段) / seat / regime_cycle / event_calendar / macro_indicator / model / alert_threshold / field_dictionary / experiment** | depgraph / blueprint | 条目 id 唯一 + module_id MOD-* + depgraph 存在性（fail-open） | 新条目注册时 | BUSINESS-REGISTRY gate（139，满贯版） |
| **rule_catalog_registry**（规则目录库） | 规则 YAML ↔ Catalog ↔ Disk ↔ Code | 四边纵向闭环（见 §4.4） | 新规则创建时 | RULE-FOUR-WAY-ALIGN gate(76) + align_all 第五节 |

### 4.2 治理库（4 个）

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **architecture_issue_registry**（架构议题库） | ruling_registry | #ARCH-NNN 议题必须有裁定或标 proposed/decided | 议题创建/关闭时 | 既有门禁 |
| **ruling_registry**（裁定库） | architecture_issue_registry | 裁定必须关联议题 | 裁定创建时 | 既有门禁 |
| **candidate_module_registry**（候选池） | capability_canonical_file_registry / depgraph / frontend_map | CAND 转正时必须移到能力注册表 + 登记 depgraph + （涉前端时）登记 frontend_map | CAND 转正 commit | 既有门禁 + 待建 frontend 门禁 |
| **feature_adjudication_registry**（特性裁定库） | architecture_issue_registry | 特性裁定必须关联议题 | 裁定创建时 | 既有门禁 |

### 4.3 能力/依赖库（3 个）

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **capability_canonical_file_registry**（能力→真源文件反查库） | depgraph / 实际文件 | 能力必须指向真实存在的文件路径 | 新能力注册时 / 文件移动时 | 既有门禁 |
| **cross_module_dependency_registry**（跨模块依赖库） | depgraph / 实际代码 import | 声明依赖必须与实际 import 一致 | 新依赖声明时 | 既有门禁 |
| **module_translation_registry**（模块翻译库） | capability_canonical_file_registry | 模块中文名必须与能力注册表一致 | 新模块注册时 | 既有门禁 |

### 4.4 规则库（3 个）

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **rule_catalog_registry**（规则目录库） | 规则 YAML ↔ Catalog ↔ Disk ↔ Code | 四边纵向闭环：①YAML 在目录登记 ②登记 path 磁盘存在 ③frontmatter rule_id=文件名 ④代码 rule_id 引用在目录（--with-code-refs） | 新规则创建时 | [check_rule_four_way_alignment.py](../../../scripts/governance/d5_architecture/checkers/check_rule_four_way_alignment.py)（checker）+ RULE-FOUR-WAY-ALIGN gate(76)（commit 硬）+ align_all 第五节（恒跑报告） |
| **gate_registry**（门禁库） | 实际门禁代码 | 门禁必须在库中登记 | 新门禁创建时 | 既有门禁 |
| **hard_boundaries_registry**（硬边界库） | system_charter | 硬边界必须与宪章一致 | 硬边界变更时 | 既有门禁 |

### 4.5 其他注册表（24+ 个）

> 全量清单见 [registry_master_index.yaml](../_registry/catalogs/registry_master_index.yaml)，此处列出关键对齐规则

| 注册表类别 | 对齐规则 | 对齐时机 |
|---|---|---|
| **告警/阈值类**（alert_threshold_registry 等） | 阈值必须与 config/ 实际配置一致 | 阈值变更时 |
| **基建类**（infrastructure_registry 等） | 基础设施必须与 src/zephyr/infrastructure/ 实际代码一致 | 基建变更时 |
| **模型类**（model_registry 等） | 模型必须与 ML 平台实际注册一致 | 新模型注册时 |
| **数据类**（macro_indicator_registry 等） | 数据资产必须与 schemas/ 实际表一致 | 新数据表创建时 |
| **运行时常数类**（regime_cycle_registry 等） | 常数必须与代码实际值一致 | 常数变更时 |

### 4.6 字典/Schema 类库（新增 2026-09-11）

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **field_dictionary**（全局字段字典） | factor.inputs / technical_indicator.inputs（FK 消费方，62号 §4.6） | FK 悬空=0（inputs 引用字段必须已登记）；field_id/field_name 唯一；孤儿字段 warn 计数 | 新字段/新因子注册时 | test_field_dictionary_fk + align_all 第五节 |
| **industry_graph_field_dictionary**（产业链域字段字典） | DDL-as-Code（apply_industry_graph_ddl）+ 引擎词表 + 工具词表 | 结构四边：表集=DDL ig_* 表集/每表字段=DDL 列/validated_by 引擎存在性/enum vocab 引用 | 字典/DDL/引擎任一变更同 commit | INDUSTRY-CHAIN-MAP gate(141) + test_field_dictionary_alignment（词表↔常量） |

（schema v2.1 code_symbol/code_fingerprint 的门禁 A/B 按 #ARCH-BREG-002 既定路线另行施工，不在本批范围）

**注册表对齐统一原则**：
1. **新建必须登记**：任何新模块/因子/策略/指标/能力/规则/门禁，必须在对应注册表登记，否则门禁拦截
2. **转正必须迁移**：候选池（CAND）转正时必须从 candidate_module_registry 移到正式库
3. **变更必须同步**：注册表内容变更时，必须同步到依赖它的全景图/其他注册表
4. **删除必须清理**：注册表条目删除时，必须清理全景图/其他注册表的引用
5. **新库必挂轴**（D38 铁律，2026-09-07）：新建业务资产库必须在 trading_decision_map `_XREF_SPECS` 同 commit 加交叉轴（两行）+ 真源挂载；治理类库必须在 `TestNewRegistryGate._GOVERNANCE_EXEMPT` 登记豁免——`tests/trading/test_decision_map.py` 门禁测试强制二选一
6. **新图必挂总线**（D38 同源）：新建全景图必须以 module_id 为对齐 key 挂入七图体系（走 MOD 总线两跳互通，不搞 N² 直连），并在本清单 §3 登记

## 5. 第三层：代码↔文档↔测试对齐

| 对齐关系 | 对齐规则 | 对齐时机 | 对齐工具 | 失败处置 |
|---|---|---|---|---|
| **代码 → 蓝图** | 模块代码必须与 blueprint.md 描述的接口/状态机/依赖一致 | commit 前 / 文档审查时 | blueprint_frontmatter_reconciler（post-commit） | 不一致→阻断或 warn |
| **代码 → 设计备忘** | 代码实现必须与 design_memo 决策一致 | 文档审查时 | document_review_and_optimization_sop 第 2 轮 | 不一致→回填或修代码 |
| **代码 → 测试** | 模块代码必须有对应测试文件（tests/ 下） | commit 前 | test_residue_reclaim reconciler | 缺测试→warn |
| **文档 → 代码** | 文档引用的代码路径/接口必须真实存在 | 文档审查时 | document_review_and_optimization_sop 第 2 轮事实核验 | 引用失效→修正文档 |
| **测试 → 代码** | 测试用例必须覆盖代码实际功能 | commit 前 | pytest-cov（可选） | 覆盖率过低→warn |
| **前端 → 后端** | 前端功能必须挂 backend_ref 到模块注册表（frontend_map 已建 2026-09-01；自动门禁待建，暂人工核对） | commit 前 | 人工核对（施工 SOP Step 3）+ 待建 frontend 门禁 | backend_ref 空→阻断 |
| **后端 → 前端** | 后端模块必须声明 has_frontend（frontend_map 已建 2026-09-01；自动门禁待建，暂人工核对） | 新模块注册时 | 人工核对 + 待建 frontend 门禁 | has_frontend 空→阻断 |

## 6. 对齐时机矩阵

| 时机 | 触发条件 | 必须对齐的对象 | 工具 |
|---|---|---|---|
| **commit 前** | 任何 commit | 六图（如触及模块/依赖/路径/蓝图/前端）+ 相关注册表 | panorama_alignment_gate + GitCommitGateway |
| **新模块注册时** | 新建模块 | depgraph + blueprint + capability_canonical_file_registry + module_translation_registry + （涉前端时）frontend_map | 门禁强制 |
| **CAND 转正时** | 候选池转正式 | candidate_module_registry → capability_canonical_file_registry + depgraph + （涉前端时）frontend_map | 门禁强制 |
| **新前端功能上线时** | 前端新功能 commit | frontend_map + 验收单 + backend_ref 挂载 | 人工核对（施工 SOP Step 3）+ 待建 frontend 门禁 |
| **文档审查时** | 按 document_review_and_optimization_sop 七轮流程 | 代码↔文档↔测试 | document_review_and_optimization_sop |
| **新 AI 冷启动时** | 新 AI session 开始 | 必读本清单 + construction_workflow_sop + frontend_handbook（如涉及前端） | construction_workflow_sop Step 0 |
| **新业务条目注册时**（2026-09-11 满贯） | 因子/策略/指标/形态/席位/阈值等任何业务库条目 commit | BUSINESS-REGISTRY gate 21 段整库校验 + depgraph 存在性 + （涉字典）FK 闭环 | gate 139 自动 + align_all 第五节 |
| **产业链工件变更时**（2026-09-11 图 8） | 触及 industry_graph_field_dictionary/chainmap_cluster_names/DDL 真源 | INDUSTRY-CHAIN-MAP gate 结构四边 + 簇名词表 sanity；数据层 align_all 第七节 | gate 141 自动 + align_all 恒跑 |

## 7. 不一致处置

| 不一致类型 | 处置 |
|---|---|
| **六图 domain_mismatches>0** | 阻断 commit，回 Step 2 修正 |
| **六图 ghost_anchors>0** | 阻断 commit，清理幽灵锚点 |
| **注册表条目缺失** | 阻断 commit，补登记 |
| **注册表条目漂移**（内容与实际不一致） | warn-only，登记到漂移清单，定期修复 |
| **代码↔文档不一致** | 文档审查时发现→回填文档或修代码 |
| **代码↔测试缺失** | warn-only，登记到测试补全清单 |
| **frontend_ref 悬空** | 阻断 commit，挂载 backend_ref 或声明 has_frontend=no+理由（自动门禁待建；建成前施工 SOP Step 10 提交时人工确认） |
| **业务库条目违规**（id 重复/module_id 缺失或非 MOD-*/depgraph 不存在） | 阻断 commit（gate 139 满贯版）；depgraph 子检查 DB 不可用 fail-open |
| **产业链 git 侧工件违规**（字典↔DDL↔引擎不同步/簇名词表格式） | 阻断 commit（gate 141）；数据层违规=引擎判定+长城专项清欠（非 advisory 清零后升硬） |
| **字段字典 FK 悬空** | 阻断（test_field_dictionary_fk）；孤儿字段 warn 计数不列清单 |

## 8. 新 AI 必读清单

新 AI 进项目 MUST 按顺序读完以下三份文件：

1. **本清单**（alignment_checklist.md）——知道要对齐哪些东西
2. **[construction_workflow_sop](../construction_sop/construction_workflow_policy.md)**——知道什么时候对齐、怎么对齐
3. **[frontend_handbook](../../../docs/03_modules/_domain_frontend/frontend_handbook/)**（如涉及前端，2026-09-01 已建）——知道前端怎么做

**冷启动验证**：读完后必须能回答"六图是哪六张、注册表分几类、代码文档测试怎么对齐"——答不出=没读懂，重读。

## 9. 边界与不做

### 9.1 不做的事
- **不编排流程**：流程步骤以 construction_workflow_sop 为准，本清单只列对象+规则
- **不重复门禁规则**：门禁具体实现在 src/zephyr/gov_enforcement/commit_gates/，本清单只引用
- **不替代注册表**：注册表内容是各自的真源，本清单只列对齐规则

### 9.2 适用边界
- **适用**：全项目所有模块/前端/文档/注册表的对齐
- **不适用**：具体施工步骤（走 construction_workflow_sop）、文档审查方法（走 document_review_and_optimization_sop）

## 10. 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 初稿：三层对齐体系（六图+注册表+代码文档）+ 对齐时机矩阵 + 新 AI 必读清单 | 项目对齐体系片段化，缺统一清单；新 AI 进项目不知道要对齐什么；前端全景图（frontend_map）待建需预留对齐规则 |
| 2026-09-04 | 1.1.0 | frontend_map 状态修正：待建→已建（2026-09-01 实建 web/frontend_map.yaml，stockq 功能点已登记）+ 真源路径修正（原写的 architecture_model/frontend/ 为失效路径）+ 对齐工具改"人工核对（施工 SOP Step 3）+自动门禁待建" | Owner 巡检发现清单状态漂移：frontend_map.yaml 已实建 4 天，清单仍标"待建"且真源路径失效——对齐清单自身先对齐（§5 文档→代码规则自证） |
| 2026-09-04 | 1.2.0 | frontend_map 双真源合并落地（Owner 裁定：web 版唯一真源）+ 全景图补登专项 + 对齐校验器 | ①architecture_model/frontend/ 版（74KB/17 功能点/三级）降级废弃，superseded_by 指向 web 版；②web 版 v2.0.0：迁移 21 条真增量（2 条语义重复合并）+scan_frontend_pages 改造指向 web 版半自动补登 38 页→302 功能点/44 页全类型化零重复；③gap_views 脚本改读 web 版+悬空判定升级五前缀；④新建 check_frontend_map.py 校验器（R0 id 重复/R1 类型化/R2 manifest 双向/R3 file 存在，auto 条目宽严分级）——对齐工具"待建"项部分落地 |
| 2026-09-05 | 1.3.0 | **"全图全库对齐"简称裁定（#ARCH-ALIGN-NAMING-001）+ 第七图 trading_decision_map 入表 + §4.1 业务库门禁转正式** | ①计数无关命名（五图→六图→七图三次改名腐化史）；②§3 新增图 7 行（R1-R12 校验+DECISION-MAP gate 138+check_decision_map 校验器）+验证命令块更新；③§4.1 六库对齐工具"门禁（待建）"→BUSINESS-REGISTRY gate(139) 转正式（G1 落地，基线 735 条目 100% 实证）——配合 #ARCH-DECISION-MAP-GATE-001/#ARCH-BUSINESS-REG-GATE-001/#ARCH-BATTLE-MAP-HARD-001 三裁定 |
| 2026-09-11 | 1.4.0 | **八图满贯（全图全库对齐施工批）**：①§3 新增图 8 产业链全景图行（chain_id 轴+INDUSTRY-CHAIN-MAP gate 141+graph_quality_check 引擎判定）；②§4.1 BUSINESS-REGISTRY gate 6→19 文件/21 段满贯扩容（基线 1463 条目 100% 实证，逻辑真源=registry_alignment.py 三方同源）；③§4.4 rule_catalog 行工具落地四边 checker 真源链接；④新增 §4.6 字典/Schema 类（两本字段字典 FK/结构四边）；⑤§6/§7 时机矩阵与处置表补三行；⑥depgraph 存在性 SQL 治本（nodes.module_id 列不存在→blueprint_id，原子检查自上线恒 fail-open）；⑦406 条域级占位锚正名（MOD-FACTOR→MOD-L02-001 等 7 组）+FCT-SENT-028 inputs FK 修复+字典补 3 字段 | 四方对齐机制升级为全图全库对齐的 Owner 指令；实施细节见收尾报告 |
| 2026-09-15 | 1.6.0 | **十图升级（GOMAP 转正，#ARCH-312）**：①§3 新增图 10 治理运行地图行（module_id/import spec 双轴：机生层与生成器 scan() 重建比对+人工层 mounts/disconnected 路径实存+层位合法+disconnected 必带 note；工具=align_all 第九节，免独立校验器/免 gate，触发率实证后再议）；②计数命名合规清理（#ARCH-ALIGN-NAMING-001）：frontmatter 标题/§3 标题去"九图满贯"改"全图全库对齐"，引言/§3 数量改"现 10 张"动态口径，硬阻断条件行去计数命名；③统一验证命令块更新（align_all 加第九节图 10） | Owner 2026-09-15 放行 GOMAP 转正为全景图体系图 10（battle_map 定位措辞同步升级，语义与机制零变更）；实施细节见收尾报告 |
| 2026-09-19 | —（§11 节增；frontmatter 版本/日期行按“只增节不改行”约束未动，下次全量修订时一并升版） | 新增 §11 全景图唯一性裁定（Owner 2026-09-19） | W4-5 TDM 唯一地图裁定落地（final3 战役）；裁定号补登归 00_master_directive §X-0 裁定登记批 |

## 11. 全景图唯一性裁定（Owner 2026-09-19）

> 裁定来源：Owner 2026-09-19 终裁（final3 战役 `00_master_directive.md` §W4-5）；裁定号待该指令 §X-0 裁定登记批补登，本节为对齐真源侧落地。本节只增不改——§3 既有行（含图 3 decisiongraph 行）维持原文，状态以本节为准。

| # | 裁定内容 | 落地含义 |
|---|---|---|
| 1 | **TDM=交易决策流程唯一地图**：`config/trading_decision_map.yaml` 是交易决策流程类全景图的唯一真源，**禁建第二张流程类全景图**（流程类新图提案一律违裁；与 D38“新图必挂总线”/§4.6 原则 6 的准入面叠加执行） | 新图准入双重口径：非流程类新图仍走 §3 登记+depgraph 挂轴；流程类=本条直接禁止 |
| 2 | **decisiongraph 半下岗**：图 3（decisiongraph，PG decision_* 3 表）保留 schema 与对齐通道（§3 行、三图对齐检测不变），不扩容；decision_* 表组**列入季度退役审计观察名单**（跟踪载体=本节，首观察窗 2026-Q4，按宪法 §4.2 季度退役审计以触发率/消费方实测判定，禁凭记忆判定）；退役处置=Owner 门位 | 半下岗≠删除：未经裁定禁清理 decision_* 表组或跳过其对齐通道 |
| 3 | **“10 层决策架构+PDF 模型族”防幻觉锚点**：遗产对话**未立项**，仅部分吸收——禁任何会话声称“十层架构已建/在建”。承接件=W4-7 差距表（`docs/_working/archive/2026-09/final3_campaign/w4_7_tdm_absorption_gap.md`，commit b7aeaa39f2）：15 决策点三态对照完成，4 条接线（差距表“形态不符”四行 UP-2/UP-3/UP-4/UP-5 升级件已建成待接线）**待 Max 复验后施工** | 幻觉红线：超出 w4_7 差距表记载的“已建成”外推一律无效；接线施工前必过 Max 复验门 |
