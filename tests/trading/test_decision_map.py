# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [DOMAIN] D_TRADING
# [TESTS] tests/trading/test_decision_map.py
# [TTL] permanent
"""交易决策地图模块测试——加载/schema/校验 R1-R8/真源自检（回归锚）。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.trading.decision_map import (
    DecisionMapSchemaError,
    load_decision_map,
    validate_decision_map,
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
        payload["nodes"].append(_make_min_node(node_id="TDM-T-2"))
        payload["nodes"].append(_make_min_node(node_id="TDM-T-3"))
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
        payload["nodes"].append(_make_min_node(node_id="TDM-T-2"))
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
