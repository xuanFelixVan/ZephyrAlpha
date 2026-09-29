# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_cleaning_engines
# [DOMAIN] D_DATA
# [TTL] permanent
"""cleaning_engines 统一入口测试 — F04 夜战批（tmp_path 数据，零生产 data/ 写入）

覆盖: 四引擎静态台账 / 四派发函数端到端（真引擎小数据）/
      C6 AI 判净接口位 fail-closed。
"""

from __future__ import annotations

import pandas as pd
import pytest

from zephyr.data.cleaning_engines import (
    AiAdjudicationPendingOwnerGateError,
    ai_adjudicate,
    detect_frame_anomalies,
    engines_status,
    evaluate_anomaly_signals,
    run_dsl_rules,
    validate_expectations,
)


class TestEnginesStatus:
    def test_four_engines_listed(self):
        status = engines_status()
        assert len(status) == 4
        assert {e.key for e in status} == {
            "dsl_rule_engine",
            "cleaning_anomaly_engine",
            "expectation_governance",
            "data_anomaly_alerter",
        }

    def test_wiring_reality_declared(self):
        """接线实况声明：DSL 引擎=已接线（hosting 读侧托管），其余三件 built-not-wired。"""
        by_key = {e.key: e for e in engines_status()}
        assert by_key["dsl_rule_engine"].wired is True
        assert "cleaning_rules_hosting" in by_key["dsl_rule_engine"].consumer
        for key in ("cleaning_anomaly_engine", "expectation_governance", "data_anomaly_alerter"):
            assert by_key[key].wired is False, f"{key} 接线实况声明漂移"
            assert "Owner" in by_key[key].consumer


class TestRunDslRules:
    def test_block_rule_intercepts(self):
        # op=gt value=0 → "price 必须 > 0"（违规=price<=0），真源=config/cleaning_rules.yaml close_positive 同语义
        specs = [{"name": "px_positive", "field": "price", "op": "gt", "value": 0, "action": "block"}]
        rows = [
            {"symbol": "A", "price": 10.0},
            {"symbol": "B", "price": -1.0},  # 违规→拦截
        ]
        clean, stats = run_dsl_rules(rows, specs, table="t1")
        assert stats["total"] == 2
        assert stats["intercepted"] == 1
        assert len(clean) == 1
        assert clean[0]["symbol"] == "A"

    def test_lt_cap_rule_flags_above_cap(self):
        # op=lt value=100 → "close 必须 < 100"（违规=close>=100），close_cap 上限语义
        specs = [{"name": "close_cap", "field": "close", "op": "lt", "value": 100, "action": "flag"}]
        _, stats = run_dsl_rules([{"close": 50.0}, {"close": 200.0}], specs, table="t2")
        assert stats["flagged"] == 1
        assert stats["intercepted"] == 0  # flag 动作只打标不剔除

    def test_invalid_spec_raises(self):
        with pytest.raises(Exception):  # CleaningRuleError——DSL 非法 fail-closed
            run_dsl_rules([{"price": 1.0}], [{"name": "bad", "field": "price", "op": "nope", "value": 1}])


class TestDetectFrameAnomalies:
    def test_clean_frame_empty_findings(self):
        df = pd.DataFrame(
            {
                "close": [10.0, 10.1, 10.2, 10.1],
                "volume": [100.0, 110.0, 105.0, 108.0],
            }
        )
        findings = detect_frame_anomalies(df, symbol="600000.SH")
        assert findings == []

    def test_price_jump_detected(self):
        df = pd.DataFrame(
            {
                "close": [10.0, 10.0, 15.0, 15.0],  # +50% 单根跳变
                "volume": [100.0, 100.0, 100.0, 100.0],
            }
        )
        findings = detect_frame_anomalies(df, symbol="600000.SH")
        assert any(f.rule == "price_jump" for f in findings)


class TestValidateExpectations:
    def test_schema_expectations_pass_and_fail(self):
        from zephyr.data_eng.expectation_governance import Expectation, ExpectationGovernance

        gov = ExpectationGovernance()
        exps = [
            Expectation(type="schema", column="close"),
            Expectation(type="not_null", column="volume"),
        ]
        ok_df = pd.DataFrame({"close": [1.0, 2.0], "volume": [10.0, 20.0]})
        report = validate_expectations(ok_df, exps, suite_name="t")
        assert report.verdict.value == "ok"

        bad_df = pd.DataFrame({"close": [1.0, None], "volume": [10.0, None]})
        report2 = validate_expectations(bad_df, exps, suite_name="t")
        assert report2.verdict.value != "ok"

    def test_unknown_expectation_type_raises(self):
        from zephyr.data_eng.expectation_governance import Expectation

        df = pd.DataFrame({"a": [1.0]})
        with pytest.raises(ValueError, match="未知"):
            validate_expectations(df, [Expectation(type="nope", column="a")])


class TestEvaluateAnomalySignals:
    def test_signals_graded_and_events_emitted(self):
        from datetime import datetime, timezone

        from zephyr.data_eng.data_anomaly_alerter import AnomalyKind, AnomalySignal

        sig = AnomalySignal(
            kind=AnomalyKind.MISSING_RATE,
            symbol="600000.SH",
            metric_value=0.5,
            threshold=0.1,
            detail="missing 50%",
        )
        routed: list[tuple] = []
        alerts, events = evaluate_anomaly_signals(
            [sig],
            now_utc=datetime.now(timezone.utc),
            source="test",
            alert_sink=lambda *a, **kw: routed.append((a, kw)) or True,
        )
        assert len(alerts) == 1
        assert alerts[0].grade.value in ("AL-P1", "AL-P2", "AL-P3", "AL-P4")
        assert len(events) == 1
        assert events[0].kind == AnomalyKind.MISSING_RATE


class TestAiAdjudicateGate:
    def test_ai_adjudicate_fail_closed(self):
        """C6 接口位：调用即抛 OwnerGate（花钱点禁自作主张）。"""
        with pytest.raises(AiAdjudicationPendingOwnerGateError, match="OWNER-GATE"):
            ai_adjudicate([{"finding": "x"}], requested_by="test")

    def test_ai_adjudicate_zero_findings_still_gate(self):
        with pytest.raises(AiAdjudicationPendingOwnerGateError):
            ai_adjudicate([])
