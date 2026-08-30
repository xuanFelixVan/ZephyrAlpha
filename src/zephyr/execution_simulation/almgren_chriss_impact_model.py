# [BLUEPRINT] MOD-EXSIM-001 | docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md
# [MODULE] zephyr.execution_simulation.almgren_chriss_impact_model
# [DOMAIN] D_EXEC_SIM
# [DEPENDENCIES] 无（纯内存/DI；分钟成交额序列由调用方注入；语义旁挂 simulation.volume_aware_impact sqrt 冲击形式）
# [CONSUMERS] 运行时装配批（执行仿真/回测冲击成本真源装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 临时冲击=η×参与率^β×σ; 永久冲击=γ×参与率^0.5×σ(默认档指数0.5可注入); 参与率∈[0,1]越界Fail-Closed; 衰减曲线按成交节奏分段(uniform|front|back词表闭合); 临时冲击段间按λ∈[0,1]几何衰减; 参数估计器输入分钟成交额非空且为正; 结果frozen; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_execution_sim/almgren_chriss_impact_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] AlmgrenChrissError(占位 ZA-EXSIM-UNREGISTERED-ALMGREN-CHRISS)——非法参数/参与率越界/非法订单量或市场量/未知节奏词表/估计输入非法时抛
# [TESTS] tests/execution_simulation/test_almgren_chriss_impact_model.py
# [A_module] module_id=MOD-EXSIM-001 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



AlmgrenChrissImpactModel — Almgren-Chriss 冲击成本模型（MOD-EXSIM-001）。

B3-06286（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-EXSIM-001，B3 R-118）：
**临时冲击**（η × 参与率^β × σ，段后按 λ 几何衰减）+ **永久冲击**
（γ × 参与率^0.5 × σ 默认档，指数可注入）参数化 + **冲击衰减曲线**
（按成交节奏分段：uniform/front/back 词表闭合）+ **基于分钟成交额的
参数估计器** + **冲击成本真源输出**供执行仿真/回测消费。

查重分工（蓝图 §0）：volume_aware_impact=权重变化率 sqrt 冲击（组合再
平衡 NAV loop 场景）；本件=order-driven 参与率冲击建模（单笔订单执行
场景），含衰减曲线与参数估计器，不改动既有 slippage 链路。本件纯数学
无时间/随机需求——无需时钟/随机源注入点。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: params 参数
#   fields: 参数 params（无注解）
#   code: almgren_chriss_impact_model.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: decay_lambda 参数
#   fields: 参数 decay_lambda（无注解）
#   code: almgren_chriss_impact_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AlmgrenChrissImpactModel
#   name_en: AlmgrenChrissImpactModel
#   intro: Almgren-Chriss 冲击成本模型（临时+永久参数化 + 衰减曲线 + 估计器）。
#   desc: Almgren-Chriss 冲击成本模型（临时+永久参数化 + 衰减曲线 + 估计器）。；公共方法（定义序）: params, temporary_impact, permanent_impact, quote, d…
#   inputs: params decay_lambda
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: AlmgrenChrissImpactModel
#   downstream: 运行时装配批（执行仿真/回测冲击成本真源装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "AlmgrenChrissError",
    "AlmgrenChrissImpactModel",
    "ImpactParams",
    "ImpactQuote",
    "ImpactTrajectory",
    "MinuteBar",
    "ScheduleType",
    "TrajectoryPoint",
]


class AlmgrenChrissError(Exception):
    """Almgren-Chriss 冲击建模输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-EXSIM-UNREGISTERED-ALMGREN-CHRISS。
    """


class ScheduleType(str, Enum):
    """成交节奏（词表闭合）：匀速 / 前重后轻 / 前轻后重。"""

    UNIFORM = "uniform"
    FRONT = "front"
    BACK = "back"


@dataclass(frozen=True)
class ImpactParams:
    """冲击参数（frozen）：η 临时系数 / β 参与率指数 / γ 永久系数 / σ 日波动率。"""

    eta: float
    beta: float
    gamma: float
    sigma: float
    permanent_exponent: float = 0.5  # 默认档 sqrt(参与率)

    def __post_init__(self) -> None:
        if self.eta < 0:
            raise AlmgrenChrissError(f"eta 不能为负: {self.eta!r}")
        if self.beta <= 0:
            raise AlmgrenChrissError(f"beta 须为正: {self.beta!r}")
        if self.gamma < 0:
            raise AlmgrenChrissError(f"gamma 不能为负: {self.gamma!r}")
        if self.sigma < 0:
            raise AlmgrenChrissError(f"sigma 不能为负: {self.sigma!r}")
        if self.permanent_exponent <= 0:
            raise AlmgrenChrissError(f"permanent_exponent 须为正: {self.permanent_exponent!r}")


@dataclass(frozen=True)
class ImpactQuote:
    """单笔冲击报价（frozen；冲击为价格相对位移比例，cost_bps=total×1e4）。"""

    participation: float
    temporary_impact: float
    permanent_impact: float
    total_impact: float
    cost_bps: float


@dataclass(frozen=True)
class TrajectoryPoint:
    """衰减曲线分段点（frozen）。

    effective_permanent = 前段永久冲击累积 + 本段永久冲击 × 0.5
    （本段均价承受本段永久冲击的一半，Almgren-Chriss 标准处理）；
    residual_temporary = Σ_{j≤i} temp_j × λ^(i-j)（段间几何衰减残留）。
    """

    step: int
    fraction: float
    participation: float
    temporary: float
    residual_temporary: float
    effective_permanent: float
    segment_cost: float


@dataclass(frozen=True)
class ImpactTrajectory:
    """冲击衰减曲线（frozen；total_cost_bps 为分段成本按成交占比加权）。"""

    schedule: ScheduleType
    slices: int
    points: tuple[TrajectoryPoint, ...]
    total_cost: float
    total_cost_bps: float


@dataclass(frozen=True)
class MinuteBar:
    """分钟成交额估计输入（frozen；range_pct=(高-低)/收 为分钟波幅代理）。"""

    minute: str
    dollar_volume: float
    range_pct: float


#: 默认档参数（无量纲标定；生产经 estimate_params 估出后注入）
DEFAULT_PARAMS: Final = ImpactParams(eta=0.1, beta=1.0, gamma=0.05, sigma=0.02)


def _validate_participation(p: float) -> float:
    try:
        pf = float(p)
    except (TypeError, ValueError) as exc:
        raise AlmgrenChrissError(f"参与率必须是数值: {p!r}") from exc
    if not 0.0 <= pf <= 1.0:
        raise AlmgrenChrissError(f"参与率越界（须 ∈ [0,1]）: {pf!r}")
    return pf


def _schedule_fractions(schedule: ScheduleType, slices: int) -> list[float]:
    """按成交节奏生成分段成交占比（确定性；权重线性，归一化）。"""
    if schedule is ScheduleType.UNIFORM:
        return [1.0 / slices] * slices
    if schedule is ScheduleType.FRONT:
        weights = [float(slices - i) for i in range(slices)]  # 前重后轻
    else:  # BACK
        weights = [float(i + 1) for i in range(slices)]  # 前轻后重
    total = sum(weights)
    return [w / total for w in weights]


class AlmgrenChrissImpactModel:
    """Almgren-Chriss 冲击成本模型（临时+永久参数化 + 衰减曲线 + 估计器）。"""

    def __init__(
        self,
        *,
        params: ImpactParams | None = None,
        decay_lambda: float = 0.5,
    ) -> None:
        if not 0.0 <= decay_lambda <= 1.0:
            raise AlmgrenChrissError(f"decay_lambda 须 ∈ [0,1]: {decay_lambda!r}")
        self._params = params if params is not None else DEFAULT_PARAMS
        self._lambda = float(decay_lambda)

    @property
    def params(self) -> ImpactParams:
        """冲击参数（只读）。"""
        return self._params

    # ── 冲击原子 ──────────────────────────────────────────────────────────

    def temporary_impact(self, participation: float) -> float:
        """临时冲击 = η × 参与率^β × σ（价格相对位移比例，段后衰减）。"""
        p = _validate_participation(participation)
        return self._params.eta * (p**self._params.beta) * self._params.sigma

    def permanent_impact(self, participation: float) -> float:
        """永久冲击 = γ × 参与率^permanent_exponent × σ（默认档 sqrt）。"""
        p = _validate_participation(participation)
        return self._params.gamma * (p**self._params.permanent_exponent) * self._params.sigma

    # ── 单笔报价（真源输出） ─────────────────────────────────────────────

    def quote(self, order_qty: float, market_volume: float) -> ImpactQuote:
        """单笔冲击报价：参与率=order/market，总冲击=临时+永久，×1e4 得 bps。"""
        if not isinstance(order_qty, (int, float)) or isinstance(order_qty, bool) or order_qty <= 0:
            raise AlmgrenChrissError(f"order_qty 须为正: {order_qty!r}")
        if not isinstance(market_volume, (int, float)) or isinstance(market_volume, bool) or market_volume <= 0:
            raise AlmgrenChrissError(f"market_volume 须为正: {market_volume!r}")
        participation = _validate_participation(order_qty / market_volume)
        temp = self.temporary_impact(participation)
        perm = self.permanent_impact(participation)
        total = temp + perm
        quote = ImpactQuote(
            participation=participation,
            temporary_impact=temp,
            permanent_impact=perm,
            total_impact=total,
            cost_bps=total * 1e4,
        )
        _log.debug(
            "冲击报价: qty=%s vol=%s p=%.4f temp=%.6f perm=%.6f bps=%.3f",
            order_qty,
            market_volume,
            participation,
            temp,
            perm,
            quote.cost_bps,
        )
        return quote

    # ── 冲击衰减曲线（按成交节奏分段） ────────────────────────────────────

    def decay_curve(
        self,
        order_qty: float,
        market_volume: float,
        slices: int,
        *,
        schedule: ScheduleType = ScheduleType.UNIFORM,
    ) -> ImpactTrajectory:
        """分段冲击衰减曲线：订单按节奏切 slices 段，市场量均匀分段。

        段 i 成本 = 前段永久累积 + 0.5×本段永久 + 临时冲击几何衰减残留
        （residual_i = Σ_{j≤i} temp_j × λ^(i-j)）；总成本按成交占比加权。
        """
        if not isinstance(schedule, ScheduleType):
            raise AlmgrenChrissError(f"未知成交节奏: {schedule!r}（词表闭合 uniform|front|back）")
        if not isinstance(slices, int) or isinstance(slices, bool) or slices < 1:
            raise AlmgrenChrissError(f"slices 须为正整数: {slices!r}")
        if not isinstance(order_qty, (int, float)) or isinstance(order_qty, bool) or order_qty <= 0:
            raise AlmgrenChrissError(f"order_qty 须为正: {order_qty!r}")
        if not isinstance(market_volume, (int, float)) or isinstance(market_volume, bool) or market_volume <= 0:
            raise AlmgrenChrissError(f"market_volume 须为正: {market_volume!r}")
        _validate_participation(order_qty / market_volume)

        fractions = _schedule_fractions(schedule, slices)
        slice_market = market_volume / slices  # 市场量均匀分段假设
        temps: list[float] = []
        points: list[TrajectoryPoint] = []
        cum_perm = 0.0
        total_cost = 0.0
        for i, frac in enumerate(fractions):
            qty_i = order_qty * frac
            p_i = _validate_participation(qty_i / slice_market)
            temp_i = self.temporary_impact(p_i)
            perm_i = self.permanent_impact(p_i)
            residual = sum(t * (self._lambda ** (i - j)) for j, t in enumerate(temps + [temp_i]))
            effective_perm = cum_perm + 0.5 * perm_i
            seg_cost = effective_perm + residual
            points.append(
                TrajectoryPoint(
                    step=i,
                    fraction=frac,
                    participation=p_i,
                    temporary=temp_i,
                    residual_temporary=residual,
                    effective_permanent=effective_perm,
                    segment_cost=seg_cost,
                )
            )
            total_cost += frac * seg_cost
            cum_perm += perm_i
            temps.append(temp_i)
        trajectory = ImpactTrajectory(
            schedule=schedule,
            slices=slices,
            points=tuple(points),
            total_cost=total_cost,
            total_cost_bps=total_cost * 1e4,
        )
        _log.debug(
            "衰减曲线: schedule=%s slices=%d total_bps=%.3f",
            schedule.value,
            slices,
            trajectory.total_cost_bps,
        )
        return trajectory

    # ── 参数估计器（基于分钟成交额） ──────────────────────────────────────

    @staticmethod
    def estimate_params(
        bars: Iterable[MinuteBar],
        *,
        minutes_per_day: int = 240,
        reference_participation: float = 0.10,
        beta: float = 1.0,
        gamma_ratio: float = 0.5,
        permanent_exponent: float = 0.5,
    ) -> ImpactParams:
        """基于分钟成交额的参数估计器（确定性标定）。

        σ_daily = mean(range_pct) × √minutes_per_day（分钟波幅放大到日）；
        η 按参考参与率校准：使 临时冲击(p_ref) = mean(range_pct)，即
        η = mean(range_pct) / (p_ref^β × σ_daily)；γ = gamma_ratio × η。
        bars 全零波幅 → σ_daily=0 无法校准 → Fail-Closed。
        """
        rows = list(bars)
        if not rows:
            raise AlmgrenChrissError("bars 为空（无法估计）")
        for b in rows:
            if b.dollar_volume <= 0:
                raise AlmgrenChrissError(f"dollar_volume 须为正: {b!r}")
            if b.range_pct < 0:
                raise AlmgrenChrissError(f"range_pct 不能为负: {b!r}")
        if minutes_per_day < 1:
            raise AlmgrenChrissError(f"minutes_per_day 须为正: {minutes_per_day!r}")
        if not 0.0 < reference_participation <= 1.0:
            raise AlmgrenChrissError(f"reference_participation 越界: {reference_participation!r}")
        if beta <= 0 or gamma_ratio < 0 or permanent_exponent <= 0:
            raise AlmgrenChrissError(
                f"估计器超参非法: beta={beta!r} gamma_ratio={gamma_ratio!r} permanent_exponent={permanent_exponent!r}"
            )
        mean_range = sum(b.range_pct for b in rows) / len(rows)
        sigma_daily = mean_range * math.sqrt(minutes_per_day)
        if sigma_daily == 0:
            raise AlmgrenChrissError("bars 全零波幅（σ_daily=0，无法校准 η）")
        eta = mean_range / ((reference_participation**beta) * sigma_daily)
        params = ImpactParams(
            eta=eta,
            beta=beta,
            gamma=gamma_ratio * eta,
            sigma=sigma_daily,
            permanent_exponent=permanent_exponent,
        )
        _log.debug(
            "参数估计: bars=%d mean_range=%.6f sigma=%.6f eta=%.6f gamma=%.6f",
            len(rows),
            mean_range,
            sigma_daily,
            eta,
            params.gamma,
        )
        return params
