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


# ── 事件挂点（maybe_snapshot_emotion_index：快照器从 manual 挂上事件门，照抄 judgment settle 先例）──
# 测试隔离：marker/告警/子进程全 monkeypatch（零生产 IO；子进程假件注入——禁真触发生产调度）。

sys.path.insert(0, str(_RUN_ROOT / "src"))
from zephyr.strategy_pipeline import pipeline_events as pe  # noqa: E402


class _FakeProc:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_hook_skips_non_wake_points() -> None:
    # 非情绪落表任务 / 失败完成 / pre_open（盘前抢跑会挡当日收盘态快照，5_self §3.2）全跳过
    assert (
        pe.maybe_snapshot_emotion_index(task_id="kline_daily_incremental", success=True)["action"]
        == "skipped_wake_point"
    )
    assert (
        pe.maybe_snapshot_emotion_index(task_id="emotion_index_close_final", success=False)["action"]
        == "skipped_wake_point"
    )
    assert (
        pe.maybe_snapshot_emotion_index(task_id="emotion_index_pre_open", success=True)["action"]
        == "skipped_wake_point"
    )


def test_hook_marker_idempotent_zero_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-10-12")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: True)
    called: list = []
    monkeypatch.setattr(
        "zephyr.shared.infra.process_pool.run_subprocess_hidden",
        lambda *a, **k: called.append(a) or _FakeProc(),
    )
    out = pe.maybe_snapshot_emotion_index(task_id="emotion_index_close_final")
    assert out == {"action": "already_snapshotted", "trade_date": "2026-10-12"}
    assert called == []  # 业务日记号已落=零子进程


def test_hook_success_runs_snapshot_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-10-12")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: False)
    touched: list[str] = []
    monkeypatch.setattr(pe, "_touch_marker", lambda key: touched.append(key))
    cmds: list[tuple[list, dict]] = []

    def fake_run(cmd, **kwargs):
        cmds.append((cmd, kwargs))
        return _FakeProc(returncode=0, stdout='{"rows": 2044, "file": "emotion_index_x.jsonl.gz"}')

    monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", fake_run)
    alerts: list = []
    monkeypatch.setattr(pe, "alert", lambda *a, **k: alerts.append((a, k)))
    out = pe.maybe_snapshot_emotion_index(task_id="emotion_index_close_final")
    assert out["action"] == "snapshotted" and out["trade_date"] == "2026-10-12"
    assert "2044" in out["brief"]  # 台账行（stdout 末行）进 brief
    assert touched == ["emotion_index_snapshot_daily:2026-10-12"]
    cmd, kw = cmds[0]
    assert cmd[0] == sys.executable and cmd[1].endswith("emotion_index_snapshot.py")
    assert "--out-dir" in cmd and str(pe.ROOT / "data/emotion_index_snapshots") in cmd  # 绝对路径钉死仓库根
    assert kw["timeout"] == pe.EMOTION_SNAPSHOT_TIMEOUT_S and str(pe.ROOT) == kw["cwd"]
    assert alerts and alerts[0][1].get("level") == "INFO"


def test_hook_marker_touched_before_subprocess_and_error_visible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", lambda: "2026-10-12")
    monkeypatch.setattr(pe, "_marker_seen", lambda key: False)
    order: list[str] = []
    monkeypatch.setattr(pe, "_touch_marker", lambda key: order.append("marker"))
    monkeypatch.setattr(pe, "alert", lambda *a, **k: order.append("alert"))

    def fake_run(cmd, **kwargs):
        order.append("subprocess")
        return _FakeProc(returncode=1, stderr="CH down")

    monkeypatch.setattr("zephyr.shared.infra.process_pool.run_subprocess_hidden", fake_run)
    out = pe.maybe_snapshot_emotion_index(task_id="emotion_index_close_final")
    assert order[:2] == ["marker", "subprocess"]  # 记号先落再动手（防失败重跑风暴裁定）
    assert out["action"] == "error" and out["trade_date"] == "2026-10-12"
    assert "alert" in order  # 失败必须出声


def test_hook_never_raises_on_resolver_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom():
        raise RuntimeError("CH down")

    monkeypatch.setattr(pe, "resolve_pf_alloc_trade_date", boom)
    monkeypatch.setattr(pe, "alert", lambda *a, **k: None)
    out = pe.maybe_snapshot_emotion_index(task_id="emotion_index_close_final")
    assert out["action"] == "error" and "RuntimeError" in out["error"]
