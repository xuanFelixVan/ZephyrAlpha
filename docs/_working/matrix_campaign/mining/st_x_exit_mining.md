---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_x_exit —— TDM 离场与应急保命（exit_flow，19 节点——最大缺口带）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.7。
- 计数: 19 = A1 / B3 / C13（含组 3）/ D2。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-X-FLOW | 输出离场信号（终端聚合） | C | L4 | 无 module_ref；strat STR-VREV-001（live 挂载与回测缺口并存，防误读注记见 00 §7.10）；**考卷无任何主动离场**（_c4_engine:561-616 无止损/止盈路径） | TDM:L135 |
| TDM-X-R1 | 应急保命（cross_cutting） | B | L2 | security/access_control/kill_switch；6 mounts（AU×3/L04/RK×2）；模拟盘回撤六态机 defensive_only 已接（sim_daily_runner.py:1318,1356-1394）；**BM-BUY-02-D 已映射** | TDM:L3502 |
| TDM-X-R1-01 | 熔断分级判定 | B | L2 | risk/core/drawdown_state_machine；4 mounts；c2 CRISIS MaxDD 判据在册 | TDM:L3546 |
| TDM-X-R1-02 | 熔断期减仓与持仓处置 | B | L2 | drawdown_liquidation_guard；模拟盘 KILL→execute_kill_switch_liquidation（sim_daily_runner.py:1465） | TDM:L3584 |
| TDM-X-R1-03 | 护盘资产定向加仓白名单 | C | L3 | position/core/defensive_asset_whitelist；state_matrix 防御格内容=Owner 资金门位（AI 禁自填，H9 S4） | TDM:L3617 |
| TDM-X-S1 | 卖出信号收集评分（组骨架） | C | L4 | 无 module_ref（mounts MOD-SELL-006/016）；**BM-SELL-03 已映射** | TDM:L3453 |
| TDM-X-S1-01 | 信号收集与六桶分类 | C | L3 | sell_signal_collector（live） | TDM:L3658 |
| TDM-X-S1-02 | 止损族判定 | C | L3 | stop_loss_strategy；MOD-RK-35/SELL-015；研究样板 ATR3 止损带在册（indicator_consumption_demo.py:34），**考卷零实现**；**BM-SELL-04-B 已映射** | TDM:L3689 |
| TDM-X-S1-03 | 止盈族判定 | C | L3 | take_profit_strategy（live）；**BM-SELL-04-A 已映射** | TDM:L3732 |
| TDM-X-S1-04 | 破位与情绪退潮信号 | C | L3 | breakout_failure_detector（live） | TDM:L3762 |
| TDM-X-S1-05 | 信号融合与紧迫度评分 | C | L3 | sell_signal_fusion_engine；MOD-SELL-008/009；**BM-SELL-02 已映射** | TDM:L3800 |
| TDM-X-S1-06 | 强制清仓绕过通道 | D | ND | strategy_abnormal_exit_orchestrator；MOD-TRADING-011——实盘异常处置 | TDM:L3837 |
| TDM-X-S2 | 离场执行（组骨架） | C | L4 | 无 module_ref | TDM:L3479 |
| TDM-X-S2-01 | 执行方式路由（critical） | C | L3 | sell_execution_planner（live） | TDM:L3875 |
| TDM-X-S2-02 | T+1 与涨跌停约束 | A（近似） | L1 | 封板闸双向+shift(1)（_c4_engine:453-497）；失真=日级 close 判封板（H9 §4.4） | TDM:L3918 |
| TDM-X-S2-03 | 执行时段路由 | C | L3 | ex_sor/core/sell_session_router（live）；考卷单一收盘口径 | TDM:L3958 |
| TDM-X-S2-04 | 本地条件单管理 | C | L3 | ex_core/local_order_queue；日内价格触发语义，考卷无日内路径 | TDM:L4000 |
| TDM-X-S2-05 | 分批止盈执行 | C | L3 | sell_decision/core/scaling_out（live）；考卷调仓日一次性全额 | TDM:L4036 |
| TDM-X-S2-06 | 卖出闭环与退出效率 | D | ND | sell_execution_quality_tracker——执行质量遥测；**BM-SELL-09 已映射** | TDM:L4069 |

## 2. 缺口与可考性判定

- X-FLOW=C 是全图最重单点：离场终端在考卷零语义（被动清仓=跌出 Top-N）。
- B3（R1 保命轨）模拟盘平面已接、网格考卷无——T3b 的 M2（回撤六态机日级向量化）是开考路径。
- C13 中 M 级可考：S1-02/S1-03（H9 M1：ATR 止损带/移动止盈/目标价向量化，研究样板可翻译）、S2-05（分批止盈随 M4）；L 级：S2-04 条件单（tick 平面）；D2 枚=实盘遥测。
- BM 映射集中带：11 条 tdm_node_id 映射中 **8 条落 X/P 族**（H9 §1.9"讽刺点"：作战地图挂 TDM 最密处=考卷零实现带）——本族是 BM↔考卷落差最大层。

## 3. 一句话修复建议

T3b 前置落 M1+M2（止损止盈档+熔断档作新增考维，重标定耗时口径后开考）；R1-03 防御格内容留给 Owner 门位，禁代填。

## 4. 交叉验证

- H9 §1.7 判定全转录对平；chief B1 ENV-13（exit_flow=19）计数一致。
- TDM state_matrix：euphoria/distribution 两态 PP-001 无防御型 sleeve、格子 pending-owner-adoption（H9 §1.2 R1-03 证据引 state_matrix cells）——六态名与 24 cells 计数两图一致（00 §4）。
- SPM 邻居：FAC-E7-M-022 月度危机演练件（SPM:L4327）与 R1 熔断族同域；FAC-E8-M-031 前瞻概率止损（SPM:L4717，forward_stop_loss）是 X-S1-02 的工厂侧近亲——止损件分散三处，矩阵考试宜合并命题。
