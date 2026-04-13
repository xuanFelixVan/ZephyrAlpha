---
module_id: DIRECTORY_NAMING_COMPLIANCE_20260412
version: 1.0.0
status: Active
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_09
responsibility: STATE
---



# 目录命名合规性扫描报告

> **生成脚本**: `scripts/governance/scan_directory_naming_compliance.py`
> **扫描日期**: 20260412

```
```---
```

## 扫描摘要

| 指标 | 数量 |
|------|------|
| 总目录数 | 372 |
| 包含中文 | 0 |
| 包含空格 | 0 |
| 包含特殊字符 | 3 |
| 缺少编号前缀 | 187 |
| 合规目录 | 184 |

## 包含特殊字符的目录

| 路径 | 目录名 |
|------|--------|
| `.audit_cache` | `.audit_cache` |
| `.github` | `.github` |
| `.trae` | `.trae` |

## 缺少编号前缀的目录

> **说明**: 以下目录未使用 2 位数字前缀（如 `00_`、`01_`）。部分根目录（如 `docs`、`scripts`）为例外。

| 路径 | 目录名 |
|------|--------|
| `.audit_cache` | `.audit_cache` |
| `.github/workflows` | `workflows` |
| `.trae` | `.trae` |
| `.trae/skills` | `skills` |
| `.trae/skills/audit-sentinel` | `audit-sentinel` |
| `config/factors` | `factors` |
| `config/risk` | `risk` |
| `data/assessments` | `assessments` |
| `data/assessments/economic_regime` | `economic_regime` |
| `data/assessments/market_impact` | `market_impact` |
| `data/assessments/smart_execution` | `smart_execution` |
| `data/monitoring` | `monitoring` |
| `data/monitoring/reports` | `reports` |
| `data/monitoring/reports/daily` | `daily` |
| `database` | `database` |
| `database/ddl` | `ddl` |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM` | `AI_VIRTUAL_RESEARCH_TEAM` |
| `docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS` | `ARCHITECTURE_DECISIONS` |
| `docs/01_FRAMEWORK/LAYER4_ML` | `LAYER4_ML` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/CONFIG_MANAGEMENT` | `CONFIG_MANAGEMENT` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ANOMALY_DETECTION` | `DATA_ANOMALY_DETECTION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_API_GATEWAY` | `DATA_API_GATEWAY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_BACKUP_RECOVERY` | `DATA_BACKUP_RECOVERY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_CATALOG` | `DATA_CATALOG` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_COMPRESSION_ARCHIVE` | `DATA_COMPRESSION_ARCHIVE` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_CONTRACT` | `DATA_CONTRACT` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_FEDERATION` | `DATA_FEDERATION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_LIFECYCLE_MANAGEMENT` | `DATA_LIFECYCLE_MANAGEMENT` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_LINEAGE_TRACKING` | `DATA_LINEAGE_TRACKING` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_MONITORING_ENHANCED` | `DATA_MONITORING_ENHANCED` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_OBSERVABILITY` | `DATA_OBSERVABILITY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ORCHESTRATION_ENHANCED` | `DATA_ORCHESTRATION_ENHANCED` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_PERMISSION_MANAGEMENT` | `DATA_PERMISSION_MANAGEMENT` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_PROFILING` | `DATA_PROFILING` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SECURITY_PRIVACY` | `DATA_SECURITY_PRIVACY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_STANDARDIZATION` | `DATA_STANDARDIZATION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SYNC_REPLICATION` | `DATA_SYNC_REPLICATION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_TESTING_FRAMEWORK` | `DATA_TESTING_FRAMEWORK` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_VERSION_CONTROL` | `DATA_VERSION_CONTROL` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/IFIND` | `IFIND` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/REALTIME_DATA_STREAMING` | `REALTIME_DATA_STREAMING` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/TIME_SERIES_STORAGE` | `TIME_SERIES_STORAGE` |
| `docs/03_TRADING_TACTICS/04_YOUZI_STRATEGIES/other-masters` | `other-masters` |
| `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state` | `audit_state` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON` | `CANON` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REPORTS` | `REPORTS` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/a_stock_rules` | `a_stock_rules` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/data_consistency` | `data_consistency` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/database` | `database` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/trading_costs` | `trading_costs` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/ui_design` | `ui_design` |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/web_interface` | `web_interface` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state` | `audit_state` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/checklists` | `checklists` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/improvement_plans` | `improvement_plans` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/improvements` | `improvements` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base` | `knowledge_base` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/best_practices` | `best_practices` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies` | `case_studies` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/tools_guides` | `tools_guides` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/monitoring` | `monitoring` |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/standards` | `standards` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive` | `20260404_audit_reports_archive` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/audit_state` | `audit_state` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/audit_state/archived_json_reports_20260402` | `archived_json_reports_20260402` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/audit_state/archived_reports_20260402` | `archived_reports_20260402` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/technical_reviews` | `technical_reviews` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/IFIND_CONNECTOR` | `IFIND_CONNECTOR` |
| `docs/06_ARCHIVE/20260404_audit_reports_archive/technical_reviews/QMT_DATA_INTERFACE` | `QMT_DATA_INTERFACE` |
| `docs/06_ARCHIVE/20260404_market_participant_consolidation` | `20260404_market_participant_consolidation` |
| `docs/06_ARCHIVE/20260405_economic_regime_cleanup` | `20260405_economic_regime_cleanup` |
| `docs/06_ARCHIVE/20260406_encoding_issues_archive` | `20260406_encoding_issues_archive` |
| `docs/06_ARCHIVE/20260406_encoding_issues_archive/layer1_blueprints` | `layer1_blueprints` |
| `docs/06_ARCHIVE/20260407_duplicate_audit_reports` | `20260407_duplicate_audit_reports` |
| `docs/06_ARCHIVE/20260407_duplicate_reports` | `20260407_duplicate_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports` | `20260407_old_layer_audit_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer10_reports` | `layer10_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer11_reports` | `layer11_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer25_reports` | `layer25_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer5_reports` | `layer5_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer6_reports` | `layer6_reports` |
| `docs/06_ARCHIVE/20260407_old_layer_audit_reports/layer9_reports` | `layer9_reports` |
| `docs/06_ARCHIVE/20260407_p1_cleanup_archive` | `20260407_p1_cleanup_archive` |
| `docs/06_ARCHIVE/20260408_double_yaml_dryrun_sample` | `20260408_double_yaml_dryrun_sample` |
| `docs/06_ARCHIVE/20260410_c2_benchmark_management` | `20260410_c2_benchmark_management` |
| `docs/06_ARCHIVE/20260410_c2_data_version_control` | `20260410_c2_data_version_control` |
| `docs/06_ARCHIVE/20260410_c2_disaster_recovery` | `20260410_c2_disaster_recovery` |
| `docs/06_ARCHIVE/20260410_c2_document_creation_checklist` | `20260410_c2_document_creation_checklist` |
| `docs/06_ARCHIVE/20260410_c2_document_metadata_template` | `20260410_c2_document_metadata_template` |
| `docs/06_ARCHIVE/20260410_c2_full_process_data_persistence` | `20260410_c2_full_process_data_persistence` |
| `docs/06_ARCHIVE/20260410_c2_market_regime_detection` | `20260410_c2_market_regime_detection` |
| `docs/06_ARCHIVE/20260410_c2_model_performance_version_management` | `20260410_c2_model_performance_version_management` |
| `docs/06_ARCHIVE/20260410_c2_model_risk_management` | `20260410_c2_model_risk_management` |
| `docs/06_ARCHIVE/20260410_c2_p1_audit_report_basenames` | `20260410_c2_p1_audit_report_basenames` |
| `docs/06_ARCHIVE/20260410_c2_p1_audit_reports_batch2` | `20260410_c2_p1_audit_reports_batch2` |
| `docs/06_ARCHIVE/20260410_c2_performance_attribution` | `20260410_c2_performance_attribution` |
| `docs/06_ARCHIVE/20260410_c2_realtime_risk_monitoring` | `20260410_c2_realtime_risk_monitoring` |
| `docs/06_ARCHIVE/20260410_c2_research_workflow_management` | `20260410_c2_research_workflow_management` |
| `docs/06_ARCHIVE/20260410_c2_short_term_improvement_completion` | `20260410_c2_short_term_improvement_completion` |
| `docs/06_ARCHIVE/20260410_c2_strategy_engine` | `20260410_c2_strategy_engine` |
| `docs/06_ARCHIVE/20260410_c2_strategy_lifecycle_management` | `20260410_c2_strategy_lifecycle_management` |
| `docs/06_ARCHIVE/20260410_c2_strategy_selection` | `20260410_c2_strategy_selection` |
| `docs/06_ARCHIVE/20260410_c2_transaction_cost_analysis` | `20260410_c2_transaction_cost_analysis` |
| `docs/06_ARCHIVE/20260410_system_manifest_backup` | `20260410_system_manifest_backup` |
| `docs/06_ARCHIVE/20260411_c2_data_quality_monitoring` | `20260411_c2_data_quality_monitoring` |
| `docs/06_ARCHIVE/architecture_v4` | `architecture_v4` |
| `docs/06_ARCHIVE/architecture_v4/module_designs` | `module_designs` |
| `docs/06_ARCHIVE/architecture_v4/module_designs/layer_1` | `layer_1` |
| `docs/06_ARCHIVE/architecture_v4/module_designs/layer_11` | `layer_11` |
| `docs/06_ARCHIVE/architecture_v4/module_designs/layer_9` | `layer_9` |
| `docs/06_ARCHIVE/duplicate_documents` | `duplicate_documents` |
| `docs/06_ARCHIVE/duplicate_documents/20260404_layer7_audit_reports` | `20260404_layer7_audit_reports` |
| `docs/06_ARCHIVE/encoding_backups` | `encoding_backups` |
| `docs/06_ARCHIVE/encoding_backups/20260406_ai_workflow` | `20260406_ai_workflow` |
| `docs/06_ARCHIVE/factor-library` | `factor-library` |
| `docs/06_ARCHIVE/incomplete_documents` | `incomplete_documents` |
| `docs/06_ARCHIVE/incomplete_documents/20260404_blueprint_incomplete` | `20260404_blueprint_incomplete` |
| `docs/06_ARCHIVE/integrated_documents` | `integrated_documents` |
| `docs/06_ARCHIVE/integrated_documents/20260403_market_simulation` | `20260403_market_simulation` |
| `docs/06_ARCHIVE/knowledge_library` | `knowledge_library` |
| `docs/06_ARCHIVE/knowledge_library/enterprise_plans` | `enterprise_plans` |
| `docs/06_ARCHIVE/main` | `main` |
| `docs/06_ARCHIVE/main/BLUEPRINTS` | `BLUEPRINTS` |
| `docs/06_ARCHIVE/main/v4_development` | `v4_development` |
| `docs/06_ARCHIVE/temp_pending` | `temp_pending` |
| `docs/08_KNOWLEDGE/BEST_PRACTICES` | `BEST_PRACTICES` |
| `docs/08_KNOWLEDGE/FACTOR_LIBRARY` | `FACTOR_LIBRARY` |
| `docs/08_KNOWLEDGE/STRATEGY_LIBRARY` | `STRATEGY_LIBRARY` |
| `docs/09_ARCHIVE/TECHNICAL_SPECIFICATIONS` | `TECHNICAL_SPECIFICATIONS` |
| `docs/09_ARCHIVE/duplicates` | `duplicates` |
| `docs/09_AUDIT/AUTOMATION` | `AUTOMATION` |
| `docs/09_AUDIT/BEST_PRACTICES` | `BEST_PRACTICES` |
| `docs/09_AUDIT/CASE_STUDIES` | `CASE_STUDIES` |
| `docs/09_AUDIT/CONFIG` | `CONFIG` |
| `docs/09_AUDIT/CONFIGURATION` | `CONFIGURATION` |
| `docs/09_AUDIT/DECISION_RECORDS` | `DECISION_RECORDS` |
| `docs/09_AUDIT/GUIDES` | `GUIDES` |
| `docs/09_AUDIT/PROCEDURES` | `PROCEDURES` |
| `docs/09_AUDIT/REPORTS` | `REPORTS` |
| `docs/09_AUDIT/RESEARCH_MEMOS` | `RESEARCH_MEMOS` |
| `docs/09_AUDIT/SOLUTIONS` | `SOLUTIONS` |
| `docs/09_AUDIT/STANDARDS` | `STANDARDS` |
| `docs/09_AUDIT/STATE` | `STATE` |
| `docs/09_AUDIT/STATE/overnight_runs` | `overnight_runs` |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_021344` | `20260408_021344` |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_022356` | `20260408_022356` |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_033240` | `20260408_033240` |
| `docs/09_AUDIT/TEMPLATES` | `TEMPLATES` |
| `docs/09_AUDIT/TOOLS` | `TOOLS` |
| `docs/09_AUDIT/TRAINING` | `TRAINING` |
| `docs/09_AUDIT/WORKFLOWS` | `WORKFLOWS` |
| `docs/09_RESEARCH_INNOVATION/_archive` | `_archive` |
| `docs/09_RESEARCH_INNOVATION/maintenance_records` | `maintenance_records` |
| `docs/10_GOVERNANCE_COMPLIANCE/CI_CD_INTEGRATION` | `CI_CD_INTEGRATION` |
| `docs/10_GOVERNANCE_COMPLIANCE/CLASSIFICATION` | `CLASSIFICATION` |
| `docs/10_GOVERNANCE_COMPLIANCE/GOVERNANCE_PROCESSES` | `GOVERNANCE_PROCESSES` |
| `docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE` | `KNOWLEDGE_BASE` |
| `docs/10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM` | `TRAINING_SYSTEM` |
| `docs/11_STRATEGIC_DECISION/archive` | `archive` |
| `docs/module_designs` | `module_designs` |
| `docs/module_designs/layer_0` | `layer_0` |
| `notebooks` | `notebooks` |
| `reports` | `reports` |
| `review_materials_package` | `review_materials_package` |
| `review_materials_package/a_stock_rules` | `a_stock_rules` |
| `review_materials_package/data_consistency` | `data_consistency` |
| `review_materials_package/trading_costs` | `trading_costs` |
| `review_materials_package/web_interface` | `web_interface` |
| `scripts/governance` | `governance` |
| `src/api` | `api` |
| `src/api/routes` | `routes` |
| `src/core` | `core` |
| `src/engines` | `engines` |
| `src/modules` | `modules` |
| `src/modules/ai_factor_miner` | `ai_factor_miner` |
| `src/modules/ai_factor_miner/examples` | `examples` |
| `src/modules/economic_regime_engine` | `economic_regime_engine` |
| `src/modules/economic_regime_engine/examples` | `examples` |
| `src/modules/examples` | `examples` |
| `src/modules/statistical_arbitrage` | `statistical_arbitrage` |
| `src/modules/statistical_arbitrage/examples` | `examples` |
| `src/utils` | `utils` |
| `tests/fixtures` | `fixtures` |
| `tests/integration` | `integration` |
| `tests/performance` | `performance` |
| `tests/unit` | `unit` |
| `tools` | `tools` |

```
```---
```

## 参考标准

- PATH_STANDARD.md §1.1
- FILE_NAMING_STANDARD.md
