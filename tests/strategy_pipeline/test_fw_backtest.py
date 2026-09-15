# [BLUEPRINT] MOD-BT-198 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_fw_backtest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.fw_backtest; zephyr.strategy_pipeline.pipeline_events
# [CONSUMERS] pytest（SOP Step 5 循环验收）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 测试禁写生产路径（journal/证据包目录全走 tmp_path monkeypatch）；不触 ClickHouse
#   与真实回测（run_framework_backtest 打桩）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] pytest tests/strategy_pipeline/test_fw_backtest.py
# [A_module] module_id=MOD-BT-198-tests | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fw_backtest_due 自动触发件单测（MOD-BT-198）。

覆盖面:
    - 契约钉死: run_fw_backtest_due(event) 四步流（生成器→幂等闸→参数→回测+证据包）
    - 幂等: 同 plan 指纹且最近 ok → skipped（不重跑）
    - 验收: 对账超容差 → ok=False + ERROR 告警 + 证据包落档（不 raise）
    - 瞬时故障: 生成器失败 → RuntimeError 上抛（journal 留档语义）
    - emit 帮手: rc=0 出队 / rc≠0 留档计 attempts
"""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

import zephyr.pf_core.strategy_engine.framework_composer as fc
import zephyr.strategy_pipeline.fw_backtest as fw
import zephyr.strategy_pipeline.pipeline_events as pe

_FP = {"plan_id": "fw-tdm-current", "weights": {"a": 1.0}, "tdm_sha256_12": "deadbeef1234",
       "fingerprint": "abc123def456"}


def _fake_run_result(ok: bool = True, within: bool = True, equity: int = 60) -> dict:
    return {
        "ok": ok,
        "run_id": "bt-fw-test1234",
        "plan_id": "fw-tdm-current",
        "participants": ["a", "STR-TEST-001"],
        "skipped": [["b", "panel/data empty"]],
        "rescale_factor": 1.0,
        "dynamic": False,
        "regime_day_counts": {},
        "per_regime": [],
        "panel_reconciliation": {"within_tolerance": within, "max_abs_diff": 0.0 if within else 1e-3,
                                 "over_tolerance_cells": 0 if within else 5},
        "equity_points": equity,
        "trades": 42,
        "metrics": {"total_return": 0.1, "sharpe_ratio": 1.2, "plan_id": "fw-tdm-current"},
        "warn": None if (ok and within and equity) else "degraded",
    }


@pytest.fixture()
def isolated(tmp_path: Path, monkeypatch):
    """隔离三件套：事件 journal→tmp、证据目录→tmp、告警→捕获。"""
    state = tmp_path / "strategy_pipeline"
    monkeypatch.setattr(pe, "STATE_DIR", state)
    monkeypatch.setattr(pe, "JOURNAL", state / "pending_events.jsonl")
    monkeypatch.setattr(pe, "RECEIPT", state / "last_receipt.json")
    monkeypatch.setattr(fw, "EVIDENCE_DIR", tmp_path / "fw-auto")
    alerts: list[tuple[str, str]] = []
    monkeypatch.setattr(fw, "_alert", lambda msg, level="WARN": alerts.append((level, msg)))
    return {"alerts": alerts, "tmp": tmp_path}


def _patch_happy_path(monkeypatch, run_result: dict | None = None, fp: dict | None = None):
    monkeypatch.setattr(fw, "_run_generator",
                        lambda t: {"rc": 0, "duration_s": 0.1, "summary": {"changed": False}})
    monkeypatch.setattr(fw, "plan_fingerprint", lambda p=None: dict(fp or _FP))
    monkeypatch.setattr(fw, "_latest_evidence", lambda: None)
    monkeypatch.setattr(fw, "resolve_symbols",
                        lambda s, e, base=None: (["600000", "000852"], {"str_members": [], "str_columns_n": {}, "total": 2}))
    monkeypatch.setattr(fw, "load_regime_series", lambda s, e: {
        "mode": "static", "freshness": {"stale_days": 1}, "note": "test"})
    calls: list[tuple] = []

    def _fake_run(plan_id, symbols, start, end, config=None):
        calls.append((plan_id, tuple(symbols), start, end))
        return run_result or _fake_run_result()

    monkeypatch.setattr(fc, "run_framework_backtest", _fake_run)
    return calls


class TestRunFwBacktestDue:
    def test_contract_happy_path(self, isolated, monkeypatch):
        calls = _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"kind": "fw_backtest_due",
                                      "payload": {"trigger": "auto_mount", "sids": ["STR-X-1"]}})
        assert out["ok"] is True
        assert calls and calls[0][0] == "fw-tdm-current"
        assert out["window"]["end"] >= out["window"]["start"]
        assert out["run"]["run_id"] == "bt-fw-test1234"
        assert out["run"]["artifact_path"].endswith("bt-fw-test1234.json")
        assert out["acceptance"]["within_tolerance"] is True
        assert Path(out["evidence_path"]).exists()
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        assert body["plan"]["fingerprint"] == _FP["fingerprint"]  # 证据包含 plan 身份
        assert (fw.EVIDENCE_DIR / "latest.json").exists()

    def test_idempotent_skip_on_same_fingerprint(self, isolated, monkeypatch):
        _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True},
            "evidence_path": "latest.json",
        })
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out.get("skipped") and "fingerprint_unchanged" in out["skipped"]

    def test_force_bypasses_idempotent_skip(self, isolated, monkeypatch):
        calls = _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]}, "acceptance": {"ok": True}})
        out = fw.run_fw_backtest_due({"payload": {"force": True}})
        assert out["ok"] is True and calls  # force 越过幂等闸真实重跑

    def test_over_tolerance_no_retry(self, isolated, monkeypatch):
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(within=False))
        out = fw.run_fw_backtest_due({"payload": {}})  # 不 raise（语义失败不重试）
        assert out["ok"] is False
        assert out["acceptance"]["within_tolerance"] is False
        assert any(lv == "ERROR" for lv, _ in isolated["alerts"])
        assert Path(out["evidence_path"]).exists()

    def test_generator_failure_raises(self, isolated, monkeypatch):
        monkeypatch.setattr(fw, "_run_generator",
                            lambda t: (_ for _ in ()).throw(RuntimeError("方案表生成器失败 rc=1")))
        with pytest.raises(RuntimeError, match="生成器失败"):
            fw.run_fw_backtest_due({"payload": {}})  # 瞬时故障上抛→journal 留档重试


class TestEmitFwBacktestDue:
    def test_emit_success_dequeues(self, isolated, monkeypatch):
        monkeypatch.setattr(fw, "subprocess", types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(
            returncode=0, stdout=json.dumps({"ok": True}), stderr="")))
        out = fw.emit_fw_backtest_due("auto_mount", sids=["STR-X-1"])
        assert out["drained"] is True
        assert pe.pending() == []  # 成功出队

    def test_emit_failure_retains_with_attempts(self, isolated, monkeypatch):
        monkeypatch.setattr(fw, "subprocess", types.SimpleNamespace(run=lambda *a, **k: types.SimpleNamespace(
            returncode=1, stdout="", stderr="boom")))
        out = fw.emit_fw_backtest_due("auto_mount")
        assert out["drained"] is False
        left = pe.pending()
        assert len(left) == 1 and left[0]["kind"] == "fw_backtest_due"
        assert left[0]["attempts"] == 1 and "boom" in (left[0].get("last_error") or "")


class TestEventPayloadTolerance:
    def test_bare_payload_dict_accepted(self, isolated, monkeypatch):
        """契约宽容：裸 payload dict（无 kind/payload 包装）同构处理。"""
        calls = _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"trigger": "manual"})
        assert out["ok"] is True and calls
