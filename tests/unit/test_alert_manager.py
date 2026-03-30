"""
告警管理器单元测试
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.modules.alert_manager import (
    AlertManager,
    Alert,
    AlertLevel,
    AlertChannel,
    EmailAlertChannel,
    ServerChanAlertChannel,
    BarkAlertChannel,
)


class TestAlertLevel:
    """测试告警级别枚举"""

    def test_alert_levels(self):
        """测试告警级别存在"""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"


class TestAlert:
    """测试 Alert 数据类"""

    def test_default_timestamp(self):
        """测试默认时间戳"""
        alert = Alert(
            level=AlertLevel.INFO,
            title="Test",
            message="Test message"
        )

        assert alert.timestamp is not None
        assert isinstance(alert.timestamp, datetime)

    def test_custom_timestamp(self):
        """测试自定义时间戳"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        alert = Alert(
            level=AlertLevel.INFO,
            title="Test",
            message="Test message",
            timestamp=custom_time
        )

        assert alert.timestamp == custom_time

    def test_default_tags(self):
        """测试默认标签"""
        alert = Alert(
            level=AlertLevel.INFO,
            title="Test",
            message="Test message"
        )

        assert alert.tags == {}

    def test_custom_tags(self):
        """测试自定义标签"""
        alert = Alert(
            level=AlertLevel.INFO,
            title="Test",
            message="Test message",
            tags={"key": "value"}
        )

        assert alert.tags == {"key": "value"}


class TestAlertChannel:
    """测试 AlertChannel 基类"""

    def test_send_raises_not_implemented(self):
        """测试 send 方法抛出 NotImplementedError"""
        channel = AlertChannel()

        with pytest.raises(NotImplementedError):
            channel.send(Mock())


class TestEmailAlertChannel:
    """测试邮件告警渠道"""

    def test_init(self):
        """测试初始化"""
        config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "password",
            "from_addr": "test@example.com",
            "to_addrs": [" recipient@example.com"]
        }

        channel = EmailAlertChannel(config)

        assert channel.smtp_server == "smtp.gmail.com"
        assert channel.max_retries == 3
        assert channel.timeout == 30

    def test_init_custom_retry(self):
        """测试自定义重试参数"""
        config = {"username": "test@example.com", "password": "password"}

        channel = EmailAlertChannel(config, max_retries=5, timeout=60)

        assert channel.max_retries == 5
        assert channel.timeout == 60

    def test_send_without_recipients(self):
        """测试无收件人时返回 False"""
        channel = EmailAlertChannel({"username": "test", "password": "test"})

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")
        result = channel.send(alert)

        assert result is False

    @patch('smtplib.SMTP')
    def test_send_success(self, mock_smtp):
        """测试发送成功"""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__ = Mock(return_value=mock_smtp_instance)
        mock_smtp.return_value.__exit__ = Mock(return_value=False)

        config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "password",
            "from_addr": "test@example.com",
            "to_addrs": ["recipient@example.com"]
        }

        channel = EmailAlertChannel(config)
        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test message")

        result = channel.send(alert)

        assert result is True
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()
        mock_smtp_instance.sendmail.assert_called_once()

    @patch('smtplib.SMTP')
    def test_send_retry_on_failure(self, mock_smtp):
        """测试失败时重试"""
        mock_smtp.side_effect = [ConnectionError("Failed"), None]

        config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "password",
            "from_addr": "test@example.com",
            "to_addrs": ["recipient@example.com"]
        }

        channel = EmailAlertChannel(config, max_retries=3)
        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")

        result = channel.send(alert)

        assert result is True
        assert mock_smtp.call_count == 2

    @patch('smtplib.SMTP')
    def test_send_auth_failure(self, mock_smtp):
        """测试认证失败"""
        import smtplib
        mock_smtp.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")

        config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "test@example.com",
            "password": "wrong",
            "from_addr": "test@example.com",
            "to_addrs": ["recipient@example.com"]
        }

        channel = EmailAlertChannel(config)
        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")

        result = channel.send(alert)

        assert result is False


class TestServerChanAlertChannel:
    """测试 Server酱告警渠道"""

    def test_init(self):
        """测试初始化"""
        config = {"sendkey": "test_sendkey"}

        channel = ServerChanAlertChannel(config)

        assert channel.sendkey == "test_sendkey"
        assert channel.max_retries == 3
        assert channel.timeout == 10

    def test_send_without_sendkey(self):
        """测试无 sendkey 时返回 False"""
        channel = ServerChanAlertChannel({})

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")
        result = channel.send(alert)

        assert result is False

    @patch('urllib.request.urlopen')
    def test_send_success(self, mock_urlopen):
        """测试发送成功"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"code": 0, "message": "success"}'
        mock_urlopen.return_value.__enter__ = Mock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = Mock(return_value=False)

        config = {"sendkey": "test_sendkey"}
        channel = ServerChanAlertChannel(config)

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test message")
        result = channel.send(alert)

        assert result is True

    @patch('urllib.request.urlopen')
    def test_send_api_error(self, mock_urlopen):
        """测试 API 返回错误"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"code": 400, "message": "error"}'
        mock_urlopen.return_value.__enter__ = Mock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = Mock(return_value=False)

        config = {"sendkey": "test_sendkey"}
        channel = ServerChanAlertChannel(config)

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")
        result = channel.send(alert)

        assert result is False


class TestBarkAlertChannel:
    """测试 Bark 告警渠道"""

    def test_init(self):
        """测试初始化"""
        config = {"bark_url": "https://api.day.app/abc"}

        channel = BarkAlertChannel(config)

        assert channel.bark_url == "https://api.day.app/abc"
        assert channel.group == "量化系统"
        assert channel.max_retries == 3
        assert channel.timeout == 10

    def test_send_without_url(self):
        """测试无 URL 时返回 False"""
        channel = BarkAlertChannel({})

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test")
        result = channel.send(alert)

        assert result is False

    @patch('urllib.request.urlopen')
    def test_send_success(self, mock_urlopen):
        """测试发送成功"""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"code": 200, "message": "success"}'
        mock_urlopen.return_value.__enter__ = Mock(return_value=mock_response)
        mock_urlopen.return_value.__exit__ = Mock(return_value=False)

        config = {"bark_url": "https://api.day.app/abc"}
        channel = BarkAlertChannel(config)

        alert = Alert(level=AlertLevel.INFO, title="Test", message="Test message")
        result = channel.send(alert)

        assert result is True


class TestAlertManager:
    """测试 AlertManager"""

    def test_init_no_channels(self):
        """测试无配置时初始化"""
        manager = AlertManager({})

        assert len(manager.channels) == 0

    def test_init_with_email_channel(self):
        """测试配置邮件渠道"""
        config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "test@example.com",
                "password": "password",
                "from_addr": "test@example.com",
                "to_addrs": ["recipient@example.com"]
            }
        }

        manager = AlertManager(config)

        assert len(manager.channels) == 1
        assert isinstance(manager.channels[0], EmailAlertChannel)

    def test_send_info(self):
        """测试发送信息告警"""
        manager = AlertManager({})

        result = manager.send(AlertLevel.INFO, "Info Title", "Info message")

        assert result is True
        assert len(manager.alert_history) == 1
        assert manager.alert_history[0].title == "Info Title"

    def test_send_warning(self):
        """测试发送警告告警"""
        manager = AlertManager({})

        result = manager.warning("Warning Title", "Warning message")

        assert result is True
        assert manager.alert_history[0].level == AlertLevel.WARNING

    def test_send_error(self):
        """测试发送错误告警"""
        manager = AlertManager({})

        result = manager.error("Error Title", "Error message")

        assert result is True
        assert manager.alert_history[0].level == AlertLevel.ERROR

    def test_send_critical(self):
        """测试发送严重告警"""
        manager = AlertManager({})

        result = manager.critical("Critical Title", "Critical message")

        assert result is True
        assert manager.alert_history[0].level == AlertLevel.CRITICAL

    def test_send_trade_alert(self):
        """测试发送交易告警"""
        manager = AlertManager({})

        result = manager.send_trade_alert(
            symbol="000001",
            action="BUY",
            quantity=1000,
            price=10.5
        )

        assert result is True
        assert "000001" in manager.alert_history[0].title
        assert "BUY" in manager.alert_history[0].title

    def test_send_trade_alert_with_pnl(self):
        """测试发送带盈亏的交易告警"""
        manager = AlertManager({})

        result = manager.send_trade_alert(
            symbol="000001",
            action="SELL",
            quantity=1000,
            price=11.0,
            pnl=500.0
        )

        assert result is True
        assert "盈亏" in manager.alert_history[0].message

    def test_send_risk_alert(self):
        """测试发送风险告警"""
        manager = AlertManager({})

        result = manager.send_risk_alert(
            risk_type="仓位超限",
            message="单只股票持仓超过20%",
            triggered_rules=["单票持仓上限"]
        )

        assert result is True
        assert "仓位超限" in manager.alert_history[0].title

    def test_send_strategy_alert(self):
        """测试发送策略告警"""
        manager = AlertManager({})

        result = manager.send_strategy_alert(
            event_type="信号生成",
            message="检测到买入信号"
        )

        assert result is True
        assert "信号生成" in manager.alert_history[0].title

    def test_async_send(self):
        """测试异步发送"""
        manager = AlertManager({})

        result = manager.send(
            AlertLevel.INFO,
            "Async Test",
            "Async message",
            async_send=True
        )

        assert result is True

    def test_get_recent_alerts(self):
        """测试获取最近告警"""
        manager = AlertManager({})

        for i in range(15):
            manager.send(AlertLevel.INFO, f"Alert {i}", f"Message {i}")

        recent = manager.get_recent_alerts(limit=10)

        assert len(recent) == 10
        assert recent[-1].title == "Alert 14"

    def test_get_alert_summary(self):
        """测试获取告警摘要"""
        manager = AlertManager({})

        manager.send(AlertLevel.INFO, "Info 1", "Message")
        manager.send(AlertLevel.WARNING, "Warning 1", "Message")
        manager.send(AlertLevel.WARNING, "Warning 2", "Message")
        manager.send(AlertLevel.ERROR, "Error 1", "Message")

        summary = manager.get_alert_summary()

        assert summary["total"] == 4
        assert summary["by_level"]["info"] == 1
        assert summary["by_level"]["warning"] == 2
        assert summary["by_level"]["error"] == 1

    def test_get_alert_summary_empty(self):
        """测试空告警摘要"""
        manager = AlertManager({})

        summary = manager.get_alert_summary()

        assert summary["total"] == 0
        assert summary["by_level"] == {}

    def test_clear_history(self):
        """测试清除历史"""
        manager = AlertManager({})

        manager.send(AlertLevel.INFO, "Test", "Test")
        assert len(manager.alert_history) == 1

        manager.clear_history()
        assert len(manager.alert_history) == 0

    def test_alert_history_limit(self):
        """测试告警历史限制"""
        manager = AlertManager({})

        for i in range(1005):
            manager.send(AlertLevel.INFO, f"Alert {i}", f"Message {i}")

        assert len(manager.alert_history) <= 1000

    def test_shutdown(self):
        """测试关闭"""
        manager = AlertManager({})

        manager.send(AlertLevel.INFO, "Test", "Test", async_send=True)

        manager.shutdown()
