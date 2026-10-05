---
ttl: task_bound
---

# T3 整装考卷可行性挖矿：TDM 182 节点 vs 回测引擎实现对标

- 车道: H9 | sid: st-tclose-t3mine-20261005 | 日期: 2026-10-05
- 性质: 只读挖矿（唯一写=本文档）。未触碰 `data/strategy_intake/grid_20261005-*` 与任何在跑进程（T2 大考 grid_20261005-215457 在跑中）。
- 命题: Owner 判定"T1/T2 考的是因子选股主干，不是 TDM 全景图整装流程"。本文把 TDM 全部环节 vs 回测引擎实现对标挖干，给出"整装考 T3"的可行性骨架。
- 素材: `config/trading_decision_map.yaml`（182 节点/257 边/state_matrix/PP-001 组合计划）；网格执行器 `scripts/backtest/factory_grid_executor.py`；考卷引擎 `scripts/backtest/translated/_c4_engine.py`；框架引擎 `src/zephyr/backtest/`；网格维度 schema `config/position_recipe_grid_schema.yaml`；battle_map PG 三表（battle_map_steps 341 行 / anchors 588 行 / edges）；prereg `config/search_space_prereg.yaml`。

## 0. 一页结论

四类判定计数（182 节点全覆盖，逐条证据见 §1）：

| 判定 | 计数 | 占比 |
|---|---|---|
| A. 引擎已实现且可考 | **16** | 8.8% |
| B. 引擎有接口但考卷未开 | **26** | 14.3% |
| C. 引擎无实现=缺口 | **118** | 64.8% |
| D. 非回测域（盘前运维/治理/台账，天然不进回测） | **22** | 12.1% |

- Owner 命题成立且可量化：现行考卷（T0/T1/T2 网格）真实覆盖面 = A 类 16 节点（宇宙/剔除/因子合成/顺位/可交易性/定尺寸/调仓/成本档），另有 B 类 26 节点具备"接口占位"（schema 维度 J/F/K、框架撮合与 T+1 组合账本、regime 验证三件套、模拟盘风控闸）但考卷一概未开。TDM 的离场（X）、持仓（P）、组合（C 聚合层）、板块（L2）四大环节 118 节点在考卷引擎中零实现。
- "整装考 T3"可行，但必须分层：**T3a（S 级接线，纯向量化，GPU 0.53s/格口径可沿用）→ T3b（M 级模块补写，耗时口径须重标定）→ T3c（L 级子系统，回测只考日级可表达子集，整装语义转模拟盘 sim 平面考）**。详见 §3。
- BM→TDM 映射现状：battle_map PG 三表中 `battle_map_steps.tdm_node_id` 已映射仅 **11/341** 步（S2-02 止盈族/止损族/分批建仓/卖出融合/应急保命轨等，见 §1.9）；anchors 表 target_graph 只有 depgraph(560)/candidate(28)，**无 tdm 挂载**。

## 1. TDM 182 节点逐环节对标表

判定口径：
- **[已实现且可考]**：现行考卷链路（GridCompiler→evaluate_recipe→_c4_engine）真实行使该环节语义。
- **[有接口未开]**：schema 维度/框架模块/模拟盘闸门已有占位或生产实现，但现行考卷 context（`factory_grid_executor.py:101` DEFAULT_CONTEXT=`{"strategy_pool":["primary"],"phase":1,"capital_ramp_enabled":False}`）折叠或不消费。
- **[缺口]**：全仓 grep 无任何回测域实现（考卷引擎+框架引擎+模拟盘均无）。
- **[非回测域]**：盘前/盘后运维、治理、台账、实盘对账类，天然不进回测。

考卷引擎能力基线（后续证据引用基准）：
- 因子面=3 因子全从 close 现算：f_mom20/f_lowvol20/f_ma_gap（`scripts/backtest/factory_grid_executor.py:287-294`）。
- 回测核心=`w.shift(1)×rets` 的 T+1 向量化+涨跌停封板可成交性闸（`scripts/backtest/translated/_c4_engine.py:561-646, 453-497`）。
- 成本线=佣金 2.5bp 双边+印花 10bp 卖+滑点档双边，五档扫描（`_c4_engine.py:624-646`；`scripts/backtest/factory_grid_executor.py:935` exam_cost_gate）。
- 消费的引擎载荷仅：close/index/breadth/etf/valuation/fin/ST 标记/指数成分/涨跌停 limit 表（`_c4_engine.py:135-341, 372-451`）。

### 1.0 entry_flow·LROOT（1 节点）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-FLOW | 输出建仓信号（终端聚合） | 已实现且可考 | 考卷每格产出每日权重宽表=建仓清单（`factory_grid_executor.py:590-663` evaluate_recipe 返回 weights） |

### 1.1 entry_flow·L0 盘前作战计划（5 节点）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-L0 | 盘前作战计划（gate） | 非回测域 | module_ref=plan_engine/daily_warroom_pipeline.py，盘前人工+系统计划编排；回测无计划语义 |
| TDM-E-L0-01 | 计划生成 | 非回测域 | plan_engine/daily_trade_plan.py，盘前运维 |
| TDM-E-L0-02 | 偏离监控与修订 | 非回测域 | plan_engine/plan_deviation_monitor.py，盘中监控运维 |
| TDM-E-L0-03 | 收盘复盘与明日边界 | 非回测域 | plan_engine/tomorrow_boundary_planner.py，盘后运维 |
| TDM-E-L0-04 | 明日情绪盘中滚动预测 | 非回测域 | plan_engine/intraday_tomorrow_forecast.py；模拟盘 plan-bridge 已证明计划姿态仅防御态可机械执行、其余如实记 unexecutable（`scripts/backtest/sim_daily_runner.py:20-30`） |

### 1.2 entry_flow·L1 大盘总闸（cn_a 9 节点 + crypto 1）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-L1 | 大盘总闸（gate, critical） | 有接口未开 | 维度旋钮 J_regime_switch=[off,on] 已入 schema（`config/position_recipe_grid_schema.yaml:64-68`，active_if phase>=2，注释"Owner 已同意二期"）；regime 回测验证三件套在册（`src/zephyr/backtest/regime_validation/c1_runner.py` shrinkage 开/关对比、`c2_extreme_event_protection.py` CRISIS 时段 MaxDD、`c3_throttle_attribution.py` 分态归因）；考卷 phase=1 J 折叠（executor:101） |
| TDM-E-L1-S1 | 大盘指数传感器 | 缺口 | 考卷因子面 3 因子全从个股 close 现算（executor:287-294）；`load_index` 载荷函数在册但网格不消费（`_c4_engine.py:164-173`） |
| TDM-E-L1-S2 | 市场内部结构传感器（涨停梯队） | 缺口 | 涨停数据在考卷只用于封板掩码（可成交性闸），不作信号（`_c4_engine.py:372-403`）；limit_up_followthrough 逻辑无回测实现 |
| TDM-E-L1-S3 | 赚钱效应传感器（连板溢价） | 缺口 | 全仓 grep：lhb_premium_analyzer 仅 live 域，回测域零引用 |
| TDM-E-L1-S4 | 波动率传感器（合成 VIX） | 缺口 | 考卷 f_lowvol20 是个股截面低波，非市场级 VIX；synthetic_vix 无回测消费 |
| TDM-E-L1-S0 | 宏观环境传感器 | 缺口 | alt_data/policy_expectation_analyzer 仅 live；回测域零引用 |
| TDM-E-L1-S0-1 | 新闻情绪语义分析 | 缺口 | news_sentiment_analyzer 仅 live；考卷无文本因子 |
| TDM-E-L1-S5 | 日级市场条件传感器 | 缺口 | daily_condition_sensor 仅 live；回测域零引用 |
| TDM-E-L1-AGG | 市场状态判定（六态状态机, critical） | 有接口未开 | owner_regime_switcher 有日级状态机+冻结考试引擎（`src/zephyr/strategy_factory/owner_regime_switcher/switcher.py:96-243` build_schedule/hysteresis、`engine.py:167` run_leg 冻结签名）；TDM state_matrix 六态格部分已挂策略、部分 pending-owner-adoption；考卷未接 |
| TDM-C-L1 | 币圈大盘总闸（crypto） | 缺口 | crypto 4 节点无任何回测实现（grep 仅 `scripts/backtest/generate_backtest_backlog.py` 提及 crypto 属 backlog） |

### 1.3 entry_flow·L2 板块选择（cn_a 29 节点 + crypto 1）

全部 **缺口**（29 条）。证据统一：考卷维度空间=因子标准化/合成/Top-N/定尺寸/调仓/单票帽/宇宙/换手 λ 九维（`config/position_recipe_grid_schema.yaml:12-73`），无板块维；行业数据（sws2021_l1 锚 c1_market.industry_class）在考卷只用于 A1 中性化的分组 demean，不做板块选择（schema:84-91；`factory_grid_executor.py:251-272, 297-311`）。逐条：

| 节点 | 名称 | 判定 |
|---|---|---|
| TDM-E-L2 | 板块选择（组骨架） | 缺口 |
| TDM-E-L2-01 / -01-1 / -01-2 / -01-3 / -01-4 / -01-5 | 板块强度综合/结构强度/动量排名/多周期加权/资金流聚合/市场级调节注入 | 缺口 |
| TDM-E-L2-02 / -02-1 / -02-2 | 轮动序列追踪/RRG/单板块预警 | 缺口（BM-SEL-08 已映射 TDM-E-L2-02，见 §1.9） |
| TDM-E-L2-03 / -03-1 | 调整周期进度/扩散指标追踪 | 缺口（BM-SEL-09 已映射） |
| TDM-E-L2-04 / -04-1 / -04-2 | 板块级市场状态/轮动五分类/虹吸态 | 缺口 |
| TDM-E-L2-05 / -05-1 / -05-2 | 水温响应/水温档推导/信号响应三件套 | 缺口 |
| TDM-E-L2-06 / -06-1 / -06-2 / -06-3 | 板块个股传导/三级放行/龙头识别/强度加权传导 | 缺口 |
| TDM-E-L2-07 / -07-1 | 回踩质量分级/回踩ABC判定 | 缺口 |
| TDM-E-L2-08 | 板块生命周期判定 | 缺口 |
| TDM-E-L2-09 / -09-1 / -09-2 | 催化剂识别/事件图谱传导/冲击标的生成 | 缺口 |
| TDM-E-L2-10 | 同源补涨比价 | 缺口 |
| TDM-C-L2 | 赛道选择（crypto） | 缺口 |

### 1.4 entry_flow·L3 个股选择（cn_a 25 节点 + crypto 1）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-L3 | 个股选择（组骨架） | 缺口 | 组节点无独立机制 |
| TDM-E-L3-01 | Universe构建与剔除 | 已实现且可考 | G_universe=[hs300,zz500,all_a_ex_st]（schema:50-54；`factory_grid_executor.py:198-232`）；filter_st+load_st_flags（`_c4_engine.py:318-341`）——全A剔ST 域现成 |
| TDM-E-L3-02 | 九阶段选票主链（基本面漏斗） | 缺口 | 考卷=3 因子 rank，无基本面漏斗；fin_snapshot/fin_history 载荷在册不消费 |
| TDM-E-L3-03 | 双池评分（聚合） | 缺口 | 无双池语义 |
| TDM-E-L3-03-1 | 短线池5分制 | 缺口 | fine_scoring_engine 仅 live |
| TDM-E-L3-03-2 | 波段池5分制 | 缺口 | quant_short_term_strength_engine 仅 live |
| TDM-E-L3-03-3 | 双策略合流体检 | 有接口未开 | F_merge_policy=[single,equal_capital,equal_risk,signal_additive] 维占位（schema:44-48，active_if strategy_pool>1）；引擎 evaluate_recipe 不读 F 键（executor:590-663 只取 A1/A2/B/C/D1/D2/E/H/G）——接口在、执行器零实现 |
| TDM-E-L3-04 | 负面否决器 | 缺口 | 考卷除 ST 剔除外无否决维 |
| TDM-E-L3-05 | 顺位排序 | 已实现且可考 | 截面 rank+Top-N 即顺位选股主干（executor:644-651 `combined.rank(axis=1)`+`_norm_rows`） |
| TDM-E-L3-06 | 环境开关 | 有接口未开 | 同 TDM-E-L1：J 维占位+regime 三件套，考卷未接 |
| TDM-E-L3-07 | 策略专属链（组骨架） | 缺口 | 组节点 |
| TDM-E-L3-07-1 | 打板选股链 | 缺口 | daban_sleeve 仅 live+PP-001 sleeve 引用，无考卷 |
| TDM-E-L3-07-2 | 多因子打分链 | 已实现且可考 | A1 标准化 6 值×A2 合成 8 值（raw/rank/zscore/行业中性族/ic 族/halflife/orth/lasso/pc1）=多因子合成全维精确实现（executor 头注 v1/T2a/T2b；schema:13-27） |
| TDM-E-L3-07-3 | 其余 sleeve 选股链 | 缺口 | event_driven_sleeve 等仅 live |
| TDM-E-L3-08 | 候选池输出（聚合） | 已实现且可考 | Top-N 权重宽表=每日候选池输出（executor:644-663） |
| TDM-E-L3-09 | 股票池分层维护 | 缺口 | 池分层为有状态日频维护，考卷无此层 |
| TDM-E-L3-10 | 可交易性预检 | 已实现且可考 | 涨跌停封板可成交性闸：封涨停禁开新仓/封跌停禁出逃（`_c4_engine.py:453-497` apply_fillability_gate docstring 明示语义） |
| TDM-E-L3-11 | 日内动态选股（组骨架） | 缺口 | 考卷纯日频 |
| TDM-E-L3-11-1 | 竞价选股 | 缺口 | 竞价数据不进考卷；框架有 tick 级引擎（event_driven_engine/ch_tick_replay）但无竞价段考卷 |
| TDM-E-L3-11-2 | 盘中涨速异动扫描 | 缺口 | 同上 |
| TDM-E-L3-12 | 个股多维验证（组骨架） | 缺口 | 组节点 |
| TDM-E-L3-12-1 | 个股资金面分析 | 缺口 | 考卷无资金流因子 |
| TDM-E-L3-12-2 | 龙虎榜席位追踪 | 缺口 | 同上 |
| TDM-E-L3-12-3 | 筹码分布分析 | 缺口 | chip_distribution_engine 仅 live |
| TDM-E-L3-12-4 | 形态结构识别（缠论） | 缺口 | chanlun_structure 仅 live |
| TDM-C-L3 | 币对选择（crypto） | 缺口 | 同 crypto 判据 |

### 1.5 entry_flow·L4 买卖点与执行（cn_a 15 节点 + crypto 1）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-L4 | 买卖点与执行（组骨架） | 缺口 | 组节点 |
| TDM-E-L4-01 | 分批建仓 | 有接口未开 | K_capital_ramp=[lump,linear_20d,linear_60d,pyramid] 维占位（schema:69-73，active_if capital_ramp_enabled，注释自述"需 harness 支持路径依赖"=执行器未建）；考卷一次性足额建仓 |
| TDM-E-L4-02 | 买入时序（尾盘决策） | 缺口 | 考卷隐含收盘价成交（`_c4_engine.py:455` "w_t 的隐含成交价=close_t"），无时序选择；修正=接 Open/VWAP 宽表（S 级） |
| TDM-E-L4-03 | 价格锚定 | 缺口 | 同上，单一 close 口径 |
| TDM-E-L4-04 | 资金分配多标的 | 已实现且可考 | C_sizing 7 值（equal_weight/mkt_cap/inv_vol/risk_parity/kelly_025/kelly_050/signal_strength）全精确实现（executor:472-523；头注 T2a） |
| TDM-E-L4-05 | 打板执行专项 | 缺口 | 封板闸只挡单，无打板排单语义 |
| TDM-E-L4-06 | 执行算法（SOR） | 有接口未开 | 框架有 ADV 五分位滑点腿+Almgren-Chriss 冲击腿（`src/zephyr/backtest/core/matching_engine.py:14-19` INV-COST-LEGS；`zephyr.execution_simulation.almgren_chriss_impact_model`）；考卷用平档 slippage_bp |
| TDM-E-L4-07 | 条件触发队列 | 缺口 | 本地条件单为实盘语义；考卷无订单对象（诚实位 §4.3） |
| TDM-E-L4-08 | 突破失败降级 | 缺口 | breakout_failure_detector 仅 live，回测域零引用 |
| TDM-E-L4-09 | 执行硬约束（price cage, critical） | 有接口未开 | 框架 matching_engine 强制 A股约束=T+1/涨跌停/停牌/100股整数倍（matching_engine.py:18-19）；考卷侧仅封板闸、无手数取整 |
| TDM-E-L4-10 | 订单生命周期状态机 | 有接口未开 | 框架 portfolio.apply_fill 强制 T+1（`src/zephyr/backtest/core/portfolio.py:147,195-210`）+event_driven fills；模拟盘 bridge-execute 走三闸 OrderManager（`sim_daily_runner.py:50-55`）；考卷无订单对象 |
| TDM-E-L4-11 | 部分成交与撤改处理 | 缺口 | 考卷满仓成交假设；框架参与率/冲击隐含部分成交语义（INV-UNIT-001）但无撤改 |
| TDM-E-L4-12 | 订单级预检 | 有接口未开 | 模拟盘 bridge-execute 三闸预检在册（sim_daily_runner.py:50-55）；考卷无 |
| TDM-E-L4-13 | 执行容灾对账（三方对账） | 非回测域 | three_way_reconciliation=实盘账务运维 |
| TDM-E-L4-14 | 执行成本反馈与选型回写 | 非回测域 | execution_quality_scorer=实盘遥测；邻近件=框架 cost_attribution/cost_model_calibration 在册 |
| TDM-C-L4 | 币圈买卖点（crypto） | 缺口 | 同 crypto 判据 |

### 1.6 position_flow·P 族（18 节点）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-P-FLOW | 输出持仓信号（终端聚合） | 已实现且可考 | 每日权重路径=持仓路径（weights ffill） |
| TDM-P-P1 | 持仓体检（组骨架） | 缺口 | 考卷无持仓态维护/体检层 |
| TDM-P-P1-01 | 持仓对账与台账快照 | 非回测域 | 台账/对账=账务运维 |
| TDM-P-P1-02 | 持仓分级与监控频率 | 非回测域 | 监控运维 |
| TDM-P-P1-03 | 买入逻辑存活判定 | 缺口 | 可回测的卖出纪律（thesis_survival），回测域零引用 |
| TDM-P-P1-04 | 风险否决体检（A 止损引擎） | 缺口 | 止损引擎无回测挂接——全仓 grep src/zephyr/backtest+scripts/backtest 引擎面零引用 sell_decision/risk 止损（仅研究样板与模拟盘 legacy，见 §1.7 S1-02） |
| TDM-P-P1-05 | 组合级持仓体检（漂移监控） | 已实现且可考（近似） | D2_rebalance_trigger=drift_band 漂移带触发已精确实现（executor:546-577 numpy 行循环，头注"nansum=逐行 skipna 同语义"）；仅漂移一腿 |
| TDM-P-P1-06 | 体检结论与动作清单 | 非回测域 | 裁定中心运维 |
| TDM-P-P2 | 做T与加减仓（组骨架） | 缺口 | 组节点 |
| TDM-P-P2-01 | 做T资格与成本前置（T+1 可卖, critical） | 有接口未开 | 日级 T+1 已隐含实现（w.shift(1)=当日买入次日方可调出）；逐笔 T+1 锁定在框架 portfolio（portfolio.py:147）；做T 级资格无考卷 |
| TDM-P-P2-02 | 做T策略调度 | 缺口 | 日频向量化原理上不可表达日内 T+0 轮回（诚实位 §4.2） |
| TDM-P-P2-03 | 做T闭环与成功判定（critical） | 缺口 | t0_trading_pipeline 仅 live |
| TDM-P-P2-04 | 减仓与再平衡 | 已实现且可考 | D1 调仓频率 4 值+D2 触发+H 换手惩罚 λ=调仓引擎三件（executor:546-577, 530-545） |
| TDM-P-P3 | 加仓决策（组骨架） | 有接口未开 | K 维 pyramid 取值占位（schema:71） |
| TDM-P-P3-01 | 加仓资格门 | 有接口未开 | 同上（K 维 harness 未建） |
| TDM-P-P3-02 | 金字塔加仓规则 | 有接口未开 | 同上（pyramid 在 K values 中，执行器不消费） |
| TDM-P-P3-03 | 加仓量级与风险核算 | 缺口 | position_sizing_engine 仅 live |
| TDM-P-P3-04 | 加仓时点与执行 | 缺口 | position_limit_enforcer 仅 live |

### 1.7 exit_flow·X 族（19 节点）——**最大缺口带**

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-X-FLOW | 输出离场信号（终端聚合） | 缺口 | **考卷无任何主动离场**：权重仅在调仓日变动，跌出 Top-N 即被动清仓（`_backtest_core` gross=w.shift(1)×rets，无止损/止盈路径，`_c4_engine.py:561-616`） |
| TDM-X-R1 | 应急保命（cross_cutting） | 有接口未开 | 模拟盘平面已接回撤六态机 defensive_only（CRISIS/KILL 拒新开仓，`sim_daily_runner.py:1318,1356-1394`）；网格考卷无 |
| TDM-X-R1-01 | 熔断分级判定 | 有接口未开 | DrawdownStateMachine 在模拟盘 bridge 接线（同上）；c2_extreme_event_protection 可做 CRISIS 时段 MaxDD 分析（框架在册） |
| TDM-X-R1-02 | 熔断期减仓与持仓处置 | 有接口未开 | 模拟盘 KILL→execute_kill_switch_liquidation（`sim_daily_runner.py:1465`）；考卷无 |
| TDM-X-R1-03 | 护盘资产定向加仓白名单 | 缺口 | TDM state_matrix 自述：euphoria/distribution 两态"PP-001 无防御型 sleeve"，格子 pending-owner-adoption（trading_decision_map.yaml state_matrix cells）；防御档内容=Owner 资金分配门位 |
| TDM-X-S1 | 卖出信号收集评分（组骨架；BM 已映射） | 缺口 | 组节点（BM-SELL-03→TDM-X-S1 映射在册，回测侧仍零实现） |
| TDM-X-S1-01 | 信号收集与六桶分类 | 缺口 | sell_signal_collector 仅 live |
| TDM-X-S1-02 | 止损族判定（BM-SELL-04-B 已映射） | 缺口 | 研究样板在册：ATR 3 倍止损带（`scripts/backtest/indicator_consumption_demo.py:34`）、forward_stop_loss（`scripts/backtest/panic_rebound_depth.py:149`）、模拟盘 legacy stop_loss 路径（`sim_daily_runner.py:1423`）；**考卷引擎零实现** |
| TDM-X-S1-03 | 止盈族判定（BM-SELL-04-A 已映射） | 缺口 | take_profit_strategy 仅 live；全仓 grep 考卷/框架无止盈实现 |
| TDM-X-S1-04 | 破位与情绪退潮信号 | 缺口 | 同 S1-02 |
| TDM-X-S1-05 | 信号融合与紧迫度评分（BM-SELL-02 已映射） | 缺口 | sell_signal_fusion_engine 仅 live |
| TDM-X-S1-06 | 强制清仓绕过通道 | 非回测域 | strategy_abnormal_exit_orchestrator=实盘异常处置编排 |
| TDM-X-S2 | 离场执行（组骨架） | 缺口 | 组节点 |
| TDM-X-S2-01 | 执行方式路由（critical） | 缺口 | sell_execution_planner 仅 live |
| TDM-X-S2-02 | T+1 与涨跌停约束 | 已实现且可考（近似） | 封板闸双向：封涨停禁买入/封跌停禁卖出（`_c4_engine.py:453-497`）+shift(1) T+1；框架侧 matching_engine 同约束；失真点=日级 close 判定封板（§4.4） |
| TDM-X-S2-03 | 执行时段路由 | 缺口 | sell_session_router 仅 live；考卷单一收盘口径 |
| TDM-X-S2-04 | 本地条件单管理 | 缺口 | 条件单=日内价格触发语义，考卷无日内路径 |
| TDM-X-S2-05 | 分批止盈执行 | 缺口 | scaling_out 仅 live；考卷调仓日一次性全额 |
| TDM-X-S2-06 | 卖出闭环与退出效率（BM-SELL-09 已映射） | 非回测域 | 执行质量遥测=实盘域 |

### 1.8 portfolio_flow·C 族（13 节点）

| 节点 | 名称 | 判定 | 证据 |
|---|---|---|---|
| TDM-F-FLOW | 输出组合信号（终端聚合） | 有接口未开 | F_merge 维占位（schema:44-48）；考卷恒 single（strategy_pool=["primary"]） |
| TDM-F-C1 | 预算切分（gate） | 有接口未开 | F 取值含 equal_capital/equal_risk（schema:46-47）；multi_strategy_capital_allocator 仅 live；考卷未开多策略 |
| TDM-F-C2 | 组合聚合（组骨架） | 有接口未开 | 同 F 维占位 |
| TDM-F-C2-01 | 目标聚合与净额轧平 | 缺口 | firm_risk_aggregator 仅 live；考卷无组合聚合层 |
| TDM-F-C2-02 | 组合约束栈 | 已实现且可考（子集） | E 单票上限（cap5/10/20，含 B×E 交互的持仓数扩展语义 executor:644-651）+H 换手惩罚+B Top-N=约束栈三腿；行业/风格敞口腿缺 |
| TDM-F-C2-03 | 相关性聚类与 cluster 上限 | 缺口 | correlation_regime_monitor 仅 live；考卷无相关性约束 |
| TDM-F-C2-04 | budget 变动三级升级 | 非回测域 | 治理升级流程 |
| TDM-F-C3 | 绩效归因反馈（组骨架） | 有接口未开 | 框架 cost_attribution.py 在册（`src/zephyr/backtest/core/cost_attribution.py:148` CostAttribution）；考卷 manifest 仅 stats 摘要列 |
| TDM-F-C3-01 | 多维归因引擎 | 有接口未开 | 同上；performance_attribution_engine 仅 live |
| TDM-F-C3-02 | 升降级管线与退役评审 | 非回测域 | 因子治理流程；邻近件=考卷侧 decision_gate/overfitting 判定已实现（`f06_e4_wfa_exam.py:43-44` 三阶段门控+过拟合检测） |
| TDM-F-C3-03 | sleeve 权重调权 | 有接口未开 | owner_regime_switcher scaled_schedule/caps 日级帽在册（switcher.py:223-243）；F 维+J 维联合占位 |
| TDM-F-C3-04 | 参数校准闭环 | 已实现且可考 | walk_forward/cpcv/purged_kfold 框架全在册且 E4-WFA 考卷在用（`scripts/backtest/f06_e4_wfa_exam.py` 8 折滚动；`src/zephyr/backtest/core/walk_forward.py, cpcv.py, purged_kfold.py`） |
| TDM-F-C3-05 | 可靠度养成与信号健康 | 有接口未开 | 框架 services/decay_monitor.py 在册；考卷未接 |

### 1.9 entry_flow·L9 数据与知识供给（44 节点）

| 节点组 | 数量 | 判定 | 证据 |
|---|---|---|---|
| TDM-E-L9-A01 源线·日线/分钟行情 | 1 | 已实现且可考 | load_px←c1_market.kline_daily（`_c4_engine.py:135-149`） |
| TDM-E-L9-A02 源线·Tick 分笔 | 1 | 有接口未开 | ch_tick_replay+event_driven tick 引擎在册；网格不消费 |
| TDM-E-L9-A04 源线·估值 | 1 | 有接口未开 | load_valuation 在考卷引擎自身（`_c4_engine.py:189-229`）；网格因子不消费 |
| TDM-E-L9-A05 源线·财务 | 1 | 有接口未开 | fin_snapshot/fin_history 在考卷引擎自身（`_c4_engine.py:231-268`）；不消费 |
| TDM-E-L9-D1 决策假设·因子组合挖掘 | 1 | 已实现且可考 | `scripts/backtest/mcts_expression_search.py`（D_BACKTEST 域因子挖掘） |
| TDM-E-L9-E1 验证·一问一考考试链 | 1 | 已实现且可考 | `src/zephyr/trading/validation/runner.py`+框架 layered_validation_pipeline/strategy_validation_pipeline 在册在用 |
| TDM-E-L9-A03/A06/A07/A08/A09/A10/A11/A12/A13/A14/A16、B01-B10、C01-C03、G1-G5 | 30 | 缺口 | 全仓 grep：考卷引擎载荷面仅 close/index/breadth/etf/valuation/fin/ST/成分/limit 表（§0 基线）；资金流/另类数据/图谱 30 条源线无考卷消费。G3 实体股权穿透 live script 在册不进考卷 |
| TDM-E-L9-A15 源线·加密永续/费率 | 1 | 缺口 | crypto 域，无任何回测实现 |
| TDM-E-L9-V1/V2/V3 状态变量快照 | 3 | 非回测域 | judgment_ledger 判定台账=实盘/模拟盘语义（sim plan-bridge 只读消费，`sim_daily_runner.py` [CONSUMERS]） |
| TDM-E-L9-AGG 知识供给汇聚 | 1 | 非回测域 | l9_readiness_aggregator=数据就绪运维 |
| TDM-E-L9-D2 登记与考试方案 | 1 | 非回测域 | 预注册治理（search_space_prereg 册） |
| TDM-E-L9-E2 结论回传与修正 | 1 | 非回测域 | 治理闭环 |
| TDM-E-L9-Z1/Z2 治理 | 2 | 非回测域 | 问题治理/净零对账=治理域 |

### 1.10 crypto 族（4 节点）

TDM-C-L1/L2/L3/L4 全部 **缺口**（已计入 §1.2/1.3/1.4）：无 crypto 行情载荷、无 crypto 回测（grep 仅 backlog 提及）。

### 1.11 BM→TDM 映射现状（battle_map PG 三表）

- `battle_map_steps` 341 行，`tdm_node_id` 非空仅 **11 行**：BM-RC-10→TDM-P-P1-04、BM-SELL-03→TDM-X-S1、BM-SEL-03→TDM-E-L1-AGG、BM-SELL-04-A→TDM-X-S1-03、BM-SELL-04-B→TDM-X-S1-02、BM-BUY-04→TDM-E-L4-01、BM-SELL-02→TDM-X-S1-05、BM-SELL-09→TDM-X-S2-06、BM-SEL-08→TDM-E-L2-02、BM-SEL-09→TDM-E-L2-03、BM-BUY-02-D→TDM-X-R1。
- 讽刺点：11 条映射里 8 条落在 X/P 族（止盈止损/卖出/保命轨）——正是考卷零实现的缺口带。作战地图挂了 TDM，考卷没跟上。
- `battle_map_anchors` 588 行 target_graph 仅 depgraph(560)/candidate(28)，无 tdm。

## 2. 缺口清单（C 类 118 项按工作量分级）

工作量口径：**S=参数/数据接线（复用在册模块，向量化可写，≤1 个考卷迭代）**；**M=模块补写（新逻辑但日频向量化可表达）**；**L=新子系统（需新引擎面/新数据面/新编排）**。

### S 级（接线即可考，估计 5 项）

| # | 缺口（TDM 节点） | 接线内容 | 复用在册资产 |
|---|---|---|---|
| S1 | L1 总闸/L1-AGG/L3-06 环境开关 | J_regime_switch=on：owner_regime_switcher 日级 cap 调度表 × 权重矩阵逐行乘（向量化一行） | switcher.py build_schedule；schema J 维 |
| S2 | L4-02 买入时序 + L4-03 价格锚定 | 成交价口径 close→next_open / vwap 宽表（rets 换源即可） | _c4_engine load_px 泛化 |
| S3 | L9-A04 估值 / L9-A05 财务 | 载荷函数已在考卷引擎自身，接入因子面即考（PB/PE 因子档） | load_valuation/fin_snapshot |
| S4 | X-R1-03 护盘白名单 | 防御档资产（ETF/红利）进 G_universe 候选+state_matrix 防御格内容——**格子内容属 Owner 资金分配门位，AI 禁自填**（state_matrix mounted_reason 明示） | TDM state_matrix；load_etf |
| S5 | F-C3-01 归因 manifest 增列 | cost_attribution 输出进 manifest 列 | 框架 cost_attribution.py |

### M 级（模块补写，日频向量化可表达，估计 8 项）

| # | 缺口（TDM 节点） | 补写内容 | 备注 |
|---|---|---|---|
| M1 | X-S1-02 止损族 + X-S1-03 止盈族 | 日级 ATR 止损带/移动止盈/目标价向量化（indicator_consumption_demo 已有 ATR 样板可翻译） | X 族最小考卷核 |
| M2 | X-R1-01/02 熔断分级与减仓 | 回撤六态机日级向量化（峰值权益 running-max→态→帽） | DrawdownStateMachine 语义翻译；c2 已有 CRISIS MaxDD 判据 |
| M3 | L2 板块主干最简版 | sws2021_l1 行业动量 Top-K 板块 × 板块内个股两层排序（行业锚已在） | 行业锚=c1_market.industry_class（schema:84-91） |
| M4 | L4-01 分批建仓 + P3 金字塔 + S2-05 分批止盈 | K_capital_ramp 四取值的权重路径渐变后处理（lump/linear/pyramid 均可向量化） | schema 自述"需 harness 路径依赖"——向量化实现即满足 |
| M5 | P1-03 买入逻辑存活判定 | 入场理由因子存活追踪（入场因子值退化→离场） | thesis_survival 语义回测化 |
| M6 | C2-03 相关性 cluster 上限 | 滚动相关矩阵贪心聚类+簇帽 | 日频可算但 O(S²) 注意 GPU |
| M7 | L4-11 部分成交 | 参与率上限向量化（成交额/ADV 帽） | INV-UNIT-001 口径 |
| M8 | L3-03 双池评分最简版 | 动量池/低波池双 5 分制+合流 | F 维 signal_additive 可搭桥 |

### L 级（新子系统，估计 5 项）

| # | 缺口（TDM 节点带） | 子系统 | 备注 |
|---|---|---|---|
| L1 | P2-01~03 做T全链 + L3-11 日内动态选股 + S2-04 条件单 | tick/分钟级考卷编排（框架 event_driven_engine+ch_tick_replay+matching_engine 在册，缺考卷层+竞价段） | 做T 语义只有 tick 级可表达 |
| L2 | L4-07/10/11/12 订单九态语义 | 订单生命周期考卷（部分成交/撤改/废单/条件触发） | 模拟盘 bridge-execute 已有三闸实盘件，考卷化=新编排 |
| L3 | L9 另类数据源线 30 条消费 | 每条=数据工程+因子工程 | 破坏"净零"纪律风险高，须逐条立项替代声明 |
| L4 | C2-01 净额轧平+C1 预算切分+C3-03 调权全链 | 多策略组合层引擎（F 维全取值+组合聚合） | PP-001 整装组合 V0 是现成蓝图 |
| L5 | TDM-C-* crypto 域 | crypto 行情载荷+回测 | 独立域 |

## 3. 整装考卷 T3 设计草案

### 3.1 分批结构（对应 §2 缺口分级，三步走）

| 批次 | 考什么 | 依赖缺口 | 名义空间 | 预计算量（GPU 0.53s/格口径） |
|---|---|---|---|---|
| **T3a** | 开闸考：J_regime_switch=on × G_universe=all_a_ex_st，九维网格整卷重跑（S1+S3 接线） | S1, S3 | phase=2：N_raw=362,880×2(J)=**725,760**（F/K 仍折叠），分层抽样 | T3a-T0 标定 200 格≈1.8min；T3a-T1 7,400 格≈**65min**；T3a-T2 1,800 格≈16min；总帽 25,000 格≈3.7h——单作业 12h 帽内、59h 窗内全部可容 |
| **T3b** | 加离场考：T3a 幸存子空间 ×（M1 止损止盈档 + M2 熔断档 × 叠加为新增考维） | M1, M2 | 新增 X 维（如 stop=[off,atr3x,trail20%] × breaker=[off,dd20%]）空间 ×N；须先重标定单格耗时 | **0.53s/格口径不再适用**（新增日级回路破坏纯向量化，CPU 口径 35.33s/格 → 7,400 格≈72.6h 超 12h 单作业帽）——T3b-T0 强制重标定 per_point_seconds 后再定 T1/T2 点数，fail-closed 沿用现行 prereg 钳制机制 |
| **T3c** | 整装考：多策略组合层（L4：F 维全开+PP-001 八 sleeve 权重）+ 订单/做T 语义子集 | L1, L2, L4 | 不再是格点网格，转**模拟盘 sim 平面考**（plan-bridge+bridge-execute 已有三闸实盘件） | 回测只考日级可表达子集；tick/订单语义以模拟盘为准（诚实位 §4） |

### 3.2 配置形态（T3a 为例）

- context：`{"strategy_pool": ["primary"], "phase": 2, "capital_ramp_enabled": false}` + 考卷维 `G_universe=all_a_ex_st` + `J_regime_switch=on`。
- J 的引擎语义必须先钉死并写进 prereg honesty：T3a 的"总闸"=owner_regime_switcher 日级帽调度（cap_A/cap_B 乘性帽+迟滞），**不等于** TDM L1 六态挂载矩阵（后者多格 pending-owner-adoption、C5 已对 euphoria/distribution 禁用——无防御 sleeve）。两者差距是 T3a 的已知失真，不是等价实现。
- 执行器改造点（均在 `factory_grid_executor.py`）：①`DEFAULT_CONTEXT` 按 stage 参数化（t3→phase=2）；②evaluate_recipe 接 J（调度表 join 乘帽）；③manifest 增 `j_state` 列（每日总闸态，审计用）；④stage 帽/耗时键沿 `_apply_prereg_budget` 既有 fail-closed 机制扩展 `t3` 键。

### 3.3 预注册要点（prereg 治理）

1. **空间变更定性须 Owner 裁定**：J 维已在 schema（values/active_if 全在），T3a 开 J 属 context 翻转而非增删轴——按 #ARCH-366 先例"budget/判据键非 tracks/axes 不触发作废重开"，但 phase 翻转使 N_raw 翻倍，建议同袋原子提交：`budget_caps.t3_points`+`t3_per_point_seconds_measured` 回填键+honesty 披露块，Owner 签字后冻结。
2. **判据**：主干沿用 17 号文 §一验收判据（t1_t2_handover 已机读实现）；新增 regime 增益判据——J=on vs off 同格配对比较：CRISIS 时段 MaxDD 改善≥5pp（口径真源=`src/zephyr/backtest/regime_validation/c2_extreme_event_protection.py`，c3 分态归因复核"改善应来自预期防御态"）。
3. **成本门不放松**：`cost_gate_in_every_tier=true` 沿用；t3 stage 档位集走 `_resolve_stage_cost_tiers` 增 `t3→全档` 分支。
4. **E0 问闸+GPU 独占+vram.concurrency=1** 不变（t2 波12 语义同款，`_ask_compute_window_gate`）。
5. **失败语义 fail-closed**：J 调度表数据缺失=整格阴性（degraded 不得静默），沿用 NegativeRecord 死亡层机制。

### 3.4 GPU 算力账（0.53s/格口径，源=#ARCH-366/W-173 prereg 回填 gpu_core 薄核冒烟实测）

- T3a 全程（200+7,400+1,800=9,400 格）≈ **83 分钟** GPU 纯算；含成本档扫描（T1 轻档两档）仍在 2h 内。
- 与现行口径的关系：35.33s/格 是 CPU/pandas 全链实测（budget_caps.per_point_seconds_measured），0.53s/格 是 gpu_core 张量核薄循环冒烟——T3a 保持纯向量化才可用后者口径；**任何 M 级模块进考卷都必须 T3b-T0 重标定**，这是 prereg 硬门槛不是估算项。

## 4. 诚实位：回测只能近似的 TDM 环节

| # | 环节 | 实盘真语义 | 回测近似方式 | 失真点 |
|---|---|---|---|---|
| 4.1 | 成交价与延迟（L4-02/03/06） | 盘中多时段下单、SOR 分单、五档盘口吃单 | 考卷：w_t 隐含成交价=close_t 的零延迟收盘成交（`_c4_engine.py:455`）；框架 matching_engine 有 ADV 五分位滑点+冲击腿但考卷未用 | **乐观偏差**：无开盘缺口风险、无自身冲击、滑点只有平档标量。框架件可收敛但耗时口径重算 |
| 4.2 | 做T/日内轮回（P2 全族、L3-11） | 日内 T+0 底仓轮动、竞价/涨速触发 | 原理上不可用日频向量化表达；框架 event_driven tick 引擎"同 tick 成交=对盘口即时性的刻意建模，非前视"（engine 头注自述） | 只有模拟盘/tick 考卷能考；日频考卷的"做T"必然是伪造语义——禁做 |
| 4.3 | 订单九态（L4-07/10/11/12） | 委托/部分成交/撤改/废单/条件单生命周期 | 考卷：无订单对象，全仓成交假设+封板闸；模拟盘 bridge-execute 有真实三闸 OrderManager | 部分成交/撤改在回测域只能参与率近似（INV-UNIT-001 口径），条件单只能日内价格路径重构 |
| 4.4 | 涨跌停/熔断触发时点（S2-02、X-R1） | 盘中实时触发（开板可成交、盘中熔断） | 考卷：日级 close 判定封板（保守拒绝开板日成交）；熔断日级化 | 双向失真：错杀开板可成交日（保守）、止损触发滞后到收盘（激进与保守并存）；框架 matching_engine 三级涨跌停价解析链可收敛 |
| 4.5 | 盘前计划与人的判断（L0 全族、V1-V3） | Owner/盘前运维的判断环节 | 不可回测；模拟盘 plan-bridge 已如实声明：计划姿态仅防御态（空仓）可机械执行，其余记 unexecutable 不伪造仓位（`sim_daily_runner.py:20-30`） | 这是**设计边界不是缺口**——任何"回测计划节点"的实现都是编造 |
| 4.6 | regime 状态机（L1-AGG） | 六态锚定状态机+策略挂载 | T3a 近似=owner_regime_switcher 日级帽（两帽+迟滞）；c1_runner mock 模式自述"规则映射非 HMM 概率，结果无 regime 部署决策价值" | 状态粒度与挂载语义都窄于 TDM state_matrix；格子内容待 Owner 填 |
| 4.7 | 数据前视风险（L9 全消费面） | — | **正向项**：v1 因子全 close 现算 PIT；知识生效日哨兵在册（`_c4_engine.py:816-845` S3 哨兵）；f06 WFA 全链因果/PIT | 新增 M/L 级模块每引入一条新数据线都要过同一哨兵，否则前视 |

**无法判定项（如实声明）**：①X-S1-06 强制清仓、L4-13 三方对账等"非回测域"判定基于模块职责与 [CONSUMERS] 面推定，未逐一运行验证；②battle_map anchors 无 tdm 挂载是查询时点快照（2026-10-05），不排除在途批次将补；③`_SQL_ALL_A`（executor:212-218）的剔 ST 细节未逐行核对 SQL 文本，但 filter_st+load_st_flags 双保险在链路上。

## 5. 附：关键证据文件清单

| 资产 | 路径 |
|---|---|
| TDM 全景图（182 节点/257 边/state_matrix/PP-001） | `config/trading_decision_map.yaml` |
| 网格维度 schema（A-H 九维+J/F/K/I 占位） | `config/position_recipe_grid_schema.yaml` |
| 网格执行器（考卷编排/预算钳制/E0 问闸） | `scripts/backtest/factory_grid_executor.py` |
| 考卷回测引擎（T+1 向量化/封板闸/成本档/DSR） | `scripts/backtest/translated/_c4_engine.py` |
| 框架撮合（涨跌停/停牌/手数/滑点冲击两腿） | `src/zephyr/backtest/core/matching_engine.py` |
| 框架组合账本（逐笔 T+1 锁定） | `src/zephyr/backtest/core/portfolio.py` |
| tick 级引擎（做T 专用） | `src/zephyr/backtest/implementations/event_driven_engine.py` |
| regime 回测验证三件套 | `src/zephyr/backtest/regime_validation/c1_runner.py / c2_extreme_event_protection.py / c3_throttle_attribution.py` |
| Owner 切换器（状态机+冻结考试引擎） | `src/zephyr/strategy_factory/owner_regime_switcher/switcher.py / engine.py` |
| 模拟盘日链（plan-bridge/e4-replay/bridge-execute 三闸） | `scripts/backtest/sim_daily_runner.py` |
| WFA 考卷（E4 三阶段门控） | `scripts/backtest/f06_e4_wfa_exam.py` |
| T1→T2 交接件（验收判据机读） | `scripts/backtest/t1_t2_handover.py` |
| 预注册册（预算帽/耗时口径/honesty） | `config/search_space_prereg.yaml` |
| 全档成本门真源 | `config/exam_scale_cost_gate.yaml` |
| battle_map PG 三表 schema | `src/zephyr/governance/persistence/battlemap_schema.py`（battle_map_steps/anchors/edges） |
| GPU 0.53s/格口径出处 | `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml` #ARCH-366（W-173）；`docs/_working/gpu_rewrite/p1_wiring_benchmark.md` |
