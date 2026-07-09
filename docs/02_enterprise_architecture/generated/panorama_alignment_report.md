# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-09 19:34:40
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=140 / dataflow=165 / decision=296 / blueprint=110
- 问题总数: 48
  - 孤儿（仅一图）: 18
  - 状态漂移（design_maturity 不一致）: 8
  - 域不一致（domain_id 不一致）: 22
  - 设计态孤立（design 仅一图）: 0

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| ARCH-BIZDB-001 | blueprint | _cross_layer/database/business_data_architecture.md |
| C1-MARKET-CH | blueprint | _cross_layer/database/sub_blueprints/c1_market_clickhouse.md |
| GOV-AI-ENG-ORC-001 | blueprint | _cross_layer/_b_track_interfaces/agent_orchestrator_interface.md |
| GOV-AI-ENG-VMS-001 | blueprint | _cross_layer/_b_track_interfaces/vector_memory_service_interface.md |
| MOD-003 | blueprint | _cross_layer/_b_track_interfaces/context_engine_interface.md |
| MOD-013 | blueprint | _cross_layer/shared_core/contracts_blueprint.md |
| MOD-015 | blueprint | _cross_layer/shared_core/shared_infra_blueprint.md |
| MOD-DB_DEPGRAPH_PG | blueprint | _cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md |
| MOD-DB_DEPGRAPH_PG | blueprint | _cross_layer/database/sub_blueprints/mod_inf_012b_p2_task_cards.md |
| MOD-L00-002 | blueprint | _domain_data/data_source_capability_map.md |
| MOD-L00-002 | blueprint | _domain_data/data_source_operation_manual.md |
| MOD-L00-003 | blueprint | _domain_data/data_acquisition_plan.md |
| MOD-MASTER-001 | blueprint | _master_blueprint/blueprint_agent_spec.md |
| MOD-MASTER-002 | blueprint | _master_blueprint/blueprint_baseline.md |
| MOD-MASTER-003 | blueprint | _master_blueprint/blueprint_capacity.md |
| SYS-MASTER-001 | blueprint | _system_master/blueprint.md |
| MOD-GOV-ENFORCEMENT | decision | layer:MOD-GOV-ENFORCEMENT |
| MOD-GOV-tests_coverage_gate | decision | layer:MOD-GOV-tests_coverage_gate |

## 2. 状态漂移（design_maturity 不一致）

| module_id | depgraph | dataflow | decision | blueprint |
|---|---|---|---|---|
| MOD-INF-019 | design | production | production | design |
| MOD-INF-020 | design | prototype | prototype | design |
| MOD-INF-022 | design | prototype | prototype | design |
| MOD-L04-001 | prototype | prototype | design |  |
| MOD-L05-001 | prototype | prototype | design |  |
| MOD-L06-001 | design | prototype | prototype | design |
| MOD-LLM_SECURITY | prototype | production | production |  |
| MOD-SECURITY | prototype | production | production | - |

## 3. 域不一致（domain_id 不一致）

| module_id | depgraph | dataflow | decision | blueprint |
|---|---|---|---|---|
| MOD-CONTEXT_ENGINE | D_AUTONOMY_CORE | - | - | D_GOVERNANCE |
| MOD-FEEDBACK_LOOP | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-GATE_ENGINE | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-INF-005 | D_GOV_SCRIPTS | - | - | D_GOVERNANCE |
| MOD-INF-009 | D_INFRA_RUNTIME | - | - | D_GOVERNANCE |
| MOD-INF-011 | D_INTEGRATION | - | - | D_KNOWLEDGE |
| MOD-INF-016 | D_SHARED | - | - | D_GOVERNANCE |
| MOD-INF-019 | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-INF-020 | D_GOVERNANCE | - | - | D_GOV_AUDIT |
| MOD-INF-021 | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-INF-023 | D_GOVERNANCE | - | - | D_GOV_DRIFT |
| MOD-INF-027 | D_AUDITTEST | - | - | D_GOV_AUDIT |
| MOD-INF-029 | D_SECURITY | - | - | D_GOVERNANCE |
| MOD-INF-030 | D_SECURITY | - | - | D_GOVERNANCE |
| MOD-INF-031 | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-INF-033 | D_AUDITTEST | - | - | D_GOVERNANCE |
| MOD-INF-034 | D_INTELLIGENCE | - | - | D_ML_TRAIN |
| MOD-INF-035 | D_AUDITTEST | - | - | auto_runtime_core |
| MOD-INF-036 | D_INTELLIGENCE | - | - | D_GOVERNANCE |
| MOD-INF-039 | D_TRADING | - | - | agent_orchestrator |
| MOD-KB-001 | D_GOVERNANCE | - | - | D_KNOWLEDGE |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | D_TRADING | - | - | D_GOVERNANCE |

## 4. 设计态孤立（design 仅一图）

> 无设计态孤立。

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：以最成熟状态为准，统一更新（建议 production > prototype > design）
- 域不一致：核对真源并统一 domain_id
- 设计态孤立：评估设计态是否需要同步到另三图
