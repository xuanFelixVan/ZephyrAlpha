# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md
# [MODULE] zephyr.regime.core.regime_detector
# [DOMAIN] D_REGIME
# [DEPENDENCIES] hmmlearn; numpy; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PA-007(RegimeMetaAllocator消费RegimeProbabilities+Shrinkage); BM-BT-03-E(回测验证消费7维概率)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RegimeProbabilities.probabilities Σ=1.0; Shrinkage≤1.0(只减不增); shrinkage_enabled=False时Shrinkage=1.0; HMM 4态walk-forward季度重拟合; 不输出硬标签只输出7维灰度概率(4 HMM+3 overlay)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegimeFeatureError(ZA-REGIME-0001); HMMFittingError(ZA-REGIME-0002); ShrinkageComputationError(ZA-REGIME-0003); OverlayRuleError(ZA-REGIME-0004); ProbabilityNormalizationError(ZA-REGIME-0005)
# [TESTS] tests/regime/test_regime_detector.py
# [A_module] module_id=MOD-REGIME-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RegimeDetector — 7态Regime检测器 (MOD-REGIME-001)

D_REGIME 域核心模块，整个交易决策架构的**最上游**。输出 7 维灰度概率分布 +
Shrinkage 风险节流因子，供 RegimeMetaAllocator 做 budget 分配。是 regime 链源头
（regime → Shrinkage → budget → StrategyBook）。

五子模块（11_regime_backtest_validation_plan §8.1）：
    ① HMM 4态（BIC 扫描确定，Viterbi 解码验证语义）—— hmmlearn GaussianHMM
    ② D-SIGNAL-68 覆盖层（CRISIS/RECOVERY/BREAKOUT 规则触发 + 8转换评分）
    ③ ConfidenceSignal（max(P) 4档映射 + 稀有态折扣）
    ④ RiskSignal（13参数完整计算 + 聚合公式）
    ⑤ Shrinkage（ConfidenceSignal × RiskSignal，可开关）

可验证性接口（11_regime_backtest_validation_plan §4 验证需求，接口设计不可破坏）：
    ① 输出 7 维概率分布（RegimeProbabilities，Σ=1）—— B1 校准度 / B2 CRPS
    ② Shrinkage 可开关（shrinkage_enabled）—— C1 开/关对比（**一票否决**）
    ③ 8 转换触发可记录（TransitionTriggered）—— B4 转换触发准确性
    ④ HMM hmmlearn GaussianHMM 4态 walk-forward 季度重拟合 —— A1/A2/A3 模型质量

降态说明（13_regime_phase3_engineering_plan §2.1，2026-08-07）：
    原 9 态（3×3 趋势×波动率网格）经 BIC 扫描确认过度细分——A2 OOS/IS 一致率仅
    0.34（门槛 0.7），9 态在 2010-2018 和 2019-2026 学的规律完全不同。全历史 BIC
    Kneedle 拐点=4，walk-forward 46 季度拐点分布{4:19, 5:25, 7:2}。选 4 态：
      r1 低波震荡(27.6%) / r2 中波震荡(37.4%) / r3 牛市趋势(14.9%) / r4 熊市阴跌(20.2%)
    Viterbi 统计特征（全历史 3733 样本，RobustScaler 标准化后）：
      r1: vol_pct=-0.52, fr_5d=+0.0003（低波横盘）
      r2: vol_pct=+0.42, fr_5d=+0.0018（中波温和偏强）
      r3: vol_pct=+0.58, slope=+0.149, fr_5d=+0.0039（强涨量增，最高正收益）
      r4: vol_pct=-0.44, slope=-0.049, fr_5d=-0.0014（唯一负收益，阴跌）

降级策略（blueprint §7.4）：hmmlearn 不可用 / 拟合失败 → HMM 4 态均匀分布 P=1/4；
RiskSignalInputs 缺失 → RiskSignal=1.0；OverlaySignals 缺失 → 退化为纯 HMM。

依据: 10_regime_detector_spec v1.3.1（原12态spec）/ 11_regime_backtest_validation_plan v1.0.0（验证方案）/ 13_regime_phase3_engineering_plan §2.1（4态降维）
SSoT: depgraph MOD-REGIME-001
Version: 0.3.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 沪深300 日线数据
#   fields: 收盘价 + 成交量
#   code: 000300
# - id: I2
#   name: 中证500 日线数据
#   fields: 收盘价
#   code: 000905
# - id: I3
#   name: 创业板指 日线数据
#   fields: 收盘价
#   code: 399006
# - id: I4
#   name: 深证综指 涨跌家数数据
#   fields: 上涨家数 + 下跌家数
#   code: 399106
# 层: 特征
# - id: F1
#   name_zh: 已实现波动率分位
#   name_en: realized_vol_pct
#   intro: 近20日波动率在250日的排名分位
#   formula: r=log(C/C.shift1) → HV=r.rolling20.std×√252 → HV.rolling250.rank(pct) ∈0,1
#   code: market_features.py L45
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2a
#   name_zh: 趋势持续性指数
#   name_en: hurst_dfa
#   intro: DFA法Hurst >0.5有趋势 <0.5均值回归
#   formula: 累积和profile → 多窗口线性去趋势 → log-log回归斜率 ∈0,1
#   code: trend_features.py L35
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2b
#   name_zh: 卡尔曼趋势斜率
#   name_en: kalman_slope
#   intro: 卡尔曼滤波算自适应趋势斜率
#   formula: s(t)=s(t-1)+w(t) 归一化 clamp(s/10×std(r),-1,1)
#   code: trend_features.py L132
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 跨资产相关性
#   name_en: cross_asset_corr
#   intro: 沪深300/中证500/创业板三大指数相关度
#   formula: 两两 rolling corr(60日)均值 ∈-1,1
#   code: market_features.py L80
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F4
#   name_zh: 涨跌家数比
#   name_en: ad_ratio
#   intro: 全市场上涨家数vs下跌家数
#   formula: tanh(log((涨+1)/(跌+1))) ∈-1,1
#   code: market_features.py L116
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F5
#   name_zh: 成交量异常度
#   name_en: volume_anomaly
#   intro: 成交量相对均值的异常程度
#   formula: z=(vol-ma20)/std20
#   code: market_features.py L147
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 指标
# - id: KDJ
#   name_zh: 随机指标 9,3,3
#   name_en: KDJ
#   intro: 判断超买超卖和短期转折信号
#   formula: RSV=(C-Ln)/(Hn-Ln)×100 K=SMA(RSV,3,1) D=SMA(K,3,1) J=3K-2D
#   code: risk_features.py L338 自实现ewm
#   registry: 指标表有kdj列 但代码未读表
#   is_break: true
# - id: MA
#   name_zh: 均线 5/20/60
#   name_en: MA
#   intro: 判断趋势方向和支撑压力位
#   formula: close.rolling(N).mean
#   code: overlay_features.py L495 pandas重算
#   registry: 指标表有ma列 但代码未读表
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① HMM隐马尔可夫 4态模型
#   name_en: HMM 4-state
#   intro: 用4种市场状态概率分布判断大盘所处阶段
#   desc: BIC贝叶斯信息准则扫描定态数 + Viterbi维特比解码
#   inputs: F1 F2a F2b F3 F4 F5
#   outputs: 4维概率
#   invariant: Σ=1.0
# - id: A2
#   name_zh: ② 覆盖层规则 D-SIGNAL-68
#   name_en: Overlay
#   intro: 在HMM上叠加危机/复苏/突破3种特殊状态规则
#   desc: 8转换31维度规则触发 CRISIS危机/RECOVERY复苏/BREAKOUT突破
#   inputs: F1 F3 F5 KDJ MA
#   outputs: 3维覆盖态概率
# - id: A3
#   name_zh: ③ 置信度信号
#   name_en: ConfidenceSignal
#   intro: 根据HMM最大概率映射4档置信度，稀有态打折扣
#   desc: max(P) 4档映射 + 稀有态折扣
#   inputs: A1 A2
#   outputs: 置信度
# - id: A4
#   name_zh: ④ 风险信号 13参数
#   name_en: RiskSignal
#   intro: 13个风险维度聚合算风险系数，越低越危险
#   desc: 9有效计算 + 4stub未实现
#   inputs: F1 F2a F2b F3 F4 F5 KDJ
#   outputs: 风险系数 0.30~1.00
# - id: A5
#   name_zh: ⑤ 风险节流因子
#   name_en: Shrinkage
#   intro: 置信度×风险=资金收缩比例，只减不增
#   desc: value = Confidence × Risk
#   inputs: A3 A4
#   outputs: Shrinkage
#   invariant: ≤1.0 只减不增
# 层: 输出
# - id: O1
#   name_zh: 7维灰度概率分布
#   name_en: 7-dim gray probability
#   intro: 4个HMM态 + 3个覆盖层态的概率
#   invariant: Σ=1.0
#   downstream: 不输出硬标签
# - id: O2
#   name_zh: 风险节流因子 Shrinkage
#   name_en: Shrinkage
#   intro: 传给RegimeMetaAllocator做budget资金分配
#   invariant: ≤1.0
#   downstream: RegimeMetaAllocator MOD-PA-007
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F5
# I1 -.->|断点| F2a
# I1 -.->|断点| F2b
# I1 -.->|断点| KDJ
# I1 -.->|断点| MA
# I2 -.->|断点| F3
# I3 -.->|断点| F3
# I4 -.->|断点| F4
# F1 --> A1
# F2a --> A1
# F2b --> A1
# F3 --> A1
# F4 --> A1
# F5 --> A1
# F1 --> A2
# F3 --> A2
# F5 --> A2
# KDJ --> A2
# MA --> A2
# A1 --> A3
# A2 --> A3
# F1 --> A4
# F2a --> A4
# F2b --> A4
# F3 --> A4
# F4 --> A4
# F5 --> A4
# KDJ --> A4
# A3 --> A5
# A4 --> A5
# A1 --> O1
# A2 --> O1
# A5 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# 7 态编号（10_regime_detector_spec §3 + 13_regime_phase3_engineering_plan §2.1 降态：HMM 9态→4态）
# r1-r4: HMM 4态（BIC 扫描确定，Viterbi 解码验证语义）；r10 CRISIS / r11 RECOVERY / r12 BREAKOUT
REGIME_STATES: list[str] = ["r1", "r2", "r3", "r4", "r10", "r11", "r12"]
HMM_STATES: list[str] = [f"r{i}" for i in range(1, 5)]
OVERLAY_STATES: list[str] = ["r10", "r11", "r12"]

# 8 转换（10_regime_detector_spec §4，T1-T6 趋势/震荡转换 + S1/S2 恐慌/复苏转换）
TRANSITIONS: list[str] = ["T1", "T2", "T3", "T4", "T5", "T6", "S1", "S2"]

# Shrinkage 4 档映射（30_multi_strategy_concurrency §2.2 / 10_regime_detector_spec §5.1）
# (max(P) 下界, base_confidence) —— 从高到低匹配，取首个 max(P) >= 下界
# C1 验证 2026-08-06 校准：原阈值 0.95/0.80/0.60 对 HMM 过高（分散概率质量，
# max(P) 天然偏低，总落入最低档 base=0.3 致平时过度收缩）。
# 调整为适应 HMM 分布的阈值，下限抬高到 0.7：ConfidenceSignal 只做"高置信加成"
# 而非"低置信惩罚"，让稳定的 feature-risk（RiskSignal）主导危机节流。
# ⚠️ 4 态降维后（13_regime_phase3_engineering_plan §2.1）：均匀分布 max(P)=0.25，有信号时 0.4-0.7。
# 当前阈值沿用 9 态校准值，步骤8 C1 验证后根据 4 态 max(P) 分布精调。
_CONFIDENCE_BANDS: tuple[tuple[float, float], ...] = (
    (0.50, 1.0),   # top1 ≥50% → 满部署（4态下0.5已是高置信）
    (0.30, 0.9),   # 30-50% → 轻度收缩
    (0.15, 0.8),   # 15-30% → 中度收缩（4态均匀分布=0.25，此档极少触发）
    (0.0, 0.7),    # <15% → 强收缩（4态下不可能低于0.25，此档为防御保留）
)
# 稀有态折扣（30_multi_strategy_concurrency §2.2）：(频率下界, discount)
_RARITY_BANDS: tuple[tuple[float, float], ...] = (
    (0.05, 1.0),   # 常见态 >5%
    (0.01, 0.85),  # 中等态 1-5%
    (0.0, 0.7),    # 稀有态 <1%
)
# 状态风险因子（13_regime_phase3_engineering_plan §2.1.6.2 重设计，基于 4 态 Viterbi 统计特征）
# ⚠️ DEPRECATED — C1 验证 2026-08-06 从 ConfidenceSignal 移除，不再参与 Shrinkage 计算。
# 原因：无监督 HMM 标签在 walk-forward refit 间有 label-switching 问题（r1 本季=牛市，
# 下季可能=熊市），按数字标签套风险因子 = 随机惩罚。危机保护改由 RiskSignal 的
# feature_risk（vol_pct + slope）承担——可靠信号非任意标签。
# 保留定义供未来 label-switching 对齐后（§2.1.6.4 协议）重新启用。
# 4 态语义（13_regime_phase3_engineering_plan §2.1，Viterbi 全历史 3733 样本 RobustScaler 标准化后统计）：
#   r1 低波震荡(27.6%): vol_pct=-0.52, slope=-0.027, fr_5d=+0.0003 → 轻微收缩 0.90
#   r2 中波震荡(37.4%): vol_pct=+0.42, slope=+0.007, fr_5d=+0.0018 → 轻微收缩 0.85
#   r3 牛市趋势(14.9%): vol_pct=+0.58, slope=+0.149, fr_5d=+0.0039 → 不收缩 1.0
#   r4 熊市阴跌(20.2%): vol_pct=-0.44, slope=-0.049, fr_5d=-0.0014 → 大幅收缩 0.50
# overlay 态 r10-r12 编号不变（独立于 HMM 基态，13_regime_phase3_engineering_plan §2.1.6.3）
_STATE_RISK_FACTORS: dict[str, float] = {
    "r1": 0.90,  # 低波震荡  低波动横盘，轻微正收益 → 轻微收缩
    "r2": 0.85,  # 中波震荡  中波动温和偏强，正收益 → 轻微收缩
    "r3": 1.0,   # 牛市趋势  强涨量增，最高正收益 → 不收缩
    "r4": 0.50,  # 熊市阴跌  唯一负收益，阴跌 → 大幅收缩
    "r10": 0.30, # CRISIS    系统性危机（overlay）→ 最强收缩
    "r11": 0.50, # RECOVERY  危机复苏过渡 → 中强收缩
    "r12": 1.0,  # BREAKOUT  突破主升苗头 → 满部署
}

# 8 转换阶段配置（10_regime_detector_spec §4.1 总览表 + §4.6/§4.10.8/§4.11.8/§4.12.8 标准汇总）
# 13_regime_phase3_engineering_plan §2.1.6.3 降态重设计：原 T1/T4/T5/T6 依赖 3×3 网格态间转移
# （如 T4="Bull-Medium→Bull-High"），4 态降维后网格语义不存在，转换语义重新映射：
#   T1 震荡态(r1/r2)→BREAKOUT / T2 熊市态(r4)→RECOVERY / T3 RECOVERY→BREAKOUT
#   T4 牛市态(r3)赶顶 / T5 牛市态(r3)→熊市态(r4)逃顶 / T6 熊市态(r4)冰点
#   S1 任意态→CRISIS / S2 CRISIS→RECOVERY（S1/S2 不依赖基态语义，不变）
# stages 阈值暂沿用原值，P1 阶段（E3 NLP+E5 T3+E6 bad_news_flat）精调
# 每个 stage 的条件：total_gte（总分下界）/ keys_gte（关键维度下界，任一缺失即不满足）/
# keys_or_gte（析取下界，P1-E9d：任一 key 达阈即通过；与 keys_gte 并存时两组均须通过）
# p_overlay：该阶段触发的特殊态概率覆盖（覆盖 HMM）；shrinkage：该阶段的 Shrinkage 锚定值
# stage 判定优先级：strong_confirm > confirm > trigger > fail（取首个满足）
# 维度 key 命名对齐 spec：调用方在 score_breakdown 中提供同名 key
TRANSITION_CONFIG: dict[str, dict[str, Any]] = {
    "T1": {  # 震荡态(r1/r2) → BREAKOUT（§4.6 三阶段评分，4态下降维后原 Neutral-Medium 合并到 r1/r2）
        "overlay_target": "r12",
        "stages": {
            "confirm":       {"keys_gte": {"bqs": 60, "rcs": 60}, "p_overlay": {}, "shrinkage": 1.0},
            "trigger":       {"keys_gte": {"bqs": 60}, "p_overlay": {"r12": 0.80}, "shrinkage": 0.85},
            "fail":          {"keys_gte": {"frs": 60}, "p_overlay": {}, "shrinkage": 0.6},
        },
    },
    "T2": {  # 熊市态(r4) → RECOVERY（§4.7 冰点反核，4态下原 Bear-Low 合并到 r4）
        "overlay_target": "r11",
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {"r11": 0.65}, "shrinkage": 0.6},
            "trigger":  {"total_gte": 120, "p_overlay": {"r11": 0.35}, "shrinkage": 0.6},
            "fail":     {"keys_gte": {"continue_decline": 1}, "p_overlay": {}, "shrinkage": 0.3},
        },
    },
    "T3": {  # RECOVERY → BREAKOUT（§4.10.8 主升确立，不依赖基态语义）
        "overlay_target": "r12",
        "stages": {
            "strong_confirm": {"total_gte": 200, "p_overlay": {}, "shrinkage": 1.0},
            "confirm":        {"keys_gte": {"volume_price": 60, "ma_trend": 50, "money_effect": 50},
                               "p_overlay": {}, "shrinkage": 0.85},
            "trigger":        {"keys_gte": {"sentiment": 60, "mainline": 60, "leader": 60},
                               "p_overlay": {"r12": 0.55}, "shrinkage": 0.7},
            "fail":           {"keys_gte": {"one_day_mainline": 1}, "p_overlay": {"r11": 0.60}, "shrinkage": 0.6},
        },
    },
    "T4": {  # 牛市态(r3) 赶顶（§4.8 疯狂期赶顶，4态下无 Bull-Med/Bull-High 细分，改为 r3 内部赶顶信号）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.85},
            "trigger":  {"total_gte": 120, "p_overlay": {}, "shrinkage": 0.85},
            "fail":     {"keys_gte": {"shrink_flat": 1}, "p_overlay": {}, "shrinkage": 0.85},
        },
    },
    "T5": {  # 牛市态(r3) → 熊市态(r4) 逃顶（§4.11.8 逃顶退潮，4态下原 Bull-High→Bear-Med 映射为 r3→r4）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.6},
            "trigger":  {"keys_gte": {"leader_break": 60}, "p_overlay": {}, "shrinkage": 0.6},
            "fail":     {"keys_gte": {"rebound_wrap": 1}, "p_overlay": {}, "shrinkage": 0.85},
        },
    },
    "T6": {  # 熊市态(r4) 冰点（§4.7 退潮冰点，4态下无 Bear-Med/Bear-Low 细分，改为 r4 内部冰点信号）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.3},
            "trigger":  {"total_gte": 120, "p_overlay": {}, "shrinkage": 0.3},
            "fail":     {"keys_gte": {"sudden_volume": 1}, "p_overlay": {"r11": 0.40}, "shrinkage": 0.6},
        },
    },
    "S1": {  # Any → CRISIS（§4.9 VIX Panic + 相关性 + 流动性，不依赖基态语义）
        "overlay_target": "r10",
        "stages": {
            "confirm":  {"keys_gte": {"vix_panic": 60, "correlation": 60, "liquidity": 60},
                         "p_overlay": {"r10": 0.80}, "shrinkage": 0.3},
            "trigger":  {"keys_gte": {"vix_panic": 60, "correlation": 60},
                         "p_overlay": {"r10": 0.60}, "shrinkage": 0.3},
            "fail":     {"keys_gte": {"flash_recover": 1}, "p_overlay": {}, "shrinkage": 0.6},
        },
    },
    "S2": {  # CRISIS → RECOVERY（§4.12.8 八维度见底，不依赖基态语义）
        "overlay_target": "r11",
        "stages": {
            # P1-E9e：three_yang 升级 6 维分级后门槛 1→2（标准红三兵及以上）
            "strong_confirm": {"total_gte": 250, "keys_gte": {"spring": 1, "three_yang": 2},
                               "p_overlay": {"r11": 0.80}, "shrinkage": 0.7},
            # P1-E9d：confirm 析取通路——(wyckoff≥60 ∨ breadth_thrust≥60) ∧ 共同必要条件。
            # V 反转/政策型复苏不走 Wyckoff 吸筹（wyckoff 合法偏低），breadth_thrust 补盲区
            "confirm":        {"keys_or_gte": {"wyckoff": 60, "breadth_thrust": 60},
                               "keys_gte": {"policy": 40, "valuation": 40, "fund": 50},
                               "p_overlay": {"r11": 0.65}, "shrinkage": 0.6},
            "trigger":        {"keys_gte": {"capitulation": 60, "vix": 40, "bad_news_flat": 40},
                               "p_overlay": {"r11": 0.40}, "shrinkage": 0.4},
            "fail":           {"keys_gte": {"break_sc_low": 1, "vix_new_high": 1, "fund_outflow": 1},
                               "p_overlay": {"r10": 0.60}, "shrinkage": 0.3},
        },
    },
}
# 阶段判定顺序（从高到低）
_STAGE_ORDER: tuple[str, ...] = ("strong_confirm", "confirm", "trigger", "fail")


@dataclass(frozen=True)
class RegimeProbabilities:
    """7 维灰度概率分布（CTR-SIG-012）。

    满足 11_regime_backtest_validation_plan 验证需求 ①：输出 7 维概率分布（非硬标签），供 B1 校准度 / B2 CRPS。
    probabilities 必须 Σ=1.0（INVARIANTS）。
    """

    probabilities: dict[str, float]          # {r1..r4, r10..r12: P(ri)}，Σ=1.0
    hmm_probabilities: dict[str, float]      # {r1..r4: P_hmm(ri)}（归因用）
    overlay_probabilities: dict[str, float]  # {r10..r12: P_overlay(ri)}（归因用）
    dominant_regime: str                     # max(P) 对应的态
    dominant_frequency: float                # dominant_regime 历史频率（稀有态判断用）
    confidence: float                        # max(P) 值
    timestamp: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class ShrinkageResult:
    """Shrinkage 风险节流因子（CTR-SIG-014）。

    满足 11_regime_backtest_validation_plan 验证需求 ②：shrinkage_enabled 可开关。
    - True  → value = ConfidenceSignal × RiskSignal
    - False → value = 1.0（C1 开/关对比基准）
    value ≤ 1.0（只减不增，INVARIANTS）。
    """

    value: float                  # Shrinkage 最终值，≤1.0
    confidence_signal: float      # max(P) → 4 档映射 + 稀有态折扣
    risk_signal: float            # 13 参数聚合
    shrinkage_enabled: bool       # 验证开关（C1 一票否决）
    timestamp: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class TransitionTriggered:
    """8 转换触发记录（E-SIG-01）。

    满足 11_regime_backtest_validation_plan 验证需求 ③：8 转换触发可记录，供 B4 转换触发准确性。
    """

    transition_type: str          # T1-T6 / S1 / S2
    timestamp: datetime
    score_breakdown: dict[str, float]  # 各维度评分明细（如 S2 八维度）
    triggered: bool               # 是否达到触发阈值
    confirmed: bool               # 是否达到确认阈值
    stage: str                    # strong_confirm/confirm/trigger/fail/none
    total_score: float            # 总分（score_breakdown 求和）
    schema_version: str = "1.0"


@dataclass(frozen=True)
class RegimeSnapshot:
    """Regime 快照（E-SIG-02，归因用）。"""

    probabilities: RegimeProbabilities
    shrinkage: ShrinkageResult
    transitions: list[TransitionTriggered] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


# ── 错误契约（blueprint §5）──────────────────────────────────────────


class RegimeFeatureError(ZephyrBaseError):
    """ZA-REGIME-0001: RegimeFeatures 格式非法/缺失必需字段。"""


class HMMFittingError(ZephyrBaseError):
    """ZA-REGIME-0002: HMM 拟合失败（特征缺失/NaN/不收敛/hmmlearn 不可用）。"""


class ShrinkageComputationError(ZephyrBaseError):
    """ZA-REGIME-0003: ConfidenceSignal/RiskSignal 计算异常。"""


class OverlayRuleError(ZephyrBaseError):
    """ZA-REGIME-0004: 覆盖层规则计算异常（评分维度缺失/阈值非法）。"""


class ProbabilityNormalizationError(ZephyrBaseError):
    """ZA-REGIME-0005: 7 维归一化失败（Σ≠1 / 含 NaN）。"""


class RegimeDetector:
    """7 态 Regime 检测器（MOD-REGIME-001）。

    使用方式：
        detector = RegimeDetector(hmm_params={"n_states": 4}, shrinkage_enabled=True)
        detector.fit(train_features)              # walk-forward 季度重拟合
        probs, shrinkage = detector.detect(features, overlay_signals, risk_inputs)

    降级：hmmlearn 不可用 → fit 标记 degraded，detect 返回 HMM 均匀分布（§7.4）。
    """

    def __init__(
        self,
        hmm_params: dict[str, Any] | None = None,
        shrinkage_enabled: bool = True,
        state_frequencies: dict[str, float] | None = None,
        temperature: float = 1.0,
        overlay_gated: bool = True,
    ) -> None:
        """初始化 Regime 检测器。

        Args:
            hmm_params: HMM 超参（n_states=4, covariance_type, n_iter 等）。
            shrinkage_enabled: Shrinkage 开关（验证用，默认 True）。
                11_regime_backtest_validation_plan C1 开/关对比一票否决——False 时 Shrinkage=1.0。
            state_frequencies: 各态历史频率（稀有态判断用），未提供时按 Viterbi 统计估计。
            temperature: HMM 概率温度缩放参数（13_regime_phase3_engineering_plan §2.2 P0-E2 Stage 1）。
                T=1.0（默认）不缩放；T>1 降温（摊平分布，缓解 GaussianHMM full
                covariance 后验过尖——B1 实测 80-100% 桶预测 0.982 实际 0.523）；
                T<1 升温（锐化，一般不用）。对 HMM 后验做 softmax(log P / T) ≡
                P^(1/T)/ΣP^(1/T)，是"tempering"——数学有效但非 Guo2017 严格 Brier
                最优（标准 TS 需对 pre-softmax logits 操作，HMM log_proba 是对数后验）。
                正式的 T 学习（IS 数据最小化 BCE）见 13_regime_phase3_engineering_plan §2.2.6 Step 3。
            overlay_gated: overlay #1 门控开关（#ARCH-REGIME-OVERLAY-001 方案A治本）。
                True（默认）→ overlay 仅在危机期（#1<1.0）生效，非危机期屏蔽 overlay 概率
                注入（overlay_probs 置零）——避免 T1/S1 在非危机期假阳性触发系统性压仓致
                Sharpe 退化 0.02。转换评估记录（_last_transitions）始终保留，确保 S2
                (CRISIS→RECOVERY) 在危机结束（#1≥1.0）时点的触发能被 B4 验证捕获。
                与 _compute_risk_signal 的 #1 门控对齐（#1>=1.0 时 RiskSignal=1.0）。
                False → overlay 全程生效（ungated，诊断用，如 dump_overlay_triggers.py）。
        """
        self.hmm_params = hmm_params or {"n_states": 4, "covariance_type": "full", "n_iter": 100}
        self.shrinkage_enabled = shrinkage_enabled
        self.temperature = float(temperature)
        self.overlay_gated = overlay_gated
        self._hmm_model: Any = None  # hmmlearn GaussianHMM，fit() 后赋值
        self._hmm_degraded: bool = False  # hmmlearn 不可用 / 拟合失败标记
        # 各态历史频率（稀有态判断用），默认按 13_regime_phase3_engineering_plan §2.1 Viterbi 全历史统计
        # r1 低波震荡 27.6% / r2 中波震荡 37.4% / r3 牛市 14.9% / r4 熊市 20.2%
        # overlay 态 r10-r12 为规则触发，频率低（稀有态折扣生效）
        self._state_frequencies: dict[str, float] = dict(state_frequencies or {
            "r1": 0.28, "r2": 0.37, "r3": 0.15, "r4": 0.20,
            "r10": 0.02, "r11": 0.02, "r12": 0.01,
        })
        self._last_transitions: list[TransitionTriggered] = []  # 最近一次 detect 的转换事件

    # ── 公共接口 ──────────────────────────────────────────────────────

    def detect(
        self,
        regime_features: dict[str, Any],
        overlay_signals: dict[str, Any],
        risk_signal_inputs: dict[str, Any],
    ) -> tuple[RegimeProbabilities, ShrinkageResult]:
        """主入口：输出 7 维灰度概率 + Shrinkage。

        满足 11_regime_backtest_validation_plan 验证需求 ①②：7 维概率分布 + Shrinkage 可开关。
        供 RegimeMetaAllocator (MOD-PA-007) 消费。

        Args:
            regime_features: HMM 特征（波动率分位/趋势斜率/相关性矩阵/涨跌家数/量能异动）。
            overlay_signals: 覆盖层信号，结构 {"transitions": {T_id: {dim: score}}}。
            risk_signal_inputs: RiskSignal 13 参数输入，结构 {"params": {#id: coef}, "opportunity": {...}}。

        Returns:
            (RegimeProbabilities, ShrinkageResult)
        """
        # 子模块①：HMM 4态
        hmm_probs = self._run_hmm(regime_features)
        # 子模块②：覆盖层 3 特殊态 + 8 转换评分（始终评估，记录 _last_transitions 供 B4 验证）
        overlay_probs = self._run_overlay(overlay_signals)
        # 方案A门控（#ARCH-REGIME-OVERLAY-001）：overlay 仅在危机期（#1<1.0）生效。
        # 非危机期屏蔽 overlay 概率注入（避免 T1/S1 假阳性触发系统性压仓致 Sharpe 退化
        # 0.02），但保留转换评估记录（_last_transitions）——S2(CRISIS→RECOVERY) 在危机
        # 结束时触发，恰好是 #1≥1.0 时点，若在入口清空 overlay_signals 会跳过 S2 转换
        # 评估，致 B4 验证 S2 recovery 0/3 漏触发（Phase 2 不闭环）。故门控改为在
        # _run_overlay 之后屏蔽概率注入，与 RiskSignal #1 门控（#1>=1.0 时=1.0）对齐。
        if self.overlay_gated:
            _params = (risk_signal_inputs or {}).get("params") or {}
            if float(_params.get(1, 1.0)) >= 1.0:
                overlay_probs = {s: 0.0 for s in OVERLAY_STATES}
        # 7 维合并归一化
        probs = self._merge_probabilities(hmm_probs, overlay_probs)
        # 子模块③④⑤：Shrinkage 链
        confidence = self._compute_confidence_signal(probs)
        risk = self._compute_risk_signal(risk_signal_inputs)
        shrinkage = self._compute_shrinkage(confidence, risk)
        return probs, shrinkage

    def fit(self, train_features: dict[str, Any]) -> None:
        """HMM 拟合（walk-forward 季度重拟合）。

        满足 11_regime_backtest_validation_plan 验证需求 ④：hmmlearn GaussianHMM 4 态 walk-forward。

        Args:
            train_features: {"X": np.ndarray (T, F), "lengths": list[int]} 序列特征。
                X 为观测矩阵（T 个时间步 × F 个特征），lengths 为多序列长度（可选）。

        Raises:
            HMMFittingError: 特征缺失/含 NaN/不收敛。
        """
        try:
            from hmmlearn.hmm import GaussianHMM  # lazy import，hmmlearn 不可用时降级
        except Exception as exc:  # pragma: no cover
            self._hmm_degraded = True
            self._hmm_model = None
            raise HMMFittingError(
                "hmmlearn 不可用，HMM 降级为均匀分布（blueprint §7.4）"
            ) from exc

        X = train_features.get("X")
        if X is None:
            raise HMMFittingError("train_features 缺少 'X' 观测矩阵")
        try:
            import numpy as np
            if not isinstance(X, np.ndarray):
                X = np.asarray(X, dtype=float)
            if X.ndim != 2:
                raise HMMFittingError(f"X 维度应为 2D (T, F)，实际 {X.ndim}D")
            if not np.isfinite(X).all():
                raise HMMFittingError("X 含 NaN/Inf，无法拟合")
        except HMMFittingError:
            raise
        except Exception as exc:
            raise HMMFittingError(f"X 校验失败: {exc}") from exc

        n_states = int(self.hmm_params.get("n_states", 4))
        n_init = int(self.hmm_params.get("n_init", 3))
        base_seed = int(self.hmm_params.get("random_state", 42))
        lengths = train_features.get("lengths")
        # 多次拟合取 log-likelihood 最高的（EM 局部最优问题，单次 fit 不稳定）
        # 2026-08-06 C1 验证发现：random_state 固定仍因 EM 数值敏感性收敛到不同解，
        # 导致 Shrinkage schedule 不可复现（均值 0.818 vs 0.589）。n_init 取最优解稳定结果。
        best_model = None
        best_score = -np.inf
        last_exc: Exception | None = None
        for k in range(max(1, n_init)):
            try:
                m = GaussianHMM(
                    n_components=n_states,
                    covariance_type=self.hmm_params.get("covariance_type", "full"),
                    n_iter=self.hmm_params.get("n_iter", 100),
                    random_state=base_seed + k,
                )
                if lengths is not None:
                    m.fit(X, lengths=lengths)
                    score = float(m.score(X, lengths=lengths))
                else:
                    m.fit(X)
                    score = float(m.score(X))
                if score > best_score:
                    best_score = score
                    best_model = m
            except Exception as exc:
                last_exc = exc
        if best_model is None:
            self._hmm_degraded = True
            self._hmm_model = None
            raise HMMFittingError(f"GaussianHMM.fit 不收敛: {last_exc}") from last_exc
        self._hmm_model = best_model
        self._hmm_degraded = False

    def predict_log_proba(self, X: np.ndarray) -> np.ndarray:
        """返回 HMM 对数后验概率矩阵 (T, n_states)——校准器输入（13_regime_phase3_engineering_plan §2.2.6 Step 1）。

        hmmlearn 的 predict_proba(X) 返回 P(state|X) 后验概率矩阵，取 np.log()
        得到对数后验。加 epsilon 防 log(0)。Temperature Scaling 对此做
        softmax(log_proba/T) 是 tempering（§2.2.3 注释：数学有效但非 Guo2017
        严格 Brier 最优，因 HMM log_proba 是对数后验非 pre-softmax logits）。

        ⚠️ 返回**原始** log_proba，不应用 self.temperature——校准器的
        TemperatureCalibrator 会从 IS 数据学习自己的 T 参数（BCE 最小化），
        self.temperature 是 detect 路径（_run_hmm）的手动 tempering，两机制独立。

        降级（hmmlearn 不可用 / 未 fit）：返回均匀分布的 log，即 log(1/n_states)。

        Args:
            X: 观测矩阵 (T, F)，同 fit() 的特征格式。

        Returns:
            (T, n_states) 对数后验概率矩阵。
        """
        import numpy as np

        if X is None:
            raise HMMFittingError("predict_log_proba: X 为 None")
        if not isinstance(X, np.ndarray):
            X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        n_states = len(HMM_STATES)
        if self._hmm_model is None or self._hmm_degraded:
            # 降级：均匀分布的 log 概率
            return np.full((X.shape[0], n_states), np.log(1.0 / n_states))

        try:
            proba = self._hmm_model.predict_proba(X)  # (T, n_states)
            return np.log(proba + 1e-30)  # 加 epsilon 防 log(0)
        except Exception as exc:
            _logger.warning("predict_log_proba 推断异常，降级均匀分布: %s", exc)
            return np.full((X.shape[0], n_states), np.log(1.0 / n_states))

    def record_transition(
        self, transition_type: str, score_breakdown: dict[str, float]
    ) -> TransitionTriggered:
        """记录 8 转换触发事件（动态评分制聚合）。

        满足 11_regime_backtest_validation_plan 验证需求 ③：8 转换触发可记录，供 B4 转换触发准确性。

        Args:
            transition_type: T1-T6 / S1 / S2（不在 TRANSITIONS 中抛 ValueError）。
            score_breakdown: 各维度分值明细（如 S2 的 {capitulation, wyckoff, vix, ...}）。

        Returns:
            TransitionTriggered：含 stage（strong_confirm/confirm/trigger/fail/none）+ 总分。
        """
        if transition_type not in TRANSITIONS:
            raise ValueError(f"未知转换类型 {transition_type}，合法值 {TRANSITIONS}")
        if not isinstance(score_breakdown, dict):
            raise OverlayRuleError(f"{transition_type} score_breakdown 必须为 dict")

        total = float(sum(v for v in score_breakdown.values() if isinstance(v, (int, float))))
        cfg = TRANSITION_CONFIG.get(transition_type, {})
        stages = cfg.get("stages", {})
        stage = "none"
        for cand in _STAGE_ORDER:
            cond = stages.get(cand)
            if cond and self._eval_stage(score_breakdown, total, cond):
                stage = cand
                break
        return TransitionTriggered(
            transition_type=transition_type,
            timestamp=datetime.now(),
            score_breakdown=dict(score_breakdown),
            triggered=stage in ("trigger", "confirm", "strong_confirm"),
            confirmed=stage in ("confirm", "strong_confirm"),
            stage=stage,
            total_score=total,
        )

    # ── 子模块 ① HMM 4态 ─────────────────────────────────────────────

    def _run_hmm(self, regime_features: dict[str, Any]) -> dict[str, float]:
        """子模块①：HMM 4态推断，输出 P_hmm(r1)..P_hmm(r4)，Σ=1.0。

        降级：_hmm_model is None（未 fit / hmmlearn 不可用）→ 均匀分布 1/4（§7.4）。
        """
        n_states = len(HMM_STATES)
        if self._hmm_model is None or self._hmm_degraded:
            return {s: 1.0 / n_states for s in HMM_STATES}

        X = regime_features.get("X")
        if X is None:
            # 缺特征时降级（不抛错，保证 detect 可用）
            return {s: 1.0 / n_states for s in HMM_STATES}
        try:
            import numpy as np
            if not isinstance(X, np.ndarray):
                X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(1, -1)
            # predict_proba 返回 (T, n_states)，取最后一步（因果 Viterbi 防前视）
            probs = self._hmm_model.predict_proba(X)
            last = probs[-1]
            if len(last) != n_states:
                # 状态数不匹配，降级
                return {s: 1.0 / n_states for s in HMM_STATES}
            # 温度缩放（13_regime_phase3_engineering_plan §2.2.3 tempering）：对 HMM 后验做
            # softmax(log P / T) ≡ P^(1/T) / Σ P^(1/T)。T>1 降温摊平分布，
            # 缓解 GaussianHMM full covariance 后验过尖（B1 实测过度自信）。
            # 数值稳定实现：log-sum-exp 减最大值。T=1.0 时恒等（短路跳过省算）。
            if self.temperature != 1.0:
                if self.temperature <= 0.0:
                    # 非法温度，降级均匀分布（防御）
                    return {s: 1.0 / n_states for s in HMM_STATES}
                log_p = np.log(np.clip(last, 1e-12, 1.0))
                scaled = log_p / self.temperature
                scaled -= np.max(scaled)  # 数值稳定
                last = np.exp(scaled)
                last /= np.sum(last)
            return {HMM_STATES[i]: float(last[i]) for i in range(n_states)}
        except Exception:
            # 推断异常降级为均匀分布，保证 detect 鲁棒
            return {s: 1.0 / n_states for s in HMM_STATES}

    # ── 子模块 ② D-SIGNAL-68 覆盖层 ──────────────────────────────────

    def _run_overlay(self, overlay_signals: dict[str, Any]) -> dict[str, float]:
        """子模块②：3 特殊态（CRISIS/RECOVERY/BREAKOUT）规则触发 + 8 转换评分。

        输出 P_overlay(r10..r12)，并内部调用 record_transition() 记录 8 转换。
        无转换触发时返回全 0（退化为纯 HMM）。

        overlay_signals 结构：{"transitions": {T_id: {dim: score}, ...}}
        """
        transitions_in: dict[str, dict[str, float]] = (
            overlay_signals.get("transitions") if isinstance(overlay_signals, dict) else None
        ) or {}
        recorded: list[TransitionTriggered] = []
        # 每个特殊态取所有相关转换里最高的 p_overlay（后发覆盖先发）
        overlay_best: dict[str, float] = {"r10": 0.0, "r11": 0.0, "r12": 0.0}
        for tid, breakdown in transitions_in.items():
            if tid not in TRANSITIONS or not isinstance(breakdown, dict):
                continue
            try:
                trig = self.record_transition(tid, breakdown)
            except (ValueError, OverlayRuleError):
                continue
            recorded.append(trig)
            if trig.stage == "none":
                continue
            stage_cfg = TRANSITION_CONFIG[tid]["stages"][trig.stage]
            for state, p in stage_cfg.get("p_overlay", {}).items():
                if state in overlay_best and p > overlay_best[state]:
                    overlay_best[state] = float(p)
        self._last_transitions = recorded
        return overlay_best

    # ── 子模块 ③④⑤ Shrinkage 链 ─────────────────────────────────────

    def _merge_probabilities(
        self, hmm_probs: dict[str, float], overlay_probs: dict[str, float]
    ) -> RegimeProbabilities:
        """7 维合并归一化（blueprint §3.3）：覆盖层概率压缩 HMM 概率质量。

            overlay_mass = Σ P_overlay(r10..r12)
            hmm_scale = 1 − overlay_mass
            P(r1..r4) = P_hmm(r_i) × hmm_scale
            P(r10..r12) = P_overlay(r_i)
            normalize → Σ=1.0
        """
        overlay_mass = sum(overlay_probs.get(s, 0.0) for s in OVERLAY_STATES)
        if overlay_mass > 1.0:
            # 覆盖层总概率超 1（多转换同时触发），等比压缩回 1.0
            overlay_mass = 1.0
            scale = 1.0 / sum(overlay_probs.get(s, 0.0) for s in OVERLAY_STATES)
            overlay_probs = {s: overlay_probs.get(s, 0.0) * scale for s in OVERLAY_STATES}
        hmm_scale = 1.0 - overlay_mass

        merged: dict[str, float] = {}
        for s in HMM_STATES:
            merged[s] = hmm_probs.get(s, 0.0) * hmm_scale
        for s in OVERLAY_STATES:
            merged[s] = overlay_probs.get(s, 0.0)

        merged = self._normalize(merged)
        dominant = max(merged, key=lambda k: merged[k])
        confidence = merged[dominant]
        freq = self._state_frequencies.get(dominant, 0.0)
        return RegimeProbabilities(
            probabilities=merged,
            hmm_probabilities=dict(hmm_probs),
            overlay_probabilities=dict(overlay_probs),
            dominant_regime=dominant,
            dominant_frequency=freq,
            confidence=confidence,
            timestamp=datetime.now(),
        )

    def _compute_confidence_signal(self, probs: RegimeProbabilities) -> float:
        """子模块③：max(P) → 4 档映射 × 稀有态折扣（30_multi_strategy_concurrency §2.2 / 模块 docstring ③）。

        ConfidenceSignal = base_confidence(max(P)) × rarity_discount(dominant_frequency)

        - base: max(P) 四档映射（HMM 对当前态的自信程度）
        - rarity: 稀有态不确定性折扣（稀有态 = HMM 见过少 = 自信度打折）

        设计原则：ConfidenceSignal 只度量"HMM 有多自信"，不度量"市场有多危险"。
        市场风险由 RiskSignal（子模块④，feature-risk / 13 参数）统一承载。
        Shrinkage = ConfidenceSignal × RiskSignal，两者职责正交、不重复计数。

        C1 验证 2026-08-06 修正：此前在 ConfidenceSignal 中乘以 state_risk_factor
        （_STATE_RISK_FACTORS），存在两个致命缺陷：
          ① HMM 状态标签任意性：无监督 HMM 的 r1-r9 标签在 walk-forward 各季
             refit 间无一致语义（r1 本季=Bull-Low，下季可能=Bear-High），
             按数字标签套风险因子 = 随机惩罚。
          ② 永久中性态惩罚：r4/r5/r6（震荡态）state_risk=0.70-0.90，而 A 股
             长期处于震荡市 → 平时永久压仓 10-30%，牛市也跟着砍 → 收益崩塌
             （C1 实测 Sharpe 0.37→0.10）。
        危机保护改由 feature_risk 承担（vol_pct + slope，可靠信号，非任意标签）：
        高波 + 下跌 → RiskSignal=0.3-0.5，Shrinkage 自然走低。

        最低 0.7 × 0.7 = 0.49（低置信度 + 稀有态）；危机时再乘 RiskSignal=0.3 → 0.147。
        """
        max_p = probs.confidence
        base = 0.3
        for bound, coef in _CONFIDENCE_BANDS:
            if max_p >= bound:
                base = coef
                break
        rarity = 0.7
        for bound, coef in _RARITY_BANDS:
            if probs.dominant_frequency >= bound:
                rarity = coef
                break
        return base * rarity

    def _compute_risk_signal(self, risk_inputs: dict[str, Any]) -> float:
        """子模块④：13 参数聚合（10_regime_detector_spec §5.3.3）。

        RiskSignal = clamp[0.30, RiskBase × 共振惩罚 + 机会恢复, 1.00]
          RiskBase = #1 门控 + min(11 个风险参数系数 #1-10/#12)
          共振惩罚 = 1 − 0.05 × max(0, 异常参数数 − 1)，下限 ×0.80
          机会恢复 = #11 鬼故事抵消 + #13 利空不跌抵消，上限 +0.25

        #1 门控（C1 验证 2026-08-06 二次调优引入）：
          #1（realized_vol）是 Phase 1 验证过的主风险信号，附加参数（#2-#10/#12）
          是 #1 的"深化器"而非"替代者"。当 #1=1.0（无风险）时，附加参数不能独自
          创造收缩——避免附加参数在非危机日误触发（#7 广度普跌 12.7%、#3 破前低 5.3%
          等）经 min() 聚合 + EMA 平滑后扩散到 99.6% 日子，致 Sharpe 从 Phase 1 的
          0.2678 退化至 0.2464。当 #1<1.0（已检测到风险）时，附加参数可加深收缩
          （min(all) ≤ #1），提供多层危机保护。这保证 Phase 2a risk_base ≤ Phase 1
          risk_base（危机区只更严不更松），同时非危机日 ≈ Phase 1（不退化）。

        risk_inputs 结构：
            {"params": {1: 0.85, 2: 1.0, ..., 12: 0.6},  # #1-10/#12 系数
             "opportunity": {"news_ghost": 0.10, "bad_news_flat": 0.15}}  # #11/#13 抵消值
        缺失时降级为 RiskSignal=1.0（§7.4）。
        """
        if not isinstance(risk_inputs, dict) or not risk_inputs:
            return 1.0
        params: dict[int, float] = risk_inputs.get("params") or {}
        if not params:
            return 1.0
        # #1 门控：主风险信号未触发 → 附加参数不参与（避免假阳性致 Sharpe 退化）
        primary = float(params.get(1, 1.0))
        if primary >= 1.0:
            return 1.0
        # #1 已触发 → 附加参数可加深收缩（min(all) ≤ #1）
        risk_param_ids = [i for i in list(range(1, 11)) + [12]]
        coefs = [float(params[i]) for i in risk_param_ids if i in params and params[i] is not None]
        if not coefs:
            return 1.0
        risk_base = min(coefs)
        # 共振惩罚：异常参数数（系数<1.0）每多一个再扣 5%，下限 ×0.80
        anomaly_count = sum(1 for c in coefs if c < 1.0)
        resonance = max(0.80, 1.0 - 0.05 * max(0, anomaly_count - 1))
        # 机会恢复：#11 鬼故事 + #13 利空不跌，上限 +0.25
        opp = risk_inputs.get("opportunity") or {}
        recovery = 0.0
        if isinstance(opp, dict):
            recovery = float(opp.get("news_ghost", 0.0)) + float(opp.get("bad_news_flat", 0.0))
        recovery = min(recovery, 0.25)
        risk = risk_base * resonance + recovery
        return max(0.30, min(1.00, risk))

    def _compute_shrinkage(
        self, confidence: float, risk: float
    ) -> ShrinkageResult:
        """子模块⑤：Shrinkage = ConfidenceSignal × RiskSignal（可开关）。

        - shrinkage_enabled=True  → value = confidence × risk
        - shrinkage_enabled=False → value = 1.0（C1 验证基准）
        value ≤ 1.0（只减不增，INVARIANTS）。
        """
        if not self.shrinkage_enabled:
            return ShrinkageResult(
                value=1.0, confidence_signal=confidence, risk_signal=risk,
                shrinkage_enabled=False, timestamp=datetime.now(),
            )
        value = confidence * risk
        if value > 1.0:  # 理论上不会（两者均 ≤1.0），防浮点误差
            value = 1.0
        return ShrinkageResult(
            value=value, confidence_signal=confidence, risk_signal=risk,
            shrinkage_enabled=True, timestamp=datetime.now(),
        )

    # ── 辅助 ─────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(probs: dict[str, float]) -> dict[str, float]:
        """归一化到 Σ=1.0（防浮点误差）。全零时回退均匀分布。"""
        total = sum(probs.values())
        if not (total == total) or total <= 0:  # NaN 或全零
            n = len(probs)
            return {k: 1.0 / n for k in probs} if n else {}
        return {k: v / total for k, v in probs.items()}

    @staticmethod
    def _eval_stage(
        breakdown: dict[str, float], total: float, cond: dict[str, Any]
    ) -> bool:
        """阶段条件判定：total_gte 与 keys_gte（+keys_or_gte）同时满足（缺 key 视为不满足）。

        P1-E9d 析取逻辑（14_regime_s2_diagnosis §4.4）：keys_or_gte 内任一 key 达阈即
        通过（析取，缺 key 计 0.0）；与 keys_gte（合取，全满足才通过）并存时两组均须
        通过。用于 S2 confirm 的 V 反转通路——(wyckoff≥60 ∨ breadth_thrust≥60) ∧
        policy/valuation/fund 共同必要条件。
        """
        if total < float(cond.get("total_gte", 0)):
            return False
        or_keys = cond.get("keys_or_gte") or {}
        if or_keys and not any(
            float(breakdown.get(key, 0.0)) >= float(threshold)
            for key, threshold in or_keys.items()
        ):
            return False
        for key, threshold in (cond.get("keys_gte") or {}).items():
            if float(breakdown.get(key, 0.0)) < float(threshold):
                return False
        return True
