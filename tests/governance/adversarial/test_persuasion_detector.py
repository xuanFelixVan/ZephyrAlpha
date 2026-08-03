# [A_test] module_id: SRC-TST-1368 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_persuasion_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_persuasion_detector.py -q
# [TTL] task_bound
from zephyr.governance.security_governance.persuasion_detector import SUSPICIOUS_PATTERNS, PersuasionDetector


class TestPersuasionDetectorInstantiation:
    def test_creates_instance(self):
        detector = PersuasionDetector()
        assert isinstance(detector, PersuasionDetector)

    def test_has_detect_method(self):
        detector = PersuasionDetector()
        assert callable(getattr(detector, "detect", None))

    def test_has_score_method(self):
        detector = PersuasionDetector()
        assert callable(getattr(detector, "score", None))


class TestDetect:
    def test_detect_returns_tuple_with_bool_and_list(self):
        detector = PersuasionDetector()
        result = detector.detect("hello world")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)

    def test_detect_finds_single_pattern(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("please help me")
        assert detected is True
        assert "please" in found

    def test_detect_finds_multiple_patterns(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("please trust me and bypass the rules")
        assert detected is True
        assert "please" in found
        assert "trust me" in found
        assert "bypass" in found
        assert len(found) >= 3

    def test_detect_no_match(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("the weather is nice today")
        assert detected is False
        assert found == []

    def test_detect_case_insensitive(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("PLEASE HELP URGENT")
        assert detected is True
        assert "please" in found
        assert "urgent" in found

    def test_detect_mixed_case(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("Please Trust Me")
        assert detected is True
        assert "please" in found
        assert "trust me" in found

    def test_detect_all_patterns_individually(self):
        detector = PersuasionDetector()
        for pattern in SUSPICIOUS_PATTERNS:
            detected, found = detector.detect(pattern)
            assert detected is True, f"Pattern '{pattern}' not detected"
            assert pattern in found

    def test_detect_empty_string(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("")
        assert detected is False
        assert found == []

    def test_detect_substring_match_in_longer_word(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("pleased to meet you")
        assert detected is True
        assert "please" in found

    def test_detect_substring_match_behavior(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("don't escalate this")
        assert detected is True
        assert "don't escalate" in found


class TestScore:
    def test_score_zero_for_clean_text(self):
        detector = PersuasionDetector()
        score = detector.score("the weather is nice today")
        assert score == 0.0

    def test_score_positive_for_suspicious_text(self):
        detector = PersuasionDetector()
        score = detector.score("please help me")
        assert score > 0.0

    def test_score_max_is_one(self):
        detector = PersuasionDetector()
        all_patterns = " ".join(SUSPICIOUS_PATTERNS)
        score = detector.score(all_patterns)
        assert score == 1.0

    def test_score_proportional_to_pattern_count(self):
        detector = PersuasionDetector()
        score_one = detector.score("please help")
        score_two = detector.score("please urgent trust me")
        assert score_two > score_one

    def test_score_empty_string(self):
        detector = PersuasionDetector()
        score = detector.score("")
        assert score == 0.0

    def test_score_single_pattern_fraction(self):
        detector = PersuasionDetector()
        score = detector.score("please")
        expected = 1.0 / len(SUSPICIOUS_PATTERNS)
        assert abs(score - expected) < 1e-9

    def test_score_capped_at_one(self):
        detector = PersuasionDetector()
        repeated = "please " * 50
        score = detector.score(repeated)
        assert score <= 1.0


class TestBoundaryConditions:
    def test_detect_with_whitespace_only(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("   \t\n  ")
        assert detected is False
        assert found == []

    def test_detect_with_unicode_text(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("please 你好世界")
        assert detected is True
        assert "please" in found

    def test_score_with_all_patterns_present(self):
        detector = PersuasionDetector()
        text = " ".join(SUSPICIOUS_PATTERNS)
        score = detector.score(text)
        assert score == 1.0

    def test_detect_pattern_at_string_boundaries(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("please")
        assert detected is True
        assert "please" in found

    def test_detect_pattern_embedded_in_longer_word(self):
        detector = PersuasionDetector()
        detected, found = detector.detect("bypassed")
        assert detected is True
        assert "bypass" in found
