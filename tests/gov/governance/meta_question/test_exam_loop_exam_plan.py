# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1.1 预注册结构 / §1.2 六查 / §3.3 时间分层
# [MODULE] tests.governance.meta_question.test_exam_loop_exam_plan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.exam_loop.exam_plan（纯计算件，零 IO）
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红腿：①样本不足必判 defer（无降阈值出口）②窗口跨越生成时戳必判 violation
#              ③缺功效预锁项必 defer 并点名缺项（禁伪造默认阈）④份额不可核必返回 None（禁按 0/1 猜）；
#              蓝腿：结构化投影不改底稿原值 + 阈值文本机解逐条可比 + Fisher-z 功效单调性
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红；naive 时戳/越界效应量必须抛
# [TESTS] self
# [TTL] task_bound
"""预注册考卷结构化 + 功效核验 + 时间分层机检测试（PQ-0055/0098 判据载体）。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from zephyr.governance.meta_question.exam_loop import exam_plan

NOW = datetime(2026, 9, 24, 3, 0, 0, tzinfo=timezone.utc)


def _window(start: str, end: str, **extra: object) -> dict[str, object]:
    return {"start": start, "end": end, **extra}


class TestStructurePlan:
    def test_structured_projection_keeps_baseline_and_adds_clauses(self) -> None:
        plan = exam_plan.structure_plan(
            {"method": "全表扫描", "criterion": "rank_ic", "threshold": ">=0.02", "min_confidence": 90.0},
            plan_version="v2-wo-b1",
        )
        assert plan["criterion"] == "rank_ic" and plan["threshold"] == ">=0.02"  # 底稿原值不改
        assert plan["plan_version"] == "v2-wo-b1"
        clauses = [c for c in plan["threshold_clauses"] if "value" in c]
        assert clauses and clauses[0]["value"] == 0.02 and clauses[0]["op"] == ">="
        assert "min_confidence" not in plan["degraded"]
        assert "sample_size" in plan["degraded"]  # 缺项显式留痕（禁静默补默认）

    def test_mixed_threshold_text_parses_primary(self) -> None:
        clauses = exam_plan.parse_threshold_clauses("≥95%（逾期挂起≤5%）")
        values = [c for c in clauses if "value" in c]
        assert values[0]["value"] == 95.0 and values[0]["op"] == ">="
        assert values[1]["value"] == 5.0 and values[1]["op"] == "<="

    def test_required_for_answered_points_missing(self) -> None:
        assert exam_plan.required_for_answered({"criterion": "", "threshold": ""}) == ("criterion", "threshold")
        assert exam_plan.required_for_answered({"criterion": "ic", "threshold": ">=0.02"}) == ()


class TestPowerGate:
    def test_low_power_must_defer_never_lower_threshold(self) -> None:
        """红腿：功效不足→action=defer（本设计无降阈值出口）。"""
        plan = exam_plan.structure_plan(
            {"criterion": "rank_ic", "threshold": ">=0.05", "min_confidence": 95.0, "power_min": 0.8},
            plan_version="v2",
        )
        verdict = exam_plan.assess_power(plan, sample_size=60, effect_size=0.06)
        assert verdict.action == "defer" and verdict.power < 0.8

    def test_sufficient_power_passes(self) -> None:
        plan = exam_plan.structure_plan(
            {"criterion": "rank_ic", "threshold": ">=0.02", "min_confidence": 95.0, "power_min": 0.8},
            plan_version="v2",
        )
        verdict = exam_plan.assess_power(plan, sample_size=500, effect_size=0.15)
        assert verdict.action == "pass" and verdict.power >= 0.8

    def test_missing_prelock_defers_with_named_keys(self) -> None:
        """红腿：功效预锁缺项必 defer 且点名缺项（禁伪造默认阈）。"""
        plan = exam_plan.structure_plan({"criterion": "rank_ic", "threshold": ">=0.02"}, plan_version="v2")
        verdict = exam_plan.assess_power(plan)
        assert verdict.action == "defer"
        assert "power_prelock_missing" in verdict.reason
        assert {"sample_size", "effect_size", "power_min"} <= set(verdict.reason.split(":", 1)[1].split(","))

    def test_fisher_z_monotonic_and_bounds(self) -> None:
        small = exam_plan.fisher_z_power(100, 0.05)
        big = exam_plan.fisher_z_power(1000, 0.05)
        assert small < big
        with pytest.raises(ValueError):
            exam_plan.fisher_z_power(3, 0.5)
        with pytest.raises(ValueError):
            exam_plan.fisher_z_power(500, 1.4)


class TestTimeLayering:
    def test_end_after_previous_close_is_violation(self) -> None:
        """今日输出→明日输入：end 落在执行日当天必违规。"""
        violations = exam_plan.check_time_layering(
            _window("2026-09-01", NOW.date().isoformat()), execution_day=NOW.date()
        )
        assert any(v.code == "window_end_not_before_close" for v in violations)

    def test_straddling_generation_stamp_is_violation(self) -> None:
        """红腿：窗口跨越问题生成时戳（重叠）必违规。"""
        violations = exam_plan.check_time_layering(
            _window("2025-01-01", "2026-01-01"),
            generated_at="2025-06-01T00:00:00+00:00",
            execution_day=date(2026, 9, 24),
        )
        assert any(v.code == "window_straddles_generation" for v in violations)

    def test_clean_windows_pass(self) -> None:
        assert (
            exam_plan.check_time_layering(
                _window("2025-01-01", "2025-06-30"),
                generated_at="2025-09-01T00:00:00+00:00",
                execution_day=date(2026, 9, 24),
            )
            == []
        )

    def test_missing_bounds_violation(self) -> None:
        violations = exam_plan.check_time_layering(_window("2025-01-01", None), execution_day=date(2026, 9, 24))
        assert violations[0].code == "window_bounds_missing"

    def test_inverted_window_violation(self) -> None:
        violations = exam_plan.check_time_layering(_window("2025-06-30", "2025-01-01"), execution_day=date(2026, 9, 24))
        assert any(v.code == "window_inverted" for v in violations)


class TestOutOfSampleShare:
    def test_declared_wins_then_fresh_window_then_in_sample_bounds(self) -> None:
        assert exam_plan.out_of_sample_share(_window("2025-01-01", "2025-06-30"), declared=0.4) == (0.4, "declared")
        share, basis = exam_plan.out_of_sample_share(
            _window("2025-10-01", "2026-01-01"), generated_at="2025-09-01T00:00:00+00:00"
        )
        assert (share, basis) == (1.0, "fresh_window_after_generation")
        share, basis = exam_plan.out_of_sample_share(
            _window("2024-01-01", "2025-01-01", in_sample_start="2024-01-01", in_sample_end="2024-07-01")
        )
        assert basis == "derived_from_in_sample_bounds" and 0.4 < share < 0.6

    def test_unverifiable_returns_none_not_guess(self) -> None:
        """红腿：既无申报又无边界⇒None/unverifiable（禁按 0 或 1 猜，防假绿/假红）。"""
        assert exam_plan.out_of_sample_share(_window("2024-01-01", "2025-01-01")) == (None, "unverifiable")
