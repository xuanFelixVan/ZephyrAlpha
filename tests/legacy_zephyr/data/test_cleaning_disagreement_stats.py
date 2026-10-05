# [A_test] module_id=MOD-L00-004-R3-T1 | layer=test | stability=new | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.scripts.test_cleaning_disagreement_stats
# [DOMAIN] D_DATA
# [TTL] permanent
"""C6 分歧率统计 prep 件测试（F04 C6 prep，2026-09-30 F 组夜班）。全部 tmp_path 隔离。"""

from __future__ import annotations

import json
from pathlib import Path

from zephyr.data.cleaning_disagreement_stats import compute, load_t2_threshold


def _write_pairs(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "pairs.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return p


class TestCompute:
    def test_no_data_honest(self, tmp_path):
        out = compute(tmp_path / "missing.jsonl")
        assert out["verdict"] == "no_data" and out["total"] == 0

    def test_rate_and_weekly(self, tmp_path):
        rows = [
            {"ts": "2026-09-01T03:00:00+00:00", "item_key": "a", "engine_verdict": "clean", "ai_verdict": "clean"},
            {"ts": "2026-09-02T03:00:00+00:00", "item_key": "b", "engine_verdict": "clean", "ai_verdict": "dirty"},
            {"ts": "2026-09-08T03:00:00+00:00", "item_key": "c", "engine_verdict": "dirty", "ai_verdict": "dirty"},
        ]
        out = compute(_write_pairs(tmp_path, rows))
        assert out["verdict"] == "ok" and out["total"] == 3 and out["disagreements"] == 1
        assert abs(out["disagreement_rate"] - 0.3333) < 0.001
        assert len(out["weekly"]) == 2 and out["vs_t2"] in ("within", "over")

    def test_corrupt_lines_skipped_counted(self, tmp_path):
        p = tmp_path / "pairs.jsonl"
        p.write_text(
            json.dumps({"ts": "2026-09-01T03:00:00+00:00", "item_key": "a", "engine_verdict": "x", "ai_verdict": "x"})
            + "\n{broken\n",
            encoding="utf-8",
        )
        out = compute(p)
        assert out["total"] == 1 and out["skipped"] == 1

    def test_t2_threshold_from_criteria(self):
        v, src = load_t2_threshold()
        assert src == "switch_criteria" and v is not None and 0 < v < 1
