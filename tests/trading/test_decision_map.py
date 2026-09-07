# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [DOMAIN] D_TRADING
# [TESTS] tests/trading/test_decision_map.py
# [TTL] permanent
"""交易决策地图模块测试——加载/schema/校验 R1-R19/真源自检（回归锚）。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.trading.decision_map import (
    DecisionMapSchemaError,
    load_decision_map,
    validate_decision_map,
    _XREF_SPECS,
)

_REPO = Path(__file__).resolve().parents[2]
_MAP_PATH = _REPO / "config" / "trading_decision_map.yaml"
_REGISTRY_DIR = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"

# 代码 StrategyMeta 真源（8 实盘策略，pf_core/*.py）
_KNOWN_STRATEGIES = frozenset(
    {
        "daban-sleeve",
        "default-equity",
        "eventdriven-sleeve",
        "multifactor-sleeve",
        "topn-momentum",
        "intraday-surge-fall",
        "orderbook-imbalance",
        "vwap-reversion",
    }
)


def _make_min_node(**overrides) -> dict:
    base = {
        "node_id": "TDM-T-1",
        "name_zh": "测试环节",
        "market": "cn_a",
        "flow": "entry_flow",
        "layer": "L9",
        "node_type": "stage",
        "point": "盘前",
        "decision_question": "测试问题",
        "algo_note_zh": "测试大白话说明：怎么算的（R37 必填）。",
        "factor_refs": [],
        "data_refs": [],
        "module_ref": None,
        "strategy_mounts": [],
    }
    base.update(overrides)
    return base


def _write_map(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "map.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return p


def _minimal_payload() -> dict:
    return {
        "schema_version": "1.0",
        "map_id": "TDMAP-TEST",
        "markets": ["cn_a"],
        "nodes": [_make_min_node()],
        "edges": [],
        "state_matrix": {"states": ["强势"], "cells": []},
    }


# ── A1 加载 ──────────────────────────────────────────────────────────────────


class TestLoad:
    def test_load_minimal_ok(self, tmp_path: Path) -> None:
        dm = load_decision_map(_write_map(tmp_path, _minimal_payload()))
        assert dm.map_id == "TDMAP-TEST"
        assert len(dm.nodes) == 1
        assert dm.nodes[0].node_id == "TDM-T-1"
        assert dm.state_matrix.states == ("强势",)

    def test_load_missing_field_raises(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        del payload["nodes"][0]["decision_question"]
        with pytest.raises(DecisionMapSchemaError, match="decision_question"):
            load_decision_map(_write_map(tmp_path, payload))

    def test_load_bad_schema_version_raises(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["schema_version"] = "9.9"
        with pytest.raises(DecisionMapSchemaError, match="schema_version"):
            load_decision_map(_write_map(tmp_path, payload))

    def test_load_duplicate_node_id_raises(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"].append(_make_min_node())
        with pytest.raises(DecisionMapSchemaError, match="node_id 重复"):
            load_decision_map(_write_map(tmp_path, payload))

    def test_load_nonexistent_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(DecisionMapSchemaError, match="不存在"):
            load_decision_map(tmp_path / "nope.yaml")


# ── A2 校验 R1-R8 ────────────────────────────────────────────────────────────


class TestValidate:
    def test_clean_minimal_ok(self, tmp_path: Path) -> None:
        dm = load_decision_map(_write_map(tmp_path, _minimal_payload()))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        errors = [i for i in issues if i.level == "error"]
        assert ok is True
        assert errors == []
        # module_ref=null → warning（缺口占位）
        assert any(i.level == "warning" and i.code == "R1" for i in issues)

    def test_r1_bad_enum(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["market"] = "mars"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R1" and "market 非法" in i.detail for i in issues)

    def test_r3_unknown_strategy_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "no-such-strategy", "confidence": "proposed", "evidence": None}
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R3" and "no-such-strategy" in i.detail for i in issues)

    def test_r6_verified_requires_evidence(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "verified", "evidence": None}
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R6" and "evidence" in i.detail for i in issues)

    def test_r6_verified_with_evidence_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "verified", "evidence": "run-2026-001"}
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R6" for i in issues)
        assert ok is True

    def test_r2_dangling_edge(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["edges"] = [{"from_node": "TDM-T-1", "to_node": "TDM-GHOST", "edge_type": "sequence"}]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(
            i.code == "R2" and i.node_id == "TDM-GHOST" and "to_node 不存在" in i.detail
            for i in issues
        )

    def test_r8_sequence_cycle_detected(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"].append(_make_min_node(node_id="TDM-T-2", name_zh="第二环节"))
        payload["nodes"].append(_make_min_node(node_id="TDM-T-3", name_zh="第三环节"))
        payload["edges"] = [
            {"from_node": "TDM-T-1", "to_node": "TDM-T-2", "edge_type": "sequence"},
            {"from_node": "TDM-T-2", "to_node": "TDM-T-3", "edge_type": "sequence"},
            {"from_node": "TDM-T-3", "to_node": "TDM-T-1", "edge_type": "sequence"},
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R8" and "成环" in i.detail for i in issues)

    def test_r8_no_cycle_for_feedback(self, tmp_path: Path) -> None:
        """feedback 边允许回指（指数↔情绪双向互动，D6）。"""
        payload = _minimal_payload()
        payload["nodes"].append(_make_min_node(node_id="TDM-T-2", name_zh="第二环节"))
        payload["edges"] = [
            {"from_node": "TDM-T-1", "to_node": "TDM-T-2", "edge_type": "sequence"},
            {"from_node": "TDM-T-2", "to_node": "TDM-T-1", "edge_type": "feedback"},
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R8" for i in issues)
        assert ok is True

    def test_r7_matrix_cell_dangling_node(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["state_matrix"]["cells"] = [
            {"node_id": "TDM-GHOST", "state": "强势", "mounted": [], "confidence": "proposed"}
        ]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R7" for i in issues)

    def test_r4_unknown_factor_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["factor_refs"] = ["FCT-NO-SUCH-999"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R4" and "FCT-NO-SUCH-999" in i.detail for i in issues)

    def test_r5_unknown_data_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["data_refs"] = ["DS-NO-SUCH-999"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R5" and "DS-NO-SUCH-999" in i.detail for i in issues)


# ── A4 D36 八库交叉轴 R26-R33 ────────────────────────────────────────────────


class TestXrefAxes:
    """D36 全库交叉轴：形态/席位/宏观/周期/宇宙/成本/事件/风险限额（表驱动）。"""

    def test_r26_pattern_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["pattern_refs"] = ["PAT-CLL-002", "PAT-NO-SUCH-999"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R26" and "PAT-NO-SUCH-999" in i.detail for i in issues)

    def test_r27_seat_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["seat_refs"] = ["SEAT-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R27" for i in issues)

    def test_r28_macro_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["macro_refs"] = ["MAC-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R28" for i in issues)

    def test_r29_cycle_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["cycle_refs"] = ["CYC-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R29" for i in issues)

    def test_r30_universe_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["universe_refs"] = ["UNI-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R30" for i in issues)

    def test_r31_cost_model_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["cost_model_refs"] = ["CST-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R31" for i in issues)

    def test_r32_event_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["event_refs"] = ["EVT-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R32" for i in issues)

    def test_r33_risk_limit_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["risk_limit_refs"] = ["RLM-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R33" for i in issues)

    def test_r34_portfolio_model_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["portfolio_model_refs"] = ["PFM-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R34" for i in issues)

    def test_r35_benchmark_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["benchmark_refs"] = ["BMK-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R35" for i in issues)

    def test_r36_threshold_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["threshold_refs"] = ["THD-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R36" for i in issues)

    def test_all_axes_valid_ok(self, tmp_path: Path) -> None:
        """11 轴全挂真实条目 → error=0。"""
        payload = _minimal_payload()
        payload["nodes"][0].update(
            {
                "pattern_refs": ["PAT-CLL-002"],
                "seat_refs": ["SEAT-INST-001"],
                "macro_refs": ["MAC-CN-006"],
                "cycle_refs": ["CYC-STAT-001"],
                "universe_refs": ["UNI-RULE-001"],
                "cost_model_refs": ["CST-ASTOCK-001"],
                "event_refs": ["EVT-EARN-001"],
                "risk_limit_refs": ["RLM-DRAWDOWN-001"],
                "portfolio_model_refs": ["PFM-RB-001"],
                "benchmark_refs": ["BMK-INDEX-003"],
                "threshold_refs": ["THD-RETIRE-001"],
            }
        )
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is True
        assert not any(
            i.code in {f"R{n}" for n in range(26, 37)} for i in issues
        )


# ── A3 D32/D33 门禁包 R13-R19 ────────────────────────────────────────────────


class TestGovernanceGates:
    """D32 治理门禁（R13-R16/R18）+ D33 容量粒度门禁（R17/R19）。"""

    def test_r13_unknown_algo_ref(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["algo_refs"] = ["EXA-NO-SUCH-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R13" and "EXA-NO-SUCH-001" in i.detail for i in issues)

    def test_r13_known_algo_ref_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["algo_refs"] = ["EXA-TWAP-001"]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R13" for i in issues)

    def test_r14_doc_ref_missing_file(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["doc_ref"] = "docs/__no_such_doc__.md#§1"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R14" and "__no_such_doc__.md" in i.detail for i in issues)

    def test_r14_doc_ref_existing_file_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["doc_ref"] = "AGENTS.md"
        dm = load_decision_map(_write_map(tmp_path, payload))
        _, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R14" for i in issues)

    def test_r15_bad_activation_enum(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["activation"] = "半夜"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R15" and "activation 非法" in i.detail for i in issues)

    def test_r15_v15_node_requires_governance_fields(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"].append(
            _make_min_node(node_id="TDM-T-2", name_zh="子环节", parent_node="TDM-T-1")
        )
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R15" and "activation" in i.detail for i in issues)
        assert any(i.code == "R15" and "ai_autonomy" in i.detail for i in issues)

    def test_r15_v15_node_with_governance_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"].append(
            _make_min_node(
                node_id="TDM-T-2",
                name_zh="子环节",
                parent_node="TDM-T-1",
                activation="intraday",
                ai_autonomy="auto",
            )
        )
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R15" for i in issues)
        assert ok is True

    def test_r16_parent_dangling(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["parent_node"] = "TDM-GHOST"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R16" and "TDM-GHOST" in i.detail for i in issues)

    def test_r16_parent_cycle(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["parent_node"] = "TDM-T-2"
        payload["nodes"].append(
            _make_min_node(node_id="TDM-T-2", name_zh="父环节", parent_node="TDM-T-1")
        )
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R16" and "成环" in i.detail for i in issues)

    def test_r16_tree_depth_over_limit(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        chain = ["TDM-T-1"]
        for i in range(2, 8):  # 1→2→...→7 深度 6 > 4
            nid = f"TDM-T-{i}"
            payload["nodes"].append(
                _make_min_node(
                    node_id=nid,
                    name_zh=f"环节{i}",
                    parent_node=chain[-1],
                    activation="intraday",
                    ai_autonomy="auto",
                )
            )
            chain.append(nid)
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R16" and "树深度" in i.detail for i in issues)

    def test_r16_tree_width_warning_not_error(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        for i in range(13):
            payload["nodes"].append(
                _make_min_node(
                    node_id=f"TDM-C-{i}",
                    name_zh=f"子环节{i}",
                    parent_node="TDM-T-1",
                    activation="intraday",
                    ai_autonomy="auto",
                )
            )
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is True  # warning 不阻断
        assert any(i.code == "R16" and i.level == "warning" and "树宽过大" in i.detail for i in issues)

    def test_r17_question_too_long(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["decision_question"] = "长" * 101
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R17" and "超上限" in i.detail for i in issues)

    def test_r17_vague_word(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["decision_question"] = "到时候再说怎么下单"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R17" and "模糊词" in i.detail for i in issues)

    def test_r17_mounts_over_capacity(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ] * 9
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R17" and "strategy_mounts" in i.detail for i in issues)

    def test_r17_factor_refs_over_capacity(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["factor_refs"] = [f"FCT-X-{i:03d}" for i in range(13)]
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R17" and "factor_refs" in i.detail for i in issues)

    def test_r17_within_capacity_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ] * 8
        dm = load_decision_map(_write_map(tmp_path, payload))
        _, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R17" for i in issues)

    def test_r18_duplicate_name_zh(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"].append(_make_min_node(node_id="TDM-T-2", name_zh="测试环节"))
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R18" and "重复" in i.detail for i in issues)

    def test_r19_module_ref_missing_file(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["module_ref"] = "src/zephyr/__no_such_module__.py"
        dm = load_decision_map(_write_map(tmp_path, payload))
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is False
        assert any(i.code == "R19" and "__no_such_module__.py" in i.detail for i in issues)

    def test_r19_module_ref_existing_file_ok(self, tmp_path: Path) -> None:
        payload = _minimal_payload()
        payload["nodes"][0]["module_ref"] = "src/zephyr/trading/decision_map.py"
        dm = load_decision_map(_write_map(tmp_path, payload))
        _, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert not any(i.code == "R19" for i in issues)
        assert not any(i.level == "warning" and "module_ref 缺失" in i.detail for i in issues)


# ── A5 D38 新库必挂门禁（全图全库对齐铁律的机制化落地）──────────────────────


# 治理类豁免清单（管"怎么施工"不管"怎么赚钱"，不入 TDM 决策索引）
_GOVERNANCE_EXEMPT = frozenset(
    {
        "_index.yaml",
        "ai_autonomy_authority_registry.yaml",
        "ai_risk_register.yaml",
        "ai_session_registry.yaml",
        "architecture_issue_registry.yaml",
        "battle_map_domain_policy.yaml",
        "business_streams_registry.yaml",
        "candidate_module_registry.yaml",
        "capability_canonical_file_registry.yaml",
        "compliance_report_registry.yaml",
        "cross_module_dependency_registry.yaml",
        "dataflow_graph_registry.yaml",
        "declarative_contract_tracker_registry.yaml",
        "depgraph_scan_exclusions.yaml",
        "derived_identifier_registry.yaml",
        "directory_registry.yaml",
        "domain_naming_rules.yaml",
        "experiment_registry.yaml",
        "external_contract_verification_registry.yaml",
        "feature_adjudication_registry.yaml",
        "field_dictionary.yaml",
        "frontier_llm_benchmark_ranking.yaml",
        "frontmatter_field_registry.yaml",
        "functional_domain_registry.yaml",
        "gate_registry.yaml",
        "gate_tracked_write_allowlist.yaml",
        "generator_registry.yaml",
        "governance_convergence_map.yaml",
        "hard_boundaries_registry.yaml",
        "in_process_gate_registry.yaml",
        "infrastructure_registry.yaml",
        "interface_contract_registry.yaml",
        "knowledge_article_registry.yaml",
        "migration_registry.yaml",
        "model_registry.yaml",
        "module_translation_registry.yaml",
        "noqa_exempt_registry.yaml",
        "panorama_exempt_list.yaml",
        "registry_consistency_contract.yaml",
        "registry_master_index.yaml",
        "registry_of_logs.yaml",
        "rule_ai_perception_index.yaml",
        "rule_catalog_registry.yaml",
        "rule_enforcement_registry.yaml",
        "rule_registry_collection.yaml",
        "ruling_registry.yaml",
        "scripts_registry.yaml",
        "task_card_meta_registry.yaml",
        "terminology_glossary.yaml",
        "test_suite_registry.yaml",
        "trust_boundary_surface_registry.yaml",
        "wiring_registry.yaml",
    }
)

_AXIS_FILES = frozenset(
    {
        "strategy_registry.yaml",
        "factor_registry.yaml",
        "data_asset_registry.yaml",
        "execution_algo_registry.yaml",
        "technical_indicator_registry.yaml",
        *(spec[1] for spec in _XREF_SPECS),
    }
)


def _unregistered_libs(catalog_dir: Path) -> set[str]:
    """目录中未挂轴且未登记豁免的库（新库必挂铁律判定核心，D38 供对抗测试攻击）。"""
    actual = {p.name for p in catalog_dir.glob("*.yaml")}
    return actual - _AXIS_FILES - _GOVERNANCE_EXEMPT


def _missing_axis_files(catalog_dir: Path) -> list[str]:
    """已挂轴的注册表文件在目录中缺失的（防轴文件删除后门禁静默失效）。"""
    return sorted(f for f in _AXIS_FILES if not (catalog_dir / f).exists())


def _stale_exemptions(catalog_dir: Path) -> list[str]:
    """豁免清单中已不存在的文件（防清单腐烂）。"""
    return sorted(f for f in _GOVERNANCE_EXEMPT if not (catalog_dir / f).exists())


class TestNewRegistryGate:
    """新业务库必须挂 TDM 交叉轴，治理库必须显式登记豁免——新建即被本门禁抓到。

    Owner 2026-09-07 裁定（D38）：全图全库对齐铁律——以后新上的图和库都必须挂上去打通。
    本测试是铁律的机制化：catalogs 出现新 yaml 时，必须二选一：
      ① 业务资产库 → decision_map.py _XREF_SPECS 加轴（两行）+ 真源挂载
      ② 治理类 → 在本模块 _GOVERNANCE_EXEMPT 登记豁免
    不做任何动作 → 本测试红，新 AI 必然看到（对抗攻击见 test_decision_map_d38_adversarial.py）。
    """

    def test_axis_files_exist_in_catalogs(self) -> None:
        """反向守门：已挂轴的 16 个注册表文件必须真实存在（防轴文件删除后测试仍绿）。"""
        assert _missing_axis_files(_REGISTRY_DIR) == []

    def test_catalogs_no_unregistered_new_library(self) -> None:
        """正向守门：catalogs 新 yaml 必须挂轴或登记豁免（新库必挂铁律）。"""
        unregistered = _unregistered_libs(_REGISTRY_DIR)
        assert not unregistered, (
            "发现未登记的新库（全图全库对齐铁律 D38）："
            f"{sorted(unregistered)} —— 若是业务资产库请在 decision_map.py _XREF_SPECS 加轴并挂载；"
            "若是治理类请在本测试 _GOVERNANCE_EXEMPT 登记豁免。二选一必做。"
        )

    def test_exempt_files_still_exist(self) -> None:
        """豁免清单卫生：登记的豁免文件必须仍存在（防删除后清单腐烂）。"""
        assert _stale_exemptions(_REGISTRY_DIR) == []


# ── 真源自检（回归锚：仓库内真实地图必须持续全绿）───────────────────────────


class TestRepoTruthSource:
    def test_repo_map_loads_and_validates_clean(self) -> None:
        dm = load_decision_map(_MAP_PATH)
        assert dm.map_id == "TDMAP-001"
        assert len(dm.nodes) >= 15
        assert dm.markets == ("cn_a", "crypto")
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        errors = [i for i in issues if i.level == "error"]
        assert errors == [], f"真源存在 error 级缺口: {errors}"
        assert ok is True

    def test_repo_map_mounts_all_eight_strategies(self) -> None:
        """8 个实盘策略必须全部挂载在地图上（D2 验收：策略归位完整）。

        v1.3 血肉（D19）：地图允许额外挂载 REG-STR-001 规则级条目（STR-*，
        R3 单独校验其存在性）——本锚只断言 8 实盘策略全覆盖（子集），不锁相等。
        """
        dm = load_decision_map(_MAP_PATH)
        mounted = {m.strategy_ref for n in dm.nodes for m in n.strategy_mounts}
        assert _KNOWN_STRATEGIES <= mounted

    def test_repo_map_matrix_cells_proposed_only(self) -> None:
        """V0 血肉阶段：矩阵格子只允许 proposed/untested，禁止冒充 verified（D5）。"""
        dm = load_decision_map(_MAP_PATH)
        assert all(c.confidence != "verified" for c in dm.state_matrix.cells)
