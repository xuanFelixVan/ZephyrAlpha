---
module_id: AUTO_67062
owner: System_Guardian
version: 1.0
status: AUDITED
last_updated: 2026-04-13
---
# 目录命名合规性扫描报告

> **生成脚本**: `scripts/governance/scan_directory_naming_compliance.py`
> **扫描日期**: 20260413

```
```---
```

## 扫描摘要

| 指标 | 数量 |
|------|------|
| 总目录数 | 492 |
| 包含中文 | 0 |
| 包含空格 | 0 |
| 包含特殊字符 | 4 |
| 缺少编号前缀 | 190 |
| 合规目录 | 301 |

## 包含特殊字符的目录

| 路径 | 目录名 |
|------|--------|
| `.audit_cache` | `.audit_cache` |
| `.audit_fix_backup` | `.audit_fix_backup` |
| `.github` | `.github` |
| `.trae` | `.trae` |

## 缺少编号前缀的目录

> **说明**: 以下目录未使用 2 位数字前缀（如 `00_`、`01_`）。部分根目录（如 `docs`、`scripts`）为例外。

| 路径 | 目录名 |
|------|--------|
| `.audit_cache` | `.audit_cache` |
| `.audit_fix_backup` | `.audit_fix_backup` |
| `.audit_fix_backup/docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM` | `AI_VIRTUAL_RESEARCH_TEAM` |
| `.audit_fix_backup/docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS` | `ARCHITECTURE_DECISIONS` |
| `.audit_fix_backup/docs/01_FRAMEWORK/LAYER4_ML` | `LAYER4_ML` |
| `.audit_fix_backup/docs/03_TRADING_TACTICS/04_YOUZI_STRATEGIES/other-masters` | `other-masters` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state` | `audit_state` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON` | `CANON` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REPORTS` | `REPORTS` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/trading_costs` | `trading_costs` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state` | `audit_state` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/checklists` | `checklists` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base` | `knowledge_base` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/best_practices` | `best_practices` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies` | `case_studies` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/monitoring` | `monitoring` |
| `.audit_fix_backup/docs/05_IMPLEMENTATION/07_OPERATIONS/standards` | `standards` |
| `.audit_fix_backup/docs/06_ARCHIVE/STAGING_AREA` | `STAGING_AREA` |
| `.audit_fix_backup/docs/06_ARCHIVE/audit_reports` | `audit_reports` |
| `.audit_fix_backup/docs/06_ARCHIVE/blueprints` | `blueprints` |
| `.audit_fix_backup/docs/06_ARCHIVE/data_management` | `data_management` |
| `.audit_fix_backup/docs/06_ARCHIVE/duplicates` | `duplicates` |
| `.audit_fix_backup/docs/06_ARCHIVE/factor_library` | `factor_library` |
| `.audit_fix_backup/docs/06_ARCHIVE/implementation` | `implementation` |
| `.audit_fix_backup/docs/06_ARCHIVE/reports` | `reports` |
| `.audit_fix_backup/docs/06_ARCHIVE/research` | `research` |
| `.audit_fix_backup/docs/06_ARCHIVE/strategy_library` | `strategy_library` |
| `.audit_fix_backup/docs/06_ARCHIVE/technical_specifications` | `technical_specifications` |
| `.audit_fix_backup/docs/06_ARCHIVE/unclassified` | `unclassified` |
| `.audit_fix_backup/docs/09_AUDIT/BEST_PRACTICES` | `BEST_PRACTICES` |
| `.audit_fix_backup/docs/09_AUDIT/CASE_STUDIES` | `CASE_STUDIES` |
| `.audit_fix_backup/docs/09_AUDIT/CONFIG` | `CONFIG` |
| `.audit_fix_backup/docs/09_AUDIT/CONFIGURATION` | `CONFIGURATION` |
| `.audit_fix_backup/docs/09_AUDIT/FORM_STANDARDS` | `FORM_STANDARDS` |
| `.audit_fix_backup/docs/09_AUDIT/GUIDES` | `GUIDES` |
| `.audit_fix_backup/docs/09_AUDIT/PROCEDURES` | `PROCEDURES` |
| `.audit_fix_backup/docs/09_AUDIT/REPORTS` | `REPORTS` |
| `.audit_fix_backup/docs/09_AUDIT/SOLUTIONS` | `SOLUTIONS` |
| `.audit_fix_backup/docs/09_AUDIT/STANDARDS` | `STANDARDS` |
| `.audit_fix_backup/docs/09_AUDIT/STATE` | `STATE` |
| `.audit_fix_backup/docs/09_AUDIT/STATE/overnight_runs` | `overnight_runs` |
| `.audit_fix_backup/docs/09_AUDIT/STATE/overnight_runs/20260408_021344` | `20260408_021344` |
| `.audit_fix_backup/docs/09_AUDIT/STATE/overnight_runs/20260408_022356` | `20260408_022356` |
| `.audit_fix_backup/docs/09_AUDIT/STATE/overnight_runs/20260408_033240` | `20260408_033240` |
| `.audit_fix_backup/docs/09_AUDIT/TRAINING` | `TRAINING` |
| `.audit_fix_backup/docs/09_AUDIT/WORKFLOWS` | `WORKFLOWS` |
| `.audit_fix_backup/docs/10_GOVERNANCE_COMPLIANCE/GOVERNANCE_PROCESSES` | `GOVERNANCE_PROCESSES` |
| `.audit_fix_backup/docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE` | `KNOWLEDGE_BASE` |
| `.audit_fix_backup/docs/12_MODULE_DESIGNS/layer_0` | `layer_0` |
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
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_RECOVERY` | `DATA_RECOVERY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SECURITY_PRIVACY` | `DATA_SECURITY_PRIVACY` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_STANDARDIZATION` | `DATA_STANDARDIZATION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SYNC_REPLICATION` | `DATA_SYNC_REPLICATION` |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_VALIDATION_FRAMEWORK` | `DATA_VALIDATION_FRAMEWORK` |
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
| `docs/06_ARCHIVE/STAGING_AREA` | `STAGING_AREA` |
| `docs/06_ARCHIVE/audit_reports` | `audit_reports` |
| `docs/06_ARCHIVE/blueprints` | `blueprints` |
| `docs/06_ARCHIVE/data_management` | `data_management` |
| `docs/06_ARCHIVE/duplicates` | `duplicates` |
| `docs/06_ARCHIVE/factor_library` | `factor_library` |
| `docs/06_ARCHIVE/implementation` | `implementation` |
| `docs/06_ARCHIVE/reports` | `reports` |
| `docs/06_ARCHIVE/research` | `research` |
| `docs/06_ARCHIVE/strategy_library` | `strategy_library` |
| `docs/06_ARCHIVE/technical_specifications` | `technical_specifications` |
| `docs/06_ARCHIVE/unclassified` | `unclassified` |
| `docs/08_KNOWLEDGE/BEST_PRACTICES` | `BEST_PRACTICES` |
| `docs/08_KNOWLEDGE/FACTOR_LIBRARY` | `FACTOR_LIBRARY` |
| `docs/08_KNOWLEDGE/STRATEGY_LIBRARY` | `STRATEGY_LIBRARY` |
| `docs/09_ARCHIVE/TECHNICAL_SPECIFICATIONS` | `TECHNICAL_SPECIFICATIONS` |
| `docs/09_ARCHIVE/audit_reports` | `audit_reports` |
| `docs/09_ARCHIVE/blueprints` | `blueprints` |
| `docs/09_ARCHIVE/duplicates` | `duplicates` |
| `docs/09_ARCHIVE/factor_library` | `factor_library` |
| `docs/09_ARCHIVE/unclassified` | `unclassified` |
| `docs/09_AUDIT/AUTOMATION` | `AUTOMATION` |
| `docs/09_AUDIT/BEST_PRACTICES` | `BEST_PRACTICES` |
| `docs/09_AUDIT/CASE_STUDIES` | `CASE_STUDIES` |
| `docs/09_AUDIT/CHECKLISTS` | `CHECKLISTS` |
| `docs/09_AUDIT/CONFIG` | `CONFIG` |
| `docs/09_AUDIT/CONFIGURATION` | `CONFIGURATION` |
| `docs/09_AUDIT/DECISION_RECORDS` | `DECISION_RECORDS` |
| `docs/09_AUDIT/FORM_STANDARDS` | `FORM_STANDARDS` |
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
| `docs/11_STRATEGIC_DECISION/maintenance_records` | `maintenance_records` |
| `docs/12_MODULE_DESIGNS/layer_0` | `layer_0` |
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
| `tests/faulty_samples` | `faulty_samples` |
| `tests/fixtures` | `fixtures` |
| `tests/integration` | `integration` |
| `tests/performance` | `performance` |
| `tests/unit` | `unit` |
| `tools` | `tools` |

```
```---
```

## 参考标准

- [PATH_STANDARD.md](../../05_IMPLEMENTATION/02_DEVELOPMENT/path-standard.md) §1.1
- [doc-naming-standard.md](../STANDARDS/doc-naming-standard.md)（含原 file-naming-standard 附录）
