# [BLUEPRINT] MOD-TEST-333 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""验证 runner v1 单元测试（P1-2）——方法推导/holdout 切分/两土规/lag 开关/dry-run 零写入。

真源: docs/_working/2026-09-09-node-backtest-governance.md §8.2 P1-2
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from zephyr.trading.validation.runner import (
    ValidationConfig,
    apply_soil_rules,
    compute_exec_metrics,
    derive_method,
    holdout_cutoff,
    load_exec_nodes,
    partition_by_holdout,
    run_validation,
)

AS_OF = datetime(2026, 9, 9, 12, 0, 0)


# ── 节点清单与方法推导 ────────────────────────────────────────────────────

def test_load_exec_nodes_first_batch_is_14_excluding_crypto():
    nodes = load_exec_nodes()
    assert len(nodes) == 14, f"首批应为 14（15 个 L4 减币圈镜像）: {len(nodes)}"
    assert all(not n["node_id"].startswith("TDM-C-") for n in nodes)
    assert any(n["node_id"] == "TDM-E-L4-03" for n in nodes)


def test_derive_method_mapping():
    assert derive_method({"layer": "L4"}) == "exec_quality"
    assert derive_method({"layer": "L1", "flow": "exit_flow"}) == "exit_counterfactual"
    assert derive_method({"layer": "L1", "flow": "portfolio_flow"}) == "portfolio_attribution"
    assert derive_method({"layer": "L1", "node_id": "TDM-E-L1-S1"}) == "sensor_monotonicity"
    assert derive_method({"layer": "L1", "node_id": "TDM-E-L1-AGG"}) == "agg_discrimination"
    assert derive_method({"layer": "L2"}) == "agg_discrimination"


# ── holdout 切分（PB-08：最近 12 个月保密考卷）────────────────────────────

def test_holdout_cutoff_twelve_months():
    assert holdout_cutoff(AS_OF, 12) == datetime(2025, 9, 9)
    assert holdout_cutoff(datetime(2026, 3, 31), 12) == datetime(2025, 3, 28)  # 月底安全截断


def test_partition_splits_at_cutoff():
    fills = [
        {"timestamp": "2025-09-09", "symbol": "x", "side": "buy", "price": 10},
        {"timestamp": "2025-09-10", "symbol": "x", "side": "buy", "price": 10},
        {"timestamp": "2026-08-14 09:30", "symbol": "x", "side": "buy", "price": 10},
        {"timestamp": "", "symbol": "x", "side": "buy", "price": 10},
    ]
    inside, locked = partition_by_holdout(fills, datetime(2025, 9, 9))
    assert len(inside) == 1 and inside[0]["timestamp"] == "2025-09-09"
    assert len(locked) == 3   # holdout 内 + 脏时间戳（宁严勿漏）


# ── 两土规（PB-13 降级裁定）───────────────────────────────────────────────

def test_soil_rule_insufficient_samples():
    sig, verdict = apply_soil_rules({"triggers": 10, "slip_bp_mean": 5.0}, ValidationConfig())
    assert sig == "insufficient_samples" and verdict == "pending"


def test_soil_rule_oos_decay_suspect():
    metrics = {"triggers": 100, "slip_bp_mean": 30.0}
    first = {"slip_bp_mean": 10.0}   # 衰减 (30-10)/10 = 200% >= 50%
    sig, verdict = apply_soil_rules(metrics, ValidationConfig(), first_metrics=first)
    assert sig == "oos_decay_suspect" and verdict == "pending"


def test_soil_rule_verdict_by_slippage():
    cfg = ValidationConfig()
    assert apply_soil_rules({"triggers": 50, "slip_bp_mean": 8.0}, cfg) == ("ok", "valid")
    assert apply_soil_rules({"triggers": 50, "slip_bp_mean": 30.0}, cfg) == ("ok", "pending")
    assert apply_soil_rules({"triggers": 50, "slip_bp_mean": 88.0}, cfg) == ("ok", "noise")
    assert apply_soil_rules({"triggers": 50, "slip_bp_mean": None}, cfg) == ("", "pending")


def test_compute_exec_metrics_direction_and_skip():
    fills = [
        {"symbol": "A", "side": "buy", "price": 11.0},    # 劣于基准 10%
        {"symbol": "B", "side": "sell", "price": 9.0},    # 卖低于基准=劣 10%
        {"symbol": "C", "side": "buy", "price": 10.0},    # 无参考价 → 跳过滑点
    ]
    m = compute_exec_metrics(fills, ref_prices={"A": 10.0, "B": 10.0})
    assert m["triggers"] == 3
    assert m["slip_samples"] == 2
    assert m["slip_bp_mean"] == 1000.0   # 两侧都劣 10% → +1000bp
    assert m["fill_rate"] is None        # 未成交数不可得，如实置空


# ── 批入口（dry-run 零写入 + 14 行产出）──────────────────────────────────

def test_run_validation_dry_run_no_write(tmp_path: Path):
    artifacts = tmp_path / "art"
    artifacts.mkdir()
    (artifacts / "bt-t1.json").write_text(json.dumps({
        "run_id": "bt-t1", "strategy_id": "test",
        "trade_log": [{"timestamp": "2026-06-01", "symbol": "A", "side": "buy", "price": 10.0}],
    }), encoding="utf-8")

    def _must_not_write(table, columns, tsv):
        raise AssertionError("dry-run 禁止写库")

    report = run_validation(
        cfg=ValidationConfig(as_of=AS_OF),
        artifacts_dir=artifacts,
        dry_run=True,
        writer=_must_not_write,
    )
    assert len(report.rows) == 14
    assert all(r["verdict"] == "pending" for r in report.rows)
    assert all(r["significance"] == "insufficient_samples" for r in report.rows)
    assert all("holdout" in r["notes"] for r in report.rows)   # notes 如实披露锁窗原因
    assert report.written is False
    assert report.snapshot_commit  # 快照绑定（PB-06）必带 commit 号


def test_run_validation_writes_tsv(tmp_path: Path):
    artifacts = tmp_path / "art"
    artifacts.mkdir()
    (artifacts / "bt-t2.json").write_text(json.dumps({"run_id": "bt-t2", "trade_log": []}), encoding="utf-8")
    captured = {}

    def fake_writer(table, columns, tsv):
        captured["table"], captured["columns"], captured["tsv"] = table, columns, tsv
        return True

    report = run_validation(cfg=ValidationConfig(as_of=AS_OF), artifacts_dir=artifacts, writer=fake_writer,
                            decay_check=False)   # 单测不依赖 CH（衰减巡检走真实台账查询）
    assert report.written is True
    assert captured["table"] == "c1_backtest.node_verdict"
    lines = captured["tsv"].decode("utf-8").strip().split("\n")
    assert len(lines) == 14
    assert all(len(l.split("\t")) == 12 for l in lines)
    assert "\\N" in lines[0]   # hit_ratio=None → CH TSV NULL 转义（空串会变 0，实测踩坑）


def test_run_validation_decay_tail_hook(tmp_path: Path, monkeypatch):
    """衰减巡检=验证批尾随事件（裁定 2026-09-10）：写库成功后自动跑，失败不阻断验证批。"""
    import zephyr.trading.validation.decay_watch as dw

    # 台账查询打桩（单测不依赖真实 CH）：基线 0.60 → 最新 0.55，未达 50% 衰减线
    monkeypatch.setattr(dw.ch_writer, "query", lambda q, timeout=30: (
        "TDM-E-L1-S1\tvalid\t2025-01-01\tVAL-A\t2025-01-02 10:00:00\t0.60\texec_quality\n"
        "TDM-E-L1-S1\tvalid\t2026-06-01\tVAL-B\t2026-06-02 10:00:00\t0.55\texec_quality\n"
    ))

    artifacts = tmp_path / "art"
    artifacts.mkdir()
    (artifacts / "bt-t3.json").write_text(json.dumps({"run_id": "bt-t3", "trade_log": []}), encoding="utf-8")
    writes: list[str] = []

    def counting_writer(table, columns, tsv):
        writes.append(table)
        return True

    report = run_validation(cfg=ValidationConfig(as_of=AS_OF), artifacts_dir=artifacts,
                            writer=counting_writer, decay_check=True)
    assert report.written is True
    assert report.decay is not None            # 钩子已执行且吃到打桩台账
    assert report.decay["checked"] == 2
    assert report.decay["decayed"] == 0        # 未达 50% 衰减线 → 不追加 decaying 行
    assert len(writes) == 1                    # 只写了验证批 14 行，无 decaying 追加
    # dry-run 不触发巡检（未写库无新数据可比）
    report_dry = run_validation(cfg=ValidationConfig(as_of=AS_OF), artifacts_dir=artifacts,
                                dry_run=True, writer=counting_writer, decay_check=True)
    assert report_dry.decay is None


# ── 衰减自动巡检（PB-14）──────────────────────────────────────────────────

class TestDecayWatch:
    TSV_HEADER = None  # ledger TSV 无表头（ch_writer TSV 惯例）

    def _row(self, node, verdict, hit, win, method="exec_quality", at="2026-01-01 10:00:00"):
        return {"node_id": node, "verdict": verdict, "window_end": win, "run_id": f"VAL-{win}",
                "verdict_at": at, "hit_ratio": hit, "validation_method": method}

    def test_detect_decay_over_threshold(self):
        from zephyr.trading.validation.decay_watch import detect_decays
        rows = [
            self._row("TDM-E-L1-S1", "valid", 0.80, "2025-01-01"),
            self._row("TDM-E-L1-S1", "valid", 0.30, "2026-01-01", at="2026-01-01 10:00:00"),  # 衰减 62.5%
            self._row("TDM-E-L4-03", "valid", 0.90, "2025-01-01"),
            self._row("TDM-E-L4-03", "valid", 0.70, "2026-01-01", at="2026-01-01 10:00:00"),  # 衰减 22% 未达线
        ]
        out = detect_decays(rows)
        assert len(out) == 1
        assert out[0]["node_id"] == "TDM-E-L1-S1"
        assert out[0]["decay"] >= 0.50

    def test_no_baseline_no_verdict(self):
        from zephyr.trading.validation.decay_watch import detect_decays
        rows = [
            self._row("TDM-X-S1", "pending", None, "2026-01-01"),
            self._row("TDM-X-S1", "valid", None, "2026-02-01", at="2026-02-01 10:00:00"),  # 无基线值不判
        ]
        assert detect_decays(rows) == []

    def test_run_decay_check_dry_run_and_write(self):
        from zephyr.trading.validation.decay_watch import run_decay_check
        tsv = (
            "TDM-F-C1\tvalid\t2025-01-01\tVAL-A\t2025-01-02 10:00:00\t0.60\tportfolio_attribution\n"
            "TDM-F-C1\tvalid\t2026-06-01\tVAL-B\t2026-06-02 10:00:00\t0.20\tportfolio_attribution\n"
        )
        captured = {}
        report = run_decay_check(ledger_tsv=tsv, dry_run=True,
                                 writer=lambda t, c, b: captured.update(table=t, tsv=b) or True)
        assert report["decayed"] == 1 and report["written"] is False
        report2 = run_decay_check(ledger_tsv=tsv, as_of=AS_OF,
                                  writer=lambda t, c, b: captured.update(table=t, tsv=b) or True)
        assert report2["written"] is True
        assert captured["table"] == "c1_backtest.node_verdict"
        line = captured["tsv"].decode("utf-8").strip().split("\n")[0].split("\t")
        assert line[4] == "TDM-F-C1" and line[9] == "decaying"
        assert line[8] == "oos_decay_suspect"
        assert line[5] == "portfolio_attribution"   # 沿用节点原验证方法
        assert "衰减" in line[11]
