# 灾备备份系统使用说明

> module_id: MOD-INF-043 | blueprint v1.1.0

## 自动触发机制

系统注册为 post-commit reconciler，每次 `session_worktree_commit` merge 后自动检查：

1. **重要文件变更**：committed_files 包含 `src/` `config/` `docs/` `scripts/` `tests/` `data/databases/` 等路径下的文件
2. **8小时间隔保护**：距上次成功备份 ≥ 8小时（状态文件：`data/databases/backup_state.json`，纯运行时产物，gitignored）

两个条件同时满足才触发备份。日均触发1-2次。

**ClickHouse 独立节奏**：CH 全量备份 315GiB≈3h，每 24h 至多一次（`last_ch_backup_time` 仅成功时推进，失败下一窗口自动重试），与代码备份 8h 节奏解耦；`-Force` 旁路。CH 阶段失败时 backup.ps1 以 exit 2 退出、reconciler 报 warn（失败可见，禁止静默跳过）。

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

另需创建 `config/.env.ch_backup`（不进git，ClickHouse 备份 MinIO/S3 桥凭据），字段见 `scripts/backup/README.md` 文末说明或本机现有文件（`MINIO_EXE`/`MINIO_ADDRESS`/`MINIO_ROOT`/`MINIO_BUCKET`/`CH_S3_ACCESS_KEY`/`CH_S3_SECRET_KEY`/`CH_S3_ENDPOINT`/`RELAY_SCRIPT`）。

### 3. 确保F盘在线

外置盘 F:(SanDisk 2TB NTFS) 必须已挂载。

### 4. 首次备份

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
```

首次运行自动初始化restic仓库（`restic init`），后续直接增量备份。

## 备份内容

**包含**：`D:\ZephyrAlpha` 全部（排除清单外）+ `D:\tmp_db_dumps`（数据库dump）+ `F:\ch_backup_store`（ClickHouse 行情库备份，315GiB+，见下节）

### ClickHouse 备份架构（2026-07-18 裁定）

CH 部署在 Hyper-V VM，其数据盘（588G/余 211G）装不下 315GiB 全量备份，且宿主机无 clickhouse-client、Windows 防火墙拦截 minio.exe。因此采用 **MinIO S3 桥**：

1. 备份时临时启动 MinIO（仅监听 127.0.0.1:<动态端口>）+ `minio_tcp_relay.py`（0.0.0.0:<relay端口>→127.0.0.1:<minio端口>，argv 传参，借 python 防火墙放行规则暴露给 VM）。端口启动前 bind 实测选取（Hyper-V HNS 会动态保留随机端口段，.env 里的端口只是首选值；2026-07-19 事故：9101-9200 被系统保留导致 MinIO 起不来）
2. CH 执行 `BACKUP DATABASE c1_market, DATABASE c3_fundamental TO S3('http://<VM侧宿主机IP>:<relay端口>/chbk/market.zip') ASYNC`，数据流直接出 VM 落到 F:
3. **每次写同一个 market.zip**：restic 内容分块（CDC）对未变化的 CH part 去重，每日增量 ≈ 新增行情（~9GiB/天），版本历史由 restic 快照管理
4. 备完即停 MinIO/relay（非常驻服务），restic 捕获 `F:\ch_backup_store`

全程 ASYNC + 轮询 `system.backups`，reconciler 超时已调至 4 小时。

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
| ClickHouse | 21.8+ | **必须**（已裁定：行情为开箱即用灾备资产，不从 bdpan 重建）。当前部署于 Hyper-V VM（172.24.30.100） | c1_market + c3_fundamental 行情库 |
| MinIO | 近期版 | 下载 `minio.exe` 到 `D:\tools\minio\`（国内镜像：`https://dl.minio.org.cn/server/minio/release/windows-amd64/minio.exe`） | **必须**，CH 备份 S3 桥 |

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
- ClickHouse：`.\scripts\backup\restore.ps1 ch` — 自动执行：定位最近含 `F:\ch_backup_store` 的快照（CH 24h 节奏与代码 8h 解耦，latest 快照通常不含 CH 存储，禁止盲取 latest）→ restic 取回 → 起 MinIO+relay → `RESTORE DATABASE c1_market, DATABASE c3_fundamental FROM S3(...)` → 行数抽查。前置：目标 CH 中相关表需先 DROP（或为空库）

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
| `backup_reconciler.py` | 事件触发器（post-commit reconciler，超时4h） |
| `backup.ps1` | 主备份脚本（六阶段流水线，含CH MinIO S3桥） |
| `minio_tcp_relay.py` | TCP中转（0.0.0.0:<relay端口>→127.0.0.1:<minio端口>，argv 传参，借python防火墙规则暴露MinIO给VM） |
| `backup_manual.ps1` | 手动兜底触发入口（-Force 模式） |
| `restore.ps1` | 恢复脚本（list/verify/latest/ch 四子命令） |
| `README.md` | 本文档 |

外部依赖（不进git/仓库）：`D:\tools\minio\minio.exe`（S3桥）、`config/.env.ch_backup`（S3凭据）
