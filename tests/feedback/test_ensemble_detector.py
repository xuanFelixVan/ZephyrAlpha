# [A_test] module_id: SRC-TST-0839 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_ensemble_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ensemble_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.ensemble_detector import EnsembleDetector


class TestEnsembleDetectorInstantiation:
    def test_default_instantiation(self):
        detector = EnsembleDetector()
        assert detector is not None
        assert detector.detectors == []

    def test_with_detector_names(self):
        detector = EnsembleDetector(detectors=["zscore", "isolation_forest", "dbscan"])
        assert len(detector.detectors) == 3

    def test_is_dataclass(self):
        detector = EnsembleDetector()
        assert hasattr(detector, "__dataclass_fields__")


class TestVote:
    def test_majority_above_threshold_returns_true(self):
        detector = EnsembleDetector()
        scores = {"zscore": 3.0, "isolation": 2.6, "dbscan": 1.0}
        result = detector.vote(scores)
        assert result is True

    def test_minority_above_threshold_returns_false(self):
        detector = EnsembleDetector()
        scores = {"zscore": 1.0, "isolation": 1.0, "dbscan": 3.0}
        result = detector.vote(scores)
        assert result is False

    def test_all_above_threshold(self):
        detector = EnsembleDetector()
        scores = {"zscore": 3.0, "isolation": 4.0, "dbscan": 5.0}
        result = detector.vote(scores)
        assert result is True

    def test_all_below_threshold(self):
        detector = EnsembleDetector()
        scores = {"zscore": 1.0, "isolation": 2.0, "dbscan": 0.5}
        result = detector.vote(scores)
        assert result is False

    def test_empty_scores(self):
        detector = EnsembleDetector()
        result = detector.vote({})
        assert result is False

    def test_single_detector_above(self):
        detector = EnsembleDetector()
        result = detector.vote({"zscore": 3.0})
        assert result is True

    def test_single_detector_below(self):
        detector = EnsembleDetector()
        result = detector.vote({"zscore": 1.0})
        assert result is False

    def test_two_detectors_one_above(self):
        detector = EnsembleDetector()
        result = detector.vote({"a": 3.0, "b": 1.0})
        assert result is False

    def test_two_detectors_both_above(self):
        detector = EnsembleDetector()
        result = detector.vote({"a": 3.0, "b": 2.6})
        assert result is True

    def test_exact_threshold_boundary(self):
        detector = EnsembleDetector()
        result = detector.vote({"a": 2.5})
        assert result is False
