# [q0213-RESCUE] 本件字节捞回自 q-0213 死袋 blob sha256=3daa7c5be0ca6ff5…（HEAD_MISSING 真孤儿，2026-09-29 车道 st-finaldel-crescue-20260929 落盘）。
# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §strategy_card_lifecycle_map
# [MODULE] tests.governance.d5_architecture.test_strategy_card_lifecycle_map_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; copy; hashlib; subprocess; sys; pathlib;
#   scripts.governance.d5_architecture.validators.validate_strategy_card_lifecycle_map
#   （validate_structure / check_instances / check_prose_counts / scan_skeleton_axes /
#   load_anchor_block / state_values / terminal_values）；
#   scripts.governance.d5_architecture.generators.generate_strategy_card_lifecycle_map
#   （build_document / serialize_document 幂等实证）
# [CONSUMERS] 图15 校验器质量守卫（坏图与坏台账必须被拦，判通过的尺必须先证明自己会红）；
#   STRATEGY-CARD-LIFECYCLE-MAP gate 的同源判据消费面
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图/坏台账用例全部构造于内存副本或 tmp_path（禁写生产路径，宪法运维红线 6）；
#   红用例断言"校验器必须点名这一条具体语义"，不接受"只判非空"；
#   必含两类硬证据——①该红仍红（SEALED 就地复活、唯一真复活链、三元错绑）
#   ②误伤归零（多成员合法族在新 CV-08 下不得红、派生指针不得被当复活）；
#   形态照抄 test_construction_workflow_map_adversarial（图14 母版）
# [MODIFY-GUARD] 本件是"校验器能红"的证据面：删用例或把断言放宽成"只判非空"=放水，
#   必须先改校验器判据再改本件；改判据输入口径（如 CV-06/CV-08 回炉）必须同步补两组用例
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图15 卡生命周期状态机校验器对抗测试（红蓝各一组的回炉证据）。

红组（每种坏必须被点名）：缺顶层键 / 词表删值 / 图自造状态值 / 状态编号重复 / 非法迁移 /
**SEALED 就地复活** / **就地改判 red→green** / 候选卡直接出 PASS / 一次性令牌二次消耗 /
复活指针三缺（缺省、指向自身、指向非终态）/ 同假设双卡 A 腿 / 卡号↔文件↔判决三元错绑 B 腿 /
族账不平 C 腿 / 凭证未在册 / 镜像与真源冲突 / 禁止边被删 / **禁止边被绕过边规避** /
禁边与无凭证合法边同对 / 六处分裂面缺一条 / 分裂面孤岛 / counts 漂移 / 散文写死计数 /
L0 旧名残留 / 越域挂载 / INV-1 超长 / CV-BUS 空挂 / production 谎与欠 / 假切源 /
判据真源不在盘 / 同字节双真源 / CLI 退出码三态。

蓝组（钉口径面）：真图 gate 面零 error；production 数恒等骨架 ✅ 数；案例 A 全链不红；
**旧 CV-08 误伤的四个合法多成员族在新判据下全部不红**；派生指针（候选卡）不被误判为复活；
n_eff 缺声明只 warn；生成器幂等逐字节等；两件源码零壁钟取时；真图零废止别名。
"""

from __future__ import annotations

import copy
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

# [q0213-RESCUE] 适配：伴生校验器 validate_strategy_card_lifecycle_map.py 现为工作区未跟踪在飞件（不碰）；生成器件 generate_strategy_card_lifecycle_map.py 尚未落 HEAD，模块级 importorskip 防收集炸弹，落库后自动恢复实跑
pytest.importorskip("validate_strategy_card_lifecycle_map")
pytest.importorskip("generate_strategy_card_lifecycle_map")

import generate_strategy_card_lifecycle_map as G  # noqa: E402
import validate_strategy_card_lifecycle_map as V  # noqa: E402

_MAP_REL = "config/strategy_card_lifecycle_map.yaml"
_PROPOSAL_REL = "docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))
_PROPOSAL = yaml.safe_load((_REPO / _PROPOSAL_REL).read_text(encoding="utf-8"))
# 2026-09-26 宿主落地：状态词表的真源=在册受控词表（不再是提案件），提案件只留施工口径与档案
_VOCAB = yaml.safe_load((_REPO / V._REGISTRY_VOCAB_REL).read_text(encoding="utf-8"))["values"]
_VOCAB_PROPOSAL = _PROPOSAL["card_state_vocabulary"]["values"]
_SKELETON = V.scan_skeleton_axes(_REPO)


def _errs(d: dict, block: dict | None = None) -> list[str]:
    """gate 面口径（live=False）：磁盘实存与在册探活跳，结构面一项不放宽。"""
    return V.validate_structure(
        d, root=_REPO, warnings=[], live=False, block=block if block is not None else _PROPOSAL_BLOCK
    )


def _inst_errs(entries: list[dict], d: dict | None = None, live: bool = False, root: Path | None = None) -> list[str]:
    e, _w = V.check_instances(
        entries, d or _GOOD, root=root or _REPO, warnings=[], live=live, block=("proposal", _PROPOSAL_BLOCK)
    )
    return e


def _entry(cid: str, state: str, **kw) -> dict:
    base = {
        "card_id": cid,
        "entry_kind": "single_hypothesis",
        "card_state": state,
        "credential": [],
        "lives_in": [],
        "verdict_bindings": [],
        "rejudge_used": False,
    }
    base.update(kw)
    return base


def _find_state(d: dict, value: str) -> dict:
    return next(s for s in d["states"] if s.get("value") == value)


def _find_trans(d: dict, tid: str) -> dict:
    return next(t for t in d["transitions"] if t.get("transition_id") == tid)


def _find_forbid(d: dict, xid: str) -> dict:
    return next(x for x in d["forbidden_edges"] if x.get("edge_id") == xid)


_PROPOSAL_BLOCK = {
    "values": _VOCAB,
    "card_entries": _PROPOSAL["card_entries"],
    "revival_authorizations": _PROPOSAL["revival_authorizations"],
    "proposal": _PROPOSAL,
}
_TRUE = str(_PROPOSAL["revival_authorizations"][1])  # 做T 复活改裁授权
_SEALED_ID = next(str(v["value"]) for v in _VOCAB if v.get("map_state") == "D15-S10")
_DRAFT_ID = next(str(v["value"]) for v in _VOCAB if v.get("map_state") == "D15-S1")


# ---------------------------------------------------------------------------
# 蓝组：口径面必须先钉住（尺不绿，红组无从谈起）
# ---------------------------------------------------------------------------


class TestBlueCaliber:
    def test_real_map_passes_gate_face(self):
        assert _errs(_GOOD) == []

    def test_host_face_is_live_registry_not_proposal(self):
        """★ 宿主落地钉（L-HOST15）：图头两口径同批翻转，且两面真源真的在盘可读。

        anchor_source=registry 必须意味着——状态值集从在册词表来、实例台账从宿主册 CARD-*
        契约条目来、提案件不再是状态真源、登记欠账为空。四腿任一不成立即假迁移。
        """
        assert _GOOD["registry_host"] == "experiment_registry"
        assert _GOOD["anchor_source"] == "registry"
        assert _GOOD["anchor_block_origin"] == V._REGISTRY_VOCAB_REL
        src, block = V.load_anchor_block(_REPO)
        assert src == "registry"
        assert {str(v["value"]) for v in block["values"]} == {str(v["value"]) for v in _VOCAB}
        host = V.host_contract_entries(_REPO)
        assert host and all(str(e["experiment_id"]).startswith("CARD-") for e in host)
        assert all(str(e["card_state"]) in {str(v["value"]) for v in _VOCAB} for e in host)
        assert _GOOD["counts"]["unregistered_declarable"] == 0
        assert _GOOD["pending_registration"]["unregistered_declarable"] == []

    def test_registered_ledger_is_the_host_face(self):
        """图实例面必须等于宿主册契约条目面（禁图自带种子=第二真源）。"""
        host_ids = {str(e.get("card_id")) for e in V.host_contract_entries(_REPO)}
        assert {str(e.get("card_id")) for e in _GOOD["card_ledger"]} == host_ids
        assert _GOOD["counts"]["registered_entries_in_ledger"] == len(host_ids)
        c = _GOOD["counts"]
        # 分母恒等式：已登记 = 语料全量 − 无头 − 待裁 − 非域 − 别名未覆盖 − 回填欠账
        assert c["corpus_files_registered"] == (
            c["cards_total"]
            - c["state_undeclared_headless"]
            - c["needs_adjudication"]
            - c["non_domain_excluded"]
            - c["unmatched_alias"]
            - c["unregistered_declarable"]
        )

    def test_landed_vocabulary_equals_proposal_block(self):
        """迁移窗口校验：在册词表与 91 号件 §2 值集逐项同构（回填无损，档案降级不留差异）。"""
        assert [(str(v["value"]), str(v["map_state"]), bool(v.get("terminal"))) for v in _VOCAB] == [
            (str(v["value"]), str(v["map_state"]), bool(v.get("terminal"))) for v in _VOCAB_PROPOSAL
        ]

    def test_production_equals_skeleton_checkmark(self):
        """双轴恒等式：图内 production 数 == 骨架 §2.1+§2.2 实查列 ✅ 数（多了算谎少了算欠）。"""
        want = len(_SKELETON["production_transitions"]) + len(_SKELETON["production_forbidden"])
        got = _GOOD["counts"]["production"]
        assert got == want == 13

    def test_three_object_classes_are_all_present(self):
        """禁止边是本图一半价值：三类对象一条不许丢。"""
        assert (len(_GOOD["states"]), len(_GOOD["transitions"]), len(_GOOD["forbidden_edges"]), len(_GOOD["gaps"])) == (
            13,
            17,
            13,
            6,
        )
        assert {x["edge_kind"] for x in _GOOD["forbidden_edges"]} == {"forbidden"}
        assert {t["edge_kind"] for t in _GOOD["transitions"]} == {"permitted"}

    def test_case_a_chain_is_not_red(self):
        """案例 A（重判一次后封卡）全链必须合法——回炉不得把唯一的活体链判红。"""
        sealed = next(e for e in _PROPOSAL["card_entries"] if e["card_id"] == "T0-PRERG-02")
        errs = _inst_errs([sealed, _entry("T0-COND-X", _SEALED_ID)])
        assert not [e for e in errs if "T0-PRERG-02" in e and ("CV-04" in e or "CV-07" in e)]

    def test_legacy_overbroad_cv08_false_positives_zeroed(self):
        """★ 误伤归零：旧判据（同 family_id 且活跃 >1 即红）在 89 张口径下命中 37 张，
        新 C 腿只判"族成员数≠声明 n_eff"，四个合法多成员族必须全绿。"""
        fam = _GOOD["corpus"]["families"]
        old_rule_hits = sum(v["members"] for v in fam.values() if v["members"] > 1)
        assert old_rule_hits >= 30  # 旧判据的误伤面（实测 37）
        errs = _inst_errs(list(_PROPOSAL["card_entries"]))
        for legal in ("P3-E1C-STABLE13", "P3-B2-VOL12", "P3-B2-STAT3", "P3-B-FIRST6"):
            assert not [e for e in errs if "CV-08C" in e and legal in e], legal
        assert [e for e in errs if "CV-08C" in e and "T0-PRERG" in e], "该红仍红：族账真不平"

    def test_derivation_is_not_revival(self):
        """★ 误伤归零：候选卡的 parent_context 指向一张 frozen 卡与其报告（派生非复活）
        不得被 CV-06 判红（簿01 OBS-K-2 的教训）。"""
        cand = _entry(
            "ALGO-CAND-MOM-01",
            "candidate",
            lives_in=[{"path": "docs/_working/x/candidate_card_open_momentum_market.md"}],
            parent_context="momentum_prereg_card.md（frozen 输入真源）+ momentum_exam_report.md",
        )
        assert not [e for e in _inst_errs([cand]) if "CV-06" in e]

    def test_missing_n_eff_is_warn_only(self):
        e, w = V.check_instances(
            [_entry("X-A1-01", "frozen", n_eff="unknown", credential=[])],
            _GOOD,
            root=_REPO,
            warnings=[],
            live=False,
            block=("proposal", _PROPOSAL_BLOCK),
        )
        assert not [x for x in e if "CV-08D" in x]
        assert any("CV-08D" in x for x in w)

    def test_no_banned_field_aliases_in_real_map(self):
        text = (_REPO / _MAP_REL).read_text(encoding="utf-8")
        for banned in V.BANNED_FIELDS:
            assert f"{banned}:" not in text, banned

    def test_generators_and_validators_forbid_wall_clock(self):
        for rel in (
            "scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py",
            "scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py",
        ):
            src = (_REPO / rel).read_text(encoding="utf-8")
            bad = [l for l in src.splitlines() if "datetime.now()" in l or "time.time()" in l]
            # 只禁可执行代码取时；纪律条款本身（注释/头文档里的"禁 datetime.now()"）必须留着
            assert all(l.lstrip().startswith("#") or "禁" in l for l in bad), (rel, bad[:2])

    def test_generator_is_byte_idempotent(self):
        a = G.serialize_document(G.build_document(as_of="2026-09-25T00:00:00+08:00", root=_REPO))
        b = G.serialize_document(G.build_document(as_of="2026-09-25T00:00:00+08:00", root=_REPO))
        assert hashlib.sha256(a.encode()).hexdigest() == hashlib.sha256(b.encode()).hexdigest()

    def test_real_map_equals_generator_output(self):
        """图 YAML 必须是生成器的当前产物（禁手改不回生成）。"""
        payload = G.serialize_document(G.build_document(as_of=_GOOD["generated_at"], root=_REPO))
        assert payload == (_REPO / _MAP_REL).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 红组 A：图结构面（状态机与禁边）
# ---------------------------------------------------------------------------


class TestRedStructure:
    def test_missing_top_level_key(self):
        d = copy.deepcopy(_GOOD)
        del d["forbidden_edges"]
        assert any("缺顶层必填键" in e for e in _errs(d))

    def test_vocabulary_value_removed_still_red(self):
        """RC-02 探针：从装载点删掉一个值，图仍在用 ⇒ 必须红（证明值集没被写死在代码里）。"""
        block = copy.deepcopy(_PROPOSAL_BLOCK)
        block["values"] = [v for v in block["values"] if v["value"] != _SEALED_ID]
        errs = _errs(_GOOD, block=block)
        assert any("CV-02" in e and _SEALED_ID in e for e in errs)

    def test_state_value_outside_vocabulary(self):
        d = copy.deepcopy(_GOOD)
        _find_state(d, _SEALED_ID)["value"] = "sealed_ish"
        assert any("CV-02" in e and "sealed_ish" in e for e in _errs(d))

    def test_duplicate_state_id(self):
        d = copy.deepcopy(_GOOD)
        d["states"][1]["state_id"] = d["states"][0]["state_id"]
        assert any("CV-03" in e for e in _errs(d))

    def test_forbidden_edge_removed_is_red(self):
        """RC-15：偷偷删掉 X03（封卡就地复活禁令）必须被骨架覆盖度腿抓住。"""
        d = copy.deepcopy(_GOOD)
        d["forbidden_edges"] = [x for x in d["forbidden_edges"] if x["edge_id"] != "D15-X03"]
        errs = _errs(d)
        assert any("CV-13" in e and "D15-X03" in e for e in errs)
        assert d["counts"]["total_forbidden_edges"] != len(d["forbidden_edges"])

    def test_forbidden_edge_bypassable_by_ungated_path(self):
        """★ 禁止边不可被绕过边规避：把 draft→frozen 与 frozen→executing 两条边的凭证都降为
        none，则 draft→executing（X06 禁令）出现全程无凭证路径，绕过探针必须红。"""
        d = copy.deepcopy(_GOOD)
        for tid in ("D15-M03", "D15-M06"):
            _find_trans(d, tid)["credential_required"] = "none"
            _find_trans(d, tid)["gated"] = False
        errs = _errs(d)
        assert any("可被绕过边规避" in e and "D15-X06" not in e and "draft" in e for e in errs), errs[:3]

    def test_forbidden_pair_with_ungated_permitted_twin(self):
        d = copy.deepcopy(_GOOD)
        t = _find_trans(d, "D15-M07")  # executing→green（X07 的条件性同对）
        t["credential_required"] = "none"
        assert any("CV-07" in e and "同对" in e for e in _errs(d))

    def test_terminal_state_with_outgoing_edge(self):
        d = copy.deepcopy(_GOOD)
        d["transitions"][0]["to_state"] = _find_state(d, _DRAFT_ID)["value"]
        d["transitions"][0]["transition_id"] = "D15-M11"  # 让终态封卡有了出边
        d["transitions"][0]["from_state"] = [_SEALED_ID]
        d["transitions"][0]["cross_instance"] = False
        assert any("CV-FSM" in e and "出边" in e for e in _errs(d))

    def test_self_loop_transition_is_red(self):
        d = copy.deepcopy(_GOOD)
        t = _find_trans(d, "D15-M03")
        t["from_state"] = [_SEALED_ID]
        t["to_state"] = _SEALED_ID
        assert any("自环迁移非法" in e for e in _errs(d))

    def test_gap_face_dropped_is_red(self):
        """六处分裂面（簿03 把普查的"三处"改判为六处）一条不许丢。"""
        for gid in ("D15-G01", "D15-G06"):
            d = copy.deepcopy(_GOOD)
            d["gaps"] = [g for g in d["gaps"] if g["gap_id"] != gid]
            assert any("CV-GAP" in e and gid in e for e in _errs(d)), gid

    def test_gap_island_is_red(self):
        d = copy.deepcopy(_GOOD)
        for it in d["states"] + d["transitions"] + d["forbidden_edges"]:
            it["gap_refs"] = [g for g in (it.get("gap_refs") or []) if g != "D15-G04"]
        assert any("孤岛" in e and "D15-G04" in e for e in _errs(d))

    def test_counts_drift_is_red(self):
        d = copy.deepcopy(_GOOD)
        d["counts"]["total_states"] = 6
        assert any("CV-14" in e and "total_states" in e for e in _errs(d))

    def test_by_state_must_equal_live_scan(self):
        d = copy.deepcopy(_GOOD)
        d["counts"]["by_state"]["frozen"] = 999
        assert any("CV-14" in e and "by_state" in e for e in _errs(d))

    def test_prose_hardcoded_counts(self):
        d = copy.deepcopy(_GOOD)
        d["laws"] = list(d["laws"]) + ["本图共 13 态 17 条边，禁止边 13 条"]
        assert any("CV-14" in e for e in V.check_prose_counts(d))

    def test_banned_field_alias(self):
        d = copy.deepcopy(_GOOD)
        d["states"][0]["mech_note_zh"] = "旧名回潮"
        assert any("CV-L0" in e and "mech_note_zh" in e for e in _errs(d))

    def test_cross_domain_field(self):
        d = copy.deepcopy(_GOOD)
        d["states"][2]["judgment_basis"] = "DSR>0.95"
        assert any("CV-DOMAIN" in e for e in _errs(d))

    def test_inv1_length_cap(self):
        d = copy.deepcopy(_GOOD)
        d["states"][0]["note_zh"] = "冻结" * 200
        assert any("CV-12 长度面" in e for e in _errs(d))

    def test_bus_requires_module_id_when_ref_present(self):
        d = copy.deepcopy(_GOOD)
        d["states"][0]["module_ref"] = "src/zephyr/backtest/run_archive.py"
        assert any("CV-BUS" in e for e in _errs(d))

    def test_bus_rejects_invented_module_id(self):
        d = copy.deepcopy(_GOOD)
        s = d["states"][0]
        s["module_id"] = "MOD-SELF-INVENTED-9"
        s["module_ref"] = "src/zephyr/backtest/run_archive.py"
        assert any("CV-BUS" in e and "MOD-SELF-INVENTED-9" in e for e in _errs(d))

    def test_dual_axis_overclaim_on_state(self):
        """状态面骨架无 ✅ 列 ⇒ 宣 production 即谎。"""
        d = copy.deepcopy(_GOOD)
        _find_state(d, _DRAFT_ID)["verified_scope"] = "production"
        assert any("CV-DUAL" in e and "不得宣 production" in e for e in _errs(d))

    def test_dual_axis_underclaim_on_transition(self):
        d = copy.deepcopy(_GOOD)
        tid = sorted(_SKELETON["production_transitions"])[0]
        _find_trans(d, tid)["verified_scope"] = "structure"
        assert any("CV-DUAL" in e and "少了算欠" in e for e in _errs(d))

    def test_fake_host_switch(self):
        """registry_host 声称已落地却 anchor_source 仍 proposal（或反之）=假迁移。"""
        d = copy.deepcopy(_GOOD)
        d["registry_host"] = "experiment_registry"
        d["anchor_source"] = "proposal"
        assert any("假迁移" in e for e in _errs(d))
        d2 = copy.deepcopy(_GOOD)
        d2["registry_host"] = "proposed:experiment_registry"
        d2["anchor_source"] = "registry"
        assert any("两口径互斥" in e for e in _errs(d2, block=_PROPOSAL_BLOCK))

    def test_anchor_origin_unloadable(self):
        d = copy.deepcopy(_GOOD)
        d["anchor_block_origin"] = "docs/_working/map_build/fig15_cardlife/99_does_not_exist.yaml"
        assert any("CV-HOST" in e for e in _errs(d))

    def test_registry_claim_without_host_face_is_red(self, tmp_path):
        """RC-22 声称 registry 期而宿主两面不在盘=假迁移（gate 面 live=False 也必须红）。"""
        empty = tmp_path / "repo"
        (empty / "docs/_working/map_build/fig15_cardlife").mkdir(parents=True)
        errs = V.validate_structure(_GOOD, root=empty, warnings=[], live=False, block=_PROPOSAL_BLOCK)
        host_errs = [e for e in errs if "CV-HOST" in e]
        assert any("词表装载点未切" in e for e in host_errs), host_errs
        assert any("无 CARD-* 契约条目" in e for e in host_errs), host_errs

    def test_registry_mode_without_contract_entries_is_red(self, tmp_path):
        """词表在册但宿主册仍是空契约面（只扩枚举不回填）=实例面未落地，必须红。"""
        vocab_dir = tmp_path / "docs/01_policies_and_standards/_registry/vocabularies"
        cats = tmp_path / "docs/01_policies_and_standards/_registry/catalogs"
        vocab_dir.mkdir(parents=True)
        cats.mkdir(parents=True)
        (vocab_dir / "card_state_vocabulary.yaml").write_text(
            yaml.safe_dump({"values": _VOCAB}, allow_unicode=True), encoding="utf-8"
        )
        (cats / "experiment_registry.yaml").write_text(
            yaml.safe_dump({"experiments": [{"experiment_id": "EXP-A-001"}]}, allow_unicode=True), encoding="utf-8"
        )
        errs = V.validate_structure(_GOOD, root=tmp_path, warnings=[], live=False, block=_PROPOSAL_BLOCK)
        assert [e for e in errs if "CV-HOST" in e and "无 CARD-* 契约条目" in e], errs

    def test_registry_debt_not_cleared_is_red(self):
        """RC-23 回填欠账未清空（卡头可判态却无登记条目）——禁"忘了就绿"。"""
        d = copy.deepcopy(_GOOD)
        d["pending_registration"]["unregistered_declarable"] = ["docs/_working/x.md"]
        assert any("CV-HOST" in e and "欠账未清空" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 红组 B：实例台账面（回炉后的 CV-05/06/07/08/09/10/17/18）
# ---------------------------------------------------------------------------


class TestRedInstances:
    def test_sealed_in_place_revival_is_red(self):
        """★ 封卡就地复活必红（#390 实弹原样复现）：sealed 卡再走 executing。"""
        e = _entry(
            "T0-PRERG-02",
            "executing",
            rejudge_used=True,
            credential=[{"seq": 1, "from": _SEALED_ID, "to": "executing", "ruling_id": "裁定#389"}],
        )
        errs = _inst_errs([e])
        assert any("CV-05" in x and "就地复活" in x for x in errs), errs
        assert any("CV-07" in x and "D15-X03" in x for x in errs), errs

    def test_red_to_green_in_place_is_red(self):
        e = _entry("X-A1-01", "green", credential=[{"seq": 1, "from": "red", "to": "green", "flag": "none"}])
        errs = _inst_errs([e])
        assert any("D15-X01" in x for x in errs)
        assert any("CV-04" in x for x in errs)  # 也不是合法边

    def test_candidate_direct_pass_is_red(self):
        e = _entry("X-A2-01", "green", credential=[{"seq": 1, "from": "candidate", "to": "green", "flag": "none"}])
        assert any("D15-X05" in x for x in _inst_errs([e]))

    def test_illegal_transition_pair_is_red(self):
        e = _entry(
            "X-A3-01", "sealed", credential=[{"seq": 1, "from": _DRAFT_ID, "to": _SEALED_ID, "ruling_id": "裁定#363"}]
        )
        assert any("CV-04" in x for x in _inst_errs([e]))

    def test_one_time_rejudge_token_twice_is_red(self):
        e = _entry(
            "T0-PRERG-02",
            _SEALED_ID,
            rejudge_used=True,
            credential=[
                {"seq": 1, "from": "red", "to": "frozen_amended", "ruling_id": "裁定#363"},
                {"seq": 2, "from": "frozen_amended", "to": "red", "flag": "test_evidence"},
                {"seq": 3, "from": "red", "to": "frozen_amended", "ruling_id": "裁定#363"},
            ],
        )
        assert any("CV-05" in x and "一次性令牌" in x for x in _inst_errs([e]))

    def test_revival_without_pointer_is_red(self):
        """★ 唯一真复活链必须被抓到（回炉前 CV-06 靠 family_id 等值，这条恰好漏判）。"""
        real = next(e for e in _PROPOSAL["card_entries"] if e["card_id"] == "T0-CONDITIONAL")
        errs = _inst_errs([dict(real)])
        assert any("CV-06" in x and "T0-CONDITIONAL" in x and _TRUE in x for x in errs), errs

    def test_revival_pointing_to_self_is_red(self):
        e = _entry("T0-CONDITIONAL", "frozen", revives="T0-CONDITIONAL", parent_context_cites=[_TRUE])
        assert any("指向自身" in x for x in _inst_errs([e]))

    def test_revival_pointing_to_non_terminal_is_red(self):
        entries = [
            _entry("OLD-AAA-01", "frozen"),
            _entry("T0-CONDITIONAL", "frozen", revives="OLD-AAA-01", parent_context_cites=[_TRUE]),
        ]
        assert any("未处于终态" in x for x in _inst_errs(entries))

    def test_revival_pointer_broken_is_red(self):
        e = _entry("T0-CONDITIONAL", "frozen", revives="NO-SUCH-CARD", parent_context_cites=[_TRUE])
        assert any("查无该卡" in x for x in _inst_errs([e]))

    def test_terminal_card_field_mutation_is_red(self):
        e = _entry("T0-PRERG-02", _SEALED_ID, field_changes=[{"field": "credential", "op": "rewrite_history"}])
        assert any("CV-05" in x and "仍变更字段 credential" in x for x in _inst_errs([e]))

    def test_terminal_card_appendable_field_is_green(self):
        e = _entry("T0-PRERG-02", _SEALED_ID, field_changes=[{"field": "lives_in", "op": "append_path"}])
        assert not [x for x in _inst_errs([e]) if "CV-05" in x]

    def test_same_hypothesis_two_cards_is_red(self):
        """CV-08 A 腿：hypothesis_key 相同（不看 family_id，两卡族名本来就不同）。"""
        entries = [
            _entry("T0-PRERG-01", "frozen", family_id="T0-PRERG", n_eff=1, hypothesis_key="vwap_reversion_t0"),
            _entry("ALGO-VWAP-03", "red", family_id=None, hypothesis_key="vwap_reversion_t0"),
        ]
        errs = _inst_errs(entries)
        assert any("X09" in x and "vwap_reversion_t0" in x for x in errs), errs

    def test_verdict_triple_misbinding_is_red(self):
        """CV-08 B 腿：卡号↔文件↔判决三元错绑（读三元组而非单字段，F-07 原判据抓不到）。"""
        entries = [
            _entry(
                "T0-PRERG-01",
                "frozen",
                family_id="T0-PRERG",
                n_eff=1,
                lives_in=[{"path": "docs/_working/x/t0_prereg_vwap_revert.md"}],
                verdict_bindings=[
                    {"ruling_id": "裁定#390", "verdict": "RED", "evidence_path": "docs/_working/y/vwap_exam_report.md"}
                ],
            ),
            _entry(
                "ALGO-VWAP-03",
                "red",
                lives_in=[
                    {"path": "docs/_working/y/vwap_prereg_card.md"},
                    {"path": "docs/_working/y/vwap_exam_report.md"},
                ],
            ),
        ]
        errs = _inst_errs(entries)
        assert any("CV-08B" in x and "三元错绑" in x for x in errs), errs

    def test_family_membership_mismatch_is_red(self):
        """CV-08 C 腿：family_id 的正确用法（族成员数 vs 声明 N_eff）。"""
        d = copy.deepcopy(_GOOD)
        d["corpus"] = dict(d["corpus"])
        d["corpus"]["families"] = {"T0-PRERG": {"members": 2, "declared_n_eff": [1], "single_hypothesis_members": 2}}
        errs = _inst_errs([_entry("T0-PRERG-01", "frozen")], d=d)
        assert any("CV-08C" in x and "T0-PRERG" in x for x in errs), errs

    def test_unregistered_credential_is_red(self):
        e = _entry(
            "X-B1-01", _SEALED_ID, credential=[{"seq": 1, "from": "red", "to": _SEALED_ID, "ruling_id": "裁定#999999"}]
        )
        assert any("CV-09" in x and "不在册" in x for x in _inst_errs([e]))

    def test_missing_credential_for_state_is_red(self):
        e = _entry("X-B2-01", _SEALED_ID)  # sealed 需凭证（词表 credential_required）
        assert any("CV-09" in x and "无迁移凭证" in x for x in _inst_errs([e]))

    def test_mirror_conflict_is_red(self):
        e = _entry(
            "P3-E1C-09",
            "suspended",
            card_face_state="frozen",
            credential=[{"seq": 1, "from": "insufficient", "to": "suspended", "ruling_id": "裁定#398"}],
        )
        assert any("CV-10" in x and "镜像" in x for x in _inst_errs([e]))

    def test_last_hop_must_equal_registered_state(self):
        e = _entry(
            "X-B3-01", "frozen", credential=[{"seq": 1, "from": "executing", "to": "red", "flag": "test_evidence"}]
        )
        assert any("CV-10" in x and "末跳" in x for x in _inst_errs([e]))

    def test_missing_truth_source_is_hard_red(self, tmp_path):
        """RC-18：被引为判据真源的卡件不在盘 ⇒ 必须 error（禁静默 warn，F-10 型）。"""
        e = _entry(
            "T0-MATRIX-VWAP-CEILING", "frozen", lives_in=[{"path": "docs/_working/t0_matrix/t0_ceiling_prereg_card.md"}]
        )
        errs = _inst_errs([e], live=True, root=tmp_path)
        assert any("CV-17" in x and "不在盘" in x for x in errs), errs

    def test_same_bytes_two_sources_is_red(self, tmp_path):
        p1 = tmp_path / "docs/_working/a/one_prereg.md"
        p2 = tmp_path / "docs/_working/b/two_prereg.md"
        body = "---\nstatus: frozen\n---\n\n# 同一份卡\n".encode()
        for p in (p1, p2):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(body)
        entries = [
            _entry("A-AA-01", "frozen", lives_in=[{"path": "docs/_working/a/one_prereg.md"}]),
            _entry("B-BB-01", "frozen", lives_in=[{"path": "docs/_working/b/two_prereg.md"}]),
        ]
        errs = _inst_errs(entries, live=True, root=tmp_path)
        assert any("CV-18" in x and "双真源" in x for x in errs), errs

    def test_card_id_form_is_enforced(self):
        e = _entry("小卡一号", "frozen")
        assert any("CV-03" in x and "形态非法" in x for x in _inst_errs([e]))

    def test_experiment_id_prefix_exclusive(self):
        e = _entry("A-AA-01", "frozen", experiment_id="EXP-A-AA-01")
        assert any("EXP-" in x for x in _inst_errs([e]))

    def test_instance_card_state_outside_loaded_vocabulary_is_red(self):
        """RC-24 登记面条目的 card_state 必须命中在册词表（值集动态装载，禁册内自造状态）。"""
        e = _entry("ZZ-AA-01", "frozen_ish")
        assert any("CV-02" in x and "ZZ-AA-01" in x for x in _inst_errs([e]))
        e2 = _entry("ZZ-AA-02", "frozen")
        assert not [x for x in _inst_errs([e2]) if "CV-02" in x]

    def test_instances_are_never_mutated(self):
        """校验器禁就地改状态：跑完判定后台账字节必须与输入一致。"""
        entries = copy.deepcopy(_PROPOSAL["card_entries"])
        before = yaml.safe_dump(entries, allow_unicode=True, sort_keys=True)
        _inst_errs(entries)
        assert yaml.safe_dump(entries, allow_unicode=True, sort_keys=True) == before


# ---------------------------------------------------------------------------
# CLI 契约：退出码三态（0/1/2）
# ---------------------------------------------------------------------------


def _cli(args: list[str]):
    cmd = [
        sys.executable,
        str(
            _REPO
            / "scripts"
            / "governance"
            / "d5_architecture"
            / "validators"
            / "validate_strategy_card_lifecycle_map.py"
        ),
        *args,
    ]
    return subprocess.run(
        cmd, cwd=str(_REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300
    )


class TestCli:
    def test_structure_only_exit_zero(self):
        r = _cli(["--structure-only", "--skip-live"])
        assert r.returncode == 0, r.stderr

    def test_full_face_exit_one_with_expected_reds(self):
        """真实台账面持续判红属预期行为（F-03/F-05/F-07/F-10），不是噪声，勿删判据凑绿。"""
        r = _cli(["--json"])
        assert r.returncode == 1
        out = yaml.safe_load(r.stdout)
        joined = "\n".join(out["errors"])
        for probe in ("CV-06", "CV-08", "CV-08B", "CV-10"):
            assert probe in joined, probe

    def test_missing_file_exit_two(self, tmp_path):
        assert _cli(["--map", str(tmp_path / "nope.yaml")]).returncode == 2

    def test_broken_yaml_exit_two(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("map_id: x\n  bad indent: [1,2\n", encoding="utf-8")
        assert _cli(["--map", str(p)]).returncode == 2

    def test_top_level_not_object_exit_two(self, tmp_path):
        p = tmp_path / "list.yaml"
        p.write_text("- a\n- b\n", encoding="utf-8")
        assert _cli(["--map", str(p)]).returncode == 2

    def test_unreachable_external_face_degrades_to_warn(self, tmp_path, monkeypatch):
        """裁定册不可达 ⇒ CV-09 降 warn，不得升级为 error（禁环境异常打死无辜提交）。"""
        empty = tmp_path / "repo"
        (empty / "docs/_working/map_build/fig15_cardlife").mkdir(parents=True)
        warns: list[str] = []
        errs = V.validate_structure(_GOOD, root=empty, warnings=warns, live=False, block=_PROPOSAL_BLOCK)
        assert isinstance(errs, list)
        assert not [e for e in errs if "不可达" in e]
