---
ttl: task_bound
title: "F46 S2 离场执行——方式路由/T+1 涨跌停约束/时段路由/条件单/分批止盈/闭环（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F46 · S2 离场执行（TDM-X-S2-01..06）

> 上游=F45 S1-05/06、P2-03/04、F-C2-01 强裁、F47 R1 broadcast；下游=F53 订单生命周期/F55 SOR、F-C3-01 归因。
> 证据基线：02_tdm_decision/13 册（2026-09-25）+本日（09-27）src/ 独立复核。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | 仲裁序（外审 R2-05/D95）：X-R1/S1-06 强清中断 ≥ F-C2-01 强裁 > P2-03/04 纪律强平 > S1-05 常规融合；地图锚 config/trading_decision_map.yaml:3500（X-S2-01）|
| 下游消费 | S2-06→F-C3-01（daily）+→E-L4-12 冷却清单；各执行通道→F53 订单（planner→订单参数，M7-03 册实证）|
| 自动化触发 | **零编排**——本日复证：sell_execution_planner/scaling_out/sell_execution_quality_tracker/sell_session_router 四件包外消费者 grep 全仓=**零命中**（仅自身域内）；t1_sellable 例外（t1_sellable.py:5 CONSUMERS 实锚 batched_position_builder 等 6 方）|
| 真源与注册表 | 地图 yaml:3500-3722（S2 六节点）；42 号备忘录 §3.7/3.8/3.11+§3.8.1；CST-ASTOCK-001；#ARCH-DATA-020（ST ±10% 修表已清偿）|
| 门禁与质量尺 | ai_autonomy：S2-01/02/04/05=paper、S2-03/06=auto；S2-01 materiality=critical+monthly |
| 当前运行状态 | **黄**——库成/编排缺/BT-P0-003 中 X-S2-01 过（858 笔滑点 2.65bp≤20bp，成本逐笔零偏差）；其余 X 流节点 pending（F52 卷汇总）|

## 二、子模块三级枚举（本日实扫 wc -l）

- **sell_decision.core**（决策→执行计划面）：sell_execution_planner.py 333 行（MOD-SELL-019，强制清仓绕融合/跌停排队/T+1 纪律 INVARIANTS）｜scaling_out.py 165（分批止盈 Exit Ladder）｜sell_execution_quality_tracker.py 210（三率闭环）——三件全纯库
- **ex_sor.core**（时段路由面）：sell_session_router.py 339 行（MOD-XS-016，竞价逃命/14:57 深市不可撤/跳水窗，纯函数）——与 planner 相邻未合流（M7-05 B4 待裁）
- **ex_core**（本地条件单面）：local_order_queue.py 271 行（MOD-L06-001，vn.py 范式 tick 触发+cancel 重挂；production，qmt_file_bridge_integration.py:165 已接线——S2 六件中唯一有真实生产通路）
- **position.core 复用件**：t1_sellable.py 66 行（S2-02 可卖额度，wired 6 消费方）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| S2-02 可卖额度 | 已接线 | t1_sellable 6 消费方 grep 实锚 |
| S2-04 本地条件单 | 半接线 | local_order_queue 已入桥装配（integration:165），但触发器注册/OCO 刷新无人编排 |
| S2-01/03/05 计划路由 | 码成闸空 | planner/scaling_out/session_router 包外零消费（本日独立复证与 13 册同判）|
| S2-06 闭环 | 码成闸空 | quality_tracker 零消费+M-39 sleeve 治理状态表未施工（冷却/连败阶梯无处落盘）|

### 骨架勘误
总册 F46 行状态=**built**——按四要素（自动化③）应判 **partial**：执行计划三件零生产调用，唯一 P0 级验证（X-S2-01）过但验证≠接线。建议骨架本行改 partial（wiring_gap_inventory §1.4 的 41 未完全接线清单亦未收编 F46，二次勘误）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | S1 扫描→S2-01 路由器编排缺位（与 F45 同根同一工单） | 挂 sell_decision 编排工单（3-5 天， Fusion 挂 bar 事件链后直接接 planner）| P0 |
| 2 | S2-06 状态持久化载体缺（M-39） | sleeve 治理状态表施工（与 F50 C3-02 状态面同批）| P1 |
| 3 | M-24 跳空分档/节前决策表挂本节点 | 施工归 position 隔夜风险批次（跨车道，勿代修）| P1 |
| 4 | 验证欠账 BT-P3-031..035 plan=null | 批次决策点预注册后重跑（F52 卷统筹）| P1 |

## 五、自审闸三态
**挖干可施工**（六节点判据/边/验证状态齐；缺口 1 有修法有量级；P0 编排与 F45 同工单两段，不重复立项）。

## 六、复跑命令
```bash
grep -rln "sell_execution_planner\|scaling_out\|sell_execution_quality_tracker" src/zephyr scripts --include="*.py" | grep -v __pycache__ | grep -v sell_decision   # 零命中=编排缺复证
grep -n "sell_session_router\|local_order_queue" src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py   # :165 local_order_queue 接线锚
wc -l src/zephyr/sell_decision/core/sell_execution_planner.py src/zephyr/ex_sor/core/sell_session_router.py
sed -n '3500,3512p' config/trading_decision_map.yaml
```
