---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_16_e9_retro_loop.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-16 复盘回测与归因 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案
- 锚件：TDM C3 层 6 节点（config/trading_decision_map.yaml，layer=C3）+ FACTORY E9 层 9 节点（config/strategy_production_map.yaml，stage=E9 切片核数=9✓）+ REG-EXP-001/REG-BTB-001 双册。
- 已知命题「实盘腿仅 sim 钩子 execution_report 未产」本轮验证：**部分成立需修正**——生产端代码已在（T6b）、sim 桥已可选接线、实盘腿是裁定#338⑤的**故意不接**（Owner 门位）、线上表仅 1 行空转。
- E9 九节点：FAC-E9(stage,partial)｜M-001 绩效归因引擎 MOD-PF-007 built｜M-002 风险归因复用 MOD-RK-16 built｜M-003 模拟盘归因报告(residual 战役) MOD-BT-215 **pending**｜M-004 决策标注数据集 MOD-ML-014 built｜M-005 盈亏计算器 MOD-TRADING-002 built｜M-006 策略迭代升级器 built（b1_source_diff_matrix 在册 8 孤儿实装之一）｜M-007 影子组合对照引擎 built｜M-008 条件胞归因 scripts/backtest/condition_attribution.py built。
- C3 六节点：TDM-F-C3(stage)｜C3-01 多维归因 MOD-PF-007→src/zephyr/pf_core/core/performance_attribution_engine.py｜C3-02 升降级/退役 MOD-L02-013→src/zephyr/factor/governance/lifecycle_state_machine.py｜C3-03 sleeve 调权 MOD-PA-007→src/zephyr/pf_alloc/core/regime_meta_allocator.py｜C3-04 参数校准 MOD-BT-001→src/zephyr/backtest/core/walk_forward.py｜C3-05 可靠度/信号健康 MOD-SIGQC-004→src/zephyr/signal_quality/signal_degradation_monitor.py（5 个 module_ref 路径逐一实存验证✓）。

## §1 六向台账（向/内部反查发现带路径/外部/判定）
| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上游数据源 | c1_market.execution_report（16 列 DDL-as-Code=schemas/categories/intraday/market_execution_report；生产端 src/zephyr/ex_core/execution_report_producer.py 已建，走 zephyr.data.ch_writer）＋c1_market.account_nav_daily（生产端 src/zephyr/position/live_nav_recorder.py 在产） | QuantConnect 对账框架（FAC-E9 design_refs） | nav 腿✅；execution_report 实盘腿🌑（表 1 行） |
| 生产接线 | 接线点 src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:191-198（仅 sim 桥 attach_execution_report_producer，ops_alert_feed 注明"仅 sim"）；attach 挂点 src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:486 自述「未接线=零行为变更，断点E4；env=real 保持现状（裁定#338⑤ Owner 门）」 | — | sim✅；real🌑=Owner 门非工程缺 |
| 下游消费 | 影子组合 src/zephyr/pf_core/core/shadow_portfolio.py:268 from_execution_reports=**内存适配器不自读表**（Iterable 入参），日账管线=FAC-E9 自述"施工单移交"；对账 src/zephyr/position/position_reconciler.py:123 handle_execution_report 头注「无生产消费方（BRK-016 在册断点，待 ex_core 终态事件扇出挂接）」；TCA 契约面 src/zephyr/reporting/default_tca_engine.py:46＋analytics_base.py:50；前端 src/zephyr/frontend/dashboard/api_server.py:1579 仅标签 | Perold 1988 IS 分解（design_refs） | 契约面✅；表读端⬜查无；对账事件入口🔨未挂 |
| 登记面 | REG-EXP-001=docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml：67 实验（regime_validation 4+walk_forward 1+factor_eval 6+无类型 56），**归因/影子专题实验=已查无**（5 个关键词命中皆 regime/walkforward）；REG-BTB-001=docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml：142 对象（untested 123/valid 16/pending 2/verified 1），C3 六卡=BT-P3-038/043/044/045/046/047 **全部 confidence=untested** | MLflow 对标（册头；51 号裁定卸载，FallbackBackend JSON=logs/experiment_tracking_fallback/） | 预注册✅齐全；归因腿回测零执行🌑 |
| 设计真源 | FAC-E9 algo_note：Perold 四分解守恒＋Brinson-Fachler＋Barra 式因子归因；IS 分解决策时间戳已落字段级链（CTR-P1-007 V2 decision_timestamp+codegen+DDL 列+producer 写入点=Order.created_at），**线上表 ALTER 待 CH 迁移窗**；TDM C3 五下游各自决策问句在册 | Brinson-Fachler（neoxam）/IS（quantitativebrokers）design_refs 带 URL | 设计✅齐；库表执行欠🔨 |
| 运行时证据 | scripts/governance/d5_architecture/generators/generate_data_supply_chain_map.py:1614 原话「消费方=SPM:334/380；生产端仅在 qmt_file_bridge_integration 对 sim 桥可选接线…全表 1 行（末次 09-18）」；回归冒烟 scripts/construction/qmt_bridge_regression_smoke.py:64 引 EXECUTION_REPORT_TABLE | — | 归因原料表近乎空转；链路冒烟件在✅ |

## §2 挖干自评
- 已挖干：三源切片核数全对上（C3=6、E9=9）；execution_report 走完「生产端→桥接接线→表→消费端」四段全链定位到文件：行号，命题修正为「生产已在、sim 已接、real 属 Owner 门故意断、表 1 行空转」；C3 六 module_ref 逐一实存；双册（EXP 67/BTB 142）计数与状态分布机生核清。
- 未挖透（点名留档）：M-003 MOD-BT-215 residual 战役内容未展开；供应链地图 SPM:334/380 两消费点未逐行读；EXP 册 56 个无 experiment_type 实验构成未清点；归因→C3-02 升降级→C3-03 调权→C3-04 校准的下游链路只到节点级未到函数级。

## §3 挖后自审闸三态裁定
- **裁定：挂起排期**。
- 理由：真断点（real 腿接线）解锁权在 Owner 门（裁定#338⑤），不可自主施工；可自主两项——①影子组合日账读端管线（c1_market.execution_report→shadow_portfolio.from_execution_reports＋持久化表）已有施工单移交在途，属 B2 车道量级；②C3 六卡回测在 REG-BTB-001 排 P3，须排队非本簿时间盒可毕。本环节无「查无即封矿」对象：所有查无（表读端、归因专题实验）都有明确上游依赖，封了会砍断闭环。
- 解锁条件：①Owner 裁定实盘账户启用→real 腿接线；②CH 线上表 ALTER 迁移窗开启→decision_timestamp 落库；③日账管线施工单被领取落地→E9 stage 可议 partial→built。

## §4 挖矿日志
- R1（图+册切片）：python 解析 strategy_production_map/trading_decision_map/experiment_registry/backtest_backlog 四源，核数 C3=6✓ E9=9✓；得 C3 六卡全 untested、EXP 册归因专题实验已查无。
- R2（全链反查）：grep execution_report 全仓 26 文件→producer 头注（T6b 自述「全仓零生产调用方」已被后续接线工作部分推翻，头注滞后）→qmt_file_bridge_integration.py:191 接线点→broker:486 断点E4/裁定#338⑤→shadow_portfolio.py:268 适配器→position_reconciler.py BRK-016→供应链地图:1614 运行时原话。命题闭环，消费面挖明：契约面 3 家、表读端 0 家。
