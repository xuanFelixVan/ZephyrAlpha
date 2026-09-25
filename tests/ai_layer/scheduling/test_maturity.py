# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_maturity
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_maturity — C5 验收：M1-M4 全枚举（单胜不开/胜率线/样本下限/draw 不计分母/超龄清零/
白名单缺席零开闸）+ policy fail-closed + 域聚合 SQL + held_maturity 转正留痕。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.ai_layer.scheduling.maturity import (
    SchedulingGateVerdict,
    SchedulingPolicyError,
    collect_region_stats,
    evaluate_region,
    load_gate_policy,
    promote_held_orders,
    region_aggregation_sql,
)

UTC = timezone.utc
NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=UTC)


def _stats(**over: Any) -> dict[str, Any]:
    base = {
        "win": 2,
        "loss": 1,
        "draw": 5,
        "latest_archived_at": NOW - timedelta(days=10),
        "whitelisted": True,
    }
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# policy 加载（fail-closed）
# ---------------------------------------------------------------------------

def test_load_real_policy(policy: dict[str, Any]) -> None:
    assert policy["policy_id"] == "schedule_gate_policy_v1"
    assert policy["maturity"]["m1_min_wins"] == 2
    assert policy["maturity"]["m2_min_win_rate"] == 0.60
    assert policy["maturity"]["m3_freshness_max_days"] == 90


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SchedulingPolicyError, match="缺文件"):
        load_gate_policy(tmp_path / "nope.yaml")


def test_load_missing_section_raises(tmp_path: Path) -> None:
    p = tmp_path / "p.yaml"
    p.write_text("policy_id: x\nmaturity: {}\n", encoding="utf-8")
    with pytest.raises(SchedulingPolicyError, match="缺节"):
        load_gate_policy(p)


def test_load_bad_maturity_keys_raises(tmp_path: Path) -> None:
    p = tmp_path / "p.yaml"
    body = {k: {} for k in ("policy_id", "priority", "quota", "compute_classes", "dispatch", "order_states")}
    body["maturity"] = {"m1_min_wins": 2}
    p.write_text(yaml.safe_dump(body), encoding="utf-8")
    with pytest.raises(SchedulingPolicyError, match="maturity 节残缺"):
        load_gate_policy(p)


# ---------------------------------------------------------------------------
# M1-M4 判定（纯函数全枚举）
# ---------------------------------------------------------------------------

def test_m1_single_win_does_not_open(policy: dict[str, Any]) -> None:
    v = evaluate_region(_stats(win=1, loss=0), policy, NOW, "governance")
    assert not v.passed and "M1" in v.failed_codes


def test_all_four_pass(policy: dict[str, Any]) -> None:
    v = evaluate_region(_stats(), policy, NOW, "governance")
    assert v.passed and v.failed_codes == []


def test_m2_win_rate_line(policy: dict[str, Any]) -> None:
    # 3 win / 2 loss = 60% 恰好过线；样本 5 ≥ 3
    v = evaluate_region(_stats(win=3, loss=2), policy, NOW)
    assert v.passed
    # 2 win / 2 loss = 50% < 60%（draw 不进分母）
    v = evaluate_region(_stats(win=2, loss=2), policy, NOW)
    assert not v.passed and "M2" in v.failed_codes
    assert v.details["samples"] == 4  # draw=5 不计分母


def test_m2_sample_floor(policy: dict[str, Any]) -> None:
    v = evaluate_region(_stats(win=2, loss=0), policy, NOW)  # N_total=2 < 3
    assert not v.passed and "M2" in v.failed_codes


def test_m3_stale_resets_counts(policy: dict[str, Any]) -> None:
    v = evaluate_region(_stats(latest_archived_at=NOW - timedelta(days=91)), policy, NOW)
    assert not v.passed and "M3" in v.failed_codes and "M1" in v.failed_codes  # 清零重攒
    assert v.details["win"] == 0


def test_m3_missing_archive_is_stale(policy: dict[str, Any]) -> None:
    v = evaluate_region(_stats(latest_archived_at=None), policy, NOW)
    assert not v.passed and "M3" in v.failed_codes


def test_naive_datetime_rejected(policy: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="naive"):
        evaluate_region(_stats(latest_archived_at=datetime(2026, 9, 1)), policy, NOW)


def test_m4_whitelist_absent_blocks(policy: dict[str, Any]) -> None:
    """冷启动诚实语义：白名单（Owner 区，本班置空）外区域永不开闸。"""
    v = evaluate_region(_stats(whitelisted=False), policy, NOW)
    assert not v.passed and "M4" in v.failed_codes
    # 真源 policy 白名单=空（L5-#2 待 Owner）：当前任何域都过不了 M4
    assert policy["maturity"]["m4_first_batch_whitelist"] == []


# ---------------------------------------------------------------------------
# 域聚合 SQL 与收集
# ---------------------------------------------------------------------------

def test_region_aggregation_sql_shape() -> None:
    sql = region_aggregation_sql("ai_compare")
    assert "ai_compare.ai_comparison_experiment" in sql
    assert "GROUP BY domain_id" in sql
    assert "status = 'archived'" in sql
    assert "win_starred" in sql  # win* 计入 win（policy 注记口径）


class FakeCursor:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def execute(self, _sql: str, _params: Any = None) -> None:
        pass

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows


class FakeConn:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._rows)


def test_collect_region_stats(policy: dict[str, Any]) -> None:
    fresh = datetime(2026, 9, 20, tzinfo=UTC)
    conn = FakeConn([("governance", 2, 1, 0, fresh)])
    wl = {"governance": True}
    stats = collect_region_stats(conn, "ai_compare", wl)
    assert stats["governance"]["win"] == 2
    verdict = evaluate_region(stats["governance"], policy, NOW, "governance")
    assert verdict.passed


def test_collect_rejects_naive_latest() -> None:
    conn = FakeConn([("governance", 2, 1, 0, datetime(2026, 9, 20))])
    with pytest.raises(ValueError, match="naive"):
        collect_region_stats(conn, "ai_compare")


# ---------------------------------------------------------------------------
# held_maturity 转正（事件唤醒重评，留痕）
# ---------------------------------------------------------------------------

def test_promote_held_orders(policy: dict[str, Any]) -> None:
    held = {
        "order_id": "WO-1",
        "domain_id": "governance",
        "state": "held_maturity",
        "audit_log": [],
    }
    untouched = {"order_id": "WO-2", "domain_id": "governance", "state": "pending", "audit_log": []}
    passed = SchedulingGateVerdict("governance", True, [], {})
    out = promote_held_orders([held, untouched], {"governance": passed}, "2026-09-23T00:00:00+00:00")
    assert out[0]["state"] == "pending"
    assert out[0]["audit_log"][0]["action"] == "held_maturity_promoted"  # 转正留痕
    assert out[1]["state"] == "pending"  # 原 pending 不动


def test_promote_requires_passing_verdict() -> None:
    held = {"order_id": "WO-1", "domain_id": "governance", "state": "held_maturity", "audit_log": []}
    failed = SchedulingGateVerdict("governance", False, ["M1"], {})
    out = promote_held_orders([held], {"governance": failed}, "ts")
    assert out[0]["state"] == "held_maturity"  # 不过线原地挂起
    out = promote_held_orders([held], {}, "ts")  # 缺域判据=不误转
    assert out[0]["state"] == "held_maturity"
