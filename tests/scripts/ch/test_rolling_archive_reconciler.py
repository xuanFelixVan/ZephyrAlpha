"""rolling_archive_reconciler 纯逻辑单测（零 CH 依赖：mock 分区列举，验证阀/限量/熔断/kill）。"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "ch"))
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
