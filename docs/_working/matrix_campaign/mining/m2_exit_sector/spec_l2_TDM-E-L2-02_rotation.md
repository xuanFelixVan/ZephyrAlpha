---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-02 | 轮动序列追踪（覆盖 TDM-E-L2-02 / -02-1 RRG / -02-2 单板块预警）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（RRG 与轮动速度计全日级可算；预警三信号日级代理）
- 开源依据: RRG=Julius de Kempenaer JdK RS-Ratio/RS-Momentum 双轴归一化四象限
  （Leading +/+ → Weakening -/+ → Lagging -/- → Improving +/-，顺时针旋转；
  StockCharts ChartSchool/relativerotationgraphs.com 权威口径）；D90 终裁已给
  rotation_velocity 口径。真源: `trading_decision_map.yaml#TDM-E-L2-02`

## 1. 机制定义

- **02 轮动序列**：谁在连涨+资金连进=接棒区，谁在连跌+资金连出=撤离区；输出接棒榜单。
  D90 已落码口径：`rotation_velocity=板块涨幅排名 5 日变动绝对值均值，>250 日窗 75 分位=
  fan_market_flag 电风扇市；轮动强度分位>80%=无主线信号`。
- **02-1 RRG**：板块相对大盘 RS 双轴四象限，目标=刚进 Leading 象限的板块；象限转移须连续
  2-3 日确认，单日跳变不采信；板块日 K 不足 62 日不参与（DualEma 最小数据量）。
- **02-2 单板块见顶预警**：RSI 日线>75、板块成交额创 20 日新高但指数滞涨（放量不涨）、
  龙头股率先破位；命中两个=该板块从候选池降级。

## 2. 计算式

```
RS[k,t]        = IND_close[k,t] / BENCH_close[t]                 # 基准=全行业等权指数（fallback 在册：
                                                                   880001 缺失→全板块均值基准）
RS_ratio[k,t]  = EMA_14(RS[k,t]) / cross_sectional_mean(EMA_14(RS))[t] × 100
RS_mom[k,t]    = EMA_14( RS_ratio[k,t] / RS_ratio[k,t-1] - 1 ) × 100 + 100
quadrant       = Leading(+,+) / Weakening(-,+) / Lagging(-,-) / Improving(+,-)
confirm        = 象限连续 ≥2 日才切换（rolling 众数或两日一致判定）
entry_flag[k,t]= quadrant 由 Improving→Leading 转移且 confirm 通过
# 02-2 预警
warn_rsi       = RSI14(IND_close) > 75
warn_vol       = IND_amount[t] == rolling20max 且 IND_ret5 ≤ 0     # 放量不涨
warn_leader    = 板块内 rank1 个股 close < MA10                    # 龙头破位日级代理
degrade        = (warn_rsi + warn_vol + warn_leader) ≥ 2 → 候选池降级
```

## 3. 向量化实现要点

EMA/RSI/rolling max 全算子级；象限判定=两个布尔矩阵；confirm=shift 后逐位与。
**纯向量化，不触发 T0 重标定**。

## 4. 引擎接法（M 级）

`sector_surface.rotation(panel) -> {quadrant, entry_flag, fan_flag, degrade}`；
executor 维 `X_sector=rrg_top` 档：候选池=entry_flag 板块∩L2-01 score 前 15%。
BM-SEL-08/09 映射（battle_map_steps 已挂 TDM-E-L2-02/03）随之首次获得回测实体。

## 5. 考法（T0 口径声明）

纯向量化。**窗口负结果**（#9）：RRG 62 日最小窗在 kline_sector（2025-07 起）上仅覆盖
~12 个月可考——深回测 RRG 必须走 L2-00 主通道行业聚合指数（1990 起），880 指数只作
2025-07 后对照窗。prereg 披露双底座口径差异（880 含概念/地域板块 728 个 vs 申万 31 个，
两套板块域不可混池）。

## 6. 数据列名

主通道=L2-00 行业聚合宽表（kline_daily×industry_class）；对照窗=`c1_market.kline_sector`
（trade_date, code, open/high/low/close, volume, amount）。
