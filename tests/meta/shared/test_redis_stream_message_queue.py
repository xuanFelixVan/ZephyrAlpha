# [BLUEPRINT] MOD-SHARED-004 | docs/03_modules/_domain_shared/redis_stream_message_queue/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SHARED-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.shared.test_redis_stream_message_queue
# [TESTS] src/zephyr/shared/redis_stream_message_queue.py
"""MOD-SHARED-004 单元测试：redis_stream_message_queue Redis Streams 可靠消息队列。

蓝图验收（B1-00341/CAND-SHARED-002，C2 D-INT-12）：
stream+consumer group+ACK重试（pending 超期重投）+ DLQ 对接（注入 dlq_sink）+
inproc/stream 双通道路由表。Redis 客户端以内存 fake 实现
xadd/xreadgroup/xack/xpending 语义注入，不连真 Redis；时钟全注入。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.shared.redis_stream_message_queue",
    reason="redis_stream_message_queue not importable",
)

from zephyr.shared.redis_stream_message_queue import (  # noqa: E402
    Channel,
    PendingEntry,
    QueueMessage,
    RedisStreamMessageQueue,
    RedisStreamQueueError,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    """可变注入时钟（测试替身）。"""

    def __init__(self, now: datetime.datetime = _T0) -> None:
        self.now = now

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


class _FakeStreamClient:
    """内存 fake Redis Streams：xadd/xreadgroup/xack/xpending 语义。"""

    def __init__(self) -> None:
        self._streams: dict[str, list[tuple[str, dict]]] = {}
        self._seq: dict[str, int] = {}
        self._read_pos: dict[tuple[str, str], int] = {}  # (stream, group) -> 已读位置
        self._pel: dict[tuple[str, str], dict[str, tuple[str, int, float]]] = {}
        # (stream, group) -> {id: (consumer, deliveries, last_delivery_epoch)}
        self._now_ms: float = 0.0

    def set_now_ms(self, now_ms: float) -> None:
        self._now_ms = now_ms

    def xadd(self, stream: str, fields) -> str:
        self._seq[stream] = self._seq.get(stream, 0) + 1
        message_id = f"{self._seq[stream]}-0"
        self._streams.setdefault(stream, []).append((message_id, dict(fields)))
        return message_id

    def xreadgroup(self, group, consumer, streams, count):
        out = []
        for stream, _marker in streams.items():
            entries = self._streams.get(stream, [])
            pos = self._read_pos.get((stream, group), 0)
            batch = entries[pos : pos + count]
            self._read_pos[(stream, group)] = pos + len(batch)
            pel = self._pel.setdefault((stream, group), {})
            for message_id, fields in batch:
                deliveries = pel.get(message_id, (consumer, 0, 0.0))[1]
                pel[message_id] = (consumer, deliveries + 1, self._now_ms)
            if batch:
                out.append((stream, [(mid, f) for mid, f in batch]))
        return out

    def xack(self, stream, group, *message_ids):
        pel = self._pel.setdefault((stream, group), {})
        n = 0
        for message_id in message_ids:
            if pel.pop(message_id, None) is not None:
                n += 1
        return n

    def xpending(self, stream, group, *, min_idle_ms=0):
        pel = self._pel.get((stream, group), {})
        return [
            PendingEntry(
                message_id=mid,
                consumer=consumer,
                deliveries=deliveries,
                idle_ms=int(self._now_ms - last_ms),
            )
            for mid, (consumer, deliveries, last_ms) in sorted(pel.items())
            if self._now_ms - last_ms >= min_idle_ms
        ]


def _queue(
    clock: _Clock | None = None,
    dlq: list | None = None,
    **kwargs,
) -> tuple[RedisStreamMessageQueue, _FakeStreamClient, _Clock]:
    clock = clock or _Clock()
    client = _FakeStreamClient()
    q = RedisStreamMessageQueue(
        client=client,
        clock=clock,
        dlq_sink=(lambda m: dlq.append(m)) if dlq is not None else None,
        pending_timeout_ms=kwargs.pop("pending_timeout_ms", 5_000),
        **kwargs,
    )
    return q, client, clock


# ──────────────────────────────────────────────────────────────────────────────
# 路由表绑定
# ──────────────────────────────────────────────────────────────────────────────


class TestBind:
    def test_bind_inproc_ok(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        assert q.channel_of("news") is Channel.INPROC
        assert q.topics() == ("news",)

    def test_bind_stream_ok(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        assert q.channel_of("ticks") is Channel.STREAM

    def test_bind_invalid_args_raise(self) -> None:
        q, _, _ = _queue()
        with pytest.raises(RedisStreamQueueError):
            q.bind("", Channel.INPROC)  # 空 topic
        with pytest.raises(RedisStreamQueueError):
            q.bind("t", "kafka")  # type: ignore[arg-type]  # 词表外通道

    def test_bind_conflicting_channel_raises(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        with pytest.raises(RedisStreamQueueError):
            q.bind("news", Channel.STREAM)  # inproc→stream 改绑拒绝

    def test_bind_stream_without_client_fail_closed(self) -> None:
        q = RedisStreamMessageQueue(clock=lambda: _T0)  # 未注入客户端
        with pytest.raises(RedisStreamQueueError):
            q.bind("ticks", Channel.STREAM)

    def test_ctor_invalid_args_raise(self) -> None:
        with pytest.raises(RedisStreamQueueError):
            RedisStreamMessageQueue(group="")
        with pytest.raises(RedisStreamQueueError):
            RedisStreamMessageQueue(max_deliveries=0)
        with pytest.raises(RedisStreamQueueError):
            RedisStreamMessageQueue(pending_timeout_ms=-1)


# ──────────────────────────────────────────────────────────────────────────────
# 进程内快路径
# ──────────────────────────────────────────────────────────────────────────────


class TestInprocChannel:
    def test_publish_consume_fifo(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        id1 = q.publish("news", {"n": 1})
        id2 = q.publish("news", {"n": 2})
        assert (id1, id2) == ("news-inproc-1", "news-inproc-2")  # 确定性 id
        out = q.consume_inproc("news")
        assert [m.payload for m in out] == [{"n": 1}, {"n": 2}]
        assert q.consume_inproc("news") == []  # 已弹空

    def test_consume_max_count(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        for i in range(3):
            q.publish("news", {"n": i})
        out = q.consume_inproc("news", max_count=2)
        assert [m.payload["n"] for m in out] == [0, 1]
        assert len(q.consume_inproc("news")) == 1

    def test_publish_unbound_topic_raises(self) -> None:
        q, _, _ = _queue()
        with pytest.raises(RedisStreamQueueError):
            q.publish("ghost", {"n": 1})

    def test_publish_invalid_payload_raises(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        with pytest.raises(RedisStreamQueueError):
            q.publish("news", ["not-a-mapping"])  # type: ignore[arg-type]
        with pytest.raises(RedisStreamQueueError):
            q.publish("news", {"bad": object()})  # 不可 JSON 序列化

    def test_consume_invalid_args_raise(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        with pytest.raises(RedisStreamQueueError):
            q.consume_inproc("news", max_count=0)
        with pytest.raises(RedisStreamQueueError):
            q.consume_inproc("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# stream 通道（xadd/xreadgroup）
# ──────────────────────────────────────────────────────────────────────────────


class TestStreamChannel:
    def test_publish_poll_roundtrip(self) -> None:
        q, client, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        message_id = q.publish("ticks", {"px": 10.5})
        assert message_id == "1-0"
        assert "za:stream:ticks" in client._streams  # 确定性 stream 键
        got = q.poll("ticks")
        assert len(got) == 1
        assert got[0].message_id == "1-0"
        assert got[0].payload == {"px": 10.5}
        assert got[0].enqueued_at == _T0
        assert q.pending_count() == 1

    def test_poll_drains_then_empty(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q.publish("ticks", {"n": 2})
        assert len(q.poll("ticks", count=5)) == 2
        assert q.poll("ticks") == []  # 消费组游标已推进

    def test_poll_channel_mismatch_raises(self) -> None:
        q, _, _ = _queue()
        q.bind("news", Channel.INPROC)
        with pytest.raises(RedisStreamQueueError):
            q.poll("news")  # inproc 主题走 stream 拉取
        q2, _, _ = _queue()
        q2.bind("ticks", Channel.STREAM)
        with pytest.raises(RedisStreamQueueError):
            q2.consume_inproc("ticks")  # stream 主题走快路径

    def test_poll_invalid_count_raises(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        with pytest.raises(RedisStreamQueueError):
            q.poll("ticks", count=0)

    def test_stream_ops_without_client_fail_closed(self) -> None:
        clock = _Clock()
        client = _FakeStreamClient()
        q = RedisStreamMessageQueue(client=client, clock=clock)
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q_no_client = RedisStreamMessageQueue(clock=clock)
        q_no_client._routes["ticks"] = Channel.STREAM  # 模拟装配态丢失客户端
        with pytest.raises(RedisStreamQueueError):
            q_no_client.publish("ticks", {"n": 2})
        with pytest.raises(RedisStreamQueueError):
            q_no_client.poll("ticks")


# ──────────────────────────────────────────────────────────────────────────────
# ACK / pending / 重投 / DLQ
# ──────────────────────────────────────────────────────────────────────────────


class TestAckRetryDlq:
    def test_ack_removes_pending(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        mid = q.publish("ticks", {"n": 1})
        q.poll("ticks")
        q.ack(mid)
        assert q.pending_count() == 0
        assert q.pending_view("ticks") == ()  # 服务端 PEL 同步清空

    def test_ack_unknown_id_raises(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        with pytest.raises(RedisStreamQueueError):
            q.ack("ghost-0")

    def test_pending_view_reflects_server(self) -> None:
        q, _, _ = _queue()
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q.publish("ticks", {"n": 2})
        q.poll("ticks")
        view = q.pending_view("ticks")
        assert [e.message_id for e in view] == ["1-0", "2-0"]  # 确定性排序
        assert all(e.deliveries == 1 for e in view)

    def test_redeliver_stale_pending(self) -> None:
        clock = _Clock()
        q, _, _ = _queue(clock=clock)
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q.poll("ticks")
        clock.advance(4.0)  # 未超 5000ms 超时
        report = q.collect_redeliveries()
        assert report.redelivered == ()
        clock.advance(2.0)  # 累计 6s 超期
        report = q.collect_redeliveries()
        assert [m.message_id for m in report.redelivered] == ["1-0"]
        assert report.dead_lettered == ()

    def test_exceed_max_deliveries_goes_dlq(self) -> None:
        clock = _Clock()
        dlq: list[QueueMessage] = []
        q, _, _ = _queue(clock=clock, dlq=dlq, max_deliveries=2, pending_timeout_ms=1_000)
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q.poll("ticks")  # deliveries=1
        clock.advance(2.0)
        q.collect_redeliveries()  # deliveries=2（重投）
        clock.advance(2.0)
        report = q.collect_redeliveries()  # deliveries=3 > 2 → DLQ
        assert [m.message_id for m in report.dead_lettered] == ["1-0"]
        assert len(dlq) == 1 and dlq[0].payload == {"n": 1}
        assert q.pending_count() == 0
        assert q.pending_view("ticks") == ()  # 死信已 xack 出 PEL

    def test_dlq_without_sink_fail_closed(self) -> None:
        clock = _Clock()
        q, _, _ = _queue(clock=clock, max_deliveries=1, pending_timeout_ms=1_000)
        q.bind("ticks", Channel.STREAM)
        q.publish("ticks", {"n": 1})
        q.poll("ticks")
        clock.advance(2.0)
        with pytest.raises(RedisStreamQueueError):
            q.collect_redeliveries()  # 超上限且无 dlq_sink

    def test_acked_message_not_redelivered(self) -> None:
        clock = _Clock()
        q, _, _ = _queue(clock=clock, pending_timeout_ms=1_000)
        q.bind("ticks", Channel.STREAM)
        mid = q.publish("ticks", {"n": 1})
        q.poll("ticks")
        q.ack(mid)
        clock.advance(10.0)
        report = q.collect_redeliveries()
        assert report.redelivered == () and report.dead_lettered == ()


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            clock = _Clock()
            dlq: list[QueueMessage] = []
            q, _, _ = _queue(clock=clock, dlq=dlq, max_deliveries=1, pending_timeout_ms=1_000)
            q.bind("ticks", Channel.STREAM)
            q.bind("news", Channel.INPROC)
            m1 = q.publish("ticks", {"b": 2, "a": 1})
            m2 = q.publish("news", {"n": 1})
            polled = q.poll("ticks")
            clock.advance(2.0)
            report = q.collect_redeliveries()
            return (m1, m2, tuple(polled), report, tuple(dlq))

        assert _run() == _run()

    def test_topics_sorted(self) -> None:
        q, _, _ = _queue()
        for topic in ("zeta", "alpha", "mid"):
            q.bind(topic, Channel.INPROC)
        assert q.topics() == ("alpha", "mid", "zeta")
