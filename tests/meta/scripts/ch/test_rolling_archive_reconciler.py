"""rolling_archive_reconciler 纯逻辑单测（零 CH 依赖：mock 分区列举，验证阀/限量/熔断/kill）。"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts" / "ch"))
import rolling_archive_reconciler as ra  # noqa: E402


def test_partition_end_ym():
    assert ra._partition_end_ym("202306") == 202306
    assert ra._partition_end_ym("20230601") == 202306
    assert ra._partition_end_ym("'202306'") == 202306
    assert ra._partition_end_ym("2023") is None
    assert ra._partition_end_ym("(2023, 6)") is None
    assert ra._partition_end_ym("abc") is None


def test_kill_switch_blocks(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "STATE_FILE", tmp_path / "state.json")
    ra.update_state(kill_switch=True)
    out = ra.evaluate("full_auto")
    assert out["valve1"] == "kill"
    assert out["executed"] == []


def test_backup_failure_valve(tmp_path, monkeypatch):
    monkeypatch.setattr(ra, "STATE_FILE", tmp_path / "state.json")
    out = ra.evaluate("full_auto", inject_backup_failure=True)
    assert "SKIP" in out["valve1"]
    assert out["executed"] == []


def test_injected_verify_mismatch_opens_circuit(tmp_path, monkeypatch):
    """红蓝注入：对账不符→拒绝 drop→连续失败达阈值→熔断。"""
    monkeypatch.setattr(ra, "STATE_FILE", tmp_path / "state.json")
    params = {
        "hysteresis_months": 1,
        "batch_max_partitions": 3,
        "batch_max_bytes": 30_000_000_000,
        "circuit_breaker_failures": 3,
        "excluded_tables": [],
        "retention_lines_months": {},
    }
    monkeypatch.setattr(ra, "load_contract_params", lambda: params)
    monkeypatch.setattr(ra, "_backup_fresh", lambda inject=False: (True, "ok"))
    monkeypatch.setattr(
        ra,
        "list_past_line_partitions",
        lambda p: (
            [
                {
                    "database": "c1_market",
                    "table": "tick_data",
                    "partition": "202401",
                    "rows": 1,
                    "bytes_on_disk": 1,
                    "line_months": 25,
                    "hysteresis_months": 1,
                },
            ]
            * 3
        ),
    )
    out = ra.evaluate("full_auto", inject_verify_mismatch=True)
    assert len(out["executed"]) == 3
    assert all("verify_mismatch" in e["result"] for e in out["executed"])
    assert out["circuit"] == "熔断开启（注入触发）"
    assert ra.load_state()["circuit_open"] is True
    # 熔断后 evaluate 拒绝
    out2 = ra.evaluate("full_auto")
    assert out2["valve1"] == "circuit_open"


def test_batch_limits(tmp_path, monkeypatch):
    """批限量：≤3 分区且 ≤30G，超限留下一事件。"""
    monkeypatch.setattr(ra, "STATE_FILE", tmp_path / "state.json")
    params = {
        "hysteresis_months": 1,
        "batch_max_partitions": 2,
        "batch_max_bytes": 10_000_000_000,
        "circuit_breaker_failures": 3,
        "excluded_tables": [],
        "retention_lines_months": {},
    }
    monkeypatch.setattr(ra, "load_contract_params", lambda: params)
    monkeypatch.setattr(ra, "_backup_fresh", lambda inject=False: (True, "ok"))
    big = 4_000_000_000
    cands = [
        {
            "database": "c1_market",
            "table": f"t{i}",
            "partition": "202401",
            "rows": 1,
            "bytes_on_disk": big,
            "line_months": 25,
            "hysteresis_months": 1,
        }
        for i in range(4)
    ]
    monkeypatch.setattr(ra, "list_past_line_partitions", lambda p: cands)
    out = ra.evaluate("shadow")
    assert len(out["batch"]) == 2  # 3rd would exceed 10G byte cap; partition cap=2 同界
    assert len(out["skipped"]) == 2
    assert "shadow" in out["note"]


def _write_backup_state(tmp_path, monkeypatch, payload):
    p = tmp_path / "backup_state.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(ra, "BACKUP_STATE_FILE", p)
    return p


def test_ch_chain_fresh_fail_closed_on_probe_failure(tmp_path, monkeypatch):
    """仪表修正 #2 的方向性断言：读不到 CH 服务端事实必须判**红**，绝不当新鲜放行。"""
    _write_backup_state(tmp_path, monkeypatch, {"last_ch_backup_verified": True})
    monkeypatch.setattr(ra, "_ch_newest_backup_created_age_h", lambda: (None, "sim outage"))
    ok, why = ra.ch_chain_fresh()
    assert ok is False
    assert "不可判" in why


def test_ch_chain_fresh_red_when_stale_green_when_fresh(tmp_path, monkeypatch):
    _write_backup_state(tmp_path, monkeypatch, {"last_ch_backup_verified": True})
    monkeypatch.setattr(ra, "_ch_newest_backup_created_age_h", lambda: (31.0, "ok"))
    assert ra.ch_chain_fresh()[0] is False
    monkeypatch.setattr(ra, "_ch_newest_backup_created_age_h", lambda: (1.2, "ok"))
    assert ra.ch_chain_fresh()[0] is True
    # verified 旗为假时，即使服务端新鲜也判红（两把尺都要过）
    _write_backup_state(tmp_path, monkeypatch, {"last_ch_backup_verified": False})
    assert ra.ch_chain_fresh()[0] is False


def test_ch_chain_fresh_not_confused_by_cadence_skipped(tmp_path, monkeypatch):
    """旧判据把节律 skipped 当故障；新探针必须不受该旗影响。"""
    _write_backup_state(
        tmp_path,
        monkeypatch,
        {
            "last_ch_backup_status": "skipped",
            "last_backup_status": "failed",
            "last_ch_backup_verified": True,
        },
    )
    monkeypatch.setattr(ra, "_ch_newest_backup_created_age_h", lambda: (3.0, "ok"))
    assert ra.ch_chain_fresh()[0] is True
    # 对照：整轮旗判据此时仍报红（说明二者确实解耦，不是我把尺调松）
    assert ra._backup_fresh()[0] is False


def test_last_compaction_days_reads_backup_state_not_archive_state(tmp_path, monkeypatch):
    """仪表修正 #1：真源=backup_state.json；原判据读 rolling_archive_state.json ⇒ 恒 None。"""
    from datetime import datetime, timedelta, timezone

    ts = (datetime.now(timezone.utc) - timedelta(days=9)).isoformat()
    _write_backup_state(
        tmp_path,
        monkeypatch,
        {"last_vhdx_compaction": ts, "last_vhdx_compaction_result": "ok"},
    )
    monkeypatch.setattr(ra, "STATE_FILE", tmp_path / "archive_state.json")
    days, why = ra.last_compaction_days()
    assert why == "ok"
    assert days is not None and 8 <= days <= 10
    # result 非 ok 时必须回 None（=从未成功压缩），不能拿时间戳充数
    _write_backup_state(
        tmp_path,
        monkeypatch,
        {"last_vhdx_compaction": ts, "last_vhdx_compaction_result": "failed"},
    )
    assert ra.last_compaction_days()[0] is None


def test_d_red_line_reader_and_missing_key(tmp_path, monkeypatch):
    """仪表修正 #3：D 线有机读读者；缺键时返回 None+原因（不静默当 0 放行）。"""
    cfg = tmp_path / "backup_config.yaml"
    cfg.write_text("capacity_guard:\n  min_free_gb:\n    F: 700\n    G: 500\n    D: 50\n", encoding="utf-8")
    monkeypatch.setattr(ra, "BACKUP_CONFIG_FILE", cfg)
    assert ra.d_drive_red_line_gb() == (50.0, "ok")
    cfg.write_text("capacity_guard:\n  min_free_gb:\n    F: 700\n", encoding="utf-8")
    val, why = ra.d_drive_red_line_gb()
    assert val is None and "缺 D 键" in why
    cfg.unlink()
    val, why = ra.d_drive_red_line_gb()
    assert val is None and "不可读" in why


def test_record_vhdx_growth_delta_and_red_line_flag(tmp_path, monkeypatch):
    """仪表修正 #4：日序列必须真落盘并算出日差；低于红线要显式标出。"""
    ser = tmp_path / "vhdx_growth_series.jsonl"
    monkeypatch.setattr(ra, "VHDX_GROWTH_SERIES", ser)
    monkeypatch.setattr(ra, "d_drive_red_line_gb", lambda: (50.0, "ok"))
    r1 = ra.record_vhdx_growth(586.5, 59.99)
    assert r1["delta_vs_prev_gb"] is None and r1["d_below_red_line"] is False
    r2 = ra.record_vhdx_growth(590.0, 48.0)
    assert r2["delta_vs_prev_gb"] == 3.5
    assert r2["d_below_red_line"] is True
    lines = [json.loads(x) for x in ser.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(lines) == 2  # 追加式，不覆写他人/历史


def test_precheck_records_series_even_when_not_due(tmp_path, monkeypatch):
    """due 只 gate 成文，不 gate 采集——否则 <90 天的年份里序列整段断掉。"""
    monkeypatch.setattr(ra, "VHDX_GROWTH_SERIES", tmp_path / "series.jsonl")
    monkeypatch.setattr(ra, "PLAN_DIR", tmp_path / "plan")
    monkeypatch.setattr(ra, "d_drive_red_line_gb", lambda: (50.0, "ok"))
    monkeypatch.setattr(ra, "last_compaction_days", lambda: (9.4, "ok"))
    monkeypatch.setattr(ra, "ch_chain_fresh", lambda: (True, "fresh"))
    monkeypatch.setattr(ra, "_backup_fresh", lambda inject=False: (False, "failed"))
    monkeypatch.setattr(
        ra,
        "_ch_newest_backup_created_age_h",
        lambda: (1.0, "ok"),
        raising=False,
    )
    import datetime as _dt

    class _FixedDate(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return _dt.datetime(2026, 10, 9, 12, 0, 0)

    monkeypatch.setattr(ra, "datetime", _FixedDate)
    out = ra.vhdx_precheck()
    assert out["due"] is False
    assert out["days_since_last_compaction"] == 9.4
    assert "vhdx_delta_gb" in out
    assert (tmp_path / "series.jsonl").exists()
    assert not (tmp_path / "plan").exists() or not list((tmp_path / "plan").glob("vhdx_precheck_*.md"))
