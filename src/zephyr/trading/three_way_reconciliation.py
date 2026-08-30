# [BLUEPRINT] MOD-TRADING-013 | docs/03_modules/_domain_trading/three_way_reconciliation/blueprint.md
# [MODULE] zephyr.trading.three_way_reconciliation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] 无（协议核心纯内存；clock/alert_sink 全注入；Decimal-only 金额数量）
# [CONSUMERS] 运行时装配批（盘后三向对账调度 / 告警路由接线 / 未匹配台账跟进工作台）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 异常词表闭合(price|quantity|fee|missing); 费用词表闭合(commission|stamp_tax|interest); 自动匹配按标的+数量/金额容差确定性配对; 利息流水仅计数不参与匹配; 台账跟进状态机 OPEN→INVESTIGATING→RESOLVED(OPEN→RESOLVED 直达); 异常ID=recon_id+序号确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_trading/three_way_reconciliation/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ThreeWayReconError(占位 ZA-TR-UNREGISTERED-THREE-WAY-RECON)——空流水号/空标的/负值/重复流水/重复引用/非法容差/重复 recon_id/未知台账项/非法跟进迁移时抛
# [TESTS] tests/trading/test_three_way_reconciliation.py
# [A_module] module_id=MOD-TRADING-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ThreeWayReconEngine — 三向对账引擎（MOD-TRADING-013）。

B13-04352（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-TRD-011，A3 D-TRADING-02）：
三向对账收口——交易/持仓/资金三方流水（券商资金流水：佣金/印花税/利息逐笔）
+ 异常分类（价格/数量/费用/缺失四类词表闭合）+ 自动匹配规则（标的 + 数量容差
+ 金额容差）+ 未匹配项台账与跟进状态机（OPEN→INVESTIGATING→RESOLVED，OPEN
→RESOLVED 直达；终态不可逆）。

查重分工（蓝图 §0）：settlement_reconciliation=系统 Fill vs 券商结算单逐笔
交易级对账（本件=交易/持仓/资金三方收口含费用逐笔与台账跟进，口径互补不重
复）；eod_processor=日终任务链（本件被调度消费，零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: qty_tolerance 参数
#   fields: 参数 qty_tolerance（无注解）
#   code: three_way_reconciliation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: amount_tolerance 参数
#   fields: 参数 amount_tolerance（无注解）
#   code: three_way_reconciliation.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: fee_tolerance 参数
#   fields: 参数 fee_tolerance（无注解）
#   code: three_way_reconciliation.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: three_way_reconciliation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ThreeWayReconEngine
#   name_en: ThreeWayReconEngine
#   intro: 三向对账引擎（交易/持仓/资金三方流水 + 未匹配台账跟进状态机）。
#   desc: 三向对账引擎（交易/持仓/资金三方流水 + 未匹配台账跟进状态机）。；公共方法（定义序）: reconcile, update_follow_up, ledger, anomaly；源码 L213-L479
#   inputs: qty_tolerance amount_tolerance fee_tolerance clock alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: ThreeWayReconEngine
#   downstream: 运行时装配批（盘后三向对账调度 / 告警路由接线 / 未匹配台账跟进工作台）
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
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "Anomaly",
    "AnomalyClass",
    "CashFlow",
    "FeeType",
    "FollowUpStatus",
    "PositionFlow",
    "ReconReport",
    "ThreeWayReconEngine",
    "ThreeWayReconError",
    "TradeFlow",
]


class ThreeWayReconError(Exception):
    """三向对账输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-TR-UNREGISTERED-THREE-WAY-RECON。
    """


class AnomalyClass(str, Enum):
    """异常分类（四类词表闭合）。"""

    PRICE = "price"
    QUANTITY = "quantity"
    FEE = "fee"
    MISSING = "missing"


class FeeType(str, Enum):
    """券商资金流水费用类型（逐笔三类词表闭合）。"""

    COMMISSION = "commission"
    STAMP_TAX = "stamp_tax"
    INTEREST = "interest"


class FollowUpStatus(str, Enum):
    """未匹配台账跟进状态机。"""

    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


#: 参与交易费用匹配的费用类型（利息为账户级，仅计数不参与逐笔匹配）
_FEE_MATCH_TYPES: Final[frozenset[FeeType]] = frozenset(
    {
        FeeType.COMMISSION,
        FeeType.STAMP_TAX,
    }
)

#: 台账跟进合法迁移（终态 RESOLVED 不可逆）
_ALLOWED_TRANSITIONS: Final[frozenset[tuple[FollowUpStatus, FollowUpStatus]]] = frozenset(
    {
        (FollowUpStatus.OPEN, FollowUpStatus.INVESTIGATING),
        (FollowUpStatus.OPEN, FollowUpStatus.RESOLVED),
        (FollowUpStatus.INVESTIGATING, FollowUpStatus.RESOLVED),
    }
)


@dataclass(frozen=True)
class TradeFlow:
    """系统侧交易流水（frozen；金额数量 Decimal-only）。"""

    flow_id: str
    symbol: str
    side: str  # "BUY" | "SELL"
    quantity: Decimal
    price: Decimal
    expected_fee: Decimal  # 系统预估费用（佣金+印花税）
    traded_at: datetime.datetime


@dataclass(frozen=True)
class PositionFlow:
    """券商侧持仓确认流水（对应一笔系统交易，frozen）。"""

    flow_id: str
    trade_ref: str
    symbol: str
    quantity: Decimal
    amount: Decimal  # 券商确认成交金额
    confirmed_at: datetime.datetime


@dataclass(frozen=True)
class CashFlow:
    """券商资金流水（佣金/印花税/利息逐笔，frozen）。"""

    flow_id: str
    fee_type: FeeType
    amount: Decimal
    trade_ref: str | None  # 利息等账户级费用为 None
    posted_at: datetime.datetime


@dataclass(frozen=True)
class Anomaly:
    """对账异常（未匹配台账条目，frozen；跟进经引擎状态机更新）。"""

    anomaly_id: str
    recon_id: str
    anomaly_class: AnomalyClass
    symbol: str
    detail: str
    expected: Decimal | None
    actual: Decimal | None
    status: FollowUpStatus
    raised_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ReconReport:
    """三向对账报告（frozen）。"""

    recon_id: str
    recon_date: datetime.date
    matched: bool
    matched_count: int
    anomalies: tuple[Anomaly, ...]
    totals: dict
    created_at: datetime.datetime


class ThreeWayReconEngine:
    """三向对账引擎（交易/持仓/资金三方流水 + 未匹配台账跟进状态机）。"""

    def __init__(
        self,
        *,
        qty_tolerance: Decimal = Decimal("0"),
        amount_tolerance: Decimal = Decimal("0.01"),
        fee_tolerance: Decimal = Decimal("0.01"),
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[ReconReport], None] | None = None,
    ) -> None:
        for label, tol in (
            ("qty_tolerance", qty_tolerance),
            ("amount_tolerance", amount_tolerance),
            ("fee_tolerance", fee_tolerance),
        ):
            if not isinstance(tol, Decimal) or tol < 0:
                raise ThreeWayReconError(f"{label} 非法: {tol!r}（须为非负 Decimal）")
        self._qty_tol = qty_tolerance
        self._amount_tol = amount_tolerance
        self._fee_tol = fee_tolerance
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._recon_ids: set[str] = set()
        self._ledger: dict[str, Anomaly] = {}

    # ── 输入校验（Fail-Closed） ───────────────────────────────────────────

    @staticmethod
    def _validate_trades(trades: tuple[TradeFlow, ...]) -> None:
        seen: set[str] = set()
        for t in trades:
            if not t.flow_id or not t.symbol:
                raise ThreeWayReconError("交易流水 flow_id/symbol 为空")
            if t.flow_id in seen:
                raise ThreeWayReconError(f"交易流水重复: {t.flow_id!r}")
            seen.add(t.flow_id)
            if t.quantity <= 0 or t.price <= 0 or t.expected_fee < 0:
                raise ThreeWayReconError(f"交易流水数值非法: {t.flow_id!r}")

    @staticmethod
    def _validate_positions(positions: tuple[PositionFlow, ...]) -> None:
        seen: set[str] = set()
        refs: set[str] = set()
        for p in positions:
            if not p.flow_id or not p.symbol or not p.trade_ref:
                raise ThreeWayReconError("持仓流水 flow_id/symbol/trade_ref 为空")
            if p.flow_id in seen:
                raise ThreeWayReconError(f"持仓流水重复: {p.flow_id!r}")
            if p.trade_ref in refs:
                raise ThreeWayReconError(f"持仓流水重复引用同一交易: {p.trade_ref!r}")
            seen.add(p.flow_id)
            refs.add(p.trade_ref)
            if p.quantity <= 0 or p.amount <= 0:
                raise ThreeWayReconError(f"持仓流水数值非法: {p.flow_id!r}")

    @staticmethod
    def _validate_cash(cash_flows: tuple[CashFlow, ...]) -> None:
        seen: set[str] = set()
        for c in cash_flows:
            if not c.flow_id:
                raise ThreeWayReconError("资金流水 flow_id 为空")
            if c.flow_id in seen:
                raise ThreeWayReconError(f"资金流水重复: {c.flow_id!r}")
            seen.add(c.flow_id)
            if not isinstance(c.fee_type, FeeType):
                raise ThreeWayReconError(f"资金流水费用类型非法: {c.flow_id!r} {c.fee_type!r}")
            if c.amount < 0:
                raise ThreeWayReconError(f"资金流水金额非法: {c.flow_id!r}")
            if c.trade_ref is not None and not c.trade_ref:
                raise ThreeWayReconError(f"资金流水 trade_ref 为空串: {c.flow_id!r}")

    # ── 对账 ─────────────────────────────────────────────────────────────

    def reconcile(
        self,
        *,
        recon_id: str,
        recon_date: datetime.date,
        trades: Iterable[TradeFlow],
        positions: Iterable[PositionFlow],
        cash_flows: Iterable[CashFlow],
    ) -> ReconReport:
        """三向对账：自动匹配（标的+数量+金额容差）→ 异常分类 → 台账登记。"""
        if not recon_id:
            raise ThreeWayReconError("recon_id 为空")
        if recon_id in self._recon_ids:
            raise ThreeWayReconError(f"recon_id 重复: {recon_id!r}")
        trades = tuple(trades)
        positions = tuple(positions)
        cash_flows = tuple(cash_flows)
        self._validate_trades(trades)
        self._validate_positions(positions)
        self._validate_cash(cash_flows)

        now = self._clock()
        anomalies: list[Anomaly] = []
        seq = 0

        def new_anomaly(
            cls: AnomalyClass,
            symbol: str,
            detail: str,
            expected: Decimal | None,
            actual: Decimal | None,
        ) -> None:
            nonlocal seq
            seq += 1
            anomalies.append(
                Anomaly(
                    anomaly_id=f"{recon_id}-A{seq:03d}",
                    recon_id=recon_id,
                    anomaly_class=cls,
                    symbol=symbol,
                    detail=detail,
                    expected=expected,
                    actual=actual,
                    status=FollowUpStatus.OPEN,
                    raised_at=now,
                    updated_at=now,
                )
            )

        pos_by_ref = {p.trade_ref: p for p in sorted(positions, key=lambda x: x.flow_id)}
        # 费用按 trade_ref 归集（佣金+印花税；利息为账户级仅计数不参与匹配）
        fee_by_ref: dict[str, Decimal] = {}
        for c in sorted(cash_flows, key=lambda x: x.flow_id):
            if c.fee_type in _FEE_MATCH_TYPES and c.trade_ref is not None:
                fee_by_ref[c.trade_ref] = fee_by_ref.get(c.trade_ref, Decimal("0")) + c.amount

        matched_count = 0
        trade_refs: set[str] = set()
        for t in sorted(trades, key=lambda x: x.flow_id):
            trade_refs.add(t.flow_id)
            p = pos_by_ref.get(t.flow_id)
            if p is None:
                new_anomaly(
                    AnomalyClass.MISSING,
                    t.symbol,
                    f"券商持仓确认缺失: 交易 {t.flow_id}",
                    t.quantity,
                    None,
                )
                continue
            if p.symbol != t.symbol:
                new_anomaly(
                    AnomalyClass.MISSING,
                    t.symbol,
                    f"标的错位: 交易 {t.flow_id} 标的 {t.symbol} vs 券商 {p.symbol}",
                    t.quantity,
                    p.quantity,
                )
                continue
            matched = True
            if abs(t.quantity - p.quantity) > self._qty_tol:
                new_anomaly(
                    AnomalyClass.QUANTITY,
                    t.symbol,
                    f"数量不一致: 系统 {t.quantity} vs 券商 {p.quantity}",
                    t.quantity,
                    p.quantity,
                )
                matched = False
            expected_amount = t.price * t.quantity
            if abs(expected_amount - p.amount) > self._amount_tol:
                new_anomaly(
                    AnomalyClass.PRICE,
                    t.symbol,
                    f"金额不一致: 系统 {expected_amount} vs 券商 {p.amount}",
                    expected_amount,
                    p.amount,
                )
                matched = False
            actual_fee = fee_by_ref.get(t.flow_id, Decimal("0"))
            if abs(t.expected_fee - actual_fee) > self._fee_tol:
                new_anomaly(
                    AnomalyClass.FEE,
                    t.symbol,
                    f"费用不一致: 系统预估 {t.expected_fee} vs 券商实际 {actual_fee}",
                    t.expected_fee,
                    actual_fee,
                )
                matched = False
            if matched:
                matched_count += 1

        for p in sorted(positions, key=lambda x: x.flow_id):
            if p.trade_ref not in trade_refs:
                new_anomaly(
                    AnomalyClass.MISSING,
                    p.symbol,
                    f"系统交易缺失: 券商持仓 {p.flow_id} 引用 {p.trade_ref}",
                    None,
                    p.quantity,
                )
        for c in sorted(cash_flows, key=lambda x: x.flow_id):
            if c.trade_ref is not None and c.trade_ref not in trade_refs:
                new_anomaly(
                    AnomalyClass.MISSING,
                    "",
                    f"资金流水引用未知交易: {c.flow_id} -> {c.trade_ref}",
                    None,
                    c.amount,
                )

        for a in anomalies:
            self._ledger[a.anomaly_id] = a
        self._recon_ids.add(recon_id)
        report = ReconReport(
            recon_id=recon_id,
            recon_date=recon_date,
            matched=not anomalies,
            matched_count=matched_count,
            anomalies=tuple(anomalies),
            totals={
                "trades": len(trades),
                "positions": len(positions),
                "cash_flows": len(cash_flows),
                "matched": matched_count,
                "anomalies": len(anomalies),
            },
            created_at=now,
        )
        if anomalies and self._alert_sink is not None:
            try:
                self._alert_sink(report)
            except Exception:  # noqa: BLE001 — 告警不阻断对账（留痕已入台账）
                _log.exception("alert_sink 告警失败")
        _log.info(
            "三向对账完成: %s matched=%d anomalies=%d",
            recon_id,
            matched_count,
            len(anomalies),
        )
        return report

    # ── 未匹配台账（跟进状态机） ───────────────────────────────────────────

    def update_follow_up(self, anomaly_id: str, new_status: FollowUpStatus, operator: str) -> Anomaly:
        """台账跟进：OPEN→INVESTIGATING→RESOLVED（OPEN→RESOLVED 直达；终态不可逆）。"""
        if not operator:
            raise ThreeWayReconError("操作人为空")
        if not isinstance(new_status, FollowUpStatus):
            raise ThreeWayReconError(f"非法跟进状态: {new_status!r}")
        anomaly = self._ledger.get(anomaly_id)
        if anomaly is None:
            raise ThreeWayReconError(f"未知台账异常: {anomaly_id!r}")
        if (anomaly.status, new_status) not in _ALLOWED_TRANSITIONS:
            raise ThreeWayReconError(f"非法跟进迁移: {anomaly_id!r} {anomaly.status.value} -> {new_status.value}")
        updated = replace(anomaly, status=new_status, updated_at=self._clock())
        self._ledger[anomaly_id] = updated
        _log.info("台账跟进: %s -> %s (operator=%s)", anomaly_id, new_status.value, operator)
        return updated

    def ledger(self, status: FollowUpStatus | None = None) -> list[Anomaly]:
        """未匹配台账查询（按 anomaly_id 确定性排序；可按状态过滤）。"""
        out = [a for a in self._ledger.values() if status is None or a.status is status]
        out.sort(key=lambda a: a.anomaly_id)
        return out

    def anomaly(self, anomaly_id: str) -> Anomaly:
        """单台账条目查询（未知 → Fail-Closed）。"""
        entry = self._ledger.get(anomaly_id)
        if entry is None:
            raise ThreeWayReconError(f"未知台账异常: {anomaly_id!r}")
        return entry
