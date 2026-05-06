# ZephyrAlpha v2.0

> 专业级量化交易系统 — 第二代架构

发行版与 Python 包版本以 `pyproject.toml` 的 `version` 为准（当前 2.0.0）。根目录 [AGENTS.md](AGENTS.md) 顶部的 **v4.x** 为**治理与 AI 基准文档**的独立版本号，二者语义不同，请勿混为同一套 semver。

## 项目结构

```
ZephyrAlpha/
├── src/zephyr/               # 核心源码
├── docs/                     # 项目文档
├── scripts/                  # 治理与工具脚本
├── config/                   # 配置文件
├── tests/                    # 测试代码
├── 模块候选池/                # 本地专题讨论（默认在 .gitignore 中，不落库；需时自行创建）
├── AGENTS.md                 # AI 基准文件
└── _DO_NOT_USE_old_tree/     # 旧树归档（禁止使用）
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
| 目录结构标准 | [directory-structure-standard.md](docs/01_policies_and_standards/governance/document/directory-structure-standard.md) |
| 文档与规则元数据（SSoT） | [document-metadata-index.yaml](docs/01_policies_and_standards/_registry/catalogs/document-metadata-index.yaml) |
| 登记表总索引 | [registry-master-index.yaml](docs/01_policies_and_standards/_registry/catalogs/registry-master-index.yaml) |
| 架构概览 | [00-overview.md](docs/02_enterprise_architecture/target-architecture/00-overview.md) |
| ADR 索引 | [adr/index.md](docs/02_enterprise_architecture/adr/index.md) |
| 知识库 | [08_knowledge/](docs/08_knowledge/) |

## 技术栈

- **语言**: Python 3.11+（与 `pyproject.toml` 一致）
- **数据库**: SQLite, ChromaDB
- **异步**: asyncio
- **验证**: Pydantic v2

## 许可证

MIT — 见 [LICENSE](LICENSE)
