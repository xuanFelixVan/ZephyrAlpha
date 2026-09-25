---
ttl: task_bound
---

# M7-04 · ex_core 骨架与订单生命周期（打板族 + ex_order 流转链）

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿（禁启终端/禁下单/禁连真实账户）
> 边界：桥面（adapters 5 件）→01 册；risk_layer/pre_execution_checker→02 册；position/sell 三件→03 册；programmatic_trading_guard 合规面→06 册。本册挖 ex_core 骨架、订单生命周期全流转与打板（daban）执行族。
> 术语注：任务书"ex_order 流转链"经 ls 实勘无 ex_order 包——订单生命周期真身=order_manager（MOD-L06-001）+订单契约 shared/contracts/order，本册即按此挖掘。

## 一、环节定义与边界
ex_core=D_EXECUTION_CORE 执行核心域（56 件，顶层 16,875 行）：订单从信号 delta 到券商回报的全生命周期骨架（创建→校验→提交→成交/拒单/过期→报告→审计），外加打板（daban）专用执行族。上游=策略权重（pf_core sleeves）/信号族（供料），下游=QMT 桥（01 册）落地、execution_report→D_REPORTING（消费）。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | 策略权重面板（daban_sleeve_strategy 等 `pf_core/strategies/`，经 StrategyRegistry）；TradingSession.rebalance（`trading_session.py:514`）；signal_providers（`signal_providers.py`，消费方 trading_session） |
| 下游消费 | broker.submit_order→QMT 桥（01 册）；Fill→_on_fill（`order_manager.py:531`）→fill_callbacks 链；ExecutionReport→D_REPORTING（`execution_report.py:22` CTR-P1-007）；audit_journal→operational_risk_monitor/default_risk_manager_orchestrator（`risk/core/` 两消费实证） |
| 自动化触发 | 盘中=rebalance 事件触发（`ex_core.rebalance.requested`，B4 治本删 Timer）；盘后=eod_reconciliation 15:40 槽（03 册，内含 `expire_open_orders:196` 日终未成交转 EXPIRED）；打板日频批产=daban_load_producer.run_daily_batch（T3⑧）；premarket_checker 挂 boot_hooks（MOD-INF-035） |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_execution_core/（blueprint.md+11 子目录+algo_flow/）；包入口=MOD-L06-001（`ex_core/__init__.py:1-20` 懒加载聚合）；策略真源=docs/_working/archive/2026-09/design_memos/24_daban_strategy_detail.md（缺失#1-#12 编号体系）；模块注册=depgraph MOD-EX-001/057 等 |
| 门禁与质量尺 | 订单状态机 VALID_TRANSITIONS 白名单（`order_manager.py:136-150`，非法转换抛 ValueError）；Saga 六步严格序+补偿幂等+≤5s 超时（`order_execution_saga.py` INVARIANTS）；整手/价格笼子（board_lot/price_cage，消费方含两 broker）；幂等键 sha256 确定性（`order_manager.py:267-272`，R-L3 治 uuid4 重放）；daban PIT 铁律 INV-004（龙虎榜 T-1） |
| 当前运行状态 | **黄**：主链（rebalance→delta→提交→成交→报告）sim 实弹绿（09-23 卖腿实证，01/03 册）；骨架自身=绿（54 测试件 tests/ex_core/）；**打板执行族=红（零实盘消费者，G22 执行层落线前）**；执行微结构算法族=design-in-code（有意冻结，见 B2） |

## 三、子模块清单（56 件全勘，剔除跨册 14 件后本册 42 件；ls+grep+头注 CONSUMERS 三源交叉）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| order_manager | 订单生命周期本体：create(:257 幂等键 R-L3)→submit(:323 报单即 record_submit)→transition(:296 白名单)→cancel(:419/:445 record_cancel)→on_fill(:531)→expire(:505)→拒单分类(:315 xttrader error_code→RETRY/ABANDON) | order_manager.py:133 | production，**全仓 6 处裸构造零合规注入**（见 06 册 B1） |
| trading_session | 会话编排主梯：rebalance:514→_do_rebalance:519→_evaluate_risk_layer:556→_apply_position_cap:583→_compute_order_deltas:636→_build_order:738→_validate_and_submit:758（内嵌风控/预执行/合规/熔断四道闸 :908/:942/:979/:1124）→_on_fill:1182→_handle_rejection:1085 | trading_session.py:296 | production（闸面细节归 02/06 册） |
| order_execution_saga | 六步 Saga（风控→信号确认→下单→成交等待→持仓更新→报告），补偿：步3败撤单/步5败反向 apply_fill/步4超时撤单败强制查终态补走 5/6（#ARCH-100 吞成交修复） | order_execution_saga.py:320（六步 :522-744，超时恢复 :771-886） | production 级代码，**零生产调用方**（grep 全仓唯 self+rejection_action_handler 引用；TradingSession 走自有 _validate_and_submit 直连路径）——见 B1 |
| local_order_queue | 本地订单队列节流（qmt_sim 间隔 180s 示例） | local_order_queue.py:84 | production，**已接线**（qmt_file_bridge_integration.py:165） |
| rejection_action_handler | 拒单动作执行器（Saga 接管后归口；未注入=仅日志不自动重试） | rejection_action_handler.py:8 | 在；与 Saga 同绑（零生产调用） |
| cancel_rate_guard | 撤单率/限频/日申报三合一计数器（500 完结窗/12% 警/15% 冻/15 笔秒限/5000 警 1 万阻/冷启动<20 样本 NORMAL） | cancel_rate_guard.py:88-108 | production；TradingSession 兜底自建（`trading_session.py:347`） |
| fill_handler | 成交入账处理器（重复成交/非法成交/订单缺失三异常） | fill_handler.py:187 | production，**已接线**（scripts/run_post_settlement.py:273,429 回放+aggregate_root_manager:156） |
| async_fill_dispatcher | 成交异步派发（回调内只入队，会话 stop 排空） | async_fill_dispatcher.py | production，**已接线**（start_paper_session assemble_risk_layer） |
| execution_report / execution_report_producer | 成交报告契约（CTR-P1-007 frozen）+生产端（柜台轮询装配） | execution_report.py:22；execution_report_producer.py:157 | production，**已接线**（qmt integration:153-160，E4 默认开，01 册） |
| audit_journal.auditor | 执行审计日志（Saga 步6 消费；ExecutionAuditReport→D-REPORTING/D-GOVERNANCE） | audit_journal/auditor.py | 在；生产耦合面=Saga（零调用→传递休眠）+risk 两件直接消费报告 schema |
| **打板族 8 件**（24 号文缺失#1-#12 逐条施工） | | | |
| daban_named_functions | 8 具名函数：梯队健康四档/连板高度死亡池/竞价三维/纸老虎否决/封单结构/次日溢价/反核板/量化席位降权（§3.1/3.9/3.11） | daban_named_functions.py:8-14 | production；消费者=自族 |
| daban_signal_decision | 前置门控 pre_validate（≥70 放行/50-70 降仓/<50 否决）+classify_decision_v192 七类决策（情绪周期 PHASE_THRESHOLDS 冰点20/反核40/主升40/疯狂65/退潮85 事实禁板） | daban_signal_decision.py:26-30 | production；消费者=daban_pit_safety 主循环 |
| daban_execution | 分笔建仓三件：ExecutionAlgorithm（60/30/opportunistic 三段+SaR>2% 削 30%+Hawkes 封单核）/TimingDecision（追板 vs 埋伏）/CapacityCalculator（四约束取最小） | daban_execution.py:8-21 | production 头注；**消费者=无（G22 执行层落线后 sleeve 组装）**——见 B3 |
| daban_exit_decision | T+1 出场：NextDayExitDecision（硬退三件+高开两档止盈+分歧软退+晋级持有）+reflush 次日出场 | daban_exit_decision.py:1-7 | production；消费者=pit_safety |
| daban_instant_circuit_breaker | sleeve 级盘中瞬时熔断（封单崩塌级联，三触发器→瞬时卖出；与账户级 Kill Switch 并列优先级更高） | daban_instant_circuit_breaker.py:1-5 | production；消费者=无（挂实盘接线） |
| daban_monitors | 持仓期微观结构持续监控+渐进降仓（#9）/信号失效分级 OK→REDUCE→STOP（#6） | daban_monitors.py:1-5 | production；消费者=无（挂实盘接线） |
| daban_pit_safety | 龙虎榜 PIT 边界（T 日盘中只用 T-1 榜，INV-004 未来函数双保险）+PIT 回测框架（唯一装配打板决策链主循环处） | daban_pit_safety.py:3-5 | production（回测面） |
| daban_load_producer | 四引擎负载日频批产真源→c1_market.daban_engine_load；daban_sleeve_strategy PIT 真读（LUE-1 治本：权重有输入没有的空转修复） | daban_load_producer.py:1-8 | production，**已闭环**（pf_core/strategies/daban_sleeve_strategy.py:4 消费实证） |
| **执行微结构族（design-in-code 有意冻结）** | | | |
| execution_engine | 算法执行引擎（懒加载 ex_sor AlgoTradingEngine，G7 AlgoType 映射） | execution_engine.py:129 | **零生产实例化**（唯 risk_validation_bridge docstring 示例+demo 脚本）——B2 |
| execution_strategy_selector / order_splitter | 算法选择（TWAP/VWAP/ICEBERG）/拆单切片；CONSUMERS=MOD-EX-014/062 设计编号 | execution_strategy_selector.py:5；order_splitter.py:5 | design-in-code（90 号裁定：个人量级 TWAP 远期降级） |
| execution_param_optimizer | 执行参数周期优化提案（人工确认通道） | execution_param_optimizer.py:5 | 零生产装配 |
| open_order_resolver / trading_halt_resolver / post_close_pricing | 未成交单治理（紧急度五档）/停牌处理/尾盘清退（40 号 §2.12 Phase 1.5） | open_order_resolver.py:5；trading_halt_resolver.py:5；post_close_pricing.py:5 | 三件链零装配（resolver 唯一消费链=halt resolver，均休眠） |
| board_lot / price_cage / pricing_policy / corporate_action_adjuster | A 股整手/价格笼子/定价分层/公司行动调整四件微结构守卫 | 各文件头 CONSUMERS 列双 broker+trading_session | production **已接线**（经 qmt broker 预校验，01 册 ：524-545 实证） |
| **骨架/契约件** | | | |
| aggregate_root_manager / repository_interface | 聚合根+仓储接口（Stage 2 集成预留） | aggregate_root_manager.py:5；repository_interface.py:5 | **零消费者**（grep 全仓除 self/test 零命中）——内收候选见 B4 |
| multi_contract_adapter | 契约注册中心（D_GOVERNANCE 消费面） | multi_contract_adapter.py:3 | 在（包入口显式导出 `__init__.py:21`） |
| signal_providers | 信号供给抽象（mock/xtdata） | signal_providers.py:4 | production（trading_session 消费） |
| live_strategy_adapter | 常驻服务化（StrategySlot+监督重启+biz 心跳；57 号文 GAP-2 CLI 已落） | live_strategy_adapter.py:5 | production；挂计划任务=Owner 窗口（M5 面未挂） |
| services/live_portfolio | 组合视图（持仓/可用/净值→前端看板） | services/live_portfolio.py:3 | production（TradingSession+前端消费） |
| premarket_checker | 盘前检查清单（boot_hooks 事件订阅消费） | premarket_checker.py:5 | production |
| performance_monitor | 执行性能监控 | performance_monitor.py（CONSUMERS 空） | **零消费者零装配**——B4 |
| rules/{base,ashare,crypto} | 市场规则族（ashare=production，crypto=研究域在盘未接） | rules/ | ashare 在；crypto 不挖（总筹裁定） |

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **双执行编排并存：Saga 六步（带补偿/超时恢复/审计）vs TradingSession._validate_and_submit 直连（无补偿语义）**。Saga production 级代码零生产调用（本班 grep 独立复证）；拒单分类/撤单终态保护等安全语义在两条路径不对称。修法二选一：①session 切换走 Saga（重）；②按内收判据"同域重复簇→收敛唯一"显式降级 Saga 为参照实现+头注声明（轻）。0.5 天（②）/2-3 天（①）；**待裁**（执行编排唯一化方向） |
| B2 | 执行微结构族 7 件（engine/selector/splitter/param_opt/open_order/halt/post_close）design-in-code：与 90 号 §19"个人量级 TWAP/VWAP 远期降级"裁定自洽=**有意冻结**，但仓库头注仍标 production 级/CONSUMERS 指向设计编号，误导接手者。修法=统一头注标 design-frozen+冻结依据指针；0.5 天；可施工 |
| B3 | 打板执行族 4 件（execution/exit/instant_breaker/monitors）零实盘消费者：signal/load/pit 三件已闭环（回测+权重面），执行半边等 G22 执行层落线。sleeve 现在产的是**权重**（走 trading_session delta 普通下单），打板专用三段分笔/瞬时熔断/持续监控全未挂。修法=G22 装配批把 daban_execution 经 sleeve→session 注入或专项执行腿；1-2 天；挂 G22（M7 施工+Owner 排期） |
| B4 | 零消费者件群（aggregate_root_manager/repository_interface/performance_monitor/execution_param_optimizer）：阶段 2 预留长期未兑现。修法=季度内收审计按"零触发零消费→退役"处置或兑现排期；审计项；归内收季度窗 |
| B5 | app_panel.py:524 前端面板自持第三只 OrderManager() 裸实例——与 session/桥实例互不相通（订单数据三面分裂+合规门零注入第三处）。修法=面板改只读视图消费 live_portfolio；0.5 天；可施工（涉前端联调） |

## 五、提速与合并机会
- 打板族 8 件+蓝图 12 缺失编号一一对应，文档↔代码映射已天然成册：algo_flow/*.yaml 已机生（各文件 [ALGO_FLOW] 行），无需另建清单（净零纪律：本册不新增注册表，只指针化）。
- Saga vs session 编排二选一后，rejection_action_handler/fill 超时恢复语义单源化，删一半测试维护面。

## 六、自审闸三态
**挖干可施工**（56 件 ls+头注+消费 grep 三源穷尽；订单生命周期全流转 file:line 实证；打板族回测半边闭环/执行半边缺口定位明确）。B1 编排唯一化方向挂待裁，不动摇主体。

## 七、复核命令（10 分钟）
```bash
ls src/zephyr/ex_core/ | wc -l                                        # 56 件对账
sed -n '136,150p' src/zephyr/ex_core/order_manager.py                  # 订单状态机白名单
sed -n '30,50p' src/zephyr/ex_core/order_execution_saga.py             # Saga 六步+补偿规则
grep -rn "OrderExecutionSaga(" src/zephyr scripts --include="*.py" | grep -v test  # B1 零生产调用实证
grep -rln "daban_load_producer" src/zephyr/pf_core/strategies/         # 打板负载闭环实证
grep -n "CONSUMERS" src/zephyr/ex_core/daban_execution.py              # G22 前暂无消费者
grep -n "run_daily_batch\|daban_engine_load" src/zephyr/ex_core/daban_load_producer.py | head -5
```
