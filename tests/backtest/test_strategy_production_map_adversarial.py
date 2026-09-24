# [BLUEPRINT] MOD-BT-081 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_strategy_production_map_adversarial
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; yaml; scripts.governance.d5_architecture.validators.validate_strategy_production_map
# [CONSUMERS] 策略生产全景图校验器质量守卫（坏图必须被拦）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 坏图用例全部构造于内存副本（不碰生产路径）；好图控制组=真实图必须通过
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-BT-081 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略生产全景图校验器对抗测试——每种坏图必须被拦，好图必须通过。"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
from validate_strategy_production_map import check_stores, validate_structure  # noqa: E402

_GOOD = yaml.safe_load((_REPO / "config" / "strategy_production_map.yaml").read_text(encoding="utf-8"))


def _set(d: dict, path: str, value) -> None:
    keys = path.split(".")
    t = d
    for k in keys[:-1]:
        t = t[int(k)] if k.isdigit() else t[k]
    t[keys[-1]] = value


def _del(d: dict, path: str) -> None:
    keys = path.split(".")
    t = d
    for k in keys[:-1]:
        t = t[int(k)] if k.isdigit() else t[k]
    t.pop(keys[-1], None)


def _find(d: dict, node_id: str) -> dict:
    return next(n for n in d["nodes"] if n["node_id"] == node_id)


def test_good_map_passes():
    assert validate_structure(copy.deepcopy(_GOOD)) == []


def test_missing_laws_rejected():
    d = copy.deepcopy(_GOOD)
    d.pop("laws")
    assert any("laws" in e for e in validate_structure(d))


def test_empty_products_rejected():
    d = copy.deepcopy(_GOOD)
    d["products"] = []
    assert any("products" in e for e in validate_structure(d))


def test_missing_stage_layer_rejected():
    d = copy.deepcopy(_GOOD)
    d["layers"] = [l for l in d["layers"] if l["layer_id"] != "E4"]
    assert any("E4" in e for e in validate_structure(d))


def test_broken_edge_rejected():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["FAC-E9", "FAC-不存在"])
    assert any("不存在" in e for e in validate_structure(d))


def test_duplicate_node_id_rejected():
    d = copy.deepcopy(_GOOD)
    d["nodes"].append(copy.deepcopy(d["nodes"][0]))
    assert any("重复" in e for e in validate_structure(d))


def test_missing_required_field_rejected():
    d = copy.deepcopy(_GOOD)
    _del(d, "nodes.2.decision_question")
    assert any("decision_question" in e for e in validate_structure(d))


def test_illegal_stage_rejected():
    d = copy.deepcopy(_GOOD)
    _set(d, "nodes.0.stage", "E99")
    assert any("stage 非法" in e for e in validate_structure(d))


def test_self_loop_rejected():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["FAC-E4", "FAC-E4"])
    assert any("自环" in e for e in validate_structure(d))


def test_undeclared_backward_edge_rejected():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["FAC-E4", "FAC-E1"])  # 反向边未声明为反馈环
    assert any("未声明" in e for e in validate_structure(d))


def test_declared_feedback_present():
    pairs = {(f["from"], f["to"]) for f in _GOOD["feedback_loops"]}
    assert ("FAC-E9", "FAC-E2") in pairs
    assert ("FAC-E6", "FAC-E1") in pairs


def test_built_without_module_ref_rejected():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E4")["module_ref"] = None
    assert any("module_ref" in e for e in validate_structure(d))


def test_lane_without_lane_field_rejected():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E1A").pop("lane")
    assert any("lane 归属" in e for e in validate_structure(d))


def test_illegal_compute_class_rejected():
    d = copy.deepcopy(_GOOD)
    _set(d, "nodes.0.compute_class", "quantum")
    assert any("compute_class" in e for e in validate_structure(d))


def test_store_ref_missing_artifact_rejected():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E4")["store_refs"][0]["artifact"] = ""
    assert any("store_refs" in e for e in validate_structure(d))


# ---- 连通性 pass（审计 F-AUDIT-BLIND-05 红测：孤立 built 节点必拦） ----


def _append_node(d: dict, node_id: str, build_status: str) -> None:
    d["nodes"].append(
        {
            "node_id": node_id,
            "name_zh": "对抗注入",
            "stage": "E0",
            "node_type": "stage",
            "decision_question": "对抗测试注入节点",
            "algo_note_zh": "对抗测试注入",
            "compute_class": "local",
            "build_status": build_status,
            "data_refs": [],
            "design_refs": [],
            "store_refs": [],
            "module_ref": "tests.adversarial",
        }
    )


def test_isolated_built_node_rejected():
    d = copy.deepcopy(_GOOD)
    _append_node(d, "FAC-E0X", "built")
    assert any("孤立" in e for e in validate_structure(d))


def test_isolated_partial_node_rejected():
    d = copy.deepcopy(_GOOD)
    _append_node(d, "FAC-E0X", "partial")
    assert any("孤立" in e for e in validate_structure(d))


def test_disconnected_built_component_rejected():
    d = copy.deepcopy(_GOOD)
    _append_node(d, "FAC-E0X", "built")
    _append_node(d, "FAC-E0Y", "built")
    d["edges"].append(["FAC-E0X", "FAC-E0Y"])
    assert any("孤立连通分量" in e for e in validate_structure(d))


def test_isolated_pending_node_allowed():
    d = copy.deepcopy(_GOOD)
    _append_node(d, "FAC-E0X", "pending")
    assert validate_structure(d) == []


# ---- data_refs 存在性（审计 F-AUDIT-BLIND-04 红测：坏 data_ref 必拦） ----


def test_data_ref_missing_path_rejected():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E1A")["data_refs"] = ["data/strategy_intake/no_such_artifact_xyz.csv"]
    errors, _ = check_stores(d, root=_REPO)
    assert any("no_such_artifact_xyz.csv" in e for e in errors)


def test_data_ref_missing_ch_table_rejected():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E1")["data_refs"] = ["c1_market.definitely_no_such_table_xyz"]
    errors, _ = check_stores(d, root=_REPO)
    assert any("definitely_no_such_table_xyz" in e for e in errors)


def test_data_ref_pending_warns_not_errors():
    d = copy.deepcopy(_GOOD)
    _find(d, "FAC-E1")["data_refs"] = ["待定:c1_market.news_data"]
    errors, warnings = check_stores(d, root=_REPO)
    assert not any("news_data" in e for e in errors)
    assert any("待定" in w and "news_data" in w for w in warnings)


def test_good_map_data_refs_all_exist():
    d = copy.deepcopy(_GOOD)
    errors, _ = check_stores(d, root=_REPO)
    assert not any("数据" in e for e in errors)
