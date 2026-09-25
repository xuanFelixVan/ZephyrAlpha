---
ttl: task_bound
session: st-ailayer-fullflow-pr-a
creation_token: fullflow-pra-f72-paper-four-pieces-20260925
title: F72 模拟盘日跑四件——六向台账+SimBridge 断链取证专节
date: 2026-09-25
status: 挖干
---

# F72 模拟盘日跑四件（PaperSession 日跑 / 平台四件 / 对账验证）

> 挖矿代理 PR-A（组 PR·模拟盘→转正链）。引用 M2 车道 `m2_backtest_sim/03_sim_daily.md` 已挖干结论不重挖，本册只补该册未覆盖的：①计划任务盘面取证 ②CH 四表实跑行数 ③SimBridge 断链一日与 st-cleanup-final 窗口修复的对照专节。

## 一、环节定义与边界

- **一句话**：入库策略与观察档的模拟盘实弹日跑链——PaperSession 常驻会话 + 平台四件产出（判定台账/成交流水/钱包快照/平台日刊）+ 对账验证（settle T+1 回填、以券商为准重建、月度偏离报告），行业实证回测夸大实盘 30-60%，此门不可跳。
- **上游**：F25（E6 入库幸存者→sim 流转）/ F70（模拟撮合与偏差件）/ 丁线 judgment_daily_plan（只读）。
- **下游**：F73（联赛 equity 原料=sim_pocket_daily 按组拉取）、F74（promotion_combo_gate 消费 sim_pocket_daily/sim_trade_log + promotion_advisories）。
- **红线**：模拟盘四禁在岗（M2 册门禁向全文引用）；本册挖矿零实跑、零桥触碰。

## 二、六向台账

| 向 | 内容（实证锚点） |
|----|------------------|
| 上游输入 | 丁线 judgment_daily_plan/judgment_intraday_market_state（只读消费，sim_daily_runner 头 DEPENDENCIES）；E4 观察档 translated/c4_* 翻译件（e4-replay 重放原料）；QMT 大桥文件镜像 E:\qmt_bridge_sim PositionStatics（HANDOFF_20260921 §1）；柜台实际持仓（rebuild_from_broker） |
| 下游消费 | c1_backtest.sim_daily_report/sim_trade_log/sim_pocket_daily/sim_platform_journal（四件本体）；league_monthly_snapshot.py（sim_pocket_daily 按组 equity）；promotion_combo_gate.py:11-12（纸面账本消费）；sim_deviation_report（回测↔模拟滑点校准，IBT-H02 分母）；pf_alloc SIM_DAILY 事件（M2 07 册） |
| 自动化触发 | ①ZephyrAlpha_PaperSession 日 09:25（09-24 LastResult=0，NextRun 09-25 09:25，schtasks 实测）②ZephyrAlpha_SimBridgeExecute 双火点 09:35/13:05（StartBoundary 2026-09-23，见专节）③SIM_DAILY_KINDS FIFO 事件链 sim_ledger_daily→sim_observe_daily→sim_journal_daily→attribution_daily（pipeline_events.py:140,147；17:31 首跑实证注释在源）④run_post_settlement 挂 _run_sim_journal_step 收盘定稿档（fb5a7821d7f 批）⑤promotion_advisory_due 事件预埋+处理器已注册（pipeline_events.py:175；sim_governance.py:134 有流转建议时 emit）——事件传动非死 cron，合宪法 §9.3 |
| 真源与注册表 | M2 册 03_sim_daily.md（日链四向真源）；scripts/backtest/sim_daily_runner.py（MOD-BT-222，INVARIANTS=判定/结算分离+丁域只读+方案C 收盘价+零伪造+幂等）；config/paper_hedge.yaml；docs/_working/automation/campaign/mining/08_模拟盘转正门/工段作业簿.md（设计面）；HANDOFF_20260921_ab_league.md（件1 交接令） |
| 门禁与质量尺 | 四禁正典+三道锁（pre_execution_checker fail-closed/live_simulation_switcher 一次性令牌/qmt_file_bridge_integration enable_real=False 默认）；R-H5E-1 盘前门注入（裁定#338-5）；bridge-execute 幂等=signal_batch=plan-bridge-\<day\>+orders_sim.csv idem-key 同日重跑不双下单；env="sim" ONLY（真账户=Owner 门）；M10/M11 豁免注记在源（20s 有界等待轮询/CLI 接电先例） |
| 当前运行状态 | **三绿一黄一空**：PaperSession 绿（09-24 09:25 fire exit 0，保活至 15:05 优雅收场 exit 0；holdings=1 cash=9995827.86 rebuild_from_broker 以券商为准）；四件平台表绿（CH reader 实测：sim_daily_report **193 行** max report_date=09-23；sim_trade_log **68 行** max=09-24；sim_pocket_daily **267 行**；sim_platform_journal **15 行**）；SimBridge 黄（09-24 断链一日，修复已落 HEAD，复验窗口=09-25 09:35 首火，见专节）；月度链空（sim_deviation_report/sim_attribution_report/sim_promotion_memo 三 CH 表不存在=产出器在、从未跑） |

## 三、子模块清单（两源交叉：ls + BLUEPRINT 头 + 盘面/CH 实测）

| # | 件 | 是什么 / 入口 | 状态 |
|---|----|---------------|------|
| 1 | scripts/backtest/sim_daily_runner.py | 日链接电执行体，六子命令 plan-bridge/plan-execute/bridge-execute/e4-replay/report/settle（:36-58 用法契约定死） | built 绿（判定台账 193 行实跑） |
| 2 | scripts/backtest/sim_paper_ledger.py | 纸面账本（与方案C 同成本模型，乐观偏差由偏离报告单列监督） | built（28KB，09-22 批） |
| 3 | scripts/backtest/sim_platform_journal.py | 平台日刊+健康三检（expected_fresh_date 复用方） | built（journal 15 行） |
| 4 | scripts/start_paper_session.py | --service 装配 LiveStrategyAdapter；slot_id=paper-keepalive（:504/:602-603），空 strategy=保活槽，事件驱动调仓 universe=0 | built 绿 |
| 5 | src/zephyr/ex_core/live_strategy_adapter.py | MOD-L06-001 多 slot 监督（异常隔离 FAILED 不扩散/退避重启上限 3 次熔断 EXHAUSTED/业务心跳原子写）；只编排不重造，无下单路径 | built 绿（09-24 日志 slots_running=1→收场 0） |
| 6 | scripts/start_paper_session_daily.ps1 + register_paper_session_task.ps1 | PaperSession 包装（is_trading_day fail-closed SKIP+QMT 进程探活）与注册器 | built 绿（09-23 02:28 在盘） |
| 7 | scripts/run_sim_bridge_execute_daily.ps1 + register_sim_bridge_execute_task.ps1 | SimBridge 包装（交易日闸/XtItClient 活性 SKIP 防死桥写单/PS5.1 stderr cmd /c 路由）与注册器（09:35+13:05 双触发） | built 新落（27449507e1c，09-24 23:08；复验待首火） |
| 8 | scripts/backtest/qmt_bridge_regression_smoke.py | QMT 桥回归冒烟（385 行，同终批落地，ab15cfb3 补翻译册） | built |
| 9 | scripts/backtest/sim_governance.py | 月度治理编排+S12 C4 promotion_advisory_due 事件发射（:134） | built（advisory 侧零流量，见 F74/PR-B） |
| 10 | sim_deviation_report.py / sim_attribution_report.py / sim_promotion_memo.py | 月度三产出器（脚本在 scripts/backtest/ 实存） | **登记态**：对应 CH 三表不存在=零运行 |
| 11 | tests/backtest/test_sim_daily_runner.py | MODIFY-GUARD 测试锚 | 在盘（construction 批"全电池 107×2 零豁免"） |

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 归属 |
|---|------|------|----------|------|
| 1 | SimBridgeExecute 09-24 全日断链（两火点 0xFFFD0000 零日志） | 包装 ps1 仅存于未提交工作区（M7 结案：09-23 首单来自丢失的工作区副本），主区裸奔 | **已修**：终批 27449507e1c 落 HEAD+盘面同步；余下=首火复验（见专节） | 本车道（验证）/提交链（已毕） |
| 2 | 破产底线未武装 | bankruptcy_floor_initial_capital 未注入（paper_session.log WARNING；35 号文 §4.10 static 腿缺席），仅 trailing peak 回撤口径生效 | 装配方注入模拟钱包本金常量（fail-visible 不猜默认） | EX/风控车道 |
| 3 | LEVEL_3 逃生链缺生产者 | systemic_input_provider+rollback_metrics_provider 未接线（日志 [RISK] 行明示"已登记 tracker"），仓位上限/熔断/对账/启动恢复四链已生效 | 市场级进料口生产者立项（涉风控分级，Owner 知会） | M7 风控域 |
| 4 | 月度链整链零运行 | 三产出器 manual CLI（M11 先例）无排产无消费方；deviation 缺位=IBT-H02 滑点校准闭环零样本（M2 册已记跨车道移交） | 与 F73 月度快照同批入 schedule.yaml 月槽（一次排产两链受益） | 本车道+SC 调度 |
| 5 | 进攻姿态订单映射=提案态 | PLAN_ACTION_POSTURE 已扩+plan-execute 实弹验证（28b85901bf：SIM-PLAN-001 建仓 65,055 股 510300@4.608，不追高闸过），参数标注"提案可修，Owner 否决删字典键即回 no-op" | Owner 对映射表逐行点头后冻结 | Owner 门位（晨报列单） |
| 6 | scripts/backtest/ 残留 3 个 sim_daily_runner.py.tmp.21732.* | safe_write_text 崩溃残留（PID 21732 会话痕迹） | 他会话在途勿代管，只登记；卫生批统一清 | 提交链/卫生批 |
| 7 | 事件日志取证盲区 | Task Scheduler operational 通道 09-24 窗口查无 SimBridge 记录（通道未开或已滚动）——LastResult 是唯一残证 | M5 S3 修法维持：通道开启+ps1 文件级旁落日志双保险 | M5/SC 车道 |

## 五、提速与合并机会

1. 四件+月度三件共用 sim_daily_runner 单 CLI 单表族——无重复件，引用即可。
2. 两个包装 ps1（PaperSession/SimBridgeExecute）同构（is_trading_day 探针+PythonExe 回退+Write-Log 样板）：可提公共 ps1 函数库；净零对价=退役两份重复样板。低优先（各 80 行内，收益有限）。
3. 堵点 4 与 F73 月度快照排产合并成一张月槽工单（见 02 册提速节）。

## 六、自审闸三态

- **六向实证完整性**：上游（文件+表）/下游（消费方 file:line）/触发（schtasks 双任务实测+事件链源码行）/真源（MOD-BT-222+M2 册）/门禁（四禁三锁+幂等）/运行（CH 四表行数+任务 exit 码+日志收场）——每向≥2 源。
- **开口项**：SimBridge 修复后首火（09-25 09:35）未到=复验未闭合，但不改变"断链已治本"的判定（文件在 HEAD+盘面零 diff+注册器一致）。
- **三态结论**：**挖干可施工**。

## 附：SimBridge 断链取证要点（M5-S3/M7-S3 线索接续 · st-cleanup-final 修复后现状对照）

**时间线（全部 git/schtasks/日志实测）**

| 时点 | 事件 | 证据 |
|------|------|------|
| 09-22 15:17 | fb5a7821d7f 落 sim_daily_runner（bridge-execute 子命令入库；死信批次重提交） | git log |
| 09-23 | st-sim-launch-20260923 注册 ZephyrAlpha_SimBridgeExecute（触发器 StartBoundary 09-23T09:35/13:05）；包装 ps1 **不在 git 史**，仅存在于未提交工作区（lane_ff 重建件） | Get-ScheduledTaskTrigger；git log 该 ps1 当日为空 |
| 09-23 13:05:07 | 首班跑通：exit_code=0，"honest no-order row"（posture=flat/action=none/in_window=true/quote age 1.9s）——首单来自丢失的未提交工作区（M7 S3 结案） | .runtime/logs/sim_bridge_execute.log 末段 |
| 09-24 09:35+13:05 | 两班全败：包装日志零新增，LastTaskResult=4294770688（0xFFFD0000，powershell -File 目标缺失级非标码）→ **断链一日，桥活饲养员死**（M5 原判读成立） | Get-ScheduledTaskInfo；日志停 09-23 |
| 09-24 23:08 | **修复落 HEAD**：27449507e1c 终批窄批（包装 ps1 80 行+注册器 60 行+回归冒烟 385 行+两份战役报告），GW 标=q-20260924-st-sim-launch-20260923-0007——经 st-cleanup-final 台账战役窗口的队列正门落地（cleanup_ledger 台账⑦行终态 faaa1390b26、终批 e9ec884201f 同窗在案） | git show --stat |
| 09-25 00:30 | 两 ps1 盘面物化，`git diff HEAD` 零差=盘面与 HEAD 一致 | ls mtime+git diff |
| 09-25 09:35 | **修复后首火（挖矿时未到）——唯一开口项** | NextRunTime 实测 |

**现状对照表**

| 维度 | 09-24（断链日） | 现在（09-25 挖矿时） |
|------|----------------|---------------------|
| 包装 ps1 git 史 | 不存在（M7："提交史中从未存在"） | 27449507e1c 在 HEAD（dev 可达） |
| 主区盘面文件 | 缺失（点火即 0xFFFD0000） | 在盘且=HEAD（diff 空） |
| 计划任务 | Ready 但每火必败 | Ready，双触发器 Enabled，NumberOfMissedRuns=0 |
| 注册器↔live 任务漂移 | 无法判定（注册器也不在史） | register 脚本=HEAD 与任务一致，无 M5-S1 同款 bc76efe3bf 回退证据（该回退只打 PostSettlement） |
| lane_ff 重建件 | 未提交蒸发风险（总筹 §四补警示"他会话在途勿代管"） | 已入库，四个 lane_ff worktree 对 sim 件 status 干净 |
| 桥执行子命令 | runner 侧 09-22 已在 HEAD | 不变 |

**残余风险**：①首火复验前本链不翻绿（探活：`Get-ScheduledTaskInfo ZephyrAlpha_SimBridgeExecute` LastTaskResult 应=0，且 sim_bridge_execute.log 应新增 `bridge-execute day=2026-09-25 exited: exit_code=0`）；②事件日志通道盲区未治（通道级归 M5/S3）；③注册脚本重注册回退病（M5 横断模式 5）对本件的免疫力来自"注册器在 git 史"，已结构性改善。

## 七、复核命令（10 分钟口径）

```bash
# 1. 双任务盘面
powershell -NoProfile -Command "Get-ScheduledTaskInfo -TaskName ZephyrAlpha_PaperSession,ZephyrAlpha_SimBridgeExecute | fl TaskName,LastRunTime,LastTaskResult,NextRunTime"
# 2. 包装器盘面=HEAD
git diff HEAD --stat -- scripts/run_sim_bridge_execute_daily.ps1 scripts/register_sim_bridge_execute_task.ps1   # 空=一致
git log --oneline -1 27449507e1c   # 修复 commit
# 3. 日志收场
tail -3 .runtime/logs/paper_session.log ; tail -3 .runtime/logs/sim_bridge_execute.log
# 4. 四件表行数（DatabaseService reader；禁裸 connect）
python -c "import sys;sys.path.insert(0,'src');from zephyr.infrastructure.database_service import get_db_service as g;ds=g();c=ds.get_clickhouse_conn(role='reader');print([c.execute(f'SELECT count(),max(report_date) FROM c1_backtest.{t}') for t in ['sim_daily_report','sim_trade_log','sim_pocket_daily','sim_platform_journal']]);ds.close_all()"
# 5. 引用不重挖
sed -n '1,60p' docs/_working/fullflow_mining/m2_backtest_sim/03_sim_daily.md
```
