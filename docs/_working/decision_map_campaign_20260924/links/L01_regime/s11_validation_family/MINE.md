---
ttl: task_bound
title: L01-S11 子模块挖矿簿 · 验证·校准·回放对拍族
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（成熟度以本册头注实测封顶）
---

# L01 · S11 验证·校准·回放对拍族

**① 职责一句话**：用四接口（A 充分性/B 概率质量/C 开关/D 聚合稳健/E 交叉验证）与双轨对拍证明状态层自身可信，是"状态层也要考试"的执行面。

**② 现状实测（MATURITY 逐文件头注 grep 实测）**

| 件（src/zephyr/regime/validation/） | 行数 | MATURITY |
|---|---|---|
| `overfitting_guard.py` | 252 | **production**（唯一） |
| `wyckoff_walkforward.py` | 901 | **validation** |
| `a3_transition_coverage.py` / `a4_feature_importance.py` / `b2_crps.py` / `b3_confidence_distribution.py` / `d1_confidence_grid.py` / `d3_aggregation_perturbation.py` / `e1_walkforward_cv.py` | 157/169/142/201/213/125 | design ×7 |
| `phase2/a1_sample_sufficiency.py` / `a2_hmm_overfitting.py` / `b1_probability_calibration.py` / `b4_transition_accuracy.py` / `confidence_calibrator.py` / `phase2_runner.py` | 374/341/346/475/788/667 | design ×6 |

外围件：`scripts/backtest/validate_p0_discrimination.py`、`compare_state_dualrun.py`（HMM vs 锚定双轨）、`alg01_ab_redo.py`（ALG-01 双臂）；t0 对拍物 `docs/_working/t0_matrix/reconcile_pack_v1_sample20.csv` + `_summary.csv`（本册目录实测存在）。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：全史七维概率 + transition 记录 + IS/OOS 双段前向收益 + historical_events.yaml 事件锚。外部：可靠性评分外部口径=Wilson LB/Brier/CRPS/DSR 族（17 号文 §一与 18 号文已立法，沿用不重复引） |
| ②下游 | 内部：印教材 QA 闸（state_health：最长连续同态>250 天=疑似锁死，人工复核）+ 考试验收链 + Owner 裁定证据面。外部：已查无（内部治理面） |
| ③算法 | 内部：两阶段温度缩放校准器（788 行）+ CRPS + walk-forward CV。外部：多模型集成投票为现役单 HMM 之外的二期候选（ensemble-HMM 文，2026-01，https://www.researchgate.net/publication/397111020 ，与 S1 册同源→**标"待第二独立源"**） |
| ④后端 | 内部：**定期重验无排班**——14/16 件 design 态、全靠人工/事件批触发；c1 开关对比件缺位（编号跳过 c1，实测目录内无 c1_*） |
| ⑤前端 | 内部：验证报告以 run 档案（VAL-P0-*）落文件。外部：已查无 |
| ⑥数据字段 | 内部：需 predict_log_proba 原始后验（detector 专供 :797-836）；无缺失字段。质量画像=对拍仅 20 行抽样（样本级非例行闸） |

**④ 缺口清单**：P1-T3"在算未交"（09 号文在册）；**L01-S11-G1 重验无排班（验证族整体 design 态）**；**L01-S11-G2 对拍仅抽样 20 日、非全史例行闸**；**L01-S11-G3 编号缺口 c1_* 从未存在（族命名不完整，后人易误以为漏件）**——三条均册内未见。

**⑤ 三态裁定**：G1=**挂起排期**（解锁=编排器把重验挂为季度事件触发；终局要自动重验，但先决=L09 车道编排器落地，且宪法 §9.3 禁 cron/Timer）；G2=**施工 P2**（全史对拍成本≈40s 级，可自动化，消灭"人抽样"）；G3=**施工 P3 文档面**（在验证族 README/本册登记"c1 号位空置属历史命名，非漏件"，防后人重挖）。

**⑥ 挖矿日志**：R1 16 件 MATURITY 实测→signal（纠正 SKEL"14/16 design"为"14 design + 1 production + 1 validation"）；R2 目录编号完整性→signal（c1 缺位实证）；R3 外部 ensemble HMM→signal（沿用+待第二源）；R4 外部"regime model validation scheduling 惯例"→noise，归因=方向无矿（治理域自有立法）。

**封矿判据**：六向封口 + 族完整性实测 → **子模块封矿**。
