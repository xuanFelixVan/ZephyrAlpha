# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [MODULE] tests.frontend.test_notification_channel_senders
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.implementations.notification_channel_senders
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;全程 mock 传输零真实 SMTP/webhook 发送
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] test_notification_channel_senders.py
# [A_test] module_id: MOD-L08-001_senders | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L08-001_senders 单元测试: Email/WeChat 通知渠道（register_channel 生产接线位）。

覆盖：
- 配置校验 fail-closed（InvalidNotificationError）：空 host/from/to、空 to_addrs 项、
  端口越界、超时非正、空 webhook_url、非 http(s) webhook；
- 未接线态（传输未注入）→ __call__ 返回 False（显式失败，不抛）；
- mock 传输：payload 字段断言（凭据透传 Owner 窗口注入位、subject 含级别+标题、
  企业微信 markdown 载荷结构）、返回 True/None=已受理、False=显式失败、异常=失败不抛；
- 注册位集成：DefaultNotificationManager.register_channel 后 send 语义
  （全成功 True / 渠道显式失败 False）；
- 契约：frozen dataclass、payload asdict JSON 可序列化、level 枚举/裸字符串兼容。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.frontend.implementations.default_notification_manager import (
    DefaultNotificationManager,
    InvalidNotificationError,
)
from zephyr.frontend.implementations.notification_channel_senders import (
    EmailChannelConfig,
    EmailNotificationSender,
    EmailPayload,
    WeChatChannelConfig,
    WeChatNotificationSender,
)
from zephyr.frontend.interface_base import Notification, NotificationLevel


def _notification(level: NotificationLevel = NotificationLevel.ERROR) -> Notification:
    return Notification(
        notification_id="n-1",
        title="回撤越线",
        body="组合回撤 10.2% 触发 ORANGE 阈值",
        level=level,
        source_layer="D_RISK",
    )


def _email_cfg(**overrides) -> EmailChannelConfig:
    base = {
        "host": "smtp.example.com",
        "from_addr": "alert@example.com",
        "to_addrs": ("owner@example.com",),
    }
    base.update(overrides)
    return EmailChannelConfig(**base)


# ----------------------------------------------------------------------
# Email 配置校验（fail-closed）
# ----------------------------------------------------------------------


class TestEmailConfigValidation:
    @pytest.mark.parametrize(
        "override",
        [
            {"host": ""},
            {"host": "   "},
            {"from_addr": ""},
            {"to_addrs": ()},
            {"to_addrs": ("ok@example.com", " ")},
            {"port": 0},
            {"port": 70000},
            {"timeout_s": 0},
            {"timeout_s": -1.5},
        ],
    )
    def test_invalid_config_raises(self, override) -> None:
        with pytest.raises(InvalidNotificationError):
            _email_cfg(**override)

    def test_valid_config_defaults(self) -> None:
        cfg = _email_cfg()
        assert cfg.port == 465
        assert cfg.use_tls is True
        assert cfg.timeout_s > 0

    def test_config_frozen(self) -> None:
        cfg = _email_cfg()
        with pytest.raises(dataclasses.FrozenInstanceError):
            cfg.host = "evil.example.com"  # type: ignore[misc]


# ----------------------------------------------------------------------
# Email 发送行为（mock SMTP 传输注入位）
# ----------------------------------------------------------------------


class TestEmailSender:
    def test_unwired_transport_returns_false(self) -> None:
        sender = EmailNotificationSender(_email_cfg())
        assert sender(_notification()) is False

    def test_mock_transport_receives_payload(self) -> None:
        seen: dict[str, EmailPayload] = {}

        def fake_smtp(payload: EmailPayload) -> bool:
            seen["payload"] = payload
            return True

        cfg = _email_cfg(username="bot", password="secret-via-owner-window", port=587, use_tls=False)
        sender = EmailNotificationSender(cfg, fake_smtp)
        assert sender(_notification()) is True

        payload = seen["payload"]
        assert payload.host == "smtp.example.com"
        assert payload.port == 587
        assert payload.username == "bot"
        assert payload.password == "secret-via-owner-window"
        assert payload.use_tls is False
        assert payload.from_addr == "alert@example.com"
        assert payload.to_addrs == ("owner@example.com",)
        assert "error" in payload.subject.lower()  # 级别前缀
        assert "回撤越线" in payload.subject
        assert "ORANGE" in payload.text

    def test_transport_none_outcome_treated_as_accepted(self) -> None:
        sender = EmailNotificationSender(_email_cfg(), lambda payload: None)
        assert sender(_notification()) is True

    def test_transport_false_is_explicit_failure(self) -> None:
        sender = EmailNotificationSender(_email_cfg(), lambda payload: False)
        assert sender(_notification()) is False

    def test_transport_exception_is_failure_not_raise(self) -> None:
        def boom(payload: EmailPayload) -> bool:
            raise ConnectionError("smtp down")

        sender = EmailNotificationSender(_email_cfg(), boom)
        assert sender(_notification()) is False  # 异常内化为 False，不外抛

    def test_payload_json_serializable(self) -> None:
        seen: dict[str, EmailPayload] = {}
        sender = EmailNotificationSender(_email_cfg(), lambda p: seen.setdefault("p", p))
        sender(_notification())
        json.dumps(dataclasses.asdict(seen["p"]), ensure_ascii=False)

    def test_level_accepts_plain_string(self) -> None:
        seen: dict[str, EmailPayload] = {}
        sender = EmailNotificationSender(_email_cfg(), lambda p: seen.setdefault("p", p))
        n = _notification()
        object.__setattr__(n, "level", "critical")  # 裸字符串 level 兼容
        sender(n)
        assert "critical" in seen["p"].subject.lower()


# ----------------------------------------------------------------------
# WeChat 配置校验（fail-closed）
# ----------------------------------------------------------------------


class TestWeChatConfigValidation:
    @pytest.mark.parametrize(
        "override",
        [
            {"webhook_url": ""},
            {"webhook_url": "   "},
            {"webhook_url": "qyapi.weixin.qq.com/no-scheme"},
            {"webhook_url": "ftp://example.com/hook"},
            {"timeout_s": 0},
        ],
    )
    def test_invalid_config_raises(self, override) -> None:
        with pytest.raises(InvalidNotificationError):
            WeChatChannelConfig(**{"webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=k"} | override)


# ----------------------------------------------------------------------
# WeChat 发送行为（mock webhook 传输注入位）
# ----------------------------------------------------------------------


class TestWeChatSender:
    def _cfg(self) -> WeChatChannelConfig:
        return WeChatChannelConfig(webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=owner-key")

    def test_unwired_transport_returns_false(self) -> None:
        assert WeChatNotificationSender(self._cfg())(_notification()) is False

    def test_mock_transport_receives_markdown_payload(self) -> None:
        seen: dict[str, object] = {}

        def fake_post(url: str, payload: dict, timeout_s: float) -> bool:
            seen["url"] = url
            seen["payload"] = payload
            seen["timeout_s"] = timeout_s
            return True

        sender = WeChatNotificationSender(self._cfg(), fake_post)
        assert sender(_notification()) is True

        assert seen["url"] == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=owner-key"
        assert seen["timeout_s"] == 10.0
        payload = seen["payload"]
        assert payload["msgtype"] == "markdown"
        content = payload["markdown"]["content"]
        assert "回撤越线" in content
        assert "ORANGE" in content

    def test_transport_false_and_exception(self) -> None:
        assert WeChatNotificationSender(self._cfg(), lambda u, p, t: False)(_notification()) is False

        def boom(u: str, p: dict, t: float) -> bool:
            raise TimeoutError("webhook timeout")

        assert WeChatNotificationSender(self._cfg(), boom)(_notification()) is False


# ----------------------------------------------------------------------
# MOD-L08-001 注册位集成
# ----------------------------------------------------------------------


class TestRegisterChannelIntegration:
    def test_email_channel_full_success(self) -> None:
        mgr = DefaultNotificationManager()
        mgr.register_channel("email", EmailNotificationSender(_email_cfg(), lambda p: True))
        assert "email" in mgr.channels()
        assert mgr.send(_notification(), channels=["email"]) is True

    def test_wechat_channel_explicit_failure_propagates(self) -> None:
        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", WeChatNotificationSender(WeChatChannelConfig(webhook_url="https://example.com/hook")))
        # 未接线态 sender 显式失败 → send 返回 False（fail-visible）
        assert mgr.send(_notification(), channels=["wechat"]) is False

    def test_both_channels_mixed_outcome(self) -> None:
        mgr = DefaultNotificationManager()
        mgr.register_channel("email", EmailNotificationSender(_email_cfg(), lambda p: True))
        mgr.register_channel("wechat", WeChatNotificationSender(WeChatChannelConfig(webhook_url="https://example.com/hook"), lambda u, p, t: True))
        assert mgr.send(_notification()) is True  # log+email+wechat 全成功
