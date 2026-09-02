# [BLUEPRINT] MOD-PLAN-017 | 待统筹登记（45号 §4 W2 + 缺口总账 GAP-F-01）
# [MODULE] zephyr.plan_engine.scenario_probability_model
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.premarket_constraint_loader(SCENARIO_LIST); zephyr.signal_ashare.next_day_8state_forecast(NextDayState/NextDayForecast); zephyr.reporting.prediction_log_writer(log_prediction/query_predictions)
# [CONSUMERS] 作战室 W2 矩阵 9 格概率%（compute/forecast 输出）; MOD-PLAN-010 Brier 多分类校准（scenario_probability 预测行×outcome 回写消费位）; W6 历史预案库回看
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三层融合核纯函数（不依赖 DB/不依赖随机数，密度层准蒙特卡洛定数网格确定性输出）; 融合权重和=1 校验 fail-closed; 缺层降级重归一+留痕; 输出 9 格行和=1 归一; 落库 append-only 经 prediction_log_writer 公共 API 零裸 SQL; 错误消息不含 session_id
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（trade_date/权重/分位数/8态分布/actual_scenario 非法 fail-closed）; 三层数据供给异常 fail-open 降级留痕（缺层重归一）; 落库失败 fail-open 返回 -1
# [TESTS] tests/plan_engine/test_scenario_probability_model.py
# [A_module] module_id=MOD-PLAN-017 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

ScenarioProbabilityModel — 情景概率分布模型 (MOD-PLAN-017)

45号作战手册 §4 W2 + 缺口总账 GAP-F-01（总单标注"最难"）落码：作战室 W2 矩阵
9 格各赋概率%（PIT 概率分布，非点位预测——与 90号 §7"只出概率分布不出点位"
裁定一致）。架构裁定（第一性原理+量化社区实践）：9 格概率=三层融合——

    - 基础率层（base_rate）：MOD-PLAN-008 落库的历史 outcome 实际命中格
      （payload.actual_scenario）经验频率（Laplace 平滑）；样本不足
      （< min_base_samples）→ 全 1/9 均匀 + degraded 低置信标记（不伪造精度）。
    - 状态条件层（state_conditional）：MOD-SIG-037 次日 8 态马尔可夫分布 →
      9 格映射（STATE_TO_GRID_MASS 条件质量折算；FLAT_CLOSE→平开洗盘格，
      VIOLENT 无开盘/方向信息 → 均匀摊 9 格，诚实表达不确定）。
    - 密度头层（density_head）：MOD-ML-DENSITY 分位数序列（q10~q90 单调带）
      → 准蒙特卡洛（定数均匀网格逆 CDF 分段线性插值+两端线性外推，零随机数）
      采样次日收益 → gap_share 拆分隔夜缺口/日内走势 → 开盘桶×走势桶 9 格
      概率质量折算（全日收益代理 30 分钟走势口径，近似层，置信先验
      density_layer_confidence 默认 0.5 待标定）。

三层可配权重合成（默认 0.5/0.3/0.2 初拍待标定），权重和=1 校验 fail-closed；
缺层（供给不可用/异常）→ 剩余层权重重归一 + degraded_layers 留痕（G4 反误导：
降级显式可见）。输出=9 格概率分布（行和=1）+ 每格置信度（跨层一致性×层自置信
加权）+ 各层样本数 + 降级标记；落库 prediction_log（module=
"plan_engine.scenario_probability_model"，prediction_type="scenario_probability"，
append-only 幂等保首条），payload 携 probabilities/top_scenario 供 MOD-PLAN-010
多分类 Brier 校准消费（验证口径已在其头部 CONSUMERS 预留）。

不做什么：不出点位/不出买卖信号（90号 §7 边界）/不判定命中（回写方职责，
44号 §12.1 M4-④ 裁定二）/不做三维归因（归 MOD-PLAN-009）/不改
scenario_plan_recorder 与 density_quantile_trainer 任何计算核（稳定节点零破坏）。

依据: 45_warroom_playbook §4 W2 + §6 缺口⑥；缺口总账 GAP-F-01；90号 §7；44号 §12.1
SSoT: depgraph MOD-PLAN-017（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 历史 outcome.actual_scenario 序列 / MOD-SIG-037 8 态分布 / MOD-ML-DENSITY 分位数带
# 特征: 9 格经验频率 / 8 态→9 格条件质量 / 分位数逆 CDF 准蒙特卡洛收益样本
# 算法: 三层各自产 9 格分布 → 可配权重合成（缺层重归一）→ 行和归一 + 每格置信度
# 输出: ScenarioProbabilityForecast（9 格概率+每格置信+样本数+降级标记，JSON 可序列化）

"""

from __future__ import annotations

import dataclasses
import datetime
import json
import logging
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.reporting.prediction_log_writer import log_prediction, query_predictions
from zephyr.signal_ashare.next_day_8state_forecast import NextDayForecast, NextDayState

log = logging.getLogger(__name__)

__all__: Final = [
    "BASE_SOURCE_MODULE",
    "DEFAULT_CONFIG",
    "LAYER_BASE_RATE",
    "LAYER_DENSITY_HEAD",
    "LAYER_STATE_CONDITIONAL",
    "MODULE_LOG_NAME",
    "PREDICTION_TYPE_SCENARIO_PROBABILITY",
    "STATE_TO_GRID_MASS",
    "LayerDistribution",
    "ScenarioProbabilityConfig",
    "ScenarioProbabilityForecast",
    "ScenarioProbabilityModel",
    "base_rate_distribution",
    "build_scenario_probability_forecast",
    "density_grid_distribution",
    "fuse_distributions",
    "map_state_distribution",
    "state_conditional_distribution",
]

# ── 落库口径常量 ──

MODULE_LOG_NAME: Final = "plan_engine.scenario_probability_model"  # prediction_log.module（产出模块口径）
PREDICTION_TYPE_SCENARIO_PROBABILITY: Final = "scenario_probability"  # 预测族（接 MOD-PLAN-010 校准消费位）
_OUTCOME_PREDICTION_TYPE: Final = "outcome"  # outcome 族（prediction_log 单一账本，裁定一）
BASE_SOURCE_MODULE: Final = "plan_engine.scenario_planner"  # 基础率层数据源（MOD-PLAN-008 outcome 落库 module 口径）
_BASE_QUERY_LIMIT: Final = 10000  # 窗口内 outcome 行数上限（骨架期远大于实际量级）

# ── 三层标识与默认权重（初拍 0.5/0.3/0.2，待 MOD-PLAN-010 校准标定）──

LAYER_BASE_RATE: Final = "base_rate"
LAYER_STATE_CONDITIONAL: Final = "state_conditional"
LAYER_DENSITY_HEAD: Final = "density_head"
_LAYER_NAMES: Final = (LAYER_BASE_RATE, LAYER_STATE_CONDITIONAL, LAYER_DENSITY_HEAD)

# ── 9 格语义：情景 → (开盘桶, 走势桶)（与 MOD-PLAN-008 determine_actual_scenario 同口径）──

_SCENARIO_BUCKETS: Final = {
    "HIGH_OPEN_REAL_UP": ("HIGH", "UP"),
    "HIGH_OPEN_FAKE_UP": ("HIGH", "DOWN"),
    "HIGH_OPEN_WASH": ("HIGH", "WASH"),
    "LOW_OPEN_REAL_DOWN": ("LOW", "DOWN"),
    "LOW_OPEN_FAKE_DOWN": ("LOW", "UP"),
    "LOW_OPEN_WASH": ("LOW", "WASH"),
    "FLAT_OPEN_REAL_UP": ("FLAT", "UP"),
    "FLAT_OPEN_REAL_DOWN": ("FLAT", "DOWN"),
    "FLAT_OPEN_WASH": ("FLAT", "WASH"),
}
_BUCKET_TO_SCENARIO: Final = {v: k for k, v in _SCENARIO_BUCKETS.items()}

# ── 8 态 → 9 格条件质量映射（状态条件层契约）──
# 口径：马尔可夫 8 态（缺口 ±0.5%/收平 ±0.3%/振幅 3%）与 9 格（开盘 ±2%×30 分钟
# 走势 ±0.1%）粒度不同，属条件概率近似调整；FLAT_CLOSE（震荡收平）无缺口方向
# 信息 → 平开洗盘格；VIOLENT（剧烈震荡）无开盘/方向信息 → 均匀摊 9 格（诚实
# 表达不确定，不伪造集中质量）。每态质量行和=1。

STATE_TO_GRID_MASS: Final = {
    NextDayState.GAP_UP_UP: {"HIGH_OPEN_REAL_UP": 1.0},
    NextDayState.GAP_UP_DOWN: {"HIGH_OPEN_FAKE_UP": 1.0},
    NextDayState.GAP_DOWN_UP: {"LOW_OPEN_FAKE_DOWN": 1.0},
    NextDayState.GAP_DOWN_DOWN: {"LOW_OPEN_REAL_DOWN": 1.0},
    NextDayState.FLAT_UP: {"FLAT_OPEN_REAL_UP": 1.0},
    NextDayState.FLAT_DOWN: {"FLAT_OPEN_REAL_DOWN": 1.0},
    NextDayState.FLAT_CLOSE: {"FLAT_OPEN_WASH": 1.0},
    NextDayState.VIOLENT: {s: 1.0 / len(SCENARIO_LIST) for s in SCENARIO_LIST},
}

_WEIGHT_SUM_TOL: Final = 1e-6  # 权重和校验容差
_PROB_SUM_TOL: Final = 1e-6  # 分布和校验容差
_AGREEMENT_EPS: Final = 1e-12  # 一致性分母保护
_UNIFORM_PROB: Final = 1.0 / len(SCENARIO_LIST)  # 均匀兜底单格概率（1/9）


# ── 基础工具 ──


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None（区别于 0.0，供降级判定）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(trade_date, str):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        datetime.date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


def _validate_prob(value: object, name: str) -> float:
    """概率校验：有限实数且 ∈ [0,1]（fail-closed）。"""
    f = _safe_float(value)
    if f is None or not (0.0 <= f <= 1.0):
        raise ValueError(f"{name} 非法（须 [0,1] 有限实数）: {value!r}")
    return f


def _validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    """融合权重校验（fail-closed）：键⊆三层标识、各∈[0,1]、行和=1。"""
    if not isinstance(weights, Mapping) or not weights:
        raise ValueError(f"weights 非法（须非空映射）: {weights!r}")
    out: dict[str, float] = {}
    for k, v in weights.items():
        if k not in _LAYER_NAMES:
            raise ValueError(f"weights 含未知层标识: {k!r}")
        out[k] = _validate_prob(v, f"weights[{k!r}]")
    total = sum(out.values())
    if abs(total - 1.0) > _WEIGHT_SUM_TOL:
        raise ValueError(f"weights 行和须=1（±{_WEIGHT_SUM_TOL}）: 实得 {total!r}")
    return out


# ── 配置契约（参数 >7 收 dataclass，§5.150）──


@dataclass(frozen=True)
class ScenarioProbabilityConfig:
    """三层融合配置（默认值=初拍待标定，45号 §4 W2 口径）。

    Attributes
    ----------
    weight_base / weight_state / weight_density : 三层融合权重（行和=1，fail-closed）。
    base_window_days : 基础率层回溯窗口（自然日，PIT：不含预测当日）。
    min_base_samples : 基础率最小样本数（不足→均匀兜底+degraded 低置信标记）。
    base_support_full : 基础率置信度=1 所需样本数（线性缩放，与 MOD-SIG-037 同族口径）。
    base_laplace_alpha : 基础率 Laplace 平滑强度（防小样本零格）。
    density_mc_samples : 密度层准蒙特卡洛采样数（定数均匀网格，确定性）。
    density_gap_share : 收益样本拆分隔夜缺口占比（0~1；全日收益→开盘桶代理）。
    density_open_threshold : 密度层开盘桶阈值（默认 ±2%，与 MOD-PLAN-008 对齐）。
    density_trend_tolerance : 密度层走势平走容忍带（全日口径代理，区别于
        recorder 30 分钟 ±0.1%——密度头只见全日收益，近似层口径写清）。
    density_layer_confidence : 密度层置信先验（MVP 近似层，默认 0.5 待标定）。
    """

    weight_base: float = 0.5
    weight_state: float = 0.3
    weight_density: float = 0.2
    base_window_days: int = 60
    min_base_samples: int = 20
    base_support_full: int = 60
    base_laplace_alpha: float = 1.0
    density_mc_samples: int = 2000
    density_gap_share: float = 0.4
    density_open_threshold: float = 0.02
    density_trend_tolerance: float = 0.003
    density_layer_confidence: float = 0.5

    def __post_init__(self) -> None:
        _validate_weights(
            {
                LAYER_BASE_RATE: self.weight_base,
                LAYER_STATE_CONDITIONAL: self.weight_state,
                LAYER_DENSITY_HEAD: self.weight_density,
            }
        )
        for name in ("base_window_days", "min_base_samples", "base_support_full", "density_mc_samples"):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise ValueError(f"{name} 非法（须正整数）: {v!r}")
        if self.base_support_full < self.min_base_samples:
            raise ValueError(
                f"base_support_full 须 ≥ min_base_samples: {self.base_support_full} < {self.min_base_samples}"
            )
        alpha = _safe_float(self.base_laplace_alpha)
        if alpha is None or alpha < 0:
            raise ValueError(f"base_laplace_alpha 非法（须非负实数）: {self.base_laplace_alpha!r}")
        share = _safe_float(self.density_gap_share)
        if share is None or not (0.0 <= share <= 1.0):
            raise ValueError(f"density_gap_share 非法（须 [0,1]）: {self.density_gap_share!r}")
        th = _safe_float(self.density_open_threshold)
        if th is None or th <= 0:
            raise ValueError(f"density_open_threshold 非法（须正实数）: {self.density_open_threshold!r}")
        tol = _safe_float(self.density_trend_tolerance)
        if tol is None or tol < 0:
            raise ValueError(f"density_trend_tolerance 非法（须非负实数）: {self.density_trend_tolerance!r}")
        _validate_prob(self.density_layer_confidence, "density_layer_confidence")


DEFAULT_CONFIG: Final = ScenarioProbabilityConfig()


# ── 输出契约 ──


@dataclass(frozen=True)
class LayerDistribution:
    """单层 9 格分布（三层融合输入契约）。"""

    name: str  # 层标识（base_rate/state_conditional/density_head）
    probabilities: dict[str, float]  # 9 格概率（行和=1）
    confidence: float  # 层自置信度 ∈ [0,1]
    sample_size: int  # 层样本数（基础率=outcome 数；状态=转移数；密度=准蒙特卡洛采样数）
    degraded: bool = False  # 降级标记（如基础率样本不足均匀兜底）
    detail: dict[str, Any] = field(default_factory=dict)  # 留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "name": self.name,
            "probabilities": dict(self.probabilities),
            "confidence": self.confidence,
            "sample_size": self.sample_size,
            "degraded": self.degraded,
            "detail": dict(self.detail),
        }


@dataclass(frozen=True)
class ScenarioProbabilityForecast:
    """9 格概率分布预测（W2 矩阵消费契约，JSON 可序列化）。"""

    trade_date: str
    probabilities: dict[str, float]  # 9 格融合概率（行和=1）
    cell_confidence: dict[str, float]  # 每格置信度（跨层一致性×层自置信）
    top_scenario: str  # 众数格（概率最大，平局取 SCENARIO_LIST 序前者）
    top_probability: float
    samples: dict[str, int]  # 各层样本数
    weights_used: dict[str, float]  # 实际生效权重（缺层重归一后）
    degraded_layers: tuple[str, ...]  # 配置有权但缺失的层（重归一留痕）
    low_confidence: bool  # 低置信总标（基础率均匀兜底/整体置信 <0.5）
    detail: dict[str, Any] = field(default_factory=dict)  # 留痕（层明细等）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（prediction_log payload + W2 前端/校准消费契约）。"""
        return {
            "trade_date": self.trade_date,
            "probabilities": dict(self.probabilities),
            "cell_confidence": dict(self.cell_confidence),
            "top_scenario": self.top_scenario,
            "top_probability": self.top_probability,
            "samples": dict(self.samples),
            "weights_used": dict(self.weights_used),
            "degraded_layers": list(self.degraded_layers),
            "low_confidence": self.low_confidence,
            "detail": dict(self.detail),
        }


# ── 基础率层（纯函数）──


def base_rate_distribution(
    actual_scenarios: Sequence[str],
    *,
    min_base_samples: int = DEFAULT_CONFIG.min_base_samples,
    support_full: int = DEFAULT_CONFIG.base_support_full,
    laplace_alpha: float = DEFAULT_CONFIG.base_laplace_alpha,
) -> LayerDistribution:
    """基础率层（纯函数）：历史实际命中格序列 → 9 格经验频率分布。

    样本 ≥ min_base_samples → Laplace(α) 平滑经验频率，confidence=
    min(1, n/support_full)；样本不足 → 全 1/9 均匀兜底 + degraded=True
    （不伪造精度，G4 反误导），confidence 仍按样本量线性缩放（低值）。

    Args:
        actual_scenarios: 历史实际命中格序列（元素须 ∈ SCENARIO_LIST）。
        min_base_samples: 最小样本数（正整数）。
        support_full: 置信度=1 所需样本数（正整数且 ≥ min_base_samples）。
        laplace_alpha: Laplace 平滑强度（非负实数）。

    Returns:
        LayerDistribution（name="base_rate"）。

    Raises:
        ValueError: 元素越界（非 SCENARIO_LIST 成员）或参数非法（fail-closed）。
    """
    if isinstance(min_base_samples, bool) or not isinstance(min_base_samples, int) or min_base_samples < 1:
        raise ValueError(f"min_base_samples 非法（须正整数）: {min_base_samples!r}")
    if isinstance(support_full, bool) or not isinstance(support_full, int) or support_full < min_base_samples:
        raise ValueError(f"support_full 非法（须 ≥ min_base_samples 的正整数）: {support_full!r}")
    alpha = _safe_float(laplace_alpha)
    if alpha is None or alpha < 0:
        raise ValueError(f"laplace_alpha 非法（须非负实数）: {laplace_alpha!r}")
    seq = list(actual_scenarios)
    for s in seq:
        if not isinstance(s, str) or s not in SCENARIO_LIST:
            raise ValueError(f"actual_scenario 越界（须 SCENARIO_LIST 成员）: {s!r}")

    n = len(seq)
    confidence = min(1.0, n / support_full)
    if n < min_base_samples:
        return LayerDistribution(
            name=LAYER_BASE_RATE,
            probabilities={s: _UNIFORM_PROB for s in SCENARIO_LIST},
            confidence=confidence,
            sample_size=n,
            degraded=True,
            detail={"reason": "insufficient_samples", "min_base_samples": min_base_samples},
        )
    counts = {s: 0 for s in SCENARIO_LIST}
    for s in seq:
        counts[s] += 1
    denom = n + alpha * len(SCENARIO_LIST)
    probs = {s: (counts[s] + alpha) / denom for s in SCENARIO_LIST}
    return LayerDistribution(
        name=LAYER_BASE_RATE,
        probabilities=probs,
        confidence=confidence,
        sample_size=n,
        degraded=False,
        detail={"laplace_alpha": alpha},
    )


# ── 状态条件层（纯函数）──


def _coerce_state(key: object) -> NextDayState:
    """8 态键归一：NextDayState 或其 value 字符串 → NextDayState（fail-closed）。"""
    if isinstance(key, NextDayState):
        return key
    if isinstance(key, str):
        try:
            return NextDayState(key)
        except ValueError as exc:
            raise ValueError(f"8 态键越界（须 NextDayState 成员）: {key!r}") from exc
    raise ValueError(f"8 态键非法（须 NextDayState 或其 value 字符串）: {key!r}")


def map_state_distribution(state_probs: Mapping[Any, float]) -> dict[str, float]:
    """8 态概率分布 → 9 格概率质量折算（纯函数，STATE_TO_GRID_MASS 条件映射）。

    Args:
        state_probs: {NextDayState 或其 value 字符串: 概率}，概率行和须=1
            （±1e-4 容差内按行和重归一，防马尔可夫输出浮点尾差）。

    Returns:
        9 格概率字典（全 9 键，无质量格为 0.0，行和=1）。

    Raises:
        ValueError: 态键越界/概率越界/行和偏离 >1e-4（fail-closed）。
    """
    if not isinstance(state_probs, Mapping) or not state_probs:
        raise ValueError(f"state_probs 非法（须非空映射）: {state_probs!r}")
    normed: dict[NextDayState, float] = {}
    for k, v in state_probs.items():
        state = _coerce_state(k)
        p = _validate_prob(v, f"state_probs[{state.value}]")
        normed[state] = normed.get(state, 0.0) + p
    total = sum(normed.values())
    if total <= 0 or abs(total - 1.0) > 1e-4:
        raise ValueError(f"state_probs 行和须=1（±1e-4）: 实得 {total!r}")
    grid = {s: 0.0 for s in SCENARIO_LIST}
    for state, p in normed.items():
        for cell, share in STATE_TO_GRID_MASS[state].items():
            grid[cell] += p / total * share
    return grid


def state_conditional_distribution(
    forecast: NextDayForecast | Mapping[Any, float],
    *,
    confidence: float | None = None,
    sample_size: int | None = None,
) -> LayerDistribution:
    """状态条件层（纯函数）：MOD-SIG-037 8 态预测 → 9 格 LayerDistribution。

    Args:
        forecast: NextDayForecast（取 probabilities/confidence/n_transitions）
            或 8 态概率映射（此时 confidence/sample_size 由参数供给，默认
            confidence=0.5 中性先验/sample_size=0）。
        confidence: 映射形态时的层自置信度（∈ [0,1]）。
        sample_size: 映射形态时的层样本数（非负整数）。

    Returns:
        LayerDistribution（name="state_conditional"）。

    Raises:
        ValueError: forecast 形态非法/分布非法/参数越界（fail-closed）。
    """
    if isinstance(forecast, NextDayForecast):
        conf = _validate_prob(forecast.confidence, "forecast.confidence")
        n = forecast.n_transitions
        probs = forecast.probabilities
    elif isinstance(forecast, Mapping):
        conf = 0.5 if confidence is None else _validate_prob(confidence, "confidence")
        if sample_size is None:
            n = 0
        elif isinstance(sample_size, bool) or not isinstance(sample_size, int) or sample_size < 0:
            raise ValueError(f"sample_size 非法（须非负整数）: {sample_size!r}")
        else:
            n = sample_size
        probs = forecast
    else:
        raise ValueError(f"forecast 非法（须 NextDayForecast 或 8 态概率映射）: {type(forecast).__name__}")
    return LayerDistribution(
        name=LAYER_STATE_CONDITIONAL,
        probabilities=map_state_distribution(probs),
        confidence=conf,
        sample_size=n,
        degraded=False,
        detail={"source": "MOD-SIG-037.next_day_8state_forecast"},
    )


# ── 密度头层（纯函数，准蒙特卡洛定数网格）──


def _inverse_cdf_points(quantiles: Mapping[float, float]) -> list[tuple[float, float]]:
    """分位数带 → 逆 CDF 折点（u, v）升序，两端线性外推至 u=0/u=1（fail-closed）。

    分位数键须 ∈ (0,1) 升序、值单调不减（MOD-ML-DENSITY predict_quantiles
    输出已 np.maximum.accumulate 修正，本层对违例 fail-closed 不二次修复）。
    """
    if not isinstance(quantiles, Mapping) or len(quantiles) < 2:
        raise ValueError(f"quantiles 非法（须 ≥2 个分位点的映射）: {quantiles!r}")
    pts: list[tuple[float, float]] = []
    for k, v in quantiles.items():
        u = _safe_float(k)
        if u is None or not (0.0 < u < 1.0):
            raise ValueError(f"分位数键非法（须 (0,1) 实数）: {k!r}")
        val = _safe_float(v)
        if val is None:
            raise ValueError(f"分位数值非法（须有限实数）: {v!r}")
        pts.append((u, val))
    pts.sort()
    for i in range(1, len(pts)):
        if pts[i][0] == pts[i - 1][0]:
            raise ValueError(f"分位数键重复: {pts[i][0]!r}")
        if pts[i][1] < pts[i - 1][1]:
            raise ValueError(f"分位数序列须单调不减: {pts[i - 1]!r} -> {pts[i]!r}")
    (u0, v0), (u1, v1) = pts[0], pts[1]
    low_v = v0 - (v1 - v0) * u0 / (u1 - u0)  # u=0 端线性外推
    (un1, vn1), (un, vn) = pts[-2], pts[-1]
    high_v = vn + (vn - vn1) * (1.0 - un) / (un - un1)  # u=1 端线性外推
    return [(0.0, low_v), *pts, (1.0, high_v)]


def _interp_inverse_cdf(points: Sequence[tuple[float, float]], u: float) -> float:
    """分段线性插值逆 CDF：u ∈ [0,1] → 收益样本（points 已含 0/1 端点）。"""
    for i in range(1, len(points)):
        if u <= points[i][0]:
            (ua, va), (ub, vb) = points[i - 1], points[i]
            if ub == ua:
                return va
            return va + (vb - va) * (u - ua) / (ub - ua)
    return points[-1][1]


def density_grid_distribution(
    quantiles: Mapping[float, float],
    *,
    mc_samples: int = DEFAULT_CONFIG.density_mc_samples,
    gap_share: float = DEFAULT_CONFIG.density_gap_share,
    open_threshold: float = DEFAULT_CONFIG.density_open_threshold,
    trend_tolerance: float = DEFAULT_CONFIG.density_trend_tolerance,
    layer_confidence: float = DEFAULT_CONFIG.density_layer_confidence,
) -> LayerDistribution:
    """密度头层（纯函数）：分位数带 → 准蒙特卡洛采样 → 9 格概率质量折算。

    准蒙特卡洛（定数均匀网格，零随机数，输出确定性）：u_i=(i+0.5)/N 逆 CDF
    分段线性插值得收益样本 r；按 gap_share 拆 r 为隔夜缺口 g=r*share 与日内
    走势 t=r-g；开盘桶（|g| vs ±open_threshold）×走势桶（|t| vs trend_tolerance）
    → 9 格计数/N。

    口径声明：密度头目标是全日收益，9 格走势桶语义为 30 分钟 VWAP 偏离——
    本层为近似折算（trend_tolerance 默认 0.3% 全日口径代理），层自置信取
    layer_confidence 先验（默认 0.5 待标定），由融合层加权稀释不确定性。

    Args:
        quantiles: {分位数(0~1): 收益值}，≥2 点、键升序、值单调不减。
        mc_samples: 准蒙特卡洛采样数（正整数）。
        gap_share: 隔夜缺口拆分占比 ∈ [0,1]。
        open_threshold: 开盘桶阈值（正实数，默认 ±2%）。
        trend_tolerance: 走势平走容忍带（非负实数，默认 ±0.3% 全日代理）。
        layer_confidence: 层自置信先验 ∈ [0,1]。

    Returns:
        LayerDistribution（name="density_head"，sample_size=mc_samples）。

    Raises:
        ValueError: 分位数带非法（键越界/重复/值非有限/非单调/点不足）或
            参数非法（fail-closed）。
    """
    if isinstance(mc_samples, bool) or not isinstance(mc_samples, int) or mc_samples < 1:
        raise ValueError(f"mc_samples 非法（须正整数）: {mc_samples!r}")
    share = _safe_float(gap_share)
    if share is None or not (0.0 <= share <= 1.0):
        raise ValueError(f"gap_share 非法（须 [0,1]）: {gap_share!r}")
    th = _safe_float(open_threshold)
    if th is None or th <= 0:
        raise ValueError(f"open_threshold 非法（须正实数）: {open_threshold!r}")
    tol = _safe_float(trend_tolerance)
    if tol is None or tol < 0:
        raise ValueError(f"trend_tolerance 非法（须非负实数）: {trend_tolerance!r}")
    conf = _validate_prob(layer_confidence, "layer_confidence")

    points = _inverse_cdf_points(quantiles)
    counts = {s: 0 for s in SCENARIO_LIST}
    for i in range(mc_samples):
        r = _interp_inverse_cdf(points, (i + 0.5) / mc_samples)
        g = r * share
        t = r - g
        if g >= th:
            open_bucket = "HIGH"
        elif g <= -th:
            open_bucket = "LOW"
        else:
            open_bucket = "FLAT"
        if t > tol:
            trend_bucket = "UP"
        elif t < -tol:
            trend_bucket = "DOWN"
        else:
            trend_bucket = "WASH"
        counts[_BUCKET_TO_SCENARIO[(open_bucket, trend_bucket)]] += 1
    probs = {s: counts[s] / mc_samples for s in SCENARIO_LIST}
    return LayerDistribution(
        name=LAYER_DENSITY_HEAD,
        probabilities=probs,
        confidence=conf,
        sample_size=mc_samples,
        degraded=False,
        detail={"n_quantiles": len(quantiles), "gap_share": share},
    )


# ── 三层融合（纯函数）──


def fuse_distributions(
    layers: Sequence[LayerDistribution],
    weights: Mapping[str, float],
) -> tuple[dict[str, float], dict[str, float], dict[str, Any]]:
    """三层加权融合（纯函数）：缺层重归一 + 行和归一 + 每格置信度。

    每格置信度口径：agreement_c = 1 − σ²_c/(p_c(1−p_c))（σ²_c=各层格概率按
    生效权重的加权方差，分母=同均值 Bernoulli 方差上界；层间越一致越接近 1）
    × overall_confidence（各层自置信按生效权重加权）——"层间一致且层自身
    可信"的格高置信，分歧大/层弱的格低置信。

    Args:
        layers: 在场层序列（非空；同名层重复 fail-closed）。
        weights: 配置权重（键⊆三层标识，行和=1 校验 fail-closed；缺层权重
            在剩余在场层间重归一，degraded_layers 留痕）。

    Returns:
        (probabilities, cell_confidence, meta)：meta 含 weights_used /
        degraded_layers / overall_confidence。

    Raises:
        ValueError: layers 为空/同名重复/层分布非法，或在场层权重和=0，
            或 weights 非法（fail-closed）。
    """
    w = _validate_weights(weights)
    present = list(layers)
    if not present:
        raise ValueError("layers 非法（三层供给全缺，禁止无中生有伪造分布）")
    seen: set[str] = set()
    for layer in present:
        if not isinstance(layer, LayerDistribution):
            raise ValueError(f"layers 元素非法（须 LayerDistribution）: {type(layer).__name__}")
        if layer.name in seen:
            raise ValueError(f"layers 含同名层: {layer.name!r}")
        seen.add(layer.name)
        probs = layer.probabilities
        if not isinstance(probs, Mapping) or not probs:
            raise ValueError(f"层 {layer.name} probabilities 非法（须非空映射）")
        for cell, p in probs.items():
            if cell not in SCENARIO_LIST:
                raise ValueError(f"层 {layer.name} 格键越界（须 SCENARIO_LIST 成员）: {cell!r}")
            _validate_prob(p, f"层 {layer.name} probabilities[{cell!r}]")
        psum = sum(probs.values())
        if abs(psum - 1.0) > _PROB_SUM_TOL:
            raise ValueError(f"层 {layer.name} 分布行和须=1（±{_PROB_SUM_TOL}）: 实得 {psum!r}")
        _validate_prob(layer.confidence, f"层 {layer.name} confidence")

    w_present_sum = sum(w.get(layer.name, 0.0) for layer in present)
    if w_present_sum <= 0:
        raise ValueError("在场层配置权重和=0（无法融合，fail-closed）")
    weights_used = {layer.name: w.get(layer.name, 0.0) / w_present_sum for layer in present}
    degraded_layers = tuple(name for name in _LAYER_NAMES if name not in seen and w.get(name, 0.0) > 0.0)

    fused = {s: 0.0 for s in SCENARIO_LIST}
    for layer in present:
        wu = weights_used[layer.name]
        for cell, p in layer.probabilities.items():
            fused[cell] += wu * p
    fsum = sum(fused.values())
    fused = {s: fused[s] / fsum for s in SCENARIO_LIST}

    overall_conf = sum(weights_used[layer.name] * layer.confidence for layer in present)
    cell_conf: dict[str, float] = {}
    for cell in SCENARIO_LIST:
        p_c = fused[cell]
        var_c = sum(weights_used[layer.name] * (layer.probabilities.get(cell, 0.0) - p_c) ** 2 for layer in present)
        denom = p_c * (1.0 - p_c)
        agreement = 1.0 if denom < _AGREEMENT_EPS else max(0.0, 1.0 - var_c / denom)
        cell_conf[cell] = min(1.0, max(0.0, agreement * overall_conf))

    meta: dict[str, Any] = {
        "weights_used": weights_used,
        "degraded_layers": list(degraded_layers),
        "overall_confidence": overall_conf,
    }
    return fused, cell_conf, meta


def build_scenario_probability_forecast(
    trade_date: str,
    layers: Sequence[LayerDistribution],
    weights: Mapping[str, float],
    *,
    detail: Mapping[str, Any] | None = None,
) -> ScenarioProbabilityForecast:
    """组合主核（纯函数）：trade_date + 在场层 + 权重 → 9 格概率预测。

    Raises:
        ValueError: trade_date/layers/weights 非法（fail-closed，见 fuse）。
    """
    v_date = _validate_trade_date(trade_date)
    fused, cell_conf, meta = fuse_distributions(layers, weights)
    top = max(SCENARIO_LIST, key=lambda s: (fused[s], -SCENARIO_LIST.index(s)))
    low_conf = any(layer.degraded for layer in layers) or meta["overall_confidence"] < 0.5
    return ScenarioProbabilityForecast(
        trade_date=v_date,
        probabilities=fused,
        cell_confidence=cell_conf,
        top_scenario=top,
        top_probability=fused[top],
        samples={layer.name: layer.sample_size for layer in layers},
        weights_used=meta["weights_used"],
        degraded_layers=tuple(meta["degraded_layers"]),
        low_confidence=low_conf,
        detail=dict(detail) if detail else {},
    )


# ── 注入隔离组合器（供给经 callable 注入，测试 fake，禁真连 DB）──


class ScenarioProbabilityModel:
    """9 格概率分布组合器（MOD-PLAN-017）。

    三路供给全部注入隔离（纯函数核零 DB/零随机）：
      - query_fn：prediction_log 查询（签名同 query_predictions；None=项目
        公共 API 默认通道；测试注入 fake query_fn）。
      - state_forecast_provider：trade_date → NextDayForecast 或 8 态概率
        映射（None=状态层缺失降级；测试注入假预测）。
      - quantile_provider：trade_date → {分位数: 收益值} 单标的单日分位
        数带（None=密度层缺失降级；测试注入假分位数带）。
    任一供给异常 → fail-open 该层缺失降级（重归一+留痕）；三层全缺 →
    ValueError（fail-closed，禁止无中生有伪造分布）。
    """

    def __init__(
        self,
        query_fn: Callable[..., list[dict]] | None = None,
        state_forecast_provider: Callable[[str], Any] | None = None,
        quantile_provider: Callable[[str], Mapping[float, float]] | None = None,
        config: ScenarioProbabilityConfig | None = None,
        db_path: str | Path | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._query_fn = query_fn
        self._state_provider = state_forecast_provider
        self._quantile_provider = quantile_provider
        self._db_path = db_path

    # ── 基础率层供给 ─────────────────────────────────────────────────────

    def _load_base_layer(self, trade_date: str) -> LayerDistribution | None:
        """prediction_log outcome 族 → 历史实际命中格 → 基础率层（fail-open 降级）。"""
        cfg = self._config
        query = self._query_fn if self._query_fn is not None else query_predictions
        try:
            rows = query(
                module=BASE_SOURCE_MODULE,
                prediction_type=_OUTCOME_PREDICTION_TYPE,
                limit=_BASE_QUERY_LIMIT,
                db_path=self._db_path,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：查询异常（如表缺失）降级缺层
            log.warning("基础率层查询异常 fail-open 降级: %s: %s", type(exc).__name__, exc)
            return None
        end = datetime.date.fromisoformat(trade_date) - datetime.timedelta(days=1)  # PIT：不含预测当日
        start = end - datetime.timedelta(days=cfg.base_window_days - 1)
        actuals: list[str] = []
        skipped = 0
        for row in rows:
            try:
                td = row["trade_date"]
            except (KeyError, TypeError):
                skipped += 1
                continue
            if not (start.isoformat() <= td <= end.isoformat()):
                continue
            try:
                payload = json.loads(row["payload_json"])
            except (json.JSONDecodeError, TypeError, KeyError):
                skipped += 1
                continue
            if not isinstance(payload, dict):
                skipped += 1
                continue
            actual = payload.get("actual_scenario")
            if not isinstance(actual, str) or actual not in SCENARIO_LIST:
                skipped += 1
                continue
            actuals.append(actual)
        layer = base_rate_distribution(
            actuals,
            min_base_samples=cfg.min_base_samples,
            support_full=cfg.base_support_full,
            laplace_alpha=cfg.base_laplace_alpha,
        )
        return dataclasses.replace(
            layer,
            detail={
                **layer.detail,
                "window_start": start.isoformat(),
                "window_end": end.isoformat(),
                "skipped_invalid": skipped,
            },
        )

    # ── 状态/密度层供给 ──────────────────────────────────────────────────

    def _load_state_layer(self, trade_date: str) -> LayerDistribution | None:
        """8 态预测供给 → 状态条件层（未注入/异常 → 缺层降级，fail-open）。"""
        if self._state_provider is None:
            return None
        try:
            forecast = self._state_provider(trade_date)
            return state_conditional_distribution(forecast)
        except Exception as exc:  # noqa: BLE001 — fail-open：供给异常降级缺层
            log.warning("状态条件层供给异常 fail-open 降级: %s: %s", type(exc).__name__, exc)
            return None

    def _load_density_layer(self, trade_date: str) -> LayerDistribution | None:
        """分位数带供给 → 密度头层（未注入/异常 → 缺层降级，fail-open）。"""
        if self._quantile_provider is None:
            return None
        try:
            quantiles = self._quantile_provider(trade_date)
            cfg = self._config
            return density_grid_distribution(
                quantiles,
                mc_samples=cfg.density_mc_samples,
                gap_share=cfg.density_gap_share,
                open_threshold=cfg.density_open_threshold,
                trend_tolerance=cfg.density_trend_tolerance,
                layer_confidence=cfg.density_layer_confidence,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：供给异常降级缺层
            log.warning("密度头层供给异常 fail-open 降级: %s: %s", type(exc).__name__, exc)
            return None

    # ── 组合入口 ─────────────────────────────────────────────────────────

    def forecast(self, trade_date: str) -> ScenarioProbabilityForecast:
        """三层供给 → 融合 → 9 格概率分布（W2 矩阵消费契约）。

        Raises:
            ValueError: trade_date 非法，或三层供给全缺（fail-closed）。
        """
        v_date = _validate_trade_date(trade_date)
        cfg = self._config
        layers = [
            layer
            for layer in (
                self._load_base_layer(v_date),
                self._load_state_layer(v_date),
                self._load_density_layer(v_date),
            )
            if layer is not None
        ]
        return build_scenario_probability_forecast(
            v_date,
            layers,
            {
                LAYER_BASE_RATE: cfg.weight_base,
                LAYER_STATE_CONDITIONAL: cfg.weight_state,
                LAYER_DENSITY_HEAD: cfg.weight_density,
            },
            detail={"layers": [layer.to_dict() for layer in layers]},
        )

    def forecast_and_record(
        self,
        trade_date: str,
        asof_ts: str | None = None,
    ) -> tuple[ScenarioProbabilityForecast, int]:
        """预测 + 落库：scenario_probability 族 append-only（幂等保首条）。

        Returns:
            (forecast, row_id)；落库异常 fail-open row_id=-1 不阻塞预测主流程。

        Raises:
            ValueError: trade_date 非法或三层供给全缺（fail-closed）。
        """
        fc = self.forecast(trade_date)
        try:
            row_id = log_prediction(
                trade_date=fc.trade_date,
                module=MODULE_LOG_NAME,
                prediction_type=PREDICTION_TYPE_SCENARIO_PROBABILITY,
                payload=fc.to_dict(),
                asof_ts=asof_ts,
                db_path=self._db_path,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：落库失败不阻塞预测主流程
            log.warning(
                "scenario_probability 落库失败 fail-open（date=%s）: %s: %s", fc.trade_date, type(exc).__name__, exc
            )
            row_id = -1
        return fc, row_id
