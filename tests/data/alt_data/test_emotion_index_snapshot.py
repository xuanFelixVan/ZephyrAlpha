# [TTL] permanent
# [BLUEPRINT] MOD-ALT-EMOTION-INDEX-BUILDER | tests/data/alt_data/test_emotion_index_snapshot.py | 快照器单测（tmp_path 注入零CH零生产目录）
"""emotion_index_snapshot 单测：append-only 落盘/同名拒写/台账追加/PIT 读径/字节保真（tmp_path 注入）。"""

from __future__ import annotations

import datetime as _dt
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_RUN_ROOT = Path(__file__).resolve().parents[3]
_MOD_PATH = _RUN_ROOT / "scripts" / "data" / "emotion_index_snapshot.py"
_spec = importlib.util.spec_from_file_location("emotion_index_snapshot_under_test", _MOD_PATH)
ex = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("emotion_index_snapshot_under_test", ex)
assert _spec.loader is not None
_spec.loader.exec_module(ex)


def _rows(n: int = 3) -> list[tuple]:
    return [
        (
            _dt.date(2026, 9, 1 + i),
            "close_final",
            _dt.datetime(2026, 9, 1 + i, 15, 10),
            0.5 + i / 10,
            json.dumps([{"name": "C1", "asof": f"2026-09-0{i + 1}"}]),
            "v0.1.0",
            _dt.datetime(2026, 9, 1 + i, 15, 30),
            "replay",
        )
        for i in range(n)
    ]


def test_write_snapshot_gz_manifest_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "snaps"
    rec = ex.write_snapshot(out, _rows(), stamp="20261008T000000Z")
    assert rec["rows"] == 3 and rec["min_trade_date"] == "2026-09-01"
    f = out / "emotion_index_20261008T000000Z.jsonl.gz"
    assert f.exists()
    payload = gzip.decompress(f.read_bytes()).decode("utf-8")
    lines = payload.strip().splitlines()
    assert len(lines) == 3
    first = json.loads(lines[0])
    assert json.loads(first["components"])[0]["name"] == "C1" and first["version"] == "v0.1.0"
    manifest = json.loads((out / "manifest.jsonl").read_text(encoding="utf-8").strip())
    assert manifest["sha256"] == rec["sha256"] == hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_write_snapshot_refuses_overwrite_and_empty(tmp_path: Path) -> None:
    out = tmp_path / "snaps"
    ex.write_snapshot(out, _rows(), stamp="20261008T000000Z")
    before = (out / "manifest.jsonl").read_text(encoding="utf-8")
    with pytest.raises(ex.SnapshotError, match="append-only"):
        ex.write_snapshot(out, _rows(), stamp="20261008T000000Z")
    assert (out / "manifest.jsonl").read_text(encoding="utf-8") == before  # 台账零污染
    with pytest.raises(ex.SnapshotError, match="0 行"):
        ex.write_snapshot(out, [], stamp="20261008T000001Z")


def test_pit_state_path_picks_latest_le_asof(tmp_path: Path) -> None:
    out = tmp_path / "snaps"
    ex.write_snapshot(out, _rows(), stamp="20261006T000000Z")
    ex.write_snapshot(out, _rows(2), stamp="20261008T000000Z")
    assert ex.pit_state_path(out, "2026-10-07").name == "emotion_index_20261006T000000Z.jsonl.gz"
    assert ex.pit_state_path(out, "2026-10-08").name == "emotion_index_20261008T000000Z.jsonl.gz"
    with pytest.raises(ex.SnapshotError, match="无合格快照"):
        ex.pit_state_path(out, "2026-10-05")


def test_rows_to_lines_rejects_bad_width() -> None:
    with pytest.raises(ex.SnapshotError, match="列宽不符"):
        ex.rows_to_lines([("2026-09-01", "close_final")])
