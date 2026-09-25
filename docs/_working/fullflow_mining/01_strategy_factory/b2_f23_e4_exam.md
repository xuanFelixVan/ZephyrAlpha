---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F23 E4 考试咽喉——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F23 · E4 考试咽喉（全厂唯一判定权）

> 组 SF·策略工厂供给链 B 后半册 1/7。上游 F22（考卷件）/F06 幸存者配方，下游 F24（及格集去重）。
> 环节真源：config/strategy_production_map.yaml FAC-E4（build_status: built，本组唯一 built 级考试件）。

## 一、环节定义与边界

一句话：IS 2020-2023 冻结窗+冻结土规成本（2.5bp+10bp+5bp）→DSR 批内折减（N=全局试验账本+本批）→OOS 新考卷→双窗及格线；运动员不兼任裁判，考试权只在此咽喉。
供料方：E3 构造（translated/c4_*.py 考卷件）、F06 网格（f06_survivors.csv 幸存者配方）、车道 E 分布预测件（MOD-BT-194 双标准考尺）。消费方：E5 及格集（bothwin）、C6 管线（c4_batch_completed 事件→intake）。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | ①translated/c4_*.py 考卷件 91 文件（含 c4_fact_* 工厂公式轨 6 件）；②data/strategy_intake/f06_survivors.csv 幸存者配方（1 行=38b453ca3683）；③E4 依赖行情 c1_market.kline_daily_hfq/stk_limit/kline_index（c4_batch_screen.py:333 数据清单） |
| 下游消费 | ①c1_backtest.strategy_screen 台账（1341 行/574 uniq，2026-09-25 实测 `strategy_screen_query.py summary`）；②c4_batch_completed 轻事件→zephyr.strategy_pipeline.intake run_intake_auto（pipeline_events.py:996）；③E4 档案 data/backtest_artifacts/runs/SCR-C4-*＋E4-F06-38b453ca/ |
| 自动化触发 | 无计划任务。半自动链：c4_batch_due=HEAVY kind 只经显式 drain（pipeline_events.py:143 `HEAVY_KINDS`；handler=子进程跑 `c4_batch_screen.py --auto-only --defer-emit`，:374-393）；IS 落账钩子发 c4_batch_completed（c4_batch_screen.py:226 `_emit_pipeline_hook`）；S3 知识生效日哨兵预检（:285-290） |
| 真源与注册表 | 图节点 FAC-E4；MOD-BT-039（注册真源）；执行件 MOD-BT-076 c4_batch_screen / MOD-BT-211 f06_e4_wfa_exam / MOD-BT-IBT-REEXAM 成本门重考 / MOD-BT-194 分布预测考尺；DSR N 真源=MOD-BT-200 TrialLedger（src/zephyr/backtest/core/n_trial_ledger.py）；判定管线=run_strategy_validation＋DecisionGate＋OverfittingDetector（f06_e4_wfa_exam.py:5-6 依赖声明） |
| 门禁与质量尺 | IS 窗冻结（股票/指数 2020-01-01..2023-12-31，ETF 声明短窗）；DSR 折减分母=全局累计 N+本批（N 账本缺失 fail-closed，c4_batch_screen.py:135-145）；RB-STATS-01 证据充分性闸（N_eff 未 verified 或过拟合三维未评满⇒禁判通过，f06_e4_wfa_exam.py:26-28）；OOS/IS<0.70 P0-9 线；成本门五档滑点单调+全档存活+E7 换手≤8x（config/exam_scale_cost_gate.yaml 冻结档）；落库未确认=RuntimeError fail-closed（c4_batch_screen.py:410-411） |
| 当前运行状态 | **绿（人工批考常态运行）+黄（自动批考链半开）**。证据：①`strategy_screen_query.py bothwin`→tested=85, passed=16（含 FACT-4b200528 等 5 件工厂公式轨件）；②f06_survivors.csv 完整三阶段考记录：exam_status=`E4_full_FAIL(OOS/IS=0.499<0.70 + OOS精确DSR 0.3046/0.0027<0.5, can_deploy=False)`——判定权真实咬人（幸存者也被刷）；③E4-F06-38b453ca 档案在盘；④**红点**：.runtime/strategy_pipeline/pending_events.jsonl 滞留 2 条 c4_batch_due（2026-09-16，85 件+1 件，attempts=0，9 天未 drain）→详见 B_后半断点清单 BP-3 |

## 三、子模块清单（两源交叉：注册表+ls/grep 实测）

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| MOD-BT-076 c4_batch_screen | translated 全量批测+落账（IS 冻结批/`--auto-only` 增量/`--auto-oos-pending` OOS 复测批/`--defer-emit` 双窗编排） | scripts/backtest/c4_batch_screen.py:238 main | built（生产跑过多批：C4-translated-20260912 冻结批+BACKLOG2/3 子集批+OOS 批在 summary 实测） |
| MOD-BT-211 f06_e4_wfa_exam | F06 幸存者配方三阶段正考（IS→8 折 WFA→OOS；判定零重写全委托既有管线） | scripts/backtest/f06_e4_wfa_exam.py | built（E4-F06-38b453ca 档案+survivors 判定列为证） |
| MOD-BT-IBT-REEXAM exam_cost_reexam | E4 存活池成本门重考（批C 照妖镜 4440 必拦/批D 新鲜窗；产 cost_qualified_list.yaml） | scripts/backtest/exam_cost_reexam.py | built（门判定 tests/backtest/test_exam_cost_gate.py） |
| MOD-BT-194 distribution_forecast_eval | 分布预测件 E4 双标准考尺（PIT+锐度+pinball，车道 E/Kronos 通用） | scripts/backtest/distribution_forecast_eval.py | built（登记在图 FAC-E3 algo_note_extra） |
| MOD-BT-200 TrialLedger | 全局试验 N 账本（DSR 折减分母；落库即 sync_screen_counts 回填，c4_batch_screen.py:415-417） | src/zephyr/backtest/core/n_trial_ledger.py | built |
| run_strategy_validation/DecisionGate/OverfittingDetector | 判定管线三件（f06 考只编排不重写） | src/zephyr/backtest/core/strategy_validation_pipeline.py 等 | built（tests/backtest/test_f06_e4_wfa_exam.py 25 用例钉死三线裁决） |
| c1_backtest.strategy_screen | 考试成绩+判定书台账（只增，幂等四键判重） | schemas categories/backtest | built（1341 行实测） |

## 四、堵点与病灶

1. **c4_batch_due 滞留 9 天**（现象=2 事件 attempts=0；根因=HEAVY kind 无显式 drain 授权者，月度审计只扫描+告警；修法=断点清单 BP-3，Owner 派工一次 `pipeline_events drain --allow-heavy`；工作量=分钟级；本车道可修=是，但属运行操作非代码）。
2. **双器两口径**：f06 三阶段正考 vs c4 双窗及格，及格语义不同（三阶段全过 vs IS>0∧decay<0.5），DSR 同源但门槛不同——判定权 technically 唯一（同用 run_strategy_validation），输出契约不同表（f06_survivors.csv vs strategy_screen）。修法：F06 判定行回写 strategy_screen 或 E5 消费面扩 f06 表（断点清单 BP-4）。
3. **E4a/E4b 拆分（开放决策点 7）**：免回测快筛 AlphaEval 式五维未裁——图上原样挂着，不阻断主链。待裁级。
4. **OOS 终点=上个周六**（c4_batch_screen.py:218-223）：随时间推移新数据持续进考卷=持续 OOS，与"冻结考卷"语义有张力；现有知识漂移哨兵+S3 声明制兜底。观察项非阻断。

## 五、提速与合并机会

- c4_batch_due 一旦 drain，`--auto-only` 幂等增量只考新件，85 件清单中已考件自动跳（四键判重）——drain 成本≈增量成本，无重复算力。
- 翻译件积压扫描（pipeline_events.py:1130-1133）与 c4_batch_due 事件可合并为一班（现已是同一 light drain 内）。
- exam_cost_reexam 与 c4 OOS 批共用 _c4_engine 口径，可合并跑窗（同 build(start,end) 一次出权重两用）。

## 六、自审闸三态

**挖干可施工**。六向双源实证齐（图节点+脚本头+台账行数+bothwin 实跑）；built 判定成立；堵点 1 有根因+修法；断点归 B_后半断点清单（BP-3/BP-4）。E4a/E4b 拆分遗留=待裁级单列，不影响本环节施工。

## 七、复核命令（10 分钟）

```bash
export PATH="/c/Users/$USER/AppData/Local/Programs/Python/Python312:$PATH"
python scripts/backtest/strategy_screen_query.py summary   # 台账批次/行数
python scripts/backtest/strategy_screen_query.py bothwin   # 双窗及格集 16
head -2 data/strategy_intake/f06_survivors.csv             # F06 三阶段判定列
tail -c 2000 .runtime/strategy_pipeline/pending_events.jsonl  # 滞留重事件
sed -n '1,40p' scripts/backtest/c4_batch_screen.py          # 幂等/冻结窗契约
```
