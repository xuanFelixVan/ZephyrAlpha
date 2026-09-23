# [BLUEPRINT] MOD-EX-024 | docs/03_modules/MOD-EX-024/
# [MODULE] zephyr.ex_core.pre_execution_checker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.risk.core.risk_data_pipeline; zephyr.risk.core.risk_veto_engine; zephyr.data.calendar; zephyr.data.trading_calendar
# [CONSUMERS] MOD-L06-001(TradingSession 逐单执行前硬拦：_validate_and_submit→_is_blocked_by_pre_execution，经 attach_pre_execution_gate()/pre_execution_checker= 注入即生效，快照源=TradingSession.build_risk_snapshot) ; MOD-EX-007(Execution Risk Gate, planned—全仓无实现代码，未落地)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五级检查顺序固定(熔断→live档阻断→时段→快照→否决); live档探针异常Fail-Closed拒单(O-6/S-1); 熔断激活短路不建快照; 各环节Fail-Closed(探针异常按熔断/非交易时段处理,快照失败拒单,C-004默认拒绝); 风险判定核心委托MOD-RK-24纯函数(本模块只编排不重造); 报告frozen不可变
# [MODIFY-GUARD] docs/03_modules/MOD-EX-024/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RiskDataPipelineError(快照装配上抛转SNAPSHOT_UNAVAILABLE阻断块,不外抛)
# [TESTS] tests/ex_core/test_pre_execution_checker.py
# [A_module] module_id=MOD-EX-024 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Pre-Execution Checker — 执行前检查器 (MOD-EX-024)

下单前统一五级硬检查（编排层，对接 MOD-RK-25 快照 + MOD-RK-24 否决引擎 + 既有风控件）：
  1. Kill Switch 闸门  — 熔断激活拒绝全部新订单（短路，不建快照；
     探针异常按已熔断处理，Fail-Closed；生产接线: DefaultRiskValidator.kill_switch_active）
  1.5 live 档阻断闸门  — blocks_live_trading=true 拒全部新单（O-6/S-1 G6 接线；
     探针异常按阻断处理 Fail-Closed；默认读 qmt_environments.yaml，环境解析走 config 层）
  2. 交易时段闸门      — L-003 非交易时段禁下单（默认 A 股窗口 09:30-11:30 / 13:00-15:00
     Asia/Shanghai + 交易日判定；探针异常按非交易时段处理，Fail-Closed；
     CAND-CRYPTO-006/#262 改造：支持 market_calendar 注入，默认 ASHareCalendar）
  3. 风控快照装配      — MOD-RK-25 RiskDataPipeline；失败 → SNAPSHOT_UNAVAILABLE 拒单
  4. 风险否决评估      — MOD-RK-24 RiskVetoEngine（判定核心为纯函数，本模块只编排）

降级铁律（C-004 默认拒绝）：任何检查环节不可用 → 拒绝新订单，不放行。

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/pre_execution_checker.yaml
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, time
from typing import TYPE_CHECKING, Final
from zoneinfo import ZoneInfo

from zephyr.data.calendar import MarketCalendar, get_market_calendar
from zephyr.risk.core.risk_data_pipeline import RiskDataPipelineError, RiskSnapshot
from zephyr.risk.core.risk_veto_engine import (
    OrderRiskRequest,
    RiskVetoEngine,
    VetoDecision,
)
from zephyr.shared.foundation.env import Env as EnvName
from zephyr.shared.foundation.env import current_env

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pathlib import Path

LiveBlockProbe = Callable[[], bool]
"""live 档阻断探针：返回 True=blocks_live_trading 生效拒单（O-6/S-1，G6）。"""


def _default_live_block_probe(
    config_path: Path | None = None,
) -> LiveBlockProbe:
    """默认探针：查 qmt_environments.yaml 当前环境档 blocks_live_trading（纯加闸）。

    环境解析走 config 层 shared.foundation.env.current_env()（禁散落直访 ZEPHYR_ENV，
    ZEPHYR-ENV-DIRECT-ACCESS 门纪律）；prod→live 档，其余→sim 档。
    Fail-Closed：配置不可读/环境档缺失/旗标缺失/解析异常 一律返回 True（拒单不放行）。
    """
    resolved_path = config_path
    cache: dict[str, bool] = {}

    def _probe() -> bool:
        from pathlib import Path as _Path

        import yaml as _yaml

        from zephyr.shared.io.paths import REPO_ROOT

        nonlocal resolved_path
        if resolved_path is None:
            resolved_path = _Path(REPO_ROOT) / "config" / "qmt_environments.yaml"
        env_key = "live" if current_env() == EnvName.PROD else "sim"
        if env_key in cache:
            return cache[env_key]
        data = _yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
        entries = {str(e.get("env")): e for e in data.get("environments") or []}
        entry = entries.get(env_key)
        if entry is None or "blocks_live_trading" not in entry:
            raise ValueError(f"qmt_environments 缺 {env_key} 档 blocks_live_trading 旗标")
        flag = bool(entry["blocks_live_trading"])
        cache[env_key] = flag
        return flag

    return _probe


__all__: Final = [
    "KillSwitchProbe",
    "LiveBlockProbe",
    "PreExecutionBlock",
    "PreExecutionChecker",
    "PreExecutionReport",
    "SessionWindowProbe",
    "SnapshotBuilder",
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


def _is_trading_window(now: datetime, calendar: MarketCalendar) -> bool:
    """基于市场日历的交易时段判定（CAND-CRYPTO-006/#262 注入式改造）。

    naive datetime 按日历 timezone 口径解释；aware datetime 先换算对应时区。
    """
    if now.tzinfo is None:
        local_now = now.replace(tzinfo=ZoneInfo(calendar.timezone))
    else:
        local_now = now.astimezone(ZoneInfo(calendar.timezone))

    try:
        if not calendar.is_trading_day(local_now.date()):
            return False
    except Exception:  # noqa: BLE001 — 日历异常降级为周日历判定
        if local_now.weekday() >= 5:
            return False

    now_time = local_now.time()
    return any(start <= now_time <= end for start, end in calendar.session_windows(local_now.date()))


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
        market_calendar: MarketCalendar | None = None,
        live_block_probe: LiveBlockProbe | None = None,
    ) -> None:
        """
        Args:
            snapshot_builder: 风控快照构建器（生产接线 RiskDataPipeline.build_snapshot）。
            kill_switch_probe: 熔断状态探针；None=未接线（不臆造熔断态，记 DEBUG 留痕）。
            session_window_probe: 交易时段探针；None=用 market_calendar 或默认 A 股窗口实现。
            veto_engine: 否决引擎；None=内置默认硬规则集。
            market_calendar: 市场日历注入（CAND-CRYPTO-006/#262）；None=ASHareCalendar 默认。
            live_block_probe: live 档阻断探针（O-6/S-1 G6）；None=默认读
                qmt_environments.yaml 当前环境档 blocks_live_trading（fail-closed）。
        """
        self._snapshot_builder = snapshot_builder
        self._kill_switch_probe = kill_switch_probe
        if session_window_probe is not None:
            self._session_window_probe = session_window_probe
        else:
            calendar = market_calendar or get_market_calendar("ashare")
            self._session_window_probe = lambda now: _is_trading_window(now, calendar)
        self._veto_engine = veto_engine or RiskVetoEngine()
        self._live_block_probe = live_block_probe or _default_live_block_probe()

    def check(self, request: OrderRiskRequest, *, now: datetime | None = None) -> PreExecutionReport:
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

        # ── 闸门 1.5: live 档阻断（O-6/S-1，blocks_live_trading 接线 G6）─────
        try:
            live_blocked = bool(self._live_block_probe())
        except Exception as exc:  # noqa: BLE001 — Fail-Closed（纯加闸不加放）
            _logger.critical("LIVE_BLOCK_PROBE_ERROR fail-closed error=%s", exc)
            live_blocked = True
        if live_blocked:
            _logger.critical(
                "LIVE_TRADING_BLOCKED 拒单 symbol=%s（blocks_live_trading=true，实盘门禁未解锁）",
                getattr(request, "symbol", "?"),
            )
            blocks.append(
                PreExecutionBlock(
                    check_id="live_env_gate",
                    reason_code="LIVE_TRADING_BLOCKED",
                    message="blocks_live_trading=true：live 档实盘门禁未解锁，拒绝全部新订单（Fail-Closed）",
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
