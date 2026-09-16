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
    - H5-B 三段门控: IS/WFA/OOS+DSR 裁决进 acceptance（达标放行、退化否决、缺净值 fail-closed）
    - H5-D 护栏降级: 引擎 fail-open 出声在消费侧计数可见 + WARN，且不新增否决权
    - 瞬时故障: 生成器失败 → RuntimeError 上抛（journal 留档语义）
    - emit 帮手: rc=0 出队 / rc≠0 留档计 attempts
"""

from __future__ import annotations

import json
import logging
import types
from pathlib import Path

import pandas as pd
import pytest

import zephyr.pf_core.strategy_engine.framework_composer as fc
import zephyr.strategy_pipeline.fw_backtest as fw
import zephyr.strategy_pipeline.pipeline_events as pe

_FP = {"plan_id": "fw-tdm-current", "weights": {"a": 1.0}, "tdm_sha256_12": "deadbeef1234",
       "fingerprint": "abc123def456"}


def _fake_run_result(ok: bool = True, within: bool = True, equity: int = 60,
                     overfitting: bool = False, dsr: float | None = 0.97,
                     n_trials: int | None = 4497,
                     dead_share: float | None = 0.0) -> dict:
    disclosure: dict | None = None
    if dead_share is not None:
        disclosure = {
            "schema": 1,
            "plan_id": "fw-tdm-current",
            "plan_weight_total": 1.0,
            "participants": [{"strategy_id": "a", "alpha": 1.0 - dead_share}],
            "skipped_members": [{"strategy_id": "b", "alpha": dead_share,
                                 "kind": "dead-member", "reason": "all-zero weight rows"}],
            "participants_alpha_base": 1.0 - dead_share,
            "skipped_alpha_base": dead_share,
            "skipped_alpha_share_of_plan": dead_share,
            "dead_member_alpha_base": dead_share,
            "rescale_factor": 1.0 / (1.0 - dead_share) if dead_share < 1.0 else 1.0,
            "row_normalization": {"rows_total": 60, "rows_normalized": 0,
                                  "max_deviation": 0.0, "material": False},
        }
    result = {
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
        # #24 H4-B 现金账本闭合闸的默认披露（形状=portfolio.reconcile_cash_ledger 产出）：
        # 缺这个键等于"账本没接"，闸按 fail-closed 判不过——反证用例自行覆写。
        "cash_ledger_reconciliation": {
            "within_tolerance": True, "samples": 5, "trade_rows": 12,
            "max_abs_residual": 0.0, "tolerance_abs": 0.01, "over_tolerance": 0,
            "worst_date": "2026-01-06", "bad_trade_rows": 0,
            "cash_last": 900000.0, "reconstructed_cash_last": 900000.0,
        },
        "equity_points": equity,
        "trades": 42,
        "metrics": {"total_return": 0.1, "sharpe_ratio": 1.2, "plan_id": "fw-tdm-current",
                    "trades_count": 42, "overfitting_flag": overfitting, "dsr": dsr,
                    "n_trials": n_trials, "n_trials_source": "trial_ledger" if n_trials else None},
        "warn": None if (ok and within and equity) else "degraded",
    }
    if disclosure is not None:
        result["dead_weight_disclosed"] = disclosure
    return result


#: 三段门控最小可用净值长度：_GATE_MIN_SEG_SAMPLES(61) × 3 段 = 183；取 250 让 IS + 2 完整折成立
_NAV_DAYS = 250


def _write_nav_artifact(artifact_dir: Path, run_id: str = "bt-fw-test1234",
                        n: int = _NAV_DAYS, mode: str = "rise") -> Path:
    """落一份 tmp 回测产物的 equity_curve（H5-B 三段门控的唯一真源输入）。

    mode="rise" 稳步上行（三段皆达标）；mode="collapse" 前 40% 上行后下行（IS 达标、
    WFA/OOS 退化），用于验证门控确有否决权而非装饰。
    """
    artifact_dir.mkdir(parents=True, exist_ok=True)
    idx = pd.bdate_range("2025-01-02", periods=n)
    cut = int(n * 0.4)
    eq, vals = 1_000_000.0, []
    for i in range(n):
        drift = 0.0015 + (0.004 if i % 7 == 0 else -0.0012 if i % 5 == 0 else 0.0005)
        if mode == "collapse" and i >= cut:
            drift = -abs(drift) - 0.004
        eq *= (1 + drift)
        vals.append({"timestamp": idx[i].strftime("%Y-%m-%d"), "equity": round(eq, 2)})
    path = artifact_dir / f"{run_id}.json"
    path.write_text(json.dumps({"run_id": run_id, "equity_curve": vals}), encoding="utf-8")
    return path


@pytest.fixture()
def isolated(tmp_path: Path, monkeypatch):
    """隔离四件套：事件 journal→tmp、证据目录→tmp、产物目录→tmp（含可用净值）、告警→捕获。"""
    state = tmp_path / "strategy_pipeline"
    monkeypatch.setattr(pe, "STATE_DIR", state)
    monkeypatch.setattr(pe, "JOURNAL", state / "pending_events.jsonl")
    monkeypatch.setattr(pe, "RECEIPT", state / "last_receipt.json")
    monkeypatch.setattr(fw, "EVIDENCE_DIR", tmp_path / "fw-auto")
    artifact_dir = tmp_path / "backtest_artifacts"
    monkeypatch.setattr(fw, "ARTIFACT_DIR", artifact_dir)
    # 默认给一份达标净值：让"风险旗标 False + 指标达标 → 过"这一路是真·四闸全绿
    _write_nav_artifact(artifact_dir)
    alerts: list[tuple[str, str]] = []
    monkeypatch.setattr(fw, "_alert", lambda msg, level="WARN": alerts.append((level, msg)))
    return {"alerts": alerts, "tmp": tmp_path, "artifact_dir": artifact_dir}


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
        # H5-B：三段门控（IS/WFA/OOS + DSR）结论是验收要件，不是旁路日志
        acc = out["acceptance"]
        assert (acc["gate_passed"], acc["gate_is_passed"], acc["gate_wfa_passed"],
                acc["gate_oos_passed"]) == (True, True, True, True)
        assert acc["gate_wfa_windows"] == "2/2"
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        assert body["plan"]["fingerprint"] == _FP["fingerprint"]  # 证据包含 plan 身份
        gate_ev = body["run"]["staged_gate_decision"]["evidence"]
        assert gate_ev["scheme"]["nav_days"] == _NAV_DAYS  # 证据口径可复核（切片自实测净值）
        assert (fw.EVIDENCE_DIR / "latest.json").exists()

    def test_idempotent_skip_on_same_fingerprint(self, isolated, monkeypatch):
        _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True, "risk_admitted": True, "cash_closure_admitted": True,
                           "gate_passed": True},
            "evidence_path": "latest.json",
        })
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out.get("skipped") and "fingerprint_unchanged" in out["skipped"]

    def test_evidence_without_gate_passed_forces_reeval(self, isolated, monkeypatch):
        """三段门控（H5-B）后接前写的证据无 gate_passed → 不得据其短路（与账本闸同族）。

        幂等闸的语义是"同一份已验收证据不必重跑"；门控成为验收要件之前产出的证据没有
        这项证据，短路它等于用新口径给旧证据背书——被门控拒的策略会永不再判。
        """
        calls = _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True, "risk_admitted": True, "cash_closure_admitted": True},
            "evidence_path": "latest.json",
        })
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert not out.get("skipped"), out
        assert calls and out["acceptance"]["gate_passed"] is True

    def test_evidence_without_cash_closure_forces_reeval(self, isolated, monkeypatch):
        """账本闸（#24 H4-B）后接前写的证据无 cash_closure_admitted → 不得据其短路。

        与 test_legacy_ok_evidence_forces_reeval 同族：幂等闸的语义是"同一份已验收
        证据不必重跑"，而账本闭合成为验收要件之前产出的证据并没有这项证据，短路它
        等于用新口径给旧证据背书。
        """
        calls = _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True, "risk_admitted": True},  # 缺 cash_closure_admitted
            "evidence_path": "latest.json",
        })
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert not out.get("skipped"), out
        assert calls and out["acceptance"]["cash_closure_admitted"] is True

    def test_force_bypasses_idempotent_skip(self, isolated, monkeypatch):
        calls = _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True, "risk_admitted": True}})
        out = fw.run_fw_backtest_due({"payload": {"force": True}})
        assert out["ok"] is True and calls  # force 越过幂等闸真实重跑

    def test_legacy_ok_evidence_forces_reeval(self, isolated, monkeypatch):
        """车道 L 接线前的老证据只有 ok=True 无 risk_admitted → 不得据其短路，必须重跑复评。"""
        calls = _patch_happy_path(monkeypatch)
        monkeypatch.setattr(fw, "_latest_evidence", lambda: {
            "plan": {"fingerprint": _FP["fingerprint"]},
            "acceptance": {"ok": True},  # 老证据：风险闸从未接，无 risk_admitted 字段
            "evidence_path": "latest.json",
        })
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert not out.get("skipped")  # 未被幂等闸短路
        assert calls  # 真实重跑并复评风险
        assert "risk_admitted" in out["acceptance"]

    def test_over_tolerance_no_retry(self, isolated, monkeypatch):
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(within=False))
        out = fw.run_fw_backtest_due({"payload": {}})  # 不 raise（语义失败不重试）
        assert out["ok"] is False
        assert out["acceptance"]["within_tolerance"] is False
        assert any(lv == "ERROR" for lv, _ in isolated["alerts"])
        assert Path(out["evidence_path"]).exists()

    def test_overfitting_strategy_rejected(self, isolated, monkeypatch):
        """P0：现网 bt-fw-823d7fd7 型——overfitting_flag=True 必须判 ok=false（禁静默放行）。"""
        _patch_happy_path(monkeypatch,
                          run_result=_fake_run_result(overfitting=True, dsr=0.000049, n_trials=4497))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is False
        assert out["acceptance"]["risk_admitted"] is False
        assert out["acceptance"]["overfitting_flag"] is True
        assert any(lv == "ERROR" and "风险闸否决" in m for lv, m in isolated["alerts"])

    def test_dsr_below_significance_line_rejected(self, isolated, monkeypatch):
        """DSR 中间带（0.5<=dsr<0.95，overfitting_flag=False）仍 fail-closed 拒——不误放行。"""
        _patch_happy_path(monkeypatch,
                          run_result=_fake_run_result(overfitting=False, dsr=0.7, n_trials=4497))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is False
        assert out["acceptance"]["risk_admitted"] is False

    def test_real_n_trials_recorded_in_evidence(self, isolated, monkeypatch):
        """n_trials 真值（非硬编码 10）随验收落证据包（来源可溯）。"""
        _patch_happy_path(monkeypatch,
                          run_result=_fake_run_result(overfitting=False, dsr=0.98, n_trials=4497))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is True
        assert out["acceptance"]["n_trials"] == 4497
        assert out["acceptance"]["n_trials"] != 10  # 绝非旧的拍脑袋默认
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        assert body["run"]["risk_decision"]["n_trials"] == 4497

    def test_dsr_recomputed_from_artifact_single_source(self, isolated, monkeypatch):
        """产物 metrics 缺 dsr 时，从净值序列用同一真源复算 n_trials，且仍走 fail-closed 判据。"""
        import pandas as pd

        res = _fake_run_result(overfitting=False)
        res["metrics"].pop("dsr", None)  # 模拟引擎 sink 不上收 dsr 的现网形态
        res["metrics"].pop("n_trials", None)
        res["metrics"].pop("n_trials_source", None)
        _patch_happy_path(monkeypatch, run_result=res)
        monkeypatch.setattr(
            fw, "_load_artifact_nav",
            lambda run_id: pd.Series([1_000_000 + 3_000 * i for i in range(120)]),
        )
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        rd = out["acceptance"]
        assert rd["dsr"] is not None  # 复算成功
        assert rd["n_trials"] is not None and rd["n_trials"] >= 1  # 真值来源，非 None

    def test_staged_gate_vetoes_time_degradation_even_with_clean_flag(self, isolated, monkeypatch):
        """H5-B 反证：旗标 False、DSR 达标，但净值后段塌陷 → 三段门控独立否决（门控非装饰）。

        阈值一律取 DecisionGate 既有真源，本用例只证"消费端确实读了它的结论"：
        IS 段过、WFA/OOS 段不过 → ok=False + gate_reasons 摊开 + ERROR 留痕。
        """
        _write_nav_artifact(isolated["artifact_dir"], mode="collapse")  # 覆写同 run_id
        _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        acc = out["acceptance"]
        assert out["ok"] is False
        assert acc["risk_admitted"] is True  # 风险闸（旗标/DSR）独独放行不了
        assert acc["gate_passed"] is False and acc["gate_is_passed"] is True
        assert acc["gate_wfa_passed"] is False and acc["gate_oos_passed"] is False
        assert acc["gate_wfa_windows"] == "0/2"
        assert any("Walk-Forward" in r or "OOS" in r for r in acc["gate_reasons"])
        assert any(lv == "ERROR" and "三段门控否决" in m for lv, m in isolated["alerts"])

    def test_staged_gate_fail_closed_without_nav_evidence(self, isolated, monkeypatch):
        """缺净值证据（产物缺件/样本切不出 IS+2 折）→ 门控按不通过处理，禁"没测=通过"。"""
        for p in isolated["artifact_dir"].glob("bt-*.json"):
            p.unlink()  # 模拟引擎产物未落/读不回
        _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        acc = out["acceptance"]
        assert out["ok"] is False
        assert acc["gate_passed"] is False and acc["gate_can_deploy"] is False
        assert any("fail-closed" in r for r in acc["gate_reasons"])
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        assert body["run"]["staged_gate_decision"]["evidence"] is None  # 缺件如实留痕，不补默认
        assert any(lv == "ERROR" and "三段门控否决" in m for lv, m in isolated["alerts"])

    def test_dead_member_alpha_over_limit_vetoes_acceptance(self, isolated, monkeypatch):
        """P0 组合完整性（T1A-2 消费端）：44.1% 未兑现 α 必须判 ok=false——warn 只进日志=知情放行。"""
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(dead_share=0.441))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is False
        acc = out["acceptance"]
        assert acc["run_ok"] is True and acc["risk_admitted"] is True  # 唯组合闸否决
        assert acc["composition_admitted"] is False
        assert acc["composition_over_limit"] is True
        assert acc["skipped_alpha_share"] == pytest.approx(0.441)
        assert any(lv == "ERROR" and "组合完整性闸否决" in m for lv, m in isolated["alerts"])
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        assert body["run"]["dead_weight_disclosed"]["skipped_alpha_share_of_plan"] == 0.441
        assert body["run"]["composition_decision"]["accepted"] is False

    def test_dead_member_alpha_under_limit_accepts(self, isolated, monkeypatch):
        """限额内的摊派仍放行，但份额必须落证据（可审计，不是布尔黑洞）。"""
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(dead_share=0.2))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is True
        assert out["acceptance"]["composition_admitted"] is True
        assert out["acceptance"]["composition_over_limit"] is False
        assert out["acceptance"]["skipped_alpha_share"] == pytest.approx(0.2)

    def test_missing_composition_disclosure_fails_closed(self, isolated, monkeypatch):
        """无 dead_weight_disclosed=无证据，与风险闸"缺失即拒"同族，禁默认放行。"""
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(dead_share=None))
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        assert out["ok"] is False
        assert out["acceptance"]["composition_admitted"] is False
        assert any("dead_weight_disclosed" in r for r in out["acceptance"]["composition_reasons"])

    def test_composition_threshold_shares_single_truth_source(self, isolated, monkeypatch):
        """阈值边界一律取 composer 常量（禁消费端另写字面量）——恰好等于限额仍放行。"""
        from zephyr.pf_core.strategy_engine.framework_composer import (
            DEAD_MEMBER_ALPHA_SHARE_LIMIT as LIMIT,
        )

        _patch_happy_path(monkeypatch, run_result=_fake_run_result(dead_share=LIMIT))
        assert fw.run_fw_backtest_due({"payload": {}})["ok"] is True
        _patch_happy_path(monkeypatch, run_result=_fake_run_result(dead_share=LIMIT + 1e-6))
        vetoed = fw.run_fw_backtest_due({"payload": {}})
        assert vetoed["ok"] is False
        assert vetoed["acceptance"]["composition_admitted"] is False

    def test_generator_failure_raises(self, isolated, monkeypatch):
        monkeypatch.setattr(fw, "_run_generator",
                            lambda t: (_ for _ in ()).throw(RuntimeError("方案表生成器失败 rc=1")))
        with pytest.raises(RuntimeError, match="生成器失败"):
            fw.run_fw_backtest_due({"payload": {}})  # 瞬时故障上抛→journal 留档重试


class TestGuardDegradationLedger:
    """H5-D：引擎侧 4 处 fail-open 护栏降级在消费侧计数可见（观测面，不新增否决权）。"""

    @staticmethod
    def _emit_engine_degradations(run_result: dict):
        """复刻引擎真实出声（同进程同 logger 家族），令采集器计数为当次真值。"""
        logging.getLogger("zephyr.backtest.core.engines.vectorized_engine").warning(
            "PIT 上市/退市窗口不可用: 标的池过滤降级（当日不做幸存者/次新剔除）")
        logging.getLogger("zephyr.backtest.core.engines.vectorized_engine").warning(
            "PIT ST 判定失败: 600000 该轮不剔 ST")
        logging.getLogger("zephyr.backtest.core.engines.event_driven_engine").warning(
            "冲击成本旁路: 报价失败 → 按无冲击成交")
        logging.getLogger("zephyr.backtest.core.engines.event_driven_engine").warning(
            "成交量上限/冲击成本自动旁路: 面板无 volume 列")
        return run_result

    def _patch_run_that_degrades(self, monkeypatch, run_result: dict):
        calls = _patch_happy_path(monkeypatch, run_result=run_result)
        monkeypatch.setattr(
            fc, "run_framework_backtest",
            lambda plan_id, symbols, start, end, config=None: self._emit_engine_degradations(run_result),
        )
        return calls

    def test_engine_fail_open_counted_and_warned(self, isolated, monkeypatch):
        self._patch_run_that_degrades(monkeypatch, _fake_run_result())
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        acc = out["acceptance"]
        assert acc["degraded_guard_n"] >= 4
        for gid in ("pit_universe_filter", "pit_st_filter", "impact_cost_model",
                    "liquidity_participation_cap"):
            assert gid in acc["degraded_guards"], acc["degraded_guards"]
        body = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))
        ledger = body["run"]["guard_degradation_ledger"]
        by_guard = {g["guard"]: g for g in ledger["degraded"]}
        assert by_guard["pit_universe_filter"]["count"] == 1  # 计数=当次真事件数，非布尔
        assert by_guard["pit_universe_filter"]["source"] == "engine_log_observed"
        assert "标的池过滤降级" in by_guard["pit_universe_filter"]["sample"]
        warns = [m for lv, m in isolated["alerts"] if lv == "WARN" and "护栏降级" in m]
        assert len(warns) >= 4  # 每条降级各自出声一次

    def test_ledger_visibility_only_no_new_veto(self, isolated, monkeypatch):
        """配置性旁路 + 门控证据缺件都入账，但不得凭此否决（升格否决属 Owner 门位）。"""
        _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount",
                                                 "symbols": ["600000"]}})
        assert out["ok"] is True  # 有降级账，仍按既有四闸放行
        acc = out["acceptance"]
        assert "pit_universe_window" in acc["degraded_guards"]  # payload 自报标的池
        assert "regime_dynamic_overlay" in acc["degraded_guards"]  # 打桩 regime=static
        assert "is_param_plateau_gate" in acc["degraded_guards"]  # DecisionGate 自报跳过
        assert "phase5_regime_gate" in acc["degraded_guards"]
        assert "stk_limit_provider" not in acc["degraded_guards"]  # 默认开闸=在岗

    def test_clean_run_still_enumerates_watched_guards(self, isolated, monkeypatch):
        """本次未听见过降级出声 → 观测项不入 degraded，但七项全在 watched 清单里可枚举。"""
        _patch_happy_path(monkeypatch)
        out = fw.run_fw_backtest_due({"payload": {"trigger": "auto_mount"}})
        ledger = json.loads(Path(out["evidence_path"]).read_text(encoding="utf-8"))[
            "run"]["guard_degradation_ledger"]
        assert ledger["schema"] == "degraded_guards/v1"
        assert ledger["log_watch_patterns"] == 7
        assert len(ledger["watched"]) == 12  # 7 引擎出声 + 3 消费侧配置 + 2 门控证据缺件
        assert "fill_integrity" in ledger["watched"]
        observed = [g["guard"] for g in ledger["degraded"] if g["source"] == "engine_log_observed"]
        assert observed == []  # 没听见就不记——但下面 note 说明"未听见≠健康"
        assert "未听见" in ledger["note"]
        assert "fill_integrity" not in out["acceptance"]["degraded_guards"]


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
