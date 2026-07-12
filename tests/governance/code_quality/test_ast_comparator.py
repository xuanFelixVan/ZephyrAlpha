# [A_test] module_id: SRC-TST-0337 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_ast_comparator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_ast_comparator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.ast_comparator import (
    ASTComparator,
    ASTCompareResult,
)


class TestASTCompareResult:
    def test_default_values(self):
        r = ASTCompareResult(similarity=0.5)
        assert r.similarity == 0.5
        assert r.hash_a == ""
        assert r.exempted is False
        assert r.partial_match_ratio == 0.0

    def test_exempted_result(self):
        r = ASTCompareResult(similarity=0.0, exempted=True, exempt_reason="Python惯用法豁免: __init__")
        assert r.exempted is True
        assert "惯用法" in r.exempt_reason


class TestASTComparator:
    def test_instantiation(self):
        comp = ASTComparator()
        assert comp is not None

    def test_compare_identical_functions(self):
        comp = ASTComparator()
        func = "def foo(x: int) -> int:\n    return x + 1\n"
        result = comp.compare(func, func)
        assert result.similarity == 1.0
        assert result.hash_a == result.hash_b

    def test_compare_different_functions(self):
        comp = ASTComparator()
        func_a = "def foo(x: int) -> int:\n    return x + 1\n"
        func_b = "def bar(y: str) -> str:\n    return y.upper()\n"
        result = comp.compare(func_a, func_b)
        assert 0.0 <= result.similarity <= 1.0
        assert result.hash_a != result.hash_b

    def test_compare_exempted_init(self):
        comp = ASTComparator()
        func_a = "def __init__(self, x):\n    self.x = x\n"
        func_b = "def __init__(self, y):\n    self.y = y\n"
        result = comp.compare(func_a, func_b, name_a="__init__", name_b="__init__")
        assert result.exempted is True

    def test_compare_exempted_repr(self):
        comp = ASTComparator()
        result = comp.compare("pass\n", "pass\n", name_a="__repr__", name_b="other")
        assert result.exempted is True

    def test_compare_no_exemption(self):
        comp = ASTComparator()
        func_a = "def process(x: int) -> int:\n    return x * 2\n"
        func_b = "def compute(y: int) -> int:\n    return y * 3\n"
        result = comp.compare(func_a, func_b, name_a="process", name_b="compute")
        assert result.exempted is False

    def test_compute_subtree_hash_deterministic(self):
        comp = ASTComparator()
        src = "def foo(x: int) -> int:\n    return x + 1\n"
        h1 = comp.compute_subtree_hash(src)
        h2 = comp.compute_subtree_hash(src)
        assert h1 == h2
        assert len(h1) == 16

    def test_compute_subtree_hash_different_sources(self):
        comp = ASTComparator()
        h1 = comp.compute_subtree_hash("def foo(x: int) -> int:\n    return x + 1\n")
        h2 = comp.compute_subtree_hash("def bar(y: str) -> str:\n    return y.upper()\n")
        assert h1 != h2

    def test_compute_subtree_hash_syntax_error(self):
        comp = ASTComparator()
        h = comp.compute_subtree_hash("def broken(:\n")
        assert isinstance(h, str)
        assert len(h) == 16

    def test_compare_bulk(self):
        comp = ASTComparator()
        pairs = [
            ("def foo():\n    return 1\n", "def foo():\n    return 1\n", "foo", "foo"),
            ("def a():\n    return 1\n", "def b():\n    return 2\n", "a", "b"),
        ]
        results = comp.compare_bulk(pairs)
        assert len(results) == 2
        assert results[0].similarity == 1.0

    def test_compare_bulk_empty(self):
        comp = ASTComparator()
        results = comp.compare_bulk([])
        assert results == []

    def test_cluster_templates(self):
        comp = ASTComparator()
        functions = [
            ("parse_json", "def parse_json():\n    pass\n"),
            ("parse_xml", "def parse_xml():\n    pass\n"),
            ("validate_input", "def validate_input():\n    pass\n"),
            ("validate_output", "def validate_output():\n    pass\n"),
            ("standalone", "def standalone():\n    pass\n"),
        ]
        clusters = comp.cluster_templates(functions)
        assert "pattern_parse" in clusters
        assert "pattern_validate" in clusters
        assert len(clusters["pattern_parse"]) == 2
        assert len(clusters["pattern_validate"]) == 2

    def test_cluster_templates_no_prefix_groups(self):
        comp = ASTComparator()
        functions = [("alpha", "pass\n"), ("beta", "pass\n"), ("gamma", "pass\n")]
        clusters = comp.cluster_templates(functions)
        assert len(clusters) == 0

    def test_lcs_ratio_identical(self):
        comp = ASTComparator()
        src = "def foo():\n    x = 1\n    return x\n"
        result = comp.compare(src, src, name_a="foo", name_b="foo2")
        assert result.similarity == 1.0
        assert result.partial_match_ratio == 0.0

    def test_compare_empty_sources(self):
        comp = ASTComparator()
        result = comp.compare("", "", name_a="a", name_b="b")
        assert isinstance(result, ASTCompareResult)
