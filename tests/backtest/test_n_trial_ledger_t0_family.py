# [TESTS] zephyr.backtest.core.n_trial_ledger (T0 批次面)
# [DOMAIN] D_BACKTEST
# [TTL] permanent
"""N 试次账本 T0 做T族批次面单测（C216 补齐，2026-10-07）——零 CH/零网络，tmp_path 注入。

考古注：本件名承 2026-10-04 孤儿考古退役的未落地规格件（T0_BATCH_KIND 当时全史
零源码，见 .runtime/commit_queue/dead q-20261004-st-sK-orphanarch 死袋）；本件随
C216 补齐（T0_BATCH_KIND/_T0_ARTIFACT_ROOT/sync_t0_manifest_counts）落地转正。

覆盖面：
- T0_BATCH_KIND 闭合集：三族 kind 与 scripts/backtest/t0_*.py 产物一一对应
- 发现口径：t0_rule_manifest_{tag}.yaml batches_done.n_pairs_by_rule_period 求和
- 幂等：同批重同步不重复登记
- 单调：断点续跑 manifest 读数增长→前进；读数缩水→禁回退
- fail-closed：batches_done 条目缺 n_pairs_by_rule_period→该条目不计入（宁少计留痕）
- 半程 manifest（零完成批）不入账
"""

from __future__ import annotations

from pathlib import Path

import yaml

from zephyr.backtest.core.n_trial_ledger import T0_BATCH_KIND, TrialLedger


def _write_manifest(root: Path, tag: str, batches_done: dict) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"t0_rule_manifest_{tag}.yaml"
    manifest = {
        "tag": tag,
        "window": {"start": "2025-01-01", "end": "2025-06-30", "closed_book_cutoff": "2025-09-09"},
        "rules": ["r01"],
        "periods": ["1min", "5min"],
        "batches_done": batches_done,
        "pairs_files": {},
    }
    path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    return path


def _batch_entry(pairs: dict[str, int]) -> dict:
    return {"n_symbols": 10, "n_pairs_by_rule_period": pairs}


def test_t0_batch_kind_closed_set():
    """三族 kind 闭合集：值与 scripts/backtest/t0_*.py 产物对齐，防手滑新增漏登记。"""
    assert T0_BATCH_KIND == {
        "rule_engine": "t0_rule_engine",
        "material_line": "t0_material_line",
        "state_match_matrix": "t0_state_match_matrix",
    }


def test_sync_t0_discovers_manifest_pairs_sum(tmp_path):
    """发现口径：n_pairs_by_rule_period 全批求和=可审计机器回测往返数。"""
    root = tmp_path / "t0_rule_engine"
    _write_manifest(
        root,
        "demo_v1",
        {
            "0": _batch_entry({"r01_1min": 120, "r01_5min": 80}),
            "1": _batch_entry({"r01_1min": 200}),
        },
    )
    ledger = TrialLedger(registry_path=tmp_path / "ledger.yaml")
    out = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="st-mastertc-l7")
    assert out["t0_scanned"] == 1
    assert out["t0_added"] == ["t0_rule_demo_v1"]
    assert out["cumulative_trials"] == 400  # 120+80+200
    snap = ledger.snapshot()
    assert snap.breakdown.get("batch:t0_rule_demo_v1") == 400


def test_sync_t0_idempotent_then_monotonic(tmp_path):
    """幂等+单调：重同步同读数零变更；读数增长→前进；缩水→禁回退。"""
    root = tmp_path / "t0_rule_engine"
    manifest = _write_manifest(root, "grow_v1", {"0": _batch_entry({"r01_1min": 100})})
    ledger = TrialLedger(registry_path=tmp_path / "ledger.yaml")
    first = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert first["t0_added"] == ["t0_rule_grow_v1"]

    same = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert same["t0_added"] == [] and same["t0_updated"] == []
    assert same["cumulative_trials"] == 100

    # 断点续跑：批 1 完成，读数增长 → 单调前进
    _write_manifest(root, "grow_v1", {"0": _batch_entry({"r01_1min": 100}), "1": _batch_entry({"r01_1min": 60})})
    grown = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert grown["t0_updated"] == ["t0_rule_grow_v1"]
    assert grown["cumulative_trials"] == 160

    # 缩水（异常 manifest）→ 禁回退，账面仍 160
    _write_manifest(root, "grow_v1", {"0": _batch_entry({"r01_1min": 10})})
    shrunk = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert shrunk["t0_updated"] == [] and shrunk["t0_added"] == []
    assert shrunk["cumulative_trials"] == 160
    assert manifest.exists()  # 审计凭据仍在盘


def test_sync_t0_skips_entries_without_pairs_readout(tmp_path):
    """fail-closed 边界：条目缺 n_pairs_by_rule_period → 该条目不计入（宁少计留痕）。"""
    root = tmp_path / "t0_rule_engine"
    _write_manifest(
        root,
        "partial_v1",
        {
            "0": _batch_entry({"r01_1min": 50}),
            "1": {"n_symbols": 10},  # 缺读数
        },
    )
    ledger = TrialLedger(registry_path=tmp_path / "ledger.yaml")
    out = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert out["cumulative_trials"] == 50  # 只计可审计条目


def test_sync_t0_ignores_empty_and_unreadable_manifests(tmp_path):
    """半程 manifest（零完成批）与整件不可读件不入账，不阻断其他批次发现。"""
    root = tmp_path / "t0_rule_engine"
    _write_manifest(root, "empty_v1", {})
    (root / "t0_rule_manifest_broken_v1.yaml").write_text(":{ not yaml", encoding="utf-8")
    _write_manifest(root, "good_v1", {"0": _batch_entry({"r01_5min": 7})})
    ledger = TrialLedger(registry_path=tmp_path / "ledger.yaml")
    out = ledger.sync_t0_manifest_counts(artifact_root=root, synced_by="s")
    assert out["t0_scanned"] == 3
    assert out["t0_added"] == ["t0_rule_good_v1"]
    assert out["cumulative_trials"] == 7
