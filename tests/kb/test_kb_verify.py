# [A_test] module_id: SRC-TST-1180 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_verify
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_kb.verify import FactChecker, FactResult


class TestFactResult:
    def test_create_fact_result(self):
        fr = FactResult(
            fact_type="file_exists",
            target="/some/path",
            verified=True,
            confidence=1.0,
        )
        assert fr.fact_type == "file_exists"
        assert fr.verified is True
        assert fr.confidence == 1.0
        assert fr.error == ""

    def test_fact_result_with_error(self):
        fr = FactResult(
            fact_type="unknown",
            target="x",
            verified=False,
            confidence=0.0,
            error="some error",
        )
        assert fr.error == "some error"


class TestFactChecker:
    def test_init_default_root(self):
        fc = FactChecker()
        assert fc._root is not None

    def test_init_custom_root(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        assert fc._root == tmp_path

    def test_verify_file_exists_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        f = tmp_path / "test_file.txt"
        f.write_text("hello", encoding="utf-8")
        result = fc.verify("file_exists", path=str(f))
        assert result.verified is True
        assert result.confidence == 1.0

    def test_verify_file_exists_false(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("file_exists", path="nonexistent_file.txt")
        assert result.verified is False
        assert result.confidence == 0.0

    def test_verify_file_contains_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        f = tmp_path / "doc.txt"
        f.write_text("hello world", encoding="utf-8")
        result = fc.verify("file_contains", path=str(f), needle="world")
        assert result.verified is True

    def test_verify_file_contains_false(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        f = tmp_path / "doc.txt"
        f.write_text("hello world", encoding="utf-8")
        result = fc.verify("file_contains", path=str(f), needle="missing")
        assert result.verified is False

    def test_verify_file_contains_missing_file(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("file_contains", path="missing.txt", needle="x")
        assert result.verified is False
        assert "not found" in result.error.lower() or "File not found" in result.error

    def test_verify_path_absolute_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("path_is_absolute", path=str(tmp_path / "sub"))
        assert result.verified is True

    def test_verify_path_absolute_false(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("path_is_absolute", path="relative/path")
        assert result.verified is False

    def test_verify_path_relative_exists(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        f = tmp_path / "rel.txt"
        f.write_text("x", encoding="utf-8")
        result = fc.verify("path_exists_relative", path="rel.txt")
        assert result.verified is True

    def test_verify_path_relative_not_exists(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("path_exists_relative", path="nope.txt")
        assert result.verified is False

    def test_verify_count_in_range_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("count_in_range", count=5, min_val=1, max_val=10)
        assert result.verified is True
        assert result.confidence == 1.0

    def test_verify_count_in_range_false_below(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("count_in_range", count=0, min_val=1, max_val=10)
        assert result.verified is False
        assert result.confidence == 0.0

    def test_verify_count_in_range_false_above(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("count_in_range", count=11, min_val=1, max_val=10)
        assert result.verified is False
        assert result.confidence == 0.3

    def test_verify_module_attribute_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("module_has_attribute", module_name="os.path", attr="join")
        assert result.verified is True

    def test_verify_module_attribute_false(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("module_has_attribute", module_name="os.path", attr="nonexistent_attr_xyz")
        assert result.verified is False

    def test_verify_module_attribute_bad_module(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("module_has_attribute", module_name="nonexistent_module_xyz", attr="x")
        assert result.verified is False
        assert result.error

    def test_verify_version_matches_true(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("version_matches", value="1.0.0", expected="1.0.0")
        assert result.verified is True

    def test_verify_version_matches_false(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("version_matches", value="1.0.0", expected="2.0.0")
        assert result.verified is False

    def test_verify_unknown_type(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("unknown_type", x="y")
        assert result.verified is False
        assert "Unknown fact type" in result.error

    def test_batch_verify(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        f = tmp_path / "batch.txt"
        f.write_text("content", encoding="utf-8")
        facts = [
            {"type": "file_exists", "path": str(f)},
            {"type": "count_in_range", "count": 5, "min_val": 1, "max_val": 10},
        ]
        results = fc.batch_verify(facts)
        assert len(results) == 2
        assert results[0].verified is True
        assert results[1].verified is True

    def test_verify_file_exists_empty_path(self, tmp_path):
        fc = FactChecker(project_root=tmp_path)
        result = fc.verify("file_exists", path="")
        assert result.fact_type == "file_exists"
