# [A_test] module_id: SRC-TST-2230 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_panorama_common.py — 共享投票工具单测"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "governance" / "d5_architecture" / "panorama_common.py"
)


@pytest.fixture(scope="module")
def pc():
    spec = importlib.util.spec_from_file_location("panorama_common", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestWeightedDomainVote:
    def _row(self, domain_id, path):
        return {"domain_id": domain_id, "path": path}

    def test_simple_majority(self, pc):
        rows = [
            self._row("D_GOVERNANCE", "src/gov.py"),
            self._row("D_GOVERNANCE", "src/gov2.py"),
            self._row("D_AUDITTEST", "tests/test_gov.py"),
        ]
        assert pc.weighted_domain_vote(rows) == "D_GOVERNANCE"

    def test_test_file_downweighted(self, pc):
        """测试文件降权：2 源码 vs 2 测试 → 源码域胜出"""
        rows = [
            self._row("D_GOV_SCRIPTS", "scripts/gov.py"),
            self._row("D_GOV_SCRIPTS", "scripts/gov2.py"),
            self._row("D_AUDITTEST", "tests/test_gov.py"),
            self._row("D_AUDITTEST", "tests/test_gov2.py"),
        ]
        assert pc.weighted_domain_vote(rows) == "D_GOV_SCRIPTS"

    def test_tie_alphabetical(self, pc):
        """平局时按 domain_id 字母序（确定性）"""
        rows = [
            self._row("D_GOVERNANCE", "src/a.py"),
            self._row("D_AUDITTEST", "tests/b.py"),
        ]
        # D_AUDITTEST < D_GOVERNANCE (字母序)，但测试文件降权后：
        # D_GOVERNANCE=1.0, D_AUDITTEST=0.1 → D_GOVERNANCE 胜出
        assert pc.weighted_domain_vote(rows) == "D_GOVERNANCE"

    def test_tie_same_weight_alphabetical(self, pc):
        """同权重平局时按字母序"""
        rows = [
            self._row("D_ZZZ", "src/a.py"),
            self._row("D_AAA", "src/b.py"),
        ]
        # 都是源码文件，weight=1.0，平局 → 字母序 D_AAA 胜出
        assert pc.weighted_domain_vote(rows) == "D_AAA"

    def test_empty_rows(self, pc):
        assert pc.weighted_domain_vote([]) == ""

    def test_no_domain(self, pc):
        rows = [{"domain_id": "", "path": "src/a.py"}]
        assert pc.weighted_domain_vote(rows) == ""

    def test_uses_blueprint_path_fallback(self, pc):
        """path 为空时用 blueprint_path 判断测试文件"""
        rows = [
            {"domain_id": "D_GOV", "path": None, "blueprint_path": "src/gov.py"},
            {"domain_id": "D_AUDITTEST", "path": None, "blueprint_path": "tests/t.py"},
        ]
        assert pc.weighted_domain_vote(rows) == "D_GOV"

    def test_deterministic_across_runs(self, pc):
        """相同输入多次运行结果一致"""
        rows = [
            self._row("D_GOV_SCRIPTS", "scripts/a.py"),
            self._row("D_AUDITTEST", "tests/b.py"),
        ]
        results = {pc.weighted_domain_vote(rows) for _ in range(10)}
        assert len(results) == 1


class TestMinMaturity:
    def test_design_wins(self, pc):
        assert pc.min_maturity(["production", "prototype", "design"]) == "design"

    def test_prototype_wins_over_production(self, pc):
        assert pc.min_maturity(["production", "prototype"]) == "prototype"

    def test_empty(self, pc):
        assert pc.min_maturity([]) == ""

    def test_single(self, pc):
        assert pc.min_maturity(["production"]) == "production"
