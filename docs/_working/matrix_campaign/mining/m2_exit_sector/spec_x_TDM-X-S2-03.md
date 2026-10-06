---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-10 | TDM-X-S2-03 执行时段路由

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **S**（复用 T6 ②已接线 exec_caliber 维，零新引擎代码）
- 真源: `config/trading_decision_map.yaml#TDM-X-S2-03`；executor T6 头注 ②

## 1. 机制定义与考卷投影

TDM 语义=时段通道分裂路由（深市 14:57 集合竞价不可撤/沪市尾盘可撤；竞价逃命单 9:15 挂跌停价；
14:30-14:45 跳水窗谨慎；14:50 决策窗做T收口）。

日频考卷的可考投影=**卖出成交价口径选择**：竞价逃命≈次日开盘价成交、尾盘决策≈当日收盘价
成交。T6 ②已把 `exec_caliber=close|next_open|vwap` 透传引擎（`_backtest_core` rets 换源，
缺 px_exec=ValueError 禁静默回落）——本卡剩余工作只是把"卖出腿的口径"从"全仓口径"细化为
"买入腿 close × 卖出腿 next_open"的混合口径（若 A/B 对照需要）；同口径对照今日即可开考。

## 2. 计算式（混合口径）

```
rets_buy_leg  = close.pct_change()                      # 建仓成本仍 close 口径（对照不变）
rets_sell_leg = exec_interval_returns(px_exec)          # 卖出腿换 next_open/vwap
gross_t       = Σ_i [ w_buy[i]·rets_buy[t,i]·held - w_sell[i]·(1 - rets_sell[t,i]) ] 的标准
                权重路径等价式（实现=卖出日权重在 px_exec 口径下结算，等价改写禁凭口算，
                以引擎 exec_interval_returns 单一真源为准）
```

## 3. 向量化实现要点

`exec_caliber≠close` 时引擎恒走 pandas 原路（GPU 核仅 close 等形面，`_GUARD_EXEC_CALIBER`
守卫在册）——纯向量化，0.53s/格口径按 pandas hoisted-cpu 档计。

## 4. 引擎接法（S 级）

- 已接线：`run_backtest_full(..., exec_caliber=, px_exec=)`（`_c4_engine.py:603-639`）。
- 本卡动作：考卷维 `exec_caliber` 进 t3 家族 prereg 抽样集（`_vwap_from_amount_volume`
  量纲哨兵已备）；A/B 判据=同格 next_open vs close 的净 Sharpe 差（执行价乐观偏差量化，
  诚实位 §4.1 的实测收敛）。
- 不可考子集=负结果 #5（14:57 不可撤/排单位次/跳水窗）。

## 5. 考法（T0 口径声明）

纯向量化，不触发 T0 重标定；但耗时口径按 `_GUARD_EXEC_CALIBER` 强制 CPU 档（gpu 薄核资格
否决），prereg 的 t3_per_point_seconds_measured 须按 CPU 档回填——这是口径换挡不是重标定。

## 6. 数据列名

`c1_market.kline_daily`：open（next_open 口径新增消费）；vwap 由
`amount×100/volume` 派生（量纲哨兵 `_vwap_from_amount_volume`，kline_daily volume 混纲
'手/股'按 data_source 归一，INV-UNIT-001 同源纪律）。
