# 灾备备份系统使用说明 (v2.0 — robocopy + CH incremental)

> module_id: MOD-INF-043 | blueprint v2.0.0 | 2026-07-28
> Companion docs: [dr_runbook.md](../../docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/dr_runbook.md) | [backup_inventory.md](../../docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md)

## 设计原则

1. **开箱即用** — 灾难恢复后立即可用（代码+数据库+程序+配置+Python环境+CH VM）
2. **每天必须触发** — Windows 计划任务每日 06:00 保底 + post-commit 补充
3. **只覆盖变化内容** — robocopy /MIR 镜像 + CH 增量（base + inc），不累积版本
4. **AI 友好恢复** — `restore.ps1` 子命令 + dr_runbook.md 逐步可执行
5. **最简单最有效** — robocopy / pg_dump / CH BACKUP，无 restic 依赖

## 触发机制

| 触发器 | 时间 | 运行 | 级别 | 节奏保护 |
|--------|------|------|------|---------|
| Windows 任务 `ZephyrAlpha-DailyBackup` | 每日 06:00 (+ StartWhenAvailable 补跑) | `backup.ps1 -Mode all -Force` | Limited | Lock 文件防并发 |
| post-commit reconciler | git commit 后（重要文件 + ≥8h） | `backup.ps1` (via backup_reconciler.py) | 继承 | 8h 最小间隔 |
| Windows 任务 `ZephyrAlpha-WeeklyVMBackup` | 每周六 06:00 | `backup_ch_vm.ps1 -AutoCheck` | Limited* | CH 版本/配置无变化则跳过 |
| 手动 | 按需 | `backup_manual.ps1` 或 `backup_ch_vm.ps1 -Force` | 当前用户 | 无 |

\* Weekly 任务注册为 Limited。AutoCheck 跳过路径（SSH 探测）无需管理员。
CH 升级/配置变更需全量备份时，手动运行（需管理员）：
`powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -Force`

## 手动触发

```powershell
# 完整备份（代码+PG+SQLite+CH增量+配置同步），跳过节奏保护
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1

# 仅代码备份
powershell -ExecutionPolicy Bypass -File scripts\backup\backup.ps1 -Mode code -Force

# 仅 CH 备份
powershell -ExecutionPolicy Bypass -File scripts\backup\backup.ps1 -Mode ch -Force

# CH VM 全量备份（停机 ~1h，仅 CH 升级时运行）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -Force

# CH VM 智能检查（不停机，无变化则跳过）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -AutoCheck
```

## 计划任务管理

```powershell
# 每日任务
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_daily_trigger.ps1 -RegisterTask   # 注册
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_daily_trigger.ps1 -TaskStatus     # 状态
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_daily_trigger.ps1 -UnregisterTask # 注销

# 每周 VM 任务（注册需管理员）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -RegisterTask    # 注册（管理员）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -TaskStatus      # 状态
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -UnregisterTask  # 注销
```

## 灾难恢复

详见 [dr_runbook.md](../../docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/dr_runbook.md)。快速入口：

```powershell
cd scripts\backup
.\restore.ps1 inventory      # 查看 F: 盘备份清单
.\restore.ps1 verify         # 验证备份完整性（只读，安全）
.\restore.ps1 all            # 完整恢复：vm -> ch -> pg -> sqlite -> code

# 单项恢复
.\restore.ps1 vm             # 恢复 CH Hyper-V VM
.\restore.ps1 ch             # 恢复 ClickHouse（base + inc）
.\restore.ps1 pg -drop       # 恢复 PostgreSQL
.\restore.ps1 sqlite         # 恢复 SQLite
.\restore.ps1 code           # 恢复代码（robocopy /MIR）
```

## 首次使用（新环境配置）

### 1. 确保配置文件存在

| 文件 | 用途 | 必需字段 |
|------|------|---------|
| `config/.env.postgres` | PG 凭据 | POSTGRES_USER, POSTGRES_PASSWORD |
| `config/.env.clickhouse` | CH 端点 | CLICKHOUSE_HOST, CLICKHOUSE_HTTP_PORT |
| `config/.env.ch_backup` | VM SSH 凭据 | CH_VM_HOST, CH_VM_USER, CH_VM_PASSWORD |

### 2. 确保 F: 盘在线

外置盘 F: 必须已挂载（`Get-Volume F` 确认）。

### 3. 确保 CH 备份 VHDX 已附加

`F:\ch_backup_disk.vhdx`（1TB 动态 VHDX）需附加到 Hyper-V VM `zephyr-ch`，
VM 内挂载到 `/mnt/chbackup_local`，CH 配置命名磁盘 `backups`（`config.d/backup_disk.xml`）。

### 4. 注册计划任务

```powershell
# 每日任务（无需管理员）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_daily_trigger.ps1 -RegisterTask

# 每周 VM 任务（需管理员 — 右键 PowerShell "以管理员身份运行"）
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -RegisterTask
```

### 5. 首次备份

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
```

首次运行会创建 CH 全量基线 `market.zip`（~199 GiB，1-2h）。后续每日自动增量。

## 备份内容

详见 [backup_inventory.md](../../docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/backup_inventory.md)。概要：

| 组件 | 方式 | 每日写入 | 频率 |
|------|------|---------|------|
| 代码+配置 | robocopy /MIR | ~10-100 MB | 每日 |
| PG 数据 | pg_dump -Fc | ~1.5 MB | 每日 |
| PG 配置 | Copy-Item → config/system_configs/pg/ | ~100 KB | 每日 |
| SQLite | sqlite3 .backup | ~几 MB | 每日 |
| CH 数据（增量） | CH BACKUP base_backup | ~1-5 GiB | 每日 |
| CH 配置 | SSH sync → config/system_configs/ch/ | ~110 KB | 每日 |
| CH VM (OS+程序) | Stop-VM → robocopy → Start-VM | 0（跳过）或 ~555 GB | 每周检查（仅升级时备份） |

**排除**：`.git/` `node_modules/` `__pycache__/` `.pytest_cache/` `.mypy_cache/` `.ruff_cache/`
`.runtime/` `.aidrafts/` `tmp/` `.venv/` `*.pyc` `*.db-wal` `*.db-shm`

## CH 增量备份逻辑

```
每日运行：
  1. stat market.zip (base) + inc.zip (incremental)
  2. 决策：
     - base 缺失          → FULL: 创建 market.zip
     - inc/base ≥ 0.5     → FULL: 重建基线（删两者，重建 market.zip）
     - 否则               → INCREMENTAL: 重建 inc.zip (base_backup=market.zip)
  3. 删除目标文件后 BACKUP（覆盖，非累积）
  4. ASYNC + 轮询 system.backups（max 3h）
  5. 验证文件存在 + 大小合理性
```

inc.zip 每天覆盖重写（非链式累积）。当 inc ≥ 50% base 时自动重建基线。

## 并发与安全

| 机制 | 用途 |
|------|------|
| `.runtime/backup.lock` | 防止每日任务与 post-commit reconciler 同时运行（4h TTL 自动过期） |
| CH 24h 节奏门 | last_ch_backup_time 仅成功时推进；-Force 旁路（每日任务用 -Force） |
| CH ASYNC + 轮询 | BACKUP/RESTORE 异步执行，脚本轮询 system.backups |
| robocopy /MIR | 镜像语义 — 删除目标多余文件，仅复制变化文件 |

## 文件清单

| 文件 | 职责 |
|------|------|
| `backup_config.yaml` | 配置 SSoT（路径/排除/CH base+inc/触发条件） |
| `backup.ps1` | 主备份脚本（Pre-check → DB dump+配置同步 → CH增量 → 代码robocopy → 报告） |
| `backup_reconciler.py` | post-commit 事件触发器（双条件：重要文件 + 8h 间隔） |
| `backup_daily_trigger.ps1` | 每日 06:00 计划任务包装（-RegisterTask/-TaskStatus/-UnregisterTask） |
| `backup_ch_vm.ps1` | CH VM 备份（-Force 全量 / -AutoCheck 智能跳过 / -RegisterTask） |
| `backup_manual.ps1` | 手动兜底入口（-Force 模式） |
| `ch_vm_ssh.py` | SSH 辅助（--sync-config / --stat-backup / --delete-backup / --cmd） |
| `restore.ps1` | 恢复脚本（inventory/verify/code/pg/sqlite/ch/vm/all） |
| `README.md` | 本文档 |

外部依赖（不进 git）：`config/.env.ch_backup`、`config/.env.postgres`、`config/.env.clickhouse`、`F:\ch_backup_disk.vhdx`

## 历史变更（2026-07-28 v2.0）

- restic → robocopy /MIR（增量覆盖，不累积版本，无 restic 依赖）
- CH 全量 → 增量（base + inc，每日写入从 199 GB 降至 1-5 GB）
- 新增每日 06:00 计划任务（保底触发，不依赖 commit）
- 新增 CH VM 智能周备（AutoCheck，CH 无变化则零停机跳过）
- 新增 PG/CH 配置每日同步到 config/system_configs/
- 新增 dr_runbook.md + backup_inventory.md（AI 友好恢复文档）
- 删除 F:\restic-zephyr（405 GB）+ config/.env.restic
