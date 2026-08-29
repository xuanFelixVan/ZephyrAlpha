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
    fetch_index_regime_panel,
    fetch_next_day_inertia,
    fetch_playbook_action,
    fetch_warroom,
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
