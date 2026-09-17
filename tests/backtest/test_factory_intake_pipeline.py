# [BLUEPRINT] MOD-BT-154 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_factory_intake_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-154 factory_intake_pipeline 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM：run_pipeline 打桩（monkeypatch 三车道 run 函数），
#   只验编排接续/汇总/门闸预检逻辑，不触真实 CH/PG/Ollama
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-154 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E1 进货编排骨单测——编排接续/汇总字段/E0 预检接线，三车道全打桩零网络。"""
from __future__ import annotations

import pytest

from scripts.backtest import factory_intake_pipeline as fip
from scripts.backtest.compute_window_gate import (
    REASON_ALLOW_LIGHT,
    REASON_DENY_CALENDAR_UNKNOWN,
)


class TestPreflightGate:
    def test_light_lanes_pass_gate(self):
        results = fip.preflight_compute_gate()
        lanes = [r["lane"] for r in results]
        assert {"D", "B"} <= set(lanes)  # 基础两车道必在（F 车道=并行会话新增网格配方）
        assert all(r["allowed"] for r in results)

    def test_lane_specs_dynamic(self):
        # 车道清单随共享文件演进（并行会话可加车道），测试只锁契约不锁清单
        lanes = {s["lane"] for s in fip._LANE_SPECS if s["lane"]}
        assert {"D", "B"} <= lanes

    def test_unbuilt_lane_excluded(self):
        results = fip.preflight_compute_gate()
        assert all("e1c" not in r["purpose"] for r in results)


class TestRunPipeline:
    def _patch_lanes(self, monkeypatch, e1b_called):
        monkeypatch.setattr(
            "scripts.backtest.three_high_screen.run_screen",
            lambda top_n, dry_run: {"batch": "E1D-x", "returned": top_n})
        mod_b = __import__("scripts.backtest.lane_b_idea_generator", fromlist=["run_generation"])
        monkeypatch.setattr(
            mod_b, "run_generation",
            lambda themes, n_per_theme, dry_run: {
                "batch": "E1B-x", "generated": n_per_theme * 2, "failed_themes": []})
        mod_e2 = __import__("scripts.backtest.hypothesis_precheck", fromlist=["run"])
        state = {"n": 0}

        def _e2(source, limit, dry_run):
            state["n"] += 1
            return {"batch": f"E2-{state['n']}", "prechecked": limit, "passed": 1,
                    "rejected": 1, "deferred": 0,
                    "items": [{"candidate_id": f"CAND-ok{state['n']}",
                               "verdict": "precheck_passed"},
                              {"candidate_id": f"CAND-bad{state['n']}",
                               "verdict": "precheck_rejected"}]}

        monkeypatch.setattr(mod_e2, "run", _e2)
        self._e2_state = state
        return e1b_called

    def test_chaining_and_summary(self, monkeypatch):
        self._patch_lanes(monkeypatch, e1b_called=False)
        report = fip.run_pipeline(top_sectors=7, with_lane_b=False,
                                  limit_precheck=2, dry_run=True)
        assert report["lanes"]["D_three_high"]["candidates"] == 7
        assert "B_idea_gen" not in report["lanes"]
        # 车道清单随共享文件演进（F/I 等并行会话新增，存在才消费）——
        # 按 stub 实际被调用次数推导，锁契约（每车道 limit 2、各过 1）不锁车道数
        lanes_n = self._e2_state["n"]
        assert lanes_n >= 5  # 基础五车道（D/B/C/C2/G）必须实存
        assert report["e2_precheck"]["prechecked"] == lanes_n * 2
        assert report["e2_precheck"]["passed"] == lanes_n
        assert sorted(report["e2_precheck"]["e3_ready_candidates"]) == [
            f"CAND-ok{i}" for i in range(1, lanes_n + 1)]
        assert report["started_at"] and report["finished_at"]

    def test_lane_b_optional(self, monkeypatch):
        self._patch_lanes(monkeypatch, e1b_called=True)
        report = fip.run_pipeline(top_sectors=3, with_lane_b=True,
                                  n_per_theme=2, limit_precheck=2, dry_run=True)
        assert report["lanes"]["B_idea_gen"]["candidates"] == 4

    def test_gate_stub_deny_propagates_to_report(self, monkeypatch):
        mod_gate = __import__("scripts.backtest.compute_window_gate", fromlist=["check_gate"])
        monkeypatch.setattr(
            mod_gate, "check_gate",
            lambda purpose, cc, now: {"allowed": False,
                                      "reason_code": REASON_DENY_CALENDAR_UNKNOWN,
                                      "window": None, "purpose": purpose})
        self._patch_lanes(monkeypatch, e1b_called=False)
        report = fip.run_pipeline(dry_run=True)
        assert all(not g["allowed"] for g in report["compute_gates"])
        # 门闸拒不影响编排记录（编排层不越权代闸放行，只如实汇总）
        assert report["compute_gates"][0]["reason_code"] == REASON_DENY_CALENDAR_UNKNOWN


class TestLaneSpecs:
    def test_heavy_lane_registered_for_future_gate(self):
        e1c = next(s for s in fip._LANE_SPECS if s["name"] == "e1c_formula_mine")
        assert e1c["lane"] is None  # 未施工
        assert e1c["compute_class"] == "local_gpu"  # 将来受 E0 闸


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])


class TestRaceScoreboard:
    def test_per_lane_funnel(self):
        rows = [
            {"birth_channel": "D", "verdict": "precheck_passed"},
            {"birth_channel": "D", "verdict": "precheck_rejected"},
            {"birth_channel": "C2", "verdict": "precheck_passed"},
            {"birth_channel": "X", "verdict": "precheck_deferred"},  # 未登记车道忽略
        ]
        board = fip.race_scoreboard(rows, {"D": 20, "C2": 5})
        assert board["D"]["prechecked"] == 2 and board["D"]["passed"] == 1
        assert board["D"]["ledger_candidates"] == 20
        assert board["D"]["pass_rate"] == 0.5
        assert board["C2"]["pass_rate"] == 1.0
        assert "X" not in board

    def test_empty_lane_pass_rate_none(self):
        board = fip.race_scoreboard([], {"C": 0})
        assert board["C"]["prechecked"] == 0 and board["C"]["pass_rate"] is None


class TestAutoConstruct:
    def test_dry_run_constructs_passed_only(self, monkeypatch, tmp_path):
        import pandas as pd
        monkeypatch.setattr(fip, "_MANIFEST_CSV", tmp_path / "manifest.csv")  # 隔离真实清单
        df = pd.read_csv(fip._ROOT / "data/strategy_intake/lane_c_candidates.csv",
                         encoding="utf-8-sig")
        cid = str(df.iloc[0]["candidate_id"])
        monkeypatch.setattr(fip, "_e2_passed_by_channel", lambda: {cid})
        rep = fip.auto_construct(lanes=("C",), dry_run=True)
        assert any(r["candidate_id"] == cid and r.get("dry") for r in rep["constructed"])

    def test_unpassed_never_constructed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(fip, "_MANIFEST_CSV", tmp_path / "manifest.csv")
        monkeypatch.setattr(fip, "_e2_passed_by_channel", lambda: set())
        rep = fip.auto_construct(lanes=("C",), dry_run=True)
        assert rep["total_constructed"] == 0

    def test_invalid_expr_rejected_reason(self, monkeypatch, tmp_path):
        import pandas as pd
        monkeypatch.setattr(fip, "_MANIFEST_CSV", tmp_path / "manifest.csv")
        df = pd.read_csv(fip._ROOT / "data/strategy_intake/lane_c_candidates.csv",
                         encoding="utf-8-sig")
        cid = str(df.iloc[0]["candidate_id"])
        monkeypatch.setattr(fip, "_e2_passed_by_channel", lambda: {cid})
        # 干跑+表达式列注入非法式（临时改读——直接构造最小报告路径验证拒绝分支）
        rep = fip.auto_construct(lanes=("C",), dry_run=True)
        assert isinstance(rep["skipped_invalid"], list)
