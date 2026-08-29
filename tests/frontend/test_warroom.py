# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-L28-WARROOM | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.frontend.test_warroom
# [TESTS] src/zephyr/frontend/dashboard/components/warroom.py
"""MOD-L28-WARROOM 单元测试：作战指挥室页组件（45号作战手册 P1）。

验收口径：
  - fetch 全通道 fail-open（空库/异常 → None + error 留痕，不抛）；
  - prediction_log scenario_plan/outcome 两族消费正确（payload 解析）；
  - playbook 模板检索（scenario → 对策）正确；
  - 惯性三桶聚合（展示口径）与方向判定正确；
  - 四指数面板注入与降级路径正确；
  - render payload 可 JSON 序列化，panel 在时 '_layout' 存在。
数据源全部内存/临时库构造，不连真实 CH/DB。
"""

from __future__ import annotations

import json

import pytest

pytest.importorskip(
    "zephyr.frontend.dashboard.components.warroom",
    reason="warroom not importable",
)

from zephyr.frontend.dashboard.components.warroom import (
    WarroomData,
    fetch_batch_boundaries,
    fetch_correlation_netting,
    fetch_index_regime_panel,
    fetch_next_day_inertia,
    fetch_playbook_action,
    fetch_sit_out_list,
    fetch_warroom,
    fetch_warroom_debate,
    fetch_warroom_outcome,
    fetch_warroom_plan,
    render_warroom,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
)
from zephyr.signal_ashare.next_day_8state_forecast import (
    NextDayForecast,
    NextDayState,
)

_DATE = "2026-08-28"


def _seed_plan_payload() -> dict:
    """最小 scenario_plan payload（MOD-PLAN-005 契约形状）。"""
    return {
        "date": _DATE,
        "three_scenarios": [
            {
                "name": "HIGH_OPEN",
                "open_pct_min": 0.02,
                "open_pct_max": None,
                "stance": "NORMAL",
                "final_shift": 0.0,
                "max_add_position": 0.3,
                "no_add_price": 1742.0,
                "reduce_trigger_price": 1690.0,
                "must_exit_price": 1745.0,
                "actions": ["高开≥+2% 激活：加仓上限 30%（NORMAL档）"],
            }
        ],
        "auction_verification": {
            "deviation": 0.0035,
            "volume_ratio": 1.31,
            "fake_ratio": 0.22,
            "yesterday_limit_premium": 0.021,
            "direction": "FLAT",
            "direction_consistent": True,
            "confirmed": True,
            "volume_shrink": False,
            "direction_void": False,
            "status": "ok",
            "detail": {},
        },
        "final_scenario": "FLAT_OPEN_REAL_UP",
        "confidence_scale": 1.0,
        "degraded": False,
        "reasons": ["final_shift=+0.0 → NORMAL档"],
        "trace": {"channels": {}},
    }


def _seed_outcome_payload() -> dict:
    """最小 outcome payload（MOD-PLAN-008 回写契约形状）。"""
    return {
        "hit": True,
        "dimension": "prediction",
        "scenario": "FLAT_OPEN_REAL_UP",
        "actual_scenario": "FLAT_OPEN_REAL_UP",
        "open_pct": 0.003,
        "trend_pct": 0.004,
        "trend_source": "kline_etf_1min",
        "predicted_confidence": 1.0,
        "signal_source": "MOD-PLAN-005.scenario_planner",
    }


class _FakeForecaster:
    """MOD-SIG-037 mock：偏空分布（下行桶最大）。"""

    def forecast(self, symbol: str) -> NextDayForecast:
        probs = {
            NextDayState.GAP_DOWN_DOWN: 0.40,
            NextDayState.FLAT_DOWN: 0.15,
            NextDayState.GAP_UP_DOWN: 0.05,
            NextDayState.GAP_UP_UP: 0.10,
            NextDayState.FLAT_UP: 0.05,
            NextDayState.GAP_DOWN_UP: 0.05,
            NextDayState.FLAT_CLOSE: 0.10,
            NextDayState.VIOLENT: 0.10,
        }
        return NextDayForecast(
            current_state=NextDayState.FLAT_DOWN,
            probabilities=probs,
            top_state=NextDayState.GAP_DOWN_DOWN,
            top_probability=0.40,
            confidence=0.32,
            n_transitions=120,
        )


class _FakePanel:
    """MOD-REGIME-008 mock：to_dict 形态。"""

    def to_dict(self) -> dict:
        return {
            "trade_date": _DATE,
            "cards": [
                {
                    "code": "000300",
                    "name": "沪深300",
                    "trade_date": _DATE,
                    "probabilities": {"r1": 0.6, "r2": 0.4},
                    "dominant_regime": "r1",
                    "confidence": 0.6,
                    "recent_return": 0.012,
                    "volatility": 0.18,
                    "strength_score": 0.5,
                    "rank": 1,
                    "degraded": False,
                    "degrade_reason": None,
                    "hmm_degraded": False,
                }
            ],
            "strength_ranking": ["000300"],
            "divergence_alerts": [],
            "degraded": False,
        }


class TestFetchPlan:
    """区① 前日预案取数（prediction_log scenario_plan 族）。"""

    def test_empty_db_returns_none_no_error(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        payload, asof, err = fetch_warroom_plan(_DATE, db_path=db)
        assert payload is None and asof is None and err is None

    def test_seeded_plan_parsed(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.scenario_planner",
            prediction_type="scenario_plan",
            payload=_seed_plan_payload(),
            db_path=db,
        )
        payload, asof, err = fetch_warroom_plan(_DATE, db_path=db)
        assert err is None and asof is not None
        assert payload is not None
        assert payload["final_scenario"] == "FLAT_OPEN_REAL_UP"
        assert payload["three_scenarios"][0]["no_add_price"] == 1742.0
        assert payload["auction_verification"]["volume_ratio"] == 1.31

    def test_missing_table_fail_open(self, tmp_path) -> None:
        db = tmp_path / "no_table.db"  # 未建表 → 查询异常 fail-open
        payload, _asof, err = fetch_warroom_plan(_DATE, db_path=db)
        assert payload is None and err is not None


class TestFetchOutcome:
    """区② outcome 族（盘后回写）取数。"""

    def test_seeded_outcome_parsed(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.scenario_planner",
            prediction_type="outcome",
            payload=_seed_outcome_payload(),
            db_path=db,
        )
        payload, err = fetch_warroom_outcome(_DATE, db_path=db)
        assert err is None and payload is not None
        assert payload["hit"] is True
        assert payload["actual_scenario"] == "FLAT_OPEN_REAL_UP"
        assert payload["trend_source"] == "kline_etf_1min"

    def test_empty_db_returns_none(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        payload, err = fetch_warroom_outcome(_DATE, db_path=db)
        assert payload is None and err is None


class TestPlaybookAction:
    """剧本对策检索（scenario_playbook production 模板库只读）。"""

    def test_known_scenario(self) -> None:
        pb = fetch_playbook_action("HIGH_OPEN_FAKE_UP")
        assert pb is not None
        assert pb["action"] == "REDUCE"
        assert pb["action_zh"] == "减仓"
        assert pb["risk_escalation"] == 1

    def test_unknown_or_empty(self) -> None:
        assert fetch_playbook_action(None) is None
        assert fetch_playbook_action("NOT_A_SCENARIO") is None


class TestInertia:
    """区③ 惯性推演（MOD-SIG-037 注入 + 三桶展示聚合）。"""

    def test_buckets_and_direction(self) -> None:
        inertia, err = fetch_next_day_inertia(forecaster=_FakeForecaster())
        assert err is None and inertia is not None
        # 下行桶 = GAP_DOWN_DOWN 0.40 + FLAT_DOWN 0.15 + GAP_UP_DOWN 0.05 = 0.60
        assert inertia["bucket_down"] == pytest.approx(0.60, abs=1e-3)
        assert inertia["direction"] == "down"
        assert inertia["current_state_zh"] == "平开低走"
        assert inertia["top_state_zh"] == "低开低走"
        assert abs(sum(inertia["probs"].values()) - 1.0) < 1e-6

    def test_forecaster_exception_fail_open(self) -> None:
        class _Boom:
            def forecast(self, symbol: str):
                raise RuntimeError("no CH")

        inertia, err = fetch_next_day_inertia(forecaster=_Boom())
        assert inertia is None and err is not None


class TestIndexPanel:
    """区④ IDX-02 四指数面板接入。"""

    def test_injected_panel(self) -> None:
        panel, err = fetch_index_regime_panel(_DATE, panel_fn=lambda _d: _FakePanel())
        assert err is None and panel is not None
        assert panel["cards"][0]["dominant_regime"] == "r1"
        assert panel["degraded"] is False

    def test_panel_exception_fail_open(self) -> None:
        def _boom(_d):
            raise RuntimeError("no CH")

        panel, err = fetch_index_regime_panel(_DATE, panel_fn=_boom)
        assert panel is None and err is not None


class TestFetchWarroomAggregate:
    """聚合取数（fail-open，单通道异常不炸）。"""

    def test_aggregate_with_seeded_db(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.scenario_planner",
            prediction_type="scenario_plan",
            payload=_seed_plan_payload(),
            db_path=db,
        )
        data = fetch_warroom(
            trade_date=_DATE,
            db_path=db,
            forecaster=_FakeForecaster(),
            panel_fn=lambda _d: _FakePanel(),
        )
        assert isinstance(data, WarroomData)
        assert data.trade_date == _DATE
        assert data.plan is not None and data.outcome is None
        assert data.playbook is not None  # final_scenario=FLAT_OPEN_REAL_UP → ADD
        assert data.playbook["action"] == "ADD"
        assert data.inertia is not None and data.index_panel is not None
        assert data.errors == []

    def test_aggregate_all_channels_down(self, tmp_path) -> None:
        db = tmp_path / "no_table.db"  # 未建表 → 预案/outcome 通道 error 留痕
        data = fetch_warroom(trade_date=_DATE, db_path=db, forecaster=_BoomAll(), panel_fn=_boom_all)
        assert data.plan is None and data.inertia is None and data.index_panel is None
        assert len(data.errors) >= 3  # plan/outcome/惯性/四指数 全留痕


def _boom_all(_d):
    raise RuntimeError("no CH")


class _BoomAll:
    def forecast(self, symbol: str):
        raise RuntimeError("no CH")


class TestRenderWarroom:
    """渲染层：payload 可序列化 + 区块占位/负反馈标注。"""

    def test_payload_serializable_and_layout(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.scenario_planner",
            prediction_type="scenario_plan",
            payload=_seed_plan_payload(),
            db_path=db,
        )
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.scenario_planner",
            prediction_type="outcome",
            payload=_seed_outcome_payload(),
            db_path=db,
        )
        data = fetch_warroom(
            trade_date=_DATE,
            db_path=db,
            forecaster=_FakeForecaster(),
            panel_fn=lambda _d: _FakePanel(),
        )
        payload = render_warroom(data)
        assert payload["has_plan"] is True
        assert payload["has_outcome"] is True
        assert payload["has_inertia"] is True
        assert payload["has_index_panel"] is True
        # payload 除 _layout 外须 JSON 可序列化
        json.dumps({k: v for k, v in payload.items() if k != "_layout"}, ensure_ascii=False)
        if payload["renderer"] == "panel":
            assert payload.get("_layout") is not None

    def test_render_empty_data_fail_open(self) -> None:
        payload = render_warroom(WarroomData(trade_date=_DATE))
        assert payload["has_plan"] is False
        assert payload["errors"] == []
        json.dumps({k: v for k, v in payload.items() if k != "_layout"}, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────────────
# P2：缺口⑥~⑩（9 格矩阵展示层/批量边界/相关性净额/禁做清单）
# ──────────────────────────────────────────────────────────────────────────────


def _seed_boundary_payload(symbol: str) -> dict:
    """最小 tomorrow_boundary payload（MOD-PLAN-012 落库契约形状）。"""
    return {
        "symbol": symbol,
        "box_upper": 1750.0,
        "box_lower": 1690.0,
        "max_add_position": 0.3,
        "no_add_price": 1742.0,
        "must_exit_price": 1745.0,
        "breakout_confirm": True,
        "source_trade_date": "2026-08-27",
        "target_date": _DATE,
        "producer": "MOD-PLAN-012.batch_boundary_runner",
    }


class TestBatchBoundaries:
    """缺口⑦：批量边界回查（tomorrow_boundary 族，只读）。"""

    def test_empty_db_returns_empty_list(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        items, err = fetch_batch_boundaries(_DATE, db_path=db)
        assert items == [] and err is None

    def test_seeded_rows_parsed(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        for sym in ("600519", "000001"):
            log_prediction(
                trade_date=_DATE,
                module="plan_engine.tomorrow_boundary_planner",
                prediction_type="tomorrow_boundary",
                payload=_seed_boundary_payload(sym),
                db_path=db,
            )
        items, err = fetch_batch_boundaries(_DATE, db_path=db)
        assert err is None and items is not None
        assert len(items) == 2
        assert {i["symbol"] for i in items} == {"600519", "000001"}
        assert items[0]["box_lower"] == 1690.0
        assert items[0]["breakout_confirm"] is True

    def test_missing_table_fail_open(self, tmp_path) -> None:
        db = tmp_path / "no_table.db"
        items, err = fetch_batch_boundaries(_DATE, db_path=db)
        assert items is None and err is not None


class TestSitOutList:
    """缺口⑩：禁做清单（MOD-PLAN-014 三源注入，未装配=待接入不假阴性）。"""

    def test_no_sources_means_pending(self) -> None:
        sit, err = fetch_sit_out_list(_DATE, sources=None)
        assert sit is None and err is None

    def test_three_sources_synthesized(self) -> None:
        sit, err = fetch_sit_out_list(_DATE, sources={
            "events": [
                {  # blackout 市场级 → NO_TRADE 进清单
                    "event_date": _DATE, "event_type": "EVT-FOMC", "scope": "market",
                    "target": None, "severity": "blackout", "name": "美联储议息",
                },
                {  # caution 级不进清单仅计数
                    "event_date": _DATE, "event_type": "EVT-DATA", "scope": "market",
                    "target": None, "severity": "caution", "name": "CPI 发布",
                },
            ],
            "stopped_symbols": [{"symbol": "600519", "stopped_at": _DATE, "reason": "破减仓触发价"}],
            "limit_down_symbols": ["000001"],
            "war_pool_symbols": ["600519"],
        })
        assert err is None and sit is not None
        rules = {e["rule"] for e in sit["entries"]}
        assert rules == {"EVENT_BLACKOUT", "STOP_LOSS_NO_REVERSE", "LIMIT_DOWN_NO_DIP", "OUT_OF_POOL"}
        actions = {e["rule"]: e["action"] for e in sit["entries"]}
        assert actions["EVENT_BLACKOUT"] == "NO_TRADE"
        assert actions["STOP_LOSS_NO_REVERSE"] == "NO_REVERSE"
        assert actions["LIMIT_DOWN_NO_DIP"] == "NO_BUY"
        assert sit["pool_rule_active"] is True
        assert any("caution" in n for n in sit["notes"])  # caution 计数留痕

    def test_bad_source_fail_open(self) -> None:
        sit, err = fetch_sit_out_list(_DATE, sources={"events": [{"event_date": "bad"}]})
        assert sit is None and err is not None


class TestCorrelationNetting:
    """缺口⑨：相关性净额（GAP-F-04 展示层消费，未装配=待接入不假阴性）。"""

    def test_no_positions_means_pending(self) -> None:
        netting, err = fetch_correlation_netting(positions=None)
        assert netting is None and err is None

    def test_cluster_merged(self) -> None:
        netting, err = fetch_correlation_netting(
            positions={"A": 0.1, "B": 0.08, "C": 0.05},
            correlation_pairs=[("A", "B", 0.85)],
            as_of=_DATE,
        )
        assert err is None and netting is not None
        assert netting["gross_position_count"] == 3
        assert netting["net_risk_units"] == 2  # A+B 合并，C 独立
        assert netting["netting_reduction"] == 1
        assert netting["clusters"][0]["members"] == ["A", "B"]
        assert netting["as_of"] == _DATE

    def test_invalid_input_fail_open(self) -> None:
        netting, err = fetch_correlation_netting(positions={"A": -0.1})
        assert netting is None and err is not None


class TestScenarioGrid:
    """缺口⑥展示层：3×3 矩阵 9 格封闭穷举 + 概率待接入标注 + 最可能格高亮。"""

    def test_nine_cells_exhaustive_no_prob(self) -> None:
        data = WarroomData(trade_date=_DATE, plan=_seed_plan_payload())
        payload = render_warroom(data)
        grid = payload["scenario_grid"]
        assert len(grid) == 9
        keys = {c["scenario"] for c in grid}
        assert len(keys) == 9  # 封闭穷举无重复
        assert "LOW_OPEN_FAKE_DOWN" in keys and "HIGH_OPEN_FAKE_UP" in keys
        assert payload["grid_prob_available"] is False
        assert all(c["prob"] is None for c in grid)  # BM-SEL-04 暂缓→待接入
        focus = [c for c in grid if c["is_focus"]]
        assert len(focus) == 1 and focus[0]["scenario"] == "FLAT_OPEN_REAL_UP"

    def test_grid_probabilities_rendered_when_logged(self) -> None:
        plan = _seed_plan_payload()
        plan["grid_probabilities"] = {"FLAT_OPEN_REAL_UP": 0.35, "FLAT_OPEN_WASH": 0.20}
        payload = render_warroom(WarroomData(trade_date=_DATE, plan=plan))
        assert payload["grid_prob_available"] is True
        cell = next(c for c in payload["scenario_grid"] if c["scenario"] == "FLAT_OPEN_REAL_UP")
        assert cell["prob"] == pytest.approx(0.35)

    def test_focus_prefers_outcome_actual(self) -> None:
        data = WarroomData(
            trade_date=_DATE,
            plan=_seed_plan_payload(),
            outcome=_seed_outcome_payload() | {"actual_scenario": "LOW_OPEN_FAKE_DOWN"},
        )
        payload = render_warroom(data)
        focus = [c for c in payload["scenario_grid"] if c["is_focus"]]
        assert len(focus) == 1 and focus[0]["scenario"] == "LOW_OPEN_FAKE_DOWN"


class TestFetchWarroomAggregateP2:
    """P2 三通道聚合（fail-open，单通道异常不炸）。"""

    def test_aggregate_p2_channels(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        log_prediction(
            trade_date=_DATE,
            module="plan_engine.tomorrow_boundary_planner",
            prediction_type="tomorrow_boundary",
            payload=_seed_boundary_payload("600519"),
            db_path=db,
        )
        data = fetch_warroom(
            trade_date=_DATE,
            db_path=db,
            forecaster=_FakeForecaster(),
            panel_fn=lambda _d: _FakePanel(),
            positions={"600519": 0.1, "000001": 0.08},
            correlation_pairs=[("600519", "000001", 0.9)],
            sit_out_sources={"war_pool_symbols": ["600519"]},
        )
        assert data.boundaries is not None and len(data.boundaries) == 1
        assert data.netting is not None and data.netting["net_risk_units"] == 1
        assert data.sit_out is not None and data.sit_out["pool_rule_active"] is True
        assert data.errors == []
        payload = render_warroom(data)
        assert payload["has_boundaries"] is True
        assert payload["has_netting"] is True and payload["has_sit_out"] is True
        json.dumps({k: v for k, v in payload.items() if k != "_layout"}, ensure_ascii=False)

    def test_aggregate_p2_unassembled_pending(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        data = fetch_warroom(
            trade_date=_DATE, db_path=db,
            forecaster=_FakeForecaster(), panel_fn=lambda _d: _FakePanel(),
        )
        assert data.boundaries == []  # 当日未跑批=待数据（非异常）
        assert data.sit_out is None and data.netting is None  # 未装配=待接入
        assert data.errors == []
        payload = render_warroom(data)
        assert payload["has_boundaries"] is False
        assert payload["has_sit_out"] is False and payload["has_netting"] is False


def _seed_debate_row(db, *, prompt_version: str = "pm-v1.0.0+debate", status: str = "success",
                     mode: str = "v2_debate", with_debate: bool = True) -> None:
    """种一行 llm_daily_analysis（MOD-PLAN-007 落库契约形状）。"""
    from zephyr.plan_engine.llm_premarket_analysis import ensure_llm_daily_analysis_table
    from zephyr.shared.io.sqlite_factory import get_db_connection

    ensure_llm_daily_analysis_table(db)
    output = {
        "mode": mode,
        "analysis": {
            "date": _DATE,
            "scenarios": {
                "gap_up": {"prob": 0.3, "key_levels": ["3900"], "action_boundary": "高开不追"},
                "flat": {"prob": 0.5, "key_levels": [], "action_boundary": "平开按预案"},
                "gap_down": {"prob": 0.2, "key_levels": [], "action_boundary": "低开等确认"},
            },
            "risk_points": ["外围波动"],
            "watch_sectors": ["半导体"],
            "confidence_note": "量能数据缺口",
        },
        "debate": {"bull": "资金面改善，主线延续", "bear": "炸板率抬升，分歧加大"} if with_debate else None,
    }
    conn = get_db_connection(db)
    try:
        conn.execute(
            "INSERT INTO llm_daily_analysis "
            "(trade_date, model_version, prompt_version, input_hash, output_json, status, "
            "error, tokens_in, tokens_out, cost_yuan, latency_ms, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (_DATE, "qwen3:14b", prompt_version, "h1", json.dumps(output, ensure_ascii=False),
             status, None, None, None, None, None, "2026-08-28T01:00:00+00:00"),
        )
        conn.commit()
    finally:
        conn.close()


class TestWarroomDebate:
    """缺口⑧ P3：W4 多空辩论台（llm_daily_analysis v2 辩论行只读消费，fail-open）。"""

    def test_no_db_returns_none_no_error(self, tmp_path) -> None:
        debate, err = fetch_warroom_debate(_DATE, db_path=tmp_path / "missing.db")
        assert debate is None and err is None  # 未启用/未跑批=正常态非异常

    def test_seeded_v2_debate_parsed(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        _seed_debate_row(db)
        debate, err = fetch_warroom_debate(_DATE, db_path=db)
        assert err is None and debate is not None
        assert debate["bull"] == "资金面改善，主线延续"
        assert debate["bear"] == "炸板率抬升，分歧加大"
        assert debate["analysis"]["scenarios"]["flat"]["prob"] == pytest.approx(0.5)
        assert debate["prompt_version"] == "pm-v1.0.0+debate"
        assert debate["model_version"] == "qwen3:14b"

    def test_v1_row_ignored(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        _seed_debate_row(db, prompt_version="pm-v1.0.0", mode="v1", with_debate=False)
        debate, err = fetch_warroom_debate(_DATE, db_path=db)
        assert debate is None and err is None  # v1 单调用行不进 W4

    def test_debate_transcripts_missing_returns_none(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        _seed_debate_row(db, with_debate=False)
        debate, err = fetch_warroom_debate(_DATE, db_path=db)
        assert debate is None and err is None  # 无陈词段=无可展示产物

    def test_missing_table_fail_open(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)  # 建库但不建 llm_daily_analysis
        debate, err = fetch_warroom_debate(_DATE, db_path=db)
        assert debate is None and err is None  # 表未建=从未跑批=待接入（正常态）

    def test_aggregate_and_render_payload(self, tmp_path) -> None:
        db = tmp_path / "governance.db"
        ensure_prediction_log_table(db)
        _seed_debate_row(db)
        data = fetch_warroom(
            trade_date=_DATE, db_path=db,
            forecaster=_FakeForecaster(), panel_fn=lambda _d: _FakePanel(),
        )
        assert data.debate is not None and data.errors == []
        payload = render_warroom(data)
        assert payload["has_debate"] is True
        assert payload["debate"]["bull"].startswith("资金面")
        json.dumps({k: v for k, v in payload.items() if k != "_layout"}, ensure_ascii=False)

    def test_render_no_debate_pending(self) -> None:
        payload = render_warroom(WarroomData(trade_date=_DATE))
        assert payload["has_debate"] is False and payload["debate"] is None
