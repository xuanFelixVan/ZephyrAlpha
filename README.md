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
python scripts/demos/demo_e2e_pipeline.py
```

## 核心文档

| 文档 | 路径 |
|------|------|
| 目录结构标准 | [trae_028_doc_structure_naming.yaml](docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) |
| 文档与规则元数据（SSoT） | [rule_catalog_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml) |
| 登记表总索引 | [registry_of_registries.yaml](docs/registry_of_registries.yaml) |
| 架构概览 | [navigation_index.md](docs/02_enterprise_architecture/00_overview_entry/navigation_index.md) |
| 知识库 | [08_knowledge/](docs/08_knowledge/) |

## 技术栈

- **语言**: Python 3.12+（与 `pyproject.toml` 一致）
- **数据库**: 见 [infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)（PostgreSQL/ClickHouse/ChromaDB/SQLite，真源唯一）
- **异步**: asyncio
- **验证**: Pydantic v2

## 环境要求（新机器 restore 开箱即用清单）

> 灾备验收标准：新机器按本清单准备环境后，执行 `scripts/backup/restore.ps1 latest` 即可恢复全部项目代码、配置与数据库 dump。详见 [disaster_recovery_backup/blueprint.md](docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md)。

### 系统层

| 项 | 要求 | 说明 |
|---|---|---|
| 宿主 OS | Windows 11 Pro | 需启用 Hyper-V 角色 |
| VM OS | Ubuntu 22.04 LTS | Hyper-V VM，运行 ClickHouse 与数据写入调度器 |
| CPU | ≥12 核 | VM 分配 12 vCPU，宿主为 Windows 留 ≥8 逻辑处理器 |
| 内存 | ≥64 GB | VM 固定 32 GB，宿主为 Windows 留 ≥16 GB |
| D 盘 | NVMe ≥1 TB | 项目根 `D:\ZephyrAlpha` + VM 数据 VHDX |
| F 盘 | 移动硬盘 ≥2 TB | restic 备份仓库 + ClickHouse 备份中转（即异地副本） |

### 运行时与数据库

> **真源说明（2026-07-19 治本）**：本表版本号派生于 [infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)（基础设施真源，INFRA-DB-003/004/006）+ [pyproject.toml](pyproject.toml)（Python 依赖真源，`requires-python` + `chromadb` 下限）。升级时 MUST 先改真源再同步本表，[`GATE-README-VERSION-SYNC`](scripts/governance/d8_doc_sync/readme_version_sync_reconciler.py) reconciler 会 post-commit 自动校验漂移并 warn。

| 组件 | 版本 | 用途（真源指向） | 连接配置 |
|---|---|---|---|
| Python | >=3.12 | 主运行时（真源：[pyproject.toml](pyproject.toml) `requires-python = ">=3.12"`） | — |
| PostgreSQL | 16 | depgraph 依赖架构图库（28 表，真源：[infrastructure_registry.yaml](docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) `INFRA-DB-003`） | [config/.env.postgres](config/.env.postgres) |
| ClickHouse | 26.6.1 | c1_market 行情仓库 + c3_fundamental 基础库，运行在 Hyper-V VM `172.24.30.100:9000`（真源：`INFRA-DB-006` note 字段） | [config/.env.clickhouse](config/.env.clickhouse) |
| ChromaDB | 0.5.23 | 向量检索（VMS 双后端过渡期，`data/vector_db/`；真源下限：[pyproject.toml](pyproject.toml) `chromadb>=0.4.24,<1.0.0`，0.5.23 为实际安装版本） | — |
| SQLite | 3.45.1 | 任务库 `governance.db`（随 Python 自带，版本随 Python 走，无独立真源） | — |

### 外部工具

> **真源说明**：本表为宿主实际安装版本，无项目内真源（灾备恢复时按表中所列版本安装）。`pg_dump` 版本随 PostgreSQL 16 安装，Hyper-V 为 Windows 内置功能。

| 工具 | 版本 | 用途 | 获取 |
|---|---|---|---|
| git | 2.48+ | 版本控制 | https://git-scm.com/ |
| restic | 0.19.1 | 灾备备份（AES-256 加密 + CDC 去重） | https://restic.net/ |
| MinIO | RELEASE.2025-07-23 | ClickHouse 备份中转对象存储 | `D:\tools\minio\minio.exe` |
| pg_dump | 16.14 | PostgreSQL dump（随 PostgreSQL 16 安装） | `C:\Program Files\PostgreSQL\16\bin\` |
| Hyper-V | Windows 内置 | ClickHouse VM 虚拟化 | 启用 Windows 功能 |

### 凭据与配置文件

| 文件 | 用途 | 灾备注意 |
|---|---|---|
| [config/.env.postgres](config/.env.postgres) | PostgreSQL 连接（含 `zephyr` 角色密码） | 备份内含，restore 后可直接读 |
| [config/.env.clickhouse](config/.env.clickhouse) | ClickHouse 连接（`172.24.30.100:9000`） | 备份内含 |
| [config/.env.ch_backup](config/.env.ch_backup) | MinIO + CH S3 备份凭据 | 备份内含 |
| [config/.env.restic](config/.env.restic) | **restic 仓库加密密码** | ⚠️ **必须离线物理副本**（U盘/纸质）— 密码本身在备份内被仓库加密，无密码无法解密备份 = 死锁 |

### 关键路径

| 路径 | 内容 |
|---|---|
| `D:\ZephyrAlpha\` | 项目根（代码、配置、文档、SQLite DB、向量库） |
| `D:\tmp_db_dumps\` | PostgreSQL dump 临时输出（备份过程产物） |
| `F:\restic-zephyr\` | restic 仓库（项目代码 + PG dump，AES-256 加密） |
| `F:\ch_backup_store\` | ClickHouse 备份中转（MinIO bucket `chbk`，输出 `market.zip`） |
| Hyper-V VM `172.24.30.100` | ClickHouse 数据库（`/var/lib/clickhouse`，3000 亿条行情） |

### 灾备恢复入口

```powershell
# 1. 列出所有快照
.\scripts\backup\restore.ps1 list

# 2. 验证某快照（restore 到 D:\restore_test\，不动生产）
.\scripts\backup\restore.ps1 verify <snapshot_id>

# 3. 灾难恢复最新快照到 D:\ZephyrAlpha\
.\scripts\backup\restore.ps1 latest

# 4. 恢复 ClickHouse（从 F:\ch_backup_store\chbk\market.zip）
.\scripts\backup\restore.ps1 ch
```

恢复后还需执行的手工动作：
1. **PostgreSQL 角色密码**：`pg_roles` dump 不含密码哈希，需手工 `ALTER ROLE zephyr PASSWORD '...';`
2. **ClickHouse VM**：需先在 Hyper-V 管理器重建 Ubuntu VM（IP `172.24.30.100`），安装 ClickHouse 26.6.1，再用 `restore.ps1 ch` 恢复数据
3. **Python 依赖**：
   ```powershell
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## 许可证

MIT — 见 [LICENSE](LICENSE)
