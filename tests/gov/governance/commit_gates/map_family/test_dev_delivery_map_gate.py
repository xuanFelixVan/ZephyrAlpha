# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §dev_delivery_map_gate
# [MODULE] tests.governance.commit_gates.test_dev_delivery_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; yaml; zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate
# [CONSUMERS] DEV-DELIVERY-MAP gate 质量守卫（坏图必拦/好图必过/触发面分域/fail-closed 双通道）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于 tmp 副本（monkeypatch 替换 _MAP_PATH，不碰生产路径、
#   禁写 config/ 与真 .runtime/commit_queue）；好图控制组=真实图必须通过；
#   形态照抄 test_strategy_factory_map_gate（图 9 母版红蓝先例）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DEV-DELIVERY-MAP gate 红蓝对抗测试（图 11，形态=FACTORY-MAP 母版先例）。

红队（必拦）：坏图（断边/built 无锚/冒充 verified）触发提交 → 阻断；YAML 损坏 → fail-closed；
             顶层非对象 → fail-closed；校验器不可达 → fail-closed；图真源缺失 → fail-closed。
蓝队（必过）：真实好图触发提交 → 放行；非触发面文件 → skip 放行；生成器真源变更 → 触发重校放行。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[5]
_VALIDATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "validators"
if str(_VALIDATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_VALIDATORS_DIR))

import zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate as gate_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate import _check  # noqa: E402

_MAP_REL = "config/dev_delivery_map.yaml"
_VALIDATOR_REL = "scripts/governance/d5_architecture/validators/validate_dev_delivery_map.py"
_GENERATOR_REL = "scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))


def _write_map(tmp_path: Path, data) -> Path:
    p = tmp_path / "dev_delivery_map.yaml"
    if isinstance(data, str):
        p.write_text(data, encoding="utf-8")
    else:
        p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


class TestBlue:
    """蓝队：好图必过+触发面分域正确。"""

    def test_real_map_passes(self):
        """真实图（骨架 §6 封顶 28 环节）触发提交 → 放行。"""
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, f"真实好图被误拦: {detail}"

    def test_non_trigger_files_skip(self):
        passed, detail = _check(gateway=None, files=["src/zephyr/some_module.py"])
        assert passed and "skip" in detail

    def test_empty_files_skip(self):
        passed, _ = _check(gateway=None, files=[])
        assert passed

    def test_generator_change_triggers_good_map(self):
        """生成器真源变更也触发重校（语义层规则同步收敛）——好图放行。"""
        passed, detail = _check(gateway=None, files=[_GENERATOR_REL])
        assert passed, f"生成器变更触发的重校误拦好图: {detail}"

    def test_validator_change_triggers_good_map(self):
        passed, detail = _check(gateway=None, files=[_VALIDATOR_REL])
        assert passed, f"校验器变更触发的重校误拦好图: {detail}"

    def test_backslash_paths_normalized(
        self,
    ):
        """Windows 反斜杠相对路径归一后命中触发面（不放行坏图）。"""
        passed, detail = _check(gateway=None, files=["config\\dev_delivery_map.yaml"])
        assert passed
        assert "skip" not in detail

    def test_absolute_path_triggers_and_blocks_bad_map(self, monkeypatch, tmp_path):
        """生产形态：commit() 传绝对路径必命中触发面（图 9 母版实弹教训同构）。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D11-C10", "D11-GHOST"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))

        class _FakeGW:  # 最小 gateway 桩：_norm_rel 读 project_root
            project_root = _REPO

        passed, detail = _check(gateway=_FakeGW(), files=[str(_REPO / _MAP_REL)])
        assert not passed
        assert "不存在的节点" in detail


class TestRed:
    """红队：坏图必拦+fail-closed（全部 tmp 副本，禁碰生产路径）。"""

    def test_dangling_edge_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D11-S01", "D11-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "不存在的节点" in detail

    def test_proposed_disguised_as_verified_blocks(self, monkeypatch, tmp_path):
        """冒充 verified（无 evidence）→ gate 必须阻断。"""
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D11-S05")["confidence"] = "verified"
        next(n for n in d["nodes"] if n["node_id"] == "D11-S05")["evidence"] = []
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "verified 必带 evidence" in detail

    def test_built_without_anchor_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D11-C01")["module_ref"] = None
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "module_ref 代码锚" in detail

    def test_missing_stage_blocks(self, monkeypatch, tmp_path):
        """抽掉契约环节（漏族=静默腐坏典型形态）→ 阻断并报缺环节。"""
        d = copy.deepcopy(_GOOD)
        d["nodes"] = [n for n in d["nodes"] if n["node_id"] != "D11-D04"]
        d["counts"]["total_nodes"] = len(d["nodes"])  # 同步 counts 以隔离出"缺环节"单因
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "缺环节" in detail

    def test_corrupt_yaml_fail_closed(self, monkeypatch, tmp_path):
        """YAML 语法损坏 → fail-closed 阻断（真源损坏须先修）。"""
        p = _write_map(tmp_path, "nodes: [unclosed")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", p)
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "解析失败" in detail

    def test_non_dict_top_fail_closed(self, monkeypatch, tmp_path):
        p = _write_map(tmp_path, "- a\n- b\n")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", p)
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "顶层非对象" in detail

    def test_map_file_missing_fail_closed(self, monkeypatch, tmp_path):
        """图真源整件缺失（被误删）→ fail-closed，不得当成 skip 放行。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", tmp_path / "no_such_map.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "解析失败" in detail

    def test_validator_unreachable_fail_closed(self, monkeypatch, tmp_path):
        """校验器不可达（sys.modules 置 None 模拟 ImportError）→ fail-closed 阻断。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, copy.deepcopy(_GOOD)))
        monkeypatch.setitem(sys.modules, "validate_dev_delivery_map", None)
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "加载失败" in detail and "fail-closed" in detail

    def test_generator_path_triggers_bad_map_blocks(self, monkeypatch, tmp_path):
        """生成器路径触发+坏图 → 阻断（规则收紧语义）。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D11-C10", "D11-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write_map(tmp_path, d))
        passed, _ = _check(gateway=None, files=[_GENERATOR_REL])
        assert not passed
