# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-15 00:49:36
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=163 / dataflow=192 / decision=323 / blueprint=75
- 问题总数: 5
  - 孤儿（仅一图）: 3
  - 状态漂移（blueprint 缺 design_maturity）: 1
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 1

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| MOD-004 | blueprint | _cross_layer/_b_track_interfaces/feedback_loop_engine_interface.md |
| MOD-GOV-ALIGNMENT-LOOP | blueprint | _domain_governance/alignment_loop/blueprint.md |
| MOD-BIZ-002 | decision | layer:MOD-BIZ-002 |

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

| module_id | depgraph | dataflow | decision | blueprint |
|---|---|---|---|---|
| MOD-004 | - | - | - | - |

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

| module_id | graph | entity_name |
|---|---|---|
| MOD-GOV-ALIGNMENT-LOOP | blueprint | _domain_governance/alignment_loop/blueprint.md |

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
