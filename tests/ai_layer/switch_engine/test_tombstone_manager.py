"""S5 tombstone_manager 验收测试：封存全链/必填 fail-closed/复活工单/退役件可查询。

零生产写：git 走注入 runner（记录调用不触真仓），工单落 tmp_path。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from zephyr.ai_layer.switch_engine.tombstone_manager import (
    GIT_TAG_PREFIX,
    REVIVAL_ROUTE,
    list_tombstones,
    revival_ticket,
    seal,
)
from zephyr.intelligence.switch_engine.switch_engine import (
    SwitchTransitionError,
    SwitchEngine,
)
from zephyr.intelligence.switch_engine.switch_registry import SwitchRegistryStore


@pytest.fixture()
def git_calls() -> list[list[str]]:
    return []


@pytest.fixture()
def fake_git(git_calls: list[list[str]]):
    """本地别名夹具：等价 conftest.fake_git（保留显式签名便于单文件运行）。"""
    def runner(args: Any) -> str:
        git_calls.append([str(a) for a in args])
        return ""

    return runner


def test_seal_full_chain(
    store: SwitchRegistryStore,
    engine: SwitchEngine,
    retired_switch: str,
    fake_git,
    git_calls: list[list[str]],
) -> None:
    record = seal(
        engine,
        retired_switch,
        failed_regime="低波动率 regime",
        revival_conditions=["regime_recurrence: 高波动重现", "owner_manual"],
        seal_ref="seal-card-1",
        ttl_windows=2,
        git_runner=fake_git,
    )
    assert record.state == "tombstone"
    # git tag 封存（物理文件零删除；tag 永不清——无任何 untag 调用）
    assert git_calls and git_calls[0][0] == "tag"
    assert git_calls[0][1].startswith(f"{GIT_TAG_PREFIX}zephyr.demo.module/")
    tombstone = record.tombstone
    assert tombstone["failed_regime"] == "低波动率 regime"
    assert tombstone["revival_conditions"]  # 复活条件字段非空（验收锚 S5）
    assert tombstone["sealed_at"].endswith("+00:00")
    assert tombstone["ttl_deadline"].endswith("+00:00")
    assert tombstone["seal_ref"] == "seal-card-1"
    assert tombstone["seal_tag"].startswith(GIT_TAG_PREFIX)


def test_seal_missing_regime_rejected(
    engine: SwitchEngine, retired_switch: str, fake_git
) -> None:
    with pytest.raises(ValueError, match="failed_regime"):
        seal(
            engine,
            retired_switch,
            failed_regime="",
            revival_conditions=["owner_manual"],
            seal_ref="s",
            git_runner=fake_git,
        )


def test_seal_missing_conditions_rejected(
    engine: SwitchEngine, retired_switch: str, fake_git
) -> None:
    with pytest.raises(ValueError, match="revival_conditions"):
        seal(
            engine,
            retired_switch,
            failed_regime="regime-x",
            revival_conditions=[],
            seal_ref="s",
            git_runner=fake_git,
        )


def test_seal_wrong_state_rejected_before_tag(
    engine: SwitchEngine, make_record, fake_git, git_calls: list[list[str]]
) -> None:
    switch_id = "SW-shadow-no-seal"
    engine.open_switch(make_record(switch_id))  # shadow 态不可封
    with pytest.raises(SwitchTransitionError, match="retired"):
        seal(
            engine,
            switch_id,
            failed_regime="r",
            revival_conditions=["owner_manual"],
            seal_ref="s",
            git_runner=fake_git,
        )
    assert git_calls == []  # 校验前置：拒绝时不落 tag（不落半态）


def test_revival_ticket_route_is_shadow_recheck(
    store: SwitchRegistryStore,
    engine: SwitchEngine,
    retired_switch: str,
    fake_git,
    tmp_path: Path,
) -> None:
    seal(
        engine,
        retired_switch,
        failed_regime="regime-x",
        revival_conditions=["owner_manual"],
        seal_ref="s",
        git_runner=fake_git,
    )
    ticket = revival_ticket(
        store,
        retired_switch,
        trigger="regime_recurrence",
        evidence_ref="L1-signal-42",
        out_dir=tmp_path,
    )
    assert ticket["route"] == REVIVAL_ROUTE  # 复活≠直提：恒回 shadow 重走对比
    assert ticket["revival_not_direct_promotion"] is True
    files = list(tmp_path.glob("REV-*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))["ticket_id"] == ticket["ticket_id"]


def test_revival_invalid_trigger_rejected(
    store: SwitchRegistryStore, engine: SwitchEngine, retired_switch: str, fake_git, tmp_path: Path
) -> None:
    seal(
        engine, retired_switch,
        failed_regime="r", revival_conditions=["c"], seal_ref="s", git_runner=fake_git,
    )
    with pytest.raises(ValueError, match="非法复活触发器"):
        revival_ticket(store, retired_switch, trigger="lottery", evidence_ref="e", out_dir=tmp_path)


def test_list_tombstones_queryable(
    store: SwitchRegistryStore,
    engine: SwitchEngine,
    retired_switch: str,
    fake_git,
) -> None:
    """验收锚 S5：退役件可查询。"""
    before = list_tombstones(store)
    assert before == []
    seal(
        engine, retired_switch,
        failed_regime="r", revival_conditions=["c"], seal_ref="s", git_runner=fake_git,
    )
    tombstones = list_tombstones(store)
    assert [record.switch_id for record in tombstones] == [retired_switch]
