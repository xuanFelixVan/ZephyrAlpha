# [A_test] module_id: MOD-GOV_forged_gw_marker_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_forged_gw_marker_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_forged_gw_marker_gate.py — Forged GW Marker 前置检测门禁单测（#ARCH-PREVENTABILITY-LAYER-001 Phase 2）

权威依据：forged_gw_marker_gate.py（make_forged_gw_marker_gate）

测试组：
- TestNoGwMarkerPass: commit msg 无 [GW: 标记 → 放行（non-GW commit 由 GATE-COMMIT-GW 兜底）
- TestRegisteredSessionPass: [GW:sess-xxx] session_id 已注册 → 放行（合法 GW commit）
- TestUnregisteredSessionWithEnvPass: session_id 未注册 + ZEPHYR_COMMIT_GATEWAY=1 env → 放行（逃生通道）
- TestForgedMarkerBlocked: session_id 未注册 + 无 env → 阻断（forged_gw_marker）
- TestUnparseableSessionIdPass: [GW: 标记但 session_id 无法解析 → 保守放行
- TestMissingCommitMsgPass: commit_message 缺失 → 放行（其他 gate 已检查）
- TestMissingProjectRootPass: gateway.project_root 缺失 → 放行
- TestRegistryExceptionSafe: SessionRegistry 异常 → 降级为未注册（保守阻断）
- TestGateSpecFields: gate_id / priority 字段正确
- TestSessionIdExtraction: _extract_session_id 正则正确（多种标记格式）
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import (
    _extract_session_id,
    _is_session_registered,
    make_forged_gw_marker_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec


def _make_gateway(project_root: Path | None = None) -> MagicMock:
    """构造 mock gateway。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


class TestNoGwMarkerPass:
    """commit msg 无 [GW: 标记 → 放行。"""

    def test_no_gw_marker_passes(self, tmp_path):
        """commit msg 无 [GW: → passed=True（non-GW commit 由 GATE-COMMIT-GW 兜底）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(gw, [], commit_message="feat: add new feature")
        assert passed is True
        assert "no [GW: marker" in detail


class TestRegisteredSessionPass:
    """[GW:sess-xxx] session_id 已注册 → 放行（合法 GW commit）。"""

    def test_registered_session_passes(self, tmp_path):
        """session_id 在 SessionRegistry 中 → passed=True。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=True,
        ):
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-test-12345678]")
        assert passed is True
        assert "session registered" in detail


class TestUnregisteredSessionWithEnvPass:
    """session_id 未注册 + ZEPHYR_COMMIT_GATEWAY=1 env → 放行（逃生通道）。"""

    def test_unregistered_with_env_passes(self, tmp_path, monkeypatch):
        """session_id 未注册但 env=1 → passed=True（GW 内部逃生通道）。"""
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=False,
        ):
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-fake-12345678]")
        assert passed is True
        assert "emergency escape" in detail


class TestForgedMarkerBlocked:
    """session_id 未注册 + 无 env → 阻断（forged_gw_marker）。"""

    def test_forged_marker_blocked(self, tmp_path, monkeypatch):
        """session_id 未注册 + 无 env → passed=False（intentional fraud）。"""
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=False,
        ):
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-fake-12345678]")
        assert passed is False
        assert "FORGED-GW-MARKER" in detail
        assert "sess-fake-12345678" in detail


class TestUnparseableSessionIdPass:
    """[GW: 标记但 session_id 无法解析 → 保守放行。"""

    def test_unparseable_session_id_passes(self, tmp_path):
        """[GW: 标记但无 sess- 前缀 → passed=True（保守放行）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        # [GW: 但无 sess- 前缀，_SESSION_ID_RE 不匹配
        passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:fake-marker]")
        assert passed is True
        assert "unparseable" in detail


class TestMissingCommitMsgPass:
    """commit_message 缺失 → 放行。"""

    def test_missing_commit_msg_passes(self, tmp_path):
        """commit_message 缺失 → passed=True（其他 gate 已检查）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(gw, [], commit_message=None)
        assert passed is True
        assert "missing" in detail


class TestMissingProjectRootPass:
    """gateway.project_root 缺失 → 放行。"""

    def test_missing_project_root_passes(self, tmp_path):
        """gateway.project_root=None → passed=True（无法校验，保守放行）。"""
        gw = _make_gateway(None)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-test-12345678]")
        assert passed is True
        assert "project_root missing" in detail


class TestRegistryExceptionSafe:
    """SessionRegistry 异常 → 降级为未注册（保守阻断）。"""

    def test_registry_exception_blocks(self, tmp_path, monkeypatch):
        """SessionRegistry.get 抛异常 → _is_session_registered 内部 try/except 返回 False → 阻断。"""
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)

        # patch SessionRegistry 让其 get_session() 抛异常
        # _is_session_registered 内部 try/except 会捕获并返回 False（保守阻断）
        # 注：mock get_session（非 .get）——SessionRegistry 真实 API 是 get_session，
        # 原 .get 调用是 bug（#7 修复：forge_gw_marker_gate._is_session_registered）
        with patch("zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.SessionRegistry") as mock_reg:
            mock_reg.return_value.get_session.side_effect = RuntimeError("registry corrupted")
            gw = _make_gateway(tmp_path)
            gate = make_forged_gw_marker_gate()
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-test-12345678]")
        assert passed is False
        assert "FORGED-GW-MARKER" in detail


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_is_forged_gw_marker(self):
        gate = make_forged_gw_marker_gate()
        assert gate.gate_id == "FORGED-GW-MARKER"

    def test_priority_is_29(self):
        """priority=29 早于 DIRECTORY-CONTRACT=30 和 SESSION-REQUIRED=31。"""
        gate = make_forged_gw_marker_gate()
        assert gate.priority == 29

    def test_gate_is_gate_spec_instance(self):
        gate = make_forged_gw_marker_gate()
        assert isinstance(gate, GateSpec)


class TestSessionIdExtraction:
    """_extract_session_id 正则正确（多种标记格式）。"""

    def test_basic_marker(self):
        assert _extract_session_id("feat: add\n\n[GW:sess-abc123]") == "sess-abc123"

    def test_overlap_marker(self):
        assert _extract_session_id("msg\n[GW:sess-abc123:overlap]") == "sess-abc123"

    def test_auto_marker(self):
        assert _extract_session_id("msg\n[GW:sess-abc123:auto]") == "sess-abc123"

    def test_merge_marker(self):
        assert _extract_session_id("msg\n[GW:sess-abc123:merge]") == "sess-abc123"

    def test_no_marker_returns_none(self):
        assert _extract_session_id("feat: add new feature") is None

    def test_empty_msg_returns_none(self):
        assert _extract_session_id("") is None

    def test_none_msg_returns_none(self):
        assert _extract_session_id(None) is None

    def test_multiple_markers_takes_first(self):
        """多个标记时取第一个（与 shell head -1 对齐）。"""
        msg = "msg\n[GW:sess-first]\n[GW:sess-second]"
        assert _extract_session_id(msg) == "sess-first"

    def test_no_sess_prefix_returns_none(self):
        """[GW: 但无 sess- 前缀 → None。"""
        assert _extract_session_id("msg\n[GW:fake-marker]") is None


class TestIsSessionRegistered:
    """_is_session_registered 行为测试。"""

    def test_registered_session_returns_true(self, tmp_path):
        """已注册 session_id → True（用真实 SessionRegistry mock）。"""
        with patch("zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.SessionRegistry") as mock_reg:
            mock_reg.return_value.get_session.return_value = MagicMock()
            result = _is_session_registered(tmp_path, "sess-test-12345678")
        assert result is True

    def test_unregistered_session_returns_false(self, tmp_path):
        """未注册 session_id → False。"""
        with patch("zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.SessionRegistry") as mock_reg:
            mock_reg.return_value.get_session.return_value = None
            result = _is_session_registered(tmp_path, "sess-test-12345678")
        assert result is False

    def test_registry_exception_returns_false(self, tmp_path):
        """SessionRegistry 异常 → False（保守阻断）。"""
        with patch("zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.SessionRegistry") as mock_reg:
            mock_reg.return_value.get_session.side_effect = RuntimeError("corrupted")
            result = _is_session_registered(tmp_path, "sess-test-12345678")
        assert result is False
