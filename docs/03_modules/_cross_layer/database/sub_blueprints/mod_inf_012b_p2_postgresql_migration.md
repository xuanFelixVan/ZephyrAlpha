---
module_id: MOD-DB_DEPGRAPH_PG
submodule_path: src/zephyr/infrastructure/db
title: "P2 PostgreSQL迁移详细施工方案 — depgraph从SQLite迁移到PostgreSQL"
doc_type: blueprint
status: Active
version: "1.0.0"
layer: L1_foundation
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260625-P2
date: "2026-06-25"
valid_from: "2026-06-25"
ttl: permanent
rule_form: structural
belongs_to: "SH-DB-001"
parent_module: "SH-DB-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: completed
actual_disk_path: ''
codification_level: L2
generation: 3
functional_domain: data
summary: "P2中期方案——将depgraph从SQLite迁移到PostgreSQL，获得MVCC并发能力，支持40+AI并发写入不同功能域。覆盖Windows原生安装、数据迁移、SQL方言调整、文件锁删除、连接配置、红蓝测试6大施工阶段。"
tags: [postgresql, migration, mvcc, depgraph, concurrency, p2, database-upgrade]
priority: P1
runtime_plane: hot
depends_on:
  - {target: "SH-DB-001", at: "全篇", why: "父蓝图——Database集成蓝图"}
  - {target: "trae_054", at: "§no_split", why: "禁止拆分depgraph——迁移后仍为单库单文件(SSoT)"}
  - {target: "D50", at: "裁定", why: "3库架构裁定——需更新为PostgreSQL"}
references:
  - {id: "MOD-INF-012A", at: "全篇", why: "Database Core——SQLite+DuckDB已实现部分"}
  - {id: "ARCH-CAP-002", at: "v1.0.8", why: "容量治理二元规则——迁移后仍适用"}
  - {id: "trae_054", at: "全篇", why: "depgraph访问协议——迁移后访问方式变更"}
---

# P2 PostgreSQL迁移详细施工方案 — depgraph从SQLite迁移到PostgreSQL

> module_id: MOD-DB_DEPGRAPH_PG | version: 1.0.0 | status: Active | belongs_to: SH-DB-001
> 施工阶段: P2（中期：治本） | 目标: 迁移depgraph.db到PostgreSQL，获得MVCC并发能力

## 文档使用说明

本文档是P2 PostgreSQL迁移的**唯一施工真源**。所有任务卡必须以本文档为准。文档中每个施工步骤都标注了 `[动作N]` 编号，对应任务卡中的具体执行项。

**文档自审规则**：本文档完成后必须经过循环审查，检查前后冲突，直到问题数=0。审查清单见§十三。

---

## 一、迁移目标与背景

### 1.1 问题根因

当前 `depgraph` 使用 SQLite，存在以下致命限制：

| 限制 | 根因 | 影响 |
|------|------|------|
| **文件级EXCLUSIVE锁** | SQLite写操作获取EXCLUSIVE锁，全局唯一 | 40个AI并发写入时，39个必须等待 |
| **WAL不支持并发写** | WAL模式仅支持"并发读+单写" | 写入串行化，吞吐量瓶颈 |
| **busy_timeout超时** | 超时后抛 `database is locked` | AI任务失败，需重试 |
| **_db_write_lock补丁** | apply_depgraph.py用threading.Lock+文件锁双重保护 | 锁粒度=整个depgraph文件，非功能域分区 |
| **sync_yaml_to_depgraph.py无锁** | 完全无锁保护 | 与其他写入并发会产生数据损坏 |

### 1.2 迁移目标

| 目标 | 量化指标 | 验证方式 |
|------|---------|---------|
| MVCC并发写入 | 40并发写不同domain_id的行，近线性加速 | 红蓝测试（§九） |
| 行级锁 | 不同domain_id的写入不互斥 | 并发写入测试 |
| 连接池 | PostgreSQL直连（无需连接池），max_connections=200 | 连接数监控 |
| 数据零丢失 | SQLite数据100%迁移到PostgreSQL | 行数对比校验 |
| 零停机回滚 | 可随时回滚到SQLite | 回滚脚本验证 |

### 1.3 架构裁定更新

> ⚠️ 历史裁定记录。当前数据库清单真源：`infrastructure_registry.yaml`（INFRA-DB-001~005，详见 AGENTS.md §11.0）。

**原D50裁定**：3库：governance.db(SQLite)+depgraph(SQLite)+market.duckdb(DuckDB)

**P2更新裁定（D50-PG）**：
- depgraph → PostgreSQL（获得MVCC并发能力）
- governance.db → 保持SQLite（任务卡系统，单写者足够，无并发写入需求）

> **更新（2026-07-04，ARCH-046）**：market.duckdb（原 INFRA-DB-005）已彻底删除（墓碑清理）。原"保持DuckDB"裁定已被 supersede，业务行情数据迁移至 ClickHouse c1_market（INFRA-DB-006）见 c1_market_clickhouse.md。当前实际为 4 库：depgraph（PostgreSQL）+ governance.db（SQLite）+ DuckDB OLAP（:memory:）+ ClickHouse c1_market。

**理由**：只有depgraph面临40+AI并发写入问题。governance.db（任务卡）由TaskRepository单写者管理，market.duckdb（行情数据）由数据管道串行写入。迁移范围最小化，降低风险。

### 1.4 不变的设计哲学

迁移后以下设计哲学**不变**：

| 设计哲学 | 迁移后如何保持 | 依据 |
|---------|-------------|------|
| **SSoT单一真源** | depgraph仍是单库（PostgreSQL单database），不拆分 | trae_054 §no_split |
| **全局视图** | 所有域数据在同一database中，跨域查询无需跨库 | 全景图§二 |
| **双态模型** | design_maturity字段保留，production/draft分区不变 | depgraph_schema.py |
| **机械判定** | SQL查询不变，仅方言调整 | depgraph_schema.py |
| **按domain_id逻辑分区** | 数据按domain_id逻辑分区，不同功能域写入数据不重叠 | project_memory |

---

## 二、迁移影响范围总览

### 2.1 影响范围统计（基于4个深度调研报告）

| 类别 | 数量 | 严重度 | 详情 |
|------|------|:---:|------|
| SQLite连接点 | 100+ | 高 | `src/`下64个文件共105处`?`占位符 |
| INSERT OR REPLACE | 28处 | 高 | 需改为`ON CONFLICT DO UPDATE` |
| PRAGMA语句 | 20+处 | 高 | 需全部删除（PG无对应） |
| AUTOINCREMENT | 25+处 | 高 | 需改为`GENERATED AS IDENTITY` |
| datetime('now') | 20+处 | 中 | 需改为`now()` |
| GROUP_CONCAT | 7处 | 中 | 需改为`string_agg` |
| 触发器定义 | 35个唯一 | 高 | 需用PL/pgSQL重写 |
| FTS5定义 | 5处 | 中 | 需改为PG tsvector + GIN |
| writable_schema | 3处 | 高 | 需完全删除（PG无此功能） |
| cursor.lastrowid | 8处 | 中 | 需改为`INSERT ... RETURNING id` |
| sqlite_master查询 | 15处 | 中 | 需改为`information_schema` |
| json_valid/json_extract | 8处 | 中 | 需改为PG JSON操作符 |
| GLOB | 1处(CHECK) | 低 | 需改为`~`正则 |
| 文件锁机制 | 24个 | 高 | 需删除/改造 |
| 写入脚本 | 12个 | 高 | 需SQL方言调整 |
| 只读触发器 | 27个(9表×3) | 高 | 需用PL/pgSQL重写 |
| 文档/规则文件 | 15+个 | 中 | 需同步更新 |
| 测试文件 | 14+个 | 中 | 需SQL方言调整 |

### 2.2 数据量基线

| 表 | 行数 | 说明 |
|----|------|------|
| nodes | 14,383 | 所有代码制品节点 |
| edges | 22,605 | 制品间依赖关系 |
| domains | 55 | 功能域 |
| 其他表 | ~500 | 规则、模板、事件等 |
| **总数据量** | ~39.2MB | SQLite文件大小 |

### 2.3 DB_PATH 真源与散布情况（必须同步修改）

> **注意**：以下行号为 2026-06-27 核查记录，实际修改前请用 `grep -rn "DB_PATH\s*=\|depgraph\.db" <文件路径>` 验证当前行号。
> **关键澄清**：`DB_PATH` 在项目中并非干净 SSoT——`governance.db` 与 `depgraph` 是两个不同数据库，各自有定义点。本迁移只动 `depgraph`。

**A. depgraph 路径定义（本迁移范围，必须改为 PostgreSQL 连接串）**

| # | 文件路径 | 行号(参考) | 当前定义 | 迁移后 |
|---|---------|------|---------|--------|
| 1 | `src/zephyr/governance/depgraph_schema.py` | 71 | `DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"`（**Schema 真源**） | PG 连接配置 |
| 2 | `src/zephyr/governance/depgraph_reader.py` | 48 | `DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"` | PG 连接配置 |
| 3 | `src/zephyr/governance/rule_engine.py` | 51 | `_DB_PATH = ... depgraph.db` | PG 连接配置 |
| 4 | `src/zephyr/governance/rule_watcher.py` | 60 | `_DEFAULT_DB_PATH = ... depgraph.db` | PG 连接配置 |
| 5 | `src/zephyr/governance/auto_runner.py` | 42 | `_DEPGRAPH_DB = ... depgraph.db` | PG 连接配置 |
| 6 | `src/zephyr/governance/blast_radius.py` | 45 | 硬编码 `Path("D:/ZephyrAlpha/data/databases/depgraph.db")` | PG 连接配置（消除硬编码） |
| 7 | `src/zephyr/governance/database_service.py` | 59 | 硬编码 `r"D:\ZephyrAlpha\data\databases\depgraph.db"` | PG 连接配置（消除硬编码） |

**B. governance.db 路径定义（不在本迁移范围，保持 SQLite）**

| # | 文件路径 | 行号(参考) | 当前定义 | 处理 |
|---|---------|------|---------|------|
| 1 | `src/zephyr/shared/io/paths.py` | 67 | `DB_PATH = REPO_ROOT / "data" / "databases" / "governance.db"`（governance.db 真源） | 不变 |
| 2 | `src/zephyr/governance/sqlite_schema.py` | 77 | `DB_PATH = _find_repo_root() / "data" / "databases" / "governance.db"` | 不变 |

**C. scripts/ 下散布的 depgraph 路径定义（约 28 处）**

`scripts/governance/` 与 `scripts/ops/` 下多个脚本各自定义 depgraph 路径（如 `apply_depgraph.py`、`audit_domain_nodes.py`、`check_rule_four_way_alignment.py`、`generate_project_depgraph.py` 等），部分硬编码 `D:/ZephyrAlpha/...`。完整清单见受影响文件索引（并发审查文档），迁移时需统一改为从 `depgraph_schema.py` 导入 PG 连接配置，消除散布与硬编码。

> **治理原则**：迁移后 depgraph 的 PG 连接配置应收敛到 `depgraph_schema.py` 单一真源，其他文件通过 `from zephyr.governance.depgraph_schema import get_db_connection` 复用，禁止重复定义。

---

## 三、施工阶段总览

| 阶段 | 名称 | 依赖 | 风险 | 预计任务卡数 |
|:---:|------|------|:---:|:---:|
| 1 | Windows原生安装PostgreSQL | 无 | 中 | 1 |
| 2 | 数据迁移脚本（SQLite→PostgreSQL） | 阶段1 | 高 | 1 |
| 3 | SQL方言调整（SQLite特有语法→PG标准） | 阶段2 | 高 | 3（按文件分组） |
| 4 | 删除文件锁补丁 | 阶段3 | 中 | 1 |
| 5 | 连接配置 | 阶段1 | 低 | 1 |
| 6 | 红蓝测试验证并发写入 | 阶段3-5 | 中 | 1 |
| - | **合计** | - | - | **8个任务卡** |

每个任务卡后面跟一个元任务卡（循环审查修复），共**8个任务卡 + 8个元任务卡 = 16个卡**。

---

## 四、阶段1：Windows原生安装PostgreSQL

### 4.1 前置条件

- [ ] Windows 10/11（x64）操作系统
- [ ] 管理员权限（用于安装和注册Windows服务）
- [ ] D盘有至少5GB可用空间（PostgreSQL数据目录）
- [ ] 端口5432未被占用

### 4.2 详细施工步骤

#### [动作1] 下载并安装PostgreSQL 16

**操作**：

1. 从 https://www.postgresql.org/download/windows/ 下载 PostgreSQL 16 的 EDB 图形化安装包（`postgresql-16.x-windows-x64.exe`）。
2. 以管理员身份运行安装程序，按图形化向导逐步安装：
   - **安装目录**：保持默认 `C:\Program Files\PostgreSQL\16`（或自定义到D盘）
   - **数据目录**：保持默认 `C:\Program Files\PostgreSQL\16\data`（或自定义）
   - **超级用户密码**：为 `postgres` 超级用户设置强密码（请妥善保存，本方案后续以 `<postgres_password>` 占位）
   - **端口**：`5432`
   - **区域设置**：`Default locale`（或 `C` 以获得最佳性能）
   - **服务配置**：勾选"Install as a Windows Service"，服务名保持默认 `postgresql-x64-16`，启动类型选择"自动"
3. 安装完成时勾选取消"Launch Stack Builder"（无需额外组件）。

**安装后验证**：

```powershell
# 检查Windows服务状态（应为 Running）
Get-Service postgresql-x64-16
```

**预期输出**：`Status=Running, Name=postgresql-x64-16, DisplayName=postgresql-x64-16 - PostgreSQL Server 16`。

#### [动作2] 创建数据库和用户

**操作**：在PowerShell中执行（会提示输入postgres超级用户密码）

```powershell
# 创建应用用户 zephyr
psql -U postgres -c "CREATE USER zephyr WITH PASSWORD 'zephyr_dev_2026';"

# 创建 depgraph (PostgreSQL)，属主为 zephyr
psql -U postgres -c "CREATE DATABASE depgraph OWNER zephyr ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;"

# 授予 zephyr 用户在 depgraph (PostgreSQL)的全部权限
psql -U postgres -d depgraph -c "GRANT ALL ON DATABASE depgraph TO zephyr;"
```

**说明**：
- 应用连接统一使用 `zephyr` 用户，不使用 `postgres` 超级用户。
- `zephyr_dev_2026` 仅为开发环境示例密码，生产环境请使用强密码并通过 `config/.env.postgres` 注入。

#### [动作3] 创建扩展初始化脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\migrate_sqlite_to_pg\01_create_extensions.sql`

**操作**：创建新文件，内容如下：

```sql
-- 创建扩展（pg_stat_statements用于监控，pgcrypto用于UUID生成）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- P3阶段将添加的扩展（预先创建占位注释）：
-- CREATE EXTENSION IF NOT EXISTS vector;  -- P3: pgvector
```

#### [动作4] 安装扩展

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
psql -U zephyr -d depgraph -f scripts\governance\migrate_sqlite_to_pg\01_create_extensions.sql
```

**预期输出**：`CREATE EXTENSION` × 2。

#### [动作5] 配置 .env.postgres

**文件路径**：`d:\ZephyrAlpha\config\.env.postgres`

**操作**：创建新文件，内容如下：

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=depgraph
POSTGRES_USER=zephyr
POSTGRES_PASSWORD=zephyr_dev_2026
```

**注意**：此文件必须加入`.gitignore`，禁止提交密码到仓库。

**更新.gitignore**：

**文件路径**：`d:\ZephyrAlpha\.gitignore`

在文件末尾追加以下行：

```gitignore

# PostgreSQL secrets
config/.env.postgres
data/databases/postgres/
```

#### [动作6] 验证服务运行

**操作**：在PowerShell中执行

```powershell
# 检查Windows服务状态
Get-Service postgresql-x64-16

# 检查PostgreSQL健康
pg_isready -U zephyr -d depgraph

# 验证连接（执行简单查询）
psql -U zephyr -d depgraph -c "SELECT 1;"

# 验证扩展已安装
psql -U zephyr -d depgraph -c "\dx"
```

**预期输出**：
- `Get-Service` 返回 `Status=Running`
- `pg_isready` 返回 `accepting connections`
- `SELECT 1` 返回 `1`
- `\dx` 显示 `pg_stat_statements` 和 `pgcrypto` 扩展

### 4.3 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | PostgreSQL服务运行 | `Get-Service postgresql-x64-16` | Status=Running |
| 2 | PostgreSQL可连接 | `pg_isready -U zephyr -d depgraph` | accepting connections |
| 3 | 简单查询可执行 | `psql -U zephyr -d depgraph -c "SELECT 1;"` | 返回1 |
| 4 | 扩展已安装 | `psql -U zephyr -d depgraph -c "\dx"` | pg_stat_statements + pgcrypto |
| 5 | zephyr用户可登录 | `psql -U zephyr -d depgraph -c "SELECT current_user;"` | zephyr |
| 6 | .env.postgres已gitignore | `git check-ignore config/.env.postgres` | 返回该文件路径 |

### 4.4 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql` | 新建 | PG扩展初始化脚本 |
| 2 | `config/.env.postgres` | 新建 | 环境变量（连接配置与密码） |
| 3 | `.gitignore` | 修改 | 添加PG secrets和data目录忽略 |

---

## 五、阶段2：数据迁移脚本（SQLite→PostgreSQL）

### 5.1 前置条件

- [ ] 阶段1已完成（PostgreSQL运行中）
- [ ] `depgraph`已git commit备份（最新状态）
- [ ] Python环境已安装`psycopg2-binary`包

#### [动作1] 安装Python依赖

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
pip install psycopg2-binary
```

#### [动作2] 创建PostgreSQL Schema DDL脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\migrate_sqlite_to_pg\01_create_pg_schema.sql`

**操作**：创建新文件。此文件将SQLite的DDL翻译为PostgreSQL DDL。

**关键翻译规则**：

| SQLite | PostgreSQL | 说明 |
|--------|-----------|------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | 自增主键 |
| `TEXT` | `TEXT` | 文本类型（不变） |
| `INTEGER` | `INTEGER` | 整数类型（不变） |
| `REAL` | `DOUBLE PRECISION` | 浮点类型 |
| `BLOB` | `BYTEA` | 二进制类型 |
| `datetime('now')` | `now()` | 当前时间 |
| `DEFAULT 0` | `DEFAULT 0` | 默认值（不变） |
| `CHECK(x IN ('a','b'))` | `CHECK(x IN ('a','b'))` | CHECK约束（不变） |
| `CREATE TRIGGER ... FOR EACH ROW WHEN ... BEGIN ... END` | `CREATE FUNCTION ... RETURNS TRIGGER ... $$ ... $$ LANGUAGE plpgsql` | 触发器语法 |
| `INSERT OR REPLACE` | `INSERT ... ON CONFLICT DO UPDATE` | Upsert |
| `PRAGMA` | （删除） | PG无对应 |
| `CREATE VIRTUAL TABLE ... USING fts5(...)` | `CREATE INDEX ... USING gin(to_tsvector(...))` | 全文搜索 |

**DDL内容**：从 `src/zephyr/governance/depgraph_schema.py` 中提取所有表定义，翻译为PostgreSQL DDL。具体DDL内容较长，作为独立SQL文件提供。

**重要**：DDL必须与SQLite实际表结构对齐（DB实际41列，非DDL的30列——调研报告3发现的DDL与DB不一致问题）。迁移前必须先从SQLite导出实际schema：

```powershell
cd D:\ZephyrAlpha
python -c "import sqlite3; conn=sqlite3.connect('data/databases/depgraph.db'); [print(r[0]) for r in conn.execute(\"SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name\")]"
```

将输出保存为 `scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql`，作为翻译基准。

#### [动作3] 创建数据迁移Python脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\migrate_sqlite_to_pg\migrate_data.py`

**操作**：创建新文件，内容如下：

```python
#!/usr/bin/env python3
"""
SQLite → PostgreSQL 数据迁移脚本
===============================
将 depgraph 的所有数据迁移到 PostgreSQL。

使用方式：
    python scripts/governance/migrate_sqlite_to_pg/migrate_data.py

前置条件：
    1. PostgreSQL已启动（Windows服务运行中）
    2. PG Schema已创建（01_create_pg_schema.sql已执行）
    3. depgraph已git commit备份
"""

import sqlite3
import psycopg2
import sys
import time
from pathlib import Path

# SQLite路径
SQLITE_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"

# PostgreSQL连接参数（直连PostgreSQL）
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "depgraph",
    "user": "zephyr",
    "password": "zephyr_dev_2026",
}

# 迁移表清单：从SQLite动态获取（见get_sqlite_tables函数），不硬编码
# 以下为参考清单（实际以动态获取为准）
TABLES_REFERENCE = [
    "_schema_version",
    "domains",
    "nodes",
    "edges",
    "domain_dependencies",
    "contracts",
    "domain_events",
    "invariants",
    "rule_bindings",
    "rule_enforcement_log",
    "templates",
    "file_script_map",
    "gate_results",
    "task_audit_findings",
    "arch_modules",
    "arch_contracts",
    "arch_decisions",
    "arch_invariants",
    "arch_events",
    "arch_dependencies",
    "arch_capacity",
    # 补充：从实际DB导出的完整表清单
]

# 批量插入大小
BATCH_SIZE = 1000


def get_sqlite_tables(conn):
    """从SQLite获取实际表清单（按名称排序，外键依赖由TRUNCATE CASCADE处理）。"""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '_fts_%' "
        "ORDER BY name"
    )
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(conn, table_name):
    """获取表的列名列表。"""
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def get_row_count(conn, table_name):
    """获取表的行数。"""
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def migrate_table(sqlite_conn, pg_conn, table_name):
    """迁移单个表的数据。"""
    columns = get_table_columns(sqlite_conn, table_name)
    col_list = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    # 获取SQLite行数
    sqlite_count = get_row_count(sqlite_conn, table_name)
    print(f"  [{table_name}] SQLite行数: {sqlite_count}")

    if sqlite_count == 0:
        print(f"  [{table_name}] 空表，跳过")
        return 0

    # 清空PG表（幂等迁移）
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE')

    # 批量读取并插入
    insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'

    total_inserted = 0
    batch = []

    for row in sqlite_conn.execute(f"SELECT {col_list} FROM {table_name}"):
        batch.append(row)
        if len(batch) >= BATCH_SIZE:
            pg_cursor.executemany(insert_sql, batch)
            pg_conn.commit()
            total_inserted += len(batch)
            batch = []
            print(f"    已插入 {total_inserted}/{sqlite_count} 行...", end="\r")

    if batch:
        pg_cursor.executemany(insert_sql, batch)
        pg_conn.commit()
        total_inserted += len(batch)

    print(f"    完成: {total_inserted}/{sqlite_count} 行")

    # 验证行数
    pg_count = pg_cursor.execute(
        f'SELECT COUNT(*) FROM "{table_name}"'
    ).fetchone()[0]

    if pg_count != sqlite_count:
        print(f"  [ERROR] {table_name}: SQLite={sqlite_count}, PG={pg_count} 行数不匹配!")
        return -1

    return total_inserted


def main():
    print("=" * 60)
    print("SQLite → PostgreSQL 数据迁移")
    print("=" * 60)

    # 检查SQLite文件
    if not Path(SQLITE_PATH).exists():
        print(f"[ERROR] SQLite文件不存在: {SQLITE_PATH}")
        sys.exit(1)

    # 连接SQLite
    print(f"\n[1/4] 连接SQLite: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    # 获取实际表清单
    tables = get_sqlite_tables(sqlite_conn)
    print(f"  发现 {len(tables)} 张表: {', '.join(tables)}")

    # 连接PostgreSQL
    print(f"\n[2/4] 连接PostgreSQL...")
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_conn.autocommit = False

    # 迁移每张表
    print(f"\n[3/4] 开始数据迁移...")
    total_rows = 0
    failed_tables = []

    for table in tables:
        try:
            rows = migrate_table(sqlite_conn, pg_conn, table)
            if rows >= 0:
                total_rows += rows
            else:
                failed_tables.append(table)
        except Exception as e:
            print(f"  [ERROR] {table}: {e}")
            pg_conn.rollback()
            failed_tables.append(table)

    # 最终验证
    print(f"\n[4/4] 最终验证...")
    all_ok = True
    for table in tables:
        sqlite_count = get_row_count(sqlite_conn, table)
        pg_cursor = pg_conn.cursor()
        pg_count = pg_cursor.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]
        status = "OK" if sqlite_count == pg_count else "MISMATCH"
        if sqlite_count != pg_count:
            all_ok = False
        print(f"  {table}: SQLite={sqlite_count}, PG={pg_count} [{status}]")

    # 总结
    print("\n" + "=" * 60)
    if all_ok and not failed_tables:
        print(f"迁移成功! 总行数: {total_rows}")
    else:
        print(f"迁移失败! 失败表: {failed_tables}")
    print("=" * 60)

    sqlite_conn.close()
    pg_conn.close()

    sys.exit(0 if all_ok and not failed_tables else 1)


if __name__ == "__main__":
    main()
```

#### [动作4] 执行数据迁移

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha

# 1. 先备份depgraph
git add data/databases/depgraph.db
git commit -m "backup: depgraph.db before PostgreSQL migration"

# 2. 执行PG Schema DDL
psql -U zephyr -d depgraph -f scripts\governance\migrate_sqlite_to_pg\01_create_pg_schema.sql

# 3. 执行数据迁移
python scripts\governance\migrate_sqlite_to_pg\migrate_data.py
```

**预期输出**：所有表行数匹配，`迁移成功! 总行数: ~37000`

#### [动作5] 验证数据完整性

**操作**：在PowerShell中执行

```powershell
# 验证关键表行数
psql -U zephyr -d depgraph -c "
SELECT 'nodes' as tbl, COUNT(*) FROM nodes
UNION ALL
SELECT 'edges', COUNT(*) FROM edges
UNION ALL
SELECT 'domains', COUNT(*) FROM domains;
"

# 验证跨表关系完整性
psql -U zephyr -d depgraph -c "
SELECT COUNT(*) as orphan_edges
FROM edges e
LEFT JOIN nodes n ON e.source_id = n.node_id
WHERE n.node_id IS NULL;
"
```

**预期输出**：
- nodes: 14383行
- edges: 22605行
- domains: 55行
- orphan_edges: 0（无孤儿边）

### 5.2 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | depgraph已备份 | `git log --oneline -1` | 显示backup commit |
| 2 | PG Schema创建成功 | `psql -U zephyr -d depgraph -c "\dt"` | 显示所有表 |
| 3 | 数据迁移成功 | `python migrate_data.py` | 迁移成功! 总行数: ~37000 |
| 4 | nodes行数匹配 | `SELECT COUNT(*) FROM nodes` | 14383 |
| 5 | edges行数匹配 | `SELECT COUNT(*) FROM edges` | 22605 |
| 6 | domains行数匹配 | `SELECT COUNT(*) FROM domains` | 55 |
| 7 | 无孤儿边 | orphan_edges查询 | 0 |
| 8 | 索引创建成功 | `psql -U zephyr -d depgraph -c "\di"` | 显示所有索引 |

### 5.3 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql` | 新建 | SQLite实际schema导出 |
| 2 | `scripts/governance/migrate_sqlite_to_pg/01_create_pg_schema.sql` | 新建 | PG Schema DDL |
| 3 | `scripts/governance/migrate_sqlite_to_pg/migrate_data.py` | 新建 | 数据迁移脚本 |
| 4 | `requirements.txt` | 修改 | 添加`psycopg2-binary` |

---

## 六、阶段3：SQL方言调整（SQLite特有语法→PG标准）

### 6.1 前置条件

- [ ] 阶段2已完成（数据已迁移到PostgreSQL）
- [ ] 所有测试在SQLite下通过（迁移前的基线）

### 6.2 施工分组

由于涉及64个文件、100+连接点，按功能分组为3个任务卡：

| 任务卡 | 分组 | 文件数 | 说明 |
|--------|------|:---:|------|
| P2-T3-A | Schema层 | 3 | depgraph_schema.py, sqlite_schema.py, db_utils.py |
| P2-T3-B | 写入脚本层 | 12 | apply_depgraph.py, sync_yaml_to_depgraph.py等 |
| P2-T3-C | 查询/工具层 | 49 | src/下其余文件 |

### 6.3 通用翻译规则（适用于所有文件）

以下规则适用于所有涉及SQL的文件。每个文件修改时必须对照此规则表。

#### 6.3.1 占位符

| SQLite | PostgreSQL | 说明 |
|--------|-----------|------|
| `?` | `%s`（psycopg2）或 `$N`（psycopg3） | 参数占位符 |

**操作方式**：全局搜索 `?` 在SQL字符串中的使用，替换为 `%s`。

**注意**：仅替换SQL语句中的 `?`，不替换Python字符串中的 `?`（如正则表达式）。

#### 6.3.2 INSERT OR REPLACE

| SQLite | PostgreSQL |
|--------|-----------|
| `INSERT OR REPLACE INTO t (a,b) VALUES (?,?)` | `INSERT INTO t (a,b) VALUES (%s,%s) ON CONFLICT (a) DO UPDATE SET b=EXCLUDED.b` |

**操作方式**：搜索 `INSERT OR REPLACE`，根据表的主键/唯一约束，改为 `ON CONFLICT DO UPDATE`。

#### 6.3.3 PRAGMA（全部删除）

| SQLite PRAGMA | 处理方式 | 说明 |
|---------------|---------|------|
| `PRAGMA journal_mode=WAL` | 删除 | PG默认WAL |
| `PRAGMA synchronous=NORMAL` | 删除 | PG配置在postgresql.conf |
| `PRAGMA foreign_keys=ON` | 删除 | PG默认启用外键 |
| `PRAGMA busy_timeout=30000` | 删除 | PG用statement_timeout |
| `PRAGMA cache_size` | 删除 | PG用shared_buffers |
| `PRAGMA temp_store=MEMORY` | 删除 | PG用temp_buffers |
| `PRAGMA writable_schema` | **完全删除** | PG无此功能，危险操作 |

**操作方式**：搜索 `PRAGMA`，删除所有PRAGMA语句。

#### 6.3.4 AUTOINCREMENT

| SQLite | PostgreSQL |
|--------|-----------|
| `id INTEGER PRIMARY KEY AUTOINCREMENT` | `id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` |

#### 6.3.5 日期时间函数

| SQLite | PostgreSQL |
|--------|-----------|
| `datetime('now')` | `now()` |
| `datetime('now', '-1 day')` | `now() - INTERVAL '1 day'` |
| `date('now')` | `CURRENT_DATE` |
| `strftime('%Y-%m-%d', col)` | `to_char(col, 'YYYY-MM-DD')` |

#### 6.3.6 聚合函数

| SQLite | PostgreSQL |
|--------|-----------|
| `GROUP_CONCAT(col)` | `string_agg(col::text, ',')` |
| `GROUP_CONCAT(col, '|')` | `string_agg(col::text, '|')` |

#### 6.3.7 系统表查询

| SQLite | PostgreSQL |
|--------|-----------|
| `SELECT * FROM sqlite_master WHERE type='table'` | `SELECT * FROM information_schema.tables WHERE table_schema='public'` |
| `SELECT * FROM sqlite_master WHERE type='index'` | `SELECT * FROM information_schema.indexes WHERE table_schema='public'` |
| `PRAGMA table_info(t)` | `SELECT * FROM information_schema.columns WHERE table_name='t'` |

#### 6.3.8 JSON操作

| SQLite | PostgreSQL |
|--------|-----------|
| `json_valid(col)` | `col IS NOT NULL AND col::jsonb IS NOT NULL`（或直接删除校验） |
| `json_extract(col, '$.key')` | `col::jsonb->>'key'` |
| `json_type(col)` | `jsonb_typeof(col)` |

#### 6.3.9 cursor.lastrowid

| SQLite | PostgreSQL |
|--------|-----------|
| `cursor.execute("INSERT ..."); id = cursor.lastrowid` | `cursor.execute("INSERT ... RETURNING id"); id = cursor.fetchone()[0]` |

#### 6.3.10 全文搜索

| SQLite | PostgreSQL |
|--------|-----------|
| `CREATE VIRTUAL TABLE fts USING fts5(col)` | `CREATE INDEX fts_idx ON t USING gin(to_tsvector('english', col))` |
| `SELECT * FROM fts WHERE fts MATCH 'query'` | `SELECT * FROM t WHERE to_tsvector('english', col) @@ to_tsquery('query')` |

#### 6.3.11 GLOB

| SQLite | PostgreSQL |
|--------|-----------|
| `col GLOB 'pattern'` | `col ~ 'pattern'`（正则匹配） |

#### 6.3.12 连接方式

| SQLite | PostgreSQL |
|--------|-----------|
| `sqlite3.connect(path)` | `psycopg2.connect(host, port, database, user, password)` |
| `conn.row_factory = sqlite3.Row` | `pg_conn.cursor(cursor_factory=RealDictCursor)` |
| `conn.commit()` | `pg_conn.commit()`（不变） |
| `conn.execute(sql)` | `pg_conn.cursor().execute(sql)`（PG需要cursor） |

### 6.4 任务卡P2-T3-A：Schema层修改

#### 6.4.1 文件：`src/zephyr/governance/depgraph_schema.py`

**当前状态**：depgraph的Schema DDL + 版本化迁移框架（v1-v18，v18 为 blueprint_id 双轨制+历史兼容 DB 触发器），23张表定义，18个索引，dep_cycles视图。

**修改清单**：

| # | 行号 | 当前内容 | 修改为 | 说明 |
|---|------|---------|--------|------|
| 1 | 77 | `DB_PATH = ...depgraph.db` | `PG_CONFIG = {"host": "localhost", "port": 5432, ...}` | DB路径→PG连接配置 |
| 2 | 全文 | `import sqlite3` | `import psycopg2` + `from psycopg2.extras import RealDictCursor` | 导入PG驱动 |
| 3 | 全文 | `sqlite3.connect(DB_PATH)` | `psycopg2.connect(**PG_CONFIG)` | 连接方式 |
| 4 | 全文 | `PRAGMA journal_mode=WAL` | （删除） | PG无PRAGMA |
| 5 | 全文 | `PRAGMA synchronous=NORMAL` | （删除） | PG无PRAGMA |
| 6 | 全文 | `PRAGMA foreign_keys=ON` | （删除） | PG默认启用 |
| 7 | 全文 | `PRAGMA busy_timeout=30000` | （删除） | PG用statement_timeout |
| 8 | 全文 | `INTEGER PRIMARY KEY AUTOINCREMENT` | `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | 自增主键 |
| 9 | 全文 | `datetime('now')` | `now()` | 日期函数 |
| 10 | 全文 | `CREATE TRIGGER ... BEGIN ... END` | `CREATE FUNCTION ... RETURNS TRIGGER ... $$ ... $$ LANGUAGE plpgsql` | 触发器语法 |
| 11 | 全文 | `?` 占位符 | `%s` | 参数占位符 |
| 12 | 全文 | `cursor.lastrowid` | `cursor.execute("... RETURNING id"); cursor.fetchone()[0]` | 获取插入ID |
| 13 | 全文 | `sqlite_master` 查询 | `information_schema` | 系统表 |
| 14 | 全文 | `GROUP_CONCAT` | `string_agg` | 聚合函数 |
| 15 | 全文 | `json_valid` / `json_extract` | `::jsonb` / `->>` | JSON操作 |
| 16 | 全文 | `CREATE VIRTUAL TABLE ... USING fts5(...)` | `CREATE INDEX ... USING gin(to_tsvector(...))` | 全文搜索 |
| 17 | 全文 | `conn.execute(sql)` | `cursor = conn.cursor(); cursor.execute(sql)` | PG需要cursor |

**具体操作**：由于此文件是depgraph的Schema真源，修改量很大。建议：
1. 先完整阅读 `depgraph_schema.py` 全文
2. 逐个函数修改，对照翻译规则表
3. 每修改一个函数，运行对应测试验证

#### 6.4.2 文件：`src/zephyr/governance/sqlite_schema.py`

**当前状态**：governance.db的Schema，4个blocked_by校验触发器。

**重要**：governance.db保持SQLite（D50-PG裁定，见§1.3），此文件**大部分不变**。

**修改清单**：

| # | 当前内容 | 修改为 | 说明 |
|---|---------|--------|------|
| 1 | 如果有引用depgraph路径的变量 | 改为引用PG连接配置 | 区分governance.db和depgraph |
| 2 | 如果有跨库查询depgraph的SQL | 改为通过PG连接执行 | 跨库查询需调整 |

**验证方法**：
```powershell
# 检查sqlite_schema.py中是否引用depgraph
grep -n "depgraph" src/zephyr/governance/sqlite_schema.py
```
如果无输出，则此文件无需修改（governance.db独立于depgraph）。

#### 6.4.3 文件：`src/zephyr/shared/utils/db_utils.py`

**当前状态**：公共DB连接API，PRAGMA基线。

**修改清单**：

| # | 当前内容 | 修改为 | 说明 |
|---|---------|--------|------|
| 1 | `import sqlite3` | `import sqlite3` + `import psycopg2` | 双驱动支持 |
| 2 | `def get_db_connection(db_type='sqlite'):` | 增加PG连接分支 | 根据db_type选择驱动 |
| 3 | PRAGMA基线设置 | 仅对SQLite连接设置PRAGMA | PG连接跳过PRAGMA |
| 4 | `?` 占位符 | 根据db_type选择`?`或`%s` | 参数占位符 |

**设计**：db_utils.py应提供统一的连接接口，内部根据数据库类型选择驱动：

```python
def get_depgraph_connection():
    """获取depgraph连接（PostgreSQL）。"""
    return psycopg2.connect(**PG_CONFIG)

def get_governance_connection():
    """获取governance连接（SQLite）。"""
    conn = sqlite3.connect(GOVERNANCE_DB_PATH)
    conn.row_factory = sqlite3.Row
    # PRAGMA仅对SQLite有效
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
```

### 6.5 任务卡P2-T3-B：写入脚本层修改

#### 6.5.1 文件：`scripts/governance/apply_depgraph.py`

**当前状态**：depgraph唯一写入口，15个命令，_db_write_lock双重锁。

> **注意**：以下行号为调研时（2026-06-25）记录，实际修改前请用 `grep -n "_db_write_lock\|_check_git_backup\|_create_physical_backup" scripts/governance/apply_depgraph.py` 验证当前行号。

**修改清单**（除§6.3通用规则外）：

| # | 行号 | 当前内容 | 修改为 | 说明 |
|---|------|---------|--------|------|
| 1 | 197-244 | `_db_write_lock` (threading.Lock + lock_files.py) | （删除整个锁机制） | PG自己管锁 |
| 2 | 76-141 | `_check_git_backup` | 保留，改为建议性检查 | PG迁移后仍需备份 |
| 3 | 148-171 | `_create_physical_backup` | 修改为PG逻辑备份(pg_dump) | 备份方式变更 |
| 4 | 全文 | `sqlite3.connect(DB_PATH)` | `psycopg2.connect(**PG_CONFIG)` | 连接方式 |
| 5 | 全文 | `?` 占位符 | `%s` | 参数占位符 |
| 6 | 全文 | `INSERT OR REPLACE` | `ON CONFLICT DO UPDATE` | Upsert |
| 7 | 全文 | `cursor.lastrowid` | `RETURNING id` | 获取插入ID |
| 8 | 全文 | `conn.execute(sql)` | `cursor.execute(sql)` | PG需要cursor |
| 9 | 全文 | `PRAGMA` 语句 | （删除） | PG无PRAGMA |

**锁删除详细操作**：

1. 删除 `import threading` 和 `from scripts.lock_files import ...`（仅DB锁相关导入）
2. 删除 `_db_write_lock = threading.Lock()` 定义
3. 删除所有 `with _db_write_lock:` 上下文管理器，保留内部逻辑
4. 删除 `lock_files.py` 的DB锁调用（`lock_files.py` 本身保留，仅删除DB专用调用）
5. 保留 `_check_git_backup` 和 `_create_physical_backup`，但修改备份方式

**备份方式修改**：

```python
def _create_physical_backup():
    """创建PG逻辑备份。"""
    import subprocess
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/databases/backups/depgraph_pg_{timestamp}.sql"
    with open(backup_path, "w") as f:
        subprocess.run([
            "pg_dump", "-U", "zephyr", "-d", "depgraph"
        ], stdout=f, check=True)
    return backup_path
```

#### 6.5.2 文件：`scripts/governance/sync_yaml_to_depgraph.py`

**当前状态**：YAML→DB同步，17项，只读触发器管理，无锁。

**修改清单**（除§6.3通用规则外）：

| # | 当前内容 | 修改为 | 说明 |
|---|---------|--------|------|
| 1 | `sqlite3.connect(DB_PATH)` | `psycopg2.connect(**PG_CONFIG)` | 连接方式 |
| 2 | 只读触发器管理（disable/restore） | PL/pgSQL触发器管理 | 触发器语法变更 |
| 3 | `?` 占位符 | `%s` | 参数占位符 |
| 4 | `INSERT OR REPLACE` | `ON CONFLICT DO UPDATE` | Upsert |
| 5 | `PRAGMA` 语句 | （删除） | PG无PRAGMA |

**只读触发器管理修改**：

SQLite中通过 `PRAGMA writable_schema=1` 临时禁用触发器的方式在PG中不可用。PG中应使用：

```sql
-- 临时禁用触发器
ALTER TABLE nodes DISABLE TRIGGER prevent_write;
-- 执行写入
-- ...
-- 重新启用触发器
ALTER TABLE nodes ENABLE TRIGGER prevent_write;
```

#### 6.5.3 其他写入脚本

以下脚本需要相同的SQL方言调整（连接方式、占位符、INSERT OR REPLACE、PRAGMA等）：

| # | 文件路径 | 说明 |
|---|---------|------|
| 1 | `scripts/governance/generate_project_depgraph.py` | 磁盘扫描→DB写入（注意：禁止运行，但代码仍需调整） |
| 2 | `scripts/governance/extract_depgraph.py` | depgraph查询导出 |
| 3 | `scripts/governance/d7_code/detect_forward_reference.py` | 前向引用检测（注意：在 d7_code/ 子目录下） |
| 4 | `scripts/governance/d7_code/check_encoding.py` | 编码检查 |
| 5 | `scripts/governance/cleanup_stash.py` | stash管理 |
| 6 | `scripts/governance/d5_architecture/`（含 generators/checkers/detectors/analyzers/syncers/validators 子目录，共 80+ 脚本） | 架构治理脚本集合（generators/ 含 16 个生成器，validators/ 含大量验证器） |
| 7 | `scripts/governance/d3_metadata/*.py` | 元数据检查脚本（多个） |
| 8 | `scripts/governance/d1_structure/*.py` | 结构检查脚本（多个） |

> **注意**：原清单中的 `check_capacity.py` 与 `validate_depgraph.py` 经核查不存在（已废弃或合并）；容量治理由 `scripts/governance/d5_architecture/generators/generate_capacity_report.py` 承担，depgraph 验证散布在 d5_architecture/validators/ 下多个 `validate_*.py`。

### 6.6 任务卡P2-T3-C：查询/工具层修改

#### 6.6.1 src/下的49个文件

以下文件需要SQL方言调整（主要是占位符`?`→`%s`、连接方式、PRAGMA删除）。

**获取完整文件清单的命令**：

```powershell
# 获取所有引用SQLite的src/文件
grep -rln "sqlite3\.\|PRAGMA\|INSERT OR REPLACE\|GROUP_CONCAT\|datetime('now')\|cursor.lastrowid\|sqlite_master\|json_extract\|json_valid\| GLOB " src/ --include="*.py" | sort -u
```

**关键文件清单**（修改量最大的前8个）：

| # | 文件路径 | 修改项 |
|---|---------|--------|
| 1 | `src/zephyr/governance/database_service.py` | 连接管理（三库连接，depgraph改为PG） |
| 2 | `src/zephyr/governance/task_repo.py` | 任务卡CRUD（保持SQLite，仅修改depgraph引用） |
| 3 | `src/zephyr/governance/event_store.py` | 事件存储（保持SQLite） |
| 4 | `src/zephyr/governance/projection_engine.py` | 投影引擎 |
| 5 | `src/zephyr/governance/rule_enforcement/gate_engine.py` | 门禁引擎 |
| 6 | `src/zephyr/governance/rule_enforcement/triple_alignment.py` | 三方对齐 |
| 7 | `src/zephyr/shared/io/paths.py` | DB_PATH定义 |
| 8 | `src/zephyr/shared/utils/db_utils.py` | 公共DB连接（已在P2-T3-A处理） |
| 9-49 | 其余41个文件 | 占位符、连接方式、PRAGMA等 |

**操作方式**：对每个文件执行以下步骤：
1. 读取文件全文
2. 搜索所有SQLite特有语法
3. 按翻译规则表逐一修改
4. 运行该文件对应的测试验证

### 6.7 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无残留PRAGMA | `grep -rn "PRAGMA" src/ scripts/governance/` | 仅governance.db相关 |
| 2 | 无残留INSERT OR REPLACE | `grep -rn "INSERT OR REPLACE" src/ scripts/governance/` | 0结果 |
| 3 | 无残留AUTOINCREMENT | `grep -rn "AUTOINCREMENT" src/ scripts/governance/` | 0结果 |
| 4 | 无残留sqlite3.connect(depgraph) | `grep -rn "sqlite3.connect.*depgraph" src/ scripts/` | 0结果 |
| 5 | 无残留cursor.lastrowid | `grep -rn "cursor.lastrowid" src/ scripts/` | 0结果 |
| 6 | 无残留sqlite_master | `grep -rn "sqlite_master" src/ scripts/` | 仅governance.db相关 |
| 7 | 无残留GROUP_CONCAT | `grep -rn "GROUP_CONCAT" src/ scripts/` | 0结果 |
| 8 | 无残留datetime('now') | `grep -rn "datetime('now')" src/ scripts/` | 0结果 |
| 9 | 无残留json_valid | `grep -rn "json_valid" src/ scripts/` | 0结果 |
| 10 | 无残留GLOB | `grep -rn " GLOB " src/ scripts/` | 0结果 |
| 11 | 无残留writable_schema | `grep -rn "writable_schema" src/ scripts/` | 0结果 |
| 12 | 无残留fts5 | `grep -rn "fts5\|FTS5" src/ scripts/` | 0结果 |
| 13 | 单元测试通过 | `pytest tests/ -x` | 全部通过 |
| 14 | apply_depgraph.py可运行 | `python scripts/governance/apply_depgraph.py diagnose` | 正常输出 |

### 6.8 受影响文件

| # | 文件路径 | 操作 | 修改项数 |
|---|---------|------|:---:|
| 1 | `src/zephyr/governance/depgraph_schema.py` | 修改 | 17 |
| 2 | `src/zephyr/governance/sqlite_schema.py` | 修改 | 2 |
| 3 | `src/zephyr/shared/utils/db_utils.py` | 修改 | 4 |
| 4 | `src/zephyr/shared/io/paths.py` | 修改 | 1 |
| 5 | `src/zephyr/governance/database_service.py` | 修改 | 3 |
| 6 | `scripts/governance/apply_depgraph.py` | 修改 | 9 |
| 7 | `scripts/governance/sync_yaml_to_depgraph.py` | 修改 | 5 |
| 8-19 | `scripts/governance/*.py`（12个写入脚本） | 修改 | 各3-5 |
| 20-64 | `src/zephyr/**/*.py`（49个查询/工具文件） | 修改 | 各2-4 |

---

## 七、阶段4：删除文件锁补丁

### 7.1 前置条件

- [ ] 阶段3已完成（SQL方言调整完毕）
- [ ] apply_depgraph.py已使用PostgreSQL连接

### 7.2 详细施工步骤

#### [动作1] 删除apply_depgraph.py中的_db_write_lock

**文件路径**：`d:\ZephyrAlpha\scripts\governance\apply_depgraph.py`

**操作**：

1. 删除以下代码块（行197-244附近）：

```python
# 删除：threading.Lock定义
_db_write_lock = threading.Lock()

# 删除：lock_files.py导入（仅DB锁相关）
from scripts.lock_files import acquire_lock, release_lock  # 删除此行
```

2. 删除所有 `with _db_write_lock:` 上下文管理器，保留内部逻辑：

```python
# 修改前：
def add_node(...):
    with _db_write_lock:
        conn = get_db_connection()
        # ... 实际逻辑

# 修改后：
def add_node(...):
    conn = get_db_connection()
    # ... 实际逻辑（不变）
```

3. 删除lock_files.py的DB锁调用：

```python
# 删除：
lock_file = acquire_lock("depgraph.db")
try:
    # ... 逻辑
finally:
    release_lock(lock_file)

# 保留内部逻辑，删除锁包装
```

**注意**：`lock_files.py` 本身**保留**（它是通用文件锁，非DB专用）。仅删除apply_depgraph.py中对lock_files.py的DB锁调用。

#### [动作2] 删除generate_project_depgraph.py中的独立锁

**文件路径**：`d:\ZephyrAlpha\scripts\governance\generate_project_depgraph.py`

**操作**：删除行2451-2482附近的独立锁实现（与apply_depgraph.py不一致的锁）。

**注意**：此脚本被禁止运行（project_memory规则），但代码仍需调整以保持一致性。

#### [动作3] 修改备份方式

**文件路径**：`d:\ZephyrAlpha\scripts\governance\apply_depgraph.py`

**操作**：将物理备份从文件复制改为pg_dump逻辑备份：

```python
# 修改前（SQLite文件复制）：
def _create_physical_backup():
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/databases/backups/depgraph_{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)
    return backup_path

# 修改后（PostgreSQL pg_dump）：
def _create_physical_backup():
    import subprocess
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/databases/backups/depgraph_pg_{timestamp}.sql"
    with open(backup_path, "w") as f:
        subprocess.run([
            "pg_dump", "-U", "zephyr", "-d", "depgraph"
        ], stdout=f, check=True)
    return backup_path
```

#### [动作4] 保留git备份门禁

**操作**：`_check_git_backup` 函数保留，但检查对象从depgraph文件改为相关代码文件：

```python
def _check_git_backup():
    """检查是否有未提交的更改（建议性检查，非阻断）。"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print("[WARN] 有未提交的更改，建议先git commit备份")
        # 不再阻断，仅警告（PG有MVCC，不需要文件级备份门禁）
    return True
```

#### [动作5] 验证锁删除完整性

**操作**：在PowerShell中执行

```powershell
# 检查是否还有_db_write_lock引用
grep -rn "_db_write_lock" scripts/governance/ src/

# 检查是否还有lock_files的DB锁调用
grep -rn "acquire_lock.*depgraph\|release_lock.*depgraph" scripts/governance/ src/

# 检查是否还有threading.Lock用于DB
grep -rn "threading.Lock.*db\|threading.Lock.*DB" scripts/governance/ src/
```

**预期结果**：0结果（无残留锁引用）。

### 7.3 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 无_db_write_lock | `grep -rn "_db_write_lock" scripts/ src/` | 0结果 |
| 2 | 无DB锁调用 | `grep -rn "acquire_lock.*depgraph" scripts/ src/` | 0结果 |
| 3 | lock_files.py保留 | `Test-Path scripts/lock_files.py` | True |
| 4 | 备份方式为pg_dump | `grep "pg_dump" scripts/governance/apply_depgraph.py` | 有结果 |
| 5 | apply_depgraph.py可运行 | `python scripts/governance/apply_depgraph.py diagnose` | 正常输出 |

### 7.4 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/apply_depgraph.py` | 修改 | 删除_db_write_lock，修改备份方式 |
| 2 | `scripts/governance/generate_project_depgraph.py` | 修改 | 删除独立锁实现 |

---

## 八、阶段5：连接配置

### 8.1 前置条件

- [ ] 阶段1已完成（PostgreSQL已安装运行）

### 8.2 详细施工步骤

#### [动作1] 验证PostgreSQL直连可用

**操作**：Windows原生安装的PostgreSQL直接连接即可，无需连接池。验证直连配置：

```powershell
# 验证PostgreSQL服务状态
Get-Service postgresql-x64-16

# 验证直连可连接
psql -U zephyr -d depgraph -c "SELECT current_user, current_database();"

# 查看当前连接数与最大连接数
psql -U zephyr -d depgraph -c "SELECT count(*) AS active, (SELECT setting FROM pg_settings WHERE name='max_connections') AS max FROM pg_stat_activity;"
```

**关键参数确认**：
- PostgreSQL服务状态：`Running`
- 直连返回：`zephyr / depgraph`
- `max_connections` 默认 100，建议调为 200（见§8.2 动作3）

#### [动作2] 创建Python连接工具

**文件路径**：`d:\ZephyrAlpha\src\zephyr\shared\utils\pg_connection.py`

**操作**：创建新文件，内容如下：

```python
"""
PostgreSQL连接工具
===================
直连PostgreSQL（Windows原生安装，无需连接池），提供统一的连接接口。

使用方式：
    from zephyr.shared.utils.pg_connection import get_depgraph_connection

    with get_depgraph_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE domain_id = %s", (domain_id,))
            rows = cur.fetchall()
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# PostgreSQL连接参数（直连PostgreSQL）
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "depgraph",
    "user": "zephyr",
    "password": "zephyr_dev_2026",
}


@contextmanager
def get_depgraph_connection():
    """获取 depgraph (PostgreSQL) 连接（直连）。

    使用方式：
        with get_depgraph_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    """
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_depgraph_dict_cursor():
    """获取depgraph字典游标（返回dict-like行）。

    使用方式：
        with get_depgraph_dict_cursor() as cur:
            cur.execute("SELECT * FROM nodes LIMIT 1")
            row = cur.fetchone()
            print(row['node_id'])
    """
    conn = psycopg2.connect(**PG_CONFIG)
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

#### [动作3] 更新db_utils.py使用PG直连

**文件路径**：`d:\ZephyrAlpha\src\zephyr\shared\utils\db_utils.py`

**操作**：修改 `get_db_connection` 函数，根据数据库类型选择连接方式：

> ⚠ **未实现的设计稿（2026-06-28 真源冲突治本标注）**：
> 此设计稿提议把 `db_utils.py` 的 `get_db_connection` 改为 `db_type` 路由器，**实际未实现**。
> 实际采用方案：PG 入口 = [`depgraph_schema.get_depgraph_pg_connection()`](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py)（原名 `get_db_connection`，已改名消除同名冲突），SQLite 入口 = [`db_utils.get_db_connection(db_path=None)`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py)（签名无 `db_type` 参数）。
> **新 AI 勿按此设计稿补全路由器**——会破坏 83 处 SQLite 调用点的隐式契约。见 AGENTS.md §11.4。

```python
def get_db_connection(db_type='governance'):
    """获取数据库连接。

    Args:
        db_type: 'governance' (SQLite) 或 'depgraph' (PostgreSQL)

    Returns:
        数据库连接对象
    """
    if db_type == 'depgraph':
        from zephyr.shared.utils.pg_connection import get_depgraph_connection
        return get_depgraph_connection()
    elif db_type == 'governance':
        conn = sqlite3.connect(GOVERNANCE_DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    else:
        raise ValueError(f"Unknown db_type: {db_type}")
```

**可选：调整 max_connections**：编辑 `C:\Program Files\PostgreSQL\16\data\postgresql.conf`，将 `max_connections` 改为 `200` 以支持40+AI并发，重启服务：

```powershell
Restart-Service postgresql-x64-16
```

#### [动作4] 验证直连并发能力

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
python -c "
import psycopg2
import threading
import time

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'depgraph',
    'user': 'zephyr',
    'password': 'zephyr_dev_2026',
}

def query_worker(worker_id):
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM nodes WHERE domain_id = %s', ('D_GOVERNANCE',))
    count = cur.fetchone()[0]
    print(f'Worker {worker_id}: {count} nodes')
    cur.close()
    conn.close()

# 启动10个并发查询
threads = []
for i in range(10):
    t = threading.Thread(target=query_worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print('All workers done')
"
```

**预期输出**：10个Worker并发查询成功，无连接错误。

### 8.3 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | PostgreSQL服务运行 | `Get-Service postgresql-x64-16` | Status=Running |
| 2 | 直连可连接 | `psql -U zephyr -d depgraph -c "SELECT 1;"` | 返回1 |
| 3 | 连接数配置 | `psql -c "SHOW max_connections;"` | 100（或调整为200） |
| 4 | 并发查询成功 | 10线程并发查询 | 全部成功 |
| 5 | pg_connection.py可用 | `from zephyr.shared.utils.pg_connection import get_depgraph_connection` | 无报错 |

### 8.4 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `src/zephyr/shared/utils/pg_connection.py` | 新建 | PG直连工具 |
| 2 | `src/zephyr/shared/utils/db_utils.py` | 修改 | 增加PG连接分支 |

---

## 九、阶段6：红蓝测试验证并发写入

### 9.1 前置条件

- [ ] 阶段3已完成（SQL方言调整完毕）
- [ ] 阶段4已完成（文件锁已删除）
- [ ] 阶段5已完成（连接池已配置）

### 9.2 测试设计

**红蓝测试**：模拟40个AI并发写入不同domain_id的节点，验证MVCC并发能力。

| 测试项 | 红队（验证失败） | 蓝队（验证成功） |
|--------|-----------------|-----------------|
| 并发写入 | 40线程写同一domain_id（应串行） | 40线程写不同domain_id（应并行） |
| 并发读写 | 写入时读取（应无阻塞） | 写入时读取（应无阻塞） |
| 事务隔离 | 脏读（应被阻止） | 读已提交（默认隔离级） |
| 死锁检测 | 故意制造死锁（应自动检测） | 无死锁（正常操作） |

### 9.3 详细施工步骤

#### [动作1] 创建红蓝测试脚本

**文件路径**：`d:\ZephyrAlpha\tests\integration\test_pg_concurrency.py`

**操作**：创建新文件，内容如下：

```python
#!/usr/bin/env python3
"""
PostgreSQL并发写入红蓝测试
=========================
验证MVCC并发能力：40个AI并发写入不同domain_id的节点。

运行方式：
    pytest tests/integration/test_pg_concurrency.py -v
"""

import psycopg2
import threading
import time
import uuid
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "depgraph",
    "user": "zephyr",
    "password": "zephyr_dev_2026",
}

# 测试用domain_id列表（40个不同域）
TEST_DOMAINS = [f"D-TEST-{i:02d}" for i in range(40)]


@pytest.fixture(scope="module")
def clean_test_data():
    """测试前清理测试数据，测试后清理。

    注意：测试用domain_id（D-TEST-XX）需要先插入domains表，
    否则外键约束会阻止nodes插入。
    """
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 插入测试域（如果不存在）
    for domain in TEST_DOMAINS:
        cur.execute(
            """
            INSERT INTO domains (domain_id, name, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (domain_id) DO NOTHING
            """,
            (domain, f"Test Domain {domain}", "红蓝测试临时域")
        )

    # 额外的测试域
    for domain in ["D-TEST-SAME", "D-TEST-RW", "D-TEST-DR", "D-TEST-DL"]:
        cur.execute(
            """
            INSERT INTO domains (domain_id, name, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (domain_id) DO NOTHING
            """,
            (domain, f"Test Domain {domain}", "红蓝测试临时域")
        )

    # 清理旧测试数据
    for domain in TEST_DOMAINS + ["D-TEST-SAME", "D-TEST-RW", "D-TEST-DR", "D-TEST-DL"]:
        cur.execute("DELETE FROM edges WHERE domain_id = %s", (domain,))
        cur.execute("DELETE FROM nodes WHERE domain_id = %s", (domain,))
    conn.commit()

    yield

    # 测试后清理
    for domain in TEST_DOMAINS + ["D-TEST-SAME", "D-TEST-RW", "D-TEST-DR", "D-TEST-DL"]:
        cur.execute("DELETE FROM edges WHERE domain_id = %s", (domain,))
        cur.execute("DELETE FROM nodes WHERE domain_id = %s", (domain,))
        cur.execute("DELETE FROM domains WHERE domain_id = %s", (domain,))
    conn.commit()
    cur.close()
    conn.close()


def insert_node(domain_id, node_index):
    """向指定domain_id插入一个节点。"""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    node_id = f"test_node_{domain_id}_{node_index}_{uuid.uuid4().hex[:8]}"
    try:
        cur.execute(
            """
            INSERT INTO nodes (node_id, node_type, domain_id, name, file_path, design_maturity)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (node_id, "module", domain_id, f"Test Node {node_index}",
             f"/test/{domain_id}/{node_index}.py", "production")
        )
        conn.commit()
        return True, node_id
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


class TestPgConcurrency:
    """PostgreSQL并发写入测试。"""

    def test_concurrent_write_different_domains(self, clean_test_data):
        """蓝队测试：40线程并发写入不同domain_id（应近线性加速）。"""
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i, domain in enumerate(TEST_DOMAINS):
                future = executor.submit(insert_node, domain, 0)
                futures.append(future)

            results = [f.result() for f in as_completed(futures)]

        success_count = sum(1 for success, _ in results if success)
        assert success_count == 40, f"只有 {success_count}/40 个写入成功"

    def test_concurrent_write_same_domain(self, clean_test_data):
        """红队测试：40线程并发写入同一domain_id（应串行，无数据损坏）。"""
        domain = "D-TEST-SAME"
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(40):
                future = executor.submit(insert_node, domain, i)
                futures.append(future)

            results = [f.result() for f in as_completed(futures)]

        success_count = sum(1 for success, _ in results if success)
        # 同一domain_id的写入可能因行锁串行，但不应失败
        assert success_count == 40, f"只有 {success_count}/40 个写入成功"

    def test_concurrent_read_during_write(self, clean_test_data):
        """蓝队测试：写入时并发读取（应无阻塞）。"""
        def writer():
            for i in range(100):
                insert_node("D-TEST-RW", i)
            return True

        def reader():
            conn = psycopg2.connect(**PG_CONFIG)
            cur = conn.cursor()
            for _ in range(100):
                cur.execute("SELECT COUNT(*) FROM nodes WHERE domain_id = %s", ("D-TEST-RW",))
                cur.fetchone()
            cur.close()
            conn.close()
            return True

        with ThreadPoolExecutor(max_workers=4) as executor:
            w_future = executor.submit(writer)
            r_futures = [executor.submit(reader) for _ in range(3)]

            assert w_future.result()
            for f in r_futures:
                assert f.result()

    def test_no_dirty_read(self, clean_test_data):
        """红队测试：验证无脏读（默认Read Committed隔离级）。"""
        conn1 = psycopg2.connect(**PG_CONFIG)
        conn2 = psycopg2.connect(**PG_CONFIG)
        cur1 = conn1.cursor()
        cur2 = conn2.cursor()

        # conn1开启事务，插入数据但不提交
        cur1.execute("BEGIN")
        cur1.execute(
            "INSERT INTO nodes (node_id, node_type, domain_id, name) VALUES (%s, %s, %s, %s)",
            ("test_dirty_node", "module", "D-TEST-DR", "Dirty Node")
        )

        # conn2不应看到未提交的数据
        cur2.execute("SELECT COUNT(*) FROM nodes WHERE node_id = %s", ("test_dirty_node",))
        count = cur2.fetchone()[0]
        assert count == 0, "脏读发生！未提交的数据被读取"

        # conn1回滚
        cur1.execute("ROLLBACK")
        cur1.close()
        cur2.close()
        conn1.close()
        conn2.close()

    def test_deadlock_detection(self, clean_test_data):
        """红队测试：死锁自动检测（PG自动中止一个事务）。"""
        conn1 = psycopg2.connect(**PG_CONFIG)
        conn2 = psycopg2.connect(**PG_CONFIG)
        cur1 = conn1.cursor()
        cur2 = conn2.cursor()

        # 插入两行测试数据
        cur1.execute("INSERT INTO nodes (node_id, node_type, domain_id, name) VALUES (%s, %s, %s, %s)",
                     ("test_dl_1", "module", "D-TEST-DL", "DL Node 1"))
        cur1.execute("INSERT INTO nodes (node_id, node_type, domain_id, name) VALUES (%s, %s, %s, %s)",
                     ("test_dl_2", "module", "D-TEST-DL", "DL Node 2"))
        conn1.commit()

        # conn1锁行1，conn2锁行2
        cur1.execute("BEGIN")
        cur1.execute("UPDATE nodes SET name = 'Updated by conn1' WHERE node_id = %s", ("test_dl_1",))

        cur2.execute("BEGIN")
        cur2.execute("UPDATE nodes SET name = 'Updated by conn2' WHERE node_id = %s", ("test_dl_2",))

        # 制造死锁：conn1尝试锁行2，conn2尝试锁行1
        deadlock_detected = False
        try:
            cur1.execute("UPDATE nodes SET name = 'Updated by conn1 again' WHERE node_id = %s", ("test_dl_2",))
            # 给conn2一点时间
            import time
            time.sleep(0.1)
            cur2.execute("UPDATE nodes SET name = 'Updated by conn2 again' WHERE node_id = %s", ("test_dl_1",))
            conn1.commit()
            conn2.commit()
        except psycopg2.errors.DeadlockDetected:
            deadlock_detected = True
            conn1.rollback()
            conn2.rollback()

        assert deadlock_detected, "死锁未被检测到"

        cur1.close()
        cur2.close()
        conn1.close()
        conn2.close()
```

#### [动作2] 执行红蓝测试

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
pytest tests/integration/test_pg_concurrency.py -v --tb=long
```

**预期结果**：所有测试通过（5个测试全绿）。

#### [动作3] 执行40AI并发写入压力测试

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
python -c "
import psycopg2
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'depgraph',
    'user': 'zephyr',
    'password': 'zephyr_dev_2026',
}

def write_worker(worker_id, domain_id, node_count):
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    for i in range(node_count):
        node_id = f'perf_test_{domain_id}_{worker_id}_{i}'
        cur.execute(
            'INSERT INTO nodes (node_id, node_type, domain_id, name, design_maturity) VALUES (%s, %s, %s, %s, %s)',
            (node_id, 'module', domain_id, f'Perf Test {worker_id}-{i}', 'draft')
        )
    conn.commit()
    cur.close()
    conn.close()
    return node_count

# 40个AI，每个写100个节点到不同域
start_time = time.time()
with ThreadPoolExecutor(max_workers=40) as executor:
    futures = []
    for i in range(40):
        domain = f'D-PERF-{i:02d}'
        future = executor.submit(write_worker, i, domain, 100)
        futures.append(future)

    total = sum(f.result() for f in as_completed(futures))

elapsed = time.time() - start_time
print(f'40 AI并发写入 {total} 个节点，耗时 {elapsed:.2f}s')
print(f'吞吐量: {total/elapsed:.1f} nodes/s')

# 清理测试数据
conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
for i in range(40):
    domain = f'D-PERF-{i:02d}'
    cur.execute('DELETE FROM nodes WHERE domain_id = %s', (domain,))
conn.commit()
cur.close()
conn.close()
"
```

**预期结果**：
- 4000个节点写入成功
- 耗时 < 30秒
- 吞吐量 > 100 nodes/s
- 无 `database is locked` 错误

### 9.4 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 并发写不同域 | `pytest test_concurrent_write_different_domains` | 40/40成功 |
| 2 | 并发写同一域 | `pytest test_concurrent_write_same_domain` | 40/40成功 |
| 3 | 读写并发 | `pytest test_concurrent_read_during_write` | 通过 |
| 4 | 无脏读 | `pytest test_no_dirty_read` | 通过 |
| 5 | 死锁检测 | `pytest test_deadlock_detection` | 通过 |
| 6 | 40AI压力测试 | 压力测试脚本 | 4000节点, <30s, >100 nodes/s |

### 9.5 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `tests/integration/test_pg_concurrency.py` | 新建 | 红蓝测试脚本 |

---

## 十、回滚方案

### 10.1 回滚触发条件

- 数据迁移失败且无法修复
- SQL方言调整后核心功能不可用
- 红蓝测试失败且无法修复
- 性能严重退化（比SQLite慢2倍以上）

### 10.2 回滚步骤

#### [动作1] 恢复SQLite连接代码

```powershell
cd D:\ZephyrAlpha
git revert HEAD~N  # N为P2迁移的commit数
```

#### [动作2] 恢复depgraph

```powershell
# depgraph从未被删除（迁移是复制不是移动），直接使用
# 如果有修改，从git恢复
git checkout -- data/databases/depgraph.db
```

#### [动作3] 停止PostgreSQL服务

```powershell
# 停止Windows服务（如需彻底卸载，可改用Stop-Service + 卸载程序）
Stop-Service postgresql-x64-16
```

#### [动作4] 验证SQLite恢复

```powershell
python scripts/governance/apply_depgraph.py diagnose
pytest tests/ -x
```

### 10.3 回滚验证

| # | 验证项 | 预期结果 |
|---|--------|---------|
| 1 | depgraph可用 | diagnose正常输出 |
| 2 | 单元测试通过 | 全部通过 |
| 3 | apply_depgraph.py可用 | 可正常执行命令 |
| 4 | PostgreSQL已停止 | `Get-Service postgresql-x64-16` 返回 Stopped |

---

## 十一、风险与缓解措施

| # | 风险 | 严重度 | 概率 | 缓解措施 |
|---|------|:---:|:---:|---------|
| 1 | 数据迁移丢失 | 高 | 低 | 迁移前后行数对比校验 + git备份 |
| 2 | SQL方言遗漏 | 中 | 高 | grep扫描残留SQLite语法 + 单元测试 |
| 3 | 触发器翻译错误 | 高 | 中 | 逐个触发器对照测试 |
| 4 | 性能退化 | 中 | 低 | 红蓝测试压力测试 |
| 5 | PostgreSQL服务异常 | 中 | 低 | Windows服务自动重启 + pg_isready健康检查 |
| 6 | 并发session冲突 | 中 | 中 | git分支隔离 + 并发session锁 |
| 7 | DDL与DB不一致 | 高 | 高 | 迁移前从DB导出实际schema |

---

## 十二、受影响文件完整索引

> **完整清单**：详见 [mod_inf_012b_p2_affected_files_index.md](mod_inf_012b_p2_affected_files_index.md)（循环审查版，包含85个文件+26项锁机制/触发器的完整清单：文件路径、位置、变量/函数名、变更影响、执行办法）
>
> **审查状态**：第1轮审查完成（2026-06-25），85个文件+26项锁机制/触发器已记录。第2轮审查待执行。

### 12.1 新建文件

| # | 文件路径 | 阶段 | 说明 |
|---|---------|:---:|------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql` | 1 | PG扩展初始化脚本 |
| 2 | `config/.env.postgres` | 1 | 环境变量（连接配置与密码） |
| 3 | `scripts/governance/migrate_sqlite_to_pg/00_sqlite_actual_schema.sql` | 2 | SQLite实际schema |
| 4 | `scripts/governance/migrate_sqlite_to_pg/01_create_pg_schema.sql` | 2 | PG Schema DDL |
| 5 | `scripts/governance/migrate_sqlite_to_pg/migrate_data.py` | 2 | 数据迁移脚本 |
| 6 | `src/zephyr/shared/utils/pg_connection.py` | 5 | PG直连工具 |
| 7 | `tests/integration/test_pg_concurrency.py` | 6 | 红蓝测试脚本 |

### 12.2 修改文件

| # | 文件路径 | 阶段 | 修改说明 |
|---|---------|:---:|---------|
| 1 | `.gitignore` | 1 | 添加PG secrets和data目录忽略 |
| 2 | `src/zephyr/governance/depgraph_schema.py` | 3 | Schema DDL翻译为PG |
| 3 | `src/zephyr/governance/sqlite_schema.py` | 3 | 区分governance/depgraph连接 |
| 4 | `src/zephyr/shared/utils/db_utils.py` | 3,5 | 增加PG连接分支 |
| 5 | `src/zephyr/shared/io/paths.py` | 3 | DB_PATH→PG连接配置 |
| 6 | `src/zephyr/governance/database_service.py` | 3 | 三库连接管理调整 |
| 7 | `scripts/governance/apply_depgraph.py` | 3,4 | SQL方言+删除锁 |
| 8 | `scripts/governance/sync_yaml_to_depgraph.py` | 3 | SQL方言+触发器管理 |
| 9 | `scripts/governance/generate_project_depgraph.py` | 3,4 | SQL方言+删除锁 |
| 10 | `scripts/governance/extract_depgraph.py` | 3 | SQL方言 |
| 11 | `scripts/governance/d7_code/detect_forward_reference.py` | 3 | SQL方言（位于 d7_code/ 子目录） |
| 12 | `scripts/governance/d7_code/check_encoding.py` | 3 | SQL方言（位于 d7_code/ 子目录） |
| 13 | `scripts/governance/cleanup_stash.py` | 3 | SQL方言 |
| 14-62 | `src/zephyr/**/*.py`（49个文件） | 3 | SQL方言调整 |
| 63 | `requirements.txt` | 2 | 添加psycopg2-binary |

> **注**：原表中的 `check_capacity.py` 和 `validate_depgraph.py` 经核查不存在（已废弃或合并），详见 §6.5.3。容量治理由 `scripts/governance/d5_architecture/generators/generate_capacity_report.py` 承担。

### 12.3 需同步更新的文档

| # | 文件路径 | 更新内容 | 完成状态 |
|---|---------|---------|:---:|
| 1 | `docs/03_modules/_cross_layer/database/blueprint.md` | MOD-DB_DEPGRAPH_PG状态更新为Active | [x] |
| 2 | `docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md` | 全景图数据源更新为PostgreSQL | [x] |
| 3 | `docs/02_enterprise_architecture/architecture_upgrade_discussion.md` | D50裁定更新（D50-PG） | [x] |
| 4 | `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml` | 访问协议更新（5步流程修改） | [x] |
| 5 | `architecture_model/layers/b_db.yaml` | DB YAML真源更新 | [x] |
| 6 | `docs/03_modules/_cross_layer/database/index.md` | 索引更新 | [x] |
| 7 | `docs/03_modules/_cross_layer/database/sub_blueprints/index.md` | 子蓝图索引更新 | [x] |

### 12.4 需修改的测试文件

**获取完整测试文件清单的命令**：

```powershell
# 获取所有引用SQLite的测试文件
grep -rln "sqlite3\.\|depgraph\.db\|PRAGMA\|INSERT OR REPLACE" tests/ --include="*.py" | sort -u
```

**关键测试文件**（修改量最大的前4个）：

| # | 文件路径 | 修改说明 | 完成状态 |
|---|---------|---------|:---:|
| 1 | `tests/db/test_task_repo.py` | SQLite→PG连接调整（仅depgraph部分，task_repo保持SQLite） | [x] |
| 2 | `tests/db/test_depgraph_schema.py` | Schema DDL测试更新 | [x] |
| 3 | `tests/gates/test_gate_engine.py` | DB连接调整 | [x] |
| 4 | `tests/test_schemas.py` | DB连接调整 | [x] |
| 5+ | 其余测试文件（通过上述grep命令获取完整清单） | DB连接调整 | [x] |

---

## 十三、文档循环审查清单

本文档完成后，必须按以下清单循环审查，直到问题数=0：

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | 前后术语一致 | 全文搜索关键术语 | 同一术语全文统一 |
| 2 | 文件路径一致 | 全文搜索文件路径 | 路径前后一致 |
| 3 | 行号引用准确 | 对照实际文件行号 | 行号偏差≤2 |
| 4 | 施工步骤无遗漏 | 对照6个施工内容 | 6项全覆盖 |
| 5 | 依赖关系正确 | 阶段间依赖检查 | 依赖顺序合理 |
| 6 | 验证清单完整 | 每个阶段有验证 | 每阶段≥5项验证 |
| 7 | 回滚方案可行 | 回滚步骤可执行 | 4步回滚完整 |
| 8 | 风险识别完整 | 7项风险全覆盖 | 每项有缓解措施 |
| 9 | 受影响文件完整 | 对照调研报告 | 文件数匹配 |
| 10 | 翻译规则准确 | 对照SQLite/PG文档 | 规则无错误 |
| 11 | 代码示例可执行 | 代码语法检查 | 无语法错误 |
| 12 | 配置参数合理 | 对照PG最佳实践 | 参数值合理 |
| 13 | 任务卡分组合理 | 每组工作量均衡 | 3组各20+文件 |
| 14 | 元任务卡设计合理 | 审查修复流程完整 | 每个任务卡有元任务卡 |

**审查流程**：
1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → 通过

---

## 十四、P2迁移完成总结（2026-06-27）

### 14.1 完成状态

| 阶段 | 任务 | 状态 | 验证结果 |
|------|------|------|----------|
| P2-T1 | PostgreSQL 16安装 | ✅ 完成 | PostgreSQL 16.14 运行正常 |
| P2-T2 | 数据迁移（SQLite→PG） | ✅ 完成 | 25表，6428 nodes，7094 edges，48 domains，schema v18 |
| P2-T3 | SQL方言调整（65文件） | ✅ 完成 | 6个src/核心文件 + 44个scripts/文件全部迁移 |
| P2-T4 | 删除文件锁补丁 | ✅ 完成 | 3个核心写入脚本已无SQLite文件锁，_concurrency业务锁保留 |
| P2-T5 | 连接配置 | ✅ 完成 | depgraph_schema.py统一PG入口，_shared/constants.py提供PgConnExecuteWrapper |
| P2-T6 | 红蓝测试 | ✅ 完成 | 5/5全过（40并发写入验证） |

### 14.2 综合验证结果（16/16通过）

- 3个核心写入脚本（apply_depgraph/sync_yaml_to_depgraph/generate_project_depgraph）--help/dry-run正常
- 6个d5_architecture生成器运行正常（generate_domain_index/capacity_report/cross_domain_matrix/domain_doc/path_tree/integration_topology）
- 4个诊断脚本正常（verify_schema_health/diagnose_depgraph/audit_rename_completeness/check_schema_version_writes）
- SQLite残留模式检查：无问题（38处sqlite3.connect全部是governance.db/zalpha_metadata.db/测试/迁移源，合理保留）
- row[N]索引访问检查：无问题（22处r[0]/row[0]全部在保留SQLite的脚本中，合理）

### 14.3 红蓝测试结果（40并发写入）

| 测试 | 场景 | 结果 | 耗时 |
|------|------|------|------|
| T1 | 40并发INSERT（独立行） | 40/40成功 | 0.27s |
| T2 | 40并发UPDATE同一行（行锁串行化） | 40/40成功，counter=40（无丢失更新） | 0.28s |
| T3 | 40并发写+40并发读（MVCC读写不阻塞） | 80/80成功 | 0.52s |
| T4 | 死锁检测与自动恢复 | PG自动检测并回滚死锁事务 | 1.55s |
| T5 | 40并发事务回滚（事务隔离） | 40/40成功，0残留行 | 0.27s |

### 14.4 关键交付物

| 文件 | 角色 |
|------|------|
| `src/zephyr/governance/depgraph_schema.py` | PG连接统一入口（get_db_connection） |
| `scripts/governance/_shared/constants.py` | PgConnExecuteWrapper + get_depgraph_pg_connection |
| `config/.env.postgres` | PG连接配置 |
| `scripts/governance/migrate_sqlite_to_pg/` | 迁移工具（DDL+数据迁移） |
| `scripts/governance/repair/p2_pg_concurrent_test.py` | 40并发红蓝测试脚本 |

### 14.5 保留SQLite的文件清单

以下文件保留SQLite访问（访问governance.db/zalpha_metadata.db或为测试/备份脚本）：

- governance.db脚本：task_show.py, task_self_check.py, _sync/*.py, meta/*.py, audit_post_sync_commands.py等
- zalpha_metadata.db脚本：validate_cross_references.py
- 测试脚本：repair/red_blue_test.py, repair/concurrent_write_test.py
- 备份脚本：phase_a_backup.py
- 迁移源脚本：migrate_sqlite_to_pg/migrate_data.py

### 14.6 后续待完成工作

- [x] §12.3 列出的7个文档同步更新（blueprint.md状态→Active等）
- [x] §12.4 列出的测试文件修改（tests/下的DB连接调整）
- [x] git提交（通过GitCommitGateway）

