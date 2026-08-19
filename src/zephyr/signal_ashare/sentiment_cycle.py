# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/28_sentiment_cycle_trading.md §3.2-§3.10
# [MODULE] zephyr.signal_ashare.sentiment_cycle
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] (待 G07 相关性验证 / G08 打板 sleeve / 10_regime BM-SEL-03-B 软影响接线)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] phase_prob Σ=1；position_scale ∈[0,1]；PHASE_DISCIPLINE/STRATEGY_DEPLOYMENT_MATRIX 覆盖全 5 阶段；wrapper 无递归
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 序列长度不足→返回 none/空结果（不抛错）；非法 regime 态名→validate 问题清单
# [TESTS] tests/signal_ashare/test_sentiment_cycle.py
# [TTL] permanent
#
# [ALGO_FLOW]
# 层: 输入
# - id: I1  SentimentLocatorInput 多维可观测指标（涨跌停/连板梯队/炸板/溢价/换手/量能/龙虎榜/北向/昨日先验）
# 层: 算法
# - id: A1  locate_sentiment_phase：多维评分→贝叶斯+转移平滑→兜底(<60%回退收缩态)→可交易性+仓位缩放
# - id: A2  compute_sentiment_temperature：七维温度计→[0,100]
# - id: A3  detect_phase_transition：底反转/顶背离 先行+确认双判定
# - id: A4  PHASE_DISCIPLINE/apply_phase_discipline：五阶段买卖纪律硬约束
# - id: A5  SENTIMENT_TO_REGIME_MAP/apply_sentiment_soft_influence：情绪软调 12 态概率（弱静态 Phase 1）
# - id: A6  combine_sentiment_regime：alpha 缩放 × regime Shrinkage 乘法叠加
# - id: A7  STRATEGY_DEPLOYMENT_MATRIX：3 策略×5 阶段部署矩阵
# - id: A8  Hawkes 系 + analyze_sentiment_driven_correlation：η 分支比 + block-bootstrap 显著性
# 层: 输出
# - id: O1  5 维灰度概率/温度/转换信号/纪律/联合指令/部署策略/验证报告
# [/ALGO_FLOW]
"""情绪周期×交易决策标准函数集（28 号 memo §3.2-§3.10，设计态准入落码）。

8 个标准函数签名（§3.10，薄包装无递归）：
① classify_sentiment_phase → locate_sentiment_phase（§3.3）
② compute_sentiment_temperature（§3.2 增补）
③ locate_sentiment_phase（§3.3）
④ detect_phase_transition（§3.2.1）
⑤ get_phase_trading_discipline（§3.4）
⑥ evaluate_locator_accuracy（§3.10）
⑦ map_sentiment_to_regime → SENTIMENT_REGIME_MAPPING + apply_sentiment_soft_influence（§3.5）
⑧ get_strategy_deployment_by_phase → compute_strategy_deployment（§3.6.1）

命名注意：本模块 SentimentPhase（FREEZING/STARTING/FERMENTING/CONSENSUS/EBING，
28 号 memo 五段命名）与 market_sentiment_analyzer.SentimentPhase（4+1 硬标签）
/ youzi_relay_emotion_engine.EmotionPhase 是三个不同模块的各自枚举，
中文值一致（冰点/反核/主升/疯狂/退潮），消费方按模块路径引用，勿混用 import。

§3.5.2 映射表权重标定：SENTIMENT_TO_REGIME_MAP 为 Phase 1 弱静态映射经验值，
**待 Phase 2 各策略 3-6 月实盘后人工调参**（28 号 §6 待裁定-2）；
validate_sentiment_regime_map 为加载校验函数。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np


class SentimentPhase(Enum):
    """情绪周期五阶段——A 股短周期炒作微观视角（28 号 memo §3.2 统一命名）。

    游资圈对照（55188 2026-07/xueqiu 2026-06/eastmoney 2026-03）：
    启动/发酵/高潮/分歧/退潮 ≈ 反核/主升/疯狂/退潮前兆/退潮。
    """

    FREEZING = "冰点"  # 绝望期：地量大跌、恐慌一致看空、利好麻木
    STARTING = "反核"  # 希望期：止跌缩量反弹、局部赚钱效应、利好敏感
    FERMENTING = "主升"  # 乐观期：放量上涨、主线清晰、赚钱效应扩散
    CONSENSUS = "疯狂"  # 一致期：加速赶顶、连板高位、波动放大
    EBING = "退潮"  # 退潮期：涨停骤降、炸板率飙升、核按钮批量


@dataclass
class PhaseCharacteristics:
    """各阶段市场特征指标（memo §3.2 先验判据，定位器参考阈值）。"""

    phase: SentimentPhase
    limit_up_range: tuple[int, int]  # 涨停家数区间
    limit_down_range: tuple[int, int]  # 跌停家数区间
    consecutive_height: tuple[int, int]  # 连板高度区间（最高板）
    explosion_rate_range: tuple[float, float]  # 炸板率区间
    next_day_premium_range: tuple[float, float]  # 打板次日溢价区间
    turnover_desc: str
    fund_behavior: str
    essence: str


PHASE_CHARACTERISTICS: dict[SentimentPhase, PhaseCharacteristics] = {
    SentimentPhase.FREEZING: PhaseCharacteristics(
        phase=SentimentPhase.FREEZING, limit_up_range=(0, 20), limit_down_range=(10, 999),
        consecutive_height=(0, 2), explosion_rate_range=(0.40, 1.00),
        next_day_premium_range=(-0.05, -0.02),
        turnover_desc="地量，成交额较均值萎缩 50%+，换手率个股<1%",
        fund_behavior="散户恐慌割肉，机构观望，北向逆势小单流入",
        essence="空头力量衰竭，多头孕育，底部拐点前夜",
    ),
    SentimentPhase.STARTING: PhaseCharacteristics(
        phase=SentimentPhase.STARTING, limit_up_range=(20, 40), limit_down_range=(0, 10),
        consecutive_height=(2, 3), explosion_rate_range=(0.30, 0.40),
        next_day_premium_range=(-0.02, 0.01),
        turnover_desc="温和放量，较冰点提升 30%+，新题材冒头试盘",
        fund_behavior="先知先觉资金布局，散户犹豫，游资试错龙头",
        essence="情绪拐点确认，赚钱效应萌芽，主线酝酿期",
    ),
    SentimentPhase.FERMENTING: PhaseCharacteristics(
        phase=SentimentPhase.FERMENTING, limit_up_range=(40, 80), limit_down_range=(0, 5),
        consecutive_height=(4, 6), explosion_rate_range=(0.20, 0.30),
        next_day_premium_range=(0.02, 0.04),
        turnover_desc="放量上涨，较均值提升 20%+，板块形成梯队",
        fund_behavior="资金共识强，风险偏好拉满，打板/追高/低吸均赚钱",
        essence="趋势确立，主线明确，赚钱效应扩散",
    ),
    SentimentPhase.CONSENSUS: PhaseCharacteristics(
        phase=SentimentPhase.CONSENSUS, limit_up_range=(80, 999), limit_down_range=(0, 3),
        consecutive_height=(7, 999), explosion_rate_range=(0.00, 0.20),
        next_day_premium_range=(0.04, 0.08),
        turnover_desc="天量，板块全面爆发，后排跟风也涨停",
        fund_behavior="资金盲目乐观，物极必反，机构开始减持",
        essence="加速赶顶，波动放大，退潮风险积累",
    ),
    SentimentPhase.EBING: PhaseCharacteristics(
        phase=SentimentPhase.EBING, limit_up_range=(0, 30), limit_down_range=(15, 999),
        consecutive_height=(0, 3), explosion_rate_range=(0.50, 1.00),
        next_day_premium_range=(-0.08, -0.03),
        turnover_desc="流动性枯竭，核按钮批量出现，全线杀跌无抵抗",
        fund_behavior="空间板闷杀→跌停家数堆积→偶尔反抽→继续埋",
        essence="主线断裂，亏钱效应扩散，空仓为最优选择",
    ),
}

# 阶段顺序（转移平滑/相邻容错用）
PHASE_ORDER: list[SentimentPhase] = [
    SentimentPhase.FREEZING,
    SentimentPhase.STARTING,
    SentimentPhase.FERMENTING,
    SentimentPhase.CONSENSUS,
    SentimentPhase.EBING,
]


# ==================================================================
# §3.2 增补 情绪温度评分（标准签名②）
# ==================================================================
@dataclass
class SentimentTemperatureComponents:
    """情绪温度七维分项得分，每维归一化到 [0,1]。"""

    limit_up_breadth: float  # 涨停广度：涨停数/max(历史峰值,100)
    limit_down_fear: float  # 跌停恐惧：跌停数/max(历史峰值,50)
    consecutive_height: float  # 连板高度：最高连板数/7
    explosion_divergence: float  # 炸板背离：炸板率
    seal_consensus: float  # 封板共识：封板率
    advance_decline_ratio: float  # 涨跌比归一化 [0,1]
    ladder_completeness: float  # 梯队完整度：层数/6


SENTIMENT_TEMPERATURE_WEIGHTS: dict[str, float] = {
    "limit_up_breadth": 0.20,
    "limit_down_fear": 0.15,
    "consecutive_height": 0.15,
    "explosion_divergence": 0.15,
    "seal_consensus": 0.10,
    "advance_decline_ratio": 0.15,
    "ladder_completeness": 0.10,
}


@dataclass
class SentimentTemperatureOutput:
    """情绪温度综合评分输出。"""

    score: float  # 综合温度 [0,100]，越高越热
    components: SentimentTemperatureComponents
    weighted_scores: dict[str, float]
    phase_hint: SentimentPhase
    risk_level: str  # "low"/"medium"/"high"/"extreme"


def compute_sentiment_temperature(
    limit_up_count: int,
    limit_down_count: int,
    explosion_count: int,
    sealed_limit_up_count: int,
    consecutive_ladder: dict[int, int],
    advance_count: int,
    decline_count: int,
    historical_peak_limit_up: int = 100,
    historical_peak_limit_down: int = 50,
) -> SentimentTemperatureOutput:
    """七维 A 股情绪温度计 → [0,100] 综合评分（标准签名②，memo §3.2 增补）。

    反向指标（跌停恐惧/炸板背离）取 1-x。
    温度→阶段粗映射：<20 冰点 / <40 反核 / <70 主升 / <90 疯狂 / ≥90 退潮前兆。
    """
    limit_up_breadth = min(limit_up_count / max(historical_peak_limit_up, 1), 1.0)
    limit_down_fear = min(limit_down_count / max(historical_peak_limit_down, 1), 1.0)
    highest_consec = max(consecutive_ladder.keys()) if consecutive_ladder else 0
    consecutive_height = min(highest_consec / 7.0, 1.0)
    total_attempt = explosion_count + limit_up_count
    explosion_divergence = explosion_count / total_attempt if total_attempt > 0 else 0.0
    total_limit_up_attempt = sealed_limit_up_count + explosion_count
    seal_consensus = (
        sealed_limit_up_count / total_limit_up_attempt if total_limit_up_attempt > 0 else 0.0
    )
    total_ad = advance_count + decline_count
    raw_ad_ratio = (advance_count - decline_count) / total_ad if total_ad > 0 else 0.0
    advance_decline_ratio = (raw_ad_ratio + 1.0) / 2.0
    ladder_layers = sum(1 for k in consecutive_ladder.keys() if 2 <= k <= 7)
    ladder_completeness = min(ladder_layers / 6.0, 1.0)
    components = SentimentTemperatureComponents(
        limit_up_breadth, limit_down_fear, consecutive_height, explosion_divergence,
        seal_consensus, advance_decline_ratio, ladder_completeness,
    )
    values = {
        "limit_up_breadth": limit_up_breadth,
        "limit_down_fear": 1.0 - limit_down_fear,
        "consecutive_height": consecutive_height,
        "explosion_divergence": 1.0 - explosion_divergence,
        "seal_consensus": seal_consensus,
        "advance_decline_ratio": advance_decline_ratio,
        "ladder_completeness": ladder_completeness,
    }
    weighted_scores = {k: SENTIMENT_TEMPERATURE_WEIGHTS[k] * v for k, v in values.items()}
    score = max(0.0, min(100.0, sum(weighted_scores.values()) * 100.0))
    if score < 20.0:
        phase_hint, risk_level = SentimentPhase.FREEZING, "low"
    elif score < 40.0:
        phase_hint, risk_level = SentimentPhase.STARTING, "medium"
    elif score < 70.0:
        phase_hint, risk_level = SentimentPhase.FERMENTING, "medium"
    elif score < 90.0:
        phase_hint, risk_level = SentimentPhase.CONSENSUS, "high"
    else:
        phase_hint, risk_level = SentimentPhase.EBING, "extreme"
    return SentimentTemperatureOutput(score, components, weighted_scores, phase_hint, risk_level)


# ==================================================================
# §3.2.1 阶段转换检测（标准签名④）
# ==================================================================
@dataclass
class PhaseTransitionSignal:
    """阶段转换信号——"先行指标 + 确认信号"双重判定。"""

    transition_type: str  # "bottom_reversal"/"top_divergence"/"none"
    from_phase: SentimentPhase
    to_phase: SentimentPhase
    leading_indicator_triggered: bool
    confirmation_triggered: bool
    leading_evidence: dict[str, float]
    confirmation_evidence: dict[str, float]
    confidence: float  # [0,1]
    is_actionable: bool  # 先行+确认双触发


def detect_phase_transition(
    current_phase: SentimentPhase,
    explosion_rate_series: list[float],
    limit_up_count_series: list[int],
    consecutive_height_series: list[int],
    limit_down_count: int,
    nuclear_button_count: int,
    lookback_window: int = 5,
) -> PhaseTransitionSignal:
    """底反转与顶背离双重判定（标准签名④，memo §3.2.1）。

    底反转（FREEZING→STARTING）：先行=炸板率骤降（5 日均值-当日 ≥0.15）
      +涨停回暖（当日 ≥5 日均值 ×1.3）；确认=连板高度突破（当日 ≥近 5 日最高+1）
    顶背离（CONSENSUS→EBING）：先行=炸板率攀升（当日-5 日均值 ≥0.15）
      +连板见顶（当日 ≤近 5 日最高 ×0.6）；确认=核按钮 ≥10 或跌停 >50
    """
    signal = PhaseTransitionSignal(
        transition_type="none", from_phase=current_phase, to_phase=current_phase,
        leading_indicator_triggered=False, confirmation_triggered=False,
        leading_evidence={}, confirmation_evidence={}, confidence=0.0, is_actionable=False,
    )
    if len(explosion_rate_series) < lookback_window + 1:
        return signal
    recent_explosion_avg = sum(explosion_rate_series[-lookback_window - 1:-1]) / lookback_window
    recent_limit_up_avg = sum(limit_up_count_series[-lookback_window - 1:-1]) / lookback_window
    recent_consec_max = max(consecutive_height_series[-lookback_window - 1:-1])
    today_explosion = explosion_rate_series[-1]
    today_limit_up = limit_up_count_series[-1]
    today_consec = consecutive_height_series[-1]
    # ===== 底反转检测（FREEZING → STARTING）=====
    if current_phase == SentimentPhase.FREEZING:
        explosion_drop = recent_explosion_avg - today_explosion
        limit_up_recover_ratio = today_limit_up / max(recent_limit_up_avg, 1.0)
        leading_triggered = (explosion_drop >= 0.15) and (limit_up_recover_ratio >= 1.3)
        confirmation_triggered = today_consec >= recent_consec_max + 1
        leading_evidence = {
            "explosion_rate_drop": explosion_drop,
            "limit_up_recover_ratio": limit_up_recover_ratio,
        }
        confirmation_evidence = {
            "consecutive_height_today": float(today_consec),
            "consecutive_height_recent_max": float(recent_consec_max),
        }
        if leading_triggered or confirmation_triggered:
            confidence = (0.5 if leading_triggered else 0.0) + (0.5 if confirmation_triggered else 0.0)
            signal = PhaseTransitionSignal(
                transition_type="bottom_reversal",
                from_phase=SentimentPhase.FREEZING, to_phase=SentimentPhase.STARTING,
                leading_indicator_triggered=leading_triggered,
                confirmation_triggered=confirmation_triggered,
                leading_evidence=leading_evidence,
                confirmation_evidence=confirmation_evidence,
                confidence=confidence,
                is_actionable=(leading_triggered and confirmation_triggered),
            )
    # ===== 顶背离检测（CONSENSUS → EBING）=====
    elif current_phase == SentimentPhase.CONSENSUS:
        explosion_rise = today_explosion - recent_explosion_avg
        consec_decline_ratio = today_consec / max(recent_consec_max, 1.0)
        leading_triggered = (explosion_rise >= 0.15) and (consec_decline_ratio <= 0.6)
        confirmation_triggered = (nuclear_button_count >= 10) or (limit_down_count > 50)
        leading_evidence = {
            "explosion_rate_rise": explosion_rise,
            "consecutive_height_decline_ratio": consec_decline_ratio,
        }
        confirmation_evidence = {
            "nuclear_button_count": float(nuclear_button_count),
            "limit_down_count": float(limit_down_count),
        }
        if leading_triggered or confirmation_triggered:
            confidence = (0.5 if leading_triggered else 0.0) + (0.5 if confirmation_triggered else 0.0)
            signal = PhaseTransitionSignal(
                transition_type="top_divergence",
                from_phase=SentimentPhase.CONSENSUS, to_phase=SentimentPhase.EBING,
                leading_indicator_triggered=leading_triggered,
                confirmation_triggered=confirmation_triggered,
                leading_evidence=leading_evidence,
                confirmation_evidence=confirmation_evidence,
                confidence=confidence,
                is_actionable=(leading_triggered and confirmation_triggered),
            )
    return signal


# ==================================================================
# §3.3 情绪周期定位器（标准签名③，BM-SEL-23-B 升级版）
# ==================================================================
@dataclass
class SentimentLocatorInput:
    """情绪周期定位器输入——多维可观测指标（盘后可获取，T 日收盘后定位 T+1）。"""

    limit_up_count: int
    limit_down_count: int
    explosion_count: int
    consecutive_ladder: dict[int, int]  # {连板数: 家数}
    yesterday_consecutive: dict[int, int]
    daban_next_day_premium: float  # 打板次日平均溢价
    avg_turnover_rate: float  # 市场平均换手率
    market_amount_ratio_vs_ma20: float  # 成交额/20 日均量
    dragon_tiger_net_buy_ratio: float  # 龙虎榜净买率
    northbound_net_inflow: float  # 北向净流入（亿）
    yesterday_phase_prob: Optional[dict[SentimentPhase, float]] = None  # 昨日 5 维概率（先验）


@dataclass
class SentimentLocatorOutput:
    """情绪周期定位器输出——5 维灰度概率分布（10_regime §2.5.4 灰度裁定）。"""

    phase_prob: dict[SentimentPhase, float]  # Σ=1
    dominant_phase: SentimentPhase
    confidence: float  # max(P)
    is_tradable: bool
    position_scale: float  # 0.0-1.0
    evidence_scores: dict[str, float]
    fallback_triggered: bool  # 置信度<60%→默认保守


def locate_sentiment_phase(
    inp: SentimentLocatorInput,
    confidence_threshold: float = 0.60,
) -> SentimentLocatorOutput:
    """情绪周期定位器（标准签名③，memo §3.3）。

    四步：①多维指标评分 → ②先验+贝叶斯更新（转移平滑）→ ③兜底（置信度
    <threshold → 回退 FREEZING/EBING 收缩态，position_scale 强制 ≤0.3）→
    ④可交易性+仓位缩放。宁保守不激进：兜底只回退收缩态不回退扩张态。
    """
    # ===== 步骤 1：多维指标评分 =====
    yesterday_consec_total = sum(inp.yesterday_consecutive.values()) if inp.yesterday_consecutive else 0
    today_promoted = sum(inp.consecutive_ladder.get(k + 1, 0) for k in inp.yesterday_consecutive)
    promotion_rate = today_promoted / yesterday_consec_total if yesterday_consec_total > 0 else 0.0
    total_attempt = inp.explosion_count + inp.limit_up_count
    explosion_rate = inp.explosion_count / total_attempt if total_attempt > 0 else 0.0
    highest_consec = max(inp.consecutive_ladder.keys()) if inp.consecutive_ladder else 0
    evidence: dict[SentimentPhase, float] = {
        phase: _score_phase(
            target=phase, limit_up=inp.limit_up_count, limit_down=inp.limit_down_count,
            explosion_rate=explosion_rate, next_day_premium=inp.daban_next_day_premium,
            highest_consec=highest_consec, amount_ratio=inp.market_amount_ratio_vs_ma20,
        )
        for phase in SentimentPhase
    }
    # ===== 步骤 2：先验+贝叶斯更新 =====
    prior = (
        inp.yesterday_phase_prob
        if inp.yesterday_phase_prob is not None
        else {p: 0.2 for p in SentimentPhase}
    )
    smoothed_prior = _apply_transition_smoothing(prior, PHASE_ORDER, diag_weight=0.6)
    posterior = {p: max(smoothed_prior[p] * evidence[p], 1e-9) for p in SentimentPhase}
    total = sum(posterior.values())
    phase_prob = {p: v / total for p, v in posterior.items()}
    # ===== 步骤 3：兜底机制 =====
    dominant = max(phase_prob, key=phase_prob.get)
    confidence = phase_prob[dominant]
    fallback_triggered = False
    if confidence < confidence_threshold:
        fallback_triggered = True
        if evidence[SentimentPhase.EBING] > evidence[SentimentPhase.FREEZING]:
            dominant = SentimentPhase.EBING
            phase_prob = {p: (1.0 if p == SentimentPhase.EBING else 0.0) for p in SentimentPhase}
        else:
            dominant = SentimentPhase.FREEZING
            phase_prob = {p: (1.0 if p == SentimentPhase.FREEZING else 0.0) for p in SentimentPhase}
        confidence = 1.0  # 兜底后置为确定（position_scale 仍强收缩）
    # ===== 步骤 4：可交易性 + 仓位缩放 =====
    is_tradable, position_scale = _compute_tradability(
        dominant, confidence, fallback_triggered, promotion_rate, explosion_rate,
    )
    return SentimentLocatorOutput(
        phase_prob=phase_prob, dominant_phase=dominant, confidence=confidence,
        is_tradable=is_tradable, position_scale=position_scale,
        evidence_scores={p.name: v for p, v in evidence.items()},
        fallback_triggered=fallback_triggered,
    )


def _score_phase(
    target: SentimentPhase,
    limit_up: int,
    limit_down: int,
    explosion_rate: float,
    next_day_premium: float,
    highest_consec: int,
    amount_ratio: float,
) -> float:
    """单阶段证据评分——高斯隶属度多指标加权。

    权重：涨停数 0.25 + 跌停数 0.15 + 炸板率 0.20 + 次日溢价 0.20 + 连板高度 0.10 + 量能 0.10
    """
    ch = PHASE_CHARACTERISTICS[target]
    s_lu = _membership_in_range(limit_up, ch.limit_up_range)
    s_ld = _membership_in_range(limit_down, ch.limit_down_range)
    s_exp = _membership_in_range(explosion_rate, ch.explosion_rate_range)
    s_prem = _membership_in_range(next_day_premium, ch.next_day_premium_range)
    s_consec = _membership_in_range(highest_consec, ch.consecutive_height)
    if target == SentimentPhase.FREEZING:
        s_amt = 1.0 if amount_ratio < 0.5 else max(0.0, 1.0 - (amount_ratio - 0.5) / 0.5)
    elif target == SentimentPhase.STARTING:
        s_amt = 1.0 - abs(amount_ratio - 0.7) / 0.5
    elif target == SentimentPhase.FERMENTING:
        s_amt = 1.0 - abs(amount_ratio - 1.2) / 0.6
    elif target == SentimentPhase.CONSENSUS:
        s_amt = 1.0 if amount_ratio > 1.5 else max(0.0, (amount_ratio - 1.0) / 0.5)
    else:  # EBING
        s_amt = 1.0 if amount_ratio < 0.6 else max(0.0, 1.0 - (amount_ratio - 0.6) / 0.6)
    score = (
        0.25 * s_lu + 0.15 * s_ld + 0.20 * s_exp + 0.20 * s_prem
        + 0.10 * s_consec + 0.10 * max(0.0, min(1.0, s_amt))
    )
    return max(0.0, min(1.0, score))


def _membership_in_range(value: float, rng: tuple) -> float:
    """高斯隶属度：在区间内=1，越偏离越小。"""
    lo, hi = rng
    if lo <= value <= hi:
        return 1.0
    center = (lo + hi) / 2 if hi != 999 else lo
    span = max((hi - lo), 1.0) if hi != 999 else 10.0
    dist = abs(value - center)
    return math.exp(-((dist / span) ** 2))


def _apply_transition_smoothing(
    prior: dict[SentimentPhase, float],
    order: list[SentimentPhase],
    diag_weight: float = 0.6,
) -> dict[SentimentPhase, float]:
    """转移平滑——情绪周期有惯性：对角线 diag_weight，邻阶段各 (1-diag)/2。"""
    n = len(order)
    smoothed = {p: 0.0 for p in order}
    for i, p in enumerate(order):
        smoothed[p] += diag_weight * prior[p]
        neighbor_weight = (1.0 - diag_weight) / 2
        if i > 0:
            smoothed[order[i - 1]] += neighbor_weight * prior[p]
        else:
            smoothed[p] += neighbor_weight * prior[p]
        if i < n - 1:
            smoothed[order[i + 1]] += neighbor_weight * prior[p]
        else:
            smoothed[p] += neighbor_weight * prior[p]
    total = sum(smoothed.values())
    return {p: v / total for p, v in smoothed.items()} if total > 0 else smoothed


def _compute_tradability(
    dominant: SentimentPhase,
    confidence: float,
    fallback_triggered: bool,
    promotion_rate: float,
    explosion_rate: float,
) -> tuple[bool, float]:
    """可交易性 + 仓位缩放（memo §3.3 步骤 4）。"""
    base_scale = {
        SentimentPhase.FREEZING: 0.0,
        SentimentPhase.STARTING: 0.5,
        SentimentPhase.FERMENTING: 1.0,
        SentimentPhase.CONSENSUS: 0.5,
        SentimentPhase.EBING: 0.0,
    }
    if fallback_triggered:
        return False, 0.2
    discount = 0.5 + 0.5 * (confidence - 0.6) / 0.4 if confidence >= 0.6 else 0.5
    scale = base_scale[dominant] * discount
    if dominant in (SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS):
        is_tradable = True
    elif dominant == SentimentPhase.STARTING:
        is_tradable = promotion_rate >= 0.50
    else:
        is_tradable = False
    if explosion_rate > 0.70:  # 炸板率 >70% 强制不可交易（24 号 §3.10）
        is_tradable = False
        scale = min(scale, 0.1)
    return is_tradable, max(0.0, min(1.0, scale))


# ==================================================================
# §3.4 各阶段买卖纪律（标准签名⑤）
# ==================================================================
@dataclass
class PhaseTradingDiscipline:
    """各阶段买卖纪律——sleeve 内 alpha 择时硬约束。"""

    phase: SentimentPhase
    position_scale: float
    throttle_factor: float
    allow_new_open: bool
    strategy_affinity: dict[str, float]
    entry_discipline: str
    exit_discipline: str


PHASE_DISCIPLINE: dict[SentimentPhase, PhaseTradingDiscipline] = {
    SentimentPhase.FREEZING: PhaseTradingDiscipline(
        phase=SentimentPhase.FREEZING, position_scale=0.0, throttle_factor=0.0,
        allow_new_open=False,
        strategy_affinity={"daban": -1.0, "multifactor": +0.5, "event_driven": -0.5},
        entry_discipline="空仓防守，严禁抄底。多因子可开始左侧布局低估标的（估值分位<15%），但仓位≤1成试错",
        exit_discipline="所有短周期持仓无条件清仓，仅保留多因子底仓",
    ),
    SentimentPhase.STARTING: PhaseTradingDiscipline(
        phase=SentimentPhase.STARTING, position_scale=0.5, throttle_factor=0.5,
        allow_new_open=True,
        strategy_affinity={"daban": +0.3, "multifactor": +1.0, "event_driven": +0.5},
        entry_discipline="试错新题材首板或空间板，仓位2-3成。多因子左侧加仓低位横截面，事件驱动布局利好公告",
        exit_discipline="打板错了就砍，对了加仓。多因子持有不动，事件驱动按衰减曲线退出",
    ),
    SentimentPhase.FERMENTING: PhaseTradingDiscipline(
        phase=SentimentPhase.FERMENTING, position_scale=1.0, throttle_factor=1.0,
        allow_new_open=True,
        strategy_affinity={"daban": +1.0, "multifactor": 0.0, "event_driven": +0.8},
        entry_discipline="打换手龙/空间板回封，仓位5-7成。事件驱动冲击 rising phase 重仓",
        exit_discipline="趋势龙持有不动，打板按 T+1 卖出纪律，连板晋级者持有至分歧/破板",
    ),
    SentimentPhase.CONSENSUS: PhaseTradingDiscipline(
        phase=SentimentPhase.CONSENSUS, position_scale=0.5, throttle_factor=0.5,
        allow_new_open=False,
        strategy_affinity={"daban": -0.5, "multifactor": -0.3, "event_driven": -0.5},
        entry_discipline="锁仓不新开！打板禁止追高后排，仅允许前排龙头锁仓。高潮期最忌换股",
        exit_discipline="准备在分歧时减仓。后排跟风全部砍掉，趋势龙破 10 日线减仓",
    ),
    SentimentPhase.EBING: PhaseTradingDiscipline(
        phase=SentimentPhase.EBING, position_scale=0.0, throttle_factor=0.0,
        allow_new_open=False,
        strategy_affinity={"daban": -1.0, "multifactor": -0.5, "event_driven": -1.0},
        entry_discipline="无条件空仓！谁打谁亏。退潮反弹都是诱多，唯一正确动作是空仓",
        exit_discipline="无条件清仓所有短周期持仓。多因子降仓至 3 成以下防守",
    ),
}


def get_phase_trading_discipline(phase: SentimentPhase) -> PhaseTradingDiscipline:
    """标准签名⑤：获取指定阶段买卖纪律（查 PHASE_DISCIPLINE 表）。"""
    return PHASE_DISCIPLINE[phase]


def apply_phase_discipline(
    sleeve_name: str,
    target_position: float,
    locator_output: SentimentLocatorOutput,
    is_new_open: bool,
) -> tuple[float, bool, str]:
    """将情绪周期买卖纪律应用到 sleeve 目标仓位（memo §3.4）。

    Returns: (adjusted_position, allowed, reason)，reason 用于归因日志。
    """
    phase = locator_output.dominant_phase
    discipline = PHASE_DISCIPLINE[phase]
    if is_new_open:
        if not discipline.allow_new_open:
            return 0.0, False, f"phase_{phase.value}_禁止新开仓"
        if discipline.throttle_factor <= 0.0:
            return 0.0, False, f"phase_{phase.value}_throttle=0"
    scale = discipline.position_scale * locator_output.position_scale
    affinity = discipline.strategy_affinity.get(sleeve_name, 0.0)
    if affinity > 0:
        affinity_mult = 1.0 + 0.2 * min(affinity, 1.0)
    elif affinity < 0:
        affinity_mult = 1.0 - 0.5 * min(abs(affinity), 1.0)
    else:
        affinity_mult = 1.0
    adjusted = max(0.0, min(1.0, target_position * scale * affinity_mult))
    if locator_output.fallback_triggered:
        adjusted = min(adjusted, 0.2)
    reason = (
        f"phase={phase.value} scale={scale:.2f} affinity={affinity:+.1f} "
        f"mult={affinity_mult:.2f} fallback={locator_output.fallback_triggered}"
    )
    return adjusted, True, reason


# ==================================================================
# §3.5.2 映射表（情绪周期软影响 12 态概率，弱静态 Phase 1）
# ==================================================================
# 权重作用于 P 更新：P_new = P_old * (1 + weight * P_sentiment)，后归一化。
# **待 Phase 2 各策略 3-6 月实盘后人工调参**（28 号 §6 待裁定-2）。
SENTIMENT_TO_REGIME_MAP: dict[SentimentPhase, dict[str, float]] = {
    SentimentPhase.FREEZING: {"Bear-Low": +0.15, "Neutral-Low": +0.10},
    SentimentPhase.STARTING: {"RECOVERY": +0.20},
    SentimentPhase.FERMENTING: {"Bull-Medium": +0.15, "BREAKOUT": +0.10},
    SentimentPhase.CONSENSUS: {"Bull-High": +0.20},
    SentimentPhase.EBING: {"Bear-Medium": +0.15, "Bear-High": +0.10},
}

# 12 态（对齐 10_regime §2.6：9 基础态 = 趋势×波动率 + 3 特殊态）
REGIME_STATES_12: list[str] = [
    "Bull-Low", "Bull-Medium", "Bull-High", "Neutral-Low", "Neutral-Medium", "Neutral-High",
    "Bear-Low", "Bear-Medium", "Bear-High", "CRISIS", "RECOVERY", "BREAKOUT",
]


def validate_sentiment_regime_map(
    mapping: dict[SentimentPhase, dict[str, float]] | None = None,
) -> list[str]:
    """§3.5.2 映射表加载校验（配置级，标"待 Phase 2 人工调参"）。

    规则：① 覆盖全 5 阶段；② 目标态名 ∈ REGIME_STATES_12；③ 权重 ∈ [-1,1]
    （Phase 1 均为正向软调）；④ 单阶段权重绝对值 ≤0.5（软影响防爆上限）。
    返回问题清单（空=通过）。
    """
    table = SENTIMENT_TO_REGIME_MAP if mapping is None else mapping
    problems: list[str] = []
    for phase in SentimentPhase:
        if phase not in table:
            problems.append(f"缺阶段映射: {phase.name}")
    known = set(REGIME_STATES_12)
    for phase, weight_map in table.items():
        if not weight_map:
            problems.append(f"{phase.name} 映射为空")
        for state, weight in weight_map.items():
            if state not in known:
                problems.append(f"{phase.name}→未知 regime 态: {state!r}")
            if not (-1.0 <= weight <= 1.0):
                problems.append(f"{phase.name}→{state} 权重越界: {weight}")
            if abs(weight) > 0.5:
                problems.append(f"{phase.name}→{state} 权重超软影响上限 0.5: {weight}")
    return problems


def apply_sentiment_soft_influence(
    regime_prob: dict[str, float],
    sentiment_output: SentimentLocatorOutput,
) -> dict[str, float]:
    """情绪周期对 12 态概率的软影响（§3.5.2 regime 概率版，弱静态 Phase 1）。

    P_new = P_old * (1 + weight * P_sentiment)，后归一化。情绪不直接被 Shrinkage 消费。
    """
    adjusted = dict(regime_prob)
    for phase, weight_map in SENTIMENT_TO_REGIME_MAP.items():
        p_sentiment = sentiment_output.phase_prob.get(phase, 0.0)
        if p_sentiment <= 0:
            continue
        for regime_state, weight in weight_map.items():
            if regime_state in adjusted:
                adjusted[regime_state] *= 1.0 + weight * p_sentiment
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {k: v / total for k, v in adjusted.items()}
    return adjusted


# ==================================================================
# §3.5.4 软影响算法 + 有效组合（情绪×regime 联合指令）
# ==================================================================
@dataclass
class CombinedTradingDirective:
    """联合交易指令——情绪周期×regime 12 态联合仓位/节流指令（乘法叠加）。"""

    sentiment_phase: SentimentPhase
    regime_state: str
    position_scale_sentiment: float
    shrinkage_regime: float
    combined_position_scale: float  # sentiment × regime
    allow_new_open: bool
    throttle_factor: float  # min(sentiment, regime)
    strategy_affinity: dict[str, float]
    rationale: str


# 5 阶段 × 12 态 → 联合仓位缩放系数（memo §3.5.4，已乘 sentiment_base × regime_shrinkage）
SENTIMENT_REGIME_MAPPING: dict[SentimentPhase, dict[str, float]] = {
    SentimentPhase.FREEZING: {
        "Bull-Low": 0.0, "Bull-Medium": 0.0, "Bull-High": 0.0, "Neutral-Low": 0.0,
        "Neutral-Medium": 0.0, "Neutral-High": 0.0, "Bear-Low": 0.0, "Bear-Medium": 0.0,
        "Bear-High": 0.0, "CRISIS": 0.0, "RECOVERY": 0.0, "BREAKOUT": 0.0,
    },
    SentimentPhase.STARTING: {
        "Bull-Low": 0.50, "Bull-Medium": 0.45, "Bull-High": 0.35, "Neutral-Low": 0.40,
        "Neutral-Medium": 0.35, "Neutral-High": 0.25, "Bear-Low": 0.30, "Bear-Medium": 0.20,
        "Bear-High": 0.10, "CRISIS": 0.10, "RECOVERY": 0.30, "BREAKOUT": 0.45,
    },
    SentimentPhase.FERMENTING: {
        "Bull-Low": 1.00, "Bull-Medium": 0.90, "Bull-High": 0.70, "Neutral-Low": 0.80,
        "Neutral-Medium": 0.70, "Neutral-High": 0.50, "Bear-Low": 0.60, "Bear-Medium": 0.40,
        "Bear-High": 0.20, "CRISIS": 0.15, "RECOVERY": 0.50, "BREAKOUT": 0.95,
    },
    SentimentPhase.CONSENSUS: {
        "Bull-Low": 0.50, "Bull-Medium": 0.45, "Bull-High": 0.35, "Neutral-Low": 0.40,
        "Neutral-Medium": 0.35, "Neutral-High": 0.25, "Bear-Low": 0.30, "Bear-Medium": 0.20,
        "Bear-High": 0.10, "CRISIS": 0.10, "RECOVERY": 0.30, "BREAKOUT": 0.45,
    },
    SentimentPhase.EBING: {
        "Bull-Low": 0.0, "Bull-Medium": 0.0, "Bull-High": 0.0, "Neutral-Low": 0.0,
        "Neutral-Medium": 0.0, "Neutral-High": 0.0, "Bear-Low": 0.0, "Bear-Medium": 0.0,
        "Bear-High": 0.0, "CRISIS": 0.0, "RECOVERY": 0.0, "BREAKOUT": 0.0,
    },
}

# 60 个有效组合（5 阶段 × 12 态）
EFFECTIVE_COMBINATIONS_60: list[tuple[SentimentPhase, str]] = [
    (phase, regime) for phase in SentimentPhase for regime in REGIME_STATES_12
]


def get_effective_combinations(
    phase_filter: Optional[SentimentPhase] = None,
    regime_filter: Optional[str] = None,
) -> list[tuple[SentimentPhase, str]]:
    """获取有效（情绪阶段, regime 态）组合列表（全量 60 个，可过滤）。"""
    return [
        (phase, regime)
        for phase in SentimentPhase
        for regime in REGIME_STATES_12
        if (phase_filter is None or phase == phase_filter)
        and (regime_filter is None or regime == regime_filter)
    ]


def apply_sentiment_position_soft_influence(
    sleeve_name: str,
    target_position: float,
    sentiment_output: SentimentLocatorOutput,
) -> tuple[float, str]:
    """情绪阶段对策略仓位的软影响（§3.5.4 仓位版；memo 注：重命名避免与 §3.5.2 同名覆盖）。

    概率加权缩放：Σ P(phase) × position_scale(phase) × affinity_mult；兜底强收缩 ≤0.2。
    Returns: (adjusted_position, rationale)
    """
    weighted_scale = 0.0
    for phase, prob in sentiment_output.phase_prob.items():
        if prob <= 0:
            continue
        base_scale = PHASE_DISCIPLINE[phase].position_scale
        affinity = PHASE_DISCIPLINE[phase].strategy_affinity.get(sleeve_name, 0.0)
        if affinity > 0:
            affinity_mult = 1.0 + 0.2 * min(affinity, 1.0)
        elif affinity < 0:
            affinity_mult = 1.0 - 0.5 * min(abs(affinity), 1.0)
        else:
            affinity_mult = 1.0
        weighted_scale += prob * base_scale * affinity_mult
    if sentiment_output.fallback_triggered:
        weighted_scale = min(weighted_scale, 0.2)
    adjusted = max(0.0, min(1.0, target_position * weighted_scale))
    dominant = sentiment_output.dominant_phase
    rationale = (
        f"soft_influence: weighted_scale={weighted_scale:.3f} "
        f"dominant={dominant.value} confidence={sentiment_output.confidence:.2f} "
        f"fallback={sentiment_output.fallback_triggered}"
    )
    return adjusted, rationale


def combine_sentiment_regime(
    sleeve_name: str,
    target_position: float,
    sentiment_output: SentimentLocatorOutput,
    regime_prob: dict[str, float],
    regime_shrinkage_map: dict[str, float],
) -> CombinedTradingDirective:
    """alpha 仓位缩放 × regime Shrinkage 乘法叠加（§3.5.4 联合交易指令）。

    乘法叠加理由（正交性）：情绪管"方向/标的"，regime 管"力度/谨慎度"。
    """
    sentiment_adjusted, sentiment_rationale = apply_sentiment_position_soft_influence(
        sleeve_name=sleeve_name, target_position=target_position,
        sentiment_output=sentiment_output,
    )
    regime_shrinkage = 0.0
    total_prob = 0.0
    for regime_state, prob in regime_prob.items():
        shrink = regime_shrinkage_map.get(regime_state, 0.5)
        regime_shrinkage += prob * shrink
        total_prob += prob
    if total_prob > 0:
        regime_shrinkage /= total_prob
    dominant_phase = sentiment_output.dominant_phase
    dominant_regime = max(regime_prob, key=regime_prob.get) if regime_prob else "Unknown"
    combined = max(0.0, min(1.0, sentiment_adjusted * regime_shrinkage))
    sentiment_allow = PHASE_DISCIPLINE[dominant_phase].allow_new_open
    allow_new_open = sentiment_allow and (regime_shrinkage >= 0.3)
    throttle_factor = min(PHASE_DISCIPLINE[dominant_phase].throttle_factor, regime_shrinkage)
    if sentiment_output.fallback_triggered:
        combined = min(combined, 0.2)
    rationale = (
        f"{sentiment_rationale} | regime_shrinkage={regime_shrinkage:.3f} "
        f"combined={combined:.3f} allow_new={allow_new_open}"
    )
    return CombinedTradingDirective(
        sentiment_phase=dominant_phase, regime_state=dominant_regime,
        position_scale_sentiment=sentiment_adjusted, shrinkage_regime=regime_shrinkage,
        combined_position_scale=combined, allow_new_open=allow_new_open,
        throttle_factor=throttle_factor,
        strategy_affinity=PHASE_DISCIPLINE[dominant_phase].strategy_affinity,
        rationale=rationale,
    )


# ==================================================================
# §3.6.1 策略部署算法（标准签名⑧）
# ==================================================================
@dataclass
class StrategyDeploymentPolicy:
    """单策略单阶段部署策略——3 策略×5 阶段部署矩阵单元格。"""

    strategy_name: str  # "daban"/"multifactor"/"event_driven"
    phase: SentimentPhase
    position_scale: float
    allow_new_open: bool
    target_holdings_ratio: float
    deployment_desc: str
    risk_notes: str


STRATEGY_DEPLOYMENT_MATRIX: dict[tuple[str, SentimentPhase], StrategyDeploymentPolicy] = {
    # ===== 打板：情绪周期纯多头 =====
    ("daban", SentimentPhase.FREEZING): StrategyDeploymentPolicy(
        strategy_name="daban", phase=SentimentPhase.FREEZING, position_scale=0.0,
        allow_new_open=False, target_holdings_ratio=0.0,
        deployment_desc="空仓，禁止打板", risk_notes="冰点打板必亏，次日溢价 -5%~-2%",
    ),
    ("daban", SentimentPhase.STARTING): StrategyDeploymentPolicy(
        strategy_name="daban", phase=SentimentPhase.STARTING, position_scale=0.3,
        allow_new_open=True, target_holdings_ratio=0.25,
        deployment_desc="试错首板/空间板，仓位 2-3 成", risk_notes="试错期，错了就砍，对了加仓",
    ),
    ("daban", SentimentPhase.FERMENTING): StrategyDeploymentPolicy(
        strategy_name="daban", phase=SentimentPhase.FERMENTING, position_scale=0.7,
        allow_new_open=True, target_holdings_ratio=0.60,
        deployment_desc="重仓换手龙/空间板回封，仓位 5-7 成",
        risk_notes="主升期打板黄金窗口，但 7 成为上限（55188 实战）",
    ),
    ("daban", SentimentPhase.CONSENSUS): StrategyDeploymentPolicy(
        strategy_name="daban", phase=SentimentPhase.CONSENSUS, position_scale=0.4,
        allow_new_open=False, target_holdings_ratio=0.35,
        deployment_desc="锁仓不新开，仅前排龙头锁仓", risk_notes="高潮期最忌换股/追高后排",
    ),
    ("daban", SentimentPhase.EBING): StrategyDeploymentPolicy(
        strategy_name="daban", phase=SentimentPhase.EBING, position_scale=0.0,
        allow_new_open=False, target_holdings_ratio=0.0,
        deployment_desc="无条件空仓，谁打谁亏", risk_notes="退潮反弹都是诱多",
    ),
    # ===== 多因子：情绪周期逆向者 =====
    ("multifactor", SentimentPhase.FREEZING): StrategyDeploymentPolicy(
        strategy_name="multifactor", phase=SentimentPhase.FREEZING, position_scale=0.1,
        allow_new_open=True, target_holdings_ratio=0.10,
        deployment_desc="左侧布局低估值标的（估值分位<15%），仓位≤1 成试错",
        risk_notes="冰点是多因子黄金布局期，但需极轻仓试错",
    ),
    ("multifactor", SentimentPhase.STARTING): StrategyDeploymentPolicy(
        strategy_name="multifactor", phase=SentimentPhase.STARTING, position_scale=0.5,
        allow_new_open=True, target_holdings_ratio=0.40,
        deployment_desc="左侧加仓低位横截面，仓位 3-5 成", risk_notes="反核期加仓，与打板试错形成对冲",
    ),
    ("multifactor", SentimentPhase.FERMENTING): StrategyDeploymentPolicy(
        strategy_name="multifactor", phase=SentimentPhase.FERMENTING, position_scale=0.8,
        allow_new_open=True, target_holdings_ratio=0.70,
        deployment_desc="持有不动，享受趋势", risk_notes="主升期多因子被动收益，不主动调仓",
    ),
    ("multifactor", SentimentPhase.CONSENSUS): StrategyDeploymentPolicy(
        strategy_name="multifactor", phase=SentimentPhase.CONSENSUS, position_scale=0.3,
        allow_new_open=False, target_holdings_ratio=0.30,
        deployment_desc="减仓至 3 成，估值高位兑现", risk_notes="疯狂期多因子减仓，与打板锁仓形成对冲",
    ),
    ("multifactor", SentimentPhase.EBING): StrategyDeploymentPolicy(
        strategy_name="multifactor", phase=SentimentPhase.EBING, position_scale=0.2,
        allow_new_open=False, target_holdings_ratio=0.20,
        deployment_desc="降仓至 3 成以下防守", risk_notes="退潮期保留底仓，但严控仓位",
    ),
    # ===== 事件驱动：跨阶段差异化 =====
    ("event_driven", SentimentPhase.FREEZING): StrategyDeploymentPolicy(
        strategy_name="event_driven", phase=SentimentPhase.FREEZING, position_scale=0.1,
        allow_new_open=True, target_holdings_ratio=0.10,
        deployment_desc="防守，仅高确定性事件（如重组落地）", risk_notes="冰点期事件冲击衰减快，仅做高确定性",
    ),
    ("event_driven", SentimentPhase.STARTING): StrategyDeploymentPolicy(
        strategy_name="event_driven", phase=SentimentPhase.STARTING, position_scale=0.4,
        allow_new_open=True, target_holdings_ratio=0.35,
        deployment_desc="布局利好公告，仓位 3-4 成", risk_notes="反核期事件驱动开始活跃",
    ),
    ("event_driven", SentimentPhase.FERMENTING): StrategyDeploymentPolicy(
        strategy_name="event_driven", phase=SentimentPhase.FERMENTING, position_scale=0.7,
        allow_new_open=True, target_holdings_ratio=0.60,
        deployment_desc="重仓 rising phase 事件，仓位 5-7 成",
        risk_notes="主升期事件冲击衰减最慢，rising phase 最强（Yukka 2026）",
    ),
    ("event_driven", SentimentPhase.CONSENSUS): StrategyDeploymentPolicy(
        strategy_name="event_driven", phase=SentimentPhase.CONSENSUS, position_scale=0.3,
        allow_new_open=False, target_holdings_ratio=0.25,
        deployment_desc="减仓，事件冲击衰减加快", risk_notes="疯狂期事件驱动退场，与打板锁仓同步",
    ),
    ("event_driven", SentimentPhase.EBING): StrategyDeploymentPolicy(
        strategy_name="event_driven", phase=SentimentPhase.EBING, position_scale=0.0,
        allow_new_open=False, target_holdings_ratio=0.0,
        deployment_desc="无条件清仓", risk_notes="退潮期事件冲击被情绪淹没，无 alpha",
    ),
}


def compute_strategy_deployment(
    phase: SentimentPhase,
    strategy_name: Optional[str] = None,
) -> "StrategyDeploymentPolicy | dict[str, StrategyDeploymentPolicy]":
    """按情绪阶段查 3 策略×5 阶段部署矩阵（§3.6.1）。"""
    if strategy_name is not None:
        return STRATEGY_DEPLOYMENT_MATRIX[(strategy_name, phase)]
    return {
        s: STRATEGY_DEPLOYMENT_MATRIX[(s, phase)]
        for s in ("daban", "multifactor", "event_driven")
    }


def get_strategy_deployment_by_phase(
    phase: SentimentPhase,
    strategy_name: Optional[str] = None,
) -> "StrategyDeploymentPolicy | dict[str, StrategyDeploymentPolicy]":
    """标准签名⑧：按阶段获取策略部署（薄包装委托 §3.6.1，无递归）。"""
    return compute_strategy_deployment(phase, strategy_name)


# ==================================================================
# §3.7 隐形驱动验证（§3.7.2 分层相关性 + §3.7.4 Hawkes+block-bootstrap）
# ==================================================================
@dataclass
class SentimentStratificationTest:
    """情绪周期分层相关性验证结果（G07 施工前必做，30 号 §6.2）。"""

    phase: SentimentPhase
    n_days: int
    correlation_matrix: dict[str, dict[str, float]]
    is_pass: bool  # ρ_max < 0.6


def _compute_corr_matrix(
    returns: dict[str, list[float]],
    idx: list[int],
) -> dict[str, dict[str, float]]:
    strategies = list(returns.keys())
    matrix = {s1: {s2: 0.0 for s2 in strategies} for s1 in strategies}
    for s1 in strategies:
        for s2 in strategies:
            r1 = [returns[s1][i] for i in idx]
            r2 = [returns[s2][i] for i in idx]
            if len(r1) > 1 and len(r2) > 1:
                matrix[s1][s2] = float(np.corrcoef(r1, r2)[0, 1])
    return matrix


def validate_sentiment_hidden_driver(
    daily_returns: dict[str, list[float]],
    daily_phases: list[SentimentPhase],
    correlation_threshold: float = 0.6,
) -> dict[SentimentPhase, SentimentStratificationTest]:
    """隐形驱动验证（§3.7.2）：分层后相关性显著下降 → 假设成立、分层有效。

    daily_returns={策略: 日收益序列}，daily_phases=每日情绪阶段标签。
    样本 <30 天的稀有阶段跳过但记录（is_pass=False）。
    """
    strategies = list(daily_returns.keys())
    n = len(daily_phases)
    results: dict[SentimentPhase, SentimentStratificationTest] = {}
    for phase in SentimentPhase:
        idx = [i for i, p in enumerate(daily_phases) if p == phase and i < n]
        if len(idx) < 30:
            results[phase] = SentimentStratificationTest(phase, len(idx), {}, False)
            continue
        phase_returns = {s: [daily_returns[s][i] for i in idx] for s in strategies}
        matrix = _compute_corr_matrix(phase_returns, list(range(len(idx))))
        max_rho = max(
            abs(matrix[s1][s2])
            for i, s1 in enumerate(strategies)
            for j, s2 in enumerate(strategies)
            if i < j
        )
        results[phase] = SentimentStratificationTest(
            phase, len(idx), matrix, max_rho < correlation_threshold,
        )
    return results


@dataclass
class SentimentHawkesParams:
    """Hawkes 自激发点过程参数（§3.7.4）。分支比 η=α/β<1 稳定，>1 爆炸（退潮/危机）。"""

    lambda_0: float  # 基础强度 λ₀
    alpha: float  # 激发系数 α
    beta: float  # 衰减率 β
    critical_ratio: float  # 临界分支比 η_c = α/β


def compute_hawkes_intensity(
    event_times: list[float],
    params: SentimentHawkesParams,
    t: float,
) -> float:
    """λ(t) = λ₀ + Σ α × exp(-β × (t - t_i))  for t_i < t（§3.7.4）。"""
    intensity = params.lambda_0
    for ti in event_times:
        if ti < t:
            intensity += params.alpha * math.exp(-params.beta * (t - ti))
    return intensity


def estimate_hawkes_branching_ratio(
    event_times: list[float],
    params: SentimentHawkesParams,
) -> float:
    """分支比 η = α/β（§3.7.4）。β≤0 → +inf。

    η<1 稳定（健康主升 0.5-0.8）；η≈1 临界（疯狂→退潮转换期）；η>1 爆炸（退潮/危机）。
    实证对标（Filimonov & Sornette 2012）：危机期 η→0.95-1.05，正常期 η≈0.4-0.7。
    """
    if params.beta <= 0:
        return float("inf")
    return params.alpha / params.beta


def compute_sentiment_correlation_driver(
    strategy_returns: dict[str, list[float]],
    sentiment_intensity_series: list[float],
) -> dict[str, float]:
    """各策略日收益与情绪 Hawkes 强度的相关系数 ρ(strategy, λ)（§3.7.4）。

    判据：ρ>0.6 强驱动（打板预期）；0.3-0.6 中等（事件驱动预期）；<0.3 弱驱动（多因子预期）。
    """
    drivers = {}
    intensity = np.array(sentiment_intensity_series)
    for strat, returns in strategy_returns.items():
        n = min(len(returns), len(intensity))
        if n < 2:
            drivers[strat] = 0.0
            continue
        r = np.array(returns[:n])
        lam = intensity[:n]
        drivers[strat] = float(np.corrcoef(r, lam)[0, 1]) if r.std() > 0 and lam.std() > 0 else 0.0
    return drivers


def analyze_sentiment_driven_correlation(
    strategy_returns: dict[str, list[float]],
    sentiment_intensity_series: list[float],
    n_bootstrap: int = 2000,
    block_size: int = 5,
    confidence_level: float = 0.95,
) -> dict:
    """G07 block-bootstrap 验证——情绪驱动相关性的统计显著性（§3.7.4）。

    ①实测 ρ_obs → ②block-bootstrap 重排情绪强度序列（保留时序自相关）→
    ③零分布 ρ_boot → ④p-value = P(|ρ_boot| >= |ρ_obs|) → ⑤p<0.05 显著。
    block_size=5：情绪周期 1-2 周 → 约 1 周保留时序结构。
    Returns: {observed_rho, p_value, is_significant, bootstrap_mean_rho,
              bootstrap_std_rho, n_bootstrap}（均为 {策略: 值} 字典，n_bootstrap 为 int）
    """
    rng = np.random.default_rng(seed=42)
    n = len(sentiment_intensity_series)
    intensity = np.array(sentiment_intensity_series)
    observed_rho = compute_sentiment_correlation_driver(strategy_returns, sentiment_intensity_series)
    n_blocks = max(n // block_size, 1)
    bootstrap_rhos: dict[str, list[float]] = {s: [] for s in strategy_returns}
    for _ in range(n_bootstrap):
        block_indices = rng.integers(0, n_blocks, size=n_blocks)
        shuffled = np.concatenate(
            [intensity[i * block_size:(i + 1) * block_size] for i in block_indices]
        )
        if len(shuffled) < n:
            shuffled = np.concatenate([shuffled, intensity[: n - len(shuffled)]])
        for strat, returns in strategy_returns.items():
            m = min(len(returns), len(shuffled))
            if m < 2:
                continue
            r = np.array(returns[:m])
            lam = shuffled[:m]
            if r.std() > 0 and lam.std() > 0:
                bootstrap_rhos[strat].append(float(np.corrcoef(r, lam)[0, 1]))
    p_values, is_significant, boot_mean, boot_std = {}, {}, {}, {}
    for strat in strategy_returns:
        boots = np.array(bootstrap_rhos[strat]) if bootstrap_rhos[strat] else np.array([0.0])
        obs = abs(observed_rho[strat])
        p_values[strat] = float(np.mean(np.abs(boots) >= obs))
        is_significant[strat] = p_values[strat] < (1.0 - confidence_level)
        boot_mean[strat] = float(np.mean(boots))
        boot_std[strat] = float(np.std(boots))
    return {
        "observed_rho": observed_rho,
        "p_value": p_values,
        "is_significant": is_significant,
        "bootstrap_mean_rho": boot_mean,
        "bootstrap_std_rho": boot_std,
        "n_bootstrap": n_bootstrap,
    }


# ==================================================================
# §3.10 标准签名 wrappers（①⑥⑦）
# ==================================================================
def classify_sentiment_phase(
    inp: SentimentLocatorInput,
    confidence_threshold: float = 0.60,
) -> SentimentLocatorOutput:
    """标准签名①：情绪周期阶段分类（薄包装委托 §3.3，无递归）。"""
    return locate_sentiment_phase(inp, confidence_threshold)


def evaluate_locator_accuracy(
    predicted_phases: list[SentimentPhase],
    actual_phases: list[SentimentPhase],
) -> dict[str, float]:
    """标准签名⑥：评估定位器准确率（对齐 30 号 §6.3）。

    错判代价不对称 → 除精确率外计算"相邻阶段容错率"（差一阶段）。
    """
    if len(predicted_phases) != len(actual_phases) or not predicted_phases:
        return {"accuracy": 0.0, "adjacent_tolerance_rate": 0.0, "n_samples": 0.0}
    correct = sum(1 for p, a in zip(predicted_phases, actual_phases) if p == a)
    accuracy = correct / len(predicted_phases)
    adjacent_correct = sum(
        1
        for p, a in zip(predicted_phases, actual_phases)
        if p != a and abs(PHASE_ORDER.index(p) - PHASE_ORDER.index(a)) == 1
    )
    return {
        "accuracy": accuracy,
        "adjacent_tolerance_rate": adjacent_correct / len(predicted_phases),
        "n_samples": float(len(predicted_phases)),
    }


def map_sentiment_to_regime(
    regime_prob: dict[str, float],
    sentiment_output: SentimentLocatorOutput,
) -> dict:
    """标准签名⑦：情绪→regime 映射（§3.5.2 软影响 + §3.5.4 查表，无递归）。"""
    adjusted_regime_prob = apply_sentiment_soft_influence(regime_prob, sentiment_output)
    dominant_phase = sentiment_output.dominant_phase
    dominant_regime = max(regime_prob, key=regime_prob.get) if regime_prob else "Unknown"
    combined_scale = SENTIMENT_REGIME_MAPPING.get(dominant_phase, {}).get(dominant_regime, 0.0)
    return {
        "regime_prob_adjusted": adjusted_regime_prob,
        "dominant_phase": dominant_phase,
        "dominant_regime": dominant_regime,
        "combined_position_scale": combined_scale,
    }
