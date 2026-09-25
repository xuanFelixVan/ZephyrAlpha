---
ttl: task_bound
title: L01-S12 子模块挖矿簿 · 次级模型农场与 TDM 传感器阵列对表（SKEL 十子块之外新矿脉）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（本册为 SKEL 子块树之外的净增矿脉）
---

# L01 · S12 次级模型农场 + TDM 传感器阵列对表

**① 职责一句话**：收容 SKEL 十子块树未覆盖的 regime 包顶层六件模型/面板模块，并把 TDM-E-L1 的 8 个节点逐一回指到真实代码件（图-码一致性）。

**② 现状实测（A）· 六件顶层模块，行数与全仓被引计数（排除自身与 `regime/__init__.py`）本册实测**

| 件 | 行数 | MATURITY（头注实测） | 被引 | 关键 INVARIANT |
|---|---|---|---|---|
| `index_regime_panel.py` | 783 | testing | 4（含 `frontend/dashboard/components/warroom.py`、`alt_data/alt_regime_signals.py`） | 只出概率分布与强弱排序，**严禁点位/方向预测**（90 号 §7 铁律：点预测 52-53% 天花板 + T+1 兑现悖论）；4 套配置非 4 套模型 |
| `institutional_regime_scorer.py` | 588 | production | 4 | — |
| `style_regime_model.py` | 295 | production | 5（含 `signal_ashare/strategy_signal/strategy_matrix_3d.py`） | 风格态词表闭合四类；hmm_runner 未注入→降级规则分档；切换确认连续 N 期防抖 |
| `market_forecast_fusion.py` | 313 | production | 2（含 `signal_ashare/core/sector_strength_aggregator.py`） | 融合分布 Σ=1；只出概率不出点位；写库委托 log_sink |
| `regime_cycle_analyzer.py` | 518 | design | 2（被 style_regime_model 引） | 统计不显著→confidence=0 且 direction=neutral，**下游禁消费** |
| `index_market_brief.py` | 235 | design | 2 | — |

测试面：六件全部有 `tests/regime/test_<件名>.py`（实测在册）→ **测试覆盖 ≠ 生产消费**，本册给出被引计数以区分。

**③ 现状实测（B）· TDM L1 八节点 → 代码件对表（`config/trading_decision_map.yaml` module_ref/module_id 逐条实测）**

| TDM 节点 | module_ref | module_id | 行数/态 | yaml 行 |
|---|---|---|---|---|
| TDM-E-L1 大盘总闸 | `regime/core/regime_detector.py` | MOD-REGIME-001 | 1,163 / production | :298 |
| L1-S1 大盘指数传感器 | `regime/features/index_sensor.py` | MOD-REGIME-016 | 135 / design，**仓内零被引** | :333 |
| L1-S2 市场内部结构传感器 | `signal_ashare/limit_up/limit_up_followthrough.py` | MOD-SIG-078 | 399 / testing | :359 |
| L1-S3 赚钱效应传感器 | `signal_ashare/limit_up/lhb_premium_analyzer.py` | MOD-SIG-057 | 460 / testing | :383 |
| L1-S4 波动率传感器 | `regime/features/synthetic_vix.py` | MOD-REGIME-002 | 228 / production | :414 |
| L1-S0 宏观环境传感器 | `alt_data/policy_expectation_analyzer.py` | MOD-ALT-010 | 在册 | :454 |
| L1-S0-1 新闻情绪语义分析 | `intelligence/news_sentiment_analyzer.py` | MOD-INT-AISA | 在册 | :480 |
| L1-S5 日级市场条件传感器 | `signal_ashare/core/daily_condition_sensor.py` | MOD-SIG-135 | 320 / testing | :504 |
| L1-AGG 市场状态判定 | `regime/core/anchored_state_machine.py` | MOD-REGIME-001 | 204 / design | :538 |

**发现（净增，SKEL 与 09 号文均未记）**：① L1-AGG 的 module_ref 指向**锚定态机**而非 HMM 融合器，与"AGG=市场状态判定"语义存在错位（AGG 应指七态融合出口，实际出口在 regime_detector `_merge_probabilities`）；② L1 与 L1-AGG 共用 module_id=MOD-REGIME-001（同 id 双节点）；③ S2/S3/S5 三传感器落在 `signal_ashare/` 域（跨域挂点），09 号文"模块在盘、无日循环触发面"的判定对本册实测的 testing 态件仍需逐件确认触发面。

**③→⑥ 六向台账（合并叙述，避免重复）**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：panel 吃 S1/S6 输出；scorer/fusion 吃外盘与板块聚合。外部：已查无（查法：本轮以"institutional regime score"检索，命中均为卖方行情评论，非方法件） |
| ②下游 | 内部：warroom（人工面）+ strategy_matrix_3d（风格轴）+ sector_strength_aggregator（融合腿）实测有边；其余 design 件无边。外部：已查无 |
| ③算法 | 内部：panel=四指数各自 6 特征同模型（同构复用）；style=风格 HMM 二轴。外部：regime 作风险滤网而非点位预测，与仓内 INVARIANT 同构（SKEL §14.1 已引 QuantStart/QuantifiedStrategies，沿用） |
| ④后端 | 内部：六件均缺日循环挂点；regime_cycle_analyzer 与 index_market_brief 为 design 且零生产消费→内收候选。外部：已查无 |
| ⑤前端 | 内部：IDX-02 四指数状态卡（panel CONSUMERS 自注"随前端批落地"=未落）。外部：已查无 |
| ⑥数据字段 | 内部：panel 需四指数完整 6 特征（000905/399006/399106 断供史即风险面）；style 需大小盘/价值成长收益差。质量画像=本册未复测指数级连续性（属 S4 册已知洞），登记不重复挖 |

**④ 缺口清单**：L01-C10（在册：次级模块农场内收审计申报，本册补齐六件被引计数实证）；**L01-S12-G1 TDM 图-码三处错位（AGG 指向/同 id 双节点/跨域挂点）**——册内未见；**L01-S12-G2 六件零日循环挂点但 MATURITY=production 三件**——册内未见。

**⑤ 三态裁定**：G1=**施工 P1**（图-码对齐属 RULE-DEPGRAPH/全景对齐义务，改的是 TDM module_ref 注记而非判据，零风险高价值）；G2=**挂起排期**（终局要"production 即有挂点"的一致性不变量，但解锁=治理班成熟度词表与挂点校验 gate 立项，非本车道权限）；C10=在册申报。

**⑥ 挖矿日志**：R1 内部：六件被引计数 + TDM 九节点 module_ref 抽取→signal（三条图-码错位净新增）；R2 内部：测试面 vs 生产面区分→signal；R3 外部：institutional regime scorer 方法件→noise，归因=**来源贫矿**（卖方评论非方法文）→ 已查无；R4 外部：style regime→noise，归因=同 R3。

**封矿判据**：六件 + 九节点全部实测封口，SKEL 子块树之外的长尾已并入本册 → **子模块封矿**。
