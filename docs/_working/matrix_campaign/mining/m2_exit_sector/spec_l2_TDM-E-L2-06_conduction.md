---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-06 | 板块个股传导（覆盖 TDM-E-L2-06 / -06-1 三级放行门槛 / -06-3 强度加权传导）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（传导系数查表+三级布尔放行，全纯向量化——L2 族与考卷因子面最近的一张卡）
- 真源: `trading_decision_map.yaml#TDM-E-L2-06`（实现锚 sector_conduction：10→+15%/6→+5%/
  <6→-10%，只调分不重排名=层级隔离承载）+#TDM-E-L2-06-1/-06-3

## 1. 机制定义

板块结论喂个股层的边界规则：只传"板块强度调节分+龙头定位"两字段（层级隔离防越权）。
- **06-1 三级放行（先 gate 后 weight）**：①板块强度分>6；②个股自身强度>5；③流动性
  （日成交>2 亿）——三关全过才进打分池。
- **06-3 强度加权传导**：板块强度 10 分制映射个股 score 加成：10 分=+15%、6 分=+5%、
  <6 分=−10%；强板块弱票也加分、弱板块强票打折。

## 2. 计算式

```
gate[t,i] = (sector_score[t, k(i)] > 6) ∧ (stock_strength[t,i] > 5) ∧ (amount[t,i] > 2e8)
            # stock_strength=个股综合因子分 10 分制（v1 合成因子的截面百分位×10）
multiplier[t,i] = 查表(sector_score 十分位): ≥9→1.15 ; ≥6→1.05 ; <6→0.90
score'[t,i] = score[t,i] × multiplier[t,i]          # 先 gate 后 weight
combined'[t,i] = where(gate, score', NaN)            # NaN=不进打分池（顺位 rank 天然剔除）
```

## 3. 向量化实现要点

industry map one-hot 矩阵 `M_i∈{0,1}^{N×K}`（PIT 快照），sector_score→个股广播=
`score_adj = (M_i @ multiplier_by_industry)`；gate 三布尔逐元素与。**零行循环、零新数据线、
零新回测语义**——本质是 A2 合成后的一次乘性后处理，是 L2 族中可最先落地的卡。

## 4. 引擎接法（M 级）

executor evaluate_recipe 在 A1/A2 之后、B Top-N 之前插入可选段
`sector_conduction(combined, sector_score, gate, multiplier_table)`；
schema 维 `X_sector=conduction`（或与 L2-01 档合并为 `X_sector=[off, strength_top15, conduction]`
三值维）。只调分不重排名=TDM 层级隔离纪律，考卷同款遵守（禁在传导段内改 Top-N 语义）。

## 5. 考法（T0 口径声明）

纯向量化 signal_side：**不触发 T0 重标定**，可沿用 gpu 薄核口径（传导在 pandas 信号面，
回测核不变）。multiplier 查表值=TDM 冻结口径（15%/5%/-10%）；gate 阈值 6/5/2 亿=TDM 口径，
进 prereg 冻结项。

## 6. 数据列名

kline_daily: close/amount；industry_class: symbol→industry_sw；
stock_indicator: total_mv（个股强度归一可选）；无新线。
