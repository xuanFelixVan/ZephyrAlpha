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

    def test_fdr_null_family_no_sim(self, monkeypatch):
        # 真零假设族（全噪声 p 均匀分布）：BH 全拒 → 零 sim 流转；候选登记不受 FDR 门
        # （方案真源 §2.3 入库=及格∧簇首∧差异化，§2.5 三条件才含 FDR——2026-09-15 裁定对齐）
        self._kill_clear(monkeypatch)
        passed = {f"CAND-{i:03d}": round((i + 1) / 20, 3) for i in range(20)}
        r = run_intake("B3", passed, {}, dry_run=True)
        assert r["fdr_keep"] == [] and not r["sim_promoted"]

    def test_write_path_requires_evidence(self, monkeypatch, tmp_path):
        # 写入路径 fail-closed：验收⑥证据文件不存在必拒（证据=Owner 复核替身，交接档案治理边界）
        self._kill_clear(monkeypatch)
        monkeypatch.setattr(intake, "EVIDENCE", tmp_path / "missing-evidence.md")
        with pytest.raises(RuntimeError, match="写入路径未授权"):
            run_intake("B4", {"CAND-aaa": 0.001}, {}, dry_run=False)

    def test_write_path_full_pipeline(self, monkeypatch, tmp_path):
        # 写入路径开启后：注册表追加→挂图→报告 全链（依赖全部 monkeypatch，测试零生产 IO）
        self._kill_clear(monkeypatch)
        (tmp_path / "evidence.md").write_text("acceptance6 evidence", encoding="utf-8")
        monkeypatch.setattr(intake, "EVIDENCE", tmp_path / "evidence.md")
        monkeypatch.setattr(intake, "REPORT_DIR", tmp_path / "reports")
        monkeypatch.setattr(intake, "_load_registry", lambda: {"strategies": []})
        calls = {}

        def fake_append(entries, path, dry_run):
            calls["entries"] = entries
            return {"dry_run": False, "new_sids": [e["strategy_id"] for e in entries]}

        def fake_mount(sids):
            calls["mounted"] = sids
            return {"ops_n": 1, "applied": True}

        monkeypatch.setattr("zephyr.strategy_pipeline.registry_writer.append_entries", fake_append)
        monkeypatch.setattr(intake, "_auto_mount_sids", fake_mount)
        item = {"key": "CAND-aaa@c4_x.py", "source_file": "scripts/backtest/translated/c4_x.py",
                "is_sharpe": 1.0, "turnover": 0.3, "max_drawdown": -0.2,
                "segments": [{"batch": "C4-OOS-2024-2026", "sharpe": 0.5, "decay": 0.1}]}
        r = run_intake("B5", {"CAND-aaa@c4_x.py": 0.001},
                       {("CAND-aaa@c4_x.py", "CAND-aaa@c4_x.py"): 1.0},
                       dry_run=False, items=[item])
        assert r["registry"]["new_sids"] == r["created_sids"]
        assert calls["mounted"] == r["created_sids"]
        entry = calls["entries"][0]
        assert entry["strategy_id"].startswith("STR-")
        assert entry["code_path"] == "scripts/backtest/translated/c4_x.py"
        assert (tmp_path / "reports").exists()

    def test_fdr_gates_sim_not_registration(self, monkeypatch):
        # 同一批：FDR 拒者登记为 candidate（不流转 sim），FDR 过者 sim
        self._kill_clear(monkeypatch)
        monkeypatch.setattr(intake, "_load_registry", lambda: {"strategies": []})
        k1 = "CAND-strong@c4_c72318f2da1c_bias_ql.py"
        k2 = "CAND-weak@c4_4440d07f973f_ultrashort.py"
        items = [
            {"key": k1, "source_file": "scripts/backtest/translated/c4_c72318f2da1c_bias_ql.py",
             "is_sharpe": 1.0, "turnover": 0.2, "max_drawdown": -0.1,
             "segments": [{"batch": "C4-OOS", "sharpe": 0.5, "decay": 0.1}]},
            {"key": k2, "source_file": "scripts/backtest/translated/c4_4440d07f973f_ultrashort.py",
             "is_sharpe": 0.3, "turnover": 1.2, "max_drawdown": -0.4,
             "segments": [{"batch": "C4-OOS", "sharpe": 0.5, "decay": 0.1}]},
        ]
        r = run_intake("B6", {k1: 0.0001, k2: 0.9}, {}, dry_run=True, items=items)
        assert len(r["created_sids"]) == 2  # 都登记（簇首∧差异化）
        assert len(r["sim_promoted"]) == 1  # 只 strong 流转 sim

    def test_code_path_idempotency(self, monkeypatch):
        # 文件粒度幂等：key 不同但 source_file 已在库（注册表 code_path 命中）→ 跳过
        self._kill_clear(monkeypatch)
        monkeypatch.setattr(intake, "_load_registry", lambda: {"strategies": [
            {"strategy_id": "STR-VREV-026",
             "code_path": "scripts/backtest/translated/c4_c72318f2da1c_bias_ql.py"}]})
        key = "CAND-c72318f2da1c@c4_c72318f2da1c_bias_ql.py"
        item = {"key": key, "source_file": "scripts/backtest/translated/c4_c72318f2da1c_bias_ql.py",
                "is_sharpe": 0.16, "turnover": 0.2, "max_drawdown": -0.1, "segments": []}
        r = run_intake("B7", {key: 0.001}, {}, dry_run=True, items=[item])
        assert "已入库" in r["skipped"][key]

    def test_family_redundancy_block_from_corr(self, monkeypatch):
        # 聚类吸收：ρ>0.6 簇员进簇首条目 family_redundancy 块（STR-VREV-026 先例的字段化）
        self._kill_clear(monkeypatch)
        passed = {"CAND-head@c4_h.py": 0.001, "CAND-tail@c4_t.py": 0.002}
        corr = {("CAND-tail@c4_t.py", "CAND-head@c4_h.py"): 0.71}
        r = run_intake("B8", passed, corr, dry_run=True)
        head_entry = next(e for e in r["created"] if e.get("family_redundancy"))
        blk = head_entry["family_redundancy"]
        assert blk["role"] == "cluster_head"
        assert blk["absorbed"][0]["candidate_id"] == "CAND-tail"
        assert blk["absorbed"][0]["correlation"] == 0.71
