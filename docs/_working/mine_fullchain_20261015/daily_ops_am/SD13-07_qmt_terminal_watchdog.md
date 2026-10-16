---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-07
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-07 QMT 终端看门狗

## 1. 定义

交易日 08:45 与 12:55 两拍（Windows 计划任务 ZephyrAlpha_QMTWatchdog）运行独立 ps1 脚本：判 XtItClient 进程存活，缺席且 exe 在则拉起并写一行留痕。无常驻进程、无循环、无 pid 锁，可任意次重入。不覆盖自动登录（🌑-1 点名项：登录只能人做）。决策问题：两拍 QMT 进程在不在？不在时谁来登录？

地图在册态：wiring=wired、build=built、skeleton ✅；是 D13-09 就绪门 C1 判据的现行执行者（双替身之一）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 进程面（Get-Process XtItClient）+ exe 存在性 | `scripts/qmt_watchdog.ps1:47-49`（实核 `$proc = Get-Process -Name "XtItClient"`、`OK process running (pid=...)`） |
| 输出面 | data/runtime/qmt_watchdog.log 逐行留痕（OK/拉起+pid）；末六行=连续三交易日两拍均 OK 且带 pid | `data/runtime/qmt_watchdog.log`；`scripts/qmt_watchdog.ps1:28` |
| SSOT 真源 | 图13 节点契约（行 624-697）+ 注册脚本声明面 | `config/trading_day_cycle_map.yaml#D13-07`；`scripts/qmt_watchdog.ps1`（New-ScheduledTaskTrigger 两拍时点在注册声明面） |
| 代码模块 | 看门狗 ps1 + 计划任务注册 | `scripts/qmt_watchdog.ps1`；机制=B_windows_task，schtasks_refs=ZephyrAlpha_QMTWatchdog（registered=true、declared_in_register_scripts=true 机生双证） |
| 门禁约束 | .ps1 纯 ASCII 铁律（PowerShell 5.1 无 BOM 按 GBK 解码）；不覆盖自动登录=失败可见性止于留痕，无人接（🌑 点名项，图不编造出处） | `AGENTS.md` §9.7；`config/trading_day_cycle_map.yaml#D13-07` fallback/note_zh |
| 自动化触发 | mechanism=B_windows_task，交易日 08:45/12:55 双拍；trigger_facts last_run=2026-10-08T12:55:01（240h 节拍窗内 count=1）；资源册 window_expr 未抽到双时点=跨机制漏拍 | `config/trading_day_cycle_map.yaml#D13-07` cadence_zh/trigger_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 进程探测单行实核在位 |
| 输出面 | pass | 逐日两拍留痕连续且带 pid |
| SSOT 真源 | pass | 节点契约+机生 schtasks_facts 双证齐 |
| 代码模块 | pass | ps1 实存实核，无 pid 锁设计自洽 |
| 门禁约束 | warn | 拉起成功≠可交易：登录腿无人接（🌑-1），失败语义只到留痕为止 |
| 自动化触发 | warn | 双拍在案，但资源画像漏拍（window_expr 未抽双时点）+12:55 第二拍是否升门内复检是 D13-09 留裁分歧落点 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无 G 节点；本格是 **D13-09 就绪门 C1 腿的现行替身**（地图 note：watchdog 查 XtItClient 与 paper-session 拉起前查 XtMiniQmt 双替身且进程名分裂）。
- gap_refs 空。
- 建议：①登录腿（人做）纳入值班清单并留痕；②资源画像补双时点 window_expr 口径；③D13-09 施工波落门时裁定本格 12:55 第二拍是否升为门内复检（benchmark:C2 分歧的具体落点，地图显式留裁未擅加拒准入出边）。
