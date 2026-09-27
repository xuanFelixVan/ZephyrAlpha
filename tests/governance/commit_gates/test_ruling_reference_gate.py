# [A_test] module_id: MOD-GOV_ruling_reference_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RULING_REFERENCE_GATE | docs/03_modules/_domain_governance/commit_gate_catalog/blueprint.md | §ruling-ref-gate
# [MODULE] tests.test_ruling_reference_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RULING_REFERENCE_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_ruling_reference_gate.py — 裁定#NNN 悬空引用检测门禁单测（RULING-REFERENCE）

权威依据：ruling_reference_gate.py（make_ruling_reference_gate）

测试组（裁定#20-G 阶段2 hard block 模式，_MANUAL_STAGE=False）：
- TestDanglingRefBlocks: 新增未登记裁定#NNN 引用 → 阻断（passed=False + RULING_REFERENCE_VIOLATION）
- TestRegisteredRefPasses: 合法已登记裁定#NNN 引用 → 通过
- TestNoRefPasses: 无裁定#NNN 引用 → 通过
- TestFailClosedNoRegistry: registry 缺失 → 阻断（fail-closed）
- TestTestExempt: tests/ 下文件豁免 → 通过
- TestIncrementalOnly: HEAD 已有引用 → 通过（增量检测不阻断历史）
- TestGateSpecFields: gate_id / priority 字段正确
- TestSuffixRef: 带字母后缀的引用（裁定#19-A / 裁定#203-B 等）检测
- TestExtractRegisteredNums / TestExtractRefs: 解析函数单元测试
- TestReferenceIntegrityUnionRedProof: 活执法台 REFERENCE-INTEGRITY 聚合门禁配对红证
  （F101 缺口 G1 治本 2026-09-27：旧单门工厂已并入聚合台不再注册，"裸裁定引用不登记"
  必须在活执法通道上可红——此前仅退役工厂有红测，聚合台只有构造冒烟）
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
    make_ruling_reference_gate,
)

# 测试用 registry YAML：含 裁定#6 / 裁定#19 / 裁定#19-B / 裁定#203-B，不含 裁定#999
# 使用真源字段 "entries"（对标 architecture_issue_registry.yaml 结构）
_REGISTRY_YAML = """\
module_id: REG-RULING-001
entries:
  - ruling_id: "裁定#6"
    title: 路径SSoT
    status: active
  - ruling_id: "裁定#19"
    title: 依赖图责任划分
    status: active
  - ruling_id: "裁定#19-B"
    title: worktree base 新鲜度检查
    status: active
  - ruling_id: "裁定#203-B"
    title: 子模块规划
    status: active
"""

# registry 在 project_root 下的相对路径（对标 ruling_reference_gate._REGISTRY_REL）
_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"


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


class TestDanglingRefBlocks:
    """阶段2 hard block：新增未登记裁定#NNN 引用 → 阻断（passed=False + RULING_REFERENCE_VIOLATION）。"""

    def test_dangling_ruling_ref_blocks(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# see 裁定#999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        # hard block: passed=False, detail 含 RULING_REFERENCE_VIOLATION
        assert passed is False, f"hard block 应阻断未登记引用，但放行。detail={detail}"
        assert "RULING_REFERENCE_VIOLATION" in detail or "RULING-REFERENCE" in detail.upper()


class TestRegisteredRefPasses:
    """合法已登记裁定#NNN 引用 → 通过。"""

    def test_registered_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# ref 裁定#6 路径SSoT\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True


class TestNoRefPasses:
    """无裁定#NNN 引用 → 通过。"""

    def test_no_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("print('hello')\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True


class TestFailClosedNoRegistry:
    """hard block 下 registry 缺失 → 阻断（fail-closed）。"""

    def test_no_registry_blocks(self, tmp_path):
        # 不写 registry
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# ref 裁定#6\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        # hard block: registry 缺失阻断
        assert passed is False
        assert "fail-closed" in detail or "not found" in detail


class TestTestExempt:
    """tests/ 下文件豁免 → 通过。"""

    def test_test_file_exempt(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "tests" / "test_module.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# ref 裁定#999 should be exempt\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True


class TestIncrementalOnly:
    """HEAD 已有引用 → 通过（增量检测不阻断历史）。

    需 git 仓库环境，非 git 环境（tmp_path）下 HEAD 检测跳过，
    所有引用视为新增——此测试验证非 git 环境下仍能正常工作。
    """

    def test_no_git_env_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        # 使用已登记的裁定#6，非 git 环境下视为新增但已登记，应通过
        target.write_text("# ref 裁定#6\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_is_ruling_reference(self):
        gate = make_ruling_reference_gate()
        assert gate.gate_id == "RULING-REFERENCE"

    def test_priority_is_74(self):
        gate = make_ruling_reference_gate()
        assert gate.priority == 74


class TestSuffixRef:
    """带字母后缀的引用（裁定#19-A / 裁定#203-B 等）检测。"""

    def test_registered_suffix_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# ref 裁定#19-B worktree base 新鲜度\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True

    def test_registered_multi_suffix_ref_passes(self, tmp_path):
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# ref 裁定#203-B 子模块规划\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True

    def test_dangling_suffix_ref_blocks(self, tmp_path):
        """hard block 下未登记的带后缀引用 → 阻断。"""
        _write_registry(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = make_ruling_reference_gate()
        target = tmp_path / "module.py"
        target.write_text("# ref 裁定#999-Z 未登记\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        # hard block: passed=False
        assert passed is False


class TestExtractRegisteredNums:
    """_extract_registered_nums 函数单元测试。"""

    def test_extract_pure_number(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_registered_nums,
        )

        # entries 是真源字段（对标 architecture_issue_registry.yaml）
        data = {"entries": [{"ruling_id": "裁定#6"}, {"ruling_id": "裁定#19"}]}
        nums = _extract_registered_nums(data)
        assert "6" in nums
        assert "19" in nums

    def test_extract_with_suffix(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_registered_nums,
        )

        data = {"entries": [{"ruling_id": "裁定#19-A"}, {"ruling_id": "裁定#203-B"}]}
        nums = _extract_registered_nums(data)
        assert "19-A" in nums
        assert "203-B" in nums

    def test_extract_rulings_alias_compatible(self):
        """早期测试用 'rulings' 字段，gate 兼容此别名。"""
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_registered_nums,
        )

        data = {"rulings": [{"ruling_id": "裁定#6"}]}
        nums = _extract_registered_nums(data)
        assert "6" in nums

    def test_extract_empty_rulings(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_registered_nums,
        )

        nums = _extract_registered_nums({})
        assert nums == set()


class TestExtractRefs:
    """_extract_refs 函数单元测试。"""

    def test_extract_pure_number_ref(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_refs,
        )

        content = "见裁定#6 和裁定#19 的说明"
        refs = _extract_refs(content)
        assert "6" in refs
        assert "19" in refs

    def test_extract_suffix_ref(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_refs,
        )

        content = "裁定#19-A 和 裁定#203-B"
        refs = _extract_refs(content)
        assert "19-A" in refs
        assert "203-B" in refs

    def test_extract_no_ref(self):
        from zephyr.gov_enforcement.commit_gates.ruling_reference_gate import (
            _extract_refs,
        )

        content = "no ruling reference here"
        refs = _extract_refs(content)
        assert refs == set()


class TestReferenceIntegrityUnionRedProof:
    """活执法台 REFERENCE-INTEGRITY 聚合门禁配对红证（F101 缺口 G1 / RULE-RULING 执法闭环）。

    病根（2026-09-27 挖干）：RULING-REFERENCE 旧单门工厂已并入 REFERENCE-INTEGRITY
    （dangling_reference_gate.make_reference_integrity_gate，priority=70）且不再注册；
    既有红测组挂的是退役工厂。活聚合台此前仅有构造冒烟（test_p4_merged_gates.py），
    "裸裁定引用不登记可红"在活执法通道上无配对证据——RULE-RULING 同 commit 原子
    实际靠流程纪律而非机检闭环。本组补齐活通道红/绿配对。
    """

    # ARCH 子检查 fail-closed 前提：architecture_issue_registry.yaml 至少一条 issue_id
    # （entry 键名真源：arch_reference_gate._extract_registered_nums 读 entries[].issue_id）
    _ARCH_REGISTRY_YAML = """\
module_id: REG-ARCH-TEST
entries:
  - issue_id: "#ARCH-001"
    title: 测试条目
    status: open
"""

    def _setup_union_env(self, tmp_path: Path) -> None:
        """tmp_path 内备齐三个子检查的真源文件（全程不触生产目录）。

        - AGENTS.md：DANGLING 子检查 fail-closed 前提（至少一个章节号标题）
        - architecture_issue_registry.yaml：ARCH 子检查 fail-closed 前提
        - ruling_registry.yaml：RULING 子检查真源（复用本文件 _write_registry）
        """
        (tmp_path / "AGENTS.md").write_text("# 测试宪法\n## 0. 冷启动\n", encoding="utf-8")
        arch = (
            tmp_path
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "architecture_issue_registry.yaml"
        )
        arch.parent.mkdir(parents=True, exist_ok=True)
        arch.write_text(self._ARCH_REGISTRY_YAML, encoding="utf-8")
        _write_registry(tmp_path)

    def _make_union_gate(self):
        from zephyr.gov_enforcement.commit_gates.dangling_reference_gate import (
            make_reference_integrity_gate,
        )

        return make_reference_integrity_gate()

    def test_bare_ruling_ref_red_through_live_union_gate(self, tmp_path):
        """红证：裸裁定引用（未登记 裁定#999）经活聚合台必须阻断。"""
        self._setup_union_env(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = self._make_union_gate()
        target = tmp_path / "module.py"
        target.write_text("# see 裁定#999 for details\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is False, f"活聚合台放行了裸裁定引用——红证失效。detail={detail}"
        assert "[RULING-REFERENCE]" in detail, f"聚合 detail 未标注来源子台：{detail}"
        assert "RULING_REFERENCE_VIOLATION" in detail

    def test_dangling_only_subcheck_not_confused_with_ruling(self, tmp_path):
        """定向性：仅 DANGLING 子台违规时，聚合红由 [DANGLING-REFERENCE] 触发、RULING 子台不误报。"""
        self._setup_union_env(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = self._make_union_gate()
        target = tmp_path / "module2.py"
        # 悬空 AGENTS.md §9.9 引用 + 合法裁定#6 引用 -> 只有 DANGLING 子台红
        target.write_text("# see AGENTS.md §9.9 and 裁定#6\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is False
        assert "[DANGLING-REFERENCE]" in detail
        assert "[RULING-REFERENCE]" not in detail

    def test_registered_ruling_ref_green_through_live_union_gate(self, tmp_path):
        """绿证：已登记裁定引用经活聚合台全绿（三子台全过）。"""
        self._setup_union_env(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = self._make_union_gate()
        target = tmp_path / "module3.py"
        target.write_text("# ref 裁定#6 路径SSoT\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True, f"已登记引用被活聚合台误阻：{detail}"

    def test_test_exempt_ruling_ref_green_through_live_union_gate(self, tmp_path):
        """绿证：tests/ 豁免区裸裁定引用经活聚合台放行。"""
        self._setup_union_env(tmp_path)
        gw = _make_gateway(tmp_path)
        gate = self._make_union_gate()
        target = tmp_path / "tests" / "test_module.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# ref 裁定#999 exempt in tests\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is True, f"tests/ 豁免失效：{detail}"

    def test_union_gate_fail_closed_without_ruling_registry(self, tmp_path):
        """fail-closed：ruling_registry.yaml 缺失时活聚合台必须红（防门禁静默失效）。"""
        # 只备 DANGLING/ARCH 真源，不写 ruling registry
        (tmp_path / "AGENTS.md").write_text("# 测试宪法\n## 0. 冷启动\n", encoding="utf-8")
        arch = (
            tmp_path
            / "docs"
            / "01_policies_and_standards"
            / "_registry"
            / "catalogs"
            / "architecture_issue_registry.yaml"
        )
        arch.parent.mkdir(parents=True, exist_ok=True)
        arch.write_text(self._ARCH_REGISTRY_YAML, encoding="utf-8")
        gw = _make_gateway(tmp_path)
        gate = self._make_union_gate()
        target = tmp_path / "module4.py"
        target.write_text("# ref 裁定#6\n", encoding="utf-8")
        passed, detail = gate.check(gw, [str(target)])
        assert passed is False
        assert "[RULING-REFERENCE]" in detail
        assert "fail-closed" in detail
