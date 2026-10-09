# [MODULE] tests.gov.governance.commit_gates.test_mass_deletion_bag_surface
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate
# [CONSUMERS] 增补令·物化域②质量守卫：REGISTRY-MASS-DELETION 入队预检袋面观测分支
# [INVARIANTS] 红证=主区 index 脏（他会话 WIP）时袋面判定不受扰（-0012：报 387 删实为
#   +56/−0 纯追加的幻影假阳性）；蓝证=[allow-mass-deletion] 标记照常放行
# [MODIFY-GUARD] 新建 2026-10-10 st-regsolo-20261010（增补令随批测试，tests/ 豁免 token）
# [TTL] permanent
"""REGISTRY-MASS-DELETION 袋面观测分支守卫（总统筹 2026-10-10 增补令·物化域②）。

入队预检传 bag_contents 时判定面=袋 diff（HEAD vs 袋内容），主区共享暂存区
（含他会话未落地 WIP）不再进入观测面；直提链不传参=行为零变更。
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (  # noqa: E402
    make_registry_mass_deletion_gate,
)

_REL = "docs/01_policies_and_standards/_registry/catalogs/demo_reg.yaml"

_HEAD = "title: t\nentries:\n- id: a\n- id: b\n"
_BAG_PURE_ADD = "title: t\nentries:\n- id: a\n- id: b\n- id: c\n"
_BAG_DROP = "title: t\nentries:\n- id: a\n"


class _RecordingGateway:
    """桩：记录 run_git 调用（验证袋面分支不碰 git diff --cached）；可注入主区脏 HEAD。"""

    def __init__(
        self, head_texts: dict[str, str], dirty_index_files: list[str], index_texts: dict[str, str] | None = None
    ):
        self._head = head_texts
        self._dirty = dirty_index_files
        self._index = index_texts or {}
        self.calls: list[list[str]] = []

    def run_git(self, cmd: list[str]):
        self.calls.append(list(cmd))
        if cmd[:3] == ["git", "diff", "--cached"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(self._dirty))
        if cmd[:2] == ["git", "show"] and cmd[2].startswith("HEAD:"):
            rel = cmd[2][len("HEAD:") :]

            class R:
                returncode = 0 if rel in self._head else 1
                stdout = self._head.get(rel, "")

            return R()
        if cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
            rel = cmd[2][1:]

            class RI:
                returncode = 0 if rel in self._index else 1
                stdout = self._index.get(rel, "")

            return RI()
        raise AssertionError(f"unexpected: {cmd}")


def test_bag_surface_ignores_dirty_main_index():
    """红证：主区 index 有他会话脏 WIP，袋面判定只看袋 diff——纯追加袋必过（-0012 假阳性根治）。"""
    gw = _RecordingGateway({_REL: _HEAD}, dirty_index_files=[_REL, "docs/other_session_wip.yaml"])
    gate = make_registry_mass_deletion_gate()
    ok, msg = gate.check(
        gw,
        [],
        session_id="st-x",
        commit_message="",
        bag_contents={_REL: _BAG_PURE_ADD},
    )
    assert ok is True, f"纯追加袋在脏 index 面必过（got: {msg}）"
    assert not any(c[:3] == ["git", "diff", "--cached"] for c in gw.calls), "袋面分支不得读主区暂存区"


def test_bag_surface_blocks_real_drop():
    """袋 diff 真删除仍必拦（观测面收窄不放松判据）。"""
    gw = _RecordingGateway({_REL: _HEAD}, dirty_index_files=[])
    gate = make_registry_mass_deletion_gate()
    ok, msg = gate.check(
        gw,
        [],
        session_id="st-x",
        commit_message="",
        bag_contents={_REL: _BAG_DROP},
    )
    assert ok is False and "净删" in msg


def test_bag_surface_marker_still_passes():
    """蓝证：[allow-mass-deletion] 标记在袋面分支照常放行（豁免语义零变更）。"""
    gw = _RecordingGateway({_REL: _HEAD}, dirty_index_files=[])
    gate = make_registry_mass_deletion_gate()
    ok, _ = gate.check(
        gw,
        [],
        session_id="st-x",
        commit_message="legal retire [allow-mass-deletion:合法退役对账在案reason]",
        bag_contents={_REL: _BAG_DROP},
    )
    assert ok is True


def test_no_bag_contents_keeps_legacy_surface():
    """直提链不传 bag_contents → 走既有 staged 面（行为零变更）。"""
    # index 陈旧版（1 条 vs HEAD 2 条）=幻影删除形态：legacy 面（他会话 WIP 占 index）照样拦
    gw = _RecordingGateway({_REL: _HEAD}, dirty_index_files=[_REL], index_texts={_REL: _BAG_DROP})
    gate = make_registry_mass_deletion_gate()
    ok, msg = gate.check(gw, [], session_id="st-x", commit_message="", bag_contents=None)
    assert ok is False, "legacy 面：index 中该册相对 HEAD 净删仍拦（零变更验证）"
