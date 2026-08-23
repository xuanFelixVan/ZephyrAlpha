# [BLUEPRINT] MOD-EX-024 | docs/03_modules/MOD-EX-024/
# [MODULE] zephyr.ex_core.pre_execution_checker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline; zephyr.risk.core.risk_veto_engine; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-L06-001(TradingSession._validate_and_submit 前置硬拦) ; MOD-EX-007(Execution Risk Gate)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四级检查顺序固定(熔断→时段→快照→否决); 熔断激活短路不建快照; 各环节Fail-Closed(探针异常按熔断/非交易时段处理,快照失败拒单,C-004默认拒绝); 风险判定核心委托MOD-RK-24纯函数(本模块只编排不重造); 报告frozen不可变
# [MODIFY-GUARD] docs/03_modules/MOD-EX-024/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RiskDataPipelineError(快照装配上抛转SNAPSHOT_UNAVAILABLE阻断块,不外抛)
# [TESTS] tests/ex_core/test_pre_execution_checker.py
# [A_module] module_id=MOD-EX-024 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Pre-Execution Checker — 执行前检查器 (MOD-EX-024)

下单前统一四级硬检查（编排层，对接 MOD-RK-25 快照 + MOD-RK-24 否决引擎 + 既有风控件）：
  1. Kill Switch 闸门  — 熔断激活拒绝全部新订单（短路，不建快照；
     探针异常按已熔断处理，Fail-Closed；生产接线: DefaultRiskValidator.kill_switch_active）
  2. 交易时段闸门      — L-003 非交易时段禁下单（默认 A 股窗口 09:30-11:30 / 13:00-15:00
     Asia/Shanghai + 交易日判定；探针异常按非交易时段处理，Fail-Closed）
  3. 风控快照装配      — MOD-RK-25 RiskDataPipeline；失败 → SNAPSHOT_UNAVAILABLE 拒单
  4. 风险否决评估      — MOD-RK-24 RiskVetoEngine（判定核心为纯函数，本模块只编排）

降级铁律（C-004 默认拒绝）：任何检查环节不可用 → 拒绝新订单，不放行。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, time
from typing import Final
from zoneinfo import ZoneInfo

from zephyr.risk.core.risk_data_pipeline import RiskDataPipelineError, RiskSnapshot
from zephyr.risk.core.risk_veto_engine import (
    OrderRiskRequest,
    RiskVetoEngine,
    VetoDecision,
)

_logger = logging.getLogger(__name__)

__all__: Final = [
    "PreExecutionBlock",
    "PreExecutionChecker",
    "PreExecutionReport",
    "is_ashare_trading_window",
]

_SHANGHAI_TZ: Final = ZoneInfo("Asia/Shanghai")

#: A 股连续竞价窗口（北京时刻；集合竞价 09:15-09:25 不接单——9:25-9:30 深交所可报
#: 但本系统策略根频率日频+3秒Tick，统一从 09:30 连续竞价起放行，L-003 口径）
_ASHARE_SESSION_WINDOWS: Final = (
    (time(9, 30), time(11, 30)),
    (time(13, 0), time(15, 0)),
)

#: 熔断探针签名（生产接线: DefaultRiskValidator.kill_switch_active）
KillSwitchProbe = Callable[[], bool]
#: 时段探针签名（生产接线: 交易日历+会话窗口）
SessionWindowProbe = Callable[[datetime], bool]
#: 快照构建器签名（生产接线: RiskDataPipeline.build_snapshot）
SnapshotBuilder = Callable[[], RiskSnapshot]


def is_ashare_trading_window(now: datetime) -> bool:
    """A 股交易时段判定（L-003：非交易时段订单为废单，执行层内置校验）。

    naive datetime 按 Asia/Shanghai 口径解释；aware datetime 先换算北京时刻。
    交易日判定优先走既有真源 zephyr.data.trading_calendar.is_trading_day；
    真源不可用（如节假日库未初始化）降级为周一至周五判定（周六/周日恒闭市）。
    """
    if now.tzinfo is None:
        local_now = now.replace(tzinfo=_SHANGHAI_TZ)
    else:
        local_now = now.astimezone(_SHANGHAI_TZ)

    try:
        from zephyr.data.trading_calendar import is_trading_day

        if not is_trading_day(local_now.date()):
            return False
    except Exception:  # noqa: BLE001 — 真源不可用降级为周日历判定
        if local_now.weekday() >= 5:
            return False

    now_time = local_now.time()
    return any(start <= now_time <= end for start, end in _ASHARE_SESSION_WINDOWS)


@dataclass(frozen=True)
class PreExecutionBlock:
    """单条执行前阻断（结构化理由）。"""

    check_id: str
    reason_code: str
    message: str


@dataclass(frozen=True)
class PreExecutionReport:
    """执行前检查报告（frozen；blocks 为空即放行）。"""

    allowed: bool
    blocks: tuple[PreExecutionBlock, ...]
    veto_decision: VetoDecision | None
    snapshot_id: str | None
    request_id: str
    evaluated_at: datetime


class PreExecutionChecker:
    """执行前检查器（四级闸门编排，全部 Fail-Closed）。"""

    def __init__(
        self,
        snapshot_builder: SnapshotBuilder,
        kill_switch_probe: KillSwitchProbe | None = None,
        session_window_probe: SessionWindowProbe | None = None,
        veto_engine: RiskVetoEngine | None = None,
    ) -> None:
        """
        Args:
            snapshot_builder: 风控快照构建器（生产接线 RiskDataPipeline.build_snapshot）。
            kill_switch_probe: 熔断状态探针；None=未接线（不臆造熔断态，记 DEBUG 留痕）。
            session_window_probe: 交易时段探针；None=用默认 A 股窗口实现。
            veto_engine: 否决引擎；None=内置默认硬规则集。
        """
        self._snapshot_builder = snapshot_builder
        self._kill_switch_probe = kill_switch_probe
        self._session_window_probe = session_window_probe or is_ashare_trading_window
        self._veto_engine = veto_engine or RiskVetoEngine()

    def check(
        self, request: OrderRiskRequest, *, now: datetime | None = None
    ) -> PreExecutionReport:
        """执行前四级检查。blocks 为空 → allowed=True。"""
        evaluated_at = now or datetime.now(tz=UTC)
        blocks: list[PreExecutionBlock] = []

        # ── 闸门 1: Kill Switch（短路）──────────────────────────────
        if self._kill_switch_probe is None:
            _logger.debug("KILL_SWITCH_PROBE_UNWIRED 未接线熔断探针，按未激活继续")
        else:
            try:
                kill_switch_active = bool(self._kill_switch_probe())
            except Exception as exc:  # noqa: BLE001 — Fail-Closed
                _logger.critical("KILL_SWITCH_PROBE_ERROR fail-closed error=%s", exc)
                blocks.append(
                    PreExecutionBlock(
                        check_id="kill_switch_gate",
                        reason_code="KILL_SWITCH_PROBE_ERROR",
                        message="熔断探针异常，按已熔断处理（Fail-Closed 拒单）",
                    )
                )
                return self._report(request, blocks, None, None, evaluated_at)
            if kill_switch_active:
                blocks.append(
                    PreExecutionBlock(
                        check_id="kill_switch_gate",
                        reason_code="KILL_SWITCH_ACTIVE",
                        message="Kill Switch 已激活，拒绝全部新订单",
                    )
                )
                return self._report(request, blocks, None, None, evaluated_at)

        # ── 闸门 2: 交易时段（L-003）────────────────────────────────
        try:
            in_window = bool(self._session_window_probe(evaluated_at))
        except Exception as exc:  # noqa: BLE001 — Fail-Closed
            _logger.error("SESSION_WINDOW_PROBE_ERROR fail-closed error=%s", exc)
            blocks.append(
                PreExecutionBlock(
                    check_id="session_window_gate",
                    reason_code="SESSION_WINDOW_PROBE_ERROR",
                    message="交易时段探针异常，按非交易时段处理（Fail-Closed 拒单）",
                )
            )
            return self._report(request, blocks, None, None, evaluated_at)
        if not in_window:
            blocks.append(
                PreExecutionBlock(
                    check_id="session_window_gate",
                    reason_code="OUTSIDE_TRADING_WINDOW",
                    message="非交易时段禁止下单（L-003：非交易时段订单为废单）",
                )
            )
            return self._report(request, blocks, None, None, evaluated_at)

        # ── 闸门 3: 风控快照装配 ────────────────────────────────────
        try:
            snapshot = self._snapshot_builder()
        except RiskDataPipelineError as exc:
            _logger.error("PRE_EXEC_SNAPSHOT_UNAVAILABLE error=%s", exc)
            blocks.append(
                PreExecutionBlock(
                    check_id="snapshot_gate",
                    reason_code="SNAPSHOT_UNAVAILABLE",
                    message=f"风控快照装配失败，拒绝下单（Fail-Closed）: {exc}",
                )
            )
            return self._report(request, blocks, None, None, evaluated_at)

        # ── 闸门 4: 风险否决评估（MOD-RK-24 纯函数判定核心）─────────
        veto_decision = self._veto_engine.evaluate(request, snapshot)
        for verdict in veto_decision.vetoes:
            blocks.append(
                PreExecutionBlock(
                    check_id=verdict.rule_id,
                    reason_code=verdict.reason_code,
                    message=verdict.message,
                )
            )
        return self._report(request, blocks, veto_decision, snapshot.snapshot_id, evaluated_at)

    @staticmethod
    def _report(
        request: OrderRiskRequest,
        blocks: list[PreExecutionBlock],
        veto_decision: VetoDecision | None,
        snapshot_id: str | None,
        evaluated_at: datetime,
    ) -> PreExecutionReport:
        report = PreExecutionReport(
            allowed=not blocks,
            blocks=tuple(blocks),
            veto_decision=veto_decision,
            snapshot_id=snapshot_id,
            request_id=request.request_id,
            evaluated_at=evaluated_at,
        )
        if not report.allowed:
            _logger.warning(
                "PRE_EXEC_BLOCKED request=%s symbol=%s reasons=%s",
                request.request_id,
                request.symbol,
                [b.reason_code for b in report.blocks],
            )
        return report
