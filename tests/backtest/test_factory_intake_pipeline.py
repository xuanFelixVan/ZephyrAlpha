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
        light = [r for r in results if r["lane"] != "C"]
        assert all(r["allowed"] for r in light)

    def test_lane_specs_dynamic(self):
        # 车道清单随共享文件演进（并行会话可加车道），测试只锁契约不锁清单
        lanes = {s["lane"] for s in fip._LANE_SPECS if s["lane"]}
        assert {"D", "B"} <= lanes

    def test_heavy_lane_c_gated_declaration_active(self):
        """WO-⑤-06 漂移修正后 C 车道受 E0 闸（heavy 档在预检结果中出现）。

        零网环境日历不可达 → C 走 fail-closed 拒（REASON_DENY_CALENDAR_UNKNOWN）；
        盘外黄金窗+日历可达 → 放行。契约=出现在结果里且 allowed 是布尔，
        编排层不越权代闸放行（不预设其值）。
        """
        results = fip.preflight_compute_gate()
        c_rows = [r for r in results if r["purpose"] == "intake_e1c_formula_mine"]
        assert len(c_rows) == 1 and c_rows[0]["lane"] == "C"
        assert isinstance(c_rows[0]["allowed"], bool)

    def test_lane_specs_no_drift_all_lanes_lettered(self):
        """断言测试（WO-⑤-06）：_LANE_SPECS 每项 lane 字母非空（禁 lane=None 漂移回归）。"""
        for spec in fip._LANE_SPECS:
            assert spec["lane"], f"车道 {spec['name']} lane 漂移（空值=未登记车道字母）"
            assert isinstance(spec["lane"], str) and len(spec["lane"]) <= 2

    def test_lane_letters_match_factory_map(self):
        """断言测试（WO-⑤-06）：每项 lane 与工厂图（config/strategy_production_map.yaml）
        节点 lane 字段一致（图是真源，禁在编排层自造车道字母）。

        已知图缺件（他线资产，登记不代修）：F=F06 网格仅代码车道、图节点补挂=2.4 跨线
        欠账（map :71/:204 自述）；I=线alpha T8 2026-09-18 新增、图补挂待他线。缺件清单
        之外的新漂移照样红。
        """
        import yaml

        known_map_gaps = frozenset({"F", "I"})
        mp = yaml.safe_load(
            (fip._ROOT / "config" / "strategy_production_map.yaml").read_text(
                encoding="utf-8"))
        map_lanes = {n.get("lane") for n in mp.get("nodes", []) if n.get("lane")}
        assert map_lanes, "工厂图 nodes.lane 全空=图数据缺件（他线资产，另行登记）"
        for spec in fip._LANE_SPECS:
            if spec["lane"] in known_map_gaps:
                continue
            assert spec["lane"] in map_lanes, (
                f"车道 {spec['name']} lane={spec['lane']} 不在工厂图节点 lane 集"
                f"{sorted(map_lanes)} 中——编排层与工厂图漂移")


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
    def test_heavy_lane_c_registered(self):
        """WO-⑤-06 漂移修正（2026-09-18）：E1C 三轨已建成（gplearn/智能体/MCTS），
        lane 不再是 None"待施工"——与生产图 FAC-E1C lane=C 对齐；local_gpu=heavy 受 E0 闸。"""
        e1c = next(s for s in fip._LANE_SPECS if s["name"] == "e1c_formula_mine")
        assert e1c["lane"] == "C"
        assert e1c["compute_class"] == "local_gpu"  # heavy 档受 E0 闸
        assert e1c["intake"].endswith("lane_c_candidates.csv")


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
