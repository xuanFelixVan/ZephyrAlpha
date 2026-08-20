# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md
# [MODULE] tests.reporting.test_review_template_engine
# [DOMAIN] D_REPORTING
# [INVARIANTS] 四段固定序; 空段降级; 输入类型校验; 纯函数
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTemplateInputError
# [TESTS] self
# [TTL] permanent
"""周复盘模板引擎测试（55 号 §6 暂缓项固化，AI-NIGHT-001 包P）。"""

from __future__ import annotations

import pytest

from zephyr.reporting.review_orchestrator import WEEKLY_REVIEW_SECTIONS
from zephyr.reporting.review_template_engine import (
    InvalidTemplateInputError,
    render_weekly_review,
)


class TestStructure:
    def test_four_sections_in_fixed_order(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="盈亏 +1.2%",
            deviation_events="无偏离告警",
            threshold_changes="THD-X 0.3→0.35",
            action_items=["复核 S1 滑点", "校准阈值"],
        )
        idx = [md.index(f"## {i}. {title}") for i, title in enumerate(WEEKLY_REVIEW_SECTIONS, 1)]
        assert idx == sorted(idx)  # 段序固定递增
        assert md.startswith("# 周复盘 2026-W34")

    def test_action_items_rendered_as_checkboxes(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="x",
            deviation_events="x",
            threshold_changes="x",
            action_items=["复核 S1 滑点", "校准阈值"],
        )
        assert "- [ ] 复核 S1 滑点" in md
        assert "- [ ] 校准阈值" in md

    def test_risk_overview_line_rendered(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="x",
            deviation_events="x",
            threshold_changes="x",
            action_items=[],
            risk_overview="日均评分 82 / 最大回撤 3.1% / 告警 2 条 / 趋势 平稳",
        )
        assert "> 风险概览：日均评分 82" in md

    def test_no_risk_overview_line_when_absent(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="x",
            deviation_events="x",
            threshold_changes="x",
            action_items=[],
        )
        assert "风险概览" not in md


class TestDegradation:
    def test_empty_sections_fallback(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="",
            deviation_events="  ",
            threshold_changes="",
            action_items=[],
        )
        assert md.count("（本期无）") == 4  # 三段空字符串 + 空 action_items

    def test_structure_complete_even_all_empty(self):
        md = render_weekly_review(
            period="2026-W34",
            pnl_attribution="",
            deviation_events="",
            threshold_changes="",
            action_items=[],
        )
        for i, title in enumerate(WEEKLY_REVIEW_SECTIONS, 1):
            assert f"## {i}. {title}" in md


class TestInputValidation:
    def test_empty_period_rejected(self):
        with pytest.raises(InvalidTemplateInputError):
            render_weekly_review("  ", "a", "b", "c", [])

    def test_non_string_section_rejected(self):
        with pytest.raises(InvalidTemplateInputError):
            render_weekly_review("2026-W34", 123, "b", "c", [])  # type: ignore[arg-type]

    def test_none_action_items_rejected(self):
        with pytest.raises(InvalidTemplateInputError):
            render_weekly_review("2026-W34", "a", "b", "c", None)  # type: ignore[arg-type]

    def test_non_string_action_item_rejected(self):
        with pytest.raises(InvalidTemplateInputError):
            render_weekly_review("2026-W34", "a", "b", "c", ["ok", 42])  # type: ignore[list-item]
