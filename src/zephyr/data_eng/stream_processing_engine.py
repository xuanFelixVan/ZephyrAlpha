# [BLUEPRINT] MOD-DATENG-004 | docs/03_modules/_domain_data_eng/stream_processing_engine/blueprint.md
# [MODULE] zephyr.data_eng.stream_processing_engine
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] 无（引擎核心纯内存；事件流/sink/侧输出/背压回调全注入）
# [CONSUMERS] 运行时装配批（行情事件流接 kline_resampler 上游 / 聚合指标落指标sink / 背压接流控）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 窗口注册表闭合(未注册禁止ingest); 事件时间水位线单调不退; 迟到判定确定性(event_time<watermark); 迟到策略词表闭合(drop|side_output); 窗口触发判定确定性(end<=watermark); 输出按(spec,key,window_start)确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/stream_processing_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StreamEngineError(占位 ZA-DE-UNREGISTERED-STREAM-ENGINE)——空窗口名/重复注册/非法窗口参数/未注册窗口ingest/空事件key/非有限value时抛
# [TESTS] tests/data_eng/test_stream_processing_engine.py
# [A_module] module_id=MOD-DATENG-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



StreamProcessingEngine — 轻量单机流处理引擎（MOD-DATENG-004）。

B5-07234（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-007，B5）：事件时
间**滚动/会话窗口**聚合（窗口注册 + 触发判定）+ 水位线与迟到数据处理
（迟到策略：丢弃/侧输出）+ 背压信号（队列水位阈值回调）——消费注入事
件流，输出实时聚合指标落 sink 回调。Flink/Bytewax 单机化纯内存版。

边界声明（蓝图 §0）：kline_resampler（D_DATA）为 K 线周期重采样件——本
件是通用事件时间窗口引擎，不重采样行情周期；引擎不拉取事件（事件流由
调用方注入 ingest），聚合输出经注入 sink 回调，不直连存储。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: allowed_lateness 参数
#   fields: 参数 allowed_lateness（无注解）
#   code: stream_processing_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: sink 参数
#   fields: 参数 sink（无注解）
#   code: stream_processing_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: side_output_sink 参数
#   fields: 参数 side_output_sink（无注解）
#   code: stream_processing_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: backpressure_sink 参数
#   fields: 参数 backpressure_sink（无注解）
#   code: stream_processing_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StreamProcessingEngine
#   name_en: StreamProcessingEngine
#   intro: 单机事件时间窗口引擎（注册 + ingest + poll 触发 + flush 排空）。
#   desc: 单机事件时间窗口引擎（注册 + ingest + poll 触发 + flush 排空）。；公共方法（定义序）: register_window, watermark, ingest, poll, flush, sta…
#   inputs: allowed_lateness sink side_output_sink backpressure_sink max_queue
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: StreamProcessingEngine
#   downstream: 运行时装配批（行情事件流接 kline_resampler 上游 / 聚合指标落指标sink / 背压接流控）
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
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "LatePolicy",
    "StreamEngineError",
    "StreamEvent",
    "StreamProcessingEngine",
    "WindowAggregate",
    "WindowKind",
    "WindowSpec",
]

_EPOCH: Final = datetime.datetime(1970, 1, 1)


class StreamEngineError(Exception):
    """流处理引擎输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DE-UNREGISTERED-STREAM-ENGINE。
    """


class WindowKind(str, Enum):
    """窗口类型（词表闭合）。"""

    TUMBLING = "tumbling"
    SESSION = "session"


class LatePolicy(str, Enum):
    """迟到数据策略（词表闭合）。"""

    DROP = "drop"
    SIDE_OUTPUT = "side_output"


@dataclass(frozen=True)
class StreamEvent:
    """流事件（事件时间语义，frozen）。"""

    key: str
    event_time: datetime.datetime
    value: float


@dataclass(frozen=True)
class WindowSpec:
    """窗口注册：TUMBLING 须 size；SESSION 须 gap（事件时间间隔超时闭合）。"""

    name: str
    kind: WindowKind
    size: datetime.timedelta | None = None
    gap: datetime.timedelta | None = None
    late_policy: LatePolicy = LatePolicy.DROP


@dataclass(frozen=True)
class WindowAggregate:
    """窗口聚合输出（count/total，frozen）。"""

    spec_name: str
    key: str
    window_start: datetime.datetime
    window_end: datetime.datetime
    count: int
    total: float


@dataclass
class _SessionState:
    """会话窗口运行态（end = last_ts + gap，左闭右开）。"""

    start: datetime.datetime
    last_ts: datetime.datetime
    gap: datetime.timedelta
    count: int = 0
    total: float = 0.0


class StreamProcessingEngine:
    """单机事件时间窗口引擎（注册 + ingest + poll 触发 + flush 排空）。"""

    def __init__(
        self,
        *,
        allowed_lateness: datetime.timedelta = datetime.timedelta(0),
        sink: Callable[[WindowAggregate], None] | None = None,
        side_output_sink: Callable[[StreamEvent], None] | None = None,
        backpressure_sink: Callable[[int], None] | None = None,
        max_queue: int = 1000,
    ) -> None:
        if allowed_lateness < datetime.timedelta(0):
            raise StreamEngineError("allowed_lateness 非法（须 >= 0）")
        if max_queue <= 0:
            raise StreamEngineError("max_queue 非法（须 > 0）")
        self._allowed_lateness = allowed_lateness
        self._sink = sink
        self._side_output_sink = side_output_sink
        self._backpressure_sink = backpressure_sink
        self._max_queue = max_queue
        self._specs: dict[str, WindowSpec] = {}
        self._pending: list[StreamEvent] = []
        self._max_seen: datetime.datetime | None = None
        # tumbling: (spec, key, window_start) -> [count, total]
        self._tumbling: dict[tuple[str, str, datetime.datetime], list] = {}
        # session: (spec, key) -> list[_SessionState]（按 start 有序）
        self._sessions: dict[tuple[str, str], list[_SessionState]] = {}
        self._dropped_late = 0
        self._side_outputted = 0

    # ── 窗口注册 ──────────────────────────────────────────────────────────

    def register_window(self, spec: WindowSpec) -> None:
        """登记窗口：TUMBLING 须 size>0；SESSION 须 gap>0；name 唯一。"""
        if not spec.name:
            raise StreamEngineError("窗口 name 为空")
        if spec.name in self._specs:
            raise StreamEngineError(f"窗口重复注册: {spec.name!r}")
        if not isinstance(spec.kind, WindowKind):
            raise StreamEngineError(f"非法窗口类型: {spec.kind!r}")
        if not isinstance(spec.late_policy, LatePolicy):
            raise StreamEngineError(f"非法迟到策略: {spec.late_policy!r}")
        if spec.kind is WindowKind.TUMBLING:
            if spec.size is None or spec.size <= datetime.timedelta(0):
                raise StreamEngineError(f"TUMBLING 窗口 size 非法: {spec.size!r}")
            if spec.gap is not None:
                raise StreamEngineError("TUMBLING 窗口不允许 gap")
        else:
            if spec.gap is None or spec.gap <= datetime.timedelta(0):
                raise StreamEngineError(f"SESSION 窗口 gap 非法: {spec.gap!r}")
            if spec.size is not None:
                raise StreamEngineError("SESSION 窗口不允许 size")
        self._specs[spec.name] = spec

    # ── 水位线 ────────────────────────────────────────────────────────────

    @property
    def watermark(self) -> datetime.datetime | None:
        """当前水位线 = 已见最大事件时间 - allowed_lateness（无事件为 None）。"""
        if self._max_seen is None:
            return None
        return self._max_seen - self._allowed_lateness

    # ── 事件摄入 ──────────────────────────────────────────────────────────

    def ingest(self, event: StreamEvent) -> bool:
        """摄入事件：迟到判定 → 迟到策略 → 入待处理队列（背压信号）。

        返回 True=接受进入窗口流；False=按迟到策略丢弃/侧输出。
        """
        if not self._specs:
            raise StreamEngineError("未注册任何窗口（窗口注册表闭合，禁止 ingest）")
        if not event.key:
            raise StreamEngineError("事件 key 为空")
        if not isinstance(event.value, (int, float)) or isinstance(event.value, bool):
            raise StreamEngineError(f"事件 value 非数值: {event.value!r}")
        if not math.isfinite(event.value):
            raise StreamEngineError(f"事件 value 非有限: {event.value!r}")

        wm = self.watermark
        if wm is not None and event.event_time < wm:
            self._handle_late(event)
            return False

        if self._max_seen is None or event.event_time > self._max_seen:
            self._max_seen = event.event_time
        self._pending.append(event)
        depth = len(self._pending)
        if depth >= self._max_queue:
            _log.warning("背压信号: 队列水位 %d >= 阈值 %d", depth, self._max_queue)
            if self._backpressure_sink is not None:
                try:
                    self._backpressure_sink(depth)
                except Exception:  # noqa: BLE001 — 背压回调异常不阻断摄入
                    _log.exception("backpressure_sink 回调失败")
        return True

    def _handle_late(self, event: StreamEvent) -> None:
        """迟到处置：任一注册窗口声明 SIDE_OUTPUT → 侧输出；否则丢弃。"""
        side = any(s.late_policy is LatePolicy.SIDE_OUTPUT for s in self._specs.values())
        if side:
            self._side_outputted += 1
            _log.info("迟到事件侧输出: key=%s ts=%s", event.key, event.event_time)
            if self._side_output_sink is not None:
                try:
                    self._side_output_sink(event)
                except Exception:  # noqa: BLE001 — 侧输出异常不阻断
                    _log.exception("side_output_sink 回调失败")
        else:
            self._dropped_late += 1
            _log.info("迟到事件丢弃: key=%s ts=%s", event.key, event.event_time)

    # ── 触发判定与输出 ────────────────────────────────────────────────────

    def poll(self) -> tuple[WindowAggregate, ...]:
        """排空待处理队列并按水位线触发闭合窗口（end <= watermark → 输出）。"""
        self._drain_pending()
        wm = self.watermark
        emitted: list[WindowAggregate] = []
        if wm is not None:
            emitted.extend(self._close_tumbling(wm))
            emitted.extend(self._close_sessions(wm))
        emitted.sort(key=lambda a: (a.spec_name, a.key, a.window_start))
        self._emit(emitted)
        return tuple(emitted)

    def flush(self) -> tuple[WindowAggregate, ...]:
        """流末排空：所有开启窗口强制闭合输出（确定性排序）。"""
        self._drain_pending()
        emitted: list[WindowAggregate] = []
        for (spec_name, key, start), (count, total) in self._tumbling.items():
            spec = self._specs[spec_name]
            assert spec.size is not None
            emitted.append(WindowAggregate(spec_name, key, start, start + spec.size, count, total))
        self._tumbling.clear()
        for (spec_name, key), sessions in self._sessions.items():
            for s in sessions:
                emitted.append(WindowAggregate(spec_name, key, s.start, s.last_ts + s.gap, s.count, s.total))
        self._sessions.clear()
        emitted.sort(key=lambda a: (a.spec_name, a.key, a.window_start))
        self._emit(emitted)
        return tuple(emitted)

    # ── 统计 ──────────────────────────────────────────────────────────────

    def stats(self) -> dict[str, int]:
        """引擎运行统计（确定性快照）。"""
        return {
            "pending": len(self._pending),
            "open_tumbling": len(self._tumbling),
            "open_sessions": sum(len(v) for v in self._sessions.values()),
            "dropped_late": self._dropped_late,
            "side_outputted": self._side_outputted,
        }

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _drain_pending(self) -> None:
        """待处理队列按 (event_time, key) 确定性排序灌入窗口状态。"""
        pending = sorted(self._pending, key=lambda e: (e.event_time, e.key))
        self._pending = []
        for event in pending:
            for spec in self._specs.values():
                if spec.kind is WindowKind.TUMBLING:
                    self._add_tumbling(spec, event)
                else:
                    self._add_session(spec, event)

    def _add_tumbling(self, spec: WindowSpec, event: StreamEvent) -> None:
        assert spec.size is not None
        offset = (event.event_time - _EPOCH) // spec.size
        start = _EPOCH + offset * spec.size
        bucket = self._tumbling.setdefault((spec.name, event.key, start), [0, 0.0])
        bucket[0] += 1
        bucket[1] += event.value

    def _add_session(self, spec: WindowSpec, event: StreamEvent) -> None:
        assert spec.gap is not None
        sessions = self._sessions.setdefault((spec.name, event.key), [])
        t = event.event_time
        merged: list[_SessionState] = []
        target = _SessionState(start=t, last_ts=t, gap=spec.gap, count=1, total=event.value)
        for s in sessions:
            # 与目标会话相交：s 窗口 [start, last+gap) 与 [t, t+gap) 相交或相邻
            if s.start <= t + spec.gap and t <= s.last_ts + spec.gap:
                target.start = min(target.start, s.start)
                target.last_ts = max(target.last_ts, s.last_ts)
                target.count += s.count
                target.total += s.total
            else:
                merged.append(s)
        merged.append(target)
        merged.sort(key=lambda s: s.start)
        self._sessions[(spec.name, event.key)] = merged

    def _close_tumbling(self, wm: datetime.datetime) -> list[WindowAggregate]:
        out: list[WindowAggregate] = []
        due = [
            k
            for k in self._tumbling
            if k[2] + self._specs[k[0]].size <= wm  # type: ignore[operator]
        ]
        for k in sorted(due):
            count, total = self._tumbling.pop(k)
            spec = self._specs[k[0]]
            assert spec.size is not None
            out.append(WindowAggregate(k[0], k[1], k[2], k[2] + spec.size, count, total))
        return out

    def _close_sessions(self, wm: datetime.datetime) -> list[WindowAggregate]:
        out: list[WindowAggregate] = []
        for sk in sorted(self._sessions):
            sessions = self._sessions[sk]
            keep: list[_SessionState] = []
            for s in sessions:
                if s.last_ts + s.gap <= wm:
                    out.append(WindowAggregate(sk[0], sk[1], s.start, s.last_ts + s.gap, s.count, s.total))
                else:
                    keep.append(s)
            self._sessions[sk] = keep
        return out

    def _emit(self, aggregates: list[WindowAggregate]) -> None:
        if self._sink is None:
            return
        for agg in aggregates:
            try:
                self._sink(agg)
            except Exception:  # noqa: BLE001 — sink 异常不阻断引擎
                _log.exception("sink 回调失败: %s/%s", agg.spec_name, agg.key)
