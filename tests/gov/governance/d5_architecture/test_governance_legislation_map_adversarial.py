# [MODULE] tests.gov.governance.d5_architecture.test_governance_legislation_map_adversarial
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; copy; sys; pathlib;
#   scripts.governance.d5_architecture.validators.validate_governance_legislation_map
#   （validate_structure / check_prose_counts）；
#   scripts.governance.d5_architecture.generators.generate_governance_legislation_map
#   （build_document / read_ledger_counts 幂等实证）
# [CONSUMERS] 图16 校验器质量守卫（坏图必须被点名，判通过的尺必须先证明自己会红）；
#   GOVERNANCE-LEGISLATION-MAP gate 同源判据消费面
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于内存副本（copy.deepcopy，禁写生产路径，宪法运维红线6）；
#   红用例断言"校验器必须点名这一条具体语义"（CV 编号+对象名），不接受"只判非空"；
#   三攻击主证据=非法迁移红/幽灵状态红/裁定实例混入 nodes 红（裁定#486 施工批任务3 规格，
#   tmp 副本宇宙先红后绿留证）
# [MODIFY-GUARD] 本件是"校验器能红"的证据面：删用例或放宽成"只判非空"=放水，必须先改校验器判据再改本件
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=TEST-MOD-GOVERNANCE-TEST_GOVERNANCE_LEGISLATION_M | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""图16 治理立法流图校验器对抗测试（三攻击主证据+红蓝两组回炉）。

红组：非法迁移（终态出边）/幽灵状态（自造 proposed）/裁定实例混入 nodes/
禁边同对被合法边覆盖/缺整段/prose 写死计数/INV-1 超长/保险丝下限击穿。
蓝组：真图结构面零 error/live 面零 error（counts 账本现算对拍）/生成器幂等逐字节等/
两件源码零壁钟取时。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

pytest.importorskip("validate_governance_legislation_map")
pytest.importorskip("generate_governance_legislation_map")

import generate_governance_legislation_map as gen  # noqa: E402
import validate_governance_legislation_map as val  # noqa: E402

_REAL_MAP = yaml.safe_load((_REPO / "config" / "governance_legislation_map.yaml").read_text(encoding="utf-8"))


def _errs(data, live: bool = False) -> list[str]:
    return val.validate_structure(copy.deepcopy(data), root=_REPO, warnings=[], live=live)


def _find(d, section, key, value):
    for item in d[section]:
        if item.get(key) == value:
            return item
    raise AssertionError(f"{section} 未找到 {key}={value}")


# ---------------------------------------------------------------------------
# 红组：三攻击主证据（裁定#486 任务3 规格）
# ---------------------------------------------------------------------------


class TestThreeMainAttacks:
    def test_illegal_transition_red_then_green(self):
        """攻击一：非法迁移——终态 superseded 出边（撤销取代链）必须红；还原后绿。"""
        d = copy.deepcopy(_REAL_MAP)
        d["transitions"].append(
            {
                "transition_id": "D16-T99",
                "from_state": ["superseded"],
                "to_state": "active",
                "name_zh": "∅攻击边",
                "note_zh": "对抗注入：撤销取代链",
                "source_anchors": ["scripts/governance/next_ruling_id.py"],
            }
        )
        errs = _errs(d)
        assert any("CV-02" in e and "superseded" in e and "终态" in e for e in errs), errs
        assert not any("幽灵状态" in e for e in errs)
        assert _errs(_REAL_MAP) == [] or all("CV-05" not in e for e in _errs(_REAL_MAP))

    def test_ghost_state_red_then_green(self):
        """攻击二：幽灵状态——自造 'proposed'（总包令提示词禁自造，实测账本无此值）必须红。"""
        d = copy.deepcopy(_REAL_MAP)
        d["states"].append(
            {
                "state_id": "D16-S7",
                "value": "proposed",
                "name_zh": "幽灵 proposed",
                "terminal": False,
                "note_zh": "对抗注入：自造状态",
                "source_anchors": ["docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"],
            }
        )
        errs = _errs(d)
        assert any("CV-01" in e and "proposed" in e for e in errs), errs
        assert _errs(_REAL_MAP) == [] or all("幽灵" not in e for e in _errs(_REAL_MAP))

    def test_ruling_instance_in_nodes_red(self):
        """攻击三：裁定实例混入 nodes——把实例键 ruling_id 塞进 machinery 必须红（保险丝二）。"""
        d = copy.deepcopy(_REAL_MAP)
        d["machinery"].append(
            {
                "node_id": "D16-N2",
                "ruling_id": "裁定#486",
                "name_zh": "实例走私",
                "note_zh": "对抗注入：裁定实例当节点",
                "source_anchors": ["scripts/governance/next_ruling_id.py"],
            }
        )
        errs = _errs(d)
        assert any("CV-07" in e and "ruling_id" in e for e in errs), errs
        clean = [e for e in _errs(_REAL_MAP) if "CV-07" in e]
        assert clean == []


# ---------------------------------------------------------------------------
# 红组：结构判据逐条能红
# ---------------------------------------------------------------------------


class TestRedStructure:
    def test_missing_section_red(self):
        d = copy.deepcopy(_REAL_MAP)
        del d["forbidden_edges"]
        assert any("forbidden_edges" in e for e in _errs(d))

    def test_forbidden_pair_shadowed_by_legal_red(self):
        """禁边同对被合法边覆盖（判据自相矛盾）必须红。"""
        d = copy.deepcopy(_REAL_MAP)
        x2 = _find(d, "forbidden_edges", "edge_id", "D16-X2")
        x2["from_state"], x2["to_state"] = "active", "void"
        d["transitions"].append(
            {
                "transition_id": "D16-T98",
                "from_state": ["active"],
                "to_state": "void",
                "name_zh": "同对走私",
                "note_zh": "对抗注入",
                "source_anchors": ["scripts/governance/next_ruling_id.py"],
            }
        )
        errs = _errs(d)
        assert any("CV-02" in e and "D16-X2" in e and "同对" in e for e in errs), errs

    def test_transition_to_ghost_state_red(self):
        d = copy.deepcopy(_REAL_MAP)
        _find(d, "transitions", "transition_id", "D16-T7")["to_state"] = "retired_ish"
        assert any("CV-02" in e and "retired_ish" in e for e in _errs(d))

    def test_prose_counts_red(self):
        d = copy.deepcopy(_REAL_MAP)
        total = str(d["counts"]["entries_total"])
        d["laws"].append(f"散文走私：在册裁定共 {total} 条")
        assert any("prose_counts" in e and total in e for e in _errs(d))

    def test_inv1_length_red(self):
        d = copy.deepcopy(_REAL_MAP)
        _find(d, "states", "state_id", "D16-S2")["note_zh"] = "长" * 201
        assert any("CV-07" in e and "超长" in e for e in _errs(d))

    def test_node_floor_fuse_red(self):
        """保险丝结构化：有意义节点 < 12 必须红（裁定#486 ①结构下限）。"""
        d = copy.deepcopy(_REAL_MAP)
        d["machinery"] = d["machinery"][:2]
        errs = _errs(d)
        assert any("CV-06" in e and "保险丝" in e for e in errs), errs

    def test_machinery_ghost_node_red(self):
        d = copy.deepcopy(_REAL_MAP)
        d["machinery"].append(
            {
                "node_id": "D16-N99",
                "name_zh": "幽灵机构",
                "note_zh": "x",
                "source_anchors": ["scripts/governance/next_ruling_id.py"],
            }
        )
        assert any("CV-03" in e and "D16-N99" in e for e in _errs(d))

    def test_machinery_missing_anchor_red(self):
        d = copy.deepcopy(_REAL_MAP)
        _find(d, "machinery", "node_id", "D16-N3")["source_anchors"] = []
        assert any("CV-03" in e and "D16-N3" in e for e in _errs(d))


# ---------------------------------------------------------------------------
# 蓝组：真图钉面
# ---------------------------------------------------------------------------


class TestBlueRealMap:
    def test_real_map_structure_passes(self):
        assert _errs(_REAL_MAP) == []

    def test_real_map_live_counts_tie(self):
        """live 面：counts 与账本现算逐键相等（CV-05 对拍；账本漂移时本测红=提示重灌图）。"""
        errs = _errs(_REAL_MAP, live=True)
        assert errs == [], errs

    def test_generator_document_idempotent(self):
        counts = gen.read_ledger_counts()
        doc_a = yaml.safe_dump(gen.build_document(counts), allow_unicode=True, sort_keys=False, width=110)
        doc_b = yaml.safe_dump(
            gen.build_document(gen.read_ledger_counts()), allow_unicode=True, sort_keys=False, width=110
        )
        assert doc_a == doc_b

    def test_generators_and_validators_forbid_wall_clock(self):
        """零壁钟取时（RULE-SCHEMA-TZ）——剥离注释/docstring 后查代码面。"""
        import ast

        for path in (gen.__file__, val.__file__):
            tree = ast.parse(Path(path).read_text(encoding="utf-8"))
            code_calls = {
                ast.unparse(node.func) if isinstance(node, ast.Call) else ""
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
            }
            assert not any("datetime.now" in c or "time.time" in c for c in code_calls), path
