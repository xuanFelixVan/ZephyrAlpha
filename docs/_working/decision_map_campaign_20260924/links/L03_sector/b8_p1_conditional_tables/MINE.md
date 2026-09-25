---
ttl: task_bound
title: L03-B8 子类目挖矿簿 · P1 板块×相位条件概率表（消费端）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（SKEL"v1 已交付 469 板"实测已被 v2 覆盖，见 §②）
---

**① 一句话**：P(板块收益|六段相位) 三张表=本环节专属概率面，供 GPU 条件轴与轮动查询。

**② 实测（本册 `data/strategy_intake/conditional_tables/` 逐文件解析）**：`p1_sector_by_phase.csv` **4,362 行 = 729 板块 × 6 相位**（**881 族 128 码已入表，764 行**）→ **SKEL B8"469 板×6=2,806 格"已过时，宇宙侧 v2 实质已跑**；exam_ok=True **2,874 格**；`sector_name` 列 **0 行有值**（与 B1-G1 同源）；`p1_phase_momentum.csv`：expansion n=156,724/−0.0158、capitulation −0.0269、distribution −0.0241、euphoria −0.1049、accumulation −0.0169、**ignition 仅 727 行/1 日/+0.5664（不可用级样本）**；`p1_phase_stay.csv`：expansion 均值 8.82 日/capitulation 11.22/euphoria 3.33/ignition 1.0；`p1_top5_by_phase.csv`（**README 记作 .txt，文件实为 .csv=清单与产物不符**）。目录实测另存 `_cache_880.parquet`。

**③ 六向**：①上游 regime 快照（S6 册实测 1,819 日真深度）+ 六段相位 + 880/881 K 线。②下游 GPU grid_gpu_sectorcond、BM-SEL-08 查询原料。③算法 Wilson LB + MIN_OBS=30；外部：短期反转/高低切在 A 股成立的两源（新浪研报复盘 2026-08-06、BigQuant 因子研究 2026-06-05，URL 见 B2 册）与 T2 负相关互证。④后端 **重算脚本仍在 `.runtime/tmp/`（未转正 scripts/）**；**README 数字与产物不一致**；图书馆资产登记未见证据。⑤前端 Owner 查询表。⑥字段 名称全空；ignition 稀薄。

**④ 缺口**：LK-03/04 号文 §四（在册）；**L03-B8-G1 P1 无 v1↔v2 对比报告（DU-01 验收第 3 条未交）**；**L03-B8-G2 README 口径漂移（469→729、.txt→.csv）**；**L03-B8-G3 重算无排班（一次性脚本）**。

**⑤ 三态裁定**：G1=**施工 P1**（对比报告是验收线，缺它 DU-01 不能销口）；G2=**施工 P0 文档面**（生成器重出 README，禁手改数字）；G3=挂起（解锁=编排器/季度重估循环，宪法 §9.5 静态清单禁手工）。

**⑥ 日志**：R1 内部：五 CSV 全解析→signal（v2 已跑、三条新缺口）；R2 外部：反转两源→沿用 B2 册引文。

**封矿判据**：六向封口 → **子模块封矿**。
