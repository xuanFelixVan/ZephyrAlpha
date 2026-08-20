# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_alert_senders
# [DOMAIN] D_SHARED
# [INVARIANTS] 默认不启用; best-effort(False不抛); 传输注入零网络; 凭据不出现在异常/日志路径
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""Email/WeChat 实发 sender 测试（55 号 §6 暂缓项，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import Enum

import pytest

from zephyr.shared.alerts.alert_senders import EmailSmtpSender, WeChatWebhookSender


class _FakeLevel(Enum):
    RED = "red"


class _FakeAlert:
    def __init__(self, level=_FakeLevel.RED, source="tail_risk", message="回撤超阈"):
        self.level = level
        self.source = source
        self.message = message
        self.timestamp = datetime(2026, 8, 20, 15, 30, tzinfo=UTC)


class _FakeResponse:
    def __init__(self, status: int = 200, errcode: int = 0):
        self.status = status
        self._payload = json.dumps({"errcode": errcode}).encode("utf-8")

    def read(self) -> bytes:
        return self._payload


class TestWeChatWebhookSender:
    def test_send_success(self):
        seen: dict = {}
        sender = WeChatWebhookSender(
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=TESTKEY",
            http_post=lambda url, body, timeout: seen.update(url=url, body=body) or _FakeResponse(),
        )
        assert sender.send_markdown("**test**") is True
        payload = json.loads(seen["body"].decode("utf-8"))
        assert payload["msgtype"] == "markdown"
        assert payload["markdown"]["content"] == "**test**"

    def test_send_errcode_nonzero_soft_fail(self):
        sender = WeChatWebhookSender(
            "https://example.invalid/hook?key=K",
            http_post=lambda url, body, timeout: _FakeResponse(errcode=93000),
        )
        assert sender.send_markdown("x") is False

    def test_send_http_500_soft_fail(self):
        sender = WeChatWebhookSender(
            "https://example.invalid/hook?key=K",
            http_post=lambda url, body, timeout: _FakeResponse(status=500),
        )
        assert sender.send_markdown("x") is False

    def test_send_exception_soft_fail(self):
        def _boom(url, body, timeout):
            raise ConnectionError("network down")

        sender = WeChatWebhookSender("https://example.invalid/hook?key=K", http_post=_boom)
        assert sender.send_markdown("x") is False

    def test_empty_content_rejected(self):
        sender = WeChatWebhookSender(
            "https://example.invalid/hook?key=K",
            http_post=lambda url, body, timeout: _FakeResponse(),
        )
        assert sender.send_markdown("   ") is False

    def test_empty_url_rejected_at_construction(self):
        with pytest.raises(ValueError):
            WeChatWebhookSender("")

    def test_alert_facade_formats_markdown(self):
        seen: dict = {}
        sender = WeChatWebhookSender(
            "https://example.invalid/hook?key=K",
            http_post=lambda url, body, timeout: seen.update(body=body) or _FakeResponse(),
        )
        assert sender.as_alert_sender()(_FakeAlert()) is True
        payload = json.loads(seen["body"].decode("utf-8"))
        assert "[告警:RED] tail_risk" in payload["markdown"]["content"]
        assert "回撤超阈" in payload["markdown"]["content"]

    def test_report_facade(self):
        seen: dict = {}

        class _FakeReport:
            report_id = "RPT-001"
            report_type = "daily_risk"
            content_hash = "abcdef0123456789"

            class source(Enum):
                RISK = "risk"

        sender = WeChatWebhookSender(
            "https://example.invalid/hook?key=K",
            http_post=lambda url, body, timeout: seen.update(body=body) or _FakeResponse(),
        )
        assert sender.as_report_sender()(_FakeReport()) is True
        payload = json.loads(seen["body"].decode("utf-8"))
        assert "RPT-001" in payload["markdown"]["content"]


class _FakeSmtp:
    instances: list[_FakeSmtp] = []

    def __init__(self, host, port, timeout):
        self.host, self.port, self.timeout = host, port, timeout
        self.logged_in: tuple | None = None
        self.sent: list[tuple] = []
        self.quit_called = False
        self.fail_on: str | None = None
        _FakeSmtp.instances.append(self)

    def login(self, user, password):
        if self.fail_on == "login":
            raise ConnectionError("auth refused")
        self.logged_in = (user, password)

    def sendmail(self, from_addr, to_addrs, msg):
        if self.fail_on == "sendmail":
            raise ConnectionError("smtp reset")
        self.sent.append((from_addr, to_addrs, msg))

    def quit(self):
        self.quit_called = True


class TestEmailSmtpSender:
    def setup_method(self):
        _FakeSmtp.instances = []

    def _make(self, **kw) -> EmailSmtpSender:
        return EmailSmtpSender(
            host="smtp.example.com",
            port=465,
            username="bot@example.com",
            password="secret",  # noqa: S106 —— 测试占位凭据，零网络
            from_addr="bot@example.com",
            to_addrs=["owner@example.com"],
            smtp_factory=lambda h, p, t: _FakeSmtp(h, p, t),
            **kw,
        )

    def test_send_success(self):
        sender = self._make()
        assert sender.send_mail("subj", "body") is True
        conn = _FakeSmtp.instances[0]
        assert conn.logged_in == ("bot@example.com", "secret")
        assert conn.sent and "owner@example.com" in conn.sent[0][1]
        assert "subj" in conn.sent[0][2]
        assert conn.quit_called is True

    def test_login_failure_soft_fail_and_quit(self):
        sender = self._make()
        sender.send_mail("s", "b")
        _FakeSmtp.instances.clear()
        conn_holder: list[_FakeSmtp] = []

        def _factory(h, p, t):
            conn = _FakeSmtp(h, p, t)
            conn.fail_on = "login"
            conn_holder.append(conn)
            return conn

        sender = EmailSmtpSender(
            host="h", port=1, username="u", password="p",  # noqa: S106
            from_addr="f", to_addrs=["t"], smtp_factory=_factory,
        )
        assert sender.send_mail("s", "b") is False
        assert conn_holder[0].quit_called is True

    def test_sendmail_failure_soft_fail(self):
        def _factory(h, p, t):
            conn = _FakeSmtp(h, p, t)
            conn.fail_on = "sendmail"
            return conn

        sender = EmailSmtpSender(
            host="h", port=1, username="u", password="p",  # noqa: S106
            from_addr="f", to_addrs=["t"], smtp_factory=_factory,
        )
        assert sender.send_mail("s", "b") is False

    def test_empty_subject_rejected(self):
        assert self._make().send_mail("  ", "body") is False

    def test_empty_host_or_recipients_rejected(self):
        with pytest.raises(ValueError):
            EmailSmtpSender(host="", port=1, username="u", password="p", from_addr="f", to_addrs=["t"])  # noqa: S106
        with pytest.raises(ValueError):
            EmailSmtpSender(host="h", port=1, username="u", password="p", from_addr="f", to_addrs=[])  # noqa: S106

    def test_alert_facade(self):
        sender = self._make()
        assert sender.as_alert_sender()(_FakeAlert()) is True
        msg = _FakeSmtp.instances[0].sent[0][2]
        assert "[ZephyrAlert:RED] tail_risk" in msg

    def test_report_facade(self):
        class _FakeReport:
            report_id = "RPT-002"
            report_type = "weekly_review"
            archive_id = "ARCH-x1"
            archived_at = "2026-08-20T15:30:00"
            content_hash = "hash"
            content = {"k": "v"}

            class source(Enum):
                TRADING_REVIEW = "trading_review"

        sender = self._make()
        assert sender.as_report_sender()(_FakeReport()) is True
        msg = _FakeSmtp.instances[0].sent[0][2]
        # 主题为 ASCII 不被 base64 编码；正文含中文被编码，故断言走主题头
        assert "Subject: [ZephyrReport] RPT-002 (weekly_review)" in msg
