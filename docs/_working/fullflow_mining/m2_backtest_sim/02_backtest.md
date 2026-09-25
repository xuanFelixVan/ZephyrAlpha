---
ttl: task_bound
volume: 02_backtest
session: st-commitspeed-tbl-20260924
---

# 02 · 回测脚本面（scripts/backtest/ 核心演练与出证链）

## 一、环节定义与边界
回测域的演练/复核/挂图/出证脚本族：同输入复现演练（replay_drill）、危机演练（crisis_drill）、策略转正自动挂图（auto_mount）、EXP 因子 IC 出证（eval_exp_expectations）、联赛与转正门（league_*/promotion_combo_gate）、C4 翻译引擎（translated/_c4_engine.py）。上游=数据链（CH 只读）+run_archive；下游=考试门（05 册）/GPU 矩阵（04 册）/模拟盘（03 册）。**禁实跑重型回测，本册全部 grep/头注取证。**

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | CH 真库（kline_daily_hfq/stock_indicator/regime_snapshot_history，经 table_registry/ch_reader）；run_archive（VAL-* run 目录）；strategy_class 映射表 |
| 下游消费 | replay_drill→run 目录 08_replay.md（只增不改）；auto_mount→决策地图（文本手术+only-add）；eval_exp_expectations→factor_registry FCT-EXP 族晋级证据+experiment_registry EXP-FACTOR-EVAL-*；league/promotion→Owner 月度终审材料 |
| 自动化触发 | 全族 CLI 手动/批次决策点触发（各件 M11 豁免注记在：replay_drill/crisis --due 月频门控/eval 晋级批次）；crisis_drill 月频接线只调 --due 判定"不做新计划任务"（crisis_drill_monthly.py 头注） |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_backtest/blueprint.md（MOD-BT-001/090/222/033 等实锚）；协议=TDMAP-001/IBT-PROTOCOL-V1；成本=CST-ASTOCK-001 |
| 门禁与质量尺 | tests/backtest/ 119 件（实测计数）；replay 四件套一致判定（exit 0/1/2 语义）；auto_mount 38 规则校验+SLE-3 守卫（test_auto_mount_sle3.py） |
| 当前运行状态 | **绿**（代码+测试面在位，historic 首跑均有案）；运行频率低（按批次手动） |

## 三、子模块清单（10 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 2.1 | 复现演练（SOP-D §8）：锁 meta→重跑→diff 四件套（判定/触发数/显著性/判定原因），写 08_replay.md，不一致=暂挂对象结论 | scripts/backtest/replay_drill.py:30-36（语义），ERROR_CONTRACT 行 | 绿 |
| 2.2 | 危机演练月频：四窗（W2015 千股跌停/W2018 贸易战/W2020 疫情/W2024 微盘崩盘）×三口径（逐日净值重放/stress_test_engine 静态 shock/流动性四情景+出场滑点）；全现金降级最近持仓快照，从未持仓出空骨架告警 | crisis_drill_monthly.py:30-58；落盘 data/backtest_artifacts/drills/<run_id>/+marker tmp/crisis_drill_last.json | 绿；测试 test_crisis_drill_monthly.py 在 |
| 2.3 | auto_mount 五步管线：映射表→分状态回测判 activation_state（R2SIX+六段 overlay；SR 单侧 t+BHY-FDR q=10%+OOS 不反向；<30 天不测）→PP-001 配比（only-add 域）→文本手术+38 规则校验→报告 | auto_mount.py:1-40 头注；resolve_six_phase:248；load_phase_panel:262 | 绿（D-3 双写修复后 76 项测试绿，t0 FINAL_REPORT 清单 B 任务③） |
| 2.4 | EXP 一致预期 IC 出证：PIT as-of（publish_date<=trade_date，DS-229/DS-275 双轨）；exp_primary（唯一晋级权，判据禁挪）+exp_r36（降权协议，|t|>3.0 只严不宽）；滑点压力 cfg/20/40/80bp 四档；成本读 MatchingConfig #233 零硬编码 | eval_exp_expectations.py:31-45（INVARIANTS），双协议注记 | 绿；窄口径滑点腿三性质已钉测试（曾整轮崩溃零覆盖，已修） |
| 2.5 | C4 翻译引擎（策略翻译件标准接口 build(start,end)） | scripts/backtest/translated/_c4_engine.py（:416,:451 实测行号）；sim_daily_runner e4-replay 消费 | 绿；pct_change FutureWarning 刷屏未清（见堵点2） |
| 2.6 | 联赛与快照：league_registry/league_monthly_snapshot（equity 序列组内对比，只留档不判胜负，终审=promotion_combo_gate+Owner） | league_monthly_snapshot.py:17-24；裁定#392 | 绿 |
| 2.7 | 转正组合门：promotion_combo_gate（sim 绩效+strategy_screen+E4 成绩+纸面账本合成打分；promote_ready≠决定） | promotion_combo_gate.py:15 头注 | 绿 |
| 2.8 | 状态双轨对照：compare_state_dualrun（TDM AGG 切换判据观察工具） | compare_state_dualrun.py:17 | 绿（观察件） |
| 2.9 | 批次筛选/工厂管线：factory_intake_pipeline/c4_batch_screen/strategy_screen_c2/hypothesis_translator/hypothesis_precheck/mcts_expression_search/lane_* 家族（30+ 件） | scripts/backtest/ ls 实测 | 黄：矿道面归 AI 层/搜索轨（04 册 GPU 轨消费它们），本册不展开 |
| 2.10 | run_archive/verify_run_archive：run 目录归档与校验（replay_drill 上游） | scripts/backtest/verify_run_archive.py；src/zephyr/backtest/run_archive.py | 绿 |

## 四、堵点与病灶
1. **编辑器残留 tmp 文件污染脚本目录**（实测 ls）：`factory_grid_executor.py.tmp.21732.*`×2、`sim_daily_runner.py.tmp.21732.*`×3——违反"项目根零临时文件"精神（在 scripts/ 下非根，属灰色）；且 sim_daily_runner 有 3 份 tmp 副本易被误编辑。修法：cleanup 脚本加 `*.py.tmp.*` 清扫。工作量 XS，**本车道可修但零 commit 红线下移交施工班**。
2. **pct_change FutureWarning 刷屏**（grid_t1_20260924.log 实测 19.5 万字节几乎全是该 warning，factory_grid_executor.py:325,:369 + _c4_engine.py:416,:451 四点）——直接劣化 GPU 跑批日志的可观测性（有意义的钳制消息被淹没，是"假绿"判定难的平台性根因）。修法：pct_change(fill_method=None) 四点+warnings.filterwarnings 收敛。工作量 XS，建议 T1 完赛后、T2 发车前修。
3. crisis_drill 口径一为"演练近似口径，非真实交易回放"（:38-40 自注）——诚实披露在案，不算病，但 Owner 读报告时须知。
4. eval_exp_expectations 的 EXP 协议 IS 窗与修复表覆盖边界错位（exp_r36 另立协议处置）——已按预注册纪律处置（禁挪主闸门），无动作。

## 五、提速与合并机会
- replay_drill 与 verify_run_archive + generate_backtest_backlog 三件都绕 run_archive 转，可合一个 `run_archive_cli`（S 工作量，提速=少一次真源切换）。
- league_monthly_snapshot/sim_promotion_memo/sim_deviation_report 三份月报输出三处落点（data/backtest_artifacts/league/、docs/_working/pipeline-research/sim-memos/、月度偏离 JSON）——可合并为单一"模拟盘月报编排器"一命令三产物（03 册联动提速案）。

## 六、自审闸三态
**挖干可施工**。子环节 2.9 矿道面不展开属车道边界声明，非证据缺失。

## 七、复核命令
```bash
sed -n '30,50p' scripts/backtest/replay_drill.py
sed -n '30,60p' scripts/backtest/crisis_drill_monthly.py
grep -n "def resolve_six_phase" scripts/backtest/auto_mount.py
ls scripts/backtest/*.tmp.*    # 残留 5 件实锚
ls tests/backtest | wc -l      # 119
```
