# [A_test] module_id: MOD-GOV_arch_reference_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ARCH_REFERENCE_GATE | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §arch-reference-gate
# [MODULE] tests.test_arch_reference_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_ARCH_REFERENCE_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
- TestDescriptiveRef: 描述性 ID（无数字后缀如 #ARCH-DOC-REF-FILE-URL）检测（2026-08-05 治本 gate 正则盲区）
- TestTemplateRefFiltered: 模板占位符（#ARCH-NNN / #ARCH-XXX 等）过滤不误报（2026-08-05）
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.arch_reference_gate import (
    make_arch_reference_gate,
)


# 测试用 registry YAML：含数字制 + 描述性 ARCH ID，不含 #ARCH-999 / #ARCH-DOC-REF-FAKE
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
  - issue_id: '#ARCH-DOC-REF-FILE-URL'
    title: test descriptive issue (no digit suffix)
    status: decided
  - issue_id: '#ARCH-IFIND-FAILOVER'
    title: test descriptive issue (registered)
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

        # mock get_head_content 返回含 #ARCH-999 的 HEAD 版本（历史已有此引用）
        # 治本（M03，2026-07-18）：get_head_content 已下沉到 _reference_helpers，
        # mock 需打在 _reference_helpers 模块上（scan_file_violations 内部调用）。
        import zephyr.gov_enforcement.commit_gates._reference_helpers as helpers

        monkeypatch.setattr(
            helpers, "get_head_content", lambda pr, rel: "# see #ARCH-999\n"
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

    def test_no_digit_suffix_now_matched(self, tmp_path):
        """无数字后缀的 #ARCH-GOV-SHIM 现在被正则匹配 → 未登记则阻断。

        治本（2026-08-05）：旧正则要求末尾 \\d+ 数字，#ARCH-GOV-SHIM（无数字）不匹配 →
        通过（零检测）。新正则 \\d+|[A-Z][A-Z0-9-]*[A-Z0-9] 同时匹配描述性 ID，
        #ARCH-GOV-SHIM 匹配为 GOV-SHIM，未登记 → 阻断。
        注意：GOV-SHIM 与已登记的 GOV-SHIM-001 是不同字符串，故 GOV-SHIM 仍未登记。
        """
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-GOV-SHIM for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed  # 新正则匹配描述性 ID，GOV-SHIM 未登记 → 阻断
        assert "GOV-SHIM" in detail


class TestDescriptiveRef:
    """描述性 ID（无数字后缀如 #ARCH-DOC-REF-FILE-URL）检测。

    治本 gate 正则盲区（2026-08-05）：旧正则 [A-Z]+(?:-[A-Z]+)*-[A-Z]?\\d+ 要求末尾 \\d+，
    导致 #ARCH-DOC-REF-FILE-URL / #ARCH-IFIND-FAILOVER 等无数字后缀的描述性 ARCH ID
    完全逃逸检测（全项目 67 个描述性引用 0% 被检出）。新正则同时匹配数字制和描述制 ID。
    """

    def test_unregistered_descriptive_blocked(self, tmp_path):
        """新增未登记描述性 #ARCH-DOC-REF-FAKE 引用 → 阻断（核心治本点）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-DOC-REF-FAKE for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "ARCH_REFERENCE_VIOLATION" in detail
        assert "DOC-REF-FAKE" in detail

    def test_registered_descriptive_passes(self, tmp_path, monkeypatch):
        """已登记描述性 #ARCH-DOC-REF-FILE-URL 引用 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# file:/// 协议处理（#ARCH-DOC-REF-FILE-URL, 2026-08-05 治本）\n",
            encoding="utf-8",
        )
        # mock load_head_registered_nums 返回 None（跳过 L2 原子性检查）——
        # tmp_path 位于真实 git 仓库内，L2 会读取真实 HEAD registry（不含未提交的
        # DOC-REF-FILE-URL），误报原子性违规。跳过 L2 隔离测试环境。
        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod
        monkeypatch.setattr(gate_mod, "load_head_registered_nums", lambda *a, **kw: None)
        passed, detail = gate.check(gw, [str(target)])
        assert passed

    def test_registered_descriptive_no_digit_passes(self, tmp_path):
        """已登记描述性 #ARCH-IFIND-FAILOVER（全字母无数字）引用 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-IFIND-FAILOVER for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed

    def test_descriptive_and_numeric_mixed(self, tmp_path):
        """文件同时含已登记描述性 + 未登记数字 ID → 阻断（只报未登记的）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# see #ARCH-DOC-REF-FILE-URL (registered) and #ARCH-999 (unregistered)\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "999" in detail
        assert "DOC-REF-FILE-URL" not in detail  # 已登记的不在违规列表


class TestTemplateRefFiltered:
    """模板占位符（#ARCH-NNN / #ARCH-XXX 等）过滤不误报。

    治本（2026-08-05）：新正则支持描述性 ID 后，模板占位符（NNN / XXX / *-NNN）
    需显式过滤，否则文档/gate 代码中的格式描述文本会误报为未登记引用。
    """

    def test_arch_nnn_filtered(self, tmp_path):
        """#ARCH-NNN（格式占位符）不误报为未登记引用 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# 任何 #ARCH-NNN 引用必须在本注册表有对应条目\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # NNN 是模板占位符，被过滤

    def test_arch_xxx_filtered(self, tmp_path):
        """#ARCH-XXX（格式占位符）不误报 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# 禁止 grep-and-claim 占位（任何 #ARCH-XXX 引用必须登记）\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # XXX 是模板占位符，被过滤

    def test_arch_ch_nnn_filtered(self, tmp_path):
        """#ARCH-CH-NNN（域前缀+占位符）不误报 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# 支持两段式域前缀（如 #ARCH-CH-NNN）和多段式（如 #ARCH-GOV-SHIM-NNN）\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # CH-NNN / GOV-SHIM-NNN 都以 -NNN 结尾，被过滤

    def test_arch_domain_nnn_filtered(self, tmp_path):
        """#ARCH-DOMAIN-NNN（格式示例）不误报 → 通过。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# 跨子系统的专题裁定使用 #ARCH-DOMAIN-NNN 格式\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # DOMAIN-NNN 以 -NNN 结尾，被过滤

    def test_mixed_template_and_unregistered(self, tmp_path):
        """文件含模板 #ARCH-NNN + 未登记 #ARCH-999 → 阻断（只报 999）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(
            "# 任何 #ARCH-NNN 引用必须登记，但 #ARCH-999 未登记\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert not passed  # 999 未登记 → 阻断
        assert "999" in detail
        # NNN 被过滤——违规列表只有 999（detail 消息头含 "#ARCH-NNN" 模板文字，需检查违规行）
        violation_lines = [l for l in detail.split("\n") if l.strip().startswith("- module.py")]
        assert len(violation_lines) == 1
        assert "NNN" not in violation_lines[0]
