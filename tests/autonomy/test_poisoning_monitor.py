# [A_test] module_id: MOD-GOV_poisoning_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_poisoning_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_poisoning_monitor.py -q
# [TTL] task_bound
from zephyr.security.llm_defense.llm_security.poisoning_monitor import PoisoningMonitor, PoisoningRisk


class TestPoisoningRisk:
    def test_dataclass_fields(self):
        risk = PoisoningRisk(
            ke_id="KE-001",
            cosine_to_nearest=0.95,
            cosine_to_centroid=0.86,
            likely_poisoned=False,
            score_delta=0.0,
        )
        assert risk.ke_id == "KE-001"
        assert risk.cosine_to_nearest == 0.95
        assert risk.cosine_to_centroid == 0.86
        assert risk.likely_poisoned is False
        assert risk.score_delta == 0.0

    def test_poisoned_flag_true(self):
        risk = PoisoningRisk(
            ke_id="KE-002",
            cosine_to_nearest=0.99,
            cosine_to_centroid=0.30,
            likely_poisoned=True,
            score_delta=0.5,
        )
        assert risk.likely_poisoned is True
        assert risk.score_delta > 0.0

    def test_equality(self):
        a = PoisoningRisk(
            ke_id="X", cosine_to_nearest=0.9, cosine_to_centroid=0.8, likely_poisoned=False, score_delta=0.0
        )
        b = PoisoningRisk(
            ke_id="X", cosine_to_nearest=0.9, cosine_to_centroid=0.8, likely_poisoned=False, score_delta=0.0
        )
        assert a == b


class TestPoisoningMonitorInstantiation:
    def test_create_instance(self):
        monitor = PoisoningMonitor()
        assert monitor is not None

    def test_has_analyze_method(self):
        monitor = PoisoningMonitor()
        assert callable(getattr(monitor, "analyze", None))


class TestPoisoningMonitorAnalyze:
    def test_analyze_returns_risk(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-001", [[0.1, 0.2, 0.3]])
        assert isinstance(result, PoisoningRisk)

    def test_analyze_preserves_ke_id(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-042", [[0.1, 0.2]])
        assert result.ke_id == "KE-042"

    def test_analyze_cosine_values_in_range(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-001", [[0.5, 0.5]])
        assert -1.0 <= result.cosine_to_nearest <= 1.0
        assert -1.0 <= result.cosine_to_centroid <= 1.0

    def test_analyze_default_not_poisoned(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-001", [[0.1, 0.2, 0.3]])
        assert result.likely_poisoned is False

    def test_analyze_score_delta_default_zero(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-001", [[0.1, 0.2, 0.3]])
        assert result.score_delta == 0.0

    def test_analyze_empty_embeddings(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("KE-EMPTY", [])
        assert isinstance(result, PoisoningRisk)
        assert result.ke_id == "KE-EMPTY"

    def test_analyze_multiple_embeddings(self):
        monitor = PoisoningMonitor()
        embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        result = monitor.analyze("KE-MULTI", embeddings)
        assert isinstance(result, PoisoningRisk)

    def test_analyze_empty_ke_id(self):
        monitor = PoisoningMonitor()
        result = monitor.analyze("", [[0.1]])
        assert result.ke_id == ""
