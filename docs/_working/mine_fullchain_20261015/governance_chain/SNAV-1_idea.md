---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-1
excavated: 2026-10-15
ttl: task_bound
---

# NAV-1 想法（nav 七段导航之一：问题→目标→约束）

## 1. 定义

治理文档管线七段的思维起点：记录碎片想法，明确问题定义。
SSOT：`config/nav_table_mapping.yaml#seven_stages①`（module_id=MOD-INF-002，v1.1.0；
宿主蓝图=`docs/03_modules/_domain_governance/governance_automation/blueprint.md` 实存）。
注意：该文件头注自declared 2026-08-17 AI-02 审计治本——原"生成器自动刷新"声明已失实纠偏（生成器已归档），本文件现为人工维护机读定义。

## 2. 六向台账

### 2.1 输入面
- Owner/提案（骨架口径）：碎片想法、问题陈述。
- 思维基线：PS-STD-011 总则（先判断最优方案，再检查规则约束）→
  `docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml`（实存）。

### 2.2 输出面
- 结构化想法卡（问题→目标→约束三要素）→ NAV-2 草稿。
- check_items 三问：三要素齐全？PS-STD-011 未来成本评估（§6.3 决策矩阵）？§3 专业框架映射表机构对标？

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[0]（实读）。
- methodology_files：PS-STD-011（trae_024 实存）、GOV-DOC-010 文档可发现性策略→
  `docs/01_policies_and_standards/rules/document_discovery_policy.md` **status: planned 未创建**（文件内自declared，P8-FIX-S0 约定）。

### 2.4 代码模块
- scripts: "人工"——本段无自动化脚本（设计内）。
- 段① rule_module_ids：PS-STD-011（实存）、GOV-DOC-010（planned）。

### 2.5 门禁约束
- 无硬门（人工思维段，设计内无 pre-commit 门覆盖想法期）。

### 2.6 自动化触发
- 无（人工段，设计内）。闭环入边：NAV-7 持续审计发现漂移后回流本段（MTH-015/MTH-006 追问根源）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | Owner/提案+PS-STD-011 基线实存 |
| 输出面 | pass | 三要素卡→NAV-2 语义清晰 |
| SSOT 真源 | pass | nav 表+宿主蓝图实存；planned 条目自declared 无伪引 |
| 代码模块 | pass | 纯人工段无代码依赖（设计内） |
| 门禁约束 | pass | 无门=设计内 |
| 自动化触发 | pass | 无触发=设计内 |

## 4. 缺口与建议

- GOV-DOC-010 政策文档 planned 未建：nav 表以 status: planned 显式防伪引（合规），但段①的 rule_module_ids 仍引用该 id——建议 planned 条目建成或从 check_items 降权，避免"引用一个不存在的规则"成为惯例。
- 全 nav 共 9 件 planned 政策文档（GOV-DOC-010/Gate Strategy/Phase Transition/GOV-ARCH-002/GOV-MOD-001/003/004/GOV-AI-008/GOV-CMP-002），建议一次打包裁定：建、并、或除名。
