---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-03 | 调整周期进度（覆盖 TDM-E-L2-03 / -03-1 扩散指标追踪）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（三维进度全日级可算；缩量维为"设计语言待扩展"如实沿 TDM 口径）
- 真源: `config/trading_decision_map.yaml#TDM-E-L2-03`（实现锚 sector_adjustment：时间 0.4+
  回撤 0.3+扩散 0.3，≥80% LATE 才放行）

## 1. 机制定义

目标板块从高点回撤算进度：回撤 5-8 天+缩量到高峰 1/3 以下=调整近尾声，进低吸观察名单；
还在放量下跌=不碰。**03-1 扩散指标**：板块内站上 20 日线个股占比——从 <30% 回升穿 50%=
调整结束；从 >80% 掉头向下=见顶；给出进度百分比。

## 2. 计算式

```
dd_days[k,t]   = 距 IND_close[k] 最近 20 日高点的交易日数
drawdown[k,t]  = 1 - IND_close[k,t]/rolling_max(20)[k,t]
diffusion[k,t] = mean_i( close[i,t] > MA20[i,t] · 1[i∈k] )        # 扩散指标（个股级 breadth）
time_score     = clip(dd_days/8, 0, 1)                            # 0.4
dd_score       = clip(drawdown/最大容忍回撤, 0, 1)                 # 0.3（容忍值进 prereg）
diff_score     = 分段：diffusion<30% 回升穿 50% 得 1；>80% 拐头得 0；线性内插  # 0.3
progress[k,t]  = 0.4·time_score + 0.3·dd_score + 0.3·diff_score   # ≥0.80=LATE 放行
vol_confirm    = IND_amount[t] ≤ (1/3)·rolling_max(amount,20)[t]   # 缩量确认（TDM"待扩展"位，
                                                                   本卡给出可考式，启用档进 prereg）
```

## 3. 向量化实现要点

扩散指标=个股布尔宽表×行业 one-hot 归一矩阵（T×K 矩阵乘，N 大时 GPU 友好但按 CPU 口径计）；
其余滚动算子。**纯向量化，不触发 T0 重标定**。

## 4. 引擎接法（M 级）

`sector_surface.adjustment_cycle(panel) -> progress/vol_confirm`；消费=低吸门控档
（`X_sector=adj_late`：仅 progress≥0.8 行业的成分股允许建仓）。与 L2-02 RRG 交叉验证
（TDM fallback 在册：扩散滞后震荡期→RRG 序列验证）作对照档非联锁。

## 5. 考法（T0 口径声明）

纯向量化。扩散指标需要全宇宙 close 面已装载（G_universe 既有），无新数据线。

## 6. 数据列名

kline_daily: close（MA20/扩散）；amount（缩量确认）；行业聚合宽表（L2-00）。
