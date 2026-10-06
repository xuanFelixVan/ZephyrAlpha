---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-10 | 同源补涨比价（TDM-E-L2-10）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M（降级通道）**——产业链图谱版 L 级登记；fallback"纯涨幅横向比价"日级可考
- 真源: `trading_decision_map.yaml#TDM-E-L2-10`（龙头翻倍后找同题材未涨股+同链上下游；fallback：
  产业链映射缺失→退化为纯涨幅横向比价）

## 1. 机制定义与切分

- **产业链版**（ig_* 图谱 DS-224/DS-225 同链扩散）：L 级登记（同 L2-09 理由——图谱时间轴
  进考卷=新数据线）。
- **fallback 横向比价版**（本卡 M 级）：龙头板块确认（L2-02 RRG Leading 或 L2-08 发酵段）后，
  在**同申万一级行业**内找滞涨股（20 日涨幅分位<20%）而板块强（sector_score 前 15%）——
  补涨经济学=同链滞涨的贝塔补涨（拉锯期资金扩散），启动滞后 3-5 天、胜率低于龙头但位置安全
  （TDM 口径）。

## 2. 计算式（fallback 版）

```
catchup_flag[t,i] = 1[sector_score[t,k(i)] ≥ P85]                       # 龙头板块
                  ∧ rank_pct(mom20[i,t]) < 0.20                          # 行业内滞涨
                  ∧ close[i,t] > MA120[i,t] ∧ drawdown120[i,t] < 0.30    # 未破位（质量闸，防接刀）
建仓权重 = base_w × 0.7                                                  # 补涨折扣（TDM"胜率低于龙头"→
                                                                          仓位打折，系数进 prereg）
```

## 3. 向量化实现要点

mom20 分位=A1 rank 既有算子；板块分位广播=one-hot。**纯向量化，不触发 T0 重标定**。

## 4. 引擎接法（M 级）

`sector_surface.catchup_flag(...)` 并入 L2-06 传导段的候选扩容（gate 放行第④条：龙头板块
滞涨股豁免个股强度>5 门槛——作为 `X_sector=conduction+catchup` 档）。

## 5. 考法（T0 口径声明）

纯向量化。滞后 3-5 天的验证判据（补涨股相对龙头 T+3~T+5 超额）= 考后归因统计列
（manifest），不进优化目标。

## 6. 数据列名

kline_daily: close（mom20/MA120）；industry_class 归属；sector_score（L2-01）。
ig_* 图谱版依赖：DS-224（governance.ig_industry_graph 四表族）——L 级不展开。
