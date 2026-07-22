# [A_test] module_id: MOD-GOV_streaming_reader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-553 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_streaming_reader
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_streaming_reader.py - StreamingReader unit tests
======================================================

TASK-INF-0140 Phase 2 verification.
"""


import json

from zephyr.shared.io.streaming_reader import stream_jsonl, tail_jsonl


def _write_jsonl(path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


class TestTailJsonl:
    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.jsonl"
        f.write_text("", encoding="utf-8")
        assert tail_jsonl(str(f)) == []

    def test_nonexistent_file(self, tmp_path):
        assert tail_jsonl(str(tmp_path / "nope.jsonl")) == []

    def test_fewer_than_n(self, tmp_path):
        f = tmp_path / "small.jsonl"
        _write_jsonl(str(f), [{"i": 1}, {"i": 2}])
        result = tail_jsonl(str(f), n=100)
        assert len(result) == 2

    def test_exactly_n(self, tmp_path):
        f = tmp_path / "exact.jsonl"
        records = [{"i": i} for i in range(5)]
        _write_jsonl(str(f), records)
        result = tail_jsonl(str(f), n=5)
        assert len(result) == 5

    def test_more_than_n(self, tmp_path):
        f = tmp_path / "big.jsonl"
        records = [{"i": i} for i in range(20)]
        _write_jsonl(str(f), records)
        result = tail_jsonl(str(f), n=5)
        assert len(result) == 5
        assert result[0]["i"] == 15
        assert result[4]["i"] == 19

    def test_preserves_order(self, tmp_path):
        f = tmp_path / "order.jsonl"
        records = [{"i": i} for i in range(10)]
        _write_jsonl(str(f), records)
        result = tail_jsonl(str(f), n=3)
        assert [r["i"] for r in result] == [7, 8, 9]

    def test_skips_malformed_lines(self, tmp_path):
        f = tmp_path / "mixed.jsonl"
        with open(str(f), "w", encoding="utf-8") as fh:
            fh.write('{"ok": 1}\n')
            fh.write("bad line\n")
            fh.write('{"ok": 2}\n')
        result = tail_jsonl(str(f), n=10)
        assert len(result) == 2
        assert result[0]["ok"] == 1

    def test_skips_blank_lines(self, tmp_path):
        f = tmp_path / "blanks.jsonl"
        with open(str(f), "w", encoding="utf-8") as fh:
            fh.write('{"a": 1}\n\n{"a": 2}\n')
        result = tail_jsonl(str(f), n=10)
        assert len(result) == 2


class TestStreamJsonl:
    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.jsonl"
        f.write_text("", encoding="utf-8")
        assert list(stream_jsonl(str(f))) == []

    def test_nonexistent_file(self, tmp_path):
        assert list(stream_jsonl(str(tmp_path / "nope.jsonl"))) == []

    def test_reads_all(self, tmp_path):
        f = tmp_path / "all.jsonl"
        records = [{"i": i} for i in range(5)]
        _write_jsonl(str(f), records)
        result = list(stream_jsonl(str(f)))
        assert len(result) == 5

    def test_generator_not_list(self, tmp_path):
        f = tmp_path / "gen.jsonl"
        _write_jsonl(str(f), [{"i": 1}])
        result = stream_jsonl(str(f))
        assert hasattr(result, "__next__")

    def test_skips_malformed(self, tmp_path):
        f = tmp_path / "mixed.jsonl"
        with open(str(f), "w", encoding="utf-8") as fh:
            fh.write('{"ok": 1}\n')
            fh.write("not json\n")
            fh.write('{"ok": 2}\n')
        result = list(stream_jsonl(str(f)))
        assert len(result) == 2
