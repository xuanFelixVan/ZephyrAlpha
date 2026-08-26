# [BLUEPRINT] MOD-PA-014 | docs/03_modules/_domain_portfolio_alloc/strategy_screener_3d/blueprint.md
# [MODULE] zephyr.pf_alloc.core.strategy_screener_3d
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] 无（评估核心纯内存；相关性矩阵/回测序列/时钟全注入）
# [CONSUMERS] 运行时装配批（策略入库评审流水线装配 / 组合分配域策略准入闸）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三维词表闭合(return_clarity|param_stability|complementarity); 权重非负且Σ=1(容差1e-9); 阈值档0≤watchlist≤accept≤1; 维度得分∈[0,1]; 加权分=Σw×s; ≥accept→ACCEPT / ≥watchlist→WATCHLIST / 否则REJECT; 相关性矩阵双向查找缺失或越[-1,1]界Fail-Closed; 报告frozen; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_portfolio_alloc/strategy_screener_3d/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyScreenerError(占位 ZA-PA-UNREGISTERED-STRATEGY-SCREENER)——权重/阈值非法/空strategy_id/指标非有限/回测序列为空/相关性缺失或越界时抛
# [TESTS] tests/pf_alloc/test_strategy_screener_3d.py
# [A_module] module_id=MOD-PA-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""StrategyScreener3D — 策略筛选三维评估器（MOD-PA-014）。

B10-02090（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PFALLOC-009，A1 PA-02）：
策略入库**三维评分**——

① 收益风险清晰性（Sharpe/回撤/卡玛复合，按 0.5/0.2/0.3 归一合成）；
② 参数稳定性（参数邻域敏感性：邻域回测序列均值相对基准序列均值的平均
   相对偏离，越不敏感越稳定，回测序列注入）；
③ 天然互补性（与现有入库策略相关性矩阵注入，1−mean|ρ|；无现有策略=1.0）。

三维加权评分 + 入库建议阈值档（≥accept→ACCEPT 入库 / ≥watchlist→WATCHLIST
观察 / 否则 REJECT 淘汰）。

查重分工（蓝图 §0）：strategy_retirement_evaluator=在库策略退役评估（出库
侧）；strategy_correlation_gate=组合相关性二元门禁（是否允许共线）。本件
=**入库前三维评分**（准入打分与档位建议），不做退役、不做二元门禁。
"""

from __future__ import annotations

import datetime
import logging
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DIM_COMPLEMENTARITY",
    "DIM_PARAM_STABILITY",
    "DIM_RETURN_CLARITY",
    "DimensionScore",
    "ScreenerVerdict",
    "ScreeningReport",
    "StrategyScreener3D",
    "StrategyScreenerError",
]

DIM_RETURN_CLARITY: Final = "return_clarity"
DIM_PARAM_STABILITY: Final = "param_stability"
DIM_COMPLEMENTARITY: Final = "complementarity"
_DIMENSIONS: Final = (DIM_RETURN_CLARITY, DIM_PARAM_STABILITY, DIM_COMPLEMENTARITY)

_SHARPE_CAP: Final = 3.0
_CALMAR_CAP: Final = 3.0
_MAXDD_CAP: Final = 0.5
_WEIGHT_SUM_TOL: Final = 1e-9
_EPS: Final = 1e-12

_DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    DIM_RETURN_CLARITY: 0.4,
    DIM_PARAM_STABILITY: 0.3,
    DIM_COMPLEMENTARITY: 0.3,
}


class StrategyScreenerError(Exception):
    """策略筛选三维评估输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PA-UNREGISTERED-STRATEGY-SCREENER。
    """


class ScreenerVerdict(str, Enum):
    """入库建议阈值档。"""

    ACCEPT = "accept"          # 入库
    WATCHLIST = "watchlist"    # 观察
    REJECT = "reject"          # 淘汰


@dataclass(frozen=True)
class DimensionScore:
    """单维评分（frozen）。"""

    dimension: str
    score: float
    detail: str


@dataclass(frozen=True)
class ScreeningReport:
    """三维筛选报告（frozen，维度按名确定性排序）。"""

    strategy_id: str
    dimension_scores: tuple[DimensionScore, ...]
    weighted_score: float
    verdict: ScreenerVerdict
    accept_threshold: float
    watchlist_threshold: float
    evaluated_at: datetime.datetime


def _require_finite(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise StrategyScreenerError(f"{name} 须为有限数值: {value!r}")
    return float(value)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


class StrategyScreener3D:
    """策略入库三维评估器（纯内存确定性，时钟注入）。"""

    def __init__(
        self,
        *,
        weights: Mapping[str, float] | None = None,
        accept_threshold: float = 0.7,
        watchlist_threshold: float = 0.4,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        raw = dict(weights) if weights is not None else dict(_DEFAULT_WEIGHTS)
        if set(raw) != set(_DIMENSIONS):
            raise StrategyScreenerError(
                f"权重维度词表闭合校验失败: 须恰为 {sorted(_DIMENSIONS)}，实收 {sorted(raw)}"
            )
        for dim, w in raw.items():
            _require_finite(f"权重[{dim}]", w)
            if w < 0:
                raise StrategyScreenerError(f"权重[{dim}] 须非负: {w!r}")
        total = sum(raw.values())
        if abs(total - 1.0) > _WEIGHT_SUM_TOL:
            raise StrategyScreenerError(f"权重Σ须=1（容差{_WEIGHT_SUM_TOL}）: Σ={total!r}")
        _require_finite("accept_threshold", accept_threshold)
        _require_finite("watchlist_threshold", watchlist_threshold)
        if not (0.0 <= watchlist_threshold <= accept_threshold <= 1.0):
            raise StrategyScreenerError(
                f"阈值档非法（须 0≤watchlist≤accept≤1）: "
                f"watchlist={watchlist_threshold!r}, accept={accept_threshold!r}"
            )
        self._weights = raw
        self._accept_threshold = accept_threshold
        self._watchlist_threshold = watchlist_threshold
        self._clock = clock or datetime.datetime.now

    # ── 内部：三维评分 ────────────────────────────────────────────────────

    @staticmethod
    def _score_return_clarity(sharpe: float, max_drawdown: float, calmar: float) -> float:
        s_sharpe = _clamp01(sharpe / _SHARPE_CAP)
        s_dd = 1.0 - _clamp01(max_drawdown / _MAXDD_CAP)
        s_calmar = _clamp01(calmar / _CALMAR_CAP)
        return 0.5 * s_sharpe + 0.2 * s_dd + 0.3 * s_calmar

    @staticmethod
    def _score_param_stability(
        base_returns: Sequence[float], neighbor_returns: Mapping[str, Sequence[float]]
    ) -> tuple[float, float]:
        base_mean = sum(base_returns) / len(base_returns)
        deviations = []
        for label in sorted(neighbor_returns):
            series = neighbor_returns[label]
            neighbor_mean = sum(series) / len(series)
            deviations.append(abs(neighbor_mean - base_mean))
        sensitivity = (sum(deviations) / len(deviations)) / (abs(base_mean) + _EPS)
        return _clamp01(1.0 - sensitivity), sensitivity

    @staticmethod
    def _lookup_corr(
        correlation_matrix: Mapping[str, Mapping[str, float]], a: str, b: str
    ) -> float:
        row = correlation_matrix.get(a)
        if row is not None and b in row:
            return row[b]
        row = correlation_matrix.get(b)
        if row is not None and a in row:
            return row[a]
        raise StrategyScreenerError(f"相关性矩阵缺失配对: ({a!r}, {b!r})")

    def _score_complementarity(
        self,
        strategy_id: str,
        correlation_matrix: Mapping[str, Mapping[str, float]],
        incumbent_ids: Sequence[str],
    ) -> float:
        if not incumbent_ids:
            return 1.0
        corrs = []
        for inc in incumbent_ids:
            corr = _require_finite(
                f"相关性[{strategy_id}|{inc}]",
                self._lookup_corr(correlation_matrix, strategy_id, inc),
            )
            if not (-1.0 <= corr <= 1.0):
                raise StrategyScreenerError(f"相关性越界[-1,1]: {corr!r}")
            corrs.append(abs(corr))
        return _clamp01(1.0 - sum(corrs) / len(corrs))

    # ── 评估 ─────────────────────────────────────────────────────────────

    def evaluate(
        self,
        *,
        strategy_id: str,
        sharpe: float,
        max_drawdown: float,
        calmar: float,
        base_returns: Sequence[float],
        neighbor_returns: Mapping[str, Sequence[float]],
        correlation_matrix: Mapping[str, Mapping[str, float]],
        incumbent_ids: Sequence[str] = (),
    ) -> ScreeningReport:
        """三维评分 + 加权 + 阈值档判定（非法输入 Fail-Closed）。"""
        if not isinstance(strategy_id, str) or not strategy_id:
            raise StrategyScreenerError("strategy_id 为空")
        sharpe = _require_finite("sharpe", sharpe)
        calmar = _require_finite("calmar", calmar)
        max_drawdown = _require_finite("max_drawdown", max_drawdown)
        if max_drawdown < 0:
            raise StrategyScreenerError(f"max_drawdown 须非负（正数表回撤幅度）: {max_drawdown!r}")
        if not base_returns:
            raise StrategyScreenerError("base_returns 为空（参数稳定性基准序列缺失）")
        base = [_require_finite("base_returns[]", r) for r in base_returns]
        if not neighbor_returns:
            raise StrategyScreenerError("neighbor_returns 为空（参数邻域回测序列未注入）")
        neighbors: dict[str, list[float]] = {}
        for label, series in neighbor_returns.items():
            if not label:
                raise StrategyScreenerError("邻域参数标签为空")
            if not series:
                raise StrategyScreenerError(f"邻域回测序列为空: {label!r}")
            neighbors[label] = [_require_finite(f"neighbor_returns[{label!r}][]", r) for r in series]

        rc = self._score_return_clarity(sharpe, max_drawdown, calmar)
        ps, sensitivity = self._score_param_stability(base, neighbors)
        cp = self._score_complementarity(strategy_id, correlation_matrix, incumbent_ids)

        scores = {
            DIM_RETURN_CLARITY: DimensionScore(
                DIM_RETURN_CLARITY, rc,
                f"sharpe={sharpe}, max_drawdown={max_drawdown}, calmar={calmar}",
            ),
            DIM_PARAM_STABILITY: DimensionScore(
                DIM_PARAM_STABILITY, ps,
                f"邻域数={len(neighbors)}, 平均相对偏离={sensitivity:.6f}",
            ),
            DIM_COMPLEMENTARITY: DimensionScore(
                DIM_COMPLEMENTARITY, cp,
                f"现有策略数={len(incumbent_ids)}",
            ),
        }
        weighted = sum(self._weights[dim] * scores[dim].score for dim in _DIMENSIONS)
        if weighted >= self._accept_threshold:
            verdict = ScreenerVerdict.ACCEPT
        elif weighted >= self._watchlist_threshold:
            verdict = ScreenerVerdict.WATCHLIST
        else:
            verdict = ScreenerVerdict.REJECT
        report = ScreeningReport(
            strategy_id=strategy_id,
            dimension_scores=tuple(scores[dim] for dim in sorted(_DIMENSIONS)),
            weighted_score=weighted,
            verdict=verdict,
            accept_threshold=self._accept_threshold,
            watchlist_threshold=self._watchlist_threshold,
            evaluated_at=self._clock(),
        )
        _log.info(
            "策略三维筛选: %s weighted=%.4f verdict=%s", strategy_id, weighted, verdict.value
        )
        return report
