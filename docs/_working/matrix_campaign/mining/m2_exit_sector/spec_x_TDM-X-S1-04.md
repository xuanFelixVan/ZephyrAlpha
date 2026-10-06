---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-06 | TDM-X-S1-04 破位与情绪退潮信号

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M（部分）**——突破失败日级可考；情绪退潮=J 维已接线代理；龙虎榜派发=负结果裁剪
- 真源: `config/trading_decision_map.yaml#TDM-X-S1-04`（三路情绪侧信号+D68/D69/PIT 纪律）

## 1. 机制定义与考卷可考性切分

| TDM 三路 | 考卷可考性 | 处置 |
|---|---|---|
| 突破失败（买入理由消失：突破价跌回+量能萎缩，连冲 3 次失败→强制清仓） | **日级可表达** | 本卡 M 级实现 |
| 情绪退潮（L1 六段 distribution+情绪票加权卖出） | 近似可考 | 复用 J_regime_switch 日级帽调度（T6 ①已接线）作退潮代理；六态挂载矩阵格子 pending-owner=如实差距 |
| 龙虎榜派发（高位游资上卖方榜/三日榜净卖出） | **不可考** | LHB 数据线无考卷消费+T 日 18:00 后发布 PIT 窗构造（M-43）未建——负结果 #4 |
| 天地板规则（D99 已改个股级） | 可考（封板掩码派生） | 并入突破失败桶：持仓股自身涨停次日跌停=观察名单标记 |

## 2. 计算式（突破失败，日级）

```
breakout_day_t,i = C_t,i > cummax(C_{t-20..t-1})[i]                       # 20 日新高=突破日
fail_t,i         = C_t,i < breakout_ref_i × (1 - giveback)                # 跌回突破价下方
vol_shrink_t,i   = amount_t,i < 0.7 × mean(amount_{t-5..t-1})[i]          # 量能萎缩（除权日 D68：分母用复权口径）
consec_fail_i    = 滚动窗口 20 日内 fail 次数 ≥ 3 → 强制清仓信号（喂 X-S1-06 语义位）
```

giveback/回看窗进 prereg 标定；连冲 3 次的"冲"=两次失败间隔内未再创 20 日新高（滚动计数，
向量化=布尔卷积）。

## 3. 向量化实现要点

突破判定=cummax+shift；量能条件=rolling mean 比较；连冲计数=rolling(sum)——全零行循环，
本卡是 X 族里唯一**无持仓记忆**的桶（信号层而非仓管理层），可与因子面同趟计算。

## 4. 引擎接法（M 级）

信号面并入 `exit_signal_surface`（X-S1-01 卡）`B_signal` 桶；强制清仓（K≥3）挂
`forced_exit` 布尔宽表透传 X-FLOW 审计列。情绪退潮腿=J 维格点语义（非本卡新代码），
在 prereg honesty 块声明"帽调度≠六态挂载"的已知失真（t3 挖矿 §3.2 同款披露）。

## 5. 考法（T0 口径声明）

本卡信号层纯向量化（0.53s/格口径不受影响）；但 K≥3 触发的强制清仓作用到仓管理层时与
X-S1-02 行循环合并执行——**凡与仓管理联跑的格点仍受 T3b-T0 重标定约束（禁用 0.53s/格）**。

## 6. 数据列名

`c1_market.kline_daily`：close/high/low/amount（amount 为本卡新增字段）。
跌停观察名单：`market_data.stk_limit` limit_up/limit_down（在册）。
龙虎榜：无（负结果）。
