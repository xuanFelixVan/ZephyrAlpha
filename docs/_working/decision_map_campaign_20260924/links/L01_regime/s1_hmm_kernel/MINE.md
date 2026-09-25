---
ttl: task_bound
title: L01-S1 子模块挖矿簿 · HMM 四态检测核（MOD-REGIME-001）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（六向封口，缺口三态裁定见 §5）
---

# L01 · S1 HMM 四态检测核

**① 职责一句话**：把 6 列 PIT 特征矩阵拟合成四态 GaussianHMM 并输出灰度概率（不出硬标签），是全环节唯一"状态真值"生产者。

**② 现状实测**

| 项 | 实测值 | 出处 |
|---|---|---|
| 代码 | `src/zephyr/regime/core/regime_detector.py` 1,163 行，MOD-REGIME-001，MATURITY=production | 本册 Read 实测 |
| 态词表 | `REGIME_STATES = ["r1","r2","r3","r4","r10","r11","r12"]`（4 HMM + 3 overlay） | regime_detector.py:107 |
| 不变量 | Σ=1.0 / Shrinkage≤1.0 / 缺数 fail-closed 双位（RB-STATS-02 观测位 + R-055a 数值位） | 头注 :8 |
| 地板值 | `RISK_SIGNAL_FLOOR: Final = 0.30`，缺腿时 RiskSignal 落地板而非 1.0 | :419/:1059/:1063/:1071/:1079/:1091 |
| 档表 | `_CONFIDENCE_BANDS`（:195）→ 对外 `CONFIDENCE_BANDS`（:217）→ 映射 :226-229/:1019 | 同件 |
| A16 对账探针 | `confidence_band_divergence()` 输出 detector_bands/alloc_bands/identical_tables | :232/:261/:263 |
| 生产触发面 | 无独立任务——经 S6 印教材链（`maybe_refresh_regime_snapshot`）日更，本件纯计算 | 见 S6 册 |
| 测试面 | `tests/regime/test_regime_detector.py` + `test_rb_stats_regime_failopen.py`（fail-open 钉住件） | tests/regime 目录实测 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：X 矩阵列序钉死 MOD-REGIME-002 FEATURE_NAMES，列0=realized_vol_pct（主锚）/列2=kalman_slope，见 :62/:112；overlay_signals dict 与 risk_signal_inputs 由 S2/S5 供。外部：多模型集成投票治单 HMM 不稳——"A forest of opinions: A multi-model ensemble-HMM voting framework for market regime shift detection and trading"（ResearchGate 镜像，AIMS 系出版方，2026-01）https://www.researchgate.net/publication/397111020 。与 SKEL §14.1 所引同族（跨验第二源） |
| ②下游 | 内部：消费 `regime_snapshot_history` 的代码文件实测 24 个（含 SKEL 未列的 `scripts/audit/t0_gpu_condition_pack.py`、`t0_six_phase_materialize.py`、`scripts/backtest/ibt/ibt_runner.py`、`ibt_mining_matrix.py`、`scripts/data/pattern_win_rate_materialize.py`）→ 详表见 S10 册。外部：regime 输出仅作风险滤网而非点位预测（SKEL §14.1 已引 QuantStart/QuantConnect，本册不重复入图，标"沿用"） |
| ③算法 | 内部：组件锚定重排治 label switching（裁定编号 304，ruling_registry 已登记）已实装于 `apply_label_anchored_order`。外部（label switching 处置的行业口径）：GMM/HMM 分量排序约束为通用做法，见"Common mistakes with Gaussian Mixture Models (GMM)"（BytePlus 工程博客，2025-03-09）https://www.byteplus.com/en/topic/400978 ——单源，**待验证**级不入图（仅佐证既有实现无返工必要） |
| ④后端 | 内部：hmmlearn 惰性导入 + n_init=3 + 降级矩阵（缺库/拟合败/缺列/态数不匹配→均匀分布）。外部：已查无（查法：本轮以"market regime detection library python hmmlearn walk forward"主题检索未见优于现役 hmmlearn+自研锚定的可复用件；hmmlearn 在用于役，无需换轨候选） |
| ⑤前端 | 内部：人工面 = 仪表盘 warroom（`src/zephyr/frontend/dashboard/components/warroom.py` 经 index_regime_panel 消费）；登记不施工。外部：已查无（查法：状态层呈现无外部方法论诉求，概率分布呈现=SKEL §14 之外零新候选） |
| ⑥数据字段 | 内部：需要 6 列（realized_vol_pct/hurst_dfa/kalman_slope/cross_asset_corr/ad_ratio/volume_anomaly）——全部由 S4 特征管道产，schema 在、质量画像见 S4 册（399106 广度断更为已知洞）。外部：字段口径与业界一致（波动率分位/换手异常/涨跌家数比）；已查无"必须补第五类字段"的结论 |

**④ 缺口清单**

| 编号 | 内容 | 状态 |
|---|---|---|
| D7 | 8 态转移先验/相似日/Brier 三消费点未接线（需求册在册） | 沿用（归属见 L02-G 册） |
| L01-S1-G1 | 4 态降维后 ConfidenceSignal 档表阈值仍沿用 9 态校准值（detector :193-194 自注），未做 4 态重校准——**册内未见编号** | 新登 |
| L01-S1-G2 | 锚定恢复"标签语义可跨 refit 比较"≠"方向预测力可跨期比较"（:64-67 裁定警示），但消费侧 owner_band_t/开关器仍把 dominant 当方向轴使用——**册内未见** | 新登 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由（量尺=终局全貌） |
|---|---|---|
| D7 | 挂起排期 | 解锁条件=三零件（8 态/相似日/校准）消费方接线批（L02-G 册 L02-G-C01）；终局要（预测→Brier 回填→自动校准闭环=消灭人工判"像不像"），非封矿 |
| L01-S1-G1 | 施工（随 S5 档表统一批） | 阈值与态数不匹配=系统性偏差，终局全自动化下无人肉眼纠档；判据口径不动，仅重校准值来源，属修复非新立 |
| L01-S1-G2 | 挂起排期 | 终局要"态→风险分档"与"态→方向"两套消费语义分离；解锁条件=S7 六段真源收编完成（附录 C 步 2）后统一定语义词表，现禁改判据 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | 备注 |
|---|---|---|---|
| R1 | 内部：detector 常量/档表/地板/探针行号复核 | signal（:107/:195/:232/:419 全部实测复核） | — |
| R2 | 内部：消费面全仓 grep（24 文件） | signal（较 SKEL 13 点净增 5 个脚本侧消费者） | — |
| R3 | 外部：ensemble-HMM + GMM 排序约束 2 轮检索 | signal 1（ensemble 投票=二期待验证候选）／noise 1（排序约束单源，**归因=来源为工程博客非学术/一线，降优先级**） | — |
| R4 | 外部：后端可复用实现替代 hmmlearn | 已查无（查法见 §③④） | 记档 |

**本册封矿判据**：六向均已填（含"已查无+查法"），S1 矿脉清单（态词表/锚定/温度/降级/档表/消费面）无未挖长尾 → **子模块封矿**。
