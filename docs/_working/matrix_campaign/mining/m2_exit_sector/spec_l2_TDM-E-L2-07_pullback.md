---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-07 | 回踩质量分级（覆盖 TDM-E-L2-07 / -07-1 回踩ABC判定）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（四因子合成全日级可算；D AL-PULLBACK-ABC 有 algo_ref 在册）
- 真源: `trading_decision_map.yaml#TDM-E-L2-07`（实现锚 sector_pullback grade_pullback：Fib×
  量能×强度三维取最弱档定级）+#TDM-E-L2-07-1（Fib 38.2% 必要条件×量能衰减 1/3×强度>7×
  时间窗 3-8 日；>15 日转横盘失效/<2 日盘中洗盘不入级/>78.6% 趋势破坏）

## 1. 机制定义

回踩分 A/B/C 决定给仓：A（黄金坑）满额、B 半仓、C 观察四因子各 0-1 分加权：
Fib 回撤位置（38.2% 附近=A 必要条件）×量能衰减（回调缩到峰值 1/3）×板块强度（>7）×时间窗
（回调 3-8 天）。

## 2. 计算式（行业指数级）

```
swing_high[k] = rolling_max(IND_high, 60)[k,t]； swing_low = 其前 60 日 rolling_min
fib_pos[k,t]  = (swing_high - IND_close) / (swing_high - swing_low)        # 0=回撤至高点
f_fib         = exp(-((fib_pos - 0.382)/0.05)^2)                           # 38.2% 邻域高斯核；
                                                                              fib_pos>0.786→0（趋势破坏）
f_vol         = clip( 1 - IND_amount / rolling_max(amount,20), 0, 1 )      # 量能衰减（1/3 阈=满分段）
f_str         = clip( (sector_score - 7)/3, 0, 1 )                         # L2-01 score 供给
f_time        = 1 if dd_days∈[3,8] else 0.5 if dd_days∈[9,15] else 0
grade[k,t]    = A if 加权分≥θA 且 f_fib>0 ; B if ≥θB ; C otherwise         # θ 阈进 prereg
              # TDM"取最弱档"纪律：任一因子=0 → 不高于 B 级
```

## 3. 向量化实现要点

滚动 max/高斯核/分段映射全算子级；sector_score 由 L2-01 面广播。**纯向量化，不触发 T0
重标定**。消费=建仓权重乘数（A=1.0/B=0.5/C=0）作用于过 gate 标的。

## 4. 引擎接法（M 级）

`sector_surface.pullback_grade(panel, sector_score) -> grade`；executor 维
`X_sector=adj_late+pullback` 档（与 L2-03 放行门串联：progress≥0.8 且 grade∈{A,B} 才建仓，
权重×grade 系数）。

## 5. 考法（T0 口径声明）

纯向量化。swing 窗 60 日/回看参数进 prereg；IND_high 需主通道宽表增 high 列（L2-00 已含）。

## 6. 数据列名

行业聚合宽表：open/high/low/close/amount（L2-00）；sector_score（L2-01）。
