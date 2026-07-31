---
module_id: MOD-INF-043
title: "dr_runbook — 灾难恢复操作手册"
doc_type: register
ttl: permanent
status: Active
version: "1.0.0"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-07-28"
last_updated: "2026-07-28"
summary: "从 F 盘备份逐步重建完整 ZephyrAlpha 环境的 AI 可执行灾难恢复操作清单，覆盖虚拟机/CH/PG/SQLite/代码全链路恢复步骤与验证命令"
tags: [disaster-recovery, runbook, backup, restore, MOD-INF-043]
responsibility_domain: 
design_maturity: production
---

# dr_runbook — 灾难恢复操作手册（AI 可执行）

> **读者**：执行从 F 盘备份进行灾难恢复的 AI 代理（或人类）。
> **目标**：从备份逐步重建完整可用的 ZephyrAlpha 环境。
> **最后更新**：2026-07-28 | 模块：MOD-INF-043
> **配套文档**：[backup_inventory.md](./backup_inventory.md) — 备份了什么内容以及存在哪里。

---

## 0. 何时使用本手册

当主环境（D:\ZephyrAlpha、PostgreSQL、ClickHouse 虚拟机）丢失或损坏，
需要从 F 盘备份重建时，使用本手册。

**不适用于**：单文件恢复（直接用 `restore.ps1 <子命令>`）、
或常规备份验证（用 `restore.ps1 verify`）。

---

## 1. 前置条件（需要重装的——不在备份中）

这些是系统级安装，记录在此供 AI 知道版本号。
备份覆盖代码 + 数据 + 配置；不覆盖安装包本身。

| 组件 | 版本 | 安装方式 | 验证位置 |
|------|------|----------|----------|
| Windows 操作系统 | 11 Pro | 系统重装 | — |
| Python | 3.12.x | https://python.org → `pip install -e .` 从 pyproject.toml 重建依赖 | `C:\Users\<用户>\AppData\Local\Programs\Python\Python312\` |
| PostgreSQL | 16 | https://postgresql.org 官方安装包 | `C:\Program Files\PostgreSQL\16\` |
| Hyper-V | Windows 功能 | `Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All` | — |
| ClickHouse | 26.6.1.1193 | （从虚拟机备份恢复——无需手动安装） | 虚拟机内部 |
| robocopy / git | 系统自带 / winget | `winget install Git.Git` | PATH |

**AI 验证命令**（重装前置条件后运行）：
```powershell
python --version          # 预期 3.12.x
psql --version            # 预期 16.x
(Get-Command Get-VM)      # 预期 Hyper-V 模块存在
robocopy /? | Select-Object -First 1   # 预期 robocopy 帮助信息
```

---

## 2. 快速恢复（自动化，F 盘完好时）

如果 F 盘备份幸存且前置条件已重装，运行：

```powershell
cd D:\ZephyrAlpha\scripts\backup
.\restore.ps1 inventory      # 1. 确认 F 盘备份产物存在
.\restore.ps1 verify         # 2. 验证备份完整性（只读，安全）
.\restore.ps1 all            # 3. 全量恢复：虚拟机 → CH → PG → SQLite → 代码
```

每个阶段会提示确认。加 `-Force` 跳过提示（自动化场景）。

**预期结果**：虚拟机导入、CH 数据恢复、PG 恢复、SQLite 恢复、
代码镜像完成。然后执行 §4 中的最终手动步骤。

---

## 3. 分步恢复（手动，用于部分恢复或调试）

### 步骤 3.1 — 恢复 ClickHouse 虚拟机（Hyper-V）

**内容**：从 `F:\ch_vm_backup\` 重新导入 zephyr-ch 虚拟机（boot.vhdx + data.vhdx + 配置）。
**停机时间**：无（虚拟机是新建，不是修改）。

```powershell
.\restore.ps1 vm
```

**执行操作**：
1. 删除现有 `zephyr-ch` 虚拟机（如存在，VHDX 文件保留在 F:\ch_vm_backup\）。
2. 从 `F:\ch_vm_backup\zephyr-ch\Virtual Machines\*.vmcx` 执行 `Import-VM`。
3. 启动虚拟机，等待 ClickHouse HTTP（端口 8123）就绪，最长 10 分钟。

**AI 验证**：
```powershell
Get-VM -Name zephyr-ch                       # 状态：Running
curl.exe -s http://localhost:8123/ --data-binary "SELECT 1"   # 预期：1
```

> **注意**：导入会在 F:\ch_vm_backup\ 原地注册虚拟机。生产环境建议
> 先将 VHDX 复制回 `D:\HyperV\VMs\zephyr-ch\`（备份盘
> F:\ch_backup_disk.vhdx 需单独重新附加到虚拟机——见步骤 3.2）。

### 步骤 3.2 — 重新附加 CH 备份 VHDX（如未自动附加）

CH 备份盘 `F:\ch_backup_disk.vhdx` 是增量备份目标。虚拟机导入后，
验证其已附加（虚拟机配置应引用它，但若路径变化，需手动重新附加）：

```powershell
# 检查备份盘是否已附加
Get-VMHardDiskDrive -VMName zephyr-ch | Format-Table ControllerType, Path
# 如果 F:\ch_backup_disk.vhdx 缺失，附加它：
Add-VMHardDiskDrive -VMName zephyr-ch -Path "F:\ch_backup_disk.vhdx" -ControllerType SCSI
```

在虚拟机内部，该盘挂载于 `/mnt/chbackup_local`（CH 命名磁盘 "backups"）。

### 步骤 3.3 — 恢复 ClickHouse 数据（基线 + 增量）

**内容**：先从基线（market.zip）再从增量（inc.zip）RESTORE c1_market + c3_fundamental。
**破坏性**：是——先删除现有 c1_market 和 c3_fundamental 数据库。

```powershell
.\restore.ps1 ch
```

**执行操作**：
1. 验证 CH 可达 + market.zip 存在于 VHDX。
2. `DROP DATABASE IF EXISTS c1_market / c3_fundamental`。
3. `RESTORE ... FROM Disk('backups', 'market.zip') ASYNC`（基线，约 199 GiB，可能需数小时）。
4. `RESTORE ... FROM Disk('backups', 'inc.zip') ASYNC`（增量，如存在）。
5. 打印行数 + 大小用于验证。

**AI 验证**：
```powershell
curl.exe -s http://localhost:8123/ --data-binary "SELECT database, count() as tables, sum(total_rows) as rows FROM system.tables WHERE database IN ('c1_market','c3_fundamental') GROUP BY database FORMAT PrettyCompact"
# 预期：约 101 张表，c1_market 中数十亿行
```

### 步骤 3.4 — 重建 ClickHouse RBAC（用户/角色）

CH 用户/角色不在备份中（它们是配置即代码）。从 YAML 重建：

```powershell
cd D:\ZephyrAlpha
python apply_rbac.py
```

**AI 验证**：
```powershell
curl.exe -s http://localhost:8123/ --data-binary "SELECT name FROM system.users WHERE name LIKE 'zephyr%' FORMAT TSV"
# 预期：zephyr_reader, zephyr_writer
```

### 步骤 3.5 — 恢复 PostgreSQL

**内容**：从 `F:\db_dumps\depgraph.dump` 恢复 depgraph 数据库 + 从 `pg_globals.sql` 恢复角色。

```powershell
.\restore.ps1 pg -drop
```

**执行操作**：
1. 从 `pg_globals.sql` 恢复角色（密码已掩码——必须重置）。
2. 删除 + 重建 `depgraph` 数据库。
3. 从 depgraph.dump 执行 `pg_restore`。
4. 打印表行数。

**重置角色密码**（全局密码已掩码）——从 `config\.env.postgres` 读取：
```sql
-- 在 psql 中以 postgres 身份运行：
ALTER ROLE zephyr PASSWORD 'zephyr_dev_2026';
ALTER ROLE depgraph_reader PASSWORD 'reader_dev_2026';
ALTER ROLE depgraph_writer PASSWORD 'writer_dev_2026';
```

**AI 验证**：
```powershell
psql -h localhost -U zephyr -d depgraph -c "SELECT count(*) FROM depgraph.nodes;"
# 预期：非零计数
```

### 步骤 3.6 — 恢复 SQLite 数据库

```powershell
.\restore.ps1 sqlite
```

将 `governance_backup.db` → `governance.db`、`session_backup.db` → `session_continuity.db`。

### 步骤 3.7 — 恢复代码

**内容**：从 `F:\code_backup\` → `D:\ZephyrAlpha\` 执行 robocopy /MIR（原地覆盖）。

```powershell
.\restore.ps1 code
```

**执行操作**：镜像代码 + 配置（包括备份时同步的
`config\system_configs\pg\` 和 `config\system_configs\ch\`）。排除 .git、缓存、.venv。

### 步骤 3.8 — 恢复 PostgreSQL 配置文件

将备份的 PG 配置从代码备份复制到 PG 数据目录：

```powershell
Copy-Item "D:\ZephyrAlpha\config\system_configs\pg\pg_hba.conf"      "C:\Program Files\PostgreSQL\16\data\" -Force
Copy-Item "D:\ZephyrAlpha\config\system_configs\pg\postgresql.conf"  "C:\Program Files\PostgreSQL\16\data\" -Force
Copy-Item "D:\ZephyrAlpha\config\system_configs\pg\pg_ident.conf"    "C:\Program Files\PostgreSQL\16\data\" -Force
# 重启 PG 使配置生效
Restart-Service postgresql-x64-16
```

### 步骤 3.9 — 重建 Python 环境

```powershell
cd D:\ZephyrAlpha
pip install -e .
```

**AI 验证**：
```powershell
python -c "import zephyr; print('zephyr importable')"
```

---

## 4. 最终验证清单

所有步骤完成后运行：

```powershell
cd D:\ZephyrAlpha\scripts\backup

# 1. 备份产物是否齐全？
.\restore.ps1 verify

# 2. PG 是否存活 + 有数据？
psql -h localhost -U zephyr -d depgraph -c "SELECT count(*) FROM depgraph.nodes;"

# 3. CH 是否存活 + 有数据？
curl.exe -s http://localhost:8123/ --data-binary "SELECT count() FROM c1_market.kline_daily"

# 4. Python 环境是否正常？
python -c "import zephyr; print('ok')"

# 5. 计划任务是否完好？
powershell -File .\backup_daily_trigger.ps1 -TaskStatus
powershell -File .\backup_ch_vm.ps1 -TaskStatus
```

全部通过 → 恢复完成。任一失败 → 见 §5。

---

## 5. 故障排除

### CH RESTORE 报 "BACKUP_FAILED"
- 查询 `system.backups` 获取错误信息：`SELECT * FROM system.backups WHERE id='<id>' FORMAT Vertical`
- 常见原因：目标数据库未完全删除。重新执行 `DROP DATABASE IF EXISTS` 后重试。
- 如果基线（market.zip）损坏：无法仅从 inc.zip 恢复——需从
  每日 BACKUP 流水线重建（需要运行中的 CH 和当前数据）。

### pg_restore 返回非零退出码
- 退出码 1 = 警告（角色所有权），可接受。退出码 >1 = 真正失败。
- 检查：`pg_restore -h localhost -U zephyr -d depgraph --list depgraph.dump`（查看内容）。

### 虚拟机导入失败
- 确保 Hyper-V 功能已启用。
- 如果 `.vmcx` 引用了缺失的 VHDX 路径：导入后编辑虚拟机设置指向 F:\ch_vm_backup\。

### inc.zip 缺失
- 如果上次备份是基线重建则可接受（下次运行会重建 inc）。
- 仅基线恢复有效——最多丢失 24 小时增量变更。

### F 盘不可访问
- 检查 `Get-Volume F`。如果离线：`Get-Disk | Where-Object {$_.BusType -eq 'USB'} | Set-Disk -IsOffline $false`
- 这是单点故障（#ARCH-CH-032，已接受的风险）。

---

## 6. 恢复时间预估

| 步骤 | 时间 | 备注 |
|------|------|------|
| 虚拟机导入 + 启动 | 约 5 分钟 | VHDX 已在 F 盘，只需注册 |
| CH RESTORE 基线 | 1-3 小时 | 199 GiB，取决于磁盘速度 |
| CH RESTORE 增量 | 5-15 分钟 | 1-5 GiB 增量 |
| RBAC 重建 | <1 分钟 | apply_rbac.py |
| PG 恢复 | <1 分钟 | 1.5 MB 转储 |
| SQLite 恢复 | <1 分钟 | 几 MB |
| 代码 robocopy | 5-30 分钟 | 取决于变更量 |
| Python pip install | 5-10 分钟 | 取决于缓存 |
| **总计（全量灾难恢复）** | **约 2-4 小时** | 主要耗时在 CH RESTORE 基线 |

---

## 7. 关键文件参考

| 文件 | 用途 |
|------|------|
| `scripts/backup/restore.ps1` | 恢复入口（inventory/verify/code/pg/sqlite/ch/vm/all） |
| `scripts/backup/backup.ps1` | 备份流水线（由每日任务 + 提交后 reconciler 调用） |
| `scripts/backup/backup_daily_trigger.ps1` | 每日 06:00 计划任务包装器 |
| `scripts/backup/backup_ch_vm.ps1` | 虚拟机备份（手动 -Force 或每周 -AutoCheck） |
| `scripts/backup/ch_vm_ssh.py` | 虚拟机文件操作 SSH 辅助工具（--sync-config, --stat-backup） |
| `scripts/backup/backup_config.yaml` | 备份配置（路径、阈值、触发规则） |
| `data/databases/backup_state.json` | 实时备份状态（last_backup_time、CH 状态、虚拟机版本/哈希） |
| `config/.env.ch_backup` | 虚拟机 SSH 凭证 + VHDX 路径 |
| `config/.env.postgres` | PG 凭证 |
| `config/.env.clickhouse` | CH HTTP 端点 + RBAC 用户 |
| `config/system_configs/pg/` | 备份的 PG 配置（pg_hba.conf, postgresql.conf, pg_ident.conf） |
| `config/system_configs/ch/` | 备份的 CH 配置（config.xml, users.xml, backup_disk.xml, fstab） |
