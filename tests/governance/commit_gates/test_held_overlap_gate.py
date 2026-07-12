# [A_test] module_id: SRC-TST-2101 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-held_overlap_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §held-overlap-gate
# [MODULE] tests.test_held_overlap_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_held_overlap_gate.py — 搭便车防护门禁单测（HELD-OVERLAP，2026-06-30 治本）

权威依据：held_overlap_gate.py（make_held_overlap_gate）

测试组：
- TestNoConflict: 无冲突时 passed=True
- TestConflictBlocked: 目标文件被其他活跃 session 持有 → passed=False
- TestAllowOverlapEscape: allow_overlap=True 逃生通道放行
- TestRegistryExceptionSafe: other_held_files 异常安全降级为空集（不阻断 commit）
- TestGateSpecFields: gate_id / priority 字段正确
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.governance.commit_gates.held_overlap_gate import (
    make_held_overlap_gate,
)


def _make_gateway(
    project_root: Path,
    other_held: set[str] | None = None,
    raise_exc: Exception | None = None,
) -> MagicMock:
    """构造 mock gateway，模拟 _registry.other_held_files。

    Args:
        project_root: 项目根目录（gate 用 relative_to 显示相对路径）。
        other_held: other_held_files 返回的归一化绝对路径集合。
        raise_exc: 若非 None，other_held_files 抛此异常（测试安全降级）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    if raise_exc is not None:
        gw._registry.other_held_files.side_effect = raise_exc
    else:
        gw._registry.other_held_files.return_value = other_held or set()
    return gw


class TestNoConflict:
    """无冲突时放行。"""

    def test_no_conflict_passes(self, tmp_path):
        """目标文件不在 other_held 中 → passed=True。"""
        gw = _make_gateway(tmp_path, other_held=set())
        gate = make_held_overlap_gate()
        target = tmp_path / "a.py"
        target.touch()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestConflictBlocked:
    """目标文件被其他活跃 session 持有 → 阻断。"""

    def test_conflict_blocked(self, tmp_path):
        """目标文件在 other_held 中 → passed=False，detail 含搭便车防护说明。"""
        target = tmp_path / "a.py"
        target.touch()
        # other_held 用 resolve() 归一化（与 gate 内部 str(Path(f).resolve()) 对齐）
        gw = _make_gateway(tmp_path, other_held={str(target.resolve())})
        gate = make_held_overlap_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "搭便车防护" in detail
        assert "HELD_OVERLAP_VIOLATION" in detail
        assert "a.py" in detail  # 相对路径显示

    def test_partial_overlap_blocked(self, tmp_path):
        """多文件中部分被持有 → 阻断。"""
        a = tmp_path / "a.py"
        b = tmp_path / "b.py"
        a.touch()
        b.touch()
        gw = _make_gateway(tmp_path, other_held={str(a.resolve())})
        gate = make_held_overlap_gate()
        passed, detail = gate.check(
            gw, [str(a), str(b)], session_id="s1", allow_overlap=False,
        )
        assert passed is False
        assert "a.py" in detail


class TestAllowOverlapEscape:
    """allow_overlap=True 逃生通道放行。"""

    def test_escape_hatch_passes_even_on_conflict(self, tmp_path):
        """有冲突但 allow_overlap=True → 放行（逃生通道）。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_gateway(tmp_path, other_held={str(target.resolve())})
        gate = make_held_overlap_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=True,
        )
        assert passed is True
        assert detail == ""


class TestRegistryExceptionSafe:
    """other_held_files 异常安全降级为空集（不阻断 commit）。"""

    def test_exception_degrades_to_pass(self, tmp_path):
        """registry 读取异常 → other_held 降级为空集 → 无 overlap → 放行。"""
        target = tmp_path / "a.py"
        target.touch()
        gw = _make_gateway(
            tmp_path, raise_exc=RuntimeError("registry down"),
        )
        gate = make_held_overlap_gate()
        passed, detail = gate.check(
            gw, [str(target)], session_id="s1", allow_overlap=False,
        )
        assert passed is True
        assert detail == ""


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        """返回的 GateSpec 字段符合约定。"""
        spec = make_held_overlap_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "HELD-OVERLAP"
        assert spec.priority == 50  # 优先于大部分校验执行
