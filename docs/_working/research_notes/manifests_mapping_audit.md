# manifests_mapping_audit.md — STEP 1 映射表

> 日期：2026-07-04 | 总数：42 | 配套：[manifests_missing_diagnosis.md](manifests_missing_diagnosis.md) · [manifests_cure_plan.md](manifests_cure_plan.md) · [c_class_modules_audit.md](c_class_modules_audit.md)
> 数据源：git 历史 `f9a9ffc6b7^`（删除前版本）+ 当前 `docs/03_modules/**/blueprint.md`（55 个）

## 分类统计

### 第一轮复核（基于 frontmatter + 语义别名表）

| 类型 | 数量 | 含义 |
|------|------|------|
| A（名称直接匹配） | 13 | manifest_name == blueprint 子目录名 |
| B（语义别名/ssot反查） | 26 | 命名不一致但可通过 diagnosis.md 核对或 ssot_path 反查 |
| C（无 blueprint） | 3 | hooks / infra_ops / script_system |
| D（孤儿） | 0 | — |
| 合计 | 42 | |

### 第二轮二次复核（基于源码头部声明 `# [BLUEPRINT] MOD-XXX | <path>`）—— 最终

| 类型 | 数量 | 变化 |
|------|------|------|
| A | 13 | 不变 |
| B | **29** | +3（hooks + script_system + infra_ops 从 C 改为 B） |
| C | **0** | -3（全部误判，详见 [c_class_modules_audit.md](c_class_modules_audit.md)） |
| D | 0 | 不变 |

**最终结论**：42 个 manifest 全部能找到归属，无真正的 C 类或 D 类。

## 映射表（42 行，精简视图）

> 完整字段（含 fm_module_id/fm_blueprint_id/fm_ssot_path/fm_title/fm_generated_at）见文末 CSV 代码块。

| # | manifest_name | 类别 | blueprint_path | basis |
|---|---------------|:----:|---------------|------|
| 1 | a2a | B | _domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | diagnosis.md: a2a→a2a_protocol |
| 2 | agent_rbac | B | _domain_autonomy_core/agent_role_based_access_control/blueprint.md | diagnosis.md: agent_rbac→agent_role_based_access_control |
| 3 | agent_spec | A | _domain_autonomy_core/agent_spec/blueprint.md | name_direct_match |
| 4 | asset_inventory | A | _domain_infrastructure_operations/asset_inventory/blueprint.md | name_direct_match |
| 5 | audit_trail | A | _domain_governance/audit_trail/blueprint.md | name_direct_match |
| 6 | behavioral_auditor | A | _cross_layer/behavioral_auditor/blueprint.md | name_direct_match |
| 7 | budget_enforcer | A | _domain_autonomy_perm/budget_enforcer/blueprint.md | name_direct_match |
| 8 | capacity_assurance | A | _domain_infrastructure_operations/capacity_assurance/blueprint.md | name_direct_match |
| 9 | code_dedup_engine | A | _domain_governance/code_dedup_engine/blueprint.md | name_direct_match |
| 10 | compliance | B | _domain_compliance/blueprint.md | ssot_path=src/zephyr/compliance |
| 11 | context_engine | A | _cross_layer/context_engine/blueprint.md | name_direct_match |
| 12 | contracts | B | _cross_layer/shared_core/blueprint.md | diagnosis.md: contracts→shared_core |
| 13 | core | B | _cross_layer/shared_core/blueprint.md | diagnosis.md: core→shared_core |
| 14 | data | B | _domain_data/blueprint.md | ssot_path=src/zephyr/data |
| 15 | db | B | _cross_layer/database/blueprint.md | diagnosis.md: db→database |
| 16 | drift_detector | A | _domain_governance/drift_detector/blueprint.md | name_direct_match |
| 17 | escalation | B | _domain_autonomy_perm/escalation_protocol/blueprint.md | diagnosis.md: escalation→escalation_protocol |
| 18 | ex_core | B | _domain_execution_core/blueprint.md | ssot_path=src/zephyr/trading |
| 19 | factor | B | _domain_factor/blueprint.md | ssot_path=src/zephyr/factor |
| 20 | feedback_loop | A | _cross_layer/feedback_loop/blueprint.md | name_direct_match |
| 21 | frontend | B | _domain_frontend/blueprint.md | ssot_path=src/zephyr/frontend |
| 22 | gates | B | _cross_layer/gate_engine/blueprint.md | diagnosis.md: gates→gate_engine |
| 23 | governance | B | _domain_governance/blueprint.md | 域级 manifest，blueprint_id=MOD-GOVERNANCE 正确 |
| 24 | hooks | C→B* | _domain_infrastructure_runtime/runtime_integration/blueprint.md | 二次复核: 头部声明归并 MOD-INF-002 |
| 25 | infra_ops | C→B* | _domain_infrastructure_runtime/runtime_integration/blueprint.md | 二次复核: layer=infra_ops 由 runtime_integration 代理 |
| 26 | kb | B | _domain_knowledge/knowledge_base/blueprint.md | diagnosis.md: kb→knowledge_base |
| 27 | llm_security | B | _cross_layer/large_language_model_security/blueprint.md | diagnosis.md: llm_security→large_language_model_security |
| 28 | mcp | B | _cross_layer/model_context_protocol_servers/blueprint.md | diagnosis.md: mcp→model_context_protocol_servers |
| 29 | orchestrator | B | _cross_layer/agent_orchestrator/blueprint.md | diagnosis.md: orchestrator→agent_orchestrator |
| 30 | pf_core | B | _domain_portfolio_core/blueprint.md | ssot_path=src/zephyr/pf_core |
| 31 | pipeline | A | _cross_layer/pipeline/blueprint.md | name_direct_match |
| 32 | red_blue_validator | A | _cross_layer/red_blue_validator/blueprint.md | name_direct_match |
| 33 | reporting | B | _domain_reporting/blueprint.md | ssot_path=src/zephyr/reporting |
| 34 | research | B | _domain_research/blueprint.md | ssot_path=src/zephyr/research |
| 35 | risk | B | _domain_risk/blueprint.md | ssot_path=src/zephyr/risk |
| 36 | rollback | B | _domain_autonomy_core/rollback_system/blueprint.md | diagnosis.md: rollback→rollback_system |
| 37 | runtime | B | _cross_layer/auto_runtime_core/blueprint.md | diagnosis.md: runtime→auto_runtime_core |
| 38 | script_system | C→B* | _domain_governance/governance_automation/blueprint.md | 二次复核: 头部声明归并 MOD-INF-005（但 5 处路径漂移） |
| 39 | shared | B | _cross_layer/shared_core/blueprint.md | diagnosis.md: shared→shared_core |
| 40 | simulation | B | _domain_simulation/blueprint.md | ssot_path=src/zephyr/simulation |
| 41 | telemetry | B | _domain_infrastructure_operations/system_telemetry/blueprint.md | ssot_path=src/zephyr/observability/telemetry |
| 42 | vector_memory | A | _domain_knowledge/vector_memory/blueprint.md | name_direct_match |

> *C→B：第一轮标 C，第二轮二次复核（基于源码头部声明）修正为 B。详见 [c_class_modules_audit.md](c_class_modules_audit.md)。
> blueprint_path 省略 `docs/03_modules/` 前缀以提升可读性，完整路径见 CSV 代码块。

## CSV 数据（机器可读，完整字段）

```csv
manifest_file,manifest_name,fm_module_id,fm_blueprint_id,fm_ssot_path,fm_title,fm_generated_at,category,blueprint_path,basis
a2a_manifest.md,a2a,MOD-041,MOD-GOVERNANCE,,A2A.Manifest,,B,docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md,diagnosis.md: a2a→a2a_protocol（命名简写）
agent_rbac_manifest.md,agent_rbac,MOD-042,MOD-GOVERNANCE,,Agent Rbac.Manifest,,B,docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md,diagnosis.md: agent_rbac→agent_role_based_access_control
agent_spec_manifest.md,agent_spec,MOD-043,MOD-GOVERNANCE,,Agent Spec.Manifest,,A,docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md,name_direct_match
asset_inventory_manifest.md,asset_inventory,MOD-044,MOD-GOVERNANCE,,Asset Inventory.Manifest,,A,docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md,name_direct_match
audit_trail_manifest.md,audit_trail,MOD-045,MOD-GOVERNANCE,,Audit Trail.Manifest,,A,docs/03_modules/_domain_governance/audit_trail/blueprint.md,name_direct_match
behavioral_auditor_manifest.md,behavioral_auditor,MOD-046,MOD-GOVERNANCE,,Behavioral Auditor.Manifest,,A,docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md,name_direct_match
budget_enforcer_manifest.md,budget_enforcer,MOD-047,MOD-GOVERNANCE,,Budget Enforcer.Manifest,,A,docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md,name_direct_match
capacity_assurance_manifest.md,capacity_assurance,MOD-048,MOD-GOVERNANCE,,Capacity Assurance.Manifest,,A,docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md,name_direct_match
code_dedup_engine_manifest.md,code_dedup_engine,MOD-049,MOD-GOVERNANCE,,Code Dedup Engine.Manifest,,A,docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md,name_direct_match
compliance_manifest.md,compliance,,MOD-GOVERNANCE,src/zephyr/compliance,,,B,docs/03_modules/_domain_compliance/blueprint.md,ssot_path=src/zephyr/compliance → 域级 _domain_compliance
context_engine_manifest.md,context_engine,MOD-050,MOD-GOVERNANCE,,Context Engine.Manifest,,A,docs/03_modules/_cross_layer/context_engine/blueprint.md,name_direct_match
contracts_manifest.md,contracts,MOD-051,MOD-GOVERNANCE,,Contracts.Manifest,,B,docs/03_modules/_cross_layer/shared_core/blueprint.md,diagnosis.md: contracts→shared_core（contracts_blueprint.md 在 shared_core/ 下）
core_manifest.md,core,MOD-052,MOD-GOVERNANCE,,Core.Manifest,,B,docs/03_modules/_cross_layer/shared_core/blueprint.md,diagnosis.md: core→shared_core（core 是 shared_core 简写）
data_manifest.md,data,,MOD-GOVERNANCE,src/zephyr/data,,,B,docs/03_modules/_domain_data/blueprint.md,ssot_path=src/zephyr/data → 域级 _domain_data
db_manifest.md,db,MOD-053,MOD-GOVERNANCE,,Db.Manifest,,B,docs/03_modules/_cross_layer/database/blueprint.md,diagnosis.md: db→database
drift_detector_manifest.md,drift_detector,MOD-054,MOD-GOVERNANCE,,Drift Detector.Manifest,,A,docs/03_modules/_domain_governance/drift_detector/blueprint.md,name_direct_match
escalation_manifest.md,escalation,MOD-055,MOD-GOVERNANCE,,Escalation.Manifest,,B,docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md,diagnosis.md: escalation→escalation_protocol
ex_core_manifest.md,ex_core,,MOD-GOVERNANCE,src/zephyr/trading,,,B,docs/03_modules/_domain_execution_core/blueprint.md,ssot_path=src/zephyr/trading → 域级 _domain_execution_core
factor_manifest.md,factor,,MOD-GOVERNANCE,src/zephyr/factor,,,B,docs/03_modules/_domain_factor/blueprint.md,ssot_path=src/zephyr/factor → 域级 _domain_factor
feedback_loop_manifest.md,feedback_loop,MOD-056,MOD-GOVERNANCE,,Feedback Loop.Manifest,,A,docs/03_modules/_cross_layer/feedback_loop/blueprint.md,name_direct_match
frontend_manifest.md,frontend,,MOD-GOVERNANCE,src/zephyr/frontend,,,B,docs/03_modules/_domain_frontend/blueprint.md,ssot_path=src/zephyr/frontend → 域级 _domain_frontend
gates_manifest.md,gates,MOD-057,MOD-GOVERNANCE,,Gates.Manifest,,B,docs/03_modules/_cross_layer/gate_engine/blueprint.md,diagnosis.md: gates→gate_engine
governance_manifest.md,governance,MOD-058,MOD-GOVERNANCE,,Governance.Manifest,,B,docs/03_modules/_domain_governance/blueprint.md,域级 manifest，blueprint_id=MOD-GOVERNANCE 正确指向域级蓝图
hooks_manifest.md,hooks,MOD-059,MOD-GOVERNANCE,,Hooks.Manifest,,C,,C类（第一轮）→B类（二次复核: 归并 MOD-INF-002 runtime_integration）
infra_ops_manifest.md,infra_ops,,MOD-GOVERNANCE,src/zephyr/infrastructure,,,C,,C类（第一轮）→B类（二次复核: layer=infra_ops 由 runtime_integration 代理）
kb_manifest.md,kb,MOD-060,MOD-GOVERNANCE,,Kb.Manifest,,B,docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md,diagnosis.md: kb→knowledge_base
llm_security_manifest.md,llm_security,MOD-061,MOD-GOVERNANCE,,Llm Security.Manifest,,B,docs/03_modules/_cross_layer/large_language_model_security/blueprint.md,diagnosis.md: llm_security→large_language_model_security
mcp_manifest.md,mcp,MOD-062,MOD-GOVERNANCE,,Mcp.Manifest,,B,docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md,diagnosis.md: mcp→model_context_protocol_servers
orchestrator_manifest.md,orchestrator,MOD-063,MOD-GOVERNANCE,,Orchestrator.Manifest,,B,docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md,diagnosis.md: orchestrator→agent_orchestrator
pf_core_manifest.md,pf_core,,MOD-GOVERNANCE,src/zephyr/pf_core,,,B,docs/03_modules/_domain_portfolio_core/blueprint.md,ssot_path=src/zephyr/pf_core → 域级 _domain_portfolio_core
pipeline_manifest.md,pipeline,MOD-064,MOD-GOVERNANCE,,Pipeline.Manifest,,A,docs/03_modules/_cross_layer/pipeline/blueprint.md,name_direct_match
red_blue_validator_manifest.md,red_blue_validator,MOD-065,MOD-GOVERNANCE,,Red Blue Validator.Manifest,,A,docs/03_modules/_cross_layer/red_blue_validator/blueprint.md,name_direct_match
reporting_manifest.md,reporting,,MOD-GOVERNANCE,src/zephyr/reporting,,,B,docs/03_modules/_domain_reporting/blueprint.md,ssot_path=src/zephyr/reporting → 域级 _domain_reporting
research_manifest.md,research,,MOD-GOVERNANCE,src/zephyr/research,,,B,docs/03_modules/_domain_research/blueprint.md,ssot_path=src/zephyr/research → 域级 _domain_research
risk_manifest.md,risk,,MOD-GOVERNANCE,src/zephyr/risk,,,B,docs/03_modules/_domain_risk/blueprint.md,ssot_path=src/zephyr/risk → 域级 _domain_risk
rollback_manifest.md,rollback,MOD-066,MOD-GOVERNANCE,,Rollback.Manifest,,B,docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md,diagnosis.md: rollback→rollback_system
runtime_manifest.md,runtime,MOD-067,MOD-GOVERNANCE,,Runtime.Manifest,,B,docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md,diagnosis.md: runtime→auto_runtime_core
script_system_manifest.md,script_system,MOD-068,MOD-GOVERNANCE,,Script System.Manifest,,C,,C类（第一轮）→B类（二次复核: 归并 MOD-INF-005 governance_automation，但 5 处路径漂移）
shared_manifest.md,shared,MOD-069,MOD-GOVERNANCE,,Shared.Manifest,,B,docs/03_modules/_cross_layer/shared_core/blueprint.md,diagnosis.md: shared→shared_core
simulation_manifest.md,simulation,,MOD-GOVERNANCE,src/zephyr/simulation,,,B,docs/03_modules/_domain_simulation/blueprint.md,ssot_path=src/zephyr/simulation → 域级 _domain_simulation
telemetry_manifest.md,telemetry,,MOD-GOVERNANCE,src/zephyr/observability/telemetry,,,B,docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md,ssot_path=src/zephyr/observability/telemetry → 模块 system_telemetry
vector_memory_manifest.md,vector_memory,MOD-070,MOD-GOVERNANCE,,Vector Memory.Manifest,,A,docs/03_modules/_domain_knowledge/vector_memory/blueprint.md,name_direct_match
```
