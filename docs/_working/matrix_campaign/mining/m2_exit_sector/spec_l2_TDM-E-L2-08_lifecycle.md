---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-08 | 板块生命周期判定（TDM-E-L2-08）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M（带负结果裁剪）**——启动/发酵/高潮可考；"炸板率>40%"不可考（负结果 #8）
- 真源: `trading_decision_map.yaml#TDM-E-L2-08`（四段：启动=首板潮/发酵=二板三板+跟风涌现/
  高潮=涨停潮+媒体热炒/熄火=龙头断板+炸板率>40%；STR-MOMTREND-003 挂载）

## 1. 机制定义与可考性切分

| 生命周期段 | 日级可考性 | 判据（考卷口径） |
|---|---|---|
| 启动 | 可考 | 板块涨停家数从 0/1 跳升至 ≥3（首板潮代理）|
| 发酵 | 可考 | 2 连板家数≥1 且涨停家数维持 ≥3 |
| 高潮 | 可考 | 涨停家数 ≥ 板块成分 8%（高潮峰）|
| 熄火 | **部分** | 龙头断板（昨日 sealed_up 今日非）可考；**炸板率=涨停后开板，需盘中开板数据，日级不可考**（负结果 #8）——代理=昨日涨停家数今日腰斩 且 板块指数收跌 |

媒体热炒/新主流分流（invalidation 四信号中的 PE 泡沫/机构减持/政策转向）非量价数据=不可考，
剔除出考卷口径并披露。

## 2. 计算式

```
limit_cnt[k,t]    = Σ_i sealed_up[i,t]·1[i∈k]
consec2_cnt[k,t]  = Σ_i (sealed_up[i,t] ∧ sealed_up[i,t-1])·1[i∈k]
phase[k,t]        = 启动 if limit_cnt∈[3,∞) ∧ limit_cnt_{t-1}≤1
                    发酵 if consec2_cnt≥1 ∧ limit_cnt≥3
                    高潮 if limit_cnt ≥ 0.08×|k成分|
                    熄火 if (limit_cnt[t] ≤ 0.5×limit_cnt[t-1]) ∧ IND_ret<0
交易规则：只做启动/发酵（建仓放行）；高潮只持有不开新；熄火清仓（喂 X 族离场桶 signal）
```

## 3. 向量化实现要点

limit_cnt=one-hot×sealed_up 矩阵乘；phase=分段布尔链；熄火清仓信号并入 X-S1-01 的
B_signal 桶（板块退潮源——MOD-RK-09 A股六模式之一）。**纯向量化**。

## 4. 引擎接法（M 级）

`sector_surface.lifecycle(panel) -> phase`；executor：`X_sector=lifecycle` 档=建仓放行掩码
（启动/发酵）+熄火清仓宽表；与 X_stop 联跑格点按 T0 重标定口径。

## 5. 考法（T0 口径声明）

信号层纯向量化；熄火清仓作用到仓管理时与 X_stop 行循环合并——**联跑格点 T3b-T0 强制重标定
per_point_seconds（禁用 0.53s/格）**。

## 6. 数据列名

stk_limit: limit_up/limit_down（封板掩码原料）；kline_daily: close（IND_ret）；
industry_class: 成分归属。无新线。
