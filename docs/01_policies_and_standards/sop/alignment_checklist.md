---
ttl: permanent
doc_type: policy
rule_form: checklist
verifiability: manual
title: 全项目对齐清单——六图+注册表+代码文档三层对齐规则
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-31
topic: full_project_alignment_checklist
scope: global
depends_on:
  - construction_workflow_sop
  - document_review_and_optimization_sop
  - trae_080_panorama_alignment
related_issues: []
related_modules:
  - scripts/governance/d5_architecture/generators/align_all.py
  - scripts/governance/d5_architecture/generators/align_panoramas.py
  - src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py
---

# 全项目对齐清单——六图+注册表+代码文档三层对齐规则

> 本清单是 **全项目对齐** 的**资产清单层真源**，列出"要对齐哪些东西、每个东西的对齐规则、用什么工具、不一致怎么办"。
> **性质**：清单层，只列对齐对象+规则+工具+处置，不编排流程。流程见 [construction_workflow_sop](construction_workflow_sop.md)（施工 SOP，管"什么时候对齐、怎么对齐"）。
> **适用范围**：**全项目所有模块/前端/文档/注册表**，不限于 07 域。新 AI 进项目必读。
> **管理规范**：[01_design_memo_management_spec](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/01_design_memo_management_spec.md)。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G06 全项目对齐清单 |
| 创建 | 2026-08-31 |
| 优先级 | P0（所有施工的前置依赖） |
| 状态 | active v1.0.0 |
| 上游 | [construction_workflow_sop](construction_workflow_sop.md)（施工流程）、[trae_080_panorama_alignment](../rules/trae_080_panorama_alignment.yaml)（五图对齐铁律） |
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

- **三层分类**：六图（第一层）+ 注册表（第二层）+ 代码文档（第三层），每层列出全量对象+对齐规则
- **每个对象四要素**：对齐对象（和什么对齐）/ 对齐时机（什么时候检查）/ 对齐工具（用什么脚本/门禁）/ 失败处置（不一致怎么办）
- **新 AI 入口**：本文档列入 [construction_workflow_sop](construction_workflow_sop.md) Step 0 必看文件清单，新 AI 冷启动时强制加载

## 3. 第一层：六图对齐

> 六图=五图（depgraph/dataflowgraph/decisiongraph/blueprint/battle_map）+ frontend_map（前端全景图，待建）

| 图名 | 真源 | 对齐 key | 对齐规则 | 对齐时机 | 对齐工具 | 失败处置 |
|---|---|---|---|---|---|---|
| **depgraph**（依赖全景图） | PostgreSQL `dep_` 表组 | module_id | 模块间 import 关系必须与代码实际 import 一致 | commit 前 / 新模块注册时 | [apply_depgraph.py](../../../scripts/governance/apply_depgraph.py) | 孤儿模块→阻断 commit |
| **dataflowgraph**（数据流全景图） | PostgreSQL 3 表 | module_id | 数据流 job 必须与代码实际 dataflow 一致 | commit 前 / sync 时 | [sync_panorama_module.py](../../../scripts/governance/sync_panorama_module.py)（单向派生） | 派生失败→阻断 |
| **decisiongraph**（决策流全景图） | PostgreSQL 3 表 | module_id | decision_layer 必须与代码实际决策路径一致 | commit 前 / sync 时 | sync_panorama_module.py（单向派生） | 派生失败→阻断 |
| **blueprint.md**（蓝图） | MD frontmatter | module_id | frontmatter 4 字段（module_id/responsibility_domain/design_maturity/build_status）必须与 depgraph 一致 | commit 前 / sync 时 | sync_panorama_module.py（单向派生） | frontmatter 漂移→warn |
| **battle_map**（作战地图） | PostgreSQL 3 表（battle_map_steps/anchors/edges） | step_id | BM-XXX 环节必须与前四图双向校验 | commit 前 / 改动涉及 BM 环节时 | [generate_battle_map_diagram.py](../../../scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py) | ghost_anchors>0→阻断 |
| **frontend_map**（前端全景图，待建） | architecture_model/frontend/frontend_map.yaml（git YAML 真源）+ governance.db 派生副本 | feature_id（F-页面-名） | 前端功能必须挂 backend_ref 到模块注册表；模块必须声明 has_frontend | commit 前 / 新前端功能上线时 | 待建（扩展 panorama_alignment_gate） | frontend_ref 空→阻断 |

**六图统一验证命令**：
```powershell
python scripts/governance/d5_architecture/generators/align_all.py  # 五图对齐（现有）
# frontend_map 对齐（待建，扩展 align_all 或 panorama_alignment_gate）
```

**硬阻断条件**：domain_mismatches>0 / ghost_anchors>0 / frontend_ref 悬空（frontend_map 建成后）

## 4. 第二层：注册表对齐

> 40+ 注册表全量清单见 [registry_master_index.yaml](../_registry/catalogs/registry_master_index.yaml)，此处按域分组列出对齐规则

### 4.1 业务资产库（6 个）

| 注册表 | 对齐对象 | 对齐规则 | 对齐时机 | 对齐工具 |
|---|---|---|---|---|
| **factor_registry**（因子库） | depgraph / blueprint | 因子模块必须登记 depgraph + 蓝图 frontmatter 一致 | 新因子注册时 | 门禁（待建） |
| **strategy_registry**（策略库） | depgraph / blueprint / battle_map | 策略模块必须登记 depgraph + 挂 BM-XXX 环节 | 新策略注册时 | 门禁（待建） |
| **technical_indicator_registry**（技术指标库） | depgraph / blueprint | 指标模块必须登记 depgraph | 新指标注册时 | 门禁（待建） |
| **chart_pattern_registry**（图形形态库） | depgraph / blueprint | 形态识别模块必须登记 depgraph | 新形态注册时 | 门禁（待建） |
| **portfolio_model_registry**（组合模型库） | depgraph / blueprint | 组合模型必须登记 depgraph | 新模型注册时 | 门禁（待建） |
| **risk_limit_registry**（风险限额库） | depgraph / blueprint / config | 限额配置必须与风控模块一致 | 限额变更时 | 门禁（待建） |

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
| **rule_catalog_registry**（规则目录库） | 实际规则文件 | 规则文件必须在目录登记 | 新规则创建时 | 既有门禁 |
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

**注册表对齐统一原则**：
1. **新建必须登记**：任何新模块/因子/策略/指标/能力/规则/门禁，必须在对应注册表登记，否则门禁拦截
2. **转正必须迁移**：候选池（CAND）转正时必须从 candidate_module_registry 移到正式库
3. **变更必须同步**：注册表内容变更时，必须同步到依赖它的全景图/其他注册表
4. **删除必须清理**：注册表条目删除时，必须清理全景图/其他注册表的引用

## 5. 第三层：代码↔文档↔测试对齐

| 对齐关系 | 对齐规则 | 对齐时机 | 对齐工具 | 失败处置 |
|---|---|---|---|---|
| **代码 → 蓝图** | 模块代码必须与 blueprint.md 描述的接口/状态机/依赖一致 | commit 前 / 文档审查时 | blueprint_frontmatter_reconciler（post-commit） | 不一致→阻断或 warn |
| **代码 → 设计备忘** | 代码实现必须与 design_memo 决策一致 | 文档审查时 | document_review_and_optimization_sop 第 2 轮 | 不一致→回填或修代码 |
| **代码 → 测试** | 模块代码必须有对应测试文件（tests/ 下） | commit 前 | test_residue_reclaim reconciler | 缺测试→warn |
| **文档 → 代码** | 文档引用的代码路径/接口必须真实存在 | 文档审查时 | document_review_and_optimization_sop 第 2 轮事实核验 | 引用失效→修正文档 |
| **测试 → 代码** | 测试用例必须覆盖代码实际功能 | commit 前 | pytest-cov（可选） | 覆盖率过低→warn |
| **前端 → 后端** | 前端功能必须挂 backend_ref 到模块注册表（frontend_map 建成后） | commit 前 | 待建 frontend 门禁 | backend_ref 空→阻断 |
| **后端 → 前端** | 后端模块必须声明 has_frontend（frontend_map 建成后） | 新模块注册时 | 待建 frontend 门禁 | has_frontend 空→阻断 |

## 6. 对齐时机矩阵

| 时机 | 触发条件 | 必须对齐的对象 | 工具 |
|---|---|---|---|
| **commit 前** | 任何 commit | 六图（如触及模块/依赖/路径/蓝图/前端）+ 相关注册表 | panorama_alignment_gate + GitCommitGateway |
| **新模块注册时** | 新建模块 | depgraph + blueprint + capability_canonical_file_registry + module_translation_registry + （涉前端时）frontend_map | 门禁强制 |
| **CAND 转正时** | 候选池转正式 | candidate_module_registry → capability_canonical_file_registry + depgraph + （涉前端时）frontend_map | 门禁强制 |
| **新前端功能上线时** | 前端新功能 commit | frontend_map + 验收单 + backend_ref 挂载 | 待建 frontend 门禁 |
| **文档审查时** | 按 document_review_and_optimization_sop 七轮流程 | 代码↔文档↔测试 | document_review_and_optimization_sop |
| **新 AI 冷启动时** | 新 AI session 开始 | 必读本清单 + construction_workflow_sop + frontend_handbook（如涉及前端） | construction_workflow_sop Step 0 |

## 7. 不一致处置

| 不一致类型 | 处置 |
|---|---|
| **六图 domain_mismatches>0** | 阻断 commit，回 Step 2 修正 |
| **六图 ghost_anchors>0** | 阻断 commit，清理幽灵锚点 |
| **注册表条目缺失** | 阻断 commit，补登记 |
| **注册表条目漂移**（内容与实际不一致） | warn-only，登记到漂移清单，定期修复 |
| **代码↔文档不一致** | 文档审查时发现→回填文档或修代码 |
| **代码↔测试缺失** | warn-only，登记到测试补全清单 |
| **frontend_ref 悬空**（frontend_map 建成后） | 阻断 commit，挂载 backend_ref 或声明 has_frontend=no+理由 |

## 8. 新 AI 必读清单

新 AI 进项目 MUST 按顺序读完以下三份文件：

1. **本清单**（alignment_checklist.md）——知道要对齐哪些东西
2. **[construction_workflow_sop](construction_workflow_sop.md)**——知道什么时候对齐、怎么对齐
3. **[frontend_handbook](../../../docs/03_modules/_domain_frontend/frontend_handbook/)**（如涉及前端，待建）——知道前端怎么做

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
