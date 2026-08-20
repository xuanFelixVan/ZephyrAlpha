# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_dual_channel_alert
# [DOMAIN] D_SHARED
# [INVARIANTS] 通道选择正确落 sent 标记; get_failed_channels 只报未达通道
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""shared/alerts DualChannelAlert 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from zephyr.shared.alerts.dual_channel_alert import Channel, DualChannelAlert


class TestDualChannelAlert:
    def test_default_both_channels_sent(self):
        dca = DualChannelAlert()
        alert = dca.send("t", "m")
        assert alert.dashboard_sent is True
        assert alert.messaging_sent is True
        assert dca.get_failed_channels() == []

    def test_dashboard_only(self):
        dca = DualChannelAlert()
        alert = dca.send("t", "m", channels=(Channel.DASHBOARD,))
        assert alert.dashboard_sent is True
        assert alert.messaging_sent is False
        failed = dca.get_failed_channels()
        assert len(failed) == 1
        assert failed[0][1] == [Channel.MESSAGING]

    def test_messaging_only(self):
        dca = DualChannelAlert()
        dca.send("t", "m", channels=(Channel.MESSAGING,))
        failed = dca.get_failed_channels()
        assert failed[0][1] == [Channel.DASHBOARD]

    def test_empty_channels_both_failed(self):
        dca = DualChannelAlert()
        alert = dca.send("t", "m", channels=())
        assert alert.dashboard_sent is False
        assert alert.messaging_sent is False
        failed = dca.get_failed_channels()
        assert set(failed[0][1]) == {Channel.DASHBOARD, Channel.MESSAGING}

    def test_multiple_alerts_failure_aggregation(self):
        dca = DualChannelAlert()
        dca.send("ok", "m")
        dca.send("partial", "m", channels=(Channel.DASHBOARD,))
        dca.send("none", "m", channels=())
        failed = dca.get_failed_channels()
        assert [a.title for a, _ in failed] == ["partial", "none"]
