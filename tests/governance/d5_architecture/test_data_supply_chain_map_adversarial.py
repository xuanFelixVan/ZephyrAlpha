# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §data-supply-chain-map
# [MODULE] tests.governance.d5_architecture.test_data_supply_chain_map_adversarial
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest; yaml; scripts.governance.d5_architecture.validators.validate_data_supply_chain_map
#   （sys.path 动态加载，单一判据真源）;
#   scripts.governance.d5_architecture.generators.generate_data_supply_chain_map（幂等与双轴同源实证）
# [CONSUMERS] 图12 校验器/生成器质量守卫——校验器必须先证明自己会红
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部坏例构造于内存副本（禁写生产路径、禁真连 ClickHouse/PG）；
#   好图控制组=真实图必须通过（结构 + INV-1 + 注入 resolver 的锚核验 + 双轴与骨架同源）；
#   红例逐条打在对图12 最有价值的判据上：挂槽≠在跑 / CV-L0 旧别名 / CV-BUS 总线在册 /
#   CV-DUAL 双轴（谎与欠双向）/ CV-FACET 分面禁 production / CV-GAP 缺口不孤岛 /
#   CV-WAIT 五处等未产表与幽灵不得隐没 / probe_failed 不得放行 production / 空串通道不作证据
# [MODIFY-GUARD] 校验器判据新增须同步补对应红例（无配对红例=判据可能失效）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError（红例未红/蓝例被误拦）
# [TESTS] self
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图12 数据供给链图对抗测试——红队（本批 40+ 例）+ 蓝队控制组（校验器必须先证明自己会红）。

覆盖判据面：结构闭合（断边/重复边/自环/未声明反向边）、字段完备（L0 必填 + 键存在性）、
枚举合法（段·节点型·装配态·时点源·下游动作·verified_scope·red_reason·缺口症状·边型边态）、
状态与证据一致（built 必有代码锚 / 未接线禁 built / gap 禁 built / verified 必带 evidence /
production 必带 freshness_evidence 八字段）、三层字段归一（CV-L0 旧别名）、总线挂载（CV-BUS 三态）、
双轴同源（CV-DUAL 谎与欠 + 计数双判）、分面（CV-FACET）、缺口显性化（CV-GAP/CV-WAIT）、
锚在册（表/task/slot/file）、INV-1 引用不复制、生成器纪律（幂等/禁取时/必经翻译 loader/
双轴不一致生成期硬失败）、CLI 退出码语义。
"""

from __future__ import annotations

import ast
import copy
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
_VALIDATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "validators"
_GENERATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "generators"
for _p in (str(_VALIDATORS_DIR), str(_GENERATORS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from validate_data_supply_chain_map import (  # noqa: E402
    STAGE_UNIVERSE,
    check_anchors,
    check_inv1,
    scan_skeleton_status,
    validate_structure,
)

_MAP_REL = "config/data_supply_chain_map.yaml"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))
# 生产断言真值面（骨架 §1 批次4 定稿）：22 行 / ✅ 10 / 等未产表 5 / 幽灵 1
EXPECTED_STAGES = 22
EXPECTED_PRODUCTION = 10


def _node(d: dict, node_id: str) -> dict:
    """按 id 取节点（就地可改，改的就是副本本体）。"""
    return next(n for n in d["nodes"] if n["node_id"] == node_id)


def _copy() -> dict:
    """真实好图的深拷贝（每个红例在其上打一处洞）。"""
    return copy.deepcopy(_GOOD)


def _red(d: dict, *needles: str) -> list[str]:
    """跑结构判据并断言确实变红，返回命中的报错行。"""
    errors = validate_structure(d, _REPO)
    assert errors, "校验器未红——判据可能失效（本仓铁律：无配对红例=疑似判据失效）"
    hits = [e for e in errors if any(n in e for n in needles)]
    assert hits, f"报错未命中预期判据 {needles}，实际={errors[:6]}"
    return hits


def _drop_node(d: dict, node_id: str) -> None:
    """连边带反馈环一起摘掉一个节点（防"删环节"只删半条链）。"""
    d["nodes"] = [n for n in d["nodes"] if n.get("node_id") != node_id]
    d["edges"] = [e for e in d["edges"] if e.get("from") != node_id and e.get("to") != node_id]
    d["feedback_loops"] = [f for f in d["feedback_loops"] if f.get("from") != node_id and f.get("to") != node_id]
    for n in d["nodes"]:
        if node_id in (n.get("gap_refs") or []):
            n["gap_refs"] = [g for g in n["gap_refs"] if g != node_id]


# ── 蓝队：真实图必须通过 ─────────────────────────────────────────────────────
class TestBlue:
    """蓝队：好图必过（结构 / INV-1 / 锚核验用注入桩，禁真连 CH）。"""

    def test_real_map_structurally_clean(self):
        assert validate_structure(_GOOD, _REPO) == []

    def test_real_map_has_all_22_stage_links(self):
        ids = {n["node_id"] for n in _GOOD["nodes"]}
        missing = sorted(STAGE_UNIVERSE - ids)
        assert not missing, f"22 环节未全覆盖，缺: {missing}"
        assert len(STAGE_UNIVERSE) == EXPECTED_STAGES
        assert len(ids) > EXPECTED_STAGES, "辅助/缺口节点应另计，禁与契约环节混为一谈"

    def test_split_and_new_nodes_are_present(self):
        """批次4 扩行的四枚新契约号必须在图里（拆行/新立不许只改骨架不改图本体）。"""
        ids = {n["node_id"] for n in _GOOD["nodes"]}
        for nid in ("DSC-10A", "DSC-10B", "DSC-19", "DSC-20", "DSC-21"):
            assert nid in ids, f"缺 {nid}"
        assert "DSC-10" not in ids, "D12-10 已拆行，旧合取号不得留在图里"

    def test_real_map_five_segments_all_populated(self):
        for seg in ("S1_collect", "S2_ingest", "S3_derive", "S4_coldstore", "S5_recon"):
            assert any(n["segment"] == seg for n in _GOOD["nodes"]), f"段 {seg} 无节点"

    def test_real_map_inv1_clean(self):
        assert check_inv1(_GOOD, _REPO) == []

    def test_real_map_anchors_resolve_with_stub(self):
        """表锚在册核验：注入"全认桩"应当零 error（task/slot/file 硬核验走真实仓内源）。"""
        errors, _warnings = check_anchors(_GOOD, _REPO, resolver=lambda want: set(want))
        assert errors == [], errors

    def test_unwired_segment_links_are_never_built(self):
        """图12 的价值判据：未接线环节一律不标 built（05 簿死结论的结构化落点）。"""
        for n in _GOOD["nodes"]:
            if str(n.get("wiring_status", "")).startswith("unwired"):
                assert n["build_status"] != "built", n["node_id"]

    def test_terminal_gap_is_explicit(self):
        """终点不可证必须显性化为 gap 节点，不许藏在散文里。"""
        gap = _GOOD["boundary"]["terminal_gap"]
        node = _node(_GOOD, gap)
        assert node["node_type"] == "gap"
        assert node["red_reason"] == "terminal"
        assert node["build_status"] == "pending"
        assert _node(_GOOD, "DSC-15")["build_status"] != "built"

    def test_production_count_equals_skeleton_tick_count(self):
        """双轴口径面的蓝队判据：production 数==骨架 ✅ 数==10（不多不少）。"""
        skel = scan_skeleton_status(_REPO)
        assert len(skel) == EXPECTED_STAGES, f"骨架 §1 实扫应 22 行，实得 {len(skel)}"
        ok = {nid for nid, sym in skel.items() if sym == "✅"}
        prod = {n["node_id"] for n in _GOOD["nodes"] if n.get("verified_scope") == "production"}
        assert len(ok) == len(prod) == EXPECTED_PRODUCTION, (sorted(ok), sorted(prod))
        assert _GOOD["counts"]["production_nodes"] == len(prod)

    def test_no_legacy_alias_anywhere_in_map(self):
        """旧别名 grep=0（图本体检索，含嵌套键）。"""
        banned = (
            "semantics_zh",
            "mech_note_zh",
            "clock_semantics_zh",
            "degradation",
            "miss_fallback_zh",
            "silent_failover",
            "data_anchors",
            "detection_only",
            "design_refs",
            "doc_ref",
        )
        text = (_REPO / _MAP_REL).read_text(encoding="utf-8")
        hit = [k for k in banned if f"{k}:" in text]
        assert not hit, f"图本体残留旧别名字段: {hit}"

    def test_every_gap_node_is_wired_and_referenced(self):
        """缺口不得孤岛：每个 gap 节点既有边、又被至少一个环节的 gap_refs 指到。"""
        gaps = [n["node_id"] for n in _GOOD["nodes"] if n["node_type"] == "gap"]
        assert gaps, "图里必须有 gap 节点"
        touched = {e["from"] for e in _GOOD["edges"]} | {e["to"] for e in _GOOD["edges"]}
        referenced = {g for n in _GOOD["nodes"] for g in (n.get("gap_refs") or [])}
        for gid in gaps:
            assert gid in touched, f"{gid} 无边"
            assert gid in referenced, f"{gid} 无 gap_refs 指入"

    def test_waiting_tables_and_ghost_all_have_gap_nodes(self):
        """5 处消费方在等的未产表 + 1 处幽灵引用全部落成在册 gap 节点（终局验收判据③）。"""
        wait = _GOOD["boundary"]["waiting_table_gaps"]
        ghost = _GOOD["boundary"]["ghost_ref_gaps"]
        assert len(wait) == 5 and len(ghost) == 1
        ids = {n["node_id"] for n in _GOOD["nodes"]}
        for table, gid in {**wait, **ghost}.items():
            assert gid in ids, f"{table} 的缺口节点 {gid} 不在图里"
        assert _node(_GOOD, ghost["c1_market.news_data"])["red_reason"] == "ghost_ref"

    def test_facet_nodes_carry_legs_and_are_not_production(self):
        facet_ids = [n["node_id"] for n in _GOOD["nodes"] if n.get("facets")]
        assert set(facet_ids) == {"DSC-07", "DSC-08", "DSC-09", "DSC-14"}
        for nid in facet_ids:
            n = _node(_GOOD, nid)
            assert len(n["facets"]) >= 2
            assert all(f.get("evidence") for f in n["facets"])
            assert n["verified_scope"] != "production"


# ── 红队 1：结构与引用闭合 ───────────────────────────────────────────────────
class TestRedStructure:
    def test_dangling_edge_blocks(self):
        d = _copy()
        d["edges"].append({"from": "DSC-04", "to": "DSC-NOT-A-NODE", "kind": "data_flow"})
        _red(d, "边引用了不存在的节点")

    def test_duplicate_edge_blocks(self):
        d = _copy()
        d["edges"].append({"from": "DSC-01", "to": "DSC-04", "kind": "data_flow"})
        _red(d, "重复边")

    def test_self_loop_blocks(self):
        d = _copy()
        d["edges"].append({"from": "DSC-06", "to": "DSC-06", "kind": "data_flow"})
        _red(d, "自环边")

    def test_undeclared_backward_edge_blocks(self):
        """对账修复段（S5）指回衍生段（S3）而未在 feedback_loops 声明 → 必红。"""
        d = _copy()
        d["edges"].append({"from": "DSC-16", "to": "DSC-07", "kind": "data_flow"})
        _red(d, "未声明为反馈环的反向边")

    def test_edge_to_missing_node_id_blocks(self):
        d = _copy()
        d["feedback_loops"].append({"from": "DSC-99", "to": "DSC-01", "note_zh": "假环"})
        _red(d, "feedback_loops 引用不存在节点")

    def test_edge_missing_kind_blocks(self):
        d = _copy()
        d["edges"].append({"from": "DSC-01", "to": "DSC-02"})
        _red(d, "边 kind 非法")

    def test_edge_illegal_status_blocks(self):
        d = _copy()
        d["edges"].append({"from": "DSC-10A", "to": "DSC-11", "kind": "data_flow", "status": "maybe"})
        _red(d, "status 非法")

    def test_feedback_loop_missing_note_blocks(self):
        d = _copy()
        d["feedback_loops"].append({"from": "DSC-14", "to": "DSC-01"})
        _red(d, "缺 note_zh")


# ── 红队 2：节点字段与枚举 ───────────────────────────────────────────────────
class TestRedNodes:
    def test_missing_top_key_blocks(self):
        d = _copy()
        d.pop("laws")
        _red(d, "缺顶层必填键: laws")

    def test_missing_required_node_field_blocks(self):
        d = _copy()
        _node(d, "DSC-07").pop("decision_question")
        _red(d, "DSC-07: 缺必填字段 decision_question")

    def test_missing_note_zh_blocks(self):
        """L0 统一名缺字段=判红（note_zh 是三层字段裁定的必用名）。"""
        d = _copy()
        _node(d, "DSC-13").pop("note_zh")
        _red(d, "DSC-13: 缺必填字段 note_zh")

    def test_missing_verified_scope_key_blocks(self):
        d = _copy()
        _node(d, "DSC-02").pop("verified_scope")
        _red(d, "缺必填键 verified_scope")

    def test_segment_membership_missing_blocks(self):
        d = _copy()
        _node(d, "DSC-13").pop("segment")
        _red(d, "segment 非法或缺失")

    def test_illegal_segment_enum_blocks(self):
        d = _copy()
        _node(d, "DSC-11")["segment"] = "S9_databreach"
        _red(d, "segment 非法或缺失")

    def test_segments_declaration_missing_blocks(self):
        d = _copy()
        d["segments"] = [s for s in d["segments"] if s["segment_id"] != "S4_coldstore"]
        _red(d, "缺五段声明之一: S4_coldstore")

    def test_illegal_node_type_blocks(self):
        d = _copy()
        _node(d, "DSC-02")["node_type"] = "mystery"
        _red(d, "node_type 非法")

    def test_illegal_wiring_status_blocks(self):
        d = _copy()
        _node(d, "DSC-15")["wiring_status"] = "看起来在跑"
        _red(d, "wiring_status 非法")

    def test_illegal_build_status_blocks(self):
        d = _copy()
        _node(d, "DSC-06")["build_status"] = "done"
        _red(d, "build_status 非法")

    def test_illegal_downstream_action_blocks(self):
        """检测≠修复必须表态；写成散文=红。"""
        d = _copy()
        _node(d, "DSC-13")["downstream_action"] = "只告警不回补"
        _red(d, "downstream_action 非法")

    def test_illegal_slot_source_blocks(self):
        d = _copy()
        _node(d, "DSC-11")["slot_source"] = "每天早上"
        _red(d, "slot_source 非法")

    def test_illegal_verified_scope_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["verified_scope"] = "mostly"
        _red(d, "verified_scope 非法")

    def test_illegal_red_reason_blocks(self):
        d = _copy()
        _node(d, "DSC-GAP-NAV")["red_reason"] = "有点问题"
        _red(d, "red_reason 非法")

    def test_illegal_gap_symptom_blocks(self):
        d = _copy()
        _node(d, "DSC-02")["gaps"].append(
            {"anchor": "c1_market.tick_data", "symptom": "大概没问题", "pointer": "x", "measured_on": "2026-09-25"}
        )
        _red(d, "gaps.symptom 非法枚举")

    def test_gap_entry_without_measured_on_blocks(self):
        d = _copy()
        _node(d, "DSC-09")["gaps"].append({"anchor": "c1_market.sector_state", "symptom": "inversion", "pointer": "x"})
        _red(d, "缺 measured_on")

    def test_built_without_module_ref_blocks(self):
        d = _copy()
        _node(d, "DSC-07")["build_status"] = "built"
        _node(d, "DSC-07")["module_ref"] = None
        _red(d, "built 节点必须有 module_ref")

    def test_unwired_node_marked_built_blocks(self):
        d = _copy()
        _node(d, "DSC-15")["build_status"] = "built"
        _red(d, "禁标 built")

    def test_gap_node_marked_built_blocks(self):
        d = _copy()
        _node(d, "DSC-GAP-TERMINUS")["build_status"] = "built"
        _red(d, "gap（缺口）节点禁标 built")

    def test_verified_without_evidence_blocks(self):
        d = _copy()
        _node(d, "DSC-18")["evidence"] = []
        _red(d, "confidence=verified 必须带 evidence")

    def test_decision_question_too_long_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["decision_question"] = "问" * 200
        _red(d, "decision_question 超")

    def test_store_refs_missing_element_blocks(self):
        d = _copy()
        _node(d, "DSC-10A")["store_refs"].append({"artifact": "冷档", "key": "table"})
        _red(d, "store_refs 条目缺 artifact/location/retention")

    def test_store_refs_string_entry_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["store_refs"] = ["plain-string"]
        _red(d, "store_refs 条目缺 artifact/location/retention")

    def test_illegal_anchor_format_blocks(self):
        d = _copy()
        _node(d, "DSC-07")["source_anchors"].append("technical_indicator")
        _red(d, "锚形态非法")

    def test_duplicate_node_id_blocks(self):
        d = _copy()
        d["nodes"].append(copy.deepcopy(_node(d, "DSC-03")))
        _red(d, "node_id 存在重复")

    def test_string_node_reports_error_not_crash(self):
        d = _copy()
        d["nodes"].append("i-am-a-string")
        _red(d, "节点非对象")

    def test_segments_order_nonint_reports_error_not_crash(self):
        d = _copy()
        d["segments"][0]["order"] = "first"
        _red(d, "order 必须是整数")

    def test_forged_node_blocks(self):
        d = _copy()
        d["nodes"].append({"node_id": "DSC-FAB", "name_zh": "编造的环节"})
        d["edges"].append({"from": "DSC-01", "to": "DSC-FAB", "kind": "data_flow"})
        _red(d, "DSC-FAB: 缺必填字段", "segment 非法或缺失")

    def test_wellformed_forged_stage_node_blocks(self):
        """字段完备的伪造 stage 节点（克隆真环节只改 id）→ 22 环节契约全集判红。"""
        d = _copy()
        rogue = copy.deepcopy(_node(d, "DSC-07"))
        rogue["node_id"] = "DSC-99"
        d["nodes"].append(rogue)
        _red(d, "DSC-99: 节点越出 22 环节契约全集")

    def test_out_of_contract_aux_node_blocks(self):
        """契约外私加辅助节点（哪怕字段完备、类型合法）同样判红——先回写骨架再进图。"""
        d = _copy()
        rogue = copy.deepcopy(_node(d, "DSC-HA"))
        rogue["node_id"] = "DSC-HZ"
        d["nodes"].append(rogue)
        _red(d, "DSC-HZ: 辅助节点不在契约辅助集")

    @pytest.mark.parametrize("missing", ["DSC-06", "DSC-19", "DSC-20", "DSC-21", "DSC-10A", "DSC-10B"])
    def test_missing_contract_stage_blocks(self, missing):
        """抽掉任一契约环节（含批次4 新立的 19/20/21 与拆行后的 10A/10B）→ 缺环节判红。"""
        d = _copy()
        _drop_node(d, missing)
        d["counts"]["nodes"] = len(d["nodes"])
        d["counts"]["edges"] = len(d["edges"])
        _red(d, f"缺环节（22 环节契约未建满）: {missing}")

    def test_judgment_field_mount_blocks(self):
        d = _copy()
        _node(d, "DSC-08")["judgment_basis"] = "因子 IC 大于阈值才入选，方向为正则做多"
        _red(d, "越域挂载——节点夹带判据字段 judgment_basis")
        d2 = _copy()
        _node(d2, "DSC-08")["extra"] = {"factor_refs": ["factor_alpha_001"]}
        _red(d2, "越域挂载——节点夹带判据字段 factor_refs")

    def test_counts_drift_blocks(self):
        d = _copy()
        d["counts"]["nodes"] = 999
        _red(d, "counts.nodes=999 与 nodes 实数")

    def test_counts_production_drift_blocks(self):
        """手改 production 计数（不改节点）→ 与实数不符判红（静态清单禁手维）。"""
        d = _copy()
        d["counts"]["production_nodes"] = EXPECTED_PRODUCTION + 3
        _red(d, "counts.production_nodes=")

    def test_terminal_gap_must_be_gap_node(self):
        d = _copy()
        d["boundary"]["terminal_gap"] = "DSC-04"
        _red(d, "terminal_gap 必须指向 node_type=gap")

    def test_missing_terminal_declaration_blocks(self):
        d = _copy()
        d["boundary"].pop("terminal_gap")
        _red(d, "boundary 缺 terminal_gap")


# ── 红队 3：CV-L0 三层字段归一 ───────────────────────────────────────────────
class TestRedFieldUnification:
    """旧别名残留即红（六图终局卷 §1 裁定一：同语义必同名）。"""

    @pytest.mark.parametrize(
        "alias,canonical",
        [
            ("semantics_zh", "note_zh"),
            ("mech_note_zh", "note_zh"),
            ("clock_semantics_zh", "note_zh"),
            ("degradation", "fallback"),
            ("miss_fallback_zh", "fallback"),
            ("silent_failover", "fallback"),
            ("data_anchors", "source_anchors + data_refs"),
            ("detection_only", "downstream_action"),
            ("design_refs", "doc_refs"),
            ("doc_ref", "doc_refs"),
        ],
    )
    def test_legacy_alias_blocks(self, alias, canonical):
        d = _copy()
        _node(d, "DSC-04")[alias] = "旧名字段残留"
        hits = _red(d, "CV-L0 旧别名残留")
        assert canonical in "".join(hits)
        assert alias in "".join(hits)

    def test_nested_alias_also_blocks(self):
        d = _copy()
        _node(d, "DSC-07")["facets"][0]["semantics_zh"] = "藏在腿里的旧名"
        _red(d, "CV-L0 旧别名残留 semantics_zh")


# ── 红队 4：CV-BUS 总线挂载 ──────────────────────────────────────────────────
class TestRedBus:
    def test_module_ref_without_module_id_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["module_id"] = None
        _red(d, "CV-BUS——module_ref 非空而 module_id 空")

    def test_module_id_wrong_form_blocks(self):
        """自造号（非 MOD-* 形态）必红。"""
        d = _copy()
        _node(d, "DSC-01")["module_id"] = "数据调度器本体"
        _red(d, "非 MOD-* 形态")

    def test_module_id_not_in_projection_blocks(self):
        """module_ref 指向在盘但无在册 claim 的路径（sector_state_pipeline.py）→ 判红。"""
        d = _copy()
        n = _node(d, "DSC-09")
        n["module_ref"] = "src/zephyr/data/sector_state_pipeline.py"
        n["module_id"] = "MOD-L00-004"
        _red(d, "不在 depgraph 派生在册投影内")

    def test_module_id_disagrees_with_projection_blocks(self):
        """在册但张冠李戴（把 scheduler 的号挂到别的路径上）→ 判红。"""
        d = _copy()
        n = _node(d, "DSC-11")
        n["module_id"] = "MOD-L00-004"  # 在册投影给 backup_reconciler 的是 MOD-INF-043
        _red(d, "与在册投影", "不符")

    def test_null_module_id_without_red_reason_blocks(self):
        """无实现代码的节点必须写"为什么 null"（纯结构/终点聚合/gap 皆不豁免）。"""
        d = _copy()
        _node(d, "DSC-12")["red_reason"] = None
        _red(d, "module_id 为空必配 red_reason")


# ── 红队 5：CV-DUAL 双轴与骨架同源 ───────────────────────────────────────────
class TestRedDualAxis:
    def test_lying_production_blocks(self):
        """骨架 🛠 环节宣 production = 谎（多判一个即红）。"""
        d = _copy()
        n = _node(d, "DSC-06")
        n["verified_scope"] = "production"
        n["confidence"] = "verified"
        n["freshness_evidence"] = [dict(_node(d, "DSC-01")["freshness_evidence"][0])]
        hits = _red(d, "谎——verified_scope=production")
        assert any("骨架 §1 行级态" in h for h in hits)

    def test_missing_production_blocks(self):
        """骨架 ✅ 环节未宣 production = 欠（少判一个也是红，禁"图比骨架干净"）。"""
        d = _copy()
        _node(d, "DSC-17")["verified_scope"] = "structure"
        _red(d, "欠——骨架 ✅ 环节未宣 production")

    def test_production_without_freshness_blocks(self):
        d = _copy()
        _node(d, "DSC-13")["freshness_evidence"] = []
        _red(d, "必带 freshness_evidence")

    def test_freshness_missing_field_blocks(self):
        d = _copy()
        ev = _node(d, "DSC-01")["freshness_evidence"][0]
        ev.pop("lag_trading_days")
        _red(d, "缺字段 ['lag_trading_days']")

    def test_probe_failed_cannot_pass_production(self):
        """探测失败必判红——禁把"查不到"写成"无问题"（本役宪法性纪律）。"""
        d = _copy()
        ev = _node(d, "DSC-02")["freshness_evidence"][0]
        ev["verdict"] = "probe_failed"
        _red(d, "probe_failed 一律不得放行 production")

    def test_illegal_verdict_enum_blocks(self):
        d = _copy()
        ev = _node(d, "DSC-17")["freshness_evidence"][0]
        ev["verdict"] = "looks_fine"
        _red(d, "verdict 非法")

    def test_silent_channel_is_not_evidence(self):
        """ch_reader.query 的失败→空串语义不得作证据（★坑1 机生版）。"""
        d = _copy()
        ev = _node(d, "DSC-04")["freshness_evidence"][0]
        ev["channel"] = "ch_reader.query(sql)"
        _red(d, "属失败返回空串语义")

    def test_facet_row_cannot_claim_production(self):
        d = _copy()
        _node(d, "DSC-07")["verified_scope"] = "production"
        _red(d, "CV-FACET——分面行禁宣 production")

    def test_skeleton_unreadable_degrades_to_warn_not_error(self):
        """骨架不可读=环境异常域：CV-DUAL 的 ✅ 对照降 warn，绝不升级为 error。"""
        d = _copy()
        warnings: list[str] = []
        errors = validate_structure(d, _REPO / "no_such_dir", warnings)
        assert any("状态列不可读" in w for w in warnings), warnings
        assert not any("谎——" in e or "欠——" in e for e in errors), errors


# ── 红队 6：CV-FACET 分面 ────────────────────────────────────────────────────
class TestRedFacets:
    def test_single_leg_facet_blocks(self):
        d = _copy()
        _node(d, "DSC-07")["facets"] = [_node(d, "DSC-07")["facets"][0]]
        _red(d, "facets 须为 ≥2 条腿的列表")

    def test_facet_without_evidence_blocks(self):
        """禁"印象 ✅"——每条腿都得带实测。"""
        d = _copy()
        _node(d, "DSC-09")["facets"][0]["evidence"] = []
        _red(d, "腿无证据即不许标态")

    def test_facet_illegal_status_blocks(self):
        d = _copy()
        _node(d, "DSC-08")["facets"][0]["status"] = "基本没问题"
        _red(d, "腿态非法")


# ── 红队 7：CV-GAP / CV-WAIT 缺口显性化 ─────────────────────────────────────
class TestRedGaps:
    def test_gap_without_red_reason_blocks(self):
        d = _copy()
        _node(d, "DSC-GAP-NAV")["red_reason"] = None
        _red(d, "gap 节点必带 red_reason")

    def test_gap_with_module_ref_blocks(self):
        d = _copy()
        _node(d, "DSC-GAP-NAV")["module_ref"] = "src/zephyr/data/ch_writer.py"
        _node(d, "DSC-GAP-NAV")["module_id"] = "MOD-L00-004"
        _red(d, "gap 节点禁挂 module_ref/module_id")

    def test_gap_island_blocks(self):
        """缺口画成孤岛=隐没的第一步：删掉唯一连边必须红。"""
        d = _copy()
        d["edges"] = [e for e in d["edges"] if e.get("from") != "DSC-GAP-FFSIG" and e.get("to") != "DSC-GAP-FFSIG"]
        d["counts"]["edges"] = len(d["edges"])
        _red(d, "gap 节点必须至少有一条边")

    def test_gap_not_referenced_by_any_node_blocks(self):
        """所有环节的 gap_refs 都抹掉该缺口 ⇒ 缺口与生产面脱钩，判红。"""
        d = _copy()
        for n in d["nodes"]:
            if "DSC-GAP-MACRO" in (n.get("gap_refs") or []):
                n["gap_refs"] = [g for g in n["gap_refs"] if g != "DSC-GAP-MACRO"]
        _red(d, "未被任何环节的 gap_refs 指到")

    def test_gap_refs_to_missing_node_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["gap_refs"].append("DSC-GAP-NOPE")
        _red(d, "gap_refs 指向不存在节点")

    def test_waiting_tables_list_missing_blocks(self):
        d = _copy()
        _node(d, "DSC-GAP-NAV")["node_type"] = "stage"
        _red(d, "不是 gap 节点")

    def test_waiting_table_entry_pointing_to_missing_node_blocks(self):
        d = _copy()
        d["boundary"]["waiting_table_gaps"]["c1_market.account_nav_daily"] = "DSC-GAP-GONE"
        _red(d, "等未产表 c1_market.account_nav_daily 指向不存在节点")

    def test_erasing_one_waiting_table_from_ledger_blocks(self):
        """已实见的 5 处断供被从账上抹掉一笔 ⇒ 覆盖数下限判红（禁以删账让图变干净）。"""
        d = _copy()
        d["boundary"]["waiting_table_gaps"].pop("c1_market.factor_signal")
        _red(d, "等未产表覆盖数 4 < 下限 5")

    def test_gap_node_deleted_from_graph_blocks(self):
        """直接把缺口节点从图里摘掉 ⇒ 同时踩中 CV-WAIT（账上指向不存在节点）与 gap_refs 断链。"""
        d = _copy()
        _drop_node(d, "DSC-GAP-FFVAL")
        d["counts"]["nodes"] = len(d["nodes"])
        d["counts"]["edges"] = len(d["edges"])
        _red(d, "幽灵引用" if False else "等未产表 c1_market.factor_feature_value 指向不存在节点")

    def test_ghost_ref_needs_ghost_reason(self):
        d = _copy()
        _node(d, "DSC-GAP-NEWSGHOST")["red_reason"] = "terminal"
        _red(d, "red_reason 必须为 ghost_ref")

    def test_waiting_table_must_appear_in_gap_anchors(self):
        """表名从 gap 节点锚里抹掉 ⇒ 账面还在、图里查无 ⇒ 判红（禁隐没）。"""
        d = _copy()
        n = _node(d, "DSC-GAP-EXECEP")
        n["data_refs"] = []
        n["source_anchors"] = ["file:src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py"]
        _red(d, "未出现在 gap 节点")

    def test_missing_boundary_waiting_list_blocks(self):
        d = _copy()
        d["boundary"].pop("waiting_table_gaps")
        _red(d, "boundary 缺 waiting_table_gaps")


# ── 红队 8：数据锚在册实存（不连 CH，注入解析桩）────────────────────────────
class TestRedAnchors:
    def test_bogus_table_anchor_on_stage_node_blocks(self):
        """不存在的表混在普通环节里=假引用；只有登记在册的缺席表可挂在 gap 节点上。"""
        d = _copy()
        _node(d, "DSC-06")["data_refs"].append("c1_market.table_that_does_not_exist")
        errors, _w = check_anchors(d, _REPO, resolver=lambda _want: set())
        assert any("指向不存在的表" in e for e in errors), errors

    def test_bogus_task_anchor_blocks(self):
        d = _copy()
        _node(d, "DSC-07")["source_anchors"].append("task:no_such_task_id_zzz")
        errors, _w = check_anchors(d, _REPO)
        assert any("task 锚不在册" in e for e in errors), errors

    def test_bogus_slot_anchor_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["source_anchors"].append("slot:slot_never_declared")
        errors, _w = check_anchors(d, _REPO)
        assert any("slot 锚不在册" in e for e in errors), errors

    def test_bogus_file_anchor_blocks(self):
        d = _copy()
        _node(d, "DSC-04")["source_anchors"].append("file:src/zephyr/data/never_written.py")
        errors, _w = check_anchors(d, _REPO)
        assert any("file 锚路径不存在" in e for e in errors), errors

    def test_module_ref_path_anchor_missing_blocks(self):
        d = _copy()
        _node(d, "DSC-01")["module_ref"] = "src/zephyr/data/never_written_xyz.py"
        errors, _w = check_anchors(d, _REPO, resolver=lambda _want: set())
        assert any("module_ref 路径锚磁盘实存检查失败" in e for e in errors), errors

    def test_absent_table_is_legal_only_on_gap_node(self):
        """反向蓝例：ghost 表锚在 gap 节点上不该被"表不存在"判红（它由 CV-WAIT 管）。"""
        d = _copy()
        errors, _w = check_anchors(d, _REPO, resolver=lambda _want: set())
        assert not any("DSC-GAP-NEWSGHOST" in e and "不存在的表" in e for e in errors), errors

    def test_table_anchor_unverified_when_ch_absent(self):
        """CH 不可达 → 只 warn 不阻断，且 warn 文案禁把未核验读成已核验。"""
        d = _copy()
        import validate_data_supply_chain_map as v

        original = v._ch_table_resolver  # noqa: SLF001 — 专测降级腿
        v._ch_table_resolver = lambda _root: None
        try:
            errors, warnings = check_anchors(d, _REPO)
        finally:
            v._ch_table_resolver = original
        assert errors == []
        assert any("未核验" in w for w in warnings), warnings


# ── 红队 9：INV-1 引用不复制 ─────────────────────────────────────────────────
class TestRedInv1:
    def _prose_from_tasks(self) -> str:
        tasks = yaml.safe_load((_REPO / "src/zephyr/data/config/tasks.yaml").read_text(encoding="utf-8"))["tasks"]
        for t in tasks:
            for cand in ((t.get("extra") or {}).get("description"), t.get("disabled_reason")):
                if isinstance(cand, str) and len(cand) >= 40 and sum(1 for ch in cand if "一" <= ch <= "鿿") >= 10:
                    return cand.strip()
        raise AssertionError("前提失效：tasks.yaml 未找到足够长的正文样本")

    def test_copying_task_description_blocks(self):
        d = _copy()
        _node(d, "DSC-02")["note_zh"] = self._prose_from_tasks()
        errors = check_inv1(d, _REPO)
        assert any("INV-1 复制侵权" in e for e in errors), errors

    def test_copying_into_freshness_evidence_blocks(self):
        """复制侵权不止发生在注解释——塞进证据字段一样红。"""
        d = _copy()
        ev = _node(d, "DSC-01")["freshness_evidence"][0]
        ev["final_variant"] = self._prose_from_tasks()
        errors = check_inv1(d, _REPO)
        assert any("INV-1 复制侵权" in e for e in errors), errors

    def test_identifier_reference_is_not_a_violation(self):
        d = _copy()
        _node(d, "DSC-07")["note_zh"] = "引用 task_id=technical_indicator_incremental 与表 kline_daily"
        assert check_inv1(d, _REPO) == []


# ── 红队 10：生成器纪律（幂等 + 禁取时 + 必经翻译 loader + 双轴同源）─────────
class TestRedGenerator:
    def _load_generator(self):
        sys.modules.pop("generate_data_supply_chain_map", None)
        spec = importlib.util.spec_from_file_location(
            "generate_data_supply_chain_map", _GENERATORS_DIR / "generate_data_supply_chain_map.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_generator_is_idempotent(self, tmp_path):
        gen = self._load_generator()
        first = tmp_path / "a.yaml"
        second = tmp_path / "b.yaml"
        assert gen.main(["--root", str(_REPO), "--out", str(first)]) == 0
        assert gen.main(["--root", str(_REPO), "--out", str(second)]) == 0
        assert first.read_bytes() == second.read_bytes(), "同输入两次产出不逐字节等=非幂等"

    def test_regenerating_over_existing_output_is_stable(self, tmp_path):
        """existing-wins 的人工层在重跑后不得漂移（幂等的第二条腿）。"""
        gen = self._load_generator()
        target = tmp_path / "map.yaml"
        assert gen.main(["--root", str(_REPO), "--out", str(target)]) == 0
        before = target.read_bytes()
        assert gen.main(["--root", str(_REPO), "--out", str(target)]) == 0
        assert target.read_bytes() == before

    def test_generator_derives_production_set_from_skeleton(self):
        """生成器不得自带一套 ✅ 口径：production 集合必须等于骨架 §1 实扫 ✅ 集合。"""
        gen = self._load_generator()
        doc = gen.build_document(_REPO, None)
        skel_ok = {nid for nid, sym in gen.scan_skeleton_status(_REPO).items() if sym == "✅"}
        prod = {n["node_id"] for n in doc["nodes"] if n["verified_scope"] == "production"}
        assert skel_ok and prod == skel_ok

    def test_generator_refuses_to_emit_axis_mismatch(self, tmp_path, monkeypatch):
        """骨架 ✅ 集与人工层 production 断言不一致 ⇒ 生成期硬失败（禁产出自粉饰的图）。"""
        gen = self._load_generator()
        real = scan_skeleton_status(_REPO)
        assert real["DSC-19"] != "✅" and not _node(_GOOD, "DSC-19")["freshness_evidence"]
        # 骨架把无新鲜度证据的一行标成 ✅ ⇒ production 集与骨架集不再相等 ⇒ 生成期硬失败
        monkeypatch.setattr(gen, "scan_skeleton_status", lambda _root: {**real, "DSC-19": "✅"})
        with pytest.raises(RuntimeError, match="双轴与骨架不一致"):
            gen.build_document(_REPO, None)

    def test_generator_has_no_wall_clock_calls(self):
        """AST 级判据（禁 substring——注释里写"禁 datetime.now()"本身会自触）。"""
        src = (_GENERATORS_DIR / "generate_data_supply_chain_map.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        banned_imports = {"time", "datetime", "arrow", "pendulum"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in banned_imports, (
                        f"生成器 import {alias.name}（RULE-SCHEMA-TZ 禁取时）"
                    )
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or "").split(".")[0]
                assert root not in banned_imports, f"生成器 from {node.module} import"
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"now", "utcnow", "today", "monotonic", "perf_counter"}, "生成器含取时调用"
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "time":
                    raise AssertionError("生成器调用 time.*")

    def test_generator_uses_shared_translation_loader(self):
        src = (_GENERATORS_DIR / "generate_data_supply_chain_map.py").read_text(encoding="utf-8")
        assert "terminology_loader" in src and "get_zh(" in src
        assert "module_translation_loader" in src

    def test_generator_output_validates(self, tmp_path):
        """生成器产物必须直接过校验器（结构面），否则机生层与判据脱节。"""
        gen = self._load_generator()
        out = tmp_path / "map.yaml"
        assert gen.main(["--root", str(_REPO), "--out", str(out)]) == 0
        assert validate_structure(yaml.safe_load(out.read_text(encoding="utf-8")), _REPO) == []

    def test_node_enumeration_is_four_source_not_tasks_only(self):
        """枚举四源硬约束：D12-19/20/21 三枚新环节的生产者都不在 tasks.yaml 面内。"""
        gen = self._load_generator()
        doc = gen.build_document(_REPO, None)
        machine = doc["machine"]["sources"]
        assert doc["counts"]["stage_nodes"] == EXPECTED_STAGES
        assert machine["tasks_yaml"]["tasks_total"] > 0
        assert machine["skeleton_status"]["rows_scanned"] == EXPECTED_STAGES
        assert machine["process_in_product"]["tables"], "第四源（进程内在产写手）必须机生可见"
        assert set(machine["skeleton_status"]["production_nodes"]) == {
            n["node_id"] for n in doc["nodes"] if n["verified_scope"] == "production"
        }


# ── CLI 退出码语义 ──────────────────────────────────────────────────────────
class TestCliExitCodes:
    """exit 1=违规，exit 2=文件/解析失败（照图9/图11 母版语义）。"""

    def _run_cli(self, argv):
        import validate_data_supply_chain_map as v

        original = sys.argv
        sys.argv = ["validate_data_supply_chain_map.py", *argv]
        try:
            return v.main()
        finally:
            sys.argv = original

    def test_good_map_exits_zero(self, tmp_path):
        assert self._run_cli(["--map", str(_REPO / _MAP_REL), "--skip-anchors", "--skip-bus"]) == 0

    def test_missing_file_exits_two(self, tmp_path):
        assert self._run_cli(["--map", str(tmp_path / "nowhere.yaml")]) == 2

    def test_corrupt_yaml_exits_two(self, tmp_path):
        p = tmp_path / "broken.yaml"
        p.write_text("nodes: [unclosed", encoding="utf-8")
        assert self._run_cli(["--map", str(p)]) == 2

    def test_non_dict_top_exits_two(self, tmp_path):
        p = tmp_path / "list.yaml"
        p.write_text("- a\n- b\n", encoding="utf-8")
        assert self._run_cli(["--map", str(p)]) == 2

    def test_structural_violation_exits_one(self, tmp_path):
        d = _copy()
        _node(d, "DSC-11")["segment"] = "S9_databreach"
        p = tmp_path / "bad.yaml"
        p.write_text(yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")
        assert self._run_cli(["--map", str(p), "--skip-anchors", "--skip-inv1", "--skip-bus"]) == 1
