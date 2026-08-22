---
module_id: MOD-INF-043
submodule_path: scripts/backup
title: "灾备备份系统蓝图 v2.0 — robocopy代码镜像+VHDX虚拟硬盘CH备份+DB dump+VM全量+校验+报告"
doc_type: blueprint
template_for: blueprint
status: Active
version: "2.0.2"
layer: L0_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-07-09"
ttl: permanent
design_maturity: production
actual_disk_path: "scripts/backup/"
last_updated: "2026-07-28"
last_verified: "2026-07-28"
generation: 2
functional_domain: operations
summary: "灾备备份系统v2.0——restic退役，改为robocopy /MIR代码镜像+VHDX虚拟硬盘CH增量备份(base+inc)+pg_dump+sqlite3 .backup+CH VM全量周备。post-commit reconciler事件触发(8h间隔)+Windows计划任务(每日06:00/每周六06:00)双轨自动驱动，覆盖代码/PG/SQLite/CH数据/CH VM，目标盘F:(SanDisk 2TB)，RPO=24h RTO=2-4h"
tags: [backup, disaster-recovery, vhdx, robocopy, pg-dump, sqlite-backup, clickhouse-backup, vm-backup, reconciler, event-triggered]
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
build_status: generated
design_maturity: production
---
> module_id: MOD-INF-043 | version: 2.0.2 | status: active | layer: L0_infrastructure
> actual_disk_path: scripts/backup/ | generation: 2 | construction_progress: completed

# 灾备备份系统蓝图 v2.0 — robocopy代码镜像+VHDX虚拟硬盘CH备份+DB dump+VM全量+校验+报告

## v2.0 变更纪要（2026-07-28）

**v1.x→v2.0 重大变更**：restic 退役（F:\restic-zephyr 405GB 已清理），MinIO S3 桥/minio_tcp_relay.py 已删除。新方案：
- **代码备份**：robocopy /MIR 镜像（替代 restic backup），F:\code_backup\（~4.3GB）
- **CH 数据备份**：VHDX 虚拟硬盘（F:\ch_backup_disk.vhdx 1TB 动态）附加到 Hyper-V VM 为 /dev/sdc，CH `BACKUP TO Disk('backups', 'market.zip')` 增量(base+inc)，速率 3-4 GiB/min
- **CH VM 备份**：每周六 06:00 计划任务检查，仅 CH 升级/配置变更时触发全量（99%周次跳过），F:\ch_vm_backup\
- **触发**：post-commit reconciler(8h间隔) + Windows计划任务 ZephyrAlpha-DailyBackup(每日06:00) + ZephyrAlpha-WeeklyVMBackup(每周六06:00)
- **恢复**：restore.ps1 all (vm→ch→pg→sqlite→code) / restore.ps1 verify
- 每日写入从~209GB降至~1-5GB（降98%），DR 演练 5 组件 PASS

## 概述

灾备备份系统是 ZephyrAlpha 的数据安全底线——解决"单点故障=项目死亡"的核心风险。系统 v2.0 采用 **robocopy /MIR 代码镜像 + VHDX 虚拟硬盘 CH 增量备份** 方案（restic/MinIO 已退役），通过 **post-commit reconciler 事件触发 + Windows 计划任务双轨**自动驱动。覆盖代码/PG/SQLite/CH 数据/CH VM 五组件，目标盘 F:(SanDisk 2TB NTFS)，RPO=24h RTO=2-4h。

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-INF-043`

> **架构归属SSoT**：本蓝图
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR-CONTRACT]/[TESTS]`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `backup_reconciler.py` | §3.1 | post-commit reconciler（事件触发+间隔保护+调用backup.ps1） | 已实现 | |
| 2 | `backup.ps1` | §3.2 | 主备份脚本v2.0（robocopy代码+pg_dump+sqlite+CH BACKUP+VM检查+校验+报告） | 已实现 | |
| 3 | `backup_config.yaml` | §3.3 | 备份配置v2.0（路径/CH VM配置/触发条件/排除规则） | 已实现 | |
| 4 | `backup_manual.ps1` | §3.4 | 手动兜底触发入口（调用backup.ps1 -Force，跳过间隔保护） | 已实现 | |
| 5 | `restore.ps1` | §3.5 | 恢复脚本v2.0（all/verify/vm/ch/pg/sqlite/code 子命令） | 已实现 | |
| 6 | `ch_vm_ssh.py` | §3.6 | SSH辅助——CH VM操作（执行命令/删备份/查状态/同步CH配置到config/system_configs/） | 已实现 | |
| 7 | `backup_ch_vm.ps1` | §3.7 | CH VM全量备份（boot.vhdx+data.vhdx+VM配置→F:\ch_vm_backup\，AutoCheck智能跳过） | 已实现 | |
| 8 | `backup_daily_trigger.ps1` | §3.8 | Windows计划任务入口脚本（每日06:00调用backup.ps1 -Force） | 已实现 | |
| 9 | `README.md` | §3.9 | 使用说明（自动触发机制/手动触发/灾难恢复） | 已实现 | |

---

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-043`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-043` 的 2 个 file 节点 | prototype | `extract_depgraph.py --modules MOD-INF-043` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | （无节点） | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-043 | MOD-INF-043 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 2 文件 | 7 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 架构设计

### §1.1 v2.0 流水线

```
┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 1.预检  │ → │ 2.DB dump │ → │ 3.代码   │ → │ 4.CH数据 │ → │ 5.CH VM  │ → │ 6.校验   │
│         │   │           │   │ 镜像     │   │ 增量备份 │   │ 智能检查 │   │ +报告    │
│ F盘在线?│   │ pg_dump   │   │ robocopy │   │ BACKUP   │   │ AutoCheck│   │ 行数抽查 │
│ VHDX?   │   │ sqlite3   │   │ /MIR →   │   │ TO Disk  │   │ skip if  │   │ JSON报告 │
│ CH alive│   │ .backup   │   │ code_bak │   │ base+inc │   │ unchanged│   │ 终端输出 │
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

**CH 独立节奏（2026-07-19 治本）**：ClickHouse 全量备份 315GiB≈3h，与代码备份 8h 节奏解耦——CH 每 24h 至多一次（`last_ch_backup_time` 仅成功时推进，失败下一调度窗口重试），`-Force` 旁路（手动演练）。代码/PG/SQLite 保持 8h 节奏不变。

**状态文件不入 git（2026-07-19 治本）**：`backup_state.json` 为纯运行时产物，已 gitignore 并退出跟踪。根因：tracked 状态文件在并发会话 worktree merge 时被还原成旧版本 → 8h 间隔检查失效 → 备份风暴。

频率预估：日均1-2次（8小时间隔 + 仅重要文件变更触发，纯日志/cache变更不触发）

**手动触发（兜底路径）**：运行 `backup_manual.ps1`（右键"用PowerShell运行"或命令行），不受间隔保护限制（force模式）。

### §1.3 备份目标（v2.0 F: 盘布局）

| 路径 | 内容 | 大小 | 方式 |
|------|------|------|------|
| `F:\code_backup\` | 代码+配置+规则（D:\ZephyrAlpha 镜像） | ~4.3GB | robocopy /MIR |
| `F:\db_dumps\` | PG dump + SQLite .backup + pg_globals.sql | ~50MB | pg_dump -Fc / sqlite3 .backup |
| `F:\ch_backup_disk.vhdx` | CH 数据备份（1TB 动态 VHDX，附加到 VM 为 /dev/sdc） | base ~199GB + inc ~0.8GB | CH BACKUP TO Disk('backups', 'market.zip') 增量 |
| `F:\ch_vm_backup\` | CH VM 全量（boot.vhdx + data.vhdx + VM 配置） | ~555GB | robocopy（仅 CH 升级/配置变更时触发） |

- **目标盘**：F:(SanDisk Portable SSD 2TB NTFS，卷标 SanDisk2TB)
- **配置真源**：`scripts/backup/backup_config.yaml` + `config/.env.ch_backup`（CH_VM_HOST/USER/PASSWORD + CH_VHDX_PATH + CH_BACKUP_FILE）

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
        capture_output=True, text=True, timeout=14400,  # 4h超时（CH 315GiB S3桥备份，见§4.3）
    )
    if result.returncode == 0:
        _update_state(last_backup_time=now_iso())
        return ReconcileResult(action="auto_committed",
                               detail=f"backup ok (clickhouse={ch_status}): ...")
    if result.returncode == 2:  # CH阶段失败但代码备份成功（2026-07-19 治本：失败可见）
        _update_state(last_backup_time=now_iso(), last_backup_status="ch_failed")
        return ReconcileResult(action="warn",
                               detail=f"backup ok but ClickHouse stage failed: {ch_err}")
    else:
        return ReconcileResult(action="warn",
                               detail=f"backup failed: {result.stderr[-200:]}")
```

**状态文件** `data/databases/backup_state.json`（纯运行时产物，gitignored——tracked 状态会在并发会话 merge 时被还原导致备份风暴，2026-07-19 治本退出跟踪）：
```json
{
  "last_backup_time": "2026-07-09T19:30:00+08:00",
  "last_backup_snapshot_id": "a1b2c3d4",
  "last_backup_status": "ok",
  "last_ch_backup_time": "2026-07-18T21:23:00+08:00",
  "last_ch_backup_status": "ok",
  "last_ch_backup_error": "(仅失败时存在)"
}
```

### §3.2 backup.ps1 — 主备份脚本

**职责**：编排六阶段流水线，输出备份报告。接受可选 `-Force` 参数跳过间隔保护（手动触发用）。

**流程伪代码**：
```powershell
param([switch]$Force)  # 手动触发时传 -Force 跳过间隔保护

# 1. 预检
Assert-Path F:\  # F盘在线
Assert-Path F:\ch_backup_disk.vhdx  # VHDX存在
# CH VM 在线检查（ch_vm_ssh.py --cmd "echo ok"）

# 2. 数据库dump（写入 F:\db_dumps\）
pg_dump -Fc depgraph > F:\db_dumps\depgraph.dump
sqlite3 governance.db ".backup F:\db_dumps\governance_backup.db"

# 3. 代码镜像（robocopy /MIR，排除清单内嵌）
robocopy D:\ZephyrAlpha F:\code_backup /MIR `
    /XD __pycache__ .pytest_cache .mypy_cache .ruff_cache .aidrafts .runtime tmp `
    /XF *.log `
    /XD .venv node_modules

# 4. CH 数据增量备份（SSH 到 VM 执行 BACKUP TO Disk）
ch_vm_ssh.py --cmd "clickhouse-client --query=BACKUP DATABASE c1_market, DATABASE c3_fundamental TO Disk('backups', 'market.zip') SETTINGS base_backup = Disk('backups', 'market.zip')"
# inc>=50%base 时自动重建基线

# 5. CH VM 智能检查（AutoCheck：版本+配置 hash 无变化则跳过）
# 仅周六计划任务或 CH 升级时触发全量

# 6. 校验 + 报告
# 文件存在性 + 大小校验 → 输出终端 + logs\backup_report_YYYYMMDD.json
```

### §3.3 backup_config.yaml — 备份配置

**职责**：集中管理路径、保留策略（文档参考）、触发条件（backup_reconciler.py 和 backup.ps1 共同读取）。

**消费者映射**（F-06 Track B 治本，2026-07-17）：
- `repository.path` → backup.ps1 L50（regex 读取 restic repo path）
- `dump_dir` → backup.ps1 L51（regex 读取 DB dump 目录）
- `trigger.*` → backup_reconciler.py `_trigger()` + `_get_state_file()`（`_load_config` 加载，F-06 Track A 治本）
- `retention` → **DOCUMENTATION ONLY**（实际值硬编码在 backup.ps1 L49，YAML 非真源）

**已删除死配置**（F-06 Track B，无消费者）：`databases` / `excludes` / `report`

**关键字段**：
```yaml
repository:
  path: "F:\\restic-zephyr"
  target_drive: "F:"
dump_dir: "D:\\tmp_db_dumps"  # 项目外临时目录，避免被tmp/排除规则冲突
# --- DOCUMENTATION ONLY（非真源，不被任何脚本消费）---
# 实际 retention 值硬编码在 backup.ps1 L49：$KeepDaily=7; $KeepWeekly=4; $KeepMonthly=3
retention:
  keep_daily: 7    # = backup.ps1 $KeepDaily
  keep_weekly: 4    # = backup.ps1 $KeepWeekly
  keep_monthly: 3   # = backup.ps1 $KeepMonthly
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
```

### §3.4 backup_manual.ps1 — 手动兜底触发入口

**职责**：手动触发备份（force模式，跳过间隔保护），作为自动触发的兜底。右键"用PowerShell运行"或命令行执行。

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup\backup_manual.ps1
# 等价于: scripts\backup\backup.ps1 -Force
```

### §3.5 restore.ps1 — 恢复脚本（v2.0）

**职责**：查看备份清单/校验完整性/单组件恢复/全链路灾难恢复。

**子命令**：
- `.\restore.ps1 list` — 列出 F:\code_backup + db_dumps + ch_backup_disk.vhdx + ch_vm_backup 内容
- `.\restore.ps1 verify` — 校验五组件文件存在性+大小（无需 snapshot-id）
- `.\restore.ps1 all` — 全链路灾难恢复（vm→ch→pg→sqlite→code 顺序）
- `.\restore.ps1 vm` — 恢复 CH VM（boot.vhdx + data.vhdx + 重建 VM）
- `.\restore.ps1 ch` — 恢复 ClickHouse（SSH RESTORE FROM Disk('backups', 'market.zip') + inc.zip）
- `.\restore.ps1 pg` — 恢复 PostgreSQL（pg_restore depgraph.dump）
- `.\restore.ps1 sqlite` — 恢复 SQLite（覆盖 governance.db / session_continuity.db）
- `.\restore.ps1 code` — 恢复代码（robocopy F:\code_backup → D:\ZephyrAlpha）

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
# pg_dump resolution: PATH first, fallback to C:\Program Files\PostgreSQL\*\bin\pg_dump.exe (highest version)
# (backup.ps1 Stage 2 resolves $pgDumpCmd before this call; PG bin not in PATH on this machine)
& $pgDumpCmd -Fc -h localhost -U $pgUser -d depgraph -f "$DumpDir\depgraph.dump"
# Cluster globals (roles) - pg_dumpall -g needs superuser (zephyr lacks pg_authid access);
# generate CREATE ROLE from public pg_roles instead (passwords masked; reset post-restore from config/.env.postgres)
$psqlCmd = $pgDumpCmd -replace 'pg_dump\.exe$', 'psql.exe'
& $psqlCmd -t -A -c "SELECT 'CREATE ROLE ' || quote_ident(rolname) || ' WITH ' || ... FROM pg_roles WHERE rolname !~ '^pg_' AND rolname <> 'postgres';" > "$DumpDir\pg_globals.sql"
```

- 输出：`depgraph.dump`（压缩格式）+ `pg_globals.sql`（集群角色：zephyr / depgraph_reader / depgraph_writer）
- 恢复：①`psql -f pg_globals.sql -d postgres`（建角色）②按 `config/.env.postgres` `ALTER ROLE zephyr PASSWORD '...'`（pg_roles 不含密码）③`pg_restore -d depgraph depgraph.dump`

### §4.2 SQLite（governance.db / session_continuity.db）

```powershell
# 在线一致性备份（不阻塞写入，dump到项目外临时目录）
sqlite3 data\databases\governance.db ".backup D:\tmp_db_dumps\governance_backup.db"
sqlite3 data\databases\session_continuity.db ".backup D:\tmp_db_dumps\session_backup.db"
```

- `.backup` 命令保证一致性快照，优于文件复制

### §4.3 ClickHouse（c1_market + c3_fundamental）— VHDX 虚拟硬盘（v2.0）

**部署约束**：CH 26.6.1 部署于 Hyper-V VM（172.24.30.100），数据 315 GiB（c1_market 298.86 GiB/202.6亿行 + c3_fundamental 15.93 GiB）。v1.x 通过 MinIO S3 桥备份（速率 ~1.4 GiB/min，协议开销大），v2.0 改为 VHDX 虚拟硬盘直挂（速率 3-4 GiB/min）。

**架构**：在 F: 盘创建 1TB 动态 VHDX，附加到 VM 为 /dev/sdc，ext4 格式化挂载到 /mnt/chbackup_local，CH 命名磁盘 backups 指向该路径：

```
backup.ps1 (宿主机)
  1. 预检：F:\ch_backup_disk.vhdx 存在 + CH VM 在线（ch_vm_ssh.py --cmd "echo ok"）
  2. SSH 到 VM 执行 CH BACKUP：
     ch_vm_ssh.py --cmd "clickhouse-client --query=\"
       BACKUP DATABASE c1_market, DATABASE c3_fundamental
       TO Disk('backups', 'market.zip')
       SETTINGS base_backup = Disk('backups', 'market.zip')\" "
     （首次全量无 base_backup；后续增量基于 base_backup）
  3. 轮询 system.backups 至 BACKUP_CREATED（ch_vm_ssh.py --stat-backup market.zip）
  4. 增量≥50%base 时自动重建基线（删旧 base+inc，重新全量）
  5. CH VM 智能周备：AutoCheck 检测 CH 版本+配置 hash 无变化则跳过（99%周次零停机）
```

**增量策略**：
- base_backup：首次全量 `BACKUP ... TO Disk('backups', 'market.zip')`（~199GB）
- 每日增量：`BACKUP ... SETTINGS base_backup = Disk('backups', 'market.zip')` → `inc.zip`（~0.8GB/天）
- inc≥50%base 时自动重建基线（防增量链膨胀）
- 速率 3-4 GiB/min（vs CIFS 1.4 GiB/min）

**CH VM 全量备份（backup_ch_vm.ps1）**：
- 每周六 06:00 Windows 计划任务 ZephyrAlpha-WeeklyVMBackup 触发
- AutoCheck：SSH 检测 CH 版本 + VM 配置 hash，无变化则 skip（99%周次跳过）
- 仅 CH 升级/VM 配置变更时执行全量：boot.vhdx + data.vhdx + VM 配置 → F:\ch_vm_backup\
- 2026-07-28 首次全量已完成：data.vhdx 554.72GB，restore.ps1 verify ALL PASSED

**凭据**：`config/.env.ch_backup`（gitignored）：CH_VM_HOST/CH_VM_USER/CH_VM_PASSWORD/CH_VHDX_PATH/CH_BACKUP_FILE。SSH 辅助 `scripts/backup/ch_vm_ssh.py`（paramiko），VM 配置同步 `ch_vm_ssh.py --sync-config` → `config/system_configs/`（gitignored，可重新生成）。

**恢复**：`restore.ps1 ch` → SSH 到 VM 执行 `RESTORE DATABASE c1_market, DATABASE c3_fundamental FROM Disk('backups', 'market.zip')` + `RESTORE ... FROM Disk('backups', 'inc.zip')` → 行数抽查验证。全链路恢复用 `restore.ps1 all`（vm→ch→pg→sqlite→code 顺序）。

---

## §5 保留策略（v2.0）

### §5.1 代码/DB 备份（robocopy /MIR 覆盖式）

robocopy /MIR 每次执行覆盖镜像——始终保留最新一份，无历史版本。版本历史依赖 git（代码）+ DB dump 文件（PG/SQLite 每日覆盖）。无需 forget/prune 清理。

### §5.2 CH 数据备份（base+inc 增量链）

- `market.zip`（base，~199GB）+ `inc.zip`（增量，~0.8GB/天）
- inc≥50%base 时自动重建基线：删旧 base+inc → 重新全量 market.zip
- 无需手动清理——CH BACKUP 增量链自动管理

### §5.3 CH VM 备份（按需全量）

- 仅 CH 升级/VM 配置变更时触发全量（AutoCheck 智能跳过）
- F:\ch_vm_backup\ 覆盖式更新（boot.vhdx + data.vhdx + VM 配置）
- 99%周次零停机跳过

---

## §6 验证流程（v2.0）

### §6.1 自动校验（每次备份后）

1. 代码镜像：robocopy 退出码 0=成功（/MIR 镜像完成）
2. DB dump：文件存在性 + 大小>0 检查（pg_dump/sqlite3 .backup）
3. CH 数据：`ch_vm_ssh.py --stat-backup market.zip` 校验文件大小 >0 + ≤ chTotalSize*1.05
4. CH VM：`restore.ps1 verify` 校验 boot.vhdx/data.vhdx 文件完整性
5. 报告写入 `logs\backup_report_YYYYMMDD.json`

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
# v2.0: restore.ps1 verify 全组件校验
.\scripts\backup\restore.ps1 verify  # 校验 code/pg/sqlite/ch/vm 五组件
```

---

## §7 恢复流程

### §7.1 查看备份清单

```powershell
.\scripts\backup\restore.ps1 list
# v2.0: 列出 F:\code_backup + db_dumps + ch_backup_disk.vhdx + ch_vm_backup 内容
```

### §7.2 验证备份完整性

```powershell
.\scripts\backup\restore.ps1 verify
# v2.0: 校验 code/pg/sqlite/ch/vm 五组件文件存在性+大小
```

### §7.3 灾难恢复（全链路）

```powershell
.\scripts\backup\restore.ps1 all
# v2.0: 按顺序恢复 vm -> ch -> pg -> sqlite -> code
```

### §7.4 单组件恢复

- 代码：`restore.ps1 code`（robocopy F:\code_backup → D:\ZephyrAlpha）
- PostgreSQL：`restore.ps1 pg`（pg_restore -d depgraph F:\db_dumps\depgraph.dump）
- SQLite：`restore.ps1 sqlite`（覆盖 governance.db / session_continuity.db）
- ClickHouse：`restore.ps1 ch`（SSH 到 VM 执行 RESTORE FROM Disk('backups', 'market.zip') + inc.zip）
- CH VM：`restore.ps1 vm`（从 F:\ch_vm_backup 恢复 boot.vhdx + data.vhdx + 重建 VM）

---

## §8 不变量（Invariants）

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| INV-01 | F: 盘备份目录必须存在且可写（code_backup/db_dumps/ch_backup_disk.vhdx/ch_vm_backup） | 脚本预检 Assert-Path |
| INV-02 | 每次备份后必须校验文件存在性+大小>0 | 脚本流程强制 |
| INV-03 | dump文件必须先写入 `D:\tmp_db_dumps\`（项目外）再随项目一起备份 | 脚本流程强制 |
| INV-04 | 备份报告必须写入 `logs/backup_report_YYYYMMDD.json` | 脚本流程强制 |
| INV-05 | 排除清单必须包含 `.aidrafts/`（4.7GB临时草稿） | 配置文件校验 |
| INV-06 | 保留策略必须执行 `--prune` 清理无引用数据块 | 脚本流程强制 |
| INV-07 | 禁止备份VMS snapshot_backup（GATE-VMS-SSOT硬阻断，30GB灾难根源） | 排除清单+AGENTS.md约束 |
| INV-08 | backup_reconciler必须通过post-commit reconciler触发，禁止时间触发（PERM-TRIGGER gate） | AST门禁+reconciler注册校验 |
| INV-09 | 自动触发必须满足双条件：重要文件变更 + 8小时间隔保护 | `_trigger`函数逻辑+单元测试 |
| INV-10 | 备份状态必须持久化到 `data/databases/backup_state.json`（纯运行时产物，gitignored，禁止重新纳入跟踪） | 状态文件存在性校验 |
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
| robocopy (Windows内置) | 代码 /MIR 镜像 + CH VM VHDX 文件复制 |
| pg_dump (PostgreSQL客户端) | PG数据库dump |
| sqlite3 (SQLite客户端) | SQLite数据库dump |
| ch_vm_ssh.py (paramiko, pip) | SSH到CH VM执行BACKUP/RESTORE/配置同步 |
| Windows Task Scheduler | 每日06:00 + 每周六06:00 计划任务自动触发 |
| Hyper-V VHDX | 1TB动态虚拟硬盘附加到VM作为CH备份磁盘 |

### §9.2 下游消费者

| 消费者 | 用途 |
|--------|------|
| 运维人员（手动） | 灾难恢复时使用restore.ps1 |
| SLAMonitor (MOD-INF-016) | RTO/RPO达标验证（RTO目标300s，RPO目标1任务） |

---

## §10 修改守卫（Modify-Guard）

- **修改本蓝图前**：必须确认备份内容裁定（§2）是否需要同步调整
- **修改backup.ps1前**：必须确认六阶段流水线顺序不被破坏
- **修改保留策略前**：必须评估快照数量是否满足RPO目标（1任务）
- **新增排除项前**：必须确认被排除内容确属"可重新生成"类别
- **修改 .ps1 文件前**：必须确保内容为纯 ASCII（禁止中文注释/非 ASCII 字符）——PowerShell 5.1 无 BOM 时按 ANSI 解码导致乱码，双层强制（F-05 治本，2026-07-17）：① pre-commit GATE-ENCODING（`check_encoding.py` INJ-007）② GitCommitGateway ENCODING-SAFETY gate（`encoding_gate.py`，priority=42，subprocess 调 check_encoding.py 复用真源，覆盖 --no-verify 绕过路径）
- **修改 PostgreSQL 凭据**：必须改 `config/.env.postgres`（真源）。`backup_config.yaml` 的 `databases` 段已删除（F-06 Track B 死配置清理，2026-07-17），不再有第二决策点

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

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/dr/__init__.py` | ⚠️ 骨架 | |
| `tests/dr/test_restore_from_backup.py` | ✅ 已实现 | |
| `tests/scripts/test_optimize_merge.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


