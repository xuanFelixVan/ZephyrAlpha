# [MODULE] tests.zephyr.data.test_cleaning_expectation_hosting
# [DOMAIN] D_DATA
"""期望门控+信号告警托管腿测试（R-M1-06 逐引擎接线收口台，同族两腿口径）。

判"已防护"的标准：
  ①谁调它 —— test_wired_into_supply_sentinel_leg / test_host_leg_delegates_to_real_gate
  ②能否改变行为 —— test_changing_yaml_expectation_changes_behavior（改 YAML 即改判定，
    判据值不在代码里）/ test_price_jump_signal_routed_through_engine
  ③故障时是否 fail-closed —— test_red_missing_yaml_fail_closed / 畸形册参数化 /
    单表降级不冒绿 / all_degraded 永不报干净
测试零生产外呼（executor/alerter 全假件）、零生产路径写（report_dir/out_dir 全 tmp_path）。
"""
# [TTL] permanent
# [STARTUP] manual

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data import cleaning_expectation_hosting as ceh
from zephyr.data import supply_sentinel as ss
from zephyr.data.cleaning_expectation_hosting import (
    ENGINE_SLOTS_WIRED,
    ExpectationGateConfigError,
    ExpectationGateRunOptions,
    gate_status,
    load_rulebook,
    run_expectation_gate,
    run_hosted_expectation_gate,
)

TABLE = "c1_market.daily_valuation"


def _today() -> date:
    """测试基准日=本地今日（freshness 期望配引擎本地钟，样本取近窗动态日期防钟漂红）。"""
    return date.today()


class RecordingAlerter:
    """告警假通道（禁写生产 data/ 告警目录）。"""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def notify(
        self, task_id: str, error: str, level: str = "ERROR", source: str | None = None, extra: dict | None = None
    ) -> bool:
        self.messages.append((level, error))
        return True


class FakeSampleExecutor:
    """CH 只读假执行器：无参查询回表样本，带 symbol 参数查询回该标的序列（测试禁触生产库）。"""

    def __init__(
        self,
        sample: list[tuple[Any, ...]],
        series: dict[str, list[tuple[Any, ...]]],
        *,
        fail_symbols: set[str] | None = None,
    ) -> None:
        self._sample = sample
        self._series = series
        self._fail_symbols = fail_symbols or set()
        self.queries: list[str] = []

    def execute(self, sql: str, parameters: dict | None = None) -> list:
        self.queries.append(sql)
        if parameters is None:
            return list(self._sample)
        symbol = str(parameters.get("symbol"))
        if symbol in self._fail_symbols:
            raise RuntimeError("CH 不可达（测试注入）")
        return list(self._series.get(symbol, []))


def _dates(count: int) -> list[date]:
    today = _today()
    return [today - timedelta(days=count - 1 - i) for i in range(count)]


def _gentle_closes(count: int = 30) -> list[float]:
    """温和序列（交替微噪声+末位归零：零跳变，供干净基准）。"""
    return [10.0 + (0.1 if i % 2 else -0.1) for i in range(count - 1)] + [10.0]


def _jump_closes(count: int = 30) -> list[float]:
    """跳变序列（同款微噪声史+末日 2.5x 跳变：z 远超阈）。"""
    base = _gentle_closes(count)
    base[-1] = 25.0
    return base


def make_sample(symbols: list[str], close: float = 10.0) -> list[tuple[Any, ...]]:
    """表样本行组（每标的 1 行近窗样本；列面=trade_date/symbol/close）。"""
    today = _today()
    return [(today.isoformat(), sym, close) for sym in symbols]


def make_series(symbol: str, closes: list[float]) -> list[tuple[Any, ...]]:
    """标的序列行组（列面=trade_date/close/volume，日期升序近窗）。"""
    dates = _dates(len(closes))
    return [(d.isoformat(), c, 100.0) for d, c in zip(dates, closes, strict=True)]


def write_carrier(
    tmp_path: Path,
    *,
    wiring: dict[str, Any] | None = None,
    alerter: dict[str, Any] | None = None,
    expectations: list[dict[str, Any]] | None = None,
    targets: list[dict[str, Any]] | None = None,
    report_dir: Path | None = None,
) -> Path:
    """畸形案/红测共用承载册工厂（缺省=合法最小册）。"""
    doc: dict[str, Any] = {
        "schema_version": 1,
        "wiring": {
            "enabled": True,
            "host_schedule": "data_supply_sentinel",
            "cadence_days": 1,
            "read_limit_rows": 2000,
            "rows_per_symbol": 60,
            "watchlist_size": 10,
            "alert_level": "warn",
            "report_dir": str(report_dir or (tmp_path / "reports")),
            "disabled_flag": str(tmp_path / "off.flag"),
        },
        "alerter": {"z_threshold": 4.0, "window": 20, "missing_warn": 0.05},
        "expectations": expectations
        if expectations is not None
        else [
            {"type": "not_null", "column": "close", "severity": "warn"},
            {"type": "range", "column": "close", "params": {"min": 0}, "severity": "warn"},
            {"type": "freshness", "column": "trade_date", "params": {"max_age_hours": 48}, "severity": "warn"},
        ],
        "targets": targets
        if targets is not None
        else [
            {
                "table": TABLE,
                "date_col": "trade_date",
                "symbol_col": "symbol",
                "lookback_days": 30,
                "frame_cols": ["close", "volume"],
                "check_cols": ["close"],
                "expected_rows": 0,
            }
        ],
    }
    if wiring:
        doc["wiring"].update(wiring)
    if alerter:
        doc["alerter"].update(alerter)
    if expectations is not None:
        doc["expectations"] = expectations
    if targets is not None:
        doc["targets"] = targets
    path = tmp_path / "carrier.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# ①谁调它
# ---------------------------------------------------------------------------


def test_wired_into_supply_sentinel_leg(monkeypatch: pytest.MonkeyPatch) -> None:
    """宿主 run_supply_sentinel 必须真的调用本腿（不接=又一枚"建了没接"）。"""
    calls: list[str] = []
    monkeypatch.setattr(
        ss, "check_tables", lambda: {"checked": 0, "breached": 0, "heartbeat_blind": 0, "ok": True, "blind_spots": []}
    )
    monkeypatch.setattr(ss, "_alert_breaches", lambda alerter, summary: None)
    monkeypatch.setattr(ss, "_run_hosted_quality_sweep", lambda alerter: {"ok": True})
    monkeypatch.setattr(ss, "_run_hosted_cleaning_gate", lambda alerter: {"ok": True})
    monkeypatch.setattr(ss, "_run_hosted_anomaly_gate", lambda alerter: {"ok": True})
    monkeypatch.setattr(
        ss,
        "_run_hosted_expectation_gate",
        lambda alerter: calls.append("called") or {"ok": True, "status": "ran_and_clean"},
    )
    summary = ss.run_supply_sentinel(alerter=RecordingAlerter())
    assert calls == ["called"], "期望门控未接到宿主排班腿=接线未成立"
    assert summary["expectation_gate"]["ok"] is True


def test_host_leg_delegates_to_real_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    """宿主托管函数必须把实调宿主槽位名交给承载册（host 不符即配置错，防册里挂空宿主）。"""
    seen: dict[str, Any] = {}

    def fake_gate(alerter=None, *, host_schedule=None, **kwargs):
        seen["host_schedule"] = host_schedule
        return {"ok": True, "status": "ran_and_clean"}

    monkeypatch.setattr(ceh, "run_hosted_expectation_gate", fake_gate)
    out = ss._run_hosted_expectation_gate(RecordingAlerter())
    assert seen["host_schedule"] == "data_supply_sentinel"
    assert out["ok"] is True


def test_host_mismatch_is_config_error(tmp_path: Path) -> None:
    """承载册声明宿主 ≠ 实调宿主 → fail-closed（不许"册里挂了别的宿主"蒙混上岗）。"""
    carrier = write_carrier(tmp_path, wiring={"host_schedule": "some_other_slot"})
    out = run_hosted_expectation_gate(
        RecordingAlerter(),
        config_path=carrier,
        executor=FakeSampleExecutor([], {}),
        ref_date=_today(),
        force=True,
    )
    assert out["ok"] is False and "config_error" in out


# ---------------------------------------------------------------------------
# ②能否改变行为（判据真源=YAML）
# ---------------------------------------------------------------------------


def test_changing_yaml_expectation_changes_behavior(tmp_path: Path) -> None:
    """同数据同执行器，只改承载册期望参数：min 0→-100，range 失败由 1→0（判据在册非在码）。"""
    symbols = ["000001"]
    sample = make_sample(symbols, close=-5.0)  # 越界行（close<0）
    series = {s: make_series(s, _gentle_closes()) for s in symbols}
    executor = FakeSampleExecutor(sample, series)

    def run(carrier: Path) -> dict:
        wiring, params, expectations, targets = load_rulebook(carrier)
        return run_expectation_gate(
            wiring,
            params,
            expectations,
            targets,
            ExpectationGateRunOptions(executor=executor, ref_date=_today(), notify=False),
        )

    red = run(write_carrier(tmp_path / "red"))
    assert red["results"][0]["expectation_verdict"] == "warn"
    failed_cols = [f["column"] for f in red["results"][0]["expectation_failed"]]
    assert "close" in failed_cols and red["findings_count"] >= 1
    green = run(
        write_carrier(
            tmp_path / "green",
            expectations=[
                {"type": "not_null", "column": "close", "severity": "warn"},
                {"type": "range", "column": "close", "params": {"min": -100}, "severity": "warn"},
                {"type": "freshness", "column": "trade_date", "params": {"max_age_hours": 48}, "severity": "warn"},
            ],
        )
    )
    green_failed = [f["column"] for f in green["results"][0]["expectation_failed"]]
    assert "close" not in green_failed, "只改册未改码，判定必须随册变（判据真源=YAML）"


def test_price_jump_signal_routed_through_engine(tmp_path: Path) -> None:
    """末日跳变序列 → 引擎分级路由 → alert_sink（宿主假通道）实收，findings 计数。"""
    symbols = ["000001"]
    sample = make_sample(symbols)
    series = {s: make_series(s, _jump_closes()) for s in symbols}
    alerter = RecordingAlerter()
    wiring, params, expectations, targets = load_rulebook(write_carrier(tmp_path))
    report = run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(executor=FakeSampleExecutor(sample, series), alerter=alerter, ref_date=_today()),
    )
    alerts = report["results"][0]["alerts"]
    assert alerts and alerts[0]["kind"] == "price_jump", "跳变信号未过引擎分级路由=告警腿假接"
    assert alerts[0]["grade"] in {"AL-P1", "AL-P2", "AL-P3", "AL-P4"}
    assert report["status"] == "ran_with_findings" and report["findings_count"] >= 1


def test_missing_rate_signal_when_expected_declared(tmp_path: Path) -> None:
    """expected_rows 在册且缺口超阈 → missing_rate 信号；未声明（0）→ 不硬造期望。"""
    symbols = ["000001"]
    sample = make_sample(symbols)
    short_series = {s: make_series(s, _gentle_closes(22)) for s in symbols}  # 22 行 << expected 50
    wiring, params, expectations, targets = load_rulebook(
        write_carrier(
            tmp_path,
            targets=[
                {
                    "table": TABLE,
                    "date_col": "trade_date",
                    "symbol_col": "symbol",
                    "lookback_days": 30,
                    "frame_cols": ["close", "volume"],
                    "check_cols": ["close"],
                    "expected_rows": 50,
                }
            ],
        )
    )
    report = run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(executor=FakeSampleExecutor(sample, short_series), ref_date=_today(), notify=False),
    )
    kinds = {a["kind"] for a in report["results"][0]["alerts"]}
    assert "missing_rate" in kinds


# ---------------------------------------------------------------------------
# ③诚实四态与 fail-closed
# ---------------------------------------------------------------------------


def test_gate_status_four_states() -> None:
    """四态判序：降级优先于命中，命中优先于干净，空批=not_run。"""
    assert gate_status([]) == "not_run"
    assert gate_status([{"degraded": False, "no_samples": False, "findings_count": 0}]) == "ran_and_clean"
    assert gate_status([{"degraded": False, "no_samples": False, "findings_count": 2}]) == "ran_with_findings"
    assert gate_status([{"degraded": True, "no_samples": False, "findings_count": 0}]) == "degraded_partial"
    assert gate_status([{"degraded": False, "no_samples": True, "findings_count": 0}]) == "degraded_partial"


def test_all_symbols_failing_never_reports_clean(tmp_path: Path) -> None:
    """全标的取数失败=巡检未生效 ok=False（禁谎报绿，同族 all_degraded 防线）。"""
    symbols = ["000001", "000002"]
    sample = make_sample(symbols)
    series = {s: make_series(s, _gentle_closes()) for s in symbols}
    wiring, params, expectations, targets = load_rulebook(write_carrier(tmp_path))
    report = run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(
            executor=FakeSampleExecutor(sample, series, fail_symbols=set(symbols)), ref_date=_today(), notify=False
        ),
    )
    assert report["status"] == "degraded_partial" and report["all_degraded"] is True


def test_uncovered_expectation_disclosed_not_clean(tmp_path: Path) -> None:
    """期望列未进取数面=uncovered 如实披露（未检非干净，禁冒"检过"）。"""
    symbols = ["000001"]
    sample = make_sample(symbols)
    series = {s: make_series(s, _gentle_closes()) for s in symbols}
    wiring, params, expectations, targets = load_rulebook(
        write_carrier(tmp_path, expectations=[{"type": "not_null", "column": "amount", "severity": "warn"}])
    )
    report = run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(executor=FakeSampleExecutor(sample, series), ref_date=_today(), notify=False),
    )
    assert report["results"][0]["expectation_uncovered"] == ["amount"]
    assert report["results"][0]["expectation_failed"] == []


def test_leg_only_reads(tmp_path: Path) -> None:
    """只读不修：本腿发出的每条 SQL 都是 SELECT（读侧 flag 档承诺，写路径零接触）。"""
    symbols = ["000001"]
    executor = FakeSampleExecutor(make_sample(symbols), {s: make_series(s, _gentle_closes()) for s in symbols})
    wiring, params, expectations, targets = load_rulebook(write_carrier(tmp_path))
    run_expectation_gate(
        wiring,
        params,
        expectations,
        targets,
        ExpectationGateRunOptions(executor=executor, ref_date=_today(), notify=False),
    )
    assert executor.queries and all(q.lstrip().upper().startswith("SELECT") for q in executor.queries)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda doc: doc.pop("wiring"), id="missing_wiring"),
        pytest.param(lambda doc: doc.pop("alerter"), id="missing_alerter"),
        pytest.param(lambda doc: doc.update({"expectations": []}), id="empty_expectations"),
        pytest.param(lambda doc: doc.update({"targets": []}), id="empty_targets"),
        pytest.param(lambda doc: doc["wiring"].update({"unknown_key": 1}), id="unknown_wiring_key"),
        pytest.param(lambda doc: doc["wiring"].update({"cadence_days": 0}), id="cadence_zero"),
        pytest.param(lambda doc: doc["wiring"].update({"read_limit_rows": -1}), id="read_limit_negative"),
        pytest.param(lambda doc: doc["alerter"].update({"window": 0}), id="window_zero"),
        pytest.param(lambda doc: doc["alerter"].update({"z_threshold": -1}), id="z_negative"),
        pytest.param(
            lambda doc: doc.update({"expectations": [{"type": "no_such", "column": "close"}]}), id="unknown_type"
        ),
        pytest.param(
            lambda doc: doc.update({"expectations": [{"type": "range", "column": "close", "severity": "burn"}]}),
            id="bad_severity",
        ),
        pytest.param(lambda doc: doc["targets"][0].update({"table": "1m; DROP TABLE x"}), id="sql_injection_table"),
        pytest.param(lambda doc: doc["targets"][0].update({"frame_cols": []}), id="empty_frame_cols"),
    ],
)
def test_malformed_carriers_fail_closed(tmp_path: Path, mutate) -> None:
    """畸形册参数化：一切非法在解析期炸（fail-closed，绝不默认放行）。"""
    carrier = write_carrier(tmp_path)
    doc = yaml.safe_load(carrier.read_text(encoding="utf-8"))
    mutate(doc)
    bad = tmp_path / "bad.yaml"
    bad.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ExpectationGateConfigError):
        load_rulebook(bad)


def test_red_missing_yaml_fail_closed(tmp_path: Path) -> None:
    """缺册：托管腿 ok=False + ERROR 出声，绝不回 ok=True。"""
    alerter = RecordingAlerter()
    out = run_hosted_expectation_gate(
        alerter, config_path=tmp_path / "nope.yaml", executor=FakeSampleExecutor([], {}), force=True
    )
    assert out["ok"] is False and out["not_run_reason"] == "config_error"
    assert any(level == "ERROR" for level, _ in alerter.messages)


# ---------------------------------------------------------------------------
# ④出厂真册自检 + 引擎面台账
# ---------------------------------------------------------------------------


def test_shipped_carrier_loads_and_declares_engine_slots() -> None:
    """出厂真册自检：真 config/cleaning_expectations.yaml 必须能加载，且四台台账在案。"""
    wiring, params, expectations, targets = load_rulebook(None)
    assert wiring.host_schedule == "data_supply_sentinel"
    assert wiring.enabled is True
    assert params.z_threshold > 0 and params.window >= 2
    assert expectations and targets
    assert targets[0].table == TABLE
    assert set(ENGINE_SLOTS_WIRED) == {
        "cleaning_rule_engine",
        "cleaning_anomaly_engine",
        "expectation_governance",
        "data_anomaly_alerter",
    }


def test_shipped_carrier_runs_clean_on_gentle_data(tmp_path: Path) -> None:
    """出厂真册配温和数据真跑：ran_and_clean 且 ok=True（防 fixture 绿而出厂册坏）。"""
    symbols = ["000001"]
    executor = FakeSampleExecutor(make_sample(symbols), {s: make_series(s, _gentle_closes()) for s in symbols})
    out = run_hosted_expectation_gate(
        RecordingAlerter(), executor=executor, report_dir=tmp_path / "reports", ref_date=_today(), force=True
    )
    assert out["ok"] is True and out["status"] == "ran_and_clean"
