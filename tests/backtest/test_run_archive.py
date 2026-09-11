# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""run_archive 图书馆 API 单测（SOP-D §4/§5/§9——tmp 根隔离，不触真实档案区）。"""
from __future__ import annotations

import json

import pytest

from zephyr.backtest.run_archive import (
    RunArchiveError,
    create_run,
    finalize_run,
    iter_run_ids,
    load_meta,
    log_iteration,
    write_step,
)


@pytest.fixture()
def root(tmp_path):
    return tmp_path / "runs"


def _open_val_run(root, run_id="VAL-20260912-000000", object_id="BT-P0-001"):
    create_run(run_id, object_id, "VAL", artifacts_root=root,
               window={"start": "2019-01-01", "end": "2025-09-10"},
               holdout={"mode": "anchor", "cutoff": "2026-09-09"})
    return run_id


def _fill_val_steps(root, run_id="VAL-20260912-000000"):
    write_step(run_id, "01", "# 候选算法清单", artifacts_root=root)
    write_step(run_id, "02", "[]", artifacts_root=root)
    write_step(run_id, "03", "[]", artifacts_root=root)
    write_step(run_id, "04", b"\x00\x01", filename="raw_metrics.bin", artifacts_root=root)
    write_step(run_id, "05", "[]", artifacts_root=root)
    write_step(run_id, "06", b"equity", filename="equity.csv", artifacts_root=root)
    write_step(run_id, "verdict", "# 判定书", artifacts_root=root)


# ── create_run ───────────────────────────────────────────────────────────

def test_create_run_writes_meta_with_snapshot(root):
    rid = _open_val_run(root)
    meta = load_meta(rid, artifacts_root=root)
    assert meta["run_id"] == rid
    assert meta["object_id"] == "BT-P0-001"
    assert meta["kind"] == "VAL"
    assert meta["snapshot_commit"]          # PB-06 快照绑定必带
    assert meta["cost_mode"] == "rough"
    assert meta["steps"] == {}
    assert (root / rid / "meta.json").exists()


def test_create_run_rejects_bad_id_and_kind(root):
    with pytest.raises(RunArchiveError):
        create_run("../evil", "BT-P0-001", "VAL", artifacts_root=root)
    with pytest.raises(RunArchiveError):
        create_run("bt-abc", "BT-P0-001", "VAL", artifacts_root=root)   # bt-* 是引擎产物前缀，非 run 目录
    with pytest.raises(RunArchiveError):
        create_run("VAL-X", "BT-P0-001", "NOPE", artifacts_root=root)


def test_create_run_frozen_unique(root):
    _open_val_run(root)
    with pytest.raises(RunArchiveError):
        _open_val_run(root)


def test_create_run_object_concurrency_gate(root):
    rid = _open_val_run(root)   # 未归档
    with pytest.raises(RunArchiveError):
        create_run("VAL-20260912-000001", "BT-P0-001", "VAL", artifacts_root=root)
    finalize_ok = _fill_val_steps_and_finalize(root, rid)
    assert finalize_ok["steps"]["verdict"] == "done"
    # 归档后同对象可开新 run（重验场景）
    create_run("VAL-20260912-000001", "BT-P0-001", "VAL", artifacts_root=root)


def _fill_val_steps_and_finalize(root, rid):
    _fill_val_steps(root, rid)
    return finalize_run(rid, verdict_ref={"table": "c1_backtest.node_verdict", "run_id": rid},
                        artifacts_root=root)


def test_create_run_concurrent_escape(root):
    _open_val_run(root)
    create_run("VAL-20260912-000002", "BT-P0-001", "VAL", artifacts_root=root, allow_concurrent=True)


# ── write_step：只增不改 + ASCII ─────────────────────────────────────────

def test_write_step_fixed_file_and_no_overwrite(root):
    rid = _open_val_run(root)
    p = write_step(rid, "01", "# 候选算法清单（>=3 候选+出处）", artifacts_root=root)
    assert p.name == "01_survey.md"
    with pytest.raises(RunArchiveError):
        write_step(rid, "01", "覆盖", artifacts_root=root)


def test_write_step_subdir_requires_ascii_filename(root):
    rid = _open_val_run(root)
    with pytest.raises(RunArchiveError):
        write_step(rid, "04", "x", artifacts_root=root)   # 缺 filename
    with pytest.raises(RunArchiveError):
        write_step(rid, "04", "x", filename="净值曲线.png", artifacts_root=root)   # 非 ASCII
    p = write_step(rid, "04", "x", filename="wide_summary.csv", artifacts_root=root)
    assert p.parent.name == "04_wide"


def test_write_step_unknown_step(root):
    rid = _open_val_run(root)
    with pytest.raises(RunArchiveError):
        write_step(rid, "99", "x", artifacts_root=root)


# ── log_iteration / finalize_run ─────────────────────────────────────────

def test_log_iteration_appends_and_counts(root):
    rid = _open_val_run(root)
    n1 = log_iteration(rid, "MA 窗口 20→30", "吸筹段信号过密", "OOS IC 0.03→0.05", True, artifacts_root=root)
    n2 = log_iteration(rid, "止损 -5%→-3%", "宽测回撤过大", "回撤改善但触发翻倍", False, artifacts_root=root)
    assert (n1, n2) == (1, 2)
    assert load_meta(rid, artifacts_root=root)["attempts"] == 2
    text = (root / rid / "07_iteration_log.yaml").read_text(encoding="utf-8")
    assert "round: 2" in text and "kept: False" in text


def test_finalize_requires_matrix_and_iteration_log(root):
    rid = _open_val_run(root)
    with pytest.raises(RunArchiveError) as ei:
        finalize_run(rid, artifacts_root=root)
    assert "01" in str(ei.value) and "verdict" in str(ei.value)
    _fill_val_steps(root, rid)
    log_iteration(rid, "a", "b", "c", True, artifacts_root=root)
    log_iteration(rid, "d", "e", "f", True, artifacts_root=root)   # attempts=2 → 07 必选
    meta = finalize_run(rid, artifacts_root=root)
    assert meta["steps"]["verdict"] == "done"
    assert meta["finalized_at"]


def test_finalize_val_full_flow(root):
    rid = _open_val_run(root)
    _fill_val_steps(root, rid)
    meta = finalize_run(
        rid, verdict_ref={"table": "c1_backtest.node_verdict", "run_id": rid},
        linked_artifacts=["../bt-8607ffc2.json"], artifacts_root=root)
    assert meta["verdict_ref"]["table"] == "c1_backtest.node_verdict"
    assert meta["linked_artifacts"] == ["../bt-8607ffc2.json"]


# ── load_meta / iter_run_ids ─────────────────────────────────────────────

def test_load_meta_missing_raises(root):
    with pytest.raises(RunArchiveError):
        load_meta("VAL-20260912-000009", artifacts_root=root)


def test_iter_run_ids_sorted_and_valid(root):
    assert iter_run_ids(artifacts_root=root) == []
    _open_val_run(root, "VAL-20260912-000000")
    _open_val_run(root, "SCR-20260912-010000", object_id="BT-P0-002")
    (root / "junk-dir").mkdir()
    assert iter_run_ids(artifacts_root=root) == ["SCR-20260912-010000", "VAL-20260912-000000"]


def test_meta_json_roundtrip_unicode(root):
    rid = _open_val_run(root)
    write_step(rid, "verdict", "# 判定书：滑点均值 12bp，分状态有效", artifacts_root=root)
    raw = (root / rid / "verdict.md").read_text(encoding="utf-8")
    assert "滑点均值" in raw
    meta = json.loads((root / rid / "meta.json").read_text(encoding="utf-8"))
    assert meta["kind"] == "VAL"
