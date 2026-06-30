# ZephyrAlpha v2.0.0

> 专业级量化交易系统

发行版版本以 `pyproject.toml` 为准（当前 2.0.0）。

> **AI 入群规则入口**: [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md)（IDE 自动注入，87 行，全读完再开工）

## 项目结构

```
ZephyrAlpha/
├── src/zephyr/               # 核心源码
├── docs/                     # 项目文档
├── scripts/                  # 治理与工具脚本
├── config/                   # 配置文件
├── tests/                    # 测试代码
├── AGENTS.md                 # AI 基准文件
```

## 快速开始

```bash
cd D:\ZephyrAlpha
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
# 可选：端到端演示 demo_e2e_pipeline.py（L00 需 Akshare）
pip install -r requirements-demo.txt
# 或等价：pip install -e ".[demo]"
```

端到端演示（依赖网络与 Akshare）：

```bash
python demo_e2e_pipeline.py
```

## 核心文档

| 文档 | 路径 |
|------|------|
| 目录结构标准 | [directory_structure_standard.md](docs/01_policies_and_standards/rules/directory_structure_standard.md) |
| 文档与规则元数据（SSoT） | [rule_catalog_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml) |
| 登记表总索引 | [registry_of_registries.yaml](docs/registry_of_registries.yaml) |
| 架构概览 | [navigation_index.md](docs/02_enterprise_architecture/00_overview_entry/navigation_index.md) |
| ADR 索引 | 已迁入 KB decisions namespace（SQLite knowledge 表） |
| 知识库 | [08_knowledge/](docs/08_knowledge/) |

## 技术栈

- **语言**: Python 3.11+（与 `pyproject.toml` 一致）
- **数据库**: SQLite, ChromaDB
- **异步**: asyncio
- **验证**: Pydantic v2

## 许可证

MIT — 见 [LICENSE](LICENSE)
