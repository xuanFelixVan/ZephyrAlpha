# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §red_blue_tests
# [DOMAIN] D_GOV_CODE_QUALITY
# [TESTS] tests/governance/test_alignment_gates_red_blue.py
# [TTL] permanent
"""对齐门禁红蓝对抗测试（#ARCH-DECISION-MAP-GATE-001 / #ARCH-BUSINESS-REG-GATE-001 / #ARCH-BATTLE-MAP-HARD-001）

红队（攻击注入→门禁必须阻断）：
  R1 地图 YAML 注入悬空 strategy_ref → DECISION-MAP 阻断
  R2 地图 YAML 注入 verified 无 evidence → 阻断
  R3 地图 YAML 注入 sequence 成环 → 阻断
  R4 业务库注入缺 module_id 条目 → BUSINESS-REGISTRY 阻断
  R5 业务库注入重复 id → 阻断
  R6 业务库注入非法 module_id 格式 → 阻断
  R7 作战地图 report 注入 ghost/orphan/narrative → 硬判定三连阻断
蓝队（防御验证→合法场景必须放行）：
  B1 仓库真源地图 run_checks 全绿
  B2 6 库整库校验全绿（基线 100%）
  B3 acknowledged 豁免环节不计违规（BM-BUY-05/14/SIM-08）
  B4 fail-open：battle_map 检测器异常 → 放行（return True）
  B5 文件未触发 → 秒回放行（BM gate/业务库 gate）
  B6 depgraph 不可达 → 业务库存在性子检查跳过不阻断
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
_GENERATORS = _REPO / "scripts" / "governance" / "d5_architecture" / "generators"
if str(_GENERATORS) not in sys.path:
    sys.path.insert(0, str(_GENERATORS))
if str(_REPO / "scripts" / "governance") not in sys.path:
    sys.path.insert(0, str(_REPO / "scripts" / "governance"))

from check_decision_map import collect_strategy_ids_via_ast  # noqa: E402
from check_decision_map import run_checks as dm_run_checks

from zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate import (  # noqa: E402
    evaluate_battle_map_report,
    make_battle_map_alignment_gate,
)
from zephyr.gov_enforcement.commit_gates.business_registry_gate import (  # noqa: E402
    REGISTRY_SPECS,
    make_business_registry_gate,
    validate_registry_file,
)
from zephyr.gov_enforcement.commit_gates.decision_map_gate import (  # noqa: E402
    make_decision_map_gate,
)

# ═══════════════════════ 红队：攻击注入 ═══════════════════════


def _write_map(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "trading_decision_map.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return p


def _bad_map_payload() -> dict:
    node = {
        "node_id": "TDM-T-1",
        "name_zh": "测试",
        "market": "cn_a",
        "flow": "entry_flow",
        "layer": "L9",
        "node_type": "stage",
        "point": "盘前",
        "decision_question": "测试",
        "factor_refs": [],
        "data_refs": [],
        "module_ref": None,
        "strategy_mounts": [],
    }
    return {
        "schema_version": "1.0",
        "map_id": "TDMAP-RED",
        "markets": ["cn_a"],
        "nodes": [node],
        "edges": [],
        "state_matrix": {"states": ["强势"], "cells": []},
    }


class TestRedDecisionMap:
    """红队：地图注入攻击 → DECISION-MAP gate 必须阻断。"""

    def _gate_check(self, tmp_path: Path) -> tuple[bool, str]:
        """用 tmp 地图替身跑 gate 闭包（monkeypatch 校验器模块级路径）。"""
        import check_decision_map as cdm

        gate = make_decision_map_gate()
        saved = (cdm._MAP_PATH, cdm._REGISTRY_DIR)
        try:
            cdm._MAP_PATH = tmp_path / "trading_decision_map.yaml"
            cdm._REGISTRY_DIR = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
            passed, detail = gate.check(gateway=None, files=["config/trading_decision_map.yaml"])
        finally:
            cdm._MAP_PATH, cdm._REGISTRY_DIR = saved
        return passed, detail

    def test_r1_dangling_strategy_ref_blocked(self, tmp_path: Path) -> None:
        payload = _bad_map_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "ghost-strategy", "confidence": "proposed", "evidence": None}
        ]
        _write_map(tmp_path, payload)
        passed, detail = self._gate_check(tmp_path)
        assert passed is False
        assert "R3" in detail and "ghost-strategy" in detail

    def test_r2_verified_without_evidence_blocked(self, tmp_path: Path) -> None:
        payload = _bad_map_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "verified", "evidence": None}
        ]
        _write_map(tmp_path, payload)
        passed, detail = self._gate_check(tmp_path)
        assert passed is False
        assert "R6" in detail

    def test_r3_sequence_cycle_blocked(self, tmp_path: Path) -> None:
        payload = _bad_map_payload()
        n2 = dict(payload["nodes"][0], node_id="TDM-T-2")
        payload["nodes"].append(n2)
        payload["edges"] = [
            {"from_node": "TDM-T-1", "to_node": "TDM-T-2", "edge_type": "sequence"},
            {"from_node": "TDM-T-2", "to_node": "TDM-T-1", "edge_type": "sequence"},
        ]
        _write_map(tmp_path, payload)
        passed, detail = self._gate_check(tmp_path)
        assert passed is False
        assert "R8" in detail

    def test_corrupt_yaml_fail_closed(self, tmp_path: Path) -> None:
        p = tmp_path / "trading_decision_map.yaml"
        p.write_text("schema_version: [unclosed", encoding="utf-8")
        passed, detail = self._gate_check(tmp_path)
        assert passed is False
        assert "fail-closed" in detail or "异常" in detail


class TestRedBusinessRegistry:
    """红队：业务库注入攻击 → BUSINESS-REGISTRY gate 必须阻断。"""

    def test_r4_entry_without_module_id_blocked(self, tmp_path: Path) -> None:
        p = tmp_path / "strategy_registry.yaml"
        p.write_text(
            yaml.safe_dump(
                {"strategies": [{"strategy_id": "STR-X-001", "module_id": None}]},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        fails = validate_registry_file(p, REGISTRY_SPECS[0])
        assert any("module_id" in f for f in fails)

    def test_r5_duplicate_id_blocked(self, tmp_path: Path) -> None:
        p = tmp_path / "factor_registry.yaml"
        p.write_text(
            yaml.safe_dump(
                {
                    "factors": [
                        {"factor_id": "FCT-X-001", "module_id": "MOD-A"},
                        {"factor_id": "FCT-X-001", "module_id": "MOD-A"},
                    ]
                },
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        fails = validate_registry_file(p, REGISTRY_SPECS[1])
        assert any("重复" in f for f in fails)

    def test_r6_bad_module_id_format_blocked(self, tmp_path: Path) -> None:
        p = tmp_path / "technical_indicator_registry.yaml"
        p.write_text(
            yaml.safe_dump(
                {"indicators": [{"indicator_id": "IND-X-001", "module_id": "WRONG-1"}]},
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
        fails = validate_registry_file(p, REGISTRY_SPECS[2])
        assert any("MOD-*" in f for f in fails)

    def test_corrupt_registry_fail_closed(self, tmp_path: Path) -> None:
        p = tmp_path / "strategy_registry.yaml"
        p.write_text("strategies: [broken", encoding="utf-8")
        with pytest.raises(Exception):
            validate_registry_file(p, REGISTRY_SPECS[0])


class TestRedBattleMap:
    """红队：作战地图 report 注入 → 硬判定三连阻断。"""

    @staticmethod
    def _report(**overrides) -> SimpleNamespace:
        base = dict(
            ghost_anchors=[],
            orphan_steps=[],
            missing_narratives=[],
            domain_drifts=[],
            dangling_edges=[],
            parent_child_issues=[],
            orphan_modules=[],
        )
        base.update(overrides)
        return SimpleNamespace(**base)

    def test_r7_ghost_anchor_blocked(self) -> None:
        hard, _ = evaluate_battle_map_report(self._report(ghost_anchors=[{"anchor_id": 1}]))
        assert any("BM-INV-002" in h for h in hard)

    def test_r7_orphan_step_blocked(self) -> None:
        hard, _ = evaluate_battle_map_report(self._report(orphan_steps=[{"step_id": "BM-GHOST-99"}]))
        assert any("BM-INV-001" in h for h in hard)

    def test_r7_missing_narrative_blocked(self) -> None:
        hard, _ = evaluate_battle_map_report(self._report(missing_narratives=[{"step_id": "BM-GHOST-98"}]))
        assert any("BM-INV-003" in h for h in hard)

    def test_orphan_modules_alone_not_blocking(self) -> None:
        """孤儿模块（G4 清淤）单独存在不得阻断。"""
        hard, soft = evaluate_battle_map_report(self._report(orphan_modules=[{"blueprint_id": "MOD-X"}]))
        assert hard == []
        assert any("BM-INV-007" in s for s in soft)


# ═══════════════════════ 蓝队：防御验证 ═══════════════════════


class TestBlueTruthSources:
    """蓝队：仓库真源必须全绿（基线回归锚）。"""

    def test_b1_repo_map_clean(self) -> None:
        fails, warns, total = dm_run_checks()
        assert fails == [], f"仓库地图存在 error: {fails}"
        assert total >= 15
        assert len(warns) > 0  # module_ref=null 红节点占位

    def test_b1b_ast_strategy_ids_contains_eight(self) -> None:
        ids = collect_strategy_ids_via_ast()
        assert "daban-sleeve" in ids and "vwap-reversion" in ids
        assert len(ids) >= 8

    def test_b2_six_registries_clean(self) -> None:
        catalogs = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
        for spec in REGISTRY_SPECS:
            fails = validate_registry_file(catalogs / spec.filename, spec)
            assert fails == [], f"{spec.filename} 存在违规: {fails}"

    def test_b3_acknowledged_excluded(self) -> None:
        """BM-BUY-05/14/SIM-08 已 acknowledged → 违规孤儿环节=0。"""
        from align_battle_map import run_alignment

        report = run_alignment(write_report=False)
        assert report.orphan_steps == []
        assert report.missing_narratives == []
        assert report.ghost_anchors == []
        assert len(report.acknowledged_orphan_steps) >= 18


class TestBlueFailOpenAndTrigger:
    """蓝队：fail-open 与文件触发语义。"""

    def test_b4_detector_exception_fail_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate as bmg

        monkeypatch.setattr(
            bmg, "_TRIGGER_SUFFIXES", ("__never_matches__.yaml",), raising=False
        )  # 不触发路径，直接验证未触发分支
        gate = make_battle_map_alignment_gate()
        passed, _ = gate.check(gateway=None, files=["src/zephyr/whatever.py"])
        assert passed is True

    def test_b4b_battle_map_exception_fail_open(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import align_battle_map

        import zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate as bmg

        gate = make_battle_map_alignment_gate()

        def _boom(write_report=False):  # noqa: ANN001
            raise RuntimeError("pg down")

        monkeypatch.setattr(align_battle_map, "run_alignment", _boom)
        passed, _ = gate.check(
            gateway=None, files=["docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml"]
        )
        assert passed is True  # fail-open

    def test_b5_untriggered_files_pass_fast(self) -> None:
        gate = make_business_registry_gate()
        passed, _ = gate.check(gateway=None, files=["src/zephyr/trading/decision_map.py"])
        assert passed is True
        gate_bm = make_battle_map_alignment_gate()
        passed2, _ = gate_bm.check(gateway=None, files=["src/zephyr/trading/decision_map.py"])
        assert passed2 is True

    def test_b5b_registry_trigger_runs_validation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """命中 6 库文件 → 触发整库校验（当前仓库全绿 → 放行）。"""
        import zephyr.gov_enforcement.commit_gates.business_registry_gate as brg

        gate = make_business_registry_gate()
        passed, _ = gate.check(
            gateway=None, files=["docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"]
        )
        assert passed is True
        # tmp 坏库 → 通过 monkeypatch catalogs 目录后阻断
        bad = tmp_path / "strategy_registry.yaml"
        bad.write_text(
            yaml.safe_dump({"strategies": [{"strategy_id": "STR-BAD-001"}]}, allow_unicode=True),
            encoding="utf-8",
        )
        monkeypatch.setattr(brg, "_CATALOGS_DIR", tmp_path)
        passed2, detail2 = gate.check(
            gateway=None, files=["docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"]
        )
        assert passed2 is False
        assert "STR-BAD-001" in detail2

    def test_b6_depgraph_down_skips_existence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import zephyr.gov_enforcement.commit_gates.business_registry_gate as brg

        def _boom(module_id: str) -> bool:  # noqa: ANN001
            raise RuntimeError("pg down")

        monkeypatch.setattr(brg, "_module_exists_in_depgraph", _boom)
        gate = make_business_registry_gate()
        passed, _ = gate.check(
            gateway=None, files=["docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"]
        )
        assert passed is True  # PG 不可达=子检查跳过（fail-open），格式校验通过即放行


class TestV11PortfolioFlow:
    """v1.1 组合资金流+整装方案层（Owner 终极定位：地图=整装仿真系统蓝图）。"""

    def _payload_with_plan(self, plan: dict) -> dict:
        node = {
            "node_id": "TDM-F-C1",
            "name_zh": "预算切分",
            "market": "cn_a",
            "flow": "portfolio_flow",
            "layer": "C1",
            "node_type": "gate",
            "point": "盘前",
            "decision_question": "测试",
            "factor_refs": [],
            "data_refs": [],
            "module_ref": None,
            "strategy_mounts": [],
        }
        return {
            "schema_version": "1.1",
            "map_id": "TDMAP-V11",
            "markets": ["cn_a"],
            "nodes": [node],
            "edges": [],
            "state_matrix": {"states": ["强势", "震荡"], "cells": []},
            "portfolio_plan": plan,
        }

    def _validate(self, payload: dict) -> list[str]:
        import tempfile

        from zephyr.trading.decision_map import load_decision_map, validate_decision_map

        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.safe_dump(payload, f, allow_unicode=True)
            tmp = Path(f.name)
        try:
            dm = load_decision_map(tmp)
        finally:
            tmp.unlink()
        _, issues = validate_decision_map(
            dm, _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs", None
        )
        return [f"{i.code} [{i.node_id}] {i.detail}" for i in issues if i.level == "error"]

    def test_repo_plan_loads_with_sleeves(self) -> None:
        from zephyr.trading.decision_map import load_decision_map

        dm = load_decision_map(_REPO / "config" / "trading_decision_map.yaml")
        assert dm.schema_version == "1.1"
        assert dm.portfolio_plan is not None
        assert len(dm.portfolio_plan.sleeves) == 8
        assert abs(sum(s.weight for s in dm.portfolio_plan.sleeves) - 1.0) < 1e-9
        assert dm.portfolio_plan.confidence == "proposed"
        c_nodes = [n for n in dm.nodes if n.flow == "portfolio_flow"]
        assert len(c_nodes) == 3 and all(n.layer.startswith("C") for n in c_nodes)
        assert any(
            e.from_node == "TDM-F-C3" and e.to_node == "TDM-E-L1-AGG" and e.edge_type == "feedback" for e in dm.edges
        )

    def test_r12_weight_sum_over_blocked(self) -> None:
        plan = {
            "plan_id": "PP-R12",
            "confidence": "proposed",
            "sleeves": [
                {"strategy_ref": "daban-sleeve", "weight": 0.7, "activation_state": None},
                {"strategy_ref": "topn-momentum", "weight": 0.7, "activation_state": None},
            ],
        }
        errors = self._validate(self._payload_with_plan(plan))
        assert any("R12" in e and "> 1.0" in e for e in errors)

    def test_r12_unknown_sleeve_strategy_blocked(self) -> None:
        plan = {
            "plan_id": "PP-R12",
            "confidence": "proposed",
            "sleeves": [{"strategy_ref": "ghost-sleeve", "weight": 0.5, "activation_state": None}],
        }
        errors = self._validate(self._payload_with_plan(plan))
        assert any("R12" in e and "ghost-sleeve" in e for e in errors)

    def test_r12_bad_activation_state_blocked(self) -> None:
        plan = {
            "plan_id": "PP-R12",
            "confidence": "proposed",
            "sleeves": [{"strategy_ref": "daban-sleeve", "weight": 0.5, "activation_state": "冰雪季"}],
        }
        errors = self._validate(self._payload_with_plan(plan))
        assert any("R12" in e and "不在列轴" in e for e in errors)

    def test_r12_duplicate_sleeve_blocked(self) -> None:
        plan = {
            "plan_id": "PP-R12",
            "confidence": "proposed",
            "sleeves": [
                {"strategy_ref": "daban-sleeve", "weight": 0.3, "activation_state": None},
                {"strategy_ref": "daban-sleeve", "weight": 0.3, "activation_state": None},
            ],
        }
        errors = self._validate(self._payload_with_plan(plan))
        assert any("R12" in e and "重复" in e for e in errors)
