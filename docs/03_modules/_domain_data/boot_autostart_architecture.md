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
last_updated: "2026-07-27"
ttl: permanent
language: zh
created_by: human_plus_agent
description: "ZephyrAlpha 开机启动架构: 任务计划程序为唯一自启真源, 7 项第一性原理约束, watchdog 三层防御, legacy 清除记录"
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

**Task Scheduler is the sole entry point for ZephyrAlpha services.** No Startup folder .bat/.lnk,
no registry Run entries for ZA services.

## 3. Watchdog Architecture (scheduler / tick_subscriber)

```
Task Scheduler (OS-hosted, survives user-mode kills)
  -> guard script (while-true, single-instance lock => idempotent re-entry)
    -> python business process (zephyr.data.scheduler / zephyr.data.tick_subscriber)
```

Three-layer defense:
1. **OS layer** — Task Scheduler AtLogOn + PT5M repeat. If guard dies, next fire (≤5min) revives it.
2. **Guard layer** — `while($true)` auto-restarts the python child on crash. Runtime <10s is
   treated as startup failure (dep not ready / miniQMT not up), waits 30s before retry.
3. **Single-instance layer** — pid file lock (`tmp/scheduler.lock` / `tmp/tick_subscriber.lock`).
   Stale lock (pid dead) triggers orphan cleanup: kill any business python from the dead guard
   (invariant: no guard => no business process). `finally` block kills child on guard exit.

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

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L00-004`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L00-004` 的 76 个 file 节点 | design | `extract_depgraph.py --modules MOD-L00-004` |
| 数据流图 (dataflow) | 5 个 Dataset / 6 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L00-004 | MOD-L00-004 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 76 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
