# [BLUEPRINT] MOD-BT-213 | docs/_working/decision_map_campaign/links/L04_stock_wire/SKEL.md §3（LK-04 通电，接线先例=daily_gate_snapshot environment_switch 采集点）
# [MODULE] tests.strategy_pipeline.test_daily_gate_snapshot_pool
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.daily_gate_snapshot; zephyr.signal_ashare.core.candidate_pool_snapshot
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 测试隔离：零生产路径写入（侧带落表经 ch_writer.write_result monkeypatch
#   捕获/拒绝，候选来源注册 save/restore）——宪法 §9.6；五层门快照契约回归位（pool 为
#   附加键，absent_layers 不受侧带影响）；
#   覆盖=通电三态（empty 零触达/ok 捕获行/absent fail-open）+collect_gate_snapshot
#   全链 pool 键透传+契约不破
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-213 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] test-daily-gate-snapshot-pool-l04c02-20260925
"""daily_gate_snapshot LK-04 通电侧带单测（L04-C02 最小侵入接线验收）。

三分支（施工验收口径）：
    ①empty：无注册候选来源 → status=empty 零行零落表触达（fail-visible 在生产者侧）
    ②ok：注册 fake 来源 → 候选池落表通道捕获快照行（五层门 JSON 附加键透传）
    ③absent：生产者异常 → fail-open 折 absent，五层门快照不炸（缺席语义同款）
"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.core import candidate_pool_snapshot as cps
from zephyr.strategy_pipeline import daily_gate_snapshot as snap

D = "2026-09-15"  # 数据日（格式合法即可，全部走注入，零生产读取）

_REGIME_ROWS = [("VAL-P0-TEST", D, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "r3", 0.9, 0.75, 0.8, 0.9, "{}")]


class _RouteReader:
    """注入式只读通道：regime SQL 返回可编排行，其余表返回空（零生产路径）。"""

    def __call__(self, sql: str) -> list[tuple]:
        if "regime_snapshot_history" in sql:
            return list(_REGIME_ROWS)
        return []


class _FakeSource:
    """fake 候选来源（单标的构造束，零生产数据）。"""

    def fetch_bundles(self, day: str) -> cps.PoolBundles:
        from zephyr.signal_ashare.core.candidate_pool_aggregator import PoolCandidateInput

        return cps.PoolBundles(
            dual_pool_candidates=(
                PoolCandidateInput(symbol="600001", sleeve="short_term", rank_score=3.2, source_rank=1),
            ),
        )


@pytest.fixture(autouse=True)
def _isolate():
    """注册表 save/restore + ch_writer 落表拒绝位（双保险零生产写入）。"""
    import zephyr.data.ch_writer as ch_writer_mod

    saved_sources = cps.registered_bundle_sources()
    saved_write_result = ch_writer_mod.write_result
    cps.clear_bundle_sources()
    ch_writer_mod.write_result = lambda result, **kw: (_ for _ in ()).throw(
        AssertionError("测试禁触生产落表通道（未显式改写捕获位）")
    )
    yield
    ch_writer_mod.write_result = saved_write_result
    cps.clear_bundle_sources()
    for src in saved_sources:
        cps.register_pool_bundle_source(src)


# ── ① empty：无注册来源（空池日零触达）──────────────────────────────────
def test_hook_empty_day_no_write_touch():
    r = snap._collect_candidate_pool(
        D, market_state="ignition", turnover_yi=12000.0, l3={"status": "ok", "switches": {"state": "ignition"}}
    )
    assert r["status"] == "empty"
    assert r["persisted"] is False and r["rows"] == 0


# ── ② ok：注册来源后落表通道捕获（生产链路形态）─────────────────────────
def test_hook_ok_day_captures_rows(monkeypatch):
    import zephyr.data.ch_writer as ch_writer_mod

    captured: list = []
    monkeypatch.setattr(ch_writer_mod, "write_result", lambda result, **kw: captured.append(result) or True)
    cps.register_pool_bundle_source(_FakeSource())
    r = snap._collect_candidate_pool(
        D, market_state="ignition", turnover_yi=12000.0, l3={"status": "ok", "switches": {"state": "ignition"}}
    )
    assert r["status"] == "ok" and r["persisted"] is True and r["rows"] == 1
    assert len(captured) == 1
    assert captured[0].table == "c1_market.stock_candidate_pool"
    row = dict(zip(captured[0].columns, captured[0].rows[0], strict=True))
    assert row["symbol"] == "600001" and row["trade_date"] == D


# ── ③ absent：生产者异常 fail-open ──────────────────────────────────────
def test_hook_producer_exception_folds_absent(monkeypatch):
    monkeypatch.setattr(cps, "run_pool_batch_for_day", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    r = snap._collect_candidate_pool(D)
    assert r["status"] == "absent" and r["error"] == "RuntimeError"
    assert r["sideband"] == "candidate_pool"


# ── 全链：collect_gate_snapshot pool 键透传 + 五层契约不破 ───────────────
def test_collect_gate_snapshot_carries_pool_key_contract_intact():
    gate = snap.collect_gate_snapshot(D, market_state="ignition", turnover_yi=12000.0, reader=_RouteReader())
    # 五层键+pool 附加键齐备；pool 不进 absent_layers（降级矩阵契约不变）
    assert {"l1", "l2", "l3", "l4", "l5", "pool", "absent_layers"} <= set(gate.keys())
    assert gate["pool"]["status"] == "empty"
    assert all(layer in ("L1", "L2", "L3", "L4", "L5") for layer in gate["absent_layers"])
    assert "pool" not in [layer for layer in gate["absent_layers"]]
    # 侧带快照元透传 L3 产物（来源标尺留痕）
    assert gate["l3"]["status"] == "ok"


def test_collect_gate_snapshot_sideband_crash_not_propagate(monkeypatch):
    """侧带炸裂不炸五层门快照（collect_gate_snapshot 层面 fail-open 回归位）。"""
    monkeypatch.setattr(cps, "run_pool_batch_for_day", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    gate = snap.collect_gate_snapshot(D, market_state="ignition", turnover_yi=12000.0, reader=_RouteReader())
    assert gate["pool"]["status"] == "absent"
    assert gate["l1"]["status"] == "ok"  # 五层采集不受侧带牵连
