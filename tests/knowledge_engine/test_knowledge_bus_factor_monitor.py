# [A_test] module_id: SRC-TST-1191 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_knowledge_bus_factor_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.knowledge_bus_factor_monitor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_knowledge_bus_factor_monitor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.knowledge_bus_factor_monitor import KnowledgeBusFactorMonitor


class TestKnowledgeBusFactorMonitorInstantiation:
    def test_default_instantiation(self):
        mon = KnowledgeBusFactorMonitor()
        assert mon.min_bus_factor == 2
        assert mon.max_owner_assignments == 5
        assert mon.subsystem_owners == {}
        assert mon.human_assignments == {}
        assert mon.bus_factor_alerts == []

    def test_custom_parameters(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=3, max_owner_assignments=8)
        assert mon.min_bus_factor == 3
        assert mon.max_owner_assignments == 8


class TestRegisterSubsystem:
    def test_register_single_owner(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice"])
        assert "auth" in mon.subsystem_owners
        assert mon.subsystem_owners["auth"] == ["alice"]

    def test_register_multiple_owners(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("db", ["alice", "bob"])
        assert len(mon.subsystem_owners["db"]) == 2

    def test_human_assignments_updated(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice"])
        mon.register_subsystem("db", ["alice"])
        assert len(mon.human_assignments["alice"]) == 2

    def test_no_duplicate_subsystem_in_human_assignments(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice"])
        mon.register_subsystem("auth", ["alice"])
        assert mon.human_assignments["alice"].count("auth") == 1

    def test_empty_owners_list(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("orphan", [])
        assert mon.subsystem_owners["orphan"] == []


class TestRemoveOwner:
    def test_remove_existing_owner(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice", "bob"])
        mon.remove_owner("auth", "alice")
        assert "alice" not in mon.subsystem_owners["auth"]
        assert "bob" in mon.subsystem_owners["auth"]

    def test_remove_nonexistent_owner(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice"])
        mon.remove_owner("auth", "charlie")
        assert mon.subsystem_owners["auth"] == ["alice"]

    def test_remove_from_human_assignments(self):
        mon = KnowledgeBusFactorMonitor()
        mon.register_subsystem("auth", ["alice"])
        mon.remove_owner("auth", "alice")
        assert "auth" not in mon.human_assignments["alice"]

    def test_remove_from_nonexistent_subsystem(self):
        mon = KnowledgeBusFactorMonitor()
        mon.remove_owner("nonexistent", "alice")
        assert mon.subsystem_owners == {}


class TestCheckBusFactor:
    def test_no_subsystems(self):
        mon = KnowledgeBusFactorMonitor()
        result = mon.check_bus_factor()
        assert result["critical_subsystems"] == []
        assert result["total_subsystems"] == 0
        assert result["overall_bus_factor_health"] == 1.0

    def test_healthy_subsystem(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("auth", ["alice", "bob"])
        result = mon.check_bus_factor()
        assert "auth" not in result["critical_subsystems"]

    def test_critical_subsystem_zero_owners(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("orphan", [])
        result = mon.check_bus_factor()
        assert "orphan" in result["critical_subsystems"]

    def test_critical_subsystem_single_owner(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("single", ["alice"])
        result = mon.check_bus_factor()
        assert "single" in result["critical_subsystems"]

    def test_overloaded_owner_alert(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2, max_owner_assignments=2)
        mon.register_subsystem("s1", ["alice"])
        mon.register_subsystem("s2", ["alice"])
        mon.register_subsystem("s3", ["alice"])
        result = mon.check_bus_factor()
        overload_alerts = [a for a in result["alerts"] if "human_owner" in a]
        assert len(overload_alerts) >= 1

    def test_alerts_appended_to_bus_factor_alerts(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("single", ["alice"])
        mon.check_bus_factor()
        assert len(mon.bus_factor_alerts) > 0


class TestGetKnowledgeHeatmap:
    def test_empty_heatmap(self):
        mon = KnowledgeBusFactorMonitor()
        assert mon.get_knowledge_heatmap() == {}

    def test_safe_subsystem(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("auth", ["alice", "bob"])
        heatmap = mon.get_knowledge_heatmap()
        assert heatmap["auth"]["risk_level"] == "SAFE"

    def test_at_risk_subsystem(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("single", ["alice"])
        heatmap = mon.get_knowledge_heatmap()
        assert heatmap["single"]["risk_level"] == "AT_RISK"

    def test_orphaned_subsystem(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("orphan", [])
        heatmap = mon.get_knowledge_heatmap()
        assert heatmap["orphan"]["risk_level"] == "ORPHANED"


class TestSuggestKnowledgeTransfer:
    def test_no_suggestions_when_healthy(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("auth", ["alice", "bob"])
        assert mon.suggest_knowledge_transfer() == []

    def test_suggestion_for_understaffed_subsystem(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2, max_owner_assignments=5)
        mon.register_subsystem("single", ["alice"])
        mon.register_subsystem("healthy", ["bob", "charlie"])
        suggestions = mon.suggest_knowledge_transfer()
        assert len(suggestions) >= 1
        assert suggestions[0]["subsystem"] == "single"

    def test_no_suggestions_empty_monitor(self):
        mon = KnowledgeBusFactorMonitor()
        assert mon.suggest_knowledge_transfer() == []


class TestOverallBusFactorScore:
    def test_empty_returns_one(self):
        mon = KnowledgeBusFactorMonitor()
        assert mon.overall_bus_factor_score() == 1.0

    def test_all_safe(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("s1", ["a", "b"])
        mon.register_subsystem("s2", ["c", "d"])
        assert mon.overall_bus_factor_score() == 1.0

    def test_mixed_health(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("safe", ["a", "b"])
        mon.register_subsystem("risky", ["c"])
        score = mon.overall_bus_factor_score()
        assert 0.0 < score < 1.0

    def test_all_critical(self):
        mon = KnowledgeBusFactorMonitor(min_bus_factor=2)
        mon.register_subsystem("s1", ["a"])
        mon.register_subsystem("s2", ["b"])
        assert mon.overall_bus_factor_score() == 0.0
