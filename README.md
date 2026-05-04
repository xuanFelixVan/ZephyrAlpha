# ZephyrAlpha v2.0

> 专业级量化交易系统 — 第二代架构

## 项目结构

```
ZephyrAlpha/
├──           # 活跃开发（新树）
│   ├── src/zephyr/           # 核心源码
│   ├── docs/                 # 项目文档
│   ├── scripts/              # 治理与工具脚本
│   ├── config/               # 配置文件
│   ├── tests/                # 测试代码
├── 模块候选池/                # 专题讨论与候选模块
├── AGENTS.md                 # AI 基准文件
└── _DO_NOT_USE_old_tree/     # 旧树归档（禁止使用）
```

你可以先在本地 fork / clone 本仓库，再进入 `` 目录。

## 快速开始

```bash
cd
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 核心文档

| 文档 | 路径 |
|------|------|
| 目录结构标准 | [directory-structure-standard.md](docs/01_policies_and_standards/governance/document/directory-structure-standard.md) |
| 规则注册表 | [governance-rules-master-registry.yaml](docs/01_policies_and_standards/_registry/catalogs/governance-rules-master-registry.yaml) |
| 文档清单 | [master-document-inventory.yaml](docs/01_policies_and_standards/_registry/catalogs/master-document-inventory.yaml) |
| 架构概览 | [00-overview.md](docs/02_enterprise_architecture/target-architecture/00-overview.md) |
| ADR 索引 | [adr/index.md](docs/02_enterprise_architecture/adr/index.md) |
| 知识库 | [08_knowledge/](docs/08_knowledge/) |

## 技术栈

- **语言**: Python 3.10+
- **数据库**: SQLite, ChromaDB
- **异步**: asyncio
- **验证**: Pydantic v2

## 许可证

MIT — 见 [LICENSE](LICENSE)
