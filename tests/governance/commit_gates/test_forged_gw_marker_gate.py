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

P1-1 治本（2026-09-14 红蓝 v3 c224e15d63 实证）后语义重设计：
原 sess- 前缀正则对现行会话命名（solo_agent/xt3-*/st-*/factory-* 等）全盲 →
unparseable 保守放行 → 伪造标记三重畅通（红蓝 v3 S1.9：[GW:xt3-fake-session:
multi-domain] 经网关零拦截落库）。新语义：自身标记放行 / 外来标记全拦（env 逃生废除）。

测试组：
- TestNoGwMarkerPass: 无 [GW:标识符 标记 → 放行（文档性提及「[GW: 空格」亦放行）
- TestSelfMarkerPass: 全部标记 == 本 session（session_id kwarg）→ 放行（自身冗余留痕惯例）
- TestForeignMarkerBlocked: 非本 session 标记 → 阻断（env=1 也不放行——逃生废除）
- TestForeignRegisteredMarkerBlocked: 外来标记已注册（嫁祸）→ 仍阻断 ★归因污染向量
- TestNonSessPrefixForgedBlocked: c224e15d63 回归——非 sess- 前缀伪造标记（生产形态）
- TestFallbackRegisteredPass: 无 session_id kwarg + 全部已注册 → 放行（隔离调用兜底）
- TestFallbackUnregisteredBlocked: 无 session_id kwarg + 未注册 → 阻断（无 env 逃生）
- TestMissingCommitMsgPass: commit_message 缺失 → 放行
- TestMissingProjectRootPass: gateway.project_root 缺失（兜底路径）→ 放行
- TestRegistryExceptionSafe: SessionRegistry 异常 → 降级为未注册（保守阻断）
- TestGateSpecFields: gate_id / priority 字段正确
- TestSessionIdExtraction: _extract_session_id 广义标识符正则
- TestExtractAllSessionTokens: 多标记全量提取（去重排序）
- TestIsSessionRegistered: 注册表查询行为
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import (
    _extract_all_session_tokens,
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
    """无 [GW:标识符 标记 → 放行。"""

    def test_no_gw_marker_passes(self, tmp_path):
        """commit msg 无 [GW: → passed=True（non-GW commit 由 GATE-COMMIT-GW 兜底）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(gw, [], commit_message="feat: add new feature")
        assert passed is True
        assert "no [GW: session marker" in detail

    def test_doc_mention_with_space_passes(self, tmp_path):
        """「[GW: 标记」文档性提及（冒号后空格，非标识符）→ 放行（防误报）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="docs: 说明 [GW: 标记的生成规范",
        )
        assert passed is True
        assert "no [GW: session marker" in detail


class TestSelfMarkerPass:
    """全部标记 == 本 session → 放行（自身冗余留痕既有惯例）。"""

    def test_self_marker_passes(self, tmp_path):
        """[GW:solo_agent] 且 session_id=solo_agent → 放行（冗余但无害）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="feat: add\n\n[GW:solo_agent]",
        )
        assert passed is True
        assert "self-marker" in detail

    def test_self_flag_markers_pass(self, tmp_path):
        """用户按网关指引手写自身旗标留痕（[GW:sid:multi-domain] 等）→ 放行。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="feat: x [GW:solo_agent:multi-domain]\n[GW:solo_agent:overlap]",
        )
        assert passed is True
        assert "self-marker" in detail

    def test_self_marker_non_sess_prefix_passes(self, tmp_path):
        """现行命名（非 sess- 前缀）自身标记 → 放行（P1-1 治本不误伤既有惯例）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, _ = gate.check(
            gw, [], session_id="factory-bottleneck-20260913",
            commit_message="fix: y [GW:factory-bottleneck-20260913:multi-domain]",
        )
        assert passed is True


class TestForeignMarkerBlocked:
    """非本 session 标记 → 阻断（env=1 也不放行——逃生废除）。"""

    def test_foreign_marker_blocked(self, tmp_path, monkeypatch):
        """伪造标记 + env=1（原逃生通道）→ 仍阻断（env 废除，P1-1 治本）。"""
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="feat: add\n\n[GW:sess-fake-12345678]",
        )
        assert passed is False
        assert "FORGED-GW-MARKER" in detail
        assert "sess-fake-12345678" in detail

    def test_foreign_marker_blocked_without_env(self, tmp_path, monkeypatch):
        """伪造标记 + 无 env → 阻断。"""
        monkeypatch.delenv("ZEPHYR_COMMIT_GATEWAY", raising=False)
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="feat: add\n\n[GW:sess-fake-12345678]",
        )
        assert passed is False
        assert "FORGED-GW-MARKER" in detail

    def test_non_sess_prefix_forged_blocked(self, tmp_path):
        """c224e15d63 回归锁：非 sess- 前缀伪造标记（红蓝 v3 实弹样本）→ 阻断。

        原实现 sess- 正则提取恒 None → unparseable 保守放行 → 伪造畅通入库。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="test [GW:xt3-fake-session:multi-domain] forged marker probe",
        )
        assert passed is False
        assert "FORGED-GW-MARKER" in detail
        assert "xt3-fake-session" in detail

    def test_mixed_self_and_foreign_blocked(self, tmp_path):
        """自身 + 外来混合标记 → 阻断且 detail 列出外来标记。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(
            gw, [], session_id="solo_agent",
            commit_message="feat: x\n[GW:solo_agent]\n[GW:evil-session]",
        )
        assert passed is False
        assert "evil-session" in detail
        assert "solo_agent" in detail  # 本 session 上下文说明


class TestForeignRegisteredMarkerBlocked:
    """外来标记已注册（嫁祸已注册会话）→ 仍阻断。"""

    def test_framing_registered_session_blocked(self, tmp_path):
        """嫁祸攻击：手写 [GW:other-registered-session]（已注册）→ 阻断。

        归因污染向量：伪造他人标记使 abuse monitor 归因错位——
        P1-1 治本新语义：非本 session 标记无论注册与否一律阻断。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=True,
        ):
            passed, detail = gate.check(
                gw, [], session_id="solo_agent",
                commit_message="feat: x\n[GW:st-fingov-20260912]",
            )
        assert passed is False
        assert "FORGED-GW-MARKER" in detail
        assert "st-fingov-20260912" in detail


class TestFallbackRegisteredPass:
    """无 session_id kwarg（隔离调用）→ 注册表校验兜底。"""

    def test_all_registered_passes(self, tmp_path):
        """无 session_id kwarg + 全部标记已注册 → 放行。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=True,
        ):
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-test-12345678]")
        assert passed is True
        assert "registered" in detail

    def test_identifier_doc_mention_not_marked_passes(self, tmp_path):
        """无 session_id + [GW:fake-marker]（可提取标识符）但已注册 → 放行（兜底口径）。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=True,
        ):
            passed, _ = gate.check(gw, [], commit_message="feat: add\n\n[GW:fake-marker]")
        assert passed is True


class TestFallbackUnregisteredBlocked:
    """无 session_id kwarg + 未注册标记 → 阻断（无 env 逃生）。"""

    def test_unregistered_blocked_even_with_env(self, tmp_path, monkeypatch):
        """兜底路径未注册标记 + env=1 → 仍阻断（env 逃生全面废除）。"""
        monkeypatch.setenv("ZEPHYR_COMMIT_GATEWAY", "1")
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            return_value=False,
        ):
            passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-fake-12345678]")
        assert passed is False
        assert "FORGED-GW-MARKER" in detail

    def test_multi_token_partial_unregistered_blocked(self, tmp_path):
        """多标记部分未注册（「首个合法+次个伪造」绕过尝试）→ 阻断。"""
        gw = _make_gateway(tmp_path)
        gate = make_forged_gw_marker_gate()
        registered = {"sess-good-12345678"}
        with patch(
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate.is_session_registered",
            side_effect=lambda root, sid: sid in registered,
        ):
            passed, detail = gate.check(
                gw, [],
                commit_message="msg\n[GW:sess-good-12345678]\n[GW:sess-evil-87654321]",
            )
        assert passed is False
        assert "sess-evil-87654321" in detail


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
    """gateway.project_root 缺失（兜底路径）→ 放行。"""

    def test_missing_project_root_passes(self, tmp_path):
        """兜底路径（无 session_id kwarg）+ project_root=None → 放行（无法校验）。"""
        gw = _make_gateway(None)
        gate = make_forged_gw_marker_gate()
        passed, detail = gate.check(gw, [], commit_message="feat: add\n\n[GW:sess-test-12345678]")
        assert passed is True
        assert "project_root missing" in detail


class TestRegistryExceptionSafe:
    """SessionRegistry 异常 → 降级为未注册（保守阻断）。"""

    def test_registry_exception_blocks(self, tmp_path, monkeypatch):
        """SessionRegistry.get 抛异常 → _is_session_registered 返回 False → 阻断。"""
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
    """_extract_session_id 广义标识符正则（P1-1 治本口径）。"""

    def test_basic_marker(self):
        assert _extract_session_id("feat: add\n\n[GW:sess-abc123]") == "sess-abc123"

    def test_non_sess_prefix_marker(self):
        """现行会话命名（非 sess- 前缀）→ 正常提取（P1-1 治本核心口径）。"""
        assert _extract_session_id("feat: add\n\n[GW:solo_agent]") == "solo_agent"

    def test_hyphenated_session_name(self):
        assert _extract_session_id("msg\n[GW:xt3-fake-session:multi-domain]") == "xt3-fake-session"

    def test_overlap_marker(self):
        assert _extract_session_id("msg\n[GW:sess-abc123:overlap]") == "sess-abc123"

    def test_merge_marker(self):
        assert _extract_session_id("msg\n[GW:sess-abc123:merge]") == "sess-abc123"

    def test_no_marker_returns_none(self):
        assert _extract_session_id("feat: add new feature") is None

    def test_empty_msg_returns_none(self):
        assert _extract_session_id("") is None

    def test_none_msg_returns_none(self):
        assert _extract_session_id(None) is None

    def test_doc_mention_with_space_returns_none(self):
        """「[GW: 标记」（冒号后空格，文档性提及）→ None（不提取、放行）。"""
        assert _extract_session_id("docs: 说明 [GW: 标记规范") is None

    def test_multiple_markers_takes_first(self):
        """多个标记时取第一个（_extract_session_id 保留单提取语义）。"""
        msg = "msg\n[GW:sess-first]\n[GW:sess-second]"
        assert _extract_session_id(msg) == "sess-first"


class TestExtractAllSessionTokens:
    """_extract_all_session_tokens 多标记全量提取（去重排序）。"""

    def test_multiple_tokens_dedup_sorted(self):
        msg = "msg\n[GW:beta-session]\n[GW:alpha-session]\n[GW:beta-session:overlap]"
        assert _extract_all_session_tokens(msg) == ["alpha-session", "beta-session"]

    def test_flag_suffix_stripped(self):
        """[GW:sid:multi-domain] 提取 sid（冒号后缀剥离）。"""
        assert _extract_all_session_tokens("x [GW:solo_agent:multi-domain]") == ["solo_agent"]

    def test_empty_and_none(self):
        assert _extract_all_session_tokens("") == []
        assert _extract_all_session_tokens(None) == []
        assert _extract_all_session_tokens("no markers here") == []


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
