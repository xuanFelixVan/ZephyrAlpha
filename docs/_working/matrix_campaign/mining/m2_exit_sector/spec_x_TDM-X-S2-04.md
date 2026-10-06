---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-11 | TDM-X-S2-04 本地条件单管理

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **L（只登记，不施工）**
- 真源: `config/trading_decision_map.yaml#TDM-X-S2-04`；t3 挖矿 §4.2/§4.3 诚实位

## 1. 结论（负结果主卡之一）

TDM 语义=vn.py 范式本地条件单：止损/止盈触发器本地存储不预占仓位、tick 触发才发限价单、
每 K 线 cancel 重挂、本地 OCO 双停、SellChase 追价状态机、快照龄闸门——**全部是 tick/日内
价格路径对象**。t3 挖矿 §4.2 已定性：日频向量化原理上不可表达日内触发，"日频考卷的条件单"
必然是伪造语义，禁做。

## 2. 归属考法

- 回测域：无（本车道明确不给出向量化代理——把 X-S1-02 的"收盘判定止损"冒充条件单即伪造）。
- 框架在册件（T3c 模拟盘平面考的挂点，只登记）：`src/zephyr/backtest/implementations/
  event_driven_engine.py`（tick 级）、`ch_tick_replay`、`matching_engine.generate_fills_with_tick()`
  （做T专用）、模拟盘 bridge-execute 三闸 OrderManager（`sim_daily_runner.py:50-55`）。
- 缺口定性：tick 级考卷编排层不存在（t3 挖矿 L1 级缺口），属 T3c 立项范围，非 M2 车道。

## 3. 考法

无回测考法。若未来 T3c 开 tick 考卷：触发价判定用盘中 high/low 路径重构（OHLCSTX 同思路），
且必须先建新耗时口径——0.53s/格与 T3b 重标定口径均不适用（tick 数据量纲不同）。
