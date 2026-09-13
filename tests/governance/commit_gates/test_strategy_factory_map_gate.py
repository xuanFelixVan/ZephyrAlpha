# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §strategy_factory_map_gate
# [MODULE] tests.governance.commit_gates.test_strategy_factory_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; yaml; zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate
# [CONSUMERS] FACTORY-MAP gate 质量守卫（坏图必拦/好图必过/触发面分域）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于 tmp 副本（monkeypatch 替换 _MAP_PATH，不碰生产路径）；好图控制组=真实图必须通过
# [MODIFY-GUARD] 与 gate 同批演进（新增触发文件须同步用例）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FACTORY-MAP gate 红蓝对抗测试——学 test_alignment_gates_red_blue.py 的 TestRedDecisionMap 先例。

红队（必拦）：坏图（断边/缺字段/非法层位/built 无锚）触发提交 → 阻断；
             YAML 损坏 → fail-closed 阻断；顶层非对象 → 阻断。
蓝队（必过）：真实好图触发提交 → 放行；非触发面文件 → skip 放行。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
_VALIDATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "validators"
if str(_VALIDATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATORS_DIR))

import zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate as gate_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate import (  # noqa: E402
    make_strategy_factory_map_gate,
)

_MAP_REL = "config/strategy_production_map.yaml"
_VALIDATOR_REL = "scripts/governance/d5_architecture/validators/validate_strategy_production_map.py"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))


@pytest.fixture()
def gate():
    return make_strategy_factory_map_gate()


def _write_map(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "strategy_production_map.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


class TestBlue:
    """蓝队：好图必过+触发面分域正确。"""

    def test_real_map_passes(self, gate):
        """真实图（v0.2 结构稿）触发提交 → 放行。"""
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert passed, f"真实好图被误拦: {detail}"

    def test_non_trigger_files_skip(self, gate):
        """非触发面文件（普通 .py/config）→ skip 放行。"""
        passed, detail = gate.check(gateway=None, files=["src/zephyr/some_module.py"])
        assert passed
        assert "skip" in detail

    def test_empty_files_skip(self, gate):
        passed, _ = gate.check(gateway=None, files=[])
        assert passed

    def test_validator_change_triggers_good_map(self, gate):
        """校验器真源变更也触发（三方同步先例）——好图放行。"""
        passed, detail = gate.check(gateway=None, files=[_VALIDATOR_REL])
        assert passed, f"校验器变更触发的重校误拦好图: {detail}"

    def test_backslash_paths_normalized(self, gate):
        """Windows 反斜杠路径归一后命中触发面。"""
        passed, detail = gate.check(gateway=None, files=["config\\strategy_production_map.yaml"])
        assert passed
        assert "skip" not in detail


class TestRed:
    """红队：坏图必拦（tmp 副本 monkeypatch，先例=TestRedDecisionMap）。"""

    def test_dangling_edge_blocks(self, gate, monkeypatch, tmp_path):
        """断边（引用不存在节点）→ 阻断。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["FAC-E0", "FAC-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "不存在的节点" in detail

    def test_missing_top_key_blocks(self, gate, monkeypatch, tmp_path):
        """缺顶层必填键（laws）→ 阻断。"""
        d = copy.deepcopy(_GOOD)
        d.pop("laws")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "laws" in detail

    def test_invalid_stage_blocks(self, gate, monkeypatch, tmp_path):
        """非法层位（E99）→ 阻断。"""
        d = copy.deepcopy(_GOOD)
        _find(d, "FAC-E0")["stage"] = "E99"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "stage 非法" in detail

    def test_built_without_anchor_blocks(self, gate, monkeypatch, tmp_path):
        """built 节点无 module_ref 代码锚 → 阻断（批1 实战抓到过的真问题类型）。"""
        d = copy.deepcopy(_GOOD)
        _find(d, "FAC-E1A")["build_status"] = "built"
        _find(d, "FAC-E1A")["module_ref"] = None
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "module_ref" in detail

    def test_undeclared_backward_edge_blocks(self, gate, monkeypatch, tmp_path):
        """未声明反馈环的反向边（E9→E0）→ 阻断。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["FAC-E9", "FAC-E0"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "反向边" in detail

    def test_corrupt_yaml_fail_closed(self, gate, monkeypatch, tmp_path):
        """YAML 语法损坏 → fail-closed 阻断（真源损坏须先修）。"""
        p = tmp_path / "strategy_production_map.yaml"
        p.write_text("nodes: [unclosed", encoding="utf-8")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", p)
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "解析失败" in detail

    def test_non_dict_top_fail_closed(self, gate, monkeypatch, tmp_path):
        """顶层非对象（列表）→ fail-closed 阻断。"""
        p = tmp_path / "strategy_production_map.yaml"
        p.write_text("- a\n- b\n", encoding="utf-8")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", p)
        passed, detail = gate.check(gateway=None, files=[_MAP_REL])
        assert not passed
        assert "顶层非对象" in detail

    def test_validator_path_triggers_bad_map_blocks(self, gate, monkeypatch, tmp_path):
        """校验器路径触发+坏图 → 阻断（规则收紧语义）。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["FAC-E0", "FAC-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, _ = gate.check(gateway=None, files=[_VALIDATOR_REL])
        assert not passed


def _find(d: dict, node_id: str) -> dict:
    return next(n for n in d["nodes"] if n["node_id"] == node_id)
