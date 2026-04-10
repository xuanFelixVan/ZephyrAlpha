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
- **文档与链接**：修改路径后运行仓库内相关 `scripts/verify_*.py` 与 `sentinel_l1_governance_scan.py`（见 `scripts/README.md`）。
- **架构/服务目录**：合并影响 `src/api` 或模块边界时，复跑 `python scripts/generate_architecture_service_catalog.py` 并视情况提交更新后的 `docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_*`。

## 许可证

贡献内容默认以本仓库根目录 [LICENSE](LICENSE)（MIT）为准，除非另行书面约定。
