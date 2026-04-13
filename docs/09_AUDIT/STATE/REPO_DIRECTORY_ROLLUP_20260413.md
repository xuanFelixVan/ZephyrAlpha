---
standard_type: audit_state
applicable_scope: 全仓库路径目录聚合（git ls-files，可选未跟踪）
generated_date: '20260413'
---

# 仓库目录深度聚合（路径条数）

> 由 `scripts/governance/export_repo_directory_rollup.py` 生成；**仅已跟踪**，共 **5369** 条路径。
> JSON 真源：[`REPO_DIRECTORY_ROLLUP_20260413.json`](./REPO_DIRECTORY_ROLLUP_20260413.json)

## 使用说明

- **深度 2**：适合一级排期（与任务清单 §1 节选表同量级）。
- **深度 3～6**：把大目录（如 `docs/09_AUDIT`、`docs/05_IMPLEMENTATION`）拆成**可分批啃完的子队列**，支撑「按最深前缀尽治」而不是只扫表面。
- 治理时按前缀从大到小或按业务优先级排序；每一前缀「清空」的标准见 [全仓库文件治理任务清单](../../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/REPO_WIDE_FILE_GOVERNANCE_TASK_LIST.md) **§7**。
- 未跟踪路径仅在使用 `--include-untracked` 时出现；适合治理「工作区里已存在、尚未 add」的文档。

## `docs/` 下深度 3 前缀 Top 50（按路径条数降序）

| 目录前缀（深度固定） | 路径条数 |
|---|---:|
| `docs/09_AUDIT/STATE` | 525 |
| `docs/09_AUDIT/REPORTS` | 500 |
| `docs/05_IMPLEMENTATION/04_OPERATIONS` | 429 |
| `docs/06_ARCHIVE/audit_reports` | 294 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS` | 283 |
| `docs/06_ARCHIVE/blueprints` | 230 |
| `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS` | 97 |
| `docs/06_ARCHIVE/reports` | 93 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE` | 83 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS` | 63 |
| `docs/01_FRAMEWORK/LAYER4_ML` | 40 |
| `docs/09_AUDIT/STANDARDS` | 34 |
| `docs/09_ARCHIVE/factor_library` | 29 |
| `docs/06_ARCHIVE/unclassified` | 25 |
| `docs/09_ARCHIVE/blueprints` | 24 |
| `docs/05_IMPLEMENTATION/02_DEVELOPMENT` | 21 |
| `docs/09_RESEARCH_INNOVATION/maintenance_records` | 20 |
| `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK` | 16 |
| `docs/09_AUDIT/FORM_STANDARDS` | 16 |
| `docs/03_TRADING_TACTICS/04_YOUZI_STRATEGIES` | 15 |
| `docs/04_EXECUTION/07_LIVE_STREAM` | 13 |
| `docs/06_ARCHIVE/implementation` | 11 |
| `docs/09_AUDIT/PROCEDURES` | 10 |
| `docs/06_ARCHIVE/technical_specifications` | 9 |
| `docs/03_TRADING_TACTICS/99_ARCHIVE` | 7 |
| `docs/05_IMPLEMENTATION/01_QUICKSTART` | 7 |
| `docs/06_ARCHIVE/factor_library` | 7 |
| `docs/09_RESEARCH_INNOVATION/_archive` | 7 |
| `docs/04_EXECUTION/03_MONITORING` | 6 |
| `docs/05_IMPLEMENTATION/03_DEPLOYMENT` | 6 |
| `docs/09_AUDIT/AUTOMATION` | 6 |
| `docs/09_AUDIT/CONFIG` | 6 |
| `docs/09_AUDIT/WORKFLOWS` | 6 |
| `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS` | 5 |
| `docs/10_GOVERNANCE_COMPLIANCE/KNOWLEDGE_BASE` | 5 |
| `docs/11_STRATEGIC_DECISION/archive` | 5 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS` | 4 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM` | 4 |
| `docs/02_FACTOR_LIBRARY/01_STANDARDS` | 4 |
| `docs/03_TRADING_TACTICS/03_ADVANCED_TACTICS` | 4 |
| `docs/04_EXECUTION/01_ORDER_EXECUTION` | 4 |
| `docs/05_IMPLEMENTATION/04_INFRASTRUCTURE` | 4 |
| `docs/05_IMPLEMENTATION/99_ARCHIVE` | 4 |
| `docs/06_ARCHIVE/duplicates` | 4 |
| `docs/08_KNOWLEDGE/BEST_PRACTICES` | 4 |
| `docs/09_AUDIT/GUIDES` | 4 |
| `docs/11_STRATEGIC_DECISION/01_asset_allocation` | 4 |
| `docs/11_STRATEGIC_DECISION/02_risk_budgeting` | 4 |
| `docs/11_STRATEGIC_DECISION/03_strategy_selection` | 4 |
| `docs/11_STRATEGIC_DECISION/04_strategic_adjustment` | 4 |


## `docs/` 下深度 4 前缀 Top 50（按路径条数降序）

| 目录前缀（深度固定） | 路径条数 |
|---|---:|
| `docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state` | 421 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS` | 179 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS` | 35 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT` | 32 |
| `docs/09_AUDIT/STATE/overnight_runs` | 31 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base` | 18 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/04_CONFIG_STANDARDS` | 13 |
| `docs/03_TRADING_TACTICS/04_YOUZI_STRATEGIES/other-masters` | 11 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/IFIND` | 5 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_OPERATION_MANUALS` | 5 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/06_CHECKLISTS` | 5 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/02_IMPLEMENTATION_GUIDES` | 4 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/improvements` | 4 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/03_CLEANING` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/07_DATA_PIPELINE` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/CONFIG_MANAGEMENT` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ANOMALY_DETECTION` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_API_GATEWAY` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_CATALOG` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_COMPRESSION_ARCHIVE` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_CONTRACT` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_FEDERATION` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_LIFECYCLE_MANAGEMENT` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_LINEAGE_TRACKING` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_MONITORING_ENHANCED` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_OBSERVABILITY` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_ORCHESTRATION_ENHANCED` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_PERMISSION_MANAGEMENT` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_PROFILING` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_RECOVERY` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SECURITY_PRIVACY` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_STANDARDIZATION` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_SYNC_REPLICATION` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_VALIDATION_FRAMEWORK` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_VERSION_CONTROL` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/REALTIME_DATA_STREAMING` | 3 |
| `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/TIME_SERIES_STORAGE` | 3 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/checklists` | 3 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/improvement_plans` | 3 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/monitoring` | 3 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/standards` | 3 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/03_CONSTRUCTION_PLANS` | 2 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state` | 2 |
| `docs/00_OVERVIEW/CHANGELOG.md` | 1 |
| `docs/00_OVERVIEW/INDEX.md` | 1 |
| `docs/00_OVERVIEW/README.md` | 1 |
| `docs/00_OVERVIEW/data-flow.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/INDEX.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/QMT_TRADING_SYSTEM_REFERENCE.pdf` | 1 |


## `docs/` 下深度 5 前缀 Top 50（按路径条数降序）

| 目录前缀（深度固定） | 路径条数 |
|---|---:|
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/REPORTS` | 14 |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_021344` | 10 |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_022356` | 10 |
| `docs/09_AUDIT/STATE/overnight_runs/20260408_033240` | 10 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/database` | 9 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON` | 6 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/data_consistency` | 4 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/trading_costs` | 4 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/web_interface` | 4 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/best_practices` | 4 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/case_studies` | 4 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/a_stock_rules` | 3 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/05_DESIGN_DOCS/ui_design` | 3 |
| `docs/05_IMPLEMENTATION/07_OPERATIONS/knowledge_base/tools_guides` | 3 |
| `docs/00_OVERVIEW/CHANGELOG.md` | 1 |
| `docs/00_OVERVIEW/INDEX.md` | 1 |
| `docs/00_OVERVIEW/README.md` | 1 |
| `docs/00_OVERVIEW/data-flow.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/INDEX.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/QMT_TRADING_SYSTEM_REFERENCE.pdf` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/README.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/xuntou_qmt_trading_system_documentation.pdf` | 1 |
| `docs/00_RESOURCES/INDEX.md` | 1 |
| `docs/00_RESOURCES/README.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-implementation-plan.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-project-kickoff.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS/README.md` | 1 |
| `docs/01_FRAMEWORK/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/README.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ai-enhancement-integration-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ai-pattern-recognition-engine-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/anomaly-detection-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/causal-inference-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/complete-missing-modules-overview.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/data-version-control-layer4-entry.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v2-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v3-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v5-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v6-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/drift-detection-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/full-process-data-layer4-entry.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/gap-analysis-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/hyperparameter-optimization-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/implementation-roadmap.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/machine-learning-governance-deep-audit-report-20260407.md` | 1 |


## `docs/` 下深度 6 前缀 Top 50（按路径条数降序）

| 目录前缀（深度固定） | 路径条数 |
|---|---:|
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/CANON/ARCHIVE` | 2 |
| `docs/00_OVERVIEW/CHANGELOG.md` | 1 |
| `docs/00_OVERVIEW/INDEX.md` | 1 |
| `docs/00_OVERVIEW/README.md` | 1 |
| `docs/00_OVERVIEW/data-flow.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/INDEX.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/QMT_TRADING_SYSTEM_REFERENCE.pdf` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/README.md` | 1 |
| `docs/00_RESOURCES/04_PLATFORM_DOCS/xuntou_qmt_trading_system_documentation.pdf` | 1 |
| `docs/00_RESOURCES/INDEX.md` | 1 |
| `docs/00_RESOURCES/README.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-implementation-plan.md` | 1 |
| `docs/01_FRAMEWORK/AI_VIRTUAL_RESEARCH_TEAM/ai-virtual-research-team-project-kickoff.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/ARCHITECTURE_DECISIONS/README.md` | 1 |
| `docs/01_FRAMEWORK/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/INDEX.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/README.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ai-enhancement-integration-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ai-pattern-recognition-engine-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/anomaly-detection-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/causal-inference-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/complete-missing-modules-overview.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/data-version-control-layer4-entry.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v2-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v3-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v5-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/deep-audit-report-v6-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/drift-detection-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/full-process-data-layer4-entry.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/gap-analysis-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/hyperparameter-optimization-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/implementation-roadmap.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/machine-learning-governance-deep-audit-report-20260407.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/market-regime-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/master-index.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-comprehensive-audit-20260404.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-layer-comprehensive-audit-20260405.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-layer-deep-governance-audit-20260406.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-layer-governance-audit-20260405.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-layer-governance-fix-report-20260406.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/ml-layer-opensource-mapping-20260405.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/model-drift-detection-blueprint.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/model-governance-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/model-interpretability-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/model-monitoring-technical-specification.md` | 1 |
| `docs/01_FRAMEWORK/LAYER4_ML/model-serving-blueprint.md` | 1 |

