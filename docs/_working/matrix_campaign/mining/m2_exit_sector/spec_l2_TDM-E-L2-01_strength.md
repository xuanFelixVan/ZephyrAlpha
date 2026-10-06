---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 L2-01 | 板块强度综合（覆盖 TDM-E-L2-01 / -01-1 / -01-2 / -01-3 / -01-4）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写：行业聚合宽表上的四路子分，全部日频向量化）
- 开源依据: Moskowitz & Grinblatt (1999, JF) "Do Industries Explain Match?"——行业动量解释
  个股动量主部，买强行业卖弱行业显著盈利；多周期动量（3/5/20 日）= 业界轮动策略标准做法
  （Grokipedia Rotational Momentum 综述同口径）。真源: `trading_decision_map.yaml#TDM-E-L2-01`
  （四路子分各 0-100 等权 0.25，±10 市场调节后 clamp，前 15% 入池）

## 1. 机制定义（四路子分，各 0-100）

- **01-1 结构强度**：板块内涨停股占比（>8%=强）+连板梯队完整性（有 2 板有 3 板=接力健康）+
  板块指数趋势（20 日线上方），合 0-10。
- **01-2 动量活跃度**：板块成交额占全市场比+环比变化，前 10%=资金扎堆（2026-09-18 修正：
  相对强度因子去 abs 保符号——弱于大盘不反向加分）。
- **01-3 多周期动量**：q20/q5/q3 动量加权，q3 主导=刚点火、q5 主导=进行中、q20 主导=涨很久。
- **01-4 板块资金流**：主力净流入 3 日累计+当日大单净额（单独成卡 L2-01b 更细）。
- **01 总评**：四路等权 0.25 合成，市场级调节 ±10（L2-01-5 卡）后 clamp[0,100]，前 15% 进候选池。

## 2. 计算式（行业 k，日 t；主通道宽表=L2-00 卡）

```
# 01-1 结构强度（涨停字段走封板掩码代理，非 DS-059）
limit_ratio[k,t]   = mean_i( sealed_up[i,t] · 1[i∈k] )                    # >8% 计满分段
ladder[k,t]        = 板块内昨日涨停今日再涨停家数≥1 且 2 连板家数≥1        # 梯队代理
trend[k,t]         = IND_close[k,t] > MA20(IND_close)[k,t]
struct_score       = 10·(0.4·norm(limit_ratio)+0.3·ladder+0.3·trend)
# 01-2 活跃度（保符号）
turn_ratio[k,t]    = IND_amount[k,t] / Σ_k' IND_amount[k',t]
act_score          = 100·rank( turn_ratio + Δ5(turn_ratio) )（截面百分位，符号保留）
# 01-3 多周期动量
mom_n[k,t]         = IND_close[k,t]/IND_close[k,t-n] - 1 , n∈{3,5,20}
q_score            = 100·(0.2·rank(mom_3)+0.3·rank(mom_5)+0.5·rank(mom_20))   # 权重进 prereg
# 01 总评
sector_score[k,t]  = clamp( 0.25·(struct/act/q/flow 归一)·4×0.25 + adj_market , 0, 100)
candidate_pool[t]  = top 15% by sector_score
```

`sealed_up`=`_c4_engine._build_seal_masks` 在册掩码（stk_limit 原始价口径，E7 修复后单位对齐）。

## 3. 向量化实现要点

全 DataFrame 滚动/截面 rank/分组聚合（groupby industry 逐日求和→pivot 宽表）零行循环；
行业聚合宽表批级共享一次构建。截面 rank=A1 维既有算子语义复用。梯队/连板的"昨日涨停"=
shift(sealed_up)，滚动计数=rolling sum——**纯向量化，不触发 T0 重标定**。

## 4. 引擎接法（M 级）

- `scripts/backtest/sector_surface.py`（新件，施工批走 CREATE-GUARD/能力反查）：
  `build_sector_panel(start, end) -> {ohlcv 宽表 dict}` + `sector_strength(panel) -> score`。
- executor：新增模块维 `X_sector=[off, strength_top15]`——激活时候选池=行业过滤掩码，
  个股合成因子按 `sector_score` 加成后重排（传导见 L2-06 卡）。schema 修订→裁定前置。
- **与 M3 的关系**：本卡即 t3 挖矿 M3"板块主干最简版"的完整化（M3 只列行业动量 Top-K 两层
  排序；本卡按 TDM 四路子分补齐，且每路独立成 prereg 档可分解归因）。

## 5. 考法（T0 口径声明）

纯向量化（signal_side 成本），**不触发 T0 重标定**，可沿用 gpu 薄核口径；行业聚合宽表构建
为批级一次性成本。数据缺席纪律：money_flow 缺失→01-4 降权归一化（TDM fallback 在册）标
degraded；industry_class 缺失→整格阴性 fail-closed（executor 既有语义）。

## 6. 数据列名

kline_daily: open/high/low/close/volume/amount；industry_class: symbol/industry_sw/
industry_level/valid_from/valid_to；stock_indicator: total_mv（市值加权）；
stk_limit: limit_up/limit_down（封板掩码）；money_flow（见 L2-01b 卡）。
