---
module_id: INDEX-ARCH-PRINCIPLES
title: "ZephyrAlpha 架构文档库 · 导航索引"
doc_type: index
rule_form: declarative
status: active
version: 1.1.0
date: 2026-08-17
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# ZephyrAlpha 架构文档库 · 导航索引

> 本索引是 `04_architecture_principles_decisions/` 的目录地图。
> 单一入口与项目全貌请读 [README.md](README.md)。本页用于快速定位具体文档。

## 一、项目现状手册（project_handbook/）— 描述"是什么"

大白话项目现状，手册 + AUTO 统计块 + 外链权威源。AUTO 块由 `generate_code_wiki_stats.py` 自动刷新。

| 文档 | 内容 | AUTO 块 | 外链权威源 |
|------|------|---------|-----------|
| [01_overview.md](project_handbook/01_overview.md) | 项目定位、大局架构、运行方式 | directory_tree / dependency_stats / external_deps | — |
| [02_repository_and_modules.md](project_handbook/02_repository_and_modules.md) | 仓库布局与全模块清单 | module_counts / py_file_total | 01_global/full_project_tree |
| [03_data_layer.md](project_handbook/03_data_layer.md) | 数据库架构全景（CH/PG/SQLite 分工） | table_counts | 05_dataflow/data_inventory |
| [04_data_sources.md](project_handbook/04_data_sources.md) | 数据源集成与下载机制 | task_counts | — |
| [05_trading_domains.md](project_handbook/05_trading_domains.md) | 交易与策略域清单 | domain_list | 02_domain_architecture_docs |
| [06_governance_and_infra.md](project_handbook/06_governance_and_infra.md) | 治理与基础设施 | governance_script_counts / gate_counts | 03_governance_reports |
| [07_dependencies.md](project_handbook/07_dependencies.md) | 依赖关系图 | edge_stats | 01_global/contract_catalog |

## 二、架构原则层（已取消，2026-07-30）

> 原 `principles/` 下 10 份原则文档已全部删除。原因：可执行约束由 `architecture_model/cross_cutting/invariants.yaml`（20 条不变量 + fitness function）+ `trae_*.yaml` 规则 + commit gates 强制执行，原则文档是已执行不变量的人类可读副本 + 通用教学，且与 depgraph 实际状态脱节。设计大纲留 git 历史。

## 三、全景图能力（panorama/）

| 文档 | 内容 |
|------|------|
| [dependency_path_panorama.md](panorama/dependency_path_panorama.md) | 依赖与路径全景图能力定位：双态模型、SSoT 分层、生成器角色、AI 查询模板 |
| [battle_map_positioning.md](panorama/battle_map_positioning.md) | 交易决策作战地图能力定位书（第五全景图 / battle_map） |
| [generator_auto_trigger_pilot.md](panorama/generator_auto_trigger_pilot.md) | 生成器自动触发机制（试点：battle_map）+ 自动触发注册表 |
| [visualization_view_template.md](panorama/visualization_view_template.md) | 可视化视图模板规范（三视图 + 可缩放 HTML） |

## 四、根级文档（本目录直属）

| 文档 | 内容 |
|------|------|
| [system_charter.md](system_charter.md) | 系统宪章 / System Charter |
| [2026-08-14_ai-liq-001_worktree_wipe_incident_review.md](2026-08-14_ai-liq-001_worktree_wipe_incident_review.md) | 架构裁定书——AI-LIQ-001 遗留项六项全面审查（worktree wipe 事故） |
| [2026-08-14_coord_reconciler_auto_delete_governance_review.md](2026-08-14_coord_reconciler_auto_delete_governance_review.md) | 架构裁定书——reconciler 自动删除/归档失控族全面审查 |

## 五、自动化说明（_automation/）

| 文档 | 内容 |
|------|------|
| [_automation/README.md](_automation/README.md) | AUTO 块清单 / 触发方式 / 生成器入口 / 维护规则 |

## 六、外部权威源矩阵（深度明细，不在本文件夹重复）

| 权威源 | 路径 | 生成器 |
|--------|------|--------|
| 全局架构图 | `docs/02_enterprise_architecture/01_global_architecture_diagram/` | generate_path_tree / generate_asset_catalog / generate_contract_catalog / generate_cross_domain_matrix / generate_integration_topology / generate_capability_heatmap |
| 域架构文档 | `docs/02_enterprise_architecture/02_domain_architecture_docs/` | generate_domain_doc |
| 数据流架构 | `docs/02_enterprise_architecture/05_dataflow_architecture/` | generate_data_inventory / generate_data_acquisition_flow / generate_dataflow_diagram |
| 决策架构 | `docs/02_enterprise_architecture/06_decision_architecture/` | generate_decision_diagram |
| 治理报告 | `docs/02_enterprise_architecture/03_governance_reports/` | generate_capacity_report / generate_constraint_violations / generate_design_vs_production |
| 全景注册表 | `docs/02_enterprise_architecture/00_overview_entry/` | generate_panorama_registry / generate_navigation_index |
| 五图对齐 | `docs/02_enterprise_architecture/generated/panorama_alignment_report.md` | align_panoramas |
