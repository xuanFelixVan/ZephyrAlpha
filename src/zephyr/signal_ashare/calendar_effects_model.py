# [BLUEPRINT] MOD-SIG-122 | docs/03_modules/_domain_signal/calendar_effects_model/blueprint.md
# [MODULE] zephyr.signal_ashare.calendar_effects_model
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（统计核心纯内存；ttest_runner/clock 全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配：收益序列 / 日历映射 / 统计器注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四类日历效应分组均值 t 检验注入统计器; 分年稳健性=显著年数/总年数>0.5; 显著节点|t|>临界且稳健; 节点数量由数据决定非人为; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/calendar_effects_model/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CalendarEffectsError(占位 ZA-SIG-UNREGISTERED-CALENDAR-EFFECTS)——空序列/参数越界/统计器未注入/日历映射不匹配/收益与日期长度不齐时抛
# [TESTS] tests/signal_ashare/test_calendar_effects_model.py
# [A_module] module_id=MOD-SIG-122 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CalendarEffectsModel — A股日历效应模型（MOD-SIG-122）。

B10-01390（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-042，A1 模块55）：
日历效应滚动统计检验：月度/周内/节假日/交割日四类（分组均值 t 检验注入
统计器 + 分年稳健性）+ 效应日历输出（显著效应节点清单，节点数量由数据
决定非人为）。

查重分工（蓝图 §0）：trading_calendar=交易日历基础定义（本件=效应统计
引擎，不复制定义）；market_lifecycle_phase=市场阶段判定（本件=日历时间
固定分组统计，零交集）；overnight_return_expectancy=隔夜收益预期（本件
=日间收益日历效应，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ttest_runner 参数
#   fields: 参数 ttest_runner（无注解）
#   code: calendar_effects_model.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: calendar_effects_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CalendarEffectsModel
#   name_en: CalendarEffectsModel
#   intro: 日历效应滚动统计件（纯内存；ttest_runner / clock 注入）。
#   desc: 日历效应滚动统计件（纯内存；ttest_runner / clock 注入）。 Args: ttest_runner: 分组均值 t 检验回调 ``runner(group_a,…；公共方法（定义序）: monthly…
#   inputs: ttest_runner clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: CalendarEffectsModel
#   downstream: 运行时装配批（统一注入点装配：收益序列 / 日历映射 / 统计器注入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CalendarEffectType",
    "CalendarEffectsModel",
    "CalendarEffectsError",
    "CalendarResult",
    "EffectNode",
]

#: 分组均值 t 检验默认显著性水平
_DEFAULT_ALPHA: Final = 0.05
#: 默认 t 临界值（|t|> 临界判定显著；双尾近似）
_DEFAULT_T_CRIT: Final = 1.96
#: 分年稳健性最小比例（显著年数/总年数 > 0.5）
_DEFAULT_ROBUSTNESS_RATIO: Final = 0.5
#: 滚动窗口最小年数
_DEFAULT_MIN_YEARS: Final = 3


class CalendarEffectsError(Exception):
    """日历效应模型输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-CALENDAR-EFFECTS。
    """


class CalendarEffectType(str, Enum):
    """日历效应类型（词表闭合）。"""

    MONTHLY = "monthly"
    WEEKLY = "weekly"
    HOLIDAY = "holiday"
    SETTLEMENT = "settlement"


@dataclass(frozen=True)
class EffectNode:
    """单个显著效应节点（frozen）。"""

    effect_type: CalendarEffectType
    label: str  # 月度如"1月"、周内如"周一"、节假日如"春节"、交割日如"交割日"
    mean_effect: float  # 分组均值
    t_stat: float  # |t| 值
    is_significant: bool  # |t| > t_critical 且 分年稳健
    robust_years: int  # 分年显著年数
    total_years: int  # 总年数


@dataclass(frozen=True)
class CalendarResult:
    """日历效应综合结果（frozen）。"""

    nodes: tuple[EffectNode, ...]
    significant_nodes: tuple[EffectNode, ...]  # 仅保留显著节点
    assessed_at: datetime.datetime


def _as_finite_series(name: str, values: Sequence[float]) -> tuple[float, ...]:
    """序列校验：长度 + 有限值，非法 Fail-Closed。"""
    try:
        seq = tuple(float(v) for v in values)
    except (TypeError, ValueError) as exc:
        raise CalendarEffectsError(f"{name} 含非数值元素: {exc}") from exc
    if len(seq) < 1:
        raise CalendarEffectsError(f"{name} 为空")
    for v in seq:
        if not math.isfinite(v):
            raise CalendarEffectsError(f"{name} 含非有限值: {v!r}")
    return seq


class CalendarEffectsModel:
    """日历效应滚动统计件（纯内存；ttest_runner / clock 注入）。

    Args:
        ttest_runner: 分组均值 t 检验回调
            ``runner(group_a, group_b) -> (t_stat, p_value)``；未注入则
            检验 Fail-Closed。
        clock: 时钟注入（测试可控）；缺省系统时钟。
    """

    def __init__(
        self,
        *,
        ttest_runner: Callable[[Sequence[float], Sequence[float]], tuple[float, float]] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._ttest = ttest_runner
        self._clock = clock or datetime.datetime.now

    # ── 通用效应检测 ──────────────────────────────────────────────────────

    def _check_ttest(self) -> Callable[[Sequence[float], Sequence[float]], tuple[float, float]]:
        """统计器注入校验。"""
        if self._ttest is None:
            raise CalendarEffectsError("ttest_runner 未注入（t 检验强制注入，Fail-Closed）")
        return self._ttest

    def _group_ttest(
        self,
        in_group: Sequence[float],
        out_group: Sequence[float],
    ) -> tuple[float, float]:
        """调用注入统计器，异常 Fail-Closed。"""
        runner = self._check_ttest()
        try:
            t_stat, p_value = runner(list(in_group), list(out_group))
        except Exception as exc:  # noqa: BLE001
            raise CalendarEffectsError(f"ttest_runner 异常: {exc}") from exc
        if not math.isfinite(t_stat) or not math.isfinite(p_value):
            raise CalendarEffectsError(f"ttest_runner 返回非有限值: t={t_stat!r} p={p_value!r}")
        return float(t_stat), float(p_value)

    def _robustness(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        labels: Sequence[str],
        target_label: str,
        t_critical: float,
        alpha: float,
    ) -> tuple[int, int]:
        """分年稳健性：每年分别对目标标签做 t 检验，|t|>t_critical 计 1。"""
        # 按年拆分为 {year: [(label, return), ...]}
        by_year: dict[int, list[tuple[str, float]]] = {}
        for y, r, l in zip(years, returns, labels, strict=False):
            by_year.setdefault(int(y), []).append((l, r))
        total = len(by_year)  # 唯一年数（非记录数）
        sig = 0
        for y, items in by_year.items():
            in_g = [r for l, r in items if l == target_label]
            out_g = [r for l, r in items if l != target_label]
            if not in_g or not out_g:
                continue
            t_stat, _ = self._group_ttest(in_g, out_g)
            if abs(t_stat) > t_critical:
                sig += 1
        return sig, total

    def _compute_effect(
        self,
        *,
        returns: Sequence[float],
        labels: Sequence[str],
        target_label: str,
        years: Sequence[int],
        t_critical: float,
        alpha: float,
        robustness_ratio: float,
        effect_type: CalendarEffectType,
        label_name: str,
    ) -> EffectNode | None:
        """单标签效应节点（无数据返回 None，数据驱动不人为）。"""
        in_group = [r for l, r in zip(labels, returns, strict=False) if l == target_label]
        out_group = [r for l, r in zip(labels, returns, strict=False) if l != target_label]
        if not in_group:
            return None  # 数据决定无此标签
        mean_eff = sum(in_group) / len(in_group)
        t_stat, _ = self._group_ttest(in_group, out_group)
        if not years or len(years) != len(returns):
            raise CalendarEffectsError("years 与 returns 长度不齐")
        robust_years, total_years = self._robustness(
            years=years,
            returns=returns,
            labels=labels,
            target_label=target_label,
            t_critical=t_critical,
            alpha=alpha,
        )
        is_sig = (abs(t_stat) > t_critical) and (total_years == 0 or (robust_years / total_years) > robustness_ratio)
        return EffectNode(
            effect_type=effect_type,
            label=label_name,
            mean_effect=mean_eff,
            t_stat=t_stat,
            is_significant=is_sig,
            robust_years=robust_years,
            total_years=total_years,
        )

    # ── 月度效应 ──────────────────────────────────────────────────────────

    def monthly_effect(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        months: Sequence[int],
        target_month: int,
        t_critical: float = _DEFAULT_T_CRIT,
        alpha: float = _DEFAULT_ALPHA,
        robustness_ratio: float = _DEFAULT_ROBUSTNESS_RATIO,
    ) -> EffectNode | None:
        """月度效应：target_month ∈ [1,12] 的分组均值 t 检验 + 分年稳健性。"""
        if not 1 <= target_month <= 12:
            raise CalendarEffectsError(f"target_month 非法: {target_month!r}")
        _as_finite_series("returns", returns)
        if len(years) != len(returns) or len(months) != len(returns):
            raise CalendarEffectsError("月度效应序列长度不齐")
        labels = [str(m) for m in months]
        return self._compute_effect(
            returns=returns,
            labels=labels,
            target_label=str(target_month),
            years=years,
            t_critical=t_critical,
            alpha=alpha,
            robustness_ratio=robustness_ratio,
            effect_type=CalendarEffectType.MONTHLY,
            label_name=f"{target_month}月",
        )

    # ── 周内效应 ──────────────────────────────────────────────────────────

    def weekly_effect(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        weekdays: Sequence[int],
        target_weekday: int,
        t_critical: float = _DEFAULT_T_CRIT,
        alpha: float = _DEFAULT_ALPHA,
        robustness_ratio: float = _DEFAULT_ROBUSTNESS_RATIO,
    ) -> EffectNode | None:
        """周内效应：target_weekday ∈ [0,6]（0=周一，6=周日）的分组 t 检验。"""
        if not 0 <= target_weekday <= 6:
            raise CalendarEffectsError(f"target_weekday 非法: {target_weekday!r}")
        _as_finite_series("returns", returns)
        if len(years) != len(returns) or len(weekdays) != len(returns):
            raise CalendarEffectsError("周内效应序列长度不齐")
        labels = [str(d) for d in weekdays]
        wname = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][target_weekday]
        return self._compute_effect(
            returns=returns,
            labels=labels,
            target_label=str(target_weekday),
            years=years,
            t_critical=t_critical,
            alpha=alpha,
            robustness_ratio=robustness_ratio,
            effect_type=CalendarEffectType.WEEKLY,
            label_name=wname,
        )

    # ── 节假日效应 ────────────────────────────────────────────────────────

    def holiday_effect(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        holiday_flags: Sequence[bool],
        t_critical: float = _DEFAULT_T_CRIT,
        alpha: float = _DEFAULT_ALPHA,
        robustness_ratio: float = _DEFAULT_ROBUSTNESS_RATIO,
    ) -> EffectNode | None:
        """节假日效应：holiday_flag=True 为节假日前/后交易日分组。"""
        _as_finite_series("returns", returns)
        if len(years) != len(returns) or len(holiday_flags) != len(returns):
            raise CalendarEffectsError("节假日效应序列长度不齐")
        labels = ["holiday" if f else "normal" for f in holiday_flags]
        return self._compute_effect(
            returns=returns,
            labels=labels,
            target_label="holiday",
            years=years,
            t_critical=t_critical,
            alpha=alpha,
            robustness_ratio=robustness_ratio,
            effect_type=CalendarEffectType.HOLIDAY,
            label_name="节假日",
        )

    # ── 交割日效应 ────────────────────────────────────────────────────────

    def settlement_effect(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        settlement_flags: Sequence[bool],
        t_critical: float = _DEFAULT_T_CRIT,
        alpha: float = _DEFAULT_ALPHA,
        robustness_ratio: float = _DEFAULT_ROBUSTNESS_RATIO,
    ) -> EffectNode | None:
        """交割日效应：settlement_flag=True 为交割日分组。"""
        _as_finite_series("returns", returns)
        if len(years) != len(returns) or len(settlement_flags) != len(returns):
            raise CalendarEffectsError("交割日效应序列长度不齐")
        labels = ["settlement" if f else "normal" for f in settlement_flags]
        return self._compute_effect(
            returns=returns,
            labels=labels,
            target_label="settlement",
            years=years,
            t_critical=t_critical,
            alpha=alpha,
            robustness_ratio=robustness_ratio,
            effect_type=CalendarEffectType.SETTLEMENT,
            label_name="交割日",
        )

    # ── 日历输出（数据驱动，节点数量由数据决定）─────────────────────────────

    def calendar_nodes(
        self,
        *,
        years: Sequence[int],
        returns: Sequence[float],
        months: Sequence[int] | None = None,
        weekdays: Sequence[int] | None = None,
        holiday_flags: Sequence[bool] | None = None,
        settlement_flags: Sequence[bool] | None = None,
        t_critical: float = _DEFAULT_T_CRIT,
        alpha: float = _DEFAULT_ALPHA,
        robustness_ratio: float = _DEFAULT_ROBUSTNESS_RATIO,
        min_years: int = _DEFAULT_MIN_YEARS,
    ) -> CalendarResult:
        """四类效应显著节点日历输出（数量由数据决定非人为）。

        不传入某类序列则该类不检测（语义等同于无此类数据）。
        """
        nodes: list[EffectNode] = []
        unique_years = sorted({int(y) for y in years})
        if len(unique_years) < min_years:
            raise CalendarEffectsError(f"总年数 {len(unique_years)} < 最小滚动窗口 {min_years}")
        if months is not None:
            for m in range(1, 13):
                node = self.monthly_effect(
                    years=years,
                    returns=returns,
                    months=months,
                    target_month=m,
                    t_critical=t_critical,
                    alpha=alpha,
                    robustness_ratio=robustness_ratio,
                )
                if node is not None:
                    nodes.append(node)
        if weekdays is not None:
            for d in range(7):
                node = self.weekly_effect(
                    years=years,
                    returns=returns,
                    weekdays=weekdays,
                    target_weekday=d,
                    t_critical=t_critical,
                    alpha=alpha,
                    robustness_ratio=robustness_ratio,
                )
                if node is not None:
                    nodes.append(node)
        if holiday_flags is not None:
            node = self.holiday_effect(
                years=years,
                returns=returns,
                holiday_flags=holiday_flags,
                t_critical=t_critical,
                alpha=alpha,
                robustness_ratio=robustness_ratio,
            )
            if node is not None:
                nodes.append(node)
        if settlement_flags is not None:
            node = self.settlement_effect(
                years=years,
                returns=returns,
                settlement_flags=settlement_flags,
                t_critical=t_critical,
                alpha=alpha,
                robustness_ratio=robustness_ratio,
            )
            if node is not None:
                nodes.append(node)
        sig = tuple(n for n in nodes if n.is_significant)
        _log.info(
            "日历效应节点: 总=%d 显著=%d 类型覆盖=%s",
            len(nodes),
            len(sig),
            sorted({n.effect_type.value for n in nodes}),
        )
        return CalendarResult(
            nodes=tuple(nodes),
            significant_nodes=sig,
            assessed_at=self._clock(),
        )
