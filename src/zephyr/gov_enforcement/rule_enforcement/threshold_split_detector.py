# [BLUEPRINT] MOD-GOV-050 | docs/03_modules/_domain_gov_enforcement/threshold_split_detector/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.threshold_split_detector
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.frontend.interface_base(MOD-L08-001); zephyr.shared.foundation.errors(MOD-INF-016)
# [CONSUMERS] 交易意图登记入口(运行时装配批串接下单链路); default_approval_gateway(MOD-L08-001, 提请审批载体)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 意图先登记后放行; 同标的同方向30分钟+当日两档滑动窗累计; 窗内≥2笔且每笔均低于阈值且累计≥阈值×alert_ratio→判拆分; 判拆分即阻断该(标的,方向)后续单且阻断单不计入窗口; 提请审批幂等(同标的同方向同日一次); 审批/告警/审计端口异常隔离但阻断必生效(Fail-Closed); 时钟可注入; 结果frozen不可变
# [MODIFY-GUARD] docs/03_modules/_domain_gov_enforcement/threshold_split_detector/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidOrderIntentError; InvalidThresholdSplitConfigError
# [TESTS] tests/governance/rule_enforcement/test_threshold_split_detector.py
# [A_module] module_id=MOD-GOV-050 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

# [ALGO_FLOW]
# I1: OrderIntent(intent_id/strategy_id/symbol/side/quantity/amount)
# I2: ThresholdSplitConfig(双阈值+alert_ratio+window_minutes+symbol覆盖) + 注入端口(gateway/alert/audit/clock)
# A1: 意图校验(非法→InvalidOrderIntentError)
# A2: 阻断集命中→BLOCKED(不计入窗口)
# A3: 登记入窗+惰性清理跨日
# A4: 两档窗累计(30分钟滑动窗/当日窗)与阈值比对(≥2笔+每笔低于阈值+累计≥阈值×ratio)
# A5: 判拆分→阻断集+提请审批(幂等)+审计+CRITICAL告警(端口异常隔离,阻断必生效)
# O1: SplitDetectionResult(frozen)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A4
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""
Threshold Split Detector — 阈值拆分检测器 (MOD-GOV-050, CAND-GOVENFOR-001 MVP)

反化整为零 = AML 结构化交易（smurfing）检测的滑动窗口累计思路。
AI 拆分交易绕过审批属 AI 自治熔断硬缺口：审批网关（MOD-L08-001）是单笔视角，
可被化整为零击穿。本模块：交易意图先登记；30 分钟滑动窗 + 当日窗两档对
同标的同方向累计数量/金额；窗内 ≥2 笔且每笔均低于审批阈值但累计 ≥ 阈值 80%
即判拆分——阻断该（标的，方向）后续单 + 提请人工审批（ApprovalRequest 经注入
网关 submit）+ 告警落审计哈希链（audit_sink 生产接线 AiAuditLogger）。

Fail-Closed 铁律：审批/告警/审计端口异常不阻断检测主流程（隔离记录），
但阻断集必先生效（宁可误阻断，不可漏拆分）。

SSoT: docs/03_modules/_domain_gov_enforcement/threshold_split_detector/blueprint.md
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: threshold_split_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: approval_gateway 参数
#   fields: 参数 approval_gateway（无注解）
#   code: threshold_split_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: threshold_split_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: threshold_split_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ThresholdSplitDetector
#   name_en: ThresholdSplitDetector
#   intro: 阈值拆分检测器（登记即检测，Fail-Closed）。
#   desc: 阈值拆分检测器（登记即检测，Fail-Closed）。 Args: config: 双阈值 + alert_ratio + window_minutes + symbol 覆盖。…；公共方法（定义序）: registe…
#   inputs: config approval_gateway alert_sink audit_sink clock
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: ThresholdSplitDetector
#   downstream: 交易意图登记入口(运行时装配批串接下单链路); default_approval_gateway(MOD-L08-001, 提请审批载体)
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

import logging
import threading
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.frontend.interface_base import ApprovalRequest
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "InvalidOrderIntentError",
    "InvalidThresholdSplitConfigError",
    "OrderIntent",
    "OrderSide",
    "SplitDetectionResult",
    "SplitVerdict",
    "ThresholdPair",
    "ThresholdSplitConfig",
    "ThresholdSplitDetector",
]


class InvalidOrderIntentError(ZephyrBaseError):
    """交易意图非法（空标识/空标的/数量非正/金额为负）。"""


class InvalidThresholdSplitConfigError(ZephyrBaseError):
    """检测器配置非法（阈值非正/比率越界/窗口非正）。"""


class OrderSide(str, Enum):
    """委托方向。"""

    BUY = "buy"
    SELL = "sell"


class SplitVerdict(str, Enum):
    """拆分判定结论。"""

    CLEAN = "CLEAN"
    SPLIT_SUSPECTED = "SPLIT_SUSPECTED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class OrderIntent:
    """交易意图（frozen；登记即检测）。"""

    intent_id: str
    strategy_id: str
    symbol: str
    side: OrderSide
    quantity: int
    amount: Decimal


@dataclass(frozen=True)
class ThresholdPair:
    """审批阈值对（数量/金额）。"""

    quantity: int
    amount: Decimal


@dataclass(frozen=True)
class ThresholdSplitConfig:
    """检测器配置（frozen；symbol_overrides 覆盖特定标的阈值）。"""

    default_thresholds: ThresholdPair
    alert_ratio: float = 0.8
    window_minutes: int = 30
    symbol_overrides: Mapping[str, ThresholdPair] = field(default_factory=dict)


@dataclass(frozen=True)
class SplitDetectionResult:
    """拆分检测结果（frozen）。"""

    verdict: SplitVerdict
    symbol: str
    side: OrderSide
    intents_in_window: int
    qty_30m: int
    amount_30m: Decimal
    qty_day: int
    amount_day: Decimal
    threshold_quantity: int
    threshold_amount: Decimal
    trigger_window: str | None
    escalation_request_id: str | None
    reason: str
    evaluated_at: datetime


#: 端口签名（生产接线：default_approval_gateway / 告警通道 / AiAuditLogger 哈希链）
AlertSink = Callable[[str, dict], None]
AuditSink = Callable[[str, dict], None]


class ThresholdSplitDetector:
    """阈值拆分检测器（登记即检测，Fail-Closed）。

    Args:
        config: 双阈值 + alert_ratio + window_minutes + symbol 覆盖。
        approval_gateway: 审批网关（submit(ApprovalRequest)->str）；None=未接线
            （判拆分仍阻断+告警审计，escalation_request_id 留空）。
        alert_sink: 告警端口（level, payload）；None=仅日志。
        audit_sink: 审计端口（event, payload）；None=仅日志。
        clock: 时钟协议（默认 datetime.now(UTC)）；测试注入固定时钟保判定确定性。
    """

    def __init__(
        self,
        config: ThresholdSplitConfig,
        approval_gateway: object | None = None,
        alert_sink: AlertSink | None = None,
        audit_sink: AuditSink | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validate_config(config)
        self._config = config
        self._gateway = approval_gateway
        self._alert = alert_sink
        self._audit = audit_sink
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = threading.Lock()
        self._intents: dict[tuple[str, OrderSide], deque[tuple[datetime, OrderIntent]]] = {}
        self._blocked: set[tuple[str, OrderSide]] = set()
        self._escalated_ids: set[str] = set()

    @staticmethod
    def _validate_config(config: ThresholdSplitConfig) -> None:
        pairs = [config.default_thresholds, *config.symbol_overrides.values()]
        for pair in pairs:
            if pair.quantity <= 0 or pair.amount <= 0:
                raise InvalidThresholdSplitConfigError(
                    "审批阈值必须为正",
                    details={"quantity": pair.quantity, "amount": str(pair.amount)},
                )
        if not 0.0 < config.alert_ratio <= 1.0:
            raise InvalidThresholdSplitConfigError(
                "alert_ratio 必须落在 (0,1]",
                details={"alert_ratio": config.alert_ratio},
            )
        if config.window_minutes <= 0:
            raise InvalidThresholdSplitConfigError(
                "window_minutes 必须为正",
                details={"window_minutes": config.window_minutes},
            )

    def register_intent(self, intent: OrderIntent) -> SplitDetectionResult:
        """登记交易意图并检测拆分。

        Raises:
            InvalidOrderIntentError: 意图字段非法。
        """
        self._validate_intent(intent)
        now = self._clock()
        key = (intent.symbol, intent.side)
        thresholds = self._config.symbol_overrides.get(intent.symbol, self._config.default_thresholds)

        with self._lock:
            if key in self._blocked:
                _logger.warning(
                    "SPLIT_ORDER_BLOCKED symbol=%s side=%s intent=%s（拆分判定后阻断）",
                    intent.symbol,
                    intent.side.value,
                    intent.intent_id,
                )
                # 阻断单不登记入窗；结果仍反映既有窗口累计（证明未计入）
                dq = self._intents.get(key, deque())
                self._prune_cross_day(dq, now)
                window_delta = timedelta(minutes=self._config.window_minutes)
                w30 = [(ts, i) for ts, i in dq if now - ts <= window_delta]
                return self._result(
                    SplitVerdict.BLOCKED,
                    intent,
                    thresholds,
                    now,
                    None,
                    None,
                    "该（标的,方向）已因拆分判定被阻断，意图未登记入窗",
                    qty_30m=sum(i.quantity for _, i in w30),
                    amt_30m=sum((i.amount for _, i in w30), Decimal("0")),
                    qty_day=sum(i.quantity for _, i in dq),
                    amt_day=sum((i.amount for _, i in dq), Decimal("0")),
                    n_items=len(dq),
                )

            dq = self._intents.setdefault(key, deque())
            dq.append((now, intent))
            self._prune_cross_day(dq, now)

            window_delta = timedelta(minutes=self._config.window_minutes)
            w30 = [(ts, i) for ts, i in dq if now - ts <= window_delta]
            day = list(dq)  # 已惰性清理跨日

            qty_30m = sum(i.quantity for _, i in w30)
            amt_30m = sum((i.amount for _, i in w30), Decimal("0"))
            qty_day = sum(i.quantity for _, i in day)
            amt_day = sum((i.amount for _, i in day), Decimal("0"))

            trigger = self._detect(
                w30_qty=qty_30m,
                w30_amt=amt_30m,
                w30_items=w30,
                day_qty=qty_day,
                day_amt=amt_day,
                day_items=day,
                thresholds=thresholds,
            )

            if trigger is None:
                return self._result(
                    SplitVerdict.CLEAN,
                    intent,
                    thresholds,
                    now,
                    None,
                    None,
                    "窗内未达拆分判据",
                    qty_30m=qty_30m,
                    amt_30m=amt_30m,
                    qty_day=qty_day,
                    amt_day=amt_day,
                    n_items=max(len(w30), len(day)),
                )

            # ── 判拆分：阻断必先生效（Fail-Closed），再提请审批/审计/告警 ──
            self._blocked.add(key)
            escalation_id = self._escalate(intent, thresholds, now, trigger, qty_day=qty_day, amt_day=amt_day)
            payload = {
                "symbol": intent.symbol,
                "side": intent.side.value,
                "strategy_id": intent.strategy_id,
                "trigger_window": trigger,
                "qty_day": qty_day,
                "amount_day": str(amt_day),
                "threshold_quantity": thresholds.quantity,
                "threshold_amount": str(thresholds.amount),
                "alert_ratio": self._config.alert_ratio,
                "escalation_request_id": escalation_id,
            }
            self._emit_audit("SPLIT_SUSPECTED", payload)
            self._emit_alert("CRITICAL", {"event": "threshold_split_suspected", **payload})
            _logger.critical(
                "THRESHOLD_SPLIT_SUSPECTED symbol=%s side=%s window=%s qty_day=%d amt_day=%s",
                intent.symbol,
                intent.side.value,
                trigger,
                qty_day,
                amt_day,
            )
            return self._result(
                SplitVerdict.SPLIT_SUSPECTED,
                intent,
                thresholds,
                now,
                trigger,
                escalation_id,
                f"窗内多笔低于阈值但累计≥阈值{self._config.alert_ratio:.0%}（{trigger}档），判拆分",
                qty_30m=qty_30m,
                amt_30m=amt_30m,
                qty_day=qty_day,
                amt_day=amt_day,
                n_items=max(len(w30), len(day)),
            )

    def is_blocked(self, symbol: str, side: OrderSide) -> bool:
        """（标的,方向）是否已被阻断。"""
        with self._lock:
            return (symbol, side) in self._blocked

    def blocked_keys(self) -> frozenset[tuple[str, OrderSide]]:
        """阻断集快照（frozenset 拷贝）。"""
        with self._lock:
            return frozenset(self._blocked)

    # ── 内部 ─────────────────────────────────────────────────────────

    @staticmethod
    def _validate_intent(intent: OrderIntent) -> None:
        problems: list[str] = []
        if not intent.intent_id.strip():
            problems.append("intent_id 为空")
        if not intent.strategy_id.strip():
            problems.append("strategy_id 为空")
        if not intent.symbol.strip():
            problems.append("symbol 为空")
        if intent.quantity <= 0:
            problems.append(f"quantity={intent.quantity} 非正")
        if intent.amount < 0:
            problems.append(f"amount={intent.amount} 为负")
        if problems:
            raise InvalidOrderIntentError(
                "交易意图非法: " + "; ".join(problems),
                details={"intent_id": intent.intent_id, "symbol": intent.symbol},
            )

    @staticmethod
    def _prune_cross_day(dq: deque[tuple[datetime, OrderIntent]], now: datetime) -> None:
        """惰性清理跨日数据（当日窗=清理后全量）。"""
        while dq and dq[0][0].date() != now.date():
            dq.popleft()

    def _detect(
        self,
        *,
        w30_qty: int,
        w30_amt: Decimal,
        w30_items: list[tuple[datetime, OrderIntent]],
        day_qty: int,
        day_amt: Decimal,
        day_items: list[tuple[datetime, OrderIntent]],
        thresholds: ThresholdPair,
    ) -> str | None:
        """两档窗判定：≥2 笔 + 每笔低于阈值 + 累计 ≥ 阈值×ratio。返回触发档（30m/day）。"""
        ratio = self._config.alert_ratio
        qty_line = thresholds.quantity * ratio
        amt_line = thresholds.amount * Decimal(str(ratio))

        def _all_singles_below(items: list[tuple[datetime, OrderIntent]]) -> bool:
            return all(i.quantity < thresholds.quantity and i.amount < thresholds.amount for _, i in items)

        if len(w30_items) >= 2 and _all_singles_below(w30_items) and (w30_qty >= qty_line or w30_amt >= amt_line):
            return "30m"
        if len(day_items) >= 2 and _all_singles_below(day_items) and (day_qty >= qty_line or day_amt >= amt_line):
            return "day"
        return None

    def _escalate(
        self,
        intent: OrderIntent,
        thresholds: ThresholdPair,
        now: datetime,
        trigger: str,
        *,
        qty_day: int,
        amt_day: Decimal,
    ) -> str | None:
        """提请人工审批（幂等：同标的同方向同日一次；网关异常隔离留空）。"""
        request_id = f"SPLIT-{intent.symbol}-{intent.side.value}-{now.date().isoformat()}"
        if request_id in self._escalated_ids:
            return request_id
        if self._gateway is None:
            _logger.error("SPLIT_ESCALATION_UNWIRED 未接线审批网关 request=%s", request_id)
            return None
        try:
            submitted = self._gateway.submit(  # type: ignore[attr-defined]
                ApprovalRequest(
                    request_id=request_id,
                    action="threshold_split_escalation",
                    reason=(
                        f"疑似拆分交易：{intent.symbol} {intent.side.value} "
                        f"{trigger}档累计数量{qty_day}/金额{amt_day} ≥ "
                        f"阈值({thresholds.quantity}/{thresholds.amount})×{self._config.alert_ratio:.0%}，"
                        "窗内单笔均低于阈值"
                    ),
                    requester="threshold_split_detector",
                    context={
                        "symbol": intent.symbol,
                        "side": intent.side.value,
                        "strategy_id": intent.strategy_id,
                        "trigger_window": trigger,
                        "qty_day": qty_day,
                        "amount_day": str(amt_day),
                    },
                    created_at=now,
                )
            )
        except Exception as exc:  # noqa: BLE001 — 端口异常隔离，阻断先生效
            _logger.error("SPLIT_ESCALATION_ERROR request=%s error=%s", request_id, exc)
            return None
        self._escalated_ids.add(request_id)
        _logger.info("SPLIT_ESCALATED request=%s", submitted)
        return request_id

    def _emit_alert(self, level: str, payload: dict) -> None:
        if self._alert is None:
            return
        try:
            self._alert(level, payload)
        except Exception as exc:  # noqa: BLE001 — 端口异常隔离
            _logger.error("ALERT_SINK_ERROR level=%s error=%s", level, exc)

    def _emit_audit(self, event: str, payload: dict) -> None:
        if self._audit is None:
            return
        try:
            self._audit(event, payload)
        except Exception as exc:  # noqa: BLE001 — 端口异常隔离
            _logger.error("AUDIT_SINK_ERROR event=%s error=%s", event, exc)

    @staticmethod
    def _result(
        verdict: SplitVerdict,
        intent: OrderIntent,
        thresholds: ThresholdPair,
        now: datetime,
        trigger: str | None,
        escalation_id: str | None,
        reason: str,
        *,
        qty_30m: int = 0,
        amt_30m: Decimal = Decimal("0"),
        qty_day: int = 0,
        amt_day: Decimal = Decimal("0"),
        n_items: int = 0,
    ) -> SplitDetectionResult:
        return SplitDetectionResult(
            verdict=verdict,
            symbol=intent.symbol,
            side=intent.side,
            intents_in_window=n_items,
            qty_30m=qty_30m,
            amount_30m=amt_30m,
            qty_day=qty_day,
            amount_day=amt_day,
            threshold_quantity=thresholds.quantity,
            threshold_amount=thresholds.amount,
            trigger_window=trigger,
            escalation_request_id=escalation_id,
            reason=reason,
            evaluated_at=now,
        )
