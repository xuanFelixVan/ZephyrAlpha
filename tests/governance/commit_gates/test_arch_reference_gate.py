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
- TestL3NonNumericWarning: L3 新条目数字制检测（ARCH_NON_NUMERIC_WARNING，不阻断）（2026-08-05 铁律#7 冻结条款）
- TestIsNumericSuffix: _is_numeric_suffix 数字制判定单元测试（2026-08-05 铁律#7 冻结条款）
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.arch_reference_gate import (
    _is_numeric_suffix,
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
_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"


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

        monkeypatch.setattr(helpers, "get_head_content", lambda pr, rel: "# see #ARCH-999\n")

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


class TestL3NonNumericWarning:
    """L3 新条目数字制检测（ARCH_NON_NUMERIC_WARNING，不阻断）。

    治本铁律#7 冻结条款（2026-08-05）：2026-08-05 起新登记 ARCH 条目末段必须为纯数字。
    L3 检测 registry 中新增的描述性 ID（末段非数字），WARNING 不阻断。
    只在 registry 在本次 commit 中时检测（registry 未修改则无新条目）。
    """

    def test_new_descriptive_entry_warns(self, tmp_path, monkeypatch):
        """新增描述性 ID 到 registry → WARNING（passed=True，不阻断）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        # mock load_head_registered_nums 返回仅数字制 ID（HEAD 无描述性 ID）
        # 模拟工作区 registry 新增了 DOC-REF-FILE-URL / IFIND-FAILOVER
        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "load_head_registered_nums",
            lambda *a, **kw: {"008", "019", "GOV-SHIM-001"},
        )

        # registry 文件必须在 commit files 列表中才触发 L3
        registry_path = str(tmp_path / _REGISTRY_REL)
        passed, detail = gate.check(gw, [registry_path])
        assert passed  # WARNING 不阻断
        assert "ARCH_NON_NUMERIC_WARNING" in detail
        assert "DOC-REF-FILE-URL" in detail
        assert "IFIND-FAILOVER" in detail

    def test_new_numeric_entry_no_warning(self, tmp_path, monkeypatch):
        """新增数字制 ID 到 registry → 无 WARNING（数字制合规）。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        # HEAD 有 008/019/描述性 ID，工作区新增 GOV-SHIM-001（数字制）
        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "load_head_registered_nums",
            lambda *a, **kw: {"008", "019", "DOC-REF-FILE-URL", "IFIND-FAILOVER"},
        )

        registry_path = str(tmp_path / _REGISTRY_REL)
        passed, detail = gate.check(gw, [registry_path])
        assert passed
        # GOV-SHIM-001 是数字制（末段 001 纯数字），不触发 L3 warning
        assert "ARCH_NON_NUMERIC_WARNING" not in detail

    def test_registry_not_in_commit_no_l3(self, tmp_path, monkeypatch):
        """registry 不在 commit files 中 → 不触发 L3 检测。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "load_head_registered_nums",
            lambda *a, **kw: {"008", "019"},  # HEAD 无描述性 ID
        )

        # 只 commit 一个普通文件（不含 registry）——registry 未修改则无新条目
        target = tmp_path / "module.py"
        target.write_text("# see #ARCH-008\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed
        assert "ARCH_NON_NUMERIC_WARNING" not in detail

    def test_head_nums_none_no_l3(self, tmp_path, monkeypatch):
        """head_nums 为 None（非 git 仓库）→ 不触发 L3 检测。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "load_head_registered_nums",
            lambda *a, **kw: None,  # 非 git 仓库
        )

        registry_path = str(tmp_path / _REGISTRY_REL)
        passed, detail = gate.check(gw, [registry_path])
        assert passed
        assert "ARCH_NON_NUMERIC_WARNING" not in detail

    def test_mixed_new_entries_only_descriptive_warns(self, tmp_path, monkeypatch):
        """新增混合条目（数字制+描述性）→ 只对描述性 WARNING。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_arch_reference_gate()

        # HEAD 只有 008，工作区新增 019/GOV-SHIM-001（数字）+ DOC-REF-FILE-URL/IFIND-FAILOVER（描述性）
        import zephyr.gov_enforcement.commit_gates.arch_reference_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "load_head_registered_nums",
            lambda *a, **kw: {"008"},
        )

        registry_path = str(tmp_path / _REGISTRY_REL)
        passed, detail = gate.check(gw, [registry_path])
        assert passed
        assert "ARCH_NON_NUMERIC_WARNING" in detail
        # 描述性 ID 出现在 warning 列表中
        assert "DOC-REF-FILE-URL" in detail
        assert "IFIND-FAILOVER" in detail
        # 数字制新条目不出现在 warning 的列表项中
        warning_section = detail.split("ARCH_NON_NUMERIC_WARNING", 1)[1]
        listed_items = [ln.strip() for ln in warning_section.split("\n") if ln.strip().startswith("- #ARCH-")]
        listed_ids = [item.replace("- #ARCH-", "") for item in listed_items]
        assert "019" not in listed_ids
        assert "GOV-SHIM-001" not in listed_ids
        assert "DOC-REF-FILE-URL" in listed_ids
        assert "IFIND-FAILOVER" in listed_ids


class TestIsNumericSuffix:
    """_is_numeric_suffix 数字制判定单元测试（铁律#7 冻结条款，2026-08-05）。

    数字制 = 末段纯数字。判定规则二元化：
    - 末段纯数字 → True（数字制）
    - 末段非数字 → False（描述性 ID）
    """

    def test_pure_number(self):
        """纯数字 '008' → True。"""
        assert _is_numeric_suffix("008") is True

    def test_two_segment_numeric(self):
        """两段式 'CH-007'（末段 007 纯数字）→ True。"""
        assert _is_numeric_suffix("CH-007") is True

    def test_multi_segment_numeric(self):
        """多段式 'GOV-SHIM-001'（末段 001 纯数字）→ True。"""
        assert _is_numeric_suffix("GOV-SHIM-001") is True

    def test_four_segment_numeric(self):
        """四段式 'A-B-C-001'（末段 001 纯数字）→ True。"""
        assert _is_numeric_suffix("A-B-C-001") is True

    def test_descriptive_url(self):
        """描述性 'DOC-REF-FILE-URL'（末段 URL 非数字）→ False。"""
        assert _is_numeric_suffix("DOC-REF-FILE-URL") is False

    def test_descriptive_expand(self):
        """描述性 'EDB-EXPAND'（末段 EXPAND 非数字）→ False。"""
        assert _is_numeric_suffix("EDB-EXPAND") is False

    def test_descriptive_failover(self):
        """描述性 'IFIND-FAILOVER'（末段 FAILOVER 非数字）→ False。"""
        assert _is_numeric_suffix("IFIND-FAILOVER") is False

    def test_s_variant_numeric(self):
        """S 阶段变体 'CAPABILITY-LOOKUP-BYPASS-DEAD-S2'（末段 S2 非纯数字）→ False。

        注意：S2 末段含字母 S，isdigit() 返回 False，故判定为描述性 ID。
        这是 _is_numeric_suffix 的二元判定边界——S 变体末段非纯数字。
        实际上 S 变体是历史已登记条目（冻结保留），不强制迁移。
        """
        assert _is_numeric_suffix("CAPABILITY-LOOKUP-BYPASS-DEAD-S2") is False
