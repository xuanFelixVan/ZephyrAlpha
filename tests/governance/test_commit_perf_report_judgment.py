# [A_test] module_id: MOD-GOV_commit_perf_report | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_PERF_REPORT | scripts/governance/commit_perf_report.py | §B2
# [MODULE] tests.governance.test_commit_perf_report_judgment
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] scripts.governance.commit_perf_report (judge_dimensions, aggregate_verdict, drift_events, block_events, _per_day)
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 模块加载失败->skip_module
# [TESTS] test_commit_perf_report_judgment.py
# [TTL] permanent
"""test_commit_perf_report_judgment.py — B2 判定公式回归（2026-09-16）

病根：竞态窗口事件 211（阈值 ≤4/日 为绿）时总体判定仍输出"绿"——原公式
``ok = formal_ratio >= 70 and machine_ratio <= 30`` 只看正式占比/机器伴生比，
竞态窗口与堵点事件游离在判定之外。

治本：judge_dimensions 四维度各自判级（正式占比 ≥70 绿 / 机器伴生 ≤30 绿 /
竞态 ≤4 绿·>4 黄·>50 红 / 堵点 ≤100 绿·>100 黄）+ aggregate_verdict 与门聚合。
本测试用 tmp_path 构造越界与不越界两种事件集（jsonl），断言判定分别为红/黄与绿。
测试隔离：全部走 tmp_path jsonl，不读/不写生产 .runtime/audit/。
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "governance" / "commit_perf_report.py"
)

try:
    _spec = importlib.util.spec_from_file_location("commit_perf_report", _SCRIPT_PATH)
    perf = importlib.util.module_from_spec(_spec)
    sys.modules["commit_perf_report"] = perf
    _spec.loader.exec_module(perf)
    judge_dimensions = perf.judge_dimensions
    aggregate_verdict = perf.aggregate_verdict
    drift_events = perf.drift_events
    block_events = perf.block_events
    _per_day = perf._per_day
except Exception as e:  # noqa: BLE001
    pytest.skip(f"commit_perf_report 模块加载失败: {e}", allow_module_level=True)


def _write_jsonl(path: Path, n: int, *, event: str = "gate_window_race", age_hours: float = 0.0) -> None:
    """构造 n 条事件 jsonl（timestamp=now-age_hours；age_hours 大于窗口=窗外应被滤除）。"""
    ts = (datetime.now(timezone.utc) - timedelta(hours=age_hours)).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            f.write(f'{{"timestamp": "{ts}", "event": "{event}", "session_id": "s{i}", "gate_id": "G-{i}"}}\n')


class TestPerDay:
    def test_24h_window_one_day(self):
        assert _per_day(211, 24) == 211.0

    def test_48h_window_two_days(self):
        assert _per_day(211, 48) == 105.5

    def test_small_window_counts_as_one_day(self):
        """窗口 <24h 按 1 日计，避免小窗放大误判。"""
        assert _per_day(3, 6) == 3.0


class TestJudgeDimensionsAllGreen:
    """不越界事件集 → 四维度全绿，总体判定绿。"""

    def test_all_green(self, tmp_path: Path):
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 4)  # 4/日 = 阈值内（≤4 绿）
        blocks_jsonl = tmp_path / "commit_block_events.jsonl"
        _write_jsonl(blocks_jsonl, 3, event="commit_blocked")

        drift_n = drift_events(24, path=drift_jsonl)
        blocks = [e for e in block_events(24, path=blocks_jsonl) if e.get("event") == "commit_blocked"]
        rows = judge_dimensions(80, 20, _per_day(drift_n, 24), _per_day(len(blocks), 24))
        assert [v for _, v, _ in rows] == ["绿", "绿", "绿", "绿"]
        assert aggregate_verdict(rows) == "绿"


class TestJudgeDimensionsRaceOverflow:
    """竞态窗口越界（B2 病根场景：211 事件）→ 不再输出绿。"""

    def test_race_211_per_day_is_red(self, tmp_path: Path):
        """24h 窗口 211 条竞态事件（211/日 > 50）→ 竞态维度红，总体红。

        复现病根数据：2026-09 并发调查中 48h 窗口 211 事件的实况。
        """
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 211)
        drift_n = drift_events(24, path=drift_jsonl)
        assert drift_n == 211
        rows = judge_dimensions(80, 20, _per_day(drift_n, 24), 0.0)
        race = next(v for name, v, _ in rows if name == "竞态窗口")
        assert race == "红"
        assert aggregate_verdict(rows) == "红"

    def test_race_48h_211_events_folds_to_105_daily_still_red(self, tmp_path: Path):
        """48h 窗口 211 条 → 折算 105.5/日 仍 > 50 → 红。"""
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 211)
        drift_n = drift_events(48, path=drift_jsonl)
        rows = judge_dimensions(70, 30, _per_day(drift_n, 48), 0.0)
        assert next(v for name, v, _ in rows if name == "竞态窗口") == "红"
        assert aggregate_verdict(rows) == "红"

    def test_race_5_per_day_is_yellow(self, tmp_path: Path):
        """5/日（>4 且 ≤50）→ 竞态维度黄，总体黄。"""
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 5)
        drift_n = drift_events(24, path=drift_jsonl)
        rows = judge_dimensions(80, 20, _per_day(drift_n, 24), 0.0)
        assert next(v for name, v, _ in rows if name == "竞态窗口") == "黄"
        assert aggregate_verdict(rows) == "黄"

    def test_boundary_4_per_day_stays_green(self, tmp_path: Path):
        """恰好 4/日（阈值 ≤4 绿，不越界）。"""
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 4)
        drift_n = drift_events(24, path=drift_jsonl)
        rows = judge_dimensions(80, 20, _per_day(drift_n, 24), 0.0)
        assert next(v for name, v, _ in rows if name == "竞态窗口") == "绿"


class TestJudgeDimensionsOtherDimensions:
    """其余维度越界 → 黄。"""

    def test_blocks_over_100_daily_is_yellow(self, tmp_path: Path):
        """堵点 101/日（>100）→ 堵点维度黄，总体黄。"""
        blocks_jsonl = tmp_path / "commit_block_events.jsonl"
        _write_jsonl(blocks_jsonl, 101, event="commit_blocked")
        blocks = [e for e in block_events(24, path=blocks_jsonl) if e.get("event") == "commit_blocked"]
        rows = judge_dimensions(80, 20, 0.0, _per_day(len(blocks), 24))
        assert next(v for name, v, _ in rows if name == "堵点事件") == "黄"
        assert aggregate_verdict(rows) == "黄"

    def test_formal_ratio_below_70_is_yellow(self):
        rows = judge_dimensions(60, 40, 0.0, 0.0)
        assert next(v for name, v, _ in rows if name == "正式提交占比") == "黄"
        assert aggregate_verdict(rows) == "黄"

    def test_machine_ratio_above_30_is_yellow(self):
        rows = judge_dimensions(65, 35, 0.0, 0.0)
        assert next(v for name, v, _ in rows if name == "机器伴生比") == "黄"
        assert aggregate_verdict(rows) == "黄"


class TestEventWindowFilter:
    def test_events_outside_window_excluded(self, tmp_path: Path):
        """窗口外（3 天前）事件不计入 → 0/日 绿。"""
        drift_jsonl = tmp_path / "hook_tracked_drift.jsonl"
        _write_jsonl(drift_jsonl, 50, age_hours=72)
        assert drift_events(24, path=drift_jsonl) == 0

    def test_missing_file_returns_zero(self, tmp_path: Path):
        assert drift_events(24, path=tmp_path / "nonexistent.jsonl") == 0
        assert block_events(24, path=tmp_path / "nonexistent.jsonl") == []
