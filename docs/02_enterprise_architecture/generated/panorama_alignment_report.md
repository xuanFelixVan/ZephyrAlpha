# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-18 19:53:14
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=169 / dataflow=25 / decision=319 / blueprint=72
- 问题总数: 17
  - 孤儿（仅一图）: 17
  - 状态漂移（blueprint 缺 design_maturity）: 0
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 0

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| MOD-AUTONOMY_PERM | decision | layer:MOD-AUTONOMY_PERM |
| MOD-GOV_DRIFT_bridges | decision | layer:MOD-GOV_DRIFT_bridges |
| MOD-GOV_DRIFT_det_bridge | decision | layer:MOD-GOV_DRIFT_det_bridge |
| MOD-GOV_DRIFT_detector_core | decision | layer:MOD-GOV_DRIFT_detector_core |
| MOD-SECURITY | decision | layer:MOD-SECURITY |
| MOD-SECURITY-LLM | decision | layer:MOD-SECURITY-LLM |
| MOD-TRADING | decision | layer:MOD-TRADING |
| MOD-GOV-029 | depgraph | scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py |
| MOD-GOV-blueprint_amodule_consistency_gate | depgraph | tests/governance/commit_gates/test_blueprint_amodule_consistency_gate.py |
| MOD-GOV-domain_fk_gate | depgraph | tests/governance/commit_gates/test_domain_fk_gate.py |
| MOD-GOV-no_import_side_effect_gate | depgraph | tests/governance/commit_gates/test_no_import_side_effect_gate.py |
| MOD-GOV-reconciliation_registry | depgraph | tests/governance/audit/test_blueprint_frontmatter_reconciler_post_commit.py |
| MOD-GOV-rename_depgraph_sync_gate | depgraph | tests/governance/commit_gates/test_rename_depgraph_sync_gate.py |
| MOD-GOV-ruling_reference_gate | depgraph | tests/governance/commit_gates/test_ruling_reference_gate.py |
| MOD-GOV_DQ | depgraph | scripts/governance/data_quality/check_tick_duplication.py |
| MOD-INF-040 | depgraph | src/zephyr/signal_quality/__init__.py |
| MOD-SEC-immutable_core | depgraph | config/immutable_core.yaml |

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

> 无状态漂移。

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

> 无设计态孤立。

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
