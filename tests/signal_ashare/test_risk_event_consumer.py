# [BLUEPRINT] MOD-SIG-088 | docs/03_modules/_domain_signal/risk_event_consumer/blueprint.md
# [MODULE] tests.signal_ashare.test_risk_event_consumer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.risk_event_consumer
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存判定核心测试，stream_client/action_handler/dlq_sink 注入式内存 stub，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=幂等去重/DLQ兜底/回执/滞后监控逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""RiskEventConsumer 单元测试（CAND-TESTB-028 / B14-04728，D-SIGNAL-99 E-RK-01）。

覆盖（min_build_spec）：
- Redis Streams 消费组语义订阅风险事件（client 注入式）
- 幂等键去重：重复事件产 deduped 回执且不重复处置
- DLQ 兜底：解析失败/处置异常进 dlq_sink，不阻断后续事件
- 触发信号降级/撤销/权重调整（action_handler 委托）并回执
- 消费滞后监控：lag 超阈值标记 lag_exceeded，last_lag_seconds 可查
"""

from __future__ import annotations

import datetime

import pytest

from zephyr.signal_ashare.risk_event_consumer import (
    RiskAction,
    RiskEvent,
    RiskEventConsumer,
    RiskEventConsumerError,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, tzinfo=datetime.timezone.utc)


def _event(
    event_id: str = "rk-001",
    key: str = "idem-001",
    action: str = "degrade",
    occurred_at: datetime.datetime = _T0,
) -> RiskEvent:
    return RiskEvent(
        event_id=event_id,
        event_type="E-RK-01",
        occurred_at=occurred_at,
        payload={"action": action, "signal_id": "sig-1", "weight": 0.5},
        idempotency_key=key,
    )


class _StubStreamClient:
    """内存流 stub：实现 Redis Streams XREADGROUP 最小语义。"""

    def __init__(self, events: list[RiskEvent]) -> None:
        self._events = list(events)

    def read_group(self, *, group: str, consumer: str, max_events: int) -> list[RiskEvent]:
        out, self._events = self._events[:max_events], self._events[max_events:]
        return out


class TestDispatch:
    """风险事件→信号处置委托。"""

    def test_degrade_dispatched_to_action_handler(self) -> None:
        calls: list[tuple] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event()]),
            action_handler=lambda action, payload: calls.append((action, payload)) or True,
        )
        receipts = consumer.poll_once()
        assert len(receipts) == 1
        assert receipts[0].applied is True
        assert receipts[0].action == RiskAction.DEGRADE
        assert calls == [(RiskAction.DEGRADE, {"action": "degrade", "signal_id": "sig-1", "weight": 0.5})]

    def test_revoke_and_reweight_actions(self) -> None:
        calls: list[tuple] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event("e1", "k1", "revoke"), _event("e2", "k2", "reweight")]),
            action_handler=lambda action, payload: calls.append(action) or True,
        )
        receipts = consumer.poll_once()
        assert [r.action for r in receipts] == [RiskAction.REVOKE, RiskAction.REWEIGHT]
        assert calls == [RiskAction.REVOKE, RiskAction.REWEIGHT]

    def test_unknown_action_goes_to_dlq(self) -> None:
        dlq: list[dict] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event(action="explode")]),
            action_handler=lambda action, payload: True,
            dlq_sink=dlq.append,
        )
        receipts = consumer.poll_once()
        assert receipts[0].applied is False
        assert "explode" in receipts[0].reason
        assert len(dlq) == 1
        assert dlq[0]["event_id"] == "rk-001"

    def test_action_handler_exception_goes_to_dlq_and_continues(self) -> None:
        dlq: list[dict] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event("e1", "k1"), _event("e2", "k2")]),
            action_handler=_raise_on_first(),
            dlq_sink=dlq.append,
        )
        receipts = consumer.poll_once()
        assert receipts[0].applied is False
        assert receipts[1].applied is True  # 后续事件不被阻断
        assert len(dlq) == 1

    def test_handler_false_counts_as_not_applied_but_no_dlq(self) -> None:
        dlq: list[dict] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event()]),
            action_handler=lambda action, payload: False,
            dlq_sink=dlq.append,
        )
        receipts = consumer.poll_once()
        assert receipts[0].applied is False
        assert dlq == []  # 业务拒绝≠异常，不进 DLQ


def _raise_on_first():
    state = {"n": 0}

    def _handler(action: RiskAction, payload: dict) -> bool:
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("handler boom")
        return True

    return _handler


class TestIdempotency:
    """幂等键去重。"""

    def test_duplicate_idempotency_key_deduped(self) -> None:
        calls: list[tuple] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event("e1", "same-key"), _event("e2", "same-key")]),
            action_handler=lambda action, payload: calls.append(payload) or True,
        )
        receipts = consumer.poll_once()
        assert receipts[0].deduped is False
        assert receipts[1].deduped is True
        assert receipts[1].applied is False
        assert len(calls) == 1  # 不重复处置
        assert consumer.seen_count == 2

    def test_dedup_window_bounded(self) -> None:
        events = [_event(f"e{i}", f"k{i}") for i in range(5)]
        consumer = RiskEventConsumer(
            _StubStreamClient(events),
            action_handler=lambda action, payload: True,
            dedup_window=3,
        )
        consumer.poll_once(max_events=5)
        # 窗口=3：最早 2 个键已滑出，同键重放不再判重
        consumer2_client = _StubStreamClient([_event("eX", "k0")])
        consumer._client = consumer2_client
        receipts = consumer.poll_once()
        assert receipts[0].deduped is False


class TestReceiptAndLag:
    """回执与滞后监控。"""

    def test_ack_hook_receives_receipt(self) -> None:
        acks: list[object] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([_event()]),
            action_handler=lambda action, payload: True,
            ack_hook=acks.append,
        )
        consumer.poll_once()
        assert len(acks) == 1
        assert acks[0].event_id == "rk-001"

    def test_lag_exceeded_flagged(self) -> None:
        now = _T0 + datetime.timedelta(seconds=120)
        consumer = RiskEventConsumer(
            _StubStreamClient([_event()]),
            action_handler=lambda action, payload: True,
            lag_warn_seconds=30.0,
            clock=lambda: now,
        )
        receipts = consumer.poll_once()
        assert receipts[0].lag_seconds == pytest.approx(120.0)
        assert receipts[0].lag_exceeded is True
        assert consumer.last_lag_seconds == pytest.approx(120.0)

    def test_lag_within_threshold_not_flagged(self) -> None:
        now = _T0 + datetime.timedelta(seconds=5)
        consumer = RiskEventConsumer(
            _StubStreamClient([_event()]),
            action_handler=lambda action, payload: True,
            lag_warn_seconds=30.0,
            clock=lambda: now,
        )
        receipts = consumer.poll_once()
        assert receipts[0].lag_exceeded is False

    def test_empty_poll_returns_empty(self) -> None:
        consumer = RiskEventConsumer(_StubStreamClient([]), action_handler=lambda a, p: True)
        assert consumer.poll_once() == []
        assert consumer.dlq_count == 0

    def test_dlq_sink_failure_does_not_block(self) -> None:
        def _boom(_rec: dict) -> None:
            raise RuntimeError("dlq down")

        consumer = RiskEventConsumer(
            _StubStreamClient([_event(action="bad"), _event("e2", "k2")]),
            action_handler=lambda action, payload: True,
            dlq_sink=_boom,
        )
        receipts = consumer.poll_once()
        assert receipts[0].applied is False
        assert receipts[1].applied is True
        assert consumer.dlq_count == 1  # 计数仍在

    def test_invalid_event_type_rejected(self) -> None:
        bad = RiskEvent(
            event_id="x",
            event_type="E-OTHER",
            occurred_at=_T0,
            payload={"action": "degrade"},
            idempotency_key="kx",
        )
        dlq: list[dict] = []
        consumer = RiskEventConsumer(
            _StubStreamClient([bad]),
            action_handler=lambda action, payload: True,
            dlq_sink=dlq.append,
        )
        receipts = consumer.poll_once()
        assert receipts[0].applied is False
        assert "E-OTHER" in receipts[0].reason
        assert len(dlq) == 1

    def test_client_type_error_raises_consumer_error(self) -> None:
        consumer = RiskEventConsumer(object(), action_handler=lambda a, p: True)  # type: ignore[arg-type]
        with pytest.raises(RiskEventConsumerError):
            consumer.poll_once()
