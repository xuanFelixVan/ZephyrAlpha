# [BLUEPRINT] MOD-RK-35 | docs/03_modules/_domain_risk/atr_stop_engine/blueprint.md
# [MODULE] zephyr.risk.atr_stop_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; scipy
# [CONSUMERS] D_SELL_DECISION(离场编排); MOD-SELL-014(风格止损框架口径互补); 回测参数优化批
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 止损间距=k×ATR14(波动率自适应); k体制映射(trend=3.5∈[3,4]/mean_reversion=1.75∈[1.5,2]/auto由ADX>25判); 追踪止损只上移不下移(多头); 分批止盈1/3@1R+1/3@2R+1/3追踪; 时间止损>N日且浮盈<1R触发; Bayesian优化留痕全部评估点; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAtrStopInputError
# [TESTS] tests/risk/test_atr_stop_engine.py
# [A_module] module_id=MOD-RK-35 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ATR Stop Engine — ATR 动态止损与 Bayesian 参数优化 (MOD-RK-35, CAND-RSK-038)

模块43 落码：Wilder(1978) ATR 止损经典——止损间距以波动率自适应单位 k×ATR14
参数化（替代固定百分比），并附 k 的离线参数优化：

  1. 初始止损 = entry − k×ATR（多头）；k 体制自适应：trend→3.5（3~4 区间中值）、
     mean_reversion→1.75（1.5~2 区间中值）、auto 由 ADX>25 判 trend 否则均值回归；
  2. 追踪止损 = max(历史 trailing, 持仓内最高价 − k×ATR)——只上移不下移；
  3. 分批止盈：1R=k×ATR，TP1=entry+1R（减 1/3）、TP2=entry+2R（再减 1/3）、
     余 1/3 走追踪止损（盈亏比 2:1 ≥ 1.5 下限）；
  4. 时间止损：持有 > N 日且浮盈 < 1R → 平仓标记；
  5. 参数优化：grid_search_k（对照基线）与 bayesian_optimize_k（轻量高斯过程
     RBF 核 + EI 采集，纯 numpy/scipy，无 sklearn 依赖）；目标函数由调用方注入
     （回测评分），全部评估点留痕。

与既有件分工：MOD-SELL-014 为"风格画像→百分比止损参数"映射框架；本模块为 ATR
波动率单位止损引擎（k 参数化 + Bayesian 优化），口径互补不重复。ATR14 由
D_FACTOR volatility 指标产出、调用方注入（本模块不越域自取数据，三维解耦）。

依据: blueprint.md（MOD-RK-35）§3 核心规则；Wilder (1978)；LuxAlgo ATR trailing
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 入场与波动
#   fields: entry_price(>0) + atr14(>0, D_FACTOR 注入)
#   code: build_plan() 参数
# - id: I2
#   name: 体制判定
#   fields: regime(TREND/MEAN_REVERSION/AUTO) + adx(AUTO 必填, >25→trend)
#   code: build_plan() 参数
# - id: I3
#   name: 持仓状态
#   fields: highest_price(持仓内最高) + current_price + holding_days
#   code: update_trailing_stop()/check_time_stop() 参数
# - id: I4
#   name: 配置 AtrStopConfig
#   fields: k_trend=3.5/k_mean_reversion=1.75/adx_threshold=25/time_stop_days=5/profit_fractions=(1/3,1/3,1/3)
#   code: AtrStopConfig
# 层: 算法
# - id: A1
#   name_zh: ① 体制自适应 k 解析
#   name_en: _resolve_k
#   intro: trend→k_trend, mean_reversion→k_mean_reversion, auto→ADX>25?trend:mr
# - id: A2
#   name_zh: ② 初始止损与R单位
#   name_en: build_plan
#   intro: 1R=k×ATR; initial=entry−1R; TP1/TP2=entry+1R/+2R(各减1/3)
# - id: A3
#   name_zh: ③ 追踪止损只上移
#   name_en: update_trailing_stop
#   intro: candidate=highest−1R; new=max(old,candidate) 不下移
# - id: A4
#   name_zh: ④ 时间止损
#   name_en: check_time_stop
#   intro: holding_days>N 且 current<entry+1R → due
# - id: A5
#   name_zh: ⑤ Bayesian k 优化
#   name_en: bayesian_optimize_k
#   intro: 网格初探→GP(RBF核)代理+EI采集序贯建议, 全评估点留痕
# 层: 输出
# - id: O1
#   name: AtrStopPlan
#   fields: initial_stop/r_unit/profit_target_1r/profit_target_2r/profit_target_fractions/current_trailing_stop
# - id: O2
#   name: BayesianOptimizationResult / GridSearchResult
#   fields: best_k/best_value/evaluations(留痕)
# 边:
# I1 --> A2
# I2 --> A1
# I4 --> A1
# I4 --> A4
# I3 --> A3
# I3 --> A4
# A1 --> A2
# A2 --> A3
# A2 --> A4
# A2 --> O1
# A5 --> O2
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Final

import numpy as np
from scipy.stats import norm as _norm

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AtrStopConfig",
    "AtrStopEngine",
    "AtrStopPlan",
    "BayesianOptimizationResult",
    "GridSearchResult",
    "InvalidAtrStopInputError",
    "StopRegime",
]

_GP_JITTER: Final = 1e-8


class InvalidAtrStopInputError(ZephyrBaseError):
    """ATR 止损引擎输入/配置非法（Fail-Closed）。"""


class StopRegime(str, Enum):
    """止损体制（k 自适应依据）。"""

    TREND = "TREND"  # 趋势（宽止损留喘息）
    MEAN_REVERSION = "MEAN_REVERSION"  # 均值回归（紧止损快认错）
    AUTO = "AUTO"  # 由 ADX>25 自动判定


@dataclass(frozen=True)
class AtrStopConfig:
    """ATR 止损引擎配置（C 类可调；默认值=候选登记真源）。"""

    k_trend: float = 3.5  # 趋势体制 k（3~4 区间中值）
    k_mean_reversion: float = 1.75  # 均值回归体制 k（1.5~2 区间中值）
    adx_threshold: float = 25.0  # AUTO 体制 ADX 分界
    time_stop_days: int = 5  # 时间止损 N 日
    profit_target_fractions: tuple[float, float, float] = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    def __post_init__(self) -> None:
        if not (math.isfinite(self.k_trend) and self.k_trend > 0):
            raise InvalidAtrStopInputError(f"k_trend 必须为正有限值: {self.k_trend}")
        if not (math.isfinite(self.k_mean_reversion) and self.k_mean_reversion > 0):
            raise InvalidAtrStopInputError(f"k_mean_reversion 必须为正有限值: {self.k_mean_reversion}")
        if not (math.isfinite(self.adx_threshold) and self.adx_threshold > 0):
            raise InvalidAtrStopInputError(f"adx_threshold 必须为正: {self.adx_threshold}")
        if self.time_stop_days < 1:
            raise InvalidAtrStopInputError(f"time_stop_days 必须 ≥1: {self.time_stop_days}")
        if len(self.profit_target_fractions) != 3 or any(
            f <= 0 or not math.isfinite(f) for f in self.profit_target_fractions
        ):
            raise InvalidAtrStopInputError(
                f"profit_target_fractions 须为 3 段正数: {self.profit_target_fractions}"
            )


@dataclass(frozen=True)
class AtrStopPlan:
    """一份 ATR 止损/止盈计划（frozen；trailing 经 with_trailing_stop 换发）。"""

    entry_price: float
    atr14: float
    k: float
    regime: StopRegime
    r_unit: float  # 1R = k×ATR
    initial_stop: float
    profit_target_1r: float
    profit_target_2r: float
    profit_target_fractions: tuple[float, float, float]
    current_trailing_stop: float


@dataclass(frozen=True)
class GridSearchResult:
    """网格搜索结果（留痕）。"""

    best_k: float
    best_value: float
    evaluations: tuple[tuple[float, float], ...]  # [(k, score)]


@dataclass(frozen=True)
class BayesianOptimizationResult:
    """Bayesian 优化结果（留痕）。"""

    best_k: float
    best_value: float
    evaluations: tuple[tuple[float, float], ...]  # [(k, score)] 初探+序贯全量


def _require_positive_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise InvalidAtrStopInputError(f"{name} 必须为正有限值: {value}")
    return v


def _gp_rbf_kernel(x1: np.ndarray, x2: np.ndarray, length_scale: float, signal_var: float) -> np.ndarray:
    d2 = (x1[:, None] - x2[None, :]) ** 2
    return signal_var * np.exp(-0.5 * d2 / (length_scale**2))


class AtrStopEngine:
    """ATR 动态止损引擎（k×ATR 参数化 + Bayesian/网格 k 优化）。"""

    def __init__(self, config: AtrStopConfig | None = None) -> None:
        self._config = config or AtrStopConfig()

    @property
    def config(self) -> AtrStopConfig:
        return self._config

    # ── ① 体制 k 解析 ────────────────────────────────────────────────

    def _resolve_k(self, regime: StopRegime, adx: float | None) -> float:
        cfg = self._config
        if regime is StopRegime.TREND:
            return cfg.k_trend
        if regime is StopRegime.MEAN_REVERSION:
            return cfg.k_mean_reversion
        if regime is StopRegime.AUTO:
            if adx is None:
                raise InvalidAtrStopInputError("regime=AUTO 必须提供 adx（ADX>25 判 trend）")
            adx_v = float(adx)
            if not math.isfinite(adx_v) or adx_v < 0:
                raise InvalidAtrStopInputError(f"adx 必须为非负有限值: {adx}")
            return cfg.k_trend if adx_v > cfg.adx_threshold else cfg.k_mean_reversion
        raise InvalidAtrStopInputError(f"非法 regime: {regime!r}")

    # ── ② 计划构建 ───────────────────────────────────────────────────

    def build_plan(
        self,
        *,
        entry_price: float,
        atr14: float,
        regime: StopRegime,
        adx: float | None = None,
    ) -> AtrStopPlan:
        """构建 ATR 止损/止盈计划（初始止损 + R 单位 + 分批止盈价位）。

        Args:
            entry_price: 入场价（>0）
            atr14: ATR14（>0，D_FACTOR volatility 指标注入）
            regime: 止损体制（AUTO 须给 adx）
            adx: AUTO 体制判定用 ADX（>25→trend）

        Returns:
            AtrStopPlan（trailing 初始=initial_stop）

        Raises:
            InvalidAtrStopInputError: 输入非法（Fail-Closed）
        """
        entry = _require_positive_finite("entry_price", entry_price)
        atr = _require_positive_finite("atr14", atr14)
        if not isinstance(regime, StopRegime):
            raise InvalidAtrStopInputError(f"regime 类型非法: {type(regime).__name__}")
        k = self._resolve_k(regime, adx)
        r_unit = k * atr
        return AtrStopPlan(
            entry_price=entry,
            atr14=atr,
            k=k,
            regime=regime,
            r_unit=r_unit,
            initial_stop=entry - r_unit,
            profit_target_1r=entry + r_unit,
            profit_target_2r=entry + 2.0 * r_unit,
            profit_target_fractions=self._config.profit_target_fractions,
            current_trailing_stop=entry - r_unit,
        )

    # ── ③ 追踪止损（只上移） ─────────────────────────────────────────

    def update_trailing_stop(self, plan: AtrStopPlan, *, highest_price: float) -> float:
        """按持仓内最高价更新追踪止损候选；只上移不下移（返回新止损价）。"""
        highest = float(highest_price)
        if not math.isfinite(highest) or highest <= 0:
            raise InvalidAtrStopInputError(f"highest_price 必须为正有限值: {highest_price}")
        candidate = highest - plan.r_unit
        return max(plan.current_trailing_stop, candidate)

    def with_trailing_stop(self, plan: AtrStopPlan, new_trailing_stop: float) -> AtrStopPlan:
        """换发带新追踪止损的计划（new 不得低于 old，防下移绕路）。"""
        new_stop = float(new_trailing_stop)
        if not math.isfinite(new_stop):
            raise InvalidAtrStopInputError(f"new_trailing_stop 必须为有限值: {new_trailing_stop}")
        if new_stop < plan.current_trailing_stop:
            raise InvalidAtrStopInputError(
                f"追踪止损只上移不下移: {new_stop} < {plan.current_trailing_stop}"
            )
        return AtrStopPlan(
            entry_price=plan.entry_price,
            atr14=plan.atr14,
            k=plan.k,
            regime=plan.regime,
            r_unit=plan.r_unit,
            initial_stop=plan.initial_stop,
            profit_target_1r=plan.profit_target_1r,
            profit_target_2r=plan.profit_target_2r,
            profit_target_fractions=plan.profit_target_fractions,
            current_trailing_stop=new_stop,
        )

    # ── ④ 时间止损 ───────────────────────────────────────────────────

    def check_time_stop(self, plan: AtrStopPlan, *, current_price: float, holding_days: int) -> bool:
        """时间止损判定：持有 > N 日且浮盈 < 1R → True（应平仓）。"""
        current = float(current_price)
        if not math.isfinite(current) or current <= 0:
            raise InvalidAtrStopInputError(f"current_price 必须为正有限值: {current_price}")
        if holding_days < 0:
            raise InvalidAtrStopInputError(f"holding_days 必须 ≥0: {holding_days}")
        if holding_days <= self._config.time_stop_days:
            return False
        return (current - plan.entry_price) < plan.r_unit

    # ── ⑤ 参数优化 ───────────────────────────────────────────────────

    def grid_search_k(
        self,
        objective: Callable[[float], float],
        *,
        k_bounds: tuple[float, float] = (1.0, 4.0),
        n_points: int = 31,
    ) -> GridSearchResult:
        """网格搜索 k（对照基线；全评估点留痕）。"""
        lo, hi = self._validate_bounds(k_bounds)
        if n_points < 2:
            raise InvalidAtrStopInputError(f"n_points 必须 ≥2: {n_points}")
        evaluations = tuple(
            (k, self._eval_objective(objective, k)) for k in np.linspace(lo, hi, n_points).tolist()
        )
        best_k, best_value = max(evaluations, key=lambda kv: kv[1])
        return GridSearchResult(best_k=best_k, best_value=best_value, evaluations=evaluations)

    def bayesian_optimize_k(
        self,
        objective: Callable[[float], float],
        *,
        k_bounds: tuple[float, float] = (1.0, 4.0),
        n_initial: int = 5,
        n_iterations: int = 12,
        random_seed: int = 20260825,
    ) -> BayesianOptimizationResult:
        """轻量 Bayesian 优化 k：RBF 核高斯过程代理 + EI 采集序贯建议。

        目标函数由调用方注入（回测评分，越大越好）。初探为均匀网格，
        序贯阶段每轮在 256 候选点上取 EI 最大者评估；全部评估点留痕。
        """
        lo, hi = self._validate_bounds(k_bounds)
        if n_initial < 2:
            raise InvalidAtrStopInputError(f"n_initial 必须 ≥2: {n_initial}")
        if n_iterations < 0:
            raise InvalidAtrStopInputError(f"n_iterations 必须 ≥0: {n_iterations}")

        xs: list[float] = np.linspace(lo, hi, n_initial).tolist()
        ys: list[float] = [self._eval_objective(objective, k) for k in xs]

        length_scale = 0.25 * (hi - lo)
        signal_var = 1.0
        noise = 1e-6
        candidates = np.linspace(lo, hi, 256)

        for _ in range(n_iterations):
            x = np.asarray(xs)
            y = np.asarray(ys)
            y_std = float(np.std(y))
            if y_std <= 0.0:
                # 目标恒定 → 无探索价值，提前收敛
                break
            k_mat = _gp_rbf_kernel(x, x, length_scale, signal_var) + (noise + _GP_JITTER) * np.eye(len(x))
            try:
                l_mat = np.linalg.cholesky(k_mat)
            except np.linalg.LinAlgError as exc:
                raise InvalidAtrStopInputError(f"GP 协方差矩阵病态，无法优化: {exc}") from exc
            alpha = np.linalg.solve(l_mat.T, np.linalg.solve(l_mat, y))
            k_cross = _gp_rbf_kernel(candidates, x, length_scale, signal_var)
            mu = k_cross @ alpha
            v = np.linalg.solve(l_mat, k_cross.T)
            var = np.maximum(signal_var - np.sum(v**2, axis=0), 0.0)
            sigma = np.sqrt(var)

            y_best = float(np.max(y))
            z = np.divide(mu - y_best, sigma, out=np.zeros_like(mu), where=sigma > 1e-12)
            ei = (mu - y_best) * _norm.cdf(z) + sigma * _norm.pdf(z)
            ei = np.where(sigma > 1e-12, ei, 0.0)
            k_next = float(candidates[int(np.argmax(ei))])
            xs.append(k_next)
            ys.append(self._eval_objective(objective, k_next))

        evaluations = tuple(zip(xs, ys, strict=True))
        best_k, best_value = max(evaluations, key=lambda kv: kv[1])
        return BayesianOptimizationResult(
            best_k=best_k,
            best_value=best_value,
            evaluations=evaluations,
        )

    # ── 内部 ─────────────────────────────────────────────────────────

    def _validate_bounds(self, k_bounds: tuple[float, float]) -> tuple[float, float]:
        if len(k_bounds) != 2:
            raise InvalidAtrStopInputError(f"k_bounds 须为 (lo, hi): {k_bounds}")
        lo, hi = float(k_bounds[0]), float(k_bounds[1])
        if not (math.isfinite(lo) and math.isfinite(hi)) or lo <= 0 or hi <= lo:
            raise InvalidAtrStopInputError(f"k_bounds 须满足 0<lo<hi: {k_bounds}")
        return lo, hi

    def _eval_objective(self, objective: Callable[[float], float], k: float) -> float:
        value = float(objective(k))
        if not math.isfinite(value):
            raise InvalidAtrStopInputError(f"目标函数在 k={k} 返回非有限值（Fail-Closed）")
        return value
