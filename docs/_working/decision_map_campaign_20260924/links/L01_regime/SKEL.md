---
ttl: task_bound
title: L01 大盘状态判定（regime）· 挖干作业簿 SKEL
created: 2026-09-25
sid: st-mining-20260924-L01（链路 L01 挖矿班，重发批）
lane: decision_map_campaign
status: final（只读挖掘+本文件唯一交付件；禁 commit；论断带路径行号；未读指针如实列 MINING）
mining_sources: src/zephyr/regime/ 全包 + 产槽/消费链实探 + t0_matrix 六段全史链 + battle_map_09 + 战役 01/09/12/17 号文 + 附录C + 全网标准件检索（§14）
doc_type: log
---

# L01 · 大盘状态判定（regime）挖干作业簿

> 骨架真源=`docs/_working/decision_map_campaign_20260924/09_link_skeletons.md` 环节 1（79-147 行）；
> 总纲=`../README.md`（六向台账+自审闸三态+施工纪律）。本簿=L01 环节唯一挖干交付件。
> **挖掘深度声明（诚实分级，逐子块标注）**：
> 【A 全文精读】=文件逐行读完；【B 结构级读】=头注+INVARIANTS+接口签名+关键函数已读、正文未逐行；
> 【C 未读】=仅指针在册。SEALED 判据按 `../README.md` §自审闸：六向全填+指针已读（A/B 级视为已读并
> 如实标注级别）+最新算法对表完成（§14）。

## 0. 子块全树（L01 父子模块穷举，10 子块）

```
L01 大盘状态判定（regime/六段相位）
├─ S1 检测器核·HMM 4 态基座（MOD-REGIME-001 regime_detector.py）        [SEALED·A]
├─ S2 overlay 覆盖层 r10-r12 + 8 转换（TRANSITION_CONFIG/overlay_features/
│    overlay_signals_builder + wyckoff/lppl/synthetic_vix/evolution 供数件）[MINING·B]
├─ S3 Shrinkage 链（ConfidenceSignal×RiskSignal×fail-closed×A16 对账）   [SEALED·A]
├─ S4 特征管道与供数件家族（MOD-REGIME-002 builder + features/ 12 件
│    + risk_features/risk_signal_builder + cross_sectional_features）    [MINING·B]
├─ S5 快照入库与自动产槽（print_regime_history→pipeline_events→CH 表）   [SEALED·A]
├─ S6 锚定态双轨（anchored_state_machine·裁定#229·regime_state_anchored）[SEALED·A]
├─ S7 六段折算真源链与相位传导（SIX_STATES→唯一映射→R2SIX→六段全史）    [SEALED·A]
├─ S8 alt_regime_signal 另类传导（AltRegimeSignalProvider→c1_market）    [SEALED·A/B]
├─ S9 下游消费面（11 消费点：总闸/分配链/编排器/计划链/策略工厂/板块管线）[SEALED·A/B]
└─ S10 验证·校准·回放对拍族（validation/ 16 件+P0 检验+reconcile 对拍）  [MINING·B]
```

与使命给定清单对表：7 态 HMM=S1；overlay r10-r11=S2；快照入库=S5；六段折算=S7；
alt_regime_signal 传导=S8；回放对拍=S10；**实探新增**：S3（Shrinkage 链为独立子系统，含 A16
双档表对账件）、S6（锚定态双轨判定器——与 HMM 并行的第二真值轴）、S4（特征/供数件家族，
占 regime 包代码量约 60%）、S9（消费面 11 点独立成块，总闸闸口语义在此落地）。
auto_mount.py 三版本分叉案=总指挥已登记 BLOCKED，本簿 §7 引用不重查。

---

## 1 · S1 检测器核·HMM 4 态基座 【SEALED·A】

**件**：`src/zephyr/regime/core/regime_detector.py`（1,163 行，MOD-REGIME-001，production，v0.4.0）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | 特征 X 矩阵（S4 供，`detect()` 入参 `regime_features["X"]`，列序钉死 MOD-REGIME-002 FEATURE_NAMES，regime_detector.py:62-63/885）；overlay_signals dict（S2 供，:654）；risk_signal_inputs 13 参数（S3 供，:655） |
| ②数据原料 | 不直接触库——纯计算核。依赖 hmmlearn（惰性导入 :731）；7 态枚举 r1-r4+r10-r12（:107-109）；锚定列假设 vol_col=0/slope_col=2（:114-115） |
| ③状态输出 | `RegimeProbabilities`（7 维灰度概率 Σ=1，:470-486）+`ShrinkageResult`（:488-514）+`TransitionTriggered`（:517-531）+`RegimeSnapshot`（:534-542）；不输出硬标签只输出灰度概率（INVARIANTS :8） |
| ④下游消费 | S5 印教材（print_regime_history.py:53-55）；MOD-PA-007 RegimeMetaAllocator + BM-BT-03-E 回测验证（头注 CONSUMERS :5）；S10 验证族经 predict_log_proba（:797-836，校准器输入） |
| ⑤自动化挂点 | 无独立挂点——经 S5 印教材链间接自动化（walk-forward 季度重拟合发生在 builder.build_shrinkage_schedule 内）；本块自身纯函数/内存件 |
| ⑥缺口债 | 沿用：D7（8 态转移先验/相似日/Brier 三消费点未接线，09 号文环节 1③）；本块新注：4 态降维后 ConfidenceSignal 阈值仍沿用 9 态校准值待精调（:193-194 自注）；锚定恢复标签语义不恢复方向预测力（:64-67 裁定警示） |

**关键机制实录**（对表 §14 标准）：9 态→4 态降维（BIC Kneedle 拐点=4，A2 OOS/IS 一致率 0.34<0.7 证据，:38-47）；**组件锚定治 label switching**（裁定#304，apply_label_anchored_order :151-181：r4 槽=训练窗斜率均值最小组件，其余按波动率均值升序占 r1/r2/r3；只重排组件参数不改似然，锚定量只用训练窗=PIT）；**在线推断**=predict_proba 取最后一步（因果防前视，:896-897）+温度缩放 tempering（:902-914，非 Guo2017 严格 TS，:800-803 如实自注）；**降级矩阵**=hmmlearn 缺/拟合败/缺特征/态数不匹配→均匀分布 1/4（:735/:883/:886-888/:899-901）；n_init=3 取最优 log-likelihood（C1 实测 EM 数值敏感致 schedule 不可复现，:758-763）。
**自审闸**：SEALED（六向全填；regime_detector.py 全文精读；与全网实践对表：walk-forward 滚动重拟合/按均值排序锚定/仅作风险滤网——三点均已实现，§14.1）。

---

## 2 · S2 overlay 覆盖层 r10-r12 + 8 转换 【MINING·B】

**件**：regime_detector.py TRANSITION_CONFIG（:303-406，T1-T6/S1/S2 阶段配置）+`src/zephyr/regime/features/overlay_features.py`（1,383 行，production，8 转换评分纯函数）+`src/zephyr/regime/overlay_signals_builder.py`（850 行，OverlaySignalsConstructor，Phase 2b）+供数件 wyckoff_engine.py（476）/lppl_detector.py（186）/synthetic_vix.py（228）/evolution_signals.py（190）/volatility_regime_alerter.py（223）/volatility_squeeze_breakout.py（317）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | overlay_signals={"transitions":{T_id:{dim:score}}}（regime_detector.py:928-932）；评分维度原料=合成 VIX（synthetic_vix）、Wyckoff FSM（wyckoff_engine）、LPPL 赶顶（lppl_detector）、广度/乖离微观腿、板块 HHI/连板晋级（overlay_signals_builder._precompute :246，_compute_t3_inputs :677，_compute_sector_metrics :733，_compute_limit_up_metrics :763） |
| ②数据原料 | kline_index 四指数+money_flow+sector_kline+limit_up_down+hk_connect_flow（残租退役后 NaN→0 降级，tasks.yaml:209）+news_sentiment+index_valuation（regime_feature_builder.py:323-356 取数面）；S2 维度≈34 个纯函数（overlay_features.py:168-1354 函数清单 s1_vix_panic_score…s2_bad_news_flat_score） |
| ③状态输出 | P_overlay(r10/r11/r12)（取各转换最高 p_overlay，regime_detector.py:935-949）+8 转换 TransitionTriggered 记录（stage=strong_confirm/confirm/trigger/fail，:838-872）；r10 CRISIS/r11 RECOVERY/r12 BREAKOUT |
| ④下游消费 | _merge_probabilities 压缩 HMM 概率质量（:955-990）→7 维合并→S3 Shrinkage；危机期门控（#ARCH-REGIME-OVERLAY-001 方案 A：overlay 仅 #1<1.0 生效，:677-696）；B4 转换触发准确性验证（S10） |
| ⑤自动化挂点 | 无独立排班——仅随 S5 印教材链 walk-forward 逐日构造（build_shrinkage_schedule 内 _overlay_ctor.build_for_date(dt)，regime_feature_builder.py:425-437/510）；**盘中实时触发面缺位**（8 转换无盘中评分任务） |
| ⑥缺口债 | 沿用 D2/D3（涨停/炸板/连板梯队 family 级无 FCT 条目，T3 money_effect/leader 维度原料受限）；evolution_signals 三函数未接入生产调用链（_TRANSITION_DIMS 外，evolution_signals.py:39 自注）；volatility_regime_alerter/squeeze_breakout 的 overlay_dims 契约"运行时装配批接线"未见落地（两件头注 CONSUMERS 自注）；S2 vix 校准 30 已落（:391-397，14 号 §4.0） |

**未读指针（MINING 清单）**：overlay_features.py 正文 1,383 行（已读头注+34 函数签名）；overlay_signals_builder.py 正文 850 行（已读头注+_TRANSITION_DIMS :95+类结构 :143-246+分 compute 函数签名）；wyckoff_engine.py/wyckoff_walkforward.py/lppl_detector.py/synthetic_vix.py/evolution_signals.py 正文；S2 八维度阈值账本（overlay_signals_builder._warn_threshold_ledger_debt :228 暗示存在阈值债登记，未读）。
**自审闸**：MINING（六向已填，上列未读指针在案；补齐后可升 SEALED）。

---

## 3 · S3 Shrinkage 链（ConfidenceSignal×RiskSignal×fail-closed×A16） 【SEALED·A】

**件**：regime_detector.py 子模块③④⑤（:992-1131）+A16 对账件（:208-267）+消费对读 `src/zephyr/pf_alloc/core/regime_meta_allocator.py:94-99`（CONFIDENCE_THRESHOLDS）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | 7 维概率 max(P)（S1 产出）；RiskSignalInputs={"params":{#1-10/#12 系数},"opportunity":{#11/#13}}（risk_signal_builder 供，S4）；主腿 #1=realized_vol |
| ②数据原料 | ConfidenceSignal=max(P) 四档映射×稀有态折扣（:195-206 档表；4 态均匀=0.25，:193-194 注）；RiskSignal=clamp[0.30, RiskBase×共振惩罚+机会恢复,1.00]（:1030-1091，#1 门控 2026-08-06 C1 二次调优） |
| ③状态输出 | ShrinkageResult{value≤1.0, confidence_signal, risk_signal, shrinkage_enabled, degraded_legs, risk_signal_source}（:488-514）；**R-055a fail-closed**：缺数→地板 RISK_SIGNAL_FLOOR=0.30（:419）+neutral_fail_closed 溯源（:424），实测修前危机断供反而放量 3.14×（:72-75） |
| ④下游消费 | regime_snapshot_history.shrinkage 列（S5 落库）→pf_alloc 分配链总节流（allocation_inputs.py:13 注记③）；allocation_orchestrator.py:48（PFA-3 治本=本件把 PIT 概率喂进分配器）；anchored cap 分家后仓位数字仍归 L1 总闸（allocation_inputs.py:612-614 设计注） |
| ⑤自动化挂点 | 随 S5 链日更；shrinkage_enabled 开关=C1 一票否决验证接口（:488-503） |
| ⑥缺口债 | **A16 两套档表未统一**（detector :195-200 降序下界表 vs allocator CONFIDENCE_THRESHOLDS :94-99 升序上界表，数值/方向均不同；confidence_band_divergence() :232-267 机械对账已备，owner_adjudication="A16-pending"）；confidence_signal/risk_signal 分量列在快照表恒 NULL（print_regime_history.py:151-152/179-180 自注，R-K9 误报率分母剔除的分量面缺）；沿用 D5（宏观四组参数部分缺口） |

**自审闸**：SEALED（A 级全文精读+消费侧 regime_meta_allocator/allocation_inputs/crisis_gate 对读+档表数值实录）。

---

## 4 · S4 特征管道与供数件家族 【MINING·B】

**件**：`src/zephyr/regime/regime_feature_builder.py`（892 行，MOD-REGIME-002，production）+`features/` 12 件（market_features 171/trend_features 215/synthetic_vix 228/risk_features 467/overlay_features 1383/regime_data_loader 629/wyckoff_engine 476/chip_distribution_engine 464/evolution_signals 190/index_sensor 135/lppl_detector 186）+`cross_sectional_features.py`（562，MOD-REGIME-007）+`risk_signal_builder.py`（344，RiskSignalConstructor）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | CH 多源经 TableRegistry：c1_market.kline_index（000300/000905/399006/399106 四指数，:111-116）、kline_daily_hfq（横截面面板，复权真源失维绊线 :118-122）、money_flow/sector_kline/limit_up_down/hk_connect_flow/option_iv_surface/multi_tf/news_sentiment/index_valuation（:323-356 取数面）、alt_regime_signal（S8，regime_data_loader.py:261-280） |
| ②数据原料 | HMM 6 特征列序钉死（:102-109）：F1 realized_vol_pct/F2a hurst_dfa/F2b kalman_slope/F3 cross_asset_corr/F4 ad_ratio/F5 volume_anomaly；ALG-01 横截面 4 列开关（默认关，:43-48）；RiskSignal 13 参数（risk_features 11 系数纯函数 :75-433+siphon/multi_tf divergence 构造，risk_signal_builder.py:292-330） |
| ③状态输出 | features DataFrame（PIT shift(1) 内置）+X 训练矩阵+shrinkage schedule（EMA α=0.15，:783）+overlay_signals/risk_signal_inputs 逐日 dict；walk-forward 季度重拟合（_quarter_end_dates :872，滚动 5 年训练 :67） |
| ④下游消费 | print_regime_history.py:125-141（印教材主链）；scripts/backtest/alg01_ab_redo.py:27（双臂对齐生产配置）；挂图侧 auto_mount._breadth_frame 复用 BREADTH_INDEX 口径（auto_mount.py:218） |
| ⑤自动化挂点 | **无独立日更任务**——特征管道只活在印教材子进程内；日常特征级监控（vol_pct/slope 漂移）无挂点 |
| ⑥缺口债 | chip_distribution_engine 打回 trial（裁定#257④：production 系虚标、零消费端+真实数据伪分布，chip_distribution_engine.py 头注；risk_signal_builder 侧仅 stub 常量，:6 注）；index_sensor=design 态；option_iv_surface 取数面在册但 D4 未明（09 号文环节 1③）；hk_connect_flow 永久退役（tasks.yaml:209）；沿用 D2/D3/D4/D5/D33 |

**未读指针（MINING 清单）**：regime_feature_builder.py 正文 150-892 行（已读头注+函数清单+关键段）；market_features/trend_features/synthetic_vix/risk_features/wyckoff_engine/chip_distribution_engine/index_sensor/lppl_detector/cross_sectional_features 正文；regime_data_loader.py 正文 196-629 行（已读 load_alt_regime_signals :261-280 全段）。
**自审闸**：MINING（六向已填；上列未读指针在案）。

---

## 5 · S5 快照入库与自动产槽 【SEALED·A】

**件**：`scripts/backtest/print_regime_history.py`（293 行，MOD-BT-032）+`src/zephyr/strategy_pipeline/pipeline_events.py`（maybe_refresh_regime_snapshot :784-840）+`fw_backtest.py`（ensure_regime_snapshot :1127-1160/regime_snapshot_freshness :1111-1125）+`scripts/ch/apply_regime_snapshot_ddl.py`（DDL 真源=schemas/categories/regime_snapshot_history.py）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | daily_kline/kline_daily/kline_index 任一任务 SUCCESS（SIM_DAILY_WAKE_TASKS，pipeline_events.py:150）；业务日=resolve_pf_alloc_trade_date（禁墙钟猜日，:815） |
| ②数据原料 | S4 特征管道全量（印教材 walk-forward 2014 起训练窗，print_regime_history.py:67/:281） |
| ③状态输出 | c1_backtest.regime_snapshot_history：16 列（run_id/snapshot_commit/trade_date/p_r1-p_r12/dominant/confidence/confidence_signal/risk_signal/shrinkage/probs_json，:60-63）；run_id=VAL-P0-<ts> **每次执行新 run_id**（:105）；落库 CH_COMMITTED 才算成功 fail-closed（:242-246）；run 档案归档（SOP-D） |
| ④下游消费 | 见 S9 全表（分配链/编排器/门快照/计划链/策略工厂/整装回测/screen_source/板块管线） |
| ⑤自动化挂点 | **在产**：maybe_refresh_regime_snapshot=唯一自动产出者（挂点 A，2026-09-16 接电；docstring :37-40/:105-110 自注），一业务日至多一印（业务日级永久记号 :816-819，记号先落再动手防重印风暴 :812 注）；滞后闸=ensure_regime_snapshot max_staleness_days=**1**（fw_backtest.py:117，Owner 批 2026-09-21 与消费方 D1 口径对齐），缺口窗补印（max(trade_date)+1~今天，append-only 零整表翻倍，:1134-1137/:1150-1156）；人工逃生口=直接跑 CLI（:805）；master_switch.ensure_regime_fresh 二道闸（daily_loop_master_switch.py:128-160，消费方口径补印） |
| ⑥缺口债 | **LK-L01-1（本簿新登）行数/日数口径混计**：LEDGER.md §1 补充实测"3,627 行/1,817 唯一日（每日恰双写）"（2026-09-22，双 run 全窗重印所致）+owner_regime_switcher/data_loader.py:102"3621 行/2 run=各 1812 整"同证——而 01_goal_and_architecture.md:24 与 12_data_universe_census.md:105 把"3,629"记作"**日**"（实为行数，唯一日≈1,818）；**真实 PIT 全史深度≈1,818 交易日非 3,629 日**；screen_source.py:160-168 window_days 用 count() 不去重=窗口天数双计污染（自注"行数口径=auto_mount 判定同源"）；fw_backtest.load_regime_series :285-299 无 run_id 过滤+同日双行 dict 覆盖次序未定（非确定性去重）；沿 D29（滞后阈值错位——代码面已治本见 ⑤，文档面未同步→L01-C02）；confidence_signal/risk_signal 分量列 NULL（→L01-C08） |

**自审闸**：SEALED（A 级：三件产槽文件全文精读+DDL 脚本+消费 SQL 真源 alloc_shrinkage_daily.py:93-99 对读；行数口径发现已登记施工项 L01-C03）。

---

## 6 · S6 锚定态双轨（regime_state_anchored·裁定#229） 【SEALED·A】

**件**：`src/zephyr/regime/core/anchored_state_machine.py`（204 行，design）+`src/zephyr/data/config/tasks.yaml:647-659`（anchored_state_build 任务）+`schemas/categories/backtest/backtest_regime_state_anchored.py`（59 行 DDL-as-Code）+`scripts/ch/build_anchored_state_history.py`/`apply_anchored_state_ddl.py`（CLI 在册）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | c1_market.kline_index 000300 收盘（load_close :165-183，start=2016-06-01 留热身）；调度依赖 kline_index_incremental（tasks.yaml:652） |
| ②数据原料 | hv20=20 日 log 收益 std×√252；vol_pct=250 日滚动分位（compute_features :112-133，全 rolling PIT 严格） |
| ③状态输出 | c1_backtest.regime_state_anchored：trade_date/dominant(r3 低风险·r2 中·r1 中高·r4 高)/vol_pct/close/ma20/60/120/data_source（:160-163；DDL 回档件 :31-47）；**锚定阈值 0.30/0.60/0.80 零拟合**（classify_state :98-109，态身份跨期恒定=HMM label switching 结构性不可能，头注 :9-15） |
| ④下游消费 | internal_compute_provider.py:656-667（anchored_state capability 路由）；allocation_inputs.py:612-700（锚定态总暴露熔断上限：cap=1.0−0.70×clamp((vol_pct−0.30)/0.70)，AGG 消费切换终批 2026-09-23，anchored_cap.disabled 一键旁路 :645-651）；sector_state_pipeline.py:58/:458-461（板块状态两 stage 读 dominant）；validate_p0_discrimination/compare_state_dualrun（DDL 件 CONSUMERS 注）；12 号文:106 实测 2,239 行 2017-07-11..09-24 健在（单行/日，无双写问题） |
| ⑤自动化挂点 | **在产**：tasks.yaml:647-659 anchored_state_build，schedule=daily_kline，source=internal，trading_day_only=true（依赖当日 000300 收盘）；全量重算幂等 40s（任务 description 自注） |
| ⑥缺口债 | **LK-L01-2（本簿新登）schema 缺符号=活体导入断裂**：allocation_inputs.py:620-622 `from schemas.categories.backtest.backtest_regime_state_anchored import SQL_LATEST_ANCHORED_STATE`，该 schema 文件（59 行）**无此符号**——本班活体 import 测试实测 `IMPORT FAIL: cannot import name 'SQL_LATEST_ANCHORED_STATE'`→allocation_inputs 及其下游（crisis_gate/allocation_orchestrator/pipeline_events 分配链导入面）当前在主区不可导入；即附录 C 修复清单第 6 步（appendix_C_six_state_truth_chain.md §4.6"dev 缺符号随车修"）在 HEAD 未落；**语义双词表未裁定**（附录 C §3 附带+t0_ceiling_capacity_exam.py:287"dominant_is_vol_band"）：锚定表 dominant 实为波动率风险四档（r3=低波），而 DDL 注释仍写"r1 低波震荡/r3 牛市趋势"（backtest_regime_state_anchored.py:35）——同名 rN 两套语义（7 态 HMM vs 4 档波动），附录 C 步 5 待 Owner 裁定 |

**自审闸**：SEALED（A 级：anchored_state_machine 全文精读+tasks.yaml 任务块+DDL 件全文+消费三点实读；两处债已登 LK-L01-2/施工项 L01-C01）。

---

## 7 · S7 六段折算真源链与相位传导 【SEALED·A】

**件**：`src/zephyr/signal_ashare/core/environment_switch.py:41-49`（SIX_STATES 词表）+`src/zephyr/pf_core/strategy_engine/framework_composer.py:152-158`（REGIME_STATE_TO_ACTIVATION_PHASE 唯一映射位点）+`scripts/backtest/auto_mount.py:129`（R2SIX 挂图侧同表）/:225-248（phase_overlay 微观腿+resolve_six_phase 两轴合成）+`daily_decision_orchestrator.py:100-124/527-587`（BUDGET_BANDS+S2 regime 腿）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | regime_snapshot_history.dominant（S5）宏观腿；广度微观腿=399106 advance/decline（断更日 EQW_ALLA 补位，auto_mount.py:203-221，known_data_gaps F4） |
| ②数据原料 | R2SIX={r10→capitulation, r4/r11→accumulation, r3→expansion, r12→ignition}，r1/r2 不路由（宁漏勿误）；微观相位=euphoria（乖离 250 日分位≥0.90 ∧ 20 日上涨家数占比分位≥0.85 ∧ 60 日收益>0）/distribution（亢奋记忆窗 60 日内破 MA20 ∧ br20<50%）（auto_mount.py:232-245，全 trailing 无前视）；PHASE_PREEMPT r10/r11 优先级最高（:248-258） |
| ③状态输出 | 当日六段相位∈SIX_STATES 六段封闭集；折算后预算带 BUDGET_BANDS（capitulation 0-10%/accumulation 20-30%/ignition 30-50%/expansion 50-70%/euphoria ≤30% 只卖不买/distribution 0%，orchestrator:100-108，全 proposed 沿 TDM-F-C1）；六段相位全史=six_phase_history_v1.{csv,meta.yaml}（1,816 日/1,054 路由，t0 班物化，LEDGER.md §3 任务①） |
| ④下游消费 | 整装回测 activation 折算（framework_composer，strict 策略 r1/r2/无快照日 α=0）；编排器 S2 腿→position_cap→S5 预算（orchestrator:548-587，缺席/陈旧/不可映射三态全落 no_trade 保守侧）；TDM-P-P2-01 做T状态门（yaml:2850，09 号文环节 1④）；挂图 CLASS_CANDIDATE_STATES（auto_mount.py:117-126，2026-09-16 车道 B 起 euphoria/distribution 可检验）；sector_preference 第一轴；P1-T1/T3 条件轴 |
| ⑤自动化挂点 | 编排器=daily_kline SUCCESS 唤醒链末棒（orchestrator:51-52）；六段全史物化**待落地**（0033 批，01_goal:26；LEDGER"已建成·待落地"，落地前置=creation_token+模块翻译登记） |
| ⑥缺口债 | **总指挥已登记 BLOCKED 案（引用不重查）**：auto_mount.py 存在三版本分叉（主区+`.aidrafts/` 多份，本班 ls 实测 `.aidrafts/st-*/scripts/backtest/auto_mount.py` ≥10 份）——以总指挥登记为准；**产线占位表已于 2026-09-25 切法定真源**（orchestrator:110-116 自注"弃用本地 v0 占位表…改为消费唯一映射位点"，主区工作副本 M 态未提交——git status 实测）；附录 C 剩余步：步 2 共享真源收编（R2SIX 与 composer 双表并存仅靠漂移守卫 test_r2six_drift_guard_vs_framework_composer 钉住）、步 4 历史结论重算标注口径版本（情绪门宽差 75% 教训：按 R2SIX=601 日 vs 占位=1,051 日）、步 5 锚定表语义裁定；euphoria/distribution 无 r 态来源⇒纯宏观腿下两段恒不激活（composer:149-151 如实披露，微观腿补齐）；沿 LK-16（六段↔五态映射未落地，09 号文环节 9⑦） |

**自审闸**：SEALED（A 级：四位点全文实读+appendix_C 全文+LEDGER 六段链全段+orchestrator 切换段实读；BLOCKED 案按指令引用不重查，不影响本子块六向封口）。

---

## 8 · S8 alt_regime_signal 另类传导 【SEALED·A/B】

**件**：`src/zephyr/alt_data/alt_regime_signals.py`（541+ 行，MOD-L00-004，production）+`src/zephyr/data/config/tasks.yaml:2783-2793`（alt_regime_signal_refresh）+`scheduler.py:1514-1517`（源路由）+`regime_data_loader.py:261-280`（消费端 loader）。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | c1_market.alt_shipping_index（BDI）/crypto_kline_daily（BTC）/sentiment_panel（恐贪）/limit_up_down+kline×stk_limit（连板高度/晋级率/炸板率）/landfall_history×track（台风 116 场）——全部已落库（模块 docstring 信号位表） |
| ②数据原料 | 5 信号位：F4_BDI_MOMENTUM_Z20/F14_BTC_MOMENTUM_30D/F15_FNG_INDEX/F23_LIMITUP_EMOTION/F7_TYPHOON_EVENT（:32-37）；F23 阶段阈值 v1=provisional（:44-48，毕业前不得进决策硬链=INVARIANT） |
| ③状态输出 | c1_market.alt_regime_signal（signal_date/signal_id/signal_value/state/detail/source，:54）；RMT 全历史重算幂等、PIT=仅用≤当日收盘（:16-17） |
| ④下游消费 | **产槽在产、消费端零调用**：regime_data_loader.load_alt_regime_signals（"供 F4/F8/F10-F12/F14/F15/F23/F25 维度用"，alt_data_consumption_plan 方案）全仓 grep 唯一出现=定义处（本班 grep 实证）；provider 头注 CONSUMERS 自注"regime 消费链（index_regime_panel/risk_signal_builder 后续接线）"=未接线；backtest/regime_validation/condition_package.py:8/:53（C-1 首批消费实证：F4_BDI_MOMENTUM_Z20 选族铁规，灰度五档×状态档条件胞） |
| ⑤自动化挂点 | **在产**：tasks.yaml:2783-2793 alt_regime_signal_refresh（schedule 档在册，source=alt_regime_signal→scheduler.py:1514-1517 路由 AltRegimeSignalProvider） |
| ⑥缺口债 | F7 校准后定位=风险日历/状态标记，禁作 BDI 收益预测因子（P0 全样本 217 场事件研究，:40-43）；F15 依赖 sentiment_panel（币圈宏观情绪面板，known_issues 自注 :55-57）；**另类信号→7 态概率/覆盖层评分的融合腿缺位**（消费端 loader 备而未用） |

**自审闸**：SEALED（A/B 级：信号位表+INVARIANTS+Provider 壳+纯函数核实读，:200-541 行正文结构级；产槽/调度/消费三点 grep 实证）。

---

## 9 · S9 下游消费面（11 消费点） 【SEALED·A/B】

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | （本块为消费汇总，输入即 S5/S6/S7 产物） |
| ②数据原料 | regime_snapshot_history（7 维概率+shrinkage）/regime_state_anchored（四档+vol_pct）/六段相位 |
| ③状态输出 | 各消费点自有产物：alloc_budget_daily/alloc_shrinkage_daily（schemas/categories/alloc_shrinkage_daily.py，MergeTree (trade_date,run_id)）、daily_gate_snapshot JSON、daily_plan 判定台账、crisis_gate_log（MergeTree 只增不改） |
| ④下游消费 | 见 ⑤ 逐点——本块即终端消费面 |
| ⑤自动化挂点+消费点实录 | ① **TDM-E-L1 总闸**（yaml:266-315，"消费 7 态概率分布当谨慎度系数"，09 号文环节 1①）；② **pf_alloc 分配链**：allocation_inputs.py:485-487 PIT 读最新快照（SQL_LATEST_REGIME_SNAPSHOT ORDER BY trade_date DESC,run_id DESC LIMIT 1，alloc_shrinkage_daily.py:93-99=自动链新 run 优先，口径正确）+anchored cap（:612-700）+crisis_gate.py:12-45（双档状态机 crisis=dominant==r10 硬拦/warning=p_r10≥θ 缩额，θ 真源 config/crisis_gate.yaml 缺省 0.5，零新建内存态每判现读）；③ **daily_gate_snapshot.py:95-130**（L1 采集，缺席→编排器 no_trade D1）；④ **daily_decision_orchestrator.py:548-587**（S2 腿：PIT 读+新鲜度判 source_date≥prev_day+六段映射+预算带合成，缺席/陈旧/不可映射→no_trade+D1_* 降级码）；⑤ **plan_engine/daily_plan.py:569-573**（_REGIME_SQL 读 dominant/confidence 作计划输入）；⑥ **plan_engine/daily_loop_master_switch.py:86/:128-160**（新鲜度闸+逃生口补印）；⑦ **strategy_factory/owner_regime_switcher**（PINNED_RUN_ID="VAL-P0-20260916-230726" 钉死单 run 读法，data_loader.py:44/:98-117；禁 FINAL 因 CH Code 181，:8 INVARIANT）；⑧ **strategy_factory/owner_band_t regime_gate.py:34-63**（trend_up 闭门集={r3,r12}+confidence≥min_confidence→门关，翻转次日生效，同 PINNED_RUN_ID :38——考试冻结口径，两考试已判 FAIL 未毕业，orchestrator:117-121 注）；⑨ **fw_backtest.py:283-299**（dominant 窗口日序，dynamic_disclosure 披露口径；:1111-1145 新鲜度体检）；⑩ **screen_source.py:48/:160-168/:214-218**（快照表当日历/窗口真源——**count() 未去重受双写污染**→L01-C03）；⑪ **sector_state_pipeline.py:58/:458-461**（板块两 stage 读锚定表 dominant）；⑫ **仪表盘 warroom.py**（index_regime_panel 人工面消费）；⑬ battle_map_09 登记面：RC-01 消费"市场状态"（:333/:341）但代码映射走 D-EX-CORE/D-FACTOR，**无一条指向 regime 表的实证消费边**；RC-12 黑天鹅"波动率体制转换"模式匹配=planned 待开发（:1799/:1806）——crisis_gate（pf_alloc）实为 RC 域唯一 regime 消费实证但未在 battle_map 登记回指 |
| ⑥缺口债 | 沿用 D29（文档面→L01-C02）；**LK-L01-3（本簿新登）**：battle_map_09 与 regime 实供件（crisis_gate/anchored cap）之间缺登记回指——风控域图上"市场状态"消费无代码边落地；owner_regime_switcher S-OWNER-002 切换器"系统性卖在低位"方向失真实证（regime_detector.py:53-56，锚定前诊断）；沿 D30/D31（state_matrix 空格/预算带 proposed） |

**自审闸**：SEALED（A/B 级：13 点逐一开卷取证带行号；消费 SQL 真源件全文对读）。

---

## 10 · S10 验证·校准·回放对拍族 【MINING·B】

**件**：`src/zephyr/regime/validation/` 16 件（a1-a4/b1-b4/c1（缺位）/d1/d3/e1/overfitting_guard production/wyckoff_walkforward/phase2_runner/confidence_calibrator 等）+`scripts/backtest/validate_p0_discrimination.py`+`compare_state_dualrun.py`+`alg01_ab_redo.py`+t0_matrix `reconcile_pack_v1_{sample20,summary}.csv`。

### 六向台账

| 向 | 内容 |
|---|---|
| ①上游输入 | regime_snapshot_history（B1 校准/B2 CRPS/B4 转换/C1 开关四接口验证输入，detector docstring :32-36）；predict_log_proba（:797-836，校准器专用原始 log 后验） |
| ②数据原料 | 全史 7 维概率+transition 记录+IS/OOS 双段前向收益（validate_p0_discrimination）；historical_events.yaml（phase2 事件锚） |
| ③状态输出 | 验证 verdict/run 档案（VAL-P0-* run_id 族）；confidence_calibrator 两阶段 TS 校准器（13 号 plan §2.2 P0-E2）；compare_state_dualrun=HMM vs 锚定双轨对拍；t0 reconcile_pack=六段两源逐日一致率 383/1,816=21.09%（appendix_C §3 引，同名 rN 两表语义不同实证） |
| ④下游消费 | 印教材质量闸（state_health QA，print_regime_history.py:77-96，最长连续同态>250 天=疑似锁死人工复核）；考试验收链（17 号文 §一判据族）；Owner 门位裁定证据（#304/#229 批） |
| ⑤自动化挂点 | phase2_runner 编排器（667 行，design）；**定期重验无排班**——A1-A4/B1-B4 全 design 态，靠人工/事件批触发；overfitting_guard 唯 production |
| ⑥缺口债 | validation/ 件 14/16 为 design 态（头注 MATURITY 实录）；c1 开关对比件的排班重验缺位；P1-T3 相位转移矩阵"在算未交"（09 号文环节 1⑥ 🟡）；回放对拍面 reconcile 仅 20 行抽样+summary（样本级，非例行闸） |

**未读指针（MINING 清单）**：validation/ 16 件正文（已读全部头注+MATURITY）；validate_p0_discrimination.py/compare_state_dualrun.py/alg01_ab_redo.py 正文；phase2/historical_events.yaml。
**自审闸**：MINING（六向已填；上列未读指针在案）。

---

## 11 · 三态汇总

| 子块 | 三态 | 一句话 |
|---|---|---|
| S1 HMM 基座 | **SEALED** | 全仓最强件，锚定/温度/降级三机制齐，与全网实践同构 |
| S2 overlay 覆盖层 | MINING | 配置与接口已封口，1,383+850 行评分正文未逐行 |
| S3 Shrinkage 链 | **SEALED** | fail-closed 已治本；A16 双档表待 Owner 选型 |
| S4 特征管道家族 | MINING | 列序/PIT/绊线已封口，12 件正文未逐行 |
| S5 快照入库产槽 | **SEALED** | 自动链在产；新发现行数/日数混计+双写污染 |
| S6 锚定态双轨 | **SEALED** | 在产零拟合；schema 缺符号=活体导入断裂（L01-C01） |
| S7 六段折算链 | **SEALED** | 法定真源链完好；产线 2026-09-25 已切（未提交）；收编/重算/裁定三步剩余 |
| S8 alt_regime 传导 | **SEALED** | 产槽在产消费端零调用——传导半线 |
| S9 下游消费面 | **SEALED** | 13 消费点逐点实证；battle_map_09 登记面缺回指 |
| S10 验证对拍族 | MINING | 四接口框架在，design 态为主，正文未逐行 |

**合计：10 子块=SEALED 7 / MINING 3 / BLOCKED 0**（S7 内引用总指挥 auto_mount 三版本分叉 BLOCKED 案，按指令不重查、不计入本簿三态）。

---

## 12 · 施工项（L01-C01 起；编号引既有账本，内收声明随项）

| # | 项 | 优先 | 内收声明 | 验收判据（对 17 号文纪律） |
|---|---|---|---|---|
| L01-C01 | **schema 缺符号随车修**：schemas/categories/backtest/backtest_regime_state_anchored.py 补 `SQL_LATEST_ANCHORED_STATE` 常量（对齐 alloc_shrinkage_daily.py:93-99 同族写法；去重口径建议 ORDER BY trade_date DESC, ingest_ts DESC LIMIT 1） | **P0** | 零新文件——改既有 DDL-as-Code 件，销附录 C 步 6 | 本簿活体复测 import OK+anchored cap 链路测试绿+`git show dev` 视角可导入（附录 C 原判据） |
| L01-C02 | **stale 阈值文档漂移收敛（D29 销口）**：fw_backtest.py:117 已=1（Owner 09-21 批），同步修 pipeline_events.py:802 注释"(3)"与 daily_loop_master_switch.py:131-133 docstring"供给方=3 错位"陈旧散文 | **P0** | 删陈旧注释零新机制；文档矛盾=事故（宪法 §4.4） | 三处文案同值=1；grep 无残留"=3"表述 |
| L01-C03 | **行数/日数口径治理+双写去重**：①01/12 号文"3,629 日"实为行数（唯一日≈1,818）——Owner 门位修正战役文件；②screen_source.window_days/window_days 调用面加 run_id 去重或唯一日计数；③fw_backtest.load_regime_series 去重确定性化；④消费面统一走 allocation_inputs.load_regime_input 先例 | **P0** | 收敛第二读取面（净 -N 散落 SQL）；不新建表 | 窗口天数=唯一日数±0；抽查 3 消费点 SQL 带 dedup 口径 |
| L01-C04 | **六段真源收编收尾（附录 C 步 2/4/5）**：orchestrator 已切（2026-09-25，M 态待提交）；剩=共享真源落位（shared.contracts 或规则 YAML）+守卫改三方同源断言+按占位口径历史结论标注重算+锚定表 rN 双词表 Owner 裁定 | P1 | R2SIX 与 composer 两表并一真源（净 -1 表） | 漂移守卫改三方断言全绿；重算清单有口径版本戳 |
| L01-C05 | **六段全史 CSV 0033 批落地**：six_phase_history_v1.{csv,meta.yaml}（1,816 日/1,054 路由）+auto_mount 双写缺陷修复随车（LEDGER 任务①已建成 76 测绿）；落地前置=add_module_translation+creation_token（LEDGER 落地态说明） | P1 | 物化件沿用 HEAD 法定 resolve_six_phase，零新映射 | 0033 批落地回执+1,816 日可查 |
| L01-C06 | **alt_regime_signal 消费端接线**：regime_data_loader.load_alt_regime_signals（零调用）接入 index_regime_panel/risk_signal_builder 消费链（F4/F8/F10-F12/F14/F15/F23/F25 维度，alt_data_consumption_plan）；F23 毕业前禁进决策硬链（INVARIANT） | P1 | 接线走既有 loader，禁第二读取面 | grep 消费调用≥1+降级路径测试 |
| L01-C07 | **A16 两套节流档表统一**（Owner 门位）：detector CONFIDENCE_BANDS vs allocator CONFIDENCE_THRESHOLDS 数值方向均异；confidence_band_divergence() 对账探针已备，选型后 import 别名同源（detector :208-218 预留机械准备） | P1 | 统一后一表为真源（净 -1 表）；别名共享同 tuple 防第二真源 | identical_tables=True；对账测试钉住 |
| L01-C08 | **confidence_signal/risk_signal 分量列回填**：print_regime_history.py:179-181 现恒 NULL（自注"P0-002 需要时扩展 builder"）；回填后 R-K9 误报率分母剔除（degraded_legs 联动）可执行 | P2 | builder 扩展打印面，零新表 | 新印 run 分量列非空占比 100% |
| L01-C09 | **run_id 钉死消费面盘点**：owner_band_t/owner_regime_switcher PINNED_RUN_ID 单 run 读法在 append-only 多 run 台账下视图停更（owner_band_t 属冻结考试口径=有意设计；生产切换前须登记供给退化面+切换 run_id 的门位动作单） | P2 | 登记面零新机制 | 盘点表入库+门位动作单 Owner 签 |
| L01-C10 | **次级模块农场内收审计申报**：MOD-REGIME-006/008/011/012/013/014/015+index_market_brief 零/弱外部消费件按宪法 §4.2 判据（零触发零消费→退役）报季度合并审计；chip_distribution 已打回 trial（#257④）同批复核 | P3 | 内收即目的 | 申报清单入季度审计窗 |

既有账本沿用（不另编号）：D2/D3/D4/D5/D7/D33（demand ledger）；D29/LK-16（09 号文）；附录 C 步 1-6；A16（detector 在册裁定号）；#257④（chip trial）。

**前 3 优先**：L01-C01（schema 缺符号=活体导入断裂，P0）→ L01-C03（行数/日数口径+双写污染，P0，影响"3,629 日全史"这一环节 1 核心口径）→ L01-C02（D29 文档销口，P0 顺手项）。

---

## 13 · 缺口债编号登记（引账本）

| 编号 | 内容 | 证据 |
|---|---|---|
| LK-L01-1 | regime_snapshot_history 行数/日数混计：01/12 号文"3,629 日"实为行数（每日恰双写，唯一日≈1,818；09-22 实测 3,627 行/1,817 日） | LEDGER.md §1 补充实测；owner_regime_switcher/data_loader.py:102；01_goal:24；12_census:105 |
| LK-L01-2 | anchored schema 缺 SQL_LATEST_ANCHORED_STATE 符号=allocation_inputs 活体不可导入（附录 C 步 6 未落） | 本簿活体 import 测试 IMPORT FAIL；allocation_inputs.py:620-622 vs backtest_regime_state_anchored.py（59 行全文无此符号） |
| LK-L01-3 | battle_map_09 风控域"市场状态"消费无 regime 实供件代码边/登记回指（crisis_gate/anchored cap 未回指入图） | battle_map_09_risk_control.md:333/:341/:1799/:1806 vs crisis_gate.py 头注 |

---

## 14 · 标准件§（全网搜；全部带出处/许可证；已有件注明沿用）

### 14.1 regime switching HMM（沿用件在册，不自造）
- **hmmlearn 0.3.3（在用，S1 基座）**：GaussianHMM+n_init 多解+walk-forward 季度重拟合+组件锚定（裁定#304）。许可：本机 dist-info METADATA `License :: OSI Approved :: BSD License`（hmmlearn-0.3.3.dist-info/METADATA 实测）。
- walk-forward 滚动重训为行业通行做法：[QuantifiedStrategies: HMM Market Regimes](https://www.quantifiedstrategies.com)、[QuantStart: Market Regime Detection with HMMs](https://www.quantstart.com)（regime 作风险滤网而非独立信号——与本仓"态层职责=风险分档"裁定同构）、[QuantConnect 2024-09 intraday 3-component HMM](https://www.quantconnect.com)。
- 最新论文：[Multi-model ensemble-HMM voting framework（AIMS, 2025-10）](https://www.aimspress.com)（集成投票治单 HMM 不稳——可作 S1 n_init 之外的二期增强候选）；[Cross-Asset Market Regime Detection Using Gaussian HMM（SSRN, 2026）](https://papers.ssrn.com)（walk-forward OOS + 动态适配定位）；[Wang 2020: Regime-Switching Factor Investing with HMM（MDPI）](https://www.mdpi.com)（经典引用件）。
- label switching 对表：本仓锚定重排（按训练窗均值排序占槽）即社区标准做法，实现无需外引；备选 statsmodels [MarkovRegression / Hamilton(1989) filter + Kim(1994) smoother](https://www.statsmodels.org)（MS-ARIMA 族，BSD-3——如需态依赖自回归动力学时的换轨候选，非现役）。

### 14.2 变点检测（CUSUM/BOCPD——overlay S1/S2 转换的在线化增强候选）
- 经典：CUSUM=Page 1954（Biometrika）；BOCPD=Adams & MacKay 2007 [arXiv:0710.3742](https://arxiv.org)（run-length 后验在线推断）。
- 可复用实现：[gwgundersen/bocd](https://github.com/gwgundersen/bocd)（**MIT**，正态模型参考实现）；[y-bar/bocd（PyPI）](https://pypi.org/project/bocd)（MIT 系衍生）；[deepcharles/ruptures](https://github.com/deepcharles/ruptures)（**BSD-2-Clause**，离线变点全家桶，论文 [arXiv:1801.00826](https://arxiv.org)）；[PrincetonLIPS/mf-bocd](https://github.com/PrincetonLIPS/mf-bocd)（multi-fidelity 扩展）。
- 实务评测：[BOCPD for Financial Time Series（ACM 2026-04）](https://dl.acm.org)、[sesen.ai BOCPD 实战（阈值选取与 CUSUM 对比）](https://sesen.ai)。
- 本仓对接位：S1/S2 危机/复苏转换现=阈值评分制（TRANSITION_CONFIG），BOCPD 可作 p_r10 预兆（warning 档）在线变点补强；CUSUM 可作 vol_pct 结构断点监测（S6 锚定阈值 0.30/0.60/0.80 稳健性巡检）。均属候选增强，现役机制不替换（净零：接入前须声明替代/合并面）。

### 14.3 在线推断与校准（沿用件在册）
- 在线滤波：HMM forward/后验取末步因果推断（regime_detector.py:896-897）——与标准 filtered inference 一致，沿用。
- 校准：温度缩放/IS-BCE（validation/phase2/confidence_calibrator.py，788 行 design；Guo et al. 2017 已在 detector docstring :600-611 引用并如实注明 tempering 与严格 TS 的差异）；CRPS（validation/b2_crps.py）。完善概率预测评分对表=17 号文 §一（Harvey-Liu haircut+DSR+PBO/CSCV 三件套，18 号文 §二）。

### 14.4 检索声明
以上为 2026-09-25 WebSearch 实检结果（两轮主题检索+两轮许可定向检索）；SSRN/ACM 条目为检索摘要引述，未下载全文核对——施工引用前按 18 号文纪律全文对表。

---

## 15 · 挖掘执行日志（mining_sop §7 纪律）

| 批 | 矿脉 | 证据源 | 深度 |
|---|---|---|---|
| B1 | 标准件：links/README+09 号文环节 1 | 两件全文 | A |
| B2 | regime 包全读：core 2 件+顶层 11 件+features 12 件+validation 16 件 | 全部头注/INVARIANTS/接口签名；core/regime_detector/anchored_state_machine/print_regime_history 全文逐行 | A/B |
| B3 | 产槽链：pipeline_events（刷新闸全段）/fw_backtest（ensure/freshness/load_regime_series）/tasks.yaml（anchored_state_build:647-659、alt_regime_signal_refresh:2783-2793、hk 退役:209）/schedule 同源核 | A |
| B4 | 六段链四位点+appendix_C 全文+LEDGER 六段链/双写实测+T0_SCHEME_MATRIX 六段行 | A |
| B5 | 消费面 13 点：pf_alloc 三件/daily_gate_snapshot/orchestrator S2 腿/daily_plan/master_switch/owner_band_t/owner_regime_switcher/fw_backtest/screen_source/sector_state_pipeline/warroom（grep 面）/battle_map_09（:333/:341/:1799/:1806） | A/B |
| B6 | 战役文：01:24/:26/:34、12:105-106/:123、17（全册无 L01 专项判据——GPU/做T/数据面判据不在本环节）、02 §三:21-24 | A |
| B7 | 活体验证：SQL_LATEST_ANCHORED_STATE import 实测 FAIL；hmmlearn 许可 METADATA 实测；git status（orchestrator M 态）只读核 | 实测 |
| B8 | 全网标准件：HMM/变点/在线推断 4 轮检索 | §14 |

**三扫收敛声明**：B1-B8 后 10 子块×六向每格均有路径行号出处或 MINING 明示；未读指针全部列名（S2/S4/S10 三块）。
**封矿声明**：本簿为环节导航+施工输入件，节点号/缺口真源仍归各册（D 系=demand ledger、LK=09 号文、LK-L01-*=本簿新登待治理班收编）；禁作为新增节点号出处。
