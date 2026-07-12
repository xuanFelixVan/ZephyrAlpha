# [A_test] module_id: SRC-TST-1264 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_meta_guard_latency_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.meta_guard_latency_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_meta_guard_latency_budget.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.meta_guard_latency_budget import MetaGuardLatencyBudget


class TestMetaGuardLatencyBudgetInstantiation:
    def test_default_instantiation(self):
        mglb = MetaGuardLatencyBudget()
        assert mglb.guard_latencies == {}
        assert mglb.max_samples_per_guard == 50
        assert mglb.poll_interval_seconds == 60.0
        assert mglb.budget_ratio == 0.2
        assert mglb.max_total_latency_ms == 5000.0
        assert mglb.downgraded_guards == set()
        assert mglb.priority_ranking == {}

    def test_custom_instantiation(self):
        mglb = MetaGuardLatencyBudget(
            guard_latencies={"g1": [10.0]},
            max_samples_per_guard=100,
            poll_interval_seconds=30.0,
            budget_ratio=0.1,
            max_total_latency_ms=3000.0,
            downgraded_guards={"g2"},
            priority_ranking={"g1": 0.9},
        )
        assert mglb.max_samples_per_guard == 100
        assert mglb.poll_interval_seconds == 30.0
        assert "g2" in mglb.downgraded_guards


class TestRecordLatency:
    def test_record_new_guard(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("guard_a", 100.0)
        assert "guard_a" in mglb.guard_latencies
        assert mglb.guard_latencies["guard_a"] == [100.0]

    def test_record_multiple_samples(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("guard_a", 100.0)
        mglb.record_latency("guard_a", 200.0)
        assert len(mglb.guard_latencies["guard_a"]) == 2

    def test_record_trims_to_max_samples(self):
        mglb = MetaGuardLatencyBudget(max_samples_per_guard=3)
        for i in range(5):
            mglb.record_latency("guard_a", float(i * 10))
        assert len(mglb.guard_latencies["guard_a"]) == 3
        assert mglb.guard_latencies["guard_a"] == [20.0, 30.0, 40.0]

    def test_record_multiple_guards(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("g1", 10.0)
        mglb.record_latency("g2", 20.0)
        assert len(mglb.guard_latencies) == 2

    def test_record_zero_latency(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("guard_a", 0.0)
        assert mglb.guard_latencies["guard_a"] == [0.0]


class TestCheckBudget:
    def test_check_budget_under_budget(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("g1", 10.0)
        result = mglb.check_budget()
        assert result["over_budget"] is False

    def test_check_budget_over_total_latency(self):
        mglb = MetaGuardLatencyBudget(max_total_latency_ms=50.0)
        mglb.record_latency("g1", 100.0)
        result = mglb.check_budget()
        assert result["over_budget"] is True

    def test_check_budget_empty_guards(self):
        mglb = MetaGuardLatencyBudget()
        result = mglb.check_budget()
        assert result["over_budget"] is False
        assert result["guard_count"] == 0

    def test_check_budget_returns_required_keys(self):
        mglb = MetaGuardLatencyBudget()
        mglb.record_latency("g1", 10.0)
        result = mglb.check_budget()
        for key in (
            "over_budget",
            "total_avg_latency_ms",
            "budget_used_ratio",
            "max_total_latency_ms",
            "guard_count",
            "downgraded_guards",
            "per_guard_avg",
        ):
            assert key in result


class TestIsActive:
    def test_active_guard(self):
        mglb = MetaGuardLatencyBudget()
        assert mglb.is_active("g1") is True

    def test_downgraded_guard(self):
        mglb = MetaGuardLatencyBudget(downgraded_guards={"g1"})
        assert mglb.is_active("g1") is False

    def test_unknown_guard_is_active(self):
        mglb = MetaGuardLatencyBudget()
        assert mglb.is_active("unknown") is True


class TestSetPriority:
    def test_set_priority(self):
        mglb = MetaGuardLatencyBudget()
        mglb.set_priority("g1", 0.9)
        assert mglb.priority_ranking["g1"] == 0.9

    def test_overwrite_priority(self):
        mglb = MetaGuardLatencyBudget()
        mglb.set_priority("g1", 0.5)
        mglb.set_priority("g1", 0.1)
        assert mglb.priority_ranking["g1"] == 0.1


class TestRestoreAll:
    def test_restore_all_clears_downgraded(self):
        mglb = MetaGuardLatencyBudget(downgraded_guards={"g1", "g2"})
        mglb.restore_all()
        assert len(mglb.downgraded_guards) == 0

    def test_restore_all_makes_guards_active(self):
        mglb = MetaGuardLatencyBudget(downgraded_guards={"g1"})
        mglb.restore_all()
        assert mglb.is_active("g1") is True

    def test_restore_all_on_empty(self):
        mglb = MetaGuardLatencyBudget()
        mglb.restore_all()
        assert len(mglb.downgraded_guards) == 0
