---
ttl: task_bound
doc_type: log
title: L03-B4 子类目挖矿簿 · 板块资金维（sector_fund_flow 与个股聚合主路径）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

**① 一句话**：给 net_inflow_pct/capital_score 供"钱从哪来到哪去"，双路径=东财行业资金流直采 + money_flow×成分聚合。

**② 实测**：`implementations/sector_fund_flow_collector.py`（90 行业，09-15 开采，改判"在产+短史"）；money_flow 5,579 股 2026-06-01 起；`market_fund_flow_daily` 东财 CDN 掐灭后 hybrid 回填；B2 探针：state 表 `net_inflow_pct` 有值、**`capital_score` 活表从未落值**（dossier NULL 普查在册，本册复核分布仍为全 NULL 面之一）。

**③ 六向**：①上游 东财 fflow / tushare money_flow。外部：**北向实时披露 2024-05-13 起停**两源（证券时报 stcn 2024-05-14 http://www.stcn.com/article/detail/1203876.html ；财富界 fortunechina 2024-05-13 https://www.fortunechina.com/jingxuan/39161.htm ）→ 与本仓 northbound 停 3 个月、hk_connect_flow 退役互证，**属持续性外部披露风险而非本仓故障**。②下游 state 第五成分；无独立下游。③算法 截面 percentile_ranks。外部：已查无（板块净流入的公开方法论口径不统一，本轮检索未得两源）。④后端 短史+CDN 掐灭史。⑤前端 板块资金排序页。⑥字段 在；画像=仅 6 日级史→分位不可算（闸 4 GAP）。

**④ 缺口**：G7（在册）；D12（在册）；**L03-B4-G1 capital_score 恒空=成分定义有、供数无、无人裁定去留**。

**⑤ 三态裁定**：G7=挂起（Owner 双轨选项定案）；G1=**施工 P1**（二选一：接三标尺供数或从契约剔除观察列，二者都消灭"空列被误当有效信号"的人工复核）。

**⑥ 日志**：R1 内部：NULL 面复核→signal；R2 外部：北向披露两源→signal（跨环节证据）；R3 外部：净流入口径→noise，归因=口径不统一/无权威件。

**封矿判据**：六向封口 → **子类目封矿**。
