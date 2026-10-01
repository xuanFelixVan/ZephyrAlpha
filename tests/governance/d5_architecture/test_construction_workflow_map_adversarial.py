# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §construction_workflow_map
# [MODULE] tests.governance.d5_architecture.test_construction_workflow_map_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; copy; hashlib; os; re; subprocess; sys;
#   scripts.governance.d5_architecture.validators.validate_construction_steps
#   （validate_structure / check_anchors / check_prose_counts / scan_skeleton_axes /
#   load_verifiability_values / STEP_UNIVERSE / GAP_NODES）;
#   scripts.governance.d5_architecture.generators.generate_construction_workflow_map
#   （build_document / serialize_document 幂等实证）
# [CONSUMERS] 图 14 校验器质量守卫（坏图必须被拦——判通过的校验器必须先证明自己会红）；
#   图 14 生成器幂等实证；construction_workflow_map_gate（同一判据真源的 gate 侧消费）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于内存副本（不碰生产路径、不写 config/ 与政策 MD）；
#   需要落盘的面只有三处，全部经 tmp_path：verifiability 词表 fixture、CLI 用的坏/漂移图、
#   boundary 回源占位件；好图控制组=真实图必须通过；
#   每个红用例断言"校验器必须报出这一条具体语义"，不只看非空；
#   形态照抄 test_dev_delivery_map_adversarial（图 11 母版红蓝先例）
# [MODIFY-GUARD] 本件是"校验器能红"的证据面：删用例或把断言放宽成"只判非空"=放水，
#   必须先改 validate_construction_steps 的判据再改本件；新增判据必同步新增能红用例
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图 14 AI 施工升级流校验器对抗测试——红优先：每种坏图必须被点名，好图必须通过。

红案清单（≥14 类，逐条对应校验器判据；编号取自
`docs/_working/map_build/fig14_construction/90_step_anchor_validator_spec.md` 的红证表）：
伪造环节越出契约全集 / 抽掉契约环节 / node_id 重复 / 断链边 / 未声明反馈环的反向边 /
**回边把主序连成环** / 自环混进 edges / 重复边 / order 撞号 / 缺顶层必填键 /
**双轴冒充**（🔨 环节宣 production 的谎、✅ 环节降级为欠、production 数≠骨架 ✅ 数、
production 无 exec_evidence、exec_evidence 无复跑把手、production×proposed 混搭、
CV-STATE 声称值与骨架实扫列不符）/ **CV-BUS**（module_id 缺、自造号、空 module_id 不写因）/
**CV-16**（verifiability=automated 而无 exec_source、声称 exec_source 而件不存在、
built 无实查证据、evidence 无日期前缀）/ 旧字段别名残留 / 越域挂载 / INV-1 抄政策正文 /
decision_question 超长 / counts 与实数不符 / 散文写死计数 / 枚举非法 /
**词表硬编码探针**（改词表 fixture 必须改判）/ CV-14 handoff 越域吞图 11 /
CV-GAP gap 孤岛与洗白 / CV-10 回边台账假门 / CV-04 政策↔图双向闭合（伪造与漏项两向）/
**锚块回落行为**（anchor_source=proposal 必须把欠账列全、=policy 必须清空）/
CV-GHOST 幽灵复活 / CV-15 boundary 引用断链 / 外部真源面不可达只降 warn 不升 error /
生成器非幂等与取时禁令。
绿组钉口径面：真图结构面零 error、gate 面（live=False）零 error、production 数==骨架 ✅ 数、
gap 节点 11（G10 幽灵复活依 invalidation 条款作废，2026-10-02 回写骨架+CR-15 在案）、政策面唯一已知红=§2.3 矩阵缺行（已登记在提案件 matrix_gaps，禁当噪声）。
"""

from __future__ import annotations

import copy
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

import validate_construction_steps as V  # noqa: E402
from validate_construction_steps import (  # noqa: E402
    GAP_NODES,
    STEP_UNIVERSE,
    check_anchors,
    check_prose_counts,
    load_verifiability_values,
    scan_skeleton_axes,
    validate_structure,
)

_GOOD = yaml.safe_load((_REPO / "config" / "construction_workflow_map.yaml").read_text(encoding="utf-8"))
_POLICY_REL = "docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md"
_POLICY = (_REPO / _POLICY_REL).read_text(encoding="utf-8", errors="replace")
_VOCAB_REL = "docs/01_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml"


def _find(d: dict, node_id: str) -> dict:
    return next(n for n in d["nodes"] if n["node_id"] == node_id)


def _errs(d: dict) -> list[str]:
    """结构/口径面（live=False）：与 gate 同面，磁盘与在册腿跳，判据一项不放宽。"""
    return validate_structure(d, root=_REPO, warnings=[], live=False)


def _live_errs(d: dict) -> list[str]:
    """带磁盘/在册探活的完整面（CV-05/06/07 的实存腿只有这里才跑）。"""
    return validate_structure(d, root=_REPO)


def _gate_errs(d: dict) -> list[str]:
    """gate 侧口径的别名（保留独立名字，防读代码时误以为 gate 走了 live=True）。"""
    return _errs(d)


def _anchor_errs(d: dict) -> list[str]:
    return check_anchors(_POLICY, d, root=_REPO)


def _cli(args: list[str]):
    """校验器 CLI 子进程（只用于验退出码/降级语义，禁在本文件里复制判据）。

    子进程 stdout/stderr 显式钉 UTF-8：Windows 下默认按 GBK 编码，中文判据行会变乱码，
    断言就废了。
    """
    cmd = [
        sys.executable,
        str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators" / "validate_construction_steps.py"),
        *args,
    ]
    return subprocess.run(
        cmd,
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )


# ---------------------------------------------------------------------------
# 绿组：判据不放宽的前提下真图必须零 error（红组证明校验器不是恒红，绿组证明不是恒绿）
# ---------------------------------------------------------------------------


def test_green_real_map_structure_zero_error():
    """真图过完整面（含磁盘实存/在册/PG 腿）——CLI 结构面绿是本图全部红案的前提。"""
    assert _live_errs(copy.deepcopy(_GOOD)) == []


def test_green_gate_face_live_off_zero_error():
    """gate 调的就是这一面（live=False）——它必须独立成立，否则 gate 会连坐拦无辜提交。"""
    assert _gate_errs(copy.deepcopy(_GOOD)) == []


def test_green_dual_axis_calibre_matches_skeleton():
    """口径面绿证：production 数==骨架 ✅ 数（不多不少）、gap=11、有码环节挂满总线号。

    gap=11：D14-G10 已按其 invalidation 条款作废（幽灵件 src/zephyr/shared/vocab
    2026-09-26 复活落仓 a2e820034bd）——契约全集 GAP_NODES 仍保留 12 槽位不收缩，
    仅提案件不再发 G10 节点（增删已先回写骨架，见 00_skeleton.md R-08 回写注记）。
    """
    skel = scan_skeleton_axes(_REPO)
    ok_ids = {k for k, v in skel.items() if v["status"] == "✅"}
    prod = {n["node_id"] for n in _GOOD["nodes"] if n.get("verified_scope") == "production"}
    assert prod == ok_ids
    assert _GOOD["counts"]["by_verified_scope"]["production"] == len(ok_ids) == 6
    assert sum(1 for n in _GOOD["nodes"] if n["node_type"] == "gap") == 11 == len(GAP_NODES)
    assert "D14-G10" not in {n["node_id"] for n in _GOOD["nodes"]}
    assert all(n.get("module_id") for n in _GOOD["nodes"] if n.get("module_ref"))
    assert all(n.get("red_reason") for n in _GOOD["nodes"] if not n.get("module_id"))
    # L0 统一名：节点字段名零旧名残留（散文里提废止名是说明，不算残留）
    for n in _GOOD["nodes"]:
        assert not (set(n) & set(V.BANNED_NODE_FIELDS)), f"旧字段名残留于 {n.get('node_id')}"


def test_green_policy_face_only_known_matrix_debt():
    """政策面唯一已知红=§2.3 矩阵缺行（提案件 matrix_gaps 已登记，属总包排产项）。

    写成"除 CV-11 外不得有别的红"而非"CV-11 必红"：总包补了矩阵行之后本用例仍绿。
    """
    assert not [e for e in _anchor_errs(copy.deepcopy(_GOOD)) if "CV-11" not in e]


def test_green_proposal_fallback_is_declared_not_silent():
    """锚块回落现态：anchor_source=proposal 且 17 环节全量进 pending_anchors ⇒ 不判红。"""
    d = copy.deepcopy(_GOOD)
    assert d["anchor_source"] == "proposal"
    assert len(d["pending_anchors"]) == len(STEP_UNIVERSE) == 17
    assert not any("pending_anchors" in e for e in _anchor_errs(d))


# ---------------------------------------------------------------------------
# 红组·结构与边轴（CV-01~04 / CV-10 / CV-13）
# ---------------------------------------------------------------------------


def test_red_missing_top_key():
    d = copy.deepcopy(_GOOD)
    d.pop("laws")
    assert any("缺顶层必填键: laws" in e for e in _errs(d))


def test_red_fabricated_node_beyond_universe():
    """RC-01 伪造环节：越出 17+12 契约全集的节点必须点名（防"图长毛"）。"""
    d = copy.deepcopy(_GOOD)
    rogue = copy.deepcopy(_find(d, "D14-06"))
    rogue["node_id"] = "D14-X99"
    d["nodes"].append(rogue)
    assert any("越出契约全集" in e and "D14-X99" in e for e in _errs(d))


def test_red_missing_contract_step_node():
    """RC-02 抽掉契约环节（漏族=静默腐坏典型形态）。"""
    d = copy.deepcopy(_GOOD)
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D14-05"]
    assert any("缺环节" in e and "D14-05" in e for e in _errs(d))


def test_red_duplicate_node_id():
    d = copy.deepcopy(_GOOD)
    d["nodes"].append(copy.deepcopy(_find(d, "D14-06")))
    assert any("node_id 存在重复" in e for e in _errs(d))


def test_red_dangling_edge():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D14-06", "D14-不存在"])
    assert any("边引用了不存在的节点" in e for e in _errs(d))


def test_red_duplicate_and_self_loop_edges():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(list(d["edges"][0]))
    d["edges"].append(["D14-10", "D14-10"])
    errs = _errs(d)
    assert any("重复边" in e for e in errs)
    assert any("自环边不得进 edges" in e for e in errs)


def test_red_order_collision():
    """order 全图唯一（主序边方向由它定，撞号=主序不可判定）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-12")["order"] = _find(d, "D14-11")["order"]
    assert any("order 全图唯一性破坏" in e for e in _errs(d))


def test_red_undeclared_reverse_edge_and_declaration_channel():
    """未声明反馈环的反向边必红；同一边显式声明进 feedback_loops+loops 台账后不红（通道有效）。"""
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D14-13", "D14-03"])
    assert any("未声明为反馈环的反向边" in e for e in _errs(d))
    d["feedback_loops"].append({"from": "D14-13", "to": "D14-03", "note": "测试声明通道"})
    d["loops"].append(
        {"loop_id": "T-TEST", "from": "D14-13", "to": "D14-03", "kind": "in_graph", "note_zh": "测试声明通道"}
    )
    assert not any("未声明为反馈环的反向边: D14-13->D14-03" in e for e in _errs(d))


def test_red_feedback_edge_creates_cycle_in_main_sequence():
    """回边成环：主序必须保持 DAG，未声明的回边把链连成环必报环路径。

    靶点选 D14-13->D14-03（主序里 03→…→13 已连通）；不能拿 B8 那条 D14-09->D14-02 当靶——
    它已在 feedback_loops 在册，校验器按契约把它从主序里摘出去，本就无环可造。
    """
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D14-13", "D14-03"])
    d["counts"]["total_edges"] = len(d["edges"])
    errs = _errs(d)
    assert any("未声明为反馈环的反向边" in e for e in errs)
    assert any("主序边成环" in e and "D14-13" in e for e in errs)
    # 对照：同一条边声明成反馈环后，环判不再误伤（回边只能由 feedback_loops 承载）
    d["feedback_loops"].append({"from": "D14-13", "to": "D14-03", "note": "测试声明通道"})
    d["loops"].append(
        {"loop_id": "T-TEST", "from": "D14-13", "to": "D14-03", "kind": "in_graph", "note_zh": "测试声明通道"}
    )
    assert not any("主序边成环" in e for e in _errs(d))


def test_red_loop_ledger_fake_door():
    """回边台账假门：feedback_loops 里删掉一条已登记的边，loops 台账仍称 in_graph ⇒ 必红。"""
    d = copy.deepcopy(_GOOD)
    d["feedback_loops"] = [f for f in d["feedback_loops"] if f.get("loop_id") != "B5"]
    assert any("假门" in e and "B5" in e for e in _errs(d))


def test_red_prose_counts():
    """RC-14 计数写进散文（骨架 R-12 的图侧防线）。"""
    text = yaml.safe_dump(copy.deepcopy(_GOOD), allow_unicode=True, sort_keys=False)
    assert check_prose_counts(text) == []  # 真图文本必须干净
    dirty = text.replace("name_zh: AI 施工升级流图", "name_zh: AI 施工升级流图 端到端 15 步")
    assert any("CV-13" in e for e in check_prose_counts(dirty))


# ---------------------------------------------------------------------------
# 红组·双轴冒充（CV-DUAL / CV-STATE，簿03 与终局卷口径）
# ---------------------------------------------------------------------------


def test_red_production_disguise_on_hammer_node():
    """谎：🔨 环节（D14-03）冒充 production → 单点谎 + 计数面（多了算谎）双双必红。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D14-03")
    node["verified_scope"] = "production"
    node["exec_evidence"] = ["复跑 python scripts/governance/dummy_probe.py 观察在产"]
    errs = _errs(d)
    assert any("谎" in e and "D14-03" in e for e in errs)
    assert any("CV-DUAL 计数" in e and "D14-03" in e for e in errs)


def test_red_production_undercount_is_debt():
    """欠：✅ 环节（D14-06）降成 structure → 必报"欠"+计数红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["verified_scope"] = "structure"
    errs = _errs(d)
    assert any("欠——骨架 ✅" in e and "D14-06" in e for e in errs)
    assert any("CV-DUAL 计数" in e for e in errs)


def test_red_production_without_exec_evidence():
    """production 却无在产证据 ⇒ 必带 exec_evidence（三证齐才许宣在产）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["exec_evidence"] = []
    assert any("必带 exec_evidence" in e and "D14-06" in e for e in _errs(d))


def test_red_exec_evidence_without_rerun_handle():
    """证据写成纯散文（无命令也无 file:line 锚）⇒ 不可复跑=判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["exec_evidence"] = ["这一环确实在产跑过"]
    assert any("无可复跑把手" in e and "D14-06" in e for e in _errs(d))


def test_red_production_confidence_mismatch():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-07")["confidence"] = "proposed"
    assert any("production 必 verified" in e and "D14-07" in e for e in _errs(d))


def test_red_anchor_claims_disagree_with_skeleton_columns():
    """CV-STATE：锚块声称的 skeleton_status 与骨架 §1 实扫列不符=判据各说各话。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-03")["skeleton_status"] = "✅"
    errs = _errs(d)
    assert any("CV-STATE" in e and "skeleton_status" in e and "D14-03" in e for e in errs)


def test_red_handoff_node_whitewashed_by_inheriting_auto():
    """反洗白：handoff 环节（D14-15）借图 11 的 auto 结论抬本图分数 ⇒ 必红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-15")["verifiability"] = "automated"
    assert any("CV-STATE" in e and "verifiability" in e and "D14-15" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·CV-BUS（module_id 总线挂载）
# ---------------------------------------------------------------------------


def test_red_module_ref_without_module_id():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["module_id"] = None
    assert any("CV-BUS" in e and "module_id 空" in e and "D14-06" in e for e in _errs(d))


def test_red_fabricated_module_id_shape():
    """自造总线号（非 MOD-* 形态）⇒ 必红：号必经在册面取，禁凭记忆。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-07")["module_id"] = "FIG14-OWNER-MADE"
    assert any("非 MOD-* 形态" in e and "D14-07" in e for e in _errs(d))


def test_red_null_module_id_without_reason():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-02")["red_reason"] = None
    assert any("必配 red_reason" in e and "D14-02" in e for e in _errs(d))


def test_red_illegal_enums_across_axes():
    """枚举非法（自造口径值）四条分别报红。"""
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D14-08")
    n["build_status"] = "almost"
    n["wiring_status"] = "half_wired"
    n["verified_scope"] = "prod"
    n["confidence"] = "certain"
    errs = _errs(d)
    for frag in ("build_status 非法", "wiring_status 非法", "verified_scope 非法", "confidence 非法"):
        assert any(frag in e for e in errs), frag


# ---------------------------------------------------------------------------
# 红组·CV-16 与锚面（automated 必带 exec_source；声称有实则没有）
# ---------------------------------------------------------------------------


def test_red_automated_without_exec_source():
    """verifiability=automated 却无 exec_source ⇒ 禁凭散文主张自动可验。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-07")["exec_source"] = None
    assert any("automated 却无 exec_source" in e and "D14-07" in e for e in _errs(d))


def test_red_exec_source_claimed_but_file_absent():
    """声称 exec_source 指向某件，件却在盘上不存在（R-01 幽灵锚原样形态）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-12")["exec_source"] = "script:scripts/no_such_tool_at_all_xyz.py"
    assert any("exec_source 声称件不存在" in e and "D14-12" in e for e in _live_errs(d))


def test_red_exec_source_claimed_gate_not_registered():
    """声称 gate: 型 exec_source 而两册均不在册 ⇒ 件不存在级 fail。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-03")["exec_source"] = "gate:NOT-A-REGISTERED-GATE"
    assert any("exec_source 声称 gate" in e and "不在册" in e for e in _live_errs(d))


def test_red_exec_source_illegal_shape():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-08")["exec_source"] = "magic:something"
    assert any("exec_source 形态非法" in e for e in _errs(d))


def test_red_built_without_evidence_and_without_date():
    """RC-16 built 却无实查证据；另一节点证据缺 YYYY-MM-DD 前缀（✅ 必附实查的机读面）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-09")["evidence"] = []
    _find(d, "D14-13")["evidence"] = ["昨天手工看过一遍"]
    errs = _errs(d)
    assert any("built 却 evidence 空" in e and "D14-09" in e for e in errs)
    assert any("YYYY-MM-DD" in e and "D14-13" in e for e in errs)


def test_red_built_without_module_ref():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["module_ref"] = None
    assert any("built 节点必须有 module_ref" in e and "D14-06" in e for e in _errs(d))


def test_red_doc_anchor_line_number_banned():
    """RC-08 行号锚（骨架 R-13 实测 7/7 全偏）⇒ 一律判红，改符号锚也不许退回去数行。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["policy_anchor"] = (
        "docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-2 L279"
    )
    assert any("禁行号锚" in e or "policy_anchor 含行号锚" in e for e in _errs(d))


def test_red_boundary_reference_broken():
    """CV-15：boundary 引用的仓内件不存在 ⇒ 边界声明不可回源即判红。"""
    d = copy.deepcopy(_GOOD)
    d["boundary"].append("不画幽灵边界——config/no_such_map_boundary_xyz.yaml 已排除")
    assert any("boundary 引用的源文件不存在" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·CV-14 handoff 边界 / CV-GAP 缺口结构 / 越域挂载 / L0 统一名
# ---------------------------------------------------------------------------


def test_red_handoff_node_swallowing_fig11_machinery():
    """RC-10 越域吞图 11：handoff 节点自带机制锚、引用不存在的 D11 环节 ⇒ 两条必红。"""
    d = copy.deepcopy(_GOOD)
    node = _find(d, "D14-15")
    node["gates"] = ["HELD-OVERLAP"]
    node["handoff_to"] = ["D11-Z99"]
    errs = _errs(d)
    assert any("handoff 节点禁登记 gates" in e for e in errs)
    assert any("handoff_to 形态非法" in e for e in errs)


def test_red_internal_node_carrying_handoff_to():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["handoff_to"] = ["D11-C01"]
    assert any("internal 节点 handoff_to 必须为空" in e for e in _errs(d))


def test_red_gap_node_orphaned_and_whitewashed():
    """gap 缺口被摘边洗成孤岛 ⇒ 必红（显性化不得只挂名不连线）。"""
    d = copy.deepcopy(_GOOD)
    d["edges"] = [e for e in d["edges"] if "D14-G01" not in e]
    d["counts"]["total_edges"] = len(d["edges"])
    assert any("gap 节点必须至少有一条边" in e and "D14-G01" in e for e in _errs(d))


def test_red_gap_node_having_module_ref():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-G01")["module_ref"] = "scripts/governance/apply_depgraph.py"
    assert any("gap 节点不得挂 module_ref" in e for e in _errs(d))


def test_red_gap_node_misdeclared_as_stage():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-G02")["node_type"] = "stage"
    assert any("契约编号为 gap 节点" in e and "D14-G02" in e for e in _errs(d))


def test_red_legacy_field_alias_residue():
    """L0 统一名回潮（note_zh→mech_note_zh、doc_refs→design_refs）⇒ 旧名残留 + 缺必填双红。"""
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D14-04")
    n["mech_note_zh"] = n.pop("note_zh")
    n["design_refs"] = n.pop("doc_refs")
    errs = _errs(d)
    assert any("字段旧名残留 mech_note_zh" in e and "D14-04" in e for e in errs)
    assert any("字段旧名残留 design_refs" in e and "D14-04" in e for e in errs)
    assert any("缺必填字段 note_zh" in e for e in errs)
    assert any("缺必填字段 doc_refs" in e for e in errs)


def test_red_cross_domain_mount():
    """越域挂载（把 TDM 的决策判据字段塞进本图节点）⇒ 必红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-09")["judgment_basis"] = ["因子A>", "情绪B<"]
    assert any("越域挂载" in e and "judgment_basis" in e for e in _errs(d))


def test_red_decision_question_and_note_overflow():
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-11")["decision_question"] = "问" * 121
    _find(d, "D14-11")["note_zh"] = "注" * 121
    errs = _errs(d)
    assert any("decision_question 超" in e for e in errs)
    assert any("note_zh 超" in e for e in errs)


def test_red_inv1_copy_of_policy_prose():
    """RC-13 INV-1 抄政策正文：把政策一行散文整段搬进节点 note_zh ⇒ 必红。

    取证不借校验器自己的语料函数（否则校验器语料判据写坏时本用例一起瞎）。
    """
    victim = None
    for line in _POLICY.split("\n"):
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "-", "*", "`")):
            continue
        compact = re.sub(r"\s+", "", s)
        if 45 <= len(compact) <= 115 and sum(1 for c in s if "\u4e00" <= c <= "\u9fff") >= 15:
            victim = s
            break
    assert victim, "政策无可抄散文行——探针前提失效"
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-12")["note_zh"] = victim
    assert any("INV-1 复制侵权" in e and "D14-12" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组·CV-13 counts 一致性（手改图不回生成）
# ---------------------------------------------------------------------------


def test_red_counts_drift_all_faces():
    d = copy.deepcopy(_GOOD)
    d["counts"]["total_nodes"] = 99
    d["counts"]["total_steps"] = 15
    d["counts"]["by_verified_scope"]["production"] = 1
    d["counts"]["by_skeleton_status"]["✅"] = 9
    errs = _errs(d)
    for frag in ("counts.total_nodes", "counts.total_steps", "counts.by_verified_scope", "counts.by_skeleton_status"):
        assert any(frag in e for e in errs), frag


# ---------------------------------------------------------------------------
# 红组·枚举词表动态加载（禁在校验器里写死字典）
# ---------------------------------------------------------------------------


def test_red_verifiability_vocabulary_is_not_hardcoded(tmp_path):
    """改词表 fixture 必须改判：造一个含自造值的新词表 ⇒ 该值合法；真仓词表下同一值必红。"""
    fake = "quantum_checkable"
    vocab = tmp_path / _VOCAB_REL
    vocab.parent.mkdir(parents=True, exist_ok=True)
    # 真仓词表值动态取用（VOCAB-HARDCODE：禁枚举词表成员字面量；fixture 面同样走真源）
    values = sorted(load_verifiability_values(_REPO, [])) + [fake]
    vocab.write_text(yaml.safe_dump({"values": [{"value": v} for v in values]}, allow_unicode=True), encoding="utf-8")
    assert load_verifiability_values(tmp_path, []) == set(values)

    d = copy.deepcopy(_GOOD)
    _find(d, "D14-02")["verifiability"] = fake
    warns: list[str] = []
    errs = validate_structure(d, root=tmp_path, warnings=warns, live=False)
    assert not any("verifiability 非法" in e for e in errs)

    d2 = copy.deepcopy(_GOOD)
    _find(d2, "D14-02")["verifiability"] = fake
    assert any("verifiability 非法" in e and "D14-02" in e for e in _gate_errs(d2))


def test_red_missing_anchor_source_and_illegal_value():
    """anchor_source 必须显式声明来源（policy=已嵌块 / proposal=回落提案件）。"""
    d = copy.deepcopy(_GOOD)
    d["anchor_source"] = "whisper"
    assert any("anchor_source 非法" in e for e in _errs(d))
    d2 = copy.deepcopy(_GOOD)
    d2.pop("anchor_source")
    assert any("anchor_source" in e for e in _errs(d2))


# ---------------------------------------------------------------------------
# 红组·政策面闭合（check_anchors：CV-04 / CV-11 / CV-GHOST / 锚块回落行为）
# ---------------------------------------------------------------------------


def test_red_fabricated_policy_step():
    """图节点声称的 policy_step 在政策 Step 段集合里查无 ⇒ 伪造环节必红（防"图长毛"）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-06")["policy_step"] = "Step 99"
    errs = _anchor_errs(d)
    assert any("伪造环节" in e and "99" in e for e in errs)
    assert any("政策有 Step 而图无节点" in e for e in errs)  # Step 2 随之失配（双向闭合）


def test_red_unmapped_step_not_declared_pending():
    """政策有 Step 而图无节点、又不在 pending_anchors ⇒ 禁"忘了就绿"。"""
    d = copy.deepcopy(_GOOD)
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D14-09"]  # Step 4 环节消失
    errs = _anchor_errs(d)
    assert any("政策有 Step 而图无节点且不在 pending_anchors" in e for e in errs)
    assert any("stage 节点数" in e for e in errs)


def test_red_proposal_source_must_list_all_debts():
    """锚块回落态行为：anchor_source=proposal 而 pending_anchors 空 ⇒ 欠账未显性化必红。"""
    d = copy.deepcopy(_GOOD)
    d["pending_anchors"] = []
    assert any("欠账必须显式列全" in e for e in _anchor_errs(d))


def test_red_policy_source_must_clear_pending():
    """政策嵌块后（未来态）pending_anchors 必须清空，残留即漂移。"""
    d = copy.deepcopy(_GOOD)
    d["anchor_source"] = "policy"
    assert any("pending_anchors 必须清空" in e for e in _anchor_errs(d))


def test_red_ghost_revived_assertion_must_be_rewritten():
    """RC/骨架 R-05 同族：gap 节点断言某件是幽灵，而该件现已在盘 ⇒ 断言作废必须回写骨架。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D14-G01")["ghost_refs"] = ["scripts/governance/apply_depgraph.py"]
    assert any("断言为幽灵的件现已在盘" in e and "D14-G01" in e for e in _anchor_errs(d))


def test_red_matrix_row_missing_is_red():
    """RC-19 关系矩阵与 Step 段闭合：fixture 政策删掉 Step 3.5 段 ⇒ CV-11 必红。"""
    fixture = _POLICY.replace("### Step 3.5 ·", "### Step 9.9 ·", 1)
    errs = check_anchors(fixture, copy.deepcopy(_GOOD), root=_REPO)
    assert any("CV-11" in e and "Step 9.9" in e for e in errs)


# ---------------------------------------------------------------------------
# 降级面：外部真源不可达只 warn，绝不升级为 error（禁环境异常打死无辜提交）
# ---------------------------------------------------------------------------


def test_downgrade_not_error_when_external_faces_absent(tmp_path):
    """骨架/图11 骨架/词表/政策四张外部件不可读 ⇒ 只降 warn，绝不升级为 error。

    tmp 根里只补 boundary 逐字回源所指的件（CV-15 那条是"引用面断链"判据、与外部真源
    可用性无关，不补就测不到"降级"这一件事本身）。
    """
    (tmp_path / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "config" / "governance_operations_map.yaml").write_text("# fixture 占位\n", encoding="utf-8")
    d = copy.deepcopy(_GOOD)
    warns: list[str] = []
    errs = validate_structure(d, root=tmp_path, warnings=warns, live=False)
    assert errs == [], errs  # 缺面不得转成 error
    assert any("骨架 §1 两列不可读" in w for w in warns)
    assert any("图11 骨架不可读" in w for w in warns)
    assert any("verifiability 受控词表不可读" in w for w in warns)
    assert not any("production 数" in e for e in errs)


def test_check_anchors_degrades_when_policy_unreadable(tmp_path):
    """政策面在 CLI 层的降级：政策不可读=降 warn 跳过，绝不因为文件不在而判图有错。"""
    r = _cli(
        [
            "--steps",
            "config/construction_workflow_map.yaml",
            "--policy",
            str(tmp_path / "no_such_policy.md"),
            "--skip-live",
        ]
    )
    assert r.returncode == 0, r.stderr
    assert "政策 MD 不可读" in r.stderr, r.stderr
    assert "ERROR:" not in r.stderr, r.stderr  # 降级只出 WARN，不得转成判红


def test_cli_exit_semantics_three_states(tmp_path):
    """RC-17 CLI 退出语义逐字照搬契约：0=PASS / 1=结构违规 / 2=文件不存在与解析类。"""
    green = _cli(
        ["--steps", "config/construction_workflow_map.yaml", "--policy", str(tmp_path / "none.md"), "--skip-live"]
    )
    assert green.returncode == 0, green.stderr

    broken = tmp_path / "broken.yaml"
    broken.write_text("schema_version: '0.1'\n  nodes: [unclosed\n", encoding="utf-8")
    assert _cli(["--steps", str(broken)]).returncode == 2
    as_list = tmp_path / "list.yaml"
    as_list.write_text("- a\n- b\n", encoding="utf-8")
    assert _cli(["--steps", str(as_list)]).returncode == 2
    assert _cli(["--steps", str(tmp_path / "nope.yaml")]).returncode == 2

    d = copy.deepcopy(_GOOD)
    d["counts"]["total_nodes"] = 3  # 手改计数=结构违规（非解析类）
    drift = tmp_path / "drift.yaml"
    drift.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")
    r = _cli(["--steps", str(drift), "--policy", str(tmp_path / "none.md"), "--skip-live"])
    assert r.returncode == 1 and "counts.total_nodes" in r.stderr


# ---------------------------------------------------------------------------
# 红组·生成器侧：非幂等=事故 + 取时禁令
# ---------------------------------------------------------------------------


def test_red_generator_is_byte_idempotent():
    import generate_construction_workflow_map as gen

    doc = gen.build_document(as_of="2026-09-25T12:00:00+08:00", root=_REPO)
    h = [hashlib.sha256(gen.serialize_document(doc).encode("utf-8")).hexdigest() for _ in range(2)]
    assert h[0] == h[1], "生成器同输入两次产出不逐字节等=非幂等事故"
    # 同 as_of 重建一次（防"读内存对象"掩盖真非幂等）
    doc2 = gen.build_document(as_of="2026-09-25T12:00:00+08:00", root=_REPO)
    assert hashlib.sha256(gen.serialize_document(doc2).encode("utf-8")).hexdigest() == h[0]


def test_red_generator_free_of_wall_clock():
    """RULE-SCHEMA-TZ：生成器禁 datetime.now()/time.time()——时间戳必经入参或 HEAD 派生。"""
    src = (
        _REPO / "scripts" / "governance" / "d5_architecture" / "generators" / "generate_construction_workflow_map.py"
    ).read_text(encoding="utf-8")
    assert not re.search(r"datetime\.now\(\)", src), "生成器出现 datetime.now()（违反取时禁令）"
    assert not re.search(r"time\.time\(\)", src), "生成器出现 time.time()（违反取时禁令）"


def test_universe_contract_covers_17_steps_and_11_gaps():
    """契约面自检：17 Step 段 + 11 gap=28——改契约必先回写骨架，此断言挡静默漂移。

    11 gap：D14-G10 已依其 invalidation 条款作废（幽灵件复活，2026-10-02 回写骨架+裁定
    CR-15 在案），契约全集同步收缩；槽位号不回收复用。
    """
    assert len(STEP_UNIVERSE) == 17 and len(GAP_NODES) == 11
    assert "D14-G10" not in GAP_NODES
    assert STEP_UNIVERSE[0] == "D14-01" and STEP_UNIVERSE[-1] == "D14-17"
    assert len(V.NODE_UNIVERSE) == 28


def test_module_translation_and_vocab_sources_present():
    """依赖面探针：verifiability 词表与骨架两张外部件必须在盘（缺了=对应腿降级，须可见）。"""
    assert (_REPO / _VOCAB_REL).exists()
    assert (_REPO / "docs/_working/map_build/fig14_construction/00_skeleton.md").exists()
    # 词表非空且足以承载三档以上生产口径（成员值动态加载，禁字面量枚举）
    assert len(load_verifiability_values(_REPO, [])) >= 3


if __name__ == "__main__":  # pragma: no cover  直跑=冒烟（pytest 才是正式入口）
    sys.exit(pytest.main([__file__, "-q"]))
