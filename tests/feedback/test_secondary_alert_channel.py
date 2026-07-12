# [A_test] module_id: SRC-TST-1538 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_secondary_alert_channel
# [INVARIANTS] active_channel set from channels[0] on init; failover increments failover_count
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.feedback_loop.actors.secondary_alert_channel import (
    ChannelState,
    SecondaryAlertChannel,
)


class TestChannelState:
    def test_enum_values(self):
        assert ChannelState.HEALTHY == "HEALTHY"
        assert ChannelState.DEGRADED == "DEGRADED"
        assert ChannelState.DOWN == "DOWN"


class TestSecondaryAlertChannelInstantiation:
    def test_default_construction(self):
        sac = SecondaryAlertChannel()
        assert sac.active_channel == "sms"
        assert sac.channels == ["sms", "email", "push"]
        assert sac.failover_count == 0
        for ch in sac.channels:
            assert sac.channel_health[ch] == ChannelState.HEALTHY

    def test_custom_channels(self):
        sac = SecondaryAlertChannel(channels=["slack", "pager"])
        assert sac.active_channel == "slack"
        assert "slack" in sac.channel_health
        assert "pager" in sac.channel_health

    def test_empty_channels(self):
        sac = SecondaryAlertChannel(channels=[])
        assert sac.active_channel == ""
        assert sac.channel_health == {}


class TestHeartbeat:
    def test_heartbeat_updates_health(self):
        sac = SecondaryAlertChannel()
        sac.channel_health["sms"] = ChannelState.DOWN
        sac.heartbeat("sms")
        assert sac.channel_health["sms"] == ChannelState.HEALTHY
        assert sac.last_heartbeat["sms"] > 0

    def test_heartbeat_nonexistent_channel(self):
        sac = SecondaryAlertChannel()
        sac.heartbeat("unknown_channel")
        assert sac.channel_health["unknown_channel"] == ChannelState.HEALTHY


class TestCheckChannels:
    def test_returns_active_when_healthy(self):
        sac = SecondaryAlertChannel()
        result = sac.check_channels()
        assert result == "sms"

    def test_failover_when_active_down(self):
        sac = SecondaryAlertChannel()
        sac.channel_health["sms"] = ChannelState.DOWN
        sac.last_heartbeat["sms"] = time.time() - sac.heartbeat_interval * 4
        result = sac.check_channels()
        assert result == "email"
        assert sac.failover_count == 1

    def test_no_failover_when_active_healthy(self):
        sac = SecondaryAlertChannel()
        sac.heartbeat("sms")
        result = sac.check_channels()
        assert result == "sms"
        assert sac.failover_count == 0


class TestSendAlert:
    def test_send_alert_returns_dict(self):
        sac = SecondaryAlertChannel()
        result = sac.send_alert(message="disk full", severity="critical")
        assert result["channel"] == "sms"
        assert result["message"] == "disk full"
        assert result["severity"] == "critical"
        assert result["failover_count"] == 0

    def test_send_alert_with_failover(self):
        sac = SecondaryAlertChannel()
        sac.channel_health["sms"] = ChannelState.DOWN
        sac.last_heartbeat["sms"] = time.time() - sac.heartbeat_interval * 4
        result = sac.send_alert(message="cpu high", severity="warning")
        assert result["channel"] == "email"
        assert result["failover_count"] == 1
