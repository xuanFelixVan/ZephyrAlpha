# [BLUEPRINT] MOD-EX-063 | docs/03_modules/_domain_execution_core/premarket_checker/blueprint.md
# [MODULE] zephyr.ex_core.premarket_checker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.risk_limits(MOD-INF-016); zephyr.data.quality_gate(MOD-L00-004); zephyr.shared.event_bus(MOD-INF-016)
# [CONSUMERS] boot_hooks(MOD-INF-035, _subscribe_eventbus_consumers 消费方注册)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 四道关顺序固定(限额→纪律→数据完整性→系统就绪); 全量评估不短路(ready=全部通过); 探针异常=该关不过(PROBE_ERROR,Fail-Closed); 限额基线日期须为当日(LIMITS_STALE); subscribe_eventbus幂等; 未接线收到请求发布ready=False(不臆造就绪); 报告frozen不可变
# [MODIFY-GUARD] docs/03_modules/_domain_execution_core/premarket_checker/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无(探针异常收敛为PROBE_ERROR阻断项,不外抛)
# [TESTS] tests/ex_core/test_premarket_checker.py
# [A_module] module_id=MOD-EX-063 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

# [ALGO_FLOW]
# I1: trading_date + clock
# I2: 四探针(risk_limits/compliance/data_quality/system_readiness)
# A1: 限额基线关(取值域+基线日期=当日)
# A2: 纪律预检关(违规清单须空)
# A3: 数据完整性关(QualityReport.passed)
# A4: 系统就绪关(子系统映射全真,未就绪点名)
# A5: 全量聚合(ready=全过; 探针异常=PROBE_ERROR阻断项)
# O1: PremarketReport(frozen)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# I2 --> A3
# I2 --> A4
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
"""
Premarket Checker — 盘前检查器 (MOD-EX-063, D-TRADING-05 MVP)

机构 OMS 与 vnpy RiskManager 标配的开盘前就绪闸。与 MOD-EX-024
pre_execution_checker（逐单执行前四级硬拦）分工：本模块管**当日开盘前**——
四道关全量核查（限额基线 / 纪律预检 / 数据完整性 / 系统就绪），任一不过即
当日不就绪（Fail-Closed，C-004 口径；探针异常 = 该关不过，绝不放行）。

boot_hooks 接线：经 `_subscribe_eventbus_consumers` 消费方注册模式接入
（`subscribe_eventbus()` 幂等）。订阅 `premarket.check.requested`，核查完成
发布 `premarket.check.completed`（透传请求载荷 + ready + failed_checks）。

SSoT: docs/03_modules/_domain_execution_core/premarket_checker/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Final

from zephyr.data.quality_gate import QualityReport
from zephyr.shared.event_bus import bus
from zephyr.trading.trading_contracts.risk.risk_limits import RiskLimits

_logger = logging.getLogger(__name__)

__all__: Final = [
    "PremarketChecker",
    "PremarketCheckItem",
    "PremarketReport",
    "register_checker",
    "subscribe_eventbus",
]

#: 事件主题（EventBusBackpressure 字符串主题）
TOPIC_CHECK_REQUESTED: Final = "premarket.check.requested"
TOPIC_CHECK_COMPLETED: Final = "premarket.check.completed"

#: 探针签名（生产接线：限额真源/纪律预检/数据质量门/健康聚合）
RiskLimitsProbe = Callable[[], RiskLimits]
ComplianceProbe = Callable[[], tuple[str, ...]]
DataQualityProbe = Callable[[], QualityReport]
SystemReadinessProbe = Callable[[], Mapping[str, bool]]


@dataclass(frozen=True)
class PremarketCheckItem:
    """单道关检查项（frozen）。"""

    check_id: str
    passed: bool
    reason_code: str
    message: str


@dataclass(frozen=True)
class PremarketReport:
    """盘前检查报告（frozen；ready=四道关全过）。"""

    trading_date: date
    ready: bool
    items: tuple[PremarketCheckItem, ...]
    evaluated_at: datetime


class PremarketChecker:
    """盘前检查器（四道关编排，全部 Fail-Closed）。

    Args:
        risk_limits_probe: 限额基线探针（生产接线限额真源；返回当日 RiskLimits）。
        compliance_probe: 纪律预检探针；返回违规清单（空=通过）。
        data_quality_probe: 数据完整性探针；返回 QualityReport（passed 须真）。
        system_readiness_probe: 系统就绪探针；返回子系统→就绪映射（全真=通过）。
        clock: 时钟协议（默认 datetime.now(UTC)）；测试注入固定时钟保判定确定性。
    """

    def __init__(
        self,
        risk_limits_probe: RiskLimitsProbe,
        compliance_probe: ComplianceProbe,
        data_quality_probe: DataQualityProbe,
        system_readiness_probe: SystemReadinessProbe,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._limits_probe = risk_limits_probe
        self._compliance_probe = compliance_probe
        self._quality_probe = data_quality_probe
        self._readiness_probe = system_readiness_probe
        self._clock = clock or (lambda: datetime.now(UTC))

    def run(self, trading_date: date | None = None) -> PremarketReport:
        """四道关全量核查（不短路；ready=全部通过）。"""
        evaluated_at = self._clock()
        day = trading_date or evaluated_at.date()
        items = (
            self._check_limits(day),
            self._check_compliance(),
            self._check_data_integrity(),
            self._check_system_readiness(),
        )
        report = PremarketReport(
            trading_date=day,
            ready=all(i.passed for i in items),
            items=items,
            evaluated_at=evaluated_at,
        )
        if not report.ready:
            _logger.warning(
                "PREMARKET_NOT_READY date=%s blocks=%s",
                day,
                [(i.check_id, i.reason_code) for i in items if not i.passed],
            )
        else:
            _logger.info("PREMARKET_READY date=%s", day)
        return report

    # ── 关 1: 限额基线（取值域 + 基线日期=当日）─────────────────────
    def _check_limits(self, day: date) -> PremarketCheckItem:
        check_id = "risk_limits"
        try:
            limits = self._limits_probe()
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("PREMARKET_LIMITS_PROBE_ERROR error=%s", exc)
            return PremarketCheckItem(check_id, False, "PROBE_ERROR", f"限额探针异常（Fail-Closed）: {exc}")
        invalid: list[str] = []
        if not 0.0 < limits.max_single_position <= 1.0:
            invalid.append(f"max_single_position={limits.max_single_position}∉(0,1]")
        if not 0.0 < limits.max_sector_concentration <= 1.0:
            invalid.append(f"max_sector_concentration={limits.max_sector_concentration}∉(0,1]")
        if limits.max_gross_leverage <= 0.0:
            invalid.append(f"max_gross_leverage={limits.max_gross_leverage}<=0")
        if invalid:
            return PremarketCheckItem(
                check_id, False, "LIMITS_INVALID", "限额取值域越界: " + "; ".join(invalid)
            )
        if limits.as_of_date.date() != day:
            return PremarketCheckItem(
                check_id,
                False,
                "LIMITS_STALE",
                f"限额基线过期: as_of_date={limits.as_of_date.date()} != trading_date={day}",
            )
        return PremarketCheckItem(check_id, True, "OK", "限额基线为当日且取值合法")

    # ── 关 2: 纪律预检（违规清单须空）───────────────────────────────
    def _check_compliance(self) -> PremarketCheckItem:
        check_id = "compliance"
        try:
            violations = tuple(self._compliance_probe())
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("PREMARKET_COMPLIANCE_PROBE_ERROR error=%s", exc)
            return PremarketCheckItem(check_id, False, "PROBE_ERROR", f"纪律预检探针异常（Fail-Closed）: {exc}")
        if violations:
            return PremarketCheckItem(
                check_id, False, "COMPLIANCE_VIOLATION", "纪律预检违规: " + "; ".join(violations)
            )
        return PremarketCheckItem(check_id, True, "OK", "纪律预检无违规")

    # ── 关 3: 数据完整性（QualityReport.passed）─────────────────────
    def _check_data_integrity(self) -> PremarketCheckItem:
        check_id = "data_integrity"
        try:
            report = self._quality_probe()
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("PREMARKET_QUALITY_PROBE_ERROR error=%s", exc)
            return PremarketCheckItem(check_id, False, "PROBE_ERROR", f"数据质量探针异常（Fail-Closed）: {exc}")
        if not report.passed:
            reason = report.failure_reason.value if report.failure_reason else "unknown"
            return PremarketCheckItem(
                check_id,
                False,
                "DATA_QUALITY_FAILED",
                f"数据完整性不达标: symbol={report.symbol} score={report.quality_score} reason={reason}",
            )
        return PremarketCheckItem(check_id, True, "OK", "数据完整性达标")

    # ── 关 4: 系统就绪（子系统映射全真，未就绪点名）──────────────────
    def _check_system_readiness(self) -> PremarketCheckItem:
        check_id = "system_readiness"
        try:
            readiness = dict(self._readiness_probe())
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("PREMARKET_READINESS_PROBE_ERROR error=%s", exc)
            return PremarketCheckItem(check_id, False, "PROBE_ERROR", f"系统就绪探针异常（Fail-Closed）: {exc}")
        not_ready = sorted(name for name, ok in readiness.items() if not ok)
        if not_ready:
            return PremarketCheckItem(
                check_id, False, "SUBSYSTEM_NOT_READY", "子系统未就绪: " + ", ".join(not_ready)
            )
        return PremarketCheckItem(check_id, True, "OK", "全部子系统就绪")


# ── boot_hooks 消费方接线（_subscribe_eventbus_consumers 模式）─────────

_registered_checker: PremarketChecker | None = None
_subscribed = False
_subscription_lock = threading.Lock()


def register_checker(checker: PremarketChecker | None) -> None:
    """注册/注销盘前检查器实例（运行时装配批注入生产探针）。"""
    global _registered_checker
    with _subscription_lock:
        _registered_checker = checker


def subscribe_eventbus() -> None:
    """订阅 premarket.check.requested（幂等；boot_hooks 统一调用）。"""
    global _subscribed
    with _subscription_lock:
        if _subscribed:
            _logger.debug("premarket_checker already subscribed, skipping (idempotent)")
            return
        _subscribed = True

    def _on_check_requested(event: object) -> None:
        payload = getattr(event, "payload", None) or {}
        try:
            raw_date = payload.get("trading_date")
            day = date.fromisoformat(raw_date) if isinstance(raw_date, str) else None
        except ValueError:
            day = None
        with _subscription_lock:
            checker = _registered_checker
        if checker is None:
            # Fail-Closed：未接线不臆造就绪
            _logger.error("PREMARKET_CHECKER_UNWIRED 收到盘前检查请求但未注册检查器实例")
            bus.emit(
                TOPIC_CHECK_COMPLETED,
                {**payload, "ready": False, "failed_checks": ["CHECKER_UNWIRED"]},
            )
            return
        report = checker.run(day)
        bus.emit(
            TOPIC_CHECK_COMPLETED,
            {
                **payload,
                "ready": report.ready,
                "failed_checks": [i.check_id for i in report.items if not i.passed],
            },
        )

    bus.subscribe(TOPIC_CHECK_REQUESTED, _on_check_requested)
    _logger.info("premarket_checker: subscribed %s", TOPIC_CHECK_REQUESTED)
