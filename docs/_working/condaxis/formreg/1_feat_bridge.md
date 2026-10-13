---
ttl: task_bound
title: 环节[1] 特征层复用——regime 46py 桥接（FEATURE_NAMES/walk-forward/7 维概率）
created: '2026-10-13'
session: st-condaxis-20261013
status: mining_workbook
family_id: CONDAXIS-CAMPAIGN
completes_when: 该环节施工完成且随 CONDAXIS-CAMPAIGN 归档
---

# 1. 逐项台账（✅ 均为 2026-10-13 本车道 Read/grep 实查，附 file:line）

| 件名 | 仓内真源路径:行号 | 现状 | 消费方 | 缺口 | 六向定位 |
|---|---|---|---|---|---|
| FEATURE_NAMES 6 特征族 | src/zephyr/regime/regime_feature_builder.py:102-109（realized_vol_pct/hurst_dfa/kalman_slope/cross_asset_corr/ad_ratio/volume_anomaly 实读） | ✅ 实查在产 | RegimeDetector X 矩阵（regime_detector.py:62 列序假设=MOD-REGIME-002 钉死序）；index_regime_panel 四指数卡 | 两态线直接喂同列序，零改动 | ③算法复用+④后端 |
| 截面 4 特征（CROSS_SECTIONAL_FEATURE_NAMES） | src/zephyr/regime/cross_sectional_features.py（regime_feature_builder.py:70 import 实读；:46-47 尾部追加开关 include_cross_sectional 默认 False） | ✅ 实查在产（A/B 臂未转正） | regime_feature_builder（开关臂） | 两态线是否收编 4 列待 P2（A/B 增量证据先行） | ③+④ |
| walk-forward 季度重拟合 | src/zephyr/regime/core/regime_detector.py:8（INVARIANTS "HMM 4态walk-forward季度重拟合"）；E1 统计口径 train_years=5/refit QE/46 季度边界（validation/e1_walkforward_cv.py 文件头实读） | ✅ 实查在产 | regime 探针/重校批（#304） | 两态 jump 层沿用同节拍还是另定——P2 呈批（建议同节拍省对账） | ③ |
| 7 维概率输出（4 HMM+3 overlay） | regime_detector.py:8（INVARIANTS "不输出硬标签只输出7维灰度概率"）；REGIME_STATES 七态清单 :107 | ✅ 实查在产 | B2 CRPS、index_regime_panel、两态线语义重排输入 | 两态层以 7 维概率为**输入之一**做语义重排+全交易日覆盖（研究册 §12.1） | ②下游+③ |
| 锚定重排（#304） | regime_detector.py:118 anchored_component_order / :151 apply_label_anchored_order / :596 anchor_labels 开关（fit 后按训练窗统计确定性重排，PIT 只用训练窗） | ✅ 实查在产 | walk-forward 跨期可比性 | jump 层无此问题（跳变惩罚显式）；规则层无此问题（结构阈值） | ③ |
| 主目标指数 000300 | regime_feature_builder.py MARKET_PROXY="000300"（:111 附近实读）；anchored_state_machine.py:165-171 load_close=c1_market.kline_index symbol='000300' | ✅ 实查在产 | 全 regime 链 | 研究册 §13-2 呈批：两态主目标=沪深300（建议默认）钉死+卡面披露 | ⑥数据字段 |
| 广度源 BREADTH_INDEX=399106 | regime_feature_builder.py（BREADTH_INDEX 常量区实读，ad_ratio 消费 advance/decline） | ✅ 实查在产 | ad_ratio 特征 | 399106 断更史（survey §7.4 可得≠可用成例 dd04d9d20c）——两态线引用前必须补数据质量画像 | ⑥ |
| 复权真源绊线 | regime_feature_builder.py _CS_HFQ_TAIL_DAYS=20 / _CS_HFQ_MIN_COVERAGE=0.5（近端 close_hfq 覆盖率<0.5 抛 RegimeFeatureError 实读） | ✅ 实查在产 | C1-C4 特征产线 | 两态线若用收盘价序列须同绊线 | ④+⑥ |
| 四指数 regime 卡（1 引擎×4 代理） | src/zephyr/regime/index_regime_panel.py:1（MOD-REGIME-008，INVARIANTS"4套配置非4套模型"+"严禁输出点位/方向预测"） | ✅ 实查在产 | Dashboard IDX-02 | 两态线扩展到板块/宽基的架构先例（引擎通用、参数组换面） | ②+⑤前端 |
| regime_state_anchored 表 | src/zephyr/regime/core/anchored_state_machine.py:84 _TABLE="c1_backtest.regime_state_anchored"；消费者 5 处 grep 实据（internal_compute_provider/sector_state_pipeline/pf_alloc.allocation_inputs/anchored_state_machine/t0_condition_pack） | ✅ 实查在产 | pf_alloc/t0 链/板块管线 | 两态逐日状态建议另立新表（禁改本表语义），命名走 TRAE-028 | ②下游 |
| 两态专用特征（峰谷距离/双门槛计数/trend-scanning span 网格） | 全仓 grep "trend_scanning\|trend-scanning" src+scripts 零命中（2026-10-13） | ⬜ 空白待建 | [2] 状态机规则层 | P2 钉 span 网格（t 值对网格敏感，研究册 §4.3）；P-S 窗参数 A 股重标定（§3.4 缺口） | ③+④ |

# 2. 与既有资产的边界（不推倒重来清单）

1. **直接复用零改动**：FEATURE_NAMES 6 列及列序、walk-forward 节拍、7 维概率输出、PIT 口径（detect(t) 只用 ≤t-1 特征，index_regime_panel INVARIANTS 实读）。
2. **参数换面**：主目标指数从"regime 链默认 000300"升格为"两态线 P2 钉死+卡面披露"（§13-2）；跨标的面（板块/宽基/个股）只换参数组，引擎通用（index_regime_panel 1×4 先例）。
3. **新建**：两态专用特征件（峰谷/门槛计数/t 值 span）——新模块，登记 creation_token+大白话简介；两态逐日状态新表。
4. **禁触碰**：regime_detector.py 的 X 列序假设（MOD-REGIME-002 钉死序）——两态特征如需加列只能学 cross_sectional 先例"尾部追加+默认关+逐字节一致"。

# 3. 施工要点（代码实读中的坑）

1. **列序即契约**：regime_detector.py:62/:112 明示 X 列序=FEATURE_NAMES 钉死序（列0=realized_vol_pct 主锚、列2=kalman_slope）。两态线接同一特征帧时**禁止重排列**——锚定重排的 vol_col/slope_col 按列索引取数，列序漂移=锚定错位。
2. **A/B 开关先例**：截面 4 特征经 include_cross_sectional 开关尾部追加、默认 False、关闭时输出与历史逐字节一致（regime_feature_builder.py:46-49 实读）。两态新特征进共享帧必须同款纪律：先证增量再谈转正。
3. **ad_ratio 缺数中性 0 坑**：market_features.py:136 实读"缺数据处为 0（中性）"——广度断更日特征静默变中性，两态层若对广度敏感须在特征桥侧加覆盖画像告警，不能等状态层发现。
4. **复权真源失维**：close_hfq 覆盖率绊线抛错是产线级的（RegimeFeatureError）；两态规则层用价格序列（P-S 峰谷搜索）时**必须同款前置校验**，禁拿前复权漂移面找峰谷。
5. **7 维概率是"输入之一"不是真值**：overlay 态 r10-r12 由 TRANSITION_CONFIG 阶梯（trigger/confirm/fail）覆盖产生（regime_detector.py:304-330 实读），两态语义重排须理解 overlay 概率是规则覆盖值非似然值——B1 校准时不能当同质概率混桶。

# 4. 自审闸三态裁定（过度工程三问：终局有位吗/已有产物覆盖吗/成本实算）

| 项 | 裁定 | 理由 |
|---|---|---|
| 特征桥（6 特征+7 维概率直通） | **施工** | 终局=条件轴全自动供料，regime 资产现成，边际成本≈接线工时；不建则两态线人工拼特征=制造人工环节 |
| 截面 4 列收编 | **挂起排期** | 终局有位（板块面差异化特征），但 A/B 增量证据未出；解锁条件=regime 班 A/B 对照转正裁定 |
| trend-scanning t 值特征 | **施工**（限训练标签用途） | [3] 辅轨必需；实时面只认已闭合 span（PIT 红线，研究册 §4.3），成本=一个纯函数件 |
| 多标的参数组面（板块/个股） | **挂起排期** | 姊妹车道（SECTOR-CAMPAIGN）职责；本线只留引擎通用性，解锁=板块线五件套过审 |
