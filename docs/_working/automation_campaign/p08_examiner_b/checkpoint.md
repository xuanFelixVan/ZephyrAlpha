---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·游标
---

# 游标

cursor: 10-15 班次 01 已交账（本族 74 张 preregistered 逐张普查＝0 张可出有效分，出分 0/8 未达保底，三道闸已定位并移交）
last_run: 2026-10-15 07:52（date 实测，耗时约 23 分钟）
last_batch: p08-1015-01 普查班（G1 双臂 29／G2 机判面待扩 39／G3 缺 oos_window_ref 5／G4 panel×持仓池 1）
notes: |
  游标由本岗每批推进；监督员(⑩)可代修。
  下一班开工前置（任一成就即有分可出）：⑥席给 5 张 G3 卡补 oos_window_ref（照抄本卡 window.oos）
  ⇒ TDM-P-P2-04/calibration/06 与 /07 两张全市场面卡立刻可考；否则本席继续只交普查，不凑假红。
  防重入两址并存期须两址同读（旧址 docs/_working、新址 docs/04_research_records/cross_domain）。
  本族零卡申报 derived_series/target_series；card_binding.py:74 SERIES_DIR 仍指已 ABSENT 旧路（HEAD 未修）。
