# [BLUEPRINT] MOD-PF-011 | docs/03_modules/_domain_portfolio_core/exposure_manager/blueprint.md
# [MODULE] zephyr.pf_core.core.exposure_manager
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（组合域敞口配置复核/行业轮动建议消费）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 权重归一化Σ=1; 行业主动敞口=组合−基准(申万31); 风格主动暴露=Σw×loading差; |active|>breach→BREACH,≥warn→WARNING,按|active/limit|降序; 轮动:动量top_n且active<band→OVERWEIGHT,bottom_n且active>−band→UNDERWEIGHT,余NEUTRAL; 缺映射/缺载荷列uncovered披露按0计; 报告frozen; 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExposureManagerError
# [TESTS] tests/pf_core/test_exposure_manager.py
# [A_module] module_id=MOD-PF-011 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Exposure Manager — PC-07 组合域敞口管理器 (MOD-PF-011, CAND-PF004-004, B3-05543)

申万 31 行业**主动敞口**（组合 − 基准）+ Barra 风格**主动暴露** + 偏离阈值告警
+ **行业轮动信号输出**（动量排名 × 当前主动敞口 → 增配/维持/减配建议）。

与既有件分工（蓝图 §0 查重裁定——异，分工论证）：factor_exposure_manager
（MOD-RK-38）=风险域**绝对**敞口监控（vs 绝对 limits，无基准无轮动）；
concentration_monitor（MOD-RK-07）=HHI/集中度三级告警；constraint_solver
（MOD-PF-006）=CTR-003 限额投影。本件=组合域基准相对主动敞口+轮动配置信号，
口径互不重复。轮动信号仅产建议，执行委托运行时装配批。

纪律：纯函数无 IO；基准/动量/载荷全部调用方注入（D_POSITION/D_FACTOR 三维解耦，
不越域取数）。

依据: blueprint.md（MOD-PF-011）§1 规则
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 组合持仓 + 行业映射（申万31）
#   fields: positions {symbol: weight}（非负归一化）; industry_map {symbol: industry}
# - id: I2
#   name: 基准（二选一）
#   fields: benchmark_weights（经映射合成行业权重）或 benchmark_industry_weights 直注
# - id: I3
#   name: 风格载荷 + 基准风格 + 行业动量
#   fields: style_loadings/benchmark_style_exposures/industry_momentum（可选注入）
# 层: 算法
# - id: A1
#   name_zh: ① 主动敞口计算
#   name_en: _active
#   intro: industry_active=p−b; style_active=Σw_p×loading−benchmark_style
# - id: A2
#   name_zh: ② 偏离分级
#   name_en: _deviations
#   intro: |active|>breach→BREACH, ≥warn→WARNING, 按|active/limit|降序
# - id: A3
#   name_zh: ③ 行业轮动信号
#   name_en: _rotation
#   intro: 动量横截面排名: top_n且active<band→OVERWEIGHT; bottom_n且active>−band→UNDERWEIGHT
# 层: 输出
# - id: O1
#   name: ActiveExposureReport
#   fields: industry_active/style_active/deviations/rotation/uncovered_symbols（frozen）
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A1 --> A3
# A2 --> O1
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ActiveExposureReport",
    "DeviationSeverity",
    "ExposureDeviation",
    "ExposureManager",
    "ExposureManagerConfig",
    "ExposureManagerError",
    "IndustryRotationAdvice",
    "RotationSignal",
]

_UNCLASSIFIED: Final = "__UNCLASSIFIED__"


class ExposureManagerError(ZephyrBaseError):
    """组合域敞口管理器输入/配置非法（Fail-Closed）。

    错误码占位：ZA-PF-0083（待主代理统一登记转正，
    建议号段 ZA-PF-0083）。
    """

    error_code = "ZA-PF-0083"


class DeviationSeverity(str, Enum):
    """偏离分级（OK 不入 deviations）。"""

    WARNING = "WARNING"
    BREACH = "BREACH"


class RotationSignal(str, Enum):
    """行业轮动建议。"""

    OVERWEIGHT = "OVERWEIGHT"
    NEUTRAL = "NEUTRAL"
    UNDERWEIGHT = "UNDERWEIGHT"


@dataclass(frozen=True)
class ExposureManagerConfig:
    """敞口管理器配置（C 类可调）。"""

    industry_warn: float = 0.05  # 行业主动敞口预警线
    industry_breach: float = 0.10  # 行业主动敞口硬上限
    style_warn: float = 0.15  # 风格主动暴露预警线（σ）
    style_breach: float = 0.30  # 风格主动暴露硬上限（σ）
    rotation_band: float = 0.10  # 轮动带宽：|active| 带内方可增/减配
    rotation_top_n: int = 5  # 动量前 N 名增配候选
    rotation_bottom_n: int = 5  # 动量后 N 名减配候选

    def __post_init__(self) -> None:
        for name in ("industry_warn", "industry_breach", "style_warn", "style_breach", "rotation_band"):
            v = float(getattr(self, name))
            if not math.isfinite(v) or v <= 0:
                raise ExposureManagerError(f"{name} 必须为正有限值: {v}")
        if self.industry_warn >= self.industry_breach:
            raise ExposureManagerError("industry_warn 必须 < industry_breach")
        if self.style_warn >= self.style_breach:
            raise ExposureManagerError("style_warn 必须 < style_breach")
        for name in ("rotation_top_n", "rotation_bottom_n"):
            v = getattr(self, name)
            if not isinstance(v, int) or v < 1:
                raise ExposureManagerError(f"{name} 必须 ≥1: {v}")


@dataclass(frozen=True)
class ExposureDeviation:
    """单维度偏离事件（frozen）。"""

    dimension: str  # industry / style
    name: str
    active: float
    limit: float
    severity: DeviationSeverity


@dataclass(frozen=True)
class IndustryRotationAdvice:
    """行业轮动建议（frozen）。"""

    industry: str
    momentum: float
    momentum_rank: int  # 1=最强
    active: float
    signal: RotationSignal


@dataclass(frozen=True)
class ActiveExposureReport:
    """组合域主动敞口报告（frozen）。"""

    industry_active: Mapping[str, float]
    style_active: Mapping[str, float]
    deviations: tuple[ExposureDeviation, ...]
    rotation: tuple[IndustryRotationAdvice, ...]
    uncovered_symbols: tuple[str, ...]
    benchmark_industry_weights: Mapping[str, float] = field(default_factory=dict)


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise ExposureManagerError(f"{name} 必须为有限值: {value}")
    return v


class ExposureManager:
    """PC-07 组合域敞口管理器（主动敞口 + 偏离告警 + 行业轮动信号）。"""

    def __init__(self, config: ExposureManagerConfig | None = None) -> None:
        self._config = config or ExposureManagerConfig()

    @property
    def config(self) -> ExposureManagerConfig:
        return self._config

    def analyze(
        self,
        *,
        positions: Mapping[str, float],
        industry_map: Mapping[str, str],
        benchmark_weights: Mapping[str, float] | None = None,
        benchmark_industry_weights: Mapping[str, float] | None = None,
        style_loadings: Mapping[str, Mapping[str, float]] | None = None,
        benchmark_style_exposures: Mapping[str, float] | None = None,
        industry_momentum: Mapping[str, float] | None = None,
    ) -> ActiveExposureReport:
        """计算主动敞口 + 偏离告警 + 轮动信号。"""
        if (benchmark_weights is None) == (benchmark_industry_weights is None):
            raise ExposureManagerError(
                "benchmark_weights 与 benchmark_industry_weights 必须二选一注入"
            )
        weights = self._normalize(positions)
        if not industry_map:
            raise ExposureManagerError("industry_map 不能为空（申万31行业分类真源）")
        uncovered: set[str] = set()

        port_ind = self._industry_weights(weights, industry_map, uncovered)
        if benchmark_industry_weights is not None:
            bench_ind = {
                k: _require_finite(f"benchmark_industry_weights[{k}]", v)
                for k, v in benchmark_industry_weights.items()
            }
        else:
            bw = self._normalize(benchmark_weights or {}, name="benchmark_weights")
            bench_ind = self._industry_weights(bw, industry_map, uncovered)

        industry_active = {
            ind: port_ind.get(ind, 0.0) - bench_ind.get(ind, 0.0)
            for ind in sorted(set(port_ind) | set(bench_ind))
        }

        style_active: dict[str, float] = {}
        if style_loadings is not None:
            port_style: dict[str, float] = {}
            for sym, w in weights.items():
                loadings = style_loadings.get(sym)
                if loadings is None:
                    uncovered.add(sym)
                    continue
                for fct, lv in loadings.items():
                    port_style[fct] = port_style.get(fct, 0.0) + w * _require_finite(
                        f"style_loadings[{sym}][{fct}]", lv
                    )
            bench_style = dict(benchmark_style_exposures or {})
            for k, v in bench_style.items():
                _require_finite(f"benchmark_style_exposures[{k}]", v)
            for fct in sorted(set(port_style) | set(bench_style)):
                style_active[fct] = port_style.get(fct, 0.0) - bench_style.get(fct, 0.0)

        deviations = self._deviations(industry_active, style_active)
        rotation = self._rotation(industry_active, industry_momentum)

        return ActiveExposureReport(
            industry_active=industry_active,
            style_active=style_active,
            deviations=deviations,
            rotation=rotation,
            uncovered_symbols=tuple(sorted(uncovered)),
            benchmark_industry_weights=dict(bench_ind),
        )

    # ── 内部 ──

    @staticmethod
    def _normalize(weights: Mapping[str, float], name: str = "positions") -> dict[str, float]:
        if not weights:
            raise ExposureManagerError(f"{name} 不能为空")
        out: dict[str, float] = {}
        for sym, w in weights.items():
            if not sym:
                raise ExposureManagerError(f"{name} 标的名不能为空")
            wv = _require_finite(f"{name}[{sym}]", w)
            if wv < 0:
                raise ExposureManagerError(f"负权重拒绝（long-only）: {sym}={w}")
            if wv > 0:
                out[sym] = wv
        total = sum(out.values())
        if total <= 0:
            raise ExposureManagerError(f"{name} 权重和必须 >0")
        return {s: w / total for s, w in out.items()}

    @staticmethod
    def _industry_weights(
        weights: Mapping[str, float], industry_map: Mapping[str, str], uncovered: set[str]
    ) -> dict[str, float]:
        agg: dict[str, float] = {}
        for sym, w in weights.items():
            ind = industry_map.get(sym)
            if ind is None:
                uncovered.add(sym)
                ind = _UNCLASSIFIED
            agg[ind] = agg.get(ind, 0.0) + w
        return agg

    def _deviations(
        self,
        industry_active: Mapping[str, float],
        style_active: Mapping[str, float],
    ) -> tuple[ExposureDeviation, ...]:
        cfg = self._config
        out: list[ExposureDeviation] = []
        for name, active, warn, breach, dim in (
            [(k, v, cfg.industry_warn, cfg.industry_breach, "industry") for k, v in industry_active.items()]
            + [(k, v, cfg.style_warn, cfg.style_breach, "style") for k, v in style_active.items()]
        ):
            a = abs(active)
            if a > breach:
                out.append(ExposureDeviation(dim, name, active, breach, DeviationSeverity.BREACH))
            elif a >= warn:
                out.append(ExposureDeviation(dim, name, active, breach, DeviationSeverity.WARNING))
        out.sort(key=lambda d: abs(d.active / d.limit), reverse=True)
        return tuple(out)

    def _rotation(
        self,
        industry_active: Mapping[str, float],
        industry_momentum: Mapping[str, float] | None,
    ) -> tuple[IndustryRotationAdvice, ...]:
        if industry_momentum is None:
            return ()
        cfg = self._config
        if not industry_momentum:
            raise ExposureManagerError("industry_momentum 注入即非空")
        mom = {
            ind: _require_finite(f"industry_momentum[{ind}]", v)
            for ind, v in industry_momentum.items()
        }
        ranked = sorted(mom, key=lambda i: (-mom[i], i))
        rank_of = {ind: i + 1 for i, ind in enumerate(ranked)}
        out: list[IndustryRotationAdvice] = []
        for ind in ranked:
            rank = rank_of[ind]
            active = industry_active.get(ind, 0.0)
            if rank <= cfg.rotation_top_n:
                signal = RotationSignal.OVERWEIGHT if active < cfg.rotation_band else RotationSignal.NEUTRAL
            elif rank > len(ranked) - cfg.rotation_bottom_n:
                signal = RotationSignal.UNDERWEIGHT if active > -cfg.rotation_band else RotationSignal.NEUTRAL
            else:
                signal = RotationSignal.NEUTRAL
            out.append(IndustryRotationAdvice(ind, mom[ind], rank, active, signal))
        return tuple(out)
