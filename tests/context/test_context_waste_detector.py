# [A_test] module_id: MOD-GOV_context_waste_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_context_waste_detector
# [INVARIANTS] waste_ratio in [0,1]; analyze returns WasteReport
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.context_governance.context_waste_detector import (
    ContextWasteDetector,
    WasteReport,
)


class TestContextWasteDetector:
    def test_instantiation_defaults(self):
        det = ContextWasteDetector()
        assert det.context_fill_ratio() == 0.0

    def test_instantiation_custom(self):
        det = ContextWasteDetector(max_context=16000, waste_threshold=0.3)
        assert det.context_fill_ratio() == 0.0

    def test_analyze_empty(self):
        det = ContextWasteDetector()
        report = det.analyze()
        assert isinstance(report, WasteReport)
        assert report.wasted_tokens == 0
        assert report.waste_ratio == 0.0
        assert report.unique_content_ratio == 1.0
        assert report.actionable is False

    def test_feed_and_analyze_unique(self):
        det = ContextWasteDetector()
        det.feed("This is unique content that is not repeated anywhere else in the context.")
        report = det.analyze()
        assert report.waste_ratio == 0.0
        assert report.actionable is False

    def test_feed_and_analyze_redundant(self):
        det = ContextWasteDetector(waste_threshold=0.3)
        repeated = "A" * 400
        for _ in range(5):
            det.feed(repeated)
        report = det.analyze()
        assert report.waste_ratio > 0.0
        assert report.redundancy_score > 0.0

    def test_context_fill_ratio(self):
        det = ContextWasteDetector(max_context=1000)
        det.feed("A" * 4000)
        ratio = det.context_fill_ratio()
        assert ratio > 0.0

    def test_context_fill_ratio_zero_max(self):
        det = ContextWasteDetector(max_context=0)
        assert det.context_fill_ratio() == 0.0

    def test_reset(self):
        det = ContextWasteDetector()
        det.feed("Some content here to fill up the context window.")
        det.reset()
        assert det.context_fill_ratio() == 0.0
        report = det.analyze()
        assert report.wasted_tokens == 0

    def test_actionable_when_high_redundancy(self):
        det = ContextWasteDetector(waste_threshold=0.2)
        chunk = "X" * 200
        for _ in range(10):
            det.feed(chunk)
        report = det.analyze()
        assert report.actionable is True

    def test_advice_severe_redundancy(self):
        det = ContextWasteDetector(waste_threshold=0.1)
        chunk = "Y" * 200
        for _ in range(20):
            det.feed(chunk)
        report = det.analyze()
        assert "严重冗余" in report.advice or "冗余" in report.advice

    def test_chunk_eviction_at_500(self):
        det = ContextWasteDetector()
        for i in range(600):
            det.feed(f"Unique chunk {i} with enough text to be a real chunk here.")
        report = det.analyze()
        assert isinstance(report, WasteReport)


class TestBoundaryCases:
    def test_feed_empty_string(self):
        det = ContextWasteDetector()
        det.feed("")
        report = det.analyze()
        assert isinstance(report, WasteReport)

    def test_feed_very_short_string(self):
        det = ContextWasteDetector()
        det.feed("Hi")
        report = det.analyze()
        assert isinstance(report, WasteReport)

    def test_analyze_without_feed(self):
        det = ContextWasteDetector()
        report = det.analyze()
        assert report.wasted_tokens == 0
