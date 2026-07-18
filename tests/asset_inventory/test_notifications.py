# [A_test] module_id: SRC-TST-0078 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-236 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_notifications
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §36 Notifications module."""

from unittest.mock import MagicMock, patch

from zephyr.infrastructure.asset_inventory.telemetry import (
    ConsoleChannel,
    FeishuWebhook,
    NotificationManager,
    NotificationRecord,
    SmtpEmailChannel,
)


class TestConsoleChannel:
    def test_channel_name(self) -> None:
        ch = ConsoleChannel()
        assert ch.channel_name == "console"

    def test_send_returns_record(self) -> None:
        ch = ConsoleChannel()
        record = ch.send("passive", "test message")
        assert isinstance(record, NotificationRecord)
        assert record.delivered
        assert record.message == "test message"


class TestFeishuWebhook:
    def test_channel_name(self) -> None:
        ch = FeishuWebhook()
        assert ch.channel_name == "feishu"

    def test_send_no_url_returns_not_delivered(self) -> None:
        ch = FeishuWebhook(webhook_url="")
        record = ch.send("semi_active", "test")
        assert not record.delivered

    @patch("zephyr.infrastructure.asset_inventory.telemetry._urlopen")
    def test_send_with_url_success(self, mock_urlopen) -> None:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        ch = FeishuWebhook(webhook_url="https://example.com/webhook")
        record = ch.send("semi_active", "test alert")
        assert record.delivered

    @patch("zephyr.infrastructure.asset_inventory.telemetry._urlopen")
    def test_send_with_url_failure(self, mock_urlopen) -> None:
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("connection refused")

        ch = FeishuWebhook(webhook_url="https://example.com/webhook")
        record = ch.send("semi_active", "test alert")
        assert not record.delivered


class TestSmtpEmailChannel:
    def test_channel_name(self) -> None:
        ch = SmtpEmailChannel()
        assert ch.channel_name == "email"

    def test_send_no_config_returns_not_delivered(self) -> None:
        ch = SmtpEmailChannel(smtp_host="", to_addrs=[])
        record = ch.send("semi_active", "test")
        assert not record.delivered

    @patch("zephyr.infrastructure.asset_inventory.telemetry._smtplib.SMTP")
    def test_send_with_config_success(self, mock_smtp_cls) -> None:
        mock_server = MagicMock()
        mock_smtp_cls.return_value = mock_server

        ch = SmtpEmailChannel(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="pass",
            from_addr="from@example.com",
            to_addrs=["to@example.com"],
            use_tls=True,
        )
        record = ch.send("blocking", "critical alert")
        assert record.delivered
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("zephyr.infrastructure.asset_inventory.telemetry._smtplib.SMTP")
    def test_send_smtp_exception_returns_not_delivered(self, mock_smtp_cls) -> None:
        mock_smtp_cls.side_effect = Exception("SMTP error")

        ch = SmtpEmailChannel(
            smtp_host="smtp.example.com",
            to_addrs=["to@example.com"],
        )
        record = ch.send("semi_active", "test")
        assert not record.delivered


class TestNotificationManager:
    def test_constructor_console_only(self) -> None:
        mgr = NotificationManager(console=True)
        assert len(mgr._channels) == 1
        assert mgr._channels[0].channel_name == "console"

    def test_notify_all(self) -> None:
        mgr = NotificationManager(console=True)
        records = mgr.notify_all("passive", "all channels test")
        assert len(records) == 1
        assert records[0].delivered

    def test_notify_specific_console(self) -> None:
        mgr = NotificationManager(console=True)
        record = mgr.notify_specific("console", "semi_active", "specific")
        assert record is not None
        assert record.delivered

    def test_notify_specific_unknown(self) -> None:
        mgr = NotificationManager(console=True)
        record = mgr.notify_specific("nonexistent", "passive", "nope")
        assert record is None

    def test_constructor_with_email(self) -> None:
        mgr = NotificationManager(
            console=True,
            smtp_host="smtp.example.com",
            email_to=["to@example.com"],
        )
        names = {ch.channel_name for ch in mgr._channels}
        assert "console" in names
        assert "email" in names
