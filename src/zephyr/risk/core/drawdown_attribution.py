# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.12/§3.16/§6.7/§6.13
# [MODULE] zephyr.risk.core.drawdown_attribution
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.risk.core.daily_auditor(import-only: AttributionBias/AttributionStatus 消费,不改)
# [CONSUMERS] RiskOrchestrator(§6.5 接线位); drawdown_session_persistence(归因持久化载荷)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 先诊断类型再分流(§3.12); 风险恶化前馈优先于NAV回撤反馈(VaR比>1.5即减仓不等回撤); 未达WARNING 5%不归因(返回None); 高相关>0.7=系统性全局收缩/低相关<0.4=策略特定单策略收缩/中间=MIXED按|dd|占比拆分; AttributionBias BIASED=行为性最高优先级(停实盘修执行); regime交叉验证只追加后缀不改主因
# [MODIFY-GUARD] tests/risk/test_drawdown_attribution.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAttributionInputError(ZA-RK-0063)
# [TESTS] tests/risk/test_drawdown_attribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 诊断输入(信号按规则/止损均R/仓位一致/频率在计划/市场结构质变, §3.12五问矩阵)
# I2: 归因输入(drawdown_pct+strategy_pnls+entry_var/current_var+pnls_history+AttributionBias+regime)
# F1: diagnose_drawdown_type(五问任一违例→BEHAVIOURAL, 全None→UNDETERMINED, 否则STATISTICAL)
# F2: drawdown_attribution_flow(0 VaR恶化比>1.5前馈减仓≤50% → 1 dd<5%门控 → 2 相关性归因 → 3 因子偏差 → 4 regime交叉)
# A1: _avg_correlation(20日窗策略PnL两两Pearson均值, 除零/样本不足守卫)
# O1: DrawdownDiagnosis / AttributionResult(systemic_pct+per_strategy+root_cause+response_routing) 或 None
# [/ALGO_FLOW]
"""D_RISK — 回撤类型诊断 + 归因自动化（35 号 memo §6.7/§6.13 施工，§3.12/§3.16 落地）。

痛点：回撤触发后不区分"方差亏损簇"（统计性）vs "AI 执行偏差"（行为性）、
"系统性"（高相关全局）vs "策略特定"（低相关单策略），仅靠人工判读矩阵。

本模块落地：
  - diagnose_drawdown_type（§3.12 五问诊断矩阵）：信号按策略规则生成？/
    止损每次执行（均损 ≈1R，>1.2R 违例）？/仓位按算法一致？/频率在计划内？/
    市场结构质变？——任一行为性违例 → BEHAVIOURAL（停实盘+修执行）；
    全部未知 → UNDETERMINED；否则 STATISTICAL（按三层映射减仓继续执行）。
  - drawdown_attribution_flow（§3.16 端到端归因）：
    0. 风险恶化前馈：current_var/entry_var > 1.5 → 乘性减仓（最高 50%），
       不等 NAV 回撤（RISK_BASED_REDUCTION，§3.19 前馈边界）；
    1. WARNING 门控：|dd| < 5% 不归因（返回 None）；
    2. 相关性归因（orstac correlation-aware）：avg_corr > 0.7 系统性 /
       < 0.4 策略特定 / 中间 MIXED 按 |dd| 占比拆分（除零守卫）；
    3. 因子归因：复用 daily_auditor AttributionBias（import-only 消费，
       禁止修改 daily_auditor.py）——BIASED → 行为性最高优先级
       （STOP_LIVE_AND_FIX_EXECUTION）；
    4. regime 交叉验证（§3.9）：ACCEL_DECLINE/PANIC_CRASH/CRISIS →
       _REGIME_ALIGNED 后缀，否则 _REGIME_MISALIGNED（异常告警信号）。

SSoT: 35_drawdown_protocol_impl §3.12/§3.16 + §6.7/§6.13
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final, Mapping, Sequence

from zephyr.risk.core.daily_auditor import AttributionBias, AttributionStatus
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidAttributionInputError",
    "DrawdownType",
    "ResponseRouting",
    "DrawdownDiagnosis",
    "AttributionResult",
    "REGIME_ALIGNED_SET",
    "diagnose_drawdown_type",
    "drawdown_attribution_flow",
]

_logger = logging.getLogger(__name__)

#: regime 交叉验证对齐集合（§3.9/§3.16：下跌/恐慌/危机态组合亏损=预期内）
REGIME_ALIGNED_SET: Final = frozenset({"ACCEL_DECLINE", "PANIC_CRASH", "CRISIS"})

#: §3.12 诊断矩阵：平均损失超 1.2R = 止损被放宽（行为性违例）
_MAX_AVG_LOSS_R: Final = 1.2


class InvalidAttributionInputError(ZephyrBaseError):
    """归因/诊断输入非法（阈值非法/历史窗口畸形等）。"""

    error_code = "ZA-RK-0063"


class DrawdownType(str, Enum):
    """回撤类型（§3.12 二分）。"""

    STATISTICAL = "STATISTICAL"      # 统计性：正期望策略的方差亏损簇 → 减仓继续
    BEHAVIOURAL = "BEHAVIOURAL"      # 行为性：AI 执行偏差 → 停实盘+修执行
    UNDETERMINED = "UNDETERMINED"    # 证据不足（全部维度未知）


class ResponseRouting(str, Enum):
    """响应分流（§3.16 对照表）。"""

    RISK_BASED_REDUCTION = "RISK_BASED_REDUCTION"          # VaR 恶化前馈减仓
    GLOBAL_CONTRACTION = "GLOBAL_CONTRACTION"              # 系统性 → 全局收缩
    PER_STRATEGY_CONTRACTION = "PER_STRATEGY_CONTRACTION"  # 策略特定 → 单策略收缩
    STOP_LIVE_AND_FIX_EXECUTION = "STOP_LIVE_AND_FIX_EXECUTION"  # 行为性 → 停实盘修执行


@dataclass(frozen=True)
class DrawdownDiagnosis:
    """回撤类型诊断结果（§3.12 五问矩阵）。

    Attributes:
        drawdown_type: STATISTICAL / BEHAVIOURAL / UNDETERMINED
        violations: 命中的行为性违例项（人类可读）
        market_structure_changed: 市场结构质变提示（regime 转换未覆盖信号）
    """

    drawdown_type: DrawdownType
    violations: tuple[str, ...] = ()
    market_structure_changed: bool | None = None


@dataclass(frozen=True)
class AttributionResult:
    """归因结果（§3.16 AttributionResult）。

    Attributes:
        systemic_pct: 系统性占比（1.0=全系统性 / 0.0=全策略特定 / 中间=混合近似）
        per_strategy_contribution: 各策略贡献占比（单策略=1.0；MIXED 按 |dd| 占比）
        root_cause: 根因码（含 _REGIME_ALIGNED/_REGIME_MISALIGNED 后缀）
        response_routing: 响应分流（ResponseRouting 值）
        attribution_bias: daily_auditor AttributionBias（None=未提供/不适用）
        risk_deterioration_ratio: VaR 恶化比（仅 RISK_DETERIORATION 路径非 None）
        recommended_reduction: 建议乘性减仓比例（仅 RISK_DETERIORATION 路径非 None）
    """

    systemic_pct: float
    per_strategy_contribution: dict[str, float] | None
    root_cause: str
    response_routing: str
    attribution_bias: AttributionBias | None = None
    risk_deterioration_ratio: float | None = None
    recommended_reduction: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """§3.18 阶段 4c 持久化载荷。"""
        return {
            "systemic_pct": self.systemic_pct,
            "per_strategy_contribution": self.per_strategy_contribution,
            "root_cause": self.root_cause,
            "response_routing": self.response_routing,
            "attribution_bias": (
                self.attribution_bias.to_dict() if self.attribution_bias else None
            ),
            "risk_deterioration_ratio": self.risk_deterioration_ratio,
            "recommended_reduction": self.recommended_reduction,
        }


def diagnose_drawdown_type(
    *,
    signals_follow_rules: bool | None = None,
    avg_loss_r: float | None = None,
    position_sizing_consistent: bool | None = None,
    trade_frequency_in_plan: bool | None = None,
    market_structure_changed: bool | None = None,
) -> DrawdownDiagnosis:
    """回撤类型诊断（§3.12 五问矩阵）：任一行为性违例 → BEHAVIOURAL。

    Args:
        signals_follow_rules: 信号是否严格按策略规则生成（False=违例①）
        avg_loss_r: 平均亏损 R 倍数（> 1.2R=止损被放宽，违例②；None=未知）
        position_sizing_consistent: 仓位是否按算法一致（False=报复性加仓，违例③）
        trade_frequency_in_plan: 交易频率是否在计划内（False=过度交易，违例④）
        market_structure_changed: 市场结构是否质变（True=regime 转换未覆盖提示，
            不构成行为性违例，仅记录）

    Returns:
        DrawdownDiagnosis（全部维度未知 → UNDETERMINED）
    """
    if avg_loss_r is not None and avg_loss_r < 0:
        raise InvalidAttributionInputError(f"avg_loss_r 须 >= 0, got {avg_loss_r}")
    violations: list[str] = []
    if signals_follow_rules is False:
        violations.append("信号未严格按策略规则生成（规则被 AI 弯曲/遗漏）")
    if avg_loss_r is not None and avg_loss_r > _MAX_AVG_LOSS_R:
        violations.append(f"平均损失 {avg_loss_r:.2f}R > 1.2R（止损被放宽）")
    if position_sizing_consistent is False:
        violations.append("仓位未按算法一致（报复性加仓）")
    if trade_frequency_in_plan is False:
        violations.append("交易频率超出计划（过度交易）")

    known = [
        signals_follow_rules, avg_loss_r, position_sizing_consistent,
        trade_frequency_in_plan, market_structure_changed,
    ]
    if violations:
        drawdown_type = DrawdownType.BEHAVIOURAL
    elif all(v is None for v in known):
        drawdown_type = DrawdownType.UNDETERMINED
    else:
        drawdown_type = DrawdownType.STATISTICAL
    if violations:
        _logger.warning("DRAWDOWN_TYPE_BEHAVIOURAL violations=%s", violations)
    return DrawdownDiagnosis(
        drawdown_type=drawdown_type,
        violations=tuple(violations),
        market_structure_changed=market_structure_changed,
    )


def _avg_correlation(
    strategy_pnls_history: Mapping[str, Sequence[float]], window: int
) -> float:
    """20 日窗策略 PnL 两两 Pearson 相关均值（orstac correlation-aware）。

    除零/样本不足守卫：任一序列方差为 0 或有效窗 < 2 → 该对跳过；
    无有效对 → 0.0（保守视为低相关=策略特定）。
    """
    series = [list(map(float, v))[-window:] for v in strategy_pnls_history.values()]
    series = [s for s in series if len(s) >= 2]
    if len(series) < 2:
        return 0.0
    corrs: list[float] = []
    for i in range(len(series)):
        for j in range(i + 1, len(series)):
            a, b = series[i], series[j]
            n = min(len(a), len(b))
            a, b = a[-n:], b[-n:]
            mean_a, mean_b = sum(a) / n, sum(b) / n
            var_a = sum((x - mean_a) ** 2 for x in a)
            var_b = sum((x - mean_b) ** 2 for x in b)
            if var_a <= 0 or var_b <= 0:
                continue  # 方差为 0（常数序列）→ 该对无相关定义，跳过
            cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
            corrs.append(cov / math.sqrt(var_a * var_b))
    if not corrs:
        return 0.0
    return sum(corrs) / len(corrs)


def drawdown_attribution_flow(
    *,
    drawdown_pct: float,
    strategy_pnls: Mapping[str, float] | None = None,
    entry_var: float | None = None,
    current_var: float | None = None,
    strategy_pnls_history: Mapping[str, Sequence[float]] | None = None,
    attribution_bias: AttributionBias | None = None,
    regime: str | None = None,
    warning_threshold: float = 0.05,
    var_deterioration_threshold: float = 1.5,
    max_reduction: float = 0.5,
    corr_window: int = 20,
    systemic_corr: float = 0.7,
    specific_corr: float = 0.4,
) -> AttributionResult | None:
    """回撤归因端到端流程（§3.16）：前馈 VaR 恶化 → 门控 → 相关性 → 因子 → regime。

    Args:
        drawdown_pct: 当前组合回撤（负号或绝对值均可，内部取 abs）
        strategy_pnls: {strategy_id: 当日 pnl}（None/单策略 → 策略特定）
        entry_var: 前日盘前 VaR_95（§3.18 阶段 4b 持久化；None=跳过前馈）
        current_var: 当日 VaR_95（None=跳过前馈）
        strategy_pnls_history: {strategy_id: 近 20 日 pnl 序列}（None=跳过相关性）
        attribution_bias: daily_auditor.detect_attribution_bias 产出
            （import-only 消费；None/NOT_APPLICABLE=跳过因子归因）
        regime: 当前 regime（REGIME_ALIGNED_SET 内=预期内）
        warning_threshold: 归因门控（默认 5%，§3.16 WARNING 触发）
        var_deterioration_threshold: VaR 恶化比阈值（默认 1.5）
        max_reduction: 前馈减仓上限（默认 0.5=50%）
        corr_window: 相关性窗口（默认 20 日）
        systemic_corr/specific_corr: 系统性/策略特定相关阈值（0.7/0.4）

    Returns:
        AttributionResult；未达 WARNING 门控返回 None
    """
    for name, v in (("entry_var", entry_var), ("current_var", current_var)):
        if v is not None and v < 0:
            raise InvalidAttributionInputError(f"{name} 须 >= 0, got {v}")
    if not 0 < warning_threshold < 1:
        raise InvalidAttributionInputError("warning_threshold 须在 (0,1)")
    if var_deterioration_threshold <= 1.0:
        raise InvalidAttributionInputError("var_deterioration_threshold 须 > 1")
    if not 0 < max_reduction <= 1:
        raise InvalidAttributionInputError("max_reduction 须在 (0,1]")
    if corr_window < 2:
        raise InvalidAttributionInputError("corr_window 须 >= 2")
    if not 0 < specific_corr < systemic_corr < 1:
        raise InvalidAttributionInputError("相关阈值须满足 0 < specific < systemic < 1")

    # ── 0. 风险恶化型归因（前馈：VaR 恶化即减仓，不等 NAV 回撤）──
    if entry_var is not None and current_var is not None and entry_var > 0:
        ratio = current_var / entry_var
        if ratio > var_deterioration_threshold:
            reduction = min(ratio - 1.0, max_reduction)
            _logger.warning(
                "RISK_DETERIORATION entry_var=%.4f current_var=%.4f ratio=%.2f reduction=%.2f",
                entry_var, current_var, ratio, reduction,
            )
            return AttributionResult(
                systemic_pct=1.0,  # VaR 是组合度量 → 风险恶化是组合级
                per_strategy_contribution=None,
                root_cause=f"RISK_DETERIORATION_VAR_RATIO_{ratio:.1f}",
                response_routing=ResponseRouting.RISK_BASED_REDUCTION.value,
                attribution_bias=attribution_bias,
                risk_deterioration_ratio=ratio,
                recommended_reduction=reduction,
            )

    # ── 门控：未达 WARNING（5%）不归因 ──
    dd = abs(drawdown_pct)
    if dd < warning_threshold:
        return None

    # ── 1. 策略间相关性归因（orstac correlation-aware）──
    pnls = dict(strategy_pnls or {})
    if len(pnls) <= 1 or strategy_pnls_history is None:
        systemic_pct = 0.0
        root_cause = (
            "STRATEGY_SPECIFIC_SINGLE_STRATEGY" if len(pnls) <= 1
            else "STRATEGY_SPECIFIC_INSUFFICIENT_HISTORY"
        )
        per_strategy = {next(iter(pnls)): 1.0} if pnls else {}
    else:
        avg_corr = _avg_correlation(strategy_pnls_history, corr_window)
        if avg_corr > systemic_corr:
            systemic_pct, root_cause, per_strategy = (
                1.0, "SYSTEMIC_HIGH_CORRELATION", None,
            )
        elif avg_corr < specific_corr:
            systemic_pct, root_cause, per_strategy = (
                0.0, "STRATEGY_SPECIFIC_LOW_CORRELATION", None,
            )
        else:
            total_abs = sum(abs(v) for v in pnls.values())
            per_strategy = (
                {sid: abs(v) / total_abs for sid, v in pnls.items()}
                if total_abs > 1e-10 else {sid: 0.0 for sid in pnls}
            )
            systemic_pct, root_cause = avg_corr, "MIXED_PARTIAL_SYSTEMIC"

    # ── 2. 因子归因（AttributionBias BIASED=行为性最高优先级，§3.12 分流）──
    if (
        attribution_bias is not None
        and attribution_bias.status is AttributionStatus.BIASED
    ):
        root_cause = "BEHAVIOURAL_ATTRIBUTION_BIAS"
        routing = ResponseRouting.STOP_LIVE_AND_FIX_EXECUTION
    elif root_cause.startswith("SYSTEMIC"):
        routing = ResponseRouting.GLOBAL_CONTRACTION
    else:
        routing = ResponseRouting.PER_STRATEGY_CONTRACTION

    # ── 3. regime 交叉验证（§3.9：只追加后缀不改主因）──
    root_cause += (
        "_REGIME_ALIGNED" if regime in REGIME_ALIGNED_SET else "_REGIME_MISALIGNED"
    )
    result = AttributionResult(
        systemic_pct=systemic_pct,
        per_strategy_contribution=per_strategy,
        root_cause=root_cause,
        response_routing=routing.value,
        attribution_bias=attribution_bias,
    )
    _logger.info(
        "DRAWDOWN_ATTRIBUTION dd=%.4f root_cause=%s routing=%s systemic=%.2f",
        dd, result.root_cause, result.response_routing, result.systemic_pct,
    )
    return result
