---
doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-7
excavated: 2026-10-15
ttl: task_bound
---

# NAV-7 持续审计（nav 七段导航之七：漂移→追问根源→闭环回流 NAV-1）

## 1. 定义

定期/触发式全量审计（push→CI / 手动→run_all.py），发现漂移→§6.15 漂移免疫自检→追问"为什么漂移没被拦截"→治根而非治标→回流 NAV-1 闭环。
SSOT：`config/nav_table_mapping.yaml#seven_stages⑦`。

## 2. 六向台账

### 2.1 输入面
- NAV-6 验收合格的全仓现状 + CI/run_all 审计结果流。
- check_items 五问：D1~D12 十二维零漂移？漂移→MTH-015 漂移免疫自检+MTH-006 追问根源？治根？Session Log 交接？审计日志完整（GOV-CMP-002 AUD-001~004）？
- 十维审计框架（audit_dimensions A~J）：责任单一/真源清晰/内容无冲突/文件夹职责/无废话/蓝图-代码同步/链接完整/安全红线/代码质量/文档同步——每维配 script_names 清单（d1~d12 脚本族），mantra 十问与维一一对应。

### 2.2 输出面
- 漂移清单/根源分析 → 回流 NAV-1（闭环边，nav 表内 stage⑦→①）。
- 审计脚本体系总入口：`scripts/governance/index.md`（实存）+`scripts/governance/quality_standard.md`（实存）。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[6]+audit_dimensions 全块。
- PS-STD-012 规则验证标准→`docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml`（实存，V1~V4 四级验证）。
- GOV-CMP-002 审计追踪策略→`docs/01_policies_and_standards/governance/compliance/audit_trail_policy.md` **planned 未创建**（自declared）。

### 2.4 代码模块
- `scripts/governance/run_all.py`（实存）+`.github/workflows/governance.yml`（实存）。
- audit_dimensions 声明的脚本族抽验（本批）：`d5_architecture/validators/blueprint/validate_blueprint_code_sync.py`、
  `d5_architecture/validators/validate_code_yaml_alignment.py`、`d3_metadata/validate_blueprint_provenance.py`（实存）；
  G 维 `d2_links/audit_broken_links.py`、E 维 `d1_structure/detect_temp_files.py` 等 d1~d12 族未逐一核验（族级抽验口径）。
- 本批实证的扫描盲区：audit_dimensions G 维只扫路径格式引用——nav 表 scripts 字段的裸标识符引用（如 scan_deep_content.py）
  逃逸断链检测（NAV-2/NAV-5 两案在卷）。

### 2.5 门禁约束
- 审计发现回流立法：硬规则修订走图16 立法流（裁定→规则 YAML→gate），本段是立法流的需求侧入口。
- CI 为 push 触发的最后防线（NAV-5 双面门禁的第二面）。

### 2.6 自动化触发
- push→CI 全量回归；手动→run_all.py；无本段专属定时器（持续审计靠事件触发，与宪法 §9.3 禁 cron 口径一致）。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | CI/run_all 结果流+十二维框架在册 |
| 输出面 | pass | 闭环回流 NAV-1 边在册 |
| SSOT 真源 | warn | GOV-CMP-002 audit_trail_policy.md planned——审计日志判据（AUD-001~004）真源缺位 |
| 代码模块 | pass | run_all/CI/quality_standard/index 全实存；d1~d12 族抽验通过 |
| 门禁约束 | pass | CI 最后防线+立法回流边 |
| 自动化触发 | pass | push/手动双触发，无违禁定时器 |

## 4. 缺口与建议

- audit_trail_policy.md 建议随 9 件 planned 打包裁定（审计段唯一判据缺位，与 NAV-6 同优先级）。
- G 维断链扫描盲区：建议扩展 d2_links 扫描范围至 YAML 列表值中的标识符型引用（scripts/rule_module_ids 字段），把 NAV-2/NAV-5 型死指针纳入机检。
- 十二维脚本族完整存在性核验（60+ 脚本）超出本环节半日清口径，建议独立小批核查。
