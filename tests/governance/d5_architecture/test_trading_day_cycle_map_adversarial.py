# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §trading_day_cycle_map
# [MODULE] tests.governance.d5_architecture.test_trading_day_cycle_map_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] none（只读校验/生成器，无状态写盘）
# [DEPENDENCIES] pytest; yaml; hashlib; re; pathlib;
#   scripts.governance.d5_architecture.validators.validate_trading_day_cycle_map;
#   scripts.governance.d5_architecture.generators.generate_trading_day_cycle_map
# [CONSUMERS] 图 13 校验器质量守卫（坏图必须被拦——判通过的校验器必须先证明自己会红）；
#   图 13 生成器幂等实证与取时禁令守卫
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于内存副本（不碰生产路径、不写 config/）；好图控制组=真实图必须
#   通过；每个红用例断言"校验器必须报出这一条"（错误语义逐条钉死，不只看非空）；
#   本图三条特有校验各 ≥2 例（伪造 slot_source 在册不存在 / 节点夹带 judgment_basis 越域 /
#   dloop_stage 不在 PHASE_STAGES）；三层字段裁定新增判据各 ≥1 例可红（CV-L0/CV-BUS/CV-DUAL/
#   CV-GAP/CV-DANGLE/CV-TDM/CV-ADMIT），且外部面不可达只降 warn 不升 error 亦有用例；
#   形态照抄 test_dev_delivery_map_adversarial（图 11 姊妹图，本役已定稿范式）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图 13 交易日循环全景图校验器对抗测试——红优先：每种坏图必须被点名报出，好图必须通过。

覆盖红案（逐条对应校验器判据）：
本图特有——伪造 slot_source 指向不存在槽（schedule/schtasks/entity 三路）/ 节点夹带 judgment_basis
等判据字段越域挂载（含嵌套键规避形态）/ dloop_stage 名不在 PHASE_STAGES 实扫集合 / 四段段归属
缺失·非法·与编号不符 / 无槽环节夹带有槽指针 / downstream_action 混判"看着"与"动手" /
落空对象与空转槽台账两侧互相放水 / dloop 段序契约（PHASE_STAGES vs dispatch）漂移 /
cron 字面量进图（让渡一特化）/ INV-1 复制侵权（排班两册 + 门禁册正文抄进节点）/
三层字段裁定新判据——CV-L0 旧名残留（mech_note_zh/clock_semantics_zh/beat_zh/miss_fallback_zh/
ready_gate_zh/design_refs/dangling_refs）/ CV-BUS（module_ref 非空而 module_id 空、自造号形态、
号与在册面归属不符、空挂总线、null 不写 red_reason）/ CV-DUAL（🔨 环节冒充 production 的谎、
✅ 环节降级为欠、production 无 exec_evidence、exec 纯散文无复跑把手、production×proposed 混搭、
by_verified_scope 计数漂移）/ CV-GAP（gap 节点孤岛、洗成 stage、red_reason 枚举外）/
CV-DANGLE（台账对象无节点认领、节点引台账外对象）/ CV-TDM（伪造 tdm_ref 幽灵交叉引用）/
CV-ADMIT（声明而无边=假门、门无出边=空门）/ 通用结构类（断边/自环/重复边/未声明反向边/缺环节/
越界节点/node_id 重复/counts 漂移/缺顶层键/laws 空置/路径锚不存在/超长）/
生成器幂等与取时禁令、计划任务面只查不写；绿组另钉口径面：production 数==骨架 ✅ 数（14）、
gap 节点=4、有码环节全挂 module_id、D13-09 已升为一等门节点带拒准入出边、表A 七条与表C 五条
逐条可查、跨图缺口（图12 侧 5+1）归属分派清楚。
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
    "SUBJECT-RETIRED: config/trading_day_cycle_map.yaml retired in 531ac17ef7; validator "
    "validate_trading_day_cycle_map never committed (git log --all empty). Adversarial guard "
    "retires with its subject (chief final-verify disposal 2026-09-28).",
    allow_module_level=True,
)

_REPO = Path(__file__).resolve().parents[3]
_VALIDATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "validators"
_GENERATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "generators"
sys.path.insert(0, str(_VALIDATORS_DIR))
sys.path.insert(0, str(_GENERATORS_DIR))

from validate_trading_day_cycle_map import (  # noqa: E402
    CONTRACT_UNIVERSE,
    GAP_NODES,
    NODE_UNIVERSE,
    scan_skeleton_status,
    validate_structure,
)

_MAP_REL = "config/trading_day_cycle_map.yaml"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))


def _find(d: dict, node_id: str) -> dict:
    return next(n for n in d["nodes"] if n["node_id"] == node_id)


def _errs(d: dict) -> list[str]:
    return validate_structure(d, root=_REPO)


# ---------------------------------------------------------------------------
# 绿组：判据不放宽的前提下，真图必须零 error（证明红组不是恒红）
# ---------------------------------------------------------------------------


def test_green_real_map_passes():
    assert _errs(copy.deepcopy(_GOOD)) == []


def test_green_map_shape_matches_contract():
    """44 环节 + 4 gap 全建；四段分布=骨架 §2（12/12/11/9）+ gap 显式声明段归属。"""
    c = _GOOD["counts"]
    assert c["total_nodes"] == len(CONTRACT_UNIVERSE) == 48
    assert c["by_segment"] == {"A": 13, "B": 14, "C": 12, "D": 9}
    assert c["by_node_type"] == {"gap": 4, "stage": 44}


def test_green_three_hard_lets_go_into_laws():
    """骨架 §0.2 三条硬让渡必须落成 laws/boundary（撞车判定的边界=图本体边界）。"""
    blob = "\n".join(_GOOD["laws"] + _GOOD["boundary"])
    assert "时刻值不搬家" in blob and "决策内容不进图" in blob and "管线内部结构不重画" in blob


def test_green_dual_axis_matches_skeleton_counts():
    """口径面（六图终局卷 §5 判据 3）：production 数 **等于** 骨架 §2 ✅ 数，不多不少。"""
    sk = scan_skeleton_status(_REPO)
    ok = {nid for nid, sym in sk.items() if sym == "✅"}
    prod = {n["node_id"] for n in _GOOD["nodes"] if n.get("verified_scope") == "production"}
    assert sk and len(ok) == 14, f"骨架实扫 ✅ 数漂移：{len(ok)}"
    assert prod == ok, f"production 集与骨架 ✅ 集不重合：多={prod - ok} 少={ok - prod}"
    assert _GOOD["counts"]["by_verified_scope"] == {"production": 14, "structure": 34}


def test_green_all_code_backed_nodes_carry_module_id():
    """总线面（§5 判据 2）：module_ref 非空者 100% 挂在册 MOD-*；null 者 100% 配 red_reason。"""
    with_ref = [n for n in _GOOD["nodes"] if n.get("module_ref")]
    assert all(n.get("module_id") for n in with_ref)
    assert all(str(n["module_id"]).startswith("MOD-") for n in with_ref)
    for n in _GOOD["nodes"]:
        if not n.get("module_id"):
            assert n.get("red_reason"), f"{n['node_id']}：module_id 空而未写 red_reason"


def test_green_no_ready_gate_node_is_first_class_gate_with_admission_edges():
    """必做 4：D13-09 升为一等节点——stage + ready_gate:true + red_reason:unwired + 拒准入出边。"""
    n = _find(_GOOD, "D13-09")
    assert n["node_type"] == "stage" and n["ready_gate"] is True
    assert n["red_reason"] == "unwired" and n["wiring_status"] == "unwired_no_caller"
    assert n["module_ref"] is None and n["module_id"] is None
    assert n["admission_denied_zh"]
    outs = {(a["from"], a["to"]) for a in _GOOD["admission_edges"] if a["from"] == "D13-09"}
    assert {("D13-09", "D13-12"), ("D13-09", "D13-15")} <= outs
    edges = {tuple(e) for e in _GOOD["edges"]}
    assert outs <= edges, "声明的拒准入边必须真实存在于 edges"


def test_green_table_a_landed_and_table_c_left_to_owner():
    """必做 5：表A 七条逐条落字段/gap 节点；表C 五条判据分歧一律未自改口径、以 gap_refs 留裁。"""
    land = {b["id"]: b["nodes"] for b in _GOOD["machine_facts"]["external_benchmark_landing"]["table_a_landed"]}
    assert set(land) == {"A1", "A2", "A3", "A4", "A5", "A6", "A7"}
    n24, n28, n27 = _find(_GOOD, "D13-24"), _find(_GOOD, "D13-28"), _find(_GOOD, "D13-27")
    assert n28["ready_basis"] == "assumed"  # A5
    assert n27["no_drift_evidence"] is False  # A7
    assert _find(_GOOD, "D13-14").get("freshness_severity_zh")  # A2
    assert _find(_GOOD, "D13-13")["expected_emits_per_trading_day"] == 1  # A4
    assert _find(_GOOD, "D13-01")["miss_policy"] == "rerun"  # A6
    assert "D13-G01" in land["A3"]  # A3 → gap 节点
    pend = {b["id"] for b in _GOOD["machine_facts"]["external_benchmark_landing"]["table_c_pending"]}
    assert pend == {"C1", "C2", "C3", "C4", "C5"}
    assert any("C2" in x for x in _find(_GOOD, "D13-09")["gap_refs"]), "表C 分歧须落 gap_refs 留裁"
    assert _find(_GOOD, "D13-43")["slot_source"] == "event"  # C5 未改守卫名单口径


def test_green_cross_map_gap_inventory_splits_fig12_owned_items():
    """必做 6：图12 侧「5 处消费方在等未产表 + 1 幽灵引用」归属分派——涉及本图的挂环节/gap 节点，
    归属图 12 的三条只交叉引用不建其节点。"""
    inv = _GOOD["machine_facts"]["cross_map_gap_inventory"]
    in_map = {x["artifact"] for x in inv["in_this_map"]}
    fig12 = {x["artifact"] for x in inv["owned_by_fig12"]}
    assert len(in_map) == 3 and len(fig12) == 3 and not (in_map & fig12)
    d12_nodes = {n["node_id"] for n in _GOOD["nodes"]}
    assert not any(str(x).startswith("D12-") for x in d12_nodes), "不得抢建图 12 的节点"
    for item in inv["in_this_map"]:
        assert item["gap_node"] in d12_nodes
        assert _find(_GOOD, item["gap_node"])["red_reason"] == item["red_reason"]


# ---------------------------------------------------------------------------
# 红组 A：本图特有校验①——四段枚举合法且必填
# ---------------------------------------------------------------------------


def test_red_segment_missing():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-05").pop("segment")
    assert any("D13-05" in e and "四段段归属必填" in e for e in _errs(d))


def test_red_segment_illegal_value():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-05")["segment"] = "E"
    assert any("四段段归属必填" in e for e in _errs(d))


def test_red_segment_conflicts_with_node_index():
    """段归属与环节编号落段不符（把盘前环节挪到盘中段）→ 必须报编号落段冲突。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-02")["segment"] = "B"
    assert any("D13-02" in e and "落段" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 B：本图特有校验②——slot_source 必填 + 在册实存（防"文档说有实则无"）
# ---------------------------------------------------------------------------


def test_red_slot_source_missing():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-14").pop("slot_source")
    assert any("D13-14" in e and "slot_source 必填" in e for e in _errs(d))


def test_red_slot_source_out_of_vocabulary():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-14")["slot_source"] = "cron_table"
    assert any("值域" in e for e in _errs(d))


def test_red_fake_schedule_slot_not_in_truth_source():
    """伪造 schedule 槽：slot_refs 指向 schedule.yaml 不存在的槽名 → 必须报在册实存失败。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-14")["slot_refs"] = ["ghost_slot_never_declared"]
    errs = _errs(d)
    assert any("伪造 slot_source" in e and "ghost_slot_never_declared" in e for e in errs), errs


def test_red_schedule_source_without_slot_ref():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-30")["slot_refs"] = []
    assert any("slot_refs 为空" in e for e in _errs(d))


def test_red_fake_schtasks_ref_not_registered():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-07")["schtasks_refs"] = ["ZephyrAlpha_NeverRegisteredWatchdog"]
    errs = _errs(d)
    assert any("伪造 slot_source" in e and "ZephyrAlpha_NeverRegisteredWatchdog" in e for e in errs), errs


def test_red_schtasks_source_without_ref():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-19")["schtasks_refs"] = []
    assert any("schtasks_refs 为空" in e for e in _errs(d))


def test_red_unscheduled_node_claims_slot():
    """无槽环节（slot_source=none）夹带槽指针 = 绕开在册实存判定 → 判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-31")["slot_refs"] = ["daily_kline"]
    assert any("夹带 schedule/schtasks/dloop_stage 指针" in e for e in _errs(d))


def test_red_fake_entity_ref_not_in_registry():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-07")["entity_refs"] = ["ops_qmt_watchdog", "ops_entity_never_registered"]
    errs = _errs(d)
    assert any("伪造 entity_ref" in e and "ops_entity_never_registered" in e for e in errs), errs


def test_red_registry_unknown_refs_ledger_must_be_empty():
    d = copy.deepcopy(_GOOD)
    d["machine_facts"]["trigger_surfaces"]["registry_entities"]["unknown_refs"] = ["ops_ghost"]
    assert any("在册实存失败" in e and "ops_ghost" in e for e in _errs(d))


def test_red_fake_tdm_ref_is_ghost_cross_reference():
    """CV-TDM：tdm_refs 挂一个 TDM 在册外的节点号 = 幽灵交叉引用（引用不查=第二真源的入口）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-32")["tdm_refs"] = ["TDM-E-L0-03", "TDM-ZZ-GHOST-99"]
    errs = _errs(d)
    assert any("伪造 tdm_ref" in e and "TDM-ZZ-GHOST-99" in e for e in errs), errs


# ---------------------------------------------------------------------------
# 红组 C：本图特有校验③——跨图边界（判据归 TDM，时序归本图）
# ---------------------------------------------------------------------------


def test_red_judgment_basis_field_is_cross_domain_mount():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-34")["judgment_basis"] = "close_verify 命中率 > 0.6 才拍板"
    errs = _errs(d)
    assert any("越域挂载" in e and "judgment_basis" in e for e in errs), errs


def test_red_strategy_and_factor_refs_also_banned():
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D13-21")
    n["strategy_refs"] = ["STR-xx"]
    n["factor_refs"] = ["FCT-xx"]
    errs = _errs(d)
    assert any("strategy_refs" in e and "越域挂载" in e for e in errs)
    assert any("factor_refs" in e and "越域挂载" in e for e in errs)


def test_red_banned_key_hidden_in_nested_field_blocks():
    """禁则一的第三形态：判据字段藏进节点嵌套子块 → 递归键扫描照样判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-34")["mech_extra"] = {"judgment_basis": "资金流连续三日净流入且 IC>0.05"}
    assert any("越域挂载" in e and "judgment_basis" in e for e in _errs(d))


def test_green_tdm_refs_is_the_only_exit_for_judgment():
    """对照：判据的合法出路是 tdm_refs 引用（引用不复制），在册号不得判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-32")["tdm_refs"] = ["TDM-E-L0-03"]
    assert not any("越域" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 D：本图特有校验④——dloop_stage 须落在 PHASE_STAGES 实扫集合
# ---------------------------------------------------------------------------


def test_red_dloop_stage_forged_name():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-23")["dloop_stages"] = ["sentiment_loop_bogus"]
    errs = _errs(d)
    assert any("PHASE_STAGES" in e and "sentiment_loop_bogus" in e for e in errs), errs


def test_red_dloop_stage_extra_unregistered_member():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-33")["dloop_stages"] = ["close_verify", "settle", "midday_settle"]
    errs = _errs(d)
    assert any("midday_settle" in e for e in errs)
    assert not any("close_verify" in e and "PHASE_STAGES" in e for e in errs)


def test_red_dloop_source_without_stages():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-34")["dloop_stages"] = []
    assert any("dloop_stages 为空" in e for e in _errs(d))


def test_green_dloop_phase_dispatch_tables_are_in_sync():
    dl = _GOOD["machine_facts"]["trigger_surfaces"]["dloop_phases"]
    assert dl["dispatch_stages"] and dl["sync_outliers"] == []


def test_red_dloop_phase_dispatch_drift_is_reported():
    d = copy.deepcopy(_GOOD)
    d["machine_facts"]["trigger_surfaces"]["dloop_phases"]["sync_outliers"] = ["phantom_stage"]
    assert any("段序契约破损" in e and "phantom_stage" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 E：三层字段裁定一 CV-L0——废止别名残留即红
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "legacy,canonical",
    [
        ("mech_note_zh", "note_zh"),
        ("clock_semantics_zh", "note_zh"),
        ("semantics_zh", "note_zh"),
        ("beat_zh", "cadence_zh"),
        ("miss_fallback_zh", "fallback"),
        ("degradation", "fallback"),
        ("silent_failover", "fallback"),
        ("ready_gate_zh", "ready_gate"),
        ("design_refs", "doc_refs"),
        ("doc_ref", "doc_refs"),
        ("dangling_refs", "gap_refs"),
    ],
)
def test_red_legacy_field_name_residue(legacy, canonical):
    """CV-L0：同义异名十一废止别名逐一注入，必须逐个报"旧名残留 + 统一名应为"。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-05")[legacy] = "旧名内容"
    errs = _errs(d)
    assert any(legacy in e and "旧名残留" in e and canonical in e for e in errs), (legacy, errs[:3])


def test_red_real_map_has_zero_legacy_field_names():
    """控制组：真图全文零旧名（否则上一条参数化用例无判别力）。"""
    blob = (_REPO / _MAP_REL).read_text(encoding="utf-8")
    for legacy in (
        "mech_note_zh",
        "clock_semantics_zh",
        "beat_zh",
        "miss_fallback_zh",
        "ready_gate_zh",
        "design_refs",
        "dangling_refs",
        "semantics_zh",
    ):
        assert legacy not in blob, legacy


def test_red_cadence_zh_must_be_declared_observed_map():
    """L1 统一名 cadence_zh 在图13 用 declared/observed 双子键（写成字符串即红）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-23")["cadence_zh"] = "每日 1 拍"
    assert any("cadence_zh" in e and "declared" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 F：CV-BUS——module_id 必挂、来源唯一、禁自造
# ---------------------------------------------------------------------------


def test_red_module_ref_without_module_id():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-28")["module_id"] = None
    assert any("CV-BUS" in e and "D13-28" in e for e in _errs(d))


def test_red_fabricated_module_id_shape():
    """自造号（非 MOD-* 形态）判红——总线号只能来自 depgraph 在册投影。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-28")["module_id"] = "TRADING-003"
    assert any("非 MOD-* 形态" in e for e in _errs(d))


def test_red_module_id_not_in_roster():
    """形态合法而号不在册（MOD-GHOST-999）同样判红——在册面是判据，不是前缀游戏。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-28")["module_id"] = "MOD-GHOST-999"
    errs = _errs(d)
    assert any("不在 depgraph 在册投影面" in e and "MOD-GHOST-999" in e for e in errs), errs[:4]


def test_red_module_id_mismatch_with_roster_ownership():
    """挂了在册存在、但与该实现路径归属不同的号（张冠李戴）→ CV-BUS 按在册面答案判红。"""
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D13-28")
    assert str(n["module_id"]).startswith("MOD-")
    n["module_id"] = "MOD-L00-004"
    errs = _errs(d)
    assert any("与在册面对" in e and n["node_id"] in e for e in errs), errs[:4]


def test_red_module_id_hanging_without_ref():
    d = copy.deepcopy(_GOOD)
    g = _find(d, "D13-G01")
    g["module_id"] = "MOD-L00-004"
    assert any("空挂总线" in e for e in _errs(d))


def test_red_null_module_id_without_red_reason():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-09").pop("red_reason")
    assert any("module_id 为空必配 red_reason" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 G：CV-DUAL——双轴口径（confidence × verified_scope × 骨架三态）
# ---------------------------------------------------------------------------


def test_red_structure_node_disguised_as_production():
    """谎：把骨架 🔨 环节标 production（生产 14 个是多出来的，计数与逐节点两条判据同时命中）。"""
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D13-16")
    n["verified_scope"] = "production"
    n["build_status"] = "built"
    n["module_ref"] = "src/zephyr/data/scheduler.py"
    n["module_id"] = "MOD-L00-004"
    n["exec_evidence"] = ["复跑: grep -n intraday_sector src/zephyr/data/config/schedule.yaml"]
    errs = _errs(d)
    assert any("谎——verified_scope=production" in e and "D13-16" in e for e in errs), errs[:4]
    assert any("CV-DUAL 计数" in e for e in errs)


def test_red_production_claim_undercount_is_red():
    """欠：把骨架 ✅ 环节降级为 structure（少报同样是口径失真，不许用降态让图变干净）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-34")["verified_scope"] = "structure"
    errs = _errs(d)
    assert any("欠——骨架 ✅ 环节未宣 production" in e for e in errs)
    assert any("CV-DUAL 计数" in e for e in errs)


def test_red_production_without_exec_evidence():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-30")["exec_evidence"] = []
    assert any("必带 exec_evidence" in e for e in _errs(d))


def test_red_exec_evidence_pure_prose_has_no_rerun_handle():
    """exec_evidence 必须是可复跑把手（命令或 文件:行），纯散文断言不构成分产证据。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-30")["exec_evidence"] = ["作者印象中该批次每天都在跑"]
    assert any("无可复跑把手" in e for e in _errs(d))


def test_red_production_confidence_mismatch():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-07")["confidence"] = "proposed"
    assert any("production 必 verified" in e for e in _errs(d))


def test_red_verified_without_evidence():
    d = copy.deepcopy(_GOOD)
    n = _find(d, "D13-16")
    n["evidence"] = []
    assert any("verified 必带 evidence" in e for e in _errs(d))


def test_red_illegal_verified_scope_and_wiring_enums():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-05")["verified_scope"] = "in_production"
    _find(d, "D13-06")["wiring_status"] = "slot_idle"
    errs = _errs(d)
    assert any("verified_scope 非法" in e for e in errs)
    assert any("wiring_status 非法" in e for e in errs)


def test_red_wiring_status_is_the_single_slot_hollow_slot_field():
    """L1 裁定：「槽挂着但没跑」只走 wiring_status 一个字段——自造第二表达位判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-13")["slot_runs"] = False
    d["nodes"] = [n for n in d["nodes"]]
    # 自造字段本身不被识别=不违规；违规点是它替代/冲突了 wiring_status：把空转槽洗成 wired
    _find(d, "D13-13")["wiring_status"] = "wired"
    _find(d, "D13-13")["machine_facts"]["slot_facts"]["idle_slot"] = False
    assert any("idle_slot 真落空标记数不符" in e for e in _errs(d))


def test_red_counts_by_verified_scope_drift():
    """手改 counts 不回生成（双轴计数是机生面，禁散文改数）。"""
    d = copy.deepcopy(_GOOD)
    d["counts"]["by_verified_scope"] = {"production": 20, "structure": 28}
    assert any("by_verified_scope" in e for e in _errs(d))


def test_red_counts_by_wiring_status_drift():
    d = copy.deepcopy(_GOOD)
    d["counts"]["by_wiring_status"]["wired"] = 99
    assert any("by_wiring_status" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 H：CV-GAP——缺口节点形态（六图终局卷 §1「gap 是合法节点，但须带 red_reason」）
# ---------------------------------------------------------------------------


def test_red_gap_node_island_without_edge():
    d = copy.deepcopy(_GOOD)
    d["edges"] = [e for e in d["edges"] if "D13-G01" not in e]
    assert any("D13-G01" in e and "不得孤岛" in e for e in _errs(d))


def test_red_gap_node_washed_into_stage():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-G02")["node_type"] = "stage"
    assert any("契约编号为 gap 节点但 node_type" in e for e in _errs(d))


def test_red_gap_node_with_module_ref():
    """gap 节点挂实现代码锚=把缺口伪装成已实现件（CV-GAP 判红）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-G03")["module_ref"] = "src/zephyr/trading/recon_runner.py:392"
    assert any("gap 节点不该有 module_ref" in e for e in _errs(d))


def test_red_illegal_red_reason_enum():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-09")["red_reason"] = "pending"
    assert any("red_reason 非法" in e for e in _errs(d))


def test_red_rogue_gap_node_beyond_contract():
    d = copy.deepcopy(_GOOD)
    rogue = copy.deepcopy(_find(d, "D13-G01"))
    rogue["node_id"] = "D13-G77"
    d["nodes"].append(rogue)
    d["edges"].append(["D13-04", "D13-G77"])
    assert any("D13-G77" in e and "越出契约全集" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 I：CV-ADMIT——就绪门语义边必须真实存在（假门/空门判红）
# ---------------------------------------------------------------------------


def test_red_declared_admission_edge_missing_from_edges():
    d = copy.deepcopy(_GOOD)
    d["edges"] = [e for e in d["edges"] if e != ["D13-09", "D13-15"]]
    errs = _errs(d)
    assert any("CV-ADMIT" in e and "D13-09->D13-15" in e for e in errs), errs[:4]


def test_red_ready_gate_node_without_admission_out_edge():
    """空门判红：把 D13-30 的准入出边声明全删（门格仍在，但语义边只在散文里）。"""
    d = copy.deepcopy(_GOOD)
    d["admission_edges"] = [a for a in d["admission_edges"] if a["from"] != "D13-30"]
    errs = _errs(d)
    assert any("无任何准入出边" in e and "D13-30" in e for e in errs), errs[:4]


def test_red_admission_edge_without_note():
    d = copy.deepcopy(_GOOD)
    d["admission_edges"][0]["note_zh"] = ""
    assert any("缺 note_zh" in e for e in _errs(d))


def test_red_gate_node_without_denial_semantics():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-09").pop("admission_denied_zh")
    assert any("拒准入语义" in e and "D13-09" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 J：空转槽与 16 落空对象的双向可查（CV-DANGLE）
# ---------------------------------------------------------------------------


def test_green_idle_slots_and_dangling_ledger_are_queryable():
    """终局判据①：2 空转槽与 16 落空对象全部可查——台账逐条带 owner_nodes 且非空。"""
    dg = _GOOD["machine_facts"]["trigger_surfaces"]["dangling_objects"]
    assert sorted(dg["fake_channel_slots"]) == ["eod_reconciliation", "post_auction"]
    assert dg["total"] == _GOOD["counts"]["machine"]["dangling_total"] == len(dg["entries"]) == 16
    assert all(e["owner_nodes"] for e in dg["entries"]), "落空对象必须至少有一个归属环节"
    by_id = {e["id"]: e for e in dg["entries"]}
    for slot in ("post_auction", "eod_reconciliation"):
        owners = by_id[f"slot:{slot}"]["owner_nodes"]
        assert all(_find(_GOOD, o)["wiring_status"] == "unwired_slot_hollow" for o in owners)
    outside = sum(x["effective_task_count"] for x in dg["tasks_outside_catchup_universe"])
    assert (len(dg["fake_channel_slots"]), len(dg["orphan_tasks"]), outside, len(dg["double_slot_tasks"])) == (
        2,
        4,
        9,
        1,
    )


def test_red_dangling_entry_without_node_claim():
    """把某条落空对象从**节点侧** gap_refs 抹掉（台账仍在）→ CV-DANGLE 判红：缺口隐身。"""
    d = copy.deepcopy(_GOOD)
    victim = "task:dividend_incremental"
    n = next(x for x in d["nodes"] if victim in (x.get("gap_refs") or []))
    n["gap_refs"] = [g for g in n["gap_refs"] if g != victim]
    errs = _errs(d)
    assert any("无节点认领" in e and victim in e for e in errs), (n["node_id"], errs[:4])


def test_red_dangling_unclaimed_ledger_flagged_at_generation_face():
    """生成期归属面（counts.machine.dangling_unclaimed）非空=有落空对象无处可查 → 判红。"""
    d = copy.deepcopy(_GOOD)
    assert d["counts"]["machine"]["dangling_unclaimed"] == []
    d["counts"]["machine"]["dangling_unclaimed"] = ["task:ghost_ownerless"]
    assert any("dangling_unclaimed" in e and "task:ghost_ownerless" in e for e in _errs(d))


def test_red_node_claims_dangling_object_not_in_ledger():
    """节点 gap_refs 引一个台账里没有的 slot:/task: 对象 = 伪造缺口或图未回生成 → 判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-05")["gap_refs"].append("slot:slot_nobody_declared")
    errs = _errs(d)
    assert any("台账在册外" in e and "slot:slot_nobody_declared" in e for e in errs), errs[:4]


def test_red_dangling_total_drift():
    d = copy.deepcopy(_GOOD)
    d["counts"]["machine"]["dangling_total"] = 99
    assert any("dangling_total" in e for e in _errs(d))


def test_red_idle_slot_flag_without_node_mark():
    """真源侧记为空转槽、节点侧 idle_slot 抹平 → counts 与节点标记交叉核对判红。"""
    d = copy.deepcopy(_GOOD)
    for n in d["nodes"]:
        if (n.get("machine_facts") or {}).get("slot_facts", {}).get("idle_slot") is True:
            n["machine_facts"]["slot_facts"]["idle_slot"] = False
    assert any("idle_slot 真落空标记数不符" in e for e in _errs(d))


def test_red_dangling_ledger_and_counts_diverge():
    d = copy.deepcopy(_GOOD)
    d["machine_facts"]["trigger_surfaces"]["dangling_objects"]["fake_channel_slots"] = ["eod_reconciliation"]
    assert any("空转槽台账须同源" in e for e in _errs(d))


def test_red_downstream_action_illegal_mixes_watch_and_do():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-02")["downstream_action"] = "auto_fix"
    assert any("downstream_action 非法" in e for e in _errs(d))


def test_red_miss_policy_out_of_vocabulary():
    """表A-A6 落格后值域即判据：把 absorb（幂等吸收）写成 ignore 属自造口径 → 判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-16")["miss_policy"] = "ignore"
    assert any("miss_policy 非法" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 K：通用结构类
# ---------------------------------------------------------------------------


def test_red_dangling_edge():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-30", "D13-不存在"])
    assert any("边引用了不存在的节点" in e for e in _errs(d))


def test_red_self_loop():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-32", "D13-32"])
    assert any("自环边" in e for e in _errs(d))


def test_red_duplicate_edge():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-28", "D13-29"])
    assert any("重复边" in e for e in _errs(d))


def test_red_undeclared_reverse_edge():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-38", "D13-04"])
    assert any("未声明为反馈环的反向边" in e for e in _errs(d))


def test_green_declared_feedback_allowed():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-38", "D13-04"])
    d["feedback_loops"].append({"from": "D13-38", "to": "D13-04", "note": "演示环路"})
    assert not any("未声明为反馈环" in e for e in _errs(d))


def test_red_feedback_without_note():
    d = copy.deepcopy(_GOOD)
    d["feedback_loops"].append({"from": "D13-44", "to": "D13-01"})
    assert any("缺 note" in e for e in _errs(d))


def test_red_feedback_references_unknown_node():
    d = copy.deepcopy(_GOOD)
    d["feedback_loops"].append({"from": "D13-44", "to": "D13-99", "note": "幽灵节点"})
    assert any("反馈环引用了不存在的节点" in e for e in _errs(d))


def test_red_built_without_module_ref():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-30")["module_ref"] = ""
    assert any("built 节点必须有 module_ref" in e for e in _errs(d))


def test_red_missing_node_in_contract_universe():
    d = copy.deepcopy(_GOOD)
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D13-26"]
    errs = _errs(d)
    assert any("缺环节" in e and "D13-26" in e for e in errs)
    assert any("total_nodes" in e for e in errs)


def test_red_missing_gap_node_is_undercount():
    d = copy.deepcopy(_GOOD)
    d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D13-G04"]
    assert any("缺环节/缺口节点" in e and "D13-G04" in e for e in _errs(d))


def test_red_rogue_node_beyond_universe():
    d = copy.deepcopy(_GOOD)
    rogue = copy.deepcopy(_find(d, "D13-04"))
    rogue["node_id"] = "D13-X99"
    d["nodes"].append(rogue)
    assert any("D13-X99" in e and "越出契约全集" in e for e in _errs(d))


def test_red_duplicate_node_id():
    d = copy.deepcopy(_GOOD)
    d["nodes"].append(copy.deepcopy(_find(d, "D13-11")))
    assert any("node_id 存在重复" in e for e in _errs(d))


def test_red_counts_edges_drift():
    d = copy.deepcopy(_GOOD)
    d["edges"].append(["D13-42", "D13-12"])
    assert any("total_edges" in e for e in _errs(d))


def test_red_counts_segment_distribution_drift():
    d = copy.deepcopy(_GOOD)
    d["counts"]["by_segment"] = {"A": 12, "B": 14, "C": 12, "D": 9}
    assert any("四段分布" in e for e in _errs(d))


def test_red_missing_module_id_scan_counters():
    d = copy.deepcopy(_GOOD)
    d["counts"]["machine"]["module_id_scan"]["nodes_with_module_id"] = 0
    assert any("module_id_scan" in e for e in _errs(d))


def test_red_missing_top_level_key():
    d = copy.deepcopy(_GOOD)
    d.pop("machine_facts")
    assert any("缺顶层必填键: machine_facts" in e for e in _errs(d))


def test_red_missing_admission_edges_top_key():
    d = copy.deepcopy(_GOOD)
    d.pop("admission_edges")
    assert any("缺顶层必填键: admission_edges" in e for e in _errs(d))


def test_red_laws_empty_drops_hard_lets_go():
    d = copy.deepcopy(_GOOD)
    d["laws"] = []
    assert any("laws" in e for e in _errs(d))


def test_red_ready_gate_false_without_reason():
    """骨架 §1 门④：非门格须写 no_ready_gate_reason_zh（空值须有语义）。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-38")["no_ready_gate_reason_zh"] = ""
    assert any("no_ready_gate_reason_zh" in e and "D13-38" in e for e in _errs(d))


def test_red_fallback_empty_string_is_not_a_declaration():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-38")["fallback"] = ""
    assert any("fallback 不得为空串" in e for e in _errs(d))


def test_red_required_key_absent_not_none():
    """双轴/总线/缺口挂载面的键必须存在（值可 null）——删键=静默缺失，判红。"""
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-15").pop("verified_scope")
    _find(d, "D13-15").pop("module_id")
    errs = _errs(d)
    assert any("缺必填键 verified_scope" in e for e in errs)
    assert any("缺必填键 module_id" in e for e in errs)


def test_red_decision_question_too_long():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-32")["decision_question"] = "长" * 121
    assert any("decision_question 超" in e for e in _errs(d))


def test_red_cadence_declared_too_long():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-11")["cadence_zh"]["declared"] = "时" * 161
    assert any("cadence_zh.declared 超" in e for e in _errs(d))


def test_red_path_anchor_not_on_disk():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-37")["source_anchors"] = ["src/zephyr/data/never_exists_module.py:1"]
    assert any("路径锚磁盘实存检查失败" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 L：INV-1 复制侵权（含图13 特化 cron 字面量禁令）
# ---------------------------------------------------------------------------


def test_red_inv1_copy_schedule_description():
    sched = yaml.safe_load((_REPO / "src/zephyr/data/config/schedule.yaml").read_text(encoding="utf-8"))
    body = next(
        str(v["description"]).strip()
        for v in sched["schedules"].values()
        if len(str(v.get("description") or "").strip()) >= 25
    )
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-17")["note_zh"] = body
    errs = _errs(d)
    assert any("INV-1 复制侵权" in e for e in errs), errs[:3]


def test_red_inv1_copy_task_capability():
    tasks = yaml.safe_load((_REPO / "src/zephyr/data/config/tasks.yaml").read_text(encoding="utf-8"))
    body = next(
        str(t["capability"]).strip() for t in tasks["tasks"] if len(str(t.get("capability") or "").strip()) >= 25
    )
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-35")["note_zh"] = body
    assert any("INV-1 复制侵权" in e for e in _errs(d))


def test_red_inv1_cross_source_copy_from_gate_registry():
    """跨真源覆盖面（与图11/12 同纪律）：门禁册条目正文抄进图 13 节点同样判红。"""
    greg = yaml.safe_load(
        (_REPO / "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml").read_text(encoding="utf-8")
    )
    stolen = next(
        g.get("description", "").strip()
        for g in greg.get("gates", [])
        if isinstance(g.get("description"), str)
        and len(g.get("description", "").strip()) >= 25
        and sum(1 for c in g["description"] if "一" <= c <= "鿿") >= 10
    )
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-34")["note_zh"] = stolen
    assert any("INV-1 复制侵权" in e for e in _errs(d))


def test_red_cron_literal_in_cadence():
    d = copy.deepcopy(_GOOD)
    _find(d, "D13-30")["cadence_zh"]["declared"] = "槽 cron 为 30 16 * * 0-4"
    errs = _errs(d)
    assert any("cron 字面量" in e for e in errs), errs[:3]


def test_red_cron_literal_anywhere_in_document():
    d = copy.deepcopy(_GOOD)
    d["laws"].append("槽位时刻以 45 16 * * 0-4 为准")
    assert any("cron 字面量" in e for e in _errs(d))


def test_green_real_map_has_no_cron_literal():
    """控制组：真图全树无 cron 字面量（否则上面两条红案无判别力）。"""
    blob = (_REPO / _MAP_REL).read_text(encoding="utf-8")
    assert not re.search(r"^\s*.*\*{1,2}\s+\*?\d*\s+\*\s+\*\s+[0-9\-\*,/]+$", blob, re.M)


# ---------------------------------------------------------------------------
# 红组 M：外部面不可达只降 warn（禁环境异常打死无辜提交），且生成器纪律守卫
# ---------------------------------------------------------------------------


def test_external_surfaces_unreachable_downgrades_to_warn(tmp_path):
    """解析根指向空目录：骨架/在册面全不可达 → 不得升级 error，只出 warnings。"""
    d = copy.deepcopy(_GOOD)
    warnings: list[str] = []
    errs = validate_structure(d, root=tmp_path, warnings=warnings)
    assert all("CV-DUAL 计数" not in e and "骨架" not in e for e in errs), errs[:4]
    assert any("骨架状态列不可读" in w for w in warnings)


def test_generator_is_byte_idempotent():
    """同输入两次产出逐字节等（幂等=机生图可复核的前提）。"""
    import generate_trading_day_cycle_map as gen

    a = gen.serialize_document(gen.build_document(as_of="2026-09-24T00:00:00+08:00", root=_REPO, skip_schtasks=True))
    b = gen.serialize_document(gen.build_document(as_of="2026-09-24T00:00:00+08:00", root=_REPO, skip_schtasks=True))
    assert hashlib.sha256(a.encode()).hexdigest() == hashlib.sha256(b.encode()).hexdigest()


def test_generator_idempotency_guard_has_teeth(tmp_path):
    """证明上一条有判别力：注入不同时间戳必须产出不同字节。"""
    import generate_trading_day_cycle_map as gen

    a = gen.serialize_document(gen.build_document(as_of="2026-09-24T00:00:00+08:00", root=_REPO, skip_schtasks=True))
    b = gen.serialize_document(gen.build_document(as_of="2026-09-25T00:00:00+08:00", root=_REPO, skip_schtasks=True))
    assert a != b
    out = tmp_path / "gen_out.yaml"
    out.write_text(a, encoding="utf-8")
    assert "generated_at: '2026-09-24T00:00:00+08:00'" in out.read_text(encoding="utf-8")


def test_generator_refuses_to_emit_production_without_exec():
    """生成期硬失败：production 环节无 exec_evidence 时宁可不产图（禁产出自粉饰的产物）。"""
    import generate_trading_day_cycle_map as gen

    original = dict(gen.EXEC)
    try:
        gen.EXEC.pop("D13-34")
        with pytest.raises(KeyError) as exc:
            gen.build_document(as_of="2026-09-24T00:00:00+08:00", root=_REPO, skip_schtasks=True)
        assert "D13-34" in str(exc.value)
    finally:
        gen.EXEC.clear()
        gen.EXEC.update(original)


def test_generator_forbids_wall_clock_take():
    src = (_GENERATORS_DIR / "generate_trading_day_cycle_map.py").read_text(encoding="utf-8")
    assert not re.search(r"datetime\.now\(\)|\btime\.time\(\)|datetime\.datetime\.now\(\)", src)


def test_schtasks_surface_is_read_only_query():
    src = (_GENERATORS_DIR / "generate_trading_day_cycle_map.py").read_text(encoding="utf-8")
    assert not re.search(r"(Register|Unregister|Change|Enable|Disable)-ScheduledTask", src)
    assert "Get-ScheduledTask" in src


def test_module_id_index_rejects_unimplemented_roster_entries():
    """在册面 existence=未实现/deprecated 的条目不得被采信为实现代码总线号（逐路径核"已实现"）。"""
    import generate_trading_day_cycle_map as gen

    idx = gen.scan_module_id_index(_REPO)
    roster = gen.scan_roster_module_ids(_REPO)
    assert idx and roster
    assert all(str(v).startswith("MOD-") for v in idx.values())
    assert set(idx.values()) <= roster


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
