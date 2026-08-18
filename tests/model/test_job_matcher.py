# [A_test] module_id: MOD-GOV_job_matcher | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_job_matcher
# [INVARIANTS] test_job_matcher完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.intelligence.model_profiling.capability_passport import (
    GRADE_LEVEL,
    CostBreakdown,
    HallucinationBreakdown,
    JobRecommendation,
    QuickProfile,
    compute_grade_simple,
)
from zephyr.intelligence.model_profiling.job_matcher import (
    JobMatcher,
    JobMatcherError,
    grades_from_scores,
    match_jobs,
)

# ── 测试 fixtures ──────────────────────────────────────────

_MINIMAL_MATRIX = """\
version: "1.0.0"
hallucination_dimensions:
  fabrication: {weight: 0.20}
  inconsistency: {weight: 0.15}
  refusal: {weight: 0.08}
  overclaim: {weight: 0.12}
  context_drift: {weight: 0.12}
  source_confusion: {weight: 0.12}
  instruction_drift: {weight: 0.10}
  format_hallucination: {weight: 0.06}
  quantity_hallucination: {weight: 0.05}
jobs:
  junior_code_worker:
    title: "初级代码工"
    description: "修简单 bug"
    required:
      code_edit_precision: "C"
      refactor: "D"
    bonus:
      dead_code_removal: "C"
      code_generate: "D"
    max_hallucination: 0.40
    category: "entry"
  rule_gatekeeper:
    title: "规则守门员"
    description: "低幻觉要求"
    required:
      rule_comprehension: "C"
      hallucination_detect: "B"
    bonus:
      anomaly_triage: "C"
    max_hallucination: 0.15
    category: "senior"
"""


@pytest.fixture
def matrix_path(tmp_path: Path) -> Path:
    """临时 yaml 矩阵 (隔离测试, 不依赖生产 data/brain/job_matrix.yaml)。"""
    p = tmp_path / "job_matrix.yaml"
    p.write_text(_MINIMAL_MATRIX, encoding="utf-8")
    return p


@pytest.fixture
def matcher(matrix_path: Path) -> JobMatcher:
    return JobMatcher(matrix_path=matrix_path)


def _make_profile(
    grades: dict[str, str] | None = None,
    *,
    fab: float = 0.0,
    inc: float = 0.0,
    ref: float = 0.0,
    ovc: float = 0.0,
    cd: float = 0.0,
    sc: float = 0.0,
    idr: float = 0.0,
    fmh: float = 0.0,
    qh: float = 0.0,
    model_id: str = "test-model",
    cost: CostBreakdown | None = None,
) -> QuickProfile:
    """构造 QuickProfile (默认零幻觉, 本地模型成本≈0)。

    九维幻觉参数 (fab/idr/fmh/qh 等) 默认 0.0；
    调用方需显式设置全部 9 维才能保证 overall_rate 等于单一设定值。
    cost 默认 None → CostBreakdown() (local, cost_score=1.0)。
    """
    return QuickProfile(
        model_id=model_id,
        capability_grades=grades or {},
        hallucination=HallucinationBreakdown(
            fabrication=fab,
            inconsistency=inc,
            refusal=ref,
            overclaim=ovc,
            context_drift=cd,
            source_confusion=sc,
            instruction_drift=idr,
            format_hallucination=fmh,
            quantity_hallucination=qh,
        ),
        cost=cost or CostBreakdown(),
    )


# ── 1. 矩阵加载 ────────────────────────────────────────────

class TestLoadMatrix:
    def test_load_default_matrix(self):
        """默认路径加载生产 job_matrix.yaml (6 岗位)。"""
        m = JobMatcher()
        assert m.job_count >= 6
        assert "junior_code_worker" in m.job_ids

    def test_load_custom_matrix(self, matrix_path: Path):
        m = JobMatcher(matrix_path=matrix_path)
        assert m.job_count == 2
        assert set(m.job_ids) == {"junior_code_worker", "rule_gatekeeper"}

    def test_file_not_found_raises(self, tmp_path: Path):
        bad = tmp_path / "nonexistent.yaml"
        with pytest.raises(JobMatcherError, match="not found"):
            JobMatcher(matrix_path=bad)

    def test_yaml_parse_error_raises(self, tmp_path: Path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: [unterminated\n  - a: b", encoding="utf-8")
        with pytest.raises(JobMatcherError, match="yaml parse error"):
            JobMatcher(matrix_path=bad)

    def test_empty_jobs(self, tmp_path: Path):
        p = tmp_path / "empty.yaml"
        p.write_text("version: '1.0'\njobs: {}\n", encoding="utf-8")
        m = JobMatcher(matrix_path=p)
        assert m.job_count == 0
        assert m.match(_make_profile()) == []

    def test_hallu_dims_loaded(self, matcher: JobMatcher):
        assert "fabrication" in matcher.hallu_dims
        assert matcher.hallu_dims["fabrication"] == pytest.approx(0.20)
        assert len(matcher.hallu_dims) == 9

    def test_tool_axis_capabilities_in_matrix(self):
        """Tool 轴 (ROADMAP-02): function_calling/tool_chaining 出现在岗位 bonus 中。"""
        m = JobMatcher()
        # refactor_specialist 应有 function_calling + tool_chaining bonus
        refactor = m.jobs.get("refactor_specialist", {})
        bonus = refactor.get("bonus", {})
        assert "function_calling" in bonus
        assert "tool_chaining" in bonus
        # code_generator 应有 function_calling bonus
        gen = m.jobs.get("code_generator", {})
        assert "function_calling" in gen.get("bonus", {})
        # architecture_reviewer 应有 tool_chaining bonus
        arch = m.jobs.get("architecture_reviewer", {})
        assert "tool_chaining" in arch.get("bonus", {})
        # rule_gatekeeper 必须有 max_cost (Cost 轴修复)
        assert "max_cost" in m.jobs.get("rule_gatekeeper", {})


# ── 2. _check_required ────────────────────────────────────

class TestCheckRequired:
    def test_all_satisfied(self, matcher: JobMatcher):
        grades = {"code_edit_precision": "B", "refactor": "C"}
        ok, missing = matcher.check_required(
            grades, {"code_edit_precision": "C", "refactor": "D"}
        )
        assert ok is True
        assert missing == []

    def test_partial_fail(self, matcher: JobMatcher):
        grades = {"code_edit_precision": "B", "refactor": "F"}
        ok, missing = matcher.check_required(
            grades, {"code_edit_precision": "C", "refactor": "D"}
        )
        assert ok is False
        assert len(missing) == 1
        assert "refactor" in missing[0]

    def test_missing_capability_defaults_F(self, matcher: JobMatcher):
        """能力缺失 → 默认 F 级, 不满足 C 要求。"""
        grades = {"code_edit_precision": "B"}  # refactor 缺失
        ok, missing = matcher.check_required(
            grades, {"code_edit_precision": "C", "refactor": "D"}
        )
        assert ok is False
        assert any("refactor" in m for m in missing)

    def test_empty_required(self, matcher: JobMatcher):
        ok, missing = matcher.check_required({}, {})
        assert ok is True
        assert missing == []

    def test_exact_grade_satisfies(self, matcher: JobMatcher):
        """刚好达到 required 级别 = 满足 (>=)。"""
        ok, _ = matcher.check_required({"cap": "C"}, {"cap": "C"})
        assert ok is True


# ── 3. _compute_bonus ─────────────────────────────────────

class TestComputeBonus:
    def test_all_hit(self, matcher: JobMatcher):
        grades = {"dead_code_removal": "B", "code_generate": "C"}
        ratio, summary = matcher.compute_bonus(
            grades, {"dead_code_removal": "C", "code_generate": "D"}
        )
        assert ratio == 1.0
        assert "dead_code_removal" in summary
        assert "code_generate" in summary

    def test_partial_hit(self, matcher: JobMatcher):
        grades = {"dead_code_removal": "B", "code_generate": "F"}
        ratio, summary = matcher.compute_bonus(
            grades, {"dead_code_removal": "C", "code_generate": "D"}
        )
        assert ratio == 0.5
        assert "dead_code_removal" in summary
        assert "code_generate" not in summary

    def test_empty_bonus(self, matcher: JobMatcher):
        ratio, summary = matcher.compute_bonus({"cap": "A"}, {})
        assert ratio == 0.0
        assert summary == ""

    def test_none_hit(self, matcher: JobMatcher):
        grades = {"dead_code_removal": "F", "code_generate": "F"}
        ratio, summary = matcher.compute_bonus(
            grades, {"dead_code_removal": "C", "code_generate": "D"}
        )
        assert ratio == 0.0
        assert summary == "none"


# ── 4. _compute_hallucination_score ───────────────────────
# 幻觉率正常评分 (非硬门): rate<=max → 0.7~1.0; rate>max → 0.7~0.0

class TestComputeHallucinationScore:
    def test_zero_hallucination_full_score(self, matcher: JobMatcher):
        """零幻觉 → 满分 1.0。"""
        hallu = HallucinationBreakdown()  # 全 0
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.4)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_within_expectation(self, matcher: JobMatcher):
        """rate=0.2, max=0.4 → 0.7 + 0.3*(1-0.5) = 0.85。"""
        hallu = HallucinationBreakdown(
            fabrication=0.2, inconsistency=0.2, refusal=0.2,
            overclaim=0.2, context_drift=0.2, source_confusion=0.2,
            instruction_drift=0.2, format_hallucination=0.2, quantity_hallucination=0.2,
        )
        assert hallu.overall_rate == pytest.approx(0.2, abs=0.01)
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.4)
        # 0.7 + 0.3 * (1 - 0.2/0.4) = 0.7 + 0.15 = 0.85
        assert score == pytest.approx(0.85, abs=0.02)

    def test_at_threshold(self, matcher: JobMatcher):
        """rate=max → 0.7 (刚好满足期望下限)。"""
        hallu = HallucinationBreakdown(
            fabrication=0.4, inconsistency=0.4, refusal=0.4,
            overclaim=0.4, context_drift=0.4, source_confusion=0.4,
            instruction_drift=0.4, format_hallucination=0.4, quantity_hallucination=0.4,
        )
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.4)
        assert score == pytest.approx(0.7, abs=0.02)

    def test_exceed_expectation_decay(self, matcher: JobMatcher):
        """rate=0.6, max=0.4 → 超出 50%, score=0.7-0.7*0.5=0.35。"""
        hallu = HallucinationBreakdown(
            fabrication=0.6, inconsistency=0.6, refusal=0.6,
            overclaim=0.6, context_drift=0.6, source_confusion=0.6,
            instruction_drift=0.6, format_hallucination=0.6, quantity_hallucination=0.6,
        )
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.4)
        # excess = (0.6-0.4)/0.4 = 0.5; score = 0.7 - 0.7*0.5 = 0.35
        assert score == pytest.approx(0.35, abs=0.02)

    def test_double_exceed_zero(self, matcher: JobMatcher):
        """rate=2*max → 超出 100%, score=0.0 (但不一票否决, 仍参与排序)。"""
        hallu = HallucinationBreakdown(
            fabrication=0.8, inconsistency=0.8, refusal=0.8,
            overclaim=0.8, context_drift=0.8, source_confusion=0.8,
            instruction_drift=0.8, format_hallucination=0.8, quantity_hallucination=0.8,
        )
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.4)
        assert score == 0.0

    def test_max_hallu_zero_uses_absolute(self, matcher: JobMatcher):
        """max_hallu=0 (岗位要求零幻觉) → 用绝对分 1-rate。"""
        hallu = HallucinationBreakdown(
            fabrication=0.3, inconsistency=0.3, refusal=0.3,
            overclaim=0.3, context_drift=0.3, source_confusion=0.3,
            instruction_drift=0.3, format_hallucination=0.3, quantity_hallucination=0.3,
        )
        score = matcher.compute_hallucination_score(hallu, max_hallu=0.0)
        assert score == pytest.approx(0.7, abs=0.01)


# ── 5. match / match_top ──────────────────────────────────

class TestMatch:
    def test_match_returns_all_jobs_sorted(self, matcher: JobMatcher):
        """match 返回全部岗位, 按 match_score 降序。"""
        profile = _make_profile(
            {"code_edit_precision": "B", "refactor": "C",
             "rule_comprehension": "F", "hallucination_detect": "F"},
            fab=0.1,
        )
        recs = matcher.match(profile)
        assert len(recs) == 2
        # 降序
        assert recs[0].match_score >= recs[1].match_score
        # 初级代码工 qualified, 规则守门员不 qualified
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        gate = next(r for r in recs if r.job_id == "rule_gatekeeper")
        assert junior.qualified is True
        assert gate.qualified is False

    def test_match_top_n(self, matcher: JobMatcher):
        profile = _make_profile({"code_edit_precision": "A"})
        recs = matcher.match_top(profile, n=1)
        assert len(recs) == 1

    def test_match_top_n_exceeds_count(self, matcher: JobMatcher):
        """n > 岗位数 → 返回全部。"""
        profile = _make_profile({})
        recs = matcher.match_top(profile, n=10)
        assert len(recs) == 2

    def test_qualified_scores_higher(self, matcher: JobMatcher):
        """qualified 岗位有 0.5 基础分, 通常高于不 qualified。"""
        profile = _make_profile(
            {"code_edit_precision": "A", "refactor": "A",  # 初级 qualified
             "rule_comprehension": "F", "hallucination_detect": "F"},  # 守门员不
        )
        recs = matcher.match(profile)
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        gate = next(r for r in recs if r.job_id == "rule_gatekeeper")
        assert junior.match_score > gate.match_score

    def test_recommendation_fields_populated(self, matcher: JobMatcher):
        profile = _make_profile({"code_edit_precision": "B", "refactor": "C"})
        recs = matcher.match(profile)
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        assert junior.job_title == "初级代码工"
        assert junior.qualified is True
        assert junior.missing_required == []
        assert isinstance(junior.bonus_summary, str)
        assert "修简单 bug" in junior.description

    def test_hallucination_passed_flag(self, matcher: JobMatcher):
        """hallucination_passed 是参考值 (非硬门), rate<=max → True。"""
        # 低幻觉
        low = _make_profile(
            {"code_edit_precision": "B", "refactor": "C"}, fab=0.05
        )
        recs_low = matcher.match(low)
        junior_low = next(r for r in recs_low if r.job_id == "junior_code_worker")
        assert junior_low.hallucination_passed is True

        # 高幻觉 (九维都高, overall_rate=0.9 > max=0.4, 仍参与匹配不淘汰)
        high = _make_profile(
            {"code_edit_precision": "B", "refactor": "C"},
            fab=0.9, inc=0.9, ref=0.9, ovc=0.9, cd=0.9, sc=0.9,
            idr=0.9, fmh=0.9, qh=0.9,
        )
        recs_high = matcher.match(high)
        junior_high = next(r for r in recs_high if r.job_id == "junior_code_worker")
        assert junior_high.hallucination_passed is False
        # 关键: 不 qualified 仍计算分数 (非一票否决)
        assert junior_high.match_score < junior_low.match_score
        assert junior_high.match_score >= 0.0


# ── 6. 端到端: 合成画像场景 ───────────────────────────────

class TestEndToEndScenarios:
    def test_strong_code_low_hallu_matches_junior(self, matcher: JobMatcher):
        """场景1: 代码强 + 幻觉低 → 初级代码工高分。"""
        profile = _make_profile(
            {"code_edit_precision": "A", "refactor": "B",
             "dead_code_removal": "B", "code_generate": "B"},
            fab=0.05, inc=0.05,
        )
        recs = matcher.match_top(profile, n=2)
        assert recs[0].job_id == "junior_code_worker"
        assert recs[0].qualified is True
        assert recs[0].match_score >= 0.8

    def test_high_hallu_still_gets_score(self, matcher: JobMatcher):
        """场景2: 高幻觉模型仍获得分数 (非一票否决)。"""
        profile = _make_profile(
            {"code_edit_precision": "A", "refactor": "B"},
            fab=0.5, inc=0.5, ref=0.5, ovc=0.5, cd=0.5, sc=0.5,
        )
        recs = matcher.match(profile)
        # 全部岗位仍有分数 (>= 0)
        assert all(r.match_score >= 0.0 for r in recs)
        # qualified 岗位分数仍 > 0 (有 0.5 基础分, 即使 hallu_score=0)
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        assert junior.qualified is True
        assert junior.match_score > 0.0

    def test_weak_model_low_hallu(self, matcher: JobMatcher):
        """场景3: 弱模型 + 低幻觉 → qualified=False 但 hallucination_passed=True。"""
        profile = _make_profile(
            {"code_edit_precision": "F", "refactor": "F"},
            fab=0.02,
        )
        recs = matcher.match(profile)
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        assert junior.qualified is False
        assert junior.hallucination_passed is True
        assert len(junior.missing_required) == 2


# ── 7. 便捷函数 ───────────────────────────────────────────

class TestConvenienceFunctions:
    def test_match_jobs_helper(self, matrix_path: Path):
        profile = _make_profile({"code_edit_precision": "B", "refactor": "C"})
        recs = match_jobs(profile, n=2, matrix_path=matrix_path)
        assert len(recs) <= 2
        assert all(isinstance(r, JobRecommendation) for r in recs)

    def test_grades_from_scores(self):
        scores = {"cap_a": 0.80, "cap_b": 0.50, "cap_c": 0.10}
        grades = grades_from_scores(scores)
        assert grades["cap_a"] == "A"
        assert grades["cap_b"] == "C"
        assert grades["cap_c"] == "F"


# ── 8. 边界情况 ───────────────────────────────────────────

class TestEdgeCases:
    def test_empty_grades(self, matcher: JobMatcher):
        """空 grades → 全部不 qualified, 但仍返回推荐。"""
        profile = _make_profile({})
        recs = matcher.match(profile)
        assert len(recs) == 2
        assert all(r.qualified is False for r in recs)

    def test_clamp_score_to_1(self, matcher: JobMatcher):
        """match_score 不超过 1.0。"""
        profile = _make_profile(
            {"code_edit_precision": "A", "refactor": "A",
             "dead_code_removal": "A", "code_generate": "A"},
        )
        recs = matcher.match(profile)
        assert all(r.match_score <= 1.0 for r in recs)

    def test_grade_level_mapping(self):
        """GRADE_LEVEL 映射正确 (A>B>C>D>F)。"""
        assert GRADE_LEVEL["A"] > GRADE_LEVEL["B"]
        assert GRADE_LEVEL["B"] > GRADE_LEVEL["C"]
        assert GRADE_LEVEL["C"] > GRADE_LEVEL["D"]
        assert GRADE_LEVEL["D"] > GRADE_LEVEL["F"]

    def test_compute_grade_simple_thresholds(self):
        """compute_grade_simple 五级阈值正确。"""
        assert compute_grade_simple(0.75) == "A"
        assert compute_grade_simple(0.749) == "B"
        assert compute_grade_simple(0.60) == "B"
        assert compute_grade_simple(0.599) == "C"
        assert compute_grade_simple(0.45) == "C"
        assert compute_grade_simple(0.449) == "D"
        assert compute_grade_simple(0.30) == "D"
        assert compute_grade_simple(0.299) == "F"
        assert compute_grade_simple(0.0) == "F"


# ── 9. Cost 轴: CostBreakdown (D-MCE-07) ──────────────────

class TestCostBreakdown:
    """CostBreakdown.cost_score property 测试。"""

    def test_local_cost_score_is_1(self):
        """本地模型成本≈0, cost_score=1.0。"""
        c = CostBreakdown(deployment_mode="local")
        assert c.cost_score == 1.0

    def test_api_free_cost_score_is_1(self):
        """API 模型 cost<=0.01 → cost_score=1.0 (近似免费, 如 zhipu)。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.005)
        assert c.cost_score == 1.0

    def test_api_zero_cost_score_is_1(self):
        """API 模型 cost=0 → cost_score=1.0。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.0)
        assert c.cost_score == 1.0

    def test_api_expensive_cost_score_is_0(self):
        """API 模型 cost>=1.0 → cost_score=0.0 (昂贵)。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=2.0)
        assert c.cost_score == 0.0

    def test_api_at_expensive_threshold(self):
        """API 模型 cost=1.0 (刚好昂贵阈值) → cost_score=0.0。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=1.0)
        assert c.cost_score == 0.0

    def test_api_mid_cost_linear(self):
        """API 模型 0.01<cost<1.0 → 线性衰减。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.5)
        # 1.0 - (0.5-0.01)/0.99 = 1.0 - 0.495 = 0.505
        assert c.cost_score == pytest.approx(0.505, abs=0.01)


# ── 10. Cost 轴: _compute_cost_score (D-MCE-07) ───────────
# 成本是维度非硬门: claude 贵但必要时仍可用

class TestComputeCostScore:
    """JobMatcher.compute_cost_score 测试。"""

    def test_local_model_full_score(self, matcher: JobMatcher):
        """本地模型 → cost_score=1.0 (成本≈0)。"""
        c = CostBreakdown(deployment_mode="local")
        score = matcher.compute_cost_score(c, max_cost=0.05)
        assert score == 1.0

    def test_api_within_budget(self, matcher: JobMatcher):
        """API cost<=max_cost → 0.7~1.0 线性 (越便宜越好)。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.01)
        # cost=0.01, max=0.05 → 0.7+0.3*(1-0.01/0.05)=0.7+0.3*0.8=0.94
        score = matcher.compute_cost_score(c, max_cost=0.05)
        assert score == pytest.approx(0.94, abs=0.02)

    def test_api_at_threshold(self, matcher: JobMatcher):
        """API cost=max_cost → 0.7 (刚好满足期望下限)。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.05)
        score = matcher.compute_cost_score(c, max_cost=0.05)
        assert score == pytest.approx(0.7, abs=0.02)

    def test_api_exceed_budget_decay(self, matcher: JobMatcher):
        """API cost>max_cost → 衰减但不一票否决。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.075)
        # cost=0.075, max=0.05 → excess=(0.075-0.05)/0.05=0.5 → 0.7-0.7*0.5=0.35
        score = matcher.compute_cost_score(c, max_cost=0.05)
        assert score == pytest.approx(0.35, abs=0.02)

    def test_api_double_exceed_zero(self, matcher: JobMatcher):
        """API cost=2*max → 超出 100%, score=0.0 (但仍参与匹配)。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.10)
        score = matcher.compute_cost_score(c, max_cost=0.05)
        assert score == 0.0

    def test_max_cost_zero_uses_absolute(self, matcher: JobMatcher):
        """max_cost=0 (只接受本地) → 用 cost.cost_score 绝对分。"""
        c = CostBreakdown(deployment_mode="api", estimated_cost_usd=0.5)
        score = matcher.compute_cost_score(c, max_cost=0.0)
        # cost_score = 1.0 - (0.5-0.01)/0.99 = 0.505
        assert score == pytest.approx(0.505, abs=0.01)


# ── 11. Cost 轴: 端到端场景 (D-MCE-07) ────────────────────

class TestCostEndToEnd:
    """成本轴端到端: claude 贵但必要时仍可用。"""

    def test_expensive_model_still_matched(self, matcher: JobMatcher):
        """claude 贵但必要时仍可用: cost_score=0 不淘汰, 仅降 10% match_score。"""
        profile = _make_profile(
            {"code_edit_precision": "A", "refactor": "A",
             "dead_code_removal": "A", "code_generate": "A"},
            cost=CostBreakdown(
                deployment_mode="api", provider="anthropic",
                estimated_cost_usd=2.0,  # 很贵, cost_score=0
            ),
        )
        recs = matcher.match(profile)
        junior = next(r for r in recs if r.job_id == "junior_code_worker")
        # qualified, bonus=1.0, hallu=1.0, cost=0.0
        # score = 0.45 + 0.25 + 0.20 + 0 = 0.90
        assert junior.qualified is True
        assert junior.match_score == pytest.approx(0.90, abs=0.02)
        # 关键: 贵模型仍能匹配 (非一票否决)
        assert junior.match_score > 0.0

    def test_local_cheaper_than_api_scores_higher(self, matcher: JobMatcher):
        """本地模型 (cost_score=1.0) 比昂贵 API (cost_score=0.0) match_score 高 0.10。"""
        grades = {"code_edit_precision": "A", "refactor": "A",
                  "dead_code_removal": "A", "code_generate": "A"}
        local_profile = _make_profile(grades)  # 默认 local
        api_profile = _make_profile(
            grades,
            cost=CostBreakdown(deployment_mode="api", estimated_cost_usd=2.0),
        )
        local_recs = matcher.match(local_profile)
        api_recs = matcher.match(api_profile)
        local_junior = next(r for r in local_recs if r.job_id == "junior_code_worker")
        api_junior = next(r for r in api_recs if r.job_id == "junior_code_worker")
        # cost 权重 0.10: local cost_score=1.0, api cost_score=0.0 → 差 0.10
        assert local_junior.match_score - api_junior.match_score == pytest.approx(0.10, abs=0.02)

    def test_free_api_same_as_local(self, matcher: JobMatcher):
        """免费 API (如 zhipu, cost<=0.01) 与本地模型 cost_score 相同。"""
        grades = {"code_edit_precision": "A", "refactor": "A"}
        local_profile = _make_profile(grades)
        free_api_profile = _make_profile(
            grades,
            cost=CostBreakdown(
                deployment_mode="api", provider="zhipu",
                estimated_cost_usd=0.005,  # 近似免费
            ),
        )
        local_recs = matcher.match(local_profile)
        free_recs = matcher.match(free_api_profile)
        local_j = next(r for r in local_recs if r.job_id == "junior_code_worker")
        free_j = next(r for r in free_recs if r.job_id == "junior_code_worker")
        # 两者 cost_score 都是 1.0 → match_score 相同
        assert local_j.match_score == pytest.approx(free_j.match_score, abs=0.01)
