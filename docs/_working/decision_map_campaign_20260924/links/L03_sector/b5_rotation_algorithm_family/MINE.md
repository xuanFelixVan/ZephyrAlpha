---
ttl: task_bound
doc_type: log
title: L03-B5 子类目挖矿簿 · 轮动算法族（RRG/状态/电风扇/龙头/动量等 16 件，逐件归位表）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（本册=SKEL B4+B5 拆分后的净增子类目层）
---

**① 一句话**：`signal_ashare/sector/` 内除聚合核外的全部板块算法件——逐件登记其成熟度与真实消费边，是本环节"零件全套、通电极少"的可核对底账。

**② 实测（行数=wc；MATURITY=头注；引用与消费边=本册 grep 实测）**

| 件 | 行 | MATURITY | 实证消费边 |
|---|---|---|---|
| sector_divergence（电风扇/5 状态/CONSENSUS_CLIMAX） | 1,141 | testing | **唯一实证生产接线**：`plan_engine/boundary_revision_engine.py:92 import SectorDivergenceResult`、:139 `TRIGGER_SECTOR_TOP_RISK`、:149 |
| sector_leader | 614 | testing | 头注"MVP 无——观测先行不接交易" |
| sector_state_aggregator | 541 | testing | 见 B2/B3（本册不重复） |
| sector_detail_enricher | 452 | testing | 候选（板块详情页） |
| sector_analyzer | 420 | **production** | 头注自曝"quant_short_term_strength_engine **未接线**（2026-09-05 AI-08 审计实证）" |
| sector_momentum_persistence | 360 | testing | 候选（主线持续性页签） |
| sector_volume_anomaly | 283 | testing | 候选（情绪页量能异动卡） |
| sector_crowding_launch | 296 | **production** | CONSUMERS="运行时装配批"=未装配 |
| sector_attribute_rules | 273 | testing | 候选（板块页属性列） |
| sector_rrg / sector_gate / sector_breadth / sector_pullback / sector_siphon / sector_momentum / sector_rotation_state | 236/169/161/156/143/113/113 | **new** ×7 | 全部"(待 G05 选股引擎…)" |

**③ 六向**：①上游 880/881 日 K（RRG 需 ≥62 日）、板块内涨停梯队、领涨史。②下游 除 divergence 外全部悬空。③算法 外部：轮动三参数框架（排名期/持有期/再平衡）与拥挤度标尺——行业拥挤度公开口径两源（乐咕乐股申万一级拥挤度 https://www.legulegu.com/stockdata/sw-congestion 2026-09-08 快照；TMT 交易拥挤度研报转载 证券之星 2024-10-22 https://4g.stockstar.com/detail/JC2024102200029644 ）+ 拥挤度度量综述一篇（新浪财经 2026-08-03 https://finance.sina.cn/2026-08-03/detail-inikzeat6114597.d.html ）→ 三源支持"换手/成交占比 z 分"配方，与本仓 crowding_launch 同构（改造点：需流通股本，D21 在册）。④后端 16 件中 15 件无生产边；`sector_rotation_score_mapping.py` 仍 `sector_overlay_active=False`。⑤前端 板块详情页候选件多。⑥字段 881 族仅 1 日 state → 轮动/RRG 的 881 行业维**近史完全不可算**（B2/B3 探针同证）。

**④ 缺口**：G14（三标尺升维）/G5（坐标系）/D17（三标尺原料待接线）在册；**L03-B5-G1 15 件零消费边的算法农场未做内收申报**；**L03-B5-G2 881 行业族轮动态从未产出（补采后无人重跑 RRG/动量）**。

**⑤ 三态裁定**：G1=**施工 P1（内收申报，走宪法 §4.2 零触发零消费→退役/挂接二选一，并入季度合并审计窗）**；G2=**挂起排期**（解锁=补采史回填 + 回放批，先有 62 日窗才可算）；G14/D17=在册挂起（预注册新卡，S10-6.2 禁本轮调权）。

**⑥ 日志**：R1 内部：16 件头注与消费边逐件实测→signal（**SKEL B4 只列 8 件、B5 只列 4 件，本册补齐 16 件**）；R2 外部：拥挤度三源→signal；R3 外部：RRG 原厂→沿用 SKEL §11-1。

**封矿判据**：`ls src/zephyr/signal_ashare/sector/` 17 文件**全部归位**（1 件在 B2 册、16 件在本册）→ **子模块封矿**。
