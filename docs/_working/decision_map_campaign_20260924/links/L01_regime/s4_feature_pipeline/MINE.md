---
ttl: task_bound
title: L01-S4 子模块挖矿簿 · 特征管道与取数面（MOD-REGIME-002 家族）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（六向封口，公式逐行对表余量记 §6）
---

# L01 · S4 特征管道与取数面

**① 职责一句话**：把 ClickHouse 十余张原料表加工成"HMM 六列 + overlay/risk 供数 dict"的 PIT 特征面板，并提供 walk-forward 季度重拟合的 schedule。

**② 现状实测**

| 件 | 行数 | 实测要点 |
|---|---|---|
| `src/zephyr/regime/regime_feature_builder.py` | 892 | MATURITY=production（:7）；六列特征定义在头注 :32-37：F1 realized_vol_pct（20 日 HV 的 250 日分位）/F2a hurst_dfa/F2b kalman_slope/F3 cross_asset_corr（三指数两两相关 60 日均值）/F4 ad_ratio（**399106 全市场涨跌家数比 tanh**）/F5 volume_anomaly（量 z-score 20 日）；`FEATURE_NAMES` 起于 :103；ALG-01 横截面 4 列为**尾部追加开关**（默认 False 时输出与历史逐字节一致，:46-48）；CONSUMERS 头注 :5=run_c1_shrinkage_validation + BM-BT-03-E |
| `src/zephyr/regime/features/regime_data_loader.py` | 629 | 取数面 9 个 load_*：money_flow:252 / **alt_regime_signals:261** / sector_kline:284 / limit_up_down:293 / hk_connect_flow:302 / option_iv_surface:311 / multi_tf_kline:320 / news_sentiment:329 / index_valuation:341；PIT 纪律=**shift(1) 统一在构造器 _precompute 做，loader 不管**（:31 头注） |
| `src/zephyr/regime/cross_sectional_features.py` | 562 | MATURITY=testing（:7）；4 列列序钉死 cross_dispersion/avg_pairwise_corr/vol_dispersion/momentum_breadth；样本 <min_cs_names→该日 4 列全 NaN（不填补）；抽样 seed 固定（:8 INVARIANTS） |
| `features/market_features.py` / `trend_features.py` | 171 / 215 | F1/F3/F4/F5 与 F2a/F2b 纯函数源 |
| 生产触发面 | — | **无独立日更任务**：整条管道只活在 S6 印教材子进程内；日常特征级漂移监控无挂点 |
| 测试面 | — | `tests/regime/test_cross_sectional_features.py`、`test_trend_features.py`、`tests/regime/features/` 目录（实测在册） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：TableRegistry 唯一真源取数（c1_market.kline_index 四指数 000300/000905/399006/399106、kline_daily_hfq、money_flow、sector_kline、limit_up_down、hk_connect_flow、option_iv_surface、multi_tf、news_sentiment、index_valuation、alt_regime_signal）。hk_connect_flow 已永久退役（tasks.yaml:209）→ loader 仍保留该函数=**死取数面**。外部：横截面离散度/相关性作为 regime 特征的机构口径未见可引新源（查法："cross-sectional dispersion regime feature" 类检索本轮未命中一线件）→ 已查无记档 |
| ②下游 | 内部：S1（X 矩阵）/S2（overlay_signals）/S5（risk_signal_inputs）三消费面 + `scripts/backtest/alg01_ab_redo.py:27`（ALG-01 双臂对齐生产配置）+ 挂图侧 `auto_mount._breadth_frame` 复用 BREADTH_INDEX 口径（auto_mount.py:218）。外部：已查无（下游为本仓内部件，无外部惯例） |
| ③算法 | 内部：walk-forward 季度重拟合（`_quarter_end_dates` :872，滚动 5 年训练窗）+ EMA α=0.15 schedule（:783）。外部：特征重要性与过拟合验证已有件（`validation/a4_feature_importance.py`、`overfitting_guard.py`，MATURITY 分别 design/production）→ 属仓内既有件，登记"沿用"（净零，不另立） |
| ④后端 | 内部：缺"特征级漂移哨兵"（vol_pct/slope 断供或分布漂移无人报）；已知断更史=399106 广度（F4 依赖，known_data_gaps F4，EQW_ALLA 补位在 auto_mount 侧而非本管道侧）。外部：已查无（查法：漂移监控属工程件，业界无统一"标准件"可引，不虚构） |
| ⑤前端 | 内部：无（特征层不呈现）。外部：已查无（查法：本层呈现诉求为零，登记即封顶） |
| ⑥数据字段 | 内部：六列全部"字段在 + 数据在"（F4 依赖 399106，属已知洞）；ALG-01 四列依赖 kline_daily_hfq 复权真源（复权失维绊线 builder :118-122）。质量画像实测：`limit_up_down` 全表 49 个唯一交易日、max 2026-09-24（本册 CH 只读探针）→ **字段在但历史深度极浅**，overlay T3 维因此降档；`option_iv_surface` 有 load 函数、未见消费实证 |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| D4 | 期权 IV 曲面口径未明（loader 有函数、无消费实证） | 需求册沿用 |
| D33 | 盘中五证据列断供（kline_index 家数列 07-02 后） | 数据充分性矩阵沿用 |
| L01-S4-G1 | hk_connect_flow 退役后 loader 死函数未清（第 8 个"零消费件"） | 册内未见 |
| L01-S4-G2 | 特征层无漂移哨兵：断供/分布漂移只能靠下游印教材失败反推 | 册内未见 |
| L01-S4-G3 | F4 广度补位（EQW_ALLA）只活在挂图侧 auto_mount，S4 主管道未共享同一补位件=两读面 | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| D4 | 挂起排期 | 同 S3 册：解锁=Owner 侧 API/账号 |
| D33 | 挂起排期 | 盘中链治理属 L03-B1/L05 车道，本层只登记边界 |
| L01-S4-G1 | 施工（P3 微修） | 死函数=假可用面，AI 自动化选型时会被误引；净零（删除即收敛） |
| L01-S4-G2 | 施工（P2） | 消灭"人盯断供"这一人工环节，终局直接要；实现走既有 known_data_gaps + 哨兵件，不新建 gate |
| L01-S4-G3 | 施工（并入 S7 真源收编批） | 两读面=第二真源风险（宪法 §6 SSOT 方向）；随六段真源收编一并统一 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：builder 六列定义 + loader 九函数行号实测 | signal | — |
| R2 | 内部：CH 只读探针（limit_up_down 49 日 / emotion / sector 面） | signal（把"字段在≠数据可得"落到具体数字） | — |
| R3 | 外部：横截面离散度机构口径 | noise | 归因=**方向本就无矿**（内部反查已足，外部件对现算法零增量）→ 已查无 |
| R4 | 外部：特征漂移监控标准件 | noise | 归因=查询词落在运维监控通用文，与交易特征语义错位 → 改判已查无 |

**本册封矿判据**：六向封口 + 三件新缺口登记，未挖长尾=12 件 features/ 正文公式逐行（施工级余量，非挖矿级）→ **子模块封矿**。
