# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler, module_id corrected 2026-07-23)
# [TTL] permanent
"""alerter 单测（MOD-L00-004 阶段2 + 阶段3 告警通道 audit 8.3）。

测试内容：
- notify 写日志 + 写失败汇总文件
- 失败汇总文件 JSON 格式正确
- check_daily_failure_rate 阈值判断
- check_consecutive_failures 连续失败告警
- list_failure_files / read_failure_file 查询
- format_alert_text 告警正文格式化
- notify_channels 通道分发与级别过滤
- send_feishu_webhook 飞书 webhook（未配置跳过 / mock 发送 / 异常吞掉）
- send_email_smtp SMTP 邮件（未配置跳过 / mock 发送 / 异常吞掉）
- alert_timeout 超时配置读取
- notify 集成：ERROR 触达通道、WARN 不触达、冷却期不重复触达

用 tmp_path fixture 隔离测试 failures/ 目录。
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.zephyr.data.alerter import (
    LEVEL_CRITICAL,
    LEVEL_ERROR,
    LEVEL_INFO,
    LEVEL_WARN,
    Alerter,
)


@pytest.fixture
def alerter(tmp_path):
    """用临时目录的 Alerter。"""
    return Alerter(failures_dir=tmp_path / "failures")


class TestNotify:
    """notify 测试。"""

    def test_error_writes_failure_file(self, alerter, tmp_path):
        """ERROR 级别应写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "连接超时", level=LEVEL_ERROR, source="akshare")
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_critical_writes_failure_file(self, alerter, tmp_path):
        """CRITICAL 级别应写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "配额耗尽", level=LEVEL_CRITICAL, source="akshare")
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_warn_no_failure_file(self, alerter, tmp_path):
        """WARN 级别不写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "慢查询", level=LEVEL_WARN)
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_info_no_failure_file(self, alerter, tmp_path):
        """INFO 级别不写失败汇总文件。"""
        ok = alerter.notify("kline_daily", "开始执行", level=LEVEL_INFO)
        assert ok is True
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_failure_file_content(self, alerter, tmp_path):
        """失败汇总文件 JSON 格式正确。"""
        alerter.notify(
            "margin_trading",
            "SSL错误",
            level=LEVEL_ERROR,
            source="akshare",
            extra={"retry_count": 3},
        )
        files = list((tmp_path / "failures").glob("*.json"))
        with open(files[0], encoding="utf-8") as f:
            data = json.load(f)
        assert data["task_id"] == "margin_trading"
        assert data["source"] == "akshare"
        assert data["error"] == "SSL错误"
        assert data["level"] == LEVEL_ERROR
        assert data["extra"]["retry_count"] == 3
        assert "timestamp" in data

    def test_notify_no_exception(self, alerter):
        """notify 不应抛异常（即使参数异常）。"""
        ok = alerter.notify("", "", level=LEVEL_ERROR)
        assert ok in (True, False)  # 不抛异常即可


class TestDailyFailureRate:
    """check_daily_failure_rate 测试。"""

    def test_rate_below_threshold(self, alerter):
        """失败率 <= 5% 不告警。"""
        assert alerter.check_daily_failure_rate(total=100, failed=3) is False
        assert alerter.check_daily_failure_rate(total=100, failed=5) is False  # 等于阈值

    def test_rate_above_threshold(self, alerter, tmp_path):
        """失败率 > 5% 告警。"""
        # 10/100 = 10% > 5%，会写 WARN 级别告警（不写失败汇总文件）
        result = alerter.check_daily_failure_rate(total=100, failed=10)
        assert result is True
        # WARN 不写失败文件
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 0

    def test_zero_total(self, alerter):
        """total=0 不告警。"""
        assert alerter.check_daily_failure_rate(total=0, failed=0) is False


class TestConsecutiveFailures:
    """check_consecutive_failures 测试。"""

    def test_below_threshold(self, alerter):
        """连续失败 < 3 天不告警。"""
        assert alerter.check_consecutive_failures("kline_daily", 2) is False

    def test_at_threshold(self, alerter, tmp_path):
        """连续失败 >= 3 天告警（CRITICAL）。"""
        result = alerter.check_consecutive_failures("kline_daily", 3)
        assert result is True
        # CRITICAL 写失败文件
        files = list((tmp_path / "failures").glob("*.json"))
        assert len(files) == 1

    def test_custom_threshold(self, alerter):
        """自定义阈值。"""
        assert alerter.check_consecutive_failures("kline_daily", 2, threshold=5) is False
        assert alerter.check_consecutive_failures("kline_daily", 5, threshold=5) is True


class TestQueryFailures:
    """list_failure_files / read_failure_file 测试。"""

    def test_list_empty(self, alerter, tmp_path):
        """无失败文件时返回空列表。"""
        assert alerter.list_failure_files() == []

    def test_list_all(self, alerter, tmp_path):
        """列出所有失败文件。"""
        alerter.notify("task_a", "err1", level=LEVEL_ERROR)
        alerter.notify("task_b", "err2", level=LEVEL_ERROR)
        files = alerter.list_failure_files()
        assert len(files) == 2

    def test_list_by_date(self, alerter, tmp_path):
        """按日期过滤。

        alerter 文件名用 UTC 日期（now_utc().strftime("%Y%m%d")），
        与文件内 timestamp（UTC）保持一致；查询也须用 UTC 日期，
        否则在 UTC<local 的时区窗口（如 CST 00:00-08:00 = UTC 前一天）
        会因日期错位而漏匹配。B2 告警通道验证发现并修复（#ARCH-CH-023）。
        """
        from zephyr.shared.utils.time_utils import now_utc

        alerter.notify("task_a", "err1", level=LEVEL_ERROR)
        today_utc = now_utc().strftime("%Y%m%d")
        files = alerter.list_failure_files(date=today_utc)
        assert len(files) == 1
        files_other = alerter.list_failure_files(date="20250101")
        assert len(files_other) == 0

    def test_read_failure_file(self, alerter, tmp_path):
        """读取失败文件内容。"""
        alerter.notify("task_a", "err1", level=LEVEL_ERROR, source="akshare")
        files = alerter.list_failure_files()
        data = alerter.read_failure_file(files[0])
        assert data is not None
        assert data["task_id"] == "task_a"
        assert data["error"] == "err1"

    def test_read_nonexistent_file(self, alerter):
        """读取不存在的文件返回 None。"""
        assert alerter.read_failure_file("nonexistent.json") is None


# ============================================================
# 告警触达通道测试（audit 8.3，#ARCH-CH-023）
# ============================================================

# 告警通道相关 env 变量名（与 alerter.py 常量保持同步）
_ENV_KEYS = [
    "ZEPHYR_FEISHU_WEBHOOK",
    "ZEPHYR_SMTP_HOST",
    "ZEPHYR_SMTP_PORT",
    "ZEPHYR_SMTP_USER",
    "ZEPHYR_SMTP_PASSWORD",
    "ZEPHYR_ALERT_RECIPIENT",
    "ZEPHYR_ALERT_SENDER",
    "ZEPHYR_ALERT_TIMEOUT",
]


@pytest.fixture
def clean_alert_env(monkeypatch):
    """清除所有告警通道 env 变量，确保通道默认未配置。"""
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    yield


class TestFormatAlertText:
    """format_alert_text 测试。"""

    def test_basic_format(self):
        """基本字段格式正确。"""
        text = Alerter.format_alert_text("kline_daily", "连接超时", LEVEL_ERROR, "akshare", None)
        assert "[ZephyrAlpha 告警]" in text
        assert "级别: ERROR" in text
        assert "任务: kline_daily" in text
        assert "数据源: akshare" in text
        assert "错误: 连接超时" in text
        assert "时间:" in text

    def test_source_none_shows_na(self):
        """source 为 None 显示 N/A。"""
        text = Alerter.format_alert_text("task_x", "err", LEVEL_CRITICAL, None, None)
        assert "数据源: N/A" in text

    def test_extra_included(self):
        """extra 字典序列化到正文。"""
        text = Alerter.format_alert_text("task_x", "err", LEVEL_ERROR, None, {"retry": 3, "code": "-4318"})
        assert "附加:" in text
        assert '"retry": 3' in text
        assert '"code": "-4318"' in text

    def test_no_extra_line_when_none(self):
        """extra 为 None 时不出现附加行。"""
        text = Alerter.format_alert_text("task_x", "err", LEVEL_ERROR, None, None)
        assert "附加:" not in text


class TestNotifyChannelsDispatch:
    """notify_channels 分发与级别过滤测试。"""

    def test_warn_does_not_reach_channels(self, alerter, clean_alert_env):
        """WARN 级别不触达通道。"""
        with (
            patch.object(alerter, "send_feishu_webhook") as mock_fw,
            patch.object(alerter, "send_email_smtp") as mock_em,
        ):
            alerter.notify_channels("task", "err", LEVEL_WARN, None, None)
            mock_fw.assert_not_called()
            mock_em.assert_not_called()

    def test_info_does_not_reach_channels(self, alerter, clean_alert_env):
        """INFO 级别不触达通道。"""
        with (
            patch.object(alerter, "send_feishu_webhook") as mock_fw,
            patch.object(alerter, "send_email_smtp") as mock_em,
        ):
            alerter.notify_channels("task", "err", LEVEL_INFO, None, None)
            mock_fw.assert_not_called()
            mock_em.assert_not_called()

    def test_error_reaches_both_channels(self, alerter, clean_alert_env):
        """ERROR 级别触达飞书+邮件两个通道。"""
        with (
            patch.object(alerter, "send_feishu_webhook") as mock_fw,
            patch.object(alerter, "send_email_smtp") as mock_em,
        ):
            alerter.notify_channels("task", "err", LEVEL_ERROR, "akshare", {"k": "v"})
            mock_fw.assert_called_once()
            mock_em.assert_called_once()
            # 验证飞书收到的 text 含任务名
            sent_text = mock_fw.call_args[0][0]
            assert "任务: task" in sent_text

    def test_critical_reaches_both_channels(self, alerter, clean_alert_env):
        """CRITICAL 级别触达两个通道。"""
        with (
            patch.object(alerter, "send_feishu_webhook") as mock_fw,
            patch.object(alerter, "send_email_smtp") as mock_em,
        ):
            alerter.notify_channels("task", "err", LEVEL_CRITICAL, None, None)
            mock_fw.assert_called_once()
            mock_em.assert_called_once()


class TestSendFeishuWebhook:
    """send_feishu_webhook 测试。"""

    def test_skip_when_not_configured(self, alerter, clean_alert_env):
        """未配置 webhook 时静默跳过（返回 False，不抛异常）。"""
        assert alerter.send_feishu_webhook("hello") is False

    def test_send_success_when_configured(self, alerter, monkeypatch):
        """配置 webhook 后 mock 发送成功。"""
        monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://open.feishu.cn/open-apis/bot/v2/hook/test-token")
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.zephyr.data.alerter.urllib.request.urlopen", return_value=mock_resp) as mock_open:
            result = alerter.send_feishu_webhook("test message")
        assert result is True
        mock_open.assert_called_once()
        # 验证 request 的 url 和 method
        req = mock_open.call_args[0][0]
        assert req.full_url.endswith("test-token")
        assert req.method == "POST"

    def test_non_200_response_returns_false(self, alerter, monkeypatch):
        """非 200 响应返回 False。"""
        monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://example.com/hook")
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.zephyr.data.alerter.urllib.request.urlopen", return_value=mock_resp):
            result = alerter.send_feishu_webhook("msg")
        assert result is False

    def test_network_exception_swallowed(self, alerter, monkeypatch):
        """网络异常被吞掉，返回 False 不抛异常。"""
        monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://example.com/hook")
        with patch("src.zephyr.data.alerter.urllib.request.urlopen", side_effect=ConnectionError("refused")):
            result = alerter.send_feishu_webhook("msg")
        assert result is False


class TestSendEmailSmtp:
    """send_email_smtp 测试。"""

    def test_skip_when_not_configured(self, alerter, clean_alert_env):
        """未配置 SMTP host 时静默跳过。"""
        assert alerter.send_email_smtp("task", LEVEL_ERROR, "body") is False

    def test_skip_when_host_but_no_user(self, alerter, monkeypatch):
        """配置了 host 但缺 user/recipient 时跳过。"""
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.delenv("ZEPHYR_SMTP_USER", raising=False)
        monkeypatch.delenv("ZEPHYR_ALERT_RECIPIENT", raising=False)
        assert alerter.send_email_smtp("task", LEVEL_ERROR, "body") is False

    def test_send_success_when_configured(self, alerter, monkeypatch):
        """完整配置后 mock 发送成功。"""
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_PORT", "587")
        monkeypatch.setenv("ZEPHYR_SMTP_USER", "alert@example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_PASSWORD", "secret")
        monkeypatch.setenv("ZEPHYR_ALERT_RECIPIENT", "ops@example.com")
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch("src.zephyr.data.alerter.smtplib.SMTP", return_value=mock_smtp) as mock_ctor:
            result = alerter.send_email_smtp("kline_daily", LEVEL_ERROR, "body text")
        assert result is True
        # local_hostname 必须显式传 ASCII 值（B2 验证发现，#ARCH-CH-023）
        mock_ctor.assert_called_once_with("smtp.example.com", 587, local_hostname="zephyr.alert.local", timeout=5)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("alert@example.com", "secret")
        mock_smtp.sendmail.assert_called_once()
        # 验证发件人/收件人
        args = mock_smtp.sendmail.call_args[0]
        assert args[0] == "alert@example.com"  # sender 默认=USER
        assert args[1] == ["ops@example.com"]  # recipient

    def test_subject_encoded_for_non_ascii(self, alerter, monkeypatch):
        """Subject 含中文时必须 RFC 2047 编码，msg.as_string() 可 ASCII 编码。

        回归 B2 验证发现：原实现 msg["Subject"] = subject（含中文）会导致
        msg.as_string() 产生非 ASCII 头，smtp.data() 的 ASCII 编码失败（#ARCH-CH-023）。
        """
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_USER", "alert@example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_PASSWORD", "secret")
        monkeypatch.setenv("ZEPHYR_ALERT_RECIPIENT", "ops@example.com")
        captured_msg: list[str] = []

        def _capture_sendmail(sender, recipients, msg_str):
            captured_msg.append(msg_str)
            return {}

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp.sendmail.side_effect = _capture_sendmail
        with patch("src.zephyr.data.alerter.smtplib.SMTP", return_value=mock_smtp):
            alerter.send_email_smtp("kline_daily", LEVEL_ERROR, "body text")
        # msg.as_string() 整体必须可 ASCII 编码（SMTP 协议要求）
        assert len(captured_msg) == 1
        msg_str = captured_msg[0]
        msg_str.encode("ascii")  # 不抛 UnicodeEncodeError 即通过
        # Subject 头应出现 RFC 2047 编码（=?utf-8?b?...?=）
        assert "=?utf-8?b?" in msg_str.lower()

    def test_sender_override(self, alerter, monkeypatch):
        """ZEPHYR_ALERT_SENDER 覆盖默认发件人。"""
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_USER", "user@example.com")
        monkeypatch.setenv("ZEPHYR_ALERT_RECIPIENT", "ops@example.com")
        monkeypatch.setenv("ZEPHYR_ALERT_SENDER", "noreply@example.com")
        monkeypatch.delenv("ZEPHYR_SMTP_PASSWORD", raising=False)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch("src.zephyr.data.alerter.smtplib.SMTP", return_value=mock_smtp):
            alerter.send_email_smtp("task", LEVEL_ERROR, "body")
        sender = mock_smtp.sendmail.call_args[0][0]
        assert sender == "noreply@example.com"

    def test_no_login_when_password_empty(self, alerter, monkeypatch):
        """password 为空时不调用 login（支持无认证 SMTP）。"""
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_USER", "user@example.com")
        monkeypatch.setenv("ZEPHYR_ALERT_RECIPIENT", "ops@example.com")
        monkeypatch.delenv("ZEPHYR_SMTP_PASSWORD", raising=False)
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch("src.zephyr.data.alerter.smtplib.SMTP", return_value=mock_smtp):
            alerter.send_email_smtp("task", LEVEL_ERROR, "body")
        mock_smtp.login.assert_not_called()

    def test_smtp_exception_swallowed(self, alerter, monkeypatch):
        """SMTP 异常被吞掉，返回 False 不抛异常。"""
        monkeypatch.setenv("ZEPHYR_SMTP_HOST", "smtp.example.com")
        monkeypatch.setenv("ZEPHYR_SMTP_USER", "user@example.com")
        monkeypatch.setenv("ZEPHYR_ALERT_RECIPIENT", "ops@example.com")
        with patch("src.zephyr.data.alerter.smtplib.SMTP", side_effect=ConnectionRefusedError("refused")):
            result = alerter.send_email_smtp("task", LEVEL_ERROR, "body")
        assert result is False


class TestAlertTimeout:
    """alert_timeout 配置读取测试。"""

    def test_default_when_not_set(self, clean_alert_env):
        """未配置时返回默认 5s。"""
        assert Alerter.alert_timeout() == 5

    def test_env_override(self, monkeypatch):
        """env 可覆盖超时。"""
        monkeypatch.setenv("ZEPHYR_ALERT_TIMEOUT", "10")
        assert Alerter.alert_timeout() == 10

    def test_invalid_value_falls_back(self, monkeypatch):
        """非法值回退到默认。"""
        monkeypatch.setenv("ZEPHYR_ALERT_TIMEOUT", "not-a-number")
        assert Alerter.alert_timeout() == 5


class TestNotifyChannelIntegration:
    """notify 集成测试：验证 ERROR 触达通道、WARN 不触达、冷却期不重复触达。"""

    def test_error_triggers_channels(self, alerter, clean_alert_env, tmp_path):
        """ERROR 级别 notify 应触达通道（failure file 写入后）。"""
        with patch.object(alerter, "notify_channels") as mock_ch:
            alerter.notify("task_a", "err", level=LEVEL_ERROR, source="akshare")
        mock_ch.assert_called_once()

    def test_critical_triggers_channels(self, alerter, clean_alert_env, tmp_path):
        """CRITICAL 级别 notify 应触达通道。"""
        with patch.object(alerter, "notify_channels") as mock_ch:
            alerter.notify("task_a", "err", level=LEVEL_CRITICAL, source="akshare")
        mock_ch.assert_called_once()

    def test_warn_does_not_trigger_channels(self, alerter, clean_alert_env):
        """WARN 级别 notify 不触达通道。"""
        with patch.object(alerter, "notify_channels") as mock_ch:
            alerter.notify("task_a", "err", level=LEVEL_WARN)
        mock_ch.assert_not_called()

    def test_info_does_not_trigger_channels(self, alerter, clean_alert_env):
        """INFO 级别 notify 不触达通道。"""
        with patch.object(alerter, "notify_channels") as mock_ch:
            alerter.notify("task_a", "err", level=LEVEL_INFO)
        mock_ch.assert_not_called()

    def test_cooldown_prevents_duplicate_channel_notify(self, alerter, clean_alert_env):
        """冷却期内重复 ERROR 不重复触达通道（failure file 跳过则通道也跳过）。"""
        with patch.object(alerter, "notify_channels") as mock_ch:
            alerter.notify("task_a", "err1", level=LEVEL_ERROR)
            # 第二次在 300s 冷却期内 → failure file 返回 False → 通道不触达
            alerter.notify("task_a", "err2", level=LEVEL_ERROR)
        mock_ch.assert_called_once()

    def test_channels_failure_does_not_affect_notify_return(self, alerter, monkeypatch):
        """通道发送失败不影响 notify 返回值（仍返回 True=failure file 已写）。"""
        monkeypatch.setenv("ZEPHYR_FEISHU_WEBHOOK", "https://example.com/hook")
        with patch("src.zephyr.data.alerter.urllib.request.urlopen", side_effect=ConnectionError("refused")):
            result = alerter.notify("task_a", "err", level=LEVEL_ERROR)
        assert result is True  # failure file 写成功，通道失败不影响
