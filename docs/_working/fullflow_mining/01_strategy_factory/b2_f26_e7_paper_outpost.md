---
ttl: task_bound
session: st-ailayer-fullflow-sf-b
title: F26 E7 模拟盘前哨（missing 缺位件）——六向台账与三态结论（SF-B 后半）
date: 2026-09-25
status: mined
---

# F26 · E7 模拟盘前哨（图上 missing，施工缺位）

> 组 SF·策略工厂供给链 B 后半册 4/7。上游 F25（registry 幸存者），下游 F27（组装资金分配）/F72（模拟盘四件，PR 组域）。
> 环节真源：config/strategy_production_map.yaml FAC-E7——module_ref: null，build_status: pending，store_refs 落点待定。**本组 P0 断链点**。

## 一、环节定义与边界

一句话（图上原文）：registry 幸存者以 live 数据跑模拟盘 N 周，逐日对账预测 vs 实际（分布校准的实盘版）+滑点/容量实测；行业统计回测夸大实盘盈亏 30-60%，此门不可跳；不达标退回 E6 标 decayed；对应 lifecycle_status=sim/paper。
边界澄清：本环节≠模拟盘基础设施（sim_* 家族已建成），缺的是**"registry sim 策略清单→逐日前哨考核→判定回写"这一段专用闭环**。与 PR 组 F72 分工：E7=准入前哨（考核期），F72=转正汇总（Owner 门），共用 sim_pocket 账本面。

## 二、六向台账

| 向 | 实证 |
|----|------|
| 上游输入 | 应有：strategy_registry.yaml lifecycle_status=sim 名单（**现状仅 1 条**=lane_e_quantile_baseline MOD-BT-084，且非经自动链入册）；实有替代面：sim_daily_runner e4-replay 消费 strategy_screen verdict=oos_tested+translated 考卷件（绕开 registry） |
| 下游消费 | 应有：E7 判定→FSM sim→shelved（机制在 lifecycle_fsm.py 合法边已注册）或回 E6 标 decayed（**判定器缺位**）；F27 StrategyBook 策略书（等 E7 幸存者名单） |
| 自动化触发 | 邻接面已接线：pipeline_events SIM_DAILY_KINDS FIFO（sim_ledger_daily→sim_observe_daily→sim_journal_daily→attribution_daily，daily_kline 族唤醒+marker 幂等，last_audit 09-24 全绿）；计划任务 ZephyrAlpha_SimBridgeExecute 注册在案且 Ready（schtasks 实测下次运行 2026-09-25 09:35——M5 册 09-24"静默断链嫌疑"已复现为在岗） |
| 真源与注册表 | 图节点 FAC-E7（module_ref=null）；方法论底座=机构四道门共识 R4+QuantConnect 对账框架+Perold 1988 IS 分解（图 design_refs）；data_refs 指向 c1_market.realtime_snapshot/c1_market.execution_report——**两表 DDL 真身在 schemas/categories/intraday/market_realtime_snapshot.py 与 market_execution_report.py（实测存在）** |
| 门禁与质量尺 | 应有：N 周考核期+逐日对账容差+滑点/容量实测档+E7→E6 判退线——全部未注册（图上 store_refs 待定；config/ 无 E7 考核参数档）。邻接面已有：sim_paper_ledger 成本模型（BUY 2.5bp+5bp/SELL 2.5bp+10bp+5bp）、sim_deviation_report"当时说 vs 实际走"偏差账、丁线桥单风控闸 R-H5E-1（裁定 #338⑤） |
| 当前运行状态 | **红（缺位确认）+邻接黄**。缺位证据：module_ref=null/pending/store_refs 待定；registry sim 策略 1 条且其分位数基线无逐日模拟盘考核记录。邻接面运行证据：e4-replay 观察平面首夜跑通（17:31 实证修正 FIFO 次序的记录在 pipeline_events.py:147 注释）；sim 家族日链 marker 09-24 全绿；attribution_daily 09-24 00:43 跑通 |

## 三、子模块清单（缺位件 vs 邻接建成件逐一）

| 模块 | 是什么 | 入口 | 状态 |
|------|--------|------|------|
| **E7 前哨考核器** | registry sim 名单→逐日跑+对账+期末判定 | **无**（全仓 grep 无 registry sim 消费驱动器） | **missing（本环节缺位本体）** |
| **E7 判定回写件** | N 周期满→FSM sim→shelved / 回 E6 decayed | 无（FSM 边在、判定器无） | **missing** |
| **E7 对账报告落点** | 前哨对账报告 store_refs | 图上"待定（E7 施工时定）" | **missing（需裁定）** |
| sim_daily_runner MOD-BT-222 | 模拟盘日链执行体（plan-bridge/plan-execute/bridge-execute/e4-replay/report/settle 六子命令） | scripts/backtest/sim_daily_runner.py | built——但 e4-replay=**观察平面**（mode=sim_observe，名义本金 100 万，收盘价口径，不占分配链额度），非 registry 策略考核 |
| sim_paper_ledger | 纸面钱包+成交账本（成本口径真源） | scripts/backtest/sim_paper_ledger.py | built（intake sim 流转后 emit sim_wallet_due 开户——因 E6 零生产运行，管道从未开过户） |
| sim_deviation_report MOD-BT-? | 预测 vs 实际偏差月账 | scripts/backtest/sim_deviation_report.py | built（E7"逐日对账"可复用其口径升频） |
| lifecycle_fsm MOD-BT-188 | sim 态+sim→shelved 合法边 | src/zephyr/strategy_pipeline/lifecycle_fsm.py | built（判定触发方缺） |
| realtime_snapshot/execution_report DDL | E7 data_refs 两表 | schemas/categories/intraday/ | DDL 真身在（实表数据到达率未核——M1/M7 域） |

## 四、堵点与病灶（=施工前置病灶）

1. 缺位本体=清单前 3 行：无消费 registry 的考核器/判定器/落点——图上登记态，施工零起步。
2. **sim 策略池空心**：E7 建成也无米下锅（registry sim 仅 1 件且非管道产物）——前置依赖 E6 自动链投产（BP-5）或 Owner 手工入册。
3. **两平面语义差**：e4-replay（收盘价、观察平面）与图上 E7（滑点/容量实测、真行情对账）口径不同——施工时须裁定 e4-replay 是否升格为 E7 底座（复用判定台账 c1_backtest.sim_daily_report）另开实测档，还是平行新建。
4. M5 册 SimBridgeExecute 断链嫌疑：本次 schtasks 实测任务在岗 Ready（09-25 09:35 下次运行）——嫌疑降级为"当日未触发一次"待 M7/PR 组取证，不阻断 E7 前置清单。

## 五、提速与合并机会

- E7 对账器=复用 sim_deviation_report 口径+sim_daily_runner 判定台账，勿新建平行账本（净零铁律）。
- E7 期末判定复用 lifecycle_fsm 合法边+promotion_advisory 的三条件回落实据范式（{ok,reason,source} 三件套）。

## 六、自审闸三态

**挖干（缺位件定性完成+施工前置清单齐）**。missing 判定属实：module_ref=null 且全仓无考核器实件；邻接建成面（sim_* 家族 8 件+FSM 边+DDL）已盘清，差什么、要建成需要什么逐条=见 B_后半断点清单 §B-E7 八项。施工归总筹派工（建议与 PR 组 F72 联合立项，共用账本面）。

## 七、复核命令（10 分钟）

```bash
grep -n "module_ref\|build_status\|store_refs" config/strategy_production_map.yaml | sed -n '20,26p'  # FAC-E7 null/pending/待定
grep -rln "lifecycle_status.*sim" src/zephyr scripts --include="*.py" | grep -v test                 # 无 registry sim 驱动器
python scripts/backtest/sim_daily_runner.py --help 2>&1 | head -20                                   # 六子命令面
cmd //c "schtasks /query /tn ZephyrAlpha_SimBridgeExecute /fo list"                                  # 在岗 Ready
ls schemas/categories/intraday/ | grep -i "snapshot\|execution"                                      # DDL 真身在
```
