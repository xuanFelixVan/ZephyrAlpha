# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §strategy_card_lifecycle_map_gate
# [MODULE] tests.governance.commit_gates.test_strategy_card_lifecycle_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; yaml; copy; sys; pathlib;
#   zephyr.gov_enforcement.commit_gates.strategy_card_lifecycle_map_gate（_check）；
#   scripts.governance.d5_architecture.validators.validate_strategy_card_lifecycle_map（口径对照）
# [CONSUMERS] STRATEGY-CARD-LIFECYCLE-MAP 子台的能红能绿证据；MAP-ALIGNMENT 聚合台挂载回归
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图与坏锚块一律构造在 tmp_path（禁写 config/ 与提案件生产路径）；
#   断言点到具体子检查名，不接受"只判非空"；真图四个触发面必须各自放行（防触发面写错导致漏校）；
#   fail-closed 三条（校验器不可达 / 图 YAML 损坏 / 锚块不可装载）必须阻断
# [MODIFY-GUARD] 触发面清单变更须与 gate 的 _TRIGGER_FILES 同批，并回写 90 号规格 §8 与 91 号件
#   §host_migration_checklist
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""STRATEGY-CARD-LIFECYCLE-MAP 子台门禁测试（图15·状态机形态）。

蓝：真图在六个触发面各自放行；触发面外 skip；空清单 skip；反斜杠与绝对路径（生产形态）都能命中；
warn 不升级为阻断；本图不注册自己（只暴露 _check）。
红：坏图阻断且点名子检查；图 YAML 损坏 fail-closed；顶层非对象 fail-closed；校验器不可达
fail-closed；口径档案损坏 fail-closed；宿主词表读不到/宿主册无契约条目 fail-closed（registry 期）；
就地复活类改动在结构面被拦（终态出边）；禁边被删被拦；production 谎报被拦；旧字段别名被拦。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[4]
_VALIDATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "validators"
if str(_VALIDATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATORS_DIR))

import zephyr.gov_enforcement.commit_gates.map_family.strategy_card_lifecycle_map_gate as gate_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.map_family.strategy_card_lifecycle_map_gate import (  # noqa: E402
    _check,
)

_MAP_REL = "config/strategy_card_lifecycle_map.yaml"
_VALIDATOR_REL = "scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py"
_GENERATOR_REL = "scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py"
_ANCHORS_REL = "docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))


class _FakeGW:
    """最小 gateway 桩：_norm_rel 读 project_root（生产形态绝对路径用例用）。"""

    project_root = _REPO


def _write(tmp_path: Path, data, name: str = "strategy_card_lifecycle_map.yaml") -> Path:
    p = tmp_path / name
    text = data if isinstance(data, str) else yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 蓝队：真图必过 + 触发面分域正确
# ---------------------------------------------------------------------------


class TestBlue:
    def test_real_map_passes_on_every_trigger_face(self):
        """六个触发面各自都要放行真图（含宿主册与宿主词表——registry 期它们是装载点）。"""
        assert len(gate_mod._TRIGGER_FILES) == 6
        for rel in sorted(gate_mod._TRIGGER_FILES):
            passed, detail = _check(gateway=None, files=[rel])
            assert passed, f"{rel} 触发的好图被误拦: {detail}"

    def test_non_trigger_files_skip(self):
        passed, detail = _check(gateway=None, files=["src/zephyr/some_module.py"])
        assert passed and "skip" in detail

    def test_empty_files_skip(self):
        passed, detail = _check(gateway=None, files=[])
        assert passed and detail == ""

    def test_backslash_paths_hit_trigger_face(self):
        passed, detail = _check(gateway=None, files=["config\\strategy_card_lifecycle_map.yaml"])
        assert passed and "skip" not in detail

    def test_absolute_production_path_hits(self, monkeypatch, tmp_path):
        bad = copy.deepcopy(_GOOD)
        bad["transitions"][0]["verified_scope"] = "production"
        bad["states"][0]["verified_scope"] = "production"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, bad))
        passed, detail = _check(gateway=_FakeGW(), files=[str(_REPO / _MAP_REL)])
        assert not passed and "CV-DUAL" in detail

    def test_only_exposes_check(self):
        """净零纪律：本图不新增 gate 台，只暴露 _check，注册与 subs 挂载归总包。"""
        assert callable(_check)
        public = {n for n in vars(gate_mod) if n.endswith("_check") or n == "check"}
        assert public == {"_check"}

    def test_warnings_never_escalate(self, monkeypatch, tmp_path):
        """装载点声明与实际装载点不一致=随结论留痕，不阻断（禁把可用性耦合进地图门禁）。"""
        d = copy.deepcopy(_GOOD)
        d["anchor_block_origin"] = "docs/_working/map_build/fig15_cardlife/00_skeleton.md"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, detail


# ---------------------------------------------------------------------------
# 红队：每种坏都必须被拦且点名
# ---------------------------------------------------------------------------


class TestRed:
    def test_missing_top_key_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        del d["forbidden_edges"]
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "缺顶层必填键" in detail

    def test_forbidden_edge_deleted_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["forbidden_edges"] = [x for x in d["forbidden_edges"] if x["edge_id"] != "D15-X03"]
        d["counts"]["total_forbidden_edges"] = len(d["forbidden_edges"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "CV-13" in detail and "D15-X03" in detail

    def test_terminal_outgoing_edge_blocks(self, monkeypatch, tmp_path):
        """结构面先给"封卡就地复活"堵死合法通道：终态不得有出边。"""
        d = copy.deepcopy(_GOOD)
        t = next(x for x in d["transitions"] if x["transition_id"] == "D15-M06")
        t["from_state"] = ["sealed"]
        t["cross_instance"] = False
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "出边" in detail

    def test_bypassable_forbidden_edge_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        for tid in ("D15-M03", "D15-M06"):
            t = next(x for x in d["transitions"] if x["transition_id"] == tid)
            t["credential_required"] = "none"
            t["gated"] = False
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "可被绕过边规避" in detail

    def test_banned_alias_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["states"][1]["semantics_zh"] = "旧名回潮"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "CV-L0" in detail

    def test_counts_drift_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["counts"]["total_transitions"] = 99
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "CV-14" in detail

    def test_broken_yaml_fails_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, "map_id: x\n  broken: [1,2\n", "broken.yaml"))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "fail-closed" in detail

    def test_top_level_not_object_fails_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, "- a\n- b\n", "l.yaml"))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "顶层非对象" in detail

    def test_validator_unreachable_fails_closed(self, monkeypatch):
        def boom(*a, **k):
            raise RuntimeError("validator down")

        monkeypatch.setattr(sys, "modules", {**sys.modules})
        import validate_strategy_card_lifecycle_map as V

        monkeypatch.setattr(V, "validate_structure", boom)
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and ("结构校验异常" in detail or "加载失败" in detail)

    def test_anchor_block_unloadable_fails_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(gate_mod, "_ANCHORS_PATH", _write(tmp_path, "not: [valid\n", "anchors.yaml"))
        passed, detail = _check(gateway=None, files=[_ANCHORS_REL])
        assert not passed and "锚块提案件不可装载" in detail

    def test_anchor_block_empty_vocabulary_blocks(self, monkeypatch):
        """registry 期装载点=在册词表：宿主词表读不到=图无源，gate fail-closed 点名装载点。"""
        import validate_strategy_card_lifecycle_map as V

        monkeypatch.setattr(V, "_REGISTRY_VOCAB_REL", "docs/_working/map_build/fig15_cardlife/zz_absent_vocab.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "词表装载点未切" in detail

    def test_anchor_block_host_contract_entries_missing_blocks(self, monkeypatch):
        """宿主册无 CARD-* 契约条目（只扩枚举不回填）=实例面未落地，gate fail-closed。"""
        import validate_strategy_card_lifecycle_map as V

        monkeypatch.setattr(V, "_REGISTRY_HOST_REL", "docs/_working/map_build/fig15_cardlife/zz_absent_registry.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "无 CARD-* 契约条目" in detail

    def test_trigger_face_changes_require_revalidation(self):
        """触发面六件必须含口径档案与宿主两面（proposal 期档案是装载点，registry 期是分母真源）。"""
        assert _ANCHORS_REL in gate_mod._TRIGGER_FILES
        assert _GENERATOR_REL in gate_mod._TRIGGER_FILES
        assert gate_mod._HOST_REGISTRY_REL in gate_mod._TRIGGER_FILES
        assert gate_mod._HOST_VOCAB_REL in gate_mod._TRIGGER_FILES
        assert len(gate_mod._TRIGGER_FILES) == 6
