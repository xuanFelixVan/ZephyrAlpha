---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_l4_exec —— TDM 买卖点与执行（L4 cn_a，15 节点——critical 集中带）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.5。
- 计数: 15 = A1 / B5 / C7（含组骨架 1）/ D2。crypto C-L4 归 st_crypto。
- materiality=critical 节点：L4-09 执行硬约束（TDM:L2672）；chief ENV-11 注"critical 11 集中带"为全 TDM 口径。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-E-L4 | 买卖点与执行（组骨架） | C | L4 | 无（mounts MOD-EX-049/050/055/EXE-AGENTS/TRIG-001；strat daban-sleeve） | TDM:L2397 |
| TDM-E-L4-01 | 分批建仓 | B | L2 | K_capital_ramp=[lump,linear_20d,linear_60d,pyramid]（schema:69-73）；执行器未建 harness | TDM:L2425 |
| TDM-E-L4-02 | 买入时序（尾盘决策） | C | L3 | plan_engine/closing_session_decision；strat STR-MULTIFACTOR-028/STR-MOMTREND-004；考卷隐含 close 成交 | TDM:L2455 |
| TDM-E-L4-03 | 价格锚定 | C | L3 | ex_core/pricing_policy；单一 close 口径 | TDM:L2487 |
| TDM-E-L4-04 | 资金分配多标的 | A | L1 | C_sizing 7 值全精确实现（executor:472-523，头注 T2a） | TDM:L2517 |
| TDM-E-L4-05 | 打板执行专项 | C | L3 | ex_core/daban_execution；封板闸只挡单无排单语义 | TDM:L2545 |
| TDM-E-L4-06 | 执行算法（SOR） | B | L2 | 框架 ADV 五分位滑点腿+Almgren-Chriss 冲击腿在册（matching_engine.py:14-19；execution_simulation）；考卷平档 slippage_bp | TDM:L2576 |
| TDM-E-L4-07 | 条件触发队列 | C | L3 | ex_core/local_order_queue；MOD-RK-41；考卷无订单对象 | TDM:L2611 |
| TDM-E-L4-08 | 突破失败降级 | C | L3 | sell_decision/core/breakout_failure_detector（live 零回测） | TDM:L2642 |
| TDM-E-L4-09 | 执行硬约束（price cage, critical） | B | L2 | 框架 matching_engine 强制 T+1/涨跌停/停牌/100股整数倍（matching_engine.py:18-19）；考卷仅封板闸无手数取整 | TDM:L2672 |
| TDM-E-L4-10 | 订单生命周期状态机 | B | L2 | 框架 portfolio.apply_fill 强制 T+1（portfolio.py:147,195-210）+模拟盘三闸 OrderManager（sim_daily_runner.py:50-55）；考卷无订单对象 | TDM:L2703 |
| TDM-E-L4-11 | 部分成交与撤改处理 | C | L3 | ex_core/fill_handler；框架参与率/冲击隐含部分成交语义（INV-UNIT-001）无撤改 | TDM:L2734 |
| TDM-E-L4-12 | 订单级预检 | B | L2 | ex_core/pre_execution_checker；MOD-RK-07；模拟盘三闸预检在册 | TDM:L2763 |
| TDM-E-L4-13 | 执行容灾对账（三方对账） | D | ND | trading/three_way_reconciliation；4 mounts——实盘账务运维 | TDM:L2795 |
| TDM-E-L4-14 | 执行成本反馈与选型回写 | D | ND | ex_sor/services/execution_quality_scorer；4 mounts——实盘遥测 | TDM:L2826 |

## 2. 缺口与可考性判定

- A1（资金分配）+封板闸近似=考卷执行面全部家底；B5 枚全部是"框架/模拟盘在、考卷未开"——本层是 L2 接口密度最高层，开考主要缺 harness 而非缺模块。
- C7 枚中：L4-02/03=S 级可考（H9 S2：成交价口径 close→next_open/vwap 换源）；L4-11=M 级（参与率帽，H9 M7）；L4-07/10/11 订单九态=L 级新编排（H9 L2）；L4-05/08=live 专项回测化未立项。
- D2 枚=实盘运维（三方对账/成本回写），邻近件框架在册（cost_attribution）。
- 诚实位（H9 §4.1/4.3/4.4）：成交价乐观偏差、订单九态不可日频伪造、封板日级判定双向失真——三处失真声明是本层考卷设计的先决阅读。

## 3. 一句话修复建议

先接 H9 S2（成交价换源）与 M7（参与率帽）把执行层考到"日级可表达子集"的边界，订单九态转模拟盘 sim 平面考（T3c），禁在日频考卷伪造条件单语义。

## 4. 交叉验证

- census §2.1 矛盾项（"13 子环节" vs 实查 14）见 00 §3 C2——本层是计数漂移发生地。
- chief B1 ENV-11（TDM L4=16 含 C-L4）计数一致。
- SPM 邻居：FAC-E7-M-013 Almgren-Chriss（SPM:L4222）与 TDM-E-L4-06 引擎同件——工厂 sim 面与 TDM 执行面共享冲击模型，互链一致。
