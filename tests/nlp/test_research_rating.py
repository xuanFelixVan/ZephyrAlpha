# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §Phase 7
# [TTL] permanent
"""test_research_rating.py — 研报结构化评级提取单元测试（CAND-NLP-006）。

覆盖：summary 三字段解析 / 评级映射（含未知→None）/ 标题变动判定（顺序敏感）
/ 目标价提取 / analyze_report 组合。真实库样本口径构造（2026-08-26 侦察）。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.nlp.research_rating import (  # noqa: E402
    REVISION_DOWNGRADE,
    REVISION_INITIATION,
    REVISION_MAINTAIN,
    REVISION_NONE,
    REVISION_UPGRADE,
    analyze_report,
    detect_revision,
    extract_target_price,
    parse_summary_fields,
    rating_score,
)


class TestParseSummaryFields:
    def test_full_form(self):
        f = parse_summary_fields("机构:国金证券 | 评级:买入 | 行业:消费电子")
        assert f == {"机构": "国金证券", "评级": "买入", "行业": "消费电子"}

    def test_partial_and_empty(self):
        assert parse_summary_fields("机构:太平洋") == {"机构": "太平洋"}
        assert parse_summary_fields("") == {}
        assert parse_summary_fields(None) == {}  # type: ignore[arg-type]


class TestRatingScore:
    def test_known_ratings(self):
        assert rating_score("买入") == 1.0
        assert rating_score("增持") == 0.6
        assert rating_score("中性") == 0.0
        assert rating_score("卖出") == -1.0
        assert rating_score("回避") == -1.0

    def test_unknown_returns_none(self):
        assert rating_score("超强烈买入") is None
        assert rating_score("") is None
        assert rating_score(None) is None  # type: ignore[arg-type]


class TestDetectRevision:
    def test_initiation_first(self):
        rev, detail = detect_revision("中小盘首次覆盖报告：高端科学仪器国产替代先锋")
        assert rev == REVISION_INITIATION
        assert detail.startswith("首次覆盖")

    def test_downgrade_with_detail(self):
        rev, detail = detect_revision("2Q换代压力集中释放；下调盈利预测及目标价")
        assert rev == REVISION_DOWNGRADE
        assert "下调盈利预测" in detail

    def test_upgrade_and_maintain(self):
        assert detect_revision("业绩超预期，上调评级至买入")[0] == REVISION_UPGRADE
        assert detect_revision("盈利符合预期，维持增持评级")[0] == REVISION_MAINTAIN

    def test_none(self):
        assert detect_revision("公司事件点评报告：定制化产品数量攀升")[0] == REVISION_NONE
        assert detect_revision("")[0] == REVISION_NONE


class TestExtractTargetPrice:
    def test_forms(self):
        assert extract_target_price("下调目标价至58.5元") == 58.5
        assert extract_target_price("目标价：120 元") == 120.0
        assert extract_target_price("给予目标价45元") == 45.0

    def test_miss_returns_none(self):
        assert extract_target_price("盈利短期承压，新业务稳步推进") is None
        assert extract_target_price("") is None


class TestAnalyzeReport:
    def test_combination(self):
        r = analyze_report(
            "首次覆盖：品牌基因驱动成长，目标价 58 元",
            "机构:招银国际 | 评级:增持 | 行业:工程机械",
        )
        assert r.org == "招银国际"
        assert r.industry == "工程机械"
        assert r.rating == "增持"
        assert r.score == 0.6
        assert r.revision == REVISION_INITIATION
        assert r.target_price == 58.0

    def test_degenerate(self):
        r = analyze_report("", "")
        assert r.score is None and r.revision == REVISION_NONE and r.target_price is None
