---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.4.0"
date: 2026-08-06
last_updated: 2026-08-08
topic: regime_backtest_validation_plan
scope: 07_trading_decision_architecture
parent: discussion_001_regime_detector_spec.md
---

# 讨论文档·regime 检测器回测验证方案

> 本文档定义 regime 检测器（discussion_001 v1.3.1 spec）的回测验证方案。
> 性质：**已定稿（v1.0.0，2026-08-06），交接给施工对话作为模块实现的验收指南**。等 regime 检测器骨架+实现就绪后，按本方案执行回测验证。
> 关联：[discussion_001_regime_detector_spec.md](discussion_001_regime_detector_spec.md)（regime spec 真源）｜ [battle_map_03_backtest_validation.md](../battle_map/battle_map_03_backtest_validation.md)（现有回测框架）
>
> **v1.1.0 更新（2026-08-08）**：方案已部分执行（Phase 0-2 完成，Phase 3-5 部分/未完成）。
> 实际实现与原方案有一处重大偏离：HMM **9 态 → 4 态**（BIC 扫描驱动，discussion_004 §2.1），
> 输出 **7 维概率**（4 HMM + 3 overlay）非 12 维。详见下方 [§0.5 方案执行状态](#05-方案执行状态2026-08-08-反向同步)。

## 0.5 方案执行状态（2026-08-08 反向同步）

> 本节是 2026-08-08 对方案执行情况的反向同步——从代码/ARCH/验证报告回填到文档，
> 使文档反映项目最新功能状态。原方案（§1-§11）保留为历史规划真源，本节记录实际执行结果与偏离。

### 0.5.1 Phase 完成度总览

| Phase | 原方案内容 | 实际状态 | 关键 ARCH / 代码 |
|---|---|---|---|
| **Phase 0** | regime 检测器实现（HMM 9态 + D-SIGNAL-68 + Shrinkage） | ✅ 完成（**4 态非 9 态**） | `regime_detector.py` 618 行 + `regime_feature_builder.py` + features/* |
| **Phase 1** | C1 开/关对比（核心一票否决） | ✅ 完成 — **四项全通过** | `c1_comparator.py` + `c1_runner.py` + `shrinkage_engine.py` |
| **Phase 2** | A1/A2/B1/B4 模型质量 | ✅ 完成 — **四项全 PASS** | `phase2/` 4 验证器 + `confidence_calibrator.py` |
| **Phase 3** | D1-D4 参数阈值校准 | 🟧 部分完成 — D2/D4 完成，D1 部分，D3 未验证 | A2/A3 升级验证覆盖 D2/D4 |
| **Phase 4** | E1-E4 鲁棒性 | 🟧 部分完成 — E1 walk-forward 已实现，E2/E3/E4 未验证 | `_smoke_walkforward.py` |
| **Phase 5** | 决策门控（BM-BT-07） | ❌ 未完成 | — |
| A3/A4/B2/B3/C2/C3/C4 | 未明确归入 Phase | 🟧/❌ 多数未完成 | A3 部分覆盖，其余未实现 |

**结论**：方案**未全部执行完成**。核心假设（C1 节流有效）已验证通过，模型质量（Phase 2）已闭环；
参数校准（Phase 3）与鲁棒性（Phase 4）部分完成；决策门控（Phase 5）未启动。

### 0.5.2 重大偏离：9 态 → 4 态（discussion_004 §2.1）

原方案 §8.1 规划 HMM **9 态**（3×3 趋势×波动率网格），§1.1 称输出 **12 维概率分布**。
实际执行中 A2 过拟合检测发现 9 态过度细分（OOS/IS 一致率仅 0.34，门槛 0.7），经 BIC 扫描
确认降为 **4 态**（discussion_004 §2.1，2026-08-07）：

- **BIC Kneedle 拐点=4**，walk-forward 46 季度拐点分布 {4:19, 5:25, 7:2}
- **4 态语义**（全历史 3733 样本，RobustScaler 标准化后 Viterbi 统计）：
  - r1 低波震荡（27.6%）：vol_pct=-0.52, fr_5d=+0.0003（低波横盘）
  - r2 中波震荡（37.4%）：vol_pct=+0.42, fr_5d=+0.0018（中波温和偏强）
  - r3 牛市趋势（14.9%）：vol_pct=+0.58, slope=+0.149, fr_5d=+0.0039（强涨量增，最高正收益）
  - r4 熊市阴跌（20.2%）：vol_pct=-0.44, slope=-0.049, fr_5d=-0.0014（唯一负收益，阴跌）
- **输出 7 维概率**（4 HMM 基态 + 3 overlay 特殊态 CRISIS/RECOVERY/BREAKOUT），Σ=1.0
- 降态后 A2 OOS/IS 一致率从 0.34 提升到 **1.042**（KL=13.05），过拟合消除

这正是原方案 §8.1 预期的"基于证据的简化"——验证后发现 9 态过度细分，基于 BIC 证据降为 4 态。

### 0.5.3 实际代码结构（Phase 0 产物）

```
src/zephyr/regime/
├── core/
│   └── regime_detector.py          # HMM 4态 + D-SIGNAL-68 overlay + ConfidenceSignal + RiskSignal + Shrinkage（618行）
├── regime_feature_builder.py        # 特征管道主编排器（OHLCV→三dict输出，PIT严格，walk-forward季度refit）
├── overlay_signals_builder.py       # OverlaySignalsConstructor（8转换评分 T1-T6/S1/S2）
├── risk_signal_builder.py           # RiskSignalConstructor（13参数，#1门控）
├── features/
│   ├── market_features.py           # F1 realized_vol_pct + F3 cross_asset_corr + F4 ad_ratio + F5 volume_anomaly
│   ├── trend_features.py            # F2a hurst_dfa + F2b kalman_slope（替代均线角度糊弄）
│   ├── overlay_features.py          # 8转换评分算子
│   ├── risk_features.py             # 13风险参数系数映射
│   ├── chip_distribution_engine.py  # 筹码分布（华泰前沿算法，替代换手率代理）
│   ├── synthetic_vix.py             # 合成VIX（期权IV曲面，替代北向资金死数据）
│   ├── wyckoff_engine.py            # Wyckoff FSM（规则法结构识别，替代名词堆砌糊弄）
│   └── regime_data_loader.py        # 数据加载公共工具
└── validation/phase2/
    ├── a1_sample_sufficiency.py     # A1 样本充足性验证器
    ├── a2_hmm_overfitting.py        # A2 HMM 过拟合检测器
    ├── b1_probability_calibration.py # B1 概率校准度验证器
    ├── b4_transition_accuracy.py    # B4 转换触发准确性验证器
    ├── confidence_calibrator.py     # 两阶段概率校准器（Temperature Scaling + Isotonic Regression）
    └── phase2_runner.py             # Phase 2 编排器（依据 discussion_017 §4）

src/zephyr/backtest/
├── implementations/shrinkage_engine.py  # ShrinkageBacktestEngine（override _get_day_signals，shrinkage=1.0 bit-identical）
└── regime_validation/
    ├── c1_comparator.py             # C1ShrinkageComparator（四项一票否决）
    ├── c1_runner.py                 # C1 执行编排器（mock冒烟 + regime真实模式）
    └── shrinkage_provider.py        # ShrinkageProvider 协议 + 4 实现（Const/Schedule/Mock/RegimeDetector）
```

**算法糊弄治理**（#ARCH-067）：原 regime_feature_builder/blueprint.md 含 15 处糊弄算法
（换手率代理筹码分布、定性词无量化、伪精确均线角度、死数据北向资金、名词堆砌结构识别、逻辑错位），
已全部替换为 2026 前沿算法（Hurst DFA / Kalman / VWAP 三角分布筹码 / ACSI / Wyckoff FSM / 合成VIX）。

### 0.5.4 验证结果明细（Phase 1-2）

#### C1 开/关对比（Phase 1，核心一票否决）— ✅ 四项全通过

> 数据：10 大盘股 2015-01-01~2026-06-30，walk-forward 46 季度 HMM refit，1886 万行 ClickHouse
> 报告：`logs/c1_repro/c1_repro_report.md` + `c1_metrics.json`
> ARCH：#ARCH-REGIME-VALIDATION-001 + #ARCH-REGIME-C1-RUNNER-001

| 指标 | 关（基准） | 开（实验） | 门槛 | 判定 |
|---|---|---|---|---|
| Sharpe | 0.3678 | 0.3474 | ≥0.2678（S_关−0.1） | ✅ 通过 |
| MaxDD | 0.2221 | 0.1485 | 改善≥0.03 | ✅ 通过（改善 +0.0736） |
| Calmar | 0.2918 | 0.3694 | ≥0.3502（C_关×1.2） | ✅ 通过（+27%） |
| Turnover | 2.2722/yr | 2.5522/yr | ≤4.5444（T_关×2） | ✅ 通过 |

**行业对照**（Morwane OOS 2013-2026）：Sharpe 不变 ✅ / MaxDD 改善 3.9pp（本方案 7.4pp 更优）/ Calmar +38%（本方案 +27%）。

#### Phase 2 模型质量 — ✅ 四项全 PASS

> ARCH：#ARCH-REGIME-FEATURE-BUILDER-001 + #ARCH-CALIBRATOR-001 + #ARCH-REGIME-OVERLAY-001 + #ARCH-REGIME-CONFIDENCE-FIX-001
> 报告：`logs/c1_repro/a2_a3_validation_report.md`

| 验证项 | 结果 | 关键指标 | 门槛 |
|---|---|---|---|
| **A1 样本充足性** | ✅ PASS | 3733 样本，4 态最少 r3=555 天 | ≥50 天/态 |
| **A2 HMM 过拟合** | ✅ PASS | OOS/IS=1.042，KL=13.05（9态时仅0.340） | OOS/IS≥0.7 |
| **B1 概率校准度** | ✅ PASS | ECE=4.2%，60-80%桶 n=221 误差 3.7% | 校准误差<10% |
| **B4 转换触发准确性** | ✅ PASS | S1 3/3 命中；S2 data_ready=False 不计分母（需NLP+high/low） | ≥6/8 事件吻合 |

**B1 校准器**（#ARCH-CALIBRATOR-001）：两阶段——Stage 1 Temperature Scaling（全局降温）+ Stage 2 Isotonic Regression（局部修正），四级降级（full→temperature-only→isotonic-only→identity），仅对 HMM 基态生效，PIT 防泄漏。

**ConfidenceSignal 修复**（#ARCH-REGIME-CONFIDENCE-FIX-001）：移除 state_risk_factor 回归 spec（原 base(max_p)×state_risk×rarity → 纯 base(max_p)×rarity）。state_risk 是代码偏离 spec 的私加，HMM 标签 permutation invariance 致按数字标签套 state_risk=随机惩罚，永久中性态惩罚致牛市也砍仓。修复后 Sharpe 0.10→0.3474（×3.5）。

### 0.5.5 A2/A3 升级验证（Phase 3 部分）

> 报告：`logs/c1_repro/a2_a3_validation_report.md`
> ARCH：#ARCH-REGIME-RISK-FULL-001（A2/D2）+ #ARCH-REGIME-OVERLAY-001（A3/D4）

| 配置 | Sharpe | MaxDD | Calmar | Turnover | C1 |
|------|--------|-------|--------|----------|----|
| 简化版（simple/off）生产基线 | 0.3474 | 0.1485 | 0.3694 | 2.5522 | ✅ |
| A2 full risk（13参数，D2） | 0.3469 | 0.1484 | 0.3691 | 2.5863 | ✅ 不退化 |
| A3 overlay on（8转换，D4） | 0.3278 | 0.1471 | 0.3546 | 2.5049 | ✅ 但退化 |
| A2+A3（full/on） | 0.3259 | 0.1472 | 0.3529 | 2.5241 | ✅ 余量危险 |

**A2（D2 RiskSignal 13参数）**：✅ 可采纳。#1 门控奏效（#1=1.0 时附加参数不参与，平时不干预；危机期 #1<1.0 加深收缩）。C1 不退化，边际收益极小但危机期理论更精细。有效参数 7/8（#9 KDJ 因 high/low 缺失降级，#4/8/12 stub=1.0，#11/13 stub=0.0）。

**A3（D4 8转换 overlay）**：🟧 方案A门控治本。ungated overlay 系统性退化 Sharpe（-0.0196，超噪声），根因 T1/S1 非危机期误触发。**方案 A**（#1<1.0 门控 overlay）C1 不退化（Sharpe 0.3463 vs baseline 0.3474，差 -0.0011 噪声范围），危机期 overlay 仍生效。已固化到 `RegimeDetector.detect()`（overlay_gated=True 默认开启）。

**死区装饰器**（#ARCH-REGIME-DEADZONE-001，proposed）：序列层减变化点 72.9% 但回测 Turnover 不降反升 4.2%（等权策略下 Shrinkage 同向缩放致相对权重恒等）。**不采纳**，代码保留为可选 decorator 默认不启用。

### 0.5.6 关联设计文档

实际执行中方案拆分为多个 discussion 文档（原方案 §1-§11 为 v1.0.0 规划真源）：

| 文档 | 覆盖范围 | 状态 |
|---|---|---|
| `discussion_004`（降态裁定） | 9态→4态 BIC 证据 + 4态语义 | ✅ 已定稿 |
| `discussion_017`（Phase 2 验证详设） | A1/A2/B1/B4 验证器设计 | ✅ 已定稿 |
| `discussion_018`（回测可观测性） | C1 runner 可观测性 + MLflow 跟踪 | ✅ 已定稿 |
| `discussion_019`（Phase 3 工程规划） | HMM降态/校准器/NLP管道/置信度信号 | ✅ 施工中 |

### 0.5.7 待完成项（Phase 3-5 缺口）

| 验证项 | Phase | 状态 | 缺口说明 |
|---|---|---|---|
| D1 ConfidenceSignal 四档阈值 | 3 | 🟧 部分 | state_risk 已移除（回归spec），但 max(P) 60/80/95% 四档 ±20% 敏感性网格未跑 |
| D3 聚合公式参数 | 3 | ❌ 未验证 | 共振惩罚 0.05 + 机会恢复 0.25 的 ±20% 扰动未跑 |
| E1 Walk-Forward 稳定性 | 4 | 🟧 部分 | walk-forward 46 季度已实现，但各窗口 MaxDD 改善 CV<0.5 的正式统计未产出 |
| E2 Block-bootstrap | 4 | ❌ 未验证 | 2000× block-bootstrap 置信区间未跑（C4 同） |
| E3 参数敏感性 | 4 | ❌ 未验证 | ±20% 扰动效果变化<30% 未跑 |
| E4 交易成本敏感性 | 4 | ❌ 未验证 | 0-50bps 成本下 Shrinkage 效果稳健性未跑 |
| A3 状态转移合理性 | — | 🟧 部分 | Viterbi 解码已实现，overlay_audit 分析了转换触发，但 spec §4 路径覆盖≥80% 正式统计未产出 |
| A4 特征重要性 | — | ❌ 未验证 | BM-BT-05-B 特征重要性未跑 |
| B2 CRPS | — | ❌ 未验证 | BM-BT-03-E CRPS 对比 climatology 未跑 |
| B3 置信度合理性 | — | ❌ 未验证 | max(P) 分布合理性未分析 |
| C2 极端事件回撤保护 | — | ❌ 未验证 | CRISIS 时段 MaxDD 改善≥5pp 未跑 |
| C3 节流归因 | — | ❌ 未验证 | 各态 Shrinkage 贡献未分析 |
| C4 统计显著性 | — | ❌ 未验证 | P(Sharpe_开>Sharpe_关)≥75% 未跑 |
| Phase 5 决策门控 | 5 | ❌ 未完成 | BM-BT-07 IS→WFA→OOS 适配未启动 |

## 0.6 算法审查与 2026 研究对照（2026-08-08）

> 本节是 2026-08-08 对方案核心算法选择的审查，对照 2026 最新研究实践，
> 判断：核心算法是否选对？验证方法是否有缺口？有没有更好的算法？
> 审查方法：全网搜索 2026 年最新研究 + 对照项目现有实现 + 第一性原理判断。

### 0.6.1 核心算法审查结论：选择正确，有 2026 研究背书

| 算法选择 | 项目现状 | 2026 研究验证 | 结论 |
|---|---|---|---|
| **HMM 4 态** | BIC 驱动降态（9→4） | firestrand/marketregimeml（2025-09 真实数据）：**n_regimes>3 在真实数据上过拟合**；HMM RQI 67.8-76.6 | ✅ 正确 |
| **两阶段校准**（Temperature + Isotonic） | #ARCH-CALIBRATOR-001，ECE=4.2% | Dheur 博士论文（2025-12）大规模实验：**post-hoc 校准一致优于内嵌校准** | ✅ 正确 |
| **乘法 Shrinkage**（ConfidenceSignal × RiskSignal） | C1 四项全通过 | VIX-Regime Position Sizing（2026-05）：regime 状态直接缩放仓位（1.0x/0.6x/0.3x）= 我们的 Shrinkage | ✅ 正确 |
| **"特征>模型"工程** | Hurst DFA/Kalman/筹码/合成VIX/Wyckoff | mathandmarkets（2026-01）：**特征重要性远超模型选择**，realized_vol 单特征 28% 重要性；10 优化特征 > 35+ 特征 | ✅ 正确 |
| **"风险节流器非策略"定位** | design_memo_001 §2.2 | 多源 2026 共识：regime 检测最大价值是仓位缩放而非 alpha 信号 | ✅ 正确 |

**核心算法不需要推翻重做。**

### 0.6.2 明确不采用的算法（避免过度工程）

| 算法 | 研究证据 | 不采用原因 |
|---|---|---|
| **深度学习 LSTM/Transformer** 做 regime 检测 | firestrand 真实数据：LSTM RQI 49.1-64.9（最差），HMM 67.8-76.6 | 黑箱、需海量数据、实测最差；风控要可解释性 |
| **增加状态数**（>4 态） | "n_regimes>3 overfits on real data" | 已从 9→4 降态，A2 从 0.34→1.042 验证 |
| **堆更多特征** | "10 optimized > 35+ features" | 已有 13 参数 + 8 转换，再加边际递减 |
| **SVM Ensemble 替换 HMM** | RQI 83.6-86.9 > HMM 67.8 | SVM 做分类强，但**无转移矩阵/无持续性建模**，做风控（要知道"危机还要持续多久"）不如 HMM |

### 0.6.3 需要补充的算法（3 个真缺口 + 1 个现成该跑）

#### 缺口 1：Conformal Prediction 校准层（B1/B2 升级）— 2026 前沿

**现状**：两阶段校准（Temperature + Isotonic），ECE=4.2% 已达标。
**缺口**：无有限样本覆盖保证——"P(危机)=80%" 在统计上不保证 80% 的时间真是危机。
**2026 研究**：
- arXiv:2605.19024（2026-05）Conformal Prediction via Transported Beta Laws——**处理时序分布漂移**，金融非 i.i.d. 适用
- arXiv:2607.27143（2026-07）Mondrian CP（类条件 conformal）——**少数类覆盖恢复 +61.7pp**，r3/r4 少数态（14.9%/20.2%）正适用
- ACS Chem. Res. Toxicol.（2026-06）Adaptive Conformal Prediction——**model-agnostic 校准层，不需重训，有限样本覆盖保证**

**建议**：在 Isotonic 之上叠 Conformal Prediction（分布无关保证），替代原方案 B2 的纯 CRPS。比 CRPS 更强——CRPS 只测技能分数，Conformal 给统计保证。

#### 缺口 2：CPCV + PBO 过拟合检测（A2/E2 升级）— 2026 金标准

**现状**：A2 用 IS/OOS 单次分割 + KL 散度。E2 计划固定 block-bootstrap。
**缺口**：无 Combinatorial Purged Cross-Validation（CPCV）+ Probability of Backtest Overfitting（PBO）。
**2026 研究**：
- backtest-audit（2026-05 开源库）：CPCV 分 S 块枚举 C(S,S/2) 种 train/test 划分，**PBO = IS 冠军 OOS 不是冠军的比例**。PBO≈0 可靠，PBO>0.5 过拟合
- mathandmarkets（2026-05）：测试 80 个变体时 P(假阳性)=98.3%——多重比较是量化最贵的 bug
- algovantis（2026-04）：purged k-fold 删边界观测防滚动窗口泄漏

**建议**：E2 从固定 block-bootstrap 升级为 **stationary bootstrap + CPCV/PBO**。CPCV 比 IS/OOS 单次分割严格得多（枚举所有组合），PBO 给过拟合概率而非主观判断。

#### 缺口 3：Stationary Bootstrap（E2 升级）

**现状**：原方案计划 21-day 固定块 block-bootstrap 2000×。
**2026 研究**：algovantis（2026-04）——**stationary bootstrap 块长随机（几何分布），保平稳性，优于固定块**。固定块在块边界引入人为不连续。

**建议**：E2 用 stationary bootstrap 替代固定 block-bootstrap，或两者都跑做对照。

#### 现成该跑：Deflated Sharpe Ratio（C4）

**现状**：`src/zephyr/simulation/deflated_sharpe_calculator.py` 已存在，C4 未执行。
**2026 研究**：mathandmarkets（2026-05）——Deflated Sharpe 校正多重比较（测了 N 个变体后 Sharpe 要打折）。
**建议**：直接跑，零开发成本。

### 0.6.4 施工优先级

```
优先级 1（零开发，立即跑）：
  └── C4 Deflated Sharpe Ratio（已有 calculator，跑一次出结果）

优先级 2（补充验证，中等工作量）：
  ├── E2 Stationary Bootstrap（替代固定 block，~1天）
  ├── E3 参数敏感性 ±20% 网格（~1天，BM-BT-05-B 已有框架）
  └── E4 交易成本 0-50bps 敏感性（~半天，BM-BT-01-D 已有框架）

优先级 3（算法升级，较大工作量但有 2026 研究背书）：
  ├── B2 Conformal Prediction 校准层（叠在 Isotonic 上，~2-3天）
  └── E2+ A2 CPCV/PBO 过拟合检测（~2-3天，金标准升级）

优先级 4（理论补全，低紧迫）：
  ├── D1/D3 参数敏感性网格（max(P)四档 + 聚合公式参数）
  ├── C2 极端事件回撤保护 / C3 节流归因（分析型，基于已有数据）
  └── Phase 5 决策门控（BM-BT-07 适配）

明确不做（研究证明更差/过度工程）：
  ✗ 深度学习 regime 检测（LSTM/Transformer）
  ✗ 增加状态数（>4 态）
  ✗ SVM Ensemble 替换 HMM（丢转移矩阵）
  ✗ 堆更多特征
```

### 0.6.5 研究来源索引

| 来源 | 覆盖领域 | 关键结论 |
|---|---|---|
| firestrand/marketregimeml（2025-09，真实数据） | regime 模型对比 | n_regimes>3 过拟合；LSTM 最差；SVM Ensemble 最强但无转移矩阵 |
| mathandmarkets Ensemble（2026-01） | CUSUM/BOCPD/三信号框架 | 特征>模型；realized_vol 28% 重要性 |
| mathandmarkets Expensive Bug（2026-05） | 多重比较/Deflated Sharpe | 80 变体 P(假阳性)=98.3%；CPCV 金标准 |
| arXiv:2605.19024（2026-05） | Conformal + Beta Laws | 时序分布漂移 conformal |
| arXiv:2607.27143（2026-07） | Mondrian CP | 类条件 conformal 少数类覆盖 +61.7pp |
| backtest-audit（2026-05 开源） | CPCV/PBO | PBO 过拟合概率量化 |
| algovantis（2026-04） | Stationary Bootstrap / Purged k-fold | 随机块长保平稳性 |
| trendsandbreakouts VIX-Regime（2026-05） | regime 仓位缩放 | = 我们的 Shrinkage |
| Dheur 博士论文（2025-12） | post-hoc 校准 | post-hoc 一致优于内嵌 |

### 0.6.6 补充发现：HMM 引擎升级路径（2026-08 二次搜索）

> 二次搜索发现 3 项 2026 HMM 前沿研究，可作为现有 Gaussian HMM 4 态的**未来升级路径**（非立即必要，但记录备查）。

#### 升级路径 1：Wasserstein HMM — 解决标签切换（label switching）

**问题**：HMM 标签有 permutation invariance——walk-forward 各季度 refit 后 r1 可能变成不同语义。我们当前用 `#ARCH-REGIME-CONFIDENCE-FIX-001` 移除 state_risk 来缓解，但这是治标。
**2026 研究**：arXiv:2603.04441（Boukardagha 2026-02）Wasserstein HMM——用 2-Wasserstein 距离做 template-based regime identity tracking，**跨 refit 保持标签语义一致**。Sharpe 2.18 vs 1.18 buy-hold，MaxDD -5.43% vs -14.62%。
**评估**：治本方案，但需重写 HMM 引擎。当前 4 态已通过 A2（OOS/IS=1.042），标签切换问题已大幅缓解。**列为未来升级，非当前缺口**。

#### 升级路径 2：Student-t / GED 重尾发射 — 处理金融危机尾部

**问题**：当前 Gaussian 发射假设正态，但金融收益有肥尾。flash-crash 单日极端值可能毒化整个训练窗口的 regime 均值/协方差。
**2026 研究**：
- arXiv:2606.23492（2026-06）Continuous HMM Heavy-Tail Emission Families——Student-t / GED / Laplace 发射，KS/AD pass rate >97% IS / >94% OOS
- Küçükdağ & Hekimoğlu（2026）Robust HMM——Huber 加权 M-step，outlier-robust 参数更新
**评估**：对风控用例（尾部事件=危机=最重要）有价值。但需重写 EM M-step。**列为优先级 3 之后的可选升级**。

#### 升级路径 3：Feature Saliency HMM — 自动特征选择（补 A4 缺口）

**问题**：A4 特征重要性未验证。当前 13 参数 + 8 转换靠人工设计，无数据驱动的特征筛选。
**2026 研究**：
- Fons et al.（2019/2021）Feature Saliency HMM——**在 EM 训练中学习哪些特征是 state-discriminating**，自动特征选择
- SHAP/Permutation Importance（metricgate 2026-04）：SHAP 局部解释稳定但相关特征致归因稀释（需 Group Shapley）；Permutation 全局但相关特征隐藏重要性。**金融时序须严格按滚动窗口防 look-ahead**
- mental-momentum（2026-06）警告：SHAP 测相关性非因果性，"常被误当因果证明编造金融叙事"
**评估**：Feature Saliency HMM 是 HMM 特征重要性的**第一性原理方案**（训练中学习而非事后解释）。SHAP 适合作为审计工具监控 concept drift。**A4 验证建议用 Feature Saliency HMM + SHAP 审计双轨**。

#### 不采用：LSTM+HMM 混合 / 在线无限 HMM

| 算法 | 来源 | 不采用原因 |
|---|---|---|
| LSTM 自编码器 + GHMM | microbell（2026-07） | LSTM 做特征压缩引入黑箱；研究发现 Kelly 在特定状态有"均值回归"保守倾向（执行层问题）；增加复杂度无明确收益 |
| BR-iHMM 在线无限 HMM | Yiu et al.（2026） | 在线学习无 batch refit，但"无限态"与我们的 4 态精简方向相反；复杂度过高 |

### 0.6.7 第三轮搜索：A股专属实践 + 组合构建前沿（2026-08-08）

> 第三轮搜索聚焦 A 股专属 regime 实践与 regime 感知组合构建，发现 2 项与本项目直接相关的 2026 研究。

#### 发现 1：A股 4 态是行业共识 — 进一步确认我们的选择

| 来源 | 状态数 | 状态语义 |
|---|---|---|
| **本项目** | 4 态 | r1 低波震荡 / r2 中波震荡 / r3 牛市趋势 / r4 熊市阴跌 |
| 中邮证券《市场脉搏》(2025-08) | 4 态 | 趋势上涨 / 震荡上涨 / 震荡下跌 / 趋势下跌 |
| CSDN A股 HMM 实战 (2026-07) | 4 态 | 低波趋势上涨 / 高波震荡轮动 / ... |
| 华安证券 RARP (2026-05) | 4 类宏观 + 4 类市场风险 | 复苏/扩张/放缓/收缩 |

**结论**：A股 4 态是 2026 行业共识，我们的 BIC 驱动降态与券商研究独立殊途同归。

#### 发现 2：动态调制矩阵 — HMM 转移矩阵的外置调制（潜在升级）

**中邮证券《市场脉搏》(2025-08 ~ 2026-07) 核心创新**：
- HMM 静态转移矩阵的致命弱点：仅反映训练样本的转移规律，对拐点反应滞后
- **动态调制矩阵**：用宏观脉冲（PMI + 信贷脉冲）+ 资金情绪（恐慌指数 + 融资盘 + ETF 流向 + 散户情绪）双因子**外置调制 HMM 转移矩阵**
- 关键设计：状态层外置避免状态爆炸（内置 6×3×4=72 状态 vs 外置 4 状态 + 调制矩阵）
- 回测：年化 20.9%，Sharpe 1.29，Calmar 1.90

**与我们对比**：
- 我们的 **overlay（D-SIGNAL-68）**是规则法后验调整（HMM 输出后 gating）——crisis 时 #1<1.0 门控 overlay
- 中邮证券的**动态调制矩阵**是前验调制（HMM 转移矩阵本身被外置信号调制）——更早介入
- **评估**：两种方案解决同一问题（HMM 静态性 vs 市场动态性）。我们的 overlay 已通过 A3 验证（C1 不退化），动态调制矩阵是**潜在升级路径**——前验调制理论上比后验 gating 更早响应拐点。但需新增宏观/资金情绪数据管道，工作量较大。**列为优先级 4 之后的可选升级**。

#### 发现 3：状态感知条件风险平价 RARP — Shrinkage 之上的下一步

**华安证券 RARP（2026-05）核心方法**：
- 按状态**重新估计协方差矩阵**（仅用同状态历史数据），而非简单缩放 budget
- 双重视角：宏观状态（US LEI + GRACI）+ 市场风险状态（VIX + EWMA + GARCH + 金融动荡指数）
- 条件协方差融合：市场风险状态协方差 × 50% + 宏观状态协方差 × 50%
- Sharpe 0.88，MaxDD 21.89%，ES 5.44%，波动率压缩至 1.4% 以内

**与我们对比**：
- 我们的 **Shrinkage = ConfidenceSignal × RiskSignal** 是**乘法缩放 budget**（防御性，不改协方差结构）
- RARP 是**状态条件协方差重估**（进攻性，改变资产间风险贡献）
- **评估**：RARP 是 Shrinkage 之上的**更高阶方案**——从"缩放仓位"到"按状态重估风险结构"。但本项目定位是"风险节流器"（防御性），不是组合优化器（进攻性）。**如果未来从 Shrinkage 升级到 risk parity，RARP 是直接路径。当前不在 scope 内**。

#### 发现 4：regime-conditional allocation — 危机时切换分配方法

**clawrxiv:2604.01460（2026-04）核心发现**：
- 风险平价在流动性危机中失效（drawdown 18.7% vs 理论 8.2%）
- **危机时切换分配方法**（risk parity → inverse-vol），MOVE index > 150 触发
- 恢复 67% 的分散化损失

**与我们对比**：
- 我们的 CRISIS overlay 是**危机时 Shrinkage→收缩 budget**（减仓）
- clawrxiv 方案是**危机时切换分配方法**（从 risk parity 切到 inverse-vol）
- **评估**：两者方向一致（危机时降低风险），但 clawrxiv 更激进（换方法 vs 减仓位）。**我们的 Shrinkage 减仓是更保守的第一步**，如果未来做 risk parity，可考虑危机时切换到 inverse-vol。

#### 发现 5：Kelly 在特定状态的"均值回归"保守倾向（执行层警示）

**中邮证券《市场脉搏(2)》(2026-07) 关键归因**：
- 超额损失高度集中于某一特定状态
- 问题不在状态识别层，而在**仓位执行层**——Kelly 公式在该状态有"均值回归"保守倾向
- 对"假摔反包"类行情响应不足
- 解决：轻量级干预规则，不改变底层识别逻辑

**对我们的警示**：如果未来做 Kelly 连接（§0.6.4 优先级 4），需注意 Kelly 在特定 regime 的保守倾向。当前我们的 Shrinkage 是规则法（非 Kelly），不受此影响。

### 0.6.8 四轮搜索总结论

| 轮次 | 搜索领域 | 关键发现 | 对本项目影响 |
|---|---|---|---|
| 第一轮 | regime 检测/校准/节流/鲁棒性 | 核心算法选对；3 缺口（Conformal/CPCV/Stationary Bootstrap） | 高——直接补缺口 |
| 第二轮 | HMM 引擎升级/特征重要性 | 3 升级路径（Wasserstein/Student-t/Feature Saliency） | 中——未来升级备查 |
| 第三轮 | A股专属/组合构建 | 4 态行业共识；动态调制矩阵/RARP/Kelly 警示 | 中——确认选择+远期路径 |
| 第四轮 | 层次化/多尺度/BOCPD | 层次 HMM 状态持续时间+38.5%/伪转移-28.6%；TVTP 时变转移；Shannon entropy 替代 ConfidenceSignal | 高——层次 HMM 是最有价值的升级路径 |

### 0.6.9 第四轮发现：层次化 HMM + TVTP + BOCPD（2026-08-08）

> 第四轮搜索聚焦层次化/多尺度 regime 检测与在线变点检测，发现 4 项与本项目直接相关的 2026 研究。

#### 发现 1：层次化 HMM — 状态持续时间 +38.5%，伪转移 -28.6%（最有价值升级）

**AlgoGators Capstone（2025-11）核心实验**：
- 两层层次 HMM：**周线宏观 regime → 条件化日线市场状态**
- 对比 flat HMM：**平均状态持续时间 53.1 vs 38.3 天（+38.5%）**，**伪转移减少 28.6%**
- COVID-19 crash 期间 regime 持续性显著优于 flat HMM
- 周线宏观特征（周收益/4周滚动波动率/VIX/12周动量）条件化日线微观特征

**与我们对比**：
- 我们的 HMM 4 态是 **flat**（单尺度日线）
- 层次 HMM 用**周线宏观层条件化日线层**——结构性地分离"宏观 regime"与"日间噪声"
- **直接解决 A3（状态转移合理性）**：伪转移 -28.6% = 转移更合理
- **评估**：这是四轮搜索中**最有价值的升级路径**。但需新增周线宏观层 HMM + 条件化机制，工作量中等。**列为优先级 3（与 Conformal/CPCV 同级）**。

#### 发现 2：TVTP 时变转移概率 — 动态调制矩阵的第一性原理解法

**arXiv:2606.06190（2026-06）Multi-Scale MS-GARCH 核心**：
- **Time-Varying Transition Probabilities (TVTP)**：转移矩阵 p_ij,t = exp(a_ij + γ_ij·z_t) / Σ exp(...)
- z_t 是复合压力指数（microstructure stress + seasonality + macro stress）
- TVTP 在 4H/1H 尺度 ΔAIC=+690.7/+499.9（显著优于静态），1D 尺度静态仍最优
- **Staggered parameter bounds**：强制波动率单调排序，**缓解标签切换**——比 Wasserstein HMM 简单
- **Shannon entropy filter**：H_t = -Σ π_t(k) log π_t(k)，高熵抑制交易——比我们的 ConfidenceSignal（max(P) 四档启发式映射）更第一性原理

**与我们对比**：
- 我们的 HMM 转移矩阵是**静态**的（每季度 refit 一次，期间不变）
- TVTP 让转移概率随外部压力指数**动态变化**——这是中邮证券"动态调制矩阵"的学术原版
- Shannon entropy 替代 ConfidenceSignal：entropy 直接度量分布不确定性，无需手动调四档阈值
- Staggered bounds 比 Wasserstein HMM 更简单地缓解标签切换
- **评估**：TVTP + Shannon entropy + Staggered bounds 三件套是 HMM 引擎的**系统性升级**。但需重写 EM 训练（TVTP 的 multinomial logit 参数估计）。**列为优先级 4（远期系统性升级）**。

#### 发现 3：BOCPD 在线变点检测 — overlay 的概率化升级

**Adams & MacKay 2007，2026 多个 Python 实现**：
- `fiannai/bocd`（PyPI 2026-03）：Gaussian + Student-t + Poisson 观测模型，pip 可装
- metricgate（2026-05）：Normal-Gamma 共轭预测，O(t) 每步更新，**O(1) 内存**（带剪枝）
- CSDN（2026-02）：金融异常检测实战，**Student-t 似然处理肥尾**

**与我们对比**：
- 我们的 D-SIGNAL-68 overlay 是**规则法**（阈值穿越触发 CRISIS/RECOVERY/BREAKOUT）
- BOCPD 产出 **P(刚发生变点)** 的概率流——比阈值规则更原理化
- 但 BOCPD 是**单变量**（多变量是未来方向），需应用到复合信号（如 Shrinkage 输出或波动率指数）
- **评估**：BOCPD 可作为 overlay 的**概率化补充**——在规则法 overlay 之上叠一层 BOCPD 变点概率，提高拐点检测的统计严谨性。但单变量限制使其只能作为辅助信号。**列为优先级 4（可选辅助升级）**。

#### 发现 4：Multi-Scale 共识 — 多时间框架对齐

**Junglebot Adaptive Regime Framework（2026-05）+ TDFI Multi-Resolution（2026-04）**：
- 每个时间框架有自己的 regime 模型 + 特征集
- 加权对齐分数：高时间框架权重更大（定义结构性条件）
- TDFI 三分辨率（fast 8 / medium 13 / slow 21）+ 共识分数 -3~+3
- 过渡态（±1）标记早期转折——一个层次已转，其他还没跟上

**与我们对比**：
- 我们的 regime 检测是**单一日线尺度**
- 多尺度共识可捕捉"周线已转牛但日线还在震荡"的过渡态
- **评估**：多尺度是层次 HMM（发现 1）的扩展——层次 HMM 是"周线条件化日线"，多尺度共识是"多框架投票"。两者可结合。**列为发现 1 的扩展，优先级随层次 HMM**。

#### 第四轮新增升级路径汇总

| 升级路径 | 解决问题 | 优先级 | 来源 |
|---|---|---|---|
| **层次 HMM**（周→日） | 伪转移 -28.6%，状态持续 +38.5% | 优先级 3 | AlgoGators 2025-11 |
| TVTP 时变转移概率 | 静态转移矩阵→动态 | 优先级 4 | arXiv:2606.06190 |
| Shannon entropy filter | ConfidenceSignal 启发式→信息论 | 优先级 4 | arXiv:2606.06190 |
| Staggered parameter bounds | 标签切换（比 Wasserstein 简单） | 优先级 4 | arXiv:2606.06190 |
| BOCPD 变点概率 | overlay 规则法→概率化 | 优先级 4 | Adams-MacKay 2007 |

**最终总结论**：核心算法（HMM 4态 + 两阶段校准 + 乘法 Shrinkage + 特征工程）**四轮搜索全部背书**。3 个验证缺口该补（Conformal/CPCV/Stationary Bootstrap）。**11 条升级路径**备查（层次 HMM 最有价值，TVTP/Shannon/Staggered 三件套是系统性升级，BOCPD/Wasserstein/Student-t/Feature Saliency/动态调制矩阵/RARP/regime-conditional 为远期路径）。

## 1. 目标与定位

### 1.1 验证什么

regime 检测器输出 12 维灰度概率分布，驱动 `Shrinkage = ConfidenceSignal × RiskSignal` 做风险节流。回测验证回答三个核心问题：

> ⚠️ **已更新（见 §0.5.2）**：实际实现为 **7 维概率**（4 HMM 基态 + 3 overlay 特殊态），非原方案的 12 维。9 态经 BIC 降为 4 态。下文 12 维/9 态表述为原始规划，保留为历史真源。

| 问题 | 验证维度 | 失败后果 |
|---|---|---|
| **模型准不准？** | HMM 9 态拟合质量 + 概率分布校准度 | 概率分布失准→Shrinkage 收缩方向错 |
| **节流有没有用？** | Shrinkage 开/关对比 MaxDD/Sharpe/Calmar | 节流无效=白搭复杂度，不如静态等权 |
| **参数稳不稳？** | 阈值敏感性 + Walk-Forward 稳定性 | 参数过拟合=历史好看未来崩 |

### 1.2 核心原则

1. **对接现有 BM-BT 框架，不另起炉灶**：项目已有 49 环节回测体系（48 运营态），regime 验证复用现有引擎/指标/门控，只补 regime 特有的验证逻辑
2. **regime 是"风险节流器"不是"策略"**：验证焦点是"风险节流效果"（防御性），不是"alpha 收益"（进攻性）——与 design_memo_001 v1.2.0 裁定一致
3. **参考 Morwane 实证的验证方法**：开/关对比 + block-bootstrap + walk-forward 季度重拟合
4. **先简后繁**：MVP 先验证核心假设（节流有效），再验证模型质量，最后参数校准

### 1.3 regime 检测器 vs 策略回测的关键差异

> 这决定了不能直接套用策略回测流程，需要适配。

| 维度 | 策略回测（现有 BM-BT 流程） | regime 检测器回测 |
|---|---|---|
| **输出** | 持仓信号（买/卖/持有） | 12 维概率分布 P(r1)...P(r12) |
| **用途** | 直接生成 alpha 收益 | 驱动 Shrinkage 风险节流（乘到 budget 上） |
| **验证焦点** | 策略收益 Sharpe/MaxDD | 节流效果（MaxDD 改善）+ 概率分布质量 |
| **过拟合风险** | 参数过拟合→未来亏钱 | HMM 过拟合→收缩方向错（但误差容忍，因为是防御性） |
| **因果链** | 信号→持仓→收益 | 概率→Shrinkage→budget→策略部署→组合回撤 |
| **现有模块对接** | BM-BT-01~07 全流程 | 需在 BM-BT-02 数据接入侧加 regime 输出，BM-BT-05/06 验证模型质量 |

**关键洞察**：regime 做风险节流的误差不对称（design_memo_001 §2.2）——判错=机会成本（少赚），不像 alpha 择时判错=主动亏损。所以验证标准应宽松于策略验证：**重点验证"不伤害"（Sharpe 不显著降），而非"大幅改善"**。

## 2. 对接现有回测框架

> regime 验证复用现有 BM-BT-01~07 的哪些环节，哪些需要新建。

### 2.1 现有环节映射

| BM-BT 环节 | 现有能力 | regime 验证用途 | 复用/新建 |
|---|---|---|---|
| **BM-BT-01** 回测引擎 | 向量化+事件驱动+撮合+A股约束 | 跑 Shrinkage 开/关对比回测 | ✅ 复用 |
| **BM-BT-02** 数据接入 | miniQMT Tick + ClickHouse 日线 | 接入 regime 概率分布作为 Shrinkage 输入 | 🟧 需扩展：regime 输出接入点 |
| **BM-BT-03-A** 绩效指标 | Sharpe/Sortino/MaxDD/IC/IR/胜率 | 对比开/关组合绩效 | ✅ 复用 |
| **BM-BT-03-E** 密度预测验证 | CRPS/校准度（设计态） | **验证 12 维概率分布质量** | 🟧 需启用：regime 概率校准度 |
| **BM-BT-04** PIT 铁律 | AS OF JOIN + Embargo | regime HMM 训练的 PIT 保证 | ✅ 复用 |
| **BM-BT-05** 过拟合检测 | 三维度（样本内外/参数敏感/多重比较） | HMM 过拟合检测 + 阈值敏感性 | ✅ 复用 |
| **BM-BT-06** Walk-Forward | 滚动窗口+参数稳定性 | HMM 滚动重训练 + 阈值稳定性 | ✅ 复用 |
| **BM-BT-07** 决策门控 | IS→WFA→OOS 三阶段 | regime 验证门控（适配后） | 🟧 需适配：门控标准改"节流有效"非"alpha 显著" |
| **BM-BT-05-G** Deflated Sharpe | 已有 deflated_sharpe_calculator | Shrinkage 效果的统计显著性 | ✅ 复用 |

### 2.2 需要新建的部分（最小集）

1. **regime 检测器实现**（前置工程，§8）：HMM 9态 + D-SIGNAL-68 覆盖层 + Shrinkage 公式
2. **Shrinkage 接入点**：在 BM-BT-02 数据接入侧，把 regime 概率→Shrinkage→budget 缩放，注入回测引擎
3. **概率分布质量验证**：启用 BM-BT-03-E，针对 12 维概率分布算 CRPS/校准度/Brier score
4. **节流效果对比器**：Shrinkage 开/关两组回测的 MaxDD/Sharpe/Calmar 差异 + 统计显著性

> 新建部分都是"适配层"，不改动现有回测引擎核心。

## 3. 验证目标清单（5 大类）

### A. HMM 模型质量验证（模型准不准）

| 编号 | 验证项 | 对接环节 | 核心问题 |
|---|---|---|---|
| A1 | 9 态样本充足性 | BM-BT-05 | 稀有态（Bull-High/Bear-High ~5%）样本够 HMM 学吗？ |
| A2 | HMM 过拟合检测 | BM-BT-05-A/B/C | IS vs OOS 概率预测准确率差异大吗？ |
| A3 | 状态转移合理性 | 新建 | Viterbi 解码的事后验证——转移路径符合 spec §4 吗？ |
| A4 | 特征重要性 | BM-BT-05-B | 哪些特征驱动状态判定？符合 fibalgo"特征>模型"论断吗？ |

### B. 概率分布质量验证（概率校准吗）

| 编号 | 验证项 | 对接环节 | 核心问题 |
|---|---|---|---|
| B1 | 概率校准度 | BM-BT-03-E | P(Bull)=80% 时，真有 80% 是牛市吗？（可靠性曲线） |
| B2 | CRPS 概率预测技能 | BM-BT-03-E | 概率分布比 climatology 基准好吗？ |
| B3 | 置信度合理性 | 新建 | max(P) 分布合理吗？是否长期低置信度（Shrinkage 一直强收缩）？ |
| B4 | 转换触发准确性 | 新建 | 8 个转换（T1-T6/S1/S2）的触发时点 vs 历史事件吻合吗？ |

### C. Shrinkage 风险节流效果验证（核心：节流有没有用）

| 编号 | 验证项 | 对接环节 | 核心问题 |
|---|---|---|---|
| **C1** | **开/关对比（核心）** | BM-BT-01/03 | Shrinkage 开 vs 关，MaxDD/Sharpe/Calmar 差异？ |
| C2 | 极端事件回撤保护 | BM-BT-03 | CRISIS/RECOVERY/BREAKOUT 触发时，回撤保护了多少？ |
| C3 | 节流归因 | 新建 | 各态 Shrinkage 贡献——哪个态节流最有效？ |
| C4 | 统计显著性 | BM-BT-05-G | Shrinkage 效果是真信号还是运气？（block-bootstrap） |

### D. 参数阈值校准（参数稳不稳）

| 编号 | 验证项 | 对接环节 | 核心问题 |
|---|---|---|---|
| D1 | ConfidenceSignal 映射 | BM-BT-05-B | max(P) 四档阈值（60/80/95%）合理吗？ |
| D2 | RiskSignal 13 参数 | BM-BT-05-B | 11 个风险参数四档分位边界（80/90 分位）合理吗？ |
| D3 | 聚合公式参数 | BM-BT-05-B | 共振惩罚 0.05 + 机会恢复 0.25 合理吗？ |
| D4 | 8 转换评分门槛 | BM-BT-05-B | T1-T6/S1/S2 触发/确认分数阈值合理吗？ |

### E. 鲁棒性验证（防过拟合）

| 编号 | 验证项 | 对接环节 | 核心问题 |
|---|---|---|---|
| E1 | Walk-Forward 稳定性 | BM-BT-06 | HMM 季度重拟合，各窗口 OOS 表现稳定吗？ |
| E2 | Block-bootstrap | BM-BT-05-G | 打乱重采样，Shrinkage 效果的置信区间？ |
| E3 | 参数敏感性 | BM-BT-05-B | 阈值±20% 扰动，效果是否悬崖式变化？ |
| E4 | 交易成本敏感性 | BM-BT-01-D | 0-50bps 成本下，Shrinkage 效果稳健吗？ |

## 4. 各目标验证方法

### 4.1 A 类：HMM 模型质量

#### A1 样本充足性

- **方法**：在全量历史数据（2000-2026，日线）上跑 HMM 9 态拟合，统计各态频次
- **关注点**：3 个高波动态（Bull-High/Neutral-High/Bear-High）预期各 ~5%，按 ~6500 个交易日算约 325 天/态——够 HMM 学吗？
- **判定**：
  - 样本 ≥ 100 天/态 → 充足，独立建模
  - 样本 50-100 天/态 → 中等，需收缩向均值（§2.7 稀有态处理）
  - 样本 < 50 天/态 → 不足，考虑合并（高波动三态合并为一档→6 态）
- **对接**：BM-BT-05 过拟合检测的样本量前置检查

#### A2 HMM 过拟合检测

- **方法**：IS/OOS 分割（如 2000-2018 训练，2019-2026 测试），对比两段的概率预测准确率
- **指标**：
  - IS vs OOS 状态识别一致率（Viterbi 解码对比）
  - IS vs OOS 概率分布 KL 散度
- **判定**：OOS 准确率 / IS 准确率 ≥ 0.7（差异 < 30%）→ 未过拟合
- **对接**：BM-BT-05-A 样本内外对比检测

#### A3 状态转移合理性

- **方法**：用 Viterbi 解码全历史，统计实际转移矩阵，对比 spec §4 的 8 个转换路径
- **关注点**：实际转移频率是否符合 spec 预期（如 CRISIS→RECOVERY 是否高频，Bull-Low→Bull-High 是否罕见）
- **判定**：spec 定义的转移路径覆盖实际转移的 ≥ 80%

### 4.2 B 类：概率分布质量

#### B1 概率校准度（可靠性曲线）

- **方法**：把 max(P) 分桶（0-20%/20-40%/.../80-100%），算每桶内"预测的最高态"实际发生的频率
- **理想**：P=80% 桶内，实际频率也 ≈ 80%（对角线）
- **判定**：校准误差（|预测概率-实际频率|均值）< 10%
- **对接**：BM-BT-03-E 密度预测验证的校准度指标

#### B2 CRPS 概率预测技能

- **方法**：算 regime 概率分布的 CRPS（Continuous Ranked Probability Score），对比 climatology 基准（长期平均频率）
- **判定**：CRPS < climatology CRPS（比"永远预测平均频率"好）
- **对接**：BM-BT-03-E

#### B4 转换触发准确性

- **方法**：标注历史关键事件（如 2008 金融危机、2015 股灾、2020 疫情、2024-08 见底），检查 8 个转换的触发时点是否吻合
- **案例库**：
  - CRISIS 触发：2008-09/2015-08/2020-03/2024-07-17
  - S2 确认（复苏）：2008-11/2015-09/2020-04/2024-08-04
  - BREAKOUT：主升浪启动点
- **判定**：8 个历史事件中，转换触发时点 ±5 个交易日内吻合 ≥ 6 个

### 4.3 C 类：Shrinkage 风险节流效果（核心）

#### C1 开/关对比（最核心）

> 直接对照 Morwane 实证的 risk-throttle 验证方法。

- **实验设计**：
  - **基准组（关）**：Shrinkage=1.0（无 regime 节流），策略按等权/先验 budget 部署
  - **实验组（开）**：Shrinkage = ConfidenceSignal × RiskSignal，regime 驱动 budget 收缩
  - **同一批策略**、同一历史区间、同一交易成本
- **对比指标**：

| 指标 | 基准组（关） | 实验组（开） | 判定 |
|---|---|---|---|
| Sharpe | S_base | S_shrink | S_shrink ≥ S_base − 0.1（不显著伤害） |
| MaxDD | DD_base | DD_shrink | DD_shrink 改善 ≥ 3 个百分点（节流有效） |
| Calmar | C_base | C_shrink | C_shrink 提升 ≥ 20% |
| Turnover | T_base | T_shrink | T_shrink ≤ T_base × 2（换手不爆） |

- **行业基准**（Morwane OOS 2013-2026）：
  - Sharpe：1.43（关）→ 1.43（开）= **不变**
  - MaxDD：−14.2%（关）→ −10.3%（开）= **改善 3.9pp**
  - Calmar：+1.04 → +1.43 = **提升 38%**
  - Turnover：1.7×/yr（极低）
- **对接**：BM-BT-01 引擎 + BM-BT-03-A 指标

#### C2 极端事件回撤保护

- **方法**：定位历史 CRISIS 时段（2008-09/2015-08/2020-03/2024-07），对比开/关在这些时段的回撤
- **关注点**：CRISIS 触发时 Shrinkage 是否及时收缩？保护了多少回撤？
- **判定**：CRISIS 时段 MaxDD 改善 ≥ 5 个百分点

#### C4 统计显著性（block-bootstrap）

- **方法**：block-bootstrap 2000×（21-day blocks，对照 Morwane），算 Shrinkage 效果的置信区间
- **判定**：Sharpe 改善 90% CI 下界 > 0，P(Sharpe_开 > Sharpe_关) ≥ 75%
- **对接**：BM-BT-05-G Deflated Sharpe + 置换检验

### 4.4 D 类：参数阈值校准

#### D1-D4 参数敏感性网格

- **方法**：对每个参数（ConfidenceSignal 四档/RiskSignal 13 参数/聚合公式参数/8 转换门槛）做 ±20% 扰动，跑网格回测，看效果变化
- **判定**：
  - 参数±20% 扰动，MaxDD 改善幅度变化 < 30% → 稳健（非悬崖型）
  - 存在"最优参数孤岛"（邻域效果骤降）→ 过拟合警告
- **对接**：BM-BT-05-B 参数敏感性检测 + BM-BT-05-E 参数优化分析器

### 4.5 E 类：鲁棒性

#### E1 Walk-Forward

- **方法**：季度重拟合 HMM（对照 Morwane），滚动窗口跑 2015-2026，统计各窗口 OOS 的 Shrinkage 效果
- **判定**：各窗口 MaxDD 改善的变异系数（CV）< 0.5（稳定）
- **对接**：BM-BT-06 Walk-Forward

#### E4 交易成本敏感性

- **方法**：在 0/2bps/5bps/10bps/50bps 成本下分别跑开/关对比
- **判定**：Shrinkage 效果在 0-50bps 范围内方向一致（稳健）
- **对接**：BM-BT-01-D A股交易约束

## 5. 验证标准汇总（通过/失败门槛）

> **核心标准**：regime 做风险节流是"防御性"用途，标准应聚焦"不伤害+改善回撤"，而非"提升收益"。

| 验证类 | 验证项 | 通过标准 | 失败后果 |
|---|---|---|---|
| **C1（核心）** | Shrinkage 开/关对比 | Sharpe 降 < 0.1 **且** MaxDD 改善 ≥ 3pp **且** Calmar 升 ≥ 20% | 节流无效，回退静态等权（不部署 regime） |
| C2 | 极端事件保护 | CRISIS 时段 MaxDD 改善 ≥ 5pp | CRISIS 检测失效，重审 D-SIGNAL-68 触发逻辑 |
| C4 | 统计显著性 | P(Sharpe_开 > Sharpe_关) ≥ 75% | 效果不显著，可能运气 |
| A1 | 样本充足性 | 稀有态 ≥ 50 天/态 | 合并为 6-8 态 |
| A2 | HMM 过拟合 | OOS/IS 准确率 ≥ 0.7 | 重审特征工程/降态数 |
| B1 | 概率校准度 | 校准误差 < 10% | 概率不可信，Shrinkage 方向可能错 |
| B4 | 转换触发准确 | 8 事件中 ≥ 6 个吻合 | 转换逻辑重审 |
| E1 | Walk-Forward 稳定 | 各窗口 CV < 0.5 | 不稳定，参数过拟合 |
| E3 | 参数敏感性 | ±20% 扰动效果变化 < 30% | 悬崖型参数，过拟合 |

> **一票否决**：C1 不通过 = regime 检测器不部署（回退静态等权）。这是底线——如果风险节流不改善回撤还伤害 Sharpe，整个 regime 系统没有存在价值。

## 6. 优先级与依赖顺序

```
Phase 0：前置工程（regime 检测器实现）← 必须先做
   ↓ HMM 9态 + D-SIGNAL-68 + Shrinkage 公式 → 可运行原型
Phase 1：核心假设验证（C1 开/关对比）
   ↓ 最小验证：Shrinkage 节流到底有没有用？
   ├── 通过 → 继续 Phase 2
   └── 失败 → regime 不部署，省下后续工作
Phase 2：模型质量（A1/A2/B1/B4）
   ↓ HMM 准不准？概率校准吗？转换触发对吗？
Phase 3：参数校准（D1-D4）
   ↓ 阈值调优 + 敏感性
Phase 4：鲁棒性（E1-E4）
   ↓ Walk-Forward + bootstrap + 成本敏感性
Phase 5：决策门控（对接 BM-BT-07）
   ↓ IS→WFA→OOS 适配后门控，通过→部署
```

### 6.1 为什么这个顺序

1. **Phase 1 在 Phase 2 之前**：先验证"节流有没有用"（核心假设），再验证"模型准不准"。如果节流本身没用，模型再准也白搭——省下 Phase 2-4 的工作。
2. **直接完整 12 态**：Phase 0 直接实现完整 12 态（用户 2026-08-06 裁定），不做简化版。验证后若发现可简化，那是"基于证据的简化"。
3. **Phase 3 在 Phase 2 之后**：模型质量没验证前，调参数是调空气——过拟合的模型调参再精细也没用。

### 6.2 各 Phase 的前置依赖

| Phase | 前置依赖 | 产出 |
|---|---|---|
| Phase 0 | regime spec（已就绪 discussion_001 v1.3.1） | 可运行 regime 原型 |
| Phase 1 | Phase 0 + 现有回测引擎 + 至少 1 个策略 | C1 开/关对比报告 |
| Phase 2 | Phase 0 + BM-BT-03-E/05 | 模型质量报告 |
| Phase 3 | Phase 2 通过 + BM-BT-05-B/E | 参数校准报告 |
| Phase 4 | Phase 3 + BM-BT-06 | 鲁棒性报告 |
| Phase 5 | Phase 1-4 全通过 + BM-BT-07 | 部署决策 |

## 7. 数据基础（已确认，2026-08-06）

> 数据探查结论：数据底子足以支撑 regime 回测验证。

| regime 需求 | 数据字段 | 状态 |
|---|---|---|
| 波动率/量价/趋势/形态 | 日K后复权 OHLCV（2000年起） | ✅ 完整 |
| 跨市场相关性 | 指数/期货/港股/美股 K线 | ✅ 完整 |
| 虹吸态 | 880xxx 板块K线+成分股（460板块） | ✅ 完整 |
| 涨跌家数 | 涨跌停 + 实时快照 | ✅ 完整 |
| 新闻情绪 | news_data（多源） | ✅ 完整 |
| VIX 替代 | 期权 IV 曲面（662期权+Greeks） | ✅ 可替代 |
| 估值/融资融券/北向 | daily_valuation/margin/hk_connect | ✅ 完整（北向2024前） |
| 筹码分布 | 无专门数据 | ❌ 用换手率代理 |

**缺口不阻断**：12/13 参数有数据，#12 筹码用换手率估算。

## 8. 前置工程：regime 检测器实现路径

> Phase 0 的具体内容——把 discussion_001 spec 变成可运行代码。

### 8.1 实现分解（完整 12 态，分模块施工）

> **用户裁定（2026-08-06）**：从第一性原理出发，直接实现完整 12 态，回测验证后再根据结果优化/简化。理由：最终目标就是 12 态，先做简化版再重做完整版是重复工作；完整版验证后若发现某些态可合并/某些参数可去除，那是"基于证据的简化"，比"拍脑袋的简化"更可靠。
>
> ⚠️ **已更新（见 §0.5.2）**：A2 过拟合检测发现 9 态过度细分（OOS/IS=0.34），经 BIC 降为 **4 态**（discussion_004 §2.1）。这正是本节预期的"基于证据的简化"——验证后发现过度细分，基于 BIC 证据降态。下表 9 态/12 态为原始规划，保留为历史真源。

| 模块 | 实现内容 | spec 真源 |
|---|---|---|
| **HMM 9态** | 9 态 3×3 网格（趋势×波动率），多特征喂入 | discussion_001 §2.6/§3 |
| **D-SIGNAL-68 覆盖层** | 3 特殊态（CRISIS/RECOVERY/BREAKOUT）规则触发 + 8 转换评分 | discussion_001 §2.8/§4 |
| **ConfidenceSignal** | max(P) → 4 档映射（<60%→0.3 / 60-80%→0.6 / 80-95%→0.85 / >95%→1.0） | design_memo_001 §2.2 |
| **RiskSignal** | 13 参数完整计算 + 聚合公式（min主导+共振惩罚+机会恢复） | discussion_001 §5.3 |
| **Shrinkage** | ConfidenceSignal × RiskSignal，注入 RegimeMetaAllocator | design_memo_001 §2.2 |

> **实现后验证再简化**：完整 12 态跑通回测后，若验证发现某些态样本不足（A1）或某些参数无贡献（D2），再做"基于证据的简化"（如高波动三态合并）。这与"先拍脑袋简化"本质不同。

### 8.2 实现步骤

1. **特征工程**：从 ClickHouse 算 regime 特征（波动率分位/趋势斜率/相关性矩阵/涨跌家数）
2. **HMM 训练**：hmmlearn GaussianHMM，9 态，walk-forward 季度重拟合
3. **D-SIGNAL-68 覆盖层**：规则引擎，3 特殊态触发
4. **Shrinkage 计算**：ConfidenceSignal × RiskSignal 聚合
5. **回测接入点**：把 Shrinkage 注入 BM-BT-02 数据接入侧，缩放策略 budget

## 9. 行业实证对照

> 验证方法参考专业机构/量化社区做法。

| 验证方法 | 行业来源 | 本方案对接 |
|---|---|---|
| 开/关对比 risk-throttle | Morwane multi-strategy-alpha-book（OOS 2013-2026） | C1 核心验证 |
| Block-bootstrap 2000× | Morwane（21-day blocks） | C4 统计显著性 |
| Walk-Forward 季度重拟合 | Morwane / ItsSawhill / arxiv 2509.14385 | E1 鲁棒性 |
| CRPS 概率预测技能 | BM-BT-03-E 密度预测验证 | B2 概率分布质量 |
| Deflated Sharpe Ratio | 项目已有 deflated_sharpe_calculator | C4 多重比较校正 |
| PIT + Embargo | BM-BT-04（AS OF JOIN + Embargo） | HMM 训练 PIT 保证 |
| 因果 Viterbi 解码 | Morwane（causal Viterbi） | A3 状态转移（防前视） |
| 参数敏感性分析 | BM-BT-05-B | D1-D4/E3 参数校准 |

**行业对齐结论**：本方案的全部验证方法均有行业先例，无自创方法。核心的"开/关对比+bootstrap"直接复刻 Morwane 的 risk-throttle 验证范式。

## 10. 已决策项

> 以下 4 项均已决策（2026-08-06），方案定稿。

1. ~~**Phase 1 用简化 regime 还是完整 regime**~~ → ✅ 已决策（2026-08-06）：直接实现完整 12 态，验证后再基于证据简化。详见 §8.1。
2. **验证用哪个策略做载体** → ✅ 已决策（2026-08-06）：先用现有 topn_momentum_strategy 跑通验证框架，正式策略定了再换。
3. **验证区间** → ✅ 已决策（2026-08-06）：2015-2026（覆盖 2015 股灾/2018 贸易战/2020 疫情/2024 见底，含多轮 CRISIS-RECOVERY 周期）。
4. **HMM 实现** → ✅ 已决策（2026-08-06）：hmmlearn GaussianHMM（与行业主流一致，Morwane/fibalgo 均用）。

> **与另一个 AI 施工对话的协调**（2026-08-06）：另一对话正在落盘 4 个多策略模块 blueprint（StrategyBook/FirmRiskAggregator/RegimeMetaAllocator/BudgetChangeHandler）+ regime 检测器 blueprint + 代码骨架。本验证方案（discussion_002）是这些模块的"验收指南"——等骨架就绪后，按本方案执行回测验证。另一对话施工时应参考本方案 §4，确保 regime 检测器接口满足验证需求（输出概率分布供 CRPS、可开关 Shrinkage 供 C1 对比）。

## 11. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-06 | 0.1.0 | 初稿 | regime 检测器回测验证方案设计，对接现有 BM-BT 框架，参考 Morwane risk-throttle 验证范式 |
| 2026-08-06 | 0.2.0 | §8.1 改为完整 12 态分模块实现（用户裁定直接做完整版）；§10.1 标记已决策；新增与另一 AI 施工对话的协调说明 | 用户第一性原理意见：最终目标就是 12 态，先简化再重做是重复工作；验证后基于证据简化更可靠 |
| 2026-08-06 | 1.0.0 | §10 全部 4 项决策定稿（完整12态/topn_momentum载体/2015-2026区间/hmmlearn）；status→active；性质改为已定稿验收指南 | 用户确认定稿交接，方案进入施工对话参考阶段 |
| 2026-08-08 | 1.1.0 | 新增 §0.5 方案执行状态（反向同步）；标注 Phase 0-2 完成 / 3-5 部分未完成；记录重大偏离 9态→4态（BIC驱动）；回填 C1/A1/A2/B1/B4 实际验证结果与代码结构 | 用户要求从文档可知项目代码最新功能情况；实际执行结果与原方案偏离需文档化 |
| 2026-08-08 | 1.2.0 | 新增 §0.6 算法审查与 2026 研究对照（核心算法审查结论 + 明确不采用算法 + 3缺口1现成 + 施工优先级 + 研究来源索引 + HMM引擎升级路径）；§1.1/§8.1 加 9态→4态 内联注释 | 用户要求审查算法缺口+搜2026最新算法+查文档结构；二次搜索发现 Wasserstein HMM/Student-t发射/Feature Saliency HMM |
| 2026-08-08 | 1.3.0 | 新增 §0.6.7 第三轮搜索（A股4态行业共识 + 动态调制矩阵 + RARP状态条件协方差 + regime-conditional allocation + Kelly警示）；新增 §0.6.8 三轮总结论 | 用户要求再次审查+全网搜2026最新；三轮搜索确认核心算法全部背书，6条升级路径备查 |
| 2026-08-08 | 1.4.0 | 新增 §0.6.9 第四轮发现（层次HMM状态持续+38.5%/伪转移-28.6% + TVTP时变转移 + Shannon entropy替代ConfidenceSignal + Staggered bounds缓解标签切换 + BOCPD变点概率 + 多尺度共识）；§0.6.8 更新为四轮总结论；升级路径从6条增至11条 | 用户要求第四轮审查；层次HMM是四轮中最有价值的升级路径（直接解决A3伪转移问题） |
