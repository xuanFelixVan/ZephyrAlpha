---
module_id: CONTRIBUTING
owner: System_Architect
version: 1.0.0
status: active
last_updated: 2026-04-13
---

# 贡献指南（Contributing）

本仓库以 **个人 Owner + 协作者 / AI 辅助** 为主；若你提交 PR 或参与文档治理，请先阅读下列入口。

## 必读

| 说明 | 路径 |
|------|------|
| 项目办公室（规章、任务清单、门禁） | [docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/README.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/README.md) |
| AI / 协作者交接 | [docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/PROJECT_OFFICE_AI_HANDOFF.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/PROJECT_OFFICE_AI_HANDOFF.md) |
| 蓝图图纸柜规则 | [docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/01_BLUEPRINTS_REPOSITORY_RULES.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/01_BLUEPRINTS_REPOSITORY_RULES.md) |

## 代码与风格

- Python **3.10+**（见 `pyproject.toml`）。
- 格式化/检查工具见 `pyproject.toml` 中 `[tool.black]`、`[tool.isort]`、`[tool.mypy]`；提交前建议本地运行 `black`、`isort`、`pytest`（若改动逻辑）。

## PR 约定

- **范围聚焦**：单 PR 解决一类问题，避免无关大重构。
- **文档与链接**：修改路径后运行仓库内相关 `scripts/governance/verify_*.py` 与 `scripts/governance/sentinel_l1_governance_scan.py`（根目录同名脚本为兼容转发；见 `scripts/README.md`）。
- **架构/服务目录**：合并影响 `src/api` 或模块边界时，复跑 `python scripts/governance/generate_architecture_service_catalog.py` 并视情况提交更新后的 `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*`。
- **内容重复**：大改 `.md`（或约定的 `yaml` 等）后，可复跑 `python scripts/governance/scan_duplicate_file_content.py --ext md`（可选 `--include-untracked`）；**工具总表**见 [治理工具总索引](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/GOVERNANCE_TOOLS_INDEX.md)；删稿裁决见同目录 [FILE_DELETION_OR_RETENTION_PLAYBOOK.md](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/FILE_DELETION_OR_RETENTION_PLAYBOOK.md)。
- **索引健全性（零入链候选）**：大改导航或批量搬迁 `docs/` 后，可复跑 `python scripts/governance/scan_index_health.py`；产出 `INDEX_HEALTH_ORPHAN_*`，口径见 [文档地图与放置规则](docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/00_MANAGEMENT/DOCUMENT_MAP_AND_PLACEMENT_GOVERNANCE.md) **§5.2**。

## 许可证

贡献内容默认以本仓库根目录 [LICENSE](LICENSE)（MIT）为准，除非另行书面约定。
