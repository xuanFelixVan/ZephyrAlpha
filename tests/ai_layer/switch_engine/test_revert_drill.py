"""S7 revert_drill 验收测试：round-robin 抽样/三查/100% 判据/报告含耗时/超窗告警。"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

from zephyr.ai_layer.switch_engine.revert_drill import (
    is_drill_stale,
    run_drill,
    select_targets,
)
from zephyr.intelligence.switch_engine.switch_engine import SwitchEngine
from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)


@pytest.fixture()
def ok_git():
    def runner(args: Sequence[str]) -> str:
        return "ref"

    return runner


@pytest.fixture()
def fail_git():
    def runner(args: Sequence[str]) -> str:
        raise RuntimeError("git rev-parse 失败：ref 不存在")

    return runner


def make_champions(make_record, engine: SwitchEngine, refs: list[str]) -> list[str]:
    ids: list[str] = []
    for index, ref in enumerate(refs):
        switch_id = f"SW-champ-{index}"
        engine.open_switch(
            make_record(
                switch_id,
                object_ref=f"obj-{index}",
                champion_ref=ref,
                challenger_ref=f"next-{index}",
            )
        )
        engine.transition(switch_id, "graduate", "g")
        engine.promote(switch_id, approved_by="auto", receipt_ref=f"r-{index}")
        engine.transition(switch_id, "stabilize", "s")
        ids.append(switch_id)
    return ids


def _patch_promoted_at(store: SwitchRegistryStore, switch_id: str, promoted_at: str) -> None:
    record = store.require(switch_id)
    store.update_state(
        switch_id,
        record.state,
        "patch-promoted-at",
        patches={"promotion_record": {**record.promotion_record,
                                      "promoted_at": promoted_at}},
    )


def test_select_targets_roundrobin_and_recency(store, engine, make_record) -> None:
    """champion 优先最近 promote+round-robin 确定性（同月序同结果）。"""
    ids = make_champions(make_record, engine, ["main", "v1", "v2"])
    for index, switch_id in enumerate(ids):
        _patch_promoted_at(store, switch_id, f"2026-0{9 - index}-01T00:00:00+00:00")
    champions = [store.require(sid) for sid in ids]
    first = select_targets(champions, [], month_index=0)
    assert first["champion"].champion_ref == "main"  # 最近 promote 优先
    second = select_targets(champions, [], month_index=1)
    assert second["champion"].champion_ref == "v1"
    again = select_targets(champions, [], month_index=0)
    assert again["champion"].switch_id == first["champion"].switch_id  # 确定性
    assert select_targets([], [], month_index=0)["champion"] is None


def test_drill_promoted_all_green(
    store, engine, make_record, ok_git, tmp_path: Path
) -> None:
    switch_ids = make_champions(make_record, engine, ["main"])
    report = run_drill(store, engine, switch_ids[0], out_dir=tmp_path, git_runner=ok_git)
    assert report["success"] is True
    assert report["incident_flag"] is False
    assert isinstance(report["elapsed_ms"], int)  # 含耗时（验收锚 S7）
    assert {check["name"] for check in report["checks"]} == {
        "revert_plan_executable", "champion_snapshot_rebuildable", "receipt_chain_complete",
    }
    assert all(check["passed"] for check in report["checks"])
    files = list(tmp_path.glob("drill_*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))["switch_id"] == switch_ids[0]


def test_drill_snapshot_failure_incident(
    store, engine, make_record, fail_git, tmp_path: Path
) -> None:
    """②快照不可重建 → 该查失败 → 100% 判据破 → incident_flag 立案。"""
    switch_ids = make_champions(make_record, engine, ["main"])
    report = run_drill(store, engine, switch_ids[0], out_dir=tmp_path, git_runner=fail_git)
    assert report["success"] is False
    assert report["incident_flag"] is True  # 任一失败=事故立案（假安全带教训）


def test_drill_tombstone_recovery_branch(
    store, engine, make_record, ok_git, fake_git, tmp_path: Path
) -> None:
    from zephyr.ai_layer.switch_engine.tombstone_manager import seal

    switch_id = "SW-20260923-retired"
    engine.open_switch(make_record(switch_id, champion_ref="tagged-ref"))
    engine.transition(switch_id, "graduate", "g")
    engine.promote(switch_id, approved_by="auto", receipt_ref="r")
    engine.transition(switch_id, "stabilize", "s")
    engine.transition(switch_id, "supersede", "next")
    seal(
        engine, switch_id,
        failed_regime="r", revival_conditions=["c"], seal_ref="s", git_runner=fake_git,
    )
    report = run_drill(store, engine, switch_id, out_dir=tmp_path, git_runner=ok_git)
    revert_check = report["checks"][0]
    assert revert_check["passed"] is True  # tombstone 复活分支 revive→shadow 可达
    assert report["state"] == "tombstone"


def test_drill_receipt_chain_broken(store, engine, make_record, ok_git, tmp_path: Path) -> None:
    """③回执链断链（history 缺 since/evidence_ref，直接落库模拟篡改）→ 查不过。"""
    switch_id = "SW-broken-chain"
    store.create(make_record(switch_id))
    store.connection().execute(
        "UPDATE switch_registry SET state_history=? WHERE switch_id=?",
        (json.dumps([{"state": "shadow", "since": ""}]), switch_id),  # 篡改：缺 since/evidence
    )
    store.connection().commit()
    report = run_drill(store, engine, switch_id, out_dir=tmp_path, git_runner=ok_git)
    chain = report["checks"][2]
    assert chain["name"] == "receipt_chain_complete"
    assert chain["passed"] is False
    assert report["incident_flag"] is True


def test_stale_drill_alert(store, make_record, engine) -> None:
    switch_id = "SW-stale"
    engine.open_switch(make_record(switch_id))
    assert is_drill_stale(store.require(switch_id)) is True  # 从未演练=恒告警
    store.update_state(
        switch_id, "shadow", "patch",
        patches={"rollback": {"last_drill_date": "2020-01-01T00:00:00+00:00"}},
    )
    assert is_drill_stale(store.require(switch_id)) is True  # 超 2 月度窗
    today = store.require(switch_id)  # 近期演练=不告警
    store.update_state(
        switch_id, today.state, "patch2",
        patches={"rollback": {"last_drill_date": store.require(switch_id).updated_at}},
    )
    assert is_drill_stale(store.require(switch_id)) is False
