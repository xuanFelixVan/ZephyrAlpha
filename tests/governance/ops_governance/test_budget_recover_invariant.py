# [TTL] permanent
"""R12 聚合不变式单测 — BudgetEngine.recover_from_snapshot（r_table_rulings R12 真GAP-吸收）.

裁定真源（主区只读）：docs/_working/fullcirculation_campaign_20261008/
01_dtable_rulings/r_table_rulings.md R12 行——恢复快照各桶满足
INVARIANT-BUDGET-AGG-CONSISTENCY: 0 <= hourly <= daily*(1+1%)，
违反 fail-closed 抛 RuntimeError（携带快照版本与桶明细），禁止静默修正。

用例：
- 蓝：一致快照（真实 shutdown→recover 往返，含降级状态）原样恢复，不抛
- 红：hourly 超出 daily×(1+1%) → RuntimeError 带版本/桶明细拒绝
- 红：负数聚合（daily<0）→ 拒绝
- 蓝：1% tolerance 边界内漂移（0.5%）→ 放行
- 蓝：空 JSON 快照/快照文件缺失 → 按既有语义返回零消费全新引擎，不抛
"""

from __future__ import annotations

import json

import pytest

be = pytest.importorskip("zephyr.governance.ops_governance.budget_engine")
bm = pytest.importorskip("zephyr.governance.ops_governance.budget_models")

BudgetEngine = be.BudgetEngine
R12_AGG_TOLERANCE = be.R12_AGG_TOLERANCE
BudgetDimension = bm.BudgetDimension
BudgetLevel = bm.BudgetLevel


@pytest.fixture(autouse=True)
def _isolate_singleton():
    """单例隔离——不泄漏 BudgetEngine._instance 给同进程其他测试。"""
    BudgetEngine.reset_instance()
    yield
    BudgetEngine.reset_instance()


def _write_snapshot(tmp_path, payload: dict, name: str = "shutdown_snapshot.json") -> str:
    p = tmp_path / name
    p.write_text(json.dumps(payload), encoding="utf-8")
    return str(p)


def test_recover_round_trip_consistent_snapshot(tmp_path):
    """蓝：一致快照往返恢复原样（消费+降级级），不变式通过不抛。"""
    engine = BudgetEngine()
    ok, _, _ = engine.try_claim_budget("p-tok", BudgetDimension.TOKEN, 500.0)
    assert ok
    assert engine.commit_claim("p-tok", BudgetDimension.TOKEN, 500.0)
    ok, _, _ = engine.try_claim_budget("p-cost", BudgetDimension.COST, 2.0)
    assert ok
    assert engine.commit_claim("p-cost", BudgetDimension.COST, 1.5)
    assert engine.advance_degradation()
    assert engine.advance_degradation()

    consumption_before = engine.get_consumption_summary()
    snap_path = str(tmp_path / "persisted.json")
    result = engine.shutdown(persist_path=snap_path)
    assert result["persisted_to"] == snap_path

    recovered = BudgetEngine.recover_from_snapshot(snap_path)  # 不变式通过=不抛
    assert recovered.get_consumption_summary() == consumption_before
    assert recovered.active_step_idx == 2
    assert recovered.current_degradation_level is BudgetLevel.L2_THROTTLED


def test_recover_rejects_aggregate_inconsistent_snapshot(tmp_path):
    """红：聚合不一致快照 fail-closed 拒绝；蓝：1% tolerance 边界内放行。"""
    # 红：hourly=50 远超 daily=10×(1+1%) —— 拒绝且携带快照版本与桶明细
    p = _write_snapshot(
        tmp_path,
        {
            "consumption": {"BP-TOKEN-001": {"daily": 10.0, "hourly": 50.0}},
            "degradation_level": 0,
            "active_step_idx": 0,
            "hash": "snap-ver-abc123",
            "health": "HEALTHY",
        },
    )
    with pytest.raises(RuntimeError) as ei:
        BudgetEngine.recover_from_snapshot(p)
    msg = str(ei.value)
    assert "r_table_rulings R12" in msg
    assert "INVARIANT-BUDGET-AGG-CONSISTENCY" in msg
    assert "snap-ver-abc123" in msg  # 快照版本（hash）随错误携带
    assert "BP-TOKEN-001" in msg and "50.0" in msg  # 桶明细

    # 红：负数聚合=漂移（daily<0）—— 拒绝
    p2 = _write_snapshot(tmp_path, {"consumption": {"BP-COST-001": {"daily": -1.0, "hourly": 0.0}}}, name="neg.json")
    with pytest.raises(RuntimeError, match="BP-COST-001"):
        BudgetEngine.recover_from_snapshot(p2)

    # 蓝：0.5% 漂移在 1% tolerance 边界内 —— 放行不抛
    p3 = _write_snapshot(
        tmp_path, {"consumption": {"BP-TOKEN-001": {"daily": 100.0, "hourly": 100.5}}}, name="boundary.json"
    )
    recovered = BudgetEngine.recover_from_snapshot(p3)
    assert recovered.get_consumption_summary()["BP-TOKEN-001"]["hourly"] == pytest.approx(100.5)


def test_recover_empty_or_missing_snapshot_keeps_existing_semantics(tmp_path):
    """空快照按既有语义：零消费全新引擎返回，不因不变式抛错。"""
    p_empty = _write_snapshot(tmp_path, {})
    fresh = BudgetEngine.recover_from_snapshot(p_empty)
    assert all(c["daily"] == 0.0 and c["hourly"] == 0.0 for c in fresh.get_consumption_summary().values())
    assert fresh.active_step_idx == 0

    # 快照文件缺失：载入失败走既有 fail-open 语义（warning+全新引擎）
    missing = BudgetEngine.recover_from_snapshot(str(tmp_path / "no_such_snapshot.json"))
    assert all(c["daily"] == 0.0 for c in missing.get_consumption_summary().values())
    assert missing.active_step_idx == 0
