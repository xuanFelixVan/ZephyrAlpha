---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_p_daytrade —— TDM 持仓管理/做T/加仓（position_flow，18 节点）

- 真源: `config/trading_decision_map.yaml`；行号=TDM:L*。类别=H9 §1.6。
- 计数: 18 = A3 / B4 / C8（含组 2）/ D3。

## 1. 族内节点全清单与接线现状

| node_id | 名称 | 类别 | 接线级 | 引擎旋钮/模块 | 行 |
|---|---|---|---|---|---|
| TDM-P-FLOW | 输出持仓信号（终端聚合） | A | L1 | 每日权重路径=持仓路径（weights ffill）；strat STR-MULTIFACTOR-098/099 | TDM:L106 |
| TDM-P-P1 | 持仓体检（组骨架） | C | L3 | position/core/position_checkup_orchestrator；MOD-POS-016 | TDM:L2863 |
| TDM-P-P1-01 | 持仓对账与台账快照 | D | ND | position_state_machine；4 mounts——账务运维 | TDM:L2943 |
| TDM-P-P1-02 | 持仓分级与监控频率 | D | ND | sell_decision/core/position_triage；MOD-POS-007 | TDM:L2978 |
| TDM-P-P1-03 | 买入逻辑存活判定 | C | L3 | plan_engine/thesis_survival；回测域零引用 | TDM:L3017 |
| TDM-P-P1-04 | 风险否决体检（A 止损引擎） | C | L3 | risk/core/ashare_stop_loss_engine；MOD-POS-008/017；**BM-RC-10 已映射此节点**（H9 §1.9：tdm_node_id 11 映射之一） | TDM:L3049 |
| TDM-P-P1-05 | 组合级持仓体检（漂移监控） | A（近似） | L1 | D2_rebalance_trigger=drift_band 漂移带精确实现（executor:546-577）；仅漂移一腿 | TDM:L3083 |
| TDM-P-P1-06 | 体检结论与动作清单 | D | ND | position_adjudication_center——裁定中心运维 | TDM:L3118 |
| TDM-P-P2 | 做T与加减仓（组骨架） | C | L4 | 无 module_ref（mounts MOD-RK-40；strat intraday-surge-fall/orderbook-imbalance/vwap-reversion/STR-DABAN-023） | TDM:L2888 |
| TDM-P-P2-01 | 做T资格与成本前置（T+1 可卖, critical） | B | L2 | 日级 T+1 隐含实现（w.shift(1)）；逐笔锁定在框架 portfolio（portfolio.py:147）；做T 级资格无考卷 | TDM:L3153 |
| TDM-P-P2-02 | 做T策略调度 | C | L3 | sell_decision/core/t_trade_coordinator；MOD-AU-011；日频向量化原理上不可表达日内 T+0（H9 §4.2） | TDM:L3193 |
| TDM-P-P2-03 | 做T闭环与成功判定（critical） | C | L3 | intraday_t0/t0_trading_pipeline（live） | TDM:L3237 |
| TDM-P-P2-04 | 减仓与再平衡 | A | L1 | D1 调仓频率 4 值+D2 触发+H 换手惩罚 λ（executor:546-577,530-545） | TDM:L3276 |
| TDM-P-P3 | 加仓决策（组骨架） | B | L2 | K 维 pyramid 占位（schema:71） | TDM:L2916 |
| TDM-P-P3-01 | 加仓资格门 | B | L2 | position/core/pyramiding_rules；K 维 harness 未建 | TDM:L3315 |
| TDM-P-P3-02 | 金字塔加仓规则 | B | L2 | pyramiding_rules（同上） | TDM:L3351 |
| TDM-P-P3-03 | 加仓量级与风险核算 | C | L3 | position_sizing_engine（live） | TDM:L3391 |
| TDM-P-P3-04 | 加仓时点与执行 | C | L3 | position_limit_enforcer（live） | TDM:L3421 |

## 2. 缺口与可考性判定

- A3：P-FLOW/P1-05/P2-04 已在考卷行使——持仓半边的考卷家底=漂移带+调仓引擎。
- B4（P2-01/P3 族）：K_capital_ramp 开闸即考（H9 M4：lump/linear/pyramid 均可向量化后处理），金字塔族是 M 级最近路径。
- C8 分层：P1-03（M5 逻辑存活判定=日级可表达）、P1-04 止损引擎（归 X 族 M1 一并考，止损在 H9 §1.7）、P2-02/03 做T=**原理上不可日频表达，只有 tick/模拟盘能考**（H9 §4.2：日频"做T"必伪造，禁做）；P3-03/04 live 件回测化未立项。
- D3：账务/监控/裁定运维，天然不进回测。

## 3. 一句话修复建议

P3 金字塔随 H9 M4 开 K 维 harness（M 级）；P1-03 随 M5（thesis survival 向量化）；P2 做T 全链明确"只在 sim/tick 平面考"并写进 prereg honesty，禁日频伪造。

## 4. 交叉验证

- H9 §1.6 判定全转录对平；"近似 A"（P1-05 仅漂移一腿）已注记。
- chief B1 ENV-12（position_flow=18）计数一致。
- BM 映射：battle_map 11 条 tdm 映射中 BM-RC-10→TDM-P-P1-04 落本族（H9 §1.9，PG 快照）——作战地图挂了、考卷未跟，H9"讽刺点"在案。
- 图13 盘中段资金流 4 槽/实时 5 分钟（census §3）是 P2 做T 的运营时序面；STR-DABAN-023 三卡 T 日信号生成件=GAP-2（chief 02 §1）——本族 P2 与实盘 Flip 组直接相邻。
