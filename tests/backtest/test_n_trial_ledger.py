"""N 试次账本（MOD-BT-200）单元测试——零 CH/零网络，假 conn + tmp_path 注入。

覆盖面：
- 口径合成：count = screen_runs + batch_records；manual_population 只入 known_floor 不入 count
- 幂等：record_run 同 batch_id 跳过；sync 重复执行不重复计
- fail-closed：账本缺失抛错；假 conn 读数缺失（空行）不阻断但读数为 0 口径自洽
- CAS：并发写冲突退避后成功（monkeypatch safe_write_text 前两次抛错）
- 骨架初始化：create_if_missing 落盘可读
- n_eff 预留位：恒 None（批次 B 落地前）
"""

from __future__ import annotations

import json

import pytest
import yaml

from zephyr.backtest.core.n_trial_ledger import (
    LEDGER_REGISTRY_PATH,
    REGISTRY_SKELETON,
    TrialLedger,
    TrialLedgerError,
)


class FakeCHConn:
    """假 ClickHouse 连接：execute(sql) -> rows，只认台账 group-by 查询。"""

    def __init__(self, rows: list[tuple]) -> None:
        self.rows = rows
        self.calls: list[str] = []

    def execute(self, sql: str):  # noqa: ANN001
        self.calls.append(sql)
        return self.rows


@pytest.fixture()
def ledger(tmp_path):
    return TrialLedger(registry_path=tmp_path / "trial_ledger_registry.yaml")


def test_missing_ledger_fail_closed(ledger):
    with pytest.raises(TrialLedgerError):
        ledger.cumulative_trials()


def test_skeleton_init_and_zero_count(ledger):
    data = ledger.load_registry(create_if_missing=True)
    assert data["screen_runs"]["total_trials"] == 0
    assert ledger.cumulative_trials() == 0
    assert LEDGER_REGISTRY_PATH.name == "trial_ledger_registry.yaml"


def test_record_run_and_snapshot(ledger):
    ledger.load_registry(create_if_missing=True)
    out = ledger.record_run("factory_grid_batch_a", "grid_x", 1999, note="manifest")
    assert out["status"] == "recorded"
    assert out["cumulative_trials"] == 1999
    snap = ledger.snapshot()
    assert snap.ledger_trials == 1999
    assert snap.breakdown == {"screen_runs": 0, "batch:grid_x": 1999}
    assert snap.manual_population == 0
    assert snap.known_floor == snap.ledger_trials
    assert snap.n_trials_raw == 1999
    assert snap.n_trials_effective is None  # 预注册：批次 B 落地前恒 None


def test_record_run_idempotent(ledger):
    ledger.load_registry(create_if_missing=True)
    ledger.record_run("manual", "B-1", 100)
    out = ledger.record_run("manual", "B-1", 100)
    assert out["status"] == "exists"
    assert ledger.cumulative_trials() == 100


def test_record_run_validation(ledger):
    ledger.load_registry(create_if_missing=True)
    with pytest.raises(ValueError):
        ledger.record_run("manual", "", 10)
    with pytest.raises(ValueError):
        ledger.record_run("manual", "B", -1)


def test_manual_population_not_in_count(ledger):
    ledger.load_registry(create_if_missing=True)
    ledger._cas_update(lambda d: d.update(manual_population=500) or "set manual")  # noqa: SLF001
    assert ledger.cumulative_trials() == 0
    snap = ledger.snapshot()
    assert snap.manual_population == 500
    assert snap.known_floor == 500
    assert snap.n_trials_raw == 0


def test_sync_screen_counts_with_fake_conn(ledger, tmp_path):
    conn = FakeCHConn([("SCR-a", 32), ("SCR-b", 5)])
    out = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out["screen_runs"] == 37
    assert out["screen_batches"] == 2
    assert out["cumulative_trials"] == 37
    # 计数边界（2026-09-15 裁定）：只算 is_sharpe 非空证据行（机器回测成绩），
    # deferred_c4 挂起行等零成绩行不入 N——同步 SQL 必须带证据行过滤。
    assert "is_sharpe IS NOT NULL" in conn.calls[0]
    data = ledger.load_registry()
    assert data["screen_runs"]["last_synced_by"] == "st-test"
    assert data["screen_runs"]["last_synced_at"]


def test_sync_discovers_grid_summaries(ledger, tmp_path):
    g = tmp_path / "grid_20260915-052749"
    g.mkdir(parents=True)
    (g / "summary.json").write_text(
        json.dumps({"n_raw": 362880, "n_sampled": 2000, "evaluated": 1999}),
        encoding="utf-8",
    )
    conn = FakeCHConn([])
    out = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out["grid_added"] == ["grid_20260915-052749"]
    assert out["cumulative_trials"] == 1999  # evaluated 优先（实跑数=可审计）
    # 幂等：重复 sync 不重复计
    out2 = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out2["grid_added"] == []
    assert out2["cumulative_trials"] == 1999


def test_sync_grid_falls_back_to_n_sampled(ledger, tmp_path):
    g = tmp_path / "grid_x"
    g.mkdir()
    (g / "summary.json").write_text(json.dumps({"n_sampled": 500}), encoding="utf-8")
    out = ledger.sync_screen_counts(FakeCHConn([]), grid_root=tmp_path)
    assert out["cumulative_trials"] == 500


def test_sync_skips_broken_summary(ledger, tmp_path):
    g = tmp_path / "grid_bad"
    g.mkdir()
    (g / "summary.json").write_text("{not json", encoding="utf-8")
    out = ledger.sync_screen_counts(FakeCHConn([]), grid_root=tmp_path)
    assert out["grid_added"] == []
    assert out["cumulative_trials"] == 0


def test_cas_retry_on_conflict(ledger, tmp_path, monkeypatch):
    """前两次 safe_write_text 抛冲突，第三次成功——立即重试（无 sleep）生效。"""
    from zephyr.backtest.core import n_trial_ledger as mod

    ledger.load_registry(create_if_missing=True)
    calls = {"n": 0}
    real = mod.safe_write_text

    def flaky(path, content, **kw):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError("simulated concurrent writer")
        return real(path, content, **kw)

    monkeypatch.setattr(mod, "safe_write_text", flaky)
    out = ledger.record_run("manual", "B-cas", 42)
    assert out["status"] == "recorded"
    assert calls["n"] == 3
    assert ledger.cumulative_trials() == 42


def test_yaml_structure_valid(ledger):
    ledger.load_registry(create_if_missing=True)
    data = yaml.safe_load(ledger._path.read_text(encoding="utf-8"))  # noqa: SLF001
    for key in REGISTRY_SKELETON:
        assert key in data
