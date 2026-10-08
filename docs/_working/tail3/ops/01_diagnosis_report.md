---
created: 2026-10-08
session: st-t3c-ops
ttl: task_bound
completes_when: 裁定③（低峰窗重启调度器+排查 10-05 后停跑因）闭环——停跑因根因+逐日证据链定案、低峰窗处置（含三快照取证）归档、09-30 补跑窗处置建议移交 16:05 复核
---

# 停跑因诊断报告 — ZephyrAlpha_PostSettlement（车道C st-t3c-ops）

> 裁定原文（Owner 已批）：「③复市前低峰窗重启调度器+排查 10-05 后停跑因；①若 10-08 复核仍三连败→QMT 人工拉起观察一周（不自启），09-30 净值补跑在 QMT 在线窗」
> 诊断时刻：2026-10-08 03:14~03:50（复市首日凌晨低峰窗）。诊断人与取证 sid=st-t3c-ops。

## 1. 结论速览

- **任务现态：已启用（Enabled）+就绪（Ready），触发链健康，无需重启。** 下次触发=今日（10-08，复市首日）15:30；上次运行=10-07 15:30、结果 0，且该次是**真实 python 执行**（日志尾块为 10-07 15:30 写入，非假绿）。
- **「10-05 后停跑」根因=两层叠加，均非新伤、均已被他队修复或属运维域，本车道零代码修复：**
  1. **调度触发链断（已修复，证据在 HEAD）**：scripts 拆簇 `a4b503a163`（10-02 20:11）把 `register_post_settlement_task.ps1` 移入 `scripts/tasks/register/`（深三级），ps1 内 `Join-Path '..'` 只上跳两级 → logPath/cliPath 挂错 → cmd 重定向打不开 → **python 从未拉起、LastTaskResult=0 假绿**（=「09-30 起日终结算+净值腿双双零执行」根因）。修复=源码 `a67d6922588`（已在 HEAD，`git merge-base --is-ancestor` 实证）+运行态任务已被他批按正确路径重注册（本报告 §4 独立复核证实）。ps1 内 FIX 注释自述：「FIX 2026-10-05/07 … Re-applied 10-07 after a battlefield reset wiped the first fix」——与任务 XML StartBoundary=`2026-10-05T15:30:00+08:00` 完全吻合。
  2. **QMT 券商腿离线（运维域，未修，待 16:05 复核窗）**：09-29、09-30、10-07 三个结算日 QMT 连接三连败（各 3 次重试全败）→ 对账 SKIPPED + **净值腿整步不跑**（脚本 INVARIANTS 明文：broker 离线则净值腿整步不跑）。DB 实证：`c1_market.account_nav_daily` 全表仅 1 行（trade_date=2026-09-28），**09-29/09-30 净值行缺失**。当前（10-08 03:14）`tasklist` 零 xt/QMT 进程 → QMT 离线，按裁定 09-30 补跑**不在凌晨执行**，移交 16:05 复核窗。
- **10-05/10-06 两触发日无输出成因**：10-05 15:30 触发点主机关机（`LastBootUpTime=2026-10-05 16:05:20`，开机晚于触发 35 分钟）；10-06 触发日落在「战场重置抹掉第一遍修复」窗内（ps1 FIX 注释自述），任务定义失效无输出。

## 2. 调度器宿主形态与现态（挖矿①③向）

- 宿主=Windows 计划任务 `\ZephyrAlpha_PostSettlement`（schtasks，非服务非常驻进程）。
- 现态快照（02_pre_restart_snapshot.md 全文存档）：
  - 模式=就绪；计划任务状态=**已启用**；上次运行=2026/10/7 15:30:00；上次结果=0；下次运行=2026/10/8 15:30:00。
  - 触发=每周 MON~FRI 15:30；StartBoundary=2026-10-05T15:30（=10-05 首次修复重注册日）；StartWhenAvailable=true（错过点开机补跑）；MultipleInstances=IgnoreNew；ExecutionTimeLimit=30min。
  - Action 已正位（独立核验，非转录他队结论）：`conhost --headless -- cmd /c cd /d D:\ZephyrAlpha && <Python312>python.exe -u D:\ZephyrAlpha\scripts\run_post_settlement.py >> D:\ZephyrAlpha\data\runtime\post_settlement_last_run.log 2>&1`。三要素存在性核验全过：python.exe（`C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe`）、CLI 真身（`scripts/run_post_settlement.py` 在 scripts 根）、日志路径（`data/runtime/`）。
- **处置判定：任务已 Enabled+Ready 且触发链健康（他队已修+本报告独立复核），按裁定意图「取证『已是健康态』即达成」，不重复仪式性重启；遵守禁 /RUN（非交易时段跑了空转）；零任务定义改动（语义等价零 diff）。**

## 3. 逐日证据链（挖矿④⑥向，日志=data/runtime/post_settlement_last_run.log）

| 日期 | 证据（日志行级锚） | 判定 |
|---|---|---|
| 09-24 | 块×3（L2-L20 等）：结算日 2026-09-24，「MiniQMT 券商连接成功」（L6） | 人工试跑×3，QMT 在线，成功 |
| 09-28 | 块（L62-L80）：连接成功（L66）exit 0；DB 唯一一行 nav=2026-09-28（data_source=miniqmt_sim，ingest 09-29 09:07 +08:00） | 成功且净值腿落库 |
| 09-29 | 块（L82-L102）：「连接重试 1/3、2/3、3/3: 连接返回错误码: 连接失败」（L86-88）→「QMT 模拟盘不可用——降级」（L97）reconcile=SKIPPED exit 0 | **三连败第 1 败**；watchdog 当日 08:45/12:55 仍报进程在（qmt_watchdog.log L30-31）→进程在≠登录会话在 |
| 09-30 | 块（L104-L124）：同款三连重试失败（L108-110）、SKIPPED（L119） | **三连败第 2 败**；净值腿未跑（DB 无 09-30 行） |
| 10-01~10-04 | 日志零新块；休市期（国庆 10-01~10-07） | 触发链坏窗内（拆簇伤 09-30 起），无输出 |
| 10-05 | 主机 15:30 关机：`LastBootUpTime=2026-10-05 16:05:20`（晚于触发 35 分钟）；ps1 FIX 注释「FIX 2026-10-05/07 … first fix」+StartBoundary=10-05T15:30 | 触发点错过；当日人工首轮修复+重注册。日志块⑤（L125-L146，结算日回推=09-30）写入时刻不可精确归日（日志无时间戳+计划任务事件通道零事件），候选=当日 16:05 开机 StartWhenAvailable 补跑或人工——**不影响根因结论** |
| 10-06 | ps1 FIX 注释自述「battlefield reset wiped the first fix」（重置发生在首修与 10-07 重申之间） | 修复被抹→任务定义失效，无输出 |
| 10-07 | 日志 mtime=10-07 15:30；尾块=块⑥（L125-L146）：三连重试失败（L130-132）SKIPPED（L141）exit 0；schtasks LastRunTime=10-7 15:30 result=0 | **三连败第 3 败**（QMT 域）；**调度域=真实执行**（python 真跑并追加日志——与「假绿」期本质区别）；ps1「Re-applied 10-07」+源码修复 a67d6922588 落 HEAD |
| 10-08（今日） | 03:14 tasklist 零 xt/QMT 进程；下次触发=今日 15:30 | QMT 仍离线→补跑移交 16:05 复核窗；15:30 调度将真实结算 2026-10-08（脚本缺省=最近交易日回推含今天，10-08 为交易日） |

## 4. 他队修复面交叉验证（挖矿②向，车道G 结论核对）

- 车道G 10-07 结论「触发链已修复·净值腿待窗」——**核实成立**，本报告补充行级证据：
  - 源码防复发：`a67d6922588`（st-vm12final-20261007-chief D批3/4）改 `Resolve-Path(Join-Path '..\..\..')`，`git merge-base --is-ancestor a67d6922588 HEAD`=YES。
  - 运行态：本报告 §2 独立复核 Action 三要素正位+10-07 15:30 真实执行。
  - 伤因上游：`a4b503a163`（st-construct-20261002 batch2-C1，10-02 20:11）scripts 拆簇移动 register_*×32；`337784b5044` 此前给脚本挂日终托管腿（净值腿 GAP-F-29 接线=9034ea09b76）。
- 净值腿「待窗」亦有 DB 物证：`c1_market.account_nav_daily` FINAL 全表 1 行（09-28），09-29/09-30 缺失（2026-10-08 03:40 reader 通道实测，脚本见 .runtime/tmp/tail3/ops_tmp/query_nav_reader.py）。

## 5. 是否需代码修复——判定：**否**

- 触发链：修复已在 HEAD（源码）+运行态正位（XML/文件存在性/真实执行三证），无残留缺陷可修。
- QMT 腿：非代码缺陷（脚本降级语义正确——QMT 离线→SKIPPED+显式标注+净值腿不跑+exit 0，INVARIANTS 如实）；属运维动作，归 16:05 复核窗按裁定分支（在线→补跑 09-30；仍败→升级呈报，QMT 人工拉起=Owner 明令禁止本车道自行操作）。
- 本车道仓库面零修改（产出全部落 docs/_working/tail3/ops/ 取证件面）。

## 6. 证据锚索引

- schtasks 三快照：本目录 02/03/04 三件（02 采集于 2026-10-08 03:24:58 +0800）。
- 运行日志：`data/runtime/post_settlement_last_run.log`（mtime 2026-10-07 15:30；六块行级锚见 §3）。
- QMT watchdog：`data/runtime/qmt_watchdog.log`（止于 10-02 12:55；09-29/09-30 进程在 L30-33）。
- QMT 终端路径：`data/runtime/qmt_terminal_path.txt`（E:\国金证券QMT交易端\bin.x64\XtItClient.exe；结算走 mini 模拟端 E:\国金QMT交易端模拟\userdata_mini）。
- reaper 无关性：`data/runtime/reaper_kill.log` grep XtItClient/miniQMT/xtquant=零命中（QMT 非被 reap）。
- git：a4b503a163（伤）、a67d6922588（修，HEAD 祖先）、9034ea09b76/337784b5044（净值腿/托管腿）。
- DB：`c1_market.account_nav_daily` FINAL count=1（09-28 行），reader 通道只读（zephyr.infrastructure.database_service，readonly=1）。
- 计划任务事件历史：Microsoft-Windows-TaskScheduler/Operational 通道零事件（Get-WinEvent 实测「找不到任何与指定的选择条件匹配的事件」）——已查无，不作为证据缺口（mtime+LastRunTime+ps1 注释三角互证足够）。

## 7. 残留不确定与移交项

1. 日志块⑤（09-30 结算）精确写入时刻不可考（日志无时间戳+事件通道未启用）——两候选已列 §3/10-05 行；对根因与处置无影响。
2. 09-29 净值行同样缺失（裁定仅点名 09-30）——已在移交项注记，由 16:05 复核窗/总包定夺是否一并补。
3. 16:05 复核窗处置建议（移交总包）：QMT 在线→`python scripts/run_post_settlement.py 2026-09-30`（幂等，ReplacingMergeTree 同键替换，净值腿预期 +1 行）；仍败→升级呈报件（QMT 人工拉起观察一周，不自启）。
