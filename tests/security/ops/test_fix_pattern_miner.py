# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] tests.security.ops.test_fix_pattern_miner
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/security/ops/test_fix_pattern_miner.py -q
# [TTL] permanent

"""修复模式挖掘器（Learn 回写闭环，MOD-INF-055）测试。

验收对照（16号文 §4.4 P2-1）：
- 周期性挖掘 data/fix_patterns/pattern_index.yaml 修复记录 → 修复策略库更新建议；
- Diagnose 匹配命中率统计输出（指标只观测不设目标值）；
- 只产建议不落策略库（A-L2 封顶，采纳 human_gated）；挖掘报告 append-only。

挖掘逻辑为纯内存函数（mine_records），夹具全内存构造；
仅 run_once 持久化用例用 tmp_path（复用真实 FixPatternStore 播种）。
"""

from __future__ import annotations

import json

from zephyr.security.ops.fix_pattern_miner import (
    FixPatternMiner,
    MinerConfig,
    SuggestionKind,
    mine_records,
)
from zephyr.security.ops.incident_pipeline import FixPatternStore


def _rec(
    category: str = "validation",
    action_type: str = "config_fix",
    status: str = "completed",
    fault_class: str = "structural",
    target: str = "src/zephyr/foo.py",
) -> dict:
    return {
        "record_id": "r-x",
        "ts": "2026-08-30T00:00:00Z",
        "fault_class": fault_class,
        "channel": "auto_template",
        "action_type": action_type,
        "action_status": status,
        "category": category,
        "target": target,
        "suggestion": "检查字段对齐",
    }


class TestDiagnoseHitRate:
    def test_empty_records_yield_zero_hit_rate_and_no_suggestions(self):
        report = mine_records([], patterns=[])
        assert report.total_records == 0
        assert report.diagnose.total_records == 0
        assert report.diagnose.matched_records == 0
        assert report.diagnose.hit_rate == 0.0
        assert report.suggestions == ()

    def test_full_coverage_hit_rate_is_one(self):
        records = [_rec(category="validation"), _rec(category="syntax", action_type="import_fix")]
        patterns = [{"category": "validation"}, {"category": "syntax"}]
        report = mine_records(records, patterns=patterns)
        assert report.diagnose.total_records == 2
        assert report.diagnose.matched_records == 2
        assert report.diagnose.hit_rate == 1.0

    def test_partial_coverage_hit_rate_and_fault_class_breakdown(self):
        records = [
            _rec(category="validation", fault_class="structural"),
            _rec(category="unknown_logic", action_type="llm_fix", fault_class="semantic"),
        ]
        patterns = [{"category": "validation"}]
        report = mine_records(records, patterns=patterns)
        assert report.diagnose.hit_rate == 0.5
        assert report.diagnose.by_fault_class["structural"] == 1.0
        assert report.diagnose.by_fault_class["semantic"] == 0.0


class TestStrategySuggestions:
    def test_promote_when_frequent_and_high_success(self):
        records = [_rec() for _ in range(3)]
        report = mine_records(records, patterns=[{"category": "validation"}])
        kinds = {s.kind for s in report.suggestions}
        assert SuggestionKind.PROMOTE_PATTERN in kinds
        sug = next(s for s in report.suggestions if s.kind is SuggestionKind.PROMOTE_PATTERN)
        assert sug.frequency == 3
        assert sug.success_rate == 1.0

    def test_no_suggestion_below_min_frequency(self):
        records = [_rec() for _ in range(2)]  # 默认 min_frequency=3
        report = mine_records(records, patterns=[{"category": "validation"}])
        assert report.suggestions == ()

    def test_review_when_low_success_rate(self):
        records = [_rec(status="failed") for _ in range(2)] + [_rec(status="completed")]
        report = mine_records(records, patterns=[{"category": "validation"}])
        kinds = {s.kind for s in report.suggestions}
        assert SuggestionKind.REVIEW_PATTERN in kinds
        assert SuggestionKind.PROMOTE_PATTERN not in kinds
        sug = next(s for s in report.suggestions if s.kind is SuggestionKind.REVIEW_PATTERN)
        assert sug.success_rate < 0.5

    def test_enrich_diagnosis_for_uncovered_category_cluster(self):
        records = [_rec(category="novel_drift", action_type="llm_fix", fault_class="semantic") for _ in range(3)]
        report = mine_records(records, patterns=[{"category": "validation"}])
        kinds = {s.kind for s in report.suggestions}
        assert SuggestionKind.ENRICH_DIAGNOSIS in kinds
        assert report.diagnose.hit_rate == 0.0

    def test_non_mapping_record_skipped_and_counted(self):
        records = [_rec(), "garbage-line"]
        report = mine_records(records, patterns=[{"category": "validation"}])
        assert report.skipped_records == 1
        assert report.total_records == 1
        assert report.diagnose.hit_rate == 1.0


class TestRunOncePersistence:
    def test_run_once_appends_report_jsonl(self, tmp_path):
        store_dir = tmp_path / "fix_patterns"
        runtime_dir = tmp_path / "runtime"
        store = FixPatternStore(store_dir)
        store.ensure_files()
        store.append_fix_record(_rec())
        miner = FixPatternMiner(MinerConfig(store_dir=store_dir, runtime_dir=runtime_dir))
        first = miner.run_once()
        second = miner.run_once()
        assert first.total_records == 1
        assert second.total_records == 1
        lines = (runtime_dir / "pattern_mining_reports.jsonl").read_text(encoding="utf-8")
        entries = [json.loads(line) for line in lines.splitlines() if line.strip()]
        assert len(entries) == 2, "挖掘报告 MUST append-only 留痕"
        assert entries[0]["report_id"] != entries[1]["report_id"]
        assert entries[0]["diagnose"]["total_records"] == 1
