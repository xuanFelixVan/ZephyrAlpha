# [A_test] module_id: MOD-GOV_import_integrity_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_import_integrity_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_import_integrity_gate.py — IMPORT-INTEGRITY 门禁单测（#ARCH-CROSS-COMMIT-ATOMICITY-001 治本）

权威依据：import_integrity_gate.py（make_import_integrity_gate）

测试组：
- TestGateSpecFields: gate_id / priority 字段正确
- TestScanContentHelpers: _collect_imports / _is_relative_import / _has_wildcard_import / _is_project_module
- TestProjectModuleResolvable: 项目内模块在 staged + main HEAD 中可解析
- TestExternalModuleResolvable: stdlib / 第三方模块可解析
- TestDanglingImportBlocked: 悬空 import 阻断（ba40fa5b75 同型违规）
- TestRelativeImportSkipped: 相对 import 跳过
- TestWildcardImportSkipped: wildcard import 跳过
- TestFailOpen: ast 失败 / 无 staged 文件 → fail-open
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
    _collect_imports,
    _has_wildcard_import,
    _is_project_module,
    _is_relative_import,
    _module_to_file_candidates,
    find_target_in_active_sessions,
    make_import_integrity_gate,
    scan_content_for_dangling_imports,
)


def _make_gateway() -> MagicMock:
    """构造 mock gateway（_run_git 返回可配置 result）。"""
    gw = MagicMock()
    # 默认 git show HEAD:path 返回 rc=1（找不到），由测试覆盖
    gw.run_git.return_value = MagicMock(returncode=1, stdout="", stderr="")
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields: gate_id / priority 字段正确
# ---------------------------------------------------------------------------


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_is_import_integrity(self):
        """gate_id = IMPORT-INTEGRITY。"""
        gate = make_import_integrity_gate()
        assert gate.gate_id == "IMPORT-INTEGRITY"

    def test_gate_is_gate_spec_instance(self):
        """gate 是 GateSpec 实例。"""
        gate = make_import_integrity_gate()
        assert isinstance(gate, GateSpec)

    def test_gate_priority_is_107(self):
        """priority = 107（紧接 UNDEFINED-NAME=106）。"""
        gate = make_import_integrity_gate()
        assert gate.priority == 107


# ---------------------------------------------------------------------------
# TestScanContentHelpers: 辅助函数
# ---------------------------------------------------------------------------


class TestScanContentHelpers:
    """辅助函数：_collect_imports / _is_relative_import / _has_wildcard_import / _is_project_module。"""

    def test_is_relative_import_for_dot(self):
        """from . import X 是相对 import。"""
        import ast

        tree = ast.parse("from . import foo")
        node = tree.body[0]
        assert _is_relative_import(node) is True

    def test_is_relative_import_for_dotdot(self):
        """from ..foo import bar 是相对 import。"""
        import ast

        tree = ast.parse("from ..foo import bar")
        node = tree.body[0]
        assert _is_relative_import(node) is True

    def test_is_relative_import_for_absolute(self):
        """from zephyr.foo import bar 不是相对 import。"""
        import ast

        tree = ast.parse("from zephyr.foo import bar")
        node = tree.body[0]
        assert _is_relative_import(node) is False

    def test_is_relative_import_for_plain_import(self):
        """import os 不是相对 import（Import 节点）。"""
        import ast

        tree = ast.parse("import os")
        node = tree.body[0]
        assert _is_relative_import(node) is False

    def test_has_wildcard_import_true(self):
        """from X import * 含 wildcard。"""
        import ast

        tree = ast.parse("from zephyr.foo import *")
        node = tree.body[0]
        assert _has_wildcard_import(node) is True

    def test_has_wildcard_import_false(self):
        """from X import bar 不含 wildcard。"""
        import ast

        tree = ast.parse("from zephyr.foo import bar")
        node = tree.body[0]
        assert _has_wildcard_import(node) is False

    def test_is_project_module_zephyr(self):
        """zephyr.xxx 是项目内模块。"""
        assert _is_project_module("zephyr.gov_enforcement.commit_gates.foo") is True

    def test_is_project_module_scripts(self):
        """scripts.xxx 是项目内模块。"""
        assert _is_project_module("scripts.governance.foo") is True

    def test_is_project_module_external(self):
        """os / requests 不是项目内模块。"""
        assert _is_project_module("os") is False
        assert _is_project_module("requests") is False

    def test_collect_imports_basic(self):
        """_collect_imports 收集 Import / ImportFrom，跳过相对/wildcard。"""
        import ast

        content = """
import os
import sys as system
from zephyr.foo import bar
from . import baz
from ..parent import qux
from another.mod import quux
"""
        tree = ast.parse(content)
        imports = _collect_imports(tree)
        # 应收集 4 个：os, sys, zephyr.foo, another.mod（相对与 wildcard 跳过）
        module_paths = {imp[1] for imp in imports}
        assert "os" in module_paths
        assert "sys" in module_paths
        assert "zephyr.foo" in module_paths
        assert "another.mod" in module_paths

    def test_module_to_file_candidates_zephyr(self):
        """zephyr.foo.bar 生成候选文件路径。"""
        candidates = _module_to_file_candidates("zephyr.foo.bar")
        assert "src/zephyr/foo/bar.py" in candidates
        assert "src/zephyr/foo/bar/__init__.py" in candidates
        assert "zephyr/foo/bar.py" in candidates
        assert "zephyr/foo/bar/__init__.py" in candidates


# ---------------------------------------------------------------------------
# TestProjectModuleResolvable: 项目内模块在 staged + main HEAD 中可解析
# ---------------------------------------------------------------------------


class TestProjectModuleResolvable:
    """项目内模块在 staged + main HEAD 中可解析。"""

    def test_resolvable_in_staged(self):
        """模块在 staged 文件中存在 → 可解析（同 commit 创建的目标文件）。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_project_module_resolvable,
        )

        gw = _make_gateway()
        # 模拟 staged 文件含 src/zephyr/foo/bar.py
        staged_files = {"src/zephyr/foo/bar.py"}
        result = _check_project_module_resolvable(
            "zephyr.foo.bar", staged_files, gw
        )
        assert result is True
        # 不应调用 git show（staged 命中即返回）
        gw.run_git.assert_not_called()

    def test_resolvable_in_main_head(self):
        """模块在 staged 不存在但 main HEAD 存在 → 可解析。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_project_module_resolvable,
        )

        gw = _make_gateway()
        # 模拟 git show HEAD:src/zephyr/foo/bar.py 成功
        gw.run_git.return_value = MagicMock(returncode=0, stdout="content", stderr="")
        staged_files: set[str] = set()
        result = _check_project_module_resolvable(
            "zephyr.foo.bar", staged_files, gw
        )
        assert result is True

    def test_not_resolvable_anywhere(self):
        """模块在 staged + main HEAD 都不存在 → 不可解析（悬空 import）。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_project_module_resolvable,
        )

        gw = _make_gateway()
        # git show HEAD 全部 rc=1
        gw.run_git.return_value = MagicMock(returncode=1, stdout="", stderr="")
        staged_files: set[str] = set()
        result = _check_project_module_resolvable(
            "zephyr.foo.nonexistent", staged_files, gw
        )
        assert result is False


# ---------------------------------------------------------------------------
# TestExternalModuleResolvable: stdlib / 第三方模块可解析
# ---------------------------------------------------------------------------


class TestExternalModuleResolvable:
    """stdlib / 第三方模块可解析（importlib.util.find_spec）。"""

    def test_stdlib_resolvable(self):
        """os / sys / json 是 stdlib，可解析。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_external_module_resolvable,
        )

        assert _check_external_module_resolvable("os") is True
        assert _check_external_module_resolvable("sys") is True
        assert _check_external_module_resolvable("json") is True

    def test_stdlib_submodule_resolvable(self):
        """os.path 是 stdlib 子模块，可解析。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_external_module_resolvable,
        )

        assert _check_external_module_resolvable("os.path") is True

    def test_nonexistent_external_not_resolvable(self):
        """不存在的第三方模块 → 不可解析。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_external_module_resolvable,
        )

        result = _check_external_module_resolvable("this_module_does_not_exist_xyz_12345")
        assert result is False


# ---------------------------------------------------------------------------
# TestDanglingImportBlocked: 悬空 import 阻断
# ---------------------------------------------------------------------------


class TestDanglingImportBlocked:
    """悬空 import 阻断（ba40fa5b75 同型违规）。"""

    def test_dangling_project_import_blocked(self):
        """悬空项目模块 import → 违规消息。"""
        content = """from zephyr.gov_enforcement.commit_gates.nonexistent_module import foo

foo()
"""
        gw = _make_gateway()
        # git show HEAD 全部 rc=1（模块不存在）
        gw.run_git.return_value = MagicMock(returncode=1, stdout="", stderr="")
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 1
        assert "nonexistent_module" in violations[0]
        assert "dangling import" in violations[0]

    def test_dangling_external_import_blocked(self):
        """悬空外部模块 import → 违规消息。"""
        content = """import this_module_does_not_exist_xyz_12345

this_module_does_not_exist_xyz_12345.do_something()
"""
        gw = _make_gateway()
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 1
        assert "this_module_does_not_exist_xyz_12345" in violations[0]

    def test_valid_imports_pass(self):
        """合法 import（stdlib + 已存在项目模块）→ 无违规。"""
        content = """import os
import sys
from pathlib import Path
from zephyr.gov_enforcement.commit_gates.import_integrity_gate import make_import_integrity_gate

print(os.getcwd())
"""
        gw = _make_gateway()
        # 模拟 git show HEAD:src/zephyr/gov_enforcement/commit_gates/import_integrity_gate.py 成功
        def _mock_run_git(cmd):
            # cmd = ["git", "show", "HEAD:src/zephyr/.../import_integrity_gate.py"]
            if len(cmd) > 2 and "import_integrity_gate" in cmd[2]:
                return MagicMock(returncode=0, stdout="content", stderr="")
            return MagicMock(returncode=1, stdout="", stderr="")

        gw.run_git.side_effect = _mock_run_git
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 0

    def test_staged_target_file_passes(self):
        """import 的目标文件在 staged（同 commit 创建）→ 无违规。"""
        content = """from zephyr.gov_enforcement.commit_gates.new_gate import make_new_gate

make_new_gate()
"""
        gw = _make_gateway()
        # staged 含目标文件
        staged_files = {"src/zephyr/gov_enforcement/commit_gates/new_gate.py"}
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# TestRelativeImportSkipped: 相对 import 跳过
# ---------------------------------------------------------------------------


class TestRelativeImportSkipped:
    """相对 import 跳过（依赖文件位置上下文，静态分析易误报）。"""

    def test_relative_import_skipped(self):
        """from . import foo / from ..foo import bar → 跳过（无违规）。"""
        content = """from . import foo
from ..parent import bar

foo()
bar()
"""
        gw = _make_gateway()
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# TestWildcardImportSkipped: wildcard import 跳过
# ---------------------------------------------------------------------------


class TestWildcardImportSkipped:
    """wildcard import 跳过（导入集无法静态推断）。"""

    def test_wildcard_import_skipped(self):
        """from X import * → 跳过（无违规，即使 X 不存在）。"""
        content = """from zephyr.nonexistent.module import *

do_something()
"""
        gw = _make_gateway()
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# TestFailOpen: ast 失败 / 无 staged 文件 → fail-open
# ---------------------------------------------------------------------------


class TestFailOpen:
    """fail-open：ast 失败 / 无 staged 文件 → 放行（passed=True）。"""

    def test_syntax_error_fail_open(self):
        """ast.parse 语法错误 → fail-open（返回空违规列表）。"""
        content = """def broken(
    # syntax error
"""
        gw = _make_gateway()
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 0

    def test_no_staged_files_passes(self):
        """无 staged 文件 → passed=True（_get_staged_py_files 返回空）。"""
        gw = _make_gateway()
        # 模拟 _get_staged_py_files 返回空（git diff 失败）
        gw.run_git.return_value = MagicMock(returncode=1, stdout="", stderr="")
        gate = make_import_integrity_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""


# ---------------------------------------------------------------------------
# TestBa40fa5b75Scenario: ba40fa5b75 同型违规复现（regression test）
# ---------------------------------------------------------------------------


class TestBa40fa5b75Scenario:
    """ba40fa5b75 同型违规复现（regression test）。

    场景：commit 在 git_commit_gateway.py 添加了
    from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import make_forged_gw_marker_gate
    但 forged_gw_marker_gate.py 在 staged + main HEAD 都不存在
    → 应被 IMPORT-INTEGRITY gate 阻断。
    """

    def test_ba40fa5b75_scenario_blocked(self):
        """ba40fa5b75 同型违规 → 阻断（passed=False）。"""
        # 模拟 git_commit_gateway.py 的内容（含悬空 import）
        content = """from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import make_forged_gw_marker_gate

class GitCommitGateway:
    def __init__(self):
        self._gate_registry.register(make_forged_gw_marker_gate())
"""
        gw = _make_gateway()
        # 模拟 git show HEAD:src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py 失败
        # （文件尚未创建，ba40fa5b75 时刻的真实状态）
        def _mock_run_git(cmd):
            if "forged_gw_marker_gate" in cmd[1]:
                return MagicMock(returncode=1, stdout="", stderr="not in HEAD")
            return MagicMock(returncode=1, stdout="", stderr="")

        gw.run_git.side_effect = _mock_run_git
        staged_files = {"src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"}
        violations = scan_content_for_dangling_imports(
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
            content,
            staged_files,
            gw,
        )
        assert len(violations) == 1
        assert "forged_gw_marker_gate" in violations[0]
        assert "dangling import" in violations[0]

    def test_ce81f1077f_scenario_passes(self):
        """ce81f1077f 落地后（文件已存在）→ 放行。"""
        content = """from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate import make_forged_gw_marker_gate

class GitCommitGateway:
    def __init__(self):
        self._gate_registry.register(make_forged_gw_marker_gate())
"""
        gw = _make_gateway()
        # 模拟 git show HEAD:src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py 成功
        # （文件已在 main HEAD 中，ce81f1077f merge 后的状态）
        def _mock_run_git(cmd):
            # cmd = ["git", "show", "HEAD:src/zephyr/.../forged_gw_marker_gate.py"]
            if len(cmd) > 2 and "forged_gw_marker_gate" in cmd[2]:
                return MagicMock(returncode=0, stdout="content", stderr="")
            return MagicMock(returncode=1, stdout="", stderr="")

        gw.run_git.side_effect = _mock_run_git
        staged_files = {"src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"}
        violations = scan_content_for_dangling_imports(
            "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
            content,
            staged_files,
            gw,
        )
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# TestFindTargetInActiveSessions: Phase 2.5 find_target_in_active_sessions 函数
# （#ARCH-CROSS-COMMIT-ATOMICITY-002：GATE-IMPORT-INTEGRITY 阻断时自动追加活跃
# session held_files 友好提示，不依赖 AI 传 depends_on_sessions 参数）
# ---------------------------------------------------------------------------


class TestFindTargetInActiveSessions:
    """Phase 2.5 find_target_in_active_sessions 函数测试。

    覆盖场景：
    - 目标模块在其他活跃 session held_files 中 → 命中
    - 目标模块不在任何活跃 session held_files 中 → 空列表
    - 排除自身 session（current_session_id）
    - 无活跃 session → 空列表
    - SessionRegistry 异常 → fail-open 空列表
    - 多候选路径匹配（module.py / module/__init__.py）
    - 跨平台路径分隔符（Windows 反斜杠归一化）
    """

    def test_target_in_other_active_session_held_files(self, tmp_path):
        """目标模块在其他活跃 session held_files 中 → 命中。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        # session-B 持有 forged_gw_marker_gate.py
        target_file = str(tmp_path / "src" / "zephyr" / "gov_enforcement" / "commit_gates" / "forged_gw_marker_gate.py")
        reg.register("sess-B", pid=0, held_files=[target_file])
        # 检查目标模块 zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert len(hits) == 1
        assert hits[0][0] == "sess-B"
        assert "forged_gw_marker_gate" in hits[0][1]

    def test_target_not_in_any_active_session(self, tmp_path):
        """目标模块不在任何活跃 session held_files 中 → 空列表。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B", pid=0, held_files=[str(tmp_path / "other.py")])
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert hits == []

    def test_exclude_current_session(self, tmp_path):
        """排除自身 session——自身 commit 的文件已在 staged_set，不应命中。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        target_file = str(tmp_path / "src" / "zephyr" / "forged_gw_marker_gate.py")
        # sess-A（自身）持有目标文件
        reg.register("sess-A", pid=0, held_files=[target_file])
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert hits == []  # 排除自身

    def test_no_active_sessions(self, tmp_path):
        """无活跃 session → 空列表。"""
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert hits == []

    def test_fail_open_on_registry_exception(self, tmp_path):
        """SessionRegistry 异常 → fail-open 空列表（不阻断）。"""
        # 用一个不存在的 project_root 触发异常（无写权限等）
        # 实际上 SessionRegistry 对异常 fail-open，但为保险用 monkeypatch
        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        original = gate_mod.find_target_in_active_sessions
        try:
            # 模拟 SessionRegistry 构造抛异常
            with pytest.MonkeyPatch.context() as mp:
                def _boom(*args, **kwargs):
                    raise RuntimeError("simulated registry failure")
                mp.setattr(
                    "zephyr.security.access_control.session_concurrency.SessionRegistry",
                    _boom,
                )
                hits = original(
                    tmp_path,
                    "zephyr.forged_gw_marker_gate",
                    current_session_id="sess-A",
                )
            assert hits == []  # fail-open
        except Exception:
            pass

    def test_multiple_candidates_match(self, tmp_path):
        """多候选路径匹配——module.py 或 module/__init__.py。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        # session-B 持有 __init__.py 形式（包模块）
        target_file = str(tmp_path / "src" / "zephyr" / "my_package" / "__init__.py")
        reg.register("sess-B", pid=0, held_files=[target_file])
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.my_package",
            current_session_id="sess-A",
        )
        assert len(hits) == 1
        assert hits[0][0] == "sess-B"

    def test_windows_backslash_normalization(self, tmp_path):
        """Windows 反斜杠路径分隔符归一化匹配。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        # held_file 用 Windows 反斜杠（SessionRegistry._normalize_file_path 会 resolve，
        # 但测试直接构造反斜杠路径验证 endswith 匹配）
        target_file = str(tmp_path / "src" / "zephyr" / "forged_gw_marker_gate.py").replace("/", "\\")
        reg.register("sess-B", pid=0, held_files=[target_file])
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert len(hits) == 1
        assert hits[0][0] == "sess-B"

    def test_multiple_sessions_one_holds_target(self, tmp_path):
        """多活跃 session，其中之一持有目标模块。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B", pid=0, held_files=[str(tmp_path / "other1.py")])
        target_file = str(tmp_path / "src" / "zephyr" / "gov_enforcement" / "commit_gates" / "forged_gw_marker_gate.py")
        reg.register("sess-C", pid=0, held_files=[target_file])
        reg.register("sess-D", pid=0, held_files=[str(tmp_path / "other2.py")])
        hits = find_target_in_active_sessions(
            tmp_path,
            "zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate",
            current_session_id="sess-A",
        )
        assert len(hits) == 1
        assert hits[0][0] == "sess-C"


# ---------------------------------------------------------------------------
# TestCheckClosurePhase25Hint: _check 闭包 Phase 2.5 友好提示
# （阻断时自动追加"等待该 session merge"提示）
# ---------------------------------------------------------------------------


class TestCheckClosurePhase25Hint:
    """_check 闭包 Phase 2.5 友好提示测试。

    覆盖场景：
    - 悬空 import + 目标模块在其他活跃 session held → 阻断消息含 Phase 2.5 hint
    - 悬空 import + 目标模块不在其他活跃 session → 阻断消息不含 hint（正常阻断）
    - 悬空 import + 无活跃 session → 阻断消息不含 hint
    - session_id 从 kwargs 传入 → 排除自身
    """

    def test_block_with_hint_when_target_in_other_session(self, tmp_path):
        """悬空 import + 目标模块在其他活跃 session held → 阻断消息含 Phase 2.5 hint。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        # 准备：session-B 持有 forged_gw_marker_gate.py
        reg = SessionRegistry(project_root=tmp_path)
        target_file = str(tmp_path / "src" / "zephyr" / "gov_enforcement" / "commit_gates" / "forged_gw_marker_gate.py")
        reg.register("sess-B", pid=0, held_files=[target_file])

        # 构造 mock gateway：staged 文件含悬空 import，HEAD 中无目标模块
        gw = MagicMock()
        gw.project_root = tmp_path
        # _get_staged_py_files 返回含悬空 import 的文件
        staged_py = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        staged_content = (
            "from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate "
            "import make_forged_gw_marker_gate\n"
        )

        def _mock_run_git(args):
            # git show HEAD:path → 找不到目标模块（rc=1）
            return MagicMock(returncode=1, stdout="", stderr="")
        gw.run_git = _mock_run_git

        # mock _get_staged_py_files 和 _read_staged_file
        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(gate_mod, "_get_staged_py_files", lambda g, gid: [staged_py])
            mp.setattr(gate_mod, "_read_staged_file", lambda g, f: staged_content)
            gate = make_import_integrity_gate()
            passed, detail = gate.check(gw, [staged_py], session_id="sess-A")
        assert passed is False
        assert "Phase 2.5 hint" in detail
        assert "sess-B" in detail

    def test_block_without_hint_when_target_not_in_other_session(self, tmp_path):
        """悬空 import + 目标模块不在其他活跃 session → 阻断消息不含 hint。"""
        # 无活跃 session 持有目标模块
        gw = MagicMock()
        gw.project_root = tmp_path
        staged_py = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        staged_content = (
            "from zephyr.gov_enforcement.commit_gates.nonexistent_module "
            "import something\n"
        )

        def _mock_run_git(args):
            return MagicMock(returncode=1, stdout="", stderr="")
        gw.run_git = _mock_run_git

        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(gate_mod, "_get_staged_py_files", lambda g, gid: [staged_py])
            mp.setattr(gate_mod, "_read_staged_file", lambda g, f: staged_content)
            gate = make_import_integrity_gate()
            passed, detail = gate.check(gw, [staged_py], session_id="sess-A")
        assert passed is False
        assert "Phase 2.5 hint" not in detail

    def test_block_without_hint_when_no_active_sessions(self, tmp_path):
        """悬空 import + 无活跃 session → 阻断消息不含 hint。"""
        gw = MagicMock()
        gw.project_root = tmp_path
        staged_py = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        staged_content = (
            "from zephyr.gov_enforcement.commit_gates.nonexistent_module "
            "import something\n"
        )

        def _mock_run_git(args):
            return MagicMock(returncode=1, stdout="", stderr="")
        gw.run_git = _mock_run_git

        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(gate_mod, "_get_staged_py_files", lambda g, gid: [staged_py])
            mp.setattr(gate_mod, "_read_staged_file", lambda g, f: staged_content)
            gate = make_import_integrity_gate()
            passed, detail = gate.check(gw, [staged_py], session_id="sess-A")
        assert passed is False
        assert "Phase 2.5 hint" not in detail

    def test_no_kwargs_session_id_still_works(self, tmp_path):
        """不传 session_id kwargs → find_target_in_active_sessions 不排除自身（仍正常工作）。"""
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(project_root=tmp_path)
        target_file = str(tmp_path / "src" / "zephyr" / "gov_enforcement" / "commit_gates" / "forged_gw_marker_gate.py")
        reg.register("sess-B", pid=0, held_files=[target_file])

        gw = MagicMock()
        gw.project_root = tmp_path
        staged_py = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        staged_content = (
            "from zephyr.gov_enforcement.commit_gates.forged_gw_marker_gate "
            "import make_forged_gw_marker_gate\n"
        )

        def _mock_run_git(args):
            return MagicMock(returncode=1, stdout="", stderr="")
        gw.run_git = _mock_run_git

        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(gate_mod, "_get_staged_py_files", lambda g, gid: [staged_py])
            mp.setattr(gate_mod, "_read_staged_file", lambda g, f: staged_content)
            gate = make_import_integrity_gate()
            # 不传 session_id
            passed, detail = gate.check(gw, [staged_py])
        assert passed is False
        assert "Phase 2.5 hint" in detail
        assert "sess-B" in detail
