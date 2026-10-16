---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-5
excavated: 2026-10-15
ttl: task_bound
---

# NAV-5 施工（nav 七段导航之五：双面门禁 pre-commit+CI）

## 1. 定义

按蓝图施工（写代码/写规则/写脚本），代码产出必须通过两部分门禁：①编写时（pre-commit）→②推送前（CI governance.yml）。
SSOT：`config/nav_table_mapping.yaml#seven_stages⑤`。
（注：施工闭环的 15 步编排真源在 construction_workflow_policy.md——骨架 §2.7 D14 承载，本段为治理文档管线视角，两者正交。）。

## 2. 六向台账

### 2.1 输入面
- NAV-4 蓝图双件。
- check_items 十问：原子事务联动同批？新建 .py 注册 script-manifest？改 src 同步测试跑通全量？index.md 更新？枚举同步（§6.13）？蓝图§16 更新？删除质量对比预检（§6.6）？GOV-AI-003 幻觉自检 6 项？GOV-AI-004 编辑器配置？PS-STD-003 ABS 48 条？

### 2.2 输出面
- 代码/规则/脚本产出（过双面门禁）→ NAV-6 验收。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[4]。
- PS-STD-003→`docs/01_policies_and_standards/rules/trae_021_behavior_other_prohibition.yaml`（实存）。
- GOV-AI-003→`docs/01_policies_and_standards/rules/trae_039_ai_hallucination_detection.yaml`（实存）。
- GOV-AI-004→`docs/01_policies_and_standards/rules/trae_040_ai_model_routing.yaml`（实存）。
- GOV-DOC-005→`docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml`（实存）。

### 2.4 代码模块
- scripts 声明 4 项，核验（2026-10-15）：
  - "pre-commit 全量（GATE-01~18+SQ+ADM+IDX+DD07）"——通道实存（`src/zephyr/gov_enforcement/commit_gates/`、rule_enforcement 门禁引擎实存；gate 双册=in_process_gate_registry 107 台+gate_registry 191 台，骨架口径）。
  - `scripts/governance/d7_code/validate_test_coverage.py`（实存）。
  - `scripts/governance/d1_structure/validate_index_reality.py`（实存）。
  - `scripts/governance/d3_metadata/validate_enum_consistency.py`——**活树零命中**，唯一实体=`scripts/_archive/governance/d3_metadata/validate_enum_consistency.py`（已归档）。
- manual_files：`docs/01_policies_and_standards/rules/encoding_safety_standard.md`——**全仓 find 零命中**（docs/scripts 均无）；编码安全内容真源实际由 GOV-DOC-005→trae_028 YAML 承接。

### 2.5 门禁约束
- 双面门禁本体：pre-commit（in-process 门禁链+shell 门禁通道，图11 D11-C05/C07 承载）+CI（`.github/workflows/governance.yml` 实存）。
- 本段即门禁密度最高段：GATE-01~18+SQ+ADM+IDX+DD07 通道语义与宪法 §1 十二硬规则在 commit 面交汇。

### 2.6 自动化触发
- pre-commit 逐 commit 触发；CI push 触发全量回归；三校验器由 run_all.py 编排。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | NAV-4 交接+十问 check_items 在册 |
| 输出面 | pass | 产出→NAV-6 |
| SSOT 真源 | pass | 五件规则 YAML 全实存 |
| 代码模块 | warn | 4 scripts 中 1 件归档（validate_enum_consistency.py）+1 manual_files 死指针（encoding_safety_standard.md）；主通道（pre-commit+2 校验器+CI）实存 |
| 门禁约束 | pass | 双面门禁实存且为全链最密段 |
| 自动化触发 | pass | pre-commit/CI/run_all 三通道实证 |

## 4. 缺口与建议

- 两件死指针建议同批修：validate_enum_consistency.py 替换为现行枚举一致性守卫（d3_metadata 现役校验器或 GATE 通道），encoding_safety_standard.md 删除或改为 trae_028 指针。
- 与 NAV-2 同型病：scripts 字段值逃逸断链扫描（G 维只扫路径格式引用）——建议 nav 表 scripts 字段路径化，纳入机检。
