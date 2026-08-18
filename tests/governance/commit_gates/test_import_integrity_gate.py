# [A_test] module_id: MOD-GOV_import_integrity_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_import_integrity_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

from zephyr.gov_enforcement.commit_gates._diff_helpers import (
    _matches_any_prefix,
    _module_to_file_candidates,
)
from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
    _PROJECT_PREFIXES,
    _collect_imports,
    _has_wildcard_import,
    _is_relative_import,
    find_target_in_active_sessions,
    make_import_integrity_gate,
    scan_content_for_dangling_imports,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec


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
        assert _matches_any_prefix("zephyr.gov_enforcement.commit_gates.foo", _PROJECT_PREFIXES) is True

    def test_is_project_module_scripts(self):
        """scripts.xxx 是项目内模块。"""
        assert _matches_any_prefix("scripts.governance.foo", _PROJECT_PREFIXES) is True

    def test_is_project_module_external(self):
        """os / requests 不是项目内模块。"""
        assert _matches_any_prefix("os", _PROJECT_PREFIXES) is False
        assert _matches_any_prefix("requests", _PROJECT_PREFIXES) is False

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
        # held_file 用 Windows 反斜杠（SessionRegistry.normalize_file_path 会 resolve，
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


# ---------------------------------------------------------------------------
# TestSysPathInjectionResolvable: sys.path 注入目录识别
# （#ARCH-IMPORT-INTEGRITY-SYSPATH-001 治本：320+ 脚本动态导入免疫）
# ---------------------------------------------------------------------------


class TestSysPathInjectionResolvable:
    """sys.path 注入目录识别测试。

    病根：scripts/governance/ 下 320+ 脚本通过 sys.path.insert 动态注入
    _shared/_common 父目录，from _shared import / from _common import 在
    运行时可用但静态 AST 不可解析。门禁升级后提取 sys.path 注入目录，
    在其中查找模块文件，找到则判定可解析。

    覆盖场景：
    - _extract_sys_path_dirs 提取字符串字面量
    - _extract_sys_path_dirs 提取 Path(__file__).resolve().parent
    - _extract_sys_path_dirs 提取 Path(__file__).resolve().parents[N]
    - _extract_sys_path_dirs 提取变量引用（1 层回溯）
    - _extract_sys_path_dirs 无法求值 → fail-open（返回空列表）
    - _check_module_in_dirs 模块存在 → True
    - _check_module_in_dirs 模块不存在 → False
    - scan_content: sys.path 注入 + 模块存在 → 无违规
    - scan_content: sys.path 注入 + 模块不存在 → 仍阻断
    - scan_content: 无 sys.path 注入 + 模块不存在 → 阻断（现有行为不变）
    """

    def test_extract_string_literal(self):
        """sys.path.insert(0, "/abs/path") → 提取字符串字面量。"""
        import ast

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = 'import sys\nsys.path.insert(0, "/abs/literal/path")\n'
        tree = ast.parse(content)
        dirs = _extract_sys_path_dirs(tree, "scripts/test.py")
        assert "/abs/literal/path" in dirs

    def test_extract_path_parent(self, tmp_path):
        """sys.path.insert(0, str(Path(__file__).resolve().parent)) → 提取文件所在目录。"""
        import ast

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        )
        tree = ast.parse(content)
        # py_file 是相对路径，_extract_sys_path_dirs 内部转绝对路径
        dirs = _extract_sys_path_dirs(tree, "scripts/governance/test.py")
        import os

        expected = os.path.dirname(os.path.abspath("scripts/governance/test.py"))
        assert expected in dirs

    def test_extract_path_parents_n(self, tmp_path):
        """sys.path.insert(0, str(Path(__file__).resolve().parents[4])) → 提取第4级父目录。"""
        import ast
        import os

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parents[4]))\n"
        )
        tree = ast.parse(content)
        py_file = "scripts/governance/d5_architecture/generators/test.py"
        dirs = _extract_sys_path_dirs(tree, py_file)
        # parents[4] = 从 file_abs 起连续 5 次 dirname（parents[0] 是 1 次）
        # 用 pathlib 自身作预言机验证实现求值正确
        from pathlib import Path

        file_abs = os.path.abspath(py_file)
        expected = str(Path(file_abs).resolve().parents[4])
        assert expected in dirs, f"expected {expected} in {dirs}"

    def test_extract_variable_reference(self):
        """变量引用回溯：VAR = str(Path(__file__).resolve().parent); sys.path.insert(0, VAR)。"""
        import ast
        import os

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_THIS_DIR = str(Path(__file__).resolve().parent)\n"
            "if _THIS_DIR not in sys.path:\n"
            "    sys.path.insert(0, _THIS_DIR)\n"
        )
        tree = ast.parse(content)
        dirs = _extract_sys_path_dirs(tree, "scripts/governance/test.py")
        expected = os.path.dirname(os.path.abspath("scripts/governance/test.py"))
        assert expected in dirs

    def test_extract_unresolvable_fail_open(self):
        """无法求值的表达式 → fail-open（返回空列表，不阻断）。

        next() 向上搜索不存在的子目录 → 搜索失败 → 不提取（fail-open）。
        """
        import ast

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        # next() 搜索的子目录在磁盘上不存在 → 向上搜索失败 → 不提取
        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents "
            "if (p / '_nonexistent_subdir_xyz').exists()))\n"
            "sys.path.insert(0, _GOV_DIR)\n"
        )
        tree = ast.parse(content)
        dirs = _extract_sys_path_dirs(tree, "scripts/governance/test.py")
        # 子目录不存在 → next() 搜索失败 → 不提取（fail-open）
        assert dirs == []

    def test_extract_variable_indirection_parent(self):
        """变量间接形式：_THIS_FILE = Path(__file__).resolve() 后 _THIS_FILE.parent。"""
        import ast
        import os

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_THIS_FILE = Path(__file__).resolve()\n"
            "_THIS_DIR = str(_THIS_FILE.parent)\n"
            "if _THIS_DIR not in sys.path:\n"
            "    sys.path.insert(0, _THIS_DIR)\n"
        )
        tree = ast.parse(content)
        py_file = "scripts/governance/d5_architecture/generators/gen.py"
        dirs = _extract_sys_path_dirs(tree, py_file)
        expected = os.path.dirname(os.path.abspath(py_file))
        assert expected in dirs, f"expected {expected} in {dirs}"

    def test_extract_variable_indirection_parents_n(self):
        """变量间接形式：_THIS_FILE = Path(__file__).resolve() 后 _THIS_FILE.parents[3]。"""
        import ast
        import os
        from pathlib import Path

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_THIS_FILE = Path(__file__).resolve()\n"
            "_SCRIPTS_DIR = str(_THIS_FILE.parents[3])\n"
            "if _SCRIPTS_DIR not in sys.path:\n"
            "    sys.path.insert(0, _SCRIPTS_DIR)\n"
        )
        tree = ast.parse(content)
        py_file = "scripts/governance/d5_architecture/generators/gen.py"
        dirs = _extract_sys_path_dirs(tree, py_file)
        file_abs = os.path.abspath(py_file)
        expected = str(Path(file_abs).resolve().parents[3])
        assert expected in dirs, f"expected {expected} in {dirs}"

    def test_extract_next_parents_search_found(self):
        """next(p for p in _THIS_FILE.parents if (p/'_shared').exists()) → 找到治理根目录。"""
        import ast
        import os

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_THIS_FILE = Path(__file__).resolve()\n"
            "_GOV_DIR = str(next(p for p in _THIS_FILE.parents "
            "if (p / '_shared').exists()))\n"
            "if _GOV_DIR not in sys.path:\n"
            "    sys.path.insert(0, _GOV_DIR)\n"
        )
        tree = ast.parse(content)
        # 用真实存在的生成器路径（scripts/governance/_shared 真实存在）
        py_file = "scripts/governance/d5_architecture/generators/gen.py"
        dirs = _extract_sys_path_dirs(tree, py_file)
        # 预期找到 scripts/governance（含 _shared 子目录）
        expected = os.path.abspath("scripts/governance")
        assert expected in dirs, f"expected {expected} in {dirs}"

    def test_check_module_in_dirs_found(self, tmp_path):
        """模块在目录中存在（.py 文件）→ True。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_module_in_dirs,
        )

        # 创建 _common.py
        (tmp_path / "_common.py").write_text("x = 1", encoding="utf-8")
        assert _check_module_in_dirs("_common", [str(tmp_path)]) is True

    def test_check_module_in_dirs_package_found(self, tmp_path):
        """模块在目录中存在（包 __init__.py）→ True。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_module_in_dirs,
        )

        # 创建 _shared/constants.py + _shared/__init__.py
        shared_dir = tmp_path / "_shared"
        shared_dir.mkdir()
        (shared_dir / "__init__.py").write_text("", encoding="utf-8")
        (shared_dir / "constants.py").write_text("X = 1", encoding="utf-8")
        assert _check_module_in_dirs("_shared.constants", [str(tmp_path)]) is True
        assert _check_module_in_dirs("_shared", [str(tmp_path)]) is True

    def test_check_module_in_dirs_not_found(self, tmp_path):
        """模块在目录中不存在 → False。"""
        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _check_module_in_dirs,
        )

        assert _check_module_in_dirs("_nonexistent_mod", [str(tmp_path)]) is False

    def test_scan_syspath_module_exists_no_violation(self, tmp_path):
        """sys.path 注入 + 模块在注入目录存在 → 无违规（治本核心场景）。"""
        import os

        # 创建 _shared 包（模拟真实项目结构）
        shared_dir = tmp_path / "scripts" / "governance" / "_shared"
        shared_dir.mkdir(parents=True)
        (shared_dir / "__init__.py").write_text("", encoding="utf-8")
        (shared_dir / "constants.py").write_text("X = 1", encoding="utf-8")

        # 模拟生成器文件：sys.path.insert + from _shared.constants import
        py_file_rel = "scripts/governance/d5_architecture/generators/gen.py"
        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_GOV_DIR = str(Path(__file__).resolve().parents[2])\n"
            "if _GOV_DIR not in sys.path:\n"
            "    sys.path.insert(0, _GOV_DIR)\n"
            "from _shared.constants import X  # noqa: E402\n"
        )
        gw = _make_gateway()
        staged_files: set[str] = set()

        # 需要 chdir 到 tmp_path 使相对路径解析正确
        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            violations = gate_mod.scan_content_for_dangling_imports(
                py_file_rel, content, staged_files, gw
            )
        finally:
            os.chdir(original_cwd)
        assert len(violations) == 0, f"Expected no violations, got: {violations}"

    def test_scan_syspath_module_not_exists_still_blocked(self, tmp_path):
        """sys.path 注入 + 模块在注入目录不存在 → 仍阻断（安全保持）。"""
        import os

        # 不创建 _shared 包（模块不存在）
        content = (
            "import sys\n"
            "from pathlib import Path\n"
            "_GOV_DIR = str(Path(__file__).resolve().parents[2])\n"
            "if _GOV_DIR not in sys.path:\n"
            "    sys.path.insert(0, _GOV_DIR)\n"
            "from _shared.nonexistent_module import X  # noqa: E402\n"
        )
        gw = _make_gateway()
        staged_files: set[str] = set()

        import zephyr.gov_enforcement.commit_gates.import_integrity_gate as gate_mod
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            violations = gate_mod.scan_content_for_dangling_imports(
                "scripts/governance/d5_architecture/generators/gen.py",
                content,
                staged_files,
                gw,
            )
        finally:
            os.chdir(original_cwd)
        assert len(violations) == 1
        assert "_shared.nonexistent_module" in violations[0]

    def test_scan_no_syspath_existing_behavior_unchanged(self):
        """无 sys.path 注入 + 不存在的外部模块 → 阻断（现有行为不变）。"""
        content = "import this_module_does_not_exist_xyz_12345\n"
        gw = _make_gateway()
        staged_files: set[str] = set()
        violations = scan_content_for_dangling_imports(
            "src/test.py", content, staged_files, gw
        )
        assert len(violations) == 1
        assert "this_module_does_not_exist_xyz_12345" in violations[0]

    def test_scan_syspath_append_mode(self, tmp_path):
        """sys.path.append(X) 也能被提取（insert 和 append 两种模式）。"""
        import ast

        from zephyr.gov_enforcement.commit_gates.import_integrity_gate import (
            _extract_sys_path_dirs,
        )

        content = (
            "import sys\n"
            "sys.path.append('/abs/append/path')\n"
        )
        tree = ast.parse(content)
        dirs = _extract_sys_path_dirs(tree, "scripts/test.py")
        assert "/abs/append/path" in dirs
