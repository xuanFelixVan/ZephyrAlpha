---
ttl: task_bound
doc_type: log
title: L03-B3 子类目挖矿簿 · 编排落库双槽与 sector_preference 产出面
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

**① 一句话**：把 B2 纯函数结果按 close_final/pre_open 两槽落库，并产 sector_preference（大盘×情绪→偏好档）。

**② 实测**：`src/zephyr/data/sector_state_pipeline.py`（MATURITY=testing，`_PANEL_SQL` :78，总闸 `_flag_disabled()` :163-165=`data/runtime/sector_state_pipeline.disabled`（实测不存在=启用态），`run_close_final` :353 / `run_pre_open` :475）；调度槽 scheduler 双槽 15:10/09:15 在 HEAD。**表侧实测（本册 CH 探针）**：`sector_state` 按 stage：close_final 426,516 行/986 日；**pre_open 仅 469 行/1 日（2026-09-23）**；逐日：09-17/18/21/22/23=469 码、**09-24=729 码（首个 881 入产日，ingest 09-25 07:10）**；`sector_preference` **全表仅 2 行**（09-23 OFFENSIVE/tilt1.2/banned=lagging、09-25 BALANCED/tilt1.0，皆 pre_open 侧，emotion 值 0.482319/0.397086 与情绪表 close_final 逐位吻合）。

**③ 六向**：①上游 B1/B2 + 锚定 dominant + 情绪（D13 已接，见 L02-H 册）。②下游 `load_l2_admission`（B6 册）+ GPU sectorcond 包 + G05 待接。③算法 22 号 spec。外部：已查无（编排层无外部方法论）。④后端 **pre_open 槽实质停摆（986 日 vs 1 日）+ 偏好表近乎空转**（本册净新增定量）。⑤前端 板块页/门快照。⑥字段 齐；画像=09-24 为宇宙切换日（469→729）无口径标记。

**④ 缺口**：G4（在册，已随 d27e0f0df3 落地，见 B6）；**L03-B3-G1 pre_open 槽近停摆（仅 1 日产出）却仍被当在产面引用**；**L03-B3-G2 宇宙切换日 09-24 无 universe_change 标记列/无注记**；**L03-B3-G3 偏好表消费语义（仅盘前）未声明**（与 L02-H-G1 同案，主场在此）。

**⑤ 三态裁定**：G1=**施工 P1**（查 run_pre_open 失败原因并补跑，或显式降级为"仅 close_final"）；G2=**施工 P2**（meta 注记，零判据变更）；G3=挂起（解锁=状态轴词表登记批）。

**⑥ 日志**：R1 内部：stage/日粒度探针→signal（两条新缺口）；R2 内部：总闸旗标实测→signal（沿用确认）。

**封矿判据**：六向封口 → **子类目封矿**。
