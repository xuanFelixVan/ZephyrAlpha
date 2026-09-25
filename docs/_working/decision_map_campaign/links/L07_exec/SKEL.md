---
ttl: task_bound
title: SKEL
doc_type: log
---

# L07 执行链路挖矿作业簿（环节 7 · 下单/滑点/盘口）

> 班次：链路 L07（执行）挖矿班 · 2026-09-25（重发班，前次限流击落）· 只读挖掘+本文件唯一写入；禁 commit；CREATE-GUARD 由总指挥统一登记（同 13 号文先例）。
> 骨架真源：`docs/_working/decision_map_campaign/09_link_skeletons.md:494-553`（环节 7）；运转审计真源=`../../13_trading_chain_audit.md` 环节④+§9 汇总表（TRD-A01..A22 已立 22 项，本文引用不重复）；总纲=`../README.md`。
> 挖掘源已读：`config/trading_decision_map.yaml`（L4-01..14 全节 :2169-2567 + X-S2 :3500-3600）、`src/zephyr/ex_core/`（order_manager/execution_report_producer/execution_engine/price_cage/execution_param_optimizer/execution_strategy_selector/daban_execution 头注全文+qmt_file_bridge_broker 头注+miniqmt_channel_manager）、`src/zephyr/ex_sor/`（algo_trading_engine/algo_execution_selector/execution_scheduler/optimal_order_router/sor_agent/sell_session_router/rl_exec_boundary 头注全文+services 三件 slippage_analyzer/execution_quality_scorer/transaction_cost_optimizer/t0_cost_model 头注）、`src/zephyr/backtest/core/cost_model_calibration.py`（头注+PROVENANCE）、`docs/01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml`（全文）、`src/zephyr/reporting/default_tca_engine.py`、`src/zephyr/trading/three_way_reconciliation.py`、`src/zephyr/pf_core/orderbook_imbalance_strategy.py`+`strategy_runner.py`、`scripts/backtest/sim_daily_runner.py`（bridge-execute 专项）、`scripts/run_sim_bridge_execute_daily.ps1`（全文）、`docs/_working/sim_launch/`（delivery_report_20260923 §3/§4+台账目录）、`docs/_working/trading_vision/2026-09-16-data-sufficiency-matrix.md` L5 行、13 号文环节④全文。
> 探针结论先行（本班新证三条）：①**桥执行腿代码载体不可达**——`git log --all -S "bridge-execute"/"def bridge_execute"` 全分支零命中，dev 工作树 `scripts/backtest/sim_daily_runner.py` 子命令仅 plan-bridge/plan-execute/e4-replay/report/settle 五个，而计划任务 SimBridgeExecute（09:35/13:05）wrapper `scripts/run_sim_bridge_execute_daily.ps1:30` 调 `bridge-execute`；②**`.runtime/logs/sim_bridge_execute.log` 末行=09-23 13:05**，09-24/09-25 四个触发窗零行（skip 与失败日志皆无）——实单腿 09-23 13:05 后静默中断；③**L4-14 断链今日复核仍断**——`grep scorer/quality algo_execution_selector.py` 零命中（2026-09-25，与 yaml L4-14 注"断链实证 2026-09-10"一致未修）。实盘相关结论保守：本文不断言任何"实盘安全"。

---

## §1 子块全树（9 子块）

```
L07 执行（环节7）
├─ EXE-1 信号→订单映射（姿态→动作翻译）…… sim_daily_runner._plan_decision (:518-538 纯函数) + plan_order_mapping_proposal（呈批未批）
├─ EXE-2 委托管线（OMS+预检+笼子）…… order_manager (MOD-L06-001, production) + pre_execution_checker 五级闸 + price_cage
│   └─ 九态机 L4-10/部分成交 L4-11(fill_handler)/硬约束 L4-09/容灾对账 L4-13(three_way_reconciliation MOD-TRADING-013)
├─ EXE-3 QMT 桥客户端（文件桥+HTTP 快路径+桥执行腿）…… qmt_file_bridge_broker (MOD-L06-001-QMTFB, draft)
│   └─ HTTP /order 32ms 快路径 fail-open 降级文件桥；双实例 env=real/sim 物理隔离；SimBridgeExecute 09:35/13:05 wrapper
├─ EXE-4 成交回报链（ExecutionReport 生产端）…… execution_report_producer (E4 断点已闭) → c1_market.execution_report（15 列）
├─ EXE-5 成本反馈 L4-14（三零件+回写断链）…… slippage_analyzer (XS-017) + execution_quality_scorer (XS-018) + transaction_cost_optimizer (XS-019)
│   └─ 断点：selector (XS-011) 不消费 scorer 评分（断链实证 09-10，本班 09-25 复核仍断=D34）
├─ EXE-6 执行算法 TWAP/VWAP/IS（双层并存）…… ex_sor 六算法引擎 (XS-005+XS-011 评分选型+XS-004 调度) ∥ ex_core 分档门禁版 (MOD-EX-062+order_splitter)
│   └─ TWAP/VWAP/ICEBERG/POV/IS(AC 轨迹)/ALT；参与率≤5% 监管硬约束；单笔≤15% ADV；RL 执行=design（XS-008 硬边界已码）
├─ EXE-7 滑点标定 cost_model_calibration（MOD-BT-001, testing）…… 滑点腿(尺寸无关)/冲击腿(AC η·p^β·σ, γ=0)/佣金腿三分
│   └─ PROVENANCE=2026-07-24~09-16 五档快照 13,119,233 条；注册表 CST-ASTOCK-001/002/T0-001/ZERO/CRYPTO 五条目
├─ EXE-8 五档深度与盘口失衡 ………… tick_depth_5（1,883 万行, D36 差约 17 交易日）+ orderbook_imbalance_strategy (MOD-L05-001, 回测态)
└─ EXE-9 卖出执行 X-S2 + 打板执行 … sell_session_router (XS-016, design) + sell_execution_planner (SELL-019) + t1_sellable (POS-028) + daban_execution（SaR/Hawkes/Passive MI 三论文落地）
```

**双层同域并行直观图**：执行算法选择器两套——MOD-XS-011（评分驱动六算法，TDM L4-06 挂点）∥ MOD-EX-062（ADV 分档表只 TWAP/VWAP+限价直发，>15% ADV 拒）；成本真源两套——cost_model_calibration 标定档位（testing）∥ CST-ASTOCK-001 fixed slippage bps=1（active，与标定"现值比实测低 3.8 倍"结论冲突未回写）。**零互认、零收编裁定**（内收 w5_1 同域重复簇，L07-C03/C08）。

---

## §2 六向台账（每子块①上游②原料③输出④消费⑤挂点⑥缺口债）

### EXE-1 信号→订单映射（姿态→动作）

| 向 | 台账 |
|---|---|
| ①上游输入 | 日计划姿态（judgment_daily_plan→plan_bridge 行，`sim_daily_runner.py:557-567` 消费 payload.posture）；五态盘中归类（E2E 四拍实证）；SIM-PLAN-001 plan 钱包状态（:541-546） |
| ②数据原料 | 000300 两日收盘（不追高闸 ret_1d 输入）+510300 收盘价（成交价）；参数=PLAN_ENTRY_FRACTION 30% 额度+NO_CHASE_MAX_RET_1D 1.5%（均"提案可修，Owner 否决删键即 no-op"，commit 28b85901bf 自述）；映射真源=`docs/_working/sim_launch/plan_order_mapping_proposal.md`（批复栏全空）+裁定卡 `01_ruling_plan_mapping_and_orphans.md` |
| ③状态输出 | 六值动作 entry/hold/trim_half/exit/wait/none（:518-538 fail-visible：价格缺失→none 不下单）；sim_trade_log plan_bridge 行+orders 事件行 |
| ④下游消费 | bridge-execute 桥真单腿（EXE-3）；plan-execute 模拟腿（SIM-PLAN-001 建仓 65,055 股 510300@4.608 实弹验证，28b85901bf）；无其他消费方（映射表 Owner 未批=语义空间仅批 1 行，13 号文环节④缺陷 2） |
| ⑤自动化挂点 | 定时（SimBridgeExecute 09:35/13:05 双触发）——**载体断（见 EXE-3⑥）**；事件链 observe 自动在产 |
| ⑥缺口债 | TRD-A09（映射提案批复接线，引用不重复）；"委托裁定与提案批准范围是否同口径"待实查（13 号文环节④缺陷 2）；LEAN 五层"scenario→sizing→订单"中间层现仅隐式（裁定卡口径，无显式 sizing 件） |

### EXE-2 委托管线（OMS+预检+笼子）

| 向 | 台账 |
|---|---|
| ①上游输入 | 已批准动作（EXE-1）；RiskLimits/持仓快照（`qmt_file_bridge_broker.py` DEPENDENCIES 注入）；kill_switch 探针态（闸门 1）；会话窗（09:30-11:25/13:00-14:55，delivery §3） |
| ②数据原料 | 订单九态机（L4-10，PendingCancel 竞态"以交易所回执为准"=invalidation 在案）；价格笼子 2026-07-06 新规（`price_cage.py`：买入基准=卖一、主板±2%+0.1 元兜底/科创严格±2%/北交所±5%，超限**夹到边界不废单**——与交易所"直接废单"新规的差异是夹单语义，头注自洽在案）；成本模型实时估算（L4-09，CST-ASTOCK-001 挂接） |
| ③状态输出 | Order/Fill 契约（CTR-004/CTR-005）；订单事件（SUBMITTED/CANCELLED/EXPIRED 三点发射，FILLED/REJECTED 不发事件——`execution_report_producer.py` 头注实证）；rejection 原因记录 |
| ④下游消费 | broker 适配器（qmt_file_bridge_broker/miqmt）；compliance 操纵冻结闸（`order_manager.py` CONSUMERS=MOD-CMP-018）；execution_report_producer（EXE-4）；fill→持仓更新（BM-EXE-06） |
| ⑤自动化挂点 | 逐单闸自动在产（sim 实证：闸门 1+1.5 fail-closed，trading_session :318,360,472 注入）；three_way_reconciliation 盘后三向对账=**"运行时装配批"自注无装配实证**（:12 CONSUMERS 列，与 MOD-PLAN-021 同病） |
| ⑥缺口债 | T6b 撤单终态不产 execution_report 行（delivery §6 移交③，producer 语义待勘）；无资金占用/购买力闸（13 号文环节④"全不全"如实注）；fill_handler/local_order_queue/order_execution_saga/open_order_resolver/async_fill_dispatcher 正文未读（§3 MINING）；三向对账装配欠账 |

### EXE-3 QMT 桥客户端（文件桥+HTTP 快路径+桥执行腿）——**本班 P0 新证**

| 向 | 台账 |
|---|---|
| ①上游输入 | 桥执行腿=sim_daily_runner bridge-execute（09-23 实弹：10:42 卖 510300 1100 股@4.604，sysid=4820 FILLED，`delivery_report_20260923.md` §3/§59）；柜台 quote（mtime>900s 拒单）；交易日历闸（ps1 is_trading_day fail-closed SKIP） |
| ②数据原料 | 指令 CSV↔哑执行器 v14/v16 文件状态机（#SENDING→#DONE 幂等）；HTTP /order 直投沙箱 EXEC v16.4（中位 32ms，失败 fail-open 降级文件桥，`qmt_file_bridge_broker.py:24-26`）；ack 文件+柜台镜像（CounterStateMirror）；R-H5E-1 sim 进桥风控前置校验（裁定 #338⑤：env=real 不触校验=Owner 门） |
| ③状态输出 | 本地 order_id+broker_order_id 异步回填（sysid 修）；柜台同步（3 秒轮询）；桥监控三件勾选空（`docs/_working/2026-09-08-qmt-bridge-migration-ledger.md` §1 未结案保留） |
| ④下游消费 | order_manager（CONSUMERS 自注）；execution_report_producer 挂点（attach_execution_report_producer，未接线=零行为变更，断点 E4 自注）；台账 bridge_fill_check=1.0（09-24 settle） |
| ⑤自动化挂点 | 计划任务 SimBridgeExecute 09:35/13:05 实测就绪（13 号文探针）——**但 wrapper 守卫后调用的 `bridge-execute` 子命令在 dev 树不存在**（pickaxe 全分支零命中）；wrapper XtItClient 活性守卫+quote 新鲜度闸在产（ps1 :22-27，隔夜单丢弃面 mitigations=裁定 #339 gap-2） |
| ⑥缺口债 | **L07-C01：载体修复**——09-23 实弹批（14+2 文件，delivery §3/57 行清单）代码未落版本库，dev 工作树该文件止于 09-22 版（commit 28b85901bf，09-22 15:48），`.runtime/workspace_alerts/stash_notice.json` 不存在（目录仅 claim_release_request_gpu.json）=无 stash 痕；若 09:35 触发将 argparse invalid-choice 失败（推断，待实查任务日志销号）。另：客户端两缺陷（隔夜单静默丢弃+submit→cancel<5s 竞态 36 合同冻结 16,203.40）=TRD-A10 引用不重复；台账勾选滞后勘误=TRD-A10 附带 | **【09-25 销号注记·桥执行腿修复班】**载体已恢复：死信袋 q-20260923-st-sim-launch-20260923-0002（09-23 18:28 快照）17 件 blob sha256 全验完好，9 件代码/测试（runner+两测试+broker+integration+order_manager+app_panel+position_monitor+pipeline_events）经 CAS safe_write 写回工作树（字节级核验 ALL True，runner 52,736B 含 :863 def bridge_execute）；bridge-execute --help 过+runner 28/pipeline 38 套件绿（与 delivery §3 口径一致）+wrapper :76 调用复效；根因=09-23 批 7 次入队 6 死 1 窄批（0001 注册表三向合并/0002 COMPLEXITY-GUARD :863 complexity=25/0003-0006 蒸发后快照连触四闸/0007 窄批 5 件误记"其余 12 件已随前批在 HEAD"）+09-24 凌晨 03:47-07:46 主区蒸发案（10 号文四起同族，runner mtime 07:27:56 在窗）；修复代码留盘面未 commit，待队列落账（token 总指挥登记）；config/trading_decision_map.yaml 批内增量未恢复（避 clobber 09-24/25 他会话注册表编辑，留 SSOT 车道）；sim_bridge_execute.log 复效后首证待 09-25 09:35 触发窗 |

### EXE-4 成交回报链（ExecutionReport 生产端）

| 向 | 台账 |
|---|---|
| ①上游输入 | 订单终态（FILLED/CANCELLED/REJECTED——observe() 轮询+fill 回调累积双路取数，补 OM 不发 FILLED/REJECTED 事件的洞，`execution_report_producer.py` 头注）；累积 Fill+佣金 |
| ②数据原料 | CTR-P1-007 契约 15 列（schemas DDL INSERT_COLUMNS 唯一列序真源）；broker_id=通道 venue（qmt_sim）；algo_type 恒 "NONE"（文件桥单笔直投无算法切片语义——算法层从未在真单腿通过的铁证） |
| ③状态输出 | `c1_market.execution_report` 聚合行（只在终态落行、order_id 幂等、ReplacingMergeTree 同键替换；有成交量而佣金不可得=拒落行禁污染 TCA） |
| ④下游消费 | **全仓零读取方**（grep c1_market.execution_report/market_execution_report 仅 producer+integration 装配两文件；`reporting/default_tca_engine.py` 消费内存 Fill/Order 契约不读表）——表在、产在、**读者缺位** |
| ⑤自动化挂点 | 柜台同步线程每轮观察终态自动（在产，09-23 sysid 回填修后 1573/1800/4820 三合同验证）；断点 E4 闭合于 09-23 批 |
| ⑥缺口债 | T6b 撤单行语义勘（EXE-2⑥）；零读者=TCA 报表/归因/param_optimizer 的 tca_reader 注入全部无表可读（L07-C04）；BM-REC-02-A TCA 执行质量分析=battle_map 域件消费端未见接表实证 |

### EXE-5 成本反馈 L4-14（三零件+回写断链）

| 向 | 台账 |
|---|---|
| ①上游输入 | 实际成交回报（SlippageResult 多基准：到达价/VWAP/TWAP/前收/决策价，`slippage_analyzer.py` 头注）；发单前成本预估（L4-09+TCO 显性六项+隐性冲击/机会） |
| ②数据原料 | 滑点归因=冲击/时机/价差三因子+残差（平方根冲击预测）；质量四维=Price(50bps 阈)/Time(300s 阈)/Cost(30bps 阈)/Impact(20bps 阈) 加权 verdict good≥0.8/acceptable≥0.5/poor；逐笔 TCA 欠账=LK-12（decision price→fill price，A 股隐性成本可达佣金 5-10 倍，yaml:3802-3803 注） |
| ③状态输出 | SlippageResult/QualityScore/TransactionCostResult 三结构（均内存态）；"历史滑点/评分记录供趋势分析"=各自模块内 history，无落库位点 |
| ④下游消费 | **断**：scorer 头注 CONSUMERS 自注"MOD-XS-011 算法选择器反馈环"，但 `algo_execution_selector.py` 零 scorer/quality 引用（本班 09-25 复核）=D34 断链实证未修；旁系消费者=`reporting/deviation_attribution_decomposer.py`/`simulation/divergence_attributor.py`/`ml_train/research_data_manager.py`（grep 实证，非选择器反馈环语义） |
| ⑤自动化挂点 | 缺位：三零件皆 manual startup、无盘后批处理挂接（L4-14 activation=postmarket 无 runner）；执行参数自优化器（MOD-EX-064，production）的 tca_reader 注入=同缺表数据源 |
| ⑥缺口债 | TRD-A08（L4-14 闭环+逐笔 TCA 台账，实盘前必修——引用不重复）；L07-C02=接线图纸（selector 增评分反馈输入+按算法分桶权重回写，三零件零新增）； reporting/default_tca_engine 的 [CONSUMERS] 空（头注 ：8）=TCA 报表消费端双层断 |

### EXE-6 执行算法 TWAP/VWAP/IS（双层并存）

| 向 | 台账 |
|---|---|
| ①上游输入 | Order+AlgoParams+MarketContext（XS-005 输入协议）；订单特征 adv_fraction/urgency/spread_bps/side（XS-011 特征提取）；日内量分布 §13.2（开盘 20%/上午 25%/午盘 10%/尾盘 45%） |
| ②数据原料 | 六算法=TWAP/VWAP/ICEBERG/POV/IS(Almgren-Chriss 轨迹)/ALT；硬约束=参与率≤5%（§10.1 监管）、单笔≤15% ADV（§13.1）、切片 Decimal 守恒、下单零重试（HB-07）；ex_core 门禁版分档表（<1% 限价直发/1-5% TWAP/5-15% VWAP/>15% 拒） |
| ③状态输出 | AlgoExecutionPlan（切片方案）→ScheduledChildOrder（XS-004 优先级队列 P0-P3+参与率逼近降速）→路由三维评分（延迟/成交率/费用，XS-001）；algo_type 字段（execution_report 恒 NONE） |
| ④下游消费 | XS-004→XS-001→XS-002 broker 提交（ex_sor 内闭环，头注依赖链）；ex_core 侧 MOD-EX-062→MOD-EX-014 order_splitter；sor_agent（XS-015，Level 0 纯规则+滑点回写反馈循环+replay 可回放）——**两套选择器对同一 L4-06 节点并存零互认**（TDM 只挂 MOD-XS-011） |
| ⑤自动化挂点 | 缺位：ex_sor 全域 STARTUP=manual，无任何现役订单走算法切片（sim 真单=单笔直投）；RL 执行=design（XS-008 硬边界包裹层已码：涨跌停带裁剪/POV 上限/禁市价三不可逾越——TDM L4-14 注"远期候选挂晨审"） |
| ⑥缺口债 | **L07-C03：算法层收口裁定+IS 基准贯通**——MOD-XS-011 评分驱动 vs MOD-EX-062 分档门禁同域收敛唯一（w5_1）；IS 基准（arrival/决策价）只在 default_tca_engine INVARIANTS（DECISION 基准为主滑点基准）与 TCO 机会成本里，未贯通到 L4-14 评分与选型；algo_selection 效果评估"Phase 1 简单差额打分"（XS-011 头注）与 scorer 未接；IS/ALT 的 A 股 T+1/涨跌停改造欠账（TDM L4-14 注） |

### EXE-7 滑点标定 cost_model_calibration

| 向 | 台账 |
|---|---|
| ①上游输入 | 标定证据=PROVENANCE 窗口 2026-07-24~09-16、5,519 标的、五档快照 13,119,233 条（`cost_model_calibration.py:36-38`）；标定脚本 `scripts/calibrate_cost_tier_redblue.py`（红蓝对抗标定，正文未读）；判重实证源=slippage_impact_cost_mining 挖矿件（§1.2/1.3/1.5 治本对象） |
| ②数据原料 | 三腿语义：滑点腿=尺寸无关按流动性分层（liquidity_tier 单调非增）、冲击腿=AC η·p^β·σ（γ=0 实证不可辨识）、佣金腿=券商费率（真源留 matching_logic，本件零字面量）；MODIFY-GUARD=改档位必附 PROVENANCE+真数据前后对比（数值即证据结论） |
| ③状态输出 | 分层阈值常量+纯查表函数（Fail-Closed 越界抛 ZA-BT-0044）；成本归因快照（cost_attribution 档位/证据/地板拖累闭式） |
| ④下游消费 | 回测域四件（matching_logic 滑点腿/matching_engine 冲击腿/vectorized_engine 默认口径/cost_attribution+result_repository，头注 CONSUMERS 列全）+exam_cost_gate（regime_validation，考试成本闸）；**执行域零消费**——L4-09 成本实时估算挂 CST-ASTOCK-001（fixed bps=1）不吃标定档位 |
| ⑤自动化挂点 | 标定=一次性批产出（imported）；无再标定调度（窗口漂移后 PROVENANCE 过期无告警——如实注） |
| ⑥缺口债 | **L07-C08：成本参数双真源收敛**——CST-ASTOCK-001 slippage fixed bps=1（active）vs 标定结论"现值比实测一侧执行成本低 3.8 倍"（:29），登记表 evidence 只覆盖佣金校准（万3→万0.854）未覆盖滑点腿回写；t0_cost_model（CST-T0-001，testing）生产链路"接线挂起待 Owner"（B-007）自注；exec 侧策略下单规模硬约束（地板佣金→最小单量）"尚无消费者"（头注 CONSUMERS 注原文） |

### EXE-8 五档深度与盘口失衡

| 向 | 台账 |
|---|---|
| ①上游输入 | tick_depth_5 五档盘口（1,883 万行、日增 1,220 万，D36 差约 17 交易日，data-sufficiency L5 行；tick L1 3s 89.5 亿行=执行优化法定通道，裁定 #413④）；auction_highfreq 09:15-09:25 每 10s 五档快照（schedule.yaml:183-192） |
| ②数据原料 | ob_imbalance=(Σbid_vol_1..5−Σask_vol_1..5)/(Σbid+Σask)（5 档全量抗大单干扰，`orderbook_imbalance_strategy.py` 头注）；数据侧产供件=tick_depth_writer/tick_subscriber/tick_depth_backfill/ch_auction_derive/qmt_bridge_provider |
| ③状态输出 | 策略侧={symbol: target_weight}（PIT 仅当前 tick，二态 flat/long）；数据侧=tick_depth_5 表（CH） |
| ④下游消费 | 策略消费=strategy_runner（INV-PIT-001 回测路径不生成 Order——**回测态非执行信号**）；执行增强消费=盘口失衡执行信号 v2"排 GPU 后"（07 号文 §B2 末行+09 号文⑤引用）——缺位；tick 独立信号已判死（62bp 实证，appendix_B） |
| ⑤自动化挂点 | 数据摄取自动在产（backfill 每晚一天少一天窗口压力——08-18~09-10 约 19 日可回补窗在 data-sufficiency L5 行已警告，时点已过部分=追认损耗）；信号面无 runner |
| ⑥缺口债 | D36（五档 walkforward 收尾，引用不重复）；盘口失衡 v2 执行增强挂起；ch_tick_replay 五档回放消费正文未读（§3 MINING）；做T三策略（surge_fall/ob_imbalance/vwap_reversion）与 CST-T0-001 接线同批挂起（registry used_by_strategies=[] 自注） |

### EXE-9 卖出执行 X-S2 + 打板执行

| 向 | 台账 |
|---|---|
| ①上游输入 | 卖出决策链（S2-02 限价策略→S2-03 时段路由→SOR 下单，XS-016 头注 CONSUMERS 自注）；紧迫度 urgency+仓位+流动性三输入（X-S2-01 路由表）；四路输入仲裁序=X-R1/S1-06 强清中断≥F-C2-01 强裁>P2-03/04 纪律强平>S1-05 常规（D95 终裁，yaml X-S2-01 注） |
| ②数据原料 | 时段窗口表（深市 14:57 后集合竞价不可撤/竞价逃命单 9:15 挂跌停/14:30-14:45 跳水窗谨慎/14:50 做T收口）；t1_sellable 可卖额度（MOD-POS-028）；跌停三步处置+特殊标的分支族（新股首日/临停复牌/ST ±10% 时变已切片回填 #ARCH-DATA-020/碎股）；D70 流动性前置三检查+IS 急卖 preset（首 1/3 时间窗≥50%）+ICEBERG ±10-20% 抖动防识别（yaml X-S2-01 注 D70/D71/D72/D95 全族在案） |
| ③状态输出 | SellRouteDecision（通道+可撤性+谨慎旗标，纯函数 fail-closed 盘外恒 NO_ROUTE）；分笔执行计划（X-S2-01 三查过才发） |
| ④下游消费 | SOR 下单链（XS-016→ex_sor）；X-S2 卖出闭环（09 号文⑧下游）；KillSwitch 清仓排序（MOD-SELL-019）；daban_execution=首批实盘接线前暂无消费（头注 CONSUMERS 自注"G22 执行层落线后由 sleeve 组装消费"） |
| ⑤自动化挂点 | XS-016=design（MATURITY 自注）——离场执行的时段路由**未接电**；sell_execution_planner/t1_sellable=production 但消费链未验（如实注） |
| ⑥缺口债 | X-S2-01/02 落码件消费链核查（sell_execution_planner MOD-SELL-019 谁在调——未验）；恐慌拦截 D72 三类绕过豁免清单落地验证；daban_execution 三论文（Passive MI/SaR/Hawkes 核/扩散悖论 arXiv 四篇）参数全 proposal 态无实弹；打板执行专项 L4-05 挂 daban 域（域界归属登记，不重复挖掘） |

---

## §3 自审闸三态汇总

| 子块 | 三态 | 未读指针清单（MINING 债） |
|---|---|---|
| EXE-1 | MINING | plan_order_mapping_proposal.md 全文（13 号文代读结论引用）、01_ruling_plan_mapping_and_orphans.md 裁定卡全文、judgment_daily_plan→plan_bridge 翻译段正文 |
| EXE-2 | MINING | fill_handler/local_order_queue/order_execution_saga/cancel_rate_guard/open_order_resolver/async_fill_dispatcher 正文、position_reconciler、43 号合规 §7.4/§8 |
| EXE-3 | MINING | qmt_file_bridge_broker 正文 994 行（隔夜单/竞态两缺陷的代码面定位）、qmt_file_bridge_integration 全文、2026-09-08 迁移台账全文、qmt_e2e_runbook、.runtime/logs/sim_bridge_execute.log 09-24 后零行原因（任务侧实查） |
| EXE-4 | MINING | execution_report.py 正文、CTR-P1-007 契约字段集、sysid 回填代码段（broker :44 行后）、schemas DDL 15 列定义 |
| EXE-5 | MINING | 三零件正文（评分权重/归因系数实现）、reporting/default_tca_engine 正文（IS 四桶分解实现）、deviation_attribution_decomposer 消费语义、MOD-EX-064 tca_reader 注入协议 |
| EXE-6 | MINING | TwapStrategy/VwapStrategy/IsStrategy 实现体（切片公式对表 AC 原文）、optimal_order_router/broker_adapter_manager/market_context_provider 正文、sor_agent 正文、execution_route_policy、rl_exec_env/rl_exec_contract、D-EX-SOR §2.2 设计稿 |
| EXE-7 | MINING | cost_model_calibration 正文常量区（各 tier 数值）、calibrate_cost_tier_redblue.py、exam_cost_gate.py、cost_attribution.py、almgren_chriss_impact_model.py（estimate_params 零生产者确认）、matching_logic 费率字面量区 |
| EXE-8 | MINING | ch_tick_replay 五档回放段、tick_depth_backfill/writer、intraday_surge_fall/vwap_reversion 两兄弟策略、07 号文 §B2 盘口失衡 v2 原文、appendix_B（62bp 判死实证） |
| EXE-9 | MINING | sell_execution_planner MOD-SELL-019 消费链、t1_sellable 正文、42 号 memo §3.7/3.8、daban_execution 正文（三论文参数区）、XS-016 blueprint |

**计数：9 子块｜SEALED 0｜MINING 9｜BLOCKED 0**（骨架/审计/代码头注层已挖尽、六向台账全部有路径证据；欠的是各件正文级对表——不阻断 P0 施工，README"挖干即开工"条款）。

---

## §4 施工项（L07-C01 起，净零声明随项；TRD 已立的引用不重复立项）

| # | 项 | 内容与真源 | 沿用账本 | 内收声明/优先 |
|---|---|---|---|---|
| L07-C01 | **桥执行腿载体修复+中断销号** | bridge-execute 子命令（09-23 实弹批 14+2 文件）全分支零命中：从 delivery_report §3/57 行清单重建或向 st-sim-launch 会话追讨未落地袋；核查 09-24/25 四触发窗零日志原因（任务侧）；销号前 SimBridgeExecute 每次 09:35/13:05 触发=必败触发面 | 新卡（关联 TRD-A10 客户端侧、不重叠载体侧） | 恢复既有件非新增；**P0**（实单腿当前静默中断） |
| L07-C02 | **L4-14 断链接线施工**（三零件零新增） | `algo_execution_selector` 增评分反馈输入：按算法分桶消费 execution_quality_scorer 历史 verdict→权重回写（TDM L4-14 algo_note 原文口径）；三零件（XS-017/018/019）production 在位，只补 selector 一条消费边 | TRD-A08 | 纯接线，零新增组件；**P0** |
| L07-C03 | **执行算法层收口裁定+IS 基准贯通** | MOD-XS-011（评分驱动六算法）vs MOD-EX-062（ADV 分档门禁版）同域收敛唯一（w5_1）；IS 基准（arrival/决策价）从 default_tca_engine INVARIANTS 贯通到 L4-14 评分与选型（LK-12 施工面）；真单腿 algo_type 恒 NONE=算法层零实弹的事实登记 | 新卡（LK-12+TRD-A08 交叉） | 二选一收编禁双轨；Owner 裁定门位；**P0** |
| L07-C04 | execution_report 表接读者 | `c1_market.execution_report` 生产端在、全仓零读取方：接 default_tca_engine/MOD-EX-064 tca_reader 注入+BM-REC-02 报表面；T6b 撤单行语义先勘（producer 终态口径） | LK-12（表侧） | 纯接线；P1 |
| L07-C05 | 映射提案批复接线+参数对账 | TRD-A09 引用不重复；L07 补：`_plan_decision` 硬编码参数（30%/1.5%）与提案文件逐行对账（13 号文环节④"同一口径待实查"销号） | TRD-A09 | Owner 逐行批；P1 |
| L07-C06 | 桥客户端两缺陷治理（仓内侧） | 隔夜单拒单化 ack 语义+终态原子性：wrapper 活性守卫已是缓解（裁定 #339 gap-2），仓内可做=qmt_file_bridge_broker 对 #DONE 无柜台收录的单据 #FAIL 化补码+竞态回归用例进 qmt_bridge_regression_smoke | TRD-A10 | 客户端侧主体在办，仓内侧补防；P1 |
| L07-C07 | 五档深度 D36 收尾+盘口失衡 v2 立项 | D36 差约 17 交易日收尾（引用不重复）；盘口失衡执行增强 v2（07 号文 §B2）排 GPU 后——L07 视角=作执行时机信号（Cartea 时间市价单框架）非独立 alpha 立项 | D36 | P2 |
| L07-C08 | 成本参数双真源收敛 | CST-ASTOCK-001 slippage fixed bps=1（active）vs cost_model_calibration 标定档位（"低 3.8 倍"实证）：登记表滑点腿回写+L4-09 执行侧成本实时估算改吃标定 tier；地板佣金→最小下单规模约束落消费者 | DU/内收（新卡） | 标定 PROVENANCE 纪律随改；P1 |
| L07-C09 | X-S2 卖出执行链消费链核查 | sell_execution_planner（MOD-SELL-019）/t1_sellable（MOD-POS-028）production 件谁在调（未验）；XS-016 sell_session_router design→接电或显式休眠裁定 | 新卡（核查型） | P2 |
| L07-C10 | BT-P2-055 保持挂起登记 | 激活前置=窄考试立项（#331 砍向）；"模板缺"实为"有裁定地缺"（13 号文环节④）——L07 只登记不动工 | TRD-A11 | 登记非施工；P2 |

**施工项计数：10（P0×3 / P1×4 / P2×3）。挖干即开工：L07-C01/C02 可直接进执行队列；L07-C03 需 Owner 一句话裁定。**

> **L07-C01 结案（2026-09-25 桥执行腿修复班 P0）**：使命四步全清——①追查：载体未落库（git log --all 该文件止于 09-22 两批；-S "def bridge_execute" 全分支零命中）非落地后蒸发而是**入队全灭+主区蒸发案叠加**（根因链见 EXE-3⑥ 销号注记）；②找回：死信袋 blobs 内容寻址恢复（内容寻址 sha256 自校验=队列袋设计初衷的实弹验证）；③验证：--help/28+38 双套件/py_compile 九件全过，禁实单红线未触（未跑真单路径，复效首证待 09:35 触发窗）；④销号：本行+EXE-3⑥ 注记即销号凭证。SimBridgeExecute 定时任务自此从"必败触发面"复效为有效触发面（保守表述：仅指 sim 腿载体在位，实盘就绪结论仍归 §6 保守声明管辖）。

---

## §5 标准件（18 号文纪律：有标准/开源必须引用并采用，不自造）

| 标准件 | 对应子块 | 出处 | 许可证/采用方式 |
|---|---|---|---|
| **Almgren-Chriss (2000) Optimal Execution of Portfolio Transactions** | EXE-6 IS 算法/冲击腿理论基线 | 原文（J. Risk 2000）；[dm13450 求解教程](https://dm13450.github.io)（2024-06，最优轨迹推导 walkthrough） | 论文（公式公开）；XS-005 IsStrategy 切片公式逐项对表即合规，禁重写推导 |
| **QuantConnect/Lean Execution Models（VWAP/TWAP 即插模型）** | EXE-6 算法工程化参照 | [官方文档](https://www.quantconnect.com/docs/v2/our-platform/algorithm-framework/execution)、仓库 `QuantConnect/Lean` | Apache-2.0；只对表切片/调度语义不引依赖（C#→Python 语义移植须 own-diff 重写） |
| **hftbacktest（nkaz001）** | EXE-8 五档/盘口级回放+OBI 做市参照 | [GitHub](https://github.com/nkaz001/hftbacktest)、[PyPI](https://pypi.org)（MIT 确认）、[文档](https://hftbacktest.readthedocs.io) | MIT；限价单排队位/延迟建模语义对表 ch_tick_replay 五档回放设计 |
| **Cartea, Donnelly & Jaimungal, Enhancing Trading Strategies with Order Book Signals** | EXE-8 盘口失衡执行时机（time market orders）理论框架 | [Oxford ORA](https://ora.ox.ac.uk)、[SSRN](https://papers.ssrn.com) | 论文；盘口失衡 v2（L07-C07）立项的方法论锚：OBI 用于执行时机而非独立 alpha（与 62bp 判死结论兼容） |
| **Order Book Filtration and Directional Signal Extraction (arXiv 2025-07)** | EXE-8 OFI 增强表征（最新对表件） | [arXiv](https://arxiv.org) | 论文（开放获取）；v2 若立项的信号构造候选，回测验证后议 |
| **Cont, Kukanov & Stoikov (2014) Order Flow Imbalance** | EXE-8 OFI 标准定义 | 论文（The Price Impact of Order Flow Imbalance）；[dm13450 OFI 教程](https://dm13450.github.io) | 论文；ob_imbalance 现行 5 档差比式与 OFI 线性回归式的口径对表欠账（MINING） |
| **BestEx Research "IS Zero"（IS 型算法机构实务）** | EXE-6 IS 基准行业标尺 | [bestexresearch.com](https://www.bestexresearch.com)（2024-01；72% 交易员以 VWAP 算法服务低紧急度 IS 最小化） | 机构实务（不开源）；佐证"低紧急度默认 VWAP/IS 混合"选型先验，对照 XS-011 评分规则复核 |
| **vragulin/Optimal_Exec_In_Comp（AC 对比实现）** | EXE-6 AC 数值参考 | [GitHub](https://github.com) | **CC BY-NC 4.0=非商用，禁引码，只可对表数值结果** |
| **Kissell-Glantz I-Star / Bouchaud-Farmer propagator** | EXE-7 冲击模型字段对表 | `cost_model_registry.yaml` v1.30.0 注释已对标（square_root=AC 经验近似；propagator 三参数 Phase 1.5+ 启用） | 标准/论文；registry 字段已就位，Phase 1.5 前维持 null=合规现状 |
| **MariaAlpha（六算法参考实现）** | EXE-6 多算法族参照 | [GitHub](https://github.com) | 许可证未核实——采前必查 LICENSE（18 号文纪律），未核前只读不采 |

---

## §6 封矿裁定

本簿 **MINING**（9/9 子块有正文级未读指针，见 §3）；但六向台账已按实证填毕、三条新证（载体不可达/执行腿静默中断/断链今日复核仍断）均有命令级探针证据，P0×3 不受 MINING 阻塞（README"挖干即开工"）。**保守声明**：所有"通"的判定仅限 sim/纸面语境；L07-C01 销号前，"桥执行腿在产"表述一律降级为"桥执行腿 09-23 实弹一次后中断"；本文不给任何"实盘就绪"结论（准入门 baseline 全红口径同 13 号文 §11）。封矿前置=清空 §3 清单后复核。
