---
module_id: MOD-INF-043
submodule_path: scripts/backup
title: "灾备备份系统蓝图 — 事件触发→DB dump→Restic去重备份→保留清理→校验→报告"
doc_type: blueprint
template_for: blueprint
status: Active
version: "1.2.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-07-09"
ttl: permanent
construction_progress: not_started
actual_disk_path: "scripts/backup/"
last_updated: "2026-07-17"
last_verified: "2026-07-09"
generation: 1
functional_domain: operations
summary: "灾备备份系统——事件触发的Restic去重备份流水线，post-commit reconciler自动驱动（重要文件变更+8小时间隔保护，日均1-2次），覆盖代码+配置+数据库+不可替代数据，目标盘F:(SanDisk 2TB)，遵循3-2-1原则与数据最小化原则"
tags: [backup, disaster-recovery, restic, pg-dump, sqlite-backup, clickhouse-backup, 3-2-1-rule, reconciler, event-triggered]
priority: P1
belongs_to: MOD-MASTER_BLUEPRINT
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - target: MOD-INF-016
    at: "§0"
    why: "数据库双库路由（DatabaseService提供PG/SQLite/ClickHouse连接）"
  - target: MOD-INF-026
    at: "§0"
    why: "资产盘点——备份内容裁定依赖资产分类"
references: []
codification_level: L2
codification_at: "2026-07-09"
responsibility_domain: 
build_status: planned
design_maturity: design
---
> module_id: MOD-INF-043 | version: 1.2.0 | status: active | layer: L0_infrastructure
> actual_disk_path: scripts/backup/ | generation: 1 | construction_progress: planned

# 灾备备份系统蓝图 — 事件触发→DB dump→Restic去重备份→保留清理→校验→报告

## 概述

灾备备份系统是 ZephyrAlpha 的数据安全底线——解决"单点故障=项目死亡"的核心风险。系统采用 Restic 去重备份工具，通过 **post-commit reconciler 事件触发**（重要文件变更+8小时间隔保护，日均1-2次）自动执行：预检→数据库dump→Restic备份→保留策略清理→完整性校验→报告输出。备份目标为外置盘 F:(SanDisk 2TB NTFS)。备份内容遵循数据最小化原则（ISO/IEC 27001）：不可替代数据必备份，可重建数据排除，可重新下载数据由Restic去重红利决定包含。系统遵循3-2-1原则的本地实现（3副本=原盘+Restic快照+git历史，2介质=SSD+外置盘，1异地=未来扩展云备份）。同时保留手动一键触发能力作为兜底。

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：本蓝图
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR-CONTRACT]/[TESTS]`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `backup_reconciler.py` | §3.1 | post-commit reconciler（事件触发+间隔保护+调用backup.ps1） | 待实现 | |
| 2 | `backup.ps1` | §3.2 | 主备份脚本（预检+dump+restic+清理+校验+报告） | 待实现 | |
| 3 | `backup_config.yaml` | §3.3 | 备份配置（路径/保留策略/排除规则/触发条件） | 待实现 | |
| 4 | `一键备份.bat` | §3.4 | 手动兜底双击触发入口（调用backup.ps1） | 待实现 | |
| 5 | `restore.ps1` | §3.5 | 恢复脚本（查看快照/恢复指定快照/灾难恢复） | 待实现 | |
| 6 | `README.md` | §3.6 | 使用说明（自动触发机制/手动触发/灾难恢复） | 待实现 | |

---

## §1 架构设计

### §1.1 六阶段流水线

```
┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 1.预检  │ → │ 2.DB dump │ → │ 3.Restic │ → │ 4.保留   │ → │ 5.校验   │ → │ 6.报告   │
│         │   │           │   │   备份   │   │ 清理     │   │          │   │          │
│ F盘在线?│   │ PG dump   │   │ restic   │   │ restic   │   │ restic   │   │ JSON报告 │
│ restic? │   │ SQLite    │   │ backup   │   │ forget   │   │ check    │   │ 终端输出 │
│ 仓库?   │   │ ClickHouse│   │ --exclude│   │ --prune  │   │ stats    │   │          │
└─────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### §1.2 触发机制（自动+手动双轨）

**自动触发（主路径）**：注册为 post-commit reconciler，每次 GitCommitGateway merge 后由 `ReconciliationRegistry.reconcile_for()` 自动调用。

触发条件（`_trigger` 函数，两项同时满足）：
1. **重要文件变更**：committed_files 中存在以下路径前缀的文件
   - `src/` `config/` `docs/` `scripts/` `tests/` `architecture_model/`
   - `data/databases/` `data/raw/bdpan/` `data/vector_db/`
   - 根目录 `AGENTS.md` `pyproject.toml` `docker-compose.yml`
2. **最小间隔保护**：距离上次成功备份 ≥ 8小时（状态持久化到 `data/databases/backup_state.json`）

频率预估：日均1-2次（8小时间隔 + 仅重要文件变更触发，纯日志/cache变更不触发）

**手动触发（兜底路径）**：保留双击 `一键备份.bat` 能力，不受间隔保护限制（force模式）。

### §1.3 备份目标

- **仓库路径**：`F:\restic-zephyr`（Restic repository，加密+去重）
- **目标盘**：F:(SanDisk Portable SSD 2TB NTFS，卷标SanDisk2TB)
- **可用空间**：1862.84GB（足够容纳数年增量备份）

### §1.4 触发流程

```
GitCommitGateway.merge()
  └─→ ReconciliationRegistry.reconcile_for(committed_files, session_id)
       └─→ backup_reconciler._trigger(committed_files)
            ├─ 检测重要文件变更? → 否 → skip
            └─ 是 → 检查距上次备份≥8h? → 否 → skip
                 └─ 是 → backup_reconciler._reconcile()
                      └─ subprocess: powershell -File backup.ps1
                           └─ 六阶段流水线执行
                                └─ 更新 backup_state.json (last_backup_time)
```

---

## §2 备份内容裁定

### §2.1 裁定原则

基于专业机构实践（ISO/IEC 27001数据最小化原则、AWS Well-Architected可靠性支柱）与量化社区共识（QuantConnect/Zipline贡献者多层归档模式）：

> 备份的目的是"灾难恢复"，不是"磁盘镜像"。采用"全量备份+排除清单"模式（Restic社区标配），既安全又简单。

### §2.2 必须备份（不可替代/重建成本极高）

| 内容 | 大小 | 理由 |
|------|------|------|
| `src/` `config/` `docs/` `scripts/` `tests/` `architecture_model/` | ~250MB | 核心代码+规则真源，重建=项目死亡 |
| `.git/` | 7.2GB | 历史记录，Restic去重后增量极小 |
| `data/databases/governance.db` + `session_continuity.db` | 17MB | SQLite治理库，任务系统SSoT，不可替代 |
| `data/raw/bdpan/` | 876MB | 百度云一次性包，API无法重新获取 |
| `data/vector_db/` | 7MB | 知识库索引，重建成本高 |
| 数据库dump（PG/SQLite/ClickHouse） | ~50MB+ | 业务数据快照 |
| `.trae/` `.github/` `AGENTS.md` `pyproject.toml` 等根配置 | 小 | 项目治理锚定 |

### §2.3 必须排除（可重新生成/临时态）

| 内容 | 大小 | 理由 |
|------|------|------|
| `__pycache__/` `.pytest_cache/` `.mypy_cache/` `.ruff_cache/` | 散布 | Python缓存，自动重建 |
| `.aidrafts/` | 4.765GB | session worktree临时草稿，commit后即废弃 |
| `.runtime/` `tmp/*`（除`_db_dumps/`） | 小 | 运行时态 |
| `logs/*.log` `logs/*.log.*` | 小 | 日志（可选保留，建议排除） |
| `.venv/` `node_modules/` | - | 依赖，pip install重建 |

### §2.4 建议包含（去重后低成本）

| 内容 | 大小 | 理由 |
|------|------|------|
| `data/models/` | 7.1GB | 可从HuggingFace重新下载，但Restic去重后首次备份后再无增量成本，恢复时无需重新下载4.4GB的bge-m3。包含——低成本高安全 |

---

## §3 模块设计

### §3.1 backup_reconciler.py — 事件触发器（post-commit reconciler）

**职责**：注册为 ReconciliationRegistry 的 reconciler，post-commit 自动触发，内置重要文件过滤+8小时间隔保护，调用 backup.ps1 执行实际备份。

**注册方式**：通过 `make_backup_reconciler(project_root)` 工厂函数返回 `ReconcilerSpec`，在 GitCommitGateway 初始化时注册。

**核心逻辑**：
```python
# [TTL] permanent
# 事件驱动：post-commit reconciler（非时间触发，满足PERM-TRIGGER gate）

_IMPORTANT_PREFIXES = (
    "src/", "config/", "docs/", "scripts/", "tests/", "architecture_model/",
    "data/databases/", "data/raw/bdpan/", "data/vector_db/",
)
_IMPORTANT_FILES = {"AGENTS.md", "pyproject.toml", "docker-compose.yml"}
_MIN_INTERVAL_SECONDS = 8 * 3600  # 8小时间隔保护
_STATE_FILE = "data/databases/backup_state.json"

def _trigger(committed_files: list[str]) -> bool:
    """重要文件变更 + 距上次备份≥8h 才触发"""
    # 1. 检测重要文件变更
    has_important = any(
        rel.startswith(_IMPORTANT_PREFIXES) or rel in _IMPORTANT_FILES
        for rel in (_rel(f) for f in committed_files)
    )
    if not has_important:
        return False
    # 2. 检查最小间隔
    state = _load_state()
    last_backup = state.get("last_backup_time")
    if last_backup and (now - parse(last_backup)).total_seconds() < _MIN_INTERVAL_SECONDS:
        return False
    return True

def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
    """调用 PowerShell backup.ps1 执行备份"""
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass",
         "-File", str(project_root / "scripts/backup/backup.ps1")],
        capture_output=True, text=True, timeout=1800,  # 30min超时
    )
    if result.returncode == 0:
        _update_state(last_backup_time=now_iso())
        return ReconcileResult(action="auto_committed",
                               detail=f"backup ok: {result.stdout[-200:]}")
    else:
        return ReconcileResult(action="warn",
                               detail=f"backup failed: {result.stderr[-200:]}")
```

**状态文件** `data/databases/backup_state.json`：
```json
{
  "last_backup_time": "2026-07-09T19:30:00+08:00",
  "last_backup_snapshot_id": "a1b2c3d4",
  "last_backup_status": "ok",
  "total_backups_count": 42
}
```

### §3.2 backup.ps1 — 主备份脚本

**职责**：编排六阶段流水线，输出备份报告。接受可选 `-Force` 参数跳过间隔保护（手动触发用）。

**流程伪代码**：
```powershell
param([switch]$Force)  # 手动触发时传 -Force 跳过间隔保护

# 1. 预检
Assert-Path F:\  # F盘在线
Assert-Command restic  # restic已安装
if (-not (Test-Path F:\restic-zephyr\config)) {
    restic init --repo F:\restic-zephyr  # 首次初始化
}

# 2. 数据库dump（写入项目外临时目录，避免被tmp/排除规则冲突）
$dumpDir = "D:\tmp_db_dumps"
New-Item $dumpDir -Force
pg_dump -Fc depgraph > $dumpDir\depgraph.dump
sqlite3 governance.db ".backup $dumpDir\governance_backup.db"
# ClickHouse: 检测服务运行，运行则dump，否则warn跳过

# 3. Restic备份（项目目录 + dump目录，排除清单内嵌）
restic -r F:\restic-zephyr backup D:\ZephyrAlpha $dumpDir `
    --exclude "**/__pycache__/" `
    --exclude "**/.pytest_cache/" `
    --exclude "**/.mypy_cache/" `
    --exclude "**/.ruff_cache/" `
    --exclude ".aidrafts/" `
    --exclude ".runtime/" `
    --exclude "tmp/" `  # tmp整体排除，dump已在项目外
    --exclude "logs/*.log" `
    --exclude ".venv/" `
    --exclude "node_modules/"

# 4. 保留策略清理
restic -r F:\restic-zephyr forget `
    --keep-daily 7 --keep-weekly 4 --keep-monthly 3 --prune

# 5. 校验
restic -r F:\restic-zephyr check
restic -r F:\restic-zephyr stats

# 6. 报告
# 输出到终端 + 写入 logs\backup_report_YYYYMMDD.json
```

### §3.3 backup_config.yaml — 备份配置

**职责**：集中管理路径、保留策略、排除规则、触发条件（backup_reconciler.py 和 backup.ps1 共同读取）。

**关键字段**：
```yaml
repository:
  path: "F:\\restic-zephyr"
  target_drive: "F:"
dump_dir: "D:\\tmp_db_dumps"  # 项目外临时目录，避免被tmp/排除规则冲突
retention:
  keep_daily: 7
  keep_weekly: 4
  keep_monthly: 3
trigger:
  min_interval_seconds: 28800  # 8小时间隔保护
  important_prefixes:
    - "src/"
    - "config/"
    - "docs/"
    - "scripts/"
    - "tests/"
    - "architecture_model/"
    - "data/databases/"
    - "data/raw/bdpan/"
    - "data/vector_db/"
  important_files:
    - "AGENTS.md"
    - "pyproject.toml"
    - "docker-compose.yml"
  state_file: "data/databases/backup_state.json"
databases:
  # PostgreSQL credentials (user/password) read from config/.env.postgres at runtime
  postgres:
    db_name: depgraph
    dump_file: "depgraph.dump"
  sqlite:
    - {src: "data\\databases\\governance.db", dump: "governance_backup.db"}
    - {src: "data\\databases\\session_continuity.db", dump: "session_backup.db"}
  clickhouse:
    db_name: c1_market
    skip_if_down: true
excludes:
  - "**/__pycache__/"
  - "**/.pytest_cache/"
  - ".aidrafts/"
  - ".runtime/"
  - "tmp/"
  - "logs/*.log"
  - ".venv/"
report:
  output_dir: "logs"
```

### §3.4 一键备份.bat — 手动兜底触发入口

**职责**：Windows双击即可触发备份（force模式，跳过间隔保护），作为自动触发的兜底。

```bat
@echo off
cd /d D:\ZephyrAlpha
powershell -ExecutionPolicy Bypass -File scripts\backup\backup.ps1 -Force
pause
```

### §3.5 restore.ps1 — 恢复脚本

**职责**：查看快照/恢复指定快照/灾难恢复最新快照。

**子命令**：
- `.\restore.ps1 list` — 列出所有快照
- `.\restore.ps1 verify <snapshot-id>` — 恢复到临时目录验证
- `.\restore.ps1 latest` — 灾难恢复最新快照到 D:\ZephyrAlpha\
- `.\restore.ps1 latest --target D:\restore_test\` — 恢复到指定目录

### §3.6 README.md — 使用说明

**职责**：自动触发机制说明、手动触发方式、灾难恢复操作手册。

---

## §4 数据库dump策略

### §4.1 PostgreSQL（depgraph）

```powershell
# Read credentials from config/.env.postgres (avoid hardcoding user/password)
$pgEnvFile = "$ProjectRoot\config\.env.postgres"
$pgUser = "postgres"; $pgPassword = ""
if (Test-Path $pgEnvFile) {
    $pgEnv = Get-Content $pgEnvFile -Encoding UTF8
    foreach ($line in $pgEnv) {
        if ($line -match '^POSTGRES_USER=(.+)$') { $pgUser = $matches[1].Trim() }
        if ($line -match '^POSTGRES_PASSWORD=(.+)$') { $pgPassword = $matches[1].Trim() }
    }
}
$env:PGPASSWORD = $pgPassword
# Compressed format dump, supports selective restore (dump to project-external temp dir)
& pg_dump -Fc -h localhost -U $pgUser -d depgraph -f "$DumpDir\depgraph.dump"
```

- 输出：`depgraph.dump`（~48MB，压缩格式）
- 恢复：`pg_restore -d depgraph depgraph.dump`

### §4.2 SQLite（governance.db / session_continuity.db）

```powershell
# 在线一致性备份（不阻塞写入，dump到项目外临时目录）
sqlite3 data\databases\governance.db ".backup D:\tmp_db_dumps\governance_backup.db"
sqlite3 data\databases\session_continuity.db ".backup D:\tmp_db_dumps\session_backup.db"
```

- `.backup` 命令保证一致性快照，优于文件复制

### §4.3 ClickHouse（c1_market）

```powershell
# 检测服务运行
$ch = Test-NetConnection -ComputerName localhost -Port 9000 -InformationLevel Quiet
if ($ch) {
    # 逐表导出为Parquet（按表分区，恢复灵活）
    clickhouse-client --query="BACKUP DATABASE c1_market TO Disk('backups', 'c1_market.zip')"
} else {
    Write-Warning "ClickHouse未运行，跳过dump（业务数据可从百度云包重建）"
}
```

- 服务未运行时warn跳过，不阻断备份（c1_market可从bdpan一次性包重建）

---

## §5 保留策略

### §5.1 Restic forget参数

```
--keep-daily 7      # 近7天每天1份
--keep-weekly 4     # 近4周每周1份
--keep-monthly 3    # 近3个月每月1份
--prune             # 清理不再引用的数据块
```

### §5.2 快照数量预估

- 总快照数：约14份（7 daily + 4 weekly + 3 monthly）
- 首次全量：~22GB（含.git 7.2GB + models 7.1GB + bdpan 876MB + 代码250MB + 其他）
- 后续增量：几十MB~几百MB（取决于代码改动量，Restic去重）
- 2TB外置盘足够容纳数年备份

---

## §6 验证流程

### §6.1 自动校验（每次备份后）

1. `restic check` — 校验仓库完整性（数据块+索引）
2. `restic stats` — 输出快照大小统计
3. `restic snapshots --latest 1` — 确认快照已写入

### §6.2 备份报告

输出到终端 + 写入 `logs\backup_report_YYYYMMDD.json`：
```json
{
  "timestamp": "2026-07-09T19:30:00+08:00",
  "duration_seconds": 180,
  "snapshot_id": "a1b2c3d4",
  "total_size_bytes": 22000000000,
  "databases": {
    "postgres": {"status": "ok", "size_bytes": 48000000},
    "sqlite": {"status": "ok", "size_bytes": 17000000},
    "clickhouse": {"status": "skipped", "reason": "service down"}
  },
  "check_result": "ok",
  "retention_pruned": 2
}
```

### §6.3 定期完整性验证（手动，建议每月）

```powershell
restic -r F:\restic-zephyr check --read-data  # 完整读取校验（慢但彻底）
```

---

## §7 恢复流程

### §7.1 查看快照

```powershell
.\scripts\backup\restore.ps1 list
# 或直接：restic -r F:\restic-zephyr snapshots
```

### §7.2 验证恢复（到临时目录）

```powershell
.\scripts\backup\restore.ps1 verify <snapshot-id>
# 恢复到 D:\restore_test\ 供检查
```

### §7.3 灾难恢复（最新快照）

```powershell
.\scripts\backup\restore.ps1 latest
# 恢复 D:\ZephyrAlpha\ 全部内容
```

### §7.4 数据库恢复

- PostgreSQL：`pg_restore -d depgraph tmp\_db_dumps\depgraph.dump`
- SQLite：覆盖 `governance.db` / `session_continuity.db`
- ClickHouse：`RESTORE DATABASE c1_market FROM Disk('backups', 'c1_market.zip')`

---

## §8 不变量（Invariants）

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| INV-01 | 备份仓库必须加密（restic init时设置密码） | `restic cat config` 检查加密 |
| INV-02 | 每次备份后必须执行 `restic check` | 脚本流程强制 |
| INV-03 | dump文件必须先写入 `D:\tmp_db_dumps\`（项目外）再随项目一起备份 | 脚本流程强制 |
| INV-04 | 备份报告必须写入 `logs/backup_report_YYYYMMDD.json` | 脚本流程强制 |
| INV-05 | 排除清单必须包含 `.aidrafts/`（4.7GB临时草稿） | 配置文件校验 |
| INV-06 | 保留策略必须执行 `--prune` 清理无引用数据块 | 脚本流程强制 |
| INV-07 | 禁止备份VMS snapshot_backup（GATE-VMS-SSOT硬阻断，30GB灾难根源） | 排除清单+AGENTS.md约束 |
| INV-08 | backup_reconciler必须通过post-commit reconciler触发，禁止时间触发（PERM-TRIGGER gate） | AST门禁+reconciler注册校验 |
| INV-09 | 自动触发必须满足双条件：重要文件变更 + 8小时间隔保护 | `_trigger`函数逻辑+单元测试 |
| INV-10 | 备份状态必须持久化到 `data/databases/backup_state.json` | 状态文件存在性校验 |
| INV-11 | 手动触发（-Force）跳过间隔保护，但必须走相同六阶段流水线 | 脚本参数校验 |

---

## §9 依赖关系

### §9.1 上游依赖

| 依赖 | 用途 |
|------|------|
| MOD-INF-016 (DatabaseService) | 提供PG/SQLite/ClickHouse连接参数 |
| MOD-INF-026 (AssetInventory) | 资产分类为备份内容裁定提供依据 |
| ReconciliationRegistry (zephyr.governance.audit) | post-commit reconciler注册与触发机制 |
| GitCommitGateway (zephyr.gov_enforcement.rule_bridge) | merge后触发reconcile_for，驱动backup_reconciler |
| Restic (外部工具) | 去重+加密+校验备份引擎 |
| pg_dump (PostgreSQL客户端) | PG数据库dump |
| sqlite3 (SQLite客户端) | SQLite数据库dump |
| clickhouse-client (ClickHouse客户端) | ClickHouse数据库dump |

### §9.2 下游消费者

| 消费者 | 用途 |
|--------|------|
| 运维人员（手动） | 灾难恢复时使用restore.ps1 |
| SLAMonitor (MOD-INF_sla_monitor) | RTO/RPO达标验证（RTO目标300s，RPO目标1任务） |

---

## §10 修改守卫（Modify-Guard）

- **修改本蓝图前**：必须确认备份内容裁定（§2）是否需要同步调整
- **修改backup.ps1前**：必须确认六阶段流水线顺序不被破坏
- **修改保留策略前**：必须评估快照数量是否满足RPO目标（1任务）
- **新增排除项前**：必须确认被排除内容确属"可重新生成"类别
- **修改 .ps1 文件前**：必须确保内容为纯 ASCII（禁止中文注释/非 ASCII 字符）——PowerShell 5.1 无 BOM 时按 ANSI 解码导致乱码，由 `check_encoding.py` (INJ-007) pre-commit GATE-ENCODING 强制检测
- **修改 PostgreSQL 凭据**：必须改 `config/.env.postgres`（真源），禁止改 `backup_config.yaml` 的 databases.postgres 字段（仅文档参考，不被代码消费）

---

## §11 测试策略

### §11.1 冒烟测试（首次实施后）

1. 执行首次备份，确认报告生成
2. 执行 `restore.ps1 verify <snapshot-id>`，确认恢复到临时目录
3. 对比恢复出的 `config/sla_targets.yaml` 与原文件，确认一致

### §11.2 增量测试

1. 修改一个配置文件
2. 再次执行备份，确认增量大小合理（<100MB）
3. 确认快照数量+1

### §11.3 恢复演练（建议每月）

1. 恢复最新快照到 `D:\restore_test\`
2. 验证关键文件存在：`AGENTS.md`、`config/`、`src/zephyr/`、`data/databases/`
3. 清理 `D:\restore_test\`
