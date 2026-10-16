---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-2
excavated: 2026-10-15
ttl: task_bound
---

# NAV-2 草稿（nav 七段导航之二：结构化+查重）

## 1. 定义

将想法写成结构化草稿（讨论型文档+scaffold 扫描盘点），遵守 DOC-001~008 文档控制 8 原则。
SSOT：`config/nav_table_mapping.yaml#seven_stages②`。

## 2. 六向台账

### 2.1 输入面
- NAV-1 产出的三要素想法卡。
- check_items 四问：专题讨论模板？5 个裁定维度覆盖？GOV-DOC-009 创建前必查（查重+查索引+查命名）？DOC-008 引用而非复制？

### 2.2 输出面
- 结构化草稿（讨论型文档）→ NAV-3 审计裁定。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[1]。
- GOV-DOC-009 文档控制原则→`docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml`（实存）。
- 宿主蓝图 `docs/03_modules/_domain_governance/governance_automation/blueprint.md`（实存）。

### 2.4 代码模块
- scripts 声明两项："人工" + `d3_metadata/scan_deep_content.py`。
- **实证失效**：`scripts/governance/d3_metadata/scan_deep_content.py` 在活树零命中（find 全仓），唯一实体=
  `scripts/_archive/governance/d3_metadata/scan_deep_content.py`（已归档）。nav 表未随归档更新指针。
- 查重职能的现行承接面（功能有替代，指针未更新）：宪法 RULE-CLONEGUARD（`clone_guard.check_before_write` 写前预查）、
  RULE-CAPABILITY-LOOKUP（`capability_lookup.find`）、CREATE-GUARD（creation_token 登记）——均已接棒查重/查重前置职责。

### 2.5 门禁约束
- 本段无 commit 级硬门（草稿期）；创建行为受 CREATE-GUARD（新建 .md 须登记 creation_token）与 GATE-SELFDOC 约束。

### 2.6 自动化触发
- 声明的扫描脚本已归档→本段自动化能力实际归零；现行自动化=宪法新规（clone_guard/capability_lookup）在写操作时触发。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | NAV-1 交接语义清晰 |
| 输出面 | pass | 草稿→NAV-3 |
| SSOT 真源 | pass | nav 表+trae_029 实存 |
| 代码模块 | fail | 唯一自动化脚本 scan_deep_content.py 已归档，声明路径活树零实体——机读配置指向不存在文件 |
| 门禁约束 | pass | CREATE-GUARD/CLONEGUARD 现行覆盖 |
| 自动化触发 | warn | 原自动化归零但职能由宪法新规接棒（替代通道存在），nav 表未回写 |

## 4. 缺口与建议

- 建议修订 `config/nav_table_mapping.yaml` stage② scripts：将 scan_deep_content.py 指针替换为现行查重入口
  （capability_lookup.find / clone_guard.check_before_write），或在 scripts 值中注记 archived+替代指针。
- 该失效与 nav 表头注"2026-08-17 AI-02 审计治本"同型（声明与磁盘漂移），建议把 nav 七段 scripts 字段纳入
  d2_links/audit_broken_links.py 类断链巡检范围（audit_dimensions G 维已有断链检测，覆盖 .md/.yaml 路径引用——
  scripts 字段值非路径格式，逃逸了 G 维扫描，属扫描盲区）。
