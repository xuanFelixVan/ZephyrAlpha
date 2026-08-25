# [BLUEPRINT] MOD-RK-31 | docs/03_modules/_domain_risk/black_swan_pattern_library/blueprint.md
# [MODULE] zephyr.risk.core.black_swan_pattern_library
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.position.core.drawdown_controller(MOD-POS-008,BlackSwanMode枚举唯一真源); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-30(Adaptive Risk Coordinator, black_swan_escalated 升级触发); 审计链(匹配记录持久化由调用方完成)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 7模板覆盖BS-001~007全模式; score∈[0,1]; matched=score≥threshold; ≥2模式命中或BS-007命中→escalate_to_c004(与BlackSwanSignal.has_black_swan语义一致); suggested_position_scale=命中模式最严; 无命中→scale=1.0; 纯函数无IO无未来函数
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidMarketFeaturesError; InvalidBlackSwanConfigError
# [TESTS] tests/risk/test_black_swan_pattern_library.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: MarketFeatures(7维市场体征: 波动率倍数/回撤/相关性/流动性萎缩/跳空/跌停潮/外围跌幅)
# I2: 7模式模板库(权重+参考水平+阈值+降仓建议) + BlackSwanConfig(统一阈值覆盖)
# A1: 逐模式加权相似度评分(score=Σw·clamp(f/r,0,1)/Σw)
# A2: 命中判定与升级规则(≥2模式或BS-007→escalate; 最严降仓建议)
# O1: BlackSwanScreenResult(matches/escalate/scale/matching_log) → C-004 升级+提前降仓+审计
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> O1
"""

Black Swan Pattern Library — C-038 黑天鹅模式库 (MOD-RK-31, MVP)

7 种黑天鹅模式（BS-001~BS-007）的事前特征模板库：当前市场 7 维体征与模板做加权
相似度匹配，超阈值 → 提前降仓建议；命中 ≥2 模式（或显式 BS-007）→
escalate_to_c004=True 升级触发 C-004（MOD-RK-30，KILL_SWITCH 建议语义）。

与存量分工（W1c 整合裁定，不复制）：模式枚举唯一真源 = MOD-POS-008
drawdown_controller.BlackSwanMode（import 复用）；drawdown_controller 管事中响应
（信号触发 → cap 查表），本库管事前相似度匹配（特征逼近 → 提前降仓），
≥2 模式命中 = BS-007 的语义两侧一致。匹配记录纯数据产出，审计持久化由调用方完成。

SSoT: docs/03_modules/_domain_risk/black_swan_pattern_library/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

from zephyr.position.core.drawdown_controller import BlackSwanMode
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BlackSwanConfig",
    "BlackSwanPattern",
    "BlackSwanScreenResult",
    "InvalidBlackSwanConfigError",
    "InvalidMarketFeaturesError",
    "MarketFeatures",
    "PatternMatchEntry",
    "get_pattern_templates",
    "screen_black_swan",
]


class InvalidMarketFeaturesError(ZephyrBaseError):
    """市场体征输入非法（Fail-Closed）。"""


class InvalidBlackSwanConfigError(ZephyrBaseError):
    """黑天鹅匹配配置非法（Fail-Closed）。"""


@dataclass(frozen=True)
class MarketFeatures:
    """当前市场 7 维体征（全部非负有限；幅度类为小数占比）。

    Attributes:
        volatility_ratio: 当前波动率 / 60 日均波动率（1=常态）
        drawdown_pct: 近期回撤幅度（正数占比）
        avg_correlation: 组合平均成对相关（0~1）
        liquidity_shrink: 流动性萎缩度（1 - 量比，0=不萎缩）
        gap_pct: 跳空幅度（占比）
        limit_down_ratio: 跌停标的占比（跌停潮）
        cross_market_drop: 外围市场跌幅（正数占比）
    """

    volatility_ratio: float
    drawdown_pct: float
    avg_correlation: float
    liquidity_shrink: float
    gap_pct: float
    limit_down_ratio: float
    cross_market_drop: float

    def __post_init__(self) -> None:
        for f in ("volatility_ratio", "drawdown_pct", "avg_correlation", "liquidity_shrink", "gap_pct", "limit_down_ratio", "cross_market_drop"):
            v = getattr(self, f)
            if not math.isfinite(v) or v < 0.0:
                raise InvalidMarketFeaturesError(f"{f} 必须为非负有限值: {v}")


@dataclass(frozen=True)
class BlackSwanPattern:
    """单模式特征模板（权重 + 参考水平 + 阈值 + 降仓建议）。"""

    mode: BlackSwanMode
    name: str
    weights: Mapping[str, float]  # 特征名 → 权重（>0）
    references: Mapping[str, float]  # 特征名 → 危险参考水平（>0，与 weights 同键）
    threshold: float  # 命中阈（∈(0,1]）
    suggested_position_scale: float  # 命中后建议仓位缩放（∈[0,1]）

    def __post_init__(self) -> None:
        if set(self.weights) != set(self.references):
            raise InvalidBlackSwanConfigError(f"{self.mode.value} 模板 weights 与 references 键集不一致")
        if not self.weights:
            raise InvalidBlackSwanConfigError(f"{self.mode.value} 模板权重为空")
        for k, w in self.weights.items():
            if not math.isfinite(w) or w <= 0.0:
                raise InvalidBlackSwanConfigError(f"{self.mode.value} 权重必须 >0: {k}={w}")
        for k, r in self.references.items():
            if not math.isfinite(r) or r <= 0.0:
                raise InvalidBlackSwanConfigError(f"{self.mode.value} 参考水平必须 >0: {k}={r}")
        if not 0.0 < self.threshold <= 1.0:
            raise InvalidBlackSwanConfigError(f"{self.mode.value} 阈值必须 ∈ (0,1]: {self.threshold}")
        if not 0.0 <= self.suggested_position_scale <= 1.0:
            raise InvalidBlackSwanConfigError(f"{self.mode.value} 降仓建议必须 ∈ [0,1]: {self.suggested_position_scale}")


def _p(mode: BlackSwanMode, name: str, refs: dict[str, float], scale: float, threshold: float = 0.8) -> BlackSwanPattern:
    """模板构造（等权基准；参考水平即危险量级，评分按 f/ref 截断归一）。"""
    weights = {k: 1.0 for k in refs}
    return BlackSwanPattern(mode=mode, name=name, weights=weights, references=refs, threshold=threshold, suggested_position_scale=scale)


#: 7 模式模板库（代码 SSoT；参考水平=危险量级经验基线，C 类可经模板替换调参）
_PATTERN_TEMPLATES: Final = MappingProxyType(
    {
        BlackSwanMode.BS001_LIQUIDITY: _p(
            BlackSwanMode.BS001_LIQUIDITY, "流动性枯竭",
            {"liquidity_shrink": 0.7, "limit_down_ratio": 0.2, "volatility_ratio": 2.0}, 0.5,
        ),
        BlackSwanMode.BS002_CORRELATION: _p(
            BlackSwanMode.BS002_CORRELATION, "相关性崩塌",
            {"avg_correlation": 0.8, "volatility_ratio": 2.0}, 0.5,
        ),
        BlackSwanMode.BS003_VOLATILITY: _p(
            BlackSwanMode.BS003_VOLATILITY, "波动爆表",
            {"volatility_ratio": 3.0, "drawdown_pct": 0.10, "gap_pct": 0.03}, 0.5,
        ),
        BlackSwanMode.BS004_MARGIN: _p(
            BlackSwanMode.BS004_MARGIN, "杠杆追缴",
            {"drawdown_pct": 0.15, "volatility_ratio": 2.5, "liquidity_shrink": 0.5}, 0.5,
        ),
        BlackSwanMode.BS005_CONTAGION: _p(
            BlackSwanMode.BS005_CONTAGION, "跨市场传导",
            {"cross_market_drop": 0.05, "gap_pct": 0.02, "avg_correlation": 0.6}, 0.7,
        ),
        BlackSwanMode.BS006_POLICY: _p(
            BlackSwanMode.BS006_POLICY, "政策事件",
            {"gap_pct": 0.03, "volatility_ratio": 2.5, "limit_down_ratio": 0.15}, 0.7,
        ),
        BlackSwanMode.BS007_SYSTEMIC: _p(
            BlackSwanMode.BS007_SYSTEMIC, "系统性风险",
            {"drawdown_pct": 0.25, "volatility_ratio": 4.0, "avg_correlation": 0.9, "liquidity_shrink": 0.8}, 0.0,
        ),
    }
)


def get_pattern_templates() -> Mapping[BlackSwanMode, BlackSwanPattern]:
    """返回 7 模式模板库（只读映射）。"""
    return _PATTERN_TEMPLATES


@dataclass(frozen=True)
class BlackSwanConfig:
    """匹配配置（C 类可调参数）。

    Attributes:
        match_threshold: 统一命中阈覆盖（None → 用各模板自身阈值）
    """

    match_threshold: float | None = None

    def __post_init__(self) -> None:
        if self.match_threshold is not None and not 0.0 < self.match_threshold <= 1.0:
            raise InvalidBlackSwanConfigError(f"match_threshold 必须 ∈ (0,1]: {self.match_threshold}")


@dataclass(frozen=True)
class PatternMatchEntry:
    """单模式匹配记录（审计留痕）。"""

    mode: BlackSwanMode
    score: float
    threshold: float
    matched: bool


@dataclass(frozen=True)
class BlackSwanScreenResult:
    """黑天鹅事前筛查结果。"""

    matched_modes: tuple[BlackSwanMode, ...]
    escalate_to_c004: bool  # ≥2 模式命中或 BS-007 命中
    suggested_position_scale: float  # 命中模式最严降仓建议（无命中=1.0）
    matching_log: tuple[PatternMatchEntry, ...]  # 全模式留痕


def _score(pattern: BlackSwanPattern, features: MarketFeatures) -> float:
    num = 0.0
    den = 0.0
    for name, w in pattern.weights.items():
        ref = pattern.references[name]
        f = getattr(features, name)
        num += w * min(max(f / ref, 0.0), 1.0)
        den += w
    return num / den if den > 0.0 else 0.0


def screen_black_swan(
    features: MarketFeatures,
    *,
    config: BlackSwanConfig | None = None,
) -> BlackSwanScreenResult:
    """黑天鹅模式事前筛查主入口。

    Args:
        features: 当前市场 7 维体征
        config: 配置（None → 各模板自身阈值）

    Returns:
        BlackSwanScreenResult
    """
    cfg = config or BlackSwanConfig()
    log: list[PatternMatchEntry] = []
    matched: list[BlackSwanMode] = []
    for mode, pattern in _PATTERN_TEMPLATES.items():
        threshold = cfg.match_threshold if cfg.match_threshold is not None else pattern.threshold
        score = _score(pattern, features)
        hit = score >= threshold
        log.append(PatternMatchEntry(mode=mode, score=score, threshold=threshold, matched=hit))
        if hit:
            matched.append(mode)

    escalate = len(matched) >= 2 or BlackSwanMode.BS007_SYSTEMIC in matched
    if matched:
        scale = min(_PATTERN_TEMPLATES[m].suggested_position_scale for m in matched)
    else:
        scale = 1.0

    return BlackSwanScreenResult(
        matched_modes=tuple(matched),
        escalate_to_c004=escalate,
        suggested_position_scale=scale,
        matching_log=tuple(log),
    )
