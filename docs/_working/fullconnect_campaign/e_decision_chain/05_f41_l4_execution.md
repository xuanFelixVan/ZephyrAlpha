---
ttl: task_bound
title: F41 L4 买卖点与执行——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f41-l4-exec-20260927
---

# F41 L4 买卖点与执行——挖干案卷

> 一句话：执行层总枢纽——分批/时序/价格锚/资金分配/打板/SOR/条件队列/突破降级/硬约束/订单状态机/部分成交/订单级预检/容灾对账/成本反馈 14 子环节；与 EX 组（F53-F58）强交界，本卷挖 TDM 判据面，执行基建血肉引用 M7/L07 册不重挖。节点组=TDM-E-L4+01..14 共 15 节点（今日 yaml:2144-2567 机数=15，零漂移）。总册 built｜**P0**｜T8；上游 F40/L0/F59，下游 F53-F58。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | F40 候选池（sleeve 标签+顺位分）；F37 L0 时序窗口与边界；F59 风控限额（precheck 消费）；kill_switch |
| ②数据原料 | 盘口/时序窗口表/券商回报/成本模型实时估算（预期冲击+佣金≤预期收益 1/3）；trade_log（order_type 全 market 无 algo_id——归因字段缺，known_data_gaps 册引） |
| ③状态输出 | 订单流（7 态 OrderStatus 显式封闭流转表）+质量三档评分+滑点分量拆解 |
| ④下游消费 | F53 订单生命周期/F57 结算对账/F58 成本反馈；EXA 六算法选型（algo_refs 全挂） |
| ⑤自动化触发 | continuous 横切件（L4-07 tick 驱动条件队列/L4-10 状态机/L4-13 容灾）事件驱动非 cron；盘后 L4-14 成本反馈回写（册引） |
| ⑥缺口债 | 九态判据-码面差异（唯一 P0 级语义债）；trade_log 归因字段缺；L4-14 反馈环断链（选择器不消费评分器）；BT-P2-047..053 valid 与 plan=None 并存 |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/ex_core/`：67 件 .py（实扫）。TDM L4 挂点族：order_manager.py（:136-149 VALID_TRANSITIONS 册引）、order_splitter.py（70/50/30 分批，ALGO_FLOW 外迁）、pricing_policy.py、batched_position_builder 相关（14:50-14:57 主窗+14:57-15:00 收盘竞价兜底）、breakout_failure_detector.py（sell_decision 域同名件双锚，册引）、pre_execution_checker.py（gate 族今日实锚 :243 kill_switch_gate/:272 live_env_gate/:286 session_window_gate/:309 snapshot_gate/:321 rule_id）、fill_handler.py、price_cage.py、order_enums 锚 src/zephyr/shared/contracts/enums/order_enums.py（7 态今日实锚 :52-63）。
- 域 `src/zephyr/ex_sor/`：29 件（core 13+services 4+__init__×2，今日 ls 实扫）。core/algo_execution_selector.py（EXA 六件）、algo_trading_engine.py、execution_scheduler.py、optimal_order_router.py、sor_agent.py、broker_adapter_manager.py、sell_session_router.py（X-S2 交界）；services/slippage_analyzer.py+execution_quality_scorer.py+transaction_cost_optimizer.py+t0_cost_model.py。
- daban 专项族（ex_core 内，今日实扫 7 件）：daban_execution/daban_exit_decision/daban_instant_circuit_breaker/daban_load_producer/daban_monitors/daban_named_functions/daban_signal_decision+pit_safety。
- 14/14 module_ref 在盘零缺件（册引 f41 册 §四）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| L4-07 条件队列/L4-10 状态机/L4-13 容灾 | **事件驱动接线** | continuous 激活+tick 驱动（册引）；order_manager 状态机 7 态今日实锚 |
| L4-02 买入时序 | **判据接线（语义分层）** | 决策侧 14:45-15:00 与执行侧 batched_position_builder 14:50-14:57 双窗（册引） |
| L4-06 EXA 选型 | **半接线（反馈断）** | **今日 grep algo_execution_selector.py scorer/quality 零命中**——L4-14 断链复核仍断（与 yaml:2550 自认注"L4-14 断链实证 2026-09-10"一致；L07 SKEL EXE-5 09-25 复核同判=D34） |
| L4-12 订单级预检 | **接线（口径漂移）** | gate 族四 gate+rule_id 今日实锚；节点散文"五查"与 check_id 非一一对应（禁做清单入口待核） |
| L4-10 九态判据 | **判据先行未回写** | 码面 7 态无 New/Accepted/Suspended/PendingCancel（今日实锚）；QMT 风格九态映射桥缺失 |

**骨架勘误**：无新增（f41 册三处结构性欠账今日独立复核全部成立：九态映射桥缺、归因字段缺、反馈环断）。总册 F41"P0"分级与 materiality=critical（L4-09）一致，维持。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G41-1 | L4-14 反馈环断链（选择器不消费评分器） | 选择器增评分输入（0.5-1 天，F58 扩册交界）——断链三零件全 production 只差最后一米 | **P0** |
| G41-2 | 订单九态判据-码面差异（语义债） | a) 桥层补券商态→内部态映射表（F53 交界，1 天）+b) 节点注对齐码面（S4 D 裁定） | **P0** |
| G41-3 | trade_log 归因字段缺（order_type/algo_id/排板标记） | 回测流水 schema 增字段（BT/M1 交界）+重放窗口；字段落地前按全量代理口径出数并披露（BT-P2-045/046 caliber_note） | P1 |
| G41-4 | BT-P2-047..053 valid 与 plan 缺失并存 | 核 c1_backtest.node_verdict 台账后补 plan 或降级标记 | P1 |
| G41-5 | BT-P0-003 成本模型（生死线三件套之一）pending | plan 已冻结 2026-09-12，待批次决策点开考（cross：L4-09+P2-01/03+X-S2-01） | P1 |
| G41-6 | precheck"五查"散文与 gate 族码面口径漂移 | 节点注对齐 check_id 清单（0.5 小时，S4 场景） | P2 |
| G41-7 | 双层执行算法选择器并存零互认（MOD-XS-011 ∥ MOD-EX-062；成本真源 CST-ASTOCK-001 vs cost_model_calibration 冲突未回写） | 内收 w5_1 同域重复簇收敛（L07-C03/C08 已立，引用不重立） | P1 |

## 五、自审闸三态

**挖干可施工**（验证状态全组最佳：13 件中 12 valid；三件结构性欠账今日复核成立且均小施工；EX 组交界引用 L07/M7 册不重复立工单）。

### 待裁
- 双层执行算法选择器与双成本真源收编方向——L07-C03/C08 工单已有，收编裁定归 Owner（内收 w5_1 同窗）。
- RL 执行（XS-008 硬边界已码）启用时点——远期候选，Owner 门。

## 六、复跑命令

```bash
sed -n '52,63p' src/zephyr/shared/contracts/enums/order_enums.py      # 7 态实锚
sed -n '136,149p' src/zephyr/ex_core/order_manager.py                 # VALID_TRANSITIONS
grep -n "check_id=" src/zephyr/ex_core/pre_execution_checker.py | head
grep -cn "scorer\|quality" src/zephyr/ex_sor/core/algo_execution_selector.py  # =0 断链复验
grep -c "node_id: TDM-E-L4" config/trading_decision_map.yaml          # =15
```
