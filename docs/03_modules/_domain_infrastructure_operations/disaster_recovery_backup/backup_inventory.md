---
module_id: MOD-INF-043
title: "backup_inventory — 备份内容与方法清单"
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
summary: "完整记录备份内容/位置/方法/频率的清单——代码/PG/SQLite/CH数据/CH配置/CH虚拟机全覆盖，AI无需猜测即可理解备份布局"
tags: [backup, inventory, register, MOD-INF-043]
responsibility_domain: 
design_maturity: production
---

# backup_inventory — 备份内容与方法清单

> **用途**：完整记录备份了什么内容、存在哪里、用什么方法——让任何 AI 代理
> （或人类）无需猜测就能理解备份布局。
> **最后更新**：2026-07-28 | 模块：MOD-INF-043
> **配套文档**：[dr_runbook.md](./dr_runbook.md) — 如何从这些备份中恢复。

---

## 1. 备份目标盘

| 属性 | 值 |
|------|------|
| 驱动器 | F:（外接硬盘） |
| 总容量 | 1863 GB |
| 可用空间（截至 2026-07-28） | 1240 GB |
| 单点故障 | 是 — #ARCH-CH-032 用户已推翻（单用户回测期，已接受该风险） |

---

## 2. F 盘备份目录结构

```
F:\
├── code_backup\              ← 代码 + 配置 + PG 配置 + CH 配置（robocopy /MIR 镜像）
│   ├── src\                   （Python 源码）
│   ├── config\
│   │   ├── .env.postgres      （PG 凭证）
│   │   ├── .env.clickhouse    （CH 端点 + RBAC 用户）
│   │   ├── .env.ch_backup     （VM SSH 凭证）
│   │   ├── system_configs\
│   │   │   ├── pg\            （pg_hba.conf, postgresql.conf, pg_ident.conf）
│   │   │   └── ch\            （config.xml, users.xml, backup_disk.xml, fstab）
│   ├── docs\, scripts\, tests\
│   ├── pyproject.toml         （Python 依赖清单）
│   └── AGENTS.md, ...
│
├── db_dumps\                  ← PG 转储 + SQLite 转储（robocopy /MIR 镜像）
│   ├── depgraph.dump          （PG 自定义格式转储，约 1.5 MB）
│   ├── pg_globals.sql         （PG 角色，密码已掩码）
│   ├── governance_backup.db   （SQLite governance.db 副本）
│   └── session_backup.db      （SQLite session_continuity.db 副本）
│
├── ch_backup_disk.vhdx        ← CH 数据备份（1 TB 动态 VHDX，附加到虚拟机）
│   └──（虚拟机内部，挂载于 /mnt/chbackup_local/）
│       ├── market.zip         （CH 全量基线备份，约 199 GiB，一次性 + 自动重建基线）
│       └── inc.zip            （CH 每日增量备份，约 1-5 GiB，每天覆盖）
│
└── ch_vm_backup\              ← CH Hyper-V 虚拟机（智能周备，仅在 CH 升级时触发）
    ├── boot.vhdx              （EFI 启动盘，约 4 MB，空但已备份）
    ├── data.vhdx              （操作系统 + CH 程序 + 配置，约 555 GB）
    └── zephyr-ch\             （虚拟机配置：.vmcx, .vmgs, Virtual Machines\, Snapshots\）
```

---

## 3. 备份清单（内容 / 位置 / 方法 / 频率）

| # | 组件 | 来源 | 备份目标 | 方法 | 频率 | 覆盖策略 | 预估每日写入量 |
|---|------|------|----------|------|------|----------|----------------|
| 1 | 代码 + 配置 | `D:\ZephyrAlpha\` | `F:\code_backup\` | robocopy /MIR | 每日（06:00）+ 提交后 | 镜像（仅变更文件） | 约 10-100 MB |
| 2 | PG 数据 | PG `depgraph` 库 | `F:\db_dumps\depgraph.dump` | pg_dump -Fc | 每日 | 覆盖 | 约 1.5 MB |
| 3 | PG 角色 | PG `pg_roles` | `F:\db_dumps\pg_globals.sql` | psql 查询 | 每日 | 覆盖（密码已掩码） | <1 KB |
| 4 | PG 配置 | `C:\Program Files\PostgreSQL\16\data\*.conf` | `config\system_configs\pg\`（→ code_backup） | Copy-Item | 每日 | 覆盖 | 约 100 KB |
| 5 | SQLite（治理库） | `data\databases\governance.db` | `F:\db_dumps\governance_backup.db` | sqlite3 .backup / Python | 每日 | 覆盖 | 约几 MB |
| 6 | SQLite（会话库） | `data\databases\session_continuity.db` | `F:\db_dumps\session_backup.db` | sqlite3 .backup / Python | 每日 | 覆盖 | 约几 MB |
| 7 | CH 数据（基线） | CH c1_market + c3_fundamental | `F:\ch_backup_disk.vhdx` → market.zip | CH BACKUP TO Disk | 一次性 + 自动重建基线（增量 ≥50% 基线时） | 重建基线时覆盖 | 0（稳定不变） |
| 8 | CH 数据（增量） | CH c1_market + c3_fundamental | `F:\ch_backup_disk.vhdx` → inc.zip | CH BACKUP ... SETTINGS base_backup | 每日 | 覆盖（单文件） | 约 1-5 GiB |
| 9 | CH 配置 | 虚拟机 `/etc/clickhouse-server/*.xml` + `/etc/fstab` | `config\system_configs\ch\`（→ code_backup） | SSH cat（ch_vm_ssh.py --sync-config） | 每日 | 覆盖 | 约 110 KB |
| 10 | CH 虚拟机（系统+程序） | `D:\HyperV\VMs\zephyr-ch\` | `F:\ch_vm_backup\` | Stop-VM → robocopy → Start-VM | 每周六 06:00 AutoCheck；仅在 CH 版本/配置变更时全量 | robocopy /MIR | 0（跳过）或约 555 GB（罕见） |
| 11 | CH RBAC 用户 | CH `system.users` | （不备份 — 配置即代码） | `apply_rbac.py` 从 YAML 重建 | 恢复时 | 不适用 | 不适用 |
| 12 | Python 依赖 | pyproject.toml | `F:\code_backup\pyproject.toml`（通过 #1） | robocopy | 每日 | 镜像 | <10 KB |

---

## 4. 触发机制

| 触发器 | 时间安排 | 运行内容 | 运行级别 | 频率门控 |
|--------|----------|----------|----------|----------|
| Windows 计划任务 `ZephyrAlpha-DailyBackup` | 每日 06:00（+ StartWhenAvailable 补漏） | `backup.ps1 -Mode all -Force` | Limited | 锁文件防止重叠 |
| 提交后 reconciler | git 提交时（若涉及重要文件 + 距上次 ≥8 小时） | `backup.ps1`（通过 backup_reconciler.py） | 继承 | 最小间隔 8 小时 |
| Windows 计划任务 `ZephyrAlpha-WeeklyVMBackup` | 每周六 06:00（+ StartWhenAvailable） | `backup_ch_vm.ps1 -AutoCheck` | Limited* | CH 版本+配置未变更则跳过 |
| 手动 | 按需 | `backup_manual.ps1`（Force）或 `backup_ch_vm.ps1 -Force` | 当前用户 | 无 |

\* 周备任务注册为 Limited。AutoCheck 跳过路径（SSH 探测）无需管理员权限。
当 CH 版本/配置变更需要全量虚拟机备份时，需以管理员身份运行：
`powershell -ExecutionPolicy Bypass -File scripts\backup\backup_ch_vm.ps1 -Force`
（Hyper-V Stop-VM/Start-VM 需要管理员权限。CH 升级是手动事件。）

---

## 5. 并发与安全

| 机制 | 用途 |
|------|------|
| `.runtime/backup.lock` | 防止每日任务与提交后 reconciler 同时运行。4 小时后过期。 |
| CH 24 小时频率门控 | 若上次成功 CH 备份不到 24 小时，`backup.ps1` 跳过 CH 阶段（除非加 -Force）。每日任务使用 -Force。 |
| CH 异步 + 轮询 | BACKUP/RESTORE 异步执行；脚本轮询 `system.backups`（备份最长 3 小时 / 恢复最长 4 小时）。 |
| robocopy /MIR | 镜像语义——删除目标端多余文件，仅复制变更文件（无版本累积）。 |
| 锁文件 TTL | 4 小时——若备份崩溃，锁自动过期，下次运行正常执行。 |

---

## 6. CH 增量备份逻辑（基线 + 增量）

```
每次每日运行：
  1. 通过 SSH 获取 market.zip（基线）+ inc.zip（增量）的 stat 信息
  2. 决定模式：
     - 基线不存在               → 全量：创建 market.zip（删除旧 inc.zip）
     - inc.size / base.size ≥ 0.5 → 全量：重建基线（删除两者，重建 market.zip）
     - 其他                     → 增量：重建 inc.zip（base_backup=market.zip）
  3. BACKUP 前删除目标文件（覆盖，不累积）
  4. BACKUP ... TO Disk('backups', '<file>') [SETTINGS base_backup=...] ASYNC
  5. 轮询 system.backups 直到 BACKUP_CREATED / BACKUP_FAILED
  6. 验证 VHDX 上文件存在 + 大小合理性检查
```

**为什么 inc.zip 是"覆盖"而非"累积"**：每个 inc.zip 捕获自基线以来的全部变更
（而非增量链）。单文件，每日覆盖。当增长到 ≥50% 基线大小时，重建基线，
增量重置为小文件。

---

## 7. 未备份内容（及原因）

| 项目 | 原因 | 恢复方式 |
|------|------|----------|
| Python 3.12 安装包 | 系统级安装 | 从 python.org 重新安装（dr_runbook §1） |
| PostgreSQL 16 安装包 | 系统级安装 | 从 postgresql.org 重新安装（dr_runbook §1） |
| Hyper-V 功能 | Windows 功能 | `Enable-WindowsOptionalFeature`（dr_runbook §1） |
| Windows 操作系统 | — | 系统重装 |
| CH RBAC 用户密码 | 配置即代码（YAML 是真源） | `python apply_rbac.py` 重建（dr_runbook §3.4） |
| `.git/` 历史 | robocopy 排除（体积大，可从远程恢复） | 需要时 `git clone` 从远程拉取 |
| `.venv/`、缓存 | 排除（可重建） | `pip install -e .`（dr_runbook §3.9） |
| `F:\ch_backup_disk.vhdx` 本身 | 它就是备份目标（不会备份到自身） | 单点故障（#ARCH-CH-032） |

---

## 8. 验证命令（只读，安全）

```powershell
cd D:\ZephyrAlpha\scripts\backup

# F 盘备份产物完整清单
.\restore.ps1 inventory

# 完整性验证（关键文件 + CH 基线/增量 + 虚拟机 VHDX 存在性）
.\restore.ps1 verify

# 计划任务状态
.\backup_daily_trigger.ps1 -TaskStatus
.\backup_ch_vm.ps1 -TaskStatus

# 实时备份状态（last_backup_time、CH 状态、虚拟机版本/哈希）
Get-Content D:\ZephyrAlpha\data\databases\backup_state.json
```

---

## 9. 配置文件（真源）

| 配置文件 | 控制内容 | 消费者 |
|----------|----------|--------|
| `scripts/backup/backup_config.yaml` | 路径、排除列表、CH 基线/增量文件名、重建基线阈值、触发规则 | backup.ps1, backup_reconciler.py, restore.ps1 |
| `config/.env.ch_backup` | 虚拟机 SSH 凭证（主机/用户/密码）、VHDX 路径 | ch_vm_ssh.py, backup.ps1, backup_ch_vm.ps1 |
| `config/.env.postgres` | PG 凭证 + RBAC 用户 | backup.ps1, restore.ps1 |
| `config/.env.clickhouse` | CH HTTP 端点 + RBAC 用户 | backup.ps1, restore.ps1 |
| `data/databases/backup_state.json` | 实时状态（last_backup_time、CH 状态/字节数、虚拟机版本/哈希、autocheck 结果） | 所有备份脚本 |

---

## 10. 历史备注（restic 移除，2026-07-28）

之前的备份系统使用 restic（去重快照工具）。被替换的原因：
- restic 累积了 14 个快照，仓库膨胀到 405 GB
- CH 每天作为完整 199 GB 副本备份（无增量）
- 无虚拟机备份、无 PG/CH 配置备份、无灾难恢复手册

新系统（robocopy + CH BACKUP 增量）将每日写入量从约 209 GB 降至约 1-5 GB
（降低 98%），并增加了虚拟机备份、配置同步、dr_runbook 和本清单。

新系统首次全量备份成功后，`F:\restic-zephyr\`（405 GB）已删除。
`config/.env.restic` 已删除。restic 密码（ZephyrBackup2026!）不再需要。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-043`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-043` 的 9 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-043` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-043 | MOD-INF-043 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 9 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
