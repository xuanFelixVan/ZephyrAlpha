# [A_test] module_id: MOD-GOV_vibe_coding | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] tests.agent_rbac.test_vibe_coding
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Vibe Coding / Novel Attack / Cybersec 2026 攻击面扩展测试."""

from __future__ import annotations

from zephyr.security.access_control.guards.cybersec_2026_guard import Cybersec2026Guard
from zephyr.security.access_control.guards.novel_attack_guard import NovelAttackGuard
from zephyr.security.access_control.guards.vibe_coding_guard import VibeCodingGuard


class TestAttackSurface:
    def test_vibe_coding_bypass_detected(self):
        guard = VibeCodingGuard()
        result = guard.scan("main.py", "# HACK: allow_all = True")
        assert len(result.detected) > 0
        assert result.risk_score > 0

    def test_vibe_coding_clean(self):
        guard = VibeCodingGuard()
        result = guard.scan("util.py", "def add(a, b): return a + b")
        assert len(result.detected) == 0
        assert result.risk_score == 0.0

    def test_novel_attack_suspicious_pattern(self):
        guard = NovelAttackGuard()
        result = guard.profile_action("agent_x", "sudo_override")
        assert result["suspicious"] is False

    def test_novel_attack_accumulate_suspicion(self):
        guard = NovelAttackGuard()
        for action in ["sudo_override", "meltdown", "bypass_killswitch", "direct_memory_write", "raw_socket"]:
            guard.profile_action("rogue_agent", action)
        result = guard.profile_action("rogue_agent", "another_novel")
        assert result["suspicion_score"] > 2.0

    def test_cybersec_2026_clean(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"operation": "read", "resource": "config.yml"})
        assert result.detected is False

    def test_cybersec_2026_agent_supply_chain(self):
        guard = Cybersec2026Guard()
        result = guard.scan({"package": "untrusted_hub", "unverified_model": True})
        assert result.detected is True
        assert "agent_supply_chain" in result.threat_category
