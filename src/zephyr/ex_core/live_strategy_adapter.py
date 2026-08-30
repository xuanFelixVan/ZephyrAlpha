# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.live_strategy_adapter
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib；zephyr.ex_core.trading_session（TradingSession 生命周期契约：start/stop/get_session_report）
# [CONSUMERS] 57 号文 GAP-2 常驻服务化——CLI 接线已落（scripts/start_paper_session.py --service：assemble_session 包 slot 常驻运行）；挂计划任务/调度=Owner 窗口
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只编排不重造（包装 TradingSession 不复制下单/撤单逻辑）；slot 异常隔离（单 slot 装配/启动/停止/崩溃不扩散其余 slot 与服务本体）；业务心跳 tmp+os.replace 原子写（tick_subscriber biz 心跳先例），与 guard 进程心跳（tmp/trading.heartbeat，ISO|guard_pid|child_pid）正交；重启上限熔断（默认 3 次，process_supervisor MAX_RESTART_ATTEMPTS 先例）超限转 EXHAUSTED 等人工；仅承载模拟盘会话（实盘启用一律 Owner 窗口，本模块无任何下单路径——下单语义在 TradingSession 内）
# [MODIFY-GUARD] 57_daily_cycle_sop.md §2/§7 GAP-2；#ARCH-DAILY-CYCLE-GAP23-001
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 装配/启动失败→slot FAILED 隔离+心跳可见不抛出；心跳写出失败→log 不阻断主流程；配置/生命周期错误→LiveStrategyAdapterError（details 字典承载 slot_id 等，消息文本不插值变量）
# [TESTS] tests/ex_core/test_live_strategy_adapter.py
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 监督循环为"有界 while not stop_event + close_at 收盘截止 + sleeper 轮询"（start_paper_session.py 保活同口径，PERM-TRIGGER 门禁批准的过渡形态结构），非 while True 永久轮询
"""
LiveStrategyAdapter — 模拟盘策略常驻服务适配器（57 号文 GAP-2 常驻服务化）。

真源
----
- 57 号文 §2/§7 GAP-2：盘中模拟盘常驻服务入口——start_paper_session.py 是
  交易日 09:25 前人工拉起的过渡形态 MVP，本件把 TradingSession 包装为常驻
  可管理服务（启动/优雅停止/心跳落盘/异常隔离）。
- strategy_runner.py §三态共用：盘中模拟盘复用同一 StrategyBase 实例——
  信号源接线（construction_backlog B4 真信号源）与 EDE tick 适配不在本件
  范围，本件只管会话生命周期。

职责边界
--------
1. **多 slot 承载**：每个 StrategySlot 包装一个 TradingSession（session_factory
   延迟装配——崩溃重启语义=工厂重造新会话实例，不复用残留态）。
2. **异常隔离**：单 slot 装配/启动/停止/盘中意外停止不扩散——标记 FAILED
   心跳可见，其余 slot 与服务本体继续运行。
3. **退避重启**：FAILED slot 经 backoff 后由监督循环重启，上限熔断
   （默认 3 次，process_supervisor MAX_RESTART_ATTEMPTS 先例）转 EXHAUSTED。
4. **双心跳正交**：本件写业务心跳 tmp/live_strategy_biz.heartbeat（JSON，
   tmp→os.replace 原子写，tick_subscriber biz 心跳先例）；guard 进程心跳
   （tmp/trading.heartbeat，PowerShell guard 代写）由 start_trading.ps1 体系
   负责——两路正交，本件不触碰 guard 心跳。
5. **有界监督**：run() 非 while True——close_at 收盘截止 / 外部 stop_event /
   KeyboardInterrupt 三通道优雅收场（stop 自动撤未成交单语义保留在
   TradingSession.stop() 内）。

实盘边界（Owner 窗口铁律）：本适配器仅承载模拟盘会话（slot 由装配方注入，
如 start_paper_session.assemble_session 口径连 QMT 模拟账户）；本模块不创建
broker、无任何下单路径；实盘启用一律 Owner 窗口。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: slots 参数
#   fields: 参数 slots（无注解）
#   code: live_strategy_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: heartbeat_path 参数
#   fields: 参数 heartbeat_path（无注解）
#   code: live_strategy_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: heartbeat_interval_seconds 参数
#   fields: 参数 heartbeat_interval_seconds（无注解）
#   code: live_strategy_adapter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: max_restart_attempts 参数
#   fields: 参数 max_restart_attempts（无注解）
#   code: live_strategy_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LiveStrategyAdapter
#   name_en: LiveStrategyAdapter
#   intro: 模拟盘策略常驻服务——多 slot 承载 TradingSession 的生命周期管理器。
#   desc: 模拟盘策略常驻服务——多 slot 承载 TradingSession 的生命周期管理器。 用法（CLI/调度接线层）:: adapter = LiveStrategyAdapt…；公共方法（定义序）: is_runn…
#   inputs: slots heartbeat_path heartbeat_interval_seconds max_restart_attempts…
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: LiveStrategyAdapter
#   downstream: 57 号文 GAP-2 常驻服务化——CLI 接线已落（scripts/start_paper_session.py --service：assemble_s…
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

import json
import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from datetime import time as dtime
from enum import Enum
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

from zephyr.ex_core.trading_session import TradingSession

_logger = logging.getLogger(__name__)

_REPO_ROOT: Final = Path(__file__).resolve().parents[3]  # src/zephyr/ex_core/ → 仓根
#: A 股交易时刻口径=北京时区（与 trading_session._SHANGHAI_TZ 同口径）
_SHANGHAI_TZ: Final = ZoneInfo("Asia/Shanghai")
#: 业务心跳默认落盘路径（与 guard 进程心跳 tmp/trading.heartbeat 正交）
_DEFAULT_HEARTBEAT_PATH: Final = _REPO_ROOT / "tmp" / "live_strategy_biz.heartbeat"
#: 心跳/监督节奏（秒）——与 guard 15s 心跳同节奏（start_trading.ps1 口径）
_HEARTBEAT_INTERVAL_SECONDS: Final = 15.0
#: slot 重启上限（process_supervisor MAX_RESTART_ATTEMPTS 先例：3 次上限终止重启循环）
_MAX_RESTART_ATTEMPTS: Final = 3
#: FAILED slot 退避秒数（退避重试属 PERM-TRIGGER 例外口径）
_RESTART_BACKOFF_SECONDS: Final = 30.0
_SERVICE_NAME: Final = "live_strategy_adapter"

__all__: Final = [
    "LiveStrategyAdapter",
    "LiveStrategyAdapterError",
    "SlotState",
    "StrategySlot",
]


class LiveStrategyAdapterError(RuntimeError):
    """适配器配置/生命周期错误（details 字典承载上下文，消息文本不插值变量）。

    Attributes:
        details: 错误上下文（slot_id/state 等，MSG-EXPOSURE 合规）。
    """

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class SlotState(str, Enum):
    """slot 生命周期状态机（PENDING→RUNNING→FAILED→(退避重启|EXHAUSTED)→STOPPED）。"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    EXHAUSTED = "EXHAUSTED"
    STOPPED = "STOPPED"


@dataclass(frozen=True)
class StrategySlot:
    """策略槽位（装配延迟到 start/重启时——崩溃重启=工厂重造新会话实例）。

    Attributes:
        slot_id: 槽位标识（心跳/日志载体，适配器内唯一）。
        session_factory: TradingSession 装配器——每次调用 MUST 返回新实例
            （复用旧实例会把残留订单/计数态带入重启会话，污染隔离语义）。
    """

    slot_id: str
    session_factory: Callable[[], TradingSession]


@dataclass
class _SlotRuntime:
    """slot 运行态（服务内部持有；failed_at 用 time.monotonic 退避锚点）。"""

    slot: StrategySlot
    state: SlotState = SlotState.PENDING
    session: TradingSession | None = None
    restart_count: int = 0
    last_error: str | None = None
    failed_at: float | None = None


class LiveStrategyAdapter:
    """模拟盘策略常驻服务——多 slot 承载 TradingSession 的生命周期管理器。

    用法（CLI/调度接线层）::

        adapter = LiveStrategyAdapter([StrategySlot("paper", factory)])
        adapter.start()                     # 逐 slot 装配+启动（异常隔离）
        adapter.run(close_at=dtime(15, 5))  # 有界监督至收盘（心跳+退避重启）
        # run() 内 finally 自动 adapter.stop()（优雅停止，撤未成交单）
    """

    def __init__(
        self,
        slots: list[StrategySlot],
        *,
        heartbeat_path: Path = _DEFAULT_HEARTBEAT_PATH,
        heartbeat_interval_seconds: float = _HEARTBEAT_INTERVAL_SECONDS,
        max_restart_attempts: int = _MAX_RESTART_ATTEMPTS,
        restart_backoff_seconds: float = _RESTART_BACKOFF_SECONDS,
        now_fn: Callable[[], datetime] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        """
        Args:
            slots: 策略槽位（非空、slot_id 唯一）。
            heartbeat_path: 业务心跳落盘路径（默认 tmp/live_strategy_biz.heartbeat）。
            heartbeat_interval_seconds: 心跳/监督节奏秒（默认 15，guard 同节奏）。
            max_restart_attempts: slot 重启上限（默认 3，超限 EXHAUSTED）。
            restart_backoff_seconds: FAILED slot 退避秒（默认 30）。
            now_fn: 当前时间（测试注入假钟；默认北京时区现在）。
            sleeper: 监督轮询睡眠（测试注入假钟；默认 time.sleep）。
        """
        if not slots:
            raise LiveStrategyAdapterError("slots 不能为空", details={"reason": "empty_slots"})
        slot_ids = [s.slot_id for s in slots]
        if len(set(slot_ids)) != len(slot_ids):
            raise LiveStrategyAdapterError("slot_id 必须唯一", details={"slot_ids": slot_ids})
        self._runtimes: list[_SlotRuntime] = [_SlotRuntime(slot=s) for s in slots]
        self._heartbeat_path = heartbeat_path
        self._heartbeat_interval_seconds = heartbeat_interval_seconds
        self._max_restart_attempts = max_restart_attempts
        self._restart_backoff_seconds = restart_backoff_seconds
        self._now_fn = now_fn or (lambda: datetime.now(_SHANGHAI_TZ))
        self._sleeper = sleeper
        self._running = False
        self._started_ts: float | None = None

    @property
    def is_running(self) -> bool:
        """服务是否在运行（start 后 stop 前）。"""
        return self._running

    # ------------------------------------------------------------------
    # 生命周期
    # ------------------------------------------------------------------

    def start(self) -> None:
        """启动全部 slot（逐 slot 异常隔离：单个装配/启动失败不扩散）。"""
        if self._running:
            _logger.warning("LiveStrategyAdapter already running")
            return
        self._started_ts = self._now_fn().timestamp()
        self._running = True
        for runtime in self._runtimes:
            self._start_slot(runtime)
        self._write_heartbeat()
        _logger.info("LiveStrategyAdapter started: %s", self._summary_counts())

    def run(self, close_at: dtime | None = None, *, stop_event: threading.Event | None = None) -> int:
        """有界监督循环（收盘时点/外部停止事件/KeyboardInterrupt 三通道截止）。

        每轮：写业务心跳 → 监督 slot 健康（意外停止检测+退避重启）→ sleep。
        收场一律优雅 stop（finally 语义，stop 自动撤未成交单保留在会话内）。

        Args:
            close_at: 保活截止时刻（默认 None=仅 stop_event/中断截止；
                57 号文 §2 口径建议 15:05 收盘后收尾缓冲）。
            stop_event: 外部停止事件（CLI/调度层注入；None=内部新建）。

        Returns:
            0=正常收场（到点/事件/人工中断均为正常语义）。

        Raises:
            LiveStrategyAdapterError: 未 start 直接 run（生命周期顺序错误）。
        """
        if not self._running:
            raise LiveStrategyAdapterError("run() 前必须先 start()", details={"state": "not_started"})
        stop_event = stop_event or threading.Event()
        close_ts = self._close_ts(close_at)
        interrupted = False
        try:
            while not stop_event.is_set():
                if close_ts is not None and self._now_fn() >= close_ts:
                    _logger.info("到达收盘截止时点——优雅停止: close_at=%s", close_at)
                    break
                self._write_heartbeat()
                self._supervise_once()
                self._sleeper(self._heartbeat_interval_seconds)
        except KeyboardInterrupt:
            interrupted = True
            _logger.info("KeyboardInterrupt——优雅停止（stop 撤未成交单语义保留）")
        finally:
            self.stop()
        _logger.info("LiveStrategyAdapter run 收场: %s", "人工中断" if interrupted else "到点/事件停止")
        return 0

    def stop(self) -> None:
        """优雅停止全部 slot（逐 slot 异常隔离）+ 最终心跳（幂等）。"""
        if not self._running:
            return
        self._running = False
        for runtime in self._runtimes:
            self._stop_slot(runtime)
        self._write_heartbeat()
        _logger.info("LiveStrategyAdapter stopped: %s", self._summary_counts())

    # ------------------------------------------------------------------
    # slot 管理（异常隔离边界）
    # ------------------------------------------------------------------

    def _start_slot(self, runtime: _SlotRuntime) -> None:
        """装配并启动单个 slot（失败 → FAILED 隔离不抛出——单策略崩溃不拖垮服务）。"""
        try:
            session = runtime.slot.session_factory()
            session.start()
        except Exception as exc:  # noqa: BLE001 — 异常隔离边界：装配/启动崩溃不扩散
            self._mark_failed(runtime, exc)
            return
        runtime.session = session
        runtime.state = SlotState.RUNNING
        runtime.last_error = None
        runtime.failed_at = None
        _logger.info(
            "slot started: slot_id=%s restart_count=%d",
            runtime.slot.slot_id,
            runtime.restart_count,
        )

    def _stop_slot(self, runtime: _SlotRuntime) -> None:
        """停止单个 slot（停止异常隔离：不扩散到其他 slot 的停止）。"""
        session = runtime.session
        runtime.session = None
        if session is not None:
            try:
                session.stop()
            except Exception:  # noqa: BLE001 — 停止异常已落日志，不改变收场语义
                _logger.exception("slot stop 异常（已隔离）: slot_id=%s", runtime.slot.slot_id)
        if runtime.state is not SlotState.EXHAUSTED:
            runtime.state = SlotState.STOPPED

    def _mark_failed(self, runtime: _SlotRuntime, exc: BaseException) -> None:
        """标记 slot FAILED（崩溃隔离+退避锚点），错误入心跳可见。"""
        runtime.state = SlotState.FAILED
        runtime.last_error = f"{type(exc).__name__}: {exc}"
        runtime.failed_at = time.monotonic()
        _logger.exception(
            "slot 崩溃隔离: slot_id=%s restart_count=%d",
            runtime.slot.slot_id,
            runtime.restart_count,
        )

    # ------------------------------------------------------------------
    # 监督（崩溃检测 + 退避重启）
    # ------------------------------------------------------------------

    def _supervise_once(self) -> None:
        """监督一轮：RUNNING slot 意外停止检测 + FAILED slot 退避重启。"""
        for runtime in self._runtimes:
            if (
                runtime.state is SlotState.RUNNING
                and runtime.session is not None
                and not runtime.session.get_session_report().get("running", False)
            ):
                self._mark_failed(runtime, RuntimeError("session stopped unexpectedly"))
            if runtime.state is SlotState.FAILED and self._restart_due(runtime):
                self._restart_slot(runtime)

    def _restart_due(self, runtime: _SlotRuntime) -> bool:
        """退避到期判定（time.monotonic 单调钟，免系统时钟回拨影响）。"""
        if runtime.failed_at is None:
            return False
        return (time.monotonic() - runtime.failed_at) >= self._restart_backoff_seconds

    def _restart_slot(self, runtime: _SlotRuntime) -> None:
        """退避重启单个 slot（上限熔断转 EXHAUSTED 等人工）。"""
        if runtime.restart_count >= self._max_restart_attempts:
            runtime.state = SlotState.EXHAUSTED
            _logger.error(
                "slot 重启超限熔断转 EXHAUSTED（等人工介入）: slot_id=%s restart_count=%d last_error=%s",
                runtime.slot.slot_id,
                runtime.restart_count,
                runtime.last_error,
            )
            return
        runtime.restart_count += 1
        _logger.warning(
            "slot 退避重启: slot_id=%s 第 %d/%d 次 last_error=%s",
            runtime.slot.slot_id,
            runtime.restart_count,
            self._max_restart_attempts,
            runtime.last_error,
        )
        self._stop_slot(runtime)  # 残留会话清理（半启动态：stop 幂等隔离）
        runtime.state = SlotState.PENDING  # _stop_slot 置 STOPPED，重启前归位
        self._start_slot(runtime)

    # ------------------------------------------------------------------
    # 心跳（tick_subscriber biz 心跳先例：tmp→os.replace 原子写）
    # ------------------------------------------------------------------

    def _write_heartbeat(self) -> None:
        """写业务心跳 JSON（与 guard 进程心跳正交；失败 log 不阻断主流程）。

        承载业务活性（slot 状态/重启计数/最近错误/会话报告），供 deadman_switch
        扩展通道与人工巡检消费；进程活性由 guard 心跳（start_trading.ps1 体系）
        覆盖——双心跳正交（#ARCH-DATA-017 裁定同构）。
        """
        started = self._started_ts
        payload = {
            "service": _SERVICE_NAME,
            "ts": self._now_fn().isoformat(timespec="seconds"),
            "pid": os.getpid(),
            "started_ts": (
                datetime.fromtimestamp(started, tz=_SHANGHAI_TZ).isoformat(timespec="seconds") if started else None
            ),
            "running": self._running,
            **self._summary_counts(),
            "slots": [self._slot_payload(rt) for rt in self._runtimes],
        }
        try:
            self._heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self._heartbeat_path.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp_path, self._heartbeat_path)
        except Exception as exc:  # noqa: BLE001 — 心跳写出失败不阻断服务主流程（tick_subscriber 先例）
            _logger.warning("业务心跳写出失败: %s", exc)

    def _slot_payload(self, runtime: _SlotRuntime) -> dict[str, Any]:
        """单 slot 心跳载荷（RUNNING 态附会话公开报告）。"""
        session_report: dict[str, Any] = {}
        if runtime.session is not None and runtime.state is SlotState.RUNNING:
            try:
                session_report = dict(runtime.session.get_session_report())
            except Exception:  # noqa: BLE001 — 报告读取失败不阻断心跳
                _logger.debug("slot report 读取失败: slot_id=%s", runtime.slot.slot_id, exc_info=True)
        return {
            "slot_id": runtime.slot.slot_id,
            "state": runtime.state.value,
            "restart_count": runtime.restart_count,
            "last_error": runtime.last_error,
            "session_report": session_report,
        }

    # ------------------------------------------------------------------
    # 报告
    # ------------------------------------------------------------------

    def status_report(self) -> dict[str, Any]:
        """服务状态快照（CLI/巡检消费，与心跳载荷同构）。"""
        return {
            "service": _SERVICE_NAME,
            "running": self._running,
            **self._summary_counts(),
            "slots": [self._slot_payload(rt) for rt in self._runtimes],
        }

    def _summary_counts(self) -> dict[str, int]:
        """slot 状态计数（心跳/日志共用）。"""
        counts = {
            "slots_total": len(self._runtimes),
            "slots_running": 0,
            "slots_failed": 0,
            "slots_exhausted": 0,
            "slots_stopped": 0,
        }
        for runtime in self._runtimes:
            if runtime.state is SlotState.RUNNING:
                counts["slots_running"] += 1
            elif runtime.state is SlotState.FAILED:
                counts["slots_failed"] += 1
            elif runtime.state is SlotState.EXHAUSTED:
                counts["slots_exhausted"] += 1
            elif runtime.state is SlotState.STOPPED:
                counts["slots_stopped"] += 1
        return counts

    def _close_ts(self, close_at: dtime | None) -> datetime | None:
        """收盘截止时刻 → 当日 tz-aware 时间戳（None=不截止）。"""
        if close_at is None:
            return None
        now = self._now_fn()
        return datetime.combine(now.date(), close_at, tzinfo=now.tzinfo)
