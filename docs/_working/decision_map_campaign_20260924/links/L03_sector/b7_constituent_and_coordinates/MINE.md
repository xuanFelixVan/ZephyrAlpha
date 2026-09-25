---
ttl: task_bound
title: L03-B7 子类目挖矿簿 · 成分映射 SCD-2 与板块坐标系
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（含补采后成分断层新证）
---

**① 一句话**：sector_constituent（SCD-2）是"个股→板块"唯一上溯枢纽，坐标系（469/596/90/729 四口径）是全层可比性地基。

**② 实测（本册 CH 探针）**：`c1_market.sector_constituent` FINAL **95,124 行 / 595 板块**（与 SKEL 同，**881 补采后成分表未扩容**——B1 实测 state/K 线已到 729 码，成分仍 595 → 881 行业族成分缺口新证）；valid_from 4 批次、valid_to 全 NULL；概念轴 concept_board 375 概念。

**③ 六向**：①上游 同花顺/通达信成分采集。②下游 涨停比分母、money_flow 聚合、labels.yaml 881 锚定 7 板。③算法 as-of 谓词正确。外部：**前视偏差两源**——"用今天的沪深300成分股回测十年前为什么可能高估结果"（同花顺量化 2026-06-09 https://quant.10jqka.com.cn/view/article/JVUR6XTVOW1580260HRHWZEJ09 ）与"回测陷阱：前视偏差、过拟合、数据窥视"（quant67 2026-05-01 https://quant67.com/post/quant/20-backtest-pitfalls/20-backtest-pitfalls.html ）→ 与 G12 概念轴硬 gate 同构，**非真 PIT 归属即回测虚高**。④后端 4 批次叠加致 42 日重复计数（dossier §2 在册）。⑤前端 板块详情。⑥字段 在；画像=valid_to 全 NULL=无法回溯历史成分。

**④ 缺口**：G5/G12/D18 在册；**L03-B7-G1 补采后成分表未同步扩容（729 宇宙 vs 595 成分=聚合上溯断层）**；**L03-B7-G2 valid_to 全空→as-of 只能"当前态"（前视风险常在）**。

**⑤ 三态裁定**：G1=**施工 P0**（补采连带义务，先修否则 P1 v2 与 state 都在混合宇宙上算）；G2=**挂起排期**（解锁=SCD-2 版本化采集改造，属数据班）；G5=挂起（Owner 坐标系裁定页 L03-C04）。

**⑥ 日志**：R1 内部：成分表探针→signal（新断层）；R2 外部：前视两源→signal；R3 外部：板块分类标准件（申万/GICS）→已查无（本轮未做定向检索，如实记）。

**封矿判据**：六向封口 → **子类目封矿**。
