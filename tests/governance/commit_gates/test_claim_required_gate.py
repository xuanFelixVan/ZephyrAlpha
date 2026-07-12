# [A_test] module_id: SRC-TST-2103 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-claim_required_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §claim-required-gate
# [MODULE] tests.test_claim_required_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_claim_required_gate.py — claim_files 前置检查门禁单测（CLAIM-REQUIRED，2026-06-30 治本）

权威依据：claim_required_gate.py（make_claim_required_gate）

测试组：
- TestSessionUnregistered: session 未注册 → 放行（测试/内部调用安全降级）
- TestClaimedPasses: session 已注册 + 目标文件已 claim → 放行
- TestUnclaimedBlocked: session 已注册但目标文件未 claim → 阻断
- TestAllowOverlapEscape: allow_overlap=True 逃生通道放行
- TestGetSessionExceptionSafe: get_session 异常安全降级为放行
- TestGateSpecFields: gate_id / priority 字段正确
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.gov_enforcement.commit_gates.claim_required_gate import (
    make_claim_required_gate,
)


def _make_gateway(
    get_session_return=None,
    get_session_exc: Exception | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 _registry.get_session。

    Args:
        get_session_return: get_session 返回值（SessionInfo 或 None）。
        get_session_exc: 若非 None，get_session 抛此异常（测试安全降级）。
    """
    gw = MagicMock()
    if get_session_exc is not None:
        gw._registry.get_session.side_effect = get_session_exc
    else:
        gw._registry.get_session.return_value = get_session_return
    return gw


def _make_session_info(held_files: list[str]) -> MagicMock:
    """构造 mock SessionInfo，仅设置 held_files 字段（gate 只读此字段）。"""
    info = MagicMock()
    info.held_files = held_files
    return info


class TestSessionUnregistered:
    """session 未注册（get_session 返回 None）→ 放行。"""

    def test_unregistered_passes(self, tmp_path):
        """session 未注册 → info=None → 放行（测试/内部调用安全降级）。"""
        gw = _make_gateway(get_session_return=None)
        gate = make_claim_required_gate()
        target = tmp_path / "a.py"
        target.touch()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestClaimedPasses:
    """session 已注册 + 目标文件已 claim → 放行。"""

    def test_claimed_passes(self, tmp_path):
        """目标文件在 held_files 中 → 放行。"""
        target = tmp_path / "a.py"
        target.touch()
        info = _make_session_info([str(target)])
        gw = _make_gateway(get_session_return=info)
        gate = make_claim_required_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestUnclaimedBlocked:
    """session 已注册但目标文件未 claim → 阻断。"""

    def test_unclaimed_blocked(self, tmp_path):
        """目标文件不在 held_files 中 → passed=False。"""
        target = tmp_path / "a.py"
        target.touch()
        # session 只 claim 了 b.py，但要 commit a.py
        other = tmp_path / "b.py"
        other.touch()
        info = _make_session_info([str(other)])
        gw = _make_gateway(get_session_return=info)
        gate = make_claim_required_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "claim" in detail.lower()
        assert "a.py" in detail  # 绝对路径含 a.py 子串

    def test_partial_unclaimed_blocked(self, tmp_path):
        """多文件中部分未 claim → 阻断（列出未 claim 文件）。"""
        a = tmp_path / "a.py"
        b = tmp_path / "b.py"
        a.touch()
        b.touch()
        # session 只 claim 了 a.py，但要 commit a.py + b.py
        info = _make_session_info([str(a)])
        gw = _make_gateway(get_session_return=info)
        gate = make_claim_required_gate()
        passed, detail = gate.check(
            gw, [str(a), str(b)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "b.py" in detail  # b.py 未 claim


class TestAllowOverlapEscape:
    """allow_overlap=True 逃生通道放行。"""

    def test_escape_hatch_passes_even_unclaimed(self, tmp_path):
        """未 claim 但 allow_overlap=True → 放行（逃生通道）。"""
        target = tmp_path / "a.py"
        target.touch()
        info = _make_session_info([])  # 空 held_files
        gw = _make_gateway(get_session_return=info)
        gate = make_claim_required_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=True,
        )
        assert passed is True
        assert detail == ""


class TestGetSessionExceptionSafe:
    """get_session 异常安全降级为放行（registry 故障不应卡死 commit 工作流）。"""

    def test_exception_degrades_to_pass(self, tmp_path):
        """registry 读取异常 → 放行。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_gateway(get_session_exc=RuntimeError("registry down"))
        gate = make_claim_required_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        """返回的 GateSpec 字段符合约定。"""
        spec = make_claim_required_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "CLAIM-REQUIRED"
        assert spec.priority == 40  # 优先于 HELD-OVERLAP(50)，先检查 claim
