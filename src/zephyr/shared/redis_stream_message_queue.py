# [BLUEPRINT] MOD-SHARED-004 | docs/03_modules/_domain_shared/redis_stream_message_queue/blueprint.md
# [MODULE] zephyr.shared.redis_stream_message_queue
# [DOMAIN] D_SHARED
# [DEPENDENCIES] 无（协议核心纯内存；Redis 客户端/clock/dlq_sink 全注入；event_bus 语义参照不 import）
# [CONSUMERS] 运行时装配批（事件总线 stream 通道绑定 / 进程内快路径装配 / DLQ 接告警路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 主题须先 bind 方可收发; inproc 与 stream 双通道路由表互斥(同主题冲突改绑拒绝); stream 通道强制注入客户端(未注入 Fail-Closed 不旁路); 消费未 ACK 进 pending 表; pending 超期重投且 deliveries 超上限进 DLQ(无 dlq_sink Fail-Closed 不静默丢弃); 消息id/序列化确定性; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_shared/redis_stream_message_queue/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RedisStreamQueueError(占位 ZA-SH-UNREGISTERED-STREAM-QUEUE)——空topic/未绑定主题/通道错配/客户端缺失/未知message_id/载荷非法/DLQ无出口时抛
# [TESTS] tests/shared/test_redis_stream_message_queue.py
# [A_module] module_id=MOD-SHARED-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""RedisStreamMessageQueue — Redis Streams 可靠消息队列（MOD-SHARED-004）。

B1-00341（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-SHARED-002，C2 D-INT-12）：
Redis Streams 承载事件总线语义——stream + consumer group + ACK 重试
（pending 超期重投）+ DLQ 对接（注入 dlq_sink 回调），保留进程内快路径
（inproc 与 stream 双通道路由表），严禁 Kafka。Redis 客户端全注入
（测试用内存 fake stream 实现），不连真 Redis。

查重分工（蓝图 §0）：event_bus=进程内发布订阅语义（本件复用其主题语义，
inproc 快路径即其承载；stream 通道与可靠投递为本件新增）；alert 路由族=
告警出口（DLQ 经注入 dlq_sink 对接，不重建告警总线）。
"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Protocol, runtime_checkable

_log = logging.getLogger(__name__)

__all__: Final = [
    "Channel",
    "PendingEntry",
    "QueueMessage",
    "RedeliveryReport",
    "RedisStreamMessageQueue",
    "RedisStreamQueueError",
    "StreamClient",
]


class RedisStreamQueueError(Exception):
    """消息队列输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SH-UNREGISTERED-STREAM-QUEUE。
    """


class Channel(str, Enum):
    """投递通道（词表闭合）：进程内快路径 / Redis Stream。"""

    INPROC = "inproc"
    STREAM = "stream"


@dataclass(frozen=True)
class QueueMessage:
    """队列消息（frozen；payload 为 JSON 可序列化字典的确定性快照）。"""

    message_id: str
    topic: str
    payload: dict
    enqueued_at: datetime.datetime


@dataclass(frozen=True)
class PendingEntry:
    """pending 表条目（服务端视图：未 ACK 的已投递消息）。"""

    message_id: str
    consumer: str
    deliveries: int
    idle_ms: int


@dataclass(frozen=True)
class RedeliveryReport:
    """一轮超期重投的结果（确定性排序）。"""

    redelivered: tuple[QueueMessage, ...]
    dead_lettered: tuple[QueueMessage, ...]


@runtime_checkable
class StreamClient(Protocol):
    """Redis Streams 客户端协议（全注入；生产=redis-py，测试=内存 fake）。"""

    def xadd(self, stream: str, fields: Mapping[str, str]) -> str:
        """追加消息，返回服务端消息 id。"""
        ...

    def xreadgroup(
        self,
        group: str,
        consumer: str,
        streams: Mapping[str, str],
        count: int,
    ) -> list[tuple[str, list[tuple[str, Mapping[str, str]]]]]:
        """消费组读取新消息（\">\" 语义），返回 [(stream, [(id, fields)])]。"""
        ...

    def xack(self, stream: str, group: str, *message_ids: str) -> int:
        """ACK 消息（移出服务端 PEL），返回确认条数。"""
        ...

    def xpending(self, stream: str, group: str, *, min_idle_ms: int = 0) -> list[PendingEntry]:
        """pending 表服务端视图（idle >= min_idle_ms）。"""
        ...


@dataclass
class _Pending:
    """模块侧 pending 镜像（持有载荷，服务端 PEL 仅存 id）。"""

    message: QueueMessage
    deliveries: int
    last_delivery: datetime.datetime


class RedisStreamMessageQueue:
    """Redis Streams 可靠消息队列（双通道路由 + ACK重试 + DLQ）。"""

    def __init__(
        self,
        *,
        client: StreamClient | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        dlq_sink: Callable[[QueueMessage], None] | None = None,
        group: str = "zephyr",
        consumer: str = "consumer-1",
        max_deliveries: int = 3,
        pending_timeout_ms: int = 30_000,
    ) -> None:
        if not group:
            raise RedisStreamQueueError("group 为空")
        if not consumer:
            raise RedisStreamQueueError("consumer 为空")
        if max_deliveries <= 0:
            raise RedisStreamQueueError(f"max_deliveries 非法: {max_deliveries!r}（须 > 0）")
        if pending_timeout_ms <= 0:
            raise RedisStreamQueueError(
                f"pending_timeout_ms 非法: {pending_timeout_ms!r}（须 > 0）"
            )
        self._client = client
        self._clock = clock or datetime.datetime.now
        self._dlq_sink = dlq_sink
        self._group = group
        self._consumer = consumer
        self._max_deliveries = max_deliveries
        self._pending_timeout_ms = pending_timeout_ms
        self._routes: dict[str, Channel] = {}
        self._inproc: dict[str, list[QueueMessage]] = {}
        self._inproc_seq: dict[str, int] = {}
        self._pending: dict[str, _Pending] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _stream_of(topic: str) -> str:
        """主题 → stream 键（确定性映射）。"""
        return f"za:stream:{topic}"

    def _route_of(self, topic: str) -> Channel:
        channel = self._routes.get(topic)
        if channel is None:
            raise RedisStreamQueueError(f"未绑定主题: {topic!r}（须先 bind）")
        return channel

    def _require_client(self) -> StreamClient:
        if self._client is None:
            raise RedisStreamQueueError(
                "Redis 客户端未注入（stream 通道强制注入，禁止旁路）"
            )
        return self._client

    @staticmethod
    def _validate_payload(payload: Mapping) -> dict:
        if not isinstance(payload, Mapping):
            raise RedisStreamQueueError(f"载荷非法: {type(payload).__name__}（须为 Mapping）")
        try:
            json.dumps(payload, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise RedisStreamQueueError(f"载荷不可 JSON 序列化: {exc}") from exc
        return dict(payload)

    # ── 路由表 ────────────────────────────────────────────────────────────

    def bind(self, topic: str, channel: Channel) -> None:
        """绑定主题到通道（同通道幂等；inproc↔stream 改绑拒绝防语义漂移）。"""
        if not topic:
            raise RedisStreamQueueError("topic 为空")
        if not isinstance(channel, Channel):
            raise RedisStreamQueueError(f"非法通道: {channel!r}")
        existing = self._routes.get(topic)
        if existing is not None:
            if existing is not channel:
                raise RedisStreamQueueError(
                    f"主题 {topic!r} 已绑定 {existing.value}，拒绝改绑 {channel.value}"
                )
            return  # 幂等
        if channel is Channel.STREAM:
            self._require_client()  # 绑定时即 Fail-Closed，不留半装配态
        self._routes[topic] = channel
        if channel is Channel.INPROC:
            self._inproc.setdefault(topic, [])
            self._inproc_seq.setdefault(topic, 0)

    def channel_of(self, topic: str) -> Channel:
        """主题通道路由查询（未绑定 Fail-Closed）。"""
        return self._route_of(topic)

    def topics(self) -> tuple[str, ...]:
        """已绑定主题清单（确定性排序）。"""
        return tuple(sorted(self._routes))

    # ── 发布 ─────────────────────────────────────────────────────────────

    def publish(self, topic: str, payload: Mapping) -> str:
        """发布：按路由表分流——inproc 进内存队列 / stream 经注入客户端 xadd。"""
        channel = self._route_of(topic)
        data = self._validate_payload(payload)
        enqueued_at = self._clock()
        if channel is Channel.INPROC:
            self._inproc_seq[topic] += 1
            message_id = f"{topic}-inproc-{self._inproc_seq[topic]}"
            self._inproc[topic].append(QueueMessage(
                message_id=message_id, topic=topic, payload=data, enqueued_at=enqueued_at,
            ))
            return message_id
        fields = {
            "topic": topic,
            "payload": json.dumps(data, ensure_ascii=False, sort_keys=True),
            "enqueued_at": enqueued_at.isoformat(),
        }
        return self._require_client().xadd(self._stream_of(topic), fields)

    # ── 消费 ─────────────────────────────────────────────────────────────

    def consume_inproc(self, topic: str, *, max_count: int | None = None) -> list[QueueMessage]:
        """进程内快路径消费（FIFO 弹出）。"""
        channel = self._route_of(topic)
        if channel is not Channel.INPROC:
            raise RedisStreamQueueError(f"主题 {topic!r} 非 inproc 通道（当前 {channel.value}）")
        if max_count is not None and max_count <= 0:
            raise RedisStreamQueueError(f"max_count 非法: {max_count!r}（须 > 0）")
        backlog = self._inproc[topic]
        n = len(backlog) if max_count is None else min(max_count, len(backlog))
        out = backlog[:n]
        del backlog[:n]
        return out

    def poll(self, topic: str, *, count: int = 10) -> list[QueueMessage]:
        """stream 通道拉取：xreadgroup 取新消息并登记 pending（待 ACK）。"""
        channel = self._route_of(topic)
        if channel is not Channel.STREAM:
            raise RedisStreamQueueError(f"主题 {topic!r} 非 stream 通道（当前 {channel.value}）")
        if count <= 0:
            raise RedisStreamQueueError(f"count 非法: {count!r}（须 > 0）")
        client = self._require_client()
        now = self._clock()
        resp = client.xreadgroup(
            self._group, self._consumer, {self._stream_of(topic): ">"}, count
        )
        out: list[QueueMessage] = []
        for stream, entries in resp:
            if stream != self._stream_of(topic):
                raise RedisStreamQueueError(f"客户端返回未知 stream: {stream!r}")
            for message_id, fields in entries:
                if message_id in self._pending:
                    raise RedisStreamQueueError(f"消息重复投递未走重投通道: {message_id!r}")
                message = QueueMessage(
                    message_id=message_id,
                    topic=fields["topic"],
                    payload=json.loads(fields["payload"]),
                    enqueued_at=datetime.datetime.fromisoformat(fields["enqueued_at"]),
                )
                self._pending[message_id] = _Pending(message=message, deliveries=1, last_delivery=now)
                out.append(message)
        return out

    # ── ACK / 重投 / DLQ ──────────────────────────────────────────────────

    def ack(self, message_id: str) -> None:
        """确认：移出 pending 镜像并对服务端 xack。"""
        entry = self._pending.pop(message_id, None)
        if entry is None:
            raise RedisStreamQueueError(f"未知 message_id: {message_id!r}（不在 pending 表）")
        acked = self._require_client().xack(
            self._stream_of(entry.message.topic), self._group, message_id
        )
        if acked != 1:
            raise RedisStreamQueueError(
                f"服务端 PEL 与本地镜像不一致: {message_id!r}（xack 返回 {acked}）"
            )

    def collect_redeliveries(self) -> RedeliveryReport:
        """pending 超期重投：超 timeout 未 ACK 重投；deliveries 超上限进 DLQ。

        DLQ 经注入 dlq_sink 出口；未注入且出现死信 → Fail-Closed（不静默丢弃）。
        """
        now = self._clock()
        stale_ids = sorted(
            mid
            for mid, entry in self._pending.items()
            if (now - entry.last_delivery).total_seconds() * 1000 >= self._pending_timeout_ms
        )
        redelivered: list[QueueMessage] = []
        dead_lettered: list[QueueMessage] = []
        for mid in stale_ids:
            entry = self._pending[mid]
            entry.deliveries += 1
            if entry.deliveries > self._max_deliveries:
                if self._dlq_sink is None:
                    raise RedisStreamQueueError(
                        f"消息 {mid!r} 超最大投递次数且 dlq_sink 未注入（拒绝静默丢弃）"
                    )
                self._dlq_sink(entry.message)
                self._require_client().xack(
                    self._stream_of(entry.message.topic), self._group, mid
                )
                del self._pending[mid]
                dead_lettered.append(entry.message)
                _log.warning("消息进 DLQ: %s（topic=%s）", mid, entry.message.topic)
            else:
                entry.last_delivery = now
                redelivered.append(entry.message)
        return RedeliveryReport(
            redelivered=tuple(redelivered), dead_lettered=tuple(dead_lettered)
        )

    # ── 观测 ─────────────────────────────────────────────────────────────

    def pending_view(self, topic: str) -> tuple[PendingEntry, ...]:
        """服务端 PEL 视图（xpending 透传；确定性按 id 排序）。"""
        channel = self._route_of(topic)
        if channel is not Channel.STREAM:
            raise RedisStreamQueueError(f"主题 {topic!r} 非 stream 通道（当前 {channel.value}）")
        entries = self._require_client().xpending(
            self._stream_of(topic), self._group, min_idle_ms=0
        )
        return tuple(sorted(entries, key=lambda e: e.message_id))

    def pending_count(self) -> int:
        """本地 pending 镜像条数。"""
        return len(self._pending)
