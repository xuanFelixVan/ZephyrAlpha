---
ttl: task_bound
completes_when: Owner 已阅覆盖矩阵与三清单；基建最小方案四件（一库一器一闸一图）挂单或立项；黄灯断点逐条归入既有 backlog 或新立工单。
---

# 交易决策骨架覆盖审计——骨架哪里有电、哪里没电、哪里没线

> 2026-09-16，st-skeletonaudit-20260916。只读盘点，零施工。对格对象=骨架定义（[`2026-09-16-owner-vision-system-mapping.md`](2026-09-16-owner-vision-system-mapping.md) §一：L1-L5 决策层 × T1-T4 时间节拍 × 双态门）与 TDM 全节点（`config/trading_decision_map.yaml`，schema 1.2）。
>
> **审计时点快照声明**：今晚多车道在飞（TDM 与 pf_core 高频变更中）。本文一切状态为 2026-09-16 审计时点快照，重点受 tonight 车道 D/D2 影响：**pf_alloc 五模块链装配体（`allocation_orchestrator`，MOD-PA-030）于今日落地并挂上事件链**——骨架映射文档 §三"L4 有件未接电"的表述在审计时点已部分过时，本文如实更新（裁定#257③ 的挂触发条件"G15→G14 编排件立项"已被车道 D 兑现）。

## 大白话摘要（给 Owner）

**骨架 5 层 × 4 拍 × 双态门的 138 个 TDM 节点全部落格**：23 个已接电、98 个覆盖未接电（零件在、没人每天叫醒它们）、4 个 crypto 空壳、13 个纯结构节点。每层一句话：

- **L1 大盘/周期判定：有电，全仓最强的一层。** 状态+置信度每天自动产出（今天刚接上自动链），喂给纸面分配和回测节流；总闸语义（"今天下不下单/给多少总仓位"）TDM 里已定义。
- **L2 板块轮动：零件全套、没电。** 强度/轮动/龙头/传导/放行门槛 30 个节点模块全在仓库里，没有任何东西每天触发它们；Owner"电风扇行情只买 300ETF"的信噪比门连零件都没有（红灯）。
- **L3 标的选择：链条活着，但只在回测里跑。** 选股主链/否决器/环境开关互调正常，消费面=回测整装，生产日循环无挂点；可交易预检今天刚落地、调用方为零。
- **L4 组合构造：审计时点已部分通电（今日最大变化）。** pf_alloc 预算切分→约束→调权链今天挂上事件链（实验级，纸面盘消费）；但"今天开不开仓"的拍板体与"今日不交易"权仍无人持有，预算切分 TDM 指定模块与生产装配体错位（审计新发现）。
- **L5 执行：下半段通电、上半段没人下单。** 委托管线/价格笼子/订单预检/熔断减抄全是 production 件且路径通，但没有任何日循环产生委托（策略模板缺，BT-P2-055）；执行成本反馈环有在案断链。
- **组织者两件：都不存在。** 周期切换器（T1）散件在（月度调权+状态矩阵配置面+环境开关）、本体缺；日度编排器（T2）有骨架（warroom pipeline）但仓库内零调用方——这就是 Owner"感觉没运作"的机械解释。

## 一、对格标准与方法

1. **骨架层映射**（TDM layer → 骨架层）：L1→SKL1；L2→SKL2；L3→SKL3；C1/C2/C3/P1/P3/S1（卖出信号=调仓单离场腿）/X1（应急保命=组合风控横切）→SKL4；L4（买卖点与执行）/P2（做T）/S2（离场执行）→SKL5；L0→ORG（组织者域）；四流根→ROOT。
2. **节拍映射**：主拍=TDM `point` 字段（盘前→T2 / 盘中→T3 / 盘后→T4 / 持续→横切）；6 个周期配置面节点追加 T1 标签（E-L1、E-L1-AGG、F-C1、F-C3-03、F-C3-04、C-L1）。方法注记：T2 晨判消费的多数信号在 T4 计算（盘后算、盘前用），节拍按**计算时点**落格，跨拍消费链在清单中注明。
3. **双态门**：`node_type=gate` 或节点语义含放行/否决/资格/约束/熔断 → 有；有门形但为评分/联动参数/聚合门槛 → 弱；传感器/信息变换/聚合 → 无。
4. **接电三态判据**：已接电=模块实码存在 **且** 有生产事件链/仪表盘消费实证；覆盖未接电=实码在盘（115/115 module_ref 零缺失）、链内互调活、但无生产日循环触发面或唯一消费方为包导出；缺失=TDM 有节点、代码无实码。判定证据=module_ref 在盘校验 + 调用方 grep（排除测试）+ 模块 MATURITY/STABILITY 头 + tasks.yaml/`pipeline_events` 生产任务面比对。

## 二、覆盖矩阵总表（骨架层 × 节拍 × 电态）

| 骨架层 | 节点数 | T1 | T2 | T3 | T4 | 持续 | 已接电 | 覆盖未接电 | 缺失 | 结构 | 门:有/弱 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 大盘/周期 | 10 | 4 | 9 | 2 | 0 | 1 | 4 | 5 | 1 | 0 | 1/1 |
| L2 板块轮动 | 30 | 0 | 5 | 5 | 18 | 2 | 1 | 28 | 1 | 0 | 1/3 |
| L3 标的选择 | 26 | 0 | 3 | 5 | 18 | 0 | 0 | 25 | 1 | 0 | 3/1 |
| L4 组合构造 | 35 | 2 | 5 | 7 | 5 | 16 | 16 | 15 | 0 | 4 | 8/8 |
| L5 执行/做T | 28 | 0 | 1 | 19 | 2 | 6 | 0 | 27 | 1 | 0 | 4/2 |
| ORG 组织者域(L0) | 5 | 0 | 2 | 2 | 1 | 0 | 2 | 3 | 0 | 0 | 1/0 |
| ROOT 流根 | 4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 0/0 |
| **合计** | **138** | 6 | 25 | 40 | 46 | 30(含跨标) | **23** | **98** | **4** | **13** | 18/15 |

（节拍列含 T1+ 追加标签的重复计；电态列互斥。门=有 19、弱 15、无 104——按全表逐行统计。）

**矩阵判读**：骨架五层的"格子"TDM 全部覆盖（落格率 100%，含 crypto 空壳格子），**没电是主旋律**（98/138=71%）。电的分布极不均匀：L1 与 L4（今日）有真电，L2/L3/L5 是"发电机已到货、没接电缆"，ORG 两件组织者一件零调用、一件不存在。

## 三、全节点落格表（138/138）

> 电判依据为审计时点 grep 实证；module_ref 省略 `src/zephyr/` 前缀。

<!-- COVERAGE-TABLE:BEGIN -->
| 节点 | 骨架层 | 节拍 | 门 | 电 | module_ref | 电判依据 |
|---|---|---|---|---|---|---|
| TDM-E-FLOW | ROOT | 持续 | 无 | 结构 |  | 流根聚合点（red_reason=terminal），纯结构不承载电 |
| TDM-P-FLOW | ROOT | 持续 | 无 | 结构 |  | 流根聚合点（red_reason=terminal），纯结构不承载电 |
| TDM-X-FLOW | ROOT | 持续 | 无 | 结构 |  | 流根聚合点（red_reason=terminal），纯结构不承载电 |
| TDM-F-FLOW | ROOT | 持续 | 无 | 结构 |  | 流根聚合点（red_reason=terminal），纯结构不承载电 |
| TDM-E-L0 | ORG | T2 | 有 | 覆盖未接电 | plan_engine/daily_warroom_pipeline.py | daily_warroom_pipeline 仓库内零调用方（自称挂 57 号日循环 SOP 环节④，无接线实证）；stability=testing |
| TDM-E-L0-01 | ORG | T2 | 无 | 覆盖未接电 | plan_engine/daily_trade_plan.py | daily_trade_plan maturity=testing，仅 execution_deviation_attributor 消费 |
| TDM-E-L0-02 | ORG | T3 | 无 | 已接电 | plan_engine/plan_deviation_monitor.py | plan_deviation_monitor maturity=production，thesis_survival 链活（盘后口径） |
| TDM-E-L0-03 | ORG | T4 | 无 | 已接电 | plan_engine/tomorrow_boundary_planner.py | tomorrow_boundary_planner maturity=production，仪表盘 warroom 组件消费（人工面） |
| TDM-E-L0-04 | ORG | T3 | 无 | 覆盖未接电 | plan_engine/intraday_tomorrow_forecast.py | intraday_tomorrow_forecast 仅 plan_engine 链内消费 |
| TDM-E-L1 | SKL1 | T1+T2 | 有 | 已接电 | regime/core/regime_detector.py | regime_snapshot_history 唯一自动产出者=pipeline_events(2026-09-16 挂 daily_kline SUCCESS)；消费=pf_alloc 分配链(纸面)+RSC-2 回测节流(#270) |
| TDM-E-L1-S1 | SKL1 | T2 | 无 | 已接电 | regime/features/index_sensor.py | regime 特征管线/miniqmt provider 内部消费 |
| TDM-E-L1-S2 | SKL1 | T3 | 无 | 覆盖未接电 | signal_ashare/limit_up/limit_up_followthrough.py | 模块在盘、域内互调；无日循环触发面 |
| TDM-E-L1-S3 | SKL1 | T2 | 无 | 覆盖未接电 | signal_ashare/limit_up/lhb_premium_analyzer.py | 模块在盘、域内互调；无日循环触发面 |
| TDM-E-L1-S4 | SKL1 | T2 | 无 | 已接电 | regime/features/synthetic_vix.py | regime 特征管线/miniqmt provider 内部消费 |
| TDM-E-L1-S0 | SKL1 | T2 | 无 | 覆盖未接电 | alt_data/policy_expectation_analyzer.py | 模块在盘；零外部调用方 |
| TDM-E-L1-S0-1 | SKL1 | 持续 | 无 | 覆盖未接电 | intelligence/news_sentiment_analyzer.py | 模块在盘、域内互调；无日循环触发面 |
| TDM-E-L1-S5 | SKL1 | T3 | 无 | 覆盖未接电 | signal_ashare/core/daily_condition_sensor.py | 模块在盘；仅包导出（零实质调用方） |
| TDM-E-L1-AGG | SKL1 | T1+T2 | 弱 | 已接电 | regime/core/regime_detector.py | 同 E-L1（状态判定含置信度；出手门在 E-L1 总闸） |
| TDM-E-L2 | SKL2 | T2 | 无 | 覆盖未接电 |  | 段落父节点（module_ref=null）：电态=子节点聚合 |
| TDM-E-L2-01 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/core/sector_strength_aggregator.py | 模块在盘（115/115 实码零缺失）、链内互调活；tasks.yaml 仅数据任务，无决策日循环触发面 |
| TDM-E-L2-01-1 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_analyzer.py | 同上 |
| TDM-E-L2-01-2 | SKL2 | T4 | 无 | 覆盖未接电 | data/sector_ranking_engine.py | 同上 |
| TDM-E-L2-01-3 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_momentum.py | 同上 |
| TDM-E-L2-01-4 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_breadth.py | 同上 |
| TDM-E-L2-01-5 | SKL2 | T4 | 无 | 覆盖未接电 | regime/market_forecast_fusion.py | 同上 |
| TDM-E-L2-02 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_divergence.py | 同上 |
| TDM-E-L2-02-1 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_rrg.py | 同上 |
| TDM-E-L2-02-2 | SKL2 | T3 | 无 | 覆盖未接电 | signal_ashare/sector/sector_analyzer.py | 同上 |
| TDM-E-L2-03 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_adjustment.py | 同上 |
| TDM-E-L2-03-1 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/adjustment_cycle_tracker.py | 同上 |
| TDM-E-L2-04 | SKL2 | T4 | 弱 | 覆盖未接电 | signal_ashare/core/sector_ecology_judge.py | 同上（板块级状态=出手档依据，门形弱） |
| TDM-E-L2-04-1 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_rotation_state.py | 同上 |
| TDM-E-L2-04-2 | SKL2 | T4 | 弱 | 覆盖未接电 | signal_ashare/sector/sector_siphon.py | 同上（虹吸识别=风险提示非出手门） |
| TDM-E-L2-05 | SKL2 | T2 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L2-05-1 | SKL2 | T2 | 无 | 已接电 | signal_ashare/sentiment/sentiment_cycle.py | sentiment_cycle 有 6 消费方（environment_switch/tomorrow_boundary_planner 等）间接通电 |
| TDM-E-L2-05-2 | SKL2 | T2 | 弱 | 覆盖未接电 | signal_ashare/sector/sector_gate.py | sector_gate 有域内消费方（conduction/rotation_state/rrg），链本身无日循环触发 |
| TDM-E-L2-06 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/core/sector_conduction.py | 同 L2 家族 |
| TDM-E-L2-06-1 | SKL2 | T3 | 有 | 覆盖未接电 | signal_ashare/sector/sector_gate.py | 三级放行门槛逻辑在，触发面缺 |
| TDM-E-L2-06-2 | SKL2 | T3 | 无 | 覆盖未接电 | signal_ashare/sector/sector_leader.py | 同 L2 家族 |
| TDM-E-L2-06-3 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/core/sector_conduction.py | 同 L2 家族 |
| TDM-E-L2-07 | SKL2 | T3 | 无 | 覆盖未接电 | signal_ashare/sector/sector_pullback.py | 同 L2 家族 |
| TDM-E-L2-07-1 | SKL2 | T3 | 无 | 覆盖未接电 | signal_ashare/sector/sector_pullback.py | 同 L2 家族 |
| TDM-E-L2-08 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/sector/sector_momentum_persistence.py | 同 L2 家族 |
| TDM-E-L2-09 | SKL2 | T2 | 无 | 覆盖未接电 | signal_ashare/screening/event_driven_screener.py | 同 L2 家族 |
| TDM-E-L2-09-1 | SKL2 | 持续 | 无 | 覆盖未接电 | intelligence/news_chain_node_linker.py | 同 L2 家族 |
| TDM-E-L2-09-2 | SKL2 | 持续 | 无 | 覆盖未接电 | intelligence/chain_impact_resolver.py | 同 L2 家族 |
| TDM-E-L2-10 | SKL2 | T4 | 无 | 覆盖未接电 | signal_ashare/supply_chain_momentum.py | 同 L2 家族 |
| TDM-E-L3 | SKL3 | T2 | 无 | 覆盖未接电 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L3-01 | SKL3 | T4 | 无 | 覆盖未接电 | data/instrument_master.py | 选股链互调活（selection_funnel 4/fine_scoring 6 消费方），消费面=回测/整装 framework_composer，生产日循环无挂点 |
| TDM-E-L3-02 | SKL3 | T4 | 无 | 覆盖未接电 | signal_fundamental/selection_funnel.py | 同 L3 家族 |
| TDM-E-L3-03 | SKL3 | T4 | 无 | 覆盖未接电 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L3-03-1 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/fine_scoring_engine.py | 同 L3 家族 |
| TDM-E-L3-03-2 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/quant_short_term_strength_engine.py | 同 L3 家族 |
| TDM-E-L3-03-3 | SKL3 | T4 | 弱 | 覆盖未接电 | signal_fundamental/router/signal_conflict_resolver.py | 同 L3 家族（合流体检=弱门） |
| TDM-E-L3-04 | SKL3 | T4 | 有 | 覆盖未接电 | signal_fundamental/negative_veto.py | 同 L3 家族（一票否决门） |
| TDM-E-L3-05 | SKL3 | T4 | 弱 | 覆盖未接电 | signal_fundamental/selection_confidence.py | 同 L3 家族（顺位截断=弱门） |
| TDM-E-L3-06 | SKL3 | T2 | 有 | 覆盖未接电 | signal_ashare/core/environment_switch.py | 同 L3 家族（六段×四开关环境门；消费方 framework_composer=回测侧） |
| TDM-E-L3-07 | SKL3 | T4 | 无 | 覆盖未接电 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L3-07-1 | SKL3 | T3 | 无 | 覆盖未接电 | pf_core/strategies/daban_sleeve_strategy.py | 同 L3 家族 |
| TDM-E-L3-07-2 | SKL3 | T4 | 无 | 覆盖未接电 | factor/analysis/multifactor_synthesis.py | 同 L3 家族 |
| TDM-E-L3-07-3 | SKL3 | T4 | 无 | 覆盖未接电 | pf_core/strategies/event_driven_sleeve_strategy.py | 同 L3 家族 |
| TDM-E-L3-08 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/core/candidate_pool_aggregator.py | 同 L3 家族 |
| TDM-E-L3-09 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/core/pool_tier_maintenance.py | 同 L3 家族 |
| TDM-E-L3-10 | SKL3 | T2 | 有 | 覆盖未接电 | signal_ashare/tradability_preflight.py | MOD-SIG-151 五查预检 2026-09-16 刚落地，调用方=0（新件待接线） |
| TDM-E-L3-11 | SKL3 | T3 | 无 | 覆盖未接电 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L3-11-1 | SKL3 | T3 | 无 | 覆盖未接电 | signal_ashare/auction_microstructure_analyzer.py | 同 L3 家族 |
| TDM-E-L3-11-2 | SKL3 | T3 | 无 | 覆盖未接电 | signal_ashare/intraday_t0/intraday_volume_orderflow.py | 同 L3 家族 |
| TDM-E-L3-12 | SKL3 | T4 | 无 | 覆盖未接电 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L3-12-1 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/capital_flow_pattern_analyzer.py | 同 L3 家族 |
| TDM-E-L3-12-2 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/limit_up/seat_pattern_analyzer.py | 同 L3 家族 |
| TDM-E-L3-12-3 | SKL3 | T4 | 无 | 覆盖未接电 | regime/features/chip_distribution_engine.py | 同 L3 家族 |
| TDM-E-L3-12-4 | SKL3 | T4 | 无 | 覆盖未接电 | signal_ashare/chanlun_structure.py | 同 L3 家族 |
| TDM-E-L4 | SKL5 | T3 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-E-L4-01 | SKL5 | T3 | 无 | 覆盖未接电 | ex_core/order_splitter.py | 分批/时序件在（order_splitter 有 sor_agent 消费），无日单源 |
| TDM-E-L4-02 | SKL5 | T3 | 无 | 覆盖未接电 | plan_engine/closing_session_decision.py | 同上 |
| TDM-E-L4-03 | SKL5 | T3 | 无 | 覆盖未接电 | ex_core/pricing_policy.py | 委托管线件族 production 成熟度、经 execution_engine/sor/QMT adapter 内部闭环通电；缺上游日单源（BT-P2-055） |
| TDM-E-L4-04 | SKL5 | T3 | 无 | 覆盖未接电 | signal_fundamental/capital/capital_allocator.py | capital_allocator 件在，无日单源 |
| TDM-E-L4-05 | SKL5 | T3 | 无 | 覆盖未接电 | ex_core/daban_execution.py | 打板执行件在；四引擎应用层 2026-09-16 真数据贯通（#277）但执行模板缺 |
| TDM-E-L4-06 | SKL5 | T3 | 无 | 覆盖未接电 | ex_sor/core/algo_execution_selector.py | 同委托管线件族 |
| TDM-E-L4-07 | SKL5 | 持续 | 弱 | 覆盖未接电 | ex_core/local_order_queue.py | 同委托管线件族（条件触发=弱门） |
| TDM-E-L4-08 | SKL5 | T3 | 弱 | 覆盖未接电 | sell_decision/core/breakout_failure_detector.py | breakout_failure_detector 有 sell_decision 消费，无日循环触发 |
| TDM-E-L4-09 | SKL5 | 持续 | 有 | 覆盖未接电 | ex_core/price_cage.py | 同委托管线件族（价格笼子=硬约束门，QMT adapter 路径通电） |
| TDM-E-L4-10 | SKL5 | 持续 | 无 | 覆盖未接电 | ex_core/order_manager.py | 同委托管线件族 |
| TDM-E-L4-11 | SKL5 | T3 | 无 | 覆盖未接电 | ex_core/fill_handler.py | 同委托管线件族 |
| TDM-E-L4-12 | SKL5 | T3 | 有 | 覆盖未接电 | ex_core/pre_execution_checker.py | 同委托管线件族（订单级预检门） |
| TDM-E-L4-13 | SKL5 | 持续 | 无 | 覆盖未接电 | trading/three_way_reconciliation.py | 同委托管线件族 |
| TDM-E-L4-14 | SKL5 | T4 | 无 | 覆盖未接电 | ex_sor/services/execution_quality_scorer.py | 断链实证在案（TDM 注记 2026-09-10）：三零件全 production，缺评分器→选择器回写接线 |
| TDM-P-P1 | SKL4 | T2 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-P-P2 | SKL5 | T3 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-P-P3 | SKL4 | T3 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-P-P1-01 | SKL4 | T2 | 无 | 已接电 | position/core/position_state_machine.py | position_state_machine 被 dashboard_feeds/audit_logger 消费（仪表盘面） |
| TDM-P-P1-02 | SKL4 | 持续 | 弱 | 已接电 | sell_decision/core/position_triage.py | position_triage/thesis_survival/adjudication_center 链内活（MOD-POS-024 在 pf_alloc 装配链） |
| TDM-P-P1-03 | SKL4 | T2 | 有 | 已接电 | plan_engine/thesis_survival.py | 同上（存活判定门） |
| TDM-P-P1-04 | SKL4 | T2 | 有 | 覆盖未接电 | risk/core/ashare_stop_loss_engine.py | 止损引擎/drift 监控件在，日循环无驱动 |
| TDM-P-P1-05 | SKL4 | 持续 | 弱 | 覆盖未接电 | position/core/position_drift_monitor.py | 同上 |
| TDM-P-P1-06 | SKL4 | T2 | 弱 | 已接电 | position/core/position_adjudication_center.py | 链内活（pf_alloc 装配链消费） |
| TDM-P-P2-01 | SKL5 | T2 | 有 | 覆盖未接电 | position/core/t1_sellable.py | 做T链件在（t0_trading_pipeline maturity=testing，t_trade_coordinator 有 2 消费方）；无日循环触发 |
| TDM-P-P2-02 | SKL5 | T3 | 无 | 覆盖未接电 | sell_decision/core/t_trade_coordinator.py | 同上 |
| TDM-P-P2-03 | SKL5 | T3 | 无 | 覆盖未接电 | signal_ashare/intraday_t0/t0_trading_pipeline.py | 同上 |
| TDM-P-P2-04 | SKL5 | T3 | 无 | 覆盖未接电 | position/core/rebalance_engine.py | 同上 |
| TDM-P-P3-01 | SKL4 | T2 | 有 | 覆盖未接电 | position/core/pyramiding_rules.py | pyramiding_rules 仅包导出（零外部调用方）；加仓资格四重门逻辑在 |
| TDM-P-P3-02 | SKL4 | T3 | 无 | 覆盖未接电 | position/core/pyramiding_rules.py | 同上 |
| TDM-P-P3-03 | SKL4 | T3 | 弱 | 覆盖未接电 | position/core/position_sizing_engine.py | position_sizing_engine 有链内消费（track_fusion/firm_risk_aggregator），加仓流无日循环触发 |
| TDM-P-P3-04 | SKL4 | T3 | 弱 | 覆盖未接电 | position/core/position_limit_enforcer.py | 同上 |
| TDM-X-S1 | SKL4 | 持续 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-X-S2 | SKL5 | T3 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-X-R1 | SKL4 | 持续 | 有 | 已接电 | security/access_control/kill_switch.py | kill_switch=autonomy_core 全家桶消费；drawdown_state_machine 有 session_persistence+defensive_whitelist 消费 |
| TDM-X-R1-01 | SKL4 | 持续 | 有 | 已接电 | risk/core/drawdown_state_machine.py | 同上（熔断分级门） |
| TDM-X-R1-02 | SKL4 | T3 | 无 | 已接电 | risk/core/drawdown_liquidation_guard.py | drawdown_liquidation_guard/defensive_whitelist 与熔断链互锁 |
| TDM-X-R1-03 | SKL4 | T3 | 无 | 已接电 | position/core/defensive_asset_whitelist.py | 同上 |
| TDM-X-S1-01 | SKL4 | 持续 | 无 | 覆盖未接电 | sell_decision/core/sell_signal_collector.py | sell_decision 链 production 成熟度、内部互调活；无日循环驱动（卖出信号无人按日收集） |
| TDM-X-S1-02 | SKL4 | 持续 | 有 | 覆盖未接电 | sell_decision/core/stop_loss_strategy.py | 同上（止损门） |
| TDM-X-S1-03 | SKL4 | 持续 | 有 | 覆盖未接电 | sell_decision/core/take_profit_strategy.py | 同上（止盈门） |
| TDM-X-S1-04 | SKL4 | 持续 | 弱 | 覆盖未接电 | sell_decision/core/breakout_failure_detector.py | 同上 |
| TDM-X-S1-05 | SKL4 | 持续 | 有 | 覆盖未接电 | sell_decision/core/sell_signal_fusion_engine.py | 同上（紧迫度融合门） |
| TDM-X-S1-06 | SKL4 | 持续 | 无 | 覆盖未接电 | trading/strategy_abnormal_exit_orchestrator.py | 同上 |
| TDM-X-S2-01 | SKL5 | T3 | 无 | 覆盖未接电 | sell_decision/core/sell_execution_planner.py | 离场执行件族在（路由/约束/条件单/分批），无上游日单源 |
| TDM-X-S2-02 | SKL5 | T3 | 有 | 覆盖未接电 | position/core/t1_sellable.py | 同上（T+1/涨跌停约束门） |
| TDM-X-S2-03 | SKL5 | T3 | 弱 | 覆盖未接电 | ex_sor/core/sell_session_router.py | 同上 |
| TDM-X-S2-04 | SKL5 | 持续 | 无 | 覆盖未接电 | ex_core/local_order_queue.py | 同上 |
| TDM-X-S2-05 | SKL5 | T3 | 无 | 覆盖未接电 | sell_decision/core/scaling_out.py | 同上 |
| TDM-X-S2-06 | SKL5 | T4 | 无 | 覆盖未接电 | sell_decision/core/sell_execution_quality_tracker.py | 同上 |
| TDM-F-C1 | SKL4 | T1+T2 | 有 | 覆盖未接电 | pf_alloc/core/multi_strategy_capital_allocator.py | multi_strategy_capital_allocator 唯一消费方=signal_weight_adjuster；生产预算切分实走 RegimeMetaAllocator 链——TDM 指定模块与生产装配体错位（审计发现） |
| TDM-F-C2 | SKL4 | 持续 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-F-C3 | SKL4 | T4 | 无 | 结构 |  | 段落父节点：电态=子节点聚合 |
| TDM-F-C2-01 | SKL4 | 持续 | 无 | 已接电 | position/core/firm_risk_aggregator.py | pf_alloc 五模块链装配体 allocation_orchestrator（车道D/D2 2026-09-16，experimental）链内活；pipeline_events.maybe_emit_pf_alloc_daily=唯一自动发射方 |
| TDM-F-C2-02 | SKL4 | 持续 | 弱 | 已接电 | position/core/firm_risk_aggregator.py | 同上（组合约束栈=弱门） |
| TDM-F-C2-03 | SKL4 | 持续 | 弱 | 已接电 | position/core/correlation_regime_monitor.py | correlation_regime_monitor 有 strategy_book/adaptive_risk_monitor 消费方 |
| TDM-F-C2-04 | SKL4 | 持续 | 弱 | 已接电 | position/core/budget_change_handler.py | 同 F-C2-01（budget 变动三级升级在装配链） |
| TDM-F-C3-01 | SKL4 | T4 | 无 | 已接电 | pf_core/core/performance_attribution_engine.py | performance_attribution_engine 有 risk 域 4 消费方（生产级弱电流） |
| TDM-F-C3-02 | SKL4 | T4 | 无 | 已接电 | factor/governance/lifecycle_state_machine.py | lifecycle_state_machine 8 消费方（factor governance 生产） |
| TDM-F-C3-03 | SKL4 | T1+T4 | 无 | 已接电 | pf_alloc/core/regime_meta_allocator.py | 同 F-C2-01（sleeve 月度调权=周期切换器散件之一） |
| TDM-F-C3-04 | SKL4 | T1+T4 | 无 | 已接电 | backtest/core/walk_forward.py | walk_forward 在整装/回测链（fw-tdm-current）消费 |
| TDM-F-C3-05 | SKL4 | T4 | 无 | 覆盖未接电 | signal_quality/signal_degradation_monitor.py | signal_degradation_monitor 仅 signal_quality 域内部 |
| TDM-C-L1 | SKL1 | T1+持续 | 弱 | 缺失 |  | crypto V0 骨架空壳，module_ref=null，等 A 股链验证后移植 |
| TDM-C-L2 | SKL2 | 持续 | 无 | 缺失 |  | crypto 空壳 |
| TDM-C-L3 | SKL3 | 持续 | 无 | 缺失 |  | crypto 空壳 |
| TDM-C-L4 | SKL5 | 持续 | 无 | 缺失 |  | crypto 空壳 |
<!-- COVERAGE-TABLE:END -->

## 四、组织者判定（骨架两件的雏形考古）

**T1 周期切换器（策略包切换执行体）：不存在，散件三块。**
- 散件 A：`regime_meta_allocator`（F-C3-03，已接电于装配链）——sleeve 权重月度调权，是"周期→权重"的一半；
- 散件 B：TDM `state_matrix` + `portfolio_plan.activation_state`——"状态→哪些 sleeve 激活"的**配置真源**已存在（24 格，proposed），但格子填充多数 `pending-owner-adoption`（=Owner 资金分配门位，AI 禁自填）；
- 散件 C：`environment_switch`（E-L3-06）——"状态→选股链开停"查表已在（回测侧消费）。
- **缺口**：三者无统一执行体；Owner 语义的"震荡期只放行 ETF 波段包、趋势期解锁进攻包"（策略卡 2 主体）无节点、无模块、无考试。E-L1 总闸 decision_question 含"月级定大档"，但"月级重定大档"的触发体同样不存在。

**T2 日度编排器（晨判+今日不交易权）：不存在，骨架一件。**
- 最接近件=`daily_warroom_pipeline`（MOD-PLAN-018，E-L0 总闸指定模块）：自称"唯一的日循环编排入口（运行时挂 57 号日循环 SOP 环节④）"，但**仓库内零调用方**（grep 无消费实证），且自述边界"不做盘中调度、纯编排零判定逻辑"——只管 scenario 样本积累，不做"晨取 L1→定包→定仓位→放行/禁做"拍板。
- 事件总线已活：`pipeline_events`（MOD-BT-190）已承载 daily_kline SUCCESS→regime 刷新→pf_alloc_daily→sim_ledger_daily 的自动链——**编排器的血管通了，心脏没装**。
- 缺口挂单：BT-P1-031（组合日度编排闭环，含今日不交易权），plan_note 明确"编排器设计须先落蓝图过审"。

## 五、双态门普查（每层参与门：有/弱/无）

| 层 | 门节点 | 门语义 | 电 |
|---|---|---|---|
| L1 | E-L1 总闸（有） | 消费 RegimeSnapshot 7 态概率=谨慎度→当日总仓位上限；"今天下不下单"定界归它（Owner 2026-09-09：计划是输入不是第二决策点） | 已接电（纸面/回测消费） |
| L2 | E-L2-06-1 三级放行（有）/ E-L2-05-2 三件套联动（弱）/ E-L2-04 板块级状态（弱）/ E-L2-04-2 虹吸（弱） | 板块强度>6+个股强度>5+流动性三关全过才进打分池；水温联动权重/门槛/象限过滤 | 覆盖未接电（触发面缺） |
| L3 | E-L3-06 环境开关（有）/ E-L3-04 负面否决（有）/ E-L3-10 可交易预检（有）/ E-L3-03-3 合流体检（弱） | 六段×四开关查表（地量停首板/冰点停短线）；负面清单一票否决；停牌/一字/权限/资金/笼子五查 | 覆盖未接电（回测侧消费） |
| L4 | F-C1 预算切分（有）/ F-C2-02 约束栈+F-C2-03 相关性上限（弱）/ P3-01 加仓资格四重门（有）/ X-R1 熔断（有） | 预算带 0% 段=禁新开仓（distribution）；总仓位=min(预算带,60% 硬顶)；ρ>0.70 减半/>0.85 禁新仓；日亏 4% 熔断全禁加 | 半接电：约束件在装配链活；**预算带→"今日不交易"的拍板体无人持有** |
| L5 | E-L4-09 价格笼子（有）/ E-L4-12 订单预检（有）/ X-S2-02 T+1 约束（有）/ P2-01 做T资格（有）/ E-L4-14 成本反馈（断链） | 价格笼子夹边；订单级 fail-closed 预检；日回转额度≤前收盘持仓（语义在 t1_sellable） | 笼子/预检通电于 QMT 路径；做T资格未触发；成本反馈环在案断链 |

**结论**：双态门在五层**全部有形**（TDM 无门缺口），弱点在两处——①门多半"无电"（L2/L3 门逻辑在回测侧空转）；②L4 的"不出手"半边（今日不交易权）只有语义（预算带 0%、禁做清单 sit_out_list 三源合成在 E-L0 注记）没有**日度拍板执行体与留痕**。

## 六、三清单

### 绿灯清单（已接电 23 节点）

| 层×拍 | 节点 | 模块/证据 |
|---|---|---|
| L1×T1/T2 | TDM-E-L1、TDM-E-L1-AGG | regime_detector：regime_snapshot_history 唯一自动产出者=pipeline_events（2026-09-16 挂 daily_kline SUCCESS）；消费=pf_alloc 纸面分配链+RSC-2 回测节流（#270） |
| L1×T2 | TDM-E-L1-S1、TDM-E-L1-S4 | index_sensor/synthetic_vix：regime 特征管线与 miniqmt provider 内部消费 |
| L2×T2 | TDM-E-L2-05-1 | sentiment_cycle：6 消费方（环境开关/明日边界）间接通电 |
| L4×持续 | TDM-F-C2-01/02/03/04 | firm_risk_aggregator/correlation_regime_monitor/budget_change_handler：pf_alloc 装配链（车道D/D2）链内活 |
| L4×T1/T4 | TDM-F-C3-03、TDM-F-C3-04 | regime_meta_allocator（装配链）/walk_forward（fw-tdm-current） |
| L4×T4 | TDM-F-C3-01、TDM-F-C3-02 | performance_attribution_engine（risk 域 4 消费方）/lifecycle_state_machine（8 消费方） |
| L4×T2/持续 | TDM-P-P1-01/02/03/06 | position_state_machine（仪表盘面）/position_triage/thesis_survival/adjudication_center（装配链） |
| L4×持续 | TDM-X-R1、TDM-X-R1-01/02/03 | kill_switch（autonomy_core 全家桶）/drawdown_state_machine/liquidation_guard/defensive_whitelist（熔断链互锁） |
| ORG×T3/T4 | TDM-E-L0-02、TDM-E-L0-03 | plan_deviation_monitor（production）/tomorrow_boundary_planner（production，仪表盘 warroom 消费） |

### 黄灯清单（覆盖未接电 98 节点，按断点分组）

| # | 断点 | 节点组（数） | 生产断在哪 | 归属 |
|---|---|---|---|---|
| Y1 | **决策链无日循环触发面**（最大公约数） | L2 全家族(26)、L3 全家族(20)、S1(7)、S2(6)、P2(4)、P3(4)、P1-04/05、E-L4 主体(13)、C3-05 等 | `tasks.yaml` 全是数据任务；决策层唯一事件挂点=daily_kline SUCCESS→regime→pf_alloc（pipeline_events）；其余决策链无发射方 | 基建方案"一器"（本文 §七）承接，归 BT-P1-031 |
| Y2 | 盘前作战计划编排件零调用方 | E-L0、E-L0-01、E-L0-04 | daily_warroom_pipeline 零消费实证、stability=testing；daily_trade_plan testing | BT-P1-031（"一器"复用其骨架） |
| Y3 | L1 传感器教材不全 | E-L1-S2/S3/S0/S0-1/S5(5) | 总闸只吃 RegimeSnapshot；S5 仅包导出、S0 零调用——传感器未进日更面，总闸教材面窄 | 待 Owner 定必需传感器集（§八待判定-1） |
| Y4 | 预算切分模块错位 | F-C1(1) | TDM 指定 multi_strategy_capital_allocator，生产实走 RegimeMetaAllocator 装配链——**指定件仅 1 弱消费方**（审计新发现） | TDM 节点 module_ref 对齐生产装配体（改图不改码，属 TDM 台账分诊另案） |
| Y5 | 执行成本反馈断链（在案） | E-L4-14(1) | 三零件全 production，评分器→选择器回写无接线（TDM 注记实证 2026-09-10） | ex_sor 小接线工单（S） |
| Y6 | 可交易预检新件零调用方 | E-L3-10(1) | MOD-SIG-151 今日落地，调用方=0 | L3 链接线时顺带挂（随 Y1） |
| Y7 | 加仓/金字塔规则零调用方 | P3-01/02(2) | pyramiding_rules 仅包导出；Owner"TD 阶<0 金字塔建仓"的规则化载体在、无消费 | 随 L4 编排（BT-P1-031）或策略卡 1 考试线 |
| Y8 | 做T链无日触发 | P2-01..04(4) | t0_trading_pipeline testing；t_trade_coordinator 2 消费方但链头无发射 | BT-P2-055（底仓+日内回转执行模板） |
| Y9 | 卖出/离场链无日驱动 | S1(7)/S2(6) | production 成熟度、内部互调活、链头无人按日喂持仓与信号 | 随 Y1 编排器（持仓体检段先通则 S1 有输入） |
| Y10 | 委托管线无上游单源 | E-L4-01..13(13) | execution_engine/sor/QMT adapter 下半段通电；上半段无策略模板产单 | BT-P2-055 |
| Y11 | 信号健康/降级监控域内自转 | F-C3-05(1) | 仅 signal_quality 域内部 | 降级观察，随退役审计（宪法 §4.2） |

### 红灯清单（骨架要求但 TDM/代码没有）

| # | 缺件 | 骨架依据 | 现状 | 挂单建议 |
|---|---|---|---|---|
| R1 | **T1 周期切换器**（策略包切换执行体） | T1 拍=周期判定→策略包配置；策略卡 2 主体 | 散件三块（§四），无执行体、无对照回测 | 随"一器"立项；先框架后考试（依赖 ≥2 个已毕业策略包） |
| R2 | **T2 日度编排器**（含"今日不交易"权） | T2 拍=开不开仓+用哪个包+仓位上限 | warroom 骨架零调用+事件血管已通；拍板体不存在 | BT-P1-031（已挂）=本文"一器" |
| R3 | **L4"今日不交易权"显式化** | L4 判定物=总仓位+调仓单+**今日不交易** | 语义三处散在（C1 预算带 0% 禁新开仓/E-L0 sit_out_list 禁做清单/kill_switch 熔断），无日度拍板+留痕 | 归"一器"核心职责：快照落库"今日不交易+理由"（一库） |
| R4 | **L2 信噪比出手门**（电风扇→只买 300ETF） | Owner 愿景三亮点①；双态门原则 L2=排序+出手门 | TDM 无节点、代码无模块；最接近的 E-L2-04/04-2 是状态识别非"混乱度→切指数"决策 | 与 BT-P1-030（板块轮动策略包模板）同批立卡 |
| R5 | crypto 全层实码 | TDM C-L1..L4 | 有意空壳（v1 等 A 股链验证后移植，非遗漏） | 维持空壳，不挂单（by-design） |

## 七、决策权视图基建最小方案（一库一器一闸一图）

> 原则：全件=升级既有件/图，不建新图（对齐既有裁定方向）；触发一律走 `pipeline_events` 事件链（宪法 §9.3 禁 cron/Timer）；Owner 门位不越权（state_matrix `pending-owner-adoption` 格子=资金分配决策归 Owner）。

| 件 | 定义（决策权视图语境） | 复用什么 | 新增/接线什么 | 工程量 | 依赖 |
|---|---|---|---|---|---|
| **一库：日度决策快照** | 每日 T2 拍板结果落一处：日期/市场状态+置信度/启用策略包/总仓位上限/禁做清单/各层门态/“今日不交易”布尔+理由。这是"谁在哪个格子拍了板"的留痕真源 | 复用 `alloc_budget_daily`（分配结果）+`regime_snapshot_history`（状态教材）+`prediction_log`（预案留痕通道） | 新增 1 张 `decision_daily` 快照表（或 prediction_log 加 decision 族行），DDL 走 depgraph 登记；写侧只挂一器 | **S** | 无（先行件） |
| **一器：日度编排器**（=BT-P1-031 本体） | T2 拍板体+T1 执行体：晨取 regime 状态→查 state_matrix/activation_state 定包→算总仓位上限（E-L1 总闸语义+预算带）→**拍板"今日交易/不交易"**→落一库→发事件驱动下游（体检/选股/执行/复盘）。持有"今日不交易权" | 复用 `daily_warroom_pipeline` 骨架（日循环两段编排/幂等/fail-open 口径现成）+`pipeline_events` 事件总线（血管已通）+E-L1 gate 语义+P3-01 资格门+C1 预算带 | 新增拍板逻辑（消费 state_matrix→包开关映射）；把零调用的 warroom pipeline 改造成晨判编排并挂事件链；蓝图先过审（BT-P1-031 plan_note 要求） | **M-L** | 一库；state_matrix 格子 Owner 采纳 |
| **一闸：分层参与门快照** | 五层门态数值化采集：L1 谨慎度/L2 放行档/L3 开关表/L4 预算带与不交易/L5 熔断态——器统一采集落一库，门逻辑本身**不改** | 复用 sector_gate 三级放行/environment_switch 查表/C1 预算带/kill_switch 熔断态/价格笼子——全部只读采集 | 接线：各门模块暴露只读快照口（或在器侧聚合查询），零判定逻辑改动 | **S-M** | 一器 |
| **一图：今日决策视图** | Owner 每天看的一屏：今日状态/包/仓位上限/各层门态/不交易原因+TDM 高亮当前位置——决策权的**可视面** | 复用 dashboard warroom 组件（tomorrow_boundary_planner 已接仪表盘）+TDM 图本体（状态矩阵 24 格已在图内） | 新增"今日决策"面板读一库；TDM 高亮=按节点 id 映射，不重建图 | **M** | 一库 |

**施工顺序**：一库（S）→ 一器（M-L，蓝图过审后）→ 一闸（S-M）→ 一图（M）；一库与一闸可并行先行。四件合计不新建任何决策算法——全部是"把已接电的 L1/L4 电力配电到全骨架"的接线工程。

## 八、待判定项清单（诚实条款：判定不了如实留）

1. **L1 必需传感器集未定义**：总闸注释只说"消费 RegimeSnapshot"，S2/S3/S0/S5 哪些是必需日更输入、哪些是可选增强——TDM 未声明，本审计不代定（Y3 归属待 Owner/架构裁）。
2. **`llm_premarket_analysis`（S3 消费方）挂点未明**：未查到其在日循环的触发面，若属 57 号日循环在飞件请车道归属会话指认。
3. **"持续"拍 30 节点未强行单拍化**：横切/监控类节点（X-R1 族、F-C2 族等）跨拍运作，映射为"持续"而非硬塞单拍。
4. **crypto 四节点节拍标签为占位**：移植时须重定，现标签不构成判定。
5. **E-L2-01 家族 point=盘后与"盘前消费"的语义差**：按计算时点落格（方法注记 §一.2），若 TDM 意图为消费时点需图侧澄清（本次只读未改）。
6. **车道在飞漂移**：pf_alloc/ex_sor/daban 今晚多车道变更中，"已接电(实验级)"判定以本审计时点 grep 为准，落地后可能升级。

## 九、引用

- 骨架定义：[`2026-09-16-owner-vision-system-mapping.md`](2026-09-16-owner-vision-system-mapping.md)（§一五层级联/§三现状映射/§四两策略卡）
- TDM 真源：`config/trading_decision_map.yaml`（schema 1.2，138 节点/194 边/24 状态格/PP-001 16 sleeve）
- 裁定：#257③（pf_alloc 挂触发——触发条件"G15→G14 编排件立项"经车道 D 兑现）、#264/#271（wyckoff 维证伪→生产显式置零，L1 教材面收缩）、#270（RSC-2 Shrinkage 双轨披露制）、#277（daban 四引擎真数据贯通，L4 daban-sleeve 0.0945 有真输入）；真源=`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`
- 缺件挂单：BT-P1-030（板块轮动策略包模板）/BT-P1-031（组合日度编排闭环）/BT-P2-055（底仓+日内回转执行模板）=`docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml`
- 生产事件链实证：`src/zephyr/strategy_pipeline/pipeline_events.py`（MOD-BT-190：maybe_refresh_regime_snapshot+maybe_emit_pf_alloc_daily 唯一自动产出者）、`src/zephyr/pf_alloc/allocation_orchestrator.py`（MOD-PA-030 五模块链装配体）、`src/zephyr/data/config/tasks.yaml`（数据任务面）
- 解析中间产物（审计过程件，.runtime/tmp 24h TTL）：`tdm_audit_nodes.json`/`coverage_table.md`/`tdm_audit_parse.py`/`gen_coverage_table.py`
- 落库记录（2026-09-17）：worktree commit → merge 回 dev；creation token 条目（trading-vision-audit-2026-09-16-skeleton-coverage-audit-20260916）随 belt 批次先期落库 HEAD；主区直连与队列路径因多车道在飞（主区 374 外来 staged、DEPGRAPH 外来 drift、registry 净删拦截、serializer 新文件 pathspec 缺口）改走会话 worktree 正道，如实留痕。
