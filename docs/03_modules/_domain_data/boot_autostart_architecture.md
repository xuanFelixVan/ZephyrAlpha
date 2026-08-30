---
module_id: MOD-L00-004
title: "开机启动架构——任务计划程序单一入口"
doc_type: architecture_view
status: Active
layer: L2_domain
layer_name: data_source
functional_domain: data
date: "2026-07-27"
version: "1.0.0"
last_updated: "2026-08-07"
ttl: permanent
language: zh
created_by: human_plus_agent
description: "ZephyrAlpha 开机启动架构: 任务计划程序为唯一自启真源, 7 项第一性原理约束, watchdog 四层防御(含心跳健康层), legacy 清除记录"
responsibility_domain: 
design_maturity: design
---

# Boot Autostart Architecture

> Module: D_DATA / scripts.start_scheduler / scripts.start_tick_subscriber / scripts.register_aux_tasks
> Last updated: 2026-07-27
> Status: production (legacy Startup folder entries removed 2026-07-27)

## 1. Design Principle (第一性原理)

ZephyrAlpha permanent services MUST auto-start on boot and self-heal on crash (AGENTS.md hard
constraint: 永久系统必须全自动——自动触发/运行/维护/关闭，禁止需手工干预的设计). The boot autostart
architecture satisfies this via a **single authoritative entry point: Windows Task Scheduler**.

The architecture must meet seven constraints derived from first principles:

| # | Constraint | Mechanism |
|---|---|---|
| C1 | Availability (auto-start + self-heal) | Task Scheduler AtLogOn + PT5M heartbeat + guard while-true |
| C2 | Correctness (no duplicate business process) | pid file lock + orphan cleanup + finally-kill |
| C3 | Single Source of Truth (one entry) | Task Scheduler is the sole entry; no .bat/.lnk/registry for ZA |
| C4 | Silent operation (no UI noise) | `-WindowStyle Hidden`, no console window flash |
| C5 | Resource efficiency (no redundant triggers) | Legacy Startup entries removed |
| C6 | Observability (failure traceable) | guard logs to tmp/*_guard.log |
| C7 | AI maintainability (declarative, idempotent) | register_*.ps1 scripts, Set-ScheduledTask in-place |

## 2. Single Entry Point (SSOT)

| Service | Task Name | Trigger | Script |
|---|---|---|---|
| Data Scheduler | `ZephyrAlpha_DataScheduler` | AtLogOn + PT5M heartbeat | scripts/start_scheduler.ps1 |
| Tick Subscriber | `ZephyrAlpha_TickSubscriber` | AtLogOn + PT5M heartbeat | scripts/start_tick_subscriber.ps1 |
| RSSHub | `ZephyrAlpha_RSSHub` | AtLogOn | `pm2 resurrect` (hidden) |
| Trae Cache Cleanup | `ZephyrAlpha_TraeCacheCleanup` | AtLogOn + PT30S delay | clean_trae_cache.ps1 |
| Process Reaper | `ZephyrAlpha_ProcessReaper` | AtLogOn + PT10M (one-shot) | `pythonw -m zephyr.trading.process_reaper` |

**Process Reaper（2026-08-28 裁定纳入，替代旧 ide_health_daemon 常驻守护模式）**：无状态
one-shot 清理器（模式先例 deadman_switch.ps1 #ARCH-BOOT-002 E），scan→判定→kill→exit，
无常驻进程/无心跳/无 pid 锁。治理范围：项目 python 残留进程（白名单优先 + 孤儿/超龄/
危险指标多重信号判定矩阵）+ Trae 幽灵窗口 + drift 指标（stash>5 自动清理）。白名单 =
本表永久服务 + Trae 进程树后代 + `data/runtime/process_reaper_keep.txt` 个案保留。
旧 ide_health_daemon「常驻守护 + AI 冷启动自觉拉起」模式违反 C1/C3 且实证失效
（track_task_process 零调用者死代码、守护死亡无人知），判定矩阵详见模块 docstring。
ExecutionTimeLimit=10min 由 OS 回收挂死实例（dogfood：清理器自身不得成为僵尸）。

**Task Scheduler is the sole entry point for ZephyrAlpha services.** No Startup folder .bat/.lnk,
no registry Run entries for ZA services.

## 3. Watchdog Architecture (scheduler / tick_subscriber / ch_health_probe)

```
Task Scheduler (OS-hosted, MultipleInstances=Parallel, survives user-mode kills)
  -> guard script (while-true, single-instance lock + heartbeat => idempotent re-entry / zombie takeover)
    -> python business process (zephyr.data.scheduler / zephyr.data.tick_subscriber / ch_health_probe.py)
```

Four-layer defense (fix #ARCH-BOOT-001, verified 2026-08-07):
1. **OS layer** — Task Scheduler AtLogOn + PT5M repeat. **`MultipleInstances=Parallel`**
   (Phase 1 治本): Task Scheduler is a DUMB periodic launcher; it must NOT participate in
   single-instance decisions. IgnoreNew blocks a new guard while a zombie guard holds the slot,
   defeating heartbeat takeover (root cause of the 08-06/08-07 2-day intraday outage). Parallel
   lets the 5min re-fire always launch a new powershell; the new powershell then either exits
   ("already running, heartbeat fresh") or takes over ("heartbeat stale").
2. **Guard layer** — `while($true)` auto-restarts the python child on crash. Runtime <10s is
   treated as startup failure (dep not ready / miniQMT not up), waits 30s before retry. Child
   monitoring **polls `$proc.HasExited`** (Phase 2 治本) instead of blocking `WaitForExit` —
   the latter deadlocks the main thread on certain Windows process-exit paths (zombie root cause).
3. **Single-instance layer** (SSoT) — pid file lock (`tmp/scheduler.lock` etc.). This is the
   SOLE single-instance enforcer. Stale lock (pid dead) triggers orphan cleanup: kill any
   business python from the dead guard (invariant: no guard => no business process). `finally`
   block kills child on guard exit.
4. **Heartbeat health layer** (Phase 2 治本) — guard writes `tmp/{scheduler,tick_subscriber,
   ch_health_probe}.heartbeat` every 15s (format `ISO8601|guard_pid|child_pid`). New guard
   takeover logic: PID alive **and** heartbeat <5min fresh → "already running, exit"; PID alive
   but heartbeat stale/missing → zombie → `Stop-Process` zombie guard + clean lock/heartbeat +
   fall through to orphan cleanup. This is the recovery path for zombie guards (layer 2 failure).

## 4. Legacy Removal (2026-07-27)

### 4.1 ZephyrAlpha Startup folder entries (removed)

| File | Why removed |
|---|---|
| `ZephyrAlpha_DataScheduler.lnk` | Redundant with Task Scheduler `ZephyrAlpha_DataScheduler` |
| `start_zephyr_scheduler.bat` | Redundant + flashed console window + dual-started tick_subscriber |

The pid lock made them "harmless" for correctness (losers exited immediately on lock contention),
but they violated C3 (SSOT) and C4 (silent) — flashed two blank PowerShell windows on every boot
and added redundant process spawn + guard-log noise. Task Scheduler AtLogOn trigger replaces them
with zero UX impact and identical availability.

### 4.2 RSSHub / TraeCache .bat -> Task Scheduler

| Old (.bat, flashed window) | New (Task Scheduler, silent) |
|---|---|
| `start_rsshub.bat` (`pm2 resurrect`) | `ZephyrAlpha_RSSHub` (hidden) |
| `CleanTraeCache.bat` (`timeout /t 30` + ps1) | `ZephyrAlpha_TraeCacheCleanup` (hidden, PT30S delay) |

Deployment: `powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1`

## 5. Deployment

```powershell
# One-time, no admin needed (interactive user):
powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1   # scheduler + tick_subscriber
powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1      # RSSHub + TraeCache

# Verify all four tasks:
schtasks /query /tn ZephyrAlpha_DataScheduler /v /fo LIST
schtasks /query /tn ZephyrAlpha_TickSubscriber /v /fo LIST
schtasks /query /tn ZephyrAlpha_RSSHub /v /fo LIST
schtasks /query /tn ZephyrAlpha_TraeCacheCleanup /v /fo LIST

# Manual start (AI sessions) — NEVER Start-Process from IDE terminal:
schtasks /run /tn ZephyrAlpha_DataScheduler
schtasks /run /tn ZephyrAlpha_TickSubscriber
```

## 6. Non-ZephyrAlpha Registry Run Entries

### Preserved (required)
- `国金证券QMT交易端_mini` (HKCU) — trading days, paired with `RestartMiniQmt` 16:00 daily task
- `SecurityHealth` (HKLM) — Windows Security Center systray
- `RtkAudUService` (HKLM) — Realtek audio background service

### Pending user decision (kept as of 2026-07-27)
- `MyWallpaperApp` (金十数据, HKCU) — keep if used daily
- `AweSun` (向日葵远程, HKLM) — keep if remote control needed

### Removed 2026-07-27 (junk)
- HKCU: `BaiduYunDetect`, `QuarkUpdaterTaskUser1.0.0.21`, `MicrosoftEdgeAutoLaunch_*`
- HKLM: `Logitech Download Assistant`, `apmwinapp` (Paragon HFS+)
- Service: `PCManager Service Store` (Microsoft PC Manager) — disabled

## 7. AI Maintainer Notes

- **NEVER** `Start-Process` guard scripts from an IDE terminal for production duty — the process
  dies with the terminal. Use `schtasks /run /tn <TaskName>`.
- **NEVER** `Unregister-ScheduledTask` + `Register-ScheduledTask` on an existing task — Unregister
  TERMINATES the running guard instance (root cause of silent guard deaths 2026-07-22). The
  `register_*.ps1` scripts use `Set-ScheduledTask` (in-place update, preserves running instance).
- To re-deploy after script changes: re-run `register_guard_tasks.ps1` / `register_aux_tasks.ps1`
  (both are idempotent).
- Backups: `tmp/startup_backup_20260727/` (Startup folder .bat/.lnk files + HKCU/HKLM Run .reg).
- Restore a removed Startup entry: copy from backup dir back to
  `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`.

## 8. Guard Watchdog 心跳治本（#ARCH-BOOT-001，已验证 resolved）

> 立项 2026-08-07。根因：2026-08-07 scheduler/tick_subscriber 主进程死亡、guard 僵尸化
> 导致 intraday 下载停滞 2 交易日（kline_1min 停在 08-05 15:00、tick_data 停在 08-04）。
> 当前状态 **resolved（已施工+端到端验证通过 2026-08-07）**。issue 登记：`architecture_issue_registry.yaml` #ARCH-BOOT-001。
>
> **scope 扩展（2026-08-07 Phase 1-4）**：初版方案（§8.1-8.3）仅覆盖 scheduler/tick 心跳逻辑，
> 端到端验证时发现 `IgnoreNew` 策略阻断新 guard 启动使心跳接管成为死代码（缺陷1）、
> ch_health_probe 同漏洞未纳入（缺陷2）、方案验证步骤4.3 在 IgnoreNew 下不可执行（缺陷3）。
> 扩展为 Phase 1-5 三层治本：A=Task Scheduler Parallel 策略、B=ch_health_probe 心跳、
> C=不变式回归测试。详见 §8.5。

### 8.1 问题根因

当前 guard（`scripts/start_scheduler.ps1` / `scripts/start_tick_subscriber.ps1`）用
`$proc.WaitForExit()` 纯阻塞等待子进程，存在两个治本缺陷：

1. **guard 僵尸化无自检**：`WaitForExit()` 在某些 Windows 进程退出场景下不返回，guard 主线程
   卡死（CPU=0），子进程已死但 guard 不 log "exited"、不重启。
2. **单实例锁只验 PID 存活、不验健康度**：Task Scheduler 每 5min 拉新 guard，锁检查只做
   `Get-Process -Id <guardPID>`——僵尸 guard 的 PID 仍在，新 guard 永远 "Guard already
   running, exit"，形成**死锁**，无法接管。

后果：scheduler/tick 主进程死亡后无人重启，intraday 下载停滞，直到人工介入。

### 8.2 治本方案：心跳 + 僵尸判定接管

核心思路：guard 定期写心跳时间戳；新 guard 启动时若 lock PID 存活但心跳超时，判定僵尸
并强制接管；子进程监控从纯阻塞 `WaitForExit` 改为轮询 `HasExited`（避免主线程死锁）。

| 机制 | 当前 | 治本后 |
|------|------|--------|
| 子进程退出检测 | `$proc.WaitForExit()` 纯阻塞 | 每 15s 轮询 `$proc.HasExited` |
| guard 健康自检 | 无 | 每 15s 写心跳文件 `tmp/scheduler.heartbeat` |
| 单实例锁接管判定 | 仅验 PID 存活 | PID 存活 **且** 心跳 < 5min 内更新；否则判僵尸接管 |
| 僵尸 guard 清理 | 无 | Stop-Process 僵尸 guard + 清 lock/heartbeat + orphan cleanup |

心跳文件格式：单行 `<ISO8601时间>|<guard_pid>|<child_pid>`，如
`2026-08-07T11:30:00+08:00|24040|25488`。

### 8.3 实施步骤

#### 步骤 1：改造 `scripts/start_scheduler.ps1`

**1.1** 新增心跳文件路径常量（`$LockFile` 旁）：

```powershell
$HeartbeatFile = Join-Path $TmpDir "scheduler.heartbeat"
```

**1.2** 新增写心跳函数：

```powershell
function Write-Heartbeat {
    param([int]$ChildPid)
    $ts = (Get-Date).ToString("o")  # ISO 8601, 含时区
    "$ts|$PID|$ChildPid" | Out-File -FilePath $HeartbeatFile -Encoding utf8 -NoNewline
}
```

**1.3** 单实例锁检查增加心跳超时判定（替换现有 `if (Test-Path $LockFile)` 块中"PID 存活即 exit"分支）：

```powershell
if (Test-Path $LockFile) {
    $lockPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if ($lockPid -match '^\d+$' -and (Get-Process -Id ([int]$lockPid) -ErrorAction SilentlyContinue)) {
        # 治本：PID 存活但心跳超时 → 判定僵尸 guard，强制接管
        $stale = $true
        if (Test-Path $HeartbeatFile) {
            try {
                $hb = (Get-Content $HeartbeatFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
                $hbTs = ($hb -split '\|')[0]
                if (((Get-Date) - ([datetime]$hbTs)).TotalMinutes -lt 5) { $stale = $false }
            } catch { }
        }
        if ($stale) {
            Write-GuardLog "Guard PID=$lockPid alive but heartbeat stale (>5min), force takeover (kill zombie guard)"
            Stop-Process -Id ([int]$lockPid) -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
            # 落入下方 orphan cleanup（既有逻辑保留）
        } else {
            Write-GuardLog "Guard already running (PID=$lockPid, heartbeat fresh), exit"
            exit 0
        }
    } else {
        Write-GuardLog "Cleaning stale lock (old PID=$lockPid no longer alive)"
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    # orphan cleanup（既有逻辑保留）：杀遗留业务 python
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("-m $BizModule") } |
        ForEach-Object { Write-GuardLog "Killing orphaned $BizModule (PID=$($_.ProcessId))"; Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}
```

**1.4** 子进程监控从 `WaitForExit` 改为轮询 + 心跳（替换 while-true 内部 `$proc.WaitForExit()`）：

```powershell
$proc = Start-Process -FilePath $PythonExe -ArgumentList "-m",$BizModule `
    -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru
Write-GuardLog "Scheduler started (PID=$($proc.Id)), polling exit (watchdog heartbeat every 15s)..."
Write-Heartbeat -ChildPid $proc.Id
# 治本：轮询 HasExited 代替纯 WaitForExit，避免主线程死锁；每 15s 写心跳
while (-not $proc.HasExited) {
    Start-Sleep -Seconds 15
    Write-Heartbeat -ChildPid $proc.Id
}
$exitCode = $proc.ExitCode
```

**1.5** finally 块追加清理心跳文件：

```powershell
finally {
    ...（既有 finally-kill 逻辑保留）
    Remove-Item $LockFile, $HeartbeatFile -Force -ErrorAction SilentlyContinue
}
```

#### 步骤 2：同步改造 `scripts/start_tick_subscriber.ps1`

- `$HeartbeatFile = Join-Path $TmpDir "tick_subscriber.heartbeat"`
- 复用 1.2–1.5 的 Write-Heartbeat 函数、锁超时判定、轮询 HasExited、finally 清理
- `$BizModule = "zephyr.data.tick_subscriber"`

#### 步骤 3：单元测试 `tests/scripts/test_guard_watchdog.py`（新建）

- `test_heartbeat_format`：Write-Heartbeat 写入 `ISO|guard|child` 三段格式正确
- `test_stale_heartbeat_triggers_takeover`：构造 >5min 旧心跳 → `$stale=true` → 接管路径
- `test_fresh_heartbeat_exits`：构造 <5min 新心跳 → `$stale=false` → "already running" exit 0
- `test_zombie_takeover_runs_orphan_cleanup`：僵尸接管后仍执行 orphan cleanup
- 用 mock `Start-Process` / `Get-Process` 避免真起 python

#### 步骤 4：端到端验证（手动）

4.1 部署：`powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1`
    （idempotent，`Set-ScheduledTask` in-place 更新，不杀运行实例）
4.2 正常路径：`schtasks /run /tn ZephyrAlpha_DataScheduler` → 确认 `tmp/scheduler.heartbeat`
    每 15s 更新 → `Stop-Process <scheduler_child_pid>` → 确认 guard log "exited" + 重启 attempt N+1
4.3 僵尸接管模拟：用 Process Explorer 挂起 guard 主线程（模拟僵尸：进程活但卡死）→
    等 >5min 心跳超时 → Task Scheduler 触发新 guard → 确认 log "heartbeat stale, force takeover"
    + 杀僵尸 + 接管 + orphan cleanup
4.4 回归：确认 intraday 下载正常、finally-kill 生效、无重复 scheduler 实例

#### 步骤 5：收尾

- 本文档 §3 Watchdog Architecture 表格更新：三层防御 → 四层（加"心跳健康层"）
- frontmatter `last_updated` → 施工日期
- `architecture_issue_registry.yaml` 中 #ARCH-BOOT-001 `status` 改 `resolved`、`fix_phase` 填施工阶段

### 8.4 风险与回退

- **检测延迟**：轮询 15s 引入最多 15s 子进程死亡检测延迟（可接受，远小于当前"无限期不重启"）
- **误判风险**：心跳超时阈值 5min——guard 在轮询循环每 15s 写心跳，正常永不超时；仅主线程
  卡死才会超时，判定准确
- **回退**：若改造有问题，`git revert` 两个 ps1 + 重跑 `register_guard_tasks.ps1`（in-place 更新）
- **不影响 xtquant 连接固化**：本改造仅治 guard 僵尸化；xtquant 进程级连接固化（QMT 启动后
  需重启 scheduler/tick）是独立问题，见 project_memory Lessons Learned，不在本 issue 范围

### 8.5 治本施工与端到端验证（2026-08-07，commit e8cf841c）

初版方案 §8.1-8.3 施工后发现端到端验证被 `IgnoreNew` 策略阻断，扩展为 Phase 1-5 三层治本：

| Phase | 治本项 | 文件 | 验证结果 |
|-------|--------|------|----------|
| 1 | Task Scheduler `MultipleInstances IgnoreNew→Parallel`（根因解除阻断） | scripts/register_guard_tasks.ps1 | ✅ schtasks /run 放行新 guard |
| 2 | ch_health_probe 心跳改造（镜像 scheduler/tick，一致性补全） | scripts/start_ch_health_probe.ps1 | ✅ 接管 9132→23384 + 心跳 15s |
| 3 | 不变式回归测试（钉死治本为可执行不变式，防 AI 回退） | tests/scripts/test_guard_invariants.py（新）+ test_guard_watchdog.py（扩展） | ✅ pytest 29 passed |
| 4 | 端到端验证（部署 + 三服务接管/心跳/崩溃重启） | — | ✅ 全绿（见下表） |
| 5 | 文档收尾 + issue 闭环 | boot_autostart_architecture.md / AGENTS.md / architecture_issue_registry.yaml | 本节 |

**端到端验证结果（2026-08-07 16:00-16:03）**：

| 验证项 | scheduler | tick_subscriber | ch_health_probe |
|--------|-----------|-----------------|-----------------|
| 僵尸接管（旧guard→新guard） | 24040→640 ✅ | 26940→19480 ✅ | 9132→23384 ✅ |
| 心跳每 15s 更新（格式 ISO\|guard\|child） | 640\|23232 ✅ | 19480\|7432 ✅ | 23384\|2364 ✅ |
| "polling exit" 日志（确认新脚本） | ✅ | ✅ | ✅ |
| 子进程崩溃→guard 重启 | 杀29640→attempt2(23232) ✅ | — | — |
| 探针运行 | — | — | 3s 探测 CH TCP+HTTP 双通连 ✅ |
| 旧僵尸全死 + 无重复实例 | 24040/26940/9132 全死，每服务1实例 ✅ |

**关键日志佐证**（scheduler_guard.log）：
```
15:59:50 Guard PID=24040 alive but heartbeat stale (>5min), force takeover (kill zombie guard)
15:59:52 Killing orphaned zephyr.data.scheduler (PID=25488)
15:59:53 Scheduler started (PID=29640), polling exit (watchdog heartbeat every 15s)...
16:00:53 Scheduler exited (exit=-1, uptime=00h01m00s)   # 杀子进程后轮询7s内检测
16:00:58 Starting scheduler (attempt 2)...                # 5s退避后重启
```

**不变式测试覆盖**（tests/scripts/test_guard_invariants.py，防 AI 回退）：
- `TestNoGuardUsesWaitForExit`：3 脚本禁用 `$proc.WaitForExit()`（僵尸根因），必须轮询 HasExited
- `TestRegisterGuardUsesParallel`：register_guard_tasks.ps1 必须 Parallel（禁 IgnoreNew）
- `TestRegisterAuxKeepsIgnoreNew`：register_aux_tasks.ps1 保持 IgnoreNew（文档化有意非对称：一次性 AtLogOn 任务无僵尸风险）
- `TestGuardsDefineHeartbeat`：3 脚本均定义 $HeartbeatFile + Write-Heartbeat + 5min 阈值 + finally 清理

### 8.6 战略补强（#ARCH-BOOT-002，已落地 2026-08-08）

主治本（Phase 1-5）已闭合僵尸接管闭环。以下三项战略补强已落地，闭合"全层失效无人知"循环：

- **D. 心跳原子写** ✅ 已落地：`Out-File` 截断+写非原子，新 guard 轮询期（5min PT5M）撞上旧 guard 写心跳的微秒窗口可能读到半写→误判 stale→假接管（杀健康 guard）。概率极低（5min×微秒级），零成本消除：3 个 guard 脚本 `Write-Heartbeat` 改为写 `$HeartbeatFile.tmp` + `Move-Item -Force`（同卷原子 rename）。不变式测试 `TestAtomicHeartbeatWrite` 钉死。
- **E. 死人开关告警** ✅ 已落地：2 日停摆是人工发现的，非系统告警。新建 `scripts/deadman_switch.ps1`——**无状态一次性 Task Scheduler 任务**（非 while-true guard，无僵尸风险），每 5min fire 读 3 个心跳文件，任一陈旧 >10min 即告警。**独立性第一性原理**：监控者不属被监控的 3 服务之一，只读心跳文件；若 3 服务全死，此任务仍独立 fire 并告警。**为何用 .ps1 而非 .py**：若故障根因是 Python 栈崩溃（坏 import/venv），.py 监控会跟着死；.ps1 读文件+发 webhook 零 Python 依赖。**告警通道**：飞书 webhook（推手机，复用 `ZEPHYR_FEISHU_WEBHOOK`，与 Alerter 同契约）+ Windows Event Log + 本地 `tmp/deadman_switch_alerts.log`（全审计无冷却）。**30min 冷却**防多小时停摆刷屏（同一 staleKey 30min 内只推一次手机）。**Fail-safe**：此任务自身死亡退化到 pre-E 现状（无监控），非倒退——无需无限递归监控。已注册为第 4 个 Task Scheduler 任务 `ZephyrAlpha_DeadmanSwitch`（`register_guard_tasks.ps1`）。不变式测试 `TestDeadmanSwitchInvariants` + `TestDeadmanSwitchRegistered` 钉死（一次性、无 WaitForExit、读 3 心跳、有冷却、有 webhook）。
- **F. `WaitForExit` 死锁根因文档化** ✅ 已落地：根因是 PowerShell 重定向输出管道满致 `WaitForExit` 不返回；polling 已绕过。3 个 guard 脚本头注释固化"pipe buffer fills → WaitForExit never returns → main thread deadlocks"知识点，防 AI "优化"回 `WaitForExit`。不变式测试 `TestWaitForExitRootCauseDocumented` 钉死。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L00-004`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L00-004` 的 155 个 file 节点 | design | `extract_depgraph.py --modules MOD-L00-004` |
| 数据流图 (dataflow) | 5 个 Dataset / 6 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L00-004 | MOD-L00-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 155 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
