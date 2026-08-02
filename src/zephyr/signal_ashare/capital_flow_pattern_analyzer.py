# [BLUEPRINT] MOD-SIG-022 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.capital_flow_pattern_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.short_term_stock_selector
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五类形态互斥; 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_capital_flow_pattern_analyzer.py
# [A_module] module_id=MOD-SIG-022 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

"""
D-SIGNAL-22 A股资金线形态分析引擎

五类资金线形态识别(四线开花/机构独强/机构主力背离/弱势反弹/全线溃退)
+ 散户狂热反向指标 + 机构分歧机会识别器 + 资金线多线共振分析。

理论依据：资金流向分析 / 形态识别 / 多线共振。

设计文档默认值可配置——所有阈值通过 CapitalFlowPatternConfig 调整，
默认值取自 D:\\临时工作区\\依赖图\\04-D-SIGNAL-信号域.md §D-SIGNAL-22。

四线定义：主力资金线 / 机构资金线 / 散户资金线 / 游资资金线。
依赖方向：D_DATA(资金流数据) -> D-SIGNAL-22 -> D-SIGNAL-23(短线选股) / D-SIGNAL-24(日内买卖点)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class CapitalFlowPattern(str, Enum):
    """五类资金线形态。"""

    FOUR_LINE_BLOOM = "四线开花"  # 健康主升
    INSTITUTIONAL_SOLO = "机构独强"  # 吸筹洗盘
    DIVERGENCE = "机构主力背离"  # 方向抉择
    WEAK_REBOUND = "弱势反弹"  # 诱多风险
    FULL_RETREAT = "全线溃退"  # 恐慌下跌
    UNKNOWN = "未知"


# ============================================================================
# 配置
# ============================================================================


@dataclass(frozen=True)
class CapitalFlowPatternConfig:
    """资金线形态分析可配置阈值——默认值取自设计文档 §D-SIGNAL-22。"""

    # ── 四线开花判定 ──
    # 四条资金线全部净流入且方向一致
    bloom_min_lines_positive: int = 4  # 至少4条线净流入
    bloom_min_total_inflow: float = 0.0  # 总净流入>=0
    bloom_max_retail_ratio: float = 0.3  # 散户占比<30%（非散户推动）

    # ── 机构独强判定 ──
    # 机构线强正，其他线弱/负
    solo_min_institutional: float = 1.0  # 机构净流入正
    solo_max_main_force: float = 0.0  # 主力净流入<=0
    solo_max_retail: float = 0.0  # 散户净流入<=0

    # ── 机构主力背离判定 ──
    # 机构与主力方向相反
    divergence_min_abs: float = 1.0  # 两线绝对差>=1.0

    # ── 弱势反弹判定 ──
    # 总净流入为负但价格微涨（诱多）
    weak_rebound_max_total_inflow: float = 0.0  # 总净流入<=0
    weak_rebound_min_price_rise: float = 0.5  # 价格涨幅>=0.5%

    # ── 全线溃退判定 ──
    # 四条线全部净流出
    retreat_max_lines_positive: int = 1  # 最多1条线正
    retreat_max_total_inflow: float = 0.0  # 总净流入<=0

    # ── 散户狂热反向指标 ──
    # 散户净流入占比超过阈值 → 反向信号（散户大量买入=见顶信号）
    retail_frenzy_threshold: float = 0.5  # 散户占比>50%

    # ── 机构分歧机会识别 ──
    # 机构之间分歧（部分买入部分卖出）→ 潜在机会
    institutional_divergence_min: float = 0.3  # 机构内部分歧度

    # ── 多线共振 ──
    # 多条线同方向 → 共振强度
    resonance_min_lines: int = 3  # 至少3条线同方向


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class CapitalFlowInput:
    """资金线形态分析输入数据。"""

    # 四条资金线净流入(万元)，正值=净流入
    main_force_inflow: list[float]  # 主力资金
    institutional_inflow: list[float]  # 机构资金
    retail_inflow: list[float]  # 散户资金
    hot_money_inflow: list[float]  # 游资资金
    prices: list[float]  # 对应价格序列
    market_sentiment_score: float = 50.0  # 来自 D-SIGNAL-25


@dataclass
class CapitalFlowPatternResult:
    """资金线形态分析结果。"""

    pattern: str
    pattern_confidence: float
    retail_frenzy_score: float  # 散户狂热度 0~100
    contrarian_signal: str  # 反向信号: buy/sell/neutral
    institutional_divergence: float  # 机构分歧度 0~1
    opportunity_detected: bool  # 机构分歧机会
    resonance_score: float  # 多线共振强度 0~100
    resonance_direction: str  # 共振方向: up/down/neutral
    overall_score: float
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    is_degraded: bool = False


# ============================================================================
# 分析器
# ============================================================================


class CapitalFlowPatternAnalyzer:
    """
    A股资金线形态分析引擎（D-SIGNAL-22）。

    4维度分析：
      1. 五类资金线形态识别
      2. 散户狂热反向指标
      3. 机构分歧机会识别
      4. 多线共振分析
    """

    def __init__(self, config: CapitalFlowPatternConfig | None = None) -> None:
        self._config = config or CapitalFlowPatternConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: CapitalFlowInput) -> CapitalFlowPatternResult:
        """执行4维度资金线形态分析。"""
        if not self._validate_input(input_data):
            logger.warning("CapitalFlowPatternAnalyzer: 输入数据不合法，返回降级结果")
            return self._degraded_result("输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 维度1: 五类形态识别 ──
        pattern, pattern_conf = self.identify_pattern(input_data)
        audit_trail.append(
            {
                "dimension": "pattern_identification",
                "result": pattern,
                "confidence": pattern_conf,
            }
        )

        # ── 维度2: 散户狂热反向指标 ──
        retail_frenzy, contrarian = self.retail_frenzy_contrarian(input_data)
        audit_trail.append(
            {
                "dimension": "retail_frenzy",
                "result": {"frenzy_score": retail_frenzy, "contrarian": contrarian},
            }
        )

        # ── 维度3: 机构分歧机会 ──
        inst_div, opportunity = self.detect_institutional_divergence(input_data)
        audit_trail.append(
            {
                "dimension": "institutional_divergence",
                "result": {"divergence": inst_div, "opportunity": opportunity},
            }
        )

        # ── 维度4: 多线共振 ──
        resonance, resonance_dir = self.analyze_resonance(input_data)
        audit_trail.append(
            {
                "dimension": "resonance",
                "result": {"score": resonance, "direction": resonance_dir},
            }
        )

        # ── 综合评分 ──
        overall = self._compute_overall_score(pattern_conf, retail_frenzy, inst_div, resonance)

        return CapitalFlowPatternResult(
            pattern=pattern,
            pattern_confidence=pattern_conf,
            retail_frenzy_score=retail_frenzy,
            contrarian_signal=contrarian,
            institutional_divergence=inst_div,
            opportunity_detected=opportunity,
            resonance_score=resonance,
            resonance_direction=resonance_dir,
            overall_score=overall,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 维度1: 五类资金线形态识别
    # ------------------------------------------------------------------

    def identify_pattern(self, input_data: CapitalFlowInput) -> tuple[str, float]:
        """
        识别五类资金线形态。

        四线：主力/机构/散户/游资净流入方向组合 → 形态判定。
        """
        cfg = self._config
        lines = [
            sum(input_data.main_force_inflow),
            sum(input_data.institutional_inflow),
            sum(input_data.retail_inflow),
            sum(input_data.hot_money_inflow),
        ]
        total = sum(lines)
        positive_count = sum(1 for x in lines if x > 0)

        # 全部为零（无资金流数据）→ 未知形态，避免被误判为全线溃退
        if all(abs(x) < 1e-9 for x in lines):
            return CapitalFlowPattern.UNKNOWN.value, 0.0

        scores: dict[str, float] = {}

        # 四线开花：4线全正 + 散户占比低
        scores[CapitalFlowPattern.FOUR_LINE_BLOOM.value] = self._score_bloom(lines, positive_count, total)
        # 机构独强：机构正 + 主力/散户负
        scores[CapitalFlowPattern.INSTITUTIONAL_SOLO.value] = self._score_solo(lines)
        # 机构主力背离：机构与主力方向相反
        scores[CapitalFlowPattern.DIVERGENCE.value] = self._score_divergence(lines)
        # 弱势反弹：总净流出 + 价格微涨
        scores[CapitalFlowPattern.WEAK_REBOUND.value] = self._score_weak_rebound(total, input_data.prices)
        # 全线溃退：最多1线正 + 总净流出
        scores[CapitalFlowPattern.FULL_RETREAT.value] = self._score_retreat(positive_count, total)

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best]
        if best_score < 20.0:
            return CapitalFlowPattern.UNKNOWN.value, best_score
        return best, best_score

    def _score_bloom(self, lines: list[float], positive_count: int, total: float) -> float:
        cfg = self._config
        score = 0.0
        if positive_count >= cfg.bloom_min_lines_positive:
            score += 50.0
        if total >= cfg.bloom_min_total_inflow:
            score += 30.0
        # 散户占比低
        retail = lines[2]
        if total > 0 and retail / total < cfg.bloom_max_retail_ratio:
            score += 20.0
        return min(score, 100.0)

    def _score_solo(self, lines: list[float]) -> float:
        cfg = self._config
        score = 0.0
        # lines = [主力, 机构, 散户, 游资]
        main_f, inst, retail, _ = lines
        if inst >= cfg.solo_min_institutional:
            score += 40.0
        if main_f <= cfg.solo_max_main_force:
            score += 30.0
        if retail <= cfg.solo_max_retail:
            score += 30.0
        return min(score, 100.0)

    def _score_divergence(self, lines: list[float]) -> float:
        cfg = self._config
        inst, main_f = lines[1], lines[0]
        diff = abs(inst - main_f)
        if diff >= cfg.divergence_min_abs and (inst > 0) != (main_f > 0):
            return 100.0
        if diff >= cfg.divergence_min_abs:
            return 60.0
        return 0.0

    def _score_weak_rebound(self, total: float, prices: list[float]) -> float:
        cfg = self._config
        score = 0.0
        if total <= cfg.weak_rebound_max_total_inflow:
            score += 50.0
        if len(prices) >= 2 and prices[0] > 0:
            rise = (prices[-1] - prices[0]) / prices[0] * 100.0
            if rise >= cfg.weak_rebound_min_price_rise:
                score += 50.0
        return min(score, 100.0)

    def _score_retreat(self, positive_count: int, total: float) -> float:
        cfg = self._config
        score = 0.0
        if positive_count <= cfg.retreat_max_lines_positive:
            score += 50.0
        if total <= cfg.retreat_max_total_inflow:
            score += 50.0
        return min(score, 100.0)

    # ------------------------------------------------------------------
    # 维度2: 散户狂热反向指标
    # ------------------------------------------------------------------

    def retail_frenzy_contrarian(self, input_data: CapitalFlowInput) -> tuple[float, str]:
        """
        散户狂热反向指标。

        散户净流入占比越高 → 狂热度越高 → 反向卖出信号。
        """
        cfg = self._config
        total_abs = (
            abs(sum(input_data.main_force_inflow))
            + abs(sum(input_data.institutional_inflow))
            + abs(sum(input_data.retail_inflow))
            + abs(sum(input_data.hot_money_inflow))
        )
        if total_abs <= 0:
            return 0.0, "neutral"

        retail_share = abs(sum(input_data.retail_inflow)) / total_abs
        frenzy_score = min(retail_share / cfg.retail_frenzy_threshold * 100.0, 100.0)

        if retail_share >= cfg.retail_frenzy_threshold:
            return frenzy_score, "sell"  # 散户狂热 → 反向卖出
        if retail_share <= 0.15:
            return frenzy_score, "buy"  # 散户冷清 → 反向买入
        return frenzy_score, "neutral"

    # ------------------------------------------------------------------
    # 维度3: 机构分歧机会识别
    # ------------------------------------------------------------------

    def detect_institutional_divergence(self, input_data: CapitalFlowInput) -> tuple[float, bool]:
        """
        机构分歧机会识别。

        机构资金线内部波动大（部分时段买入、部分时段卖出）→ 分歧度高 → 潜在机会。
        """
        cfg = self._config
        inst = input_data.institutional_inflow
        if len(inst) < 2:
            return 0.0, False

        positive = [x for x in inst if x > 0]
        negative = [x for x in inst if x < 0]
        total_abs = sum(abs(x) for x in inst)
        if total_abs <= 0:
            return 0.0, False

        # 分歧度 = min(正流入, 负流出) / 总绝对值
        pos_sum = sum(positive)
        neg_sum = abs(sum(negative))
        divergence = min(pos_sum, neg_sum) / total_abs

        opportunity = divergence >= cfg.institutional_divergence_min
        return round(divergence, 4), opportunity

    # ------------------------------------------------------------------
    # 维度4: 多线共振分析
    # ------------------------------------------------------------------

    def analyze_resonance(self, input_data: CapitalFlowInput) -> tuple[float, str]:
        """
        资金线多线共振分析。

        多条线同方向 → 共振强度高。
        返回(共振强度0~100, 方向up/down/neutral)。
        """
        cfg = self._config
        lines = [
            sum(input_data.main_force_inflow),
            sum(input_data.institutional_inflow),
            sum(input_data.retail_inflow),
            sum(input_data.hot_money_inflow),
        ]
        positive = sum(1 for x in lines if x > 0)
        negative = sum(1 for x in lines if x < 0)

        if positive >= cfg.resonance_min_lines:
            score = positive / 4.0 * 100.0
            return round(score, 2), "up"
        if negative >= cfg.resonance_min_lines:
            score = negative / 4.0 * 100.0
            return round(score, 2), "down"
        return 0.0, "neutral"

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _validate_input(self, data: CapitalFlowInput) -> bool:
        if not data.main_force_inflow or not data.institutional_inflow:
            return False
        if not data.retail_inflow or not data.hot_money_inflow:
            return False
        if not data.prices:
            return False
        return True

    def _compute_overall_score(
        self,
        pattern_conf: float,
        retail_frenzy: float,
        inst_div: float,
        resonance: float,
    ) -> float:
        """综合评分(0~100)。"""
        score = (
            pattern_conf * 0.35
            + (100.0 - retail_frenzy) * 0.20  # 散户狂热低=好
            + (inst_div * 100.0) * 0.20  # 分歧=机会
            + resonance * 0.25
        )
        return round(min(max(score, 0.0), 100.0), 2)

    def _degraded_result(self, reason: str) -> CapitalFlowPatternResult:
        return CapitalFlowPatternResult(
            pattern=CapitalFlowPattern.UNKNOWN.value,
            pattern_confidence=0.0,
            retail_frenzy_score=0.0,
            contrarian_signal="neutral",
            institutional_divergence=0.0,
            opportunity_detected=False,
            resonance_score=0.0,
            resonance_direction="neutral",
            overall_score=0.0,
            is_degraded=True,
            audit_trail=[{"dimension": "degraded", "reason": reason}],
        )


__all__ = [
    "CapitalFlowInput",
    "CapitalFlowPattern",
    "CapitalFlowPatternAnalyzer",
    "CapitalFlowPatternConfig",
    "CapitalFlowPatternResult",
]
