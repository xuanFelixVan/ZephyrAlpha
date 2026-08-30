# [BLUEPRINT] MOD-REGIME-015 | docs/03_modules/_domain_regime/institutional_regime_scorer/blueprint.md
# [MODULE] zephyr.regime.institutional_regime_scorer
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] 运行时装配批（regime 层综合评分 / 机构级三维数据融合）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 三维度独立可测; 单维缺失/非法→该维 degraded 不减权重; 综合 score=Σw_i×s_i/Σw_i（有效维度权重归一）; 输出 regime 态字典+置信度; 同输入必同输出
# [MODIFY-GUARD] tests/regime/test_institutional_regime_scorer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InstitutionalRegimeConfigError(ZA-REGIME-0038)
# [TESTS] tests/regime/test_institutional_regime_scorer.py
# [A_module] module_id=MOD-REGIME-015 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.7.6/§4.8.5/§4.11.10 #MOD-REGIME-015

"""MOD-REGIME-015 InstitutionalRegimeScorer — 三维机构级 regime 评分器。

真源：10_regime_detector_spec §4.7.6（CAPE 估值分位）、§4.8.5（Margin Debt/两融
杠杆极端）、§4.11.10（IV 隐含波动率维度）。三维度独立评分、fail-open 降级、
加权合成综合 regime_score。

数据消费（注入式，不直连数据库）：
  - CAPE 维度：index_valuation_daily（路 A 管道已投产）
  - IV 维度：option_iv_surface_incremental（tasks.yaml L767 管道在采）
  - 两融维度：margin_trading_incremental（tasks.yaml L95 管道在采）

评分语义（对齐 10 号文）：
  score ∈ [0, 100]，越高越危险/越极端（泡沫/恐慌方向）。
  0-33 低位安全区，34-66 中性区，67-100 高位极端区。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

import numpy as np

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_log = logging.getLogger(__name__)

__all__: Final = [
    "RegimeDimensionScore",
    "InstitutionalRegimeConfigError",
    "InstitutionalRegimeScorer",
    "InstitutionalRegimeScore",
    "RegimeState",
]


class InstitutionalRegimeConfigError(ZephyrBaseError):
    """机构级 regime 评分配置非法（Fail-Closed）。"""

    error_code = "ZA-REGIME-0038"


class RegimeState(str):
    """regime 态词表（闭合）。"""

    EXTREME_BUBBLE = "extreme_bubble"      # 极端泡沫（CAPE/IV/两融三高位）
    BUBBLE = "bubble"                      # 泡沫区（高估+杠杆+IV 偏高）
    NEUTRAL = "neutral"                    # 中性区
    PANIC = "panic"                        # 恐慌区（IV 飙升+两融骤降）
    EXTREME_PANIC = "extreme_panic"        # 极端恐慌（IV 极端+去杠杆完成）


# ──────────────────────────────────────────────────────────────────────────────
# 维度权重（对齐 10 号文 §4.8.5/§4.7.6/§4.11.10 权重表）
# ──────────────────────────────────────────────────────────────────────────────
WEIGHT_CAPE: Final[float] = 0.35   # 宏观估值（长期锚，§4.8.5 "高"）
WEIGHT_IV: Final[float] = 0.35     # IV 维度（前瞻性强，§4.11.10 "高"）
WEIGHT_MARGIN: Final[float] = 0.30  # 杠杆结构（平仓风险，§4.8.5 "高"）

# ──────────────────────────────────────────────────────────────────────────────
# CAPE 维度阈值（§4.7.6 维度⑨ / §4.8.5 维度④）
# ──────────────────────────────────────────────────────────────────────────────
CAPE_PERCENTILE_EXTREME: Final[float] = 0.95   # 近 20 年 >95 分位 → 极端
CAPE_PERCENTILE_HIGH: Final[float] = 0.80      # 近 20 年 >80 分位 → 高估
CAPE_PERCENTILE_LOW: Final[float] = 0.15       # 近 20 年 <15 分位 → 底部
CAPE_PERCENTILE_DEEP_LOW: Final[float] = 0.10  # 近 20 年 <10 分位 → 大底

# ──────────────────────────────────────────────────────────────────────────────
# IV 维度阈值（§4.11.10 维度⑨）
# ──────────────────────────────────────────────────────────────────────────────
IV_ABSOLUTE_PANIC: Final[float] = 35.0    # 合成 VIX >35 → 恐慌
IV_ABSOLUTE_EXTREME: Final[float] = 40.0  # 合成 VIX >40 → 极端恐慌
IV_PERCENTILE_EXTREME: Final[float] = 0.90  # IV 分位 >90 分位近 1 年 → 极端
IV_PERCENTILE_HIGH: Final[float] = 0.75     # IV 分位 >75 分位 → 偏高

# ──────────────────────────────────────────────────────────────────────────────
# 两融维度阈值（§4.7.6 维度⑩ / §4.8.5 维度⑥）
# ──────────────────────────────────────────────────────────────────────────────
MARGIN_RATIO_EXTREME: Final[float] = 0.025   # 两融余额/流通市值 >2.5% → 杠杆极端
MARGIN_RATIO_HIGH: Final[float] = 0.020      # 两融余额/流通市值 >2.0% → 杠杆高
MARGIN_DROP_EXTREME: Final[float] = 0.25     # 两融余额降幅从峰值 >25% → 去杠杆极端
MARGIN_DROP_HIGH: Final[float] = 0.15        # 两融余额降幅从峰值 >15% → 去杠杆
MARGIN_BUY_RATIO_COLD: Final[float] = 0.07   # 融资买入额占比 <7% → 冰点
MARGIN_BUY_RATIO_EXTREME_COLD: Final[float] = 0.05  # 融资买入额占比 <5% → 极端冰点


@dataclass(frozen=True)
class RegimeDimensionScore:
    """单维度评分结果（frozen）。"""

    score: float           # ∈ [0, 100]
    weight: float          # ∈ [0, 1]
    available: bool        # 数据是否可用（False=degraded）
    detail: dict[str, Any] # 维度内明细（调试用）


@dataclass(frozen=True)
class InstitutionalRegimeScore:
    """机构级 regime 综合评分输出（frozen）。"""

    regime_score: float              # 综合评分 ∈ [0, 100]
    regime_state: str                # RegimeState 词表
    confidence: float                # ∈ [0, 1]
    dimensions: dict[str, RegimeDimensionScore]  # cape / iv / margin
    degraded: bool                   # 是否降级（任一维度缺失）
    degraded_dimensions: tuple[str, ...]  # 缺失维度列表


class InstitutionalRegimeScorer:
    """三维机构级 regime 评分器。

    消费 index_valuation_daily / option_iv_surface_incremental /
    margin_trading_incremental 三源数据，独立评分后加权合成。

    降级哲学（fail-open）：
      单维数据缺失/非法 → 该维 available=False、score=0、detail 含原因，
      综合时权重归一（不减权重），输出 degraded=True + degraded_dimensions。
    """

    def __init__(
        self,
        *,
        weight_cape: float = WEIGHT_CAPE,
        weight_iv: float = WEIGHT_IV,
        weight_margin: float = WEIGHT_MARGIN,
    ) -> None:
        if weight_cape < 0.0:
            raise InstitutionalRegimeConfigError(f"weight_cape 非法负值: {weight_cape}")
        if weight_iv < 0.0:
            raise InstitutionalRegimeConfigError(f"weight_iv 非法负值: {weight_iv}")
        if weight_margin < 0.0:
            raise InstitutionalRegimeConfigError(f"weight_margin 非法负值: {weight_margin}")
        total = weight_cape + weight_iv + weight_margin
        if total <= 0.0:
            raise InstitutionalRegimeConfigError("权重和必须 > 0")
        self._w_cape = weight_cape / total
        self._w_iv = weight_iv / total
        self._w_margin = weight_margin / total

    # ──────────────────────────────────────────────────────────────────────
    # 公开入口
    # ──────────────────────────────────────────────────────────────────────

    def score(
        self,
        *,
        cape_percentile: float | None = None,
        cape_value: float | None = None,
        iv_synthetic_vix: float | None = None,
        iv_percentile_1y: float | None = None,
        margin_balance_ratio: float | None = None,
        margin_drop_from_peak: float | None = None,
        margin_buy_ratio: float | None = None,
    ) -> InstitutionalRegimeScore:
        """三维评分合成入口。

        Args:
            cape_percentile: CAPE 近 20 年分位 ∈ [0, 1]（index_valuation_daily）
            cape_value: CAPE 绝对值（辅助参考，非必要）
            iv_synthetic_vix: 合成 VIX 绝对值（option_iv_surface_incremental）
            iv_percentile_1y: IV 近 1 年分位 ∈ [0, 1]
            margin_balance_ratio: 两融余额/流通市值 ∈ [0, 1]
            margin_drop_from_peak: 两融余额从峰值降幅 ∈ [0, 1]（正数=降幅）
            margin_buy_ratio: 融资买入额占成交额比 ∈ [0, 1]

        Returns:
            InstitutionalRegimeScore（含综合 score/state/confidence/维度明细）
        """
        dims: dict[str, RegimeDimensionScore] = {}

        dims["cape"] = self._score_cape(cape_percentile, cape_value)
        dims["iv"] = self._score_iv(iv_synthetic_vix, iv_percentile_1y)
        dims["margin"] = self._score_margin(
            margin_balance_ratio, margin_drop_from_peak, margin_buy_ratio
        )

        # 有效维度权重归一
        valid = [(d.score, d.weight) for d in dims.values() if d.available]
        if not valid:
            # 全维缺失 → 无法评分，输出最低置信度中性态
            _log.warning("三维机构级数据全缺失，输出最低置信度中性态")
            return InstitutionalRegimeScore(
                regime_score=50.0,
                regime_state=RegimeState.NEUTRAL,
                confidence=0.0,
                dimensions=dims,
                degraded=True,
                degraded_dimensions=tuple(dims.keys()),
            )

        total_weight = sum(w for _, w in valid)
        composite = sum(s * w for s, w in valid) / total_weight

        degraded = any(not d.available for d in dims.values())
        degraded_dims = tuple(k for k, d in dims.items() if not d.available)

        # 置信度：有效维度占比 × 0.8 + 基础 0.2
        n_valid = len(valid)
        confidence = 0.2 + 0.8 * (n_valid / 3.0)

        state = self._map_state(composite, dims)

        return InstitutionalRegimeScore(
            regime_score=round(composite, 2),
            regime_state=state,
            confidence=round(confidence, 2),
            dimensions=dims,
            degraded=degraded,
            degraded_dimensions=degraded_dims,
        )

    # ──────────────────────────────────────────────────────────────────────
    # CAPE 维度（§4.7.6 维度⑨ / §4.8.5 维度④）
    # ──────────────────────────────────────────────────────────────────────

    def _score_cape(
        self,
        percentile: float | None,
        value: float | None,
    ) -> RegimeDimensionScore:
        """CAPE 分位映射评分。

        分位越高 → 估值越极端 → score 越高（泡沫方向）。
        """
        if percentile is None:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_cape,
                available=False,
                detail={"reason": "cape_percentile 缺失"},
            )
        if not 0.0 <= percentile <= 1.0:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_cape,
                available=False,
                detail={"reason": f"cape_percentile 越界: {percentile}"},
            )

        # 分位映射（§4.7.6：PE 分位 <15% 底部 / >95% 极端）
        # 语义：percentile 越高 → 估值越极端 → score 越高（泡沫方向）
        if percentile >= CAPE_PERCENTILE_EXTREME:
            score = 95.0   # >95% 极端泡沫
        elif percentile >= CAPE_PERCENTILE_HIGH:
            score = 75.0   # 80%~95% 高估
        elif percentile >= 0.50:
            score = 50.0   # 50%~80% 中性
        elif percentile >= 0.25:
            score = 40.0   # 25%~50% 偏低
        elif percentile >= CAPE_PERCENTILE_LOW:
            score = 25.0   # 15%~25% 底部区间
        elif percentile >= CAPE_PERCENTILE_DEEP_LOW:
            score = 10.0   # 10%~15% 大底
        else:
            score = 5.0    # <10% 极端大底

        detail: dict[str, Any] = {"percentile": percentile}
        if value is not None:
            detail["cape_value"] = value
            # CAPE 绝对值辅助修正（§4.8.5：>30 高估 / >40 极端）
            if value >= 40.0:
                score = max(score, 90.0)
            elif value >= 30.0:
                score = max(score, 70.0)

        return RegimeDimensionScore(
            score=score,
            weight=self._w_cape,
            available=True,
            detail=detail,
        )

    # ──────────────────────────────────────────────────────────────────────
    # IV 维度（§4.11.10 维度⑨）
    # ──────────────────────────────────────────────────────────────────────

    def _score_iv_absolute(
        self,
        synthetic_vix: float,
        scores: list[float],
        detail: dict[str, Any],
    ) -> None:
        """IV 绝对值映射（§4.9 / §4.11.10）。"""
        detail["synthetic_vix"] = synthetic_vix
        # 绝对值映射（§4.9 / §4.11.10：>25 恐慌 / >35 极端 / >40 历史极端）
        if synthetic_vix >= IV_ABSOLUTE_EXTREME:
            scores.append(95.0)
        elif synthetic_vix >= IV_ABSOLUTE_PANIC:
            scores.append(80.0)
        elif synthetic_vix >= 25.0:
            scores.append(65.0)
        elif synthetic_vix >= 20.0:
            scores.append(40.0)
        else:
            scores.append(20.0)

    def _score_iv_percentile(
        self,
        percentile_1y: float,
        scores: list[float],
        detail: dict[str, Any],
    ) -> None:
        """IV 分位映射（§4.11.10）。"""
        detail["percentile_1y"] = percentile_1y
        # 分位映射（§4.11.10：IV 分位 >90 极端）
        if percentile_1y >= IV_PERCENTILE_EXTREME:
            scores.append(90.0)
        elif percentile_1y >= IV_PERCENTILE_HIGH:
            scores.append(70.0)
        elif percentile_1y >= 0.50:
            scores.append(50.0)
        elif percentile_1y >= 0.25:
            scores.append(30.0)
        else:
            scores.append(15.0)

    def _score_iv(
        self,
        synthetic_vix: float | None,
        percentile_1y: float | None,
    ) -> RegimeDimensionScore:
        """IV 维度评分（合成 VIX 或 IV 分位映射）。

        IV 越高 → 恐慌越极端 → score 越高（恐慌方向）。
        """
        if synthetic_vix is None and percentile_1y is None:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_iv,
                available=False,
                detail={"reason": "iv_synthetic_vix 与 iv_percentile_1y 均缺失"},
            )

        scores: list[float] = []
        detail: dict[str, Any] = {}

        if synthetic_vix is not None:
            if synthetic_vix < 0.0:
                return RegimeDimensionScore(
                    score=0.0,
                    weight=self._w_iv,
                    available=False,
                    detail={"reason": f"iv_synthetic_vix 非法负值: {synthetic_vix}"},
                )
            self._score_iv_absolute(synthetic_vix, scores, detail)

        if percentile_1y is not None:
            if not 0.0 <= percentile_1y <= 1.0:
                return RegimeDimensionScore(
                    score=0.0,
                    weight=self._w_iv,
                    available=False,
                    detail={"reason": f"iv_percentile_1y 越界: {percentile_1y}"},
                )
            self._score_iv_percentile(percentile_1y, scores, detail)

        if not scores:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_iv,
                available=False,
                detail={"reason": "IV 双输入均缺失"},
            )

        return RegimeDimensionScore(
            score=round(float(np.mean(scores)), 2),
            weight=self._w_iv,
            available=True,
            detail=detail,
        )

    # ──────────────────────────────────────────────────────────────────────
    # 两融维度（§4.7.6 维度⑩ / §4.8.5 维度⑥）
    # ──────────────────────────────────────────────────────────────────────

    def _score_margin_balance(
        self,
        balance_ratio: float,
        scores: list[float],
        detail: dict[str, Any],
    ) -> None:
        """两融余额/流通市值占比评分（杠杆水平）。"""
        detail["balance_ratio"] = balance_ratio
        if balance_ratio >= MARGIN_RATIO_EXTREME:
            scores.append(90.0)
        elif balance_ratio >= MARGIN_RATIO_HIGH:
            scores.append(70.0)
        elif balance_ratio >= 0.015:
            scores.append(50.0)
        elif balance_ratio >= 0.010:
            scores.append(30.0)
        else:
            scores.append(15.0)

    def _score_margin_drop(
        self,
        drop_from_peak: float,
        scores: list[float],
        detail: dict[str, Any],
    ) -> None:
        """两融余额从峰值降幅评分（去杠杆程度）。"""
        detail["drop_from_peak"] = drop_from_peak
        # 降幅越大 → 去杠杆越极端 → 底部信号（score 反向：降幅大=恐慌）
        if drop_from_peak >= MARGIN_DROP_EXTREME:
            scores.append(85.0)
        elif drop_from_peak >= MARGIN_DROP_HIGH:
            scores.append(65.0)
        elif drop_from_peak >= 0.08:
            scores.append(40.0)
        else:
            scores.append(20.0)

    def _score_margin_buy(
        self,
        buy_ratio: float,
        scores: list[float],
        detail: dict[str, Any],
    ) -> None:
        """融资买入额占比评分（杠杆热度，反向指标）。"""
        detail["buy_ratio"] = buy_ratio
        # 占比越低 → 杠杆冰点 → 底部信号（score 反向）
        if buy_ratio <= MARGIN_BUY_RATIO_EXTREME_COLD:
            scores.append(85.0)
        elif buy_ratio <= MARGIN_BUY_RATIO_COLD:
            scores.append(65.0)
        elif buy_ratio <= 0.10:
            scores.append(40.0)
        else:
            scores.append(20.0)

    def _score_margin(
        self,
        balance_ratio: float | None,
        drop_from_peak: float | None,
        buy_ratio: float | None,
    ) -> RegimeDimensionScore:
        """两融维度评分（杠杆趋势/占比映射）。

        杠杆越高/去杠杆越极端 → score 越高（泡沫/恐慌方向）。
        """
        if balance_ratio is None and drop_from_peak is None and buy_ratio is None:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_margin,
                available=False,
                detail={"reason": "margin 三输入均缺失"},
            )

        scores: list[float] = []
        detail: dict[str, Any] = {}

        # ① 两融余额/流通市值占比（杠杆水平）
        if balance_ratio is not None:
            if not 0.0 <= balance_ratio <= 1.0:
                return RegimeDimensionScore(
                    score=0.0,
                    weight=self._w_margin,
                    available=False,
                    detail={"reason": f"margin_balance_ratio 越界: {balance_ratio}"},
                )
            self._score_margin_balance(balance_ratio, scores, detail)

        # ② 两融余额从峰值降幅（去杠杆程度）
        if drop_from_peak is not None:
            if not 0.0 <= drop_from_peak <= 1.0:
                return RegimeDimensionScore(
                    score=0.0,
                    weight=self._w_margin,
                    available=False,
                    detail={"reason": f"margin_drop_from_peak 越界: {drop_from_peak}"},
                )
            self._score_margin_drop(drop_from_peak, scores, detail)

        # ③ 融资买入额占比（杠杆热度，反向指标）
        if buy_ratio is not None:
            if not 0.0 <= buy_ratio <= 1.0:
                return RegimeDimensionScore(
                    score=0.0,
                    weight=self._w_margin,
                    available=False,
                    detail={"reason": f"margin_buy_ratio 越界: {buy_ratio}"},
                )
            self._score_margin_buy(buy_ratio, scores, detail)

        if not scores:
            return RegimeDimensionScore(
                score=0.0,
                weight=self._w_margin,
                available=False,
                detail={"reason": "margin 三输入均缺失"},
            )

        return RegimeDimensionScore(
            score=round(float(np.mean(scores)), 2),
            weight=self._w_margin,
            available=True,
            detail=detail,
        )

    # ──────────────────────────────────────────────────────────────────────
    # 综合态映射
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _dim_flags(
        dims: dict[str, RegimeDimensionScore],
    ) -> dict[str, bool]:
        """提取各维度高低标志（辅助 _map_state 降复杂度）。"""
        result: dict[str, bool] = {}
        for key in ("cape", "iv", "margin"):
            dim = dims.get(key)
            result[f"{key}_high"] = dim is not None and dim.available and dim.score >= 70.0
            result[f"{key}_low"] = dim is not None and dim.available and dim.score <= 30.0
        return result

    @staticmethod
    def _check_extreme_bubble(composite: float, flags: dict[str, bool]) -> bool:
        """极端泡沫判定：CAPE 高 + 两融杠杆高 + IV 不极端。"""
        return composite >= 65.0 and flags["cape_high"] and flags["margin_high"] and not flags["iv_high"]

    @staticmethod
    def _check_extreme_panic(composite: float, flags: dict[str, bool]) -> bool:
        """极端恐慌判定：IV 极端 + 两融去杠杆极端 + CAPE 低位。"""
        return composite >= 55.0 and flags["iv_high"] and flags["margin_high"] and flags["cape_low"]

    @staticmethod
    def _check_bubble(composite: float, flags: dict[str, bool]) -> bool:
        """泡沫区判定：综合高 + CAPE/两融至少一高 + IV 不极端。"""
        return composite >= 55.0 and (flags["cape_high"] or flags["margin_high"]) and not flags["iv_high"]

    @staticmethod
    def _check_panic(composite: float, flags: dict[str, bool]) -> bool:
        """恐慌区判定：综合高 + IV 高。"""
        return composite >= 55.0 and flags["iv_high"]

    @staticmethod
    def _map_state(
        composite: float,
        dims: dict[str, RegimeDimensionScore],
    ) -> str:
        """综合 score + 维度结构 → regime 态。

        语义（对齐 10 号文）：
          score 高 = 泡沫/恐慌极端（非方向性，是"极端程度"）。
          结合维度结构区分泡沫 vs 恐慌：
            CAPE 高 + IV 低 + 两融高 → 泡沫
            CAPE 低 + IV 高 + 两融去杠杆 → 恐慌
        """
        flags = InstitutionalRegimeScorer._dim_flags(dims)

        if InstitutionalRegimeScorer._check_extreme_bubble(composite, flags):
            return RegimeState.EXTREME_BUBBLE
        if InstitutionalRegimeScorer._check_extreme_panic(composite, flags):
            return RegimeState.EXTREME_PANIC
        if InstitutionalRegimeScorer._check_bubble(composite, flags):
            return RegimeState.BUBBLE
        if InstitutionalRegimeScorer._check_panic(composite, flags):
            return RegimeState.PANIC

        return RegimeState.NEUTRAL
