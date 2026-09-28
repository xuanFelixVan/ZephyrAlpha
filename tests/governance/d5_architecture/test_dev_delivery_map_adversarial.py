# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §dev_delivery_map
# [MODULE] tests.governance.d5_architecture.test_dev_delivery_map_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] none（只读校验/生成器，无状态写盘）
# [DEPENDENCIES] pytest; yaml; hashlib; scripts.governance.d5_architecture.validators.validate_dev_delivery_map;
#   scripts.governance.d5_architecture.generators.generate_dev_delivery_map
# [CONSUMERS] 图 11 校验器质量守卫（坏图必须被拦——判通过的校验器必须先证明自己会红）；
#   图 11 生成器幂等实证（同输入两次产出逐字节等）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于内存副本（不碰生产路径、不写 config/）；好图控制组=真实图必须
#   通过；每个红用例断言"校验器必须报出这一条"（错误语义逐条钉死，不只看非空）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图 11 交付流水线全景图校验器对抗测试——红优先：每种坏图必须被点名报出，好图必须通过。

覆盖红案（≥14 类，逐条对应校验器判据）：伪造节点越出契约全集 / 断链边 / 越域挂载（把别的图节点
接进本图、把 TDM 的 judgment_basis 塞进本图节点）/ 未声明反馈环的反向边 / built 无代码锚 /
verified 无 evidence / 车道归属缺失或非法 / 缺环节 / store 路径不存在 / INV-1 复制侵权
（门禁册与 tasks.yaml 等机生真源正文抄进节点，红队补洞 2026-09-24 起语料全覆盖）/ 枚举非法值 /
重复边 / 自环 / node_id 重复 / 坏字段形态报"缺必填"不抛异常 / decision_question 超长 /
counts 与实数不符（含 by_verified_scope、by_lane）/ 缺顶层必填键 / 生成器非幂等与取时禁令守卫；
**本波新增判据各自的能红用例**：CV-BUS（module_ref 非空而 module_id 空 / 自造号非 MOD-* 形态 /
空挂总线 / null 不写 red_reason）、CV-DUAL（🔨 环节冒充 production 的谎 / ✅ 环节降级为欠 /
production 无 exec_evidence / production×proposed 混搭 / verified_scope 与 wiring_status 枚举外值）、
CV-L0（note_zh/doc_refs 旧名残留 mech_note_zh/design_refs）、CV-GAP（gap 节点孤岛 / 洗成 stage /
red_reason 枚举外）、外部面不可达只降 warn 不升 error；
绿组另钉口径面：production 数==骨架 ✅ 数（26）、gap 节点=2、有码环节必挂 module_id。
"""

from __future__ import annotations

import copy
import hashlib
import re
import sys
from pathlib import Path

import pytest
import yaml

pytest.skip(
    "SUBJECT-RETIRED: config/dev_delivery_map.yaml retired in 531ac17ef7; validator "
    "validate_dev_delivery_map never committed (git log --all empty). Adversarial guard "
    "retires with its subject (chief final-verify disposal 2026-09-28).",
    allow_module_level=True,
)

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

from validate_dev_delivery_map import (  # noqa: E402
    GAP_NODES,
    NODE_UNIVERSE,
    scan_skeleton_status,
    validate_structure,
)

_GOOD = yaml.safe_load((_REPO / "config" / "dev_delivery_map.yaml").read_text(encoding="utf-8"))


def _find(d: dict, node_id: str) -> dict:
    return next(n for n in d["nodes"] if n["node_id"] == node_id)


def _errs(d: dict) -> list[str]:
    return validate_structure(d, root=_REPO)


# ---------------------------------------------------------------------------
# 绿组：判据不放宽的前提下，真图必须零 error（校验器不是恒红，红组证明不是恒绿）
# ---------------------------------------------------------------------------


def test_green_real_map_passes():
    assert _errs(copy.deepcopy(_GOOD)) == []


# ---------------------------------------------------------------------------
# 红组：每条断言"校验器必须报出这一条"
# ---------------------------------------------------------------------------


def test_red_fake_node_beyond_universe():
    """伪造节点（越出 28 环节契约全集）→ 必须报"越出环节契约全集"。"""
    d = copy.deepcopy(_GOOD)
    rogue = copy.deepcopy(_find(d, "D11-S01"))
    rogue["node_id"] = "D11-X99"
    d["nodes"].append(rogue)
    assert any("越出" in e and "D11-X99" in e for e in _errs(d))


def test_red_dangling_edge():
    """断链边（边指向不存在节点）→ 必须报"边引用了不存在的节点"。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D11-S01", "D11-不存在"])
    assert any("边引用了不存在的节点" in e for e in _errs(d))


def test_red_cross_domain_mount():
    """越域挂载（把图 9 的 FAC-E4 接进本图）→ 必须报边引用不存在节点（本图不认外来节点）。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D11-C10", "FAC-E4"])
    assert any("边引用了不存在的节点: D11-C10->FAC-E4" in e for e in _errs(d))


def test_red_undeclared_feedback_edge():
    """未声明反馈环的反向边（D04→S01 逆契约序）→ 必须报"未声明为反馈环的反向边"。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D11-D04", "D11-S01"])
    assert any("未声明为反馈环的反向边" in e for e in _errs(d))


def test_red_declared_feedback_allowed():
    """对照：把同一反向边显式声明进 feedback_loops → 该反向边不再报红（声明通道有效）。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D11-D04", "D11-S01"])
    d["feedback_loops"].append({"from": "D11-D04", "to": "D11-S01", "note": "测试声明通道"})
    errs = _errs(d)
    assert not any("未声明为反馈环的反向边" in e for e in errs)


def test_red_built_without_module_ref_anchor():
    """built 节点删掉 module_ref 代码锚 → 必须报"built 节点必须有 module_ref 代码锚"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-C01")
    assert node["build_status"] == "built"
    node["module_ref"] = None
    assert any("module_ref 代码锚" in e and "D11-C01" in e for e in _errs(d))


def test_red_verified_without_evidence():
    """去掉 verified 节点的 evidence（结构断言无实查支撑）→ 必须报"verified 必带 evidence"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-S05")  # 骨架 🔨 节点（verified/structure）
    assert node["confidence"] == "verified"
    node["evidence"] = []
    assert any("verified 必带 evidence" in e and "D11-S05" in e for e in _errs(d))


def test_red_missing_lane_attribution():
    """三车道车道归属缺失（删 lane 字段）→ 必须报"车道归属必填"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C09").pop("lane")
    assert any("车道归属必填" in e for e in _errs(d))


def test_red_lane_mismatch():
    """lane 值非法（越出 S/C/D）→ 必须报车道归属。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C09")["lane"] = "X"
    assert any("车道归属必填" in e for e in _errs(d))


def test_red_missing_stage_node():
    """节点越出全集的另一半：抽掉一个契约环节 → 必须报"缺环节"。"""
    d = copy.deepcopy(_GOOD)
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D11-D05"]
    assert any("缺环节" in e and "D11-D05" in e for e in _errs(d))


def test_red_store_path_not_exists():
    """store 路径锚指向不存在目录 → 必须报"路径锚磁盘实存"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-C08")
    node["store_refs"] = [
        dict(artifact="假入库位", location="docs/_working/no_such_store_xyz/", key="qid", retention="永久")
    ]
    assert any("路径锚磁盘实存" in e for e in _errs(d))


def test_red_inv1_copy_violation_from_gate_registry():
    """INV-1 复制侵权：把门禁册（shell 侧 gate_registry.yaml）某条目 description 正文
    整段抄进节点 mech_note_zh → 必须报"INV-1 复制侵权"。图节点只准存标识符与指针。"""
    reg = yaml.safe_load(
        (_REPO / "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml").read_text(encoding="utf-8")
    )
    bodies = [g.get("description", "").strip() for g in reg.get("gates", [])]
    stolen = next(b for b in bodies if len(b) >= 25)
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C05")["note_zh"] = stolen
    assert any("INV-1 复制侵权" in e for e in _errs(d))


def test_red_illegal_enums():
    """枚举非法值（build_status / confidence）→ 两条必须分别报出。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-S03")
    node["build_status"] = "almost_built"
    node["confidence"] = "certain"
    errs = _errs(d)
    assert any("build_status 非法" in e for e in errs)
    assert any("confidence 非法" in e for e in errs)


def test_red_duplicate_edge():
    """重复边 → 必须报"重复边"。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(list(d["edges"][0]))
    assert any("重复边" in e for e in _errs(d))


def test_red_self_loop():
    """自环 → 必须报"自环边"。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D11-C10", "D11-C10"])
    assert any("自环边" in e for e in _errs(d))


def test_red_duplicate_node_id():
    """node_id 重复（克隆一个契约环节）→ 必须报"node_id 存在重复"。"""
    d = copy.deepcopy(_GOOD)
    d["nodes"].append(copy.deepcopy(_find(d, "D11-C01")))
    assert any("node_id 存在重复" in e for e in _errs(d))


def test_red_decision_question_overflow():
    """decision_question 超 120 字上限 → 必须报超长。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-S02")["decision_question"] = "问" * 121
    assert any("decision_question 超" in e for e in _errs(d))


def test_red_counts_mismatch_rejects_handedit():
    """counts 与实数不符（手改图不回生成）→ 必须报 counts 不一致。"""
    d = copy.deepcopy(_GOOD)
    d["counts"]["total_nodes"] = 999
    assert any("counts.total_nodes" in e for e in _errs(d))


def test_red_missing_top_key():
    """缺顶层必填键（laws）→ 必须报缺键。"""
    d = copy.deepcopy(_GOOD)
    d.pop("laws")
    assert any("缺顶层必填键: laws" in e for e in _errs(d))


def test_red_store_refs_none_reports_not_crash():
    """store_refs 写成 null → 必须报缺必填字段而非抛异常（ERROR_CONTRACT：exit 1 不是 traceback）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C01")["store_refs"] = None
    assert any("缺必填字段 store_refs" in e for e in _errs(d))


def test_red_inv1_cross_source_copy_from_tasks_yaml():
    """宪章级红线·跨真源抄录：把 tasks.yaml 条目正文抄进图 11 节点 → INV-1 必须判红
    （红队补洞 2026-09-24：INV-1 语料从门禁册扩至全部机生真源册）。"""
    tasks = yaml.safe_load((_REPO / "src" / "zephyr" / "data" / "config" / "tasks.yaml").read_text(encoding="utf-8"))

    def _strings(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                yield from _strings(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                yield from _strings(v)
        elif isinstance(obj, str):
            yield obj.strip()

    stolen = next((s for s in _strings(tasks) if len(s) >= 25 and sum(1 for c in s if "一" <= c <= "鿿") >= 10), None)
    assert stolen, "tasks.yaml 无可抄正文——探针前提失效"
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C05")["note_zh"] = stolen
    assert any("INV-1 复制侵权" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·生成器侧：非幂等=事故（同输入两次产出必须逐字节等）+ RULE-SCHEMA-TZ 取时禁令
# ---------------------------------------------------------------------------


def test_red_generator_is_byte_idempotent():
    import generate_dev_delivery_map as gen

    doc1 = gen.serialize_document(gen.build_document(as_of="2026-09-24T12:00:00+08:00", root=_REPO))
    doc2 = gen.serialize_document(gen.build_document(as_of="2026-09-24T12:00:00+08:00", root=_REPO))
    h1 = hashlib.sha256(doc1.encode("utf-8")).hexdigest()
    h2 = hashlib.sha256(doc2.encode("utf-8")).hexdigest()
    assert h1 == h2, "生成器同输入两次产出不逐字节等=非幂等事故"


def test_red_generator_free_of_wall_clock():
    """RULE-SCHEMA-TZ 硬规则：生成器禁 datetime.now()/time.time()（时间戳必经入参/HEAD 派生）。
    源码级守卫——一旦有人改回取时，本用例必须变红。"""
    src = (
        _REPO / "scripts" / "governance" / "d5_architecture" / "generators" / "generate_dev_delivery_map.py"
    ).read_text(encoding="utf-8")
    assert not re.search(r"datetime\.now\(\)", src), "生成器出现 datetime.now()（违反取时禁令）"
    assert not re.search(r"time\.time\(\)", src), "生成器出现 time.time()（违反取时禁令）"


def test_red_universe_contract_covers_30_nodes_9_13_6_plus_2_gap():
    """契约面自检：28 环节（S9/C13/D6）+2 gap=30——改契约必先回写骨架/终局卷，此断言挡静默漂移。"""
    assert len(NODE_UNIVERSE) == 30
    lanes = {"S": 0, "C": 0, "D": 0}
    for nid in NODE_UNIVERSE:
        if nid.endswith(("G01", "G02")):
            continue
        lanes[nid.split("-")[1][0]] += 1
    assert lanes == {"S": 9, "C": 13, "D": 6}
    assert GAP_NODES == ("D11-G01", "D11-G02")


def test_green_dual_axis_matches_skeleton_counts():
    """口径面绿证：真图 production 数==骨架 ✅ 数、gap 节点数=2、module_id 挂满有码环节。"""
    skel = scan_skeleton_status(_REPO)
    prod = [n for n in _GOOD["nodes"] if n.get("verified_scope") == "production"]
    assert len(prod) == sum(1 for v in skel.values() if v == "✅") == 26
    assert sum(1 for n in _GOOD["nodes"] if n.get("node_type") == "gap") == 2
    assert all(n.get("module_id") for n in _GOOD["nodes"] if n.get("module_ref"))
    assert all(n.get("red_reason") for n in _GOOD["nodes"] if not n.get("module_id"))
    # L0 统一名落实：节点**字段名**零旧名残留（ssot_note_zh 散文里提废止名是说明，不算残留）
    for n in _GOOD["nodes"]:
        assert not (set(n) & {"mech_note_zh", "design_refs", "semantics_zh", "clock_semantics_zh"}), (
            f"旧字段名残留于 {n.get('node_id')}"
        )


# ---------------------------------------------------------------------------
# 红组·CV-BUS（module_id 总线挂载，六图终局卷 §2 裁定二）
# ---------------------------------------------------------------------------


def test_red_module_ref_without_module_id():
    """有实现代码却不挂总线号 → CV-BUS 必报"module_ref 非空而 module_id 空"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C10")["module_id"] = None
    _find(d, "D11-C10")["red_reason"] = "terminal"  # 只补 red_reason 也挡不住：ref 在、号缺
    assert any("CV-BUS" in e and "D11-C10" in e and "module_id 空" in e for e in _errs(d))


def test_red_fabricated_module_id_shape():
    """自造号（非 MOD-* 形态）→ 必报"非 MOD-* 形态"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C08")["module_id"] = "MY-SELF-MADE-001"
    assert any("非 MOD-* 形态" in e and "D11-C08" in e for e in _errs(d))


def test_red_module_id_hanging_without_ref():
    """空挂总线（无 module_ref 却报号）→ 必报"空挂总线=假引用"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-G01")
    node["module_id"] = "MOD-GOV-046"
    assert any("空挂总线" in e and "D11-G01" in e for e in _errs(d))


def test_red_null_module_id_without_red_reason():
    """module_id 为空却不写因 → 必报"必配 red_reason"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-G02")
    node.pop("red_reason")
    assert any("必配 red_reason" in e and "D11-G02" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·CV-DUAL（confidence×verified_scope 双轴与骨架三态同源）
# ---------------------------------------------------------------------------


def test_red_structure_node_disguised_as_production():
    """谎：骨架 🔨 环节（S05）冒充 production → 必报"谎…骨架 §1 状态标为 🔨"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-S05")
    node["verified_scope"] = "production"
    node["build_status"] = "built"
    node["exec_evidence"] = ["伪造的在产声明"]
    errs = _errs(d)
    assert any("谎" in e and "D11-S05" in e for e in errs)
    assert any("production 数" in e for e in errs)


def test_red_production_claim_undercount_is_red():
    """欠：把骨架 ✅ 环节（S06）降成 structure → 必报"欠…未宣 production"+计数红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-S06")["verified_scope"] = "structure"
    errs = _errs(d)
    assert any("欠" in e and "D11-S06" in e for e in errs)
    assert any("production 数" in e for e in errs)


def test_red_production_without_exec_evidence():
    """production 却无复跑在产证据 → 必报"必带 exec_evidence"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C10")["exec_evidence"] = []
    assert any("exec_evidence" in e and "D11-C10" in e for e in _errs(d))


def test_red_exec_evidence_pure_prose_has_no_rerun_handle():
    """exec_evidence 写成纯散文（无命令无 file:line 锚）→ 必报"无可复跑把手"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C10")["exec_evidence"] = ["反正这一环是在产跑的"]
    assert any("无可复跑把手" in e and "D11-C10" in e for e in _errs(d))


def test_red_production_confidence_mismatch():
    """production × confidence=proposed 混搭 → 必报"production 必 verified"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C04")["confidence"] = "proposed"
    assert any("production 必 verified" in e and "D11-C04" in e for e in _errs(d))


def test_red_illegal_verified_scope_and_wiring_enums():
    """verified_scope / wiring_status 枚举外值 → 两条分别报红（禁自造口径值）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C13")["verified_scope"] = "prod"
    _find(d, "D11-C13")["wiring_status"] = "half_wired"
    errs = _errs(d)
    assert any("verified_scope 非法" in e for e in errs)
    assert any("wiring_status 非法" in e for e in errs)


def test_red_counts_by_verified_scope_drift():
    """手改 counts.by_verified_scope（图不回生成器）→ 必报与节点实扫不符。"""
    d = copy.deepcopy(_GOOD)
    d["counts"]["by_verified_scope"]["production"] = 99
    assert any("by_verified_scope" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·L0 统一名 / 越域挂载 / gap 节点结构
# ---------------------------------------------------------------------------


def test_red_legacy_field_name_residue():
    """字段旧名残留（把 note_zh 改回 mech_note_zh）→ 必报"L0 统一名应为 note_zh"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-S03")
    node["mech_note_zh"] = node.pop("note_zh")
    errs = _errs(d)
    assert any("字段旧名残留 mech_note_zh" in e and "D11-S03" in e for e in errs)
    assert any("缺必填字段 note_zh" in e and "D11-S03" in e for e in errs)


def test_red_doc_refs_legacy_design_refs_residue():
    """doc_refs 被写回旧名 design_refs → 必报旧名残留且缺必填 doc_refs。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-D01")
    node["design_refs"] = node.pop("doc_refs")
    errs = _errs(d)
    assert any("字段旧名残留 design_refs" in e for e in errs)
    assert any("缺必填字段 doc_refs" in e for e in errs)


def test_red_cross_domain_judgment_basis_mount():
    """越域挂载（把 TDM 的 judgment_basis 塞进本图节点）→ 必报"越域挂载"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-C05")["judgment_basis"] = ["因子A>", "情绪B<"]
    assert any("越域挂载" in e and "judgment_basis" in e for e in _errs(d))


def test_red_required_key_absent_not_none():
    """双轴键整条消失（不是 null 而是没有）→ 必报"缺必填键 verified_scope"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-D03").pop("verified_scope")
    assert any("缺必填键 verified_scope" in e and "D11-D03" in e for e in _errs(d))


def test_red_gap_node_without_edge():
    """gap 节点画成孤岛（不连受影响环节）→ 必报"gap 节点必须至少有一条边"。"""
    d = copy.deepcopy(_GOOD)
    d["edges"] = [e for e in d["edges"] if "D11-G01" not in e]
    d["counts"]["total_edges"] = len(d["edges"])
    assert any("gap 节点必须至少有一条边" in e and "D11-G01" in e for e in _errs(d))


def test_red_gap_node_misdeclared_as_stage():
    """契约 gap 编号被改标 stage（缺口洗成正常环节）→ 必报"契约编号为 gap 节点但 node_type"。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D11-G02")
    node["node_type"] = "stage"
    assert any("契约编号为 gap 节点" in e and "D11-G02" in e for e in _errs(d))


def test_red_illegal_red_reason_enum():
    """red_reason 枚举外值（自造口径）→ 必报非法。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D11-D05")["red_reason"] = "sort_of_ok"
    assert any("red_reason 非法" in e and "D11-D05" in e for e in _errs(d))


def test_red_skeleton_cross_check_downgrades_when_absent(tmp_path):
    """骨架不可读时 CV-DUAL 的 ✅ 对照降 warn，绝不升级为 error（禁环境异常打死提交）。"""
    d = copy.deepcopy(_GOOD)
    warns: list[str] = []
    errs = validate_structure(d, root=tmp_path, warnings=warns)
    assert any("骨架三态列不可读" in w for w in warns)
    assert not any("production 数" in e for e in errs)
