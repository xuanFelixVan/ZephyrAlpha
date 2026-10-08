# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §construction_workflow_map_gate
# [MODULE] tests.governance.commit_gates.test_construction_workflow_map_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; yaml; copy; sys;
#   zephyr.gov_enforcement.commit_gates.construction_workflow_map_gate;
#   config/construction_workflow_map.yaml（只读真源，坏图一律构造于 tmp 副本）
# [CONSUMERS] CONSTRUCTION-WORKFLOW-MAP gate 质量守卫（坏图必拦/好图必过/触发面四件分域/
#   fail-closed 四通道：图 YAML 损坏·顶层非对象·文件缺失·锚块提案件不可装载·校验器不可达）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 坏图用例全部构造于 tmp 副本（monkeypatch 替换 _MAP_PATH/_ANCHORS_PATH，
#   不碰生产路径、禁写 config/ 与 docs/_working/ 真件）；好图控制组=真实图必须通过；
#   gate 侧口径=live=False（磁盘实存/在册腿不入提交面），故红案全部取结构面违规；
#   形态照抄 test_dev_delivery_map_gate（图 11 母版红蓝先例）
# [MODIFY-GUARD] 本件是 gate 阻塞语义与 fail-closed 四通道的证据面：把红案改成"接受放行"、
#   或把 tmp 副本写回生产路径=放水/越界，须先改 gate 的触发面与阻塞口径再改本件
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CONSTRUCTION-WORKFLOW-MAP gate 红蓝对抗测试（图 14，形态=DEV-DELIVERY-MAP 母版先例）。

红队（必拦）：坏图（断边/未声明反向边/主序成环/计数漂移/缺总线号或自造号/🔨 环节宣
             production 的谎/built 无实查证据/旧字段别名残留/越域挂载/handoff 吞图 11 机制/
             gap 孤岛/anchor_source 非法）触发提交 → 阻断；
             图 YAML 损坏·顶层 list·空文件·真源缺失 → fail-closed；
             锚块提案件（91 号）不可装载/缺 step_anchors → fail-closed（派生链断=真源损坏）；
             校验器不可达 → fail-closed。
蓝队（必过）：真实图 + 四个触发面任一 → 放行；触发面外 → skip；反斜杠与生产形态绝对路径
             均命中触发面；anchor_source=policy（政策已嵌块未来态）时锚块装载腿整体跳过；
             anchor_block_origin 与装载点不一致=留痕不阻断（搬家不该打死提交）。
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

import zephyr.gov_enforcement.commit_gates.map_family.construction_workflow_map_gate as gate_mod  # noqa: E402
from zephyr.gov_enforcement.commit_gates.map_family.construction_workflow_map_gate import (  # noqa: E402
    _check,
)

_MAP_REL = "config/construction_workflow_map.yaml"
_VALIDATOR_REL = "scripts/governance/d5_architecture/validators/validate_construction_steps.py"
_GENERATOR_REL = "scripts/governance/d5_architecture/generators/generate_construction_workflow_map.py"
_ANCHORS_REL = "docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml"
_GOOD = yaml.safe_load((_REPO / _MAP_REL).read_text(encoding="utf-8"))


class _FakeGW:
    """最小 gateway 桩：_norm_rel 读 project_root（生产形态绝对路径用例用）。"""

    project_root = _REPO


def _write(tmp_path: Path, data, name: str = "construction_workflow_map.yaml") -> Path:
    p = tmp_path / name
    text = data if isinstance(data, str) else yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 蓝队：真图必过 + 触发面四件分域正确
# ---------------------------------------------------------------------------


class TestBlue:
    def test_real_map_passes_on_every_trigger_face(self):
        """四个真源触发面各自触发一次，真实图（17 环节+12 gap）必须放行。"""
        for rel in (_MAP_REL, _VALIDATOR_REL, _GENERATOR_REL, _ANCHORS_REL):
            passed, detail = _check(gateway=None, files=[rel])
            assert passed, f"{rel} 触发的好图被误拦: {detail}"

    def test_non_trigger_files_skip(self):
        passed, detail = _check(gateway=None, files=["src/zephyr/some_module.py"])
        assert passed and "skip" in detail

    def test_empty_files_skip(self):
        passed, detail = _check(gateway=None, files=[])
        assert passed and detail == ""

    def test_backslash_paths_hit_trigger_face(self):
        """Windows 反斜杠相对路径归一后必须命中触发面（否则坏图会被"没触发"放过）。"""
        passed, detail = _check(gateway=None, files=["config\\construction_workflow_map.yaml"])
        assert passed and "skip" not in detail

    def test_absolute_production_path_hits(self, monkeypatch, tmp_path):
        """生产形态=commit() 传绝对路径（gateway abspath）也必须命中并重校。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-06", "D14-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=_FakeGW(), files=[str(_REPO / _MAP_REL)])
        assert not passed and "不存在的节点" in detail

    def test_round_tripped_copy_passes(self, monkeypatch, tmp_path):
        """真图过一遍 YAML 再落 tmp 也必须绿（gate 不依赖手改注释/CWD/取时）。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, copy.deepcopy(_GOOD)))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, detail

    def test_anchor_origin_mismatch_only_warns(self, monkeypatch, tmp_path):
        """anchor_block_origin 声明与装载点不一致=留痕不阻断（搬走提案件不该打死提交）。"""
        d = copy.deepcopy(_GOOD)
        d["anchor_block_origin"] = "docs/_working/map_build/elsewhere/99_moved.yaml"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, detail

    def test_policy_anchor_source_skips_anchor_block_face(self, monkeypatch, tmp_path):
        """政策已嵌块（未来态）：锚块装载腿整体跳过，提案件坏了也不阻断本 commit。"""
        d = copy.deepcopy(_GOOD)
        d["anchor_source"] = "policy"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        monkeypatch.setattr(gate_mod, "_ANCHORS_PATH", tmp_path / "gone_proposal.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, detail


# ---------------------------------------------------------------------------
# 红队：坏图必拦（全部 tmp 副本，禁碰生产路径）
# ---------------------------------------------------------------------------


class TestRedMap:
    def test_dangling_edge_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-06", "D14-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "不存在的节点" in detail

    def test_undeclared_reverse_edge_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-13", "D14-03"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "未声明为反馈环的反向边" in detail

    def test_feedback_edge_making_cycle_blocks(self, monkeypatch, tmp_path):
        """回边混进主序把 DAG 连成环 ⇒ 必拦（回边只能由 feedback_loops 承载）。

        靶点选 D14-13->D14-03：主序里 03→…→13 已连通，加这一条即成环，且未被登记为反馈环。
        """
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-13", "D14-03"])
        d["counts"]["total_edges"] = len(d["edges"])  # 隔离单因：只留成环这一条
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "主序边成环" in detail

    def test_declared_feedback_edge_not_blocked(self, monkeypatch, tmp_path):
        """对照：同一条边显式声明进 feedback_loops+loops 台账 ⇒ 放行（声明通道有效）。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-13", "D14-03"])
        d["counts"]["total_edges"] = len(d["edges"])
        d["feedback_loops"].append({"from": "D14-13", "to": "D14-03", "note": "测试声明通道"})
        d["counts"]["total_feedback"] = len(d["feedback_loops"])
        d["loops"].append(
            {"loop_id": "T-TEST", "from": "D14-13", "to": "D14-03", "kind": "in_graph", "note_zh": "测试声明通道"}
        )
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert passed, detail

    def test_counts_drift_rejects_handedit(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["counts"]["total_nodes"] = 3
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "counts.total_nodes" in detail

    def test_prose_count_in_map_blocks(self, monkeypatch, tmp_path):
        """计数写进散文（CV-13 的文本腿，gate 侧纯文本零 IO 故在面上）。"""
        text = yaml.safe_dump(copy.deepcopy(_GOOD), allow_unicode=True, sort_keys=False)
        text = text.replace("name_zh: AI 施工升级流图", "name_zh: AI 施工升级流图 端到端 15 步")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, text))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "CV-13" in detail

    def test_missing_module_id_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D14-06")["module_id"] = None
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "CV-BUS" in detail and "D14-06" in detail

    def test_fabricated_module_id_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D14-07")["module_id"] = "FIG14-OWNER-MADE"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "非 MOD-* 形态" in detail

    def test_production_disguise_on_hammer_node_blocks(self, monkeypatch, tmp_path):
        """双轴冒充：🔨 环节改宣 production ⇒ 谎 + 计数两条必拦。"""
        d = copy.deepcopy(_GOOD)
        node = next(n for n in d["nodes"] if n["node_id"] == "D14-03")
        node["verified_scope"] = "production"
        node["exec_evidence"] = ["复跑 python scripts/governance/dummy_probe.py 观察在产"]
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "谎" in detail and "CV-DUAL 计数" in detail

    def test_built_without_evidence_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D14-09")["evidence"] = []
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "built 却 evidence 空" in detail

    def test_automated_without_exec_source_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        node = next(n for n in d["nodes"] if n["node_id"] == "D14-07")
        node["exec_source"] = None
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "automated 却无 exec_source" in detail

    def test_legacy_field_alias_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        node = next(n for n in d["nodes"] if n["node_id"] == "D14-04")
        node["mech_note_zh"] = node.pop("note_zh")
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "字段旧名残留 mech_note_zh" in detail

    def test_cross_domain_mount_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        next(n for n in d["nodes"] if n["node_id"] == "D14-09")["judgment_basis"] = ["因子A>"]
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "越域挂载" in detail

    def test_handoff_swallowing_fig11_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        node = next(n for n in d["nodes"] if n["node_id"] == "D14-15")
        node["gates"] = ["HELD-OVERLAP"]
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "handoff 节点禁登记 gates" in detail

    def test_orphan_gap_node_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["edges"] = [e for e in d["edges"] if "D14-G01" not in e]
        d["counts"]["total_edges"] = len(d["edges"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "gap 节点必须至少有一条边" in detail

    def test_illegal_anchor_source_blocks(self, monkeypatch, tmp_path):
        d = copy.deepcopy(_GOOD)
        d["anchor_source"] = "whisper"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "anchor_source 非法" in detail

    def test_block_detail_carries_node_and_edge_counts(self, monkeypatch, tmp_path):
        """阻断明细必须自证规模（node/edge/anchor_source），否则排障只能重跑校验器。"""
        d = copy.deepcopy(_GOOD)
        d["counts"]["total_edges"] = 999
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        # 规模与 anchor_source 从 _GOOD 现取（禁硬编码——CR-15 契约收缩 29/34→28/33 教训，
        # 2026-10-04 适配；anchor_source 随图演进 proposal→policy 现取化，2026-10-07 适配）
        n, e = len(_GOOD.get("nodes") or []), len(_GOOD.get("edges") or [])
        src = _GOOD.get("anchor_source")
        assert not passed and f"nodes={n}" in detail and f"edges={e}" in detail and f"anchor_source={src}" in detail


# ---------------------------------------------------------------------------
# 红队：fail-closed 四通道（真源损坏/装载断链/校验器不可达，一律阻断不许当 skip）
# ---------------------------------------------------------------------------


class TestRedFailClosed:
    def test_corrupt_yaml_fail_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, "nodes: [unclosed"))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "解析失败" in detail and "fail-closed" in detail

    def test_list_top_fail_closed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, "- a\n- b\n"))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "顶层非对象" in detail

    def test_empty_file_fail_closed(self, monkeypatch, tmp_path):
        """空图（被截断/清空的极端形态）=顶层非对象，同样 fail-closed。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, ""))
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "顶层非对象" in detail

    def test_map_file_missing_fail_closed(self, monkeypatch, tmp_path):
        """图真源整件缺失（被误删）→ fail-closed，不得当成 skip 放行。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", tmp_path / "no_such_map.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "解析失败" in detail

    def _proposal_universe(self, monkeypatch, tmp_path):
        """锚块 fail-closed 用例回到 proposal 宇宙（policy 态锚腿整体跳过，2026-10-07 适配）。"""
        d = copy.deepcopy(_GOOD)
        d["anchor_source"] = "proposal"
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))

    def test_anchor_block_corrupt_fail_closed(self, monkeypatch, tmp_path):
        """91 号提案件损坏：proposal 态下它是图的真源，读不出=派生链断，必拦。"""
        self._proposal_universe(monkeypatch, tmp_path)
        broken = tmp_path / "91_broken.yaml"
        broken.write_text("step_anchors: [unclosed", encoding="utf-8")
        monkeypatch.setattr(gate_mod, "_ANCHORS_PATH", broken)
        passed, detail = _check(gateway=None, files=[_ANCHORS_REL])
        assert not passed and "锚块提案件不可装载" in detail

    def test_anchor_block_missing_step_anchors_fail_closed(self, monkeypatch, tmp_path):
        self._proposal_universe(monkeypatch, tmp_path)
        empty = tmp_path / "91_empty.yaml"
        empty.write_text(yaml.safe_dump({"schema_version": "0.1", "step_anchors": []}), encoding="utf-8")
        monkeypatch.setattr(gate_mod, "_ANCHORS_PATH", empty)
        passed, detail = _check(gateway=None, files=[_ANCHORS_REL])
        assert not passed and "step_anchors" in detail

    def test_anchor_block_missing_file_fail_closed(self, monkeypatch, tmp_path):
        self._proposal_universe(monkeypatch, tmp_path)
        monkeypatch.setattr(gate_mod, "_ANCHORS_PATH", tmp_path / "no_91.yaml")
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "锚块提案件不可装载" in detail

    def test_validator_unreachable_fail_closed(self, monkeypatch, tmp_path):
        """校验器不可达（sys.modules 置 None 模拟 ImportError）→ fail-closed 阻断。"""
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, copy.deepcopy(_GOOD)))
        monkeypatch.setitem(sys.modules, "validate_construction_steps", None)
        passed, detail = _check(gateway=None, files=[_MAP_REL])
        assert not passed and "加载失败" in detail and "fail-closed" in detail

    def test_generator_face_triggers_and_blocks_bad_map(self, monkeypatch, tmp_path):
        """生成器路径（语义层规则变更）同样触发重校，坏图照拦。"""
        d = copy.deepcopy(_GOOD)
        d["edges"].append(["D14-06", "D14-NOPE"])
        monkeypatch.setattr(gate_mod, "_MAP_PATH", _write(tmp_path, d))
        passed, _ = _check(gateway=None, files=[_GENERATOR_REL])
        assert not passed


if __name__ == "__main__":  # pragma: no cover  直跑=冒烟（pytest 才是正式入口）
    sys.exit(pytest.main([__file__, "-q"]))
