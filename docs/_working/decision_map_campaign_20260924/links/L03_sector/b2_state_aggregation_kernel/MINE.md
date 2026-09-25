---
ttl: task_bound
doc_type: log
title: L03-B2 子类目挖矿簿 · sector_state 五成分聚合核（sector_state_aggregator）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

**① 一句话**：纯函数（零 IO）把面板原料折成每板块每日五成分行（momentum_pct/rrg_quadrant/strength/net_inflow_pct/rotation_state）+ 观察列。

**② 实测**：`signal_ashare/sector/sector_state_aggregator.py` 541 行、MATURITY=testing、CONSUMERS 头注列三下游（批2 落库编排器 / daily_gate_snapshot._collect_l2 / plan_engine 板块门）；3×3 偏好 frozen 表 :452、`emotion_band` :473、fail-visible 缺轴 :497-516。**表侧实测（本册 CH 探针）**：`c1_market.sector_state` **426,985 行 / 986 唯一日 / 2022-09-01→2026-09-24 / 729 码**；rrg_quadrant 分布 lagging 158,625／leading 152,920／improving 53,459／weakening 41,580／**空串 20,401（4.8%）**；分族 880 601 码自 2022-09-01、**881 128 码仅 2026-09-24 一日**。

**③ 六向**：①上游 kline_sector_880 回看窗 + limit_up_pool×成分 + money_flow×成分 + 锚定 dominant + emotion close_final。②下游 见头注三下游 + `condition_package.py`（板块腿 observational-only）。③算法 22 号 spec 公式级真源（本层只集成）；外部：RRG 原厂 JdK RS-Ratio/RS-Momentum（StockCharts ChartSchool、relativerotationgraphs.com，SKEL §11-1 已收录，沿用不重复）；**本轮新增两源**：A 股行业动量/反转复盘（新浪财经研报库 2026-08-06 https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/strategy/rptid/839360483335/index.phtml 与 BigQuant 因子研究·动量在 A 股实证 2026-06-05 https://bigquant.com/wiki/doc/vmpoW4sE1e ）→ 两源与 S10 NO_EDGE、P1-T2 负相关互证。④后端 **五成分中 strength/net_inflow 早期 NULL 面未收口**；rrg 空串 4.8% 未登记原因（本册新发现）。⑤前端 板块页。⑥字段 成分齐；质量画像=881 族仅 1 日（宇宙扩了、史没跟上）。

**④ 缺口**：LK-03（有效成分集未定，在册）；**L03-B2-G1 rrg_quadrant 20,401 行空串无归因登记**；**L03-B2-G2 881 族 state 仅 1 日→任何按 729 码做的截面统计在近史内都是混合宇宙（可比性断层）**。

**⑤ 三态裁定**：LK-03=挂起（v2 卡判档，禁本轮调权）；G1=**施工 P2**（空串归因 + DDL 语义位）；G2=**施工 P2**（回放补 881 族史或显式标记宇宙断层日；不改判据）。

**⑥ 日志**：R1 内部：state 表分族/分布探针→signal（两条新缺口）；R2 外部：动量反转两源→signal；R3 外部：RRG→沿用。

**封矿判据**：六向封口 → **子类目封矿**。
