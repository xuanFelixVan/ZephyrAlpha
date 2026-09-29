---
ttl: task_bound
title: F72 模拟盘日跑四件（PaperSession/平台四件/对账验证/SimBridge）——L08 复飞矿道案卷·断链嫌疑取证
session: zc-l08-20260927
updated: 2026-09-29
---

# F72 · 模拟盘日跑四件

> 总册行：H 段 F72，状态 partial（SimBridge 09-24 静默断链嫌疑，M5 在案），P0。M0=B7 交叉。
> 本卷=09-27 复飞复测。基册=03_promotion_ab/01_paper_four_pieces.md（PR-A 09-25 挖干，引用不重挖）；今日清单 §1.4 列 F72 为 partial（SimBridge 静默断链嫌疑）→ **本日实测该嫌疑已解除，partial 理由更新**（见骨架勘误）。

## 一、六向台账（实证锚点，09-27 活探）

| 向 | 内容 |
|----|------|
| 上游输入 | F25 幸存者→sim 流转/F70 成本模型复用/丁线 judgment_daily_plan 只读/QMT 桥文件镜像+柜台 rebuild_from_broker（PR-A 册 §二） |
| 下游消费 | CH 四表 c1_backtest.sim_daily_report/sim_trade_log/sim_pocket_daily/sim_platform_journal；F73 联赛 equity 原料；F74 combo gate 纸面账本消费（promotion_combo_gate.py:11-12） |
| 自动化触发 | 09-27 schtasks 实测：`ZephyrAlpha_PaperSession` Ready，LastRun **09-26 09:25:01 result=0**（周末 SKIP，日志 09-25/09-26 两行 SKIP 实证），NextRun 09-27 09:25；`ZephyrAlpha_SimBridgeExecute` Ready，LastRun **09-26 13:05:01 result=0**，NextRun 09-27 09:35；事件链 SIM_DAILY_KINDS FIFO（pipeline_events.py:140,147）+promotion_advisory_due 预埋（:175） **〔过时标记 2026-09-29：09-28/29 两交易日已跑完，bridge-execute 执行腿已落地并出现 exit 0 正常行，见卷末刷新批注〕** |
| 真源与注册表 | scripts/backtest/sim_daily_runner.py（MOD-BT-222 六子命令）；scripts/run_sim_bridge_execute_daily.ps1+register（27449507e1c 落 HEAD）；paper_hedge.yaml；M2 03_sim_daily.md 日链真源 |
| 门禁与质量尺 | 四禁三锁（pre_execution_checker fail-closed/live_simulation_switcher 一次性令牌/enable_real=False 默认）；bridge-execute 幂等（signal_batch=plan-bridge-\<day\>）；env="sim" ONLY；交易日闸 fail-closed SKIP |
| 当前运行状态 | **四绿一待**：PaperSession 绿、SimBridge 包装层绿（09-25/09-26 四火全 SKIP exit 正常，日志实读）、四件平台表绿（PR-A 09-25 实测 193/68/267/15 行）、PostSettlement 绿（09-25 15:30 result=0 实测）；**待=首个真实交易日全链实弹**（09-25 中秋+09-26/27 周末连续三非交易日，复飞窗后移） |

## 二、子模块三级枚举（调度面，09-27 实扫）

1. **任务面**：PaperSession（Daily 09:25，powershell -Hidden，交易日闸+QMT 活体闸）；SimBridgeExecute（Daily 09:35+13:05 双火点）；PostSettlement（Weekly 一~五 15:30，conhost --headless 好形态）；QMTWatchdog（08:45/12:55，09-26 12:55 result=1=周末 QMT 不在语义内）。
2. **代码面**：sim_daily_runner.py（plan-bridge/plan-execute/bridge-execute/e4-replay/report/settle）；start_paper_session.py --service（slot_id=paper-keepalive）；live_strategy_adapter.py（MOD-L06-001 多 slot 监督）；sim_paper_ledger/sim_platform_journal/sim_governance；月度三产出器 sim_deviation_report/sim_attribution_report/sim_promotion_memo（登记态，CH 三表不存在=零运行）。
3. **日志/账面**：.runtime/logs/sim_bridge_execute.log（09-27 tail 实读：末 4 行=09-25/09-26 四班 SKIP non-trading day）；paper_session.log（09-24 收场 exit 0+周末 SKIP）；残留 tmp 件 scripts/backtest/*.tmp.21732.*（PR-A 登记，他会话在途勿代管）。

## 三、接线四态独立复核（SimBridge 断链嫌疑取证=本卷主责）

**09-24 断链一日（历史，PR-A/M5-S3 定案）** → **09-27 取证：嫌疑解除，修复存活四证**：
1. LastTaskResult=0（09-26 13:05:01，schtasks 实测）——对比断链日 4294770688。
2. 包装日志恢复追加：09-25 09:35:10/13:05:08、09-26 09:35:06/13:05:06 四行 SKIP（日志 tail 实读）——包装 ps1 活着且交易日闸工作。
3. 盘面=HEAD：27449507e1c（09-24 23:08 修复批）在史；PR-A 09-25 00:30 已验 git diff 零差。
4. 触发器双火点 Enabled、NumberOfMissedRuns=0（PR-A 实测维持）。
- **残余开口**：SKIP≠实弹。首个真实交易日（09-28 周一）09:35/13:05 两班须复验 exit 0+bridge-execute 正常行，F72 方可讨论翻 built 方向。**〔过时标记 2026-09-29：探活结果已出但非全绿——09-28 首班 exit_code=2（时序），09-29 13:05 班 exit_code=0 正常行已现，见卷末刷新批注〕**
- **骨架勘误**：今日清单 §1.4/总册 F72 标 partial 的理由"SimBridge 09-24 静默断链**嫌疑**"——09-27 实测嫌疑已解除（修复存活+包装层四班绿），partial 维持但理由应改写为"月度三产出器零运行+破产底线未武装+LEVEL_3 逃生链缺生产者+处女链待首个交易日实弹"（PR-A 堵点 2/3/4 维持）。

## 四、缺口清单

| # | 现象 | 处置 | 优先 |
|---|------|------|------|
| 1 | 首个真实交易日实弹未复验（09-28 09:35 首班）**〔09-29 探活已出：exit 0 正常行现，带单实弹仍未生，见刷新批注〕** | 探活=sim_bridge_execute.log 新增 `bridge-execute day=2026-09-28 exited: exit_code=0` | **P0**（复飞收口件） |
| 2 | 破产底线未武装（bankruptcy_floor 未注入，仅 trailing peak 口径） | 装配方注入模拟钱包本金常量 fail-visible | P1 |
| 3 | LEVEL_3 逃生链缺生产者（systemic_input/rollback_metrics 未接线） | 市场级进料口立项（风控分级，Owner 知会） | P1 |
| 4 | 月度链整链零运行（三产出器无排产，CH 三表不存在） | 与 F73 月槽同批排产（08/05 卷合并工单） | P1 |
| 5 | PostSettlement 注册脚本坏形态回退（M5-S1，bc76efe3bf）**〔09-28 K袋 461a86be17 落形态探测器，见刷新批注〕** | revert action 块 10 行；重注册即复断风险未除 | **P0**（活雷） |
| 6 | 事件日志通道盲区（Task Scheduler operational 通道查无记录） | 通道开启+ps1 文件级旁落日志 | P2 |
| 7 | 进攻姿态订单映射=提案态待 Owner 冻结 | Owner 门位（晨报列单） | P2 |
| STALE 13/假绿 5 | **不属 F72**（数据管线腿，归 F77 §四） | — | — |

## 五、自审闸三态

**挖干（复核维持+嫌疑解除实证）**：PR-A 基册六向全证引用+本卷四项当日活探（双任务码/双日志/NextRun/PostSettlement）。开口项=真实交易日实弹（自然时间）。三态=**partial 维持，断链嫌疑条款关闭**。**〔过时标记 2026-09-29：执行腿子命令落地+两交易日探活已出，刷新见卷末批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核＋日志/任务活体现读。

- **翻面/推进 commit**：`dd3b17f9fd`（09-28 15:05，F56 断腿重建）——`sim_daily_runner.py` **bridge-execute 子命令落地**（+308 行+tests 327 行），卷 §二 代码面所列六子命令自此名实相符（此前 F56 卷实证该子命令从未存在）。
- **实弹探活结果（.runtime/logs/sim_bridge_execute.log 现读，缺口1 P0 判定）**：
  - 09-28 13:05 班：`exit_code=2`（argparse invalid choice——子命令 15:05 才落，**时序性错过首班**，一次性历史行）；
  - 09-29 09:35 班：SKIP（XtItClient not running，终端离线）；
  - **09-29 13:05:23 班：`bridge-execute day=2026-09-29 exited: exit_code=0`（honest orders_file_missing 无单行）——卷内探活达标行已出现**；
  - **余量**：订单文件缺=无单可执行，"带真实订单的全链实弹"仍未发生；翻 built 方向的讨论仍以此为前置。
- **缺口5（PostSettlement 活雷）→ 有护网未拆雷**：`461a86be17`（09-28，K袋）落 **PostSettlement 注册脚本形态探测器**（`tests/trading/test_register_post_settlement_task_form.py` 89 行）——"重注册即复断"风险有机器探测防线；revert action 块本体未动，活雷定性维持。
- **缺口状态修订**：缺口1 P0→探活达标行已现、带单实弹余量｜缺口2/3/4/6/7 维持｜缺口5 P0→探测器护网已落、revert 未动。
- **自审闸三态（刷新后）**：**partial（维持；开口从"自然时间"转为"带单实弹+破产底线等五堵点"）**——卷内缺口1 探活处方已完成历史使命，判读口径以本批注为准。
- **复跑**：`tail -6 .runtime/logs/sim_bridge_execute.log`（09-28 exit_code=2/09-29 exit_code=0 两行）｜`python scripts/backtest/sim_daily_runner.py bridge-execute --help`（子命令在）｜`git show 461a86be17 --stat`。

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
powershell -NoProfile -Command "Get-ScheduledTaskInfo -TaskName ZephyrAlpha_PaperSession,ZephyrAlpha_SimBridgeExecute,ZephyrAlpha_PostSettlement | fl TaskName,LastRunTime,LastTaskResult,NextRunTime"
tail -6 .runtime/logs/sim_bridge_execute.log; tail -4 .runtime/logs/paper_session.log
git log --oneline -1 27449507e1c
git diff HEAD --stat -- scripts/run_sim_bridge_execute_daily.ps1   # 空=一致
# 09-28 收口探活：tail 应新增 bridge-execute day=2026-09-28 exited: exit_code=0
```
