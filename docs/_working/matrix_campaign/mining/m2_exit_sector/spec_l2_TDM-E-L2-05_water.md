---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-05 | 水温响应（覆盖 TDM-E-L2-05 / -05-1 水温档推导 / -05-2 信号响应三件套）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **L（只登记，不施工）**——TDM red_reason=pending_gate（待 L1 温度计时间周期定稿）
- 真源: `config/trading_decision_map.yaml#TDM-E-L2-05`；D20 四层架构定稿注记

## 1. 结论

水温=板块层总开关：水烫（S4）信号全放行+门槛降档；水冰（S0-S1）只放行最强 5%+门槛升档。
05-1=日级 S5 主判+月级 7 态封顶（月级一票否决激进度）；05-2=信号权重×(0.5~1.2 水温系数)+
打分门槛随档+象限过滤三件套查表。

**L 级理由**：①上游 L1-S5 日级温度计（11 信号）本身是缺口（t3 挖矿 §1.2），TDM 明示本族
"挂起待 L1 温度计定稿"——工程上无消费源；②月/周封顶与三层对齐加成是有状态多时间尺度编排，
非单格向量化语义；③T3a 已接线的 J_regime_switch 日级帽调度（owner_regime_switcher）是
"水温→放行比例"的最近似在册代理，先以 J 维考组合级，板块级细分待 S5 落地后另卡。

## 2. 未来接线形状（预留，不实现）

```
water_level[t]    ∈ {S0..S4}          # S5 温度计主判+月级封顶
weight_coef[t]    = 查表(water_level) ∈ [0.5, 1.2]
threshold_adj[t]  = 查表(water_level)
gate_filter[t]    = 水冰时仅主线象限板块（RRG quadrant 联动）
score' = score × weight_coef;  放行 = score' ≥ threshold + threshold_adj
```

## 3. 考法

无考法（禁伪造水温）。T3a 的 J 维是其合法替身考位——判据=c2_extreme_event_protection
CRISIS 时段 MaxDD 改善（t3 挖矿 §3.3 已预注册判据口径），本卡不新增。
