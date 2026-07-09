# [A_test] module_id: SRC-TST-2205 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-session_required_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_session_required_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_session_required_gate.py — SESSION-REQUIRED 门禁单测

权威依据：session_required_gate.py（make_session_required_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestReservedIds: _RESERVED_SESSION_IDS 成员/类型
- TestGatewayIntegration: mock gateway._registry
  - allow_overlap=True → 放行（逃生通道）
  - session_id 为空/unknown/none/null → 阻断
  - session_id 未注册（get_session 返回 None）→ 阻断
  - session_id 已注册 → 放行
  - get_session 异常 → fail-open 放行

注意：本 gate 不读 git diff，只读 gateway._registry.get_session(session_id)。
测试隔离：MagicMock 模拟 gateway._registry，不触碰真实 session registry。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.session_required_gate import (  # noqa: E402
    _RESERVED_SESSION_IDS,
    make_session_required_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_gateway(session_info=None, get_session_raises=False):
    """构造 mock gateway——_registry.get_session 返回 session_info 或抛异常。"""
    gw = MagicMock()
    gw._registry = MagicMock()
    if get_session_raises:
        gw._registry.get_session.side_effect = RuntimeError("registry down")
    else:
        gw._registry.get_session.return_value = session_info
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_session_required_gate(), GateSpec)

    def test_gate_id(self):
        assert make_session_required_gate().gate_id == "SESSION-REQUIRED"

    def test_priority(self):
        assert make_session_required_gate().priority == 30


# ---------------------------------------------------------------------------
# TestReservedIds — _RESERVED_SESSION_IDS 集合
# ---------------------------------------------------------------------------
class TestReservedIds:
    def test_is_frozenset(self):
        assert isinstance(_RESERVED_SESSION_IDS, frozenset)

    def test_includes_empty(self):
        assert "" in _RESERVED_SESSION_IDS

    def test_includes_unknown(self):
        assert "unknown" in _RESERVED_SESSION_IDS

    def test_includes_none(self):
        assert "none" in _RESERVED_SESSION_IDS

    def test_includes_null(self):
        assert "null" in _RESERVED_SESSION_IDS

    def test_does_not_include_valid_prefix(self):
        assert "sess-123" not in _RESERVED_SESSION_IDS


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_allow_overlap_passes(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="", allow_overlap=True
        )
        assert passed
        assert msg == ""

    def test_empty_session_id_blocked(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(gw, [], session_id="")
        assert not passed
        assert "session_id" in msg or "session_worktree_start" in msg

    def test_unknown_session_id_blocked(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="unknown"
        )
        assert not passed
        assert "unknown" in msg

    def test_none_session_id_blocked(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(gw, [], session_id="none")
        assert not passed
        assert "none" in msg

    def test_null_session_id_blocked(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(gw, [], session_id="null")
        assert not passed
        assert "null" in msg

    def test_unregistered_session_blocked(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="sess-123"
        )
        assert not passed
        assert "sess-123" in msg
        assert "未注册" in msg

    def test_registered_session_passes(self):
        info = {"session_id": "sess-123"}
        gw = _make_gateway(session_info=info)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="sess-123"
        )
        assert passed
        assert msg == ""

    def test_registry_exception_passes(self):
        gw = _make_gateway(get_session_raises=True)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="sess-123"
        )
        assert passed  # registry 故障安全降级放行
        assert msg == ""

    def test_blocking_message_mentions_escape_hatch(self):
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(gw, [], session_id="")
        assert not passed
        assert "allow_overlap=True" in msg

    def test_default_session_id_empty_blocked(self):
        gw = _make_gateway(session_info=None)
        # 不传 session_id -> 默认 ""
        passed, msg = make_session_required_gate().check(gw, [])
        assert not passed

    def test_reserved_checked_before_registry(self):
        # reserved session_id 应在调用 registry 前阻断——registry 不应被调用
        gw = _make_gateway(session_info=None)
        passed, msg = make_session_required_gate().check(
            gw, [], session_id="unknown"
        )
        assert not passed
        gw._registry.get_session.assert_not_called()
