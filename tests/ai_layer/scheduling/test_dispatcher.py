# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_scheduling
# [MODULE] tests.ai_layer.scheduling.test_dispatcher
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_dispatcher — C7 验收：两问打分全枚举/防饥饿/repair 不混队/四读数/降级梯度/
拉式问闸 exit3→deferred/老组双预检；gate 函数注入零网络零定时器。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from zephyr.ai_layer.scheduling.dispatcher import (
    ComputeGateUnavailable,
    QuotaReadings,
    advantage_bucket,
    ask_compute_gate,
    champion_overlap_precheck,
    count_labor_segments,
    degrade,
    evaluate_quota,
    rank_pending,
    work_order_score,
    _load_e0_module,
)

UTC = timezone.utc
NOW = datetime(2026, 9, 23, 12, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# 两问①消灭人工段数
# ---------------------------------------------------------------------------

def test_labor_segments_enumeration(policy: dict[str, Any]) -> None:
    assert count_labor_segments("") == 1  # 空串=1 段保守下限
    assert count_labor_segments("盯门闸") == 1
    assert count_labor_segments("盯门闸;排优先级") == 2
    assert count_labor_segments("盯门闸；排优先级、登记排班，写周报|收尾") == 4  # 5 段封顶到 4
    assert count_labor_segments("盯门闸;排优先级;登记;写周报;收尾") == 4  # 1-4 封顶
    assert count_labor_segments("a\nb\nc") == 3


# ---------------------------------------------------------------------------
# 两问②优势分桶（分桶线=policy 常量）
# ---------------------------------------------------------------------------

def test_advantage_bucket_lines(policy: dict[str, Any]) -> None:
    assert advantage_bucket(0.25, policy) == "large"
    assert advantage_bucket(0.20, policy) == "large"  # 恰好压线取高档
    assert advantage_bucket(0.15, policy) == "medium"
    assert advantage_bucket(0.10, policy) == "medium"
    assert advantage_bucket(0.05, policy) == "small"
    assert advantage_bucket(None, policy) == "small"  # 缺失保守，不虚构精度
    assert advantage_bucket("n/a", policy) == "small"


def test_score_formula(policy: dict[str, Any]) -> None:
    """score = labor_segments × advantage_bucket × demote（DESIGN §2.5 原式）。"""
    s = work_order_score("a;b", 0.25, False, policy)
    assert s["base"] == 4.0  # 2 段 × large 2.0
    s = work_order_score("a;b", 0.25, True, policy)
    assert s["base"] == 2.0  # 带星 ×0.5
    assert s["bump"] == 0.0


def test_score_starvation_bump(policy: dict[str, Any]) -> None:
    s = work_order_score("a", 0.05, False, policy, pending_age_days=7)
    assert s["bump"] == 0.0  # 恰 7 天未过线
    s = work_order_score("a", 0.05, False, policy, pending_age_days=7.5)
    assert s["bump"] == 1.0  # >7 天一次性 +1.0
    assert s["score"] == 2.0  # 1×1.0+1.0


def test_rank_pending_order_and_fifo(policy: dict[str, Any]) -> None:
    """score 降序→FIFO；带星同分排队尾；repair/骨架级不混队。"""
    mk = lambda oid, lk, sig, star=False, age=0, kind="evolution", og=False: {  # noqa: E731
        "order_id": oid, "labor_killed": lk, "significance": sig, "starred": star,
        "kind": kind, "owner_gate": og,
        "created_at": NOW - timedelta(days=age),
    }
    orders = [
        mk("WO-A", "a", 0.25),                       # 2.0
        mk("WO-B", "a", 0.25),                       # 2.0 FIFO 在后
        mk("WO-C", "a", 0.25, star=True),            # 1.0 带星
        mk("WO-D", "a", 0.05, age=8),                # 1.0+1.0 防饥饿
        mk("WO-R", "a", 0.99, kind="repair"),        # repair 不参排
        mk("WO-S", "a", 0.99, og=True),              # 骨架级只展示不占队
    ]
    ranked = rank_pending(orders, policy, NOW)
    ids = [r["order_id"] for r in ranked]
    assert "WO-R" not in ids and "WO-S" not in ids
    assert ids == ["WO-A", "WO-B", "WO-D", "WO-C"]  # 分>带星>防饥饿 bump 并列 FIFO


def test_rank_pending_rejects_naive_now(policy: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="naive"):
        rank_pending([], policy, datetime(2026, 9, 23))


# ---------------------------------------------------------------------------
# 配额四读数与降级梯度（§2.6）
# ---------------------------------------------------------------------------

def test_quota_all_green(policy: dict[str, Any]) -> None:
    r = QuotaReadings(q1_active_sessions=1, q2_subagents_requested=3, q3_tokens_today=100, q4_commit_queue_pending=0)
    assert evaluate_quota(r, policy) == []


def test_quota_each_limit(policy: dict[str, Any]) -> None:
    quota = policy["quota"]
    r = QuotaReadings(
        q1_active_sessions=int(quota["q1_active_session_cap"]),
        q2_subagents_requested=int(quota["q2_subagent_max"]) + 1,
        q3_tokens_today=int(quota["q3_daily_token_budget"]),
        q4_commit_queue_pending=int(quota["q4_commit_queue_pending_cap"]),
    )
    assert evaluate_quota(r, policy) == ["Q1", "Q2", "Q3", "Q4"]


def test_degrade_q1_defers_with_audit(policy: dict[str, Any]) -> None:
    out = degrade({"order_id": "WO-1", "state": "pending", "defer_count": 0}, ["Q1"], policy)
    assert out["state"] == "deferred" and out["defer_count"] == 1
    assert out["actions"][0]["detail"].startswith("并发槽满")


def test_degrade_q3_demotes_build_only(policy: dict[str, Any]) -> None:
    """Q3 降档仅限施工段；验收 reviewer 恒 strong 不可降。"""
    build = {"order_id": "WO-1", "state": "pending", "segment": "build", "contractor": {"model_tier": "strong"}}
    out = degrade(build, ["Q3"], policy)
    assert out["model_tier"] == policy["quota"]["q3_demote_tier_to"]
    accept = {"order_id": "WO-2", "state": "pending", "segment": "accept", "contractor": {"model_tier": "strong"}}
    out = degrade(accept, ["Q3"], policy)
    assert out["model_tier"] == "strong"  # 不降档
    assert out["state"] == "deferred"  # 转 deferred 至次日窗


def test_degrade_q4_pauses_without_state_change(policy: dict[str, Any]) -> None:
    out = degrade({"order_id": "WO-1", "state": "pending", "defer_count": 0}, ["Q4"], policy)
    assert out["state"] == "pending"  # 在途照常，仅暂停新派工
    assert out["actions"][0]["action"] == "pause_dispatch"


def test_degrade_three_defers_hits_critical(policy: dict[str, Any]) -> None:
    """同一工单连续 3 次 defer→堵点本 CRITICAL（对标 belt _ENV_ABORT_ESCALATE=3）。"""
    order = {"order_id": "WO-1", "state": "pending", "defer_count": 2}
    out = degrade(order, ["Q1"], policy)
    assert out["defer_count"] == 3 and out["critical"] is True


def test_degrade_gpu_reschedules(policy: dict[str, Any]) -> None:
    out = degrade({"order_id": "WO-1", "state": "dispatched", "defer_count": 0}, ["GPU"], policy)
    assert out["state"] == "deferred"
    assert out["actions"][0]["action"] == "reschedule_heavy_ok"


# ---------------------------------------------------------------------------
# T1 派工前置双预检
# ---------------------------------------------------------------------------

def test_champion_overlap_holds() -> None:
    ok, why = champion_overlap_precheck(["src/zephyr/gov/x.py"], ["src/zephyr/gov/x.py"])
    assert not ok and any("HELD-OVERLAP" in w for w in why)  # 不硬闯


def test_champion_active_session_holds() -> None:
    ok, why = champion_overlap_precheck(["src/zephyr/gov/x.py"], [], ["st-other"])
    assert not ok and any("在途会话" in w for w in why)


def test_champion_clean_passes() -> None:
    ok, why = champion_overlap_precheck(["src/zephyr/gov/x.py"], ["src/zephyr/other/y.py"], [])
    assert ok and why == []


# ---------------------------------------------------------------------------
# E0 拉式问闸（注入零网络；真模块按路径装载零改造）
# ---------------------------------------------------------------------------

def test_ask_compute_gate_allowed_and_denied() -> None:
    seen: dict[str, str] = {}

    def gate(purpose: str, node_compute_class: str) -> dict[str, Any]:
        seen["purpose"] = purpose
        seen["cls"] = node_compute_class
        return {"allowed": True, "reason_code": "gate_allow_light_always"}

    allowed = ask_compute_gate("WO-1", "local", gate_fn=gate)
    assert allowed == {"allowed": True, "reason_code": "gate_allow_light_always"}
    assert seen == {"purpose": "evolution_WO-1", "cls": "local"}  # 拉式问闸每段一次
    denied = ask_compute_gate(
        "WO-1", "local_gpu",
        gate_fn=lambda purpose, node_compute_class: {"allowed": False, "reason_code": "gate_deny_trading_hours"},
    )
    assert denied == {"allowed": False, "reason_code": "gate_deny_trading_hours"}  # exit 3 语义→deferred


def test_ask_compute_gate_error_is_fail_closed() -> None:
    def boom(purpose: str, node_compute_class: str) -> dict[str, Any]:
        raise RuntimeError("ch_unreachable")

    out = ask_compute_gate("WO-1", "local_gpu", gate_fn=boom)
    assert out["allowed"] is False and out["reason_code"].startswith("gate_error:")


def test_e0_module_loads_by_path() -> None:
    """真源 E0 闸按路径装载可达（exam_trigger_scheduler 同款先例；零改造调用）。"""
    module = _load_e0_module()
    assert callable(module.check_gate)
    with pytest.raises(ComputeGateUnavailable):
        # 不可达路径→fail-closed
        import zephyr.ai_layer.scheduling.dispatcher as dsp

        dsp._E0_MODULE_CACHE.clear()
        saved = dsp._E0_GATE_RELPATH
        try:
            dsp._E0_GATE_RELPATH = ("scripts", "backtest", "no_such_gate.py")
            dsp._load_e0_module()
        finally:
            dsp._E0_GATE_RELPATH = saved
            dsp._E0_MODULE_CACHE.clear()
