# [A_test] module_id: MOD-RPT-009_summary | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RPT-009 | docs/03_modules/_domain_reporting/review_orchestrator/blueprint.md | 缺口总账 GAP-F-40 行
# [MODULE] tests.reporting.test_ai_review_summary
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""AI 复盘结语生成器（GAP-F-40，MOD-RPT-009 族）施工验证测试。

覆盖：
- LLM 网关注入：mock 网关产出被采用（source=llm），prompt 含日期与行情；
  超长输出按 max_chars 截断；空输出视为失败降级；
- 降级链：网关 None/抛异常/空串 → 模板兜底（source=template_fallback）+notes 留痕不抛；
- 战报模板注入：render_war_report 五段齐（市场回顾/板块亮点/预案执行/风险事件/AI 结语）；
- fail-closed：日期非法/行情概述空；
- 契约：frozen、to_dict JSON 可序列化、模板路径确定性。
全程 mock 网关，零真 LLM/网络/DB。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.reporting.ai_review_summary import (
    ReviewContext,
    ReviewSummary,
    SummaryConfig,
    generate_review_summary,
    render_war_report,
)


def _ctx() -> ReviewContext:
    return ReviewContext(
        trade_date="2026-08-21",
        market_overview="上证涨 0.8%，两市成交 1.1 万亿放量",
        sector_highlights=("机器人主线再强化", "医药退潮"),
        plan_outcomes=("预案命中高开高走格", "拟买票 A 触边界未成交"),
        risk_events=("D3 撤单比 0.42 未越线",),
    )


class TestLLMPath:
    def test_mock_gateway_adopted(self) -> None:
        seen: dict[str, str] = {}

        def gw(prompt: str) -> str:
            seen["prompt"] = prompt
            return "今日主线清晰，明日盯龙头分歧转一致。"

        res = generate_review_summary(_ctx(), llm_gateway=gw)
        assert res.source == "llm"
        assert res.summary_text == "今日主线清晰，明日盯龙头分歧转一致。"
        assert "2026-08-21" in seen["prompt"]
        assert "上证涨 0.8%" in seen["prompt"]

    def test_long_output_clamped(self) -> None:
        res = generate_review_summary(_ctx(), llm_gateway=lambda p: "长" * 500, config=SummaryConfig(max_chars=50))
        assert len(res.summary_text) == 50
        assert res.source == "llm"

    def test_whitespace_normalized(self) -> None:
        res = generate_review_summary(_ctx(), llm_gateway=lambda p: "  多空\n\n  分歧  ")
        assert res.summary_text == "多空 分歧"


class TestFallback:
    def test_none_gateway_fallback(self) -> None:
        res = generate_review_summary(_ctx())
        assert res.source == "template_fallback"
        assert "2026-08-21" in res.summary_text
        assert any("未注入" in n for n in res.notes)

    def test_gateway_exception_fallback(self) -> None:
        def bad(prompt: str) -> str:
            raise RuntimeError("boom")

        res = generate_review_summary(_ctx(), llm_gateway=bad)
        assert res.source == "template_fallback"
        assert any("RuntimeError" in n for n in res.notes)

    def test_blank_output_fallback(self) -> None:
        res = generate_review_summary(_ctx(), llm_gateway=lambda p: "   ")
        assert res.source == "template_fallback"
        assert any("空" in n for n in res.notes)

    def test_fallback_deterministic(self) -> None:
        a = generate_review_summary(_ctx())
        b = generate_review_summary(_ctx())
        assert a.summary_text == b.summary_text


class TestWarReport:
    def test_sections_injected(self) -> None:
        summary = generate_review_summary(_ctx(), llm_gateway=lambda p: "结语测试文本")
        report = render_war_report(_ctx(), summary)
        assert "市场回顾" in report
        assert "板块亮点" in report
        assert "预案执行" in report
        assert "风险事件" in report
        assert "结语测试文本" in report
        assert "机器人主线再强化" in report

    def test_empty_sections_degrade(self) -> None:
        ctx = ReviewContext(trade_date="2026-08-21", market_overview="震荡")
        summary = generate_review_summary(ctx)
        report = render_war_report(ctx, summary)
        assert "（无）" in report


class TestValidation:
    def test_bad_date_rejected(self) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            ReviewContext(trade_date="08-21", market_overview="x")

    def test_unreal_date_rejected(self) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            ReviewContext(trade_date="2026-13-01", market_overview="x")

    def test_blank_overview_rejected(self) -> None:
        with pytest.raises(ValueError, match="market_overview"):
            ReviewContext(trade_date="2026-08-21", market_overview="  ")

    def test_bad_max_chars_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_chars"):
            SummaryConfig(max_chars=0)


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = generate_review_summary(_ctx(), llm_gateway=lambda p: "结语")
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "summary_text" in text

    def test_frozen(self) -> None:
        res = generate_review_summary(_ctx())
        assert isinstance(res, ReviewSummary)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.summary_text = "改写"  # type: ignore[misc]
