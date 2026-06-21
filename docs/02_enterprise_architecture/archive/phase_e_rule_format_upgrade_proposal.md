---
module_id: EA-DOC-017
title: 阶段E — 规则文件格式升级施工方案
doc_type: discussion
status: in_progress
version: 2.0.0
layer: L1
owner: architecture
classification: internal
language: zh-CN
created_by: AI Session
date: 2026-06-12
updated: 2026-06-13
summary: 规则文件从Markdown到结构化YAML的升级方案。YAML-SSoT+DB-Index架构已裁定并执行，53个YAML文件已创建，68个MD文件已扫描提取。当前进入深度内容覆盖核对阶段。
tags: [rule-format, yaml, governance, phase-E, architecture-upgrade]
depends_on: [PS-REG-001, PS-STD-011, GOV-ARCH-006]
---

# 阶段E：规则文件格式升级 — 施工方案

## 0. 项目背景

ZephyrAlpha 是一个 AI 自治量化交易系统。项目规模：514模块 / 388脚本 / 73门禁 / 41蓝图 / 30注册表 / 14842文件 / 35功能域。

全项目所有规则文件原为md格式，在100% AI开发项目中导致大量规则形同虚设。本阶段将规则存储升级为结构化YAML。

### 执行进度

| 阶段 | 状态 | 说明 |
|------|:---:|------|
| E1 问题诊断 | ✅ 完成 | 7大痛点已识别 |
| E2 方案对比 | ✅ 完成 | 4方案对比，方案4胜出 |
| E3 触发机制 | ✅ 设计完成 | 操作/Skill/Gate三路触发 |
| E4 迁移执行 | 🔄 进行中 | 53个YAML已创建，68个MD已提取，裁定全部YAML化，深度提取中 |
| E5 系统集成 | ⏳ 待执行 | 依赖E4完成 |
| E6~E10 架构裁定 | ✅ 完成 | YAML-SSoT+DB-Index |
| 内容类型清查 | ✅ 完成 | 49种内容类型，裁定全部YAML化 |
| MD文件处置裁定 | ✅ 完成 | 全部YAML化后删除原始MD |

---

## E1：当前问题诊断

### E1.1 核心痛点（按严重度排序）

| # | 痛点 | 严重度 | 量化证据 |
|---|------|:---:|---------|
| 1 | **85%规则是"君子协定"** — 仅20条有代码级强制，115条完全靠AI自觉 | P0 | code=10, hook=6, ci=4, doc=102, manual=13 |
| 2 | **37%规则文件是死文件** — 无任何程序化消费者 | P0 | 92个实质性文件中34个死文件 |
| 3 | **规则与Skill/Gate无结构化关联** | P0 | 22个skill无rule_ids字段 |
| 4 | **TRAE域漂移** | P1 | RULE-TWELVE~RULE-SIXTEEN未登记 |
| 5 | **Token浪费** — 冷启动读1103行project_rules.md，利用率<5% | P1 | 1103行≈8000 tokens |
| 6 | **MD循环引用** — 多组策略文件仅互相引用，无代码出口 | P1 | 安全/数据/领域策略闭环 |
| 7 | **十字段头部无解析器** | P2 | 514个模块一致性靠AI自觉 |

### E1.2 规则遵守率估算

| 规则类别 | 总数 | AI实际遵守比例 | 原因 |
|---------|:---:|:---:|------|
| RULE-ZERO~RULE-FOUR（铁律前5条） | 5 | ~70% | 有代码级执行器 |
| RULE-FIVE~RULE-ELEVEN（铁律后6条） | 6 | ~30% | 无代码级执行器 |
| RULE-TWELVE~RULE-SIXTEEN（新铁律） | 5 | ~15% | 未在rule-registry登记 |
| 防幻觉十八条 | 18 | ~40% | 部分有代码校验 |
| MTH-001~013（方法论） | 13 | ~10% | 无代码级强制 |
| ABS/COND（行为边界） | 100 | ~5% | AI几乎不查 |

**核心结论**：有代码级执行器的规则遵守率70%+，纯靠AI"读到并遵守"的规则遵守率<30%。**规则格式升级的核心目标不是换格式，而是建立程序化强制执行链路。**

<details>
<summary>E1.3 规则文件生死审计（已完成 — 死文件已YAML化激活）</summary>

| 分类 | 文件数 | 占比 | 当前状态 |
|------|:-----:|:----:|------|
| **活**（有Python代码消费者） | 27 | 29.3% | 已YAML化 |
| **半活**（仅MD/AI注入引用） | 31 | 33.7% | 已YAML化 |
| **死**（无任何消费者） | 34 | 37.0% | 已YAML化激活 |

死文件已全部提取到YAML中，通过YAML的结构化字段（triggers/conditions/actions）建立了程序化消费路径。原"死"是因为MD格式无法被程序消费，YAML化后已激活。

</details>

### E1.4 现有规则体系全景

#### 规则存储架构（E9裁定后，已实施）

| 层级 | 存储 | 格式 | 角色 | Git diff | AI Read |
|------|------|------|------|:--------:|:-------:|
| **内容SSoT** | `rules/trae_001_file_operation_security.yaml` 等 | YAML | 规则内容唯一真源 | ✅ | ✅ 直接Read |
| **关系索引** | depgraph.db nodes/edges/rule_bindings表 | SQLite | 规则元数据+关系索引 | ❌ | ✅ Python查询 |
| **执行日志** | governance.db rule_enforcement_log表 | SQLite | 规则执行记录 | ❌ | ✅ Python查询 |
| L0 注入 | `.trae/rules/project_rules.md` | Markdown | 从YAML生成，IDE注入 | ✅ | ✅ 自动注入 |
| L1 人类可读 | `rules/TRAE-001.md` | Markdown | 从YAML生成，人类审阅 | ✅ | ✅ 直接Read |

#### 规则从定义到执行的完整链路

```
YAML文件 (内容SSoT)
    ↓ sync_rule_registry.py 同步
depgraph.db (关系索引: nodes/edges/rule_bindings)
    ↓ RuleLoader查询
AI Session 上下文 (行为约束)
    ↓ 违反时触发
GateEngine / PhaseCheckRegistry (代码级强制)
    ↓ 检查结果
GateResult (GREEN/YELLOW/RED)
    ↓ 写入
governance.db rule_enforcement_log (执行日志, append-only)
```

**关键断裂点**：AI Session 上下文 → GateEngine 之间没有程序化连接。规则靠AI"读到并遵守"，Gate靠独立定义的check。两者之间无结构化关联。

---

## E2：新格式方案对比

### 最终裁定：方案4 — YAML-SSoT + DB-Index

| 维度 | 方案1: YAML规则库 | 方案2: SQLite数据库 | 方案3: YAML+MD混合 | **方案4: YAML-SSoT+DB-Index** |
|------|:---:|:---:|:---:|:---:|
| **查询效率** | 中 | 高 | 中 | 高 |
| **AI可消费性** | 高 | 低 | 高 | **最高** |
| **维护成本** | 低 | 中 | 高 | **低** |
| **版本控制** | 好 | 差 | 好 | **好** |
| **按需加载** | 好 | 好 | 好 | **最好** |
| **Policy as Code** | ✅ | ❌ | ✅ | **✅** |

<details>
<summary>E2.1~E2.4 各方案详细对比（已裁定，折叠）</summary>

**方案2不推荐原因**：AI需3步消费（DB→生成YAML→Read），生成步骤是漂移温床。

**方案3不推荐原因**：双写维护成本高，MD副本可能过时。

**方案4核心理念**：规则不是"文档"，是"功能的契约"。YAML文件是内容真源（AI直接消费），depgraph.db是关系索引（程序化查询+执行日志）。

</details>

### YAML规则定义示例（已实施）

```yaml
rule_id: TRAE-001
title: "文件操作安全协议"
aliases: [RULE-ZERO, RULE-ONE, RULE-THREE, RULE-FOUR, RULE-FIVE]
layer: L0
severity: critical
scope: file_operation
domain: TRAE
triggers:
  - operation: file_write
  - operation: file_create
sections:
  write_lock:
    title: "写入文件锁协议"
    original_rules: [RULE-ZERO]
    conditions:
      - type: pre_condition
        check: "lock_files.py check {file_path}"
        pass: FREE
        fail: BLOCKED
    actions:
      - type: mandatory
        step: "lock_files.py acquire → 写入 → lock_files.py release"
    prohibitions:
      - 绕过锁协议直接写入
references:
  rule_ids: [TRAE-008]
  scripts: [scripts/lock_files.py, scripts/scaffold.py]
  modules: [zephyr.runtime.staging_area]
enforcement:
  type: code
  executors: [lock_files.py, scaffold.py, audit_registration.py]
  bypass_allowed: false
metadata:
  change_policy: frozen
  impact_level: H
  modification_permission: immutable_core
provenance:
  source_files:
    - path: ".trae/rules/project_rules.md"
      sections: [RULE-ZERO, RULE-ONE, RULE-THREE, RULE-FOUR, RULE-FIVE]
      hash: "sha256:a1b2c3d4..."
```

---

## E3：规则分类和触发机制

### E3.1 规则三层分类

| 层级 | 标记 | 含义 | 违反后果 | 示例 |
|:---:|:---:|------|---------|------|
| L0 | `severity: critical` | 铁律，不可绕过 | 操作被阻断 | RULE-ZERO文件锁 |
| L1 | `severity: error` | 强制标准，违反必须修复 | 任务不可关闭 | 命名约定、注册表登记 |
| L2 | `severity: warning` | 建议指南，违反需记录 | 警告但不阻断 | MTH方法论、文档风格 |

### E3.2 触发机制设计

| 触发方式 | 机制 | 示例 |
|---------|------|------|
| **操作触发** | AI执行操作前，RuleLoader查DB索引→Read YAML规则 | AI要写文件→加载TRAE-001 |
| **Skill触发** | Skill激活时，自动加载关联规则子集 | implementer skill→加载代码写规则集 |
| **Gate触发** | Gate检查时，引用规则enforcement配置 | G0门禁→检查TRAE-001 |

### E3.3 推荐方案A（轻量加载器）

```
from zephyr.governance.rule_engine import RuleLoader
rules = RuleLoader.load_for_operation("file_write")
# DB查索引→Read YAML文件→返回规则内容
```

不做执行拦截——AI是外部LLM无法拦截，靠加载+Gate事后校验双保险。

<details>
<summary>E3.4~E3.6 Skill/Gate/十字段集成设计（设计完成，待实施）</summary>

**Skill集成**：扩展skill_registry.yaml的rule_bindings字段，SkillLoader加载时提取rule_ids。

**Gate集成**：扩展Gate YAML的check定义增加rule_ids字段，GateEngine返回结果增加rule_ids。

**十字段解析器**：新增HeaderFieldParser模块，[STABILITY]→metadata.change_policy→nodes.change_policy。

</details>

---

## E4：迁移执行

### E4.1 迁移范围

| 类别 | 文件数 | 操作 | 状态 |
|------|:-----:|------|:---:|
| 内容.md文件（需YAML化） | **68** | 提取→生成YAML | 🔄 进行中 |
| templates/模板文件 | **10** | 已纳入YAML provenance | ✅ |
| index.md导航文件 | 34 | 不动 | — |
| _registry/下.yaml文件 | 46 | 不动 | — |

### E4.2 当前执行进度

| 步骤 | 操作 | 产出 | 状态 |
|:---:|------|------|:---:|
| 0 | 预备份 | `D:\临时工作区\_backups\01_policies_and_standards\` | ✅ |
| 1 | 扫描68个MD文件，提取规则段落 | `extraction_manifest.json` | ✅ |
| 2 | 按操作分组，制定合并方案 | `merge_plan.yaml` | ✅ |
| 3 | 逐文件转换：提取MD→生成YAML→验证 | 53个YAML文件 | ✅ |
| 4 | 6维全量验证 | 覆盖率78/78, hash152/152, 追溯53/53, 引用80/80, 孤儿0, 重复0 | ✅ |
| 5 | **深度内容覆盖核对** | 内容类型清查（49种类型） | 🔄 进行中 |
| 6 | MD文件删除 | — | ⏳ 待决 |

### E4.3 已完成的YAML化统计

| 文件组 | 文件数 | 提取规则数 | YAML文件 |
|--------|:---:|:---:|---------|
| domains/L00-L07 | 8 | 78 | trae_050_domain_policy_data_factor.yaml |
| governance/ai | 5 | 88 | trae_039_ai_hallucination_detection.yaml, trae_040_ai_model_routing.yaml |
| governance/architecture | 7 | 50 | trae_036_arch_gate_transition.yaml~038.yaml |
| governance/compliance | 3 | 44 | trae_044_compliance_audit.yaml |
| governance/data | 3 | 43 | trae_045_data_quality_lineage.yaml |
| governance/document | 10 | 198 | trae_028_doc_structure_naming.yaml~030.yaml |
| governance/engineering | 4 | 23 | trae_010_code_naming_organization.yaml~012.yaml, trae_046_engineering_code_restructure.yaml~047.yaml |
| governance/module | 6 | 50 | trae_032_module_lifecycle.yaml~033.yaml |
| governance/security | 3 | 18 | trae_031_security_key_access.yaml |
| governance/task | 3 | 37 | trae_034_task_card_standard.yaml~035.yaml |
| meta/ | 12 | 219 | trae_018_behavior_code_prohibition.yaml~027.yaml, trae_041_meta_rule_classification.yaml~043.yaml |
| operational/ | 4 | 70 | trae_048_ops_vibe_coding_session.yaml~049.yaml |
| **合计** | **68** | **~1018** | **53个YAML文件** |

### E4.4 深度内容覆盖核对（当前阶段）

6维验证已ALL PASS，但深度抽查发现：**第一轮YAML化偏重A类规则（禁止/必须/约束），遗漏了大量B~I类内容**。

#### 内容类型清查结果

扫描68个MD文件，发现**49种内容类型**：

| 推荐格式 | 类型数 | 类型列表 | 说明 |
|---------|:---:|---------|------|
| **YAML_RECOMMENDED** | 26 | A5~A7, B2, B9, C1~C2, C4~C5, D4~D6, E1~E3, E5~E8, G1, G4, G6, H2~H3, I6 | 结构化数据，机器需消费 |
| **MD_RECOMMENDED** | 14 | B1, B3~B5, B7~B8, B10, D3, F1~F3, I1~I3 | 叙事性内容，需上下文说明 |
| **EITHER** | 19 | A1~A4, B6, C3, D1~D2, D7, E4, F4~F6, G2~G3, G5, H1, H4, I4~I5 | 两种格式均可 |

#### 高频遗漏内容类型（第一轮YAML化未充分覆盖）

| 类型 | 文件数 | 当前YAML覆盖 | 典型遗漏内容 |
|------|:---:|:---:|---------|
| **B1 步骤式程序** | 61 | 部分 | 完整操作序列、前置条件、预期结果 |
| **B2 状态机** | 11 | 部分 | 状态转换表、守卫条件、不变量 |
| **C1 层级体系** | 42 | 部分 | 分级定义、枚举值、SLA阈值 |
| **C2 分类法** | 21 | 部分 | 类别→子类别→属性层级 |
| **D4 消费者注册表** | 11 | 少量 | 模块消费者列表 |
| **E2 变更同步规则** | 14 | 少量 | "修改此文件必须同步更新X/Y/Z" |
| **F6 反模式** | 9 | 少量 | 反模式描述+分类标签 |
| **G4 字段定义** | 15 | 部分 | 字段名/类型/必填/枚举值 |

#### E4.4a 裁定：全部YAML化，二分法=能/不能=全部能

**裁定时间**：2026-06-13
**裁定人**：Owner + AI

**核心裁定**：49种内容类型全部YAML化。不存在"MD推荐"类型。MD只有一个角色：YAML的自动生成只读副本。

| 分类 | 内容 | 格式 | 编辑权 | 消费者 |
|------|------|------|:---:|--------|
| **规则内容** | 全部49种内容类型 | YAML | ✅ 可编辑 | AI / RuleLoader / Gate / Skill |
| **人类可读副本** | 从YAML自动生成 | MD | ❌ 禁止手动编辑 | 人类浏览 |

**裁定理由**：在100% AI开发项目中，YAML对AI的消费效率碾压MD。散文式描述需要AI理解语义、提取步骤、判断分支；YAML结构化表达AI零歧义消费。YAML化不是"也能做"，是"做得更好"。

**14种原"推荐MD"类型的YAML化方案**：

| 类型 | YAML schema设计 |
|------|----------------|
| B1 步骤式程序 | `procedure: [{order, action, pre_condition, expected_result, on_failure}]` |
| B3 决策树 | `decision_tree: [{condition, if_true, if_false}]` |
| B4 升级流程 | `escalation: [{trigger, level, action, timeout}]` |
| B5 回滚程序 | `rollback: [{order, action, verify, on_fail}]` |
| B7 验证流程 | `verification: [{step, command, expected_exit, on_fail}]` |
| B8 入职流程 | `onboarding: [{order, action, purpose}]` |
| B10 事件响应 | `incident_response: [{scenario, severity, steps}]` |
| D3 症状-原因映射 | `symptom_mapping: [{symptom, root_cause, treatment}]` |
| F1 错误模式 | `error_patterns: [{pattern, description, example, detection}]` |
| F2 诊断程序 | `diagnosis: [{order, check, pass_criteria, action}]` |
| F3 根因分析 | `root_cause_analysis: {methodology: [steps], reasoning_chain: [decision]}` |
| I1 原则 | `principles: [{id, statement, rationale, applies_to}]` |
| I2 背景 | `context: {summary, impact_on_rules, key_decisions}` |
| I3 示例 | `examples: [{title, code: \|, language, note}]` |

**4个讨论问题的裁定**：

| # | 问题 | 裁定 |
|---|------|------|
| 1 | "两者皆可"的19种 | **全部YAML化**，无中间态 |
| 2 | B1步骤式程序 | **YAML化**，新增procedure schema |
| 3 | 双SSoT模式 | **否决**。YAML=唯一SSoT，MD=自动生成副本 |
| 4 | GOV-MOD-007编码损坏 | **P1修复**，在深度覆盖核对时一并处理 |

#### 待决问题：MD文件处置策略（已裁定）

~~选项A~D~~ → **裁定：全部YAML化后删除原始MD**。MD副本由`_yaml_to_md.py`自动生成，禁止手动编辑。

#### E4.4b 深度覆盖核对执行计划

| 步骤 | 操作 | 产出 |
|:---:|------|------|
| 1 | 扩展YAML schema — 新增14种section类型 | schema定义 |
| 2 | 逐文件深度提取 — 对68个MD按49种内容类型全量提取到YAML | 补充后的53个YAML |
| 3 | 循环验证 — 每个文件提取后验证覆盖度，直到零遗漏 | 验证报告 |
| 4 | 删除原始MD — 验证通过后删除，仅保留YAML自动生成的MD副本 | 68个MD删除 |

<details>
<summary>E4.5 迁移过程防丢失（三锁一验 — 已实施）</summary>

| 锁 | 机制 | 状态 |
|---|------|:---:|
| 锁1 | 预备份到`D:\临时工作区\_backups\`+逐文件转换 | ✅ |
| 锁2 | SHA256指纹校验，存入YAML provenance字段 | ✅ |
| 锁3 | 双向覆盖率检查（MD→YAML + YAML→MD） | ✅ |
| 验 | `verify_rule_yaml_migration.py` 6维自动化验证 | ✅ ALL PASS |

验证结果：
- MD→YAML Coverage: 78/78 (100%)
- SHA256 Hash: 152/152 (100%)
- YAML→MD Traceability: 53/53 (100%)
- References Integrity: 80/80 (0 broken)
- No Orphan YAML: 0
- No Duplicate: 0

</details>

<details>
<summary>E4.6 合并去重策略（已实施）</summary>

**原则**：规则按AI执行的操作分组，不按"域标签"分组。

**合并后规则集**（135条→53个YAML文件）：

| 合并后rule_id | 合并内容 | 原条数 |
|-------------|---------|:---:|
| trae_001 | 文件操作安全（ZERO+ONE+THREE+FOUR+FIVE） | 5→1 |
| trae_002 | 反孤儿+搜索先行（TWO+EIGHT） | 2→1 |
| trae_003 | 任务粒度+完成门槛（SIX+THIRTEEN） | 2→1 |
| trae_004 | 并行执行+原子事务（SEVEN+ONE事务部分） | 2→1 |
| trae_005 | 修改原则+治理施工（NINE+TEN） | 2→1 |
| trae_006~009 | 防幻觉（ANTI-HALL 01~18合并为4组） | 18→4 |
| trae_010~012 | 代码构建标准 | 10→3 |
| trae_013~017 | 架构约束 | 27→5 |
| trae_050 | 域策略（L00+L02+L04+L07合并） | 8→1 |

**语义近似裁定规则**：

| 优先级 | 情况 | 裁定 |
|:---:|------|------|
| 1 | 完全重复 | 保留内容更丰富的版本 |
| 2 | 语义近似，后者更丰富 | 选后者，合并前者独有优点 |
| 3 | 粒度不均 | 统一为操作粒度 |
| 4 | 分类混乱 | 重新归类到正确操作分组 |

</details>

<details>
<summary>E4.7 优先迁移规则（批次1已完成）</summary>

| rule_id | 来源 | 代码执行器 | 状态 |
|---------|------|-----------|:---:|
| TRAE-001 | RULE-ZERO | lock_files.py | ✅ |
| TRAE-002 | RULE-ONE | 无（原子写入模板） | ✅ |
| TRAE-003 | RULE-TWO | audit_registration.py | ✅ |
| TRAE-004 | RULE-THREE | 无（删除审判流程） | ✅ |
| TRAE-005 | RULE-FOUR | scaffold.py | ✅ |
| TRAE-006 | RULE-FIVE | 无（零残留检查） | ✅ |
| TRAE-007 | RULE-SIX | TaskRepository._validate_template_fields() | ✅ |
| TRAE-008 | RULE-SEVEN | 无（ThreadPoolExecutor判定） | ✅ |
| TRAE-009 | RULE-EIGHT | 无（搜索先行协议） | ✅ |
| TRAE-010 | RULE-NINE | 无（修改原则） | ✅ |
| TRAE-011 | RULE-TEN | PhaseManager | ✅ |

</details>

---

## E5：与项目其他系统的集成

### E5.1 集成状态

| 集成点 | 具体方案 | 状态 |
|--------|---------|:---:|
| 规则作为测试用例来源 | 每条L0/L1规则→至少一个测试用例 | ⏳ |
| 与depgraph结合 | 规则作为nodes表节点，edges表constrains边 | ✅ DDL已设计 |
| 与架构全景图结合 | 规则domain字段对应35域定义 | ✅ |
| RuleLoader集成 | DB查索引→Read YAML取内容 | ✅ 已实现 |
| Skill集成 | skill_registry.yaml扩展rule_bindings | ⏳ 待开发 |
| Gate集成 | Gate YAML扩展rule_ids字段 | ⏳ 待开发 |
| 十字段解析器 | HeaderFieldParser模块 | ⏳ 待开发 |

### E5.2 RuleLoader API

```python
from zephyr.governance.rule_engine import RuleLoader
loader = RuleLoader()

# 按操作加载（AI写文件前调用）
rules = loader.load_for_operation('file_write')

# 按Skill加载
rules = loader.load_for_skill('SKILL-DOM-DED-001')

# 按Gate加载
rules = loader.load_for_gate('G0')

# 获取全部L0铁律
critical = loader.get_critical_rules()

# 按ID精确加载
rule = loader.get_rule_by_id('TRAE-001')

# 列出全部规则摘要
summary = loader.list_all_rules()
```

### E5.3 规则清单（53条）

#### L0 铁律（critical，14条）

| rule_id | 标题 | scope | 文件 |
|---------|------|-------|------|
| TRAE-001 | 文件操作安全协议 | file_operation | trae_001_file_operation_security.yaml |
| TRAE-002 | 反孤儿与搜索先行协议 | feature_creation | trae_002_anti_orphan_search_first.yaml |
| TRAE-003 | 任务粒度与完成门槛协议 | task_management | trae_003_task_granularity_threshold.yaml |
| TRAE-004 | 并行执行与原子事务协议 | script_execution | trae_004_parallel_atomic_transaction.yaml |
| TRAE-005 | 修改原则与治理施工协议 | code_modification | trae_005_modification_governance.yaml |
| TRAE-006 | 防幻觉-结构追溯层 | code_structure | trae_006_anti_hallucination_structure.yaml |
| TRAE-007 | 防幻觉-行为约束层 | code_behavior | trae_007_anti_hallucination_behavior.yaml |
| TRAE-008 | 防幻觉-输出验证层 | output_verification | trae_008_anti_hallucination_output.yaml |
| TRAE-009 | 防幻觉-安全防护层 | security_guard | trae_009_anti_hallucination_safety.yaml |
| TRAE-018 | 行为边界-代码操作绝对禁止 | code_operation_prohibition | trae_018_behavior_code_prohibition.yaml |
| TRAE-019 | 行为边界-系统安全绝对禁止 | security_prohibition | trae_019_behavior_security_prohibition.yaml |
| TRAE-020 | 行为边界-治理纪律绝对禁止 | governance_prohibition | trae_020_behavior_governance_prohibition.yaml |
| TRAE-021 | 行为边界-其余绝对禁止 | other_prohibition | trae_021_behavior_other_prohibition.yaml |
| TRAE-052 | 铁律补充-跨蓝图变更与项目瘦身 | cross_blueprint_change_cleanup | trae_052_cross_blueprint_change_cleanup.yaml |

#### L1 标准（error，27条）

| rule_id | 标题 | scope | 文件 |
|---------|------|-------|------|
| TRAE-010 | 代码构建-命名与组织 | code_naming | trae_010_code_naming_organization.yaml |
| TRAE-011 | 代码构建-类型与导入 | code_type_import | trae_011_code_type_import.yaml |
| TRAE-012 | 代码构建-测试与安全 | code_test_security | trae_012_code_test_security.yaml |
| TRAE-013 | 架构约束-跨包依赖 | architecture_dependency | trae_013_arch_cross_package_dep.yaml |
| TRAE-014 | 架构约束-蓝图对齐 | architecture_blueprint | trae_014_arch_blueprint_alignment.yaml |
| TRAE-015 | 架构约束-路径与注册 | architecture_path_registry | trae_015_arch_path_registration.yaml |
| TRAE-016 | 架构约束-漂移检测 | architecture_drift | trae_016_arch_drift_detection.yaml |
| TRAE-017 | 架构约束-治理顺序 | architecture_governance_order | trae_017_arch_governance_order.yaml |
| TRAE-022 | 行为边界-条件禁止(代码与安全) | conditional_prohibition_code_security | trae_022_behavior_conditional_code.yaml |
| TRAE-023 | 行为边界-条件禁止(治理与文档) | conditional_prohibition_governance_doc | trae_023_behavior_conditional_governance.yaml |
| TRAE-028 | 文档治理-结构与命名 | doc_structure_naming | trae_028_doc_structure_naming.yaml |
| TRAE-029 | 文档治理-操作安全 | doc_operation_safety | trae_029_doc_operation_security.yaml |
| TRAE-030 | 文档治理-编号与元数据 | doc_numbering_metadata | trae_030_doc_numbering_metadata.yaml |
| TRAE-031 | 安全治理-密钥与访问控制 | security_access | trae_031_security_key_access.yaml |
| TRAE-032 | 模块治理-准入与生命周期 | module_governance | trae_032_module_lifecycle.yaml |
| TRAE-033 | 模块治理-注册与同步 | module_registry_sync | trae_033_module_registration_sync.yaml |
| TRAE-034 | 任务系统-卡片标准与生命周期 | task_card_lifecycle | trae_034_task_card_standard.yaml |
| TRAE-035 | 任务系统-施工与验证 | task_construction_verification | trae_035_task_construction_verification.yaml |
| TRAE-036 | 架构治理-门禁与过渡 | architecture_gate_transition | trae_036_arch_gate_transition.yaml |
| TRAE-037 | 架构治理-合格与版本化 | architecture_qualification | trae_037_arch_qualification_versioning.yaml |
| TRAE-038 | 架构治理-CTR注入规则 | architecture_ctr_injection | trae_038_arch_ctr_injection.yaml |
| TRAE-039 | AI治理-幻觉检测与自检 | ai_hallucination | trae_039_ai_hallucination_detection.yaml |
| TRAE-040 | AI治理-模型路由与协作 | ai_model_routing | trae_040_ai_model_routing.yaml |
| TRAE-044 | 合规治理-审计与监管 | compliance_audit | trae_044_compliance_audit.yaml |
| TRAE-045 | 数据治理-质量与血缘 | data_governance | trae_045_data_quality_lineage.yaml |
| TRAE-046 | 工程治理-代码与重组安全 | engineering_code_restructure | trae_046_engineering_code_restructure.yaml |
| TRAE-047 | 工程治理-文件头部与扩展 | engineering_header_expansion | trae_047_engineering_file_header.yaml |

#### L2 指南（warning，12条）

| rule_id | 标题 | scope | 文件 |
|---------|------|-------|------|
| TRAE-024 | 方法论-诊断与根因分析 | methodology_diagnosis | trae_024_methodology_diagnosis.yaml |
| TRAE-025 | 方法论-决策与执行 | methodology_decision | trae_025_methodology_decision.yaml |
| TRAE-026 | 方法论-质量与度量 | methodology_quality | trae_026_methodology_quality.yaml |
| TRAE-027 | 方法论-协作与演进 | methodology_collaboration | trae_027_methodology_collaboration.yaml |
| TRAE-041 | 元规则-规则分类与裁决 | meta_rule_classification | trae_041_meta_rule_classification.yaml |
| TRAE-042 | 元规则-标准体系与模板 | meta_standard_template | trae_042_meta_rule_standard.yaml |
| TRAE-043 | 元规则-元数据与度量 | meta_metadata_metrics | trae_043_meta_rule_metadata.yaml |
| TRAE-048 | 操作-Vibe Coding会话管理 | operational_vibe_coding | trae_048_ops_vibe_coding_session.yaml |
| TRAE-049 | 操作-领域操作手册 | operational_domain | trae_049_ops_domain_manual.yaml |
| TRAE-050 | 域策略-数据源与因子层 | domain_data_factor | trae_050_domain_policy_data_factor.yaml |
| TRAE-051 | 域策略-风控与盘后层 | domain_risk_analytics | trae_051_domain_policy_risk_backtest.yaml |
| TRAE-053 | 铁律补充-自动化双轨判定 | automation_dual_track | trae_053_automation_dual_track.yaml |

### E5.4 原规则→YAML映射

| 原规则 | 合并到 | 原规则 | 合并到 |
|--------|--------|--------|--------|
| RULE-ZERO | TRAE-001 | RULE-ONE | TRAE-001 |
| RULE-TWO | TRAE-002 | RULE-THREE | TRAE-001 |
| RULE-FOUR | TRAE-001 | RULE-FIVE | TRAE-001 |
| RULE-SIX | TRAE-003 | RULE-SEVEN | TRAE-004 |
| RULE-EIGHT | TRAE-002 | RULE-NINE | TRAE-005 |
| RULE-TEN | TRAE-005 | RULE-ELEVEN | TRAE-052 |
| RULE-TWELVE | TRAE-052 | RULE-THIRTEEN | TRAE-003 |
| ANTI-HALL-01~06 | TRAE-006 | ANTI-HALL-07~10 | TRAE-007 |
| ANTI-HALL-11~14 | TRAE-008 | ANTI-HALL-15~18 | TRAE-009 |
| ABS-01~08 | TRAE-018 | ABS-09~16 | TRAE-019 |
| ABS-17~24 | TRAE-020 | ABS-25~48 | TRAE-021 |
| COND-01~26 | TRAE-022 | COND-27~52 | TRAE-023 |

完整映射见 `data/databases/governance_metadata/merge_plan.yaml`

### E5.5 维护操作

| 操作 | 命令 |
|------|------|
| 修改规则 | 编辑YAML → `python _yaml_to_md.py --all` → `python scripts/governance/sync_rule_registry.py --sync-yaml` |
| 验证迁移 | `python scripts/governance/verify_rule_yaml_migration.py --all` |
| 四方对齐 | `python scripts/governance/check_rule_four_way_alignment.py --all` |
| 监控变更 | `python -m zephyr.governance.rule_watcher --once` |
| 查看索引 | `cat docs/01_policies_and_standards/rules/_index.yaml` |

### E5.6 YAML文件schema

| 字段 | 类型 | 说明 |
|------|------|------|
| rule_id | str | 唯一标识（TRAE-XXX） |
| title | str | 规则标题 |
| aliases | list | 原规则ID列表 |
| layer | L0/L1/L2 | 层级 |
| severity | critical/error/warning | 严重度 |
| scope | str | 操作范围（用于触发匹配） |
| domain | str | 域 |
| triggers | list | 触发条件（operation/skill_id/gate_id） |
| sections | dict | 规则内容（conditions/actions/prohibitions） |
| references | dict | 引用（rule_ids/scripts/modules/blueprints） |
| enforcement | dict | 执行机制（type/executors/bypass_allowed） |
| metadata | dict | 元数据（change_policy/impact_level/modification_permission） |
| provenance | dict | 来源追溯（source_files/hash/extracted_at） |

---

## E6：SSoT架构决策

### 最终裁定：YAML-SSoT + DB-Index

| 维度 | YAML文件 | depgraph.db | governance.db |
|------|---------|-------------|-------------|
| 存储内容 | 规则内容（条件/动作/文本） | 规则元数据+关系索引 | 执行日志（append-only） |
| 角色 | 内容SSoT | 关系索引 | 运营数据 |
| 写入方向 | 人工/AI编辑 | sync脚本从YAML单向写入 | 运行时自动写入 |
| AI消费 | 直接Read | Python查询 | Python查询 |

**不存在"双栖"问题**：YAML存"规则说什么"，depgraph.db存"规则关联谁"，governance.db存"规则执行了没"。三者不重叠。

<details>
<summary>E6.1 原裁定（已推翻）及推翻原因</summary>

原E6裁定：DB为唯一真源，YAML/MD为从DB单向生成的只读产物。

推翻原因：
1. AI消费路径3步（DB→生成YAML→Read），生成步骤失败=AI读到过期规则
2. 违反Policy as Code行业共识
3. 生成步骤是漂移温床
4. 100% AI开发项目的瓶颈是上下文效率，不是查询速度

</details>

### 规则与模块的关系（四层）

| 关系层 | 含义 | 存储位置 |
|--------|------|---------|
| 1. 约束关系 | 规则约束模块的行为 | edges表 dep_type='constrains' |
| 2. 触发关系 | 操作触发规则检查 | rule_bindings表 |
| 3. 执行关系 | 代码执行器强制规则 | YAML enforcement字段 + nodes表 |
| 4. 发现关系 | AI如何找到适用规则 | RuleLoader查DB→Read YAML |

---

## E7：depgraph.db升级设计

<details>
<summary>E7.1~E7.5 depgraph.db DDL升级详情（设计完成，待实施）</summary>

### nodes表升级（20核心字段，当前DDL仅12列）

新增字段：granularity, subdomain_id, belongs_to, owner, file_header_score, tags(JSON), architecture_layer, trust_zone, license, drive_direction, type_specific_data(JSON)

字段重命名：stability→change_policy, safety_level→impact_level, ai_autonomy→modification_permission, design_state→design_maturity, runtime_state→deployment_lifecycle

### edges表升级（16字段，当前DDL仅6列）

新增字段：architecture_direction, used_symbol, invocation_method, api_contract_refs(JSON), event_ref, ddd_integration_pattern, failure_mode, fallback, activation_condition, data_transfer_description, resource_impact, relationship_type

字段重命名：strength→coupling_strength, edge_type→dep_type

### rule_bindings表（新增）

```sql
CREATE TABLE rule_bindings (
    binding_id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    binding_type TEXT NOT NULL,  -- pre_check / post_check / enforcement
    trigger_type TEXT NOT NULL,  -- operation / skill / gate
    trigger_id TEXT,
    FOREIGN KEY (rule_id) REFERENCES nodes(node_id)
);
```

### depgraph.db升级后总表：15表

| 表组 | 表数 | 表名 |
|------|:---:|------|
| dep_ | 7 | domains, nodes(升级), edges(升级), domain_dependencies, contracts, domain_events, invariants |
| arch_ | 7 | arch_domain_capacity, arch_path_mappings, arch_layers, arch_domain_layers, arch_constraints, arch_directory_tree, arch_bottlenecks |
| rule_ | 1 | rule_bindings |

</details>

---

## E8~E9：架构裁定汇总

| # | 裁定 | 理由 |
|---|------|------|
| 1 | **YAML文件是规则内容SSoT** | Policy as Code；AI直接Read；无生成步骤=无漂移 |
| 2 | **depgraph.db仅存索引+关系** | nodes表只存rule_id+path→指向YAML |
| 3 | **governance.db存执行日志** | append-only运营数据 |
| 4 | **同步=单向索引** | sync_rule_registry.py读YAML→写DB，方向不可逆 |
| 5 | **rule_bindings从YAML triggers字段同步** | 不需要单独维护 |
| 6 | **不做执行拦截** | AI是外部LLM无法拦截；靠加载+校验双保险 |
| 7 | **功能绑定为核心** | 规则是功能的契约；功能激活→规则自动加载 |

---

## E10：目录结构、命名规范

### 目录结构

**扁平目录** `docs/01_policies_and_standards/rules/`（不按域分目录）。规则全部是AI工作规则，按域分目录误暗示规则只适用于某域。AI通过`_index.yaml`或depgraph.db查询定位，目录结构对AI消费无影响。

### 命名规范

| 规范项 | 规则 | 示例 |
|--------|------|------|
| 文件名格式 | `{domain_lower}_{number_padded}.yaml` | `trae_001_file_operation_security.yaml` |
| 大小写 | 全小写 | ✅ `trae_001` ❌ `TRAE_001` |
| 分隔符 | 下划线 | ✅ `trae_001` ❌ `trae-001` |
| 编号补零 | TRAE补3位，其余补2位 | `trae_001`, `abs_01` |

---

## E11：已知问题与待办

| # | 问题 | 优先级 | 状态 |
|---|------|:---:|:---:|
| 1 | GOV-MOD-007编码损坏（中文乱码） | P1 | ⏳ 待修复 |
| 2 | 68个MD文件深度YAML化（49种内容类型全量提取） | P0 | 🔄 进行中 |
| 3 | MD文件删除（YAML化完成后） | P1 | ⏳ 待执行 |
| 4 | RuleLoader/Skill/Gate集成待开发 | P2 | ⏳ |
| 5 | 十字段解析器待开发 | P2 | ⏳ |
| 6 | project_rules.md是否改为YAML生成物 | P2 | ⏳ 待决 |

---

## 总结

| 项目 | 方案 | 状态 |
|------|------|:---:|
| **内容SSoT** | 结构化YAML文件（53个） | ✅ 已创建 |
| **关系索引** | depgraph.db（nodes/edges/rule_bindings） | ✅ DDL已设计 |
| **执行日志** | governance.db（rule_enforcement_log） | ✅ DDL已设计 |
| **同步方向** | YAML→depgraph.db（单向索引） | ✅ |
| **目录结构** | 扁平目录 `docs/01_policies_and_standards/rules/` | ✅ |
| **命名规范** | `{domain_lower}_{number_padded}.yaml` | ✅ |
| **合并去重** | 135条→53个YAML，按AI操作分组合并 | ✅ |
| **安全协议** | 三锁一验，6维验证ALL PASS | ✅ |
| **内容类型清查** | 49种类型，26种YAML推荐，14种MD推荐 | ✅ |
| **深度覆盖核对** | 第一轮偏重A类规则，B~I类需补充 | 🔄 进行中 |
| **MD文件删除** | 待深度覆盖核对完成后决定 | ⏳ |
| **系统集成** | RuleLoader/Skill/Gate/十字段解析器 | ⏳ 待开发 |
