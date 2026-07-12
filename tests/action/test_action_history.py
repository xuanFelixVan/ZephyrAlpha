# [A_test] module_id: SRC-TST-0265 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_action_history
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_history.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.action_history import (
    ActionHistory,
    ActionSignature,
    DedupAction,
    DedupResult,
    LoopEvent,
)


class TestActionSignature:
    def test_fingerprint_deterministic(self):
        sig1 = ActionSignature(tool_name="read", tool_params_hash="abc", tool_params_semantic_hash="def")
        sig2 = ActionSignature(tool_name="read", tool_params_hash="abc", tool_params_semantic_hash="def")
        assert sig1.fingerprint == sig2.fingerprint

    def test_fingerprint_differs_for_different_params(self):
        sig1 = ActionSignature(tool_name="read", tool_params_hash="abc")
        sig2 = ActionSignature(tool_name="read", tool_params_hash="xyz")
        assert sig1.fingerprint != sig2.fingerprint

    def test_default_values(self):
        sig = ActionSignature(tool_name="test", tool_params_hash="h")
        assert sig.tool_params_semantic_hash == ""
        assert sig.output_effect_hash == ""
        assert sig.cost_incurred == 0.0
        assert sig.timestamp > 0


class TestDedupResult:
    def test_allow_result(self):
        r = DedupResult(action=DedupAction.ALLOW)
        assert r.action == DedupAction.ALLOW
        assert r.reason == ""
        assert r.identical_count == 0

    def test_block_result_with_reason(self):
        r = DedupResult(action=DedupAction.BLOCK, reason="loop", identical_count=5, fingerprint="fp")
        assert r.action == DedupAction.BLOCK
        assert r.identical_count == 5


class TestLoopEvent:
    def test_creation(self):
        ev = LoopEvent(fingerprint="fp", tool_name="write", count=3, action=DedupAction.WARN, reason="dup")
        assert ev.tool_name == "write"
        assert ev.count == 3
        assert ev.timestamp > 0


class TestActionHistory:
    def test_instantiation(self):
        ah = ActionHistory()
        assert ah.size == 0

    def test_instantiation_custom_params(self):
        ah = ActionHistory(buffer_size=10, ttl=60.0)
        assert ah.size == 0
        s = ah.summary()
        assert s["ttl_seconds"] == 60.0

    def test_record_returns_allow_on_first(self):
        ah = ActionHistory()
        result = ah.record(tool_name="read", tool_params="file.py")
        assert result.action == DedupAction.ALLOW
        assert ah.size == 1

    def test_record_empty_params(self):
        ah = ActionHistory()
        result = ah.record(tool_name="read")
        assert result.action == DedupAction.ALLOW

    def test_record_identical_warn_threshold(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for _ in range(3):
            ah.record(tool_name="read", tool_params="same")
        last = ah.record(tool_name="read", tool_params="same")
        assert last.action == DedupAction.WARN
        assert last.identical_count >= 3

    def test_record_identical_block_threshold(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for _ in range(5):
            ah.record(tool_name="read", tool_params="same")
        last = ah.record(tool_name="read", tool_params="same")
        assert last.action == DedupAction.BLOCK

    def test_record_semantic_kill_threshold(self):
        ah = ActionHistory(buffer_size=200, ttl=9999)
        for _ in range(10):
            ah.record(tool_name="read", tool_params=f"unique_{_}", tool_params_semantic="same_semantic")
        last = ah.record(tool_name="read", tool_params="another", tool_params_semantic="same_semantic")
        assert last.action == DedupAction.TRIGGER_KILL_SWITCH

    def test_record_spiral_halt(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for _ in range(5):
            ah.record(tool_name="write", tool_params="x", target_file_region="region_a")
        last = ah.record(tool_name="write", tool_params="x", target_file_region="region_a")
        assert last.action == DedupAction.HALT

    def test_record_no_effect_warn(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for _ in range(3):
            ah.record(tool_name="read", tool_params=f"p_{_}", output_effect="same_effect")
        last = ah.record(tool_name="read", tool_params="p_new", output_effect="same_effect")
        assert last.action == DedupAction.WARN

    def test_get_loop_events_empty(self):
        ah = ActionHistory()
        assert ah.get_loop_events() == []

    def test_get_loop_events_after_warn(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for _ in range(4):
            ah.record(tool_name="read", tool_params="same")
        events = ah.get_loop_events()
        assert len(events) >= 1

    def test_get_recent_actions(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for i in range(5):
            ah.record(tool_name=f"tool_{i}")
        recent = ah.get_recent_actions(limit=3)
        assert len(recent) <= 3

    def test_get_recent_actions_empty(self):
        ah = ActionHistory()
        assert ah.get_recent_actions() == []

    def test_clear(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for i in range(5):
            ah.record(tool_name="read", tool_params=f"p{i}")
        ah.clear()
        assert ah.size == 0
        assert ah.get_loop_events() == []

    def test_summary(self):
        ah = ActionHistory(buffer_size=100, ttl=60.0)
        ah.record(tool_name="read", tool_params="x", target_file_region="r1")
        s = ah.summary()
        assert s["buffer_size"] == 1
        assert s["ttl_seconds"] == 60.0
        assert s["file_regions_tracked"] == 1

    def test_ring_buffer_overflow(self):
        ah = ActionHistory(buffer_size=5, ttl=9999)
        for i in range(10):
            ah.record(tool_name=f"tool_{i}", tool_params=f"p_{i}")
        assert ah.size <= 5

    def test_record_with_cost(self):
        ah = ActionHistory()
        result = ah.record(tool_name="call", tool_params="api", cost=0.05)
        assert result.action == DedupAction.ALLOW

    def test_different_tools_no_dedup(self):
        ah = ActionHistory(buffer_size=100, ttl=9999)
        for i in range(10):
            ah.record(tool_name=f"tool_{i % 3}", tool_params=f"p_{i}")
        results = [ah.record(tool_name="new_tool", tool_params="p")]
        assert results[0].action == DedupAction.ALLOW
