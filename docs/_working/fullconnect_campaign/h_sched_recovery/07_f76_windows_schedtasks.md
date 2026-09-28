---
ttl: task_bound
title: F76 Windows 计划任务群（sch_* 族 49+ 实体）——L08 复飞矿道案卷·任务全景日清
session: zc-l08-20260927
---

# F76 · Windows 计划任务群

> 总册行：I 段 F76，状态 built，P1，96 实体（resource_profile_registry 口径）。M0=S1。
> 本卷=09-27 复飞复测。基册=m5_scheduling/01_windows_schedtasks.md（09-25 全景实测）。本卷主责=**任务全列当日复核+N/A 态清理候选点名+M5 名册漂移**。

## 一、六向台账（实证锚点，09-27 06:5x schtasks 全查）

| 向 | 内容 |
|----|------|
| 上游输入 | 26 支 register_*.ps1+历史手工注册；OS Task Scheduler（点火不保证成败=单点哑发射，M5 横断 1） |
| 下游消费 | 全链（守护族/交易链/数据链/资源族/备份族——分卷见 08/09/10/11/12 及 m5 各册） |
| 自动化触发 | 今日实扫 **50 项项目相关任务**（ZephyrAlpha* 47+tilib_indicator_backfill_nightly+RestartMiniQmt+ZEPHYR-RESTORE-DRILL）；Running 5（BeltDaemon 已转 Ready、CHHealthProbe/DataScheduler/TickSubscriber/WorktreeDriftWatchdog/AI-Wrapper-Inject/OllamaServe）；Disabled 8（RestartMiniQmt/C4Exam_Full0916/C4Exam_OneShot0915/FactoryLaneC_Full0916/FactoryLaneC_OneShot0915/TradingWatchdog/WeeklyRest + NightlySentiment **已转 Ready 启用**） |
| 真源与注册表 | config/resource_profile_registry.yaml（机生，09-27 实读 **total_entities=99**，generated_at 2026-09-26T22:21Z）；schedule.yaml=槽位真源（25 槽，03 册） |
| 门禁与质量尺 | 注册脚本 in-place Set-ScheduledTask 铁律；QMT 族保 Interactive（改 S4U/SYSTEM 即失明）；注册脚本↔live 漂移=横断病 5（S1 活雷在案） |
| 当前运行状态 | **绿为主带三红点**：tilib 夜回填 exit 1（09-27 02:30，S2 活病维持）；GateFullTreeAudit exit 1（09-27 03:30，S6 语义内嫌疑）；F06Grid exit 1（09-26 23:00）；其余当日班次全 0 |

## 二、子模块三级枚举（09-27 全列，五族）

1. **守护/常驻族（8）**：BeltDaemon（PT1M，09-27 Ready result 0）、DataScheduler/TickSubscriber/CHHealthProbe（PT5M 三卫士，Running）、DeadmanSwitch（PT5M，0）、ProcessReaper（PT10M，0）、WorktreeDriftWatchdog（PT5M，Running）、AI-Wrapper-Inject（PT1M，Running 0）。
2. **盘中/交易链（6）**：QMTWatchdog（09-26 12:55 result 1=周末语义）、RestartMiniQmt（禁用）、PaperSession（0）、SimBridgeExecute（0）、PostSettlement（09-25 15:30 result 0）、TradingWatchdog（禁用）。
3. **数据/盘后链（7）**：BoardIndexRealtime（0）、SectorSnapshot（0）、IntradayFundFlow（0）、IndexMinuteEOD（0）、AltFxECB（0）、tilib 夜回填（**1**）、NightlySentiment（**复活：09-26 22:30 result 0，M5 时点为禁用+0x80070002**）。
4. **资源/治理伴生族（16）**：Resource 五件（SamplerScan 0/RegenCheck **3 语义内**/Writeback 0/ViewPublish 0/MorningReport 0）、MeasureCalibration（0）、ConfigCheck（0，09-26）、GateFullTreeAudit（**1**）、TTLRejudgeDaily（0）、PatternMining（0）、C4Exam（0）、FactoryLaneC（0）、F06Grid（**1**）、C4Exam/FactoryLaneC 各两枚一次性（禁用）、**DecisionChainSentinel（新，daily 09:40，pythonw decision_chain_sentinel.py，0）**。
5. **备份/恢复/一次性族（13）**：DailyBackup（0）、WeeklyVMBackup（0）、CH-OptimizeMerge-Weekly（0）、LibraryLedgerBackup（0）、LibraryLedgerDrill+ZEPHYR-RESTORE-DRILL（**267011 从未跑，10-01 首火**）、IOCheck-Monthly（0）、OllamaServe（Running）、RSSHub、TraeCacheCleanup、WeeklyRest（禁用）、**EvaporationBlackbox（新，PT5M，cmd→evaporation_blackbox.py，Running 但 LastTaskResult=2147946720=0x800710E0 僵尸码嫌疑）**。

**N/A 态清理候选（一次性 schtasks，Owner 门，schtasks 写禁——今日清单 §2.5 挂起维持）**：C4Exam_Full0916（曾 267014 超时被杀）、C4Exam_OneShot0915、FactoryLaneC_Full0916、FactoryLaneC_OneShot0915、TraeCacheCleanup（库外脚本）、RSSHub/OllamaServe（一次性形态辨析）、RestartMiniQmt/TradingWatchdog/WeeklyRest（禁用三席去留裁定）。

## 三、接线四态独立复核

- 总册 built → **维持 built**（全列 50 项皆有主人、有触发、有当日/近班 LastRun）。
- **骨架勘误**：①总册 F76"96 实体"→ 画像册 09-25 实测 98、09-27 实测 **99**（持续漂移，机生册禁手改，随 RegenCheck 自愈）；②**NightlySentiment 状态反转无登记**：M5 名册"禁用+0x80070002 裸路径"，09-27 实测 Ready+result 0（22:30 fire）——"DISABLED→Ready 转换无登记"第二例（第一例=PaperSession，PR-A 在案）；③**两枚新任务未入册**：DecisionChainSentinel/EvaporationBlackbox 均为 M5 名册（09-25）后新增，resource 画像册 99 实体或已含，但 M5 任务全表无此二席；④任务计数对不上：M5 名册 49→今日 50，净差 +1 与"新增 2"并存=名册侧对不上 1 席（列待裁）。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | EvaporationBlackbox Running+0x800710E0（S10 同款僵尸码） | 取证该任务注册者与语义；保活链是否双实例冲突 | **P0**（新任务带病） |
| 2 | PostSettlement 注册脚本坏形态（bc76efe3bf 回退）活雷 | revert action 块（与 03 卷缺口 5 同案） | **P0** |
| 3 | tilib 夜回填 exit 1 常态化（S2） | bat 落仓内 logs+night_probe 正名入 scripts/data | P1 |
| 4 | N/A 一次性任务 6-9 席清理 | Owner 门（schtasks 写禁） | P1 |
| 5 | NightlySentiment 复活无登记+两新任务未入 M5 名册 | M5 名册刷新（生成器化=红线 §9.5 方向） | P2 |
| 6 | 名册 49 vs 50 净差 1 席对不上 | 逐席对账（M5 全表 vs 本卷五族清单） | 待裁 |
| 7 | 报警疲劳（1/3 常态化码不分） | S6 方案分码+晨报消费（归 M3） | P2 |
| STALE 13/假绿 5 | **不属 F76**（tasks.yaml 数据管线腿，归 F77 §四） | — | — |

## 五、自审闸三态

**挖干（全列复核）**：50 席全列当日四态（State/LastRun/LastResult/NextRun）活探+五族归位+M5 名册逐项对照；开口=净差 1 席与两新任务语义（登记待裁/缺口 1）。三态=**维持 built，名册漂移 4 条勘误**。

## 六、复跑命令

```bash
powershell -NoProfile -Command 'Get-ScheduledTask | ? {$_.TaskName -match "Zephyr|tilib|RestartMiniQmt|ZEPHYR"} | % { $i=$_|Get-ScheduledTaskInfo; "{0}|{1}|{2}|{3}|{4}" -f $_.TaskName,$_.State,$i.LastRunTime,$i.LastTaskResult,$i.NextRunTime }' | tee /tmp/schtasks_$(date +%Y%m%d).txt | wc -l   # 50
powershell -NoProfile -Command '(Get-ScheduledTask -TaskName "ZephyrAlpha_EvaporationBlackbox").Actions | fl Execute,Arguments'
grep -m2 "total_entities\|generated_at" config/resource_profile_registry.yaml   # 99 / 09-26
git show bc76efe3bf -- scripts/register_post_settlement_task.ps1 | head -40     # S1 活雷
```
