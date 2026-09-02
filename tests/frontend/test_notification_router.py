# [BLUEPRINT] MOD-FE-004 | docs/03_modules/_domain_frontend/notification_router/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.frontend.test_notification_router
# [TESTS] src/zephyr/frontend/notification_router.py
"""MOD-FE-004 单元测试：notification_router 通知路由器。

蓝图验收（B1-00138/CAND-FE-004，C2 D-FE-13）：严重级→通道路由表 +
通道适配（发送器注入，密钥仅 secrets 引用不落地）+ 静默时段（注入时钟，
critical 不静默）+ 超时未 ack 升级更严重通道（单次不循环）+ 投递 best-effort。
发送器/时钟全内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.frontend.notification_router",
    reason="notification_router not importable",
)

from zephyr.frontend.notification_router import (  # noqa: E402
    ChannelBinding,
    Notification,
    NotificationChannel,
    NotificationRouter,
    NotificationRouterError,
    Severity,
    SilentWindow,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_ACK_TIMEOUT = datetime.timedelta(minutes=5)


class _Clock:
    """可推进内存时钟。"""

    def __init__(self, t: datetime.datetime = _T0) -> None:
        self.t = t

    def __call__(self) -> datetime.datetime:
        return self.t

    def advance(self, **kwargs) -> None:
        self.t = self.t + datetime.timedelta(**kwargs)


def _binding(channel: NotificationChannel, sent: list, ok: bool = True) -> ChannelBinding:
    return ChannelBinding(
        channel=channel,
        secret_ref=f"secrets://notification/{channel.value}",
        sender=lambda n, b: sent.append((b.channel, n)) or ok,
    )


def _router(
    sent: list | None = None,
    clock: _Clock | None = None,
    silent=(),
    esc: dict | None | object = ...,  # ...=默认升级表, None=无升级表
    ok: bool = True,
) -> tuple[NotificationRouter, list]:
    sent = sent if sent is not None else []
    bindings = {ch: _binding(ch, sent, ok) for ch in NotificationChannel}
    route = {
        Severity.INFO: (NotificationChannel.FEISHU,),
        Severity.WARNING: (NotificationChannel.WECOM,),
        Severity.CRITICAL: (NotificationChannel.WECOM, NotificationChannel.FEISHU),
    }
    if esc is ...:
        esc = {
            Severity.INFO: (NotificationChannel.WECOM,),
            Severity.WARNING: (NotificationChannel.WECOM, NotificationChannel.FEISHU),
            Severity.CRITICAL: (NotificationChannel.WECOM, NotificationChannel.FEISHU),
        }
    router = NotificationRouter(
        route_table=route,
        bindings=bindings,
        escalation_table=esc,
        silent_windows=silent,
        clock=clock or _Clock(),
        ack_timeout=_ACK_TIMEOUT,
    )
    return router, sent


def _notification(severity: Severity = Severity.WARNING, **kwargs) -> Notification:
    payload = {"title": "风控告警", "content": "回撤超阈", "severity": severity, "source": "alert_manager"}
    payload.update(kwargs)
    return Notification(**payload)


# ──────────────────────────────────────────────────────────────────────────────
# 构造配置（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConfig:
    def test_empty_route_table_raises(self) -> None:
        with pytest.raises(NotificationRouterError):
            NotificationRouter(
                route_table={}, bindings={NotificationChannel.WECOM: _binding(NotificationChannel.WECOM, [])}
            )

    def test_route_channel_without_binding_raises(self) -> None:
        with pytest.raises(NotificationRouterError):
            NotificationRouter(
                route_table={Severity.WARNING: (NotificationChannel.FEISHU,)},
                bindings={NotificationChannel.WECOM: _binding(NotificationChannel.WECOM, [])},
            )

    def test_plaintext_secret_ref_raises(self) -> None:
        bad = ChannelBinding(
            channel=NotificationChannel.WECOM,
            secret_ref="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=abc",
            sender=lambda n, b: True,
        )
        with pytest.raises(NotificationRouterError):
            NotificationRouter(
                route_table={Severity.WARNING: (NotificationChannel.WECOM,)},
                bindings={NotificationChannel.WECOM: bad},
            )

    def test_invalid_severity_route_raises(self) -> None:
        with pytest.raises(NotificationRouterError):
            NotificationRouter(
                route_table={"p1": (NotificationChannel.WECOM,)},
                bindings={NotificationChannel.WECOM: _binding(NotificationChannel.WECOM, [])},
            )

    def test_invalid_silent_window_raises(self) -> None:
        with pytest.raises(NotificationRouterError):
            _router(silent=(SilentWindow(0, 1440),))

    def test_non_positive_ack_timeout_raises(self) -> None:
        with pytest.raises(NotificationRouterError):
            NotificationRouter(
                route_table={Severity.WARNING: (NotificationChannel.WECOM,)},
                bindings={NotificationChannel.WECOM: _binding(NotificationChannel.WECOM, [])},
                ack_timeout=datetime.timedelta(0),
            )


# ──────────────────────────────────────────────────────────────────────────────
# 路由投递
# ──────────────────────────────────────────────────────────────────────────────


class TestNotify:
    def test_notify_ok_multi_channel(self) -> None:
        router, sent = _router()
        decision = router.notify(_notification(Severity.CRITICAL))
        assert decision.suppressed is False
        assert decision.channels == (NotificationChannel.WECOM, NotificationChannel.FEISHU)
        assert [d.channel for d in decision.deliveries] == list(decision.channels)
        assert all(d.ok for d in decision.deliveries)
        assert [c for c, _ in sent] == [NotificationChannel.WECOM, NotificationChannel.FEISHU]

    def test_deterministic_notification_ids(self) -> None:
        router, _ = _router()
        d1 = router.notify(_notification(Severity.INFO))
        d2 = router.notify(_notification(Severity.INFO))
        assert (d1.notification_id, d2.notification_id) == ("ntf-000000", "ntf-000001")

    def test_invalid_severity_raises(self) -> None:
        router, _ = _router()
        with pytest.raises(NotificationRouterError):
            router.notify(_notification(severity="p1"))

    def test_empty_title_raises(self) -> None:
        router, _ = _router()
        with pytest.raises(NotificationRouterError):
            router.notify(_notification(title=""))

    def test_sender_exception_best_effort(self) -> None:
        def _boom(n, b):
            raise RuntimeError("webhook down")

        bindings = {
            NotificationChannel.WECOM: ChannelBinding(
                channel=NotificationChannel.WECOM,
                secret_ref="secrets://notification/wecom",
                sender=_boom,
            )
        }
        router = NotificationRouter(
            route_table={Severity.WARNING: (NotificationChannel.WECOM,)},
            bindings=bindings,
            clock=_Clock(),
        )
        decision = router.notify(_notification())
        assert decision.deliveries[0].ok is False
        assert decision.deliveries[0].detail == "sender_exception"
        assert router.pending_acks() == (decision.notification_id,)  # 不阻断仍入待确认


# ──────────────────────────────────────────────────────────────────────────────
# 静默时段
# ──────────────────────────────────────────────────────────────────────────────


class TestSilent:
    _NIGHT = (SilentWindow(22 * 60, 6 * 60),)  # 22:00–06:00 跨午夜

    def test_info_suppressed_in_silent_window(self) -> None:
        clock = _Clock(datetime.datetime(2026, 8, 26, 23, 0, 0))
        router, sent = _router(clock=clock, silent=self._NIGHT)
        decision = router.notify(_notification(Severity.INFO))
        assert decision.suppressed is True
        assert decision.deliveries == ()
        assert sent == []
        assert len(router.suppressed()) == 1
        assert router.pending_acks() == ()  # 抑制件不入待确认

    def test_critical_not_silenced(self) -> None:
        clock = _Clock(datetime.datetime(2026, 8, 26, 23, 0, 0))
        router, sent = _router(clock=clock, silent=self._NIGHT)
        decision = router.notify(_notification(Severity.CRITICAL))
        assert decision.suppressed is False
        assert len(sent) == 2

    def test_wraparound_window_boundary(self) -> None:
        router_day, sent_day = _router(clock=_Clock(datetime.datetime(2026, 8, 26, 12, 0, 0)), silent=self._NIGHT)
        assert router_day.notify(_notification(Severity.INFO)).suppressed is False
        assert len(sent_day) == 1
        router_dawn, sent_dawn = _router(clock=_Clock(datetime.datetime(2026, 8, 26, 5, 30, 0)), silent=self._NIGHT)
        assert router_dawn.notify(_notification(Severity.WARNING)).suppressed is True
        assert sent_dawn == []


# ──────────────────────────────────────────────────────────────────────────────
# 确认 / 未确认升级
# ──────────────────────────────────────────────────────────────────────────────


class TestAckEscalation:
    def test_ack_ok_clears_pending(self) -> None:
        router, _ = _router()
        decision = router.notify(_notification())
        assert router.ack(decision.notification_id) is True
        assert router.pending_acks() == ()

    def test_ack_unknown_raises(self) -> None:
        router, _ = _router()
        with pytest.raises(NotificationRouterError):
            router.ack("ntf-999999")

    def test_ack_duplicate_returns_false(self) -> None:
        router, _ = _router()
        decision = router.notify(_notification())
        assert router.ack(decision.notification_id) is True
        assert router.ack(decision.notification_id) is False

    def test_escalation_after_timeout(self) -> None:
        clock = _Clock()
        router, sent = _router(clock=clock)
        decision = router.notify(_notification(Severity.INFO))
        assert [c for c, _ in sent] == [NotificationChannel.FEISHU]
        clock.advance(minutes=6)  # 超过 ack_timeout=5min
        records = router.check_escalations()
        assert len(records) == 1
        assert records[0].notification_id == decision.notification_id
        assert records[0].channels == (NotificationChannel.WECOM,)  # 升级更严重通道
        assert all(d.escalated for d in records[0].deliveries)

    def test_no_escalation_before_deadline(self) -> None:
        clock = _Clock()
        router, _ = _router(clock=clock)
        router.notify(_notification())
        clock.advance(minutes=4)
        assert router.check_escalations() == ()

    def test_escalation_single_shot(self) -> None:
        clock = _Clock()
        router, _ = _router(clock=clock)
        router.notify(_notification())
        clock.advance(minutes=10)
        assert len(router.check_escalations()) == 1
        clock.advance(minutes=60)
        assert router.check_escalations() == ()  # 单次升级不循环

    def test_acked_notification_not_escalated(self) -> None:
        clock = _Clock()
        router, _ = _router(clock=clock)
        decision = router.notify(_notification())
        router.ack(decision.notification_id)
        clock.advance(minutes=10)
        assert router.check_escalations() == ()

    def test_escalation_without_table_marks_only(self) -> None:
        clock = _Clock()
        router, sent = _router(clock=clock, esc=None)
        router.notify(_notification())
        clock.advance(minutes=10)
        before = len(sent)
        assert router.check_escalations() == ()
        assert len(sent) == before  # 无升级通道不再投递
        assert router.check_escalations() == ()


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        r1, s1 = _router()
        r2, s2 = _router()
        for sev in (Severity.INFO, Severity.WARNING, Severity.CRITICAL):
            d1 = r1.notify(_notification(sev))
            d2 = r2.notify(_notification(sev))
            assert d1 == d2
        assert s1 == s2
        assert r1.history() == r2.history()
