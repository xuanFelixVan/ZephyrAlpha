---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-05 | TDM-X-S1-03 止盈族判定（M1 配套卡）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写，与 X-S1-02 共享 ATR 面+持仓记忆；D50 欠账"峰值回撤兑现"在此落位）
- 开源依据: vectorbt `tp_stop`（百分比止盈价，OHLCSTX 同生成器）+ trailing stop（`tsl_stop`/
  `sl_trail`）成熟做法；Chandelier 盈利区跟踪=trailing 的 ATR 变体。真源:
  `config/trading_decision_map.yaml#TDM-X-S1-03`（止盈三式）

## 1. 机制定义（止盈三式）

1. **移动止盈**：Chandelier 盈利区 2×ATR(22) 跟踪（同 X-S1-02 盈利区公式），只升不降；
   涨越多回撤容忍越大。
2. **峰值回撤兑现**（D50 欠账，短线最大利润漏点="赚过没拿住"）：每仓记历史最高浮盈 peak_pnl，
   从峰值回落 30% 强制兑现。
3. **目标位**：预期涨幅达成即了结（目标档进 prereg；打板票"次日不板走"语义=涨停次日不续板
   即出——封板掩码已可考）。
   止盈条件只看市场状态变量（信号/移动止损/峰值回撤），不看连赢次数（D57 撤回语义）。

## 2. 计算式

```
移动止盈触发   = C_t < anchor_t - 2.0·ATR22_t   且 浮盈>0（anchor/ATR 同 X-S1-02 卡）
peak_pnl_t,i   = cummax( C_{entry..t}/entry_i - 1 )
峰值回撤触发   = peak_pnl_t,i > p_min 且 1 - (1+pnl_t,i)/(1+peak_pnl_t,i) ≥ 30%
目标位触发     = C_t ≥ entry_i × (1 + target_pct)
```

p_min=峰值生效下限（防止微利即兑现；prereg 标定项，TDM 未定值，禁本卡硬编码）。

## 3. 向量化实现要点

cummax/滚动算子零循环；peak_pnl 与棘轮共享 X-S1-02 的同一行循环仓级状态数组（一次循环产出
全部桶布尔，避免多趟）——这是 M1 与本卡合并施工的性能理由。

## 4. 引擎接法（M 级）

同 X-S1-02：`apply_take_profit_family` 并入 `apply_stop_family` 同一趟行循环；schema 维
`X_tp=[off, chandelier_trail, peak_giveback30, target_px, composite]`（裁定前置）。
与 X_stop 维正交组合（X_stop×X_tp 联合格点数=乘积，prereg 抽样覆盖）。

## 5. 考法（T0 口径声明）

与 X-S1-02 同体行循环：**激活任一止盈档即破坏纯向量化，T3b-T0 强制重标定
per_point_seconds（禁沿用 0.53s/格），fail-closed**。移动止盈/峰值回撤的 cummax 是路径依赖
算子，向量化"预计算 cummax"只对不与触发交互的区间成立，诚实位按行循环口径计耗时。

## 6. 数据列名

同 X-S1-02（close/high/low）。封板掩码（stk_limit：`trade_date, symbol, limit_up, limit_down`）
仅目标位"次日不板走"档消费。
