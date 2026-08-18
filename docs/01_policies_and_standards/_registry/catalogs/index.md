---
module_id: GOV-002
title: "登记表集中存储目录索引"
doc_type: index
status: Active
version: "2.4.0"
date: "2026-08-17"
summary: "_registry/catalogs/ 导航入口。v2.4.0：AI-17 审计治本重写——手写文件清单（26 条，漂移率 63%）废除，改为分类导航 + 权威清单指向 registry_master_index.yaml（自动生成，永不漂移）；外部登记表 registry_id 对齐 ROOR；排除规则死链（governance/）修正。实测 64 份登记表 YAML。"
tags: [index, catalogs, registry, navigation]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
ttl: permanent
---

# Catalogs — 登记表集中存储目录

## 责任声明（Single Responsibility）

本目录存放 ZephyrAlpha 项目所有**登记表/注册表/清单类型的 YAML 文件**（doc_type=register）。

> **权威清单不手写**：本目录的完整登记表清单以 [registry_master_index.yaml](registry_master_index.yaml)
> 为唯一真源（`generate_registry_master_index.py` 自动生成，随各登记表 frontmatter 实时重建）。
> 各登记表的分层归属/责任人/条目数声明以 [ROOR](../../../registry_of_registries.yaml) 为准。
> 本索引只做分类导航，不再手工复制文件清单（手写清单必然漂移——v2.3.0 清单 26 条 vs 实测 64 条的教训）。

## 分类导航（2026-08-17 实测：64 份登记表 YAML + `_index.yaml` + `_archive/`）

| 类别 | 数量 | 代表文件 | 说明 |
|------|:---:|---------|------|
| 总索引与一致性契约 | 2 | `registry_master_index.yaml`（auto）、`registry_consistency_contract.yaml` | 目录总索引（自动生成）+ 跨登记表共享字段一致性契约 |
| 规则/门禁治理 | 9 | `rule_catalog_registry.yaml`（auto）、`gate_registry.yaml`（auto）、`rule_enforcement_registry.yaml`、`ruling_registry.yaml`、`in_process_gate_registry.yaml`、`noqa_exempt_registry.yaml`、`panorama_exempt_list.yaml`、`rule_ai_perception_index.yaml`、`rule_registry_collection.yaml` | 规则目录/门禁清单/裁定登记 |
| 架构治理登记 | 11 | `architecture_issue_registry.yaml`（#ARCH-*）、`candidate_module_registry.yaml`（CAND-*）、`capability_canonical_file_registry.yaml`（能力反查+creation_tokens）、`module_translation_registry.yaml`（模块中英翻译 SSoT）、`generator_registry.yaml`、`scripts_registry.yaml`、`test_suite_registry.yaml`、`migration_registry.yaml`（冻结）、`derived_identifier_registry.yaml`、`domain_naming_rules.yaml`、`hard_boundaries_registry.yaml` | 议题/候选/能力/翻译/迁移等架构治理真源 |
| 域/目录/依赖 | 7 | `functional_domain_registry.yaml`、`directory_registry.yaml`、`cross_module_dependency_registry.yaml`、`interface_contract_registry.yaml`、`business_streams_registry.yaml`、`governance_convergence_map.yaml`、`battle_map_domain_policy.yaml` | 功能域/目录/跨模块依赖/契约 |
| AI 治理 | 5 | `ai_autonomy_authority_registry.yaml`、`ai_risk_register.yaml`、`ai_session_registry.yaml`、`frontier_llm_benchmark_ranking.yaml`、`trust_boundary_surface_registry.yaml` | AI 权限/风险/会话/信任边界 |
| 元数据/文档治理 | 8 | `frontmatter_field_registry.yaml`、`terminology_glossary.yaml`（术语仲裁源）、`task_card_meta_registry.yaml`、`knowledge_article_registry.yaml`、`declarative_contract_tracker_registry.yaml`、`external_contract_verification_registry.yaml`、`depgraph_scan_exclusions.yaml`、`infrastructure_registry.yaml` | frontmatter 字段/术语/任务卡/知识条目 |
| 业务注册表（#ARCH-BREG-001 等） | 21 | 回测三件套 `universe_registry.yaml`/`benchmark_registry.yaml`/`cost_model_registry.yaml`；被测对象 `factor_registry.yaml`/`strategy_registry.yaml`；交易风控 `risk_limit_registry.yaml`/`technical_indicator_registry.yaml`/`chart_pattern_registry.yaml`/`execution_algo_registry.yaml`/`data_asset_registry.yaml`；元数据 `field_dictionary.yaml`/`experiment_registry.yaml`；扩展 `seat_registry.yaml`/`regime_cycle_registry.yaml`/`model_registry.yaml`/`event_calendar_registry.yaml`/`macro_indicator_registry.yaml`/`portfolio_model_registry.yaml`；合规监控 `feature_adjudication_registry.yaml`/`compliance_report_registry.yaml`/`alert_threshold_registry.yaml` | 量化交易业务对象唯一真源（SSoT），详见 ROOR tier-2 业务注册表块 |
| 数据流图（迁移中） | 1 | `dataflow_graph_registry.yaml` | dataflowgraph 同步真源（sync_yaml_to_depgraph.py 消费）；与 `data_asset_registry.yaml` 的 S6 改名收口以 ROOR REG-DATAFLOW-001 注记为准 |

> 另有 `_index.yaml`（TRAE 规则高级别名表 PS-REG-001，RULE-ZERO..RULE-TWENTY）与 `_archive/`（归档区，如 candidate_module_registry_harvest_archive.yaml 5283 条 HARVEST 候选归档）。

## 外部登记表（不在本目录，由 ROOR 索引引用）

| 文件 | 位置 | registry_id（以 ROOR 为准） |
|------|------|:--:|
| 模块 ID 注册表 | `architecture_model/module_id_registry.yaml` | REG-MOD-ID-001 |
| 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | REG-BLUEPRINT-001 |
| Embedding 模型注册表 | `config/embedding_model_registry.yaml` | REG-EMBED-001 |

## 排除规则（不应放入本目录的内容）

- ❌ policy/standard/rule 类文件 → `docs/01_policies_and_standards/rules/`（trae_*.yaml）
- ❌ template 类文件 → `docs/01_policies_and_standards/templates/`
- ✅ YAML 格式的登记表允许存放在此，优先使用 YAML 格式
- ❌ 架构模型 YAML → `architecture_model/`
- ❌ 运行时配置 YAML → `config/` 或 `src/zephyr/` 对应子包

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 2.4.0 | 2026-08-17 | AI-17 审计治本重写。(1) 废除手写文件清单（v2.3.0 仅 26 条，实测 64 份，漂移率 63%），改为分类导航 + 权威清单指向 registry_master_index.yaml（自动生成）与 ROOR（分层/责任人）。(2) 外部登记表 registry_id 对齐 ROOR（REG-MOD-ID-001/REG-BLUEPRINT-001/REG-EMBED-001，原 REG-MOD-ALPHA_SIGNAL_DOMAIN/REG-MOD-003/REG-AI-002 与 ROOR 矛盾）。(3) 排除规则死链修正（governance/ 目录已删除 → rules/）。(4) 补 21 个业务注册表与全部漏登文件分类归属。 |
| 2.3.0 | 2026-06-26 | P2-1 向内收——删除 document_metadata_index_registry.yaml（与 rule_catalog_registry.yaml 同源同数据的真重复），所有引用重定向至 rule_catalog_registry.yaml（PS-REG-018）。计数 28→27→26。 |

## 父级目录

- 父级：[_registry](../index.md)
- 总索引：[registry_master_index.yaml](registry_master_index.yaml)（自动生成，权威清单）
- 分层索引：[ROOR](../../../registry_of_registries.yaml)（注册表的注册表）
