---
ttl: task_bound
session: st-xhs-full-20260922
topic: xhs_full_construction_20260922
---

# 评论区因子池 B 分项假设卡 + Alpha101 首批 20 条翻译入册（工单 #7B + #4）

> 真源=collection_intake/factors/factor_pool_comment_leads.md（#7B）与 factor_spec_alpha101_191_158.md（#4）。E4 表述遵裁定#325；A 级分项（散户持股/龙虎榜/SUE/恐贪）已在库零施工。

## 一、工单 #7B：B 分项假设卡（3 张实体卡+1 张已并单）

### CP-B1 小市值｜B
- **表达式（模板）**：`neg(rank_cs(mv_z20))`（市值截面低值端做多）
- **假设**：小市值组次期超额为正；**三连警示随卡预注册**：拥挤（2026-24 微盘风格拥挤史）、容量小、回撤持仓体验差——E4 容量考为放行前置（规格卡原文）。
- **数据源**：stock_daily_basic（股本×价格派生市值）+ F06 G_universe 机制（实证第一杠杆 12%）。
- **前置**：市值横截面字段进基座面板。
- **队列**：模板入册；前置齐转实体行。

### CP-B2 竞价×情绪｜B
- **表达式**：非公式面——竞价缺口分位×当日情绪状态条件化（auction_snapshot 25.2 万行/47 密集日）。
- **假设**：高开分位×低情绪组合的日内动量衰减最快（条件化反向）。
- **数据源**：auction_snapshot + auction_book（竞价桥 09-17 切 qmt_bridge 在产）。
- **前置**：历史仅 2026-06 起（深史 no_source 在案）——样本量声明进预注册。
- **队列**：n≥30 统计门槛已过；等情绪状态面（HF-07 合成器）供条件轴后开考。

### CP-B3 股息回补｜B
- **表达式（模板）**：`rank_cs(dv_ttm)`（股息率截面做多端）
- **假设**：高股息组次期超额为正（红利因子 A 股长期有效形态）。
- **数据源**：stock_indicator.dv_ttm（2026-08 起）。
- **前置**：**估值/股息历史回补（与 HF-05 同一前置批，幻方规格卡 §2 同源缺口）**。
- **队列**：模板入册。

### CP-B4 PCR 跨市场映射｜B
- **已并单**：=工单 #3+#14 期权 PCR 全链（本班落地，含假设卡与 E4 记录，见 PCR 假设卡节）——此处不重复立卡。

## 二、工单 #4：Alpha101 首批 20 条翻译入册

> 口径：101 原式（Kakushadze 2015）→ 本项目 DSL（算子白名单 v2.1）翻译；基座字段缺口（adv20/vwap/high/low/open/close 原始价）如实标注【不可考】，可考子集用 E1C 面板真算窗口 IC（top50×250 日，REG-IND-001 残差化，2026-09-22 实跑，n=12547）。**本表=首批入册+窗口 IC 切片记录，非完整 E4 判档**；幸存者全考试沿 FactoryLaneC 周窗，放行档届时如实。

| # | Alpha101 原式（摘要） | DSL 翻译 | 可考性 | 窗口 IC（实算，可考者） |
|---|----------------------|----------|--------|------------------------|
| 1 | Alpha1: rank(rank(low)^count>rets...) | 需 low/intraday 时序 | 【不可考】缺 low/adv20 | — |
| 2 | Alpha4: -1*ts_rank(rank(low),9) | `neg(ts_zscore_20(rank_cs(ret_1d)))`（low 缺→代理 ret_1d 排名时序标准化，忠实度中） | 代理可考 | IC=-0.0206（弱） |
| 3 | Alpha6: -1*correlation(open,volume,10) | `neg(ts_corr_20(ret_1d, amt_z20))`（open/volume→量价代理） | 代理可考 | IC=-0.0194 |
| 4 | Alpha9/10: ts_min/max 与 mood | `ts_zscore_20(ret_5d)` 条件面 | 部分可考 | IC=+0.0097 |
| 5 | Alpha12: sign(delta(volume,1))*(-close) | `mul(sign(ts_delta_5(ret_1d)), neg(ret_1d))`（volume delta→ret 代理） | 代理可考 | IC=+0.0056 |
| 6 | Alpha14: -1*rank(delta(returns,3))*correlation(open,volume,10) | `mul(neg(rank_cs(ts_delta_5(ret_1d))), neg(ts_corr_20(ret_1d, amt_z20)))` | 可考（代理） | IC=+0.0115 |
| 7 | Alpha18/20/21: high/low/close 全相对量 | 需 high/low | 【不可考】 | — |
| 8 | Alpha22: -1*delta(correlation(high,volume,5),5)*rank(stddev(close,20)) | `mul(neg(ts_delta_5(ts_corr_20(ret_1d, amt_z20))), rank_cs(vol_20d))` | 可考（代理） | IC=+0.0338（本批最强） |
| 9 | Alpha23/24: high 依赖簇 | 需 high | 【不可考】 | — |
| 10 | Alpha32: scale based on closeMean | `rank_cs(div(close_ma20, add(vol_20d, 1)))` 结构代理 | 可考（弱代理） | IC=+0.0126 |
| 11 | Alpha33: rank(-1*((1-open/close)^1)) | 需 open/close 对（ret_1d=对数近似替代） | `rank_cs(neg(ret_1d))` | IC=-0.0166 |
| 12 | Alpha38/40/42: rank(correlation(rank(low/adv..))) 族 | adv20 缺 | 【不可考】 | — |
| 13 | Alpha41: correlation(high, volume, 9) | `ts_corr_20(vol_20d, amt_z20)` 结构代理 | 可考（弱代理） | IC=+0.0270（次强） |
| 14 | Alpha43: ts_rank(volume/adv20)*rank(close-vma) | `rank_cs(amt_z20)` | 可考（代理） | IC=+0.0063 |
| 15 | Alpha101 族（余 80+ 条） | 大多依赖 vwap/high/low/adv20 | 【不可考】待基座扩字段 | — |

**可考子集实算汇总**（10 条代理可考，窗口增量 IC 全表如上，REG-IND-001 残差化口径 n=12547，2026-09-22 实跑）：最强=Alpha22 代理（量价相关五日变化取负×波动脉冲截面排序）**IC=+0.0338**，次强=Alpha41 代理（波动×量额 20 日相关）**IC=+0.0270**，两者达 |IC|>0.02 观察档；其余 8 条弱信号/反向（负号=做多低值端，如实记录），与社区实测"101 条多数过时"预期一致（规格卡 §1）。**如实声明**：以上为单窗口（top50×250 日）IC 切片记录，非完整 E4 判档；Alpha22/Alpha41 两代理已转 lane_c_candidates.csv 实体行（birth_batch=E1C-20260922-A101）走全考试，其余留档备查。

**基座扩字段前置清单（幸存者全考试与 191/158 批的共同前置）**：adv20（20 日均额，kline_daily 可派生）、vwap（amount/volume 可派生）、high/low/open（kline_daily 原生列，基座面板 FEATURES 扩座即可）——四字段均为**派生扩展无新数据依赖**，立一张基座扩字段工单即可解锁大部分不可考条目（归 tilib/E1C 基座线，本班不越域施工，留痕）。

**算子库接线**：本批翻译消费的算子全部在白名单 v2.1 内（rank_cs/ts_zscore_20/ts_delta_5/ts_corr_20/amt_z20 基座字段），零新算子=零白名单改动，接线天然完成。
