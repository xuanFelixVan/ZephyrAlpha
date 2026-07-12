# [A_test] module_id: SRC-TST-1035 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_fragmentation_index
# [INVARIANTS] entropy_0_to_1;alert_when_gt_0_7;zero_total_entropy_0
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_fragmentation_index.py
# [TTL] task_bound

from zephyr.gov_kb.fragmentation_index import FragmentationIndex, FragmentationScore


class TestFragmentationScore:
    def test_creation(self):
        s = FragmentationScore(
            ke_count_by_domain={"risk": 10, "infra": 5},
            total_ke=15,
            entropy=0.65,
            alert=False,
        )
        assert s.total_ke == 15
        assert s.entropy == 0.65
        assert s.alert is False


class TestFragmentationIndex:
    def test_empty_counts(self):
        idx = FragmentationIndex()
        result = idx.compute({})
        assert result.total_ke == 0
        assert result.entropy == 0.0
        assert result.alert is False

    def test_all_zero_counts(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 0, "b": 0})
        assert result.total_ke == 0
        assert result.entropy == 0.0

    def test_single_domain_low_entropy(self):
        idx = FragmentationIndex()
        result = idx.compute({"risk": 100})
        assert result.entropy == 0.0
        assert result.alert is False

    def test_uniform_distribution_high_entropy(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 10, "b": 10, "c": 10, "d": 10, "e": 10})
        assert result.entropy > 0.7
        assert result.alert is True

    def test_skewed_distribution_low_entropy(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 100, "b": 1, "c": 1})
        assert result.entropy < 0.7
        assert result.alert is False

    def test_entropy_between_0_and_1(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 10, "b": 20, "c": 30})
        assert 0.0 <= result.entropy <= 1.0

    def test_total_ke_correct(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 10, "b": 20, "c": 30})
        assert result.total_ke == 60

    def test_ke_count_by_domain_preserved(self):
        idx = FragmentationIndex()
        counts = {"risk": 5, "infra": 3}
        result = idx.compute(counts)
        assert result.ke_count_by_domain == counts

    def test_entropy_rounded_to_3_decimals(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 10, "b": 20, "c": 30})
        assert result.entropy == round(result.entropy, 3)

    def test_two_domains_moderate_entropy(self):
        idx = FragmentationIndex()
        result = idx.compute({"a": 50, "b": 50})
        assert 0.0 < result.entropy <= 1.0
