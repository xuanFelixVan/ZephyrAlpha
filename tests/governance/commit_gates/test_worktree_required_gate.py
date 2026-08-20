# [A_test] module_id: MOD-GOV_worktree_required_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_worktree_required_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_WORKTREE_REQUIRED_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_worktree_required_gate.py — WORKTREE-REQUIRED 门禁单测

权威依据：worktree_required_gate.py（make_worktree_required_gate）

测试组（11 个）：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestEscapeHatches: allow_overlap=True / allow_non_worktree=True → 放行
- TestGradedBlocking:
  - worktree 内 → 放行
  - 非 worktree + 无其他 session → 放行（solo）
  - 非 worktree + 有其他 session → 阻断
- TestFailOpen:
  - get_current_worktree 异常 → 放行
  - list_active 异常 → 放行
- TestBlockingMessage: 阻断消息含逃生通道提示

注意：本 gate 不读 git diff，只读 gateway._get_worktree_manager() + gateway.registry.list_active()。
测试隔离：MagicMock 模拟 gateway，不触碰真实 worktree/session registry。
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.worktree_required_gate import (  # noqa: E402
    make_worktree_required_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


class _FakeSession:
    """模拟 SessionInfo——只有 session_id 属性即可。"""

    def __init__(self, session_id: str):
        self.session_id = session_id


def _make_gateway(
    wt_session=None,
    wt_raises=False,
    active_sessions=None,
    list_active_raises=False,
):
    """构造 mock gateway。

    Args:
        wt_session: get_current_worktree() 返回值（None=不在 worktree 内）
        wt_raises: get_current_worktree() 是否抛异常
        active_sessions: list_active() 返回值（list of _FakeSession）
        list_active_raises: list_active() 是否抛异常
    """
    gw = MagicMock()
    gw._get_worktree_manager = MagicMock()
    wt_mgr = MagicMock()
    if wt_raises:
        wt_mgr.get_current_worktree.side_effect = RuntimeError("wt detection down")
    else:
        wt_mgr.get_current_worktree.return_value = wt_session
    gw._get_worktree_manager.return_value = wt_mgr

    gw.registry = MagicMock()
    if list_active_raises:
        gw.registry.list_active.side_effect = RuntimeError("registry down")
    else:
        gw.registry.list_active.return_value = active_sessions or []
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_worktree_required_gate(), GateSpec)

    def test_gate_id(self):
        assert make_worktree_required_gate().gate_id == "WORKTREE-REQUIRED"

    def test_priority(self):
        assert make_worktree_required_gate().priority == 44


# ---------------------------------------------------------------------------
# TestEscapeHatches — 双逃生通道
# ---------------------------------------------------------------------------
class TestEscapeHatches:
    def test_allow_overlap_passes(self):
        gw = _make_gateway(wt_session=None, active_sessions=[_FakeSession("sess-other")])
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1", allow_overlap=True)
        assert passed
        assert msg == ""

    def test_allow_non_worktree_passes(self):
        gw = _make_gateway(wt_session=None, active_sessions=[_FakeSession("sess-other")])
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1", allow_non_worktree=True)
        assert passed
        assert msg == ""


# ---------------------------------------------------------------------------
# TestGradedBlocking — 分级阻断
# ---------------------------------------------------------------------------
class TestGradedBlocking:
    def test_in_worktree_passes(self):
        gw = _make_gateway(wt_session="sess-wt-1", active_sessions=[_FakeSession("sess-other")])
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed
        assert msg == ""

    def test_non_worktree_solo_passes(self):
        gw = _make_gateway(wt_session=None, active_sessions=[])
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed
        assert msg == ""

    def test_non_worktree_concurrent_blocked(self):
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[_FakeSession("sess-other-1"), _FakeSession("sess-other-2")],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert not passed
        assert "搭便车" in msg or "worktree" in msg

    def test_non_worktree_excludes_self_session(self):
        """list_active 含自己 session_id 时不应计为 'other'。"""
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[_FakeSession("sess-1")],  # 只有自己
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed
        assert msg == ""


# ---------------------------------------------------------------------------
# TestWorkerExclusion — #ARCH-RECONCILER-WORKTREE-RACE 治本
# reconciler worker（worker-{sha8}-{pid}）是 commit 下游产物，held_files 为空，
# 不应计入"其他活跃 session"导致非-worktree commit 被阻断。
# ---------------------------------------------------------------------------
class TestWorkerExclusion:
    def test_worker_only_session_passes(self):
        """仅 reconciler worker 活跃时，非-worktree commit 应放行（worker 无搭便车风险）。"""
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[_FakeSession("worker-0f12f1aa-20176")],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed
        assert msg == ""

    def test_multiple_workers_passes(self):
        """多个 worker 活跃、无真实 user session 时应放行。"""
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[
                _FakeSession("worker-0f12f1aa-20176"),
                _FakeSession("worker-bdf1a00f-21928"),
            ],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed
        assert msg == ""

    def test_worker_does_not_mask_real_concurrent_session(self):
        """worker + 真实 user session 同时活跃时仍应阻断（user session 计数，worker 排除）。"""
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[
                _FakeSession("worker-0f12f1aa-20176"),
                _FakeSession("sess-real-user"),
            ],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert not passed  # 真实 user session 触发阻断
        # 阻断消息应只含真实 user session，不含 worker
        assert "sess-real-user" in msg
        assert "worker-" not in msg


# ---------------------------------------------------------------------------
# TestFailOpen — 基础设施故障安全降级
# ---------------------------------------------------------------------------
class TestFailOpen:
    def test_worktree_detection_exception_passes(self):
        gw = _make_gateway(wt_raises=True, active_sessions=[_FakeSession("sess-other")])
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed  # worktree 检测异常 → 安全降级放行
        assert msg == ""

    def test_list_active_exception_passes(self):
        gw = _make_gateway(wt_session=None, list_active_raises=True)
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert passed  # list_active 异常 → 安全降级放行
        assert msg == ""


# ---------------------------------------------------------------------------
# TestBlockingMessage — 阻断消息含逃生通道提示
# ---------------------------------------------------------------------------
class TestBlockingMessage:
    def test_blocking_message_mentions_escape_hatch(self):
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[_FakeSession("sess-other")],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert not passed
        assert "allow_non_worktree=True" in msg or "--allow-non-worktree" in msg

    def test_blocking_message_mentions_other_sessions(self):
        gw = _make_gateway(
            wt_session=None,
            active_sessions=[_FakeSession("sess-other-99")],
        )
        passed, msg = make_worktree_required_gate().check(gw, [], session_id="sess-1")
        assert not passed
        assert "sess-other-99" in msg
