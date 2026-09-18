---
ttl: task_bound
---

# 板块灰度层 v0 设计段（R 车道 · 只设计不实现，2026-09-19）

> 会话 st-bizmine-r-20260919 · 定位：把 R1/R2 的「大盘灰度→因子选择」轴向下延伸一层到板块灰度（Owner 主纲：大盘灰度→板块灰度→逐级选择因子与策略）。
> 本件是**设计段**：只定义+数据可得性探针，零实现、零回测。

## 1. 数据可得性探针（实测，2026-09-19 快照）

| 表 | 实测规模 | 覆盖 | 探针结论 |
|---|---|---|---|
| `c1_market.kline_sector_880` | 449,502 行 / 469 个板块（period 全='1d'） | 2020-03-17..2026-09-18 | **成熟面板只有 2022 起**：2020 年仅 2 板块 219 行、2021 年 8 板块 1315 行，2022 年 376 板块 39500 行，2023+ 稳定 418→469 板块。总包令"6.5 年"是表首尾跨度，**诚实口径=全宽 4.5 年（2022-01..2026-09，1143 交易日 × 469 板块）** |
| 同表重复行 | 449,502 行 vs 435,332 distinct(sector_code,trade_date)，重复值上限 2 倍、data_source 单一 'tqcenter' | — | plain MergeTree 双插（与 regime_state_anchored 同病），消费端必须 DISTINCT/argMax 去重 |
| `c1_market.sector_constituent_snapshot` | 190,248 行 / 595 板块 | **仅 2026-09-14..15 两天** | 成分快照是**现时点**的，无历史——板内广度若用今日成分回溯历史=成员关系前视（lookahead）；历史广度必须改从逐股 kline 按当日可得成分聚合（需成分历史源，当前缺口） |
| `c1_market.kline_sector`（对照） | 存在（未深探） | — | 与 880 族关系待考（可能=申万/中信分类日线），设计不依赖 |
| 字段 | open/high/low/close/volume/amount/forward_factor/sector_name | sector_name 实测空串 | 板块名翻译需另接 sector_list/sector_meta；**指数性质**：880xx 通达信板块指数，个股除权链问题理论上不适用，但 forward_factor 列语义未考，v0 直接用 close 不复权（暂定，同全局复权链警示） |

## 2. 板块强度灰度 v0 定义（设计）

对每个板块 s、每个交易日 t（只用 ≤t 数据，滚动窗 PIT）：

```
mom20_s,t   = close_s,t / close_s,t-20 − 1                     （20 日动量）
rel_s,t     = mom20_s,t − median_k(mom20_k,t)                （对全板块横截面中位数）
volx_s,t    = amount_s,t 在自身滚动 250 日内的分位             （量能灰度 ∈[0,1]）
strength_s,t = 横截面分位合成（v0 等权）:
              0.6 × pct_rank_k(rel_s,t) + 0.4 × pct_rank_k(volx_s,t)   ∈[0,1]
```

- **单板块灰度** = strength ∈[0,1]，连续值不设硬标签（与 R1 结论一致：灰度轴不用二值态）。
- **市场级板块灰度聚合**（接到大盘轴的桥，供「大盘灰度→板块灰度→选因子」传导考试）：
  - `strong_share_t` = strength>0.8 的板块占比（呼应判定台账 evidence.attack_sector_count——生产层已在产同族证据，见 regime_status_assessment.md §2 E 表）
  - `dispersion_t` = strength 的横截面标准差（呼应 alt_regime_signal F12_HOG_DISPERSION 的离散度思路）
  - `median_strength_t` = strength 中位数
- 与大盘灰度的关系假设（v0 待考，不预设）：R2 已证幸存因子收益集中在高波灰度桶；板块层的传导考试=「strong_share 高的日子，板块动量/轮动类因子 IC 是否系统性高于 strong_share 低的日子」——即把 F 车道的因子 IC 大海选加一个板块灰度条件维度。

## 3. v0 可考假设卡方向（草案，非正式卡）

1. 「板块动量因子 IC 的板块灰度条件化」：rel_mom 因子在中高 strong_share 状态下 IC 显著为正、低 strong_share 状态下衰减——预注册口径沿用 R2 范式（IS 定边界、T-1 落桶、双段判读）。
2. 「板块灰度领先大盘灰度」：strong_share_t 对 T+1/T+5 大盘 vol_pct 桶迁移的预测力（信息检验，非收益检验）。
3. 「强势板块成员股因子增强」：同一因子在 strong 板块成员 vs 弱势板块成员的条件 IC 差（需成分历史，受 §1 成分缺口约束，**当前不可考**，先登记数据缺口）。

## 4. 施工前置清单（给后续车道/总包）

1. **成分历史缺口**：sector_constituent_snapshot 仅 2 天，历史广度线需补成分历史源或改用逐股聚合方案——实现前必须解决，禁用现时成分回溯（前视）。
2. 去重义务：kline_sector_880 双插行，任何实现先 DISTINCT。
3. 复权链警示随件：板块指数 close 未复权（forward_factor 语义未考），结论带「暂定」。
4. 落库形态建议：板块灰度输出建议挂 `c1_backtest` 或专表（plain MergeTree 重复插入的教训：生产写入走 BufferedWriter 去重键），实现时走 construction_sop 流程+depgraph 登记。
5. 880 族覆盖 2022 起才够宽——与 regime_state_anchored（2017-07 起）对齐时，板块轴的 IS 期比大盘轴短 4.5 年，预注册窗口要相应重划（v0 建议 IS=2022-01..2024-12，考试=2025-01..2026-09）。

---
*本件只设计不实现（总包令 R 车道第 5 条）。数据探针只读。所有覆盖数字为 2026-09-19 快照，暂定。*
