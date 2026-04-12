---
module_id: 09_ARCHIVE_BLUEPRINTS_INDEX
layer: layer_09
version: 1.0.0
status: Active
responsibility:
  - 处理INDEX相关业务
created_date: 2026-04-07
last_updated: 2026-04-11
owner: 文档管理团队
---

## 变更记录



| 版本 | 日期 | 变更内容 | 变更人 |

|------|------|----------|--------|

| v1.0.1 | 2026-04-11 | P5 §7：`INDEX_HEALTH_20260422`；本页增上级/rollup 互指 + 全量 md 挂载清单使零入链归零（归档池非真源口径不变） | 文档治理系统 |

| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |



---



## 🧭 canonical 指针入口（本目录不作为真源）



> **强规则**：`docs/09_ARCHIVE/duplicates/` 仅用于重复池与追溯，canonical 真源必须在业务目录。  

> 本索引文件历史格式不规范（自动生成残留），统一入口以台账为准。



- **canonical 指针台账**：`CANONICAL_POINTERS.md`

- **重复文档处理标准**：`DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`



---



## 上级与接力



- [09_ARCHIVE 索引](../INDEX.md)

- 全仓库文件治理任务清单 §7

- 治理工具总索引

- [09_AUDIT STATE 索引](../../09_AUDIT/STATE/INDEX.md)



### 索引健全性与目录体量（P5 §7）



- **零入链扫描（最新）**：../../09_AUDIT/STATE/INDEX_HEALTH_ORPHAN_20260422.md（`scan_index_health.py --prefix docs/09_ARCHIVE/duplicates --date 20260422`；**zero_inbound=0**；候选 md **54**；首轮 **45** 处零入链，已由本页「全量挂载」补链后复跑归零）

- **rollup（深度 3 前缀条数）**：../../09_AUDIT/STATE/REPO_DIRECTORY_ROLLUP_20260414.md（检索 `docs/09_ARCHIVE/duplicates` **54** 条）



## 本目录已跟踪 Markdown 全量挂载（入链用 · 非真源）



> 与上文「canonical 指针」并列：`CANONICAL_POINTERS` 仍为台账真源；下列列表仅为 **P5 §7** 索引可达性与 `scan_index_health` 入链证据，**不**改变归档物语义。



- ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_ROUND2_20260407_191332_legacy_09_archive_duplicates.md

- backtest_standards.md

- BAOSTOCK_CONNECTOR.md

- BARRA_STYLE_FACTORS.md

- CANONICAL_POINTERS.md

- CLEANING_RULES.md

- CORRELATION_ANALYSIS.md

- correlation_matrix.md

- DATA_ACQUISITION.md

- DATA_REQUIREMENTS.md

- DATA_SOURCE_ADAPTERS.md

- DATA_SOURCE_LAYER_GAP_ANALYSIS.md

- FACTOR_CALCULATION_FRAMEWORK.md

- FACTOR_DECAY.md

- FACTOR_DEFINITION.md

- FACTOR_MANAGEMENT_STANDARD_legacy_09_archive_duplicates.md

- factor_master_index.md

- FACTOR_MINING_GUIDE.md

- factor_neutralization.md

- factor_preprocessing.md

- FACTOR_REGISTRY_legacy_09_archive_duplicates.md

- factor_return_analysis.md

- FACTOR_SCREENING_STRATEGY.md

- factor_synthesis.md

- FACTOR_TAXONOMY_legacy_09_archive_duplicates.md

- FACTOR_TRANSPARENCY_REPORT.md

- FACTOR_VALIDATION_BLUEPRINT.md

- FACTOR_VALIDATION_GUIDE.md

- FAQ_legacy_09_archive_duplicates.md

- FINANCIAL_STATEMENTS_API.md

- FREE_DATA_SOURCES.md

- FUTURE_FACTOR_TOOLS.md

- [HANDOVER.md](09_ARCHIVE/factor_library/HANDOVER.md)

- ic_analysis.md

- IFIND_CONNECTOR.md

- INDUSTRY_FACTORS.md

- KNOWLEDGE_MANAGEMENT.md

- LAYERED_BACKTEST.md

- MACRO_DATA.md

- MODULE_DESIGN_PLAN.md

- NEWS_SENTIMENT_DATA_SOURCE.md

- OPTIMIZATION_SUMMARY.md

- OVERFITTING_TEST.md

- QMT_INTERFACE.md

- QUALITY_METRICS.md

- [README.md](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md)

- research_management.md

- SCHEDULER_API.md

- `SITEMAP.md` (已归档)

- STATISTICAL_TOOLS.md

- SUPERCMD_CONNECTOR.md

- TAIL_RISK_FACTORS.md

- TECHNICAL_INDICATORS.md

