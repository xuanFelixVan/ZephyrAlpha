# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [MODULE] tests.frontend.test_default_notification_manager
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.implementations.default_notification_manager
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_default_notification_manager.py
# [A_test] module_id: MOD-L08-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L08-001 单元测试: DefaultNotificationManager — 默认通知管理器。

蓝图验收: import 成功, send 返回 bool, channels 返回 list[str]。
覆盖: log 内建渠道, 注册外部渠道(微信接口位), 全成功/部分失败语义,
未知渠道失败, sender 异常容错, 空通知校验。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.frontend.implementations.default_notification_manager",
    reason="default_notification_manager not importable",
)

from zephyr.frontend.implementations.default_notification_manager import (  # noqa: E402
    DefaultNotificationManager,
    InvalidNotificationError,
)
from zephyr.frontend.interface_base import Notification, NotificationLevel  # noqa: E402


def _notification(title: str = "风控告警") -> Notification:
    return Notification(
        notification_id="n-1",
        title=title,
        body="body",
        level=NotificationLevel.WARNING,
        source_layer="D_RISK",
    )


class TestChannels:
    def test_log_channel_builtin(self):
        mgr = DefaultNotificationManager()
        assert "log" in mgr.channels()
        assert isinstance(mgr.channels(), list)

    def test_register_external_channel(self):
        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", lambda n: True)
        assert "wechat" in mgr.channels()

    def test_register_duplicate_channel_rejected(self):
        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", lambda n: True)
        with pytest.raises(InvalidNotificationError):
            mgr.register_channel("wechat", lambda n: True)


class TestSend:
    def test_send_log_channel_success(self):
        mgr = DefaultNotificationManager()
        assert mgr.send(_notification()) is True

    def test_send_to_external_channel(self):
        received = []
        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", received.append)
        assert mgr.send(_notification(), channels=["wechat"]) is True
        assert len(received) == 1
        assert received[0].title == "风控告警"

    def test_send_multi_channel_partial_failure(self):
        mgr = DefaultNotificationManager()
        mgr.register_channel("ok", lambda n: True)
        mgr.register_channel("bad", lambda n: False)
        assert mgr.send(_notification(), channels=["ok", "bad"]) is False

    def test_unknown_channel_fails(self):
        mgr = DefaultNotificationManager()
        assert mgr.send(_notification(), channels=["no-such"]) is False

    def test_sender_exception_tolerated(self):
        def _boom(n):
            raise RuntimeError("network down")

        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", _boom)
        assert mgr.send(_notification(), channels=["wechat"]) is False

    def test_default_channels_include_log(self):
        # channels=None → 全渠道（含 log + 已注册外部渠道）
        received = []
        mgr = DefaultNotificationManager()
        mgr.register_channel("wechat", received.append)
        assert mgr.send(_notification()) is True
        assert len(received) == 1

    def test_empty_title_rejected(self):
        mgr = DefaultNotificationManager()
        with pytest.raises(InvalidNotificationError):
            mgr.send(_notification(title=""))

    def test_return_type_bool(self):
        mgr = DefaultNotificationManager()
        result = mgr.send(_notification())
        assert isinstance(result, bool)
