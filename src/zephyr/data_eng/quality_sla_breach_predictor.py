# [BLUEPRINT] MOD-DATENG-003 | docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md
# [MODULE] zephyr.data_eng.quality_sla_breach_predictor
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] 无（预测核心纯内存；SLO序列/clock/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（数据新鲜度/完整性/信号产出 SLO 巡检挂调度 / 告警接 alert 路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] SLO注册表闭合(未注册SLO禁止预测); 达成率序列线性外推确定性(最小二乘); burn-rate分级词表闭合(healthy|elevated|critical|exhausted); 错误预算累计消耗(左黎曼)确定性; 预测输入至少2观测点; 告警仅回调不阻断; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/quality_sla_breach_predictor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] QualitySlaPredictorError(占位 ZA-DE-UNREGISTERED-QUALITY-SLA-PREDICT)——空SLO名/非法target/重复注册/未知SLO/观测点不足/达成率越界时抛
# [TESTS] tests/data_eng/test_quality_sla_breach_predictor.py
# [A_module] module_id=MOD-DATENG-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
QualitySlaBreachPredictor — 质量 SLA 违约预测器（MOD-DATENG-003）。

B14-04723（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-006，A9运维架
构）：基于历史达成率与消耗速率**趋势外推**的数据质量 SLO（数据新鲜度/
完整性/信号产出）违约预测——最小二乘线性外推 + 错误预算累计消耗双线
预测违约时间窗、Google SRE 式 burn-rate 分级、提前告警回调、建议处置
窗口输出。

边界声明（蓝图 §0）：sla_monitor（D_INFRASTRUCTURE）为运行时 SLI 采集
件——本件不采集指标，只对注入的达成率序列做外推预测；告警经注入
alert_sink 回调，本件不接告警路由。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: quality_sla_breach_predictor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: quality_sla_breach_predictor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: elevated_threshold 参数
#   fields: 参数 elevated_threshold（无注解）
#   code: quality_sla_breach_predictor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: critical_threshold 参数
#   fields: 参数 critical_threshold（无注解）
#   code: quality_sla_breach_predictor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① QualitySlaBreachPredictor
#   name_en: QualitySlaBreachPredictor
#   intro: 质量 SLO 违约预测件（注册表 + 趋势外推 + burn-rate 分级 + 告警）。
#   desc: 质量 SLO 违约预测件（注册表 + 趋势外推 + burn-rate 分级 + 告警）。；公共方法（定义序）: register_slo, forecast；源码 L155-L287
#   inputs: clock alert_sink elevated_threshold critical_threshold
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: QualitySlaBreachPredictor
#   downstream: 运行时装配批（数据新鲜度/完整性/信号产出 SLO 巡检挂调度 / 告警接 alert 路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "BreachForecast",
    "BurnRateLevel",
    "QualitySlaBreachPredictor",
    "QualitySlaPredictorError",
    "SloPoint",
]


class QualitySlaPredictorError(Exception):
    """质量 SLA 违约预测输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DE-UNREGISTERED-QUALITY-SLA-PREDICT。
    """


class BurnRateLevel(str, Enum):
    """burn-rate 分级（词表闭合）。"""

    HEALTHY = "healthy"
    ELEVATED = "elevated"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"


@dataclass(frozen=True)
class SloPoint:
    """SLO 达成率观测点（attainment ∈ [0,1]，frozen）。"""

    observed_at: datetime.datetime
    attainment: float


@dataclass(frozen=True)
class BreachForecast:
    """违约预测结论（burn-rate + 分级 + 预测违约时刻 + 建议处置窗口）。"""

    slo_name: str
    target: float
    burn_rate: float
    level: BurnRateLevel
    predicted_breach_at: datetime.datetime | None
    action_window: tuple[datetime.datetime, datetime.datetime] | None
    detail: str


def _linear_fit(xs: tuple[float, ...], ys: tuple[float, ...]) -> tuple[float, float]:
    """最小二乘拟合 y = slope*x + intercept（确定性，n>=2）。"""
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x == 0.0:
        # 全部观测同一时刻：无法外推速率，斜率按 0 处理
        return 0.0, mean_y
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=False))
    slope = cov / var_x
    return slope, mean_y - slope * mean_x


def _budget_crossing_x(xs: tuple[float, ...], ys: tuple[float, ...], allowed: float) -> float | None:
    """错误预算耗尽时刻（左黎曼累计消耗穿越 allowed 的线性插值 x 偏移秒）。"""
    consumed = 0.0
    for i in range(len(xs) - 1):
        seg = (1.0 - ys[i]) * (xs[i + 1] - xs[i])
        if seg > 0.0 and consumed + seg >= allowed:
            frac = (allowed - consumed) / seg
            return xs[i] + frac * (xs[i + 1] - xs[i])
        consumed += seg
    return None  # 观测窗内未耗尽


class QualitySlaBreachPredictor:
    """质量 SLO 违约预测件（注册表 + 趋势外推 + burn-rate 分级 + 告警）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[BreachForecast], None] | None = None,
        elevated_threshold: float = 1.0,
        critical_threshold: float = 2.0,
    ) -> None:
        if elevated_threshold < 0:
            raise QualitySlaPredictorError("elevated_threshold 非法")
        if critical_threshold < elevated_threshold:
            raise QualitySlaPredictorError("critical_threshold 须 >= elevated_threshold")
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._elevated = elevated_threshold
        self._critical = critical_threshold
        self._slos: dict[str, float] = {}

    # ── SLO 注册 ──────────────────────────────────────────────────────────

    def register_slo(self, name: str, target: float) -> None:
        """登记质量 SLO：name 唯一，target ∈ (0,1)（如 0.99）。"""
        if not name:
            raise QualitySlaPredictorError("slo name 为空")
        if not 0.0 < target < 1.0:
            raise QualitySlaPredictorError(f"target 非法: {target!r}（须 ∈ (0,1)）")
        if name in self._slos:
            raise QualitySlaPredictorError(f"SLO 重复注册: {name!r}")
        self._slos[name] = target

    # ── 预测 ──────────────────────────────────────────────────────────────

    def forecast(self, name: str, points: Iterable[SloPoint]) -> BreachForecast:
        """违约预测：趋势外推 + 错误预算消耗双线预测 + burn-rate 分级。

        - burn_rate（短窗）= (1-末次达成率)/(1-target)：>elevated→ELEVATED，
          >critical→CRITICAL；
        - 错误预算（长窗）= budget_rate×观测跨度，累计消耗（左黎曼）超支
          → EXHAUSTED，耗尽时刻线性插值；
        - 预测违约时刻 = min(趋势外推 fitted(t*)=target, 预算耗尽时刻)。
        """
        target = self._slos.get(name)
        if target is None:
            raise QualitySlaPredictorError(f"未知 SLO: {name!r}（未注册）")
        obs = sorted(points, key=lambda p: p.observed_at)
        if len(obs) < 2:
            raise QualitySlaPredictorError(f"观测点不足: {name!r} 需 >=2，实得 {len(obs)}")
        for p in obs:
            if not 0.0 <= p.attainment <= 1.0:
                raise QualitySlaPredictorError(f"达成率越界: {p.attainment!r}（须 ∈ [0,1]）")

        t0 = obs[0].observed_at
        xs = tuple((p.observed_at - t0).total_seconds() for p in obs)
        ys = tuple(p.attainment for p in obs)
        slope, intercept = _linear_fit(xs, ys)

        last = obs[-1]
        budget_rate = 1.0 - target
        burn_rate = max(0.0, (1.0 - last.attainment) / budget_rate)

        span = xs[-1] - xs[0]
        allowed = budget_rate * span
        consumed = sum((1.0 - ys[i]) * (xs[i + 1] - xs[i]) for i in range(len(xs) - 1))
        exhausted = consumed >= allowed > 0.0

        if exhausted:
            level = BurnRateLevel.EXHAUSTED
        elif burn_rate > self._critical:
            level = BurnRateLevel.CRITICAL
        elif burn_rate > self._elevated:
            level = BurnRateLevel.ELEVATED
        else:
            level = BurnRateLevel.HEALTHY

        # 双线预测违约时刻：① 趋势外推 fitted(t*)=target；② 预算耗尽
        candidates: list[float] = []
        if slope < 0.0:
            t_star = (target - intercept) / slope
            if t_star > xs[-1]:
                candidates.append(t_star)
        if exhausted:
            cross_x = _budget_crossing_x(xs, ys, allowed)
            candidates.append(cross_x if cross_x is not None else xs[-1])
        elif consumed > 0.0:
            rate = consumed / span if span > 0.0 else 0.0
            if rate > 0.0:
                candidates.append(xs[-1] + (allowed - consumed) / rate)

        predicted_breach_at: datetime.datetime | None = None
        if candidates:
            predicted_breach_at = t0 + datetime.timedelta(seconds=min(candidates))

        now = self._clock()
        action_window: tuple[datetime.datetime, datetime.datetime] | None = None
        if predicted_breach_at is not None:
            action_window = (now, predicted_breach_at)

        detail = (
            f"burn_rate={burn_rate:.4f} level={level.value} "
            f"budget_consumed={consumed:.1f}s/{allowed:.1f}s "
            f"slope={slope:.6e}/s last_attainment={last.attainment:.4f} target={target}"
        )
        forecast = BreachForecast(
            slo_name=name,
            target=target,
            burn_rate=burn_rate,
            level=level,
            predicted_breach_at=predicted_breach_at,
            action_window=action_window,
            detail=detail,
        )
        if level in (BurnRateLevel.CRITICAL, BurnRateLevel.EXHAUSTED):
            self._alert(forecast)
        return forecast

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, forecast: BreachForecast) -> None:
        _log.warning(
            "质量SLO违约预警: %s burn_rate=%.2f level=%s breach_at=%s",
            forecast.slo_name,
            forecast.burn_rate,
            forecast.level.value,
            forecast.predicted_breach_at,
        )
        if self._alert_sink is not None:
            try:
                self._alert_sink(forecast)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败: %s", forecast.slo_name)
