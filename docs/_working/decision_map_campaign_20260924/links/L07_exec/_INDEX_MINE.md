---
ttl: task_bound
doc_type: index
title: L07 执行环节深挖总勾表（9 子块 MINE 索引 + 穷尽性声明）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L07
status: 九册全落盘（外部对表已做一轮，部分块标受阻）
---

# L07_exec `_INDEX_MINE` — 本环节深挖总勾表

> 上游骨架=`SKEL.md`（子块树 §1/§2、施工项 §4、标准件 §5 真源，本组册**不重切子块、不重复立项**）；本目录 9 册=SKEL 往下钻一层的正文/数据级实测。
> 方法真源=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` §2/§5/§6（外部论断须 URL+发布方+年份、关键结论 ≥2 独立源、A 股适配闸、"字段在≠数据可得"、禁以现状规模小封矿）。
> 分工纪律：EXE-3 桥实现两缺陷由 LANE-BUILD 在修，本组册**零代码改动、零 git 操作**，只出增量清单与移交项。

## §1 九册状态总勾

| 子块 | 册目录 | 六向 | 正文级实读件数 | 缺口条（本册新立/改判） | P0 | 三态主判 | 外部对表 |
|---|---|---|---|---|---|---|---|
| EXE-1 信号→订单映射 | `s1_signal_to_order/` | 6/6 | 3（runner 五区段 + 映射件 2 篇） | 6 | 0 | 已接电（sim 平面） | 受阻（未取二源，标待办） |
| EXE-2 委托管线 | `s2_order_pipeline/` | 6/6 | 11（ex_core 全族） | 6 | 1 | 混合：主干已接电 / 4 件覆盖未接电 | **已做，4 论断含 2 独立源** |
| EXE-3 QMT 桥客户端 | `s3_qmt_bridge_client/` | 6/6 | 1（1,098 行件 5 个函数族） | 8 | 3 | 已接电（sim 腿，载体已由 LANE-BUILD 复效） | 未做（缺口全为代码直读证据） |
| EXE-4 成交回报链 | `s4_execution_report_chain/` | 6/6 | 3 + CH 实查 3 次 | 7 | 2 | 已接电但**数据面 0 闭合**（表内 1 行） | 未做（结论不依赖外部） |
| EXE-5 成本反馈 L4-14 | `s5_cost_feedback_loop/` | 6/6 | 4（1,819 行三零件 + optimizer） | 7 | 1 | **覆盖未接电（三零件全量 + 自优化器）** | 部分（费率口径未对表，记债） |
| EXE-6 执行算法 | `s6_execution_algorithms/` | 6/6 | 2（1,011 行引擎读 5 个算法族 + helpers + optimizer） | 6 | 1 | **覆盖未接电（ex_sor 全域 manual）** | **已做（AC 双源确证）** |
| EXE-7 滑点标定 | `s7_slippage_calibration/` | 6/6 | 1（501 行常量区+读法）+ 注册表逐字段 | 6 | 2 | 标定=一次性批产出，无再标定调度 | 未做（本册结论全为仓内字段实测） |
| EXE-8 五档与盘口失衡 | `s8_depth_and_imbalance/` | 6/6 | 2 + CH 实查 5 次 + 交易日历 | 6 | 2 | 数据面**已追平** / 执行消费面**零** | 未做（做 T/Cartea 属别车道与 §5 已登记） |
| EXE-9 卖出 + 打板 | `s9_sell_and_daban/` | 6/6 | 2（daban 全件 + 4 件 import 反查） | 6 | 2 | 混合：t1_sellable 已接电 / 其余三件覆盖未接电 | 受阻（四论文可核性未验，记债） |

**合计**：9/9 册落盘｜本组新立缺口 **58 条**（含 3 条对 SKEL/13 号文既有判定的**证伪或改判**）｜其中 **P0 共 14 条**｜**判"覆盖未接电"的子块：EXE-5、EXE-6、EXE-9 三块整块 + EXE-2/EXE-8 两块内 5 件**｜外部对表：2 册确证 + 1 册部分 + 6 册标受阻/未做。

## §2 对上游文档的三条改判（必须回写，否则下游按过期口径排期）

| # | 被改判的原判定 | 本组实测结论 | 出处册 |
|---|---|---|---|
| R1 | SKEL §2 EXE-1⑥ / 13 号文环节④缺陷 2："映射表 Owner 未批=语义空间仅批 1 行" | **证伪**：真源是 `01_ruling_plan_mapping_and_orphans.md` 表一（AI 受托自裁，6 行全裁，与代码逐行一致）；proposal 批复栏全空是**未归档的旧提案件**。新真实缺口=裁定未归 `ruling_registry`（grep 计数 0） | s1 |
| R2 | SKEL §2 EXE-8⑥ / data-sufficiency L5 行："tick_depth_5 1,883 万行、D36 差约 17 交易日" | **过期**：实测 103,493,839 行、覆盖 2026-07-24~09-24，而 09-25/09-26 非交易日（`is_trading_day` 实测）→ **缺口=0，D36 收尾分量应摘除** | s8 |
| R3 | SKEL §2 EXE-4⑤："断点 E4 闭合于 09-23 批" | **仅代码闭合**：表内 FINAL=1 行且停在 09-18，09-23 三合同未落表；该行还是 `slippage_bps=-10000.0` 毒值 → E4 应改判"半闭（生产端在、数据未回补、语义有毒）" | s4 |

## §3 跨块串成的三条主线结论（单册看不到的）

1. **"闸在而不作用"是一个族，不是三起孤立事故**：EXE-2 价格笼子（桥路径恒 UNKNOWN）→ EXE-6 参与率 5%（只校验输入参数不回算时刻表）→ EXE-9 SaR>2% 削量（η 量级使触发需下单量>可见买量 10 倍，且空盘口时整段跳过）→ EXE-5 三零件接了也无数据。四者的共同形状=**声明合规 + 无闭环校验 + 无静默计数**。建议总指挥把 4 条 P0 并一个"闸有效性自证"施工批（真源：s2 C-GATE-01、s6 G3、s9 G1、s5 G1）。
2. **反馈环缺的不是那条 selector→scorer 边，是数据平面**：execution_report 表 1 行（含毒值）→ 三零件历史全内存 → `ExecutionParamOptimizer` 因 tca_reader 未注入而 fail-closed → L07-C02 单独施工会接出一条"永不带载"的边（比断链更坏，因为看着是通的）。**顺序必为：EXE-4 语义修 → 落库位点 → 接读者 → 接 selector**（真源：s4 G1、s5 G1、s5 G2）。
3. **五档原料与执行链之间是一根没接的管子**：CH 里 1.03 亿行五档（已追平），但 `MarketContext` 与 `PretradeQuote` 都只有一档 → 参与率闭环（s6）、冲击腿进执行侧（s7）、盘口时机信号（s8）三块 P0 卡在同一字段缺席上；单独立项 **L07-S8-G2** 为共同前置（真源：s8 G2、s6 G3、s7 G1）。

## §4 本环节穷尽性声明

**已扫过的源（本组 9 册覆盖）**：
`scripts/backtest/sim_daily_runner.py`（五区段正文）· `docs/_working/sim_launch/`（proposal + 裁定卡全文）· `src/zephyr/ex_core/`（order_manager / pre_execution_checker / price_cage / fill_handler / async_fill_dispatcher / order_execution_saga / open_order_resolver / cancel_rate_guard / position_reconciler / local_order_queue / execution_report_producer / execution_report / execution_param_optimizer / daban_execution / adapters/qmt_file_bridge_broker 五函数族 / adapters/miniqmt_broker 笼子段 / rules/ashare+base）· `src/zephyr/ex_sor/`（core/algo_trading_engine 六算法族 / core/sell_session_router / services 三零件）· `src/zephyr/sell_decision/core/sell_execution_planner` · `src/zephyr/position/core/`（t1_sellable / intraday_position_constraint）· `src/zephyr/pf_core/orderbook_imbalance_strategy.py` · `src/zephyr/backtest/core/cost_model_calibration.py` 常量区+读法 · `config/.../cost_model_registry.yaml` CST-ASTOCK-001 逐字段 · `schemas/categories/intraday/market_execution_report.py` · 契约三件比对 · `scripts/` 生产包装器 6 支（run_sim_pipeline_daily / run_sim_bridge_execute_daily / run_l06_observe_daily / bridge_monitor_check / diag_tick_data_quality / start_paper_session）· `.runtime/monitor/bridge_monitor_check.txt` 实读 · `config/quarantine/qmt_trade_csv_quarantine_20260622/` 旁证 · CH 只读实查 8 次（execution_report 全表逐行 / tick_depth_5 行数日期标的 / system.parts / system.tables / 交易日历四日）。

**仍剩的长尾（明列，不假装挖尽）**：
① **LANE-BUILD 领地主动止手**：`qmt_file_bridge_broker.submit_order/cancel_order/_scan_instruction_states` 逐行、`qmt_file_bridge_integration`、2026-09-08 迁移台账、qmt_e2e_runbook（避免产冲突结论）。
② **正文未逐行**：`execution_engine.py`（`ExecutionEngineRunRecord` 产出路径）、`order_execution_saga.py` 六步实现体、`cancel_rate_guard.py` 解冻条件、`open_order_resolver.py` 决策表实现体、`execution_scheduler/optimal_order_router/sor_agent` 三件、`TwapStrategy` 之外的 Iceberg/POV/ALT 三族实现、`transaction_cost_optimizer` 机会成本段、`slippage_analyzer._attribute` 全式、`sell_session_router/sell_execution_planner` 正文、`calibrate_cost_tier_redblue.py`、`exam_cost_gate.py`、`almgren_chriss_impact_model.estimate_params`、`tick_replay/tick_depth_backfill/ch_auction_derive`、XS-016 blueprint、42/43 号 memo 相关节。
③ **外部对表未完成（受阻项）**：TCA 未成交行口径（业界如何表达 parent 未成交）二源未取；`daban_execution` 所引四篇 arXiv 编号（2607.28323 / 2603.09164 / 2608.02002 / 2608.00988）可核性未验；A 股有效价差/冲击成本实证量级未做外部二源；pre-trade compliance 框架（如美国 SEC Rule 15c3-5 类）权威页未命中；LEAN/hftbacktest 切片调度语义逐项对表未做（§5 已登记为义务）。
④ **越界不掘**：做 T（881xxx/CST-T0-001/B-007）、GPU 侧、T1 备份仓、SSOT 注册表车道在改的 `trading_decision_map.yaml` 增量。

**封矿裁定（本组 9 册一致口径）**：**不封**。9 块均判 MINING（正文级/外部级长尾已具名于上），但每块的六向台账与三态裁定已达"代码行号 + 数据行级"证据强度，**P0×14 无一条被 MINING 阻塞**（README"挖干即开工"条款）。禁以"现状规模小/sim 未爆事故"作封矿或降优先级理由——本组四条最强结论（笼子不作用、回报链零读者、反馈环无数据平面、五档管子没接）恰恰都是"规模小所以没人发现"型。

**保守声明**：本目录全部"通/在产"判定仅限 **sim/纸面语境**；不给任何实盘就绪结论（口径承接 SKEL §6 与 13 号文 §11 baseline 全红）。所有 CH 数字为本班 2026-09-26 单次只读快照，复核命令见各册 §⑥ 日志行。
