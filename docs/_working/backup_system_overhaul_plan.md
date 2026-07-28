---
ttl: task_bound
---
# 备份系统改造方案 v1.0

> 日期: 2026-07-28 | 模块: MOD-INF-043 | 状态: 待确认

## 一、背景与目标

ZephyrAlpha 量化金融研究项目需要一套**开箱即用、全自动、只覆盖变化内容、AI 友好**的灾备备份系统。

### 用户 6 条最终要求

1. **开箱即用** — 灾难恢复后立即可用（代码+数据库+程序+配置+Python环境+CH VM）
2. **每天必须触发一次** — 每日自动备份，保证每天至少一份
3. **只覆盖变化内容** — 不全量复制、不累积版本、只写变化的部分（含数据库碎片级增量）
4. **AI 友好恢复** — dr_runbook 让 AI 照做就能恢复
5. **最简单最有效** — robocopy/pg_dump/CH BACKUP，不用 restic
6. **备份清单让 AI 知道** — backup_inventory.md 完整清单

## 二、现状分析

### 环境清单

| 组件 | 位置 | 大小 |
|------|------|------|
| 代码 | D:\ZephyrAlpha | ~10GB |
| PostgreSQL 16 | C:\Program Files\PostgreSQL\16\ (localhost:5432, db=depgraph) | ~1.5MB dump |
| SQLite | D:\ZephyrAlpha\data\databases\governance.db + session_continuity.db | ~几MB |
| ClickHouse | Hyper-V VM (D:\HyperV\VMs\zephyr-ch\), 172.24.30.100:8123 | data.vhdx 555GB |
| Python 3.12 | C:\Users\fanzi\AppData\Local\Programs\Python\Python312\ | pyproject.toml |
| 备份盘 F: | 外接硬盘 1863GB, 剩余 1240GB | — |

### VM 磁盘布局（SSH 确认）

```
sda (80G)  = boot.vhdx    ← 空盘，未挂载，未使用（4MB on disk）
sdb (600G) = data.vhdx    ← 一切都在这里（555GB on disk）
  ├─ sdb1 (1G)   /boot/efi     (EFI引导分区, vfat)
  └─ sdb2 (599G) /             (根文件系统, ext4: Ubuntu + CH程序 + CH配置 + CH数据)
sdc (1T)   = ch_backup_disk.vhdx ← CH备份目标盘 (挂载在 /mnt/chbackup_local)
```

**关键发现**: boot.vhdx 是空盘（VM 未使用），OS + CH程序 + CH配置 + CH数据全在 data.vhdx 上。

### 当前备份系统问题

| 问题 | 详情 |
|------|------|
| restic 累积版本 | 14 个快照, 仓库膨胀到 405GB |
| CH 每天全量 199GB | delete market.zip + recreate = 每天写 199GB 到外接盘 |
| 无 VM 备份 | CH 程序/OS 未备份，灾难时需从头安装 |
| 无 PG 配置备份 | pg_hba.conf 等未备份 |
| 无 CH 配置备份 | config.xml/users.xml/backup_disk.xml 在 VM 内，未同步 |
| 无每日保底触发 | post-commit 不保证每天触发（无 commit = 无备份）|
| 无 dr_runbook | 恢复无文档，AI 无法照做 |
| 无备份清单 | 无完整清单文档 |

## 三、备份架构设计

### 总览

```
F: 盘（外接硬盘，备份目标）
├── F:\code_backup\          ← 代码+配置+PG配置+CH配置 (robocopy /MIR)
├── F:\db_dumps\             ← PG dump + SQLite dump (robocopy /MIR)
├── F:\ch_backup_disk.vhdx   ← CH数据备份 (VHDX虚拟硬盘, 已有)
│   └── /mnt/chbackup_local/
│       ├── market.zip       ← CH全量基线 (一次性, ~199GB)
│       └── inc.zip          ← CH每日增量 (覆盖重写, ~1-5GB)
└── F:\ch_vm_backup\         ← CH虚拟机 (智能周备)
    ├── boot.vhdx            ← 空盘 (4MB, 顺带备份)
    ├── data.vhdx            ← OS+CH程序+配置 (555GB, 仅CH升级时更新)
    └── zephyr-ch\           ← VM配置 (.vmcx/.vmgs)
```

### 3.1 代码备份 — robocopy /MIR

| 项 | 值 |
|----|-----|
| 源 | D:\ZephyrAlpha |
| 目标 | F:\code_backup |
| 方式 | `robocopy D:\ZephyrAlpha F:\code_backup /MIR /XD .git node_modules __pycache__ .pytest_cache .mypy_cache .ruff_cache .runtime .aidrafts tmp .venv /XF *.pyc *.db-wal *.db-shm` |
| 覆盖策略 | 镜像覆盖（/MIR 删除目标多余文件，仅复制变化的文件）|
| 每日写入 | ~10-100MB（仅变化文件）|
| 频率 | 每日 |

**为什么 robocopy 满足"只覆盖变化"**: robocopy 逐文件比较源和目标的时间戳+大小，相同的跳过（零写入），不同的覆盖。不是全量复制，不是累积版本。

### 3.2 PG 备份 — pg_dump + 配置同步

| 项 | 值 |
|----|-----|
| PG 数据 | `pg_dump -Fc -h localhost -U zephyr -d depgraph → D:\tmp_db_dumps\depgraph.dump` (~1.5MB, 覆盖) |
| PG 角色 | `psql ... pg_roles → D:\tmp_db_dumps\pg_globals.sql` (覆盖, 密码掩码) |
| PG 配置 | Copy-Item `C:\Program Files\PostgreSQL\16\data\{pg_hba,postgresql,pg_ident}.conf` → `config\system_configs\pg\` |
| 每日写入 | ~1.5MB（极小，全量覆盖合理）|
| 频率 | 每日 |

### 3.3 SQLite 备份 — .backup

| 项 | 值 |
|----|-----|
| 源 | governance.db + session_continuity.db |
| 目标 | D:\tmp_db_dumps\ (覆盖) |
| 方式 | `sqlite3 src ".backup dst"` 或 Python sqlite3.backup fallback |
| 每日写入 | ~几MB（极小）|
| 频率 | 每日 |

### 3.4 DB dumps → F: — robocopy /MIR

| 项 | 值 |
|----|-----|
| 源 | D:\tmp_db_dumps |
| 目标 | F:\db_dumps |
| 方式 | `robocopy D:\tmp_db_dumps F:\db_dumps /MIR` |
| 频率 | 每日（在 DB dump 之后）|

### 3.5 CH 数据备份 — 增量 (base + inc)

**核心设计**（回应要求 #3 "数据库能不能识别不同碎片只覆盖碎片"）:

```
首次（或重建基线）:
  BACKUP DATABASE c1_market, c3_fundamental TO Disk('backups', 'market.zip')
  → 全量基线 market.zip (~199GB, 一次性写入)

之后每天:
  BACKUP DATABASE ... TO Disk('backups', 'inc.zip')
    SETTINGS base_backup = Disk('backups', 'market.zip')
  → inc.zip 只含自 base 以来变化的数据 parts (~1-5GB)
  → 每天先删旧 inc.zip 再建新的（覆盖，非累积）

自动重建基线（全自动）:
  当 inc.zip ≥ 50% × market.zip 大小时
  → 删 inc.zip + market.zip，创建新全量 market.zip
  → 下一天起 inc.zip 重新从小开始
```

| 项 | 值 |
|----|-----|
| 基线 | market.zip (~199GB, 一次性, inc 膨胀时自动重建) |
| 增量 | inc.zip (~1-5GB, 每日覆盖重写) |
| 每日写入 | ~1-5GB（vs 旧方案 199GB/天，降 98%）|
| 恢复 | RESTORE market.zip → RESTORE inc.zip (2步, CH原生叠加) |
| 频率 | 每日 |

**为什么 inc.zip 是"覆盖"不是"累积"**: 每次 inc.zip = 从 base 到现在的全部变化（不是链式 delta），所以只有一个 inc.zip 文件，每天覆盖重写。

### 3.6 CH 配置备份 — SSH 同步

| 项 | 值 |
|----|-----|
| 源 | VM 内 /etc/clickhouse-server/ (config.xml, users.xml, config.d/*.xml) + /etc/fstab |
| 目标 | D:\ZephyrAlpha\config\system_configs\ch\ (随代码 robocopy 带走) |
| 方式 | ch_vm_ssh.py --cmd "cat <file>" → 写入本地文件 |
| 频率 | 每日 |
| 大小 | ~110KB（极小）|

**文件清单**: config.xml (100KB), users.xml (6.8KB), config.d/backup_disk.xml (380B), fstab (挂载参考)

### 3.7 CH VM 备份 — 智能周备

**策略**: 每周六自动检查 CH 版本 + 配置哈希，无变化则跳过（零停机），有变化才停机备份。

```
每周六 6:00 自动触发 backup_ch_vm.ps1:
  1. SSH 检查: clickhouse-server --version + config 文件哈希
  2. 与上次记录对比 (存在 backup_state.json)
  3. 版本+配置均未变 → 跳过, 记日志, 零停机
  4. 版本或配置变了 → 停VM → robocopy data.vhdx+boot.vhdx+config → 启VM → 更新记录
```

| 项 | 值 |
|----|-----|
| 源 | D:\HyperV\VMs\zephyr-ch\ (boot.vhdx 4MB + data.vhdx 555GB + zephyr-ch\ config) |
| 目标 | F:\ch_vm_backup\ |
| 方式 | Stop-VM → robocopy → Start-VM |
| 触发 | 每周六 6:00 Windows 计划任务（自动检查，变化才备份）|
| 停机 | 仅 CH 升级/配置变更时 ~1h；正常周备零停机 |
| 频率 | 每周检查（实际备份仅 CH 升级时）|

**为什么 data.vhdx 不每周全量复制**: data.vhdx (555GB) 每天因 CH 写数据而变化，但数据本身由每日 BACKUP TO Disk 增量备份覆盖。VM 备份的 value 是 OS + CH程序 + 配置（静态，仅升级时变）。智能检查避免 99% 周次的无效 555GB 复制。

### 3.8 Python 环境

| 项 | 值 |
|----|-----|
| 依赖清单 | pyproject.toml (在代码目录, 随 robocopy 备份) |
| 恢复 | `pip install -e .` (从 pyproject.toml 重建) |
| Python 本体 | 需从 python.org 重装 (dr_runbook 记录版本 3.12) |

## 四、触发机制

### 4.1 每日备份（保底）

| 项 | 值 |
|----|-----|
| 触发 | Windows 计划任务 `ZephyrAlpha-DailyBackup` |
| 时间 | 每天 06:00 |
| 命令 | `powershell -ExecutionPolicy Bypass -File D:\ZephyrAlpha\scripts\backup\backup.ps1 -Mode all -Force` |
| 补跑 | StartWhenAvailable（机器 6:00 关着则开机后补跑）|
| 运行级别 | Highest（当前用户）|

### 4.2 post-commit 补充触发（保留）

| 项 | 值 |
|----|-----|
| 触发 | backup_reconciler.py (post-commit reconciler) |
| 条件 | 重要文件变更 + ≥8h 间隔 |
| 作用 | 白天开发时 commit 后及时备份（不等次日 6:00）|

### 4.3 每周 VM 备份

| 项 | 值 |
|----|-----|
| 触发 | Windows 计划任务 `ZephyrAlpha-WeeklyVMBackup` |
| 时间 | 每周六 06:00 |
| 命令 | `powershell -ExecutionPolicy Bypass -File D:\ZephyrAlpha\scripts\backup\backup_ch_vm.ps1 -AutoCheck` |

### 4.4 并发保护

`backup.ps1` 启动时创建锁文件 `D:\ZephyrAlpha\.runtime\backup.lock`，退出时删除。post-commit 和每日任务不会同时运行。

## 五、每日写入量对比

| 组件 | 改造前 | 改造后 |
|------|--------|--------|
| 代码 | restic 增量但累积 14 快照 (405GB 仓库) | robocopy 仅变化文件 (~10-100MB) |
| PG/SQLite | ~2MB | ~2MB（不变）|
| CH | **199GB/天**（全量重写）| **~1-5GB/天**（增量覆盖）|
| **日总写入** | **~209GB** | **~1-5GB**（降 98%）|
| F: 累积 | restic 405GB + 增长 | 删 restic 后稳定（base+inc 固定 2 文件）|

## 六、恢复流程（dr_runbook 概要）

```
1. 装环境: Python 3.12 + PostgreSQL 16 + Hyper-V (dr_runbook 记录版本和步骤)
2. 恢复代码: robocopy F:\code_backup D:\ZephyrAlpha /E
3. 装 Python 依赖: pip install -e .
4. 恢复 PG:
   a. 复制 config/system_configs/pg/*.conf → C:\Program Files\PostgreSQL\16\data\
   b. psql -f pg_globals.sql -d postgres (恢复角色)
   c. ALTER ROLE zephyr PASSWORD '...' (按 .env.postgres)
   d. pg_restore -d depgraph depgraph.dump
5. 恢复 SQLite: copy F:\db_dumps\*.db → data\databases\
6. 恢复 CH VM:
   a. Import-VM (从 F:\ch_vm_backup\zephyr-ch\ 配置)
   b. 附加 data.vhdx + boot.vhdx
   c. 附加 F:\ch_backup_disk.vhdx (备份盘)
   d. 启动 VM, 等待 CH 就绪
7. 恢复 CH 数据:
   a. RESTORE DATABASE c1_market, c3_fundamental FROM Disk('backups', 'market.zip')
   b. RESTORE DATABASE ... FROM Disk('backups', 'inc.zip')  (如果 inc.zip 存在)
8. 恢复 CH RBAC: python apply_rbac.py (从 YAML 重建用户/角色)
9. 逐项验证 (DR_RUNBOX 提供验证命令)
```

## 七、遗漏检查 (Gap Analysis)

### 已覆盖

| 备份项 | 方式 | 覆盖状态 |
|--------|------|---------|
| 代码 | robocopy /MIR | ✅ |
| PG 数据 | pg_dump -Fc | ✅ |
| PG 角色 | pg_globals.sql | ✅ |
| PG 配置 | Copy-Item → config/system_configs/pg/ | ✅ |
| SQLite | .backup | ✅ |
| CH 数据 | BACKUP 增量 (base+inc) | ✅ |
| CH 配置 | SSH sync → config/system_configs/ch/ | ✅ |
| CH RBAC 用户 | apply_rbac.py (配置即代码) | ✅ |
| CH VM (OS+程序) | 智能周备 data.vhdx | ✅ |
| Python 依赖 | pyproject.toml (随代码) | ✅ |
| .env 凭据 | 随代码 robocopy (config/.env.*) | ✅ |

### 需重装（dr_runbook 记录，不在备份范围）

| 项 | 原因 | 恢复方式 |
|----|------|---------|
| Python 3.12 | 系统级安装 | python.org 下载安装 |
| PostgreSQL 16 | 系统级安装 | 官方安装包 |
| Hyper-V | Windows 功能 | Enable-WindowsOptionalFeature |
| Windows OS | — | 系统重装 |
| robocopy/sqlite3/git | 系统工具 | winget 安装 |

### 已知风险（用户已接受）

| 风险 | 详情 | 裁定 |
|------|------|------|
| F: 盘单点故障 | 所有备份在 F: 一个外接盘，F: 损坏则全丢 | #ARCH-CH-032 overruled_by_user (单用户回测期，外接盘足够) |
| CH 增量 inc.zip 增长 | inc.zip 随数据变化累积，到 50% base 时自动重建 | 自动处理，无需人工 |
| boot.vhdx 空盘 | 未使用，备份无实际意义 | 顺带备份（4MB），无成本 |

## 八、实施任务清单

| # | 任务 | 文件 | 优先级 |
|---|------|------|--------|
| 0 | PG 配置已复制 | config/system_configs/pg/ | ✅ 已完成 |
| 1 | 重写 backup.ps1 | scripts/backup/backup.ps1 | 高 |
| 2 | 更新 backup_config.yaml | scripts/backup/backup_config.yaml | 高 |
| 3 | 更新 backup_reconciler.py | scripts/backup/backup_reconciler.py | 高 |
| 4 | 重写 restore.ps1 | scripts/backup/restore.ps1 | 高 |
| 5 | 创建 backup_daily_trigger.ps1 + 注册计划任务 | scripts/backup/backup_daily_trigger.ps1 | 高 |
| 6 | 更新 backup_ch_vm.ps1 (智能检查模式) | scripts/backup/backup_ch_vm.ps1 | 高 |
| 7 | 注册每周 VM 备份计划任务 | — | 高 |
| 8 | 创建 dr_runbook.md | docs/dr_runbook.md | 高 |
| 9 | 创建 backup_inventory.md | docs/backup_inventory.md | 高 |
| 10 | 更新 README.md | scripts/backup/README.md | 中 |
| 11 | 首次运行 VM 全量备份 | — | 高 |
| 12 | 删除 F:\restic-zephyr | — | 中（验证后）|
| 13 | 删除 config/.env.restic | — | 中 |

## 九、验证方法

1. **语法验证**: `powershell -Command "& { . scripts/backup/backup.ps1 -Mode code -Force }"` (干跑代码备份)
2. **robocopy 验证**: 检查 F:\code_backup 关键文件存在 (AGENTS.md, pyproject.toml, config/.env.postgres)
3. **CH 增量验证**: 首次创建 base market.zip，第二次创建 inc.zip，验证大小 << base
4. **VM 备份验证**: backup_ch_vm.ps1 -AutoCheck 检测无变化时跳过
5. **计划任务验证**: Get-ScheduledTask 确认 ZephyrAlpha-DailyBackup + ZephyrAlpha-WeeklyVMBackup 存在
6. **dr_runbook 验证**: AI 逐步执行恢复流程，每步有预期输出
