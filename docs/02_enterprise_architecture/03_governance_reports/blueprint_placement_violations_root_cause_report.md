---
title: 蓝图物理位置与 belongs_to 归属链违规——病根调研与裁定报告
doc_type: audit_report
status: active
ttl: permanent
created_by: agent
created: '2026-06-26'
approved_by: owner
approved_date: '2026-06-26'
module_id: REG-GOV-PLACEMENT-RCA-001
related_adjudication: '#206 (B 子裁定执行遗漏) + 本次新增裁定 R1-R7'
related_validator: 'validate_blueprint_placement.py (P0-1/P0-2/P0-3/P0-4/P1-1/P1-2)'
---

# 蓝图物理位置与 belongs_to 归属链违规——病根调研与裁定报告

> **文档定位**：`validate_blueprint_placement.py --ci` 报告 11 条 P0 + 11 条 P1 违规（共 22 条），阻塞 CI。这些违规在裁定#206-D 收尾（OPS-2026062646）执行 `validate_blueprint_placement.py --ci` 时暴露，但与 dir_prefix 修改无关（0 条 P0-3），属预先存在的架构债务。本报告作为客观架构师调研，查清病根、对标真源、给出裁定与治本方案。
>
> **用户触发质疑**：用户提出"名字规则我记得好像都必须是小写，并且下划线啊？"——本报告 §2 一并回答此命名规则质疑。
>
> **调研方法**：内部规则真源审计（trae_028 / trae_014 / layer_vocabulary.yaml）+ 校验器源码核对 + 蓝图 frontmatter 实测探针 + #206 既有裁定核对。所有结论附证据（文件:行号 / 量化数据）。

---

## 1. 问题陈述

### 1.1 违规全貌

`validate_blueprint_placement.py --ci` 当前输出（探针实测，见附录 B）：

| 严重级 | 检查项 | 数量 | 含义 |
|---|---|---|---|
| P0-1 | 蓝图缺 belongs_to 字段 | 1 | 违反 PS-STD-005 §6 MUST |
| P0-2 | cross_layer 蓝图不在 _cross_layer/ 下 | 10 | 物理位置与 layer 错位 |
| P0-3 | layer L{NN} 与物理路径不匹配 | 0 | — |
| P0-4 | 域覆盖度漏洞 | 0 | — |
| P1-1 | belongs_to 链不可达金字塔顶点 | 3 | 归属链断裂/自环/循环 |
| P1-2 | belongs_to 指向的目标蓝图不存在 | 8 | 悬空引用 |
| **合计** | | **22** | P0=11 阻塞 CI（exit=1） |

### 1.2 三个核心问题

> **Q1**：蓝图标识符（module_id / blueprint_id）的命名规则到底是什么？是否应为小写+下划线？（用户质疑）
> **Q2**：22 条违规的病根是什么？是数据问题、规则问题、还是校验器问题？
> **Q3**：治本方案是什么？如何分阶段施工且不引入新漂移？

---

## 2. 命名规则真源审计（回答 Q1）

### 2.1 真源定位

项目命名规则唯一真源为 [trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1022-L1074)。各标识符规则：

| 标识符层 | 真源规定 | 证据 |
|---|---|---|
| **domain_id** | `D-XXX_YYY`（大写D+大写域缩写+下划线分隔子域） | [trae_028:1033-1035](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1033-L1035) |
| **module_id** | `MOD-{LAYER}-{SEQ}`（如 MOD-L00-001）或 `D-XXX-{SEQ}` | [trae_028:1036-1039](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1036-L1039) |
| **Level 0 总蓝图 ID** | `SYS-MASTER-NNN`（如 SYS-MASTER-001） | [trae_014:393-397](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L393-L397) |
| **文件名** | 全小写 snake_case；禁 kebab-case/大写（AGENTS.md 白名单除外） | [trae_028:1041-1043](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1041-L1043) |
| **目录名** | 单词或 snake_case（小写+下划线） | [trae_028:1045-1047](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1045-L1047) |

### 2.2 关键边界声明

[trae_028:1064](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1064)：

> "域ID保持大写 D-XXX_YYY 格式（**标识符不是文件名**）；统一使用下划线分隔子域（禁止连字符）"

[trae_028 doc_001 NUM-V02](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L67-L69)：

> "蓝图 frontmatter layer 字段使用域英文名 snake_case"——layer 字段是语义名（data/factor/signal...），不是 L00-L13 编号。

### 2.3 回答 Q1

**否，标识符不是小写+下划线。** 用户"应该是小写"的直觉源于**文件名规则**（snake_case 小写），但标识符层（module_id / domain_id / blueprint_id）另有规则：

- module_id 大写+连字符（MOD-TASK_SYSTEM）是合法格式（[trae_028:1036-1039](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1036-L1039)）
- Level 0 总蓝图 ID 是 `SYS-MASTER-NNN`（大写+连字符，[trae_014:393-397](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L393-L397)）
- "标识符不是文件名"是刻意设计边界（[trae_028:1064](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1064)）

> 此结论与既有裁定 [blueprint_id_naming_root_cause_report.md §5.1 Q1](file:///d:/ZephyrAlpha/docs/_working/blueprint_id_naming_root_cause_report.md)（Owner 已拍板）一致——"否"。

**但** layer 字段是另一回事：layer 应为语义 snake_case 名（factor/signal），不是 L02/L03 编号。详见 §4.4 病根 #4。

---

## 3. 校验器逻辑核对

[validate_blueprint_placement.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py) 检查逻辑（已逐行核对）：

| 检查 | 逻辑 | 关键代码 |
|---|---|---|
| P0-1 | 蓝图 frontmatter 无 belongs_to 字段 | [L131-134](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L131-L134) |
| P0-2 | `layer==cross_layer` 且 `module_id not in KNOWN_LEVEL_01_IDS` 且不在 `_cross_layer/` 下 | [L139-147](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L139-L147) |
| P0-3 | `layer in VALID_LAYERS` 时校验路径含 `dir_prefix` | [L150-166](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L150-L166) |
| P1-1 | belongs_to 链追溯，遇 SYS-MASTER-001 终止，否则断裂/自环/循环 | [L192-215](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L192-L215) |
| P1-2 | belongs_to 目标不在注册蓝图列表 | [L218-220](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L218-L220) |

**关键常量**：
- `KNOWN_LEVEL_01_IDS = {"MOD-MASTER_BLUEPRINT", "SYS-MASTER-001", "DOM-GOV-001"}`（[L138](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L138)）——P0-2 豁免集，按 **frontmatter module_id** 匹配
- `VALID_BELONGS_TO = {"SYS-MASTER-001", "MOD-MASTER_BLUEPRINT", "DOM-GOV-001"}`（[L77](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L77)）
- P1-1 链追溯遇 `SYS-MASTER-001` 即 `break`（[L203](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L203)）——SYS-MASTER-001 是金字塔顶点终止符

---

## 4. 病根分析（回答 Q2）

探针实测 22 条违规分 6 类病根。违规影响数见每类标题。

### 4.1 病根 #1：SYS-MASTER-001 蓝图 module_id 双轨制（8 条违规，核心）

**现象**：金字塔顶点蓝图 [_sys_master/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md) frontmatter `module_id: MOD-073`（[L2](file:///d:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L2)），但全项目按 `SYS-MASTER-001` 引用它。

**证据**：
- frontmatter：`module_id: MOD-073`、`belongs_to: "ROOT"`、`blueprint_level: system`（[L2,L10,L26](file:///d:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L2)）
- 正文自述：`> module_id: SYS-MASTER-001 | blueprint_level: system`（蓝图正文行 61，frontmatter 与正文不一致）
- 真源 [trae_014 §5.1](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L393-L397)：Level 0 总蓝图 ID = `SYS-MASTER-NNN`，example `SYS-MASTER-001`
- 5 个蓝图 belongs_to 指向 SYS-MASTER-001（MOD-ALPHA_SIGNAL_DOMAIN/MOD-GOVERNANCE/MOD-MASTER_BLUEPRINT/MOD-ML_EXPERIMENT_DOMAIN/MOD-INF-035）

**连锁影响**：
- 1× P0-2：MOD-073 不在 KNOWN_LEVEL_01_IDS → cross_layer 错位
- 1× P1-1：MOD-073 → ROOT 链断裂
- 1× P1-2：ROOT 不在注册列表
- 5× P1-2：SYS-MASTER-001 不在注册列表（因注册名是 MOD-073）

**病根**：蓝图 frontmatter module_id 与项目约定 ID 不一致（双轨制）。校验器按 frontmatter module_id 注册，找不到 SYS-MASTER-001。这是 [blueprint_registry.yaml 变更历史](file:///d:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L1005-L1015) 记录的"新增 MOD-073 → _sys_master/blueprint.md"引入的——registry 用 MOD-073，但蓝图正文与引用方用 SYS-MASTER-001。

### 4.2 病根 #2：SYS-MASTER-001 belongs_to=ROOT 非法（含于病根 #1）

**现象**：`belongs_to: "ROOT"`（[L26](file:///d:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md#L26)）。

**真源**：[trae_014 §6.1 belongs_to_values](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L504-L516) 合法值仅 `MOD-MASTER_BLUEPRINT`/`MOD-DOMAIN-SIG-001`/`MOD-DOMAIN-RISK-001`/`SYS-MASTER-001`，**无 ROOT**。校验器 `VALID_BELONGS_TO` 亦无 ROOT。

**裁定方向**：金字塔顶点应自指 `belongs_to: SYS-MASTER-001`——校验器 P1-1 链追溯遇 SYS-MASTER-001 即 `break`（[L203](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L203)），自指能干净终止。

### 4.3 病根 #3：ALPHA-SIGNAL-DOMAIN-001 改名未传播（4 条违规）

**现象**：[blueprint_registry.yaml 变更历史](file:///d:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml#L1005-L1015) 记录"移除 ALPHA-SIGNAL-DOMAIN-001 → 新增 MOD-ALPHA_SIGNAL_DOMAIN"，但 [MOD-L02-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_factor/alpha_factor_core/blueprint.md#L20) 和 [MOD-L03-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_signal/signal_generation_core/blueprint.md#L23) 的 belongs_to 仍指向旧 ID。

**证据**：
- MOD-L02-001：`belongs_to: "ALPHA-SIGNAL-DOMAIN-001"`（[L20](file:///d:/ZephyrAlpha/docs/03_modules/_domain_factor/alpha_factor_core/blueprint.md#L20)）
- MOD-L03-001：`belongs_to: "ALPHA-SIGNAL-DOMAIN-001"`（[L23](file:///d:/ZephyrAlpha/docs/03_modules/_domain_signal/signal_generation_core/blueprint.md#L23)）
- 新名 MOD-ALPHA_SIGNAL_DOMAIN 已在 [_alpha_signal_domain/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_alpha_signal_domain/blueprint.md#L2)（`module_id: MOD-ALPHA_SIGNAL_DOMAIN`, `belongs_to: SYS-MASTER-001`）

**影响**：2× P1-1（链断裂）+ 2× P1-2（ALPHA-SIGNAL-DOMAIN-001 不在注册列表）

**病根**：改名传播规则缺失（与 [blueprint_id_naming_root_cause_report.md 病根#2](file:///d:/ZephyrAlpha/docs/_working/blueprint_id_naming_root_cause_report.md) 同源）——domain 蓝图改名后，下游 belongs_to 引用未同步。

### 4.4 病根 #4：layer 字段用废弃 L 格式（3 处，#206-B 执行遗漏，潜在违规）

**现象**：3 个蓝图 layer 字段仍用 `L01`/`L02`/`L03` 废弃格式：

| 蓝图 | 当前 layer | 应为 | 证据 |
|---|---|---|---|
| MOD-INF-042 | `L01` | `infra_ops` | [_domain_integration/local_model L8](file:///d:/ZephyrAlpha/docs/03_modules/_domain_integration/local_model/blueprint.md#L8) |
| MOD-L02-001 | `L02` | `factor` | [_domain_factor/alpha_factor_core L8](file:///d:/ZephyrAlpha/docs/03_modules/_domain_factor/alpha_factor_core/blueprint.md#L8) |
| MOD-L03-001 | `L03` | `signal` | [_domain_signal/signal_generation_core L8](file:///d:/ZephyrAlpha/docs/03_modules/_domain_signal/signal_generation_core/blueprint.md#L8) |

**真源**：
- [layer_vocabulary.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml#L50-L144) 16 个有效值均为语义名（data/infra_ops/factor/signal...），L01/L02/L03 仅作 `ai_keywords` 别名，非有效 `value`
- [trae_028 NUM-V02](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L67-L69)：蓝图 frontmatter layer 字段用域英文名 snake_case
- [panorama #206-B 详情 L2106-2118](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/dependency_architecture_panorama.md#L2106-L2118)：裁定"废弃 L0/L1/L2/L3 旧格式"，标记 ✅ 已执行（commit 9bc187061）

**病根**：#206-B 执行（任务卡 OPS-2026062627）范围仅覆盖 59 个 `trae_*.yaml` 规则文件（layer→compliance），**遗漏 blueprint.md frontmatter 的 layer 字段**。这 3 个蓝图的 L 旧值未被迁移。

**为何不在 22 条违规内**：P0-3 检查逻辑 `if layer in VALID_LAYERS`（[L152](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L152)）——L01/L02/L03 不在 VALID_LAYERS，检查被跳过。**这是校验器漏洞**：废弃值既不报 P0-3，也不报"layer 值非法"。属潜在违规，需新增检查项。

### 4.5 病根 #5：cross_layer 物理错位——校验器过严（9 条 P0-2）

**现象**：9 个 cross_layer 蓝图不在 `_cross_layer/` 下，但在各自域目录树内。探针实测分两组：

**A 组：4 个域级集成蓝图**（`blueprint_level=domain`，合法位于域根目录）：

| 蓝图 | 路径 | functional_domain |
|---|---|---|
| MOD-ALPHA_SIGNAL_DOMAIN | _alpha_signal_domain/blueprint.md | alpha_signal |
| MOD-GOVERNANCE | _domain_governance/blueprint.md | governance |
| MOD-GOVERNANCE | _domain_governance/capacity_upgrade/blueprint.md | governance |
| MOD-ML_EXPERIMENT_DOMAIN | _ml_experiment_domain/blueprint.md | ml_experiment |

**B 组：5 个域内子模块**（`blueprint_level=''`，位于域子目录，有明确域归属）：

| 蓝图 | 路径 | functional_domain |
|---|---|---|
| MOD-INF-011 | _domain_knowledge/vector_memory/blueprint.md | data |
| MOD-INF-019 | _domain_autonomy_core/agent_spec/blueprint.md | intelligence |
| MOD-INF-023 | _domain_governance/drift_detector/blueprint.md | governance |
| MOD-KB-001 | _domain_knowledge/knowledge_base/blueprint.md | intelligence |
| GOV-FSTR-001 | _restructuring/blueprint.md | governance |

**对照**：合规的 21 个 `_cross_layer/` 蓝图中，17 个 `blueprint_level=''`——**blueprint_level 不是可靠区分依据**（合规与错位蓝图大多都为空）。真正区分依据是**目录归属**：错位蓝图都在 `_{domain}/` 树下，属域所有；合规蓝图在 `_cross_layer/` 下，属无域归属的横切组件。

**真源**：[trae_014 §4.1 目录树](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L305-L328）——`level_1_dirs` 含 `_domain-l02-l03/` 等，`level_2_dirs` 含 `_cross_layer/` 与 `l{NN}_*/`。即**域蓝图应在域目录、横切模块在 _cross_layer/**。当前 P0-2 强制所有 cross_layer 进 `_cross_layer/`，与"域归属组件应在域目录"的架构原则冲突。

**病根**：P0-2 检查过严——未区分"有域归属的 cross_layer"与"无域归属的横切 cross_layer"。这与 project_memory 铁律"功能域平级→物理路径平级；能平铺绝不嵌套"一致：域拥有的组件应留在域目录。

> 注：第 10 个 P0-2（MOD-073）属病根 #1，正名后豁免于 KNOWN_LEVEL_01_IDS，不在此列。

### 4.6 病根 #6：MOD-INF-042 缺 belongs_to（1 条 P0-1）

**现象**：[_domain_integration/local_model/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_integration/local_model/blueprint.md) 无 belongs_to 字段（frontmatter 无此键）。

**真源**：[trae_014 §6.1](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L498-L503) + [trae_014 s1_2 prohibition L109](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L109)——Level 2 模块蓝图 MUST 声明 belongs_to。

**病根**：蓝图创建时遗漏字段。同时该蓝图 layer=L01（病根 #4），需一并修正。

### 4.7 附带发现：真源 §3.1 内部矛盾

[trae_014 §3.1](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L230-L233) 写 `Level 0 id: MOD-MASTER_BLUEPRINT`，但 [§5.1](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L393-L397) 写 `Level 0 prefix: SYS-MASTER, example: SYS-MASTER-001`。现实：SYS-MASTER-001 是系统顶点（_sys_master/），MOD-MASTER_BLUEPRINT 是域级集成索引（_master_blueprint/, belongs_to=SYS-MASTER-001）。**§3.1（information 段）陈旧，应改为 SYS-MASTER-001 与 §5.1 对齐。**

---

## 5. 裁定结果（回答 Q3 治本方向）

### 5.1 裁定总表

| 裁定 | 病根 | 决定 | 依据 | 消除违规 |
|---|---|---|---|---|
| **R1** SYS-MASTER-001 正名 | #1+#2 | frontmatter `module_id: MOD-073` → `SYS-MASTER-001`；`belongs_to: ROOT` → `SYS-MASTER-001`（自指终止） | trae_014 §5.1（Level 0=SYS-MASTER）+ §6.1（SYS-MASTER-001 合法，ROOT 非法）+ 校验器 L203 自指 break | 8 |
| **R2** ALPHA-SIGNAL 引用修正 | #3 | MOD-L02-001/L03-001 的 `belongs_to: ALPHA-SIGNAL-DOMAIN-001` → `MOD-ALPHA_SIGNAL_DOMAIN` | registry 变更历史已改名，派生引用须跟随（裁定#206 B-1 派生范式） | 4 |
| **R3** P0-2 校验放宽 | #5 | 改造校验器：有 functional_domain 且在域目录树内的 cross_layer 豁免；仅无域归属的横切组件强制 _cross_layer/ | project_memory"域平级→物理平级"+ trae_014 §4.1 域目录约定；**Owner 已确认** | 8 |
| **R4** MOD-INF-042 补 belongs_to | #6 | 补 `belongs_to`（指向 MOD-MASTER_BLUEPRINT 或其域蓝图） | trae_014 §6.1 MUST | 1 |
| **R5** 废弃 L 值修正 | #4 | MOD-INF-042 L01→infra_ops、MOD-L02-001 L02→factor、MOD-L03-001 L03→signal | #206-B 裁定 + layer_vocabulary.yaml | 0（潜在，需新检查项暴露） |
| **R6** P0-3 增强 + 真源 §3.1 修正 | #4+#7 | 校验器新增"layer 不得为废弃 L 格式"检查；trae_014 §3.1 Level 0 id → SYS-MASTER-001 | 填补校验漏洞 + 消除真源内部矛盾 | 防再发 |
| **R7** GOV-FSTR-001 迁移 | #5 | `_restructuring/` → `_cross_layer/restructuring/`（横切治理组件归位，非域归属） | directory_registry 无 _restructuring；GOV-FSTR-001 scope=global 同 _cross_layer/ peers | 1 |

**合计**：R1(8)+R2(4)+R3(8)+R4(1)+R7(1) = 22 条违规全部消除；R5+R6 治本防再发。

### 5.2 R1 正名风险量化

MOD-073 全项目引用：**8 文件 11 处**（探针实测）：

| 文件 | 处数 |
|---|---|
| docs/03_modules/module_registry.yaml | 1 |
| docs/03_modules/blueprint_registry.yaml | 2 |
| docs/03_modules/_sys_master/blueprint.md | 1 |
| docs/03_modules/_sys_master/index.md | 2 |
| docs/03_modules/_sys_master/changes/sys_master_001/index.md | 1 |
| docs/03_modules/_sys_master/changes/index.md | 1 |
| data/asset_index/target_path_tree.yaml | 1 |
| data/asset_index/project_entity_depgraph.yaml | 2 |

> 注意：`data/asset_index/*` 为派生文件（由 generate_derived_files.py 生成），改完源头后须重生成，禁止手改。

### 5.3 R3 放宽边界（关键裁定）

P0-2 放宽**不是无条件放行**，而是引入"域归属"判据：

```
cross_layer 蓝图合规条件（满足任一即放行）：
  (a) module_id in KNOWN_LEVEL_01_IDS（Level 0/1 特例，已豁免）
  (b) 在 _cross_layer/ 目录下（无域归属横切组件，原规则）
  (c) functional_domain 非空 且 物理路径在某 _{domain}/ 树下（域归属组件）
```

> 判据 (c) 与 project_memory"功能域平级→物理路径平级"一致，避免域组件被强制迁移到 _cross_layer/ 破坏域内聚。
>
> **R3 已由 Owner 确认采纳（2026-06-26）**。

**GOV-FSTR-001 裁定（已查清）**：`_restructuring/` **非注册域**（[directory_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml) 无记录），且不匹配 `_domain_*` 命名约定。GOV-FSTR-001 是**横切治理组件**（`scope: global`、代码在 `scripts/governance/restructuring/`、`functional_domain: governance` 与 `_cross_layer/audit_orchestrator`/`gate_engine` 等同属 governance 横切）。故 GOV-FSTR-001 **不走 R3 放宽，而走迁移**——迁入 `_cross_layer/restructuring/`（仅 blueprint.md + index.md 共 2 文件，影响小）。

**R3 放宽适用范围修正**：8 条 P0-2（A 组 4 域级 + B 组 4 域内子模块）走放宽；GOV-FSTR-001 单独走迁移。合计仍消除 9 条 P0-2。

---

## 6. 治本施工方案（分阶段，按风险递增）

### 阶段 A：规则与校验器治本（低风险，先做）

| 步骤 | 内容 | 验证 |
|---|---|---|
| A1 | 修复 [trae_014 §3.1](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml#L230-L233) Level 0 id `MOD-MASTER_BLUEPRINT` → `SYS-MASTER-001`（消除真源内部矛盾，R6） | grep §3.1 无 MOD-MASTER_BLUEPRINT 作为 Level 0 id |
| A2 | 改造 [validate_blueprint_placement.py P0-2](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_placement.py#L139-L147)：增加判据 (c) 域归属豁免（R3） | 单测：9 条 P0-2 转合规 |
| A3 | 新增 P0-5 检查：`layer` 值不得匹配 `^L\d{2}$` 废弃格式（R6，填补 P0-3 漏洞） | 单测：MOD-INF-042/L02-001/L03-001 报 P0-5 |

### 阶段 B：SYS-MASTER-001 正名（中风险）

| 步骤 | 内容 | 影响 |
|---|---|---|
| B1 | [_sys_master/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_sys_master/blueprint.md) frontmatter：`module_id: MOD-073` → `SYS-MASTER-001`；`belongs_to: ROOT` → `SYS-MASTER-001` | 1 文件 |
| B2 | 同步 8 文件 11 处 MOD-073 引用 → SYS-MASTER-001（registry/index/changes） | 8 文件 |
| B3 | 重生成派生文件 `data/asset_index/target_path_tree.yaml` + `project_entity_depgraph.yaml` | 2 文件（generate_derived_files.py） |
| B4 | 循环验收 `validate_blueprint_placement.py --ci` 至 0 P0 | — |

### 阶段 C：ALPHA-SIGNAL 引用 + layer 修正（低风险）

| 步骤 | 内容 | 影响 |
|---|---|---|
| C1 | [MOD-L02-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_factor/alpha_factor_core/blueprint.md#L20) `belongs_to: ALPHA-SIGNAL-DOMAIN-001` → `MOD-ALPHA_SIGNAL_DOMAIN`；`layer: L02` → `factor` | 1 文件 |
| C2 | [MOD-L03-001](file:///d:/ZephyrAlpha/docs/03_modules/_domain_signal/signal_generation_core/blueprint.md#L8) `belongs_to: ALPHA-SIGNAL-DOMAIN-001` → `MOD-ALPHA_SIGNAL_DOMAIN`；`layer: L03` → `signal` | 1 文件 |
| C3 | [MOD-INF-042](file:///d:/ZephyrAlpha/docs/03_modules/_domain_integration/local_model/blueprint.md) 补 `belongs_to: MOD-MASTER_BLUEPRINT`（或域蓝图）；`layer: L01` → `infra_ops` | 1 文件 |
| C4 | GOV-FSTR-001 迁移：`_restructuring/` → `_cross_layer/restructuring/`（blueprint.md + index.md），更新路径引用 | 2 文件 + 引用 |
| C5 | 循环验收至全 0 违规 | — |

### 阶段 D：DB 与 registry 同步

| 步骤 | 内容 |
|---|---|
| D1 | apply_depgraph.py 同步 depgraph.db 的 module_id/blueprint_id（MOD-073→SYS-MASTER-001） |
| D2 | module_registry.yaml / blueprint_registry.yaml 同步 |
| D3 | 全量重生成派生文件 + 循环验收 |

---

## 7. 防再发机制

1. **P0-5 检查固化**（R6/A3）：layer 废弃 L 格式被 CI 阻断，#206-B 遗漏不再可能。
2. **正名门禁**：未来 module_id 改名须用 apply_depgraph.py `--propagate-rename`（裁定#206 B-1/B-7 已规划）自动传播 belongs_to 引用，避免病根 #3 重演。
3. **域归属判据形式化**（R3/A2）：cross_layer 放置规则写入 trae_014 §4，使"域组件留域目录"有真源依据，而非校验器隐式逻辑。
4. **真源一致性巡检**：定期校验 trae_014 §3.1(information) 与 §5.1(rule) 不矛盾，防病根 #7 重演。

---

## 8. 回滚预案

- 每阶段前 `git commit` 备份（改 depgraph.db 前必备份，项目铁律）
- 阶段 B 正名若引发引用断裂，git checkout 回滚蓝图 + 重生成派生文件
- 阶段 A 校验器改造若误放行，单测可定位判据边界

---

## 附录 A：22 条违规清单（探针实测）

**P0（11）**：
```
[P0-1] MOD-INF-042 缺 belongs_to -> _domain_integration/local_model/blueprint.md
[P0-2] GOV-FSTR-001 不在 _cross_layer/ -> _restructuring/blueprint.md
[P0-2] MOD-ALPHA_SIGNAL_DOMAIN 不在 _cross_layer/ -> _alpha_signal_domain/blueprint.md
[P0-2] MOD-GOVERNANCE 不在 _cross_layer/ -> _domain_governance/blueprint.md
[P0-2] MOD-GOVERNANCE 不在 _cross_layer/ -> _domain_governance/capacity_upgrade/blueprint.md
[P0-2] MOD-ML_EXPERIMENT_DOMAIN 不在 _cross_layer/ -> _ml_experiment_domain/blueprint.md
[P0-2] MOD-073 不在 _cross_layer/ -> _sys_master/blueprint.md
[P0-2] MOD-INF-011 不在 _cross_layer/ -> _domain_knowledge/vector_memory/blueprint.md
[P0-2] MOD-INF-019 不在 _cross_layer/ -> _domain_autonomy_core/agent_spec/blueprint.md
[P0-2] MOD-INF-023 不在 _cross_layer/ -> _domain_governance/drift_detector/blueprint.md
[P0-2] MOD-KB-001 不在 _cross_layer/ -> _domain_knowledge/knowledge_base/blueprint.md
```

**P1（11）**：
```
[P1-1] MOD-073 链断裂: MOD-073 -> ROOT
[P1-1] MOD-L02-001 链断裂: -> ALPHA-SIGNAL-DOMAIN-001
[P1-1] MOD-L03-001 链断裂: -> ALPHA-SIGNAL-DOMAIN-001
[P1-2] SYS-MASTER-001 (来自 MOD-ALPHA_SIGNAL_DOMAIN) 不在注册列表
[P1-2] SYS-MASTER-001 (来自 MOD-GOVERNANCE) 不在注册列表
[P1-2] SYS-MASTER-001 (来自 MOD-MASTER_BLUEPRINT) 不在注册列表
[P1-2] SYS-MASTER-001 (来自 MOD-ML_EXPERIMENT_DOMAIN) 不在注册列表
[P1-2] SYS-MASTER-001 (来自 MOD-INF-035) 不在注册列表
[P1-2] ROOT (来自 MOD-073) 不在注册列表
[P1-2] ALPHA-SIGNAL-DOMAIN-001 (来自 MOD-L02-001) 不在注册列表
[P1-2] ALPHA-SIGNAL-DOMAIN-001 (来自 MOD-L03-001) 不在注册列表
```

## 附录 B：证据索引

| 编号 | 证据 | 位置 |
|---|---|---|
| E1 | 命名规则 SSoT + "标识符不是文件名" | trae_028:1022-1074, L1064 |
| E2 | Level 0 ID=SYS-MASTER | trae_014:393-397 (§5.1) |
| E3 | belongs_to 合法值（含 SYS-MASTER-001，无 ROOT） | trae_014:504-516 (§6.1) |
| E4 | layer 16 语义值，L 格式废弃 | layer_vocabulary.yaml:50-144 |
| E5 | #206-B 裁定"废弃 L0/L1/L2/L3"标记已执行 | panorama:2106-2118 |
| E6 | #206-B 执行仅覆盖 trae_*.yaml，遗漏 blueprint.md | panorama:2115-2116 |
| E7 | SYS-MASTER-001 双轨制（frontmatter MOD-073） | _sys_master/blueprint.md:2,26 |
| E8 | ALPHA-SIGNAL-DOMAIN-001 改名记录 | blueprint_registry.yaml:1005-1015 |
| E9 | MOD-L02/L03-001 belongs_to 指向旧 ID | alpha_factor_core:20, signal_generation_core:23 |
| E10 | MOD-INF-042 layer=L01 + 缺 belongs_to | local_model:8 |
| E11 | 校验器 P0-2/P1-1/P1-2 逻辑 | validate_blueprint_placement.py:139-220 |
| E12 | 真源 §3.1 与 §5.1 矛盾 | trae_014:230-233 vs 393-397 |
| E13 | MOD-073 引用 8 文件 11 处 | grep 实测 |
