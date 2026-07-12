# [A_test] module_id: SRC-TST-2102 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-dangling_reference_gate | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §dangling-reference-gate
# [MODULE] tests.test_dangling_reference_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_dangling_reference_gate.py — AGENTS.md §X.Y 悬空引用检测门禁单测（DANGLING-REFERENCE）

权威依据：dangling_reference_gate.py（make_dangling_reference_gate）

测试组：
- TestDanglingBlocked: 新增悬空引用 → 阻断
- TestValidRefPasses: 合法引用 → 通过
- TestNoRefPasses: 无引用 → 通过
- TestFailClosedNoAgentsMd: AGENTS.md 缺失 → 阻断（fail-closed）
- TestTestExempt: tests/ 下文件豁免 → 通过
- TestBlueprintRefIgnored: blueprint.md §X.Y 引用不检测 → 通过
- TestIncrementalOnly: HEAD 已有悬空引用 → 通过（增量检测不阻断历史）
- TestGateSpecFields: gate_id / priority 字段正确
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.dangling_reference_gate import (
    make_dangling_reference_gate,
)


# § 字符常量（避免源文件中直接写 § 导致编码问题）
_SEC = chr(0xA7)

# 测试用 AGENTS.md 内容：含 §6 和 §7，不含 §6.9
_AGENTS_MD_CONTENT = f"""# AGENTS.md

## 6. 关键路径

一些内容。

## 7. 代码规范

更多内容。
"""


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway，仅需 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


def _write_agents_md(project_root: Path) -> None:
    """在 project_root 下写入测试用 AGENTS.md。"""
    (project_root / "AGENTS.md").write_text(_AGENTS_MD_CONTENT, encoding="utf-8")


class TestDanglingBlocked:
    """新增悬空引用 → 阻断。"""

    def test_dangling_ref_blocked(self, tmp_path):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(f"# see AGENTS.md {_SEC}6.9 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "DANGLING_REFERENCE_VIOLATION" in detail
        assert "6.9" in detail


class TestValidRefPasses:
    """合法引用 → 通过。"""

    def test_valid_ref_passes(self, tmp_path):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(f"# see AGENTS.md {_SEC}6 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed


class TestNoRefPasses:
    """无引用 → 通过。"""

    def test_no_ref_passes(self, tmp_path):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# no references here\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed


class TestFailClosedNoAgentsMd:
    """AGENTS.md 缺失 → 阻断（fail-closed）。"""

    def test_no_agents_md_blocked(self, tmp_path):
        # 不创建 AGENTS.md
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text(f"# see AGENTS.md {_SEC}6\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert not passed
        assert "fail-closed" in detail.lower() or "not found" in detail.lower()


class TestTestExempt:
    """tests/ 下文件豁免 → 通过（即使含悬空引用）。"""

    def test_tests_dir_exempt(self, tmp_path):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        target = tests_dir / "test_something.py"
        target.write_text(f"# see AGENTS.md {_SEC}6.9\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # tests/ 豁免，不检测


class TestBlueprintRefIgnored:
    """blueprint.md §X.Y 引用不检测 → 通过。"""

    def test_blueprint_ref_ignored(self, tmp_path):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()
        target = tmp_path / "module.py"
        # blueprint.md §9.9 引用不应被检测（不是 AGENTS.md 引用）
        target.write_text(
            f"# see blueprint.md {_SEC}9.9 and AGENTS.md {_SEC}6\n", encoding="utf-8"
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed  # blueprint §9.9 不检测，AGENTS.md §6 合法


class TestIncrementalOnly:
    """HEAD 已有悬空引用 → 通过（增量检测不阻断历史）。"""

    def test_existing_dangling_not_blocked(self, tmp_path, monkeypatch):
        _write_agents_md(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_dangling_reference_gate()

        target = tmp_path / "module.py"
        target.write_text(f"# see AGENTS.md {_SEC}6.9\n", encoding="utf-8")

        # mock _get_head_content 返回含 §6.9 的 HEAD 版本（历史已有此引用）
        import zephyr.gov_enforcement.commit_gates.dangling_reference_gate as mod

        monkeypatch.setattr(
            mod, "_get_head_content", lambda pr, rel: f"# see AGENTS.md {_SEC}6.9\n"
        )

        passed, detail = gate.check(gw, [str(target)])
        assert passed  # 历史悬空引用不阻断


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id(self):
        gate = make_dangling_reference_gate()
        assert gate.gate_id == "DANGLING-REFERENCE"

    def test_priority(self):
        gate = make_dangling_reference_gate()
        assert gate.priority == 70
