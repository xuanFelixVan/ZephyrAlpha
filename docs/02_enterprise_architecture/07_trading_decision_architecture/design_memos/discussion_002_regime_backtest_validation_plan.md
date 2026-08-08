---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.1.0"
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

## 1. 目标与定位

### 1.1 验证什么

regime 检测器输出 12 维灰度概率分布，驱动 `Shrinkage = ConfidenceSignal × RiskSignal` 做风险节流。回测验证回答三个核心问题：

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
