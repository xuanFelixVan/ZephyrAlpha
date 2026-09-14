# [BLUEPRINT] MOD-BT-189 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_intake
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.intake
# [CONSUMERS] MOD-BT-189 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零 IO（monkeypatch 注册表/KillSwitch）；默认 dry_run=True 防误写
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/intake.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-189 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""intake 编排测试——验收①②⑤条款的编排层部分（幂等/KillSwitch/簇首/FDR 联动/差异化拒收）。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import intake  # noqa: E402
from zephyr.strategy_pipeline.intake import (  # noqa: E402
    cluster_heads,
    differentiation_ok,
    fdr_gate,
    next_strategy_number,
    promote_to_sim,
    run_intake,
)
from zephyr.strategy_pipeline.lifecycle_fsm import build_strategy_fsm  # noqa: E402


class TestClusterHeads:
    def test_greedy_clustering_deterministic(self):
        corr = {("CAND-b", "CAND-a"): 0.7, ("CAND-c", "CAND-a"): 0.65}
        heads, redundant = cluster_heads(corr, {"CAND-a", "CAND-b", "CAND-c", "CAND-d"})
        assert heads == {"CAND-a", "CAND-d"}
        assert redundant == {"CAND-b": "CAND-a", "CAND-c": "CAND-a"}

    def test_below_rho_no_cluster(self):
        corr = {("CAND-b", "CAND-a"): 0.55}
        heads, _ = cluster_heads(corr, {"CAND-a", "CAND-b"}, rho=0.6)
        assert heads == {"CAND-a", "CAND-b"}


class TestDifferentiation:
    def test_reject_when_all_axes_same(self):
        reg = [{"strategy_id": "STR-OLD-001", "strategy_class": "mined",
                "holding_period": "波段", "sleeve": "alpha"}]
        ok, why = differentiation_ok({"signal_axis": "mined", "holding_period": "波段",
                                      "state_adaptation": "alpha"}, reg)
        assert not ok and "STR-OLD-001" in why

    def test_pass_when_one_axis_differs(self):
        reg = [{"strategy_id": "STR-OLD-001", "strategy_class": "mined",
                "holding_period": "波段", "sleeve": "hedge"}]
        ok, why = differentiation_ok({"signal_axis": "mined", "holding_period": "波段",
                                      "state_adaptation": "alpha"}, reg)
        assert ok


class TestNextNumber:
    def test_sequential(self, tmp_path, monkeypatch):
        monkeypatch.setattr(intake, "REGISTRY", tmp_path / "no.yaml")
        assert next_strategy_number({"strategies": [
            {"strategy_id": "STR-AUTO-001"}, {"strategy_id": "STR-AUTO-003"}]}, "AUTO") == 4
        assert next_strategy_number({"strategies": []}, "AUTO") == 1


class TestPromoteToSim:
    def test_full_pass(self):
        fsm = build_strategy_fsm("STR-T-001")
        ok, why = promote_to_sim(fsm, dual=True, fdr=True, no_decay=True)
        assert ok and fsm.current_state == "sim"

    def test_fail_when_any_condition_false(self):
        for kw in ({"dual": False}, {"fdr": False}, {"no_decay": False}):
            fsm = build_strategy_fsm("STR-T-002")
            ok, _ = promote_to_sim(fsm, dual=kw.get("dual", True), fdr=kw.get("fdr", True),
                                   no_decay=kw.get("no_decay", True))
            assert not ok and fsm.current_state == "candidate"


class TestRunIntake:
    def _kill_clear(self, monkeypatch, clear=True):
        monkeypatch.setattr(intake, "_kill_switch_clear", lambda: clear)

    def test_end_to_end_replay_idempotent(self, monkeypatch):
        # 同批重放：第二次全部 skipped=已入库（验收②编排层）
        passed = {"CAND-aaa": 0.001, "CAND-bbb": 0.4}
        corr = {("CAND-bbb", "CAND-aaa"): 0.7}
        self._kill_clear(monkeypatch)
        r1 = run_intake("B1", passed, corr, dry_run=True)
        assert r1["promoted"] and "CAND-aaa" in r1["fdr_keep"]
        # 模拟已入库：库内已有簇首映射 id
        monkeypatch.setattr(intake, "_load_registry", lambda: {"strategies": [
            {"strategy_id": "CAND-aaa", "strategy_class": "mined",
             "holding_period": "波段", "sleeve": "alpha"}]})
        r2 = run_intake("B1", passed, corr, dry_run=True)
        assert "CAND-aaa" in r2["skipped"]

    def test_kill_switch_blocks(self, monkeypatch):
        self._kill_clear(monkeypatch, clear=False)
        with pytest.raises(RuntimeError, match="KillSwitch"):
            run_intake("B2", {"CAND-aaa": 0.001}, {}, dry_run=True)

    def test_fdr_rejects_null_batch(self, monkeypatch):
        self._kill_clear(monkeypatch)
        passed = {f"CAND-{i:03d}": round((i + 1) / 20, 3) for i in range(20)}
        r = run_intake("B3", passed, {}, dry_run=True)
        assert r["fdr_keep"] == [] and not r["promoted"]

    def test_write_path_fail_closed(self, monkeypatch):
        # 验收⑥前写入路径必须 fail-closed（Owner 复核后才开启）
        self._kill_clear(monkeypatch)
        with pytest.raises(NotImplementedError):
            run_intake("B4", {"CAND-aaa": 0.001}, {}, dry_run=False)
