---
module_id: ARCHIVE_DUPLICATES_CANONICAL_POINTERS_001
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: 2026-04-08
owner: 文档治理系统
standard_type: 重复文档裁决台账
applicable_scope: docs/09_ARCHIVE/duplicates（重复池统一入口与 canonical 指针）
compliance_level: 专业标准
layer: layer_09
responsibility: "处理CANONICAL_POINTERS相关业务"
---



# duplicates：canonical 指针台账（统一入口）

> **定位**：`docs/09_ARCHIVE/duplicates/` 是“重复/候选合并/历史草案”的暂存池。  
> **强规则**：本目录内的 `.md` **默认不作为权威真源（canonical）**，除非在本台账中被明确标注为 canonical。

## 1) 使用方式（专业机构做法）

- **当你发现重复文档**：先把“真源”确定在业务目录（例如 `docs/01_FRAMEWORK/`、`docs/02_FACTOR_LIBRARY/`、`docs/03_TRADING_TACTICS/` 等）  
- **duplicates 里的副本**：只保留追溯价值，并在这里写清楚：
  - **canonical_path**（真源路径）
  - **disposition**（保留/合并后删除/长期归档）
  - **rationale**（裁决理由，1-2 句）

## 2) canonical 指针表（待裁决默认 TBD）

> 说明：为便于批处理推进，本表允许先落 “TBD”，后续按主题逐批裁决与回填。

| file | canonical_path | disposition | rationale |
|------|----------------|------------|-----------|
| `duplicates/FACTOR_CALCULATION_FRAMEWORK.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/FACTOR_CALCULATOR_TECHNICAL_SPECIFICATION.md` | merge_then_delete | 本文件内容更像“因子计算引擎/框架”的技术实现范畴，真源以技术规格书为准 |
| `duplicates/FACTOR_DEFINITION.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md` | merge_then_delete | 因子定义与元数据口径以注册表（含定义/注册流程）为准 |
| `duplicates/FACTOR_MANAGEMENT_STANDARD_legacy_09_archive_duplicates.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md` | retain_trace | basename 消歧后缀；业务真源在标准层 |
| `duplicates/IFIND_CONNECTOR.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/IFIND_CONNECTOR_TECHNICAL_SPECIFICATION.md` | retain_trace | 数据源连接器真源以技术规格书为准 |
| `duplicates/QMT_INTERFACE.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md` | retain_trace | QMT 数据接口真源以技术规格书为准 |
| `duplicates/STATISTICAL_TOOLS.md` | `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS/statistical_tools.md` | retain_trace | 统计工具集合真源在研究支持层 |
| `duplicates/backtest_standards.md` | `docs/08_KNOWLEDGE/BEST_PRACTICES/BACKTEST_BEST_PRACTICES.md` | merge_then_delete | 回测标准与常见陷阱以知识库最佳实践为准 |
| `duplicates/FACTOR_TAXONOMY_legacy_09_archive_duplicates.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_TAXONOMY.md` | merge_then_delete | basename 消歧后缀；因子分类体系真源在标准层 |
| `duplicates/DATA_ACQUISITION.md` | `docs/01_FRAMEWORK/DATA_SOURCE_LAYER_BLUEPRINT.md` | merge_then_delete | 数据采集与多源接入的总体真源以 Layer 0 数据源层蓝图为准 |
| `duplicates/README.md` | `docs/06_ARCHIVE/README.md` | retain_trace | 本目录说明以归档总入口为准；duplicates 内仅保留追溯与台账入口 |
| `duplicates/BAOSTOCK_CONNECTOR.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/BAOSTOCK_TECHNICAL_SPECIFICATION.md` | merge_then_delete | Baostock 连接器/适配器真源以技术规格书为准 |
| `duplicates/SUPERCMD_CONNECTOR.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/SUPERCOMMAND_TECHNICAL_SPECIFICATION.md` | merge_then_delete | SuperCommand 连接器真源以技术规格书为准 |
| `duplicates/SCHEDULER_API.md` | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/02_SCHEDULER/FACTOR_LIB_DATA_SOURCE_SCHEDULER_OVERVIEW.md` | merge_then_delete | 调度 API 的权威描述应归入数据源层调度模块（后续可再细分到专门接口文档） |
| `duplicates/DATA_SOURCE_ADAPTERS.md` | `docs/01_FRAMEWORK/DATA_SOURCE_LAYER_BLUEPRINT.md` | merge_then_delete | 数据源适配器接口总体归属 Layer 0 数据源层蓝图（后续可细化到统一数据基础设施/网关蓝图或技术规格） |
| `duplicates/DATA_REQUIREMENTS.md` | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/DATA_CONTRACT/FACTOR_LIB_DATA_SOURCE_DATA_CONTRACT_OVERVIEW.md` | merge_then_delete | “需要什么数据/字段/质量口径”的权威归属更贴近数据契约（Data Contract）模块；后续可在该模块下沉淀专门需求清单 |
| `duplicates/CLEANING_RULES.md` | `docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/03_CLEANING/FACTOR_LIB_DATA_SOURCE_CLEANING_OVERVIEW.md` | merge_then_delete | 清洗规则权威归属数据清洗模块（后续可再细分到具体规则文档） |
| `duplicates/FINANCIAL_STATEMENTS_API.md` | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/IFIND_CONNECTOR_TECHNICAL_SPECIFICATION.md` | merge_then_delete | 财务报表 API 属于数据源连接器能力的一部分，真源以连接器技术规格书为准 |
| `duplicates/MACRO_DATA.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ECONOMIC_REGIME_ENGINE_BLUEPRINT.md` | merge_then_delete | 宏观数据更贴近经济范式/宏观因子相关蓝图；后续可独立成“宏观数据源”文档再调整 canonical |
| `duplicates/NEWS_SENTIMENT_DATA_SOURCE.md` | `docs/01_FRAMEWORK/SENTIMENT_DATA_INTEGRATION_BLUEPRINT.md` | merge_then_delete | 新闻/舆情数据源的权威归属为舆情数据集成蓝图 |
| `duplicates/CORRELATION_ANALYSIS.md` | `docs/07_RESEARCH/02_EXPLORATORY_ANALYSIS/correlation_analysis.md` | merge_then_delete | 相关性统计与 EDA 真源在研究支持层 |
| `duplicates/correlation_matrix.md` | `docs/02_FACTOR_LIBRARY/37_FACTOR_CORRELATION/FACTOR_CORRELATION_BLUEPRINT.md` | merge_then_delete | 因子相关矩阵/冗余检测以因子相关性模块蓝图为准 |
| `duplicates/QUALITY_METRICS.md` | `docs/02_FACTOR_LIBRARY/19_FACTOR_DATA_QUALITY/FACTOR_DATA_QUALITY_BLUEPRINT.md` | merge_then_delete | 因子质量指标真源以因子数据质量蓝图为准 |
| `duplicates/FACTOR_VALIDATION_GUIDE.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | merge_then_delete | 因子验证与回测集成流程以该施工蓝图为准 |
| `duplicates/OVERFITTING_TEST.md` | `docs/08_KNOWLEDGE/BEST_PRACTICES/BACKTEST_BEST_PRACTICES.md` | merge_then_delete | 过拟合检验与稳健性以回测最佳实践为准 |
| `duplicates/FACTOR_VALIDATION_BLUEPRINT.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | merge_then_delete | 因子验证框架以因子-回测集成施工蓝图为准 |
| `duplicates/FACTOR_SCREENING_STRATEGY.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md` | merge_then_delete | 因子筛选/分层与生命周期口径以因子管理标准为准 |
| `duplicates/ic_analysis.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | merge_then_delete | IC 分析流程纳入因子研究与回测集成；真源以该蓝图为准 |
| `duplicates/FACTOR_DECAY.md` | `docs/02_FACTOR_LIBRARY/33_FACTOR_DECAY_MGMT/FACTOR_DECAY_MGMT_BLUEPRINT.md` | merge_then_delete | 因子衰减以衰减管理模块蓝图为准 |
| `duplicates/LAYERED_BACKTEST.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/EXECUTION_STRATEGY_BACKTESTER_BLUEPRINT.md` | merge_then_delete | 分层/执行侧回测以执行策略回测器蓝图为准 |
| `duplicates/FACTOR_REGISTRY_legacy_09_archive_duplicates.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md` | merge_then_delete | basename 消歧后缀；因子注册表真源在标准层 |
| `duplicates/FREE_DATA_SOURCES.md` | `docs/01_FRAMEWORK/DATA_SOURCE_LAYER_BLUEPRINT.md` | merge_then_delete | 免费/多源数据接入口径以 Layer 0 数据源层蓝图为准 |
| `duplicates/FACTOR_MINING_GUIDE.md` | `docs/02_FACTOR_LIBRARY/11_FACTOR_MINING_ENGINE/FACTOR_MINING_ENGINE_BLUEPRINT.md` | merge_then_delete | 因子挖掘以因子挖掘引擎蓝图为准 |
| `duplicates/TECHNICAL_INDICATORS.md` | `docs/03_TRADING_TACTICS/99_ARCHIVE/technical_indicators.md` | merge_then_delete | 技术指标说明以交易战术归档真源为准 |
| `duplicates/BARRA_STYLE_FACTORS.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md` | merge_then_delete | Barra/风格风险口径以 Barra 风险模型蓝图为准 |
| `duplicates/INDUSTRY_FACTORS.md` | `docs/02_FACTOR_LIBRARY/03_RISK_FACTORS/FACTOR_LIB_RISK_FACTORS_OVERVIEW.md` | merge_then_delete | 行业/风险因子归属风险因子模块概览 |
| `duplicates/TAIL_RISK_FACTORS.md` | `docs/01_FRAMEWORK/TAIL_RISK_PREDICTION_BLUEPRINT.md` | merge_then_delete | 尾部风险相关以尾部风险预测蓝图为准 |
| `duplicates/DATA_SOURCE_LAYER_GAP_ANALYSIS.md` | `docs/01_FRAMEWORK/DATA_SOURCE_LAYER_BLUEPRINT.md` | merge_then_delete | 数据源层缺口分析应对齐 Layer 0 蓝图真源 |
| `duplicates/SITEMAP.md` | `docs/02_FACTOR_LIBRARY/SITEMAP.md` | merge_then_delete | 因子库站点地图以业务目录 SITEMAP 为准 |
| `duplicates/KNOWLEDGE_MANAGEMENT.md` | `docs/10_AI_WORKFLOW/KNOWLEDGE_MANAGEMENT_BLUEPRINT.md` | merge_then_delete | 知识管理体系以知识管理蓝图为准 |
| `duplicates/research_management.md` | `docs/07_RESEARCH/INDEX.md` | merge_then_delete | 研究管理入口以 07_RESEARCH 索引为准 |
| `duplicates/factor_neutralization.md` | `docs/02_FACTOR_LIBRARY/31_FACTOR_NEUTRALIZATION/FACTOR_NEUTRALIZATION_BLUEPRINT.md` | merge_then_delete | 因子中性化以中性化模块蓝图为准 |
| `duplicates/factor_preprocessing.md` | `docs/01_FRAMEWORK/DATA_PREPROCESSING_LAYER_BLUEPRINT.md` | merge_then_delete | 预处理口径以数据预处理层蓝图为准 |
| `duplicates/FUTURE_FACTOR_TOOLS.md` | `docs/02_FACTOR_LIBRARY/11_FACTOR_MINING_ENGINE/FACTOR_MINING_ENGINE_BLUEPRINT.md` | merge_then_delete | 因子工具演进与挖掘引擎蓝图对齐 |
| `duplicates/factor_return_analysis.md` | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | merge_then_delete | 因子收益分析纳入因子-回测集成流程 |
| `duplicates/factor_synthesis.md` | `docs/02_FACTOR_LIBRARY/11_FACTOR_MINING_ENGINE/FACTOR_MINING_ENGINE_BLUEPRINT.md` | merge_then_delete | 因子合成与挖掘引擎职责一致 |
| `duplicates/factor_master_index.md` | `docs/02_FACTOR_LIBRARY/INDEX.md` | merge_then_delete | 主索引以因子库目录 INDEX 为准 |
| `duplicates/MODULE_DESIGN_PLAN.md` | `docs/module_designs/INDEX.md` | merge_then_delete | 模块设计计划入口以 module_designs 索引为准 |
| `duplicates/FACTOR_TRANSPARENCY_REPORT.md` | `docs/02_FACTOR_LIBRARY/03_RISK_FACTORS/FACTOR_LIB_RISK_FACTORS_OVERVIEW.md` | retain_trace | 透明度/暴露类叙述对齐风险因子模块（后续可独立成报告真源） |
| `duplicates/OPTIMIZATION_SUMMARY.md` | `docs/09_AUDIT/REPORTS/INDEX.md` | retain_trace | 优化类摘要应归入审计报告索引或具体报告真源 |
| `duplicates/FAQ_legacy_09_archive_duplicates.md` | `docs/02_FACTOR_LIBRARY/10_MANUAL/FAQ.md` | merge_then_delete | basename 消歧后缀；因子库 FAQ 真源在 10_MANUAL |
| `duplicates/ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_ROUND2_20260407_191332_legacy_09_archive_duplicates.md` | `docs/09_AUDIT/STATE/ALPHA_FACTOR_LAYER_DEEP_AUDIT_REPORT_ROUND2_20260407_191332.md` | retain_trace | basename 消歧后缀；审计报告真源在 09_AUDIT/STATE |
| `duplicates/HANDOVER.md` | `docs/09_AUDIT/REPORTS/ISSUE_HANDOVER_DOCUMENT_20260407.md` | retain_trace | 交接类文档以审计报告中的 issue handover 为准 |
| `duplicates/CANONICAL_POINTERS.md` | `docs/09_ARCHIVE/duplicates/CANONICAL_POINTERS.md` | keep_index | 本文件即 duplicates 池的权威 canonical 台账真源（自指）；与 INDEX 联合作为入口 |
| `duplicates/INDEX.md` | `duplicates/CANONICAL_POINTERS.md` | keep_index | 将本目录入口收敛到台账 |
| `06_ARCHIVE/overlap_FACTOR_MANAGEMENT_STANDARD_20260407_190203.md` | `docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md` | retain_trace | overlap 副本；module_id 已改为 FACTOR_GUIDE_001_OVERLAP_ARCHIVE（ADR-OC-003，2026-04-09） |
| `09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md` | `docs/09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_REGEN_20260408.md` | retain_trace | 原始版已被 REGEN 取代；module_id 已改为 _ORIG（ADR-OC-003，2026-04-09） |

## 3) 相关标准与入口

- **重复文档处理标准**：`docs/09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`
- **归档总入口**：[`docs/06_ARCHIVE/README.md`](10_GOVERNANCE_COMPLIANCE/TRAINING_SYSTEM/README.md)
