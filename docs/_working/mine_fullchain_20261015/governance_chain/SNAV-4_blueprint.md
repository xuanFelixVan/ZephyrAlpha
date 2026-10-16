---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-4
excavated: 2026-10-15
ttl: task_bound
---

# NAV-4 蓝图（nav 七段导航之四：YAML canonical+MD 视图）

## 1. 定义

将裁定结论写入蓝图（YAML canonical + MD 视图），遵守 PS-STD-002 标准文档模板（L1/L2/L3）；架构决策走 KB 决策记录。
SSOT：`config/nav_table_mapping.yaml#seven_stages④`。

## 2. 六向台账

### 2.1 输入面
- NAV-3 固化的裁定结论。
- check_items 七问：蓝图自包含？YAML canonical SSoT 先登记？§16 路径索引与磁盘一致？provenance 三件套（origin_drafts+audit_chain≥3+arbitration）？GOV-ARCH-002 架构评审触发？GOV-MOD-003 生命周期 8 阶段？接口契约注册 cross_layer_contracts.yaml（GOV-MOD-004）？

### 2.2 输出面
- 蓝图双件（YAML canonical+MD 视图）→ NAV-5 施工。
- 宿主范例：`docs/03_modules/_domain_governance/governance_automation/blueprint.md`（MOD-INF-002 蓝图，实存）。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[3]。
- PS-STD-002→`docs/01_policies_and_standards/rules/trae_042_meta_rule_standard.yaml`（实存）。
- GOV-ARCH-001→"KB:namespace=decisions"（33 ADRs 已迁 KB，原 adr-protocol.md 已删除——nav 自declared；KB 命名空间为运行时面，磁盘不可直接 ls，登记为口径注记）。
- GOV-ARCH-002/GOV-MOD-003/GOV-MOD-004 三件 policy 文档 status: planned 未创建（文件内自declared）。

### 2.4 代码模块
- 三校验器全实存核验（2026-10-15）：
  `scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_code_sync.py`、
  `scripts/governance/d3_metadata/validate_blueprint_provenance.py`、
  `scripts/governance/d5_architecture/validators/validate_code_yaml_alignment.py`。
- 手册件：`docs/01_policies_and_standards/templates/blueprint_construction_template.md`（实存）。

### 2.5 门禁约束
- 蓝图落档后受断链（G 维）/蓝图-代码同步（F 维）审计维覆盖；§16 路径索引由 validate_blueprint_code_sync 扫描。
- 涉及架构决策须触发 GOV-ARCH-002 评审（政策文档 planned，触发语义在 nav 行动列人工执行）。

### 2.6 自动化触发
- 三校验器为 run_all.py/CI（.github/workflows/governance.yml，实存）编排的 push/手动触发面。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | NAV-3 交接+provenance 语义在册 |
| 输出面 | pass | 双件蓝图→NAV-5，宿主范例实存 |
| SSOT 真源 | warn | check_items 引用的 3 件政策文档（GOV-ARCH-002/GOV-MOD-003/GOV-MOD-004）planned 未建；GOV-ARCH-001 为 KB 面磁盘不可核 |
| 代码模块 | pass | 三校验器+模板全实存 |
| 门禁约束 | pass | F/G 审计维+校验器覆盖 |
| 自动化触发 | pass | run_all/CI 编排实证 |

## 4. 缺口与建议

- planned 三件为 NAV-4 核验项的判据真源缺口：验收项"是否符合 GOV-MOD-003 生命周期"目前无政策可对照——建议随 §4（全 nav 9 件 planned）统一打包裁定。
- cross_layer_contracts.yaml（GOV-MOD-004 契约注册表）存在性未在本批核验，建议 NAV-4 深挖时补核。
