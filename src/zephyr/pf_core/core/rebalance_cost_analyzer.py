# [BLUEPRINT] MOD-PF-014 | docs/03_modules/_domain_portfolio_core/rebalance_cost_analyzer/blueprint.md
# [MODULE] zephyr.pf_core.core.rebalance_cost_analyzer
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] 无（分析核心纯内存；税率表/告警回调/时钟全注入）
# [CONSUMERS] 运行时装配批（rebalance_engine 调仓复盘 / 成本归因报表装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 成本四类闭合(explicit|implicit|tax|opportunity); explicit=Σ(佣金+印花税); implicit=Σ(冲击+价差); tax=max(0,股息)×股息率+max(0,利得)×利得率; opportunity=名义额×(基准收益-组合收益)(带符号); 报告按|占比|降序平手按类名; cost_bps=总成本/名义额×10000; 超阈值告警(回调异常不阻断如实记录); Decimal-only拒绝float; 报告frozen; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_portfolio_core/rebalance_cost_analyzer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RebalanceCostError(占位 ZA-PF-UNREGISTERED-REBALANCE-COST)——税率表缺键/越界/非Decimal/空腿单/非法数量价格成本时抛
# [TESTS] tests/pf_core/test_rebalance_cost_analyzer.py
# [A_module] module_id=MOD-PF-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
RebalanceCostAnalyzer — 再平衡成本分析器（MOD-PF-014）。

B10-02079（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PF004-007，A1 PC-10）：
调仓成本**四拆解**（Decimal-only）——

① 显性成本：Σ（佣金 + 印花税）（腿单注入）；
② 隐性成本：Σ（冲击成本 + 价差成本）（腿单注入）；
③ 税收：max(0,股息)×股息率 + max(0,资本利得)×利得率（税率表注入，
   负利得不退税）；
④ 机会成本：调仓名义额 ×（基准收益 − 组合收益）（带符号，跑赢基准为负
   成本即收益）。

拆解报告按 |占比| 降序（平手按类名字典序）；cost_bps = 总成本/名义额
×10000；超告警阈值 → 告警回调（异常不阻断如实记录）。

查重分工（蓝图 §0）：rebalance_engine=调仓决策与执行（事前/事中）；本件
=**事后成本归因分析器**（四拆解+占比排序+异常告警），不做调仓决策。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: tax_table 参数
#   fields: 参数 tax_table（无注解）
#   code: rebalance_cost_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: alert_threshold_bps 参数
#   fields: 参数 alert_threshold_bps（无注解）
#   code: rebalance_cost_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: rebalance_cost_analyzer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: rebalance_cost_analyzer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RebalanceCostAnalyzer
#   name_en: RebalanceCostAnalyzer
#   intro: 再平衡成本四拆解分析器（纯内存确定性，税率表/告警/时钟注入）。
#   desc: 再平衡成本四拆解分析器（纯内存确定性，税率表/告警/时钟注入）。；公共方法（定义序）: analyze；源码 L174-L282
#   inputs: tax_table alert_threshold_bps alert_sink clock
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: RebalanceCostAnalyzer
#   downstream: 运行时装配批（rebalance_engine 调仓复盘 / 成本归因报表装配）
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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "CostBreakdownItem",
    "CostCategory",
    "RebalanceCostAnalyzer",
    "RebalanceCostError",
    "RebalanceCostReport",
    "TradeLeg",
    "TradeSide",
]

_DIVIDEND_RATE_KEY: Final = "dividend_rate"
_CAPITAL_GAIN_RATE_KEY: Final = "capital_gain_rate"
_TAX_KEYS: Final = (_DIVIDEND_RATE_KEY, _CAPITAL_GAIN_RATE_KEY)
_BPS_FACTOR: Final = Decimal("10000")


class RebalanceCostError(Exception):
    """再平衡成本分析输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PF-UNREGISTERED-REBALANCE-COST。
    """


class TradeSide(str, Enum):
    """调仓腿单方向。"""

    BUY = "buy"
    SELL = "sell"


class CostCategory(str, Enum):
    """成本四类（词表闭合）。"""

    EXPLICIT = "explicit"  # 显性：佣金/印花税
    IMPLICIT = "implicit"  # 隐性：冲击/价差
    TAX = "tax"  # 税收：股息税/资本利得
    OPPORTUNITY = "opportunity"  # 机会成本：偏离基准收益


@dataclass(frozen=True)
class TradeLeg:
    """调仓腿单（成本分量注入，frozen，Decimal-only）。"""

    symbol: str
    side: TradeSide
    qty: Decimal
    price: Decimal
    commission: Decimal
    stamp_duty: Decimal
    impact_cost: Decimal
    spread_cost: Decimal


@dataclass(frozen=True)
class CostBreakdownItem:
    """单类成本拆解项（frozen）。"""

    category: CostCategory
    amount: Decimal
    ratio: Decimal  # |amount| / Σ|各类amount|（Σ=0 时各类=0）


@dataclass(frozen=True)
class RebalanceCostReport:
    """成本拆解报告（frozen，items 按占比降序确定性排序）。"""

    items: tuple[CostBreakdownItem, ...]
    total_cost: Decimal
    total_notional: Decimal
    cost_bps: Decimal
    alerted: bool
    alert_threshold_bps: Decimal
    analyzed_at: datetime.datetime


def _require_decimal(name: str, value: object) -> Decimal:
    if not isinstance(value, Decimal):
        raise RebalanceCostError(f"{name} 须为 Decimal（Decimal-only，拒绝 float 隐式转换）: {type(value).__name__}")
    if not value.is_finite():
        raise RebalanceCostError(f"{name} 非有限: {value!r}")
    return value


class RebalanceCostAnalyzer:
    """再平衡成本四拆解分析器（纯内存确定性，税率表/告警/时钟注入）。"""

    def __init__(
        self,
        *,
        tax_table: Mapping[str, Decimal],
        alert_threshold_bps: Decimal = Decimal("50"),
        alert_sink: Callable[[RebalanceCostReport], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not tax_table:
            raise RebalanceCostError("tax_table 为空（税率表须注入）")
        for key in _TAX_KEYS:
            if key not in tax_table:
                raise RebalanceCostError(f"税率表缺键: {key!r}")
            rate = _require_decimal(f"tax_table[{key!r}]", tax_table[key])
            if not (Decimal("0") <= rate <= Decimal("1")):
                raise RebalanceCostError(f"税率越界[0,1]: {key!r}={rate!r}")
        _require_decimal("alert_threshold_bps", alert_threshold_bps)
        if alert_threshold_bps < 0:
            raise RebalanceCostError(f"alert_threshold_bps 须非负: {alert_threshold_bps!r}")
        self._tax_table = dict(tax_table)
        self._alert_threshold_bps = alert_threshold_bps
        self._alert_sink = alert_sink
        self._clock = clock or datetime.datetime.now

    # ── 分析 ─────────────────────────────────────────────────────────────

    def analyze(
        self,
        *,
        legs: Sequence[TradeLeg],
        dividend_income: Decimal = Decimal("0"),
        capital_gain: Decimal = Decimal("0"),
        portfolio_return: Decimal = Decimal("0"),
        benchmark_return: Decimal = Decimal("0"),
    ) -> RebalanceCostReport:
        """四拆解 + 占比排序报告 + 异常告警（非法输入 Fail-Closed）。"""
        if not legs:
            raise RebalanceCostError("legs 为空（无调仓腿单）")
        _require_decimal("dividend_income", dividend_income)
        _require_decimal("capital_gain", capital_gain)
        _require_decimal("portfolio_return", portfolio_return)
        _require_decimal("benchmark_return", benchmark_return)

        explicit = Decimal("0")
        implicit = Decimal("0")
        notional = Decimal("0")
        for i, leg in enumerate(legs):
            if not isinstance(leg, TradeLeg):
                raise RebalanceCostError(f"legs[{i}] 须为 TradeLeg: {type(leg).__name__}")
            if not leg.symbol:
                raise RebalanceCostError(f"legs[{i}] 标的为空")
            if not isinstance(leg.side, TradeSide):
                raise RebalanceCostError(f"legs[{i}] 非法方向: {leg.side!r}")
            qty = _require_decimal(f"legs[{i}].qty", leg.qty)
            price = _require_decimal(f"legs[{i}].price", leg.price)
            if qty <= 0:
                raise RebalanceCostError(f"legs[{i}].qty 须为正: {qty!r}")
            if price <= 0:
                raise RebalanceCostError(f"legs[{i}].price 须为正: {price!r}")
            for field_name in ("commission", "stamp_duty", "impact_cost", "spread_cost"):
                value = _require_decimal(f"legs[{i}].{field_name}", getattr(leg, field_name))
                if value < 0:
                    raise RebalanceCostError(f"legs[{i}].{field_name} 须非负: {value!r}")
            explicit += leg.commission + leg.stamp_duty
            implicit += leg.impact_cost + leg.spread_cost
            notional += qty * price

        tax = (
            max(dividend_income, Decimal("0")) * self._tax_table[_DIVIDEND_RATE_KEY]
            + max(capital_gain, Decimal("0")) * self._tax_table[_CAPITAL_GAIN_RATE_KEY]
        )
        opportunity = notional * (benchmark_return - portfolio_return)

        amounts = {
            CostCategory.EXPLICIT: explicit,
            CostCategory.IMPLICIT: implicit,
            CostCategory.TAX: tax,
            CostCategory.OPPORTUNITY: opportunity,
        }
        total_abs = sum(abs(v) for v in amounts.values())
        items = []
        for category, amount in amounts.items():
            ratio = abs(amount) / total_abs if total_abs > 0 else Decimal("0")
            items.append(CostBreakdownItem(category=category, amount=amount, ratio=ratio))
        items.sort(key=lambda item: (-item.ratio, item.category.value))

        total_cost = explicit + implicit + tax + opportunity
        cost_bps = total_cost / notional * _BPS_FACTOR
        alerted = cost_bps > self._alert_threshold_bps
        report = RebalanceCostReport(
            items=tuple(items),
            total_cost=total_cost,
            total_notional=notional,
            cost_bps=cost_bps,
            alerted=alerted,
            alert_threshold_bps=self._alert_threshold_bps,
            analyzed_at=self._clock(),
        )
        if alerted:
            _log.warning("调仓成本异常: cost_bps=%s > 阈值=%s", cost_bps, self._alert_threshold_bps)
            if self._alert_sink is not None:
                try:
                    self._alert_sink(report)
                except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                    _log.exception("alert_sink 告警失败")
        return report
