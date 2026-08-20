# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_heartbeat_server
# [DOMAIN] D_SHARED
# [INVARIANTS] 未注册组件判死(last=0); 超时判死; beat 刷新生效; check_all 覆盖全组件
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""shared/alerts HeartbeatServer 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import time

from zephyr.shared.alerts.heartbeat_server import HeartbeatServer


class TestHeartbeatServer:
    def test_registered_component_alive(self):
        server = HeartbeatServer(timeout_seconds=30.0)
        server.register("engine")
        status = server.check("engine")
        assert status.is_alive is True
        assert status.interval_seconds == 30.0
        assert status.last_heartbeat > 0

    def test_unregistered_component_dead(self):
        server = HeartbeatServer()
        status = server.check("ghost")
        assert status.is_alive is False
        assert status.last_heartbeat == 0.0

    def test_beat_refreshes(self):
        server = HeartbeatServer(timeout_seconds=30.0)
        server.register("engine")
        first = server.check("engine").last_heartbeat
        time.sleep(0.01)
        server.beat("engine")
        assert server.check("engine").last_heartbeat >= first

    def test_timeout_marks_dead(self):
        server = HeartbeatServer(timeout_seconds=0.02)
        server.register("engine")
        time.sleep(0.05)
        assert server.check("engine").is_alive is False

    def test_check_all_covers_registered(self):
        server = HeartbeatServer()
        server.register("a")
        server.register("b")
        statuses = server.check_all()
        assert {s.component_id for s in statuses} == {"a", "b"}
        assert all(s.is_alive for s in statuses)

    def test_check_all_empty(self):
        assert HeartbeatServer().check_all() == []
