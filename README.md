# ZephyrAlpha v2.0.0

> 专业级量化交易系统

发行版版本以 `pyproject.toml` 为准（当前 2.0.0）。

> **AI 入群规则入口**: [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md)（IDE 自动注入，全读完再开工；规则体量随项目演进，勿写死行数）

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
# 可选：端到端演示 scripts/construction/demo_e2e_pipeline.py（L00 需 Akshare/Baostock）
pip install -r requirements-demo.txt
# 或等价：pip install -e ".[demo]"
```

### 启动应用

| 入口 | 命令 | 用途（真源：AGENTS.md §3） |
|------|------|------|
| AutoRuntime Core | `python -m zephyr.trading` | 主运行时（Dockerfile CMD） |
| zephyr CLI | `zephyr` | 主 CLI（pyproject `[project.scripts]`） |
| 数据源集成器 | `integrator status\|list\|run\|rerun-failed\|pause <src>\|resume <src>\|start` | MOD-L00-004 数据源集成器（7 子命令） |
| 主 Dashboard | `panel serve src/zephyr/frontend/dashboard/app_panel.py --port 5006` | Panel 可视化（#ARCH-047） |
| LLM Security Dashboard | `streamlit run src/zephyr/security/llm_defense/llm_security/dashboard/app.py` | 安全网关监控（MOD-SEC-app，production） |

端到端演示（依赖网络与 Akshare）：

```bash
python scripts/construction/demo_e2e_pipeline.py
```

## 核心文档

| 文档 | 路径 |
|------|------|
| 目录结构标准 | [trae_028_doc_structure_naming.yaml](docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) |
| 文档与规则元数据（SSoT） | [rule_catalog_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml) |
| 登记表总索引 | [registry_of_registries.yaml](docs/registry_of_registries.yaml) |
| 架构概览 | `docs/02_enterprise_architecture/00_overview_entry/navigation_index.md`（派生产物不入库——`python scripts/serve_docs.py` 按需生成） |
| 知识库 | `docs/08_knowledge/`（规划落盘区——ke-*.md 知识条目沉淀后生成，当前无条目；命名契约见 g4_activate/g5_extract 规则） |

## 技术栈

- **语言**: Python 3.12+（与 `pyproject.toml` 一致）
- **数据库**: 见 [infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)（PostgreSQL/ClickHouse/ChromaDB/SQLite，真源唯一）
- **异步**: asyncio
- **验证**: Pydantic v2

## 环境要求（新机器 restore 开箱即用清单）

> **灾备真源（2026-07-30 治本 #ARCH-README-BACKUP-001）**：备份配置以 [`scripts/backup/backup_config.yaml`](scripts/backup/backup_config.yaml)（v2.0.0，robocopy + CH 增量）为唯一真源；恢复步骤以 [`dr_runbook.md`](docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/dr_runbook.md)（AI 可执行操作手册）为唯一操作手册；备份清单见 [`backup_inventory.md`](docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md)。本节仅列环境要求与版本号，不重复灾备架构叙事（消除第二真源漂移；restic/MinIO 方案已于 2026-07-28 退役）。
>
> 灾备验收：新机器按本清单准备环境后，执行 `scripts/backup/restore.ps1 all` 即可恢复全部项目代码、配置与数据库 dump。

### 系统层

| 项 | 要求 | 说明 |
|---|---|---|
| 宿主 OS | Windows 11 Pro | 需启用 Hyper-V 角色 |
| VM OS | Ubuntu 22.04 LTS | Hyper-V VM，运行 ClickHouse 与数据写入调度器 |
| CPU | ≥12 核 | VM 分配 12 vCPU，宿主为 Windows 留 ≥8 逻辑处理器 |
| 内存 | ≥64 GB | VM 固定 32 GB，宿主为 Windows 留 ≥16 GB |
| D 盘 | NVMe ≥1 TB | 项目根 `D:\ZephyrAlpha` + VM 数据 VHDX |
| F 盘 | 移动硬盘 ≥2 TB | 备份仓库（robocopy 代码 + DB dump + CH VHDX 增量 + VM 周备） |

### 运行时与数据库

> **真源说明（2026-07-19 治本）**：本表版本号派生于 [infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)（基础设施真源，INFRA-DB-003/004/006）+ [pyproject.toml](pyproject.toml)（Python 依赖真源，`requires-python` + `chromadb` 下限）。升级时 MUST 先改真源再同步本表，[`GATE-README-VERSION-SYNC`](scripts/governance/d8_doc_sync/readme_version_sync_reconciler.py) reconciler 会 post-commit 自动校验漂移并 warn。

| 组件 | 版本 | 用途（真源指向） | 连接配置 |
|---|---|---|---|
| Python | >=3.12 | 主运行时（真源：[pyproject.toml](pyproject.toml) `requires-python = ">=3.12"`） | — |
| PostgreSQL | 16 | depgraph 依赖架构图库（28 表，真源：[infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) `INFRA-DB-003`） | `config/.env.postgres`（gitignored，本地自建） |
| ClickHouse | 26.6.1 | c1_market 行情仓库 + c3_fundamental 基础库，运行在 Hyper-V VM `172.24.30.100:9000`（真源：`INFRA-DB-006` note 字段） | `config/.env.clickhouse`（gitignored，本地自建） |
| ChromaDB | 0.5.23 | 向量检索（VMS 双后端过渡期，`data/vector_db/`；真源下限：[pyproject.toml](pyproject.toml) `chromadb>=0.4.24,<1.0.0`，0.5.23 为实际安装版本） | — |
| SQLite | 3.45.1 | 任务库 `governance.db`（随 Python 自带，版本随 Python 走，无独立真源） | — |

### 灾备恢复入口

> 完整恢复步骤（含前置条件、手工动作、验证命令）见 [`dr_runbook.md`](docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/dr_runbook.md)。备份产物清单见 [`backup_inventory.md`](docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md)。

```powershell
# 1. 确认 F 盘备份产物存在
.\scripts\backup\restore.ps1 inventory

# 2. 验证备份完整性（只读，安全）
.\scripts\backup\restore.ps1 verify

# 3. 灾难恢复全链路（vm → ch → pg → sqlite → code）
.\scripts\backup\restore.ps1 all
```

恢复后还需执行的手工动作详见 dr_runbook.md §2-§3（PostgreSQL 角色密码、ClickHouse VM、Python 依赖）。

## 许可证

MIT — 见 [LICENSE](LICENSE)
