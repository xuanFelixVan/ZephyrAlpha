# [A_test] module_id: SRC-TST-2095 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-arch_reference_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §arch-reference-gate
# [MODULE] tests.test_arch_reference_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_arch_reference_gate.py — #ARCH-NNN 悬空引用检测门禁单测（ARCH-REFERENCE）

权威依据：arch_reference_gate.py（make_arch_reference_gate）

测试组：
- TestArchRefBlocked: 新增未登记 #ARCH-NNN 引用 → 阻断
- TestRegisteredRefPasses: 合法已登记 #ARCH-NNN 引用 → 通过
- TestNoRefPasses: 无 #ARCH-NNN 引用 → 通过
- TestFailClosedNoRegistry: registry 缺失 → 阻断（fail-closed）
- TestTestExempt: tests/ 下文件豁免 → 通过
- TestIncrementalOnly: HEAD 已有引用 → 通过（增量检测不阻断历史）
- TestGateSpecFields: gate_id / priority 字段正确
- TestMultiSegmentRef: 多段式域前缀（#ARCH-GOV-SHIM-001 等）检测（2026-07-17 治本 ARCH-GOV-SHIM-001 漏检）
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.arch_reference_gate import (
    make_arch_reference_gate,
)


# 测试用 registry YAML：含 #ARCH-008 / #ARCH-019 / #ARCH-GOV-SHIM-001，不含 #ARCH-999
_REGISTRY_YAML = """\
module_id: REG-ARCH-ISSUE-001
entries:
  - issue_id: '#ARCH-008'
    title: test issue 008
    status: open
  - issue_id: '#ARCH-019'
    title: test issue 019
    status: decided
  - issue_id: '#ARCH-GOV-SHIM-001'
    title: test multi-segment issue
    status: decided
"""

# registry 在 project_root 下的相对路径（对标 arch_reference_gate._REGISTRY_REL）
_REGISTRY_REL = (
    "docs/01_policies_and_standards/_registry/catalogs/"
    "architecture_issue_registry.yaml"
)


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway，仅需 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _write_registry(project_root: Path) -> None:
    """在 project_root 下写入测试用 registry YAML。"""
    registry_path = project_root / _REGISTRY_REL
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(_REGISTRY_YAML, encoding="utf-8")


class TestArchRefBlocked:
    """新增未登记 #ARCH-NNN 引用 → 阻断。"""

    def test_dangling_arch_ref_blocked(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "ARCH_REFERENCE_VIOLATION" in detail
        assert "999" in detail


class TestRegisteredRefPasses:
    """合法已登记 #ARCH-NNN 引用 → 通过。"""

    def test_registered_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-008 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed


class TestNoRefPasses:
    """无 #ARCH-NNN 引用 → 通过。"""

    def test_no_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# no references here\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed


class TestFailClosedNoRegistry:
    """registry 缺失 → 阻断（fail-closed）。"""

    def test_no_registry_blocked(self, tmp_path):
        # 不创建 registry
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-008\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "fail-closed" in detail.lower() or "not found" in detail.lower()


class TestTestExempt:
    """tests/ 下文件豁免 → 通过（即使含未登记引用）。"""

    def test_tests_dir_exempt(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        target = tests_dir / "test_something.py"
        target.write_text("# see #ARCH-999\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # tests/ 豁免，不检测


class TestIncrementalOnly:
    """HEAD 已有引用 → 通过（增量检测不阻断历史）。"""

    def test_existing_ref_not_blocked(self, tmp_path, monkeypatch):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-999\n", encoding="utf-8")

        # mock _get_head_content 返回含 #ARCH-999 的 HEAD 版本（历史已有此引用）
        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as mod

        monkeypatch.setattr(
            mod, "_get_head_content", lambda pr, rel: "# see #ARCH-999\n"
        )

        passed, detail = gate.check(gw, [str(target)])
        assert passed  # 历史悬空引用不阻断


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id(self):
        gate = make_arch_reference_gate()
        assert gate.gate_id == "ARCH-REFERENCE"

    def test_priority(self):
        gate = make_arch_reference_gate()
        assert gate.priority == 75


class TestMultiSegmentRef:
    """多段式域前缀（#ARCH-GOV-SHIM-001 等）检测。

    治本 ARCH-GOV-SHIM-001 漏检（2026-07-17）：旧正则
    ``#ARCH-([A-Z]+-\\d+|\\d+)`` 只匹配两段式（#ARCH-CH-007）和纯数字（#ARCH-008），
    三段式 #ARCH-GOV-SHIM-001 漏检导致未登记编号可绕过门禁。
    扩展为 ``#ARCH-([A-Z]+(?:-[A-Z]+)*-\\d+|\\d+)`` 支持任意段数域前缀。
    """

    def test_unregistered_multi_segment_blocked(self, tmp_path):
        """新增未登记三段式 #ARCH-GOV-SHIM-999 引用 → 阻断（核心治本点）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-GOV-SHIM-999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "ARCH_REFERENCE_VIOLATION" in detail
        assert "GOV-SHIM-999" in detail

    def test_registered_multi_segment_passes(self, tmp_path):
        """已登记三段式 #ARCH-GOV-SHIM-001 引用 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-GOV-SHIM-001 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed

    def test_four_segment_supported(self, tmp_path):
        """四段式 #ARCH-A-B-C-001 未登记 → 阻断（验证任意段数支持）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-A-B-C-001 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "A-B-C-001" in detail

    def test_two_segment_still_works(self, tmp_path):
        """两段式 #ARCH-CH-999 未登记 → 阻断（验证向后兼容）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-CH-999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "CH-999" in detail

    def test_pure_number_still_works(self, tmp_path):
        """纯数字 #ARCH-999 未登记 → 阻断（验证纯数字向后兼容）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "999" in detail

    def test_no_digit_suffix_not_matched(self, tmp_path):
        """无数字后缀的 #ARCH-GOV-SHIM 不被正则匹配 → 通过（正则要求尾部数字）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        # #ARCH-GOV-SHIM 无尾部数字，正则不匹配，视为无引用 → 通过
        target.write_text("# see #ARCH-GOV-SHIM for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed
