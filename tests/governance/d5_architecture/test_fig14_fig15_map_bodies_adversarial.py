# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §fig14_fig15_map_bodies
# [MODULE] tests.governance.d5_architecture.test_fig14_fig15_map_bodies_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; copy;
# [CONSUMERS] 图14/图15 图本体 yaml 与 card_state_vocabulary.yaml 的结构自含质量守卫（夜战 SW13 车道）；
#   不依赖 chief7 在飞 validator/generator——本件是纯结构判据（引用完整性/派生计数/闭集枚举/
#   封卡即终），与 tests/governance/d5_architecture/test_*_map_adversarial.py（校验器质量守卫族）
#   互补不重叠
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部 mutant 构造于 tmp_path 内存副本（不碰生产路径）；好图控制组=真实图必须零违例；
#   每个红用例断言"判据必须报出这一条具体语义"（按 marker 前缀匹配），不只看非空
# [MODIFY-GUARD] 本件是"结构判据能红"的证据面：删用例或放宽断言=放水；收紧判据必同步新增能红用例
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图14/图15 图本体结构对抗测试——红优先：每种坏图必须被点名，好图必须全绿。

判据面（自含，不依赖 chief7 在飞件）：
- 图14：node_id 唯一 / 边与反馈环端点封闭（悬空必红）/ node_type 闭集 / counts 与 by_* 派生计数一致
- 图15：状态值 ∈ card_state_vocabulary（跨文件闭集）/ 迁移端点封闭 / 非 cross_instance 迁移禁出终态
  （封卡即终，M17 复活边以 cross_instance=True 走新卡）/ 禁边 pattern_kind 闭集且 state_pair 型端点
  封闭 / card_ledger 状态闭集 + revives 指针不悬空 / registered_by_state 与台账实数一致
- 词表：total_values 与实数一致 / 值集与图15 状态 1:1

红蓝四向量：杀节点 / 断边 / 伪造计数 / 坏枚举（+封卡就地复活加验）。
mutant 全部经 tmp_path 副本注入，生产文件只读。
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
FIG14 = _REPO / "config" / "construction_workflow_map.yaml"
FIG15 = _REPO / "config" / "strategy_card_lifecycle_map.yaml"
VOCAB = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "card_state_vocabulary.yaml"

_NODE_TYPES = {"stage", "gap"}
_FORBIDDEN_PATTERN_KINDS = {
    "state_pair",
    "self_pair",
    "cross_cutting",
    "copy_guard",
    "credential_guard",
    "revival_guard",
}


# ---------------------------------------------------------------------------
# 判据函数（返回违例清单；每条带 marker 供红案点名断言）
# ---------------------------------------------------------------------------
def check_fig14(d: dict) -> list[str]:
    bad: list[str] = []
    nodes = d.get("nodes") or []
    ids = [n.get("node_id") for n in nodes]
    id_set = set(ids)
    if len(ids) != len(id_set):
        bad.append("FIG14-DUP-NODE-ID")
    for e in d.get("edges") or []:
        for end in e:
            if end not in id_set:
                bad.append(f"FIG14-DANGLING-EDGE:{e}")
                break
    for fb in d.get("feedback_loops") or []:
        if fb.get("from") not in id_set or fb.get("to") not in id_set:
            bad.append(f"FIG14-DANGLING-FEEDBACK:{fb.get('loop_id')}")
    for n in nodes:
        if n.get("node_type") not in _NODE_TYPES:
            bad.append(f"FIG14-BAD-NODE-TYPE:{n.get('node_id')}")
    c = d.get("counts") or {}
    stages = sum(1 for n in nodes if n.get("node_type") == "stage")
    gaps = sum(1 for n in nodes if n.get("node_type") == "gap")
    expect = {
        "total_nodes": len(nodes),
        "total_edges": len(d.get("edges") or []),
        "total_feedback": len(d.get("feedback_loops") or []),
        "total_steps": stages,
        "total_gaps": gaps,
    }
    for k, v in expect.items():
        if c.get(k) != v:
            bad.append(f"FIG14-COUNT-MISMATCH:{k}")
    if c.get("by_node_type") != dict(_count_by(nodes, "node_type")):
        bad.append("FIG14-COUNT-MISMATCH:by_node_type")
    if c.get("by_segment") != dict(_count_by(nodes, "segment")):
        bad.append("FIG14-COUNT-MISMATCH:by_segment")
    return bad


def _count_by(rows: list, key: str) -> dict:
    out: dict = {}
    for r in rows:
        k = r.get(key)
        out[k] = out.get(k, 0) + 1
    return out


def check_vocab(d: dict) -> list[str]:
    bad: list[str] = []
    values = [v.get("value") for v in d.get("values") or []]
    if len(values) != len(set(values)):
        bad.append("VOCAB-DUP-VALUE")
    if (d.get("total_values") is not None) and d["total_values"] != len(values):
        bad.append("VOCAB-COUNT-MISMATCH:total_values")
    return bad


def check_fig15(d: dict, vocab_values: set[str]) -> list[str]:
    bad: list[str] = []
    states = d.get("states") or []
    state_vals = [s.get("value") for s in states]
    state_set = set(state_vals)  # 图自身状态集（内部闭包轴）；vocab_values 是枚举闭集轴，两轴并用
    if len(state_vals) != len(set(state_vals)):
        bad.append("FIG15-DUP-STATE-VALUE")
    outside = [v for v in state_vals if v not in vocab_values]
    if outside:
        bad.append(f"FIG15-STATE-OUTSIDE-VOCAB:{sorted(outside)}")
    terminal = {s.get("value") for s in states if s.get("terminal")}

    def _ends(v):
        return v if isinstance(v, list) else [v]

    for t in d.get("transitions") or []:
        if t.get("edge_kind") != "permitted":
            bad.append(f"FIG15-BAD-TRANSITION-KIND:{t.get('transition_id')}")
        srcs = [x for x in _ends(t.get("from_state")) if x is not None]
        unknown_src = [x for x in srcs if x not in state_set]
        if unknown_src:
            bad.append(f"FIG15-TRANSITION-DANGLING-FROM:{t.get('transition_id')}")
        if t.get("to_state") not in state_set:
            bad.append(f"FIG15-TRANSITION-DANGLING-TO:{t.get('transition_id')}")
        # 封卡即终：非 cross_instance 迁移禁出终态（M17 复活边 cross_instance=True 走新卡）
        if srcs and set(srcs) & terminal and not t.get("cross_instance"):
            bad.append(f"FIG15-TERMINAL-REVIVE-INPLACE:{t.get('transition_id')}")
    for f in d.get("forbidden_edges") or []:
        if f.get("edge_kind") != "forbidden":
            bad.append(f"FIG15-BAD-FORBIDDEN-KIND:{f.get('edge_id')}")
        pk = f.get("pattern_kind")
        if pk not in _FORBIDDEN_PATTERN_KINDS:
            bad.append(f"FIG15-BAD-PATTERN-KIND:{f.get('edge_id')}")
            continue
        if pk in {"state_pair", "self_pair"}:
            bad_ends = [x for x in _ends(f.get("from_state")) + [f.get("to_state")] if x not in state_set]
            if bad_ends:
                bad.append(f"FIG15-FORBIDDEN-DANGLING:{f.get('edge_id')}")
    c = d.get("counts") or {}
    term_n = sum(1 for s in states if s.get("terminal"))
    expect = {
        "total_states": len(states),
        "total_transitions": len(d.get("transitions") or []),
        "total_forbidden_edges": len(d.get("forbidden_edges") or []),
        "terminal_states": term_n,
        "total_gaps": len(d.get("gaps") or []),
    }
    for k, v in expect.items():
        if c.get(k) != v:
            bad.append(f"FIG15-COUNT-MISMATCH:{k}")
    ledger = d.get("card_ledger") or []
    card_ids = {e.get("card_id") for e in ledger}
    for e in ledger:
        if e.get("card_state") not in vocab_values:
            bad.append(f"FIG15-LEDGER-BAD-STATE:{e.get('card_id')}")
        if e.get("revives") and e.get("revives") not in card_ids:
            bad.append(f"FIG15-LEDGER-DANGLING-REVIVES:{e.get('card_id')}")
    if c.get("registered_by_state") != _count_by(ledger, "card_state"):
        bad.append("FIG15-COUNT-MISMATCH:registered_by_state")
    if c.get("registered_entries_in_ledger") is not None and c["registered_entries_in_ledger"] != len(ledger):
        bad.append("FIG15-COUNT-MISMATCH:registered_entries_in_ledger")
    return bad


def check_vocab_matches_fig15(vocab_d: dict, fig15_d: dict) -> list[str]:
    values = {v.get("value") for v in vocab_d.get("values") or []}
    state_vals = {s.get("value") for s in fig15_d.get("states") or []}
    if values != state_vals:
        bad = sorted(values ^ state_vals)
        return [f"VOCAB-FIG15-NOT-1TO1:{bad}"]
    return []


# ---------------------------------------------------------------------------
# 绿组：真实图必须零违例
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def real():
    return {
        "fig14": yaml.safe_load(FIG14.read_text(encoding="utf-8")),
        "fig15": yaml.safe_load(FIG15.read_text(encoding="utf-8")),
        "vocab": yaml.safe_load(VOCAB.read_text(encoding="utf-8")),
    }


def _dump(tmp_path: Path, name: str, d) -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return p


def test_real_fig14_green(real):
    assert check_fig14(real["fig14"]) == []


def test_real_fig15_green(real):
    vocab_values = {v["value"] for v in real["vocab"]["values"]}
    assert check_fig15(real["fig15"], vocab_values) == []


def test_real_vocab_green(real):
    assert check_vocab(real["vocab"]) == []
    assert check_vocab_matches_fig15(real["vocab"], real["fig15"]) == []


# ---------------------------------------------------------------------------
# 红组·图14：杀节点 / 断边 / 伪造计数 / 坏枚举
# ---------------------------------------------------------------------------
def test_fig14_kill_node_dangling_edge_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    victim = d["nodes"][0]["node_id"]
    assert any(victim in e for e in d["edges"]), "victim 节点必须有关联边，否则用例无效"
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != victim]
    d["counts"]["total_nodes"] = len(d["nodes"])  # 计数同步改对，隔离出悬空边单一语义
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert any(b.startswith("FIG14-DANGLING-EDGE") for b in bad), bad


def test_fig14_broken_edge_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    d["edges"].append(["D14-01", "D14-NO-SUCH-NODE"])
    d["counts"]["total_edges"] = len(d["edges"])
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert any(b.startswith("FIG14-DANGLING-EDGE") for b in bad), bad


def test_fig14_fake_count_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    d["counts"]["total_nodes"] += 1  # 伪造计数
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert "FIG14-COUNT-MISMATCH:total_nodes" in bad, bad


def test_fig14_fake_derived_count_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    key = next(iter(d["counts"]["by_node_type"]))
    d["counts"]["by_node_type"][key] += 1
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert "FIG14-COUNT-MISMATCH:by_node_type" in bad, bad


def test_fig14_bad_enum_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    d["nodes"][0]["node_type"] = "super_stage"  # 闭集外枚举
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert any(b.startswith("FIG14-BAD-NODE-TYPE") for b in bad), bad


def test_fig14_dup_node_id_red(real, tmp_path):
    d = copy.deepcopy(real["fig14"])
    d["nodes"].append(copy.deepcopy(d["nodes"][0]))
    d["counts"]["total_nodes"] = len(d["nodes"])
    bad = check_fig14(yaml.safe_load(_dump(tmp_path, "f14.yaml", d).read_text(encoding="utf-8")))
    assert "FIG14-DUP-NODE-ID" in bad, bad


# ---------------------------------------------------------------------------
# 红组·图15+词表：坏枚举 / 杀状态（断边）/ 伪造计数 / 就地复活
# ---------------------------------------------------------------------------
def test_fig15_bad_enum_state_outside_vocab_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["states"][0]["value"] = "super_green"  # 词表外状态
    vocab = copy.deepcopy(real["vocab"])
    bad = check_fig15(
        yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")),
        {v["value"] for v in vocab["values"]},
    )
    assert any(b.startswith("FIG15-STATE-OUTSIDE-VOCAB") for b in bad), bad


def test_fig15_ledger_bad_enum_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["card_ledger"][0]["card_state"] = "half_green"
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert any(b.startswith("FIG15-LEDGER-BAD-STATE") for b in bad), bad


def test_fig15_kill_state_dangling_transition_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    victim_value = d["states"][-1]["value"]
    still_ref = any(
        victim_value in (t["from_state"] if isinstance(t["from_state"], list) else [t["from_state"]])
        or t["to_state"] == victim_value
        for t in d["transitions"] + d["forbidden_edges"]
    )
    assert still_ref, "victim 状态必须被边引用，否则用例无效"
    d["states"] = d["states"][:-1]
    d["counts"]["total_states"] = len(d["states"])
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert any("DANGLING" in b for b in bad), bad


def test_fig15_fake_count_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["counts"]["total_transitions"] += 1
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert "FIG15-COUNT-MISMATCH:total_transitions" in bad, bad


def test_fig15_fake_ledger_count_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["counts"]["registered_entries_in_ledger"] += 1
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert "FIG15-COUNT-MISMATCH:registered_entries_in_ledger" in bad, bad


def test_fig15_sealed_inplace_revive_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["transitions"].append(
        {
            "transition_id": "D15-MXX",
            "edge_kind": "permitted",
            "from_state": "sealed",
            "to_state": "executing",
            "cross_instance": False,  # 就地复活：无 cross_instance
        }
    )
    d["counts"]["total_transitions"] = len(d["transitions"])
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert any(b.startswith("FIG15-TERMINAL-REVIVE-INPLACE") for b in bad), bad


def test_fig15_dangling_revives_pointer_red(real, tmp_path):
    d = copy.deepcopy(real["fig15"])
    d["card_ledger"][0]["revives"] = "NO-SUCH-CARD"
    vocab = {v["value"] for v in real["vocab"]["values"]}
    bad = check_fig15(yaml.safe_load(_dump(tmp_path, "f15.yaml", d).read_text(encoding="utf-8")), vocab)
    assert any(b.startswith("FIG15-LEDGER-DANGLING-REVIVES") for b in bad), bad


def test_vocab_bad_enum_red(real, tmp_path):
    v = copy.deepcopy(real["vocab"])
    v["values"][0]["value"] = "※非法值※"
    d15 = copy.deepcopy(real["fig15"])
    bad = check_vocab(yaml.safe_load(_dump(tmp_path, "v.yaml", v).read_text(encoding="utf-8")))
    bad += check_vocab_matches_fig15(yaml.safe_load(_dump(tmp_path, "v.yaml", v).read_text(encoding="utf-8")), d15)
    assert any(b.startswith("VOCAB-FIG15-NOT-1TO1") for b in bad), bad


def test_vocab_fake_count_red(real, tmp_path):
    v = copy.deepcopy(real["vocab"])
    v["total_values"] += 5
    bad = check_vocab(yaml.safe_load(_dump(tmp_path, "v.yaml", v).read_text(encoding="utf-8")))
    assert "VOCAB-COUNT-MISMATCH:total_values" in bad, bad
