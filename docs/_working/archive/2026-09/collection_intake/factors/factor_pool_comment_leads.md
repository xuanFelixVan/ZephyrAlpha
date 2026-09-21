---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# 评论区因子池 16 条——分项判定 2026-09-20

> 来源：PCR 帖 96 楼 + 幻方帖 + 101 帖评论区（楼主小结：小市值/动量/散户持仓/资金流向/SUE）。本文件逐条给"内部现状 → 判定"。**社区因子一律按假设卡走 E4 重考，判定只回答"原料在不在"。**

## A 级：数据已在库，随时可立假设卡

| 因子 | 内部现状 `[亲验]` | 备注 |
|------|------------------|------|
| 散户持仓 | `c3_fundamental.shareholder_count` + `top10_shareholders`（150 万行）+ `top10_circulating_shareholders`（214 万行）；**X-7 断供已治本补齐（2026-09-19，55591 行）** | 用法"散户持股集中→做空重仓股"A 股做空受限，转化为规避/低配信号；覆盖率旧账 2025 报告期 ~70% 在案 |
| 席位资金流 | `c1_market.dragon_tiger` + `dragon_tiger_seat`（Top5 买卖席位，institution/broker/connect 分类）已在产 | "跟踪外资/机构/散户席位变化"原料齐；覆盖起始建议实查 CH min(trade_date) |
| SUE 盈余惊喜 | `financial_derived` 派生层，`build_financial_derived.py:154` 明文 RevSUE 口径（营收比净利难操纵） | 直接可算 |
| 恐贪情绪 | `ingest.crypto_fear_greed`（alternative.me）→ `sentiment_panel` 在产 | 币圈轴现成 |
| 动量 | ROC/MTM/TSI/SMI/RMI 等 138 指标库在产 | 多人共识"还行" |
| 资金流向 | money_flow（个股）/market_fund_flow_daily（大盘）/sector_fund_flow（板块）三表在产 | 与席位资金流互补 |

## B 级：有底子需小补

| 因子 | 内部现状 | 缺口 |
|------|---------|------|
| 小市值 | universe 机制有（F06 实证 G_universe=第一杠杆 12%）；股本市值在 stock_daily_basic | 立假设卡即可；**拥挤+容量小+持仓体验差**三连警示随卡预注册（E4 容量考） |
| 竞价×情绪 | `c1_market.auction_snapshot`（25.2 万行/47 密集日）+ auction_book；竞价桥 2026-09-17 切 qmt_bridge | n≥30 统计门槛已过；历史只有 2026-06 起，深史 no_source 在案 |
| 股息 | stock_indicator 含股息率（akshare，2026-08 起） | 历史浅需回补 |
| PCR 跨市场映射 | 见 factor_spec_options_pcr.md（P1 立项） | 期权数据批 |

## C 级：真缺口可立项（P2）

| 因子 | 说明 |
|------|------|
| 拥挤度 | 内部无拥挤度度量；E4 出证维度可加"因子拥挤度"（代理：换手异动/多空拥挤代理/相关度抬升）。社区机制描述自洽：人少有效→挤入失效→弃用复活 |
| 因子动量 | 因子层面的动量（上期好的因子下期延续）——E4/组合层 meta 信号，生产无实现 |

## D 级：存档不排期

- **冷门因子×0.5 + M200/M100 金叉距离×0.5**（波段混合配方）——组合权重思路，pf_alloc 接电时可参考。
- **弱技术面+强基本面 配型**——配型思路存档。
- **Barra 风险模型**（幻方帖评论区）——内部无风险模型；组合归因体系（W7 股权穿透/归因线）复活时作参照系。
- **风险调整动量族**——tilib 需求池已有同类（M-L6 学术矿脉）。
- **长周期均线择时**——regime 线（S-OWNER-002）考试 FAIL 挂起中，复活时一并考。
- **牛市打板**——"真正赚大钱是牛市打板"；项目 daban 全族 59 条 candidate 待转正，此条为其价值佐证。

## 附：因子工程方法论要点（评论区+论文，均已核实者标 `[外部]`）

1. **拥挤度轮动**：因子失效主因是拥挤而非死亡；监控+动态上下线。
2. **降回撤双法**：多策略多品种分散 + 按近期数据动态变参，两者结合；WorldQuant=百 PM 优胜劣汰的 MOE 结构；低相关组合（Ray Dalio 风险平价类比）。内部挂点：pf_alloc 算器件齐但 wiring=exempt 未接电 `[亲验]`——接电时的设计引用。
3. **组合三原则**：单因子弱组合强；多样性与低相关是关键；保留主观修改层。
4. **Factor Zoo 过滤文献** `[外部]`（Crossref 逐字核实）：Feng/Giglio/Xiu《Taming the Factor Zoo: A Test of New Factors》**Journal of Finance** 2020, 75(3)（注意常被误记为 JFE）；Harvey/Liu/Zhu《…and the Cross-Section of Expected Returns》RFS 2016, 29(1)；补充 Hou/Xue/Zhang《Replicating Anomalies》RFS 2020 与 Jensen/Kelly/Pedersen《Is There a Replication Crisis in Finance?》JF 2023。**这四篇=E4 准入门的引用基础。**
5. **超级 Alpha 内部撮合**（101 论文）：海量因子整合+内部净额撮合省执行成本——执行层成本优化思想，存档。
6. **反方观点（信息维度论）**：公开信息已 price-in、AI 时代规律被挖尽→"大道至简长均线择时"。作为对立观点存档，提醒：因子挖掘的边际收益在递减，组合与执行层挖潜同等重要。
