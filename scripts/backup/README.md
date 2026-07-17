# 灾备备份系统使用说明

> module_id: MOD-INF-043 | blueprint v1.1.0

## 自动触发机制

系统注册为 post-commit reconciler，每次 `session_worktree_commit` merge 后自动检查：

1. **重要文件变更**：committed_files 包含 `src/` `config/` `docs/` `scripts/` `tests/` `data/databases/` 等路径下的文件
2. **8小时间隔保护**：距上次成功备份 ≥ 8小时（状态文件：`data/databases/backup_state.json`）

两个条件同时满足才触发备份。日均触发1-2次。

## 手动触发（兜底）

右键 `scripts/backup/backup_manual.ps1` → "用PowerShell运行"，以 `-Force` 模式运行（跳过间隔保护）。

或命令行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
```

## 首次使用（新环境配置）

### 1. 安装依赖

```powershell
# Restic备份引擎
winget install restic.restic

# sqlite3（可选，不可用时自动用Python fallback）
winget install SQLite.SQLite
```

### 2. 创建密码文件

创建 `config/.env.restic`（不进git，安全考虑），内容：

```
RESTIC_PASSWORD=<你的备份仓库密码>
```

**注意**：密码是加密密钥，忘记=数据无法恢复。与config/.env.postgres、config/.env.clickhouse同样不进git。

同时确保 `config/.env.postgres` 存在（PostgreSQL连接密码）。

### 3. 确保F盘在线

外置盘 F:(SanDisk 2TB NTFS) 必须已挂载。

### 4. 首次备份

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
```

首次运行自动初始化restic仓库（`restic init`），后续直接增量备份。

## 备份内容

**包含**：`D:\ZephyrAlpha` 全部（排除清单外）+ `D:\tmp_db_dumps`（数据库dump）

**排除**：
- `.aidrafts/` — session worktree临时草稿（4.7GB）
- `__pycache__/` `.pytest_cache/` 等 — Python缓存
- `.runtime/` `tmp/` — 运行时态
- `logs/*.log` — 日志
- `.venv/` — 依赖

## 灾难恢复

### 0. 新机器环境清单（开箱即用前提）

备份只含数据和代码，不含软件本体。恢复前必须先装好：

| 软件 | 版本 | 安装方式 | 用途 |
|------|------|----------|------|
| Restic | 近期版 | `winget install restic.restic` | 恢复引擎 |
| PostgreSQL | 16 | 官方安装包（含 pg_restore） | depgraph 库 |
| Python | ≥3.12（pyproject.toml requires-python） | python.org | 项目运行时 |
| 项目依赖 | - | `pip install -r requirements.txt -r requirements-dev.txt` | venv 重建 |
| SQLite | 任意 | `winget install SQLite.SQLite` | 可选（有 Python fallback） |
| ClickHouse | 按需 | 当前机器未安装；行情可从 `data/raw/bdpan` 重建 | 可选 |

还需准备：外置盘 F:（或拷贝出的仓库目录）+ `RESTIC_PASSWORD`（**仓库外离线副本**，密码在加密仓库内部，无副本则备份无法解开）。

### 查看快照

```powershell
.\scripts\backup\restore.ps1 list
```

### 验证恢复（到临时目录）

```powershell
.\scripts\backup\restore.ps1 verify <snapshot-id>
# 恢复到 D:\restore_test\ 供检查
```

### 灾难恢复（最新快照）

```powershell
.\scripts\backup\restore.ps1 latest
# 恢复到 D:\ZephyrAlpha\（会提示确认）
```

### 数据库恢复

- PostgreSQL：①`psql -f D:\tmp_db_dumps\pg_globals.sql -d postgres`（恢复 zephyr / depgraph_reader / depgraph_writer 角色）②按 `config/.env.postgres` 执行 `ALTER ROLE zephyr PASSWORD '...'`（pg_roles 导出不含密码）③`pg_restore -d depgraph D:\tmp_db_dumps\depgraph.dump`
- SQLite：覆盖 `data/databases/governance.db` 等
- ClickHouse：`RESTORE DATABASE c1_market FROM Disk('backups', 'c1_market_YYYYMMDD.zip')`

## 保留策略

- 近7天：每天1份快照
- 近4周：每周1份快照
- 近3个月：每月1份快照
- 超出范围的快照自动清理（`restic forget --prune`）

## 定期验证（建议每月）

```powershell
restic -r F:\restic-zephyr check --read-data
```

完整读取校验所有数据块，确保备份完整性。

## 文件清单

| 文件 | 职责 |
|------|------|
| `backup_config.yaml` | 配置SSoT（路径/保留/排除/触发条件） |
| `backup_reconciler.py` | 事件触发器（post-commit reconciler） |
| `backup.ps1` | 主备份脚本（六阶段流水线） |
| `backup_manual.ps1` | 手动兜底触发入口（-Force 模式） |
| `restore.ps1` | 恢复脚本（查看/验证/灾难恢复） |
| `README.md` | 本文档 |
