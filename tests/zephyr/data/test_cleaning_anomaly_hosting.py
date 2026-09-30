# [MODULE] tests.zephyr.data.test_cleaning_anomaly_hosting
# [DOMAIN] D_DATA
"""清洗异常引擎托管腿测试（R-M1-06 逐引擎接线第二台反证三件，同族 cleaning_rules_hosting 口径）。

判"已防护"的标准：
  ①谁调它 —— test_wired_into_supply_sentinel_leg / test_host_leg_delegates_to_real_gate
  ②能否改变行为 —— test_changing_yaml_threshold_changes_behavior（改 YAML 即改判定，
    判据值不在代码里）
  ③故障时是否 fail-closed —— test_red_missing_yaml_fail_closed / 畸形册参数化 /
    单标的降级不冒绿
测试零生产外呼（executor/alerter 全假件）、零生产路径写（report_dir/out_dir 全 tmp_path）。
"""
# [TTL] permanent
# [STARTUP] manual

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml

from zephyr.data import cleaning_anomaly_hosting as cah
from zephyr.data import supply_sentinel as ss
from zephyr.data.cleaning_anomaly_hosting import (
    ENGINE_SLOTS_RESERVED,
    ENGINE_SLOTS_WIRED,
    AnomalyGateConfigError,
    GateRunOptions,
    gate_status,
    load_anomaly_rulebook,
    run_anomaly_gate,
    run_hosted_anomaly_gate,
)

REF = date(2026, 9, 28)
TABLE = "c1_market.daily_valuation"


class RecordingAlerter:
    """告警假通道（禁写生产 data/ 告警目录）。"""

    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def notify(
        self, task_id: str, error: str, level: str = "ERROR", source: str | None = None, extra: dict | None = None
    ) -> bool:
        self.messages.append((level, error))
        return True


class FakeFrameExecutor:
    """CH 只读假执行器：DISTINCT 查询回标的清单，帧查询回该标的行组（测试禁触生产库）。"""

    def __init__(self, frames: dict[str, list[tuple[Any, ...]]], *, fail_symbols: set[str] | None = None) -> None:
        self._frames = frames
        self._fail_symbols = fail_symbols or set()
        self.queries: list[str] = []

    def execute(self, sql: str, parameters: dict | None = None) -> list:
        self.queries.append(sql)
        if sql.lstrip().upper().startswith("SELECT DISTINCT"):
            import re as _re

            m = _re.search(r"LIMIT\s+(\d+)", sql, flags=_re.IGNORECASE)
            limit = int(m.group(1)) if m else len(self._frames)
            return [[s] for s in sorted(self._frames)[:limit]]
        assert parameters and "symbol" in parameters, "帧查询必须带 symbol 参数"
        symbol = str(parameters["symbol"])
        if symbol in self._fail_symbols:
            raise RuntimeError("CH 不可达（测试注入）")
        return list(self._frames.get(symbol, []))


def _rows(closes: list[float], volumes: list[float] | None = None) -> list[tuple[Any, ...]]:
    vols = volumes or [100.0] * len(closes)
    return [(f"2026-09-{i + 1:02d}", c, v) for i, (c, v) in enumerate(zip(closes, vols, strict=True))]


def write_carrier(
    tmp_path: Path,
    *,
    wiring: dict[str, Any] | None = None,
    engines: dict[str, Any] | None = None,
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
            "rows_per_symbol": 60,
            "watchlist_size": 10,
            "alert_level": "warn",
            "report_dir": str(report_dir or (tmp_path / "reports")),
            "disabled_flag": str(tmp_path / "off.flag"),
        },
        "engines": {
            "price_jump_pct": 0.20,
            "price_jump_z": 8.0,
            "volume_spike_mult": 20.0,
            "volume_z": 6.0,
        },
        "targets": [
            {
                "table": TABLE,
                "date_col": "trade_date",
                "symbol_col": "symbol",
                "lookback_days": 30,
                "frame_cols": ["close", "volume"],
            },
        ],
    }
    if wiring:
        doc["wiring"].update(wiring)
    if engines:
        doc["engines"].update(engines)
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
    monkeypatch.setattr(
        ss,
        "_run_hosted_anomaly_gate",
        lambda alerter: calls.append("called") or {"ok": True, "status": "ran_and_clean"},
    )
    summary = ss.run_supply_sentinel(alerter=RecordingAlerter())
    assert calls == ["called"], "清洗异常门控未接到宿主排班腿=接线未成立"
    assert summary["anomaly_gate"]["ok"] is True


def test_host_leg_delegates_to_real_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    """宿主托管函数必须把实调宿主槽位名交给承载册（host 不符即配置错，防册里挂空宿主）。"""
    seen: dict[str, Any] = {}

    def fake_gate(alerter=None, *, host_schedule=None, **kwargs):
        seen["host_schedule"] = host_schedule
        return {"ok": True, "status": "ran_and_clean"}

    monkeypatch.setattr(cah, "run_hosted_anomaly_gate", fake_gate)
    out = ss._run_hosted_anomaly_gate(RecordingAlerter())
    assert seen["host_schedule"] == "data_supply_sentinel"
    assert out["ok"] is True


def test_host_mismatch_is_config_error(tmp_path: Path) -> None:
    """承载册声明宿主 ≠ 实调宿主 → fail-closed（不许"册里挂了别的宿主"蒙混上岗）。"""
    carrier = write_carrier(tmp_path, wiring={"host_schedule": "some_other_slot"})
    out = run_hosted_anomaly_gate(
        RecordingAlerter(),
        config_path=carrier,
        executor=FakeFrameExecutor({"000001": _rows([10.0, 10.1])}),
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False and "config_error" in out


def test_shipped_carrier_loads_and_declares_engine_slots() -> None:
    """出厂真册自检：真 config/cleaning_anomaly_rules.yaml 必须能加载，且引擎面台账在案。"""
    wiring, engines, targets = load_anomaly_rulebook(None)
    assert wiring.host_schedule == "data_supply_sentinel"
    assert wiring.enabled is True
    assert engines.price_jump_pct > 0
    assert targets and targets[0].table == TABLE
    assert "cleaning_anomaly_engine" in ENGINE_SLOTS_WIRED
    assert set(ENGINE_SLOTS_RESERVED) == {"data_anomaly_alerter", "expectation_governance"}


# ---------------------------------------------------------------------------
# ②能否改变行为（判据真源=YAML）
# ---------------------------------------------------------------------------


def test_changing_yaml_threshold_changes_behavior(tmp_path: Path) -> None:
    """只改 price_jump_pct（0.20→0.001），同帧 findings 由 0→N：判据在册不在码。"""
    frames = {"000001": _rows([10.0, 10.05, 10.1])}  # 单根 4.9%：0.20 阈下静默
    base = run_anomaly_gate(
        *load_anomaly_rulebook(write_carrier(tmp_path / "a", report_dir=tmp_path / "r1")),
        GateRunOptions(
            executor=FakeFrameExecutor(frames),
            alerter=RecordingAlerter(),
            ref_date=REF,
            report_dir=tmp_path / "r1",
            notify=False,
        ),
    )
    tight = run_anomaly_gate(
        *load_anomaly_rulebook(
            write_carrier(tmp_path / "b", engines={"price_jump_pct": 0.001}, report_dir=tmp_path / "r2")
        ),
        GateRunOptions(
            executor=FakeFrameExecutor(frames),
            alerter=RecordingAlerter(),
            ref_date=REF,
            report_dir=tmp_path / "r2",
            notify=False,
        ),
    )
    assert base["findings_count"] == 0
    assert tight["findings_count"] >= 1, "改承载册阈值未改变行为=判据真源不在 YAML（装饰性护栏）"


def test_changing_watchlist_size_changes_symbol_count(tmp_path: Path) -> None:
    """只改 watchlist_size（10→1），symbols_checked 随变：标的口径真源在册。"""
    frames = {f"6000{i:02d}": _rows([10.0, 10.05]) for i in range(3)}
    base = run_anomaly_gate(
        *load_anomaly_rulebook(write_carrier(tmp_path / "a", report_dir=tmp_path / "r1")),
        GateRunOptions(
            executor=FakeFrameExecutor(frames),
            alerter=RecordingAlerter(),
            ref_date=REF,
            report_dir=tmp_path / "r1",
            notify=False,
        ),
    )
    tight = run_anomaly_gate(
        *load_anomaly_rulebook(write_carrier(tmp_path / "b", wiring={"watchlist_size": 1}, report_dir=tmp_path / "r2")),
        GateRunOptions(
            executor=FakeFrameExecutor(frames),
            alerter=RecordingAlerter(),
            ref_date=REF,
            report_dir=tmp_path / "r2",
            notify=False,
        ),
    )
    assert base["symbols_checked"] == 3
    assert tight["symbols_checked"] == 1


def test_detect_only_never_repairs(tmp_path: Path) -> None:
    """读侧 flag 档：报告必须自证 repair_invoked=False（修复=改生产数据，属 Owner 门位）。"""
    report = run_anomaly_gate(
        *load_anomaly_rulebook(write_carrier(tmp_path, report_dir=tmp_path / "r")),
        GateRunOptions(
            executor=FakeFrameExecutor({"000001": _rows([10.0, 13.0])}),
            alerter=RecordingAlerter(),
            ref_date=REF,
            report_dir=tmp_path / "r",
            notify=False,
        ),
    )
    assert report["repair_invoked"] is False
    assert report["read_side_only"] is True


# ---------------------------------------------------------------------------
# ③故障 fail-closed / 诚实读数
# ---------------------------------------------------------------------------


def test_red_missing_yaml_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(AnomalyGateConfigError):
        load_anomaly_rulebook(tmp_path / "nope.yaml")
    out = run_hosted_anomaly_gate(RecordingAlerter(), config_path=tmp_path / "nope.yaml", ref_date=REF, force=True)
    assert out["ok"] is False and out["not_run_reason"] == "config_error"


def test_red_unparseable_yaml_fail_closed(tmp_path: Path) -> None:
    bad = tmp_path / "carrier.yaml"
    bad.write_text("wiring: [unclosed", encoding="utf-8")
    with pytest.raises(AnomalyGateConfigError):
        load_anomaly_rulebook(bad)


@pytest.mark.parametrize(
    "mutator",
    [
        pytest.param(lambda doc: doc["wiring"].update({"bogus_key": 1}), id="wiring_unknown_key"),
        pytest.param(lambda doc: doc["engines"].pop("price_jump_pct"), id="engines_missing_required"),
        pytest.param(lambda doc: doc["engines"].update({"price_jump_pct": True}), id="bool_poisoning_float"),
        pytest.param(lambda doc: doc["wiring"].update({"watchlist_size": 0}), id="zero_watchlist"),
        pytest.param(lambda doc: doc["wiring"].update({"rows_per_symbol": -1}), id="negative_rows_limit"),
        pytest.param(lambda doc: doc["wiring"].update({"alert_level": "loud"}), id="illegal_alert_level"),
        pytest.param(lambda doc: doc["targets"].clear(), id="empty_targets"),
        pytest.param(lambda doc: doc["targets"][0].update({"table": "c1.x; DROP TABLE t"}), id="table_sql_fragment"),
        pytest.param(lambda doc: doc["targets"][0].update({"symbol_col": "1=1"}), id="symbol_col_injection"),
        pytest.param(
            lambda doc: doc["targets"][0].update({"frame_cols": ["close", "star_rating"]}), id="unknown_frame_col"
        ),
        pytest.param(lambda doc: doc.update({"schema_version": 2}), id="schema_version_drift"),
    ],
)
def test_malformed_carriers_fail_closed(tmp_path: Path, mutator) -> None:
    import copy

    doc: dict[str, Any] = {
        "schema_version": 1,
        "wiring": {
            "enabled": True,
            "host_schedule": "data_supply_sentinel",
            "cadence_days": 1,
            "rows_per_symbol": 60,
            "watchlist_size": 10,
            "alert_level": "warn",
            "report_dir": str(tmp_path / "r"),
            "disabled_flag": str(tmp_path / "off.flag"),
        },
        "engines": {"price_jump_pct": 0.2, "price_jump_z": 8.0, "volume_spike_mult": 20.0, "volume_z": 6.0},
        "targets": [
            {
                "table": TABLE,
                "date_col": "trade_date",
                "symbol_col": "symbol",
                "lookback_days": 30,
                "frame_cols": ["close", "volume"],
            },
        ],
    }
    mutator(doc)
    path = tmp_path / "carrier.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(AnomalyGateConfigError):
        load_anomaly_rulebook(path)


def test_degraded_symbol_never_reports_clean(tmp_path: Path) -> None:
    """单标的取数故障=degraded_partial 且 ok=False（禁把失明标的稀释成绿）。"""
    out = run_hosted_anomaly_gate(
        RecordingAlerter(),
        config_path=write_carrier(tmp_path, report_dir=tmp_path / "r"),
        executor=FakeFrameExecutor({"000001": _rows([10.0, 10.1])}, fail_symbols={"000001"}),
        ref_date=REF,
        force=True,
    )
    assert out["ok"] is False
    assert out["status"] == cah.STATUS_DEGRADED_PARTIAL


def test_zero_sample_symbol_is_degraded_not_clean(tmp_path: Path) -> None:
    """近窗零标的=跑了却无对象可判 → degraded_partial 禁冒干净（rb2 §二.10 同族防线）。"""
    out = run_hosted_anomaly_gate(
        RecordingAlerter(),
        config_path=write_carrier(tmp_path, report_dir=tmp_path / "r"),
        executor=FakeFrameExecutor({}),
        ref_date=REF,
        force=True,
    )
    assert out["status"] == cah.STATUS_DEGRADED_PARTIAL
    assert out["ok"] is False
    assert out["empty_watchlist"] is True


def test_findings_alert_at_yaml_level(tmp_path: Path) -> None:
    """命中走 Alerter 唯一正门出声，级别随承载册 alert_level。"""
    alerter = RecordingAlerter()
    run_anomaly_gate(
        *load_anomaly_rulebook(write_carrier(tmp_path, wiring={"alert_level": "error"}, report_dir=tmp_path / "r")),
        GateRunOptions(
            executor=FakeFrameExecutor({"000001": _rows([10.0, 13.0])}),
            alerter=alerter,
            ref_date=REF,
            report_dir=tmp_path / "r",
            notify=True,
        ),
    )
    assert any(level == "ERROR" and "清洗异常命中" in msg for level, msg in alerter.messages)


def test_report_persisted_and_body_verified_for_cadence(tmp_path: Path) -> None:
    """报告落盘=节奏闸状态真源；坏正文不占节奏闸（防空文件催眠）。"""
    rdir = tmp_path / "r"
    first = run_hosted_anomaly_gate(
        RecordingAlerter(),
        config_path=write_carrier(tmp_path, report_dir=rdir),
        executor=FakeFrameExecutor({"000001": _rows([10.0, 10.05])}),
        ref_date=REF,
        force=True,
    )
    assert first["ok"] is True
    body = json.loads((rdir / f"{REF.isoformat()}_anomaly_report.json").read_text(encoding="utf-8"))
    assert body["gate"] == "cleaning_anomaly_hosting"
    # 坏正文（gate 不自对）不得占节奏闸：同日 force=False 仍应真跑（此处直接断言 _latest_report_date）
    (rdir / f"{REF.isoformat()}_anomaly_report.json").write_text("{}", encoding="utf-8")
    assert cah._latest_report_date(rdir) is None


def test_disabled_flag_produces_not_run_with_ledger(tmp_path: Path) -> None:
    rdir = tmp_path / "r"
    carrier = write_carrier(tmp_path, report_dir=rdir)
    flag = tmp_path / "off.flag"
    flag.write_text("", encoding="utf-8")
    out = run_hosted_anomaly_gate(
        RecordingAlerter(), config_path=carrier, executor=FakeFrameExecutor({}), ref_date=REF, force=False
    )
    assert out["ok"] is False and out["not_run_reason"] == cah.NOT_RUN_MASTER_SWITCH_OFF
    assert (rdir / f"{REF.isoformat()}_anomaly_gate_status_ledger.json").exists()


def test_gate_status_ordering() -> None:
    """四态判序：降级优先于命中（禁稀释）；全净才 ok。"""
    degraded = {"degraded": True, "no_samples": False, "findings_count": 5}
    hit = {"degraded": False, "no_samples": False, "findings_count": 2}
    clean = {"degraded": False, "no_samples": False, "findings_count": 0}
    assert gate_status([degraded, hit]) == cah.STATUS_DEGRADED_PARTIAL
    assert gate_status([hit]) == cah.STATUS_RAN_FINDINGS
    assert gate_status([clean]) == cah.STATUS_RAN_CLEAN
    assert gate_status([]) == cah.STATUS_NOT_RUN
