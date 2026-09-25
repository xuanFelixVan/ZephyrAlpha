# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_order_daemon
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_order_daemon — C4 验收：§2.1 映射表全字段/必填机检 held_incomplete/criteria_hash 机检
拒派/单例锁让位与僵尸接管/offset 断点续读/堵点本 append；全部 tmp_path 注入零生产路径。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

from zephyr.ai_layer.scheduling.order_daemon import (
    LOCK_TTL_SECONDS,
    OrderDaemon,
    OrderDaemonError,
    build_task_order,
    check_criteria_hash,
    missing_required_fields,
    next_order_id,
    append_bottleneck,
)
from zephyr.ai_layer.scheduling.scheduling_events import KIND_EVOLUTION_WINNER_DUE


@pytest.fixture()
def evidence() -> dict[str, Any]:
    return {
        "verdict": "win",
        "domain_id": "governance",
        "evidence_ref": "EX-20260923-demo#verdict",
        "experiment_id": "EX-20260923-demo",
        "criteria_hash": "a" * 64,
        "significance": "0.25",
        "title": "治理闸加快照缓存",
        "labor_killed": "人工盯门闸;人工排优先级",
        "card_id": "card-1",
        "champion_ref": "src/zephyr/governance/foo.py",
        "compute_class": "local",
    }


@pytest.fixture()
def daemon(journal: Any, policy: dict[str, Any], tmp_path: Path) -> OrderDaemon:
    return OrderDaemon(
        journal,
        policy,
        ledger_path=tmp_path / "ledger.jsonl",
        lock_dir=tmp_path / "locks",
        sink=lambda order: {"inserted": order["order_id"]},
    )


# ---------------------------------------------------------------------------
# 纯函数件
# ---------------------------------------------------------------------------

def test_next_order_id_format() -> None:
    assert next_order_id("20260923", 7) == "WO-20260923-007"


def test_build_task_order_full_mapping(evidence: dict[str, Any], policy: dict[str, Any]) -> None:
    """§2.1 字段映射表逐行断言。"""
    order = build_task_order(evidence, policy, 1, "20260923", pre_rulings=[{"id": "R-1"}], owner_gate=False)
    assert order["schema_version"] == "0.1"
    assert order["order_id"] == "WO-20260923-001"
    assert order["title"] == "治理闸加快照缓存"
    assert order["contractor"] == {"session": "", "model_tier": "pending_dispatch", "lane": "B4"}
    assert "利弊对照" in order["objective"]
    assert order["definition_of_done"]["criteria_ref"] == f"EX-20260923-demo#{'a' * 64}"
    assert "work_order_id" in order["definition_of_done"]["l6_receipt_fields"]  # L6 回执预登记
    assert "老组不动" in order["red_lines"]["champion_freeze"]
    assert order["budget"]["compute_class"] == "local"
    assert order["budget"]["subagent_quota"] == policy["quota"]["q2_subagent_max"]
    assert order["pre_rulings"] == [{"id": "R-1"}]
    assert order["acceptance"]["reviewer"]["model_tier"] == "strong"  # 恒 strong 不可降
    assert order["acceptance"]["owner_gate"] is False
    assert "worktree abort" in order["rollback"]["plan"]
    assert "附录 C" in order["constitution_discipline"]["discipline"]
    assert order["honesty_clause"]["clause"]
    assert order["starred"] is False


def test_build_task_order_starred_and_missing_evidence(evidence: dict[str, Any], policy: dict[str, Any]) -> None:
    starred = dict(evidence, verdict="win_starred", title="", mechanism="缓存机制一句话")
    order = build_task_order(starred, policy, 2, "20260923")
    assert order["starred"] is True
    assert order["title"] == "缓存机制一句话"  # experiment 卡 mechanism 兜底
    with pytest.raises(OrderDaemonError, match="evidence_missing_keys"):
        build_task_order({"verdict": "win"}, policy, 1, "20260923")  # 缺 domain_id/evidence_ref


def test_missing_required_fields_enumeration(evidence: dict[str, Any], policy: dict[str, Any]) -> None:
    order = build_task_order(evidence, policy, 1, "20260923")
    assert missing_required_fields(order) == []
    hollow = {"order_id": "", "title": "t", "objective": "o", "domain_id": "d",
              "definition_of_done": {}, "red_lines": {}, "budget": {}, "acceptance": {}}
    missing = missing_required_fields(hollow)
    assert "order_id" in missing and "definition_of_done.criteria_ref" in missing


def test_check_criteria_hash_paths() -> None:
    h = "b" * 64
    assert check_criteria_hash(f"EX-1#{h}", h) == (True, "ok")
    assert check_criteria_hash(f"EX-1#{h}", "c" * 64)[0] is False  # 不匹配=拒派
    assert check_criteria_hash(f"EX-1#{h}", "")[1] == "frozen_hash_absent"
    assert check_criteria_hash("EX-1", h)[1] == "criteria_ref_missing_hash"
    assert check_criteria_hash("EX-1#", h)[1] == "criteria_hash_missing"


def test_append_bottleneck_schema(tmp_path: Path) -> None:
    ledger = tmp_path / "bl" / "ledger.jsonl"
    append_bottleneck(ledger, {"ts": "t", "kind": "held_incomplete", "order_id": "WO-1", "reason": "r", "protocol": "专人专事"})
    line = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert line["kind"] == "held_incomplete" and line["protocol"].startswith("专人专事")


# ---------------------------------------------------------------------------
# 守护消费闭环（journal 唯一真源）
# ---------------------------------------------------------------------------

def test_handle_winner_builds_pending_and_sinks(daemon: OrderDaemon, evidence: dict[str, Any]) -> None:
    result = daemon.handle_winner(evidence)
    assert result["state"] == "pending" and result["missing"] == []
    assert result["order_id"].startswith("WO-")


def test_handle_winner_incomplete_goes_held_with_bottleneck(
    journal: Any, policy: dict[str, Any], tmp_path: Path, evidence: dict[str, Any]
) -> None:
    ledger = tmp_path / "ledger.jsonl"
    daemon = OrderDaemon(journal, policy, ledger_path=ledger, lock_dir=tmp_path / "locks")
    bad = dict(evidence, title="", labor_killed="")  # title 空→必填缺失
    result = daemon.handle_winner(bad)
    assert result["state"] == "held_incomplete"
    assert any("title" in m for m in result["missing"])
    line = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert line["kind"] == "held_incomplete"  # 堵点本事件（禁静默降级）


def test_process_once_consumes_winner_event(daemon: OrderDaemon, journal: Any, evidence: dict[str, Any]) -> None:
    journal.emit(KIND_EVOLUTION_WINNER_DUE, evidence)
    receipt = daemon.process_once()
    assert not receipt.get("yielded")
    assert receipt["processed"] and receipt["processed"][0]["kind"] == KIND_EVOLUTION_WINNER_DUE
    assert receipt["pending_left"] == 0
    assert receipt["read_offset"] >= 0  # 断点检查点已写


def test_process_once_yields_when_lock_held(daemon: OrderDaemon) -> None:
    daemon.lock_path.parent.mkdir(parents=True, exist_ok=True)
    daemon.lock_path.write_text(json.dumps({"pid": os.getpid(), "ts": time.monotonic()}), encoding="utf-8")
    receipt = daemon.process_once()
    assert receipt == {"yielded": True, "reason": "singleton_lock_held"}  # 让位不抢


def test_process_once_takes_over_stale_lock(daemon: OrderDaemon) -> None:
    """僵尸锁（PID 不存在或超 TTL 600s）→ 接管（belt 机械照用）。"""
    daemon.lock_path.parent.mkdir(parents=True, exist_ok=True)
    daemon.lock_path.write_text(
        json.dumps({"pid": 999999, "ts": time.monotonic() - LOCK_TTL_SECONDS - 1}), encoding="utf-8"
    )
    receipt = daemon.process_once()
    assert receipt.get("yielded") is not True


def test_offset_checkpoint_rolls_back_on_truncation(daemon: OrderDaemon) -> None:
    daemon.offset_path.parent.mkdir(parents=True, exist_ok=True)
    daemon.offset_path.write_text(json.dumps({"offset": 10**9, "ts": "x"}), encoding="utf-8")
    size = daemon._checkpoint_offset()  # journal 不存在/更小→回卷为 0 并如实记录
    assert size == 0
    assert json.loads(daemon.offset_path.read_text(encoding="utf-8"))["offset"] == 0
