---
ttl: task_bound
title: E4 WYF-3 封矿核实作业簿——#264→#271→#285 证伪加厚链终态确认
session: st-tdchain-20260917
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# E4 WYF-3 封矿核实作业簿

## 六向台账

- **目标**：交接令任务 3（WYF-3 特征工程立项：vol_z 钝化→换固定基准量纲重校）。经侦察**前班已完整执行并终态**，本环节降级为封矿核实：确认报告/裁定/引擎三面全部落地，登记后续方向供 Owner 立项。
- **证据**：
  - 裁定链：#264（阈值维持）→ #271（证伪置零+重跑触发条件）→ **#285（v2 重跑后证伪加厚，维持置零）**。
  - 报告：docs/_working/wyf3/wyf3_preregistered_protocol.md（v1）+ wyf3_preregistered_protocol_v2.md（跑数前写死）+ wyf3_recalibration_report.md（根因实证：2015 股灾 18 个大跌日 vol_z 全≤1.34，含 2015-08-24 -8.75% z=0.04）+ **wyf3_v2_rerun_report.md（终态：三族固定基准候选 0/204 合格，L0 层零检出）**。
  - 引擎：src/zephyr/regime/features/wyckoff_engine.py——WyckoffParams 新增 sc_vol_mode/sc_vol_ratio/sc_vol_epct/sc_vol_qratio/sc_vol_baseline_window/sc_vol_expanding_min_periods 六字段（默认值=历史路径逐位一致）+ sc_volume_leg 三族固定基准单一实现+PIT 自反测试；_DIMENSION_STATUS 维持 falsified。
  - 预注册 hash 锁：.runtime/tmp/wyf3_v2/wyf3_v2_prereg.json（wyf3_v2 作废+wyf3_v2_r2 有效）。
- **块**：B1 本核实簿；B2 dev 落地状态核实（报告文件是否已 commit 入 dev——执行时核实，若仍在分支/未跟踪则登记不代提交，属 st-wyffeat-20260916 会话资产）。
- **依赖**：无。
- **三态**：挖干（封矿）。维度维持置零，无需新裁定。
- **下一步**：无施工。v3 候选方向已由 v2 报告 §8 登记（普跌结构腿 advance/decline_count 推荐、成交额口径、判据语义层），**均属裁定#271 触发条件第 2 条=须 Owner 立项**，本战役不开（留下一步证据指针即止）。

## 长尾登记

- v2 报告 §7 警示：预注册网格外诊断点（量比 1.3/1.2、分位 0.90）已被数据污染一次，开 v3 必带先验声明+信息量门（池化 t≥2 等）前置。
- overlay_features.s2_wyckoff_score 回退路径的 20 日窗参数契约失真=独立债，不在本裁定范围（v1 报告 §7.3）。
