---
ttl: permanent
doc_type: architecture_view
title: 文档自动化说明 / Documentation Automation
owner: ZephyrAlpha-Owner
language: zh
---

# 文档自动化说明

> 本文件夹的文档分三类维护方式：手工区 / 自动区 / 外链区。
> 自动区由生成器全自动刷新，遵循项目铁律"永久系统必须全自动（自动触发/运行/维护/关闭）"。

## 一、维护方式分类

| 方式 | 标识 | 谁维护 | 何时变 |
|------|------|--------|--------|
| **手工区** | 普通正文 | 人工 | 概念/设计变更时 |
| **自动区** | `<!-- AUTO-START:name -->` ... `<!-- AUTO-END:name -->` 标记块 | 生成器 | depgraph 刷新时自动 |
| **外链区** | 链接到 `docs/02/{00,01,02,05,06}/` | 各自的生成器 | 各自触发 |

> **铁律**：自动区标记块内内容禁止手工编辑（会被生成器覆盖）。要改统计口径，改生成器（`generate_code_wiki_stats.py`），不改文档。

## 二、生成器

**入口**：[scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py](../../../../scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py)

- **职责**：从数据源（depgraph PG / pyproject.toml / 文件系统扫描 / table_registry / YAML 真源）拉取统计，更新 `project_handbook/*.md` 与 `README.md` 中的 AUTO 标记块。
- **触发**：`event_driven`，由 `generate_project_depgraph.py` 刷新钩子触发（depgraph 运营态刷新后自动同步统计）。
- **不变量**：只更新 AUTO 标记内、不碰手工区、输出幂等、双语格式。
- **错误契约**：depgraph 不存在→exit 1；目标文件不存在→exit 1；标记块缺失→跳过该块并 warning。

调用：

```bash
python -m scripts.governance.d5_architecture.generators.generate_code_wiki_stats
```

## 三、AUTO 块清单

| AUTO 块名 | 目标文件 | 数据源 | 已有/新增 |
|-----------|---------|--------|----------|
| `project_snapshot` | README.md | depgraph PG 聚合 | 新增 |
| `directory_tree` | project_handbook/01_overview.md | FS 扫描 src/zephyr + scripts/governance | 已有（迁移） |
| `dependency_stats` | project_handbook/01_overview.md | depgraph PG nodes/edges | 已有（迁移） |
| `external_deps` | project_handbook/01_overview.md | pyproject.toml [project.dependencies] | 已有（迁移） |
| `module_counts` | project_handbook/02_repository_and_modules.md | src/zephyr 包/文件计数 + module_id_registry.yaml | 新增 |
| `py_file_total` | project_handbook/02_repository_and_modules.md | src/zephyr .py 文件总数 | 新增 |
| `table_counts` | project_handbook/03_data_layer.md | table_registry 内存加载（CH/PG/SQLite 表数） | 新增 |
| `task_counts` | project_handbook/04_data_sources.md | architecture_model/data/data_sources_registry.yaml | 新增 |
| `domain_list` | project_handbook/05_trading_domains.md | depgraph PG domains + nodes 按域聚合 | 新增 |
| `governance_script_counts` | project_handbook/06_governance_and_infra.md | scripts/governance/d*/ 扫描 | 已有（迁移） |
| `gate_counts` | project_handbook/06_governance_and_infra.md | CommitGateRegistry | 新增 |
| `edge_stats` | project_handbook/07_dependencies.md | depgraph PG edges 按类型聚合 | 新增 |

## 四、外链权威源（不在本文件夹重复的全量明细）

深度明细（完整表清单 / 全模块树 / 全契约 / 全域文档）由各自的生成器产出在 `docs/02_enterprise_architecture/{00,01,02,05,06}/`，本文件夹只放**易变统计量**（计数/汇总/速查表），遵守 SSoT 铁律与"全景图是真源"。

| 权威源 | 生成器 | 输出位置 |
|--------|--------|---------|
| 全项目树 | generate_path_tree | 01_global_architecture_diagram/full_project_tree_{en,zh}.md |
| 资产目录 | generate_asset_catalog | 01_global_architecture_diagram/asset_catalog.md |
| 契约目录 | generate_contract_catalog | 01_global_architecture_diagram/contract_catalog.md |
| 域文档 | generate_domain_doc | 02_domain_architecture_docs/ |
| 数据清单 | generate_data_inventory | 05_dataflow_architecture/data_inventory.md |
| 决策图 | generate_decision_diagram | 06_decision_architecture/ |
| 治理报告 | generate_capacity_report 等 | 03_governance_reports/ |
| 全景注册表 | generate_panorama_registry | 00_overview_entry/panorama_registry.md |
| 五图对齐 | align_panoramas | generated/panorama_alignment_report.md |

## 五、SSoT 红线

- handbook AUTO 块**只读**真源（depgraph PG / YAML / table_registry / pyproject），**禁止反向写**。
- 规则数据真源 = YAML（`architecture_model/`、`docs/01_policies_and_standards/rules/`）→ `sync_yaml_to_depgraph.py` 单向同步到 DB。
- 架构数据真源 = PostgreSQL depgraph → `apply_depgraph.py` / `generate_project_depgraph.py` 直接写。
- 改统计口径 = 改生成器，不改文档；原则文档层（`principles/`）已于 2026-07-30 取消——可执行约束真源为 `architecture_model/cross_cutting/invariants.yaml` + `trae_*.yaml` 规则 + commit gates。
