---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-04 | 板块级市场状态（覆盖 TDM-E-L2-04 / -04-1 轮动五分类 / -04-2 虹吸态 / -01-5 市场级调节注入）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（三态/五分类/虹吸判据全部是板块截面统计量，日级可算；-01-5 为其注入口）
- 真源: `trading_decision_map.yaml#TDM-E-L2-04`（实现锚 sector_ecology_judge：高潮分≥90=次日
  分歧警示；梯队连击≥2 且 Top2 集中度≥30%=主线清晰；其余混沌降仓）+#TDM-E-L2-04-1/04-2/01-5

## 1. 机制定义

- **04 三态封闭判定**（优先级 高潮>主线清晰>混沌）：高潮分≥90=次日分歧警示；梯队连击≥2 且
  Top2 集中度≥30%=主线清晰聚焦做；其余混沌降仓等待。
- **04-1 轮动五分类**：按"板块强度方差+涨停集中度"分 高潮/主线/分歧/派发/混沌，每态给全板块
  统一调节分（主线+10%/派发-15%），喂 01-5 注入。
- **04-2 虹吸态**：前 3 板块成交占比>40% 时只做头部板块，其余候选池清空。
- **01-5 市场级调节注入**：把上述态分统一加/减到全板块强度（fallback：watch_score 缺失按 0）。

## 2. 计算式

```
climax_score[k,t]  = 100·(0.5·norm(limit_ratio[k,t]) + 0.3·ladder[k,t] + 0.2·norm(Δ5 momentum))
top2_conc[t]       = Σ 前2行业 amount / Σ 全行业 amount
ecology[t]         = 高潮  if max climax_score ≥ 90
                     主线  if ladder 连击≥2 且 top2_conc ≥ 30%
                     混沌  otherwise
rot_state[t]       = 五分类：f(方差(score), 涨停集中度=Σ前3行业 limit 家数/Σ 全部)——分界阈值
                     全部进 prereg 标定（TDM 只冻结了调节分 ±10/−15%）
siphon[t]          = top3_conc[t] > 40%
adj_market[k,t]    = {主线:+10%, 派发:-15%, 其余:0}（01-5 注入口=逐行广播加到 sector_score）
```

## 3. 向量化实现要点

全部是 L2-01 面上量（limit_ratio/amount/climax）的截面统计：逐行 sum/方差/top-k。
**纯向量化，不触发 T0 重标定**。态→调节分=查表广播（T 长向量）。

## 4. 引擎接法（M 级）

`sector_surface.ecology(panel) -> {ecology, rot_state, siphon, adj_market}`；
消费方式两档：①adj_market 进 sector_score（01 总评）；②siphon=true 行=候选池只留 top3
行业成分。落 manifest 审计列 `sector_state_json`（每日态，与 j_state 列同形）。

## 5. 考法（T0 口径声明）

纯向量化。与 J_regime_switch 的关系=**两套正交状态轴**（L2 态是板块分布结构，J 是组合级帽），
prereg honesty 须声明不互替；联合格点= X_sector×J 乘积抽样。

## 6. 数据列名

复用 L2-01 面（kline_daily/stk_limit/industry_class 聚合），无新数据线。
