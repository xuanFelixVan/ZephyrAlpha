# [MODULE] tests.gov.governance.commit_gates.test_registry_yaml_parse_watch_extension
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate
# [CONSUMERS] C 件质量守卫：REGISTRY-YAML-PARSE watch 面 P0 扩面（六册）+投影 tamper 全档案生效
# [INVARIANTS] 全部用例 tmp 状态文件/桩 gateway（零主区零 PG）；红蓝双向=手改拦/生成器过；
#   独立成文件避让他会话 staged 的 test_registry_yaml_parse_gate.py WIP（共写禁令）
# [MODIFY-GUARD] 新建 2026-10-09 st-regsolo-20261010（热册单口写战役 C 件随批测试，tests/ 豁免 token）
# [TTL] permanent
"""REGISTRY-YAML-PARSE watch 面扩面守卫（裁定#502 战役 C 件）。

P0 七热册中六册进 watch（module_translation 随翻译轨改道 A2 同批上线）：
hot_registry_basic 档=parse+根键唯一；投影 tamper 判别对全档案生效——
已武装册 staged≠状态文件指纹必拦（手改无效），生成器重打后 staged==指纹必过。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import (  # noqa: E402
    _WATCH_FILES,
    make_registry_yaml_parse_gate,
)
from zephyr.shared.io.file_utils import content_sha256  # noqa: E402

_RULE = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"
_CAND = "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml"

_VALID_RULING = """module_id: REG-RULING-001
ttl: permanent
title: 裁定中央登记表
unique_key:
- ruling_id
entries:
- ruling_id: "裁定#502"
  title: t
"""


def test_watch_table_contains_p0_six():
    """六册在挂（module_translation 显式缓武装=A2 车道随翻译轨改道上线）。"""
    assert _WATCH_FILES[_RULE] == "hot_registry_basic"
    assert _WATCH_FILES[_CAND] == "hot_registry_basic"
    assert (
        _WATCH_FILES["docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"]
        == "hot_registry_basic"
    )
    assert (
        _WATCH_FILES["docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"]
        == "hot_registry_basic"
    )
    assert _WATCH_FILES["architecture_model/contracts/error_code_registry.yaml"] == "hot_registry_basic"
    assert "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml" not in _WATCH_FILES


def test_hot_registry_basic_duplicate_root_key_blocks():
    """basic 档结构断言生效：双根键必拦（PyYAML 静默取后者盲区）。"""
    dup = _VALID_RULING + "\nentries2_dup: []\nentries:\n- ruling_id: x\n"

    class GW:
        project_root = "."

        def run_git(self, cmd):
            if cmd[:3] == ["git", "diff", "--cached"]:
                return SimpleNamespace(returncode=0, stdout=_RULE)
            if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
                return SimpleNamespace(returncode=0, stdout=dup)
            raise AssertionError(f"unexpected: {cmd}")

    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(GW(), [], session_id=None)
    assert ok is False and "顶层根键重复" in msg


def _state_gateway(tmp_path: Path, staged_text: str):
    """桩 gateway：project_root=tmp（带状态文件）；staged 内容由调用方定。"""

    class GW:
        pass

    gw = GW()
    gw.project_root = str(tmp_path)

    def run_git(cmd):
        if cmd[:3] == ["git", "diff", "--cached"]:
            return SimpleNamespace(returncode=0, stdout=_RULE)
        if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
            return SimpleNamespace(returncode=0, stdout=staged_text)
        raise AssertionError(f"unexpected: {cmd}")

    gw.run_git = run_git
    state_dir = tmp_path / ".runtime" / "projection"
    state_dir.mkdir(parents=True, exist_ok=True)
    return gw, state_dir


def test_projection_tamper_blocks_hand_edit(tmp_path):
    """红证：已武装册手改一行 → staged≠状态指纹 → 必拦（tamper 对 basic 档生效）。"""
    rendered = _VALID_RULING
    hand_edited = rendered.replace("title: t", "title: 手改")
    gw, state_dir = _state_gateway(tmp_path, hand_edited)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps(
            {"registries": {"REG-RULING-001": {"registry_path": _RULE, "content_sha256": content_sha256(rendered)}}}
        ),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is False, "手改投影册必拦"
    assert "意图 API" in msg or "投影" in msg


def test_generator_rendered_diff_passes(tmp_path):
    """蓝证：生成器重打后 staged==状态指纹 → 必过（合法 render-sync 通道畅通）。"""
    rendered = _VALID_RULING
    gw, state_dir = _state_gateway(tmp_path, rendered)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps(
            {"registries": {"REG-RULING-001": {"registry_path": _RULE, "content_sha256": content_sha256(rendered)}}}
        ),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is True, f"生成器产物必过（got: {msg}）"


def test_unarmed_registry_fail_open(tmp_path):
    """未武装册（状态文件无本册条目）= fail-open 零行为（武装顺序自由，门不误伤）。"""
    gw, state_dir = _state_gateway(tmp_path, _VALID_RULING)
    (state_dir / "registry_projection_state.json").write_text(
        json.dumps({"registries": {"REG-OTHER-001": {"registry_path": "docs/x.yaml", "content_sha256": "ab"}}}),
        encoding="utf-8",
    )
    gate = make_registry_yaml_parse_gate()
    ok, msg = gate.check(gw, [], session_id=None)
    assert ok is True, f"未武装册零行为（got: {msg}）"
