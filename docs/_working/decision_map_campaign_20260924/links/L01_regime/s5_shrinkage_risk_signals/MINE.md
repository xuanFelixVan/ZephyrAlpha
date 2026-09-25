---
ttl: task_bound
title: L01-S5 子模块挖矿簿 · Shrinkage 链（置信×风险双信号与 A16 双档表）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（六向封口）
---

# L01 · S5 Shrinkage 链

**① 职责一句话**：把"概率有多可信"（ConfidenceSignal）与"当前有多危险"（RiskSignal）折成一个 ≤1.0 的仓位/暴露节流系数，并在缺数时 fail-closed 落到地板。

**② 现状实测**

| 项 | 实测 |
|---|---|
| 主件 | `regime_detector.py` 子模块③④⑤（约 :992-1131）；`RISK_SIGNAL_FLOOR=0.30`（:419，缺腿地板，非 1.0）；地板分支实测 :1059/:1063/:1071/:1079/:1091 |
| 档表 | `_CONFIDENCE_BANDS` :195 → `CONFIDENCE_BANDS` :217 → 使用点 :226-229 与 :1019 |
| A16 对账 | `confidence_band_divergence()` :232，输出 detector_bands :261 与 `identical_tables` :263（机械判两表是否同源） |
| 供数件 | `src/zephyr/regime/risk_signal_builder.py` 344 行（MATURITY=production :7；params 系数∈[0.30,1.00]，缺数→1.0 降级 :8）+ `features/risk_features.py` 467 行 11 个系数纯函数：realized_vol_coef:75 / volume_anomaly_coef:112 / price_pattern_coef:149 / space_position_coef:187 / cross_asset_corr_coef:223 / ad_ratio_extreme_coef:261 / siphon_coef:302 /（kdj:341 + detect_top_divergence:365 →）tech_divergence_coef:388 / trend_slope_decay_coef:433 |
| 消费侧 | `src/zephyr/pf_alloc/core/regime_meta_allocator.py`（CONFIDENCE_THRESHOLDS 升序上界表）与 `allocation_inputs.py` 分配链总节流 |
| 落库面 | 快照表 shrinkage 列有值；**confidence_signal / risk_signal 分量列在印教材侧恒 NULL**（print_regime_history.py 自注，见 S6 册） |
| 测试面 | `tests/regime/test_rb_stats_regime_failopen.py`（fail-open 双位钉住）、`test_risk_signal_builder.py`（实测在册） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：max(P)（S1）+ RiskSignalInputs 13 参（11 系数 + #11/#13 机会腿），主腿 #1=realized_vol（2026-08-06 二次调优门控在案）。外部：概率可信度→暴露缩放的外部实证=波动率管理族（Volatility-Managed Portfolios，期刊镜像 2024-12 https://economy.alljournals.cn/view_abstract.aspx?aid=C0AA8CB0927F7510A298847FF5ED4F80 ；波动率目标综述，腾讯财经 2025-09-19 https://new.qq.com/rain/a/20250919A04Z9100 ）——两源跨验：本仓"风险信号节流"与该族同构，**但外部族是 vol-targeting，本仓是 conf×risk 双轴**，差异如实记（不构成立即改算法的理由） |
| ②下游 | 内部：pf_alloc 分配链 + 整装回测 RSC-2 引擎边界节流（framework_composer 头注 INVARIANTS：α 乘当日 Shrinkage、剩余质量落现金禁再归一化，裁定编号 270，ruling_registry 已登记）+ 锚定 cap 分家后"仓位数字仍归 L1 总闸"。外部：已查无（消费方=本仓自有系统） |
| ③算法 | 内部：稀有态折扣 + clamp 区间 [0.30,1.00]。外部：概率校准（温度缩放）在 `validation/phase2/confidence_calibrator.py`（788 行，MATURITY=**design**，实测）——校准器已写但未进生产链 = 算法在盘、链路断 |
| ④后端 | 内部：A16 双档表未统一（detector 降序下界 vs allocator 升序上界，数值/方向皆异），对账探针已备而选型未做；分量列 NULL 使 R-K9 误报率分母无法剔分量。外部：已查无（工程债类无外部件） |
| ⑤前端 | 内部：仪表盘无 shrinkage/双信号独立卡面（只随快照 JSON）。外部：已查无（查法：呈现面在 S10 面板册统一挖） |
| ⑥数据字段 | 内部：需 vol_pct/hurst/slope/ad_ratio/HHI/资金集中度等 13 参，全部由 S4 供；`siphon_coef` 依赖板块 HHI（同 S2 短史约束）。质量画像=见 S4 册探针（limit_up_down 49 日） |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| A16（既有在册号） | detector 与 allocator 两套置信档表未统一 | detector :208-218 在册 |
| D5 | 宏观四组参数部分缺口（RiskSignal 系数供数不全） | 需求册沿用 |
| L01-S5-G1 | confidence_calibrator（788 行 design）与生产 Shrinkage 链断开，校准结果从未回灌档表 | 册内未见 |
| L01-S5-G2 | 4 态降维后档表阈值仍沿用 9 态校准值（与 S1 册 G1 同案，此处为处置主场） | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| A16 | 施工（P1，Owner 选型门位） | 两表并存=每次分配结果依赖"哪条路读到哪张表"，终局不可自动审计；探针已备，选型后即 import 别名同源（净 -1 表） |
| D5 | 挂起排期 | 宏观两融已供、其余三组解锁=外部数据源账号 |
| L01-S5-G1 | 挂起排期 | 终局要"校准闭环自动化"，但解锁条件=快照表有足量分量列真值（G2/先决 L01-C08 分量列回填）；现在接=空跑 |
| L01-S5-G2 | 施工（P2，随档表统一批） | 阈值与态数不匹配属系统性偏差，无人复核即长期错 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：档表/地板/对账探针行号 + 11 系数函数清单 | signal | — |
| R2 | 内部：confidence_calibrator MATURITY 实测 | signal（design 态实证，SKEL 仅"未接线"散文） | — |
| R3 | 外部：vol-targeting 双源 | signal | — |
| R4 | 外部：confidence→position sizing 机构件 | noise | 归因=**来源贫矿**（命中多为通用仓位管理文，与"概率可信度折系数"语义不贴合）→ 已查无 |

**本册封矿判据**：六向封口；未挖长尾无（校准器接线属施工项）→ **子模块封矿**。
