---
module_id: AUDIT_BLUEPRINT_D_OVERLAP_TRIAGE_20260412
standard_type: audit_state
generated_by: scripts/governance/triage_blueprint_d_overlap_pairs.py
source_overlap_json: 'BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json'
---

# 蓝图 D 类重叠 — A 档分流摘要（`20260412`）

> **输入**：`docs/09_AUDIT/STATE/BLUEPRINT_D_OVERLAP_CANDIDATES_20260412.json`
> **二审提示词模板**：[D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/D_CLASS_OVERLAP_SECOND_PASS_PROMPT_TEMPLATE.md)

## 统计

- 候选对数：**400**
- 写入二审队列（JSONL）行数：**400**（`queue_mode=all`）

### triage_tier

- `DUAL_ACTIVE`: **353**
- `DUAL_CABINET`: **32**
- `MIXED`: **9**
- `DUAL_ARCHIVE`: **3**
- `BLUEPRINTS_VS_ARCHIVE`: **3**

### second_pass_priority（写入 JSONL 的分布）

- `HIGH`: **385**
- `MEDIUM`: **12**
- `LOW`: **3**

## 产出文件

- [`BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json`](./BLUEPRINT_D_OVERLAP_TRIAGE_20260412.json)
- [`BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl`](./BLUEPRINT_D_OVERLAP_SECOND_PASS_QUEUE_20260412.jsonl)
