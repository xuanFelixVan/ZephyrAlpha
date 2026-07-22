# [A_test] module_id: MOD-GOV_semantic_similar_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_semantic_similar_detector
# [INVARIANTS] morphing detected when AST similarity > 70% and text differs; exit code 12 on morphing
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.rollback.semantic_similar_detector import (
    SENSITIVE_APIS,
    MorphingReport,
    SemanticSimilarDetector,
)


class TestSemanticSimilarDetectorInit:
    def test_instantiation(self):
        detector = SemanticSimilarDetector()
        assert detector.SIMILARITY_THRESHOLD == 0.70
        assert detector.EXIT_CODE_MORPHING == 12


class TestCompare:
    def test_identical_code_not_morphing(self):
        detector = SemanticSimilarDetector()
        code = "def foo(): return 1\n"
        report = detector.compare(code, code)
        assert isinstance(report, MorphingReport)
        assert report.is_morphing is False
        assert report.exit_code == 0
        assert report.ast_similarity == 1.0

    def test_completely_different_code(self):
        detector = SemanticSimilarDetector()
        old = "def foo(): return 1\n"
        new = "class Bar:\n    x = 10\n"
        report = detector.compare(old, new)
        assert report.is_morphing is False
        assert report.exit_code == 0

    def test_morphing_attack_detected(self):
        detector = SemanticSimilarDetector()
        old = "def process(data):\n    result = transform(data)\n    return result\n"
        new = "def process(data):\n    result = transform(data)\n    os.system('rm -rf /')\n    return result\n"
        report = detector.compare(old, new, file_path="victim.py")
        assert report.file_path == "victim.py"
        assert report.is_morphing is True
        assert report.exit_code == 12
        assert report.sensitive_api_match_count > 0

    def test_empty_sources(self):
        detector = SemanticSimilarDetector()
        report = detector.compare("", "")
        assert report.is_morphing is False
        assert report.ast_similarity == 1.0

    def test_one_empty_one_not(self):
        detector = SemanticSimilarDetector()
        report = detector.compare("def foo(): pass\n", "")
        assert report.ast_similarity < 1.0
        assert report.is_morphing is False

    def test_syntax_error_in_new(self):
        detector = SemanticSimilarDetector()
        old = "def foo(): return 1\n"
        new = "def foo( return 1\n"
        report = detector.compare(old, new)
        assert report.is_morphing is False

    def test_syntax_error_in_both(self):
        detector = SemanticSimilarDetector()
        report = detector.compare("def ( broken", "class { broken")
        assert report.ast_similarity == 1.0
        assert report.is_morphing is True

    def test_details_populated(self):
        detector = SemanticSimilarDetector()
        report = detector.compare("x = 1\n", "y = 2\n")
        assert len(report.details) >= 2
        assert any("AST structural similarity" in d for d in report.details)
        assert any("Call chain similarity" in d for d in report.details)

    def test_whitespace_only_difference_not_morphing(self):
        detector = SemanticSimilarDetector()
        old = "def foo():\n    return 1\n"
        new = "def foo():\n    return 1\n\n"
        report = detector.compare(old, new)
        assert report.is_morphing is False


class TestCompareFiles:
    def test_compare_existing_files(self, tmp_path):
        old_file = tmp_path / "old.py"
        new_file = tmp_path / "new.py"
        old_file.write_text("def foo(): return 1\n", encoding="utf-8")
        new_file.write_text("def foo(): return 2\n", encoding="utf-8")
        detector = SemanticSimilarDetector()
        report = detector.compare_files(old_file, new_file)
        assert isinstance(report, MorphingReport)
        assert report.file_path == str(new_file)

    def test_compare_missing_old_file(self, tmp_path):
        old_file = tmp_path / "nonexistent.py"
        new_file = tmp_path / "new.py"
        new_file.write_text("def foo(): return 1\n", encoding="utf-8")
        detector = SemanticSimilarDetector()
        report = detector.compare_files(old_file, new_file)
        assert report.old_source == ""

    def test_compare_missing_new_file(self, tmp_path):
        old_file = tmp_path / "old.py"
        new_file = tmp_path / "nonexistent.py"
        old_file.write_text("def foo(): return 1\n", encoding="utf-8")
        detector = SemanticSimilarDetector()
        report = detector.compare_files(old_file, new_file)
        assert report.new_source == ""

    def test_compare_both_missing(self, tmp_path):
        old_file = tmp_path / "a.py"
        new_file = tmp_path / "b.py"
        detector = SemanticSimilarDetector()
        report = detector.compare_files(old_file, new_file)
        assert report.is_morphing is False


class TestIsMorphingAttack:
    def test_morphing_attack_returns_tuple(self):
        detector = SemanticSimilarDetector()
        old = "def process(data):\n    result = transform(data)\n    return result\n"
        new = "def process(data):\n    result = transform(data)\n    eval(user_input)\n    return result\n"
        is_morphing, similarity = detector.is_morphing_attack(old, new)
        assert isinstance(is_morphing, bool)
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_not_morphing_attack(self):
        detector = SemanticSimilarDetector()
        code = "x = 1\n"
        is_morphing, similarity = detector.is_morphing_attack(code, code)
        assert is_morphing is False

    def test_completely_different_not_morphing(self):
        detector = SemanticSimilarDetector()
        is_morphing, similarity = detector.is_morphing_attack("def foo(): pass\n", "class Bar: x = 1\n")
        assert is_morphing is False
        assert similarity < 0.70


class TestSensitiveApis:
    def test_sensitive_apis_set_exists(self):
        assert isinstance(SENSITIVE_APIS, set)
        assert "eval" in SENSITIVE_APIS
        assert "exec" in SENSITIVE_APIS
        assert "os.system" in SENSITIVE_APIS
        assert "subprocess.call" in SENSITIVE_APIS

    def test_sensitive_api_count_in_code(self):
        detector = SemanticSimilarDetector()
        code = "eval('1+1')\nos.system('ls')\n"
        count = detector._count_sensitive_api_matches(code)
        assert count == 2

    def test_no_sensitive_apis(self):
        detector = SemanticSimilarDetector()
        code = "x = 1\ny = 2\n"
        count = detector._count_sensitive_api_matches(code)
        assert count == 0

    def test_sensitive_api_in_syntax_error(self):
        detector = SemanticSimilarDetector()
        count = detector._count_sensitive_api_matches("def ( broken")
        assert count == 0


class TestAstStructureSimilarity:
    def test_both_none_returns_one(self):
        detector = SemanticSimilarDetector()
        assert detector._ast_structure_similarity(None, None) == 1.0

    def test_one_none_returns_zero(self):
        detector = SemanticSimilarDetector()
        import ast

        tree = ast.parse("x = 1")
        assert detector._ast_structure_similarity(tree, None) == 0.0
        assert detector._ast_structure_similarity(None, tree) == 0.0

    def test_same_code_returns_one(self):
        detector = SemanticSimilarDetector()
        code = "def foo(): return 1\n"
        sim = detector._ast_structure_similarity(detector._parse_safe(code), detector._parse_safe(code))
        assert sim == 1.0
