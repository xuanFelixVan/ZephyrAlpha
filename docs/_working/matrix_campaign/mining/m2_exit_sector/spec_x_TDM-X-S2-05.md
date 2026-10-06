---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-12 | TDM-X-S2-05 分批止盈执行（Exit Ladder）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写：R 倍数阶梯的权重路径变换；与 K_capital_ramp=pyramid 语义对偶）
- 真源: `config/trading_decision_map.yaml#TDM-X-S2-05`（+1R 减 50%/+2R 减 25%/尾仓 25% 跟踪）

## 1. 机制定义

Exit Ladder 阶梯：+1R（赚一个风险单位）减 50% 且止损移保本；+2R 再减 25% 锁利；尾仓 25% 跟踪
止盈跑趋势。信号强度定密度：弱信号一次走完、强信号留 runner。MFE 捕获率<50%=卖太早（反馈
校准，实盘域）。

R 的定义（本卡钉定，TDM 未显式给出）：`1R = 入场价与初始止损价之差`，初始止损取 X-S1-02
固定 -7% 档（或 ATR 3 倍档，随 X_stop 维取值），即 `1R_i = entry_i × 0.07`（固定档）。

## 2. 计算式

```
R_t,i      = (C_t,i - entry_i) / 1R_i
ladder_w_t,i = 1.00                      if R < 1
             = 0.50                      if 1 ≤ R < 2     # 止损上移至 entry（保本）
             = 0.25                      if R ≥ 2
             = 0                         if X-S1-03 跟踪止盈触发（尾仓归宿）
w_exit[t,i]= w_tgt[t,i] × ladder_w_t,i   （只减不增；与调仓日目标取 min）
```

弱信号一次走完=urgency<0.5 时 ladder 折叠为 1.00→0（与 X-S1-05 urgency 列联动）。

## 3. 向量化实现要点

R_t=逐元素算术；ladder=分段映射（np.digitize）；与 X-S1-02 棘轮共享同一行循环（保本上移
写回 stop 数组）。权重乘法路径变换与 K_capital_ramp 的渐变后处理（t3 挖矿 M4）同形，
实现可共用一个权重路径变换器。

## 4. 引擎接法（M 级）

`apply_exit_ladder(w_tgt, entry, stop_1r, urgency) -> w_exit`；schema 维
`X_ladder=[off, ladder_1r, all_at_once]`。MFE 捕获率统计=S 级 manifest 增列
（`mfe_capture = 卖出价相对期间最高价的比值` 逐仓事后统计，审计用，不进优化目标）。

## 5. 考法（T0 口径声明）

行循环（棘轮共享）：**激活即 T3b-T0 强制重标定 per_point_seconds（禁用 0.53s/格），
fail-closed**。分批卖出与 X-S2-01 分批路由共享"卖出日切分"实现，防同一语义两套代码。

## 6. 数据列名

close（kline_daily）；entry/stop 来自 X-S1-02 状态数组，无新数据线。
