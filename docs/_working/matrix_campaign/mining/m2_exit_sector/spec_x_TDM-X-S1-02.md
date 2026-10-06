---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-04 | TDM-X-S1-02 止损族判定（M1 核心卡）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写，日级可表达但带持仓记忆=路径依赖；X 族最小考卷核）
- 开源依据: vectorbt `Portfolio.from_signals` 的 `sl_stop/tsl_stop` 为百分比离场价+Numba 逐列
  编译例程（OHLCSTX 停止信号生成器，`vectorbt.signals.generators`），同 bar 触发序列在向量化
  模式下不可分辨、以 close 判定——本卡采用同一口径（收盘判定）并如实披露其失真；
  Chandelier Exit 公式=highest(close,n)−m·ATR(n)（awesome-quant 在册多实现同式）。
  真源: `config/trading_decision_map.yaml#TDM-X-S1-02`（五路止损+D91 终裁+2026-09-18 锚修正）

## 1. 机制定义（五路并行，同层取最严）

1. **Chandelier 悬停**：亏损区 N=10/M=3.0、盈利区 N=22/M=2.0；锚=`max(入场后最高收盘, 入场价)`
   （2026-09-18 深度审查修正，消除盈利期止损悬崖）。
2. **固定生死线**：-7%。
3. **支撑破位（D69 双触发）**：硬底（-7%~-8% 或 2×ATR(14) 单日，立即离场）+软确认（跌破支撑→
   次日开盘 30 分钟观察窗：收复开盘价+量能配合=持有；未收复/窗口结束=离场）；站稳=收盘连续
   2 日收于支撑上方。**软确认的"次日开盘观察窗"日级降维为"次日收盘是否收复支撑位"**。
4. **时间止损**：盈利仓 5 日不涨 / 亏损仓 3 日（1×ATR/5日时间止损注记）。
5. **分时破位**（盘中跌破分时均线 30 分钟）——**日级不可表达，负结果裁剪**（99 负结果 #1）。
6. 棘轮：止损位只升不降 `stop[t]=max(stop[t-1], 本期新止损)`；同层多档取最严（距离最小者先生效）。
   fallback：ATR 缺失→固定 4%（短线）/8%（中长线）降级，标 degraded。

## 2. 计算式（持仓日级，i=标的）

```
ATR(n)_t,i = mean_{k<t} [ max(H-L, |H-C_prev|, |L-C_prev|) ] 滚动 n 日     # True Range 均值
anchor_t,i = max( cummax(C_{entry..t})[i], entry_i )                       # 同构锚（2026-09-18 修正）
chandelier_亏损区 = anchor - 3.0·ATR(10)； 盈利区 = anchor - 2.0·ATR(22)
fixed_stop        = entry_i × (1 - 7%)
time_stop 触发    = 持仓 t-entry≥5 且 C_t ≤ C_{t-5}（盈利仓判据=浮盈>0 时 5 日不涨；
                    浮盈≤0 时 t-entry≥3 且 C_t ≤ C_{t-3}）
stop_t,i          = max( 各路止损价, stop_{t-1,i} )                        # 棘轮
触发              = C_t < stop_t,i                                          # 收盘判定（vectorbt 同口径）
```

entry_i=建仓日执行价（随 exec_caliber：close/next_open/vwap，T6 S2 已接线）。

## 3. 向量化实现要点

- ATR/锚/触发布尔：全 DataFrame 滚动算子（cummax/rolling.max/shift），零逐元素循环。
- **持仓记忆段**（entry、stop 棘轮、时间止损计数）：T 行循环 × N 维 numpy 向量，
  与 `apply_fillability_gate`（`_c4_engine.py:495-519`）的 prev 行循环同形——引擎既有模式，
  非新范式。indicator_consumption_demo `b1_volatility_stop`（ATR 止损带研究样板）可翻译。
- forward_stop_loss（panic_rebound_depth.py:149）与模拟盘 legacy stop_loss 路径为参考语义，
  不直接复用（考卷是权重路径不是逐笔持仓）。

## 4. 引擎接法（M 级）

- 接线点=executor 侧 evaluate_recipe 产物 `w_tgt` 之后、引擎 `_backtest_core` 的
  `apply_fillability_gate` 之前：`w_exit = apply_stop_family(w_tgt, closes, highs, lows, params)`，
  权重改写规则=触发日 `w_exit[t,i]=0`（清仓）或预登记的减半档；未触发日 `w_exit=w_tgt`。
- 顺序铁律：离场变换→封板闸（跌停禁卖已由闸兜底=想卖卖不掉的残余仓自然保留）→回测核。
- schema：新增维 `X_stop=[off, atr_chandelier, fixed_7pct, time_stop, composite]`——schema
  修订须裁定（施工前置）；参数档（N/M/百分比）进 prereg 不进 schema（禁维爆炸）。

## 5. 考法（T0 口径声明——本卡为路径依赖首卡）

棘轮+持仓记忆=T 行循环，**破坏纯向量化：T3b-T0 必须先重标定 per_point_seconds 再定 T1/T2
点数（0.53s/格 gpu 薄核口径与 35.33s/格 CPU 旧口径均禁沿用），fail-closed 沿用
`config/search_space_prereg.yaml` 钳制机制；数据缺失（ATR 窗不足）=降级 fallback 并标
degraded，禁静默**。t3 挖矿 §3.1 已预算：CPU 口径 35.33s/格 → 7,400 格≈72.6h 超 12h 单作业帽，
重标定后按实测重切点数。

## 6. 数据列名

`c1_market.kline_daily`：`trade_date, symbol, open, high, low, close`（high/low 为本卡新增
load_px fields；close 已有）。ATR 全程自算，禁引外部指标表第二口径。
