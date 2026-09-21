---
ttl: task_bound
title: 深度审查战役全景清单 deep_review_full
owner: st-deeprev-20260918
created: 2026-09-18
---

# 审查对象全景清单（阶段0封矿真源）

- 总对象数: **159**（初册）→ **235**（T08 对账补册 +76）（P0级=58 P1级=54 P2/P3级=47）
- 三域: p0_money_path=38 / p1_decision_chain=76 / p2_infra=45
- 基线 commit: 2fa92002c3｜对象来源=三路只读勘察（file:line 逐一核实）+ tasks.yaml 235 在册任务归并为 15 时段族
- 台账真源: `01_master_ledger.csv`（唯一进度真源，状态实时更新）

## 封矿判据（阶段0出口条件）
1. 全景清单对账零缺口：本清单 ∪ TDM地图节点 ∪ ROOR 在册注册表 对账无遗漏（T08 作业簿承载对账记录）；
2. 总台账满格：161 行×状态列无空白；
3. 自审闸三态裁定全过（过度工程/材料缺失/优先级倒挂逐项裁定）。

## 排除项登记（审过边界、判定不入册的对象+理由）
- ReconciliationLoop(src/zephyr/orchestrator/execution/reconciliation_loop.py:60)——未接入实盘会话，接线后升级；
- OptimalOrderRouter(ex_sor:292)——单券商现状未在钱路径生效；
- miniqmt_channel_manager——无外部消费者，疑预留；
- FeatureGate(compliance/hard_boundary_adjudicator.py:103)——管建设权不管资金，P1治理域；
- LSGSecurityGateway——当前消费方为AI治理链，未挂下单建议链，LLM直达交易决策时须立即升P0；
- AsyncInterceptQueue——治理网关吞吐件非资金路径；
- post_close_pricing——科创板盘后定价独立小通道，P2后置；
- position/position_reconciler.py:41——与ex_core同名平行实现，并入R02的D轴去重审查；
- docs业务注册表(REG-*)——配置真源非可执行算法，由ROOR一致性校验兜底；
- sell_decision族——裁定#309整族挂起（审查继续，施工受裁定约束）；
- strategy_pipeline生命周期FSM在T04；卖出决策在E01-E06。

## 全对象索引

| ID | 域 | 级别 | 名称 | 类型 | 入口 |
|---|---|---|---|---|---|
| V01 | p0_money_path | P0 | Wilson下界单源 | 算法 | `src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py:42` |
| V02 | p0_money_path | P0 | 四闸证据认证器 | 闸门 | `src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py:186` |
| V03 | p0_money_path | P0 | BHY/BH FDR双实现 | 算法 | `src/zephyr/factor/analysis/bhy_fdr.py:79 + src/zephyr/strategy_pipeline/bh_fdr.py:42` |
| V04 | p0_money_path | P0 | n-trial台账 | 模块 | `src/zephyr/backtest/core/n_trial_ledger.py:179` |
| V05 | p0_money_path | P0 | 决策闸DecisionGate | 闸门 | `src/zephyr/backtest/core/decision_gate.py:539` |
| V06 | p0_money_path | P0 | 过拟合裁决器 | 闸门 | `src/zephyr/backtest/core/overfitting_adjudicator.py:514` |
| V07 | p0_money_path | P0 | DSR计算器 | 算法 | `src/zephyr/simulation/deflated_sharpe_calculator.py:327` |
| V08 | p0_money_path | P0 | 过拟合保护闸 | 闸门 | `src/zephyr/simulation/overfitting_protection_gate.py:138` |
| C01 | p0_money_path | P0 | 日度资金分配编排 | 管线 | `src/zephyr/pf_alloc/allocation_orchestrator.py:686 + batched_position_builder.py:240` |
| C02 | p0_money_path | P0 | 多策略资金分配器 | 算法 | `src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py:156` |
| C03 | p0_money_path | P0 | 持仓裁决中心 | 闸门 | `src/zephyr/position/core/position_adjudication_center.py:192` |
| C04 | p0_money_path | P0 | 仓位定位引擎(Kelly) | 算法 | `src/zephyr/position/core/position_sizing_engine.py:379` |
| C05 | p0_money_path | P0 | 现金台账+划拨账本 | 模块 | `src/zephyr/position/core/cash_manager.py:153(:452)` |
| C06 | p0_money_path | P1 | 危机闸CrisisGate | 闸门 | `src/zephyr/pf_alloc/crisis_gate.py:413(:193/:265)` |
| C07 | p0_money_path | P0 | VolTargetAllocator(L1总闸) | 闸门 | `src/zephyr/pf_alloc/core/vol_target_allocator.py:32` |
| X01 | p0_money_path | P0 | 交易会话编排器 | 管线 | `src/zephyr/ex_core/trading_session.py:287` |
| X02 | p0_money_path | P0 | 订单管理器+执行Saga | 模块 | `src/zephyr/ex_core/order_manager.py:131 + order_execution_saga.py:320` |
| X03 | p0_money_path | P0 | 执行引擎 | 管线 | `src/zephyr/ex_core/execution_engine.py:129` |
| X04 | p0_money_path | P0 | SOR算法执行引擎 | 管线 | `src/zephyr/ex_sor/core/algo_trading_engine.py:749` |
| X05 | p0_money_path | P0 | 执行前置闸门组+价格笼子 | 闸门 | `src/zephyr/ex_core/pre_execution_checker.py:147 + price_cage.py:153` |
| X06 | p0_money_path | P0 | TWAP拆单器 | 算法 | `src/zephyr/ex_core/order_splitter.py:213` |
| X07 | p0_money_path | P0 | 成交回报处理 | 模块 | `src/zephyr/ex_core/fill_handler.py:182` |
| X08 | p0_money_path | P0 | 券商柜台文件桥 | 模块 | `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:319` |
| X09 | p0_money_path | P0 | 打板执行+瞬时熔断 | 闸门 | `src/zephyr/ex_core/daban_execution.py:59 + daban_instant_circuit_breaker.py:40` |
| R01 | p0_money_path | P0 | 风控分层编排器(盘中对账) | 管线 | `src/zephyr/ex_core/risk_layer_orchestrator.py:453(start_reconcile_loop:1781)` |
| R02 | p0_money_path | P0 | 持仓对账器(ex_core) | 模块 | `src/zephyr/ex_core/position_reconciler.py:101` |
| R03 | p0_money_path | P0 | 三流对账+日终对账 | 管线 | `src/zephyr/trading/three_way_reconciliation.py:175 + ex_core/eod_reconciliation.py:95` |
| R04 | p0_money_path | P0 | 结算对账链 | 管线 | `src/zephyr/trading/post_settlement_pipeline.py:101 + settlement_reconciliation.py:174 + recon_runner.py:392` |
| R05 | p0_money_path | P0 | 盈亏与费用计算 | 算法 | `src/zephyr/trading/pnl_calculator.py:206(:176 AShareFeeCalculator)` |
| K01 | p0_money_path | P0 | KillSwitch清仓链 | 闸门 | `src/zephyr/risk/stop_loss.py:98(:282/:545)` |
| K02 | p0_money_path | P0 | KillSwitch编排器 | 闸门 | `src/zephyr/autonomy_core/kill_switch_orchestrator.py:259` |
| K03 | p0_money_path | P0 | 交易总停止闸StopGate | 闸门 | `src/zephyr/trading/stop_gate.py:40` |
| K04 | p0_money_path | P0 | 风控否决引擎 | 闸门 | `src/zephyr/risk/core/risk_veto_engine.py:111(:138-217内置规则)` |
| K05 | p0_money_path | P0 | VaR计算器 | 算法 | `src/zephyr/risk/core/var_calculator.py:233` |
| K06 | p0_money_path | P0 | A股止损规则引擎 | 闸门 | `src/zephyr/risk/core/ashare_stop_loss_engine.py:286` |
| K07 | p0_money_path | P0 | 回撤控制器 | 闸门 | `src/zephyr/position/core/drawdown_controller.py:329` |
| K08 | p0_money_path | P0 | 先报告后交易闸 | 闸门 | `src/zephyr/compliance/compliance_report_registry.py:133` |
| K09 | p0_money_path | P1 | 清仓执行保护 | 闸门 | `src/zephyr/risk/core/drawdown_liquidation_guard.py:108(:164)` |
| D01 | p1_decision_chain | P0 | RegimeDetector(HMM四态) | 算法 | `src/zephyr/regime/core/regime_detector.py:437(detect:510)` |
| D02 | p1_decision_chain | P1 | 锚定状态机 | 算法 | `src/zephyr/regime/core/anchored_state_machine.py:142` |
| D03 | p1_decision_chain | P1 | 机构Regime评分器 | 算法 | `src/zephyr/regime/institutional_regime_scorer.py:134` |
| D04 | p1_decision_chain | P1 | 市场预测融合 | 算法 | `src/zephyr/regime/market_forecast_fusion.py:98` |
| D05 | p1_decision_chain | P0 | Regime特征构建器 | 管线 | `src/zephyr/regime/regime_feature_builder.py:124` |
| D06 | p1_decision_chain | P1 | 筹码分布引擎 | 引擎 | `src/zephyr/regime/features/chip_distribution_engine.py:287(:194)` |
| D07 | p1_decision_chain | P2 | LPPL顶部探测 | 算法 | `src/zephyr/regime/features/lppl_detector.py:123` |
| D08 | p1_decision_chain | P1 | 合成VIX | 算法 | `src/zephyr/regime/features/synthetic_vix.py:106` |
| D09 | p1_decision_chain | P2 | Wyckoff引擎(regime) | 引擎 | `src/zephyr/regime/features/wyckoff_engine.py:297` |
| D10 | p1_decision_chain | P1 | 指数Regime面板 | 管线 | `src/zephyr/regime/index_regime_panel.py:269` |
| D11 | p1_decision_chain | P1 | Overlay信号构建 | 管线 | `src/zephyr/regime/overlay_signals_builder.py:143` |
| D12 | p1_decision_chain | P1 | 风险信号构建 | 管线 | `src/zephyr/regime/risk_signal_builder.py:71` |
| D13 | p1_decision_chain | P2 | 周期分析器 | 算法 | `src/zephyr/regime/regime_cycle_analyzer.py:182` |
| D14 | p1_decision_chain | P2 | 风格Regime模型 | 算法 | `src/zephyr/regime/style_regime_model.py:64` |
| D15 | p1_decision_chain | P2 | 波动率告警器 | 算法 | `src/zephyr/regime/volatility_regime_alerter.py:112` |
| W01 | p1_decision_chain | P0 | 信号合成器 | 算法 | `src/zephyr/pf_alloc/core/signal_synthesis_combiner.py:209` |
| W02 | p1_decision_chain | P0 | Regime BMA加权 | 算法 | `src/zephyr/pf_alloc/core/regime_bma_weighting.py:122` |
| W03 | p1_decision_chain | P0 | Regime元分配器 | 算法 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py:199` |
| W04 | p1_decision_chain | P1 | 策略相关性闸 | 闸门 | `src/zephyr/pf_alloc/core/strategy_correlation_gate.py:220` |
| W05 | p1_decision_chain | P1 | 风险预算分配 | 算法 | `src/zephyr/pf_alloc/core/risk_budget_allocator.py:29(:69/:79)` |
| W06 | p1_decision_chain | P2 | 尾部对冲信号 | 算法 | `src/zephyr/pf_alloc/core/tail_hedge_signal.py:27` |
| W07 | p1_decision_chain | P1 | 回撤限额分配 | 闸门 | `src/zephyr/pf_alloc/core/maxdd_limit_allocator.py:88` |
| B01 | p1_decision_chain | P0 | 事件驱动回测引擎 | 引擎 | `src/zephyr/backtest/implementations/event_driven_engine.py:102` |
| B02 | p1_decision_chain | P0 | 向量化回测引擎 | 引擎 | `src/zephyr/backtest/implementations/vectorized_engine.py:160` |
| B03 | p1_decision_chain | P0 | 撮合引擎 | 引擎 | `src/zephyr/backtest/core/matching_engine.py:152` |
| B04 | p1_decision_chain | P0 | 回测数据装配器 | 引擎 | `src/zephyr/backtest/core/data_handler.py:68(:496 MultiSource)` |
| B05 | p1_decision_chain | P0 | PIT管理器 | 闸门 | `src/zephyr/backtest/core/pit_manager.py:74` |
| B06 | p1_decision_chain | P1 | Tick重放器 | 引擎 | `src/zephyr/backtest/core/tick_replay.py:70` |
| B07 | p1_decision_chain | P2 | CH Tick重放器 | 引擎 | `src/zephyr/backtest/implementations/ch_tick_replay.py` |
| B08 | p1_decision_chain | P1 | WalkForward分析器 | 算法 | `src/zephyr/backtest/core/walk_forward.py:88` |
| B09 | p1_decision_chain | P1 | CPCV切分 | 算法 | `src/zephyr/backtest/core/cpcv.py:64` |
| B10 | p1_decision_chain | P1 | 策略CPCV矩阵 | 管线 | `src/zephyr/backtest/core/strategy_cpcv_matrix.py:83` |
| B11 | p1_decision_chain | P1 | 成本归因 | 引擎 | `src/zephyr/backtest/core/cost_attribution.py:148` |
| B12 | p1_decision_chain | P0 | 成本模型校准 | 引擎 | `src/zephyr/backtest/core/cost_model_calibration.py:77(:198)` |
| B13 | p1_decision_chain | P1 | 验证方法学runner | 管线 | `src/zephyr/trading/validation/runner.py:480` |
| B14 | p1_decision_chain | P2 | 回测预检器 | 闸门 | `src/zephyr/backtest/core/preflight_checker.py:50` |
| B15 | p1_decision_chain | P1 | 策略验证管线 | 管线 | `src/zephyr/backtest/core/strategy_validation_pipeline.py:67` |
| B16 | p1_decision_chain | P1 | C1收缩对比runner | 管线 | `src/zephyr/backtest/regime_validation/c1_runner.py:96` |
| B17 | p1_decision_chain | P2 | C4 DSR runner | 管线 | `src/zephyr/backtest/regime_validation/c4_deflated_sharpe_runner.py:62` |
| F01 | p1_decision_chain | P0 | Alpha信号管线 | 管线 | `src/zephyr/signal_fundamental/pipeline.py:102` |
| F02 | p1_decision_chain | P1 | 因子工厂阶段闸 | 引擎 | `src/zephyr/factor/factor_factory.py:78(:160)` |
| F03 | p1_decision_chain | P1 | WQ Alpha87算子库 | 引擎 | `src/zephyr/factor/wq_alpha_87.py:91` |
| F04 | p1_decision_chain | P1 | UFL确定性分层 | 闸门 | `src/zephyr/factor/ufl_deterministic_layer.py:70(:84)` |
| F05 | p1_decision_chain | P0 | 技术指标注册引擎 | 引擎 | `src/zephyr/factor/technical_indicators/indicator_base.py:175(:254)` |
| S01 | p1_decision_chain | P0 | 水温传感器五档 | 算法 | `src/zephyr/signal_ashare/core/daily_condition_sensor.py:45` |
| S02 | p1_decision_chain | P0 | 板块强度聚合器 | 算法 | `src/zephyr/signal_ashare/core/sector_strength_aggregator.py:85(:139)` |
| S03 | p1_decision_chain | P0 | 个股精评分引擎 | 算法 | `src/zephyr/signal_ashare/fine_scoring_engine.py:52` |
| S04 | p1_decision_chain | P1 | 主线概率 | 算法 | `src/zephyr/signal_ashare/mainline_probability.py:111` |
| S05 | p1_decision_chain | P1 | 市场九宫格传感 | 算法 | `src/zephyr/signal_ashare/market_state_sensor.py:90(:110)` |
| S06 | p1_decision_chain | P1 | 个股信号强度 | 算法 | `src/zephyr/signal_ashare/stock_signal_strength.py:82` |
| S07 | p1_decision_chain | P1 | 缠论结构识别 | 算法 | `src/zephyr/signal_ashare/chanlun_structure.py:78` |
| S08 | p1_decision_chain | P1 | 粗筛漏斗 | 管线 | `src/zephyr/signal_ashare/screening/coarse_screening_funnel.py:44` |
| S09 | p1_decision_chain | P2 | 趋势线支撑压力 | 算法 | `src/zephyr/signal_ashare/trendline_sr_detector.py:63` |
| S10 | p1_decision_chain | P2 | 指数共振评分 | 算法 | `src/zephyr/signal_ashare/index_resonance_scorer.py:92` |
| S11 | p1_decision_chain | P2 | 机构行为分析器 | 算法 | `src/zephyr/signal_ashare/institutional_behavior_analyzer.py:93` |
| S12 | p1_decision_chain | P2 | 市场生命周期相位 | 算法 | `src/zephyr/signal_ashare/market_lifecycle_phase.py:97` |
| M01 | p1_decision_chain | P0 | 次日概率闸 | 闸门 | `src/zephyr/signal_ashare/ml_forecast/next_day_probability_gate.py:90(:172)` |
| M02 | p1_decision_chain | P1 | 次日八态预测 | 算法 | `src/zephyr/signal_ashare/ml_forecast/next_day_8state_forecast.py:78` |
| M03 | p1_decision_chain | P1 | 条件密度预测 | 算法 | `src/zephyr/signal_ashare/ml_forecast/conditional_density_predictor.py:56` |
| M04 | p1_decision_chain | P1 | 保形预测族 | 算法 | `src/zephyr/signal_ashare/ml_forecast/conformal_predictor.py:54(+tcp_rm/adaptive两变体)` |
| T01 | p1_decision_chain | P0 | TDM决策地图加载校验 | 闸门 | `src/zephyr/trading/decision_map.py:348(:215/:230)` |
| T02 | p1_decision_chain | P0 | 策略intake准入 | 闸门 | `src/zephyr/strategy_pipeline/intake.py:263(fdr_gate:80)` |
| T03 | p1_decision_chain | P0 | 日度决策编排器 | 管线 | `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:582` |
| T04 | p1_decision_chain | P1 | 生命周期FSM | 状态机 | `src/zephyr/strategy_pipeline/lifecycle_fsm.py:112(:75 SimPromotionGuard)` |
| T05 | p1_decision_chain | P1 | 前向回测窗口/指纹 | 管线 | `src/zephyr/strategy_pipeline/fw_backtest.py:132` |
| T06 | p1_decision_chain | P2 | 晋升建议器 | 管线 | `src/zephyr/strategy_pipeline/promotion_advisory.py:110` |
| G01 | p1_decision_chain | P1 | 基本面信号合成器 | 算法 | `src/zephyr/signal_fundamental/synth/signal_synthesizer.py:58` |
| G02 | p1_decision_chain | P1 | 基本面选股漏斗 | 管线 | `src/zephyr/signal_fundamental/selection_funnel.py:93` |
| G03 | p1_decision_chain | P0 | 负面事实否决闸 | 闸门 | `src/zephyr/signal_fundamental/negative_veto.py:42` |
| E01 | p1_decision_chain | P0 | 卖出信号融合引擎 | 算法 | `src/zephyr/sell_decision/core/sell_signal_fusion_engine.py:159` |
| E02 | p1_decision_chain | P1 | 卖出信号评分器 | 算法 | `src/zephyr/sell_decision/core/sell_signal_scorer.py:68(:92)` |
| E03 | p1_decision_chain | P1 | 止损策略(sell) | 算法 | `src/zephyr/sell_decision/core/stop_loss_strategy.py:121(:131)` |
| E04 | p1_decision_chain | P1 | 买卖冲突仲裁器 | 闸门 | `src/zephyr/sell_decision/core/sell_conflict_arbitrator.py:118(:146)` |
| E05 | p1_decision_chain | P1 | 持仓分诊 | 算法 | `src/zephyr/sell_decision/core/position_triage.py:72` |
| E06 | p1_decision_chain | P2 | 分批卖出 | 算法 | `src/zephyr/sell_decision/core/scaling_out.py` |
| T08 | p1_decision_chain | P1 | TDM全图对账 | 对账 | `docs/01_policies_and_standards/alignment_checklist.md + config/trading_decision_map.yaml` |
| I01 | p2_infra | P1 | IntegratorScheduler主调度 | 调度 | `src/zephyr/data/scheduler.py:449` |
| I02 | p2_infra | P1 | 调度监控+metrics | 调度 | `src/zephyr/data/scheduler.py:2429(monitor:2387,锁:86)` |
| I03 | p2_infra | P2 | 数据CLI | 管线 | `src/zephyr/data/cli.py:333(:390 main)` |
| I04 | p2_infra | P2 | DataService查询服务 | 管线 | `src/zephyr/data/data_service.py:96(:257)` |
| I05 | p2_infra | P1 | Provider基类+能力契约 | 管线 | `src/zephyr/data/provider_base.py:202(:106/:58/:79)` |
| I06 | p2_infra | P1 | QMT桥采集Provider | 管线 | `src/zephyr/data/implementations/qmt_bridge_provider.py:156` |
| I07 | p2_infra | P1 | Tick订阅器 | 管线 | `src/zephyr/data/tick_subscriber.py:225(:1453)` |
| I08 | p2_infra | P1 | ch_writer统一写入 | 存储 | `src/zephyr/data/ch_writer.py:757/:818/:832(get_client:153)` |
| I09 | p2_infra | P2 | ch_reader只读查询 | 存储 | `src/zephyr/data/ch_reader.py:95` |
| I10 | p2_infra | P2 | 缓冲写入器 | 管线 | `src/zephyr/data/buffered_writer.py:62` |
| I11 | p2_infra | P2 | 缺口探测 | 管线 | `src/zephyr/data/backfill_checker.py:176` |
| I12 | p2_infra | P2 | 自动补下载器 | 管线 | `src/zephyr/data/auto_backfiller.py:118(:85)` |
| I13 | p2_infra | P2 | 补跑守卫 | 调度 | `src/zephyr/data/catchup_guard.py:168(锁:91)` |
| I14 | p2_infra | P2 | 完整性巡检 | 管线 | `src/zephyr/data/integrity_checker.py:253(:204)` |
| I15 | p2_infra | P2 | 一致预期交叉验证 | 管线 | `src/zephyr/data/consensus_crosscheck.py` |
| I16 | p2_infra | P3 | 双源交叉验证 | 管线 | `src/zephyr/data/cross_source_validator.py:105` |
| I17 | p2_infra | P2 | 数据源策略注册 | 管线 | `src/zephyr/data/policy_registry.py:188(:49)` |
| I18 | p2_infra | P3 | capability语义/符号门 | 管线 | `src/zephyr/data/capability_semantic_gate.py:177 + capability_symbol_gate.py:286` |
| I19 | p2_infra | P2 | 任务水位存储 | 存储 | `src/zephyr/data/progress_store.py:57` |
| I20 | p2_infra | P2 | 数据域告警出口 | 管线 | `src/zephyr/data/alerter.py:65` |
| I21 | p2_infra | P3 | CH parts监控 | 管线 | `src/zephyr/data/ch_parts_monitor.py:119(:165)` |
| I22 | p2_infra | P3 | 分钟K重采样 | 管线 | `src/zephyr/data/kline_resampler.py:172` |
| I23 | p2_infra | P2 | 本地降级回放 | 存储 | `src/zephyr/data/local_replay.py:80` |
| I24 | p2_infra | P2 | DatabaseService | 存储 | `src/zephyr/infrastructure/database_service.py:86(:365)` |
| I25 | p2_infra | P1 | CH DDL部署器 | 存储 | `scripts/ch/apply_market_tables_ddl.py:1084(:1150,main:1197)` |
| I26 | p2_infra | P2 | 面板API服务 | 前端 | `src/zephyr/frontend/dashboard/api_server.py:56(uvicorn:4449)` |
| I27 | p2_infra | P3 | 运维控制台面板 | 前端 | `src/zephyr/frontend/dashboard/app_panel.py:170(:489)` |
| I28 | p2_infra | P3 | 旧版dashboard装配 | 前端 | `src/zephyr/frontend/dashboard/app.py:74(:128)` |
| I29 | p2_infra | P1 | GitCommitGateway+提交队列 | 基建 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py + scripts/commit_queue.py` |
| I30 | p2_infra | P2 | 提交门禁链own-scope机制 | 基建 | `src/zephyr/gov_enforcement/commit_gates/ + gate_registry.yaml` |
| TF01 | p2_infra | P1 | intraday_realtime盘中实时族(16任务) | 自动化任务族 | `tasks.yaml:143-2944` |
| TF02 | p2_infra | P1 | intraday_minute分钟K族(16任务) | 自动化任务族 | `tasks.yaml:287-481` |
| TF03 | p2_infra | P1 | intraday_sector板块分钟族(5任务) | 自动化任务族 | `tasks.yaml:2147-2207` |
| TF04 | p2_infra | P1 | auction_highfreq竞价族(2任务) | 自动化任务族 | `tasks.yaml:1720,:1732` |
| TF05 | p2_infra | P2 | event_driven事件族(11任务) | 自动化任务族 | `tasks.yaml:158-2810` |
| TF06 | p2_infra | P2 | news_slow慢新闻族(2任务) | 自动化任务族 | `tasks.yaml:1201,:1298` |
| TF07 | p2_infra | P1 | daily_kline盘后日K族(31任务) | 自动化任务族 | `tasks.yaml:22-3127` |
| TF08 | p2_infra | P2 | pre_market盘前族(8任务) | 自动化任务族 | `tasks.yaml:1378-2989` |
| TF09 | p2_infra | P2 | daily_capital盘后资金族(29任务) | 自动化任务族 | `tasks.yaml:107-2869` |
| TF10 | p2_infra | P2 | daily_event盘后事件族(39任务) | 自动化任务族 | `tasks.yaml:557-3165` |
| TF11 | p2_infra | P2 | research_nightly研报族(2任务) | 自动化任务族 | `tasks.yaml:581,:594` |
| TF12 | p2_infra | P2 | nightly_financial夜间财务族(10任务) | 自动化任务族 | `tasks.yaml:95-1912` |
| TF13 | p2_infra | P2 | crypto+alt_fx币圈外汇族(3任务) | 自动化任务族 | `tasks.yaml:820,:833,:3189` |
| TF14 | p2_infra | P2 | weekend_calibration周末校准族(41+1任务) | 自动化任务族 | `tasks.yaml:810-3177,:2071` |
| TF15 | p2_infra | P3 | monthly_static月度静态族(20任务+1停用) | 自动化任务族 | `tasks.yaml:932-2102,:676` |


## 补册记录（T08 对账，2026-09-18）
- TDM 138 节点对账：115 有 module_ref，去重后 78 个模块未入册；2 个与已审对象重复（kill_switch→K02、price_cage→X05），实补 **76 行**（P01-P76，p1_decision_chain）。
- 台账总行数 235；P 系列为计划引擎/板块族/卖出执行/做T/持仓体检等 TDM 决策链环节。
