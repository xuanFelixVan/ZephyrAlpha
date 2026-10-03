# [BLUEPRINT] MOD-RPT-037 | 待统筹登记（54号 BM-REC-02-B 归因结果落库+查询，§3.5 两层归因持久化） | §test
# [MODULE] tests.reporting.test_attribution_result_store
# [DOMAIN] D_REPORTING
# [INVARIANTS] append-only仅INSERT(INSERT OR IGNORE同幂等键跳过保首条); SQL参数化+常量(NO-BARE-SQL); db_path默认None走DB_PATH SSoT(测试注入tmp库); DDL真源=reconciliation_schema.get_ddl(测试侧禁止复刻副本); 落库保原文字符串防浮点二次失真
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(输入非法fail-closed); sqlite3.Error透传
# [TESTS] self
# [A_test] module_id: MOD-RPT-037 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""归因结果落库/查询单元测试（54 号 BM-REC-02-B 残余：消费落库 DDL + 查询接口）。

覆盖：
- ensure_attribution_results_table：tmp 库幂等建表（DDL 真源=reconciliation_schema，
  测试侧零复刻），列契约含两层归因必备字段；
- store_attribution_report：firm/strategy 两层写入-查询闭环（float→repr 字符串
  保原文，回读 float() 精确往返）；幂等键 UNIQUE 同键重复=跳过保首条返同 id；
- persist_two_layer_attribution：求和不变量 PASS/FAIL 落 invariant_status（复用
  zephyr.reporting.attribution.validate_strategy_pnl_invariant 不重复实现），
  策略键集不一致 fail-closed；
- query_attribution_results：组合过滤/倒序/limit 截断；get_attribution_by_key 命中/未中；
- fail-closed：非法 layer / 非法 invariant_status / 空幂等键 / 非法 limit；
- 默认 db_path 走 DB_PATH SSoT（monkeypatch 模块常量指向 tmp，不触真 governance.db）。
全 tmp 隔离，不连生产库。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from zephyr.reporting import attribution_result_store as store
from zephyr.reporting.attribution_result_store import (
    ensure_attribution_results_table,
    get_attribution_by_key,
    persist_two_layer_attribution,
    query_attribution_results,
    store_attribution_report,
)
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)


def _report(
    portfolio_id: str = "PF-FIRM",
    key: str = "attr-20260821-firm",
    start: str = "2026-08-21",
    end: str = "2026-08-21",
    alloc: float = 0.002,
    sel: float = 0.03,
    inter: float = 0.006,
    drag: float = 0.001,
) -> PerformanceAttributionReport:
    total = alloc + sel + inter - drag
    return PerformanceAttributionReport(
        portfolio_id=portfolio_id,
        period_start=start,
        period_end=end,
        total_return=total,
        allocation_effect=alloc,
        selection_effect=sel,
        interaction_effect=inter,
        factor_contributions={},
        transaction_cost_drag=drag,
        idempotency_key=key,
    )


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """tmp 库 + 幂等建表（DDL 真源=reconciliation_schema，测试侧零复刻）。"""
    db = tmp_path / "governance.db"
    ensure_attribution_results_table(db)
    return db


class TestEnsureTable:
    def test_create_is_idempotent_and_has_columns(self, tmp_path: Path) -> None:
        db = tmp_path / "g.db"
        ensure_attribution_results_table(db)
        ensure_attribution_results_table(db)  # 二次执行幂等
        conn = sqlite3.connect(str(db))
        try:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(attribution_results)")}
        finally:
            conn.close()
        # 54 号 §3.5 两层归因必备列
        assert {
            "period",
            "portfolio_id",
            "layer",
            "allocation_effect",
            "selection_effect",
            "interaction_effect",
            "total_return",
            "transaction_cost_drag",
            "net_pnl",
            "invariant_status",
            "computed_at",
            "idempotency_key",
        } <= cols

    def test_default_db_path_ssot(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        db = tmp_path / "ssot.db"
        monkeypatch.setattr(store, "DB_PATH", db)
        resolved = ensure_attribution_results_table()  # None → DB_PATH SSoT
        assert resolved == db
        assert db.exists()


class TestStoreAndQueryRoundtrip:
    def test_firm_row_roundtrip(self, tmp_db: Path) -> None:
        rid = store_attribution_report(_report(), layer="firm", net_pnl=12345.67, db_path=tmp_db)
        assert rid > 0
        rows = query_attribution_results(portfolio_id="PF-FIRM", db_path=tmp_db)
        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == rid
        assert row["layer"] == "firm"
        assert row["period"] == "2026-08-21"
        # 保原文字符串，float() 精确往返（repr 精度）
        assert float(row["allocation_effect"]) == 0.002
        assert float(row["selection_effect"]) == 0.03
        assert float(row["interaction_effect"]) == 0.006
        assert float(row["total_return"]) == 0.037
        assert float(row["transaction_cost_drag"]) == 0.001
        assert float(row["net_pnl"]) == 12345.67
        assert row["idempotency_key"] == "attr-20260821-firm"
        assert row["schema_version"] == "1.0"

    def test_multi_day_period_format(self, tmp_db: Path) -> None:
        store_attribution_report(_report(key="k-range", start="2026-08-01", end="2026-08-07"), db_path=tmp_db)
        row = query_attribution_results(db_path=tmp_db)[0]
        assert row["period"] == "2026-08-01~2026-08-07"

    def test_idempotent_same_key_keeps_first(self, tmp_db: Path) -> None:
        rid1 = store_attribution_report(_report(), layer="firm", db_path=tmp_db)
        # 同幂等键、不同内容重跑 → 跳过保首条返回同 id
        rid2 = store_attribution_report(_report(alloc=9.9), layer="firm", db_path=tmp_db)
        assert rid2 == rid1
        rows = query_attribution_results(db_path=tmp_db)
        assert len(rows) == 1
        assert float(rows[0]["allocation_effect"]) == 0.002

    def test_query_filters_and_order(self, tmp_db: Path) -> None:
        store_attribution_report(_report(key="f1"), layer="firm", db_path=tmp_db)
        store_attribution_report(_report(portfolio_id="S1", key="s1"), layer="strategy", db_path=tmp_db)
        store_attribution_report(
            _report(portfolio_id="S2", key="s2", start="2026-08-22", end="2026-08-22"),
            layer="strategy",
            db_path=tmp_db,
        )
        # layer 过滤
        firm_rows = query_attribution_results(layer="firm", db_path=tmp_db)
        assert len(firm_rows) == 1
        strat_rows = query_attribution_results(layer="strategy", db_path=tmp_db)
        assert len(strat_rows) == 2
        # 倒序：period DESC（2026-08-22 在前）
        assert strat_rows[0]["period"] == "2026-08-22"
        # period 过滤 + limit
        d21 = query_attribution_results(period="2026-08-21", db_path=tmp_db)
        assert len(d21) == 2
        assert len(query_attribution_results(limit=1, db_path=tmp_db)) == 1

    def test_get_by_key_hit_and_miss(self, tmp_db: Path) -> None:
        store_attribution_report(_report(), layer="firm", db_path=tmp_db)
        hit = get_attribution_by_key("attr-20260821-firm", db_path=tmp_db)
        assert hit is not None and hit["portfolio_id"] == "PF-FIRM"
        assert get_attribution_by_key("no-such-key", db_path=tmp_db) is None


class TestTwoLayerPersist:
    def test_pass_invariant_writes_three_rows(self, tmp_db: Path) -> None:
        firm = _report()
        s1 = _report(portfolio_id="S1", key="attr-s1", alloc=0.001, sel=0.01, inter=0.0, drag=0.0)
        s2 = _report(portfolio_id="S2", key="attr-s2", alloc=0.001, sel=0.02, inter=0.006, drag=0.001)
        result = persist_two_layer_attribution(
            firm_report=firm,
            strategy_reports={"S1": s1, "S2": s2},
            strategy_pnls={"S1": 5000.0, "S2": 7345.67},
            firm_pnl=12345.67,
            db_path=tmp_db,
        )
        assert result.invariant_status == "PASS"
        assert result.rows_written == 3
        assert set(result.strategy_row_ids) == {"S1", "S2"}
        rows = query_attribution_results(db_path=tmp_db)
        assert len(rows) == 3
        firm_row = next(r for r in rows if r["layer"] == "firm")
        assert firm_row["invariant_status"] == "PASS"
        assert float(firm_row["net_pnl"]) == 12345.67
        s1_row = get_attribution_by_key("attr-s1", db_path=tmp_db)
        assert s1_row["invariant_status"] is None  # 策略层不挂不变量状态（schema 口径）
        assert float(s1_row["net_pnl"]) == 5000.0

    def test_fail_invariant_recorded_not_silent(self, tmp_db: Path) -> None:
        # firm_pnl 与策略和差 10%（远超 1bp 门禁）→ FAIL 落库显性标记
        result = persist_two_layer_attribution(
            firm_report=_report(),
            strategy_reports={"S1": _report(portfolio_id="S1", key="attr-s1")},
            strategy_pnls={"S1": 1000.0},
            firm_pnl=2000.0,
            db_path=tmp_db,
        )
        assert result.invariant_status == "FAIL"
        firm_row = next(r for r in query_attribution_results(db_path=tmp_db) if r["layer"] == "firm")
        assert firm_row["invariant_status"] == "FAIL"

    def test_key_mismatch_rejected(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="不一致"):
            persist_two_layer_attribution(
                firm_report=_report(),
                strategy_reports={"S1": _report(portfolio_id="S1", key="attr-s1")},
                strategy_pnls={"S2": 1.0},  # 键集不一致
                firm_pnl=1.0,
                db_path=tmp_db,
            )
        # 拒绝后零写入（fail-closed 先于任何落库）
        assert query_attribution_results(db_path=tmp_db) == []


class TestFailClosed:
    def test_invalid_layer(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="layer"):
            store_attribution_report(_report(), layer="middle", db_path=tmp_db)

    def test_invalid_invariant_status(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="invariant_status"):
            store_attribution_report(_report(), invariant_status="MAYBE", db_path=tmp_db)

    def test_empty_idempotency_key_rejected(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="idempotency_key"):
            store_attribution_report(_report(key="  "), db_path=tmp_db)

    def test_invalid_limit(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="limit"):
            query_attribution_results(limit=0, db_path=tmp_db)

    def test_invalid_layer_filter(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="layer"):
            query_attribution_results(layer="bogus", db_path=tmp_db)


# ──────────────────────────────────────────────────────────────────────────────
# 结算完成事件腿（L10b-W1：事件 → 归因计算 → attribution_results 落库）
# ──────────────────────────────────────────────────────────────────────────────


def _inputs(portfolio_id: str = "PF-FIRM", drag: float = 0.001) -> store.DailyAttributionInputs:
    """板块级 BHB 输入单（两板块，基准/组合权重和各=1，守恒口径可验算）。"""
    return store.DailyAttributionInputs(
        portfolio_id=portfolio_id,
        portfolio_weights={"成长": 0.6, "价值": 0.4},
        benchmark_weights={"成长": 0.5, "价值": 0.5},
        portfolio_returns={"成长": 0.02, "价值": 0.01},
        benchmark_returns={"成长": 0.015, "价值": 0.008},
        transaction_cost_drag=drag,
    )


def _deps(db: Path, provider=..., alert_calls: list | None = None) -> store.AttributionDeps:
    """事件腿装配单（tmp 库注入；provider 缺省=正常桩，alert_calls 捕获告警）。"""
    if alert_calls is None:
        alert_calls = []

    def _alert(day: str, message: str) -> None:
        alert_calls.append((day, message))

    if provider is ...:
        provider = lambda day: _inputs()  # noqa: E731 — 测试桩
    return store.AttributionDeps(input_provider=provider, db_path=db, alert_sink=_alert)


class TestRunDailyAttribution:
    def test_unwired_without_deps(self, tmp_db: Path) -> None:
        """依赖未装配 → UNWIRED 显式态不伪跑（零落库，禁拍假值）。"""
        store.reset_attribution_bridge_state()
        result = store.run_daily_attribution("2026-10-04")
        assert result["status"] == "UNWIRED"
        assert query_attribution_results(db_path=tmp_db) == []

    def test_ok_computes_and_persists(self, tmp_db: Path) -> None:
        """装配齐全 → OK：BHB 计算+落库，幂等键确定性派生，列契约吻合。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        result = store.run_daily_attribution("2026-10-04")
        assert result["status"] == "OK"
        assert result["residual_quality"] == "PASS"  # 单期 BHB 守恒 → residual 浮点精度级
        rows = query_attribution_results(portfolio_id="PF-FIRM", layer="firm", db_path=tmp_db)
        assert len(rows) == 1
        row = rows[0]
        assert row["period"] == "2026-10-04"
        assert row["idempotency_key"] == "attribution:PF-FIRM:2026-10-04"
        assert row["invariant_status"] is None  # 单层落库不挂两层不变量态
        # total_return = 几何超额收益 (1+R_p)/(1+R_b)−1 − drag（Carino 链接口径）
        r_p = 0.6 * 0.02 + 0.4 * 0.01
        r_b = 0.5 * 0.015 + 0.5 * 0.008
        assert float(row["total_return"]) == pytest.approx((1 + r_p) / (1 + r_b) - 1 - 0.001)

    def test_idempotent_replay_keeps_first(self, tmp_db: Path) -> None:
        """同日重跑（事件重放）→ 幂等键同键跳过保首条。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        first = store.run_daily_attribution("2026-10-04")
        second = store.run_daily_attribution("2026-10-04")
        assert first["status"] == "OK" and second["status"] == "OK"
        assert first["row_id"] == second["row_id"]
        assert len(query_attribution_results(db_path=tmp_db)) == 1

    def test_degraded_provider_raises_isolated(self, tmp_db: Path) -> None:
        """归因输入异常 → DEGRADED 显式态+告警，不逃逸主流程。"""
        store.reset_attribution_bridge_state()
        alerts: list[tuple[str, str]] = []

        def _boom(day: str) -> store.DailyAttributionInputs:
            raise RuntimeError("provider down")

        store.register_attribution_deps(_deps(tmp_db, provider=_boom, alert_calls=alerts))
        result = store.run_daily_attribution("2026-10-04")
        assert result["status"] == "DEGRADED"
        assert "provider down" in result["error"]
        assert alerts and alerts[0][0] == "2026-10-04"
        assert query_attribution_results(db_path=tmp_db) == []

    def test_degraded_bad_weights_isolated(self, tmp_db: Path) -> None:
        """非法权重（BHB fail-closed）→ DEGRADED 不抛 ValueError 出函数。"""
        store.reset_attribution_bridge_state()
        bad = store.DailyAttributionInputs(
            portfolio_id="PF-BAD",
            portfolio_weights={"成长": -0.5},  # 负权重 fail-closed
            benchmark_weights={"成长": 0.5},
            portfolio_returns={"成长": 0.02},
            benchmark_returns={"成长": 0.015},
        )
        store.register_attribution_deps(
            store.AttributionDeps(input_provider=lambda day: bad, db_path=tmp_db, alert_sink=None)
        )
        result = store.run_daily_attribution("2026-10-04")
        assert result["status"] == "DEGRADED"
        assert "负权重" in result["error"]

    def test_register_rejects_wrong_type(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="AttributionDeps"):
            store.register_attribution_deps("not-deps")  # type: ignore[arg-type]
        store.reset_attribution_bridge_state()


class TestAttributionEventLeg:
    def test_swept_event_triggers_attribution(self, tmp_db: Path) -> None:
        """sweep 完成回执（status=OK）→ 事件腿自动归因落库。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        store.subscribe_eventbus()
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import TOPIC_RECON_SWEPT

        bus.emit(TOPIC_RECON_SWEPT, {"trade_date": "2026-10-04", "status": "OK"})
        rows = query_attribution_results(portfolio_id="PF-FIRM", db_path=tmp_db)
        assert len(rows) == 1
        store.reset_attribution_bridge_state()  # 退订防跨测试残留

    def test_unwired_sweep_skipped(self, tmp_db: Path) -> None:
        """UNWIRED/ERROR sweep 或缺日期 → 事件腿不归因。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        store.subscribe_eventbus()
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import TOPIC_RECON_SWEPT

        for payload in (
            {"trade_date": "2026-10-04", "status": "UNWIRED"},
            {"trade_date": "2026-10-04", "status": "ERROR"},
            {"status": "OK"},
            {},
        ):
            bus.emit(TOPIC_RECON_SWEPT, payload)
        assert query_attribution_results(db_path=tmp_db) == []
        store.reset_attribution_bridge_state()

    def test_subscribe_is_idempotent(self, tmp_db: Path) -> None:
        """重复 subscribe_eventbus → 单 handler，事件重放零重复落库。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        store.subscribe_eventbus()
        store.subscribe_eventbus()  # 幂等
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import TOPIC_RECON_SWEPT

        bus.emit(TOPIC_RECON_SWEPT, {"trade_date": "2026-10-04", "status": "OK"})
        assert len(query_attribution_results(db_path=tmp_db)) == 1  # 幂等键+单 handler 双保险
        store.reset_attribution_bridge_state()

    def test_reset_unsubscribes(self, tmp_db: Path) -> None:
        """reset 后事件不再触发归因（退订防跨测试叠加双跑）。"""
        store.reset_attribution_bridge_state()
        store.register_attribution_deps(_deps(tmp_db))
        store.subscribe_eventbus()
        store.reset_attribution_bridge_state()
        from zephyr.shared.event_bus import bus
        from zephyr.trading.post_settlement_pipeline import TOPIC_RECON_SWEPT

        bus.emit(TOPIC_RECON_SWEPT, {"trade_date": "2026-10-04", "status": "OK"})
        assert query_attribution_results(db_path=tmp_db) == []
