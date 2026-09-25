# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §budget_analyzer
# [MODULE] tests.intelligence.test_budget_analyzer
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.intelligence.budget_analyzer（纯函数+CLI）；tests/intelligence 常规 pytest 栈
# [CONSUMERS] pytest / CI（TRANSLATION-COVERAGE 等本地 gate 体系）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 全部走纯函数与注入通道（records 注入/fake alerter 模块注入），零生产 DB 读、零真实外呼、零生产路径写；
#              阈值恰好等于阈值=触发（≥语义）与四档全枚举为本测试的验收锚点（DESIGN §6.4）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §6
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；emit_alerts 降级路径以 sys.modules 置 None 强制 ImportError（不写任何失败汇总文件）
# [TESTS] tests/intelligence/test_budget_analyzer.py（自指）
# [TTL] permanent
"""budget_analyzer 单元测试（OBJ_M M5 / C7，DESIGN §6）。

覆盖：predicted_30d 两窗公式（已知序列精确值+数据不足降级）/ burn_rate 两窗与非法窗口 /
budget_verdict 四档全枚举（恰好等于阈值=触发）与零告警 / recharge_advice（余额充足不建议·
缺口×1.2·余额 0 立即）/ free_window_savings 零差价 / analyze 组装字段齐 /
render_budget_advisory_payload 无按钮类字段+直达链接是文本字段 / emit_alerts 正常派发与
ImportError 降级 / CLI --demo 与 --report fail-closed（退出码 2）。
"""

from __future__ import annotations

import json
import sys
import types

import pytest

import zephyr.intelligence.budget_analyzer as ba
from zephyr.intelligence.budget_analyzer import (
    BudgetAnalyzerError,
    DEFAULT_THRESHOLDS,
    analyze,
    budget_verdict,
    burn_rate,
    emit_alerts,
    free_window_savings,
    load_daily_usage,
    main,
    predicted_30d,
    recharge_advice,
    render_budget_advisory_payload,
)


def _day(date: str, usd: float) -> dict:
    return {"date": date, "usd": usd, "tokens_in": 100, "tokens_out": 50}


def _seq(prefix: str, n: int, usd: float) -> list[dict]:
    return [_day(f"{prefix}-{i:02d}", usd) for i in range(1, n + 1)]


def _known_30d() -> list[dict]:
    """已知序列：14 天@0.5 + 9 天@1.0 + 7 天@2.0 → 总和恰 30，mean30=1.0 / mean7=2.0 精确可断言。"""
    return _seq("a", 14, 0.5) + _seq("b", 9, 1.0) + _seq("c", 7, 2.0)


class TestPredicted30d:
    def test_two_window_formula_exact(self):
        daily = _known_30d()  # mean7=2.0 / mean30=1.0 → 0.5×2+0.5×1=1.5
        assert predicted_30d(daily) == pytest.approx(1.5)

    def test_insufficient_days_degrades_to_available_mean(self):
        daily = _seq("2026-09", 5, 3.0)  # 不足 7 天：两窗都用现有 5 天均值
        assert predicted_30d(daily) == pytest.approx(3.0)

    def test_empty_returns_zero(self):
        assert predicted_30d([]) == 0.0


class TestBurnRate:
    def test_two_windows(self):
        daily = _known_30d()
        assert burn_rate(daily, 7) == pytest.approx(2.0)
        assert burn_rate(daily, 30) == pytest.approx(1.0)

    def test_empty_returns_zero(self):
        assert burn_rate([], 7) == 0.0

    def test_invalid_window_rejected(self):
        with pytest.raises(ValueError, match="two-window"):
            burn_rate(_seq("2026-09", 3, 1.0), 1)  # B14：1d 短窗不施工


class TestBudgetVerdict:
    @pytest.mark.parametrize(
        ("predicted", "expected_tiers"),
        [
            (5.0, ["notify"]),  # 恰好=50% → 触发 notify（≥语义）
            (7.0, ["notify", "warning"]),  # 恰好=70%
            (8.0, ["notify", "warning", "model_switch"]),  # 恰好=80%
            (10.0, ["notify", "warning", "model_switch", "halt"]),  # 恰好=100% 全档
            (1.0, []),  # 零告警
        ],
    )
    def test_thresholds_boundary_enumeration(self, predicted, expected_tiers):
        verdicts = budget_verdict(predicted, 10.0, dict(DEFAULT_THRESHOLDS))
        assert [v["tier"] for v in verdicts] == expected_tiers

    def test_levels_increase_across_tiers(self):
        verdicts = budget_verdict(10.0, 10.0, dict(DEFAULT_THRESHOLDS))
        levels = [v["level"] for v in verdicts]
        assert levels == sorted(levels) == [1, 2, 3, 4]

    def test_custom_thresholds_override(self):
        verdicts = budget_verdict(5.0, 10.0, {"notify": 0.6, "warning": 0.7, "model_switch": 0.8, "halt": 1.0})
        assert verdicts == []

    def test_non_positive_limit_rejected(self):
        with pytest.raises(ValueError, match="daily_limit"):
            budget_verdict(5.0, 0.0, dict(DEFAULT_THRESHOLDS))


class TestRechargeAdvice:
    def test_sufficient_balance_no_advice(self):
        out = recharge_advice(100.0, 1.0)  # 缺口=7×1−100<0
        assert out["advise"] is False
        assert out["days_to_depletion"] == 100.0
        assert out["suggested_topup_usd"] == 0.0

    def test_gap_times_safety_factor(self):
        out = recharge_advice(5.0, 1.0)  # 缺口=7−5=2 → 建议 2×1.2=2.4
        assert out["advise"] is True
        assert out["days_to_depletion"] == 5.0
        assert out["suggested_topup_usd"] == pytest.approx(2.4)
        assert isinstance(out["link_text"], str) and out["link_text"].startswith("https://")

    def test_zero_balance_immediate(self):
        out = recharge_advice(0.0, 1.0)
        assert out["advise"] is True
        assert out["days_to_depletion"] == 0.0
        assert out["suggested_topup_usd"] == pytest.approx(8.4)  # 7×1×1.2

    def test_no_burn_no_urgency(self):
        out = recharge_advice(50.0, 0.0)
        assert out["advise"] is False
        assert out["days_to_depletion"] is None


class TestFreeWindowSavings:
    def test_zero_price_is_zero(self):
        routes = [{"model": "deepseek-chat", "migratable_tokens": 100_000}]
        assert free_window_savings(routes, {"deepseek-chat": 0.0}) == 0.0

    def test_empty_inputs_zero(self):
        assert free_window_savings([], {"m": 1.0}) == 0.0
        assert free_window_savings([{"model": "m", "migratable_tokens": 1}], None) == 0.0

    def test_normal_summation(self):
        routes = [
            {"model": "deepseek-chat", "migratable_tokens": 100_000},
            {"model": "glm-4", "migratable_tokens": 50_000},
        ]
        pricing = {"deepseek-chat": 0.001, "glm-4": 0.002}  # USD / 1k tokens
        assert free_window_savings(routes, pricing) == pytest.approx(0.1 + 0.1)

    def test_unknown_model_skipped(self):
        routes = [{"model": "unknown-model", "migratable_tokens": 999_999}]
        assert free_window_savings(routes, {"deepseek-chat": 0.001}) == 0.0


class TestLoadDailyUsage:
    def test_records_injection_normalizes_and_sorts(self):
        records = [
            {"date": "2026-09-02", "usd": "2.5", "tokens_in": "10", "tokens_out": "5"},
            {"date": "2026-09-01", "usd": 1.5, "tokens_in": 8, "tokens_out": 4},
        ]
        daily = load_daily_usage(30, records=records)  # 注入通道：零 DB 依赖
        assert [r["date"] for r in daily] == ["2026-09-01", "2026-09-02"]  # 升序
        assert daily[0] == {"date": "2026-09-01", "usd": 1.5, "tokens_in": 8, "tokens_out": 4}

    def test_record_missing_date_rejected(self):
        with pytest.raises(ValueError, match="missing date"):
            load_daily_usage(7, records=[{"usd": 1.0}])

    def test_non_positive_days_rejected(self):
        with pytest.raises(ValueError, match="days"):
            load_daily_usage(0, records=[])


class TestAnalyze:
    def test_report_fields_assembled(self):
        daily = _known_30d()
        report = analyze(daily, daily_limit=10.0, thresholds=dict(DEFAULT_THRESHOLDS), balance_usd=5.0)
        for key in ("date", "daily_usd", "predicted_30d", "burn_7d", "burn_30d", "alerts", "recharge", "free_savings"):
            assert key in report
        assert report["predicted_30d"] == pytest.approx(1.5)
        assert report["daily_usd"] == pytest.approx(2.0)
        assert report["recharge"]["advise"] is True
        assert report["subscription_quota_used"] is None  # 缺省 None（订阅线不折美元）
        assert report["generated_at"].endswith("+00:00") or "T" in report["generated_at"]

    def test_subscription_quota_passthrough(self):
        report = analyze(_seq("2026-09", 3, 1.0), subscription_quota_used=0.42)
        assert report["subscription_quota_used"] == pytest.approx(0.42)

    def test_insufficient_sample_note(self):
        report = analyze(_seq("2026-09", 5, 3.0))
        assert report["sample_days"] == 5
        assert report["predicted_note"] is not None and "5" in report["predicted_note"]

    def test_balance_unavailable_marks_reason(self):
        report = analyze(_seq("2026-09", 10, 1.0), balance_usd=None)
        assert report["recharge"] == {
            "advise": False,
            "reason": "balance_unavailable",
            "suggested_topup_usd": 0.0,
        }


class TestRenderPayload:
    PAYLOAD = render_budget_advisory_payload(
        analyze(_seq("2026-08", 23, 1.0) + _seq("2026-09", 7, 2.0), balance_usd=5.0)
    )

    def test_no_button_like_fields(self):
        forbidden = ("button", "form", "submit", "onclick", "action_url", "endpoint")

        def _scan(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    assert not any(tok in str(k).lower() for tok in forbidden), f"按钮类字段: {k}"
                    _scan(v)
            elif isinstance(node, list):
                for item in node:
                    _scan(item)

        _scan(self.PAYLOAD)
        assert self.PAYLOAD["readonly"] is True

    def test_direct_links_are_text_fields(self):
        assert self.PAYLOAD["links"], "至少一条直达链接"
        for link in self.PAYLOAD["links"]:
            assert link["kind"] == "text"
            assert isinstance(link["url_text"], str) and link["url_text"].startswith("https://")
            assert "href" not in link and "action" not in link

    def test_json_safe_roundtrip(self):
        text = json.dumps(self.PAYLOAD, ensure_ascii=False)
        assert json.loads(text)["date"] == self.PAYLOAD["date"]


class TestEmitAlerts:
    @staticmethod
    def _report_with_halt() -> dict:
        return {
            "date": "2026-09-23",
            "predicted_30d": 10.0,
            "daily_limit_usd": 10.0,
            "alerts": [
                {"tier": "notify", "level": 1, "ratio": 1.0, "threshold": 0.5, "action": "INFO 通知+建议"},
                {"tier": "halt", "level": 4, "ratio": 1.0, "threshold": 1.0, "action": "CRITICAL+建议暂停非关键 API"},
            ],
        }

    def test_no_error_plus_alerts_dispatches_nothing(self):
        report = {"alerts": [{"tier": "notify", "level": 1, "ratio": 0.5, "threshold": 0.5, "action": "x"}]}
        assert emit_alerts(report) == 0

    def test_dispatches_to_alerter(self, monkeypatch):
        calls: list[tuple[str, str]] = []

        class FakeAlerter:
            def notify(self, *, task_id, error, level="ERROR", source=None, extra=None):
                calls.append((task_id, level))
                return True

        fake = types.ModuleType("zephyr.data.alerter")
        fake.Alerter = FakeAlerter  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "zephyr.data.alerter", fake)
        try:
            assert emit_alerts(self._report_with_halt()) == 1  # 仅 halt（ERROR+）派发
            assert calls == [("budget_analyzer", "CRITICAL")]
        finally:
            sys.modules.pop("zephyr.data.alerter", None)  # 当下自清（#ARCH-107 污染探针要求）

    def test_import_error_degrades_without_raising(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "zephyr.data.alerter", None)  # 强制 ImportError
        try:
            assert emit_alerts(self._report_with_halt()) == 1  # 降级仅日志，仍计入已处理且不炸
        finally:
            sys.modules.pop("zephyr.data.alerter", None)  # 当下自清（#ARCH-107 污染探针要求）


class TestCli:
    def test_demo_outputs_report_without_db(self, capsys):
        rc = main(["--demo"])
        out = capsys.readouterr().out
        assert rc == 0
        data = json.loads(out)
        assert data["sample_days"] == 30
        assert "predicted_30d" in data and "alerts" in data

    def test_report_fail_closed_exit_2(self, monkeypatch, capsys):
        def _boom(days, *, records=None):
            raise BudgetAnalyzerError("db unreachable")

        monkeypatch.setattr(ba, "load_daily_usage", _boom)
        rc = main(["--report"])
        captured = capsys.readouterr()
        assert rc == 2
        assert json.loads(captured.err)["ok"] is False
        assert captured.out == ""  # 绝不编造报告
