# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.5
# [MODULE] tests.clone_guard.test_aggregator
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_aggregator.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""FindingAggregator 单元测试——覆盖去重/多数表决/严重性就高/降级/少数派过滤。"""

from pathlib import Path

import pytest

from zephyr.clone_guard.aggregator import (
    AggregatedFinding,
    AggregationResult,
    FindingAggregator,
)
from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

# ---------------------------------------------------------------------------
# 辅助工厂
# ---------------------------------------------------------------------------


def _make_finding(
    *,
    severity: str = "extract",
    clone_type: str = "T2",
    similarity: float = 0.9,
    source_file: str = "src/new.py",
    source_function: str = "calc",
    source_lineno: int = 10,
    existing_file: str = "src/old.py",
    existing_function: str = "compute",
    existing_lineno: int = 20,
    import_suggestion: str | None = "from src.old import compute",
    finding_id: str = "F-001",
) -> Finding:
    return Finding(
        finding_id=finding_id,
        severity=severity,
        clone_type=clone_type,
        similarity=similarity,
        source_file=source_file,
        source_function=source_function,
        source_lineno=source_lineno,
        existing_file=existing_file,
        existing_function=existing_function,
        existing_lineno=existing_lineno,
        import_suggestion=import_suggestion,
    )


# ---------------------------------------------------------------------------
# 边界条件测试
# ---------------------------------------------------------------------------


class TestEmptyAndDegraded:
    """空输入和全降级边界条件。"""

    def test_empty_engine_results(self):
        """空 engine_results 返回空 AggregationResult。"""
        aggregator = FindingAggregator()
        result = aggregator.aggregate({})
        assert result.findings == []
        assert result.degraded_engines == []
        assert result.active_engine_count == 0
        assert result.total_raw_findings == 0

    def test_all_degraded_returns_empty(self):
        """全部引擎降级 → 返回空 findings + degraded_engines 列表。"""
        f = _make_finding()
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f], True),
                "redup": ([f], True),
            }
        )
        assert result.findings == []
        assert set(result.degraded_engines) == {"echo_guard", "redup"}
        assert result.active_engine_count == 0
        assert result.total_raw_findings == 2  # 降级引擎的 findings 仍计入 raw

    def test_single_engine_no_findings(self):
        """单引擎无 findings → 空结果。"""
        aggregator = FindingAggregator()
        result = aggregator.aggregate({"echo_guard": ([], False)})
        assert result.findings == []
        assert result.active_engine_count == 1


# ---------------------------------------------------------------------------
# 共识判定测试
# ---------------------------------------------------------------------------


class TestConsensus:
    """多数表决共识判定。"""

    def test_single_engine_unanimous(self):
        """单引擎报告 → consensus="unanimous"（1/1 = 100%）。"""
        f = _make_finding()
        aggregator = FindingAggregator()
        result = aggregator.aggregate({"echo_guard": ([f], False)})
        assert len(result.findings) == 1
        assert result.findings[0].consensus == "unanimous"
        assert result.findings[0].vote_count == 1
        assert result.findings[0].active_engine_count == 1

    def test_two_engines_same_finding_unanimous(self):
        """两引擎报告同一克隆对 → consensus="unanimous"（2/2 = 100%）。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")  # 同一克隆对，不同 finding_id
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert len(result.findings) == 1  # 去重后 1 个
        assert result.findings[0].consensus == "unanimous"
        assert result.findings[0].vote_count == 2

    def test_two_engines_different_findings_single(self):
        """两引擎报告不同克隆对 → 各自 consensus="single"（1/2 < ceil(2/2)=1... 实际 1>=1 → majority）。"""
        f1 = _make_finding(source_function="func_a", finding_id="F-1")
        f2 = _make_finding(source_function="func_b", existing_function="other", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        # 2 引擎活跃，每个 finding 各 1 票，threshold = ceil(2/2) = 1
        # 1 >= 1 → "majority"（不是 "single"）
        assert len(result.findings) == 2
        for af in result.findings:
            assert af.consensus == "majority"
            assert af.vote_count == 1

    def test_three_engines_two_report_same_majority(self):
        """三引擎中两个报告同一克隆对 → consensus="majority"（2/3 >= ceil(3/2)=2）。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")  # 同一克隆对
        f3 = _make_finding(source_function="other_func", finding_id="F-3")  # 不同克隆对
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
                "ast_grep": ([f3], False),
            }
        )
        # f1+f2 合并 → 2/3 票 → "majority"
        # f3 → 1/3 票 → "single"（1 < 2）
        by_func = {af.source_function: af for af in result.findings}
        assert by_func["calc"].consensus == "majority"
        assert by_func["calc"].vote_count == 2
        assert by_func["other_func"].consensus == "single"
        assert by_func["other_func"].vote_count == 1

    def test_three_engines_all_report_same_unanimous(self):
        """三引擎全报告同一克隆对 → consensus="unanimous"（3/3 = 100%）。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")
        f3 = _make_finding(finding_id="F-3")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
                "ast_grep": ([f3], False),
            }
        )
        assert len(result.findings) == 1
        assert result.findings[0].consensus == "unanimous"
        assert result.findings[0].vote_count == 3


# ---------------------------------------------------------------------------
# 严重性就高测试
# ---------------------------------------------------------------------------


class TestSeverityTakesHighest:
    """严重性就高原则——extract > review > acknowledged。"""

    def test_review_and_extract_yields_extract(self):
        """引擎 A 说 review, 引擎 B 说 extract → 最终 extract。"""
        f1 = _make_finding(severity="review", finding_id="F-1")
        f2 = _make_finding(severity="extract", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert len(result.findings) == 1
        assert result.findings[0].severity == "extract"
        assert result.findings[0].engine_severities == {"echo_guard": "review", "redup": "extract"}

    def test_acknowledged_and_review_yields_review(self):
        """引擎 A 说 acknowledged, 引擎 B 说 review → 最终 review。"""
        f1 = _make_finding(severity="acknowledged", finding_id="F-1")
        f2 = _make_finding(severity="review", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert result.findings[0].severity == "review"

    def test_all_extract_yields_extract(self):
        """两引擎都说 extract → 最终 extract。"""
        f1 = _make_finding(severity="extract", finding_id="F-1")
        f2 = _make_finding(severity="extract", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert result.findings[0].severity == "extract"


# ---------------------------------------------------------------------------
# 相似度取最大测试
# ---------------------------------------------------------------------------


class TestSimilarityTakesMax:
    """相似度取最大值（最悲观估计）。"""

    def test_max_similarity_selected(self):
        """引擎 A 说 0.8, 引擎 B 说 0.95 → 最终 0.95。"""
        f1 = _make_finding(similarity=0.8, finding_id="F-1")
        f2 = _make_finding(similarity=0.95, finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert result.findings[0].similarity == pytest.approx(0.95)
        assert result.findings[0].engine_similarities == {"echo_guard": 0.8, "redup": 0.95}

    def test_three_engines_max_similarity(self):
        """三引擎相似度 0.7 / 0.9 / 0.85 → 最终 0.9。"""
        f1 = _make_finding(similarity=0.7, finding_id="F-1")
        f2 = _make_finding(similarity=0.9, finding_id="F-2")
        f3 = _make_finding(similarity=0.85, finding_id="F-3")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
                "ast_grep": ([f3], False),
            }
        )
        assert result.findings[0].similarity == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# 降级引擎排除测试
# ---------------------------------------------------------------------------


class TestDegradedExclusion:
    """降级引擎完全排除出表决。"""

    def test_degraded_engine_findings_excluded(self):
        """降级引擎的 findings 不出现在结果中。"""
        f1 = _make_finding(source_function="func_a", finding_id="F-1")
        f2 = _make_finding(source_function="func_b", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], True),  # degraded
            }
        )
        # 只有 echo_guard 的 f1 出现
        assert len(result.findings) == 1
        assert result.findings[0].source_function == "func_a"
        assert result.active_engine_count == 1
        assert result.degraded_engines == ["redup"]

    def test_degraded_engine_not_in_active_count(self):
        """降级引擎不计入 active_count。"""
        f = _make_finding()
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f], False),
                "redup": ([], True),  # degraded
            }
        )
        assert result.active_engine_count == 1
        assert result.findings[0].active_engine_count == 1
        assert result.findings[0].consensus == "unanimous"  # 1/1 = 100%


# ---------------------------------------------------------------------------
# 去重键归一化测试
# ---------------------------------------------------------------------------


class TestDedupNormalization:
    r"""去重键路径归一化——\ 和 / 视为相同。"""

    def test_backslash_and_forward_slash_treated_same(self):
        r"""Windows 路径 (\) 和 Unix 路径 (/) 视为同一克隆对。"""
        f1 = _make_finding(source_file="src\\new.py", finding_id="F-1")
        f2 = _make_finding(source_file="src/new.py", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert len(result.findings) == 1  # 去重合并

    def test_different_existing_function_not_deduplicated(self):
        """existing_function 不同 → 不去重（不同的克隆对）。"""
        f1 = _make_finding(existing_function="compute", finding_id="F-1")
        f2 = _make_finding(existing_function="calculate", finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert len(result.findings) == 2

    def test_ast_grep_rule_finding_not_deduplicated_with_clone(self):
        """ast-grep 的 existing_file 是规则文件，不与克隆对去重。"""
        f1 = _make_finding(
            existing_file="src/old.py",
            existing_function="compute",
            finding_id="F-1",
        )
        f2 = _make_finding(
            existing_file="clone_guard/rules/no-duplicate-try-except.yml",
            existing_function="rule:no-duplicate-try-except",
            finding_id="F-2",
        )
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "ast_grep": ([f2], False),
            }
        )
        assert len(result.findings) == 2  # 不去重


# ---------------------------------------------------------------------------
# filter_minority 配置测试
# ---------------------------------------------------------------------------


class TestFilterMinority:
    """filter_minority 配置——过滤少数派 findings。"""

    def test_filter_minority_true_removes_single(self):
        """filter_minority=True → consensus="single" 的 findings 被过滤。"""
        f1 = _make_finding(source_function="func_a", finding_id="F-1")
        f2 = _make_finding(source_function="func_b", finding_id="F-2")
        f3 = _make_finding(source_function="func_a", finding_id="F-3")  # 与 f1 同克隆对
        cfg = CloneGuardConfig(filter_minority=True)
        aggregator = FindingAggregator(cfg)
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1, f2], False),
                "redup": ([f3], False),
                "ast_grep": ([], False),
            }
        )
        # f1+f3 合并 → 2/3 票 → "majority" → 保留
        # f2 → 1/3 票 → "single" → 过滤
        assert len(result.findings) == 1
        assert result.findings[0].source_function == "func_a"

    def test_filter_minority_false_keeps_single(self):
        """filter_minority=False（默认）→ 保留 "single" findings。"""
        f1 = _make_finding(source_function="func_a", finding_id="F-1")
        f2 = _make_finding(source_function="func_b", finding_id="F-2")
        f3 = _make_finding(source_function="func_a", finding_id="F-3")
        aggregator = FindingAggregator()  # 默认 filter_minority=False
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1, f2], False),
                "redup": ([f3], False),
                "ast_grep": ([], False),
            }
        )
        assert len(result.findings) == 2  # 都保留

    def test_filter_minority_with_single_engine(self):
        """单引擎 + filter_minority=True → 全部保留（1/1 = unanimous，不是 single）。"""
        f = _make_finding()
        cfg = CloneGuardConfig(filter_minority=True)
        aggregator = FindingAggregator(cfg)
        result = aggregator.aggregate({"echo_guard": ([f], False)})
        assert len(result.findings) == 1
        assert result.findings[0].consensus == "unanimous"


# ---------------------------------------------------------------------------
# 计数和元数据测试
# ---------------------------------------------------------------------------


class TestCountsAndMetadata:
    """total_raw_findings / deduplicated_count / engines 元数据。"""

    def test_total_raw_findings_counts_all(self):
        """total_raw_findings 包括降级引擎的 findings。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")
        f3 = _make_finding(source_function="other", finding_id="F-3")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1, f3], False),
                "redup": ([f2], False),
            }
        )
        # raw: 3 findings (f1 + f3 from echo_guard, f2 from redup)
        assert result.total_raw_findings == 3
        # dedup: f1+f2 合并 → 1, f3 → 1, total 2
        assert result.deduplicated_count == 2

    def test_engines_list_in_aggregated_finding(self):
        """AggregatedFinding.engines 包含所有报告该克隆对的引擎。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([f1], False),
                "redup": ([f2], False),
            }
        )
        assert set(result.findings[0].engines) == {"echo_guard", "redup"}

    def test_finding_id_is_stable(self):
        """同一克隆对多次聚合生成相同 finding_id（基于 hash）。"""
        f1 = _make_finding(finding_id="F-1")
        f2 = _make_finding(finding_id="F-2")
        aggregator = FindingAggregator()
        result1 = aggregator.aggregate({"echo_guard": ([f1], False)})
        result2 = aggregator.aggregate({"redup": ([f2], False)})
        assert result1.findings[0].finding_id == result2.findings[0].finding_id
        assert result1.findings[0].finding_id.startswith("AGG-")

    def test_import_suggestion_preserved(self):
        """import_suggestion 从原始 finding 保留。"""
        f = _make_finding(import_suggestion="from src.old import compute")
        aggregator = FindingAggregator()
        result = aggregator.aggregate({"echo_guard": ([f], False)})
        assert result.findings[0].import_suggestion == "from src.old import compute"


# ---------------------------------------------------------------------------
# 多 finding 混合场景测试
# ---------------------------------------------------------------------------


class TestMixedScenario:
    """多引擎多 finding 混合场景——模拟真实使用。"""

    def test_real_world_scenario(self):
        """模拟真实场景：3 引擎，部分降级，部分克隆对重叠。"""
        # echo_guard 报告 2 个克隆
        eg_f1 = _make_finding(
            source_function="calc_tax",
            existing_function="compute_tax",
            severity="extract",
            similarity=0.92,
            finding_id="EG-1",
        )
        eg_f2 = _make_finding(
            source_function="format_report",
            existing_function="render_report",
            severity="review",
            similarity=0.75,
            finding_id="EG-2",
        )
        # redup 也报告 calc_tax 克隆（但判 review），并发现新克隆
        rd_f1 = _make_finding(
            source_function="calc_tax",
            existing_function="compute_tax",
            severity="review",
            similarity=0.88,
            finding_id="RD-1",
        )
        rd_f3 = _make_finding(
            source_function="validate_input",
            existing_function="check_input",
            severity="extract",
            similarity=0.95,
            finding_id="RD-3",
        )
        # ast_grep 降级
        aggregator = FindingAggregator()
        result = aggregator.aggregate(
            {
                "echo_guard": ([eg_f1, eg_f2], False),
                "redup": ([rd_f1, rd_f3], False),
                "ast_grep": ([], True),  # degraded
            }
        )

        # 验证
        assert result.active_engine_count == 2
        assert result.degraded_engines == ["ast_grep"]
        assert result.total_raw_findings == 4
        assert result.deduplicated_count == 3  # calc_tax 合并, format_report, validate_input

        by_func = {af.source_function: af for af in result.findings}

        # calc_tax: 2/2 → unanimous, severity=extract（就高）, similarity=0.92（max）
        assert by_func["calc_tax"].consensus == "unanimous"
        assert by_func["calc_tax"].severity == "extract"
        assert by_func["calc_tax"].similarity == pytest.approx(0.92)
        assert by_func["calc_tax"].vote_count == 2

        # format_report: 1/2 → majority（threshold=ceil(2/2)=1, 1>=1）
        assert by_func["format_report"].consensus == "majority"
        assert by_func["format_report"].severity == "review"
        assert by_func["format_report"].vote_count == 1

        # validate_input: 1/2 → majority
        assert by_func["validate_input"].consensus == "majority"
        assert by_func["validate_input"].severity == "extract"
