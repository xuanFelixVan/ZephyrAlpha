---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-01b | 板块资金流聚合（TDM-E-L2-01-4）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写，纯向量化；数据底座 2021 起可考）
- 真源: `config/trading_decision_map.yaml#TDM-E-L2-01-4`（3 日累计净流入+当日大单净额，权重 25%）

## 1. 机制定义

板块主力净流入 3 日累计+当日大单净额：连续 3 日净流入=资金建仓；当日大单净流出>流入 2 倍=
出货嫌疑。资金流权重占板块总分 25%（01 总评卡消费）。

## 2. 计算式

```
main_net[t,i]   = money_flow.main_net_inflow                     # tushare 主力净流入（元）
big_net[t,i]    = super_large_net_inflow + large_net_inflow      # 大单=超大+大
flow_3d[k,t]    = Σ_{τ=t-2..t} Σ_{i∈k} main_net[τ,i]
big_ratio[k,t]  = Σ_{i∈k} big_net[t,i] / Σ_{i∈k} |main_net[t,i]|
flow_score[k,t] = 100·rank( flow_3d[k,t] )，出货惩罚= big_ratio < -2 时 score×0.8
```

## 3. 向量化实现要点

个股→行业=map+groupby sum（与 L2-01 主通道同一次 join）；3 日累计=rolling(3).sum()；
截面 rank 复用。**纯向量化，不触发 T0 重标定**。

## 4. 引擎接法（M 级）

并入 `sector_surface.sector_strength()` 第四路；缺席降级=TDM fallback 在册（资金维度降权，
结构+动量两维归一化）标 degraded。口径欠账登记：tushare 主力净流入的"主力"定义与 TDM 手工
"大单净流出>流入 2 倍"的阈值系不同口径——阈值 2.0 进 prereg 标定项，禁当冻结常量（负结果
台账 #12 关联）。

## 5. 考法（T0 口径声明）

纯向量化。回测窗约束：money_flow 2021-01 起（实测），更早窗本路自动缺席降级——prereg honesty
块须披露"资金流腿有效窗=2021 起"。

## 6. 数据列名

`c1_market.money_flow`（DESCRIBE 实测）：trade_date, symbol, close, pct_change,
main_net_inflow, main_net_inflow_pct, super_large_net_inflow(_pct), large_net_inflow(_pct),
medium_net_inflow(_pct), small_net_inflow(_pct)。
