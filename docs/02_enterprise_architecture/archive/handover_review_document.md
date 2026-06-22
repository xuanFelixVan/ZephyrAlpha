# 项目架构交接审查文档

> **文档性质**：交接审查文档，供Claude全项目审查使用
> **创建时间**：2026-06-21
> **当前阶段**：STEP 3（物理路径对齐）已完成，待重新生成depgraph
> **前置条件**：STEP 1（骨架评估）✓ + STEP 2（物理路径对齐检查）✓

---

## 一、项目背景与目标

### 1.1 项目概况

ZephyrAlpha是一个AI驱动的量化交易系统，正在经历**架构级大更新**，目标是支撑**1500个模块容量**。

### 1.2 核心目标

| # | 目标 | 说明 |
|---|------|------|
| 1 | 支撑1500模块容量 | 从原有架构升级到39域方案，每域可独立扩展 |
| 2 | 数据库全景图作为项目蓝图 | depgraph.db是SSoT（唯一真源），包含所有文件夹、文件、功能域的依赖关系和架构关系 |
| 3 | 物理目录对齐全景图设计 | 实际目录结构按照DB全景图的ssot_path设计去修改和搬家 |
| 4 | 生成器对齐实际目录和DB | 修改生成器代码，使其正确反映实际目录结构和DB全景图 |
| 5 | 抽屉式扩展能力 | 未来功能域可像抽屉一样增加，不影响现有架构 |

### 1.3 第一性原理执行顺序

```
STEP 1: ✓ 确认运营态设计是"好的"（骨架评估）
  - 39域容量够用 ✓
  - 路径规范统一 ✓
  - 抽屉式扩展能力 ✓
  - 骨架扫描全部合格 ✓
  - 根目录清理完成 ✓
  - 空目录清理完成 ✓

STEP 2: ✓ 检查所有物理路径是否对齐DB设计
  - production节点804个，物理文件100%对齐 ✓
  - 修复90个路径问题（规则YAML/infra/layers前缀等）✓
  - 剩余"不匹配"均为正常现象（设计态逻辑路径+跨域文件）✓

STEP 3: → 重新生成depgraph，让prototype节点对齐物理文件
  - 物理文件对齐DB（production）已完成 ✓
  - 待做：重新生成depgraph（prototype节点自动派生）
  - 待做：全景图36项检查连续两次零问题
```

### 1.4 谁对齐谁（关键逻辑）

| 节点类型 | 数量 | 对齐方向 | 状态 |
|---------|:---:|---------|:---:|
| design（设计态） | 8020 | 不需要对齐（逻辑路径） | — |
| production（运营态） | 804 | **物理文件 → 对齐DB** | ✓ 已完成 |
| prototype（原型态） | 5636 | **DB → 对齐物理文件**（生成器派生） | 待重新生成 |

---

## 二、当前项目状态

### 2.1 depgraph.db 基本统计

| 指标 | 数值 |
|------|:---:|
| 节点总数 | 14,459 |
| 边总数 | 22,697 |
| 域总数 | 39 |
| design节点 | 8,020 |
| production节点 | 804 |
| prototype节点 | 5,635 |

> 注（2026-06-21 外部审查后修正）：原记录14,460/prototype 5,636为审查前值。审查中删除market_data/__init__.py的1个重复prototype节点（保留production），故prototype 5,636→5,635、节点总数14,460→14,459。重新生成depgraph后prototype节点将按物理文件重新派生，此数字会再次刷新。

### 2.2 39域清单

| domain_id | 域名 | ssot_path | build_status | 模块数 |
|---|---|---|---|:---:|
| D-ALT_DATA | 另类数据 | src/zephyr/alt_data/ | production | 68 |
| D-AUTONOMY_CORE | 自治核心 | src/zephyr/autonomy_core/ | production | 650 |
| D-AUTONOMY_PERM | 自治保护 | src/zephyr/autonomy_perm/ | production | 206 |
| D-BACKTEST | 回测 | src/zephyr/backtest/ | unbuilt | 9 |
| D-COMPLIANCE | 合规 | src/zephyr/compliance/ | production | 916 |
| D-CROSS_ASSET | 跨资产 | src/zephyr/cross_asset/ | unbuilt | 79 |
| D-DATA_ENG | 数据工程 | src/zephyr/data_eng/ | production | 147 |
| D-DATA_GOV | 数据治理 | src/zephyr/data_governance/ | production | 38 |
| D-DATA_SEC | 数据安全 | src/zephyr/data_security/ | production | 30 |
| D-DIGITAL_TWIN | 数字孪生 | src/zephyr/digital_twin/ | unbuilt | 13 |
| D-EXEC_SIM | 执行仿真 | src/zephyr/execution_simulation/ | unbuilt | 8 |
| D-EX_CORE | 执行核心 | src/zephyr/ex_core/ | production | 134 |
| D-EX_SOR | 执行路由 | src/zephyr/ex_sor/ | production | 131 |
| D-FACTOR | 因子 | src/zephyr/factor/ | production | 319 |
| D-FRONTEND | 前端 | src/zephyr/frontend/ | production | 237 |
| D-GOVERNANCE | 治理 | src/zephyr/governance/ | production | 4643 |
| D-INFRA_RUNTIME | 运行时基础设施 | src/zephyr/infrastructure/ | production | 726 |
| D-INFRA_OPS | 基础设施运维 | src/zephyr/infra_ops/ | unbuilt | 404 |
| D-INTEGRATION | 集成 | src/zephyr/integration/ | production | 704 |
| D-INTELLIGENCE | 智能 | src/zephyr/intelligence/ | production | 272 |
| D-KNOWLEDGE | 知识 | src/zephyr/knowledge/ | production | 160 |
| D-MKT_DATA | 行情数据 | src/zephyr/market_data/ | production | 265 |
| D-ML_SERVE | 推理 | src/zephyr/ml_serve/ | production | 69 |
| D-ML_TRAIN | 训练 | src/zephyr/ml_train/ | production | 118 |
| D-OPS | 运维 | src/zephyr/ops/ | production | 634 |
| D-PF_ALLOC | 组合分配 | src/zephyr/pf_alloc/ | unbuilt | 112 |
| D-PF_CORE | 组合核心 | src/zephyr/pf_core/ | production | 203 |
| D-POSITION | 仓位管理 | src/zephyr/position/ | production | 76 |
| D-REPORTING | 报告 | src/zephyr/reporting/ | production | 132 |
| D-RISK | 风控 | src/zephyr/risk/ | production | 774 |
| D-SECURITY | 安全 | src/zephyr/security/ | production | 909 |
| D-SELL_DECISION | 卖出决策 | src/zephyr/sell_decision/ | production | 64 |
| D-SHARED | 共享基础 | src/zephyr/shared/ | production | 289 |
| D-SIGNAL | 信号 | (空) | design_only | 476 |
| D-SIGNAL_ASHARE | A股特色信号 | src/zephyr/signal_ashare/ | production | 27 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | src/zephyr/signal_fundamental/ | production | 24 |
| D-SIGNAL_QUALITY | 信号质量 | src/zephyr/signal_quality/ | production | 18 |
| D-SIMULATION | 仿真 | src/zephyr/simulation/ | unbuilt | 128 |
| D-TRADING | 交易运营 | src/zephyr/trading/ | production | 249 |

### 2.3 production节点对齐状态

| 指标 | 数值 | 状态 |
|------|:---:|:---:|
| production节点总数 | 804 | — |
| 有path的节点 | 804 | — |
| 物理文件存在 | 804 | ✓ 100%对齐 |
| 物理文件缺失 | 0 | ✓ |

---

## 三、相关文档链接

### 3.1 核心规则文档（必读）

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目规则(L0) | [project_rules.md](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) | 项目硬规则，AI行为铁律 |
| 入职细则(L1) | [onboarding_detail.md](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md) | L0的详细补充，施工指导 |
| AGENTS.md | [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) | AI代理配置 |

### 3.2 架构文档 — 必读（6个）

> Claude审查前必须读完以下6个文档，理解项目背景、架构演变和当前状态。

| # | 文档 | 路径 | 必读原因 |
|:---:|------|------|------|
| 1 | 全景图能力定位书 | [依赖与架构全景图能力定位书.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/依赖与架构全景图能力定位书.md) | **定义depgraph.db的能力定位、设计决策和裁定记录**。Claude必须理解全景图是什么、解决什么问题、边界在哪里。V5.8版本，包含依赖全景图+架构全景图合并说明。 |
| 2 | 域归并映射报告 | [域归并映射报告.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/域归并映射报告.md) | **记录52域→39域的归并映射**。Claude需要理解域结构演变历史：12个域合并到父域+1个域删除。任务卡DM-100255，源文档architecture_upgrade_discussion.md §17.6。 |
| 3 | 架构升级讨论 | [architecture_upgrade_discussion.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md) | **架构升级项目的导航图**。包含项目背景、架构设计上下文、重大决策、进展追踪、方法论。V2.6.0，记录了阶段0-7的完整执行状态。 |
| 4 | 待决策架构决策 | [architecture_decisions_pending.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_decisions_pending.md) | **T6/T7/T17等待Owner审批的决策**。Claude需要知道哪些决策待审批，审查时不能擅自决策。 |
| 5 | 搬家方案备忘录 | [phase5_migration_plan.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/phase5_migration_plan.md) | **P0-P3搬家操作计划（已执行）**。记录了所有搬家操作的详细清单：删除shim目录、ssot_path更新、跨域搬家、大域改名。 |
| 6 | 目录索引 | [index.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/index.md) | **02_enterprise_architecture目录的导航索引**。GOV-036，V2.1.0，包含双轨制规则、子目录一览。 |

### 3.3 架构文档 — 可选读（4个）

> 以下文档与审查相关但非必须，Claude可按需查阅。

| # | 文档 | 路径 | 可选读原因 |
|:---:|------|------|------|
| 7 | 治理收敛计划 | [governance_convergence_plan.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/governance_convergence_plan.md) | 阶段7b治理收敛工作内容。P0工作项（修复severity_types.py等）与当前审查相关，但已执行完毕。 |
| 8 | SSoT权威映射 | [ssot_authority_map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/ssot_authority_map.md) | 定义跨文件受保护字段的权威来源。V2.6.0，validate_ssot.py的校验规则配置。 |
| 9 | 迁移注册表 | [migration_registry.yaml](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/migration_registry.yaml) | 历史迁移操作记录（YAML格式）。记录了D-DATA等域的文件迁移。 |
| 10 | AI团队模式配置 | [AI团队模式完整配置.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/AI团队模式完整配置.md) | AI团队10模式配置V3.5。与审查工作本身相关（Claude是Guard Review），但与架构审查关系不大。 |

### 3.4 不需要读的文档（5个）

> 以下文档与当前架构审查无关，Claude不需要读。

| # | 文档 | 路径 | 不需要读原因 |
|:---:|------|------|------|
| 11 | 蓝图效能回顾报告 | [blueprint_effectiveness_report.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/blueprint_effectiveness_report.md) | 历史报告，对标Codified Context的回顾，与当前搬家审查无关。 |
| 12 | 阶段E规则格式升级 | [phase_e_rule_format_upgrade_proposal.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/archive/phase_e_rule_format_upgrade_proposal.md) | 已归档。规则文件MD→YAML格式升级方案，核心任务已完成（53个YAML已创建），项目数字已过时。 |
| 13 | 阶段F YAML优化 | [phase_f_yaml_rule_optimization_proposal.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/archive/phase_f_yaml_rule_optimization_proposal.md) | 已归档。YAML规则文件优化方案，修复方案A/B已执行完成，项目数字已过时。 |
| 14 | 规则文件审查指令 | [rule_file_audit_19ai_split.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/rule_file_audit_19ai_split.md) | 19AI并发审查53个trae_XXX.yaml的指令集，与架构搬家无关。 |
| 15 | 交接文档本身 | [handover_review_document.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/handover_review_document.md) | 本文档，Claude正在读。 |

### 3.5 关键脚本

| 脚本 | 路径 | 说明 |
|------|------|------|
| depgraph生成器 | [generate_project_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py) | 生成依赖图（⚠️架构升级期间慎用） |
| depgraph提取器 | [extract_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/extract_depgraph.py) | 提取依赖图摘要（安全，只读） |
| 全景图检查脚本 | [_panorama_full_check.py](file:///d:/ZephyrAlpha/scripts/_panorama_full_check.py) | 38项全景图检查 |
| 注册审计 | [audit_registration.py](file:///d:/ZephyrAlpha/scripts/governance/audit_registration.py) | 孤儿检测 |
| 关键导入验证 | [verify_key_imports.py](file:///d:/ZephyrAlpha/scripts/governance/verify_key_imports.py) | 关键模块导入测试 |

### 3.6 数据库

| 文件 | 路径 | 说明 |
|------|------|------|
| depgraph.db | [depgraph.db](file:///d:/ZephyrAlpha/data/databases/depgraph.db) | 依赖图+全景图唯一真源 |
| 备份目录 | [data/databases/](file:///d:/ZephyrAlpha/data/databases) | 多个历史备份 |

---

## 四、已执行的工作记录

### 4.1 STEP 1：骨架评估（已完成）

| 工作项 | 状态 | 说明 |
|--------|:---:|------|
| 39域容量评估 | ✓ | 所有域容量够用 |
| 路径规范统一 | ✓ | ssot_path全部指向src/zephyr/xxx/ |
| 骨架扫描 | ✓ | 根目录11个顶级目录+src/zephyr/40域+docs/6目录+tests/22目录全部合格 |
| 根目录清理 | ✓ | 删除13个垃圾文件，移动/删除8个冗余目录 |
| 空目录清理 | ✓ | 清理11,692个空目录 |
| 遗留问题4修复 | ✓ | D-INFRA_RUNTIME→D-INFRA_RUNTIME，D-SIGNAL→design_only |

### 4.2 STEP 2：物理路径对齐检查（已完成）

| 工作项 | 状态 | 修复数量 | 说明 |
|--------|:---:|:---:|------|
| 问题A：规则YAML路径 | ✓ | 53 | trae_001.yaml → trae_001_file_operation_security.yaml |
| 问题B：infra/路径 | ✓ | 3 | infra/ → config/infra/ |
| 问题C：设计态旧路径 | ✓ | 20 | design/前缀、portfolio_allocation→pf_alloc等 |
| 问题D：运营态路径 | ✓ | 1 | src/zephyr/data/ → src/zephyr/market_data/ |
| 问题E：layers层级前缀 | ✓ | 14 | infrastructure.yaml → l01_infrastructure.yaml |
| **合计修复** | ✓ | **91** | — |

### 4.3 P0-P3搬家操作（已执行）

| 阶段 | 操作 | 文件数 | 状态 |
|------|------|:---:|:---:|
| P0 | 删除3个shim目录（execution_core/portfolio_core/portfolio_allocation） | 3目录 | ✓ |
| P0 | 简单改名3个目录（alternative_data/data_engineering/execution_router） | 21文件 | ✓ |
| P1 | 18个域ssot_path更新 | 0（仅DB） | ✓ |
| P2 | 跨域搬家（observability→ops/、signal→signal_fundamental/） | 36文件 | ✓ |
| P3 | 大域改名（infra_runtime→infrastructure） | 428文件+619引用 | ✓ |

### 4.4 DB备份记录

| 备份文件 | 说明 |
|---------|------|
| depgraph_legacy_fix_20260621_131728.db | 遗留问题修复前 |
| depgraph_legacy_fix_20260621_131813.db | 遗留问题修复前 |
| depgraph_path_fix_20260621_133706.db | 路径修复A/B前 |
| depgraph_cd_fix_20260621_133827.db | 路径修复C/D前 |
| depgraph_layers_fix_20260621.db | layers前缀修复前 |

---

## 五、Claude审查清单

### 5.0 前置阅读（必须完成）

> Claude审查前必须先读完以下文档，建立项目背景理解。

- [ ] **阅读3.1核心规则文档**（3个）：project_rules.md、onboarding_detail.md、AGENTS.md
- [ ] **阅读3.2必读架构文档**（6个）：
  - [ ] 依赖与架构全景图能力定位书.md（理解全景图是什么、边界在哪里）
  - [ ] 域归并映射报告.md（理解52域→39域的归并历史）
  - [ ] architecture_upgrade_discussion.md（理解架构升级项目导航）
  - [ ] architecture_decisions_pending.md（理解T6/T7/T17待审批决策）
  - [ ] phase5_migration_plan.md（理解P0-P3搬家操作计划）
  - [ ] index.md（理解目录结构）

**阅读完成后确认**：
- [ ] 理解depgraph.db是项目蓝图（SSoT），包含依赖关系+架构位置
- [ ] 理解39域方案是52域归并后的结果（12域合并+1域删除）
- [ ] 理解design/production/prototype三种design_maturity的区别
- [ ] 理解"物理文件对齐DB"（production）vs "DB对齐物理文件"（prototype）的方向性
- [ ] 理解P0-P3搬家操作已全部执行完毕
- [ ] 理解T6/T7/T17是待Owner审批的决策，审查时不能擅自决策

### 5.1 审查目标

确认以下结论是否正确：
1. **production节点804个，物理文件100%对齐** — 所有production节点的path指向的物理文件都存在
2. **39域ssot_path物理目录全部存在** — 38个代码域目录存在，1个design_only域（D-SIGNAL）无ssot_path
3. **物理文件对齐DB工作已完成** — 不需要再搬家任何物理文件
4. **可以重新生成depgraph** — 让prototype节点（5636个）与物理文件对齐

### 5.2 审查项清单

#### A. DB完整性审查

- [ ] **A1**: 验证depgraph.db节点总数=14,460
- [ ] **A2**: 验证depgraph.db边总数=22,697
- [ ] **A3**: 验证depgraph.db域总数=39
- [ ] **A4**: 验证design_maturity分布：design=8020, production=804, prototype=5636
- [ ] **A5**: 验证所有域的ssot_path格式正确（src/zephyr/xxx/ 或 空）

**验证命令**：
```bash
python scripts/governance/extract_depgraph.py --summary
```

#### B. production节点对齐审查（核心）

- [ ] **B1**: 验证804个production节点全部有path
- [ ] **B2**: 验证804个production节点的path指向的物理文件全部存在
- [ ] **B3**: 抽样检查10个production节点的path是否合理（在对应域的ssot_path下或跨域文件）
- [ ] **B4**: 检查是否有production节点的path指向不存在的文件

**验证方法**：编写脚本查询所有production节点的path，检查物理文件存在性

#### C. 域目录对齐审查

- [ ] **C1**: 验证38个代码域的ssot_path物理目录全部存在
- [ ] **C2**: 验证D-SIGNAL域是design_only（ssot_path为空，476设计态节点）
- [ ] **C3**: 抽样检查5个域的物理目录结构是否合理

**验证方法**：编写脚本检查每个域的ssot_path物理目录存在性

#### D. 跨域文件审查

- [ ] **D1**: 确认254个运营态跨域文件（path不在ssot_path下）是正常现象
- [ ] **D2**: 确认这些跨域文件通过[DOMAIN]字段覆盖路径派生的domain_id
- [ ] **D3**: 抽样检查10个跨域文件的[DOMAIN]字段是否正确

**验证方法**：查询254个跨域文件，检查其[DOMAIN]字段

#### E. 设计态节点审查

- [ ] **E1**: 确认867个设计态path不匹配是正常现象（逻辑路径+蓝图文档）
- [ ] **E2**: 确认29个空path设计态节点是正常现象（AGG-002/A-001/MS-02等逻辑聚合节点）
- [ ] **E3**: 确认7221个逻辑路径（如"数据域-L0数据接入/D-DATA-67"）是设计态标识符，非文件系统路径

**验证方法**：查询设计态节点的path分布，确认逻辑路径占比

#### F. 生成器安全性审查

- [ ] **F1**: 确认生成器的G1修复（load_design_state_from_db）正常工作
- [ ] **F2**: 确认生成器的双态保护（DELETE FROM nodes WHERE design_maturity != 'design'）
- [ ] **F3**: 确认生成器的merge_design_fields()只在lifecycle=='design'时合并保留旧字段
- [ ] **F4**: 确认重新生成depgraph不会丢失production节点的手动维护元数据

**验证方法**：阅读generate_project_depgraph.py源码，确认保护机制

#### G. 全景图检查

- [ ] **G1**: 运行_panorama_full_check.py，确认36/36 PASS
- [ ] **G2**: 如有问题，记录问题清单

**验证命令**：
```bash
python scripts/_panorama_full_check.py
```

### 5.3 审查结论模板

Claude审查完成后，请输出以下结论：

```
## 审查结论

### 0. 前置阅读
- 核心规则文档(3个): [已读/未读]
- 必读架构文档(6个): [已读/未读]
- 背景理解确认: [是/否]

### A. DB完整性
- 节点总数: [确认/不符] (期望: 14,460)
- 边总数: [确认/不符] (期望: 22,697)
- 域总数: [确认/不符] (期望: 39)

### B. production节点对齐
- production节点数: [确认/不符] (期望: 804)
- 物理文件存在: [确认/不符] (期望: 804)
- 物理文件缺失: [确认/不符] (期望: 0)

### C. 域目录对齐
- 代码域目录存在: [确认/不符] (期望: 38)
- design_only域: [确认/不符] (期望: D-SIGNAL)

### D. 跨域文件
- 跨域文件数: [确认/不符] (期望: 254)
- 是否正常现象: [是/否]

### E. 设计态节点
- path不匹配数: [确认/不符] (期望: 867)
- 空path节点数: [确认/不符] (期望: 29)
- 是否正常现象: [是/否]

### F. 生成器安全性
- G1修复: [确认/不符]
- 双态保护: [确认/不符]
- production保护: [确认/不符]

### G. 全景图检查
- 检查结果: [PASS数]/36
- 问题数: [N]

### 最终结论
[ ] 所有审查项通过，可以重新生成depgraph
[ ] 存在问题，需要修复后再重新生成
```

---

## 六、下一步工作

### 6.1 待Claude审查确认后执行

| 步骤 | 操作 | 命令 | 风险 |
|------|------|------|:---:|
| 1 | 备份depgraph.db | `copy depgraph.db depgraph_pre_regen_20260621.db` | 🟢 |
| 2 | 重新生成depgraph | `python scripts/governance/generate_project_depgraph.py --max-workers 8` | 🟡 |
| 3 | 全景图检查 | `python scripts/_panorama_full_check.py` | 🟢 |
| 4 | 关键导入验证 | `python scripts/governance/verify_key_imports.py` | 🟢 |
| 5 | 注册审计 | `python scripts/governance/audit_registration.py` | 🟢 |
| 6 | 连续两次零问题确认 | 重复步骤3-5 | 🟢 |

### 6.2 重新生成depgraph的安全性说明

| 保护机制 | 说明 |
|---------|------|
| G1修复 | `load_design_state_from_db()` 从DB加载design节点，不会被覆盖 |
| 双态保护 | `DELETE FROM nodes WHERE design_maturity != 'design'` 只删除非design节点 |
| production保护 | production节点从DB加载，不会被覆盖（与design同等待遇） |
| prototype自动派生 | 5636个prototype节点根据物理文件重新生成，更新path |
| domains表保护 | 无DELETE操作，ssot_path不会被覆盖 |

**预期变化**：
- design节点（8020个）：不变
- production节点（804个）：不变
- prototype节点（5636个）：path更新为物理文件实际路径
- 节点总数可能变化（新增物理文件/删除不存在的文件）

### 6.3 重新生成后的验证标准

| 验证项 | 通过标准 |
|--------|---------|
| 全景图检查 | 36/36 PASS，连续两次零问题 |
| production节点 | 804个全部保留，path不变 |
| design节点 | 8020个全部保留 |
| prototype节点 | path与物理文件对齐 |
| 关键导入 | verify_key_imports.py exit 0 |
| 注册审计 | audit_registration.py exit 0（CLEAN） |

---

## 七、注意事项

### 7.1 架构升级期间禁止事项

| 禁止操作 | 原因 |
|---------|------|
| 禁止直接修改depgraph.db的design节点 | 设计态是真源，手动维护 |
| 禁止直接修改depgraph.db的production节点 | 运营态是手动维护元数据 |
| 禁止跳过G1修复运行生成器 | 会覆盖design节点 |
| 禁止跳过双态保护运行生成器 | 会删除design节点 |

### 7.2 重新生成depgraph的前提条件

1. ✓ STEP 1骨架评估完成
2. ✓ STEP 2物理路径对齐检查完成
3. ✓ production节点804个100%对齐
4. ✓ 39域ssot_path物理目录全部存在
5. ⏳ Claude审查确认上述结论

### 7.3 如果审查发现问题

- 记录问题清单
- 修复问题
- 重新审查
- 连续两次零问题后再重新生成depgraph

---

## 八、项目架构骨架现状

### 8.1 根目录顶级结构（11个）

```
d:\ZephyrAlpha\
├── .trae/              # Trae IDE配置
├── AGENTS.md           # AI代理配置
├── CLAUDE.md           # Claude配置
├── README.md           # 项目说明
├── agent_spec/         # 代理规格（已迁移到data/capability_cards/）
├── config/             # 配置文件
├── data/               # 数据文件
├── docs/               # 文档
├── scripts/            # 脚本
├── src/                # 源代码
└── tests/              # 测试
```

### 8.2 src/zephyr/域结构（40个域目录）

所有39个代码域的ssot_path都指向src/zephyr/xxx/，物理目录全部存在。

### 8.3 骨架评估结论

- 根目录11个顶级目录：合格 ✓
- src/zephyr/40个域目录：合格 ✓
- docs/6个目录：合格 ✓
- tests/22个目录：合格 ✓
- 抽屉式扩展能力：具备 ✓

---

## 九、文档维护

- **创建者**：GLM-5.2（Trae IDE）
- **审查者**：Claude（待审查）
- **文档位置**：[handover_review_document.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/handover_review_document.md)
- **文档性质**：临时交接文档，审查完成后可归档或删除
