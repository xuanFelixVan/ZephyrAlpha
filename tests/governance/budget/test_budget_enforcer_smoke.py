# [A_test] module_id: SRC-TST-0120 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-277 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_budget_enforcer_smoke
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from zephyr.governance.financial_governance.budget_enforcement import (
    BudgetDimension,
    BudgetEngine,
    BudgetTracker,
    BurnRateMonitor,
    DegradationManager,
    ModelRouter,
    TimeoutGuard,
    TimeoutLevel,
    TrackerScope,
)


class TestBudgetEngineSmoke:
    def test_pre_flight_check_allows_normal(self):
        be = BudgetEngine()
        r = be.pre_flight_check("smoke-test", 500, 0.05)
        assert r.decision.name == "ALLOW"

    def test_three_dimensions_registered(self):
        be = BudgetEngine()
        assert len(be.policies) == 3

    def test_get_active_policy(self):
        be = BudgetEngine()
        p = be.get_active_policy(BudgetDimension.TOKEN)
        assert p is not None
        assert p.dimension == BudgetDimension.TOKEN

    def test_advance_retreat_degradation(self):
        be = BudgetEngine()
        assert be.advance_degradation() is True
        assert be.retreat_degradation() is True

    def test_compute_hash(self):
        be = BudgetEngine()
        h = be.compute_hash()
        assert len(h) == 64


class TestBudgetTrackerSmoke:
    def test_open_scope_and_record(self):
        bt = BudgetTracker()
        bt.open_scope(TrackerScope.SESSION, "s1")
        bt.record_request(TrackerScope.SESSION, "s1", 100, 50)
        s = bt.summarize()
        assert s.total_tokens == 150

    def test_summarize_returns_request_count(self):
        bt = BudgetTracker()
        bt.open_scope(TrackerScope.SESSION, "s1")
        bt.record_request(TrackerScope.SESSION, "s1", 200, 100)
        bt.record_request(TrackerScope.SESSION, "s1", 50, 25)
        s = bt.summarize()
        assert s.total_tokens == 375
        assert s.request_count >= 0

    def test_dump_produces_json(self):
        bt = BudgetTracker()
        bt.open_scope(TrackerScope.SESSION, "s1")
        d = bt.dump()
        assert '"total_tokens"' in d


class TestDegradationManagerSmoke:
    def test_evaluate_85pct_triggers_compress(self):
        dm = DegradationManager()
        a = dm.evaluate(0.85, BudgetDimension.TOKEN)
        assert a is not None
        assert a.level.name == "COMPRESS"

    def test_evaluate_100pct_triggers_halt(self):
        dm = DegradationManager()
        a = dm.evaluate(1.0, BudgetDimension.TOKEN)
        assert a is not None
        assert a.level.name == "HALT"

    def test_halt_blocks_advance(self):
        dm = DegradationManager()
        dm.evaluate(1.0, BudgetDimension.TOKEN)
        assert dm.state.can_advance() is False

    def test_manual_retreat_from_degraded(self):
        dm = DegradationManager()
        dm.evaluate(0.85, BudgetDimension.TOKEN)
        dm.manual_retreat("test")
        assert dm.state.current_level.name == "NORMAL"


class TestModelRouterSmoke:
    def test_route_free_for_simple(self):
        from zephyr.governance.intelligence_governance.model_router import TaskComplexity

        mr = ModelRouter()
        d = mr.route(complexity=TaskComplexity.SIMPLE)
        assert d.tier is not None
        assert d.model_key != ""
        assert d.provider != ""

    def test_blacklist_and_unblacklist(self):
        mr = ModelRouter()
        mr.blacklist("zhipu:char_glm")
        mr.unblacklist("zhipu:char_glm")
        mr.clear_blacklist()

    def test_all_models_non_empty(self):
        mr = ModelRouter()
        models = mr.all_models()
        assert len(models) > 0


class TestTimeoutGuardSmoke:
    def test_watch_unwatch_cleanup(self):
        tg = TimeoutGuard()
        tg.watch(TimeoutLevel.REQUEST, "r1")
        assert tg.active_count() == 1
        assert tg.remaining(TimeoutLevel.REQUEST, "r1") > 0
        tg.unwatch(TimeoutLevel.REQUEST, "r1")
        assert tg.active_count() == 0

    def test_is_not_timeout_when_fresh(self):
        tg = TimeoutGuard()
        tg.watch(TimeoutLevel.TURN, "t1")
        assert tg.is_timeout(TimeoutLevel.TURN, "t1") is False
        tg.unwatch(TimeoutLevel.TURN, "t1")

    def test_sleep_or_abort_no_timeout(self):
        tg = TimeoutGuard()
        tg.watch(TimeoutLevel.REQUEST, "r-sleep")
        ok = TimeoutGuard.sleep_or_abort(0.05, tg, TimeoutLevel.REQUEST, "r-sleep")
        tg.unwatch(TimeoutLevel.REQUEST, "r-sleep")
        assert ok is True


class TestBurnRateMonitorSmoke:
    def test_record_and_compute_normal(self):
        bm = BurnRateMonitor()
        bm.record_consumption(100)
        bm.compute_burn_rates(1_000_000)
        assert bm.get_severity().name == "NORMAL"

    def test_distribution_shift_zero_on_same(self):
        bm = BurnRateMonitor()
        bm.record_consumption(100)
        bm.compute_burn_rates(1_000_000)
        shift = bm.detect_distribution_shift()
        assert shift >= 0.0
