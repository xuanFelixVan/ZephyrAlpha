---
ttl: task_bound
title: L01 大盘状态判定 · 子模块清单与封矿状态总勾表
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: 环节 1 子层挖干交付
---

# L01 · 子模块总勾表（父层=SKEL.md，本表=子层唯一入口）

> 读法：SKEL.md=环节级骨架（父层，含 10 子块树与 L01-C01~C10 施工项）；本目录下 `sNN_*/MINE.md`=子模块级挖干簿（每份含 ①职责 ②现状实测 ③六向台账 ④缺口清单 ⑤自审闸三态 ⑥挖矿日志）。编号沿用：L01-Cxx（SKEL 施工项）/Dxx（需求册）/LK-xx（09 号文）/LK-L01-x（SKEL 新登）；本层新缺口以 `L01-Sn-Gm` 续编并注"册内未见"。

## 1. 子模块清单与状态

| 子簿 | 覆盖件（主） | 封矿态 | 净新增缺口 | 对 SKEL 的改判 |
|---|---|---|---|---|
| `s1_hmm_kernel` | regime_detector.py HMM 核 | 已挖干 | G1 阈值待重校准 / G2 态语义双消费 | — |
| `s2_overlay_transition_engine` | overlay_features(1,383)+overlay_signals_builder(850)+TRANSITION_CONFIG | 已挖干（公式逐行余量转施工） | G1 阈值债账本未落盘 / G2 盘中触发缺位 / G3 供数零调用 | — |
| `s3_overlay_signal_suppliers` | wyckoff/lppl/synthetic_vix/evolution/双 volatility 件/chip/index_sensor | 已挖干 | G1 四只零消费件 / G2 production 未装配 / G3 LPPLS 换轨候选 | 四件零消费由散文改为引用计数实证 |
| `s4_feature_pipeline` | regime_feature_builder(892)+features 12 件+cross_sectional+data_loader | 已挖干 | G1 死取数面 / G2 无漂移哨兵 / G3 广度补位两读面 | — |
| `s5_shrinkage_risk_signals` | detector③④⑤+risk_signal_builder+risk_features 11 系数 | 已挖干 | G1 校准器断链 / G2 档表阈值待重校准（主场） | — |
| `s6_snapshot_production_slot` | print_regime_history+pipeline_events+fw_backtest+DDL | 已挖干 | G1 run 台账无盘点面 | **口径以实测封顶：3,629=行数、1,819=唯一日、5 个 run**（LK-L01-1 定量收口） |
| `s7_anchored_state_track` | anchored_state_machine+任务+DDL+allocation_inputs | 已挖干 | G1 本地 SQL=第二真源 / G2 成熟度失真 | **L01-C01 已以本地常量旁路（import 实测 OK）但 schema 符号仍缺 → 判据未达**（LK-L01-2 改判） |
| `s8_six_phase_truth_chain` | environment_switch+framework_composer+auto_mount+orchestrator | 已挖干 | G1 微观腿阈值无考试卡 | **六段切源已进 HEAD（commit d27e0f0df3）**；**six_phase_history_v1.csv 仍未落地（生成器在 HEAD、产物不在）** |
| `s9_alt_regime_channel` | alt_regime_signals+loader | 已挖干 | G1 融合腿未定义 / G2 F23 无毕业排期 | **消费端非零调用**：condition_package.py 已直读该表作 GPU 状态轴 |
| `s10_downstream_consumer_surface` | 24 个消费文件全清单 | 已挖干 | G1 状态读门面缺失（7 处 SELECT）/ G2 三新消费者未入册 | 消费点 13→24（净增 5 脚本侧） |
| `s11_validation_family` | validation/ 16 件 + 三脚本 + t0 对拍 | 已挖干 | G1 重验无排班 / G2 对拍仅抽样 / G3 c1 号位空置 | 成熟度改判：14 design + 1 production + 1 validation |
| `s12_secondary_model_farm` | 六件顶层模块 + TDM L1 八节点对表 | 已挖干 | G1 图-码三处错位 / G2 production 无挂点 | **SKEL 十子块树之外的净增矿脉** |

**合计 12 子簿：已挖干 12 / 在挖 0**（各簿内"公式级逐行对表"余量一律转施工清单，不作 MINING 挂着——判据见挖矿 SOP §3：矿脉枯竭=六向全查无+无未挖长尾，逐行读码属施工而非挖矿）。

## 2. 本环节新缺口汇总（子层净增，共 21 条）

| 编号 | 一句话 | 三态 |
|---|---|---|
| L01-S1-G1 / S5-G2 | 4 态降维后置信档阈值仍沿用 9 态校准值 | 施工（随档表统一批） |
| L01-S1-G2 | dominant 被当方向轴消费 vs 锚定只保标签可比 | 挂起 |
| L01-S2-G1 | overlay 阈值债有声无账本 | 施工 P2 |
| L01-S2-G2 | 8 转换盘中触发面缺位 | 挂起（含反驳者一问留痕） |
| L01-S2-G3 | 四只供数件零调用 | 施工（内收申报） |
| L01-S3-G1~G3 | 零消费件 / production 未装配 / LPPLS 换轨未评估 | 施工 / 施工 / 挂起 |
| L01-S4-G1~G3 | 死取数面 / 特征漂移哨兵缺 / 广度补位两读面 | 施工 / 施工 / 施工 |
| L01-S5-G1 | 788 行校准器与生产节流链断开 | 挂起 |
| L01-S6-G1 | run 台账无机读盘点面（5 run 谁作正身靠人记） | 施工 P1 |
| L01-S7-G1~G2 | 本地 SQL 第二真源 / 成熟度与职责不符 | 施工 / 施工 |
| L01-S8-G1 | 六段微观腿阈值无预注册卡 | 挂起 |
| L01-S9-G1~G2 | 另类信号融合腿未定义 / F23 无毕业排期 | 挂起 / 挂起 |
| L01-S10-G1~G2 | 状态读取门面缺失（7 散落 SQL）/ 新消费者未入册 | 施工 P1 / 施工 P0 |
| L01-S11-G1~G3 | 重验无排班 / 对拍仅 20 日抽样 / c1 号位空置 | 挂起 / 施工 / 施工 |
| L01-S12-G1~G2 | TDM 图-码三处错位 / production 无挂点 | 施工 P1 / 挂起 |

## 3. 本环节穷尽性声明

**扫过的源（全部只读）**：①`config/trading_decision_map.yaml` L1 全段（266-545，含 module_ref/module_id 逐节点抽取）②`src/zephyr/regime/` 全包 46 个 .py（17,337 行，头注 MATURITY/CONSUMERS/INVARIANTS 逐件、core 与产槽件行号级）③产槽链 `strategy_pipeline/{pipeline_events,fw_backtest,screen_source,daily_gate_snapshot,daily_decision_orchestrator}.py` ④消费链 `pf_alloc/` 三件 + `plan_engine/` 两件 + `strategy_factory/owner_*` ⑤六段链 `signal_ashare/core/environment_switch.py`、`pf_core/strategy_engine/framework_composer.py`、`scripts/backtest/auto_mount.py` ⑥`src/zephyr/data/config/tasks.yaml`（anchored_state_build:647 / alt_regime_signal_refresh:2783 等 regime 系任务全查）⑦`schemas/categories/backtest/` 两件 DDL ⑧`tests/regime/` 全目录 ⑨CH 只读探针（regime_snapshot_history / regime_state_anchored 行列与 run 分布）⑩全网检索 6 轮（ensemble-HMM、GMM 排序约束、volatility-managed 两源、LPPLS 论文+两开源实现、变点族沿用）。

**封顶判据**：12 子簿六向全部为"有发现"或"已查无+查法"，无空格；SKEL 十子块树 + 本层净增 2 子块（供数件家族拆分、次级模型农场）后，`src/zephyr/regime/` 目录内**无一文件落在任何子簿之外**（对表方式=find 全清单 46 件逐一归位）。噪音轮 7 轮全部记档并归因；未以"连续噪音"或轮数封矿。

**边界声明（越界不挖）**：情绪预测件（L0-04）归 L02-G 册；板块 dominant 消费归 L03-B3 册；做T状态门归 L05 车道； battle_map 图回指治理归治理班。
